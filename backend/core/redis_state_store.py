"""Redis transport for fixed, fenced coordination primitives.

The implementation stays independent of :mod:`core.state_store` so the legacy
state-store import can re-export this class without creating a cycle.
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib
import math
import secrets
import weakref
from typing import Any, Optional
from urllib.parse import urlsplit

from core.coordination import (
    MAX_COORDINATION_INTEGER,
    MAX_IDENTIFIER_LENGTH,
    MAX_PAYLOAD_BYTES,
    MAX_TTL_SECONDS,
    CasRequest,
    CasResult,
    CoordinationCorruptError,
    CoordinationReconciliationRequiredError,
    CoordinationUnavailableError,
    Epoch,
    EpochState,
    InvalidationGeneration,
    InvalidationRequest,
    InvalidationResult,
    QuotaCommitRequest,
    QuotaCommitResult,
    QuotaReservationDecision,
    QuotaReservationRequest,
    validate_deployment_namespace,
    validate_epoch,
    validate_operation_id,
)

_SCHEMA = b"1"
_THIRTY_DAYS_MS = 30 * 86_400 * 1000
_DEFAULT_REPLAY_LIMIT = 100_000
_MAX_CLEANUP = 256
_MAX_INTEGER_TEXT = "9223372036854775807"
_QUOTA_RATE_WINDOW_MS = 60_000
_QUOTA_MONTHLY_WINDOW_MS = _THIRTY_DAYS_MS
_CORRUPT_DRIVER_ERROR_MARKERS = (
    "COORDINATION_CORRUPT",
    "WRONGTYPE",
    "HASH VALUE IS NOT AN INTEGER",
    "VALUE IS NOT AN INTEGER OR OUT OF RANGE",
    "INCREMENT OR DECREMENT WOULD OVERFLOW",
)


_EPOCH_READ_SCRIPT = """-- omni:epoch_read:v1
local function valid_integer(value)
  return value and string.match(value, '^[1-9][0-9]*$')
    and (#value < 19 or (#value == 19 and value <= '9223372036854775807'))
end
local count = redis.call('HLEN', KEYS[1])
if count == 0 then
  redis.call('HSET', KEYS[1], 'schema_version', '1', 'epoch', '1', 'state', 'ready')
elseif count ~= 3 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local values = redis.call('HMGET', KEYS[1], 'schema_version', 'epoch', 'state')
if values[1] ~= '1' or not valid_integer(values[2])
  or (values[3] ~= 'ready' and values[3] ~= 'reconciling') then
  return redis.error_reply('COORDINATION_CORRUPT')
end
return {'1', 'ok', values[2], values[3]}
"""

_EPOCH_ADVANCE_SCRIPT = """-- omni:epoch_advance:v1
local function valid_integer(value)
  return value and string.match(value, '^[1-9][0-9]*$')
    and (#value < 19 or (#value == 19 and value <= '9223372036854775807'))
end
local function next_integer(value)
  if value == '9223372036854775807' then return nil end
  local digits, carry = {}, 1
  for index = #value, 1, -1 do
    local digit = string.byte(value, index) - 48 + carry
    if digit == 10 then digit, carry = 0, 1 else carry = 0 end
    table.insert(digits, 1, string.char(digit + 48))
  end
  if carry == 1 then table.insert(digits, 1, '1') end
  return table.concat(digits)
end
local function valid_replay(value, score)
  if not value or not score or not valid_integer(score) then return false end
  local schema, fingerprint, saved_epoch, saved_state, saved_expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
  return schema == '1' and fingerprint and valid_integer(fingerprint)
    and valid_integer(saved_epoch) and saved_epoch == next_integer(fingerprint)
    and saved_state == 'reconciling'
    and valid_integer(saved_expiry) and saved_expiry == score
end
local count = redis.call('HLEN', KEYS[1])
if count == 0 then
  redis.call('HSET', KEYS[1], 'schema_version', '1', 'epoch', '1', 'state', 'ready')
elseif count ~= 3 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local epoch = redis.call('HMGET', KEYS[1], 'schema_version', 'epoch', 'state')
if epoch[1] ~= '1' or not valid_integer(epoch[2])
  or (epoch[3] ~= 'ready' and epoch[3] ~= 'reconciling') then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if not valid_integer(ARGV[1]) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local clock = redis.call('TIME')
local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
if redis.call('HLEN', KEYS[2]) ~= redis.call('ZCARD', KEYS[3]) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local replay = redis.call('HGET', KEYS[2], ARGV[2])
local replay_expiry = redis.call('ZSCORE', KEYS[3], ARGV[2])
if not valid_replay(replay, replay_expiry) and (replay or replay_expiry) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if replay and tonumber(replay_expiry) > now_ms then
  local _, fingerprint, saved_epoch, saved_state =
    string.match(replay, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
  if fingerprint == ARGV[1] then
    return {'1', 'ok', saved_epoch, saved_state}
  end
  return {'1', 'ok', epoch[2], epoch[3]}
end
local due = redis.call('ZRANGEBYSCORE', KEYS[3], '-inf', now_ms, 'LIMIT', 0, 257)
if #due > 256 then
  return {'1', 'reconciliation_required', '', ''}
end
for _, operation_id in ipairs(due) do
  if not valid_replay(redis.call('HGET', KEYS[2], operation_id),
      redis.call('ZSCORE', KEYS[3], operation_id)) then
    return redis.error_reply('COORDINATION_CORRUPT')
  end
end
if #due > 0 then
  redis.call('HDEL', KEYS[2], unpack(due))
  redis.call('ZREM', KEYS[3], unpack(due))
end
if epoch[2] ~= ARGV[1] or epoch[3] ~= 'ready' then
  return {'1', 'ok', epoch[2], epoch[3]}
end
if redis.call('HLEN', KEYS[2]) >= tonumber(ARGV[4]) then
  return {'1', 'reconciliation_required', '', ''}
end
if epoch[2] == '9223372036854775807' then
  return redis.error_reply('COORDINATION_CORRUPT')
end
redis.call('HINCRBY', KEYS[1], 'epoch', 1)
redis.call('HSET', KEYS[1], 'state', 'reconciling')
local new_epoch = redis.call('HGET', KEYS[1], 'epoch')
local expires_at = now_ms + tonumber(ARGV[3])
local expires_text = string.format('%.0f', expires_at)
redis.call('HSET', KEYS[2], ARGV[2],
  '1|' .. ARGV[1] .. '|' .. new_epoch .. '|reconciling|' .. expires_text)
redis.call('ZADD', KEYS[3], expires_at, ARGV[2])
return {'1', 'ok', new_epoch, 'reconciling'}
"""

_EPOCH_READY_SCRIPT = """-- omni:epoch_ready:v1
local function valid_integer(value)
  return value and string.match(value, '^[1-9][0-9]*$')
    and (#value < 19 or (#value == 19 and value <= '9223372036854775807'))
end
local function valid_replay(value, score)
  if not value or not score or not valid_integer(score) then return false end
  local schema, fingerprint, saved_epoch, saved_state, saved_expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
  return schema == '1' and fingerprint and valid_integer(fingerprint)
    and valid_integer(saved_epoch) and saved_epoch == fingerprint and saved_state == 'ready'
    and valid_integer(saved_expiry) and saved_expiry == score
end
local count = redis.call('HLEN', KEYS[1])
if count == 0 then
  redis.call('HSET', KEYS[1], 'schema_version', '1', 'epoch', '1', 'state', 'ready')
elseif count ~= 3 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local epoch = redis.call('HMGET', KEYS[1], 'schema_version', 'epoch', 'state')
if epoch[1] ~= '1' or not valid_integer(epoch[2])
  or (epoch[3] ~= 'ready' and epoch[3] ~= 'reconciling') then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local clock = redis.call('TIME')
local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
if redis.call('HLEN', KEYS[2]) ~= redis.call('ZCARD', KEYS[3]) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local replay = redis.call('HGET', KEYS[2], ARGV[2])
local replay_expiry = redis.call('ZSCORE', KEYS[3], ARGV[2])
if not valid_replay(replay, replay_expiry) and (replay or replay_expiry) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if replay and tonumber(replay_expiry) > now_ms then
  local _, fingerprint, saved_epoch, saved_state =
    string.match(replay, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
  if fingerprint == ARGV[1] then
    return {'1', 'ok', saved_epoch, saved_state}
  end
  return {'1', 'ok', epoch[2], epoch[3]}
end
local due = redis.call('ZRANGEBYSCORE', KEYS[3], '-inf', now_ms, 'LIMIT', 0, 257)
if #due > 256 then
  return {'1', 'reconciliation_required', '', ''}
end
for _, operation_id in ipairs(due) do
  if not valid_replay(redis.call('HGET', KEYS[2], operation_id),
      redis.call('ZSCORE', KEYS[3], operation_id)) then
    return redis.error_reply('COORDINATION_CORRUPT')
  end
end
if #due > 0 then
  redis.call('HDEL', KEYS[2], unpack(due))
  redis.call('ZREM', KEYS[3], unpack(due))
end
if epoch[2] ~= ARGV[1] or epoch[3] ~= 'reconciling' then
  return {'1', 'ok', epoch[2], epoch[3]}
end
if redis.call('HLEN', KEYS[2]) >= tonumber(ARGV[4]) then
  return {'1', 'reconciliation_required', '', ''}
end
redis.call('HSET', KEYS[1], 'state', 'ready')
local expires_at = now_ms + tonumber(ARGV[3])
local expires_text = string.format('%.0f', expires_at)
redis.call('HSET', KEYS[2], ARGV[2],
  '1|' .. ARGV[1] .. '|' .. epoch[2] .. '|ready|' .. expires_text)
redis.call('ZADD', KEYS[3], expires_at, ARGV[2])
return {'1', 'ok', epoch[2], 'ready'}
"""

_CAS_SCRIPT = """-- omni:cas:v1
local function valid_integer(value, allow_zero)
  if allow_zero and value == '0' then return true end
  return value and string.match(value, '^[1-9][0-9]*$')
    and (#value < 19 or (#value == 19 and value <= '9223372036854775807'))
end
local function valid_replay(value, score)
  if not value or not score or not valid_integer(score, false) then return false end
  local schema, fingerprint, status, revision, saved_expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]+)|([^|]*)|([^|]+)$')
  if schema ~= '1' or not fingerprint or not valid_integer(saved_expiry, false)
    or saved_expiry ~= score then return false end
  return (status == 'applied' and valid_integer(revision, false))
    or (status == 'not_applied' and revision == '')
end
local epoch_count = redis.call('HLEN', KEYS[1])
if epoch_count == 0 then
  redis.call('HSET', KEYS[1], 'schema_version', '1', 'epoch', '1', 'state', 'ready')
elseif epoch_count ~= 3 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local epoch = redis.call('HMGET', KEYS[1], 'schema_version', 'epoch', 'state')
if epoch[1] ~= '1' or not valid_integer(epoch[2], false)
  or (epoch[3] ~= 'ready' and epoch[3] ~= 'reconciling') then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if epoch[2] ~= ARGV[4] or epoch[3] ~= 'ready' then
  return {'1', 'not_applied', '', '0'}
end
local clock = redis.call('TIME')
local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
if redis.call('HLEN', KEYS[3]) ~= redis.call('ZCARD', KEYS[4]) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local replay = redis.call('HGET', KEYS[3], ARGV[5])
local replay_expiry = redis.call('ZSCORE', KEYS[4], ARGV[5])
if not valid_replay(replay, replay_expiry) and (replay or replay_expiry) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if replay and tonumber(replay_expiry) > now_ms then
  local _, fingerprint, status, revision =
    string.match(replay, '^([^|]+)|([^|]+)|([^|]+)|([^|]*)|([^|]+)$')
  if fingerprint == ARGV[6] then
    return {'1', status, revision, '1'}
  end
  return {'1', 'not_applied', '', '0'}
end
local due = redis.call('ZRANGEBYSCORE', KEYS[4], '-inf', now_ms, 'LIMIT', 0, 257)
if #due > 256 then
  return {'1', 'reconciliation_required', '', '0'}
end
for _, operation_id in ipairs(due) do
  if not valid_replay(redis.call('HGET', KEYS[3], operation_id),
      redis.call('ZSCORE', KEYS[4], operation_id)) then
    return redis.error_reply('COORDINATION_CORRUPT')
  end
end
if #due > 0 then
  redis.call('HDEL', KEYS[3], unpack(due))
  redis.call('ZREM', KEYS[4], unpack(due))
end
if redis.call('HLEN', KEYS[3]) >= tonumber(ARGV[7]) then
  return {'1', 'reconciliation_required', '', '0'}
end
local record_count = redis.call('HLEN', KEYS[2])
local current_revision = nil
if record_count ~= 0 then
  if record_count ~= 3 then return redis.error_reply('COORDINATION_CORRUPT') end
  local record = redis.call('HMGET', KEYS[2], 'schema_version', 'revision', 'payload')
  local record_ttl = redis.call('PTTL', KEYS[2])
  if record[1] ~= '1' or not valid_integer(record[2], false) or record[3] == false
    or #record[3] > 16384 or record_ttl < 0 or record_ttl > 2592000000 then
    return redis.error_reply('COORDINATION_CORRUPT')
  end
  current_revision = record[2]
end
local status = 'not_applied'
local revision = ''
if (not current_revision and ARGV[1] == '0')
  or (current_revision and current_revision == ARGV[1]) then
  status = 'applied'
  if not current_revision then
    revision = '1'
    redis.call('HSET', KEYS[2], 'schema_version', '1', 'revision', revision, 'payload', ARGV[2])
  else
    if current_revision == '9223372036854775807' then
      return redis.error_reply('COORDINATION_CORRUPT')
    end
    redis.call('HINCRBY', KEYS[2], 'revision', 1)
    revision = redis.call('HGET', KEYS[2], 'revision')
    redis.call('HSET', KEYS[2], 'payload', ARGV[2])
  end
  redis.call('PEXPIRE', KEYS[2], tonumber(ARGV[3]))
end
local expires_at = now_ms + tonumber(ARGV[3])
local expires_text = string.format('%.0f', expires_at)
redis.call('HSET', KEYS[3], ARGV[5],
  '1|' .. ARGV[6] .. '|' .. status .. '|' .. revision .. '|' .. expires_text)
redis.call('ZADD', KEYS[4], expires_at, ARGV[5])
return {'1', status, revision, '0'}
"""

_INVALIDATION_SCRIPT = """-- omni:invalidation:v1
local function valid_integer(value)
  return value and string.match(value, '^[1-9][0-9]*$')
    and (#value < 19 or (#value == 19 and value <= '9223372036854775807'))
end
local function valid_replay(value, score)
  if not value or not score or not valid_integer(score) then return false end
  local schema, fingerprint, generation, saved_expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
  return schema == '1' and fingerprint and valid_integer(generation)
    and valid_integer(saved_expiry) and saved_expiry == score
end
local epoch_count = redis.call('HLEN', KEYS[1])
if epoch_count == 0 then
  redis.call('HSET', KEYS[1], 'schema_version', '1', 'epoch', '1', 'state', 'ready')
elseif epoch_count ~= 3 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local epoch = redis.call('HMGET', KEYS[1], 'schema_version', 'epoch', 'state')
if epoch[1] ~= '1' or not valid_integer(epoch[2])
  or (epoch[3] ~= 'ready' and epoch[3] ~= 'reconciling') then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if epoch[2] ~= ARGV[1] or epoch[3] ~= 'ready' then
  return {'1', 'not_applied', '', '0'}
end
local clock = redis.call('TIME')
local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
if redis.call('HLEN', KEYS[3]) ~= redis.call('ZCARD', KEYS[4]) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local replay = redis.call('HGET', KEYS[3], ARGV[2])
local replay_expiry = redis.call('ZSCORE', KEYS[4], ARGV[2])
if not valid_replay(replay, replay_expiry) and (replay or replay_expiry) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if replay and tonumber(replay_expiry) > now_ms then
  local _, fingerprint, generation =
    string.match(replay, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
  if fingerprint == ARGV[4] then return {'1', 'applied', generation, '1'} end
  return {'1', 'not_applied', '', '0'}
end
local due = redis.call('ZRANGEBYSCORE', KEYS[4], '-inf', now_ms, 'LIMIT', 0, 257)
if #due > 256 then
  return {'1', 'reconciliation_required', '', '0'}
end
for _, operation_id in ipairs(due) do
  if not valid_replay(redis.call('HGET', KEYS[3], operation_id),
      redis.call('ZSCORE', KEYS[4], operation_id)) then
    return redis.error_reply('COORDINATION_CORRUPT')
  end
end
if #due > 0 then
  redis.call('HDEL', KEYS[3], unpack(due))
  redis.call('ZREM', KEYS[4], unpack(due))
end
if redis.call('HLEN', KEYS[3]) >= tonumber(ARGV[5]) then
  return {'1', 'reconciliation_required', '', '0'}
end
local generation_count = redis.call('HLEN', KEYS[2])
local generation
if generation_count == 0 then
  generation = '1'
  redis.call('HSET', KEYS[2], 'schema_version', '1', 'generation', generation)
elseif generation_count == 2 then
  local record = redis.call('HMGET', KEYS[2], 'schema_version', 'generation')
  if record[1] ~= '1' or not valid_integer(record[2])
    or record[2] == '9223372036854775807' then
    return redis.error_reply('COORDINATION_CORRUPT')
  end
  redis.call('HINCRBY', KEYS[2], 'generation', 1)
  generation = redis.call('HGET', KEYS[2], 'generation')
else
  return redis.error_reply('COORDINATION_CORRUPT')
end
local expires_at = now_ms + tonumber(ARGV[3])
local expires_text = string.format('%.0f', expires_at)
redis.call('HSET', KEYS[3], ARGV[2],
  '1|' .. ARGV[4] .. '|' .. generation .. '|' .. expires_text)
redis.call('ZADD', KEYS[4], expires_at, ARGV[2])
return {'1', 'applied', generation, '0'}
"""

_INVALIDATION_READ_SCRIPT = """-- omni:invalidation_read:v1
local function valid_integer(value)
  return value and string.match(value, '^[1-9][0-9]*$')
    and (#value < 19 or (#value == 19 and value <= '9223372036854775807'))
end
local count = redis.call('HLEN', KEYS[1])
if count == 0 then return {'1', 'ok', ''} end
if count ~= 2 then return redis.error_reply('COORDINATION_CORRUPT') end
local record = redis.call('HMGET', KEYS[1], 'schema_version', 'generation')
if record[1] ~= '1' or not valid_integer(record[2]) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
return {'1', 'ok', record[2]}
"""

_INCREMENT_SCRIPT = """-- omni:increment:v1
local value = redis.call('INCRBY', KEYS[1], ARGV[1])
if ARGV[2] ~= '' then redis.call('PEXPIRE', KEYS[1], tonumber(ARGV[2])) end
return {'1', 'ok', redis.call('GET', KEYS[1])}
"""

_LOCK_RELEASE_SCRIPT = """-- omni:lock_release:v1
local deleted = '0'
if redis.call('GET', KEYS[1]) == ARGV[1] then
  redis.call('DEL', KEYS[1])
  deleted = '1'
end
return {'1', 'ok', deleted}
"""

# Quota records and replay entries are stored in separate per-target hash/ZSET pairs.  The
# record hash contains lifecycle records only, so HLEN is both the per-target count and the
# bound for every HGETALL traversal.  The common parser is intentionally strict because Redis
# state is untrusted and cleanup must validate every due pair before deleting any evidence.
_QUOTA_LUA_COMMON = r"""
local function valid_uint(value)
  return value and (value == '0' or string.match(value, '^[1-9][0-9]*$'))
    and (#value < 19 or (#value == 19 and value <= '9223372036854775807'))
end
local function valid_positive(value) return valid_uint(value) and value ~= '0' end
local function valid_hex(value)
  return value and #value == 64 and string.match(value, '^[0-9a-f]+$')
end
local function valid_decimal(value)
  if not value or #value > 64 then return false end
  if value == '0' then return true end
  if string.match(value, '^[1-9][0-9]*$') or string.match(value, '^0%.[0-9]*[1-9]$')
    or string.match(value, '^[1-9][0-9]*%.[0-9]*[1-9]$') then return true end
  local mantissa, exponent = string.match(value, '^([^e]+)e([+-]?[0-9]+)$')
  if not mantissa or not exponent or not (string.match(mantissa, '^[1-9]$')
    or string.match(mantissa, '^[1-9]%.[0-9]*[1-9]$')) then return false end
  return string.match(exponent, '^[+-]?0[1-9]$') or string.match(exponent, '^[+-]?[1-9][0-9]*$')
end
local function split_record(value)
  if not value or #value > 2048 then return nil end
  local fields = {}
  for field in string.gmatch(value .. '|', '(.-)|') do fields[#fields + 1] = field end
  if #fields ~= 24 then return nil end
  return fields
end
local function parse_record(value)
  local f = split_record(value)
  if not f then return nil end
  local r = {
    schema=f[1], fingerprint=f[2], key=f[3], state=f[4], active_until=f[5],
    retained_until=f[6], accepted_at=f[7], estimated_tokens=f[8], estimated_cost=f[9],
    committed_at=f[10], actual_tokens=f[11], actual_cost=f[12], durable=f[13],
    daily_reconciled=f[14], monthly_reconciled=f[15], business_commit=f[16],
    rpm_limit=f[17], tpm_limit=f[18], daily_budget=f[19], monthly_budget=f[20],
    daily_spend=f[21], monthly_spend=f[22], retention_ms=f[23], next_expiry=f[24]
  }
  if r.schema ~= '1' or not valid_hex(r.fingerprint) or not valid_hex(r.key)
    or (r.state ~= 'active' and r.state ~= 'committed' and r.state ~= 'released'
      and r.state ~= 'expired')
    or not valid_positive(r.active_until) or not valid_positive(r.retained_until)
    or not valid_positive(r.accepted_at) or not valid_uint(r.estimated_tokens)
    or not valid_decimal(r.estimated_cost) or not valid_uint(r.committed_at)
    or not valid_uint(r.actual_tokens) or not valid_decimal(r.actual_cost)
    or (r.durable ~= '0' and r.durable ~= '1')
    or (r.daily_reconciled ~= '0' and r.daily_reconciled ~= '1')
    or (r.monthly_reconciled ~= '0' and r.monthly_reconciled ~= '1')
    or not valid_decimal(r.business_commit)
    or (r.rpm_limit ~= 'n' and not valid_positive(r.rpm_limit))
    or (r.tpm_limit ~= 'n' and not valid_positive(r.tpm_limit))
    or (r.daily_budget ~= 'n' and not valid_decimal(r.daily_budget))
    or (r.monthly_budget ~= 'n' and not valid_decimal(r.monthly_budget))
    or not valid_decimal(r.daily_spend) or not valid_decimal(r.monthly_spend)
    or not valid_positive(r.retention_ms) or tonumber(r.retention_ms) > 2592000000
    or not valid_positive(r.next_expiry)
  or tonumber(r.accepted_at) > tonumber(r.active_until)
  or tonumber(r.active_until) > tonumber(r.retained_until)
    or tonumber(r.next_expiry) > tonumber(r.retained_until) then return nil end
  local terminal_source = r.state == 'active' or r.state == 'released' or r.state == 'expired'
  if terminal_source and (r.committed_at ~= '0' or r.actual_tokens ~= '0'
    or r.actual_cost ~= '0' or r.durable ~= '0' or r.business_commit ~= '0') then return nil end
  if terminal_source and ((r.daily_budget == 'n' and r.daily_reconciled ~= '1')
    or (r.daily_budget ~= 'n' and r.daily_reconciled ~= '0')
    or (r.monthly_budget == 'n' and r.monthly_reconciled ~= '1')
    or (r.monthly_budget ~= 'n' and r.monthly_reconciled ~= '0')) then return nil end
  if terminal_source and (tonumber(r.accepted_at) > 9223372036854775807 - tonumber(r.retention_ms)
    or tonumber(r.retained_until) ~= tonumber(r.accepted_at) + tonumber(r.retention_ms)) then return nil end
  if r.state == 'active' and r.next_expiry ~= r.active_until then return nil end
  if (r.state == 'released' or r.state == 'expired')
    and r.next_expiry ~= r.retained_until then return nil end
  if r.state == 'committed' then
    if r.committed_at == '0' or tonumber(r.committed_at) > tonumber(r.active_until)
      or r.next_expiry ~= r.retained_until then return nil end
    local expected_expiry = tonumber(r.committed_at) + 60000
    if r.daily_reconciled == '0' then expected_expiry = math.max(expected_expiry, tonumber(r.committed_at) + 86400000) end
    if r.monthly_reconciled == '0' then expected_expiry = math.max(expected_expiry, tonumber(r.committed_at) + 2592000000) end
    if tonumber(r.retained_until) ~= expected_expiry then return nil end
    if (r.daily_budget == 'n' and r.daily_reconciled ~= '1')
      or (r.daily_budget ~= 'n' and r.durable == '0' and r.daily_reconciled ~= '0')
      or (r.monthly_budget == 'n' and r.monthly_reconciled ~= '1')
      or (r.monthly_budget ~= 'n' and r.durable == '0' and r.monthly_reconciled ~= '0') then return nil end
  end
  return r
end
local function encode_record(r)
  return table.concat({r.schema, r.fingerprint, r.key, r.state, r.active_until,
    r.retained_until, r.accepted_at, r.estimated_tokens, r.estimated_cost,
    r.committed_at, r.actual_tokens, r.actual_cost, r.durable, r.daily_reconciled,
    r.monthly_reconciled, r.business_commit, r.rpm_limit, r.tpm_limit,
    r.daily_budget, r.monthly_budget, r.daily_spend, r.monthly_spend,
    r.retention_ms, r.next_expiry}, '|')
end
local function valid_reservation_locator(value)
  if not value then return nil end
  local schema, key = string.match(value, '^([^|]+)|([^|]+)$')
  if schema ~= '1' or not valid_hex(key) then return false end
  return key
end
local function valid_operation_locator(value)
  if not value then return nil end
  local schema, key, fingerprint = string.match(value, '^([^|]+)|([^|]+)|([^|]+)$')
  if schema ~= '1' or not valid_hex(key) or not valid_hex(fingerprint) then return false end
  return key, fingerprint
end
local function read_reservation_locator(key)
  local value = redis.call('GET', key)
  if not value then return nil end
  if redis.call('PTTL', key) <= 0 then return false end
  return valid_reservation_locator(value)
end
local function read_operation_locator(key)
  local value = redis.call('GET', key)
  if not value then return nil end
  if redis.call('PTTL', key) <= 0 then return false end
  return valid_operation_locator(value)
end
local function validate_record_pair(value, score, expected_key)
  local record = parse_record(value)
  if not record or record.key ~= expected_key or not valid_positive(score)
    or tonumber(score) ~= tonumber(record.next_expiry) then return nil end
  return record
end
local function plan_prune_target(now_ms, expected_key, record_limit, replay_limit, replay_validator)
  local record_count, lifecycle_count = redis.call('HLEN', KEYS[2]), redis.call('ZCARD', KEYS[3])
  local replay_count, replay_expiry_count = redis.call('HLEN', KEYS[4]), redis.call('ZCARD', KEYS[5])
  if record_count ~= lifecycle_count or replay_count ~= replay_expiry_count
    or record_count > record_limit or replay_count > replay_limit then return nil end
  local replay_due = redis.call('ZRANGEBYSCORE', KEYS[5], '-inf', now_ms, 'LIMIT', 0, 257)
  local lifecycle_due = redis.call('ZRANGEBYSCORE', KEYS[3], '-inf', now_ms, 'LIMIT', 0, 257)
  if #replay_due > 256 or #lifecycle_due > 256
    or #replay_due + #lifecycle_due > 256 then return false end
  for _, operation_id in ipairs(replay_due) do
    if not replay_validator(redis.call('HGET', KEYS[4], operation_id),
      redis.call('ZSCORE', KEYS[5], operation_id)) then return nil end
  end
  local due_records = {}
  for index, reservation_id in ipairs(lifecycle_due) do
    local record = validate_record_pair(redis.call('HGET', KEYS[2], reservation_id),
      redis.call('ZSCORE', KEYS[3], reservation_id), expected_key)
    if not record or tonumber(record.next_expiry) > now_ms then return nil end
    due_records[index] = {reservation_id, record}
  end
  return {replay_due=replay_due, due_records=due_records}
end
local function aggregate_target_records(now_ms, expected_key, record_limit,
  daily_snapshot, monthly_snapshot, reconcile, override_id, override_record)
  local record_count = redis.call('HLEN', KEYS[2])
  if record_count > record_limit or record_count ~= redis.call('ZCARD', KEYS[3]) then
    return nil
  end
  local flattened = redis.call('HGETALL', KEYS[2])
  if #flattened ~= record_count * 2 then return nil end
  local parsed, updates = {}, {}
  for index = 1, #flattened, 2 do
    local reservation_id, value = flattened[index], flattened[index + 1]
    local record = validate_record_pair(value, redis.call('ZSCORE', KEYS[3], reservation_id), expected_key)
    if not record then return nil end
    if override_id and reservation_id == override_id then record = override_record end
    parsed[#parsed + 1] = {reservation_id, record}
  end
  local result = {rate_count=0, rate_tokens=0, active_cost=0,
    daily_unreconciled=0, monthly_unreconciled=0, oldest=nil}
  local cutoff = now_ms - 60000
  for _, pair in ipairs(parsed) do
    local reservation_id, record = pair[1], pair[2]
    if reconcile and record.state == 'committed' and record.durable == '1' then
      local changed = false
      if record.daily_reconciled == '0' and daily_snapshot >= tonumber(record.business_commit) then
        record.daily_reconciled, changed = '1', true
      end
      if record.monthly_reconciled == '0'
        and monthly_snapshot >= tonumber(record.business_commit) then
        record.monthly_reconciled, changed = '1', true
      end
      if changed then
        local evidence_expiry = tonumber(record.committed_at) + 60000
        if record.daily_reconciled == '0' then
          evidence_expiry = math.max(evidence_expiry, tonumber(record.committed_at) + 86400000)
        end
        if record.monthly_reconciled == '0' then
          evidence_expiry = math.max(evidence_expiry, tonumber(record.committed_at) + 2592000000)
        end
        record.retained_until = string.format('%.0f', evidence_expiry)
        record.next_expiry = record.retained_until
        updates[#updates + 1] = {reservation_id, record}
      end
    end
    if record.state == 'active' and tonumber(record.active_until) > now_ms then
      result.active_cost = result.active_cost + tonumber(record.estimated_cost)
      if tonumber(record.accepted_at) > cutoff then
        result.rate_count = result.rate_count + 1
        result.rate_tokens = result.rate_tokens + tonumber(record.estimated_tokens)
        result.oldest = result.oldest and math.min(result.oldest,
          tonumber(record.accepted_at)) or tonumber(record.accepted_at)
      end
    elseif record.state == 'committed' then
      if tonumber(record.committed_at) > cutoff then
        result.rate_count = result.rate_count + 1
        result.rate_tokens = result.rate_tokens + tonumber(record.actual_tokens)
        result.oldest = result.oldest and math.min(result.oldest,
          tonumber(record.committed_at)) or tonumber(record.committed_at)
      end
      if record.daily_reconciled == '0' then
        result.daily_unreconciled = result.daily_unreconciled + tonumber(record.actual_cost)
      end
      if record.monthly_reconciled == '0' then
        result.monthly_unreconciled = result.monthly_unreconciled + tonumber(record.actual_cost)
      end
    end
  end
  return result, updates
end
local function ready_epoch(expected)
  local count = redis.call('HLEN', KEYS[1])
  if count == 0 then
    return expected == '1', 'ready', expected == '1'
  elseif count ~= 3 then return nil end
  local epoch = redis.call('HMGET', KEYS[1], 'schema_version', 'epoch', 'state')
  if #epoch ~= 3 or epoch[1] ~= '1' or not valid_positive(epoch[2])
    or (epoch[3] ~= 'ready' and epoch[3] ~= 'reconciling') then return nil end
  return epoch[2] == expected and epoch[3] == 'ready', epoch[3], false
end
"""

_QUOTA_RESERVE_SCRIPT = (
    "-- omni:quota_reserve:v1\n"
    + _QUOTA_LUA_COMMON
    + r"""
local function valid_replay(value, score)
  if not value or not score or not valid_positive(score) then return false end
  local schema, fingerprint, status, reason, retry_after, expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]+)|([^|]*)|([^|]+)|([^|]+)$')
  return schema == '1' and valid_hex(fingerprint)
    and (status == 'accepted' or status == 'denied')
    and (reason == '' or reason == 'rpm' or reason == 'tpm' or reason == 'daily_budget'
      or reason == 'monthly_budget' or reason == 'capacity')
    and valid_uint(retry_after) and valid_positive(expiry)
    and tonumber(expiry) == tonumber(score)
    and ((status == 'accepted' and reason == '' and retry_after == '0')
      or (status == 'denied' and reason ~= ''))
end
local fenced, epoch_state, bootstrap_epoch = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then
  return {'1', 'denied', ARGV[2], epoch_state == 'reconciling'
    and 'reconciling' or 'stale_epoch', '0', '0'}
end
if not valid_hex(ARGV[3]) or not valid_hex(ARGV[4]) or not valid_positive(ARGV[6])
  or not valid_positive(ARGV[7]) or not valid_positive(ARGV[8])
  or not valid_positive(ARGV[9]) or not valid_decimal(ARGV[10])
  or not valid_uint(ARGV[11]) or not valid_decimal(ARGV[12])
  or (ARGV[13] ~= '' and not valid_positive(ARGV[13]))
  or (ARGV[14] ~= '' and not valid_positive(ARGV[14]))
  or (ARGV[15] ~= '' and not valid_decimal(ARGV[15]))
  or (ARGV[16] ~= '' and not valid_decimal(ARGV[16]))
  or not valid_decimal(ARGV[17]) or not valid_decimal(ARGV[18])
  or not valid_decimal(ARGV[19]) or not valid_decimal(ARGV[20]) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local reservation_key = read_reservation_locator(KEYS[6])
if reservation_key == false then return redis.error_reply('COORDINATION_CORRUPT') end
if reservation_key and reservation_key ~= ARGV[3] then
  return {'1', 'denied', ARGV[2], 'conflict', '0', '0'}
end
local operation_key, operation_fingerprint = read_operation_locator(KEYS[7])
if operation_key == false then return redis.error_reply('COORDINATION_CORRUPT') end
if operation_key and (operation_key ~= ARGV[3] or operation_fingerprint ~= ARGV[4]) then
  return {'1', 'denied', ARGV[2], 'conflict', '0', '0'}
end
local clock = redis.call('TIME')
local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
local plan = plan_prune_target(now_ms, ARGV[3], tonumber(ARGV[8]), tonumber(ARGV[9]), valid_replay)
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not plan then
  return {'1', 'denied', ARGV[2], 'reconciliation_required', '0', '0'}
end
if reservation_key and not redis.call('HGET', KEYS[2], ARGV[2]) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local replay, replay_expiry = redis.call('HGET', KEYS[4], ARGV[5]),
  redis.call('ZSCORE', KEYS[5], ARGV[5])
if (replay or replay_expiry) and not valid_replay(replay, replay_expiry) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if operation_key and not replay then return redis.error_reply('COORDINATION_CORRUPT') end
local aggregate, aggregate_updates = aggregate_target_records(now_ms, ARGV[3], tonumber(ARGV[8]),
  tonumber(ARGV[19]), tonumber(ARGV[20]), true)
if not aggregate then return redis.error_reply('COORDINATION_CORRUPT') end
local existing = redis.call('HGET', KEYS[2], ARGV[2])
local existing_record = existing and validate_record_pair(existing,
  redis.call('ZSCORE', KEYS[3], ARGV[2]), ARGV[3]) or nil
if existing and not existing_record then return redis.error_reply('COORDINATION_CORRUPT') end
local replay_status, replay_reason, replay_retry = nil, nil, nil
if replay then
  local _, fingerprint, status, reason, retry_after =
    string.match(replay, '^([^|]+)|([^|]+)|([^|]+)|([^|]*)|([^|]+)|([^|]+)$')
  if fingerprint == ARGV[4] then replay_status, replay_reason, replay_retry = status, reason, retry_after
  else replay_status, replay_reason, replay_retry = 'denied', 'conflict', '0' end
end
local reason, retry_after = '', '0'
if not replay_status and existing_record then
  if existing_record.fingerprint == ARGV[4] then replay_status, replay_reason, replay_retry = 'accepted', '', '0'
  else replay_status, replay_reason, replay_retry = 'denied', 'conflict', '0' end
elseif not replay_status and redis.call('HLEN', KEYS[4]) >= tonumber(ARGV[9]) then
  reason = 'reconciliation_required'
elseif not replay_status and redis.call('HLEN', KEYS[2]) >= tonumber(ARGV[8]) then reason = 'capacity'
elseif ARGV[13] ~= '' and aggregate.rate_count >= tonumber(ARGV[13]) then reason = 'rpm'
elseif ARGV[14] ~= '' and aggregate.rate_tokens + tonumber(ARGV[11]) > tonumber(ARGV[14]) then reason = 'tpm'
elseif ARGV[15] ~= '' and tonumber(ARGV[17]) + aggregate.daily_unreconciled
  + aggregate.active_cost + tonumber(ARGV[12]) > tonumber(ARGV[15]) then reason = 'daily_budget'
elseif ARGV[16] ~= '' and tonumber(ARGV[18]) + aggregate.monthly_unreconciled
  + aggregate.active_cost + tonumber(ARGV[12]) > tonumber(ARGV[16]) then reason = 'monthly_budget' end
if reason == 'rpm' or reason == 'tpm' then
  retry_after = aggregate.oldest and tostring(math.max(1,
    math.ceil((aggregate.oldest + 60000 - now_ms) / 1000))) or '1'
end
-- apply validated mutation
if bootstrap_epoch then redis.call('HSET', KEYS[1], 'schema_version', '1', 'epoch', '1', 'state', 'ready') end
if #plan.replay_due > 0 then redis.call('HDEL', KEYS[4], unpack(plan.replay_due)); redis.call('ZREM', KEYS[5], unpack(plan.replay_due)) end
for _, pair in ipairs(plan.due_records) do
  local reservation_id, record = pair[1], pair[2]
  if record.state == 'active' and tonumber(record.active_until) <= now_ms and tonumber(record.retained_until) > now_ms then
    record.state, record.next_expiry = 'expired', record.retained_until
    redis.call('HSET', KEYS[2], reservation_id, encode_record(record)); redis.call('ZADD', KEYS[3], tonumber(record.next_expiry), reservation_id)
  else redis.call('HDEL', KEYS[2], reservation_id); redis.call('ZREM', KEYS[3], reservation_id) end
end
for _, pair in ipairs(aggregate_updates) do redis.call('HSET', KEYS[2], pair[1], encode_record(pair[2])); redis.call('ZADD', KEYS[3], tonumber(pair[2].next_expiry), pair[1]) end
if replay_status then return {'1', replay_status, ARGV[2], replay_reason, replay_retry, '1'} end
if reason == 'reconciliation_required' then return {'1', 'denied', ARGV[2], reason, '0', '0'} end
if reason ~= '' then
  local denial_expiry = string.format('%.0f', now_ms + tonumber(ARGV[6]))
  redis.call('HSET', KEYS[4], ARGV[5], table.concat(
    {'1', ARGV[4], 'denied', reason, retry_after, denial_expiry}, '|'))
  redis.call('ZADD', KEYS[5], tonumber(denial_expiry), ARGV[5])
  redis.call('SET', KEYS[7], '1|' .. ARGV[3] .. '|' .. ARGV[4], 'PXAT', denial_expiry)
  return {'1', 'denied', ARGV[2], reason, retry_after, '0'}
end
local active_until = string.format('%.0f', now_ms + tonumber(ARGV[6]))
local retained_until = string.format('%.0f', now_ms + tonumber(ARGV[7]))
local record = {
  schema='1', fingerprint=ARGV[4], key=ARGV[3], state='active', active_until=active_until,
  retained_until=retained_until, accepted_at=string.format('%.0f', now_ms),
  estimated_tokens=ARGV[11], estimated_cost=ARGV[12], committed_at='0', actual_tokens='0',
  actual_cost='0', durable='0', daily_reconciled=ARGV[15] == '' and '1' or '0',
  monthly_reconciled=ARGV[16] == '' and '1' or '0', business_commit='0',
  rpm_limit=ARGV[13] == '' and 'n' or ARGV[13], tpm_limit=ARGV[14] == '' and 'n' or ARGV[14],
  daily_budget=ARGV[15] == '' and 'n' or ARGV[15],
  monthly_budget=ARGV[16] == '' and 'n' or ARGV[16], daily_spend=ARGV[17],
  monthly_spend=ARGV[18], retention_ms=ARGV[7], next_expiry=active_until
}
redis.call('HSET', KEYS[2], ARGV[2], encode_record(record))
redis.call('ZADD', KEYS[3], tonumber(active_until), ARGV[2])
redis.call('HSET', KEYS[4], ARGV[5], table.concat(
  {'1', ARGV[4], 'accepted', '', '0', retained_until}, '|'))
redis.call('ZADD', KEYS[5], tonumber(retained_until), ARGV[5])
redis.call('SET', KEYS[6], '1|' .. ARGV[3], 'PXAT', retained_until)
redis.call('SET', KEYS[7], '1|' .. ARGV[3] .. '|' .. ARGV[4], 'PXAT', retained_until)
return {'1', 'accepted', ARGV[2], '', '0', '0'}
"""
)

_QUOTA_COMMIT_SCRIPT = (
    "-- omni:quota_commit:v1\n"
    + _QUOTA_LUA_COMMON
    + r"""
local function valid_replay(value, score)
  if not value or not score or not valid_positive(score) then return false end
  local schema, fingerprint, status, overspent, expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
  return schema == '1' and valid_hex(fingerprint)
    and (status == 'committed' or status == 'not_committed')
    and (overspent == '0' or overspent == '1') and valid_positive(expiry)
    and tonumber(expiry) == tonumber(score)
    and (status == 'committed' or overspent == '0')
end
local fenced, _, bootstrap_epoch = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then return {'1', 'not_committed', '0', '0'} end
if not valid_hex(ARGV[2]) or not valid_hex(ARGV[5]) or not valid_decimal(ARGV[6])
  or (ARGV[7] ~= '' and not valid_uint(ARGV[7]))
  or (ARGV[8] ~= '' and not valid_decimal(ARGV[8]))
  or (ARGV[9] ~= '0' and ARGV[9] ~= '1') or not valid_positive(ARGV[10])
  or not valid_positive(ARGV[11]) or not valid_positive(ARGV[12]) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local reservation_key = read_reservation_locator(KEYS[6])
if reservation_key == false then return redis.error_reply('COORDINATION_CORRUPT') end
if reservation_key and reservation_key ~= ARGV[5] then return {'1', 'not_committed', '0', '0'} end
local operation_key, operation_fingerprint = read_operation_locator(KEYS[7])
if operation_key == false then return redis.error_reply('COORDINATION_CORRUPT') end
if operation_key and (operation_key ~= ARGV[5] or operation_fingerprint ~= ARGV[2]) then
  return {'1', 'not_committed', '0', '0'}
end
local clock = redis.call('TIME')
local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
local plan = plan_prune_target(now_ms, ARGV[5], tonumber(ARGV[10]), tonumber(ARGV[11]), valid_replay)
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not plan then return {'1', 'reconciliation_required', '0', '0'} end
if reservation_key and not redis.call('HGET', KEYS[2], ARGV[4]) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local replay, replay_expiry = redis.call('HGET', KEYS[4], ARGV[3]),
  redis.call('ZSCORE', KEYS[5], ARGV[3])
if (replay or replay_expiry) and not valid_replay(replay, replay_expiry) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if operation_key and not replay then return redis.error_reply('COORDINATION_CORRUPT') end
local replay_status, replay_overspent = nil, nil
if replay then
  local _, fingerprint, status, overspent =
    string.match(replay, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
  if fingerprint == ARGV[2] then replay_status, replay_overspent = status, overspent
  else replay_status, replay_overspent = 'not_committed', '0' end
end
if not replay_status and redis.call('HLEN', KEYS[4]) >= tonumber(ARGV[11]) then
  return {'1', 'reconciliation_required', '0', '0'}
end
local encoded = redis.call('HGET', KEYS[2], ARGV[4])
local record = encoded and validate_record_pair(encoded,
  redis.call('ZSCORE', KEYS[3], ARGV[4]), ARGV[5]) or nil
if encoded and not record then return redis.error_reply('COORDINATION_CORRUPT') end
local expiry = string.format('%.0f', now_ms + tonumber(ARGV[12]))
local status, overspent = 'not_committed', '0'
if record then expiry = record.retained_until end
if not replay_status and record and record.state == 'active' and tonumber(record.active_until) > now_ms then
  record.state = 'committed'
  record.committed_at = string.format('%.0f', now_ms)
  record.actual_tokens = ARGV[7] == '' and record.estimated_tokens or ARGV[7]
  record.actual_cost = ARGV[8] == '' and record.estimated_cost or ARGV[8]
  record.durable = ARGV[9]
  record.daily_reconciled = record.daily_budget == 'n' and '1' or '0'
  record.monthly_reconciled = record.monthly_budget == 'n' and '1' or '0'
  record.business_commit = ARGV[6]
  local evidence_expiry = now_ms + 60000
  if record.daily_reconciled == '0' then evidence_expiry = math.max(evidence_expiry, now_ms + 86400000) end
  if record.monthly_reconciled == '0' then evidence_expiry = math.max(evidence_expiry, now_ms + 2592000000) end
  record.retained_until = string.format('%.0f', evidence_expiry)
  record.next_expiry = record.retained_until
  if not parse_record(encode_record(record)) then return redis.error_reply('COORDINATION_CORRUPT') end
  local aggregate = aggregate_target_records(now_ms, ARGV[5], tonumber(ARGV[10]), 0, 0, false,
    ARGV[4], record)
  if not aggregate then return redis.error_reply('COORDINATION_CORRUPT') end
  local overspent_value =
    (record.tpm_limit ~= 'n' and aggregate.rate_tokens > tonumber(record.tpm_limit))
    or (record.daily_budget ~= 'n' and tonumber(record.daily_spend)
      + aggregate.active_cost + aggregate.daily_unreconciled > tonumber(record.daily_budget))
    or (record.monthly_budget ~= 'n' and tonumber(record.monthly_spend)
      + aggregate.active_cost + aggregate.monthly_unreconciled > tonumber(record.monthly_budget))
  overspent = overspent_value and '1' or '0'
  status, expiry = 'committed', record.retained_until
end
-- apply validated mutation
if bootstrap_epoch then redis.call('HSET', KEYS[1], 'schema_version', '1', 'epoch', '1', 'state', 'ready') end
if #plan.replay_due > 0 then redis.call('HDEL', KEYS[4], unpack(plan.replay_due)); redis.call('ZREM', KEYS[5], unpack(plan.replay_due)) end
for _, pair in ipairs(plan.due_records) do
  local reservation_id, due = pair[1], pair[2]
  if due.state == 'active' and tonumber(due.active_until) <= now_ms and tonumber(due.retained_until) > now_ms then
    due.state, due.next_expiry = 'expired', due.retained_until
    redis.call('HSET', KEYS[2], reservation_id, encode_record(due)); redis.call('ZADD', KEYS[3], tonumber(due.next_expiry), reservation_id)
  else redis.call('HDEL', KEYS[2], reservation_id); redis.call('ZREM', KEYS[3], reservation_id) end
end
if replay_status then return {'1', replay_status, replay_overspent, '1'} end
if record and status == 'committed' then redis.call('HSET', KEYS[2], ARGV[4], encode_record(record)); redis.call('ZADD', KEYS[3], tonumber(record.next_expiry), ARGV[4]); redis.call('SET', KEYS[6], '1|' .. ARGV[5], 'PXAT', expiry) end
redis.call('HSET', KEYS[4], ARGV[3], table.concat(
  {'1', ARGV[2], status, overspent, expiry}, '|'))
redis.call('ZADD', KEYS[5], tonumber(expiry), ARGV[3])
redis.call('SET', KEYS[7], '1|' .. ARGV[5] .. '|' .. ARGV[2], 'PXAT', expiry)
return {'1', status, overspent, '0'}
"""
)

_QUOTA_RELEASE_SCRIPT = (
    "-- omni:quota_release:v1\n"
    + _QUOTA_LUA_COMMON
    + r"""
local function valid_replay(value, score)
  if not value or not score or not valid_positive(score) then return false end
  local schema, fingerprint, released, expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
  return schema == '1' and valid_hex(fingerprint) and (released == '0' or released == '1')
    and valid_positive(expiry) and tonumber(expiry) == tonumber(score)
end
local fenced, _, bootstrap_epoch = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then return {'1', 'ok', '0', '0'} end
if not valid_hex(ARGV[2]) or not valid_hex(ARGV[5]) or not valid_positive(ARGV[6])
  or not valid_positive(ARGV[7]) or not valid_positive(ARGV[8]) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local reservation_key = read_reservation_locator(KEYS[6])
if reservation_key == false then return redis.error_reply('COORDINATION_CORRUPT') end
if reservation_key and reservation_key ~= ARGV[5] then return {'1', 'ok', '0', '0'} end
local operation_key, operation_fingerprint = read_operation_locator(KEYS[7])
if operation_key == false then return redis.error_reply('COORDINATION_CORRUPT') end
if operation_key and (operation_key ~= ARGV[5] or operation_fingerprint ~= ARGV[2]) then
  return {'1', 'ok', '0', '0'}
end
local clock = redis.call('TIME')
local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
local plan = plan_prune_target(now_ms, ARGV[5], tonumber(ARGV[7]), tonumber(ARGV[8]), valid_replay)
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not plan then return {'1', 'reconciliation_required', '0', '0'} end
if reservation_key and not redis.call('HGET', KEYS[2], ARGV[4]) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local replay, replay_expiry = redis.call('HGET', KEYS[4], ARGV[3]),
  redis.call('ZSCORE', KEYS[5], ARGV[3])
if (replay or replay_expiry) and not valid_replay(replay, replay_expiry) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if operation_key and not replay then return redis.error_reply('COORDINATION_CORRUPT') end
local replayed = false
if replay then
  local _, fingerprint = string.match(replay, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
  replayed = fingerprint == ARGV[2]
end
if not replay and redis.call('HLEN', KEYS[4]) >= tonumber(ARGV[8]) then
  return {'1', 'reconciliation_required', '0', '0'}
end
local encoded = redis.call('HGET', KEYS[2], ARGV[4])
local record = encoded and validate_record_pair(encoded,
  redis.call('ZSCORE', KEYS[3], ARGV[4]), ARGV[5]) or nil
if encoded and not record then return redis.error_reply('COORDINATION_CORRUPT') end
local released, expiry = '0', string.format('%.0f', now_ms + tonumber(ARGV[6]))
if not replay and record then
  expiry = record.retained_until
  if record.state == 'active' and tonumber(record.active_until) > now_ms then
    released, record.state, record.next_expiry = '1', 'released', record.retained_until
    if not parse_record(encode_record(record)) then return redis.error_reply('COORDINATION_CORRUPT') end
  end
end
-- apply validated mutation
if bootstrap_epoch then redis.call('HSET', KEYS[1], 'schema_version', '1', 'epoch', '1', 'state', 'ready') end
if #plan.replay_due > 0 then redis.call('HDEL', KEYS[4], unpack(plan.replay_due)); redis.call('ZREM', KEYS[5], unpack(plan.replay_due)) end
for _, pair in ipairs(plan.due_records) do
  local reservation_id, due = pair[1], pair[2]
  if due.state == 'active' and tonumber(due.active_until) <= now_ms and tonumber(due.retained_until) > now_ms then
    due.state, due.next_expiry = 'expired', due.retained_until
    redis.call('HSET', KEYS[2], reservation_id, encode_record(due)); redis.call('ZADD', KEYS[3], tonumber(due.next_expiry), reservation_id)
  else redis.call('HDEL', KEYS[2], reservation_id); redis.call('ZREM', KEYS[3], reservation_id) end
end
if replay then return {'1', 'ok', '0', replayed and '1' or '0'} end
if released == '1' then redis.call('HSET', KEYS[2], ARGV[4], encode_record(record)); redis.call('ZADD', KEYS[3], tonumber(record.next_expiry), ARGV[4]) end
redis.call('HSET', KEYS[4], ARGV[3], table.concat({'1', ARGV[2], released, expiry}, '|'))
redis.call('ZADD', KEYS[5], tonumber(expiry), ARGV[3])
redis.call('SET', KEYS[7], '1|' .. ARGV[5] .. '|' .. ARGV[2], 'PXAT', expiry)
return {'1', 'ok', released, '0'}
"""
)

SCRIPT_SOURCES = {
    "epoch_read": _EPOCH_READ_SCRIPT,
    "epoch_advance": _EPOCH_ADVANCE_SCRIPT,
    "epoch_ready": _EPOCH_READY_SCRIPT,
    "cas": _CAS_SCRIPT,
    "invalidation": _INVALIDATION_SCRIPT,
    "invalidation_read": _INVALIDATION_READ_SCRIPT,
    "increment": _INCREMENT_SCRIPT,
    "lock_release": _LOCK_RELEASE_SCRIPT,
    "quota_reserve": _QUOTA_RESERVE_SCRIPT,
    "quota_commit": _QUOTA_COMMIT_SCRIPT,
    "quota_release": _QUOTA_RELEASE_SCRIPT,
}


def _validate_identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= MAX_IDENTIFIER_LENGTH:
        raise ValueError(f"{label} is invalid.")
    if any(ord(character) < 32 or ord(character) > 126 for character in value):
        raise ValueError(f"{label} is invalid.")
    return value


def _validate_redis_url(value: object) -> str:
    if not isinstance(value, str) or not value or any(ord(character) < 32 for character in value):
        raise ValueError("Redis URL is invalid.")
    try:
        parsed = urlsplit(value)
        _ = parsed.port
    except ValueError:
        raise ValueError("Redis URL is invalid.") from None
    if parsed.scheme not in {"redis", "rediss", "unix"}:
        raise ValueError("Redis URL is invalid.")
    if parsed.scheme == "unix":
        valid_location = bool(parsed.path)
    else:
        valid_location = bool(parsed.hostname)
    if not valid_location or parsed.fragment:
        raise ValueError("Redis URL is invalid.")
    return value


def _ttl_ms(value: object, *, optional: bool = False) -> int | None:
    if optional and value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("TTL is invalid.")
    number = float(value)
    if not math.isfinite(number) or not 1.0 <= number <= MAX_TTL_SECONDS:
        raise ValueError("TTL is invalid.")
    return math.ceil(number * 1000)


def _integer_bytes(value: int) -> bytes:
    return str(value).encode("ascii")


def _float_bytes(value: float) -> bytes:
    return format(float(value), ".17g").encode("ascii")


def _quota_operation_bytes(kind: str, operation_id: str) -> bytes:
    return f"{kind}:{operation_id}".encode("ascii")


def _fingerprint(*parts: object) -> bytes:
    digest = hashlib.sha256()
    for part in parts:
        if isinstance(part, bytes):
            encoded = part
        elif isinstance(part, float):
            encoded = part.hex().encode("ascii")
        else:
            encoded = str(part).encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest().encode("ascii")


def _quota_retention_ms(request: QuotaReservationRequest) -> int:
    """Return the active-or-evidence retention window without trusting the caller clock."""
    windows = [_QUOTA_RATE_WINDOW_MS]
    if request.daily_budget_usd is not None:
        windows.append(86_400_000)
    if request.monthly_budget_usd is not None:
        windows.append(_QUOTA_MONTHLY_WINDOW_MS)
    ttl = _ttl_ms(request.ttl_seconds)
    assert ttl is not None
    return min(max(ttl, *windows), _QUOTA_MONTHLY_WINDOW_MS)


def _strict_array(reply: object, length: int) -> list[object]:
    if not isinstance(reply, list) or len(reply) != length:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    if reply[0] != _SCHEMA or not isinstance(reply[0], bytes):
        raise CoordinationCorruptError("Coordination reply is invalid.")
    if any(not isinstance(value, bytes) for value in reply):
        raise CoordinationCorruptError("Coordination reply is invalid.")
    return reply


def _strict_positive_int(value: bytes) -> int:
    if not value or (len(value) > 1 and value.startswith(b"0")) or not value.isdigit():
        raise CoordinationCorruptError("Coordination reply is invalid.")
    result = int(value)
    if not 1 <= result <= MAX_COORDINATION_INTEGER:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    return result


def _decode_epoch_reply(reply: object) -> Epoch:
    values = _strict_array(reply, 4)
    if values[1] == b"reconciliation_required":
        if values[2:] != [b"", b""]:
            raise CoordinationCorruptError("Coordination reply is invalid.")
        raise CoordinationReconciliationRequiredError("Reconciliation is required.")
    if values[1] != b"ok":
        raise CoordinationCorruptError("Coordination reply is invalid.")
    try:
        state = EpochState(values[3].decode("ascii"))
    except (UnicodeDecodeError, ValueError):
        raise CoordinationCorruptError("Coordination reply is invalid.") from None
    return Epoch(_strict_positive_int(values[2]), state)


def _decode_cas_reply(reply: object) -> CasResult:
    values = _strict_array(reply, 4)
    if values[1] == b"reconciliation_required":
        if values[2:] != [b"", b"0"]:
            raise CoordinationCorruptError("Coordination reply is invalid.")
        raise CoordinationReconciliationRequiredError("Reconciliation is required.")
    if values[1] not in {b"applied", b"not_applied"} or values[3] not in {b"0", b"1"}:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    applied = values[1] == b"applied"
    if applied == (values[2] == b""):
        raise CoordinationCorruptError("Coordination reply is invalid.")
    revision = _strict_positive_int(values[2]) if applied else None
    return CasResult(applied, revision, values[3] == b"1")


def _decode_invalidation_reply(reply: object) -> InvalidationResult:
    values = _strict_array(reply, 4)
    if values[1] == b"reconciliation_required":
        if values[2:] != [b"", b"0"]:
            raise CoordinationCorruptError("Coordination reply is invalid.")
        raise CoordinationReconciliationRequiredError("Reconciliation is required.")
    if values[1] not in {b"applied", b"not_applied"} or values[3] not in {b"0", b"1"}:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    applied = values[1] == b"applied"
    if applied == (values[2] == b""):
        raise CoordinationCorruptError("Coordination reply is invalid.")
    if not applied and values[3] != b"0":
        raise CoordinationCorruptError("Coordination reply is invalid.")
    generation = _strict_positive_int(values[2]) if applied else None
    return InvalidationResult(applied, generation, values[3] == b"1")


def _decode_generation_reply(reply: object) -> InvalidationGeneration:
    values = _strict_array(reply, 3)
    if values[1] != b"ok":
        raise CoordinationCorruptError("Coordination reply is invalid.")
    generation = None if values[2] == b"" else _strict_positive_int(values[2])
    return InvalidationGeneration(generation)


def _decode_integer_reply(reply: object, *, nonnegative: bool = False) -> int:
    values = _strict_array(reply, 3)
    if values[1] != b"ok" or not values[2]:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    raw = values[2]
    if raw.startswith(b"-"):
        digits = raw[1:]
    else:
        digits = raw
    if (
        not digits
        or not digits.isdigit()
        or (len(digits) > 1 and digits.startswith(b"0"))
        or raw == b"-0"
    ):
        raise CoordinationCorruptError("Coordination reply is invalid.")
    result = int(raw)
    if abs(result) > MAX_COORDINATION_INTEGER or (nonnegative and result < 0):
        raise CoordinationCorruptError("Coordination reply is invalid.")
    return result


def _decode_quota_reserve_reply(reply: object) -> QuotaReservationDecision:
    values = _strict_array(reply, 6)
    if values[1] not in {b"accepted", b"denied"} or values[5] not in {b"0", b"1"}:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    try:
        reservation_id = values[2].decode("ascii")
        reason = values[3].decode("ascii")
    except UnicodeDecodeError:
        raise CoordinationCorruptError("Coordination reply is invalid.") from None
    retry_after = _strict_positive_int(values[4]) if values[4] != b"0" else 0
    try:
        return QuotaReservationDecision(
            values[1] == b"accepted", reservation_id, reason, retry_after, values[5] == b"1"
        )
    except ValueError as exc:
        raise CoordinationCorruptError("Coordination reply is invalid.") from exc


def _decode_quota_commit_reply(reply: object) -> QuotaCommitResult:
    values = _strict_array(reply, 4)
    if values[1] == b"reconciliation_required":
        if values[2:] != [b"0", b"0"]:
            raise CoordinationCorruptError("Coordination reply is invalid.")
        raise CoordinationReconciliationRequiredError("Reconciliation is required.")
    if (
        values[1] not in {b"committed", b"not_committed"}
        or values[2] not in {b"0", b"1"}
        or values[3] not in {b"0", b"1"}
    ):
        raise CoordinationCorruptError("Coordination reply is invalid.")
    try:
        return QuotaCommitResult(values[1] == b"committed", values[2] == b"1", values[3] == b"1")
    except ValueError as exc:
        raise CoordinationCorruptError("Coordination reply is invalid.") from exc


def _decode_quota_release_reply(reply: object) -> bool:
    values = _strict_array(reply, 4)
    if values[1] == b"reconciliation_required":
        if values[2:] != [b"0", b"0"]:
            raise CoordinationCorruptError("Coordination reply is invalid.")
        raise CoordinationReconciliationRequiredError("Reconciliation is required.")
    if values[1] != b"ok" or values[2] not in {b"0", b"1"} or values[3] not in {b"0", b"1"}:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    return values[2] == b"1"


class RedisStateStore:
    """Lazy, secret-safe Redis implementation of the coordination surface."""

    def __init__(
        self,
        redis_url: str,
        deployment_namespace: str = "omni-gateway",
        *,
        _coordination_replay_limit_for_testing: int | None = None,
        _quota_record_limit_for_testing: int | None = None,
        _redis_module_for_testing: Any = None,
    ) -> None:
        redis_url = _validate_redis_url(redis_url)
        namespace = validate_deployment_namespace(deployment_namespace)
        replay_limit = (
            _DEFAULT_REPLAY_LIMIT
            if _coordination_replay_limit_for_testing is None
            else _coordination_replay_limit_for_testing
        )
        if (
            isinstance(replay_limit, bool)
            or not isinstance(replay_limit, int)
            or not 1 <= replay_limit <= _DEFAULT_REPLAY_LIMIT
        ):
            raise ValueError("Coordination replay limit is invalid.")
        quota_record_limit = (
            _DEFAULT_REPLAY_LIMIT
            if _quota_record_limit_for_testing is None
            else _quota_record_limit_for_testing
        )
        if (
            isinstance(quota_record_limit, bool)
            or not isinstance(quota_record_limit, int)
            or not 1 <= quota_record_limit <= _DEFAULT_REPLAY_LIMIT
        ):
            raise ValueError("Quota record limit is invalid.")
        self._redis_url = redis_url
        self._redis_module = _redis_module_for_testing
        self._tag = hashlib.sha256(namespace.encode("ascii")).hexdigest()
        self._prefix = f"omni:{{{self._tag}}}:v1"
        self._replay_limit = replay_limit
        self._quota_record_limit = quota_record_limit
        self._client: Any = None
        self._scripts: dict[str, Any] = {}
        self._lock_tokens: weakref.WeakKeyDictionary[asyncio.Task[Any], dict[str, bytes]] = (
            weakref.WeakKeyDictionary()
        )
        self._closed = False
        self._lifecycle_lock = asyncio.Lock()

    def __repr__(self) -> str:
        state = "closed" if self._closed else "open"
        return f"RedisStateStore(deployment={self._tag!r}, state={state!r})"

    def _ensure_open(self) -> None:
        if self._closed:
            raise CoordinationUnavailableError("Coordination store is closed.")

    def _key(self, category: str, logical_name: str | None = None) -> str:
        suffix = category
        if logical_name is not None:
            suffix += ":" + hashlib.sha256(logical_name.encode("ascii")).hexdigest()
        return f"{self._prefix}:{suffix}"

    def _quota_bucket_key(self, category: str, key_digest: bytes) -> str:
        if len(key_digest) != 64 or any(byte not in b"0123456789abcdef" for byte in key_digest):
            raise CoordinationCorruptError("Stored coordination state is invalid.")
        return f"{self._prefix}:{category}:{key_digest.decode('ascii')}"

    def _quota_keys(self, key_digest: bytes, reservation_id: str, operation_id: str) -> list[str]:
        """The complete, explicit key bundle for each quota script invocation."""
        return [
            self._key("epoch"),
            self._quota_bucket_key("quota:records", key_digest),
            self._quota_bucket_key("quota:lifecycle", key_digest),
            self._quota_bucket_key("quota:replay", key_digest),
            self._quota_bucket_key("quota:replay-expiry", key_digest),
            self._key("quota:locator", reservation_id),
            self._key("quota:operation", operation_id),
        ]

    async def _quota_locator(
        self, category: str, identifier: str
    ) -> tuple[bytes, bytes | None] | None:
        value = await self._run_command("get", self._key(category, identifier))
        if value is None:
            return None
        if not isinstance(value, bytes):
            raise CoordinationCorruptError("Stored coordination state is invalid.")
        fields = value.split(b"|")
        expected_fields = 3 if category == "quota:operation" else 2
        if len(fields) != expected_fields or fields[0] != b"1":
            raise CoordinationCorruptError("Stored coordination state is invalid.")
        key_digest = fields[1]
        self._quota_bucket_key("quota:records", key_digest)
        fingerprint = fields[2] if expected_fields == 3 else None
        if fingerprint is not None:
            self._quota_bucket_key("quota:records", fingerprint)
        return key_digest, fingerprint

    async def _quota_routing_digest(self, reservation_id: str, operation_id: str) -> bytes:
        reservation = await self._quota_locator("quota:locator", reservation_id)
        operation = await self._quota_locator("quota:operation", operation_id)
        if operation is not None:
            return operation[0]
        if reservation is not None:
            return reservation[0]
        return _fingerprint("unknown-quota-target")

    async def _get_client(self) -> Any:
        self._ensure_open()
        if self._client is not None:
            return self._client
        async with self._lifecycle_lock:
            self._ensure_open()
            if self._client is not None:
                return self._client
            client: Any = None
            try:
                redis_module = self._redis_module or importlib.import_module("redis.asyncio")
                client = redis_module.from_url(self._redis_url, decode_responses=False)
                scripts = {
                    name: client.register_script(source) for name, source in SCRIPT_SOURCES.items()
                }
            except Exception:
                if client is not None:
                    try:
                        await client.aclose()
                    except Exception:
                        pass
                raise CoordinationUnavailableError("Redis coordination is unavailable.") from None
            self._client = client
            self._scripts = scripts
            return client

    async def _run_script(self, name: str, *, keys: list[str], args: list[object]) -> object:
        await self._get_client()
        try:
            return await self._scripts[name](keys=keys, args=args)
        except UnicodeError:
            raise CoordinationCorruptError("Coordination reply is invalid.") from None
        except Exception as exc:
            error_text = str(exc).upper()
            if any(marker in error_text for marker in _CORRUPT_DRIVER_ERROR_MARKERS):
                raise CoordinationCorruptError("Stored coordination state is invalid.") from None
            raise CoordinationUnavailableError("Redis coordination is unavailable.") from None

    async def _run_command(self, method: str, *args: object, **kwargs: object) -> object:
        client = await self._get_client()
        try:
            return await getattr(client, method)(*args, **kwargs)
        except UnicodeError:
            raise CoordinationCorruptError("Coordination reply is invalid.") from None
        except Exception as exc:
            error_text = str(exc).upper()
            if any(marker in error_text for marker in _CORRUPT_DRIVER_ERROR_MARKERS):
                raise CoordinationCorruptError("Stored coordination state is invalid.") from None
            raise CoordinationUnavailableError("Redis coordination is unavailable.") from None

    async def get(self, key: str) -> Optional[Any]:
        logical_key = _validate_identifier(key, "State key")
        reply = await self._run_command("get", self._key("generic", logical_key))
        if reply is not None and not isinstance(reply, bytes):
            raise CoordinationCorruptError("Coordination reply is invalid.")
        if reply is None:
            return None
        try:
            return reply.decode("utf-8")
        except UnicodeDecodeError:
            raise CoordinationCorruptError("Coordination reply is invalid.") from None

    async def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        logical_key = _validate_identifier(key, "State key")
        ttl = _ttl_ms(ttl_seconds, optional=True)
        payload = str(value).encode("utf-8")
        if len(payload) > MAX_PAYLOAD_BYTES:
            raise ValueError("State value is invalid.")
        options = {} if ttl is None else {"px": ttl}
        reply = await self._run_command(
            "set", self._key("generic", logical_key), payload, **options
        )
        if reply is not True:
            raise CoordinationUnavailableError("Redis coordination is unavailable.")

    async def delete(self, key: str) -> None:
        logical_key = _validate_identifier(key, "State key")
        reply = await self._run_command("delete", self._key("generic", logical_key))
        if isinstance(reply, bool) or not isinstance(reply, int) or reply not in {0, 1}:
            raise CoordinationCorruptError("Coordination reply is invalid.")

    async def increment(
        self, key: str, amount: int = 1, ttl_seconds: Optional[float] = None
    ) -> int:
        logical_key = _validate_identifier(key, "State key")
        if (
            isinstance(amount, bool)
            or not isinstance(amount, int)
            or not -MAX_COORDINATION_INTEGER <= amount <= MAX_COORDINATION_INTEGER
        ):
            raise ValueError("Increment amount is invalid.")
        ttl = _ttl_ms(ttl_seconds, optional=True)
        reply = await self._run_script(
            "increment",
            keys=[self._key("generic", logical_key)],
            args=[_integer_bytes(amount), b"" if ttl is None else _integer_bytes(ttl)],
        )
        return _decode_integer_reply(reply)

    async def acquire_lock(self, lock_key: str, ttl_seconds: float = 10.0) -> bool:
        logical_key = _validate_identifier(lock_key, "Lock key")
        ttl = _ttl_ms(ttl_seconds)
        assert ttl is not None
        token = secrets.token_bytes(32)
        redis_key = self._key("lock", logical_key)
        reply = await self._run_command("set", redis_key, token, nx=True, px=ttl)
        if reply is None:
            return False
        if reply is not True:
            raise CoordinationCorruptError("Coordination reply is invalid.")
        task = asyncio.current_task()
        if task is None:
            raise CoordinationUnavailableError("Redis coordination is unavailable.")
        self._lock_tokens.setdefault(task, {})[redis_key] = token
        return True

    async def release_lock(self, lock_key: str) -> None:
        logical_key = _validate_identifier(lock_key, "Lock key")
        self._ensure_open()
        redis_key = self._key("lock", logical_key)
        task = asyncio.current_task()
        token = self._lock_tokens.get(task, {}).get(redis_key) if task is not None else None
        if token is None:
            return
        reply = await self._run_script("lock_release", keys=[redis_key], args=[token])
        deleted = _decode_integer_reply(reply, nonnegative=True)
        if deleted not in {0, 1}:
            raise CoordinationCorruptError("Coordination reply is invalid.")
        owned_tokens = self._lock_tokens.get(task) if task is not None else None
        if owned_tokens is not None and owned_tokens.get(redis_key) == token:
            owned_tokens.pop(redis_key, None)
            if not owned_tokens:
                self._lock_tokens.pop(task, None)

    async def read_epoch(self) -> Epoch:
        reply = await self._run_script("epoch_read", keys=[self._key("epoch")], args=[])
        return _decode_epoch_reply(reply)

    async def advance_epoch(self, expected_epoch: int, operation_id: str) -> Epoch:
        expected = validate_epoch(expected_epoch)
        operation = validate_operation_id(operation_id)
        reply = await self._run_script(
            "epoch_advance",
            keys=[
                self._key("epoch"),
                self._key("replay:epoch-advance"),
                self._key("expiry:epoch-advance"),
            ],
            args=[
                _integer_bytes(expected),
                operation.encode("ascii"),
                _integer_bytes(_THIRTY_DAYS_MS),
                _integer_bytes(self._replay_limit),
            ],
        )
        return _decode_epoch_reply(reply)

    async def mark_epoch_ready(self, epoch: int, operation_id: str) -> Epoch:
        requested_epoch = validate_epoch(epoch)
        operation = validate_operation_id(operation_id)
        reply = await self._run_script(
            "epoch_ready",
            keys=[
                self._key("epoch"),
                self._key("replay:epoch-ready"),
                self._key("expiry:epoch-ready"),
            ],
            args=[
                _integer_bytes(requested_epoch),
                operation.encode("ascii"),
                _integer_bytes(_THIRTY_DAYS_MS),
                _integer_bytes(self._replay_limit),
            ],
        )
        return _decode_epoch_reply(reply)

    async def compare_and_set(self, request: CasRequest) -> CasResult:
        if not isinstance(request, CasRequest):
            raise ValueError("CAS request is invalid.")
        ttl = _ttl_ms(request.ttl_seconds)
        assert ttl is not None
        fingerprint = _fingerprint(
            request.key,
            request.expected_revision,
            request.payload,
            float(request.ttl_seconds),
            request.epoch,
        )
        reply = await self._run_script(
            "cas",
            keys=[
                self._key("epoch"),
                self._key("cas", request.key),
                self._key("replay:cas"),
                self._key("expiry:cas"),
            ],
            args=[
                _integer_bytes(request.expected_revision),
                request.payload,
                _integer_bytes(ttl),
                _integer_bytes(request.epoch),
                request.operation_id.encode("ascii"),
                fingerprint,
                _integer_bytes(self._replay_limit),
            ],
        )
        return _decode_cas_reply(reply)

    async def invalidate(self, request: InvalidationRequest) -> InvalidationResult:
        if not isinstance(request, InvalidationRequest):
            raise ValueError("Invalidation request is invalid.")
        ttl = _ttl_ms(request.replay_ttl_seconds)
        assert ttl is not None
        fingerprint = _fingerprint(request.scope, request.epoch, float(request.replay_ttl_seconds))
        reply = await self._run_script(
            "invalidation",
            keys=[
                self._key("epoch"),
                self._key("invalidation", request.scope),
                self._key("replay:invalidation"),
                self._key("expiry:invalidation"),
            ],
            args=[
                _integer_bytes(request.epoch),
                request.operation_id.encode("ascii"),
                _integer_bytes(ttl),
                fingerprint,
                _integer_bytes(self._replay_limit),
            ],
        )
        return _decode_invalidation_reply(reply)

    async def read_invalidation_generation(self, scope: str) -> InvalidationGeneration:
        logical_scope = _validate_identifier(scope, "Invalidation scope")
        reply = await self._run_script(
            "invalidation_read", keys=[self._key("invalidation", logical_scope)], args=[]
        )
        return _decode_generation_reply(reply)

    async def reserve_quota(self, request: QuotaReservationRequest) -> QuotaReservationDecision:
        if not isinstance(request, QuotaReservationRequest):
            raise ValueError("Quota reservation request is invalid.")
        ttl = _ttl_ms(request.ttl_seconds)
        assert ttl is not None
        retention = _quota_retention_ms(request)
        fingerprint = _fingerprint(
            request.reservation_id,
            request.key_id,
            float(request.now),
            float(request.ttl_seconds),
            request.estimated_tokens,
            float(request.estimated_cost_usd),
            request.rpm_limit,
            request.tpm_limit,
            request.daily_budget_usd,
            request.monthly_budget_usd,
            float(request.daily_spend_usd),
            float(request.monthly_spend_usd),
            float(request.daily_snapshot_started_at),
            float(request.monthly_snapshot_started_at),
            request.fencing_epoch,
        )
        operation_id = _quota_operation_bytes(
            "reserve", request.operation_id or request.reservation_id
        )
        reply = await self._run_script(
            "quota_reserve",
            keys=self._quota_keys(
                _fingerprint(request.key_id), request.reservation_id, operation_id.decode("ascii")
            ),
            args=[
                _integer_bytes(request.fencing_epoch),
                request.reservation_id.encode("ascii"),
                _fingerprint(request.key_id),
                fingerprint,
                operation_id,
                _integer_bytes(ttl),
                _integer_bytes(retention),
                _integer_bytes(self._quota_record_limit),
                _integer_bytes(self._replay_limit),
                _float_bytes(request.now),
                _integer_bytes(request.estimated_tokens),
                _float_bytes(request.estimated_cost_usd),
                b"" if request.rpm_limit is None else _integer_bytes(request.rpm_limit),
                b"" if request.tpm_limit is None else _integer_bytes(request.tpm_limit),
                b"" if request.daily_budget_usd is None else _float_bytes(request.daily_budget_usd),
                b""
                if request.monthly_budget_usd is None
                else _float_bytes(request.monthly_budget_usd),
                _float_bytes(request.daily_spend_usd),
                _float_bytes(request.monthly_spend_usd),
                _float_bytes(request.daily_snapshot_started_at),
                _float_bytes(request.monthly_snapshot_started_at),
            ],
        )
        return _decode_quota_reserve_reply(reply)

    async def commit_quota(self, request: QuotaCommitRequest) -> QuotaCommitResult:
        if not isinstance(request, QuotaCommitRequest):
            raise ValueError("Quota commit request is invalid.")
        fingerprint = _fingerprint(
            request.reservation_id,
            float(request.now),
            request.actual_tokens,
            request.actual_cost_usd,
            request.durable_cost_recorded,
            request.fencing_epoch,
        )
        operation_id = _quota_operation_bytes(
            "commit", request.operation_id or request.reservation_id
        )
        key_digest = await self._quota_routing_digest(
            request.reservation_id, operation_id.decode("ascii")
        )
        reply = await self._run_script(
            "quota_commit",
            keys=self._quota_keys(key_digest, request.reservation_id, operation_id.decode("ascii")),
            args=[
                _integer_bytes(request.fencing_epoch),
                fingerprint,
                operation_id,
                request.reservation_id.encode("ascii"),
                key_digest,
                _float_bytes(request.now),
                b"" if request.actual_tokens is None else _integer_bytes(request.actual_tokens),
                b"" if request.actual_cost_usd is None else _float_bytes(request.actual_cost_usd),
                b"1" if request.durable_cost_recorded else b"0",
                _integer_bytes(self._quota_record_limit),
                _integer_bytes(self._replay_limit),
                _integer_bytes(_QUOTA_MONTHLY_WINDOW_MS),
            ],
        )
        return _decode_quota_commit_reply(reply)

    async def release_quota(
        self,
        reservation_id: str,
        *,
        now: float,
        fencing_epoch: int = 1,
        operation_id: str | None = None,
    ) -> bool:
        identifier = _validate_identifier(reservation_id, "Reservation ID")
        epoch = validate_epoch(fencing_epoch)
        if isinstance(now, bool) or not isinstance(now, (int, float)) or not math.isfinite(now):
            raise ValueError("Quota time is invalid.")
        if not 0.0 <= float(now) <= MAX_COORDINATION_INTEGER:
            raise ValueError("Quota time is invalid.")
        if operation_id is not None:
            validate_operation_id(operation_id)
        fingerprint = _fingerprint(identifier, epoch)
        script_operation = _quota_operation_bytes("release", operation_id or identifier)
        key_digest = await self._quota_routing_digest(identifier, script_operation.decode("ascii"))
        reply = await self._run_script(
            "quota_release",
            keys=self._quota_keys(key_digest, identifier, script_operation.decode("ascii")),
            args=[
                _integer_bytes(epoch),
                fingerprint,
                script_operation,
                identifier.encode("ascii"),
                key_digest,
                _integer_bytes(_QUOTA_MONTHLY_WINDOW_MS),
                _integer_bytes(self._quota_record_limit),
                _integer_bytes(self._replay_limit),
            ],
        )
        return _decode_quota_release_reply(reply)

    async def close(self) -> None:
        async with self._lifecycle_lock:
            if self._closed:
                return
            self._closed = True
            client = self._client
            self._client = None
            self._scripts = {}
            self._lock_tokens.clear()
        if client is not None:
            try:
                await client.aclose()
            except Exception:
                raise CoordinationUnavailableError("Redis coordination is unavailable.") from None

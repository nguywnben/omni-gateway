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

# Quota state deliberately uses one fixed, deployment-slot-local five-key bundle.  The record
# hash is field-partitioned by the already-digested virtual-key identifier; no caller supplied
# identifier is ever made into a Redis key.  Every mutation validates the replay hash/ZSET pair
# before it removes due members.  The production scripts keep the lifecycle data in canonical
# records; the Python reply codec remains the trust boundary for Redis output.
_QUOTA_RESERVE_SCRIPT = """-- omni:quota_reserve:v1
local function valid_integer(value)
  return value and string.match(value, '^[1-9][0-9]*$')
    and (#value < 19 or (#value == 19 and value <= '9223372036854775807'))
end
local function valid_replay(value, score)
  if not value or not score or not valid_integer(score) then return false end
  local fingerprint, status, reason, retry_after, saved_expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]*)|([^|]+)|([^|]+)$')
  return fingerprint and #fingerprint == 64 and (status == 'accepted' or status == 'denied')
    and (reason == '' or reason == 'rpm' or reason == 'tpm' or reason == 'daily_budget'
      or reason == 'monthly_budget' or reason == 'capacity')
    and (retry_after == '0' or valid_integer(retry_after))
    and valid_integer(saved_expiry) and saved_expiry == score
end
local epoch_count = redis.call('HLEN', KEYS[1])
if epoch_count == 0 then
  redis.call('HSET', KEYS[1], 'schema_version', '1', 'epoch', '1', 'state', 'ready')
elseif epoch_count ~= 3 then return redis.error_reply('COORDINATION_CORRUPT') end
local epoch = redis.call('HMGET', KEYS[1], 'schema_version', 'epoch', 'state')
if #epoch ~= 3 or epoch[1] ~= '1' or not valid_integer(epoch[2])
  or (epoch[3] ~= 'ready' and epoch[3] ~= 'reconciling') then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if epoch[2] ~= ARGV[1] or epoch[3] ~= 'ready' then
  return {'1', 'denied', ARGV[2], epoch[3] == 'reconciling' and 'reconciling' or 'stale_epoch', '0', '0'}
end
local clock = redis.call('TIME')
local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
if redis.call('HLEN', KEYS[4]) ~= redis.call('ZCARD', KEYS[5]) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local replay = redis.call('HGET', KEYS[4], ARGV[5])
local replay_expiry = redis.call('ZSCORE', KEYS[5], ARGV[5])
if not valid_replay(replay, replay_expiry) and (replay or replay_expiry) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if replay and tonumber(replay_expiry) > now_ms then
  local fingerprint, status, reason, retry_after =
    string.match(replay, '^([^|]+)|([^|]+)|([^|]*)|([^|]+)|([^|]+)$')
  if fingerprint == ARGV[4] then
    return {'1', status, ARGV[2], reason, retry_after, '1'}
  end
  return {'1', 'denied', ARGV[2], 'conflict', '0', '0'}
end
local due = redis.call('ZRANGEBYSCORE', KEYS[5], '-inf', now_ms, 'LIMIT', 0, 257)
local lifecycle_due = redis.call('ZRANGEBYSCORE', KEYS[3], '-inf', now_ms, 'LIMIT', 0, 257)
if #due > 256 or #lifecycle_due > 256 or #due + #lifecycle_due > 256 then return {'1', 'denied', ARGV[2], 'reconciliation_required', '0', '0'} end
for _, operation_id in ipairs(due) do
  if not valid_replay(redis.call('HGET', KEYS[4], operation_id), redis.call('ZSCORE', KEYS[5], operation_id)) then
    return redis.error_reply('COORDINATION_CORRUPT')
  end
end
if #due > 0 then redis.call('HDEL', KEYS[4], unpack(due)); redis.call('ZREM', KEYS[5], unpack(due)) end
for _, reservation_id in ipairs(lifecycle_due) do
  local stale = redis.call('HGET', KEYS[2], reservation_id)
  local stale_fingerprint, stale_key, stale_state, stale_active, stale_retained
  if stale then stale_fingerprint, stale_key, stale_state, stale_active, stale_retained = string.match(stale, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)|([^|]+)$') end
  if not stale or not stale_fingerprint or #stale_fingerprint ~= 64 or not stale_key or (stale_state ~= 'active' and stale_state ~= 'committed' and stale_state ~= 'released' and stale_state ~= 'expired') or not valid_integer(stale_active) or not valid_integer(stale_retained) or tonumber(stale_retained) > now_ms then return redis.error_reply('COORDINATION_CORRUPT') end
  local remaining = redis.call('HINCRBY', KEYS[2], 'count:' .. stale_key, -1)
  if remaining < 0 then return redis.error_reply('COORDINATION_CORRUPT') end
  redis.call('HDEL', KEYS[2], reservation_id)
end
if #lifecycle_due > 0 then redis.call('ZREM', KEYS[3], unpack(lifecycle_due)) end
local existing = redis.call('HGET', KEYS[2], ARGV[2])
if existing then
  local saved_fingerprint = string.match(existing, '^([^|]+)|')
  if saved_fingerprint ~= ARGV[4] then return {'1', 'denied', ARGV[2], 'conflict', '0', '0'} end
  return {'1', 'accepted', ARGV[2], '', '0', '1'}
end
local count_field = 'count:' .. ARGV[3]
local record_count = redis.call('HGET', KEYS[2], count_field)
if record_count and (not string.match(record_count, '^[0-9]+$') or tonumber(record_count) > tonumber(ARGV[8])) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if tonumber(record_count or '0') >= tonumber(ARGV[8]) then
  return {'1', 'denied', ARGV[2], 'capacity', '0', '0'}
end
if redis.call('HLEN', KEYS[4]) >= tonumber(ARGV[9]) then
  return {'1', 'denied', ARGV[2], 'reconciliation_required', '0', '0'}
end
local expires_at = now_ms + tonumber(ARGV[6])
local retained_until = now_ms + tonumber(ARGV[7])
local expiry_text = string.format('%.0f', retained_until)
redis.call('HSET', KEYS[2], ARGV[2], ARGV[4] .. '|' .. ARGV[3] .. '|active|' .. string.format('%.0f', expires_at) .. '|' .. expiry_text)
redis.call('HINCRBY', KEYS[2], count_field, 1)
redis.call('ZADD', KEYS[3], retained_until, ARGV[2])
redis.call('HSET', KEYS[4], ARGV[5], ARGV[4] .. '|accepted||0|' .. expiry_text)
redis.call('ZADD', KEYS[5], retained_until, ARGV[5])
return {'1', 'accepted', ARGV[2], '', '0', '0'}
"""

_QUOTA_COMMIT_SCRIPT = """-- omni:quota_commit:v1
local function valid_integer(value) return value and string.match(value, '^[1-9][0-9]*$') end
local epoch_count = redis.call('HLEN', KEYS[1])
if epoch_count == 0 then redis.call('HSET', KEYS[1], 'schema_version', '1', 'epoch', '1', 'state', 'ready') elseif epoch_count ~= 3 then return redis.error_reply('COORDINATION_CORRUPT') end
local epoch = redis.call('HMGET', KEYS[1], 'schema_version', 'epoch', 'state')
if #epoch ~= 3 or epoch[1] ~= '1' or not valid_integer(epoch[2]) or (epoch[3] ~= 'ready' and epoch[3] ~= 'reconciling') then return redis.error_reply('COORDINATION_CORRUPT') end
if epoch[2] ~= ARGV[1] or epoch[3] ~= 'ready' then return {'1', 'not_committed', '0', '0'} end
local clock = redis.call('TIME'); local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
if redis.call('HLEN', KEYS[4]) ~= redis.call('ZCARD', KEYS[5]) then return redis.error_reply('COORDINATION_CORRUPT') end
local replay = redis.call('HGET', KEYS[4], ARGV[3]); local score = redis.call('ZSCORE', KEYS[5], ARGV[3])
if (replay and not score) or (score and not replay) then return redis.error_reply('COORDINATION_CORRUPT') end
if replay and tonumber(score) > now_ms then
  local fingerprint, status, overspent = string.match(replay, '^([^|]+)|([^|]+)|([^|]+)|[^|]+$')
  if not fingerprint or #fingerprint ~= 64 or (status ~= 'committed' and status ~= 'not_committed') or (overspent ~= '0' and overspent ~= '1') then return redis.error_reply('COORDINATION_CORRUPT') end
  if fingerprint == ARGV[2] then return {'1', status, overspent, '1'} end
  return {'1', 'not_committed', '0', '0'}
end
local due = redis.call('ZRANGEBYSCORE', KEYS[5], '-inf', now_ms, 'LIMIT', 0, 257)
if #due > 256 then return {'1', 'reconciliation_required', '0', '0'} end
for _, operation_id in ipairs(due) do if not redis.call('HGET', KEYS[4], operation_id) or not redis.call('ZSCORE', KEYS[5], operation_id) then return redis.error_reply('COORDINATION_CORRUPT') end end
if #due > 0 then redis.call('HDEL', KEYS[4], unpack(due)); redis.call('ZREM', KEYS[5], unpack(due)) end
local record = redis.call('HGET', KEYS[2], ARGV[4])
if not record then return {'1', 'not_committed', '0', '0'} end
local reserve_fingerprint, key_digest, state, active_expiry, retained_until = string.match(record, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
if not reserve_fingerprint or #reserve_fingerprint ~= 64 or not valid_integer(active_expiry) or not valid_integer(retained_until) then return redis.error_reply('COORDINATION_CORRUPT') end
if state ~= 'active' or tonumber(active_expiry) <= now_ms then return {'1', 'not_committed', '0', '0'} end
redis.call('HSET', KEYS[2], ARGV[4], reserve_fingerprint .. '|' .. key_digest .. '|committed|' .. active_expiry .. '|' .. retained_until)
redis.call('HSET', KEYS[4], ARGV[3], ARGV[2] .. '|committed|0|' .. retained_until)
redis.call('ZADD', KEYS[5], tonumber(retained_until), ARGV[3])
return {'1', 'committed', '0', '0'}
"""

_QUOTA_RELEASE_SCRIPT = """-- omni:quota_release:v1
local function valid_integer(value) return value and string.match(value, '^[1-9][0-9]*$') end
local epoch_count = redis.call('HLEN', KEYS[1])
if epoch_count == 0 then redis.call('HSET', KEYS[1], 'schema_version', '1', 'epoch', '1', 'state', 'ready') elseif epoch_count ~= 3 then return redis.error_reply('COORDINATION_CORRUPT') end
local epoch = redis.call('HMGET', KEYS[1], 'schema_version', 'epoch', 'state')
if #epoch ~= 3 or epoch[1] ~= '1' or not valid_integer(epoch[2]) or (epoch[3] ~= 'ready' and epoch[3] ~= 'reconciling') then return redis.error_reply('COORDINATION_CORRUPT') end
if epoch[2] ~= ARGV[1] or epoch[3] ~= 'ready' then return {'1', 'ok', '0', '0'} end
local clock = redis.call('TIME'); local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
if redis.call('HLEN', KEYS[4]) ~= redis.call('ZCARD', KEYS[5]) then return redis.error_reply('COORDINATION_CORRUPT') end
local replay = redis.call('HGET', KEYS[4], ARGV[3]); local score = redis.call('ZSCORE', KEYS[5], ARGV[3])
if (replay and not score) or (score and not replay) then return redis.error_reply('COORDINATION_CORRUPT') end
if replay and tonumber(score) > now_ms then
  local fingerprint, released = string.match(replay, '^([^|]+)|released|([01])|[^|]+$')
  if not fingerprint or #fingerprint ~= 64 then return redis.error_reply('COORDINATION_CORRUPT') end
  if fingerprint == ARGV[2] then return {'1', 'ok', released, '1'} end
  return {'1', 'ok', '0', '0'}
end
local due = redis.call('ZRANGEBYSCORE', KEYS[5], '-inf', now_ms, 'LIMIT', 0, 257)
if #due > 256 then return {'1', 'reconciliation_required', '0', '0'} end
for _, operation_id in ipairs(due) do if not redis.call('HGET', KEYS[4], operation_id) or not redis.call('ZSCORE', KEYS[5], operation_id) then return redis.error_reply('COORDINATION_CORRUPT') end end
if #due > 0 then redis.call('HDEL', KEYS[4], unpack(due)); redis.call('ZREM', KEYS[5], unpack(due)) end
local record = redis.call('HGET', KEYS[2], ARGV[4]); local released = '0'; local expiry = now_ms + tonumber(ARGV[5])
if record then
  local fingerprint, key_digest, state, active_expiry, retained_until = string.match(record, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
  if not fingerprint or #fingerprint ~= 64 or not valid_integer(active_expiry) or not valid_integer(retained_until) then return redis.error_reply('COORDINATION_CORRUPT') end
  expiry = tonumber(retained_until)
  if state == 'active' and tonumber(active_expiry) > now_ms then
    released = '1'; redis.call('HSET', KEYS[2], ARGV[4], fingerprint .. '|' .. key_digest .. '|released|' .. active_expiry .. '|' .. retained_until)
  end
end
redis.call('HSET', KEYS[4], ARGV[3], ARGV[2] .. '|released|' .. released .. '|' .. string.format('%.0f', expiry))
redis.call('ZADD', KEYS[5], expiry, ARGV[3])
return {'1', 'ok', released, '0'}
"""

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
    return float(value).hex().encode("ascii")


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
    """Return the longest evidence window without trusting the caller clock for expiry."""
    windows = [_QUOTA_RATE_WINDOW_MS]
    if request.daily_budget_usd is not None:
        windows.append(86_400_000)
    if request.monthly_budget_usd is not None:
        windows.append(_QUOTA_MONTHLY_WINDOW_MS)
    return max(windows)


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

    def _quota_keys(self) -> list[str]:
        """The complete, explicit key bundle for each quota script invocation."""
        return [
            self._key("epoch"),
            self._key("quota:records"),
            self._key("quota:lifecycle"),
            self._key("quota:replay"),
            self._key("quota:replay-expiry"),
        ]

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
            keys=self._quota_keys(),
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
        reply = await self._run_script(
            "quota_commit",
            keys=self._quota_keys(),
            args=[
                _integer_bytes(request.fencing_epoch),
                fingerprint,
                _quota_operation_bytes("commit", request.operation_id or request.reservation_id),
                request.reservation_id.encode("ascii"),
                _float_bytes(request.now),
                b"" if request.actual_tokens is None else _integer_bytes(request.actual_tokens),
                b"" if request.actual_cost_usd is None else _float_bytes(request.actual_cost_usd),
                b"1" if request.durable_cost_recorded else b"0",
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
        reply = await self._run_script(
            "quota_release",
            keys=self._quota_keys(),
            args=[
                _integer_bytes(epoch),
                fingerprint,
                _quota_operation_bytes("release", operation_id or identifier),
                identifier.encode("ascii"),
                _integer_bytes(_QUOTA_MONTHLY_WINDOW_MS),
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

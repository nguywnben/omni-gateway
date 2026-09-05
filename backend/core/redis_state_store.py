"""Redis transport for fixed, fenced coordination primitives.

The implementation stays independent of :mod:`core.state_store` so the legacy
state-store import can re-export this class without creating a cycle.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import importlib
import json
import math
import re
import secrets
import weakref
from typing import Any, Optional
from urllib.parse import urlsplit

from core.coordination import (
    ADMISSION_BINDING_KEY,
    ADMISSION_FENCE_KEY,
    MAX_COORDINATION_INTEGER,
    MAX_IDENTIFIER_LENGTH,
    MAX_PAYLOAD_BYTES,
    MAX_TTL_SECONDS,
    AdmissionFence,
    CasRequest,
    CasResult,
    CasSnapshot,
    CoordinationAdmissionFencedError,
    CoordinationCorruptError,
    CoordinationReconciliationRequiredError,
    CoordinationTime,
    CoordinationUnavailableError,
    Epoch,
    EpochState,
    InvalidationGeneration,
    InvalidationRequest,
    InvalidationResult,
    QuotaCommitRequest,
    QuotaCommitResult,
    QuotaReconciliationResult,
    QuotaReservationDecision,
    QuotaReservationRequest,
    validate_deployment_namespace,
    validate_epoch,
    validate_operation_id,
)
from core.quota_redis_scripts import (
    QUOTA_COMMIT_SCRIPT,
    QUOTA_RELEASE_SCRIPT,
    QUOTA_RESERVE_SCRIPT,
)
from core.security_coordination import (
    MAX_OIDC_TRANSACTION_TTL_SECONDS,
    MAX_SECURITY_PAGE_SIZE,
    MIN_SECURITY_ATTEMPT_WINDOW_SECONDS,
    AttemptClearRequest,
    AttemptClearResult,
    AttemptReservationDecision,
    AttemptReservationRequest,
    OidcTransactionConsumeRequest,
    OidcTransactionConsumeResult,
    OidcTransactionCreateRequest,
    SecurityAttemptCategory,
    SecurityPrincipalType,
    SecuritySessionState,
    SessionIssueRequest,
    SessionListRequest,
    SessionMutationResult,
    SessionPage,
    SessionResolveRequest,
    SessionResolveResult,
    SessionRevokeRequest,
    SessionRevokeResult,
    SessionRotateRequest,
    TransactionCreateResult,
)

_SCHEMA = b"1"
_THIRTY_DAYS_MS = 30 * 86_400 * 1000
_DEFAULT_REPLAY_LIMIT = 100_000
_MAX_CLEANUP = 256
_MAX_INTEGER_TEXT = "9223372036854775807"
_QUOTA_RATE_WINDOW_MS = 60_000
_DEFAULT_SECURITY_SESSION_LIMIT = 10_000
_DEFAULT_SECURITY_ATTEMPT_LIMIT = 100_000
_DEFAULT_OIDC_TRANSACTION_LIMIT = 1_000
_DEFAULT_SECURITY_REPLAY_LIMIT = 100_000
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
local marker = redis.call('GET', KEYS[2])
local encoded_epoch = redis.call('GET', KEYS[1])
if not marker and not encoded_epoch then
  if redis.call('MSETNX', KEYS[1], '1|1|ready', KEYS[2], '1|initialized') ~= 1 then
    return redis.error_reply('COORDINATION_CORRUPT')
  end
  marker, encoded_epoch = '1|initialized', '1|1|ready'
elseif not marker or not encoded_epoch then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if marker ~= '1|initialized' or redis.call('PTTL', KEYS[1]) ~= -1
  or redis.call('PTTL', KEYS[2]) ~= -1 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local schema, epoch, state = string.match(encoded_epoch, '^([^|]+)|([^|]+)|([^|]+)$')
if schema ~= '1' or not valid_integer(epoch)
  or (state ~= 'ready' and state ~= 'reconciling') then
  return redis.error_reply('COORDINATION_CORRUPT')
end
return {'1', 'ok', epoch, state}
"""

_TIME_READ_SCRIPT = """-- omni:time_read:v1
local function valid_integer(value)
  return value and string.match(value, '^[1-9][0-9]*$')
    and (#value < 19 or (#value == 19 and value <= '9223372036854775807'))
end
local marker, encoded_epoch = redis.call('GET', KEYS[2]), redis.call('GET', KEYS[1])
if marker ~= '1|initialized' or not encoded_epoch or redis.call('PTTL', KEYS[2]) ~= -1
  or redis.call('PTTL', KEYS[1]) ~= -1 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local schema, current_epoch, current_state =
  string.match(encoded_epoch, '^([^|]+)|([^|]+)|([^|]+)$')
if schema ~= '1' or not valid_integer(current_epoch)
  or (current_state ~= 'ready' and current_state ~= 'reconciling') then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if current_epoch ~= ARGV[1] or current_state ~= 'ready' then
  return {'1', 'unavailable', ''}
end
local clock = redis.call('TIME')
local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
return {'1', 'ok', string.format('%.0f', now_ms)}
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
local marker, encoded_epoch = redis.call('GET', KEYS[4]), redis.call('GET', KEYS[1])
if marker ~= '1|initialized' or not encoded_epoch or redis.call('PTTL', KEYS[4]) ~= -1
  or redis.call('PTTL', KEYS[1]) ~= -1 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local schema, current_epoch, current_state =
  string.match(encoded_epoch, '^([^|]+)|([^|]+)|([^|]+)$')
if schema ~= '1' or not valid_integer(current_epoch)
  or (current_state ~= 'ready' and current_state ~= 'reconciling') then
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
  return {'1', 'ok', current_epoch, current_state}
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
if current_epoch ~= ARGV[1] or current_state ~= 'ready' then
  return {'1', 'ok', current_epoch, current_state}
end
if redis.call('HLEN', KEYS[2]) >= tonumber(ARGV[4]) then
  return {'1', 'reconciliation_required', '', ''}
end
if current_epoch == '9223372036854775807' then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local new_epoch = next_integer(current_epoch)
redis.call('SET', KEYS[1], '1|' .. new_epoch .. '|reconciling')
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
local marker, encoded_epoch = redis.call('GET', KEYS[4]), redis.call('GET', KEYS[1])
if marker ~= '1|initialized' or not encoded_epoch or redis.call('PTTL', KEYS[4]) ~= -1
  or redis.call('PTTL', KEYS[1]) ~= -1 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local schema, current_epoch, current_state =
  string.match(encoded_epoch, '^([^|]+)|([^|]+)|([^|]+)$')
if schema ~= '1' or not valid_integer(current_epoch)
  or (current_state ~= 'ready' and current_state ~= 'reconciling') then
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
  return {'1', 'ok', current_epoch, current_state}
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
if current_epoch ~= ARGV[1] or current_state ~= 'reconciling' then
  return {'1', 'ok', current_epoch, current_state}
end
if redis.call('HLEN', KEYS[2]) >= tonumber(ARGV[4]) then
  return {'1', 'reconciliation_required', '', ''}
end
redis.call('SET', KEYS[1], '1|' .. current_epoch .. '|ready')
local expires_at = now_ms + tonumber(ARGV[3])
local expires_text = string.format('%.0f', expires_at)
redis.call('HSET', KEYS[2], ARGV[2],
  '1|' .. ARGV[1] .. '|' .. current_epoch .. '|ready|' .. expires_text)
redis.call('ZADD', KEYS[3], expires_at, ARGV[2])
return {'1', 'ok', current_epoch, 'ready'}
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
local marker, encoded_epoch = redis.call('GET', KEYS[5]), redis.call('GET', KEYS[1])
if marker ~= '1|initialized' or not encoded_epoch or redis.call('PTTL', KEYS[5]) ~= -1
  or redis.call('PTTL', KEYS[1]) ~= -1 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local schema, current_epoch, current_state =
  string.match(encoded_epoch, '^([^|]+)|([^|]+)|([^|]+)$')
if schema ~= '1' or not valid_integer(current_epoch, false)
  or (current_state ~= 'ready' and current_state ~= 'reconciling') then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if current_epoch ~= ARGV[4] or current_state ~= 'ready' then
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

_CAS_READ_SCRIPT = """-- omni:cas_read:v1
local function valid_integer(value)
  return value and string.match(value, '^[1-9][0-9]*$')
    and (#value < 19 or (#value == 19 and value <= '9223372036854775807'))
end
local marker, encoded_epoch = redis.call('GET', KEYS[3]), redis.call('GET', KEYS[2])
if marker ~= '1|initialized' or not encoded_epoch or redis.call('PTTL', KEYS[3]) ~= -1
  or redis.call('PTTL', KEYS[2]) ~= -1 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local schema, current_epoch, current_state =
  string.match(encoded_epoch, '^([^|]+)|([^|]+)|([^|]+)$')
if schema ~= '1' or not valid_integer(current_epoch)
  or (current_state ~= 'ready' and current_state ~= 'reconciling') then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if current_epoch ~= ARGV[1] or current_state ~= 'ready' then
  return {'1', 'unavailable', '', ''}
end
local record_count = redis.call('HLEN', KEYS[1])
if record_count == 0 then return {'1', 'not_found', '', ''} end
if record_count ~= 3 then return redis.error_reply('COORDINATION_CORRUPT') end
local record = redis.call('HMGET', KEYS[1], 'schema_version', 'revision', 'payload')
local record_ttl = redis.call('PTTL', KEYS[1])
if record[1] ~= '1' or not valid_integer(record[2]) or record[3] == false
  or #record[3] > 16384 or record_ttl <= 0 or record_ttl > 2592000000 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
return {'1', 'found', record[2], record[3]}
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
local marker, encoded_epoch = redis.call('GET', KEYS[5]), redis.call('GET', KEYS[1])
if marker ~= '1|initialized' or not encoded_epoch or redis.call('PTTL', KEYS[5]) ~= -1
  or redis.call('PTTL', KEYS[1]) ~= -1 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local schema, current_epoch, current_state =
  string.match(encoded_epoch, '^([^|]+)|([^|]+)|([^|]+)$')
if schema ~= '1' or not valid_integer(current_epoch)
  or (current_state ~= 'ready' and current_state ~= 'reconciling') then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if current_epoch ~= ARGV[1] or current_state ~= 'ready' then
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
local marker, encoded_epoch = redis.call('GET', KEYS[3]), redis.call('GET', KEYS[2])
if marker ~= '1|initialized' or not encoded_epoch or redis.call('PTTL', KEYS[3]) ~= -1
  or redis.call('PTTL', KEYS[2]) ~= -1 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local schema, epoch, state = string.match(encoded_epoch, '^([^|]+)|([^|]+)|([^|]+)$')
if schema ~= '1' or not valid_integer(epoch)
  or (state ~= 'ready' and state ~= 'reconciling') then
  return redis.error_reply('COORDINATION_CORRUPT')
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

_SECURITY_SESSION_COMMON = r"""
local function valid_integer(value)
  return value and (value == '0' or string.match(value, '^[1-9][0-9]*$'))
    and (#value < 16 or (#value == 16 and value <= '9007199254740991'))
end
local function ready_epoch(expected)
  local marker, encoded = redis.call('GET', KEYS[2]), redis.call('GET', KEYS[1])
  if marker ~= '1|initialized' or not encoded or redis.call('PTTL', KEYS[2]) ~= -1
    or redis.call('PTTL', KEYS[1]) ~= -1 then return nil, nil end
  local schema, epoch, state = string.match(encoded, '^([^|]+)|([^|]+)|([^|]+)$')
  if schema ~= '1' or not valid_integer(epoch)
    or (state ~= 'ready' and state ~= 'reconciling') then return nil, nil end
  return epoch == expected and state == 'ready', state
end
local function now_milliseconds()
  local clock = redis.call('TIME')
  return (clock[1] * 1000) + math.floor(clock[2] / 1000)
end
local function parse_session(value)
  if not value then return nil end
  local schema, reference, principal, principal_type, payload, issued, last_seen, idle_expiry,
    absolute_expiry = string.match(value,
      '^([^|]+)|([^|]+)|([^|]+)|([^|]+)|([^|]+)|([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
  if schema ~= '1' or not reference or not principal or not principal_type or not payload
    or not valid_integer(issued) or not valid_integer(last_seen)
    or not valid_integer(idle_expiry) or not valid_integer(absolute_expiry)
    or tonumber(issued) > tonumber(last_seen) or tonumber(last_seen) >= tonumber(idle_expiry)
    or tonumber(idle_expiry) > tonumber(absolute_expiry) then return nil end
  return {reference=reference, principal=principal, principal_type=principal_type, payload=payload,
    issued=issued, last_seen=last_seen, idle_expiry=idle_expiry,
    absolute_expiry=absolute_expiry}
end
local function validate_session(digest, value)
  local session = parse_session(value)
  if not session then return nil end
  local expected_expiry = string.format('%.0f',
    math.min(tonumber(session.idle_expiry), tonumber(session.absolute_expiry)))
  if redis.call('ZSCORE', KEYS[4], digest) ~= expected_expiry
    or redis.call('HGET', KEYS[5], session.reference) ~= digest
    or not redis.call('ZSCORE', KEYS[6], session.reference)
    or not redis.call('ZSCORE', KEYS[7], session.principal .. ':' .. digest)
    or not redis.call('ZSCORE', KEYS[8], session.principal_type .. ':' .. digest) then return nil end
  return session
end
local function valid_replay(value, score)
  if not value or not score then return false end
  local schema, fingerprint, digest, status, reason, issued, absolute_expiry, expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]*)|([^|]+)|([^|]*)|([^|]+)|([^|]+)|([^|]+)$')
  return schema == '1' and fingerprint and digest and status and reason ~= nil
    and valid_integer(issued) and valid_integer(absolute_expiry) and valid_integer(expiry)
    and expiry == score
end
local function plan_cleanup(now_ms)
  local session_count = redis.call('HLEN', KEYS[3])
  if session_count ~= redis.call('ZCARD', KEYS[4])
    or session_count ~= redis.call('HLEN', KEYS[5])
    or session_count ~= redis.call('ZCARD', KEYS[6])
    or session_count ~= redis.call('ZCARD', KEYS[7])
    or session_count ~= redis.call('ZCARD', KEYS[8])
    or redis.call('HLEN', KEYS[9]) ~= redis.call('ZCARD', KEYS[10]) then return nil end
  local due = redis.call('ZRANGEBYSCORE', KEYS[4], '-inf', now_ms, 'LIMIT', 0, 257)
  local replay_due = redis.call('ZRANGEBYSCORE', KEYS[10], '-inf', now_ms, 'LIMIT', 0, 257)
  if #due > 256 or #replay_due > 256 or #due + #replay_due > 256 then return false end
  for _, digest in ipairs(due) do
    if not validate_session(digest, redis.call('HGET', KEYS[3], digest)) then return nil end
  end
  for _, operation_id in ipairs(replay_due) do
    if not valid_replay(redis.call('HGET', KEYS[9], operation_id),
      redis.call('ZSCORE', KEYS[10], operation_id)) then return nil end
  end
  return {due=due, replay_due=replay_due}
end
local function delete_session(digest, session)
  redis.call('HDEL', KEYS[3], digest)
  redis.call('ZREM', KEYS[4], digest)
  redis.call('HDEL', KEYS[5], session.reference)
  redis.call('ZREM', KEYS[6], session.reference)
  redis.call('ZREM', KEYS[7], session.principal .. ':' .. digest)
  redis.call('ZREM', KEYS[8], session.principal_type .. ':' .. digest)
end
local function apply_cleanup(plan)
  for _, digest in ipairs(plan.due) do
    local session = parse_session(redis.call('HGET', KEYS[3], digest))
    delete_session(digest, session)
  end
  if #plan.replay_due > 0 then
    redis.call('HDEL', KEYS[9], unpack(plan.replay_due))
    redis.call('ZREM', KEYS[10], unpack(plan.replay_due))
  end
end
local function session_reply(status, reason, idempotent, digest, session)
  if not session then
    return {'1', status, reason, idempotent and '1' or '0', '', '', '', '', '', '', '', '', ''}
  end
  return {'1', status, reason, idempotent and '1' or '0', digest, session.reference,
    session.principal, session.principal_type, session.payload, session.issued, session.last_seen,
    session.idle_expiry, session.absolute_expiry}
end
local function store_replay(operation_id, fingerprint, digest, status, reason, issued,
    absolute_expiry, expiry)
  redis.call('HSET', KEYS[9], operation_id, table.concat({'1', fingerprint, digest, status, reason,
    issued, absolute_expiry, expiry}, '|'))
  redis.call('ZADD', KEYS[10], tonumber(expiry), operation_id)
end
local function parse_replay(value)
  local _, fingerprint, digest, status, reason, issued, absolute_expiry, expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]*)|([^|]+)|([^|]*)|([^|]+)|([^|]+)|([^|]+)$')
  return {fingerprint=fingerprint, digest=digest, status=status, reason=reason, issued=issued,
    absolute_expiry=absolute_expiry, expiry=expiry}
end
"""


_SECURITY_SESSION_ISSUE_SCRIPT = (
    "-- omni:security_session_issue:v1\n"
    + _SECURITY_SESSION_COMMON
    + r"""
local fenced, epoch_state = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then return session_reply('denied', epoch_state == 'reconciling'
  and 'reconciling' or 'stale_epoch', false, '', nil) end
local now_ms = now_milliseconds()
local plan = plan_cleanup(now_ms)
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if plan == false then return session_reply('denied', 'reconciliation_required', false, '', nil) end
local replay_value, replay_score = redis.call('HGET', KEYS[9], ARGV[9]),
  redis.call('ZSCORE', KEYS[10], ARGV[9])
if (replay_value or replay_score) and not valid_replay(replay_value, replay_score) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local digest_value = redis.call('HGET', KEYS[3], ARGV[2])
local reference_digest = redis.call('HGET', KEYS[5], ARGV[3])
if digest_value and not validate_session(ARGV[2], digest_value) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if reference_digest and not validate_session(reference_digest,
  redis.call('HGET', KEYS[3], reference_digest)) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
-- apply validated mutation
apply_cleanup(plan)
if replay_score and tonumber(replay_score) <= now_ms then replay_value = nil end
if replay_value then
  local replay = parse_replay(replay_value)
  if replay.fingerprint ~= ARGV[10] then return session_reply('denied', 'conflict', false, '', nil) end
  if replay.status ~= 'applied' then return session_reply('denied', replay.reason, true, '', nil) end
  local value = redis.call('HGET', KEYS[3], replay.digest)
  local session = validate_session(replay.digest, value)
  if not session or session.issued ~= replay.issued or session.absolute_expiry ~= replay.absolute_expiry
    or replay.digest ~= ARGV[2] or session.reference ~= ARGV[3] or session.principal ~= ARGV[4]
    or session.principal_type ~= ARGV[5] or session.payload ~= ARGV[6] then
    return session_reply('denied', 'conflict', false, '', nil)
  end
  return session_reply('applied', '', true, replay.digest, session)
end
digest_value = redis.call('HGET', KEYS[3], ARGV[2])
reference_digest = redis.call('HGET', KEYS[5], ARGV[3])
local reason = ''
if digest_value or reference_digest then reason = 'conflict'
elseif redis.call('HLEN', KEYS[3]) >= tonumber(ARGV[11]) then reason = 'capacity'
elseif redis.call('HLEN', KEYS[9]) >= tonumber(ARGV[12]) then reason = 'reconciliation_required' end
local absolute_expiry = string.format('%.0f', now_ms + tonumber(ARGV[8]))
if reason ~= '' then
  if redis.call('HLEN', KEYS[9]) >= tonumber(ARGV[12]) then
    return session_reply('denied', 'reconciliation_required', false, '', nil)
  end
  store_replay(ARGV[9], ARGV[10], '', 'denied', reason, '0', '0', absolute_expiry)
  return session_reply('denied', reason, false, '', nil)
end
local issued, idle_expiry = string.format('%.0f', now_ms),
  string.format('%.0f', now_ms + tonumber(ARGV[7]))
local session = {reference=ARGV[3], principal=ARGV[4], principal_type=ARGV[5], payload=ARGV[6],
  issued=issued, last_seen=issued, idle_expiry=idle_expiry, absolute_expiry=absolute_expiry}
store_replay(ARGV[9], ARGV[10], ARGV[2], 'applied', '', issued, absolute_expiry, absolute_expiry)
redis.call('HSET', KEYS[3], ARGV[2], table.concat({'1', ARGV[3], ARGV[4], ARGV[5], ARGV[6],
  issued, issued, idle_expiry, absolute_expiry}, '|'))
redis.call('ZADD', KEYS[4], tonumber(idle_expiry), ARGV[2])
redis.call('HSET', KEYS[5], ARGV[3], ARGV[2])
redis.call('ZADD', KEYS[6], 0, ARGV[3])
redis.call('ZADD', KEYS[7], 0, ARGV[4] .. ':' .. ARGV[2])
redis.call('ZADD', KEYS[8], 0, ARGV[5] .. ':' .. ARGV[2])
return session_reply('applied', '', false, ARGV[2], session)
"""
)


_SECURITY_SESSION_RESOLVE_SCRIPT = (
    "-- omni:security_session_resolve:v1\n"
    + _SECURITY_SESSION_COMMON
    + r"""
local fenced, epoch_state = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then return session_reply('denied', epoch_state == 'reconciling'
  and 'reconciling' or 'stale_epoch', false, '', nil) end
local now_ms = now_milliseconds()
local original = redis.call('HGET', KEYS[3], ARGV[2])
local original_session = original and validate_session(ARGV[2], original) or nil
if original and not original_session then return redis.error_reply('COORDINATION_CORRUPT') end
local was_expired = original_session and math.min(tonumber(original_session.idle_expiry),
  tonumber(original_session.absolute_expiry)) <= now_ms
local plan = plan_cleanup(now_ms)
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if plan == false then return session_reply('denied', 'reconciliation_required', false, '', nil) end
local replay_value, replay_score = redis.call('HGET', KEYS[9], ARGV[4]),
  redis.call('ZSCORE', KEYS[10], ARGV[4])
if (replay_value or replay_score) and not valid_replay(replay_value, replay_score) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
-- apply validated mutation
apply_cleanup(plan)
if replay_score and tonumber(replay_score) <= now_ms then replay_value = nil end
if replay_value then
  local replay = parse_replay(replay_value)
  if replay.fingerprint ~= ARGV[5] then
    return session_reply('denied', 'reconciliation_required', false, '', nil)
  end
  if replay.status ~= 'resolved' then return session_reply('denied', replay.reason, true, '', nil) end
  local session = validate_session(ARGV[2], redis.call('HGET', KEYS[3], ARGV[2]))
  if not session or session.issued ~= replay.issued then
    return session_reply('denied', 'not_found', true, '', nil)
  end
  return session_reply('resolved', '', true, ARGV[2], session)
end
if redis.call('HLEN', KEYS[9]) >= tonumber(ARGV[6]) then
  return session_reply('denied', 'reconciliation_required', false, '', nil)
end
local session = validate_session(ARGV[2], redis.call('HGET', KEYS[3], ARGV[2]))
if not session then
  local reason = was_expired and 'expired' or 'not_found'
  local expiry = string.format('%.0f', now_ms + tonumber(ARGV[3]))
  store_replay(ARGV[4], ARGV[5], ARGV[2], 'denied', reason, '0', '0', expiry)
  return session_reply('denied', reason, false, '', nil)
end
local idle_expiry = string.format('%.0f',
  math.min(now_ms + tonumber(ARGV[3]), tonumber(session.absolute_expiry)))
if tonumber(idle_expiry) <= now_ms then return redis.error_reply('COORDINATION_CORRUPT') end
session.last_seen, session.idle_expiry = string.format('%.0f', now_ms), idle_expiry
store_replay(ARGV[4], ARGV[5], ARGV[2], 'resolved', '', session.issued,
  session.absolute_expiry, idle_expiry)
redis.call('HSET', KEYS[3], ARGV[2], table.concat({'1', session.reference, session.principal,
  session.principal_type, session.payload, session.issued, session.last_seen, session.idle_expiry,
  session.absolute_expiry}, '|'))
redis.call('ZADD', KEYS[4], tonumber(idle_expiry), ARGV[2])
return session_reply('resolved', '', false, ARGV[2], session)
"""
)


_SECURITY_SESSION_ROTATE_SCRIPT = (
    "-- omni:security_session_rotate:v1\n"
    + _SECURITY_SESSION_COMMON
    + r"""
local fenced, epoch_state = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then return session_reply('denied', epoch_state == 'reconciling'
  and 'reconciling' or 'stale_epoch', false, '', nil) end
local now_ms = now_milliseconds()
local plan = plan_cleanup(now_ms)
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if plan == false then return session_reply('denied', 'reconciliation_required', false, '', nil) end
local replay_value, replay_score = redis.call('HGET', KEYS[9], ARGV[10]),
  redis.call('ZSCORE', KEYS[10], ARGV[10])
if (replay_value or replay_score) and not valid_replay(replay_value, replay_score) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local current_value = redis.call('HGET', KEYS[3], ARGV[2])
local current = current_value and validate_session(ARGV[2], current_value) or nil
if current_value and not current then return redis.error_reply('COORDINATION_CORRUPT') end
local collision = redis.call('HGET', KEYS[3], ARGV[3])
local reference_digest = redis.call('HGET', KEYS[5], ARGV[4])
if collision and not validate_session(ARGV[3], collision) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
if reference_digest and not validate_session(reference_digest,
  redis.call('HGET', KEYS[3], reference_digest)) then return redis.error_reply('COORDINATION_CORRUPT') end
-- apply validated mutation
apply_cleanup(plan)
if replay_score and tonumber(replay_score) <= now_ms then replay_value = nil end
if replay_value then
  local replay = parse_replay(replay_value)
  if replay.fingerprint ~= ARGV[11] then return session_reply('denied', 'conflict', false, '', nil) end
  if replay.status ~= 'applied' then return session_reply('denied', replay.reason, true, '', nil) end
  local session = validate_session(ARGV[3], redis.call('HGET', KEYS[3], ARGV[3]))
  if not session or session.issued ~= replay.issued or session.absolute_expiry ~= replay.absolute_expiry
    or session.reference ~= ARGV[4] or session.principal ~= ARGV[5]
    or session.principal_type ~= ARGV[6] or session.payload ~= ARGV[7] then
    return session_reply('denied', 'not_found', false, '', nil)
  end
  return session_reply('applied', '', true, ARGV[3], session)
end
current = validate_session(ARGV[2], redis.call('HGET', KEYS[3], ARGV[2]))
collision = redis.call('HGET', KEYS[3], ARGV[3])
reference_digest = redis.call('HGET', KEYS[5], ARGV[4])
local reason = ''
if not current then reason = 'not_found'
elseif collision or (reference_digest and reference_digest ~= ARGV[2]) then reason = 'conflict'
elseif redis.call('HLEN', KEYS[9]) >= tonumber(ARGV[12]) then reason = 'reconciliation_required' end
local absolute_expiry = string.format('%.0f', now_ms + tonumber(ARGV[9]))
if reason ~= '' then
  if redis.call('HLEN', KEYS[9]) >= tonumber(ARGV[12]) then
    return session_reply('denied', 'reconciliation_required', false, '', nil)
  end
  store_replay(ARGV[10], ARGV[11], '', 'denied', reason, '0', '0', absolute_expiry)
  return session_reply('denied', reason, false, '', nil)
end
local issued, idle_expiry = string.format('%.0f', now_ms),
  string.format('%.0f', now_ms + tonumber(ARGV[8]))
local replacement = {reference=ARGV[4], principal=ARGV[5], principal_type=ARGV[6], payload=ARGV[7],
  issued=issued, last_seen=issued, idle_expiry=idle_expiry, absolute_expiry=absolute_expiry}
store_replay(ARGV[10], ARGV[11], ARGV[3], 'applied', '', issued, absolute_expiry,
  absolute_expiry)
delete_session(ARGV[2], current)
redis.call('HSET', KEYS[3], ARGV[3], table.concat({'1', ARGV[4], ARGV[5], ARGV[6], ARGV[7],
  issued, issued, idle_expiry, absolute_expiry}, '|'))
redis.call('ZADD', KEYS[4], tonumber(idle_expiry), ARGV[3])
redis.call('HSET', KEYS[5], ARGV[4], ARGV[3])
redis.call('ZADD', KEYS[6], 0, ARGV[4])
redis.call('ZADD', KEYS[7], 0, ARGV[5] .. ':' .. ARGV[3])
redis.call('ZADD', KEYS[8], 0, ARGV[6] .. ':' .. ARGV[3])
return session_reply('applied', '', false, ARGV[3], replacement)
"""
)


_SECURITY_SESSION_REVOKE_SCRIPT = (
    "-- omni:security_session_revoke:v1\n"
    + _SECURITY_SESSION_COMMON
    + r"""
local fenced = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then return redis.error_reply('COORDINATION_UNAVAILABLE') end
local now_ms = now_milliseconds()
local plan = plan_cleanup(now_ms)
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if plan == false then return {'1', 'reconciliation_required', '0', '0'} end
local replay_value, replay_score = redis.call('HGET', KEYS[9], ARGV[5]),
  redis.call('ZSCORE', KEYS[10], ARGV[5])
if (replay_value or replay_score) and not valid_replay(replay_value, replay_score) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
-- apply validated mutation
apply_cleanup(plan)
if replay_score and tonumber(replay_score) <= now_ms then replay_value = nil end
if replay_value then
  local replay = parse_replay(replay_value)
  if replay.fingerprint ~= ARGV[6] then return redis.error_reply('COORDINATION_UNAVAILABLE') end
  return {'1', 'ok', replay.digest, '1'}
end
if redis.call('HLEN', KEYS[9]) >= tonumber(ARGV[7]) then
  return {'1', 'reconciliation_required', '0', '0'}
end
local digests = {}
if ARGV[2] == 'digest' then
  if redis.call('HGET', KEYS[3], ARGV[3]) then table.insert(digests, ARGV[3]) end
elseif ARGV[2] == 'reference' then
  local digest = redis.call('HGET', KEYS[5], ARGV[3])
  if digest then table.insert(digests, digest) end
elseif ARGV[2] == 'principal' then
  local members = redis.call('ZRANGEBYLEX', KEYS[7], '[' .. ARGV[3] .. ':',
    '[' .. ARGV[3] .. ':\255', 'LIMIT', 0, 257)
  if #members > 256 then return {'1', 'reconciliation_required', '0', '0'} end
  for _, member in ipairs(members) do table.insert(digests, string.sub(member, 66)) end
else
  local members = redis.call('ZRANGEBYLEX', KEYS[8], '[' .. ARGV[3] .. ':',
    '[' .. ARGV[3] .. ':\255', 'LIMIT', 0, 257)
  if #members > 256 then return {'1', 'reconciliation_required', '0', '0'} end
  for _, member in ipairs(members) do table.insert(digests, string.sub(member, #ARGV[3] + 2)) end
end
local sessions = {}
for index, digest in ipairs(digests) do
  local session = validate_session(digest, redis.call('HGET', KEYS[3], digest))
  if not session then return redis.error_reply('COORDINATION_CORRUPT') end
  sessions[index] = session
end
local expiry = string.format('%.0f', now_ms + tonumber(ARGV[4]))
store_replay(ARGV[5], ARGV[6], tostring(#digests), 'revoked', '', '0', '0', expiry)
for index, digest in ipairs(digests) do delete_session(digest, sessions[index]) end
return {'1', 'ok', tostring(#digests), '0'}
"""
)


_SECURITY_SESSION_LIST_SCRIPT = (
    "-- omni:security_session_list:v1\n"
    + _SECURITY_SESSION_COMMON
    + r"""
local fenced = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then return redis.error_reply('COORDINATION_UNAVAILABLE') end
local now_ms = now_milliseconds()
local plan = plan_cleanup(now_ms)
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if plan == false then return redis.error_reply('COORDINATION_RECONCILIATION_REQUIRED') end
-- apply validated mutation
apply_cleanup(plan)
local minimum = ARGV[3] == '' and '-' or '[' .. ARGV[3]
local references = redis.call('ZRANGEBYLEX', KEYS[6], minimum, '+', 'LIMIT', 0,
  tonumber(ARGV[2]) + 1)
local next_reference = ''
if #references > tonumber(ARGV[2]) then
  next_reference = references[#references]
  table.remove(references, #references)
end
local reply = {'1', 'ok', next_reference, tostring(#references)}
for _, reference in ipairs(references) do
  local digest = redis.call('HGET', KEYS[5], reference)
  local session = digest and validate_session(digest, redis.call('HGET', KEYS[3], digest)) or nil
  if not session or session.reference ~= reference then return redis.error_reply('COORDINATION_CORRUPT') end
  table.insert(reply, digest); table.insert(reply, session.reference)
  table.insert(reply, session.principal); table.insert(reply, session.principal_type)
  table.insert(reply, session.payload); table.insert(reply, session.issued)
  table.insert(reply, session.last_seen); table.insert(reply, session.idle_expiry)
  table.insert(reply, session.absolute_expiry)
end
return reply
"""
)


_SECURITY_ATTEMPT_COMMON = r"""
local function valid_integer(value)
  return value and (value == '0' or string.match(value, '^[1-9][0-9]*$'))
    and (#value < 16 or (#value == 16 and value <= '9007199254740991'))
end
local function ready_epoch(expected)
  local marker, encoded = redis.call('GET', KEYS[2]), redis.call('GET', KEYS[1])
  if marker ~= '1|initialized' or not encoded or redis.call('PTTL', KEYS[2]) ~= -1
    or redis.call('PTTL', KEYS[1]) ~= -1 then return nil, nil end
  local schema, epoch, state = string.match(encoded, '^([^|]+)|([^|]+)|([^|]+)$')
  if schema ~= '1' or not valid_integer(epoch)
    or (state ~= 'ready' and state ~= 'reconciling') then return nil, nil end
  return epoch == expected and state == 'ready', state
end
local function now_milliseconds()
  local clock = redis.call('TIME')
  return (clock[1] * 1000) + math.floor(clock[2] / 1000)
end
local function valid_record(value, score)
  if not value or not score then return false end
  local schema, count, expiry = string.match(value, '^([^|]+)|([^|]+)|([^|]+)$')
  return schema == '1' and valid_integer(count) and count ~= '0' and valid_integer(expiry)
    and expiry == score
end
local function parse_record(value)
  local _, count, expiry = string.match(value, '^([^|]+)|([^|]+)|([^|]+)$')
  return {count=tonumber(count), expiry=expiry}
end
local function valid_replay(value, score)
  if not value or not score then return false end
  local schema, fingerprint, status, reason, remaining, retry_after, expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]+)|([^|]*)|([^|]+)|([^|]+)|([^|]+)$')
  if schema ~= '1' or not string.match(fingerprint, '^[0-9a-f][0-9a-f]+$')
    or #fingerprint ~= 64 or not valid_integer(remaining) or not valid_integer(retry_after)
    or not valid_integer(expiry) or expiry ~= score then return false end
  if status == 'allowed' then return reason == '' and retry_after == '0' end
  if status == 'denied' then
    return remaining == '0' and ((reason == 'limited' and retry_after ~= '0')
      or ((reason == 'capacity' or reason == 'reconciliation_required') and retry_after == '0'))
  end
  return status == 'cleared' and reason == '' and (remaining == '0' or remaining == '1')
    and retry_after == '0'
end
local function parse_replay(value)
  local _, fingerprint, status, reason, remaining, retry_after, expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]+)|([^|]*)|([^|]+)|([^|]+)|([^|]+)$')
  return {fingerprint=fingerprint, status=status, reason=reason, remaining=remaining,
    retry_after=retry_after, expiry=expiry}
end
local function plan_cleanup(now_ms)
  if redis.call('HLEN', KEYS[3]) ~= redis.call('ZCARD', KEYS[4])
    or redis.call('HLEN', KEYS[5]) ~= redis.call('ZCARD', KEYS[6]) then return nil end
  local due = redis.call('ZRANGEBYSCORE', KEYS[4], '-inf', now_ms, 'LIMIT', 0, 257)
  local replay_due = redis.call('ZRANGEBYSCORE', KEYS[6], '-inf', now_ms, 'LIMIT', 0, 257)
  if #due > 256 or #replay_due > 256 or #due + #replay_due > 256 then return false end
  for _, identifier in ipairs(due) do
    if not valid_record(redis.call('HGET', KEYS[3], identifier),
      redis.call('ZSCORE', KEYS[4], identifier)) then return nil end
  end
  for _, operation_id in ipairs(replay_due) do
    if not valid_replay(redis.call('HGET', KEYS[5], operation_id),
      redis.call('ZSCORE', KEYS[6], operation_id)) then return nil end
  end
  return {due=due, replay_due=replay_due}
end
local function apply_cleanup(plan)
  if #plan.due > 0 then
    redis.call('HDEL', KEYS[3], unpack(plan.due)); redis.call('ZREM', KEYS[4], unpack(plan.due))
  end
  if #plan.replay_due > 0 then
    redis.call('HDEL', KEYS[5], unpack(plan.replay_due)); redis.call('ZREM', KEYS[6], unpack(plan.replay_due))
  end
end
local function store_replay(operation_id, fingerprint, status, reason, remaining, retry_after,
    expiry)
  redis.call('HSET', KEYS[5], operation_id, table.concat({'1', fingerprint, status, reason,
    remaining, retry_after, expiry}, '|'))
  redis.call('ZADD', KEYS[6], tonumber(expiry), operation_id)
end
"""


_SECURITY_ATTEMPT_RESERVE_SCRIPT = (
    "-- omni:security_attempt_reserve:v1\n"
    + _SECURITY_ATTEMPT_COMMON
    + r"""
local fenced, epoch_state = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then return {'1', 'denied', epoch_state == 'reconciling'
  and 'reconciling' or 'stale_epoch', '0', '0', '0'} end
local now_ms = now_milliseconds()
local plan = plan_cleanup(now_ms)
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if plan == false then return {'1', 'denied', 'reconciliation_required', '0', '0', '0'} end
local replay_value, replay_score = redis.call('HGET', KEYS[5], ARGV[5]),
  redis.call('ZSCORE', KEYS[6], ARGV[5])
if (replay_value or replay_score) and not valid_replay(replay_value, replay_score) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local record_value, record_score = redis.call('HGET', KEYS[3], ARGV[2]),
  redis.call('ZSCORE', KEYS[4], ARGV[2])
if (record_value or record_score) and not valid_record(record_value, record_score) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
-- apply validated mutation
apply_cleanup(plan)
if replay_score and tonumber(replay_score) <= now_ms then replay_value = nil end
if replay_value then
  local replay = parse_replay(replay_value)
  if replay.fingerprint ~= ARGV[6] then
    return {'1', 'denied', 'reconciliation_required', '0', '0', '0'}
  end
  return {'1', replay.status, replay.reason, '1', replay.remaining, replay.retry_after}
end
if redis.call('HLEN', KEYS[5]) >= tonumber(ARGV[8]) then
  return {'1', 'denied', 'reconciliation_required', '0', '0', '0'}
end
record_value = redis.call('HGET', KEYS[3], ARGV[2])
local record = record_value and parse_record(record_value) or nil
local status, reason, remaining, retry_after, expiry = 'allowed', '', '0', '0',
  string.format('%.0f', now_ms + tonumber(ARGV[4]))
if not record and redis.call('HLEN', KEYS[3]) >= tonumber(ARGV[7]) then
  status, reason = 'denied', 'capacity'
elseif record and record.count >= tonumber(ARGV[3]) then
  status, reason, retry_after, expiry = 'denied', 'limited',
    tostring(math.max(1, math.ceil((tonumber(record.expiry) - now_ms) / 1000))), record.expiry
else
  local count = record and record.count + 1 or 1
  remaining, expiry = tostring(math.max(0, tonumber(ARGV[3]) - count)),
    record and record.expiry or expiry
end
store_replay(ARGV[5], ARGV[6], status, reason, remaining, retry_after, expiry)
if status == 'allowed' then
  local count = record and record.count + 1 or 1
  redis.call('HSET', KEYS[3], ARGV[2], table.concat({'1', tostring(count), expiry}, '|'))
  redis.call('ZADD', KEYS[4], tonumber(expiry), ARGV[2])
end
return {'1', status, reason, '0', remaining, retry_after}
"""
)


_SECURITY_ATTEMPT_CLEAR_SCRIPT = (
    "-- omni:security_attempt_clear:v1\n"
    + _SECURITY_ATTEMPT_COMMON
    + r"""
local fenced = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then return redis.error_reply('COORDINATION_UNAVAILABLE') end
local now_ms = now_milliseconds()
local plan = plan_cleanup(now_ms)
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if plan == false then return {'1', 'reconciliation_required', '0', '0'} end
local replay_value, replay_score = redis.call('HGET', KEYS[5], ARGV[4]),
  redis.call('ZSCORE', KEYS[6], ARGV[4])
if (replay_value or replay_score) and not valid_replay(replay_value, replay_score) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local record_value, record_score = redis.call('HGET', KEYS[3], ARGV[2]),
  redis.call('ZSCORE', KEYS[4], ARGV[2])
if (record_value or record_score) and not valid_record(record_value, record_score) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
-- apply validated mutation
apply_cleanup(plan)
if replay_score and tonumber(replay_score) <= now_ms then replay_value = nil end
if replay_value then
  local replay = parse_replay(replay_value)
  if replay.fingerprint ~= ARGV[5] then return redis.error_reply('COORDINATION_UNAVAILABLE') end
  return {'1', 'ok', replay.remaining, '1'}
end
if redis.call('HLEN', KEYS[5]) >= tonumber(ARGV[6]) then
  return {'1', 'reconciliation_required', '0', '0'}
end
record_value = redis.call('HGET', KEYS[3], ARGV[2])
local cleared = record_value and '1' or '0'
local expiry = record_value and select(3, string.match(record_value, '^([^|]+)|([^|]+)|([^|]+)$'))
  or string.format('%.0f', now_ms + tonumber(ARGV[3]))
store_replay(ARGV[4], ARGV[5], 'cleared', '', cleared, '0', expiry)
if record_value then redis.call('HDEL', KEYS[3], ARGV[2]); redis.call('ZREM', KEYS[4], ARGV[2]) end
return {'1', 'ok', cleared, '0'}
"""
)


_OIDC_TRANSACTION_COMMON = r"""
local function valid_integer(value)
  return value and (value == '0' or string.match(value, '^[1-9][0-9]*$'))
    and (#value < 16 or (#value == 16 and value <= '9007199254740991'))
end
local function valid_digest(value)
  return value and #value == 64 and string.match(value, '^[0-9a-f]+$')
end
local function ready_epoch(expected)
  local marker, encoded = redis.call('GET', KEYS[2]), redis.call('GET', KEYS[1])
  if marker ~= '1|initialized' or not encoded or redis.call('PTTL', KEYS[2]) ~= -1
    or redis.call('PTTL', KEYS[1]) ~= -1 then return nil, nil end
  local schema, epoch, state = string.match(encoded, '^([^|]+)|([^|]+)|([^|]+)$')
  if schema ~= '1' or not valid_integer(epoch)
    or (state ~= 'ready' and state ~= 'reconciling') then return nil, nil end
  return epoch == expected and state == 'ready', state
end
local function now_milliseconds()
  local clock = redis.call('TIME')
  return (clock[1] * 1000) + math.floor(clock[2] / 1000)
end
local function valid_transaction(value, score)
  if not value or not score then return false end
  local schema, browser, payload, expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
  return schema == '1' and valid_digest(browser) and payload and payload ~= ''
    and valid_integer(expiry) and expiry == score
end
local function parse_transaction(value)
  local _, browser, payload, expiry = string.match(value, '^([^|]+)|([^|]+)|([^|]+)|([^|]+)$')
  return {browser=browser, payload=payload, expiry=expiry}
end
local function valid_replay(value, score)
  if not value or not score then return false end
  local schema, fingerprint, status, reason, state, browser, expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]+)|([^|]*)|([^|]*)|([^|]*)|([^|]+)$')
  if schema ~= '1' or not valid_digest(fingerprint) or not valid_integer(expiry)
    or expiry ~= score then return false end
  if status == 'applied' or status == 'consumed' then
    return reason == '' and valid_digest(state) and valid_digest(browser)
  end
  return status == 'denied' and state == '' and browser == ''
    and (reason == 'conflict' or reason == 'capacity'
      or reason == 'reconciliation_required' or reason == 'not_found'
      or reason == 'expired' or reason == 'browser_mismatch')
end
local function parse_replay(value)
  local _, fingerprint, status, reason, state, browser, expiry =
    string.match(value, '^([^|]+)|([^|]+)|([^|]+)|([^|]*)|([^|]*)|([^|]*)|([^|]+)$')
  return {fingerprint=fingerprint, status=status, reason=reason, state=state, browser=browser,
    expiry=expiry}
end
local function plan_cleanup(now_ms)
  if redis.call('HLEN', KEYS[3]) ~= redis.call('ZCARD', KEYS[4])
    or redis.call('HLEN', KEYS[5]) ~= redis.call('ZCARD', KEYS[6]) then return nil end
  local due = redis.call('ZRANGEBYSCORE', KEYS[4], '-inf', now_ms, 'LIMIT', 0, 257)
  local replay_due = redis.call('ZRANGEBYSCORE', KEYS[6], '-inf', now_ms, 'LIMIT', 0, 257)
  if #due > 256 or #replay_due > 256 or #due + #replay_due > 256 then return false end
  for _, state in ipairs(due) do
    if not valid_transaction(redis.call('HGET', KEYS[3], state),
      redis.call('ZSCORE', KEYS[4], state)) then return nil end
  end
  for _, operation_id in ipairs(replay_due) do
    if not valid_replay(redis.call('HGET', KEYS[5], operation_id),
      redis.call('ZSCORE', KEYS[6], operation_id)) then return nil end
  end
  return {due=due, replay_due=replay_due}
end
local function apply_cleanup(plan)
  if #plan.due > 0 then
    redis.call('HDEL', KEYS[3], unpack(plan.due)); redis.call('ZREM', KEYS[4], unpack(plan.due))
  end
  if #plan.replay_due > 0 then
    redis.call('HDEL', KEYS[5], unpack(plan.replay_due)); redis.call('ZREM', KEYS[6], unpack(plan.replay_due))
  end
end
local function store_replay(operation_id, fingerprint, status, reason, state, browser, expiry)
  redis.call('HSET', KEYS[5], operation_id, table.concat({'1', fingerprint, status, reason, state,
    browser, expiry}, '|'))
  redis.call('ZADD', KEYS[6], tonumber(expiry), operation_id)
end
"""


_OIDC_TRANSACTION_CREATE_SCRIPT = (
    "-- omni:oidc_transaction_create:v1\n"
    + _OIDC_TRANSACTION_COMMON
    + r"""
local fenced, epoch_state = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then return {'1', 'denied', epoch_state == 'reconciling'
  and 'reconciling' or 'stale_epoch', '0'} end
local now_ms = now_milliseconds()
local plan = plan_cleanup(now_ms)
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if plan == false then return {'1', 'denied', 'reconciliation_required', '0'} end
local replay_value, replay_score = redis.call('HGET', KEYS[5], ARGV[6]),
  redis.call('ZSCORE', KEYS[6], ARGV[6])
if (replay_value or replay_score) and not valid_replay(replay_value, replay_score) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local transaction_value, transaction_score = redis.call('HGET', KEYS[3], ARGV[2]),
  redis.call('ZSCORE', KEYS[4], ARGV[2])
if (transaction_value or transaction_score) and not valid_transaction(transaction_value,
  transaction_score) then return redis.error_reply('COORDINATION_CORRUPT') end
-- apply validated mutation
apply_cleanup(plan)
if replay_score and tonumber(replay_score) <= now_ms then replay_value = nil end
if replay_value then
  local replay = parse_replay(replay_value)
  if replay.fingerprint ~= ARGV[7] then return {'1', 'denied', 'conflict', '0'} end
  if replay.status ~= 'applied' then return {'1', 'denied', replay.reason, '1'} end
  local transaction = redis.call('HGET', KEYS[3], ARGV[2])
  local parsed = transaction and parse_transaction(transaction) or nil
  if not parsed or replay.state ~= ARGV[2] or replay.browser ~= ARGV[3]
    or parsed.browser ~= ARGV[3] or parsed.payload ~= ARGV[4] or parsed.expiry ~= replay.expiry then
    return {'1', 'denied', 'conflict', '0'}
  end
  return {'1', 'applied', '', '1'}
end
if redis.call('HLEN', KEYS[5]) >= tonumber(ARGV[9]) then
  return {'1', 'denied', 'reconciliation_required', '0'}
end
transaction_value = redis.call('HGET', KEYS[3], ARGV[2])
local reason = transaction_value and 'conflict' or
  (redis.call('HLEN', KEYS[3]) >= tonumber(ARGV[8]) and 'capacity' or '')
local expiry = string.format('%.0f', now_ms + tonumber(ARGV[5]))
store_replay(ARGV[6], ARGV[7], reason == '' and 'applied' or 'denied', reason,
  reason == '' and ARGV[2] or '', reason == '' and ARGV[3] or '', expiry)
if reason ~= '' then return {'1', 'denied', reason, '0'} end
redis.call('HSET', KEYS[3], ARGV[2], table.concat({'1', ARGV[3], ARGV[4], expiry}, '|'))
redis.call('ZADD', KEYS[4], tonumber(expiry), ARGV[2])
return {'1', 'applied', '', '0'}
"""
)


_OIDC_TRANSACTION_CONSUME_SCRIPT = (
    "-- omni:oidc_transaction_consume:v1\n"
    + _OIDC_TRANSACTION_COMMON
    + r"""
local fenced, epoch_state = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then return {'1', 'denied', epoch_state == 'reconciling'
  and 'reconciling' or 'stale_epoch', '0', ''} end
local now_ms = now_milliseconds()
local original_value, original_score = redis.call('HGET', KEYS[3], ARGV[2]),
  redis.call('ZSCORE', KEYS[4], ARGV[2])
if (original_value or original_score) and not valid_transaction(original_value, original_score) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local was_expired = original_score and tonumber(original_score) <= now_ms
local plan = plan_cleanup(now_ms)
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if plan == false then return {'1', 'denied', 'reconciliation_required', '0', ''} end
local replay_value, replay_score = redis.call('HGET', KEYS[5], ARGV[5]),
  redis.call('ZSCORE', KEYS[6], ARGV[5])
if (replay_value or replay_score) and not valid_replay(replay_value, replay_score) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
-- apply validated mutation
apply_cleanup(plan)
if replay_score and tonumber(replay_score) <= now_ms then replay_value = nil end
if replay_value then
  local replay = parse_replay(replay_value)
  if replay.fingerprint ~= ARGV[6] then
    return {'1', 'denied', 'reconciliation_required', '0', ''}
  end
  if replay.status == 'consumed' then return {'1', 'denied', 'not_found', '1', ''} end
  return {'1', 'denied', replay.reason, '1', ''}
end
if redis.call('HLEN', KEYS[5]) >= tonumber(ARGV[7]) then
  return {'1', 'denied', 'reconciliation_required', '0', ''}
end
local transaction_value = redis.call('HGET', KEYS[3], ARGV[2])
local transaction = transaction_value and parse_transaction(transaction_value) or nil
local status, reason, payload, expiry = 'denied', '', '',
  string.format('%.0f', now_ms + tonumber(ARGV[4]))
if not transaction then reason = was_expired and 'expired' or 'not_found'
elseif transaction.browser ~= ARGV[3] then reason, expiry = 'browser_mismatch', transaction.expiry
else status, payload, expiry = 'consumed', transaction.payload, transaction.expiry end
if admission_fenced and status ~= 'consumed' then
  return {'1', 'denied', reason, '0', ''}
end
store_replay(ARGV[5], ARGV[6], status, reason, status == 'consumed' and ARGV[2] or '',
  status == 'consumed' and ARGV[3] or '', expiry)
if status == 'consumed' then
  redis.call('HDEL', KEYS[3], ARGV[2]); redis.call('ZREM', KEYS[4], ARGV[2])
  return {'1', 'consumed', '', '0', payload}
end
return {'1', 'denied', reason, '0', ''}
"""
)

_ADMISSION_SCRIPTS = frozenset(
    {
        "cas",
        "invalidation",
        "quota_reserve",
        "security_session_issue",
        "security_session_resolve",
        "security_session_rotate",
        "security_session_revoke",
        "security_attempt_reserve",
        "security_attempt_clear",
        "oidc_transaction_create",
    }
)
_SETTLEMENT_SCRIPTS = frozenset({"quota_commit", "quota_release", "oidc_transaction_consume"})

# Every accessed fence/binding key is appended explicitly to KEYS by _run_script.
# This prelude runs inside the same Redis invocation as the admitted mutation.
_ADMISSION_FENCE_LUA = r"""
local drain = redis.call('GET', KEYS[#KEYS - 1])
local admission_fenced = drain ~= false
if admission_fenced then
  local binding = redis.call('GET', KEYS[#KEYS])
  local function decode_closed(raw, fields, count)
    if not raw or #raw > 16384 then return nil end
    local ok, value = pcall(cjson.decode, raw)
    if not ok or type(value) ~= 'table' then return nil end
    local found, positions = 0, {}
    local start, escaped, closed = nil, false, nil
    -- Tokenize quoted strings so escaped/duplicate field names cannot disagree
    -- with cjson or make integer validation read text embedded in a value.
    for i = 1, #raw do
      local char = string.sub(raw, i, i)
      if start then
        if escaped then escaped = false
        elseif char == '\\' then escaped = true
        elseif char == '"' then
          closed, start = {start, i}, nil
        end
      elseif char == '"' then start, closed = i, nil
      elseif closed and char == ':' then
        local key = cjson.decode(string.sub(raw, closed[1], closed[2]))
        if not fields[key] or positions[key] then return nil end
        positions[key], found, closed = i + 1, found + 1, nil
      elseif not string.match(char, '%s') then closed = nil
      end
    end
    for key, _ in pairs(value) do
      if not fields[key] or not positions[key] then return nil end
    end
    if found ~= count then return nil end
    return value, positions
  end
  local d, dp = decode_closed(drain, {schema_version=true, namespace_digest=true, epoch=true,
    quota_reconciliation_cursor=true, quota_reconciliation_complete=true}, 5)
  local b, bp = decode_closed(binding, {schema_version=true, deployment_id=true,
    namespace_digest=true, identifier_key_fingerprint=true, fencing_epoch=true,
    manifest_checksum=true, activation_record=true}, 7)
  local function digest(value)
    return type(value) == 'string' and #value == 64 and string.match(value, '^[0-9a-f]+$')
  end
  local function integer_field(raw, position)
    local value = string.match(string.sub(raw, position), '^%s*([1-9][0-9]*)%s*[,}]')
    if not value or #value > 19 or (#value == 19 and value > '9223372036854775807') then
      return nil
    end
    return value
  end
  local encoded_epoch = redis.call('GET', KEYS[1])
  if not encoded_epoch or #encoded_epoch > 34 then return redis.error_reply('COORDINATION_CORRUPT') end
  local current_epoch, current_state = string.match(encoded_epoch or '', '^1|([1-9][0-9]*)|(%a+)$')
  if not d or not b or not current_epoch or d.schema_version ~= 2 or b.schema_version ~= 1
    or #current_epoch > 19 or (#current_epoch == 19 and current_epoch > '9223372036854775807')
    or integer_field(drain, dp.schema_version) ~= '2'
    or integer_field(binding, bp.schema_version) ~= '1'
    or not digest(d.namespace_digest) or d.namespace_digest ~= ARGV[#ARGV]
    or d.namespace_digest ~= b.namespace_digest or not digest(b.identifier_key_fingerprint)
    or not digest(b.manifest_checksum) or type(b.deployment_id) ~= 'string'
    or #b.deployment_id < 8 or #b.deployment_id > 64
    or type(b.activation_record) ~= 'string' or #b.activation_record ~= 36
    or not string.match(b.activation_record, '^act_[0-9a-f]+$')
    or redis.call('PTTL', KEYS[#KEYS - 1]) ~= -1 or redis.call('PTTL', KEYS[#KEYS]) ~= -1
    or type(d.quota_reconciliation_complete) ~= 'boolean'
    or d.quota_reconciliation_complete ~= (d.quota_reconciliation_cursor == cjson.null)
    or (d.quota_reconciliation_cursor ~= cjson.null and
      (type(d.quota_reconciliation_cursor) ~= 'string' or #d.quota_reconciliation_cursor < 1
      or #d.quota_reconciliation_cursor > 4096
      or string.find(d.quota_reconciliation_cursor, '[^ -~]')))
  then return redis.error_reply('COORDINATION_CORRUPT') end
  local drain_epoch = integer_field(drain, dp.epoch)
  local binding_epoch = integer_field(binding, bp.fencing_epoch)
  -- Exact decimal string comparison avoids the binary64 epoch boundary.
  local function prior(value)
    local carry, out = 1, ''
    for i = #value, 1, -1 do
      local digit = tonumber(string.sub(value, i, i)) - carry
      if digit < 0 then digit = 9 else carry = 0 end
      out = tostring(digit) .. out
    end
    return string.gsub(out, '^0', '')
  end
  if not drain_epoch or not binding_epoch or binding_epoch ~= current_epoch
    or not (drain_epoch == current_epoch or
      (drain_epoch == prior(current_epoch) and d.quota_reconciliation_complete))
    or (current_state ~= 'ready' and current_state ~= 'reconciling')
  then return redis.error_reply('COORDINATION_CORRUPT') end
end
"""

_CAS_SETTLEMENT_LUA = r"""
if ARGV[8] ~= '' then
  local proof = redis.call('HGET', KEYS[3], ARGV[8])
  local expiry = redis.call('ZSCORE', KEYS[4], ARGV[8])
  local schema, fingerprint, status, revision, saved_expiry =
    string.match(proof or '', '^([^|]+)|([^|]+)|([^|]+)|([^|]*)|([^|]+)$')
  local clock = redis.call('TIME')
  local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
  if not valid_replay(proof, expiry) or schema ~= '1' or fingerprint ~= ARGV[9] or status ~= 'applied'
    or not revision or not string.match(revision, '^[1-9][0-9]*$')
    or not expiry or saved_expiry ~= expiry or not tonumber(expiry)
    or tonumber(expiry) <= now_ms then
    return redis.error_reply('COORDINATION_ADMISSION_FENCED')
  end
elseif admission_fenced then
  return redis.error_reply('COORDINATION_ADMISSION_FENCED')
end
"""

_DRAIN_COMPLETE_SCRIPT = (
    "-- omni:drain_complete:v1\n"
    + _ADMISSION_FENCE_LUA
    + r"""
if redis.call('GET', KEYS[4]) ~= '1|initialized' or redis.call('PTTL', KEYS[4]) ~= -1
  or redis.call('GET', KEYS[1]) ~= '1|' .. ARGV[1] .. '|ready'
  or redis.call('PTTL', KEYS[1]) ~= -1
then return redis.error_reply('COORDINATION_CORRUPT') end
local replay = redis.call('HGET', KEYS[2], ARGV[2])
local expiry = redis.call('ZSCORE', KEYS[3], ARGV[2])
local clock = redis.call('TIME')
local now_ms = clock[1] * 1000 + math.floor(clock[2] / 1000)
if not replay or not expiry or not tonumber(expiry) or tonumber(expiry) <= now_ms
  or replay ~= '1|' .. ARGV[1] .. '|' .. ARGV[1] .. '|ready|' .. expiry
  or (drain and drain ~= ARGV[3])
then return redis.error_reply('COORDINATION_DRAIN_CONFLICT') end
if drain then redis.call('DEL', KEYS[#KEYS - 1]) end
return {'1', 'ok'}
"""
)


def _with_admission_fence(name: str, source: str) -> str:
    if name not in _ADMISSION_SCRIPTS | _SETTLEMENT_SCRIPTS:
        return source
    header, body = source.split("\n", 1)
    if name in {"quota_commit", "quota_release"}:
        marker, reply = (
            ("local status, overspent =", "{'1', 'not_committed', '0', '0'}")
            if name == "quota_commit"
            else ("local released, expiry, window =", "{'1', 'ok', '0', '0'}")
        )
        # Only a retained reservation (or the earlier exact replay branch) authorizes
        # settlement. Unknown IDs cannot allocate denied replays during a drain.
        body = body.replace(
            marker,
            "if admission_fenced and not record then apply_cleanup(plan); return "
            + reply
            + " end\n"
            + marker,
            1,
        )
    if name == "cas":
        # An exact accepted settlement replay needs no new admission proof after proof expiry.
        body = body.replace("local due =", _CAS_SETTLEMENT_LUA + "local due =", 1)
        return (
            header + "\n" + _ADMISSION_FENCE_LUA + "if admission_fenced and ARGV[8] == '' then "
            "return redis.error_reply('COORDINATION_ADMISSION_FENCED') end\n" + body
        )
    guard = (
        "if admission_fenced then return redis.error_reply('COORDINATION_ADMISSION_FENCED') end\n"
    )
    if name in _SETTLEMENT_SCRIPTS:
        guard = ""
    return header + "\n" + _ADMISSION_FENCE_LUA + guard + body


SCRIPT_SOURCES = {
    name: _with_admission_fence(name, source)
    for name, source in {
        "drain_complete": _DRAIN_COMPLETE_SCRIPT,
        "epoch_read": _EPOCH_READ_SCRIPT,
        "time_read": _TIME_READ_SCRIPT,
        "epoch_advance": _EPOCH_ADVANCE_SCRIPT,
        "epoch_ready": _EPOCH_READY_SCRIPT,
        "cas": _CAS_SCRIPT,
        "cas_read": _CAS_READ_SCRIPT,
        "invalidation": _INVALIDATION_SCRIPT,
        "invalidation_read": _INVALIDATION_READ_SCRIPT,
        "increment": _INCREMENT_SCRIPT,
        "lock_release": _LOCK_RELEASE_SCRIPT,
        "quota_reserve": QUOTA_RESERVE_SCRIPT,
        "quota_commit": QUOTA_COMMIT_SCRIPT,
        "quota_release": QUOTA_RELEASE_SCRIPT,
        "security_session_issue": _SECURITY_SESSION_ISSUE_SCRIPT,
        "security_session_resolve": _SECURITY_SESSION_RESOLVE_SCRIPT,
        "security_session_rotate": _SECURITY_SESSION_ROTATE_SCRIPT,
        "security_session_revoke": _SECURITY_SESSION_REVOKE_SCRIPT,
        "security_session_list": _SECURITY_SESSION_LIST_SCRIPT,
        "security_attempt_reserve": _SECURITY_ATTEMPT_RESERVE_SCRIPT,
        "security_attempt_clear": _SECURITY_ATTEMPT_CLEAR_SCRIPT,
        "oidc_transaction_create": _OIDC_TRANSACTION_CREATE_SCRIPT,
        "oidc_transaction_consume": _OIDC_TRANSACTION_CONSUME_SCRIPT,
    }.items()
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
    number = float(value)
    if number == 0.0:
        return b"0"
    return format(number, ".17g").encode("ascii")


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
    ttl = _ttl_ms(request.ttl_seconds)
    assert ttl is not None
    return max(ttl, _QUOTA_RATE_WINDOW_MS + 1_000)


def _encode_quota_reconciliation_cursor(
    *, family: str, key_scan: int, target: str | None, member_scan: int
) -> str:
    payload = json.dumps(
        {
            "schema_version": 1,
            "family": family,
            "key_scan": key_scan,
            "target": target,
            "member_scan": member_scan,
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")


def _decode_quota_reconciliation_cursor(cursor: str | None) -> dict[str, object]:
    if cursor is None:
        return {
            "schema_version": 1,
            "family": "records",
            "key_scan": 0,
            "target": None,
            "member_scan": 0,
        }
    if (
        not isinstance(cursor, str)
        or not 1 <= len(cursor) <= 2048
        or any(
            not (character.isascii() and (character.isalnum() or character in "-_"))
            for character in cursor
        )
    ):
        raise ValueError("Quota reconciliation cursor is invalid.")
    try:
        padding = "=" * (-len(cursor) % 4)
        decoded = base64.urlsafe_b64decode(cursor + padding)
        if base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii") != cursor:
            raise ValueError
        payload = json.loads(decoded)
    except (ValueError, UnicodeError, json.JSONDecodeError):
        raise ValueError("Quota reconciliation cursor is invalid.") from None
    if (
        not isinstance(payload, dict)
        or set(payload) != {"schema_version", "family", "key_scan", "target", "member_scan"}
        or payload.get("schema_version") != 1
        or payload.get("family") not in {"records", "replays"}
        or type(payload.get("key_scan")) is not int
        or not 0 <= payload["key_scan"] <= MAX_COORDINATION_INTEGER
        or (
            payload.get("target") is not None
            and (
                not isinstance(payload["target"], str)
                or not 1 <= len(payload["target"]) <= 512
                or not payload["target"].isascii()
            )
        )
        or type(payload.get("member_scan")) is not int
        or not 0 <= payload["member_scan"] <= MAX_COORDINATION_INTEGER
    ):
        raise ValueError("Quota reconciliation cursor is invalid.")
    return payload


def _quota_reconciliation_record(value: object, score: object, key_digest: bytes) -> str:
    if (
        not isinstance(value, bytes)
        or len(value) > 2048
        or isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not math.isfinite(float(score))
        or not float(score).is_integer()
    ):
        raise CoordinationCorruptError("Stored coordination state is invalid.")
    try:
        fields = value.decode("ascii").split("|")
    except UnicodeDecodeError:
        raise CoordinationCorruptError("Stored coordination state is invalid.") from None
    expected = 24 if fields and fields[0] == "1" else 14 if fields and fields[0] == "2" else 0
    if (
        len(fields) != expected
        or len(fields[1]) != 64
        or any(character not in "0123456789abcdef" for character in fields[1])
        or fields[2] != key_digest.decode("ascii")
        or fields[3] not in {"active", "committed", "released", "expired"}
    ):
        raise CoordinationCorruptError("Stored coordination state is invalid.")
    safe_indexes = (4, 5, 6, 9, 22, 23) if expected == 24 else (4, 5, 6, 8, 12, 13)
    uint_indexes = (7, 10) if expected == 24 else (7, 9)
    for index in (*safe_indexes, *uint_indexes):
        text = fields[index]
        maximum = 9_007_199_254_740_991 if index in safe_indexes else MAX_COORDINATION_INTEGER
        if (
            not text
            or (len(text) > 1 and text.startswith("0"))
            or not text.isdigit()
            or int(text) > maximum
        ):
            raise CoordinationCorruptError("Stored coordination state is invalid.")
    active_until, retained_until, accepted_at = map(int, fields[4:7])
    committed_at = int(fields[9] if expected == 24 else fields[8])
    retention = int(fields[22] if expected == 24 else fields[12])
    next_expiry = int(fields[23] if expected == 24 else fields[13])
    if (
        active_until == 0
        or retained_until == 0
        or accepted_at == 0
        or retention == 0
        or next_expiry == 0
        or accepted_at > active_until
        or ((expected == 14 or fields[3] != "committed") and active_until > retained_until)
        or next_expiry > retained_until
        or int(score) != next_expiry
    ):
        raise CoordinationCorruptError("Stored coordination state is invalid.")
    if expected == 14:
        if (
            (fields[10] != "n" and not _quota_positive_uint(fields[10]))
            or (fields[11] != "n" and not _quota_positive_uint(fields[11]))
            or retention < 61_000
            or (
                fields[3] == "active"
                and (committed_at != 0 or fields[9] != "0" or next_expiry != active_until)
            )
            or (
                fields[3] == "committed"
                and (
                    committed_at == 0
                    or committed_at < accepted_at
                    or committed_at > active_until
                    or committed_at > 9_007_199_254_679_991
                    or retained_until != max(active_until, committed_at + 61_000)
                    or next_expiry != retained_until
                )
            )
            or (
                fields[3] in {"released", "expired"}
                and (committed_at != 0 or fields[9] != "0" or next_expiry != retained_until)
            )
        ):
            raise CoordinationCorruptError("Stored coordination state is invalid.")
    elif not _valid_v1_quota_record(fields):
        raise CoordinationCorruptError("Stored coordination state is invalid.")
    return fields[3]


def _quota_uint(value: str, *, maximum: int = MAX_COORDINATION_INTEGER) -> bool:
    return bool(
        value
        and value.isdigit()
        and (value == "0" or not value.startswith("0"))
        and int(value) <= maximum
    )


def _quota_positive_uint(value: str, *, maximum: int = MAX_COORDINATION_INTEGER) -> bool:
    return _quota_uint(value, maximum=maximum) and value != "0"


_QUOTA_DECIMAL = re.compile(
    r"(?:0|[1-9][0-9]*|0\.[0-9]*[1-9]|[1-9][0-9]*\.[0-9]*[1-9]|"
    r"(?:[1-9]|[1-9]\.[0-9]*[1-9])e(?:[+-]?0[1-9]|[+-]?[1-9][0-9]*))\Z"
)


def _quota_decimal(value: str) -> float | None:
    if len(value) > 64 or _QUOTA_DECIMAL.fullmatch(value) is None:
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) and 0 <= number <= MAX_COORDINATION_INTEGER else None


def _valid_v1_quota_record(fields: list[str]) -> bool:
    if (
        fields[12] not in {"0", "1"}
        or fields[13] not in {"0", "1"}
        or fields[14] not in {"0", "1"}
        or (fields[16] != "n" and not _quota_positive_uint(fields[16]))
        or (fields[17] != "n" and not _quota_positive_uint(fields[17]))
        or any(_quota_decimal(fields[index]) is None for index in (8, 11, 15, 20, 21))
        or any(fields[index] != "n" and _quota_decimal(fields[index]) is None for index in (18, 19))
    ):
        return False
    active_until, retained_until, accepted_at = map(int, fields[4:7])
    committed_at, retention, next_expiry = int(fields[9]), int(fields[22]), int(fields[23])
    terminal_source = fields[3] in {"active", "released", "expired"}
    if retention > 2_592_000_000:
        return False
    if terminal_source:
        if (
            committed_at != 0
            or fields[10:13] != ["0", "0", "0"]
            or fields[15] != "0"
            or fields[13] != ("1" if fields[18] == "n" else "0")
            or fields[14] != ("1" if fields[19] == "n" else "0")
            or accepted_at > 9_007_199_254_740_991 - retention
            or retained_until != accepted_at + retention
        ):
            return False
        return next_expiry == (active_until if fields[3] == "active" else retained_until)
    expected_expiry = committed_at + 60_000
    if fields[13] == "0":
        expected_expiry = max(expected_expiry, committed_at + 86_400_000)
    if fields[14] == "0":
        expected_expiry = max(expected_expiry, committed_at + 2_592_000_000)
    return bool(
        fields[3] == "committed"
        and committed_at != 0
        and accepted_at <= committed_at <= active_until
        and next_expiry == retained_until == expected_expiry
        and (fields[18] != "n" or fields[13] == "1")
        and (fields[18] == "n" or fields[12] == "1" or fields[13] == "0")
        and (fields[19] != "n" or fields[14] == "1")
        and (fields[19] == "n" or fields[12] == "1" or fields[14] == "0")
    )


def _quota_reconciliation_replay(value: object, score: object) -> None:
    if (
        not isinstance(value, bytes)
        or len(value) > 1024
        or isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not math.isfinite(float(score))
        or not float(score).is_integer()
    ):
        raise CoordinationCorruptError("Stored coordination state is invalid.")
    try:
        fields = value.decode("ascii").split("|")
    except UnicodeDecodeError:
        raise CoordinationCorruptError("Stored coordination state is invalid.") from None
    if (
        not fields
        or fields[0] not in {"1", "2"}
        or len(fields) < 2
        or len(fields[1]) != 64
        or any(character not in "0123456789abcdef" for character in fields[1])
    ):
        raise CoordinationCorruptError("Stored coordination state is invalid.")
    if fields[0] == "2" and len(fields) != 7:
        raise CoordinationCorruptError("Stored coordination state is invalid.")
    if fields[0] == "1" and len(fields) not in {4, 5, 6}:
        raise CoordinationCorruptError("Stored coordination state is invalid.")
    expiry = fields[-1]
    if not _quota_positive_uint(expiry, maximum=9_007_199_254_740_991) or int(score) != int(expiry):
        raise CoordinationCorruptError("Stored coordination state is invalid.")
    if fields[0] == "2":
        kind, status, result, retry = fields[2:6]
        valid = _quota_uint(retry) and (
            (
                kind == "reserve"
                and status in {"accepted", "denied"}
                and (
                    (status == "accepted" and result == "" and retry == "0")
                    or (
                        status == "denied"
                        and result in {"rpm", "tpm", "capacity", "reconciliation_required"}
                    )
                )
            )
            or (
                kind == "commit"
                and status in {"committed", "not_committed"}
                and result in {"0", "1"}
                and retry == "0"
                and (status == "committed" or result == "0")
            )
            or (
                kind == "release"
                and status in {"released", "not_released"}
                and result == ""
                and retry == "0"
            )
        )
    elif len(fields) == 6:
        valid = (
            fields[2] in {"accepted", "denied"}
            and _quota_uint(fields[4])
            and (
                (fields[2] == "accepted" and fields[3] == "" and fields[4] == "0")
                or (
                    fields[2] == "denied"
                    and fields[3]
                    in {
                        "rpm",
                        "tpm",
                        "daily_budget",
                        "monthly_budget",
                        "capacity",
                        "reconciliation_required",
                    }
                )
            )
        )
    elif len(fields) == 5:
        valid = (
            fields[2] in {"committed", "not_committed"}
            and fields[3] in {"0", "1"}
            and (fields[2] == "committed" or fields[3] == "0")
        )
    else:
        valid = fields[2] in {"0", "1"}
    if not valid:
        raise CoordinationCorruptError("Stored coordination state is invalid.")


def _validate_quota_schema_marker(value: object) -> None:
    if not isinstance(value, bytes):
        raise CoordinationCorruptError("Stored coordination state is invalid.")
    try:
        fields = value.decode("ascii").split("|")
    except UnicodeDecodeError:
        raise CoordinationCorruptError("Stored coordination state is invalid.") from None
    if (
        len(fields) != 3
        or fields[0] not in {"1", "2"}
        or not _quota_positive_uint(fields[1])
        or fields[2] != "ready"
    ):
        raise CoordinationCorruptError("Stored coordination state is invalid.")


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


def _strict_nonnegative_int(value: bytes) -> int:
    if not value or (len(value) > 1 and value.startswith(b"0")) or not value.isdigit():
        raise CoordinationCorruptError("Coordination reply is invalid.")
    result = int(value)
    if not 0 <= result <= MAX_COORDINATION_INTEGER:
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


def _decode_time_reply(reply: object) -> CoordinationTime:
    values = _strict_array(reply, 3)
    if values[1] == b"unavailable":
        if values[2] != b"":
            raise CoordinationCorruptError("Coordination reply is invalid.")
        raise CoordinationUnavailableError("Coordination epoch is not ready.")
    if values[1] != b"ok":
        raise CoordinationCorruptError("Coordination reply is invalid.")
    return CoordinationTime(_strict_nonnegative_int(values[2]))


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


def _decode_cas_snapshot_reply(reply: object) -> CasSnapshot:
    values = _strict_array(reply, 4)
    if values[1] == b"unavailable":
        if values[2:] != [b"", b""]:
            raise CoordinationCorruptError("Coordination reply is invalid.")
        raise CoordinationUnavailableError("Coordination epoch is not ready.")
    if values[1] == b"not_found":
        if values[2:] != [b"", b""]:
            raise CoordinationCorruptError("Coordination reply is invalid.")
        return CasSnapshot(None, None)
    if values[1] != b"found" or len(values[3]) > MAX_PAYLOAD_BYTES:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    return CasSnapshot(_strict_positive_int(values[2]), values[3])


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
    if values[1] != b"ok" or (values[2], values[3]) not in {
        (b"0", b"0"),
        (b"1", b"0"),
        (b"0", b"1"),
    }:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    return values[2] == b"1"


def _decode_security_session(values: list[bytes], offset: int = 4) -> SecuritySessionState:
    fields = values[offset : offset + 9]
    if len(fields) != 9:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    digest, reference, principal, principal_type, encoded_payload, *timestamps = fields
    try:
        payload = base64.b64decode(encoded_payload, validate=True)
        session = SecuritySessionState(
            digest.decode("ascii"),
            reference.decode("ascii"),
            principal.decode("ascii"),
            SecurityPrincipalType(principal_type.decode("ascii")),
            payload,
            *(_strict_positive_int(value) / 1000.0 for value in timestamps),
        )
    except (UnicodeDecodeError, ValueError) as exc:
        raise CoordinationCorruptError("Coordination reply is invalid.") from exc
    return session


def _decode_session_mutation_reply(reply: object) -> SessionMutationResult:
    values = _strict_array(reply, 13)
    if values[1] not in {b"applied", b"denied"} or values[3] not in {b"0", b"1"}:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    try:
        reason = values[2].decode("ascii")
        if values[1] == b"applied":
            if reason:
                raise ValueError
            return SessionMutationResult(
                True,
                _decode_security_session(values),
                idempotent=values[3] == b"1",
            )
        if any(values[4:]):
            raise ValueError
        return SessionMutationResult(False, None, reason, values[3] == b"1")
    except (UnicodeDecodeError, ValueError) as exc:
        raise CoordinationCorruptError("Coordination reply is invalid.") from exc


def _decode_session_resolve_reply(reply: object) -> SessionResolveResult:
    values = _strict_array(reply, 13)
    if values[1] not in {b"resolved", b"denied"} or values[3] not in {b"0", b"1"}:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    try:
        reason = values[2].decode("ascii")
        if values[1] == b"resolved":
            if reason:
                raise ValueError
            return SessionResolveResult(
                True,
                _decode_security_session(values),
                idempotent=values[3] == b"1",
            )
        if any(values[4:]):
            raise ValueError
        return SessionResolveResult(False, None, reason, values[3] == b"1")
    except (UnicodeDecodeError, ValueError) as exc:
        raise CoordinationCorruptError("Coordination reply is invalid.") from exc


def _decode_session_revoke_reply(reply: object) -> SessionRevokeResult:
    values = _strict_array(reply, 4)
    if values[1] == b"reconciliation_required":
        if values[2:] != [b"0", b"0"]:
            raise CoordinationCorruptError("Coordination reply is invalid.")
        raise CoordinationReconciliationRequiredError("Reconciliation is required.")
    if values[1] != b"ok" or values[3] not in {b"0", b"1"}:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    try:
        return SessionRevokeResult(_strict_nonnegative_int(values[2]), values[3] == b"1")
    except ValueError as exc:
        raise CoordinationCorruptError("Coordination reply is invalid.") from exc


def _decode_session_page_reply(reply: object, *, requested_limit: int) -> SessionPage:
    if (
        not isinstance(reply, list)
        or len(reply) < 4
        or any(not isinstance(value, bytes) for value in reply)
    ):
        raise CoordinationCorruptError("Coordination reply is invalid.")
    values = list(reply)
    if values[0:2] != [b"1", b"ok"]:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    count = _strict_nonnegative_int(values[3])
    if count > requested_limit or len(values) != 4 + count * 9:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    try:
        next_reference = values[2].decode("ascii") or None
        sessions = tuple(_decode_security_session(values, 4 + index * 9) for index in range(count))
        return SessionPage(sessions, next_reference)
    except (UnicodeDecodeError, ValueError) as exc:
        raise CoordinationCorruptError("Coordination reply is invalid.") from exc


def _decode_attempt_reservation_reply(reply: object) -> AttemptReservationDecision:
    values = _strict_array(reply, 6)
    if values[1] not in {b"allowed", b"denied"} or values[3] not in {b"0", b"1"}:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    try:
        return AttemptReservationDecision(
            values[1] == b"allowed",
            _strict_nonnegative_int(values[4]),
            _strict_nonnegative_int(values[5]),
            values[2].decode("ascii"),
            values[3] == b"1",
        )
    except (UnicodeDecodeError, ValueError) as exc:
        raise CoordinationCorruptError("Coordination reply is invalid.") from exc


def _decode_attempt_clear_reply(reply: object) -> AttemptClearResult:
    values = _strict_array(reply, 4)
    if values[1] == b"reconciliation_required":
        if values[2:] != [b"0", b"0"]:
            raise CoordinationCorruptError("Coordination reply is invalid.")
        raise CoordinationReconciliationRequiredError("Reconciliation is required.")
    if (
        values[1] != b"ok"
        or values[2] not in {b"0", b"1"}
        or values[3]
        not in {
            b"0",
            b"1",
        }
    ):
        raise CoordinationCorruptError("Coordination reply is invalid.")
    return AttemptClearResult(values[2] == b"1", values[3] == b"1")


def _decode_transaction_create_reply(reply: object) -> TransactionCreateResult:
    values = _strict_array(reply, 4)
    if values[1] not in {b"applied", b"denied"} or values[3] not in {b"0", b"1"}:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    try:
        return TransactionCreateResult(
            values[1] == b"applied",
            values[2].decode("ascii"),
            values[3] == b"1",
        )
    except (UnicodeDecodeError, ValueError) as exc:
        raise CoordinationCorruptError("Coordination reply is invalid.") from exc


def _decode_transaction_consume_reply(reply: object) -> OidcTransactionConsumeResult:
    values = _strict_array(reply, 5)
    if values[1] not in {b"consumed", b"denied"} or values[3] not in {b"0", b"1"}:
        raise CoordinationCorruptError("Coordination reply is invalid.")
    try:
        reason = values[2].decode("ascii")
        if values[1] == b"consumed":
            if reason or not values[4]:
                raise ValueError
            payload = base64.b64decode(values[4], validate=True)
            return OidcTransactionConsumeResult(
                True,
                payload,
                idempotent=values[3] == b"1",
            )
        if values[4]:
            raise ValueError
        return OidcTransactionConsumeResult(
            False,
            None,
            reason,
            values[3] == b"1",
        )
    except (UnicodeDecodeError, ValueError) as exc:
        raise CoordinationCorruptError("Coordination reply is invalid.") from exc


class RedisStateStore:
    """Lazy, secret-safe Redis implementation of the coordination surface."""

    def __init__(
        self,
        redis_url: str,
        deployment_namespace: str = "omni-gateway",
        *,
        _coordination_replay_limit_for_testing: int | None = None,
        _quota_record_limit_for_testing: int | None = None,
        _security_session_limit_for_testing: int | None = None,
        _security_attempt_limit_for_testing: int | None = None,
        _oidc_transaction_limit_for_testing: int | None = None,
        _security_replay_limit_for_testing: int | None = None,
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
        security_session_limit = (
            _DEFAULT_SECURITY_SESSION_LIMIT
            if _security_session_limit_for_testing is None
            else _security_session_limit_for_testing
        )
        security_attempt_limit = (
            _DEFAULT_SECURITY_ATTEMPT_LIMIT
            if _security_attempt_limit_for_testing is None
            else _security_attempt_limit_for_testing
        )
        oidc_transaction_limit = (
            _DEFAULT_OIDC_TRANSACTION_LIMIT
            if _oidc_transaction_limit_for_testing is None
            else _oidc_transaction_limit_for_testing
        )
        security_replay_limit = (
            _DEFAULT_SECURITY_REPLAY_LIMIT
            if _security_replay_limit_for_testing is None
            else _security_replay_limit_for_testing
        )
        for value, maximum, label in (
            (security_session_limit, 100_000, "Security session limit"),
            (security_attempt_limit, 100_000, "Security attempt limit"),
            (oidc_transaction_limit, 10_000, "OIDC transaction limit"),
            (security_replay_limit, 100_000, "Security replay limit"),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
                raise ValueError(f"{label} is invalid.")
        self._redis_url = redis_url
        self._redis_module = _redis_module_for_testing
        self._tag = hashlib.sha256(namespace.encode("ascii")).hexdigest()
        self._prefix = f"omni:{{{self._tag}}}:v1"
        self._replay_limit = replay_limit
        self._quota_record_limit = quota_record_limit
        self._security_session_limit = security_session_limit
        self._security_attempt_limit = security_attempt_limit
        self._oidc_transaction_limit = oidc_transaction_limit
        self._security_replay_limit = security_replay_limit
        self._client: Any = None
        self._scripts: dict[str, Any] = {}
        self._lock_tokens: weakref.WeakKeyDictionary[asyncio.Task[Any], dict[str, bytes]] = (
            weakref.WeakKeyDictionary()
        )
        self._closed = False
        self._closing = False
        self._lifecycle_lock = asyncio.Lock()
        self._close_task: asyncio.Task[None] | None = None

    def __repr__(self) -> str:
        state = "closed" if self._closed else "closing" if self._closing else "open"
        return f"RedisStateStore(deployment={self._tag!r}, state={state!r})"

    def _ensure_open(self) -> None:
        if self._closed or self._closing:
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
            self._key("initialization"),
            self._quota_bucket_key("quota:rate-buckets", key_digest),
            self._quota_bucket_key("quota:state-schema", key_digest),
        ]

    def _security_session_keys(self) -> list[str]:
        """Return the complete fixed key bundle for every session script."""
        return [
            self._key("epoch"),
            self._key("initialization"),
            self._key("security:sessions"),
            self._key("security:session-expiry"),
            self._key("security:session-references"),
            self._key("security:session-reference-order"),
            self._key("security:session-principals"),
            self._key("security:session-principal-types"),
            self._key("security:session-replay"),
            self._key("security:session-replay-expiry"),
        ]

    def _security_attempt_keys(self, category: SecurityAttemptCategory) -> list[str]:
        """Return the fixed key bundle isolated to one throttle category."""
        scope = f"security:attempt:{category.value}"
        return [
            self._key("epoch"),
            self._key("initialization"),
            self._key(f"{scope}:records"),
            self._key(f"{scope}:expiry"),
            self._key(f"{scope}:replay"),
            self._key(f"{scope}:replay-expiry"),
        ]

    def _oidc_transaction_keys(self) -> list[str]:
        """Return the fixed key bundle for pending OIDC proof state."""
        return [
            self._key("epoch"),
            self._key("initialization"),
            self._key("security:oidc-transactions"),
            self._key("security:oidc-transaction-expiry"),
            self._key("security:oidc-replay"),
            self._key("security:oidc-replay-expiry"),
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
        if len(fields) != expected_fields or fields[0] != b"2":
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
        if name in _ADMISSION_SCRIPTS | _SETTLEMENT_SCRIPTS or name == "drain_complete":
            keys = [
                *keys,
                self._key("generic", ADMISSION_FENCE_KEY),
                self._key("generic", ADMISSION_BINDING_KEY),
            ]
            args = [*args, self._tag.encode("ascii")]
        await self._get_client()
        try:
            return await self._scripts[name](keys=keys, args=args)
        except UnicodeError:
            raise CoordinationCorruptError("Coordination reply is invalid.") from None
        except Exception as exc:
            error_text = str(exc).upper()
            if "COORDINATION_ADMISSION_FENCED" in error_text:
                raise CoordinationAdmissionFencedError(
                    "Coordination admission is drained."
                ) from None
            if "COORDINATION_DRAIN_CONFLICT" in error_text:
                raise CoordinationUnavailableError(
                    "Coordination drain transition does not match."
                ) from None
            if "COORDINATION_RECONCILIATION_REQUIRED" in error_text:
                raise CoordinationReconciliationRequiredError(
                    "Reconciliation is required."
                ) from None
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
        reply = await self._run_script(
            "epoch_read", keys=[self._key("epoch"), self._key("initialization")], args=[]
        )
        return _decode_epoch_reply(reply)

    async def read_coordination_time(self, *, epoch: int) -> CoordinationTime:
        requested_epoch = validate_epoch(epoch)
        reply = await self._run_script(
            "time_read",
            keys=[self._key("epoch"), self._key("initialization")],
            args=[_integer_bytes(requested_epoch)],
        )
        return _decode_time_reply(reply)

    async def advance_epoch(self, expected_epoch: int, operation_id: str) -> Epoch:
        expected = validate_epoch(expected_epoch)
        operation = validate_operation_id(operation_id)
        reply = await self._run_script(
            "epoch_advance",
            keys=[
                self._key("epoch"),
                self._key("replay:epoch-advance"),
                self._key("expiry:epoch-advance"),
                self._key("initialization"),
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
                self._key("initialization"),
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

        def request_fingerprint(value: CasRequest) -> bytes:
            return _fingerprint(
                value.key,
                value.expected_revision,
                value.payload,
                float(value.ttl_seconds),
                value.epoch,
            )

        fingerprint = request_fingerprint(request)
        proof_operation, proof_fingerprint = b"", b""
        if request.settlement is not None:
            proof_operation = request.settlement.admission.operation_id.encode("ascii")
            proof_fingerprint = request_fingerprint(request.settlement.admission)
            fingerprint = _fingerprint(fingerprint, proof_operation, proof_fingerprint)
        reply = await self._run_script(
            "cas",
            keys=[
                self._key("epoch"),
                self._key("cas", request.key),
                self._key("replay:cas"),
                self._key("expiry:cas"),
                self._key("initialization"),
            ],
            args=[
                _integer_bytes(request.expected_revision),
                request.payload,
                _integer_bytes(ttl),
                _integer_bytes(request.epoch),
                request.operation_id.encode("ascii"),
                fingerprint,
                _integer_bytes(self._replay_limit),
                proof_operation,
                proof_fingerprint,
            ],
        )
        return _decode_cas_reply(reply)

    async def complete_admission_drain(
        self, fence: AdmissionFence, *, epoch: int, operation_id: str
    ) -> None:
        validate_epoch(epoch)
        validate_operation_id(operation_id)
        if (
            type(fence) is not AdmissionFence
            or fence.epoch != epoch - 1
            or not fence.quota_reconciliation_complete
        ):
            raise ValueError("Coordination drain is invalid.")
        reply = await self._run_script(
            "drain_complete",
            keys=[
                self._key("epoch"),
                self._key("replay:epoch-ready"),
                self._key("expiry:epoch-ready"),
                self._key("initialization"),
            ],
            args=[
                _integer_bytes(epoch),
                operation_id.encode("ascii"),
                fence.encode().encode("ascii"),
            ],
        )
        if reply != [b"1", b"ok"]:
            raise CoordinationCorruptError("Coordination drain reply is invalid.")

    async def read_cas(self, key: str, *, epoch: int) -> CasSnapshot:
        logical_key = _validate_identifier(key, "Coordination key")
        requested_epoch = validate_epoch(epoch)
        reply = await self._run_script(
            "cas_read",
            keys=[
                self._key("cas", logical_key),
                self._key("epoch"),
                self._key("initialization"),
            ],
            args=[_integer_bytes(requested_epoch)],
        )
        return _decode_cas_snapshot_reply(reply)

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
                self._key("initialization"),
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
            "invalidation_read",
            keys=[
                self._key("invalidation", logical_scope),
                self._key("epoch"),
                self._key("initialization"),
            ],
            args=[],
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
                _integer_bytes(_QUOTA_RATE_WINDOW_MS + 1_000),
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
                _integer_bytes(_QUOTA_RATE_WINDOW_MS + 1_000),
                _integer_bytes(self._quota_record_limit),
                _integer_bytes(self._replay_limit),
            ],
        )
        return _decode_quota_release_reply(reply)

    async def reconcile_quota_state(
        self, *, epoch: int, cursor: str | None, limit: int, apply: bool
    ) -> QuotaReconciliationResult:
        requested_epoch = validate_epoch(epoch)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 256:
            raise ValueError("Quota reconciliation limit is invalid.")
        if not isinstance(apply, bool):
            raise ValueError("Quota reconciliation mode is invalid.")
        state = _decode_quota_reconciliation_cursor(cursor)
        current = await self.read_epoch()
        if current.epoch != requested_epoch or current.state is not EpochState.RECONCILING:
            raise CoordinationUnavailableError("Coordination epoch is not reconciling.")
        completion_key = self._key("quota:reconciliation", str(requested_epoch))
        completed, completion_ttl = await asyncio.gather(
            self._run_command("get", completion_key),
            self._run_command("pttl", completion_key),
        )
        if completed is not None:
            if completed != b"1|complete" or completion_ttl != -1:
                raise CoordinationCorruptError("Stored coordination state is invalid.")
            return QuotaReconciliationResult(0, True, None)
        if completion_ttl != -2:
            raise CoordinationCorruptError("Stored coordination state is invalid.")

        family = state["family"]
        assert isinstance(family, str)
        target = state["target"]
        scan_cursor = state["key_scan"]
        member_cursor = state["member_scan"]
        assert isinstance(scan_cursor, int) and isinstance(member_cursor, int)
        if family == "replays" and target == "@schema":
            schema_prefix = f"{self._prefix}:quota:state-schema:"
            scan_reply = await self._run_command(
                "scan", scan_cursor, match=schema_prefix + "*", count=limit
            )
            if (
                not isinstance(scan_reply, (list, tuple))
                or len(scan_reply) != 2
                or isinstance(scan_reply[0], bool)
                or not isinstance(scan_reply[0], int)
                or not 0 <= scan_reply[0] <= MAX_COORDINATION_INTEGER
                or not isinstance(scan_reply[1], (list, tuple))
                or len(scan_reply[1]) > limit
                or any(not isinstance(key, bytes) for key in scan_reply[1])
            ):
                raise CoordinationCorruptError("Coordination reply is invalid.")
            markers = sorted(set(scan_reply[1]))
            if len(markers) != len(scan_reply[1]):
                raise CoordinationCorruptError("Coordination reply is invalid.")
            for marker_key_bytes in markers:
                try:
                    marker_key = marker_key_bytes.decode("ascii")
                except UnicodeDecodeError:
                    raise CoordinationCorruptError(
                        "Stored coordination state is invalid."
                    ) from None
                digest_text = marker_key.removeprefix(schema_prefix)
                if marker_key != schema_prefix + digest_text:
                    raise CoordinationCorruptError("Stored coordination state is invalid.")
                key_digest = digest_text.encode("ascii")
                self._quota_bucket_key("quota:records", key_digest)
                marker, marker_ttl = await asyncio.gather(
                    self._run_command("get", marker_key),
                    self._run_command("pttl", marker_key),
                )
                _validate_quota_schema_marker(marker)
                if marker_ttl != -1:
                    raise CoordinationCorruptError("Stored coordination state is invalid.")
                record_count, replay_count = await asyncio.gather(
                    self._run_command("hlen", self._quota_bucket_key("quota:records", key_digest)),
                    self._run_command("hlen", self._quota_bucket_key("quota:replay", key_digest)),
                )
                if (
                    isinstance(record_count, bool)
                    or not isinstance(record_count, int)
                    or isinstance(replay_count, bool)
                    or not isinstance(replay_count, int)
                    or record_count != 0
                    or replay_count != 0
                ):
                    raise CoordinationCorruptError("Stored coordination state is invalid.")
                if apply:
                    deleted = await self._run_command(
                        "delete", self._quota_bucket_key("quota:rate-buckets", key_digest)
                    )
                    if (
                        isinstance(deleted, bool)
                        or not isinstance(deleted, int)
                        or deleted
                        not in {
                            0,
                            1,
                        }
                    ):
                        raise CoordinationCorruptError("Coordination reply is invalid.")
                    reply = await self._run_command(
                        "set", marker_key, f"2|{requested_epoch}|ready".encode("ascii")
                    )
                    if reply is not True:
                        raise CoordinationUnavailableError("Redis coordination is unavailable.")
            next_schema_scan = scan_reply[0]
            if next_schema_scan != 0:
                return QuotaReconciliationResult(
                    len(markers),
                    False,
                    _encode_quota_reconciliation_cursor(
                        family="replays",
                        key_scan=next_schema_scan,
                        target="@schema",
                        member_scan=0,
                    ),
                )
            for pending_family, pending_prefix in (
                ("records", f"{self._prefix}:quota:records:*"),
                ("replays", f"{self._prefix}:quota:replay:*"),
            ):
                pending_reply = await self._run_command("scan", 0, match=pending_prefix, count=1)
                if (
                    not isinstance(pending_reply, (list, tuple))
                    or len(pending_reply) != 2
                    or isinstance(pending_reply[0], bool)
                    or not isinstance(pending_reply[0], int)
                    or not 0 <= pending_reply[0] <= MAX_COORDINATION_INTEGER
                    or not isinstance(pending_reply[1], (list, tuple))
                    or any(not isinstance(key, bytes) for key in pending_reply[1])
                ):
                    raise CoordinationCorruptError("Coordination reply is invalid.")
                if pending_reply[0] != 0 or pending_reply[1]:
                    return QuotaReconciliationResult(
                        len(markers),
                        False,
                        _encode_quota_reconciliation_cursor(
                            family=pending_family,
                            key_scan=0,
                            target=None,
                            member_scan=0,
                        ),
                    )
            if apply:
                reply = await self._run_command("set", completion_key, b"1|complete")
                if reply is not True:
                    raise CoordinationUnavailableError("Redis coordination is unavailable.")
            return QuotaReconciliationResult(len(markers), True, None)

        category = "records" if family == "records" else "replay"
        index_category = "lifecycle" if family == "records" else "replay-expiry"
        target_prefix = f"{self._prefix}:quota:{category}:"
        next_scan = scan_cursor
        if target is None:
            scan_reply = await self._run_command(
                "scan", scan_cursor, match=target_prefix + "*", count=1
            )
            if (
                not isinstance(scan_reply, (list, tuple))
                or len(scan_reply) != 2
                or isinstance(scan_reply[0], bool)
                or not isinstance(scan_reply[0], int)
                or not isinstance(scan_reply[1], (list, tuple))
                or any(not isinstance(key, bytes) for key in scan_reply[1])
            ):
                raise CoordinationCorruptError("Coordination reply is invalid.")
            if not 0 <= scan_reply[0] <= MAX_COORDINATION_INTEGER:
                raise CoordinationCorruptError("Coordination reply is invalid.")
            next_scan = scan_reply[0]
            candidates = sorted(scan_reply[1])
            if len(candidates) != len(set(candidates)):
                raise CoordinationCorruptError("Coordination reply is invalid.")
            if candidates:
                try:
                    target = candidates[0].decode("ascii")
                except UnicodeDecodeError:
                    raise CoordinationCorruptError(
                        "Stored coordination state is invalid."
                    ) from None
            elif next_scan != 0:
                return QuotaReconciliationResult(
                    0,
                    False,
                    _encode_quota_reconciliation_cursor(
                        family=family,
                        key_scan=next_scan,
                        target=None,
                        member_scan=0,
                    ),
                )
            elif scan_cursor != 0:
                return QuotaReconciliationResult(
                    0,
                    False,
                    _encode_quota_reconciliation_cursor(
                        family=family,
                        key_scan=0,
                        target=None,
                        member_scan=0,
                    ),
                )
            elif family == "records":
                return QuotaReconciliationResult(
                    0,
                    False,
                    _encode_quota_reconciliation_cursor(
                        family="replays", key_scan=0, target=None, member_scan=0
                    ),
                )
            else:
                return QuotaReconciliationResult(
                    0,
                    False,
                    _encode_quota_reconciliation_cursor(
                        family="replays", key_scan=0, target="@schema", member_scan=0
                    ),
                )

        if not isinstance(target, str) or not target.startswith(target_prefix):
            raise ValueError("Quota reconciliation cursor is invalid.")
        digest_text = target.removeprefix(target_prefix)
        try:
            key_digest = digest_text.encode("ascii")
        except UnicodeEncodeError:
            raise ValueError("Quota reconciliation cursor is invalid.") from None
        self._quota_bucket_key("quota:records", key_digest)
        index_key = self._quota_bucket_key(f"quota:{index_category}", key_digest)
        marker_key = self._quota_bucket_key("quota:state-schema", key_digest)
        record_count, index_count, existing_marker, existing_marker_ttl = await asyncio.gather(
            self._run_command("hlen", target),
            self._run_command("zcard", index_key),
            self._run_command("get", marker_key),
            self._run_command("pttl", marker_key),
        )
        if existing_marker is not None:
            _validate_quota_schema_marker(existing_marker)
            if existing_marker_ttl != -1:
                raise CoordinationCorruptError("Stored coordination state is invalid.")
        elif existing_marker_ttl != -2:
            raise CoordinationCorruptError("Stored coordination state is invalid.")
        if (
            isinstance(record_count, bool)
            or not isinstance(record_count, int)
            or isinstance(index_count, bool)
            or not isinstance(index_count, int)
            or record_count < 0
            or index_count < 0
            or record_count != index_count
            or (record_count > self._quota_record_limit and family == "records")
            or (record_count > self._replay_limit and family == "replays")
        ):
            raise CoordinationCorruptError("Stored coordination state is invalid.")
        start = 0 if apply else member_cursor
        page = await self._run_command(
            "zrange", index_key, start, start + limit - 1, withscores=True
        )
        if not isinstance(page, (list, tuple)) or len(page) > limit:
            raise CoordinationCorruptError("Coordination reply is invalid.")
        now_reply = await self._run_command("time")
        if (
            not isinstance(now_reply, (list, tuple))
            or len(now_reply) != 2
            or any(isinstance(value, bool) or not isinstance(value, int) for value in now_reply)
            or not 0 <= now_reply[0] <= MAX_COORDINATION_INTEGER // 1000
            or not 0 <= now_reply[1] <= 999_999
        ):
            raise CoordinationCorruptError("Coordination reply is invalid.")
        now_ms = now_reply[0] * 1000 + now_reply[1] // 1000
        validated: list[bytes] = []
        locator_names: list[str] = []
        for item in page:
            if (
                not isinstance(item, (list, tuple))
                or len(item) != 2
                or not isinstance(item[0], bytes)
            ):
                raise CoordinationCorruptError("Coordination reply is invalid.")
            member, score = item
            try:
                locator_name = member.decode("ascii")
                if family == "records":
                    _validate_identifier(locator_name, "Reservation ID")
                else:
                    operation_kind, separator, operation_id = locator_name.partition(":")
                    if not separator or operation_kind not in {"reserve", "commit", "release"}:
                        raise ValueError
                    validate_operation_id(operation_id)
            except (UnicodeDecodeError, ValueError):
                raise CoordinationCorruptError("Stored coordination state is invalid.") from None
            value = await self._run_command("hget", target, member)
            if family == "records":
                state_name = _quota_reconciliation_record(value, score, key_digest)
                if state_name == "active":
                    fields = value.split(b"|")
                    active_until = int(fields[4])
                    if active_until > now_ms:
                        raise CoordinationReconciliationRequiredError(
                            "Active quota reservations must drain before reconciliation."
                        )
            else:
                _quota_reconciliation_replay(value, score)
            validated.append(member)
            locator_names.append(locator_name)

        if apply and validated:
            client = await self._get_client()
            try:
                async with client.pipeline(transaction=True) as pipeline:
                    pipeline.hdel(target, *validated)
                    pipeline.zrem(index_key, *validated)
                    locator_category = "quota:locator" if family == "records" else "quota:operation"
                    for identifier in locator_names:
                        pipeline.delete(self._key(locator_category, identifier))
                    results = await pipeline.execute()
                    if (
                        not isinstance(results, (list, tuple))
                        or len(results) != 2 + len(validated)
                        or results[0:2] != [len(validated), len(validated)]
                        or any(
                            isinstance(result, bool)
                            or not isinstance(result, int)
                            or result not in {0, 1}
                            for result in results[2:]
                        )
                    ):
                        raise CoordinationCorruptError("Coordination reply is invalid.")
            except CoordinationCorruptError:
                raise
            except Exception as exc:
                error_text = str(exc).upper()
                if any(marker in error_text for marker in _CORRUPT_DRIVER_ERROR_MARKERS):
                    raise CoordinationCorruptError(
                        "Stored coordination state is invalid."
                    ) from None
                raise CoordinationUnavailableError("Redis coordination is unavailable.") from None

        target_complete = start + len(validated) >= record_count
        if apply and target_complete:
            counterpart = self._quota_bucket_key(
                "quota:replay" if family == "records" else "quota:records",
                key_digest,
            )
            counterpart_count = await self._run_command("hlen", counterpart)
            if isinstance(counterpart_count, bool) or not isinstance(counterpart_count, int):
                raise CoordinationCorruptError("Coordination reply is invalid.")
            if counterpart_count == 0:
                remaining_count = await self._run_command("hlen", target)
                if (
                    isinstance(remaining_count, bool)
                    or not isinstance(remaining_count, int)
                    or remaining_count != 0
                ):
                    raise CoordinationCorruptError("Stored coordination state is invalid.")
                deleted = await self._run_command(
                    "delete", self._quota_bucket_key("quota:rate-buckets", key_digest)
                )
                if (
                    isinstance(deleted, bool)
                    or not isinstance(deleted, int)
                    or deleted
                    not in {
                        0,
                        1,
                    }
                ):
                    raise CoordinationCorruptError("Coordination reply is invalid.")
                reply = await self._run_command(
                    "set",
                    marker_key,
                    f"2|{requested_epoch}|ready".encode("ascii"),
                )
                if reply is not True:
                    raise CoordinationUnavailableError("Redis coordination is unavailable.")
            target = None
            member_cursor = 0
        elif target_complete:
            target = None
            member_cursor = 0
        else:
            member_cursor = start + len(validated)
        return QuotaReconciliationResult(
            len(validated),
            False,
            _encode_quota_reconciliation_cursor(
                family=family,
                key_scan=next_scan,
                target=target,
                member_scan=member_cursor,
            ),
        )

    async def issue_security_session(self, request: SessionIssueRequest) -> SessionMutationResult:
        if not isinstance(request, SessionIssueRequest):
            raise ValueError("Session issue request is invalid.")
        idle_ttl = _ttl_ms(request.idle_ttl_seconds)
        absolute_ttl = _ttl_ms(request.absolute_ttl_seconds)
        assert idle_ttl is not None and absolute_ttl is not None
        fingerprint = _fingerprint(
            request.session_digest,
            request.session_reference,
            request.principal_index,
            request.principal_type.value,
            request.payload,
            float(request.idle_ttl_seconds),
            float(request.absolute_ttl_seconds),
            request.fencing_epoch,
        )
        reply = await self._run_script(
            "security_session_issue",
            keys=self._security_session_keys(),
            args=[
                _integer_bytes(request.fencing_epoch),
                request.session_digest.encode("ascii"),
                request.session_reference.encode("ascii"),
                request.principal_index.encode("ascii"),
                request.principal_type.value.encode("ascii"),
                base64.b64encode(request.payload),
                _integer_bytes(idle_ttl),
                _integer_bytes(absolute_ttl),
                request.operation_id.encode("ascii"),
                fingerprint,
                _integer_bytes(self._security_session_limit),
                _integer_bytes(self._security_replay_limit),
            ],
        )
        return _decode_session_mutation_reply(reply)

    async def resolve_security_session(
        self, request: SessionResolveRequest
    ) -> SessionResolveResult:
        if not isinstance(request, SessionResolveRequest):
            raise ValueError("Session resolve request is invalid.")
        idle_ttl = _ttl_ms(request.idle_ttl_seconds)
        assert idle_ttl is not None
        fingerprint = _fingerprint(
            request.session_digest,
            float(request.idle_ttl_seconds),
            request.fencing_epoch,
        )
        reply = await self._run_script(
            "security_session_resolve",
            keys=self._security_session_keys(),
            args=[
                _integer_bytes(request.fencing_epoch),
                request.session_digest.encode("ascii"),
                _integer_bytes(idle_ttl),
                request.operation_id.encode("ascii"),
                fingerprint,
                _integer_bytes(self._security_replay_limit),
            ],
        )
        return _decode_session_resolve_reply(reply)

    async def rotate_security_session(self, request: SessionRotateRequest) -> SessionMutationResult:
        if not isinstance(request, SessionRotateRequest):
            raise ValueError("Session rotation request is invalid.")
        replacement = request.replacement
        idle_ttl = _ttl_ms(replacement.idle_ttl_seconds)
        absolute_ttl = _ttl_ms(replacement.absolute_ttl_seconds)
        assert idle_ttl is not None and absolute_ttl is not None
        fingerprint = _fingerprint(
            request.current_session_digest,
            replacement.session_digest,
            replacement.session_reference,
            replacement.principal_index,
            replacement.principal_type.value,
            replacement.payload,
            float(replacement.idle_ttl_seconds),
            float(replacement.absolute_ttl_seconds),
            request.fencing_epoch,
        )
        reply = await self._run_script(
            "security_session_rotate",
            keys=self._security_session_keys(),
            args=[
                _integer_bytes(request.fencing_epoch),
                request.current_session_digest.encode("ascii"),
                replacement.session_digest.encode("ascii"),
                replacement.session_reference.encode("ascii"),
                replacement.principal_index.encode("ascii"),
                replacement.principal_type.value.encode("ascii"),
                base64.b64encode(replacement.payload),
                _integer_bytes(idle_ttl),
                _integer_bytes(absolute_ttl),
                request.operation_id.encode("ascii"),
                fingerprint,
                _integer_bytes(self._security_replay_limit),
            ],
        )
        return _decode_session_mutation_reply(reply)

    async def revoke_security_sessions(self, request: SessionRevokeRequest) -> SessionRevokeResult:
        if not isinstance(request, SessionRevokeRequest):
            raise ValueError("Session revocation request is invalid.")
        replay_ttl = _ttl_ms(request.replay_ttl_seconds)
        assert replay_ttl is not None
        fingerprint = _fingerprint(
            request.target.value,
            request.target_value,
            request.fencing_epoch,
            float(request.replay_ttl_seconds),
        )
        reply = await self._run_script(
            "security_session_revoke",
            keys=self._security_session_keys(),
            args=[
                _integer_bytes(request.fencing_epoch),
                request.target.value.encode("ascii"),
                request.target_value.encode("ascii"),
                _integer_bytes(replay_ttl),
                request.operation_id.encode("ascii"),
                fingerprint,
                _integer_bytes(self._security_replay_limit),
            ],
        )
        return _decode_session_revoke_reply(reply)

    async def list_security_sessions(self, request: SessionListRequest) -> SessionPage:
        if not isinstance(request, SessionListRequest):
            raise ValueError("Session list request is invalid.")
        if request.limit > MAX_SECURITY_PAGE_SIZE:
            raise ValueError("Session page size is invalid.")
        reply = await self._run_script(
            "security_session_list",
            keys=self._security_session_keys(),
            args=[
                _integer_bytes(request.fencing_epoch),
                _integer_bytes(request.limit),
                b"" if request.after_reference is None else request.after_reference.encode("ascii"),
            ],
        )
        return _decode_session_page_reply(reply, requested_limit=request.limit)

    async def reserve_security_attempt(
        self, request: AttemptReservationRequest
    ) -> AttemptReservationDecision:
        if not isinstance(request, AttemptReservationRequest):
            raise ValueError("Security attempt request is invalid.")
        window = _ttl_ms(request.window_seconds)
        assert window is not None
        fingerprint = _fingerprint(
            request.category.value,
            request.client_index,
            request.limit,
            float(request.window_seconds),
            request.fencing_epoch,
        )
        reply = await self._run_script(
            "security_attempt_reserve",
            keys=self._security_attempt_keys(request.category),
            args=[
                _integer_bytes(request.fencing_epoch),
                request.client_index.encode("ascii"),
                _integer_bytes(request.limit),
                _integer_bytes(window),
                request.operation_id.encode("ascii"),
                fingerprint,
                _integer_bytes(self._security_attempt_limit),
                _integer_bytes(self._security_replay_limit),
            ],
        )
        return _decode_attempt_reservation_reply(reply)

    async def clear_security_attempts(self, request: AttemptClearRequest) -> AttemptClearResult:
        if not isinstance(request, AttemptClearRequest):
            raise ValueError("Security attempt clear request is invalid.")
        replay_ttl = _ttl_ms(MIN_SECURITY_ATTEMPT_WINDOW_SECONDS)
        assert replay_ttl is not None
        fingerprint = _fingerprint(
            request.category.value,
            request.client_index,
            request.fencing_epoch,
        )
        reply = await self._run_script(
            "security_attempt_clear",
            keys=self._security_attempt_keys(request.category),
            args=[
                _integer_bytes(request.fencing_epoch),
                request.client_index.encode("ascii"),
                _integer_bytes(replay_ttl),
                request.operation_id.encode("ascii"),
                fingerprint,
                _integer_bytes(self._security_replay_limit),
            ],
        )
        return _decode_attempt_clear_reply(reply)

    async def create_oidc_transaction(
        self, request: OidcTransactionCreateRequest
    ) -> TransactionCreateResult:
        if not isinstance(request, OidcTransactionCreateRequest):
            raise ValueError("OIDC transaction create request is invalid.")
        ttl = _ttl_ms(request.ttl_seconds)
        assert ttl is not None
        fingerprint = _fingerprint(
            request.state_index,
            request.browser_index,
            request.payload,
            float(request.ttl_seconds),
            request.fencing_epoch,
        )
        reply = await self._run_script(
            "oidc_transaction_create",
            keys=self._oidc_transaction_keys(),
            args=[
                _integer_bytes(request.fencing_epoch),
                request.state_index.encode("ascii"),
                request.browser_index.encode("ascii"),
                base64.b64encode(request.payload),
                _integer_bytes(ttl),
                request.operation_id.encode("ascii"),
                fingerprint,
                _integer_bytes(self._oidc_transaction_limit),
                _integer_bytes(self._security_replay_limit),
            ],
        )
        return _decode_transaction_create_reply(reply)

    async def consume_oidc_transaction(
        self, request: OidcTransactionConsumeRequest
    ) -> OidcTransactionConsumeResult:
        if not isinstance(request, OidcTransactionConsumeRequest):
            raise ValueError("OIDC transaction consume request is invalid.")
        replay_ttl = _ttl_ms(MAX_OIDC_TRANSACTION_TTL_SECONDS)
        assert replay_ttl is not None
        fingerprint = _fingerprint(
            request.state_index,
            request.browser_index,
            request.fencing_epoch,
        )
        reply = await self._run_script(
            "oidc_transaction_consume",
            keys=self._oidc_transaction_keys(),
            args=[
                _integer_bytes(request.fencing_epoch),
                request.state_index.encode("ascii"),
                request.browser_index.encode("ascii"),
                _integer_bytes(replay_ttl),
                request.operation_id.encode("ascii"),
                fingerprint,
                _integer_bytes(self._security_replay_limit),
            ],
        )
        return _decode_transaction_consume_reply(reply)

    async def close(self) -> None:
        async with self._lifecycle_lock:
            if self._closed:
                return
            if self._close_task is None:
                self._closing = True
                self._close_task = asyncio.create_task(self._close_client())
            close_task = self._close_task
        await asyncio.shield(close_task)

    async def _close_client(self) -> None:
        client = self._client
        try:
            if client is not None:
                await client.aclose()
        except BaseException as exc:
            async with self._lifecycle_lock:
                self._closing = False
                self._close_task = None
            if isinstance(exc, Exception):
                raise CoordinationUnavailableError("Redis coordination is unavailable.") from None
            raise

        async with self._lifecycle_lock:
            self._client = None
            self._scripts = {}
            self._lock_tokens.clear()
            self._closed = True
            self._closing = False
            self._close_task = None

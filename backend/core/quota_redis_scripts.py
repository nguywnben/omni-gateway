"""Redis Lua transitions for bounded Quota State v2."""

from __future__ import annotations

_QUOTA_COMMON = r"""
local RATE_BUCKET_COUNT = 61
local RATE_WINDOW_SECONDS = 60
local MAX_UINT = '9223372036854775807'

local function valid_uint(value)
  return value and (value == '0' or string.match(value, '^[1-9][0-9]*$'))
    and (#value < 19 or (#value == 19 and value <= MAX_UINT))
end
local function valid_positive(value) return valid_uint(value) and value ~= '0' end
local function valid_safe_uint(value)
  return valid_uint(value)
    and (#value < 16 or (#value == 16 and value <= '9007199254740991'))
end
local function valid_hex(value)
  return value and #value == 64 and string.match(value, '^[0-9a-f]+$')
end
local function uint_greater_than(left, right)
  if #left ~= #right then return #left > #right end
  return left > right
end
local function add_uint(left, right)
  if not valid_uint(left) or not valid_uint(right) then return nil end
  local width = math.max(#left, #right)
  local left_padding, right_padding = width - #left, width - #right
  local digits, carry = {}, 0
  for position = width, 1, -1 do
    local left_digit = position > left_padding
      and string.byte(left, position - left_padding) - 48 or 0
    local right_digit = position > right_padding
      and string.byte(right, position - right_padding) - 48 or 0
    local sum = left_digit + right_digit + carry
    table.insert(digits, 1, string.char((sum % 10) + 48))
    carry = math.floor(sum / 10)
  end
  if carry > 0 then table.insert(digits, 1, string.char(carry + 48)) end
  local result = table.concat(digits)
  if uint_greater_than(result, MAX_UINT) then return nil end
  return result
end
local function subtract_uint(left, right)
  if not valid_uint(left) or not valid_uint(right) or uint_greater_than(right, left) then
    return nil
  end
  local width, right_padding = #left, #left - #right
  local digits, borrow = {}, 0
  for position = width, 1, -1 do
    local left_digit = string.byte(left, position) - 48 - borrow
    local right_digit = position > right_padding
      and string.byte(right, position - right_padding) - 48 or 0
    if left_digit < right_digit then left_digit, borrow = left_digit + 10, 1
    else borrow = 0 end
    table.insert(digits, 1, string.char(left_digit - right_digit + 48))
  end
  local result = string.gsub(table.concat(digits), '^0+', '')
  return result == '' and '0' or result
end
local function split_exact(value, count, maximum)
  if not value or #value > maximum then return nil end
  local fields = {}
  for field in string.gmatch(value .. '|', '(.-)|') do fields[#fields + 1] = field end
  if #fields ~= count then return nil end
  return fields
end

local function parse_record(value)
  local f = split_exact(value, 14, 1536)
  if not f then return nil end
  local record = {
    schema=f[1], fingerprint=f[2], key=f[3], state=f[4], active_until=f[5],
    retained_until=f[6], accepted_at=f[7], estimated_tokens=f[8],
    committed_at=f[9], actual_tokens=f[10], rpm_limit=f[11], tpm_limit=f[12],
    retention_ms=f[13], next_expiry=f[14]
  }
  if record.schema ~= '2' or not valid_hex(record.fingerprint) or not valid_hex(record.key)
    or (record.state ~= 'active' and record.state ~= 'committed'
      and record.state ~= 'released' and record.state ~= 'expired')
    or not valid_safe_uint(record.active_until) or record.active_until == '0'
    or not valid_safe_uint(record.retained_until) or record.retained_until == '0'
    or not valid_safe_uint(record.accepted_at) or record.accepted_at == '0'
    or not valid_uint(record.estimated_tokens)
    or not valid_safe_uint(record.committed_at)
    or not valid_uint(record.actual_tokens)
    or (record.rpm_limit ~= 'n' and not valid_positive(record.rpm_limit))
    or (record.tpm_limit ~= 'n' and not valid_positive(record.tpm_limit))
    or not valid_safe_uint(record.retention_ms) or tonumber(record.retention_ms) < 61000
    or not valid_safe_uint(record.next_expiry) or record.next_expiry == '0' then return nil end
  record.active_until_number, record.retained_until_number =
    tonumber(record.active_until), tonumber(record.retained_until)
  record.accepted_at_number, record.committed_at_number =
    tonumber(record.accepted_at), tonumber(record.committed_at)
  record.retention_ms_number, record.next_expiry_number =
    tonumber(record.retention_ms), tonumber(record.next_expiry)
  if record.accepted_at_number > record.active_until_number
    or record.active_until_number > record.retained_until_number
    or record.next_expiry_number > record.retained_until_number then return nil end
  if record.state == 'active' then
    if record.committed_at ~= '0' or record.actual_tokens ~= '0'
      or record.next_expiry ~= record.active_until then return nil end
  elseif record.state == 'committed' then
    if record.committed_at == '0' or record.committed_at_number < record.accepted_at_number
      or record.committed_at_number > record.active_until_number
      or record.committed_at_number > 9007199254679991
      or record.retained_until_number ~= math.max(record.active_until_number,
        record.committed_at_number + 61000)
      or record.next_expiry ~= record.retained_until then return nil end
  elseif record.committed_at ~= '0' or record.actual_tokens ~= '0'
    or record.next_expiry ~= record.retained_until then return nil end
  return record
end
local function encode_record(record)
  return table.concat({record.schema, record.fingerprint, record.key, record.state,
    record.active_until, record.retained_until, record.accepted_at,
    record.estimated_tokens, record.committed_at, record.actual_tokens,
    record.rpm_limit, record.tpm_limit, record.retention_ms, record.next_expiry}, '|')
end
local function validate_record_pair(value, score, expected_key)
  local record = parse_record(value)
  if not record or record.key ~= expected_key or not valid_safe_uint(score)
    or tonumber(score) ~= record.next_expiry_number then return nil end
  return record
end

local function parse_replay(value, score)
  local f = split_exact(value, 7, 1024)
  if not f or f[1] ~= '2' or not valid_hex(f[2])
    or (f[3] ~= 'reserve' and f[3] ~= 'commit' and f[3] ~= 'release')
    or not valid_uint(f[6]) or not valid_safe_uint(f[7]) or f[7] == '0'
    or not valid_safe_uint(score) or tonumber(score) ~= tonumber(f[7]) then return nil end
  if f[3] == 'reserve' then
    if (f[4] ~= 'accepted' and f[4] ~= 'denied')
      or (f[4] == 'accepted' and (f[5] ~= '' or f[6] ~= '0'))
      or (f[4] == 'denied' and f[5] ~= 'rpm' and f[5] ~= 'tpm'
        and f[5] ~= 'capacity' and f[5] ~= 'reconciliation_required') then return nil end
  elseif f[3] == 'commit' then
    if (f[4] ~= 'committed' and f[4] ~= 'not_committed')
      or (f[5] ~= '0' and f[5] ~= '1') or f[6] ~= '0' then return nil end
  elseif (f[4] ~= 'released' and f[4] ~= 'not_released')
    or f[5] ~= '' or f[6] ~= '0' then return nil end
  return {fingerprint=f[2], kind=f[3], status=f[4], value=f[5], retry=f[6], expiry=f[7]}
end
local function encode_replay(fingerprint, kind, status, value, retry, expiry)
  return table.concat({'2', fingerprint, kind, status, value, retry, expiry}, '|')
end

local function read_reservation_locator(key)
  local value = redis.call('GET', key)
  if not value then return nil end
  if redis.call('PTTL', key) <= 0 then return false end
  local schema, digest = string.match(value, '^([^|]+)|([^|]+)$')
  if schema ~= '2' or not valid_hex(digest) then return false end
  return digest
end
local function read_operation_locator(key)
  local value = redis.call('GET', key)
  if not value then return nil end
  if redis.call('PTTL', key) <= 0 then return false end
  local schema, digest, fingerprint = string.match(value, '^([^|]+)|([^|]+)|([^|]+)$')
  if schema ~= '2' or not valid_hex(digest) or not valid_hex(fingerprint) then return false end
  return {key=digest, fingerprint=fingerprint}
end

local function ready_epoch(expected)
  local initialized, encoded = redis.call('GET', KEYS[8]), redis.call('GET', KEYS[1])
  if initialized ~= '1|initialized' or not encoded
    or redis.call('PTTL', KEYS[8]) ~= -1 or redis.call('PTTL', KEYS[1]) ~= -1 then return nil end
  local schema, epoch, state = string.match(encoded, '^([^|]+)|([^|]+)|([^|]+)$')
  if schema ~= '1' or not valid_positive(epoch)
    or (state ~= 'ready' and state ~= 'reconciling') then return nil end
  return epoch == expected and state == 'ready', state, epoch
end
local function quota_schema(expected_epoch)
  local marker = redis.call('GET', KEYS[10])
  if not marker then
    local empty = redis.call('HLEN', KEYS[2]) == 0 and redis.call('ZCARD', KEYS[3]) == 0
      and redis.call('HLEN', KEYS[4]) == 0 and redis.call('ZCARD', KEYS[5]) == 0
      and redis.call('HLEN', KEYS[9]) == 0 and not redis.call('GET', KEYS[6])
      and not redis.call('GET', KEYS[7])
    return empty and 'initialize' or 'reconciliation_required'
  end
  if redis.call('PTTL', KEYS[10]) ~= -1 then return nil end
  local version, epoch, state = string.match(marker, '^([^|]+)|([^|]+)|([^|]+)$')
  if version == '1' and valid_positive(epoch) then return 'reconciliation_required' end
  if version ~= '2' or not valid_positive(epoch) or state ~= 'ready' then return nil end
  if epoch ~= expected_epoch then return 'reconciliation_required' end
  return 'ready'
end

local function plan_prune_target(now_ms, expected_key, record_limit, replay_limit)
  local record_count, lifecycle_count = redis.call('HLEN', KEYS[2]), redis.call('ZCARD', KEYS[3])
  local replay_count, replay_expiry_count = redis.call('HLEN', KEYS[4]), redis.call('ZCARD', KEYS[5])
  if record_count ~= lifecycle_count or replay_count ~= replay_expiry_count
    or record_count > record_limit or replay_count > replay_limit then return nil end
  local replay_due = redis.call('ZRANGEBYSCORE', KEYS[5], '-inf', now_ms, 'LIMIT', 0, 257)
  local lifecycle_due = redis.call('ZRANGEBYSCORE', KEYS[3], '-inf', now_ms, 'LIMIT', 0, 257)
  if #replay_due > 256 or #lifecycle_due > 256
    or #replay_due + #lifecycle_due > 256 then return false end
  for _, operation_id in ipairs(replay_due) do
    if not parse_replay(redis.call('HGET', KEYS[4], operation_id),
      redis.call('ZSCORE', KEYS[5], operation_id)) then return nil end
  end
  local due_records = {}
  for index, reservation_id in ipairs(lifecycle_due) do
    local record = validate_record_pair(redis.call('HGET', KEYS[2], reservation_id),
      redis.call('ZSCORE', KEYS[3], reservation_id), expected_key)
    if not record or record.next_expiry_number > now_ms then return nil end
    due_records[index] = {reservation_id, record}
  end
  return {record_count=record_count, replay_count=replay_count,
    replay_due=replay_due, due_records=due_records}
end
local function record_after_planned_prune(record, now_ms)
  if record and record.next_expiry_number <= now_ms then return nil end
  return record
end
local function apply_cleanup(plan)
  if #plan.replay_due > 0 then
    redis.call('HDEL', KEYS[4], unpack(plan.replay_due))
    redis.call('ZREM', KEYS[5], unpack(plan.replay_due))
  end
  for _, pair in ipairs(plan.due_records) do
    redis.call('HDEL', KEYS[2], pair[1])
    redis.call('ZREM', KEYS[3], pair[1])
  end
end

local function parse_bucket(value, slot, now_second)
  local f = split_exact(value, 4, 128)
  if not f or f[1] ~= '2' or not valid_safe_uint(f[2])
    or tonumber(f[2]) % RATE_BUCKET_COUNT ~= slot or tonumber(f[2]) > now_second
    or not valid_uint(f[3]) or not valid_uint(f[4]) then return nil end
  return {second=tonumber(f[2]), requests=f[3], tokens=f[4], dirty=false}
end
local function read_rate_window(now_second)
  local count = redis.call('HLEN', KEYS[9])
  if count > RATE_BUCKET_COUNT then return nil end
  local names = redis.call('HKEYS', KEYS[9])
  if #names ~= count then return nil end
  for _, name in ipairs(names) do
    if not valid_uint(name) or tonumber(name) >= RATE_BUCKET_COUNT
      or tostring(tonumber(name)) ~= name then return nil end
  end
  local fields = {}
  for slot = 0, RATE_BUCKET_COUNT - 1 do fields[#fields + 1] = tostring(slot) end
  local values = redis.call('HMGET', KEYS[9], unpack(fields))
  local window = {slots={}}
  for slot = 0, RATE_BUCKET_COUNT - 1 do
    local value = values[slot + 1]
    if value then
      local bucket = parse_bucket(value, slot, now_second)
      if not bucket then return nil end
      window.slots[slot + 1] = bucket
    end
  end
  return window
end
local function rate_totals(window, now_second)
  local requests, tokens, earliest = '0', '0', nil
  for slot = 0, RATE_BUCKET_COUNT - 1 do
    local bucket = window.slots[slot + 1]
    if bucket and bucket.second >= now_second - RATE_WINDOW_SECONDS then
      requests, tokens = add_uint(requests, bucket.requests), add_uint(tokens, bucket.tokens)
      if not requests or not tokens then return nil end
      if bucket.requests ~= '0' or bucket.tokens ~= '0' then
        earliest = earliest and math.min(earliest, bucket.second) or bucket.second
      end
    end
  end
  return {requests=requests, tokens=tokens, earliest=earliest}
end
local function adjust_rate(window, second, request_mode, requests, token_mode, tokens)
  local slot = second % RATE_BUCKET_COUNT
  local bucket = window.slots[slot + 1]
  if not bucket or bucket.second ~= second then
    if request_mode == 'subtract' or token_mode == 'subtract' then return false end
    bucket = {second=second, requests='0', tokens='0', dirty=true}
    window.slots[slot + 1] = bucket
  end
  if request_mode == 'add' then bucket.requests = add_uint(bucket.requests, requests)
  elseif request_mode == 'subtract' then bucket.requests = subtract_uint(bucket.requests, requests) end
  if token_mode == 'add' then bucket.tokens = add_uint(bucket.tokens, tokens)
  elseif token_mode == 'subtract' then bucket.tokens = subtract_uint(bucket.tokens, tokens) end
  if not bucket.requests or not bucket.tokens then return false end
  bucket.dirty = true
  return true
end
local function apply_rate(window)
  for slot = 0, RATE_BUCKET_COUNT - 1 do
    local bucket = window.slots[slot + 1]
    if bucket and bucket.dirty then
      redis.call('HSET', KEYS[9], tostring(slot), table.concat(
        {'2', tostring(bucket.second), bucket.requests, bucket.tokens}, '|'))
    end
  end
end
local function retry_after(now_ms, earliest_second)
  if not earliest_second then return '1' end
  return tostring(math.max(1, math.ceil(((earliest_second + RATE_BUCKET_COUNT) * 1000
    - now_ms) / 1000)))
end
"""


QUOTA_RESERVE_SCRIPT = (
    "-- omni:quota_reserve:v2\n"
    + _QUOTA_COMMON
    + r"""
local fenced, epoch_state, current_epoch = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then return {'1', 'denied', ARGV[2], epoch_state == 'reconciling'
  and 'reconciling' or 'stale_epoch', '0', '0'} end
if not ARGV[2] or #ARGV[2] == 0 or #ARGV[2] > 255 or not valid_hex(ARGV[3])
  or not valid_hex(ARGV[4]) or not ARGV[5] or #ARGV[5] == 0 or #ARGV[5] > 263
  or not valid_safe_uint(ARGV[6]) or tonumber(ARGV[6]) < 61000
  or not valid_safe_uint(ARGV[7]) or tonumber(ARGV[7]) < 61000
  or not valid_positive(ARGV[8]) or tonumber(ARGV[8]) > 100000
  or not valid_positive(ARGV[9]) or tonumber(ARGV[9]) > 100000
  or not valid_uint(ARGV[11])
  or (ARGV[13] ~= '' and not valid_positive(ARGV[13]))
  or (ARGV[14] ~= '' and not valid_positive(ARGV[14])) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local schema_status = quota_schema(current_epoch)
if schema_status == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if schema_status == 'reconciliation_required' then
  return {'1', 'denied', ARGV[2], 'reconciliation_required', '0', '0'}
end
local reservation_key = read_reservation_locator(KEYS[6])
local operation = read_operation_locator(KEYS[7])
if reservation_key == false or operation == false then return redis.error_reply('COORDINATION_CORRUPT') end
if reservation_key and reservation_key ~= ARGV[3] then
  return {'1', 'denied', ARGV[2], 'conflict', '0', '0'}
end
if operation and (operation.key ~= ARGV[3] or operation.fingerprint ~= ARGV[4]) then
  return {'1', 'denied', ARGV[2], 'conflict', '0', '0'}
end
local clock = redis.call('TIME')
local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
local now_second = math.floor(now_ms / 1000)
local plan = plan_prune_target(now_ms, ARGV[3], tonumber(ARGV[8]), tonumber(ARGV[9]))
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not plan then return {'1', 'denied', ARGV[2], 'reconciliation_required', '0', '0'} end
local replay_value, replay_score = redis.call('HGET', KEYS[4], ARGV[5]),
  redis.call('ZSCORE', KEYS[5], ARGV[5])
local replay = (replay_value or replay_score) and parse_replay(replay_value, replay_score) or nil
if (replay_value or replay_score) and not replay then return redis.error_reply('COORDINATION_CORRUPT') end
if replay and tonumber(replay.expiry) <= now_ms then replay = nil end
if operation and not replay then return redis.error_reply('COORDINATION_CORRUPT') end
if replay then
  apply_cleanup(plan)
  if replay.fingerprint ~= ARGV[4] or replay.kind ~= 'reserve' then
    return {'1', 'denied', ARGV[2], 'conflict', '0', '0'}
  end
  return {'1', replay.status, ARGV[2], replay.value, replay.retry, '1'}
end
local encoded, score = redis.call('HGET', KEYS[2], ARGV[2]),
  redis.call('ZSCORE', KEYS[3], ARGV[2])
local record = (encoded or score) and validate_record_pair(encoded, score, ARGV[3]) or nil
if (encoded or score) and not record then return redis.error_reply('COORDINATION_CORRUPT') end
record = record_after_planned_prune(record, now_ms)
if reservation_key and not record then return redis.error_reply('COORDINATION_CORRUPT') end
if record then
  apply_cleanup(plan)
  if record.fingerprint == ARGV[4] then
    return {'1', 'accepted', ARGV[2], '', '0', '1'}
  end
  return {'1', 'denied', ARGV[2], 'conflict', '0', '0'}
end
local effective_records = plan.record_count - #plan.due_records
local effective_replays = plan.replay_count - #plan.replay_due
local status, reason, retry = 'accepted', '', '0'
local window = read_rate_window(now_second)
if not window then return redis.error_reply('COORDINATION_CORRUPT') end
local totals = rate_totals(window, now_second)
if not totals then return redis.error_reply('COORDINATION_CORRUPT') end
if effective_records >= tonumber(ARGV[8]) then status, reason = 'denied', 'capacity'
elseif ARGV[13] ~= '' and uint_greater_than(totals.requests, ARGV[13])
  or ARGV[13] ~= '' and totals.requests == ARGV[13] then
  status, reason, retry = 'denied', 'rpm', retry_after(now_ms, totals.earliest)
else
  local projected = add_uint(totals.tokens, ARGV[11])
  if not projected and ARGV[14] == '' then return redis.error_reply('COORDINATION_CORRUPT') end
  if ARGV[14] ~= '' and (not projected or uint_greater_than(projected, ARGV[14])) then
    status, reason, retry = 'denied', 'tpm', retry_after(now_ms, totals.earliest)
  end
end
if effective_replays >= tonumber(ARGV[9]) then
  return {'1', 'denied', ARGV[2], 'reconciliation_required', '0', '0'}
end
local active_until = now_ms + tonumber(ARGV[6])
local retained_until = math.max(active_until, now_ms + tonumber(ARGV[7]))
local expiry = status == 'accepted' and retained_until or now_ms + tonumber(ARGV[6])
local expiry_text = string.format('%.0f', expiry)
if status == 'accepted' and not adjust_rate(window, now_second, 'add', '1', 'add', ARGV[11]) then
  return redis.error_reply('COORDINATION_CORRUPT')
end
-- apply validated mutation
if schema_status == 'initialize' then
  redis.call('SET', KEYS[10], '2|' .. current_epoch .. '|ready')
end
apply_cleanup(plan)
if status == 'accepted' then
  apply_rate(window)
  local active_text = string.format('%.0f', active_until)
  local record_value = table.concat({'2', ARGV[4], ARGV[3], 'active', active_text,
    expiry_text, tostring(now_ms), ARGV[11], '0', '0',
    ARGV[13] == '' and 'n' or ARGV[13], ARGV[14] == '' and 'n' or ARGV[14],
    ARGV[7], active_text}, '|')
  redis.call('HSET', KEYS[2], ARGV[2], record_value)
  redis.call('ZADD', KEYS[3], active_until, ARGV[2])
  redis.call('SET', KEYS[6], '2|' .. ARGV[3], 'PXAT', expiry)
end
redis.call('HSET', KEYS[4], ARGV[5],
  encode_replay(ARGV[4], 'reserve', status, reason, retry, expiry_text))
redis.call('ZADD', KEYS[5], expiry, ARGV[5])
redis.call('SET', KEYS[7], '2|' .. ARGV[3] .. '|' .. ARGV[4], 'PXAT', expiry)
return {'1', status, ARGV[2], reason, retry, '0'}
"""
)


QUOTA_COMMIT_SCRIPT = (
    "-- omni:quota_commit:v2\n"
    + _QUOTA_COMMON
    + r"""
local fenced, _, current_epoch = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then return {'1', 'not_committed', '0', '0'} end
if not valid_hex(ARGV[2]) or not ARGV[3] or #ARGV[3] == 0 or #ARGV[3] > 263
  or not ARGV[4] or #ARGV[4] == 0 or #ARGV[4] > 255 or not valid_hex(ARGV[5])
  or (ARGV[7] ~= '' and not valid_uint(ARGV[7]))
  or (ARGV[9] ~= '0' and ARGV[9] ~= '1')
  or not valid_positive(ARGV[10]) or tonumber(ARGV[10]) > 100000
  or not valid_positive(ARGV[11]) or tonumber(ARGV[11]) > 100000
  or not valid_safe_uint(ARGV[12]) or tonumber(ARGV[12]) < 61000 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local schema_status = quota_schema(current_epoch)
if schema_status == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if schema_status == 'reconciliation_required' then
  return {'1', 'reconciliation_required', '0', '0'}
end
local reservation_key = read_reservation_locator(KEYS[6])
local operation = read_operation_locator(KEYS[7])
if reservation_key == false or operation == false then return redis.error_reply('COORDINATION_CORRUPT') end
if reservation_key and reservation_key ~= ARGV[5] then return {'1', 'not_committed', '0', '0'} end
if operation and (operation.key ~= ARGV[5] or operation.fingerprint ~= ARGV[2]) then
  return {'1', 'not_committed', '0', '0'}
end
local clock = redis.call('TIME')
local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
local now_second = math.floor(now_ms / 1000)
local plan = plan_prune_target(now_ms, ARGV[5], tonumber(ARGV[10]), tonumber(ARGV[11]))
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not plan then return {'1', 'reconciliation_required', '0', '0'} end
local replay_value, replay_score = redis.call('HGET', KEYS[4], ARGV[3]),
  redis.call('ZSCORE', KEYS[5], ARGV[3])
local replay = (replay_value or replay_score) and parse_replay(replay_value, replay_score) or nil
if (replay_value or replay_score) and not replay then return redis.error_reply('COORDINATION_CORRUPT') end
if replay and tonumber(replay.expiry) <= now_ms then replay = nil end
if operation and not replay then return redis.error_reply('COORDINATION_CORRUPT') end
if replay then
  apply_cleanup(plan)
  if replay.fingerprint ~= ARGV[2] or replay.kind ~= 'commit' then
    return {'1', 'not_committed', '0', '0'}
  end
  return {'1', replay.status, replay.value, '1'}
end
local encoded, score = redis.call('HGET', KEYS[2], ARGV[4]),
  redis.call('ZSCORE', KEYS[3], ARGV[4])
local record = (encoded or score) and validate_record_pair(encoded, score, ARGV[5]) or nil
if (encoded or score) and not record then return redis.error_reply('COORDINATION_CORRUPT') end
record = record_after_planned_prune(record, now_ms)
if reservation_key and not record then return redis.error_reply('COORDINATION_CORRUPT') end
if plan.replay_count - #plan.replay_due >= tonumber(ARGV[11]) then
  return {'1', 'reconciliation_required', '0', '0'}
end
local status, overspent = 'not_committed', '0'
local expiry = record and record.retained_until_number or now_ms + tonumber(ARGV[12])
local window = nil
if record and record.state == 'active' and record.active_until_number > now_ms then
  window = read_rate_window(now_second)
  if not window then return redis.error_reply('COORDINATION_CORRUPT') end
  local accepted_second = math.floor(record.accepted_at_number / 1000)
  if accepted_second >= now_second - RATE_WINDOW_SECONDS
    and not adjust_rate(window, accepted_second, 'subtract', '1',
      'subtract', record.estimated_tokens) then return redis.error_reply('COORDINATION_CORRUPT') end
  local actual_tokens = ARGV[7] == '' and record.estimated_tokens or ARGV[7]
  if not adjust_rate(window, now_second, 'add', '1', 'add', actual_tokens) then
    return redis.error_reply('COORDINATION_CORRUPT')
  end
  local totals = rate_totals(window, now_second)
  if not totals then return redis.error_reply('COORDINATION_CORRUPT') end
  if record.tpm_limit ~= 'n' and uint_greater_than(totals.tokens, record.tpm_limit) then
    overspent = '1'
  end
  status = 'committed'
  expiry = math.max(record.active_until_number, now_ms + 61000)
  record.state, record.committed_at, record.actual_tokens =
    'committed', tostring(now_ms), actual_tokens
  record.retained_until, record.next_expiry =
    string.format('%.0f', expiry), string.format('%.0f', expiry)
end
local expiry_text = string.format('%.0f', expiry)
-- apply validated mutation
if schema_status == 'initialize' then
  redis.call('SET', KEYS[10], '2|' .. current_epoch .. '|ready')
end
apply_cleanup(plan)
if status == 'committed' then
  apply_rate(window)
  redis.call('HSET', KEYS[2], ARGV[4], encode_record(record))
  redis.call('ZADD', KEYS[3], expiry, ARGV[4])
  redis.call('SET', KEYS[6], '2|' .. ARGV[5], 'PXAT', expiry)
end
redis.call('HSET', KEYS[4], ARGV[3],
  encode_replay(ARGV[2], 'commit', status, overspent, '0', expiry_text))
redis.call('ZADD', KEYS[5], expiry, ARGV[3])
redis.call('SET', KEYS[7], '2|' .. ARGV[5] .. '|' .. ARGV[2], 'PXAT', expiry)
return {'1', status, overspent, '0'}
"""
)


QUOTA_RELEASE_SCRIPT = (
    "-- omni:quota_release:v2\n"
    + _QUOTA_COMMON
    + r"""
local fenced, _, current_epoch = ready_epoch(ARGV[1])
if fenced == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not fenced then return {'1', 'ok', '0', '0'} end
if not valid_hex(ARGV[2]) or not ARGV[3] or #ARGV[3] == 0 or #ARGV[3] > 263
  or not ARGV[4] or #ARGV[4] == 0 or #ARGV[4] > 255 or not valid_hex(ARGV[5])
  or not valid_safe_uint(ARGV[6]) or tonumber(ARGV[6]) < 61000
  or not valid_positive(ARGV[7]) or tonumber(ARGV[7]) > 100000
  or not valid_positive(ARGV[8]) or tonumber(ARGV[8]) > 100000 then
  return redis.error_reply('COORDINATION_CORRUPT')
end
local schema_status = quota_schema(current_epoch)
if schema_status == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if schema_status == 'reconciliation_required' then
  return {'1', 'reconciliation_required', '0', '0'}
end
local reservation_key = read_reservation_locator(KEYS[6])
local operation = read_operation_locator(KEYS[7])
if reservation_key == false or operation == false then return redis.error_reply('COORDINATION_CORRUPT') end
if reservation_key and reservation_key ~= ARGV[5] then return {'1', 'ok', '0', '0'} end
if operation and (operation.key ~= ARGV[5] or operation.fingerprint ~= ARGV[2]) then
  return {'1', 'ok', '0', '0'}
end
local clock = redis.call('TIME')
local now_ms = (clock[1] * 1000) + math.floor(clock[2] / 1000)
local now_second = math.floor(now_ms / 1000)
local plan = plan_prune_target(now_ms, ARGV[5], tonumber(ARGV[7]), tonumber(ARGV[8]))
if plan == nil then return redis.error_reply('COORDINATION_CORRUPT') end
if not plan then return {'1', 'reconciliation_required', '0', '0'} end
local replay_value, replay_score = redis.call('HGET', KEYS[4], ARGV[3]),
  redis.call('ZSCORE', KEYS[5], ARGV[3])
local replay = (replay_value or replay_score) and parse_replay(replay_value, replay_score) or nil
if (replay_value or replay_score) and not replay then return redis.error_reply('COORDINATION_CORRUPT') end
if replay and tonumber(replay.expiry) <= now_ms then replay = nil end
if operation and not replay then return redis.error_reply('COORDINATION_CORRUPT') end
if replay then
  apply_cleanup(plan)
  if replay.fingerprint ~= ARGV[2] or replay.kind ~= 'release' then
    return {'1', 'ok', '0', '0'}
  end
  return {'1', 'ok', '0', '1'}
end
local encoded, score = redis.call('HGET', KEYS[2], ARGV[4]),
  redis.call('ZSCORE', KEYS[3], ARGV[4])
local record = (encoded or score) and validate_record_pair(encoded, score, ARGV[5]) or nil
if (encoded or score) and not record then return redis.error_reply('COORDINATION_CORRUPT') end
record = record_after_planned_prune(record, now_ms)
if reservation_key and not record then return redis.error_reply('COORDINATION_CORRUPT') end
if plan.replay_count - #plan.replay_due >= tonumber(ARGV[8]) then
  return {'1', 'reconciliation_required', '0', '0'}
end
local released, expiry, window = false,
  record and record.retained_until_number or now_ms + tonumber(ARGV[6]), nil
if record and record.state == 'active' and record.active_until_number > now_ms then
  window = read_rate_window(now_second)
  if not window then return redis.error_reply('COORDINATION_CORRUPT') end
  local accepted_second = math.floor(record.accepted_at_number / 1000)
  if accepted_second >= now_second - RATE_WINDOW_SECONDS
    and not adjust_rate(window, accepted_second, 'subtract', '1',
      'subtract', record.estimated_tokens) then return redis.error_reply('COORDINATION_CORRUPT') end
  released, record.state, record.next_expiry = true, 'released', record.retained_until
end
local expiry_text = string.format('%.0f', expiry)
-- apply validated mutation
if schema_status == 'initialize' then
  redis.call('SET', KEYS[10], '2|' .. current_epoch .. '|ready')
end
apply_cleanup(plan)
if released then
  apply_rate(window)
  redis.call('HSET', KEYS[2], ARGV[4], encode_record(record))
  redis.call('ZADD', KEYS[3], expiry, ARGV[4])
end
local status = released and 'released' or 'not_released'
redis.call('HSET', KEYS[4], ARGV[3],
  encode_replay(ARGV[2], 'release', status, '', '0', expiry_text))
redis.call('ZADD', KEYS[5], expiry, ARGV[3])
redis.call('SET', KEYS[7], '2|' .. ARGV[5] .. '|' .. ARGV[2], 'PXAT', expiry)
return {'1', 'ok', released and '1' or '0', '0'}
"""
)


__all__ = ["QUOTA_COMMIT_SCRIPT", "QUOTA_RELEASE_SCRIPT", "QUOTA_RESERVE_SCRIPT"]

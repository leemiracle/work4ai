#!/bin/bash
# tinydb + tinycache 端到端测试
set -e
PASS=0; FAIL=0
ok()   { echo "  ✅ $1"; PASS=$((PASS+1)); }
fail() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }

echo "════════════════════════════════════════════"
echo "  tinydb + tinycache 测试"
echo "════════════════════════════════════════════"

# ─── tinydb 测试 ───
echo ""
echo "── tinydb: KV 存储引擎 ──"
DB="/tmp/tinydb_test.db"
rm -f $DB $DB.wal

# SET + GET
python3 /mnt/c/workspace/csdiy/projects/tinydb/main.py $DB set hello world
RESULT=$(python3 /mnt/c/workspace/csdiy/projects/tinydb/main.py $DB get hello)
if [ "$RESULT" = "world" ]; then ok "tinydb SET/GET"; else fail "SET/GET: got '$RESULT'"; fi

# 多 key
python3 /mnt/c/workspace/csdiy/projects/tinydb/main.py $DB set key2 value2
python3 /mnt/c/workspace/csdiy/projects/tinydb/main.py $DB set key3 "some long value here for testing"
RESULT=$(python3 /mnt/c/workspace/csdiy/projects/tinydb/main.py $DB get key2)
if [ "$RESULT" = "value2" ]; then ok "tinydb 多 key"; else fail "多 key"; fi

# UPDATE
python3 /mnt/c/workspace/csdiy/projects/tinydb/main.py $DB set hello updated
RESULT=$(python3 /mnt/c/workspace/csdiy/projects/tinydb/main.py $DB get hello)
if [ "$RESULT" = "updated" ]; then ok "tinydb UPDATE"; else fail "UPDATE: $RESULT"; fi

# DELETE
python3 /mnt/c/workspace/csdiy/projects/tinydb/main.py $DB delete key2
RESULT=$(python3 /mnt/c/workspace/csdiy/projects/tinydb/main.py $DB get key2)
if [ "$RESULT" = "(nil)" ]; then ok "tinydb DELETE"; else fail "DELETE"; fi

# STATS
echo ""
python3 /mnt/c/workspace/csdiy/projects/tinydb/main.py $DB stats

# HEXDUMP（参照 sqlite-btree 精读的验证方式）
echo ""
echo "  hexdump Page 1（参照 sqlite-btree 精读 §九）:"
python3 /mnt/c/workspace/csdiy/projects/tinydb/main.py $DB hexdump 1

# ─── tinycache 测试 ───
echo ""
echo ""
echo "── tinycache: 内存缓存服务器 ──"
python3 /mnt/c/workspace/csdiy/projects/tinycache/main.py -p 6390 &
CACHE_PID=$!
sleep 1

# 基础 SET/GET
RESP=$(printf '*3\r\n$3\r\nSET\r\n$5\r\nhello\r\n$5\r\nworld\r\n' | nc -w 2 localhost 6390)
if echo "$RESP" | grep -q "+OK"; then ok "tinycache SET (RESP)"; else fail "SET: $RESP"; fi

RESP=$(printf '*2\r\n$3\r\nGET\r\n$5\r\nhello\r\n' | nc -w 2 localhost 6390)
if echo "$RESP" | grep -q "world"; then ok "tinycache GET (RESP)"; else fail "GET: $RESP"; fi

# PING
RESP=$(printf '*1\r\n$4\r\nPING\r\n' | nc -w 2 localhost 6390)
if echo "$RESP" | grep -q "PONG"; then ok "tinycache PING"; else fail "PING"; fi

# DEL
printf '*2\r\n$3\r\nSET\r\n$5\r\ntest1\r\n$5\r\naaa\r\n' | nc -w 2 localhost 6390 > /dev/null
RESP=$(printf '*2\r\n$3\r\nDEL\r\n$5\r\ntest1\r\n' | nc -w 2 localhost 6390)
if echo "$RESP" | grep -q ":1"; then ok "tinycache DEL"; else fail "DEL: $RESP"; fi

# EXPIRE + TTL
printf '*3\r\n$3\r\nSET\r\n$4\r\ntmp1\r\n$3\r\nabc\r\n' | nc -w 2 localhost 6390 > /dev/null
RESP=$(printf '*3\r\n$6\r\nEXPIRE\r\n$4\r\ntmp1\r\n$1\r\n5\r\n' | nc -w 2 localhost 6390)
if echo "$RESP" | grep -q ":1"; then ok "tinycache EXPIRE"; else fail "EXPIRE: $RESP"; fi

RESP=$(printf '*2\r\n$3\r\nTTL\r\n$4\r\ntmp1\r\n' | nc -w 2 localhost 6390)
if echo "$RESP" | grep -q ":5"; then ok "tinycache TTL"; else fail "TTL: $RESP"; fi

# DBSIZE
RESP=$(printf '*1\r\n$6\r\nDBSIZE\r\n' | nc -w 2 localhost 6390)
echo "  DBSIZE: $RESP"

# KEYS
RESP=$(printf '*2\r\n$4\r\nKEYS\r\n$1\r\n*\r\n' | nc -w 2 localhost 6390)
if echo "$RESP" | grep -q "hello"; then ok "tinycache KEYS"; else fail "KEYS: $RESP"; fi

# INFO
RESP=$(printf '*1\r\n$4\r\nINFO\r\n' | nc -w 2 localhost 6390)
if echo "$RESP" | grep -q "redis_version"; then ok "tinycache INFO"; else fail "INFO"; fi

kill $CACHE_PID 2>/dev/null

# ─── 总结 ───
echo ""
echo "════════════════════════════════════════════"
echo "  测试结果: ✅ $PASS passed / ❌ $FAIL failed"
echo "════════════════════════════════════════════"

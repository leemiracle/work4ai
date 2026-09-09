#!/bin/bash
# tinyproxy 端到端测试脚本
# 验证：代理能正确转发 TCP 流量到后端
# 参照 frp test/e2e/ 的测试思路

set -e

echo "=== tinyproxy 端到端测试 ==="
echo ""

# 清理函数
cleanup() {
    echo ""
    echo "=== 清理 ==="
    kill $PROXY_PID $BACKEND_PID 2>/dev/null || true
}
trap cleanup EXIT

# 1. 启动后端 echo server（Python 单行）
echo "1. 启动后端 echo server (:8080)..."
python3 -c "
import socket, threading
def handle(c):
    data = c.recv(1024)
    c.sendall(b'echo: ' + data)
    c.close()
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 8080))
s.listen(5)
print('backend echo server on :8080')
while True:
    c,_ = s.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
" &
BACKEND_PID=$!
sleep 1

# 2. 启动代理
echo "2. 启动代理 (:9090 → :8080)..."
python3 /mnt/c/workspace/csdiy/projects/tinyproxy/main.py -l :9090 -b 127.0.0.1:8080 &
PROXY_PID=$!
sleep 1

# 3. 测试
echo "3. 测试转发..."
RESULT=$(echo "hello tinyproxy" | nc -w 2 localhost 9090)
echo "   发送: hello tinyproxy"
echo "   收到: $RESULT"

if echo "$RESULT" | grep -q "echo: hello tinyproxy"; then
    echo ""
    echo "   ✅ 测试通过！代理正确转发。"
else
    echo ""
    echo "   ❌ 测试失败！"
    exit 1
fi

# 4. 测试并发
echo ""
echo "4. 测试并发（5 个请求同时）..."
for i in $(seq 1 5); do
    echo "concurrent-$i" | nc -w 2 localhost 9090 &
done
wait
echo "   ✅ 并发测试完成"

echo ""
echo "=== 全部测试通过 ==="

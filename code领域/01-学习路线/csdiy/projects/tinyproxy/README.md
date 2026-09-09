# tinyproxy — 参照 frp 的 TCP 负载均衡代理

> **毕业项目**：不从零造玩具，参照 frp（87k star）+ gnet（9k star）的真实设计，造一个能用的 TCP 代理。
> 用 csdiy 的网络/redis 知识当脚手架，验证"真的会了"。

## 参照的真实项目

| 项目 | 参照什么 | csdiy 对应 |
|------|---------|-----------|
| **frp** (fatedier/frp, 87k⭐) | Proxy 接口+Factory、连接桥接、连接池、指数退避 | network-程序员视角、redis-eventloop |
| **gnet** (panjf2000/gnet, 9k⭐) | Go 版 epoll 事件循环、Reactor 模式 | redis-eventloop（ae.c 的 Go 版） |
| **HAProxy** | 负载均衡算法（轮询/最少连接/加权） | — |

## 从 frp 提取的核心设计模式

```
frp 的 TCP 代理核心链路 (server/proxy/proxy.go):

  startCommonTCPListenersHandler()
    │ for { Accept → go handleUserTCPConnection() }
    │ 临时错误: 指数退避 5ms→1s
    ↓
  handleUserTCPConnection(userConn)
    │ 1. 从连接池获取 workConn (GetWorkConnFromPool)
    │ 2. 可选: 加密 / 压缩 / 限流 (装饰器模式)
    │ 3. metrics.Server.OpenConnection()
    ↓
  joinUserConnection(local, userConn)
    │ libio.Join → 两个 goroutine 双向 io.Copy
    │ user → backend | backend → user
    ↓
  连接关闭 → metrics.CloseConnection + AddTraffic
```

## 项目目标

| Phase | 目标 | 参照 | 验证 |
|-------|------|------|------|
| ✅ P1 | TCP 转发代理（单后端） | frp handleUserTCPConnection | nc 通过代理 echo |
| ⬜ P2 | 负载均衡（多后端轮询） | HAProxy roundrobin | 请求分散到多后端 |
| ⬜ P3 | 健康检查 + 故障转移 | frp health.Check | 杀一个后端，自动切换 |
| ⬜ P4 | 连接池 + 指数退避 | frp GetWorkConnFromPool | 高并发压测 |
| ⬜ P5 | Prometheus metrics | frp metrics | /metrics 端点 |
| ⬜ P6 | 优雅退出 + 信号处理 | frp signal.Close | SIGTERM 不丢连接 |

## 用法（Phase 1）

```bash
# 启动代理（将 :9090 的流量转发到 127.0.0.1:8080）
python3 main.py -l :9090 -b 127.0.0.1:8080

# 另一个终端：启动后端 echo server
python3 -c "
import socket
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 8080))
s.listen()
while True:
    c,_ = s.accept()
    data = c.recv(1024)
    c.sendall(b'echo: ' + data)
    c.close()
"

# 第三个终端：通过代理发送
echo hello | nc localhost 9090
# 预期输出: echo: hello
```

## 技术栈

- **Python 3.10+ asyncio**（Go 未安装时的替代；后续可用 Go 重写）
- **零第三方依赖**（只用标准库，和 frp 的 philosoph 一致）

## 和 csdiy 知识的交叉验证

读完这个项目的代码后，你应该能回答：

1. `network-程序员视角 §二`：为什么 asyncio 用 epoll 比 select 快？（→ 看 Python asyncio 源码）
2. `redis-eventloop §四`：frp 的 Accept 循环和 Redis 的 aeMain 有什么共同结构？（→ 都是 `for { wait → dispatch }`）
3. `network-程序员视角 §四`：代理的 CLOSE_WAIT 怎么来的？（→ 谁负责 close？）
4. `csapp-程序员视角 Ch9`：代理的内存怎么管理？（→ asyncio buffer）

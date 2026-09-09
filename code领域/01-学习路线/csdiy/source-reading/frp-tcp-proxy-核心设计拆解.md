# frp TCP 代理核心设计拆解

> 精读 `fatedier/frp` 的 `server/proxy/proxy.go`（500 行核心）+ `server/proxy/tcp.go`。
> 目标：理解一个 87k star 的 TCP 代理是怎么设计的，把每个设计模式钉死在 csdiy 的知识上。
>
> 配套实证：本文每个设计模式都能在 `projects/tinyproxy/main.py` 里找到对应的 Python 实现。

---

## 一、frp 是什么 + 架构全景

frp 是一个**反向代理**（内网穿透）：把内网服务暴露到公网。

```
用户 ──TCP──→ frps(公网) ←──控制连接──→ frpc(内网) ──→ 本地服务
                    ↓ new user conn
                    └──通知 frpc──→ frpc 建新连接(work conn) ──→ frps
                                                                       ↓
                frps 桥接 user conn ↔ work conn ──────────────────────┘
```

**关键区别**：
- 传统代理（HAProxy/nginx）：client → proxy → server（正向）
- frp：user → frps ↔ frpc → server（反向，frpc 主动连 frps）

本文聚焦 **frps 端的 TCP 代理核心**——从 Accept 到桥接。

---

## 二、Proxy 接口 + Factory 注册（设计模式之魂）

### 代码（`server/proxy/proxy.go`）

```go
// 接口定义
type Proxy interface {
    Run() (remoteAddr string, err error)
    GetName() string
    GetConfigurer() v1.ProxyConfigurer
    Close()
    // ... 9 个方法
}

// Factory 注册表（全局 map）
var proxyFactoryRegistry = map[reflect.Type]func(*BaseProxy] Proxy{}

func RegisterProxyFactory(proxyConfType reflect.Type, factory func(*BaseProxy) Proxy) {
    proxyFactoryRegistry[proxyConfType] = factory
}
```

```go
// tcp.go 的注册（init 时自动执行）
func init() {
    RegisterProxyFactory(reflect.TypeFor[*v1.TCPProxyConfig](), NewTCPProxy)
}
```

### 设计分析

**为什么用接口 + Factory**：
- frp 支持 TCP/HTTP/HTTPS/STCP/SUDP/XTCP 6 种代理类型
- 每种类型的 `Run()` 不同（TCP 监听端口，HTTP 监听 vhost）
- 但通用逻辑（Accept、桥接、close）相同 → 放 `BaseProxy`

**对比 csdiy 知识**：
- 这就是 `patterns-程序员视角.md` 的**工厂模式 + 模板方法**
- GoF 的"工厂"被 Go 的 reflect + init 优雅实现——没有工厂类的繁文缛节
- **红线提醒**（参照 patterns §5）：如果你的代理只有一种类型，别上 Factory——直接写

---

## 三、startCommonTCPListenersHandler（Accept 循环 + 指数退避）

### 代码（`proxy.go` L263-296）

```go
func (pxy *BaseProxy) startCommonTCPListenersHandler() {
    for _, listener := range pxy.listeners {
        go func(l net.Listener) {
            var tempDelay time.Duration  // ← 指数退避计数器

            for {
                c, err := l.Accept()    // ← 阻塞等连接
                if err != nil {
                    // 临时错误（端口耗尽、fd 上限）→ 指数退避重试
                    if err, ok := err.(interface{ Temporary() bool }); ok && err.Temporary() {
                        if tempDelay == 0 {
                            tempDelay = 5 * time.Millisecond
                        } else {
                            tempDelay *= 2   // ← 5ms → 10ms → 20ms → ...
                        }
                        if tempDelay > 1 * time.Second {
                            tempDelay = 1 * time.Second  // ← 上限 1s
                        }
                        time.Sleep(tempDelay)
                        continue
                    }
                    // 非临时错误（listener 关闭）→ 退出
                    return
                }
                go pxy.handleUserTCPConnection(c)  // ← 每连接一个 goroutine
            }
        }(listener)
    }
}
```

### 设计分析

**这是 Go 网络编程的标准 Accept 循环**——和 Redis 的 `aeMain` 同构：

| Redis ae.c | frp proxy.go | 本质 |
|-----------|-------------|------|
| `aeMain()` 的 `while(!stop)` | `for { Accept }` | 永不返回的事件循环 |
| `aeProcessEvents()` | `l.Accept()` | 阻塞等事件 |
| `aeCreateFileEvent(client_fd, readHandler)` | `go handleUserTCPConnection(c)` | 每事件一个 handler |
| 无（单线程串行） | `go` 关键字 | Go 的并发优势 |

**指数退避的工程智慧**：
- Accept 偶尔会返回临时错误（`EMFILE` fd 耗尽、`ENOMEM`）
- 如果立刻重试 → 空转烧 CPU
- 如果退出 → 服务中断
- 指数退避 → 给系统恢复时间，同时不过度延迟
- **上限 1s** → 避免退避太久（参照 `csapp Ch5` 的优化原则：先量后改）

**对比 tinyproxy 的实现**：
Python 的 `asyncio.start_server` 把 Accept 循环封装在内部了。你不需要手写指数退避——asyncio 帮你做了。但**理解 frp 的原始实现**，让你知道 asyncio 底层在干什么。

---

## 四、handleUserTCPConnection（核心处理链路）

### 代码（`proxy.go` L298-345，精简）

```go
func (pxy *BaseProxy) handleUserTCPConnection(userConn net.Conn) {
    defer userConn.Close()

    // 1. 从连接池获取 work connection（frpc 预创建的）
    workConn, err := pxy.GetWorkConnFromPool(
        userConn.RemoteAddr(), userConn.LocalAddr())
    if err != nil { return }
    defer workConn.Close()

    // 2. 装饰器链（可选）：加密 / 压缩 / 限流
    var local io.ReadWriteCloser = workConn
    if cfg.Transport.UseEncryption {
        local, _ = libio.WithEncryption(local, pxy.encryptionKey)
    }
    if cfg.Transport.UseCompression {
        local, _ = libio.WithCompressionFromPool(local)
    }
    if pxy.GetLimiter() != nil {
        local = libio.WrapReadWriteCloser(
            limit.NewReader(local, pxy.GetLimiter()),
            limit.NewWriter(local, pxy.GetLimiter()),
            local.Close)
    }

    // 3. metrics 记录
    metrics.Server.OpenConnection(name, proxyType)

    // 4. 双向桥接（核心！）
    inCount, outCount, _ := pxy.joinUserConnection(local, userConn)

    // 5. metrics 更新
    metrics.Server.CloseConnection(name, proxyType)
    metrics.Server.AddTrafficIn(name, proxyType, inCount)
    metrics.Server.AddTrafficOut(name, proxyType, outCount)
}
```

### 设计分析

**三个层次清晰分离**：
1. **连接获取**：GetWorkConnFromPool（和 frpc 通信）
2. **装饰器链**：加密/压缩/限流（参照 `patterns §3 装饰器`）
3. **数据桥接**：joinUserConnection（纯 IO）

**装饰器链是经典的 Go 语言惯用法**：
```go
var local io.ReadWriteCloser = workConn  // 原始连接
local = libio.WithEncryption(local)     // 包一层加密
local = libio.WithCompression(local)    // 再包一层压缩
local = limit.Wrap(local, limiter)      // 再包一层限流
```
每一层都实现 `io.ReadWriteCloser`，层层嵌套——**和 Python 的 io.BufferedReader(io.FileIO()) 完全同构**。

**对比 csdiy 知识**：
- `patterns §3 装饰器`：这就是装饰器模式的 Go 版
- `csapp Ch10`：装饰器 = 多层 file descriptor 包装
- `code-review §3`：错误处理——每一步都有 `if err != nil`

---

## 五、joinUserConnection（双向桥接 = libio.Join）

### 代码（`proxy.go` L347-360）

```go
func (pxy *BaseProxy) joinUserConnection(
    local io.ReadWriteCloser, userConn net.Conn, ...
) (int64, int64, []error) {
    // ... 特殊协议处理（SUDP）省略 ...
    return libio.Join(local, userConn)
}
```

`libio.Join` 的本质（`github.com/fatedier/golib/io`）：

```go
// 等价于：
func Join(dst1, dst2 io.ReadWriteCloser) (int64, int64, error) {
    var wg sync.WaitGroup
    wg.Add(2)

    var inCount, outCount int64

    // 方向 1：dst1 → dst2（user → backend）
    go func() {
        defer wg.Done()
        inCount, _ = io.Copy(dst1, dst2)
        dst1.Close()  // 一个方向结束 → 关闭另一个方向
    }()

    // 方向 2：dst2 → dst1（backend → user）
    go func() {
        defer wg.Done()
        outCount, _ = io.Copy(dst2, dst1)
        dst2.Close()
    }()

    wg.Wait()
    return inCount, outCount, nil
}
```

### 设计分析

**这是 TCP 代理的灵魂——一句话概括**：
> 两个 `io.Copy` 背靠背，一个读 user 写 backend，一个读 backend 写 user。

**关键细节**：
1. **64KB buffer**：`io.Copy` 默认用 32KB buffer，可以调到 64KB 减少 syscall 次数（参照 `csapp Ch10` 的 read/write 短读写）
2. **半关闭**：一个方向结束 → Close 另一个方向（让对方的 read 返回 EOF）
3. **WaitGroup**：等两个方向都结束才返回（否则连接泄漏）

**对比 tinyproxy 的实现**：
```python
# tinyproxy/main.py 的 join_connections
async def forward(src, dst, direction):
    while True:
        data = await src.read(65536)  # ← 64KB，和 frp 一致
        if not data: break
        dst.write(data)
        await dst.drain()

await asyncio.gather(
    forward(client_r, backend_w, "→"),  # ← 方向 1
    forward(backend_r, client_w, "←"),  # ← 方向 2
)
```
**完全同构**——Go 的 goroutine + io.Copy = Python 的 asyncio + gather。

**对比 csdiy 知识**：
- `network §三`：TCP 是字节流——io.Copy 不管"包"，只搬字节
- `network §四`：CLOSE_WAIT 怎么来的——一方 close 了，另一方没 close
- `csapp Ch10`：read/write 的返回值可能短——io.Copy 内部循环

---

## 六、GetWorkConnFromPool（连接池）

### 代码（`proxy.go` L145-180，精简）

```go
func (pxy *BaseProxy) GetWorkConnFromPool(src, dst net.Addr) (net.Conn, error) {
    for i := 0; i < pxy.poolCount+1; i++ {  // ← 重试 poolCount+1 次
        pxyWorkConn, err := pxy.getWorkConnFn()  // ← 从 frpc 获取
        if err != nil {
            continue  // ← 失败重试
        }

        workConn, err = pxyWorkConn.Start(&msg.StartWorkConn{
            ProxyName: pxy.GetName(),
            SrcAddr:   srcAddr,
            DstAddr:   dstAddr,
        })
        if err != nil {
            pxyWorkConn.Close()
            workConn = nil
            continue  // ← 失败重试
        }
        break  // ← 成功退出
    }
    return workConn, err
}
```

### 设计分析

**连接池的工程价值**：
- frpc 预创建 `poolCount` 个 work connection
- 用户请求来了 → frps 直接从池里取一个，不用等 frpc 新建
- **降低首次响应延迟**（参照 `csapp Ch6` 的 cache 原理）

**重试逻辑**：
- 最多 `poolCount+1` 次——池里全取完了还能试一次新的
- 失败的连接 Close（防泄漏）
- 全失败才返回错误

**对比 csdiy 知识**：
- `patterns §7 享元/对象池`：连接池 = 对象池的变体
- `db §五 连接池`：数据库连接池同理——预热 vs 懒创建
- `csapp Ch6`：cache 的本质——贵的操作预做

---

## 七、设计模式总结

| 模式 | frp 代码 | csdiy 对应章节 | tinyproxy 实现 |
|------|---------|---------------|---------------|
| **接口+Factory** | Proxy interface + RegisterProxyFactory | patterns §5 工厂 | TinyProxy 类 |
| **模板方法** | BaseProxy 的通用逻辑 + 子类 Run() | patterns §8 模板方法 | TinyProxy.__init__ |
| **装饰器链** | WithEncryption → WithCompression → Limit | patterns §3 装饰器 | （Phase 2 待加） |
| **对象池** | GetWorkConnFromPool | patterns §7 享元 | BackendManager（简化版） |
| **指数退避** | Accept 临时错误的 tempDelay | csapp Ch5 优化 | asyncio 内部处理 |
| **双向桥接** | libio.Join = 2× io.Copy | network §三 字节流 | join_connections |
| **metrics** | OpenConnection/CloseConnection/AddTraffic | perf §1 工具箱 | active_conns/total_conns |
| **优雅退出** | signal handler → listener.Close() | os §三 进程状态 | signal handler → stop_event |

---

## 八、和 csdiy 知识的交叉验证

读完这篇 + tinyproxy 代码后，你应该能回答：

### 从 bug 反推（network 视角）
1. **代理的 CLOSE_WAIT 堆积**：如果 backend 先关闭，user 没关闭 → 你在 `forward()` 的 finally 里 Close 了吗？
2. **代理的粘包**：TCP 代理不管"包"——它只搬字节。粘包是应用层的问题。
3. **代理的 RST**：如果 backend 连接被拒，proxy 该怎么处理？（tinyproxy 的 `except ConnectionRefusedError`）

### 从性能反推（perf 视角）
4. **代理的吞吐瓶颈**：不是 CPU，是 syscall 次数。64KB buffer 比 4KB 快 16 倍。
5. **goroutine 泄漏**：每个连接 2 个 goroutine。如果 join 没正确 Wait → goroutine 泄漏。

### 从架构反推（csapp 视角）
6. **fd 上限**：每个代理连接占 2 个 fd（user + backend）。`ulimit -n` 够吗？
7. **内存**：64KB buffer × 1000 连接 = 64MB。可接受吗？

---

## 九、一句话总结

> frp 的 TCP 代理核心 = `Proxy 接口(Factory 注册)` + `Accept 循环(指数退避)` + `连接池(GetWorkConn)` + `装饰器链(加密/压缩/限流)` + `双向 io.Copy(libio.Join)` + `metrics 记录`。
>
> 整个 server/proxy/proxy.go 500 行，没有一个多余的抽象。读懂它，你就理解了所有 TCP 代理的本质——nginx、HAProxy、Envoy 的核心链路都是这个骨架的变体。

---

*配套项目：`projects/tinyproxy/main.py`（Python 实现版）*
*参照上游：`fatedier/frp` master 分支 `server/proxy/proxy.go`*

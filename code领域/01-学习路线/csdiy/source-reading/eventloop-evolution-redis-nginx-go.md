# 事件循环演化史：Redis ae.c → nginx worker → Go netpoller

> 三种世界级事件循环实现的对照精读。
> 揭示一个本质：**所有事件循环都是 `for { epoll_wait → dispatch → repeat }` 的变体**。
>
> 配套：[redis-eventloop-逐行拆解.md](redis-eventloop-逐行拆解.md) | [frp-tcp-proxy-核心设计拆解.md](frp-tcp-proxy-核心设计拆解.md)
> csdiy 对应：network §二(epoll) + os §六(IO模型) + csapp Ch10(系统级IO)

---

## 一、为什么写这篇

csdiy 已有 [redis-eventloop 逐行拆解](redis-eventloop-逐行拆解.md)（691 行），把 Redis 的 `ae.c` 从 `main()` 到 `aeMain()` 到 `epoll_wait` 全链路讲透了。

但 Redis 只是事件循环的**一种实现**。真实的工程世界里，还有两个重量级选手：

| 实现 | 代表项目 | 模型 | 并发策略 |
|------|---------|------|---------|
| Redis ae.c | Redis | 单线程 Reactor | 串行执行所有命令 |
| nginx worker | nginx | 多进程 Reactor | 每进程一个事件循环 |
| Go netpoller | Go runtime | M:N 调度 + 非阻塞 IO | goroutine per connection |

读完这篇，你会理解：**为什么 Redis 单线程够快、nginx 为什么多进程而不是多线程、Go 为什么不需要手写事件循环**。

---

## 二、Redis ae.c 摘要（详见 [专文](redis-eventloop-逐行拆解.md)）

### 核心结构

```c
// ae.h
typedef struct aeEventLoop {
    int maxfd;                // 最大 fd（select 需要）
    int setsize;              // events[] 数组大小
    aeFileEvent *events;      // fd → 回调表（读/写回调）
    aeFiredEvent *fired;      // epoll_wait 返回的就绪事件
    aeTimeEvent *timeEventHead; // 定时事件链表
    int stop;
    aeBeforeSleep *beforesleep; // 钩子：每圈阻塞前
    aeAfterSleep *aftersleep;   // 钩子：阻塞后
} aeEventLoop;
```

### 核心循环

```c
// ae.c
void aeMain(aeEventLoop *eventLoop) {
    while (!eventLoop->stop) {
        aeProcessEvents(eventLoop, AE_ALL_EVENTS|AE_CALL_BEFORE_SLEEP|AE_CALL_AFTER_SLEEP);
    }
}

int aeProcessEvents(aeEventLoop *eventLoop, int flags) {
    // ① 计算最近定时事件的超时
    shortest = aeSearchNearestTimer();
    // ② beforesleep 钩子（刷 AOF、聚合待写客户端）
    eventLoop->beforesleep(eventLoop);
    // ③ epoll_wait（阻塞直到有事件或超时）
    numevents = aeApiPoll(eventLoop, tvp);
    // ④ aftersleep 钩子
    eventLoop->aftersleep(eventLoop);
    // ⑤ 分发：对每个就绪 fd 调用读/写回调
    for (j = 0; j < numevents; j++) {
        aeFileEvent *fe = &eventLoop->events[eventLoop->fired[j].fd];
        if (fe->mask & AE_READABLE) fe->rfileProc(...);
        if (fe->mask & AE_WRITABLE) fe->wfileProc(...);
    }
    // ⑥ 处理定时事件
    processed += processTimeEvents(eventLoop);
}
```

### 一句话总结

> Redis = `while(1) { epoll_wait → 逐个调用 fd 回调 → 处理定时器 }`
>
> **没有锁、没有线程切换、没有并发竞争**。所有命令在同一个线程串行执行。

---

## 三、nginx worker：多进程 Reactor

### 为什么不单线程

Redis 单线程能扛 10 万 QPS，因为每条命令是 O(1) 内存操作。但 nginx 要做：

1. **HTTP 解析**（CPU 密集，不是 O(1)）
2. **TLS 握手**（CPU 极重）
3. **gzip 压缩**（CPU 极重）
4. ** upstream 转发**（网络等待）

如果 nginx 用单线程，一个慢请求会阻塞所有连接。所以 nginx 用**多进程**。

### 架构

```
nginx master
  ├── worker process 1  (epoll 事件循环)
  ├── worker process 2  (epoll 事件循环)
  ├── worker process 3  (epoll 事件循环)
  └── worker process N  (epoll 事件循环)  N = CPU 核数
```

每个 worker 是一个**独立的单线程事件循环**——和 Redis 的 aeMain 完全同构。

### 核心循环（`ngx_process_cycle.c`）

```c
// 简化版 nginx worker 循环
void ngx_worker_process_cycle(ngx_cycle_t *cycle) {
    // 初始化
    ngx_worker_process_init(cycle);

    // 每个 worker 自己的 epoll
    ngx_event_actions = ngx_epoll_module_ctx.actions;

    // 主循环（和 Redis aeMain 同构！）
    for (;;) {
        // ① 计算超时
        ngx_event_expire_timers();

        // ② epoll_wait（等事件）
        ngx_process_events_and_timers(cycle);
        //   内部调 epoll_wait → 对每个就绪 fd 调 handler

        // ③ 信号处理
        if (ngx_terminate) break;
        if (ngx_quit) ngx_close_listening_sockets(cycle);
    }
}
```

### 关键设计：惊群问题

多个 worker 同时 `epoll_wait` 同一个监听 fd → 新连接到达 → 所有 worker 被唤醒 → 只有一个能 accept → 其余白醒。

nginx 的解决方案：
- **ngx_accept_mutex**：worker 轮流获取"accept 锁"，只有持锁的 worker 才在监听 fd 上注册读事件
- 获取锁的 worker：注册 accept 事件 + 已有连接的读写事件
- 未获取锁的 worker：只处理已有连接的读写事件

这保证了**同一时刻只有一个 worker 会 accept 新连接**，避免惊群。

### 和 Redis 的对比

| 维度 | Redis ae.c | nginx worker |
|------|-----------|-------------|
| 进程/线程数 | 1 | N（=CPU核数） |
| 事件循环数 | 1 | N（每进程一个） |
| epoll 实例 | 1 | N |
| 共享状态 | 不需要（单线程） | 不需要（进程隔离） |
|惊群问题 | 不存在 | 存在（用 accept_mutex 解决） |
| 适用场景 | O(1) 命令 | CPU 密集（TLS/gzip） |

### 一句话总结

> nginx = N 个 Redis aeMain 并行，每个进程独立处理自己的连接，互不干扰。
>
> **多进程而非多线程**——因为进程隔离免锁、共享内存用 mmap 精确控制、崩溃不影响其他 worker。

---

## 四、Go netpoller：M:N 调度 + 非阻塞 IO

### 革命性在哪

Redis 手写 `for { epoll_wait → dispatch }`，nginx 也手写。Go 说：**程序员不该手写事件循环**。

Go 的方案：
1. 所有 `net.Conn.Read()` / `Write()` **自动设为非阻塞**
2. 非阻塞 IO 返回 `EAGAIN` 时，Go runtime **自动挂起当前 goroutine**
3. runtime 的后台线程做 `epoll_wait`，fd 就绪后**自动唤醒对应的 goroutine**
4. 程序员写的是**同步阻塞式代码**，runtime 帮你做异步

### 架构

```
Go Runtime
  ├── netpoller（1 个后台线程，epoll_wait）
  ├── GMP 调度器
  │   ├── G1: conn.Read()  ← 挂起（fd 未就绪）
  │   ├── G2: conn.Read()  ← 挂起
  │   ├── G3: handle()     ← 运行中
  │   └── ...（百万 goroutine）
  ├── M1: OS 线程（执行 G3）
  ├── M2: OS 线程（执行就绪的 G）
  └── M3: OS 线程（执行就绪的 G）
```

### 核心代码（Go runtime `netpoll_epoll.go`）

```go
// Go runtime 内部（程序员看不到，但原理和 Redis ae.c 同构）

func netpoll(delay int64) gList {
    // epoll_wait（和 Redis aeApiPoll 完全一样！）
    var events [128]epollevent
retry:
    n := epollwait(epfd, &events[0], int32(len(events)), waitms)
    if n < 0 { ... }

    var toRun gList
    for i := int32(0); i < n; i++ {
        ev := &events[i]
        // 从 epoll 事件取出 fd → 找到对应的 goroutine（pd）
        pd := *(**pollDesc)(unsafe.Pointer(&ev.data))
        if ev.events&(_EPOLLIN|_EPOLLRDHUP|_EPOLLHUP|_EPOLLERR) != 0 {
            // fd 可读 → 唤醒等待 Read 的 goroutine
            rg := pd.rg
            if rg != 0 { rg.setReady() }
        }
        if ev.events&_EPOLLOUT != 0 {
            // fd 可写 → 唤醒等待 Write 的 goroutine
            wg := pd.wg
            if wg != 0 { wg.setReady() }
        }
    }
    return toRun  // 返回所有就绪的 goroutine 列表
}
```

**看出来了？这和 Redis ae.c 的 `aeProcessEvents` 完全同构！**

```
Redis aeProcessEvents          Go netpoll
─────────────────────────────────────────────
aeApiPoll(epoll_wait)    ←→    epollwait
events[fd].rfileProc     ←→    pd.rg.setReady（唤醒 goroutine）
events[fd].wfileProc     ←→    pd.wg.setReady
processTimeEvents        ←→    timer goroutine
```

**唯一的区别**：Redis 直接调用回调函数，Go 唤醒 goroutine 让 GMP 调度器在合适的 OS 线程上执行。

### 程序员视角

```go
// Go 程序员写的代码（看起来是"阻塞"的）
func handleConn(conn net.Conn) {
    buf := make([]byte, 1024)
    n, err := conn.Read(buf)  // ← 这里"阻塞"
    // 但实际上：runtime 把 fd 注册到 netpoller → 挂起 goroutine → 线程释放给其他 G
    // fd 就绪后 → netpoller 唤醒这个 goroutine → Read 返回
    conn.Write(buf[:n])
    conn.Close()
}

func main() {
    ln, _ := net.Listen("tcp", ":8080")
    for {
        conn, _ := ln.Accept()
        go handleConn(conn)  // ← 每连接一个 goroutine
    }
}
```

**没有 `epoll_wait`、没有回调表、没有事件循环。** 程序员写的是最朴素的"每连接一个线程"模型，runtime 帮你做事件循环。

### 和 Redis/nginx 的对比

| 维度 | Redis ae.c | nginx worker | Go netpoller |
|------|-----------|-------------|-------------|
| 事件循环 | 程序员手写 | 程序员手写 | **runtime 自动** |
| 编程模型 | 回调 | 回调 | **同步阻塞** |
| 并发单位 | 无（单线程） | 进程 | **goroutine** |
| 并发数 | 1 | ~CPU核数 | **百万 goroutine** |
| 程序员心智负担 | 高（手管 fd） | 高（手管 fd+惊群） | **低（像写同步代码）** |
| epoll 实例 | 1 | N | 1（runtime 全局） |
| 适用场景 | O(1) 命令 | CPU 密集 | **通用** |

---

## 五、三者共同的本质

剥开所有差异，三种实现的**内核是同一个**：

```c
// 所有事件循环的本质（伪代码）
while (!stop) {
    // ① 等待事件（epoll_wait / kqueue / IOCP）
    events = poll(fds, timeout);

    // ② 分发：对每个就绪 fd 执行 handler
    for (event in events) {
        handler = callback_table[event.fd];
        handler(event);  // Redis: 直接调用  nginx: 直接调用  Go: 唤醒 goroutine
    }

    // ③ 定时任务
    run_expired_timers();
}
```

| 步骤 | Redis | nginx | Go |
|------|-------|-------|-----|
| ① poll | aeApiPoll | ngx_epoll_process_events | runtime.netpoll |
| ② dispatch | fe->rfileProc() | ev->handler() | pd.setReady() → GMP 调度 |
| ③ timers | processTimeEvents | ngx_event_expire_timers | timer 堆 |

**差异只在 dispatch 的方式**：
- Redis/nginx：直接调用回调函数（同步、串行）
- Go：唤醒 goroutine（异步、可并行，由 GMP 调度器决定在哪个 OS 线程执行）

---

## 六、tinyproxy/tinycache/tinyhttpd 在哪里？

csdiy 的 3 个毕业项目用的 **Python asyncio**，本质上也是事件循环：

```python
# Python asyncio 的核心（和 Redis/Go 同构）
# asyncio.BaseEventLoop._run_once()

while True:
    # ① poll（epoll_wait，和 Redis/Go 一样）
    event_list = self._selector.select(timeout)

    # ② dispatch
    self._process_events(event_list)
    #   → 对每个就绪 fd，找到对应的 callback 并调用

    # ③ 定时任务
    nconsumed = self._run_once_timers()
```

| 实现 | poll | dispatch | 并发模型 |
|------|------|---------|---------|
| Redis ae.c | epoll_wait | 回调函数 | 单线程串行 |
| nginx worker | epoll_wait | 回调函数 | 多进程并行 |
| Go netpoller | epoll_wait | 唤醒 goroutine | M:N 调度 |
| **Python asyncio** | **epoll_wait** | **回调/coroutine** | **单线程协程** |

**Python asyncio 的位置**：
- 和 Redis 一样是**单线程**（没有并行）
- 和 Go 一样用 **coroutine**（看起来是同步代码）
- 但**不需要 runtime**（程序员显式用 `async/await`）

---

## 七、和 csdiy 知识的交叉验证

### network-程序员视角 §二（epoll vs select）

> "为什么 epoll 比 select 快？"

答案在这篇精读里：
- epoll_wait 是 O(就绪 fd 数)，不是 O(总 fd 数)
- Redis/nginx/Go/Python **都选了 epoll**，没有一个用 select
- **这就是 epoll 的胜利**——所有世界级项目都站在它上面

### os-程序员视角 §六（IO 模型）

> "阻塞 vs 非阻塞 vs 异步 IO"

四种事件循环用了**同一个答案**：
- fd 设为非阻塞
- 用 epoll_wait 等"哪些 fd 就绪了"
- **不是等"一个 fd 就绪"**（阻塞 IO），而是等"N 个 fd 中的任意一个"

### csapp Ch10（系统级 I/O）

> "read/write 的短读写问题"

Redis 的回答：`aeCreateFileEvent(fd, AE_WRITABLE, ...)` —— 如果 write 没写完，注册写事件，等 epoll 告诉你"现在能写了"再继续。这就是非阻塞 IO 的标准做法。

### redis-eventloop §七（为什么单线程够）

> "为什么 Redis 单线程能扛 10 万 QPS？"

这篇精读的回答：**因为瓶颈在 IO 不在 CPU**。epoll_wait 让"等 N 个客户端"和"等 1 个"一样便宜。如果 CPU 成为瓶颈（TLS/gzip），就用 nginx 的多进程或 Go 的多 goroutine。

---

## 八、选择指南

| 你的场景 | 推荐模型 | 参照项目 |
|---------|---------|---------|
| O(1) 内存操作（缓存/计数器） | 单线程 Reactor | Redis |
| CPU 密集（HTTP/TLS/gzip） | 多进程 Reactor | nginx |
| 通用网络服务 | M:N 调度 | Go / Python asyncio |
| 百万连接 | M:N + 连接限流 | Go（goroutine 轻量） |
| 极低延迟 | 多线程 Reactor（共享内存） | Envoy / gnet |

---

## 九、一句话总结

> 事件循环的本质是 `for { epoll_wait → dispatch → timers }`。
>
> Redis 用单线程串行 dispatch（简单免锁）、nginx 用多进程并行 dispatch（CPU 密集型）、Go 用 M:N 调度 dispatch（程序员不感知）。
>
> 但**底层的 epoll_wait 完全一样**。理解了这一行 `epoll_wait`，你就理解了所有高性能网络服务器的核心。

---

*配套：[redis-eventloop-逐行拆解.md](redis-eventloop-逐行拆解.md) | [frp-tcp-proxy-核心设计拆解.md](frp-tcp-proxy-核心设计拆解.md)*
*参照项目：[tinyproxy](projects/tinyproxy/) | [tinycache](projects/tinycache/) | [tinyhttpd](projects/tinyhttpd/)*

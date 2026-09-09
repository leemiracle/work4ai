# Go GMP 调度器精读：M:N 调度的工程艺术

> Go 不需要手写事件循环——GMP 调度器把"同步阻塞代码"变成了"异步执行"。
>
> 配套：[eventloop-evolution-redis-nginx-go.md](eventloop-evolution-redis-nginx-go.md)
> csdiy 对应：os §五(并发) + network §二(epoll) + patterns §9(状态机)

---

## 一、问题：如何让百万 goroutine 高效运行

Redis 用单线程事件循环（简单但无并行）。nginx 用多进程（并行但开销大）。

Go 的目标：**让程序员写"每连接一个 goroutine"的同步代码，runtime 帮你实现事件循环的效率 + 多核并行**。

```
Go 程序员写的代码：
  go handleConn(conn)   // 看起来创建了百万"线程"

实际运行：
  runtime 在 N 个 OS 线程上调度这些 goroutine
  IO 阻塞时自动挂起（netpoller）
  就绪后自动恢复
```

---

## 二、GMP 三元组

```
┌──────────────────────────────────────────────────────┐
│                    Go Runtime                         │
│                                                      │
│  G1   G2   G3   G4   G5   ...   G1000000  (goroutine)│
│   │    │    │                                      │
│   ↓    ↓    ↓         (绑定到本地队列)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ P1  LRQ  │  │ P2  LRQ  │  │ P3  LRQ  │ (处理器)  │
│  │ [G1,G2]  │  │ [G3,G4]  │  │ [G5,G6]  │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│       │              │              │                 │
│       ↓              ↓              ↓                 │
│     M1(线程)       M2(线程)       M3(线程)           │
│       │              │              │                 │
│    epoll_wait     执行 G3       执行 G5              │
│                                                      │
│              ┌──────────┐                            │
│              │ GRQ      │ (全局运行队列)              │
│              │ [G7,G8]  │                            │
│              └──────────┘                            │
└──────────────────────────────────────────────────────┘
```

### G — Goroutine

```go
// 参照 runtime/runtime2.go
type g struct {
    stack       stackDesc    // 栈（初始 2KB，可增长）
    status      uint32       // _Gidle/_Grunnable/_Grunning/_Gwaiting/_Gsyscall
    m           *m           // 当前绑定的 M
    sched       gobuf        // 保存的寄存器（用于上下文切换）
    // ...
}
```

Goroutine 的栈只有 **2KB**（OS 线程默认 8MB）→ 百万 goroutine 只需 2GB（vs 线程需 8TB）。

### M — Machine（OS 线程）

```go
type m struct {
    g0          *g           // 调度专用 goroutine（栈较大）
    curg        *g           // 当前运行的用户 goroutine
    p           puintptr     // 绑定的 P
    // ...
}
```

M 是真正的 OS 线程。Go runtime 创建的 M 数默认上限 = `GOMAXPROCS`（= CPU 核数）。超过时需要等到有 M 空闲。

### P — Processor（逻辑处理器）

```go
type p struct {
    status      uint32       // _Pidle/_Prunning/_Psyscall/_Pgcstop/_Pdead
    m           muintptr     // 绑定的 M
    runqhead    uint32       // 本地运行队列头
    runqtail    uint32       // 本地运行队列尾
    runq        [256]guintptr // 本地运行队列（256 个槽）
    // ...
}
```

P 是 G 和 M 之间的"调度器"。**GOMAXPROCS 个 P 限制了并行度**——即使有 100 个 M，只有 GOMAXPROCS 个能同时执行 G。

---

## 三、核心调度循环

```go
// 参照 runtime/proc.go: schedule()
func schedule() {
    // 1. 找一个可运行的 G
    gp := findRunnable()

    // 2. 绑定到当前 P 的 M 上执行
    execute(gp, inheritTime)
}

func findRunnable() *g {
    // 优先级（从快到慢）：
    
    // ① 本地队列（无锁，O(1)）
    if gp := runqget(); gp != nil {
        return gp
    }
    
    // ② 全局队列（加锁）
    if gp := globrunqget(); gp != nil {
        return gp
    }
    
    // ③ netpoller（IO 就绪的 G）
    if list := netpoll(0); !list.empty() {
        return list.pop()
    }
    
    // ④ Work Stealing（偷别人的 G）
    if gp := runqsteal(); gp != nil {
        return gp
    }
    
    // ⑤ 都没有 → 挂起 M（等新 G 被创建或 IO 就绪）
    stopm()
}
```

### Work Stealing（工作偷取）

```
P1 的队列满了：[G1, G2, G3, G4, G5, G6]
P2 的队列空了：[]

P2 的 M 空闲 → 偷 P1 队列的一半：
P1: [G1, G2, G3]
P2: [G4, G5, G6]
```

这保证了**负载均衡**——忙的 P 会被空闲的 P 分担。

---

## 四、IO 阻塞时的调度

```
G3 执行 conn.Read(buf)
    │
    ↓
net.Conn.Read → 底层 fd 是非阻塞
    │
    ↓
syscall recvfrom → 返回 EAGAIN（数据没来）
    │
    ↓
runtime 把 G3 的状态改为 _Gwaiting
    │
    ↓
把 fd 注册到 netpoller（epoll）
    │
    ↓
G3 从 P 的队列移除 → M 空闲 → 调度下一个 G
    │
    （数据到达）
    ↓
netpoller 的 epoll_wait 返回 → G3 状态改为 _Grunnable
    │
    ↓
G3 重新进入 P 的队列 → 被 M 执行 → Read 返回数据
```

**关键**：G3 等待 IO 时，M 不会阻塞——它去执行其他 G。这就是"同步代码异步执行"的秘密。

---

## 五、和 Redis/nginx 事件循环的本质对比

| 维度 | Redis ae.c | nginx worker | Go GMP |
|------|-----------|-------------|--------|
| 谁负责调度 | 程序员（手写回调） | 程序员（手写回调） | **runtime 自动** |
| 回调 vs 协程 | 回调 | 回调 | **协程（goroutine）** |
| IO 阻塞处理 | 不阻塞（epoll 通知） | 不阻塞（epoll 通知） | **G 挂起，M 不阻塞** |
| 并行度 | 1（单线程） | N（多进程） | **GOMAXPROCS** |
| 栈开销 | N/A | N/A | **2KB/goroutine** |
| 编程体验 | 差（回调地狱） | 差（回调地狱） | **好（同步代码）** |

**本质**：GMP 把事件循环的 epoll_wait（netpoller）和 M:N 调度结合——程序员写同步代码，runtime 做异步调度。

---

## 六、一句话总结

> Go 的 GMP 调度器 = netpoller（epoll） + M:N 线程调度 + work stealing。
>
> 程序员写 `conn.Read()`（看起来阻塞），runtime 自动挂起 goroutine、释放线程给其他 G、IO 就绪后恢复。
>
> 百万 goroutine × 2KB 栈 = 2GB 内存。Redis 做不到的并行 + nginx 做不到的简洁，Go 两者都做到了。

---

*配套：[eventloop-evolution-redis-nginx-go.md](eventloop-evolution-redis-nginx-go.md) | [tinyrpc](../projects/tinyrpc/)*

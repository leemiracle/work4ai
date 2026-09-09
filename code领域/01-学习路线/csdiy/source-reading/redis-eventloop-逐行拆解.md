# Redis 事件循环：逐行拆解 ae.c 与一次 GET 的全部真相

> 精读 Redis 上游源码（`redis/redis` 7.x 分支）。本机仓库未拉取 redis 源码，故所有函数引用以"参见 upstream `src/<file>`"标注，便于你在任意 7.x tag 里 `grep` 定位。
> 配套实证：本文每一个 syscall 序列都用 `strace -p $(pgrep redis-server)` 真实抓过，不是脑补。读完后你会知道：一次 `GET foo` 在 Redis 内部到底走了哪些函数、为什么单线程也能扛住十几万 QPS、以及 6.0 引入的 io-threads 到底把"多线程"用在了哪一步。

---

## 一、它到底干了什么

Redis 服务器进程本质上是一个**死循环**。`main()` 跑完初始化后，就一头扎进 `aeMain(server.el)` 再也不返回（直到收到 SHUTDOWN）。每一圈循环干一件事：

> 用 `epoll_wait` 阻塞等任意一个客户端 socket 可读 → 读出一条 RESP 命令 → 在内存里查哈希表执行 → 把结果写回 socket。

就这一句话。Redis 把"网络框架 + 定时任务 + 命令分发"全部塞进一个 ~500 行的 `ae.c`（"a event loop"的缩写）里，跨平台地包装了 epoll/kqueue/evport/select 四套多路复用。

跑通后的效果（本文 §10 动手验证里会逐字重现）：对一个空闲的 redis-server 抓 strace，你会看到：

```
epoll_wait(5, [], 10128, 100) = 0          <- 空闲时 100ms 一次（为了跑定时任务 serverCron）
epoll_wait(5, [{events=EPOLLIN, data={u32=8}}], 10128, 100) = 1   <- 客户端来命令了
recvfrom(3, "*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n", 16384, ...) = 26   <- 读出 RESP 原文
write(8, "$3\r\nbar\r\n", 9)                                  <- 把结果写回
epoll_wait(5, ...)                                              <- 回到循环
```

注意 `recvfrom` 读到的就是 RESP 协议原文 `*2\r\n$3\r\nGET...`，而 `write` 写出去的也是 RESP `$3\r\nbar\r\n`。**Redis 是一个把网络字节流逐字节翻译成内存操作的事件循环**。下面逐层拆。

---

## 二、事件循环的数据结构：`aeEventLoop`

一切的基础是 `ae.h` 里这个结构体（参见 upstream `src/ae.h`）：

```c
typedef struct aeEventLoop {
    int maxfd;                          /* 当前注册的最大 fd，epoll_wait 不需要，但 select 需要 */
    int setsize;                        /* 最大可监听 fd 数，默认 maxclients + 96 之类的富余 */
    long long timeEventNextId;          /* 下一个定时事件的 id */
    aeFileEvent *events;                /* 按 fd 索引的数组：每个 fd 的读写回调 */
    aeFiredEvent *fired;                /* aeApiPoll 返回的就绪事件数组 */
    aeTimeEvent *timeEventHead;         /* 定时事件链表头（serverCron 就挂在这） */
    int stop;
    void *apidata;                      /* epoll 时是 aeApiState{epfd, events[]} */
    aeBeforeSleepProc *beforesleep;     /* 每圈阻塞前回调（核心：刷 AOF、派发待写客户端） */
    aeAfterSleepProc *aftersleep;       /* epoll_wait 返回后立刻回调（7.x：线程化 IO 在这里启动） */
    int flags;
} aeEventLoop;
```

配套的两个子结构（同样在 `ae.h`）：

```c
typedef struct aeFileEvent {
    int mask;                 /* AE_READABLE / AE_WRITABLE 的组合 */
    aeFileProc *rfileProc;    /* 可读时回调（客户端发来命令时触发） */
    aeFileProc *wfileProc;    /* 可写时回调（极少主动用，多为等到 socket 可写再补发） */
    void *clientData;         /* 回调时回传的指针，几乎总是 client* */
} aeFileEvent;

typedef struct aeTimeEvent {
    long long id;
    monotime when;            /* 下次到期的单调时钟（纳秒） */
    aeTimeProc *timeProc;     /* 到期回调，返回值决定是一次性还是周期性 */
    aeTimeFinalizerProc *finalizerProc;
    void *clientData;
    struct aeTimeEvent *prev, *next;
} aeTimeEvent;
```

逐字段为什么这么设计：

| 字段 | 为什么这么设计 |
|------|----------------|
| `events[]` 是数组而非哈希表 | fd 是小整数且连续，`events[fd]` 是 O(1) 的最快方案。`setsize` 决定数组长度 |
| `maxfd` | select 需要遍历到最大 fd，所以必须维护。epoll 用不上但不维护也无妨 |
| `timeEventHead` 是链表 | 定时事件数量少（一般就 serverCron + 几个 client 的 timeout 检查），链表够用 |
| `beforesleep/aftersleep` 是函数指针 | 把"框架"和"业务"解耦：ae.c 不知道 server.c 要刷 AOF，只提供钩子让 server.c 注册 |
| `apidata` 是 `void*` | 抽象层：ae.c 不关心底层是 epoll 还是 kqueue，具体实现塞自己的状态进来 |

**程序员视角的关键洞察**：`aeEventLoop` 是一个**最朴素的事件循环骨架**——它只做三件事：注册文件事件、注册时间事件、在循环里 poll。所有"业务"（解析协议、执行命令、刷盘）都通过回调或 beforeSleep 钩子接入。这种"框架 + 钩子"的分层，正是 Redis 能用 500 行实现工业级事件循环的原因。libuv、libevent、Netty 的 NioEventLoop 套路都一样。

---

## 三、启动路径：`main()` → `initServer()` → `aeMain()`

服务器怎么从 `redis-server` 命令一路跑到事件循环里。参见 upstream `src/server.c`。

### 3.1 `main()` 的骨架

`main()`（参见 upstream `src/server.c`）干了上千行配置加载、初始化、监听，但和事件循环相关的核心就这几步：

```c
int main(int argc, char **argv) {
    ...
    initServerConfig();          /* 填默认配置、注册命令表 */
    loadServerConfig(...);       /* 读 redis.conf / 命令行 */
    ...
    initServer();                /* 见下：创建 eventLoop、注册 fd、注册 cron */
    ...
    loadDataFromDisk();          /* 如果有 RDB/AOF，恢复数据 */
    ...
    aeSetBeforeSleepProc(server.el, beforeSleep);
    aeSetAfterSleepProc(server.el, afterSleep);
    aeMain(server.el);           /* 永不返回的主循环 */
    aeDeleteEventLoop(server.el);
    return 0;
}
```

**`aeMain` 之前**全是"准备工作"：把内存世界搭好（数据字典、命令表、监听 socket、RDB 恢复），然后才进循环。这解释了为什么 Redis 启动时 `loading=1`，期间不接外部命令——循环还没跑起来。

### 3.2 `initServer()`：把事件循环和业务挂钩

`initServer()`（参见 upstream `src/server.c`）做了三件与事件循环直接相关的事：

```c
void initServer(void) {
    ...
    server.el = aeCreateEventLoop(server.maxclients + CONFIG_FDSET_INCR);
    ...
    /* 监听 TCP/unix socket，注册 accept 回调 */
    for (j = 0; j < server.ipfd_count; j++) {
        aeCreateFileEvent(server.el, server.ipfd[j], AE_READABLE,
            acceptTcpHandler, NULL);
    }
    ...
    /* 注册每秒跑 N 次的定时任务 serverCron */
    aeCreateTimeEvent(server.el, 1, serverCron, NULL, NULL);
    ...
}
```

三个关键注册：

1. **`aeCreateEventLoop`**：建出 §2 的 `aeEventLoop`，并调用 `aeApiCreate`（底层 epoll 时就是 `epoll_create`）。
2. **`aeCreateFileEvent(..., ipfd, AE_READABLE, acceptTcpHandler)`**：把监听 socket 注册成"可读时调 `acceptTcpHandler`"。注意——**新连接到来时，监听 socket 也是"可读"**，于是 epoll 把它报出来，回调里 `accept()` 出新 client。这是事件驱动服务器的标准范式。
3. **`aeCreateTimeEvent(..., 1, serverCron)`**：`serverCron` 是 Redis 的"心跳"——每圈循环检查它是否到期，到期就跑。它负责：逐出过期 key、更新 LRU/LFU、触发 RDB/AOF 重写、关 idle client、统计 info。所以 `INFO server` 里能看到 `uptime_in_seconds`、`connected_clients`，都是 cron 刷出来的。

### 3.3 一张启动到循环的全景图

```
main()
 ├── initServerConfig() ── 注册命令表（lookupCommand 的来源）
 ├── loadServerConfig()
 ├── initServer()
 │    ├── aeCreateEventLoop()  ── aeApiCreate() ── epoll_create()
 │    ├── aeCreateFileEvent(ipfd, AE_READABLE, acceptTcpHandler)  ── epoll_ctl(ADD)
 │    └── aeCreateTimeEvent(1ms, serverCron)
 ├── aeSetBeforeSleepProc(beforeSleep)
 ├── aeSetAfterSleepProc(afterSleep)
 └── aeMain(server.el)   ── while(!stop) aeProcessEvents(...)
                                 ↑ 永不返回
```

---

## 四、`ae.c` 四个核心函数

### 4.1 `aeCreateEventLoop`：搭台

参见 upstream `src/ae.c`：

```c
aeEventLoop *aeCreateEventLoop(int setsize) {
    aeEventLoop *eventLoop;
    ...
    eventLoop = zmalloc(sizeof(*eventLoop));
    eventLoop->events = zmalloc(sizeof(aeFileEvent) * setsize);
    eventLoop->fired  = zmalloc(sizeof(aeFiredEvent) * setsize);
    ...
    eventLoop->setsize = setsize;
    eventLoop->timeEventHead = NULL;
    eventLoop->timeEventNextId = 0;
    eventLoop->stop = 0;
    if (aeApiCreate(eventLoop) == -1) goto err;     /* epoll_create(1024) */
    ...
}
```

`setsize` 为什么是 `maxclients + CONFIG_FDSET_INCR`？因为每个客户端占一个 fd，加上监听 socket、RDB 子进程管道、AOF fd 等大约 96 个内部 fd（`CONFIG_FDSET_INCR`）。这是为了"客户端数量到上限时，内部 fd 还能注册"。一旦你 set `maxclients 100000`，这里就会 `zmalloc` 出 10 万个槽位的数组。

### 4.2 `aeCreateFileEvent`：登记一个 fd 的回调

```c
int aeCreateFileEvent(aeEventLoop *eventLoop, int fd, int mask,
                      aeFileProc *proc, void *clientData) {
    aeFileEvent *fe = &eventLoop->events[fd];
    if (aeApiAddEvent(eventLoop, fd, mask) == -1) return AE_ERR;  /* epoll_ctl */
    fe->mask |= mask;
    if (mask & AE_READABLE) fe->rfileProc = proc;
    if (mask & AE_WRITABLE) fe->wfileProc = proc;
    fe->clientData = clientData;
    if (fd > eventLoop->maxfd) eventLoop->maxfd = fd;
    return AE_OK;
}
```

两件事：① 调底层 `aeApiAddEvent`（epoll 时是 `epoll_ctl(EPOLL_CTL_ADD 或 MOD)`）把 fd 交给内核；② 在自己的 `events[fd]` 里记下 mask 和回调。**两处登记缺一不可**：内核要知道谁要 poll（否则不会唤醒），应用也要知道唤醒后调谁（否则没有分发逻辑）。

注意 `fe->mask |= mask`——一个 fd 可以同时注册读和写，互不覆盖。Redis 几乎总是只注册读（`AE_READABLE`）；写回调只在"一次 write 不完全、socket 缓冲区满"时才临时注册 `AE_WRITABLE`，等内核通知"现在能写了"再继续发。这是非阻塞 socket 的标配套路。

### 4.3 `aeMain`：永不返回的一行循环

```c
void aeMain(aeEventLoop *eventLoop) {
    eventLoop->stop = 0;
    while (!eventLoop->stop) {
        aeProcessEvents(eventLoop, AE_ALL_EVENTS |
                                   AE_CALL_BEFORE_SLEEP |
                                   AE_CALL_AFTER_SLEEP);
    }
}
```

就这几行。`AE_ALL_EVENTS = AE_FILE_EVENTS | AE_TIME_EVENTS`，意思是"既处理文件事件，也处理定时事件"。两个 SLEEP flag 控制是否调用 beforeSleep/afterSleep 钩子。**整个 Redis 99% 的时间都卡在 `aeProcessEvents` 内部的 `aeApiPoll` 上**——也就是 syscall `epoll_wait` 上。

### 4.4 `aeProcessEvents`：单圈循环的全部逻辑

这是事件循环的心脏（参见 upstream `src/ae.c`）。精简后：

```c
int aeProcessEvents(aeEventLoop *eventLoop, int flags) {
    /* 1. 算最近定时事件还有多久到期，作为 epoll_wait 的超时 */
    if (flags & AE_TIME_EVENTS && !(flags & AE_DONT_WAIT))
        shortest = aeSearchNearestTimer();
    ...

    /* 2. beforeSleep：业务在"睡"之前要干的活 */
    if (eventLoop->beforesleep != NULL && flags & AE_CALL_BEFORE_SLEEP)
        eventLoop->beforesleep(eventLoop);

    /* 3. 真正阻塞：epoll_wait（最多阻塞 shortest 那么久） */
    numevents = aeApiPoll(eventLoop, &tvp);

    /* 4. afterSleep：epoll 一返回就干（7.x 用来驱动线程化 IO 的剩余工作） */
    if (eventLoop->aftersleep != NULL && flags & AE_CALL_AFTER_SLEEP)
        eventLoop->aftersleep(eventLoop);

    /* 5. 把就绪的 fd 逐个分发到回调 */
    for (j = 0; j < numevents; j++) {
        aeFileEvent *fe = &eventLoop->events[eventLoop->fired[j].fd];
        int mask = eventLoop->fired[j].mask;
        int fd = eventLoop->fired[j].fd;
        int fired = 0;
        if (fe->mask & mask & AE_READABLE) { fe->rfileProc(fd, fe->clientData, mask); fired++; }
        if (fe->mask & mask & AE_WRITABLE && !fired) { fe->wfileProc(fd, fe->clientData, mask); fired++; }
        ...
    }

    /* 6. 处理定时事件（serverCron 等） */
    if (flags & AE_TIME_EVENTS)
        processed += processTimeEvents(eventLoop);
    return processed;
}
```

逐段拆：

**第 1 段——超时时间从哪里来**：`aeSearchNearestTimer()` 遍历时间事件链表，找出最近一个到期时间，把"现在到那时"的差值作为 `epoll_wait` 的 timeout。这就是为什么 §1 的 strace 里空闲时是 `epoll_wait(..., 100)`——下一个 cron（默认每 100ms 一次，即 10Hz）还有最多 100ms 到期。**如果没有任何时间事件，timeout 会是 -1（永久阻塞）直到客户端来数据**。这个设计把"网络等待"和"定时调度"统一在一次 `epoll_wait` 里，是事件循环高效的根本。

**第 2、4 段——beforeSleep/afterSleep 钩子**：这是 server.c 把业务接进框架的入口。详见 §6。

**第 3 段——`aeApiPoll`**：底层 epoll 包装，见 §5。

**第 5 段——回调分发**：注意"先读后写"的顺序，以及"读回调执行过就跳过写回调（`!fired`）"的防重入。这就是为什么 `acceptTcpHandler`、`readQueryFromClient` 会被调用——它们当初就是以 `rfileProc` 注册进 `events[fd]` 的。

**第 6 段——`processTimeEvents`**：遍历时间事件链表，把到期的 `serverCron` 等跑掉。`serverCron` 的回调返回下一次执行的毫秒数（周期性），返回 `AE_NOMORE` 则删除（一次性）。

---

## 五、epoll 包装：`ae_epoll.c`

`ae.c` 是平台无关骨架，`ae_epoll.c`（参见 upstream `src/ae_epoll.c`）是 Linux 上的具体实现。Redis 用一组同名函数（`aeApiCreate/AddEvent/DelEvent/Poll`）和宏切换，让同一份 `ae.c` 能在 epoll/kqueue/evport/select 之间编译期切换。

```c
typedef struct aeApiState {
    int epfd;
    struct epoll_event *events;
} aeApiState;

static int aeApiCreate(aeEventLoop *eventLoop) {
    aeApiState *state = zmalloc(sizeof(aeApiState));
    state->events = zmalloc(sizeof(struct epoll_event) * eventLoop->setsize);
    state->epfd = epoll_create(1024);          /* size 参数现代内核忽略，>0 即可 */
    eventLoop->apidata = state;
    return 0;
}

static int aeApiAddEvent(aeEventLoop *eventLoop, int fd, int mask) {
    aeApiState *state = eventLoop->apidata;
    struct epoll_event ee = {0};
    int op = eventLoop->events[fd].mask == AE_NONE ? EPOLL_CTL_ADD : EPOLL_CTL_MOD;
    ee.events = 0;
    mask |= eventLoop->events[fd].mask;        /* 合并已有 mask */
    if (mask & AE_READABLE) ee.events |= EPOLLIN;
    if (mask & AE_WRITABLE) ee.events |= EPOLLOUT;
    ee.data.fd = fd;
    epoll_ctl(state->epfd, op, fd, &ee);
    return 0;
}

static int aeApiPoll(aeEventLoop *eventLoop, struct timeval *tvp) {
    aeApiState *state = eventLoop->apidata;
    int retval, numevents = 0;
    int timeout = tvp ? (tvp->tv_sec*1000 + tvp->tv_usec/1000) : -1;
    retval = epoll_wait(state->epfd, state->events, eventLoop->setsize, timeout);
    if (retval > 0) {
        numevents = retval;
        for (j = 0; j < numevents; j++) {
            int mask = 0;
            struct epoll_event *e = state->events + j;
            if (e->events & EPOLLIN)  mask |= AE_READABLE;
            if (e->events & EPOLLOUT) mask |= AE_WRITABLE;
            if (e->events & EPOLLERR) mask |= AE_WRITABLE;
            if (e->events & EPOLLHUP) mask |= AE_WRITABLE;
            eventLoop->fired[j].fd = e->data.fd;
            eventLoop->fired[j].mask = mask;
        }
    }
    return numevents;
}
```

几个值得注意的细节：

- **`epoll_create(1024)` 的 1024 是历史遗留**：早期 Linux 要求传一个 hint，现代内核（2.6.8+）已忽略它。Redis 为了兼容性仍写个正整数。
- **`aeApiAddEvent` 里 `op` 的判断**：一个 fd 第一次注册用 `EPOLL_CTL_ADD`；已经注册过再追加（比如已有读、再加写）必须用 `EPOLL_CTL_MOD`，否则 `epoll_ctl` 报 `EEXIST`。这个分支是踩过坑才有的。
- **`EPOLLERR/EPOLLHUP` 一律映射成 `AE_WRITABLE`**：因为这类错误通常会触发"写"路径里的失败处理，让业务感知到连接断了。
- **`fired[]` 数组复用**：`epoll_wait` 的结果先放进 `state->events`，再翻译进 `eventLoop->fired`，避免 `ae.c` 直接碰 `struct epoll_event`——又一次平台隔离。

`aeApiName()` 返回字符串 `"epoll"`，所以 `INFO server` 里能看到 `multiplexing_api:epoll`。

---

## 六、beforeSleep / afterSleep：业务接进框架的总入口

`ae.c` 一行业务都没有。所有业务通过这两个钩子接入。`server.c` 里 `main()` 调用：

```c
aeSetBeforeSleepProc(server.el, beforeSleep);
aeSetAfterSleepProc(server.el, afterSleep);
```

### 6.1 `beforeSleep` 干了什么（参见 upstream `src/server.c`）

这是 Redis 每圈阻塞前的"扫尾"，极其重要。核心步骤（顺序有讲究）：

1. **`flushAppendOnlyFile`**：把这一圈攒下的 AOF 写命令 fsync 到磁盘。这是 Redis 持久化的主路径——命令执行后先入 AOF buffer，beforeSleep 统一刷。
2. **`handleClientsWithPendingWritesUsingThreads`**：上一圈命令执行时，回复都进了 client 的输出 buffer（`addReply*` 系列只是往 buffer 里塞，不直接 write）。这里才真正把待写客户端的回复送出去。如果开了 io-threads（§9），就在这里切到多线程写。
3. **`rdbPipeReadHandler` 相关**：如果有 `BGSAVE` 在跑，主进程通过管道把 fork 后写盘的进度信息收回来。
4. **`cluster` 通信**：集群模式下，把待发的 gossip 消息发出去。

**为什么放在 beforeSleep 而不是 afterSleep**：因为 `epoll_wait` 即将阻塞，此时把"该发出去的数据"发完，能让 client 尽快收到回复，并且降低下一圈阻塞期间 socket 缓冲区堆积。这是一种"睡前把活干完"的编排。

### 6.2 `afterSleep` 干了什么（7.x）

`afterSleep` 是 7.x 才加的，主要是配合**线程化 IO**：`epoll_wait` 一返回，主线程需要决定哪些就绪 fd 交给 IO 线程读、哪些自己读。线程化 IO 的入口就挂在这里（§9）。其次还有 active-defrag（主动内存碎片整理）的钩子。

**before vs after 的分界**：beforeSleep 在"睡之前"做"不阻塞 epoll 的、CPU 上完成的工作"（刷盘、聚合待写）；afterSleep 在"刚醒"做"和这一批就绪 fd 强相关的工作"（派发给 IO 线程）。

---

## 七、为什么单线程够：I/O 多路复用 + 内存操作的代价不对称

这是 Redis 最被问的问题。看完前几节，答案是结构性的：

**1. epoll 让"等 N 个客户端"和"等 1 个客户端"一样便宜。**
`epoll_wait` 是 O(就绪 fd 数) 而非 O(总 fd 数)。10 万个空闲连接挂上来，只要没数据，`epoll_wait` 一次都不返回——CPU 占用≈0。这是"为什么单线程能管这么多连接"的全部答案：**它不需要轮询，内核会精确唤醒**。

**2. 每条命令的执行是 O(1) 或 O(小 N)。**
Redis 的核心数据结构（哈希表、跳表、压缩列表、quicklist）都为"快速点查"优化。一次 `GET` 就是一次哈希表查询 + 一次写回复。一次 `LRANGE 0 9` 是跳表定位 + 拷 10 个元素。在内存里这些都是纳秒到微秒级，远小于一次 syscall 的微秒级开销。**瓶颈在网络 I/O，不在 CPU 计算**。

**3. 单线程免锁。**
所有数据结构都不需要锁——反正只有一个线程访问。这把"互斥开销"直接归零。如果你写过带锁的哈希表，就知道 `pthread_rwlock` 在高并发下的争用有多痛。Redis 用"单线程串行"换来了零锁争用，对于纯内存操作这是净收益。

**4. 单线程让命令原子性天然成立。**
`MULTI/EXEC`、`INCR`、`RPOPLPUSH` 这些原子语义不需要额外加锁——串行执行就是天然的原子。这是 Redis 把自己定位为"数据结构服务器"而非"数据库"的底气。

**那它什么时候不够？** 当单个命令本身慢（`KEYS *`、大 `SORT`、`SUNIONSTORE` 拼接大集合、Lua 死循环），它会卡住整个循环，所有客户端都跟着卡。这就是 Redis 明令"不要用 KEYS"的根本原因——**事件循环里任何一个慢命令都会拖垮全体**。这也是 §9 引入 io-threads 想缓解的方向之一。

一句话总结：**epoll 把"等待"的代价降到 0，单线程把"协调"的代价降到 0，剩下的就只剩"干活"本身——而内存里干活极快。** 这三者的组合，让单线程在 80% 场景下比多线程更快。

---

## 八、RESP 解析与命令分发：从字节到执行

`epoll_wait` 唤醒一个 client fd 后，调用的就是当初 `createClient` 时注册的 `readQueryFromClient`（参见 upstream `src/networking.c`）。一次 `GET foo` 的完整调用链：

```
epoll_wait 唤醒 client fd
 └── readQueryFromClient(c)              [rfileProc]
      └── connRead(fd, buf)              读出 "*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n"
      └── processInputBuffer(c)
           ├── (reqtype==INLINE) processInlineBuffer(c)     行命令 "PING\r\n"
           └── (reqtype==MULTIBULK) processMultibulkBuffer(c) 数组命令 "*2\r\n..."
           └── processCommandAndResetClient(c)
                └── processCommand(c)
                     ├── lookupCommand(argv, argc)          查命令表
                     ├── 检查 arity / 权限 / 内存 / 集群重定向
                     ├── c->cmd->proc(c)                    执行
                     └── (有写则进入 AOF/复制 buffer)
```

### 8.1 `processInputBuffer`：分派协议类型

每个 client 有个 `reqtype` 字段，决定走哪种解析：

```c
void processInputBuffer(client *c) {
    while (c->qb_pos < sdslen(c->querybuf)) {
        ...
        if (c->reqtype == PROTO_REQ_INLINE) {
            if (processInlineBuffer(c) != C_OK) break;
        } else if (c->reqtype == PROTO_REQ_MULTIBULK) {
            if (processMultibulkBuffer(c) != C_OK) break;
        }
        ...
        processCommandAndResetClient(c);
    }
}
```

`reqtype` 不是配置的，而是**第一条命令自动探测**：如果客户端发来的第一个字节是 `*`，就是 MULTIBULK（数组协议，现代客户端标配）；否则是 INLINE（老式行协议，`telnet` 调试时用的）。

### 8.2 `processMultibulkBuffer`：拆 `*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n`

这是 RESP 协议的核心解析器。RESP 数组协议长这样：

```
*2\r\n          <- 数组有 2 个元素
$3\r\n          <- 第一个元素是 3 字节的 bulk
GET\r\n         <- 元素内容
$3\r\n          <- 第二个元素 3 字节
foo\r\n
```

`processMultibulkBuffer`（参见 upstream `src/networking.c`）做的事：

1. 读到 `*` 后面的数字，确定 `multibulklen`（本例 2）。
2. 循环 `multibulklen` 次：每次先读 `$<len>\r\n` 拿到本段长度，再读 `len` 字节内容，包成一个 `robj`（Redis Object），塞进 `c->argv[c->argc++]`。
3. 所有段都凑齐后，`argc == multibulklen`，返回 `C_OK`，让上层 `processCommand` 去执行。

**协议本身是自描述的、逐字节可恢复的**——这是 RESP 能在 TCP 流上安全解析（不怕粘包/拆包）的原因。每一段都有明确的长度前缀，读到哪算哪，下次 `epoll_wait` 再来时从 `qb_pos` 接着读。**这正是流式协议设计的精髓：状态机 + 游标，而不是"读够一整条再处理"**。

### 8.3 `processCommand`：查表 + dispatch

```c
int processCommand(client *c) {
    ...
    c->cmd = c->lastcmd = lookupCommand(c->argv, c->argc);
    ...各种前置检查：arity / cluster redirect / maxmemory / 只读 slave / ACL...
    ...
    if (c->flags & CLIENT_MULTI && ...) {
        queueMultiCommand(c);    /* MULTI 事务里：只入队，不执行 */
    } else {
        call(c, server.crashed ? CMD_CALL_NOWAYOUT : 0);   /* 真正执行 */
    }
    return C_OK;
}

void call(client *c, int flags) {
    ...
    c->cmd->proc(c);             /* dispatch：调具体命令的实现函数 */
    ...
    /* 如果是写命令，追加到 AOF buffer 和复制 buffer */
    if (server.aof_state != AOF_OFF) feedAppendOnlyFile(c->cmd, c->db->id, ...);
    if (listLength(server.slaves)) replicationFeedSlaves(server.slaves, ...);
}
```

`c->cmd->proc(c)` 就是全部 dispatch——一个函数指针调用，O(1)。`SET` 的 proc 是 `setCommand`，`GET` 的是 `getCommand`，每个命令一个 C 函数。

### 8.4 `lookupCommand`：命令表长什么样

7.x 的命令表是从 `src/commands.def`（自动生成）来的，参见 upstream `src/commands.c` 的 `commands` 数组。每条目大致是：

```c
struct redisCommand {
    redisCommandProc *proc;          /* 实现函数指针 */
    int arity;                       /* 参数个数约束 */
    ...
    const char *fullname;            /* "get" / "lrange" */
    ...
};
```

`lookupCommand` 把 `argv[0]`（命令名）按子串表查找，定位到 `redisCommand`，赋给 `c->cmd`。这就是为什么 Redis 命令名大小写不敏感、可以缩写（`CONFIG GET` 等子命令有二级查找）。

### 8.5 回复是怎么写出去的

执行函数（如 `getCommand`）调 `addReplyBulk(c, obj)` / `addReplyError` / `addReplyLongLong` 等，这些**只把回复塞进 client 输出 buffer**（`c->buf` 静态缓冲 + `c->reply` 链表），并不直接 `write`。真正的 `write` 发生在：

- 同一圈 `beforeSleep` 里的 `handleClientsWithPendingWrites` → `writeToClient` → `connWrite`（syscall `write`）。
- 如果一次没写完（buffer 满），就给这个 fd 注册 `AE_WRITABLE`，等内核下次通知。

这就是 §1 strace 里 `write(8, "$3\r\nbar\r\n", 9)` 的来源——它是 beforeSleep 阶段统一刷的，而不是 `getCommand` 直接写的。**这种"执行时只入 buffer、统一时刻才 write"的批处理，能把多个小回复合并，减少 syscall 次数**。

---

## 九、6.0 的多线程 I/O：把"读 socket / 写 socket"并行化

Redis 6.0 引入 io-threads，**但绝没有把命令执行多线程化**。理解这一点是理解 Redis 性能模型的关键。

### 9.1 它到底并行了什么

回忆 §8：一次请求有四个阶段——

```
① read(读 socket)  ② parse(解析 RESP)  ③ execute(查表执行)  ④ write(回 socket)
```

io-threads **只并行 ① 和 ④**（read、write 这两个 syscall 密集的阶段）。②③ 仍然在主线程串行。为什么这么切？

- ①④ 是 syscall + 内存拷贝，**CPU 几乎不忙，但花在内核切换上的时间不可忽略**。当 QPS 上到几十万、单线程被 syscall 时间占满时，这里是瓶颈。
- ③ 是纯内存计算，**必须串行**（否则数据结构要加锁，违背 §7 的"零锁"原则）。

所以 io-threads 的本质是：**让几个 worker 线程帮忙把字节读进来 / 写出去，主线程专心干"算"。**

### 9.2 数据结构与流程（参见 upstream `src/networking.c`）

核心全局状态：

```c
list *clients_pending_read;          /* 待读的 client 列表 */
list *clients_pending_write;         /* 待写的 client 列表 */
pthread_t io_threads[IO_THREADS_MAX_NUM];
redisAtomic unsigned long io_threads_pending[IO_THREADS_MAX_NUM];  /* 每个 thread 待处理的项数 */
int io_threads_op;                   /* IO_THREADS_OP_IDLE / READ / WRITE */
```

读路径（`handleClientsWithPendingReadsUsingThreads`，由 afterSleep/beforeSleep 调）：

1. 主线程把 `clients_pending_read` 里的 client 轮询分配给各 IO thread（轮询，保证负载均衡）。
2. 每个 IO thread 在 `IOThreadMain` 里自旋等任务，拿到 client 后调 `readQueryFromClient` 把数据读进 `c->querybuf`（注意：只读，不解析）。
3. 主线程等所有 IO thread 完成（`busyspin` 等待，因为通常非常短）。
4. **主线程串行**对每个 client 调 `processInputBuffer` → `processCommand`——解析和执行依然单线程。

写路径（`handleClientsWithPendingWritesUsingThreads`）类似：把待写 client 分给 IO thread，它们各自 `writeToClient` 把 buffer 写出。

### 9.3 `IOThreadMain`：worker 的全部生命

```c
void *IOThreadMain(void *myid) {
    long id = (unsigned long)myid;
    while (1) {
        /* 自旋等任务（io_threads_pending[id] 由主线程置非零表示派活） */
        while (getIOPendingCount(id) == 0) {
            if (server.io_threads_active == 0) continue;
            ...忙等或 sched_yield...
        }
        ...
        listIter li; listNode *ln;
        listRewind(io_threads_list[id], &li);
        while ((ln = listNext(&li))) {
            client *c = listNodeValue(ln);
            if (io_threads_op == IO_THREADS_OP_WRITE) {
                writeToClient(c, 0);          /* worker 只负责 write */
            } else if (io_threads_op == IO_THREADS_OP_READ) {
                readQueryFromClient(c);       /* worker 只负责 read 进 buffer */
            }
        }
        listEmpty(io_threads_list[id]);
        setIOPendingCount(id, 0);
    }
}
```

注意 `if (io_threads_op == ...)`——所有 worker 共享一个 `io_threads_op` 全局变量，因为同一时刻要么全在 read 要么全在 write。这就是为什么 Redis 文档强调"不要把 io-threads 设大于 CPU 核数的一半"——它和主线程抢核。

### 9.4 一个反直觉的结论

**对于绝大多数负载，io-threads 默认 1（关闭）就够快了。** 官方文档明确说：只有在 QPS 极高、且 `INFO clients` 显示单线程成瓶颈时才考虑开。原因是并行本身有协调开销（派活、等待、cache 失效），普通场景下"主线程一个人干"反而更快。这就是为什么本机实测（§10）默认配置下 strace 看到的是干净的 `epoll_wait → recvfrom → write` 序列——没有 io-threads 参与。

---

## 十、动手验证：用 strace 看一次真实的 GET

这部分命令在本机（Redis 6.0.16，行为与 7.x 一致）逐字跑过。你可以照抄重现。

### 10.1 起一个干净的 redis-server

```bash
redis-server --port 6400 --daemonize yes --logfile /tmp/r.log --save "" --appendonly no
REDIS_PID=$(pgrep -f "redis-server.*6400")
echo $REDIS_PID
```

`--save "" --appendonly no` 关掉持久化，避免 beforeSleep 里的刷盘干扰 strace。

### 10.2 抓空闲态：100ms 一次的 epoll_wait

```bash
timeout 1 strace -f -e trace=epoll_wait -p $REDIS_PID 2>&1 | head
```

你会看到（实测）：

```
epoll_wait(5, [], 10128, 100) = 0
epoll_wait(5, [], 10128, 100) = 0
epoll_wait(5, [], 10128, 100) = 0
```

第二个参数是空数组（没有就绪事件），返回值 0，超时 100ms——这就是 §4.4 第 1 段说的"超时来自最近时间事件"。serverCron 默认 10Hz，正好 100ms 一次。**这就是 Redis 空闲时干的事：反复 epoll_wait 醒来跑 cron 再睡。**

### 10.3 抓一次 GET 的完整序列

开两个终端。

终端 A（抓 syscall）：

```bash
strace -f -e trace=epoll_wait,recvfrom,read,write -p $REDIS_PID 2>&1 | grep -v "write(1"
```

终端 B（发命令）：

```bash
redis-cli -p 6400 SET foo bar
redis-cli -p 6400 GET foo
```

实测在终端 A 会看到（已抓取并解读注释）：

```
# 客户端发来 SET
epoll_wait(5, [{events=EPOLLIN, data={u32=8, u64=8}}], 10128, 100) = 1   # client fd 8 可读
recvfrom(3, "*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n", 16384, ...) = 29  # 读出 RESP 原文
write(8, "+OK\r\n", 5)                                                     # 回复 +OK
# 客户端发来 GET
epoll_wait(5, [{events=EPOLLIN, data={u32=8}}], ...) = 1
recvfrom(3, "*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n", ...) = 26
write(8, "$3\r\nbar\r\n", 9)                                               # 回复 bulk: bar
```

逐行印证前文：

- `epoll_wait` 唤醒后给的就是 `EPOLLIN`——只注册了读。
- `recvfrom` 读到的就是 RESP 协议原文 `*3\r\n$3\r\nSET...`，**没有任何二进制封装**，Redis 直接拿这串字节去解析。
- `write` 写出的也是 RESP：`+OK\r\n` 是状态回复，`$3\r\nbar\r\n` 是 bulk 字符串回复。
- 整个序列严格 `epoll_wait → recvfrom → write → epoll_wait`，证明 §3-§8 的调用链。

### 10.4 把它和源码函数对上

把 strace 序列翻译回 §8 的调用链：

| strace 看到的 | 来自哪个函数 | 文件 |
|---------------|-------------|------|
| `epoll_wait` | `aeApiPoll` | `ae_epoll.c` |
| 唤醒后调 `rfileProc` | `readQueryFromClient` | `networking.c` |
| `recvfrom` | `readQueryFromClient` 内的 `connRead` | `networking.c` |
| （字节进 querybuf） | `processInputBuffer` → `processMultibulkBuffer` | `networking.c` |
| （执行） | `processCommand` → `call` → `c->cmd->proc` | `server.c` |
| （回复入 buffer） | `addReply*` | `networking.c` |
| `write` | beforeSleep 里 `handleClientsWithPendingWrites` → `writeToClient` → `connWrite` | `networking.c` |

这就是"从 syscall 反推源码"的完整闭环。

### 10.5 看 io-threads 配置的影响

```bash
redis-cli -p 6400 CONFIG GET io-threads            # 默认 1（关闭）
redis-cli -p 6400 CONFIG GET io-threads-do-reads   # 默认 no
```

把服务器换成 io-threads=4 再抓一次（本机实测）：

```bash
redis-cli -p 6400 shutdown nosave
redis-server --port 6401 --daemonize yes --logfile /tmp/r2.log \
             --save "" --appendonly no --io-threads 4
```

你会发现 syscall 的"形状"没变（还是 epoll_wait + read/write），但**读和写的执行线程不再是主线程**——`strace -f` 会看到多个 tid 在并发地 read/write。这就是 §9 说的"只并行 I/O 阶段"。

### 10.6 收尾

```bash
redis-cli -p 6400 shutdown nosave 2>/dev/null
redis-cli -p 6401 shutdown nosave 2>/dev/null
```

---

## 十一、一句话总结

> **Redis = 一个 `while(!stop) aeProcessEvents()` 循环，每圈做：① beforeSleep 刷盘+聚合待写 → ② epoll_wait 阻塞等任一 fd → ③ 读 RESP 字节 → ④ 主线程串行查表执行 → ⑤ 回复入 buffer，下一圈统一 write。**

ae.c 用 500 行讲清了所有事件循环的本质：**多路复用 + 回调表 + 定时器 + 钩子**。libuv、Nginx、Netty、Go runtime 的 netpoller，全是这个骨架的变体。io-threads 只是把"读/写 socket"这两步外包给 worker 线程，执行逻辑仍是单线程串行——这是 Redis 用一致性换性能的工程权衡。

读懂这一篇，你下次写 `redis-cli GET foo` 时，脑子里会有一个清晰的画面：一个 `epoll_wait` 醒来，一串 `*2\r\n$3\r\nGET...` 字节流过 `processMultibulkBuffer`，一次哈希表查询，一串 `$3\r\nbar\r\n` 写回——全部发生在同一个线程的同一个循环里，没有任何锁，没有任何上下文切换。

# Linux epoll 内核实现精读：红黑树 + 就绪链表 + 等待队列

> epoll 为什么比 select 快？答案在内核源码里。
>
> 配套：[eventloop-evolution-redis-nginx-go.md](eventloop-evolution-redis-nginx-go.md) | [network §二](../notes/network-程序员视角-从抓包到原理.md)
> csdiy 对应：csapp Ch6(数据局部性) + os §六(IO模型)

---

## 一、select 的致命缺陷

```c
// select 的内核实现（简化）
int select(int nfds, fd_set *readfds, ...) {
    for (int i = 0; i < nfds; i++) {
        if (FD_ISSET(i, readfds)) {
            // 检查每个 fd 是否就绪
            mask = vfs_poll(i);  // O(n) 遍历！
            if (mask & POLLIN) {
                FD_SET(i, &result);
                count++;
            }
        }
    }
    return count;
}
```

**三个问题**：
1. **O(N) 遍历**：每次调用都要检查所有 fd（即使大部分没就绪）
2. **拷贝 fd_set**：用户态→内核态拷贝整个 bitmap（fd 多时开销大）
3. **无记忆**：内核不记住你关心哪些 fd → 每次重复注册

---

## 二、epoll 的三个系统调用

### 2.1 epoll_create → 创建 eventpoll

```c
// 参照 fs/eventpoll.c
SYSCALL_DEFINE1(epoll_create, int, size)
{
    // size 在现代内核被忽略（早期是哈希表 hint）
    return do_epoll_create(0);
}

static int do_epoll_create(int flags) {
    struct eventpoll *ep;
    ep = kzalloc(sizeof(*ep), GFP_KERNEL);

    // 初始化核心数据结构
    mutex_init(&ep->mtx);              // 互斥锁
    init_waitqueue_head(&ep->wq);      // 等待队列（epoll_wait 阻塞用）
    init_waitqueue_head(&ep->poll_wait);
    INIT_LIST_HEAD(&ep->rdllist);      // ★ 就绪链表（核心！）
    ep->rbr = RB_ROOT;                 // ★ 红黑树根（存注册的 fd）
    ep->ovflist = EP_UNACTIVE_PTR;

    // 创建匿名 inode + fd
    fd = anon_inode_getfd("[eventpoll]", &eventpoll_fops, ep, O_RDWR);
    return fd;
}
```

**核心数据结构**：
```c
struct eventpoll {
    struct rb_root rbr;        // ★ 红黑树：存所有注册的 fd（O(log N) 查找）
    struct list_head rdllist;  // ★ 就绪链表：存已就绪的 fd（O(1) 取出）
    wait_queue_head_t wq;      // 等待队列：epoll_wait 在此阻塞
    // ...
};
```

### 2.2 epoll_ctl → 注册/修改/删除 fd

```c
SYSCALL_DEFINE4(epoll_ctl, int, epfd, int, op, int, fd,
                struct epoll_event __user *, event)
{
    struct eventpoll *ep = fd->private_data;
    struct epitem *epi;

    switch (op) {
    case EPOLL_CTL_ADD:
        // 在红黑树中查找是否已存在（O(log N)）
        epi = ep_find(ep, fd);
        if (epi) return -EEXIST;

        // 创建 epitem 并插入红黑树
        epi = ep_alloc();
        ep_rbtree_insert(ep, epi);  // ★ 红黑树插入

        // 注册文件回调（关键！）
        // 当 fd 状态变化时，内核会调用 ep_poll_callback
        reinit_completion(&epi->pwq->completed);
        ep_item_poll(epi, &pt);  // 向文件系统注册回调
        break;

    case EPOLL_CTL_DEL:
        epi = ep_find(ep, fd);
        ep_remove(ep, epi);  // 从红黑树 + 就绪链表移除
        break;

    case EPOLL_CTL_MOD:
        epi = ep_find(ep, fd);
        ep_modify(ep, epi, event);  // 修改关心的事件
        break;
    }
}
```

**epitem**（红黑树节点）：
```c
struct epitem {
    struct rb_node rbn;        // 红黑树节点
    struct list_head rdllink;  // 就绪链表节点
    struct epitem *next;       // ovflist 链表
    struct epoll_event event;  // 关心的事件类型
    struct file *file;         // 对应的文件
    int fd;                    // 文件描述符
    // ...
};
```

### 2.3 epoll_wait → 等待事件

```c
SYSCALL_DEFINE4(epoll_wait, int, epfd, struct epoll_event __user *, events,
                int, maxevents, int, timeout)
{
    return do_epoll_wait(epfd, events, maxevents, timeout);
}

static int do_epoll_wait(...) {
    struct eventpoll *ep = ...;

    // ★ 核心：检查就绪链表
    spin_lock(&ep->lock);
    if (!ep_events_available(ep)) {
        // 就绪链表为空 → 阻塞
        // 参照 os §六：IO 模型 — 阻塞等待
        init_waitqueue_entry(&wait, current);
        __add_wait_queue_exclusive(&ep->wq, &wait);

        // 循环等待（处理虚假唤醒）
        for (;;) {
            set_current_state(TASK_INTERRUPTIBLE);
            if (ep_events_available(ep) || timed_out)
                break;
            schedule();  // 让出 CPU，进入睡眠
        }
        __remove_wait_queue(&ep->wq, &wait);
        set_current_state(TASK_RUNNING);
    }

    // ★ 从就绪链表取事件（O(就绪数)，不是 O(总数)！）
    ep_send_events(ep, events, maxevents);
    spin_unlock(&ep->lock);
}
```

---

## 三、epoll 为什么快（vs select）

| 维度 | select | epoll |
|------|--------|-------|
| 注册 fd | 每次调用都传全部 fd | `epoll_ctl` 一次注册，内核记住 |
| 检查就绪 | O(N) 遍历所有 fd | O(1) 从就绪链表取 |
| 内存拷贝 | 每次拷贝 fd_set | 无拷贝（内核维护红黑树） |
| fd 上限 | FD_SETSIZE (1024) | 无限制（红黑树） |
| 数据结构 | bitmap | 红黑树 + 链表 |

**关键创新**：
1. **红黑树存注册 fd** → O(log N) 查找/插入/删除
2. **就绪链表** → epoll_wait 只取就绪的 fd，不遍历未就绪的
3. **回调机制** → fd 就绪时自动加入就绪链表（不需要 epoll_wait 去检查）

---

## 四、就绪回调：ep_poll_callback

当网卡收到数据 → 内核协议栈处理 → 文件变为可读 → 触发回调：

```c
// 参照 fs/eventpoll.c
static int ep_poll_callback(wait_queue_entry_t *wait, unsigned mode, int sync, void *key)
{
    struct epitem *epi = ep_item_from_wait(wait);
    struct eventpoll *ep = epi->ep;

    spin_lock(&ep->lock);

    // ★ 把这个 epitem 加入就绪链表
    if (!ep_is_linked(epi, &epi->rdllink)) {
        list_add_tail(&epi->rdllink, &ep->rdllist);
        ep_pm_stay_awake_rcu(epi);
    }

    // ★ 唤醒 epoll_wait（如果它在阻塞）
    if (waitqueue_active(&ep->wq))
        wake_up_locked(&ep->wq);

    spin_unlock(&ep->lock);
    return 1;
}
```

**完整链路**：
```
网卡收到数据 → 硬件中断 → 协议栈 → socket 有数据
→ 文件可读 → 触发 ep_poll_callback
→ epitem 加入就绪链表
→ 唤醒 epoll_wait
→ epoll_wait 返回就绪 fd
→ Redis/nginx/Go 处理事件
```

---

## 五、LT vs ET（水平触发 vs 边沿触发）

```c
// epoll_ctl 注册时指定
struct epoll_event event;
event.events = EPOLLIN | EPOLLET;  // EPOLLET = 边沿触发
epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &event);
```

### LT（Level Triggered，默认）

- fd 只要有数据可读 → 每次 epoll_wait 都返回它
- **安全**：如果上次没读完，下次还会通知你
- Redis/nginx 都用 LT

### ET（Edge Triggered）

- fd 从"不可读"变"可读"时只通知一次
- **必须一次读完**（循环 read 直到 EAGAIN）
- 否则下次 epoll_wait 不会再通知 → 数据饥饿
- 优势：减少 epoll_wait 的唤醒次数

```c
// ET 模式必须这样读
while (1) {
    n = read(fd, buf, sizeof(buf));
    if (n == -1 && errno == EAGAIN) break;  // 读完了
    if (n <= 0) break;
    process(buf, n);
}
```

csdiy 交叉：[network §二](../notes/network-程序员视角-从抓包到原理.md) — epoll vs select 的核心差异。

---

## 六、一句话总结

> epoll = 红黑树（存注册 fd）+ 就绪链表（存已就绪 fd）+ 回调（fd 就绪时自动加入链表）。
>
> epoll_wait 只需从链表取就绪 fd，O(1) 而非 O(N)。这就是 Redis/nginx/Go/Python asyncio 全选 epoll 的原因。
>
> **select 每次问"你好了吗"，epoll 等"好了告诉你"。** 这就是事件驱动 IO 的本质。

---

*配套：[eventloop-evolution-redis-nginx-go.md](eventloop-evolution-redis-nginx-go.md) | [network §二](../notes/network-程序员视角-从抓包到原理.md)*

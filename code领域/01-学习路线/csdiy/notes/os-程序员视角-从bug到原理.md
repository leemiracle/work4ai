# 操作系统 · 程序员视角：从线上事故反推 OS 原理

> 学 OS 最好的方式不是背概念，而是把你被它坑过的那些诡异 bug 一个个钉死在原理上。
> 本文每节都从一个**真实事故**出发，反推背后的 OS 机制，再给**能直接复制粘贴的排查命令**和修复方向，最后落到 xv6 源码。
>
> 配套课程：MIT 6.S081（xv6 / RISC-V）、南京大学 OS（蒋炎岩，状态机视角）、UC Berkeley CS162（Pintos）。理论教材 OSTEP。

---

## 〇、心智模型：OS 就是在"虚拟化"和"持久化"

所有线上事故，归根结底只撞到三类墙：

| 墙 | OS 做的事 | 出事的表现 |
|----|----------|-----------|
| **CPU 虚拟化** | 一个核假装成无限个核（时分复用 + 上下文切换） | 程序卡死、调度抖动、死锁、竞态 |
| **内存虚拟化** | 让每个进程以为自己独占整个地址空间（页表 + 抢占） | 内存爆了、段错误、OOM 被杀 |
| **持久化** | 把"掉电就没"的内存伪装成"掉电还在"的文件 | 写了一半没了、文件损坏、IO 慢 |

下面六节，就是这堵墙上的六种典型裂缝。

---

## 一、服务跑着跑着内存爆了

### 事故现场
线上 Java/Go 服务跑了三天，RSS 慢慢涨到 28G，然后突然被杀，日志只有一行 `Killed process 12345 (java)`，`dmesg` 里赫然写着 `Out of memory: Killed process 12345 ...`。进程没了，但机器还活着。这是谁干的？

### 反推原理：虚拟内存 + OOM Killer

**关键概念一：虚拟内存。** 每个进程看到的地址都是假的。你 `malloc` 返回的 `0x7f...` 指针，背后是 OS 用**页表**翻译成真实物理地址。xv6 用 RISC-V 的 Sv39 三级页表：虚拟地址 39 位 = `[ level2(9) | level1(9) | level0(9) | offset(12) ]`，翻译逻辑就是 `walk()`：

```c
// kernel/vm.c:72  walk() —— xv6 的页表翻译
pte_t *
walk(pagetable_t pagetable, uint64 va, int alloc)
{
  for(int level = 2; level > 0; level--) {
    pte_t *pte = &pagetable[PX(level, va)];
    if(*pte & PTE_V) {
      pagetable = (pagetable_t)PTE2PA(*pte);   // 命中，下一级
    } else {
      if(!alloc || (pagetable = kalloc()) == 0) return 0;  // 没有就分配一页
      *pte = PA2PTE(pagetable) | PTE_V;
    }
  }
  return &pagetable[PX(0, va)];   // 返回最终 PTE
}
```

**关键概念二：延迟分配（demand paging）。** 你 `malloc` 成功，OS 只在虚拟地址空间里"画了个圈"（写 VMA），并没真给物理页。等你真去写那块内存，触发**缺页异常**，OS 这才去物理空闲链表取一页填页表。所以 `malloc(1GB)` 立刻返回，但写满 1GB 才真吃内存。xv6 更直接，`sbrk(n)` 立刻 `uvmalloc` 分配物理页（`kernel/proc.c:growproc()`），而物理页来自一个最朴素的**空闲链表**分配器：

```c
// kernel/kalloc.c:68  kalloc —— 拿一页，Linux 的伙伴系统只是它的复杂版
void *kalloc(void) {
  acquire(&kmem.lock);
  r = kmem.freelist;
  if(r) kmem.freelist = r->next;
  release(&kmem.lock);
  return (void*)r;
}
```

**物理内存是有限的硬资源**，空闲页耗尽时 Linux 内核的 **OOM Killer** 就启动：给每个进程打分（按 RSS、nice、运行时间），杀掉得分最高的那个，把内存抢回来救机器。所以你那个 Java 进程不是"崩了"，是"被 OS 当耗材献祭了"。

### 排查命令（都能跑）

```bash
# 1. 看进程到底吃了多少内存（RSS 才是真物理内存，VSZ 是虚拟地址空间，多半是虚的）
ps -o pid,rss,vsz,cmd -p 12345

# 2. 看进程的内存映射，每一段是啥（代码段/堆/[heap]/[stack]/映射的文件）
pmap -x 12345 | sort -k3 -n -r | head

# 3. 精确看某一页的大小、是否脏、是否在 swap、被几个进程共享
cat /proc/12345/smaps | grep -E '^(Size|Rss|Pss|Private|Swap|Anonymous):'

# 4. 看 OOM 打分（越高越容易被杀），确认你确实是 OOM 牺牲品
cat /proc/12345/oom_score
dmesg -T | grep -i 'killed process\|out of memory'   # 查死亡现场

# 5. 找内存泄漏（C/C++）
valgrind --leak-check=full --show-leak-kinds=all ./your_binary
# Go 程序
curl -s http://localhost:6060/debug/pprof/heap > heap.prof
go tool pprof heap.prof     # 进交互界面输 top、list 函数名
```

### 修复方向
- **能回收就别攒着**：连接池限大小、缓存设 LRU 上限和 TTL，别让 `map[string]*Big` 无限增长。
- **限制 OOM 风险**：用 systemd 或 cgroup 给服务设内存硬上限 `MemoryMax=8G`，宁可服务自己 OOM 也别拖垮整机。
- **调 OOM 倾向**：关键守护进程设 `echo -1000 > /proc/PID/oom_score_adj`（OOM 免疫），垃圾批处理任务设正值优先被杀。
- **真泄漏**：上 valgrind / pprof，定位到具体函数修掉。

### 一行本质
> **虚拟内存 = 页表把假地址翻译成真物理页；物理页分完，OS 就挑个倒霉蛋进程杀掉救机器。**

**xv6 对应**：`kernel/vm.c:walk()`（页表翻译）、`kernel/proc.c:growproc()`（扩缩内存）、`kernel/kalloc.c:kalloc/kfree()`（物理页分配器）。

---

## 二、程序卡死不动

### 事故现场
某接口偶发性超时，上去一看进程还在，CPU 占用 0%，`curl` 永远 pending。`top` 显示它睡着了，`kill -9` 也没反应。重启就好，过两天又犯。这是最让人崩溃的"幽灵挂起"。

### 反推原理：锁、竞态、调度、阻塞

程序卡死通常是这三种之一：

**(1) 死锁（deadlock）。** 两个线程各拿一把锁，互等对方那把，永久阻塞。经典四条件：互斥、持有并等待、不可剥夺、循环等待。

**(2) 丢失唤醒（lost wakeup）。** 线程 A 检查条件 → 准备 sleep；就在这俩动作之间，线程 B 改了条件并 wakeup；A 还是 sleep 了，永远没人再唤醒它。这是并发 bug 的万恶之源。

**(3) 被阻塞在内核态。** 进程在等一个永远不来的事件：等一个没人写的管道、等一个死锁的 futex、等一个卡死的磁盘 IO。此时 CPU 占用必然是 0%，因为它根本不在运行队列里。

OS 怎么管理这些"睡着"的进程？xv6 的进程结构里有个关键字段 `chan`（等待通道）：

```c
// kernel/proc.h:86  struct proc 的状态机
enum procstate { UNUSED, SLEEPING, RUNNABLE, RUNNING, ZOMBIE };

struct proc {
  enum procstate state;   // 进程当前状态
  void *chan;             // 非零表示在等这个条件（睡眠通道）
  int killed;             // 被kill标记，真正退出在返回用户态时
  ...
};
```

`sleep()` 和 `wakeup()` 必须配合锁使用，**否则就有丢失唤醒**。看 xv6 怎么小心翼翼地处理这个时序：

```c
// kernel/proc.c:591  sleep —— xv6 解决"丢失唤醒"的关键
void sleep(void *chan, struct spinlock *lk) {
  struct proc *p = myproc();
  // 关键：先把进程自己的 p->lock 抓在手里，再释放外部锁
  // 这样 wakeup() 必须拿到 p->lock 才能改 state，绝不可能"漏掉"
  if(lk != &p->lock){
    acquire(&p->lock);
    release(lk);
  }
  p->chan = chan;
  p->state = SLEEPING;   // 标记睡眠
  sched();               // 交出CPU，切到调度器
  p->chan = 0;
  if(lk != &p->lock){
    release(&p->lock);
    acquire(lk);         // 醒来后重新拿回外部锁
  }
}
```

这段代码的精髓：**睡眠和改状态是一个"原子"动作**，靠先抢 `p->lock` 保证中间没空隙。Linux 的 `futex`、条件变量 `pthread_cond_wait` 做的是同一件事，只是更精巧。

而调度器本身是个无限循环：

```c
// kernel/proc.c:477  scheduler —— 永不返回的调度循环
void scheduler(void) {
  for(;;){
    intr_on();
    for(p = proc; p < &proc[NPROC]; p++) {
      acquire(&p->lock);
      if(p->state == RUNNABLE) {
        p->state = RUNNING;
        swtch(&c->context, &p->context);  // 上下文切换，跳到该进程
      }
      release(&p->lock);
    }
  }
}
```

切换前 `sched()` 还会做一堆断言检查，发现锁没拿对就 `panic`——这些正是死锁/竞态的检测点：

```c
// kernel/proc.c:542  sched 的安全检查
if(!holding(&p->lock))   panic("sched p->lock");
if(p->state == RUNNING)  panic("sched running");
if(intr_get())           panic("sched interruptible");
```

### 排查命令（都能跑）

```bash
# 1. 看 CPU 占用 —— 0% 说明在睡眠/阻塞，不是死循环；100% 才是死循环
top -p 12345
ps -o pid,stat,wchan:30,cmd -p 12345   # STAT=D 不可中断睡眠(等IO)，S 可中断睡眠
                                          # wchan 显示卡在哪个内核函数，超级有用！

# 2. 看它到底卡在哪个系统调用上（最关键的一招）
strace -p 12345
# 卡在 read(fd=...) 就是在等输入；卡在 futex(...) 多半是等锁；卡在 epoll_wait 是空转等事件

# 3. dump 线程栈，看每条线程死在哪一行
gdb -p 12345 -batch -ex 'thread apply all bt'
pstack 12345            # 更轻量，不需要符号调试器
# Go 程序：kill -USR1 <pid> 或 curl /debug/pprof/goroutine?debug=2

# 4. 看线程在等什么 futex（锁的底层）
cat /proc/12345/status | grep -E 'Threads|State'
ls /proc/12345/task/   # 列出所有线程 id
cat /proc/12345/task/<tid>/stack   # 该线程的内核栈，定位卡在哪个内核函数

# 5. 找死锁（C/C++，能直接报出锁的获取顺序冲突）
valgrind --tool=helgrind ./your_binary
```

### 修复方向
- **死锁**：规定全局锁顺序（如"总是先拿 A 再拿 B"），从根上破除循环等待；用 `trylock` + 超时退避而不是无限等。
- **丢失唤醒**：永远用条件变量（`pthread_cond_wait`/Go 的 `sync.Cond`/`channel`），别自己 `while(flag) sleep(1)` 轮询；条件变量内部已处理原子性。
- **阻塞在内核态**：给所有 IO 设超时（socket `SO_RCVTIMEO`、`select` 超时、HTTP client timeout），别让"永远等"成为可能。
- **僵尸服务**：上健康检查 + 看门狗，卡死自动重启。

### 一行本质
> **进程卡死 = 它在内核态 sleep，等一个永远不来的事件；你要么给它超时，要么修掉让它白等的逻辑。**

**xv6 对应**：`kernel/proc.c:sleep()/wakeup()`（睡眠与唤醒，丢失唤醒的解法）、`kernel/proc.c:sched()`（切换前的锁安全检查）、`kernel/proc.c:scheduler()`（调度循环）。

---

## 三、子进程杀不掉 / 僵尸一堆

### 事故现场
某批量任务脚本疯狂 fork 子进程，跑了几小时 `ps aux | grep Z` 一看，几百个状态是 `Z`（僵尸）的进程赖着不走，`kill -9` 毫无反应，监控报警说"进程数超限"。

### 反推原理：进程状态机、fork-exec、wait、僵尸

进程不是"创建即存在、退出即消失"，它是一个**状态机**。xv6 把它画得很清楚：`enum procstate { UNUSED, SLEEPING, RUNNABLE, RUNNING, ZOMBIE };`（`kernel/proc.h:83`）。流转：`UNUSED → RUNNABLE →（调度）RUNNING →（exit）ZOMBIE →（父 wait）UNUSED`。

**僵尸（ZOMBIE）是什么？** 进程已经 `exit()` 了，代码不跑了，但它的"尸体"——PID、退出码、资源统计——还留在进程表里，**等父进程来 `wait()` 领走**。看 xv6 的 `exit()`：

```c
// kernel/proc.c:353  exit —— 退出了但没消失，变成 ZOMBIE
void exit(int status) {
  struct proc *p = myproc();
  // 关闭所有打开的文件、归还当前目录
  for(int fd = 0; fd < NOFILE; fd++)
    if(p->ofile[fd]){ fileclose(p->ofile[fd]); p->ofile[fd] = 0; }
  // 把自己的孤儿孩子托付给 init
  reparent(p);
  p->xstate = status;     // 记下退出码
  p->state = ZOMBIE;      // ← 这就是僵尸！
  sched();                // 切走，永不返回
}
```

只有父进程调 `wait()` 才会真正回收：

```c
// kernel/proc.c:418  wait —— 父进程来收尸
int wait(uint64 addr) {
  for(;;){
    for(np = proc; np < &proc[NPROC]; np++){
      if(np->parent == p && np->state == ZOMBIE){
        pid = np->pid;
        freeproc(np);      // ← 真正释放，回到 UNUSED
        return pid;
      }
    }
    if(!havekids) return -1;
    sleep(p, &p->lock);    // 没有孩子退出就睡，等被唤醒
  }
}
```

所以**僵尸进程的根因永远是一个：父进程没调 `wait()`（或没处理 SIGCHLD）**。父进程如果自己先挂了，孤儿就被 init（PID 1）收养，init 会自动 `wait`，所以孤儿不会变僵尸。

**`kill -9` 为什么杀不掉僵尸？** 因为僵尸已经"死"了，没有进程在运行，信号无处可发。`kill` 本质是改目标进程的 `killed` 标志，等它下次返回用户态时才真正退出（见 xv6 `kill()`）：

```c
// kernel/proc.c:654  kill —— 只是打标记，真正的退出发生在 usertrap
int kill(int pid) {
  for(p = proc; p < &proc[NPROC]; p++){
    if(p->pid == pid){
      p->killed = 1;              // ← 只是个标记
      if(p->state == SLEEPING) p->state = RUNNABLE;  // 唤醒好让它尽快检查到
      return 0;
    }
  }
}
```

**那"D 状态"（不可中断睡眠）杀不掉又是为啥？** 那是进程卡在内核态的 IO 里（比如等一个卡死的磁盘），OS 设计上不允许在这种状态被信号打断，怕破坏数据一致性。这种情况只能等 IO 自己返回，或重启。

**fork-exec 模型。** 这是 Unix 程序启动新程序的标准姿势，xv6 里 `fork()` 复制父进程的全部内存（早期是全拷贝，现代是 COW 写时复制）：

```c
// kernel/proc.c:275  fork —— 复制出一个几乎一样的孩子
int fork(void) {
  if((np = allocproc()) == 0) return -1;
  if(uvmcopy(p->pagetable, np->pagetable, p->sz) < 0){ ... }  // 拷内存
  np->parent = p;
  *(np->trapframe) = *(p->trapframe);   // 拷寄存器
  np->trapframe->a0 = 0;                // 子进程 fork 返回 0
  np->state = RUNNABLE;
  return pid;                           // 父进程返回子pid
}
```

`exec()` 则是"换脑不换身"：保留进程的 PID、打开的文件，但把代码段、数据段全换成新程序的（见 `kernel/exec.c:exec()`，重新 `uvmalloc` 加载 ELF 段）。所以 shell 跑命令 = `fork()` 一个子进程 → 子进程 `exec()` 成新程序 → 父进程 `wait()`。

### 排查命令（都能跑）

```bash
# 1. 找僵尸进程
ps -eo pid,ppid,stat,cmd | awk '$3 ~ /Z/'

# 2. 看进程树，搞清楚僵尸的爹是谁（罪魁祸首）
pstree -p -s <僵尸pid>
ps -o pid,ppid,stat,cmd -p <僵尸pid>   # PPID 那列就是它爹

# 3. 僵尸的爹如果还活着 → 修父程序（加 wait/SIGCHLD 处理）
#    僵尸的爹如果死了 → 不可能，孤儿会被 init 收养自动清理
#    想强清僵尸：只能杀掉它爹，让 init 接管
kill -9 <父进程PID>

# 4. 写代码时正确姿势（C）
while (waitpid(-1, NULL, WNOHANG) > 0);   // 非阻塞收割
// 或者忽略 SIGCHLD，让内核自动收尸
signal(SIGCHLD, SIG_IGN);
// Linux 专有：设 SIGCHLD 为 SA_NOCLDWAIT 也能避免僵尸

# 5. D 状态（不可中断睡眠）排查 —— 多半是 IO 卡死
ps -eo pid,stat,wchan:30,cmd | awk '$2 ~ /D/'
cat /proc/<pid>/stack    # 看内核栈，定位卡在哪个文件系统/驱动函数
iostat -x 1              # 看磁盘是不是 100% util 卡死了
```

### 修复方向
- **写多进程程序**：父进程必须 `wait`/`waitpid`，或显式 `signal(SIGCHLD, SIG_IGN)` 让内核自动收尸。
- **用线程池/协程**替代无脑 fork，从源头减少进程数。
- **D 状态**：排查底层 IO（NFS 卡死、磁盘坏道、内存不足导致换页风暴），必要时升级内核修复已知的 D 状态 bug。
- **运维兜底**：cron 定时清理、设 `ulimit -u` 限制单用户进程数，防止僵尸打满进程表。

### 一行本质
> **僵尸 = 进程已死但爹没收尸；杀不掉要么是它已经死了（僵尸），要么是它卡在内核不可中断 IO（D 状态）。**

**xv6 对应**：`kernel/proc.h` 的 `enum procstate`（状态机）、`kernel/proc.c:exit()`（变僵尸）、`kernel/proc.c:wait()`（收尸）、`kernel/proc.c:kill()`（打标记非真杀）、`kernel/exec.c:exec()`（fork-exec 的后半段）。

---

## 四、文件写了一半没了 / 缓冲没刷

### 事故现场
程序里 `fwrite` 写完 100MB 日志，函数返回了，立刻 `kill` 进程。重启一看文件只有 8KB，剩下的全丢了。或者更惨：数据库突然断电，重启后数据损坏，半条事务写进去半条没写进去。

### 反推原理：page cache、write-back、fsync、日志

你调 `write(fd, buf, n)`，函数返回成功，**并不代表数据真的落盘了**。现代 OS 为了性能，在内存和磁盘之间塞了一大堆缓冲：

```
你的 write() → [用户态缓冲 stdio] → [内核 page cache] → [文件系统日志] → [磁盘]
                  ↑ fwrite 在这层        ↑ write 到这层就返回      ↑ 只有 fsync 才保证到这里
```

**第一层：用户态缓冲（stdio buffer）。** `fwrite`/`printf` 默认带缓冲，数据先攒在一个用户态 buffer 里（满 4KB 或换行或 `fflush` 才真正 `write`）。进程被 `kill` 时这个 buffer 里的数据直接蒸发。

**第二层：内核 page cache。** 你的 `write()` 系统调用到了内核，内核把数据写到 **page cache**（一段在内存里的"磁盘缓存"）就立刻返回成功。此时如果断电，数据全没。

**第三层：文件系统日志（journal/log）。** 像 ext4、xfs 这类日志文件系统，会先把"我要改什么"写进日志区，再改真正的数据区。崩溃后靠日志重放恢复一致性。但日志本身也在 page cache 里，没落盘等于没写。

**只有 `fsync(fd)` 才强制把该文件相关的脏页一路冲到磁盘**，返回后才算"真的存下来了"。

xv6 虽小，但完整地实现了这套"日志保证一致性"的思想。它的 `log.c` 用一个"先写日志、后写实际块、再提交"的协议（write-ahead logging）。所有文件操作都被 `begin_op()/end_op()` 包起来：

```c
// kernel/exec.c:24  任何文件系统操作都要被 begin_op/end_op 包围
begin_op();
if((ip = namei(path)) == 0){ end_op(); return -1; }
ilock(ip);
... // 干活
end_op();   // ← 这里才把本次操作的日志真正提交落盘
```

xv6 还有个 **buffer cache**（`bio.c`），相当于它的"page cache"：磁盘块先读到内存的 buffer 里，读写都在 buffer 上，由日志层负责择机写回。这就是"延迟写回"（write-back）策略的雏形。

**为什么不是 write-through（写穿）？** 因为性能。磁盘一次 IO 几毫秒，内存几十纳秒，差了十万倍。OS 攒一批写、合并、排序、一次性刷，效率高几个数量级。代价就是你必须显式 `fsync` 才有持久化保证。

### 排查命令（都能跑）

```bash
# 1. 看系统有多少脏页（dirty，还没落盘的数据）
cat /proc/meminfo | grep -E 'Dirty|Writeback|Cached'

# 2. 看某个文件被谁打开、打开了哪些
lsof /var/log/app.log
lsof -p 12345

# 3. 强制把所有脏页刷盘（谨慎，会卡 IO）
sync
# 查看还有多少没刷完
cat /proc/meminfo | grep Dirty

# 4. 追踪进程到底有没有调 fsync
strace -e trace=fsync,fdatasync,write -p 12345
# 如果你的"重要写"后没看到 fsync 调用 → 数据随时可能丢

# 5. 调内核脏页刷写策略（多久/多少脏页触发自动刷）
sysctl vm.dirty_ratio vm.dirty_background_ratio vm.dirty_expire_centisecs
# dirty_ratio=20 表示脏页占内存20%时，写操作会阻塞直到刷完

# 6. 观察磁盘实际写入压力
iostat -x 1    # 看 w/s（每秒写次数）、await（写延迟）
```

### 修复方向
- **关键数据**：写完立刻 `fsync(fd)`（数据库 WAL、配置文件、断点续传文件）。注意 `fsync` 目录也要做，否则新建的文件元数据可能丢。
- **正确用 stdio**：调 `fwrite` 后 `fflush(fp)` 把用户缓冲冲到内核，再 `fsync(fileno(fp))` 冲到磁盘。三步缺一不可。
- **原子写**：用"写临时文件 → `fsync` → `rename`"模式，`rename` 是原子的，崩溃后要么是旧文件要么是新文件，不会是半个。
- **别滥用 fsync**：每次写都 fsync 性能会暴跌（慢几十倍）。用批量写 + 周期性 fsync，或上数据库自带的 WAL。
- **数据库**：正确配置 `innodb_flush_log_at_trx_commit=1`（MySQL）、`synchronous_commit=on`（PostgreSQL）才保证事务持久。

### 一行本质
> **write 返回不代表落盘；write 只到内存，fsync 才到磁盘，这中间断电全丢。**

**xv6 对应**：`kernel/log.c`（write-ahead log 保证崩溃一致性）、`kernel/bio.c`（buffer cache，xv6 的"page cache"）、`kernel/exec.c` 中 `begin_op()/end_op()`（文件操作的事务边界）。

---

## 五、并发一高就崩

### 事故现场
压测单机跑 100 QPS 一切正常，上到 5000 QPS 偶发性出现诡异数据：计数器少加、余额对不上、链表出现环死循环、偶尔 segfault。单线程永远复现不了，加上 `-fsanitize=thread` 一跑就报 `data race`。

### 反推原理：并发、原子性、可见性、同步原语

并发 bug 的三大根源，本质都是**"多个执行流在抢同一份资源，而程序假设它们是顺序的"**：

**(1) 竞态（race condition）。** `count++` 看着是一行，CPU 上是三步：读内存、加一、写回。两个线程同时做，可能都读到旧值、都加一、都写回同一个数 → 少加了一次。这就是"非原子"。

**(2) 可见性 / 重排序。** CPU 和编译器为了快，会把指令重排序（只要单线程结果不变）。线程 A 写了 `data` 再写 `ready=1`，线程 B 看到 `ready==1` 却可能读到旧的 `data`——因为 A 那边 `data` 的写还没刷到 B 能看到的内存。需要**内存屏障**（memory barrier）来禁止重排序。

**(3) 死锁/活锁。** 见第二节，锁用错就是互相卡死或互相谦让。

OS 提供的同步原语，本质都是用**硬件原子指令**（如 `lock xadd`、`cmpxchg`/CAS、RISC-V 的 `amoswap`）在软件上搭出"看起来原子"的操作。xv6 的自旋锁就是用 RISC-V 的原子交换指令实现：

```c
// xv6 kernel/spinlock.c 的 acquire（标准实现，本仓库未含，见 upstream）
// 核心是 while(__sync_lock_test_and_set(&lk->locked, 1)) ; —— 原子交换，自旋等锁
void acquire(struct spinlock *lk) {
  push_off();                              // 关中断，防止中断里又抢这把锁
  while(__sync_lock_test_and_set(&lk->locked, 1) != 0) ;  // 原子CAS自旋
  __sync_synchronize();                    // 内存屏障，保证后面的读看不到旧值
  ...
}
```

为什么要 `push_off()` 关中断？因为如果持锁期间来了时钟中断，中断处理程序也要拿同一把锁，就死锁了。**自旋锁的持有期间必须关中断**，这是多核 OS 的铁律。

xv6 用锁的地方遍布全代码：`kalloc` 用 `kmem.lock` 保护空闲链表、`pid` 分配用 `pid_lock`、每个进程用 `p->lock`。看分配 PID 这段，对比"加锁 vs 不加锁"：

```c
// kernel/proc.c:77  allocpid —— 必须加锁，否则两个进程可能拿到同一个 pid
int allocpid() {
  int pid;
  acquire(&pid_lock);          // ← 没这把锁，nextpid++ 就有竞态
  pid = nextpid;
  nextpid = nextpid + 1;
  release(&pid_lock);
  return pid;
}
```

**锁粒度是门艺术**：锁太粗并发上不去（一个全局大锁 = 退化成单线程）；锁太细容易死锁、维护成本高。Linux 从早期"大内核锁 BKL"演化到现在的细粒度锁（每对象一把锁、RCU 无锁读），就是这个权衡过程。

### 排查命令（都能跑）

```bash
# 1. C/C++ 编译期加检测，一跑就报 race
g++ -fsanitize=thread -g your.cpp -o your    # ThreadSanitizer，报数据竞争
valgrind --tool=helgrind ./your_binary       # 报锁顺序冲突，能定位死锁

# 2. 内存问题（越界、use-after-free，并发下也常触发）
valgrind --tool=memcheck --track-origins=yes ./your_binary
g++ -fsanitize=address -g your.cpp -o your   # AddressSanitizer，又快又准

# 3. 性能分析，看锁竞争热点（哪个函数耗时、在哪自旋）
perf record -g -p 12345 -- sleep 10
perf report
perf top -p 12345    # 实时看热点，__mutex_lock_slowpath 多半就是锁瓶颈

# 4. UPROF（Java）/ pprof（Go）看锁竞争
go tool pprof http://localhost:6060/debug/pprof/mutex   # 需先开 mutex profiling
jstack 12345 | grep -A5 BLOCKED                          # 看阻塞的线程

# 5. 看进程/线程数，确认没因为线程爆炸导致调度抖动
ps -eL | wc -l
cat /proc/12345/status | grep Threads
```

### 修复方向
- **优先用语言级高层抽象**：Go 的 channel、Rust 的所有权 + Send/Sync、Java 的 `java.util.concurrent`（`AtomicLong`、`ConcurrentHashMap`、`ReentrantLock`）。它们把"哪里要加锁、加什么锁"封装好了，比手搓 `pthread_mutex` 安全得多。
- **减少共享**：并发最高效的同步是"不共享"。用 per-thread / per-core 的本地变量、无锁队列、消息传递代替共享状态。
- **不可变对象**：只读不改的东西天生无竞态。函数式思路（copy-on-write）在并发里很值钱。
- **细粒度 / 无锁**：热点路径用 CAS（`std::atomic`/`sync/atomic`）代替互斥锁；读多写少用 RCU/读写锁。
- **分层加锁防死锁**：全局规定锁顺序；用 `trylock` + 超时；用工具（TSan/Helgrind）回归测试。

### 一行本质
> **并发 bug = 多个执行流在抢共享资源，而程序假设了本不存在的"顺序"；解法是用同步原语强制顺序，或干脆不共享。**

**xv6 对应**：`kernel/spinlock.c`（自旋锁，基于 `amoswap` 原子指令）、`kernel/proc.c:allocpid()`（加锁保护共享计数器）、`kernel/proc.c:sleep()/wakeup()`（条件等待，配合锁解决丢失唤醒）、`kernel/proc.c:sched()` 的 panic 检查（锁正确性断言）。

---

## 六、IO 慢得像蜗牛

### 事故现场
服务平时接口 10ms，一到业务高峰就飙到 3 秒。`top` 看 CPU 不忙、内存不紧，`iostat` 一看磁盘 `%util 100%`、`await 200ms`。或者：日志写一写程序整体卡顿，`strace` 一堆 `write` 系统调用。

### 反推原理：系统调用开销、缓冲、零拷贝、IO 模型

IO 慢有四个层次的原因：

**(1) 系统调用太频繁。** 每次 `read`/`write` 都要：用户态切内核态（上下文切换）→ 内核处理 → 切回来。一次切换几百纳秒到几微秒。如果你一字节一个 `write`，光切换就把 CPU 跑满了。xv6 的 `write` 系统调用要经过 `uservec → usertrap → syscall → sys_write → ... → usertrapret`，这一套在真实 Linux 上更重。

**(2) 用户态缓冲没用好。** 见第四节，`fwrite` 有 4KB 缓冲，`write` 没有。直接 `write(fd, buf, 1)` 一万次 vs 攒成 4KB `write` 一次，能差上百倍。

**(3) page cache 命中率低 / 换页风暴。** 内存不够时 OS 把 page cache 挤掉去换页，导致本该命中缓存的读变成真实磁盘 IO。或者反过来，大量写产生巨量脏页，刷盘跟不上。

**(4) 数据在内存里搬来搬去。** 经典场景：从磁盘读文件 → 内核 buffer → 拷到用户态 → 再拷回内核 socket buffer → 网卡发出去。一份数据拷了四次。**零拷贝（zero-copy）**技术（`sendfile`/`mmap`/`splice`）就是干掉这些无谓拷贝的。

xv6 里你能直接看到"用户态 ↔ 内核态"数据拷贝的原始实现：

```c
// kernel/vm.c:463  copyin —— 从用户地址空间拷贝到内核，每次最多一页
int copyin(pagetable_t pagetable, char *dst, uint64 srcva, uint64 len) {
  while(len > 0){
    va0 = PGROUNDDOWN(srcva);
    pa0 = walkaddr(pagetable, va0);     // 翻译用户虚拟地址到物理地址
    n = PGSIZE - (srcva - va0);
    if(n > len) n = len;
    memmove(dst, (void *)(pa0 + (srcva - va0)), n);  // ← 逐页拷贝
    len -= n; dst += n; srcva = va0 + PGSIZE;
  }
  return 0;
}
```

每次 `read`/`write` 都得这么拷一遍。这就是为什么 Linux 后来搞了 `copyin_new`（xv6 pgtbl lab 里就是优化这个，让内核页表直接映射用户页，省一次 `walk`）。生产里 `sendfile(out_fd, in_fd, ...)` 让内核直接把文件页搬到 socket，全程不进用户态。

**IO 模型的演化**，本质都是"怎么让等待 IO 时不浪费 CPU"：
- **阻塞 IO**：`read` 没数据就睡，简单但一个连接占一个线程。
- **非阻塞 IO**：`read` 立刻返回（没数据返回 EAGAIN），得轮询，浪费 CPU。
- **IO 多路复用**（`select`/`poll`/`epoll`）：一个线程盯一堆 fd，谁就绪通知谁。这是 Nginx/Redis/Netty 高并发的核心。
- **异步 IO**（`io_uring`/Linux AIO）：连"就绪通知"都省了，直接"完成了通知我"，内核和用户态通过共享环形缓冲区通信，零拷贝 + 批量提交。

### 排查命令（都能跑）

```bash
# 1. 磁盘整体压力（最常用）—— 看 %util、await、w/s、r/s
iostat -x 1
# %util≈100% 说明磁盘打满；await 持续高说明队列堆积；svctm 是单次服务时间

# 2. 谁在狂读写磁盘（按进程）
iotop -oP          # 实时看每个进程的读写速率（需要 root）
pidstat -d 1       # 更稳定的替代

# 3. 看进程到底在调哪些 IO 系统调用、每次多大、耗时多少
strace -p 12345 -e trace=read,write,fsync -T -tt
# 如果看到一堆 write(fd, buf, 8) → 罪魁就是"没缓冲，碎调用"

# 4. page cache 命中率 / 内存是否在换页
cat /proc/meminfo | grep -E 'Cached|Buffers|SwapTotal|SwapFree'
vmstat 1           # si/so 列非零 = 在换页风暴，磁盘被换页打满
sar -B 1           # 详细换页统计

# 5. 文件级别的缓存命中（用 pcstat 看某文件多少在 cache）
# pip install pcstat; pcstat app.log   # 显示每个文件在page cache的百分比

# 6. 网络零拷贝是否启用（Nginx 等）
strace -p <nginx_pid> -c -e trace=sendfile,write   # 看到 sendfile 多 write 少就是对的
```

### 修复方向
- **合并 IO**：用缓冲（`setvbuf`/`BufferedWriter`），攒一批再写；批量接口优于循环单条。
- **用对 IO 模型**：高并发用 `epoll`（C/Java NIO/Netty）/ `kqueue`（Go 底层）/ `io_uring`；别用一连接一线程的阻塞模型扛 C10K+。
- **零拷贝**：发文件用 `sendfile`（Nginx 的 `sendfile on`）；大块共享内存用 `mmap`；管道间用 `splice`。
- **治换页风暴**：加内存、限 swap（`swappiness=1`）、给数据库设 `O_DIRECT` 绕过 page cache（自己管缓存更可控）。
- **异步化**：日志用单独线程 + 内存队列异步刷盘；慢操作（落库、发邮件）扔进队列或线程池，别阻塞主流程。
- **硬件**：HDD → SSD → NVMe，IOPS 差几个数量级；随机写多的场景上 NVMe + 关闭 atime。

### 一行本质
> **IO 慢 = 要么调用太碎（系统调用开销 + 没缓冲）、要么真磁盘打满（缓存失效/换页风暴）、要么数据搬太多次（没零拷贝）。**

**xv6 对应**：`kernel/vm.c:copyin()/copyout()`（用户↔内核数据拷贝的开销源头）、`kernel/pipe.c`（管道，xv6 的缓冲 IO 雏形，标准 upstream 文件）、`kernel/virtio_disk.c`（块设备驱动，IO 的最底层，标准 upstream 文件）。

---

## 附录：把它们串起来的学习路径

1. **先建立状态机直觉**（南京大学 OS 核心方法论）：进程 = 状态机，调度器 = 在状态机间搬运，所有 bug 都是"状态机的非法跳转"。
2. **精读 xv6 源码**（MIT 6.S081）：本文引用的 `proc.c`/`vm.c`/`kalloc.c` 加起来不到 1500 行，却完整覆盖了进程/内存/锁/文件。配 11 个 lab（lazy paging、COW、multithreading），动手能力直接质变。
3. **对照生产系统**：xv6 是"裸"实现，Linux 是它的工业化版——空闲链表→伙伴系统、自旋锁→多种锁+RCU、缓冲→page cache+slab。理解 xv6 后读 Linux 源码会有"原来如此"的通透感。
4. **用事故反向巩固**：每遇线上诡异问题，都回头问"xv6 里这块怎么做的，Linux 为什么这么改"。这才是把 OS 学成肌肉记忆的方式。

> 注：本文 xv6 引用基于 `PKUFlyingPig/MIT6.S081-2020fall`（含 pgtbl/lab 修改）。标"标准 upstream 文件"（`spinlock.c`/`bio.c`/`log.c`/`pipe.c`/`virtio_disk.c`）在标准 xv6-riscv 仓库中，本课程仓库未含（学生未修改），路径文件名一致。所有命令在常见 Linux（procfs / util-linux）下可直接运行，遇权限加 `sudo`。

---

## 🎤 费曼挑战（真懂了吗？）

> 费曼法：能讲给小学生听才算真懂。用 `python3 tools/feynman.py --source os` 记录。

### 挑战 1：OOM Killer（对应 §一）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | 向运维解释"Linux 为什么不让你 malloc 失败，而是直接杀进程" | 说出 overcommit 机制 |
| L2 联系 | 你的服务被 OOM Kill 过吗？当时 RSS 是多少？ | 能用 smaps 解释 |
| L3 创造 | 写一个内存监控脚本，在接近 OOM 前报警 | 读取 /proc/meminfo |
| L4 教学 | 用"银行超贷"比喻向非技术人员解释 OOM Killer | 小孩能复述 |

### 挑战 2：死锁四条件（对应 §二）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | 背出死锁的四个必要条件 | 互斥/占有等待/不可剥夺/循环等待 |
| L2 联系 | 你代码里哪里有潜在的死锁？ | 指出锁顺序问题 |
| L3 创造 | 写一个一定会死锁的程序，然后用 pstack 检测 | 两个线程交叉锁 |
| L4 教学 | 用"十字路口堵车"比喻向小孩解释死锁 |

### 挑战 3：fork-exec-wait（对应 §三）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | 解释僵尸进程是怎么产生的 | 子进程死了但父进程没 wait |
| L2 联系 | 你的服务有僵尸进程吗？怎么检查？ | ps Z 或 /proc/pid/stat |
| L3 创造 | 写一个永远不会产生僵尸的 shell（用 SIGCHLD） | signal + waitpid |
| L4 教学 | 解释"为什么 fork 后子进程的 fd 不能自动关闭" | FD_CLOEXEC 的意义 |

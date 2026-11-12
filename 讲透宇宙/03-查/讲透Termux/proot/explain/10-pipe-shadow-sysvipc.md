# 10 · 管道读端影子与 SysV IPC 仿真：pipe_shadow.c + sysvipc.c（L09 重型仿真）

> 图谱锚：L09 重型仿真扩展。锚均现场核实于 /usr-data/data2/repos/termux-repo/proot@b27d81a。**勘误钉版：pipe_shadow.c 实际位于 `src/syscall/pipe_shadow.c`（293 行），不在 src/tracee/ 下**；pipe_shadow.h:29-61 注释即全模块设计书。

## 一、角色定位

这对模块是 Termux fork 的两条"内核补丁式"路线，上游 proot-me 均无：**pipe_shadow.c 治 ptrace 自己制造的病，sysvipc/ 治 Android 内核阉割掉的功能**。

pipe_shadow 是防 EPIPE 保险丝。ptrace 序列化 guest 行为：本该并发的"父进程关读端"与"子进程写管道"，在 proot 下变成父进程的 close() 先放行——若父是最后读者，管道瞬间零读者，子进程 write(2) 拿 EPIPE，bash 对 `echo <(echo a)` 打 "Broken pipe"（pipe_shadow.c:26-30 注释）。无 proot 时几乎不输的竞态被 proot 拉成必输。修法：在 close() 入口 proot 替自己多开一份读端引用，替子进程扛过窗口（:32-36）。

sysvipc 是 System V IPC 用户态仿真器（sysvipc.c 370 行 + msg/sem/shm 三件 + internal.h）。Android 沙箱 seccomp 禁绝 msgget/semop/shmat 等调用，guest 发行版的 php/wine 一调即死。它拦全部 12 个 SysV IPC 调用（sysvipc.c:19-33），消息队列与信号量在跟踪器内存纯软件实现，共享内存借 memfd + SCM_RIGHTS 真映射。

## 二、内部结构

### 2.1 pipe_shadow：静态槽位表 + 三把回收尺子

零动态分配：`Shadow shadows[32]`（pipe_shadow.c:77,101）静态槽位，fd==-1 即空闲（:111-112）。三常量定节奏：影子寿命 `SHADOW_MAX_AGE_MS=1000`（:83，过期影子=人工续命管道）、事件循环定时器 `SHADOW_TIMER_MS=50`（:88）、探测限频 `SHADOW_REAP_INTERVAL_MS=25`（:94，TIMER/2 保证一 tick 必有一轮探测）。

**开影子（shadow_pipe_read_end，:165-223）两道验证**：①readlink `/proc/<pid>/fd/<n>` 须以 `pipe:[` 开头（:184）；②读 fdinfo 的 flags（:188-198），`(flags & O_ACCMODE)==O_RDONLY` 确认读端（:200-201）。随后 `open("/proc/<pid>/fd/<n>", O_RDONLY|O_CLOEXEC)` 在 proot 进程空间取引用（:215）。全程不读一字节：数据留在管道缓冲等真读者（diff、cat），影子只是引用计数 +1（:211-213）。

**收影子（shadow_pipes_reap，:225-269）三关任一命中即 release**（close+还槽，:116-121）：

1. **POLLHUP**（:246-253）：poll(timeout=0) 且 events=0 只等挂起；读端 POLLHUP 当且仅当所有写端已关——对手退场。
2. **管道满**（writer_would_block，:145-163）：F_GETPIPE_SZ 取容量、FIONREAD 取在缓冲字节，`buffered > capacity - PIPE_BUF` 判满（:162）。原理（:140-143）：内核保证 ≤PIPE_BUF 写原子落地，空间不足直接停写者。此刻不撤影子，写者永远等不到读者，`yes | head -1` 与 mandb 解压大手册就从"该死的 EPIPE"变成"永远堵死的 write"（:40-44 原始事故）。
3. **1s 超龄**（:265-267）：兜底——窗口早过，槽位仅 32 个。

设计公理（:48-51）：释放影子永远安全——它是多余引用，真读者握着自己的。

### 2.2 sysvipc：三张表 + 两台状态机 + 一个 helper

**数据面三张表**（internal.h）：namespace 级数组 shms/queues/semaphores（:105-113），元素带 key/generation/valid（:88-92）。IPC id 编码 `(index+1) | (generation<<12)`（:224-225），LOOKUP_IPC_OBJECT（:210-222）校验索引与代数；IPC_RMID 后 generation+1（sysvipc_shm.c:291）令旧 id 失效——对齐内核代际语义。

**shm 段映射表是双锚点设计**：`SysVIpcSharedMemMap`（internal.h:52-85）同挂两条 LIST——`link_shmid` 入段级 `SysVIpcSharedMem.mappings`（IPC_RMID 与 nattch 统计视角），`link_process` 入进程级 `SysVIpcProcess.mapped_shms`（shmdt 与 execve 清场视角）。map 记 addr/size/ipc_namespace/shm_index（:53-74），size==0 表示"已登记、mmap 还在链上"的 pending 态（:57-58；sysvipc_shm.c:431 靠它找回映射）。进程结构按线程组共享：CLONE_THREAD 时子 Tracee 引用父 config 的 process（sysvipc.c:189-190），fork 才深拷贝（:192-196）；execve 时 SYSCALL_ENTER_END 全量拆映射（:204-213）。

**等待状态机**解决"纯用户态仿真里 tracee 要等内核对象"：wait_reason 是业务原因（等消息/等信号量/等 shmat 串行，internal.h:115-120），wait_state 是六态机制（:122-129）。sysvipc_syscall_common（sysvipc.c:36-128）三出口：同步完成者改写 getpid 桩（:121-125，结果由 status_after_wait 谎报）；需阻塞者改写 ppoll 挂起（:101-115，超时从 semtimedop 第四参透传 :59-61）；唤醒走 sysvipc_wake_tracee（:356-370）——对方已真进 ppoll 则 `tkill(pid, SIGSTOP)` 拽出（:361-364），SIGSTOP_IGNORED 吞掉自产 SIGSTOP。超时与被唤在 SYSCALL_EXIT_START 合流回填（:250-294）。

**链式状态机**（CSTATE_*，internal.h:131-139）只服务 shmat：socket→connect→recvmsg→mmap 四连击、后步依赖前步，靠 chain.c 的 register_chained_syscall 推进。

## 三、外部连接

pipe_shadow 三个挂点：①enter.c 的 PR_close（enter.c:3039-3057）在 fd 释放前调 shadow_pipe_read_end（:3056），同 case 顺带清 auxv_fd 与 netlink 跟踪（:3042-3050）；②event.c 主循环每轮 waitpid 前 reap（event.c:405）；③持影子期间 arm ITIMER_REAL（:413）。

sysvipc 走标准扩展协议：INITIALIZATION 建 config（sysvipc.c:161-177，libandroid 开关 :166-170）、INHERIT_CHILD 定共享边界（:182-202）、GUEST_PATH 仿真 `/proc/sysvipc/shm`（:335-341，fill_proc 按 ipcs(8) 列印，sysvipc_shm.c:706-745）、filtered_sysnums 交 seccomp 布防（:175；被拦调用触发 SIGSYS，走 from_sigsys=true 的同一 common 函数 :243-248）。CLI 侧 `--sysvipc`（proot.c:310-320）挂扩展；`--shm-helper`（cli.c:457-458）是同二进制第二人格，直进 helper 主循环；WITH_LIBANDROID_SHMEM 决定兼容层，`PROOT_DONT_SHARE_LIBANDROID_SHMEM` 可关。

## 四、数据流

**影子管道全旅程**：guest 父进程 close(fd) → enter.c:3056 影子开在 fd 释放前（close 放行后 /proc 路径即失效）→ 父 close 真执行，读者数=1（只剩影子）→ 子 write 成功，数据滞留缓冲 → 按二节三条件之一释放，写者最终拿 EPIPE 或被真读者消化。**定时器协作**：持影子期间每轮 setitimer(ITIMER_REAL, 50ms)（event.c:413 → pipe_shadow.c:284-286），waitpid 被打断（EINTR，event.c:421-423）回循环顶再 reap，返回即拆（:418）。SIGALRM 处理器是空函数（event.c:182-184），sigaction 只设 SA_SIGINFO 不设 SA_RESTART（:382-384）——waitpid 必须真打断而非自动重启，否则 blocked writer 不产生任何 ptrace 事件、循环睡死（pipe_shadow.h:55-60 明言契约）。

**shmat 四段链**：①shmget（sysvipc_shm.c:199-273）按 key 查表，未命中且带 IPC_CREAT 则发 SHMHELPER_ALLOC（:245-251），helper 端 sysvipc_shm_do_allocate（:777-815）Android 上优先 memfd_create（:783，Android 10+ 打不开 /dev/ashmem）回退 ashmem（:791-805），非 Android 用 tmpfile；fd 留 helper，proot 只记账。②shmat（:342-425）先双链登记 pending 映射（:401-406），再查并发串行化（:411-416，有同道在链上则排队），改写 socket(AF_UNIX, SOCK_SEQPACKET)。③sysvipc_shmat_chain（:438-554）接力：SOCKET 态收 fd、把 helper 套接字地址写进 guest 栈（:450-457）→ CONNECT 态发 SHMHELPER_DISTRIBUTE（:473-477）并注册 recvmsg → helper 端 accept 后把 memfd 塞进 SCM_RIGHTS sendmsg 出去（:883-913）→ RECVMSG 态读回 cmsg 校验取 fd（:491-506），页对齐注册 mmap2（64 位用 mmap，:508-515），**MAP_SHARED 是灵魂**——同一 memfd 多份映射才真共享 → MMAP 态收地址补全 mapping（:524-526）、链式 close 中间 fd、force_chain_final_result 把 mmap 返回值谎报成 shmat 返回值（:528-530）。④shmdt（:556-571）反查 mapped_shms，改写 munmap + talloc_free 触发析构（:295-325）从双链摘除；末位映射消失且 rmid_pending 才真发 FREE（:300-304）——IPC_RMID 在仍有映射时只立旗（:92），复刻内核"段延迟到 nattch==0 才销毁"。

## 五、设计决策

**一：影子必须自证短命**（pipe_shadow.c:38-51）。多数实现开个引用完事，这里反问"谁替 yes|head 的写者解套"：POLLHUP 与管道满是语义条件（对手退场 / 再留即有害），超龄只是槽位兜底；假阳性无害（提前释放=竞态复发=回到 proot 前，:142-143）。

**二：借 ITIMER_REAL 而非专用线程做心跳**。blocked writer 不产生 ptrace 事件，循环必须自我唤醒；SIGALRM+不可重启 waitpid 是单线程 proot 最小改动解。细节：限频 25ms 严格小于 tick 50ms（:90-94 保证 tick 不落空）；arm/disarm 紧贴 waitpid 前后，不干扰 ptrace 仿真层自己的 wait4（event.c:410-412）。

**三：fd 放 helper、SCM_RIGHTS 过桥**。memfd 开在 proot 进程无法变成 guest 地址空间映射；helper 反向 accept guest 发起的连接，fd 用 SCM_RIGHTS 发进 guest 内核态套接字缓冲，recvmsg 链在 guest 上下文执行，fd 天然落进 guest fd 表——**借 guest 自己的 syscall 执行能力完成 fd 移交**。代价是四连击 chain 与 helper 单线程串行（wake_pending_shmat 排队，sysvipc_shm.c:327-340）。

**四：ppoll/getpid 双桩包装等待**。把用户态仿真的阻塞翻译成真 syscall 让内核代挂起：信号语义、EINTR、多 tracee 并发全免费。seccomp 与非 seccomp 两条进入路径（from_sigsys）共用 common（sysvipc.c:95-119）。

**五：libandroid-shmem 生态兼容**（sysvipc.c:166-170）。Termux 存量 NDK 程序已用 libandroid-shmem 的 ashmem 后端，两种内存对象须同 id 空间互通，故 shm_use_libandroid 分支让请求直通 helper 里的真 libandroid 调用（sysvipc_shm.c:916-951）。

## 六、新人提示

1. **改回收逻辑先跑 `yes | head -1` 与 `echo <(echo a)`**：前者验管道满回收不 hang，后者验 EPIPE 消失——天然回归对。
2. **动 sysvipc 前先画状态表**：wait_state 六态 × wait_reason 四值 × chain_state 七值的合法组合全由 assert 把守（sysvipc.c:87-90,239,266,292），assert 崩即状态机走错格，别删 assert。
3. **helper 是另一个进程**：与 proot 间只有两条管道 + 一个 unix socket，协议是定长 SysVIpcShmHelperRequest（sysvipc_shm.c:860-872 校验长度）；其 stderr 带 "proot-shm-helper:" 前缀。
4. **别扩大 filtered_sysnums**：每加一个被拦调用多一次 seccomp 停机；pipe_shadow 不进这张表正因 close 超高频——它在 enter 翻译路径顺带完成（enter.c:3056），零额外停机。

> 本篇覆盖 L09 重型仿真扩展两大 Termux 特色件；fake_id0（07 篇）与 link2symlink（08 篇）同层，扩展框架协议见 06 篇，链式 syscall 见 03/04 篇。

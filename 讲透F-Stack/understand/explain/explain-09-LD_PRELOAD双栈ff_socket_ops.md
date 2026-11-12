# explain-09 · LD_PRELOAD 双栈适配：adapter/syscall/ff_socket_ops.c（请求-应答服务端）

## 角色定位

存量 Linux 应用零改造接入 F-Stack 的完整链路是：libff_syscall.so 经 LD_PRELOAD 劫持约 40 个 socket 类调用（ff_hook_syscall.c，3445 行）→按 fd 归属分流：内核 fd 走 ff_linux_syscall 直接真 syscall，F-Stack fd 则把调用打包成请求→跨进程送进 fstack 主进程→主进程的 main_loop 每圈调 ff_handle_each_context 处理请求→ff_socket_ops.c（752 行）就是**服务端的执行器**：ff_so_handler（`:434`）一个 switch 摊开全部 FF_SO_* 操作码，逐个解包参数、转调 lib 的 ff_socket/ff_bind/ff_epoll_wait…，再把 result/error 写回共享上下文。一句话：hook 层是"总机转接"，本文件是"坐席办事"。

## 内部结构

文件三段：① ff_sys_* 执行函数约 35 个（`:125-431`），全部是薄包装——ff_sys_socket 直接 ff_socket(args->domain,...)（`:127`）；特殊的三个：ff_sys_bind（`:131`）先查 ff_bound_fds 表（8 槽，`:42`），同地址已被别的 fd 绑过就直接 ff_dup2 复用（`:135-137`），成功才 sockaddr_bind 登记——多进程 SO_REUSEPORT 场景下避免重复绑定的语义修补；ff_sys_epoll_wait/kevent（`:306/:354`）额外维护 sem_flag 决定何时唤醒应用（有事件立即回、timeout<0 阻塞到有事件）；ff_sys_fork（`:382`）把 Linux 的真 fork 翻译成 fstack 侧 ff_adapt_user_thread_add 造新线程复刻 fd 表。② ff_so_handler 分发器（`:434-511`，未匹配返回 EINVAL）。③ 服务循环两套实现：sem 模式 ff_handle_socket_ops（`:554`，trylock+状态机 FF_SC_IDLE→REQ→REP）与 FF_USE_RING_IPC 模式 ff_handle_socket_ops_ring（`:525`，SPSC 环免锁）；入口 ff_handle_each_context（`:622`）按 pkt_tx_delay 的 TSC 预算循环排空请求。

## 外部连接

上游两路：hook 进程侧的 ff_so_zone.c 在共享内存建 struct ff_socket_ops_zone（ff_socket_ops.h:89，含 sc 数组与状态字），sem 模式用信号量握手、ring 模式用 ff_ring_ipc.c 的 req_ring/rsp_ring（`:746-750` 注释：环形助手已抽到 ff_ring_ipc.c 供两侧共用）；请求提交宏 SYSCALL 在 ff_hook_syscall.c:134（ring 版：ff_ring_submit_and_wait 阻塞等待）与 :187（sem 版：ACQUIRE_ZONE_LOCK(FF_SC_IDLE)→置 REQ→等 REP，注释自曝"NOTE: deadlock prone while fstack adapter run error"）。fd 编址：hook 侧把 F-Stack fd 加 ff_kernel_max_fd 偏移（ff_hook_syscall.c:296 convert_fstack_fd，默认 FF_KERNEL_MAX_FD_DEFAULT、select 场景换大值 `:282-284`），is_fstack_fd（`:311`）按 >= 阈值判归属（注释 FIXED ME 承认 ff_linux_socket 未被约束在低位、可能误判）。下游 fstack.c：主进程 main_loop 每圈调 ff_handle_each_context；FF_USE_THREAD_STRUCT_HANDLE 打开时 ff_switch_curthread 切换 curthread（`:530`）——FreeBSD 栈 API 依赖 per-thread 上下文，服务不同应用线程必须换装。

## 数据流

以应用调 accept() 为例全链：LD_PRELOAD 命中 ff_hook_accept→is_fstack_fd(fd) 为真→DEFINE_REQ_ARGS(accept) 在共享 sc 里填参数→SYSCALL(FF_SO_ACCEPT,args)（sem 版：自旋等 sc 空闲，置 FF_SC_REQ 后让出；ring 版：入 req_ring 后睡在 rsp 环上）→fstack 主进程 main_loop→ff_handle_each_context（`:687-733`：先脏读 status==FF_SC_REQ 再 trylock 复核，按 drain_tsc 预算内循环；无请求时开锁窗 rte_pause 防止应用初始化抢不到 zone 锁被饿死，`:728-732`）→ff_handle_socket_ops：errno 清零、ff_switch_curthread、ff_so_handler→ff_sys_accept→ff_accept→（协议栈收包路径已在 explain-01/08）→result/error 写回 sc→FF_SC_REP+sem_post 唤醒应用（epoll_wait/kevent 有 sem_flag 特例：timeout=0 且无事件不置 REP，下圈继续问，`:587-615`）。fd 回到应用手上时已加 ff_kernel_max_fd 偏移，后续 send/recv 走同一管道，非 F-Stack fd（unix socket/文件）直接落内核——双栈就这样并存。

## 设计决策

① **同步阻塞语义跨进程重建**：应用期望 accept/send 是同步调用，而 fstack 是单线程 run-to-completion 循环——请求-应答+信号量/环把"应用的阻塞"翻译成"主循环的一次排空"，代价是每次 socket 调用一次跨核往返，这正是 adapter 模式 CPS 低于 native ff_api 的原因。② sem_flag 的事件节流（`:296-347`）：epoll_wait(0) 空轮询场景不反复握手，避免两边空转互踩——注释保留下来的 EVENT_LOOP_TIMES 实验代码（`:31-35`）是失败优化的墓碑。③ ring 模式（v3.3 D5+v3.4 D6 注释，`:643-652`）用 rte_ring_empty 空检+内联 dequeue burst 干掉函数指针间接调用与整层调用栈，且刻意复用 prod/cons 尾指针"不引入新共享缓存行"（明确记着被移除的 pending_count 方案 v3.2/H25）——性能注释诚实到记录失败尝试。④ ff_sys_bind 的 dup2 去重是给 SO_REUSEPORT 语义打的补丁：FreeBSD 栈重复 bind 同地址返回错误，而 Linux 应用（多 worker nginx）期望成功——8 槽静态表（FF_MAX_BOUND_NUM）够小，注释没解释上限依据，扩端口型应用要小心。

## 新人提示

调试这套 IPC 的三件套：DEBUG_LOG 开关在编译期（ff_socket_ops.c 顶部 DEBUG_LOG 宏），先确认请求真的到达服务端（ff_so_handler 的 ops 日志）再看结果回传；sem 模式卡死的典型是 fstack 主进程异常退出——SYSCALL 宏的注释已预警死锁；ring 模式则要同时看 req/rsp 两环的水位。fd 偏移体系（ff_kernel_max_fd）是全链隐形契约，select 编译用大偏移值（NFDBITS 位图容量），混用两套编译配置会 fd 判错。main_stack_epoll.c / main_stack_epoll_kernel.c 两示例分别演示纯 F-Stack 与双栈共存的最小骨架，先跑它们再读 fstack.c。ff_sys_fork 只建线程不复制栈状态，依赖 hook 侧父子各自 register——多进程应用的 fork 语义边界要实测验证。

# explain-10 · micro_thread 协程接口：adapter/micro_thread/mt_api.cpp（同步风格写异步）

## 角色定位

mt_api.cpp（1035 行）是腾讯 micro_thread 框架的 API 门面：把"协程调度 + 非阻塞 IO + 连接复用"封装成**带 timeout 参数的同步函数**——mt_tcpsendrcv(dst, pkg, len, buf, size, timeout, len_func) 一行完成建连（或复用）、发送、收包、判包，业务代码全程顺序流。有状态应用（游戏后台/微服务）不必写 epoll 状态机，也不用回调地狱。它同时是 micro_thread 与 F-Stack 的缝合点：mt_init_frame（`:573`）直接调 ff_init + ff_set_hook_flag，之后所有 IO 经 MtFrame 的 kqueue 代理在协程间调度。mt_api 是"应用的词汇表"（what），micro_thread.cpp/MtFrame 是"语法引擎"（how）。

## 内部结构

三组 API：① 一问一答族——mt_tcpsendrcv（`:210` 长连接版）/mt_tcpsendrcv_short（`:274` 短连接版）/mt_tcpsend/rcv 分离版（`:334/:387`）/mt_tcpsendrcv_ex（`:438` 按 MT_TCP_CONN_KEEP/SHORT 选路）；核心是 mt_tcp_check_recv（`:150`）：循环 MtFrame::recv 累积字节，每轮调用户传入的 MtFuncTcpMsgLen 判包函数（返回 -1 坏包 /0 还不够 /n 完整长度），超时预算随剩余时间收缩（`timeout - cost_time :157/:164`）。② 原语族——mt_connect/accept/read/write/recv/send/recvfrom/sendto（`:588-627`）全部一行转 MtFrame:: 同名方法，多带 timeout 参数；mt_sleep/mt_wait_events/mt_start_thread/mt_thread_wait/wakeup（`:628-663`）管理协程生命周期。③ 并行任务族——mt_exec_all_task（`:501`）：把 IMtTaskList 里每个任务 CreateThread 成 SUB_THREAD 子协程、全部入就绪队列、父协程 thread->Wait() 让出——醒来时全部子任务已并行跑完，scatter-gather 一行搞定（`:516-544`）。零拷贝变体（`:738-1035`）用 ScopedBuf 按 4096 对齐水位管理接收缓冲（`:672-677` 的 BUF_ALIGN 宏），收完直接移交指针免一次拷贝。

## 外部连接

向下两层：MtFrame（micro_thread.cpp）是调度器——就绪/IO/睡眠/挂起四链表 + heap_timer + kqueue_proxy 代理真实 ff_kqueue，KqueueSchedule 让出协程等事件；arch_ctx.S 提供汇编上下文切换。IO 分流在 mt_sys_hook.cpp：编译链接期覆盖全局 socket/connect/close 等（mt_sys_hook.cpp:132 socket→ff_hook_socket 并 mt_hook_new_fd 登记、随即 FIONBIO 置非阻塞），ff_hook.cpp:37 的 ff_hook_socket 再按 ff_hook_active() 决定走 F-Stack 还是内核——三层 hook 叠加（协程调度→双栈选择→真 IO）。向上：echo.cpp 是最小示范；mt_init_frame 的 argv 直通 ff_init（config.ini 全套生效），mt_set_stack_size（`:583`）调 ThreadPool::SetDefaultStackSize 控制每协程默认栈（切换即整栈换页，太大浪费内存太小爆栈）。

## 数据流

一次 mt_tcpsendrcv 的生命周期：参数校验（`:212`）→mt_tcp_get_keep_conn（`:120`）：NtfyObjMgr 领一个 THREAD 型通知对象、ConnectionMgr 按 dst 地址池里捞 TcpKeepConn（连接复用池的核心——同 dst 后续调用零建连）、CreateSocket 得非阻塞 fd→MtFrame::connect（`:234`，内部 KqueueSchedule 等 EPOLLOUT，非阻塞 connect 在协程世界"看起来是阻塞的"）→剩余时间预算算出后 MtFrame::send（`:244`）→mt_tcp_check_recv（`:254`）按用户判包函数凑整包→EXIT_LABEL（`:264`）按连接类型决定 FreeConnection 归还池还是真关闭。每个 MtFrame::xxx 的内部模式统一是：非阻塞系统调用→EAGAIN 则挂 kqueue 事件+协程让出→事件到达恢复重试→超时返回 ETIME。MtFrame 主循环（Schedule）在无就绪协程时 epoll 一轮拿新事件——整个框架是"N 协程跑在 1 个 OS 线程、阻塞点全被翻译成调度器让出"。

## 设计决策

① **timeout 参数化每个调用**而不是全局设置：每次调用自带预算（连接/发送/收包逐段扣减 `:242-253`），组合调用总时长可控——这是微服务超时传递的正确姿势，比 SO_RCVTIMEO 全局态好推理。② 判包函数 MtFuncTcpMsgLen 回调设计（`:178`）：框架不懂协议，"一个完整消息多长"由业务答——rc>0 表示还需 rc 字节、rc==0 未知、凑满 buf_size 仍不完整报 -6（`:186-189`）；这让通用收包循环无须复制粘贴。③ 连接池按目的地址键（OBJ_TCP_KEEP，`:129`）：短连接版每次 close（`_short` 后缀），长连接版归还池——调用方用后缀选语义，池化管理对业务透明。④ mt_exec_all_task 的父子协程模型（SUB_THREAD 类型 + AddSubThread + Wait）：并行 IO 任务的写法退化成"提交列表→等一觉"，与 mt_sleep 共用同一调度器，没有第二套并发原语。

## 新人提示

上手顺序：echo.cpp → mt_api.h 的注释（每个函数的负数错误码表都在头文件）→ mt_tcp_check_recv 的判包循环。三个高频坑：判包函数写错（返回值语义搞反）会在 `:178-204` 的循环里死转或提前断包，先用定长头（如 4 字节长度前缀）练手；timeout 传 0 是立即超时不是无限等，无限等用 -1（`recvfrom` 里 -1 映射 0x7fffffff，micro_thread.cpp）；micro_thread 与 adapter/syscall 的 LD_PRELOAD 是**两套互斥的接入方式**（前者链接期 hook 适合新开发，后者运行期注入适合存量程序），别在同一个进程混用。调试用 MTLOG_LOG_LEVEL 控制日志，协程栈溢出的表现为切换后数据莫名损坏，先调大 mt_set_stack_size 再查逻辑。

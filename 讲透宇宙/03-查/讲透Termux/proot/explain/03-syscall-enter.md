# 03 · syscall 翻译总控与 sysenter 主战场：syscall.c + enter.c

> 锚均经源码现场核实（仓 b27d81a）。syscall.c 350 行、enter.c 3069 行。

## 一、角色定位

`syscall.c` 是双阶段协议调度器：`translate_syscall()`（syscall.c:140）被事件循环四停机点调用（event.c:615），按 `IS_IN_SYSENTER`（tracee.h:202）劈成进入、退出两半，不翻译具体调用。`enter.c` 是 sysenter 主战场：`translate_syscall_enter()`（enter.c:1887）按中立 Sysnum 分派，把 guest 参数改写成 host 真实参数。核心契约：内核照常执行 syscall，proot 只在停机窗口改参数与结果。

enter.c 三段式：路径/挂载辅助群（enter.c:148-570）、伪造 netlink 子系统（enter.c:572-1826，约 1250 行占四成，Termux fork 最重增量）、主分派（:1887 起）。

## 二、内部结构

### 2.1 syscall.c：双阶段协议

进入分支三拍（syscall.c:176-180）：无链式队列先存 ORIGINAL，调 `translate_syscall_enter`，再存 MODIFIED。寄存器三版本（tracee.h:40-43）：ORIGINAL 原始请求、CURRENT 翻译现值、MODIFIED 进入定格。队列非空=proot 注入的链式调用，跳过翻译只发链式事件（syscall.c:181-186）。

错误协议：进入返回负 errno 时，总控统一改 void 并把错误值直接写进结果寄存器（syscall.c:191-198），tracee 不出内核即失败。

自答调用的保命机制：proot 亲自应答的调用（getcwd、mount 等）换号 SYSCALL_AVOIDER、当场写结果。默认 avoider 是 -2（arch.h:34），号改负即内核取消、结果保留；但 ARM 32 位是 222 号 tuxcall（arch.h:112），真到内核可能被 -ENOSYS 覆盖，必须置 `sysexit_pending` 强制二停、退出阶段补回伪造结果（syscall.c:219-222，判据 :131-138）。`is_voided_syscall()` 判"当前是 avoider 而原始不是"（syscall.c:108-119）。

改不动号的降级链（syscall.c:294-333）：推回失败且原始号≠当前号时，走 `restart_current_syscall_as_chained`（chain.c:182）重排链式，六参数全写 -1 赌内核拒掉（brk 传 0，:322-325）；`voided_syscall_cancelled` 告知事件循环内核不报 sysenter（:342-344）。

退出分支（syscall.c:246-284）：seccomp 快道 PTRACE_CONT 时提前还原栈指针（:240-244）。

### 2.2 enter.c 主分派：四类手法

先发 `SYSCALL_ENTER_START`，扩展返回>0 即整案移交（fake_id0/link2symlink 从此截胡，enter.c:1904），再按原始号进 switch（:1911）：

- 路径翻译类：`get_sysarg_path` 从 tracee 内存读路径（syscall.c:42-64），`translate_path2` 经 canonicalize 换成 host 路径写回（syscall.c:72-101，栈下分配+改指）。REGULAR/SYMLINK 由 flags 定：open 带 `O_NOFOLLOW` 或 `O_EXCL|O_CREAT` 不追末级链接（enter.c:2661-2665），`*at` 看 `AT_SYMLINK_NOFOLLOW`（:2689-2692）；创建型新路径只翻父目录不碰末分量，免得探测新名扰动老内核（:171-220）。
- 自答 void 类：getcwd（enter.c:1950-1954）、chdir/fchdir 整套仿真更新 `fs->cwd`（:1956-2026）、mount/pivot_root/umount 转成绑定表操作（:2586-2598/:483）、unshare/setns 谎报成功（:2510-2522）、prctl 全家（拒 PR_SET_DUMPABLE :2922-2926、封 SECCOMP 过滤器 :2939-2948、NO_NEW_PRIVS 改报自身意图防 sudo-rs 拒跑 :2964-2968）。
- 改写类：clone/clone3 剥全部 namespace 位让 fork 照常（enter.c:2542-2575，NEWNS/NEWNET 记账）；openat2 降级为 openat（:2774-2794）、新挂载 API 一律报 ENOSYS 逼 libmount 回退 mount(2)（:2607-2615）。
- 拒绝类：memfd_create 按名打击——`JITCode:` 逼 Qt 回退匿名 mmap、`opcache_lock` 逼 php8.3 回退 O_TMPFILE、`lib/apk/exec/` 逼 apk-tools v3 放弃 memfd+execveat，全报 EACCES（enter.c:3010-3038）。

两个小辅助：`force_fork_sysexit`（enter.c:118）修 aarch64 4.14 forking 调用走快道空转的怪病；`keep_pushed_args`（:135）让栈下参数活到退出，防信号打断重启读到垃圾。

### 2.3 伪造 netlink 子系统（enter.c:572-1826）

动机：Android SELinux 对 untrusted_app 拒发 netlink（enter.c:572-591），bubblewrap、glibc getifaddrs、iproute2 全遭殃。方案：`host_blocks_af_netlink()` 三段探测——socket、bind、无害 RTM_NEWADDR 探针（enter.c:614/623/654）；Android 只授读不授写，到 sendmsg 才 EACCES 的主机也正确归类；静态缓存探一次（:596）。替身链由 12 个 `nl_` 构造器加 22 个辅助共约 34 函数组成：

1. socket 改写：`socket(AF_NETLINK,*,NETLINK_ROUTE)` 改成 `AF_UNIX/SOCK_DGRAM`，置待登记标志（enter.c:2127-2149）；退出阶段由 exit.c:781-806 收进 `fake_netlink_fds`。只仿真 NETLINK_ROUTE，其余协议放行拿真错（enter.c:2119-2126）。
2. 发送截停：sendto/sendmsg 命中假 fd 根本不发，`build_fake_netlink_reply()`（enter.c:1416）就地合成应答存进该 socket 条目，写结果为发送长并 void（:2151-2225）。应答策略：RTM_GETLINK/GETADDR 用 getifaddrs 枚举**真实 host 接口**（`build_host_links`:1146 从 AF_PACKET 取权威 index/MAC；`build_host_addrs`:1250），失败回退合成 loopback；RTM_GETROUTE 亲自向内核发 dump 再中继、重写序号与 pid（`relay_route_dump`:1318）；其余 dump 给空 NLMSG_DONE、非 dump 给零错误 ack，保底 EINVAL 不留零应答（:1511-1524）。
3. 接收交付：按**数据报**逐给——NLMSG_DONE 终结符单独成帧复刻内核分帧，否则 fastfetch 这类"读到 DONE 才收手"的调用永远阻塞（`fake_netlink_datagram_len`:1542）。MSG_PEEK 不消费、MSG_TRUNC 报未截断长度（enter.c:2282-2284），按 iovec 散写，源地址伪造成 `nl_pid=0` 的内核 sockaddr_nl——glibc 只认内核来源（:2288-2290/:2353-2365），msg_flags 置截断位（:2372-2376）。队列空放行真读让替身自报阻塞，绝不伪造零长报文（:2266-2269）。
4. 周边圆谎：假 fd 的 bind 静默成功（enter.c:2036-2042）；getsockname/getpeername 手写 sockaddr_nl 兜住 iproute2 "地址长度 2" 报错（:2091-2102）；ioctl 的 SIOCGIFINDEX 在 tracer 代查、只碰两个定长字段避开 32/64 位结构体长度差（:1803-1826）；close 摘账防 fd 复用（:3049-3050）。

另一半——真 socket 加假 netns：clone 被剥 CLONE_NEWNET 后 tracee 自以为有网络命名空间（`fake_netns`，enter.c:2511），但真 socket 在宿主命名空间、无 CAP_NET_ADMIN，重配置必被 EPERM 拒。不替换 socket（保住真查询能力）：进入记下重配置请求序号（`note_netns_netlink_request`:1663；判据 `nl_type_reconfigures`:1643——四员一组 NEW/DEL/GET/SET，非 GET 即重配置），该 fd 的下一个接收停退出阶段（:1689-1696），由 `handle_netlink_reply_exit()`（enter.c:1705；exit.c:832 挂钩）把内核错误应答的 error 字段改 0（enter.c:1761）——ack 与序号都是真的，只有 error 撒了谎。

## 三、外部连接

- 上游：event.c 事件循环四处调用；reg.h 三版本读写与推回（reg.h:50/54）。
- 路径子系统：translate_path2 进 path.c:370 与 canon.c:199；挂载仿真操作绑定队列（enter.c:330）。
- execve/socket：PR_execve 转交 execve/enter.c:596；sockaddr_un 改写走 socket.c:150。
- 管道影子挂 close 防 EPIPE（enter.c:3056）。
- 扩展框架：进入/链式各两相事件出口（enter.c:1904/3064、syscall.c:183/273）。
- exit.c 消费：void 调用把进入定格结果回写结果寄存器（exit.c:81-82）；accept/getsockname 尺寸从 MODIFIED 取（:147-148）；fd 登记（:781-826）与 ack 改写（:832）。

## 四、数据流

例一 openat "/etc/hosts"：报停 → 存 ORIGINAL（syscall.c:177）→ 命中 case（enter.c:2797）→ canonicalize 得 host 路径 → 写栈下新块、改寄存器指向（syscall.c:78-88）→ 存 MODIFIED → 推回 → 内核真开文件 → 退出反向翻译。proot 全程未代执行任何 syscall。

例二 Android 上建 netlink socket：探测被拒 → 参数改 AF_UNIX 数据报（enter.c:2133-2135）→ 退出登记 fd（exit.c:781-806）→ 发 dump 命中假 fd → 合成应答、写结果并 void（enter.c:2159-2162）→ 内核空转 → 退出回写定格结果（exit.c:81-82）→ 接收再命中：散写、伪造内核源地址后 void（enter.c:2335-2379）。getifaddrs 就这样在 netlink 被禁的世界拿到真网卡表。

链式衔接：扩展/execve 用 `register_chained_syscall`（chain.c:41）排队；退出末尾 `chain_next_syscall`（syscall.c:282-283，chain.c:103）把队首六参数与号写进 CURRENT；下一停见队列非空即跳过翻译直通内核（syscall.c:176-186）；队列耗尽按需强制最终结果（chain.c:113-121）。

## 五、设计决策

1. 两停机改参数，不代理执行：proot 从不替 tracee 调 syscall——描述符、凭据、信号等内核态天然连续；代价是每调用两停，由 seccomp 只放行需翻译者摊薄（seccomp.c:109-112）。
2. 三版本寄存器与 void 加 avoider：MODIFIED 供退出回读进入改动；负号被内核取消（结果保住、无停机），ARM 的 222 真上内核必须补停——同一协议吸收跨架构 ptrace 差异。
3. 替身选数据报而非流式：数据报语义天然承载 NLMSG 分帧，才能逐报交付、复刻 PEEK/TRUNC；探测做到 sendmsg 一层，避免"能开就当能用"的误判。
4. 真数据优先假数据兜底：接口地址真值、路由 dump 中继真内核，仅 loopback 纯合成——谎言最小化。
5. 拒绝即引导：memfd 与新挂载 API"报错逼走备胎"而非硬仿真，复杂度还给上游库回退。

## 六、新人提示

- 阅读顺序：先通读 syscall.c 吃透双阶段三版本；再读 enter.c:1887 骨架（先跳过 572-1826）；最后整块啃 netlink，注释密度极高（enter.c:998-1010/:1529-1541）。
- 加新 syscall 处理器（本仓接受的 PR 类型）：switch 加 case、守 status 约定；写结果寄存器务必同置 void 号，否则内核返回值会盖掉答案；需退出跟进就置 `sysexit_pending` 加 SYSCALL 重启。
- 三个易踩坑：一，链式注入的调用不走进入翻译（syscall.c:176/265 两处判空）；二，`SYSNUM_WORKAROUND` 状态机（syscall.c:182/265-271）专治改不动号的架构；三，seccomp 快道栈指针提前还原（syscall.c:240-244），栈下参数存活依赖 `keep_pushed_args`。
- 测试：一缺陷一 hash 回归；netlink 替身对应 iproute2/getifaddrs/bubblewrap 三类消费方，改完务必真 Android 验证——裸 Linux 测不出 SELinux 分层拒绝。

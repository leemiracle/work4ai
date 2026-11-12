# 02 · Tracee 结构与生命周期：tracee.h + tracee.c（L02 运行时核心）

> 锚均现场核实于 /usr-data/data2/repos/termux-repo/proot@b27d81a（tracee.h 437 行、tracee.c 1053 行）。

## 1. 角色定位：PRoot 进程宇宙的档案卡与户籍科

PRoot 用单个 `ptrace()` 跟踪器监视整棵 guest 进程树：每个被跟踪的进程**或线程**在跟踪器内存里对应一个 `Tracee` 实例（tracee.h:75-414，80+ 字段）。知识图谱 76 条边指向 `file:src/tracee/tracee.h`，全仓 fan-in 第一——src/ 每个子系统都要回头问它"这个进程现在什么状态"。

这对文件不做翻译、不做事件分派（分别是 `syscall/`+`path/` 与 `event.c` 的活），只做三件事：**定义状态**（Tracee 是全部运行时状态的唯一容器：寄存器四版本缓存、绑定三队列引用、虚拟堆、ptrace 仿真会话、链式 syscall 队列）；**管理生命周期**（创建、继承、改名、死亡）；**维护父子配对**（pid 复用、vfork 时序倒置等内核边角）。event.c 是心脏起搏器，tracee.c/h 是血液本身。

## 2. 内部结构：按"共享边界"分区的档案卡

结构体注释把 340 行切成六分区（tracee.h:76-412），依据是**字段何时与父进程分离**——这是 clone 语义仿真的钥匙：

| 分区 | 行锚 | 语义 |
|---|---|---|
| 私有资源 | tracee.h:76-322 | 出生即自有：pid/vpid/status/寄存器/ptrace 会话/chain |
| 私有但继承 | tracee.h:324-362 | 出生拷贝：verbose/seccomp/pending_child/no_new_privs |
| 按 CLONE_FS/VM 共享 | tracee.h:364-372 | `fs`/`heap`：内核共享则引用，否则拷贝 |
| execve 前共享 | tracee.h:374-382 | `exe`：fork 后共享，直到子进程自己 execve |
| 按配置共享 | tracee.h:385-397 | `qemu`/`glue`/`extensions` |
| 只读共享 | tracee.h:400-412 | `host_ldso_paths`/`tool_name` |

关键构件：

- **双内存池**：`ctx`（tracee.h:261）是"事件跨度"池，一次 syscall 翻译的临时分配全落此，`get_tracee()` 命中即整池倾倒重建（tracee.c:336-338）；`life_context`（tracee.h:265）是"生命跨度"池，存绑定等活到进程死的对象（tracee.h:267-268 留有 event_span/life_span 更名备注）。
- **双面 ptrace 身份**：`as_ptracer`（tracee.h:163-176，含 zombies 队列与 waits_in 三态）与 `as_ptracee`（tracee.h:178-194）内嵌同一结构——任何 Tracee 可同时是 tracer 与被 tracer，嵌套 ptrace 仿真（gdb 跑在 proot 里）不需要第二套类型；`event4` 双事件槽（tracee.h:182-187）区分"PRoot 翻译停机"与"上报 guest tracer 的停机"。
- **四版本寄存器**：`_regs[NB_REG_VERSION]`（tracee.h:216）配 RegVersion 枚举（tracee.h:37-43）：CURRENT/ORIGINAL/MODIFIED/ORIGINAL_SECCOMP_REWRITE；`status` 三值编码（tracee.h:196-200）配 `IS_IN_SYSENTER`（tracee.h:202）。另有 `restart_how`（tracee.h:207-213）、`sigstop` 三态（tracee.h:235-239）、`terminated`（tracee.h:92-94 的 TODO 想换专用链表）。
- **vpid**（tracee.h:87）：64 位单调 ID，由 `next_vpid`（tracee.c:211）分发——pid 会被内核复用（attach_child 的 pid-reused 分支 tracee.c:738-743），vpid 不会，故日志全程用 vpid。

## 3. 外部连接：谁创建、谁消费、死时通知谁

**唯一事件入口**是 `event_loop()`（event.c:314）：`waitpid(-1,...,__WALL)` 拿 pid 后 `get_tracee(NULL, pid, true)` 现查现建（event.c:432），循环顶部 `free_terminated_tracees()`（event.c:401，注释明言唯一安全释放点）；fork 家族事件分派 `new_child()`（event.c:801/807），SIGSTOP 首停 Pending 在 event.c:819-830；进程真死调 `terminate_tracee()`（event.c:513/520）；syscall 停机交 `translate_syscall()`（syscall/syscall.c:140），它是 status/chain/_regs 的最大消费者。

**ptrace 仿真**反向依赖：`attach_to_ptracer`/`detach_from_ptracer`（ptrace/ptrace.c:104/116）操作 as_ptracee，`PTRACER`/`PTRACEE` 宏（ptrace/ptrace.h:33-34）就是两个内嵌结构的缩写。**扩展框架**经 `inherit_extensions`（extension.c:128）在 attach_child 尾声（tracee.c:963）逐扩展发 INHERIT_PARENT 协商继承。**绑定子系统**经 `clean_life_span_object` 回调（tracee.c:69-81）在析构时收到 `remove_binding_from_all_lists`（path/binding.c:277）通知。**CLI** 在 proot.c:197 给初始 tracee 设 `killall_on_exit=true`，首领一死触发 `kill_all_tracees()`（tracee.c:1043-1049）全表 SIGKILL。

考古：`swap_config()`（tracee.c:1027-1040）在 src/ 全树零调用者（grep 实证），是子重配置（`reconf` 字段 tracee.h:279-282）时代的历史 API。

## 4. 数据流：一个 Tracee 的一生

**出生三路**，全汇入 `attach_child(parent, clone_flags, pid)`（tracee.c:716）：

- **正路**：fork 事件带 child pid。`new_child()`（tracee.c:662）先重读寄存器确认真实 flags——事件类型会骗人（tracee.c:667-683，含 clone3 从 clone_args 首字取 flags），再 `PTRACE_GETEVENTMSG` 取 pid（tracee.c:699）直达 attach_child。
- **无 pid 岔路**：某些内核（注释点名 aarch64 4.14.357，tracee.c:691-698）把 event message 清零、pid 读成 0。存三字段 `pending_child/pending_clone_flags/pending_child_sp`（tracee.h:341-343）等回收：`resolve_pending_child()`（tracee.c:613）在父达 fork 系 syscall 的 sysexit 时从 `SYSARG_RESULT` 捞 pid（sysnum 白名单卡死 clone/clone3/fork/vfork，tracee.c:619-630）；`adopt_held_children()`（tracee.c:574）处理 vfork 时序倒置——父被卡住、孩子先跑到 SIGSTOP，只能从孩子侧认亲。
- **认亲算法**（`is_pending_child_of`，tracee.c:530）：读 `/proc/<pid>/status` 的 Tgid/PPid/TracerPid（tracee.c:465-488），按 CLONE_THREAD→同线程组、CLONE_PARENT→同祖父、默认→父子判亲（tracee.c:543-548）；多线程并发 fork 分不清时用**栈指针指纹**终判——孩子首停 SP 等于父登记的 `pending_child_sp`（tracee.c:563），原理是线程不共享栈（tracee.c:556）。

**继承表**是 attach_child 主体，逐字段复刻 clone(2) 语义：CLONE_VM→heap 引用共享否则 memdup（tracee.c:804-807）、CLONE_PARENT→parent 指向祖父（tracee.c:822-825）、CLONE_THREAD→clone 置位（tracee.c:832）、CLONE_FS→fs 共享否则拷 cwd（tracee.c:872-886）。特例 clone_stripped_newns（剥掉 CLONE_NEWNS 的补偿，tracee.h:106-110）：绑定树逐节点深拷贝重建双环（tracee.c:888-910），假 mount 只影响这个孩子，标志无条件一次性消费（tracee.c:927）。netlink 表按 fd 拷贝但清空待答复（tracee.c:940-946）。收尾 inherit_extensions（tracee.c:963）；孩子若在 SIGSTOP_PENDING 中等则放行重启并给 guest ptracer 补报事件（tracee.c:969-996）。

**改名换姓**：非 leader 线程 execve 时内核杀光其余线程、把 leader 的 pid 悄悄转给该线程。`get_execve_tracee()`（tracee.c:408，event.c:440 在 PTRACE_EVENT_EXEC 停机调用）用 GETEVENTMSG 取前线程 ID（tracee.c:415），让该线程条目顶替 leader：继承 pid/vpid/parent/clone/killall_on_exit（tracee.c:432-436）、全表改挂 parent（tracee.c:427-430）、`TALLOC_FREE(leader)` 释放旧壳（tracee.c:439，进程还活着故不能用 terminate_tracee()）。

**死亡两步走**：先 `terminate_tracee()` 只置标记（tracee.c:350-361），首领死亡顺带 killall；真正释放等循环顶部 `free_terminated_tracees()`（tracee.c:366-379，手写 while 推进——LIST_FOREACH 迭代中不能删节点）。`TALLOC_FREE(tracee)` 触发析构器 `remove_tracee`（tracee.c:88，注册于 tracee.c:227）：出链→清扫 life_context（tracee.c:98）→全表扫描给孤儿挂 parent=NULL、给被释放 ptracee 重放 pending 事件（tracee.c:102-124）→若死者是 ptracee 且死讯未上报 guest tracer，造**僵尸替身**：new_dummy_tracee 挂进 `PTRACER.zombies` 顶替 pid 与亲缘（tracee.c:133-155），保住 wait(2) 语义；ptracer 无 tracee 可等时返回 -ECHILD 并唤醒（tracee.c:162-171）。

## 5. 设计决策

- **talloc 层级即生命周期**：new_dummy_tracee 里 ctx/fs/heap 全 talloc 子分配（tracee.c:192-199），根一释放整棵树自动回收——这是全仓选 libtalloc 为唯二依赖的根本理由；`clean_life_span_object`（tracee.c:69）是唯一"析构前钩子"（绑定还要出三条环形队列）。
- **标记-清扫而非立即删除**：terminate 只做 O(1) 标记、统一清扫，因为调用点常在链表迭代中（tracee.c:370 注释）、死者可能还有 pending 事件要给别人看（僵尸替身依赖"条目还活着"）。
- **vpid 解 pid 复用**：pid-reused 分支（tracee.c:738-743）把旧条目 terminate 换新主，vpid 串起"同 pid 两世"；`is_still_traced()`（tracee.c:450-457，waitid WNOWAIT 探测）兜住"孩子没报到就死"的条目泄漏。
- **pending_child 三路认领**是对内核碎片化的工程妥协，栈指针指纹（tracee.c:563）是最后防线；这块连同 sigstop 三态、execve 身份顶替是 Termux fork 的活跃修补区，维护态铁律下近期提交集中于此层竞态。
- **assert 清单即不变量文档**：attach_child 十二条断言（tracee.c:753-762）逐条列出"新生 child 必须尚无 exe/cwd/bindings/parent/ptracer"。

## 6. 新人提示

1. **读法**：先 tracee.h:75-414 读完六分区注释（每区标题就是 clone 语义考点），再顺第 4 节三条出生路径读 tracee.c，最后回 event.c:314-470 看分派侧。配套：ptrace/ptrace.c:104（僵尸细节）、extension.c:128（继承协商）。
2. **调试**：`-v` 开高后生命周期日志全以 `vpid N: ...` 开头（tracee.c:701/727/739/998），排查"进程消失"类 bug 先抓 vpid 再对 pid。
3. **陷阱三连**：`get_tracee()` 命中即 flush ctx（tracee.c:337-338），从该池拿的指针过一次调用就悬空，跨函数传缓冲要么换池要么拷走；LIST_FOREACH 迭代中严禁删节点；给 Tracee 加字段先想清归哪个共享分区，放错区即 fork 语义 bug。
4. **改动红线**：此文件是竞态修补热区，AGENTS.md 只收 bug 修复；tracee.h:92-94 的 TODO（terminated 专用链表）贸然实现即大重构会被拒 PR。

> 勘误免责：swap_config 零调用者、fan-in 76 均为本次源码/图谱实测结论；上游 proot-me 同名文件结构有差异，勿混读。

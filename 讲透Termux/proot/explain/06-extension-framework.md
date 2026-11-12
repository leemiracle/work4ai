# 06 · 扩展框架：extension.h + extension.c 与 23 事件协议（L07）

> 锚均现场核实于 /usr-data/data2/repos/termux-repo/proot@b27d81a（239+169 行）。

## 一、角色定位：翻译引擎旁边的插件总线

这对文件是 proot 的**观察者模式基础设施**：`extension.h` 定义协议（23 种 `ExtensionEvent`、`Extension` 结构体、回调签名、内联分发器），`extension.c` 提供四个生命周期函数。框架自身**不做任何仿真**，只保证三件事：扩展挂得上 Tracee、在正确钩点被叫到、fork 时传承配置。

总线乘客即 proot 全部"非翻译"能力：extension.h:227-237 声明的九个内建回调里，轻量钩子（kompat/hidden_files/port_switch/fix_symlink_size/mountinfo/ashmem_memfd，Android 条件编译 :234-236）与重型 fake_id0（L08）/link2symlink（L09）同乘此总线——拦截 syscall 全生命周期靠的是事件广播而非特权。

**勘误钉版（再勘误）**：`ExtensionEvent` 枚举（extension.h:33-176）实测 **23 个成员**，非 21 个。onboarding 的"21"本身是计数工具产物：`[A-Z_]+` 正则匹配枚举名会漏掉 `LINK2SYMLINK_RENAME`（:148）与 `LINK2SYMLINK_UNLINK`（:152）——数字 `2` 不在字符类里，23−2 恰好=21。

## 二、内部结构：23 事件五分组 + 三字段乘客卡

### 事件枚举（extension.h:33-176）

| 分组 | 成员（行锚） | data1/data2 要点 |
|---|---|---|
| 路径翻译钩点 ×4 | GUEST_PATH(:40)、HOST_PATH(:50)、SYMLINK_DEREFERENCED(:59)、TRANSLATED_PATH(:65) | 基路径+guest 路径；host 路径+末次迭代；链接路径+内容；翻译结果可替换 |
| syscall 四相+链式 ×6 | SYSCALL_ENTER_START(:72)、ENTER_END(:79)、EXIT_START(:85)、EXIT_END(:90)、CHAINED_ENTER(:119)、CHAINED_EXIT(:124) | ENTER_END 的 data1=翻译状态 |
| 进程事件 ×1 | NEW_STATUS(:96) | data1=waitpid status |
| 继承协商 ×2 | INHERIT_PARENT(:106)、INHERIT_CHILD(:113) | 子 Tracee+clone flags（CLONE_RECONF 哨兵 :178） |
| 框架管理 ×4 | INITIALIZATION(:129)、REMOVED(:133)、PRINT_CONFIG(:137)、PRINT_USAGE(:141) | CLI 参数串；bool |
| Termux 增补 ×6 | SIGSYS_OCC(:144)、LINK2SYMLINK_RENAME(:148)、LINK2SYMLINK_UNLINK(:152)、STATX_SYSCALL(:158)、READLINK_PROC_FD(:167)、EXECVE_PROC_EXE(:175) | 专用 state 结构体指针 |

前四组是上游 PRoot 原产协议；Termux 增补组里 SIGSYS_OCC 是 seccomp 拦截后的抢救（seccomp.c:156），STATX/READLINK_PROC_FD/EXECVE_PROC_EXE 三个出口修正事件给 link2symlink 维持谎言自洽，LINK2SYMLINK_* 是罕见的**扩展间通信**通道。

### 数据结构

`extension_callback_t`（:181-182）是唯一契约：`int (*)(Extension *, ExtensionEvent, intptr_t, intptr_t)`——所有事件共用一个函数，靠扩展内部 switch 自筛。`Extension`（:184-198）三件行李：`callback` 指针、`config`（talloc 配置区）、`filtered_sysnums`（seccomp 布防表）；`link`（:197）串进双向链表（:200，头指针 `tracee->extensions` tracee.h:396-397），注释警告**顺序从不保证**（:195-196）。

### notify_extensions 总闸（:210-225）

`static inline`（头文件内联省调用）三步：无扩展直接返 0（:215-216）；`LIST_FOREACH` 逐个回调（:218）；**首个非零返回立即短路**（:219-221）。无订阅过滤、无寻址——每个扩展收到每个事件。

### extension.c 四函数

`new_extension`（:54-76）懒分配链表头（:59-63）→ `talloc_zero`（:66）→ `LIST_INSERT_HEAD` 头插（:72）→ 挂析构器（:73）。`remove_extension`（:40-47）即该析构器：摘链、补发 REMOVED、bzero——**扩展死亡由 talloc 引用计数自动触发**。`get_extension`（:82-95）按回调指针寻址。`initialize_extension`（:103-122）= new + 发 INITIALIZATION，返负则当场 `TALLOC_FREE` 摘除（:116-119），初始化失败自愈。

## 三、外部连接：注册、分发、消费三张网

**注册侧**在 CLI 层：proot.c 的 `-k` kompat（:168）、`-i/-0/-S` fake_id0（:186）、`--link2symlink`（:289）、`--ashmem-memfd`（:302）、`--sysvipc`（:315）、`-L/-H/-p`（:324/:330/:336）；外加 cli.c:482 无条件挂载 mountinfo（除非 `PROOT_NO_MOUNTINFO`）。重复选项去重也走框架：`-i` 先 `get_extension` 再 `TALLOC_FREE` 旧实例（proot.c:180-185）。

**分发侧**=全仓 22 个调用点、11 文件：syscall 主线（enter.c:1904/:3064、exit.c:64/:842/:479、syscall.c:183/:273）、路径（path.c:410/:440、canon.c:149/:349）、seccomp（seccomp.c:156）、statx（statx.c:133）、execve（execve/enter.c:647）、CLI 打印（cli.c:101/:212）、link2symlink 外播（link2symlink.c:900/:1017）。

**消费侧**连 seccomp：`enable_pending_seccomp_filter` 把各家 `filtered_sysnums` 合并进 BPF 程序（seccomp.c:514-522），`filter_sysnum` 查询某 syscall 是否被任一扩展要求停机（:554-561）。反向连接靠 `TRACEE()` 宏（tracee.h:418）两级 `talloc_parent` 上跳（extension→链表头→Tracee），talloc 层级即回指指针，fake_id0 回调拿宿主 tracee（fake_id0.c:1406）。

## 四、数据流：一次 syscall 的事件时序

以 `openat("/etc/hosts")`（fake_id0 + link2symlink）为例：

1. **ENTER_START**（enter.c:1904）：负值 `goto end` 写 errno；正值 `return 0` **整个翻译被跳过**（:1905-1907）；零继续。
2. 路径翻译内嵌四钩子：**GUEST_PATH**（path.c:410）→ 逐目录/绑定替换发 **HOST_PATH**（canon.c:149，绑定初始化期静默 ：147-150）→ 逐符号链接发 **SYMLINK_DEREFERENCED**（canon.c:349）→ **TRANSLATED_PATH**（path.c:440，可改写 result 缓冲）。fake_id0 在 HOST_PATH 做 `override_permissions`（fake_id0.c:1405），link2symlink 借 SYMLINK_DEREFERENCED 记账（link2symlink.c:1943-1951）。
3. **ENTER_END**（enter.c:3064）：data1=翻译状态，负值时 link2symlink 放弃（link2symlink.c:1788-1793）。
4. 链式 syscall：每条注入指令伴随 **CHAINED_ENTER**（syscall.c:183）/**CHAINED_EXIT**（:273）。
5. **EXIT_START**（exit.c:64）：负值写结果寄存器（:65-67），正值跳过全部出口修正（:69-70）。fake_id0 主战场在此：转发 `handle_sysexit_start`（fake_id0.c:1517→:1285）的 193 个 `case PR_` 大 switch 谎报 uid/gid=0。statx 另有出口 **STATX_SYSCALL**（statx.c:133）；**EXIT_END**（exit.c:842-844）是最后否决机会。
6. 进程级：waitpid 唤醒先过 **NEW_STATUS**（event.c:450-452，非零即接管）；seccomp 误杀走 **SIGSYS_OCC**（seccomp.c:156）；`/proc/<pid>/fd`、`<pid>/exe` 读取触发 **READLINK_PROC_FD**（exit.c:479）/**EXECVE_PROC_EXE**（execve/enter.c:647）。

**继承流**（fork/clone）：`inherit_extensions`（extension.c:128-169）逐个问父扩展 INHERIT_PARENT：负=不继承（:147-149）；零=继承且 **config 共享**（`talloc_reference`，:158-162）；正=走 INHERIT_CHILD 自建配置（:165-167）。两重型扩展同返 1 但策略异：fake_id0 深拷贝 Config（fake_id0.c:1381-1385；注释：glibc 线程组信号协议使 clone flags 无关）；link2symlink 子配置留空懒分配（link2symlink.c:1972-1980）。

**扩展间广播**：link2symlink 在 rename/unlink 元数据目录时反向 `notify_extensions(LINK2SYMLINK_RENAME/UNLINK)`（link2symlink.c:900/:1017），fake_id0 接住后把 `.proot-meta-file.` 元文件跟着搬（fake_id0.c:1429 起）——两仿真层的谎言因此不打架。

## 五、设计决策：一份返回值契约撑起整个框架

**返回值三分支是唯一控制协议**，语义按事件微调：通用约定"正=抢占（PRoot 跳过自身处理）、负=errno（短路上报）、零=旁观"（extension.h:34-39 注释逐事件重申）；NEW_STATUS 特化为非零即接管（:92-95）；TRANSLATED_PATH/STATX_SYSCALL 这类改写型事件正返回无意义——直接改 data1 指向的缓冲后返零。负值去向由调用点决定：ENTER 阶段进 `tracee->status` 并改 syscall 为 PR_void（syscall.c:193-197），EXIT 阶段 poke 结果寄存器（exit.c:842-844）。

其余五决策：①**全广播+首个非零短路**而非订阅制——协议极简，代价是每事件 O(扩展数) 回调风暴——不关心的事件须立刻 `default: return 0`；②**talloc 即生命周期**——Tracee 死亡时析构链自动补发 REMOVED，零手动清理（extension.c:73/:40-47）；③**filtered_sysnums 是性能契约**——seccomp BPF 让无关 syscall 直通（seccomp.c:514-522），扩展只为声明的 syscall 付两次停机代价；④**顺序不保证**（extension.h:195-196）逼出显式扩展间通信事件（LINK2SYMLINK_*），杜绝隐式执行序依赖；⑤**懒分配链头**（extension.c:59-63）+ 内联分发器（extension.h:210）让不用扩展的 tracee 近零开销——对每个 syscall 都要过的框架，这份克制必要。

## 六、新人提示

**最小扩展五步**：实现 `xxx_callback`（switch 处理 INITIALIZATION：分配 config、填 filtered_sysnums、返 0——及关心的事件）；extension.h:227-237 声明；proot.c 加选项 handler 调 `initialize_extension`；按需实现 INHERIT_PARENT/CHILD；逃生门参考 cli.c:481。但 AGENTS.md 治理铁律：维护态只收 bug 修复与新 syscall 处理器，**新扩展会被拒**。

三个坑：①`notify_extensions` 短路只看**第一个**非零返回——两个扩展都返负时后者收不到事件，调试"扩展没被调用"先查是否被前者短路（链表头插序与注册序相反，extension.c:72）；②config 共享（INHERIT_PARENT 返 0）时父子指同一块内存，要隔离须走 INHERIT_CHILD；③写断言前自己数枚举，别信文档（21→23 再勘误即教训：数字 2 骗过两代计数器）。

阅读顺序：extension.h:33-176 读全 23 事件注释（注释即协议规范）→ kompat.c（最小完整样本）→ fake_id0.c:1327-1543 的 switch 骨架对照第四节时序图。

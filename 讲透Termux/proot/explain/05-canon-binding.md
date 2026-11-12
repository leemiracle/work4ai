# 05 · canon.c 与 binding.c：路径双向翻译引擎与绑定表

> 锚基准：termux-repo/proot@b27d81a；file:line 均经源码核实（2026-10-26）。

## 一、角色定位：谎言的两个半球

PRoot 的承诺一句话：tracee 看到 guest 文件系统视图，内核看到 host 真实路径，换算几乎全在这两个文件。`canonicalize`（canon.c:199）是 guest→host 的唯一入口——带路径的 syscall 在 enter 阶段经 `translate_path`（path.c:370）走到它；`detranslate_path`（path.c:454）负责反向，在 exit 阶段把内核输出换算回 guest 坐标。绑定表（binding.c）是两套坐标系的"汇率表"：`-r /data/rootfs` 即 guest `/` ↔ host `/data/rootfs`，`-b` 追加通道——`mount --bind` 与 chroot 的用户态等价物（AGENTS.md:3-5）。属 14 层架构 L03：上承 L04 翻译链，下接 L06-L09 扩展。

## 二、内部结构：一算法三队列

### 2.1 绑定表：一个对象，三种视图

`Binding`（binding.h:32-44）极简：`host`/`guest` 一对 `Path`（path.h:50-54）加一个 `need_substitution` 布尔（binding.h:36）。机关在 link 字段：**同一 Binding 节点经三套 `CIRCLEQ_ENTRY` 同时挂三条环形队列**（binding.h:40-42）——`pending`（声明序）、`guest`（按 guest 路径排序）、`host`（按 host 路径排序）。BSD CIRCLEQ 让一套数据三种遍历序零拷贝：声明序给 `initialize_bindings`（binding.c:747-758），guest 序供正向查表，host 序供反向查表。访问宏（binding.c:40-57）编译期展开 side，插入时 `talloc_reference`（binding.c:65）。

排序**最长前缀优先**：`insort_binding`（binding.c:297）保证 `-b /bin:/foo/bin -b /usr/bin/more:/foo/bin/more` 嵌套绑定时深层先命中。`get_binding`（binding.c:120）逐条 `compare_paths2`（binding.c:146），首个命中必最深；两条绑定 guest 路径相同则后者替换前者（binding.c:335-346）。`get_root`（binding.c:199）取 guest 路径为 `/` 的绑定，从队尾取，故 `/` 必须垫底（binding.c:530-532）。

`substitute_binding`（binding.c:239）是执行侧：命中且 `need_substitution=false`（对称绑定，binding.c:250）返回 0"命中但无需替换"；否则掐头换前缀（binding.c:269 调 path.c:731）返回 1。对称绑定登记"此路径属于本命名空间"——没有它 `get_binding` 返回 NULL 直接 ENOENT。

### 2.2 正向翻译：userspace namei 逐组件爬行

`canonicalize`（canon.c:199）三关键参数：`user_path`（syscall 原路径）、`deref_final`（**末段**是否解引用，lstat/unlink 要 false）、`guest_path` 双向复用（进=相对路径的 base，canon.c:220-224；出=结果）。递归超 `MAXSYMLINKS` 即 ELOOP（canon.c:209-210）。主循环（canon.c:232）每轮一个分量，复刻内核 namei：

1. **切分量**：`next_component`（canon.c:87）跳多余 `/`、切出 ≤NAME_MAX 分量（超长 ENAMETOOLONG），判 finality——FINAL_SLASH（后随 `/`，期望目录）/FINAL_NORMAL/FINAL_DOT（path.h:57-62）。
2. **`.`/`..` 纯字符串处理**：`.` 跳过并按需标 FINAL_DOT（canon.c:242-246）；`..` 调 `pop_component`（canon.c:44）在 **guest 路径**上掐末段（canon.c:248-252），不碰 host。
3. **拼前缀**：`join_paths`（canon.c:255）组 `guest_path/component`。
4. **查表+类型检查**：`substitute_binding_stat`（canon.c:136）先 `substitute_binding(GUEST)` 换 host 路径再 `lstat`：非末段必须是目录或符号链接，否则 ENOENT/ENOTDIR（canon.c:179-184）。
5. **非链接快速路径**：`status<=0` 或"末段不解引用"，分量直接追加进 `guest_path`（canon.c:274-280）。
6. **符号链接慢路径**：`readlink` 取目标（canon.c:340）→ `detranslate_path` 剥 host 前缀回 guest 坐标（canon.c:357）→ **递归 canonicalize**（canon.c:366）：绝对目标从当前 `guest_path` 重走，相对目标以其为 base。**逃逸防护的真身在此**：不是拦截 `..`，而是链接跳转后整体重走全流程，自然圈回 rootfs。
7. **收尾恢复语义**：FINAL_SLASH 补回尾部 `/`（canon.c:390-395）、FINAL_DOT 补 `/.`（canon.c:397-402）——`open("dir/")` 报 ENOTDIR 靠这步保真。

### 2.3 /proc 特判：内核动态链接的用户态仿真

`/proc/self`、`/proc/<pid>/{exe,cwd,root}`、`/proc/<pid>/fd/N` 是内核**读取时**生成的 magic link——host 内核解出的 `self` 是 PRoot 的 pid，对 tracee 是错的。处理在慢路径入口（canon.c:289）：先 `compare_paths("/proc", guest_path)`，字面不匹配再做**别名探测**——`guest_path` 过 `substitute_binding` 后再比（canon.c:297-305）：`-b /oldroot:/` 会让 `/oldroot/proc` 实际就是 `/proc`，不探测则 `/oldroot/proc/self` 被真内核解析成 PRoot 的 pid。

命中后交 `readlink_proc`（proc.c:43），四种结局：`/proc/self` → `/proc/<tracee pid>`（proc.c:59-68，返回 CANONICALIZE 在 canon.c:316 续走）；`/proc/<pid>/{exe,cwd,root}` → 经 `get_tracee` 查 PRoot 所跟踪进程的对应字段（proc.c:130-132）；`/proc/<pid>/fd/N` → DONT_CANONICALIZE **不立即解引用**（proc.c:153-172），可能指向 pipe/socket，真 readlink 由 exit 的 `readlink_proc2`（proc.c:190）补台；其余 DEFAULT 走真 readlink(2)。termux fork 补的 `normalized_base`（proc.c:88-97）把 base `/proc/self/fd` 归一为 `/proc/<pid>/fd`，否则 `atoi("self/fd")==0` 提前 DEFAULT 就 ENOENT。

## 三、外部连接

**上游**：syscall enter 链 `translate_path`（path.c:370）是热调用方；冷调用方是 `initialize_binding`（binding.c:596）——绑定初始化时 guest 路径也要消毒，鸡蛋问题。解法：`initialize_bindings`（binding.c:711）先装 `/` 绑定（binding.c:741-742）再逆序处理其余，用 "/" bootstrap 整个 canonicalization。

**协同**：glue.c 在绑定初始化发现路径缺失时现场造假（`build_glue` 挂 canon.c:174，组件类型由 binding.c:578-581 `glue_type` 预记录）；f2fs-bug.c 绕过 Termux 设备 f2fs 的 EEXIST 误报（canon.c:156）；扩展经 HOST_PATH（canon.c:149）与 SYMLINK_DEREFERENCED（canon.c:349）钩点介入；Android 补丁：`/linkerconfig` stat EACCES 硬编码 S_IFDIR（canon.c:165-168）。

**下游**：`detranslate_path`（path.c:454）服务两处——canon 主循环剥链接目标（canon.c:357）与 exit 阶段输出回译。

## 四、数据流：双向各走一遍

**正向（open("/bin/sh")，usr-merge rootfs，`-r /data/rootfs -b /sdcard:/sdcard`）**：分量 `bin` → 查表换出 `/data/rootfs/bin` → lstat 见符号链接（指 `usr/bin`）→ readlink+detranslate 后递归，`guest_path` 变 `/usr/bin` → 回外层续 `sh` → host `/data/rootfs/usr/bin/sh` 交内核。usr-merge 的 `/bin → usr/bin` 跳转**全程在 guest 坐标系**；若开 `/sdcard/x.jpg`，分量 `sdcard` 命中第二条绑定直接进入 Android 真实存储。

**反向（getcwd 回填）**：内核写入 `/data/rootfs/home/user`，exit 阶段 `detranslate_path`：相对路径放行（path.c:468-469）；无 referrer 时 `follow_binding=true`（path.c:521-524）→ `substitute_binding(HOST)` 在 **host 序队列**查前缀，命中 `/` 绑定剥掉前缀（path.c:537-550）→ tracee 拿到 `/home/user`。带 referrer 的链接仅当其在 `/proc` 下（path.c:479-498），或链接与目标同属一条绑定（`-b /lib:/foo` 下 `/lib/a → /lib/b` 应呈现 `/foo/a → /foo/b`，path.c:499-519）才回译，否则保留原文。

## 五、设计决策

1. **逐组件而非一次 realpath(3)**：内核 realpath 不认识绑定表——会把 `/bin` 解析成 host 真身，也无法把链接目标圈回 rootfs。主循环是"每推进一分量就翻译一次"的 userspace namei，防逃逸是结构的自然结果。
2. **三队列而非三份拷贝**：绑定集天然需三种顺序，三链字段一份数据三视图，增删经 `insort_binding2`（binding.c:381）同步两表，漏一边就"正向通反向断"。
3. **对称绑定返回 0**（binding.c:250）：命中≠替换，host==guest 的绑定仍登记命名空间归属。
4. **HOST 侧假阳性防御**（binding.c:156-159）：`-m /usr:/location` 时 host 路径 `/usr/x` 错命中该绑定，`belongs_to_guestfs`（path.c:573）排除。
5. **host 侧 `/proc/self` 不做 realpath**（binding.c:485-503）：`new_binding` 对其跳过 `realpath2`，否则 "self" 固定成 PRoot 的 pid，`-b /proc/self/fd/N` 会把 fd 表永久错绑。
6. **`!` 后缀与目录特例**：guest 路径 `path!` 显式禁末段解引用（binding.c:565-567）；但 host 侧是目录时强制不解引用（binding.c:590-591）——否则绑定注册到链接目标处，字面 stat(2) 漏馅。
7. **ELOOP 与内存双保险**：递归超 MAXSYMLINKS 即 ELOOP（canon.c:209），canon.c:366 还叠加 `symlinks_followed` 计数；队列宏内嵌 talloc 引用计数（binding.c:65/93、422）。

## 六、新人提示

**阅读路径**：binding.h:32-46（结构）→ binding.c 的 `get_binding`/`substitute_binding`（热路径）→ canon.c:199 主循环（对照 2.2 节七步）→ 最后 `insort_binding` 家族与 `initialize_bindings`。调试用 `-v` 经 `print_bindings`（binding.c:100）先看表。

**钉版坑位**：① `guest_path` 参数**双向**（进=base，出=结果），canon.c:215 禁止 `user_path` 与其别名传参；② FINAL_SLASH/FINAL_DOT 不是摆设，尾部恢复（canon.c:385-407）决定 `open("dir/")` 报不报 ENOTDIR；③ /proc magic link 仿真有**两处**——enter 的 `readlink_proc`（proc.c:43）与 exit 的 `readlink_proc2`（proc.c:190），改一处必查另一处；④ termux fork 补丁浓度最高三处：canon.c:297-305 别名探测、proc.c:88-97 normalized_base、binding.c:485-503 `/proc/self` 保留，动前先读注释 issue 链接。

**扩展点**：新 magic link 在 proc.c:130-132 加一行；新路径类型在 binding.c:578-581 调整。动手前先读 AGENTS.md 维护态铁律。

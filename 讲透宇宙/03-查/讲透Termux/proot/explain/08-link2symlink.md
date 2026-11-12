# 08 · link2symlink.c：在不能硬链接的文件系统上硬链接

> 锚约定：未注明文件名的 `:N` 锚均指 `src/extension/link2symlink/link2symlink.c`（1985 行，L09 重型仿真扩展，图谱@b27d81a）；其余锚带完整路径。所有断言均经源码现场核实。

## 一、角色定位：为什么需要"伪造"硬链接

link2symlink 是 proot 的第二个重型仿真扩展（第一个是 fake_id0，见本系列 07 篇），解决一个非常具体的 Android 痛点：**目标文件系统不支持 link(2)**。

背景先澄清：Android 应用私有目录（`/data/data/<pkg>`）落在 ext4/f2fs 上，内核本就支持硬链接。真正不支持的是**共享存储**——`/storage/emulated/0`、`/sdcard` 由 FUSE（emulated storage，历史上 sdcardfs→FUSE 演进）以"FAT 语义模拟视图"呈现，外置 SD/U 盘则干脆是 exFAT/FAT32。FAT 家族没有"一个 inode 多个目录项"的概念，FUSE 桥接层也无从表达，于是 link(2) 在这类路径上返回 EPERM。而 proot 的典型部署恰恰是把整个发行版 rootfs 放在共享存储（容量大、MTP 可见），此时 apt/dpkg 解包时铺天盖地的硬链接操作全部失败。

link2symlink 的策略一行话讲完：**把硬链接降格为符号链接**——`link(old, new)` 被改写成"把 `old` 的数据文件搬进元数据目录 + 在 `new` 处放一个指向它的符号链接"，再在 stat/getdents/proc 等所有观测面上把这对符号链接伪装成真硬链接。元数据目录前缀由宏 `PREFIX` 定义：USERLAND 构建下为 `.proot.l2s.`（:30），非 USERLAND 为 `.l2s.`（:33）；目录本身由环境变量 `PROOT_L2S_DIR` 指定（:155），未配置时中间体就地创建在文件旁边（:141-143 注释）。

该扩展默认关闭，由 CLI 显式装配：`--link2symlink` 选项在 `src/cli/proot.h:239` 注册、:242 绑定 handler，`handle_option_link2symlink`（`src/cli/proot.c:284`）调 `initialize_extension(tracee, link2symlink_callback, NULL)`（proot.c:289）。注意上游遗留的 doc/manual.txt 里搜不到该选项——文档即 CLI 配置的惯例（ONBOARDING §6）对 Termux 新增扩展并不成立。

## 二、内部结构：一张命名协议撑起的账本

### 2.1 文件名即数据库（"stat 缓存文件格式"）

link2symlink 不维护任何索引文件，**目录本身就是账本**，链接计数直接编码进文件名。链条共三层：

```
guest 视角         host 盘面（l2s 目录或原目录）
/usr/bin/cc   →   <l2s>/.proot.l2s.cc0001.0003   (final：数据真身，尾段=计数)
（原位符号链接）      <l2s>/.proot.l2s.cc0001      (intermediate：指向 final)
                  新建的链接处再放一个符号链接 → intermediate
```

- **final**（真身）：`<PREFIX><name><NNNN>.<count>`，`<NNNN>` 是 4 位中间体后缀，`<count>` 是当前链接计数，至少 4 位、从 10000 起变 5 位、至多 9 位——`get_link_count`（:355）逐段校验：前缀匹配（:368）、倒数第一个点前有 4 位数字（:378-381）、点后长度 4..9 的纯数字（:383-391）。9 位封顶是防 int 溢出，配合 `MAX_LINK_COUNT 999999999`（:345）双保险（:923）。
- **intermediate**（中间体）：`<PREFIX><name><NNNN>`，内容是 final 的路径。`find_intermediate`（:497）从 final 名剥掉 `.<count>` 段反推中间体路径（:506-508），再用 `st_dev/st_ino` 双字段验证两者确是同一文件（:517-518）——名字只是线索，inode 才是判据。
- **原位链接**：guest 在原路径和新路径看到的名字，内容指向 intermediate。

改计数用 `name_link_count`（:411）：以 `%04d` **整体重写**尾段而非改末 4 字符（:418-420 注释明说，因为 10000 处会进位变长）。这个格式设计让任意第三方（或重启后的 PRoot 本身）都能从盘面无损恢复全部状态——无状态、免恢复、崩溃安全。

### 2.2 每调用配置与全局态

`Link2SymlinkConfig`（:56-73）挂在扩展实例上，只描述"正在处理的这一个 syscall"：`dereferenced_link`（:60，路径翻译刚穿过的假硬链接）、`pending_link`（:65，即将返回 fd 的打开被重定向自哪个假硬链接）、`removed_link/removed_intermediate`（:71-72，即将被 unlink/rename 抹掉的名字）。它刻意不传子进程——`INHERIT_PARENT` 返回 1 拒绝共享（:1972-1975），每回配置按需重分配。

全局态三件套（:132-135）：l2s 目录路径、其长度、以及**目录 fd**。用 fd 而非路径名，是一段精心论证的安全设计（详见五节）：注释 :108-131 完整论证了 tracee 如何用 `rm -rf` + `ln -s` 把 l2s 目录换成指向任意 host 路径的符号链接，从而诱导 PRoot 把文件写进 rootfs 之外；对策是 `open(O_NOFOLLOW)` 一次性钉住 inode（:187-188），此后所有操作走 `*at` 族。配套的 `l2s_entry`（:208）把"l2s 目录下的直接子项"分解为 (dirfd, 相对名)，`l2s_lstat/l2s_symlink/l2s_unlink/l2s_rename/my_readlink`（:245/:256/:267/:278/:303）五个包装把裸路径调用降级为 `fstatat/symlinkat/unlinkat/renameat/readlinkat`；目录打不开时直接失败而非回退裸路径（:202-206 注释：回退恰恰是攻击者想要的状态）。

另有 64 槽环形 `fd_cache`（:99-106）记 (pid, fd, link) 三元组，供 /proc 圆谎（见 4.4）。

### 2.3 事件分派骨架

`link2symlink_callback`（:1741）是唯一入口，INITIALIZATION 时布防 17 个 syscall 的 seccomp 过滤（:1749-1768：link/linkat/unlink/unlinkat、stat 族七兄弟、rename 三兄弟、getdents 两兄弟，全部 FILTER_SYSEXIT）。事件五相：ENTER_START 清残留状态（:1773-1780）、ENTER_END 做语义改写、EXIT_END 圆谎（:1918）、CHAINED_EXIT 处理链式 syscall（:1922），外加 GUEST_PATH/TRANSLATED_PATH/SYMLINK_DEREFERENCED/STATX_SYSCALL/READLINK_PROC_FD/EXECVE_PROC_EXE 六个路径钩点（:1943-1970）。

## 三、外部连接

- **扩展框架**：事件枚举与回调协议见 `src/extension/extension.h`（本系列 06 篇）。link2symlink 还让框架为自己新增了两个专用事件 `LINK2SYMLINK_RENAME/LINK2SYMLINK_UNLINK`（extension.h:146-153）：它移动/删除文件时广播给其他扩展——fake_id0 的属主元数据文件必须跟着数据文件一起搬，否则权限记账断裂。
- **statx 主线**：`src/tracee/statx.c` 在 statx 出口经 `notify_extensions(STATX_SYSCALL)` 通知本扩展改写 `stx_nlink`（:1546-1563），并置 `updated_stats` 让结果重写回 tracee（:1562）。
- **fix_symlink_size 配套**（`src/extension/fix_symlink_size/fix_symlink_size.c`，119 行）：link2symlink 管 nlink/inode，size 维度由它补——lstat 出口若发现路径是普通符号链接，`readlink` 取内容长度覆写 `st_size`（fix_symlink_size.c:72,:80-81）。背景：proot 路径翻译会跟随符号链接，导致内核 lstat 的对象变成目标文件，`st_size` 变成文件大小；该扩展把它修正回符号链接语义的"内容长度"。两个扩展共用 `PREFIX` 与 `DELETED_SUFFIX` 定义（fix_symlink_size.c:20-21，属复制非共享，改前缀须两处同步）。
- **hidden_files**：l2s 目录以 `.proot` 开头的条目从 getdents 流剔除（hidden_files.c:20 `HIDDEN_PREFIX ".proot"`，:131 前缀判定），guest 永远看不见账本。
- **f2fs-bug**：`translated_path` 钩子先问 `should_skip_file_access_due_to_f2fs_bug`（:1613，实现在 `src/path/f2fs-bug.c`）——f2fs 大小写 bug 探测命中的路径直接放行，不做假硬链接解析（探测逻辑 f2fs-bug.c:56-78）。
- **回归测试**：tests/ 下 14 个脚本引用本扩展，个个对应一条历史伤疤：test-4171f0b5.sh（计数 4 位/5 位边界）、test-60e0614d.sh（access(2) 探空闲槽跟悬空链接的竞争）、test-9f16ee06.sh（rename/unlink 先记账后销账）、test-6e3a9d21.sh（linkat AT_SYMLINK_FOLLOW）、test-02686ecd.sh（翻译失败不得越界改宿主）、test-d4187784.sh（O_NOFOLLOW 打开后的 /proc/fd 名字）。
- **消费方**：proot-distro 以 `-l` 选项在共享存储部署时启用。

## 四、数据流

### 4.1 link(2) 主流程：三步走

ENTER_END 分派（:1859-1873）：`PR_link` → `move_and_symlink_path(SYSARG_1, SYSARG_2)`；`PR_linkat` 先试 `handle_linkat_from_proc_fd`（见 4.4），否则 `move_and_symlink_path(SYSARG_2, SYSARG_4)`（:1906）。

`move_and_symlink_path`（:759-958）第一步判型：目录拒绝 EPERM（:785）；**普通符号链接**走 `link_symbolic_link`（:809→:734）——link(2) 本不跟随符号链接，伪造时应复制"内容"而非制造计数，于是在新位置 `symlink` 同样内容（:744），两个符号链接各是各的 inode（:730-732 注释承认元数据不再共享是可接受代价）；名字带 PREFIX 的符号链接（:801）或已有假硬链接的文件（:811 经 `find_intermediate` 验证）则 `first_link=0` 走增量路径。

**首个链接**（:861-915）：循环探测后缀 0001..9999（超限 EMLINK，:874），用 `l2s_symlink` 原子占位——注释 :862-872 记载了旧版用 access(2) 探空闲的教训：access 会跟随悬空的 intermediate，探出"不存在"却创建失败，文件搬走后失去所有名字。占位成功即敲定 final 名 `<intermediate><NNNN>.0002`（:877），`l2s_rename` 把原文件搬过去（:894），失败则拆占位符返回（:895-898）；成功后广播 LINK2SYMLINK_RENAME（:900），再在原位 `symlink(intermediate, original)`（:903），此步失败则把文件搬回原地（:908-914）——每一步都有对称回滚。

**后续链接**（:916-944）：读 intermediate 得 final（:918），计数 +1 重命名（:922-930），广播（:933），把 intermediate 换指向新 final（:938-941：先 unlink 再 symlink）。最后一步（:947-955）统一处理：读 link_target 参数路径，`symlink(intermediate, final_guest_path)`，然后 `poke_reg(SYSARG_RESULT, 0)` + `set_sysnum(PR_void)`（:954-955）——syscall 已由 PRoot 亲手代劳，内核侧整单作废。

### 4.2 unlink/rename 语义重写：先记账、后销账

假硬链接被 unlink 时，guest 只删掉"一个名字"，host 侧还要维护计数——但**绝不能在内核删除之前动账本**。注释 :1026-1034 记录了历史 bug：提前减计数，若 syscall 随后失败，最后一次减账会把数据文件连同唯一名字一起删掉；或计数偏低一格，日后误删仍有名字引用的数据。

正确时序两段式：ENTER 阶段 `remember_removed_link`（:1035）只把 link/intermediate 抄进 config（:1057-1058）；内核照常删除符号链接；EXIT 阶段 `forget_removed_link`（:1158）**双重确认**后才销账——syscall 结果为 0 **且**该名字确实不再是原符号链接（:1175-1177，`my_readlink` 失败或内容已变；注释 :1169-1174 解释：外层 seccomp 拒绝时寄存器里是内核回滚后的杂值，rename 的 exit 阶段甚至会把它圆成 0，光看结果不够）。确认后 `decrement_intermediate_count`（:967）：计数 >1 则改名减一（:988-1006），=1 则删 intermediate 与 final 并广播 LINK2SYMLINK_UNLINK（:1011-1017）；断链静默跳过（:978-981）。计数维护遇 EACCES 时还有一段"临时 chmod 提权重试"（`decrement_removed_link_count`，:1142-1148）——目录可能只在本 syscall 期间可写（fake_id0 的授权方式），而账本是 PRoot 自己的事。

rename 的重写更细（`prepare_rename`，:1068）：RENAME_NOREPLACE/EXCHANGE 不覆盖新名，直接放过（:1079）；否则新名若是假硬链接，照 unlink 记账（:1082）。最妙的是新旧同文件场景（:1097-1107）：guest 语义里两个名字指向同一 inode，rename 应为 no-op；内核却看见两个不同符号链接，会真删掉新名。对策是把 new_sysarg 直接改成 old_sysarg（:1107），让内核"自我改名"——同一个 no-op，同一套检查（EROFS 等），零风险圆谎。`translated_path` 钩子还豁免了 unlink/link/rename 族的符号链接解析（:1602-1611）：这些 syscall 需要看见符号链接本身而非其目标。

### 4.3 stat/getdents 圆谎

stat 族七个 syscall 在 `handle_sysexit_end`（:1361-1544）统一处理：PREFIX 开头的路径按 intermediate/final 分别 `goto`（:1443-1451）；假硬链接追到 final 后，把 `finalStat.st_nlink` 覆写为名字里的计数（:1480-1484）再写回 tracee 内存（:1499）——32on64 模式只写前 72 字节（`SIZEOF_RELEVANT_STRUCT_STAT`，:1355，注释 :1341-1354 列出 32/64 位布局一致的字段范围）。追不下去的断链按内核原样报告（:1456-1462 注释：报错会让文件无法 lstat、无法用常规工具删除）。fstat 的路径要用 fd 反查 `/proc/<pid>/fd` 并剥掉 " (deleted)" 后缀（:1406-1413，`DELETED_SUFFIX` :35）。

getdents（:1231-1338）修 `d_type`：假硬链接对内核是符号链接（DT_LNK），但 `find -type f`、ripgrep、Python `DirEntry.is_symlink()` 都依赖 d_type 与 lstat 一致（:1216-1222 注释）。逐条目解析 dirent 布局（32 位 `struct linux_dirent` 与 64 位 dirent64 的字段偏移分别处理，:1263-1273），DT_LNK 条目经 `get_faked_hard_link_type`（:1194）换成真身文件类型（:1322），只回写被修改的内存跨度（:1334，注释：无 process_vm_writev 时逐字写，省一拍是一拍）。该 syscall 永不失败（:1229）。statx 走独立事件改 `stx_nlink`（:1546-1563）。

### 4.4 /proc 双坐标：bind 前缀与 guest 路径的换算

假硬链接永远活在两个坐标系里：**guest 坐标**是 tracee 使用的原位名字（如 `/usr/bin/cc`），**host 坐标**是内核实际看到的 l2s 目录路径（如 `/storage/…/.proot.l2s.cc0001.0003`）。盘面 intermediate 符号链接的内容刻意存 host 绝对路径且**永不在盘面上换算**（:123-126 注释："Only the syscalls change, never the contents"），坐标系换算全部发生在翻译层。

正向（guest→host）：路径翻译主线解完符号链接后触发 `TRANSLATED_PATH` 钩子（:1956→:1595），把假硬链接解析为 final 的 host 路径交给内核（:1621-1627）；若是 open 族（`is_open_syscall`，:328），`remember_opened_link`（:1572）把 guest 侧名字存进 `pending_link`（:1583），并置 `sysexit_pending`/`restart_how = PTRACE_SYSCALL`（:1587-1588，字段在 `src/tracee/tracee.h:335/:213`）强制 exit 停机——seccomp 默认跳过 exit 阶段，而拿到 fd 号必须等 exit（:1585-1586 注释）。

反向（host→guest）：内核在 `/proc/<PID>/fd/<FD>` 报告的是 l2s 目录里的名字，tracee 会看穿伪装。READLINK_PROC_FD 事件（:1964）触发 `readlink_proc_fd`（:593）：从 64 槽 fd_cache 里 `recall_fd` 找回 guest 名字（:603，线程共享 fd 不共享 pid，兄弟条目作 fallback，:570-586），再 `resolve_faked_hard_link` 验证该名字确实还指向同一个文件（:609-611，fd 号会复用、链接会被删），比对通过才替换（:614-615）。fd 是在 open 的 exit 阶段由 `remember_fd`（:527，环形复用同 (pid,fd) 槽防重复膨胀 :533-543）登记的（:1528-1530）。`/proc/<PID>/exe` 同理走 EXECVE_PROC_EXE（:1968→:703）：把 host 路径经 `detranslate_path`（:714，host→guest 的绑定前缀逆替换）换回 guest 名字——uutils 这类 multi-call 程序按 argv[0] 名字决定行为（:696-701 注释），名字错了程序拒绝运行。

还有一处 enter 阶段的整段代劳：`handle_linkat_from_proc_fd`（:1644-1735）处理 Termux 的 `ln` 常见形态 `linkat("/proc/X/fd/Y", target, AT_SYMLINK_FOLLOW)`（:1879）。当 fd 指向已 "(deleted)" 的文件（:1657-1662 校验后缀），内核无从 link，PRoot 亲自读源 fd、以 4KB 循环把内容整份拷到 target（:1705-1729），成功后 `PR_void`+结果 0 消化整个 syscall（:1884-1885）。这段代码里"`status >= 0` 再强制 `-EPERM`"的防御（:1698-1699 等）是因为 errno 为 0 时 `-errno` 会变成正确的 0——07 篇 fake_id0 同款坑。

## 五、设计决策与取舍

1. **符号链接当底座而非复制**：零数据拷贝、改动双向可见，最接近硬链接语义。代价在元数据（inode/owner/times）两份不共享（:730-732）——coreutils 的 `--preserve=links` 类校验靠 st_nlink/st_ino 圆谎补齐，而 st_ino 两个字段（链接处与真身处）本就不同，这是该方案公认的残缺上限。
2. **计数入名、目录即账本**：任何崩溃后盘面自解释，无需恢复流程；代价是每次增减链要 rename 一次真身文件（改尾号），链接数大时 l2s 目录写放大。9999 后缀/目录（:874）与 9 位计数（:384）划出双层上限。
3. **l2s 目录 fd 化是对 TOCTOU 的正面试击**（:108-131）：PRoot 代劳的 syscall 不经自身翻译，裸路径会被 tracee 预埋的符号链接劫持到 rootfs 外；`O_NOFOLLOW` 开一次、`*at` 族钉住 inode，名字解析不再重复发生。教训浓缩成一句：检查名字没用，钉住 inode 才算数。test-02686ecd.sh 专门守"翻译失败不得越界改宿主"的底线。
4. **两段式记账**（remember→forget）保 syscall 失败语义：宁可多停一次 syscall（exit 阶段被迫保留，:1587），不可提前销账——:1026-1034 与 test-9f16ee06.sh 是同一段历史。
5. **圆谎永不升级为报错**：getdents 修不了就按内核原样（:1229）；断链 stat 按悬空符号链接报告（:1456-1462）。伪装层的失败模式必须退化到"看起来像真文件系统也会发生的怪事"，而不是 proot 独有的 errno。
6. **与 fake_id0 的分工靠事件而非耦合**：LINK2SYMLINK_RENAME/UNLINK 广播（extension.h:146-153）让 meta 文件跟随搬迁；fstat 的 USERLAND 链式交互（:1368-1374,:1932-1939）专门给 fake_id0 的 readlinkat 仿真让路。两个重型扩展零直接调用。
7. **fix_symlink_size 拆成独立扩展**是分而治之：size 修正对一切"被翻译跟随的符号链接"都成立，不止假硬链接，独立扩展可单独启停（fix_symlink_size.c:103-108 只布防 lstat 两个号）。

## 六、新人提示

**阅读路径**：① 宏与两份注释（:29-46、:108-131）建立词汇表 → ② `get_link_count`/`name_link_count` 吃透命名协议 → ③ `move_and_symlink_path`（:759）逐行读，配合画三层链条图 → ④ `handle_sysexit_end`（:1361）看圆谎矩阵 → ⑤ 最后回到 `link2symlink_callback`（:1741）总装。记住三个专名：final（真身）、intermediate（中间体）、faked hard link（原位链接）。

**调试**：`-v` 至少 2 级可见本扩展的 VERBOSE（:979 断链跳过、:1181 减账失败、:1408 fd 反查失败都是排障金矿）；盘面上直接 `ls -a` l2s 目录核对尾号计数与 intermediate 指向，比任何日志都直观。

**改动守则**：AGENTS.md 维护态铁律全量适用——只修 bug 不加特性；动这个文件前先跑 14 个 link2symlink 测试（tests/test-{4171f0b5,60e0614d,9f16ee06,6e3a9d21,02686ecd,d4187784}.sh 等），改命名协议（PREFIX/位数/分隔符）属于破坏性格式变更，盘上存量数据无法迁移，历史上从未做过；USERLAND 与非 USERLAND 的 PREFIX 双定义（:29-34）与 fix_symlink_size.c:20 的复制粘贴是三处必须同步的隐患点。新增观测面（新 syscall 或新 /proc 入口）时自问一句：内核在这个观测面上会怎么报告一个真硬链接？答案就是圆谎目标。

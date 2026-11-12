# 02 · bundle↔runtime 互引与 glibc 兼容层

> 锚全部源自 /usr-data/data2/repos/agent-repos/NVIDIA/enroot 核实（2026-11-07）

## 角色定位

本篇覆盖 enroot 两大「反直觉」设计：一是**两个 shell 文件互相引用构成的自解压闭环**（bundle.sh 既是库又是 .run 包头）；二是**主动选择 musl 后必须自己补 glibc 差异**的兼容层（compat.h + bundled libbsd）。前者是离线分发能力的根，后者是静态编译的代价。

## 内部结构

**互引环**：打包侧 `src/runtime.sh:632` `runtime::bundle() ()` 子 shell——`:693` 把 `common.sh,runtime.sh` 拷进镜像 bundle_lib_dir（/.enroot/lib），`:709` 调 `enroot-makeself --tar-quietly --header "${ENROOT_LIBRARY_PATH}/bundle.sh"` 生成 .run（`deps/Makefile:35` 证实 enroot-makeself 是上游 makeself.sh 的改名安装，非自研）。运行侧 `src/bundle.sh`：`:49` `bundle::_dd()` 子 shell 按偏移+尺寸从自身 dd 出数据段（progress= 配 pv 风格进度条），`:193` `bundle::extract` 逐段 `dd|解压|tar` 展开，`:215`/`:239` 是 --usage/--info 入口，`:95` `bundle::verify` 找 /boot 等候选位置的内核 config 逐一查 CONFIG_NAMESPACES/USER_NS/SECCOMP_FILTER。**兼容层**：`bin/compat.h:30` 整体 `#ifdef __GLIBC__`——glibc 分支 `:31-32` 宏直通系统 getmntent_r/lastlog；musl 分支 `:75` 手写重入版解析器（fgets+sscanf 偏移+八进制转义还原）、`:116` `struct compat_lastlog` 按 `__x86_64__` 修正 time_t 布局。

## 外部连接

bundle 环的另一半是 makeself：enroot-makeself 只负责把 bundle.sh 打成头+尾数据段，真正的解包逻辑全在 bundle.sh 自身——.run 文件在**没装 enroot 的目标机**上可直接执行（sh 即可解释头），解包后 source 拷入的 runtime.sh 以同参数语义启动容器。FUSE 侧 `src/runtime.sh:182` `_mount_rootfs` 与 `:149` `_mount_rootfs_shim` 成对：shim 负责拉 squashfuse/fuse-overlayfs 并等 mountpoint 就绪，rootfs 用 fifo+`:199` `set -m` 进程组+SIGSTOP 孤儿规则（`:212` 检查）绑定生命周期——进程组被孤儿化时内核 SIGHUP 杀掉 FUSE 守护，替代 subreaper/pidns。

## 数据流

bundle 生成：容器目录 + {common.sh,runtime.sh} + enroot.conf → makeself --header bundle.sh → 单文件 .run。bundle 运行：sh .run → bundle::_check 校验 → bundle::extract dd 解包 → source runtime.sh → runtime::start 同参数启动。getmntent_r 数据流：enroot-mount 读 /proc/self/mountinfo 或 fstab → compat_getmntent_r（musl 下走 compat.h:75 手写版）逐行填 struct mntent → mount_opts 表翻译选项。

## 设计决策

①「脚本身兼数据」双态文件换取零依赖分发——代价是 bundle.sh 改动必须极端保守（老 .run 包里嵌的是旧版本头）；②musl 而非 glibc 静态链：musl 对 static-pie 支持干净，但 getmntent_r/lastlog 签名与 glibc 不同，compat.h 用宏层抹平；③libbsd 只 bundle 5 个源文件（`deps/Makefile:47` -isystem overlay 注入头）而非引整个库，`deps/Makefile:4` flock AR 锁防并发构建；④tree-sitter 对 `#ifdef __GLIBC__` 块与 fparseln（`deps/libbsd/src/fparseln.c:71`）零提取——图谱该域全部手补，是本仓最大的工具盲区。

## 新人提示

改 bundle.sh 前先想清楚：所有存量 .run 包内嵌的是旧头，向后兼容语义不能破。读 compat.h 从 `:30` 的 #ifdef 开始建立两分支心智图，再对照 glibc mntent.h 看 `:75` 手写版缺了什么（提示：锁与流状态）。验证 .run 兼容性直接 `./xx.run --verify`（bundle::verify 会查宿主内核 config），比翻 doc/requirements.md 更快。图谱 caveat：本域函数行号系源码手补产物，引用前建议 sed 复核。

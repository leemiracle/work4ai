# enroot Onboarding（NVIDIA/enroot v4.2.0）

> 图谱基线：226 节点 / 329 边 / 5 层 / 7 步 tour · fingerprints 88 文件 @ead3a25e · 源码锚全部从仓内核实（2026-11-07）

## 1. 项目定位：无特权用户态容器运行时

enroot 是 NVIDIA 开源的**用户态容器运行时与镜像打包系统**，README 自我定位为「把容器/OS 镜像变成无特权沙箱的增强版 chroot」。三条设计铁律（README.md）：

- **KISS、无守护进程**：没有 dockerd/runc 之类的常驻进程，全部操作是短命令直接完成；
- **完全无特权、多用户**：普通用户即可 import/create/start 容器，靠 user namespace 而非 setuid daemon 实现；
- **弱隔离换性能**：刻意不做强隔离（HPC 场景信任域内），换来 3-5 倍速的 Docker 镜像导入与接近原生的启动开销，内建 libnvidia-container GPU 支持。

它是 Slurm 集群上跑 PyTorch NGC 容器的事实标准搭档（PyTorch 官方 HPC 文档推荐），与 k8s 生态的 containerd/runc 完全不同谱系。版本锚：`Makefile:16` `VERSION := 4.2.0`。

## 2. 三层架构：CLI 模板 → shell 库 → 五个 C 工具

全仓 88 个指纹文件分三层（图谱 L01/L04/L05）：

**① 入口层** `enroot.in`（858 行，构建期 `Makefile:124` 用 sed 把 `@sysconfdir@/@libdir@/@version@` 替换进模板生成 `enroot` CLI）。它内嵌 `config::` 配置装载体系：`enroot.in:27` `config::export` 统一管理「文件值→环境默认值」覆盖序，`enroot.in:31` `config::load` 逐行读键值，`enroot.in:50` `config::init` 按「全局 enroot.conf → drop-in conf.d → 环境默认」三级合并，`enroot.in:71` 首先装载 `@sysconfdir@/enroot.conf`。13 个子命令（import/create/start/exec/export/bundle/load/list/remove/batch/version…）在 case 分派表里调度到 src/ 库函数。

**② shell 库层** `src/common.sh`（fanIn=12 的公共底座）、`src/docker.sh`（镜像导入）、`src/runtime.sh`（容器全生命周期）、`src/bundle.sh`（自解压包头）。全部以 `命名空间::函数` 组织，`src/common.sh` 以 `_COMMON_SH_` 哨兵变量实现 include guard。

**③ C 工具层** `bin/` 下五个辅助二进制 + 两个共享头。这是全仓唯一的 C 代码，全部以 musl 静态 PIE 编译（`Makefile:113` musl-gcc 包装器、`Makefile:114` `-static-pie`，`Makefile:21` `FORCE_GLIBC` 可退回 glibc 动态链）。

## 3. 五工具链精讲（bin/）

五个 C 二进制各司一职，共享 `bin/common.h`（fanOut=14 的 C 层枢纽）：

- **enroot-mount**（`bin/enroot-mount.c:623` main）：fstab 语义挂载器。`bin/enroot-mount.c:54` 的 `mount_opts[]` 静态表把字符串选项（bind/atime/dev…）映射到 `MS_*` 标志位，capability 升降仅包裹在每次 mount(2) 前后。它解析 fstab 用的是自带的 `compat_getmntent_r`（见 §4 glibc 盲域）。
- **enroot-nsenter**（`bin/enroot-nsenter.c:503` main）：容器进入器。创建全套新命名空间或 `--target` 注入既有进程；`bin/enroot-nsenter.c:115` 手写 BPF `sock_filter` 数组按架构号白名单化 execve 等系统调用；`bin/enroot-nsenter.c:73` 在 `SYS_pidfd_open` 未定义时以裸 syscall 号 434 兜底支持旧内核，`:206` 是 pidfd_open 包装函数——pidfd 用于精确信号转发。
- **enroot-switchroot**（`bin/enroot-switchroot.c:730` main）：容器伪 init。切根、丢特权、完成登录会话初始化后 exec 目标程序。两个精妙实现：rcfile 通过 mmap+memfd（`bin/enroot-switchroot.c:117` map_fd、`:125` memfd_create）在 chroot 后仍可访问；config 参数表用 bundled BSD 的 SLIST 单链表（`:70` SLIST_HEAD 声明、`:258` 用 `fparseln` 逐行解析续行配置）。
- **enroot-aufs2ovlfs**（`bin/enroot-aufs2ovlfs.c:135` main）：把 AUFS 白标记转 overlayfs 语义——`bin/enroot-aufs2ovlfs.c:33` 定义 `.wh.` 前缀识别，`:63` do_mknod 创建 0,0 字符设备白出，`:85` 写 `trusted.overlay.opaque` xattr。`:155` 有 `#if 0` 保留的 userns 无特权路径，因内核限制被禁用——需要 CAP_MKNOD/CAP_SYS_ADMIN 才能工作。
- **enroot-mksquashovlfs**（`bin/enroot-mksquashovlfs.c:58` main）：导出侧伙伴。私有 mount 命名空间内以 `:89` `lowerdir=` 挂只读 overlay，`:94-96` 丢 CAP_SYS_ADMIN + 设 no_new_privs 后 `:100` execvpe mksquashfs 把联合视图压成 squashfs。

公共底座 `bin/common.h`：`:39` `struct capabilities_v3` 是 capset/capget 位图载体；`:57` `__attribute__((constructor))` 让每个程序启动时读 ENROOT_DEBUG 环境变量开调试；`:93` `unshare_userns` 创建用户命名空间并写 uid_map/gid_map（remap_root 时映射为容器内 root）——这是无特权容器化的核心原语；`:148` `load_environment_fd` 先 clearenv 再逐行 setenv 整体替换环境，`:186` `load_environment` 是其文件入口，enroot exec 的环境注入即由此实现。

两个辅助二进制装 file capabilities（`Makefile:173-175`）：mksquashovlfs 得 `cap_sys_admin+pe`，aufs2ovlfs 得 `cap_sys_admin,cap_mknod+pe`——这就是「无 setuid 无守护进程仍能挂载/创建设备节点」的权限答案；deb/rpm 包的 postinst/prerm 对称地 setcap/回收。

## 4. glibc 兼容层：图谱里的「全盲域」

`bin/compat.h` 整体包裹于 `#ifdef __GLIBC__`（`bin/compat.h:30`）：glibc 下 `:31-32` 把 `compat_getmntent_r/compat_lastlog` 宏直通系统实现；非 glibc（musl）时提供手写实现——`:75` 起的 getmntent_r 重入版解析器（fgets 逐行 + 八进制转义还原）、`:116` 起的 `struct compat_lastlog`（按 `__x86_64__` 修正 time_t 布局差异）。**enroot 以 musl 静态编译，所以 mount/switchroot 实际永远走手写分支**。tree-sitter 对这层条件编译全盲（零提取），图谱中该域函数节点全部为批阶段源码手补——这是本仓最重要的解析盲区，读码时别指望工具索引能覆盖 compat.h。

bundled libbsd（`deps/libbsd/`）只编 5 个源文件成静态库：`deps/libbsd/src/fparseln.c:71`（fparseln，switchroot 配置解析用，tree-sitter 同样未提取）、`deps/libbsd/src/closefrom.c:192`（closefrom：先试 close_range(2) 系统调用、失败扫 /proc/self/fd、再退朴素循环——libc polyfill 的三段式典型结构）、`deps/libbsd/src/strtoi.c:48`（带范围钳制的整数解析）。overlay 头经 `deps/Makefile:47` `-isystem libbsd/include/bsd` 注入。`deps/Makefile:4` 用 `AR := flock $(LOCKFILE) $(AR)` 文件锁实现多进程构建互斥。

## 5. bundle↔runtime 互引：makeself 自解压的双脚本闭环

离线分发是 enroot 的招牌能力，实现是**两个 shell 文件互相引用构成的自举环**：

- `src/runtime.sh:632` `runtime::bundle() ()` 打包侧：`:693` 把 `common.sh,runtime.sh` 两个库拷进镜像的 bundle_lib_dir，`:709` 调 `enroot-makeself --header bundle.sh` 生成 .run 自解压包（复用镜像原压缩算法，ENROOT_BUNDLE_CHECKSUM 开 sha256）。`enroot-makeself` 不是自研——`deps/Makefile:35` 把上游 makeself/makeself.sh 改名安装为 dist 产物。
- `src/bundle.sh` 运行侧：.run 文件的头就是它。`src/bundle.sh:49` `bundle::_dd` 按偏移+尺寸从自身文件 dd 出数据段（progress= 输出配 pv 风格进度条），`:193` `bundle::extract` 逐段 `dd|解压|tar` 展开到目标目录，`:95` `bundle::verify` 找内核 config 检查 CONFIG_NAMESPACES/USER_NS/SECCOMP_FILTER 等宿主兼容性。

所以 bundle.sh 是「脚本身兼数据」的双态文件（文件本体既是库又是生成的 .run 包头），解包后 source 拷入的 runtime.sh 以同参数语义直接启动容器——目标机**不需要装 enroot** 就能跑 .run 包，这是它区别于 docker save/load 的根本设计。

FUSE 内存容器同文件另一绝技：`src/runtime.sh:182` `_mount_rootfs` 用 fifo + `:199` `set -m` 新进程组 + SIGSTOP 孤儿规则（`:212` 检查点）替代 subreaper/pidns 管理 squashfuse/fuse-overlayfs 守护——进程组被孤儿化时内核发 SIGHUP，FUSE 生命周期就此绑死容器，`:149` `_mount_rootfs_shim` 负责 squashfuse 拉起与 mountpoint 就绪等待。

## 6. hooks 体系：三类目录 + 12 个脚本

配置协议三类目录（environ.d/mounts.d/hooks.d）由 `src/common.sh:206` `common::runparts` 统一遍历执行。`conf/hooks/` 下 8 个标准 hook（编号即执行序）：aptfix/cgroups/devices/home/localtime/shadow（10-*）、nvidia（98）、mellanox（99）；`conf/hooks/extra/` 另有 4 个非默认（mig-config/sharp/slurm-pmi/slurm-pytorch）。

三个代表实现的 Bash 技巧值得学：`conf/hooks/10-cgroups.sh:18` `shopt -s lastpipe` 让管道尾进程的变量赋值在当前 shell 生效；`conf/hooks/99-mellanox.sh:43-54` 直接 `(. "$uevent")` source /sys 的 uevent 文件取 DEVNAME/NAME，`:40` 关联数组 providers 记录驱动需求；`conf/hooks/extra/50-slurm-pmi.sh:24` `compgen -e "SLURM_"` 前缀枚举环境变量避免依赖 env 外部命令。GPU 注入是 `conf/hooks/98-nvidia.sh`：`:30` 组装 `--no-cgroups --ldconfig=@...` 参数，`:33-37` 按 NVIDIA_VISIBLE_DEVICES 加 --device，`:80` 起支持 GDRCopy/IMEX 通道设备，最终 exec nvidia-container-cli configure。

## 7. 打包自举：用 enroot 构建 enroot（dogfooding）

pkg/ 目录是全仓最有性格的部分——**自己的发布包在自己的容器里构建**：

- `pkg/debbuild:1` shebang 是 `#!/usr/bin/enroot batch`，`:6` `mounts()` 把仓库源码 bind 进容器 `/usr/local/src/enroot`，environ()/rc() 两个函数与 mounts() 一起构成 batch 配置脚本的 runtime 装配协议——在 ubuntu.sqsh 容器内装 debhelper 后 make deb；`pkg/rpmbuild` 是 centos.sqsh 的 RPM 对称版。
- `pkg/runbuild:15` 更彻底：`enroot import docker://busybox:musl` 拉最小镜像，注入打印成功的 /etc/rc，走完 import→create→export→bundle 全链路产出 `enroot-check_<ver>_<arch>.run`——既是发布物也是端到端冒烟测试。
- `pkg/release/` 的 Dockerfile.ubuntu/Dockerfile.almalinux 提供构建容器（almalinux 版 TARGETARCH 参数化，x86_64 交叉编译 aarch64），deb/rpm 双风味各出标准与 hardened 包（后者关 ALLOW_SPECULATION/INHERIT_FDS 宏）。

## 8. 数据流总览与上手路径

一条主线串起全仓：**docker:// URI →（docker::import `src/docker.sh:453` 并行下载层 + aufs2ovlfs 转白出 + `src/docker.sh:343` docker::configure 把 Volumes/Entrypoint/Env 翻译成 fstab/rc/environment）→ .sqsh 镜像 →（`src/runtime.sh:401` runtime::create unsquashfs 落盘 或 `:480` runtime::load squashfuse 内存直挂）→ runtime::start `:294` 三阶段装配（_do_environ `:32` → _do_hooks `:93` → mounts）→ enroot-nsenter → enroot-switchroot → 容器内 login shell**；旁路 export 反向压回 .sqsh，bundle 打成 .run 离线出走。

上手建议：先读 `doc/usage.md` 与 `doc/configuration.md`（五层配置来源）建立框架；再按 `bin/common.h` → 五个 .c → `src/common.sh` → `src/runtime.sh` 顺序精读（图谱 tour t01-t07 即此序）；跑一遍 `make && sudo make install` 后用 `enroot import docker://ubuntu && enroot create` 验证环境；最后拿 `pkg/runbuild` 产出一个 enroot-check.run 体验 bundle 闭环。图谱细节见同目录 `explain/` 三篇（五工具链 / bundle-runtime 与 glibc 兼容 / hooks 与自举打包）。

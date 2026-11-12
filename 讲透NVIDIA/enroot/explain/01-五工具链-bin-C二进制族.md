# 01 · 五工具链：bin/ 下的 C 二进制族

> 锚全部源自 /usr-data/data2/repos/agent-repos/NVIDIA/enroot 核实（2026-11-07）

## 角色定位

bin/ 是 enroot 唯一的 C 代码域：五个辅助二进制承担 shell 干不了的特权原语操作（mount/mknod/namespace/切根），全部 musl 静态 PIE 编译（`Makefile:113-114` musl-gcc + `-static-pie`），产出自包含可执行文件、无 libc 依赖。共享头 `bin/common.h`（fanOut=14）提供 capability 位图、userns 创建、环境加载三大原语。

## 内部结构

**enroot-mount**（`bin/enroot-mount.c:623` main）：fstab 语义挂载器。`:54` `mount_opts[]` 静态表把字符串选项映射到 `MS_*` 标志（`:44` MS_PROPAGATION 聚合传播属性位），支持 bind/rbind/overlay/squashfs/tmpfs；每次 mount(2) 前后精确升降 capability。**enroot-switchroot**（`:730` main）：容器伪 init，切根+丢特权+登录会话初始化（passwd/MOTD/时区/utmp/lastlog）后 exec 目标；`:117` map_fd + `:125` memfd_create 让 rcfile 在 chroot 后仍可访问，`:70` SLIST 链表存参数、`:258` 用 fparseln 解析带续行的配置。**enroot-nsenter**（`:503` main）：容器进入器，创建或 `--target` 注入命名空间；`:115` 手写 BPF sock_filter 按架构白名单系统调用，`:73` SYS_pidfd_open 未定义时兜底裸 syscall 号 434。**enroot-aufs2ovlfs**（`:135` main）：`:33` 识别 `.wh.` 白标记，`:63` do_mknod 造 0,0 字符设备白出，`:85` 写 trusted.overlay.opaque xattr；`:155` `#if 0` 保留的 userns 无特权路径因内核限制禁用。**enroot-mksquashovlfs**（`:58` main）：`:89` lowerdir= 挂只读 overlay，`:94-96` 丢 CAP_SYS_ADMIN+no_new_privs，`:100` execvpe mksquashfs。

## 外部连接

公共底座 `bin/common.h`：`:39` capabilities_v3 位图结构是五个二进制权限操作的载体；`:57` constructor 属性启动即读 ENROOT_DEBUG；`:93` unshare_userns 写 uid_map/gid_map（remap_root 决定映射成容器 root 还是同 id）；`:148` load_environment_fd 先 clearenv 再逐行 setenv 整体换环境。三个 bundled libbsd 函数支撑：`deps/libbsd/src/closefrom.c:192` closefrom 三段式探测（close_range→/proc/self/fd→朴素循环）、`deps/libbsd/src/strtoi.c:48` 带钳制的整数解析、`deps/libbsd/src/fparseln.c:71` 续行感知的行读取。权限答案在 `Makefile:173-175`：setcap 给 mksquashovlfs `cap_sys_admin+pe`、aufs2ovlfs `cap_sys_admin,cap_mknod+pe`——无 setuid 无守护进程也能挂载。

## 数据流

start 路径：runtime::start 装配完环境/fstab/hooks 后 fork enroot-nsenter（建 user/pid/mount/net 命名空间+seccomp）→ nsenter exec enroot-mount 处理 fstab → exec enroot-switchroot 切根+会话初始化 → login shell。exec 路径：nsenter `--target <pid>` 直接加入运行中容器。export 路径：mksquashovlfs 私有 mount ns 内造 overlay 联合视图压 squashfs。import 路径：aufs2ovlfs 在下载的层目录上转白出供 mksquashfs 叠加。

## 设计决策

①静态 musl 而非 glibc：NFS/HPC 环境无常驻 libc 假设，`Makefile:21` FORCE_GLIBC 留退路；②capability 精确包裹而非整体提权——每次系统调用前后 CAP_SET/CAP_CLR（aufs2ovlfs do_mknod 是范本）；③手写 BPF seccomp 白名单而非 SCMP_ACT_ERRBPF 库依赖，代价是按架构维护 syscall 表；④fork+exec 链（nsenter→mount→switchroot）替代长驻 init，每个环节都是一次性程序。

## 新人提示

读码顺序 common.h → mount.c → switchroot.c 最陡也最值；compat.h 那层是解析盲区（`bin/compat.h:30` `#ifdef __GLIBC__` 内 tree-sitter 全盲），grep 手翻别信工具索引；调试直接 `ENROOT_DEBUG=1 enroot start ...`，constructor 会把 warndbg（`bin/common.h:64`）全打开；白出语义（.wh. 前缀 vs opaque 目录）建议对照 overlayfs 文档读 aufs2ovlfs 的 33-100 行，这是理解 Docker 镜像层合并的最短路径。

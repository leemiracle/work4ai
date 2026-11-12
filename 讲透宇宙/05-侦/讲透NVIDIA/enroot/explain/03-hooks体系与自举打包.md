# 03 · hooks 体系与自举打包（dogfooding）

> 锚全部源自 /usr-data/data2/repos/agent-repos/NVIDIA/enroot 核实（2026-11-07）

## 角色定位

hooks 是 enroot 的「运行时插件协议」——容器 start 前在宿主侧执行的 shell 片段，用环境变量（ENROOT_MOUNTS/ENROOT_ENVIRON）向运行时回写装配指令；pkg/ 则是全仓最有性格的 dogfooding 域：enroot 的 deb/rpm 发布包在 enroot 自己的容器里构建。

## 内部结构

**hook 族**：`conf/hooks/` 8 个标准 hook 按编号序执行——aptfix/cgroups/devices/home/localtime/shadow（10-*）、nvidia（98）、mellanox（99）；`conf/hooks/extra/` 4 个非默认（mig-config/sharp/slurm-pmi/slurm-pytorch）。三个代表实现：`conf/hooks/10-cgroups.sh:18` `shopt -s lastpipe` 让管道尾进程变量赋值在当前 shell 生效，解析 /proc/self/cgroup 后把所属 cgroup 子树（含 SLURM 步骤 /.. 回退）rbind 进容器——cgroup 继承而非虚拟化；`conf/hooks/99-mellanox.sh:43-54` 直接 `(. "$uevent")` source /sys uevent 文件取 DEVNAME/NAME 枚举 InfiniBand 设备，`:40` 关联数组 providers 记驱动需求，issm（SubNet Manager）设备仅 ENROOT_ALLOW_SUPERUSER 且 uid_map 显示真实 root 才挂；`conf/hooks/extra/50-slurm-pmi.sh:24` `compgen -e "SLURM_"` 前缀枚举环境变量免依赖 env 命令。GPU 注入 `conf/hooks/98-nvidia.sh`：`:30` 组装 `--no-cgroups --ldconfig=@$(command -v ldconfig...)`，`:33-37` 按 NVIDIA_VISIBLE_DEVICES 加 --device，`:80` 起 GDRCopy/IMEX 通道设备，`:73-74` 找不到 nvidia-container-cli 时给出 libnvidia-container 链接报错。

**自举域 pkg/**：`pkg/debbuild:1` shebang `#!/usr/bin/enroot batch` + `:4` `#ENROOT_ROOTFS=ubuntu.sqsh` 注释式配置——`:6` `mounts()` 把仓库 bind 进容器 /usr/local/src/enroot，`:10` environ()、`:16` rc() 三函数正是 batch 命令的 runtime 装配协议；容器内装 debhelper 后 make deb 出标准/加固双风味包。`pkg/rpmbuild` 是 centos.sqsh 对称版。`pkg/runbuild:15` `enroot import --arch ${arch} -o busybox.sqsh docker://busybox:musl`，`:18-20` 注入打印 "Bundle ran successfully!" 的 /etc/rc，走完 import→create→export→bundle 全链路产出 enroot-check_<ver>_<arch>.run——发布物兼端到端冒烟测试。

## 外部连接

遍历协议在 `src/common.sh:206` `common::runparts`：list/exec 双模式统一走 environ.d/mounts.d/hooks.d 三目录。执行时序挂在 `src/runtime.sh` 的 start 装配线：`:32` _do_environ → `:64` _do_mounts_init → `:93` _do_hooks（hook 在此跑、回写的 ENROOT_MOUNTS 生效）→ `:120` _do_mounts_fini → `:138` _do_rc。文档侧 `doc/standard-hooks.md`（fanOut=8）逐个说明 8 hook 的触发条件与开关。构建容器在 `pkg/release/Dockerfile.ubuntu`（debhelper 链）与 `Dockerfile.almalinux`（TARGETARCH 参数化，x86_64 下载 ARM 14.3 交叉工具链编 aarch64）。

## 数据流

start 装配线：enroot.conf/d 三层合并 → hook 执行回写 ENROOT_MOUNTS/ENROOT_ENVIRON → enroot-mount 按 fstab+回写项挂载 → nsenter+switchroot 进容器。自举链：宿主 make → pkg/debbuild（enroot batch 语义）→ ubuntu.sqsh 容器内 make deb → DEB 回到宿主 dist/ → postinst `pkg/deb/PACKAGE+caps.postinst` setcap 两个辅助二进制——工具自身完成了一次完整的「容器装配→执行→产物导出」循环。

## 设计决策

①hook 用「约定优于配置」：不搞 DSL，就是 shell + 环境变量回写，HPC 管理员零学习成本；②编号前缀定执行序（runparts 按名排序），98/99 留给 GPU/IB 这类依赖前面挂载就绪的硬件 hook；③自举打包同时是回归测试——pkg/runbuild 每次发布都把 import/create/export/bundle 四命令全跑一遍；④加固风味（hardened）关 ALLOW_SPECULATION/INHERIT_FDS 宏，用同一份源码出安全/性能两版二进制。

## 新人提示

写自定义 hook 从 `conf/hooks/extra/50-slurm-pmi.sh` 抄骨架最稳（它展示了环境枚举+条件回写的完整范式）；排查「hook 没生效」先看 `src/common.sh:190` common::envfmt 的清洗规则——非法行/保留变量会被静默剔除。想理解 enroot batch 配置脚本形态，`pkg/debbuild` 12 行就是全部语义（shebang 指定 rootfs，三函数装配运行时）。graph caveat：hooks 层在图谱 L02 的代表节点为空（分层产物），hook 文件节点实际落在 L01/L05，检索时直接按 conf/hooks/ 路径找。

# 03 · Pyxis 与 NHC：容器作业入口与节点健康门禁

## 角色定位

pyxis 与 nhc 是 Slurm 产线的两个"插拔件"：pyxis（roles/pyxis）把 Enroot 容器通过 SPANK 插件接进 sbatch/srun，让用户 `srun --container-image=...` 原生跑 NGC 容器；nhc（roles/nhc）是 Node Health Check，Slurm 的 HealthCheckProgram 调它在作业前后体检节点，不合格即 drain。

## 内部结构

pyxis 分两层。main.yml 先修宿主机：Ubuntu 23.10+ 默认开 `kernel.apparmor_restrict_unprivileged_userns=1`，enroot-nsenter 会报 "failed to create user namespace: Permission denied"（`main.yml:16-20` 注释）；角色优先走窄授权路径——探测 /proc 旋钮（:21-24）、装 AppArmor userspace（:29-37）、缺失 apparmor_parser 直接 fail 并给出两个出路（:49-62）、安装并加载 enroot-nsenter 专属 profile（:66-101，是否加载由内核 profile 列表判定，手工卸载后重跑可收敛）；`pyxis_userns_allow_globally` 为真才退回 sysctl 全局豁免（:116-126，注释明言这会降全主机安全默认值）。随后 :128-140 把 enroot 的 slurm-pmi/slurm-pytorch hook 链接进 /etc/enroot/hooks.d/——这就是 slurmd PATH drop-in 事故的源头组件。tasks/pyxis.yml 负责编译：下载源码到 /usr/local/src/pyxis（:9-16），`make -j` 带 `CPPFLAGS: -I {{ slurm_install_prefix }}/include`（:29-42）对齐自编译 Slurm 的头文件路径，产物 `spank_pyxis.so` 置 0755（:65-68），plugstack 两级配置：顶层 `plugstack.conf` 一行 include（plugstack.conf:1），`plugstack.conf.d/pyxis.conf` 一行 `required /usr/local/src/pyxis/spank_pyxis.so`（pyxis.conf:1）。nhc 是经典的源码装：探测 `nhc_install_dir/sbin/nhc` 存在且不 force 则跳过 build（main.yml:19-28），否则下载 tar.xz（:45-51）configure/make。

## 外部连接

SPANK 协议是 pyxis 与 slurmd 的契约：restart slurmctld/slurmd 的 notify 在 build 后触发（tasks/pyxis.yml:39-41），Slurm 侧由 slurm-cluster.yml:144-150 的双条件 `slurm_install_enroot + slurm_install_pyxis` 引入。nhc 与 Slurm 的接线在两处：`sysconfig_nhc.j2:2-4` 写 `NHC_RM=slurm` 并指定 `SLURM_SINFO/SLURM_SCONTROL` 全路径（自编译前缀场景），slurm.conf:72 的 `HealthCheckProgram` 指向它。GPU 驱动、DCGM、InfiniBand 工具链都是 nhc 检查的外部依赖。

## 数据流

NHC 是"双配置"结构：`nhc.conf`（模板渲染，nhc/tasks/main.yml:86-92）声明"跑哪些检查"，`nhc/scripts/deepops.nhc`（:78-84 拷入）提供"检查的函数体"。nhc.conf.j2 由 facts 驱动：CPU 拓扑（:4 `check_hw_cpuinfo` 读 ansible_local.topology）、内存 ±5% 容差（:7）、sshd+slurmd 存活（:20-21）；`ansible_local.gpus.count > 0` 才展开 GPU 段（:23），`check_nv_gpu_count`（deepops.nhc:12-20）默认启用，DCGM diag（:41-47）、驱动版本（:3-10 读 /proc/driver/nvidia/version）、retired pages（:22-28）、PCIe 链宽（:30-39）以注释态供选配。`check_xid_errors`（:89-97）用 journalctl 抓近 1 小时 "NVRM: Xid" 并排除 Xid 94——GPU 掉线前最常见的内核信号。

## 设计决策

① pyxis 全程不碰 Slurm 源码，仅靠 plugstack 声明 `required`——加载失败即作业失败，宁可硬失败不静默降级。② AppArmor 走"单可执行文件 profile 优先、全局豁免 opt-in"的最小权限次序。③ nhc 版本探测跳过重编（幂等）但 deepops.nhc 无条件覆盖拷贝——检查集始终随 DeepOps 版本走。④ `resize /run` tmpfs（pyxis/tasks/main.yml:150-157）针对 pyxis 默认 runtime_path=/run/pyxis 撑爆小 tmpfs 的镜像导入，暴露 `pyxis_run_tmpfs_size`。

## 新人提示

排障：容器作业报 "Command not found: scontrol" 是 PATH drop-in 问题（见 02 篇）；报 user namespace Permission denied 是 AppArmor profile 未加载；节点被自动 drain 先手跑 nhc 看哪条检查红——nhc.conf 的注释行就是可开启的检查菜单，`config.example` 的 `nhc.conf.example-dgxa100` 是 DGX A100 全量参考。

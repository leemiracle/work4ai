# 03 · kmsg / modprobe 工具链与守护同步（kmsg.rs / syslog.rs / modprobe.rs / kernel_params.rs / daemon.rs）

## 角色定位

这一组是"最小 init 世界的基础设施"：没有 systemd、udev、配置文件，NVRC 用四件工具补齐——kernel_params.rs 把 `/proc/cmdline` 当配置文件，modprobe.rs 包装模块加载，kmsg.rs+syslog.rs 组成"日志即信号"的守护就绪同步通道，daemon.rs 在其上装配 NVIDIA 守护群。

## 内部结构

- kernel_params.rs（487 行）：`kernel_cmdline()` 用 OnceCell 读一次缓存（kernel_params.rs:12-19）；`process_kernel_params` 的 match 覆盖 `nvrc.log/nvrc.uvm.persistence.mode/nvrc.uvm.tools/nvrc.dcgm/nvrc.smi.srs/lgc/lmc/pl` 九键（kernel_params.rs:65-81）。宽容布尔解析 on/true/1/yes（:23-36），但 `nvrc.smi.srs` 走严格版——nvidia-smi 只认 0/1，宽容会让 GPU 静默 NotReady（:113-120）。`nvrc.log` 顺手开 `/proc/sys/kernel/printk_devkmsg`（:109-110）。`try_process_kernel_params` 是给 fuzz 目标的 Result 孪生（cargo-fuzz 用 panic=abort，catch_unwind 失效，:56-59）。
- modprobe.rs：`load()` 两个特判——单 GPU 给 nvidia 模块追加 `NVreg_NvLinkDisable=1`（modprobe.rs:11,25-27）；gpu 扩展在场时 `--dirname /run/kata-extensions/gpu`（modprobe.rs:12-13），且只对 `nvidia*` 模块生效（gpu_extension.rs:66-68），`ib_umad`/`mlx5_ib` 等树内模块留在基础镜像。
- kmsg.rs：`kernlog_setup` 把四个 rmem/wmem sysctl 全调 16MB 防驱动突发丢日志（kmsg.rs:13-34）；`open_kmsg("/dev/kmsg")` 实际打开 `/run/syslog.log`（kmsg.rs:51-56）——同步不能依赖 debug 日志开关；`wait_for_marker` 非阻塞读行、EOF 退化 `try_poll_for`、单次等待上限 500ms（kmsg.rs:89-112）。
- syslog.rs：绑 `/dev/log` datagram socket、非阻塞、4KB 缓冲剥 PRI 前缀（syslog.rs:39-83）；`try_poll` 家族错误吞掉不 panic——handoff 循环里一次 I/O 错不许断电（syslog.rs:93-103）。
- daemon.rs：persistenced 等 `"Local RPC services initialized"` 600s（daemon.rs:56-63）；FM 等 `"FM starting NvLink Inband"` 120s（daemon.rs:108-110）；fabricmanager.cfg 走 copy→write→chmod 0o400 模式（daemon.rs:102-107）；FABRIC_MODE_FULL=0/SHARED=1（daemon.rs:46-48），NVL4 配 greedy、NVL5 配 symmetric（"required for CC on Blackwell"，daemon.rs:138）。

## 外部连接

上游消费 `/proc/cmdline`、`/proc/sys/net/core/*`、`/dev/log`、`/run/syslog.log`；下游驱动 execute.rs 的 foreground/background 两模式（execute.rs:24,37）与 gpu_extension::path 路径重映射（DCGM counters CSV，daemon.rs:31-38）。fuzzing.yaml 持续模糊 kernel_params/mount 两个解析面。

## 数据流

cmdline（被度量）→ NVRC 状态字段 → 模式分发时被消费。守护同步流：daemon 子进程 → syslog(/dev/log) → /run/syslog.log → wait_for_marker 阻塞等标记 → 等到才继续装配下一步。这条总线把"进程就绪"降维成"文件里出现一行字"。

## 设计决策

1. **文件而非信号**：日志文件是唯一不依赖日志级别、不依赖父子关系、可在 fork 后继续读的就绪介质（kmsg.rs:48-50 注释）。
2. **先开 reader 再 spawn**：`wait_for_marker_after` 先 open 再 start，标记不可能被错过（kmsg.rs:80-86）。
3. **16MB socket 缓冲**：GPU 驱动初始化时会爆发诊断日志（kmsg.rs:13-15）。
4. **测试可用 /bin/true 代替真 NVIDIA 二进制**：daemon.rs 各 spawn 函数的 bin 参数都可注入（daemon.rs:50-52）。

## 新人提示

`wait_for_marker` 的 EOF 分支（kmsg.rs:108-109）是理解同步机制的钥匙；debug 未开时 `kmsg()` 返回 `/dev/null`（kmsg.rs:39-45），别在 dmesg 找不到日志就以为挂了；modprobe.rs 与 smi.rs 是 src/ 下唯二无 SPDX 头的文件（`grep -L SPDX` 实证）；改守护顺序时每步之后都要 health_checks（main.rs:39,47,66-68）。

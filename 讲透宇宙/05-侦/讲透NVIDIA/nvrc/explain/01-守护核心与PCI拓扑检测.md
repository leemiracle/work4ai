# 01 · 守护核心与 PCI 拓扑检测（main.rs / init.rs / mode.rs / nvrc.rs）

## 角色定位

这四个文件构成 NVRC 的"生物钟"：main.rs 是 103 行的纯分发入口（main.rs:71-103），init.rs 守住 PID 1 身份，mode.rs 用 PCI 拓扑决定"今天是谁"（gpu/cpu/servicevm），nvrc.rs 用一个结构体承载全部运行状态与守护清单。全仓其余 20 个模块都只在 main() 的某一步被调用——理解这四个文件就理解了调用图的骨架。

## 内部结构

- init.rs 的守卫很克制：`as_pid1()`（init.rs:10-12）委托 `as_pid1_with(running_as_init(), exit)`，非 PID 1 时打印 `hash::version_line()` 后退出（init.rs:22-23）——这一行就是 CI 冒烟测试的全部输出。判定用裸 `libc::syscall(libc::SYS_getpid) == 1`（init.rs:29），因为此刻 /proc 尚未挂载、且 hardened_std 目标是纯 syscall。
- mode.rs 的 Detection 结构只有两个字段：`mode: &'static str` 与 `nvswitch: Option<&'static str>`（mode.rs:19-24）。决策核心是 `detect_from()` 对 `(nvswitches, gpus, sw_mng)` 三元组的穷举 match（mode.rs:41-96）：(4,8,0)→gpu+nvl4 裸金属、(4,0,0)→servicevm-nvl4、(0,8,4)→gpu+nvl5、(0,0,4)→servicevm-nvl5、其余组合 panic（mode.rs:90-95）。
- nvrc.rs 的 NVRC 结构（nvrc.rs:15-35）把内核命令行驱动的配置（smi 时钟/功耗/srs、uvm/dcgm 开关、port_guid）与私有 `children: Vec<(String, Child)>` 放在一起；`spawn_daemon`/`track_daemon`（nvrc.rs:41-47）注册，`health_checks()`（nvrc.rs:52-60）在交接前逐个 `try_wait`，非零退出即 panic 关机。

## 外部连接

- 上游：`/proc/cmdline`（kernel_params.rs:15-19）与 `/sys/bus/pci/devices`（mode.rs:16）是两大数据源。
- 下游：main() 按检测结果调用 mode_gpu/mode_nvl4/mode_nvl5（main.rs:90-99）；NVL5 路径要拉 infiniband.rs 的 `detect_port_guid()`（main.rs:59-62）与 daemon.rs 的 NVLSM/FM。
- mode_gpu（main.rs:18-40）串起 modprobe::load、setup_uvm_tools、persistenced、smi 三连、hostengine/dcgm、nvidia_ctk_cdi、srs、健康检查。

## 数据流

sysfs 三计数器（vendor+class 判 NVSwitch/GPU，mode.rs:99-125；Mellanox VPD 内 6 字节窗口搜 SW_MNG，mode.rs:141-143）→ Detection → main() match 分发 → NVRC 状态被 kernel_params 填充后由各装配函数消费 → 子进程句柄进 children → health_checks 兜底。整个流是一次性的、单向的、不可重入——符合"ephemeral VM 一次开机一次初始化"的定位。

## 设计决策

1. **拓扑判定不信任软件，只信 PCI**：SW_MNG 直接裸读 vpd 文件而不等 IB 驱动（mode.rs:127-130 注释），让模式检测可以发生在任何模块加载之前。
2. **未知拓扑宁可关机**：match 的 `_` 分支 panic（mode.rs:91-94），与全仓 fail-fast 哲学一致。
3. **单线程无锁**：PID 1 没有别的线程，fork/exec 的 SAFETY 论证全部建立在这一点上（kata_agent.rs:85-88）。
4. `opt-level="z"` + `panic='abort'`（Cargo.toml:17-23）：一次引导跑一次，体积压倒速度。

## 新人提示

先读 main.rs 再读任何东西；mode.rs 的测试区（mode.rs:148-395）用 TempDir 伪造 sysfs，是学习"环境注入测试"范式的最好样本；注意 crate 名是大写 `NVRC`（Cargo.toml:2），所以 import 全是 `use ::NVRC::...`（main.rs:4-11）；"fork 出 kata-agent 子进程"的说法方向反了——父进程 exec 成 kata-agent（详见 02 篇）。

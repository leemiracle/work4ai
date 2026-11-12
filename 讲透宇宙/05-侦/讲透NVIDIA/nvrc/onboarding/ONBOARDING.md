# NVRC 深度导览（ONBOARDING）

> 基于知识图谱（150 节点 / 233 边 / 8 层 / 9 步 tour，fingerprints 65 文件 @ b9700f3e）与全量源码行号锚核实编写。仓位于 `/usr-data/data2/repos/agent-repos/NVIDIA/nvrc`。

## 一、一页纸定位：这是什么

NVRC 全称 **NVRC - NVIDIA Runtime Container Init**（README.md:1；nvrc.rs:10 注释同称 "NVIDIA Runtime Container init"）——它是跑在 **Kata Containers 机密（confidential）微型 VM** 里的**最小 init 进程（PID 1）**，负责在容器工作负载进场之前完成 GPU 世界的一切初始化：加载内核模块、调频锁频、拉起 NVIDIA 管理守护、生成 CDI 规格，最后把自己交接给 kata-agent。

语言形态是**纯 Rust 单 crate**：`src/` 下 24 个 `.rs` 模块共约 5400 行（Cargo.toml 仅一个 `[package] name = "NVRC"`，依赖只有 nix/log/kernlog/rlimit/libc/once_cell/sha2/cfg-if 八个）。没有任何 Python——如果带着"NVIDIA 生态脚本=Python"的预期进来，第一眼就会被推翻。发布构建追求极小体积：`opt-level = "z"`（注释直言 "PID 1 runs once per boot: size beats speed"）、LTO 全开、strip、`panic = 'abort'`（Cargo.toml:17-23）。

三条理解主线：

1. **fail-fast 哲学**（README.md:9-18）：机密 VM 里任何配置失败都直接断电关机，零恢复逻辑。全仓错误处理靠 `or_panic` 一个扩展 trait 统一（macros.rs:13-17，`#[cold] #[inline(never)]`）。
2. **机密计算安全**：dm-verity 镜像扩展验证、panic 断电、禁模块加载、供应链签名——全都 fail-closed。
3. **交接即终点**：NVRC 不是常驻管理进程，`main()` 最后 fork：父进程 exec 成 kata-agent，子进程退化成 syslog 轮询循环保活（kata_agent.rs:83-97）。

## 二、启动主线：main() 的十二步时序

`main()`（main.rs:71-103）是全仓唯一入口，读懂它就读懂了调用图的主干：

1. `init::as_pid1()`（main.rs:72）——身份守卫。init.rs:28-30 用裸 `libc::syscall(libc::SYS_getpid) == 1` 判定，而非 `std::process::id()`：此刻 `/proc` 还没挂载（mount::setup 在后面），且 hardened_std 的目标是纯 syscall 路径。非 PID 1（CI 冒烟、开发 shell）时打印版本摘要行后 `exit(0)`（init.rs:16-24），这是 CI 唯一可观测输出。
2. `lockdown::set_panic_hook()`（main.rs:74）——panic 即 `reboot(RB_POWER_OFF)`（lockdown.rs:18-20），hook 内先写 `/dev/kmsg` 再 `sync()`（lockdown.rs:40-50），保证 panic 信息留在客户机控制台。
3. `mount::setup()` + `net::loopback_up()`（main.rs:76-77）——挂 proc/sys/dev/run/tmp、拉起回环口。
4. `kmsg::kernlog_setup()` + `syslog::poll()`（main.rs:78-79）——内核日志初始化 + 首轮 syslog 抽干。
5. `init.process_kernel_params(None)`（main.rs:80）——解析 `/proc/cmdline` 里的 `nvrc.*` 参数填充 NVRC 状态（详见第五节）。
6. `hash::self_exe()`（main.rs:81）——对 `/proc/self/exe` 做 SHA-256 打进日志，供与 Rekor 发布证据对账（hash.rs:32-39）。
7. `guest_extension_image::mount_all()`（main.rs:84）——dm-verity 挂载冷插镜像扩展。注意 main.rs:83 的注释：**必须赶在 `disable_modules_loading()` 之前**，否则 dm-verity/erofs 模块加载不进来。
8. `gpu_extension::setup()`（main.rs:87）——绑定扩展固件目录、重建 loader 缓存，"在任何驱动加载前暴露 gpu 扩展 libs/firmware"。
9. `mode::detect()`（main.rs:89）——PCI 拓扑检测运行模式（第三节）。
10. 模式分发（main.rs:90-99）：`cpu` 只打日志；`gpu` 走 `mode_gpu`（加载 nvidia/nvidia-uvm → NVL4/NVL5 特判 → persistenced → smi 调频 → hostengine/DCGM → CDI → srs → 健康检查，main.rs:18-40）；`servicevm-nvl4/nvl5` 走共享虚拟化路径（FABRIC_MODE_SHARED）。
11. `lockdown::disable_modules_loading()`（main.rs:101）——写 `/proc/sys/kernel/modules_disabled` 单向关门（lockdown.rs:58-70）。
12. `kata_agent::fork_agent(POLL_FOREVER)`（main.rs:102）——交接。`SYSLOG_POLL_FOREVER = u32::MAX`（kata_agent.rs:22-23，注释戏称"136 年"）。

## 三、模式检测：一张 PCI 拓扑决策表

mode.rs 的核心是 `detect_from()` 里对三元组 `(nvswitches, gpus, sw_mng)` 的穷举 match（mode.rs:41-96）：

| (NVSwitch, GPU, SW_MNG) | 模式 | 语义 |
|---|---|---|
| (0,0,0) | `cpu` | 无 GPU，裸跑 |
| (0,任意,0) | `gpu` | GPU 直通，无 NVSwitch |
| (4,8,0) | `gpu` + nvl4 | HGX H100/H200/H800 裸金属（三代 NVSwitch） |
| (4,0,0) | `servicevm-nvl4` | GPU 在租户 VM，本机只看得到 4 颗 NVSwitch |
| (0,8,4) | `gpu` + nvl5 | HGX Bx00：GPU 直通 + 4 个 CX7 管理 PF |
| (0,0,4) | `servicevm-nvl5` | 只看得到 CX7 桥的管理 VM |
| 其他 | `panic!` | 未知拓扑直接关机（mode.rs:90-95） |

三个计数器的判据都在 sysfs 上，零外部依赖：

- **NVSwitch**：vendor `0x10de` + class 前缀 `0x0680`（mode.rs:99-111）；
- **GPU**：vendor `0x10de` + class 前缀 `0x03`（display 控制器，mode.rs:113-125）；
- **SW_MNG**：vendor `0x15b3`（Mellanox）且 PCI VPD 里有 `SW_MNG` 六字节标记（`data.windows(6).any(|w| w == b"SW_MNG")`，mode.rs:130-146）。注释点明这是为了**不依赖 IB 驱动是否已加载**——直接裸读 vpd 文件。

NVL5（Blackwell HGX Bx00）是拓扑特判的精华：CX7 网桥替代 GPU 直连做 NVLink 管理（main.rs:50-51），`mode_nvl5` 要先加载 `ib_umad`/`mlx5_ib`、从 `/sys/class/infiniband` 探测端口 GUID（infiniband.rs:18-22，`IS_SM_DISABLED_MASK = 1<<10` 过滤禁用 SM 的口），再起 NVLSM、最后才起 fabricmanager，且 rail policy 必须是 `symmetric`（"required for CC on Blackwell"，daemon.rs:138）——与 NVL4 的 `greedy` 相对。

模式落位后由 NVRC 结构体（nvrc.rs:15-35）承载状态：smi 时钟/功耗/CC Ready State、UVM 开关、DCGM 开关、port_guid，以及私有的 `children: Vec<(String, Child)>` 守护清单。`health_checks()`（nvrc.rs:52-60）对每个已 spawn 的守护做 `try_wait`：非零退出立即 panic 关机——"守护崩了就别交接"。

## 四、机密计算安全核心：fail-closed 三件套

### 4.1 dm-verity 镜像扩展（guest_extension_image.rs，512 行）

"Composable Image Extensions"（ARCHITECTURE.md:434 起）是全仓最重要的机制设计：GPU 用户态（库、模块、固件、工具）不再打进基础 rootfs，而是冷插成 virtio-blk 扩展盘（serial 为 `extension-<name>`），NVRC 负责验证后挂载。核心不变量写在模块头（guest_extension_image.rs:14-17）：

```
device + params   -> verify and mount
device, no params -> panic (verity stripped)
params, no device -> panic (mismatch / missing extension)
```

`plan_mounts()`（guest_extension_image.rs:65-90）做设备↔命令行参数的 1:1 对账，两边任何一边多出来都 panic——**没有未度量的 raw-mount 回退**，这是"机密专用"与普通发行版的本质区别。verity 参数五字段（root_hash/salt/data_blocks/data_block_size/hash_block_size）来自被度量的内核命令行 `kata.extension.<name>.verity_params`，缺一或为零即 fatal（guest_extension_image.rs:133-166）。`veritysetup open` 显式带 `--no-superblock --hash sha256`（guest_extension_image.rs:176-195）；挂载 flags 是 `MS_RDONLY|MS_NOSUID|MS_NODEV`，**刻意不含 NOEXEC**——扩展要出货可执行文件（如 attestation-agent，guest_extension_image.rs:102）。扩展名走 charset 白名单（字母数字加 `_-`）并拒绝全点号名，堵死 `..` traversal（guest_extension_image.rs:209-215，对应测试 :411-416）。

### 4.2 自证摘要（hash.rs）

启动时对 `/proc/self/exe` 算 SHA-256 打进 dmesg（hash.rs:49-51），运维可拿它跟 release 证据里的 cosign/Rekor 摘要比对。但模块头（hash.rs:9-13）极其清醒地写着：**"Not a security primitive"**——被入侵的 NVRC 完全可以谎报自己的哈希，真正的完整性在 execve 之前就已由 dm-verity（块层）、fs-verity（文件层）和 IPE 强制；可信的摘要在 Rekor 里，不在 dmesg 里。GIT_REV（`-dirty` 后缀）只是开发便利戳，同样可伪造（hash.rs:24-30）。

### 4.3 lockdown 与 kata 交接（lockdown.rs / kata_agent.rs）

- panic 断电已述；`disable_modules_loading` 对 `NotFound` 容忍（内核没编 CONFIG_MODULES 时本来就无模块可载），其余错误照旧 panic（lockdown.rs:62-70）。
- kata 交接（kata_agent.rs:83-97）：fork 后**父进程 exec 成 kata-agent**（继承 PID 1 地位），子进程跑 `syslog_loop`——每 500ms `try_poll()` 一次，故意不用会 panic 的版本：子进程继承了断电 panic hook，"kata 还在跑时一次瞬时 I/O 错误不许重启 VM"（kata_agent.rs:67-77）。
- 交接前的 `agent_setup()`：RLIMIT_NOFILE 提到 1048576、`oom_score_adj = -997`（接近不可杀，kata_agent.rs:27-41）。
- 若 gpu 扩展在场，注入 `KATA_ATTESTER_VARIANT=nvidia`（kata_agent.rs:19 与 gpu_extension.rs:102-114）：stock attester 不产出 `gpu0` 证据，GPU KBS 策略永远过不了，nvidia 变体才行。

## 五、内核侧初始化与守护装配

### 5.1 命令行即配置（kernel_params.rs，487 行）

最小 init 没有配置文件、没有环境变量，唯一输入是 `/proc/cmdline`（`OnceCell` 读一次缓存，kernel_params.rs:12-19）。识别的键全部在 kernel_params.rs:65-81 的一个 match：`nvrc.log`（六档级别 + 开 devkmsg，:96-111）、`nvrc.uvm.persistence.mode`、`nvrc.uvm.tools`、`nvrc.dcgm`、`nvrc.smi.srs/lgc/lmc/pl`。布尔解析宽容（on/true/1/yes 任一），但 `nvrc.smi.srs` 用严格版——nvidia-smi 只认 0/1，宽容解析会让每颗 GPU 静默 NotReady（kernel_params.rs:113-120）。

### 5.2 模块加载（modprobe.rs）

`load()` 两个特判：单 GPU 时给 `nvidia` 模块追加 `NVreg_NvLinkDisable=1`（modprobe.rs:11,26）；gpu 扩展在场时 `--dirname` 指向 `/run/kata-extensions/gpu`，NVIDIA 模块从扩展取（modprobe.rs:12；gpu_extension.rs:62-68 只对 `nvidia*` 模块生效，`ib_umad`/`mlx5_ib` 这类内核树内模块留在基础镜像）。

### 5.3 kmsg/syslog 双通道同步

这是全仓最巧的工程：守护进程的"就绪"如何感知？答案是用**日志标记**。

- 写侧：kernlog 初始化时把四个 socket 缓冲 sysctl 全部调到 16MB，防驱动突发日志丢消息（kmsg.rs:13-34）；
- 读侧：`open_kmsg("/dev/kmsg")` 实际打开的是 `/run/syslog.log`（kmsg.rs:51-56）——同步不能依赖 debug 日志开着与否，文件是唯一可靠介质；
- 等待：`wait_for_marker()` 非阻塞读行，EOF 时退化为 `try_poll_for`（单次上限 500ms，kmsg.rs:89-112），超时即 panic。
- 两个生产消费者：nvidia-persistenced 等 `"Local RPC services initialized"`（600s，daemon.rs:56-63）；fabricmanager 等 `"FM starting NvLink Inband"`（120s，daemon.rs:108-110）。

### 5.4 守护群与运行时配置

daemon.rs 装配四类守护：persistenced（UVM 持久默认开）、nv-hostengine + dcgm-exporter（仅 `nvrc.dcgm` 显式开启，`spawn_if_dcgm`，daemon.rs:91-95）、nv-fabricmanager、NVLSM（NVL5 专属）。fabricmanager.cfg 是"copy→write→chmod 0o400"模式的实例：只读 rootfs 上的原件拷到 `/run` tmpfs 再改（FABRIC_MODE/PARTITION_RAIL_POLICY，daemon.rs:99-111）——CLAUDE.md 把它总结为 hardened_std 的 copy-write-seal 约定。DCGM exporter 的 collectors CSV 路径经 `gpu_extension::path()` 重映射（daemon.rs:31-38）。

### 5.5 工具链收尾

- smi.rs：`-lmc/-lgc/-pl` 锁频限功率，`conf-compute -srs` 在 attest 后把 GPU 从 NotReady 翻成 Ready（smi.rs:47-52）；参数未设则全部 no-op。
- toolkit.rs：`nvidia-ctk cdi generate` 产出 `/var/run/cdi/nvidia.yaml`（toolkit.rs:37），扩展模式下补 `--driver-root`/`--dev-root=/`/`--nvidia-cdi-hook-path` 三面旗子（toolkit.rs:39-46；gpu_extension.rs:70-98 记录了每面旗子缺了会怎么坏）。
- uvm.rs：`uvm_tools_enabled` 时 mknod `/dev/nvidia-uvm-tools`，minor 固定 1，major 从 `/proc/devices` 动态查（uvm.rs:8-38，device.rs:4）。

## 六、工程链：18 条 workflow 的供应链矩阵

`.github/workflows/` 下 18 条流水线可分四组：

- **质量主链**：`ci.yaml`（主 CI 在 **g5g.metal**——AWS Graviton 裸金属真机——跑 E2E，ci.yaml:51）、`ci-on-push`、`coverage`（带 per-file 覆盖门，见 init.rs:65-71 的注释）、`static-checks`（clippy/rustfmt）、`fuzzing`（持续模糊 kernel_params 与 mount 两个解析面）、`shellcheck`/`actionlint`/`docs`。
- **供应链安全**：`release.yaml` 用 anchore/sbom-action 出 SPDX JSON、cosign keyless 双签（binary + SBOM 各出 sig/cert/bundle，release.yaml:105-134）；`reproducible.yaml` 从不同目录构建两次强制 sha256 一致（reproducible.yaml:49-62）；`codeql`/`zizmor`/`scorecard`/`revoke-ok-to-test`（防提示注入的 OK-to-test 吊销线）。
- **上游联动**：`kata-checkout`/`update-kata`——与 kata-agent 仓库的契约（`KATA_ATTESTER_VARIANT`）有专门守护。
- **仓库卫生**：`dependabot-auto-merge`。

文档群（L05 层 8 篇）里 ARCHITECTURE.md 是 1074 行权威文档（威胁模型/Rootkit 手法/防护机制，:434 起是 Composable Image Extensions 的设计出处），VERIFY.md 是签名核对复现指南，CLAUDE.md 记录 no_std 长期路线图（11 条 checklist）与 hardened_std 白名单原则——NVRC 的终局是退掉 libstd、纯 syscall 接口、路径/二进制全白名单。

## 七、新人上路：阅读顺序与常见坑

**推荐阅读顺序**：README.md（含 mermaid 全流程图）→ ARCHITECTURE.md 的 Introduction + Composable Image Extensions 两节 → main.rs（103 行，主干全在）→ mode.rs 的 match 表 → guest_extension_image.rs → daemon.rs → kata_agent.rs。

**五个必知的坑**：

1. **crate 名是大写 `NVRC`**（Cargo.toml:2），所以 main.rs 里全是 `use ::NVRC::...`（main.rs:4-11）——Rust 惯例 crate 名应小写，这是全仓有意为之的异类。
2. **"fork 出 kata-agent 子进程"是反的**：父进程 exec 成 kata-agent，子进程才是 syslog 轮询器（kata_agent.rs:80-97 的 SAFETY 注释四条都值得读）。
3. **日志默认全关**：kernlog_setup 里 `set_max_level(Off)`（kmsg.rs:25），生产日志去向由 `nvrc.log=` 命令行参数决定；debug 没开时 kmsg() 返回 `/dev/null`（kmsg.rs:39-45）。
4. **or_panic 之外没有错误处理**：任何 `Err` 都是关机。改代码时"防御性检查再降级"在这个仓是反模式（CLAUDE.md 的 offensive programming 原则）。
5. **测试三件套**：`require_root()`（无 root 跳过）、miri `#[ignore]`（fork/syscall 无法模拟）、`--include-ignored` 只在专用 runner 跑（lockdown.rs:81 的注释：模块禁载测试会永久弄脏宿主机）。

**图谱导航**：L01 入口生命周期 → L02 机密防护 → L03 内核侧 init → L04 工具链守护 → L05 文档 → L06 构建配置 → L07 CI/CD → L08 fuzz/发布脚本，与上文二~六节一一对应；9 步 tour 从威胁模型走到质量防线，适合按步打开源文件对照。

# 讲透 NVRC（NVIDIA/nvrc）

NVRC = **NVRC - NVIDIA Runtime Container Init**（README.md:1）：Kata Containers 机密微型 VM 的最小 init（PID 1），Rust 单 crate（src/ 24 模块 ~5400 行），负责 GPU 驱动加载、硬件配置、NVIDIA 守护装配，最终交接 kata-agent。

## 全链状态表

| 阶段 | 状态 | 产物/数据 |
|---|---|---|
| deepwiki | ✅ 完成 | `deepwiki/` 25 页（8 章 17 子页，INDEX.md + _coverage-check.md） |
| understand 图谱 | ✅ 完成 | 仓内 `.understand-anything/knowledge-graph.json`：150 节点 / 233 边 / 8 层 / 9 步 tour / 校验 0 issues；fingerprints 65 文件 @ b9700f3e |
| onboarding | ✅ 完成 | `onboarding/ONBOARDING.md` 7 节，60+ 行号锚（源码逐条核实） |
| explain | ✅ 完成 | `explain/` 3 篇（六节结构，每篇 1500-2500 非空白字符、锚 15+） |
| 勘误 | ✅ 完成 | 见下方 8 条源码级实证勘误 |

## explain 索引

- `explain/01-守护核心与PCI拓扑检测.md` —— main.rs / init.rs / mode.rs / nvrc.rs：启动时序、三元组拓扑决策表、NVRC 状态与守护健康检查
- `explain/02-dm-verity-fail-closed与供应链对账.md` —— guest_extension_image.rs / hash.rs / lockdown.rs / release.yaml：1:1 对账不变量、自证摘要的"非安全原语"自白、cosign+Rekor
- `explain/03-kmsg-modprobe工具链与守护同步.md` —— kmsg.rs / syslog.rs / modprobe.rs / kernel_params.rs / daemon.rs：命令行即配置、日志标记总线、copy-write-0o400 模式

## 源码级实证勘误（8 条）

1. **名称展开勘误**：nvrc 不是 "NVIDIA Remote Controller"——上游 README.md:1 明写 "NVRC - NVIDIA Runtime Container Init"（nvrc.rs:10 注释 "NVIDIA Runtime Container init" 同）。任何 "Remote Controller" 的展开均为讹传。
2. **语言预期推翻**：不是 Python 生态脚本，是纯 Rust 单 crate（Cargo.toml `[package] name = "NVRC"`，仅 8 个直接依赖；发布配置 `opt-level="z"`+`panic='abort'`，Cargo.toml:17-23）。图谱阶段 Rust `use` 边 scanner 有盲区，imports 依赖人工补扫核对。
3. **"fork 出 kata-agent 子进程"方向反了**：fork_agent（kata_agent.rs:83-97）是**父进程 exec 成 kata-agent**（继承 PID 1），子进程退化为 syslog 轮询器。图谱/摘要里"kata-agent 子进程"的说法与 kata_agent.rs:80-81 注释（"Parent execs kata-agent (becoming it), child stays as syslog poller"）相反。
4. **crate 名大写 `NVRC`**：Rust 惯例 crate 名应小写，本仓有意用大写，故 main.rs 全部 `use ::NVRC::...`（main.rs:4-11）。按习惯写 `use nvrc::` 直接编译失败。
5. **hash.rs 不是完整性机制**：模块头自认 "Not a security primitive"（hash.rs:9-13）——被入侵的二进制可谎报自身 SHA-256；真正强制完整性的是 dm-verity/fs-verity/IPE，可信摘要在 Rekor。引用时勿把启动日志哈希当验证手段。
6. **日志默认全关**：kernlog_setup 里 `set_max_level(LevelFilter::Off)`（kmsg.rs:25），生产可观测性全部依赖 `nvrc.log=` 命令行参数；debug 未开时 `kmsg()` 写 `/dev/null`（kmsg.rs:39-45）。"初始化内核日志"≠"打开日志"。
7. **modprobe.rs 与 smi.rs 是 src/ 下唯二无 SPDX 头的文件**（`grep -L SPDX src/*.rs` 实证）——其余 22 个模块全部带 Apache-2.0 SPDX 行，这两处是仓库卫生缺口而非规范。
8. **dm-verity 挂载与模块禁载的时序耦合**：guest_extension_image::mount_all 必须先于 lockdown::disable_modules_loading（main.rs:83-101），否则 dm-verity/erofs 模块载不进来、启动直接失败——这是重排 main() 顺序时最容易踩的暗雷。

## 快速上手

源码仓：`/usr-data/data2/repos/agent-repos/NVIDIA/nvrc`（commit b9700f3e）。阅读顺序：README → ARCHITECTURE.md（1074 行权威文档，:434 起 Composable Image Extensions）→ main.rs → mode.rs → guest_extension_image.rs。工程链 18 条 workflow（ci 在 g5g.metal 裸金属真机跑 E2E，ci.yaml:51）详见 ONBOARDING 第六节。

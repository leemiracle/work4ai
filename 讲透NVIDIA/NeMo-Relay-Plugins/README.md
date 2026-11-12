# 讲透 NeMo-Relay-Plugins

> NVIDIA NeMo Relay 插件联邦：三个教学示例插件（Python gRPC worker/Rust gRPC worker/Rust native 共享库）+ Switchyard 生产路由插件 + 一整套发布工具链（七平台矩阵/plan 体系/包源验证/归档完整性）+ 许可归属机器（1072 行双语言收集器）。**AGENTS.md 十条=AI 协作开发仓库宪法**。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| understand 图谱 | ✅ 2026-11-12 | 仓内 `.understand-anything/knowledge-graph.json`：**276n/441e/11 层/12 步 tour**，双 validate 0/0，fingerprints 102@115b2ae8（layers/tour 主会话自做，1308 死代理工作接管） |
| onboarding | ✅ 2026-11-12 | `onboarding/ONBOARDING.md`（8 节 6475 字不计空格，50 锚 0 坏） |
| explain 6 篇 | ✅ 2026-11-12 | `explain/01-06` 合计 **25201 字符**，105 锚（主会话抽验 3/3 命中） |

## 战况（14 批，单 worker，跨 1308 两段）

批 worker 自纠 8 条悬空边（6 个跨文件消费的导出函数补节点+batch-1 重组 3 part）；merge 悬空 0，罕见的 calls(99)/configures(30)/triggers(6) 边型齐全。layers/tour worker 死于 1308 核锚期未写盘——主会话 02:3x 接管完成（11 层 102 节点）。

## 甄别精选（源码级实证）

1. **插件双形态**：native=共享库进 Relay 进程（example-rust-native-plugin 四模块中间件）vs worker=独立进程 gRPC（Python/Rust 示例逐钩子对应）；manifest 双轨=relay-plugin.toml 运行时+release.toml 发布（473 行 JSON Schema 单一真相）
2. **三个示例的 smoke_test.py 字节级相同**（diff 实证）——共享 scripts/smoke.py 基座按 samefile 身份匹配
3. **"37 测试"三口径勘误**：test_worker.py 实为 36 个测试函数，两处 parametrize 展开后 40 个收集项，37 与任一口径都不符
4. native 示例 src/ 实为六文件（config.rs 307 行占近 1/3，任务书"四模块"旧口径）
5. attributions_lockfile_md.py 1072 行=Rust 走 cargo-about JSON+Python 走 uv.lock 双语言收集；ATTRIBUTIONS-Rust.md 72190 行 536 包节=生成物（仓内最大文件）
6. 跨文件消费实况：5 个消费模块消费 13+ 个导出符号（generate.py 改写模块级 ROOT 的耦合）
7. Switchyard=唯一生产插件：remote 源钉 commit sha、native 类型，与示例的发布形态差异
8. wheel_backend.py 纯 stdlib PEP 517 后端被复制进 wheel bundle（自包含设计）；test_workflows 强制全部外部 action 钉 40 位 sha

## 分层速览（11 层，102 文件节点）

治理与发布文档(11) → CI(1) → 发布工具链核心(13) → 脚本辅助(2) → 许可归属工具线(10) → 全仓归属清单(2) → Python worker 示例(12) → Rust worker 示例(14) → Rust native 示例(17) → Switchyard(5) → 工具链测试群(15)

*2026-11-12 · cuda-stack-第七轮会话（舰队夜战 · 1308 双杀恢复轮）*

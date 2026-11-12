# 讲透 NeMo-Fabric

> NVIDIA NeMo Fabric——**跨 agent 框架的统一运行时/工具适配层**：fabric-core Rust（+PyO3 绑定）+ fabric CLI + Python SDK 三发行包（runtime/collector/adapter-catalog）+ TypeScript 契约 + **19 个适配器矩阵**（openclaw/codex/cline/opencode/deepagents/nooa/strands…Python×10+TS×9）+ OpenShell 环境提供器（lib.rs 3397 行全仓最大单文件）+ Harbor 基准示例群 + **21+2 仓内 agent skills（战役 agent-first 迄今最完整发布生命周期套件）**。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| understand 图谱 | ✅ 2026-11-12 | 仓内 `.understand-anything/knowledge-graph.json`：**1367n/1825e/15 层/16 步 tour**，双 validate 0/0，fingerprints 1020@86f86882 |
| onboarding | ✅ 2026-11-12 | `onboarding/ONBOARDING.md`（8 节 9279 字不计空格，31 锚） |
| explain 12 篇 | ✅ 2026-11-12 | `explain/01-12` 合计 **60607 字符**，340 锚（六节全检 12/12；主会话抽验 4/4——lib.rs:4 doc 注释+3397 行实证、basename 锚 adapter.py 归属三适配器均界内） |

## 战况（105 批，双 worker 分段，跨 1308 两波）

scanner 对 Python src-layout+namespace 包几乎全盲——**imports 297+281 条全为 worker AST/use 重扫**；主会话三重手术：b88 tags 类型修正、b89 cline 三文件节点补建、b98 README 节点补建、14 条前缀错位悬空边（service:→file:/document:→config:/裸路径→加前缀）改写回补 13。写作期 1308 双杀于终压轮——12 篇+onboard 全部落盘零损失（防丢稿条款第 N 次救场）。

## 甄别精选（源码级实证）

1. **agent-first 第 12 例（最完整）**：.agents/skills 21 技能+顶层 skills/ 2 导出——覆盖三级打 tag（beta/RC/stable）、code freeze、release notes、版本三语同步、CI/打包维护、贡献 API/adapter/docs、PR 准备、验证矩阵选择+scoped karpathy-guidelines
2. **JSON Schema 契约权威源**：adapter-contract 11+sdk 16 张 schema，27 条 defines_schema 边锚定 Rust/TS 实现——"schema 即真理源"落地
3. **OpenShell 环境提供器=单文件巨石**：lib.rs 3397 行（environment-providers/openshell/），host Fabric core 的进程级环境提供
4. **适配器双语矩阵三风格**：openclaw adapter.py 1742 行（运行时校验链 995+授权 79+usage 归一 1052）/codex 1724/deepagents 1346——同契约三种集成深度
5. **runtime_server 命令桥**：单 serve 前景进程托管任意数独立寻址 SDK 运行时，短命命令走私有 Unix socket 复用公共 SDK；镜像/凭据/挂载/网络/删除全归调用方
6. **跨批全集对账新坑**：前段 worker 审计后段产物抓出 4 处"批内自检过、全集对账漏"（tags 非列表+三文件零节点）——每文件≥1 节点终验必须全集口径
7. test_deepagents.py 2686 行=全仓最大测试（五路测试矩阵之一）；harness 16 篇接入文档+27 条 schema→实现边
8. TS 适配器 cline-sdk.ts 612 行 fs/promises 临时目录管理；4 张 Excalidraw 架构图+docs/index.yml 文档站

## 分层速览（15 层，1027 文件节点）

治理配置(57) → 仓内 skills(40) → JSON Schema 契约(28) → fabric-core(24) → OpenShell(5) → fabric CLI(23) → Python SDK(45) → 契约双语言实现(39) → Python 适配器(84) → TS 适配器(123) → 接入文档(29) → Harbor 基准(123) → 文档站(18) → 测试矩阵(180) → API 参考(209)

*2026-11-12 · cuda-stack-第七轮会话（舰队夜战 · 双仓 II 上半场）*

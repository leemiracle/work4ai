# 12 · 文档站与架构图：docs/index.yml 导航树、4 张 Excalidraw 与 16 篇 harness 接入文档

## 角色定位

文档体系是 Fabric 对外 API 的另一半。`docs/` 是 Fern 文档站源（250 个 md/mdx 文件），由 `fern/docs.yml` 配置成站：instances 指 `nvidia-nemo-fabric.docs.buildwithfern.com/nemo/fabric` 与 custom domain `docs.nvidia.com/nemo/fabric`，`global-theme: nvidia`，products 以 `../docs/index.yml` 为导航根（fern/docs.yml:6-19）。`assets/` 的 4 张 Excalidraw 源图 + PNG 导出（ecosystem/fabric-hero/openshell_architecture/openshell_invocation）承担全部架构叙事。CLAUDE.md 把文档同步定为工程纪律："公共行为、nemo-fabric 包、示例或支持的 bindings 变更时，必须更新 README.md、fern 文档（导航 docs/index.yml、站点配置 fern/docs.yml）与适配器 README 群，并用 `just docs` 重新生成"。

## 内部结构

**`docs/index.yml` 是五层导航树**（约 140 行）：About（overview/ecosystem/release-notes，index.yml:5-11）→ Getting Started（install/quickstart，:13-17）→ Experimentation（CLI，:19）→ SDK（python/health-checks/system-stats，:23-29）→ **Adapter Contract**（README + custom-agents + 六篇教程 adapter-descriptor/normalized-configuration/execution/results/registration-and-discovery/conformance，:31-53）→ **Integrations**（consumer 两页 :57-61 + harness 17 页 :63-97）→ Reference（API：Python Library Reference 11 页 :103 起 + Rust Library Reference 整目录自动发现——注释写明"cargo doc -p nemo-fabric-core 经 scripts/docs/generate_rust_library_reference.py 生成"）→ Resources/legal。这棵树同时定义阅读路径与写作义务：每加一个适配器必须在 Integrations/Harness 下加一页。

**16 篇 harness 接入文档**（docs/integrations/harness/）是适配器的用户手册面：overview.mdx（36 行）一张表列全 16 harness——首行 Claude Code（overview.mdx:18）到末行 Remote Agent（overview.mdx:33），含 Codex/Cline/Factory Droid/Hermes/LangChain Deep Agents/Kilo/Kiro/AWS Strands/mini-SWE-agent/OpenClaw/OpenHands/OpenCode/Pi/Qwen Code，与 adapters/ 目录一一对应；表末链接回 GitHub adapters 目录做兼容性对照（overview.mdx:36）。每页模板高度一致，以最长的 deepagents.mdx（228 行）为例：frontmatter（deepagents.mdx:1-4）→ 定位段（"runs LangChain Deep Agents in the persistent NeMo Fabric Python adapter host，映射归一化配置到 model/tools/skills/MCP/workspace/telemetry"，deepagents.mdx:8-11）→ `## Install the Adapter`（deepagents.mdx:13）给两种装法：一体 `pip install "nemo-fabric[deepagents]"`（deepagents.mdx:19）vs 只装适配器 `nemo-fabric-adapters-deepagents[harness]`（deepagents.mdx:26），另有 relay/full extras（deepagents.mdx:37）→ `## Configure the Adapter`（deepagents.mdx:63）→ `### Enable Local Shell Execution for a Supervised Demo`（deepagents.mdx:146）→ `## Understand the Runtime Lifecycle`（deepagents.mdx:211）。其余各页 38-228 行（strands.mdx 38 行最薄，openclaw.mdx 175、opencode.mdx 198、claude.mdx 184、remote-agent.mdx 160），全 MDX 可嵌 Fern 组件。

**4 张 Excalidraw 是自绘架构资产**（JSON 源入库 + 同名 PNG）：
- `ecosystem.excalidraw`（40 元素/22 文本）：Fabric 在 NVIDIA agent 版图的位置——上游消费者 NeMo Helix（"Build, deploy, evaluate"）/NemoClaw/NeMo Gym/NeMo Polar（"Agentic RL rollouts"），中轴自述"Typed configuration · lifecycle · normalized evidence / Plan · diagnose · run · observe"，下游 "Adapter targets / Agent harnesses"。文档页 docs/about-nemo-fabric/ecosystem.mdx 嵌入该图（ecosystem.mdx:10）并逐个介绍 Helix（ecosystem.mdx:25 "platform-managed agent path 把持久 agent 定义翻译成 Fabric configuration"）与 Gym（ecosystem.mdx:41 "同一 environments 与 verifiers 比较 harnesses 或收集 rollouts 而不改任务契约"）。
- `fabric-hero.excalidraw`（193 元素/108 文本，最重）：主页横幅，三段泳道 CONSUMERS（Applications/Evaluation systems/RL rollout systems）→ EXECUTION LAYER（NeMo Fabric: Configure·Run·Observe，下分 CONFIGURE/FabricConfig、RUN/Agent lifecycle 步骤框）→ ADAPTER TARGETS。
- `openshell_architecture.excalidraw`（47 元素/25 文本）：沙盒拓扑——Consumer host 的 Application process（NeMo Fabric SDK Python+Rust core + OpenShell Rust SDK）→ OpenShell gateway（policy boundary）→ sandbox 内 fabric-runtime-ctl（short-lived per command）/fabric-runtime-server（persistent process）/Fabric adapter（persistent process）/Agent harness；注释行"Env ops: shared worker / Runtime: one worker per ID"点出 worker 复用模型。
- `openshell_invocation.excalidraw`（55 元素/26 文本）：一次 `invoke(): RunRequest → RunResult` 的时序穿越——Consumer→Fabric SDK→OpenShell Provider/Gateway→runtime-ctl→runtime-server→adapter & agent。

## 外部连接

文档站三处锁死：`docs/index.yml` 导航 ↔ `fern/docs.yml` 站点配置 ↔ 仓内 README 群（adapters/README.md 与各子 README、sdk/python/.../integrations/*/README.md、examples/README.md）。CLAUDE.md 列的同步义务还有：API 变化时更新 `docs/sdk/python.mdx` 与 `adapter-contract/{python,typescript}` 绑定、`schemas/SCHEMA.md`、`docs/reference/api/` 生成参考、以及 `skills/` 集成技能（"restate public contracts and must be kept in parity"）。reference/api 的 Python 部分由 `scripts/generate_api_docs.sh`（CLAUDE.md 点名的稳定公共包装）生成，手写与生成内容在 index.yml 以 `folder:` 自动发现节点区分。

## 数据流

一次文档变更：改代码/适配器 → 手改对应 harness mdx 与 README → `just docs` 重新生成 API 参考并校验链接 → 新页面在 index.yml 手动登记 → Fern 构建站点。Excalidraw 改动是手工的：编辑 assets/*.excalidraw（JSON）→ 导出同名 PNG 入库 → mdx 引用 PNG（如 ecosystem.mdx:10 的 `../../assets/ecosystem.png`）。适配器作者的接入文档最小集来自模板：install 双 extras 写法、能力边界、示例命令——deepagents.mdx 的 228 行是填到最满的样例。

## 设计决策

1. **导航树即产品主张**：index.yml 把 "Adapter Contract + 六篇教程"（:31-53）放在 Integrations 之前——先教契约再教用法，第三方作者被引着走 adapter-descriptor→normalized-configuration→execution→results→registration→conformance 完整路径。
2. **图用 Excalidraw 源入库**：手绘风 JSON 源让任何人可续改，PNG 只是导出物；四图各管一层（生态位/主架构/沙盒拓扑/调用时序）不重叠。
3. **docs 与 skills 双轨同源**：skills/nemo-fabric-integrate 与 nemo-fabric-build-adapter 复述公共契约且必须保持一致（CLAUDE.md）——文档站面向人类、skills 面向 coding agent，同一合同两种发行。
4. **16 页 harness 文档与 16 个适配器目录强制对称**：overview 表一行对一页对一仓，缺页即欠债，由 CLAUDE.md 更新清单兜底。
5. **生成内容与手写分层**：API reference 整目录脚本生成并经 folder: 自动挂载，防手写参考漂移；手写区只放叙事与教程。

## 新人提示

按 index.yml 顺序读即官方 onboarding：overview→quickstart→sdk/python→adapter-contract 六教程→挑一个 harness 页。改文档先读根 CLAUDE.md 的 "Documentation And Contribution Workflow" 节——文件联动、分支前缀（docs/）、Conventional Commit 标题、`git commit -s`。画新架构图克隆 assets/ 最接近的一张改（fabric-hero 最全、openshell_invocation 最简），PNG 同名覆盖。给新适配器写 harness 页直接抄 deepagents.mdx 骨架，写完必须在 overview.mdx 表格与 index.yml :63-97 段各加一行，否则导航出死链。校验一条命令 `just docs`，PR 前必跑。

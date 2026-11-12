# 09 CLI 与双 skills：`retriever` 命令行 + agent-first 发布形态

## 角色定位

NeMo-Retriever 把自己发布成"人用的 CLI + agent 用的 skill"双形态。`nemo_retriever/src/nemo_retriever/cli/` 是产品级 `retriever` 命令（typer 框架）；`skills/` 目录是两个 Agent Skill 包（`nemo-retriever` CLI 版与 `nemo-retriever-mcp` MCP 版），各带评测集、基准报告与 sigstore 签名束——仓库不再只发库和文档，而是把"教 agent 正确使用本产品"当成一等交付物，这是本仓 agent-first 形态的核心证据（仓根 `AGENTS.md` 同样为 Cursor/Claude Code 等 AI 编码 agent 写就）。

## 内部结构

**CLI**。`cli/main.py:18` 建 typer app，挂三个可见子应用 service/ingest/query（`main.py:28-30`）；另有五个惰性加载子应用（`main.py:35-41`）——harness 可见，eval/benchmark/recall/skill-eval 一律 `hidden=True`（`main.py:43-48` import 失败仅 debug 跳过，兼容裁剪安装）。`--version` 走 eager callback（`main.py:63-71`）。query 侧 `cli/query/app.py:114-119` 严格校验 `--format` 只认 `hits|evidence`，`--max-text-chars` 仅对 hits 合法；evidence 输出调 `build_evidence_result`（`app.py:141-142`）；本地查询命令 `_local_command` 默认 `--lancedb-uri lancedb`（`app.py:179`、`app.py:185`）。evidence 的真实实现在 `query/evidence.py:95`：把原始命中投影成 `{evidence, coverage}` 契约，薄证据（只有视觉命中无文本）显式降级告警（`evidence.py:118-130`）；`cli/evidence.py:1-15` 是向后兼容 re-export 壳——模块头注释明说搬家是为了让 service `/v1/query` 复用而不依赖 cli。ingest 的公共形态是子命令而非 flag：`ingest local|batch|service`（`docs/cli/README.md` 的对照表），设计动机写在文档里——"把非法 flag 组合挡在 parser 外"。

**双 skill**。`skills/nemo-retriever/SKILL.md`（frontmatter name/description/license）面向 CLI：教 agent 用 uv venv（`SKILL.md:17`）装 `nemo-retriever==26.8.1`（`SKILL.md:25`）四种变体（基础/`[local]`/`[service,local]`/`[local,multimedia]`），明确"不要 clone 仓或从 Git URL 安装"（`SKILL.md:39`）；本地工作流两条命令 `retriever ingest --lancedb-uri --table-name` 与 `retriever query --top-k 5 --format evidence`；service 工作流用 `RETRIEVER_SERVICE_URL`+`NEMO_RETRIEVER_API_TOKEN`，并警告"service 子命令别带 LanceDB 本地 flag"。规则区硬约束：已有索引/服务不重建、只从检索证据作答、引用保留 source/page 元数据。`skills/nemo-retriever-mcp/SKILL.md` 面向 MCP server：开头即纠偏"server 暴露的是 tools 不是 resources，别调 list_mcp_resources"（`skills/nemo-retriever-mcp/SKILL.md:12`）；默认 `top_k=5`+`format="hits"` 按需加量；最尖锐的一条安全边界——"agent 可见的路径不等于 Retriever server 可读"（`skills/nemo-retriever-mcp/SKILL.md:22-23`）。

**评测与签名**。每个 skill 配 `evals/evals.json`（4 任务：3 正例 1 负例）与 `BENCHMARK.md`：CLI 版 2026-09-11 评测，evaluator 1.5.6，Claude Code（bedrock-claude-opus-4-8）与 Codex（gpt-5.5）双 agent、每任务 3 次尝试、独立 k8s sandbox pod（`skills/nemo-retriever/BENCHMARK.md` 元数据节）；结论 PASS（`BENCHMARK.md:3`）——Correctness 从 27.5%→90.0%（Claude，+62.5 分）与 26.0%→70.0%（Codex，+44 分）（`BENCHMARK.md:40`）。MCP 版更戏剧化：Codex Security 30.0%→90.0%（+60 分）——没有 skill 时 Codex 会做不安全操作。`skill-card.md` 是发布卡片：owner NVIDIA、Apache 2.0、输出类型 Shell commands、五维指标（Security/Correctness/Discoverability/Effectiveness/Efficiency）定义（`skills/nemo-retriever/skill-card.md` 指标节）。`skill.oms.sig` 是 sigstore 签名束：`application/vnd.dev.sigstore.bundle.v0.3+json`，DSSE envelope 载荷类型 `application/vnd.in-toto+json`，predicateType 为 `https://model_signing/signature/v1.0`（复用 model-transparency 模型签名规范签 skill），subject 是 skill 名的 sha256 摘要，证书链 3 张——叶子 `CN=NVIDIA Agent Skills Signing 001`、签发者 `CN=NVIDIA Agent Capabilities ICA 01`（NVIDIA 私有 CA），有效期 2026-04-01→2028-04-22，`tlogEntries` 为空（未上公共透明日志）。

## 外部连接

CLI 闭环比表面大：隐藏子命令 `skill-eval`（`main.py:40`）挂的是仓内评测 harness `tools/skill_eval/`（cli/dataset/runner/score/report/trace_summarizer 全套），pyproject 还为它打包 prompts 模板与 configs（`nemo_retriever/pyproject.toml:270`）——"发布 skill→评测 skill"的工具链就在同一 CLI 里。`.claude/skills/` 下同名目录让两个 skill 直接作为 Claude Code 项目 skill 生效。skill 文档引用外部 docs.nvidia.com 检索库文档与 GitHub 26.08 分支（`skills/nemo-retriever/skill-card.md` Reference 节）。CLI 的 service 子命令连到第 12 篇的 service 部署；query/ingest 工作流复用篇 7 的模型接入层与 LanceDB 索引。

## 数据流

agent 视角：宿主 agent 载入 SKILL.md → 判断适用（描述区写明触发条件与排除项"不用于编辑文档或 web search"）→ 按指引建 venv 装对应变体 → `retriever ingest` 建/复用索引 → `retriever query --format evidence` 拿 `{evidence, coverage}` 结构 → 基于证据作答并带引用。MCP 形态：agent 调 `query` tool（top_k=5, format=hits）→ 命中不足再加量 → 需要 `ingest_documents` 时先确认 server 侧可读路径。发布者视角：SKILL.md+evals.json → skill-eval harness 在 k8s 沙箱跑 4 任务×3 次×双 agent → 产出 BENCHMARK.md 五维分 → NVIDIA 内部签名流水线出 skill.oms.sig → 发布。

## 设计决策

1. **skill 是产品而非文档副产品**：四件套（SKILL/BENCHMARK/skill-card/oms.sig）+ 评测 harness 进仓，发布流程可复现、可审计。
2. **负例任务进评测**：4 任务含 1 负例——测 agent 会不会在该拒绝时拒绝（如对不可见路径硬 ingest）。
3. **签名复用模型签名规范**：skill 按 model-transparency `model_signing/signature/v1.0` 谓词签——AI 供应链里"skill 即模型级资产"的定位。
4. **CLI 子命令化而非 flag 化**：local/batch/service 三模式互斥 flag 组合从 parser 层消失（docs 明言）。
5. **SKILL.md 里写反模式**：不 clone 仓、不重建索引、service 命令不带本地 flag、MCP 无 resources——把 agent 最常踩的坑前置成禁令。

## 新人提示

- `cli/evidence.py` 只是壳，改 evidence 逻辑去 `query/evidence.py`（service 端点同源复用）。
- 隐藏子命令（`retriever eval/benchmark/recall/skill-eval --help`）在 help 里看不见但可用，排查"命令去哪了"先想 hidden。
- 验签工具不在本仓：skill.oms.sig 的校验方在 NVIDIA 发布管道/宿主侧，本地只能自验证书链（openssl 即可）。
- skill 版本号（26.8.1）与仓分支（26.08）对齐，升版本要同步改 SKILL.md 安装命令与 BENCHMARK 元数据。
- 写新 skill 时照抄双 skill 的负例设计与"路径可见性"警告——这是评测里 Security 分差最大的两个来源。

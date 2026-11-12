# EXPLAIN-10 · Agent-first 插件体系：plugins/modelopt + skills + agents + AGENTS.md

## 一、角色定位

Model-Optimizer 把"给 AI agent 用的能力"做成仓内一等公民：**可安装插件 + 技能卡 + 子代理 + 协作铁律**四位一体。CLAUDE.md（符号链接到 AGENTS.md，.agents/TOOLING.md:6-7）第一条指路：技能树权威位置在 `plugins/modelopt/skills/`，`.agents/skills` 与 `.claude/skills` 只是符号链接暴露（AGENTS.md:10-13）。骨架三层：①插件包三入口——`.claude-plugin/plugin.json`、`.codex-plugin/plugin.json`、`.mcp.json`（把 tools/mcp 以 uvx 挂为插件 MCP server）；②技能卡 **16 张**（实测 ls；**勘误：任务书称 17 张，实际 16 个技能目录**）；③子代理 `plugins/modelopt/agents/` 6 个 md + `.codex/agents/` 6 个 TOML 镜色。与 EXPLAIN-09 的 MCP 层互补：技能卡是工作流知识，MCP 是环境操作。

## 二、内部结构（16 张技能卡逐张点名）

**主链五张**：

- **ptq**（214 行，最重执行卡）：五段工作流 Step1 环境→Step2 支持→Step3 选格式→Step4 跑→Step5 验证（ptq/SKILL.md:19-160）。细节：Step 2.5 处理 trust_remote_code 依赖（:37-53）；Step 3 按 GPU 代际选格式（Blackwell→nvfp4、Hopper→fp8/int4_awq，:66-69）且"跑前数 recipe 命中数，为 0 即停"（:73）；VLM 警告 `*mlp*` 误伤 vision tower（:75）；Step 4 三分支 4A/4B/4C（:108-115）；Step 5 validation 是部署前强制闸（:169-180）。
- **quant-recipe-search**（167 行）：多候选搜索策略卡——Skill Boundaries 执行全委托（quant-recipe-search/SKILL.md:27-37）；三输入缺即问，"Do not silently default to FP8"（:53-54）；搜索空间七轴（:62-80）；"一次只动一个主轴"（:115-116）。
- **deployment**（276 行）：vLLM/SGLang/TRT-LLM+AutoDeploy；`deploy.sh` 管生命周期（deployment/SKILL.md:15-35）；推荐表（:71-77，AutoQuant checkpoint 只有 TRT-LLM AutoDeploy 一条路）；显存口诀 BF16×2B/FP8×1B/FP4×0.5B（:94-99）。
- **evaluation**（140 行主卡+大子树）：NEL 十步清单（evaluation/SKILL.md:19-31）+两分支——agentic 基准走 nel-next（:35-48）、MRCR 走 gym 且"never mix with aa/ tasks"（:52-59）。
- **compare-results**（111 行）：基线 vs 候选裁判——8 步流程（compare-results/SKILL.md:13-46）强制 External Baseline Sanity Check（:34-40）与 Comparability Checklist（:48-60）；没阈值就报 inconclusive（:44-46）。

**编排运维五张**：

- **day0-release**（314 行，总指挥）：发布链 PTQ→canary→baseline-eval→quantized-eval→compare→verbosity→closeout 每段一闸（day0-release/SKILL.md:38-43、:59-69）；四 gate 脚本；决策词汇 ACCEPT/REGRESSION/ANOMALOUS/INFEASIBLE（:3）；:105-109 记录"不会说谎的 canary"教训（50 分钟轮询撞 51 分钟 MoE 加载）。
- **monitor**（171 行）：作业注册表按 session id 分文件防多 agent 互踩（monitor/SKILL.md:17-35）。
- **launching-evals**（71 行）与 **accessing-mlflow**（104 行）：**vendored verbatim 卡**——原样同步自 NeMo Evaluator（launching-evals/SKILL.md:5-7；accessing-mlflow/SKILL.md:5-9），手改禁止（.agents/README.md:49-50）。Key Facts 全是坑：NEL 成对 RUNNING+PENDING restart 别误杀（launching-evals:66）、`dp_size` 是每节点（:68）、`export --dest local` 假复制（:71）。
- **debug**（33 行，最小）：走 tools/debugger 文件中继在远程 Docker 执行命令（debug/SKILL.md:3、:14-33）。

**专项四张+底座**：

- **speculative-decoding**（92 行）：双轴——`references/stages/` 流程 × `references/algorithms/` 四算法（EAGLE3/DFlash/DSpark/Domino）数据表（speculative-decoding/SKILL.md:27-37）；DSpark/Domino 是 DFlash 变体（:63-66）。
- **run-agentx**（90 行）：AgentX agentic serving 基准；pinned revision 装机（run-agentx/SKILL.md:27）；"submission_valid 缺失即非基准结果"（:85-90）。
- **benchmark-model-kernels**（145 行）：meta tensor 上 per-rank GEMM/MoE 微基准，永不加载权重（benchmark-model-kernels/SKILL.md:14-16）；"一次一问"纪律（:18-23）。
- **release-cherry-pick**（176 行）：按 `cherry-pick-<version>` 标签收割，先审计 NVBugs 防漏（release-cherry-pick/SKILL.md:22-24）。
- **qad**（106 行）：量化感知蒸馏，首句成本警告（qad/SKILL.md:12-14）。
- **common**（10 行占位）：Codex 校验要求技能必须有 SKILL.md 故做引用占位（common/SKILL.md:8-10）。

## 三、外部连接（符号链接暴露约定）

`.agents/README.md` 是约定权威（:28-41）：**永不复制只做相对符号链接**——Claude Code 只自动发现 `.claude/skills/`，故 16 条链接指 `../../.agents/skills/<name>`（`.agents/skills` 又链到 `../plugins/modelopt/skills`）；`.claude/agents/` 6 条链接指 `../../plugins/modelopt/agents/*.md`；Codex 只认 `.codex/agents/` 的 TOML（:40-41"Codex plugins cannot currently install custom roles"）。编辑规则：技能永远改 `plugins/modelopt/skills/`（:45），新技能落 `<name>/SKILL.md`（:51），共享文件进 common/（:52）。集群配置按 `~/.config/modelopt/clusters.yaml`→`.agents/clusters.yaml`→`.claude/clusters.yaml` 三级查找（:56-60）。上游生态：vendored 卡拴 NeMo Evaluator；`.mcp.json` 拴 tools/mcp。

## 四、数据流

day-0 发布串全体系："release model X at day-0"→ 触发 **day0-release**（description 精确匹配，SKILL.md:3）→ 调 **ptq** 产 checkpoint+validation-summary JSON → `gate_ptq.py` 吐 `{pass, failure_class}`（:89-91）→ canary（复用 ptq 卡规范，:93-100）→ **evaluation** 起 NEL 作业（自部署端点）→ **monitor** 注册轮询 → **compare-results** 过外部基线闸 → `gate_compare.py`+`gate_verbosity.py` 双闸 → closeout 决策。每张卡 description 都写"何时不用我、该用谁"（ptq/SKILL.md:8-9、quant-recipe-search/SKILL.md:9-12），路由声明式完成。子代理同理：`modelopt-model-quantizer` 只做父级选定的一个候选，禁止搜配方/部署/评测（agents/modelopt-model-quantizer.md:9），交接八标题固定（:18）。

## 五、设计决策

1. **单一事实源+链接扇出**：技能只存 plugins/modelopt/skills/ 一处，三 agent 目录全链接——零同步成本，precommit 脚本守护一致性。
2. **description 即路由器**：16/16 张卡全有"Use when…/Do NOT use for…"触发词与互指，技能选择从模型猜测变声明式匹配。
3. **conductor 与 worker 分层**：day0-release 只编排不重实现（SKILL.md:10-12）；quant-recipe-search 只管策略执行全委托（:19-21）；闸门是脚本不是 prose（gate_*.py 返回结构化 failure_class）。
4. **负知识入卡**：canary 误判实录（day0-release:105-109）、假复制（launching-evals:71）、vision tower 误伤（ptq:75）——踩过的坑变卡片正文，是技能卡区别于普通文档的核心价值。
5. **AGENTS.md 协作铁律**：PR 预算 ~500 行新增源码（:51-57，测试/文档/删除不计）；超预算先提拆分再动手（:58-60）；结构先拆、`[x/N]` 标题（:61-70）；签名提交 `git commit -s -S`（:31-33）；**push 需当轮显式批准**（:34-38）；技能卡精简令"每行都花 token"（:42-47）；"bot 评论是待验证主张"（:102-105）。
6. **vendored 卡带溯源**：注明上游 commit 与 resync 脚本，可同步性写进卡头。

## 六、新人提示

- 改技能只改 `plugins/modelopt/skills/<name>/SKILL.md`，提交前压缩 pass（AGENTS.md:45-47）。
- 找"该用哪张卡"读 frontmatter description；完整发布决策才用 day0-release，单段路由到域卡（day0-release/SKILL.md:19-22）。
- 加新技能：`plugins/modelopt/skills/<name>/SKILL.md` 落卡（.agents/README.md:51）→ `.claude/skills/` 加链接 → 大卡配 references/ 与 tests/。
- 卡是知识、子代理是隔离上下文的执行者；父持全局，子回固定交接（modelopt-model-quantizer.md:18）。
- 坑：common 卡是空壳占位（common/SKILL.md:8）。
- 坑：技能数对外用 16（以 ls 为准）；改 agents/*.md 后同步 `.codex/agents/` TOML（README:40-41）。

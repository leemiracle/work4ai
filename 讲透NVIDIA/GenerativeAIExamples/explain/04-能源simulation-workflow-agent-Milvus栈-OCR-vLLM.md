# 04 · industries/energy/simulation-workflow-agent：油藏模拟多 Agent 编排 + Milvus 栈 + GLM-OCR

> 覆盖 `industries/energy/simulation-workflow-agent/`（181 文件，全仓最大单示例）：orchestration_agent 路由、sim_agent 交互问答（LangGraph 七节点）、workflow_agent 优化循环（LangGraph 六节点五 Agent）、llm_provider 共享层、docker-compose-full.yml 全栈。

## 一、角色定位

回答的问题：**"LLM Agent 要驱动一个跑几十分钟的科学计算器（油藏数值模拟器）时，架构怎么分层？"** 四层分治：**orchestration_agent**（`orchestration_agent/agent.py`）按查询是否携带 workflow 配置路由——agent.py:17 模块 docstring 直言"routes user queries to sim_agent (interactive) or workflow_agent (deterministic)"；**sim_agent** 是工程师对话助手（改输入/跑模拟/读结果/画图，每步可审批），模拟器为开源 OPM Flow（`sim_agent/EXAMPLES.md:3`），标准算例 SPE10（EXAMPLES.md:97）；**workflow_agent** 是油藏优化自主循环（多 Agent 辩论策略 + 子进程跑遗传算法 + 预算迭代）；**llm_provider**（`llm_provider/__init__.py`）共享 ChatOpenAI 工厂（图谱 fanIn 9）。它是"industries = 主线骨架 × 领域深度"的最佳标本。

## 二、内部结构

**workflow_agent 六节点图**（`workflow_graph.py:419-449`）：`initial_analysis → evolve_strategy → run_workflow → update_best`，条件路由 `_route_after_run`（workflow_graph.py:405-411：should_continue 真→回 evolve；phase=final→final_report；否则→prepare_final），`prepare_final → run_workflow（复用）→ final_report → END`。

- **State**：`WorkflowState(TypedDict, total=False)`（workflow_graph.py:56-93）——输入/Phase 1 四产物/迭代游标/累积（all_solutions、best_solution、total_simulations）/控制（phase: initial|iterate|final|done）/输出。
- **Phase 1 多 Agent 辩论**（workflow_graph.py:109-142）：`ReservoirAnalystAgent.extract_characteristics` 静态提特征（workflow_graph.py:121）→ analyst → KnowledgeRetriever（挂 RAG）→ StrategyProposer → Critic，四产物入 state；团队 `_get_team` 惰性组装五 Agent（workflow_graph.py:380-392）。
- **evolve_strategy**（workflow_graph.py:145-183）：以 best 策略为基按 execution_mode 选 `evolve`/`evolve_diverse`（并行变体，workflow_graph.py:169）；建 `iter_XX_var_XX` 目录（workflow_graph.py:174）。
- **run_workflow**（workflow_graph.py:186-247）：**工作流无关**的子进程执行——`workflow.run_command` 是唯一契约（`_get_executor` 强制 workflow_graph.py:101-106；`conf/config.yaml:74` 为 `python ./optimization/src/run_optimization.py {config_path}`）；超时双档 quick 3600s/full 14400s（workflow_graph.py:203-207）；quick 代数按 ratio 0.25 折减（workflow_graph.py:209-217）；成功后补收敛/多样性指标（workflow_graph.py:264-291）。
- **update_best**（workflow_graph.py:310-357）：目标更优换 best（workflow_graph.py:324-331）；预算双闸 `max_iterations`+`max_total_simulations`（workflow_graph.py:337-350）。**final_report**（workflow_graph.py:360-377）落 `final_report.json`。

**BaseAgent 积木**（`agents/base_agent.py`）：`AgentResponse` dataclass（base_agent.py:33-43）；`BaseAgent`（base_agent.py:46）双模式 LLM——配置含 `endpoints` 则 `MultiLLMManager` 按任务路由（base_agent.py:58-59），否则单端点、api_key 走 `{PROVIDER}_API_KEY` 约定（base_agent.py:66-68）。三个默认：任务类型从类名推断（base_agent.py:70-82，多 LLM 路由零配置）；prompt 用 `yaml.safe_dump` 序列化任务字典（base_agent.py:109-110）；响应解析 yamlish→jsonish→raw 三级兜底（base_agent.py:112-117）——对 LLM 输出的极端容忍。

**sim_agent 七节点图**（`graph/build.py:38-60`）：`query_routing → check_args → approval_needed → execute_tools → advance_step` + `skill_failed_handling` + `final_response`，入口条件路由（build.py:49）。技能目录化（`skills/`：input_file/simulation/results/plot/rag_skill，各带 SKILL.md+test.py），`skill_loader.py` 动态装配。input_file_skill 的 utils.py（图谱 fanIn 5）：keyword 块定位、块内第 N 数值替换、think 块剥离——**改 DAT 输入文件是精确文本手术，不让 LLM 重写全文件**。

**sim_agent 配置**（`config.py`）：`AgentConfig`（config.py:33）加载 `CONFIG_PATH` 或默认 config.yaml（config.py:44-45），同步模型名进 `SIM_LLM_MODEL` 且不覆盖已有值（config.py:55-62）；集合名白名单三选一（config.py:89-94）；reranker 默认云上 rerankqa（config.py:80-81）。

**orchestration_agent**（`agent.py`）：**配置探测路由**——`_looks_like_workflow_config` 查配置节（agent.py:49），配置路径正则归一（agent.py:143-145）；以 **Python API**（import 调函数）驱动下游（agent.py:187/234，`from workflow_agent.runner import AgenticWorkflow` agent.py:241），sim_agent 输出目录/上传文件回传下一轮（agent.py:167）。

**部署拓扑**（`docker-compose-full.yml`，112 行）：`agent` 服务 `command: ["python","-m","orchestration_agent","--interactive"]`（compose:27），`MILVUS_URI: http://standalone:19530`（compose:19）、`OPM_PROJECT_ROOT`（compose:20）、`OPM_FLOW_EXTRA_ARGS` 兼容开关（compose:21）、OMPI root 放行（compose:22-23）。`ocr-vllm`（compose:31）：镜像 `glm-ocr-vllm`（compose:32），命令 `zai-org/GLM-OCR --port 8080 --max-model-len 32768`（compose:36）——**手册摄取走 VLM OCR**；`Dockerfile.ocr` 基底 vllm nightly，官方 transformers 太旧不含 GLM-OCR 架构，**从 GitHub 主线装 transformers**（Dockerfile.ocr:9-10）——本仓罕见的非 NVIDIA 模型引用。Milvus 栈：etcd v3.5.5（compose:53）+ minio RELEASE.2023-03-20（compose:70）+ milvus v2.5.4 standalone（compose:88，seccomp:unconfined compose:91，healthz compose:98）——**与主线 local_deploy（v3.5.16/v2.4.15-gpu）不同源**。精简版 docker-compose.yml（26 行）只起 agent 依赖外部 milvus。

## 三、外部连接

OPM Flow：run_command 子进程契约的下游。Milvus：sim_agent rag_skill 检索手册/示例。LLM 三通道：llm_provider 的 OpenAI 兼容端点（可指 NIM）、云 reranker（config.py:80）、GLM-OCR vLLM（8080）。主线基因：配置+环境变量同步、skills 目录化与 examples 目录化同哲学；但**不复用 chain_server**——领域对话循环由 LangGraph 原生承担。**双副本警示**：`sim_agent/scripts/milvus/nvidia_embedding.py` 与 `skills/rag_skill/scripts/nvidia_embedding.py` **md5 完全相同**，改一必查二。

## 四、数据流

**交互线**：指令 → query_routing（闲聊/工具二分）→ check_args 补参 → approval_needed 人审 → execute_tools 调 skill（input_file_skill 对 DAT 做 keyword 定位+数值替换；simulation_skill 起 OPM Flow；results/plot/rag_skill 各司其职）→ advance_step → final_response。OCR 线独立：PDF → GLM-OCR（32k 上下文）→ 切块/嵌入 → Milvus simulator_manual 集合。

**优化线**：base_config → Phase 1 辩论初始策略 → 循环{evolve_strategy → 写 config.yaml → 子进程跑优化（quick 25% 代数快速筛）→ update_best（双预算闸）} → 预算尽 → prepare_final（best 策略 full 全量跑）→ final_report.json。每轮独立目录可追溯。

## 五、设计决策

1. **"LLM 辩论出策略、子进程执行"硬边界**（workflow_graph.py:101-106）：贵且不可回滚的模拟交给 run_command 子进程，LLM 只写 YAML——失败可捕获、超时可预算、换 run_command 即换优化器/历史拟合。这是对"Agent 直接跑科学计算"可靠性焦虑的结构性回答。
2. **双预算闸**（workflow_graph.py:337-350）：迭代数与总评估数同时封顶，防 LLM 策略循环烧干算力。
3. **quick/full 两档**：25% 代数筛 + 全量终跑（workflow_graph.py:209-217），遗传算法语境的 early stopping。
4. **类名即路由 + 三级响应解析**（base_agent.py:70-117）：少配置多容忍的 Agent 工程 pragmatism。
5. **编排用 Python API 而非 CLI 串联**（agent.py:187/234）：跨 agent 传状态零序列化损耗，代价是三包同容器。
6. **OCR 选 VLM 而非解析器**：油藏手册表格公式多，GLM-OCR 整页视觉转录（compose:36），代价是 GPU 常驻 + transformers 源码构建。

## 六、新人提示

- 阅读顺序：根 README → `workflow_agent/conf/config.yaml`（run_command/llm/agents/constraints 四节一览）→ workflow_graph.py（450 行三张图里最清晰）→ base_agent.py → build.py → EXAMPLES.md 跑通第一条 SPE10 指令。
- 全栈前提：LLM key、HF 缓存（GLM-OCR 权重数十 GB）、GPU≥2（ocr-vllm 必须）。
- 精简 compose 不带 milvus/ocr——rag_skill 会空转，先起 full 或外接 Milvus。
- `TOOL_DECISION_TREE.md`（sim_agent/src/simulator_agent/）是工具选择决策树，排查"选错工具"先读它。
- 甄别条款：行号锚在 commit `203b0de` 核实（etcd compose:53 / milvus v2.5.4 compose:88）；nvidia_embedding 双副本为 md5 实证；GLM-OCR 构建依赖 transformers 主线（Dockerfile.ocr:9-10 注释明示）。

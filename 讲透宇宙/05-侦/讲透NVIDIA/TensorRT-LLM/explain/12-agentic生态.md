# 12 · agentic 生态：scaffolding、agent-flow 与 NVIDIA 的 agent 协作开发实证

## 一、角色定位

本主题是 TensorRT-LLM 里"用 LLM 开发/使用 LLM 引擎"的三个层面：**scaffolding**（`tensorrt_llm/scaffolding/`，推理时计算框架——CoT/majority vote/best-of-N/MCTS 的模块化底座）、**agent-flow**（顶层 `agent-flow/` 仓中目录，驱动 Claude Code/Codex 等 coding agent 的四工作流编排库）、**.claude 生态**（11 个 agents + 28 个 skills，NVIDIA 工程师把 agent 协作开发写进仓里的第一手实证）。三者对应图谱 L08/L15 层，是理解"AI 时代infra 仓自噬"现象的最佳标本。

## 二、内部结构

**scaffolding 三概念**（README 钉版）：`Controller` 定义方法逻辑只产出 Task（controller.py:17 ABC，generate:25/process:32 双接口）；`Worker` 完成任务（worker.py:50 ABC）；`ScaffoldingLlm`（scaffolding_llm.py:26）粘合二者对外提供 API。**五 Worker 实现**：OpenaiWorker（worker.py:105，OpenAI 兼容端点）、TRTOpenaiWorker（:529，继承前者接 trtllm-serve）、TRTLLMWorker（:538，直连 PyExecutor 原生后端）、MCPWorker（:705，工具调用）、ApiaryMCPWorker（:819）。**Controller 谱系**：NativeGenerationController（controller.py:80）→NativeChatController（:110）→NativeRewardController（:122）→PRMController（:138，过程奖励模型），ChatWithMCPController（:246）挂工具；ParallelProcess（:36）+from_generators（:53）支持子控制器并发组装——majority vote 套任意采样子控制器的组合性由此而来。`contrib/` 九个方法包（Dynasor、TreeInference、Coder、DeepConf、AsyncGeneration、iter_research、open_deep_research、tree_of_thought_research、mcp）是方法库；task_collection.py（1259 行）负责任务收集与并发调度，三级并发（请求间/子控制器间/Task 间）是性能承诺的核心。

**agent-flow 仿 torch 造 agent**：`module.py` 仿 nn.Module 树形生命周期；`layers.py` 的 AgentLayer（layers.py:118）提供同步 `forward`（:137）与异步 `aforward`（:142）双态；`runtime.py` 的 PortalRunner（runtime.py:13）用线程+队列让同步代码安全驱动 async SDK（_invoke:60/call:66/acall:78）；`tools.py` 从注解反射推导 JSON Schema（get_type_hints include_extras，tools.py:96；递归 TypedDict 必须显式 Schema，:93），支持 shorthand/TypedDict/MCP 三形态（:139/:171）。backends 五件：base.py 的 ABC+PEP 604 联合类型事件、claude_code.py（SDK 消息归一化+subprocess 探 CLI 版本）、codex_config/events/transport（URL 解析防御、per-turn 用量计数、contextvars 工具分发）。**四工作流**全用 PEP 562 `__getattr__` 惰性加载（agent_team/__init__.py:47、perf_analyze:41、perf_optimize:68、modeling_bringup:31）：agent_team 是 1543 行 33 方法的大成（workflow.py:73 AgentTeamWorkflow、:346 _invoke_agent 统一调用，状态机+tempfile 原子写 checkpoint）；modeling_bringup 自动 onboard 新模型（_common.py 用 lru_cache 探测技能可用性、缺失优雅降级）；perf_analyze/perf_optimize 覆盖性能诊断与调优（sol_methodology 的 fail-open：探针失败退回完整方法学；perf_optimize/disagg.py 的 fill-or-error 权威源调和；gitops.py 的 worktree 隔离+绕过失败 pre-commit）。

**.claude 生态**：agents/ 11 文件四前缀族——exec×3（compile/local-slurm/remote-slurm，编译与作业环境专家）、kernel×4（cuda/cute/tileir/triton 四种 kernel 写作专家）、perf×3（profiling/test-sync/torch-cuda-graph）、trtllm×1（test-specialist）；skills/ 28 目录同四族（exec 6/kernel 3/perf 10/trtllm 9）。perf-optimization-casebook 的三份数据文件构成一个微型知识库协议：`tags.yaml` 受控词表（case frontmatter 只许写 canonical 词）、`aliases.yaml` 查询期同义词归一（同义词不得与 canonical 或彼此碰撞，否则归一歧义）、`patterns.yaml` 混合注册表（case 引用的 pattern id 必须存在、pattern 的 instances 必须回指真实案例，KernelWiki DEC-1 风格手工一致性）。

## 三、外部连接

scaffolding 向上接 examples/scaffolding/ 示例与 LLM API（ScaffoldingLlm 复用 llmapi 的 executor），向下 TRTLLMWorker 直连 _torch/pyexecutor；MCPWorker 走 mcp_client.py。agent-flow 的 backends 对外依赖 Claude Agent SDK 与 Codex SDK（外部进程），workflows 消费本仓的 benchmark 产物（perf_analyze 的曲线模式按 concurrency/num_prompts 索引配对）与 .claude skills（modeling_bringup 探测 trtllm-model-onboard-multimodal 等 skill）。.claude agents/skills 又被 agent-flow 的 agent_team 通过 CLI 调用——三层互相咬合：**仓里的工具链既是开发协作设施，又是 agent 工作流的执行素材**。

## 四、数据流

scaffolding 一轮：用户请求 → ScaffoldingLlm 起 ScaffoldingRequest（scaffolding_llm.py:19）→ Controller.process 产出 Task 流（生成/奖励/工具任务混排）→ task_collection 并发分发到 Worker（TRTLLMWorker 进原生引擎享受连续批处理）→ GenerationResult 汇回 Controller 决定下一轮（vote/剪枝/扩展）。agent-team 一轮：编排器读 YAML 的 decision 字段驱动状态机（progress.py，杜绝正则解析散文）→ _invoke_agent 按 role 起子 agent（coder/plan_drafter/plan_reviewer/qa/reviewer，prompts/ 下纯常量模块）→ 产物写 worktree → 状态 tempfile 原子落盘。casebook 一查：用户词→aliases 归一→tags 词表约束→按 pattern/case 索引取案例。

## 五、设计决策

① **scaffolding 把"方法"与"后端"正交解耦**：CoT 算法不该知道跑在 TRT-LLM 还是 OpenAI 上——五 Worker 就是五个世界，Controller 零感知。② **agent-flow 选 torch 心智模型**（Module/forward/参数树）而非 LangChain 图模型：目标用户是 kernel 工程师，nn.Module 是他们唯一熟的组织原语。③ **四工作流全部 PEP 562 惰性加载**：提示词常量与 CLI 依赖解耦，import 包零开销。④ **YAML decision 字段而非散文解析**：agent 输出的结构化锚点必须是一等公民，正则解析 LLM 散文是被明令禁止的反模式。⑤ **casebook 三文件协议**：受控词表+查询期归一+双向引用校验，是小型领域知识库防漂移的最小完备设计。⑥ NVIDIA 把 agents/skills 入仓：agent 协作开发被视为仓库基础设施而非个人配置——与 cuda-tile 仓 CLAUDE.md 同一现象（见全局记忆 NVIDIA-CUDA-STACK 考据）。

## 六、新人提示

scaffolding 从 README.md 与 controller.py:17-50 读起，五 Worker 只需精读你用的那个（TRTLLMWorker，worker.py:538，是本仓原生路径）。agent-flow 从 workflows/ 挑一个最像你需求的抄（perf_analyze 最小、agent_team 最全）；改 prompts 只动 prompts/ 常量模块，别在编排器里内联文案。用 .claude agents 前先看 exec-local-slurm 这类环境专家——它们封装了集群登录/编译的坑；写 case 必须先查 tags.yaml 是否有 canonical 词，造词先扩词表。三层关系一句话：scaffolding 服务引擎用户，agent-flow 服务仓贡献者，.claude 服务日常开发——别用错层。图谱入口：L08（scaffolding/agent-flow）与 L15（skills 生态）。

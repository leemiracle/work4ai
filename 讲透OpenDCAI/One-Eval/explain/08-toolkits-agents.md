# 08 · toolkits 工具层与 agents 编排层

## 角色定位

`one_eval/toolkits/`（6 文件）与 `one_eval/agents/`（8 个 Agent）是工作流的"手"与"脑"：agents 做 LLM 推理（理解需求、解析基准、推荐指标、生成报告），toolkits 做确定性外部动作（搜 HF、探结构、下载数据、跑评测）。中间隔两个框架构件：`toolkits/tool_manager.py` 的 ToolManager（注册分发中枢）与 `core/agent.py` CustomAgent + `serving/custom_llm_caller.py` CustomLLMCaller（框架封装与 LLM 调用器）。nodes 层（09 篇）把"Agent+工具"包成 LangGraph 节点薄壳。

## 内部结构

**toolkits 分工**：`tool_manager.py`（55 行注册表单例）、`hf_search_tool.py`（36 行，**全仓唯一 @tool**，L6-7：list_datasets 搜索 L14 + DatasetCard.load L19，失败也返回带 error 的占位项 L27-34——给 function_call 的容错约定）、`hf_dataset_structure_tool.py`（174 行，dataclass 探测器 RepoStructure L10-29）、`hf_download_tool.py`（116 行，HF→JSONL，HF_TOKEN/HF_HUB_OFFLINE 环境变量 L25-29）、`dataflow_eval_tool.py`（1289 行评测重器）、`external_repo_runner.py`（1059 行，见 05 篇）。除 hf_search_tool 外全是普通类，由节点直接 import，不进 LangChain 工具链。

**ToolManager 双轨**（tool_manager.py）：按 role 分桶——pre_tool（L19-37）存 `func(state)->dict` 裸回调，`execute_pre_tools` 统一跑、异步自动 await（L30-33）、单失败置 None（L34-36）；post_tool（L40-47）存 LangChain Tool，仅在 `bind_post_tools=True` 时经 bind_tools 注入。pre 产出直进 state 不经 LLM，post 才要 schema 给模型看。`get_tool_manager()`（L51-55）进程级单例。

**CustomAgent 三层**：BaseAgent（agent.py L17-110 抽象基类）定死三抽象属性 role_name/system_prompt_template_name/task_prompt_template_name（L73-89），默认 `parse_result` 剥 ```json fence 后 json.loads、失败回退 `{"raw": content}`（L91-106）；`__init_subclass__`（L20-27）定义期试实例化但异常全吞。CustomAgent（L113-201）补骨架：`create_llm`（L150-171）按 `DF_MODEL_NAME > OE_MODEL_NAME > 节点 model_name` 优先级解析（L153-157）；run 三步——组消息、ainvoke、parse 写回（L179-192）。业务 Agent 最小样板 `query_understand_agent.py`（54 行）：三 property（L16-26）+ run（L29-54），结果写 `state.result[self.role_name]`（L51）——以角色名为键是全框架约定。

**CustomLLMCaller 二分**（custom_llm_caller.py L203-231）：`bind_post_tools=False`（多数情况）→ `_call_raw_api`（L138-197）httpx 直 POST `{base_url}/chat/completions`，`_convert_lc_message`（L90-136）做 LangChain→OpenAI 五分支转换，**429/502/503/504 重试 3 次**退避 `0.6*(attempt+1)`s（L148-168）；`bind_post_tools=True` → 取该角色 post_tools 走 `ChatOpenAI(...).bind_tools`（L224-229）。`ainvoke`（L233-237）恒走无工具分支。超时链 timeout_s > OE_TIMEOUT_S > DF_TIMEOUT_S > 60（L66-70）。任务书提到的 `runToolAgent`：全仓检索**不存在**，工具执行全收敛在双模式分流里。

**dataflow_eval_tool 三个亮点**：①`RobustAPILLMServing`（L28-83）临时猴子补丁替换 session.post（L39-48）把 DataFlow 内部吞掉的 429 重抛，指数退避+抖动重试（L60-83）——不改上游源的侵入式容错；②类级缓存 `_cached_llm_serving`（L94-95）防每次重载 vLLM，`release_serving`（L97-107）释放显存；③`_normalize_api_url`（L117-135）归一任意 URL 形态到 `.../chat/completions`。入口 `run_eval` L986，`_emit` 进度回调 L1022 供 server 轮询。

## 外部连接

- 上游依赖：huggingface_hub、DataFlow 库、langchain-core/openai、httpx。
- 被 nodes 消费：node import 对应 agent 并传入 ToolManager 单例（query_understand_node.py L24-30）。
- 环境变量契约：OE_API_BASE/OE_API_KEY/DF_MODEL_NAME/OE_MODEL_NAME/OE_TIMEOUT_S/HF_TOKEN。
- prompt 与代码解耦：模板名统一到 utils/prompts.py 的 prompt_registry（agent.py L8/L173-176）。

## 数据流

```
LangGraph 调度 → Node.run(state)（query_understand_node.py L20）
  → tm = get_tool_manager()（L24 单例）
  → agent = QueryUnderstandAgent(tm, model_name="gpt-4o")（L27-30）
  → agent.run：get_prompt 取模板 → create_llm 解析模型名（agent.py L153-157）
  → CustomLLMCaller.call(msgs, False) → httpx POST（429 退避 3 连试）
  → parse_result → state.result["QueryUnderstandAgent"]（L51）→ checkpoint
```

需要工具的 Agent（如 bench_resolve_agent.py L203 的 run）则 `bind_post_tools=True`，模型在对话里发起 tool_calls，由 ChatOpenAI executor 循环执行 hf_search_tool。

## 设计决策（含批判）

1. 双轨工具体系清晰（pre=确定性准备、post=LLM 自主调用），但严重失衡：post 轨全仓只有 hf_search_tool 一个 Tool 挂靠，pre 轨几乎无人用——ToolManager 更像预留架构位。
2. **register_custom_tool 死链**：core/graph.py L122/L129 调 `tm.register_custom_tool`，而 ToolManager 没这方法；未炸全靠 L116-117 `hasattr(self,"custom_tool_registry")` 守卫提前返回（字段只在 custom_tool 装饰器 L100-108 被用时懒创建，全仓无人用）。真注册时抛 AttributeError 且 L128 `except TypeError` 接不住，直接崩（详见 12 篇 A3）。
3. **硬编码 fallback API**：默认端点公网 IP `http://123.129.219.111:3000/v1`（agent.py L128-131）——不设环境变量时 Agent 请求默认打向它（12 篇 B4）。
4. `"argument" in str(e)` 降级重调（graph.py L159-168）会误捕节点内部业务 TypeError 致静默重跑，窄而险。
5. 裸 httpx 而非 ChatOpenAI 是合理性能选择（掌控重试日志），代价是双路径行为可能有微妙差异。

## 新人提示

- 新增 Agent：抄 query_understand_agent.py 改三 property 和 run，prompt 注册进 utils/prompts.py，node 层照抄挂进 workflow。
- 排查"请求打到奇怪地址"：`env | grep OE_`，再看 agent.py L128-135 默认值链。
- 新工具要被 LLM 调用：@tool 装饰（照抄 hf_search_tool.py）+ post 轨按角色注册；pre 轨只放无需 LLM 决策的函数。
- 读 dataflow_eval_tool.py 先看 L86-115（类与缓存）、L986（run_eval）、L28-83（429 补丁），其余 `_normalize_*` 是清洗碎片，用到再查。

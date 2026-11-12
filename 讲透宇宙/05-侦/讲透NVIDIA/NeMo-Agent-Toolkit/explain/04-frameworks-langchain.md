# 04 框架适配器群：nvidia_nat_langchain 与三种 agent 范式

## 一、角色定位

`packages/` 下 35 个 `nvidia_nat_*` 包中最大的框架适配器是 `nvidia_nat_langchain`：把 LangChain/LangGraph 生态翻译成 NAT 的组件注册体系，写 `_type: react_agent` 即得完整 LangGraph 工作流。NAT 的 YAML 配置语言是稳定内核，LangChain 是可替换外壳；并列同类 `nvidia_nat_agno/llama_index/adk/autogen/crewai/semantic_kernel/strands/mem0ai/zep_cloud` 等均同构接入 `nat.plugins.<framework>`。

## 二、内部结构

### 包的统一形态：register.py 三件套

契约：`src/nat/plugins/<framework>/register.py` 入口聚合 → 子域聚合 → 叶子组件各带 register.py。顶层 `register.py:21-31` 纯副作用 import 完成注册（含 **agent** L27、**control_flow** L28）；`agent/register.py:19-26` 再聚合 react/rewoo/tool_calling/reasoning/responses_api/auto_memory/prompt_optimizer 七线及 per-user 变体。叶子目录三件套 = **config 定义（Pydantic）+ `@register_function` 装饰的 build 函数 + 图实现 agent.py**。

### react_agent：文本 ReAct 解析 + 可选 native tool calling

`react_agent/register.py:61` 定义 `class ReActAgentWorkflowConfig(AgentBaseConfig, OptimizableMixin, name="react_agent")`（勘误：任务书称 L48 附近，实为辅助函数 `_build_lc_config`）。关键字段：`max_tool_calls=15`（register.py:79，别名 `max_iterations`）、解析失败重试护栏（register.py:73）、`use_native_tool_calling=False`（register.py:95）；装饰器在 register.py:114。agent.py（523 行）中 `ReActAgentGraph(DualNodeAgent)`（agent.py:105）于 L154 组装 `prompt | self._maybe_bind_llm_and_yield(...)`：native 模式尝试 `bind_tools`，`NotImplementedError` 时**自动回退文本解析**（output_parser.py:84），跨供应商兼容的关键防御。

### rewoo_agent：一次规划、分步执行

`rewoo_agent/register.py:38` 的 `ReWOOAgentWorkflowConfig(name="rewoo_agent")` 用 planner/solver 双提示词（register.py:46/49）。612 行 agent.py 的核心：`_parse_planner_output`（agent.py:156）、`_parse_planner_dependencies`（agent.py:164，**按证据依赖分层，无依赖步骤并行**）、`_replace_placeholders`（agent.py:213）。ReWOO 先规划后执行，省每步回喂开销，代价是计划错了无法中途修正。

### tool_calling_agent：结构化直通车

`tool_calling_agent/register.py:78` 的 `ToolCallAgentWorkflowConfig(name="tool_calling_agent")` 要求 LLM 原生支持 tool calling：`handle_tool_errors`（register.py:81）、`max_iterations=15`（register.py:82）、`return_direct`（register.py:97，跳过 LLM 后处理直接返回）。独有的防御层：`TruncationRetryConfig`（register.py:47/89）与 `max_empty_response_retries`（register.py:92）。

### 公共底座与特殊成员

图实现共享 `base.py` 的 `BaseAgent(ABC)`（base.py:138；L156/L220/L346 分别为流式调用/工具执行/图组装）；`dual_node.py:33` 的 `DualNodeAgent` 把 agent_node/tool_node/conditional_edge 接成 LangGraph 循环（L48-59）。偏离主模式者：`responses_api_agent/register.py:34` 的 config 继承 `FunctionBaseConfig` 而非 `AgentBaseConfig`（直连 OpenAI Responses API）；`prompt_optimizer/register.py:27/100` 的 `prompt_init`/`prompt_recombiner` 实为工具函数。

## 三、外部连接

**注册机制在 nvidia_nat_core，依赖彻底反转。** `register_workflow.py:172` 的 `register_function` 把 build 函数包成 `asynccontextmanager` 写入 `GlobalTypeRegistry`；`runtime/loader.py:128` 的 `discover_entrypoints` 在 L139 明言 aiq 前缀组名保留兼容（前身 AIQ），L140 定组名 `nat.plugins`/`nat.components`。起点是 `pyproject.toml:109-111`：

```toml
[project.entry-points.'nat.components']
nat_langchain = "nat.plugins.langchain.register"
```

**装机即注册**：loader 取 entry point（loader.py:151）后 `entry_point.load()` 触发 import 瀑布，core 因此**不 import langchain 也能构建任何工作流**——langchain 依赖全压在 build 函数体内 lazy import（react_agent/register.py:116-120）。

**对 nat optimize**：react_agent 的 config 继承 `OptimizableMixin`（core `optimizable.py:216`），`additional_instructions` 是 `OptimizableField`（register.py:104）且带 `SearchSpace(is_prompt=True)`（optimizable.py:49），即可被提示词进化优化；`nat optimize` 命令由 `nvidia_nat_config_optimizer/pyproject.toml:69-70` 经 `nat.cli` entry point 插件化注册。

## 四、数据流：一个 agent 组件从注册到被 config.yml 引用

1. **安装期**：安装即写入 entry point `nat.components.nat_langchain`；
2. **启动与注册**：任意 `nat` 命令触发 `discover_and_register_plugins`（loader.py:182），`entry_point.load()` 级联执行两层 register.py，装饰器（register.py:114）把 `(full_type, config_type, build_fn)` 写进 GlobalTypeRegistry；
3. **配置解析**：`examples/agents/react/configs/config.yml:39-44` 的 `workflow: _type: react_agent` 按判别字段查出 config 类并 Pydantic 校验（register.py:67）；
4. **构建期**：build_fn 内 lazy import langchain，`builder.get_llm/get_tools` 取模型与 BaseTool；
5. **运行期**：组图后文本解析或 bind_tools 循环至 `max_tool_calls` 或产出 final_answer。

关键性质：**注册是静态声明，构建是动态装配，运行是图执行**，三层互不耦合。

## 五、设计决策

**router_agent 不在 agent/ 目录（甄别结论）。** 仓内确有独立 router agent，但位于 `control_flow/router_agent/register.py:30`（`RouterAgentWorkflowConfig(name="router_agent")`）而非 agent/ 下。router 语义是"消息 + 分支列表交给 LLM 选一条"（`branches`，register.py:36；`max_router_retries=3`，register.py:40）——不做工具循环、不产出内容，是**编排原语**，与同目录的 parallel/sequential executor 同类。

**三种 agent 的取舍是显式的。** `references/agents.md:27-29` 给出判据：工具缺 JSON schema 或 LLM 不可靠支持 tool calling 选 react_agent（文本解析跨供应商更稳）；schema 良好选 tool_calling_agent；可容忍计划一次成型选 rewoo_agent。agents.md:41-42 的实战经验：某些 NVIDIA Inference API 模型在 native tool calling 下不调用工具，切回 false 即恢复——默认 False 的原因。

**低成本扩展。** `register_per_user_agent.py:31/39` 注册 `per_user_react_agent`（config 继承复用，每用户惰性实例化）；`auto_memory_wrapper/register.py:33/116` 的 `auto_memory_agent` 挂持久记忆——都是"config 继承 + 装饰器复用"样板。

## 六、新人提示

按"注册面 → 公共底座 → 单个 agent"三步读：两个聚合 register.py → base.py:138 与 dual_node.py:33 → react_agent 一条线（register.py:61-114 → agent.py:97-154 → output_parser.py:84）。三个坑：config 加字段须带 AliasChoices 兼容旧名（register.py:71/75/80）；新组件必须挂进 register.py 聚合链；新框架适配器照抄 langchain 包形态，core 侧零改动。调试用 `nat info components -t function` 看注册表全部 `_type`。

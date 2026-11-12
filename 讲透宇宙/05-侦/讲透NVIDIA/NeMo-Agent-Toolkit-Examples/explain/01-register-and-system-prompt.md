# 01 注册与提示词层：register.py 与 130 行系统提示词——全仓 NAT 注册范式

## 角色定位

`examples/sandbox_agent/src/nat_sandbox_agent/register.py`（317 行）是整个 sandbox_agent example 接入 NAT（NeMo-Agent-Toolkit）框架的唯一入口：它把一个普通 Python 包变成 NAT 组件注册表中可被 YAML `_type` 引用的 workflow。同目录 `prompts/system_prompt.py`（174 行）则承载 agent 的行为规范——正文 L17-150 是一段约 130 行的系统提示词，全仓最重的一份 prompt 资产。二者合起来回答两个问题：**"一个 example 如何被框架发现"**（注册范式）与**"agent 的行为宪法从哪来"**（提示词工程）。NeMo-Agent-Toolkit-Examples 仓 12 个 example 里，sandbox_agent 是把 NAT 注册三件套（Config 类 + `@register_function` 装饰器 + builder 依赖注入）展示得最完整的范本。

## 内部结构

register.py 是清晰的四段式：

1. **配置类** `SandboxAgentWorkflowConfig(FunctionBaseConfig, name="sandbox_agent")`（register.py:48）——pydantic 模型，类参数 `name="sandbox_agent"` 即注册名，YAML 里 `workflow._type: sandbox_agent` 按此匹配。字段覆盖 agent 全部可调项：`llm_name: LLMRef` 必填（register.py:57），`vision_llm_name` 可选、为 None 时 image_describe 工具直接禁用（register.py:61-64）；`max_iterations` 默认 20（register.py:67）；`max_observation_tokens` 默认 10000（register.py:71）；`sandbox_config` 是裸 dict、默认给出 docker+python:3.12-slim+1g 内存+2 CPU 的完整样例（register.py:77-85）；`enabled_tools` 白名单（register.py:88）与 `system_prompt`/`additional_instructions` 双提示词槽（register.py:94-101）。
2. **状态类** `AgentState(TypedDict)`（register.py:107），详见第 5 篇。
3. **装饰器注册** `@register_function(config_type=..., framework_wrappers=[LLMFrameworkEnum.LANGCHAIN])`（register.py:118-121）。
4. **异步工厂主体** `sandbox_agent_workflow(config, builder)`（register.py:122），从建沙箱（register.py:145）到 yield 响应函数（register.py:305），`finally` 块保证沙箱必被销毁（register.py:311-317）。

system_prompt.py 两段：常量 `SANDBOX_AGENT_SYSTEM_PROMPT`（system_prompt.py:17-150）+ 组装函数 `get_system_prompt`（system_prompt.py:153-174），后者支持追加 `additional_instructions`（system_prompt.py:168-169）和按 `available_tools` 名单附注（system_prompt.py:171-172）。

## 外部连接

- **上游框架**：`nat.builder.builder.Builder`、`nat.cli.register_workflow.register_function`、`nat.data_models.component_ref.LLMRef`（register.py:33-40）——register.py 是 example 与 NAT 内核之间的全部接触面；LangChain/LangGraph 仅经 `LLMFrameworkEnum.LANGCHAIN` 包装进入（register.py:120）。
- **import 副作用注册**：包根 `nat_sandbox_agent/__init__.py:42-43` 显式 `from . import register`，注释写明 "Import registration to enable NAT component discovery"——不 import 就不注册，这是 NAT entry-point 范式的关键一环，新人最常漏。
- **下游三模块**：prompts（register.py:38）、sandbox.factory（register.py:39）、tools.factory（register.py:40）、utils.answer_cleaning（register.py:41），register.py 是四个子系统的唯一汇聚点。
- **YAML 侧**：configs/config.yaml 的 `workflow._type: sandbox_agent` 与 `llms.agent_llm._type: nim` 经 `llm_name: agent_llm` 引用串起 LLM 与 workflow（config.yaml 中 llm_name 行）。

## 数据流

冷启动路径：NAT 加载 YAML → 包 import 触发注册（`nat_sandbox_agent/__init__.py:42`）→ `_type` 匹配 `name="sandbox_agent"`（register.py:48）→ 调用工厂 → `create_sandbox_from_dict(config.sandbox_config)`（register.py:145）→ `sandbox.start()`（register.py:150）→ `builder.get_llm()` 取 LLM（register.py:154-157），vision LLM 可选分支（register.py:161-165）→ `create_all_tools()` 建工具（register.py:173-178）→ `llm.bind_tools`（register.py:182）→ 系统提示词组装 `config.system_prompt or get_system_prompt(...)`（register.py:185-188）→ `yield _response_fn`。注意 register.py:172 的换算 `max_output_chars = config.max_observation_tokens * 4`——把 token 预算近似转成字符预算（约 4 字符/token）传给工具层做截断，配置口径（token）与执行口径（char）在此分界。

## 设计决策

1. **注册范式=pydantic Config 子类而非装饰器参数表**。全部可配置项收进带 Field description 的模型（register.py:56-101），NAT 因此能做配置校验与文档生成；example 作者只需声明 schema，框架负责实例化。
2. **提示词内容与配置解耦**。130 行正文放 prompts 层常量，config 只留覆盖槽（register.py:94-101）；`additional_instructions` 是追加而非替换（system_prompt.py:169），保证基础规则永不丢失。
3. **提示词本身是"规则化宪法"而非人设**：L23-44 按宿主/沙箱两族列工具并写明分工（如 "Do NOT use shell for data processing; use python instead"，system_prompt.py:24-25）；L46-56 固定 /workspace 四目录布局；L66-81 专治 LLM 常见病——Python 工具不回显表达式值，所以 "ALWAYS use print()"（system_prompt.py:69）与 "empty stdout 意味着忘了 print"（system_prompt.py:81）；L83-95 给出扩展名→工具分派表（xlsx→pandas、pdf→pdfplumber、mp3→faster_whisper "tiny" 预装）；L117-118 "NEVER declare a problem impossible without writing Python code"是针对 GAIA 类基准的反弃答锚。
4. **vision LLM 缺席即降级**而非报错（register.py:161-165），工具族随配置自适应收缩。
5. **沙箱生命周期绑在工厂 finally**（register.py:311-317）而非 response 函数内——一次 workflow 装载对应一个沙箱、多个问题共享；只有卸载 workflow 才销毁容器。

## 新人提示

- 想被 NAT 发现，三件事缺一不可：Config 类带 `name`（register.py:48）、`@register_function`（register.py:118）、包 `__init__` import register 模块（`nat_sandbox_agent/__init__.py:42`）。
- 改提示词优先改 `additional_instructions`（YAML 注入），不要动 130 行常量——它是与工具描述联动的（工具 description 也写了分工，见 execution.py:137-143），单边改动会制造矛盾。
- `max_observation_tokens` 是近似 token 数、实际截断按 ×4 字符执行（register.py:172），调参时别被两个口径绕晕。
- system_prompt.py:150 结尾的 image 规则（"Never trust the vision model's calculations"，system_prompt.py:147）与 image_describe 工具描述（image_describe.py:172-173）互为印证，是跨文件一致性设计的样例。
- 测试锚点：test_prompts.py 与 test_register.py 分别锁提示词组装与配置默认值，改字段名先看这两份测试。

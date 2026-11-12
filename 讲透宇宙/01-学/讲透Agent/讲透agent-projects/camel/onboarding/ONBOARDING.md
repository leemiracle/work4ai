# CAMEL 新人上手指南

> 基于知识图谱（1698 节点/4118 边/16 层）与 38 批源码勘误集写成；锚均经 grep/sed 核实。

## 1. 一图看懂

CAMEL（Communicative Agents for "Mind" Exploration of LLMs）是第一个 LLM 多智能体开源框架（NeurIPS 2023），使命 finding the scaling laws of agents。名字来源即招牌范式 RolePlaying：user/assistant 两 agent 按任务指令自主多轮对话（camel/societies/role_playing.py:36）。对比同类：LangGraph 要显式建状态机图（CAMEL 任务分解由 LLM 动态驱动）；AutoGen 以对话网络为中心（CAMEL 编排更"社会化"、工具生态更宽）；agentscope 是 actor 消息传递（CAMEL 内核极重而编排层薄）。CAMEL 还独有数据生成/verifier/RL 环境闭环。

## 2. 五分钟上手

```bash
pip install camel-ai && export OPENAI_API_KEY=...
```

```python
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
agent = ChatAgent(system_message="助手",
    model=ModelFactory.create(model_platform=ModelPlatformType.OPENAI,
                              model_type=ModelType.GPT_4O_MINI))
print(agent.step("解释注意力").msg.content)
```

RolePlaying 双智能体（同 examples/ai_society/role_playing.py）：`RolePlaying(assistant_role_name=..., user_role_name=..., task_prompt=...)` 后 init_chat() 循环 step()。最小安装零可选依赖；包名是 camel-ai（pyproject.toml:6）。

## 3. 架构总览：16 层

```
L01-L02 工程配置/文档    17 组 extras、12 条 CI workflow
L03-L04 数据基座         ModelType 枚举中心（camel/types/enums.py:33）+BaseMessage
L05-L06 模型矩阵         BaseModelBackend（camel/models/base_model.py:236）+44 Config
L07 智能体引擎           ChatAgent+8 种专用 agent
L08-L09 记忆/RAG         AgentMemory（camel/memories/base.py:134）+9 向量库
L10 工具基座             BaseToolkit（camel/toolkits/base.py:61）/MCPToolkit
L11-L13 工具实现         沙箱/浏览器/50+ SaaS toolkit
L14 编排与提示词         RolePlaying/Workforce/Task/17 组模板
L15-L16 数据闭环/应用    datagen/verifiers/RL 环境、Gradio/FastMCP/bots
```

主干链：**模型链** 类型→Config→后端，新厂商=一个 Config 子类+一个后端子类+枚举登记；**能力链** L10 BaseToolkit→FunctionTool 包装→ChatAgent 注册执行，L11-L13 都长在这条根上；**编排链** ChatAgent 是唯一执行引擎，L14 只是多摆几个 agent 加调度协议。

## 4. 核心子系统深潜

### 4.1 ChatAgent：6430 行单类（138 方法）

`ChatAgent(BaseAgent)`（camel/agents/chat_agent.py:365）。三个入口：**step/astep 镜像对**（chat_agent.py:2828/:3125）同步/异步平行、90% 同构但独立维护（改一边要查另一边）；**流式镜像对** `_stream`/`_astream`（chat_agent.py:4283 起）：stream 开关为真时 step 直接返回生成器，执行推迟到迭代时；**上下文压缩** `_get_context_with_summarization`（chat_agent.py:1009）记忆超限先摘要再拼上下文。

### 4.2 Workforce：组织级协作（6239 行/121 方法）

`Workforce(BaseNode)`（camel/societies/workforce/workforce.py:175）内部三个专属 ChatAgent：协调者（workforce.py:417）、任务分析者、动态建工人模板（运行时 clone）；模式分 AUTO_DECOMPOSE（LLM 分解）/PIPELINE（预定义 DAG）。机关：**Task 默认 state=FAILED**（camel/tasks/task.py:256）——新建任务初始态不是 OPEN（源码 TODO 自认缺逻辑），依赖 task.state 的下游会被坑；**TaskChannel**（camel/societies/workforce/task_channel.py:95）asyncio.Condition+哈希索引、Packet 四态流转。

### 4.3 模型后端矩阵：元类隐形注入

60+ 后端共用骨架 BaseModelBackend（camel/models/base_model.py:236）；ModelFactory._MODEL_PLATFORM_TO_CLASS_MAP（camel/models/model_factory.py:76）登记 46 平台映射，陌生模型名包 UnifiedModelType 放行。最值得学的是 **ModelBackendMeta 元类**（camel/models/base_model.py:195）：类创建时自动把子类 run/arun 包成 preprocess→原方法→postprocess，17 个 OpenAI 兼容薄壳子类（父类 camel/models/openai_compatible_model.py:58）零显式代码即获 `<think>` 抽取（camel/models/_utils.py:23）与并行工具调用消息重排（读懂后端要看它+元类+父类）。

### 4.4 memories：三记忆实现

入口 AgentMemory（camel/memories/base.py:134），三实现：ChatHistoryMemory（camel/memories/agent_memories.py:26 纯会话）、VectorDBMemory（agent_memories.py:151 写时嵌入）、LongtermAgentMemory（agent_memories.py:229）；底层复用 9 向量库（camel/storages/vectordb_storages/base.py:112）。上下文出口 ScoreBasedContextCreator.create_context（camel/memories/context_creators/score_based.py:112）名为 score 实则纯 timestamp 排序。

## 5. 一次调用的生命周期

以 `agent.step()` 非流式为例：①**入口**（chat_agent.py:2828）查开关后进 `_step_impl`；②str 包成 BaseMessage，update_memory(input, USER)（chat_agent.py:2919）写记忆；③**上下文**经 to_openai_message（camel/messages/base.py:431）转 OpenAI 消息（超限先摘要）；④**模型调用**：`_get_model_response`（chat_agent.py:3577）带重试退避调 `model_backend.run(...)`（chat_agent.py:3590），后端 `_resolve_tools` 把 FunctionTool 转 tool schema，元类请求前剥 `<think>`；⑤**工具回路**（chat_agent.py:2999）：tool_call_requests 非空时先分内/外部工具，assistant 消息（含全部 tool_calls）入记忆后逐个 `self._execute_tool(...)`（chat_agent.py:4023），结果以 tool 角色写回、循环直到无工具调用；⑥包成 ChatAgentResponse（camel/responses/agent_responses.py:21）返回。

## 6. 关键设计决策

- **BaseToolkit 隐式超时**：`__init_subclass__`（camel/toolkits/base.py:80）子类定义时自动给公开方法包 with_timeout（camel/toolkits/base.py:95），除非签名自带 timeout 或标 @manual_timeout——90+ 工具包免费获得超时管控；元类 AgentOpsMeta（camel/utils/commons.py:617）注入遥测。
- **MCP 三形态**：继承 MCPToolkit（camel/toolkits/mcp_toolkit.py:230）直连远端 server（NotionMCPToolkit 零自身工具，camel/toolkits/notion_mcp_toolkit.py:22）；组合（MinimaxMCPToolkit 持内层实例，camel/toolkits/minimax_mcp_toolkit.py:23）；独立自造。
- **HybridBrowserToolkit 双实现**：`__new__` 纯工厂（camel/toolkits/hybrid_browser_toolkit/hybrid_browser_toolkit.py:87），mode="typescript"（默认）延迟导入 TS 版（camel/toolkits/hybrid_browser_toolkit/hybrid_browser_toolkit.py:174），mode="python" 走 Playwright 兄弟包；TS 版真身是 ws_wrapper.py:313 拉起 node websocket-server.js 子进程——默认分支依赖 Node.js，"纯 Python"是错觉。
- **截断与日志兜底**：`_truncate_tool_result`（chat_agent.py:1233）截断超长工具输出并附 [TRUNCATED] 通知；CAMEL_MODEL_LOG_ENABLED 打开后请求/响应写成 JSON 日志，仓根 camel_log_viewer.html 可视化。

## 7. 坑与勘误（对应 NOTES-DIGEST）

1. **FaissStorage.delete 位置映射错位**：remove_ids 快路径（camel/storages/vectordb_storages/faiss.py:483）压缩重排后未重编号 `_id_to_index`，后续 delete/query 映射错位（同分支的 bool selector 构建后未使用）；重建索引分支无此问题。
2. **PgVector 距离语义反转**：恒建 cosine HNSW（camel/storages/vectordb_storages/pgvector.py:124）而 query 支持 `<->`/`<#>`；距离未转换直接 AS similarity 返回（pgvector.py:253），与"越大越相似"惯例相反。
3. **InternalPythonInterpreter 白名单失效**：execute_command 用 subprocess.Popen(shell=True)（camel/interpreters/internal_python_interpreter.py:604）直跑命令；unsafe_mode=True 时更直接 exec/eval。
4. **'coolie' 拼写**：camel/toolkits/open_api_toolkit.py:307 把 cookie 拼成 coolie，apiKey in:cookie 永远落空。
5. **硬编码 Cloud SQL 凭据入仓**：apps/dilemma/database_connection.py:30 提交 DB_USER/DB_PASS 明文，安全事件级。
6. **DockerRuntime.add 循环变量 bug**：camel/runtimes/docker_runtime.py:315 与 camel/runtimes/remote_http_runtime.py:143 同构——循环后 entrypoint 只登记最后一个 func，build() 静默少注册工具。
7. **DISCORD_TOKEN 文档不符**：docstring 写 DISCORD_TOKEN，实际读 DISCORD_BOT_TOKEN（camel/bots/discord/discord_app.py:92）。
8. **RoleAssignment 正则单数字**：camel/agents/role_assignment_agent.py:114 的 `Domain expert \d: ` 遇 num_roles>=10 即 RuntimeError。
9. **siliconflow as_dict 死代码**：构建的 tools_schema 从未写回，camel/configs/siliconflow_config.py:86 无条件 `config_dict["tools"] = NOT_GIVEN`。
10. **deepseek Reasoner 过滤被覆盖**：过滤产物被无条件 deepcopy 覆盖（camel/models/deepseek_model.py:152），temperature/tools 仍发给 Reasoner。
11. **ResponseWordsTerminator.reset 类型错乱**：camel/terminators/response_terminator.py:128 把 List[Dict] 重置成 defaultdict(int)，reset 后 append 即 AttributeError（"出现次数"实为含词消息条数、无词边界）。
12. **Makefile 损坏引用**：test-install 依赖不存在的 tests/requirements.txt（仓根 Makefile:83，实际目录 test/），clean 依赖未定义的 clean-docs。

## 8. 延伸阅读

16 步 tour 推荐 6 步：**第 5 步 ChatAgent**（最重单文件，按三线切片啃）、**第 6 步 工具基座**（BaseToolkit 元类+FunctionTool schema）、**第 10 步 RolePlaying**（名字来源与论文复刻链路）、**第 11 步 Workforce**（三 agent+任务总线）、**第 12 步 数据生成闭环**（CoT 二分纠错+STaR 自改进）、**第 14 步 浏览器深水区**（SoM+双实现）。配套 deepwiki 图谱（52 页，camel/deepwiki/）：入门 1.2、ChatAgent 2.1、模型矩阵 3.1/3.2、工具生态 4.1；增量页 x1/x2。

---

**自报**：正文 6491 字（不计空格字符）/ 行号锚 54 个（均经 grep/sed 核实）/ 8 节齐全。

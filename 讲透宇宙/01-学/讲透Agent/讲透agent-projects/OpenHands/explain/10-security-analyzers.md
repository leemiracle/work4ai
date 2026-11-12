# 10 · openhands/security/：防提示注入分析器三家族（Invariant / GraySwan / LLM）

## 1. 角色定位

`openhands/security/` 是 V0 的**动作风险审计层**：每当 agent 要执行危险动作（命令、编辑、浏览、MCP 调用），`AgentController` 在确认闸门处调 `security_risk(action)`，分析器返回 LOW/MEDIUM/HIGH/UNKNOWN，HIGH 或"无分析器的 UNKNOWN"强制人工确认（`openhands/controller/agent_controller.py:997-1021`）。三个实对应三种哲学：**InvariantAnalyzer** 把轨迹送进本地 Docker 跑的 Invariant Labs 策略监控器（规则引擎）；**GraySwanAnalyzer** 调 GraySwan Cygnal 云 API 做 AI 安全评分（专攻间接提示注入 IPI）；**LLMRiskAnalyzer** 纯透传 LLM 自报的风险等级。全目录 Legacy-V0 头注（`openhands/security/analyzer.py:1-7` 等，批 16 阶段实证），但防注入问题域在 V1 中继续存在——这批文件是研究"agent 安全如何产品化"的完整标本。

## 2. 内部结构

**基座** `openhands/security/analyzer.py:15` 的 `SecurityAnalyzer` 是极薄抽象类：`handle_api_request`（`:22-26`）与 `security_risk`（`:28-32`）直接 `raise NotImplementedError`，而 `set_event_stream`（`:34-40`）与 `close`（`:42-44`）是**空实现的可选钩子而非抽象方法**——子类只需实现前两个即可用。选择表在 `openhands/security/options.py:9-13`：`SecurityAnalyzers = {'invariant': ..., 'llm': ..., 'grayswan': ...}`，按配置字符串取类。

**InvariantAnalyzer**（`openhands/security/invariant/analyzer.py:22`）是重资产路线。类属性声明容器名 `openhands-invariant-server`、镜像 `ghcr.io/invariantlabs-ai/server:openhands`、180 秒超时（`openhands/security/invariant/analyzer.py:27-30`）。构造即运维（`openhands/security/invariant/analyzer.py:32-94`）：`docker.from_env()` 失败直接 re-raise（`openhands/security/invariant/analyzer.py:44-51`，日志明示"请检查 Docker 在跑或去设置里关掉分析器"——**没 Docker 就抛异常**）；容器三级查找——在跑的复用（`openhands/security/invariant/analyzer.py:52-54`）、停着的重启（`:56-61`）、都没有就 `containers.run` 拉镜像起服务（`:62-70`，`find_available_tcp_port` 随机映射宿主端口）；轮询等容器 running（`:74-82`）；从 `container.attrs` 反查实际端口（`:84-86`）；policy 缺省时从服务端 `Policy.get_template()` 拉默认模板（`:90-94`）。运行期 `security_risk`（`openhands/security/invariant/analyzer.py:117-132`）四步：`parse_element` 把新事件转 Invariant 轨迹节点并 extend 本地 trace（`:119-121`）→ `monitor.check(past, pending)` 增量检查（`:122-123`）→ 出错只 warning 返回 UNKNOWN（`:127-130`）→ `get_risk` 用正则 `(?<=risk=)\w+` 从结果串抠风险词取最大值（`:99-115`，`:105` 的正则）。`close` 停容器（`:96-97`）。

**InvariantClient**（`openhands/security/invariant/client.py:14`）是裸 httpx 客户端，无 SDK：构造即建会话（`_create_session` 轮询重试至 120 秒，`openhands/security/invariant/client.py:25-46`），内嵌两个命名空间类 `_Policy`（`:58-104`，create/template/analyze）与 `_Monitor`（`:106-147`，`check(past_events, pending_events)` POST 增量轨迹，`:133-147`）。

**parser**（`openhands/security/invariant/parser.py`）做 OpenHands 事件→Invariant 节点的翻译：`TraceElement = Message | ToolCall | ToolOutput | Function` 四类型联合（`openhands/security/invariant/parser.py:26`，节点定义在 `nodes.py`）。`parse_action`（`openhands/security/invariant/parser.py:46-67`）：用户/助手 `MessageAction` 翻成对应 role 的 `Message`（`:49-53`）；带 `action` 属性的动作先抽出 `thought` 翻成 assistant Message（`:59-63`），其余打包 `Function(name, arguments)` 塞进 `ToolCall`（`:61-64`），`get_next_id` 用"找最小未用整数"保证 ID 稠密（`:29-34`）。`parse_observation`（`openhands/security/invariant/parser.py:70-80`）把观察内容挂到 `ToolOutput(tool_call_id=last_id)`——靠 `get_last_id` 反查最近 ToolCall 配对（`:37-43`）。`parse_element`（`:83-88`）是分发口，`parse_trace`（`:91-96`）批量驱动，`InvariantState`（`:99-109`）提供增量容器。这条"thought 先行、ToolCall 随后、ToolOutput 回挂"的轨迹结构就是 Invariant 策略语言的输入模型。

**GraySwanAnalyzer**（`openhands/security/grayswan/analyzer.py:25`）走云 API：构造期 `GRAYSWAN_API_KEY` 缺失即抛 ValueError（`openhands/security/grayswan/analyzer.py:55-60`）；`GRAYSWAN_POLICY_ID` 缺省回退**硬编码默认策略 ID `689ca4885af3538a39b2ba04`**（"GraySwan default coding agent policy"，`openhands/security/grayswan/analyzer.py:62-67`）；端点 `https://api.grayswan.ai/cygnal/monitor`（`:82`）。`security_risk`（`:170-204`）先用 `View.from_events` 重建"agent 的 LLM 真正看到的上下文"（`:183`，注释明说这样裁剪/摘要/掩码语义一致）再取尾部 `history_limit=20` 条（`:184-188`），经 `convert_events_to_openai_messages`（`openhands/security/grayswan/utils.py:30`，跳过五类内部事件 `openhands/security/grayswan/utils.py:40-47`）转 OpenAI 消息格式发云。`_call_grayswan_api`（`openhands/security/grayswan/analyzer.py:125-164`）：violation 分数按 0.3/0.7/1.0 三阈值映射风险级（`_map_violation_to_risk`，`:116-123`），**`'ipi' in result` 直接强制 HIGH**（间接提示注入一票升级，`:146-149`），任何异常/超时一律 UNKNOWN（`:159-164`）。API key 双头注入 `Authorization: Bearer` 与 `x-grayswan-api-key`（`:99-103`）。

**LLMRiskAnalyzer**（`openhands/security/llm/analyzer.py:19`）最简：`security_risk` 只 `getattr(action, 'security_risk')` 透传 LLM 在工具调用时自报的等级（`:32-48`），不认识就 UNKNOWN——把判断权完全交给模型自身的 49 行实现。

## 3. 外部连接

消费链上游是 controller：`openhands/controller/agent_controller.py:17-18` TYPE_CHECKING 前置 import `SecurityAnalyzer`，实例由 runtime 传入（`openhands/server/session/agent_session.py:451`：`security_analyzer=self.runtime.security_analyzer if self.runtime else None`），确认闸门在 `_handle_security_analyzer`（`openhands/controller/agent_controller.py:216-254`）调用并覆写 `action.security_risk`。风险枚举与动作类型来自 `openhands/events/action/action.py`（`parser.py` 的 imports `:11-24`；`openhands/security/invariant/analyzer.py:15`）。事件序列化借 `events/serialization/event.py` 的 `event_to_dict`（`openhands/security/invariant/parser.py:23`）；GraySwan 线额外依赖 `openhands/memory/view.py` 的 View（`openhands/security/grayswan/analyzer.py:20`，与 condenser 家族共享同一个"LLM 视角"定义——这是本目录与 memory/ 的隐性耦合）。docker/httpx/aiohttp 三个外部客户端家族各占一线（`openhands/security/invariant/analyzer.py:12`、`openhands/security/invariant/client.py:11`、`openhands/security/grayswan/analyzer.py:14`）。下游：`security_risk` 结果由 controller 的确认逻辑消费；`handle_api_request` 预留给 webhook 类扩展（GraySwan 实现返回占位 `{'status': 'ok'}`，`openhands/security/grayswan/analyzer.py:166-168`）。

## 4. 数据流

以一次"agent 要跑 rm -rf"为线（Invariant 路线）：LLM 产出 `CmdRunAction` → controller `_step` 进入确认闸门（`openhands/controller/agent_controller.py:978-990`）→ `_handle_security_analyzer` 调 `analyzer.security_risk(action)` → `parse_element` 翻译出 thought Message + ToolCall 节点（`openhands/security/invariant/parser.py:56-64`）→ `monitor.check` POST `{past_events, pending_events}` 到 localhost 随机端口上的 Invariant 容器（`openhands/security/invariant/client.py:133-147`）→ 策略命中返回 `["risk=high ..."]` 串 → `get_risk` 正则抠词（`openhands/security/invariant/analyzer.py:105-115`）→ HIGH → `action.confirmation_state = AWAITING_CONFIRMATION`（`openhands/controller/agent_controller.py:1019-1021`）→ 状态机转 `AWAITING_USER_CONFIRMATION`（`openhands/controller/agent_controller.py:1030`）等人类点按钮。GraySwan 路线差异仅在"送云端的是 OpenAI 消息格式的近 20 条裁剪后历史"，IPI 命中一票 HIGH。

## 5. 设计决策

Legacy-V0→V1 语境下的三个决策：其一，**三哲学并存的注册表**（`openhands/security/options.py:9-13`）而非单实现——规则引擎（Invariant，可本地审计、要 Docker）、云 AI 评分（GraySwan，免运维、数据出域）、LLM 自评（零成本、零防护）是 agent 安全谱系的三个端点，产品让部署者选；V1 弃用了实现但保留了这个"风险分析是可插拔槽位"的架构判断。其二，**fail-safe 语义落在 controller 而非分析器**：分析器任何失败只返回 UNKNOWN（`openhands/security/grayswan/analyzer.py:159-164`、`openhands/security/invariant/analyzer.py:127-130`），而"UNKNOWN 无分析器=强制确认"（`openhands/controller/agent_controller.py:998-1001`）——安全层宁可烦人不可放行。其三，**GraySwan 用 View 而非原始历史**（`openhands/security/grayswan/analyzer.py:181-188`）：审计对象必须是"LLM 实际看到的内容"而非全量日志，否则裁剪/掩码后的注入内容会漏检——这是安全审计与上下文管理的正确对齐。代价面同样清晰：Invariant 构造期拉容器（`openhands/security/invariant/analyzer.py:64-70`）意味着"启用安全分析=强制 Docker+外网拉镜像"，CI 与离线环境直接不可用。

## 6. 新人提示

- **安全发现一**：`InvariantAnalyzer.__init__` 会自动从 ghcr.io 拉 `invariantlabs-ai/server:openhands` 镜像并起容器（`openhands/security/invariant/analyzer.py:28`、`:64-70`）——无 Docker 直接抛（`:44-51`），供应链上等于把策略引擎信任外包给镜像发行方。
- **安全发现二**：GraySwan 默认策略 ID **硬编码 `689ca4885af3538a39b2ba04`**（`openhands/security/grayswan/analyzer.py:64-66`）——不设 `GRAYSWAN_POLICY_ID` 时你的所有轨迹都按别人定义的"coding agent policy"判。
- **安全发现三**：GraySwan 线把近 20 条会话消息（含你的代码/秘密上下文）发到 `api.grayswan.ai`（`openhands/security/grayswan/analyzer.py:82`、`:184-191`），且 `logger.info(f'Payload: {payload}')`（`:137`）**把完整 payload 打进日志**——日志系统成了二次泄漏面。
- 勘误：`_handle_security_analyzer` docstring 说"无分析器设 HIGH"（`openhands/controller/agent_controller.py:220`），代码实际设 UNKNOWN（`:248-254`）——效果靠 `is_ask_for_every_action` 补齐（`:998-1001`），读文档会误判。
- `get_risk` 的正则 `(?<=risk=)\w+`（`openhands/security/invariant/analyzer.py:105`）在结果串含多个风险词时取 max（`:112-113`），但策略串里任何 `risk=...` 文本都会被抠走——自定义 policy 输出格式变化会静默降级为 LOW（映射不中时落 LOW 而非 UNKNOWN，`:112-115`，这是个值得商榷的默认）。
- `openhands/security/invariant/parser.py:64` 的 `ToolCall(id=next_id)` 用自造稠密整数 ID 而非事件真实 id——与真实事件 ID 对不上账，回溯审计时要靠顺序而非 ID。
- 基类 `set_event_stream`/`close` 是空实现钩子（`openhands/security/analyzer.py:34-44`），InvariantAnalyzer **没有覆写 `set_event_stream` 却在 `close` 里停容器**（`openhands/security/invariant/analyzer.py:96-97`）——多个会话共享同一容器名（`:27`），第一个会话 close 会把第二个会话的策略引擎停掉。
- 批 16 阶段实证整个 security/ 目录全批 Legacy-V0：改这里之前先确认 V1（app_server/外部 SDK）是否已有对应物，避免给将死代码打补丁。

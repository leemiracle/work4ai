# 11 A2UI 生成协议与 CUA 计算机使用引擎

> 对应导览 S13+S14。代表文件：`jiuwenswarm/server/runtime/a2ui/`（protocol.py 761 行/parser.py/integration.py）与独立打包的 `jiuwenswarm/cua_engine/src/computer_use/`。

## 一、角色定位

两个子系统共享"让 agent 输出超越纯文本"的目标但方向相反：**A2UI** 让 agent 的回答变成前端可渲染的交互 UI——模型在回复中输出 `<a2ui-json>` 块，Web 前端把它渲染成表单/卡片/确认流；**CUA**（Computer-Use Agent）让 agent 获得操作真实桌面的手——独立的 `cua_engine` 包提供 Computer/App/Element 三 facade 与原子执行引擎，"一个意图、一个 deadline、有限路由计划、不做不确定重放"（cua_engine/src/computer_use/execution/engine.py:1）。A2UI 是出口（展示层协议），CUA 是入口（感知与操控层），都遵守"宿主模块保持通用、子系统自带分支"的接线哲学（integration.py:2-7）。

## 二、内部结构

**A2UI 协议层**：`A2UIProtocolSpec` 是 v0.8 的唯一注册项，未来版本以新文件加入（a2ui/protocol.py:72-78）。`build_prompt` 双语生成系统提示——角色/UI 时机/工作流三段，钉死"块内必须是 JSON list、先 beginRendering 再 surfaceUpdate、父组件先于子组件、不得输出其它协议版本字段"（a2ui/protocol.py:100-137），再拼 autonomy 指令与可选浏览器工作流规则（a2ui/protocol.py:139-141），最后过 `_normalize_prompt_contract`——把 SDK 默认的 "JSON object 工作流" 措辞替换成 jiuwenswarm 的 "JSON list" 契约（a2ui/protocol.py:64-70,150）。

**解析层**：A2UI message 的判据是"恰含四键之一"——beginRendering/surfaceUpdate/dataModelUpdate/deleteSurface（a2ui/parser.py:17-23）。`parse_a2ui_response` 按优先级尝试四条路径：整体 JSONL（每行独立对象）→ 整体裸 JSON（list 或单对象）→ tagged 块（`<a2ui-json>` 分帧，容忍未闭合尾块，a2ui/parser.py:34-47,92-113）→ 全文按纯文本兜底。validator.py 建 data model 索引校验 path 引用与组件子树（a2ui/validator.py:51-115）；stream_guard.py 管流式分帧期 tagged 块的边界。运行时副包 runtime/ 有 finalizer/formatter/prompt/response_finalization/stream/team_stream（TeamA2UIBlockBuffer 供 team 场景）。

**CUA 引擎**：`__init__.pyi` 是三 facade 完整存根——Computer（连接的桌面会话，native driver 在第一次系统调用时才启动，__init__.pyi:50-51）/App（绑定工作窗口，或预备一个已安装 app 供首次读取时启动，:53-55）/Element（read/click/typeText/paste/pressKey/focus/openMenu，:83-100）。execution/engine.py 的 `Engine.execute` 先做 retired/busy 双闸（退役会话报 execution_unknown、占用中报 invalid_request，cua_engine/src/computer_use/execution/engine.py:33-39），`with self.native.calls.claim(timeout_ms)` 领取**剩余预算**再进 `execute_in_call`（cua_engine/src/computer_use/execution/engine.py:40-41）；入参校验三铁律：launch 意图必须配 ApplicationBinding 且无 path/参数、有限查询等待必须有 element path、scoped path 必须有"已观察到的可达工作窗口根"（cua_engine/src/computer_use/execution/engine.py:46-61）；随后 operation lease 内 `resolve_path` 解析路径、进入路由选择循环（cua_engine/src/computer_use/execution/engine.py:68-80）。native_semantics.py 立宪法："名字只描述数据，没有任何 role 单独授予输入路由；未知 role 保留原名展示"（native_semantics.py:1-5），UNKNOWN 哨兵只存在于 Python 内、绝不进 wire 或展示值（native_semantics.py:7-8）。mcp/ 子目录是 stdio MCP host，工具输出保留 content blocks 与 history metadata（mcp/server.py:1）。

## 三、外部连接

A2UI 接线三面：①integration.py 是对宿主的唯一 API——`build_user_prompt_if_a2ui_event`（非 a2ui.client_event 或未启用返回 None 让宿主原流程继续，integration.py:65-86）、`finalize_assistant_response_if_a2ui`（校验/修复/去 A2UI 重试三连，:89-117）；②渠道闸——`is_a2ui_channel` 只认 "web"（integration.py:28-33），非 Web 渠道完全绕过 A2UI，`apply_non_web_text_fallback_to_payload` 如今是保留旧 Gateway 钩子的直通 no-op（:120-130）；③common 注入点——import 即自注册 `PROVIDER_DOMAIN_A2UI`，common 经 `provider("a2ui")` 反向取用，分层规则 R1（integration.py:170-184）。前端侧 `channels/web/frontend/src/features/a2ui` 渲染。CUA 通过 mcp/ 子目录以 MCP server 形态接入工具生态，另配 backends/ 与 skills/ 资产。**跨层同名 session_input 消歧**：`jiuwenswarm/runtime/session_input.py`（98 行）是**传输无关的 Session 输入意图**——STEER/FOLLOW_UP 两模式、SessionInputRejectedError 表示入 SDK 队列前的已知拒绝，无 SDK/渠道依赖（session_input.py:2-12）；`jiuwenswarm/server/runtime/agent_adapter/session_input.py`（581 行）是 **SDK 适配层**——"补投输入而不启动新一轮 chat turn"。同名的两模块一个定义意图、一个实现落地，读代码时先看 import 路径再判断谈的是哪层。

## 四、数据流

A2UI 出向流：chat 响应流 → stream_guard 分帧 → parser 三级解析（JSONL/裸 JSON/tagged）→ validator 校验 → finalizer：非法时调 repair_call 让模型修复、仍失败可 retry_without_a2ui_call 降级纯文本（integration.py:110-117）→ Web payload 保留原始 A2UI 块给前端渲染器。入向流：前端 UI 事件（表单提交等）打回 `a2ui.client_event` → `build_user_prompt_if_a2ui_event` 把事件翻译成模型 prompt → 进入正常 chat 链（integration.py:83-86）。CUA 流：agent 发起意图（click/typeText/launch…）+ OperationTarget + timeout → Engine 领算 → 校验 → resolve_path 把 ElementPath 解析到实际可达目标 → policy.py 的 choose/route_key 从有限路由计划选路（文本路由优先于指针，有独立文本路由就不动鼠标）→ native port 执行 → ActionResult 带错误码/next 提示（如 retired 时 next='close the old driver and observe a new session'，cua_engine/src/computer_use/execution/engine.py:36-39）。

## 五、设计决策

①**examples 路径悬空（勘误）**：`_examples_dir` 解析到 `jiuwenswarm/server/runtime/resources/a2ui/examples/<version>`（a2ui/protocol.py:50-56，`Path(__file__).resolve().parents[1] / "resources"`），**该 resources 目录在盘上不存在**；`load_examples` 对不存在的目录静默返回空表（a2ui/protocol.py:158-159），于是 build_prompt 的 "### Examples:" 段永远拼不上去（a2ui/protocol.py:151-153）——不崩、不报错，但 v0.8 的 few-shot 示例实为空转，模型只能靠 schema 描述学习输出格式。②**中英混拼 bug（勘误）**：中文指令块 `requested_component_rule_zh` 拼接序列是 template_binding_rule_zh + image_url_rule_zh + **icon_font_rule_en** + unsupported_component_rule_zh + autonomy_rule_zh（prompt_instructions.py:292-297）——全仓只定义了 `icon_font_rule_en`（:210），没有 zh 版，导致中文 A2UI prompt 里嵌着一段英文图标字体规则；英文块则结构不对称（autonomy 在外层另拼，:251,325）。③**恰一键判据**：`is_a2ui_message` 要求四键**恰好命中一个**（a2ui/parser.py:23），多键对象直接不是 A2UI message——防两种消息混拼的畸形输入。④**CUA 的确定性优先**：engine 的模块 docstring 就是设计宣言（cua_engine/src/computer_use/execution/engine.py:1），配合 native_semantics 的"role 不授权"原则，把"模型不确定的 UI 操控"约束成"有限路由计划内的原子执行"。⑤**延迟启动**：Computer 构造不碰驱动，第一次系统调用才拉 native driver（__init__.pyi:51）。

## 六、新人提示

- 调"模型学不会 A2UI 格式"先查 examples 悬空——补齐 `server/runtime/resources/a2ui/examples/v0.8/*.json` 是零代码改动的高杠杆修复。
- 改中文 prompt 注意 icon_font 那段是英文——要么补 zh 版要么接受混拼，别在不知情下继续拼接。
- A2UI 只在 web 渠道生效是刻意的；给其它渠道加 A2UI 支持要动 `is_a2ui_channel` 与 finalizer 的渠道闸两处，不是只改前端。
- 读 CUA 从 `__init__.pyi` 入手（100 行全 API 面），再进 execution/policy.py 看路由选择；engine 的错误 dict 自带 next 建议字段，排障时优先读它。
- grep `session_input` 必看全路径：`runtime/session_input` 是意图枚举，`agent_adapter/session_input` 是 SDK 投递，两者在 agent_ws_server 的调用链上有先后关系但不可互换。

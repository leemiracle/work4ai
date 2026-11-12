# JiuwenSwarm 新人上手指南（ONBOARDING）

> 基于知识图谱（19290 节点/39329 边/16 层/16 步 tour，commit `8827ad7b`）+源码逐锚核实。`path:line` 均已验证。

## 1. 仓库定位与全景

openJiuwen-ai 旗舰开源多智能体 swarm 框架（Apache-2.0，8543★），定位"懂你所想自主演进，蜂群协作完成复杂任务"（README_CN.md:7）——完整 Agent 操作系统而非编排库：渠道、执行内核、Skill 自演进、Designer 编排、CUA 全栈自持。一图流：

- **双顶层包同根部署**：`jiuwenswarm/` 主包+`gateway/` 网关进程包，pyproject.toml:183 include 进同一 wheel；`jiuwenbox/` 沙箱侧车（bwrap/landlock/cgroup/conch 策略全集）。
- **发布名 workswarm ≠ 仓名**（pyproject.toml:6；AGENTS.md:7），v0.2.5.beta1，Python 3.11-3.14。
- **双语 SDK**：sdks/python+typescript 只依赖线协议（sdks/PROTOCOL.md），与 Runtime 彻底隔离（sdks/python/tests/test_client.py:308 有 python -I 硬测试背书）。
- **Skill 资产**：resources/agent/workspace/skills/ 内置 35 个 skill（全仓 53 个 SKILL.md）+人格文件，被 server runtime 反向加载。
- **文档即代码**：.doc_project_maintainer/（455 文件审计签名体系）+.agents/（agent-docs 规约+5 个开发 skill）。

## 2. 架构分层总览

16 层依赖方向 **基础设施→核心引擎→子系统→渠道/前端**，分六带看：

- **L1-L2 基础设施带**（211+232 文件）：交付外壳（根配置/scripts/双语 SDK/jiuwenbox）+common 基础库（utils.py 3318 行、config.py 4444 行配置中枢、schema/ 线协议）。
- **L3-L4 引擎带**（54+449）：runtime 内核（kernel.py:119 ResourceKernel 做 worker 资源 LRU/plan/checkpointer/symphony/cron）+harness（spec.py 声明式 DeepAgentSpec、Rails 干轨、team 的 pyzmq+PostgreSQL、remote_member_bootstrap.py 3134 行）。
- **L5-L6 服务端带**（117+112）：agent_ws_server 枢纽/dispatch 查表/lifecycle 状态机/worker-supervisor；session+KV Cache/skill/mcp/agent_adapter 巨类。
- **L7-L8 生成与增值带**（136+53）：orchestration.py 4539 行 Director/A2UI v0.8/marketplace；agent_warm_pool/debug_trace/harmonyos。
- **L9-L11 资产带**（110+256+477）：video_duplex 插件（79 文件）；CUA SDK+142 backends（Swift/C#）；约 400 个 skill/plugins 资产。
- **L12-L16 接入与治理带**（502+1654+520）：gateway（channel_manager/enterprise/routing/cron）→web 前端（359 组件+476 features）+TUI/浏览器/IDE/desktop/acp→.doc_project_maintainer+.agents。

主链：渠道/前端→gateway→server（L5-8）→runtime/harness（L3-4）→common（L2）。SDK 是旁路。

## 3. 核心链路：一条消息的旅程

以 Web chat 为例（权威叙述 .doc_project_maintainer/project/flows/gateway-agentserver-e2a-chat.md）：

1. **前端**：webClient.ts 的 WebClient 单例（5 次重连/15s 超时/legacy 事件名映射）发请求。
2. **Gateway**：channel_manager 管渠道；gateway/common/mode_matrix.py 把前端三值 mode 组合成 canonical 模式串（work_mode×mode 正交两维）。
3. **跨进程**：WebSocketAgentServerClient 连 AgentServer，ack 后发 E2AEnvelope JSON（真源 openjiuwen_protocol 包）。
4. **AgentServer 收帧**：agent_ws_server.py:1222 的 AgentWebSocketServer（14735 行/264 方法全仓枢纽）逐帧建 task，_handle_message 按 ReqMethod 分发——已搬出的走 dispatch.py:127 HANDLERS 查表，chat 类进 _handle_stream/_handle_unary。
5. **Agent 借出**：AgentManager 按 (channel_id,mode) 管实例，从 agent_warm_pool 预热池借出。
6. **DeepAdapter 执行**：agent_adapter/interface.py:1527 JiuWenSwarm 门面背后，interface_deep.py:1799 的 JiuWenSwarmDeepAdapter（22839 行/535 方法）封装 openjiuwen DeepAgent 全部专属逻辑（模型凭据/KV cache/rails/权限/沙箱/team），调 harness 跑 agent turn。
7. **回包**：session_manager.py:3 任务队列"先进后出，新任务优先"；响应经 E2A wire 在发送锁下推回，chatStore.ts（2408 行最大 store）按 conversationKey 隔离渲染。

枢纽三件：agent_ws_server（协议分发）、AgentManager+DeepAdapter（生命周期）、mode_matrix（模式归一）。

## 4. 关键子系统深潜

**server/runtime 六件**：①session——session_metadata.py（2516 行）+session_history.py（1704 行，legacy JSON+JSONL 游标）+kv_cache/ 双文件所有权设计；②cron——runtime/cron/（etcd_store/dingtalk_routing）；③mcp——registry.py 读内置+Hub 清单暴露 mcp.* RPC；④skill——skill_manager.py:994 SkillManager（12475 行/317 方法）巨型门面；⑤designer——orchestration.py 4539 行 Director、node_agent.py（2269 行）逐节点装 DeepAgent、契约真源 common/schema/designer_graph.py（三方共享）；⑥a2ui——protocol.py v0.8+parser 识别 tagged 块/裸 JSON，agent 输出直接变 UI。

**extensions/video_duplex**：extension.py:41 register_video_live_handler 注册渠道与生命周期；video_voice.py:553 产出 video.transcribe/tts.* handler，video_live.py:678 统一 register_method(local_only=True)——插件挂双端的样本。

**resources skills**：SKILL.md frontmatter+脚本目录；skill_files.py 装载；初始化装进 ~/.jiuwenswarm。

## 5. 进程模型与部署形态

- **一条命令双进程**：jiuwenswarm/app.py:2 钉版 "Orchestrate AgentServer + Gateway in two processes (split layout, one command)"——先拉 server/app_agentserver.py（312 行）再拉 gateway/app_gateway.py（4008 行）。
- **Front/Runtime 拆分**：supervisor/runtime_supervisor.py:3 钉版 "This process does not execute Agent turns"（只监督 Worker）；worker/dispatcher.py:60 分发 IPC 帧；worker/gateway_bridge.py:3 "Virtual Gateway socket. Worker writes land on IPC, never on the Front port"。
- **就绪状态机**：lifecycle.py:12 ReadinessState 八态（STARTING→TRANSPORT_READY→CONTROL_READY→RUNTIME_WARMING→AGENT_READY+DEGRADED/DRAINING/FAILED）。
- **exe 入口路由**：pyproject.toml:158 起 14 个 console scripts（cli/process/app/agentserver/gateway/web/start/stop/init/desktop/acp/acp-chat/jiuwenbox 双件），覆盖桌面一键、pip、源码 uv 三通道。
- **同根部署约束**：gateway 与主包必须同根（源码跑需 PYTHONPATH=.，AGENTS.md:25）；gateway/common/config.py（2828 行）与 paths.py 是母仓裁剪副本、共享同一 config.yaml。
- **jiuwenbox 侧车**：独立沙箱进程，server 经端点调用。

## 6. 扩展与插件机制

**Skill 五路远程安装**：①skillnet 归档（install_skill_sync，skill_manager.py:11311，支持 mirror/sha256）；②teamskillshub；③clawhub；④git clone（skill_manager.py:2614）；⑤管理面预置保护归档。三源搜索排序由 skill_manager.py:340 钉死；marketplace/hub_client.py 对接市场，asset_mcp_publish_converter 支持资产以 MCP 发布。

**skilldev 十阶段=骨架已建、LLM 调用点全是未接线桩**：stages/ init→plan→generate→test_design→test_run→evaluate→improve→desc_optimize→validate→package，但 create_stage_agent 全是"待实现"：evaluate_stage.py:161 grader 被注释、评分恒 pass_rate=0.0（:170）；generate_stage.py:182 产出占位文件；improve_stage.py:112、init_stage.py:87 同款。端到端跑通前别指望它真生成 skill。

**extensions 插件**：video_duplex 样板——extension.py:173 register_extensions 经 registry.register_application_plugin 挂载，自带 frontend Panel。

**ReqMethod 运行时补齐**：common/schema/message.py:27 _ensure_req_method 用 object.__new__ 直写 Enum 私有注册表，pin 35+ 未发布线协议方法（TRAJECTORY_*/SKILLDEV_*/MCP_APP_*），上游发布同名自动让位——但依赖 CPython 实现细节，值冲突即 RuntimeError，升级协议包首查此处。

## 7. 已知地雷与勘误精选（10 条全复核）

1. **三大 god-class≈5 万行**：AgentWebSocketServer 264 方法/14735 行（agent_ws_server.py:1222）、JiuWenSwarmDeepAdapter 535 方法/22839 行（interface_deep.py:1799）、SkillManager 317 方法/12475 行（skill_manager.py:994）——集中式编排风格：改 agent 行为必经，grep 方法名比理解边界快。
2. **skilldev 全是桩**（第 6 节）："Skill 自演进"闭环当前不可用。
3. **delayed-restart-app 双重断链死技能**：launch_delayed_restart.py:27 import jiuwenswarm.paths——模块不存在（真源 common/utils.py:1766）；:35 启动 jiuwenswarm.scripts.delayed_restart_app——scripts/ 只有 3 个 js。一执行就崩。
4. **symbol_fingerprints 悬垂 import**：skills/project-maintainer/scripts/inventory_symbols.py:19 与 audit_integrity.py:20 import 全仓不存在的模块，审计双脚本不可运行。
5. **TEAMATE_MODE typo+双副本陷阱**：server/control/config_service.py:104、common/config_panel/config_set_handlers.py:371、gateway 同名文件 :151 均映射为 "TEAMATE_MODE"（少个 M）——三处一致所以能跑，按正确拼写读的拿空值；根因是 gateway/common/config.py 为母仓裁剪副本，改配置逻辑须双边同步。
6. **designer speech 节点 KeyError**：designer/handlers/__init__.py:130 对 pipeline=="speech" 返回 "speech"，但 :98 NODE_HANDLERS 未注册该键，get_node_handler（:147）必 KeyError。
7. **付费端点硬编码旁路**：skills/advanced-daily-report/analyzers/ai_analyzer.py:107 硬编码 glm-4.7+api/paas/v4；agents/harness/common/tools/video_tools.py:174 默认同端点——绕过 config.yaml 模型资源体系。
8. **opencode_zen 伪装 UA**：opencode_zen.py:64-74 把 User-Agent 伪装成 "opencode" 绕 Zen 免费层限流——上游收紧即断。
9. **SDK/Runtime 两世界**：test_client.py:308 用 python -I 断言 SDK 导入后 sys.modules 无 jiuwenswarm.*/openjiuwen——协议变更必须走 PROTOCOL.md 版本化。
10. **README 链接腐烂**：42 条仓内链接 40 条指向已裁剪的 docs/ 树——找文档看 .doc_project_maintainer/INDEX.md。

## 8. 新人上手路径（tour 16 步 3 天）

**Day 1 地基与内核**（tour-01~05）：README/Makefile/pyproject 建立"双进程+14 入口"心智→.doc_project_maintainer/INDEX.md+.agents/agent-docs/INDEX.md→app.py 启动链→runtime 内核→harness spec+Rails→team（remote_member_bootstrap 略读）。动手：`make init && make start-debug`，发一条消息看全链路日志。

**Day 2 服务端主干**（tour-06~11，核心日）：agent_ws_server 只读 _connection_handler/_handle_message+dispatch 查表→supervisor/worker 拆分→interface.py:1527 门面→agent_adapters.py:25 Protocol→interface_deep 按方法名 grep→session 四件+skill_manager+mcp/registry。动手：在 dispatch.py 加自定义 ReqMethod handler 走通注册-分发-回包。

**Day 3 生成面与接入面**（tour-12~16）：designer 三件+designer_graph.py 契约→a2ui protocol/parser→cua_engine __init__.pyi 存根+execution/engine.py→extensions/video_duplex 样板→gateway/channel_manager+web 前端（App.tsx 5151 行外壳、webClient/chatStore 枢纽）。动手：给 video_duplex handlers 加假 RPC 从前端调通。

**避坑三原则**：①"自演进/skilldev"承诺先看第 7 节勘误；②改 god-class 用 grep 定位小步提交，别重构；③文档以 .doc_project_maintainer/ 为准。

# OpenHands 新人上手文档（ONBOARDING）

> 基于知识图谱（1590 节点 / 4310 边 / 16 层）与 307 条批阶段甄别笔记生成；源码锚定 commit `4dfcd68`（2026-03-15）。行号锚均从源码逐条核实。

## 1. 一句话定位与仓库全景

OpenHands（前身 OpenDevin，约 92k star）是开源自主软件工程 agent 平台：LLM agent 在沙箱里跑命令、改代码、开 PR。产品三形态——Software Agent SDK（引擎）、CLI（已拆独立仓，本仓 `AGENTS.md` 仍引用已不存在的 `openhands/cli/utils.py`，文档滞后实证）、Local GUI（本仓主线：REST API + React SPA）。

总钥匙是事件流架构：决策=Action、反馈=Observation，EventStream 兼发布订阅总线与持久化仓库（`openhands/events/stream.py:43`），步进/回放/审查/成本统计全挂其上。顶层目录：`openhands/` 主包、`frontend/`（V0 SPA）、`openhands-ui/`（组件库）、`skills/`（V1 技能资产）、`enterprise/`（source-available Polyform，图谱裁剪线外）、`dev_config/`（ruff/mypy 工具链）。注意 `openhands/__init__.py` 是 namespace package（pkgutil.extend_path）——让 openhands-sdk / openhands-tools / openhands-agent-server 多分发包共用 `openhands` 包名，V1 拆仓战略的包结构伏笔。

## 2. Legacy-V0→V1 大重构代际（全仓主线）

**读任何文件先问：它属于哪一代？**

- **V0 弃用线**：统一头注释 `# IMPORTANT: LEGACY V0 CODE - Deprecated since 1.0.0, scheduled for removal April 1, 2026`（`openhands/server/app.py:1`），覆盖 server/controller/core 配置/runtime/agenthub/resolver/security。弃用≠死代码：V0 仍是 stable 主线。
- **V1 活跃线**：`openhands/app_server/`（Injector DI 应用服务器）+ 外部仓 software-agent-sdk（`openhands/core/const/guide_url.py:4` 指认）。新功能一律进此。
- **跨代际共享层**（无 V0 头注释）：events / io / storage / memory / microagent / llm。

**双栈物证链**：

1. `openhands/server/app.py:102` 把 v1_router 挂进 V0 app——双代同进程。
2. `openhands/server/routes/conversation.py:42` 的 `_is_v1_conversation` 运行时按 UUID 判代分流；`openhands/server/routes/manage_conversations.py:568` 删除路径同款双栈——同端点服务两代际的兼容层范式。
3. `docker-compose.yml:3` 主容器跑 V0，`:11-12` AGENT_SERVER_IMAGE_* 注入 V1 agent-server 侧车。版本漂移：compose 默认 `1.12.0-python` vs `openhands/app_server/sandbox/sandbox_spec_service.py:16` 钉死 `1.14.0-python`，不同步。
4. `openhands/storage/settings/file_settings_store.py:27` 硬编码 `v1_enabled = True`（V0 退役过渡补丁）。

**术语代际**：`skills/README.md:5` 钉版——同一批 markdown 文件 V0 称 microagents、V1 称 skills；加载位置首选 `.openhands/skills/`、兼容 `.openhands/microagents/`。

## 3. 目录地图与 16 层图谱导览

16 层按"共享底座在下、双线居中、资产在上"排布：L01 仓级配置（pyproject 双锁清单 poetry.lock+uv.lock；`config.template.toml` 与 `openhands/core/config/openhands_config.py` 逐段对应，`[llm]` 命名组多模型分工）→ L02-L04 共享底座（utils/io → events 骨架 → storage，`openhands/storage/__init__.py:15` 的 get_file_store 按字符串分发本地/内存/S3/GCS）→ L05-L06 V1 活跃线（app_server 组合根 + integrations 六平台，V1 最厚一层）→ L07-L09 V0 服务端（server 兼容层三形态 conversation_manager + 12 组 REST 路由；controller 与 mcp；core 配置族，`openhands/core/config/openhands_config.py:29` 的 OpenHandsConfig 是 V0 顶层聚合根：llms/agents 两级命名字典 + sandbox/security/mcp 子配置）→ L10 LLM 抽象（litellm 封装，共享）→ L11-L12 记忆（condenser 家族）与安全（SecurityAnalyzer 闸）→ L13-L14 agenthub（CodeAct + readonly/browsing/visualbrowsing）与 runtime 五实现（Docker/Remote/Local/K8s/CLI）→ L15-L16 resolver 旗舰与 skills 资产（26 个 markdown）。

## 4. 核心链路一：V1 app_server 线

与 V0 全局单例（`openhands/server/shared.py` 模块级副作用装配）相反，**一切经 Injector 注入**：

- **组合根**：`openhands/app_server/config.py:99` 的 AppServerConfig 在 `:109` 起 11 类注入器字段（event/sandbox/sandbox_spec/app_conversation 三件套/user/jwt/httpx/db_session 等），config_from_env 按环境装配；14 处函数体内延迟 import 破循环依赖（全仓惯例）。InjectorState 以 starlette State 为载体支持嵌套复用，端点经 FastAPI Depends 消费。
- **sandbox 即服务**：`openhands/app_server/sandbox/sandbox_service.py:24-26` 的 `OH_SESSION_API_KEYS_0` 等三环境变量是向沙箱注入回调与鉴权的协议；`openhands/app_server/sandbox/process_sandbox_service.py:62` 全局字典 `_processes` 进程注册表（重启即失），`:93` 起 base_port 线性探测 10000 端口。
- **会话域**：`openhands/app_server/app_conversation/live_status_app_conversation_service.py` 1714 行巨石（37 方法），`:103` 内嵌 PLANNING_AGENT_INSTRUCTION 提示词——V1 编排心脏。
- **integrations 六平台门面**（mixin-composition）：`openhands/integrations/provider.py:131` service_class_map 字典工厂（provider_tokens 强制 MappingProxyType 只读）；`openhands/integrations/github/github_service.py:21` 五 mixin 组装，`:75` 环境变量可替换实现类，`:95` `__getattr__` 惰性代理。
- **持久化**：`app_lifespan/alembic/` 迁移随 lifespan 执行，`%(here)s` 使一份 ini 适配 SQLite 与 PG。

## 5. 核心链路二：V0 事件流线

执行链=事件流为骨架、会话为容器、controller 为心跳、runtime 为手脚。

- **事件契约**：`openhands/events/action/files.py:62` FileEditAction 单 dataclass 承载两套互斥参数集；`openhands/events/action/message.py:23` `images_urls` 是 `image_urls` 废弃别名。EventStream 线程模型=每订阅者独立事件循环+队列。
- **会话五步**：`openhands/server/session/agent_session.py:98` `start()`——`:143` _create_runtime → 令牌注入 → `:164` _create_memory → `:435` AgentController → `:176` add_mcp_tools_to_agent。
- **controller 心跳**：`openhands/controller/agent_controller.py:112` 巨石 1392 行 36 方法，`:379` step() 异步驱动、`:413` should_step 按事件源判定；卡死检测 `openhands/controller/stuck.py:28` StuckDetector（`:154` _eq_no_pid 忽略进程号噪声）。
- **主力 agent**：`openhands/agenthub/codeact_agent/codeact_agent.py:57` CodeActAgent（arXiv:2402.01030；`openhands/resolver/issue_resolver.py:56` 硬编码 AGENT_CLASS）；`function_calling.py:80` response_to_actions（266 行）是 LLM 输出→Action 唯一咽喉。
- **LLM 封装**：`openhands/llm/llm.py:64` `class LLM(RetryMixin, DebugMixin)` 874 行；`openhands/llm/metrics.py:54` Metrics 成本核算；`openhands/llm/llm_registry.py:30` 命名模型与规则路由（`:118` get_router）。
- **runtime 落地**：`openhands/runtime/impl/docker/docker_runtime.py:82` 转发进容器，`openhands/runtime/action_execution_server.py:173` ActionExecutor（485 行 19 方法）统一执行 bash/ipython/编辑/浏览器；`openhands/runtime/impl/local/local_runtime.py:76` `_WARM_SERVERS` 预热机制。

## 6. 记忆与上下文

- **Memory 门面**：`openhands/memory/memory.py:42`；`:34` GLOBAL_MICROAGENTS_DIR 指向仓内 `openhands/skills/`，用户目录 `~/.openhands/microagents/`——目录名是代际活化石。
- **condenser 家族**：`openhands/memory/condenser/condenser.py:44` `Condenser(ABC)` 与 `:169` RollingCondenser；`impl/` 恰 10 实现（conversation_window 双游标双口径 / llm_summarizing / llm_attention / structured_summary / amortized_forgetting / observation_masking / browser_output / recent_events / pipeline / no_op）。`dev_config/python/mypy.ini` 专为 `impl/*` 开 override 豁免——签名变体系刻意。
- **转换**：`openhands/memory/conversation_memory.py` 898 行单类 12 方法承载事件→消息转换（V0/V1 共享）；压缩经 events/action/agent.py 的 CondensationAction 表达（ID 列表与区间 XOR 互斥多态）。
- **双资产**：`openhands/microagent/microagent.py:52` load 解析 frontmatter（knowledge/repo/task 三类）；`openhands/microagent/types.py:26` MicroagentMetadata 与 `skills/*.md` 字段一一对应。同名异物：resolver 的 `prompts/repo_instructions/` 目录与 microagent 机制无关。

## 7. 安全与隐私（10 处发现精选）

1. **feedback 轨迹外传**：`openhands/server/routes/feedback.py:56` 收全轨迹，`openhands/server/data_models/feedback.py:44` httpx.post 直发 `:29` 硬编码 `share-od-trajectory-...gateway.dev`——点反馈即全对话出境。
2. **secrets.json 明文**：`openhands/storage/secrets/file_secrets_store.py:35` 以 `expose_secrets: True` 绕掩码序列化真实令牌。
3. **InvariantAnalyzer 自动拉容器**：`openhands/security/invariant/analyzer.py:28` 钉 `ghcr.io/invariantlabs-ai/server` 镜像，`:64` 容器不在即自动拉起——启用分析器=隐式供应链拉取；无 Docker 直接抛异常。
4. **MCP key 三头注入**：`openhands/mcp/client.py:75-77` 同一 api_key 进 Authorization/s/X-Session-API-Key 三请求头。
5. **沙箱双空密码**：`openhands/runtime/utils/runtime_templates/Dockerfile.j2:88` NOPASSWD:ALL，`:90`/`:92` openhands 与 root 双双 `passwd -d`，`:94` 改 PAM——镜像内提权零阻力。
6. **技能教 agent 拼 token**：`skills/github.md:20` 指导 `git remote set-url origin https://${GITHUB_TOKEN}@...`，令牌入 history/config。
7. **docker.sock 直挂**：`docker-compose.yml:23` 容器内可控制宿主 Docker。
8. **VSCode 扩展 XSS 面**：`openhands/runtime/utils/vscode-extensions/memory-monitor/memory_monitor.js` 把进程命令行未转义插值进 enableScripts:true 的 webview，chart.js 走公网 jsdelivr。
9. **grayswan 硬编码默认策略 ID** + 双认证头，依赖外部 SaaS。
10. **宽容限流**：`openhands/server/middleware.py:107` 超限 2 倍内 sleep 放行，超 2 倍才 429。

附 latent bug 与死资产：`openhands/mcp/utils.py:299` Windows 裸 return 与签名 `-> MCPConfig` 不符；`openhands/security/invariant/policies.py:8` DEFAULT_INVARIANT_POLICY 全仓零消费者；`openhands/integrations/templates/resolver/linear/linear_instructions.j2:1` 首句照抄 Jira——双份维护拷贝事故。

## 8. 新人路线图与上手禁忌

**16 步导览精编七站**：

1. 双栈鸟瞰：README → `docker-compose.yml` → `openhands/events/stream.py` → `openhands/storage/__init__.py:15`（事件流+外置状态世界观）。
2. V1 钥匙：`openhands/app_server/config.py` → app_conversation → SandboxService → `openhands/integrations/provider.py:131` 与 github_service（DI 四件套）。
3. V0 主线：`openhands/server/session/agent_session.py` 五步 → `openhands/controller/agent_controller.py` 心跳 → core/main.py 的 run_controller（headless 调试首选）。
4. 配置与模型：`openhands/core/config/openhands_config.py:29` 对照 config.template.toml → `openhands/llm/llm.py` → fn_call_converter.py（979 行双向转换）。
5. 记忆与安全：condenser 十实现 → `openhands/security/invariant/analyzer.py`。
6. agent 与执行：codeact_agent 的 tools/ → readonly_agent（`openhands/agenthub/readonly_agent/tools/glob.py:14` 提示词与 Claude Code 高度同源）→ `openhands/runtime/impl/docker/`。
7. 旗舰收尾：`openhands/resolver/issue_resolver.py:89` 五平台 token 回退链 → patching/patch.py（35 条方言正则 diff 引擎）→ `skills/` 资产。

**上手禁忌**：

- **`.env.zhipu`（仓根 367 字节）是用户本地凭据残留，勿读勿改勿删**。
- **原仓只读**：禁编译/运行/安装（make build 渲染 Dockerfile.j2 建镜像；install 改锁文件）。
- **enterprise/** source-available（Polyform）且属图谱裁剪线外，分析以 `openhands/` 主包为准。
- **勿扩 V0 文件**（头注释明示 avoid extending），新代码进 app_server/ 或 SDK。
- **双份维护陷阱**：github/gitlab 方法一一对应、Bitbucket Cloud/DC 两形态、Jira/Linear 模板互拷——单点修改必查孪生。
- **agent-server 镜像版本两处声明**（compose 与 `openhands/app_server/sandbox/sandbox_spec_service.py:16`）需同步。
- **Windows 宿主 MCP 整体禁用**（`openhands/mcp/utils.py:299`）。

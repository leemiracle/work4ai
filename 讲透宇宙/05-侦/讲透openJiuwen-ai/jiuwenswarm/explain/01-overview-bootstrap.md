# 01 全景与双进程启动链路（tour S01+S02）

## 一、角色定位

JiuWenSwarm 是 openJiuwen-ai 的旗舰多智能体框架，README.md:6 的一句话定位是 "Understands Your Intent, Evolves Autonomously — Swarm Collaboration for Complex Tasks"（意图理解 × 自主演进 × 蜂群协作）。产品能力矩阵在 README.md:42-50 展开：多智能体协作（Leader 分解任务组装团队）、分布式蜂群（Leader 与 Teammates 跨进程跨机部署）、Swarmflow 确定性多阶段工作流（README.md:47，含 HITL 与 token 预算）、Skill 自演进、技能市场共享、Auto Harness 与工具权限安全。

本篇讲两条入口链路。第一条是"部署形态"入口：`jiuwenswarm/app.py` 用一条命令拉起 AgentServer + Gateway 双进程（split layout）。第二条是"运维 CLI"入口：`jiuwenswarm/start_services.py` 提供实例化的启动/列表/停止/重启。两个独立进程各自的 main 在 `jiuwenswarm/server/app_agentserver.py` 与 `gateway/app_gateway.py`。要理解这个仓库，先要记住一条主线：**Gateway 是渠道与路由层，AgentServer 是 agent 执行层，两者只通过 WebSocket 对话**。

构建全貌看两个文件：`Makefile` 与 `pyproject.toml`。pyproject.toml:158-173 的 `[project.scripts]` 注册了 14 个命令行入口（jiuwenswarm / jiuwenswarm-process / jiuwenswarm-app / jiuwenswarm-agentserver / jiuwenswarm-gateway / jiuwenswarm-web / jiuwenswarm-start / jiuwenswarm-stop / jiuwenswarm-init / jiuwenswarm-desktop / jiuwenswarm-acp / jiuwenswarm-acp-chat / jiuwenbox / jiuwenbox-server），每个入口对应一个进程形态或运维动作。Makefile:48 的 `install` 走 uv editable 安装，Makefile:104-122 提供 `start-debug` / `restart-debug` / `stop` 的开发循环包装。

## 二、内部结构

### app.py：进程编排入口（125 行小文件，职责极克制）

app.py:15-16 在**任何 jiuwenswarm 模块导入之前**先调 `parse_dotenv_early("jiuwenswarm-app")`——dotenv 早解析是多实例隔离的第一环：`--dotenv <path>` 让同名机器上并存多套实例。随后 app.py:35-41 依次做陈旧 openjiuwen 描述符清理（`cleanup_stale_openjiuwen_descs`）、运行时工作区准备（`prepare_runtime_workspace`）、env 加载与媒体能力开关迁移。

`main()` 里三个细节值得逐个看：

1. **SIGTERM 路由**（app.py:64-73）：注释写得很清楚——Python 默认 SIGTERM 直接杀进程，`supervise()` 的 `finally` 清理不会执行，AgentServer/Gateway 子进程会变成占着端口的孤儿。Ctrl-C 从不暴露这个 bug，因为 SIGINT 会送达整个前台进程组。所以 app.py:73 把 SIGTERM 改接 `signal.default_int_handler`，让"按 PID 停进程"（如 `jiuwenswarm-start --stop`）与 Ctrl-C 走同一条优雅关闭路径。
2. **PyInstaller frozen 分支**（app.py:88-93）：桌面打包模式下 `-m` 模块启动不可用，改用 `--desktop-run-agent` / `--desktop-run-gateway` 两个 flag 启动同一份可执行文件；源码模式则是 `[python, "-m", "jiuwenswarm.server.app_agentserver"]` 与 `[python, "-m", "gateway.app_gateway"]`。
3. **进程组隔离**（app.py:115-119）：非 Windows 下每个子进程 `start_new_session=True`，各自拥有独立进程组——这样某个子进程崩溃重生时可以 `killpg` 清掉它遗留的后代，而 Ctrl-C/SIGTERM 仍经由 supervisor 的 handler 统一拆除。app.py:121 最后 `raise SystemExit(supervise({...}))` 把双进程监督交给 `common/process_supervision`。

### start_services.py：实例管理 CLI（1183 行）

start_services.py:14-17 说明 debug 模式是开发者捷径：`npm install` + `npm run build` + `uv sync` 后台式启动，日志重定向到 `logs/swarm-<timestamp>.log`。核心结构：

- **端口冲突向上扫描**（start_services.py:229-251）：`_resolve_ports_with_fallback` 从实例自身 index 向上扫 10 组端口，成功后**持久化**——命名实例写回 `instances.yaml` + bootstrap .env，默认实例写 `~/.jiuwenswarm/config/.env`（app.py:39 会以 `override=True` 加载）。注意 start_services.py:272-274 的 `exclude_ports`：回退端口组永不与其它运行中实例静默碰撞。
- **PID 文件 schema v2**（start_services.py:436-441 写入，start_services.py:516-523 结构）：记录 launcher 的 pid/create_time/pgid/sid 与每个子进程的 witnesses（pid、create_time、module、dotenv 路径）。出生时间 + 见证人列表是防 PID 复用的经典组合——PID 被系统回收后复用是进程管理的头号误杀来源。start_services.py:461-465 用 psutil 取 launcher 出生时间。
- **四条运维子命令**：start_services.py:1064-1079 注册 `--list` / `--status` / `--stop` / `--restart`。
- **命令组装**（start_services.py:526-563）：mode `all/app/web/dev` 决定拉起哪些子命令；dev 模式（start_services.py:550-561）在包安装下若无 frontend package.json 会直接 RuntimeError。

### app_agentserver.py：AgentServer 进程入口（312 行）

docstring（app_agentserver.py:2-12）一句话讲透架构：**Front 先监听 WebSocket，Runtime Supervisor 再经本地 IPC 附着常驻 Worker；OpenJiuwen 与 Agent Runtime 在那个 Worker 里加载，不在本进程**。这就是后面第 05 篇要展开的 Front/Worker 拆分。本篇先记三个锚：

- app_agentserver.py:24-25 的 `_STARTUP_IMPORT_PHASES` 启动阶段打点，配合 （app_agentserver.py:100-111） 的阶段日志输出——冻结 EXE 排查启动超时的对齐手段，Gateway 侧同款（app_gateway.py:34-39）。
- app_agentserver.py:53-78 `_start_supervisor`：构造 `RuntimeSupervisor`、`attach_runtime_backend` 附着到 Front、`run_until_ipc_ready()` 等待 Worker IPC 就绪；`AGENT_READY` 更晚会从 IPC readiness 流到达，而控制面请求 Front 已能服务。
- app_agentserver.py:177-186 关闭路径的注释 "Detach only. The Worker keeps its loaded Runtime for the next Front"——Front 退出只 detach，Worker 保留已加载的 Runtime 等下一个 Front。这是**常驻模型伏笔**：重启 Front 不必重付模型加载成本。
- app_agentserver.py:220-258 `_resolve_bind_host` 兼顾沙箱一体机：`AGENT_SERVER_HOST` 显式指定优先；处于 jiuwenbox 沙箱管控（`JIUWENBOX_LISTEN` 存在）时读 `SANDBOX_IP` 快照或 UDP connect 探测 veth 地址；单机默认 127.0.0.1。端口默认 18092（app_agentserver.py:298-304）。
- app_agentserver.py:81-91 `_install_common_providers` 是个实坑：Front 控制面直接处理 config.*，但 a2ui/team/mcp_credential 域不经功能路径自然加载——不装配则 config.get 静默回退默认值、团队模板保存失败、MCP 凭证占位符不解析。

### app_gateway.py：Gateway 进程入口（4008 行）

app_gateway.py:4-13 列出本进程职责：MessageHandler + ChannelManager、WebChannel WebSocket 服务器（浏览器入站）、heartbeat 心跳、cron 调度（经 ws 触发远端 AgentServer），并连接远端/本地 AgentServer WebSocket 端点。结构要点：

- `_run` 主循环从 app_gateway.py:1884 开始，函数体内大量惰性 import——app_gateway.py:1888-1892 注释明说 IM 平台（dingtalk/feishu/whatsapp/wechat/xiaoyi/telegram/discord/slack/wecom）只在对应 channel enabled 分支内导入，避免冷启动为禁用平台读重依赖（slack_bolt/telegram/redis 等）。
- app_gateway.py:466-478 `_connect_with_retry`：连 AgentServer 前先做轻量 TCP 端口探测，端口通了才走 WS 握手；重试指数退避从 0.2s 起翻倍。app_gateway.py:493-501 对桌面场景特判——本机 AgentServer 用 0.05s 起步、0.25s 封顶、最多 240 次的快节奏，因为 Desktop 总是连它刚 spawn 的 loopback AgentServer。
- app_gateway.py:62 `_SAFE_USER_ID_RE` 白名单正则，只允许字母数字与 `_-`，拒绝路径遍历——Gateway 是对外面，入口处的卫生检查。
- app_gateway.py:592 `_exec_gateway_restart` 与 GATEWAY_RESTART_EXIT_CODE（app_gateway.py:110-113 导入）支持进程监督下的 exec 式自重启。

## 三、外部连接

启动链路的上下游关系可以串成一条线：

- `Makefile:104` start-debug → `jiuwenswarm-start`（start_services.py:158 附近的 pyproject 入口 `jiuwenswarm.start_services:main`）→ mode 决定 → app.py supervise() → 两个子进程。
- AgentServer（app_agentserver.py）内部分两层：Front（`server/front/server.py` 的 AgentServerFront，:113 实例化）+ RuntimeSupervisor（:59 导入）附着的常驻 Worker。Gateway 连的是 Front 的 WS 端口（默认 18092）。
- Gateway（app_gateway.py）反向依赖 `gateway/channel_manager/*`（渠道管理）、`gateway/cron`、`gateway/heartbeat`、`gateway/routing`（路由绑定），以及 `openjiuwen_protocol` 的 Message/ReqMethod 消息协议（app_gateway.py:41-49）。
- 上游 SDK 是 openjiuwen DeepAgent（`_mark_startup_import_phase("openjiuwen_and_channel_base_imported")`，app_gateway.py:93），它只在 AgentServer 的 Worker 进程里加载，Gateway 进程完全不碰。
- 桌面形态（`jiuwenswarm-desktop`）与 CLI 形态（`jiuwenswarm` / `jiuwenswarm-process`）复用同一对进程入口；PyInstaller 打包走 app.py:88-93 的 flag 分支。

## 四、数据流

以一次 `jiuwenswarm-start` 为例：

1. start_services.py:33 早解析 dotenv → `_build_commands`（start_services.py:526）产出 `[python, -m, jiuwenswarm.app]`（mode=all/app/dev）与可选的 web 进程。
2. 端口冲突时 `_resolve_ports_with_fallback`（start_services.py:229）扫描替代端口组并持久化到实例配置。
3. `_run_instance_with_pid`（start_services.py:414-452）：逐个 `_start_process`，写 PID schema v2（start_services.py:436-441），`_wait_for_services_ready`（start_services.py:688）等就绪，然后 0.5s 轮询 `proc.poll()` 直到任一子进程退出。
4. app.py 进程内：模块导入期完成 workspace 准备（app.py:35-41），main() 里组装双进程命令与 Popen kwargs（app.py:108-121），`supervise()` 接管监督循环。
5. AgentServer 子进程：`_run`（app_agentserver.py:94）→ Front 监听（app_agentserver.py:118）→ 异步 task 拉起 supervisor（app_agentserver.py:137-140）→ Worker 加载 OpenJiuwen Runtime → `AGENT_READY`。
6. Gateway 子进程：`_run`（app_gateway.py:1884）→ 扩展加载 → 渠道装配 → `_connect_with_retry`（app_gateway.py:466）连上 AgentServer → 消息开始在 Gateway↔AgentServer 的 WebSocket 上流动。
7. 关闭：SIGTERM/SIGINT → 双方的优雅拆除路径（app.py:73 路由；app_agentserver.py:154-195 信号 handler + drain + detach-only）。

## 五、设计决策

1. **split layout 双进程而非单体**：渠道接入（IM/Web/桌面）与 agent 执行彻底分离，Gateway 可以和 AgentServer 不在一台机器上（"connects to a remote/local AgentServer"，app_gateway.py:10）。代价是两个进程各有一套启动打点与 dotenv 早解析（app.py:16 / app_agentserver.py:33 / app_gateway.py:66 / start_services.py:33 四处重复出现，是有意的复制而非疏漏——dotenv 必须在任何仓内 import 之前完成）。
2. **Front 先听端口、Runtime 后附着**：可用性优先——控制面（config.*）秒级可用，重的 OpenJiuwen Runtime 在 Worker 里慢慢加载。配合 lifecycle 8 态就绪状态机（详见 05 篇），执行请求可以排队等待。
3. **Worker 常驻、Front 可换**（app_agentserver.py:183）：模型加载是分钟级成本，Front 崩溃重启不拖累 Worker，这是把"重启代价"从全进程压缩到薄前端的取舍。
4. **PID schema v2 + witnesses**：外部 launcher 可能 `setsid` 脱管，PID 文件记录出生时间与子进程见证人（start_services.py:468-523），`--stop` 时多证据交叉验证，防 PID 复用误杀。
5. **god-class 风格的集中式编排**：本仓入口层刻意保持薄（app.py 仅 125 行），但把编排职责集中到后续的巨物文件（agent_ws_server.py 1.47 万行、interface_deep.py 2.09 万行）——这是全仓一以贯之的编排层风格，后续各篇会反复见到。

## 六、新人提示

- 读代码顺序建议：README.md:42-50 能力矩阵 → pyproject.toml:158 入口表 → app.py 全文（125 行，半小时）→ app_agentserver.py:94-195（_run 主流程）→ app_gateway.py 只看 docstring 与 `_connect_with_retry`，1983 行的 `_run` 留到需要时再钻。
- 排查"起不来"先看启动阶段日志：两进程都有 `startup stage=... process_elapsed=...` 打点（app_agentserver.py:100-111 / app_gateway.py:1931-1946），卡在哪个 stage 一目了然。
- 多实例实验用 `--name` + instances.yaml，别手动改端口环境变量——端口扫描回退逻辑（start_services.py:229）会自动持久化，手动改容易和已持久化的配置打架。
- config.get 返回默认值、团队模板存不上、MCP 凭证不解析，先查 app_agentserver.py:81-91 的 provider 装配是否执行——这是已钉版的静默失败模式。
- 改启动行为时牢记：dotenv 早解析必须在所有 jiuwenswarm/gateway import 之前（app.py:15-18 的注释 "Now safe to import"），顺序错了多实例隔离就失效。

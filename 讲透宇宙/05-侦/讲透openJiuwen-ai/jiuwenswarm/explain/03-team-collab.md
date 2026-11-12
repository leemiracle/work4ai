# 03 Team 多智能体协作（tour S05）

## 一、角色定位

Team 子系统是"蜂群协作"（Swarm Collaboration）的载体。Leader 智能体分解复杂任务、组装团队，成员各自专业化并动态协商（README.md:42-43 的能力承诺）。本篇覆盖四个文件：`team/__init__.py`（惰性门面）、`config_loader.py`（配置装载）、`distributed_runtime.py`（分布式判定与 PG 编排）、`remote_member_bootstrap.py`（3134 行的远端成员 bootstrap 协议层），加上 server 侧的 `team_binding_store.py`（团队实体的持久绑定）。

一条理解主线：**Team 的"配置面"与"运行面"分离**。config_loader 把 modes.team 模板 + models.defaults 解析成 TeamAgentSpec 兼容 dict；真正的运行时编排（TeamManager、spawn、消息传递）在 openjiuwen agent_teams 与 team_manager.py；而 jiuwenswarm 在两者之间补齐了分布式部署、远端空白成员拉起、模板持久化这三个产品化缺口。

## 二、内部结构

### team/__init__.py：单层 __getattr__ 惰性门面（113 行）

17 个公开符号（__init__.py:13-30）全部经模块级 `__getattr__`（__init__.py:32）按需 re-export，分四组：config_loader 三函数（team/__init__.py:33-46）、TeamManager 及八个跨管理器操作（team/__init__.py:47-74）、team_name_generator（team/__init__.py:75-83）、双 monitor handler（team/__init__.py:84-99）。好处写在 docstring（__init__.py:7-8）：`team.expert_org` 等子包可先行导入而不拉 TeamManager 依赖链。未知属性显式 `raise AttributeError`（__init__.py:107）——不给静默 None 留机会。

### config_loader.py：模板到 Spec 的完整装配线（657 行）

入口 `load_team_spec_dict`（config_loader.py:557-657）接受 template_snapshot（快照优先，config_loader.py:576-583）或 template_id 选择（config_loader.py:584-589），然后装配出一个 TeamAgentSpec 兼容 dict。值得逐条看的字段：

- **生命周期与模式族**：lifecycle 默认 persistent（config_loader.py:606）、teammate_mode 默认 build_mode（config_loader.py:607）、spawn_mode 默认 inprocess（config_loader.py:608）、dispatch_mode 默认 autonomous（config_loader.py:609）。bootstrap_mode 默认 "leader"（config_loader.py:613）——注释标明 F_122：谁物化团队，leader 经 build_team 还是框架直接启动。
- **模型回退链**是本文件最精细的部分：`_select_default_model_config`（config_loader.py:132-186）按序尝试——显式 model 名匹配（config_loader.py:156-158，含 agentos 的 `name#index` 占位符定位 config_loader.py:144-151）→ 请求级 login_model_entry（config_loader.py:160-166，登录授予的模型是请求作用域、绝不写回 models.defaults）→ Zen 免费模型内存缓存（config_loader.py:168-174）→ 列表首项（config_loader.py:183-184）。`_sanitize_team_member_model`（config_loader.py:203-232）把内部 reasoning_level 映射到 provider 中立的请求 kwargs。
- **swarmflow 预算**：`_apply_swarmflow_budget`（config_loader.py:530-554）只接受正数值，非法值弹警告并移除键；`swarmflow_progressive_tool` 改名为 spec 侧的 `progressive_tool`（config_loader.py:624-629）。
- **其余组件**：`_build_agents_config`（config_loader.py:367）、`_build_workspace_spec`（config_loader.py:450）、`_build_transport_spec`（config_loader.py:463）、`_build_leader_spec`（config_loader.py:473）、`_build_predefined_members`（config_loader.py:488）、`_resolve_storage_config`（config_loader.py:320）与 sqlite 路径解析（config_loader.py:91）。`_prepare_external_cli_agents`（config_loader.py:33）负责外部 CLI agent 准备。

### distributed_runtime.py：分布式判定与 PG 自愈（412 行）

- 判定层：`is_distributed_mode`（distributed_runtime.py:20）、`runtime_role`（distributed_runtime.py:31）、`normalize_distributed_transport_fields`（distributed_runtime.py:74）负责 leader/follower 角色与 transport 字段归一。
- **依赖缺失降级**：`missing_distributed_dependencies`（distributed_runtime.py:160-172）检查 pyzmq 与（PG 存储时的）asyncpg；`fallback_distributed_to_local`（distributed_runtime.py:175-220）深拷贝配置后把 runtime.mode 改 local、transport.type 改 inprocess、PG 存储降级为 sqlite team.db——分布式部署失败时团队仍能以本进程模式跑起来。
- **PG 自愈**：`ensure_postgresql_for_leader`（distributed_runtime.py:319-412）只对 leader + PG 存储生效（distributed_runtime.py:329-337）。PG 不可达时先 `try_start_pg_cluster`（distributed_runtime.py:349-351），失败再依次试 systemctl/service（distributed_runtime.py:353-360）；启动命令成功后指数退避等就绪（0.4s 起、1.45 倍增、2s 封顶、最长 30s，distributed_runtime.py:375-405）。`extract_pg_endpoint`（distributed_runtime.py:223-235）兼容 sqlalchemy 风格 URL（postgresql+asyncpg:// 拆出 host/port）。

### remote_member_bootstrap.py：远端成员协议层（3134 行）

docstring（remote_member_bootstrap.py:3-13）讲清机制：leader LLM 调 `spawn_teammate` 时，对 `team.metadata.jiuwen_remote_member_names` 列出的成员（或 `jiuwen_remote_all_spawn_members` 为真时的全部成员），**DB 插入成功后**经 ZMQ 直发 bootstrap envelope，让远端已注册的"空白爪子"（blank claw）应用运行时提示（transport 拓扑、leader id 等）。安全约束明写在 （remote_member_bootstrap.py:11-12）：**载荷刻意不含 DB 凭据，只镜像 pyzmq 协调已共享的 messager 字段**。

关键构件：

- 三类直发事件类型（remote_member_bootstrap.py:56-59）：remote_teammate_bootstrap.direct / remote_team_destroy.direct / remote_member_shutdown.direct；回执走普通 P2P 消息 `jiuwen.remote_bootstrap_ack`。
- **两阶段 spawn**：`precheck_and_reserve_remote_spawn`（remote_member_bootstrap.py:482-525）在 spawn_teammate 改动团队 DB **之前**做 fail-fast 校验并预留空白成员（A2X registry 的 `reserve_blank_teammate_agent`，remote_member_bootstrap.py:505-510）——重名（remote_member_bootstrap.py:493-497）、预留失败、无可用空白成员三种错误都提前返回。
- `build_bootstrap_envelope`（remote_member_bootstrap.py:632-670）：type/version/bootstrap_id/team_name/session_id/member_name/leader 三元组（agent_id + member_name + direct_addr）+ messager dict + prompt，再叠加 `_swarm_assembly_hint`（remote_member_bootstrap.py:593）让远端 teammate 以相同请求模式/项目目录重建。
- 地址卫生：`_normalize_leader_direct_addr`（remote_member_bootstrap.py:538-543 起的注释）——direct_addr 常被配置成 bind 地址 0.0.0.0，对端必须拨真实 host，归一化在此完成；`_normalize_leader_agent_id`（remote_member_bootstrap.py:528-535）给空 id 兜底成 `{team}_{leader}` 稳定形式。
- `build_team_destroy_envelope`（remote_member_bootstrap.py:673-712）携带 registry 预留信息（dataset/service_id/endpoint）供拆队清理；`_apply_leader_route_from_envelope`（remote_member_bootstrap.py:715）在空白 teammate 侧做 best-effort 动态路由注册，保证"空白成员能回话给 leader"。
- 全文的包装模式用属性打标防重复包装（remote_member_bootstrap.py:32-48 一排 `_WRAPPED_*_ATTR`），shutdown 清理有 20s 超时 + 0.25s 轮询（remote_member_bootstrap.py:52-53）。

### team_binding_store.py：团队实体持久化（394 行）

docstring（team_binding_store.py:1-5）声明设计边界：**刻意小而本地文件化**——只记录稳定的用户面团队实体名与构造运行时 spec 所用的模板；运行时状态在别处派生、不在此持久化。TeamBinding（team_binding_store.py:36-48）是 frozen dataclass：team_name/template_id/session_ids/last_session_id/template_snapshot/model_selection。注释（team_binding_store.py:44-46）点明 model_selection 是业务级模型选择，运行时模型池仍在 spec/checkpoint 里、每次冷构建重新解析。TeamBindingStore（team_binding_store.py:124）提供 create（team_binding_store.py:164）/bind_session（team_binding_store.py:194）/unbind_session（team_binding_store.py:281）/delete（team_binding_store.py:314），文件锁下读写（_read_unlocked team_binding_store.py:326/_write_unlocked team_binding_store.py:350），团队名校验 TEAM_NAME_RE 拒绝路径字符（team_binding_store.py:23、team_binding_store.py:112）。`get_team_binding_store`（team_binding_store.py:371）进程单例。

## 三、外部连接

- config_loader 上游消费 `modes.team` 配置与 models.defaults（经 common/config），下游产出被 openjiuwen agent_teams 的 TeamManager 与 team_manager.py（经 __init__.py 惰性导出）消费。
- distributed_runtime 的 `ensure_postgresql_for_leader` 由 TeamManager 启动路径调用；PG 连接串与 storage.params 约定对齐。
- remote_member_bootstrap 包装的 spawn_teammate 是 openjiuwen 团队原语；A2X registry（a2x/a2x_registry_runtime）提供空白 teammate 预留。它同时被 server/handlers/team.py 与 agent_ws_server.py 引用（TeamBindingStore 的两个消费方）。
- TeamBindingStore 挂在 server/runtime/ 下，被 session_provisioner.py 用于会话与团队的绑定解析——前端"这个会话属于哪个团队"由它回答。

## 四、数据流

分布式团队一次冷启动：

1. 前端选模板与模型 → server 层 `load_team_spec_dict`（config_loader.py:557）解析出 spec dict（成员模型按回退链兜底）。
2. TeamManager 启动：`is_distributed_mode` 判真 → `missing_distributed_dependencies` 查依赖，缺失则 `fallback_distributed_to_local` 降级（distributed_runtime.py:175）；PG 存储则 `ensure_postgresql_for_leader`（distributed_runtime.py:319）探测/拉起/等就绪。
3. leader 运行中调 `spawn_teammate`：包装层先 `precheck_and_reserve_remote_spawn`（remote_member_bootstrap.py:482）重名校验 + A2X 预留 → 原始 spawn 完成 DB 插入 → `build_bootstrap_envelope`（remote_member_bootstrap.py:632）组包 → ZMQ 直发到空白 teammate。
4. 远端 teammate daemon 消费 envelope：`_apply_leader_route_from_envelope`（remote_member_bootstrap.py:715）注册回话路由 → 按 swarm assembly hint 以同模式重建 provider → 进入团队消息环。
5. teammate 就绪后回 `jiuwen.remote_bootstrap_ack`；拆队时 leader 直发 destroy envelope（remote_member_bootstrap.py:673），成员侧 20s 超时内完成清理。
6. 会话侧：TeamBindingStore.bind_session（team_binding_store.py:194）把会话钉到团队实体；模型选择存 model_selection、冷构建时重新解析成当时的有效模型条目。

## 五、设计决策

1. **回退链而非硬失败**（config_loader.py:132-186 与 distributed_runtime.py:175-220 一致哲学）：成员模型缺显式配置 → 页面选择 → 登录模型 → 免费模型 → 首项；分布式依赖缺失 → 降级 local。产品化 agent 框架的可用性优先取向——但要注意这也会把"配置错了"掩盖成"用了别的模型"。
2. **登录模型不落盘**（config_loader.py:160-166 注释）：请求作用域的凭据模型绝不写回 models.defaults，避免临时授权变成持久配置——安全与可预期性的双重要求。
3. **预留在先、变更在后**（remote_member_bootstrap.py:488）：A2X 预留发生在 spawn_teammate 改 DB 之前，失败路径不留半成品团队状态。
4. **bootstrap 载荷最小化**（remote_member_bootstrap.py:11-12）：只传协调必需的 messager 字段，DB 凭据永不进 envelope——远端成员自己去取需要的东西，攻击面收敛。
5. **TeamBindingStore 拒绝膨胀**（team_binding_store.py:1-5）：明确"只存实体与模板、不存运行时状态"，394 行的自我克制是全仓少见的反 god-class 样本。
6. **单层 __getattr__ 门面**（__init__.py:32-107）：用 Python 3.7+ 模块级 __getattr__ 做依赖隔离，比传统 import * 干净且可静态分析。

## 六、新人提示

- 改团队行为先分清三层：模板字段语义在 config_loader.py:605-644（默认值表）；编排行为在 openjiuwen agent_teams 与 team_manager.py；**分布式协议在 remote_member_bootstrap.py**。搜索"团队为什么不 XX"时先确认落在哪层。
- 模型回退链的坑：用户说"我明明选了模型 A 团队却用了 B"——九成是 `_select_default_model_config` 的回退命中了别名/同名项（config_loader.py:156-158 的 alias 分支），查日志 `[TeamConfigLoader]` 前缀。
- `jiuwen_remote_member_names` 是列表型 metadata（remote_member_bootstrap.py:30-31），配置时注意 str | list[str] 两种形态都被接受。
- direct_addr 配 0.0.0.0 是高频错误（:538 注释），leader 侧日志有归一化痕迹；远端连不上先查这个再查防火墙。
- PG 自愈默认 30s 等待窗（:323 post_start_ready_max_sec），慢盘环境团队启动"卡住"多半在等这个，可调参而非改代码。
- TeamBinding 的 model_selection 每次冷构建重解析（team_binding_store.py:44-46 注释）——改了 models.defaults 后重建团队即生效，无需迁移存量 binding。

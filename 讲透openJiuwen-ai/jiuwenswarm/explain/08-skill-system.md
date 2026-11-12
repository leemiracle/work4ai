# 08 技能系统闭环

> 对应导览 S10。代表文件：`jiuwenswarm/server/runtime/skill/skill_manager.py`（12475 行）、`skilldev/` 子包、`marketplace/hub_client.py`。

## 一、角色定位

技能系统是 swarm 的"能力资产层"：skill 以目录+`SKILL.md`（frontmatter 声明 name/description/触发词）为本体，例如内置的 `agent-creator`（resources/agent/workspace/skills/agent-creator/SKILL.md:1-8，frontmatter 里塞满中英触发词供路由匹配）。`SkillManager` 是 `skills.*` 全部 RPC 的门面（skill_manager.py:994-996），marketplace 子包对接远程技能市场，skilldev 子包提供"从需求到 .skill 包"的流水线。它与主 ReActAgent 完全隔离——不共享对话上下文与内存，仅复用模型配置、MCP 工具工厂与文件系统配置（skilldev/DESIGN.md 的架构图一节）。

## 二、内部结构

**skill_manager.py 是全仓最大单类之一**：`SkillManager` 一个类约 322 个方法（regex 统计 12475 行中 `\n    def /async def`），74 个 `handle_*` RPC handler。RPC 面在 jiuwenswarm/server/dispatch.py:287-316 成片登记（SKILLS_LIST/GET/INSTALL/TOGGLE/MARKETPLACE_*/SKILLNET_*/CLAWHUB_*/TEAMSKILLS_HUB_* 等），且有一条硬规则：凡 pod_rest_map.REST_ROUTES 中的 skills.* 都必须登记，否则企业版 Gateway→Pod HTTP 直接回 HTTP_METHOD_NOT_HANDLED（jiuwenswarm/server/dispatch.py:285-286）。

**五路远程安装**：①marketplace spec 安装 `"plugin_name@marketplace_name"`（handle_skills_install，skill_manager.py:2558）；②内置/企业预置安装（handle_skills_install_builtin，skill_manager.py:2654；企业态走 `_sync_enterprise_builtin_skills()`，skill_manager.py:1044-1046）；③Team Skills Hub 资产安装（handle_skills_team_skills_hub_install，skill_manager.py:4067）；④ClawHub slug 安装（统一入口按 source 转发，handle_skills_online_search_install，skill_manager.py:3022-3031，`source: teamskillshub | clawhub | skillnet`）；⑤SkillNet URL 异步安装（handle_skills_skillnet_install，skill_manager.py:3166-3168——立即返回 `uuid4().hex` 的 install_id、后台 `_skillnet_install_background` 下载不阻塞网关队列，前端轮询 skills.skillnet.install_status）。三个在线源有固定同步集合 `_ONLINE_SYNC_SOURCES = {"skillnet","clawhub","teamskillshub"}`（skill_manager.py:189）。

**周边模块各管一摊**：`skill_files.py` 管技能文件的枚举/解析/预览（list_skill_workspace_files 排除 `.archive/`，skill_files.py:87,101；resolve_skill_relative_file 防路径逃逸，skill_files.py:158）；`archive_store.py` 钉版"版本真值只在 Skill 根目录 `.archive/versions/index.json`，不再用 skills_state.json.installed_plugins[].version"（archive_store.py:2-5）；`artifact_security.py` 做 SkillHub HMAC 完整性校验；`skill_type.py` 定识别优先级 skillpack > swarm_skill > multimodal_skill > skill（skill_type.py:2-4）；`skill_state_lock.py` 是跨进程 workspace 状态事务锁；`skill_prebuilt.py` 按租户同步预置技能。

**skilldev 十阶段流水线**：`SkillDevPipeline` 是确定性状态机，`STAGE_HANDLERS` 注册十个执行阶段——INIT/PLAN/GENERATE/VALIDATE/TEST_DESIGN/TEST_RUN/EVALUATE/IMPROVE/PACKAGE/DESC_OPTIMIZE（skilldev/pipeline.py:55-66），外加 PLAN_CONFIRM/REVIEW/DESC_OPTIMIZE_CONFIRM 三个挂起点（SUSPENSION_POINTS，skilldev/pipeline.py:54,82-83）。Pipeline 不长驻内存：每请求"StateStore 加载状态→new SkillDevPipeline→run()/resume()→checkpoint→释放"（DESIGN.md 3.2 节），崩溃可从 checkpoint 恢复。

## 三、外部连接

上游：`agent_ws_server.py:3660-3670` 的 `_is_stateless_method_request` 把 `skills./skilldev./plugins./symphony.` 前缀请求判为**无状态**——跳过 adapter 搭建直取轻量 JiuWenSwarm；其注释钉版两个坑：技能广场读必须在会话被永久删除后仍可用（#5886），且 fallback 必须按 channel 复用，否则每次 cache miss 新建 SkillManager 会让 SkillNet install/install_status 落到不同实例误报"安装会话已过期"（agent_ws_server.py:3715-3733）。门面接线：interface.py:1560 构造 `SkillManager(workspace_dir=...)`，interface.py:1580-1581 声明 SkillDev 模式懒初始化（首次 skilldev.* 请求才构造 `_skilldev_service`）。下游：安装完成后 `set_skillnet_install_complete_hook` 挂的重载钩子触发 Agent 重建（skill_manager.py:1048,1056）；symphony 把 Skill 仓库构建成知识图谱（见 03 篇）消费技能资产；marketplace 的 hub_client.py 是"Team Skills Hub 兼容 API 的通用异步客户端"，与 hub_asset_installer/hub_package_downloader/hub_catalog_cache 组成下载链。

## 四、数据流

以 SkillNet 安装为例：`skills.skillnet.install {url}` → 生成 install_id 入 `_skillnet_install_jobs` 字典（status=pending）→ `asyncio.create_task(_skillnet_install_background(...))`（skill_manager.py:3189-3191，任务名 `skillnet_install_{id 前 8 位}`）→ 立即返回 `{success, pending, install_id}` → 后台下载校验落盘 → 完成回调 hook 重载 Agent → 前端轮询 `install_status` 到 done/failed。本地状态走"动作→skill_state_lock 跨进程事务→skills_state.json+`.archive/versions/index.json`"双写。skilldev 流则：`skilldev.start {query, resources?, existing_skill?}` → SkillDevService.handle 按 `_METHOD_DISPATCH` 路由（skilldev/service.py:67-73）→ 新建 task_id+state+Pipeline → run() 推进到第一个挂起点 emit TODOS_UPDATE/CONFIRM_REQUEST 后 checkpoint 暂停 → 用户确认后 `resume(data)` 继续（skilldev/pipeline.py:74,150）→ PACKAGE 产出 .skill 包。

## 五、设计决策

①**名字安全闸**：所有外部传入的名字先过 `_safe_path_name`（skill_manager.py:656），ValueError 时 `_log_rejected_name` 记录并拒绝（skill_manager.py:834）——安装入口的路径注入防线。②**异步安装换 UX**：SkillNet 下载可能分钟级，同步等待会塞爆网关队列，install_id+轮询把慢操作变查询。③**版本真值单点化**：archive_store 明确废弃 skills_state.json 里的 version 字段，消除两处状态漂移。④**skilldev 桩与实现的分离**（系统级勘误）：**skilldev 流水线的 LLM 调用点全部是未接线桩**——`create_stage_agent` 直接 `raise NotImplementedError("create_stage_agent 尚未接入 openjiuwen，待实现")`（skilldev/context.py:105），`_register_tools` 同样（skilldev/context.py:114）；PLAN 阶段 `_generate_plan` 返回占位 plan（plan_stage.py:130-135，skill_name 固定 "placeholder-skill"）；GENERATE 阶段创建 `<!-- 待实现 -->` 占位文件（generate_stage.py:176-182）；IMPROVE 跳过改进（improve_stage.py:128）；INIT 的 docx/pdf/zip 解析全是 TODO（init_stage.py:87,109,118）。**状态机、checkpoint、事件流都是真实现，唯独"智能"部分缺席**——读这个子包时要把 DESIGN.md 的理想架构与代码现状分开。⑤**三入口自动识别**：create/create_with_resources/modify 由参数组合自动判定（DESIGN.md §1），前端无需传模式标志。

## 六、新人提示

- 改 `skills.*` 行为先查 dispatch.py 的登记表与 pod_rest_map 是否同步，企业版 HTTP 通道会静默 405。
- **不要假设 skilldev 能真生成技能**——十阶段能走通、能 checkpoint、能打包，但 PLAN/GENERATE/IMPROVE 的产物是占位符；演示前先接线 create_stage_agent。
- SkillManager 巨物找方法的技巧：handler 按 `handle_skills_<域>` 命名成簇（install 簇 2558-5000、列表读簇 1064-1500），先 grep 方法名再跳。
- 版本问题先看 `.archive/versions/index.json`，skills_state.json 里的 version 是遗留字段不可信。
- 新增在线源要同时维护 `_ONLINE_SYNC_SOURCES`（skill_manager.py:189）、`_ONLINE_SEARCH_SOURCE_ORDER`（skill_manager.py:340）与 normalize_sync_category 的归一化白名单（skill_manager.py:210-214），三处口径不一致会在同步状态判定里出现 unknown。

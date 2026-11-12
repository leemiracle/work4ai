# SettingsManager：database-first 三层配置中枢

> `src/local_deep_research/settings/manager.py`（1842 行；在 `settings/` 包，非 `config/setting_manager.py`）。接口契约在同包 `base.py` 的 `ISettingsManager`。

## 1. 角色定位

16 层架构中的**配置管理层**（layer:config："settings 管理器与环境变量注册表、defaults 各场景默认 settings JSON 20+ 方案"）。全仓配置唯一权威：Web 设置页、研究管线、搜索引擎工厂、LLM 提供方、调度器都经它或其快照读配置。图谱入度 30（`web/routers/settings.py`、`database/initialize.py`、`scheduler/background.py`、`api/settings_utils.py`、20+ defaults JSON config 节点），横切面最广的基础模块。

## 2. 内部结构

**模块级解析函数族**（前 500 行）：
- `UI_ELEMENT_TO_SETTING_TYPE`（L344）：9 种 ui_element → 类型转换器映射，"值从哪来决定怎么解析"的核心表；
- `parse_boolean`（L31）：HTML checkbox 语义，任意非空串=True（`"disabled"` 返 True 是刻意设计）；
- `get_typed_setting_value`（L357）：先 env（L391）后 DB，转换失败回退 default；
- `check_env_setting`（L419）：`search.tool`→`LDR_SEARCH_TOOL` 命名规则（L441），空串视为未设置（K8s/Terraform 兼容）；
- `is_valid_setting_key`（L281）：拒绝 `"foo."`/`"foo.."` 畸形 key（#4840，曾致 UI 渲染 `[object Object]`）。

**`SettingsManager`**（L506）四组：
- 生命周期：`__init__`（L512，`db_first=True` 硬编码 L530；记录创建线程 ID）、`_check_thread_safety`（L575，跨线程用 session 直接抛 RuntimeError）、`close`（L542）；
- 读：`default_settings` cached_property（L612，`rglob("*.json")` 合并 defaults/ 20+ JSON 并注入主题/策略动态 options）、`__query_settings`（L714，前缀查询带 `escape_like` 防 `keys[]=%` 全表泄露）、`get_setting`（L777）、`get_all_settings`（L1044）、`get_settings_snapshot`（L1191，压平供线程传递）；
- 写：`set_setting`（L885）、`create_or_update_setting`（L1223）、`delete_setting`（L1356）、`import_settings`（L1506，含 `_validate_imported_setting_value` L167 的 schema 校验 #5589）；
- 版本：`db_version_matches_package`（L1435）、`update_db_version`（L1455）、`load_from_defaults_file`（L1402）。

## 3. 外部连接

依赖：`database/models.Setting/SettingType`（ORM）、`defaults` 包、`web/models/settings`（5 个 Pydantic 模型）、`settings/env_registry`、`__version__`。被依赖：Web 层 routers（settings/chat/rag）与 services；启动链 `database/initialize.py`、`web/auth/routes.py`（登录后版本对账）；线程侧经 `config/thread_settings.get_setting_from_snapshot`（L71，`_NOT_FOUND` 哨兵区分"key 不存在"与"值为 null"，#4208）；标准入口 `utilities/db_utils.get_settings_manager`。

## 4. 数据流：一次配置读取链

研究线程读 `search.tool`：主线程 `get_settings_snapshot()` → `get_all_settings` 三段合并——① defaults JSON 打底（新设置免重置即入 UI）；② DB 行**含 schema 整体覆盖**（L1144 注释：DB 行是自包含快照，schema 仅版本对账时刷新，刻意不随读叠加 JSON，保住 export/import 往返不变量）；③ env 覆盖值并置 `editable=False`（L1177）→ 压平传后台线程 → `get_setting_from_snapshot` 解析（兼容 `{"value":x}` 与裸值）→ 引擎工厂消费。单 key 直读：`get_setting` 先 env-only 注册表（L804）→ DB 过滤畸形子键（L816）→ 单行返标量/多行返命名空间映射（L821）→ env → default。排队任务跨重启由 `apply_environment_overrides_to_snapshot`（L461）派发时重放 env。写入：`set_setting` 过五关（closed/`settings_locked` L586 懒读 `app.lock_settings`/env 锁 L604/editable/畸形 key 拒新建 L982），成功后自愈 ui_element（L943）与 type/category（L953）+ 安全 key 审计（L1025）+ WebSocket `settings_changed` 定向推送（L1680，只发本人）。

## 5. 设计决策：为什么 database-first

- **多用户 + 运行时可改**：本产品是 Web 服务（多账号），配置须按用户持久化且 UI 修改即时生效——文件型配置做不到；`db_first=True` 硬编码宣示 DB 是权威而非缓存。
- **三层 env > DB > defaults 各有语义**：env 是运维策略（operator 意志，故 `editable=False` 且写路径直接拒绝）；DB 是用户意图；defaults 只是出厂兜底 + UI schema 来源。env-only 设置（`env_settings.py`：路径/加密钥等 DB 自举前提）单独成注册表，解决"读库之前配置存哪"的鸡蛋问题。
- **schema 随版本对账而非随读合并**（L1129-1143 钉版注释）：随读叠加会绕过版本门破坏快照不变量，被否决的 PR #2474 记录了权衡。
- **线程安全**：不做跨线程锁，"每线程一实例 + snapshot 传递"匹配 SQLite 会话模型，代价是 `_check_thread_safety` 强约束。

## 6. 新人提示

读 `get_setting` → `get_typed_setting_value` → `check_env_setting` 这条 150 行主线覆盖 80% 场景。配置不生效按序排查：`LDR_*` env（L1779 查映射）→ DB 行 editable/settings_locked → key 畸形 → 版本对账（`app.version` 与包版本不符时登录后触发 `import_settings(overwrite=False)` 刷 schema）。加新设置只需在 defaults JSON 加条目（带 `ui_element`，否则 env 覆盖无类型转换并告警 L854），无需迁移。改本文件必读 L1129-1143 与 L739-756 两段注释——#4840/#4208/#5589/#4437 的边界都钉在那里。

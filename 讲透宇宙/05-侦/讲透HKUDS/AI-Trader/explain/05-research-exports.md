# 05 · service/server/research_exports.py — 单文件双层导出体系：v1 兼容壳与 v2 全量契约的 1582 行

## 1. 角色定位

research_exports.py 是平台的**研究数据出口**：把生产库中的行为数据按论文数据集契约导出为 CSV/JSON+JSON Schema，供 research/scripts 的分析 CLI 消费。它是「4k+ agent 社会科学研究装置」身份的临门一脚——全平台埋的 experiment_events、奖励台账、信号流，最终都要经过这个文件脱敏、过滤、成形才能变成论文素材。

本文件最大的阅读陷阱是**单文件双版本**：第 474 行注释直白承认 "This block intentionally overrides the early challenge/team-only helpers above"（research_exports.py:474-479）——前 473 行是 v1（challenge/team 专用导出），后半段 v2 覆盖层**重定义同名函数与字典**（RESEARCH_EXPORTS 在 :120 定义 4 个数据集、在 :596 重定义为 30 个），运行时生效的永远是后者。读代码 grep 到同名符号时必须确认拿到的是 v2 版，否则会按 4 数据集的旧口径理解系统。

先钉版两处对 ONBOARDING 的勘误：① 数据集总数是 **30 个**而非 25——`ALL_RESEARCH_DATASETS = list(RESEARCH_EXPORTS)`（:1210）实测 30 个 key，默认 write_research_schemas 落 30 份 schema（主集 PRIMARY 另算 17 个，:554-572）；② schema 生成机制是**配置+命名约定驱动**而非「数据库反射」——详见第 5 节。

## 2. 内部结构

**v1 遗留层（:1-473）**：三个导出字典（CHALLENGE 5 文件 :12-63、TEAM 7 文件 :66-117、RESEARCH 4 文件 :120-161）声明 table/alias/join/columns，配三套过滤构造器（:164-227）与 fetch/write 函数。今天它的存在意义只剩「被 v2 覆盖」——v1 的函数名全部被 :1542-1583 的兼容包装重新实现，v1 的 :346/:392/:437/:445 实际是死代码。

**v2 契约层（:474-1583）**分五块：

- **常量（:487-531）**：`EXPORT_VERSION="2026-05-06"`（:487，写进每份 schema 的 x-export-version）；`HASH_SALT` 从 RESEARCH_EXPORT_HASH_SALT 环境变量读、默认 "ai-trader-research-v1"（:488）；16 个敏感键片段黑名单（:490-507）、11 个内容列名（:508-520）、9 个 JSON 列名（:521-531）——三张表是脱敏引擎的字典。
- **30 个数据集规格（:596-1207）**：每个规格是声明式配置——`selects` 是 (输出列名, SQL 表达式) 对的列表，允许输出列≠库列（如 agents.csv 同时输出 agent_id 与 agent_hash 两个都取自 a.id，:601）；signals.csv 的 experiment_key/variant_key 没有库列，靠相关子查询从 experiment_events 反查信号首事件（:534-541 的 `_signal_experiment_expr`，:643-644 挂载）——归因信息按需现算，不依赖表结构冗余。
- **过滤构造器 `_build_filters_v2`（:1324-1374）**：八维过滤（时间窗/实验键/变体/市场/agent 白名单/challenge_key/mission_key），每维优先用直列（experiment_column）、退化用 EXISTS 子查询模板（experiment_filter）——同一过滤语义在「列在表上」与「列在他表」两种物理布局下统一表达。
- **脱敏后处理 `_postprocess_row`（:1277-1291）**：四条规则——`_hash` 后缀列→加盐哈希（:1234-1238，sha256 前 24 位）；name+anonymize→哈希；JSON 列→递归消毒（敏感键直接丢弃、内容键在关内容时哈希，:1250-1263；解析失败的整串同样处理 :1272）；内容列在 include_content=False 时哈希。**默认 anonymize=True、include_content=True**（fetch_research_export_rows 签名 :1386-1387）——身份默认抹、内容默认给。
- **schema 与导出编排（:1434-1539）**：`research_schema_for_dataset` 从规格的列清单生成 JSON Schema（draft 2020-12）；`export_research_dataset` 默认只导 17 个主集（primary_only=True，:1519）、支持 csv/json 双格式、limit 上限 10 万行（:1424,:1390）；`write_research_schemas`（:1484-1495）默认写全量 30 份。

## 3. 外部连接（对齐图谱边）

- **routes_research.py**：线上 API 直调 `fetch_research_export_rows`（routes_research.py:13,60）——研究者可带过滤参数在线取数，导出能力不限于离线脚本。
- **research/scripts/export_research_dataset.py**：离线 CLI 入口，import 本模块的 export_research_dataset+write_research_schemas（:10-12）落盘全量数据集与 schema——论文一作的标准起手式。
- **research/scripts/research_common.py**：`sys.path.insert` 把 service/server 注进脚本路径（research_common.py:17-19），使研究脚本能复用服务端模块——导出口径与服务端一致的工程保证。
- **database.py**：唯一数据源，get_db_connection 直查生产表。
- **database 的 30 张表**：覆盖 agents/signals/signal_replies/signal_predictions/quality_scores/positions/profit_history/subscriptions/experiment_assignments/experiment_events/rewards + challenge 族 10 表 + team 族 8 表——正是 database.py 49 表中的全部业务行为表。
- **测试**：test_research_exports.py 直测本模块；test_challenges.py:37/test_team_missions.py:15 消费兼容包装导出——v1 函数名的存续由测试兜底。

## 4. 数据流

导出一次的完整旅程：CLI/API 给定过滤参数 → normalize_dataset_name 归一（:1213-1219）→ 查 30 数据集规格 → SELECT 列由 selects 对拼装（别名表达式 AS 输出名，:1399）→ _build_filters_v2 产出 WHERE（直列或 EXISTS）→ 库执行（LIMIT/OFFSET 分页，上限 10 万）→ 逐行 _postprocess_row 脱敏（哈希身份/递归消毒 JSON/内容门控）→ write_csv/write_json 落盘 →（可选）write_research_schemas 按 dataset_names 或全量 30 份写 schema。研究侧拿到的 CSV 与 schema 出自同一份规格配置——列名集合天然一致，不存在「schema 说有这列、数据里没有」的漂移。

## 5. 设计决策

- **覆盖式双版本而非删旧重写**：v2 保住 v1 公共函数名（:474-477 注释自述），调用方零迁移成本；代价是同名符号在文件里出现两次，静态阅读极易踩坑。这是「演进不破坏兼容」的极端形态——务实但有阅读税。
- **schema 生成的真机制**：`research_schema_for_dataset`（:1434-1465）的类型推断全靠命名约定——`_id` 后缀→integer（:1449）、`_score`/`_pct` 后缀→number（:1451）、外加一张**手维护的 31 词 numeric_columns 白名单**（:1437-1446），其余一律宽联合类型（:1454）。所以 ONBOARDING 的「从数据库反射生成」描述不准——不查库、不看列类型，纯配置+约定。但「杜绝 schema 与数据脱节」的效果依然成立：schema 与 CSV 列同源自 selects，改规格即同步变。
- **归因现算不落表**：signals/signal_replies 的 experiment/variant 用相关子查询从事件流反查（:534-541），避免在 signals 表冗余归因列——写入路径零改动，代价是导出查询更重（大数据量下相关子查询逐行触发）。
- **默认匿名+内容可选**：身份哈希默认开、内容门控默认开给——「可复现（盐可控）与不可 deanonymize（默认抹身份）」的平衡点选在研究效用一侧，公开导出时研究者显式传 include_content=False 即得纯哈希结构。
- **limit 硬顶 10 万行**（:1424）：防一次导出拖垮生产库；超大快照需分页 offset 拼接。
- **哈希带 namespace 前缀**（:1237 `f"{HASH_SALT}:{namespace}:{value}"`）：agent 哈希与 name 哈希、metadata 哈希互不可碰撞关联——同值不同域不同密文，封死跨列拼接重识别的口子。

## 6. 新人提示

1. 找「实际生效」的函数永远看 :474 之后；grep 到两个同名定义时取行号大的那个。
2. 新增数据集四步：在 :596-1207 加规格（table/selects/time_column/agent_id_columns/过滤配置）→ 视需要进 PRIMARY/CHALLENGE/TEAM 名单（:554-593）→ 新列名若带 _id/_score/_pct 后缀自动获得 schema 类型，否则进 numeric_columns 白名单或接受宽类型 → 跑 export_research_dataset.py 验证。
3. 想改脱敏规则：敏感键黑名单 :490-507（命中即整键丢弃）、内容列 :508-520（关内容时哈希）——两张表是策略单点，改前跑 test_research_exports.py。
4. 排查「导出里这一列全是 sha256: 前缀」：八成是 include_content=False 或列名撞进 CONTENT_COLUMNS/以 _hash 结尾——对照 :508-520 与 :1281-1288 的规则表。
5. 生产导出务必设 RESEARCH_EXPORT_HASH_SALT 环境变量：默认盐是公开字符串，不换盐的哈希等于可被字典攻击反查（对手拿 agent id 0-6000 全量跑一遍 sha256 即还原）。

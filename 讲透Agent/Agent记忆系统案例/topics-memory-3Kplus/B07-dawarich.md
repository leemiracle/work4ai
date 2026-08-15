# B-07 `Freika/dawarich`（10.1K★）[结构档-未克隆]
> 来源：deepwiki（索引 2026-08-02, da551a）+ GitHub README/tree ｜ Ruby on Rails + PostGIS ｜ AGPL-3.0
> 一句话定位：自托管**位置历史**系统（Google Timeline 替代）——把"个人记忆 = 原始事件流 → 轨迹 → 停留 → 语义地点 → 摘要"的多级凝缩管线做成了产品；对 Agent 的 RESTORED 式记忆蒸馏有直接启发

## 1. 定位与形态
- 自我定位：隐私优先、数据主权的个人位置智能中枢（deepwiki Purpose："bridge the gap between raw GPS coordinates and meaningful travel insights"）。
- 技术栈（deepwiki 引用行号）：Ruby on Rails 8.1（Gemfile:54）+ PostgreSQL/PostGIS（db/schema.rb:15-17 空间类型与索引）+ Sidekiq 后台作业 + Action Cable 实时推送（config/initializers/sidekiq.rb）。
- 分发：多容器 Docker 应用（README.md:79-86）；云托管版有 Lite/Pro/Family 订阅分层（plan-based feature gating）。
- tree 实证 3671 条目：标准 Rails 单体（app/models、app/javascript/controllers/maps_controller.js 等）。

## 2. 架构与核心模块
### 2.1 数据管线 Coordinate → Insight（deepwiki Data Flow，逐级引行号）
1. **Ingestion**：
   - 实时：REST API（Dawarich iOS/Android App、OwnTracks、Overland、GPSLogger、PhoneTrack，README.md:62-75）；
   - 批量 Import：Google Takeout、GPX、GeoJSON、Strava 等（README.md:147-155）。
2. **清洗**：剔除 (0,0) 型 GPS 毛刺点（CHANGELOG.md:54）；**按 import 打点 id** 防多设备轨迹互相"编织"（braiding，CHANGELOG.md:48）。
3. **Enrichment**：reverse geocoding 补城市/国家；**夜间 geocoding 不覆盖用户手工命名的地点**（CHANGELOG.md:49）。
4. **聚合**：Points → Tracks（app/models/user.rb:33）。
5. **语义化**：Visits（在用户定义 geofence Area 内的停留，关联 Place）。
6. **分析**：月/年 Stats 与 Digests（距离、访问国家/城市数等，db/schema.rb:84-108）。

### 2.2 核心数据模型（deepwiki Core Data Model 表，引 db/schema.rb 行号）
| 模型 | 角色 | 关键关系 |
|---|---|---|
| Point | 原始 GPS 记录 | belongs_to user/import |
| Track | 移动轨迹（点聚合） | db/schema.rb:355-365 |
| Visit | 停留事件 | belongs_to place |
| Area | geofence 先验 | db/schema.rb:57-66 |
| Trip | 命名旅程 | notes + share_link |
| Digest | 周期旅行摘要 | db/schema.rb:84-108 |

### 2.3 呈现与共享
- 双地图引擎：Map v1（Leaflet）与 v2（MapLibre GL JS），热力图 + 预计算轨迹（maps_controller.js:1-29,150-153）；
- Action Cable 驱动 Live Map 实时位置（maps_controller.js:113）；
- Poster Studio：从地图/旅程生成可打印高分辨率海报；
- Family Sharing：consent 请求制实时位置共享（app/models/user.rb:4；db/schema.rb:128-184）；
- 照片集成：Immich/PhotoPrism 地理照片上图（app/models/user.rb:161-167）。

### 3.1 管线逐级对位（地理版 → 记忆版）
| Dawarich 层级 | 地理语义 | Agent 记忆对应物 |
|---|---|---|
| Point | 单次 GPS 定位 | 单条消息/单次工具调用 |
| Track | 连续移动聚合 | 同任务/同会话的事件序列 |
| Visit | 在 Area 内的停留 | 围绕关键实体的持续工作块 |
| Place | 语义地点（家/公司） | 语义实体/主题节点 |
| Digest | 月/年旅行摘要 | 周期性记忆综述 |
- 判定"停留"的输入一半来自用户先验（Area），一半来自数据（时长/密度）——记忆凝缩也应是"用户关注 + 统计显著"双输入。

## 4. 与 Agent 记忆的可迁移机制
1. **五级蒸馏管线**就是 episodic→semantic 记忆的标准形态：
   `原始事件(Point) → 序列聚合(Track) → 停留检测(Visit) → 语义实体(Place) → 周期摘要(Digest)`；
   每级独立建模、可从下一级重算（Digest 可由 Points 重建）——A 层记忆库大多"对话→向量"一步到位，缺的正是 Track/Visit 中间层。
2. **用户先验参与编码**：geofence Area 是用户声明的"重要区域"，决定哪些事件升级为 Visit——Agent 记忆里"用户关注的实体/项目"应作为凝缩的先验过滤器，而非纯统计显著才算重要。
3. **来源溯源防编织**：多设备 import 打标防轨迹串线——多源记忆（不同会话/工具写入）必须携带 source id，聚合时才不会把独立脉络错误拼接。
4. **机器富化不覆盖人工标注**：nightly geocoding 绕开用户命名的 place——自动记忆更新不得覆盖用户显式记忆，冲突时人工优先。
5. **数据主权作为产品主张**（vs Google Timeline 对照表）：自托管、可导出（GPX/GeoJSON）、导入不删原件（README.md:56 "Do not delete your original data"）——原始数据不可变原则。

## 5. 局限
- 地理专用语义：Track/Visit 依赖时空连续性，纯文本记忆需重新定义"停留"（如同一主题的连续会话）。
- Rails 单体 + Sidekiq 的吞吐上限；结构档未核 Ruby 源码细节（行号均转引自 deepwiki）。

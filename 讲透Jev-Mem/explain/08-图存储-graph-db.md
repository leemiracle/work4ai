> 标题：图存储——GraphDBInterface 与 NetworkXGraphDB 精讲 · 源文件：memory/graph_db.py（707 行）· 图谱标签：记忆存储与检索子系统 / 一级枢纽（文件级+NetworkXGraphDB 类级双枢纽）

## 角色定位

Jev-Mem 记忆图的"数据模型+存储引擎"层：定义图里有什么（节点/边/枚举）以及怎么存取。文件头（memory/graph_db.py:4-5）点明意图："abstraction layer ... that can be swapped for Neo4j"——用 ABC 接口抽象图操作，当前跑进程内 NetworkX，未来可平移 Neo4j 而不动上层。

它存在的理由：`trg_memory` 不该关心边怎么去重、`query_engine` 不该关心序列化格式。三层节点（事件/情景/会话）、四类边、边状态机、遍历约束判定在这里一次性钉死成领域词汇表，其余模块（memory_builder/query_engine/jev_mem_policies/jev_mem_retrieval/两个 benchmark）全 import 这套类型，是全仓被引最广的文件之一。

## 内部结构

**枚举**：`NodeType`（graph_db.py:19-25，EVENT/EPISODE/NARRATIVE/ENTITY/SESSION）、`LinkType`（graph_db.py:27-32，TEMPORAL/SEMANTIC/CAUSAL/ENTITY）、`LinkSubType`（graph_db.py:34-57，时间 3+语义 5+因果 5+实体 2，如 RESPONSE_TO 对话流、BELONGS_TO_SESSION 会话归属）、`LinkStatus`（graph_db.py:59-63，ACTIVE/DEPRECATED/PENDING 软删除预留）。

**数据类（均带 to_dict/from_dict 往返）**：`EventNode`（graph_db.py:65-99）、`EpisodeNode`（graph_db.py:101-166，title/summary/起止时间/event_node_ids）、`SessionNode`（graph_db.py:168-205）、`Link`（graph_db.py:207-257，`__post_init__` 在 217-222 自动打 created_at 与 ACTIVE）。`TraversalConstraints`（graph_db.py:259-301）是遍历策略对象，`allows_link`（graph_db.py:272-301）六连判：link_types 白名单→subtypes 白名单→置信阈值（graph_db.py:285，缺省 1.0）→必须 ACTIVE→三个 follow_* 布尔闸。

**接口**：`GraphDBInterface`（graph_db.py:303-367）12 个抽象方法——节点/边增删改查（graph_db.py:307-349）、`get_neighbors`（graph_db.py:327，返回 (节点,边) 二元组）、`traverse`（graph_db.py:352）、`find_path`（graph_db.py:359）、`get_subgraph`（graph_db.py:365）。

**实现**：`NetworkXGraphDB`（graph_db.py:369）。`__init__`（graph_db.py:372-377）四件套：`nx.MultiDiGraph()`+nodes 字典+links 字典+node_to_links 倒排。核心方法：`add_node`（graph_db.py:379，dict 与 graph 双写）、`add_link`（graph_db.py:388，391-394 校验两端否则 ValueError）、`get_neighbors`（graph_db.py:418，出边+入边都收）、`delete_link`（graph_db.py:491，499-502 裸 except 吞异常）、`traverse`（graph_db.py:513，deque BFS，524 与 527 双预算闸，返回 paths[:10] 见 556）、`find_path`（graph_db.py:565，按边类型过滤用 `nx.subgraph_view`+`filter_edge`）、`get_temporal_chain`（graph_db.py:612，沿 SUCCEEDS 前走/PRECEDES 后退）、`find_causal_paths`（graph_db.py:645，DFS 只跟 LEADS_TO/ENABLES）、`export_to_json`/`import_from_json`（graph_db.py:667、677，688-694 按 node_type 分派三种节点类）、`save`/`load`（graph_db.py:701/705，别名）。

## 外部连接

import 极简：stdlib+networkx+`collections.deque`，项目内只引 `.cache_compat.normalize_metadata`（graph_db.py:17，序列化时清洗 metadata）。被动层，不依赖任何业务模块。被引（grep 实证 10 文件）：`trg_memory.py`（拉走全部类型）、`query_engine.py`（直接用 graph_db.nodes/links/get_neighbors）、`memory_builder.py`、`jev_mem_policies.py`、`jev_mem_retrieval.py`、`longmemeval.py`、`scripts/evaluate_anchor_recall.py`、两测试。图谱双枢纽。

## 数据流

写入：`trg_memory` 造好 EventNode 调 `add_node`（graph_db.py:379）——nodes 字典存对象且 `graph.add_node(id, **node.to_dict())` 两处同步。建边调 `add_link`（graph_db.py:388）：校验两端→`links[link_id]=link`→`graph.add_edge(..., key=link_id)`→倒排两侧登记（graph_db.py:405-406）。

读取（查询链路核心）：`query_engine` 传锚点列表+约束调 `traverse`（graph_db.py:513）：队列初始化 `(node_id, depth=0, path=[node_id])`（graph_db.py:522），弹出后每个邻居过 `allows_link` 六连判（graph_db.py:537），通过则记边、扩展路径入队（graph_db.py:541-546）；受 max_nodes（graph_db.py:524）与 max_depth（graph_db.py:527）双闸；返回的 paths[:10]（graph_db.py:556）就是喂给叙事合成的"事件序列"。

持久化：`export_to_json`（graph_db.py:667）把两类对象 to_dict 后 json.dump；`import_from_json`（graph_db.py:677）先清空四件套（graph_db.py:682-685）再按 node_type 分派反序列化（graph_db.py:688-694），边在节点全部就位后才逐条 add_link（graph_db.py:697-699）——顺序保证不悬空。

## 设计决策

**dict+MultiDiGraph 双存储**（graph_db.py:375-383）是最显眼取舍：nodes 存活对象（O(1) 拿类型化实例），graph 存序列化属性（白嫖 NetworkX 的 subgraph_view/shortest_path/边枚举）。代价是每次 update 两边同步（graph_db.py:453、471-472），漏一处就漂移——`delete_link` 里 graph_db.py:499-502 的裸 except 正是同步失败的静默吞噬点，属于方便优先于严谨的债。

**有向图+双向成对边**（上游每条逻辑边建两条）让 `get_neighbors` 无需方向参数就给完整邻域（graph_db.py:418-441），遍历代码极简；代价是存储×2，且 find_path 的 shortest_path 在双向图上永远能原路折返，路径语义被稀释。**LinkStatus 三态**+allows_link 强制 ACTIVE（graph_db.py:290-291）为"因果边被推翻"的软删除留了通道——但全仓无生产代码置 DEPRECATED，属预留未用。**遍历返回 dict 而非对象图**（graph_db.py:553-563）方便落盘与日志，但调用方要再 get_node 回查对象，多一跳。**import 类型分派**（graph_db.py:688-694）用字符串比对而非枚举单态，是老缓存两种表示都出现过的兼容代码，新人别学。

局限：全内存、单进程、无事务；万级节点下 traverse 每步 append 完整路径拷贝（graph_db.py:543-546），内存 O(路径长×路径数)。真上生产规模就是换 Neo4j 的地方——接口已备好。

## 新人提示

阅读顺序：先读四个枚举（graph_db.py:19-63）建立词汇表——后续所有边类型讨论都基于 LinkSubType；再读 `EventNode`（graph_db.py:65）与 `Link`（graph_db.py:207）掌握数据形状；然后直奔 `traverse`（graph_db.py:513）+`allows_link`（graph_db.py:272），这对是查询链路咽喉；`get_temporal_chain`（graph_db.py:612）与 `find_causal_paths`（graph_db.py:645）是两个"当前无人调用但展示图威力"的方法，读它们能理解为什么用图而非列表存记忆。

三个常见误解：以为 traverse 的 paths 是最短路径——不是，是 BFS 扩展记录的所有到达序列前 10 条（graph_db.py:543-556），可能高度重叠；以为删边可软删——`delete_link` 是物理删，软删要走 DEPRECATED 状态（虽然还没人用）；以为 nodes 字典只有 EventNode——实际是 `Union[EventNode, EpisodeNode]`（graph_db.py:375），get_node 也可能返回 SessionNode（graph_db.py:410 类型注解），下游大量 `hasattr(node,'content_narrative')` 防御写法（query_engine 里到处是）就是在应付联合类型，别当冗余删掉。

# 10 Designer 图编排引擎

> 对应导览 S12。代表文件：`jiuwenswarm/server/runtime/designer/orchestration.py`（4539 行）、`node_agent.py`、`graph_store.py`，以及执行层 `jiuwenswarm/server/runtime/design/` 七件套。

## 一、角色定位

Designer 是可视化视频创作编排引擎：用户在画布上摆节点（brief/storyboard/character/scene/clip/music/compose），系统把每个节点装配成一个 DeepAgent 去"创意"，再由确定性 handler 保证"产物"。职责分层清晰：`orchestration.py` 的 `Director` 是总控智能体——brief、分镜、执行图、锁、prompt 闸、评分（orchestration.py:940-942）；`node_agent.py` 的 `NodeAgentHost` 把单个节点跑成 DeepAgent（node_agent.py:1955-1957）；`graph_store.py` 持久化图与运行态（`graphs/{graph_id}.json` + `runs/{run_id}.json` 双 schema，graph_store.py:5-9）；`smart_graph.py` 从 cast/shot 分析构建 prompt 感知的默认质量布局（smart_graph.py:2-9）；`design/` 目录是 swarmflow 迁移后的执行层——"graph → swarmflow script → per-node workers"（runtime/design/__init__.py:2-4）。

## 二、内部结构

**Designer 侧**：Director 的存活入口只剩两个——`design.director_chain`（designer_graph_autorun 的创作链）与 `onboard_user_added_nodes`（用户画布节点晋升为 LLM agent：保留用户画的边、永不删除 user_added 孤儿、模型缺失时在入口拒绝而非降级 handler，orchestration.py:944-956）。全量方法覆盖 plan/author_creative_brief/author_storyboard/design_execution_graph/review_*/validate_plan/finalize（orchestration.py:1062-3857）。node_agent.py 提供 `build_node_user_query`（节点→用户提示，node_agent.py:512）、`build_designer_tools`（图工具集，node_agent.py:1520）；NodeAgentHost 的铁律是"agent/LLM 失败 fail closed，绝不降级 handler 软成功；媒体后端仍在 handler——agent 创意通过后文本输出可由 handler 物化"（node_agent.py:1957-1961）。handlers/ 目录是节点物化注册表 `NODE_HANDLERS`：brief/character/scene/storyboard/clip/compose/music 七角色 + text/table/image/video/audio 五类型 + user_reference/comfyui 双特殊键（jiuwenswarm/server/runtime/designer/handlers/__init__.py:98-116），`resolve_handler_key` 按 pipeline→role→type 三级解析（jiuwenswarm/server/runtime/designer/handlers/__init__.py:120-137）。

**design/ 执行层（swarmflow 迁移终态）**：barrel 只导出四件——`GraphScriptCompiler`（确定性的图→脚本编译，frozen-once-produced 规则）、`RunCoordinator`（一图一终身 run_id、直调 run_workflow、run 记录+节点历史持久化）、`DesignEventBridge`（引擎进度事件→designer run payload）、`DesignContextRegistry/StoreNodeSpawner`（runtime/design/__init__.py:6-14）。文档钉版"替换被拣选的 designer 调度器，executor.py 原样保留作库，此处类是唯一调度面"（runtime/design/__init__.py:4-5）。`media_guarantee.py` 记录了迁移丢掉的三条宿主保证并按用户裁定（2026-10-12 方案 A"完全照搬"）重新武装到 worker 后端：**text guarantee**（有文本无 output_ref 就落盘文件盖戳，否则画布格子空白）、**media materialization**（期望媒体的节点缺产物族时用与 generate_image/generate_video 工具**同一套** handler 后端物化——LLM 保持创意路径、宿主保证产品）、**family gate**（物化仍不满足产物族就 FAIL，绝不带 markdown 桩 completed；gate 失败 decline 成 AgentResult.skipped 防引擎重试 LLM 轮，media_guarantee.py:4-28）。

## 三、外部连接

上游：Gateway 的 `designer_adapter._save_graph` 调 Director.onboard_user_added_nodes 晋升用户节点；`designer_graph_autorun` 驱动 director_chain。下游：RunCoordinator 走 openjiuwen 的 `run_workflow`（journal/WAL 路径来自 `openjiuwen.agent_teams.paths`，run_coordinator.py:37-41）；每个节点的 worker 由 team_worker/team_bridge 供给上下文；媒体生成最终落到 handlers 的厂商调用。容量约束横切：`pipeline/model_capacity.py` 的厂商容量口径表按 2026-09 厂商文档收录 Wan 3.0（2-30s、480/720/1080P、10 参考图，model_capacity.py:45-47）、Seedance 2.5（4-30s、30 参考图，:59-60）、Seedance 2.0/fast/mini（:72-86）、MiniMax-H3（4-15s、768P/2K、9 参考图，:98-99）、H3-Max（5-15s、拒绝参考图，:111-112）；`capacity_for_model` 未知 id 回退 Wan 3.0（:138-139），`snap_duration` 把画布时长吸附到档位（:177），`media_generation.py:237` 在生成时实际调用。

## 四、数据流

一次触发的完整链路（run_coordinator.py:229-320 一手注释）：`start(trigger)` → `heal_zombie_runs` 先把"running 但无活触发"的记录判为进程崩溃残留，写 error="interrupted by process restart (zombie self-heal)" 复位（run_coordinator.py:182,191-213）→ `_ensure_run_id`：图 meta 里有 `team_design_run_id` 就复用，没有则铸 `run_{token_hex(6)}` 终身绑定（run_coordinator.py:131-137）→ **版本号递增**：本次将执行的节点先 bump `state["version"]`，编译器把版本编进 agent() 的 phase("v{n}") 骑在调用签名上——重跑 bump 版本→新签名→WAL miss→真实执行（"gacha"）；未触碰节点版本稳定→跨触发 WAL 命中→免费回放；下游无需失效传播，其签名嵌入上游输出文本、上游一变自然 miss；WAL 保持只增不删不变量（run_coordinator.py:240-252）→ `trigger_scope = f"{run_id}-t{token_hex(4)}"` 承担旧"每次重跑一个 run_id"的角色，仅用于 worker 侧会话缓存/工作区文件名/媒体目录（run_coordinator.py:264-266）→ `GraphScriptCompiler.compile` 按 frozen-once-produced 生成脚本：已完成节点内联为字面量、只执行请求的节点、下游永不入脚本（无从重执行）→ 节点结果经 DesignEventBridge **单写者**逐节点即刻写回 Store（崩溃/取消恢复全靠 Store 驱动，无 resume 簿记）→ history 槽保留旧版本日志（每次覆盖前归档，history[-1] 是真前版），text/output_ref 恒持最新（run_coordinator.py:18-27）。

## 五、设计决策

①**一图一终身 run_id（用户裁定 2026-10-10）**：首个全量运行铸 run_id，此后每次触发合并进同一 run 记录、追加同一 journal+WAL 对（run_coordinator.py:2-13）；缓存失效改由节点版本承担而非换 run_id 或删记录——这是把"身份"与"缓存代际"正交化的干净解法。②**frozen-once-produced**：编译规则只有一条——节点 X 的 prompt 拼入祖先的冻结文本、排除每个已冻结节点（graph_compiler.py:4-23）；波次划分 `_waves` 让"frozen 节点绑字面量且永不拖波"（graph_compiler.py:188-201）。③**speech handler 键地雷（勘误）**：`resolve_handler_key` 对 `pipeline == "speech"` 提前返回字面量 "speech"（jiuwenswarm/server/runtime/designer/handlers/__init__.py:130-131），但 NODE_HANDLERS **没有注册** "speech" 键（jiuwenswarm/server/runtime/designer/handlers/__init__.py:98-116 的 16 个键里无它）——speech 节点一旦走 handler 物化路径，`get_node_handler` 会 `raise KeyError("no handler registered for node type: 'speech'")`（jiuwenswarm/server/runtime/designer/handlers/__init__.py:145-147）。实际执行路由在 orchestration.py 的 speech 工具链（call_speech_model）而非专属 handler，所以平时踩不到；但这是注册表与解析器之间的隐性契约缺口。④**单写者原则**：swarmflow 层只 emit 节点结果事件、bridge 是唯一持久化写者（run_coordinator.py:283-287）。⑤**迁移保真**：三条宿主保证原样搬、family/satisfaction/merge 辅助函数全部 import 自 node_agent"零重实现"（media_guarantee.py:29-31）。

## 六、新人提示

- 读执行语义先啃 run_coordinator.py 的模块 docstring（1-31 行）与 start 内注释（240-320 行），四条用户裁定（终身 run_id/版本失效/trigger_scope/单写者）全在里面，别从代码反推。
- **加新 pipeline 类型必须同时在 NODE_HANDLERS 注册**——speech 的前车之鉴就是"解析器认识、注册表不认识"。
- 排查"画布格子空白"：先看 text guarantee 是否触发（有文本无 output_ref 的落盘路径）；排查"重跑还是旧结果"：看节点版本是否 bump（谁重跑谁的缓存失效）。
- 厂商容量表是 2026-09 快照口径，新模型上线先更新 `_WAN3/_SEEDANCE_*/_H3*` 条目，否则 snap_duration 会把请求吸到错误档位。
- Director 不是对话入口——team.design 已把 Director 会话替换为 design leader，改交互逻辑去 director_chain 找，别在 Director 里加聊天方法。

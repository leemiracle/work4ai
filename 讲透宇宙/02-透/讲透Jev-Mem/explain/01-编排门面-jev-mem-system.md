> 标题：编排门面——JevMemSystem 精讲 · 源文件：jev_mem/system.py（75 行）· 图谱标签：编排、CLI 与兼容入口层 / 枢纽（file:jev_mem/system.py，fanIn=3 / fanOut=5）

## 角色定位

`JevMemSystem`（`jev_mem/system.py:10`）是整个仓库的公共 API 门面（facade）：对外只暴露 build / query / save / load 四个动作，对内把 `MemoryBuilder`、`QueryEngine`、`JevClient`、TRG 图库、向量库一次性组装好。它存在的理由是把"用户视角的记忆系统"与内部实现切开——`jev_mem/__init__.py:8` 把它登记为懒加载导出（`_EXPORTS`），CLI 经由它工作（`jev_mem/cli.py:15` import、`jev_mem/cli.py:64` 构造），发布面测试只认这个入口（`tests/test_public_release.py:124`、`tests/test_project_layout.py:38`）。

文件只有 75 行，却是论文主张的浓缩：`build_memory_from_conversation` 走 System-One 写路径（admission 概率打分，不做 LLM 抽取），`query` 把唯一一次 System-Two LLM 调用留给答案生成（`jev_mem/system.py:59`），并在 `jev_mem/system.py:60` 发出 `system_two_answer` 审计事件——把"深层推理只花在答题上"变成可计量的账目事实。

## 内部结构

单类四方法，无任何辅助函数：

- `__init__`（11-23）：五个参数全可注入（`model`/`embedding_model`/`cache_dir`/`jev_config`/`memory/memory_builder`）。默认构造 `MemoryBuilder`（15-16）后，把它的内部件"展开"挂到自己名下：`trg_memory`（17）、`graph_db`（18）、`vector_db`（19）、`llm_controller`（20）、`answer_formatter`（21）；再用 `memory_builder.node_index` 与 `memory_builder.jev` 组装 `QueryEngine`（22-23）。17-21 行是引用别名而非拷贝——builder 与 system 始终共享同一份状态，这是后面 `load_memory` 回填逻辑成立的前提。
- `build_memory_from_conversation`（25-52）：双入口。传入 LoCoMo sample（有 `conversation` 属性，27-28）直接转 `memory_builder.build_memory`；传入 list 则先全量校验（31 行注释 "Validate the full input before any insertion"）：每项可为 str 或 dict（34-35），`content`/`text` 必须非空（38-40），`timestamp` 接受 ISO 8601 并把 `Z` 归一为 `+00:00`（42-43），`metadata` 必须是 dict（46-48）；校验通过后逐条调 `memory_builder.build`（50-51），返回 `{"admitted": n, "rejected": m}`（52）。
- `query`（54-61）：`query_engine.query(question, top_k=5)`（55）拿 `(context, evidence)`；无 `llm_controller` 时直接返回 evidence 或字符串 "Information not found"（56-57，即没配 OPENAI_API_KEY 的无 LLM 降级）；否则 `build_qa_prompt`（58）→ `get_completion(temperature=0.0, response_format text)`（59）→ 审计（60）→ `extract_answer`（61）。
- `save_memory` / `load_memory`（63-72）：可选参数改写 `memory_builder.cache_dir` 后委托 `save()`/`load()`；`load_memory` 额外把重建的 `node_index` 回填给 `query_engine`（72）——漏掉这行，查询会静默失忆。

## 外部连接

import 三件（5-7）：`memory.memory_builder.MemoryBuilder`、`memory.query_engine.QueryEngine`、`memory.jev_mem_config.JevMemConfig`。被 import：`jev_mem/__init__.py` 经 `_EXPORTS` 懒加载（8）与 `__getattr__`（15-20），`jev_mem/cli.py:15`，加 `tests/test_public_release.py:124`、`tests/test_naming.py:14` 两个发布面测试。值得注意的是 `jev_mem/demo.py:7-9` **绕过**门面直接用 `MemoryBuilder`/`QueryEngine`——门面服务于 CLI 与外部用户，demo 展示的是内部组装方式。图谱把它放在 layer:orchestration（编排层，11 个文件），hub 统计 fanIn=3 / fanOut=5：扇出大于扇入，典型的顶层汇聚点。它的下游依赖全部经 `MemoryBuilder`（写）与 `QueryEngine`（读）中转，自身不直接碰 typesafe_sdk、numpy 或图库——这让公共 API 的依赖面最小。

## 数据流

写入例：`system.build_memory_from_conversation([{"content": "[Alice]: I moved to Berlin", "timestamp": "2026-01-05T10:00:00Z"}])` → 42-43 行解析出 aware datetime → 50 行逐条进 `MemoryBuilder.build`（admission 打分 → EventNode → 关系边 → 事务化入库）→ 返回 `{"admitted": 1, "rejected": 0}`。若某条是 "ok thanks"（无 recallable detail），admission 分低于 0.60，`build` 返回 None，计入 rejected——观察是否入库完全由 System-One 概率决定，全程零 LLM 抽取。

查询例：`system.query("Where does Alice live?")` → QueryEngine 检索（向量锚点 + 四图预算分配 + beam 遍历 + 多跳，内部还会问 routing/stopping/traversal 问题）产出 evidence 文本 → 58 行拼 QA prompt → 59 行 GPT-4o-mini 生成 → 61 行抽取答案字符串。Jev 决策全部发生在 QueryEngine 内部，门面对此无感知。

持久化：`save_memory("/path")` 把 `cache_dir` 切到新路径再落盘 graph.json / vectors / keyword_index.json / jev_mem_config.json（由 builder 的 `save()` 完成）；`load_memory` 反向恢复并回填索引（72）。

## 设计决策

门面 + 依赖注入：`jev_config` 与 `memory/memory_builder` 都可外部传入（12），测试注入 mock client 不必碰网络。校验前置（31）是刻意设计：先验证整个输入列表再逐条插入，避免"写一半报错"的半状态记忆库。`query` 的降级（56-57）让无 LLM 环境仍可做纯检索评测。audit 事件 `system_two_answer` 带 `llm_calls=1`（60）——System-Two 成本核算的最小计量单位，与写路径的 `memory_constructed`（`memory/memory_builder.py:180`）遥相呼应，两边账目合起来就是论文的成本曲线。

批判地看局限：(1) 50-51 行用 `sum(... for ...)` 逐条 build，返回值只有 admitted/rejected 计数，调用方拿不到建好的 node_id 句柄，想做"刚写的这条马上查"得自己扫图；(2) `top_k=5` 硬编码（55），`JevMemConfig.answer_top_k`（`memory/jev_mem_config.py:38`）管不到这里，两处口径易漂移；(3) `save_memory(save_path)` 会永久改写 `memory_builder.cache_dir`（65）——一次带参保存后，后续无参 save 落到新目录，是隐藏副作用；(4) 双入口靠 `hasattr(conversation)` 鸭子判断（27）而非显式类型分支，LoCoMo 对象与裸 list 的语义差异只藏在 docstring（26）里。

## 新人提示

先读 11-23 行看组装关系图，再读 25-52 行看输入契约。三个常见误解：① 以为 `JevMemSystem` 里有记忆逻辑——它一行业务都没有，全在 builder/engine，找 bug 别在这层停留；② 以为传 list 进 `build_memory_from_conversation` 会走 LLM 抽取——走的是 `MemoryBuilder.build` 的 System-One 路径，LLM 抽取只在 LoCoMo sample 分支的 MAGMA 路径里；③ 忘了默认 `JevMemConfig()` 的 `write_enabled=False`（`memory/jev_mem_config.py:12`），此时 build 全部落 `_build_magma` 基线路径，在节点属性里看到 `jev_mem.controller=magma_fallback` 不要意外。调试断点建议放 `jev_mem/system.py:50`（写）与 `:59`（读）。

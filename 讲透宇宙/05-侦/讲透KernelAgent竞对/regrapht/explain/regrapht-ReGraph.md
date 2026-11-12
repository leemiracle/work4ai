# 深解：ReGraphT/ReGraph/ReGraph.py —— 推理图的数据结构与检索基石

> 源码 221 行，git d1ea9b4。图谱归属 `layer:regraph-core`（推理图核心层，tour 第 4 站）。
> 上游论文叙事：《From Large to Small》——大模型优化轨迹沉淀为图，小模型沿图执行。

## ① 角色定位

本文件是整个 ReGraphT 方法的**存储与检索单引擎**：定义"优化知识"以什么形态被积累（图结构）、如何被写入（merge）、如何被持久化（save/from_graph）、如何被读取（get_state + 状态游走）。它不调用任何 LLM、不做任何评测——纯数据结构层，被 construct.py（离线建图）与 run.py（在线装配 reasoner）两侧共同依赖，是"建图"与"用图"的唯一交汇点。

## ② 内部结构

**三个类，两层语义**：

- `ReGraphNode`（节点=**优化方法**，不是 kernel、不是代码片段）：仅 `index` + `name` + 入/出边列表。节点语义被刻意压到最薄——"shared memory""warp divergence elimination"这类方法名。
- `ReGraphEdge`（边=**两方法间的状态迁移**）：`src/tgt` 整型索引 + `examples: list[dict]`。每个 example 是一次真实迁移实例：`{name(来源kernel), think(推理), detail(手法), before/after(迁移前后代码)}`。**知识本体存在边上而非节点上**——节点只是路由标签，"怎么从 A 优化到 B"的可复用证据全部挂在 A→B 边的 examples 里。
- `ReGraph`（有向图容器 + 游走状态机）：`regraph_nodes/regraph_edges` 平行列表（邻接信息冗余存于节点内）；`init_state` 恒为节点 0（"init state"=未优化的顺序版本代码）；**`self.state` 是当前游走位置**，`reset()` 归位——图不只被动存储，还主动维护"优化进行到哪个方法了"的游标。

**存储形态**：`save()` 序列化为单 JSON `{"node":[{index,name,in,out}], "edge":[{src,tgt,examples}]}`；`from_graph()` 逆向重建（先建边，再按 (src,tgt) 对把边配回节点的 in/out——O(n·e) 暴力匹配，图小无碍）。纯标准库（json+dataclasses），零第三方依赖。

**检索 API——按什么键检索？**这是关键事实：**本文件内没有任何相似度检索**（无 embedding、无向量库、零依赖决定了不可能有）。可用检索原语只有三个：① `get_state(index)` 按索引取节点；② 沿 `state.out_edges` 的**结构化游走**——当前方法状态决定候选下一跳方法及其 examples；③ `merge()` 内部的**方法名精确匹配**（`tgt.name == step['method']`）。名字能精确匹配的前提是 construct.py 的 `relabel()` 步骤：LLM 把新轨迹的方法名改写归一到图中已有方法名（如 "shared memory"→"shared memory optimization"）。**即：检索键 = 规范化方法名 + 图上位置，相似度检索的角色被 LLM relabel + 图结构替代**。

## ③ 外部连接

出边：`contains/exports` 三类及五个函数（图谱全量）。入边（importers）：`ReGraph/__init__.py`（barrel）、`construct.py`（建图主循环）、`run.py`（推理入口）。注意：run.py import 的 `ReGraphTReasoner/ReGraphTMCGSReasoner` 及 reasoner 变体在仓内**均为 0 行空文件**——仓库系早期形态，"用图检索"一侧只有接口签名与 prompt 证据，无实现体。

## ④ 数据流

**建图（大模型侧）**：kernel jsonl → `reason()`（CUDA_REASONING_SYSTEM_PROMPT 产出轨迹 `[{think,method,detail,code}]`）→ `relabel()`（对齐图中已有方法名，失败即丢弃该 kernel）→ `merge()`：逐步行走，三分支状态机——已有出边→**只追加 example**（同路收敛，边越来越厚）；方法已有节点但无出边→建新边；全新方法→建节点+建边。每 10 kernel 存检查点。**效果：N 条轨迹折叠成一张方法转移图，重复的优化模式在边上累积实例与统计（examples 长度≈转移频次）**。

**推理（小模型侧）**：`run.py` 加载 JSON → `from_graph()` → 注入 `ReGraphTReasoner(engine, regraph)`。REGRAPHT_SYSTEM_PROMPT 写明机制："user will also provide you with an optimization example... optimize the code follow the example"——即**从图上取出的边 examples（think/detail/before/after 迁移对）作为 in-context 示例喂给小模型**，让它"照例优化"。按接口推断的完整链路：新任务从 init_state 起步→按当前代码状态沿 out_edges 选下一方法→取该边 examples 作 prompt 示例→小模型产出该步代码→状态前移；MCGS 变体暗示游走策略可换（贪edy vs 蒙特卡洛图搜索）。**此段为接口级推断，实现体未开源**。

## ⑤ 设计决策：图 vs 平面记忆库

平面轨迹库（RAG 式）检索只能靠代码相似度，返回"整条历史轨迹"；本图的论据：①**组合性**——轨迹被分解为方法序列，公共前缀自动去重收敛，检索单位从"整条轨迹"细化为"一步迁移"（before/after 对恰好是可模仿的最小单元）；②**状态条件化**——候选下一步由"当前已用了哪些方法"决定，这是结构先验，而非只言片语的近邻；③**频次免费获得**——examples 累积即转移统计，无需额外计数；④**零依赖可移植**——JSON 工件与模型解耦，知识是数据资产。代价同样明显：方法名匹配脆弱（relabel 失败整条丢弃）、examples 无淘汰无去重、边无显式权重、`__init__` 可变默认参数 `[]` 是 Python 陷阱（现仅作真值判断未踩中）。

## ⑥ 竞对启示（ReGraphT 事实清单，对比由主会话补）

- 记忆形态：**方法转移图**；知识挂在边 examples（含 before/after 代码对），非节点。
- 检索键：**规范化方法名 + 图游走位置**；无 embedding/相似度检索（与 KernelMem 双层记忆的对比：留空）。
- 写入路径：LLM relabel 归一 → 三分支合并，同路只增厚边（与 KernelBlaster 优化数据库的对比：留空）。
- 消费路径：边 examples 直接作小模型 ICL 示例；游走策略可插拔（greedy/MCGS）。
- 开源完整度：数据结构层完整可跑；reasoner 层空文件，在线检索逻辑未放出。

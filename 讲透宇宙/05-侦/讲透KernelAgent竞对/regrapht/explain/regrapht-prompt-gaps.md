# ReGraphT prompt 双模板 + executor/reasoner 空壳考古

> 五文件全读 + run.py/construct.py/engine 交叉印证。姊妹篇：regrapht-ReGraph / construct / run-engine。commit d1ea9b4。

## ① 角色定位

这组文件是论文主贡献"从大到小迁移"的**消费侧（small 侧）骨架**：prompt/ 是全部提示资产（按建图侧/推理侧分两文件），reasoner/ 是七种策略的座位表，executor/ 是评测编排抽象。上游三件（construct 建图、ReGraph 图结构、engine 后端）完整可用；本组除两个 prompt 文件与两份 base 抽象外**全是空位或缺失**——仓库停在"图建好了、没人消费"。

## ② prompt 双模板解剖

**agent.py（小模型侧 5 常量，完成度三档）**：
- `STANDARD`（完整）：单步优化。注入点= user message `{"kernel": <cpp>}`（与 construct.reason 同构）；输出契约 `{think, code}`；三硬约束：函数名不变、host↔device 传输与 kernel 调用自含、完整无省略。
- `COT`（完整）：分步输出 list，每步 `{think, method, detail, code}`，method 有枚举（shared memory、warp divergence elimination）。此四元组即图的边属性——**baseline prompt 与建图数据同源**；method 字段身兼两职：小模型侧供评测归因，大模型侧作边标签，一份 schema 贯穿双侧。
- `CODERAG`：**空字符串**，连占位文案都没有。
- `REGRAPHT`：仅 2 句+1 句 example 机制说明（"follow the example"，"What's mode"系 What's more 笔误），无 Format 节。example=图检索出的迁移对作 in-context 注入；但"怎么选 example"（按相似度检索、贪心沿边、还是蒙特卡洛游走）恰是缺失实现的核心自由度，也是 ReGraphT 与 ReGraphT-MCGS 两变体的分野所在。
- `REGRAPHT_MCTS`：只有第 1 句，戛然而止。

`prompt/__init__.py` 只导出 STANDARD/COT——REGRAPHT 系与 CODERAG 应由缺失的 ReGraphT_reasoner.py、code_rag.py 直接从 prompt.agent import。

**ReGraph.py（建图侧 2 常量，均完整且被 construct.py 使用）**：
- `CUDA_REASONING`：与 COT 版逐字 diff 仅一处——**删掉 host/device 传输自含约束**（大模型只产轨迹，工程闭合交下游），是双模板唯一语义差异。
- `CUDA_RELABEL`：归一器。输入 `{methods: 图上已有方法名, process: 轨迹}`，输出 `[{existed, method}]`。merge 前的语义闸门：把自由方法名吸附到已有节点防图膨胀；relabel 失败整条轨迹弃用。

## ③ executor/base.py 抽象意图

registry-factory 模式（与 InferenceEngine.create_engine 同构）：`@register_executor(dataset)` 按数据集名（CUDAEval/ParEval）注册；Executor 持 `agent: Reasoner`（字段名与类型不一致，命名残留）；抽象方法 `run(kernels)` = "逐 kernel 调 optimize→评测"的编排壳。**全仓无一处使用该装饰器**，run.py 的 meta 也是空字典；executor/__init__ 还导入不存在的 utils.py。

## ④ reasoner 三空文件接口考古

基类契约：`__init__(engine)` + `optimize(kernel) -> dict`。engine 除 generate 外还有 `rollout(state)`、`generate_available_actions` 两抽象方法——**图游走语义下放 engine 层**，是 MCTS 系变体的接口级证据。

- **StandardReasoner**：类名与构造（仅 engine）被 run.py L17/L70 钉死，实现可复原：STANDARD 作 system + `{"kernel":…}` 作 user → engine.generate → 按 construct.py 的 ```json fence 正则提取 → 返回 `{think, code}` 恰为 dict，与基类签名吻合。
- **CoTReasoner**：响应是 list，与 `->dict` 错位。推断二选一：逐步驱动（每步喂上一步 code，"每步完整代码"约束支持此喂法）或包成 `{"trajectory":…}`；前者更合 trajectory 语义。
- **CodeRAGReasoner**：run.py L74 证明构造仅 engine——检索语料必须内聚；prompt 空串使其证据最少：按注释"代码相似度 RAG"，形态=检相似代码作 few-shot 拼入 user message。
- 顺带：rethink_mcts/mcts_rag/ReGraphT_reasoner 连空文件都没有，但已被引用 4 个类名（ReGraphTReasoner 多一个 `regraph=` 参数）。

## ⑤ 完成度审计（论文叙事 vs 仓库现实）

八环链：①轨迹生成 ✓②方法归一 ✓③入图 ✓④引擎抽象 ✓⑤Standard/CoT/RAG baseline ✗（0 字节）⑥RethinkMCTS/MCTS-RAG ✗（文件不存在）⑦**ReGraphT/MCGS 主贡献本体 ✗**（prompt 仅 2 句+文件缺失）⑧评测执行 ✗（无注册实现、utils.py 缺）。**辅助线占位、主线缺席**——开源截断在建图侧，主贡献未释出（与竞对情报"agent 框架未开源"一致）。当前 import ReGraphT.reasoner / executor / run.py 顶层三处直接崩：空文件报 ImportError（模块在、类名无），缺失文件报 ModuleNotFoundError，run.py 顶层 import 连坐全灭，仓库只能按"源码素材"读、不能作为包运行。笔误群佐证早期形态：What's mode、max_tokens 8196（construct 为 8192）、construct.py 两处 `matches is None` 失效（re.findall 返回空列表，靠外层 except 兜底）——该仓从未跑通一次端到端自检。

## ⑥ 新人提示

从 **standard.py** 动手最合理：证据最全（prompt 完整、响应恰为 dict、construct.py 有同构样板可整段改写）；是所有变体的最小内核（CoT=多步 standard，RAG=+检索前缀，ReGraphT=+图示例注入）；依赖最少（只碰 generate）。次序：standard → cot（复用同一 fence 解析，对照 construct.py 改三行即可起步；逐步驱动方案可先用"整段 CoT 一次生成"兜底再迭代）→补 executor/utils.py（纯 IO，让 run.py 可 import 的最短修复）→ code_rag → 最后 ReGraphT_reasoner（需自定义图检索协议与 Format 节，是论文真贡献，最该谨慎设计）。

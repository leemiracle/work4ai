# ReGraphT 新人上手指南

> 基于 `.understand-anything/knowledge-graph.json`（48 节点 / 84 边，commit `d1ea9b4`）自动生成，2026-09-04。

## 1. Project Overview

**ReGraphT**（作者 blacknickwield）是 ICLR 2026 投稿论文 **《From Large to Small: Transferring CUDA Optimization Expertise via Reasoning Graph》** 的配套代码仓库。语言为 Python（+ Markdown），框架依赖仅"OpenAI 兼容 LLM API"一项。

核心论点——"大→小"迁移：

1. **From Large（离线构图）**：让大模型逐个求解 CUDA kernel 优化任务，产出分步推理轨迹（每步含 think/method/detail/code 四字段）；
2. **沉淀**：轨迹按"优化方法名"重标注后增量合并进一张**推理图（ReGraph）**——节点=优化方法，边=方法间状态迁移，边上累积具体优化实例；
3. **To Small（在线执行）**：小模型加载该图作为可检索的优化知识，按图索骥复用大模型的优化路径完成 CUDA kernel 优化评测。

**完成度诚实披露**：本仓库处于**论文配套代码的早期形态**，全仓 19 个实质文件、约 35KB 代码（不含 .gitignore）。"From Large"半段（构图流水线 construct.py + 图数据结构 ReGraph.py + 双引擎 + 提示词）骨架完整；"To Small"半段几乎缺失——三种基线 reasoner（standard/cot/code_rag）均为 **0 字节空占位**，`reasoner/__init__.py` 声明的 RethinkMCTS/MCTSRAG/ReGraphT_reasoner 三个模块**尚未提交**，executor 侧的数据集加载 utils 也不存在。README 仅两行，无安装说明、无数据集、无已构图 checkpoint。**当前状态下任何端到端复现都不可行**（详见第 6 节）。

## 2. Architecture Layers（六层）

| 层 | 职责 | 关键文件 |
|---|---|---|
| L1 入口与编排 | 评测主入口：`--method` 选七种推理器，按数据集建 Executor 跑评测；扇出 5、零扇入的系统枢纽 | `run.py` |
| L2 推理图核心 | 方法的心脏：图数据结构（节点/边/重建/合并/检索）+ 离线构图流水线（reason→relabel→merge→checkpoint） | `ReGraph/ReGraph.py`、`construct.py` |
| L3 提示词 | 构图两模板（分步优化/重标注）+ 评测五策略（STANDARD/COT/CODERAG/REGRAPHT/REGRAPHT_MCTS） | `prompt/ReGraph.py`、`prompt/agent.py` |
| L4 推理后端 | EngineType(LOCAL/REMOTE) 枚举 + 注册表 + 抽象基类；vLLM 本地引擎与 OpenAI 兼容远程引擎 | `engine/` 四文件 |
| L5 执行器与推理器 | 评测执行骨架与"待补实现"：Executor 注册机制（持有 Reasoner）、Reasoner 抽象（持有 Engine，声明 `optimize(kernel)`）；三个空占位 | `executor/base.py`、`reasoner/base.py` 等 |
| L6 文档与配置 | 两行 README（论文主旨+入口指向）+ 标准 GitHub Python .gitignore | `README.md`、`.gitignore` |

## 3. Key Concepts

- **推理图（ReGraph）**：知识载体。`ReGraphNode`=一种优化方法；`ReGraphEdge`=两方法间的状态迁移并**累积具体优化实例**（边不只是关系，还是实例容器）；`ReGraph` 提供 `from_graph`（JSON 重建）/`merge`（增量合并）/`save`（序列化）/`get_state`（检索）。纯标准库实现（json + dataclasses），零第三方依赖。
- **推理轨迹沉淀**：`construct.py` 的四步循环——`reason`（大模型生成四字段轨迹）→ `relabel`（方法名归一化到图中已有方法集，命中则改名）→ `merge`（三分支状态机：已有出边→追加示例；方法已有节点→建新边；全新方法→建节点+建边）→ `save_re_graph`（周期性检查点）。relabel 是边归一化的文字契约，由 `CUDA_RELABEL_SYSTEM_PROMPT` 约束。
- **图检索注入**：run.py 从本地 JSON 加载 ReGraph 注入 reasoner，作为小模型可检索的 in-context 优化示例——这就是"迁移"发生的现场。
- **大模型构图-小模型执行**：构图走大模型（远程引擎），执行走小模型（vLLM 本地引擎），同一套 Engine 抽象屏蔽部署位置差异。
- **注册表+工厂插件模式**：`register_engine`/`ENGINE_REGISTRY` 与 `register_executor`/`EXECUTOR_REGISTRY` 两套同构机制，方法与数据集均按名查表实例化。
- **四字段轨迹协议**：think/method/detail/code——method 字段在 reasoning 与 relabel 两模板间前后衔接对齐，是整张图的 schema 基础。
- **executor 抽象**：Executor 持有 Reasoner 代理并声明 `run()`；"--method 选 Reasoner、数据集选 Executor，两者在工厂汇合"。
- **执行链路数据流**：构图链=kernel → construct.reason（大模型+REASONING 提示）→ relabel（方法名归一化）→ ReGraph.merge → checkpoint JSON；评测链=run.py → ReGraph.from_graph 加载 JSON → 注入 Reasoner → Executor 遍历 kernel 调 optimize → 回收优化代码。两条链以图 JSON 文件为唯一交接物，解耦离线与在线。
- **输出契约的容错设计**：LLM 输出一律按 JSON 解析（正则抽取 fence 内容），失败即跳过该条——构图是"尽力而为"的增量过程，靠检查点与 continue 语义保证批量鲁棒，代价是轨迹回收率不可见。

## 4. Guided Tour（推荐阅读路径，9 步）

> 上手提示：本仓无任何可运行入口（包级导入即报错），建议全程"纸上读码"。优先精读第 3、4 步（构图流水线+图结构），它们是论文方法的真正载体，也是独立于缺失实现、当下就能理解与改动的部分；引擎层可只读接口签名；推理器/执行器留待动手实现时再回来对照。

1. **项目概览**：读 README，建立"推理图迁移 CUDA 优化专长"的问题框架。
2. **评测主入口 `run.py`**：在脑中建立"一次实验=选方法+建执行器+跑评测"的全景骨架，后续各步都是拆解它的导入。
3. **离线构图流水线 `construct.py`**：论文标题的前半段——大模型轨迹如何变成图。
4. **图数据结构 `ReGraph/ReGraph.py`**：全仓扇入最高的模块之一，迁移方法的存储与检索基石。
5. **提示词模板库 `prompt/`**：构图与评测两条链路的文字契约（注意输出均为 JSON schema 约定）。
6. **推理后端抽象 `engine/inference_engine.py`**：注册表+工厂如何让上层对 local/remote 无感。
7. **双引擎实现 `local_engine.py`/`remote_engine.py`**：vLLM 与 OpenAI 兼容接口的两个具体后端。
8. **推理器与执行器抽象 `reasoner/base.py`+`executor/base.py`**：Method×Dataset 在此汇合。
9. **占位现状**：直面三个空文件与缺失模块——对贡献者这恰是路线图：骨架已立，七种推理器变体的落地是最有价值的切入点。

## 5. File Map（全部 19 文件）

| 文件 | 层 | 复杂度 | 一句话职责 |
|---|---|---|---|
| `README.md` | L6 | simple | 两行：标题+论文全题（ICLR 2026 投稿） |
| `run.py` | L1 | moderate | 评测主入口，七方法分派+双数据集执行编排 |
| `construct.py` | L2 | **complex** | 离线构图流水线（reason/relabel/merge/checkpoint+CLI） |
| `ReGraph/__init__.py` | L2 | simple | barrel：重导出三个核心类 |
| `ReGraph/ReGraph.py` | L2 | **complex** | 图数据结构：Node/Edge/ReGraph（重建/合并/保存/检索） |
| `prompt/__init__.py` | L3 | simple | barrel：再导出构图两模板+两个基线模板 |
| `prompt/ReGraph.py` | L3 | moderate | CUDA_REASONING + CUDA_RELABEL 两系统提示词（四段式结构） |
| `prompt/agent.py` | L3 | moderate | 五策略提示词；CODERAG 为空串、MCTS 仅骨架 |
| `engine/__init__.py` | L4 | simple | barrel：统一再导出 engine 抽象层 |
| `engine/inference_engine.py` | L4 | moderate | EngineType/EngineConfig/SamplingParams/注册表/抽象基类 |
| `engine/local_engine.py` | L4 | moderate | LocalEngine：vLLM+AutoTokenizer 加载本地模型批量推理 |
| `engine/remote_engine.py` | L4 | moderate | RemoteEngine：openai.OpenAI(base_url) 兼容远程调用 |
| `reasoner/__init__.py` | L5 | simple | barrel：声明 7 个推理器导入（仅 4 个目标存在） |
| `reasoner/base.py` | L5 | simple | Reasoner 抽象：持有 Engine，声明 optimize(kernel) |
| `reasoner/standard.py` | L5 | — | **0 字节空占位**（应实现 StandardReasoner 基线） |
| `reasoner/cot.py` | L5 | — | **0 字节空占位**（应实现 CoTReasoner） |
| `reasoner/code_rag.py` | L5 | — | **0 字节空占位**（应实现 CodeRAGReasoner） |
| `executor/__init__.py` | L5 | simple | barrel：导出 Executor；引用不存在的 .utils（导入即失败） |
| `executor/base.py` | L5 | simple | register_executor 注册装饰器+Executor 抽象基类 |

（另有 `.gitignore`：GitHub Python 模板近乎原样拷贝，未针对 GPU 实验特化。）

## 6. Complexity Hotspots 与缺口

**热点（修改前先深读）**：

- `ReGraph.merge`（complex）：三分支状态机决定图的生长语义，任何改动都影响后续所有合并行为；与 `construct.py` 的 `construct_regraph`（complex）耦合——后者是全流水线编排，含正则提取 ```json```、失败即跳过、单 kernel 异常捕获后 continue 等容错逻辑。
- `run.py` 主流程（moderate）：连续 if 分派七方法 + 双引擎配置组装（max_tokens 默认 8196，疑为 8192 笔误）。

**空文件与缺失模块意味着什么**：

1. **核心方法本体缺失**：论文声称的七种方法中，ReGraphT/ReGraphT-MCGS/RethinkMCTS/MCTS-RAG 的 reasoner 模块**根本不在仓库**，三个基线是空文件——即"To Small"的执行半段（含论文主方法）没有任何实现，`import ReGraphT.reasoner` 直接 ImportError。
2. **评测侧缺口**：executor 只有抽象基类，CUDAEval/ParEval 两个具体执行器与 `utils` 数据集加载均未提交——评测闭环不存在。
3. **已埋的 bug**：`register_engine` 设计为需带 EngineType 参数的装饰器工厂，但两个引擎均以无参 `@register_engine` 使用——`ENGINE_REGISTRY` 实际从未被写入，`create_engine` 查表大概率失败；`local_engine.py` 中自定义 `SamplingParams` 遮蔽 vLLM 同名类，传给 `llm.generate` 的是 dataclass 实例。
4. **静默数据损失**：构图时 LLM 输出正则提取失败即跳过该步、单 kernel 异常 continue——图的质量对解析成功率敏感且无统计上报。
5. **环境契约未文档化**：依赖环境变量 LOG_PATH/OPENAI_API_KEY/BASE_URL；无 requirements.txt、无数据集、无已构图 JSON 工件发布。

**与论文声称的差距 / 复现风险**：论文叙述的完整故事=大模型构图+小模型按图执行+多基线对比评测；仓库现状=构图半段可读可改（fix 两处 bug 后理论可离线构图），执行与评测半段为零。量化差距：论文七方法，仓库落地 0/7（三基线空文件、四方法无模块）；论文两评测集（CUDAEval/ParEval），仓库落地 0/2；方法主件中已交付的是"知识表示"（ReGraph）与"知识获取"（construct+prompt）两块，"知识消费"整块缺席。复现风险评级：**高**——即使补齐代码，还需自备双端模型、CUDA kernel 数据集与正确性/性能测量脚本，且构图 prompt 的版本一致性无法与论文对账。对新贡献者的建议路径：先修 engine 注册 bug 与 SamplingParams 遮蔽 → 落地 StandardReasoner/CoTReasoner 两基线打通 run.py → 实现 ReGraphT_reasoner 完成方法闭环 → 再补 executor 与数据集加载。

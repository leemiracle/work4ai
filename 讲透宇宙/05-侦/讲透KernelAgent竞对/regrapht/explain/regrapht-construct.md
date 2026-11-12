# 深解 ReGraphT/construct.py —— 推理图构建流水线（全仓最核心）

> 源码 248 行 | 图谱层：`layer:regraph-core`（推理图核心层）| 依赖：`ReGraph/ReGraph.py`（图数据结构）、`prompt/ReGraph.py`（双提示词）

## 一、角色定位：大模型优化轨迹 → 结构化推理图的转化器

ReGraphT 论文标题是《From Large to Small: Transferring CUDA Optimization Expertise via Reasoning Graph》——把大模型（large，默认 `deepseek-chat`）的 CUDA 优化能力沉淀为可复用的推理图，再迁移给小模型执行。construct.py 就是"From Large"这一侧的知识沉淀器：它是一个**独立的离线 CLI 入口**（`python -m ReGraphT.construct`），逐个读入 CUDA kernel，让大模型分步推理出优化轨迹，然后把轨迹**结构化为一张方法转移图**（ReGraph），周期性落盘为 JSON。整个仓库其余部分（run.py/reasoner/executor）都是这张图下游的消费者——没有 construct.py 就没有 ReGraphT 方法本身。

## 二、内部结构：五函数三段流水

文件由 `construct_regraph()` 主循环（L155-222）编排，对每个 kernel 执行 **reason → relabel → merge** 三段：

1. **`reason()`（L34-68）——轨迹生成**。输入单条 kernel 记录 `{index, name, kernel: CPP源码}`，只把 `kernel` 字段打包成 user message，配上 `CUDA_REASONING_SYSTEM_PROMPT` 调 LLM。该提示词要求"step by step 优化"，每步输出四字段：`think`（推理过程）/`method`（优化方法名，如 shared memory）/`detail`（方法怎么用）/`code`（本步优化后代码），整体以 JSON list 返回。解析用正则 `` r'```json\n(.*?)\n```' `` 从回复中提取代码块再 `json.loads`。**注意一个真实缺陷**：`re.findall` 永不返回 `None`（只返回空列表），所以 L61 的 `if matches is None` 是死分支——无 JSON 块时实际走 `matches[0]` 抛 IndexError，靠外层 `construct_regraph` 的 try/except 记日志后 continue 兜底。"提取失败返回 None"的契约形同虚设。

2. **`relabel()`（L71-126）——方法名对齐（全文件最关键的机制）**。LLM 自由生成的 `method` 名必然同义漂移（"shared memory" vs "shared memory optimization"），若直接入图，图会被同义节点炸成碎片。relabel 在 merge 前做在线规范化：把图中**当前全部已有方法名** `methods` + 新轨迹 `process` 一起再发一次 LLM（`CUDA_RELABEL_SYSTEM_PROMPT`），让它逐步判断 `existed: yes/no`，yes 则把方法名改写为已有标准名。代码做了两道保守校验：标签数必须等于轨迹长度；`existed=yes` 时返回的方法名必须在 methods 表中——任一失败即整体返回 None、丢弃该 kernel（宁缺毋滥）。

3. **`merge()`（L129-139）+ `save_re_graph()`（L142-152）**。前者是薄包装，转调 `ReGraph.merge`（真正的建图逻辑在 ReGraph.py，见下节）；后者负责检查点：每 `save_steps` 个 kernel 存一次 `prefix_N.json`，结束存 `prefix_final.json`。

4. **`construct_regraph()` 主循环**。支持 `--re_graph` 加载已有图实现**增量构建**；kernel 数据是 JSONL（每行一个 kernel）；单 kernel 异常仅记日志不中断。另注意 `top_k` 参数被解析（L236）但从未传进任何 LLM 调用——死参数。

环境侧硬约束：模块 import 时就读 `LOG_PATH`/`OPENAI_API_KEY`/`BASE_URL` 三个环境变量（L25/L30-31），缺 `LOG_PATH` 会在导入瞬间 KeyError。LLM 客户端走 OpenAI 兼容端点。

## 三、外部连接：run.py 不直接调用它

图谱边显示 construct.py 只 import 两个东西：`ReGraph/ReGraph.py`（数据结构）和 `prompt/`（提示词）。**关键架构事实：run.py 与 construct.py 之间没有任何函数调用**——衔接媒介是 JSON 文件。construct.py 离线产出 `ReGraph_*.json`；run.py 在 `--method ReGraphT` 或 `ReGraphT-MCGS` 时用 `--local_regraph_path` 加载该 JSON，经 `ReGraph.from_graph()` 重建图对象，注入 `ReGraphTReasoner`/`ReGraphTMCGSReasoner`。所以对任务问题的回答是"两者都喂"：合并期产物是 ReGraph.py 的内存结构，落盘后由下游 reasoner 把图内容（节点方法名+边上 examples）转写进小模型的 prompt。**但**：`reasoner/__init__.py` 声明的 7 个导入中，standard/cot/code_rag 是 0 字节空文件，RethinkMCTS/MCTS-RAG/ReGraphT_reasoner 三个目标文件**尚未提交**，executor 的 `load_cuda_eval_dataset` 所在 utils 也不存在——run.py 当前 import 即崩，消费端整体缺位，仓库是早期形态。

## 四、数据流：从 LLM 文本到可检索图结构

```
JSONL kernel 数据集 {index, name, kernel:CPP码}
  → reason(): LLM 调用 → ```json``` 块正则提取 → 轨迹 [{think, method, detail, code}]
  → relabel(): 第 2 次 LLM 调用（附图中已有方法名表）→ 方法名对齐后的轨迹
  → ReGraph.merge(): 沿轨迹逐步走图（三层判定）：
      ①当前节点已有指向同名方法的出边 → 复用边，examples.append(载荷)
      ②方法节点已存在但无边 → 新建边
      ③方法不存在 → 新建节点(index=len(nodes))+新边
      载荷 = {name, think, detail, before:上一步代码, after:本步代码}
  → save(): {node:[{index,name,in,out}], edge:[{src,tgt,examples}]}
  → (下游) from_graph() 重建 → reasoner 按状态检索边上的 before/after 代码对
```

检索接口在 ReGraph.py 侧：`state` 游标 + `reset()` + `get_state(index)`，暗示下游是"图上逐状态游走、每步取边 example 做代码级示范"的推理模式。

## 五、设计决策：保留了什么，丢了什么（对比直接存 few-shot）

**保留**：①方法级抽象——每步的 `method` 名升格为图的节点身份，是知识复用的原子单元；②顺序结构——边 (A→B) 编码"优化方法 A 之后做 B 有效"的转移知识，这是 few-shot 整条轨迹无法跨 kernel 复用的部分；③代码级实例——每条边挂 before/after 代码对+推理文本，具体性不丢。

**丢弃/压缩**：①轨迹的线性整体性被打散——多 kernel 的经验在同一图上叠加重组，example 列表 append-only，不保留来源顺序；②**零验证**——轨迹纯出自大模型推理，全程没有编译、运行、speedup 或正确性检查，图的可信度等于 LLM 幻觉的可信度；③无频率/质量权重——examples 数量隐含了路径热度但代码未显式利用；④kernel 领域特征只剩 example 里的 `name` 字段。

与 few-shot 的本质差别：RAG-fewshot 按 kernel 相似度取整条轨迹，知识粒度=一条轨迹；ReGraph 粒度=一条方法转移边，同一条优化路径可从不同 kernel 的碎片经验中拼装，且 relabel 保证了跨 kernel 的方法名严格对齐（在线去重）。代价是每个 kernel 要两次 LLM 调用，且规范化质量依赖 relabel LLM 的判断。

## 六、新人提示与空缺分析

**上手提示**：①跑之前必须 `export LOG_PATH=... OPENAI_API_KEY=... BASE_URL=...`，否则 import 即挂；②看懂本文件只完成一半，`ReGraph.merge`（L116-185）才是建图算法本体（内含两处 `TODO: 封装加边后操作`）；③`--re_graph` 支持断点续建，配 `--save_steps` 用。

**空缺清单**（按影响排序）：①**消费端整体缺失**——ReGraphT/MCGS reasoner 及全部 baseline reasoner 未提交/空文件，"图怎么变成小模型 prompt"目前只能从 prompt/agent.py 和 ReGraph 的 state API 反推；②**构建端零验证**——最值得补的是 merge 前插入编译+计时门（本仓若做迁移定律研究，这正是"记忆毒性/去伪"实验的抓手）；③`matches is None` 死分支、无重试机制（LLM 格式错一次丢整个 kernel）、top_k 死参数；④relabel 的 methods 列表随图线性膨胀，无截断/embedding 归并策略，图大了以后 prompt 会爆；⑤边 examples 无上限、无淘汰；⑥串行处理无并发；⑦`from_graph` 不校验 init_state=index 0 的假设；⑧docs 目录此前为空——本文档即首篇 explain。

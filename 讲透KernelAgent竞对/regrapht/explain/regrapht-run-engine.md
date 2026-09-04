# 深解 ReGraphT：run.py 入口 + engine 三件

> 范围：`ReGraphT/run.py`（112 行）、`engine/inference_engine.py`（85 行）、`engine/local_engine.py`（73 行）、`engine/remote_engine.py`（64 行）。源码全读 + 本地实测验证。仓库背景：ReGraphT = "From Large to Small: Transferring CUDA Optimization Expertise via Reasoning Graph"——用大模型把 CUDA 优化经验沉淀成「优化方法迁移图」，再让评测期模型沿图优化。

## ① 角色定位：run.py 在「构图→迁移→评测」中只占最后一段

完整流水线实际由两个入口分担：

- **构图段（`construct.py`，不在本次范围但必须理解）**：用大模型（默认 `deepseek-chat`）对每个 CPU kernel 生成逐步优化轨迹（`reason()`），再 `relabel()` 把轨迹中的方法名对齐到图里已有方法词表，最后 `ReGraph.merge()` 合入图中，周期性 `save()` 成 JSON。
- **迁移段**：载体就是那份 ReGraph JSON——`run.py --local_regraph_path` 加载它（`ReGraph.from_graph`）注入 ReGraphTReasoner，"迁移"即图作为 few-shot 例子库被小模型消费。
- **评测段（`run.py` 本体）**：编排四件事——建推理引擎、按 `--method` 七选一组装 reasoner、加载数据集（CUDAEval/ParEval）、创建 Executor 驱动全部 kernel。

知识图谱把它归入 `entry-orchestration` 层（扇出 5、零扇入），engine 三件归 `engine` 层——run.py 是纯编排枢纽，不含任何业务逻辑。

## ② run.py 内部结构

单文件两函数，`main()` 五个阶段线性串联：

1. **建引擎**（L54-66）：`--engine local|remote` 二选一，只把 `local_model_path` 或 `base_url` 塞进 `EngineConfig`，经 `InferenceEngine.create_engine` 静态工厂从注册表取类实例化。
2. **建 reasoner**（L68-94）：`--method` 七选一 = 2 条基线（standard/CoT）+ 2 个检索/搜索基线（RAG/RethinkMCTS、MCTS-RAG）+ 2 个本方法（ReGraphT/ReGraphT-MCGS）。仅 ReGraphT 系多一步：读 JSON → `ReGraph.from_graph()` → 注入。
3. **加载数据集**（L96-99）：`load_cuda_eval_dataset` / `load_par_eval_dataset`。
4. **建 Executor**（L103-107）：`Executor.create_executor(dataset=args.dataset, agent=reasoner)`——按数据集名查 `EXECUTOR_REGISTRY`。
5. **跑**（L109）：`executor.run(kernels=dataset)`。

**大模型/小模型各在哪步**：run.py 里根本没有"模型大小"概念——只有引擎位置（本地/远程）。大模型出现在**上游构图段**（construct.py，教师角色）；run.py 驱动的是**学生**：本地路径通常是小模型（vLLM 加载），remote 则任意（base_url 指哪都行）。

**输出物**：run.py 自身零落盘（连日志都没配）；输出责任完全在缺失的 Executor 实现里。构图段才有明确输出物（`{prefix}_{steps}.json` + `_final.json`）。

## ③ engine 三件解剖

**inference_engine.py——抽象核心（85 行）**：五个符号撑起一个微注册表模式。`EngineType` 枚举（LOCAL/REMOTE）；`EngineConfig`（仅 `base_url`/`local_model_path` 两字段）；`SamplingParams`（采样参数信封，model 也放这）；`register_engine` 装饰器写 `ENGINE_REGISTRY`；`InferenceEngine` 抽象基类——三个抽象方法 `generate` / `rollout` / `generate_available_actions` + 一个默认空实现的 `extract_state`。**这个接口签名暴露了设计意图**：engine 不只是文本生成器，`rollout(state)` 和"可用动作生成"是为 MCTS 类 reasoner 预留的状态机后端语义（把图节点/迁移当动作空间）。

**local_engine.py——进程内 vLLM（73 行）**：模型服务形态 = **离线批推理**，无服务进程。构造时 `AutoTokenizer`（`trust_remote_code=True`）+ vLLM `LLM(model_path)` 一次性把模型拉进自己进程。`generate()` 把 OpenAI 风格 messages 用 `tokenizer.apply_chat_template` 渲染成字符串（自动兼容单条/批量两种输入形状），交 `llm.generate()`，返回信息最全的 batch：`generation` 文本、`generation_ids` token 序列、逐 token `logprobs`、prompt/generation/总 token 计数。注意文件内 `from vllm import SamplingParams` 与本模块同名类局部遮蔽——恰好能跑，属易踩雷写法。

**remote_engine.py——OpenAI 兼容客户端（64 行）**：模型服务形态 = **外部 HTTP 服务**。`openai.OpenAI(base_url=config.base_url)`——**是 OpenAI chat.completions 兼容协议**，任何 `vLLM serve`/SGLang/各家网关都能接。构造时不传 `api_key`，静默依赖 `OPENAI_API_KEY` 环境变量。逐条串行请求（无并发），返回瘦身 batch：只有文本和可选 logprobs，token 计数与 ids 全 `None`（接口对齐 local 的降级）。**实测发现潜伏 bug**：`for i, choice in enumerate(response)` 迭代的是 `ChatCompletion` 对象而非 `response.choices`——pydantic 迭代产出 `(key, value)` 元组，`choice.message` 必 `AttributeError`，除格式外没有任何 openai 版本能救。

## ④ 数据流

评测主链：`CLI args → EngineConfig → InferenceEngine 实例 → Reasoner(engine)（ReGraphT 系另挂 ReGraph）→ Executor(agent) → run(kernels) → 每个 kernel: reasoner.optimize() → engine.generate(prompts, SamplingParams) → batch[{generation,…}]`。

构图侧链（上游）：`kernel.jsonl → reason()（大模型轨迹，\`\`\`json fence 正则抽取）→ relabel()（对齐图内方法词表）→ ReGraph.merge()（已有边加 example/缺节点建节点建边）→ save() JSON → 成为 run.py 的 --local_regraph_path`。图的 schema：`node[{index,name,in[],out[]}] + edge[{src,tgt,examples[]}]`，examples 携带 before/after 代码对——这就是"迁移"的全部载荷。

## ⑤ 复现要点（实测钉死，不是猜测）

1. **import 即崩**：`SamplingParams` 定义非法——`model: Optional[str] = None` 之后跟无默认值的 `temperature: float`，dataclass 规则直接 `TypeError: non-default argument 'temperature' follows default argument`（本地复现成功）。修法：删 model 默认值或给 temperature/max_tokens 补默认。
2. **开源快照不完整**：`reasoner/standard.py`、`cot.py`、`code_rag.py` 全是 **0 字节空文件**；`rethink_mcts.py`、`mcts_rag.py`、`ReGraphT_reasoner.py` **不存在**（但 `__init__.py` 照样 import）→ run.py 第 15-24 行必 `ImportError`。七个 reasoner 发布了骨架没发布肌肉。
3. **executor 同样残缺**：`executor/utils.py` 不存在（`load_*_eval_dataset` 无处可导）；`@register_executor` 注册 CUDAEval/ParEval 的子类全缺 → `EXECUTOR_REGISTRY` 空，`create_executor` 必 `KeyError`。
4. **五个死参数**：run.py 解析的 `--model/--temperature/--max_tokens/--top_p/--top_k` 从未传给 EngineConfig 或 reasoner——按意图应是 SamplingParams 来源，接线被裁掉了。
5. **环境变量**：remote 引擎需 `OPENAI_API_KEY`（openai SDK 隐式读）；构图需 `OPENAI_API_KEY`+`BASE_URL`+`LOG_PATH` 三个 env，且 `LOG_PATH` 文件必须预先可写（`logging.basicConfig(filename=…)` 在 import 时执行）。
6. **模型需求**：local 路线要 GPU + vLLM + 本地模型路径；remote 路线任意 OpenAI 兼容端点；构图默认 `deepseek-chat`。
7. 小瑕疵：`--max_tokens` 默认 8196 是 8192 笔误；`top_k: float = 0.7` 类型与默认值都怪（vLLM 惯例 -1=关闭）；run.py/construct.py 全用 `if` 不用 `elif`（choices 约束下能跑）；remote_engine 的 `response` 迭代 bug（见③）。

## ⑥ 新人提示

**读码路线**：`ReGraph/ReGraph.py`（数据结构，221 行，图的全部语义）→ `prompt/ReGraph.py`（构图两提示词，理解"轨迹/重标注"协议）→ `construct.py`（图怎么长出来）→ `engine/` 三件（模型怎么被调）→ `run.py`（怎么串）。**心态预期**：这不是能 `pip install && run` 的仓库，是论文方法的协议规范+参考骨架——run.py+engine+ReGraph+construct+prompt 五件是完整的"协议层"，七 reasoner 中五缺三空、executor 实现全无，复现论文数字需自己按 `optimize(kernel)→dict` 和 `run(kernels)` 契约补齐。**最快上手实验**：先修 SamplingParams 两行 → 补一个 30 行的 StandardReasoner（REGRAPHT prompt 已在 `prompt/agent.py` 备好）→ remote 端点指向任意 OpenAI 兼容服务，即可打通最小闭环。**最值得学的**：微注册表 + abc 的插件骨架，和 `rollout/generate_available_actions` 这对"LLM 引擎即搜索环境"的接口设计。

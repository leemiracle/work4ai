# 10 · x-router 复杂度分类：五档契约与启发式兜底

## ① 角色定位

x-router 的决策前提是「这个请求有多难」：先把会话分进五档复杂度之一，再按档位路由（本地/云边界）。`complexity.py`（302 行）定义五档、冻结的分类 prompt、严格输出解析与模型-free 的启发式分类器；`classifier/engine.py`（177 行）是加载运行小模型的执行器。两文件构成「问题与读法固定、模型可换」的结构——docstring（`complexity.py:1-7`）明说：prompt 模板、preview 规则、启发式阈值**全部冻结**——分类器是 stock 小模型没有 checkpoint 契约，这些文本就是决定其行为的全部，改任何一个都会让 benchmark 不可比（DESIGN.md §4）。

五档定义在 `types.py:74-86` 的 `ComplexityLevel(IntEnum)`：SIMPLE=1、MEDIUM=2、COMPLEX=3、RESEARCH=4、REASONING=5。docstring（`types.py:77-80`）点睛：「排序就是全部意义——路由就是把分类档位与本地能力边界做比较」，IntEnum 让比较免费。

## ② 内部结构

**complexity.py 的四层**：

1. **来源常量**（`complexity.py:34-38`）：SOURCE_LLM / SOURCE_HEURISTIC / SOURCE_HEURISTIC_FALLBACK / SOURCE_PARSE_FAILED / SOURCE_UNAVAILABLE 五个码写进 Decision.reasoning——分类器健康度从路由遥测即可看，不用另开监控。
2. **冻结 prompt**（`:43-59`）：PROMPT_TEMPLATE 给五档各一句判据（SIMPLE=直答不动手、MEDIUM=有界起草/编辑/计算、COMPLEX=多步交织规划实现、RESEARCH=多源搜集综合、REASONING=多跳推理/形式证明为核心），并冻结 locality 规则（`:53`）：SIMPLE/MEDIUM 属本地档，其余属云档；需要网络/外部源/远程 API 就是云档，但「写将来会调 API 的代码」不算。「分剩余步骤而非整个任务、工具存在与否不影响档位」也在 prompt 里冻结（`:54`）。
3. **统一文本视图**（`:109-216`）：`content_text`（`:117-136`）把 string 或 OpenAI 式 content-parts 列表都展平成文本（协议层只收字符串，直递分类器的消息可能还带列表形态）；`_is_scaffolding`（`:139-150`）滤掉 system 消息与 harness 注入的 `<system-reminder>` 块——它们描述笼架不描述任务；`conversation_messages`（`:167-183`）产出 (role, text, tool_calls) 过滤视图，**preview 与启发式都从这里出发**——两条路径看到的文本永远一致（`:170-173`）。`conversation_preview`（`:197-216`）取最近 WINDOW=6 条（`:41`），关键补丁（`:203-210`）：agent 循环尾部常全是 assistant/tool 流量，任务会掉出窗口——强制把最近一条 user 提回窗首。超长走 `_bounded_text`（`:186-194`）**中间截断**，保住任务定义与最新进展。
4. **双分类器**：`parse_complexity`（`:228-234`）用 `re.fullmatch`（`:63`）要求整串恰好一个标签——散文或多标签是漂移，不是要弥缝的解析问题。`classify_heuristic`（`:237-266`）纯关键词+阈值链：REASONING 关键词（`:66-74`）→ RESEARCH 关键词或 token>1200（`:75-88`）→ COMPLEX 关键词或 token>400/用户轮>6/工具深度>2/问号>3（`:89-95`）→ MEDIUM 关键词或 token>80/用户轮>2（`:96-101`）→ SIMPLE。总入口 `classify`（`:269-294`）永不抛异常、只降级：无后端/后端异常/解析失败分别落 SOURCE_HEURISTIC/FALLBACK/PARSE_FAILED，`_safe_heuristic`（`:297-302`）连启发式都崩则 MEDIUM+SOURCE_UNAVAILABLE。docstring 立了不对称原则（`:271-275`）：**任何失败路径都不得产生比分类器更高的档位——坏掉的分类器绝不能引发升级**。

**engine.py——懒加载执行器**：`ClassifierEngine` 构造廉价（`engine.py:37-53` 只存参数与锁），`load`（`:57-97`）双检锁懒加载，重 import 全在方法内（`:7-9` 注释：`import openjiuwen` 不得拖进 torch，且未装 x-router extra 时本模块也可导入——**配置错误先于模型加载暴露**）。`:76-88` 两处刻意选择：用 transformers 5 的 `dtype` 拼法（4.x 的 `torch_dtype` 会被静默忽略，extra 钉 >=5.0 正为此）；先加载到主机内存再 `.to(device)` 而非 `device_map`——注释给出实测依据（safetensors 逐 shard mmap 下两者峰值 RSS 与加载时间相同，后者白加 accelerate 依赖）。`build_prompt`（`:118-136`）`enable_thinking=False` 压制 Qwen3 系思考块（`:19-22` 预置 `_EMPTY_THINK` 兜底老模板）；`generate`（`:138-171`）temperature=0 贪心解码——注释（`:141-145`）：同 prompt 必须返回同标签，推理栈在这点上行为不一，这也是分类器本地自持的理由；输入按 `max_input_tokens` 截断（`:149-154`）。

## ③ 外部连接

`classifier/backend.py` 的 `LocalBackend`（`backend.py:19-38`）把 engine 适配成 `ComplexityBackend` 协议（classify+warmup），`backend_from_config`（`:41-73`）读 `[x_router.classifier_model]` 段——**缺段是错误**（`:53-58` 的报错给两条出路：给 model_path 或显式 `enabled = false`），只有显式 false 才返回 None 走纯启发式。这是已知勘误的实锤：**无分类器必须显式 `enabled = false`，否则启动即失败**（pyproject.toml:12-14 注释同义）——理由在 docstring（`backend.py:45-52`）：缺模型静默回退会造出「看着健康、其实从不升级」的路由器。消费侧：`algorithm.py` 每 request 调 `classify`；`facade.py:214-219` 装配时 warmup——请求期失败是**有意**降级，所以加载不了的模型必须在校时炸出来。`service.py:97-108` 复用 `conversation_preview` 作 bandit 检索文本（同一视图原则）。判定链下游 `decide_by_tier`（`algorithm.py:29-60`）：`tier <= local_capability` 走本地，目标被排除降级本地，否则按档选云模型。

## ④ 数据流

请求进来：messages → `normalize_messages`（facade.py:81-102）→ `classify(messages, params)`：后端在则 `build_classifier_request`（`complexity.py:219-225`）→ `LocalBackend.classify` → `engine.classify_text`（engine.py:173-177）→ 16 token 贪心生一个词 → `parse_complexity` fullmatch → (tier, SOURCE_LLM)；任何一环异常降级启发式。tier 与来源码进 Decision.reasoning（`tier=X ... source=Y`），供 `parse_reasoning`（service.py:128-133）回读。同一条 preview 文本同时被 bandit 臂拿去查近邻（11 篇）。

## ⑤ 设计决策与权衡

1. **冻结即契约**：五档判据、关键词表、阈值、WINDOW 全部写死并声明不可改（`complexity.py:3-6`）。换模型可以，换尺子不行——尺子一换，存量观测与新旧 benchmark 全部作废。bandit 的 quality 均值同理（judge 权重也是冻结的），两者共同构成「可跨时间比较」的地基。
2. **降级只降不升**（`:271-275`）：失败安全方向 = 不升级。错把难题分简单损失质量（可由 bandit 事后纠正），错把简单题分复杂烧云钱且不可逆。不对称成本结构决定了不对称的错误策略。
3. **fullmatch 拒绝宽容解析**（`:63`/`:228-234`）：分类器输出啰嗦就判 PARSE_FAILED 落启发式，而不是从散文里抠标签——漂移要暴露不要弥缝，这决定分类器健康可观测。
4. **最新用户消息保底**（`:203-210`）是 agent 场景特化的典型：通用「取最近 N 条」在 ReAct 循环里会把任务本体挤掉，这一行补丁让分类器永远看得到「要干什么」。
5. **本地自持模型 vs 远程 API**：engine 注释（`:141-145`）给出本地派理由——temperature=0 语义在推理栈间不统一，本地 generate 保证贪心。代价是每宿主占一份显存，多宿主共享需另配 HTTP classifier server（engine.py docstring `:3-5` 提及该形态）。
## ⑥ 新人提示与坑

- **无模型跑 x-router 必须显式声明**：配置里写 `[x-router.classifier_model] enabled = false`，报错文案见 `backend.py:55-58`。README 目录树还漏了 `config/stage_router.toml`（已知勘误），对着 README 找配置文件会缺一份。
- **启发式阈值是契约的一部分**：`classify_heuristic` 里的 1200/400/80 token 阈值与关键词表「看起来可以调」——不可以，动了就破坏可比性（`:239` 注释明示）。
- **RESEARCH/REASONING 关键词是英文的**（`:66-88`）：中文请求的启发式分类基本走 token 数与轮数通道，命中关键词档的概率低——启发式兜底对中文会偏保守（易落 MEDIUM/COMPLEX），主路径仍应配模型。
- **`content_text` 丢非文本 part**（`:133-135` 只取 type=="text"）：多模态消息的图片部分对分类器不可见，这是有意的（x-router 只读文本）。
- **改 PROMPT_TEMPLATE 前三思**：它是冻结契约（DESIGN.md §4），PR 里改一行模板等于作废全部历史 benchmark 与 bandit 观测的可比性。

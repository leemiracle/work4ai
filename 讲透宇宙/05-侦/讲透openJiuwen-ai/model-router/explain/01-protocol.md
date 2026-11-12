# 01 · crates/protocol/src/：零依赖词汇表为何是架构基石

## 一、角色定位：整个仓的"宪法"

如果把 model-router 比作一个五层法庭，`crates/protocol/src/` 就是 L1 宪法层——它定义了所有层对话时使用的全部名词：请求长什么样（`request.rs`）、决策长什么样（`decision.rs`）、结果反馈长什么样（`feedback.rs`）、状态快照长什么样（`state_view.rs` / `state_query.rs`）、训练样本长什么样（`training.rs`），以及出错时怎么说（`error.rs`）。`lib.rs:1-3` 的模块文档一锤定音："零依赖底座——只有数据、没有行为。其他 crate 只经本层对话；任何一层可独立替换。"

这句话的实证在 `crates/protocol/Cargo.toml`：`[dependencies]` 段是**空的**（仅位于 workspace 声明之后，无任何条目）。连 serde、toml 这种 Rust 生态标配都没有。这是有意为之的架构决策：协议层一旦依赖任何外部库，它的编译产物就会牵着所有下游 crate 走，"任何一层可独立替换"就成了空话。零依赖还带来一个副产品——协议层是全仓编译最快的单元，且永远不会因为依赖升级而 break。

数据流方向上，protocol 处于所有箭头的起点和终点：宿主构造 `RouteRequest` 进来，算法返回 `Decision` 出去，宿主再拿 `Feedback` 回来。state、algorithms、runtime、py 四个 crate 全部 import 它（如 `crates/state/src/state_provider.rs:6-8`、`crates/algorithms/src/algorithm_provider.rs:15-17`），而它谁也不 import。这个"只被依赖、不依赖人"的形态，就是词汇表的形态。

## 二、内部结构：八个文件的词汇分工

### request.rs（108 行）——路由请求侧

- `ToolCall`（`request.rs:7-10`）：算法能看到的工具调用，只有 `name` 和可选 `command`。注意它是被"削减"过的投影——真实工具调用的参数、结果都不进协议，协议层只搬运"路由所需的信号"（`request.rs:12` 注释）。
- `Message`（`request.rs:13-18`）：`role` + `content` + `tool_calls`。role 是裸 String 而非 enum，这是刻意的松约束：宿主的 role 词汇表（user/assistant/tool/system/developer...）由算法自行解释。
- `RequestMetadata`（`request.rs:21-25`）与 `RoutingKey`（`request.rs:37-41`）：`(session_id, agent_id)` 二元组构成状态快照的键空间。`routing_key()` 方法（`request.rs:28-34`）把 Option 字段降级为空串——键永远存在，只是可能为空。
- `TargetSet`（`request.rs:44-72`）：可选目标的语义名集合。两个关键方法：`first()`（L57）给 stage_router 之类"取第一个"的算法用；`without(exclusions)`（`request.rs:62-71`）做排除过滤且**保持原顺序**——顺序语义后面会被 stage_router 的"第一个是 efficient、第二个是 capable"约定（`config/stage_router.toml:1` 注释）复用。
- `RouteHint`（`request.rs:81-93`）：每请求输入。注意 `request.rs:80` 的注释——因为 `StateQuery` 携带 `Vec<f32>` 浮点向量，本结构体**只派生 `PartialEq` 不派生 `Eq`**（浮点无全序）。这是全协议层唯一一处 Eq 的缺口，Rust 类型系统在替你记住"这里有浮点"。
- `RouteRequest`（`request.rs:96-108`）：消息 + 元数据 + `exclusions`。注释明确 exclusions 由**宿主重试逻辑**填写（`request.rs:95`）——重试语义被推到宿主侧，协议只运输。

### decision.rs（26 行）与 selection.rs（31 行）——决策侧的一对双胞胎

`Decision`（`decision.rs:4-14`）是算法的返回值：`selected_model_id` + `reasoning`（**必填**，`decision.rs:3` 注释"每个决策可解释"）+ `is_answer_call` + `route_id`。`decision.rs:10-11` 记录了一个历史收敛："本架构已收敛为仅应答，默认 true"——字段保留是为了与 Switchyard 同构（`decision.rs:1`），但语义上只剩一个值。

`ModelSelection`（`selection.rs:8-14`）字段与 Decision 完全相同，区别写在 `selection.rs:3-4`：`Decision` 是 runtime 内部返回值，`ModelSelection` 是"跨边界规格"——凡是要跨出 Rust 内核（给 PyO3、给宿主插件）的地方，一律转成 ModelSelection（`From<&Decision>` 实现在 `selection.rs:16-25`）。同一个数据的两种身份，用类型隔离了"内核内部"与"对外承诺"。

### feedback.rs（464 行）——全协议层最大最精密的文件

这是协议层的预算执法中心：

- `Outcome`（`feedback.rs:6-11`）：Ok / Overflow / Unavailable / Rejected 四态。注释（`feedback.rs:1`）强调"语义失败不在此列"——模型答得不好不算 Outcome，只有调用层面的成败才进反馈。
- 预算常量：`VALUE_MAX_BYTES = 65_536`（`feedback.rs:14`）、`MAX_EXTENSIONS = 32`（L15）、`VALUE_MAX_DEPTH = 8`（L21）、`VALUE_MAX_ELEMENTS = 256`（L22）。
- `Value` 枚举（`feedback.rs:69-78`）：一个**手写的 JSON 子集**。为什么不直接用 serde_json？`feedback.rs:66-68` 注释给出答案："协议层零依赖，故自定义实现"。它的校验器 `validate_inner`（`feedback.rs:112-156`）同时累计三个预算：字节（字符串按 UTF-8 长度计，其他节点每个 8 字节，L118-121）、深度、元素数；并拒绝非有限浮点（L134）、i64 越界、对象重复键（L143-148）。字节口径注释（`feedback.rs:13`）特意说明"非 JSON 编码长度"——预算按节点开销相加，不是序列化后的尺寸。
- `Extension`（`feedback.rs:170-175`）：宿主任意扩展载荷，`(schema, version, data)` 三元组。`feedback.rs:169` 注释声明最小版本**不做 schema 注册表**——未知 schema 也透传并校验，"明确不承诺语义"。
- `Feedback`（`feedback.rs:207-217`）：反馈主体。三个构造器体现"缺失表示未知"的统一约定：`ok()`（L223，成功调用）、`delayed()`（L241，`call: None` 表示结果未可知）。`validate()`（`feedback.rs:259-275`）先查协议版本 `FEEDBACK_VERSION`（L18，当前为 1），再查扩展条数，最后把**所有扩展的预算加在一起**算总账——单条合法但合计超限照样拒绝（测试 `extension_budget_includes_schema_and_is_cumulative`，`feedback.rs:433-463` 实证了预算跨扩展累加而非逐条重置）。

### state_view.rs（27 行）与 state_query.rs（341 行）——状态读取的双通道

`StateView`（`state_view.rs:10-15`）极简：`affinity`（亲和提示）+ `exclusions`（排除列表）+ `stats.sample_count`（样本计数）。文件头注释（`state_view.rs:1`）是全仓反复出现的哲学："算法必须能在空视图下降级为冷路由"。

`StateQuery`（`state_query.rs:31-38`）是 `snapshot` 的平级可选扩展（`state_query.rs:1-4`），字段全 Optional：`text` / `vector`（二选一或同时）/ `top_k` / `extensions` / `route_id`。四条硬上限：`QUERY_MAX_TEXT_BYTES = 16_384`（L12）、`QUERY_MAX_VECTOR_DIMS = 4_096`（L13）、`QUERY_MAX_TOP_K = 256`（L14）、`QUERY_MAX_RETRIEVED = 256`（L17）。`route_id` 的注释（`state_query.rs:26-30`）值得细读：它**由 runtime 注入**，宿主填了也会被覆盖，作用是把"检索时看到的上下文"与"之后到达的反馈"对上号；且 `is_empty()` / `validate()` 都无视它（L70-75、L82-121 均不触及该字段）。

返回侧 `StateSnapshot`（`state_query.rs:150-154`）= `view`（与 snapshot 同构）+ `retrieved`（命中列表）。`RetrievedItem`（L128-133）的 `data` 复用 `Value` 的同一套预算。`StateSnapshot::validate()`（L181-198）是防御性校验：条数、分数有限性、载荷预算。`StateQueryError::Backend`（L217）单列了"实现侧自身失败（如跨语言桥接调用异常），runtime 会回退到 snapshot"。

### training.rs（273 行）与 error.rs（29 行）

`TrainingPrompt`（`training.rs:35-44`）把 `请求 → 决策 → 反馈` 组装成一条训练样本，三元组均可选（`training.rs:4-7` 的文档把为什么讲透了：单条 Feedback 只说明"选了谁、结果如何"，不含"问了什么"与"为什么选"）。同时支持宿主直接给渲染好的 `text`。上限四条：`TRAINING_MAX_PROMPTS = 1_024`（L18）、`TRAINING_MAX_TEXT_BYTES = 65_536`（L20）、`TRAINING_MAX_MESSAGES = 256`（L22）、`TRAINING_MAX_MESSAGE_BYTES = 65_536`（L24）。

`RouterError`（`error.rs:7-13`）四态：Config / Algorithm / State / NoTarget。`error.rs:1` 的注释划出关键界线："装配期错误在启动时暴露；决策期错误可回退。"——Config 错误该 panic 级处理，NoTarget 是运行期正常分支。

## 三、外部连接：被谁消费

protocol 是全仓唯一"入度为零"的 crate（除 workspace 本身）。四个消费者：

1. **state crate**：`state_provider.rs:6-8` 引入 `Feedback, RoutingKey, StateQuery, StateQueryError, StateSnapshot, StateView`——trait 签名的全部词汇。
2. **algorithms crate**：`algorithm_provider.rs:15-17` 引入 `Decision, RetrievedItem, RouteRequest, RouterError, StateView, TargetSet`——`RouteContext`（L21-33）就是这些类型的打包。
3. **runtime crate**：`router.rs:9-12` 引入 7 个类型；`decide_loop.rs:3-5` 同时引 protocol 与 algorithms 的类型缝合决策循环。
4. **py crate**：`convert.rs`（903 行，全仓最大的转换层）把 PyO3 对象逐字段翻成 protocol 类型再翻回去。

反向依赖为零。这就是"词汇表"的验证标准：改 protocol 会让全仓重编译，改任何其他 crate 不动 protocol 一行。

## 四、数据流：一次路由经过的协议类型

以一次带检索意图的路由为例：

1. 宿主构造 `RouteRequest`（messages + metadata + exclusions）和 `RouteHint`（cache_affinity + `StateQuery`）；
2. runtime 生成 `route_id`（`router.rs:125`），经 `decide_loop.rs:25` 的 `with_route_id` 注入 `StateQuery`；
3. state 收到带 route_id 的查询，返回 `StateSnapshot`（view + retrieved）；
4. runtime 把 view.exclusions 并入请求 exclusions（`decide_loop.rs:52-54`），过滤出 `TargetSet`，打包进 `RouteContext`；
5. 算法读 ctx 返回 `Decision`（不知 route_id）；
6. runtime 把 route_id 写回 Decision（`router.rs:136`），跨边界时投影为 `ModelSelection`；
7. 宿主调用模型后构造 `Feedback`（带同一 route_id）回传，`Feedback::validate` 把关后写入 state，成为下一次 `StateView` 的素材。

route_id 是这条链的线：StateQuery.route_id（`state_query.rs:37`）→ Decision.route_id（`decision.rs:13`）→ Feedback.route_id（`feedback.rs:211`）三点一线，而**算法全程接触不到它**（`decide_loop.rs:36-37` 注释）。

## 五、设计决策与权衡

**为什么零依赖（连 serde 都不用）？** 代价是手写 `Value` 枚举与 464 行的校验逻辑。收益有三：编译隔离（下游永不因协议层依赖升级而重建）、跨语言对称（Python 侧不需要理解 serde 的序列化怪癖，只对齐字段语义）、以及**预算口径完全自控**——serde_json 的 Value 没有深度/元素数预算概念，自己写才能精确执行"每个节点 8 字节"的计费（`feedback.rs:118-121`），并有测试钉死边界行为（`feedback.rs:411-430` 专测"恰好 max 通过、再+8 超限"）。

**为什么 reasoning 必填？** 每个决策可解释（`decision.rs:3`）。stage_router 的 reasoning 会输出 `source=override score=... confidence=...`（`stage_router/mod.rs:188-193`），x-router 输出 `rule=... tier=... source=...`（`x_router/algorithm.py:118-120`）。可解释性被写进类型而非文档。

**为什么 Decision 与 ModelSelection 分家？** 内部类型允许携带不变量（如 route_id 只能由 runtime 填），对外投影是纯数据承诺。这防止宿主依赖内核实现细节——投影类型可以加字段、加序列化，而 Decision 保持自由。

**砍掉了什么？** schema 注册表（`feedback.rs:169` 明确不做）、Outcome 的语义失败态、Message 的多模态 content（Python 侧 facade.py 的 `normalize_messages` 负责拍平，`facade.py:19-24` 的 docstring 讲了为什么必须做：协议只收 str，多模态列表直传会 raise，宿主降级本地模型"看起来健康其实全本地"）。

## 六、新人提示与坑

1. **Value 的字节预算是"节点开销"不是 JSON 长度**（`feedback.rs:13`）：字符串按 len()，容器每个 8 字节，schema/version 字节也计入。手算预算时别用 `len(json.dumps(...))`。
2. **Feedback 预算跨扩展累加**：三条各 40KB 的扩展单条都合法，合计 120KB 超过 65_536 会被拒（`feedback.rs:453-462` 测试实证）。
3. **StateQuery.route_id 是 runtime 的私产**：宿主自己填的值会被 `decide_loop.rs:25` 覆盖，别指望它传自定义关联 id。
4. **RouteHint 无 Eq**：`Vec<f32>` 导致只 PartialEq（`request.rs:80`），想拿它做 HashMap 键的人会撞墙。
5. **`is_answer_call` 是化石字段**：架构已收敛为仅应答（`decision.rs:10-11`），读到它别以为还有"非应答调用"分支。
6. **改 protocol 的成本最高**：任何字段变更会级联到 state/algorithms/runtime/py 四个 crate 与 Python 侧的 `_openjiuwen.pyi` 类型桩（`python/openjiuwen/_openjiuwen.pyi:1`，.pyd 二进制不在仓、.pyi 是 IDE 跳转的唯一依据）。新增字段时先想清楚是否所有消费方都愿意跟着动。

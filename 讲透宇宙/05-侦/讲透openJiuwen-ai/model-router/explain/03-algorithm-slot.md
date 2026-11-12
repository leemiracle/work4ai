# 03 · crates/algorithms/src/：算法槽契约与纯函数纪律（algorithm_provider.rs + evolving_provider.rs + lib.rs）

## 一、角色定位：决策智能的唯一合法居所

L3 算法层回答一个问题："选哪个模型？"整个仓里允许有"智能"的地方只有这一层的两个 trait：`AlgorithmProvider`（在线决策）与 `EvolvingProvider`（离线自演进）。其余各层都是管道与执法——protocol 定词汇、state 管记忆、runtime 做装配与循环、py 架桥。

`lib.rs:1` 把层的组织原则写在一行："公共插件契约与测试实现分离。"本 crate 的三个核心文件恰好是三层递进：`algorithm_provider.rs`（46 行，在线决策契约）、`evolving_provider.rs`（122 行，离线训练契约）、`lib.rs`（28 行，feature 门控与兼容导出）。具体算法（stage_router、test_algo 家族）在子目录，属另一篇的故事。

与 state 层对位是刻意的结构性呼应：一个槽管"怎么选"，一个槽管"记住什么"，都是 `运行期单槽选一`（`algorithm_provider.rs:35` 注释原话"与 state 侧 `StateProvider` 对位"），都由 profile 按名字装配，都可被 Python 实现替换。

## 二、内部结构

### algorithm_provider.rs：46 行的在线决策契约

**三条边界**（`algorithm_provider.rs:5-13` 模块文档，按重要性排序）是这一层的灵魂：

1. **不得调用被选中的目标模型。** "决策止于返回 `Decision` 里的 `selected_model_id`；调用目标模型由宿主（runtime / host）负责。"这是决策与执行分离的核心。
2. **可以自带决策辅助模型**（如复杂度分类器），它服务决策本身，与第 1 条不冲突——x-router 的本地 Qwen3-0.6B 分类器就是这条的合法应用。
3. **调用应尽量保持无状态纯调用**——无论自带还是外部辅助模型，都避免在调用链引入可变状态（缓存、会话粘性），"以免削弱可重放性"。

注意第 3 条的措辞（`algorithm_provider.rs:11-13`）："这是**实现者自身的责任**，框架不强制约束。"框架无法阻止你在自己模块里存状态，所以纪律写成文档而非运行时检查。Python 侧契约把这段一字不落地复述了一遍（`python/openjiuwen/algorithm_provider.py:6-20`），并补上关键一句："把它写成纪律要求，而非运行时校验。"

**`RouteContext`（`algorithm_provider.rs:20-33`）**——注入给算法的只读上下文，四个字段：

- `targets: TargetSet`——"本次可选目标（已剔除 exclusions）"，注意 runtime 已替你过滤过一遍（`decide_loop.rs:52-56` 把请求 exclusions 与 state exclusions 合并过滤），算法再做 `without()` 是处理剩余边界（stage_router 直接用 first/get(1)，passthrough 系再做一次防御性 without）；
- `view: StateView`——状态提示，"可为空，算法必须能降级"；
- `retrieved: Vec<RetrievedItem>`——检索命中，"宿主未发起检索、或 state 未实现 query 时为空"，"算法必须能在空命中下降级为冷路由"；
- `seed: u64`——"随机性显式注入，保证可重放"。需要随机性的算法必须从这里取种子，不允许自己 `thread_rng()`。

这个结构是"算法能看到的世界"的完整清单：没有时钟、没有网络句柄、没有 route_id、没有自身历史。世界越窄，纯函数越可信。

**`AlgorithmProvider` trait（`algorithm_provider.rs:36-46`）**：

```rust
pub trait AlgorithmProvider: Send + Sync {
    fn name(&self) -> &str;
    fn decide(&self, request: &RouteRequest, ctx: &RouteContext)
        -> Result<Decision, RouterError>;
}
```

`name()` 要求"稳定的低基数名称，用于注册表与遥测"（L37-38）——低基数（有限的、可枚举的名字集合）是遥测标签的硬要求，名字会进 registry 的 match 臂（`runtime/src/registry.rs:13-29`）与 Python 注册表。`decide()` 是单步纯函数：读请求与快照，返回决策；错误只剩 `RouterError`（没有可用目标用 `NoTarget`）。

### evolving_provider.rs：自演进的另一半

在线决策之外，架构给"算法会变好"留了通道。`evolving_provider.rs:1-4` 的定位："纯计算、无 I/O。拉数据 / 调度 / CAS 写回由 runtime `TrainingJob` 履行。"——fit 是纯的，脏活归 runtime。

**`TrainingBatch`（L17-21）**是双通道输入容器：

- `feedbacks: Vec<Feedback>`——"仅含结果反馈的旧通道，向后兼容"；
- `prompts: Vec<TrainingPrompt>`——"带『请求 → 决策 → 反馈』三元组的富样本，供无法只凭反馈建模的算法使用（如需要原始 prompt 做 embedding 或监督信号）"（L13-15）。

注释（L16）说清了两通道的关系："两者可同时非空；算法按需读取，缺失时降级（**空批次是合法输入**）。"`validate()`（L45-56）检查 `TRAINING_MAX_PROMPTS = 1_024` 上限并逐条校验。为什么需要 prompts 通道？`runtime/src/training.rs:10-17` 给出数据来源的产权划分：feedbacks 来自 StateProvider（hint 层只存聚合反馈）；prompts 必须由**宿主 journal** 提供——"runtime 在 route 时不落盘决策与请求"，宿主在调用模型后生成三元组交进来，"这也是唯一能拿到原始 prompt 文本的地方"。

**`Artifact`（L59-64）**：`{kind, payload: Vec<u8>}`——"不可变新参数集快照，可多版本共存"。不可变性让回滚与 A/B 成为可能：新旧工件并存，state 的 publish 按版本号 CAS 切换。

**`EvolvingProvider` trait（L66-73）**：`name()` + `fit(&self, batch) -> Arc<Artifact>`。"单步重算。同输入必同输出；不允许 I/O。"（L71）返回 `Arc` 是为了让工件零拷贝共享。注释点明它与路由槽的差别："与路由侧 `AlgorithmProvider` 对位，但**不占路由单槽**"（L66）——一台路由器同时只能有一个决策算法，但可以挂多个演进任务。

### lib.rs：feature 门控与兼容层

`lib.rs:5-6` 的 `#[cfg(feature = "algo-stage_router")]` 是关键一行：stage_router 与五个 test_algo 一样按 feature 条件编译。workspace 根 `Cargo.toml:26` 定下了重要约束——runtime 依赖 algorithms 时 `default-features = false`，每个算法由 runtime 的 feature 透传（`crates/runtime/Cargo.toml:18-23` 的 `algo-stage_router = ["openjiuwen-algorithms/algo-stage_router"]`）。**编进产物的算法集合是构建期决策**：嵌入式部署可以只带 passthrough，砍掉一切多余代码。

`lib.rs:13-28` 两个兼容模块（`pub mod algorithm`、`pub mod evolving`）保留旧路径导出，注释统一口径："新代码应从 crate 根导入契约。"`#[doc(hidden)]`（L23）把它们从文档里藏起来。

## 三、外部连接

- **上游**：只依赖 protocol（`algorithm_provider.rs:15-17`、`evolving_provider.rs:8` 引入的类型全部来自 `openjiuwen_protocol`）。
- **runtime 消费**：`registry.rs:3-4` 引入 test_algo 样本与 trait，`create_algorithm`（L12-30）按名实例化；`decide_loop.rs:3` 引入 `AlgorithmProvider, RouteContext` 构造上下文并调 decide；`training.rs:5` 引入 `Artifact, EvolvingProvider, TrainingBatch` 驱动 fit。
- **py 消费**：`py/src/adapter.rs` 把 Python 算法适配成 `Box<dyn AlgorithmProvider>`；`py/src/lib.rs:100-103` 的装配顺序是 **Python 注册表优先、Rust registry 兜底**——这决定了 Python 侧注册同名算法能覆盖 Rust 内置。
- **Python 对位契约**：`python/openjiuwen/algorithm_provider.py` 是本文件的 Python 镜像，但机制不同——Rust 靠 registry match 臂，Python 靠 `__init_subclass__` 在**类定义时**自动校验并注册（`algorithm_provider.py:74-76`）：必须实现 decide、必须设非空 name、必须无参构造（L44-57 的 `_validate`），"配置放在类属性上，不要靠构造参数"（模块 docstring）。若 native 扩展未构建，类先进 `_pending` 队列，等 `bind_register` 注入登记函数后再补交（L32-41）。

## 四、数据流：decide 的一次调用与 fit 的一次批量

**在线**：宿主 → `Router::route`（生成 seed 与 route_id）→ `decide_loop::run` 组装 `RouteContext{targets(已过滤), view, retrieved, seed}` → `algorithm.decide(req, &ctx)` → `Decision`。算法的全部宇宙就是 req + ctx 两个只读引用；它返回的 route_id 恒为 None（由 runtime 在 `router.rs:136` 回填）。

**离线**：触发器（`runtime/src/trigger.rs` 的 TriggerSpec：Startup/Delay/Interval/Cron/Threshold/Event/Composite）唤醒 `TrainingJob`（`training.rs:50-61`）→ `DataSelector::select()` 组 batch（骨架是宿主 prompts 的透传，`training.rs:35-39`）→ `evolving.fit(&batch)` 纯计算 → `Artifact` 经 `publish(slot, artifact, expected_version)` CAS 写回 state → 下个版本的决策参数生效。"判定在 runtime，不进算法"（`trigger.rs:1`）——算法连"何时训练"都不知道。

## 五、设计决策与权衡

**为什么 decide 是纯函数？** 可重放性（同 `(request, ctx)` 必同 `Decision`，`algorithm_provider.rs:3`）带来三个工程红利：测试无需 mock 时钟与随机数（seed 注入）；线上事故可以离线复现；A/B 对比两个算法时输入完全公平。代价是算法拿不到真实时间与自身调用计数——需要那些信息的决策要么编码进 messages（stage_router 的做法：从消息历史推断阶段），要么挪到 state 层。

**为什么纯度只写纪律不写校验？** Python 侧提供了 `check_purity`（`algorithm_provider.py:86-95`，同输入双调用比对输出）作为**验收辅助**，但它只是抽查工具。更深的一层在 x-router 的文档注释里（`x_router/algorithm.py:74-77`）：对带活分类器的算法，check_purity "没有有用的模式"——真实服务栈不完全贪心解码（有的钳温到小正值）、batch 推理非 bitwise 可复现，纯度检查会间歇性假失败；对打桩后端又恒通过、证明不了任何事。所以 x-router 的策略是**把确定性半场（`decide_by_tier` 真值表）单独抽出来直接测**。纯度契约与纯度测试的这道缝，是带 LLM 的算法特有的工程现实。

**为什么 Artifact 不可变 + CAS？** `evolving_provider.rs:59` 注释"可多版本共存"。可变参数集 + 并发训练任务 = 竞态地狱；不可变快照 + 版本号（`CasConflict.expected/actual`，`state_provider.rs:11-16`）把并发问题化归为一次原子比较。

**砍掉了什么？** trait 上没有 `init`/`warmup`/`shutdown` 生命周期（x-router 想要 warmup 只能靠 facade 在装配期手动调，`facade.py:217-219`）；没有 `params` 通道（槽要求无参构造，Python 侧用 `specialize` 生成带参数子类绕过，`x_router/algorithm.py:129-148`；facade docstring 承诺"当内核长出 `[algorithm.params]` 表，这些都会塌缩进 `Router.from_config`"，`facade.py:13-15`）。

## 六、新人提示与坑

1. **`ctx.targets` 已被 runtime 过滤过**：请求与 state 的 exclusions 都已应用。你的算法里的 `without()` 调用多数是防御性冗余（passthrough 系 stub 就都做了，无害）。
2. **随机性只许用 `ctx.seed`**：自己起 RNG 会在重放时对不上。目前内置算法没人用 seed，它是留给加权/探索类算法的。
3. **Python 算法注册发生在 import 时**：`import openjiuwen` 触发 `discover.install()`（`python/openjiuwen/__init__.py:164-167`）扫描子包；但 x-router 这种需要配置的算法 import 后是**未配置态**（`params = None`），必须先 `specialize()` 或 `build_router()`，否则 decide 直接抛 ParamsError（`x_router/algorithm.py:88-93`）。
4. **同名注册是覆盖语义**：Python 注册表"re-registering a name overwrites it"（`x_router/algorithm.py:137-139`），名字必须每部署唯一；Rust 侧则是 match 臂静态唯一，无此问题。
5. **空 TrainingBatch 合法**：写 fit 时别假设 prompts 非空；`TrainingBatch::is_empty()` 的分支要能产出有意义的空 Artifact（mf 骨架返回空 payload，`test_algo/evolving/mf.rs:11-17`）。
6. **EvolvingProvider 不占算法槽**：配置里 `[[evolving]]` 段（`config/cloud.toml:12-15`）声明的是训练任务，与 `algorithm = "..."` 的路由槽是两回事，别混。

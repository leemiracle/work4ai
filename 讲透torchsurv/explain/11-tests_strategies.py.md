# `tests/strategies.py`：hypothesis 属性测试的策略库

## 一、角色定位

一句话：定义 **hypothesis 组合策略（composite strategies）**，为属性测试随机生成"结构合法"的生存数据张量——样本量、事件指示、时间、评估时刻四类输入的随机性全部收口在这 107 行里。位于 **L4 测试体系层**，是 CHANGELOG 里被单列为版本特性的 hypothesis 属性测试的供给侧；固定样本单测覆盖不到的输入空间，由它驱动的随机化补位。

## 二、内部结构

四个 `@st.composite` 策略（`tests/strategies.py:7/39/58/80`）：

- **`survival_tensors`**（L7-36）：基础数据对 (event, time)。先抽样本量 n∈[10,100]（L19）；事件列表抽 n 个布尔后**强制下标 0 为 True**（L22-24）——这是对 `SurvivalInputs` "至少一个事件"校验（`tools/validators.py:127-128`）的策略侧镜像：保证任何随机样本都通过被测函数的入口校验，让属性测试测的是数学性质而非报错路径；时间抽 (1e-6, 1e6) 的有限正浮点、显式 `allow_nan=False, allow_infinity=False`（L27-33）。
- **`cox_log_hazard`**（L39-55）：`(n,)` 风险分，值域 [-50, 50] 禁 NaN/Inf（L48-54）；n 缺省自抽 [10,100]（L45-46），也可外部指定以配合 survival_tensors 的 n。
- **`weibull_log_params`**（L58-77）：`(n, 2)` 参数，两列都是 [-10, 10]（L67-76）——比 cox 的 ±50 收窄，因为 weibull 的 exp(exp(...)) 双重指数对大参数敏感，策略直接把数值爆炸风险挡在生成侧。
- **`new_times`**（L80-106）：在给定 time 的随访窗内抽评估时刻。退化防护 t_min≥t_max 时只回首个排序值（L91-92）；常规路径抽 m∈[1,10] 个浮点、上界取 `t_max - 1e-6`（L94-101）——这个 1e-6 边距是对 `NewTimeInputs` 左闭右开窗口（`tools/validators.py:311`）的策略侧对齐；最后 `unique(sort())`（L103）满足升序无重复约束，抽空时回落 `[t_min]`（L104-105）。

四个策略共同的设计词汇：**约束感知生成**——每个策略都把自己生成的数据约束在被测代码的合法输入域内，这是 hypothesis "valid-input generation"的最佳实践，避免测试火力浪费在"本来就该报错"的输入上。

## 三、外部连接

- **唯一消费者**：`tests/test_hypothesis.py`（图谱唯一出边）——L6-12 导入 `survival_tensors`/`cox_log_hazard`，并把 `weibull_log_params` 以 `weibull_log_params_strategy` 别名引入（与 conftest 的同名 fixture 区分）；六个测试函数分别以 `@given(...)` 挂策略：Cox 损失有限性（test_hypothesis.py:21）、Weibull 损失有限性（:32）、C-index 值域（:43）、AUC 值域（:56）、KM 单调性（:81）、Brier 值域（:92），全部 `@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])`（:22 等）。
- **与 conftest.py 的分工**：conftest 提供固定种子夹具（`survival_data` seed=42、`benchmark_loader` 等，`tests/conftest.py:21-68`），本文件提供随机域——图谱里两者同层但边不相通，一个服务确定性对拍、一个服务性质扫描。
- **被测对象**：经 test_hypothesis.py 间接覆盖 `loss/cox.py`、`loss/weibull.py`、`metrics/cindex.py`、`metrics/auc.py`、`metrics/brier_score.py`、`stats/kaplan_meier.py` 六个文件。
- **上游依赖**：仅 hypothesis 库（L4）与 torch（L3）。

## 四、数据流

一次属性测试的运行走读：pytest 收集 `test_cox_loss_finite` → hypothesis 引擎按策略树随机 draw：先 n=37，再 37 个布尔（强制首个 True）、37 个时间浮点、37 个风险分 → 作为参数注入测试体 → 测试体内部却有一步值得注意的替换：`torch.manual_seed(0); log_hz = torch.randn(n)`（`tests/test_hypothesis.py:26-27`）——策略抽出的 log_hz_vals 被**现场重生成**的 randn 覆盖，策略实际贡献的是 n 与 survival_tensors 的数据形态（Weibull 测试同款，L36-37）→ 调 `neg_partial_log_likelihood` → 断言 `torch.isfinite(loss)` → 若失败，hypothesis shrink 到最小反例再报告。

50 个 example × 6 测试 = 每次全量跑约 300 次随机调用，覆盖 n、事件模式、时间分布的联合空间——这是固定 seed=42 的 conftest 数据（单一 n=64 样本点）做不到的。

## 五、设计决策

**为什么值域收窄而不是全实数？** hypothesis 默认会主动生成边界值与 NaN/Inf 等毒输入；本仓被测函数的契约里这些输入本就该被 validators 拦（错误路径已有 test_validators.py 专测），属性测试的兴趣点在"合法输入上的数学性质"。[-50,50]/[-10,10]/[1e-6,1e6] 是"合法域内足够野"的折中——既覆盖跨数量级时间，又不把火力浪费在必然爆炸的参数上。

**`new_times` 的 1e-6 边距（L97）**：直接抽到 t_max 会撞 NewTimeInputs 的右开窗口被拒——不是被测性质失败而是入口校验失败，hypothesis 会把它当"测试错误"处理。边距让随机时刻永远合法，校验语义的精确性转化成了策略里的一个常数，这是"契约漂移的编译期对齐"做不到时的务实补丁（校验改窗口语义时这行会静默失配，需人工同步）。

**批判视角**：① 测试体丢弃策略值、改用 `torch.randn(n)`（test_hypothesis.py:26-27、L36-37）意味着 `cox_log_hazard`/`weibull_log_params` 两个策略的**值域设计实际未生效**——它们退化为"样本量发生器"，[-50,50]/[-10,10] 的精心的数值边界是死配置；这不影响正确性（randn 的值域恰好温和），但让"策略约束数值爆炸"的设计意图落空，是策略库与测试体之间的一次实现漂移。② 50 examples 的量级对"有限性/值域"这类一票否决性质够用，对"分布正确性"类性质（如 KM 无偏性）远远不够——当前属性集停留在守门级。③ `survival_tensors` 强制 index 0 为 True（L23）会轻微扭曲事件比例的分布（首个样本永远事件），对值域类性质无感，对依赖事件占比的性质（若未来加）是隐性偏倚。

## 六、新人提示

- **上手顺序**：先读 `survival_tensors`（约束感知生成的范式），再对照 `test_hypothesis.py` 的六个 `@given` 看策略如何挂载；跑 `pytest tests/test_hypothesis.py` 观察 hypothesis 的随机与 shrink 行为。
- **坑 1**：给策略加新约束时先查 validators 的对应规则（两处必须同步漂移）——窗口、值域、至少一事件三类约束各有一对镜像（L23↔validators:127、L97↔validators:311、L29↔validators:37-40）。
- **坑 2**：**conftest.py 的夹具当前零消费**——`survival_data`/`cox_log_hz`/`benchmark_loader` 等在 tests/ 下 grep 不到任何测试函数引用（各测试模块自建数据，如 `test_cox.py:14-24` 模块级加载 JSON、test_cox.py:27-28 自设种子）；想复用固定种子数据别指望夹具，先确认它是否真的被谁用过。
- **坑 3**：本地复现 hypothesis 反例用其报告的 `@seed` 装饰器或 `.example()` 重放；随机失败不重现时先查是否 `suppress_health_check` 掩盖了 too_slow 数据。
- **坑 4**：新增属性测试优先挂现有四策略，只有新输入形态（如 strata、时变矩阵）才扩策略——策略库的增长速度是属性测试维护成本的领先指标。

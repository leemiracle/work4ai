# `src/torchsurv/loss/survival.py`：灵活生存模型——唯一需要数值积分的损失

## 一、角色定位

一句话：实现**无参数形式约束的灵活生存模型**——神经网络在离散评估时间网格上逐点直出连续 log hazard，损失用梯形法数值近似累积风险，是四族损失中唯一需要数值积分、也因此唯一原生支持时变协变量的成员。位于 **L1 生存分析损失函数层**，是 TorchSurv"无参数化约束"承诺的最纯粹落点：Cox 锁死比例风险、Weibull 锁死单调 hazard 形状，本文件的模型连 hazard 的函数族都不锁，`log h_i(t) = f_θ(x_i, t)` 直接学。

## 二、内部结构

264 行、3 个函数，短小但概念密度高：

- **`_cumulative_hazard_trapezoid`**（`src/torchsurv/loss/survival.py:16`）：核心积分器。先按 `respective_times` 决定输出形状——逐主体 `(n,)` 或全网格 `(n, m)`（L47-54）；主循环遍历每个观测时间（L56），用 `mask_time = eval_time <= new_time[t]`（L58）截取该主体观测时刻之前的网格段，`torch.exp` 恢复 hazard 后交 `torch.trapezoid`：逐主体分支在 L62（一维梯形）、全网格分支在 L65（`dim=1` 按行积分）；最后 clamp 到 `[0, 1e10]`（L67）。
- **`neg_log_likelihood`**（`src/torchsurv/loss/survival.py:70`）：训练入口。零事件/单样本 guard 与 Cox 同款（L156-161）；squeeze 后三连校验——`SurvivalInputs` + `ModelInputs(model_type="survival")`（要求 `(n, n_eval_time)` 2-D）+ `EvalTimeInputs`（列数与 eval_time 等长、严格递增）（L169-174）；累积风险一次算齐（L177）；事件项的 log hazard 用 `torch.searchsorted(eval_time, time[i], right=True) - 1` 取"不超过 T_i 的最近网格点"（L183）再 clamp(min=0) 防越界（L184）；NLL 合成 `-(event * log_hz_at_time) + cum_hazard`（L187）；reduction 分派 L189-196。
- **`survival_function`**（`src/torchsurv/loss/survival.py:199`）：外推入口，`S = exp(-∫h)`。仅过 `EvalTimeInputs`（L250），复用积分器默认 `respective_times=False` 出全网格，再 `torch.exp(-...)`（L252）。

与 `cox.py` 对照看结构：两者都有"零事件 guard → squeeze → validators → 主计算 → reduction"五段式，但本文件的主计算是一段 Python 循环里的积分，而非纯张量核——这是"网格化灵活性"换来的代价。

## 三、外部连接

- **imports 出边**：`tools/validators.py`（本文件 L11 引 `EvalTimeInputs`/`ModelInputs`/`SurvivalInputs`）。`EvalTimeInputs` 是本文件独有依赖——Cox/Weibull 的校验都不需要 eval 网格概念。
- **上游**：`src/torchsurv/__init__.py:9` re-export `neg_log_likelihood` 与 `survival_function` 两个符号；`docs/loss.rst`、`docs/notebooks/loss.md`（第 4 节）、`docs/notebooks/time_varying_covariates.md`、`docs/package_overview.md` 四处文档引用；`dev/run-doctests.sh` 会扫到本文件的 `__main__` doctest 块。
- **tested_by**：`tests/test_survival.py`（无 R 对拍——灵活模型在 R 侧无直接对应物，值正确性靠"若网络输出恰为 Weibull 形式的 hazard，NLL 应与 Weibull 闭式一致"这类等价性验证，即 `docs/notebooks/loss.md:153` 声言的性质）。
- **层内邻居**：`loss/momentum.py` 与本文件同层；`helpers_time_varying.py` 教程管线以时变长表喂本损失。

## 四、数据流

训练走读（以 `docs/notebooks/regression_time_varying.ipynb` 的 `(start, stop]` 长表场景为典型）：网络对每个主体输出 `log_hz (N, M)`——M 个列对应 `eval_time` 网格点（通常 `linspace(0, t_max)`）→ `neg_log_likelihood(log_hz, event, time, eval_time)` 入口 guard → 三连校验（形状错、网格不递增都在此报 ValueError）→ 积分器逐主体截网格、梯形积分得 `H_i(T_i)` → 事件项取左邻网格点的 log hazard（L183 的地板索引）→ 合成 NLL → mean。

注意数据流的隐含假设：`τ_1` 应取观测起点（常为 0，docstring L123-124 明说），且 T_i 落在两网格点之间时事件项用的是左邻值——网格越粗，事件项的量化误差越大（积分项有梯形修正，事件项没有）。这是"网格分辨率换计算量"的直接权衡。

推断走读：`survival_function(new_log_hz, new_time, eval_time)`——新主体在原网格上的 hazard 矩阵 + 想查询的新时刻列表，积分器出 `(n_new, n_times)` 累积风险，exp 负号得存活概率。新时刻不必是网格点，梯形积分天然支持任意上限。

## 五、设计决策

**为什么梯形法而不是闭式？** 神经网络输出的 hazard 无解析原函数，离散化是唯一选择；梯形法是最低阶且对平滑 hazard 足够的方案。`torch.trapezoid` 的调用让积分本身可微且随反向传播自动获得 adjoint——比手写累积和更接近"数值积分"语义，比 Simpson 复杂度低。

**为什么事件项不插值？** L183-184 只取左邻网格点，线性插值明明更准。合理推断：hazard 在网格间无定义，插值会引入"模型并未承诺的"线性假设；取左邻是保守一致的阶梯语义，误差随网格加密消失。使用者能做的是把 `eval_time` 给密。

**`EvalTimeInputs` 独立成模**：网格校验（2-D、列数匹配、严格递增，`tools/validators.py:359-369`）只在训练与外推两个入口出现，独立模型让它可被两者复用而无需挂进 `ModelInputs`——小而正确的拆分。

**批判视角**：① 主循环逐观测时间跑 Python 级 trapezoid（L56-65），batch 大时是四族损失中最慢的，向量化余地（mask 矩阵一次成型）存在但会牺牲可读性；② `clamp(min=0)`（L67）把数值负值静默归零——真实累积风险非负，负值只可能来自数值误差，但 clamp 同时也会掩盖 hazard 输出严重异常的 bug；③ 时变协变量支持是"原生"的但接口不显式：没有 start/stop 参数，时变性全靠用户让网络输出依赖 t（`f_θ(x_i, t)`），Cox 扩展模型反而有显式 `(N,N)` 矩阵约定——两种时变表达并存，选型时要读 `docs/notebooks/time_varying_covariates.md` 的论证。

## 六、新人提示

- **上手顺序**：先读 `neg_log_likelihood` docstring 的近似公式节（L106-139，"τ_1 应为观测起点"的提醒在 L123-124），再读积分器 25 行实现（L46-67），最后跑 doctest（`python -m torchsurv.loss.survival`，L141-152 的示例自带）。
- **坑 1**：`eval_time` 必须严格递增且首点尽量取 0（或观测起点），否则积分区间少一段、损失系统性偏小——校验层只查递增不查起点。
- **坑 2**：网格列数 M 与 batch 无关，是全局超参；换 M 等于换损失曲面（积分近似不同），对拍实验时 M 要固定。
- **坑 3**：本模型没有 R 基准 JSON 兜底，数值正确性依赖等价性测试——怀疑实现有 bug 时，构造 Weibull 形式的 hazard 喂进来，与 `neg_log_likelihood_weibull` 对比是最快的自证手段。
- **坑 4**：与 `loss/cox.py` 的时变版（`(N,N)` 矩阵）不要混用概念——本文件的 `(N,M)` 列是 eval_time 网格，Cox 的列是"其他主体的时间"，语义完全不同，虽然形状记法像。

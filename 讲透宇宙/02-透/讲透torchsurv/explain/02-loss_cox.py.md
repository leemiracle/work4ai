# `src/torchsurv/loss/cox.py`：Cox 偏部分似然的全家桶（损失、基线、外推）

## 一、角色定位

一句话：实现 **Cox 比例风险模型的负偏部分似然损失**及配套的 Breslow 基线生存函数估计与新个体生存概率外推，是全仓被引最广的文件（图谱总扇入 15）。位于 **L1 生存分析损失函数层**，是四族损失中最经典、选项最多的一个：Efron/Breslow 两种并列时间处理、分层 strata、扩展时变协变量三选项全部在这一个文件里。

## 二、内部结构

756 行，7 个函数、清晰三段式：

**私有计算核（无校验、可复用）**
- `_searchsorted`（`src/torchsurv/loss/cox.py:23-25`）：torch.searchsorted 的 CPU 回退版——MPS 等设备不支持时先 `.cpu()` 再搬回，一行解决设备兼容。
- `_partial_likelihood_cox`（`src/torchsurv/loss/cox.py:28`）：无并列情形。核心三行——flip 后 `torch.logcumsumexp`（L46）实现数值稳定的"后缀风险集和"，再 flip 回来；时变情形取对角线（L49-50）；最后按事件掩码筛选（L52）。
- `_partial_likelihood_efron`（`src/torchsurv/loss/cox.py:56`）：Efron 并列处理。标量分支被完全向量化：`time_to_k = _searchsorted(...)` 把每个受试者映射到唯一时刻索引（L94），`m` 用 `scatter_add_` 统计各时刻事件数（L98-99），风险集分母 `denominator_naive` 用反向累积和 `reverse_cumsum = exp_hz.flip(0).cumsum(0).flip(0)`（L111）+ `first_idx`（L112-113）O(N) 取齐；Efron 修正项 `r/m * T` 以 `(K, max_ties)` 填充张量一次算完（L121-130），padding 位填 1 使 `log(1)=0` 不贡献（L129）。
- `_partial_likelihood_breslow`（`src/torchsurv/loss/cox.py:136`）：Breslow 并列处理，向量化套路同上，分母 `torch.log(reverse_cumsum[first_idx])`（L192），结果乘事件数 `m`（L194）。
- `_cumulative_baseline_hazard`（`src/torchsurv/loss/cox.py:198`）：Breslow 基线累积风险 `sum(m_k / sum_j exp(log_hz))`，最后 `torch.cumsum`（L245）。

**公共 API**
- `neg_partial_log_likelihood`（`src/torchsurv/loss/cox.py:248`）：训练入口。全事件为零或单样本时告警并返回 `torch.tensor(0.0, requires_grad=True)`（L390-395）；strata 缺省补全 1（L398-399）；squeeze 后经 `SurvivalInputs`+`ModelInputs` 定型（L407-412，jit 场景跳过）；`len(log_hz.size()) == 2` 判定时变（L415）；按时间排序（L418，时变用 `log_hz[idx[:, None], idx]` 行列同步重排，L421）；时变再过 `TimeVaryingCoxInputs` 查并列时刻列一致性（L426-427）；逐 stratum 循环（L435），层内先查 `has_ties`（L442）——无并列走标准 Cox（L446），有并列告警并按 `ties_method` 分派 efron/breslow（L449-474）；最后 `torch.neg(torch.cat(pll))`（L477），mean 归约用 `nanmean`（L479）、sum 用 `sum`（L482）。
- `baseline_survival_function`（`src/torchsurv/loss/cox.py:488`）：训练后估基线。单 stratum 返回 `{"time", "baseline_survival"}` 二键 dict（L615-620），多 stratum 返回以 stratum 整数为键的嵌套 dict（L621-627），`S_0 = exp(-H_0)`（L619）。
- `survival_function_cox`（`src/torchsurv/loss/cox.py:632`）：外推入口 `S_i(t) = S_0(t)^λ_i`。基线取值用 `_searchsorted(..., right=True) - 1` 做地板索引（L729）再 `clamp(min=0)`（L733），幂运算在 L740-742（时变版对每个 t 单独取 λ）。

## 三、外部连接

- **imports 出边 1 条**：`tools/validators.py`（本文件 L11 引入 `ModelInputs`/`SurvivalInputs`/`TimeVaryingCoxInputs`）——src 内扇入最高的汇聚点。
- **上游**：两个 barrel（`src/torchsurv/__init__.py:7` 与 `loss/__init__.py`）re-export 三个公共函数；文档侧 `README.md`、`docs/loss.rst`、`docs/notebooks/loss.md`、`docs/notebooks/time_varying_covariates.md`、`docs/package_overview.md` 五处引用。
- **tested_by**：`tests/test_cox.py`（R 基准对拍主战场）、`tests/test_hypothesis.py`、`tests/test_mnist.py`、`tests/test_momentum.py`、`tests/test_torch_jit.py`；`tests/benchmark_script/test_cox.R` 生成对拍参照；`docs/notebooks/helpers_momentum.py` 在教程里消费。
- **内部函数节点**：图谱为 7 个函数各建节点，`neg_partial_log_likelihood` → 三个 `_partial_likelihood_*` 的分派边清晰可见。

## 四、数据流

训练一个 batch 的完整走读：网络输出 `log_hz (N,)` → `neg_partial_log_likelihood` 入口 guards（零事件返回 0 损失，避免空梯度和 NaN）→ validators 定型（event 强制 bool、time 非负、log_params 形状按 cox 约定检查 `(N,)` 或 `(N,N)`）→ 排序 → 无并列快路径：`logcumsumexp` 后缀和一次张量运算出全事件的 `log λ_i - log(Σ_R λ_j)` → 有并列慢路径：按 `ties_method` 进 Efron/Breslow 向量化核 → 三函数共享"算子"层拼装 stratum 列表 → cat、取负、nanmean → 标量损失出函数，backward 梯度沿 logcumsumexp/cumsum 反传。

推断链：训练完先 `baseline_survival_function`（Breslow 累积风险 → exp 负号），再对新个体 `survival_function_cox(baseline, new_log_hz, new_time)`——地板索引保证 new_time 落在两个观测时刻之间时取左端基线值，等价于阶梯函数右连续约定。

## 五、设计决策

**数值稳定优先**：分母风险集和全部走 logcumsumexp/logsumexp 或先 exp 后 cumsum，绝不明写 `sum(exp(...))` 的 log——大 log_hz 下 exp 溢出是生存模型训练的头号 NaN 源。`neg_partial_log_likelihood` 用 `nanmean` 而非 `mean`（L479），让个别 NaN 样本不毒化整批损失。

**两代实现并存**：Efron/Breslow 的时变分支保留 Python 逐时刻循环（L82-91、L163-172），非时变分支向量化——注释明言"Variable-size 2-D indexing — keep per-time-point loops"（L82）。这是"先正确再快"的诚实取舍：时变索引形状不定，向量化收益抵不过复杂度。

**并列处理在层内自动检测**（L442）而非要求用户声明：小数据 ties 稀疏时总走无并列快路径，只有真撞上才告警降速——用户拿到的是"默认最快正确"的行为。

**批判视角**：① stratum 循环（L435）是 Python 级，strata 数多时成为吞吐瓶颈，但正确性无虞；② `has_ties` 只查事件时间的并列（L442），删失与事件同时刻的边缘语义交给 `_get_comparable` 侧的指标层处理，两处口径要对照读；③ 返回 0.0 损失的 guard（L390-395）静默吞掉"整批删失"这个数据质量问题——训练循环若不监控告警，会以为在正常训练。

## 六、新人提示

- **上手顺序**：先读 `neg_partial_log_likelihood` 的 docstring 数学节（L282-358，Cox/Breslow/Efron/分层/时变五组公式），再读 L389-485 的实现体，最后回头看三个私有核；对照 `docs/notebooks/loss.md` 第 1 节的推导。
- **对拍验证**：`tests/test_cox.py:14-24` 模块级加载 4 个 R 基准 JSON，含结/无结各带 Breslow/Efron 两套参照——改任何数值代码后跑它，R `survival::coxph` 是真值源。
- **坑 1**：log_hz 形状决定语义——`(N,)` 比例风险、`(N,N)` 时变扩展，传错形状会在 validators 报 `(n_samples, n_samples)` 约定错误而非形状错误。
- **坑 2**：ties 告警（L449-452）每个 batch 都会刷，pytest 下记得 filterwarnings；且默认 efron 与 lifelines 默认 breslow 对拍会有微小数值差，属预期。
- **坑 3**：`baseline_survival_function` 的返回类型随 strata 数量变（dict vs 嵌套 dict），下游代码要按 `survival_function_cox` L716 的 isinstance 判别式消费，别硬编码单一形态。

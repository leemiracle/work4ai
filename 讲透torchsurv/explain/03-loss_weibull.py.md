# `src/torchsurv/loss/weibull.py`：Weibull AFT 全参数化路线

## 一、角色定位

一句话：实现 **Weibull 加速失效时间（AFT）模型的闭式似然族**——累积风险、log hazard、生存函数、负对数似然四件全部解析可算，是四族损失中唯一的"全参数化"路线。位于 **L1 生存分析损失函数层**，与 `cox.py` 构成"参数化 vs 半参数化"的对偶：Cox 把基线留给非参数估计、网络只学相对风险 λ_i；Weibull 把分布形状也交给网络——输出 log scale 与 log shape 两列参数。

## 二、内部结构

306 行、5 个函数，全部围绕两个参数张量展开：

- **`_cumulative_hazard`**（`src/torchsurv/loss/weibull.py:16`）：`H_i(t) = (t/λ_i)^{ρ_i}` 的对数空间实现。L56 `impute_missing_log_shape(...).unbind(1)` 一步完成"补缺 shape 列 + 拆成 log_scale/log_shape 两量"；随后三分支决定广播形态——标量时间复制到每个样本（L58-60）、`respective_times` 逐主体配对（L61-62）、默认外积成 `(n_samples, n_times)` 网格（L63-67）；最终 `exp(exp(log_shape) * (log(clamp(time, min=1e-100)) - log_scale))` 并 clamp 到 `[0, 1e10]`（L69-73）。
- **`log_hazard`**（`src/torchsurv/loss/weibull.py:76`）：`log h_i(t) = log ρ_i - log λ_i + (ρ_i-1)(log t - log λ_i)`。同样的广播三分支（L119-128）；关键稳定技巧是 `torch.expm1(log_shape)`（L133）——直接算 `ρ-1 = exp(log_shape)-1` 在 shape≈1（指数分布退化）附近会灾难性消去，expm1 保住有效数字；输出 clamp 到 `[-1e10, 1e10]`（L134-135）。
- **`survival_function_weibull`**（`src/torchsurv/loss/weibull.py:139`）：`S = 1 - F`，但 CDF 不手写——L178 直接实例化 `torch.distributions.weibull.Weibull(exp(log_scale), exp(log_shape)).cdf(time)`，把数值实现外包给 PyTorch 官方分布族。
- **`neg_log_likelihood_weibull`**（`src/torchsurv/loss/weibull.py:181`）：训练入口。`ll = Σ_{δ=1} log h_i(T_i) - Σ H_i(T_i)` 的向量化即 L280-282 一行：`torch.neg(event * log_hazard(...) - _cumulative_hazard(...))`，两个内嵌调用都开 `respective_times=True`（每个主体在自己的观测时间上取值）；`torch.isinf` 的样本被直接剔除（L284-286）；reduction mean/sum 在 L288-293 分派。

参数约定钉死在 docstring：`log_params` 第 1 列 = log scale、第 2 列 = log shape（L28-30 与 L220-221）；只给 1 列时校验层补 0，即 ρ=1 退化为指数模型（`docs/notebooks/loss.md` 第 3 节明说这是"免费获得的第三个模型"）。

## 三、外部连接

- **imports 出边**：`tools/validators.py`（本文件 L7 引 `ModelInputs`/`SurvivalInputs`/`impute_missing_log_shape`）。
- **上游**：`src/torchsurv/__init__.py:10` re-export 三个公共函数（`log_hazard`/`neg_log_likelihood_weibull`/`survival_function_weibull`）；`README.md` 的 Weibull 十行伪代码示例、`docs/loss.rst`、`docs/notebooks/loss.md`（第 2/3 节的数学对应物）均指向本文件。
- **tested_by（图谱最广的测试网之一）**：`tests/test_weibull.py`（R 对拍主战场）、`tests/test_hypothesis.py`（有限性属性）、`tests/test_survival.py`、`tests/test_momentum.py`、`tests/test_train.py`、`tests/test_torch_jit.py`；`tests/benchmark_script/test_weibull.R` 生成参照 JSON。
- **横向对偶**：图谱里 `cox.py` 与本文件同为 L1，`docs/notebooks/loss.md` 一文同时挂两者的 documents 边——"一篇文档讲两族损失"是本仓文档组织的惯例。

## 四、数据流

训练走读：网络头输出 `(N, 2)`（或 `(N, 1)`）→ `neg_log_likelihood_weibull` 先过 `SurvivalInputs` + `ModelInputs(model_type="weibull")`（L269-273，jit 跳过）——后者在 `validators.py:230-240` 完成三件事：维度限 1/2、列数限 1/2、调 `impute_missing_log_shape` 归一成 `(N,2)` → squeeze → 核心一行（L280-282）：事件样本贡献 `log h_i(T_i)`（乘 event 布尔掩码自然置零删失样本的事件项），全部样本贡献 `-H_i(T_i)` → 取负、滤 inf → mean 得标量。

注意参数流的一个细节：`log_hazard` 与 `_cumulative_hazard` 各自内部又调了一次 `impute_missing_log_shape`（L117/L56）——归一化是幂等的，重复调用只为让推断函数独立于训练入口可用（单拿 `log_hazard` 给新主体算 hazard 时无需先手动补列）。

推断走读：`survival_function_weibull(new_log_params, new_time)` 无校验直接广播（L167-176）→ torch.distributions CDF → `1-F` 出 `(n_new, n_times)` 存活概率矩阵。

## 五、设计决策

**为什么全在 log 空间？** 网络输出天然无界，log scale/log shape 直接保证 scale、shape 严格为正（exp 一次即得），免掉软约束或裁剪；且 `(t/λ)^ρ` 改写为 `exp(ρ·(log t - log λ))` 后与 log 参数无缝衔接。代价是 docstring 里的示例损失值巨大（L250 的 `tensor(143039.2656)`）——随机参数下 H 项轻松爆到 clamp 上限 1e10 附近，这是"先能训不炸"的工程选择，配合 L284-286 的 inf 剔除双保险。

**clamp 的三层防御**：time 下限 `1e-100` 防 log(0)（L70）；累积风险上限 `clamp_value=1e10` 防 exp 溢出（L69-73，且作为可调参数暴露）；NLL 里再剔 inf（L284-286）。每层都可独立关掉观察原始行为，适合调参时定位数值问题在哪一层爆。

**CDF 外包给 `torch.distributions`**（L178）：Weibull CDF 的解析式 `1-exp(-(t/λ)^ρ)` 自己写也就一行，但官方实现在极端参数下的 log-space 处理更稳，还免费获得 rsample/log_prob 等配套——"不重写标准分布"是本仓的隐性纪律。

**批判视角**：① inf 剔除（L284-286）改变了有效样本量却不在 loss 上做补偿，mean 语义在含 inf 的 batch 里悄悄漂移；② `respective_times` 分支要求 `new_time.size(0) == log_params.size(0)` 但只在不等时静默走外积分支（L61 条件不满足即落到 else），形状巧合相同时两种语义二选一的判定靠调用者自觉；③ 单调 hazard 的模型假设（FAQ 明示 U 形风险不适用）意味着它对.batch 效应明显的人群（如治疗初期风险高后期回落）天然吃亏，选型时别只看对拍数字。

## 六、新人提示

- **上手顺序**：先读 `neg_log_likelihood_weibull` docstring 的四组公式（L207-241），再对照 `_cumulative_hazard`/`log_hazard` 的实现行（L56-73、L117-136），最后读 `docs/notebooks/loss.md` 第 2-3 节补全推导；doctest（L244-258）可直接 `python -m torchsurv.loss.weibull` 跑。
- **坑 1**：列序是 log scale 在前、log shape 在后，与部分教材"shape 优先"的记法相反，对拍 R 脚本（`test_weibull.R`）时先核对参数映射。
- **坑 2**：损失值大是常态不是 bug——clamp 上限 1e10 与 inf 剔除兜底之下，训练初期 `tensor(1e5)` 量级完全正常，盯梯度是否有限比盯损失绝对值有意义。
- **坑 3**：只输出一列 log_params 时静默退化为指数模型（shape=1），若本意是 Weibull 而网络头少了一个输出单元，不会报错只会欠拟合——用 `ModelInputs` 的归一结果（`(N,2)`）反查网络头形状。
- **坑 4**：`tests/benchmark_script/test_weibull.R:107` 的 write_json 硬编码了原作者绝对路径，重生成基准前要先改这一行。

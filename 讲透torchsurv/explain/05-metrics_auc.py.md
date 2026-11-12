# `src/torchsurv/metrics/auc.py`：时间依赖 AUC 与双引擎统计推断

## 一、角色定位

一句话：实现**时间依赖 AUC**（cumulative/dynamic 与 incident/dynamic 两种定义）及其完整的统计推断链——置信区间、p 值、两模型比较，每种推断都提供 Blanche 影响函数法与 bootstrap 法双引擎。位于 **L2 模型评估指标层**，1221 行是全仓最大文件，也是三件套指标中数学最重的一个：点估计只是开头，标准误的影响函数推导（Blanche 2013）占了近四百行。

## 二、内部结构

单类 `Auc`（`src/torchsurv/metrics/auc.py:16`），26 个方法分四组：

**构造与状态**：`__init__`（L19，签名单行、默认 `tied_tol=1e-8`）初始化 11 个实例槽位（L44-56）——estimate/is_case/is_control/weight 等，全部 `None` 起步，等 `__call__` 填充。这是"可调用对象 + 惰性推断"模式：点估计先算，推断方法复用状态。

**点估计**：`__call__`（L59，`auc_type` 默认 `"cumulative"` 在 L64）五步走——① 输入流水线：`_validate_auc_inputs`（L204 调用，定义 L1124）查 weight_new_time 配对与 auc_type 合法性，`_update_auc_new_time`（L207，定义 L1149）在 new_time 缺省时取"删失截断的唯一事件时间"（`mask = event & (time < max(time))` + `torch.unique`），`_update_auc_estimate`（L210）把一维风险分广播成 `(n, n_times)`，`_update_auc_weight`（L211）补默认全 1 权重；② 四张长表按列 expand（L223-226）；③ 每列按风险分降序排（L229-232 的 argsort+gather）；④ case/control 判定——incident 要求 `time == t 且 event`（L236）、cumulative 只要 `time <= t 且 event`（L238）、control 是 `time > t`（L239），随后 cumsum 出 TP/FP 率（L243-246）；⑤ 逐时刻列去掉并列阈值（L250 的 `tied_tol` 判定 + L261-262 掩码）、补 (0,0) 起点后 `torch.trapz` 梯形积分（L270-274）。`instate=True` 时反变换回原顺序并存全部状态（L277-292）。

**积分**：`integral`（L296）——单一时刻直接返回（L339-340）；否则 `tmax` 缺省取 `new_time[-1]`（cumulative）或 `-1`（incident）（L343-344），拟合 KM 生存分布（L347-349）后按类型加权：cumulative 用事件密度（`_integrate_cumulative` L594）、incident 用 2×事件密度×生存函数（`_integrate_incident` L555），即 Heagerty & Zheng 的 AUC 累积/发生密度权。

**推断双引擎**：`confidence_interval`（L358）/`p_value`（L429）/`compare`（L490）三个公共门面各分派到 `_confidence_interval_blanche`（L633）或 `_bootstrap`（L656）、`_p_value_blanche`（L695，正态 CDF 在 L706）或 `_p_value_bootstrap`（L718，置换风险分）、`_compare_blanche`（L751）或 `_compare_bootstrap`（L794）。Blanche 引擎的核心是 `_auc_se`（L818）：内部再拟 KM（L833-835）、构造 `ipsw = I(T_i ≥ t)/S(t)`（L843）、调 `_integral_censoring_martingale_divided_survival`（L897）算删失鞅积分、组装 `h_t`/`H_t`（L860-868）后交 `_phi_blanche`（L950）得影响函数。`_compare_blanche` 用 torchmetrics 的 `SpearmanCorrCoef` 算两模型风险分相关性（L774），配对 t 统计量在 L781-783，p 值走 scipy 的 `stats.t.cdf`（L787，注释明言"student-t cdf not available on torch"）。bootstrap 引擎统一收敛在 `_bootstrap_auc`（L982），按 metric 参数切换原假设（p_value 置换 / ci 重采样 / compare 混合池）。

## 三、外部连接

- **imports 出边 3 条**：`stats/kaplan_meier.py`（auc.py:10 引入，integral 与 _auc_se 两处消费）、`tools/validators.py`（auc.py:11）、`tests/test_auc.py`。**Auc 是唯一依赖 KM 的指标**——cindex/brier 的删失校正走 IPCW（用户传入），Auc 连积分权重都要自己现算 KM。
- **第三方依赖**：scipy.stats（t 分布 CDF，L7）与 torchmetrics（Spearman 相关，L8）——三件套中外部依赖最多的一个。
- **上游**：`src/torchsurv/__init__.py:11` 与 `metrics/__init__.py` re-export；`README.md`、`docs/metrics.rst`、`docs/notebooks/metrics.md`（C-index 与 AUC 积分关系的证明）、`docs/package_overview.md` 引用。
- **tested_by**：`tests/test_auc.py`（R 对拍，`benchmark_script/test_auc.R` 用 survAUC/timeROC/riskRegression 三包生成参照）、`tests/test_hypothesis.py`（AUC 落 [0,1] 属性）。

## 四、数据流

评估走读（训练循环末尾的典型用法）：模型对验证集输出风险分 `estimate (N,)` → `auc = Auc()(estimate, event, time, auc_type="incident")` → 输入流水线自动把 new_time 定为唯一事件时间、权重补 1 → 排序建 ROC → 逐时刻 trapz → 返回 `tensor([auc_1, ..., auc_T])` 存入实例 → `auc.integral()` 拟 KM 加权积分出单值 → `auc.confidence_interval()` 触发 Blanche SE：沿 L818-950 的影响函数链算出每个时刻的标准误 → `auc.compare(other_auc)` 取另一模型的同套状态，Spearman 相关 + 配对 t 检验出每个时刻的 p 值——论文里"模型 A 的时间依赖 AUC 在 t=5y 显著高于 B"即此一行的输出。

训练/测试切分的正确姿势（docstring L162-163 明文）：IPCW 权重应该用**训练集**估的删失分布在测试集时间上取值再传入 `weight`，让校正不偷看测试集信息。

## 五、设计决策

**为什么 case/control 定义只差一个等号？** L236 与 L238 的唯一区别是 `==` vs `<=`：incident/dynamic 把"T 恰在 t 时刻事件"当 case（分母是时刻 t 的风险者），cumulative/dynamic 把"T ≤ t 已事件"都算 case（分母更大）。这一行决定了两种 AUC 的统计含义差异——前者对"恰在 t 的判别"敏感，后者对"到 t 为止的累积判别"敏感。统一在同一循环里实现，两种定义共享全部排序与积分机械。

**影响函数 vs bootstrap 双轨**：Blanche 法一次前向算出 SE（快、确定），bootstrap 慢但无需推导、任意统计量通用。两者并存且默认 Blanche，是把"论文要快而稳的 CI"与"审稿人要稳健性检查"两类需求都满足的工程答案。

**torch 不够就借 scipy**：L787 注释直白承认 t 分布 CDF torch 没有——库的"纯 torch"边界允许在推断层（非训练路径）借 scipy，训练可微性不受影响。这是全仓 torch/scipy 分工的代表性切面。

**批判视角**：① `_auc_se` 的影响函数链四百行张量代码，可读性靠注释里的公式编号（L870 引 Blanche 补充材料页码）维持，改一处要重推全链；② `integral` 的 tmax 缺省对 incident 取 `new_time[-1]-1`（L344）是硬编码减 1，隐含"时间单位为整数"的假设，连续时间网格下这个缺省值得推敲；③ 1221 行单类已接近"上帝类"边界，点估计与推断引擎拆成两个类的重构空间明显存在——但 R 对拍资产锁住了行为，重构成本高收益低，维持现状是理性选择。

## 六、新人提示

- **上手顺序**：先读 `__call__` docstring 的定义节（L70-197，两种 AUC 的 case/control 数学定义），再啃 `integral`（L296-356）与 `_auc_se`（L818 起）；`docs/notebooks/metrics.md` 的 AUC-Cindex 积分关系证明是理解加权积分的前置。
- **坑 1**：`auc_type` 拼错在 `_validate_auc_inputs`（L1137 的合法性检查）报错，且大小写敏感——`"Cumulative"` 会挂。
- **坑 2**：给 `weight` 必须同时给 `weight_new_time`（L1133 的配对检查），且两者要来自训练集删失分布——漏配对是最高频的调用错误。
- **坑 3**：置信区间出现 0/1 边界值（如 docstring L38-39 的 `[0.0000, 1.0000]`）不是 bug，是小样本下 Blanche 正态近似的截断，换 bootstrap 法看真实分布。
- **坑 4**：`compare` 前两个 Auc 实例必须在**同一批数据**上算过，否则 Spearman 相关维度对不上直接断言失败。

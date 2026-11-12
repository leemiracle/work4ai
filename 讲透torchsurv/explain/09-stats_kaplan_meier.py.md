# `src/torchsurv/stats/kaplan_meier.py`：KaplanMeierEstimator 双分布引擎

## 一、角色定位

一句话：实现 **Kaplan-Meier 非参数估计器**——以 `censoring_dist` 旗标一物两用，既估生存分布 S(t) 又估删失分布 D(t)（后者供 IPCW 消费），是 L3 基础层的最底层构件。位于 **L3 统计估计与输入校验基础层**。全仓对"删失"的处理最终都回溯到这 274 行：损失侧绕开删失（偏似然），指标侧校正删失（IPCW），而校正的原料在这里生产。

## 二、内部结构

单类 `KaplanMeierEstimator`（`src/torchsurv/stats/kaplan_meier.py:17`）六方法：

- **`__init__`**（L20）：仅存 `self.device`（L26-29 的 `torch.device` 归一），无状态设计——拟合状态在 `__call__` 里创建。
- **`__call__`**（L31，`censoring_dist` 默认 False 在 L35）：
  1. 原始 event/time 上设备（L73-74）。
  2. jit 场景外过 `SurvivalInputs`（L77-79）。
  3. `_compute_counts()` 出四元组：唯一时刻/事件数/风险集数/删失数（L82）。
  4. **角色互换三行**（L85-87）：`censoring_dist=True` 时 `n_at_risk -= n_events; n_events = n_censored`——把删失当事件、事件当删失，同一连乘公式立刻变成删失分布估计器。这是全文件最精巧的三行。
  5. 连乘核：`torch.where(n_events != 0, n_events/n_at_risk, 0)`（L90-96，防除零）、`values = 1 - ratio`（L97）、`y = torch.cumprod(values, dim=0)`（L98）——KM 估计量 Π(1-d_k/N_k) 的张量直译。
  6. 状态落盘 `self.time`/`self.km_est`（L101-102）。doctest（L50-61）并排展示两种分布的输出，同一数据、一行旗标之差。
- **`predict`**（L136）：在 new_time 上取值。四步：搬设备（L160）；构造参考轴——时间向量前拼 `-inf`、估计前拼 1.0（L164-165），使"观测开始前 S=1"有明确锚点；越界处理 `extends = new_time > max(ref_time)`（L168），越界时刻的估计**冻结**在最后一个训练时刻的值（L175，"probability holds after the last event"）；界内用 `torch.searchsorted(..., side="left")`（L178）+ eps 容差比对（L181-182）实现**左极限**取值——new_time 不落在任何拟合时刻上时，取它左边最近那个时刻的估计，与 KM 阶梯函数的右连续性约定一致。
- **`plot_km`**（L104）：matplotlib 阶梯图（`ax.step(..., where="post")` L131），惰性 import（L126）。
- **`get_survival_table`**（L189）：print 生存表 + 返回 pandas DataFrame（L207）——pandas 依赖只服务这一个展示函数。
- **`_compute_counts`**（L209）：统计核心。排序（L224）后 `itertools.groupby` 按时刻分组（L232），Python 循环内逐组数事件（L242-248）；风险集用"总数减错位累积和"（L258-260 的 `n_samples - cumsum([0]+counts)`）一步算齐；返回时丢掉末位补零（L262）。

## 三、外部连接

- **imports 出边**：`tools/validators.py`（本文件 L10）+ pandas（L7，仅表格用）。
- **上游（两条消费线）**：① 用户线——`src/torchsurv/__init__.py:15` re-export，notebook 里直接画 KM 曲线；② 系统线——`stats/ipcw.py:76-77` 以 `censoring_dist=True` 消费（IPCW 的删失分布来源）、`metrics/auc.py` 两处消费（auc.py:347-349 积分权重、auc.py:833-835 影响函数，均为生存分布）。**图谱中唯一被 metrics 直接 import 的 stats 文件**。
- **tested_by**：`tests/test_kaplan_meier.py`（R 对拍，`benchmark_script/test_kaplan_meier.R` 用 survival::survfit 生成参照）、`tests/test_hypothesis.py`（估计量单调非增性等属性）。
- **文档边**：`docs/stats.rst`、`docs/package_overview.md`。

## 四、数据流

系统线走读（IPCW 生产链）：`get_ipcw` → `KaplanMeierEstimator(device)(event, time, censoring_dist=True)` → 角色互换 → 连乘出 D̂ → `predict(new_time)` 左极限取值 → 倒数成权重 → 喂给三件套指标。这条链上 predict 的左极限语义有实际后果：评估时刻恰与某删失时刻重合时取的是"该时刻之前"的 D̂，权重不会因该时刻的删失事件而骤降——保守且无跳变。

用户线走读（notebook 诊断）：`km = KaplanMeierEstimator(); km(event, time); km.plot_km()` 出阶梯曲线；`km.predict(torch.tensor([1.0, 5.0]))` 查两个时刻的存活率。`get_survival_table()` 出 DataFrame 便于贴进报告。

内部数据流的关键在 `_compute_counts` 的返回约定：四元组按唯一时刻对齐，风险集数组的长度与唯一时刻数相同（L262 丢补零）——下游的 where/cumprod 全部无掩码直算，形状契约靠这个对齐维持。

## 五、设计决策

**一物两用而非两个类**：`SurvivalEstimator` 与 `CensoringEstimator` 分开写要复制整个连乘与预测机械；三行角色互换（L85-87）证明两者数学上同构（KM 对"何为事件"对称）。删失分布估计从"新功能"降格为"旗标"，API 面少一个类。

**连乘核的防除零**：`n_at_risk` 在尾部理论上不会为 0（最后一刻仍有风险者），但 ties 与整数下溢的边缘场景存在；`torch.where` 显式给 0（L90-96）比 try-except 快且 jit 友好。

**predict 的 -inf/1.0 前缀技巧**（L164-165）：把"观测前 S=1"这个边界情形并入统一索引——new_time 小于首个拟合时刻时 searchsorted 自然指向前缀位。配合 extends 冻结（L175），任意 new_time 都有定义，`predict` 成为全时间轴无异常函数。这比"范围内 assert、范围外报错"的接口对下游（尤其 IPCW 的任意评估时刻）友好得多。

**批判视角**：① `_compute_counts` 是 Python 级 groupby 循环（L232-249），N 大时是全文件瓶颈——torch.unique + scatter_add 的向量化版本完全可行（cox.py 的 Efron 核就是现成范式），维持循环版应是可读性优先的取舍；② 估计量的单调性没有强制——浮点 cumprod 理论单调，但上游喂入怪异数据时 km_est 可能出现 1+ε 之类的微扰，`test_hypothesis.py` 的单调性属性测试正是为这个兜底；③ `predict` 的 eps 判等（L181-182）在时间量级极大（如秒级时间戳 ~1e9）时相对精度不足，可能出现"本应精确命中却走了左极限"的边缘——量纲归一后使用更稳。

## 六、新人提示

- **上手顺序**：先读 `__call__` 的 doctest（L50-61，两种分布对照），再看 L85-98 十四行核心（角色互换 + 连乘），然后 `predict`（L136-187）吃透左极限与越界冻结两个语义，最后扫 `_compute_counts`。
- **坑 1**：`censoring_dist` 默认 False——IPCW 场景忘开这个旗标会把生存分布当删失分布取倒数，权重系统性偏小且不报错。
- **坑 2**：`predict` 返回的越界时刻值是"冻结"而非外推（L175），随访结束后真实生存继续下降而估计保持不变——画图时尾部平台是估计器性质不是数据特征。
- **坑 3**：实例不可重入——`__call__` 直接覆写 `self.time`/`self.km_est`，同一实例先拟合生存再拟合删失会静默覆盖，两个分布要两个实例（doctest L54-59 正是这么演示的）。
- **坑 4**：`plot_km`/`get_survival_table` 把 matplotlib/pandas 拉进运行时（惰性 import 缓解了前者），纯生产管线不要调用它们。

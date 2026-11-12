# `src/torchsurv/metrics/cindex.py`：Harrell/Uno 一体的 ConcordanceIndex

## 一、角色定位

一句话：实现**一致性指数（C-index）**——"事件先发生的个体风险分更高"的概率，默认 Harrell 估计量、传入 IPCW 权重即得 Uno 版，配 noether/conservative/bootstrap 三套推断。位于 **L2 模型评估指标层**。它是三件套里概念最亲民的一个（医生一眼懂"排序对不对"），但 docstring 开头就自我警告：对固定时点的判别任务它不是 proper 指标，该用 Auc（L103-104 引 Blanche 2018）。

## 二、内部结构

单类 `ConcordanceIndex`（`src/torchsurv/metrics/cindex.py:16`），20 个方法：

**构造**：`__init__`（L19，`tied_tol=1e-8` 在 L21）初始化 10 个状态槽（L47-56）：cindex/concordant/discordant/tied_risk/weight/weight_squared/tmax 等——计数器分项留着给 Noether SE 用。

**点估计 `__call__`**（L60）七步：
1. squeeze（L184-185）与 `_update_cindex_estimate`（L188，定义 L861）：一维风险分先 unsqueeze 再 expand 成 `(N,N)`（L867）——统一到时变记法 `q_i(T_j)`，i=j 处即"自己事件时刻的风险分"。
2. `_update_weight`（L189，定义 L842）：权重缺省补 1；`tmax` 截断在这里做——`masks = time < tmax`（L853），窗口外样本权重置 0（L854-856）。
3. 权重平方 `weight_squared`（L192）——Uno 公式的 ω² 项。
4. `SurvivalInputs` 校验（L195-197，jit 跳过）。
5. `_get_comparable_and_tied_time`（L200 调用，定义 L773）建可比对字典：按时间排序后双指针扫并列段（L809-815），事件者的 mask 把"严格更晚者"（L828 `mask[end:] = True`）与"同刻删失者"（L831 `mask[i:end] = censored_at_same_time`）标为可比——同刻删失算可比是 Harrell 的经典约定；无比对时抛 ValueError（L836-837）。
6. 主循环（L214-243）：对每个事件时刻取 `est_i = estimate[order[ind], order[ind]]`（L217，对角元）与可比集风险分 `est_j`（L223），并列判定 `|est_j - est_i| <= tied_tol`（L229），concordant 计 `est_j < est_i`（L233），numerator 累加 `w_i·n_con + 0.5·w_i·n_ties`（L237，并列记半分），denominator 累加 `w_i·n`（L238）。
7. `instate` 存状态（L246-256），返回 `numerator / denominator`（L258）。

**推断三件套**：`confidence_interval`（L260，默认 noether，另 conservative/bootstrap）→ `_confidence_interval_noether`（L465）/`_confidence_interval_conservative`（L493）/`_confidence_interval_bootstrap`（L524）；`p_value`（L336）→ `_p_value_noether`（L555，正态近似对 0.5）/`_p_value_bootstrap`（L578，置换）；`compare`（L397，默认 noether）→ `_compare_noether`（L603）/`_compare_bootstrap`（L645）。

**标准误 `_concordance_index_se`**（L663）：Noether 公式——用 concordant/discordant 的和与平方和（L671-675 的 pc/pd/pcc/pdd/pcd）组装方差（L676），`sqrt(varp/N)`（L678）。它只依赖 `__call__` 存下的四个计数张量，不重算任何比对——这是分项计数的回报。

**`_bootstrap_cindex`**（L680）：三种重采样语义——p_value 置换风险分行（L708-710）、CI 按行重采（L722-740，时变的 `(N,N)` 矩阵要行列同步 `estimate[index, :][:, index]`，L733）、compare 混合两模型池（L741-768）。全部 `instate=False` 复用 `__call__` 而不污染原状态（L718 等）。

## 三、外部连接

- **imports 出边**：`tools/validators.py`（本文件 L11）；第三方 scipy.stats（L8）与 torchmetrics regression（L9，compare 的相关系数用）。
- **上游**：`src/torchsurv/__init__.py:13` 与 `metrics/__init__.py` re-export；`README.md`、`docs/metrics.rst`、`docs/notebooks/metrics.md`、`docs/package_overview.md` 引用；`docs/notebooks/helpers_momentum.py` 在动量教程里消费（记忆库版训练的评估端）。
- **tested_by**：`tests/test_cindex.py`（R 对拍，`benchmark_script/test_cindex.R` 生成参照）、`tests/test_hypothesis.py`、`tests/test_mnist.py`（MNIST 生存化实验的指标）、`tests/test_torch_jit.py`。
- **与 IPCW 的关系是"约定"而非 import**：本文件不 import `get_ipcw`——权重作为参数由用户传入（docstring 示例 L167-169 演示 `ipcw = get_ipcw(event, time)` 后再调），依赖箭头留在调用侧。这是三件套的共同设计：指标层对删失校正保持"被动"。

## 四、数据流

评估走读：`estimate (N,)` + event/time 进 `__call__` → 广播成 `(N,N)` → 权重处理（tmax 截断、平方）→ 建可比对字典（一次 O(N log N) 排序 + 线性扫）→ 逐事件者累加分子分母 → 出标量 C-index。不带权重 = Harrell；`get_ipcw` 的输出作为 weight 传入 = Uno（IPCW 的平方在 L192 内部完成，用户无需预平方）。

推断走读：`cindex.confidence_interval()` → noether 分支读四计数张量 → `_concordance_index_se` 出 SE → 正态分位数 ± 出上下界。`cindex.compare(other)` noether 分支算两 SE 与风险分相关 → 配对 z/t 统计量出 p 值序列。

训练监控走读（test_mnist 的用法）：每个 epoch 末 `cindex(train_estimate, event, time)` 复用同一实例——`__call__` 重入即整体覆写状态（L246-256），没有跨 epoch 的隐式累积，可安全挂在训练循环里。

## 五、设计决策

**Harrell 与 Uno 只差一个 weight 参数**：两者数学上是同一个估计量族（docstring L139 vs L152 的公式只差 ω² 因子），实现上统一为"加权排序对"一套代码——这是对"R 里 survComp/pec 各自成包"的碎片化的直接回应，也把"该用哪个"变成显式的用户决策而非实现细节。

**计数分项即时留存**：主循环里 concordant/discordant/tied_risk 按事件者逐项 append（L241-243），不只为了调试——Noether SE 的 pc/pd/pcc/pdd 全部由这些分项的和与积组装（L671-675）。点估计与推断共享中间量，避免推断时重算 O(N²) 比对。

**`tied_tol` 而非精确相等**：浮点风险分的"并列"用容差判定（L229），默认 1e-8。没有它，数值上本应并列的风险分（如两模型同一线性头）会因 1e-16 级抖动被拆成一对 concordant+discordant，CI 被系统性低估。

**批判视角**：① 主循环 Python 级遍历事件者（L214），N 大且事件多时比 Auc 的全张量实现慢一个量级，但可比对字典的构建（L773-839）本身就是双指针+掩码的近线性结构，瓶颈在循环体而非算法；② 同刻删失算可比（L831）是 Harrell 约定， administer-heavy 删失下会给 C-index 带来偏倚——Uno 加权能纠一部分，但 docstring 已提示时点判别请用 Auc；③ `_update_weight` 对 `tmax` 窗口外样本置 0 权重而非剔除（L850-856），这些样本仍参与排序只是不贡献——语义正确但内存占用不变，超大数据集上无节省。

## 六、新人提示

- **上手顺序**：先读 `__call__` docstring 的定义与公式节（L99-156，Harrell→Uno 的过渡在 L141-152），再读 `_get_comparable_and_tied_time`（L773-839，可比性判定的全部细节），最后看 `_concordance_index_se`（L663-678，Noether 公式与计数分项的对应）。
- **坑 1**：全删失数据在 `SurvivalInputs` 就报"All samples are censored"，但"无比对"（所有事件都在最后一个时刻）要到 L836 的 ValueError 才拦——两类报错位置不同。
- **坑 2**：`tmax` 截断后若窗口内无比对，同样触发 L836；选 tmax 的原则是"tmax 后仍有未删失样本"（docstring L89-90）。
- **坑 3**：Uno 版的权重来自训练集删失分布（docstring L154-155 明确），拿测试集自身估 IPCW 再自评是常见方法论错误，数字会偏乐观。
- **坑 4**：风险分方向——约定"高风险分=先事件"（concordant 判 `est_j < est_i`，L233）。如果你的网络输出的是生存概率（越大越安全），先取负号再喂进来。

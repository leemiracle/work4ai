# `src/torchsurv/stats/ipcw.py`：逆概率删失加权——指标层的共享地基

## 一、角色定位

一句话：实现 **IPCW（inverse probability of censoring weighted）权重** ω(t) = 1/D̂(t)——用 KM 估计的删失分布取倒数，为三个评估指标提供删失无偏校正，是 L3 与 L2 之间最重要的那条边。位于 **L3 统计估计与输入校验基础层**，126 行的小文件却是全仓方法论枢纽：Harrell→Uno、朴素 BS→Graf BS 的"校正"二字，数值上都发生在这里。

## 二、内部结构

两函数 + 一个已知的死代码区：

- **`get_ipcw`**（`src/torchsurv/stats/ipcw.py:17`）六步：
  1. `new_time` 缺省回落到 `time` 自身（L59-60）——权重默认在每个主体的观测时刻上取值。
  2. 设备对齐：time/new_time 与 event 不在同一 device 时告警并统一 cast 到 event 的设备（L63-69）——三件套在 GPU 上调用时最常见的摩擦点在此静默吸收。
  3. jit 场景外过 `SurvivalInputs`（L71-73）——全删失在入口即报错。
  4. 拟合删失分布：`KaplanMeierEstimator(device=device)` + `km(event, time, censoring_dist=True)`（L76-77）——把"删失当事件"的角色互换发生在 KM 内部。
  5. 在 new_time 上预测删失生存概率 D̂（L80）。
  6. 权重合成：`mask = ct > 0`（L83），mask 内取倒数、mask 外置 0（L84-85）——删失分布已降到 0 的时刻（尾部无人"幸免删失"），权重置 0 而非 inf，等价于把这些时刻的样本从校正中剔除。
- **`_inverse_censoring_dist`**（`src/torchsurv/stats/ipcw.py:90`）：取倒数的辅助函数。L108-114 在 ct 含 0 时告警"Returning ones as weight"，但 **if 块内没有提前 return**——L115 的 `weight = 1.0 / ct` 随即被 L116 的 `weight = torch.ones_like(ct) / ct` 完全覆盖：L115 是死赋值，而告警文案宣称的"返回 1"与实际行为（1/0 = inf）不符。由于上游 L83-85 已把 0 元素 mask 掉，这条告警+inf 路径在 `get_ipcw` 主链上不可达，属防御性死代码。

doctest 块（L36-45）演示两个调用形态：同长（评估在自身时间）与 2 倍长（评估在新时间），输出里可见 0 权重样本——就是 mask 生效的样子。

## 三、外部连接

- **imports 出边**：`stats/kaplan_meier.py`（本文件 L7 引入）与 `tools/validators.py`（本文件 L8）——向下两跳即到底，是"三跳到 validators"规律的标准示例。
- **上游（被谁消费）**：`src/torchsurv/__init__.py:14` 与 `stats/__init__.py` re-export（**唯一直接暴露给用户的 stats 函数**，KM 都要通过它才能被多数用户用到）；测试侧 `tests/test_ipcw.py`（R 对拍，`benchmark_script/test_ipcw.R` 用 pec 包生成参照）；三个指标测试 `tests/test_auc.py`/`test_brier_score.py`/`test_cindex.py` 也各自 import 它来构造权重。
- **关键结构性事实**：metrics 三文件都**不** import get_ipcw——权重作为参数传入。IPCW 的消费者是"用户代码 + docstring 示例"，依赖箭头 `metrics → stats` 在图谱上是经 auc→kaplan_meier 与三件套→validators 间接体现的。这个"被动校正"设计把"权重来自训练集"的方法论责任显式交给了调用者。
- **文档边**：`docs/stats.rst` 与 `docs/package_overview.md`。

## 四、数据流

标准评估链走读：训练集 (event, time) 进 `get_ipcw` → KM 以 censoring_dist=True 拟合（内部事件/删失角色互换）→ 在测试时刻 new_time 上 predict 出 D̂(t) → 逐元素倒数、0 处置 0 → `tensor([ω(t_1), ..., ω(t_K)])` → 一分为二：`weight`（主体时刻处）与 `weight_new_time`（评估时刻处）分别喂给 BrierScore/Auc。

直觉走读：一个在时刻 t 仍被观测的样本，"代表" 1/D̂(t) 个同类样本——删失概率越高的时点，幸存观测的代表性权重越大。删失稀疏区 D̂≈1、权重≈1（校正自动退化）；删失密集区权重飙升，个别样本开始主导指标——这也是 IPCW 估计量高方差的来源，样本量小时置信区间变宽是正确行为而非 bug。

cindex 的用法略不同：Uno 版把 `get_ipcw(event, time)` 直接当 weight 传入，平方在 `cindex.py:192` 内部完成（`weight_squared = torch.square(weight)`）——所以用户永远不需要自己预平方。

## 五、设计决策

**为什么删失分布用 KM 而不是参数模型？** D̂(t) = P(D > t) 是生存函数的对偶——把 event 指示符取反（"删失当事件"）后 KM 估计器原样可用（`kaplan_meier.py:85-87` 的三元置换）。零新代码换来非参数、无模型假设的删失分布，这是"问题归约到已有工具"的教科书案例。

**0 处置放在调用侧（L83-85）而非工具函数内**：`_inverse_censoring_dist` 名义上管倒数，但"ct=0 怎么办"的策略（置 0 剔除）由 `get_ipcw` 决定。工具保持数学纯度、策略留在业务层——若未来想改策略（如置 1、截断到分位数），只动一处。

**设备告警而非报错（L64-67）**：多 GPU 训练里权重张量与数据张量的设备错位是高频小错，硬报错打断训练循环反而烦人；告警+自动 cast 把它降级为可忽略信息，代价是极端情况下静默搬运开销。

**批判视角**：① 死代码 + 文案漂移（L112 vs L115-116）是本仓"注释与代码漂移"家族的最典型标本——读代码或调试权重异常时勿被"Returning ones"误导，实际返回的是 1/ct（含 inf 可能）；② IPCW 的一致性依赖独立删失假设，删失与事件相关（如复发者更易失访）时权重本身就是有偏的——这是方法层限制，代码无法兜底；③ 尾部 D̂→0 处样本被置 0 权重，等于静默缩小的有效样本集，报告指标时应同时报告"权重非零样本数"，本文件未提供这个诊断量，需用户自查。

## 六、新人提示

- **上手顺序**：先读 `get_ipcw` docstring 的 Note 节（L47-53，ω(t) 定义与 D̂ 的含义），再读 6 步实现（L58-87），配合 `tests/test_ipcw.py` 的 R 对拍用例理解输出语义；doctest（L36-45）可直接跑。
- **坑 1**：训练/测试切分时权重永远用**训练集**拟合——`get_ipcw(train_event, train_time, test_time)`，三个指标的 docstring 都重复了这个提醒，评审论文时这是高频方法论错误。
- **坑 2**：输出里的 0 权重（见 doctest L42 的 `0.0000`）表示该时刻删失分布已耗尽，不是计算错误；对指标的影响是该样本不贡献校正。
- **坑 3**：`new_time` 传标量或一维皆可，但必须排序（`NewTimeInputs` 语义）——KM 的 `predict` 用 searchsorted，乱序输入不报错但结果错位。
- **坑 4**：想修死代码（删 L115 或让告警分支提前 return 1）注意同步修 L112 的文案——只删行不修文案会留下新的漂移，这是 ONBOARDING 已钉版的教训。

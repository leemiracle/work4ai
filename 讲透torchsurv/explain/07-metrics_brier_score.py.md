# `src/torchsurv/metrics/brier_score.py`：Graf 删失校正 Brier 分与 IBS

## 一、角色定位

一句话：实现**时间依赖 Brier 分**（Graf 1999 删失校正版均方误差）及其积分 IBS、参数法/bootstrap 双引擎推断——三件套中唯一的 calibration（校准）指标，吃的是生存概率而非风险分。位于 **L2 模型评估指标层**。与 Auc/C-index 的分工：后两者量 discrimination（能不能排序），本文件量"预测的 S(t) 与真实事件状态差多少"——生存分析里"在哪个时刻、对谁、以什么权重算平方误差"三问的答案全在这里。

## 二、内部结构

单类 `BrierScore`（`src/torchsurv/metrics/brier_score.py:14`），18 个方法：

**构造 `__init__`**（L17）：9 个状态槽（L41-49），order_time/residuals 等全部 None 起步。

**点估计 `__call__`**（L51）四段：
1. 输入流水线：squeeze（L167-168）→ `_validate_brier_score_inputs`（L171，定义 L780：weight 与 weight_new_time 配对检查 L788-789、estimate 必须落在 [0,1] 的概率区间 L792-793、必须 2-D L796、列数与 time 匹配 L799-803）→ `_update_brier_score_new_time`（L174-179，定义 L807：new_time 缺省时取全部唯一时间并同步选列 L824-830）→ `_update_brier_score_weight`（L180，定义 L837：缺省补 1）→ jit 场景外的 `SurvivalInputs` + `NewTimeInputs(within_follow_up=False)`（L183-186）。
2. **残差核**（L189-197）：逐评估时刻循环，`is_case = (time <= t) & event`（L192）、`is_control = time > t`（L193），残差 = `S_i(t)² · case · ω(T_i) + (1-S_i(t))² · control · ω(t)`（L196）——case 项权重用主体自身时刻的 IPCW、control 项权重用评估时刻的 IPCW，这就是 Graf 估计量的双权重结构；删失在 t 前的样本两项都不进（自然零贡献），偏倚由权重放大纠正。
3. 归约：`torch.mean(residuals, axis=0)`（L200）出各时刻 BS。
4. `instate` 存状态（L203-213）——注意按 time 排序后存（L205 的 argsort + L211 的 index_select），residuals 留给推断引擎逐样本复用。

**积分 `integral`**（L217）：单一时刻直返（L254-255），否则 `torch.trapezoid(bs, new_time) / (t_max - t_min)`（L257）——IBS 定义 ∫BS dW(t)、W(t)=t/t₂，归一化分母就是时间窗长。

**推断双引擎**：`confidence_interval`（L260，默认 parametric）/`p_value`（L330，默认 bootstrap 置换）/`compare`（L410，默认 parametric）三门面，分派到 `_confidence_interval_parametric`（L485）与 `_bootstrap`（L512）、`_p_value_parametric`（L554）与 `_p_value_bootstrap`（L582）、`_compare_parametric`（L613）与 `_compare_bootstrap`（L646）。`_brier_score_se`（L478）是参数法的 SE 入口（基于 residuals 的影响函数式和），`_bootstrap_brier_score`（L670）统一三种重采样语义。

**工具组**：`_find_torch_unique_indices`（L760）——torch.unique 的逆索引换算，Auc 里有逐字相同的复制品。

## 三、外部连接

- **imports 出边**：`tools/validators.py`（本文件 L9 引 `NewTimeInputs`/`SurvivalInputs`）+ scipy.stats（L7）。注意它不依赖 KM/ipcw——删失校正权重作为参数从外部进来。
- **上游**：`src/torchsurv/__init__.py:12` 与 `metrics/__init__.py` re-export；`README.md`、`docs/metrics.rst`、`docs/notebooks/metrics.md`、`docs/package_overview.md` 引用。
- **tested_by**：`tests/test_brier_score.py`（R 对拍，`benchmark_script/test_brier_score.R` 用 pec 包生成参照）、`tests/test_hypothesis.py`（[0,1] 值域属性）。
- **与其他件的协作边**：典型调用链里它消费 `stats/ipcw.py:17` 的 `get_ipcw` 两次（time 处与 new_time 处，docstring 示例 L143-152）与损失侧的 `survival_function*` 输出——它是"损失产出概率 → 指标评估概率"这条数据流的终点。

## 四、数据流

评估走读（test split）：损失侧 `survival_function_cox`/`survival_function_weibull`/`survival_function` 出 `estimate (N, T)` 存活概率 → 训练集上 `get_ipcw(train_event, train_time)` 得 ω(T_i)、`get_ipcw(train_event, train_time, new_time)` 得 ω(t_k) → `bs = BrierScore()(estimate, test_event, test_time, new_time, ipcw, ipcw_new_time)` → 残差核逐时刻算加权平方误差 → `tensor([bs_1,...,bs_T])` → `bs.integral()` 梯形归一出 IBS 单值 → `bs.confidence_interval()` 参数法沿 residuals 影响函数出各时刻上下界。

无 new_time 的简写：estimate 给 `(N,N)`（每主体在其他主体时刻上的生存概率），L824 的 unique 自动把列收缩到唯一时刻——与 Auc 的差别是这里不排除最大时刻（Auc 的 mask 有 `time < max(time))` 截断，Brier 没有）。

## 五、设计决策

**为什么残差核用逐时刻 Python 循环（L190-197）而不是全张量广播？** 每个时刻的 is_case/is_control 掩码与 `weight_new_time[index]` 标量配对，广播版本需要构造 `(N,T)` 的权重矩阵再逐列点积——内存翻 N×T 倍。T 通常不过几十，循环换内存是清醒的取舍（与 Auc 的全张量路线相反，因 Auc 的排序无法逐列剥离）。

**`within_follow_up=False`（L186）**：评估时刻允许落在随访窗外——外推评估（train 窗 [0,10y]、test 想看 12y）是合法需求，Brier 把这个检查交给用户；对比 cindex/auc 的 NewTimeInputs 用默认 True。同一名词两种严格度，是"评估时刻语义本就不同"的体现。

**case/control 双权重不对称（L196）**：case 项的 ω(T_i) 校正"事件被删失截掉"的缺失，control 项的 ω(t) 校正"还没到时刻 t 就被删失"的缺失——两个缺失机制不同权重不同。这是 Graf 公式的核心，也是与朴素"补 0/删样本"两个错误做法的分水岭。

**批判视角**：① IBS 的 W(t)=t/t₂ 权重（L246）隐含"均匀时间重要性"假设，临床场景常想加权早期时刻——接口未暴露权重函数，只能事后自己拿 brier_score 张量加权；② [0,1] 区间检查（L792-793）拦住风险分误用，但拦不住"S(t) 单调性破坏"的劣质概率输出——校准指标不查单调性，配合 KM 诊断食用；③ `_find_torch_unique_indices` 在 Auc/Brier 两文件重复出现（L760 与 auc.py L1104），是三件套共享工具未上提的显性复制粘贴债——重构方向明显（挪进 tools/），但同样被 R 对拍的行为锁定劝退。

## 六、新人提示

- **上手顺序**：先读 `__call__` docstring 的 Graf 公式节（L101-129，双权重的推导动机），再读残差核五行（L189-200），最后 `integral`（L217-258）；`docs/notebooks/introduction.ipynb` 的 GBSG2 全流程有本指标的实际调用。
- **坑 1**：estimate 必须是生存概率（越大越安全），与 cindex 吃风险分（越大越危险）方向相反——两指标共用一个网络输出时先变换符号/取补。
- **坑 2**：`weight` 与 `weight_new_time` 必须成对出现（L788-789），且都来自训练集删失分布；只给前者会在校验层被拦，报错文案直接告诉你缺谁。
- **坑 3**：`integral()` 只在 `__call__` 之后有效（L251-252 的 assert）——顺序反了会得到 AssertionError 而非静默错值，这是三件套的统一防御。
- **坑 4**：jit 场景（L183）跳过 pydantic 校验但保留 `_validate_brier_score_inputs` 的轻量检查——编译路径上区间/维度错误仍会报，只是报错信息少了 validators 的细节。

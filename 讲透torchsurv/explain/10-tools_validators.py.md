# `src/torchsurv/tools/validators.py`：pydantic 输入定型——全仓代码依赖的汇聚点

## 一、角色定位

一句话：以 **pydantic v2 模型家族**统一完成全部公共入口的输入定型（类型强转 + 语义校验），是 src 内 imports 扇入最高的文件（11 条）——改输入格式只动这一个文件。位于 **L3 统计估计与输入校验基础层**（虽在 tools/ 目录，图谱将其与 KM/IPCW 同层归为"被损失与指标共用的底层设施"）。TorchSurv 的报错体验（带具体维度的 ValueError）全部产自这里。

## 二、内部结构

468 行，2 个私有助手 + 1 个基类 + 5 个输入模型 + 1 个张量函数：

- **`_to_float_tensor`**（`src/torchsurv/tools/validators.py:22`）：非 Tensor 拒收（L34-35）、NaN 拒收（L37-38）、Inf 默认拒收但 `allow_inf=True` 可放行（L39-40，log_params/log_hz 需要——训练初期 inf 是告警素材而非错误）。`_to_bool_tensor`（L44）同构。
- **`_TorchModel`**（L60）：唯一职责是 `arbitrary_types_allowed=True`（L63）——pydantic 默认不认 torch.Tensor 字段，这个 ConfigDict 是全部模型的地基。
- **`SurvivalInputs`**（L71）：event/time/strata 三字段（L119-121）。`coerce_event` 强制 bool 且**至少一个事件**（L125-129，全删失报"All samples are censored"）；`coerce_time` 非负（L133-137）；`coerce_strata` 转 long（L141-146）；`check_dimensions`（model_validator after 模式，L149）查三者等长（L150-154）、strata 缺省补全 1（L155-156）。
- **`ModelInputs`**（L160）：log_params/event/model_type 三字段（L202-204），`model_type` 是 `Literal["cox","weibull","survival"]`（L204）+ 小写化/去空格（L218-221，`"  COX  "` 合法）。`check_shape`（L224-249）按模型分派形状约定——weibull 限 1/2 维、列限 1/2 并调 `impute_missing_log_shape` 归一成 `(n,2)`（L230-240）；cox 限 `(n,)` 或方阵 `(n,n)`（L241-245）；survival 强制 2-D `(n, n_eval)`（L246-248）。
- **`NewTimeInputs`**（L252）：评估时刻。`check_new_time`（L304-315）三查——升序（L305-307）、无重复（L308-309）、默认须落在随访窗 `[min(time), max(time))`（L310-314，**左闭右开**：上界时刻本身不许评）；`within_follow_up=False` 可跳过范围检查（L283-286 的 doctest 演示）。
- **`EvalTimeInputs`**（L318）：灵活模型的网格一致性。log_hz 必须 2-D（L360-361）、列数与 eval_times 等长（L362-366）、eval_times 严格递增无重复（L367-368）。
- **`TimeVaryingCoxInputs`**（L372）：扩展 Cox 的并列时刻列一致性。向量化找并列位置 `tie_indices = (time[:-1] == time[1:]).nonzero()`（L425），逐对 `torch.allclose` 比列（L426-432）——同一时刻的两个列必须是同一函数值，防长表错位。
- **`impute_missing_log_shape`**（L436）：唯一的 `@torch.jit.script` 函数（L436 装饰），`(n,)`/`(n,1)` 补零列升 `(n,2)`（L464-467）。jit 化是因为 weibull 的计算函数在 jit 路径上也要调它，而 pydantic 模型在 jit 下不可用——校验跳过、归一不跳过。

## 三、外部连接

- **入边 11 条 imports（全仓最高）**：`loss/cox.py`、`loss/survival.py`、`loss/weibull.py`、`metrics/auc.py`、`metrics/brier_score.py`、`metrics/cindex.py`、`stats/ipcw.py`、`stats/kaplan_meier.py`、`tools/__init__.py`、`tests/test_cox.py`、`tests/test_validators.py`。除 momentum（纯训练机制无公共输入面）外，src 所有实现文件都汇聚于此。
- **出边**：五个模型类与两个函数各成图谱节点；`tests/test_validators.py` 专测本文件（唯一被独立单测的内部设施）。
- **第三方**：pydantic v2（L6，`BaseModel`/`ConfigDict`/`field_validator`/`model_validator`）——运行依赖五包之一，`pyproject.toml:35` 钉 `pydantic>=2.0`。
- **消费模式钉版**：所有调用方都写 `if not (torch.jit.is_scripting() or torch.jit.is_tracing()):` 再实例化模型（如 `cox.py:407-412`）——pydantic 的动态类构造与 torch.compile 不兼容，这一行 guard 是"校验只挡人、不挡编译器"的边界。

## 四、数据流

一次错误输入的完整旅程：用户把 `(N,1)` 的 log_hz 传给 `neg_partial_log_likelihood` → 函数体先 squeeze（`cox.py:402`）→ jit guard 内 `ModelInputs(log_params=log_hz, event=event, model_type="cox")`（`cox.py:411`）→ field_validator 链先跑：log_params 转 float（放行 inf）、event 转 bool → model_validator `check_shape` 后跑：cox 分支发现 2-D 但非方阵 → pydantic 抛 `ValidationError`（内含 "Value error, For Cox model, 'log_hz' must have shape (n_samples,) or (n_samples, n_samples)."）→ 用户看到带形状约定的报错。正常输入则原路返回**定型后的张量**（bool 化的 event、float 化的 time、补全的 strata），调用方用返回值覆写局部变量继续算——校验与归一一次完成。

分层语义对照：同一个 new_time，在 `NewTimeInputs`（BrierScore 的 L186 传 `within_follow_up=False`）与 `EvalTimeInputs`（严格网格）里要求不同——模型族而非文件族决定校验强度。

## 五、设计决策

**为什么 pydantic 而不是手写 if 链？** 11 个入口 × 每入口 3-5 项检查 ≈ 40+ 条规则，手写散布在各文件会漂移；pydantic 的 field_validator（before 模式做强转）+ model_validator（after 模式做跨字段）把"逐字段"与"跨字段"两类检查正交化，且 doctest 直接写在模型 docstring 里（`SurvivalInputs` 的 L78-116 有 6 组正反示例）随 `dev/run-doctests.sh` 执行——校验规则与它的证明住同一个文件。

**强转优于报错（event int→bool 静默转）**：生存数据的 event 常以 0/1 int 存储，R 转 Python 的肌肉记忆是 1/0；拒收会制造大量无谓报错。代价是语义模糊输入（0.5）被 `v.bool()` 截断成 True/False——两可之间选择了宽容。

**allow_inf 的分级**：time 上的 inf 一定是数据错误（拒），log_params 上的 inf 是训练早期现象（放，让损失层自己的 inf 剔除机制处理）——同一个助手函数按字段分极，避免一刀切。

**批判视角**：① pydantic 模型每 batch 实例化一次，大 N 高频训练循环里有可测的固定开销（guard 只挡了 jit，没挡 eager 的热路径）——损失函数每步都过校验属于"安全税"，追求极限吞吐的用户得自行 bypass；② `NewTimeInputs` 的左闭右开窗口（L311）语义精确但反直觉（`new_time == max(time)` 被拒），报错文案里的 `[1.0, 5.0)` 数学记号是唯一提示；③ strata 的缺省补全（L155-156）让"用户没传"与"用户传了全 1"不可区分，cox.py 的分层循环因此总跑一遍单层——正确但多一层间接。

## 六、新人提示

- **上手顺序**：先读 `_TorchModel` 与 `SurvivalInputs`（最简完整样例，含正反 doctest），再按 cox→weibull/survival→new_time→eval_time 的消费顺序读各模型，最后 `impute_missing_log_shape`；`tests/test_validators.py` 是行为规格书。
- **坑 1**：加新模型族要同时动 `model_type` 的 Literal（L204）与 `check_shape` 分支（L224-249）——漏 Literal 会在 normalize 阶段就报字面量错误，信息不在形状层。
- **坑 2**：`torch.jit.script` 下校验整体跳过，坏输入在 jit 路径会走到深处才炸——给 compile 场景写测试要在 eager 下先过一遍校验。
- **坑 3**：`impute_missing_log_shape` 是幂等的但**不查越界**——`(n,3)` 的 weibull 参数会先被 L235-238 的列数检查拦下，但绕过 ModelInputs 直接调它时 `(n,3)` 原样返回。
- **坑 4**：报错是 `ValidationError` 不是裸 `ValueError`——`pytest.raises(ValueError)` 能捕到（pydantic 继承链），但断言 message 时要用 `e.errors()[0]["msg"]` 的形式（doctest L104-108 是标准写法）。

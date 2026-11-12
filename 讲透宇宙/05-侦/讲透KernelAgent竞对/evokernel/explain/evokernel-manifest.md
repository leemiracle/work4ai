# EvoKernel 五份 manifest.json 深解（集合级账本）

> 对象：`ops-{attention,kernelbench,mhc}-{cuda-ncu,910b}` 五集合各一份 manifest.json，合计 **567 个 kernel**（79+250+58+165+15）。图谱定位：数据集定义层（`layer:dataset-definition`），与 README 数据集卡片同级，向下以 `related` 边连接各 kernel 目录的 `result.json`/`best_code.py`/`op_host`/`op_kernel`，向上由 `pytorch-references/`（Attention/KernelBench level1-3/MHC 参考实现）标注任务来源。

## ① 角色定位：集合级账本

manifest 是每个集合的**汇总索引与质量账本**。每个 kernel 目录内都有自己的 `result.json`（单条实验记录）与最优产物（CUDA 集合是 `best_code.py`，910B 集合是 Ascend CANN 的 `op_host`/`op_kernel` 源码对）；manifest 把这几百条记录聚合成三件事——集合里有什么（kernels 名录）、质量如何（编译率/正确率）、跑多快（性能统计）。它让使用者不必逐个打开 567 个目录就能完成采样、筛选与价值评估，是 EvoKernel 数据集（HF `noahli/EvoKernel`，论文 arXiv:2603.10846，主打"冷启动起草+持续精炼"的价值驱动内核合成）的选样入口。五个集合覆盖两条硬件线：CUDA+NCU 剖析线（attention 79 + KernelBench 250）与昇腾 910B NPU 线（attention 58 + KernelBench 迁移 165 + MHC 算子族 15），任务源均可回溯到 `pytorch-references/` 下的参考实现。

## ② Schema 解剖

顶层三个字段，职责清晰：

- **`exported_operator_count`**：导出算子总数（= `len(kernels)`，五集合实测均自洽）。它是集合规模的"封面数字"，快速引用时用它，做统计时仍以下方数组为准。
- **`summary`**：集合级聚合账。`compiled_true`/`correctness_true` 是通过计数，`compiled_rate`/`correctness_rate` 是对应比率（分母为全部导出数，含失败样本）；910B 三集合另有 `faster_than_baseline` 计数，CUDA-NCU 两集合则**根本没有该字段**——字段有无本身就是"是否做了基线对比"的元信息。
- **`kernels[]`**：逐 kernel 记录，存在两条 schema 谱系：
  - **公共字段**：`kernel_project_name`（既是显示名也是目录名/连接键）；`outer_iter` 与 `inner_iter` 是搜索/精炼的迭代计数——全库 `inner_iter` 恒为 1，实际信息全在 `outer_iter`（可解读为"产出该导出所耗的外层进化轮数"，触顶即预算耗尽）；`compiled`(bool) 与 `correctness`(bool|null) 是两级质量门。
  - **嵌套式**（四个 attention/kernelbench 集合）：性能收进 `performance{mean, std, min, max, num_trials}`。CUDA-NCU 组 `num_trials=5`，即固定 5 次计时试验并给出 min/max/std 三统计，可做方差感知筛选；910B 组结构同名但 `num_trials=null`，试验次数未记录。
  - **平铺式**（仅 MHC-910b）：`mean_ms`、`baseline_mean_ms`、`speedup_vs_baseline`（基线/实测之比）、`log2_speedup_vs_baseline`（已对称化，快/慢等距）、`relative_change_pct`（百分数相对变化）五字段直接平铺在 kernel 记录上——全库**唯一**携带 PyTorch 基线对比与相对价值判断的集合。
  - **null 级联语义**：`compiled=false` ⇒ `correctness=null` ⇒ 性能字段全 null。这是"未测"而非"为零"：attention-cuda 的 2 个正确性失败样本同样 `performance=null`。做性能统计前必须显式排除 null。

## ③ 五集合对比表

| 集合 | 数量 | 编译率 | 正确率 | faster_than_baseline | outer_iter 中位(范围) | 性能字段 | num_trials |
|---|---|---|---|---|---|---|---|
| attention-cuda-ncu | 79 | 100% | 97.5% (77) | **字段缺失** | 22 (1–30) | 嵌套 performance | 5 |
| kernelbench-cuda-ncu | 250 | 100% | 100% | **字段缺失** | 18 (1–27) | 嵌套 performance | 5 |
| attention-910b | 58 | 100% | 100% | 0 | 18 (3–30) | 嵌套 performance | null |
| kernelbench-910b | 165 | 100% | 100% | 0 | 24 (2–30) | 嵌套 performance | null |
| mhc-910b | 15 | 66.7% (10) | 66.7% (10) | **6** | 30 (17–39) | **平铺 5 字段（含基线）** | — |

命名口径也不同：CUDA 集合保留 KernelBench/任务编号名（`1_ScaledDotProductAttention`），910B 集合为 `XxxCustom` 后缀的 CANN 自定义算子名。

## ④ 统计画像

- **全对集合**：kernelbench-cuda（250/250）、attention-910b（58/58）、kernelbench-910b（165/165）——编译、正确率双满分，是"干净数据"主力。
- **attention-cuda 77/79**：仅 `20_BigBirdAttention`、`48_S2Attention` 两个正确性失败（性能字段随之 null），都是稀疏/结构化注意力这类实现复杂度高的变体。
- **MHC 为何 10/15**：5 个编译失败样本（FusedMhcKernels/MhcBlock2d/MhcBlockBottleneck2d/MhcModule/StaticMhcHyperConnections）的 `outer_iter` **全部触顶 39**——搜索预算耗尽仍未产出可编译内核，而非"测出错误"。失败的恰是复合粒度最大的算子（融合组、模块级 Block、超连接结构），印证"合成范围越大，CANN 冷启动编译越难"；MHC 的预算上限 39 也高于其他集合的 27–30。注意其 `baseline_mean_ms` 在失败样本上仍 populated，可独立用于基线侧分析。
- **MHC 编译≠快**：10 个过验算子中仅 6 个快于 PyTorch 基线，形成 6 win / 4 trap / 5 编译失败的天然三分。最优 `SinkhornKnoppCustom` 41.96×（0.027 vs 1.133ms），最差 `MhcPreBlockCustom` 慢约 86×（112.474ms vs 1.31ms）——同一集合内相对价值横跨近四个数量级。
- **耗时量级**（performance.mean 范围）：attention-cuda 0.011–63.4、kernelbench-cuda 0.032–629.3、attention-910b 0.04–9751.5、kernelbench-910b 0.003–118827.4（中位即高达 4479）。

## ⑤ 使用建议

1. **采样入口**：标准流程是"summary 选集合 → compiled/correctness 过滤 → `kernel_project_name` 拼路径进目录"。该字段就是目录名与图谱连接键，manifest 经 `related` 边直达各 kernel 的 `result.json` 与最优代码（CUDA=`best_code.py`，910B=`op_host`/`op_kernel`）。
2. **方差感知筛选**：CUDA 组有 `num_trials=5` 与 `std`，可按变异系数（std/mean）剔除不稳样本；910B 组 `num_trials=null`，应视为单次测量，任何基于它的结论都要降级表述或自行复测。
3. **价值评估只有 MHC 能做**：`log2_speedup_vs_baseline` 已对称化，正=快于基线、负=慢于基线且等距，可直接作 win/trap 轴做图与统计；6 win/4 trap/5 编译失败的 15 样本结构，恰好是迁移定律类研究（win/trap 可交换性、冷启动失败模式）现成的小型压力测试集。其余集合的 `performance.mean` 只能做**集合内**排序，不能当"是否优于基线"的证据。
4. **搜索成本研究**：`outer_iter` 是"找到可编译解所耗轮数"的代理变量——触顶（27/30/39）= 预算耗尽，小值 = 快速收敛，可与算子类型交叉做难度分层采样。
5. **失败样本别丢**：MHC 的 5 个编译失败 + attention-cuda 的 2 个正确性失败是数据集里稀缺的负样本，做失败模式分析或鲁棒性检验时反向筛选即可。

## ⑥ 数据质量警示

- **`performance.mean` 跨集合单位口径未声明**：仅 MHC 字段名自带 `ms`。kernelbench-910b 中位 4479、最大 118827——若按 ms 解读为 4.5s/119s 明显异常，疑为 μs 或含同步开销的另一种测量口径；跨集合比较原始 mean 前必须回查 `result.json` 校准单位与计时方式（NPU vs GPU、num_trials 5 vs null 亦不可比）。
- **`faster_than_baseline: 0` ≠ 全败**：attention-910b/kernelbench-910b 逐 kernel 记录里**没有任何基线字段**，该 0 应理解为"基线对比未执行/未导出"而非"0 个快于基线"（推断，使用前核实）。
- **null 级联**：过滤性能分布时须显式排除 null，否则 MHC 的 5 个失败样本会把统计拉向 0。
- **计数以 kernels[] 为准**：`exported_operator_count` 与数组长度虽当前一致，聚合统计建议直接重算以防字段漂移。

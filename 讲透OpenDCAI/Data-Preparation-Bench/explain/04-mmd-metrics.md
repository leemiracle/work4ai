# 04 · MMD 距离与指标层：MMDDistance、DASMetric 与名字不匹配的坑

## 角色定位

`src/distflow/mmd.py` + `src/distflow/metrics/` 构成基准第三板块"数据质量评测"的数学内核。回答的问题：**不看下游训练，仅凭嵌入分布能否预测候选数据集的微调收益？** 手段是把候选集与目标集映射到嵌入空间算 MMD（Maximum Mean Discrepancy），距离越近对齐越好，取负号即 DAS 分数（Distributional Alignment Score）。examples/run_benchmark.py:12 的注释给出闭环：指标分数与真实下游 accuracy 做相关分析，验证"分布对齐分数"是不是好代理。

## 内部结构

**MMDDistance（mmd.py:13-209）**。构造参数：kernel 仅 RBF（L38 直接 assert）；`rbf_sigma=1.0` 默认固定；`bias=True` 选有偏/无偏估计；`max_fail_ratio=0.02` 嵌入失败容忍上限。计算链三步：`compute`（L101-130）对 src/tgt 分别 embed，过 `_filter_embeddings`（L66-99）滤 None——失败率超阈值抛 RuntimeError，宁可终止不让残缺样本污染分布；`_compute_kernel`（L43-64）cdist 平方欧氏距离经 `exp(−d²/2σ²)` 得 RBF 核；`_compute_distance`（L132-209）有偏估计 `mean(Kxx)+mean(Kyy)−2·mean(Kxy)` 开方（L166-169），无偏排除对角线自相似 `(sum(Kxx)−n)/(n(n−1))`（L172-178）。meta 除三项核均值外，塞进 `ndarray_summary`/`embedding_list_summary`（utils/stats.py:8-111）统计摘要，把"数怎么算的"完整落盘。

**指标层**。`metrics/types.py:6-9` MetricsResult 三元组 name/value/meta；`metrics/protocol.py:7-8` MetricsProtocol 要求指标类有 `score(dataset) -> list[MetricsResult]`；`metrics/dsa.py:9-34` DASMetric 构造时固定 target_set 并内置 MMDDistance，`compute(candidate)` 返回 `[MetricsResult(name="DAS", value=-mmd_value)]`——**负号是全部语义**：MMD 越小对齐越好，取负后与 accuracy 方向一致。

**消费方 benchmark.py**。`DataQualityEvaluatorBenchmark`（L20-75）持数据集列表与人工测得的 accuracys（键集合与 dataset.name 全等，L24-26 断言）；`run_benchmark`（L28-52）对每数据集调 `metrics.score(dataset)` 聚合成 (accuracy, metric) 点对；`_compute_benchmark_result`（L54-75）np.polyfit 拟合斜率 + pearson/spearman 双相关及 p 值。

## 外部连接

向上依赖 embed 子系统（三后端可换）；数据侧依赖 `data/dataset.py` DistflowDataset——load_type 三通道 datasets/modelscope/pandas（L53-84），cached_property 只加载一次（L42-102），shuffle_seed+data_size 保采样可复现。examples 双入口：compute_mmd.py 与 run_benchmark.py（DummyMetrics 占位演示）。

## 数据流

```
DistflowDataset.load() → list[DatasetProcessOutputItem]
  → DASMetric.compute → MMDDistance.compute(target, candidate)
  → 两侧 embed → 滤 None → 三核矩阵 → MMD + meta
  → MetricsResult("DAS", -mmd) → Benchmark 与 accuracy 配对
```

## 设计决策（含批判）

1. **头号坑：DASMetric.compute 与 MetricsProtocol.score 名字不匹配**。协议要求 `score`，DASMetric 实现的是 `compute`（dsa.py:28），**不满足协议**——把 DASMetric 传给 run_benchmark，benchmark.py:31 的 `metrics.score(dataset)` 运行时直接 AttributeError；开 pyright 则静态期就标红（Protocol 结构化检查，方法名对上才算数）。examples/run_benchmark.py:26-28 的 DummyMetrics 老实写 `score` 才是可运行姿势。方法名漂移正是结构化类型最常见的翻车点。
2. **rbf_sigma=1.0 写死，无 median heuristic**：RBF 带宽对嵌入尺度极敏感，换嵌入模型距离尺度就变，跨实验 MMD 值不可直接比大小。改进：按成对距离中位数自适应带宽。
3. **无偏 MMD² 估计可能为负**，L172-178 开方前无 clip——负值产出 NaN，meta 的 kernel_terms 可助诊断。
4. meta 落统计摘要而非原始矩阵（防 JSON 爆体积），值得抄。

## 新人提示

先读 mmd.py 三方法（compute → _compute_kernel → _compute_distance 三段式），对照 run_benchmark.py 理解"指标怎么被消费"。动手任务：(1) 给 DASMetric 加 `score = compute` 别名修复协议不匹配，跑通 run_benchmark；(2) 实现 median-heuristic sigma，对比固定 sigma 下 DAS 与 accuracy 相关性——本身就是一个小消融。

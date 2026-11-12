# 03 · mpu 分布式栈与损失家族：并行原语 × 评分函数

## 角色定位

`makani/mpu/` 是自制模型并行算子库（不依赖 Megatron，为球面网格定制），`makani/utils/loss*.py`+`metric.py` 把气象评分函数（CRPS/能量分数/ACC 等）代码化。两者一个管"怎么切"，一个管"怎么评分"，合起来是 makani 区别于通用训练框架的两块领域肌肉。

## 内部结构

**mappings.py（544 行）——并行区映射原语**：autograd.Function 五件 `_DistributedTranspose`:38、`_CopyToParallelRegion`:70、`_ReduceFromParallelRegion`:94、`_ScatterToParallelRegion`:117、`_GatherFromParallelRegion`:152（forward/backward 显式写通信，模仿 Megatron 的区映射语义）；公开接口 copy/reduce/scatter/gather/transpose 五件（mappings.py:186-220）全部带 `comm_id` 命名进程组参数；mappings.py:333 `init_gradient_reduction_hooks` 给参数挂梯度归约钩子（含 mappings.py:255 `gradient_print_wrapper` 调试件）。

**halo.py（406 行）**：分布式球面网格的 halo 交换与方位角（经度环绕）交换——空间并行（h/w 切分）下邻居边界通信。

**layers.py（1091 行）——通道并行层动物园**：`DistributedMatmul`:35、`DistributedEncoderDecoder`:248、`DistributedMLP`:386、`StochasticMLP`:577（随机插值专用）、`DistributedPatchEmbed`:835、`DistributedAttention`:960——全部消费 fin/fout 通道并行区。

**layer_norm.py——分布式归一化**：统计量跨 rank 合并用 Welford 在线算法，`_welford_kernel`:55 是 **@torch.compile 融合核（非手写 CUDA 源码）**，`distributed_welford_variance`:84 先本地统计再 `gather_from_parallel_region` 归约。`fft.py` 分布式 FFT 与 `_amp_utils.py` fp8 AMP 工具同层。

**损失侧**：`LossHandler`（utils/loss.py:58，550 行——注意在 utils/ 根不在 losses/ 目录）按 config 组合加权：`_parse_loss_type`:282、多步权重 `_compute_multistep_weight`:239、运行统计 `_update_running_stats`:297/`get_running_stats`:325、缺测掩码 `_mask_missing_targets`:349、集成均值 `_ensemble_mean`:340、forward:403 统一入口。CRPS 家族（losses/crps_loss.py 1196 行）：核函数 `_crps_ensemble_kernel`:55、`_crps_skillspread_kernel`:105、`_crps_probability_weighted_moment_kernel`:134、`_crps_naive_skillspread_kernel`:161、`_crps_gauss_kernel`:187；类五件 `CRPSLoss`:220（GeometricBaseLoss）、`SpectralCRPSLoss`:398（SpectralBaseLoss）、`GradientCRPSLoss`:585、`VortDivCRPSLoss`:795、`KernelScoreLoss`:971；`rankdata`:42 辅助。能量分数家族（energy_score.py 997 行）：`LpEnergyScoreLoss`:30、`SobolevEnergyScoreLoss`:244、`SpectralL2EnergyScoreLoss`:438、`SpectralCoherenceLoss`:618、`CorrectedSpectralL2EnergyScoreLoss`:822。基类四类在 base_loss.py:310 `GeometricBaseLoss`/base_loss.py:364 `SpectralBaseLoss`/base_loss.py:446 `VortDivBaseLoss`/base_loss.py:537 `GradientBaseLoss`（base_loss.py:263 `LossType` 枚举），专题损失 amse/hydrostatic/likelihood/mmd/regularization 各一文件。指标侧 metric.py:47 `MetricRollout`、metric.py:260 `MetricsHandler` + functions.py（746 行，L1/RMSE/ACC/Spread/SSR/RankHistogram）。

## 外部连接

comm.py:34 `_initialize_manager` 建立命名进程组——mpu 一切 `comm_id` 的来源（comm.py:116 get_group；comm.py 全 322 行，图谱 fanIn=64）；mpu 层被 networks 的并行版消费（README.md:48-50 并行表：fin/fout 通道、h/w 空间、ensemble）；损失/指标被四 Trainer 与 Inferencer 消费，rollout 期统计汇入 rollout_buffer。

## 数据流

并行前向：输入在数据并行区分片 → PatchEmbed/层在通道并行区 scatter/gather（mappings.py:204/:212）→ 空间切分处 halo 交换（halo.py）→ 归一化统计 Welford 跨 rank 归约（layer_norm.py:84）→ 反向经梯度归约钩子（mappings.py:333）。损失流：预报/真值对 → LossHandler 按配置实例化各损失项加权求和（含多步衰减、缺测掩码、集成成员维）→ 指标侧 MetricsHandler 同源装配。

## 设计决策

1. **autograd.Function 手写通信**：scatter/gather 的 forward 与 backward 通信方向相反，显式写比 autograd 自动推导可靠（mappings.py:70-184）。
2. **Welford 而非两遍统计**：在线算法一轮合并 mean/var/count，数值稳且省一遍数据（layer_norm.py:55-84）。
3. **命名进程组分治**：数据/模型/IO 组各自命名，避免全局通信互相阻塞（comm.py）。
4. **损失即配置**：LossHandler 从 yaml 实例化损失项，损失家族做成可组合基类树（GeometricBaseLoss/SpectralBaseLoss 等）。
5. **test_losses.py 4282 行 31 类是契约**：每个损失变体（谱/梯度/涡散/核/能量分数）都有独立 TestCase（:253-4208），改损失先跑它。

## 新人提示

找 LossHandler 别在 losses/ 目录里翻（在 utils/loss.py:58）；"Welford CUDA 核"的说法要修正为 torch.compile 融合核（layer_norm.py:55）；新损失类先继承正确的基类（谱系看 crps_loss.py:220/:398 两例）再注册进 yaml 可解析名；调试并行减脂先开 `gradient_print_wrapper`（mappings.py:255）；指标对齐 WeatherBench2 的口径在 functions.py，别自造公式。

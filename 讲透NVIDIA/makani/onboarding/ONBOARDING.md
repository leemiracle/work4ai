# Makani 上手指南（ONBOARDING）

> 仓：github.com/NVIDIA/makani（本地 `/usr-data/data2/repos/agent-repos/NVIDIA/makani`，HEAD `3fdeb7a6`）
> 图谱：`.understand-anything/knowledge-graph.json`（680 节点 / 1606 边 / 14 层 / 16 步导览，fingerprints 231 文件基线）
> 论文线：FourCastNet3（arXiv 2507.12144）/ SFNO（2306.03838）/ HENS-SFNO（2408.03100）/ FourCastNet1（2202.11214），均经 README.md:9 链接钉版

## 1. 一句话定位：AI 天气/气候模型大规模并行训练库

**Makani 不是 HPC 网络测试工具（任务书原判断被源码推翻）**，而是 NVIDIA+NERSC 联合研究代码——用 PyTorch 在 **100+ GPU 上大规模并行训练 ML 天气/气候预报模型**的库（README.md:1、README.md:19）。Makani 是夏威夷语"风"（README.md:9）。它训练出了 FourCastNet3（旗舰，Disco 连续编解码神经算子）、FourCastNet2 用的 SFNO 球面傅里叶神经算子、HENS 巨型集合 SFNO、FourCastNet1 AFNO。能力面：模型/数据/集成多种并行、异步数据加载、动态静态输入特征、自回归训练、全在线评分（WeatherBench2 兼容）、yaml 全配置化研究工作流。

七个用户入口全是薄壳：`makani/train.py`（确定性训练）、`train_stochastic.py`（随机插值）、`train_autoencoder.py`、`ensemble.py`（集合）、`inference.py`（推理评分）、`benchmark.py`（657 行计时）、`convert_checkpoint.py`（分片检查点合并）——重量级逻辑全部下沉到 Driver/Trainer。

## 2. 配置链：yaml target × CLI flag 双件

配置链两端：`makani/utils/YParams.py` 把 yaml target 展开为属性访问对象；`makani/utils/argument_parser.py`（181 行）定义全部 CLI flag，flag 覆盖 yaml。旗舰配置 `config/fourcastnet3.yaml`（438 行）：`base_config`（L1 anchor）声明数据元信息（metadata_json_path:4）、网格 721×1440（:13-14）、归一化 stats 五件套（mins/maxs/time_means/global_means/global_stds :17-24）、架构超参（nettype FCN3:24、atmo/surf/aux_embed_dim、num_layers 10、sfno_block_frequency 5、filter_basis_type morlet、kernel_shape [3,3]）；`ensemble_base`:144/`ensemble_finetune`:174 是集合多 target。其他架构配方：sfnonet.yaml、icml_models（HENS）、afnonet、pangu、vit、debug。

数据元信息解析在 `makani/utils/parse_dataset_metada.py`（**文件名缺 't' 的历史拼写**，函数名 `parse_dataset_metadata`:22 正确）：读 metadata json，要求 `coords.grid_type` 必填——缺了直接 ValueError，注释明言"旧版静默默认 equiangular 对所有非该网格数据集都是错的"（:37-45）；`coords.lat/lon` 缺席时按 grid_type 重建纬经度（:50-62，纬度北向南存）。五个 CLI 入口都过它（train.py:149-150、inference.py:259-260、ensemble.py:169-170、train_stochastic.py:163-164、train_autoencoder.py:142）。

## 3. 仓库地图（图谱 14 层）

| 层 | 内容 | 代表文件（行数） |
|---|---|---|
| L01 | 门户/CI/容器 | README 325 行、4 workflows、docker/Dockerfile |
| L02 | 配置系统 | fourcastnet3.yaml 438、YParams、argument_parser |
| L03 | 离线数据工程 | data_process/ 21 文件（convert_era5_to_makani_input 338、get_stats 669） |
| L04 | 数据加载与后端 | backends/（base 430、icon 701）、dali_dataloader 532、sample_source 538、rollout 421 |
| L05 | 模型公共层 | common/layers 1232、spectral_convolution 516、fft 464 |
| L06 | 网络动物园 | fourcastnet3 1186、sfnonet 1088、pangu 1160、afnonet×2、vit、snonet、debug |
| L07 | 模型组装包装 | model_registry、model_package 569、preprocessor 916、noise 1239、stepper |
| L08 | mpu 分布式 | mappings 544、halo 406、layers 1091、layer_norm、fft |
| L09 | 损失与指标 | loss.py 550、crps_loss 1196、energy_score 997、metric 742 |
| L10 | Driver 与引擎 | driver 1098、四 Trainer、inferencer 917、rollout_buffer 1572 |
| L11 | CLI 七件 | train/inference/benchmark 657 等 |
| L12 | 通用工具 | comm 322、checkpoint_helpers 446、remap 966、grids/features |
| L13 | 辅助脚本 | benchmark sweep/report/show、make_rollout_video |
| L14 | 测试 | tests/ 串行 + tests/distributed/ 多 GPU 矩阵 |

## 4. 引擎面：Driver 总控 + 四 Trainer + Inferencer

`Driver`（makani/utils/driver.py:61，ABC 元类）是所有会话的中枢：driver.py:99 `__init__` 装配 params/world_rank/device；checkpoint 双格式 `restore_from_checkpoint`:460 → `_restore_checkpoint_legacy`:551 / `_restore_checkpoint_flexible`:627，driver.py:680 `save_checkpoint` → driver.py:716 `_save_checkpoint_legacy` / driver.py:781 `_save_checkpoint_flexible`（README.md:199：legacy 按模型并行 rank 分文件可完整恢复含优化器；flexible 可换并行配置恢复但优化器恢复仍实验性）；优化器/调度器 `get_optimizer`:857/`get_scheduler`:912；dataloader 状态 gather/restore（:412-551）支持异步加载断点续训；wandb/可视化（:292、:977-1080）。

四个 Trainer 是 Driver 的子类但**不并列**：确定性 `Trainer(Driver)`（deterministic_trainer.py:62，807 行，makani.train 的核心）；**`EnsembleTrainer(Trainer)`**（ensemble_trainer.py:62，788 行，HENS 多成员——继承确定性 Trainer 而非直接继承 Driver）；`StochasticTrainer(Driver)`（stochastic_trainer.py:60）；`AutoencoderTrainer(Driver)`（autoencoder_trainer.py:57）。推理侧 `Inferencer`（inferencer.py，917 行）：在线推理、自回归 rollout、逐窗评分与输出写出；评分存储后端 rollout_buffer.py（1572 行）的 DataBuffer/RolloutBuffer/MeanStd/谱平均家族支持 HDF5 `direct` VFD（O_DIRECT 绕页缓存，rollout_buffer.py:59 `odirect_available`）与 GDS（cuFile 指针直写，:44-46/:82 探测、:215 `enable_odirect`）。

## 5. 模型面：动物园 + 组装三级台阶

**网络动物园（models/networks/）**：旗舰 `fourcastnet3.py`——fourcastnet3.py:108 `DiscreteContinuousEncoder` · fourcastnet3.py:248 `DiscreteContinuousDecoder`（Disco 连续表示编解码，cutoff 半径 `_compute_cutoff_radius`:48）、`NeuralOperatorBlock`:428（内嵌 disco 卷积 :518-542）、主网络 `AtmoSphericNeuralOperatorNet`:650（三层 embed：atmo/surf/aux，`fused_disco` 融合开关 :699-876），3.1 变体 fourcastnet3_1.py（1168 行）。`sfnonet.py`——`SpectralFilterLayer`:52/`NeuralOperatorBlock`:188/`SphericalFourierNeuralOperatorNet`:438（FCN2 与 HENS 主力；sfnonet.py:1022 `FourierNeuralOperatorNet` 直接继承 SFNO）。Pangu 复现 pangu.py（1160 行）：`get_earth_position_index`:40、`EarthAttention3D`:341（3D 窗口注意力+地球位置偏置表 :382-398）+ ONNX 封装 pangu_onnx.py（147 行）。另有 afnonet.py:621/afnonet_v2.py:599（FCN1）、vit.py:467、snonet.py:908、debug.py:59（CI 冒烟小网络）。

**公共层（models/common/）**：layers.py 1232 行 13 类（layers.py:49 `DropPath` · layers.py:154 `LayerScale` · layers.py:199 `PatchEmbed2D` · layers.py:309 `PatchEmbed3D` · layers.py:408 `PatchRecovery2D` · layers.py:468 `PatchRecovery3D` · layers.py:537 `EncoderDecoder` 等）；spectral_convolution.py 516 行（spectral_convolution.py:37 `SpectralConv` + 球谐域 spectral_convolution.py:273 `SpectralAttention`）；fft.py 464 行单进程 FFT 家族（fft.py:28 `RealFFT1` 至 fft.py:303 `RealFFT3` 正逆变换模块）。

**组装三级台阶**：`model_registry.get_model`:147 按 nettype 注册发现（model_registry.py:98 `register_model`，全部训练入口的构造器）→ `model_package.py:99` `ModelWrapper`（569 行）把网络+预处理器+归一化封装为可保存模型包（model_package.py:38 `LocalPackage`）→ `stepper.py:52` `StepWrapper` 包装为多步 rollout 模块。其上还有生成式包装 `stochastic_interpolant.py`（562 行）连接 noise.py（1239 行球面随机场：noise.py:36 `BaseNoiseS2` · noise.py:388 `IsotropicGaussianRandomFieldS2` · noise.py:638 `DiffusionNoiseS2` · noise.py:977 `DummyNoiseS2`）与网络；`preprocessor.py:127` 的 `Preprocessor2D`（916 行）管输入特征装配（preprocessor.py:416 `assemble_input` 含噪声注入与扩散调度）、history 统计归一化（preprocessor.py:520 `compute_history_stats` · preprocessor.py:603 `history_normalize`）；`features.py` 的通道分类（features.py:37 `get_auxiliary_channels` · features.py:89 `get_water_channels` · features.py:102 `get_wind_channels`）。

## 6. 分布式面：mpu 自制模型并行栈

README.md:48-50 并行特性表：通道并行（`--fin_parallel_size` · `--fout_parallel_size`）、空间模型并行（`--h_parallel_size` · `--w_parallel_size`，模型与数据同切，每 rank 只读数据一分片）、集成并行（`--ensemble_parallel_size`）；README.md:58 给出 256 GPU SFNO 示例（`mpirun -np 256 ... --h_parallel_size=4`）。

mpu 栈：`mappings.py` autograd 原语五件（mappings.py:38 `_DistributedTranspose` · mappings.py:70 `_CopyToParallelRegion` · mappings.py:94 `_ReduceFromParallelRegion` · mappings.py:117 `_ScatterToParallelRegion` · mappings.py:152 `_GatherFromParallelRegion`）+ 公开函数（mappings.py:186-220 copy/reduce/scatter/gather/transpose）+ `init_gradient_reduction_hooks`:333 梯度归约钩子；`halo.py`（406 行）球面网格 halo 交换与方位角交换；`layers.py`（1091 行）通道并行层动物园（DistributedMatmul:35/DistributedEncoderDecoder:248/DistributedMLP:386/StochasticMLP:577/DistributedPatchEmbed:835/DistributedAttention:960）；`layer_norm.py` 的分布式归一化统计用 Welford 在线算法合并——`_welford_kernel`:55 是 **@torch.compile 融合核**（非手写 CUDA），`distributed_welford_variance`:84 gather 后归约。进程组管理 `comm.py`（322 行）：命名进程组（`_initialize_manager`:34、serial:67、get_size/get_rank/get_group :100-116）是数据/模型/IO 组分治的基石（图谱 fanIn=64 全仓第二）；分布式检查点 gather/scatter 在 checkpoint_helpers.py（446 行）。

## 7. 损失/指标面：评分函数代码化

`LossHandler`（**makani/utils/loss.py:58**，550 行——注意不在 losses/ 目录）按 config 组合加权损失项：loss.py:282 `_parse_loss_type`、multistep 权重 `_compute_multistep_weight`:239、running stats（:297-334）、缺测掩码 `_mask_missing_targets`:349。CRPS 家族（crps_loss.py 1196 行，集合预报核心）：ensemble kernel crps_loss.py:55 `_crps_ensemble_kernel`、crps_loss.py:220 `CRPSLoss`、crps_loss.py:398 `SpectralCRPSLoss`、crps_loss.py:585 `GradientCRPSLoss`、crps_loss.py:795 `VortDivCRPSLoss`、crps_loss.py:971 `KernelScoreLoss`，辅助 crps_loss.py:42 `rankdata`。能量分数家族（energy_score.py 997 行五类）：energy_score.py:30 `LpEnergyScoreLoss` · energy_score.py:244 `SobolevEnergyScoreLoss` · energy_score.py:438 `SpectralL2EnergyScoreLoss` · energy_score.py:618 `SpectralCoherenceLoss` · energy_score.py:822 `CorrectedSpectralL2EnergyScoreLoss`。基类四类几何/谱在 base_loss.py；另有静力平衡/涡散/NLL/MMD/正则专题。指标侧 `metric.py`：metric.py:47 `MetricRollout` rollout 期统计管理、metric.py:260 `MetricsHandler` 装配 L1/RMSE/ACC/Spread/SSR 等（functions.py 746 行）。**tests/test_losses.py 4282 行 31 个 TestCase 类**（test_losses.py:253 TestLossCommon … test_losses.py:4208 TestTransformedCRPSVariants）是损失家族语义的权威口径。

## 8. 数据面与质量防线：三后端 + 离线工程 + 测试

**后端协议**：`backends/base.py`（430 行）钉版 base.py:124 `GridSpec` · base.py:156 `BackendMetadata` · base.py:190 `DatasetBackend` 的发现/分块/读取生命周期；`factory.py` factory.py:59 `detect_backend` 嗅探格式（h5 vs `.zarr` glob factory.py:86，zarr 内含 dataset_name 则判 arco_wb2 factory.py:89）。五实现：**ICON**（icon.py 701 行，非结构网格：icon.py:133 `variable_of_file` 变量归属取最长前缀匹配防 u/u_10m 静默错配、时间戳解码 regex 表 `_DATE_PATTERNS`:150-153（`(\d{8})T(\d{6})Z` 全时戳与 `_(\d{6})` 月聚合两模式）、icon.py:156 `date_of_file`、icon.py:172 `survey_files` 开文件前先按名分组、icon.py:180 `VariableSource` 变量-文件-样本索引 NamedTuple）；CF 时间单位解析在 icon_helpers.py:86 `_CF_UNITS_PATTERN`。其余四实现：makani_zarr / makani_hdf5（原生格式）；makani_concat（多集拼接）；mesh 混入。`SampleSource`（sample_source.py:55，538 行）桥接 backend 与 dataloader（sample_source.py:244 `_generate_indexlist`、:425 `_compute_zenith_angle` 天顶角、`__getstate__`:446 pickle 协作）；DALI GPU 直读异步流水线 dali_dataloader.py（532 行，dali_dataloader.py:74 `DaliDataloader`）；rollout.py（421 行，rollout.py:75 `RolloutStep` · rollout.py:115 `Rollout`）验证期自回归 rollout 循环。

**离线工程（data_process/）**：ERA5→makani 输入主力 convert_era5_to_makani_input.py（338 行）+ 不变量转换；WB2 输出转换 convert_makani_output_to_wb2.py 与气候态生成 generate_wb2_climatology.py；四大收集器 get_stats.py:669（逐通道统计）/get_histograms/get_spectra/get_hydrostatic_balance_climatology；数据集拼接/合并/标注/重分块与 sources 抽象（NCAR zarr/ARCO-WB2）。

**容器与 GDS**：docker/Dockerfile:41 源码编译 HDF5 启 `HDF5_ENABLE_DIRECT_VFD=ON`，:49 以 `H5PY_DIRECT_VFD=1` 装 h5py==3.16.0——容器级 GDS 直读集成关键两行；Dockerfile.aws:147 变体再加 H5PY_ROS3=1。

**测试与 CI**：tests/ 串行单测（模型/损失/指标/网格/remap/预处理器/dataloader + testutils.py）+ tests/distributed/ 多 GPU 矩阵（test_distributed_checkpoint.py / test_distributed_dataloader_checkpoint.py / test_distributed_fft.py / test_distributed_layers.py / test_distributed_losses.py / test_distributed_metrics.py / test_distributed_model.py（495 行）/ test_distributed_remap.py / test_distributed_rollout_buffers.py，夹具在 distributed_helpers.py）；四工作流 style.yml/test_serial.yml/tests.yml/test_distributed.yml 分别消费；Makefile 提供 install/wheel/test（`coverage run -m pytest tests`）/format。**tests/test_losses.py 4282 行 31 个 TestCase 类**（test_losses.py:253 TestLossCommon … test_losses.py:4208 TestTransformedCRPSVariants）是损失家族语义的权威口径。

**上手路线**：① README.md 快速开始跑通 debug 网络 → ② 读 fourcastnet3.yaml 对照 L06 架构 → ③ driver.py:61-139 看 Driver 装配流 → ④ train.py → Trainer 链路 → ⑤ 数据侧 backends/base.py 协议 + sample_source → ⑥ 并行实验从 benchmark.py:85 合成数据起步（无需数据集）→ ⑦ 评分深入 inferencer + rollout_buffer + crps_loss。新人三坑：a) grid_type 必填别删（parse_dataset_metada.py:37）；b) 恢复优化器状态换并行配置时 legacy 格式做不到（README.md:199）；c) FourCastNet3 常见 OOM 是 torch 内存池碎片，按 README.md:231 设环境变量；inductor 编译 DISCO 卷积超 recompile 上限时 makani 已把上限提到 32（README.md:243）。

# 04 · 数据后端体系与 Preprocessor2D：从再分析到张量

## 角色定位

`makani/utils/dataloaders/`（后端协议+五实现+SampleSource+DALI+rollout）与 `makani/models/preprocessor.py` 的 Preprocessor2D 构成数据面：离线侧 data_process/ 把 ERA5/WB2 转成 makani zarr/HDF5；在线侧后端协议屏蔽格式差异，SampleSource 桥接 DataLoader，Preprocessor2D 在进网络前完成特征装配/噪声注入/归一化。

## 内部结构

**后端协议（backends/base.py 430 行）**：base.py:124 `GridSpec`/base.py:156 `BackendMetadata`/base.py:190 `DatasetBackend` 钉版"发现→分块→读取"生命周期（`self.metadata`:313、`__len__` 由 metadata.files 推导 base.py:329-331）。工厂（backends/factory.py）`detect_backend`:59 嗅探存储格式：h5 布局直接判 makani_hdf5（:73/:83），`.zarr` glob（:86）后开 store 看是否含 dataset_name 区分 makani_zarr 与 arco_wb2（:89），都不中抛 IOError（:92）。

**五实现**：ICON 后端 icon.py（701 行）处理非结构网格——`variable_of_file`:133 从文件名判变量并取**最长前缀匹配**（注释钉版 `u_10m_dyamond_...` 同时前缀匹配 `u_` 与 `u_10m_`，读错即静默错报十米风为高空 u）；时间戳解码 regex 表 `_DATE_PATTERNS`:150-153（`(\d{8})T(\d{6})Z` 全时戳 / `_(\d{6})` 月聚合两模式）；`date_of_file`:156 解不出返回 None 提示去开文件而非瞎猜；`survey_files`:172 开文件前按名分组清点；`VariableSource`:180 NamedTuple 记录变量-文件-样本索引映射。CF 时间单位解析在 icon_helpers.py:86 `_CF_UNITS_PATTERN`（"hours since ..."）。makani_zarr/makani_hdf5（原生格式）、makani_concat（多集拼接）、mesh 混入（arco_wb2.py 对接 Google ARCO）。

**读取源与吞吐**：`SampleSource`（sample_source.py:55，538 行 16 方法）桥接 backend 与 dataloader——sample_source.py:244 `_generate_indexlist` 样本索引、sample_source.py:385 `_open_with_retries` 重试、sample_source.py:396 `_read_window` 读窗口、sample_source.py:425 `_compute_zenith_angle` 天顶角动态特征、sample_source.py:446-450 `__getstate__/__setstate__` pickle 协作（DALI worker 需要）。DALI 路线 dali_dataloader.py:74 `DaliDataloader`（532 行）GPU 直读异步流水线；rollout.py:115 `Rollout`（421 行）验证期自回归 rollout 循环。

**Preprocessor2D（preprocessor.py:127，916 行 21 方法）**：`flatten_history`:317/`expand_history`:342 管多历史步打包；`assemble_input`:416 装配输入（含动态特征与噪声注入、扩散调度）；`noise_source`:494 取噪声源（`_NoiseSource`:81 带版本与状态管理，`NoiseState`:61 可序列化）；归一化走 history 统计（`compute_history_stats`:520、`_check_history_stats`:587、`history_normalize`:603、`history_denormalize`:636）。通道分类辅助在 utils/features.py（`get_auxiliary_channels`:37、`get_water_channels`:89、`get_wind_channels`:102、`split_channel_name`:116）。

**离线工程（data_process/）**：ERA5 主力转换 convert_era5_to_makani_input.py（338 行）+ 不变量 convert_era5_invariants_to_makani_input.py；WB2 出口 convert_makani_output_to_wb2.py、气候态 generate_wb2_climatology.py、merge_wb2_dataset.py；统计四收集器 get_stats.py（669 行，产出 yaml 引用的 mins/maxs/global_means/global_stds :17-24）/get_histograms/get_spectra/get_hydrostatic_balance_climatology；数据集整理 concatenate/annotate/postprocess_stats；sources/ 抽象数据源（NCAR zarr、ARCO-WB2）。

## 外部连接

容器层 GDS 集成：docker/Dockerfile:41 源码编译 HDF5 开 `HDF5_ENABLE_DIRECT_VFD=ON`，:49 `H5PY_DIRECT_VFD=1` 装 h5py==3.16.0（AWS 变体 Dockerfile.aws:147 加 H5PY_ROS3=1）——直读 VFD 是 rollout_buffer O_DIRECT/GDS 写与后端高吞吐读的容器前提。元信息链：parse_dataset_metada.py:22 的 metadata（grid_type 必填 :37-45，缺 lat/lon 按 grid_type 重建 :50-62）决定网格与求积。

## 数据流

ERA5/ARCO（外部）→ data_process 转换+统计收集 → makani zarr/HDF5 + metadata + stats npy → detect_backend 嗅探构造后端 → SampleSource 按索引读窗口（DALI 异步/GDS 直读）→ DataLoader 批 → Preprocessor2D（history 展平→通道装配→噪声→归一化）→ 网络输入；验证侧同源进 rollout.py 自回归循环。

## 设计决策

1. **协议先行**：新格式只需实现 DatasetBackend 三段生命周期，工厂与 SampleSource 不动（base.py）。
2. **文件名即元数据（ICON）**：先按名分组再开文件（survey_files:172），IO 省一个量级；代价是 regex 表要覆盖真实命名（:150-153）。
3. **噪声状态可序列化**：随机插值训练的噪声发生器状态随 checkpoint 走（NoiseState:61），恢复训练噪声序列连续。
4. **归一化统计离线一次算好**：yaml 引用 npy（fourcastnet3.yaml:17-24），在线零开销。
5. **grid_type 强制声明**：求积权重由网格决定，静默默认即静默错（parse_dataset_metada.py:37 注释原话）。

## 新人提示

加新数据格式从 base.py 协议起步，先写 detect 分支（factory.py:59）再写实现；ICON 变量对不上先查文件名最长前缀匹配（icon.py:133）；调试归一化用 `compute_history_stats` 对拍 yaml 的 stats 文件；容器里 GDS 不生效先查 Dockerfile:49 的 h5py 构建行；动态特征（天顶角）在 SampleSource 算而不是 Preprocessor（sample_source.py:425）。

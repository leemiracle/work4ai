# ⑥ groot_dreams 机器人数据层与 configs 十 yaml 训练配方

## 角色定位

`groot_dreams/`（16 文件）是 DreamDojo 后训练的**机器人数据供给层**：以 LeRobot 数据集格式（分片 parquet + MP4 视频 + meta json）读取 AgiBot/G1/GR1/YAM 四本体的真机轨迹，装配成 `{video, lam_video, action, state}` 模态样本喂给世界模型。顶层 `configs/` 十个 hydra experiment yaml 则是"一域一配方"的训练入口——`{2b,14b}_480_640_{pretrain,agibot,g1,gr1,yam}.yaml` 覆盖 2B/14B 两档模型 × 预训练/四真机域五场景，是复现论文后训练矩阵的最短路径。

## 内部结构

**LeRobotSingleDataset**（`groot_dreams/data/dataset.py:76`，1098 行）：构造（81-146）七步——modality_configs/transforms 注入 → `EmbodimentTag` 归一（117-120）→ `_get_metadata` 读 dataset 目录 metadata.json（239）→ 轨迹表 `_get_trajectories`（405）→ 全部合法采样点 `_get_all_steps`（418，`single_base_index` 控制是否只从轨迹头采样）→ modality_keys/delta_indices（444/454）→ LeRobot 特有五元（lerobot_modality_meta/info_meta/data_path_pattern/video_path_pattern/chunk_size，462-506）+ tasks 表（510）→ `_check_integrity`（518）。**读取路径**：`__getitem__`（558）= `(traj_id, base) -> transforms(get_step_data(...))`；`get_step_data`（571）按 modality→key 装配原始数组；`get_trajectory_data`（597）**整条 parquet 进 DataFrame 缓存**（curr_traj_id 命中即复用，601-603）——大轨迹内存占用与随机访问的折中；`get_episode_chunk`（625）`ep_index//chunk_size` 定位分片；越界 `retrieve_data_and_pad`（632）按 first_last 策略补齐。

**schema.py**（207 行）：pydantic 模型树定义 LeRobot 契约——`RotationType`（13）九种旋转表示枚举；`LeRobotStateActionMetadata`（40）以 `start/end` 段坐标描述某模态在拼接 state/action 大向量中的位置，配 `absolute/dtype/range`；`DatasetStatistics`（172，内嵌 `DatasetStatisticalValues:159` 支持 ndarray 序列化）承载逐维 mean/std/q01/q99——归一化的数据契约。`embodiment_tags.py:4` `EmbodimentTag` 四值枚举（GR1/AGIBOT/G1/YAM）与 shared_meta 十 JSON 一一对应（`GR1_unified_modality.json` 里 `state.left_arm` 即 start:0,end:7 段声明）。

**transform 三链**（`data/transform/`）：video 链（`video.py`，`VideoCrop:229`/`VideoResize:296`/`VideoColorJitter:414` 等十余种）；state_action 链（`state_action.py:261` `StateActionTransform` 为主——用 metadata 做 concat 切段/旋转转换/`Normalizer:83` 依 stats 归一化，另有 `StateActionPerturbation:514`/`StateActionDropout:548`/`StateActionSinCosTransform:576` 三个正则化变体）；concat 链（`concat.py:11`）把多模态键合并。骨架 `base.py:9` `ModalityTransform`/`78` `ComposedModalityTransform`（metadata 经 `set_transforms_metadata:534` 下发）。

**封装层**：`groot_configs.py:8` `construct_modality_config_and_transforms(num_frames, embodiment, agibot_pad_freq10, waist_concat)` 按本体返回 (config, train_tf, test_tf)——GR1/GR1_human/AgiBot/G1/YAM 分支各拼 modality 键与增强链（162-164 行 VideoToTensor→VideoCrop→VideoResize 标准三连）；`dataloader.py` 的封装类在 `construct_modality_config_and_transforms(num_frames+1, ...)`（37-39）**多采一帧前缀**算 delta action 基线，`__getitem__`（58-75）帧数不符时**随机换样本重试**（62 行警告路径）并透出 `lam_video` 键（LAM 隐动作模型的输入帧对）。

**configs 十 yaml**：结构极简（37-274 行不等）——job（project=dreamdojo/group=exp1201）、trainer（grad_accum/callbacks 采样频率）、model_parallel（context_parallel_size）、model.config（`state_t:4`（`2b_480_640_gr1.yaml:21`，注释 `1+12//4`——13 像素帧压成 4 潜帧）、`action_dim:384`（23）、`num_action_per_chunk:12`、`zero_init_action_embedder` pretrain true/域适配 false）、dataloader_train.dataset（`num_frames:13`（32）、dataset_path 列表与 `dataset_mixing_weights`）。差异分布：pretrain 三源混采 1:2:10（`2b_480_640_pretrain.yaml:34-40`，44k 小时人类视频 egodex 占权重 2、GR1 人类遥操作 1、自采 10）；agibot 79 个分片全列（114 行版）；yam 最大 274 行；gr1 最小 37 行且 dataset_path 用 HF 相对路径（`datasets/PhysicalAI-Robotics-GR00T-Teleop-GR1/GR1_robot`，30-31）——**唯一非内网路径的配方**。变体 dataset_mano/dataset_video（`dataset_mano.py`/`dataset_video.py`）服务手部动作与纯视频数据。

## 外部连接

消费方：`predict2/action/datasets/`（GR00T 动作条件训练）与 `interactive/configs/data.py`（自强迫数据装配）经 `groot_dreams/dataloader.py` 引 dataset；上游契约 = shared_meta 十 JSON（`G1_modality.json`+`G1_stats.json` 等）与 HF 数据集 `PhysicalAI-Robotics-GR00T-Teleop-GR1`。yaml 经 `launch.sh` 的 `experiment=<name>` 注入 `action/configs/action_conditioned/config.py` python 配置（hydra override 语义）。`scripts/gen_stats.py` 可对新数据重算 stats。

## 数据流

一次取样：`(traj_id, base)` → parquet DataFrame 取 state/action 行 → 按各模态 delta_indices 取窗口 → video 后端 decord 抽帧 → transforms（resize→归一化→concat）→ `{video:[T,H,W,C], action:[T,D], state, lam_video}` → 上层再切 (num_cond, num_gen) 帧组。混采在 dataloader 层按 `dataset_mixing_weights` 加权随机（多 dataset_path 列表）。训练侧 `state_t=4` 与 VAE 时间压缩比对齐：13 帧=1 条件帧+12 生成帧→4 潜帧。

## 设计决策

1. **parquet 整轨迹缓存**（597-603）：顺序 epoch 内命中率高，避免逐行 IO；代价是内存驻留，超大轨迹需注意 worker 数×轨迹大小。
2. **模态以"段坐标"描述**（start/end）：新增本体只写一个 modality.json+stats.json，代码零改动——shared_meta 是数据侧的插件点。
3. **一帧前缀预采**（dataloader.py:39）：delta action 需要前一帧基准，在数据层多采一帧比在模型层特判干净。
4. **帧数不符随机重试**（62 行）：短视频轨迹天然不足 13 帧，重试比 pad 保真（pad 只在 retrieve_data_and_pad 内部对动作窗口用）。
5. **配方只存差量**：yaml 不重复 python 配置默认值，2B/14B 仅 batch_size/grad_accum/zero_init 差异——审配方 diff 即知域间真正差异。

## 新人提示

- 复现顺序：先跑 gr1 配方（唯一公开路径），其余域把 dataset_path 换成本地转换后的 LeRobot 目录（格式见 `docs/POSTTRAIN.md`）。
- 新数据域五步：EmbodimentTag 加枚举 → 写 `{X}_modality/{X}_stats.json`（仿 GR1_unified 对）→ `groot_configs.py` 加分支 → 写 yaml → `scripts/gen_stats.py` 校验统计。
- **勘误（源码实证）**：①九个 yaml 的 dataset_path 是内网绝对路径（`/mnt/amlfs-0X/shared/datasets/...`，如 `2b_480_640_pretrain.yaml:34-36`），开箱即跑会 FileNotFoundError；②`2b_480_640_yam.yaml` 274 行远超同类（其余 37-114），含大量逐分片路径与重复覆盖，维护时建议脚本生成；③`num_frames:13` 与 `state_t:4` 的换算注释（`1+12//4`）只在 gr1/pretrain 配方有，g1/agibot 无注释但同值，勿误读为不同语义。

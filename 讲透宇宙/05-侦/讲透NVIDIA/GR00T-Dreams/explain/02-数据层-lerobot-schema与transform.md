# 数据层：LeRobot schema 加载与 modality transform 体系

## 一、角色定位

`gr00t/data/dataset.py`（877 行）与 `gr00t/data/transform/` 四件套（`base.py`/`state_action.py`/`video.py`/`concat.py`）是管线的地基：真机数据与 IDM 合成数据走同一套代码，GR00T 微调、IDM 训练、动作 dump 三阶段全踩在这层。核心类 `LeRobotSingleDataset`（`dataset.py:L86`）把 LeRobot 格式（五个元文件常量，`dataset.py:L37-42`）抽象成"每步一条样本"的 Dataset。中心思想是**声明式配置**：`ModalityConfig`（`dataset.py:L77-84`）声明每个模态读哪些 key 及相对当前步的 `delta_indices`（如 `[0]` 单帧或 `[0, 16]` 首尾两帧），dataset 负责取数回填、交 transform 链整形。

## 二、内部结构

初始化把每条轨迹的每步展开为 `(trajectory_id, base_index)` 对，`__len__` 即步总数，`__getitem__` = 原始取数 + transforms（`dataset.py:L478-488`）。

`_get_metadata`（`dataset.py:L244`）做三件事：把 `modality.json` 里 state/action 各段（`schema.py:L54-68` 的 `start/end` 切片、`absolute`、`rotation_type`）简化为四字段元信息，`continuous` 由 dtype 是否浮点推断（`dataset.py:L261-279`）；视频元数据从 `info.json` 取，try/except 兼容新旧 LeRobot 的 `channel`/`channels` 键名差（`dataset.py:L296-302`）；stats 缺失时现场重算——`calculate_dataset_statistics`（`dataset.py:L45`）拼全部 parquet 逐列算 mean/std/min/max/q01/q99 并写回，整表统计再按 `start:end` 切片重映射回子键（`dataset.py:L324-338`）。

取数按模态分派。state/action 走 `get_state_or_action`（`dataset.py:L659`）：`delta_indices + base_index` 后按元数据切片，越界交给 `retrieve_data_and_pad`（`dataset.py:L558`）——**绝对量**复制首/末步值、**相对量**补零（`dataset.py:L709-713`）。视频走 `get_video`（`dataset.py:L615`）：clamp 后按 parquet 的 `timestamp` 对齐帧（`dataset.py:L648-652`），decord/torchvision 双后端。语言按 `task_index` 查 tasks 表。单轨迹 parquet 缓存于 `curr_traj_data`，子类 `CachedLeRobotSingleDataset` 把全部帧解到内存直接索引。

transform 骨架在 `base.py`：`ModalityTransform` 是带 `set_metadata` 的 pydantic 模型，`ComposedModalityTransform` 顺序 apply、逆序 unapply 且只对可逆变换生效（`base.py:L118-126`）——**可逆性**是最大财产。

## 三、外部连接

- **上游**：`IDM_dump/raw_to_lerobot.py` 产出本 schema 的合成数据集（零占位 action + 预置 stats，见第 3 篇）；`gr00t/experiment/data_config.py` 与 `data_config_idm.py` 是 788 行复制粘贴双胞胎，逐 diff 仅四处差异（transform 类 import、`observation_indices` `[0]` vs `[0,16]`）。
- **下游**：`GR00TTransform`（第 1 篇）与 `GR00TIDMTransform`（第 3 篇）消费 concat 后的键；`scripts/gr00t_finetune.py` 组装 DataLoader。
- **pytorch3d**：`RotationTransform`（`state_action.py:L29-34`，改自 diffusion_policy）所有旋转互转以矩阵为中转。

## 四、数据流

样本旅程：`(traj_id, base_idx)` → 按模态取原始 numpy → transform 链四节点：

1. **StateActionToTensor**：numpy→torch；
2. **StateActionTransform**（`state_action.py:L276`）先旋转后归一化（`state_action.py:L488-495`）：`Normalizer`（`state_action.py:L98`）的 q99 模式公式 `2*(x-q01)/(q99-q01)-1` 后 clamp [-1,1]（`state_action.py:L113-134`）。旋转维统计不从数据来：绝对旋转强制 min_max、统计取 `_DEFAULT_MIN_MAX_STATISTICS`（`state_action.py:L309-326`，rotation_6d 用 ±1、euler 用 ±π）；相对旋转直接抛错（`state_action.py:L453-457`）；
3. **VideoTransform**：多视角拼接、rearrange 展平成帧批统一增强再拆回（`video.py:L182`）；albumentations 后端用 `ReplayCompose` 保证同一样本所有帧吃同一随机参数（`video.py:L186-206`）；eval 下增强类返回 None 跳过，`VideoToTensor` 把 uint8 除 255 转浮点；
4. **ConcatTransform**（`concat.py:L26`）：多视角视频在倒数第 4 维拼成 `[..., V, H, W, C]`（`concat.py:L102-109`）；state/action 沿末维 cat，维度校验容忍旋转表示变体与 sin-cos 2 倍宽。

训练扰动也在链上（`StateActionPerturbation` 加噪声、`StateActionDropout` 整条置零，均 eval 直通）。

## 五、设计决策

1. **schema 防沉默损坏**：`_check_integrity` 逐 key 验证元数据存在，唯一豁免 `lapa_action`/`dream_actions`（`dataset.py:L444-445`，"comes normalized"）。
2. **padding 语义二分**：绝对量复制边界值、相对量补零（`dataset.py:L709-713`），把"外推 vs 归零"的领域知识压进一行三元式。
3. **统计三级容错**：读 stats → pydantic 校验 → 失败重算并落盘（`dataset.py:L310-323`），数据集目录自愈。
4. **可逆链而非单向管道**：`unapply` 逆序回放，IDM 的伪标签动作因此能无损回物理单位。

## 六、新人提示

- **调试先看 shapes**：`get_step_data` 的 docstring 写明各模态返回形状约定，transform 链 assert 全以此为契约。
- **报 "Unable to find key"** 先 diff `modality.json` 与 `modality_configs`。- **timestamp 对齐是隐形坑**：fps 元数据与实际视频不符会静默取错帧；IDM 线 `raw_to_lerobot.py` 就有 info.json 写 8fps、时间戳按 16fps 生成的矛盾（见第 3 篇）。
- **加新增强**：继承 `VideoTransform` 实现 `get_transform(mode)`（train 随机版、eval None）。
- **双胞胎配置**：改 `data_config.py` 必查 `data_config_idm.py`。

# 05 · 数据契约层：DataConfig、EmbodimentTag 与 SO100 新本体注册范例

> 覆盖：`gr00t/configs/data/data_config.py` · `gr00t/data/embodiment_tags.py` · `examples/SO100/so100_config.py` · `gr00t/data/types.py`（辅锚 `gr00t/configs/data/embodiment_configs.py`）

## 一、角色定位

四个文件构成 GR00T N1.7 的"数据契约层"：不搬运数据，只回答三个问题——**喂哪些数据集、按什么比例混**（`data_config.py`）；**数据属于哪台机器人**（`embodiment_tags.py`）；**每模态取哪些键、怎么时间采样、动作用什么表示**（`types.py`）。`so100_config.py` 是串联三者的最小范例。与 LeRobot v2 的关系是"风味扩展"：GR00T 在 `meta/modality.json` 里声明语义键（如 `single_arm`）在扁平 state/action 列中的 `[start,end)` 切片，配置里的 `modality_keys` 必须与之一致，否则切片期只产出空列+warning（loader 侧 `lerobot_episode_loader.py:340-342`）。

## 二、内部结构

**DataConfig（`data_config.py:52`）** 聚合混训清单 `datasets: List[SingleDatasetConfig]`（`:59`），每项五字段：`dataset_paths`（`:37`，复数可挂多条路径）、`embodiment_tag`（`:40`）、`mix_ratio`（`:43`，相对采样概率）、`dataset_type`（`:45`，默认 `physical_embodiment`）、可选 `val_dataset_path`（`:49`）。全局旋钮：`shard_size=2**10`（`:76`）、`episode_sampling_rate=0.1`（`:77`）、`num_shards_per_epoch=int(1e5)`（`:78`）、幂律混训 `ds_weights_alpha`（`:80`）、`override_pretraining_statistics=True`（`:83`）、`multiprocessing_context="fork"`（`:93`）。

**EmbodimentTag（`embodiment_tags.py:29`）** 16 成员 Enum 分三层，各有独立 frozenset 归档：预训练 8 标签（`PRETRAIN_TAGS` `:192-203`）——OXE_DROID `:60`、XDOF/XDOF_SUBTASK `:65/:70`、REAL_G1 `:75`、R1_PRO_SHARPA 四变体 `:80-95`（按 human/maxinsights/mecka 采数来源拆分）；posttrain 5 标签（`POSTTRAIN_TAGS` `:206-215`）——UNITREE_G1 `:102`、UNITREE_G1_SONIC `:107`（动作空间是 SONIC latent 非关节角）、SIMPLER_ENV_GOOGLE/WIDOWX `:112/:117`、LIBERO_PANDA `:122`；微调专用 3 标签（`FINETUNE_ONLY_TAGS` `:217-224`）——NEW_EMBODIMENT `:128` 与两个 ROBOCASA `:133/:139`。`resolve()`（`:145-180`）大小写不敏感两轮匹配：先枚举名（`xdof`→XDOF）再枚举值，失败报错分层列出全部合法标签（`:171-179`）。

**types.py** 是数据类底座。三个动作枚举：`ActionRepresentation`=RELATIVE/DELTA/ABSOLUTE（`:33-36`）、`ActionType`=EEF/NON_EEF（`:39-41`）、`ActionFormat`=DEFAULT/XYZ_ROT6D/XYZ_ROTVEC（`:44-47`）。`ActionConfig`（`:76-80`）四字段 rep/type/format/state_key——state_key 指明 RELATIVE 动作相对哪个 state 键取差分。`ModalityConfig`（`:84-85`）核心三件：`delta_indices`（`:92`，相对基准索引的时间偏移，负值=历史帧）、`modality_keys`（`:94`）、`action_configs`（`:100`，与 modality_keys 一一同位，`__post_init__` 强断言数量相等 `:112-115`，并兼容 dict 就地解析 `:117-126`）。`VLAStepData`（`:50-51`）是贯穿训练/推理的统一步样本：images/states/actions 三字典+可选 masks、text、embodiment（默认 NEW_EMBODIMENT `:67-69`）、`is_demonstration`（`:70`，该步不计 loss）、metadata（`:73`）。

**so100_config.py** 是 NEW_EMBODIMENT 注册模板：video 取 `["front","wrist"]` 且 `delta_indices=[0]`（`:29-32`）；state 取 `["single_arm","gripper"]`（`:34-40`）；action 用 `list(range(0,16))` 预测 16 步（`:43`），两键分别配 RELATIVE/NON_EEF（`:50-54`，注释"delta from current state (better generalization)"）与 ABSOLUTE/NON_EEF（`:56-60`，注释"binary open/close works better absolute"）；language 键 `annotation.human.task_description`（`:66`）。末行 `register_modality_config(so100_config, embodiment_tag=EmbodimentTag.NEW_EMBODIMENT)`（`:70`）触发注册。

## 三、外部连接

注册实现是 `embodiment_configs.py:355-361`：断言标签未占用后写入全局字典 `MODALITY_CONFIGS`（初值含 7 个预注册本体 `:26`）。`DataConfig.modality_configs` 默认值即它（`data_config.py:70-72`），用 `tyro.conf.Suppress` 从 CLI 隐藏；注释列出模态配置三来源：代码默认/YAML/checkpoint（`data_config.py:61-69`）。消费端三处：`launch_finetune.py:56-57` importlib 导入用户 .py 触发注册副作用；`DatasetFactory.build` 按标签索引建数据集（`factory.py:64`）；`Gr00tPolicy.__init__` 从 checkpoint processor 读全部本体配置并校验（`gr00t_policy.py:129-130`）。校验闭环在 `base_config.py:183-193`：数据集出现的每个标签必须已注册。

## 四、数据流

微调数据流头一公里：`launch_finetune.py:59` 用 `os.pathsep` 拆多路径 → 组装 `SingleDatasetConfig`（`:61-74`）→ factory 按标签取 modality_configs 建数据集 → loader 依 modality.json 的 start/end 切扁平列（`lerobot_episode_loader.py:331-336`）→ `extract_step_data` 按 delta_indices 组装 `VLAStepData`（`sharded_single_step_dataset.py:40`）。注册流是单行副作用：import so100_config.py → `MODALITY_CONFIGS["new_embodiment"]` 就位 → 训练与推理共用同一份契约。

## 五、设计决策

1. **三层标签=把"预训练知识边界"编码进类型系统。** 基座只认 8 个预训练标签；posttrain 标签需微调 checkpoint。约束在运行时生效：`gr00t_policy.py:142-152` 对两类标签给出不同报错 hint，比一刀切友好。
2. **mix_ratio 会被两级改写。** factory 先乘数据集相对长度（`factory.py:71-76`），`ds_weights_alpha` 设置后再整体替换为 `len^alpha` 幂律权重（`factory.py:78-85`）——用户以为的"精确比例"有三层语义，调参须知道最终生效哪层。
3. **RELATIVE/ABSOLUTE 混合是本体级工程判断。** 臂关节用相对（泛化好）、夹爪用绝对（二值信号），同样二分在 G1 全身配置再现（`embodiment_configs.py:158-164`，注释"G1 hand is controlled by binary signals like a gripper"）。
4. **action_configs 缺省时 validate() 兜底补 ABSOLUTE/NON_EEF/DEFAULT**（`base_config.py:203-210`）——`libero_sim` 就没写 action_configs（`embodiment_configs.py:202-205`），全靠兜底，不能误以为"没配=没约束"。
5. **`__post_init__` 校验与协议适配一体**（dict→ActionConfig，`types.py:117-126`），YAML/JSON 与纯 Python 场景共用一个类。

## 六、新人提示

- 接新机器人抄 SO100 三件套：数据集写 `meta/modality.json` 切片 → 复制 `so100_config.py` 改四模态 → `--embodiment-tag new_embodiment --modality-config-path your_config.py`。键名必须与 modality.json 完全一致，mismatch 只在加载期以 warning/KeyError 暴露。
- 历史帧合法：OXE_DROID 的 video `delta_indices=[-15,0]`（`embodiment_configs.py:30`）取 15 帧前+当前；推理端强校验 T 维等于 `len(delta_indices)`（`gr00t_policy.py:286`），训练改 horizon 推理观测必须同步。
- language 多键只用第一个：loader 训练期裁剪（`lerobot_episode_loader.py:260-273`）、policy 推理期断言（`gr00t_policy.py:171-175`），多键仅用于训练期改写增广。
- `resolve` 报错信息本身就枚举全部合法标签（`embodiment_tags.py:171-179`），故意跑一次报错比查文档快。

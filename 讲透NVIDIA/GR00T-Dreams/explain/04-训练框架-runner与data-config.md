# 04 训练框架：TrainRunner、DualBrainTrainer 与 9 个具身数据配置

## 一、角色定位

这组文件是 GR00T-Dreams 管线"GR00T N1 微调"一环的完整训练框架：`scripts/gr00t_finetune.py`（tyro 入口）→ `gr00t/experiment/runner.py`（实验编排）→ `gr00t/experiment/trainer.py`（训练内核）→ `gr00t/experiment/data_config.py`（数据规格注册表）。世界模型生成视频、IDM 提取动作后，合成数据集就喂给这条链。设计哲学是薄封装：不重写训练循环，继承 HuggingFace Trainer 只做最小手术，把工程复杂度压到数据侧。

## 二、内部结构

**配置注册表**：`BaseDataConfig` 是只有 `modality_config()`/`transform()` 两个抽象方法的 ABC（data_config.py:37-43），下挂 8 个具体类（`Gr1ArmsOnly` :49、`So100`、`BimanualPandaGripper`、`Gr1ArmsWaist` :648、`Franka` :678 等），与基类合计 9 个。继承树几乎全平，唯一继承边是 `Gr1ArmsWaistDataConfig(Gr1ArmsOnlyDataConfig)`：只覆写类属性（keys 加 `waist`、语言键换 `annotation.human.coarse_action`，:664），两个方法直接 `return super()`（:669-672）。这依赖 Python 类属性动态查找——父类 `transform()` 里的 `self.state_keys` 运行时解析到子类属性，"加一个腰部自由度"零代码复制。`DATA_CONFIG_MAP`（:779-788）以 8 个短名到单例实例收口。

**Runner**：`TrainRunner`（runner.py:34）管四件事：experiment_cfg 元数据（`metadata.json` 按 dataset tag 累积合并，:77-84）、collator `DefaultDataCollatorGR00T(processor=EagleProcessor())`（:56-58）、wandb/tensorboard 双通道（:88-112）、`create_trainer` 工厂（:114）——支持 `global_batch_size` 反推梯度累积（:127），并挂 `CheckpointFormatCallback`（:144-147）让每个 checkpoint 自带 experiment_cfg 副本、可独立分发。

**Trainer**：`BaseSampler`（trainer.py:33-60）补 HF Trainer 不调 `dataset.set_epoch` 的缺口——每 epoch 透传给 LeRobot 数据集换变换随机种子（:53-57）；"must not add rank" 注释（:49）是分布式锚点：各 rank 必须生成同一 permutation，否则多卡数据失配。`DualBrainTrainer(transformers.Trainer)`（:63）的"双脑联合优化"其实极薄：`compute_loss` 就是整字典进模型、取 `outputs["loss"]`（:74-77）。双系统分离在模型内——`GR00T_N1.forward`（gr00t_n1.py:161-169）一次跑完 System 2 VLM backbone 与 System 1 动作头，单一 flow-matching MSE 靠 `tune_*` 开关决定梯度是否流进视觉塔（:201-210）。其余 override 是标准适配：weight-decay 分组（LayerNorm 与 bias 免 decay，:92-93）、`resume_from_checkpoint=True` 翻译成 `get_last_checkpoint` 并预载 TrainerState（:141-152）。

**入口**：`Config` 默认值即推荐配方——`base_model_path="nvidia/GR00T-N1-2B"`（gr00t_finetune.py:62）、`tune_llm=False` 而其余三开关 True（:65-75）、`embodiment_tag="new_embodiment"`（:106）、`lora_rank=0` 关 LoRA（:90-97）。流程：查表建数据集（:124-135）→ `from_pretrained` 透传开关后双写 `compute_dtype="bfloat16"` 到模型与 config（:147-148）→ 按需 `get_lora_model`（:150-156）。`num_train_epochs=300` 与 `max_steps=10000` 并存（:181-182），max_steps 先到先停。多卡是代码自举：无 `IS_TORCHUN` 哨兵时脚本把 dataclass 序列化回命令行（bool 转 `--flag`/`--no-flag`）再 subprocess 起 torchrun（:243-266）。

## 三、外部连接

`runner_idm.py` 是 runner 的复制式孪生——实测全文 diff 仅 11 行（import 换 `IDM`+`DefaultDataCollatorGR00TIDM`、类型注解、collator 去 processor，runner_idm.py:25-26/55），wandb 与 checkpoint 逻辑一字不差，消费者是 `scripts/idm_training.py`。LoRA 走 `gr00t/utils/peft.py:get_lora_model`：扫描模块名含 `q_proj/v_proj/to_q` 等的 Linear（peft.py:21-25），一次命中 eagle LLM 与 DiT 两套子系统。`_wrap_forward`（:5-14）是必要猴子补丁：PEFT 包装后 forward 签名与字典输入不兼容，手工复刻 GR00T_N1.forward 四步链。下游 `scripts/eval_policy.py` 读 experiment_cfg 的 metadata 反推归一化统计。

## 四、数据流

单样本旅程：LeRobot 帧按 `modality_config()` 四类模态取数（观测 `delta_indices=[0]` 单帧、动作 `range(16)` horizon，data_config.py:64-65）→ `transform()` 流水线（Gr1ArmsOnly，:98-134）：视频五连 `ToTensor→Crop(0.95)→Resize(224)→ColorJitter→ToNumpy`；状态走 sin-cos 编码（:113，仅 Gr1 系；Panda 系用 min_max+rotation_6d :387-397、夹爪 binary :403-405）；`ConcatTransform` 按 key 序拼接；`GR00TTransform(max_state_dim=64, max_action_dim=32)`（:127-132）补零到模型槽位。collator 成批 → `compute_loss` → `GR00T_N1.forward` 出 `{"loss"}`。出口两路：HF 常规保存 + callback 把 experiment_cfg copytree 进 checkpoint（gr00t/utils/experiment.py:53-62）。

## 五、设计决策

1. **配置即类属性而非 YAML**：8 套具身规格硬编码，改规格=改代码；`new_embodiment` 默认值暗示用户本就该复制一份类再注册。
2. **继承压到最低**：9 类仅 1 条继承边，但五连视频变换在 8 份 transform() 里逐字重复七次——显式复制优先。
3. **trainer 极薄、runner 承重**：训练语义差异全压进 154 行 trainer.py，换来 IDM 线 11 行 diff 克隆整套实验设施。
4. **梯度选择性流过=联合优化**：无独立 backbone loss，靠 requires_grad 而非分离优化器，一条 loss 通路。

## 六、新人提示

- `--data_config` 传错键直接 KeyError，无模糊匹配。
- `num_train_epochs=300` 不必慌，`max_steps` 才是停止条件；`save_total_limit=8` 意味着磁盘最多 8 个 checkpoint。
- resume 陷阱：底层只认 `True→get_last_checkpoint`，output_dir 无 checkpoint 会 ValueError（trainer.py:143-146）。
- 多卡直接 `python scripts/gr00t_finetune.py --num_gpus N` 让脚本自举 torchrun；手动 torchrun 忘设 `IS_TORCHUN` 会无限递归 spawn。
- LoRA 先看 `get_lora_model` 打印的 trainable 参数量，确认 DiT 的 to_q/to_v 在列。
- 改数据规格后删 output_dir 下 `experiment_cfg/metadata.json`——它是累积合并的，旧归一化统计会残留进新 checkpoint，推理端反归一化就错了。

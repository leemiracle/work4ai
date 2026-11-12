# 07 · 训练入口：launch_finetune → experiment.run → Gr00tTrainer → DeepSpeed 分流

> 覆盖：`gr00t/experiment/launch_finetune.py` · `experiment.py` · `trainer.py` · `gr00t/configs/finetune_config.py` · `base_config.py` 的 `get_deepspeed_config`/`validate`

## 一、角色定位

这是用户命令行到第一个优化器 step 之间的全部代码。`launch_finetune.py` 是 tyro CLI 门面，把 `FinetuneConfig` 翻译成内部三段式 `Config`；`experiment.py::run` 是编排中枢（分布式初始化、管线装配、TrainingArguments、profiling）；`trainer.py::Gr00tTrainer` 继承 HF Trainer，重写数据加载/恢复/损失记录；`base_config.py` 提供 DeepSpeed ZeRO 分流与全局校验。分工是"门面-编排-引擎-契约"四层。

## 二、内部结构

**launch_finetune.py**。`load_modality_config`（`:31-41`）把用户 .py 所在目录塞进 `sys.path` 后 import（`:37-38`）——注册靠 import 副作用。主流程：`tyro.cli(FinetuneConfig)`（`:49`）→ `EmbodimentTag.resolve`（`:52`）→ 任意 rank 都要注册（`:55-57`）→ `dataset_path.split(os.pathsep)` 多路径（`:59`）→ `load_dict` 注入 datasets 块（`:61-74`）→ 覆写模型开关与增广（`:78-96`）→ 硬编码策略值 `model_name="nvidia/Cosmos-Reason2-2B"`/`use_relative_action=True` 等（`:98-102`）→ training/data 直拷（`:104-124`）→ `run(config)`（`:130`）。

**FinetuneConfig（`finetune_config.py:21-22`）**。默认值即官方微调配方：tune_llm=False（`:49`）、tune_visual=False（`:52`）、tune_projector=True（`:55`）、tune_diffusion_model=True（`:58`）——冻结骨干、只训 projector+扩散动作头；state_dropout_prob=0.2（`:61`）随机丢 state 逼模型依赖视觉。增广族（旋转/色彩抖动/分位归一化/裁剪比例，`:67-102`）与 extra_augmentation_config JSON（`:104-121`）。超参默认 global_batch_size=64、lr=1e-4、max_steps=10000（`:124/:131/:163`）。resume 默认 False（重跑从头开始，`:188-192`）、save_only_model 不可恢复（`:185-186`）、skip_weight_loading 供 CI 只验架构（`:194-197`）。

**experiment.py::run（`:192-385`）**。前置校验：`warn_configs`（`:194`，其中 `_assert_num_gpus_matches_world_size` `:53-69` 把 num_gpus 与 torchrun WORLD_SIZE 对账——8 卡启动写 num_gpus=1 会静默 8 倍批大小）、`check_resume_compatibility`（`:195`）、`set_seed(config.data.seed)`（`:203`）。`_init_distributed_process_group`（`:142-157`）用 `device_id=cuda:LOCAL_RANK` 急切绑定 NCCL（`:152-155`）。装配：`MODEL_REGISTRY.get(type(config.model))` 选管线（`:248-253`）；processor 经 rank0 落盘 `output_dir/processor`，部署期被 `Gr00tPolicy.from_pretrained` 消费（`:254-256`）。DeepSpeed 分流（`:259-262`）：`num_gpus > 1 and not use_ddp` 才生成配置。per-device 批大小=global_batch_size//num_gpus（`:264-268`）；`TrainingArguments` 直拷（`:271-303`，含 `ignore_data_skip=True`）；`CheckpointFormatCallback` 把 processor 拷进 checkpoint（`:315-321`）；profiling 分支（`:338-365`）。

**trainer.py**。`Gr00tTrainer(Trainer)`（`:152`）三处重写：①`log` 临时置 `state.epoch=None`——IterableDataset 下 epoch 误导（`:169-174`）；②`get_train_dataloader`（`:176-218`）先 `ignore_data_skip=True`（`:181`），global_step>0 则 `reset_seed(seed+global_step)`（`:184-195`）再手工组 DataLoader（`:206-218`）；③`train`（`:220-248`）在 super().train 前预载 `TrainerState.load_from_json`（`:244-246`），且 resume=True 无 checkpoint 时抛错而非静默重训（`:230-235`）。`compute_loss`（`:254-327`）委托父类（`:270-275`）、记 `self.loss`（`:284`）、每 logging_steps 算 token 级准确率（`:134-148`，action_offset 非空时只取动作区段 `:294-297`），并打印 GT vs Pred 前 20 个动作 token（`:311-325`）。

**base_config.py**。`get_deepspeed_config`（`:155-167`）极简分流：stage==2 读 `zero2_config.json`、stage==3 读 zero3（`:160-163`），非法 stage 抛错；json 内 batch/fp16 均为 "auto" 由 HF Trainer 注入。`validate`（`:169-214`）：physical_embodiment 必带 embodiment_tag（`:177-178`）、每个标签必须已注册并裁剪 modality_configs（`:182-193`）、mix_ratio 总和>0（`:196-198`）、action_configs 缺省补 ABSOLUTE/NON_EEF/DEFAULT（`:203-210`）、fp16/bf16 互斥（`:213-214`）。安全：`Config.save` 用 `yaml.safe_dump` 且 Enum 先降级字符串（`:90-104`），`_load_safe_yaml` 拒绝旧 `!!python/object` 标签（`:54-75`）——加载配置不再是代码执行入口。

## 三、外部连接

launch_finetune 依赖 05 篇契约层（resolve/importlib 注册）与 06 篇数据层（datasets 块被 DatasetFactory 消费）；experiment 依赖 `MODEL_REGISTRY`（`:36/:248`）与 `run_on_rank0` 护栏（`:216/:223-229`）；trainer 的 reset_seed 协议由 ShardedMixtureDataset 实现（06 篇 `:487-512`）；TrainingArguments 接收 base_config 的 deepspeed 产物（`:295`）。

## 四、数据流

配置流：CLI flag → FinetuneConfig → load_dict 合入默认 Config → validate 裁剪 → run 组 TrainingArguments。控制流：run → pipeline.setup()（载基座权重、建 processor/dataset/collator）→ Gr00tTrainer.train（预载 TrainerState → get_train_dataloader 可能 reset_seed → HF 循环调 compute_loss）→ save_model。检查点流：save_steps 保存 → 回调补 processor → resume 时 global_step 驱动种子重置。

## 五、设计决策

1. **门面层硬编码策略值（`:98-102`）**：vision backbone 固定 Cosmos-Reason2-2B、可训参数强制 fp32、启用相对动作——是 N1.7 微调配方而非用户旋钮，易漏读。
2. **num_gpus 与 WORLD_SIZE 对账（`:53-69`）**：在信任边界拦截"配置世界"与"启动器世界"的静默分歧，多数分布式入口没有这层校验。
3. **resume=重播种而非数据跳跃**：IterableDataset 不可 seek，选换种子继续（代价=不可复现）而非 skip 空转（`trainer.py:191-195`）。
4. **甄别（与类名直觉冲突，以源码为准）**：`Gr00tTrainer` docstring 自称"bypasses torch dataloader and makes data collator async"（`trainer.py:153`），但 `get_train_dataloader` 实际返回标准 `torch.utils.data.DataLoader`（`:218`）；`_PrefetchIterator`（`:77-115`，Queue maxsize=4 `:85`）与 `_BatchIterator`（`:51-74`）全仓 grep 仅剩定义零调用——死代码，真正的异步预取在数据集侧（06 篇）。
5. **DeepSpeed 只做 2/3 两档 json 分流**（复杂度交给 HF "auto" 注入）；**训练即回归测试**：assert_loss_less_than（`:373-378`）+ GT/Pred token 打印（`:311-325`）让 CI 冒烟训练可机判。

## 六、新人提示

- 单卡跑通再加卡：num_gpus 必须与 WORLD_SIZE 一致（`:63-69`），global_batch_size 必须被 num_gpus 整除（`:75-77`）。
- 微调首选默认四开关（冻结 LLM+视觉、训 projector+diffusion）；显存富余再开 tune_llm。
- 想复现就别 resume（会重播种 `:191-195`）；日志 "GT vs Pred (first 20 action tokens)"（`:319-325`）数值靠拢是最直观学习信号。
- per_gpu_batch_size/warmup_steps 是弃用中旧字段，当前仍覆盖新字段（`experiment.py:88-96`）。

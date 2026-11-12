# 01 · Driver 与四 Trainer：会话中枢的继承谱系

## 角色定位

`makani/utils/driver.py` + `makani/utils/training/` 四 Trainer + `makani/utils/inference/inferencer.py` 是 makani 的"会话层"：一次训练/推理的全部生命周期——配置解析、模型/优化器/调度器/数据装配、checkpoint 管理、执行流——都由 Driver 家族托管。七个 CLI 入口（train.py 等）只做参数解析与调用，真正的心跳在这里。

## 内部结构

**Driver（driver.py:61，ABC 元类，1098 行 24 方法）**：
- 装配：`__init__`:99（params/world_rank/device）、`_set_dataloader`:143、`_set_default_parameters`:149、`_set_data_shapes`:209；
- checkpoint 双格式：`restore_from_checkpoint`:460 分派 `_restore_checkpoint_legacy`:551（按模型并行 rank 分文件，含优化器/调度器完整状态）与 `_restore_checkpoint_flexible`:627（可换并行配置恢复，优化器恢复实验性）；写侧 `save_checkpoint`:680 → `_save_checkpoint_legacy`:716 / `_save_checkpoint_flexible`:781。README.md:199 钉版两种格式语义边界；
- 优化器/调度器：`get_optimizer`:857、`get_scheduler`:912；
- dataloader 状态：`get_train_dataloader_state`:412 / `get_train_dataloader_for_restore`:425 / `gather_dataloader_state`:448 / `_restore_dataloader_state`:511——异步加载断点续训的生存线；
- 观测：`_log_timers`:68、`_watch_model`:75、`_init_wandb`:292、`init_visualizer`:977 与 `_visualize_step`:1080、`dump_weights_and_grads`:842。

**四 Trainer 继承谱系（不并列！）**：确定性 `Trainer(Driver)`（deterministic_trainer.py:62，807 行，makani.train 核心——**类名就叫 Trainer 不是 DeterministicTrainer**）；`EnsembleTrainer(Trainer)`（ensemble_trainer.py:62，788 行，HENS 多成员，继承自确定性 Trainer）；`StochasticTrainer(Driver)`（stochastic_trainer.py:60，随机插值生成式训练，入口 train_stochastic.py）；`AutoencoderTrainer(Driver)`（autoencoder_trainer.py:57，入口 train_autoencoder.py）。公共训练逻辑在 training_helpers.py。

**Inferencer（inferencer.py，917 行）**：在线推理 + 自回归 rollout + 逐窗评分 + 输出写出；评分的存储后端是 rollout_buffer.py（1572 行）的 DataBuffer/RolloutBuffer/MeanStd/时间平均/谱平均/纬向谱平均家族——支持 HDF5 `direct` VFD（O_DIRECT 绕页缓存，`odirect_available`:59）与 GDS（:44-46 注释钉版 direct/gds 两驱动都不保证存在，:82 GDS 写路径吃 cuFile 指针，:215 `enable_odirect` 开关）。

**benchmark.py（657 行）**：`get_benchmark_argument_parser`:91、`build_trainer`:256、`run_inference`:264——在合成数据上计时训练/推理步，架构与并行分解对比无需数据集（README.md:85）。

## 外部连接

- 上游：YParams（yaml target）+ argument_parser.py（181 行 flag）注入 params；`parse_dataset_metadata`（parse_dataset_metada.py:22）展开数据元信息（train.py:150 等五入口调用）。
- 下游：Trainer 调 `model_registry.get_model` 构网、LossHandler（loss.py:58）算损失、comm.py:34 命名进程组与 mpu 栈通信、checkpoint_helpers.py（446 行）做分布式状态 gather/scatter。

## 数据流

CLI flag + yaml target → YParams → Driver.__init__ → 检查点恢复（或全新）→ Trainer 训练循环（dataloader→Preprocessor2D→StepWrapper 前向→LossHandler 反传→save_checkpoint 周期落盘 / Inferencer 侧：rollout 循环→逐窗评分写 RolloutBuffer→写出）。

## 设计决策

1. **模板方法而非插件系统**：Driver ABC 收编全部横切关注点（checkpoint/优化器/可视化），Trainer 只写训练循环差异——研究代码的务实选择。
2. **双 checkpoint 格式**：legacy 保"同配置完整恢复"，flexible 保"换并行配置可恢复"，两者不可兼得且显式声明（README.md:199）。
3. **dataloader 状态也进检查点**：异步加载（DALI/GDS）下数据位置是训练状态的一部分，漏存即重复读盘（driver.py:412-551）。
4. **EnsembleTrainer 复用 Trainer**：集合训练只是在确定性训练上叠多成员，继承而非平行实现（ensemble_trainer.py:62）。
5. **benchmark 与数据解耦**：合成数据计时让并行分解调优不碰 ERA5（benchmark.py:85、README.md:85）。

## 新人提示

找"确定性 Trainer"类名时直接搜 `class Trainer`；换并行配置恢复只支持模型权重，优化器状态要等 flexible 格式成熟（README.md:199）；调 Inference 输出性能先看 rollout_buffer 的 O_DIRECT/GDS 探测日志（:59/:82）；计时对比一律走 benchmark.py 而不是往训练脚本里塞计时器。

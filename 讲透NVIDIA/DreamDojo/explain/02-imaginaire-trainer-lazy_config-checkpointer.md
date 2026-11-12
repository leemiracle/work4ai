# ② imaginaire 训练核心：ImaginaireTrainer + lazy_config + Checkpointer

## 角色定位

`cosmos_predict2/_src/imaginaire/`（115 文件的 L04 层）是 DreamDojo 全部训练任务的"发动机+底盘"：`trainer.py` 编排主循环，`lazy_config/` 提供"python 即配置"的延迟装配体系，`checkpointer/` 三级检查点体系（单机线程异步 / DDP 分片 / torch.distributed.checkpoint 分布式）。predict2 世界模型、reason1 VLM、distill 蒸馏线全部站在这一层之上——理解它等于拿到全仓训练代码的钥匙。

## 内部结构

**ImaginaireTrainer**（`trainer.py:45`，353 行）生命周期三段。`__init__`（57）：`distributed_init()` 起 NCCL → Megatron `parallel_state.initialize_model_parallel`（85-96，兼容新旧签名：有 `create_gloo_process_groups` 就传 False）→ rank0 落 config.pkl/yaml 双份（107-109）→ seed/cudnn/TF32 → 装配 `CallBackGroup`（127）→ **检查点分叉**（129-134）：`config.checkpoint.type is None` 用内置 `Checkpointer`，否则 lazy 实例化 DCP 版 → SIGALRM 挂训练步超时哨兵（147）。`train`（149）：模型上卡 → `model.init_optimizer_scheduler`（168）→ `checkpointer.load` 拿起始 iteration（172）→ DDP 或 FSDP 包装（175-181 硬校验）→ 双层 while 主循环；每 optimizer 步 iteration+1，达 `save_iter` 落盘（242）、`validation_iter` 验证（246）、`signal.alarm` 重置超时（249）。`training_step`（265）：`distributed.ddp_sync_grad`（292）只在梯度累积**最后一步**开 DDP 同步（no_sync 优化），前向 `model_ddp.training_step`（298），反向 `grad_scaler.scale(loss/grad_accum_iter).backward()`（305）+ `on_after_backward` 钩子（308），满窗后 step/scheduler/zero_grad（321-329）。

**ImaginaireModel 契约**（`model.py:23`）：子类必须实现 `training_step/validation_step/forward`（56/72/88 三处 NotImplementedError），默认实现给 `init_optimizer_scheduler`（38：把 `self.parameters()` 注入 optimizer 配置再 instantiate——**lazy 装配的教科书用法**）与三钩子 `on_train_start/on_before_zero_grad/on_after_backward`（100/108/120，trainer 在精确时点回调）。

**lazy_config**（fvcore/detectron2 血统）：`lazy.py:87` `LazyCall`——`LazyCall(nn.Conv2d)(in_ch=32)` 不执行调用而是返回带 `_target_` 的 DictConfig（109-121，先填 `get_default_params` 默认值再覆盖 kwargs）；`LazyConfig.load`（253）用 `_patch_import`（165）劫持 builtins.__import__，让配置文件的相对 import 按文件位置解析、模块不进全局缓存、导入 dict 自动转 DictConfig——配置即代码。`instantiate.py:56` 递归展开 `_target_`：先递归实例化子配置（90）、字符串 target 再 import（96-97），比 hydra 快（85-87 注释引 issue #1200）。`__init__.py:15` `LazyDict` 仅作类型标记。

**Checkpointer 三级**：
1. 单机基线 `utils/checkpointer.py:43`：`save`（70）rank0 组 state_dict（89-98），CPU 化后**独立线程**落盘（105-110），训练不阻塞；`load`（160）三级优先：latest_checkpoint.txt 断点续训 → `load_path` 指定权重 → 随机初始化（187-206 注释明示）。
2. 抽象+DDP `checkpointer/base.py:28` `AbstractCheckpointer`（save/load_dirname 自动拼 s3 或本地）→ `checkpointer/ddp.py:35`：`generate_save_state_dict`（167）只让 `rank_dp_w_cp==0` 出 weight、全局 rank0 出 trainer 态（183-186），`_save_worker`（165）经 `easy_io.dump(fast_backend=True)` 上传后 `mp_gloo_pg` barrier（178）。
3. DCP 分布式 `predict2/checkpointer/dcp.py:461`：`ModelWrapper/OptimizerWrapper`（246/335）实现 `Stateful` 协议喂 `dcp.save/load`；`AsyncMode`（360）支持 pinned-memory 异步——`save_checkpoint_in_background`（382）起独立进程，**MASTER_PORT+2 避让主进程**（402-403），队列收 `(state_dict, path)` 与 `Terminate/SaveDone` 信号（365-377），失败软回报不退出（436-438）。reason1 线另有平行 DCP（`reason1/parallelisms/dcp_checkpointer.py:186`）与 distill 变体（`distill/checkpointer/dcp_distill.py:39`）。

## 外部连接

上游：`scripts/train.py:19` → `cosmos_oss.scripts.train.main`（`packages/cosmos-oss/`）→ `trainer.train(model, dl_train, dl_val)`（其 56 行）。模型侧全走契约：`predict2/models/text2world_model_rectified_flow.py:122` 继承 ImaginaireModel 并复用默认 `init_optimizer_scheduler`。配置侧：所有 experiment py（如 `interactive/configs/experiment/exp_action_warmup.py`）都是 LazyCall/LazyDict 的组合。并行侧：`utils/distributed.py` 与 `utils/context_parallel.py`（a2a_cp 上下文并行）由 trainer 的 megatron 初始化铺垫。回调侧 `utils/callback.py:606` 行 CallBackGroup 提供 30+ 钩子点位（on_before_forward/on_after_backward/on_save_checkpoint...）。

## 数据流

一次断点续训：torchrun 起 N 进程 → 各自 `ImaginaireTrainer(config)` → `checkpointer.load`：读 latest_checkpoint.txt → 本地或 S3StorageReader 拿 state_dict → load_state_dict（DDP 版先从 MP 组 rank0 广播，`ddp.py:245` `load_broadcast_state_dict`）→ 返回 iteration 续跑。每 save_iter：callbacks.on_save_checkpoint（可注入 EMA）→ 线程/子进程异步写 → success 回调记账。**配置流**独立成线：experiment py 被 `LazyConfig.load` 动态 import → hydra 覆盖合并（yaml 只是差量）→ `instantiate` 递归物化出模型。

## 设计决策

1. **同步开关精确到梯度累积窗口**（`trainer.py:292`）：中间步 no_sync 省 AllReduce，是吞吐关键。
2. **配置用 python 不用纯 yaml**：继承/循环/条件全保留，代价是要 `_patch_import` 这种侵入式 hack（`lazy.py:165-228`）与随机包名防缓存（160）。
3. **落盘永远异步**：线程（单机/DDP）或独立进程（DCP pinned-memory），且先 join 上一次再起新一次（`utils/checkpointer.py:102-103`）防止 IO 积压。
4. **检查点按 rank 角色分工**而非全 rank 冗余：dp_w_cp rank0 出 model/optim，全局 rank0 出 trainer——FSDP/CP 场景下省显存与带宽。
5. **旧字段迁移靠启动期硬校验**：`config.model.context_parallel_size` 已废弃，与 `model_parallel.context_parallel_size` 同时设置直接 raise（`trainer.py:70-74`），不静默。

## 新人提示

- 找"为什么没存上检查点"：先看 `on_save_checkpoint_success` 日志（`utils/checkpointer.py:112-114` 注释明说 end 回调不准，success 才准）。
- DCP 后台进程的失败是**软失败**（`dcp.py:436-438`），训练不中断——终检时必须核对 SaveDone 的 succeeded 标志。
- **勘误（源码实证）**：仓库存在两个同名 `ImaginaireTrainer`——`imaginaire/trainer.py:45` 与 `distill/trainer/trainer_distillation.py:43`（蒸馏线魔改：三优化器切换等），import 时必须看清来源；同理 `checkpointer` 名字也出现在 `imaginaire/utils/checkpointer.py`、`imaginaire/checkpointer/ddp.py`、`predict2/checkpointer/dcp.py`、`reason1/parallelisms/dcp_checkpointer.py` 四处，作用各异。
- 写新模型只要实现三个抽象方法+按需覆写三钩子；优化器/调度器配置从 defaults（`predict2/configs/common/defaults/optimizer.py`）抄起改。

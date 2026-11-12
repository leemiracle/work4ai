# DreamDojo 新人上手指南（ONBOARDING）

> 基于知识图谱（2088 节点/4968 边，commit `02f119b`）与源码逐行核实撰写；所有行号锚均已在源码验证。
> DreamDojo = NVIDIA 开源的"从大规模人类视频学习的交互式机器人世界模型"训练框架，论文 arXiv:2602.06949（`README.md:36`）。代码主体是内嵌的 **Cosmos-Predict2**（`cosmos_predict2/`）+ **Imaginaire4** 训练基建（`cosmos_predict2/_src/imaginaire/`）+ **reason1** VLM 并行线（`cosmos_predict2/_src/reason1/`）+ **GR00T 梦境数据层**（`groot_dreams/`）+ **LAM 隐动作模型**（`external/lam*`）五大板块的合体。

## 1. 项目定位与心智模型

一句话：**DreamDojo 把"视频扩散世界模型"训成"能被机器人动作驱动、蒸馏后 10FPS 实时交互的学生模型"的全流程开源复现仓**。README 宣告三大贡献（`README.md:14-18`）：44k 小时人类视频预训练数据、可泛化的基础机器人世界模型、蒸馏后 10FPS 实时交互——对应仓库五阶段工作流：LAM 预训练 → 世界模型预训练（POSTTRAIN 文档实为阶段名）→ 后训练（真机域 SFT）→ Self-Forcing 滚动训练 → DMD2 蒸馏。七个 `launch*.sh`（`launch.sh`、`launch_teacher_gen.sh`、`launch_warmup.sh`、`launch_self_forcing.sh`、`launch_student_inference.sh`、`launch_student_inference_teleop.sh`）每阶段一个启动器，全部以 `torchrun -m scripts.train` 收口（`scripts/train.py:17-19`，它只是 `cosmos_oss.scripts.train.main` 的薄转发）。

技术底座三件套：整流流（Rectified Flow）扩散 + DiT 骨干 + 机器人动作/LAM 隐动作条件。模型家族 2B/14B 两档（`configs/` 下 `{2b,14b}_480_640_{pretrain,agibot,g1,gr1,yam}.yaml` 十个 hydra experiment 覆盖盖五个域）。

## 2. 仓库布局与目录地图

- `cosmos_predict2/` 门面 API：`action_conditioned.py`（动作条件生成全流程）、`inference.py`（`Inference.generate` 世界 rollout 统一入口）、`config.py`（pydantic 枚举定位检查点）。
- `cosmos_predict2/_src/imaginaire/` 训练基建：`trainer.py:45` `ImaginaireTrainer` 主循环；`model.py:23` `ImaginaireModel` 模型契约；`lazy_config/`（fvcore 血统的延迟求值配置，`lazy.py:87` `LazyCall`）；`checkpointer/`（`base.py:28` `AbstractCheckpointer` → `ddp.py:35` / `tp_ema.py:26`）；`utils/` 81 个工具（distributed/context_parallel/easy_io/cluster_env）；`datasets/` webdataset 生态与 `auxiliary/guardrail/`（LlamaGuard3/Qwen3Guard/人脸模糊安全护栏）。
- `cosmos_predict2/_src/predict2/` 世界模型本体：`networks/minimal_v4_dit.py:1418` `MiniTrainDIT` 全家族共同 DiT 基座；`models/text2world_model_rectified_flow.py:122` 整流流主模型（`models/text2world_model.py:133` `DiffusionModel` 是其基类，**多处 `import ... as Text2WorldModel` 的别名**）；`models/video2world_model_rectified_flow.py:62` 视频续生变体；`tokenizers/`（Wan2.1/2.2 VAE 封装）与 `text_encoders/`（Reason1/UMT5）；`interactive/`（Self-Forcing 主线：`models/action_video2world_self_forcing.py:47`）、`distill/`（DMD2 蒸馏：`models/video2world_model_distill_dmd2.py:99`）、`action/`（GR00T 动作条件线）、`camera/`（多相机线）、`checkpointer/dcp.py:461`（torch.distributed.checkpoint 分布式检查点）。
- `cosmos_predict2/_src/reason1/` 内嵌移植的 torchtitan 式 VLM 训练栈（Qwen2-VL/2.5-VL 全家：`models/vlm_qwen.py`、`networks/qwen2_5_vl.py`），为世界模型产出 reason embeddings。
- `groot_dreams/` RL/机器人数据层：`data/dataset.py:76` `LeRobotSingleDataset` 读分片 parquet+视频；`data/schema.py` LeRobot 模态 schema；`data/transform/`（video/state_action/concat 三链）。
- `external/lam` 与 `external/lam_project`：LAM 双副本（研究版被 DreamDojo 消费，生产副本独立成包，详见第 7 节）。
- `packages/`：`cosmos-oss`（根工程配置正本+训练入口）、`cosmos-gradio`（演示）、`cosmos-cuda`（pip 依赖哨兵包）。
- `shared_meta/`：10 个 JSON——`{AgiBot,G1,GR1_human,GR1_unified,YAM}_{modality,stats}.json`，机器人本体关节段切分与逐维归一化统计（如 `GR1_unified_modality.json` 里 `state.left_arm` 占 `observation.state` 的 0..7 段）。
- `docs/` 七篇指南与七阶段一一对应（SETUP/LAM/PRETRAIN/POSTTRAIN/DISTILL/EVAL/ISSUES）。

## 3. 构建与启动链路

`justfile`（158 行）是任务总入口：`setup`（uv sync 按 `.cuda-name` 持久化 CUDA extra）、`lint`、`test-install`（四级测试 test-cpu/gpu 1与8卡/level-0/1/2）、`release-check`（license+link 检查）。`Dockerfile` 基于 `nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04`，uv sync --locked 后 STANDALONE 模式拷仓 `just install`，ENTRYPOINT 指向 `bin/entrypoint.sh`。

启动链三步：①`source .venv/bin/activate`；②`PYTHONPATH=$(pwd)`（`launch_self_forcing.sh:29`；注意 `launch.sh:23` 还残留内网硬编码路径 `/mnt/amlfs-01/shared/shenyuang/DreamDojo`，公开仓需自行改掉）；③`torchrun --nproc_per_node=8 -m scripts.train --config=<python 配置> -- experiment=<configs/下 yaml 名>`。配置体系是"python 为骨、yaml 为皮"：`--config` 指 lazy_config python 文件（如 `cosmos_predict2/_src/predict2/interactive/configs/config_distill.py`），`experiment=` 用 hydra 语法把顶层 yaml 的覆盖注入。wandb 必须显式给 key（`launch_self_forcing.sh:33` 的 `${WANDB_API_KEY:?}` 会硬失败）或 `job.wandb_mode=disabled`。

## 4. 核心架构分层（图谱 14 层导览）

- **L01 入口/构建**：launch*.sh+justfile+Dockerfile；**L02 训练配方**：顶层 10 yaml+shared_meta 契约+cosmos_predict2 门面；**L03 注意力多后端**：`attention/frontend.py:55` `attention()` 统一分发到 flash2/flash3/cudnn/natten（`backends.py:107` `get_backend_list` 按 SM 架构排序择优：SM90 → flash3 优先，SM100/103 → cudnn 优先，SM80 → flash2）；**L04 训练核心**：trainer/lazy_config/checkpointer；**L05 数据与护栏**：webdataset+guardrail；**L06 网络与编解码**：minimal_v4_dit/wan2pt1/2、tokenizers、text_encoders、rectified_flow 调度器（`schedulers/rectified_flow.py:76`）；**L07 动作/相机条件**：`action/` 的 GR00T 推理管线（`action/inference/inference_gr00t.py`）与 `camera/networks/dit_multiview_camera.py`；**L08 实验配置**：predict2 configs 矩阵；**L09 推理交互与蒸馏**：interactive+distill；**L10 reason1 VLM 并行线**；**L11 groot_dreams 数据层**；**L12 LAM 双副本**；**L13 packages 三件套**；**L14 文档与脚本副本**。

依赖主干：门面 API → lazy_config 装配 `Text2WorldModelRectifiedFlow` →（训练）ImaginaireTrainer 主循环 +（数据）groot_dreams/webdataset →（算子）imaginaire attention →（检查点）DCP/本地双轨。

## 5. 关键数据流

**训练一步**（`trainer.py:149-263`）：`next(dataloader_train_iter)` → `misc.to(data_batch,"cuda")` → `training_step`（`trainer.py:265`）：梯度累积窗口内 `distributed.ddp_sync_grad` 只在最后一步开同步（`trainer.py:292`），`model_ddp.training_step(data, iteration)` 前向（`trainer.py:298`），`grad_scaler.scale(loss/grad_accum_iter).backward()`（`trainer.py:305`），满窗口后 step+scheduler+zero_grad（`trainer.py:321-329`）；iteration 达 `checkpoint.save_iter` 触发异步落盘（`trainer.py:242-243`）。

**整流流前向**（`text2world_model_rectified_flow.py:856-937`）：在线算 reason embeddings（858-861）→ **LAM 隐动作注入**（863-869：`lam_video` 重排后 `self.lam.lam(lam_input)` 取 `z_rep`，乘进 action 末 32 维）→ VAE encode 得 x0 → `rectified_flow.sample_train_time` 采 t（877）→ `get_interpolation(eps,x0,sigma)` 造 xt/vt（909）→ DiT 预测 velocity（911）→ MSE + 0.1×帧间运动一致性损失（919-925）。

**交互式一帧**（`interactive/models/action_video2world_self_forcing.py:349-454`）：`generate_streaming_video` 逐帧循环：`generate_next_frame`（277，@torch.no_grad 外层）在 `selected_sampling_time` 少步时间表上多步去噪（308-344），只在最后一 hop 开梯度（313）；每帧生成后 `update_kv_cache`（456）把**模型自己生成的帧**写入 KV cache 供下一帧attend——这就是"自强迫"：条件历史来自自身 rollout 而非 GT。

## 6. 扩展点与二次开发

- **换注意力后端**：`Attention(backend=...)`（`minimal_v4_dit.py:439` 五选一：transformer_engine/torch/torch-flex/minimal_a2a/i4），底层经 `imaginaire/attention/frontend.py`。
- **加数据域**：仿 `groot_dreams/data/embodiment_tags.py:4` 加 EmbodimentTag → 写 `shared_meta/{X}_modality.json`+`{X}_stats.json` → `groot_configs.py:8` `construct_modality_config_and_transforms` 加分支 → 顶层加 yaml。
- **加实验**：仿 `predict2/interactive/configs/experiment/exp_action_warmup.py`（hydra defaults override 组装 LazyDict），顶层 yaml 只放差量。
- **换检查点策略**：`config.checkpoint.type is None` 走单机 `Checkpointer`（`trainer.py:129-134`），否则 lazy 实例化 DCP（`predict2/checkpointer/dcp.py:461`，支持 `AsyncMode.ASYNC_WITH_PINNED_MEM` 后台进程保存，`dcp.py:360`）。
- **模型侧钩子**：`ImaginaireModel` 的 `on_train_start/on_after_backward/on_before_zero_grad`（`model.py:100-129`）。

## 7. 常见坑与勘误（源码实证）

1. **`CheckpointMode` 四处平行定义**：`networks/selective_activation_checkpoint.py:34`（仅 NONE/MM_ONLY/BLOCK_WISE 三值）、`networks/minimal_v4_dit.py:182`、`camera/networks/dit_multiview_camera.py:171`、`camera/networks/dit_multiview_camera_ar.py:172`（后三处九值全同）——改枚举须四处同步。
2. **`torchtitan_utilts` 上游拼写笔误**：`reason1/parallelisms/` 下文件名本身少个 i（`vlm_base.py:30` 等四处 import），非本地笔误，照抄即可。
3. **LAM 双副本不同源**：DreamDojo 消费的是研究版 `external/lam`（`text2world_model_rectified_flow.py:70`），其 `modules/lam.py:57` 有 `assert T == 2` 且 `z_rep=z_mu` 只取均值（72）；生产副本 `external/lam_project/lam/modules/lam.py:74-76` 支持 T>2、训练时从后验采样。import 前缀也不同：前者 `external.lam.*`、后者 `lam.*`。
4. **`tokenizers/cosmos.py` 名不副实**：28 行小文件实为 Wan2pt1/Wan2pt2 VAE 的 LazyCall 配置注册表（`cosmos.py:22-28`），没有 Cosmos 自研 VAE 实现。
5. **`launch.sh:23` 残留内网绝对路径**（`/mnt/amlfs-01/shared/shenyuang/...`），pretrain/agibot 等 yaml 的 dataset_path 也全是内网路径（如 `configs/2b_480_640_pretrain.yaml:34-36`），开源复现需替换为 HF 数据集本地路径。
6. **CFG 公式两处不一致**：`text2world_model_rectified_flow.py:508` 是 `uncond+g*(cond-uncond)` 标准 CFG；`video2world_model_rectified_flow.py:209` 却是 `cond+g*(cond-uncond)`——继承未对齐，引用时注意口径。
7. **`ImaginaireTrainer` 双定义**：`imaginaire/trainer.py:45` 与 `distill/trainer/trainer_distillation.py:43` 同名平行（蒸馏线魔改版），import 时别拿错。
8. **`frontend.py:421` 疑似上游 bug**：`value_t = key.reshape(value.shape...)`——multi-dim 降维路径把 key 的数据 reshape 给 value（当 K/V 形状不同时结果错误；当前调用路径 K=V 同形所以未爆）。
9. **flash3 仅 Hopper**：`flash3/meta.py:41` `arch_tag != 90` 直接返回空 dtype 表；且 `flash3/checks.py:81` 明确不支持 torch.compile。Blackwell(SM100/103) 上最优后端是 cuDNN。

## 8. 上手路线图（建议 7 步）

1. 读 `README.md`+`docs/SETUP.md`，`just setup` 建环境（需 CUDA 12.8/13.0 + 8 卡）。
2. 读 `docs/LAM.md` 跑通 LAM：入口 `external/lam_project/main.py`。
3. 精读 `models/text2world_model_rectified_flow.py`（1264 行）——整流流训练/推理/EMA/state_dict 全在这。
4. 用 `configs/2b_480_640_gr1.yaml`+`launch.sh` 复现 GR1 后训练（先把内网路径换掉）。
5. 精读 `interactive/models/action_video2world_self_forcing.py`（495 行）+ `launch_self_forcing.sh` 理解自强迫与 KV cache rollout。
6. 精读 `distill/models/video2world_model_distill_dmd2.py:184-308` 的 generator/critic 双相损失，跑 `launch_student_inference.sh` 验证 10FPS 学生。
7. 按需深入：多机训练看 `imaginaire/utils/distributed.py`+`context_parallel.py`；安全护栏看 `auxiliary/guardrail/`；评估看 `docs/EVAL.md` 与 `packages/cosmos-oss` 的 VQA 管线。

> 词表速查：RF=Rectified Flow 整流流；DMD2=Distribution Matching Distillation 2；LAM=Latent Action Model；CR1/Reason1=Qwen2.5-VL 改造的 reason embedding 编码器；DCP=torch.distributed.checkpoint；SAC=selective activation checkpointing；CP=context parallel。

# ⑤ 交互主线：Self-Forcing 自强迫滚动与 DMD2 蒸馏

## 角色定位

`predict2/interactive/` + `predict2/distill/` 两子包合起来是 DreamDojo 从"多步教师世界模型"到"10FPS 实时学生"的核心创新链：DMD2（Distribution Matching Distillation 2）把整流流底座蒸馏成少步生成器，Self-Forcing 再让学生**吃自己生成的历史帧**继续滚动训练，消除"训练吃真值、推理吃自己"的 exposure bias。入口模型 `interactive/models/action_video2world_self_forcing.py:47` `ActionVideo2WorldModelTrigflowSelfForcingDMD2` 同时继承两者：父类 `Video2WorldModelDistillDMD2TrigFlow`（`distill/models/video2world_model_distill_dmd2.py:99`，mixin 组合 `DistillationCoreMixin`+`TrigFlowMixin`+Video2WorldModel）。

## 内部结构

**三体装配**（`set_up_model`，self_forcing 93-178，魔改自 mixin 175）：teacher 网必须给 ckpt（104 硬断言）→ student `self.net`（no_fsdp 模式给因果学生网，117）→ fake score 网以 teacher 权重初始化（121-133，逐 key 对账日志）→ 判别器头（139-148，`distill/networks/discriminator.py` 的多头 CrossAttention 池化，`num_branches == len(intermediate_feature_ids)` 校验）→ teacher 冻结（160）。EMA 用闭式系数 `np.roots([1,7,16-s**-2,12-s**-2]).real.max()`（175）——DMD2 论文的半衰期换算。

**Student/Critic 双相**（`distillation_base_mixin.py:634-686` `training_step`）：`is_student_phase(iteration)`（439，按 `phase1_lr` 周期切换）分支——Student 相：net.train 可训、fake score/判别器 eval 冻结（661-667），走 `training_step_generator`；Critic 相反过来（672-683），训 fake score + 判别器。多优化器调度由 `get_optimizers(iteration)`（459）按相位取。

**Generator 损失**（`video2world_model_distill_dmd2.py:184-308`）：①`n_steps` 在 rank0 采 random 后 broadcast（217-222）——少步数本身是训练分布；②`prepare_random_slice`（405-418）随机截尾：`grad_start_idx = max(0, end_frame-(state_t-1))`，只对尾部帧反传——**长滚动只训最后几帧**的显存关键；③`backward_simulation`（151）少步采样出 `G_x0_theta`（with_grad=True 且梯度只开在最后一 hop）；④重加噪构造判别器输入（247-251，TrigFlow 坐标 `cos/sin` 混合）；⑤fake score 与 teacher 对同一噪声输入各出 x0（255-264，teacher 可 CFG）；⑥**分布匹配梯度**：`grad = (x0_fake - x0_teacher)/weight_factor`（283，逐样本归一权重 275-279 截断 min=1e-5），再用 `(G - (G-grad).detach())**2` 技巧（287）让该"伪梯度"只流回 student——teacher/fake score 零梯度；⑦可选 GAN：判别器吃 fake score 中间特征出 logits，generator 用 BCE(fake,1)（292-300）。Critic 相（311-403）对称训 fake score 回归 + 判别器 BCE。

**自强迫滚动**（`action_video2world_self_forcing.py`）：`generate_streaming_video`（349-454）逐帧循环——`make_network_kv_cache`（393，`cache_frame_size=3` 滑窗，-1 全量）→ 初始帧 `update_kv_cache` 预填充（423-427）→ 每帧 `generate_next_frame`（277）：在 `config.selected_sampling_time` 少步时间表上迭代（308-344），中间步以 `cos(t_next)*x0/sigma_data + sin(t_next)*noise` 重加噪（342-344），**仅最后一 hop 开梯度**（313，`enable_grad_on_last_hop`）→ 生成帧写回 `output_latents` 并 `update_kv_cache`（448-452）——条件历史由此完全来自模型自身输出（真值只在首帧），这就是 Self-Forcing。CUDA graph 预捕获 `precapture_cuda_graphs`（`interactive/networks/dit_action_causal.py:47-108`，按 t_idx×block 逐图缓存）；无状态 KV 模式（`stateless_kv`，364-368 注释）为 torch.compile 兼容把 cache 状态外置成张量（399-408）。`denoise_edm_seq`（180-238）是 EDM 参数化去噪：条件帧时间替换为 `atan(sigma_conditional/sigma_data)`（204-205），`c_skip/c_out/c_in/c_noise` 四系数重建 x0（208-234）。

**因果动作 DiT**：`ActionChunkCausalDITwithConditionalMask`（`dit_action_causal.py:38`）继承 action 线 LVG DiT，`forward` 按 `video_pos` 关键字分流到 `forward_seq`（111-113）；动作块嵌入加进 timestep 嵌入与 AdaLN-LoRA 双流（152-159）；`_num_action_per_latent_frame`（304 使用）把每个潜帧的动作块切片注入。

## 外部连接

启动：`launch_self_forcing.sh`（torchrun config=config_distill.py + `experiment=exp_action_self_forcing`）→ 先 warmup（`config_warmup.py`/`exp_action_warmup.py`，`launch_warmup.sh`）→ 自强迫 → 学生推理 `launch_student_inference.sh`（`interactive/inference/action_video2world.py`，teleop 变体接遥操作）。蒸馏骨架 mixin 同时服务非交互 DMD2 线（`distill/configs/experiment/experiments_dmd2_predict2p5.py`，Predict2.5 底座）。检查点用 `distill/checkpointer/dcp_distill.py:39` 的三体分桶 DCP。回调 `interactive/configs/callbacks.py` 挂 wandb 滚动视频可视化（`latest_backward_simulation_video`，273 行）。

## 数据流

训练一步（student 相）：data_batch（GR00T 序列）→ conditioner → `training_step_generator`：噪声 backward_simulation 逐帧生成（KV cache 滚动，仅尾帧带梯度）→ 重加噪 → fake score/teacher 打分 → DMD 伪梯度 + GAN 损失 → 反传只更新 student。Critic 相无 backward_simulation 梯度（353 行 `with_grad=False`）。推理（10FPS）：学生 net + 预捕获 CUDA graph + KV cache，每帧 n_steps≤len(selected_sampling_time) 少步去噪，动作流实时驱动。

## 设计决策

1. **梯度只开最后一 hop + 随机截尾**（`grad_start_idx`）：把 O(T²) 的滚动反传播压成 O(T·k)，是长时程自强迫可训的工程前提。
2. **相位制而非交替 batch**：student/critic 按迭代整段切换，锁 eval/train 态避免 BN/EMA 干扰，且 `get_effective_iteration`（449）让 LR 调度按各自相位独立计数。
3. **fake score 用 teacher 热启动**：DMD2 的 fake score 初期最不稳，继承 teacher 权重省去前期崩塌。
4. **DMD 伪梯度 detach 技巧**（287）：损失值无意义（恒可逼近 0），真正作用是把 (x0_fake-x0_teacher) 当梯度注入——读日志别把它当 loss 曲线解读。
5. **KV cache 三形态**（状态化模块态/无状态列表/无状态张量，389-408）：分别服务 eager、compile、CUDA graph 三种执行后端。

## 新人提示

- 复现顺序勿倒：warmup（学生继承 teacher 初始化）→ self-forcing → 推理；跳过 warmup 直接自强迫会因 student 未经一致性预热而崩（`docs/DISTILL.md` 同口径）。
- **勘误（源码实证）**：①`set_up_model` 91 行注释自认"不 load student weight（从 checkpointer load_path 来）"——学生初始权重路径由 checkpoint 配置而非 teacher_load_from 控制，配错会静默从头训；②`launch_self_forcing.sh:33` 强制要求 WANDB_API_KEY（缺省硬失败），不想联网须删该行并配 `wandb_mode=disabled`；③判别器注释拼写 `Distriminator`（`discriminator.py:17` 文件 docstring）。
- 调试滚动质量：开 `vis_debug`（229-230 行 dump_iter 机制）每 N 步落 `out-*.mp4`；NaN 防护见 `loss_dmd[isnan]=0`（288）。

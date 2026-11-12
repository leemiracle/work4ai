# 01 · gr00t_n1d7.py — N1.7 全模型装配与 flow matching 动作头

> 源码：`gr00t/model/gr00t_n1d7/gr00t_n1d7.py`（627 行）。本仓图谱（`.understand-anything/knowledge-graph.json`，1018 节点/1771 边）中它是连接密度最高的装配节点：上游 Qwen3Backbone 与 dit.py/embodiment_conditioned_mlp.py 全部汇于这里。

## 一、角色定位

这个文件是 VLA 模型的"总装车间"，只定义两个类：`Gr00tN1d7ActionHead`（gr00t_n1d7.py:38）——flow matching 扩散动作头；`Gr00tN1d7`（gr00t_n1d7.py:500）——继承 `PreTrainedModel` 的全模型，把 backbone（Cosmos-Reason2-2B，Qwen3-VL 架构）+ 动作头 + 数据 collator 三件套拼在一起。文件尾部 `AutoConfig.register("Gr00tN1d7", ...)` 与 `AutoModel.register(...)`（gr00t_n1d7.py:626-627）把它挂进 HuggingFace 生态，使 `from_pretrained` 直接可用。backbone 负责看和读，动作头负责"怎么做"——两者在 `Gr00tN1d7.forward` 里只通过一个 `BatchFeature`（backbone_features + 两个 mask）交接（gr00t_n1d7.py:598-599）。

## 二、内部结构

**动作头装配**（`__init__`，gr00t_n1d7.py:43-119）：
- 降噪骨干按 `config.use_alternate_vl_dit` 二选一：`AlternateVLDiT`（默认 True，configs/model/gr00t_n1d7.py:88）带 `attend_text_every_n_blocks=2`（config:89），否则退回普通 `DiT`（gr00t_n1d7.py:49-61）；`cross_attention_dim` 固定为 `backbone_embedding_dim=2048`（config:44）。
- 三个投影件全部来自 embodiment_conditioned_mlp.py：`state_encoder`（CategorySpecificMLP，输入 `max_state_dim×state_history_length`→1536，gr00t_n1d7.py:66-71）、`action_encoder`（MultiEmbodimentActionEncoder，:72-76）、`action_decoder`（hidden_size 1024→action_dim 132，:77-82；config:74-78）。
- `vlln`（backbone 特征的 LayerNorm，:84-86）与可选 `vl_self_attention`（:88-92）；`add_pos_embed` 时建 1024×1536 位置嵌入（:94-96）。
- **Beta 噪声时间采样钉死 CPU/fp32**（gr00t_n1d7.py:112-115）：上方 10 行注释（:101-111）给出完整理由——动作头可能在 `meta`/`no_init_weights` 默认设备上下文中被构造（嵌套 from_pretrained），裸 Python float 造的 Beta 会把 concentration 张量放到 meta 设备或 bf16，validate_args 下 `__init__` 直接炸，关掉校验则采样返回垃圾。显式 `device="cpu"`+`float32` 让噪声调度只依赖 config，在 SDPA/FA2/FA4 与 meta/真实设备加载间完全一致。
- `set_trainable_parameters`（gr00t_n1d7.py:121-149）用三个开关（tune_projector/tune_diffusion_model/tune_vlln）控制投影件、DiT、vlln 是否训练。

**全模型装配**（gr00t_n1d7.py:529-551）：`get_backbone_cls`（:490-497）按模型名路由——只认 "nvidia/Cosmos-Reason2" 或 "Qwen/Qwen3-VL"，其余直接 `ValueError`；collator 在 :545 才**延迟导入**（避免 model↔processing 循环导入）。

## 三、外部连接

- 上游导入：dit.py 的 `AlternateVLDiT/DiT/SelfAttentionTransformer`（:28）、embodiment_conditioned_mlp.py 两个类（:29-32）；Qwen3Backbone 经 `get_backbone_cls` 按需导入（:492-493，注释说明它依赖更新的 transformers 版本）。
- 下游消费：训练走 `Gr00tN1d7.forward`（:585-601）；推理走 `get_action`（:603-614）；部署侧 TensorRT 会 `del action_head.model` 后 monkey-patch `get_action_with_features` 换成 TRT 引擎循环（scripts/deployment/trt_model_forward.py:878-905），所以 :325 这个方法的签名是部署契约。
- `prepare_input`（:553-583）是模型与策略层的接口：若输入带 `vlm_content`，先经内置 collator 转 token（:566），注释明确这是"n_envs>1 修复"（:559）——多环境观测逐个过 collator 再合并；随后 `tree.map_structure` 按"浮点转 self.dtype、整型保设备"搬数据（:574-581）。

## 四、数据流

**训练前向**（forward，:182-286）：backbone 特征先过 `process_backbone_output`（vlln→vl_self_attention，gr00t_n1d7.py:175-180）；state 从 [B,history,dim] 摊平成 [B,1,history×dim]（:213-214）编码；训练期按 `state_dropout_prob`（config 默认 0.8，config:118）整样本置零编码状态（:220-226）。flow matching 核心四行在 :230-235：采噪声、`t=(1-Beta(1.5,1.0)样本)×0.999`（sample_time，:170-173）、`noisy_trajectory=(1-t)·noise+t·actions`、回归目标 `velocity=actions-noise`。t 连续值×1000 桶离散化（:238）后进 action_encoder，加位置嵌入（:242-245），与 state 特征拼成 sa_embs（:248）。AlternateVLDiT 分支额外传 `image_mask`（:252）；输出经 decoder 后**只取尾部 action_horizon 段**（:272-273，因为序列头部是 state token）。损失是带 mask 的 MSE：`F.mse_loss(pred,velocity)×action_mask`，再按 mask 求均值、分母加 1e-6 防零（gr00t_n1d7.py:277-278）。

**推理去噪循环**（get_action_with_features，:325-443）：初始动作=纯噪声（:349-353），`dt=1/num_inference_timesteps`（gr00t_n1d7.py:355，config 默认仅 4 步，config:106）；循环里 t 从 0 均匀走向 1（gr00t_n1d7.py:397-399），每步编码当前动作→过 DiT→解码速度→欧拉积分 `actions += dt·pred_velocity·vel_strength`（gr00t_n1d7.py:435）。**RTC 实时控制**（gr00t_n1d7.py:358-394）：输入带 action 且 options 含四个 rtc_* 键时激活——用上一动作块尾部 inpainting 替换噪声初值（:373-378），前 `rtc_frozen_steps` 步 vel_strength 置 0 冻结（:379，对应推理延迟不可回滚的已下发动作），中间过渡步用 `1-exp(-rate·t)` 归一化指数爬坡（:380-394）平滑衔接。

## 五、设计决策

1. **t=1 为数据、t=0 为噪声**的约定与常见 DDPM 相反，velocity 目标 `actions-noise` 就是 ODE 斜率，4 步欧拉即可出动作——为实时控制牺牲精度换延迟。
2. Beta(1.5,1.0) 使 `1-sample` 均值≈0.4，训练采样偏向高噪声区——模型在"最像噪声"的阶段见更多样本。
3. `set_frozen_modules_to_eval_mode`（:151-168）并在 forward 首行调用（:201）：因为 HF trainer 每个 training_step 都 `model.train()`，冻结模块必须手工恢复 eval 才能 guarantee dropout 行为。
4. 甄别一条：**RTC 机制在仓内无消费者**——全仓 grep 仅本文件出现 rtc_* 四键，`Gr00tPolicy._get_action` 调 `model.get_action(**collated_inputs)` 时不传 options（gr00t/policy/gr00t_policy.py:417），RTC 分支需 action_input 含 "action" 且 options 非空（:358-368）才触发，属留给外部机器人控制栈的接口。
5. 另一条：普通 DiT 路径的 `encoder_attention_mask` 形参实际未用（dit.py:320-326 传 None），padding token 会被交叉注意；默认 AlternateVLDiT 才真正用 mask 组合。

## 六、新人提示

- 读此文件前先读 `gr00t/configs/model/gr00t_n1d7.py`：hidden_size=1024/input_embedding_dim=1536/max_action_dim=132/action_horizon=40（config:74-78）决定了所有张量形状。
- `supports_gradient_checkpointing=True` 写在普通 `nn.Module` 上（:41）只是约定标志，真正生效靠 HF Trainer。
- 调试形状时记住 sa_embs 序列 = 1 个 state token + action_horizon 个 action token，decoder 输出切片 `pred[:, -actions.shape[1]:]`（:273）就是为此。
- 想看冻结/解冻效果，`set_trainable_parameters` 末尾会 warning "No action head trainable parameters found"（:148-149），全冻结时别慌，这是提示不是错误。

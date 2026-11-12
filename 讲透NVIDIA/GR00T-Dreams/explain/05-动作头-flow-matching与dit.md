# 05 动作头：FlowmatchingActionHead、DiT 与 vendored SigLIP

## 一、角色定位

这组文件实现 GR00T N1 的 System 1——从视觉语言状态直接回归动作轨迹的快系统。`gr00t/model/action_head/flow_matching_action_head.py` 用条件流匹配把动作生成建模成噪声到数据的向量场回归；`cross_attention_dit.py` 提供回归器骨干 DiT；`action_head/siglip/modeling_siglip.py`（1678 行）是 vendored SigLIP 全量拷贝，但服务对象不是主模型，而是 IDM 线的视觉编码器。

## 二、内部结构

**多本体投影层**：核心抽象 `CategorySpecificLinear`（flow_matching_action_head.py:65-76）——权重形状 `(num_categories, in, hidden)`，按 `embodiment_id` 索引出每本体独立 W/b 再 `torch.bmm`（:74-76），32 个本体（:167）各持私有矩阵、互不串味。`MultiEmbodimentActionEncoder`（:91-135）三级 MLP：W1 投维（:98）→ 动作嵌入与时间 τ 的正弦编码拼 2w 后 W2 压回（:130-131）→ W3；时间必须是 `(B,)` 标量广播到 T 步（:115-121）。`state_encoder`/`action_decoder` 是同款 `CategorySpecificMLP`（:195-211）。

**流匹配数学与训练**（forward，:266-320）：设噪声 $x_0\sim\mathcal N(0,I)$、数据 $x_1=a$，线性插值路径 $x_t=(1-t)x_0+t\,x_1$（:286，t=1 是纯数据）。该路径的条件速度场是常数 $\mathrm dx_t/\mathrm dt=x_1-x_0$，即 `velocity = actions - noise`（:287）。训练即噪声条件回归：模型在 $(x_t,t)$ 预测速度，损失 `mse_loss(pred, velocity) * action_mask` 按 mask 归一（:315-316），padding 维不参与。时间采样是本实现的个性：`t=(noise_s-sample)/noise_s`，`sample~Beta(1.5,1.0)`、`noise_s=0.999`（:155-159, :259-261）——Beta(1.5,1) 均值 0.6 偏大，取 1 减后 t 均值 ≈0.4，**训练刻意偏向高噪声段**。连续 t 乘 1000 入离散桶（:290）。`set_frozen_modules_to_eval_mode`（:243-257）是冻结配套：HF Trainer 每步 `model.train()`，它保证冻结子模块维持 eval 防 dropout 漏出。

**推理积分**（get_action，:322-376）：`@torch.no_grad()` 下从纯噪声起步（:334-338），N 步欧拉积分 `actions += dt * pred_velocity`（:375）。VL 嵌入循环外算一次，循环内每步只重编码动作特征（:352）——推理开销与 N 线性、大头在 DiT 前向。

**DiT**（cross_attention_dit.py:190-299）：默认 12 层、8 头×64 维、`norm_type="ada_norm"`（:196-212）。时间经 `TimestepEncoder`（:31-41）成 temb，逐层 `AdaLayerNorm` 注入（:44-67，SiLU→Linear→chunk 出 scale/shift）。**最反直觉处**：`BasicTransformerBlock`（:70-187）名字带 cross_attention 却**没有 attn2**——注释 "# Define 3 blocks"（:117）与编号跳到 "3. Feed-forward"（:135）是 diffusers 模板裁剪的化石。交叉条件化靠唯一 `attn1`：diffusers `Attention` 在 `encoder_hidden_states=None` 时自注意力、传入时变交叉（:124-133）。拼接方式：state+action 嵌成为 hidden_states、VL 嵌成为 encoder_hidden_states（:300-309），同层注意力先在状态-动作内自混合、再以 VL 为 K/V 交叉读取。`interleave_self_attention` 在奇数层丢掉条件转纯自注意力（:274-281，N1.5 特性）。输出 adaLN 式：`proj_out_1(temb)` chunk 出最终 scale/shift（:293-295）。

**SigLIP 副本**：头部 Google/HF 双版权（modeling_siglip.py:2）与多处 "# Copied from transformers.models.clip..." 注释（:176/:403/:886）标明血统。注意力三级继承树：`SiglipAttention`（:400，手写 QK^T、fp32 softmax :464-466）→ `SiglipFlashAttention2`（:484）→ `SiglipSdpaAttention`（:571，`output_attentions=True` 回退基类 :587-597）。工厂 `SIGLIP_ATTENTION_CLASSES`（:643-647）由 `SiglipEncoderLayer` 按 `config._attn_implementation` 查表（:670）。JAX 风格初始化（:116-172）、位置插值（:300-338）、probe 注意力池化（:1189-1212）全保留。

## 三、外部连接

动作头上游是 `GR00T_N1`（backbone_features 经 BatchFeature 传入，:271-275），推理时被 `gr00t_n1.py:178` 的 `get_action` 调用；`SelfAttentionTransformer`（cross_attention_dit.py:302）是 IDM 动作头骨干。SigLIP 副本的消费关系要**甄别**：主模型 Eagle2 backbone 用的是 **transformers 上游**——`modeling_eagle_chat.py:26` `from transformers.models.siglip.modeling_siglip import SiglipVisionModel`；本仓副本的消费者全在 IDM 线：`transforms_idm.py:26` import 本仓 `SiglipProcessor`（:84 加载 `google/siglip2-large-patch16-256`）、`flow_matching_action_head_idm.py:193-195` instantiate 后直接 `del text_model` 只留视觉塔。暗坑：`siglip/__init__.py` 注册了 `image_processing_siglip` 子模块但目录里**没有**该文件——直接 `import SiglipImageProcessor` 会 ImportError，现行消费路径恰好绕开。

## 四、数据流

训练一条 batch：`action_input`（state/action/embodiment_id/action_mask）+ VL 嵌入进入 forward → 采 noise 与 t → 构造 noisy 与 velocity（:281-287）→ action_encoder 编码 + 可学习位置嵌入（:294-297）→ 拼 `sa_embs`（:300）→ DiT 12 层（AdaLN→attn1 自/交叉→FFN 残差）→ decoder 回动作维、切轨迹段（:311）→ masked MSE。推理对称反向：噪声起步 N 次（编码→DiT→解码→Euler）出 `action_pred`（:376）。

## 五、设计决策

1. **线性 OT 路径+常数条件速度**是流匹配最简实例：避开 DDPM 噪声调度表，训练目标恒为 $x_1-x_0$。
2. **本体独立投影+共享 DiT**：量纲差异隔离在 CategorySpecific 层，DiT 学共享运动先验——比 embodiment 嵌入方案参数多一点但无串扰。
3. **单注意力复用**（砍 attn2）：省一半注意力开销，代价是自混合与 VL 条件读取在同层纠缠；interleave 开关提供折中。
4. **时间离散桶 1000**：训练与推理（:346）都量化到同一网格，与扩散生态 API 习惯对齐。
5. **SigLIP vendored 锁版本**：IDM 线免疫上游 transformers API 漂移，代价是与 eagle 线并存两份 SigLIP、不同源演进。

## 六、新人提示

- 全部数学就两行：`noisy=(1-t)*noise+t*actions; velocity=actions-noise`（:286-287）。想改非线性路径须同步改 velocity 与积分式，:286/:287/:375 三处缺一不可。
- **encoder_attention_mask 全链未生效**：forward 把 VL mask 传给 DiT（:302-307），但 DiT 循环显式传 `encoder_attention_mask=None`（:287），block 内 attn1 的 mask 参数也被注释（:171）——VL 嵌入若有 padding，当前是平均注意而非屏蔽；get_action 干脆不传（:365-369）。
- `num_inference_timesteps` 来自 config（:163-166），权重兼容任意 N，调 N 即换速度/质量档。
- LoRA 扫描的 to_q/to_v 同样命中 DiT 的 diffusers Attention，DiT 也被 LoRA 化。
- 查 SigLIP 行为先分线：Eagle backbone 查 transformers 上游，IDM 才查本仓副本——两份 95% 相同但不同步。

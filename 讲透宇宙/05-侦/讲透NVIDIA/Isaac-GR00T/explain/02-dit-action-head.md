# 02 · dit.py + embodiment_conditioned_mlp.py — DiT 降噪骨干与多本体投影层

> 源码：`gr00t/model/modules/dit.py`（483 行）+ `gr00t/model/modules/embodiment_conditioned_mlp.py`（238 行）。二者是被 01 篇动作头消费的"发动机+变速箱"：DiT 做时序去噪，embodiment 层做按机器人型号查表的输入/输出投影。

## 一、角色定位

dit.py 提供 flow matching 的降噪网络：`DiT`（dit.py:222）、其子类 `AlternateVLDiT`（dit.py:339，图文 token 分流交叉注意）、`SelfAttentionTransformer`（dit.py:417，给 backbone 特征做可选后处理），以及积木 `TimestepEncoder`/`AdaLayerNorm`/`BasicTransformerBlock`（dit.py:61/74/100）。它基于 diffusers 的 `ModelMixin+ConfigMixin`（dit.py:20,222），可被 diffusers 的 save/load 机制管理。embodiment_conditioned_mlp.py 是 N1 系列的"多本体签名"：`CategorySpecificLinear/CategorySpecificMLP`（embodiment_conditioned_mlp.py:59/143）给每个机器人型号一套独立权重，`MultiEmbodimentActionEncoder`（:177）把带噪动作+扩散时间步编进隐空间。

## 二、内部结构

**平台补丁三件套**（dit.py:29-58）：`_is_spark_sm121` 用 `torch.cuda.get_device_capability()==(12,1)` 识别 DGX Spark（dit.py:29-34）；`_should_force_math_sdpa` 支持环境变量 `GR00T_DIT_SDPA_MODE=math/default` 覆盖（dit.py:37-44）；`_sdpa_context` 返回 `torch.backends.cuda.sdp_kernel` 只开 math 后端的上下文——注释明说 Spark 的 mem-efficient SDPA kernel dispatch "noisy/broken"（dit.py:47-58）。该上下文包裹每个 block 的注意力调用（dit.py:197-204）。

**DiT 主体**：构造器 `@register_to_config`（dit.py:225）默认 12 层 8 头（dit.py:230-231），但 N1.7 实际由 `diffusion_model_cfg` 注入 16 层/32 头/头维 48（configs/model/gr00t_n1d7.py:92-102），inner_dim=32×48=1536 恰好等于 input_embedding_dim（config:78）。`interleave_self_attention=True` 时奇数层走自注意、偶数层走交叉注意（构造侧 dit.py:258-261，前向侧 dit.py:310-326）；输出层是 adaLN 风格 `proj_out_1(silu(temb))` 切 shift/scale 再仿射（dit.py:330-332），`proj_out_2` 降到 output_dim=1024=hidden_size（dit.py:286,config:92-102）。

**AlternateVLDiT**：新增唯一参数 `attend_text_every_n_blocks=2`（dit.py:345）；forward 断言必须有 `image_mask`（dit.py:359）且必须开 interleave（dit.py:376）；用 `image_mask & backbone_attention_mask` / `(~image_mask) & backbone_attention_mask` 造两套交叉注意掩码（dit.py:372-373）；偶数层里 `idx % (2×n)==0` 注意文本 token，其余注意图像 token（dit.py:391-396）——16 层展开即 0/4/8/12 看文本、2/6/10/14 看图像、奇数层全自注意。

**embodiment 层**：`CategorySpecificLinear` 权重是三维张量 `[num_categories, input_dim, hidden_dim]`（0.02×randn 初始化，embodiment_conditioned_mlp.py:66-67），forward 按批次内各样本的 `cat_ids` 索引取行再 `torch.bmm`（:77-79）——一个 batch 可混装不同机器人。`MultiEmbodimentActionEncoder` 三段式（:186-188 注释标明形状）：W1 把动作 d→w（:214），扩散时间步 τ 从 (B,) 复制成 (B,T)（:205-211，形状不符直接 ValueError），经 `SinusoidalPositionalEncoding`（:26-56）得 tau_emb 后与动作嵌入拼接，W2 降维加 swish（:220-221），W3 收尾（:224）。注意 tau_emb 沿 T 全同——它编码的是**噪声水平**，动作步的位置信息由 DiT 内 sinusoidal 位置嵌入或外层 position_embedding 负责。

## 三、外部连接

- 唯一仓内消费者是 gr00t_n1d7.py:28-32 的导入；DiT/AlternateVLDiT 的 `cross_attention_dim` 由调用方传 `backbone_embedding_dim=2048`（gr00t_n1d7.py:52-59）。
- 依赖 diffusers 的 `Attention/FeedForward/Timesteps/TimestepEmbedding/SinusoidalPositionalEmbedding`（dit.py:20-23）——attention 后端选择（SDPA/FA）由 diffusers Attention 内部决定，这正是 Spark 补丁要包在 block 级的原因。
- TRT 部署只替换 `action_head.model`（即这里的 DiT 实例），encoder/decoder 留在 PyTorch（scripts/deployment/trt_model_forward.py:881-882）。
- 图谱佐证：两文件均只被 gr00t_n1d7.py 引用，属叶子模块，改动不影响仓内其他文件。

## 四、数据流

训练/推理共用同一条 DiT 通路：`hidden_states`=sa_embs（B, 1+T, 1536）、`encoder_hidden_states`=backbone 特征（B, S, 2048）、`timestep`=(B,) 离散桶值。TimestepEncoder 先把标量时间步经 256 维正弦投影+两层 MLP 变 temb（dit.py:64-71），每个 BasicTransformerBlock 里：norm1 用 temb 调制（ada_norm 分支 dit.py:189-192）→ diffusers Attention 以 encoder_hidden_states 是否为 None 切换自/交叉注意（dit.py:197-204）→ 残差（:208）→ norm3+FeedForward+残差（:213-216）。`return_all_hidden_states=True` 时返回逐层隐状态列表（dit.py:333-334），训练侧目前只取最终输出（gr00t_n1d7.py:264-270 取第一个返回值）。embodiment 侧数据流在 01 篇已述：state→CategorySpecificMLP、noisy_action+τ→MultiEmbodimentActionEncoder、DiT 输出→CategorySpecificMLP 解码。

## 五、设计决策

1. **图文分流而非混合交叉注意**：AlternateVLDiT 把视觉 token（长序列、空间信息）与文本 token（短、稀疏）分开供注意，文本每 n=2 个交叉块才轮到一次——语言指令是低频条件，图像是高频信号，硬性交替避免了文本 token 被海量图像 token 淹没。
2. **一个 Attention 类两用**（dit.py:154-163）：BasicTransformerBlock 只建一个 attn1，交叉/自注意靠传不传 encoder_hidden_states 切换；注释 "Define 3 blocks"、"1. Self-Attn"、"3. Feed-forward"（dit.py:147-165）是旧版独立 cross-attn 块（编号 2）被删后的历史遗物。
3. 甄别一条：**普通 DiT 的 `encoder_attention_mask` 形参是摆设**——forward 签名收了它（dit.py:297），但喂给 block 时写死 None（dit.py:320-326），padding 的 VL token 会被注意；只有 AlternateVLDiT 用 image_mask 组合真正屏蔽。默认配置 use_alternate_vl_dit=True 规避了此坑。
4. `TimestepEncoder` 的 `compute_dtype` 参数传入即弃——forward 用 `next(self.parameters()).dtype` 自适应（dit.py:68），显式参数形同虚设，算代码债。
5. **expand_action_dimension 的平铺初始化**（embodiment_conditioned_mlp.py:81-129）：新本体动作维超旧维时按整块复制旧权重（含余数切片 :103-107），保行为连续；且显式区分 input/output 维（CategorySpecificMLP 只扩 layer2 输出 :163-174，ActionEncoder 只扩 W1 输入 :227-238），比盲目两维同扩安全。
6. 用 bmm 而非 grouped Conv1d/embedding 实现 per-category 权重：语义直白、checkpoint 兼容好，代价是显存随类别数线性涨（默认 32 档，configs/model/gr00t_n1d7.py:123）。

## 六、新人提示

- DiT 构造完会 print 参数量（dit.py:287-290），首次实例化看到裸 print 属正常。
- 想关 Spark 补丁做 A/B 测试：`export GR00T_DIT_SDPA_MODE=default`（dit.py:39-42）即可，不用改码。
- `interleave_self_attention` 在 AlternateVLDiT 是硬前提（dit.py:376 断言），配置里忘开会直接 assert 崩，错误信息就是字面量 "Interleave self attention must be enabled"。
- CategorySpecificLinear 的 b 在构造时全零（embodiment_conditioned_mlp.py:67），若微调发现某本体输出恒偏，先查该 category 的 W 是否被正确加载而非怀疑 b。
- 改 `attend_text_every_n_blocks` 不动权重结构但改变图文注意轮换语义，属行为级超参，微调慎动。

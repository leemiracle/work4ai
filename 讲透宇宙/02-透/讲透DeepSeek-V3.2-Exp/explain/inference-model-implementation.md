# DeepSeek-V3.2-Exp inference/ 精讲：DSA Indexer、non-interleaved RoPE 与 TileLang FP8

> 对象：`deepseek-ai/DeepSeek-V3.2-Exp` 仓 `inference/`（model.py 922 行 + kernel.py 274 + generate.py/convert.py/config_671B_v3.2.json）。全部 `文件:行号` 锚点从源码核实。姊妹篇：V3 参考实现精讲见 `../../../../讲透宇宙/02-透/讲透DeepSeek-V3//explain/`。

## ① 文件定位与角色：DSA 的首个官方参考实现

V3.2-Exp 权重仓的 `inference/` 是 DeepSeek Sparse Attention（DSA）的第一个官方参考实现。model.py 922 行（V3 是 808，增量几乎全是 Indexer 与精度改造）；kernel.py 274 行从 Triton 换血 TileLang；fp8_cast_bf16.py 消失（不再提供 BF16 权重转换）。依赖同样换血：`tilelang==0.1.6`+`fast_hadamard_transform`（Hadamard 旋转用，model.py:430）取代 V3 的 triton，torch 不钉版本（requirements.txt）。

README 把 kernel 生态分三层并写明本仓位置（"Open-Source Kernels" 节）：本 demo 的 TileLang 精简实现 → 研究友好完整版在 tile-ai/tilelang/examples/deepseek_v32 → 高性能版 indexer logit kernel 在 DeepGEMM PR#200（含 paged）、稀疏注意力 kernel 在 FlashMLA PR#98。config 与 V3 逐键对比只有四个新增（config_671B_v3.2.json:22-25）：`scale_fmt: ue8m0` 与 `index_n_heads: 64 / index_head_dim: 128 / index_topk: 2048`——61 层/128 头/256+1 专家照旧，**架构层面唯一的新东西是每层 MLA 挂了一个 Indexer**（model.py:539）。convert.py 映射表新增 4 键 `wq_b/wk/k_norm/weights_proj`（convert.py:30-33），indexer 的 wq_b 不 MP 分片（对应 model.py:445 用普通 Linear）。

## ② MLA 前向的代码路径：按 mask 分支、residual 融合与 FP8 KV 精度模拟

V3 的 `attn_impl` 开关消失（V3 model.py:17 → V3.2 model.py:13-15），实现选择改为**运行时按 mask 分支**：`mask is not None` 走 MHA prefill（model.py:574-589），None 走 MQA absorb decode（model.py:590-606）；mask 在 Transformer.forward 里 seqlen>1 才构造（model.py:903）——prefill 用完整 MHA（展开 k/v，model.py:575-580），decode 走 latent 吸收。`q_lora_rank==0` 分支被删（V3 model.py:424-425 vs V3.2 model.py:526-528），因为 **indexer 复用 query latent qr**（model.py:560-561 产出、460 消费），q_lora_rank 必须存在。

absorb 数值本体与 V3 相同：q_nope 右乘 W_k^T 吸收进 latent 空间（model.py:595），打分 = q̃·c_KV + q_pe·k_pe（model.py:596-597），输出 latent 加权和再上投影（model.py:605-606）。三处演进值得点名：其一，**FP8 KV cache 精度模拟**（model.py:569-571，注释 "we use fp8 kv cache in actual deployment, so here we simulate the precision"）——latent 先 act_quant 再乘回 scale 存 bf16，demo 连部署精度差都复刻。其二，wkv_b 反量化结果缓存 `self.dequant_wkv_b`（model.py:543, 591-593），修掉 V3 每步重解量化（V3 model.py:481）。其三，**残差流重构**：RMSNorm 增加 residual 入参、内部 fp32 累加（model.py:286-306），Block 全程携带 (x, residual)（model.py:844-851），收尾 norm(h, residual)（model.py:907）——V3 是裸 `x = x + attn(...)`（V3 model.py:733），这是 vLLM fused-add-RMSNorm 式的数值布局；lm_head 参数另存 fp32 保 logits 精度（model.py:885-886, 908）。

## ③ MoE 块：路由语义照旧，全链 fp32 化

路由逻辑与 V3 逐行同构：sigmoid 打分（model.py:691）、**bias 硬编码 `dim==7168`**（model.py:675）、bias 只影响 top-k 选择而权重取自 original_scores（model.py:693-695, 705）、分组 8→4 再 top-8（model.py:695-704）、sigmoid 归一后乘 route_scale=2.5（model.py:706-708）。变化全在数值精度：Gate 输入先升 fp32 `linear(x.float(), self.weight.float())`（model.py:687；V3 是 bf16 输入+softmax 处强制 fp32，V3 model.py:577-578），返回权重不再 type_as(x)（model.py:709 vs V3 model.py:598）保持 fp32 进 MoE；Expert/MLP 的 SwiGLU 中间激活显式 fp32（model.py:744, 643）；MoE 累加器显式 fp32（model.py:793）；共享专家改 reduce_output=False（model.py:778）从而 `y += z` 后只做一次 all_reduce（model.py:801-803；V3 先 all_reduce 再加 z）。意图明确：DSA 是 FP8 继续训练的产物，参考实现把所有 reduction/非线性边界升 fp32 贴近训练数值。

## ④ FP8 路径：Triton→TileLang、ue8m0 位操作与纯 torch 反量化

`linear()` 分派改按 dtype 判断（model.py:159-160）并 `assert bias is None`（model.py:157）——V3.2 全模型无 bias 项。`act_quant`（kernel.py:36-111）TileLang JIT 按 (N, round_scale) 编译：blk_m=32、group 128（kernel.py:44-46），round_scale 仅当 scale_fmt 存在时启用（kernel.py:109），用 IEEE754 位操作实现快速 ceil-log2/pow2（kernel.py:20-33, 71-74）——与 V3 Triton 版 2^ceil(log2 s)（V3 kernel.py:29-31）数学相同，但把 exp2/log2 换成指数位重解读。config 的 `scale_fmt: ue8m0` 由此端到端生效。`fp8_gemm`（kernel.py:114-196）scale 布局与 V3 一致（A per-(行, K/128)、B per-(128 行块, K/128)，kernel.py:129-130），但 tiling 固定 32×128×128、4 级流水（kernel.py:118-122, 149）加 L2 swizzle（kernel.py:144）与 "2xAcc" fp32 提升（kernel.py:160-163）——V3 是 36 配置 autotune（V3 kernel.py:113-118），此处单配置手工调优。`weight_dequant` 降级为纯 torch reshape（model.py:490-495）——decode 吸收只在首步用一次（model.py:591）。

## ⑤ V3.2 独有：DSA Indexer 与 NSA kernel 调用

**Indexer 结构**（model.py:435-487）逐件对应论文公式 I_{t,s}=Σ_j w_{t,j}·ReLU(q_{t,j}·k_s)：q 路 `wq_b: Linear(1536→64×128)`（model.py:445）吃 query latent qr（model.py:460），前 64 维过 non-interleaved RoPE（model.py:462-464）；k 路 `wk: Linear(7168→128)`（model.py:446）+ **LayerNorm**（model.py:447，非 RMSNorm），每 token 一把共享 key（MQA 式）；w_{t,j} 由 `weights_proj: Linear(7168→64)` 产出（model.py:449；checkpoint 存 bf16、参数存 fp32，448 行注释）。打分前 q/k 过 `rotate_activation`：fast_hadamard_transform 正交旋转保内积、摊匀 FP8 量化误差（model.py:428-432, 472-473），再 act_quant（model.py:474-475）；k 缓存本身就是 FP8——`k_cache float8_e4m3fn`+每 token 一个 scale（model.py:453-454）。

**scale 折叠**（model.py:478-479）：`weights_proj(x)·n_heads^-0.5`、q_scale、softmax_scale 全部折进传给 kernel 的逐头 scale——论文里 w_{t,j} 的显式乘加在实现中消失。数学严格：`fp8_index` kernel（kernel.py:199-251，TileLang 双级块 512×128）先对 FP8 点积 relu、乘 q_s（含 s_q·w）、头求和、末乘 k_s（kernel.py:240-247）；因 s_q·s_k>0 可穿 relu，整条 ≡ w·relu(q·k)，且 w 在 relu 后乘、符号任意。

**top-k 与跨 rank 一致性**：`topk(min(index_topk, end_pos))`（model.py:483，短序列退化为全量）；`dist.broadcast`+`assert` 强校验各 rank 选集一致（model.py:484-486）——wq_b 不分片但 fp8_index 各 rank 只算本地 KV 段，broadcast 保全局 top-k 一致：稀疏路径对并行一致性敏感的实证。

**non-interleaved RoPE 勘误**（README Update 2025.11.17 原文："the input tensor to RoPE in the indexer module requires a non-interleaved layout, whereas RoPE in the MLA module expects an interleaved layout"）：`apply_rotary_emb` 新增 interleaved 参数（model.py:405）——False 时先 `view(...,2,-1).transpose` 把前后半维配成复数对（model.py:418-419）、输出再隔行拆回（model.py:423-424）；Indexer 两处调用带注释 `# rope in indexer is not interleaved`（model.py:463, 469），MLA 的 q_pe/k_pe 则用默认 interleaved（model.py:564, 568）。同一层内两种 RoPE 配对并存、权重不可互换——修复前的 demo 把 indexer 写成 interleaved 导致性能退化。

**关键勘误（论文/README vs 代码）**：DSA 号称把注意力复杂度降到 O(L·k)，但这份 model.py 的"稀疏"是**数值语义**而非计算语义——prefill（model.py:582-586）与 decode（model.py:599-602）都是先算全量 scores，再用 `scatter_(-1, topk_indices, 0)` 的 -inf/0 加性 mask 盖掉非 top-2048 位置；demo 计算复杂度仍是 O(L²)，真正 gather top-k KV 的稀疏 kernel 在 FlashMLA PR#98，不在本仓；`k_cache[...].contiguous()`（model.py:480）每步拷整段前缀同理。

## ⑥ 与 vLLM/SGLang 等生产实现的关系

README 部署节只给两条生产路径：SGLang（docker lmsysorg/sglang:dsv32 系列，`--enable-dp-attention`）与 vLLM（"day-0 support"，指向 docs.vllm.ai 的 DeepSeek-V3_2-Exp recipe）；demo 与生产的分工由 "Open-Source Kernels" 三层结构写明。参考实现为引擎立了三条契约：①indexer top-k 跨 rank 一致性（model.py:484-486）——引擎里 indexer 与主注意力必须同置或同选集；②FP8 KV cache 精度（model.py:569-571）——官方明示部署侧 KV 是 FP8；③fp8_index 的 q_s 折叠接口（model.py:478-479）——逐头权重作为 scale 进 kernel 而非显式乘 logits，DeepGEMM PR#200 对齐的正是它。外围差异同理：V3 的 load 前随机权重 warmup（V3 generate.py:118）被删（generate.py:118-119 直接 load）；默认温度 0.2→0.6（generate.py:183）；批式输入改空行分段（generate.py:148）；softmax 明确 fp32（generate.py:26）。一句话：这份 922 行 model.py 是 DSA 的"可执行规格书"，vLLM/SGLang 拿它对齐数值、拿 DeepGEMM/FlashMLA 换速度。

（完）

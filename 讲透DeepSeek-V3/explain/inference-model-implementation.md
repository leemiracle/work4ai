# DeepSeek-V3 inference/ 参考实现精讲：MLA 吸收、DeepSeekMoE 路由与 blockwise FP8

> 对象：`deepseek-ai/DeepSeek-V3` 仓 `inference/`（model.py 808 行 + kernel/generate/convert/fp8_cast_bf16/config_671B.json）。全部 `文件:行号` 锚点从源码逐一核实。姊妹篇：V3.2-Exp 的 DSA/Indexer 详解见 `讲透DeepSeek-V3.2-Exp/explain/`。

## ① 文件定位与角色：权重仓里的官方参考实现

DeepSeek-V3 仓本质是 HF 权重仓，`inference/` 是官方参考实现——README 自己说透：demo 列 8 个推理方案之首且 §6.1 标题明写 "(example only)"（README.md:231, 252），后面才是 SGLang/vLLM 等生产框架（README.md:232, 235）。使命是**把架构讲清楚、数值算对**，性能交给引擎。分工：model.py 808 行承载全部架构；kernel.py 三个 Triton kernel（act_quant/weight_dequant/fp8_gemm）；generate.py 是 torchrun 交互/批式脚本；convert.py 做 HF→MP 分片；fp8_cast_bf16.py 做 FP8→BF16 权重转换（官方只发 FP8 权重，README.md:240）；configs/ 四份 JSON（16B/236B/671B/v3.1）跨 checkpoint 复用；依赖钉死版本（requirements.txt：torch==2.4.1/triton==3.0.0）。

两个静默行为值得点名：其一，convert.py:53-54 硬编码跳过 `model.layers.61`——61 层主模型之外的第 62 层是 MTP 模块权重，参考实现直接丢弃（MTP 本可做投机解码，README.md:67）。其二，并行不靠配置而靠模块级全局变量：`world_size`/`rank`（model.py:13-14）在 Transformer 构造时覆写（model.py:758-759），`block_size=128`（model.py:15）与开关 `gemm_impl`/`attn_impl`（model.py:16-17，默认 "bf16"/"absorb"）同为全局量。

## ② MLA 前向的代码路径：latent 压缩、q/k 分维与吸收后的 per-head 计算

维度参数（config_671B.json）：q_lora_rank=1536、kv_lora_rank=512、qk_nope=128、qk_rope=64、v_head_dim=128、n_heads=128。投影族（model.py:412-433）：查询侧低秩两段 `wq_a(7168→1536)→q_norm→wq_b(1536→128×192)`（model.py:427-429）；KV 侧单投影 `wkv_a(7168→512+64)`（model.py:430）一刀切出 512 维共享 latent c_KV 与 64 维解耦 k_pe——latent 压缩发生于此，再由 `kv_norm`（model.py:431）+`wkv_b(512→128×256)`（model.py:432）按需展开各头 k_nope/v。`softmax_scale=(128+64)**-0.5`（model.py:434）。

KV cache 双形态（model.py:439-444）：naive 分支缓存 per-head k/v（model.py:440-441）；absorb 分支只存 `kv_cache(512)+pe_cache(64)`（model.py:443-444）——576 维/token 对 MHA 的 40960 维/token。

forward（model.py:446-497）：q 过低秩链后 view 成 (b,s,heads,192) 并 split 出 q_nope(128)/q_pe(64)（model.py:464-466），**仅 64 维 rope 部分过 apply_rotary_emb**（model.py:467；复数式 interleaved 实现 model.py:390）；kv 同样 split [512,64]（model.py:469-470）。absorb 主干（model.py:480-495）：wkv_b 反量化后 view 成 (heads,256,512)（model.py:481-482）；q_nope 右乘 W_k^T **吸收**进 latent 空间（model.py:483）；kv_cache 写的是 norm 后 latent 本体（model.py:484）；打分两项 einsum 相加（model.py:486-487）= q̃·c_KV + q_pe·k_pe，decode 由此变成对 512 维 latent 的 MQA 式注意力；输出先在 latent 空间加权求和（model.py:494）再乘 W_v^T 上投影（model.py:495）。softmax 强制 fp32（model.py:490）。注意 **absorb 每 forward 都重新 weight_dequant wkv_b（model.py:481），零缓存**——"正确优先、性能靠边"的最直白证据（V3.2 补了缓存，姊妹篇 model.py:591-593）。

## ③ MoE 块：sigmoid+分组 top-k 路由、bias 只管选择、routed_scaling_factor 只管加权

层类型由 `layer_id < n_dense_layers(3)` 切换（model.py:716）：前 3 层稠密 MLP（SwiGLU 三矩阵，model.py:518-520, 532），后 58 层 MoE。

路由在 `Gate`（model.py:535-598）：sigmoid 打分（model.py:580）。**bias 创建条件硬编码 `self.dim == 7168`**（model.py:564）——只有 671B 挂 auxiliary-loss-free 均衡偏置（HF 的 `e_score_correction_bias`，convert.py:61 改名 bias）。语义关键两行：bias 加进 scores 只用于 top-k **选择**（model.py:582-583, 593），最终权重从加 bias 前的快照 `original_scores` gather（model.py:581, 594）——均衡偏置参与挑专家但**不进前向加权和**。分组路由（model.py:584-592）：256 专家 8 组，组打分有 bias 时 `topk(2).sum`（model.py:589）、无 bias 时 amax（model.py:587），先选 4 组置组外 -inf（model.py:590-592），再全局 top-8（model.py:593）。sigmoid 归一化（model.py:595-596）后乘 `route_scale=2.5`（model.py:597）= HF 配置的 routed_scaling_factor；共享专家不乘此系数。

`MoE.forward`（model.py:669-693）：`torch.bincount` 统计后**Python 循环逐专家** `torch.where` 捞子集（model.py:683-689）——引擎的 grouped GEMM 在这只是循环；共享专家是 inter_dim=1×2048 的普通 MLP（model.py:667）；TP 先 all_reduce 路由输出 y 再加共享 z（model.py:690-693）。

## ④ FP8 路径：blockwise 量化、per-128 缩放与 FP8→BF16 权重转换

FP8 checkpoint 每个量化矩阵旁挂 (out/128, in/128) 的 fp32 scale（model.py:184-187）；`Linear.dtype` 按 `args.dtype=="fp8"` 切 float8_e4m3fn（model.py:760）。分派在 `linear()`（model.py:131-163）：非量化权重直走 F.linear（:153-154）；量化权重+`gemm_impl=="bf16"` 时 weight_dequant 后 bf16 GEMM（:155-157）；fp8 路径激活 act_quant、权重带 scale 进 fp8_gemm（:158-163），bias 只在此分支显式相加（:161-162）。

`act_quant`（kernel.py:9-57）：128 块 amax 下钳 1e-4（kernel.py:26-27）、`s=amax/448`（kernel.py:28）；`ue8m0` 时 scale 取 2^ceil(log2 s)（kernel.py:29-31）。V3 671B 配置无 scale_fmt 键，但 kernel 已为 V3.1 的 ue8m0 权重备好路径（config_v3.1.json:22）。**此处有一处源码级发现（勘误）**：`ColumnParallelLinear.forward`（model.py:233）与 `RowParallelLinear.forward`（model.py:262）调 `linear()` 都**漏传 scale_fmt**，只有普通 `Linear.forward` 传了（model.py:205）——换 config_v3.1.json 时专家/wq_a/wkv_a 做 ue8m0 激活量化而 wq_b/wkv_b/wo/w1-w3/head 不做，同类层两种量化格式混跑；V3.2 已修复（V3.2 model.py:233, 263 显式传 self.scale_fmt）。

`fp8_gemm_kernel`（kernel.py:113-172）是训练同款 blockwise FP8 GEMM 的推理缩影：BLOCK_SIZE_K 恒 128（kernel.py:114）；A 的 scale per-(行, K/128)（kernel.py:153）、B 的 scale per-(128 行块, K/128)（kernel.py:154）；累加循环每过一个 128-K 块，`tl.dot` 结果立即乘 `a_s[:,None]*b_s[None,:]` 进 fp32 累加器（kernel.py:156-166）——逐块反量化融合进 GEMM。加载偏移 `%M/%N` 取模防越界（kernel.py:148-149），仅存储时 mask（kernel.py:171）。autotune 按 (N,K) 缓存 36 配置（kernel.py:113-118）；generate.py:118 在 load_model 前先用随机权重跑两 token 生成即为其预热。`fp8_cast_bf16.py`：跳过 `*_scale_inv`（:72-73）、FP8 权重 weight_dequant（:74-80）、索引 pop 掉 scale_inv（:98-101）、缓存 2 分片控显存（:91-94）。

## ⑤ RoPE/YaRN 与生成循环——以及这份代码"没有"什么

RoPE 只作用于每头 64 个 rope 维：`precompute_freqs_cis` 的 dim 取 `args.qk_rope_head_dim`（model.py:307）。YaRN 仅当 seqlen 超 original_seq_len 时介入：求修正维度区间+线性 ramp 混合（model.py:366-370），并叠 mscale 平方到 softmax_scale（model.py:435-437）。易忽略的事实：**config_671B.json 根本没有 yarn 与 max_seq_len 键**，16K 窗口全由 dataclass 默认值决定——max_seq_len=4096*4（model.py:56）、original_seq_len=4096（model.py:81）、rope_factor=40（model.py:83）、beta 32/1（model.py:84-85）。

生成循环（generate.py:31-78）是教学级极简：prefill 一把从 0 起跑后逐 token 前向（generate.py:60-61, 69）；prompt 段 teacher forcing 回填（:66）；采样用 Gumbel-max 等价技巧 `probs.div_(exponential_(1)).argmax`（:25-27）。

负空间盘点（对照姊妹篇 V3.2）：无 indexer/稀疏注意力；671B 配置无 scale_fmt；KV cache 纯 bf16 无精度模拟；残差流是裸 `x = x + attn(...)`（model.py:733-734）。四点在 V3.2-Exp 的 inference/ 全部改变。

## ⑥ 与 vLLM 等生产实现的关系：写给引擎作者的"语义说明书"

代码五处硬证据说明它当不了引擎：KV cache 按 max_batch×max_seq_len 整块预分配（model.py:440-444），无 PagedAttention/前缀缓存/continuous batching；MoE 逐专家 Python 循环（model.py:684-689）；absorb 每步重新反量化（model.py:481）；RowParallel 每 forward 朴素 all_reduce（model.py:263-264）；无 CUDA Graph/torch.compile/投机解码（MTP 权重被 convert.py:53-54 扔掉）。README 的部署位全部让给引擎：SGLang "recommended"（README.md:305）、vLLM FP8/BF16 张量+流水并行（README.md:235）。

反方向同样有实证：本仓 HEAD 提交即 `Merge pull request #969 from youkaichao/rmsnorm`——分支名即 vLLM 核心维护者 youkaichao，该 PR 把手写 RMSNorm 换成一行 `F.rms_norm`（model.py:294）。vLLM 侧开发者在反向维护这份参考实现，两边互为"正确语义"的镜子：vLLM 的 DeepSeek FP8 要对齐 kernel.py 的 per-128 blockwise 语义（kernel.py:153-166）与 MLA absorb 数值路径（model.py:480-495）。分工一句话：这份 808 行 model.py 定义"算什么"，vLLM/SGLang 解决"怎么算得快"。

（完）
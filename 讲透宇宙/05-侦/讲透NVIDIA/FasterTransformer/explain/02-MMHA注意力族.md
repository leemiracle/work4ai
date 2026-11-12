# 02 · MMHA 注意力内核族：单 kernel 吃下解码步自注意力

## 角色定位

MMHA（decoder_masked_multihead_attention）是自回归解码步专属注意力内核：当前 token 的 Q 对历史 K/V cache 做 masked self-attention；unfused 三精度系服务 prefill/context 整段序列，拆成 GEMM+softmax 接力；变体群（disentangled/longformer/xlnet×2/gen_relative_pos_bias）覆盖非标准注意力。

**甄别（fusion 粒度勘误）**："含 QKV 投影的 fused kernel"是误读——输入是投影已完成的 qkv_buf（`kernels/decoder_masked_multihead_attention.h:58`），GEMM 由 cublas 先做完，`DecoderSelfAttentionLayer.cc:144` 才进 MMHA。fusion 范围=bias+rotary+cache 写入+QK^T+softmax+PV+可选量化——**七件事一 kernel，不含投影**。

## 内部结构

顶层按 hidden_size_per_head switch 出 12 档特化（32~256，`kernels/decoder_masked_multihead_attention.cu:28`）；非 2 幂尺寸**不走独立 fallback kernel**，而是同模板双参数：48 档发射 `<T,48,64>`（`:33`），Dh 真实维度、Dh_MAX 静态上限，访存以 `Dh==Dh_MAX||越界` 守卫（模板 decoder_masked_multihead_attention_template.hpp，下称 template.hpp；写 K 守卫 `template.hpp:1416`）；default 仅 assert(false)（`decoder_masked_multihead_attention.cu:66`）。

12 个实例 .cu 各显式实例化 8 个 launcher（4 类型×2 参数，`decoder_masked_multihead_attention_48.cu:75`），再按 tlength 三档切换（<32→64 线程×4 threads/key、<2048→128×2、更长→256×1，`decoder_masked_multihead_attention_32.cu:50`），并以 cache_indir 非空切 HAS_BEAMS——每文件 48 个 kernel 体，拆独立编译单元并行编译（`kernels/CMakeLists.txt:162`）。kernel 本体 `template.hpp:1119`，grid=(num_heads,batch)；utils 头为工具箱。

## 外部连接

上游两个 SelfAttention 层（fp16/fp8）填 params 进 kernel；cache 池由 Gpt/Decoder 供给，beam 时 cache_indir 由 topk/penalty kernels 维护；Cross_multihead_attention_params 特化复用同 kernel 做 enc-dec 交叉注意力。unfused 系上游是 Unfused/GptContext attention 层（参数结构 MaskedSoftmaxParam `kernels/unfused_attention_kernels.h:42`）。

## 数据流

①Q/K 就地处理：向量化读入（int8_mode==2 按 qkv_scale_out[0/1] 反量化 `:1249`），加 bias/ia3/rotary；K 以 16B chunk 写入 cache `[B,H,Dh/x,L,x]`（`:1410`，x=16/sizeof(T)；注释：写不合并无妨，"写后不管"）。②V：vo==tlength%V_PER_ITER 线程组把 V+bias 写入 `[B,H,L,Dh]` 布局 v_cache（`:1857`）。③QK^T：ti 扫 [first_step,tlength]（环形 ti%memory_max_len，超长滑窗弃最老），warp 归约、乘 inv_sqrt_dh 叠 bias 入 qk_smem，**max 在线跟踪**（`:1590`）。④softmax 两遍：block 归约 max→exp+求和+归一（`:1629`）；masked token 在 exp 处置 0。⑤PV：分组扫 v_cache fma 累加+当前步 V 单独补，树形归约出 out（`:1889`）。**beam search**：bi 按 batch×beam 展开，K/V 读取时 beam_offset=cache_indir[ti]*num_heads*memory_max_len*Dh（`:1535`、V 侧 `:1731`），自父 beam 槽位间接寻址，**物理 cache 零搬运**，重排全在 indir。

## 设计决策

**按 head size 特化**：向量宽、K_PER_ITER、threads_per_value（`:1948`，=Dh_MAX*sizeof(T)/16，fp8 特化×4）全是编译期常量——Dh 定死才有 16B 对齐 LDG+寄存器展开；非 2 幂 padding 代价是 48 档约 1/4 线程空转。**fused/unfused 分界**：decode 阶段 GEMM 退化成 GEMV，单 kernel 吃掉中间往返；context 阶段 QK^T/PV 是规整 batched GEMM，拆开走 cublasLt 才划算。**量化位置**：int8 在 Q/K/V 加载点 dequant、出口乘 attention_out_scale 后 cast_to_int8（`template.hpp:1925`；同族公式 `kernels/unfused_attention_int8_kernels.cu:109`）；fp8 unfused 在 QKV transpose 时反量化到 bf16 再 GEMM/softmax（`kernels/unfused_attention_fp8_kernels.cu:132`）。

## 新人提示

1. **勘误**：fp8 融合路径是半成品——`utils/cuda_fp8_utils.h:24` 的 FP8_MHA 被注释，softmax 乘 scale²（`template.hpp:1635`）与出口 result_scale（`:1919`）都在 `#ifdef FP8_MHA` 内；不开宏时 fp8 输出分支为空 if 体而调用方照常触发（`DecoderSelfAttentionFP8Layer.cc:133`）。读 fp8 先查此宏。
2. softmax 是"smem 全量+两遍"，非 Flash 式流式；只有 max 在线跟踪。
3. assert(false) 在 NDEBUG 下被编译掉，非法 head size **静默不发射**。
4. K/V cache 布局不同（[B,H,Dh/x,L,x] vs [B,H,L,Dh]），x 随精度变（fp16=8/fp32=4）。
5. launcher 按 tlength 换 block 形态，profile 按 step 分段看。

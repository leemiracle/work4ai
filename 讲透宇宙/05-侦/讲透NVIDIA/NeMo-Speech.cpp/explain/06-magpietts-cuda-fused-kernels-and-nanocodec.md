# 06 · MagpieTTS 四 CUDA 融合内核 + NanoCodec 声码器

## 角色定位

TTS 计算深水区四件套：三个 .cu（lt_fused 1473 行、decoder_fused 874 行、cuda_sampling 880 行）+ 共享构件 chain_common.cuh（1212 行），把 MagpieTTS 每帧的 ggml 图压缩成"单 launch 持久内核"——CUDA Graph 之外的第二条图外加速路线（收益钉在头注释：每轮 ~26 内核→11 launch，magpietts_lt_fused.h:7-9）。NanoCodec（src/tts/nanocodec/model.cpp 2009 行）是 token→22kHz 声码器，走互补路线：固定形状持久 ggml 流式图。一融合一固化，兑现首音频 <10ms、60× 实时。

## 内部结构

**chain_common.cuh 共享构件**：平面 Q8 布局 ltf_q8p（magpietts_chain_common.cuh:49-56）把 ggml Q8_0 的 34 字节交错块重排成纯量矩阵——quants/scales 分离、每块 2 次 uint4 载入替代 10 次 4B，是带宽的根。常量族：LTF_THREADS=256、LTF_CHAIN_BLOCKS_PER_SM=1（:23-26——更少更肥的 block 减栅栏参与者）、LTF_CHAIN_MAX_REGS=168+__maxnreg__（:32-40，旧工具链退化 launch_bounds）——限寄存器给 NanoCodec 共驻留 SM。ltf_kernel_arch_supported 硬校验 sm_80+ 且 sm_90+ 设备须 sm_90+ 内核镜像（:59-79——老 PTX 会跑未调优兼容回退）。ltf_chain_tier 模板（:428-436）按每 warp 行数给每块容量，两档 tier_large=64 块/tier_small=48 块按 SM 数选（:439-440）。cp.async 三件 ltf_cp_async16/commit/wait_all（:694-721）——sm_90+ 刻意去掉 L2 cache_hint（:701-705 注释：CUDA 13.0 ptxas 会把带 hint 的 cp.async 错编译成非法指令）。ltf_grid_barrier（:726-748）用 red.release + ld.acquire 而非 fence+atomic，注释给出实测 ~7% 步时收益。ltf_chain_arrival_rank 到达选举（:751 起）让最后到达的块拥有尾部工作（如对刚完成 K/V 的注意力）。

**lt_fused（CFG 双 lane 的 LT 全链）**：magpietts_lt_fused_round() 按轮次 c 入队（magpietts_lt_fused.h:70）；ltf_chain_kernel（magpietts_lt_fused.cu:606）是持久主体——动态共享内存放权重 tile（超 48KB 静态限）、先 stage 首层 QKV（magpietts_lt_fused.cu:653）、轮×层循环内四相位：LN+QKV+K/V cache 写入（:666 起，round 0 现场组装输入，其余读生产者的部分 LN 统计）→ O 投影 stage → 注意力（最后完成的块做，LTF_ATTN_SPLIT warp 分摊，:699）→ FF1/FF2。magpietts_lt_fused_sampler 结构（magpietts_lt_fused.h:52-62）支持内核内采样：输出投影最后完成的块直接跑 top-k 采样写 codes/argmax。

**decoder_fused（单 launch 解码步）**：magpietts_decoder_fused.cu:16-17 头注释列相位——每层 qkv GEMV(+K/V 追加环形缓存)、自注意力 partials（flash-decoding split，:101）、交叉注意力（尾部 8 块共享 key，8×64=512 文本窗，:30-44）、FFN、终 LN 与平均对齐。环形 KV 映射在 :128-129（逻辑 key j → 物理环行，新行落在 ring_head 本身）；step 参数 magpietts_decoder_fused_step_args（magpietts_decoder_fused.h:70-83）：position/ring_head/valid_len/text_len+prior/mask（-1e30 pad）；magpietts_decoder_fused_exclusive（magpietts_decoder_fused.h:85）告知持久内核是否占满 SM；容量校验失败给出 "no persistent tier fits" 硬错（magpietts_decoder_fused.cu:724）。

**cuda_sampling（设备端采样）**：device 侧 magpietts_cuda_sampling_device.cuh 实现——MAGPIETTS_CUDA_MAX_VOCAB=4096（:11）、rng/温度/top-k 全 __device__ 内联（magpietts_cuda_sampling_device.cuh:29-91）；宿主侧 magpietts_cuda_sampling.cu 用 cub::BlockRadixSort 做 logits top-k（magpietts_cuda_sampling.cu:8、:87），配置经 magpietts_cuda_sampler_configure 上传稳定设备缓冲（magpietts_cuda_sampling.h:24-31）；零主机往返——采样结果留在设备端供链内核直接消费（magpietts_cuda_sampler_codes_device，magpietts_cuda_sampling.h:14）。序列级 CUDA 图：magpietts_cuda_sampler_sequence_begin_build/finish_build_and_launch（magpietts_cuda_sampling.h:36-46）把整条 LT 序列捕获成子图 replay，sequence key 钉结构指纹（fused vs ggml LT、内核内 vs 独立采样、CFG 对 vs 单），失配即 reset 重建。

**NanoCodec** 的 NanoCodecHParams（src/tts/nanocodec/model.h:15-32）：22.05kHz、1024 样本/帧、8 码本、levels/base/scale RVQ 分层与 up_rates 上采样。三个性能支点：①nc_pack_grouped_convs（nanocodec/model.cpp:252-262 注释+实现，:481 调用）把每残差层 G 个核尺寸分支并成一个 grouped op——2*D*G 次 launch 压成 2*D 次；②nc_stream_decode_graph（nanocodec/model.cpp:1046）持久流式图：固定 chunk_frames 形状、左上下文历史张量设备驻留图内更新（nanocodec/model.cpp:1692）；③decode_eval_stream（nanocodec/model.cpp:1661-1727）：dequantize_tokens_padded（:1469）转 latent（:1683）、上传、graph_compute（:1693-1696）、回读、require_finite_audio 非有限即清状态（:35、:1718）。

## 外部连接

调用方全在 magpietts.cpp 主循环（explain/05）：decoder_fused_step 替代 MagpieDecoder 的 ggml 图步、lt_fused_round 替代 LocalTransformerGraphBank（magpietts/lt.cpp:87）、cuda_sample 替代 CPU rng；NanoCodec 由 codec_stream_worker 驱动（magpietts.cpp:794-800）。依赖侧：chain_common 的平面 Q8 需要 ASR 侧同源的 skinny-Q8 planar 补丁（fastconformer.h:319-327 契约）；融合注意力可用性探测 magpietts_fused_cached_attention_available（magpietts/model.h:424-426——ggml_fused_attn_cached 只存在于补丁后的 CUDA 后端）。tools/nanocodec.cpp 提供 CLI 解码工具做独立验证。

## 数据流

一帧解码步（全设备）：tokens(8×int32) → decoder_fused：embedding+位置 → 各层 [QKV GEMV→环形 KV 追加→自注意力 split→交叉注意力(prior 偏置)] → 终 LN 出 hidden_cond/uncond+alignment → cuda_sampling：CFG 合并 logits→top-k→采样码本帧留设备 → lt_fused 链：hidden+上轮码→LN/QKV/attention/FF 相位（grid barrier 同步）→输出投影（可内核内采样）→write_frame 入队 → NanoCodec worker：dequantize latent→残差层→上采样→1024 样本 PCM。图序列路径下 decoder→sampler→LT 进一张 CUDA 图单 launch replay。

## 设计决策

①持久内核+grid barrier 替代多 launch：省启动开销与全局同步；代价是 tier 容量上限（寄存器/共享内存）与独占性标记。②平面 Q8 重排：量化权重布局适配 cp.async 16B 殽量，带宽换回排序成本（一次性）。③采样下沉设备：top-k→multinomial→EOS 从主机关键路径摘除，TTFA 受益。④decoder_fused 与 lt_fused 各自保留 ggml 图回退（resolve 失败/形状不配即回退），正确性优先于峰值。⑤NanoCodec 反向选择持久 ggml 图：卷积形状固定无需重建，图内历史比手写内核可维护。⑥sm_90+ 去 L2 hint 的编译器 bug 规避写成显式分支而非禁用整个路径。

## 新人提示

读代码顺序：magpietts_chain_common.cuh:1-79（常量+平面布局+架构守卫）→ magpietts_lt_fused.cu:606 的 ltf_chain_kernel 主循环（配 -DLTF_CHAIN_TIMING 的 %globaltimer 打点，magpietts_chain_common.cuh:443-460）→ decoder_fused 头 70 行相位注释 → cuda_sampling_device 的 __device__ 工具族。调试：LTF_CHAIN_TIMING 重编译看每相位栅栏延迟；NVTX（ggml_nvtx::range 全覆盖三个 .cu）配 nsys 定位；tools/nanocodec 单测声码器。坑：四件全是形状特化——hparams 变（vocab/堆叠/n_embd 超限）即静默回退 ggml 路径，性能掉了先查 tier 匹配；环形 KV 的 ring_head/valid_len 契约错一帧即整段音频错位；NanoCodec 改动必跑 tests/cpp/tts/test_nanocodec_half_snake_fusion.cpp（守护图分配器与融合的时序错配）。

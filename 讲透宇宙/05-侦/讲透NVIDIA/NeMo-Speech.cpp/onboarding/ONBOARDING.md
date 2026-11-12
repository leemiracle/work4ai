# NeMo-Speech.cpp ONBOARDING（图谱 1037 节点 @ e680fc30）

## 1. 项目定位：ggml 上的 NVIDIA 语音全家桶

NeMo-Speech.cpp 是 NVIDIA 官方的本地语音推理 C++ 运行时（README.md:11 自我声明），把 NeMo 语音模型家族——Nemotron 3.5 ASR、Sortformer 分离、Riva Translate NMT、MagpieTTS、Nemotron Labs VoiceChat——全部搬到 ggml 上原生执行，不依赖 PyTorch/ONNX。性能口径（README.md:30-40）：RTX 4090 上 160ms 分块 ASR 2.3ms/块、67× 实时；MagpieTTS 首音频 9ms、60× 实时；CPU 也实时以上。

关键结构"**一条推理底座、五条业务管线**"：src/runtime/ggml/ 是唯一张量计算层（派生自 parakeet.cpp，ggml/runtime.h:4-6），ASR/TTS/S2S 是业务编排。三线实现风格各异——ASR 走 Module 三段式协议（ggml/runtime.h:192-205）；MagpieTTS 直接持 ggml_tensor* 裸指针自建计算图（magpietts/model.h:280-299），CUDA 上用持久内核绕开 ggml 图执行；S2S 复用 llama.cpp KV 槽位主干。C ABI 边界在 include/nemo_speech/ 四头：append-only+size 前缀+尾字段容错。pipeline.cpp 全仓最大，magpietts.cpp 2173 行第二。

## 2. 构建与引擎注册：llama.cpp 补丁链 + EngineRegistry

构建：根 CMakeLists.txt 以 VERSION 为版本单一真源（CMakeLists.txt:5），30+ 个 NEMO_SPEECH_WITH_* 开关装配各子树；CMakePresets.json 预定义后端×功能组合；cmake/llama_cpp.cmake 是核心——llama.cpp 子模块永不改动，构建时把 patches/series 的 19 个补丁（16 ggml+3 llama）应用到构建目录钉版拷贝，内容哈希增量刷新+双向核对防漏。

进程级引擎所有者是 `src/core/engine_registry.h:47` 的 EngineRegistry：前端只翻译协议并借用类型化引擎；模型生命周期、warmup（engine_registry.cpp:156，默认 tts_steps=8 够建融合运行时与 codec 图）、能力上报（engine_registry.cpp:203）与跨管线组合全在这里。三个组合语义：①load_asr 发现 recognizer 内嵌 diar 模型则免费派生 Diarizer（engine_registry.cpp:53-60）；②ASR+NMT 同时加载自动组装 SpeechTranslator（engine_registry.cpp:142-153）；③并存时调 keep_skinny_q8_weights_separate()（engine_registry.cpp:16），load_tts 时调 keep_cuda_graphs_resident()（engine_registry.cpp:77）——补丁群的进程级开关（ggml/runtime.h:213-216）：前者防 skinny-Q8 重排与多流调度器竞态，后者防 CUDA 图缓存 10s 闲置逐出。

推理底座三层：GGUFLoader（ggml/runtime.h:85-138，mmap 零拷贝+按需重开）→ Module 协议（ggml/runtime.h:196-204，build_graph 必须幂等——缓存 miss 被调两次：probe 测 arena+real 建缓存）→ Session（ggml/runtime.h:352-512）。Session::run_impl（session.cpp:677）是执行中枢：per-shape 图缓存以输入哈希为 key（ggml/runtime.h:502-504）；调度器池增长按 pool_generation 整代作废（session.cpp:701-710，防 stale 放置崩溃）；单后端无状态图绕过调度器直发（session.cpp:819-848）。BackendManager（ggml/runtime.h:226）暴露 compute_mutex——同管理器的 Session 串行，独立 lane 各建管理器。

cublas_shim（kernels/cublas_shim.cu:3-20）是仓内 drop-in libcublas 替换：ggml-cuda 的非量化 GEMM（FastConformer 注意力/下采样卷积/CTC 头）走一小撮 cuBLAS 入口，而真 cuBLAS 拖进 514MB libcublasLt；shim 精确实现 ggml 导入的 13 个符号（kernels/ver_cublas.map），形状特化+WMMA tensor core fp32 累加，SONAME 钉 12/13（CMakeLists.txt:268-271），是发布归档唯一 libcublas——ggml 零修改。

## 3. ASR 链路：Recognizer 门面 + 三 runner + 双解码族

主干从 `src/asr/recognizer.h:123` 的线程安全 Recognizer 门面进入：组装 BackendManager/AsrModel/DiarModel/SileroVadModel/Postprocessor/共享 FlashlightResources（recognizer.h:173-187），对外 streaming_recognize()（每流 RecognitionStream，push/next/finish 拉取，recognizer.h:77-87 钉死 drain 循环）与离线 recognize() 双入口。

模型层 asr/model.h:48 的 AsrModel 派生 CtcModel（infer_ctc 族，asr/model.h:140）与 RnntModel；model.cpp 承载编码尾部三变体（离线根/流式 cache-aware/S2S 投影）与预测-联合两级解码。runner 三派生（runner.h）：BufferedStreamRunner（runner.h:115，非 cache-aware 缓冲窗流式，每窗 [左垫|chunk|右垫] 默认 1.92/0.16/1.92s 只解码中心块，mel 增量缓存防 96% 重叠窗重复计算，runner.h:148-153）；CacheStreamRunner（runner.h:254，逐 chunk 推进，K/V/conv 缓存设备驻留、图内更新零主机拷贝，runner.h:349-353；mel 几何由 GGUF 钉死，runner.h:298-305）；OfflineRunner（runner.h:212，整段一次编码+桶填充）。

特征前端 fe.h:63 的 MelSpectrogramExtractor 双路径同布局：GPU 缓存 cgraph、CPU 手写 radix-2 FFT，输出都 frame-major（ne[0]=n_mels，fe.h:74-76）。数值契约深：log_zero_guard 必须是 2^-24 而非直觉 1e-5（fe.h:38-41——1e-5 把静音抬高 ~5 nats）、Hann 窗 periodic/symmetric 之别、无效尾帧显式 mask（fe.h:52-56）。批处理 batching.h:31 默认关，核心约束 exact-shape 微批——只有形状完全相容的工作才合并，防 dynamic shape 触发图重捕获（docs/development/asr-batching.md）。

解码器族在 src/asr/decoders/decoder.h 17 方法契约下四实现：greedy CTC（设备端 argmax）、RNNT/TDT greedy、flashlight_decoder（570 行，详见 explain/04）、context_biasing 热词 trie。VAD 三件套：Silero VAD（每流自持递归状态、每步观测一次共享给 masker+endpointer）→ masker（静音 mel 帧置零）→ endpointer（尾静音发火一次、语音推进后重武装）。说话人分离 diar_pipeline.h 以 Sortformer（sortformer_model.h）驱动 DiarStream；后处理串 ITN（与 TTS TN 共享同一双 Sparrowhawk FAR，fst_normalizer.h）、脏话过滤与 PnC 标点（pnc_model.h）。

## 4. TTS 线：MagpieTTS 主体 + 四 CUDA 文件 + NanoCodec

Synthesizer（src/tts/synthesizer.h）组装 TN→分词→MagpieTtsRuntime→重采样。MagpieTTS 主体 20 文件：magpietts/model.h:44 的 magpietts_hparams 定义 8 码本×2016 码本，frame_stacking_factor 区分 v2602/v2607 两代 profile（magpietts/model.h:96-105 指纹推断）；MagpieModel（magpietts/model.h:260）从单 GGUF 三分部装载 encoder/decoder/local transformer 与烘焙音色；MagpieAttentionPriorState（magpietts/model.h:203）及 Longform 变体维护"注意力先验"——从交叉注意力对齐分数统计文本侧已读位置，作为后续步 softmax 偏置引导对齐。

流式主循环 stream_magpie_to_audio（magpietts.cpp:1130）：token 分 chunk → 逐帧解码器步（CFG 双 lane，forbid_eos 直到 min_generated_frames，magpietts.cpp:1626）→ LT → 采样 → EOS lane 判定（magpietts.cpp:1885-1924）→ 码本帧推给后台 codec_stream_worker（magpietts.cpp:793）。主线程首帧后 wait_first_audio（magpietts.cpp:877，防占满 GPU 的解码步推迟首音频）。长文本 chunk_prefetch 旁路线程（magpietts.cpp:1305-1397）：chunk k 生成时并行预跑 k+1 的编码器/cross-KV，历史长度投机+边界校验回退。EOS 帧是硬编码 8 码本 token 串（magpietts.cpp:886）。

四 CUDA 文件把 ggml 图压成单 launch 持久内核：magpietts_lt_fused.cu（1473 行，~26 内核→11 launch）、magpietts_decoder_fused.cu（874 行，每 lane 环形缓冲 KV + 交叉注意力 log-prior 偏置）、magpietts_cuda_sampling.cu（880 行，cub 排序 top-k 零主机往返）、magpietts_chain_common.cuh（1212 行共享构件：平面 Q8 重排——34 字节交错块压成纯量矩阵、2 次 uint4 载入替代 10 次 4B；cp.async；grid barrier 快 ~7%；__maxnreg__ 168 换 NanoCodec 共驻）。tier（64/48 块）按 SM 数选择（magpietts_chain_common.cuh:439-440），sm_80+ 硬校验（magpietts_chain_common.cuh:59-79）。NanoCodec（src/tts/nanocodec/model.cpp 2009 行）是 token→22kHz 声码器：分组卷积权重打包 nc_pack_grouped_convs（nanocodec/model.cpp:252）、持久流式解码图 nc_stream_decode_graph（固定 chunk_frames、历史图内设备驻留，nanocodec/model.cpp:1046）、decode_eval_stream 逐帧解码（nanocodec/model.cpp:1661，非有限输出即清状态）。

## 5. S2S VoiceChat 与 NMT

S2S 线（src/s2s/，32 文件）：pipeline.cpp（全仓最大）中 S2SPipeline 持共享引擎、S2SStream 持会话状态，process_chunk 每 160ms 步进（s2s/pipeline.h:6）：LLM/TTS 双 StepBatcher、RNNT 显示与 EOU 轮替、函数调用解析。四大件：perception（音频感知）、codec（神经音频编解码器，codec.h 流式 codes→wav 解码与静音码）、llm（llama.cpp 主干，backbone.h 的 LLMBackbone 暴露 prefill/step 与槽位映射）、eartts（EarTTS 语音生成+采样器）；voicechat.h:27 的 VoiceChat 是进程级门面。NMT 线（src/nmt/）用 ctranslate2 线程池做句束翻译，langpairs 规范化 BCP-47 码；speech_translator.h:65 的 SpeechTranslator 串 ASR→NMT→可选 TTS 成语音翻译流。

## 6. 服务层与 CLI

服务层两形态：riva_server.cc 单端口宿主 Riva 兼容 gRPC（src/services/ 适配器只做协议转换，与 serve 互为独立进程）；server/http 的 cpp-httplib 服务器提供 REST/SSE 流式转写与 OpenAI Realtime 风格 S2S WebSocket（s2s_realtime.h），VoiceChat 仅走 WebSocket 是文档钉死边界（docs/server.md）。CLI 入口 app/main.cpp:212 按 argv[1] 分发 transcribe/synthesize/diarize/bench/serve/model/doctor/health：transcribe 最复杂（批/麦克风/SRT/VTT/JSON/语音翻译）；model_store.cpp（全 CLI 最大）管模型索引/SHA256/断点下载；examples/ 五个 SDK 示例+clients/ Python 客户端。

## 7. 分词器与数据资产

Magpie 分词器（tokenizer.cpp）手写 YAML 解析器加载 profile，按语言分派 native/byt5/hindi/arabic/IPA 路径；Mandarin 分词器（mandarin_tokenizer.cpp）走 cppjieba 分词 + 拼音 G2P 双表查读 + HMM 新词发音回退，数据目录编译期与安装期双路径探测（mandarin_tokenizer.cpp:20-24），同一二进制在源码树和安装前缀下都能找到四张表。注意四张中文数据表是 Git LFS 指针文件（仓内只存 sha256 oid，manifest.json 钉版）。

## 8. 陷阱与勘误（图谱工程 + 仓本身）

图谱工程侧：scanner 对 C++ include 解析近乎全盲（约 140 条 imports 全部由 worker 重扫补齐）；.cu/.cuh 的 __global__ kernel 与模板 tier 也是 tree-sitter 盲区，行号锚以人工 grep 核实为准。

仓本身的坑：①ggml 19 补丁群是运行时行为的隐式依赖——keep_cuda_graphs_resident/keep_skinny_q8_weights_separate、融合注意力算子（magpietts/model.h:424：只存在于补丁后的 CUDA 后端）、skinny-Q8 planar 布局（fastconformer.h:319-327 的 planar hook 在非 CUDA 缓冲直接拒绝装载——平面字节不是合法 block_q8_0，其他后端静默解码垃圾）——读任何 CUDA fast path 先过 patches/README.md；②shim 不 include cublas_v2.h 是 ABI 技巧（cublas_shim.cu:15-17：其函数在 nvcc 下是 __host__ __device__ 会编译失败，改裸声明+固定 ABI 枚举值）；③mandarin 数据表 LFS 指针，直接读仓内文件拿到的是指针不是词典；④ASR GGUF vocab 与 flashlight lexicon 不匹配时按丢弃率发响亮告警（flashlight_decoder.cpp:144-150）防静默 WER 退化；⑤log_zero_guard 2^-24 这类"数值考古"参数散布在 fe.h 注释里，改前端前必读；⑥MagpieTTS 与 ASR 实现风格不共享（Module 协议 vs 裸 tensor），跨线重构须谨慎。

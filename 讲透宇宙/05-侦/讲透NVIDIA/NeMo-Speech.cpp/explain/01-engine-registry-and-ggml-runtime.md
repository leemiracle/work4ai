# 01 · engine_registry + ggml runtime：引擎注册与推理底座

## 角色定位

`src/runtime/ggml/` 是全仓唯一的张量计算层（部分派生自 parakeet.cpp，ggml/runtime.h:4-6），把 GGUF 权重装载、计算图构建、多后端调度执行抽象成一套与业务无关的协议；`src/core/engine_registry.h:47` 的 EngineRegistry 则是进程级的"引擎所有者"——前端（CLI/HTTP/gRPC）只翻译协议并借用类型化引擎，模型生命周期、warmup、能力上报与跨管线组合全部收拢于此。两者合起来构成"一条推理底座、五条业务管线"的地基：ASR 全线、diar、PnC、VAD 都直接建在 Module 协议上，是理解本仓的第一站。

## 内部结构

runtime.h 是被全仓 include 的总头，五个支柱类：**GGUFLoader**（ggml/runtime.h:85-138）mmap 装载 GGUF，元数据访问器 get_u32/get_i32_array 等（ggml/runtime.h:117-124），release_file_resources() 在权重上传后释放文件句柄但保留元数据（ggml/runtime.h:92-94，后续懒建的 Session 可按需重开）。**Module 协议**（ggml/runtime.h:192-205）三段式：define_tensors 声明持久张量、build_graph 为一个输入形状建前向图、set_data 上传权重；头注释钉死 build_graph 必须幂等——缓存 miss 时运行时会调它两次（probe 测 arena + real 建缓存）。nn.h 提供八个 Module 积木（Conv1D/Conv2D/Conv2DDW/ReLU/Sequence/Linear/LayerNorm/BatchNorm1d），Conv1D 的 is_pointwise_2d 分支（nn.h:50-54）让转换器压扁的 k=1 卷积走 mul_mat 从而原生支持量化权重。**BackendManager**（ggml/runtime.h:226-262）持后端句柄，第二构造器可借用别的管线已初始化的 GPU 后端（ggml/runtime.h:229-232）；compute_mutex（ggml/runtime.h:249）使同管理器的 Session 串行。**TensorContainer**（ggml/runtime.h:264-337）管 arena 与多 buft 分配，ArenaSizes 默认 64MB 虚拟（ggml/runtime.h:267-273），set_mmap_loader 开零拷贝权重绑定（ggml/runtime.h:296），import_tensor 引入外部拥有的存储（ggml/runtime.h:306）。**Session**（ggml/runtime.h:352-512）是执行引擎：setup()（session.cpp:347-381）建 model/state 两个容器（state 容器刻意不做 bulk 分配，设备背板由每次 run 的 SessionState 供给，ggml/runtime.h:438-442 注释）；run()（session.cpp:467）以输入哈希为 key 进 run_impl（session.cpp:677）。

执行中枢 run_impl 的缓存协议：pool_generation 失配即整条作废重建（session.cpp:701-710——调度器池增长后旧放置会触发 CUDA invalid-argument）；LRU 先驱逐再分配（session.cpp:711-717）；probe 容器 64MB（session.cpp:689）跑一遍图量尺寸，fit_size 按 1.05 倍 +64KB 头寸对齐页（session.cpp:729-734）后建真缓存项；图节点数超 65536 的 80%/95% 分级告警/报错（session.cpp:66-69、757-769）；SchedResetGuard 保证任何退出路径都 reset 调度器（session.cpp:797-806，否则下次 GGML_ASSERT 直接崩进程）；fresh 项跑失败会被逐出而非缓存重试（session.cpp:811-814 事务语义）；单后端无状态图走 direct 旁路（session.cpp:819-848）。CachedRun 结构在 ggml/runtime.h:487-504（LRU 容量默认 4，set_run_cache_capacity 可调）。

EngineRegistry 侧：WarmupOptions 默认 tts_steps=8（engine_registry.h:34-40，注释说明足够建融合运行时与 codec 图）；load_asr 发现 recognizer 内嵌 diar 模型即免费派生 Diarizer（engine_registry.cpp:53-60，diar_from_asr_ 标记）；ASR+NMT 同时在场自动组装 SpeechTranslator（rebuild_compositions_locked，engine_registry.cpp:142-153）；构造时 ASR+NMT 并存触发 keep_skinny_q8_weights_separate（engine_registry.cpp:16），load_tts 触发 keep_cuda_graphs_resident（engine_registry.cpp:77）——两者是补丁群暴露的进程级开关（ggml/runtime.h:213-216）。capabilities()（engine_registry.cpp:202-234）按已加载引擎拼 asr/diarization/tts/translation/speech-translation/speech-to-speech/realtime-speech-to-speech 列表。

## 外部连接

上游：GGUF 文件（loader.cpp 的 llama_file/llama_mmap，ggml/runtime.h:62-63 前置声明）；补丁后的 ggml/llama.cpp（ggml/runtime.h:15-17 的 NEMO_SPEECH_CUDA_FAST_PATHS 门控；conv_1d 包装函数 ggml/runtime.h:67-83 修上游 batch 维混轴 bug ggml-org/llama.cpp#28738，注释声明上游修复进 pin 后可撤）。下游消费者：AsrModel 族、Sortformer、PnC、Silero VAD、FE 模块（fe.cpp 经 Session 跑 GPU mel）；EngineRegistry 的六个 load_*/getter 被 app/serve.cpp、riva_server.cc、http_server 共享。MagpieTTS 例外——它绕开 Module 协议直接用 ggml 裸 API（见 explain/05），但 BackendTensor/pinned scratch 的分配思想同源。

## 数据流

典型一次推理：模块构造期 define_tensors → Session::setup 锁 compute_mutex、建容器、set_data 上传权重、init_schedule（session.cpp:78-92，重建即清缓存）→ 每次调用 run(inputs, outputs, state)：哈希输入（session.cpp:139-176）→ 命中缓存则绑定 SessionState（bind_state，ggml/runtime.h:451）、上传输入（异步 tensor_set_async，session.cpp:513-515）、执行（直发或调度器）、回读输出（DeviceTensor 可免同步，ggml/runtime.h:407-408）。流式状态（cache-aware K/V）走 create_state_tensor_* 声明（ggml/runtime.h:418-422）+ make_session_state（ggml/runtime.h:425）每流一份，collect_state_views（ggml/runtime.h:454）收集需每次重绑的视图。

## 设计决策

①probe-then-fit 两段建图换确定性：幂等 build_graph 是协议级硬约束，而非可选优化。②调度器池代数校验（pool_generation）承认"池会变"这一现实并给出整代作废的廉价解。③compute_mutex 粗粒度串行 + 借用后端构造器：宁可牺牲并行度也避免多管线各建 CUDA context 的显存浪费。④run cache 容量默认 4 形状：流式几何有限（首块/稳态两形状），离线大形状靠驱逐腾显存。⑤warmup 进 EngineRegistry 而非各前端：首请求延迟是服务层 SLO，统一在装配期消化。

## 新人提示

读代码顺序：runtime.h 全文 → session.cpp 的 run_impl → engine_registry.cpp（10 分钟可读完）→ 挑 nn.cpp 一个积木看三段式落地。调试开关：NEMO_SPEECH_MEMSTATS 打 arena 用量（session.cpp:71-75、771-783），NEMO_SPEECH_TIMING 打分阶段耗时（session.cpp:808-847），dump_schedule（ggml/runtime.h:435）看图放置与 CPU 回退。坑：build_graph 里做任何非幂等副作用（如累加计数）都会在 probe pass 被触发一次；同一个 BackendManager 上的两个 Session 不会并行，追求并发要复制管理器。

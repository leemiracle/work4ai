# 01 · utils 底座与 GEMM 调优（cublas 三兄弟 + gemm_test 闭环）

## 角色定位

`utils/` 是全引擎最小依赖底座，allocator/Tensor/logger 被所有层引用；cublas 三兄弟（MMWrapper/INT8MMWrapper/FP8MMWrapper）是全仓唯一稠密矩阵乘出口，QKV/FFN/lm head 全经它落到 cuBLAS。algo 选错差 2-3 倍，故带 gemm_test 离线穷举把最优 algo 固化进 `gemm_config.in`，运行时查表复现——"离线测量、在线查表"是本仓性能工程骨架。

勘误：任务书所述 gemm.h 的 `_Gemm_`/`GemmIdx`/`ex_` 代理宏在源码中不存在（全仓 grep 零命中）。真实机制朴素：各 layer 直接调 `cublas_wrapper_->Gemm`（layers/FfnLayer.cc:265）；gemm.h 的 `Gemm` 类是实验性二代抽象，全仓无外部 include，实现自认抄自 wrapper（utils/gemm.cc:227）。

## 内部结构

基类核心 Gemm 双路径：FP16/BF16 默认 cublasLt（utils/cublasMMWrapper.cc:175），FP32 默认 cublasGemmEx；查表命中且 stages!=-1 时强制 Lt，用 AlgoInit+六连 ConfigSetAttribute（tile/splitK/swizzle/reduction/stages/customOption，utils/cublasMMWrapper.cc:243-261）重建离线 algo；未命中退 cublasGemmEx 取 DEFAULT（utils/cublasAlgoMap.cc:141-142）。另有运行时缓存：miss 时 findBestAlgo 各跑 11 遍取排序第 6 名（中位数抗抖，utils/cublasMMWrapper.cc:886）。

INT8 子类服务 VOLTA/Turing IMMA：激活/输出 COL32、权重按算力选 COL32_2R_4R4/COL4_4R2_8C。勘误：它调 cublasLtMatmul 而非 cublasGemmEx（utils/cublasINT8MMWrapper.cc:230）；表未命中写死经验值 algoId=7/6、tile=20（utils/cublasINT8MMWrapper.cc:198-226）而非退 DEFAULT。基类另有新式 Int8Gemm（走 findBestAlgo，per-column scaling 用 ALPHA_DEVICE_VECTOR_BETA_HOST 指针模式，utils/cublasMMWrapper.cc:1017-1019）。

FP8 子类只依赖 cublasLt。勘误：scale 非 alpha/beta 标量，而是把 device 指针挂到 `CUBLASLT_MATMUL_DESC_A/B_SCALE_POINTER`（utils/cublasFP8MMWrapper.cu:174-177），且 devAscalePtr=kernel_scale、devBscalePtr=input_scale（utils/cublasFP8MMWrapper.cu:141-142）——cublas 视角 A 是转置权重，命名易看反。

## 外部连接

serving 入口 `new cublasAlgoMap("gemm_config.in")`（triton_backend/multi_gpu_gpt/ParallelGptTritonModel.cc:328）→ wrapper → 模型 → 各层。algo map 键为 {batch_count,m,n,k,data_type}。基础设施：IAllocator 三后端、Tensor 裸指针视图、logger 单例、nccl/mpi_utils 张量并行；gemm_test 九个 *_gemm_func 一一对应各模型及 INT8 变体。

## 数据流

离线：generate_*_gemm_config 枚举模型全部 GEMM 形状（encoder 七个，utils/gemm_test/encoder_gemm_func.cc:85-124），FP16/BF16 再调 LtHgemmCustomFind：AlgoGetIds 取前 100 个 algoId（utils/gemm_test/gemm_func.cc:417），逐 id 穷举 tile/stages/swizzle/splitK 等组合（上限 5000），各 100 遍实测取最优写盘；产物为空格分隔文本（勘误：非 json，GEMM_CONFIG="gemm_config.in"，utils/cublasAlgoMap.h:30），行格式由 printPerfStructure 决定。

关键对应（勘误重点）：写盘列序 batchCount,n,m,k（表头自证，utils/gemm_test/encoder_gemm_func.cc:178）；读盘 fscanf 却存 &n2,&m2（utils/cublasAlgoMap.cc:73-76）；运行时又用 {n,m} 反交换查（utils/cublasAlgoMap.cc:128）。两次交换恰好抵消——测试侧 m/n 是模型行主序（cublasGemmEx 传 n,m,k，utils/gemm_test/encoder_gemm_func.cc:218-236），层侧则 m=输出特征、n=tokens（layers/FfnLayer.cc:265-275）。不理清这条三重换位，读配置必被绕晕。

## 设计决策

①文本格式+fscanf：零依赖可 diff，滚动窗口只留最近 20 组形状。②stages==-1 兼作"非 Lt 记录"信号，运行时据此降级（utils/cublasMMWrapper.cc:186-192）。③全类共用一把 mutex：多流瓶颈亦是正确性底线。④reMalloc 三态（utils/allocator.h:82-101）：REUSE 原地复用，INCREASE 必 free+malloc，DECREASE 仅 CUDA≥11.2 mempool 下真释放（utils/allocator.h:88-94），池 threshold 拉满防缩池、free 后流同步防踩内存。⑤FP8 查表键序 (n,m) 与基类相反，改动须双向核对。

## 新人提示

读码顺序：cublasAlgoMap.h → wrapper 的 Gemm → 任一 *_gemm_func.cc → FP8/INT8。缺 gemm_config.in 只打 WARNING 不报错（utils/cublasAlgoMap.cc:46），静默走 DEFAULT，性能腰斩无提示；新增形状必须重跑 gemm_test。algoId 语义随 cuBLAS 版本漂移（11.11 前后多出 inner_shape/cluster 字段，utils/cublasAlgoMap.h:40-44）。在线调优可抄"11 次取中位数"模式，抗噪优于取 min。

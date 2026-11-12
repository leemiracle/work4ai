# MatX FFT：cuFFT / cuFFTDx / FFTW 三实现与 plan 缓存

## 一、角色定位

FFT 是 MatX 中后端选择最丰富的变换：`transforms/fft/` 下四文件（fft_common/fft_cuda/fft_cufftdx/fft_fftw）+ 立即层入口 transforms.h + 惰性门面 operators/fft.h（FFTOp :59、FFT2Op :772）。用户只写 `fft(x)` / `ifft(x)` / `fft2(x)`，库按执行域与张量类型选路径：device 张量默认走 cuFFT 库调用（fft_cuda.h），JIT 融合路径可改用 cuFFTDx 设备端单 block FFT（fft_cufftdx.h），host 张量在 `MATX_EN_X86_FFTW` 下走 FFTW（fft_fftw.h:47 编译门控）。三个实现的公共语义（C2C/R2C/C2R 推导、batch 维计算、归一化约定）沉淀在 fft_common.h。

## 二、内部结构

### 2.1 惰性门面：类型推导先行

operators/fft.h 的入口族 `fft(a, fft_size, norm)`（:542）、轴向重载（:592）、`ifft`（:679/:705）、`fft2`（:1194/:1216）第一步都调 `ComplexInType<OpA>()`（:543）——fft_common.h:143-175 的 `DeduceFFTTransformType` 按输入输出实/复推导 C2C/R2C/C2R。FFTOp 挂 `matx_transform_op` 与 `can_alias` 标记（fft.h:84/:86），允许输入输出同内存原地变换——这是 FFT 区别于一般变换的特权。

### 2.2 cuFFT 路径：Plan 类 + 参数键缓存

`matxCUDAFFTPlan_t`（fft_cuda.h:104）是核心计划类。构造时 `GetFFTParams`（:190）把执行所需一切编进 `FftCUDAParams_t`（stream/irank/orank/transform_type/io 类型/fft_rank/batch，:89-90 字段可见 batch 与 batch_dims）：C2R 时 FFT 长度取输出尺寸（:208 一带的 `o.Size(RANK-1)`）；**batch 维自动推导**——秩 >2 的连续张量把前 n-1 维连乘成 batch（:218 `std::accumulate(... multiplies)`），rank=2 取 `i.Size(RANK-2)`（:227）。注释 :214-216 记录了一个性能决策史：早期用 `cudaMemGetInfo` 按空闲显存决定 batch，因该调用太慢被放弃，改为信任用户。执行接口 Exec(o,i,CUFFT_FORWARD)（:141）/INVERSE（:170），`ifft_impl`/`ifft2_impl` 在 :730/:821。

**缓存**：plan 按 `FftCUDAParams_t` 全参数键控——`FftCUDAParamsKeyHash`（:617）+`KeyEq`（:630）+ `fft_cuda_cache_t = unordered_map<FftCUDAParams_t, std::any,...>`（:645）。第二次同形状 FFT 直接复用 cufftPlanMany，省掉 plan 创建这个著名大开销。错误路径 MATX_CUFFT_ASSERT 宏（:51/:71）把 cuFFT 错误码翻译成带建议文案的 `matxCufftError` 异常（:75）。

### 2.3 cuFFTDx 路径：device 端融合 FFT

fft_cufftdx.h 服务 CUDAJITExecutor：把 FFT 编成 device 函数（前缀宏 `fft_cufftdx_func` :35，include libcufftdx.h :42）。`cufftdxDescriptor GeneratePlan()`（:95）用 cufftdxCreateDescriptor/SetOperatorInt64 描述：API 选 LMEM（寄存器）/SMEM（共享内存）两路（:102 一带 method_ 判定）、执行域 BLOCK（:105）、FFT 尺寸（:109）。`ffts_per_block_`（:67/:80）控制一个 block 叠几个 FFT。源码 :97-99 留有被注释的"≤32 用寄存器"分界实验——LMEM/SMEM 选择目前交由 method_ 显式配置。**整棵 `y = fft(x*w)` 表达式可以被 NVRTC 编成单 kernel**（与 05 篇 nvrtc_helper.h:387 的符号前缀识别机制对接），这是 MatX 相对 cuFFT 库调用的核心增量价值。

### 2.4 FFTW 路径：host 后端

fft_fftw.h 的 `FftFFTWParams_t`（:65）与 GetFFTParams（:83）镜像 cuda 版结构，plan 缓存同样键控（KeyHash :224/KeyEq :239），用 fftw_plan/fftw_execute 家族执行。与 lapack 后端一样由张量所在域自动触发。

## 三、外部连接

- **上游**：operators/fft.h 的 FFTOp/FFT2Op 惰性对象在 `.run()` 后经 BaseOp::run 的 transform 短路（base_operator.h:222 TransformExec）进入本层；
- **横向**：fft 与 conv（FFT 卷积实现）、pwelch（分段加窗 FFT）、spectrogram（examples/spectrogram.cu）、雷达脉压（examples/simple_radar_pipeline.cu:83 PulseCompression）构成信号处理族；
- **下游**：cuFFT handle/plan 归 core/cache.h 全局缓存管理（GetCache cache.h:742），测试间由 ClearCachesAndAllocations 清场（test/main.cu:45）。

## 四、数据流

`(Y = fft(X)).run(stream)` 的完整路径：FFTOp 构造（只记参数）→ run 分派 → GetFFTParams 推导 transform_type/batch → 查 fft_cuda_cache_t 命中则复用 plan、未命中 cufftPlanMany 新建 → cufftExecC2C/Z2Z/R2C（方向由 FORWARD/INVERSE 定）→ 归一化按 FFTNorm（BACKWARD/ORTHO/FORWARD，operators/fft.h:542 签名默认 BACKWARD=NumPy 语义）。R2C/C2R 的长度不对称、stride 与 batch 均在 plan 参数里一次性表达，执行期零再计算。

## 五、设计决策

1. **三实现而非一**：cuFFT 最快但只能整库调用；cuFFTDx 换来融合（省全局存取）；FFTW 补 host 域。域驱动选择对用户零感知。
2. **全参数键缓存**：plan 键含 stream/batch/io 类型/方向，杜绝"同形状不同流误复用"的隐患类 bug——代价是键结构必须完备（hash+eq 双结构体维护）。
3. **can_alias 特权**：FFT 允许原地执行（can_alias fft.h:86），配 base_operator.h:225 一带的别名检查，原地与非原地走不同 plan 分支。
4. **batch 显式化**：把 batch 从"运行时探测空闲显存"（:214 注释记载的旧方案）改为"编译期从张量形状推导"，牺牲极端自适应换稳定延迟。
5. **甄别**：任务书称"fft_common.h 共享计划/参数结构"——实证它共享的是**类型推导**（ComplexInType/DeduceFFTTransformType，fft_common.h:143/:155），参数结构在各后端各自定义（FftCUDAParams_t/FftFFTWParams_t）。

## 六、新人提示

1. plan 缓存跨调用持久：循环里每帧 FFT 不会重建 plan，但换了 stream/shape 就会——基准测试前先热身一次（bench/00_transform/fft.cu 的 nvbench 计时天然包含热身轮）；
2. R2C 输出只存 N/2+1 个点，`fft_size` 参数（operators/fft.h:542）用于补零/截断，别与张量实际长度混淆；
3. FFTNorm 默认 BACKWARD（除以 N 在逆变换），与 NumPy fft 一致、与 scipy 不同；
4. cuFFTDx 路径需 JIT 执行器与 mathdx 工具链，直接 `.run(stream)` 不会用到它——想融合就在 CUDAJITExecutor 上跑；
5. 排查 FFT 错误从 MATX_CUFFT_ASSERT 的文案入手（fft_cuda.h:71），它已按 cuFFT 错误码给出参数级建议。

*锚清单：operators/fft.h:59/772/84/86/542/543/592/679/705/1194/1216、fft_common.h:143/146/149/155/165/171/175、fft_cuda.h:51/71/75/89-90/104/141/170/190/208/214-216/218/227/382/515/617/630/645/730/821、fft_cufftdx.h:35/42/67/80/95/102/105/109/97-99、fft_fftw.h:47/63/65/83/224/239、base_operator.h:222/225、cache.h:742、test/main.cu:45、bench/00_transform/fft.cu。*

# 05 · 案例深读：resampling 重采样内核族与 clahe 单文件算子

## 角色定位

本篇对照精读两个极端样本，覆盖 DALI 计算层的两种典型形态。resampling 家族（dali/kernels/imgproc/resample/，头文件合计约 2900 行）是"框架内"路线：纯模板头+SIMD+VALUE_SWITCH 实例化，CPU/GPU 各一套同构实现；其中 resampling_impl_cpu.h 整整 633 行全是模板函数——tree-sitter 对它零提取，图谱节点全靠批阶段人工手扫补偿。clahe_op.cu 则是"框架外"路线：1257 行单文件 9 个 include（clahe_op.cu:15-25，全部是 cuda_runtime/math 与 dali/core 四件，零算子框架头），从色彩空间转换到双线性 LUT 合成一整套 CUDA kernel 塞在一个编译单元里。

## 内部结构

resampling_impl_cpu.h 的核心是三轴分离重采样。`ResampleCol`（resampling_impl_cpu.h:50-86）是逐像素原语：模板参数 `static_channels+clamp_left+clamp_right` 三重编译期开关——通道数已知时内层循环换到通道维并用 `float tmp[static_channels]` 累加（resampling_impl_cpu.h:76-83，SIMD 友好），未知时退化为逐通道逐滤波系数（resampling_impl_cpu.h:57-66）；越界用 clamp 布尔模板参消掉运行时分支。SIMD 版本 `SIMD_vert/horz_resample_impl`（resampling_impl_cpu.h:88-89/:126-127）在 `__SSE2__` 下用 128 位向量化（kVecSize=16、load/store lanes 推导 :91-99）。三轴入口：ResampleHorz_Channels 走 Surface2D/Surface3D（resampling_impl_cpu.h:318/:339），ResampleVert（:362/:403），ResampleDepth 的 Surface3D 版经 `SliceY/FuseXY` 把 3D 面切成 2D 复用（resampling_impl_cpu.h:418-426/:444-455）；`ResampleHorz`（resampling_impl_cpu.h:477-488）用 VALUE_SWITCH 把 out.channels 在 (1,2,3,4) 内炸成模板参、缺省回落 -1 动态路径；`ResampleAxis`（resampling_impl_cpu.h:500-516）按 axis 0/1/2 分派三轴；`ResampleNN`（resampling_impl_cpu.h:522）是最近邻特例，注释明确 scale 可为负实现翻转。滤波器定义在 resampling_filters.cuh：`ResamplingFilter` 结构（resampling_filters.cuh:30-35，coeffs/num_coeffs/anchor/scale）带 `__host__ __device__` 的 rescale/support/operator()（resampling_filters.cuh:38-48，operator() 用 `if (!(x > -1))` 一并挡 NaN），工厂提供 Cubic/Gaussian/Lanczos3/Triangular（resampling_filters.cuh:73-76），`GetResamplingFilters/CPU` 两套全局表（resampling_filters.cuh:88-89）；文件用 `#ifndef __CUDACC__` 回退 cmath/algorithm（resampling_filters.cuh:23-26）实现双端编译。框架侧 separable.h 定义虚接口 `SeparableResamplingFilter`（separable.h:30-52，Setup/Run 纯虚+静态 Create），separable_impl_select.h 的 Create 直接 new `SeparableResamplingGPUImpl`（separable_impl_select.h:25-37）；参数封装 ResamplingParamsND（params.h:96）。

clahe_op.cu 自底向上：设备端色彩转换族 srgb_to_linear/linear_to_srgb/xyz_to_lab_f/rgb_to_lab/lab_to_rgb（clahe_op.cu:132-232，各带 _ref 参考版），然后是两级 kernel 谱系——基础版 rgb_to_y_u8_nhwc（clahe_op.cu:306）/hist_per_tile_256（clahe_op.cu:583）/clip_cdf_lut_256（clahe_op.cu:646）/apply_lut_bilinear_gray+rgb（clahe_op.cu:725/:977），优化版 coalesced/warp_optimized/fused/vectorized 变体（clahe_op.cu:266/:497/:835/:895）。CDF 重分布核心是设备函数 clip_redistribute_cdf（clahe_op.cu:335）。尾部两个 launcher：基础三步 Launch（RGB→Y→直方图→clip→apply，clahe_op.cu:1180 附近）与 `LaunchCLAHE_RGB_U8_NHWC_Optimized`（clahe_op.cu:1186）——注释明说 fused RGB→Y+直方图"saves one kernel launch + memory round-trip"（clahe_op.cu:1192）。宿主侧 clahe_op.cc 的 ClaheGPU（clahe_op.cc:67）实现 SetupImpl/RunImpl（clahe_op.cc:88/:96），DALI_SCHEMA(Clahe) 注册 tiles_x/tiles_y/clip_limit 三参数+InputLayout("HWC")（clahe_op.cc:178 起），DALI_REGISTER_OPERATOR 绑 GPU（clahe_op.cc:248）。

## 外部连接

resampling 的消费链：separable.h → imgproc/resample.h 聚合 → operators/image/resize 家族（resize_base.cc/resize_op_impl_gpu.h）；resize_base.cc 用 extern template+.cc 尾显式实例化控制编译膨胀（NOTES batch-41）。测试是全 kernels 最密的：dali/kernels/test/resampling_test/ 八个文件覆盖 CPU/GPU/滤波器/可分离性。clahe 的 CPU 参考在 clahe_cpu.cc（139 行），行为对照靠 clahe_test.cc 与 test_clahe.py。

## 数据流

resampling：ResamplingParamsND（origin/scale/滤波器）→ InitializeResamplingFilter 预计算每输出列的 in_columns+coeffs（resampling_impl_cpu.h:36，预计算左端索引与系数是全家族性能前提）→ 按轴依次 ResampleHorz/Vert/Depth（可分离滤波逐轴复合）→ ConvertSat 落目标 dtype。clahe：RGB→亮度 Y→按 tile 统计 256 bin 直方图→clip 重分布得每 tile LUT→四 tile 双线性插值 LUT 合成输出→RGB 按比例回缩。

## 设计决策

1. 通道数当模板参（1/2/3/4 炸开）+未知回落：覆盖典型图像通道又不强行实例化全空间。
2. clamp/翻转等边界语义编译期化：ResampleCol 的布尔模板参把边界处理从热循环里挤掉。
3. 3D 复用 2D（SliceY/FuseXY）：深度重采样不另写一套，切片后走同一条 2D 路径。
4. 滤波器表全局单例+双端编译：CPU/GPU 共享同一套系数语义，`__CUDACC__` 分支只是数学库适配。
5. clahe 选单文件而非 kernels 框架：三步流程强耦合 tile 状态，fused kernel 收益（省一次显存往返）大于框架复用收益；代价是 1257 行难拆、只能靠专门 test 对拍。
6. 优化版与基础版并存：coalesced/warp/fused 各有适用形状，基准版保底正确性。

## 新人提示

读 resampling 顺序：params.h → resampling_filters.cuh → ResampleCol（resampling_impl_cpu.h:50）→ VALUE_SWITCH（resampling_impl_cpu.h:477）→ separable.h 虚接口；对照 GPU 版 resampling_impl.cuh（724 行）看同一算法两种落地。图谱提示：resampling_impl_cpu.h 节点几乎全为人工补扫，读图须回源码。改 clahe 先跑 clahe_test.cc 的 CPU 对拍再动优化 kernel；schema 文档明说 GPU 只支持 luma_only=True（clahe_op.cc:240 docstring），per-channel 仅 CPU。任何"重采样输出差一像素"问题先查 in_columns 预计算与 clamp 模板参，再查滤波器 support() 的 ceilf 语义（resampling_filters.cuh:44）。

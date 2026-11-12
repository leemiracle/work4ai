# 07 · cuFFT 与 LTO callback：从经典变换到构建链深水区

## 角色定位

cuFFT 域在图谱中占 L06 层（43 节点），分两支：七组经典 FFT 示例（1d_c2c / 1d_r2c_c2r / 2d_c2r_r2c / 3d_c2c / 三组 mgpu 多 GPU）走"plan→执行→对拍"教学路线；`lto_callback_window_1d` 是全仓唯一同时演示 **LTO 回调、NVRTC 运行时编译、legacy 回调**三种设备码注入方式的深水区示例，也是把"fatbin→bin2c→C 数组嵌入"这条构建链讲透的教材。

## 内部结构

LTO 四件套的分工：`r2c_c2r_lto_callback_device.cu` 定义两个 `__device__` 回调——`windowing_callback`（r2c_c2r_lto_callback_device.cu:31，经 `cb_params* info` 取窗口参数）与常量内存变体（:45-46 的 `__constant__ cmem_window_size/cmem_signal_size` + :47）；`nvrtc_helper.h` 的 `compile_file_to_lto`（nvrtc_helper.h:50）以六个编译参数（:66-72，含 `-dlto` 与 `--relocatable-device-code=true`）产出 NVVM IR，经 `nvrtcGetLTOIRSize/nvrtcGetNVVM`（:96/:98）取回；`callback_params.h:23-26` 的 `cb_params` 结构 + :29-32 的全 constexpr 问题规格（batches=830、signal_size=328、window_size=32）+ :35 的 1e-6 精度阈值；宿主侧 `r2c_c2r_lto_callback_example.cpp` 在 ：78 以 `cufftXtSetJITCallback` 绑定回调名+fatbin 字节数组。

## 外部连接

`cufft_utils.h` 是 cuFFT 全域共享枢纽（cufft_utils.h:23 的 `CUDA_RT_CALL` 与 :41 的 `CUFFT_CALL` 两宏 + :57 的 scaling_kernel），被七个经典示例 include（mgpu 示例靠它做 1/N 归一化）。构建侧连接 CUDA 工具链三件：CMakeLists.txt:92 用 nvcc `-dc -fatbin` 产出 LTO fatbin，:93 用 `bin2c --name window_callback --type longlong` 转 C 数组头（对应 example.cpp:32 的 include 注释），:99 legacy 目标改链 `CUDA::cufft_static`。

## 数据流

主链路：`init_input_signals` 造时域信号→R2C 正变换（example.cpp:90）→C2R 逆变换时 **load callback 在读取频谱瞬间加窗**（窗内样本直通、窗外置零，device.cu:41 三目式）→拷回与 `reference_r2c_window_c2r`（独立 kernel 加窗的参考实现）对拍 L2 误差（example.cpp:113-116）。关键时序约束写在 ：60 注释：**LTO 回调必须在 plan 创建之前设置且不可解除**——与 legacy 的 `cufftXtSetCallback`（legacy_example.cu:101）行为不同，这是迁移时最易踩的坑。

## 设计决策

三种实现对照是本示例的教学核心：LTO 版回调被内联进 cuFFT plan（无函数指针开销，需 SM≥5.0 检查 example.cpp:127-129）；NVRTC 版运行时编译同一份回调源（宿主与设备源码解耦）；legacy 版（:38 定义、:53 取函数指针）必须整链静态库+`CUDA_SEPARABLE_COMPILATION`+`CUDA_RESOLVE_DEVICE_SYMBOLS ON`（CMakeLists.txt:85）。`static_assert(window_size < signal_size/2+1)`（example.cpp:35）把频谱半轴约束前移到编译期；常量内存开关 `CB_USE_CONSTANT_MEMORY` 是 CMake option（:61-76 双分支），演示参数传递两条路。

## 新人提示

先跑 1d_c2c 理解 plan 模型，再读 lto_callback 的 README（三版本对照表）；改问题规格只动 callback_params.h 的 constexpr；bin2c 生成的 `_fatbin.h` 在 build 目录而非 src（include 路径含 `${CMAKE_BINARY_DIR}`）。注意 `CUDA_LTO_ARCHITECTURES` 硬编码 75（CMakeLists.txt:39）——回调 fatbin 只含 sm_75 LTO 码，plan 侧靠 LTO IR 再 lowering。

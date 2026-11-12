# 04 · nvpl_fft：FFTW API 兼容层示例全景

## 1. 角色定位

`nvpl_fft/` 是七库中唯一以"兼容第三方 API"为卖点的示例集：NVPL FFT 对外暴露的正是 **FFTW 3.x 接口**（`fftw_*/fftwf_*` 前缀、`nvpl_fftw.h` 头、`nvpl::fftw` target，README.md:152），20 个 cxx 文件加 5 个 Fortran 文件全部演示既有 FFTW 代码如何零改动迁移到 aarch64 CPU。血统注释直白：`1d_c2c_single_example.cpp:5` 标注 "Modified from CUDALibrarySamples/cuFFT"。示例兼具正确性自测（PASS/FAIL）与基准两职。

## 2. 内部结构

**测试框架双头**是公共地基。`cxx/common.h` 定义布局七元组容器 `test_info`（`common.h:27-51`）与精度评估三件套：`fill_real_input_data`（`:135`，按 `pad_offset` 展开带 stride/embedding 布局，填可复现整数序列）、`compute_reference`（`:151`，FFT_iFFT 往返期望值直接取输入×fft_size，因正逆合成=恒等×N）、`compute_error`（`:170`，相对 L2 误差，`:177` 注释提醒 `std::norm(z)=z*conj(z)` 非模长），`assess_error`（`:186`）按容差判定。容差在 `cxx/utils.h:10-20`（double 1e-6/float 1e-5）；utils.h 藏钉版笔误——include guard 拼成 `NVPLFFT_EXAMPLE_UNTILS_H_`（`utils.h:1/:50`），"UTILS"成了"UNTILS"，自洽故无碍。r2c 布局数学集中在 `get_r2c_c2r_setups`（`common.h:70-100`）：复数谱元素数=前若干维积×(末维/2+1)（`:75`，Hermitian 半谱）、in-place 实数组 padding 到 2×complex_elems（`:77`）、强制两侧 stride 相同防覆写（`:79-82`）。

**基础生命周期** `1d_c2c_single_example.cpp`：`fftwf_plan_dft_1d` 建 plan（`:27-28`，forward out-of-place、backward in-place）→逐 batch `fftwf_execute_dft`（`:35-36`）→`destroy_plan`+`cleanup`（`:47-49`）。plan→execute→destroy 三段式是全仓骨架。

**wisdom 三通道** `auxiliary_apis_example.cpp`：①系统级 `fftw_import_system_wisdom`（`:20`）；②文件级 export/import（`:34/:43`）；③字符串级 export/import（`:52/:59`），另有 `print_plan`/`set_timelimit`/`cost`/`flops`（`:68/:72/:76/:81`），成功判定取 1（`:8-9`）。此文件两处松散写法须警惕：`complex<double>` 向量被 cast 成 `fftwf_complex*` 且变量名拼成 `inpout_data`（`:13-14`），`fftwf_plan_dft_1d` 返回值赋给 `fftw_plan`（`:26`）——f/d 混用，因 plan 从未 execute 才无事，照抄进生产是坏示范。

**OpenMP 双场景** `c2c_single_withomp_example.cpp`：`ONE_PLAN_PER_THREAD`（`:44-73`）每线程在并行区内自建 plan、私有缓冲，甚至令 `iostride=1+tid`（`:54`）；`ONE_PLAN_PER_PROCESS`（`:74-91`）建一次 plan、各线程用 `execute_dft` 对不同分片并发执行同一 plan（plan 不可并发、execute 可，FFTW 官方口径）。线程配置 72/2（`:10-12`），NVHPC 下退化 1，因其 OpenMP 不支持 CPU 嵌套并行区（`:7-8`）；嵌套开关做 OpenMP 5.0 适配：`omp_set_nested` 已废弃，GCC 16+/Clang 15+ 改 `omp_set_max_active_levels(2)`（`:37-42`）。

**基准** `plan_many_dft_benchmark_example.cpp`（595 行最大）以 traits 模板 `struct fftw<SINGLE/DOUBLE>`（`:131/:177`）统一单双精度的 init/plan/execute/cleanup，`plan_many` 内分派 c2c/c2r/r2c。性能口径 5·N·log2N（`:222-228`）加带宽（`:231`）；计时分整段秒表与逐次取中位两档（`:357-379`，统计源自 `common.h:212`）。结果以 `++++CSV-Header/Data` 机器格式打印（`:560/:385`）供 `nvplbench_generic.py` 采集，行内带 `LD_PRELOAD` 探测标签（`:29-46`，识别 nvpl/fftw-sve/fftw/armpl），为与上游 FFTW、ArmPL 同机对比。

**Fortran 侧**：f03 例 `include 'fftw3.f03'`（`c2c_c2r_r2c_double_apis_example.f90:73`），`nvpl_fft_get_version()` 作函数（`.f90:79`）；F77 例 `include 'fftw3.f'`（`.f:65`）以子程序调用（`.f:71`）——同 API 两种绑定形态。`.f90` 另演示 `fftw_alignment_of`（`:109/:118`）与线程套件（`:627-645`）。最特殊的是 `rank_mismatch_test_example.f90`：头注释（`:1-3`）言明专测"多维数组传给 `dimension(*)` 接口"——旧具名接口版 fftw3.f03 会因 TKR 秩检查编译失败。手法是 `fftw_alloc_complex` 后 `c_f_pointer` 整形 `[NX,NY]`（`:88-92`）再喂 rank=1 的 plan_many（`:101`）；后段三个 `*_rank_cmp_test`（`:357/:422/:487`）验证同一变换在 1D 扁平与 2D 整形数组上逐位一致（`:351-354`）。

## 3. 外部连接

cxx 例链 `nvpl::fftw`（`cxx/CMakeLists.txt:28`），OMP 组加链 `OpenMP::OpenMP_CXX`（`:30`）；顶层 `find_package(OpenMP REQUIRED)`+`find_package(nvpl REQUIRED COMPONENTS fft)`（`nvpl_fft/CMakeLists.txt:21-22`），Fortran 例仅 GNU/NVHPC 启用（`:29-33`）。`include_header_example.cpp` 是对外声明：include 系统名 `fftw3.h`（`:4`），靠调用 NVPL 专有的 `nvpl_fft_get_version()`（`:10`）确认拿到的是 NVPL 而非系统 FFTW。CTest 矩阵 thread 1..144×双精度×1D/2D/3D（`cxx/CMakeLists.txt:43-90`），超核数跳过（`:45-48`），基准例再补 2/3/5/7 幂尺寸（`:102-117`）。参照系双轨：`common.h:73` 引 cuFFT 文档讲 r2c 布局，benchmark `:17-22` 引 FFTW 官方 advanced-DFT 文档。

## 4. 数据流

正确性例：解析 n（至 3 维）→`test_info`→`set_howmany` 按 256MB 上限压 batch（`common.h:16/:196-204`）→三件套生成输入与期望→plan→forward+backward→相对 L2→判定。基准例相反：`--size` 支持 64m 后缀（`:419-437`）→**先建 plan 后填数**（`:343-347`，`FFTW_MEASURE` 会覆写输入）→warmup→计时→单行 CSV。Fortran 例用 `fftw_alloc_complex`+`c_f_pointer` 手工管内存。

## 5. 设计决策

①**相对 L2 而非逐元素**：FFT 误差随规模累积，归一化容差可对全尺寸段统一 1e-5/1e-6；②**ESTIMATE/MEASURE 分工**：正确性例全用 ESTIMATE、基准用 MEASURE，`c2c_c2r_r2c_single_apis_example.cpp` 同文件混用两旗（`:118-123`）直观示范差异；③**simple/advanced 双 API 对照**：同一组变换分别用 `fftwf_plan_dft`（`:118`）与带 istride=2 的 `fftwf_plan_many_dft`（`:177`）各跑一遍；④**.f03 内容以 .f90 扩展承载**：老 CMake 不认 .f03 后缀（`fortran/CMakeLists.txt:17-19`），`-std=f2003 -fall-intrinsics` 保 EXIT()（`:27`），F77 例则 `-std=legacy`（`:44`）。

## 6. 新人提示

顺序：`1d_c2c_single`（最小骨架）→`c2c_c2r_r2c_single_apis`（双 API 对照）→`*_many`（多线程 strided）→`auxiliary_apis`→benchmark。四个坑：① in-place r2c/c2r 实数组必须 padding 且 rank≥2 时要求 istride==ostride（`common.h:79-82`、benchmark `:297-305`），否则输入被覆写；② NVHPC 别指望嵌套 OpenMP（`c2c_single_withomp_example.cpp:7-8`）；③ Fortran 多维数组传参前确认 fftw3.f03 是 dimension(*) 版本，否则 TKR 编译失败——`rank_mismatch_test_example.f90` 即官方回归测试；④ benchmark `--size 0` 按 256MB 工作集算 batch（README.md:58），小内存机器跑全量 CTest 吃力。另 README.md:41-43 的 Run 命令把 `.f/.f90` 源文件名当可执行名写，实际二进制是 `*_example_03/_77`（`fortran/CMakeLists.txt:20/:37`）。

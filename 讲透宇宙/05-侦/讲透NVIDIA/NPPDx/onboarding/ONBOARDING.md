# NPPDx 新人入门（ONBOARDING）

> 基于知识图谱（547 节点/1151 边/14 层/14 步导览，commit e7efdc12）与源码核实撰写，锚点行号全部经源码验证。

## 1. 项目定位

NPPDx 是 NVIDIA 开源的 **header-only CUDA C++ 图像处理库**（Apache-2.0，版本 0.1.2，`include/nppdx/nppdx_version.hpp:L29` 的 `NPPDX_VERSION 102` 与 CMake 包版本一致），可视为经典 NPP 库的「Dx 编程模型」重设计：不再调用黑盒库函数，而是用算子组合（`InputOutput`/`InputFormat`/`Function`/`TileSize`/`SM`/`Block`）在**编译期描述**整条图像管线——ingest、色彩转换、pointwise、area（盒式/高斯/中值/锐化）、resize——然后在你**自己的 CUDA kernel 内**执行，从而把 NPP 需要多次 kernel 启动+全局内存往返的多步操作融合为单内核。

解决的核心痛点：视频/图像管线中「格式转换→滤波→再转换」的中间拷贝与重复访存。技术栈为 C++17 重度模板元编程 + CUDA C++17，无任何 .cpp 编译单元（示例的 `error_checking.cpp` 是唯一例外）。规模：约百个头文件、19 种像素打包格式、SM 700~1210 共 14 个架构白名单、8 个函数族后端、8 个格式家族后端。依赖姐妹库 commondx 1.5.1（共享 Dx 表达式骨架），可选依赖 CuTe/CUTLASS 与 CCCL（NVRTC 路径）。

## 2. 架构总览

图谱 14 层，依赖方向自上而下（上层引用下层）：

- **L01 项目治理**：README/LICENSE/CONTRIBUTING（DCO 签署、NVIDIA 内部开发随发布公开）/SECURITY（漏洞须走 PSIRT，禁止 GitHub 报告）。
- **L02 CMake 包导出**：`lib/cmake/nppdx/` 与 `lib/cmake/commondx/` 的 find_package CONFIG 件，两个 INTERFACE IMPORTED 目标，见 `lib/cmake/nppdx/nppdx-config.cmake:L43-62`。
- **L03 commondx 编译基座**：命名空间重定位宏对 + std/cuda::std 双轨 STL 垫片（NVRTC 可整体迁移），代表 `include/commondx/detail/stl/type_traits.hpp`。
- **L04 commondx 数值与张量**：复数类型体系（half/bf16/FP8）、SM 共享内存查表（`include/commondx/device_info_shared_memory.hpp:L31`，Blackwell 1000 系=227KB）、CuTe 适配层。
- **L05 commondx 算子与 traits**：Dx 系库共享的表达式骨架。标签树根在 `include/commondx/detail/expressions.hpp:L29`（`operator_expression`），常量算子基 `constant_operator_expression`（L36-39）混入 integral_constant，使 `SM<900>` 这类算子本身就是编译期值。
- **L06 nppdx 入口与值类型**：唯一伞头 `include/nppdx.hpp:L22`；`Array`/`ImageLayout`/纹理句柄等值类型 + 20 余个 Description 查询 traits（`include/nppdx/traits/nppdx_traits.hpp`）。
- **L07 编译配置与工具链守卫**：`include/nppdx/detail/config.hpp:L25-31` 定义 `NPPDX_STD`（NVRTC 下 `::cuda::std`）；`include/nppdx/detail/decl.hpp:L20-36` 用助记字母表（N/S/C/E/I/F/H/D）生成 191 个修饰符速记宏；`system_checks.hpp` 按 NVCC/NVRTC/Clang 三路径 #error 拦截不达标工具链。
- **L08 图像算子 DSL**：15 个算子头组成描述语言词汇表，聚合入口 `include/nppdx/operators.hpp:L21-34`。
- **L09 管道描述与执行引擎**：库心脏（见第 4 节）。
- **L10 执行数据库与 cell 运行时**：`detail/database/` 下 cell 配置/数据视图/网格执行器/存储槽位与 op_impl 实现库。
- **L11 函数算子后端**：八大函数族的纯计算 device 后端 + constexpr 数学库 + 高斯 FIR 系数全档查表。
- **L12 像素格式与纹理后端**：8 个格式家族（fast/safe 双路径）+ CUDA array 纹理/表面路径。
- **L13 示例公共设施**：错误统计/计时/随机数据/CPU 金标准/NPP 参考线/SM 分派 runner（`example/nppdx/common/example_sm_runner.hpp:L32-74` 用 14 个 `NPPDX_EXAMPLE_ENABLE_SM_*` 宏 + 运行时 switch 分派）。
- **L14 渐进示例集**：00 入门→01 色彩→02 融合 pointwise→03 area→04 resize 五组，全部带 NPPDx vs NPP vs CPU 三方对拍。

## 3. 核心链路

以入门示例为叙事主线（导览 t01→t02→t05→t06→t07）：

1. **接入**：用户只 include 根伞头 `nppdx.hpp`，它仅包含 `nppdx/nppdx.hpp` 聚合头（版本宏/config/operators/traits/types/description/execution 一并引入）。
2. **拼装描述**：`example/nppdx/00_introduction/introduction_example.cu:L79-85` 用 `operator+` 把五个算子加成类型：`InputOutput<ingest>() + InputFormat<rgb24>() + TileSize<48,48>() + Block() + SM<SM>()`。四个 `operator+` 重载（算子+算子/描述+算子/算子+描述/描述+描述）在 `include/nppdx/detail/nppdx_description_arithmetic.hpp:L57-85`。
3. **条件升格**：`make_description`（同文件 L40-50）按 `is_complete_description` 决定产物是普通 `nppdx_description`（还不完整、仅可继续拼接）还是可执行的 `nppdx_execution`；NVRTC/MSVC 走 `nppdx_execution_partial` 降级规避编译错误。
4. **静态校验**：`include/nppdx/detail/nppdx_description.hpp:L142-161` 集中 static_assert——每类算子至多一个、ingest 必配 InputFormat 且禁 OutputFormat（exgest 反之）、color_convert 必须携带 ColorConvert 算子。错误全部在编译期爆出。
5. **推导执行**：`include/nppdx/detail/nppdx_execution.hpp:L45` 的 `nppdx_execution` 把算子集合打包成运行时值 `value`（L90 经 `normalize_exec_operator` 回填推荐的 block_dim），再静态算出 `impl` 类型（L94-96）、tile/block 尺寸与共享内存字节数（L139-140）。
6. **kernel 内执行**：回到示例 `introduction_example.cu:L29-46`——每线程持寄存器数组 `intermediate_data[elements_per_thread]`，`IngestOp().execute(global_input, intermediate_data, ...)`（L40）把 packed 全局内存解包成内部 float×3 格式；`ExgestOp().execute(...)`（L45）反向打包写回。数据流主径：**全局内存/纹理(packed) → 寄存器 cell(4×2×3 float) → 计算后端 → 写回**；area 类算子改走共享内存 TileStorage 路径（halo 边界由 MemoryHalo/CumulativeHalo 描述）。
7. **落地实现**：execute 最终派发到 `op_impl<...>` 特化（`include/nppdx/detail/database/operation_common.hpp:L34` 主模板未特化即 static_assert），再进 L11 函数后端或 L12 格式后端做纯计算。

## 4. 关键文件深读

- **`include/nppdx/detail/nppdx_execution.hpp`（361 行，库心脏）**：从描述推导一切执行要素——`value`/`recommended_op_config`/`impl`/`shared_memory_size`（L139-140）全部是编译期常量，内核里零运行时决策。暴露 19 个 `execute()` 重载（L147-354）覆盖三族路径：寄存器直通（L154）、纹理/表面 ingest/exgest（L181/L190）、共享内存 TileStorage 输入/输出/中转（L226/L322/L345）。内部处理类型恒为 float、3 通道（L106-109），这是全库「中间格式」契约。
- **`include/nppdx/detail/nppdx_description.hpp`（174 行）**：`nppdx_description`（L40）是描述类型的校验基座，同时给出全部默认值（SM 默认 700、BlockDim 默认 256×1×1、TileSize 默认 16×16，L49-110），让最小描述也能通过。空描述有独立特化（L167-170）作为 `operator+` 的单位元。
- **`include/nppdx/operators/function.hpp`（759 行）**：函数算子全家桶。`function` 枚举（L42）列八种函数；高斯模糊按半径段查 `tap_configs` 表（L203）取 3..21 tap FIR；Resize（L532）用互素 J:K 有理缩放。每个算子配 `operation_operator_traits` 特化声明自己的 halo 与存储需求——执行引擎据此自动布共享内存。
- **`include/nppdx/operators/formats.hpp`（441 行）**：`packing_format` 枚举（L32）定义 19 种真实格式（另加 none/internal 哨兵）；`packing_format_props`（L94）提供通道数/位深/子采样/平面数/最小行 stride 的唯一事实来源；L393 的 `dispatch_format` 用宏表驱动编译期/运行时双态分派。改枚举必须同步 NPPDX_FOR_PACKING_FORMATS 宏表（文件尾注释明言）。
- **`example/nppdx/00_introduction/introduction_example.cu`（179 行）**：最短可读样例。L124-134 展示描述的 trait 查询与 static_assert 兼容性检查（tile/block/elements 必须一致、方向必须相反）——这是「描述即类型、约束即编译期」哲学的浓缩演示。

## 5. 模块间关系

- **commondx ← nppdx 单向依赖**：nppdx 的每个算子头（如 `include/nppdx/operators/input_output.hpp:L47`）都向 `commondx::detail` 登记 `is_operator`/`get_operator_type` 特化，把图像算子接入 Dx 分派体系；`operator_type` 枚举（`include/nppdx/operators/operator_type.hpp:L30-46`）是全库分派键。
- **循环包含靠 fd 头打破**：operators↔traits 互相引用，靠 `is_operator_fd.hpp`/`get_operator_fd.hpp` 前置声明对解环（commondx 侧同样模式）。
- **op_impl 特化契约**：执行层与实现层唯一接口。input_output 线经宏为 19 种格式批量实例化；function 线在 `function_operation_implementation.hpp` 为八族算子特化；安全读写统一过 `nppdx_safe_functions`（static_assert `format_backend<Format>::is_implemented` 后才转发）。
- **三编译路径契约**：`NPPDX_STD_INCLUDE_*` 宏（`config.hpp`）把 std 头选择抽象成一点——NVCC 走 `<...>`、NVRTC 走 libcu++ `<cuda/std/...>`、clang CUDA 兼容模式重定向到 push/undef 宏的包装头。
- **示例层契约**：`common_example_objects` 静态库（`example/nppdx/CMakeLists.txt:L236`，唯一 .cpp 编译单元）承载 error_checking 模板显式实例化，全示例共享对拍设施。

## 6. 构建与运行

仓库**没有顶层 CMakeLists**（README 明言 no top-level configure/build/install step）——克隆即用。两条路：

- **跑示例**：`cmake -S example/nppdx -B build-nppdx-examples -DNPPDX_BUILD_CUDA_EXAMPLES=ON -DNPPDX_CUDA_ARCHITECTURES=80-real`，然后 `cmake --build ... --target nppdx_examples` 与 `ctest --test-dir ... --output-on-failure`。`add_nppdx_example` 函数族（`example/nppdx/CMakeLists.txt:L303`）为每个示例生成可执行 + CTest 用例；`NPPDX_EXAMPLE_ENABLE_SM_*` 宏（L215）注入架构白名单。要求 sm_75+/CUDA 13.0+/CMake 3.30+/C++17（README 口径）。
- **消费接入**：`find_package(nppdx CONFIG)` 后 `target_link_libraries(... nppdx::nppdx)`。config 件自动解析 commondx 依赖（已建目标则复用，否则二次 find_package 回落本前缀，缺失则 FATAL_ERROR），见 `lib/cmake/nppdx/nppdx-config.cmake:L43-62`；targets 件附加 `--expt-relaxed-constexpr` 与 C++17 特性。
- **非标准编译线**：clang PTX 线（Clang 21+ `--cuda-device-only` 离线出 .ptx，host 侧纯 C++ runner 经 dlopen Driver API 加载，见 `example/nppdx/clang_ptx/fused_resize.cpp`）；NVRTC 线运行时编译（`example/nppdx/common_nvrtc.hpp` 解析 include 目录）。

## 7. 设计决策与取舍

- **约束全前置编译期**：格式配对/算子唯一性/架构合法性全部 static_assert（`include/nppdx/detail/nppdx_description.hpp:L142-161`），运行时零校验；代价是模板报错深、NVRTC/MSVC 走 partial 降级丢部分诊断。
- **float×3 中间格式契约**：内部恒 float 三通道（`include/nppdx/detail/nppdx_execution.hpp:L106-109`），换取任意格式×函数×格式自由组合，代价是 8bit 图走浮点往返；cell 全库单点 {{4,2},3}（`include/nppdx/detail/database/cell_config.hpp:L60-64`）。
- **fast/safe 双路径**：格式后端按对齐假设整块搬运，否则逐像素 clamp；exgest 固定 clip 饱和（与 NPP 同契约）。
- **勘误①**：README 称 sm_75+，代码白名单含 700/720（`include/nppdx/detail/nppdx_checks.hpp:L35-52`），守卫仅拦 <sm_70（`system_checks.hpp:L22`）、is_supported 判 sm>=700（`include/nppdx/detail/nppdx_is_supported.hpp:L41`）——实为 sm_70+。
- **勘误②**：`system_checks.hpp:L22` 的 #error 消息串尾多 `");`，报错文案原样带出。
- **勘误③**：README 要 CUDA 13.0+，NVRTC 守卫仅要 CTK>=12.0（`system_checks.hpp:L31`）。图谱称 15 重载/约 190 宏，实测 19/191。

## 8. 新人上路

**先看再改**：README→跑通 00_introduction 三示例→精读 `introduction_example.cu:L79-85` 拼接与 L124-134 校验→按导览 t03/t05/t06 读算子/描述/执行层→最后碰 backend。**修改起点**：加格式=formats.hpp 枚举+props+家族后端特化（同步 NPPDX_FOR_PACKING_FORMATS 宏表）；加函数算子=function.hpp 枚举+traits 特化+backend+op_impl 四处联动。**常见坑**：①仅 1D 线程块（`include/nppdx/operators/block_dim.hpp:L32`）；②ingest/exgest 与 function 互斥且方向-格式必须配对；③`formats_compat.hpp` 禁直接 include（L19 #error）；④NVRTC 下 partial 降级丢部分诊断，排错回 NVCC；⑤外部唯一入口是根 `nppdx.hpp`。

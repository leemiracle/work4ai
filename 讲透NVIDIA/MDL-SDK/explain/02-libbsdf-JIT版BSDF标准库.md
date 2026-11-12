# 02 · libbsdf.cpp —— JIT 版 BSDF 标准库：为什么一个"库"住在 jit/ 目录里

> 文件：`src/mdl/jit/libbsdf/libbsdf.cpp`（11031 行，图谱 195 子节点，全图最大文件）
> 同目录：libbsdf_internal.h / libbsdf_runtime.h / libbsdf_utilities.h / libbsdf_multiscatter.h / libbsdf_hair.h + general_tables/ + multiscatter_tables/ + CMakeLists.txt

## 1. 角色定位：不是宿主库，是 JIT 的"源码级标准库"

MDL 材质里写的 `df::diffuse_reflection_bsdf()`、`df::microfacet_ggx_bsdf()` 这些内建 distribution function，最终必须变成渲染代码。本文件就是全部 df::*（以及对应 EDF）内建函数的**唯一实现源码**——但它从不被编译进任何宿主 CPU 库。它的宿主是 LLVM：CMake 用 clang 把它编译成 **LLVM bitcode**（`src/mdl/jit/libbsdf/CMakeLists.txt` L39-64 生成 `libbsdf_${HS}.bc`，L105 `target_add_tool_dependency(TOOL clang)`），JIT 后端为每个材质生成 LLVM IR 后把这些 bitcode **链接进最终的可执行代码**。

这就是它住在 `src/mdl/jit/` 下的根本原因：它是 JIT 后端的链接输入，与 `libdevice`、`libmdlrt` 并列的运行时源资产。证据链：① 头部 L41-42 明写 `// These functions are not implemented and will be replaced during DF instantiation`——`BSDF_PARAM bool get_material_thin_walled(State*)` 等符号是留给每个材质实例化时由生成代码替换的占位；② `BSDF_API` 就是 `extern "C"`（libbsdf_internal.h L36），保证跨编译器的符号 ABI；③ 消费端 `src/mdl/jit/generator_jit/generator_jit_libbsdf.cpp` L42-50 `#include "libbsdf_bitcode_hsmp.h"` 等 12 个头（bin2c 把 .bc 转成字节数组内嵌），`generator_jit_llvm.cpp` L1519 `m_link_libbsdf_df_handle_slot_mode` 按编译选项挑选变体链接。

## 2. 内部结构

**公开入口（BSDF_API，全部 extern "C"，每个内建 4 件套 sample/evaluate/pdf/auxiliary）**：

- `black_bsdf_*`（L356-390）：全吸收占位，三函数全是 `absorb(data)`。
- `diffuse_reflection_bsdf_*`（L402-460）/`dusty_diffuse_reflection`（L494）/`diffuse_transmission`（L570）。
- `specular_bsdf_*`（L833）与 thin_film 变体（L907）；`simple_glossy`（L1724/L1854）。
- `sheen_bsdf_*`（L2011）；`backscattering_glossy_reflection`（L2299）。
- microfacet 家族：`microfacet_beckmann_vcavities_*`（L2537）、`microfacet_ggx_vcavities_*`（L2825）、thin_film 变体（L2669）及 smith masking 变体。
- EDF 尾部：`measured_edf_evaluate`（L10681 区段）、`clamped_mix_edf_*`/`unbounded_mix_edf_*`（L10902-11031，含 color 变体）。

**策略类群（组合出全部行为）**：

- Fresnel 家族：`Fresnel_function_none`（L649）/`Fresnel_function_default`（L661，Schlick）/`Fresnel_function_coated`（L681）；曲线求值器 `Fresnel_curve_eval`（L6776）+ Thin_film/Color 变体（L6897/L7045/L7164）。
- 自定义曲线：`Custom_curve_eval`（L7311）+ Thin_film/Color 变体（L7439/L7607）。
- 测量数据：`Measured_curve_eval`（L7866）、`Color_measured_curve_eval`（L8197）。
- 微facet 分布：基类 `Vcavities_masking`（L1672）+ `Distribution_phong_vcavities`（L1705）/`Distribution_sheen_vcavities`（L1988）/`Distribution_beckmann_vcavities`（L2517）/`Distribution_ggx_vcavities`（L2806，构造器存 `m_inv_roughness`，L2813 sample 一行调 `hvd_ggx_sample`）；Smith masking 路线 `Distribution_beckmann_smith`（L3094）/`Distribution_ggx_smith`（L3394）。
- 工具 `float3_float`（L1477）：光谱模式下 color 拆 float 标量+浮点三元组的双载体。

**模板化 mix 引擎**：L8534-9810 是十几个 `template<typename TDF_sample_data, typename TDF_component, bool normalized_mix>` 的 sample/evaluate/pdf/auxiliary 通用实现——clamped/unbounded/normalized mix 与 color 变体全部由同一模板 + 布尔参实例化。光谱门控在 L52-57（`MDL_DF_SPECTRAL_ENABLE`/`MDL_DF_SPECTRAL_SAMPLES`）。multiscatter 命名空间别名 L37：`namespace multiscatter = mi::libdf::multiscatter;`。

## 3. 外部连接

头依赖：libbsdf_internal.h（宏与 df 命名空间）、libbsdf_utilities.h、libbsdf_multiscatter.h（预计算多散射补偿表，源在 multiscatter_tables/）、libbsdf_hair.h（L350，头发 BSDF）。运行时反向依赖 `State*` 回调宿主渲染器：`state->texture_tangent_u(0)`（L413）、`state->adapt_microfacet_roughness()`（L2838）、`state->get_bsdf_data_texture_id(BDK_GGX_VC_MULTISCATTER)`（L2844-2845）、`state->light_profile_evaluate/pdf`（L10668 区段）。上游消费：generator_jit_libbsdf.cpp（内嵌 bitcode）+ generator_jit_llvm.cpp（链接选择）；general_tables/ 提供 BDK 常量等生成表。

## 4. 数据流

编译期：本 .cpp →（clang，按 DF_HANDLE_SLOT_MODES hsmp/hsmn/hsm1/hsm2/hsm4/hsm8 × debug × spectral 共 24 变体）→ libbsdf_${HS}.bc → bin2c → C++ 字节数组头 → 链接进 generator_jit_libbsdf.cpp。材质编译期：MDL 的 `df::xxx_bsdf(...)` 调用被 JIT 代码生成器翻译成对 extern "C" 入口的 call → LLVM 链接器把 bitcode 并入模块 → 内联/LTO 后这些函数体直接长在材质代码里；`get_material_thin_walled` 等占位符号此时被替换为该材质的真实求值。渲染期：`BSDF_sample_data*`（入射方向 k1、随机数 xi、出射槽）+ `State*`（几何/纹理回调）→ 几何检查（`get_geometry` L413）→ 分布采样/求值 → `bsdf_over_pdf` 权重写回 data。

## 5. 设计决策

- **源码→bitcode→链接，而非运行时动态调用**：材质可执行码零外部调用开销，LLVM 可跨"内建函数边界"做死代码消除与常量传播（tint 为常量 color(1.0) 时整段饱和逻辑可被优化掉）；对比"运行时函数库 + call 指令"方案（OSL 早期），换的是编译时间、得的是运行性能——这是 NVIDIA 选择 LLVM JIT 路线的核心动机。
- **模板+策略类组合而非逐内建手写**：24 个 microfacet 入口共享 `microfacet_sample/evaluate/pdf/auxiliary` 引擎，分布（Distribution_*）与菲涅尔（Fresnel_*）作为模板参数注入，L2841-2852 一次组合 GGX+default+Fresnel；新增分布只写一个 30 行类。
- **extern "C" ABI**：bitcode 与 JIT 生成代码之间无 C++ name mangling，跨 clang 版本链接稳定（CMake 注释 TODO 也点明变体生成仍可裁剪）。
- **handle-slot 模式编译期特化**（hsm1..hsm8）：DF 句柄槽数是材质空间/时间的权衡维，按模式预编译六份 bitcode 而非运行时参数化，保持 JIT 端零分支。
- **光谱/RGB 双模式编译**：`MDL_DF_SPECTRAL_ENABLE`（L52）使同一源码产出两套数值路径，color_sample 在光谱模式退化为标量带（float3_float L1477）。

## 6. 新人提示

- 调试入口：CMake 同时产出 `.ll`（L43 注明 "useful for debugging"）——看 JIT 到底链了什么，直接读 `build/.../generated/libbsdf_hsmX.ll`。
- 改本文件**必须重新跑 bitcode 生成**（构建系统自动，但手拷 .cpp 到别处编译是常见错误）；它与 general_tables/multiscatter_tables 是配套的，表变了 bc 也要重编。
- `absorb(data)` 是所有"不可能方向"的统一出口（L361），渲染器据此终止光路。
- BDK_*_MULTISCATTER 常量（L1744 等）指向预计算多散射能量补偿表，纹理 id 经 `State::get_bsdf_data_texture_id` 取得——多散射 tint 为 0 时跳过（L2844 三目）。
- 相关文件：libbsdf_internal.h（宏定义）、generator_jit_libbsdf.cpp（bitcode 内嵌）、generator_jit_llvm.cpp（链接逻辑）、libbsdf_multiscatter.h（表数据）。

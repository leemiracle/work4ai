# 09 · mdlrt Resource_handler 与 Baker：JIT 纹理桥与 GPU/CPU 双路烘焙

## 1. 角色定位

本篇覆盖 render 树两条互补的执行线。**`src/render/mdl/runtime/mdlrt_resource_handler.cpp`**（1146 行，文件头注释"Functionality to handle textures in jitted code"，:29-30）实现 `mi::mdl::IResource_handler`：MDL JIT 编译器把材质编成 LLVM 代码后，`tex::lookup_*` 等资源内建函数无法内联，需要 C++ 运行时回调表——Resource_handler 就是这张表，把 tag 直译成 scene 元素访问。它在 `Target_code::finalize()` 里按需创建（backends_target_code.cpp:199-201），传给 lambda 的 `init(transaction, NULL, m_rh)`。**`src/render/baker/baker/baker.cpp`**（1149 行）是烘焙模块：把编译好的材质表达式在参数空间采样成纹理，供 distiller 工作流蒸馏材质，经 `Mdl_distiller_api_impl::create_baker()`（neuray_mdl_distiller_api_impl.cpp:428-447）暴露成公共 `mi::neuraylib::IBaker` API。

## 2. 内部结构

**Resource_handler** 是纯回调分派层。资源对象生命周期用 placement new 管理：`tex_init()`（mdlrt_resource_handler.cpp:61）按 shape 把 `Texture_2d/3d/cube/ptex` 之一的构造函数放到调用方给的 16 字节对齐缓冲上——tag 经 `DB::Typed_tag<TEXTURE::Texture>` 直转（:68-69），`DB::Transaction*` 通过 ctx 透传；`tex_term()`（:91）显式调析构。缓冲大小由 `get_data_size()`（:45-59）取六种资源 struct 的 sizeof 最大值。TS_BSDF_DATA 无专属类，按 3D 纹理处理（:84-86）。lookup 族是全对称矩阵：float/float2/float3/float4/color × 2d/3d/cube/ptex × 带 derivs 变体（:154/:175/:542），加 texel 读取（:642 起）与分辨率查询（:130/:142）。光分布 `lp_*`（lp_evaluate :854、lp_sample :866）；BSDF 测量 `bm_*`（bm_evaluate :934、bm_sample :954、bm_albedos :989）。**光谱运行时**九组 `mdl_rgb_to_spectral_*`（ior :1058、reflectance :1076、luminance :1094，各带 _deriv 变体）与 `mdl_get_wavelengths()`（:1130）全部委托 spectral 库的 rgb_to_spectral 模板（`<false>`/`<true>` 区分反射率/亮度语义）。

**Baker** 三层结构。`Baker_fragmented_job`（baker.cpp:110，`final : DB::Fragmented_job`）是 CPU 采样工作单元：纹理按行分片，`MAX_FRAGMENT=256`（:188），每片记录"像素是否全等"与首像素颜色（:190/:192），跨片一致性比较用 `m_epsilon=1e-7f`（:195，注释明言对齐 GPU 阈值）。`Baker_code_impl`（:426）持 GPU/CPU 双份 target code（:446/:455）。`Baker_module_impl`（:469 起）是模块单例：`create_baker_code_internal()`（:591）做类型→像素格式映射（TK_FLOAT→"Float32"、TK_COLOR→"Rgb_fp"、TK_VECTOR 按分量→Float32<2/3/4>，:617-655）；`bake_texture_internal()`（:955）是执行主入口。

## 3. 外部连接

- **JIT 编译器契约**：`mi::mdl::IResource_handler` 纯虚接口——每个方法对应 codegen 可能发出的一个外部调用点。
- **scene 元素层**：Texture_2d/3d 等包装类（`i_mdlrt_texture.h` 等，mdlrt_resource_handler.cpp:36-38）内部经 `DB::Access` 取 `TEXTURE::Texture`；`i_spectral.h`（:40）提供光谱转换核。
- **DB 调度**：Baker 复用 dblight 的 fragmented job 机制——`transaction->execute_fragmented(&job, ...)`（baker.cpp:1028），分片自动铺满线程池。
- **backends 层**：PTX 后端编译选项 `tex_lookup_call_mode=vtable` + `num_texture_results=0`（baker.cpp:748-749，注释 :741-747 解释：OSS GPU baker 的设备侧纹理运行时走 vtable 派发、不接受预计算结果数组）。
- **CUDA 可选**：`ENABLE_GPU_BAKING_OSS` 开关（baker.cpp:32-33、:66-72）映射 CMake `MDL_ENABLE_GPU_BAKER`；GPU 路径在 baker_cuda_oss.cpp(744 行)/baker_kernel_oss.cu(289 行)，经 CUDA driver API 加载（ensure_cuda_loaded_oss :518）。
- **公共 API**：distiller API 实现是唯一上游消费者（neuray_mdl_distiller_api_impl.cpp:441-447）。

## 4. 数据流

**烘焙主流程**：create_baker_code_internal（baker.cpp:591）先 `lookup_sub_expression` 找 path 子表达式（:608-613）定 pixel_type；随后双路生成 target code——GPU 路 PTX（:741 起），CPU 路 LLVM lambda。bake_texture_internal（:955）先查 uniform 短路（:972-976 直接 `bake_constant()` :1046）；GPU 可用则 GPU 路并回读（:991）；否则 CPU 路（:1024-1028）：构造 job → execute_fragmented 并行分片 → 常数检测 `are_all_pixels_equal()`（:1031→:140）判全等，全等则 `set_constant_from_canvas()`（:912）取 (0,0) 像素当常数返回。

**每像素采样**：execute_fragment（baker.cpp:291）按片起止行循环；每像素 `m_num_samples` 次抖动采样，偏移来自**radical inverse 序列** `radinv2(k)`（:92-100 位反转）与 `(float)k*inv_spp`（:331-335）；environment 模式把 UV 映射球面方向 `from_polar`（:82-90、:337-340）调 `execute_environment`（:341）；普通模式 `BAKER_STATE_POSITION_DIRECTION` 时位置走球面、否则 UV 平面填 tex_coords（:345-356）调 `execute`（:355）。NaN 清零（:365-368）；Sint8（bool）目标专门 lift：裸字节抬成 0/1 再平均（:370-374），阈值"过半数投票"（:386），与 GPU 路径对齐。

**运行时资源流**：JIT 代码遇 `tex::lookup_color2d(...)` → 经 vtable 进 `tex_lookup_color_2d`（mdlrt_resource_handler.cpp:542）→ reinterpret 成 `Texture_2d const*` → mipmap 采样落 `TEXTURE::Texture` 元素。tag 解引用只在 tex_init 发生一次。

## 5. 设计决策

- **placement new 而非虚接口对象**：JIT 侧只拿裸缓冲 + vtable 回调，避免跨编译边界传 C++ 对象布局——get_data_size 取六 struct 最大值让单一缓冲适配所有资源类型（mdlrt_resource_handler.cpp:45-59）。
- **derivatives 显式分叉**：构造参数 use_derivatives（backends_target_code.cpp:200）+ 每个 _deriv 独立回调（mdlrt_resource_handler.cpp:1067 起），无导数时零开销。
- **CPU/GPU 双实现 + 常数短路**：uniform 材质不进采样循环直接 bake_constant（baker.cpp:972）；GPU 失败自动回落 CPU（:756-760）；常数检测靠碎片 job 首像素比较（:140-163），ε 与 GPU 对齐（:193-195 注释）——同一语义三处复刻。
- **radical inverse 抖动**：radinv2（baker.cpp:92）是低差异序列最便宜的实现（整数位反转），比 Sobol 少依赖、比白噪声方差低，离线烘焙够用。
- **PTX vtable 模式为兼容开源纹理运行时**：baker.cpp:741-747 注释坦承这是为 OSS 版 device 侧 texture_support_cuda.h 接口形状的妥协。
- **光谱转换集中托管**：九组回调收敛到 spectral 库模板（仅模板参数不同，mdlrt_resource_handler.cpp:1058-1128），JIT 只管分派不管数值。

## 6. 新人提示

- 调纹理不生效先查两头：tag 是否真在 tex_init（mdlrt_resource_handler.cpp:61）被正确 resolve（ctx 必须是活事务指针）；构造失败会静默成空查找。
- 加新资源类型须同步三处：get_data_size 最大值、tex_init/tex_term 的 switch、对应 lookup 回调；漏第一处会越界。
- baker 的 Sint8 路径（baker.cpp:370-386）是 bool 材质特殊通道，改阈值逻辑时 CPU（多数投票）与 GPU（kernel 内）要一起动。
- 常数检测的 1e-7f 是跨 CPU/GPU 契约值（baker.cpp:195），单边改动会造成两路结果分叉。
- GPU baker 默认不编（ENABLE_GPU_BAKING_OSS 由 CMake MDL_ENABLE_GPU_BAKER 控制），#ifdef 块内行号在其他构建里不存在。
- `execute_fragment` 的行分片公式（baker.cpp:295-301）把余数行摊给前几片，改分片数时别破坏行连续覆盖。
- Resource_handler 方法全 const 且无锁——线程安全完全依赖 Texture_* 包装类；在那层加缓存前先确认单线程语义。

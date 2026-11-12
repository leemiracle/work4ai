# NVIDIA MDL-SDK 新人上手文档

基于知识图谱（10933 节点/18596 边，commit `1b9592c`，2026.0.2）撰写，`路径:行号` 锚均经源码核实。

## 一、这是什么：物理材质 DSL 的全家桶

MDL（Material Definition Language）是 NVIDIA 的**物理材质领域专用语言**：声明式 material 定义 + 过程式函数（README.md:38），也是行业材质交换标准（vMaterials 等按此分发）。本仓是官方开源 C++ SDK（README.md:105）：

- **编译器前端**（src/mdl/compiler/compilercore）+ `.mdl` 内置标准库（src/mdl/compiler/stdmodule）；
- **代码生成双线**：DAG（generator_dag）→ LLVM JIT（PTX/IR/本机码）与 GLSL/HLSL 源码；无 LLVM 桩（src/mdl/no_jit/generator_stub/generator_stub.cpp:39）；
- **distiller**：材质→后端目标模型规则变换（README.md:137）；
- **BSDF 运行时**：1.1 万行手写设备侧物理库（src/mdl/jit/libbsdf/libbsdf.cpp:649 起 Fresnel 族）；
- **周边**：图像 IO、baker、neuraylib 服务端（src/api/api）、CLI（src/prod/bin）、30 余示例。


## 二、构建与目录地图

强制 vcpkg 工具链（CMakeLists.txt:56），依赖钉在 vcpkg.json，vcpkg commit 亦钉死（INSTALL.md:31）。子树挂载 CMakeLists.txt:132（include）、CMakeLists.txt:137（api）、CMakeLists.txt:138（base）、CMakeLists.txt:139（mdl）、CMakeLists.txt:140（io）、CMakeLists.txt:141（render）、CMakeLists.txt:142（prod）、CMakeLists.txt:143（shaders）。

| 目录 | 职责 |
|------|------|
| `include/` | 全部公共头（mi/base、mi/math、mi/mdl、mi/neuraylib），唯一契约层 |
| `src/base` | 跨平台底座：hal、system、data（dblight/序列化/线程池）、lib（vendored zlib/libzip） |
| `src/mdl` | compiler（compilercore+stdmodule+glsl/hlsl+coco）、codegenerators、jit、no_jit、distiller、runtime、integration |
| `src/io` | image（像素格式插件）+ scene（mdl_elements 数据库元素） |
| `src/render`、`src/shaders` | backends 目标码装配 + baker 烘焙；图像插件样例 + 内嵌 base.mdl 标准库 |
| `src/api`、`src/prod` | 公共接口服务端实现；CLI 与 libneuray/集成库 |
| `examples/`、`doc/` | mdl_sdk/mdl_core/mdl_python 示例；Doxygen 文档源 |

条件挂载：thirdparty（CMakeLists.txt:150）、optix7 嵌套于 CUDA 分支（CMakeLists.txt:200）。

## 三、公共 API 面：include/mi 双面貌

**mi::neuraylib——集成者主 API**，barrel 头 include/mi/mdl_sdk.h（include/mi/mdl_sdk.h:79 imdl_backend_api、include/mi/mdl_sdk.h:88 imdl_factory、include/mi/mdl_sdk.h:96 ineuray）。用法：INeuray（include/mi/neuraylib/ineuray.h:67）start→get_api_component→事务（include/mi/neuraylib/itransaction.h:116）→shutdown；生成码出口 IMdl_backend_api（include/mi/neuraylib/imdl_backend_api.h:79）/IBackend（include/mi/neuraylib/imdl_backend_api.h:41）。

**mi::mdl——编译器接口**（mdl_core 直连）。IMDL（include/mi/mdl/mdl_mdl.h:114）装载入口 include/mi/mdl/mdl_mdl.h:235 load_module、include/mi/mdl/mdl_mdl.h:254 from_string、include/mi/mdl/mdl_mdl.h:274 from_stream；结果 IModule（include/mi/mdl/mdl_modules.h:172）。类型契约 IType 族 39 子接口（include/mi/mdl/mdl_types.h:45）。

**ABI 基石**：接口继承 IInterface（include/mi/base/iinterface.h:61），生命周期用侵入式 Handle（include/mi/base/handle.h:135，retain 在 include/mi/base/handle.h:186）。无 STL 指针全是 `Handle<I>`，版本靠 Uuid 链。

## 四、编译器核心链路：源码到目标码

**① compilercore 前端**：1.9 万行语义分析 Analysis（compilercore_analysis.cpp:2187 起，类型检查/常量折叠/重载解析）；模块装载（compilercore_modules.cpp:197）；搜索路径 File_resolver（compilercore_file_resolution.cpp:493）。

**② stdmodule 标准库**：std.mdl:30 起 `export using` 聚合 anno/math/tex/df；BSDF 标准型 df.mdl:47（diffuse_reflection_bsdf）、df.mdl:169（microfacet_ggx_smith_bsdf）；纹理 tex.mdl:44。

**③ generator_dag：AST→DAG**。DAG_builder（generator_dag_builder.cpp:1298）做内联/CSE；结果容器 Generated_code_dag（generator_dag_generated_dag.cpp:76 起）是全后端共享 IR。

**④ generator_jit：DAG→LLVM→目标码**。MDL_JIT（generator_jit_llvm.cpp:355）产 IR 并 JIT（generator_jit_llvm.cpp:657 入口、generator_jit_llvm.cpp:10493 编排）。分布函数物理求值不进 LLVM，链到 **libbsdf**（src/mdl/jit/libbsdf/libbsdf.cpp，11031 行）。

**⑤ compiler_glsl/compiler_hlsl：着色语言出口**。各有一套前端把 DAG 物化为 shader 源码；访问者骨架 compiler_glsl_visitor.cpp:91、compiler_hlsl_visitor.cpp:41。**coco**（src/mdl/compiler/coco/，Coco/R）是扫描器/LL(1) 运行时（Tab.cpp:42），mdltlc 的 .atg 文法复用。

## 五、distiller 蒸馏子系统

把任意复杂材质压平成单一 BSDF+EDF 近似供受限后端消费。

**接口** i_dist.h：Dist_module（i_dist.h:52）定义 distill()（i_dist.h:67 注释、i_dist.h:86 声明）。前置 i_dist.h:71：先加载 `::nvidia::distilling_support`（examples/mdl/nvidia/distilling_support.mdl）。

**调度** dist.cpp：distill()（dist.cpp:47）两路——内建目标 **"none" 直通**（dist.cpp:63 分支、dist.cpp:64 注释）；其余查注册表（dist.cpp:68），经 create_distiller_plugin_api（dist.cpp:78）委派插件（dist.cpp:79）。

**DSO 插件机制**：`Module_registration<Dist_module_impl>(M_DIST,"DIST")`（dist_module_impl.cpp:124）；init() 遍历 PLUG 描述符登记全部蒸馏目标（重名拒绝）；Forwarding_logger（dist_module_impl.cpp:73）。插件实现 mdl_distiller_plugin_api.h 规则/匹配/后置条件契约。

**mdltlc 工具**（src/prod/bin/mdltlc/）：MDLTL 模板→C++ 匹配代码。解析器 mdltlc_parser_rd.cpp + 生成器 mdltlc_codegen.cpp，入口 main.cpp:96，文法 mdltlc.atg，Compiler 在 mdltlc_compiler.h:84。

## 六、运行时与支撑

**dblight**（src/base/data/dblight/）：自研 MVCC 内存事务引擎，Transaction_impl（dblight_transaction.cpp:54）管存取/可见性/journal。**io**：image 插件化接像素格式；mdl_elements 是 MDL 在数据库里的家（模块/材质/compiled material 皆数据库元素，mdl_elements_module.cpp 2337 行；工具集 mdl_elements_utilities.cpp:825 起）。**render**：backends 装配目标码（PTX 后端 SM 协商 backends_backends.h:158）；baker 烘焙子表达式（i_baker.h:66、i_baker.h:82）。**集成**：src/api/api/neuray 实现公共契约（neuray_transaction_impl.cpp:111 commit、neuray_transaction_impl.cpp:210 access）；mdlnr 桥注册名是 **MDLC**（mdlnr.cpp:186；i_mdlnr.h:77 定义 DAG 序列化对）。

## 七、示例群导读：三条路线

**mdl_sdk——集成主线（30+）**：start_shutdown→modules→instantiation→calls→compilation→code_gen 六步走完工作流；execution_native/cuda/glsl/glsl_vk 四后端对照（example_execution_glsl.cpp:709）；**dxr 最完整**（D3D12 路径追踪含 glTF，example_dxr.cpp 2755 行）；optix7 内联 PTX 进 OptiX 7（optix7_mdl_closest_hit_radiance.cu）；distilling 系列含自定义目标插件（example_distilling_unity.cpp:512）；axf_to_mdl 与 mdl_browser（Qt）。

**mdl_core——编译器直连**：不经 neuraylib 直接用 mi::mdl；example_shared.h:381 起自带编译管线，df_native/df_cuda/df_vulkan 直接编译执行 BSDF。

**mdl_python——绑定路线**：pymdlsdk + start_shutdown/pymdl_inspection 示例。

## 八、新人陷阱与勘误（全部实证）

1. **src/api/api/ 双层是真实路径非笔误**：`ls src/api/api/` 实证只有 mdl、neuray 两子目录——外层是 CMake 挂载点（CMakeLists.txt:137），内层按命名空间分组实现。别当 typo"修复"。

2. **编译器两处"多一层"**：BSDF 库在 **src/mdl/jit/libbsdf/**（同层还有 devlib/libdevice/libmdlrt/llvm）；前端在 **src/mdl/compiler/compilercore/**（compiler/ 下并排 coco/glsl/hlsl/stdmodule）；generator_dag/generator_code 却在 **src/mdl/codegenerators/**——三套生成器分住三个目录，勿按名猜路。

3. **shared 近似副本对共 4 组**（mdl_sdk/shared vs mdl_core/shared）：example_cuda_shared.h（diff 2037 行）、example_shared.h（1424）、texture_support_native.h（614）、example_vulkan_shared.h（76，最接近）。**勘误**："vulkan 版仅版权行差异"不严格成立：examples/mdl_sdk/shared/example_vulkan_shared.h:2（版权年份）与 examples/mdl_sdk/shared/example_vulkan_shared.h:29（路径注释）之外，mdl_sdk 版是 Vulkan_example_app 持三个 neuray 句柄、mdl_core 版是 Vulkan_base_app 零 neuray 依赖。同源分叉，改一处须评估另一处。

4. **examples/mdl/nvidia/ 不只 .mdl**：core_definitions.mdl（4855 行）与 distilling_support.mdl 之外，core_definitions_de.xlf/core_definitions_fr.xlf 本地化（配套 src/prod/bin/i18n 与 src/mdl/integration/i18n）及 axf_importer/、sdk_examples/ 子目录易漏看。

5. **dblight dump 是测试期望快照（生成物）**：图谱收录的 267 个 txt/css/bat 轻资产中 **75 个 `*.dump.txt` 全在 src/base/data/dblight/data/**（ls 实证），系单测期望状态（src/base/data/dblight/data/test_transaction_access.dump.txt:1 起计数行供回归比对），测试进程生成非手写。

6. **distiller 接口在 src/mdl/distiller/dist/（双层 dist）**：i_dist.h 等三文件均在 dist/ 子目录，曾被依赖扫描漏掉（图谱补录批 109 修复）；补录后全仓核实，dist 接口**唯一外部消费者是 src/api/api/neuray/neuray_mdl_distiller_api_impl.cpp**——neuray_mdl_distiller_api_impl.cpp:43 的 `#include <mdl/distiller/dist/i_dist.h>` 是唯一桥（grep 全仓实证）。

7. **mdlnr 目录名 ≠ 模块名**：src/mdl/integration/mdlnr/ 注册的是 Mdlc_module/M_MDLC（mdlnr.cpp:186）；neuray 里没有叫 MDLNR 的模块。

8. **标准库两大件**：stdmodule 之外，src/shaders/mdl/base/base.mdl（5879 行）是 neuray 侧 ::base:: 权威实现。找 base 函数别只盯 stdmodule。

9. **distill 的 "none" 直通**（dist.cpp:63）：真实目标全部来自插件注册；调试蒸馏管线可先用 none 验证接线。

10. **构建强绑 vcpkg**：CMakeLists.txt:56 无工具链直接 FATAL_ERROR，且 INSTALL.md:31 钉 vcpkg commit（9d7f79f）——版本漂移是构建失败第一嫌疑人。

---

字数口径：不计空格字符
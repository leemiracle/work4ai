# 讲透 MDL-SDK

> NVIDIA MDL SDK 2026.0.2（@1b9592c）——**Material Definition Language 全家**：物理材质 DSL 编译器（compilercore）+ stdmodule/libbsdf 标准库 + DAG/JIT/Code/Stub 四代码生成器 + GLSL/HLSL 后端 + **distiller 蒸馏**（通用材质→渲染后端目标模型）+ dblight 内存数据库 + io/render/baker + neuray 集成 API + mdltlc 规则语言编译器 + OptiX/DXR/Qt 示例群。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| understand 图谱 | ✅ 2026-11-11 | 仓内 `.understand-anything/knowledge-graph.json`：**10932n/18596e/16 层/16 步 tour**，双 validate 0/0，fingerprints 2513@1b9592c1 |
| onboarding | ✅ 2026-11-11 | `onboarding/ONBOARDING.md`（8 节 6946 字不计空格，78 锚全验） |
| explain 12 篇 | ✅ 2026-11-11 | `explain/01-12` 合计 **56492 字符**，712 锚（两组写手，主会话抽验 8/8 命中含 4 处自我修正后锚） |

## 战况（108 批 + 3 补录批，跨两夜三段断点续跑）

108 主批四 worker 大段滚动；本夜复活续跑发现批阶段实际已 100% 完成，直接进入 merge。**三处覆盖率缺口全部手术修复**：①`src/mdl/distiller/` 整目录 5 文件 scanner 漏扫→补录批 109 真分析（17n/46e，distiller 接口+DSO 插件注册表全入图）；②scan 2513−配批 2246=**267 个轻资产**（235 txt+13 md+19 web/脚本）从未配批→补录批 110（267 节点 1:1 对账，147 CMakeLists 全量+75 dblight dump 族+17 族定性）；③mdl_sdk vulkan 副本类未提取→批 111 克隆，后经 onboard 写手甄别**反转修正**（见勘误 1）。merge 终态悬空 0、覆盖审计 2518/2518 零缺零溢。

## 甄别精选（源码级实证，12 条）

1. **mdl_sdk/shared 与 mdl_core/shared 的 vulkan 头并非副本**：76 行实差——mdl_sdk 版 `Vulkan_example_app`（L126，持 3 个 neuray 句柄）vs mdl_core 版 `Vulkan_base_app`（L128，零依赖）；原批工人把继承目标误写成 Vulkan_base_app，图谱手术后终态正确
2. **libbsdf 为何在 jit/ 下**：它不是宿主库而是 JIT 后端的"源码级标准库"——CMake（libbsdf/CMakeLists.txt:39-64）用 clang 编出 24 个 LLVM bitcode 变体（6 handle-slot 模式×debug×spectral），generator_jit_libbsdf.cpp:42-50 以字节数组头内嵌，BSDF_API=extern "C" 占位符号在 DF instantiation 时替换
3. **src/api/api/ 双层目录成因**：target 名 `api-api-mdl`（api/api/mdl/CMakeLists.txt:30）=NVIDIA ARC 内部构建系统"路径即目标名"约定的化石；src/api/CMakeLists.txt 是 2023 开源新增薄壳
4. **distiller 分派**：dist.cpp:63-66 "none" 是唯一 builtin target（直通 retain 不 clone）；其余目标经双索引 map 路由到 DSO 插件；API 版本硬门禁+重名 target 拒绝注册
5. **mdltlc 定性实证**：MDLTL=DAG 重写规则语言（真实用例 src/shaders/plugin/mdl_distiller/dist_rules.mdltl:30 `rules Reduce_1_4_to_1_3_rules topdown`）；**Coco/R 与手写 RD 双解析器并行跑、逐节点比对 AST**（mdltlc_compilation_unit.cpp:231 coco→:245 comparison_unit→:275 compare_asts）——生成器迁移期的自校验设计
6. **dblight 是 API 层唯一 DB 后端**（mdl_neuray_impl.cpp:244 DBLIGHT::factory）；75 个 *.dump=单测期望状态快照（Test_db RAII+diff -u+approval cp 工作流）
7. mdl_elements 三层翻译（core/int/ext）+%XX 转义 DB 名（%3C0%3E）；Module_cache+wait_queue 单线程加载不变式
8. mdltlc 的 `--plugin` 是 legacy ignored 选项；dump 快照 approval 的 cp 方向=期望→实际
9. OptiX7 示例 dual 模式：direct call（5 callable+__direct_callable__ 前缀）vs renderer module 链接；代码字符串级 OptiX program cache
10. mdl_browser 的 IMdl_cache 四类层次+locale 不一致即整体弃用重建；MaterialX 桥资源解析失败走丢弃降级
11. mdlnr 注册的模块实名 MDLC（mdlnr.cpp:186）；examples/mdl/nvidia/ 有 .xlf 本地化与 core_definitions.mdl
12. **配批缺口新坑钉版**：scan-result 文件数（2513）≠ batches.json exportsByPath（2246）——267 个 txt/md/css/bat/sh/json 被配批算法静默跳过；开工 merge 前必须对账 scan−ebp 差集，补录批收纳

## 分层速览（16 层，2544 文件级节点）

构建体系 → include 公共 API(169) → base 基础（平台/数据结构/三方）→ compilercore(122) → DAG/JIT/蒸馏生成器 → GLSL/HLSL/CoCo → IO(image/scene) → render → neuray API(108) → CLI 工具（mdltlc 等）→ neuray 库/测试 → 示例群 → 文档站点

*2026-11-11 · cuda-stack-第七轮会话（舰队夜战 · 四大专项收官之战）*

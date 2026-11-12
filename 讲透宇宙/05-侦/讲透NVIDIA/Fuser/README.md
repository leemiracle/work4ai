# 讲透 NVIDIA Fuser（nvFuser）

> 仓库：`NVIDIA/Fuser` @ `5198f114`（Symmetric memory pytorch backends #6023，快照 2026-11-07）。
> 定位：PyTorch 生态的运行时 Fusion 代码生成编译器（Python Fusion Definition → Fusion IR → 调度 → CUDA 源码 → NVRTC 即时编译执行）。

## 一、流水线状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| DeepWiki 抓取 | ✅ 28 文件（22 内容页+索引校验） | `deepwiki/`（1-overview ~ 6.2 全层级页） |
| understand 图谱 | ✅ 1958 节点 / 5555 边 / 14 层 / 16 步导览 / validator 0 issues / fingerprints 752 文件 @ `5198f114` | 仓内 `.understand-anything/knowledge-graph.json` |
| 批阶段甄别 | ✅ 38 条 NOTES（NOTES-DIGEST.md） | 仓内 `.understand-anything/NOTES-DIGEST.md` |
| ONBOARDING | ✅ 9 节（~万字级，行号锚全源码核实） | `onboarding/ONBOARDING.md` |
| explain 精讲 | ✅ 8/12 落盘；03-06 组 1 并行产出中 | `explain/`（见下表） |

## 二、explain 索引（六节结构：角色定位/内部结构/外部连接/数据流/设计决策/新人提示）

| 篇 | 文件 | 主题线 | 字符（不计空格）/行号锚 |
|---|---|---|---|
| 01 | `explain/01-IR三根继承树.md` | 核心线：Statement/Val/Expr 三根 | 2759 / 25 |
| 02 | `explain/02-TensorView与interface.md` | 核心线：TensorView 与 interface 节点 | 3078 / 35 |
| 03-06 | （组 1 并行实例产出中） | 核心线：遍历求值 / IdModel / 调度器 | — |
| 07 | `explain/07-preseg与分段器.md` | 执行线：PreSegmenter 20-pass 总驱动+5042 行分段器 | 3556 / 38 |
| 08 | `explain/08-GpuLower与pass链.md` | 执行线：analysis+23-pass 表，unroll.h 谓词钉版 | 3421 / 31 |
| 09 | `explain/09-codegen与NVRTC执行.md` | 执行线：codegen.cpp 11 实体+156 行 compile 全链+kernel_db | 3761 / 27 |
| 10 | `explain/10-runtime设备库与cuda_p2p.md` | 生态线：43 个 .cu 设备库+stringify 链+绕 NCCL 通信 | 3243 / 19 |
| 11 | `explain/11-HostIR与多层CUTLASS.md` | 生态线：HostIrJit Pimpl+LLVM ORC+CUTLASS 三层 | 3501 / 23 |
| 12 | `explain/12-Python前端与工具链.md` | 生态线：nvfuser_direct/DTensor/pybind 235 处/codediff | 3349 / 32 |

入口建议：先读 `onboarding/ONBOARDING.md` 第 1-2 节建全局图景 → 按兴趣选 explain（编译主线 07→08→09，多设备与生态 10→11，前端 12）→ 14 层/16 步导览在图谱 JSON 内对照。

## 三、勘误清单（12 条，全部本快照源码核实）

1. **三层（实为四处）CUTLASS 实体同名不同物**：仓根 `cutlass/`=手写封装层，CMake 编成共享库 libnvf_cutlass.so（`cutlass/CMakeLists.txt:31`）；`csrc/cutlass/`=运行时代码生成层，以 R"(...)" 字符串拼 C++（`csrc/cutlass/gemm.cpp:164` 起 19 处）；`third_party/cutlass/`=外部 submodule（本快照未 checkout，目录空壳非克隆损坏）；另有第四易混实体 `csrc/scheduler/cutlass.cpp:66` 的 CutlassScheduler（2025 新，默认关闭 `cutlass.cpp:71`）。
2. **transpose_tma.cpp 是显式 stub**：`getTransposeHeuristics` 直接 `return nullptr`（`csrc/scheduler/transpose_tma.cpp:24`），`scheduleTranspose` 为 NVF_THROW（`:28`）——仓库内罕见的自曝式未完成接口，别当可用调度器引用。
3. **tools 双份拷贝**：`tools/gen_nvfuser_version.py` 与 `python/tools/` 同名文件 md5 一致（d8b8298e…），`tools/memory.py` 同（0160a3fc…）——修改必须双写，否则 Python 包内版本漂移。
4. **分片守恒断言的边界**：`validateDisjoint`（`csrc/fusion_segmenter.cpp:4912`）只在 `#ifndef NDEBUG` 下经 `validateIfDebug`（`:2684`）生效，且收尾调用显式放宽 `require_disjoint=false`（`:4006`）——转发输入让 unary expr 合法跨组共享，Release 版完全无此校验。
5. **宏前缀类全盲**：`runtime/casts.cu` 的 81 处宏实例化（NAIVE 39+FROM_TEMPLATE 27+VEC2 12+VEC4 3，宏定义 `casts.cu:12/34/50`）对 tree-sitter 不可见，图谱仅手扫 file 节点。
6. **.cu 文件全盲**：runtime/ 43 个 .cu 零提取，图谱 43 file+18 function 节点全部手扫补齐（.cu 是 C++ 工具链的断代盲区）。
7. **重载函数折叠单节点**：`SegmentCandidateFinder::segment` 三个重载（`fusion_segmenter.cpp:1612/1621/1634`）在图谱中是一个 function 节点；`tryMerge` 两重载（`:2137/2160`）同理——引用行号前必须亲验。
8. **unroll.h 谓词钉版**：「A bit deceptively: UnrollPass adds all predicates, so it needs to be run even if we don't unroll any loops」（`csrc/device_lower/pass/unroll.h:26-28`）——谓词插入的真家在 UnrollPass，不是 predicate.cpp。
9. **SegmenterSet 双阶段生命周期**：分段器检测（`fusion_segmenter.cpp:1665`）→ lower 前被 `segmenterHintCleanup` 还原为普通 Set（`lower2device.cpp:151-153`）——该"算子"只是提示标记，非真实语义算子。
10. **documentation.h 不参与编译**：文件首部 `#error`（`csrc/docs/documentation.h`）使其只在 doxygen 文档生成时被解析。
11. **`csrc/C++23/` 是特殊文件名兼容路径**（含 `+` 的目录），仅作兼容 include 目标存在，无实现。
12. **.inl 后缀双漏**：`csrc/struct.inl` 被 scanner 与 tree-sitter 双双漏扫（imports 亦漏），结构手工补齐。

**未复现项**：任务清单中的「include_next 自环」在本快照全仓（.h/.cpp/.cu 及 .understand-anything 产物）`include_next` 0 命中、最终图谱自环边 0 条——如实报告为未复现，若指扫描期中间态需另行核验。

## 四、图谱消费提示

- 三大盲区（模板头文件/.cu/宏前缀）节点为手扫产物，行号锚可信但函数粒度不全；查询优先 file 节点 summary。
- 边分布：imports 3141 / contains 1194 / exports 1011 / inherits 184——继承边稀疏是模板盲区的直接后果，IR 继承树请以 `explain/01` 与源码为准。

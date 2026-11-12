# 讲透 NVIDIA/jitify

NVIDIA header-only CUDA 运行时编译库：单头 `jitify.hpp` 把 NVRTC 封装为 `JitCache→Program→Kernel→KernelInstantiation→KernelLauncher` 流式 API，支持内嵌字符串/磁盘文件/回调虚拟/链接器嵌入四类源码。

## 全链状态表

| 产物 | 状态 | 位置 |
|---|---|---|
| DeepWiki 全量 | ✅ TRUE_100 | `deepwiki/` |
| understand 图谱 | ✅ 67n/78e/4 层/6 步 tour，0 issues，fingerprints 15 文件 @ e0a37a6c | 仓内 `.understand-anything/knowledge-graph.json` |
| ONBOARDING | ✅ 6 节 / 65 行号锚（任务书 6 节 20 锚超额） | `onboarding/ONBOARDING.md` |
| explain | ✅ 2 篇（单头库本体 / 构建侧双世界） | `explain/01-…md` `explain/02-…md` |
| NOTES-DIGEST | ✅ 8 条 | 仓内 `.understand-anything/NOTES-DIGEST.md` |

## 源码级勘误清单（5 条，行号实证 @ e0a37a6c）

1. **两代同名类被图谱合并**：`jitify.hpp` 实有 **8 个**公开句柄类——classic 层 `KernelLauncher:3176`/`KernelInstantiation:3244`/`Kernel:3392`/`Program:3457` + `jitify::experimental::serialization`（`:3927-3931` 开命名空间）内同名四类 `Program:4071`/`Kernel:4174`/`KernelInstantiation:4229`/`KernelLauncher:4419`（支持 PTX+链接文件落盘重建）。图谱 13 个 class 节点中这四个名字各只一个节点，"可序列化 API"一层的存在被合并吞掉；`jitify_test.cu:133/278/456` 的 `*_experimental` 用例证明两代并存。
2. **README 平台/版本声明强于构建现实**：`README.md:51` 称"CUDA 7.0, 7.5, 8.0, 9.x, 10.x, Linux and Windows"，但 `Makefile:25-34` 只有 Linux/Darwin 分支无 Windows 目标；链接器嵌入技巧注释明示 "only supported by gcc on Linux"（`Makefile:27`）；README 的 Windows 构建实际只有 CMake/get-deps 路径。
3. **.jit 是构建产物非源码**：`example_headers/` 下无任何 `.jit` 入库（ls 实证），`jitify_example.cpp:45` include 的 `my_header1.cuh.jit` 由 `Makefile:50-51` 的 `%.jit: % stringify` 规则生成——克隆后跳过 make 直接编译 example 必失败；把 .jit 当仓库文件引用的文档/图谱边是构建期视角。
4. **cuda/std include 位置极易误读**：`jitify.hpp:1439-1442`、`:1998-2001` 的 `#include <cuda/std/…>` 全部位于 `jitsafe_header_limits_h`（`:1437` 起 `R"(`）等原始字符串**内部**，是给 JIT 侧探测 libcu++ 的垫片内容，不是本文件的宿主依赖——grep 会产生大量假命中。
5. **构建即测试的非典型结构**：`Makefile:56-58` 的 nvrtc_cli 目标在链接完成后自动执行 `bash nvrtc_cli_test.sh`（断言链失败即中止构建）；而 `jitify_test.cu` 的 26 个 `TEST(JitifyTest, …)` 用例对 tree-sitter 全盲（TEST 宏展开零提取，图谱用例结构为手扫补充）——测试覆盖的真相以源码 grep 为准，图谱 contains 边不含它们。

## 快速上手

`make` 一发入魂（先决：CUDA 工具链；gtest 需 `make get-deps` + `Makefile:66-71` 拉 googletest release-1.12.1）。读代码顺序：`README.md` Quick example → `jitify_example.cpp` 的 test_* 函数序列（`:40-42` 三个 JITIFY_PRINT_* 调试宏）→ `jitify.hpp` 按 detail 工具/jitsafe 垫片/impl/公开层四段纵切。

## 深讲入口

- 单头库内部结构与编译数据流：`explain/01` 第 4 节
- .jit 双世界/链接器嵌入/stringify：`explain/02`
- 图谱导览：`.understand-anything/onboard-input.json`（4 层/6 步 tour）

# 讲透 NVIDIA/cutlass（CUTLASS 4.8.0）

CUTLASS：NVIDIA GPU kernel 模板库三件套——C++ CuTe 布局代数与 collective 组件、CuTeDSL Python 编译栈（PyIR→cute MLIR→LLVM）、cutlass_compiler/cutegen C++ MLIR 编译器后端。本目录是 understand 流水线知识库产物索引。

## 状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| deepwiki | ✅ 2026-10-26 | `deepwiki/`（71 页 898,631 字符，MCP 通道 TRUE_100） |
| understand 图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`：**9311 节点 / 20737 边 / 16 层 / 16 步 tour / 0 issues / fingerprints 1911 文件 @0b55a2f6**；批阶段甄别笔记收割 `NOTES-DIGEST.md`（259 条） |
| onboarding | ✅ 并行实例（2026-11-06 落盘） | `onboarding/ONBOARDING.md`（图谱基线 9311n/20737e/16L/16T 行号锚逐条核实） |
| explain 组 1（篇 1-6）：✅ 12/12 篇全落盘，锚抽验 14/14 全好 并行实例进行中 | 01-CuTe核心代数 / 02-GEMM-kernel与device层 / 03-CollectiveBuilder与collective层 / 04-SM90-atom动物园 / 06-Convolution与transform支撑 已落盘，05 待落 |
| explain 组 2（07-12：Python 世代+工具链） | ✅ 本轮 | 见下 |

## explain 索引（组 2 · Python 世代+工具链，2026-11-06）

| 篇 | 文件 | 主题 | 字符（不计空格）/行号锚 |
|---|---|---|---|
| 07 | [07-CuTeDSL运行时.md](explain/07-CuTeDSL运行时.md) | base_dsl 基型（Int32/Int64/Param/CallProvider/AuxRuntimeFunc）+jit_executor 类层次+runtime/ 子包+experimental 流水线 | 3496 / 33 |
| 08 | [08-PyIR编译器栈.md](explain/08-PyIR编译器栈.md) | pyir_runtime 六层链 facade（state→core→corewalk→loop_carry→entrypoints→call_boundary）+ _mlir_helpers 加固层+scheduler._mlir 运行时注入 | 3481 / 18 |
| 09 | [09-operators库.md](explain/09-operators库.md) | fusion DAG IR（compute/load/store nodes）+EVTPassManager 十 pass+pycute vendored 分叉+rubin kernel | 3489 / 20 |
| 10 | [10-cutlass_compiler与cutegen.md](explain/10-cutlass_compiler与cutegen.md) | base 伪方言/cute_ir 方言/三 MlirOptMain 工具+cutegen 17 头+347 测试面+LLVM.cmake 依赖链 | ~3500 / 16 |
| 11 | [11-generator代码生成器.md](explain/11-generator代码生成器.md) | 13092 行单文件：__main__ L13035 无 main()、12 代际旗舰、shapes×3 纯数据表、Manifest 发射器 | 3531 / 39 |
| 12 | [12-构建链与文档产物.md](explain/12-构建链与文档产物.md) | 根 CMakeLists/cmake 七件/Python 四包发布载荷/Sphinx 化石层与 nblink 断链 | 3496 / 16 |

字数口径：不计空格总字符（组 2 全部落在 2000-3500 区间）；行号锚格式 `文件:行号`，全部主会话源码核实。

## 勘误清单（源码级实证，≥10 条）

1. **ElementAMmaccumulator 笔误全量 15 处**：`include/cutlass/gemm/collective/builders/sm107_common.inl` 5 处（:47/:73/:91/:126/:141）+`sm100_common.inl` 10 处，应为 ElementAccumulator（与 ElementAMma 相邻致误）。注意 NOTES-DIGEST 的"sm107 ×7"是批阶段口径，全量 grep 实数如上。
2. **arch simd 三头零引用死代码**：`include/cutlass/arch/simd.h`/`simd_sm60.h`/`simd_sm61.h` 在 include/examples/tools/test 全域 `#include "cutlass/arch/simd` 零命中；simd.h 的 dot 主模板用未声明的 T（自身编译不过），simd_sm60.h 是 4.x 重构后空壳（上游历史版本有真实 __hfma2）。
3. **version.h 引用不存在的头**：`include/cutlass/version.h:46` 包含 `cutlass/version_extended.h`——仓内不存在，由 CMakeLists.txt:759-760 从 cmake/version_extended.h.in configure 到构建目录（CUTLASS_VERSIONS_GENERATED 宏见 :265-266），缺省回落 `CUTLASS_BUILD 0`（version.h:48）。版本真值 4.8.0 在 version.h:41-43。
4. **CallbacksImpl 非实体类**：`include/cutlass/epilogue/threadblock/fusion/visitor_2x.hpp:177/240` 的 `template<class CallbacksImpl>` 是 duck-typing 模板形参名，仓内无该类定义——按"实体类"检索会扑空。
5. **packed_stride.hpp 图谱裁剪漏网**：tools/util/ 整目录被裁剪，唯 `tools/util/include/cutlass/util/packed_stride.hpp` 一张节点入图谱（非工具问题，是裁剪边界产物）。
6. **CuTeDSL 包同名解析歧义**：`python/docs/externals/00_basic_gemm.ipynb` 的 `import cutlass`（v3.x 世代）与 CuTeDSL 的 `cutlass` 包同名——静态扫描会把旧文档快照误连到 CuTeDSL 线。
7. **LICENSE 是 BSD-3-Clause 非 Apache**：LICENSE.txt:2 SPDX 标注；全文件 grep "Apache" 零命中；cutlass_compiler/LICENSE.txt 与根仅版权年份行不同。CuTeDSL 另受专有 EULA（python/CuTeDSL/EULA.txt 与根 EULA.txt 逐字节相同）。
8. **cutlass_cppgen 前身名就是 cutlass**：python/README.md 明言整体更名（非删除，模块一一对应）；python/docs/ 旧 Sphinx 快照的 cutlass.emit/cutlass.op/cutlass.utils 均对应现 cutlass_cppgen.*；setup_cutlass.py:34/35/38 三死导入（copy/os/build_ext 未用）为迁移残迹。
9. **scheduler.py 的 _mlir 是运行时注入**：`operators/cutlass/operators/providers/cutedsl/gemm/implementations/scheduler.py:31` `from cutlass._mlir import ir`——目标模块仓内不存在，由 MLIR 后端动态注入；静态依赖分析看不到此边。
10. **Python 轮子版本三线不同步**：根 pyproject.toml:7 `4.2.0.0` 落后 C++ 4.8.0；CuTeDSL pyproject.toml:18/29 dynamic version 指向 VERSION.EDITABLE（git 检出不存在，发布管线生成，源码树直接 pip install 必失败）；轮子体积大头是 C++ 模板资产（setup.cfg exclude_package_data 剔 .py）。
11. **base 是伪方言**：cutlass_compiler/README 自述 base=cute 降级后的上游 MLIR 方言集合（arith/scf/gpu/LLVM/NVVM）；base-opt 刻意不注册 cute（Registration.h 头注释），泄漏引用在解析期报错——"base 层测试失败=降级不彻底"是设计内语义。
12. **nblink 断链被构建容忍**：python/docs_src/source/externals/*.nblink 指向的 notebook 已迁 examples/python/deprecated/（原路径失效），conf.py 的 nbsphinx_allow_errors=True 让 Sphinx 构建静默通过——文档站可构建≠链接有效。
13. **SM100/SM120 不兼容警示**：README.md 明确数据中心 Blackwell（sm100a 条件特性）内核无法跑 RTX 50（SM120）——两代不能混用 sm 代际后缀。
14. **operators 内嵌 pycute 是 vendored 分叉非重复失误**：fusion/pycute/layout.py（409 行、2 空格缩进）与 python/pycute/layout.py（367 行、4 空格）同源分叉，operators 副本略多函数——避免 PyPI 运行时依赖的刻意复制。
15. **cutlass_compiler 测试面 347 的构成**：322 个 .mlir（lit）+25 个测试 .cpp；cutegen 的 cg_tuple_test.cpp 单文件 2148 行 61 TEST 是数值代数层最大测试面。

## 流水线备注

- 图谱校验 0 issues；fingerprints 1911 文件基线 @0b55a2f6 支持增量更新。
- 行号锚验收口径：`文件:行号` 正则计数，全部主会话从源码独立核实；字数为不计空格总字符。
- 本 README 由 explain 组 2 会话落盘（2026-11-06）；onboarding 与组 1（01-06）由并行实例产出——组 2 收官时点组 1 已落 5/6 篇（05 缺），ONBOARDING.md 已在盘，状态表已按盘上事实刷新；组 1 收官后请补齐状态。

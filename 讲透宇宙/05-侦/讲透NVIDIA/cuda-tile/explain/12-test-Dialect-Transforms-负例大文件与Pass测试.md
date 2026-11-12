# 12 · test/Dialect/ + test/Transforms/ —— invalid.mlir 负例大文件的 CHECK 组织与 Pass 测试

## ① 角色定位

这对目录是方言**语义层**的测试阵地（与第 11 篇的字节码层互补）：test/Dialect/CudaTile/（31 个文件）验证 op 验证器、类型系统、属性约束、debuginfo 属性——核心是 2705 行的 invalid.mlir，单文件装下全方言的负例集；test/Transforms/（6 个文件、2876 行）逐 pass 钉住第 7 篇四个变换的行为合同。两者全部由 cuda-tile-opt 驱动（lit.cfg.py:62-65 注册），断言范式两条：正例 `RUN: cuda-tile-opt ... | FileCheck %s`（输出必须长这样），负例 `RUN: cuda-tile-opt %s -verify-diagnostics -split-input-file`（诊断必须精确出现且不多不少）。

## ② 内部结构

**invalid.mlir 的组织术**是这个仓库测试工程的教科书：RUN 行 `cuda-tile-opt %s -verify-diagnostics -allow-unregistered-dialect -split-input-file`（invalid.mlir:1）配 `// -----` 分隔符把 2705 行切成 **294 个独立用例**（293 个分隔符实测），`--split-input-file` 让每个用例单独跑验证器、互不污染。每个用例 3-8 行：一段非法 IR + `// expected-error @below{{...}}` 内联标注（全文 289 个 expected-error、13 个 expected-note、2 个 expected-error-re）。错误消息本身就是被测合同——如 :3 的 `expected '<'`（constant 语法拒绝裸字符串）、:13-14 拒绝 MLIR tensor 类型 `must be tile of i1 or i8 ... but got 'tensor<f32>'`、:38 `region with 1 blocks`、:44 continue 的父 op 约束、:55 嵌套祖先链约束、:64 `operand #0 must be 0D tile of i1 values`。`expected-error-re`（:30）用正则吸收可选 token（`{{( or f8E5M3FNU)?}}`），是为枚举列表演进留的弹性。**正例与专项**：ops.mlir/types.mlir/arith.mlir/conversion.mlir 铺基础语义；主题负例拆成专文件——memory_consistency_ops_invalid、reduce_and_scan_invalid、view_invalid、get_shape_invalid、math_invalid、permute_invalid、dense_attr_invalid；opt_hints 家族五件（error/warn/invalid/default_silent 正反组合，对应 cuda-tile-opt 的 -Wunsupported-hints 开关矩阵）；debuginfo 家族（attr/loc_invalid/update_symbol_names + _fail，钉 TransformsUtils.updateSymbolName 的成功/失败两态）；syntax_omit_dialect_prefix.mlir 测方言前缀省略语法；round_trip_test.sh 提供 %round_trip_test 脚本本体。**test/Transforms/ 六文件**按 pass 分（任务书称"三 pass"，实际 6 文件覆盖 4 个 cuda_tile pass + MLIR 标准 strip-debuginfo——以源码为准）：fuse-fma.mlir（554 行，RUN 挂 `testing$func` 层级，:1）21 个用例正反对照——:188-194 不同 rounding 不融合、:293-300 乘积多用途不融合、链式 canonicalize+FMA 两连击；licm.mlir（612 行，:1 同层级）按"Group 1: Basic Hoisting from ForOp"分组注释推进，含 iv 依赖/iter_args 依赖不提升的负例；loop_split.mlir（1556 行，RUN 挂 `cuda_tile.entry` 层级，:1）从 `@unsupported_cmp_non_iv` 不支持形态开始逐条件展开；loop_split_if_no_else.mlir（41 行）是回归钉子——"loop-split must not crash when IfOp has no else block"（:3）；synthesize-debuginfo-scopes.mlir（79 行）加 `--mlir-print-debuginfo` 让 DIAttr 显形（:1）；strip-debug-info.mlir（34 行）用 `--strip-debuginfo` + `CHECK-NOT: loc(` 断言位置信息被清空。

## ③ 外部连接

被测物映射关系清晰：invalid.mlir 各用例对应 Ops.td 的 verifier/约束声明；opt_hints 家族 ↔ Dialect 的 hint 诊断配置（cuda-tile-opt.cpp:39-48 注入的开关）；debuginfo_update_symbol_names ↔ TransformsUtils.cpp:17 的 updateSymbolName；Transforms 六文件 ↔ 第 7 篇四 Pass 的 Passes.td 定义；strip-debug-info ↔ MLIR 标准 pass（cuda-tile-opt.cpp:53 注册）。test/lib/TestPasses.cpp 供给 updateSymbolName 的测试 pass（`registerTransformsUtilsTestPasses`，cuda-tile-opt.cpp:56-58）；test/CudaTile/cuda-tile-optimize.mlir 是 optimize 工具的 lit 端到端；test/CAPI/register.c 与 test/python/ 系（cuda_tile_public_bindings.py）补 C/Python 边界。工具链依赖 FileCheck、not（负例包裹）、`--split-input-file`/`-verify-diagnostics` 三个 MLIR 测试基建特性。

## ④ 数据流

负例流：lit 把 invalid.mlir 按 `// -----` 切成 N 片 → 每片独立跑 cuda-tile-opt parse+verify → `-verify-diagnostics` 收集实际诊断与 expected 标注做双向往返匹配（少报=漏验证、多报=误报，都算失败）→ 全部片通过才算文件通过。Pass 测试流：.mlir 输入 → textual pipeline 字符串（如 `builtin.module(cuda_tile.module(cuda_tile.testing$func(cuda-tile-licm)))`）解析嵌套 OpPassManager → 目标 pass 在匹配的 op 层级执行 → 输出打印 → FileCheck 按 CHECK-LABEL 定位函数、CHECK-NEXT 锁相邻序、CHECK-NOT 断消失（fuse-fma.mlir:4-6 `CHECK-NOT: mulf/addf` 三连是"融合彻底"的证据）。round-trip 流见第 11 篇——Dialect 侧的 round_trip_test.sh 正是该宏的实现。

## ⑤ 设计决策

**单文件负例大集 vs 一例一文件**：CUDA Tile 选了前者，收益是 294 个用例共享一次 lit 发现/调度开销、新增负例零文件成本，代价是必须依赖 `--split-input-file` 且任何人改文件要遵守"用例间必隔 `// -----`"的纪律——测试组织本身成了约定。**expected 内联 vs 独立 CHECK 文件**：负例选 `-verify-diagnostics`（错误标注紧贴触发 IR，一眼因果），正例选管道+FileCheck（输出即合同）——两条范式按测试性质分流而非一刀切。**pass 挂载层级差异**是新手最易踩的坑：fuse-fma/licm 是 `InterfacePass<FunctionOpInterface>` 所以挂 `testing$func`，loop-split 虽同是 InterfacePass 却因测试 IR 用 `entry` 写法而挂 `cuda_tile.entry`，synthesize-debug-info-scopes 是 ModuleOp 级 Pass 挂 `cuda_tile.module`——pipeline 字符串的括号层级必须与 IR 嵌套严格同构。**负例中的正例**（fuse-fma 的"不同 rounding 仍保留 mulf+addf"、licm 的"iv 依赖留在循环内"）与正例同等重要：证明 pass 的克制面、防止过度变换。

## ⑥ 新人提示

给新 op 加验证器时的工作流：先在 Ops.td 写约束 → invalid.mlir 末尾追加 `// -----` 用例 + expected-error（消息从 `cuda-tile-opt` 实际输出拷贝）→ 若消息含枚举全列表，学 :30 用 expected-error-re 留 `( or x)?` 弹性，否则每加一个元素类型全仓测试红一片。调 pass 测试时 `--split-input-file` 忘写会出现"第一个用例通过后面全挂"的假象；CHECK-LABEL 用函数名锚点（`testing$func @test_xxx`）保证用例间独立。看不懂某负例为何非法时，直接搜 Ops.td 里 expected-error 消息的关键词——消息文本与 TableGen 约束声明基本一一对应。源码勘误：任务书"Transforms 三 pass 测试"实为 6 文件（4 个 cuda_tile pass + strip-debug-info；loop_split 另有 if_no_else 回归专文件）；invalid.mlir 用例数按 293 个 `// -----` 分隔符计为 294 例、expected-error 共 289 处（另有 note 13/re 2），以上均为 2026-11 快照实测。

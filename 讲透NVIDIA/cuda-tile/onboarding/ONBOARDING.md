# cuda-tile ONBOARDING（CUDA Tile IR 开源侧全景导览）

> 基于知识图谱（720 节点/1128 边/16 层/15 步 tour，commit `5b3fa4c0`）+ 源码逐锚核实。行号锚均经本仓源码验证。

## 1. 仓库一句话定位与坐标

**cuda-tile 是 NVIDIA CUDA Tile IR 的开源 IR 层**：面向 CUDA kernel 优化的 MLIR 方言生态（README.md:11 明言对齐 CUDA Toolkit 13.1），四大组件=MLIR 方言+Python 绑定+TileIR 字节码序列化（`.tilebc`）+一致性测试。它与 CUDA Toolkit 中**闭源 tileiras 编译器（约 93.9MB AOT 工具）构成双层结构**：本仓止于方言/字节码读写/轻量优化，tileiras 消费 `.tilebc` 编 cubin 或经驱动 API 运行时 JIT（README.md:219-220、330-331）。坐标印痕：`lib/Dialect/CudaTile/IR/CMakeLists.txt:40-42` 的 PRIVATE include 指向本仓不存在的 `../../../../compiler/include`——源码树预期嵌入 tileiras 仓布局（`compiler/` 为兄弟目录），坐实"开源 IR/闭源编译器"同源分发。

## 2. 分层架构总览（16 层全景）

| 层 | 名称 | 件 | 职责与代表 |
|---|---|---|---|
| L01 | 构建配置 | 11 | `CMakeLists.txt:53-57`（MSVC 留 64MiB 栈，LLVM Bug 5680414）；`cmake/IncludeLLVM.cmake:29` 钉版 LLVM `c495a9b796c4` |
| L02 | 方言 TableGen | 15 | 事实源：`Dialect.td:33`、`Ops.td`（107 op）、`Types.td`、`AttrDefs.td`+三张 Bytecode 冻结表 |
| L03 | IR 公共头 | 12 | `Ops.h`/`Types.h` 装载生成物；`SharedVerifiers.h` 集中校验 |
| L04 | 方言实现 | 10 | `CudaTile.cpp`（6400 行）、`Types.cpp`（1074 行五类视图）等六实现 |
| L05 | Bytecode 接口 | 16 | 七稳定头；`Version.h:84-111` 锚点族；MinVersionAnalyzer |
| L06 | 编解码核心 | 6 | `BytecodeWriter.cpp`（1832 行）/`BytecodeReader.cpp`（3044 行）镜像；Translation |
| L07 | Transforms | 10 | FuseFMA/LICM/LoopSplit（395 行最重）/SynthesizeDebugInfoScopes+`Passes.td` |
| L08 | Optimizer | 3 | `CudaTileOptimizer.cpp`（378 行）L1/L2/L3 管线，bytecode 进出 |
| L09 | CAPI/Python | 13 | `cuda_tile-c/Dialect/CudaTileDialect.h` 97 C 函数；nanobind+`cuda_tile_ops.py` 5375 行 |
| L10 | tblgen 生成 | 14 | `BytecodeGen.cpp`（1443 行写）/`BytecodeReaderGen.cpp`（874 行读） |
| L11 | tblgen 规格 | 12 | `SpecGen.cpp`/`Emitter.h`→Markdown 规格与 `spec/ops.rst` |
| L12 | CLI 工具链 | 9 | `cuda-tile-opt`（MlirOptMain）/`cuda-tile-translate`/`cuda-tile-optimize` |
| L13 | 测试设施 | 8 | `test/lit.cfg.py`（`%round_trip_test` 替换）、`TestPasses.cpp` |
| L14 | Bytecode 测试 | 85 | round-trip/负例/版本兼容+13 组逐字节 golden |
| L15 | Dialect 测试 | 31 | `arith.mlir`（1738 行）正例、`invalid.mlir`（2705 行）负例总集 |
| L16 | 集成测试 | 12 | Transforms 六测+13 pytest+`test/CAPI/register.c` 冒烟 |

依赖走向：L02 .td 是根，tblgen 与手写实现共生成运行时主体，L09-L12 出口，L13-L16 验证。

## 3. 核心数据流

**正向**：① `.td` 定义——`Ops.td` 107 op 按FloatingPoint 30/Core 20/Integer 14/Conversion 9/Views 8/ControlFlow 8/Memory 6/Misc 4/Bitwise 3/Atomics 3 分组（基类 `Dialect.td:183-216`），`Dialect.td:95-102` 让每 op 携带 `sinceVersion`。② tblgen 生成——`mlir_tablegen` 产 `Ops.h.inc` 等；`cuda-tile-tblgen` 四路产 Bytecode/StaticOpcodes/Type/Attr 四个 `.inc`。③ lib 实现 parse/print/verify。④ 序列化——`writeBytecode`（`BytecodeWriter.cpp:1770`）先 verify+自包含校验，写 **12 字节头**：8B 魔数 `{0x7F,'T','i','l','e','I','R',0x00}`+uint8 major+uint8 minor+uint16 tag 小端（`BytecodeWriter.cpp:195-201`；类型 `Version.h:35-41`），随后 Global→Func→Constant→Debug→Type→Producer→String→End 写节（`BytecodeWriter.cpp:1797-1829`）。⑤ tileiras 编 cubin。

**反向**：`isTileIRBytecode` 魔数探测（`BytecodeReader.cpp:45`）→ `readBytecode` 解码各节重建 ModuleOp。

**版本前向覆盖**：`BytecodeOpcodes.td:55-58` 声明 13.1-13.4——13.2-13.4 已前向引入（如 `BytecodeTypeOpcodes.td:86` Float8E5M3FNU tag 0x82 属 13.4），`getMinBytecodeVersion`（`MinVersionAnalyzer.cpp:44`）反查模块最早可序列化版本。

## 4. 关键模块深读

**① BytecodeWriter.cpp（容器格式权威）**：头注释（`BytecodeWriter.cpp:41-58`）即格式规范——`bytecode=header+section*`，每节 sectionId[低 7 位 ID+高位 hasAlignment]+length[varint]+[alignment]+data；`writeLE` 在 `BytecodeWriter.cpp:107`；五大管理器各管一节。

**② BytecodeEnums.h（92 行）**：`BytecodeEnums.h:30-42` Section 表（End=0x00/String=0x01/Func=0x02/Debug=0x03/Constant=0x04/Type=0x05/Global=0x06/Producer=0x07）；`:26` 对齐填充常量 `kAlignmentByte=0xCB`；tag 枚举由生成 .inc 注入。

**③ Ops.td（指令集）**：`module/entry/for/loop/if` 控制流、`load_ptr_tko/store_ptr_tko` tko 访存、`mma_f/mma_f_scaled` tensor core、`make_*_view` 视图族；配套冻结表见第 6 节。

**④ CudaTile.cpp（运行时主体）**：全 op parse/print/verify+canonicalization+`DenseTypedElementsAttr` 编解码（`CudaTile.cpp:381`）+内存一致性验证；testing 方言前缀解析在 `CudaTile.cpp:5768`。`Types.h:43` 的 `maxTileNumElements=16777216`（16M）是 tile 硬上限。

**⑤ MinVersionAnalyzer.cpp（74 行）**：`getMinBytecodeVersion`（`MinVersionAnalyzer.cpp:44-74`）三路回调——类型（去重）/属性（枚举 case+参数）/操作（`Bytecode.inc` 的 `GEN_OP_VERSION_CHECK_DISPATCH`）取最大下界；配合 `Version.cpp:39-75` 五个 k* 版本锚点常量。

## 5. 新人导览路线（15 步 tour 精编）

| 步 | 主题 | 必读 | 要点 |
|---|---|---|---|
| 1 | 全景 | `README.md`、`cmake/IncludeLLVM.cmake` | 开源 IR 配闭源 tileiras |
| 2 | 方言事实源 | `Dialect.td`、`Ops.td`、`Types.td` | 改方言必从 .td 出发 |
| 3 | 字节码宪法 | 三张 `Bytecode*Opcodes.td` | tag 冻结永不重编号 |
| 4 | 手写骨架 | `Ops.h`、`SharedVerifiers.h` | 生成物与实现间接口层 |
| 5 | 方言实现 | `lib/.../CudaTile.cpp`、`Types.cpp` | 先 Types 再定向查巨文件 |
| 6 | Bytecode API | `Bytecode/*` 七头 | 闭源侧全部依赖 |
| 7 | 编解码双核 | `BytecodeWriter.cpp`、`BytecodeReader.cpp` | 读懂写序=读懂 .tilebc |
| 8 | 版本兼容 | `Version.cpp`、`MinVersionAnalyzer.cpp` | 门控+最小版本+自包含三闸 |
| 9 | Transforms | `Passes.td`+四 pass cpp | 轻优化本仓，重编译 tileiras |
| 10 | Optimizer | `CudaTileOptimizer.{h,cpp}` | L1/L2/L3 组装管线 |
| 11 | C API | `cuda_tile-c/Dialect/CudaTileDialect.h` | 唯一稳定 ABI |
| 12 | Python 绑定 | `DialectCudaTile.cpp`、`cuda_tile_ops.py` | nanobind 层+手写 API 层 |
| 13 | tblgen | `cuda-tile-tblgen/`（main `cuda-tile-tblgen.cpp:28`） | 一个 .td 变三千行代码 |
| 14 | CLI 三件套 | `tools/cuda-tile-*/` | 调试与 CI 入口 |
| 15 | 测试收口 | `lit.cfg.py`、`encoding_stability/` | 测试即规格 |

节奏：1-3 第一周，4-8 第二周，9-15 按需。

## 6. 设计决策与取舍

1. **IR 开源+编译器闭源双层**：本仓止于 `.tilebc`，指令选择/PTX→cubin 在闭源 tileiras；公共 API 与实现刻意分离，闭源侧只依赖稳定头。
2. **操作码冻结表**：`BytecodeOpcodes.td:71` 明言公共段 0x0-0xFFF "must never be renumbered"。两处跳洞——0x18 后直接 0x25、0x33 后直接 0x3A——历史 op 删除后编号不回收，分配即消耗。测试 op 独占 0x3000+（`BytecodeOpcodes.td:179-182`）。
3. **类型 tag 跳号**：`BytecodeTypeOpcodes.td:86` Float8E5M3FNU 分 **0x82** 而非续 13.3 段的 23——连续段（0-22）视为冻结，新段另起。
4. **私有 include 印证嵌入布局**：见第 1 节；独立构建时该 include 落空不致错。
5. **`useStrictPropertiesInAssemblyFormat=0`**（`Dialect.td:49`）：LLVM c495a9b796c4 后的临时 opt-out；`IncludeLLVM.cmake:29` 恰钉版该 commit，README.md:372-383 区间表（v13.1.0→81b576e66、v13.1.1→cfbb4cc3121、v13.1.3→3d7018c70）是对外承诺。
6. **显式手写换生成器复杂度**：CAPI 97 函数逐一手写桥接，Python 手写 5375 行 API 层——可审计性优先。

## 7. 已知坑与勘误（源码级实证）

1. **上游拼写笔误**：`tools/cuda-tile-tblgen/SpecGen.cpp:220` `covertSyntaxToSignature`（应为 convert），`:471` 有注释掉的调用；改名需同动两处。
2. **注释漂移**：`BytecodeWriter.cpp:56` 写 padding "(0xCF)"，真常量是 `BytecodeEnums.h:26` 的 0xCB——以常量为准。
3. **README 区间表滞后**：表止于 v13.1.3→`3d7018c70`（latest），HEAD 实钉 `c495a9b796c4`（`IncludeLLVM.cmake:29`）；查钉版以该 cmake 为准。
4. **.inc 是构建产物**：`Bytecode.inc`/`Types.h.inc` 仓内不存在；改 .td 后必须重建 tblgen 目标（`CudaTileBytecodeIncGen` 等）。
5. **testing$ 前缀**：测试方言装配语法带 `cuda_tile.testing$` 前缀（解析 `CudaTile.cpp:5768`），仅 TILE_IR_INCLUDE_TESTS 构建存在——正式构建找不到 Test_FuncOp 不是 bug。
6. **双后缀并存**：测试用 `.tileirbc`（`encoding_stability/goldens/*.golden.tileirbc`），README 链路用 `.tilebc`，同一格式不区分。

## 8. 二次开发指引

**加新 op（完整链）**：① `Ops.td` 用分组基类（`Dialect.td:183-216`）定义并填 `sinceVersion`；② `BytecodeOpcodes.td` 在现最大 0x7A 后追加 opcode（勿复用 0x19-0x24/0x34-0x39 空洞）；③ 新类型/属性同步 `Types.td`/`AttrDefs.td`+两张 tag 表（参考 0x82 跳号先例）；④ 补 SupportedVersion（`BytecodeOpcodes.td:55-58`），`Version.cpp:39-75` 锚点族按需新增；⑤ verify/canonicalization 落 `CudaTile.cpp`（共享校验进 `SharedVerifiers.h`）；⑥ 重建（tblgen 级联生成四路 .inc）；⑦ lit 三件套——正例（双 opt 幂等+round-trip）、负例（`*_invalid.mlir`）、涉常量编码加 `encoding_stability/` golden；Python 侧补 `cuda_tile_ops.py` 构造函数。

**加新类型（轻链）**：`Types.td`（可选参数走版本有序位分配，`BytecodeGenUtilities.cpp` 处理）→ `BytecodeTypeOpcodes.td` 分 tag → `Types.cpp` 实现 parse/print/verify → 版本映射由 `tools/cuda-tile-tblgen/BytecodeTypeCodeGen.cpp` 自动生成。

**纪律**：冻结表只增不改不删；新特性必须被 `getMinBytecodeVersion` 正确定级；自包含不变量（顶层仅函数/全局、全 op 属本方言，`lib/Bytecode/Common/BytecodeVerification.cpp`）不许放松——闭源 tileiras 与版本兼容测试均以此为前提。

---
*understand-anything 流水线 onboarding 子代理，2026-11-06；图谱 commit `5b3fa4c0dd04d`。*

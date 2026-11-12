# 11 · test/Bytecode/ —— lit 测试体系：黄金字节基线、版本矩阵与损坏 fixture 负例

## ① 角色定位

test/Bytecode/（85 个文件）是 CUDA Tile 字节码格式的"宪法守护层"：它把三件事钉进 CI——**编码稳定性**（同一 IR 必须产生逐字节相同的 bytecode）、**版本兼容性**（13.1-13.4 四个生产版本的可读/可写/拒绝行为）、**对抗健壮性**（损坏输入必须给出精确错误而非崩溃）。测试跑在 LLVM lit 框架上（test/lit.cfg.py:17 `ShTest`，:14 套件名 "CUDA_TILE"），断言工具有三种：FileCheck（匹配输出文本）、`cmp`（逐字节比对 golden）、`not`（断言命令必须失败）。与 test/Dialect 的 IR 语义测试不同，这里的主角是**字节流本身**——多个 fixture 直接是 `.tileirbc` 二进制文件入库。

## ② 内部结构

四个子目录 + 22 个顶层测试。**encoding_stability/**（13 对 .mlir+golden）：每对的 RUN 是两行——`cuda-tile-translate -mlir-to-cudatilebc -no-implicit-module %s -o %t.bc` 然后 `cmp %t.bc %S/goldens/xxx.golden.tileirbc`（i1_splat_true.mlir:3-4）。覆盖矩阵刻意挑编码边角：i1 splat true/false、i1 non-splat、i32/i64 数组（i64_msb_set 钉最高位符号扩展）、f16/bf16/tf32/f8E4M3FN/f8E5M2 splat、f64/i8 负数——每个注释都写明防什么（i8_signed_negative.mlir:1-2 "Catches regressions in sign-extension / signedness handling on the writer side"）。配套 `regenerate_goldens.sh` 的头注释（:10-16）是流程契约：**只在编码迁移是有意的时候跑**；回归出现时要么是 MLIR 底层编码悄悄变了（"the i1 0xff bug pattern"→在 BytecodeReader.cpp 加向后兼容 shim）、要么是 writer 侧误改（→revert），禁止"为了让失败消失"而重生成。**invalid/**（8 个 fixture）：损坏字节码的负例集，由 invalid_structure.mlir 单文件用 `not cuda-tile-translate -cudatilebc-to-mlir ... 2>&1 | FileCheck --check-prefix=XXX` 驱动——魔数错（fixture 首字节 0x7e，对应 invalid_structure.mlir:8 "invalid magic number"）、版本超界（:14 "unsupported Tile version 18.0.0, this reader supports versions [13.1 - 13.4]"）、未知 section ID 127（:20）、section 长度越界（:26 附近）、DenseArray 值 -2147483648 不可表示（:32）、DictionaryAttr 空属性名（:38）；另有 constant_rawdatasize_overflow 等独立 fixture。**versioning/**（18 个 .mlir + Inputs/ 四版本目录）：向后兼容行为测试，Inputs/13.1/ 存 f4e2m1fn-in-13.1.tileirbc、negi-op-13.1.tileirbc、print-op-13.1.tileirbc 等旧版产物（13.2 存 partition_view 可选枚举旧编码、13.3 存 i1 旧编码、13.4 存 opt-hints 空字典新旧两份）；`-bytecode-version=13.1` 目标下用 13.2 特性则被拒（oldVersionRejectionTest.mlir:4-5 "attribute 'overflow' requires bytecode version 13.2+"）；list_versions.mlir:3-11 钉死 `--list-versions` 输出：13.1→13.4 顺序 + 测试专用 250.0/250.1（仅 TILE_IR_INCLUDE_TESTS 构建出现）；test_forward_compatibility.mlir:4-5 用 `-test-cudatile-roundtrip -bytecode-version=250.0/250.1` 验证"不用新特性时老版本可序列化"的前向兼容语义。**顶层**：constantTest/operationsTest/producerTest 等走 `%round_trip_test` 宏（constantTest.mlir:2）；legacy_i1_splat_compat.mlir:13 直接读入库的 legacy_i1_splat_0xff.tileirbc 验证历史 bug 编码的兼容垫片；Analysis/ 存 min_version 分析测试。

## ③ 外部连接

上游被测物：lib/Bytecode 的 Reader/Writer/Version/MinVersionAnalyzer 与 tools 的 cuda-tile-translate（所有 RUN 的执行者）。lit 基建：test/lit.cfg.py:20 声明 .mlir/.c/.py 后缀；:62-65 注册 cuda-tile-opt/optimize/FileCheck/not 工具替换；:50-55 定义 `%round_trip_test` 跨平台替换（Windows 用 round_trip_test.py，Unix 用 Dialect/CudaTile/round_trip_test.sh）；translate 的测试翻译（`-test-cudatile-roundtrip`）只在测试构建注册（cuda-tile-translate.cpp:25）。版本常量与第 10 篇 translate 的 `--list-versions`/`-bytecode-version` 选项同源；min version 分析对接 `analyze-min-version` 翻译（BytecodeTranslation.cpp:89-109）。

## ④ 数据流

golden 比对流：.mlir 源 → translate 编码 → `%t.bc` 临时字节流 → `cmp` 与 `%S/goldens/*.golden.tileirbc`（`%S` 是源文件目录）逐字节比对——任何 writer 端的编码抖动（字节序、varint 宽度、splat 判定变化）立即爆红。golden 文件头两字节区即格式签名：实测 hexdump `7f 54 69 6c 65 49 52 00 0d 04`——`\x7fTileIR\x00` 魔数后跟 `0d 04`=版本 13.4 的变长编码；而 invalid fixture 把首字节换成 `7e`，一步差触发 magic 检查。负例流：`not` 包住 translate 调用断言非零退出 + stderr 文本被 FileCheck 前缀逐条认领。兼容流：Inputs 里的旧版 .tileirbc 是**以旧 writer 实际产物形式入库**的化石，新 reader 必须成功反序列化并 FileCheck 语义等价输出——这保证"读老文件"能力不被重构无声破坏。

## ⑤ 设计决策

三层防线的设计哲学各不同。golden 基线选 `cmp` 而非 FileCheck 匹配十六进制转储：字节级比对零歧义、零转义噪音，代价是任何合法重构都要显式重生成——所以 regenerate 脚本用注释把"何时允许重生成"写成纪律（regenerate_goldens.sh:10-16），甚至点名历史事故模式（i1 0xff：i1 全真 splat 曾用 0xff 填充字节，MLIR 上游编码变更后靠 reader 垫片续命）。版本矩阵用**真实旧字节码 fixture**而非"降版本重新序列化"来测向后兼容，因为两条路径走的是不同代码（老 writer 的字节形态只有化石能代表）。负例测试要求错误**消息本身可匹配**（FileCheck 认领 "invalid magic number" 等），这同时钉住了错误分类的稳定性——下游工具链依赖这些消息做诊断分流。250.x 测试版本号是妙笔：用虚构大版本号演练"未来版本演进"（新属性默认值、DefaultValuedParameter 降级），不污染生产版本语义。

## ⑥ 新人提示

改 Writer/Reader 后跑 `llvm-lit test/Bytecode` 先看红的是"稳定基线"还是"兼容测试"——前者查 writer，后者查 reader 垫片；两者同红说明格式本身变了，这时才轮到 regenerate_goldens.sh，且必须先写清迁移理由。新增编码特性时同步三件事：encoding_stability 加一对 golden、versioning 加降级拒绝测试、list_versions 若有新版本要更新快照。调试字节流用 `od -A x -t x1z file.tileirbc` 直接看十六进制，魔数后第 9-10 字节就是版本号。注意 `%S`（源目录）与 `%T`/`%t`（临时）的区别：golden 永远经 `%S` 引用，保证从任意执行目录跑 lit 都能命中。源码勘误：任务书提及 `\x7fTileIR\x00` 魔数——实测一致（golden 首 8 字节 7f 54 69 6c 65 49 52 00）；"invalid/ 损坏 fixture 负例"共 8 文件（含 constant_rawdatasize_overflow.tileirbc 等，并非全部由 invalid_structure.mlir 驱动）。

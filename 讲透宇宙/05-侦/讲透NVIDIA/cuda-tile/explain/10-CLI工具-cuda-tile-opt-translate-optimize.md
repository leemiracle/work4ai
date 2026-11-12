# 10 · tools/ —— CLI 三件套：opt 测试驱动、translate 双向翻译、optimize 优化器

## ① 角色定位

tools/ 下三个可执行（外加 cuda-tile-tblgen 代码生成器，属另一条生产线）：**cuda-tile-opt**（60 行）是标准 MLIR `MlirOptMain` 换皮——lit 测试的主力驱动，消费 textual pass pipeline；**cuda-tile-translate**（28 行）同样是 `mlirTranslateMain` 换皮，注册了 bytecode↔MLIR 双向翻译与三个隐藏测试翻译，是格式转换与版本管理的唯一 CLI 出口；**cuda-tile-optimize**（232 行）唯一的"产品型"工具：bytecode in → 默认优化管线 → bytecode/MLIR out，直接薄封装第 8 篇的 `optimizeTileIR`。三者分工一句话：opt 面向 IR 级测试（input 是 .mlir 文本），optimize 面向 artifact 级流水线（input 是 .tileirbc 字节码），translate 负责两者世界的翻译。

## ② 内部结构

**cuda-tile-opt.cpp** 做四件事：定义两个 hint 诊断开关 `-Wunsupported-hints`/`-Werr-hints`（cuda-tile-opt.cpp:27-34）；向 DialectRegistry 挂 extension，在方言加载时把这两个开关值注入方言实例（:39-48，`setWarnUnsupportedHints`/`setErrorOnHints`）；注册 canonicalizer/CSE/inliner/strip-debuginfo 与全部 cuda_tile pass（:50-54）；`CUDA_TILE_ENABLE_TESTING` 编译宏下额外注册 `registerTransformsUtilsTestPasses`（:56-58，TransformsUtils 的 updateSymbolName 测试通道）；最后交 `MlirOptMain`（:60-61，描述串 "CudaTile test driver"）。**cuda-tile-translate.cpp** 只有 main：注册三个 bytecode 相关命令行选项（版本选项、优化 hints 选项、`--list-versions`，:21-23）+ 正式翻译 + 测试翻译（:24-25），然后 `mlirTranslateMain`。翻译本体在 lib/Bytecode/Translation/BytecodeTranslation.cpp：`cudatilebc-to-mlir`（:36-43）经 `deserializeModule`（:26-34，同样注入 hint 开关）调 `readBytecode`；`mlir-to-cudatilebc`（:67-83）经 `getCudaTileModuleOp`（:48-65，兼容 cuda_tile 模块裸放或嵌在 builtin module 里的两种输入，:53-62）调 `writeBytecode`，目标版本来自 `getCurrentBytecodeVersion()`（即 `-bytecode-version=` 选项）；第三个注册是 `analyze-min-version`（:89-109），对每个 cuda_tile.module 输出所需最低字节码版本。**cuda-tile-optimize.cpp** 前半是一个 `Options` 结构体（:36-150）：输入为位置参数，`--output-file/-o`、`--quiet/-q`、`--emit-bytecode`、`--run-before/after-default-pipeline`（alias `--before/--after`）、`--fuse-fma`、`--opt-level/-O`（默认 3）、`--verbose/-v`、`--enable-multithread`；后半 main 填 `TileIROptimizerConfig`（:186-201），实现输出模式优先级（:203-223）：给了 -o 就按 --emit-bytecode 选 BytecodeFile 或 MlirFile，verbose 追加 stdout；没给 -o 且非 quiet 则默认 stdout 打印 MLIR。

## ③ 外部连接

opt 依赖 Passes.h 的 `registerCudaTilePasses` 与 MLIR 标准 pass 注册；translate 依赖 Bytecode 层（Reader/Writer/CommandLineOptions/MinVersionAnalyzer）与 `test/RoundTripTestRegistration.h`（测试翻译 `-test-cudatile-roundtrip` 等，仅测试构建可见——versioning 测试大量使用）；optimize 依赖 Optimizer 库的 `optimizeTileIR`（:226）。版本打印机（:148-185）拼出 "NVIDIA (R) CUDA Tile IR -> CUDA Tile IR optimizer / Built on {date}"，日期来自构建注入的 `STD_DATE` 宏。lit 侧：test/lit.cfg.py:62-65 把三工具与 FileCheck/not 一并声明进 substitutions，`%round_trip_test` 脚本内部就是 translate 的两次调用+opt 一次调用（round_trip_test.sh:5-9）。

## ④ 数据流

round-trip 验证流（lit `%round_trip_test %s %t`）：`cuda-tile-translate -mlir-to-cudatilebc foo.mlir -o t.out.tilebc`（写 bytecode）→ `cuda-tile-translate -cudatilebc-to-mlir t.out.tilebc -o t.roundtrip.mlir`（读回）→ `cuda-tile-opt foo.mlir -o t.ref.mlir`（规范化参照）→ `diff -B` 两者必须逐字一致（round_trip_test.sh:5-11）——把"序列化无信息损失"与"opt 输出是规范形式"两个性质一次钉死。生产优化流：`cuda-tile-optimize kernel.tileirbc -O3 --fuse-fma -o k2.tileirbc --emit-bytecode` → loadInputModule 嗅探魔数 → builtin 包裹 → 管线 → extract → writeBytecode。诊断流：optimize 的错误直接走 MLIR 默认 handler 打 stderr（cuda-tile-optimize.cpp:218-222 注释解释了为何不能前置挂 handler——context 在 optimizeTileIR 内部创建）。

## ⑤ 设计决策

三个设计点。其一，opt 与 optimize 的**双轨制**：同样叫"优化"，opt 走显式 textual pipeline（用户全权组合），optimize 走封装好的默认管线（optLevel 分级）——前者服务编译器开发者，后者服务流水线集成，CUDA Tile 没有把两者塞进一个工具。其二，translate 的 hint 开关注入发生在**反序列化时**（BytecodeTranslation.cpp:30-32）而非 parse 后：非法 optimization hints 的 warn/error 语义在读字节码的第一时间生效，与 opt 的 extension 注入（加载时）形成两条不同生命周期的配置通路。其三，optimize 的输出模式用位掩码组合（`BytecodeFile | MlirStdout` 可并存，cuda-tile-optimize.cpp:222-223），复用第 8 篇 emitOutputs 的"生成一次多路分发"。`-no-implicit-module` 选项在 translate 测试里几乎无处不在——它防止 MLIR parser 自动包 builtin module，保证 golden 字节比对不受容器层影响（encoding_stability 测试的隐含前提）。

## ⑥ 新人提示

跑 lit 前先确认工具在 PATH（lit.cfg.py 用 `config.cuda_tile_tool_dir`）；手工复现用 `cuda-tile-opt foo.mlir --pass-pipeline='builtin.module(cuda_tile.module(cuda_tile.entry(loop-split)))' --split-input-file | FileCheck foo.mlir`，注意 pass 要挂在与 op 匹配的嵌套层级（fuse-fma 挂 testing$func、loop-split 挂 entry，见第 12 篇）。translate 查版本矩阵：`cuda-tile-translate --list-versions` 列 13.1-13.4 与测试版 250.0/250.1。optimize 排"输出为空"先看是否 `-q` 与无 `-o` 组合；排"没优化"用 `--verbose` 打印实际管线串。改这三个 main 文件时克制——它们刻意保持薄，逻辑该进 lib/（translate 的翻译体在 BytecodeTranslation.cpp、optimize 的流程在 Optimizer），main 里塞逻辑会破坏 CAPI/CLI 共享内核的结构。源码勘误：无——行号经 2026-11 快照核实。

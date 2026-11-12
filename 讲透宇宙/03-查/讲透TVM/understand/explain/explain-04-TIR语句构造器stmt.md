# explain-04 · TIR 语句构造器：src/tirx/ir/stmt.cc（SBlock/While/Break 与新 FFI 反射）

## 角色定位

`src/tirx/ir/stmt.cc`（749 行）是 TIR **语句侧 AST 节点的 C++ 构造器与校验器总册**——explain-03 讲的是"表达式怎么算"，本文件讲"程序怎么写"：循环（For/While）、控制流（IfThenElse/Break/Continue/Return）、访存（BufferStore/BufferRegion）、缓冲管理（DeclBuffer/AllocBuffer/MatchBufferRegion）、以及调度层的锚点节点 SBlock/SBlockRealize。每个构造函数都是一座**类型与良构性检查站**：非法 IR 在构造时即被拒绝，而不是等 codegen 才炸。

本文件同时是观察 fork 两大改造的最佳窗口：其一，语句家族与上游差异明显——`Block` 改名 **SBlock**（"可调度 TIR"，配套 `SBlockRealize`，L652/L715），新增 **While/Break/Continue** 一等语句（L301/L336/L348，上游 TIR 没有后两者），`Allocate` 演化为 **DeclBuffer/AllocBuffer**（L360/L389，buffer 与内存声明解耦）；其二，FFI 层整体换成 `tvm::ffi` 新反射框架——`TVM_FFI_STATIC_INIT_BLOCK` + `refl::GlobalDef().def("tirx.XXX", ...)` 取代了上游的 `TVM_REGISTER_GLOBAL` 宏。

## 内部结构

文件节奏高度统一：每个节点 = 构造器（做 ICHECK 校验）+ 一个 static init block（注册反射与 Python 构造函数）。按行号走主线：

- **L37-93 匿名命名空间**：`RealizeBufferRegionSubscript`——把 Python 下标表达式（含 slice 三元组）实现为 BufferRegion 切片；L54 明确"non-unit step 不支持"，全点索引时直接降级为 BufferLoad（L59-66），slice 经 `arith::Analyzer` 化简 extent（L68-90）。它被注册为 `__subscript_expr_realize__` 类型属性（L114-115），这是 TVMScript 里 `A[i, j:k]` 能直接用的原因。
- **L95-121 反射注册总表**：StmtNode 家族 20 个节点逐个 `RegisterReflection()`。
- **For（L202-264）**：最重的校验。L217-219 要求 loop_var/min/extent 必须是标量整数；L224-241 的 `try_promote_imm_dtype` 是精致的类型规范化——当 min/extent 是字面量且与循环变量 dtype 不一致时，只要值可表示（`IntImmValueFits`，L191-198 手写补码/无符号边界判断）就提升为循环变量 dtype，否则报错；L243-250 最终钉死三者 dtype 全等。L246-251 对可选的 `step` 同样处理——**带步长循环是 fork 扩展**（`HasTrivialStep()` L266 判 +1）。L279-298 是 ForKind 的打印枚举：kSerial/kParallel/kUnrolled/kVectorized/kThreadBinding。
- **While/Break/Continue/Return（L301-357）**：控制流完备化。While 仅校验 condition 是标量（L303）；Break/Continue 无字段纯标记节点。
- **DeclBuffer（L360-379）**：**存储作用域规则执法现场**——scope 为空默认 "global"（L363-365）；`tmem` 作用域必须恰好一个 `allocated_addr`（L366-369，张量内存/TCU 类硬件的特性），而 global/shared/shared.dyn/local 禁止携带 allocated_addr（L370-373）。AllocBuffer（L389）只带 buffer 与 annotations。
- **SeqStmt（L407-431）**：两条硬规则——空序列禁止（"To write a no-op, use Evaluate(0)"，L420-422）、单元素序列禁止（"Use the node directly"，L423-425）；嵌套 SeqStmt 在构造期自动拍平（L408-418）。这保证了 IR 中 SeqStmt 永远是"真序列"。
- **BufferStore（L486-541）**：本文件最长的校验链。L488-491 维度匹配；L493-496 "只有最后一个索引可以是向量"（向量化访存的形状约束）；L498-533 是 **scalable vector（vscale/可伸缩向量，RISC-V RVV/SVE 风格）的 lanes 三方对账**：index lanes × buffer element lanes 必须等于 value lanes（L515-518），scalable 与非 scalable 不可混存（L504-509）。`GetLanesOrVScaleFactor`（L482-484）统一取 lanes 或 VScaleFactor。
- **BufferRegion（L556-587）**：区域的三个构造姿势——全量 `FullRegion`（L568）、从点构造 `FromPoint`（L576，Ramp 索引被还原为 base/stride*lanes 区间，L579-581）。
- **MatchBufferRegion（L598-642）**：把子视图绑定到既有 buffer 的合法性证明：scope 相等（L602）、dtype 相等（L605）、对齐整除（L610）、高维必须可证明为 1（L623 用 `analyzer->CanProve`）——依赖 arith 引擎做符号证明；L635 注释明言不检查 elem_offset 与 strides。
- **SBlock/SBlockRealize（L652-728）**：调度层的语义单元。SBlock 聚合 iter_vars/reads/writes/init/alloc_buffers/match_buffers（L652-669，另有简化构造器 L671）；SBlockRealize 是"实例化"——iter_values 数量必须等于 block 的 iter_vars 数量（L717-718）、predicate 必须 bool（L719-721）。这两者就是 s_tir 调度原语（explain-05）操作的目标。
- **TypeAnnotation（L738-746）**：以 `Call` 形式包装 type_annotation op 并注册 `TCallEffectKind=kPure`——收尾示范了 op 注册三件套。

## 外部连接

- **头文件**：`include/tvm/tirx/stmt.h`（节点字段定义）；`tvm/tirx/op.h`+`op_attr_types.h`（L27-29）。
- **新 FFI**：`tvm/ffi/reflection/registry.h`（L26）提供 `GlobalDef().def`；`TVM_FFI_STATIC_INIT_BLOCK` 保证静态注册顺序安全。Python 侧经 explain-01 的 tvm_ffi 桥按 "tirx.For" 等名字直接调到这些 lambda。
- **arith**：`tvm/arith/analyzer.h`（L23）——MatchBufferRegion/RealizeBufferRegionSubscript 都靠 `CanProve/Simplify` 做符号推理。
- **上下游**：上游供给是 TVMScript parser（构这些节点）与 relax `emit_te`（te→PrimFunc lowering 产物）；下游消费是 `src/tirx/transform/` 全部 pass、`verify_well_formed.cc`（重查这些不变量）、`src/target/` codegen（按 ForKind/thread_binding 生成 CUDA/LLVM 代码）、`src/s_tir/` 调度引擎（改写 SBlock 结构）。

## 数据流

以 TVMScript 写一个带 slice 的 block 为例：parser 构造 `SBlock`（reads/writes 用 BufferRegion）→ 下标语法 `A[bi*16 : bi*16+16]` 走 `__subscript_expr_realize__`（L114）进 `RealizeBufferRegionSubscript`，slice 差值被 Analyzer 化简成 extent → 循环写成 `For(loop_var, 0, n, kSerial, body)`，dtype 规范化在 L224-241 完成 → 之后任何 pass 用 StmtFunctor 遍历/重建，每次重建都再次过这些构造器校验——**IR 不变量的执行点在构造器，遍及程序全生命周期**。

## 设计决策

1. **构造即校验（ICHECK in constructor）**：非法 IR 无法被构造出来，所有 pass 的输出自动良构——把 verify 从"阶段任务"变成"持续不变量"，代价是构造路径稍慢。
2. **字面量 dtype 宽容策略**（try_promote_imm_dtype）：既不粗暴拒绝 `for i in range(n)` 里 int32 字面量配 int64 循环变量的常见混用，又用 `IntImmValueFits` 保证无损——可用性grammaticality与安全性的精细折中。
3. **SeqStmt 禁空禁单**：消灭规范形（canonical form）歧义，StructuralEqual/hash 无需处理退化情形。
4. **Break/Continue 入 IR**：让 TIR 能表达 CUDA 式 early-exit kernel（如 flash attention 内层循环），不再需要上层先做控制流消除——服务 fork 的 LLM kernel 生成线。
5. **tmem scope 特判**（L366-373）：为张量核心（Tensor Memory）类硬件预留 allocated_addr 通道，普通作用域显式禁止——新硬件特性以"构造期规则"而非文档约定的方式落地。

## 新人提示

- 报错 "An empty SeqStmt is prohibited" / "length of 1" 时直接用 `Evaluate(0)` 或 `SeqStmt::Flatten`（L420-425 的报错文案本身就是修复指南）。
- 遇到 BufferStore dtype mismatch，按 L515-518 的公式自查：value lanes = 最后一个索引的 lanes × buffer 元素 lanes。
- 查某语句的字段与不变量，先读构造器再读头文件——L202-264 的 For 校验比 stmt.h 注释更能说明约束。
- 调度代码里看到 SBlock/SBlockRealize 不要与上游 Block/BlockRealize 混淆：本 fork 的调度层叫 s_tir，S 前缀贯穿（详见 explain-05/06）。

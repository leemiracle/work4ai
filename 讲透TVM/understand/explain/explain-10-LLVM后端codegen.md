# explain-10 · LLVM 后端旗舰：src/target/llvm/codegen_llvm.cc（2568 行）

## 角色定位

`codegen_llvm.cc` 是 TVM **CPU 后端的中枢**——把 explain-04 的 tirx 语句树逐节点翻译成 LLVM IR，再交给 LLVM 优化管线出机器码，服务 x86/ARM/RISC-V/WebAssembly 全线 CPU 目标。文件头 L24 注明血统："Part of the code are adapted from Halide's CodeGen_LLVM"——TVM 的 CPU codegen 是 Halide 十年工程资产的直系继承。整份文件就是一个类 `CodeGenLLVM` 的方法集：既是 **IRBuilder 驱动器**（L180 起的 `builder_` 发射指令）、又是 **tirx→LLVM 类型系统映射表**、还是 **intrinsic 词典**（L1363 的 CreateIntrinsic 处理上百种内建）。

fork 特征在本文件同样密集：L23-24 的 `#ifdef TVM_LLVM_VERSION` 整文件条件编译（无 LLVM 构建时物理消失）；L32-36/L63-72 的**双版本适配**（LLVM ≥17 的 Triple 头、≥16 的 new PassManager vs 老的 legacy）；L104-120 匿名命名空间三函数引入 **scalable vector（vscale）一等支持**（RISC-V RVV/SVE），与 explain-04 BufferStore 的 lanes 对账遥相呼应；L1474-1486 把 fork 新增的 **Break/Continue 语句**经 `loop_frame_jump_tgts_` 循环帧栈降级为 LLVM br。

## 内部结构

**骨架（L128-590）**：构造器放这里并配注释（L124-127：unique_ptr 成员要求类型完整，"Put the constructor here"）；工厂 `Create`（L132-148）按 `"tvm.codegen.llvm.target_<target>"` 查全局函数——**目标特化子类的注册点**（如 amdgpu/cpu 的 llvm codegen 各自注册）；`Init/InitTarget`（L150/182）建 module/targetmachine；`AddFunction`（L238）→`AddFunctionInternal`（L319）逐 PrimFunc 生成 llvm::Function；`Verify`（L366）跑 IR verifier；`Finish`（L375）取走 module；`HandleImport`（L388）支持**直接吃 LLVM IR 文本**（`llvm.compile` 注入外部 IR）；`AddLinkModule`（L418）挂待链接模块。`Optimize` 有两副面孔：L438 起的 new-PM 版（PassBuilder + 四个 AnalysisManager 交叉注册，L470 起 pipeline 按 opt level 选 `default<O0..O3>` 字符串）与 L529 起的 legacy 版（`#else` 分支）——**同一函数名的版本双写**，LLVM 16 分水岭。

**类型与内存模型（L585-983）**：`DTypeToLLVMType`（L585）——scalable 向量走 `llvm::VectorType::get(etype, VScaleFactor, /*scalable=*/true)`（L626），定长走 FixedVectorType（L628）；`AddAliasInfo`（L670）给 load/store 挂 **alias.scope/noalias 元数据**——TIR 的 buffer 互不别名知识直接喂给 LLVM 的指针分析，这是 CPU 性能的隐形发动机；`GetAlignment`（L733）按 buffer 对齐与索引推指令对齐；`AllocateSharedMemory`（L762）为 CPU 线程作用域分配可见内存。

**访存与向量（L1726-2070）**：`BufferAccessHelper`（L1741）统一 load/store 的指针构造与 lanes 三方对账（L1766-1768，与 explain-04 L515 同一公式）；`VisitExpr_(TensorLoadNode)`（L1851）——fork 把 BufferLoad 升级成 TensorLoad 节点后的专属 visitor；`CreateMaskedLoad/MaskedStore`（L1895/1925）用 masked vector 指令实现带谓词的向量化访存；Ramp（L1998）/Shuffle（L2034）/Broadcast（L2059）三个向量表达式节点各自映射到向量 IR 构造；`Scalarize`（L1549）是向量搞不定时的逐 lane 兜底。

**表达式 visitor（L1564-1724）**：L1564 Var、L1570 IntImm、L1585/1603/1613 三组宏批量生成二元算子的 Create/Visit 对；**Div/Mod 的语义分派是必看点**（L1632-1658）：int→SDiv/SRem、uint→UDiv/URem、float→FDiv/FRem——explain-03 里 div 歧义被 Python 层强制显式化，这里的 `prim::DivNode` 就是 trunc 语义（C 行为）的直接体现；Min/Max 降级为 select（L1660-1671）；Select（L1706）、Let（L1711）。

**语句 visitor（L2072-2343）**：`BufferStore`（L2072）；**ForNode（L2112-2126）**：analyzer 先 Bind 循环域（L2114），kUnrolled 在此被警告忽略（L2115-2117，"consider set unroll_explicit=True"——unroll 靠 pass 而非 codegen），非 kSerial 直接 ICHECK 拒绝（L2119，parallel/vectorize/thread_binding 必须在更早的 pass 降级）；带 step 的循环 end 经 analyzer 化简（L2121-2122）；**WhileNode（L2128-2143）**：经典三基本块（cond/body/merge）+ PushLoopFrame/PopLoopFrame（L2138-2140）——Break/Continue（L1474-1486 在 CreateIntrinsic 的 builtin 分支里）就跳到栈顶的 backedge/exit 目标；**ReturnNode（L2145-2157）**：只接受 return 0（pass 期已归一化），并因"LLVM 基本块恰一个终止符"追加 ret_dummy 块（L2153-2156）——IR 约束的工程化处理范本；IfThenElse（L2160）、AllocBuffer（L2184）、AttrStmt（L2231）、AssertStmt（L2253）、Bind（L2259）、SeqStmt（L2298）、DeclBuffer（L2305）、Evaluate（L2339）。

**杂项与调试（L984-1180、L2344-2568）**：CreatePrintf（L1030，内核 printf 调试）、CreateCallExtern（L1082）、GetIntrinsicDecl（L1100，按版本找 LLVM intrinsic 重载）、EmitFloat16ConversionBuiltins（L1180，fp16 ABI 差异的地雷区）；调试信息线 EmitDebugLocation/AddDebugInformation/GetDebugType（L2344-2568）把 TVMScript 的 Span 映射成 DWARF——**kernel 在 gdb 里能按源码行断点**。

## 外部连接

- **上游**：tirx stmt/expr 树（explain-03/04）；`arith::Analyzer`（L2114 在用）；Target/LLVMTarget（llvm_instance.h 封装 LLVM 初始化的单例）。
- **兄弟后端**：`codegen_cpu.cc`（继承本类，加数学函数调用约定）、各 target 特化经 L134 的工厂模板注册。
- **下游**：Finish() 产出的 module 被编成 .o/汇编，进 runtime Module（explain-01 的 libtvm_runtime 加载）；WebAssembly 线还能输出 .wasm。
- **与调度层闭环**：dlight/meta_schedule 调出的循环结构（L2112 处理的正是它们的产物）决定向量化机会，AddAliasInfo 的 noalias 元数据决定 LLVM 能否自由重排。

## 数据流

PrimFunc 进入 AddFunctionInternal → 形参映射为 LLVM Argument、buffer 指针挂 alias info → 语句树递归 Visit：For→CreateSerialFor（L877，生成 phi+cmp+br 循环骨架）→ BufferStore→CreateBufferPtr+对齐 load/store（向量化时走 masked 变体）→ 表达式按 dtype 选指令（Div 的三分派）→ 函数完 → Verify → Optimize（new-PM pipeline）→ Finish 交回模块。整个过程中 builder_ 的插入点、loop_frame 栈、analyzer 的已知域共同维护"当前生成位置"状态。

## 设计决策

1. **一 visitor 一指令族**：树遍历器模式让 tirx 每种节点语义固定在一处（Div 的 S/U/F 三分派、Min→Select），新增节点=加一个 VisitExpr_——fork 加 While/Break/Continue 时此文件只需 ~30 行。
2. **双 LLVM 版本并存**（L438/L529、L63-72）：上游生态 LLVM 14-20 横跨 new/legacy PM，条件编译保全部——维护税换兼容面。
3. **unroll 提示不进 codegen**（L2115-2117）：循环展开决策留给 pass 管线（annotate 的 pragma 在更早的 tirx transform 消化），codegen 只信 kSerial——层次分明的单一职责。
4. **noalias 元数据前馈**（L670）：TIR buffer 不别名是构造期已知的事实，主动写进 IR 让 LLVM 不必保守——跨层知识传递的典型。
5. **Return 归一化 + dummy 块**（L2145-2157）：把"多返回点"这个图结构问题在 pass 期解决、codegen 期只剩 return 0，是降低后端复杂度的管线分工。

## 新人提示

- 改循环相关 bug 先读 L2112-2143（For/While 两个 visitor）+ L877 CreateSerialFor；Break/Continue 跳转目标在 L1474-1486。
- LLVM 版本编译错误先看 L32-72 的 include 分组——各版本头文件搬家史全在这两段里。
- 调试 kernel：`TVM_BACKEND=llvm` 下 CreatePrintf（L1030）产物 + 调试信息线（L2344 起）支持源码级 gdb。
- 看到 "Unroll hint get ignore" 警告别慌，按 L2117 提示改用 unroll_explicit 注记；kParallel 循环漏降级会撞 L2119 的 ICHECK——先查 LowerThreadAllreduce/ThreadBinding pass 是否跑了。

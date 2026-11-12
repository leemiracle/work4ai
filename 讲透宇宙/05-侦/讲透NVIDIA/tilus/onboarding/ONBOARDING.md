# tilus ONBOARDING（新人上船指南）

> 仓库：NVIDIA/tilus @ 20474568（2026-10-23）· 671 个分析文件 · 图谱 2782 节点 / 7099 边 / 14 层 / 15 步导览
> 本文全部行号锚基于上述 commit 的源码实证核对。

---

## 1. 仓库定位：tile 级 GPU kernel 编译型 DSL

tilus 是 NVIDIA 开源的**研究型 GPU kernel 编程语言**（DSL），定位介于 Triton 与手写 CUDA 之间：以**线程块（thread block）为编程粒度**、以**张量为一等公民**，并原生支持 **1-8 bit 任意位宽低精度类型**（`README.md`）。它不解释执行、不即时翻译成 Python 调用，而是走完整的**编译器管线**：Python DSL → Tilus IR → Hidet IR → CUDA C → NVCC → .so。

三条血统线决定了它的形态（`README.md:52-59` 致谢节）：
- **Hidet**：直接把 hidet v0.6.1 fork 内嵌为低层 IR 基座（`python/tilus/hidet/__init__.py:4` docstring 明示 "originally from hidet v0.6.1"）——tilus 自己只做上半场（DSL/布局/指令），下半场（表达式/语句/优化 pass/代码生成/NVCC）整套复用 hidet；
- **Triton**：tile 级抽象的思想来源，但 tilus 反其道而行——**显式控制**共享内存与寄存器张量（README 明言 "unlike Triton"）；
- **Hexcute**：自动布局推断（layout inference）思想的来源（`python/tilus/ir/layout/__init__.py` 模块摘要亦承认）。

版本动态：v0.1.0（2025/04，Ampere）→ v0.2.0（2025/07，Blackwell+Hopper 支持，B200 上 matmul 达 cuBLAS 级），对应 ASPLOS'26 论文（arXiv:2504.12984）。硬件目标由 `Target` 管理（`python/tilus/target.py:29`），默认架构探测 `get_default_target` 用 cuda-python 查设备能力映射到 sm_90/sm_100 等（`python/tilus/target.py:325`）。

一个值得进门就记住的形态判断：这个仓**按 agent 协作开发模式维护**——根目录 `CLAUDE.md`（95 行）沉淀了编译管线六步、IR 结构、pass 编写规范与 IRVisitor/IRRewriter 陷阱清单；`.claude/skills/` 下还挂着两个 agent 技能：`ncu-report`（271 行，解析 Nsight Compute 报告，`.claude/skills/ncu-report/SKILL.md`）与 `write-docs`（220 行，指令 docstring/RST 写作规范，`.claude/skills/write-docs/SKILL.md`）。读代码之前先读 `CLAUDE.md`，能省一半迷路时间。

## 2. 顶层入口：import tilus 之后你拿到什么

包入口 `python/tilus/__init__.py` 是一个 barrel：从 `hidet.ir.dtypes` 重导出全系列 dtype 别名（标准 f16/f32/i8..i64、任意位宽 f3e1m1..f8e5m2、int1b..int8b），并导出 script 体系——`from tilus.lang.instantiated_script import InstantiatedScript`（`python/tilus/__init__.py:101`）、`from tilus.lang.script import Script, autotune`（`python/tilus/__init__.py:102`）。注意：**没有 `tilus_script` 装饰器**，写 kernel 是类子类化风格 `class MyKernel(tilus.Script)`（见第 4 节与勘误）。

四个外围模块构成"库的外壳"：
- **target**：`Target` dataclass + 当前目标栈 `scope()`（`python/tilus/target.py:298`）——所有 pass/发射器都通过它感知目标架构；
- **option**：编译选项中枢——`cache_dir`（`python/tilus/option.py:124`）、`parallel_workers`（`python/tilus/option.py:136`）、`bench_warmup`/`bench_repeat`、`debug.dump_ir`（`python/tilus/option.py:174`，每 pass 后 dump IR 到缓存目录）；
- **tensor**：前端张量封装 `Tensor`（`python/tilus/tensor.py:27`，torch 张量桥接）+ `from_torch`（`python/tilus/tensor.py:102`）——host 侧数据进入 kernel 的入口；
- **compiler_fingerprint**：编译缓存指纹，目录内容 Merkle 哈希 `_leaf_digest`（`python/tilus/compiler_fingerprint.py:68`）+ 双阶段指纹 `frontend_fingerprint`/`backend_fingerprint`（`python/tilus/compiler_fingerprint.py:247,253`）——前端改动使 specialization 缓存失效、后端改动使编译产物失效，这是 CLAUDE.md 钉版的双阶段失效机制的实现。

编译产物加载在 `python/tilus/runtime/compiled_program.py`：`CompiledModule`（:20）/`CompiledProgram`（:35）动态加载 .so，`load_compiled_program`（:48）与缓存命中检查 `compiled_program_exists`（:65）。仓里唯一的预置 kernel 是类型转换 `Cast`（`python/tilus/kernels/cast.py:27`，本身也是一个 Script 模板类，可当参考实现读）。

## 3. 编译管线：六步总装

总驱动是 `python/tilus/drivers.py`（366 行），CLAUDE.md 钉版的六步：

1. **Verify**：`ir.tools.verify(prog)`；
2. **Optimize（Tilus IR）**：`optimize_program`（`python/tilus/drivers.py:63`）应用 `get_default_passes()`（`python/tilus/transforms/__init__.py:31`）——12 个 pass：declare_to_let → let_propagation → lower_assume → lower_param_only_expr → analyze_scalar → lower_print_tmem_tensor → **layout_inference** → lower_load_store → **layout_inference（再跑一遍）** → bound_aware_simplify → analyze_scalar → DCE。注意布局推断在管线中执行两次（lower_load_store 规范化访存参数后需重推）；
3. **Lower to Hidet IR**：`backends.codegen.generate_ir_module`（`python/tilus/backends/codegen.py:503`）——逐指令取发射器翻译；
4. **Optimize（Hidet IR）**：`optimize_ir_module`（`python/tilus/drivers.py:97`）串 32 个 hidet pass（unify_global_objects → inline_register_tensor → lower_subbyte_type → generate_launch_func → ... → deadcode_elimination，全列表在 `python/tilus/drivers.py:146-182`）；
5. **Codegen**：Hidet IR → CUDA C 源码（`python/tilus/hidet/backend/codegen.py:1166` 的 `codegen()` 入口）；
6. **Compile**：NVCC 编 .so（`python/tilus/hidet/backend/build.py:127` 的 `NVCC` 类 + :270 `compile_source`）。

缓存三层结构（CLAUDE.md:5-8）：`/scripts/`（模板+调参空间）→ `/programs/`（具体 schedule 实例）→ `/specializations/`（持久化的 script 特化清单，键含用户代码、闭包值、外部依赖快照；不可追踪依赖触发保守回退）。缓存目录随时可安全删除。

Pass 框架自身：`PassContext`（`python/tilus/transforms/base.py:25`，带 instrument 挂点）、`Pass` 基类（:68，覆写 `process_function`）、应用入口 `apply_transforms`（:86）。调试时 `DumpIRInstrument`（`python/tilus/transforms/instruments/dump_ir.py`）把每 pass 后的 IR 落盘到缓存目录 `ir/` 与 `module/ir/`。

## 4. DSL 前端：tilus Script 与实例化引擎

用户 API 是**类子类化**：`class MatmulV1(tilus.Script)`（`examples/matmul/matmul_v1.py:20`），`__init__` 放编译期配置（block_m/block_n 等），`__call__` 写 kernel 体。`Script.__new__` 直接返回 `InstantiatedScript`（`python/tilus/lang/script.py:49-56`）——所以"实例化 Script 类"得到的不是 Script 对象而是实例化引擎的句柄。调参空间用 `autotune` 装饰器声明（`python/tilus/lang/script.py:106`），它只是往类上挂 `_autotune_space` 字典。

kernel 体内的 `self.*` 指令面由 `RootInstructionGroup` 提供（`python/tilus/lang/instructions/root.py:32`，2200 行、77 个方法，仓内最大文件）：`load_global`（:476）/`store_global`（:528）/`store_shared`（:645）/`load_shared`（:619）/`free_shared`（:688）/`dot`（:856）/`cast`（:938）/`scan`（:1684）/`sync`（:1889）等全套；Blackwell 的 `self.tcgen05.*`、TMA 的 `self.tma.*`、mbarrier 的 `self.mbarrier.*` 各自独立成组（`python/tilus/lang/instructions/tcgen05.py` 等 12 个指令组）。

**实例化引擎**是 tilus 的核心运行时（`python/tilus/lang/instantiated_script.py`，1148 行）：
- `CallParameters`（:236）规范化调用参数；`extract_keys`（:340）把参数分为常量键与调参键（int 按 2 的幂/16 整除性分桶，`_tuning_key_part`:334）；
- `span_space`（:54）+ `generate_schedules`（:108）枚举 autotune 调度空间；
- `JitInstance`（:395）是 transpile→build→tune 全流程的载体：`_transpile_programs`（:629）跑转译、`_build_programs`（:760）并行编译、`_pick_best_program`（:874）autotune 选优；
- `InstantiatedScript`（:995）是用户侧对象，`_jit_instance_for`（:1088）是 CLAUDE.md 钦点的测试入口（拿 `ji.transpiled_programs[0]` 即得 Program）；`InstantiatedScriptCache`（:1108）按调用形状缓存。

Python AST → Tilus IR 的转译器在 `python/tilus/lang/transpiler/transpiler.py:82`（`Transpiler` 继承 `ScopedProgramBuilder` + `PythonAstFunctor`）；`for` 循环经 `RangeLoop`（`python/tilus/lang/constructs/loops.py:35`）落成 ForStmt。转译依赖快照由 `script_dependency_fingerprint`（`python/tilus/lang/script_dependencies.py:62`）保守捕获。指针参数语法糖是类型注解 `a_ptr: ~float16`（`examples/matmul/matmul_v1.py:33`，DataType 的 `~` 反转运算符重载）。

## 5. Tilus IR：语句-指令-张量三级结构

CLAUDE.md 钉版的层级（`CLAUDE.md:28-37`）：
- **Program**（`python/tilus/ir/prog.py:25`）= `frozendict[str, Function]`，编译单元；
- **Function**（`python/tilus/ir/func.py:84`）= name + params + body(Stmt) + `Metadata`（:45，GPU 指令属性）+ `Analysis`（:28，缓存的分析结果）；
- **Stmt**（`python/tilus/ir/stmt.py:27` 基类）：控制流族 SeqStmt（:32）/ForStmt（:41）/IfStmt（:96）/WhileStmt（:106）/LetStmt（:134）；**ThreadGroupStmt**（:54，warp/warpgroup/单线程域限定）；张量-Hidet 变量桥 TensorItemPtrStmt（:154）/TensorItemValueStmt（:161）；**InstStmt**（:167）包装一条 Instruction 挂进语句树——指令进语句树的唯一形态；
- **Instruction**（`python/tilus/ir/inst.py:25`，frozen dataclass）：`output: Optional[Tensor]` + `inputs: tuple[Tensor,...]` + 类型专属属性。是否"功能性（可删除）"由 **DCE 里的显式 allowlist** 判定（`python/tilus/transforms/dead_code_elimination.py:76` 的 `FUNCTIONAL_INST_TYPES` + :129 isinstance 判定），副作用指令永不消除；
- **Tensor**（`python/tilus/ir/tensor.py`）四级存储身份：基类（:30）+ RegisterTensor（:82，35 方法）/SharedTensor（:549）/TMemoryTensor（:661）/GlobalTensor（:767），全部 identity-based frozen dataclass（`eq=False`，按对象身份判等）。

指令全集分两族：**架构无关 generic**（`python/tilus/ir/instructions/generic.py`：AssignInst:31、LoadGlobalInst:71、StoreSharedInst:121、AddInst:390、ReduceInst:501、ScanInst:526、ViewInst:564 等约 50 类）与 **CUDA 扩展族**（`python/tilus/ir/instructions/cuda/`）：Ampere cp_async、TMA 四向 bulk 拷贝（`python/tilus/ir/instructions/cuda/cp_async_bulk.py:26-116`）+ mbarrier 全家（`python/tilus/ir/instructions/cuda/mbarrier.py:27-111`）、Hopper wgmma（`python/tilus/ir/instructions/cuda/wgmma.py:36-96`）、Blackwell tcgen05 全家族（`python/tilus/ir/instructions/cuda/tcgen05.py:27-162`：Alloc/Dealloc/Slice/Load/Store/Copy/MmaSS/MmaTS）与 CLC 工作窃取（`python/tilus/ir/instructions/cuda/clc.py`）。另有不产代码只影响优化的 hint 指令：`AnnotateLayoutInst`（`python/tilus/ir/instructions/hints.py:26`）与 `AssumeInst`（:41）。

两个分析器支撑 pass 决策：`GridAnalyzer`（`python/tilus/ir/analyzers/grid_analyzer.py:431`）把 script 自由维分析成网格/循环结构（autotune 空间推导引擎）；`ScalarSetAnalyzer`（`python/tilus/ir/analyzers/scalar_analyzer.py:321`）做标量取值集分析（ScalarSet :78，区间+枚举混合）——布局合法性证明与守卫消除（bound_aware_simplify）的数学引擎。

## 6. 布局系统：tilus 的灵魂

布局（Layout）描述"一个张量的元素如何分布在存储层级与线程上"，三个中枢 dataclass：
- **RegisterLayout**（`python/tilus/ir/layout/register_layout.py:35`，491 行）：`local × spatial × replicated` 的代数结构——spatial=哪些元素分给哪些线程（`python/tilus/ir/layout/ops/register_ops.py:29`）、local=每线程私有部分（:65）、replicated=跨线程复制（:101）；其上有 compose（:231）/permute/reshape/divide/left_divide 全代数变换（`ops/register_ops.py` 975 行 19 个函数）；
- **SharedLayout**（`python/tilus/ir/layout/shared_layout.py:88`）+ Swizzle（:30）：共享内存 stride 代数与 bank conflict 消除模式；swizzle 模式计算在 `shared_row_major_swizzle`（`python/tilus/ir/layout/ops/shared_ops.py:283`）；
- **GlobalLayout**（`python/tilus/ir/layout/global_layout.py:25`）：shape+strides。

**自动布局推断**（借鉴 Hexcute）让用户不写布局：
- 协议层：`LayoutInferenceRule`（`python/tilus/ir/layout/inference/rule.py:56`，静态方法 `inference`）与 `LayoutValidationRule`（:37，静态方法 `validate`）；`register_rule`（:100）注册、每指令可挂多条规则（`_inference_rules` defaultdict(list)）；
- 规则族：`inference_rules/` 27 个文件、45 个 Rule 类，逐指令定制——MmaDotRule（`python/tilus/ir/layout/inference/inference_rules/mma_dot.py:24`，按 MMA 碎片约定推 A/B/C 布局）、LoadStoreGlobalRule 族（`python/tilus/ir/layout/inference/inference_rules/ldst_global.py:25,93,103`，含向量化宽度约束）、BinaryRule（`python/tilus/ir/layout/inference/inference_rules/elementwise_binary.py:22-28`，双操作数+输出共享布局）、AssignRule（`python/tilus/ir/layout/inference/inference_rules/assign.py:22`）等；
- 主算法 `infer_layout`（`python/tilus/ir/layout/inference/inference.py:160`）：收集缺布局指令 → 按 `(已定布局优先, 规则全局序, 程序逆序)` 三元组排序（`pair_sort_key` :246-253）→ 每轮只应用一条规则并重写函数 → 循环到不动点；无规则可用即抛 `LayoutInferenceError`（:322 附近）而非静默停止。**规则全局序是手工调优的优先级表**（`python/tilus/ir/layout/inference/order.py:56` `inference_order` → :90 `rule2order`）：TMEM 规则最先，mma/wgmma 次之，元素级再次，共享内存规则殿后；
- 管线入口：`LayoutInferencePass`（`python/tilus/transforms/layout_inference.py:69`）先由 `ApplyLayoutAnnotationRewriter`（:26）应用用户的 `AnnotateLayoutInst` 标注，再调主算法；`verify_layouts`（python/tilus/ir/layout/inference/inference.py:323）终检一致性。

与 CUTLASS 的互操作词汇翻译层在 `python/tilus/ir/layout/utils/cute.py`（CuteLayout/CuteSwizzle/SwizzledCuteLayout）；tcgen05 硬件布局约定对接层是 CanonicalSharedLayout（`python/tilus/ir/layout/cuda/tcgen05/smem.py:75` + `canonicalize_shared_layout`:166 + `generate_canonical_layout`:307）。

## 7. 后端发射：指令 → Hidet IR

下降核心 `FunctionCodegen`（`python/tilus/backends/codegen.py:76`，26 方法）：遍历 Tilus 语句树，对每条指令 `resolve_inst_emitter`（:123）查全局注册表取发射器；`ProgramCodegen`（:487）+ `generate_ir_module`（:503）组装整个 Program。注意 `resolve_inst_emitter` 按 REGISTRY **迭代序取第一个匹配父类即 break**（:124-131）——发射器注册顺序参与解析语义。

发射器框架：`BaseInstEmitter`（`python/tilus/backends/emitter.py:34`，33 方法）+ `register_emitter` 装饰器（:267，按 (指令类型, target) 二维注册，重复注册直接抛错）。发射器家族 22 个模块（`python/tilus/backends/emitters/`）+ CUDA 专属 15 个（`emitters/cuda/`）+ Blackwell 子包：cp_async（Ampere）、cp_async_bulk（TMA 四方向，`python/tilus/backends/emitters/cuda/cp_async_bulk.py:142,172,197,237`）、mbarrier、wgmma（Hopper，`python/tilus/backends/emitters/cuda/wgmma.py:115` WgmmaMmaSSEmitter + SharedMatrixDescriptor:54 做 LBO/SBO/swizzle 位域编码）、tcgen05 全家（alloc/ldst/copy/mma 四模块，`python/tilus/backends/emitters/cuda/tcgen05/mma.py:199` TMemoryMmaSSEmitter + `Tcgen05MmaInstDesc`:60 指令描述符位域）、CLC 工作窃取（`python/tilus/backends/emitters/cuda/blackwell/clc.py:25,40`）。指令底层的 PTX 原语注册在 hidet 基座：`register_tcgen05_instructions`（`python/tilus/hidet/ir/primitives/cuda/tcgen05.py:268`，228 行巨型注册函数，9 个 Kind 枚举）+ 描述符编码 `tcgen05_encode_smem_descriptor`/`tcgen05_encode_mma_inst_descriptor`（同文件 :545,:559）。

发射期资源由上下文族管理（`python/tilus/backends/contexts/`）：`EmitContexts`（`python/tilus/backends/contexts/contexts.py:27`）聚合全部子上下文——共享内存分配器 `SharedMemoryAllocator`（`python/tilus/backends/contexts/smem_alloc_ctx.py:28`，first-fit 空闲槽 + 相邻合并，决定最终 dynamic shared memory 大小）、全局内存池化分配、mbarrier 槽位表（`python/tilus/backends/contexts/mbarrier_alloc_ctx.py:33`）、TMEM 分配状态（`python/tilus/backends/contexts/tcgen05_ctx.py:23`）、leader lane 跟踪、循环不变量跟踪。发射完成后 `inline_register_tensor_pass`（`python/tilus/backends/transforms/inline_register_tensor.py`）在 Hidet IR 上做后处理，把单用途寄存器张量内联掉以降压寄存器压力。

## 8. hidet 基座：下半场全套

`python/tilus/hidet/` 是 fork 自 hidet v0.6.1 的完整编译器（115 文件的 IR + 30 个 transforms 文件 + backend + lang DSL）：
- **IR 层**：`Expr`（`python/tilus/hidet/ir/expr.py:55`，41 方法）+ Var（:539）/Call（:416）/Let（:425）；Stmt 族含 **AsmStmt**（`python/tilus/hidet/ir/stmt.py:306`，内联 PTX 的落点）与 **LaunchKernelStmt**（:342，host 侧 kernel 启动）；类型系统（`hidet/ir/type.py`）与 dtype 注册中心（`hidet/ir/dtypes/__init__.py`）——tilus 顶层 `import tilus` 拿到的全部 dtype 别名其实来自这里；
- **原语系统**：`PrimitiveFunctionRegistry`（`python/tilus/hidet/ir/primitives/func.py:33`）管理全部 PTX/intrinsic 原语函数表；数学函数集按 dtype 分发（`primitives/math.py`）；集群/cvta/tcgen05 等 CUDA 原语在 `primitives/cuda/`；
- **优化 pass**：hidet 层 `Pass`（`python/tilus/hidet/transforms/base.py:58`）+ `lower_with`（`python/tilus/hidet/transforms/__init__.py:62`）串接；代表作：规则化简引擎（`python/tilus/hidet/transforms/_rule_based_simplifier_base.py:160` RuleBasedSimplifier，模式规则表 + any_expr/int_constant 通配）、**lower_subbyte_type**（759 行，子字节类型的字节地址+位偏移改写，tilus 1-8bit 类型真正落地的地方）、lower_affine_to_recurrence（仿射→归纳变量强度消减）、hoist_loop_invariants、deadcode_elimination；
- **hidet 自带 DSL**：`@script` 装饰器 + PythonToHidetTranslator（`python/tilus/hidet/lang/transpiler.py:406`，46 方法 AST 直译）——tilus Script 的转译器在结构上与它同构，但目标是 Tilus IR；
- **codegen 与编译**：`Codegen` 基类（`python/tilus/hidet/backend/codegen.py:81`，71 方法）→ CUDACodegen（:776）→ UpdatedCUDACodeGen（:884，表达式美化版）；HIPCodegen（:1045）/CPUCodegen（:1115）存在但 tilus 仅面向 CUDA（AMD 侧仅 AmdgpuCastInstEmitter 占位）；最终 NVCC 编译（`python/tilus/hidet/backend/build.py:127`，并行 job+缓存键+CompilationFailed 错误报告）。

## 9. 上手路线与调试工具箱

推荐阅读顺序（15 步导览的浓缩版）：
1. `README.md` + `CLAUDE.md`（形态与铁律）→ `examples/matmul/matmul_v1.py`（最完整的入门样例：global_view/shared_tensor/register_tensor/dot/sync 全链路）；
2. `examples/` 按硬件进阶：Ampere matmul v0-v5 → Hopper matmul v0-v3（TMA/wgmma 渐进引入）→ Blackwell matmul v0-v6（v6 达 cuBLAS 级）→ attention v1-v3 / attention_with_kvcache / flash_attention_decode（tilus/torch/triton 三框架对照）/ moe / quantization / softmax / norm；
3. 对照 `docs/source/tutorials/`（41 篇，与示例一一对应）与 `docs/source/programming-guides/`（19 篇，instructions.rst 418 行最长）；
4. 改动后先跑冒烟：CLAUDE.md 钉版先 `tests/kernels/matmul/test_matmul_v2.py` 再全量（全量慢）。

调试工具箱：`tilus.option.cache_dir(...)` 指缓存目录看生成的 source.cu；`debug_schedule=dict(...)` 钉单一 schedule 只编译一份；`tilus.option.debug.dump_ir()` 每 pass 落 IR；`transforms/inject_print_instruction.py` 往 kernel 里插打印查中间值；profiler 框架（`python/tilus/utils/profiler/`）+ `/ncu-report` skill 吃 ncu 报告；基准用 `benchmark_func`（`python/tilus/utils/bench_utils.py`，cuda_sleep 隔离计时 + L2 清空）。

两个高频坑（CLAUDE.md 钉版）：① `store_shared` 后接 `tma.shared_to_global` 必须 `self.fence.proxy_async(...)`（generic proxy 写 → async proxy 读的可见性，否则 TMA 读到脏数据，CLAUDE.md:69-83）；② IRRewriter 的 memo 按身份缓存不重访、`visit_Expr` 不下钻 Hidet 子表达式、指令属性里的 Var 要扫 `inst.attributes`（CLAUDE.md:50-55）。

## 10. 一页速查

| 概念 | 落点 |
|---|---|
| 编译六步 | `python/tilus/drivers.py:302` build_program |
| Tilus 默认 12 pass | `python/tilus/transforms/__init__.py:31` |
| Hidet 默认 32 pass | `python/tilus/drivers.py:146-182` |
| 指令→语句树 | `python/tilus/ir/stmt.py:167` InstStmt |
| functional 判定 | `python/tilus/transforms/dead_code_elimination.py:76` |
| 布局推断主算法 | `python/tilus/ir/layout/inference/inference.py:160` |
| 规则优先级表 | `python/tilus/ir/layout/inference/order.py:56` |
| 发射器注册 | `python/tilus/backends/emitter.py:267` |
| tcgen05 PTX 原语 | `python/tilus/hidet/ir/primitives/cuda/tcgen05.py:268` |
| 共享内存分配器 | `python/tilus/backends/contexts/smem_alloc_ctx.py:28` |

（完）

# 04 · hidet 基座与优化 pass（python/tilus/hidet/）

## 1. 角色定位

`python/tilus/hidet/` 是**整套 fork 内嵌的 hidet v0.6.1 编译器**（`python/tilus/hidet/__init__.py:4` docstring："Hidet IR/transforms/backend integrated into tilus (originally from hidet v0.6.1)"）。tilus 复用它作为编译下半场：低层 IR（表达式/语句/类型）、30 个优化与 lowering pass、CUDA 代码生成器、NVCC 调度、ctypes 运行时加载，以及一份自己的 Python DSL。图谱 L08-L11 四层（约 190 文件）都属它。对读者的意义：**看 tilus 生成的 CUDA 为什么长那样，答案大半在这个目录**。

## 2. 内部结构

四块拼图：

**IR 数据结构**（L09，115 文件）：`Expr` 基类（`python/tilus/hidet/ir/expr.py:55`，41 方法）+ 全部二元/一元/条件/Let（:425）/Call（:416）/Constant（:442）/Var（:539）dataclass 与 36 个构造辅助函数；Stmt 族（`python/tilus/hidet/ir/stmt.py`，455 行）含两个特殊节点——**AsmStmt**（:306，内联 PTX/汇编的落点，tcgen05/wgmma 最终都走它）与 **LaunchKernelStmt**（:342，host 侧启动）；类型系统 `type.py`（482 行）与 dtype 注册中心（`python/tilus/hidet/hidet` 不对——`python/tilus/hidet/ir/dtypes/__init__.py`，279 行：boolean/int8-64/float16-64/bfloat16/tfloat32 及**子字节类型单例**——tilus 任意位宽类型的注册地）；模块级 IRModule（`python/tilus/hidet/ir/module.py`，全局变量+函数表，`merge_ir_modules` 供链接期合并）。

**原语系统**：`PrimitiveFunctionRegistry`（`python/tilus/hidet/ir/primitives/func.py:33`）管理全部 device 原语函数表（register/lookup/is_primitive/call）；数学函数按 dtype 分发（`primitives/math.py`，MathFunctionSet 39 方法）；CUDA 专属原语在 `primitives/cuda/`——thread_idx/block_idx 内建变量（`vars.py`）、集群 14 入口（`cluster.py`）、cvta 地址空间互转（`cvta.py`）、**tcgen05 原语总库**（`primitives/cuda/tcgen05.py`，645 行：9 个 Kind 枚举 + `register_tcgen05_instructions`:268 巨型注册函数 + 描述符编码 :545/:559）。

**优化 pass**（L10，30 个 transforms 文件）：hidet 层 `Pass`（`python/tilus/hidet/transforms/base.py:58`）+ `lower_with`（`python/tilus/hidet/transforms/__init__.py:62`）串接。代表作四件：规则化简引擎（`python/tilus/hidet/transforms/_rule_based_simplifier_base.py:160` RuleBasedSimplifier——模式规则表驱动，`any_expr`/`int_constant` 通配 :66-74，C 截断语义辅助 `c_trunc_div`/`c_trunc_mod` :85-100；`rule_based_simplifier.py` 在其上加 bound-aware 分支排除）；**lower_subbyte_type**（759 行，`Addressing` 分析子字节寻址 :46，把 1-8bit 张量的存储/加载/地址算术全改写为字节地址+位偏移——tilus 低精度卖点的落地现场）；lower_affine_to_recurrence（434 行，仿射→每步 += stride 的归纳变量强度消减）；deadcode_elimination（220 行，DeadcodeAnalyzer 22 方法活性分析）。

**hidet 自带 DSL 与后端**：`@script` 装饰器（`python/tilus/hidet/lang/script.py`，源码捕获 + eliminate_indent 预处理）与 AST 直译器 `PythonToHidetTranslator`（`python/tilus/hidet/lang/transpiler.py:406`，46 方法）——与 tilus Script 的 Transpiler 同构但目标为 Hidet IR；codegen（`python/tilus/hidet/backend/codegen.py`：Codegen 基类 :81 71 方法 → CUDACodegen :776 → UpdatedCUDACodeGen :884 表达式美化版 → HIPCodegen :1045 / CPUCodegen :1115 占位）；NVCC 编译（`python/tilus/hidet/backend/build.py:127` NVCC 类，并行 job、缓存键、`CompilationFailed`:46 错误报告，入口 `compile_source`:270）。

## 3. 外部连接

tilus 顶层的 dtype 别名**全部来自这里**（`python/tilus/__init__.py` 从 hidet.ir.dtypes 重导出）——用户写 `tilus.float16` 实际拿到 hidet 的类型单例。工具层双向转发避免双份实现：`hidet/utils/__init__.py` 从 tilus.utils 转发公共工具（NOTES-DIGEST 钉版："canonical 实现在 tilus.utils.py，hidet 侧引用旧路径由此适配"），`doc.py` 排版库合并自两边。上游消费者是 `optimize_ir_module`（`python/tilus/drivers.py:97`）——Tilus IR 经发射器降成 IRModule 后，在此串 32 个 hidet pass（全列表 `python/tilus/drivers.py:146-182`：unify_global_objects → inline_register_tensor → bind_predefined_variables → lower_subbyte_type → generate_launch_func → ... → simplify_stmt → deadcode_elimination）。运行时出口：生成源码 include 的 C 头就在 `python/tilus/hidet/include/tilus/`（context.h 流管理、float8_e4m3/e5m2 软件编解码 fallback、TVM FFI 桥接头）。

## 4. 数据流（lower_subbyte_type 一个样本）

tilus 层一个 `i3` 张量的 Cast 指令降到底层后，Hidet IR 里仍是子字节类型——CUDA 没有原生 3bit 算术。`lower_subbyte_type_pass` 的处理链：`Addressing`（python/tilus/hidet/transforms/lower_subbyte_type.py:46）先分析每处子字节访问是"整字节对齐+位偏移"还是"跨字节"；Rewriter 随后把子字节 BufferStore/Load 改写为相邻字节的 load→移位掩码→store（位拼装），把子字节地址算术改写为 `byte_addr = bit_addr // 8` + `bit_offset = bit_addr % 8`；配合 `lower_integer_subbyte`（392 行，子字节**算术/比较**改写为字节级位操作，含符号扩展）与 `lower_special_cast`（bfloat16/tfloat32 无 C 对应转换时改写为位操作原语），三层接力后 IR 只剩标准 C 类型。这条链是 README"任意位宽低精度"承诺的全部代价所在——也是 ASPLOS'26 论文的主题。

## 5. 设计决策

**fork 整个 hidet 而非依赖 pip 包**：tilus 需要改 hidet 内部（原语注册、tcgen05、子字节支持），fork 内嵌让两端同步演进、版本耦合可控；代价是仓体积与 hidet 上游修复不自动流入。**UpdatedCUDACodeGen 的存在**（python/tilus/hidet/backend/codegen.py:884）：新版表达式美化与旧版并存，由目标/选项选择——hidet 式"渐进迁移"风格，名字直白到近乎草率。**HIP/CPU codegen 保留但不用**：fork 携带的遗产，tilus 只面向 CUDA（AMD 侧仅 `emitters/cast.py` 的 AmdgpuCastInstEmitter 占位）——读代码时别被 HIP 路径迷惑。**规则化简做成规则表而非 ad-hoc if**：模式通配 + 规则注册让简化可扩展可测试；Sum 中间表示（ConvertAddSubToSum/MergeTerm）处理结合律下的系数合并。**pass 序列里 resolve/import 原语跑三遍**（python/tilus/drivers.py:162-169）：原语解析会引入新表达式再需解析——pipeline 的单调性让位于实用性。

## 6. 新人提示

- 别在 `hidet/lang/` 学写 kernel——那是 hidet 原生 DSL，tilus 用户面是 `tilus.lang`；hidet DSL 在仓里主要被运行时与启动函数生成使用。
- 找生成代码为何某种写法：缓存目录 `module/ir/`（dump_ir 开启时）按 pass 序看 Hidet IR 演化，最后看 `source.cu`。
- 拼写陷阱两处：`lower_affine_to_recurence.py`（recurence）与 `hidet/utils/py.py` 转发层；import 时以函数名为准。
- 子字节类型调试：`nbytes_from_nbits`（`python/tilus/utils/py.py`）与 dtype 单例的 nbytes 属性是尺寸计算的事实源。
- 想理解 tcgen05 的 PTX 细节，先读 `primitives/cuda/tcgen05.py` 的 9 个 Kind 枚举（:32-178）再读发射器——枚举即 PTX 参数空间的完整编码。

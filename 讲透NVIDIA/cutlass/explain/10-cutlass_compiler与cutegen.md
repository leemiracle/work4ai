# 10 · cutlass_compiler 与 cutegen：C++ MLIR 编译器栈与数值代数库

## 角色定位

`cutlass_compiler/`（图谱域 462 文件，file 节点 426）是 CuTeDSL 的 C++ 编译器后端：cute MLIR 方言 → base 层 → LLVM/cubin 全管线，外加 cutegen 数值代数库。由 LLVM/MLIR 驱动（LLVM_COMMIT 钉版 23a60f15…958b732），测试面 347（322 .mlir + 25 .cpp）。第 08 篇 PyIR 产出的 IR 交给这里收尾。

## 内部结构

**三层组织**：`base/` 是"cute 降级后的上游方言集合"（arith/scf/gpu/LLVM/NVVM，README 称伪方言）；`cute_ir/` 定义 cute 方言本体；`tools/cutlass-compiler/` 全管线驱动。三个 opt 工具同构复用 `MlirOptMain`：base-opt.cpp:84、cute-opt.cpp:82、cutlass-compiler.cpp:85——头注释钉版分工：本工具=全管线，cute-opt/base-opt=单层隔离。

**base 层**刻意不注册 cute 方言（base/include/base/Registration/Registration.h 头注释），泄漏引用在解析期即报 unregistered dialect 错——测试隔离边界。`registerBaseDialects`（RegisterBase.cpp:61）insert arith/cf/func/NVVM/scf/ub（L63-65）；陷阱注释钉版：SCF 无直降接口先转 cf（L71）、NVVM TargetAttrInterface 是外部模型（L81）。三个 pass（Passes.td）：`BasePrepare`（Passes.td:39）、`AttachNVVMTarget`（L135，暴露 chip/features/optLevel）、`EmitGPUBinary`（L173，`compilationTarget` L187 支持 bin/cubin/fatbin/llvm）。`OneShotConvertToLLVM.cpp` 两阶段 convertHostCode（L79）/convertGPUModule（L109）都用 `ConvertToLLVMPatternInterface` 钩子收集方言 pattern（L92/L128）。

**cute_ir 方言**把布局编进类型系统：`CuteTypes.td` 的 `Cute_IntTupleType`（CuteTypes.td:47）与 `Cute_CoordType`（L104）——静态签名编进类型后 SSA 值即携带完整布局信息，`?` 是动态槽位（默认 i32，`?{i64}` 显式位宽，示例 L71-77）。操作面（CuteOps.td）：`StaticOp`（L46，编译期常量完全编进结果类型——同型两个 static op 即同值）、`MakeIntTupleOp`（L124）、`MakeLayoutOp`（L541）、`MakeComposedLayoutOp`（L740）。命名约定：def 带 Cute_ 前缀，tablegen 生成时剥前缀得 C++ 类名。降级实现 `ExpandOps.cpp` 的 `buildLayout` 两重载（L88/L103）是 layout 构造底座，`InverseOpConversion` 模板统一左右逆；属性 storage 手写（genStorageClass=0），CuteAttributes.cpp 的 .cpp.inc 必须晚于 storage 定义。

**cutegen**（17 个头文件）是 C++ 数值代数层：`comp_pred` 枚举（cg_int.hpp:273）+`compare` 四谓词特化（L283-308）是代数值比较统一入口；`dynamic_t`（dynamic.hpp:111）经 `has_dynamic_t_base`（L358）trait 判定继承；`rec_var_base`（rec_var.hpp:128）以 std::variant 承递归变体，`wrapped_value_t`（L91）显式控制嵌套层级；swizzle.hpp:65-68 头注释给出 N_MASK=4,NUM_SHIFT=11,NUM_BASE=4 位变换示例；`llvm_type_sparse_flat_t`（cutegen_mlir.hpp:892）让动态叶在 LLVM struct 稀疏排布（`llvm_type_generator` 特化 L906）；charconv.hpp:56 用 `__has_include` 而非 `__cpp_lib_to_chars` 探测；rec_var_algorithms.hpp 的错误以 cg_error_t 在类型系统内传播。

## 外部连接

构建依赖链：`cutlass_compiler/cmake/LLVM.cmake` 捆绑模式设定 `LLVM_ENABLE_PROJECTS "mlir"`（LLVM.cmake:57）、关 MLIR Python bindings（L63）与 examples/tests/benchmarks；`Standalone.cmake` 被 CMakeLists.txt include（L35），`AddBase/AddCute` 包装函数（L62 起）落回 dialect/conversion 函数。顶层把 Assert 构建型映射为 Release+LLVM_ENABLE_ASSERTIONS，RUN_CUDA_SM90_TESTS 控制 SM90 真机集成测试。脚本：`run_integration_host.sh` 自述 canonical 入口（LIT 经 substitution 调同一命令行）；`run_integration_device.sh` 的 resolve_target_sm 三级回退（env→TEST_GPU_ARCH→sm_90）；`test/Integration/lit.cfg.py` GPU 可见性三函数探测链。它是 CuTeDSL `CUTE_DSL_USE_EXTENSION_COMPILER=1` 管线（CHANGELOG 4.8.0 预览）的落点。

## 数据流

CuTeDSL/PyIR 产出 cute 方言 module → `cute-opt` 单层检查/变换 → `cutlass-compiler` 全管线：cute→base 降级（ExpandOps）→ `BasePrepare` 清理（算术简化/CSE/LICM）→ `AttachNVVMTarget` 挂目标 → `OneShotConvertToLLVM` 降 LLVM → `EmitGPUBinary` 序列化 cubin/fatbin。测试金字塔：322 个 .mlir lit 用例按 Conversion/{BasePrepare,NVVMLowering,OneShotConvertToLLVM} 分层 + cute_ir 自测 + cutegen 单测（cg_tuple_test.cpp 2148 行 61 TEST 是最大测试面）+ Integration 真机层。

## 设计决策

1. **base 伪方言+不注册 cute**（Registration.h）：cute 泄漏在解析期暴露而非静默错降——降级彻底性变成可测不变量。
2. **布局进类型**（CuteTypes.td:47）：静态布局编进类型使非法组合在类型检查期失败，动态槽 `?` 显式标注边界。
3. **三个 MlirOptMain 工具而非一个大 CLI**（base-opt.cpp:84 等）：单层隔离调试是 MLIR 编译器开发刚需。
4. **cutegen 错误走类型系统**（rec_var_algorithms.hpp）：代数库不抛异常，cg_error_t 作为变体元素传播。

## 新人提示

- 先读三个工具 main 头注释（各 84-88 行），再跑 `cute-opt … | base-opt -base-prepare` 管线。
- cute 类型文法看 CuteTypes.td:71-77 示例上手（`(1,(2,3))`/`(?,32)`/`?{i64}`）。
- 改 pass 先写 .mlir 测试：base/test 按 pass 分文件夹，新用例进对应子目录。
- cutegen 与 C++ CuTe（include/cute/）是两套布局代数：前者服务编译器 IR（dynamic_t），后者服务 kernel 内编译期计算，勿混。

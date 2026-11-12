# 04 · kernels 执行框架：Kernel 概念、KernelManager 与 GPU/CPU 双实现

## 角色定位

图谱 L04「kernels执行框架」（75 节点）是 DALI 的中立计算骨架：operator 层负责参数解析/设备路由/管线适配，kernels 层只认 TensorView+KernelContext，同一份 kernel 可以被算子、TF 插件、独立测试直接调用。kernel.h 是全库 import 第十名（76 处），是 CPU/GPU 双实现算子的统一框架。它的"接口"不是虚函数而是概念（concept）：kernel.h:47-60 注释写死契约——"A kernel must provide two non-overloaded functions: Run and Setup"，参数序固定为 Setup(KernelContext, [inputs], [arguments]) 与 Run(KernelContext, [outputs], [inputs], [arguments])。

## 内部结构

Kernel 概念用 kernel_traits.h 做编译期内省：`is_input/is_output` trait（kernel_traits.h:32-38/41-48）区分 InTensor/InList 与 TensorView/TensorListView 包装——底层同是 L02 的视图类型，角色由包装类决定；`filter+tuple_cat` 元函数（:67-92）从 `&Kernel::Run` 的函数签名里提取输入/输出/参数三元组，`kernel_run_inputs/outputs`（:108/:135）供 kernel::Setup/Run 伪方法（kernel.h:138-163）做 check_kernel 校验后 apply_all 转发。运行环境 `KernelContext`（context.h:199）= cpu+gpu 两个上下文+`Scratchpad *`（:201-209）；GPU 上下文内嵌 `cudaStream_t stream = AccessOrder::null_stream()`（context.h:37-38）。Scratchpad 基类提供 ToHost/ToPinned/ToManaged/ToContiguousHost/ToContiguousGPU 五族拷贝（context.h:150-192）与虚 Alloc（:197）；实现类 DynamicScratchpad（dynamic_scratchpad.h:133）按 AccessOrder 流序分配/释放，默认 64k 起步（:162-164），Alloc 内部用 TYPE_SWITCH 按 memory_kind 分派（:176-178）。其类前注释是全库最重要的一条警告：实例只能做局部变量，长期持有会造成"UNDETECTABLE functional MEMORY LEAK"（dynamic_scratchpad.h:123-127）——内存可达、sanitizer 无感，只有显存涨。产出契约 `KernelRequirements` 只有 output_shapes 一个成员（kernel_req.h:31-34）。实例管理 KernelManager：`AnyKernelInstance` 用 `unique_ptr<void, deleter>` 类型擦除存 kernel 实例（kernel_manager.h:32-36），取用时类型不符抛 logic_error（:40-45）；`instances` 是 SmallVector<AnyKernelInstance,1>（:206），CreateOrGet/Get/Setup/Run 按 instance_idx（通常对应管线节点）复用（kernel_manager.h:120/133/167/187）。公共设施 BlockSetup（block_setup.h:91）做图像块划分（ndim/channel_dim/tensor_ndim :93-95），其模板递归有"prevent infinite template expansion"守卫（:260）。

## 外部连接

上游全部来自 L02：TensorView/TensorShape/span/static_switch 是 kernel 签名的词汇表；DynamicScratchpad 的分配走 L03 的 mm 资源。下游每个 operator（L10-L13 算子族）都包一个或多个 kernel；executor 在每次迭代构造 DynamicScratchpad 塞进 KernelContext；join 家族给"双实现"提供了标准样本——tensor_join_cpu.h 与 tensor_join_gpu.h+impl.cu/.cuh 同构分设备（kernels/common/join/ 目录）。cast_gpu.cu、scatter_gather.cu 是被广泛复用的底层件。需要特别说明的是图谱质量：这层模板头是 tree-sitter 的重灾区——kernel_traits.h 的 is_input/is_output 实为 trait 结构体而非类节点（NOTES batch-59 甄别），static_switch.h 宏展开无法提取（batch-32），operators 侧的 arithmetic_meta.h 纯模板头零提取需人工补扫（batch-16），expression_impl_factory.h 全宏生成提取为空（batch-20）——本层图节点含大量人工补偿，读图时勿把节点稀疏当成代码稀疏。

## 数据流

一次 kernel 生命周期：operator 拿到输入 → `KernelManager::Setup(instance_idx, ctx, inputs...)` 调 kernel.Setup 只看 shape 推出 KernelRequirements（kernel.h:72 注释警告"看数据会严重拖慢 Setup"）→ 执行器按 output_shapes 分配输出 → `KernelManager::Run(instance_idx, ctx, out, in, args)` → kernel.Run 内按需向 scratchpad 要临时缓冲（ToContiguousGPU 走指定流）→ 迭代结束 DynamicScratchpad 析构按 AccessOrder 流序释放。

## 设计决策

1. 概念而非接口：kernel 无虚函数、无继承，契约靠注释+static_assert 表达；好处是 kernel 可内联进调用者、可在 .cuh 里做 __host__ __device__ 双端。
2. is_input/is_output 用包装类型定角色：同一 TensorView 包成 InTensorGPU/OutTensorGPU 后语义不同，签名即文档。
3. 类型擦除只发生在 KernelManager 一处：算子代码保持全模板，管理器侧付擦除成本。
4. scratchpad 流序释放（AccessOrder）而非立即释放：临时缓冲的 GPU 生命周期对齐消费流，避免同步等待。
5. 双实现采用"同构两套头"而非一套 if-branch：warp_cpu.h（225 行）与 warp_gpu.h+134 行 .cuh 各自独立；运行期枚举（如插值类型）经 VALUE_SWITCH 炸成模板参数——warp_cpu.h:84-87 把 interp 在 (DALI_INTERP_NN, DALI_INTERP_LINEAR) 内展开后调用 RunImpl<static_interp>（:94），核内零分支（NOTES batch-11）。
6. 64k 惰性起步+按 kind 懒分配：无请求的 memory kind 零开销（dynamic_scratchpad.h:159-164）。

## 新人提示

入门顺序：kernel.h:47-60 概念注释 → kernel_traits.h 的 trait → warp_cpu.h 225 行全读（最小的真实 kernel）→ 再看 warp_gpu.h 对照双实现差异。铁律一条：DynamicScratchpad 永远做局部变量（dynamic_scratchpad.h:123 的大写警告）。写新 kernel 先抄 dali/kernels/test/kernel_test_utils.h 的测试骨架；instance_idx 语义看 kernel_manager.h:156 注释（对应管线节点，跨迭代复用内核实例）。查"kernel 不被调用"先看 check_kernel 的 static_assert 是否被吞；查"显存缓涨"先查有没有人把 scratchpad 或其分配物存进了长命对象。图谱导航注意：纯模板头（kernel_traits.h、static_switch.h）在图里节点很少是工具盲区，不是"这里没代码"。

# 03 · kernel_ir 与 internal_nodes：算子词汇表与设备侧 IR

## 角色定位

这一篇覆盖 IR 主线的"下半场"：`csrc/ir/internal_nodes.h/.cpp` 是 Fusion IR 的算子词汇表——用户不该直接接触的底层 IR 全集；`csrc/kernel_ir.h/.cpp`（命名空间 kir，kernel_ir.h:29 开、:1861 合）则是 lowering 产物——设备侧节点的直接输入，codegen 一字一句翻译它们。两套节点共用第 01 篇的 Statement/Val/Expr 骨架：kernel.h:222 声明 class NVF_API Kernel final : public Fusion，Kernel 本身就是一个 Fusion 容器，lower 的本质是把 Fusion 里的算子表达式重写为 kir 里的控制流表达式。

## 内部结构

internal_nodes.h（2385 行）47 个顶层类，几乎全是 Expr 子类（图谱甄别：构成 IR 最大继承树）：标量层 UnaryOp（internal_nodes.h:465）/BinaryOp（internal_nodes.h:505）/TernaryOp（:548）、张量层 FullOp（:108）/BroadcastOp（:928）/SqueezeOp（:979）/ReductionOp（internal_nodes.h:1035）/GroupedReductionOp（:1100）/WelfordOp（internal_nodes.h:1282）/GroupedWelfordOp（:1394）/MmaOp（:1516）/ExpandOp（:1607）/RepeatOp（:1643）/ReshapeOp（:1707）/LoadStoreOp（:1741）、域变换 Split（internal_nodes.h:1796）/Merge（:1840）/Partition（:1873）/Combine（:1917）/Swizzle（:1952）/Swizzle1D（:2003）/Resize（internal_nodes.h:2036）、不规则算子 PadOp（:2157）/SliceOp（:2235）/CatOp（:2285）以及 grid 同步 WaitForPriorGridOp（:2362）；非 Expr 的例外有作用域容器 Scope（:40，kir 嵌套结构的物理载体）与 WelfordTriplet（:1162）。NamedScalar（:2083）是唯一 Val 子类。kir 侧 39 个类（kernel_ir.h:78-1828）分两支：Val 系 Predicate（kernel_ir.h:206）/TensorIndex（kernel_ir.h:306）；Expr 系从 ForLoop（kernel_ir.h:78）/Allocate（kernel_ir.h:422）/IfThenElse（kernel_ir.h:1178）到 Hopper/Blackwell 专用 MBarrierInit（:824）/MBarrierWaitParity（:983）/AsyncWait（:1074）/InitMagicZero（:1137）/EncodeTensorMapTiled（:1713）/AllocTMem（:619），grid 通信节点 GridReduction（kernel_ir.h:1224）直接 final 继承 Fusion IR 的 ReductionOp。对应实现：internal_nodes.cpp 3265 行 197 个函数（全仓最大 IR 文件），ReductionOp 构造@1672、WelfordOp::evaluate@2058、CatOp::evaluate@3181——197 个函数几乎全是构造器与重载 evaluate，是常量折叠的执行点；kernel_ir.cpp 2169 行承载 kir 全部 toString。

## 外部连接

internal_nodes 的消费者是 ops/arith.cpp（创建）与 composite 层；kir 的消费者是 GpuLower 的各 pass（device_lower/pass/，如 index.cpp 的 IndexLowering 78 个 handle）与 codegen.cpp。双向遍历有专用基座 kernel_ir_dispatch.h:39 IrVisitor（OptOutDispatch 系）/ :65 ConstIrVisitor（OptOutConstDispatch 系）/ :114 ExprMutator（支持结构化插入替换删除）——注意它们与 iter_visitor.h 的 Fusion 侧遍历器是平行世界。产物摘要汇入 kernel.h:35 KernelSummary（约 40 属性）与 :166 KernelPerformanceProfile。

## 数据流

lower 前：用户算子 → internal_nodes 的 Expr 进 Fusion；常量输入可走 evaluate 直接折叠。lower 中：lower2device.cpp 的 pass 链把 ReductionOp 包成 GridReduction（补工作缓冲与同步）、把逻辑域变成 ForLoop 嵌套 Scope、把访问地址物化为 TensorIndex。lower 后：Kernel 持有 kir 表达式树，codegen 按遍历序吐 CUDA C++。evaluate 的第二重载（base_nodes.h:564）让 CatOp 联合前置 PadOp 求值，属同一思想的跨文件应用。

## 设计决策

kir 不另起炉灶而是寄生在 Fusion 容器上（Kernel final : public Fusion），换来 cloner/dispatcher/printer 全套基础设施零成本复用——代价是 kir 节点必须防御性地区分自己处于哪种容器。GridReduction 直接继承 ReductionOp 而非重新组合，说明 kir 定位是"设备语义的超集装饰"而非平行 IR。MagicZero（InitMagicZero/UpdateMagicZero）这类细粒度节点入 IR 而非藏在 codegen 字符串里，保证 index 分析与谓词化简能看见它们。图谱勘误：kernel_ir.h 实际 39 类，图谱仅收 31，FenceAsyncProxy@731、MBarrierWait@960、InitMagicZero@1137 等八个类被 tree-sitter 漏掉，引用前先对源码。

## 新人提示

找算子先分四层：arith 层（用户 API）、internal（本篇）、composite（MatmulOp 等高层）、kir（设备侧）。读 lower 中间态 dump 用 NVFUSER_DUMP=lower_verbose 或 Kernel::print。改 kir 节点必看 kernel_ir_dispatch.h 的 mutator 契约（注释警告 TensorView 域变更不注册为 mutation）。Scope 是 std::list 而非 vector，插入迭代器稳定性是 pass 正确性的隐含前提。

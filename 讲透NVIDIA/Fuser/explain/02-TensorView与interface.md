# 02 · TensorView 与 interface：张量的用户面与域的内核

## 角色定位

如果说 base_nodes 是 IR 的骨，TensorView 就是 IR 的脸。`csrc/ir/interface_nodes.h`（1018 行）中 class NVF_API TensorView : public Val@380 占了 380-970 近 600 行，是用户施加调度的 API 面；它操纵的 IterDomain（internal_base_nodes.h:92）、RaggedIterDomain（internal_base_nodes.h:445）、TensorDomain（internal_base_nodes.h:535）全住在 `csrc/ir/internal_base_nodes.h`（896 行）的 internal 一侧。interface/internal 的分野即访问边界：用户只碰视图不碰域。头注释（interface_nodes.h:353-357）说得直白：TensorView 可视为物理内存，但维度随 split/merge/computeAt 改写，变换历史被保留、用于生成引用物理内存的代码。

## 内部结构

TensorView 持 domain_（interface_nodes.h:910）指向 TensorDomain。TensorDomain 用四段域刻画张量生命周期：root（广播/规约标注后的原始域）、logical（view/reshape 后的用户视角）、allocation（内存分配序）、loop（调度后的循环序）——构造器重载链从单参 logical 到全参含 alternate_loop_domain（internal_base_nodes.h:539-586），nDims（internal_base_nodes.h:595）按 loop_domain_ 计数，root 为空时 root() 回退 logical（internal_base_nodes.h:676）是历史兼容路径。IterDomain 是"一切调度的原子单位"：构造带 start/extent/expanded_extent/stop_offset/parallel_type/iter_type/is_rfactor_domain/is_padded_dimension/padded_to_size 九类信息（internal_base_nodes.h:96-107），域级原语 static merge（internal_base_nodes.h:137）与 split（internal_base_nodes.h:145）；IterDomainBuilder（internal_base_nodes.h:40）统一组装。RaggedIterDomain 挂 TensorView\* extents 描述参差张量。TensorView 的调度 API 全部返回自身引用支持链式：split（interface_nodes.h:596，头注释 :589-594 给了 inner_split 双向例子）、merge（interface_nodes.h:615）、reorder（interface_nodes.h:635）；computeAt 三件套 inlineAt（interface_nodes.h:775）/computeWith（interface_nodes.h:793）/resolveComputeWith（interface_nodes.h:800）；rFactor（interface_nodes.h:682，注释警告不返回 this）；硬件接口 circularBuffer（interface_nodes.h:729）、applyMmaSwizzle（interface_nodes.h:748）、swizzleTMABox（interface_nodes.h:756）。构造走 TensorViewBuilder（interface_nodes.h:971，strideOrder@991）。实现镜像在 tensor_view.cpp:473/518/779/1376。

## 外部连接

上游：ops/arith.cpp 算子函数接受并返回 TensorView，Python pybind 一比一暴露。域侧：Split/Merge/Swizzle/Resize 本身是 Expr 子类（internal_nodes.h:1796/:1840/:1952/:2036）——"调度即 IR"，TensorView::split 创建的是以 IterDomain 为输入输出的 Split 表达式，因此能被 cloner、iter_visitor、transform_replay 统一处理。下游：调度器经 AbstractTensor 在域上符号推演，IdModel 把全部 IterDomain 收进等价类图，MaxPosCalculator（interface_nodes.h:66 前向声明）算 computeAt 上限，Pipelined/WarpSpecialized（interface_nodes.h:208 起）挂流水线意图。

## 数据流

一次 tv->split(0,4) 的旅程：interface_nodes.h:596 入口 → tensor_view.cpp:518 实现 → IterDomain::split（internal_base_nodes.h:145）生成 outer/inner 新 ID（底层由 IrBuilder 创建 Split Expr 登记）→ 新 loop 域装回 TensorDomain → 返回 this 继续链式。getComputeAtPosition（interface_nodes.h:550）读的正是 loop 域上记录的内联位置；:803 判 computeWith 位与 computeAt 位大小、:822 取 max，说明 computeWith 是 computeAt 的泛化，且必须先 resolveComputeWith 传入拓扑排序后的表达式表才能安全使用。

## 设计决策

TensorView 继承 Val 而非 Expr：张量是值、可作算子输入输出，调度决策下沉到域层以 Split/Merge 表达式进 IR——视图方法只是域变换的语法糖，调度历史因此天然可克隆可重放。四段域模型把用户语义（root/logical）与机器现实（allocation/loop）显式分离，是 nvFuser 与 TVM 系调度器的最大结构差异。is_rfactor_domain 双标记让 rFactor 后的中间域可追溯。本文件类全部 NVF_API 前缀，tree-sitter 提取失灵，图谱中 TensorView [380,970]、IterDomain [92,444] 行区间系人工核实。

## 新人提示

改布局前先问动的是哪段域：reorder 影响 loop、view/reshape 造成 logical 与 root 差异、allocation 由调度器定。debug 用 tv->toString() 加各段域 dump。读 split 语义先看 interface_nodes.h:589-594 两例。RaggedIterDomain 的 extents 是 TensorView 不是标量列表。computeWith 不 resolve 就用是断言级错误。行号以本图谱区间为准。

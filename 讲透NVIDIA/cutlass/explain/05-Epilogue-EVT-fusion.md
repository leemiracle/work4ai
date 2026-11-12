# 05 · Epilogue 体系与 EVT 融合树

## 角色定位

Epilogue 层（图谱 L07 域 133 节点）管"MMA 之后的全部算术"：类型转换、activation、bias、残差、D 侧归约。CUTLASS 3.x 的答案是 EVT（Epilogue Visitor Tree）——融合公式写成类型级表达式树，每节点一个 visitor，编译期装配零抽象开销。2.x 扁平 functor（`epilogue/thread/linear_combination*.h`）与 3.x 树体系并存。

## 内部结构

树骨架在 `include/cutlass/epilogue/fusion/sm90_visitor_tma_warpspecialized.hpp:711`：`struct Sm90TreeVisitor : Sm90VisitorImpl<ChildOps..., NodeOp>`；基类族 `Sm90VisitorImplBase` 按 0-4 个算子递归特化（`sm90_visitor_tma_warpspecialized.hpp:483/893/969/1063/1176`）；DAG 场景有 `:771` `Sm90SplitTreeVisitor` 与 `:819` `Sm90TopologicalVisitor`。求值核心是 `ConsumerStoreCallbacks::visit`：先访问前 R-1 个子节点收集 `frg_inputs`，再传给 node op——**孩子先算、父节点后算**的纯函数式折叠。节点动物园按三色分文件：compute 色 `include/cutlass/epilogue/fusion/sm90_visitor_compute_tma_warpspecialized.hpp:91` `Sm90Compute`；load 色 `include/cutlass/epilogue/fusion/sm90_visitor_load_tma_warpspecialized.hpp`——`:62` `Sm90AccFetch`（最内叶子）、`:91` `Sm90SrcFetch`、`:213` `Sm90AuxLoad`（TMA 旁路张量）、`:1010` `Sm90ScalarBroadcast`、`:1363/:1627` Row/ColBroadcast；store 色 `include/cutlass/epilogue/fusion/sm90_visitor_store_tma_warpspecialized.hpp`——`:70` `Sm90AuxStore`、`:893` `Sm90ScalarReduction`、`:1078/:1666` Row/ColReduction，外加 `sm90_visitor_topk_softmax.hpp:335`。公式注册表在 `include/cutlass/epilogue/fusion/sm90_callbacks_tma_warpspecialized.hpp`（2886 行）：`:58` `using Sm90EVT = Sm90TreeVisitor<NodeOp, ChildOps...>`（**别名而非独立结构**），其后 **24 个 FusionCallbacks 特化**把 D=acc、D=alpha*acc+beta*C 等公式预装成树（`:221` 注释 `beta * C + (alpha * acc)`）。capability 契约在 `include/cutlass/epilogue/fusion/operations.hpp`：`FusionOperation` 基类暴露 IsSourceSupported/IsAuxOutSupported 等静态字段——builder 从字段一次性推断 smem/alignment 需求。SM100/SM120 各有一套同名 visitor/callbacks 变体（`sm100_callbacks_tma_warpspecialized.hpp` 与 `sm120_callbacks_tma_warpspecialized.hpp` 各 14 个特化）。

## 外部连接

Collective 侧 `include/cutlass/epilogue/collective/sm90_epilogue_tma_warpspecialized.hpp:83` 的 `CollectiveEpilogue`（963 行）消费 EVT：`:294` `make_tma_copy_C_sm90` 构造 C 的 TMA、`:714` `issue_tma_store`（单 warp 发射）——visitor 树挂在 store 循环的 R2S callbacks 链上逐 fragment 调用。装配桥梁是 CallbacksBuilder：`include/cutlass/epilogue/collective/collective_builder.hpp:88` 主模板 + `builders/sm90_builder.inl:184/224/262` 特化链，把 FusionOperation 映射成 FusionCallbacks；StagesC/StagesD 在 epilogue 侧 dispatch_policy。Python 侧**双侧镜像**：`python/cutlass_cppgen/epilogue/epilogue.py` 是 176 行薄注册表（8 个激活别名+工厂函数），真身在 `python/cutlass_cppgen/backend/epilogue.py`（541 行）：`:94` `EpilogueFunctorBase`、`:117` `LinearCombination`、`:204/:253` Clamp 家族、`:305` `LinearCombinationGeneric`；关键在 `:160` `_EpilogueOutputOpParamsEVT(ctypes.Structure)` 用 ctypes 复刻 C++ Params 布局并提供 `to_evt_params`——Python 侧 alpha/beta 无序列化层直接进 C++。

## 数据流

设备端一个 store fragment 的生命周期：acc 从 MMA 出来 → `get_consumer_store_callbacks` 沿树给每节点发 callbacks → epilogue 主循环按 (epi_v,epi_m,epi_n) 调 `visit(frg_acc,...)` → 叶子产出 → 上行到 Sm90Compute 做算术 → 根结果经 R2S 拷贝进 smem → 单 warp TMA store 到 gmem。AuxLoad/AuxStore 共享 C/D smem 流水。宿主侧：构造 EVT 树 → `to_underlying_arguments` 逐节点展开（AuxLoad 在此构造 TMA descriptor）。

## 设计决策

① 树而非扁平 functor：融合公式可组合，新 activation 只需一个 Sm90Compute 特化+一条 callbacks；代价是深树编译慢。② 24 个预装公式：高频组合开箱即用，冷门组合手写 Sm90EVT。③ SplitTree/Topological 变体兜 DAG：多输出共享输入不需要通用 DAG 引擎。④ capability 字段前置 operations.hpp：选型期即读 IsAuxOutSupported。⑤ cppgen 用 ctypes.Structure 镜像 Params：两侧 ABI 直接对齐。

## 新人提示

① `Sm90EVT` 是 `sm90_callbacks_tma_warpspecialized.hpp:58` 的别名，真身 Sm90TreeVisitor 在 visitor 文件——追定义别在 callbacks 文件打转。② visitor 三件套按数据角色命名：`*_visitor_load_*`（产数据叶子）、`*_visitor_compute_*`（纯算术）、`*_visitor_store_*`（副作用根）。③ 找融合公式先看 callbacks 特化顶部的 `// D = ...` 注释，24 选 1 通常已覆盖。④ 新增 activation 最短路径：`epilogue/thread/activation.h` 加 functor → cppgen 注册 → C++ 用 LinearCombinationGeneric 包。⑤ StagesC/StagesD/ReuseSmemC 都在 epilogue 侧 dispatch_policy。⑥ Python 镜像有两层：`epilogue/epilogue.py` 只是门面，改行为去 `backend/epilogue.py`；旧 `python/docs/_modules/cutlass/*` 是 v3.x Sphinx 快照，别照抄。

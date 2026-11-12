# 01 · CuTe 核心代数：layout / swizzle / algorithm 三件套与基础数值层

## 角色定位

CuTe（include/cute/）是 CUTLASS 3.x 之后的代数地基（图谱 L01 层 52 节点，仓版本 4.8.0，`include/cutlass/version.h:41-43`）：把"坐标→地址"映射抽象成编译期可运算的类型代数，让 GEMM 分块、bank-conflict 消除、TMA 描述符构造全部变成类型计算。三件套分工：`layout.hpp` 的 Layout（形状×步长）、`swizzle.hpp` 的 Swizzle（位级坐标扰动）、`algorithm/`（在此代数上运转的 gemm/copy 算法），底层由 `numeric/integral_constant.hpp` 与 `container/tuple.hpp` 提供"零大小静态值"地基。

## 内部结构

`include/cute/layout.hpp:98-100`——`struct Layout : private cute::tuple<Shape, Stride>`，私有继承+注释点明 EBO（静态布局零大小）；默认 stride 是 `LayoutLeft::Apply<Shape>`。坐标求值入口 `:167-171` 的 `operator()`：含 `_` 占位符走 `slice`，否则 `crd2idx(coord, shape(), stride())`——而 `crd2idx` 实现在 `include/cute/stride.hpp:102`（基例 `:119` `coord * stride`），不在直觉以为的 int_tuple.hpp。`LayoutLeft/LayoutRight`（`stride.hpp:277-281`）是空 tag，紧凑步长计算在 `:348` 的 `compact_major`。Swizzle 是第二种坐标原语：`include/cute/swizzle.hpp:54-55` 的 `template <int BBits, int MBase, int SShift>`，核心变换一行在 `:78`：`offset ^ shiftr(offset & yyy_msk{}, msk_sft{})`（ZZZ 异或 YYY 位段），与 layout 组合成 `ComposedLayout`（`include/cute/layout_composed.hpp:54`，`:102` 直接 `stride() const = delete`），swizzle 版本切片时会尝试衰减回普通 Layout（`include/cute/swizzle_layout.hpp:38-47` 注释明言）。数值层：`include/cute/numeric/integral_constant.hpp:42-44` 的 `C<v>`，`:92` 的 `is_static` 判据是 `is_empty`——类型即值、零存储。容器层：`include/cute/container/tuple.hpp:199` 的 `tuple : eso::ESO_t<T...>`，`:54-55` 注释自曝"放弃 standard-layout 换 3 倍编译加速"。最上层 `include/cute/tensor_impl.hpp:136` 的 `struct Tensor`（`:71` ArrayEngine 自持数组/`:107` ViewEngine 持迭代器）。指针层 `include/cute/pointer.hpp` 用四个空间标签 `gmem_ptr:87 / smem_ptr:150 / rmem_ptr:222 / tmem_ptr:273` 分派寻址。

## 外部连接

向上，`include/cute/algorithm/`（14 文件）消费这套代数：`gemm.hpp:160-175` 的朴素 `gemm(D,A,B,C)` 用 `MMA_Atom<UniversalFMA<...>>` 起步，按 rmem/smem/gmem 与布局秩五级静态分派；`copy.hpp:242-256` 的向量化 copy 用 `max_common_vector` 求公共向量。向硬件层，`include/cute/atom/mma_atom.hpp:531` 的 `make_tiled_mma` 把 L02 的 MMA 原子铺成 tile 级对象（`:548` 重载自动包 Atom）。向 TMA，`include/cute/atom/copy_traits_sm90_tma_swizzle.hpp:47-55` 把 Swizzle 的 B 位宽映射硬件 swizzle 模式：B==3→B128、B==2→B64、B==1→B32——**(B,M,S) 与 TMA descriptor swizzle 枚举一一对应**。向 CUTLASS 层，`include/cutlass/detail/layout.hpp` 的 TagToStrideA/B/C 把 2.x 布局 tag 翻译成 CuTe stride。

## 数据流

静态折叠链：`C<v>` 的运算符由 `integral_constant.hpp:207-219` 的宏生成（`C<(t OP u)>`），静态×静态折叠为新静态类型；静态×动态只在特例（0 乘、±1 取模等 `:262-310`）保持静态。布局化简：`coalesce`（`layout.hpp:861-867`）从最后一阶向前合并同模式，`:815-818` 注释承诺域内函数值不变；`complement`（`:1223`，`:1186` 断言 rank>1 必须静态 stride）求补布局，是 smem 分配底座；`logical_divide`（`:1599-1611`）= composition(tiler 补布局)，`zipped_divide`（`:1650`）在其上 zip 整形。GEMM 两大动作：`tensor_impl.hpp:1037` 的 `local_tile`（inner）与 `:1079` 的 `local_partition`（outer：按线程/CTA 索引取外层划分）。线程-值划分核心一行在 `include/cute/atom/partitioner.hpp:74`。

## 设计决策

① 全静态优先：`is_static = is_empty`（integral_constant.hpp:92）贯穿 Layout/Stride/Tensor——纯静态布局 sizeof 为 0。② 代数用命名函数不用运算符：4.8 的 Layout 没有 `operator* / / %`，组合一律 `composition / logical_divide / zipped_divide / tiled_divide`。③ tuple 故意非 standard-layout：ESO 替代递归 EBO，空类型不构造、get 时按需构造（tuple.hpp:90-95），编译提速 3 倍。④ Swizzle 独立于 layout：不可线性化的对合变换（swizzle_layout.hpp:376/384 两个 inverse 同构），与 TMA 硬件模式对齐时才进 ComposedLayout。⑤ ComposedLayout 删除 stride()：强制"无 stride 也可用"，逼调用方走 composition 语义。

## 新人提示

① 职能拆分勘误：`crd2idx/idx2crd` 在 stride.hpp，tuple 算法在 `algorithm/tuple_algorithms.hpp`，`tensor.hpp` 是 64 行纯伞形头；不存在 tiled_mma.hpp/tiled_copy.hpp——对应 `atom/mma_atom.hpp`（TiledMMA `:211`）与 `atom/copy_atom.hpp`（TiledCopy `:188`）。② NVRTC 门控：所有 `operator<<`（layout.hpp:1963、pointer.hpp:391 等）包在 `#if !defined(__CUDACC_RTC__)` 里，device 侧调试用 printf 版 `print()`。③ `partition_fragment_A/B` 依赖运行时 thread_idx，`mma_atom.hpp:582-584` 明言静态上下文只能用 `partition_shape_A/B/C`。④ complement 报 "Dynamic-stride complement only for rank-1"（layout.hpp:1186）时先 filter 静态化。⑤ tmem_ptr（pointer.hpp:273-301）不可解引用、字寻址，用 raw_pointer_cast。

# 04 · SM90 atom 动物园：Op→Traits→Atom 三层装配与 wgmma/tcgen05 体系

## 角色定位

图谱 L02 域 2201 节点（arch 层 + atom/traits 层）是全仓"家族化解码"最密集的层：同名模板的成百上千个特化合并为单节点（如 mma_traits_sm90_gmma_ext 的 736 个特化）。体系分三层：`include/cute/arch/` 的 Op（struct + static 方法内联 PTX asm）、`include/cute/atom/` 的 Traits（给 Op 配线程/值布局）、`atom/mma_atom.hpp` 的 Atom 装配（继承 Traits 再加易用接口）。体量可怖：`arch/mma_sm90_gmma_ext.hpp` 56,445 行（最大单体）、`arch/mma_sm90_gmma_sparse.hpp` 22,745 行。

## 内部结构

装配链：`include/cute/atom/mma_atom.hpp:45` 主模板把任何 Op 转发到 Traits，`:49` 真身 `struct MMA_Atom<MMA_Traits<...>> : MMA_Traits<...>`——**Atom 直接继承 Traits**。`make_tiled_mma:531`（`:548` 自动包 Atom）。Copy 侧同构：`copy_atom.hpp:48/:52`、`ThrCopy:358`、`make_tiled_copy:495`。通用骨架勘误：**atom/ 下没有 atom.hpp**——`mma_traits.hpp:64/:66` 哨兵 + `:70` 唯一通用特化 UniversalFMA；copy 侧 `copy_traits.hpp:60/:66/:81`。wgmma 封装：`include/cute/arch/mma_sm90_gmma.hpp:105` 整文件一个 `namespace SM90::GMMA`；fence 三件套 `:49/:62/:76`（fence/wait_group/commit_batch）；SS 变体 `:147` `fma(uint64_t desc_a, uint64_t desc_b, ...)`——A/B 都是 64-bit smem descriptor，`:158` asm `wgmma.mma_async.sync.aligned.m64n8k16.f16.f16.f16`；RS 变体 `:194` A 从寄存器来，SS/RS 相邻成对定义（`:2247/:2291`）；全文件 320 条 wgmma asm。Traits 侧 `include/cute/atom/mma_traits_sm90_gmma.hpp:477`——**公开名 `SM90_64x8x16_F16F16F16_SS` 在这里诞生**（arch 层叫 `MMA_64x*`），`:480` 第一个特化，`:487` `FrgTypeA = GMMA::smem_desc`（fragment 不是寄存器而是 smem descriptor——GMMA 与 warp 级的本质区别），`:490-494` ThrID=`Layout<_128>`（128 线程=一个 warpgroup），`:464` ABLayout 的 `Stride<_0,...>` 表示 128 线程共享同一 descriptor。ext 家族（N 非 8 倍数）736 个特化全部显式 checked-in（非宏生成）。TMA copy traits：`include/cute/atom/copy_traits_sm90_tma.hpp:103` `Copy_Traits<SM90_TMA_LOAD, NumBitsPerTMA>`——**不按 2D/3D/4D 分档**，维度全在 `:118` 的 opaque TmaDescriptor，`:104` `ThrID=Layout<_1>`（单线程 elect_one）；变体 `:261` MULTICAST/`:363` STORE/`:474` REDUCE_ADD；arch 侧 `arch/copy_sm90_tma.hpp:103/:159/:215/:327` 才分维，`:116` asm `cp.async.bulk.tensor.2d...`。tcgen05（SM100）：`include/cute/arch/mma_sm100_umma.hpp:46` `SM100_MMA_TF32_SS` 直接带公开名（不再两段式），`:71` asm `tcgen05.mma...[%0], %1, %2`——`[%0]` 是 **TMEM 累加器地址**；TS 变体 `:127`（A 来自 tensor memory），`:142` `fma(uint32_t tmem_a, uint64_t desc_b, ...)`；TMEM 分配在 `arch/tmem_allocator_sm100.hpp:82`。selector 巨链：`include/cute/arch/mma_sm90.hpp:366` `ss_op_selector` 约 2240 行纯 `if constexpr` 树（`:2609/:4852/:7096` 三兄弟，全文件 1900 个 `if constexpr`）。

## 外部连接

向上供 collective/builder 消费：builder 内 `make_tiled_mma(SM90_64x..._SS{})` 的原子即出自 `mma_traits_sm90_gmma.hpp:477` 别名；Copy 与 MMA 在 layout 层耦合——`copy_atom.hpp:424/:433/:442` 的 `make_tiled_copy_A/B/C` 直接从 TiledMMA 的 `get_layoutA_TV()` 派生 TiledCopy。TiledMMA 本体 `mma_atom.hpp:211`。向下是 PTX：wgmma 受 `CUTE_ARCH_MMA_SM90A_ENABLED` 门控（sm90a 条件指令）。

## 数据流

编译期：Op（asm struct）→ `MMA_Traits<Op>` 特化提供 Shape/ThrID/ALayout/BLayout/CLayout/FrgType → `MMA_Atom` 继承装配 → `make_tiled_mma` 铺成 tile 级 → ThrMMA partition 出 per-thread fragment。运行期（SS）：smem 摆好 A/B → 构造 64-bit descriptor → `warpgroup_arrive` → 循环 `fma`+commit_batch → `warpgroup_wait<N>` 收割寄存器累加器。tcgen05 不同：累加器在 TMEM（256KB tensor memory），主循环后还要 TMEM→寄存器搬运。

## 设计决策

① Op/Traits/Atom 三层分离：PTX 封装零依赖，布局知识后置到 traits。② 命名两段式（SM90）：arch 层 `MMA_64x*`，公开名 `SM90_*` 在 traits 层别名——sparse 系连别名都没有（直接 `GMMA_64x8x32_*`）。③ SS/RS（wgmma：A 来源 smem/寄存器，累加器恒寄存器）vs SS/TS（tcgen05：A 来源 smem/TMEM，累加器恒 TMEM）——**累加器所在存储体是两代硬件的分野**。④ ext 家族 checked-in 显式特化而非宏生成。⑤ TMA traits 按 NumBitsPerTMA 参数化而非维度分档。⑥ selector 用 if-constexpr 巨链：全编译期，代价是不可读。

## 新人提示

① 找 atom 先分清层：`SM90_*` 公开名在 traits 文件，asm 在 arch 文件；`SM90_64x64x16_F32BF16` 这类名字不存在——真名形如 `MMA_64x8x16_F32BF16BF16_SS`（`:2247`）。② traits 特化数实测：gmma 320/ext 736/sparse 320/sparse_ext 736/sm80 65/sm100 48，`grep -c "^struct MMA_Traits"` 可验证。③ 无 `TmaDotSized` 符号；SM100 的 TMA 在 `copy_sm100_tma.hpp`（含 2SM_LOAD 双 SM 系列），**`copy_sm100_desc.hpp` 不存在**；tcgen05.commit 在 `cutlass/arch/barrier.h:860` 不在 cute/arch。④ 图谱 2201 节点是同名家族合并后的家族数，真实特化量以 grep 计。⑤ `mma_sm90.hpp` selector 区段是查表不是叙事代码，读签名处分派层级即可。⑥ wgmma wait N∈[0,7]（`:63`），批深度=在飞 mma 组数。

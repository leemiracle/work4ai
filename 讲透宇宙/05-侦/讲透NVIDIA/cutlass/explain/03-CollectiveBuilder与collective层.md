# 03 · CollectiveBuilder 与 GEMM collective 主循环层

## 角色定位

collective 层是 CUTLASS 3.x 的"引擎舱"（图谱 L06 域 173 节点）：mainloop 实现 load/mma 两大设备端循环，`CollectiveBuilder` 是宿主入口的编译期装配器——用户给 13 个模板参数，builder 查表产出正确特化的 `CollectiveMma`。`include/cutlass/gemm/collective/` 有 55 个主循环 .hpp + `builders/` 35 个 .inl 共约 6.1 万行。

## 内部结构

入口契约在 `include/cutlass/gemm/collective/collective_builder_decl.hpp:77-92`（13 参主模板），`:93` 主模板体只有失败哨兵 `:94` `static_assert(sizeof(ElementA) == 0, "Could not build a collective...")`——查表失败的统一报错面。`collective_builder.hpp:39-65` 是纯聚合器，SM100+ 的 builder 全包在 `:42` `#if !defined(__CUDACC_RTC__)` 内。Stage 编排：`collective_builder_decl.hpp:41/:49/:66` 的 StageCount 三兄弟，公式在 `builders/sm90_gmma_builder.inl:84`：`(capacity_bytes - carveout_bytes) / stage_bytes`（容量常量 `builders/sm90_common.inl:57` 的 232448）。SM90 builder 特化族：`builders/sm90_gmma_builder.inl` 内 `struct CollectiveBuilder<` 共 **8 处**（209/327/524/633/772/875/984/1064），按 KernelScheduleType 的 enable_if 分族；最精妙是 `:984` 的 `KernelScheduleAuto`：`:1021-1023` 按 TileM 是否 64 选 Pingpong/Cooperative，`:1031` **递归回填 schedule 再查一次 builder 表**。blockscaled 动物园在 `builders/sm1xx_common.inl`：`:431` `enum class BlockScaledInstr{MXF4_NVF4, MXF4F6F8}`，`:436-437` 主模板 `blockscaled_type<BuilderScheduleTag, T>`，偏特化 **6 个**（勘误：常见说法 8 个）——`:440` 泛型 tuple<T,SF>、`:447` 显式钉 SF 向量宽、`:454/:463/:480` mx_float6/4/8（ue8m0 scale）、`:472` nv_float4（ue4m3）；指令映射在 `builders/sm100_common.inl:852` `SM100_MMA_MXF8F6F4_SS`（= tcgen05.mma.kind::mxf8f6f4）与 `:864/:918` mxf4nvf4（含 2x1SM 双 SM 对）。SM103 特有 `builders/sm103_blockscaled_umma_builder.inl:210` 空体主模板 `Sm103TrivialBlockscaledMma` + `:224/:251` 两个偏特化。mainloop 本体 `include/cutlass/gemm/collective/sm90_mma_tma_gmma_ss_warpspecialized.hpp:72-73`：`CollectiveMma` 按 DispatchPolicy 偏特化，`:178` `make_tma_copy_A_sm90` 以 nullptr 张量推 TMA 描述符类型，设备侧三段 `:310 load` / `:417 mma` / `:563 mma_tail`。

## 外部连接

向上被 kernel 层消费（load/mma 接口）；向下依赖 CuTe atom（`sm90_mma_tma_gmma_ss_warpspecialized.hpp:178` 的 make_tma_copy 系）与 `include/cutlass/gemm/dispatch_policy.hpp:266` 的 `MainloopSm90TmaGmmaWarpSpecialized`（Stages/ClusterShape/ArchTag/Schedule 四元组；SM100 侧 `:1155` 把 pipeline 拆 scheduler/accumulator 两级）。侧向 trait：`include/cutlass/detail/mma.hpp:47` `IsSparseTensorOp`（探测 `ValTypeE`）、`:56` `IsBlockScaledTensorOp`（探测 `FrgTypeSFA`）。兼容层：`include/cutlass/detail/layout.hpp:53/:72/:126` 的 `TagToStrideA/B/C` 把 2.x 布局 tag 翻成 CuTe stride。传统三级对照：`gemm/threadblock/mma_pipelined.h:92` `MmaPipelined : MmaBase<...,2>`、`mma_singlestage.h:82` 单缓冲版（勘误：无 mma_singlethread.h）、`threadblock/default_mma_core.h:110` `DefaultMmaCore` 中枢、`gemm/warp/mma_simt.h:84` `MmaSimt`、`warp/mma_tensor_op.h:167` `MmaTensorOp`、`gemm/thread/mma.h:72`——threadblock/warp/thread 三级是 2.x 分层，3.x collective 压缩进一个类。

## 数据流

宿主：`CollectiveBuilder<..., StageCountAuto>` 实例化 → 匹配 enable_if 特化 → 算 stages → 产出 `CollectiveOp = CollectiveMma<DispatchPolicy,...>` → kernel 层组装。设备端（producer）：`load` 循环逐 K-tile 投递 TMA 并 `producer_acquire`；（consumer）：`mma` 循环 `consumer_acquire` → 从 smem descriptor 发 GMMA → `warpgroup_commit_batch` → `warpgroup_wait` 留一级在飞。blockscaled 路径多一路 SFA/SFB 因子张量。

## 设计决策

① 查表式 builder：主模板哨兵 + enable_if 特化族，参数组合无解时编译期即死，无运行时降级。② KernelScheduleAuto 递归回填：先决策 schedule 再重入 CollectiveBuilder，自动与手写策略共享同一张表。③ IsSparse/IsBlockScaled 用成员类型探测（void_t 惯用法）而非枚举轴。④ 三级层保留完整：2.x kernel 与 SIMT 路径仍依赖，3.x 不迁移只并存。⑤ Hopper smem 容量 232448 写死在 `sm90_common.inl:57`，StageCountAuto 的除法出自它。

## 新人提示

① 主模板不在 collective_builder.hpp 而在 collective_builder_decl.hpp:93——从哨兵报错回溯别走错文件。② builder 特化总数勘误：SM90 dense 8 个（sparse 另 4 个），全仓 builders/*.inl 合计 36 处 `struct CollectiveBuilder<`；不存在"CA/SA/CG/SG"缩写令牌。③ blockscaled_type 偏特化 6+1 个不是 8。④ 源码笔误钉版：`builders/sm107_common.inl:47` 模板参数名 `ElementAMmaccumulator`（应为 ElementAAccumulator，同文件 5 处），`sm100_common.inl:297` 同款——照抄参数名会编译失败。⑤ mainloop 无 `mma_loop` 成员，循环体在 `mma()` 内部。⑥ `sm90_common.inl` 全文件 0 个聚合类型，工具提取"零符号"是正常现象不是解析失败。

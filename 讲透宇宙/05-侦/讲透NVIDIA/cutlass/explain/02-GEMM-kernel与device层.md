# 02 · GEMM kernel 调度层与 device API

## 角色定位

这一层是 CUTLASS 的指挥塔（图谱 L05 域 150 节点）：kernel 层编排 producer/consumer warp 的三大循环与 tile 调度，device 层把 kernel 包成宿主 `Gemm` 类。`include/cutlass/gemm/kernel/` 目录 116 个文件中 80 个 `.h`（2.x）与 36 个 `.hpp`（3.x+）**两代 API 物理共存**——`gemm_universal.h`（2.x）与 `sm90_gemm_tma_warpspecialized*.hpp`（3.x）同目录并行，是理解本层的钥匙。

## 内部结构

SM90 主力 `include/cutlass/gemm/kernel/sm90_gemm_tma_warpspecialized.hpp`（523 行）：`:65` `class GemmUniversal<...>` 是主模板特化，`:70` SFINAE `is_base_of_v<KernelTmaWarpSpecialized, ...DispatchPolicy::Schedule>`——**分派机制 = Schedule 标记继承哪个 tag 就落哪个 kernel 文件**。护栏：`:82` 形状秩断言、`:100` SM90 能力断言、`:111` 锁死 scheduler。角色分派是 kernel 内局部枚举：`sm90_gemm_tma_warpspecialized.hpp:284` `WarpGroupRole{Producer,Consumer}` 与 `:288` `ProducerWarpRole`。三大循环：`collective_mainloop.load`（`:436`，producer 单 warp 发 TMA）、`mma`（`:472`）、`collective_epilogue.store`（`:496`），收尾 `:450/:483/:510`。PDL 接缝：`:435` wait_on_dependent_grids 与 `:492` launch_dependent_grids 成对。`:276` `#define ENABLE_SM90_KERNEL_LEVEL 1`——arch guard 一半是宏+运行期致命路径（`:281`），wgmma 是 sm90a 条件指令。persistent 版 `sm90_gemm_tma_warpspecialized_cooperative.hpp`（893 行）加码：`:373` 硬性 256 线程、`:374-375` TileM≥128 是 Cooperative/Pingpong 分界；`:436` 揭示 **tile scheduler 本身是一条 SM90 pipeline**（载荷 CLCResponse），`:438-441` throttle pipeline 反压查询频率，`:791/:803` 两 consumer warpgroup 协作同一 tile。2.x 对照 `gemm/kernel/gemm_universal.h:65`：`:98` kStages 来自 Mma 而非 policy，`:352` `union SharedStorage` 时间复用 smem（SM90 是并列 struct），`:468` 的"调度器"只是 ThreadblockSwizzle。

## 外部连接

kernel 对 collective 的全部调用面 = `load/load_tail/mma/mma_tail` + epilogue `store/store_tail`，kernel 不直接碰数据。scheduler 家族：`gemm/kernel/tile_scheduler.hpp:49-57` 五个空 tag，`:86` TileSchedulerSelector 按 ArchTag+TileShape+ClusterShape 选型；`sm90_tile_scheduler.hpp:40` CRTP 继承跨代基类 `StaticPersistentTileScheduler`（`static_tile_scheduler.hpp:48`，`:163/:192` persistent 循环核心）；`sm100_tile_scheduler.hpp:63` `UnderlyingTileScheduler = PersistentTileSchedulerSm90`——**SM100 复用 SM90 实现**。RasterOrder 真身在 `tile_scheduler_detail.hpp:38/:43`（勘误：不在 gemm_enumerated_types.h），heuristic 按网格纵横比选向（`tile_scheduler_params.h:333-340`）。device 层 `include/cutlass/gemm/device/gemm_universal_adapter.h:123` 特化接 3.x kernel、`:655` 特化接 2.x——**一个 adapter 两个世界**；`:195` kStages SFINAE 探测；`:231` can_implement 委托 kernel；`:395-399` 静态 run 带 `launch_with_pdl`；`:427-438` **动态 cluster fallback 仅 Blackwell 有**；`kernel_launch.h:91` 最终 `device_kernel<<<>>>`。`include/cutlass/kernel_hardware_info.h:43` KernelHardwareInfo（`:100` 查 max_active_clusters）供 persistent grid 计算，`.hpp` 版是垫片（`:33`）。

## 数据流

宿主：`Gemm::run(Arguments)` → adapter `initialize`（`gemm_universal_adapter.h:313`）打包 Params → can_implement → get_grid_shape（persistent 时 grid=可驻留 CTA 数）→ `kernel_launch` 发射。设备侧（cooperative）：producer warpgroup 的单 warp 发 TMA load，同时在 `sm90_gemm_tma_warpspecialized_cooperative.hpp:588-659` CLC 查询循环里问硬件"下一个 tile 归谁"；两个 consumer warpgroup 各持一半累加器跑 mma 循环，完成后 `:840` 向 scheduler 上报取下一工作项；epilogue 由最后一个 consumer 执行 store_tail。PDL 下 435 行等依赖网格、492 行提前释放让下游重叠。

## 设计决策

① schedule tag 单向分派：Schedule 从 builder 传到 kernel SFINAE，改 tag 即换 kernel 文件，无运行时开关。② cooperative vs pingpong 以 TileM≥128 为界——大 tile 需两个 warpgroup 寄存器预算。③ scheduler 即 pipeline：CLC 硬件查询也要流水化+节流。④ smem union（2.x）→并列 struct（3.x）：warp specialization 后两阶段时间重叠，union 反而亏。⑤ 一个 GemmUniversalAdapter 吃两代 kernel。⑥ PDL 仅 SM90+ 且显式开启（`kernel_launch.h:96` 断言）。

## 新人提示

① 读 kernel 从 523 行的 `sm90_gemm_tma_warpspecialized.hpp` 入手，先看 `:284-288` 角色枚举再读 operator() 三大循环。② RasterOrder 去找 `tile_scheduler_detail.hpp:38`；`gemm_enumerated_types.h:48/57/69` 只有 Operand/GemmUniversalMode/SharedMemoryClearOption 三个枚举。③ StagesC/StagesD 在 `include/cutlass/epilogue/dispatch_policy.hpp:181-183`，不在 gemm 侧。④ `kernel_hardware_info.hpp` 是垫片实体在 `.h`。⑤ `tile_scheduler_params.h` 是 `.h` 后缀但 2582 行全是 3.x 内容——**后缀与代际不可互推**。⑥ sm90a 条件指令没开 arch flag 时，报错在运行期日志（`:281`）而非编译期。

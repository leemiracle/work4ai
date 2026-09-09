# 精讲：csrc/jit_kernels/heuristics/sm90.hpp —— 形状到内核参数的启发式映射

> 原文件：`csrc/jit_kernels/heuristics/sm90.hpp`（DeepGEMM，246 行）

## 一、角色定位

GEMM 内核没有放之四海皆优的 tile 配置：BLOCK_M/N/K、cluster 大小、流水级数都随问题形状（M/N/K、分组类型、数据类型）变化。本文件的 `SM90ArchSpec` 是 SM90（Hopper）上的**启发式决策器**（图谱 tour 第 5 步"启发式配置"）：给定 `GemmDesc`，枚举合法 tile 候选、按解析成本模型估耗时、选出最优 `Layout`，再派生存储/流水/启动配置，供 JIT 生成特化内核。它对应 SM100 的姊妹文件是 `heuristics/sm100.hpp`，公共类型在 `config.hpp`。

## 二、内部结构

`SM90ArchSpec` 全为静态方法，构成一条决策流水线：

- **`get_layout_candidates(desc)`**：枚举入口。BLOCK_M 候选按 GemmType 分支（Normal/Batched/KGrouped 为 {64,128} 加小 M 特例 16/32、BF16 输出加 256；MGroupedContiguous 只允许 `heuristics_runtime` 给出的对齐值；Masked 为 {64,128}）；BLOCK_N 按 `lcm(16, block_n_multiple_of)` 步进枚举（1D1D+FP32 输出为避 bank conflict 特设 start=24 并补 16；上限 256，1D2D 收到 192、1D1D 收到 160 防寄存器溢出）；BLOCK_K 固定为 `128 / 元素大小`（FP8=128，BF16=64）。
- **`get_storage_config`**：按主序与元素大小决定 A/B/C-D 的 swizzle 模式；1D1D 内核 store_block_m 固定为 wgmma_m=64（单 warpgroup 写回）。
- **`get_pipeline_config`**：共享内存预算 `smem_capacity = 232448` 字节，扣除 CD、barriers、额外 SFB/tensormap 后除以每级 A+B+SFA(+SFB) 占用，得上限 16 的 `num_stages`。
- **`get_launch_config`**：128 个 TMA 线程 + 128/256 数学线程（block_m≤64 用 128）。
- **`get_layout_info`**：解析成本模型，输出 wave 数、末波利用率与 `num_cycles` 估计。
- **`compare`**：以 `num_cycles` 小者胜。

## 三、外部连接

include CUTLASS 的 `mma_sm100_desc.hpp`（复用 `cute::UMMA::Major` 类型）与自家 `deep_gemm/common/types.cuh`、同目录 `common.hpp`/`utils.hpp`。运行时依赖全局 `heuristics_runtime`（M/K 对齐值、BLOCK_N 公倍数约束——这两个值可被 Python 侧 `set_block_size_multiple_of` 等接口影响）。其输出 `Layout`/`StorageConfig`/`PipelineConfig` 直接喂给 `jit_kernels/impls/sm90_fp8_gemm_1d2d.hpp` 一类宿主包装，后者把它们编进内核模板参数。

## 四、数据流

候选枚举是四层循环过滤：cluster_m × cluster_n（乘积 ≤2，SM 数必须整除 cluster；KGrouped 组数 >4 或 Batched 直接禁 multicast）× block_m × block_n，逐个剔除：①1D2D 展开（unroll）约束（block_n 与 block_k 之差必须整除其一）；②Masked/Psum 布局下 `ceil_div(n, block_n) % cluster == 0` 的 multicast 合法性；③寄存器约束——block_m 与 block_n 不得同时 >128；④swizzle 模式必须 ≥64B（32B 性能差）；⑤流水深度 `num_stages ≥ 3`（小块还要 ≥4）以掩盖 TMA 延迟。存活者按 `get_layout_info` 打分：以 L1/L2 每周期带宽（L2 取 `min(64B×SM数, ~6154B)`，L1 128B×SM）折算搬运周期，除以 wave 效率（块数/(wave 数×SM 数)）取 max 为预估周期；单 wave 时禁用 multicast（周期设 INT64_MAX 哨兵）。

## 五、设计决策

- **"枚举+成本模型"取代查表**：候选空间小（几十个），解析模型（只建模随配置变化的 L1/L2 周期，HBM 与算力视为常量）比实测调参快且可解释，注释明言这是有意简化。
- **Multicast 克制**：只在多 wave、组数少、整除性满足时启用 2-CTA cluster——避免 L2 OOB 与无效同步。
- **类型驱动的 BLOCK_K**：128B/元素 位数 的换算让 FP8 与 BF16 共用一套逻辑。
- **约束显式化**：寄存器上限、swizzle 下限、stage 下限都以 `continue` 过滤而非事后修正，保证候选即合法。

## 六、新人提示

调优入门先读 `GemmDesc` 定义（`config.hpp`）再回来；想理解"为什么我的形状选了 128×192 而不是 64×256"，把 `get_layout_info` 的带宽公式手算一遍最有效。新增 GemmType 时记得在 `get_layout_candidates` 补分支并检查 multicast 合法性条件。注意 `smem_capacity=232448` 是 Hopper 每 SM 上限，SM100 不同——别把 SM90 的 stage 数结论平移。性能回归时，先确认是不是候选被某个 `continue` 过滤导致次优配置胜出。

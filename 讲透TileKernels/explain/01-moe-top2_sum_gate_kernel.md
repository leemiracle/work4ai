# tile_kernels/moe/top2_sum_gate_kernel.py 精讲

> 原文件：`tile_kernels/moe/top2_sum_gate_kernel.py`（424 行）

## ① 角色定位

仓库**最核心的单内核**：DeepSeek 系 MoE 的 token 路由门控。一个 kernel 完成全流程——四种评分函数、专家偏置、按"组内 top2 之和"选组、top-k 选择、权重归一化、逻辑→物理专家映射、EP/TP 并行重排。上层 `top2_sum_gate()` 是薄封装。

## ② 内部结构

三段式：`@T.macro warp_reduce_sum`（5 轮 shfl_xor 蝶形归约）→ `@tilelang.jit` 内核工厂（19-303 行）→ Python 封装。工厂参数（`scoring_type/num_topk/num_groups/...` 与四个 `*_exists` 布尔）全部 **JIT 编译期特化**；`num_tokens` 等用 `T.dynamic` 留作运行时符号。核心 `@T.prim_func` 声明 13 个张量/标量参数，布局 `T.Kernel(num_tokens, threads=32)`——**grid 等于 token 数，一个 warp 一个 token**。内存层级用满：两组 scores shared、若干 local 寄存器与标量变量。

## ③ 外部连接

依赖 `utils.align/ceil_div`、`moe/scoring.ScoringFunc`（SIGMOID=0/SQRTSOFTPLUS=1/SOFTMAX=2/IDENTITY=3）与 `softplus` macro、`moe/common.get_topk_group_idx`（组选择 warp macro）。输出喂给同域 dispatch/combine 类内核。`TK_PRINT_KERNEL_SOURCE=1` 打印生成的 CUDA 源码。

## ④ 数据流

① mask 为 False 的 token 写 -1/0 后 `T.thread_return`；② 向量化加载 logits+bias（`num_vectorize=4`），逐元素 `T.isfinite` 断言；③ 评分：SOFTMAX 两遍——先 `exp(x-warp_max)` 存 shared 求和再相除，其余逐元素。**无偏分数**另存 `scores_wo_bias_shared`（185 行），**有偏分数**（+bias）用于排序；④ 选组：`num_groups==num_topk_groups` 时跳过；否则 `get_topk_group_idx` 按每组 top1+top2 之和选组，组索引冒泡排序保稳定，选中组分数收进寄存器；⑤ top-k：`num_topk` 轮"找当前最大"——上轮赢家置 -inf，warp shfl_xor 5 轮归约，**平局取更小索引**（247 行）保稳定排序；⑥ 权重取无偏分数，除 `topk_sum`（初值 1e-20 防零）乘 `routed_scaling_factor`；共享专家槽权重 1.0、索引 `lane + num_routed_experts - num_topk`；⑦ 物理映射：`duplicate_idx = (ep_rank + token*23333) % num_duplicates`（285 行，大质数打散负载）查 `to_physical_map`；⑧ ETP 掩码：目标 EP rank 的 TP 奇偶不匹配则置 -1，否则重排为本 rank 局部索引；⑨ 写 `topk_idx (tokens, num_physical_topk) int64` 与 `topk_weights`。

## ⑤ 设计决策

- **TileLang JIT 特化**：评分类型、分组形状、可选输入编译期固化，运行时分支消失；`T.dynamic` 只留随 batch 变的量避免重编译。三个 `pass_configs`（关 warp specialization/越界警告/线程存储同步）是显式的"程序员担保安全，编译器别多插同步"。
- **warp-per-token**：路由本质是数百专家上的归约+排序，单 warp shfl 通讯够用且免 shared 同步。
- **top2-sum 分组语义**：DeepSeek V3 分组路由按"组内前两名之和"衡量组重要性，本内核是该语义的逐 warp 实现。
- **路由与并行重排融合**：物理映射 + ETP 掩码本可拆两个 kernel，融合省两次全量读写；`fix_routing_mask` 通道允许逐 token 冻结路由复用旧结果，服务投机解码等场景。

## ⑥ 新人提示

1. 读不懂 warp 排序段就手推 5 轮 `shfl_xor(1<<i)` 蝶形。
2. 有偏分数管排序、无偏分数管权重，别"顺手统一"。
3. `assert num_topk <= warp_size` 等约束是算法边界，超界需换算法。

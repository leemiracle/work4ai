# LPLB/lplb/resources/csrc-tmpl/minilp.cu 精讲——单 SM 内点法 LP 内核

> 原文件：`LPLB/lplb/resources/csrc-tmpl/minilp.cu`（515 行 CUDA 模板）

## 一、角色定位

minilp.cu 是 LPLB 的数学心脏：**一个 CUDA block（占一个 SM）在动态共享内存里完整跑一遍线性规划内点法**，解出"组内每个 rank 的冗余专家该分走多少比例 token"。README 对问题的建模是"冗余专家成边、边容量为副本 token 数、LP 最小化组内不均衡"；这份文件就是该 LP 的 GPU 求解器，外加配套的计数与重定向两个辅助 kernel。它被 plugin.cpp 在运行时读入、NVRTC 按拓扑宏特化编译——本身不参与 AOT 构建。

## 二、内部结构

- **宏头**：默认 `GROUP_SIZE=8 / DUP_PER_RANK=2 / SM_Ver=900 / BLOCK_DIM=128`（Cube8P2E on Hopper，plugin.cpp 编译时会用 `-D` 覆盖）；`#undef uint64_t` 重定义为 unsigned long（NVRTC 头环境差异）。
- **线性代数原语**：`gaussian_elimination_solve<N>` 用 **cusolverdx** 的 `posv`（Cholesky 分解求解，decltype 表达式模板在编译期定制 SM/BlockDim/布局）；`matmulNT/matmulNN` 用 **cublasdx** 块级 GEMM。
- **维度常量**：`NC = GROUP_SIZE + GROUP_SIZE*DUP_PER_RANK`（约束数）、`NV = GROUP_SIZE*DUP_PER_RANK*2 + GROUP_SIZE + 2`（变量数：原始槽分流比 + 副本槽分流比 + 每 rank 的 max 松弛 + 全局 max 变量 + BigM 人造列）。
- **`smem_variables`**：dup_workload/b/a/c/ax2/ax2a/x/ax2c/r/d 全部矩阵与向量住共享内存；`get_solve_smem_size` kernel 把 `sizeof(smem_variables)` 报给宿主设置动态共享上限。
- **三个入口 kernel**：`kernel_solve`（五段式主流程）；`kernel_count_idx`（SM 分片直方图计数 + 跨 block 前缀归约）；`kernel_map_idx`（按前缀与期望计数做在线重定向）。辅助 `split_and_align` 把元素区间按 blockDim 对齐切分（防跨块原子竞争）。

## 三、外部连接

上游是 plugin.cpp 的 `compile_cubin`（读文件 → NVRTC → 与离线 `libcusolverdx.fatbin` LTO 链接）；三个 kernel 经 `cudaLibraryGetKernel` 取句柄后由 solve/count_idx/map_idx 发射。NVSHMEM device API（`nvshmem_putmem_signal_nbi` / `nvshmem_signal_wait_until` / `nvshmem_team_translate_pe`）在 USE_NVSHMEM 时参与 workload 全局聚合。产出被 planner.py 的 `solve_probs/weighted_select_target` 消费；tests/test_solve.py 从 Python 侧验证 max/mean 负载比。

## 四、数据流

**kernel_solve 五段**（grid = n_group 个 block，各管一组）：

1. **workload allreduce**（NVSHMEM 分支）：block 0 负责——写本节点缓冲 → `putmem_signal_nbi` 环状 allgather 到各节点 → 单线程 `signal_wait_until` 等齐 → 求和写入节点内共享缓冲 → IPC 原子信号量等本节点各卡到齐 → 全体求和得 global_workload；随后 warp shuffle 归约 max 并把全局负载归一化到 max=1（无 NVSHMEM 时仅做归一化）→ `cg::this_grid().sync()`。
2. **LP 构造**：`dup_workload` 按 phy2log 聚合出每冗余槽负载；约束矩阵 A 的前 GROUP_SIZE 行是各 rank 的负载方程（原始槽系数 + 副本槽系数 + 松弛变量 -1×max 变量），后 GROUP_SIZE 行是"分流比和 = 1"；b 向量前段为固定专家负载取负、后段为 1；目标 c 只罚 max 变量（系数 1）和 BigM 列（1000）；**BigM 列**按 `A@vec(1)=b` 补齐，保证 x 全 1 时人造可行。
3. **IPM 主循环（5 步）**：affine scaling 内点法——`ax2 = A * x²` → `ax2a = ax2 @ Aᵀ`（matmulNT）→ Cholesky 解 `ax2a @ y = ax2 @ c` → `r = yᵀ @ A`（matmulNN）→ 下降方向 `d = x ⊙ (c - r)` → `alpha = 0.999 / d_max` → `x *= 1 - alpha·d`。
4. **可行性判定**：`d_max < 0.1 && 0 ≤ x[max] < 1e-4 && max_residual < 0.05` 才算成功，`atomicAdd(avail_num)` 累计成功率；失败回退 `result = 0.5`（均分）。
5. **回写** x 的分流比到 result。

**kernel_count_idx**：每 block 对自己区间做共享内存直方图（atomicAdd），grid sync 后末段循环把各 block 计数累成前缀和布局（`counts[sm*n+i] += counts[(sm-1)*n+i]`）。**kernel_map_idx**：期望计数 = 总计数 × o_weight；`smem_log2r` 双槽查表（原槽/冗余槽），token 序号经 `(cnt*499+41) % total` 散列后与期望计数比较决定去向。

## 五、设计决策

- **LP 放进单 SM**：求解在路由热路径上，CPU 往返与 launch 延迟不可接受；问题规模小（NC≤24、NV≈52），一个 block 装得下，cuSolverDx/cuBLASDx 的"块级"原语与这个粒度精确匹配。
- **affine scaling 而非单纯形**：固定 5 步迭代、无分支、无表驱动——GPU 友好；BigM 人造列给出 x=1 的初始可行点，是教科书技巧的工程化。
- **不可行回退 0.5**：LP 失败时退化为均分而非报错，可用性优先；avail_counter 把失败率暴露给监控。
- **`(cnt*499+41) % total` 伪散列**：token 在主/冗副本间的分配要"确定但均匀"，真随机数需要跨 SM 状态同步，代价高且不可复现。
- **归一化 max→1**：负载是 int32 计数（可达百万级），直接进 float32 矩阵会丢精度。
- **内存预算自报**：`get_solve_smem_size` 把 sizeof 暴露给宿主——共享内存需求随 GROUP_SIZE/DUP_PER_RANK 编译期变化，运行时自报是最不易错的方案。

## 六、新人提示

读 kernel_solve 前先手推小规模 LP（2 rank × 1 冗余）把 A/b/c 写在纸上，五段式每段对应教科书一章。499/41 是经验魔数，不是素数讲究。要 debug 就在 plugin.cpp 的编译选项里临时加 `-DDEBUG_DUMP`，kernel 里有现成的 printf 分支（A/b/c/x 全打印）。改 GROUP_SIZE 必须同步心算 smem（编译期没有 static_assert，超限在 launch 时才炸）。kernel_count_idx 的前缀布局是 map_idx 的隐式协议——单独改任何一个都要重审另一个。

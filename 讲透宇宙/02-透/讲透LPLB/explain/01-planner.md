# LPLB/lplb/planner.py 精讲——动态负载均衡总调度

> 原文件：`LPLB/lplb/planner.py`（266 行，Python 侧唯一对外类）

## 一、角色定位

planner.py 是 LPLB（Linear Programming Load Balancer）的 Python 主干：`Planner` 类经 `lplb/__init__.py` barrel 重导出为整个包的公共接口。它站在 MoE 专家并行的运行路径上，职责一句话：**拿冗余专家拓扑 + 当前路由负载统计，解一个线性规划，输出"每个 token 该走主副本还是冗余副本"的分流比例**。它本身不做重活——计数、求解、重定向三个重活全部下沉到 CUDA（csrc/plugin.cpp），它负责拓扑代数与流程编排，并决定"何时静态重排、何时动态求解"。

## 二、内部结构

- **`_get_solver`**：`functools.lru_cache` 按 `(n_group, group_size, dup_per_rank, n_local_experts, n_combined_experts, ep_group)` 缓存 `CompiledSolver`——JIT 编译昂贵，同拓扑进程内只发生一次。block_dim 固定 256。
- **`Planner.__init__`**：`r2o = redundant_to_original.int().cuda()`（[group_size, num_redundants]，冗余专家→原专家索引）；`o2r = r2o.argsort(dim=0)` 逆映射；从 r2o 形状推 `group_size/num_redundants`；`n_group = ep_size // group_size`；`combined_redundant_experts = (本地物理数 - 本地逻辑数) // num_redundants`（把冗余专家打包成 LP 变量组）；最后 `update_redundancy_mapping()` 建默认 phy2log。
- **`update_redundancy_mapping(workload=None)`**：静态重排。workload 为 None 时 phy2log 退化为 `arange`（纯直通）；否则调 `lplb/eplb.py` 的 `rebalance_experts`（内嵌 EPLB，"reordering only" 不做复制）得无冗余布局，再按历史负载 `argsort(descending=True)` gather 排序，每组取前 `combined * num_redundants` 个热门专家，按 r2o gather 复制到对端 rank，拼出 phy2log，并构建 log2phy（转置后插入保证原专家先于副本）与 logcnt（断言 `max_logcnt == 2`——每逻辑专家恰好两个物理副本，这是 LP 边模型成立的前提）。
- **三个执行原语**：`count_workload`（solver.count_idx 按 SM 分片计数）；`solve_probs`（workload reshape 成 [n_group, group_size, 本地逻辑数]，ep_group 存在且 DeepEP 未初始化时 `torch.distributed.all_reduce`，然后 solver.solve）；`weighted_select_target`（solver.map_idx 按前缀计数重定向）。`run()` = 三步组合，n_sms 默认取 `multi_processor_count`。

## 三、外部连接

向下两条腿：`lplb._cpp.CompiledSolver`（setup.py 把 csrc/plugin.cpp 编出的扩展，NVRTC JIT 出三个 CUDA kernel）与 `lplb/eplb.rebalance_experts`（EPLB 算法的内嵌副本）。`init_from_deep_ep(buffer)` 对接 DeepEP：`solver.init_comm(device, not buffer.low_latency_mode, buffer.num_rdma_bytes == 0)` 三个布尔决定 NVSHMEM 初始化策略（是否多平面、是否需要自 init），`deep_ep_initialized` 标志保证幂等。测试面：tests/test_solve.py 验证求解后每 rank 负载 max/mean 比不超容差；test_idx_processing.py 对照 `scatter_add_` 参考实现验证计数与重定向；scripts/run_ep16_cube8p2e.py 是 EP=16 Cube 拓扑的 torchrun 端到端基准。

## 四、数据流

初始化流：用户给 r2o 拓扑（如 Cube8P2E：8 rank 一组、每 rank 2 个冗余槽）→ 构造 o2r/combined 计数 → EPLB 静态重排产出 phy2log（物理专家号→逻辑专家号的全局表）→ CompiledSolver 构造触发 JIT。

稳态运行流（每次路由决策）：`idx`（本 rank 的逻辑专家索引张量，-1 忽略）→ `count_workload` 得 `(总计计数, 每 SM 计数矩阵)` → `solve_probs` 把负载（可选 all_reduce 成全局）喂给 LP kernel，返回 `o_weight [n_group, group_size, dup_per_rank]`（各冗余专家的分流比例）与全局负载 → `weighted_select_target` 以"每 SM 前缀计数 + o_weight"把逻辑 idx 在线映射成物理 idx（主/冗余副本按比例分摊）。avail_counter（可行性计数）一路透传，LP 不可行时 kernel 回退 0.5 均分。

## 五、设计决策

- **结构化冗余拓扑**：docstring 立了三条约束——每 rank 冗余数相同；任一 rank 的第 i 个冗余必须是另一 rank 第 i 个专家的副本；从而每冗余专家恰被两 rank 共享（LP 里"冗余专家成边"）。扩展条款允许可变冗余数为倍数以分组做权重分发。
- **静态 + 动态两级均衡**：EPLB 重排是慢时间尺度（改物理布局，需停机/同步），LP 分流是快时间尺度（逐 step 在线解）——两级分工避免"复制专家"这种重操作进热路径。
- **lru_cache 工厂**：把"拓扑参数 → 求解器实例"的映射变成进程级缓存，配合 cubin 磁盘缓存（plugin.cpp 侧）双层去重。
- **DeepEP 复用而非重建**：NVSHMEM team 由 DeepEP 初始化过就直接借（`not low_latency_mode` 等参数只影响走哪条初始化分支），省一次集合通信栈起栈。
- **int32/int64 纪律**：idx 走 int64（torch 路由张量原生）、拓扑表 int32、workload int32 计数——与 C++ 侧断言严格对齐。

## 六、新人提示

先把 r2o / o2r / phy2log / log2phy 四张映射的手推一遍再读别的（update_redundancy_mapping 里那几段 gather/reshape 是全文件最绕处）。调优先跑 tests/test_solve.py 的参数化用例熟悉输入输出形状。README 的 Cube8P2E 是默认调优目标（minilp.cu 的默认宏同此）。注意 `solve_probs` 的 all_reduce 只在"有 ep_group 且未走 DeepEP 路径"时发生——两条全局聚合路径互斥，别重复聚合。

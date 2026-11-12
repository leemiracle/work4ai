# 02 测量器家族：cold/hot/cpu_only/CUPTI 四种策略与计时核心

## 角色定位

测量器（measurer）是 nvbench 的采样引擎：给定一个 state，负责启动 kernel、计时、攒样本、问判据要不要停。`nvbench/detail/` 四种策略对应四种测量语义——冷启动延迟、热稳态吞吐、纯主机路径、硬件计数器剖析。选择权在 exec 标签：`nvbench/detail/state_exec.cuh:55` 的 `state::exec` 按 tags 分派，cold 分支 `nvbench/detail/state_exec.cuh:77`、cold|hot :81、cpu_only :86、组合 :92/:96。理解四者的差异 = 理解"你测的是什么数"。

## 内部结构

- **measure_cold**（声明 `nvbench/detail/measure_cold.cuh` 321 行，实现 `nvbench/detail/measure_cold.cu` 573 行）：逐次冷启动——每次 launch 前刷 L2、逐 kernel 计时。构造期读配置（`nvbench/detail/measure_cold.cu:50-54`）；判停 `nvbench/detail/measure_cold.cu:175-202` `is_finished`（min_samples+判据+超时三重出口）；`:223` 产出 `nv/cold/sample_size` 等摘要。
- **measure_hot**（`nvbench/detail/measure_hot.cu` 250 行）：连续采样不清理状态，自适应批大小——`nvbench/detail/measure_hot.cu:43` `predict_batch_size`、`:104` `predict_cuda_batch_size`、`:131` `grow_batch_size`（预测→倍增）。
- **measure_cpu_only**（`nvbench/detail/measure_cpu_only.cxx` 306 行）：纯主机路径，CPU 计时，演示 `examples/cpu_only.cu`。
- **measure_cupti**（`nvbench/detail/measure_cupti.cu` 273 行）：硬件计数器会话嵌入冷测量循环；`nvbench/detail/measure_cupti.cu:182` 处理 profiler 构造失败。仅当 `NVBENCH_HAS_CUPTI`（`cmake/NVBenchCUPTI.cmake` 探测置宏）时编译。

**共享计时核心**：`nvbench/detail/measure_cold_launch_timer_core.cuh`（183 行）是 config/core/cleanup_guard 三件套，被 cold 与 cupti 共用（NOTES batch-19 甄别）；`nvbench/detail/kernel_launcher_timer_wrapper.cuh` 把 kernel 启动包装成可计时单元；设备侧时戳 `nvbench/detail/timestamps_kernel.cu`（81 行）。

**测量环境控制三件套**：L2 flush（`nvbench/detail/l2flush.cuh:42` cudaMalloc 与 L2 等大缓冲，`:68` flush() cudaMemsetAsync 整块写零）、GPU 频率（`nvbench/detail/gpu_frequency.cxx`：NVML 读时钟+has_throttled）、独占负载（`nvbench/blocking_kernel.cu` 134 行多 SM 均布自旋）。超时告警收口在 `nvbench/detail/measure_timeout_warnings.cuh`。

## 外部连接

- 上游：state_exec 按 exec 标签选择测量器（`nvbench/exec_tag.cuh:40` `enum class exec_flag`）；`nvbench/runner.cxx:38` `handle_sampling_exception` 分流测量期异常（:42 skip vs 致命）。
- 下游：每批样本喂判据，判停后 `nvbench/detail/statistics.cuh`（533 行）+ `nvbench/detail/online_linear_regression.cuh`（199 行）汇总；样本缓冲在 `nvbench/detail/ring_buffer.cuh`（247 行）。
- CUPTI 线：measure_cupti 只依赖统一接口 `nvbench/cupti_profiler.cuh`（33 行选择头），实现双份——`nvbench/cupti_profiler_host.cxx`（709 行，CUPTI Profiler API）与 `nvbench/cupti_profiler_nvpw.cxx`（761 行，Nsight Perfworks SDK，metric_evaluator 依赖树+user-loop 重放）。

## 数据流

以 cold 为例：runner 驱动 state → 循环 {刷 L2 → 计时核心包住一次 launch（timestamps_kernel 记时戳对）→ cuda/cpu 双时间入 ring_buffer → 判据 add_measurement → is_finished?} → 超时置 m_max_time_exceeded → generate_summaries 把统计+超时警告（`nvbench/detail/measure_cold.cu:204`）写回 state。hot 不刷 L2、按预测批大小连发一批整体计时；cupti 循环外再套 profiler 会话（每 pass 重放负载）。

## 设计决策

1. **冷热分离而非参数化**：冷/热是两种测量语义（延迟 vs 吞吐），L2 状态、批大小策略、摘要键全不同——分成两类。
2. **L2 flush 用"写满同尺寸缓冲"**（`nvbench/detail/l2flush.cuh:68`）而非内建缓存 API：可移植、语义确定，代价是带宽开销——只放 cold 循环。
3. **自适应批大小**：用户给"目标批时长"而非批次数。
4. **CUPTI/NVPW 双后端同构**：两代驱动栈各一份实现、接口一致，measure_cupti 零感知。
5. **超时打警告不抛异常**：结果仍产出（带警告），比硬失败适合 CI 长跑。

## 新人提示

- 想清楚你报的数是 cold 还是 hot：`state.exec(nvbench::exec_tag::cold, ...)` 与默认 exec 的语义差 = 每次刷 L2 与否。带宽走 hot，首次调用延迟走 cold。
- `blocking_kernel` 在 `nvbench/state.cuh:255` 注释处有死锁告诫：与默认 exec 语义搭配可能死锁，读注释再动手。
- CUPTI 构建默认可能未开：看 `cmake/NVBenchCUPTI.cmake` 探测逻辑与 NVBENCH_HAS_CUPTI 宏。
- 图谱工艺：.cuh 符号全部手扫（README 勘误#6）；launch_timer_core 的"双消费者"关系是 NOTES 甄别结论。

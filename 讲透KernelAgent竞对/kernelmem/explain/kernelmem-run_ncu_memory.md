# 深解 KernelMem 剖析双件：run_ncu_memory.py + run_nsys.py

> 对象：`run_ncu_memory.py`（1151 行）/ `run_nsys.py`（439 行）/ `config_metrics.ncu-cfg` / `config_section.ncu-cfg`
> 图谱定位：两者均被 `main_memory_latest.py:_run_single_task` 调用，是性能记忆（profiling evidence）的采集端；两个 .ncu-cfg 通过 `configures` 边指向 `run_ncu_memory.py`。

## ① 角色定位：NCU 管细、nsys 管粗

这是**双探针互补架构**，为优化 judger 提供两种粒度的性能证据：

- **run_ncu_memory.py（NCU = Nsight Compute）**：kernel 级**细粒度指标**。回答"这个 kernel 内部慢在哪"——计算 vs 访存、occupancy 受什么限制、warp 停在哪种依赖上、分支分化多严重。NCU 用 kernel replay 模式重放被监控 kernel 多次收集计数器，开销大但指标深。
- **run_nsys.py（nsys = Nsight Systems）**：进程级 **launch 行为**。回答"这个 kernel 被启动了多少次、占多少时间"——不重放、低开销、全轨迹。launch count 是"kernel 太碎、该上 CUDA Graph / 合并"这类**结构性优化**的直接证据（judger 模板明文允许用 "Nsight Systems launch counts / many short kernels" 论证 cuda_graph_capture 方向）。

一句话：NCU 出"微观病理切片"，nsys 出"宏观行为统计"，二者拼进同一个优化 prompt。这个分工也解释了为什么 nsys 端没有 kernel 名过滤参数——它本来就不深入 kernel 内部，全量记录轨迹后再在 stats 端按名字聚合即可；而 NCU 端必须精确指定目标，否则重放开销会失控。

## ② 内部结构

### run_ncu_memory.py 三段流水线

1. **`profile_bench`（组装+执行 ncu 命令）**：`ncu --config-file-path <cfg> --log-file=<csv> python bench.py`。kernel 过滤用 `--kernel-name=::regex:\b<转义名>\b`（单名，容忍参数签名后缀）；`--test <kernel_file>` 指定被测 kernel；`--repeat/--device-idx` 透传。**关键策略：多 kernel 时逐个单独跑 ncu**（每个 kernel 一轮 metrics+section），因为 `--launch-count` 是全局配额，合并跑会漏采排在后面的 kernel；跑完由 `_merge_multiple_ncu_csvs` 用 `==METRICS_START:kernel名==` / `==SECTION_START:==` 标志行合并成单 CSV（metrics 共享一次表头，section 各带表头）。执行用 `Popen + preexec_fn=os.setsid` 建进程组，超时先 SIGTERM（5s 宽限）再 SIGKILL 整组杀，防止 bench 卡死泄漏。
2. **`load_ncu_metrics`（CSV→DataFrame）**：兼容三种历史格式（标志行版 / CSV section 版 / 文本 section 版）；`read_csv(comment="=")` 跳过 ncu 的 `==` 注释行；列选择按 `METRIC_COLUMNS_NEW` 前缀匹配**保留全部变体**（.avg/.pct/…）；删单位行、按 name_list 三级模糊匹配（`_extract_core_kernel_name` 剥 `_vec4/_v2/模板参数/函数签名` → contains → prefix）；`select="last"` 取末次 launch 代表稳态。sections 另解析为 `dict[kernel名]=CSV字符串`。
3. **`metrics_to_prompt`（DataFrame→prompt 文本）**：指标转 JSON（按 Kernel Name 分键、round 3 位、NaN/inf/Timestamp 经 `_deep_clean` 全转 None 防序列化崩），输出 `# Metrics (JSON)` + `# Detailed Section Analysis` 两段 markdown 代码块；空数据时显式 WARNING 提示"kernel 名与 ncu 采到的不匹配"。

### run_nsys.py 两段流水线

1. **`profile_bench`**：`nsys profile -t cuda,nvtx,osrt --sample=none -o <rep> python bench.py`（不采样 CPU 栈，降开销）；nsys **无 kernel 名过滤**，过滤留给 stats 端。同样进程组超时（默认 300s）。附带 `extract_cuda_kernel_names`：正则从 kernel 源码抽 `__global__ void 名(`（含 `__launch_bounds__` 变体），这是双探针共用的目标名单来源。
2. **`extract_kernel_launch_counts`**：`nsys stats --report cuda_gpu_kern_sum` 输出的是**文本表格**（非 CSV），按 2+ 空格分列、动态定位 Instances 列与末列 Name、去千分位逗号，再用 contains+core-name 剥离法把轨迹里的 kernel 聚到目标名下；`load_nsys_stats` 整理为 `[Kernel Name, kernel_launch_count]` DataFrame 并落 CSV。

## ③ 采集配置审计

**config_metrics.ncu-cfg（原始指标，约 30 项）**：`--launch-skip=2 --launch-count=6 --replay-mode=kernel --page=raw --csv`。指标按瓶颈判定逻辑分层：
- **Roofline 双轴**：`sm__throughput%.elapsed`（算力利用率）vs `gpu__dram_throughput%.elapsed`（带宽利用率）——一高一低即分出 compute-bound / memory-bound，这是第一层判决。
- **Occupancy 因果链**：`sm__warps_active%` + `launch__occupancy_limit_registers/shared_mem/warps` + `launch__registers_per_thread/block_size/shared_mem/waves_per_multiprocessor`——不仅说"并行度不够"，还指出**是寄存器还是共享内存限制的**，直接映射到可操作动作（降寄存器/改 block size）。
- **停顿分解**：`smsp__warp_issue_stalled_long/short_scoreboard、no_instruction、not_selected_per_warp_active`——long scoreboard 高=访存延迟暴露，not_selected 高=调度竞争过并行。
- **分支分化**：`sass_branch_targets_divergent/uniform` + pred_on 比例，对 reduction/掩码类 kernel 关键。
- **层级补充**：L1/L2 命中率与吞吐（`l1tex__*`/`lts__*`）区分"DRAM 慢"还是"cache 友好度差"。

**config_section.ncu-cfg（整节报告）**：`--launch-skip=2 --launch-count=3`，七个 section：Occupancy / MemoryWorkloadAnalysis / ComputeWorkloadAnalysis / SpeedOfLight / WarpStateStats / SchedulerStats / SourceCounters——面向人读+LLM 读的成套解读（如 SpeedOfLight 的 SM/Memory 双百分比），count 更少因为 section 采集更贵。

两配置的分工即"机器可判定的原始数字"（metrics）与"成节上下文叙述"（section），一起进 prompt，judger 可交叉印证。指标清单并非照抄 `--set` 预设，而是从"瓶颈分类决策树"反推的最小充分集：先看双轴分 compute/memory-bound，再沿对应分支下钻限制因素与停顿原因，每一层指标都对应一个可执行的优化方向（降寄存器压力、改分块、向量化访存、消除分化等）。这也呼应源码中 `METRICS`→`METRICS_NEW` 的演进：旧版以 DRAM 字节为主，新版补齐了停顿分解与 occupancy 因果链，判据更完整。

## ④ 数据流

`main_memory_latest.py:_run_single_task` 每轮优化循环：

```
kernel 源码 --正则--> kernel_names
  ├─ ncu profile_bench(两 cfg 各跑一遍) → ncu_temp_{sid}.csv（标志行合并格式）
  │    → load_ncu_metrics(name_list, select="last") → (metrics_df, sections_dict)
  │    → metrics_to_prompt → metrics_block；原始 CSV 存 profile_dir/{kernel}_ncu.csv
  ├─ nsys profile_bench → .nsys-rep → load_nsys_stats → nsys_df（launch_count）
  │    → 失败不致命：fallback 用 NCU 行数 len(rows) 当 launch_count
  └─ build_judger_optimization_prompts(
        ncu_metrics_block=metrics_block,      → 模板变量 {NCU_METRICS}
        metrics_df,                            → 喂 machine_check_ver2 做 YAML 结构化校验
        nsys_csv_path)                         → {NSYS_LAUNCH_COUNTS} + kernel_launch_count
     → judger LLM 输出"单一最 impactful 优化方向+计划"
```

即：profile 结果→CSV/DataFrame→markdown/JSON 文本块→judger prompt 的证据字段；结构化 metrics_df 另走机器校验通道防 LLM 幻觉。

## ⑤ 设计决策与新人提示

- **NCU 开销意识**：replay 模式下被监控 kernel 重放 N 次采计数器，整体比原生慢一个量级以上。代码体现：metrics/section 分别给 600s/900s 超时；level3 任务显式 `timeout_override=1800s + repeat=3`。
- **launch-skip=2 是稳态假设**：跳过前 2 次启动避开 JIT/冷缓存失真——改 bench 时保证至少有 2 次"热身" launch。
- **多 kernel 必须分跑**：`--launch-count` 全局配额会被第一个 kernel 吃光，逐 kernel 独立运行再合并是正确性前提，不是优化。
- **进程组清理是硬要求**：`os.setsid + killpg` 两级终止，孤儿 GPU 进程会污染后续 profiling。
- **复用 torch 扩展缓存**：代码内 FIX 注释记录了教训——曾用临时 `TORCH_EXTENSIONS_DIR` 导致 ncu 环境下重复编译卡死，现故意不设置以复用 `~/.cache/torch_extensions`。
- **环境耦合警告**：ncu 二进制路径 `/root/miniconda3/envs/robust_kbench/bin/ncu` 与配置路径 `/root/KernelMem/*.ncu-cfg` 硬编码，迁移部署需先改这两处；ncu 采计数器还需 root/性能权限。
- **CSV 是自造混合格式**：`==` 注释 + metrics 表 + section 表 + `==METRICS_START==` 标志混在一个文件，`load_ncu_metrics` 因此有三种格式兼容分支——新增解析逻辑时先弄清自己在哪个分支。
- **降级链完整**：nsys 挂→launch_count 降级；ncu 挂→保存部分 CSV（`_ncu_error.csv`）+ 复用上轮 kernel，单探针失败不阻断循环。
- **名字对齐是全程暗线**：源码正则抽的裸名、ncu demangled 全名、nsys 轨迹名三套体系不完全一致，`_extract_core_kernel_name` 的剥离规则（`_vec\d+`/`_v\d+`/模板/签名）贯穿采集、解析、聚合三端——新增 kernel 命名变体时优先检查这条链。
- **prompt 里空指标是显式信号**：`metrics_to_prompt` 对空数据输出 WARNING 而非静默空串，让 judger 知道是"名字没对上"而非"没有数据"，排障时先看这里。

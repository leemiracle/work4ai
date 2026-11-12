# run.py 深度解析：bench-suite 预提交回归基准的编排核心

> 源码：`tirx_kernels/bench_suite/run.py`（2612 行）｜图谱节点 `file:tirx_kernels/bench_suite/run.py`（complexity=complex，fan-in 59）

## 角色定位：14 层架构中的位置

在 TIRx-kernels 的 14 层知识图谱中，run.py 位于**基准编排层（bench-harness）**，与 ab.py、ratio_diff.py 同层。TIRx-kernels 是 mlc-ai 的 GPU kernel 合集与调度库——以 TVM TIR 为 kernel 表示，统一接入 flash-attention/cudnn/flashinfer/deepgemm 等上游源。这类库的命门是：**每一次提交都可能引入性能回归**，而人肉盯 GPU 既不可重复也不可扩展。run.py 就是预提交回归基准的运行器：从 kernel YAML 配置装配工作负载，协调多张 GPU 并发执行，采集完整 provenance（环境快照），最后与 pinned baseline 对比并给出机器可判定的退出码（0 通过 / 1 失败 / 2 配置错误 / 3 回归）。图谱显示它的 fan-in 高达 59——59 个 config YAML 都在"配置"它，另被 `__main__.py` 引用、README 文档化，是整个 bench_suite 的骨架。

## 内部结构：41 个子节点分七个功能区

图谱 contains 边列出 4 类 + 37 函数，源码按注释分区更清晰：

| 区块 | 行号区间 | 核心成员 | 职责 |
|---|---|---|---|
| 工作负载装配 | 114-299 | `_read_kernel_config` / `load_config_dir` / `write_generated_workloads` | 递归读取 `config/**/*.yaml`，严格校验（kernel 名==文件名、去重、default 标记、selection_role 三元组），并强制 registry 与 config 目录**双向一致**（269-279 行：注册了没配置、配置了没注册都报错） |
| GPU 资源池 | 302-545 | `GpuPool` | 世代化的独占 GPU 池（下详） |
| 输出与日志 | 548-586 | `_Tee` / `log()` | stdout/stderr 同时进终端与 run 日志，`_log_lock` 保证多线程行原子 |
| 探测与编译档案 | 588-716 | `probe_gpu` / `detect_usable_gpus` / `gpu_compile_profile` / `partition_workloads_by_arch` | 并行真负载探测 + NVML 编译档案（sm_100a/103a/107a）+ 按架构分流工作负载 |
| 陌生进程检测 | 719-941 | `_pid_sm_on_gpus` / `_BenchPidRegistry` / `_our_pids` / `_attempt_strangers` | 区分"自家基准进程"与"陌生 GPU 占用"，是干扰判定的基础 |
| prepared 子进程 | 943-1119 | `_spawn_prepared_attempt` / `_receive_child_messages` / `_PreparedAttempt` | socketpair 控制通道 + one-shot 子进程生命周期 |
| provenance 与定稿 | 1122-1610 | `collect_repo_git` / `collect_kernel_fingerprint` / `package_provenance` / `_finalize_bench_record` / `write_summary` | 三层可追溯性快照 + 结果记录校验 |
| 调度主循环与 CLI | 1612-2612 | `run_scheduled_jobs` / `main` | 三线程编排 + 消息泵 + 退出码语义 |

## 外部连接：图谱边视图

- **imports →** `registry.py`（`kernel_index` 提供各 kernel 的 `runtime_cuda_archs`，用于架构分流）、`runner.py`（默认 rounds/cooldown 常量，以及 `PREPARE_CUDA_ARCH_ENV`/`PREPARE_NUM_SMS_ENV` 环境变量契约——这是 prepared 子进程"无 GPU 也能编译"的钥匙）、`impls.our_impls`。
- **被 imports ←** `__main__.py`（`python -m tirx_kernels.bench_suite` 入口）。
- **延迟 import（函数体内）←** ab.py 复用它的 `GpuPool`/`detect_usable_gpus`/`gpu_compile_profile`/`_tir_repo_root`；ratio_diff.py 复用 `load_config_dir`/`partition_workloads_by_arch`。延迟引用既避免 CLI 模块级循环依赖，也让这两个文件能独立脚本执行。
- **configures ←** 59 个 `config/**/*.yaml`；**documents ←** `bench_suite/README.md`。

## 数据流：主流程走读

`main()`（2158-2612）是唯一入口，按序：

1. **参数校验**（2280-2301）：rounds/cooldown/阈值/并发上限的非法值直接 exit 2。注意 2202-2204 行注释：**故意不提供 `--gpus`**——人工钉卡会绕过利用率门禁把任务派到忙卡上。
2. **装配工作负载**（2303-2337）：无 `--workloads` 时从 config 目录组装全部 `default: true` 条目，物化为 `workloads.generated.yaml` 供审查复现。
3. **A/B 分流**（2339-2381）：`--ab-before REV` 时整体转交 `ab.run_ab`，本文件的其余流程不执行。
4. **日志与 run id**（2383-2407）：递增整数 run id；`_Tee` 挂接管 stdout/stderr；`latest.log` symlink 立即指向新日志，`tail -f` 可以跟上。
5. **GPU 自动选择**（2409-2494）：可见卡 → 并行 fp16 512×512 matmul 探针（PROBE_SCRIPT，94-111 行）→ 剔除探测失败卡 → `gpu_compile_profile` 要求所有可用卡**同构** → 按编译档案架构分流/校验工作负载。
6. **调度循环** `run_scheduled_jobs`（1736-2155）——本文件心脏，三线程协作：**occupancy 线程**每 5s 调 `pool.refresh_external_occupancy()`；**dispatch 通知线程**阻塞在 `pool.wait_for_change(generation)` 上，池状态一变就向 socketpair 写一字节唤醒主循环；**主循环**跑 `select` 消息泵（1974 行），统一响应两类事件——派发时机与子进程控制消息。每个 `_PreparedAttempt` 走状态机 `PREPARING_CPU → READY → ASSIGNED → RUNNING_GPU → RESULT/FAILED`：子进程先在 CPU 上编译（`PREPARE_CUDA_ARCH_ENV` 让它不碰 GPU），READY 后父进程 `dispatch_ready()`（1862-1898）尝试原子领卡，发 `ASSIGN` 消息（附 GPU 索引与 UUID）；子进程回 `RUNNING_GPU` 时父进程**复核回报的物理 UUID 是否等于派发预期**（2016-2029 行，防串卡）；`RESULT_READY` 经 `_finalize_bench_record`（1615-1733）校验协议（轮数、round_aggregate=mean、cooldown、实现顺序排列、样本正有限）后聚合为 `impls` 均值。
7. **干扰恢复**：运行中每 0.5s 对 RUNNING_GPU 的卡做 per-PID SM 采样，发现陌生进程 → 发 SIGUSR1 → 子进程回报 `INTERFERED` → `acknowledge_interference`（1815-1840）释放卡、attempt+1、**回到 READY 原地重试**（复用已编译产物）；30s 未确认停止则判死。
8. **落盘与退出**（2510-2608）：`write_run` 写 runs/N.json（含 git 三仓 SHA、kernel tree SHA、包 provenance、pipeline 元数据、干扰重试日志），`write_summary` 出人类可读报告，失败 exit 1；`--with-references` 时才追加 ratio_diff 回归报告，回归 exit 3。

## 设计决策：值得学习的模式

- **世代化（generation）唤醒**：GpuPool 用单调递增的 `_change_generation` + Condition（329-332 行）。等待方记下当前世代号，`wait_for_change(generation)` 只在世代**改变**时醒来——避免"轮询是否有变化"的经典竞态。再用 socketpair 把"池变化"翻译成 select 可读事件，让单线程消息泵同时吃定时器与事件两类唤醒，这是事件循环设计的教科书手法。
- **随机选卡 + 亲和重取**：`try_acquire_many` 用 `random.sample` 随机挑卡（474 行）防止多实例热点聚集；而干扰重试优先 `try_acquire_exact(gpu_affinity)` 回到原卡，保持数据可比。
- **真负载探针**：nvidia-smi 的"free"看不出驱动挂/ECC/cuBLAS 初始化失败/MIG 限制（90-93 行注释），一个真实 matmul 才能暴露。
- **PID namespace 容错**：NVML 报 host PID 而 `/proc` 可能在容器 namespace——`_attempt_strangers`（918-940）利用"派发前池已证明卡静默"这一不变量，把首次观察到的活跃集归属本次尝试，后续新增才算干扰。
- **三层 provenance**：commit SHA 会被 squash/rebase 改写，所以补 **git tree SHA**（Merkle 内容寻址，merge 前后不变，1199-1230 行注释明说动机）+ PEP 610 `direct_url.json` 追 pip 安装来源。基线可比性靠内容指纹而非历史指针。
- **fail-closed**：`_pid_sm_on_gpus` 采样失败返回 None，调用方一律按"有干扰"处理（1945-1956），绝不静默放行。
- **退出码语义分离**：失败(1)/配置错误(2)/回归(3) 是三种不同的 CI 动作，混淆它们会让自动化退化成人肉分诊。

## 新人提示

- 阅读切入点：先读文件头 docstring（退出码声明）与 `bench_suite/README.md`，再从 `main()` 倒着读；`_PreparedAttempt.state` 的六态状态机是理解主循环的钥匙，先画出来再读代码。
- 易混淆点一：**"外部占用门禁"（分配前，util/mem 阈值，决定能不能领卡）与"陌生进程干扰"（运行中，per-PID SM 采样，决定要不要重试）是两套独立机制**，前者在 GpuPool，后者在主循环 + NVML 采样。
- 易混淆点二：干扰重试是 attempt+1 回 READY，**不重新 spawn 子进程**——编译产物与缓存都保留，只有 GPU 阶段重来。
- 易混淆点三：`_foreign_mem_pct` 只统计进程树之外的显存（396-404 行注释）：被"干扰停车"的自家子进程在卡上留有残留 CUDA context，算成外部占用会永久饿死它正等的那张卡。
- `run_scheduled_jobs` 的 finally 块（2112-2136）是全量资源清理的范本：停线程、关 socket、对每种状态残留的子进程给出正确的终止路径（RESULT 等 10s、PREPARING/READY 发 CANCEL、其余 killpg），值得逐行读。

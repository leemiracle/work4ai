# 深解 utils/：compile_and_run.py + kernel_io.py + print_utils.py

> 图谱定位：**编译评测与工具层（eval-utils）**——"CUDA kernel 的编译执行与子进程隔离评测、kernel 文件 IO 与打印工具，是性能真值采集的底层基础设施"。三文件同层，被主编排 `main_memory_latest.py` 直接消费。

## ① 角色定位

这三个文件构成 KernelMem 进化循环的**评测真值管线**：`kernel_io.py` 是 LLM 输出与文件系统之间的闸门（提取代码/JSON、落盘、溯源）；`compile_and_run.py` 是地面真值评测器（编译→对齐→正确性→计时，809 行，全模块最重）；`print_utils.py` 是 8 行的 ANSI 彩色打印极简件。没有它们，"LLM 生成的 kernel 是否能跑、是否更快"就没有裁判。

## ② 内部结构（compile_and_run.py）

**load_inline 编译捕获**。`_capture_import(path, timeout=600)` 用 `importlib.util.spec_from_file_location` 动态 import 候选/参考文件（模块名 = 路径 md5，注册进 `sys.modules`）——真正的 nvcc 编译发生在 `exec_module` 执行模块顶层代码时（候选文件内部调用 `load_inline`/cpp_extension）。它同时重定向两层输出：Python 层 stdout/stderr → StringIO，OS 层 `os.dup2` 把 FD 1/2 指向临时文件（捕获 ninja/nvcc 子进程字节流，这是 StringIO 抓不到的），最后合并成 full_log，`finally` 中无条件恢复原 FD 与信号处理器。任何构建失败抛 `CompilationError(full_log)`——**第一个参数就是完整日志**，直接喂修复 prompt，这是"编译错误可修复"闭环的根基。

**超时处理**。`signal.SIGALRM` + `_timeout_handler`（Unix-only）：编译超 600 秒抛 `CompilationTimeoutError`（CompilationError 子类，触发主编排的专用超时修复路径）。上层 `_bench_and_score` 再加一道 spawn 子进程 `p.join(1200)`（20 分钟）硬杀。双保险。

**计时协议**。`_bench(model, inp, dev, warm, rep)`：先 warmup 次（默认 5）空跑热身；再 repeat 次（默认 20）逐次 `s.record() → forward → e.record() → e.synchronize()`，取 `elapsed_time` 毫秒。CUDA Event 计时，CPU 回退用 `datetime.now()`。逐次同步排除 launch 异步干扰。

**tol 数值比对**。统一取首个输出 Tensor、`.contiguous()`、dtype/device 对齐后：`torch.allclose(ref, test, atol=tol, rtol=tol)`，tol 默认 1e-4；整型输出（argmax 类）改用 `torch.equal` 完全相等。失配时 `_build_mismatch_debug_msg` 输出输入/权重 shape、卷积属性、max_err 坐标与两侧值。超大输出（>40GB 估算）移 CPU 比对或跳过精度检查。

**speedup 计算**。本模块只产 `ref_latency_ms`/`test_latency_ms`（各含 avg/min/max/all）；**speedup 由调用方算**：`main_memory_latest.py:414` = `ref_avg / max(1e-9, test_avg)`，写入 `metrics["score"]`。

另有隐形关键件：`_seed_everything(100)` 三处播种（生成输入前、两个模型构造前各一次）+ 确定性后端（`CUBLAS_WORKSPACE_CONFIG=:4096:8`、cudnn deterministic、`use_deterministic_algorithms(warn_only=True)`——无确定性实现的算子只告警不报错）；三级参数对齐 `try_align_params`（导出名对 → 实例类名对 → 任务自定义 `map_ref_to_test_params`/`align_params` → 通用对齐），通用层先同名同形拷贝、再唯一形状匹配、最后走 `_try_map_shape_and_copy_` 的形状映射表（depthwise 2D/3D 压扩维、PW/Linear 四维二维互转、Conv3D 首两维交换），并把命中统计写进 `align_stats` 随结果返回——保证 ref/test 权重一致，不然 speedup 无意义。

## ③ 外部连接

图谱边全入向：`main_memory_latest.py --imports-->` 两文件；`query_server.py --imports--> print_utils`；`README.md --documents--> compile_and_run`。函数级：`_llm_to_kernel` 调 `extract_code_block`/`save_kernel_code`；`_extract_kernel_from_optimization_reply` 调前者；`_bench_worker_entry` 调 `compare_and_bench`（spawn 子进程内，Pipe 回传结果）；`_run_single_task` 调 `extract_cuda_kernel_names`（NCU 剖析过滤）与 `extract_json`（judger 输出解析）。compile_and_run 内部还 lazy import `psutil` 与 `print_warning` 做大张量内存预警。

## ④ 数据流（一次评测的完整旅程）

```
LLM 原始回复
  → kernel_io.extract_code_block（首代码围栏，容忍未闭合 fence；
     无 fence 则落盘 llm_output_error_*.txt 并 raise）
  → kernel_io.save_kernel_code → kernels/kernel_YYYYmmdd_HHMMSS.py
  → 主编排 spawn 子进程 _bench_worker_entry
  → compile_and_run.compare_and_bench(ref_py, test_py)：
     _capture_import ×2（编译+全日志）→ get_init_inputs/get_inputs（仅取自 ref）
     → 播种×3 → 双模型构造 → try_align_params（权重迁移）
     → _run_once 正确性（tol 比对）→ _bench ×2 计时（warmup/repeat）
  → result dict（timestamp/tolerance/max_abs_err/ref+test_latency/seed/align_stats）
  → 调用方补 speedup/score/runnable/error → 指标 JSON 落盘 metrics_dir
  → 失败分支：CompilationError→修复 prompt；AccuracyError→精度修复；超时→专用路径
```

## ⑤ 设计决策：与 KernelBench 上游计时协议的异同

对照 DeepWiki KernelBench 2.5 timing-and-profiling（cuda_event 协议：warmup + **每次计时前清 L2 cache** + n_perf_trials）：

| 维度 | KernelBench cuda_event | KernelMem compile_and_run |
|---|---|---|
| 计时器 | CUDA Event | 同（elapsed_time）|
| warmup | 有 | 有（默认 5）|
| L2 清缓存 | **每 trial 写大 buffer 刷 L2** | **无** |
| 试验数 | n_perf_trials（~100）| repeat=20 |
| 同步粒度 | 循环后统一 sync | 逐 trial sync |

相同点：都用 CUDA Event、都热身。**关键差异是 L2 清缓存**：KernelMem 在暖 L2 下计时，工作集塞得进 L2 的 memory-bound kernel 会得到偏乐观延迟 → speedup 相对上游协议**系统性通胀**，跨论文对比数字时必须注意。其次 repeat=20 < 100，方差更大（只报 avg/min/max，无中位数/CI）；逐 trial sync 更接近 kernel 纯时间但每轮多付同步开销。这些是本项目评测数字的"协议标签"，写论文复现时须声明。

## ⑥ 新人提示

1. **文件头注释是遗迹**：模块 docstring 写 "compare_and_bench.py" 且宣称支持 `--cpu` flag——实际 CLI 无此参数，CPU 模式仅在无 CUDA 时自动回退。
2. `TORCH_DEVICE` 是**模块级常量**，import 时定死；GPU 热插拔/遮蔽（CUDA_VISIBLE_DEVICES）后不刷新。
3. `Dict/Any` 未在顶部 import 却出现在签名——靠 `from __future__ import annotations` 的惰性求值兜住，删掉首行会炸。
4. SIGALRM 只在 Unix 生效；且只打断 Python 层，深陷 nvcc 子进程时靠上层 20 分钟 join 兜底。
5. `extract_code_block` 只取**第一个**围栏——prompt 设计必须让代码块先于解释文字出现；优化分支另走 `_extract_kernel_from_optimization_reply` 定界符感知版。
6. `_run_once` 图谱摘要称"比对并抛 AccuracyError"，实际只跑一次返回输出；比对在 `compare_and_bench` 主体。**以源码为准**。
7. `save_kernel_code` 文件名时间戳只有秒级精度，同秒两次保存会**互相覆盖**——并行评测批次要自备子目录隔离。
8. 因无 L2 清缓存（见⑤），本系统报的 speedup 与 KernelBench 论文基线**不可直接对比**，复现实验需自行补 flush buffer 或声明协议差异。
9. 调试单 kernel 直接 CLI：`python utils/compile_and_run.py ref.py cand.py --warmup 5 --repeat 20 --dump out.json`。

# nvbench Onboarding（GPU 微基准框架）

> 仓：`/usr-data/data2/repos/agent-repos/NVIDIA/nvbench` @410dcdd2（348 文件）
> 图谱：`.understand-anything/knowledge-graph.json`（649 节点/979 边/14 层/16 步 tour，fingerprints 348@410dcdd2）
> 全部行号锚已对源码核实；本文件是「新人第一小时」读图与读码的合并导览。

## 1. 项目定位：把 GPU 微基准做成框架

nvbench 是 NVIDIA 开源的 **GPU 微基准框架**：你写一个基准函数（`void bench_x(nvbench::state&)`），框架替你完成参数空间展开、kernel 启动、计时、收敛判停、统计汇总与三种格式输出。它不是压测工具也不是 profiler——它是"单 kernel 级性能测量"的标准化骨架，与 Google Benchmark 同型但面向 CUDA（README.md:1-189；docs/benchmarks.md 全 515 行是权威使用手册）。

三个形态一体：
- **C++ 头文件库**：用户只 include 伞头 `nvbench/nvbench.cuh`（48 行，聚合全部公共 API，fanIn=19），加一行 `NVBENCH_BENCH(my_func)`（`nvbench/create.cuh:40`，带类型轴版本 `NVBENCH_BENCH_TYPES` 在 `nvbench/create.cuh:47`）即注册完成；
- **CLI 可执行**：`nvbench/main.cu`（24 行）只调 `NVBENCH_MAIN` 宏（`nvbench/main.cuh:104`），真正装配在宏体系（`nvbench/main.cuh:114` 的 NVBENCH_MAIN_BODY）与 `nvbench::detail::main_*` 内联函数族（`nvbench/main.cuh:191-261`：main_initialize :194、main_run_benchmarks 等）里——**注意仓内不存在 `main_impl` 函数**（全仓 grep 零命中，图谱摘要此点为误，详见 README 勘误#1）；
- **Python 包 cuda-bench**：`python/cuda/bench/` 提供 `@cuda.bench` 装饰器 API，经 pybind11 桥回同一 C++ 引擎（`python/src/py_nvbench.cpp`，1577 行，PYBIND11_MODULE 在 `python/src/py_nvbench.cpp:1498`）。

依赖面极小：fmt（格式化）、nlohmann/json（结果输出）、可选 CUPTI/NVPW/NVML（`cmake/NVBenchDependencies.cmake` 全 94 行的装配策略）。构建支持 CUDA 12.0-12.9 × gcc7-14/llvm14-20 矩阵（`ci/matrix.yaml`，84 行），`.devcontainer/` 由 `.devcontainer/make_devcontainers.sh`（138 行）按矩阵批量生成 40+ 容器定义。

## 2. 分层架构速览（图谱 14 层）

图谱把 348 文件归 14 层，读码顺序即层的依赖顺序：

| 层 | 内容 | 代表文件 |
|---|---|---|
| L04 类型系统与轴 | type_list/type_strings/六类轴 | `nvbench/type_list.cuh`(157 行) |
| L05 基准对象与状态 | benchmark/manager/state/named_values | `nvbench/state.cuh`(397 行) |
| L06 测量器家族 | hot/cold/cpu_only/cupti | `nvbench/detail/measure_cold.cu`(573 行) |
| L07 统计与收敛判据 | stdrel/entropy/sample_count | `nvbench/detail/statistics.cuh`(533 行) |
| L08 CUPTI/NVPW 后端 | 双剖析后端 | `nvbench/cupti_profiler_nvpw.cxx`(761 行) |
| L09 设备与运行时 | device/stream/timer/blocking | `nvbench/device_info.cu`(177 行) |
| L10 输出打印 | printer 三连+multiplex | `nvbench/json_printer.cu`(682 行) |
| L11 CLI 入口 | option_parser 巨石 | `nvbench/option_parser.cu`(1311 行) |
| L12 内部执行支撑 | generator/exec/l2flush/timestamps | `nvbench/detail/state_generator.cxx` |
| L13 Python 工具链 | cuda.bench+scripts | `python/scripts/nvbench_compare_robust.py`(3591 行) |
| L14 测试框架 | 37 个 .cu 测试 | `testing/option_parser.cu`(1905 行) |

（L01-L03 是构建/CI/文档示例层，按需查阅。）数据流主干：**用户注册 → benchmark_manager 登记 → state_generator 笛卡尔展开参数空间 → runner 逐 state 驱动 → 测量器采样 → 判据判停 → statistics 汇总 → printer 三格式输出**。

## 3. 轴与类型系统：参数空间的声明式定义

基准的"变量"全部走轴体系（`nvbench/axis_base.cuh` 抽象基类：轴名/输入数/克隆接口，是 int64/type/string 三族共同祖先）。四种值轴 + 一种类型轴：

- `int64_axis`（`nvbench/int64_axis.cxx`：set_inputs 解析输入串）、`float64_axis`（`nvbench/float64_axis.cxx`）、`string_axis`（`nvbench/string_axis.cxx`）——值轴就是离散取值表，`nvbench/range.cuh`（62 行）提供区间便捷生成（示例 `examples/axes.cu:50` 用 `nvbench::range(0., 1e-3, 1e-4)`）；
- `type_axis`（`nvbench/type_axis.cuh`）是框架最有特色的一维：以类型列表为取值，同一基准对 `T=float/double/...` 各实例化一份模板（`nvbench/type_axis.cxx:36` set_active_inputs 勾选启用类型，`nvbench/type_axis.cxx:59` get_type_index 由字符串反查索引）。类型元编程底座在 `nvbench/type_list.cuh`（157 行，`NVBENCH_TYPE_AXES` 宏）与 `nvbench/type_strings.cuh` + `nvbench/type_strings.cxx`（demangle 类型转可读名）；
- `nvbench/enum_type_list.cuh`（106 行）把 enum class 包装成可入 type_axis 的类型并自动字符串化（示例 `examples/enums.cu`，207 行）。

全部轴元数据装进 `nvbench/axes_metadata.cuh` 容器，被 benchmark 与 state_generator 两端共享（fanIn=8/fanOut=8）。`examples/axes.cu`（212 行）五段式演示单轴/网格 sweep/类型 sweep/类型转换 sweep/组合轴：`NVBENCH_BENCH(simple)`（`examples/axes.cu:36`）、float64 轴（`examples/axes.cu:48`）、类型 sweep（`examples/axes.cu:122`）到双类型轴组合 `NVBENCH_BENCH_TYPES(copy_type_and_block_size_sweep, ...)`（`examples/axes.cu:211`）。

## 4. 基准对象与执行模型

- **注册与生命周期**：`nvbench/benchmark_base.cuh`（377 行）是全部基准的根类型——聚合 axes/stopping_criterion/描述元数据，纯虚 `do_` 钩子密集；模板子类 `nvbench/benchmark.cuh` 把用户函数桥接进来；`nvbench/benchmark_manager.cxx:34` 单例 `get()`，`nvbench/benchmark_manager.cxx:40` `initialize()` 驱动全部注册基准，`nvbench/benchmark_manager.cxx:58` `clone_benchmarks()` 为多设备运行复制基准。
- **state 是用户一等接口**（`nvbench/state.cuh`，397 行，fanIn=18）：读轴值 `get_axis_values()`（`nvbench/state.cuh:270`）、取执行流 `get_cuda_stream()`（`nvbench/state.cuh:83`，:95 set_cuda_stream）、标注吞吐 `add_element_count`（`nvbench/state.cuh:123`）与 `add_global_memory_reads/writes`（`nvbench/state.cuh:129-140`，带宽自动换算的字节来源）、跳过 `skip(reason)`（`nvbench/state.cuh:150`）、启动 kernel `state.exec(ExecTags{}, launcher)`（`nvbench/state.cuh:328`，`nvbench/state.cuh:331` 是无标签捷径）。`examples/throughput.cu:50` 与 `examples/throughput.cu:51` 是吞吐标注的最小范例。
- **执行语义用类型标签**：`nvbench/exec_tag.cuh`（160 行）`enum class exec_flag`（`nvbench/exec_tag.cuh:40`）+ 空基类 `tag_base`（`nvbench/exec_tag.cuh:70`）+ `tag` 模板（`nvbench/exec_tag.cuh:81`）——`exec_tag::cold/hot/sync/cpu_only/no_block` 等以编译期零开销方式标注 kernel 同步语义，`nvbench/detail/state_exec.cuh:55` 的 `state::exec` 按 tags 分派到 cold（`nvbench/detail/state_exec.cuh:77`）、cold|hot（:81）、cpu_only（:86）与组合（:92/:96）路径。配套：`nvbench/launch.cuh`（72 行）统一 grid/dim 推断的启动包装、`nvbench/callable.cuh` 编译期提取函数名、`nvbench/flags.cuh`（53 行）est_runtime/favor_determinism 提示位。
- **驱动引擎**：`nvbench/runner.cuh:43` 定义 `stop_runner_loop` 异常（异常作为控制流：提前终止主循环），`nvbench/runner.cxx:38` `handle_sampling_exception` 把"用户 skip"与"致命异常"分流（:42 判 `is_skipped` 只打通知，`nvbench/runner.cxx:84` print_skip_notification 输出跳过原因）；`nvbench/detail/state_generator.cxx:102` `build_axis_configs` 展开 type 轴与非 type 轴（`nvbench/detail/state_generator.cxx:131` 特意将 type 轴反序排列以对齐 cartesian_product 展开序），`nvbench/detail/state_generator.cxx:213` `build_states`、`nvbench/detail/state_generator.cxx:231` `add_states_for_device` 逐设备生成 state 向量。

## 5. 测量器家族与收敛判据（框架的心脏）

**四种测量策略**（`nvbench/detail/` 下，全部继承同一 base、由 state_exec 按执行标签选择）：

- `measure_hot`（`nvbench/detail/measure_hot.cu`，250 行）：批内热循环连续采样不清理状态，`nvbench/detail/measure_hot.cu:43` `predict_batch_size`、`nvbench/detail/measure_hot.cu:104` `predict_cuda_batch_size`、`nvbench/detail/measure_hot.cu:131` `grow_batch_size` 实现"按目标批时长预测批大小再倍增"的自适应批次；
- `measure_cold`（`nvbench/detail/measure_cold.cu`，573 行）：逐次冷启动——每轮 flush L2、逐 kernel launch 计时，`nvbench/detail/measure_cold.cu:50-54` 构造期从 exec_state 读 warmup/超时配置，`nvbench/detail/measure_cold.cu:175-202` `is_finished` 判停（min_samples + 判据 + 超时三重），`nvbench/detail/measure_cold.cu:223` `generate_summaries` 产出 `nv/cold/sample_size` 等摘要。L2 flush 的实现非常直白：`nvbench/detail/l2flush.cuh:42` 构造时 `cudaMalloc` 一块与 L2 等大的缓冲，`nvbench/detail/l2flush.cuh:68` `flush()` 用 `cudaMemsetAsync` 整块写零把 L2 冲干净；冷测量的共享计时核心在 `nvbench/detail/measure_cold_launch_timer_core.cuh`（183 行，config/core/cleanup_guard 三件套，被 cold 与 cupti 两测量器共用——NOTES batch-19 甄别）；
- `measure_cpu_only`（`nvbench/detail/measure_cpu_only.cxx`，306 行）：纯主机路径，不走 CUDA 事件（`examples/cpu_only.cu` 演示）；
- `measure_cupti`（`nvbench/detail/measure_cupti.cu`，273 行）：把硬件计数器会话嵌入冷测量循环（`nvbench/detail/measure_cupti.cu:182` 处理 profiler 构造失败的报错路径），只在 `NVBENCH_HAS_CUPTI` 定义时编译（`cmake/NVBenchCUPTI.cmake`，127 行，负责探测与宏开关）。

**收敛判据**（何时停止采样）由 `nvbench/stopping_criterion.cuh` 抽象 + `nvbench/criterion_manager.cxx:34-36` 注册三实现（`:34` stdrel、`:35` entropy、`:36` **注册名是 "sample-count" 带连字符**，`nvbench/criterion_manager.cxx:74` 重名注册抛错），CLI `--criterion` 按名切换，自定义判据经 criterion_manager 登记（`examples/custom_criterion.cu`，77 行）：

- `stdrel`（`nvbench/detail/stdrel_criterion.cxx:72` `do_is_finished`）：相对标准误收敛，**双门限**——噪声 < max-noise 即停；同时 `nvbench/detail/stdrel_criterion.cxx:103-115` 检查"噪声稳定窗口"（窗口 64/检查间隔 16）：噪声若长期稳定在阈值之上（天生噪声大的基准）也放行结束，防止永不收敛；
- `entropy`（`nvbench/detail/entropy_criterion.cxx`）：样本频率直方图估熵，`nvbench/detail/entropy_criterion.cxx:61` `compute_entropy` 用 `log2(n) - Σc·log c / n`，`nvbench/detail/entropy_criterion.cxx:30` 注册的默认参数名是 **`max-angle 0.048 / min-r2 0.36`**（不是直观的"熵阈值"，新人易懵）；
- `sample-count`（`nvbench/detail/sample_count_criterion.cxx`）：数满即停的最简判据。

统计底座：`nvbench/detail/statistics.cuh`（533 行全模板）流式均值方差/分位数/摘要函数族；`nvbench/detail/online_linear_regression.cuh`（199 行）流式拟合 + 置信区间；`nvbench/detail/transform_reduce.cuh` 一遍式归约。样本存储在 `nvbench/detail/ring_buffer.cuh`（247 行）。测量环境控制三件套：`gpu_frequency`（NVML 查时钟/降频）、`timestamps_kernel`（设备侧时戳对，`nvbench/detail/timestamps_kernel.cu` 81 行）、`blocking_kernel`（自旋维持独占负载，`nvbench/blocking_kernel.cu` 134 行）。

## 6. CUPTI/NVPW 双剖析后端

`nvbench/cupti_profiler.cuh`（33 行）是后端选择头：编译期按宏把实现指到两套完全同构的实现——`cupti_profiler_host.cxx`（709 行，CUPTI Profiler API，pimpl 惯例 `host_impl`+RAII 守护类，availability/config/counter-data 三大镜像）与 `cupti_profiler_nvpw.cxx`（761 行，Nsight Perfworks SDK，`metric_evaluator` 解析指标依赖树 + user-loop 重放模式）。这是"同一指标面在两代驱动栈上的适配"的干净样本：measure_cupti 只依赖统一接口，后端差异全部收敛在两文件内。

## 7. 输出打印系统与 CLI

**打印三连**（全部派生自 `nvbench/printer_base.cuh` 266 行骨架，15 个 `do_` 渲染钩子）：`markdown_printer.cu`（638 行，控制台人读默认输出，分级表格+进度行+颜色）、`csv_printer.cu`（184 行，三级表供脚本消费）、`json_printer.cu`（682 行，结果文件生产者）。`nvbench/printer_multiplex.cxx:33-141` 把 15 个钩子逐一扇出到多个 printer（md+json 同时落盘）。表格渲染原语共享：`nvbench/internal/table_builder.cuh`（95 行）+ `markdown_table.cuh`（163 行，列宽自适应）。

json_printer 的样本旁挂机制值得注意（`nvbench/json_printer.cu:347` `do_process_bulk_data_float64`）：开启 `m_enable_binary_output`（`nvbench/json_printer.cuh:86`，默认 false）后，sample_times/sample_freqs 不进 JSON 正文，而是写 **小端 float32 二进制 sidecar 文件**（`-bin` 后缀 metadata 在 `nvbench/json_printer.cu:361`、`-freqs-bin` 在 `nvbench/json_printer.cu:373`）——**不是 base64 内嵌**（全仓 grep "base64" 零命中，NOTES batch-20 的"base64/二进制"表述半误，README 勘误#2）。

**CLI 解析巨石**：`nvbench/option_parser.cu`（1311 行，全仓最大源文件）解析 20+ flag——`--axes`/`--axis`（`nvbench/option_parser.cu:642` 起，含轴过滤 DSL 与 `--help-axes` `nvbench/option_parser.cu:537`）、设备/判据/输出格式等；`nvbench/option_parser.cu:439`/`:457` 两级 parse 入口、`nvbench/option_parser.cu:369` 轴值非法时抛 "Invalid axis value spec"、`nvbench/option_parser.cu:1022` 把基准专属 `--axis` 参数透传给全局 benchmark args、`nvbench/option_parser.cu:1060` 汇聚轴选项错误。配套文档 `docs/cli_help.md`（233 行）与 `docs/cli_help_axis.md`（69 行）。独立控制驱动 `exec/nvbench-ctl.cu`（48 行）是精简入口壳。main 的可定制点全部以宏暴露（`nvbench/main.cuh:49-177` 的 NVBENCH_MAIN_INITIALIZE_CUSTOM_PRE 等 8 个钩子宏），testing/ 里 custom_main_* 四个测试就是这些宏的用例。

## 8. Python 工具链与测试体系

**cuda.bench 包**（wheel 名 cuda-bench，`python/pyproject.toml`）：`python/cuda/bench/__init__.py:97` 用 `importlib.import_module` 延迟加载编译好的 C++ 扩展、`python/cuda/bench/__init__.py:110` 模块级 `__getattr__` 惰性解析符号——**避免导入期触发 CUDA 初始化**（NOTES batch-2 甄别）。装饰器层 `python/cuda/bench/_decorators.py:33` `_append_benchmark_action` 把 @axis/@opt_* 修饰挂成延迟动作（`python/cuda/bench/_decorators.py:39` 显式校验装饰器顺序，axis 必须在 option 之上；`python/cuda/bench/_decorators.py:84` make_register）。CLI 转发入口 `python/cuda/bench/nvbench.py:42` `_build_parser`、`python/cuda/bench/nvbench.py:86` `main`。C 扩展 `python/src/py_nvbench.cpp` 绑定六大类：CudaStream `python/src/py_nvbench.cpp:430`、Launch :477、Timer :509、Benchmark `python/src/py_nvbench.cpp:566`（add_int64_axis `python/src/py_nvbench.cpp:582` / set_stopping_criterion :762 / set_min_samples :824 等约 30 个方法）、State `python/src/py_nvbench.cpp:942`（占 :942-1493，约 550 行，即 NOTES 所称"State 624 行绑定"的主体）、PYBIND11_MODULE :1498。结果解析 `python/cuda/bench/results/_benchmark_result.py`（511 行）：`python/cuda/bench/results/_benchmark_result.py:186` parse_binary_meta 读 sidecar 元数据，:204/:208 识别 `nv/json/bin`/`nv/json/freqs-bin` 标签，`python/cuda/bench/results/_benchmark_result.py:229` `parse_float32_binary` 按 "<f4" 小端 float32 切样本（:250 注释明示对齐 np.fromfile "<f4"）。

**脚本族**：`python/scripts/nvbench_compare_robust.py`（3591 行 167 函数的巨石 CLI）做两份结果 JSON 的稳健对比——判据链层层升级取证：`python/scripts/nvbench_compare_robust.py:1426` `make_decision` 起步，`python/scripts/nvbench_compare_robust.py:1434` `compare_intervals_for_clear_gap` 判显著快/慢，再经 `python/scripts/nvbench_compare_robust.py:1737` `confirm_clear_gap_with_clock_rate`（时钟速率确认）、:1770 `confirm_clear_gap_with_bulk_cycles`、:1865 `confirm_same_with_clock_rate`、:1983 `confirm_bulk_time_same_without_cycles` 四个 confirm_* 逐级确认（方法论见 `docs/nvbench_compare_robust.md`，742 行）。`python/scripts/nvbench_json/reader.py`+`version.py` 是结果文件读取门面（版本校验）；`python/scripts/nvbench_tooling_deps.py` 懒加载 matplotlib/tabulate/jsondiff 可选依赖。

**测试**：testing/ 共 37 个 .cu（44 文件）——**自研断言体系非 gtest**（`testing/test_asserts.cuh:26` ASSERT、`testing/test_asserts.cuh:40` ASSERT_MSG、`testing/test_asserts.cuh:58` ASSERT_THROWS_ANY；每个测试自带 `int main()`，如 `testing/state.cu:131`）。`testing/CMakeLists.txt:1-35` 的 test_srcs 清单注册 35 个测试目标，另有 `testing/device/noisy_bench.cu`（噪声负载）与 `testing/cmake/test_export/test_bench.cu`（下游消费冒烟）。三大件：`testing/option_parser.cu`（1905 行全仓最大测试）、`testing/state_generator.cu`（810 行黄金断言）、`testing/statistics.cu`（707 行）。

**上手路线**：① 读 `docs/benchmarks.md` + 跑 `examples/axes.cu`/`throughput.cu`；② 跟 tour 步骤 T05→T07 打通 state→测量器主线；③ 需要硬件计数器再看 L08 双后端；④ 结果分析直接用 compare_robust，别手搓均值比较。

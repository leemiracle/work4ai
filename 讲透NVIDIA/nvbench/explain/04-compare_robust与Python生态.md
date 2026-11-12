# 04 Python 生态：cuda.bench 包与 compare_robust 稳健比较

## 角色定位

Python 线是 nvbench 的"第二引擎 + 结果分析器"。第二引擎：`cuda.bench` 包（wheel 名 cuda-bench）提供 `@cuda.bench` 装饰器 API，让 Python 基准跑在同一 C++ 测量引擎上——桥是 `python/src/py_nvbench.cpp`（1577 行 pybind11 绑定）。结果分析器：`python/scripts/` 工具族，旗舰是稳健比较 `python/scripts/nvbench_compare_robust.py`（3591 行 167 函数）。两条线以结果文件格式（json_printer 产物 + sidecar 样本）解耦。

## 内部结构

**cuda.bench 包**：入口 `python/cuda/bench/__init__.py:97` 延迟加载 C++ 扩展、`python/cuda/bench/__init__.py:110` 模块级 `__getattr__` 惰性解析——避免 import 期触发 CUDA 初始化。装饰器层 `python/cuda/bench/_decorators.py:33` `_append_benchmark_action` 把 @axis/@opt_* 挂成延迟动作、注册时统一应用，`python/cuda/bench/_decorators.py:39` 校验装饰器顺序（axis 必须在 option 之上），`python/cuda/bench/_decorators.py:84` make_register。绑定六大类：CudaStream（`python/src/py_nvbench.cpp:430`）、Launch（`:477`）、Timer（`:509`）、Benchmark（`:566`，add_int64_axis `python/src/py_nvbench.cpp:582`/set_stopping_criterion `:762`/set_min_samples `:824` 约 30 方法）、State（`python/src/py_nvbench.cpp:942`，占 :942-1493，即 NOTES"State 624 行绑定"主体）、PYBIND11_MODULE（`:1498`）。

**结果解析**：`python/cuda/bench/results/_benchmark_result.py`（511 行）——`python/cuda/bench/results/_benchmark_result.py:186` parse_binary_meta、`:204`/`:208` 识别 `nv/json/bin`/`nv/json/freqs-bin`、`:229` `parse_float32_binary` 按 "<f4" 切样本；`python/scripts/nvbench_json/reader.py` 是版本校验门面。

**compare_robust 判据链**：`python/scripts/nvbench_compare_robust.py:1426` `make_decision` 构造 TimingDecision → `:1434` `compare_intervals_for_clear_gap` 用 bootstrap 置信区间判显著快/慢 → 四个 confirm_* 逐级加固：`python/scripts/nvbench_compare_robust.py:1737` `confirm_clear_gap_with_clock_rate`（确认非降频假象）、`:1770` `confirm_clear_gap_with_bulk_cycles`、`:1865` `confirm_same_with_clock_rate`、`:1983` `confirm_bulk_time_same_without_cycles`。方法论文档 `docs/nvbench_compare_robust.md`（742 行）。

## 外部连接

构建：scikit-build-core（`python/CMakeLists.txt` 60 行）；可选依赖由 `python/scripts/nvbench_tooling_deps.py` 懒加载。CI：`.github/workflows/build-and-test-python-wheels.yml`（178 行）在自托管 L4 GPU runner 构建 wheel 并实机冒烟（NOTES batch-7）。测试：`python/test/test_benchmark_result.py`（750 行 31 用例）、`python/test/test_cuda_bench.py`（459 行）。示例：`python/examples/benchmark_result_autotune.py`（360 行按中位数择优 tile 再重跑）。

## 数据流

跑基准：装饰器收集轴/选项 → C++ Benchmark 对象（py_nvbench 绑定）→ 同一套 runner/测量器 → json_printer 落盘。分析：reader 校验版本 → BenchmarkResult/State 树 → compare_robust 读两份 JSON → 逐 state 对齐（基准名+轴值）→ bootstrap 得置信区间 → make_decision 出 `SAME`/`FAST`/`SLOW`/`AMBG`（或 `????`，`docs/nvbench_compare_robust.md:2`）→ confirm_* 复核 → 报告；`nvbench-compare-legacy` 保留旧均值/标准差规则（同文档 :10-15）。

## 设计决策

1. **Python API 复用 C++ 引擎而非重写**：测量语义跨语言一致、结果可比；代价是绑定面大（Benchmark 约 30 方法手写）。
2. **延迟导入贯穿全包**：`__getattr__` 惰性解析 + 可选依赖统一懒加载——`import cuda.bench` 永不拉起 CUDA、永不要求 matplotlib。
3. **compare_robust 单文件巨石**：判据链是整体决策流，拆文件遮蔽"层层升级取证"；可读性靠命名自律。
4. **比较判据三重确认**（bootstrap 区间+样本覆盖率+时钟确认）：性能对比最大的坑是把降频噪声当回归——confirm_clear_gap_with_clock_rate 先查时钟再下结论。
5. **装饰器顺序校验放注册期**：错误在完整上下文里抛，好定位。

## 新人提示

- Python 基准先抄 `python/examples/axes.py`（198 行，与 `python/test/stubs.py` 镜像同构）；CuTe DSL 看 cute_dsl_sgemm.py。
- `nvbench-compare-robust` 的 `AMBG` 是常态输出（样本不足/噪声大），别肉眼比均值。
- 绑定层文档就是 docstring：`help(cuda.bench.Benchmark)` 最准。
- 跨版本比较先看处理器版本字段（`python/scripts/nvbench_json/version.py` 硬校验）。

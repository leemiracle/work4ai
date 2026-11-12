# KernelBlaster 数据集加载层深解：`data/dataset.py` + `data/kernelbench.py` + `data/kernelbench_cuda.py`

> 图谱定位：`layer:data-knowledge`（数据与优化知识库层，7 节点）。数据流：`scripts/run_RL.py:async_main` → `data/__init__.py:get_dataset` → 两个 Dataset 子类 → RL 优化工作流。

## ① 角色定位：KernelBench → KernelBench-CUDA 的"格式转接层"

这一层不做任何计算，它回答一个问题：**"本次优化循环的输入题从哪来、长什么样"**。

上游 KernelBench（ScalingIntelligence）的题目是纯 Python 世界：每个 `problem.py` 定义 `get_inputs()`/`get_init_inputs()` 和 `Model(nn.Module)`（forward 内用标准 PyTorch 算子），由 harness 动态 import、用 `torch.compile` 做 baseline、跑 extension 编译评 speedup。而 KernelBlaster 的主战场是**原生 CUDA 源文件**：每题是一对 `init.cu`（待优化的起始 kernel）+ `driver.cpp`（libtorch C++ 验证器）。数据加载层就是这两种题目格式的统一索引与过滤入口——它把磁盘上的题目目录/文件扫描成内存里的 `dict` 条目列表，供 RL 循环逐题消费。

从 problem.py 到 init.cu+driver.cpp 的转译**不是本仓做的**（详见⑤），这层只负责"装载已转译的产物 + 保留一条通往 Python 原版的通道"。

## ② 内部结构：三个文件的分工

- **`dataset.py` — 基类 `Dataset`（77 行）**：极简模板。持有 `self.data: list[dict]`，提供序列协议（`__len__/__getitem__/__iter__`）、`get_iter(split)` 惰性迭代器，以及固定种子（`SEED=4589`）的 train/test 50/50 洗牌切分。子类只需在 `__init__` 里填 `self.data`。注意：两个 KernelBench 子类都 `assert split is None`——切分能力存在但从未使用。
- **`kernelbench.py` — `KernelBenchDataset`（上游 PyTorch 版）**：glob 扫描 `data/kernelbench/kernelbench/**/*.py`，从文件名解析题号与 level，构造规范化 id（`level{N}/{num:03d}_name`），支持 level/problem_numbers/start/end 多级过滤。独门操作是**精度注入**：在 `reference_code` 的 `class Model` 前插入 `torch.set_default_dtype(...)`（fp32/fp16/bf16），即运行时打补丁而非改源文件。默认跳过 level3/level4（超出当前 agent 范围）。
- **`kernelbench_cuda.py` — `KernelBenchCUDADataset`（默认主数据集）**：索引 `data/kernelbench-cuda/level{1,2,3}/<problem_name>/` 目录，**要求 driver.cpp 与 init.cu 同时存在**才算完整条目（缺一即静默跳过），输出 `driver_cpp_fp`/`init_cuda_fp` 路径条目（附 `final_cuda_fp` 向后兼容别名），按 id 排序。

`data/__init__.py` 的工厂 `get_dataset(name, ...)` 用 match/case 分发：`"kernelbench"` 与 `"kernelbench-cuda"` 两个名字，支持 `problem_numbers="8-60"` 混合区间语法，统一返回 `(dataset, iterator)` 二元组。调用方 `run_RL.py:async_main` 拿到迭代器后按条目逐题构造协程，并把 dataset 名（含 precision 后缀）拼进输出目录 `out/<dataset>/<experiment>/<model>`——也就是说，这层同时决定了**产物落盘的命名空间**。

## ③ 数据集解剖：184 对 cu+cpp

| Level | 题数 | 内容 |
|---|---|---|
| level1 | 94 | 单算子 kernel（GEMM 各变体/ReLU/Sigmoid 等激活/归约） |
| level2 | 81 | 多算子融合（Conv+ReLU+BiasAdd、Conv3d+Mish+Tanh 等） |
| level3 | 9 | 完整模型块（MLP/LeNet5/ResNetBasicBlock/SqueezeNet/EfficientNet/MinGPT attention 等） |

目录名带零填充题号（`001_Square_matrix_multiplication`），题号不连续（策展子集，level3 只挑了 9 个）。

每题目录固定两文件，以 level1/001 为例：
- **`init.cu`**：起始 kernel——注意它**不是朴素实现**，001 号已是面向 Ada/L40S 的 Tensor Core 版（mma.h、FP32 累累加、async copy），顶部注释即 kernel 签名 `launch_gpu_implementation(void* output, void* A, void* B, int64_t N)`。
- **`driver.cpp`**：验证 harness。以 libtorch 为真值：`torch::randn` 造 fp16 CUDA 输入 → `torch::matmul` 等 libtorch 算子算参考输出 → 调 `launch_gpu_implementation` 跑被测 kernel → `torch::allclose(rtol=1e-1, atol=1e-1)`（fp16 宽容差）→ stdout 打印 `passed`/`failed`。level3 的 driver 用 `torch::nn::Linear` 逐层复刻 Python 模型（注释明言 "equivalent to the Python nn.Sequential"）。level2 融合题（如 `001_Conv2D_ReLU_BiasAdd`）同理：libtorch 按算子序列逐步算参考值，被测 kernel 一次融合完成全部计算——验证的是"融合后数值等价"。三级 driver 的验证骨架完全一致（真值→launch→allclose→打印），差异只在参数个数与模型复杂度。

编译时的关键机关在 `src/kernelblaster/servers/compile.py:split_files_for_compilation`：driver.cpp 里的 `launch_gpu_implementation` **声明**被抽出写成 `cuda_model.cuh`，init.cu 改写为 `cuda_model.cu`，两者各 prepend `#include "cuda_model.cuh"`、剥掉 `inline`/`extern "C"`，经 cmake（`GPU_ARCH_VERSION`）分编译单元链接——这就是为什么盘上的 init.cu 从不直接 `#include` driver。

## ④ 外部连接

- **上游消费者**：`scripts/run_RL.py`（`get_dataset` → 逐题 `process_problem`）；`src/kernelblaster/graph/nodes/optimization_rl_ncu.py`（读 `init_cuda_fp`/`driver_cpp_fp` 启动 RL 优化，带 curated→run 目录降级查找：策展文件缺失时回退到上次 run 的工件）。
- **知识库联动**：`run_RL.py` 还会 `load_comprehensive_analysis_results` 扫历史分析 JSON，按 op_name/task_id 匹配当前题目，把历史优化经验注入 user message——数据条目的 `problem_name` 是这条跨问题经验检索链的主键。
- **下游依赖**：CompileServer（cu→exe）、GPUServer（跑 driver）、`data/kernelblaster/optimization_database.json`（持久优化知识库，同层节点，配 database.py 与 workflow.py 两个消费者）。
- **出仓路径**：主 README 规定实验产物写 `out/<dataset>/<experiment>/`，最优结果落 `final_rl_cuda_perf.cu`。

## ⑤ 与上游 KernelBench 的差异：转译是谁做的？

**结论：继承的，不是 KernelBlaster 自己做的。** 三条代码证据：
1. `data/kernelbench-cuda/README.md` 原文："These problems were **generated via a separate project** and are provided as input benchmarks"——即 NVIDIA 的 KernelBench-CUDA 项目产出，本仓 vendored 消费；
2. 全仓 grep 不到任何 transpile/converter 脚本，git 历史里该目录一次性整体进入；
3. driver.cpp 里残留自动翻译痕迹（"matching the provided Python code"、"equivalent to the Python nn.Sequential"），输入维度（N=2048）与上游 problem.py 的 `get_inputs` 一致。

本仓另保留 `KernelBenchDataset` 通道：主 README 指引用户 `git clone ScalingIntelligence/KernelBench.git` 到 data/ 下，供 `run_baselines.py`（eager）与 `run_baselines_compile.py`（torch.compile）直接走 problem.py 路线——**两代格式并存，RL 主线默认 `DATASET=kernelbench-cuda`**。本质差异：上游验证是"Python 真值 + speedup 对比"，本仓验证是"libtorch C++ 真值 + allclose 二值判定"，评估重心从正确性+加速比转向 NCU profiling 的 elapsed cycles。

## ⑥ 新人提示

1. **driver 恒返回 0**（"Always exit with return code 0"）——判定 pass/fail 要解析 stdout 的 `passed` 字符串，别信 exit code。
2. **init.cu 是强基线**：起点已是 Tensor Core 优化版，优化空间在"更强"而非"从朴素到快"。
3. `data/kernelbench/`（PyTorch 版）**不在仓里**，需按 README 自行 clone，否则 `KernelBenchDataset` 抛 FileNotFoundError。
4. 题号不连续：94/81/9 是上游的策展子集（level2 从 004 起跳、level3 只挑 9 个），用 `problem_numbers` 过滤时别假设连续区间都存在。
5. 精度是运行时补丁（fp16 默认 + allclose 1e-1 宽容差），复现实验时 precision 参数必须对齐。
6. `kernelbench.py` 的 level 断言只认 level1-3，但默认分支的过滤代码里出现了 level4——上游存在第四级，本仓显式排除，扩展时留意这条历史残留。

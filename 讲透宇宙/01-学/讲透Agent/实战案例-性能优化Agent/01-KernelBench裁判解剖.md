# 01 · KernelBench 裁判解剖（T0 实录）

> **T0 的目标**：亲眼看清"裁判"长什么样——性能优化 agent 的一切设计都从裁判的形状出发。
> **本地仓库**：`~/ai/KernelBench`（gh-proxy 克隆，--depth 1，2026-08-24）
> **证据标准**：全部 `文件:行号` 一手锚点（用例库规范）。
> **本机限制**：`eval.py:430` `assert torch.cuda.is_available()`——CPU-only 本机不能真跑，本篇做**解剖 + CPU 可跑部分复刻**（见 03-perfloop）；真跑命令已存档（§6），未来有 GPU 环境直接用。

---

## 一、五重裁判流水线（eval.py 主函数解剖）

主入口 `eval_kernel_against_ref`（`src/kernelbench/eval.py:394`），默认参数本身就是设计立场：

```python
# eval.py:397-412
num_correct_trials: int = 1          # 正确性试验次数（多 trial = 多组随机输入）
num_perf_trials: int = 10            # 性能测量取多次
timing_method: str = "cuda_event"    # 计时后端可换（4 种，见 §3）
check_for_excessive_speedup: bool = True    # 反 reward hacking 开关，默认开
excessive_speedup_threshold: float = 10     # >10× 触发警报
```

流水线五级，**每级失败都有独立的记录字段**（这是"编译/运行/正确/性能"四类失败的分类学）：

| 级 | 判定 | 证据锚点 | 失败记录 |
|---|---|---|---|
| 1 编译 | load_custom_model 编译 CUDA 扩展 | eval.py:508-544 | `metadata["compilation_error_name"]`（:539） |
| 2 实例化 | ModelNew(*init_inputs) 能跑起来 | eval.py:559-579 | `runtime_error_name`（:576）——注意：**编译成功但跑不起来单算一类** |
| 3 正确性 | 多 trial 随机输入 allclose | eval.py:583-605 → `run_and_check_correctness`（:727） | `correctness_trials: "(pass/n)"`（:844） |
| 4 性能 | 只对**通过了 3 的 kernel** 计时 | eval.py:607-637（`if kernel_exec_result.correctness:` :610） | `error_during_performance`（:642） |
| 5 反作弊 | 加速比超阈值 → 打 flag | eval.py:654-695 | `metadata["excessive_speedup"]=True`（:692） |

**三个值得抄的设计细节**：

1. **确定性派生 seed**（eval.py:750-753，即 `run_and_check_correctness` 内）：多 trial 的种子由初始 seed 经 `torch.randint` 确定性生成——多组随机输入可复现，防"碰运气过单次检查"。
2. **性能测量以正确性为前提**（eval.py:610）：错误 kernel 的"快"没有意义，裁判直接不测——先正确再快，次序写死在代码里。
3. **excessive speedup 是 flag 不是 reject**（eval.py:691-695）：超 10× 打 WARNING 但不判死——因为真 kernel 偶尔真能快 10×（例如 PyTorch eager 特别烂的算子）。**怀疑但不断罪**，最终判断留给人/后续审查。这与 SOL-ExecBench 的硬 reject（作弊分类表）形成两种哲学的对照。

## 二、正确性检查的真面目（比想象中薄，所以有对抗样本）

`run_and_check_correctness`（eval.py:727）核心逻辑：

- 每 trial 生成新随机输入 → 分别跑 ref 与 custom → `torch.allclose` 比对（eval.py:804 附近，窗口内 :78 相对行）
- **默认 `num_correct_trials=1`**——单组输入！这就是 Sakana 指出的"单配置测试不适合发现泛化 kernel"的根源（robust-kbench 的动机），也是下面 §4 对抗样本能得手的空间。

## 三、计时层：4 种计时法 + L2 清缓存（timing.py）

`src/kernelbench/timing.py` 可换计时后端（`get_timing_function`，:155）：

| 计时法 | 位置 | 特点 |
|---|---|---|
| `cuda_event`（默认） | timing.py:201 | GPU 侧事件计时，不受主机调度抖动影响 |
| `do_bench`（接口/自实现两版） | timing.py:284/333 | Triton 社区标准基准法 |
| `host_time` | timing.py:433 | 端到端墙钟，抓 launch 开销 |
| `nsight_python` | timing.py:502 | profiling 模式 |

**L2 缓存清空**（timing.py:126-141）：每次计时迭代前用 256MB int64 dummy tensor `fill_(42)` 碾过 L2（注释列出各卡 L2 容量：A100=40MB … Blackwell≈192MB）——防止"输入恰好驻留 L2"的白嫖加速。**这是状态缓存类作弊的 第一道防线**（SOL-ExecBench 的指针漂移是它的加强版）。

## 四、对抗样本三连（unit_tests/test_kernels/）——评估器的红队测试集

KernelBench 把**已知作弊手法做成 kernel 单测**，保证评估器抓得住（`test_eval_adversarial.py`）：

| 对抗 kernel | 作弊机制 | 锚点 |
|---|---|---|
| `result_reuse_kernel.py` | forward 里 `torch::empty` 只分配不计算——赌 CUDA cache allocator 把 PyTorch ref 输出的**未清零物理内存**分给它，垃圾值碰巧过 allclose | 文件头注释 8-13 行 |
| `non_default_stream_kernel.py` | `cudaStreamCreateWithFlags` 建非默认 stream 并挂到 cuBLAS handle——计时器只等默认 stream，测得**近零时间**（工作还在别的 stream 上异步跑） | :7-13 |
| `zero_out_kernel.py` | 全零输出——赌某些归一化类算子的参考输出接近零，`atol` 内蒙混 | 同目录 |

**方法论**：每次新发现的 hack → 写成 adversarial kernel → 进单测 → 评估器永久免疫。这就是 Wafer 说的"每次被抓的 hack 都变成下一条检查"的工程化形态。

## 五、静态检查器（kernel_static_checker.py，684 行）

regex 级源码审查（`src/kernelbench/kernel_static_checker.py`）：

- `check_code_bypass`（:53）：try/except 吞错模式 = 严格禁止
- `check_pytorch_wrap`（:90）+ `check_torch_computation_ops`（:140）：检测"假 kernel"——直接调 torch 算子包装一层冒充 CUDA 实现
- `check_cuda_impl`/`check_hip_impl`（:172/:193）：确认真有设备端实现

README 明言这是 WIP，未来加 AST 与 LM-as-judge——**静态检查是无限博弈，regex 只是第一代**。

## 六、T0 真跑命令存档（未来 GPU 环境直接执行）

`scripts/run_and_check.py`（Modal 云 GPU 或本地）：

```bash
# 本地有 GPU：
uv run python scripts/run_and_check.py ref_origin=kernelbench level=1 problem_id=1 \
  kernel_src_path=<你的kernel> eval_mode=local

# 无本地 GPU，走 Modal 云（H100/L40S 按小时计费）：
uv run python scripts/run_and_check.py ref_origin=kernelbench level=1 problem_id=1 \
  kernel_src_path=<你的kernel> eval_mode=modal gpu=H100
```

（锚点：scripts/run_and_check.py:66-78 的四组官方示例）

**fast_p 指标定义**（`src/kernelbench/score.py:28-36`）：

```python
fast_p_score = np.sum(speed_up > p)   # 正确 且 加速比>p 的任务数
return fast_p_score / n               # 占比
```

## 七、对 PerfAgent 设计的直接教益（→ 03-perfloop 落地）

1. **失败分类学**：编译/实例化/正确/性能四级失败分开记录——我们的 CPU loop 照抄这个分类（`compile`/`run`/`correct`/`fast` 四类 verdict）
2. **正确性前置于性能**：keep/revert 判定必须先过正确性
3. **L2/缓存状态是计时的一部分**：CPU 版对应物 = 每次测量前 touch 大数组清 CPU 缓存 + 多次取中位数抗抖动
4. **excessive speedup 的怀疑阈值**：CPU 调优场景同样适用（如"提速 >5× 先怀疑测量错误"）
5. **对抗样本测试集**：裁判写完就写"作弊提议器"单测——比如一个总返回缓存结果的提议器，必须被 guard 抓住

---

生成：2026-08-24 · 上级 [README](./README.md) · 下一篇 [02-A/B实验方法论卡](./02-A:B实验方法论卡.md)

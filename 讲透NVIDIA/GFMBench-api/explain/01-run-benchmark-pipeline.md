# 01 · run_benchmark 执行链：从 CLI 参数到聚合报告的完整干线

> 锚点均以 `usage_examples/run_benchmark.py`（476 行）为主，配合 `gfmbench_api/utils/logutils.py` 与 `gfmbench_api/benchmark_report/benchmark_report.py`，全部行号经源码逐条核实。

## 一、角色定位

`run_benchmark.py` 是整个 GFMBench 的**总指挥**：它不在 `gfmbench_api` 库内，而是住在 `usage_examples/`——这个位置本身就是声明：库只提供任务/指标/报告协议，"怎么把 22 个任务和 7 个模型跑起来"是使用方的事。它一个文件干了五件事：解析 CLI 参数、按注册表懒加载模型适配器、实例化全部任务、按"微调或零样本"二分执行、把每个任务的分数即时写进 CSV。图谱 L08 层只有 4 个节点（`run_benchmark.py` + `trainers/` 三件套），正说明这条干线高度单文件化——读通这一个文件，就掌握了基准的完整生命周期。

它还自带两个工程化的"开机动作"：在 torch 导入前设 `CUBLAS_WORKSPACE_CONFIG=":4096:8"`（`run_benchmark.py:27-28`，确定性 cuBLAS matmul 的前提），以及把仓库根插进 `sys.path`（`:36-38`，因为该文件在 `usage_examples/` 下两层，要保证 `gfmbench_api` 与 `usage_examples.trainers` 都能解析）。

## 二、内部结构

**两份注册表，一懒一饿。** `TASK_REGISTRY`（`:71-94`）是饿加载——文件顶部 `:47-69` 直接 import 了全部 22 个任务类，因为每个任务都必然要用；`MODEL_REGISTRY`（`:97-140`）是懒加载——只存元数据（module/class/max_length/可选 model_kwargs），真正的类由 `get_model_class()` 在运行时用 `importlib.import_module(spec["module"])`（`:147`）动态导入。这 7 个条目只对应 6 个适配器类：`NTv3_8M` 与 `NTv3_100M`（`:113-123`）共用 `ntv3_model` 模块，靠 `model_kwargs` 里的 `model_name` 与 `use_autocast` 区分；`HyenaDNA`（`:125-134`）注释明确把 tiny-16k 的上下文 cap 到 8192 以对齐其他长序列基线；`IsolatedMock`（`:135-139`）max_length 只有 128，是协议冒烟用的进程隔离假模型。**懒加载的收益是硬的**：不装 Evo2 的 megatron 依赖也能跑 DNABERT2 全量基准，ImportError 会被 `:149-150` 包装成带模型名与模块路径的友好报错。

**参数体系三层语义。** 必选两项：`--csv_path`（报告落点，存在则续写）与 `--root_data_dir_path`（数据根目录，`:155-160`/`:211-216`）。模式类：`--linear_prob`（`:173-178`，store_true，只训投影层）与 `--sanity_check_mode`（`:218-222`，每数据集限 100 样本）；前者有一条**硬性联动规则**：`if args.model == "Evo2" and not args.linear_prob: raise ValueError`（`:296-297`）——Evo2 的适配器内部也钉了 `force_linear_probe = True`（`evo2_model.py:94`），全模型微调对 7B 级 AR 模型既不现实也无意义，CLI 与适配器双闸。调参类：`--epochs`（默认 3）、`--seed`（默认 0）、`--cache_size`（GB 上限，None 无限并打 warning `:322-326`）、`--disable_safe_model_call`（`:198-203`，关掉安全包装让异常直接抛，调试用）、`--exclude_tasks`（`:223-229`，跳过指定任务）。

**任务循环主体**（`main()`，`:267-469`）按固定节拍走：`logutils.init_logger()`（`:269`）→ 设备探测 → `set_seed`（`:233-252`，覆盖 random/numpy/torch/cudnn/PYTHONHASHSEED 五路随机源）→ `BenchmarkReport(csv_path)`（`:288`）→ 组装 `task_config`（`:313-320`，把模型 max_length、批大小、缓存等打包传给每个任务）→ 列表推导实例化未被排除的任务（`:337-341`，**构造即下载数据**）。

## 三、外部连接

向上它消费库的三层：`gfmbench_api.tasks.concrete.*`（22 个任务类）、`gfmbench_api.benchmark_report.BenchmarkReport`（聚合）、`gfmbench_api.utils.logutils`（日志）；向下它指挥 `usage_examples.trainers` 的 `GFMFinetuner`（`:65` import，`:414-430` 实例化）。`test_heavy.py:48-49` 直接 `from usage_examples.run_benchmark import TASK_REGISTRY, main`——重回归测试把这条 CLI 干线当库函数调用，说明它虽在 examples 目录，事实上是公共 API。

**22 项注册表不是全集。** `tasks/concrete/` 下有 23 个任务类，唯一缺席注册的就是 `LRBCagePredictionTask`（`lrb_cage_task.py:32`，binned 多轨道回归，50 条 CAGE 轨 × 128bp bin）。原因在循环内部：拿到 `has_finetuning_data=True` 的任务后，`:387-390` 无条件检查 `task_type != "classification"` 即抛 `NotImplementedError("The usage-example fine-tuner currently supports classification only.")`——示例微调器只实现了分类头，CAGE 若注册会在运行时第一刻暴毙，干脆不入表。这是"示例代码能力边界决定注册表范围"的直接实证。

## 四、数据流

单任务迭代（`:364-457`）的数据流是一条**状态重置流水线**：

1. **重播种**（`:376`）：每任务前 `set_seed(seed)` 复位，保证投影头初始化确定；
2. **重建模型**（`:379-382`）：`ModelClass(...)` 全新实例 + 可选 checkpoint 重载——上一任务微调出的权重绝不泄漏到下一任务；
3. **二分执行**：`get_task_attributes()` 返回的 `has_finetuning_data` 决定路线。有监督路径先算输出宽度 `num_outputs`（`:395-399` 的三元表达式：单标签取 num_classes，二类多标签取 num_labels，否则 num_labels×num_classes），再 `task.get_finetune_dataset()` 造 DataLoader（`:406-412`，带独立种子的 `torch.Generator`），交给 `GFMFinetuner.fine_tune()`（`:433`）拿回 `GFMWithProjection` 包装的 test_model；零样本路径直接 `test_model = model`（`:437`）；
4. **评测**：`test_model.eval()` → `task.eval_test_set(test_model)`（`:442`）返回 `{metric_name: score}`；
5. **即时落盘**：`report.add_scores(...)` + `report.save_csv()`（`:449-450`），随后 `clear_ref_cache()`（`:445-446`）清推理缓存。**每任务一存**是刻意的容错设计——22 任务跑数小时，中途 OOM/断电只丢当前任务。

`BenchmarkReport`（`benchmark_report.py:22-117`）是长表聚合器：行=`(task, metric)`，列=模型，未测组合填 `NO_RESULTS` 哨兵（`:32`）；构造时 CSV 存在则 `pd.read_csv` 续写（`:47-50`），所以多次运行不同模型会自然合并成对比矩阵。`:52-61` 与 `:98-100` 的 `_ensure_object_column` 处理了一个真实的 pandas 新版坑：PyArrow `str` dtype 列拒绝 float 赋值，concat 重推断后必须强制回 `object`。

## 五、设计决策

**动态加载而非 if-else 分发**（`:147`）：7 个适配器依赖彼此冲突（transformers vs megatron），importlib 方案让"装什么跑什么"成立，代价是注册表里的 module 字符串失去静态检查——类名拼错要到运行时才炸。

**每任务重建模型**（`:379`）而非只重置投影头：简单粗暴但语义绝对干净，代价是大模型反复加载；对 Evo2 这类初始化昂贵的模型，这是可感知的浪费，但换来"任务间零状态泄漏"的强保证。

**日志线是自建的 ConditionalFileHandler 体系**（`logutils.py:30-71`）：delay 文件创建、error/debug 分流到独立带时间戳文件（`:274-280`）、`atexit` 清理空日志（`:291`/`:327-343`）。但这条线藏着一个**写反的 if/else**：`get_log_prefix()` 的逻辑是"若 log_path 为 None 则从 root logger 找文件 handler 的 baseFilename"（`:407-413`），而 else 分支——即**用户显式传了路径时——直接 `return "unknown"`**（`:414-415`）。语义完全颠倒：提供路径反而拿到 "unknown"，不提供才去自动探测。结合全仓 grep 无人调用 `get_log_prefix`/`get_stamp_from_log`，这是从旧项目带来的工具函数死代码 + 潜伏 bug，修复方式应是把 `else: return "unknown"` 移到"找不到 handler"的分支。

**seed 双重设置**（`:277` 一次、`:376` 每任务一次）：前者管全局，后者管逐任务公平。配合 `--disable_safe_model_call` 默认关闭，默认路径上模型方法失败会被 `_safe_model_call` 吞成 None、指标返回 None 而非崩溃——跑 22 任务的长途车，中途一个任务的不支持不该废掉整趟。

## 六、新人提示

- 读这个文件建议顺序：`:71-140`（两份注册表）→ `:267-361`（main 前半）→ `:364-457`（任务循环）→ 回头看 `parse_args`。参数与语义对上后，`main` 就是直线代码。
- `--linear_prob` 对 Evo2 不是可选项：忘了加会在 `:296-297` 秒抛 ValueError，报错文案已写明修法。
- 想复现论文数字，四件套别动：`--seed 0`、`--epochs 3`、lr 3e-5（`:346` 硬编码在 training_params）、AdamW + weight_decay 0.01（`:347-348`）。
- `test_heavy` 用 `_benchmark_argv`（`test_heavy.py:107-131`）走的就是这条 main，加 `--sanity_check_mode --linear_prob --disable_safe_model_call --exclude_tasks vepeval_clinvar`；想改执行链行为，先看测试怎么锁它。
- 给注册表加新任务只需一行 dict entry；但如果它是回归任务且要微调，先补 `finetuner.py` 的回归头，否则 `:387-390` 会教你做人。改 `get_log_prefix` 类工具函数时记得它当前零调用者，属安全重构区。

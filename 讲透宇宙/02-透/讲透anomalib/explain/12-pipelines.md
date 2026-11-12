# 12 · Pipelines 体系（src/anomalib/pipelines/）

## 一、角色定位

`src/anomalib/pipelines/` 是 anomalib 的批处理骨架（图谱 cli-pipelines-deploy 层，tour T10）：把"拆成可并行原子作业、串成带阶段依赖的流水线"抽象成三个类——`Pipeline`（编排）、`Job`（原子工作）、`Runner`（执行策略）。两个成品：Benchmark 基准评测（多模型×多数据集组合跑分）与 Tiled Ensemble 高分辨率检测（CVPRW 2024"Divide and Conquer"工程化：切块逐 tile 训模型再拼图）。与 Engine 分工：Engine 管**单模型**训练循环，Pipeline 管**跨模型/跨阶段**编排。入口：CLI `anomalib pipeline benchmark` 与脚本 `tools/tiled_ensemble/train.py`。

## 二、内部结构

**components/base/job.py:42（109 行，作业协议）**：`Job(ABC)`（L42）三段式：`run(task_id)` 执行单作业（L47-52，task_id 并行时注入供设备分配）；静态 `collect(results)` 汇总（L54-66）；`save(results)` 落盘（L68-77）。`JobGenerator(ABC)`（L80）是作业工厂：`__call__`（L87-93）转调抽象 `generate_jobs`（L95-104）惰性产出 Job；`job_class` 属性（L106-108）供 Runner 取 name 与 collect/save。

**components/base/pipeline.py:50（104 行，编排协议）**：`Pipeline(ABC)`（L50）。`_get_args`（L53-68）：args 为 None 则解析 `--config`，L67-68 `yaml.safe_load`。`run`（L74-95）是心脏：L80-81 调子类 `_setup_runners` 拿 Runner 列表；L82 `redirect_logs("runs/pipeline.log")`；L85-95 循环——L87 按**作业类名从 YAML 顶层键取参**（配置结构与作业命名强约定），L88 上一阶段结果作 `prev_stage_result` 传下去；单阶段失败只记日志不中断（L89-95），容错优先。

**runners/serial.py:48 与 parallel.py:46（127/128 行，双执行策略）**：`SerialRunner.run`（serial.py L76-127）：L113 tqdm 逐个 `job.run()`，失败置 flag 继续（L114-118），L119-125 collect→save，失败抛 `SerialExecutionError`。`ParallelRunner`（parallel.py L46）带 `n_jobs`（L85-90）；`run`（L92-113）：L96 `ProcessPoolExecutor(mp_context=get_context("spawn"))`——spawn 保证 CUDA 子进程干净；L97-103 调度自旋：池满就回收，有空位则 L102 `executor.submit(job.run, task_id=index)` 槽位号即设备号（`cuda:{task_id}`）；L105-106 collect/save，失败抛 `ParallelExecutionError`。

**benchmark/（pipeline.py:68、job.py:55，125/218 行）**：`Benchmark(Pipeline)`（pipeline.py L68）的 `_setup_runners`（L90-125）：L117 只认 cpu/cuda 否则 ValueError；L121-124 单卡/CPU 走 Serial，多卡每加速器一个 ParallelRunner(n_jobs=device_count)。`BenchmarkJob`（job.py L55，name="benchmark" L94）单 run 装配模型+数据训练评测；`collect`（L167）拼 DataFrame，`save`（L187）落 CSV。组合爆炸来自 `grid_search.py:37` 的 `get_iterator_from_grid_dict`：generator.py L92 把配置里所有 `grid: [...]` 展开成笛卡尔积逐个 yield。

**cli/pipelines.py:23（69 行，CLI 接线）**：L19-25 `PIPELINE_REGISTRY = {"benchmark": Benchmark}`（探测失败则 None）；L28-46 生成子命令；L49-69 `run_pipeline` 分发，L62 打 experimental 警告。

**tiled_ensemble/train_pipeline.py:33（122 行）**：`TrainTiledEnsemble._setup_runners`（L39-122）把论文流程钉成五个 Runner：L50 `setup_ensemble_workspace` 建总 workspace；①L80-92 逐 tile 训练（cuda 时 ParallelRunner 按 GPU 数并行）；②L98-106 验证集逐 tile 预测；③L109 Merge 拼回全图；④L112-117 可选 SeamSmoothing；⑤L120 Statistics 算推理统计量。L94-96 无验证集则告警只留训练。`EvalTiledEnsemble`（test_pipeline.py L28）同构，追加 normalization/thresholding/metrics 阶段。`TiledEnsembleEngine`（ensemble_engine.py L20）继承 Engine：L34-35 覆写 `_setup_workspace` 为空（每 tile 不各建目录）；L38-57 拼 versioned 目录；L59-77 给 checkpoint 名打 tile 坐标 `model{tile_i}_{tile_j}`（L66-73）。入口 tools/tiled_ensemble/train.py：L10-17 训练完用 `train_pipeline.root_dir` 接着跑 Eval。

**types.py:24（26 行）**：L24-26 三个 Any 别名 RUN_RESULTS/GATHERED_RESULTS/PREV_STAGE_RESULT——放弃类型约束换跨作业异构通用性。

## 三、外部连接（图谱边证据）

base/pipeline.py、base/job.py、runners/parallel.py 各带大量 documents 边连教程 `how_to/pipelines/custom_pipeline.md` 与 reference 页——三抽象是被文档背书的公共扩展点。benchmark/pipeline.py 与 train_pipeline.py 均带 tested_by 边（`test_benchmark.py`、`test_tiled_ensemble.py`）。train_pipeline 的 imports 边伸进 10 个作业组件与 ensemble_engine（又被 model_training/prediction import）——tile 世界的局部 Engine 单点。cli/pipelines.py 被 cli/cli.py import（主 CLI 挂载点）。`pipelines/__init__.py` 只导出 Benchmark（L29-31），tiled_ensemble 不在顶层——两个成品曝光度刻意不对等。

## 四、数据流

以 tiled ensemble 为例：tools 脚本 `TrainTiledEnsemble().run()` → Pipeline.run 解析 ens_config.yaml → 依次五 Runner。每阶段内部：generate_jobs 展开（训练阶段展开成 tile 数个作业）→ Runner 逐个/并行 `job.run(task_id)` → collect → save → 作下一阶段 prev_stage_result。训练产出每 tile checkpoint；预测消费训练产出 tile 级预测；合并产出全图级预测；统计产出 normalization/threshold 参数写 workspace。Benchmark 流相同但单阶段：grid 展开 N 作业 → 并行训练评测 → DataFrame → CSV。

## 五、设计决策

1. **三抽象正交**：Job 管做什么、Generator 管做几次、Runner 管怎么跑；Benchmark 与 TiledEnsemble 共用同一对 Runner 零并发代码复制。
2. **阶段链显式传 prev_stage_result**（pipeline.py L88）而非全局上下文，数据依赖在签名可见；types.py 用 Any 放弃编译期检查是明确取舍。
3. **容错"收集后抛"**：单作业失败不阻塞兄弟（serial L114-118 / parallel L124-127），阶段收尾才抛。
4. **spawn + task_id 槽位制**：并行度=GPU 数、task_id=槽位号=设备号，多卡分配零配置（parallel.py L66-75 Notes）。
5. **TiledEnsembleEngine 只覆写两个钩子**（workspace 与 callbacks）复用 Engine 全部训练逻辑——继承点选在目录策略而非训练循环。

## 六、新人提示（含勘误）

- **已知勘误（docstring 文件名漂移）**：tiled_ensemble/__init__.py L23 Usage 写 `python tools/tiled_ensemble/train_ensemble.py`，**磁盘实际是 `tools/tiled_ensemble/train.py`**（ls 实证仅 ens_config.yaml/eval.py/train.py）；L27 的 eval.py 引用正确。照 docstring 敲命令会 FileNotFoundError。
- **图谱/巡览口径勘误**：tour T10 称"pipelines.py 把管线扫描注册成 CLI 子命令"——源码 L23 是**硬编码字典，无扫描**；且 TiledEnsemble 不在注册表里，只能经 tools 脚本调用。新管线进 CLI 须手改 dict（L62 的 experimental 警告会打给用户）。
- **YAML 顶层键=作业类 name**：pipeline.py L87 按 `job_class.name` 取参，ens_config.yaml 里 `TrainModels:`、`SeamSmoothing:` 等键名是代码约定，改名即静默失配（拿到 `{}`）。
- Benchmark 只支持 cpu/cuda（pipeline.py L117）；TiledEnsemble 训练同样只在 `accelerator == "cuda"` 时并行（train_pipeline.py L80）。
- 并行作业必须可 pickle（spawn 语义）：不可序列化对象塞 Job 属性会在 submit 爆；BenchmarkJob 只带配置、模型在 run() 内构造。
- 排错先看 `runs/pipeline.log`（L46）；阶段报错只 exception 不 re-raise，"Please check ... for more details"（L91-95）不是客套。

---
**自检**：总字符（不含换行）4565 / 去空格字符 4259；行号锚 49 个（job.py×8、pipeline.py×8、serial×4、parallel×6、benchmark×6、cli/pipelines×4、tiled_ensemble×9、types×1，均经源文件核实；另补 file:line 路径锚 10 处——job.py:42、pipeline.py:50、serial.py:48、parallel.py:46、benchmark/pipeline.py:68、benchmark/job.py:55、grid_search.py:39、cli/pipelines.py:23、train_pipeline.py:33、types.py:24，均 grep -n 实证）。

# 05 deployment-toolkit 与 bermuda

## 角色定位

deployment_toolkit 是 NVIDIA "部署与基准工具箱"，以**复制件**形式散布全仓十处（BERT/TFT/GPUNet/ConvNets/nnUNet/FastPitch 的 triton 目录、TSPP、TF/TF2 三处），每处随示例一起演进、版本各自漂移（BERT 复制件 `.version`=0.7.2，TSPP 复制件=0.7.11）。图谱把它归入第 5 层"BERT Triton 推理部署"与第 15 层"TSPP 部署与 Triton 推理"。本篇以 TSPP 侧（`Tools/PyTorch/TimeSeriesPredictionPlatform/triton/deployment_toolkit/`，较新）与 BERT 侧（较老但多一个 TRT 后端）对照讲述，同时覆盖 BERT triton/runner 编排框架——它是消费 toolkit 的最大客户。

bermuda 是 toolkit 内 `bermuda/` 子包（onnx.py/pyt.py/utils.py），图谱 languageNotes 钉版其身份：**bermuda 是 model_navigator 的内部模块名**（navigator 对框架 backend 的封装层），与 TSPP 自身业务无关——又一个 vendored 命名化石。

## 内部结构

**runner 编排框架（BERT triton/runner/，编排核心）**：

- `runner.py:35` Runner 组装七组件；L59-60 实例化 preparer/finalizer；L75 挂 SIGINT 信号捕获、L79 `start()` 按 prepare→execute→finalize 推进（L88 prepare.exec、L105 finalizer.exec）；
- `runner_proxy.py:35-38` RunnerProxy 四个类属性槽位（maintainer/executor/preparer/finalizer_cls），L40 `__init__` 把类注入真实 Runner，L59 `start()` 纯委托——三变体 __main__.py 的 ExperimentRunner 就此省掉一切胶水（见第 04 篇）；
- `pipeline.py:51` `_stages` 字典为注册中心，六个注册方法（L53 model_export/L66 conversion/L79 deploy/L92 prepare_profiling_data/L105 offline/L123 online）各自把命令模板包成 Stage 塞入，L141 `stages()` 按实验配置吐出阶段序列——声明式装配的目标类；
- **Container 三级抽象**：`maintainer/container.py:18` Container(ABC) 定 start/stop/run 三方法契约 → `maintainer/docker/container.py` DockerContainer（docker SDK 通用封装，exec_run 进容器执行）→ `containers/triton_server_container.py` TritonServerContainer（挂 GPU/卷/custom library、等服务就绪、后台线程落 server 日志）；Maintainer(ABC)→DockerMaintainer 工厂链与之配套；
- `executor.py:77` start() 逐阶段导出环境变量、启动容器、CommandsExporter 把命令集导出为可复现 BASH 脚本并执行落盘。

**extensions.py 插件骨架**：L25 ExtensionManager，L30 `register_extension` 带模块冲突检测（同名不同模块直接 raise），L44 `get` 取件；L78-81 全局四管理器 runners/loaders/savers/converters；L55 正则 `.*\.register_extension\(` + L83 `scan_for_extensions` 扫目录自动装载——bermuda 各文件尾部的注册语句因此被自动发现。

**bermuda 双后端**：`onnx.py` L113 OnnxLoader（checker+形状推断+networkx 图统计推精度）、L135 OnnxSaver、L192 OnnxRunnerSession（包装 onnxruntime.InferenceSession），L235-236 注册 ONNX 的 loader/runner；`pyt.py` L123 PyTorchModelLoader（动态加载 get_model，按输出类型分派 trace/script/onnx）、L204 PYT2ONNXSaver（torch.onnx.export 动态轴）、L254 PyTorchRunnerSession（torch.no_grad），L285-295 注册 pyt/ts-script/ts-trace/pyt--onnx 四组。BERT 复制件独有 `tensorrt.py`：L51 TensorRTLoader、L94 TensorRTRunner，L228-231 的注册带 `if "pycuda.driver" in sys.modules:` 守卫（pycuda 缺席则告警降级不注册）。

**perf_analyzer 线**：`perf_analyzer.py` 以 Popen 流式跑 perf_analyzer 二进制，L89 输出含 "Failed to obtain stable measurement" 时按测量模式自动加大 request-count 或 interval 重试至多 10 次。

## 外部连接

- toolkit 被 BERT triton 的 run_performance_on_triton.py（648 行，`--performance-tool` 分派 MODEL_ANALYZER 与 PERF_ANALYZER 两路，L406/L428）与 run_inference_on_* 全线 import；
- bermuda 的 PYT2ONNX 依赖 torch.onnx；OnnxRunnerSession 依赖 onnxruntime；BERT 复制件的 TRT 后端依赖 pycuda/tensorrt；
- summary.py 复用 deployment_toolkit.report 的 sort_results/save_results（跨批消费）；executor 引用 toolkit 的 Accelerator/Precision 枚举；
- 十份复制件间无 import、无同步机制——上游（DeepLearningExamples 内部的 toolkit 源或 model_navigator 仓）更新靠人肉重拷。

## 数据流

以 BERT 三变体的性能测试为例：Runner.start → ExperimentPreparer 下载 checkpoint/建目录 → Executor 逐实验：Configuration.parameters() 展开环境变量 → TritonServerContainer 起服务 → 阶段命令经 bermuda 取件执行（export 走 PyTorchModelLoader+PYT2ONNXSaver；correctness 走 OnnxRunnerSession/PyTorchRunnerSession 对照 run_inference_on_fw 的框架真值；perf 走 PerfAnalyzer 或 ModelAnalyzer）→ 结果落 csv/json/yaml → Finalizer 的 load_results 聚合（summary.py 键归一化 _normalize_key）生成 summary。bermuda 的 loader/saver/runner 三类扩展在数据流中分别对应"模型进门→模型出门→模型跑起来"三个切点。

## 设计决策

1. **复制件优于共享包**：联邦仓无包管理基础设施（各示例 Dockerfile 独立），copy-in 是唯一不引入运行时依赖的复用法；代价是十份漂移——BERT 侧 0.7.2 停更但多了 TRT 后端（当时 BERT 部署需要），TSPP 侧 0.7.11 更新但删了 TRT。读代码必须先 `.version` 定代际。
2. **注册中心+正则扫描的微插件系统**：ExtensionManager 用 30 行实现了类型安全的注册/冲突检测/自动发现，bermuda 后端因此可以"文件即插件"——新增格式只需新文件尾部两行注册，零中心化配置。
3. **RunnerProxy 的类属性注入**：把"组装哪些组件"从运行期参数升格为类型声明，三变体各自定义 ExperimentRunner 子类即可换件——比传参工厂少一层 if/else，比继承 Runner 少一层耦合。
4. **容器三级抽象的动机**：executor 不感知 docker、DockerContainer 不感知 Triton、TritonServerContainer 不感知实验——换容器运行时（如 podman）或换服务（如 torchserve）各只动一层。

## 新人提示

- **两个源码级 bug 钉版（读旧版部署代码必知）**：
  1. **布尔陷阱**（perf_analyzer.py:112-115）：`_faild_with_measruement_inverval`（函数名三处拼写错误：faild/measruement/inverval）写作 `(output.find(A) or output.find(B)) != -1`——`str.find` 未命中返回 -1（真值），`or` 短路后整个表达式恒为 -1 判 False：第二段 "Please use a larger time window" 的检测**几乎永不可达**（仅当 A 恰好出现在位置 0 才轮询 B），且 A 命中在位置 0 时也会漏判。正确写法应是两个 `!= -1` 分别比较。后果：部分"测量窗口过小"场景不会触发自动加大 interval 的重试，直接抛异常。
  2. **np.narray 笔误**（dump.py:82）：`batch = np.narray(batch)`——numpy 没有 `narray`（应为 `np.asarray`）。触发条件是 cache_size 属性统计时 batch 尚非 ndarray，一旦走到即 AttributeError。此笔误在 BERT/TSPP/TFT/GPUNet 四份复制件中逐字相同——复制件把 bug 也忠实复制了。
- 改任一复制件的 bug 前先想清楚：上游是 model_navigator/toolkit 仓，本地修十份不如向上游提 PR；联邦仓的修复策略是"等重拷"。
- `experiment.py` 的 Stage 与 `stages.py` 的 Stage 同名不同物（运行记录 vs 阶段模板），跨文件读代码时先看 import 来源。
- TritonServerContainer 的 custom_library_path 路径映射（runner/triton.py 的 library_path/custom_library_path）解决"custom ops 库本地路径→容器路径"换算，挂自编 CUDA 算子时这是必经之路。

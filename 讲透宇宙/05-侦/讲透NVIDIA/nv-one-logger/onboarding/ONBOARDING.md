# nv-one-logger 深度导览（ONBOARDING）

> 基于知识图谱（560 节点 / 1341 边 / 11 层 / 12 步 tour，fingerprints 153 文件 @ c382dd51）与全量源码行号锚核实编写。仓位于 `/usr-data/data2/repos/agent-repos/NVIDIA/nv-one-logger`。

## 一、一页纸定位：统一遥测的"永不打断训练"库

nv-one-logger 是 NVIDIA 开源的**统一遥测（unified logging）Python 库**：给训练/推理/数据处理作业提供一套 span/event/attribute 数据模型，把遥测数据同时发给多个后端（OpenTelemetry、Weights & Biases、文件/日志）。核心承诺写在 safe_execution 模块头（safe_execution.py:4）——**"errors in onelogger library do not cause the instrumented application to crash"**：遥测代码出任何错都不许打断训练主进程。

语言形态要先钉死：这是**纯 Python 五包 monorepo**（Poetry 构建、src-layout），不是某些人预期的 C++ 日志库。五个包同版本号 2.3.1（one_logger_core/pyproject.toml:3），按"核心最小 + 后端可选"分层：

| 包 | 角色 | 依赖关键项 |
|---|---|---|
| one_logger_core | 数据模型 + Recorder + exporter 插件框架 | pydantic ^2.10.6, overrides（python ^3.8） |
| one_logger_training_telemetry | TrainingRecorder 训练语义层 | 依赖 core |
| one_logger_otel | OTel 后端 | opentelemetry-sdk |
| one_logger_wandb | W&B 后端（同步/异步双实现） | wandb ^0.20.1（one_logger_wandb/pyproject.toml:19）, urllib3>=2.5.0（NSPECT 要求 :23-24） |
| one_logger_pytorch_lightning_integration | Lightning 无侵入接入 | lightning |

作者群是 `HWInf-MLWFO`（NVIDIA 硬件基础设施 ML 工作流团队，one_logger_core/pyproject.toml:5）。

## 二、五包共存术：PEP 420 命名空间包

五个包怎么拼成一个 `nv_one_logger` 导入树？答案是**隐式命名空间包（PEP 420）**：每个包都在 `src/nv_one_logger/` 下发货自己的子包（core 在 `src/nv_one_logger/core/`，otel 在 `src/nv_one_logger/otel/`），而 `src/nv_one_logger/` 目录**故意没有 `__init__.py`**。仓里四处放着 no_init.md 警告（one_logger_core/src/nv_one_logger/no_init.md:3）：*"Do not add an init.py to this directorty. nv_one_logger is a namespace package."*

机制：PyPI 上分别安装五个发行版后，Python 的命名空间包机制自动把五个 `nv_one_logger` 目录合并成一个包——core 提供 `nv_one_logger.core/api/recorder/exporter`，training_telemetry 提供 `nv_one_logger.training_telemetry`，otel/wandb/lightning 集成各自补 `nv_one_logger.otel/wandb/training_telemetry.integration`。这也解释了为什么用户可以"只装 core+file exporter"零重依赖起步。

工程后果：**静态分析器与图谱 scanner 对这种布局天然失明**——import 目标（如 `nv_one_logger.training_telemetry.api.training_recorder`）跨发行版分布，单包扫描看不到全貌；本仓图谱阶段的 imports 边大量依赖人工补扫核对（勘误清单第 4 条）。

## 三、core 包纵览：四子包分工

`one_logger_core/src/nv_one_logger/` 下四个子包构成最小契约面：

- **api/**：使用方视角。`OneLoggerProvider`（one_logger_provider.py:15，`metaclass=SingletonMeta`）是全局入口——docstring（:20-24）解释了为什么必须单例：Recorder 有状态，不搞单例就得把实例在应用里到处穿。`configure()` 只许调一次（:62-66 断言）；`one_logger_enabled`（:88-90）综合"已配置 + 未被强制禁用 + 当前 rank 启用"三态；`force_disable_logging()`（:92-94）是错误处理策略的执行器。配置模型 `OneLoggerConfig`（config.py:91）是 pydantic BaseModel：application_name（:105）、world_size_or_fn（:109）、session_tag_or_fn（:119），字段全部支持 `Union[T, Callable[[], T]]` 惰性求值；LoggerConfig（:70）定义日志级别/格式与 info/err 双文件（:73-81）。`Recorder` 是 ABC + EnforceOverrides（recorder.py:13），start 五参数签名（:33-41）确立了"父子 span 自动追踪"的入口契约。
- **core/**：值对象。`Span`（span.py:60）带 uuid id/parent_span/events/attributes，刻意保留 Attributes 子类类型（span.py:104-107 注释）；`StandardSpanName`（span.py:15）与 `NVTXColor`（span.py:38）内置标准名与 Nsight 拓扑追踪桥接；`TracingTimestamp`（time.py:11）是 frozen dataclass，**双时钟设计**——epoch 墙钟给人看、perf_counter 高分辨率给算时长用（time.py:15-22）；`AttributeValue`（attributes.py:17）只允许原始类型与同质列表（attributes.py:29-33 强校验），注释明说是为了 wandb/OTel 后端的序列化友好。
- **core/internal/**：四件套机制。`SingletonMeta`（singleton.py:8）用类级 dict + RLock（:19-20）双检锁（:36-42），`__call__` 直接 `raise TypeError` 逼你走 `instance()`（:22-25）；`safe_execution` 详见第四节；`MetricSummarizer`（metric_summarizer.py:13，Generic[T]）add_value 维护 latest/min/max/avg/total/count 六统计（:28-33）；`MultiWindowTimer`（multi_window_timer.py:10）专管"可暂停恢复的多窗口计时"（训练迭代/存 ckpt 这类反复起停的操作），docstring（:33-34）自认非线程安全、窗口不可重叠。
- **exporter/** 与 **recorder/**：插件体系（第五节）与 `DefaultRecorder`（default_recorder.py:55）。

## 四、fail-open 内核：错误处理策略双轨

整个库的安全哲学是**遥测永远让路于训练**，由 config.py:33-67 的 `OneLoggerErrorHandlingStrategy` 枚举定义双轨：

1. `PROPAGATE_EXCEPTIONS`（config.py:59）——异常直接抛给调用方，开发期要最大可见性；
2. `DISABLE_QUIETLY_AND_REPORT_METRIC_ERROR`（config.py:67）——吞异常、打一条日志、通知后端"数据有缺陷"、然后**把整个库静默关掉**。

智能默认（config.py:44-46）：被启用遥测的 rank 默认 PROPAGATE（要看见错误），未启用的 rank 默认 DISABLE_QUIETLY（要安全）。执行者是 `exception_guard` 装饰器（safe_execution.py:39-84）：先调 `recorder.telemetry_data_error()` 通知所有 exporter（:56-58），再按策略分流；模块级旗标 `__telemetry_data_issue_already_logged`（:36，:72-76）保证应用日志里只留一条错误不刷屏；`safely_execute`（:87-105）在外层再加一道"未启用就不执行"的闸（:98）。

与之配套的是 DefaultRecorder 的 **exporter 级熔断**（default_recorder.py:24-26）：`_DISABLE_EXPORTER_AFTER_N_FAILURES = 5`——一个 exporter 连挂 5 次就 `force_disabled`（_ExporterState 四字段 :37-53），理由写在 docstring（:65-71）：后端网络抖动不代表库有 bug，一个挂了别拖累其他。类 docstring（:74-77）还给出"零 exporter 构造"的合法用法：几千卡作业只在 rank 0 记录，其他 rank 全静默。

## 五、exporter 插件体系：entry-points 发现 + 动态导入

`Exporter` 是七方法 ABC（exporter.py:19，initialize/export_start/export_stop/export_event/export_error/export_telemetry_data_error/close，:22-101），`BaseExporter`（:104）加状态机防护：NOT_INITIALIZED→READY→CLOSED（:110-115），未初始化或已关闭即抛 ExportError（:173-177）。

配置发现走 **Python entry points**：`ExporterConfigManager.ENTRY_POINT_NAME = "nv_one_logger.exporter_configs"`（export_config_manager.py:32，import 自 importlib.metadata :4），任何第三方包在 pyproject 注册这个 entry point 即可被发现；三级优先级 direct > file(YAML/JSON) > package（:18-28，generate_export_config :48-109，file 配置完全替换而非合并 :97-98）；`create_exporters_from_config`（:111-137）按 config 里的 class_name **动态导入**并跳过创建失败项（:131-136）。

内置与官方实现四个：

- **BaseJsonExporter**（base_json_exporter.py:19）：JSON 行输出基类，RLock + `os.getpid()` 防 fork 后误写（:28-30），`_last_start_span` 缓存实现"叶子 span 合并成单条记录"的优化（:33-37）；子类 `FileExporter`（file_exporter.py:17，紧凑 JSON+换行 :67-70）与 `LoggerExporter`（logger_exporter.py:16，层级 key 格式化 :35-69 + 可反序列化 deserialize_log :80）。
- **OTelExporter**（otel_exporter.py:25）：构造时注入任意 `opentelemetry.sdk.trace.export.SpanExporter`（otel_exporter.py:28-32），内部用 TracerProvider/BatchSpanProcessor（otel_exporter.py:15-16），把 one-logger span 映射成 OTel trace span 并维护 uuid→(span, context) 映射传播父子关系（otel_exporter.py:39，:75-91）；event 被映射成"fake_event_span"（otel_exporter.py:158）以适配 OTel 无事件概念的现实。
- **WandBExporterSync / WandBExporterAsync**（wandb_exporter.py:282/335）：W&B 没有 span 概念，于是用 `MetricNamingStrategy`（:73）把属性拍平成指标名——默认 `HierarchicalMetricNamingStrategy` 生成 `my_span.my_event.bar` 式点分名（:103，:351-354），另有 Flat 变体（:135）。**异步版是全库最重的设计**：`mp.Pipe(duplex=True)` + daemon 子进程（:362-363），wandb 初始化与 log 全在子进程（:373-414），双向管道传指标/回错误（:434-456）；`_initialize_wandb` 特意临时改 WANDB_RUN_ID/WANDB_SERVICE 环境变量避免与用户自己的 wandb 记录打架（:57-61）——这是"onelogger 不干扰应用"承诺在进程边界的延伸。

## 六、training_telemetry：TrainingRecorder 千行主线

`TrainingRecorder`（training_telemetry/api/training_recorder.py:187，全文 1068 行）继承 DefaultRecorder，把训练作业建模成**标准 span 树**（spans.py:5 StandardTrainingJobSpanName 共 19 个：spans.py:17 TRAINING_LOOP、spans.py:30 DIST_INIT、spans.py:45 CHECKPOINT_SAVE_SYNC、spans.py:49 CHECKPOINT_SAVE_ASYNC、spans.py:52 CHECKPOINT_SAVE_FINALIZATION、spans.py:59 TRAINING_SINGLE_ITERATION 等），并定义标准事件（events.py:5：events.py:16 ONE_LOGGER_INITIALIZATION、events.py:34 TRAINING_METRICS_UPDATE 等）。

三大状态机：

- `_TrainingState`（training_recorder.py:95-184）：迭代计数、样本数、FLOPs、token 数、各阶段时间戳；五把 `MultiWindowTimer` 分别跟训练/验证/存档窗口（:49-66，字段挂载 :115）；`tflops_per_gpu` 用 MetricSummarizer 聚合（:166）。
- `_ProductivityState`（:70-91）+ `productivity_state: Dict[int, _ProductivityState]`（:179）：**生产力度量**——只有最终落进成功 checkpoint 的工作才算"productive"，异步存档可能乱序完成，所以按迭代号字典存快照、配合 `max_reported_productive_train_iterations`（:184）防止旧 ckpt 回填乱序指标。这是"算力利用率审计"思维的落地。
- `on_*` 事件钩子族（:360 on_app_start、:688 on_training_single_iteration_start、:938 on_save_checkpoint_start、:986 on_save_checkpoint_success……共 20+ 个），全部 @safely_execute 包裹（如 :442）——遥测故障绝不打断训练。

上游 `TrainingTelemetryProvider`（training_telemetry_provider.py:43，又一个 SingletonMeta 单例）是 OneLoggerProvider 的训练特化包装：builder 模式增量拼配置（with_base_config/with_config_override/with_exporter/configure_provider，:85-115）；默认**黑名单导出**八个高频短 span（:25-34 DEFAULT_SPANS_EXPORT_BLACKLIST：单迭代/前向/反向/优化器步等——"量太大，默认不导出"）；`_ReadOnlyConfig`（:37-40）frozen 拷贝防运行中篡改。注意 **api/ 下的 training_recorder.py 才是真身，包根的 src/nv_one_logger/training_recorder.py 是 0 字节空文件**（上游兼容遗留占位，甄别见勘误）。

## 七、框架集成：Lightning 的三种接入路径

one_logger_pytorch_lightning_integration 包提供三层递进的接入方式（pytorch_lightning.py，304 行）：

1. **TimeEventCallback**（pytorch_lightning.py:47）：标准 Lightning `Callback` 子类，构造签名（pytorch_lightning.py:57）吃 provider；挂进 Trainer 的 callbacks 列表即可吃 on_train_start（pytorch_lightning.py:70）/on_train_batch_end（pytorch_lightning.py:93）/on_validation_*（pytorch_lightning.py:98-127）等钩子；但 Lightning Callback 没有"存档后"钩子（pytorch_lightning.py:50-53 docstring 自述），所以又补了 pytorch_lightning.py:129-185 一批非 Callback 接口的手动钩子。
2. **hook_trainer_cls**（pytorch_lightning.py:189-248）：**运行时打补丁**——包装 `cls.__init__` 强制把 telemetry callback 插到 callbacks 列表头（pytorch_lightning.py:215-228），包装 `save_checkpoint` 前后埋 on_save_checkpoint_start/success/end（pytorch_lightning.py:236-246），并注入 `nv_one_logger_callback` 只读属性（pytorch_lightning.py:230-233）。docstring（pytorch_lightning.py:194-195）坦承只覆盖**同步**存档路径，异步存档不在其内。
3. **OneLoggerPTLTrainer**（pytorch_lightning.py:251）：继承 `Trainer` 的正式子类，构造器自动插 callback（pytorch_lightning.py:268-270），`save_checkpoint` 覆写用 try/TypeError 兼容新旧 Lightning 签名（pytorch_lightning.py:287-292 有无 storage_options 参数）。零改动用户代码、又拿到存档全遥测，推荐路径。

`_compat/lightning.py`（21 行）处理 Lightning 版本兼容面。训练语义层的强类型门面是 training_telemetry/api/attributes.py（1140 行，每类 `create()` 类方法逐属性校验，产出扁平 Attributes 字典）与 context.py（运行上下文 272 行）、checkpoint.py 的 CheckPointStrategy。

## 八、工程链、测试体系与新人路线

- **CI**：根 .gitlab-ci.yml 只声明 test/build_deploy 两 stage（:2-4），include 五个子包各自的 .gitlab-ci.yml（:8-13）——**每包独立流水线**是 monorepo 的发布纪律。内部源流是 GitLab（Makefile:19 的 GIT_URL 指向 gitlab-master.nvidia.com/hwinf-dcm，开源镜像在 GitHub）。
- **Makefile 四命令**（one_logger_core/Makefile:6-9 注释）：make check（lint+format+flake8）/ format / test / publish（五包同构）。
- **测试**：31 个 test_*.py、382 个测试函数；分布 core 19 个文件（api/recorder/exporter/core.internal 四线齐测）> training_telemetry 8 > wandb 2 > otel/lightning 各 1。契约测试范式突出：test_one_logger_provider 验"只许 configure 一次"、test_singleton 验单例语义、test_export_config_manager 验三级优先级合并；training_telemetry 侧单例重置工具是 tests/nv_one_logger/training_telemetry/api/utils.py:17 的 reset_singletong_providers_for_test（上游拼写错误，勘误第 3 条）。
- **版本管理**：python-semantic-release（build-system 五包统一），version.py 运行时向上找 pyproject.toml 读版本（version.py:13-22），找不到回退 importlib.metadata。

**新人路线**：README 的 How to use → core/api/one_logger_provider.py 全文（95 行）→ default_recorder.py 的 docstring（错误处理哲学都在里面）→ spans.py+events.py 的标准名词表 → training_recorder.py 的 _TrainingState 注释段（:95-184）→ 想接 Lightning 就读 pytorch_lightning.py 的三种路径选型。图谱导航：L01 CI 总线 → L02-L05 core 四层 → L06 training_telemetry → L07 框架/后端集成 → L08-L09 测试 → L10-L11 工程配置与许可，与本文三~八节一一对应。

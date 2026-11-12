# 01 · core 包与 PEP 420 命名空间（no_init.md / one_logger_provider / singleton）

## 角色定位

one_logger_core 是五包体系的基座：定义 Span/Event/Attributes 数据模型、Recorder 抽象、exporter 插件接口与 OneLoggerProvider 全局入口。它对上不依赖任何兄弟包，对下只靠 pydantic/overrides/StrEnum 四个轻依赖（pyproject.toml，python ^3.8）——"最小契约面"是它的存在理由：不装 OTel/wandb 也能用 FileExporter 跑通全链路。

## 内部结构

core 内部四子包分工明确：api/（provider+config+Recorder ABC+timed_span）、core/（值对象）、core/internal/（singleton/safe_execution/summarizer/timer 四件套）、exporter/ 与 recorder/。OneLoggerProvider（one_logger_provider.py:15）用 `metaclass=SingletonMeta["OneLoggerProvider"]` 起步；configure() :62-66 断言"只许一次"；one_logger_enabled :88-90 是三态合成（已配置 ∧ 未强制禁用 ∧ 当前 rank 启用）。OneLoggerConfig（config.py:91）是 pydantic BaseModel，application_name/world_size_or_fn/session_tag_or_fn（config.py:105-119）字段全支持 `Union[T, Callable[[], T]]`——配置可以先声明、求值推迟到真正使用；LoggerConfig（config.py:70）另定日志级别/格式与 info/err 双文件（:73-81）。Recorder ABC 的 start 五参数签名在 recorder.py:33-41。

## 外部连接

PEP 420 命名空间包是五包共存的关键：src/nv_one_logger/ 目录刻意无 `__init__.py`，no_init.md（one_logger_core/src/nv_one_logger/no_init.md:3）警告"加了 init.py 就毁掉命名空间"。安装后 Python 自动把五个发行版的 nv_one_logger 目录合并：core 出 core/api/recorder/exporter 四子树，training_telemetry/otel/wandb/lightning 各自补自己的子树（集成包同样有自己的 integration/no_init.md）。下游消费方只 import `nv_one_logger.*`，完全不感知发行版边界。

## 数据流

应用启动 → OneLoggerProvider.instance().configure(config, recorder)（one_logger_provider.py:55-68）→ 全局任意位置 provider.recorder.start(...) 开 span（Recorder 契约 recorder.py:33-41）→ DefaultRecorder（default_recorder.py:55）分发 exporter → close。SingletonMeta（singleton.py:8）保证"每进程一个 Provider"：类级 `_instances` dict + RLock 双检锁（singleton.py:19-20,36-42），`__call__` 直接 raise TypeError（singleton.py:22-25）封死直接实例化。

## 设计决策

1. **单例的理由写在 docstring**（one_logger_provider.py:20-24）：Recorder 有状态、不单例就得把实例在应用里到处穿，采纳成本高。
2. **lazy 配置字段**（config.py:109 的 world_size_or_fn）：分布式训练的 world_size 在初始化时可能未知，留 Callable 接口让求值时机后移。
3. **Attributes 弱类型 + 强校验**：AttributeValue 只收原始类型与同质列表（attributes.py:17,29-33），注释明说为 wandb/OTel 序列化友好。
4. **版本读取双通道**：version.py:13-22 向上遍历找 pyproject.toml，兜底 importlib.metadata。
5. **双时钟时间戳**：TracingTimestamp（time.py:11）同时存 epoch 墙钟与 perf_counter（time.py:15-22），人读与高精度计时两不误。

## 新人提示

先读 one_logger_provider.py 全文（95 行含完整 docstring 示例）再看任何实现；诊断导入问题时记得这是命名空间包——`nv_one_logger/__init__.py` 不存在是特性不是缺陷；图谱/scanner 对跨发行版 import 天然盲（本仓 imports 边靠人工补扫），分析依赖时以五个 pyproject 为准绳而非目录树。

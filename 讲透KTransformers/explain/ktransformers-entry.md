# ktransformers.py + archive/ktransformers/__init__.py：框架入口的世代交替

> 基于知识图谱（commit 31985f4）。先钉事实：老教程说的肥 `__init__.py`（TransformerLayer+`ktransformers()` 组装器）在本快照已不存在，但代码现状足以还原演进全貌。

## 1. 角色定位

两文件同属 `layer:framework-core`（18 节点），却分属两世代：

- 根 `ktransformers.py`（35 行）：**新生代入口**。退化为"版本+能力探测"薄壳，内核整体迁往 `kt-kernel`（图谱 kt-kernel 两层共 207 节点，全仓最大板块）。`pyproject.toml` 明写 `py-modules=["ktransformers"]`；`setup.py` 的 `install_requires` 仅 `kt-kernel=={__version__}`——**pip install ktransformers 实际装的是 kt-kernel**。
- `archive/ktransformers/__init__.py`（11 行）：**旧世代遗骸**，仅剩 `__version__="0.4.1"`，图谱摘要"归档占位入口，无任何导入逻辑"。旧 Python 框架整树搬进 `archive/` 保尸。

## 2. 内部结构

`ktransformers.py` 三段：①版本双通道（L14-24）：`_read_repo_version()` 用 `exec` 读 `version.py`（仅 `__version__="0.7.0.post1"`，注释声明与 kt-kernel 共享）；主路径优先 `importlib.metadata.version()`，`PackageNotFoundError` 才回退源码。②`has_sft_support()`（L27-32）try-import `kt_kernel.sft`，裸 `except Exception` 返回 False。③`__all__` 两符号（L35）即全部 API。

旧组装器遗产散落三处：`archive/ktransformers/local_chat.py::local_chat()`（L76）是手工装配活化石，L60-64 架构→YAML 规则表（如 `DeepseekV3ForCausalLM→DeepSeek-V3-Chat.yaml`）即当年 `ktransformers(config, models, optimize_rules)` 的等价物；`server/backend/interfaces/ktransformers.py` L57 `__init__` 调 `optimize_and_load_gguf`（L99）做 YAML 装配；新生代 `kt-kernel/python/cli/main.py`——typer 的 `kt` CLI，九命令（run/chat/quant/bench/doctor/model/config/sft/version）。

## 3. 外部连接

`file:ktransformers.py` 出边仅 3 条：`depends_on→version.py`、`depends_on→kt-kernel/python/sft/__init__.py`、`exports→has_sft_support`，全仓耦合最少；**入边为零**——消费者是 pip 元数据与构建系统而非代码。archive 的 `__init__.py` 入边仅两条 `documents`（两份 README）；archive 树内残余 `import ktransformers.optimize.optimize`（interfaces/ktransformers.py L23）树内自洽、脱离 archive 布局即断链，证明 archive 只读不活。

## 4. 数据流

源码 checkout：`import ktransformers` → 元数据查询抛 `PackageNotFoundError` → `_read_repo_version()` 得 `0.7.0.post1`。`has_sft_support()` → 运行时 import `kt_kernel.sft`（需 `pip install ktransformers[sft]`）。真正运行链不走本文件：新链 `kt run`；旧链 `local_chat` 或 `server/main.py::main()`，都汇到 `optimize_and_load_gguf` 装配+GGUF 加载。

## 5. 设计决策

- **薄壳而非删包**：保住 `import ktransformers` 命名延续与 PyPI 占位，依赖转置零破坏迁移；extras（`[sft]`/`[sglang]`）用 pip 标准机制而非自研插件系统。
- **整树 archive 而不删**：保留 0.4.x 全量实现供对照迁移；两代版本号（0.4.1/0.7.0.post1）并存即演进年轮。
- **lazy import 探测**：可选依赖失败推迟到运行时布尔化，主链永远可装。
- 毛边：`exec` 读版本不如 AST 安全；裸 `except Exception` 吞掉 ABI 崩溃等真实错误。

## 6. 新人提示

- 切入点：先读 `setup.py`+`pyproject.toml`，再进 `kt-kernel/python/__init__.py` 看 CPU 变体自动探测（`__cpu_variant__`，AMX/AVX512/AVX2）——新内核真正门面。
- 易错点：①拿旧教程在 HEAD 找 `ktransformers()` 必扑空，先 `ls archive/`；②已安装环境 `__version__` 来自元数据，发版窗口期与 `version.py` 可能不一致；③改 `version.py` 须同步 kt-kernel 侧。
- 测试：`archive/ktransformers/local_chat_test.py` 是旧链唯一冒烟；新 CLI 靠 `kt doctor` 自检。

# 07 · config 系统：一份 YAML 驱动的反射装载中枢

## 角色定位

`backend/packages/harness/deerflow/config/` 是整个 harness 的"器官分化指挥书"。DeerFlow 把"装了哪些模型、哪些工具、沙箱用什么实现"全部从代码里抽出来，塞进仓根的 `config.yaml`（模板为 `config.example.yaml`），运行时靠两条腿走路：pydantic 模型做结构校验，`deerflow/reflection/resolvers.py` 做运行时反射装载。仓库图谱中 `config.example.yaml` 共发出 18 条 configures 边，指向 models 工厂、sandbox provider、community 工具等装载目标——它是全仓唯一一份"声明即架构"的文件：改一行 `use:` 路径，agent 的模型供应商、沙箱隔离级别就整个换掉。

该包共 16 个文件 1455 行，其中 `__init__.py` 只有 19 行，却是全仓最高频的 barrel：从 6 个子模块导入并导出 10 个符号（`config/__init__.py:1-6`），全仓 13 个非测试文件经 `from deerflow.config import ...` 消费它——从 `models/factory.py`、`sandbox/sandbox_provider.py` 到 `app/gateway/routers/models.py`（App 层经 barrel 而非直连模块路径，见 `backend/app/gateway/routers/models.py:1` 的导入形态）。barrel 让 config 内部拆分重构不破坏消费方。

## 内部结构

包内是一层"主配置 + 副配置"结构：

- **app_config.py（273 行）**：核心巨类 `AppConfig`（`app_config.py:26`），持有 models/sandbox/tools/tool_groups/skills/extensions/checkpointer 七大字段（`app_config.py:29-36`）。模块级 `load_dotenv()`（`app_config.py:21`）保证 .env 在任何配置读取前生效。
- **单例三件套**：`get_app_config()` 惰性缓存（`app_config.py:223-232`）、`reload_app_config()` 热重载（`app_config.py:235`）、`reset_app_config()`/`set_app_config()` 供测试注入（`app_config.py:253-273`）。
- **副配置模块**：memory_config、tracing_config、title_config、summarization_config、subagents_config、checkpointer_config 各自持有独立的模块级全局实例与 `load_*_from_dict` 装载器，由 `from_file` 在解析主 YAML 时顺带灌入（`app_config.py:89-106` 的五段 if 块）。
- **extensions_config.py**：独立文件 `extensions_config.json` 的宿主，`alias="mcpServers"`（`extensions_config.py:61`）兼容 camelCase JSON 键，`ConfigDict(extra="allow")` 允许携带未知字段。
- **paths.py**：所有磁盘路径的推导中心（详见 08 篇消费语境），`host_base_dir` 支持 DooD 场景 `DEER_FLOW_HOST_BASE_DIR` 覆盖（`paths.py:42-55`）。

配置文件定位四级优先链在 `resolve_config_path`（`app_config.py:39-65`）：显式参数 > `DEER_FLOW_CONFIG_PATH` 环境变量 > CWD 的 config.yaml > 父目录 config.yaml——最后一级正是"推荐放仓根、命令在 backend/ 下跑"这一工作流的技术支撑。

## 外部连接

**向下：reflection 反射装载。** 配置里所有 `use:` 字段形如 `package.module:Class`，由 `resolve_variable` 解析——先用 `rsplit(":", 1)` 切出模块与符号（`resolvers.py:44`），`import_module` 动态加载（`resolvers.py:49`），再 `getattr` 取符号并做 isinstance 校验（`resolvers.py:59-68`）。`resolve_class` 在此之上强制子类检查（`resolvers.py:92-93`）：`sandbox.use` 指向的类必须继承 `SandboxProvider`，防止配置笔误指向无关类。两个函数都是 PEP 695 泛型语法 `def resolve_variable[T]`（`resolvers.py:25`，Python 3.12+），调用方 `create_chat_model[T]` 拿到的是已收窄类型。由于 import 目标来自运行时配置，静态分析天然不可见——这是图谱 scanner 对 config→装载目标只能按语义发 configures 边、无法发 imports 边的根本原因。

**向上：三类消费者。** ① models/factory.py 按 `models[].use` 反射出 ChatModel 类；② tools/tools.py 按 `tools[].use` 装配工具清单（`config.example.yaml:170` 的 `deerflow.community.tavily.tools:web_search_tool` 到 `:225` 的 `bash_tool` 共 9 个默认工具）；③ sandbox 双 provider 切换——`config.example.yaml:235` 默认 `deerflow.sandbox.local:LocalSandboxProvider`，`:243` 注释给出 `deerflow.community.aio_sandbox:AioSandboxProvider` 容器隔离选项，`:281` 再给 provisioner/K8s 三态。

**环境变量双向渗透。** 出向：`resolve_env_variables` 递归把 `$` 前缀字符串替换为环境变量值，缺失即抛 ValueError（`app_config.py:173-178`）；入向：tracing_config 的四条独立候选链 `LANGSMITH_* > LANGCHAIN_*`（`tracing_config.py:81-84`），enabled 是三候选、api_key/project/endpoint 各双候选，兼容新旧两代 LangSmith 命名。

## 数据流

冷启动一次完整装载：`get_app_config()` → `AppConfig.from_file()`（`app_config.py:68`）→ 四步流水：① `yaml.safe_load` 读入（`app_config.py:80-81`）；② `_check_config_version` 版本比对（`app_config.py:84`）——向上最多搜 5 级目录找 `config.example.yaml`（`app_config.py:130`），用户 `config_version` 缺失按 0 处理（`app_config.py:123`），落后则 warning 提示 `make config-upgrade`（`app_config.py:154-158`）；③ `resolve_env_variables` 全树展开 env 引用（`app_config.py:86`）；④ 五段 if 依次灌入 title/summarization/memory/subagents/checkpointer 副配置（`app_config.py:89-106`），随后强制从磁盘读 extensions_config.json 覆盖 extensions 字段（`app_config.py:109-110`）——注意这一步绕过了单例缓存的 extensions getter，Gateway 进程对 MCP 配置的修改经 mtime 检测才被 LangGraph 进程感知，两进程各持一份内存配置。

装载完成后配置进入"读多写少"稳态：模型/工具装配只在 agent 构建时反射一次；memory_config 等副配置被各自子系统直接读全局实例（`memory_config.py:61` 的 `_memory_config`）；唯一的热更新路径是 `reload_app_config` 与 skills/extensions 的专用重载。

## 设计决策

**① 双形态字符串契约。** `use: module:Class` 与 `$ENV_VAR` 两种微语言并存于同一份 YAML：前者是"延迟到运行时的 import 语句"，后者是"延迟到运行时的环境读取"。好处是模板文件可以覆盖所有可选组合（config.example.yaml 里三套沙箱方案全以注释形态躺在文件里随时取消注释），代价是 IDE 对配置的静态检查完全失效，typo 只能在运行时爆。

**② 版本化配置迁移。** `config_version: 1`（`config.example.yaml:15`）+ 五级向上搜索 + `make config-upgrade`（scripts/config-upgrade.sh 的 heredoc Python 负责合并缺失字段），把"上游加字段、用户老配置"这一 YAML 项目的经典痛点做成了带警告的半自动流程。

**③ 副配置的模块级单例 vs AppConfig 的惰性单例。** memory/tracing 等用"导入即默认实例"（`memory_config.py:61`），AppConfig 用"首次访问才读文件"（`app_config.py:230`）。后者让测试可以 `reset_app_config()` 清缓存换配置（`app_config.py:253`），前者则被 from_file 的副作用装载覆写——两种生命周期并存是因为副配置需要在 AppConfig 校验失败时也能独立可用（tracing 只看环境变量，完全不需要 config.yaml 存在，`tracing_config.py:79-86` 的构造不依赖任何文件）。

**④ skills_config 的循环依赖豁免。** `get_skills_path` 在未配置 path 时才在函数体内 `from deerflow.skills.loader import get_skills_root_path`（`skills_config.py:34`）——config 是依赖链最底层，skills 包却反向依赖 config，这条延迟 import 是环的唯一断点，图谱批分析时曾作为 scanner 漏报被手工补边。

## 新人提示

- 改配置先看 `config.example.yaml` 而不是猜 schema：它就是权威注释文档，`config_version` 落后会有启动警告但**不阻断**，别误以为没生效。
- `use:` 路径写错时的报错是可操作的：resolvers 会给出 `uv add langchain-anthropic` 之类的安装提示（`resolvers.py:11-22` 的 `MODULE_TO_PACKAGE_HINTS` 映射表，`resolvers.py:3-8`），甚至能穿透传递依赖报错（配置 `langchain_google_genai` 但缺的是底层 `google` 包时仍提示装 `langchain-google-genai`）。
- `$ENV_VAR` 引用不存在的变量是硬错误（ValueError），不是静默空串——排查"配置明明写了却起不来"先查 .env 是否被 `load_dotenv()`（`app_config.py:21`）加载到。
- memory 的 `storage_path` 有迁移陷阱：相对路径现在按 `Paths.base_dir` 解析而非 backend 工作目录，Field description 里原文记录了这一语义变更（`memory_config.py:15-24`），老用户从 `.deer-flow/memory.json` 升级后文件会"换位置"。
- 想加新配置节：在 config/ 下建副配置模块 + 模块级默认实例 + `load_*_from_dict`，然后在 `app_config.py:89-106` 的 if 链上加一段，最后 bump `config.example.yaml` 的 config_version——三处缺一不可，漏 bump 版本则老用户永远收不到升级提示。

# 02 · Registry 体系：五注册表与容器横跨装配

## 角色定位

`backend/app/services/` 的注册表家族是后端数据层：把"上游 DataFlow 包的反射信息"与"本地 yaml/json 持久化"封装成服务对象供端点消费。核心五个——`operator_registry.py`（算子）、`dataset_registry.py`（数据集）、`prompt_registry.py`（内置 Prompt）、`serving_registry.py`（LLM Serving）、`pipeline_registry.py`（1458 行最大）；旁系 task/text2sql×2/json_schema/user_prompt。它们都不全局实例化，而由 `core/container.py` 的 `AppContainer.init()`（L20-55）统一装配——顺序完全显式，是对"模块级全局初始化顺序不可控"的根治。

## 内部结构

五注册表呈现三种形态。**反射型**：`OperatorRegistry`（operator_registry.py:144）持上游 `OPERATOR_REGISTRY` 引用，`__init__` 触发全量加载（L154-157）；`dump_ops_to_json`（L211）用 `inspect.signature` 逐算子提取 `__init__`/`run` 参数、`ALLOWED_PROMPTS`、三级分类落 `ops.{lang}.json` 缓存——重操作，只在 startup 钩子（main.py:61-69）跑。`PromptRegistry`（prompt_registry.py:56）同样反射 `PROMPT_REGISTRY`，`inspect.getsource` 直接返回 Prompt 类源码（L106）。**文件型**：`DatasetRegistry`（dataset_registry.py:59）以 yaml 为真源，`scan_all_datasets`（L66）遍历 core 目录 example_data 批量注册；`ServingRegistry`（serving_registry.py:26）管 API Serving 实例，`get_serving_classes`（L100）反射 init 参数供前端表单，`_update` L70 明令 cls_name 不许改。**混合型**：`PipelineRegistry`（pipeline_registry.py:235）文件持久化 + `PipelineFileAnalyzer`（L19，frozen dataclass）AST 解析 pipeline 源码——`execution_order`（L35）按 forward() 里 `self.xxx.run()` 出现序提取算子链，是"从代码反向出图"的核心。

## 外部连接

上游依赖 `dataflow.utils.registry` 的 `OPERATOR_REGISTRY`/`PROMPT_REGISTRY`（operator_registry.py:6）——CLAUDE.md 钉版"只能扩展不能重定义"。下游被 endpoints/operators、datasets、prompts、serving、pipelines 经 container 消费。路径集中在 `core/config.py`：L21-32 定义 9 个数据文件路径；L36-52 的 `_PRESET_PIPELINE_NAME_WHITELIST`（15 个模板名）决定前端模板可见性。

## 数据流

算子线：上游 import 注册 → `OperatorRegistry` 拉全量 → startup dump 双语 json → 前端读 `/api/v1/operators/` 组装样式分组。数据集线：example_data 扫描或 Agent 经 MCP `register_dataset` → yaml 持久化 → pipeline 按 id 引用。Prompt 线：Prompts 页 `list_prompt_info`（prompt_registry.py:125）看 docstring/参数/反向 operator 映射，点开看类源码。

## 设计决策（含批判）

- **勘误·user_prompt_registry 设计未兑现**：docstring L21-22 承诺"算子参数出现 `user_prompt:<id>` 时由 `param_coercion.resolve_user_prompt_ref(...)` 解引用"，但全仓 grep 两符号只命中 docstring 自身——函数零实现、前缀零消费者。对照 `param_coercion.py:16` 的 `schema_ref:` 前缀有完整实现（L19-40 惰性查 JsonSchemaManager），用户 prompt 的运行时解引用链路是断的：CRUD/preview 可用，接进算子参数停留在设计文档。
- **勘误·L12-14 绝对路径丢弃左侧**：operator_registry.py:13 `OPS_JSON_PATH = BACKEND_DIR / settings.OPS_JSON_PATH`——settings 值在 config.py:28 是 `os.path.join(BASE_DIR,...)` 的**绝对路径**，pathlib 遇绝对右操作数丢弃左侧 `BACKEND_DIR`。看似相对拼接实为恒等（两处 BASE_DIR 恰好同值才不出错），纯误导；L14 `RESOURCE_DIR` 再往下传。正确写法是直接 `Path(settings.OPS_JSON_PATH)`。
- **自愈边界**：yaml 注册表自带 `_ensure()` 空文件自愈（dataset_registry.py:115、serving_registry.py:32），首启零配置。
- **批判·巨型文件**：pipeline_registry.py 1458 行塞下 AST 分析+校验+模板过滤+CRUD；`get_prompts` 算子不存在时返回 None（prompt_registry.py:74-75）而非抛错，端点层得自己判空。
- **反射即契约**：参数文档、serving 表单全来自 inspect 反射而非显式 schema——上游改签名前端自动跟上，但默认值不可序列化时靠 `_safe_json_val` str() 兜底（operator_registry.py:19-33），类型信息丢失。

## 新人提示

找"数据在哪"：先看 `config.py` 路径常量，再顺 container 槽位进注册表。算子面板缺参数，跑 `refresh()`+`dump_ops_to_json` 而非改代码。写新注册表照三模板选一（反射=PromptRegistry、文件=ServingRegistry、复合=PipelineRegistry），务必挂进 `AppContainer.init()`。别信 user_prompt 的 docstring，先 grep 消费者。

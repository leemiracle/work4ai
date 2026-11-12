# 01 · 入口与 dataclass↔argparse 桥：inspector_app.py + parse_agruments_helpers.py

## 角色定位

这一对文件是 NeMo-Inspector 的"点火系统"。`inspector_app.py`（67 行）是应用主函数：装 CLI、装配配置、点燃 Dash 服务；`parse_agruments_helpers.py`（133 行）是一个可独立复用的通用桥——把任意 dataclass 的字段定义递归翻译成 argparse 参数，再把解析结果递归翻译回 dataclass 实例。InspectorConfig 自身（`settings/inspector_config.py:40-50`）只声明三个字段，CLI 的全部复杂度都被桥吸收。`setup.py:43-47` 注册的 console_scripts 入口 `nemo_inspector` 与 `__main__.py:15-18` 的 `python -m nemo_inspector` 两条启动路径最终都落在 `main()`（inspector_app.py:35）。

## 内部结构

**main() 的十行流水线**（inspector_app.py:35-62）：

1. `signal.signal(signal.SIGALRM, signal.SIG_IGN)`（:36）——启动即屏蔽闹钟信号；
2. `add_arguments_from_dataclass(parser, InspectorConfig, enforce_required=False, use_type_defaults=True)`（:40-45）——两个开关的含义：不强求必填（本工具允许空跑起 UI）、缺省值按字段类型构造而非 None；
3. `parser.parse_args()` 后 `vars(args)` 转 dict（:47-48）；
4. `create_dataclass_from_args(InspectorConfig, args_dict)` + `dataclasses.asdict`（:50）——重建并立即拍平成纯 dict；
5. `cfg.setdefault("code_tags", {})` 后 `{**CODE_SEPARATORS, **cfg["code_tags"]}`（:51-52）——用户传的 code 标记与 llama 风格四标记默认值（`configurations.py:15-21`）合并，用户键覆盖默认键；
6. `args_postproccessing(cfg)`（:53）——目前只做 `input_file` 的 str 化（`parse_agruments_helpers.py:129-132`），而 InspectorConfig 根本没有 input_file 字段，此键恒为 `""`（上游 monorepo 孤儿链路，见 ONBOARDING §8.6）；
7. `from nemo_inspector.callbacks import app`（:54）——**延迟 import**：callbacks 包在 import 时创建全局 Dash app 并注册全部回调（`callbacks/__init__.py:20-30`），必须发生在 argparse 之后以保持入口纯粹；
8. `app.server.config.update({"nemo_inspector": cfg})`（:56）——配置走 Flask config 通道，运行期由 `utils/common.py:106/:289/:397` 的 `current_app.config` 读取；
9. `app.run(host="localhost", port="8080")`（:59-62）——host 写死，是 exec 注入面唯一的安全围栏。

**桥的正向：dataclass→argparse**（`add_arguments_from_dataclass`，:30-95）。逐字段处理，四类分派：

- 嵌套 dataclass（:46-55）：递归加 `prefix.`（外层 `field_name.`），CLI 上出现 `--outer.inner` 型参数——本仓 InspectorConfig 无嵌套，但桥按通用件设计；
- bool（:79-84）：`action="store_true"`——注意语义缺口：store_true 只能"打开"，CLI 无法显式传 false（默认值由 `get_type_default(bool)()` 得 False，:69-70）；
- dict（:85-91）：`nargs="*"` + 自定义 `ParseDict` action——`ParseDict.__call__`（:22-27）把每个 `k=v` 串 split 后塞 dict，**value 一律是 str**，不做类型还原；
- 其余（:92-95）：`type=field_type` 直接让 argparse 做构造转换。

类型先行经 `resolve_union_or_any`（:60）洗过——它委托 `resolve_type`（`utils/common.py:421-430`）：泛型取 `get_origin`（List[str]→list），普通类原样，Any 等特殊形态降级 str。必需性判定在 :63（无 default 且无 default_factory 且 use_default），最终经内层 `add_argument` 闭包（:66-74）统一注入 default 与 required。

**桥的反向：args→dataclass**（`create_dataclass_from_args`，:98-126）。与正向完全对称的递归（嵌套在 :106-113），缺席字段三级回退：field.default（:119-120）→ field.default_factory()（:121-122）→ `get_type_default(field_type)`（:124，构造失败返回 None，`utils/common.py:433-437`）。

## 外部连接

上游：`__main__.py`、console_scripts。下游：InspectorConfig（其 `model_prediction` 经 `__post_init__` 展开成具体文件列表，`inspector_config.py:46-50`）；Flask config 消费群（utils/common 三处）；`get_type_default`/`resolve_union_or_any` 反向依赖 utils/common.py——注意方向是 settings 层工具借 utils 层的 typing 工具，桥文件虽在包根却 import utils（:19）。`inspector_app.py:27` 还有一句 `sys.path.append(str(Path(__file__).parents[1]))`——把仓根塞进 sys.path，使从任意 cwd 以脚本方式运行也能定位 nemo_inspector 包。

## 数据流

命令行字符串 → argparse 命名空间 → `vars()` dict → 递归重建 InspectorConfig（三级回退兜底）→ `asdict` 拍平 → code_tags 合并默认分隔符 → postprocess（input_file 死键）→ Flask config["nemo_inspector"] → 全仓运行期读取。一次装配，全程只读。典型输入形如 `python -m nemo_inspector --model_prediction modelA=runs/a.jsonl modelB='runs/glob/*.jsonl'`——ParseDict 收串，InspectorConfig 展开路径，Dash 起来后 `get_available_models()`（utils/common.py:395-404）把同一配置再变成模型注册表。

## 设计决策

- **桥与配置分离**：argparse 的机械翻译全部沉在通用桥里，InspectorConfig 保持纯 dataclass——加一个配置字段零成本获得 CLI 支持，这是"声明式配置"的本益。
- **asdict 后再注入**（:50-52）：重建后立即 `dataclasses.asdict`，后续全走 dict——下游（Flask config、回调）不必再懂 dataclass；代价是类型信息在入口处就丢光。
- **延迟 import**（:54）而非模块顶：保证"import inspector_app"无副作用，也让 argparse 错误能在 Dash app 创建前干净报出。
- **两个开关的组合**（:43-44）：`enforce_required=False` + `use_type_defaults=True` 意味着"所有参数可选、缺省值取类型零值"——匹配"本地工具先起 UI 再说"的产品定位。
- **已知妥协**：ParseDict 的 value 全 str（:26）；bool 无法显式传 false（:80）；input_file 死键无人清理。三处都是上游拆仓的欠账而非刻意设计。

## 新人提示

- 读配置问题先分清三层：CLI 解析层（桥）、dataclass 层（InspectorConfig+__post_init__ 展开）、运行期层（Flask config）——同一个值在三层形态不同（str→展开 list→dict 内的 key）。
- 调试 CLI 最快的办法是直接 `python -m nemo_inspector --help`，所有参数 help 都由桥按 `f"{field_name} flag (default: ...)"` 生成（:77、:82、:89、:94）。
- 给 InspectorConfig 加字段后记得 `python_requires>=3.10`（setup.py:48）与 `kw_only=True`（inspector_config.py:40）的约束：新字段无需关心声明顺序。
- 想复用这个桥：它对嵌套 dataclass、泛型、Union/Any 的降级都写好了，唯独别指望 dict 字段保类型。
- 文件名 `parse_agruments_helpers` 的拼写笔误（agruments）是历史事实，改名要动 inspector_app.py:21-25 的 import——修之前先权衡值不值。

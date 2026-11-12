# 01 · Registry 核心：四族组件的户籍处与装配线

## 角色定位

`src/dataflex/core/registry.py` 全文只有 33 行，却是整个 DataFlex 的心智模型入口：Selector/Mixer/Weighter/Reorder 四族组件全部经它注册、全部经它实例化。DataFlex（NeurIPS 2026 D&B Track 录用）是挂在 LlamaFactory 上的数据为中心训练系统，"组件可插拔"这件事的地基就是这一个类加一个全局单例。读懂它，后面五篇的所有组件族都是同一个故事的不同变体。

## 内部结构

`Registry` 类（registry.py:4）内部是一张两级字典 `_store: kind → name → class`（:6）。三个方法各司其职：

- `register(kind, name)`（:8-15）是装饰器工厂：把类挂进字典，重名直接 `ValueError`（:11-12）。这保证了两个文件注册同名 selector 时在 import 阶段就炸，而不是训练到一半才发现。
- `get`（:17-18）纯查表。
- `build`（:20-27）是装配核心，三步：先合并配置 `{**cfg, **runtime}`，**runtime 依赖优先**（:23）；再用 `inspect.signature` 拿构造函数参数名集合（:24-25）；最后只把组件**声明过的**参数喂进去（:26）。这就是"声明什么收什么"的依赖注入。

文件尾部 `REGISTRY = Registry()`（:29）建全局单例，随后四个一行装饰器 `register_selector/register_mixer/register_weighter/register_reorder`（:30-33）分别对应四个 kind。

## 外部连接

**配置侧**：`utils/load_component.py` 的 `load_component(type, cfg_file, name, runtime_vars)`（:35）从 YAML 读 `selectors:`/`mixers:` 等桶，取 `params` 子字典，并做 `${var}` 占位符替换（:44-53）。还有一张 `_BUCKET_ALIASES`（:10-12）把旧拼写 `reorderers:` 静默迁移到 `reorders:`——重命名后的向后兼容只警告不报错。

**注册表本体**是 `src/dataflex/configs/components.yaml`，五族 41 预设：selectors 15、mixers 5、weighters 7、reorders 10、pipelines 4。注意 `pipelines:` 是 lego 组合子系统的桶（见第 5 篇），不经 Registry 注册类，只存 stage 清单。

**消费侧**：四个 trainer 的 `__init__` 都是同一模式——`load_component` 拿参数 → 组 runtime 四依赖（dataset/eval_dataset/accelerator/data_collator）→ `REGISTRY.build`，例如 select_trainer.py:56-71。

**版本**：`version.py:1` 钉 `__version__ = "1.1.0"`，pyproject.toml:72 以 `dynamic = ["version"]` 引用同一处；`cli.py:225` 打招呼时用 `importlib.metadata` 反查、查不到兜底 `unknown`。

## 数据流

一次 `dataflex-cli train config.yaml` 的组件生命周期：YAML 桶名+`component_name` → `load_component` 返回 params dict → trainer 注入 runtime 依赖 → `build` 按签名过滤 → 组件实例进入训练循环。签名过滤的妙处在 coincide 上最明显：`CoincideSelector.__init__` **故意不声明** `eval_dataset` 参数（coincide_selector.py:49-58 的 docstring 明说），于是 registry 永远不会注入它——组件用"不声明"表达"不需要"，无需任何配置开关。

## 设计决策（含批判）

1. **签名过滤式注入**：静态组件（random/tsds）自动忽略动态依赖，新增 runtime 依赖不必改任何旧组件。代价是继承链上的参数必须逐级重复声明——`TracInSelector.__init__` 里那一排 ClusterBase 参数就是纯为 registry 过滤服务的（tracin_selector.py:41-47 注释自认"registry 按名字过滤需要声明"），父类 `**kwargs` 透传在这里帮不上忙。
2. **单例+import 副作用注册**：`import dataflex.train.selector`（select_trainer.py:39）本身就完成全部注册，代价是"忘了在 `__init__.py` 里 import 就等于组件不存在"，且报错形态是查无此名而非明确提示。
3. **批判**：components.yaml 单文件 647 行五族混居，族内预设一多就难维护；`build` 只认 `__init__` 签名，对 dataclass 风格或工厂函数组件不友好；41 预设里有调试残留（`odm` 的 `initial_proportions: [0.5, 0.5] # debug`，components.yaml:267）。

## 新人提示

新增组件三步：写类→挂 `@register_xxx("name")`→components.yaml 加预设，官方教程在 `skills/how_to_add_algorithm.md`。两个必踩坑：忘了 `__init__.py` 导入导致注册不生效；构造参数名与 YAML params 键不一致会被静默过滤掉（不报错、用默认值），排查时先 diff 两边名字。跑通第一个实验用 `examples/test/test_select.yaml`，数据用仓内 `data/` 的 demo 集。

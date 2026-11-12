# 04 · registry 与 LazyLoader——几百算子的零成本懒加载体系

## 角色定位

`utils/registry.py` 是"名称→类"的枢纽：`Registry` 注册表 + `LazyLoader` 模块替身，支撑 dataflow/operators 下十几个子包、数百个算子类在 `import dataflow` 时零加载成本，第一次真正取用时才载入对应文件。最终图谱里 `registry.py` 有 214 条入边（几乎每个算子文件都 import 它拿 `OPERATOR_REGISTRY`），是 utils 包被引用最广的文件。

## 内部结构

`Registry`（`registry.py:34`）：`__init__` 直接 `os.listdir` 扫 `dataflow/{name}/` 子包名建 `loader_map`（`registry.py:67-74`）；`get()` 未命中先 `_init_loaders` 逐个 import 子包（`registry.py:108-109`），再对每个模块 `getattr(module_lib, name)`（`registry.py:114`）——这一下会触发 LazyLoader 真加载，全程只 AttributeError 被吞、其余异常上抛（`registry.py:117-121`）；`apply_whitelist` 白名单就地裁剪并出报告（`registry.py:131-206`）；`__repr__` 用 rich 表格打印全部注册项（`registry.py:217-229`）。`generate_import_structure_from_type_checking`（`registry.py:15-31`）是声明的解析器：ast.parse 源码，找 `if TYPE_CHECKING:` 块里的 `ImportFrom`，把类名映射到 `(文件路径, 类名)`（`registry.py:28-29`）。`LazyLoader`（`registry.py:261`）是 ModuleType 子类：`__all__` 即可加载清单（`registry.py:275`）；`__getattr__`（`registry.py:343-364`）查缓存→查映射→`_load_class_from_file`（`registry.py:281`），后者把相对路径重建成合法模块名（`registry.py:296-302`）、为父包注入 dummy 模块（`registry.py:306-316`）、`spec_from_file_location` 执行文件（`registry.py:317-325`），找不到类名抛 AttributeError（`registry.py:339-341`）。

## 外部连接

两个全局注册表在文件尾：`OPERATOR_REGISTRY`（`registry.py:257`）与 `PROMPT_REGISTRY`（`registry.py:259`）。operators 的 14 个子包 `__init__.py` 全用同一双态模板：`if TYPE_CHECKING:` 分支给 IDE/mypy 看完整 import 面（`general_text/__init__.py:1-71`），`else:` 分支运行时解析声明并把 `sys.modules[__name__]` 整个替换成 LazyLoader（`general_text/__init__.py:72-79`，`text_pt/__init__.py:25-31` 同构）。图谱事实：scanner 对 TYPE_CHECKING 静态导入与 sys.modules 运行时替换双盲，这批 imports 边全部靠 AST 重扫补齐。

## 数据流

用户写 `from dataflow.operators.general_text import NgramFilter` → 子包 `__init__` 执行后 sys.modules 中该包已被 LazyLoader 顶替 → 属性访问进 `__getattr__` → 加载 `filter/ngram_filter.py` 并执行其中的 `@OPERATOR_REGISTRY.register()` → 类对象返回。经注册表的路径同构，入口换成 `OPERATOR_REGISTRY.get("NgramFilter")`：注册表平时是空的，靠 get 未命中时批量 import 子包、算子文件自注册回填（`registry.py:108-116`）。

## 设计决策

该模式源自 HuggingFace transformers 的 `_LazyModule`：声明面（TYPE_CHECKING）与运行时面共享同一份 import 语句，单一事实源、IDE 补全不损。批判与甄别有三：其一，`text_pt/filter/__init__.py` 整文件全注释——旧版手写 `_import_structure` 映射表的尸体，指向的 `dataflow/operators/filter/` 旧路径已不存在（真实 filter 文件如今在 `general_text/filter/` 与 `text_pt/filter/*.py`）；它无害的原因恰是"全注释"：Python 导入该子包时执行的是空 `__init__`，懒加载只挂在 text_pt 顶层。其二，`PROMPT_REGISTRY=Registry('prompts')` 是潜在雷：`dataflow/prompts/` 下是 .py 文件不是子包，`_init_loaders` 会拼出 `dataflow.prompts.core_text.py` 这种非法模块名（`registry.py:78`）import 必炸——只因主代码从不调 `PROMPT_REGISTRY.get` 才潜伏。其三，逐模块 getattr 试错的报错定位差：类名拼错只能得到笼统 KeyError（`registry.py:122-123`），不会告诉你哪个包里差点命中。

## 新人提示

新增算子的正确姿势：写好算子文件（挂 `@OPERATOR_REGISTRY.register()`），再在所属子包 `__init__.py` 的 TYPE_CHECKING 块加一行 import——绝不手写映射表，死代码就是反例。排查"No object named"先查三件事：装饰器漏挂、包 `__init__` 漏声明、类名拼写。调试可打 `print(OPERATOR_REGISTRY)` 看注册面；`apply_whitelist` 裁剪不可逆，用前先留快照。看到 `text_pt/filter/__init__.py` 全是注释不要慌着"修复"——它是刻意留存的化石，但新代码别再往里加东西。

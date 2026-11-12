# 02 · tests/test_import_rules.py：惰性 facade 的架构 fitness function

> 定位：这是一个**测试文件**，但它测的不是行为而是**架构**。`agent_shield/tests/test_import_rules.py` 用六个测试把整个包的 import 布局钉死成"包根零导出零加载、子模块各自为 facade、跨子模块只走对方根、兄弟项目单向依赖"。它是理解本仓静态分析（understand scanner）为什么几乎找不到 import 边的钥匙，也是"用 CI 守卫架构决策"的教科书样本。

## 一、角色定位

模块 docstring 开宗明义（`agent_shield/tests/test_import_rules.py:3-12`）：

```
- The package root exports nothing and loads no submodule on import.
- Each submodule is its own facade; callers import from ``agent_shield.<sub>``.
- Inside a submodule, imports are relative.  Across submodules, only the other
  submodule's root may be imported (never its internals).
- Code outside agent_shield (jiuwenbox, agent_ssas) imports at most one level
  below the package root, and agent_shield never imports those projects.
```

四条规则对应一个清晰的目标：**强制惰性 facade**。agent_shield 是被嵌进每个工具进程的安全库，`import agent_shield` 的代价必须是零——不加载任何子模块（不触发 torch/tree-sitter 等重依赖的传递导入）、不绑定任何名字。只有真正用到 `tool_permission` 或 `detection` 的人才付出加载成本。

这类测试在架构圈叫 **fitness function**（《Building Evolutionary Architectures》术语）：不验证业务正确性，验证"架构约束没有被后续提交侵蚀"。每次 `pytest` 都是一次架构审查。

它同时解释了 understand 流水线的一个现象：scanner 的 `batchImportData`/`neighborMap` 对本仓几乎全空。不是工具坏了——是**架构本身就在消灭可静态发现的 import 边**（详见第六节）。

## 二、内部结构

文件本身只有 115 行，一个常量、两个工具函数、六个测试：

- `SUBMODULES = ("tool_permission", "detection")`（`test_import_rules.py:27`）——受检子模块白名单；
- `_python_files(root)`（L30-34）：`rglob("*.py")` 遍历，跳过 `__pycache__` 与 `build` 目录；
- `_imports(path)`（L37-46）：`ast.parse` 后 `ast.walk`，对 `ImportFrom` 产出 `(module, level)`、对 `Import` 产出每个 alias 的 `(name, 0)`——**level 字段是核心**：相对导入 `from .models import X` 的 level=1，绝对导入 level=0。

六个测试逐条对位 docstring 的规则：

| 测试 | 行号 | 守卫内容 |
|---|---|---|
| `test_package_root_loads_nothing` | L49-62 | 包根零加载零导出 |
| `test_tool_permission_facade_names_resolve` | L65-67 | facade `__all__` 每个名字真实存在 |
| `test_guard_components_are_not_public` | L70-73 | 组件类名不进 facade |
| `test_submodule_imports_are_relative_or_through_other_facade` | L76-89 | 子模块内 import 纪律 |
| `test_agent_shield_does_not_import_sibling_projects` | L92-100 | 不依赖兄弟项目 |
| `test_other_projects_use_submodule_roots_only` | L103-114 | 兄弟项目只许深一层 |

## 三、外部连接

- **被测对象一：包根**。`agent_shield/__init__.py` 全文只有版权头 + docstring（"本包根不导出任何名字，也不在导入时加载子模块"），连一行 import 都没有——`test_package_root_loads_nothing` 的两条断言（`sys.modules` 里无 `agent_shield.*`、`dir()` 无公开名）因此恒真。
- **被测对象二：`tool_permission/__init__.py` facade**。`__all__` 列 13 个名字（`tool_permission/__init__.py:27-42`）：PermissionComponent、PermissionEngine、PermissionLevel、PermissionManager、PermissionResult、CandidateKind、CommandDialect、RouteContext、RouteInterest、SecurityTarget、SandboxPolicyProjection、SkippedSandboxRule、project_sandbox_policy、get_permission_manager。注意 docstring 明言 toolguard/fileguard/netguard/hostguard 与 engine、routing "不对外承诺稳定"（L5-8）——engine 虽在 `__all__` 里，但那是给宿主的；guard 子包永远不是 API。
- **被测对象三：兄弟项目 jiuwenbox / agent_ssas**。`test_other_projects_use_submodule_roots_only` 会真实遍历 `REPO_ROOT / project` 下的全部 .py（仓里这两个目录存在时不 skip，`test_import_rules.py:105-107`），保证它们对 agent_shield 的 import 不超过两段（`agent_shield.tool_permission` 合法、`agent_shield.tool_permission.engine` 违规）。
- **测试基础设施**：标准 pytest，仅用 `parametrize` 与 `subprocess`，无自定义 fixture——刻意保持零依赖，让这条守卫在任何最小环境都能跑。

## 四、数据流

### 测试 1：子进程隔离验证"导入零副作用"

`test_package_root_loads_nothing`（L49-62）不能在当前进程里做——pytest 进程早已 import 过 `agent_shield.tool_permission`（本文件 L23 顶部就 import 了）。所以它拼一段代码用 `sys.executable -c` 在**干净子进程**里执行：

```python
import sys, agent_shield
loaded = [m for m in sys.modules if m.startswith('agent_shield.')]
assert not loaded, loaded
assert not [n for n in dir(agent_shield) if not n.startswith('_')]
```

cwd 设为 REPO_ROOT 保证 `agent_shield` 可被发现。这条测试防的是最隐蔽的侵蚀方式：某天有人往包根 `__init__.py` 里加一行 `from .tool_permission import PermissionEngine` "方便用户"——功能全对，但每个 import agent_shield 的进程都被迫加载整条权限引擎链。

### 测试 4：AST 级 import 纪律审查

`test_submodule_imports_are_relative_or_through_other_facade`（L76-89）遍历 `tool_permission`/`detection` 下所有 .py 的每条 import，判定逻辑浓缩在 L83-88：

```python
parts = module.split(".")
if parts[0] != "agent_shield":
    continue                      # 外部依赖（re/pathlib/httpx）不管
if len(parts) != 2 or parts[1] == submodule:
    offenders.append(...)          # 两段以上 或 自我绝对导入 → 违规
```

注意 level>0（相对导入）在 L82 提前 `continue`——**子模块内部互相引用必须写相对导入**；`agent_shield.tool_permission` 这种两段绝对导入只有在**跨子模块**（detection 引 tool_permission）时才合法；`agent_shield.tool_permission.engine` 三段（伸进对方内部）与 `agent_shield.tool_permission.xxx`（自己写绝对路径，偷懒不写相对）都算违规。

### 测试 3：组件不是 API

`test_guard_components_are_not_public`（L70-73）断言五个内部名——`NetGuardComponent`、`FileGuardComponent`、`HostGuardComponent`、`TieredPolicyComponent`、`InjectionComponent`——与 facade `__all__` 无交集。这是第 01 篇"组件构造私有、只经 PermissionEngine facade"纪律的测试化：一旦有人把组件类挂到 `__init__`，宿主就会绕过引擎直接 new 组件，聚合与原子换装全部失效。

### 测试 5/6：依赖方向单向化

`test_agent_shield_does_not_import_sibling_projects`（L92-100）扫全包（tests 目录豁免，L95-96），任何 `jiuwenbox.*`/`agent_ssas.*` 的 import 都是违规——**安全库不得依赖上层应用**，否则会出现循环依赖且安全组件无法独立发版。`test_other_projects_use_submodule_roots_only`（L103-114）反向约束：应用可以依赖安全库，但**最深一层**（`len(parts) > 2` 即违规，L112）——防止应用伸进 guard 内部模块，将来内部重构必炸。

## 五、设计决策与权衡

**为什么用 AST 而不是正则扫 import？** 正则无法区分字符串里的 "import x"、无法拿到 `from . import y` 的 level、会被多行 import 折行骗过。`ast.parse` + `ast.walk`（L40-46）给出的是语法树级真相。代价是 Python 语法演进（如未来的 import 变体）需要跟进，但对一个安全仓这是值得的。

**为什么 facade 检查用 `__all__` 而不是 `dir()`？** `test_tool_permission_facade_names_resolve` 遍历的是 `tool_permission.__all__`（L66-67）。`__all__` 是显式契约：作者承诺的公开集合。`dir()` 会混入传递进来的名字（比如 facade import engine 时顺带可见的 `logging`），用它做断言会误伤。

**为什么兄弟项目缺席时 skip 而不是 fail？**（L106-107）agent-security 是集合仓，clone 可能只带部分子项目。架构守卫的目标是"在场的代码守纪律"，不是"目录必须齐全"——用 skip 保持守卫在任何裁剪下可运行。

**为什么相对导入强制到测试级？** 相对导入让子模块可以整体改名搬移（`agent_shield.tool_permission` → 别的顶层名）而不改一行内部代码；绝对自我导入则把包名焊死在几十个文件里。对预期长期演进的安全库，这个自由度值得用 CI 锁住。

## 六、新人提示与坑

1. **这是 scanner 全空的根因**（understand 流水线视角）：包根零 import（没边可发现）、子模块内部全是相对导入（level>0，绝对路径解析器通常不展开 `.` 前缀）、跨子模块合法边只存在于 detection→tool_permission 一条窄通道、兄弟项目被禁止反向依赖。做知识图谱/依赖分析时，本仓的 import 边几乎要靠语义重扫（对照 routing 表、`_COMPONENT_BY_NAME`、facade `__all__`）而不是 import 语句。
2. **给 agent_shield 加新公开 API 的正确姿势**：实现放子模块内部 → 在子模块 `__init__.py` import 并加进 `__all__` → 跑这六个测试。三步缺一，要么名字解析不了（L65-67 炸），要么组件泄漏（L70-73 炸）。
3. **新加第三个子模块要改 L27 的 `SUBMODULES`**。忘了改，新子模块的 import 纪律就无人守卫——白名单机制天然有这个维护税。
4. **"从 agent_shield 根 import 任何东西"永远是错的**。正确写法 `from agent_shield.tool_permission import PermissionEngine`；写成 `from agent_shield import PermissionEngine` 现在直接 AttributeError，且这正是测试 1 要保住的形态。
5. **tests 目录是唯一豁免区**（L95-96 跳过 tests 的兄弟依赖检查）。测试里 import jiuwenbox 的夹具不违规——但生产代码永远别学着写。
6. **别把这文件当文档维护**：它没有 mock、没有业务断言，改动它的唯一理由是架构规则本身变了。若某条规则要放开（比如允许 detection 引用 toolguard 内部某稳定函数），改 docstring、改判定逻辑、跑全绿，一次 commit 说清楚——让架构演进的每一步在 git 历史里可追溯。

# 01 · pipeline/core.py——引擎控制流内核：15 类三层的组合式执行骨架

## 一、角色定位

`computer_use_engine/pipeline/core.py`（627 行）是 GUI Agent 引擎的**控制流内核**：它不认识窗口、元素、截图，只提供"把 typed step 组合成可执行流"的通用机制。全文件 import 仅 stdlib（`abc`/`dataclasses`/`enum`/`inspect`/`typing`，core.py:8-30），**零仓内依赖**——它是仓内依赖拓扑的根，`pipeline/__init__.py:9-11` 明文钉死其地位："Keep this package above both layers"（native 生命周期层不得反向依赖 interaction）。

一个必须先钉死的映射坑：消费方 import 的是 `computer_use.pipeline`（如 `interaction/read/passes/parse_read_request.py:14`），但磁盘上没有 `computer_use/` 目录——`setup.py:21-26` 的 `PACKAGE_ROOTS` 把 `computer_use` 别名到 `computer_use_engine` 目录。搜代码时 `computer_use.X` 自动换算到 `computer_use_engine/X/`。

## 二、内部结构：15 个类，三层划分

**元数据层（4 类）**
- `Effect`（core.py:45-52）：五档副作用分类 `PURE/QUERY/PREPARE/DISPATCH/RESOURCE`，全仓纯度经济的货币。
- `Contract`（core.py:55-76）：步骤契约，声明输入/输出描述符、effects、前置事实 `requires`、可写面 `writes`、失败面 `failures`；`__post_init__`（L75-76）把 effects 强冻成 `frozenset`。
- `Event`（core.py:79-103）：诊断事件，携带 `path/phase/effects/error_type/call_id/attempt/branch` 九字段。
- `Control`（core.py:106-146）：贯穿嵌套调用的不可变元数据（预算回调、取消谓词、诊断 sink、路径），提供 `child/with_remaining/with_attempt/with_branch` 纯派生方法。

**接口层（2 类）**
- `Step`（core.py:188-203）：结构化类型（`Protocol`，逆变入参/协变出参），约定 `name/contract/run/arun`——凡有此四成员的对象皆为合法 step。
- `Pipeline`（core.py:206-248）：可复用流程抽象基类，子类实现 `build()`（L221-228）组合 root step，构造时绑定（L218-219），`run/arun`（L242-248）纯转发。

**执行节点层（9 类）**
- `Node`（core.py:270-329）：唯一执行基类。`run/arun` 模板方法统一做三件事——`control.child(self.name)` 延长诊断路径（L301）、`emit("enter"/"exit"/"error")` 打点（L302/306/308）、行为下放给 `_run/_arun` 钩子。钩子声明放在 `if TYPE_CHECKING:` 块内（L278-286）带 `@abstractmethod`——运行时不强制、静态检查强制。
- `Pass`（core.py:332-371）：把 `Callable[[T, Control], U | Awaitable[U]]` 包成节点；`_run` 走 `_sync`（L367-368），`_arun` 走 `_await`。
- `PassDefinition`（core.py:374-397）：声明与绑定分离的载体，`signature` 属性（L391-394）反射工厂参数供检查，`__call__`（L396-397）绑依赖生成 `Pass`。
- 组合子：`Sequence`（L407-440，顺序串联、空序列原样返回输入 L411）、`Select`（L443-466，纯 selector 选分支）、`Repeat`（L495-579，body+纯 Gate 循环）、`Scope`（L582-626，上下文管理器包资源生命周期）；循环决策值 `Continue/Done`（L469-493）。私有函数 `_sync`/`_await`/`_composite`（L251-267/400-404）分别负责同步拒绝、awaitable 解析、契约合并。

## 三、外部连接

- **消费规模**：仓内 231 个文件 import 本包——`interaction/` 230 个 + `native/lifecycle.py` 1 个，与 `__init__.py` docstring 自述吻合；interaction 的 read/write/control/query 子流水线全以 `Pass`/`Sequence` 为砖块。
- **define 双轨典型**：`interaction/read/passes/parse_read_request.py:25-29` 用 `Pass.define(...)` 声明模块级 `stage`，`stage()` 即得无依赖 Pass。全仓 `Pass.define` 104 处、`Pass.factory` 56 处——define 用于零依赖纯函数，factory 用于注入端口/存储。
- **Pipeline 子类样例**：`interaction/read/delivery/diff/pipeline.py:55-76`——`__init__` 里 `super().__init__(root=self.build())`（L63），`build()` 返回 `Sequence(Select(...), _RenderPlannedDelivery())`。
- **native 层反向消费**：`native/lifecycle.py:18` import `Control, Effect`；L78-83 用 `port.pipeline_diagnostic` 组装 Control；L111/115/218/230 打 `Effect.RESOURCE` 事件。

## 四、数据流

一次 `run(value)` 的完整路径：

1. **入流**：`Pipeline.run`（core.py:242-244）→ root `Node.run`（L291-309）→ `(control or Control()).child(name)` 造新 Control → `emit("enter")` → `_run` 钩子。
2. **组合子递归**：`Sequence._run`（L432-435）线性传递；`Select._run`（L456-460）跑 selector 得 key，`with_branch(key)` 挂标签并 `emit("branch")`，把**原始输入**（非 selector 输出）交给选中分支；`Repeat._run`（L559-568）每轮 `with_attempt(iteration)`，body 结果交 `_decision`（L548-557）——Gate 返回 `Continue` 则 `.value` 作下一轮输入，`Done` 则 `.value` 是最终输出。
3. **诊断出流**：enter/exit/error/attempt/branch 经 `Control.emit`（L148-185）投给可选 sink；emit 用 `try/except BaseException: pass`（L183-185）兜底——诊断 best-effort，绝不影响业务结果。
4. **同步/异步双轨**：`Pass._run` 拿到 awaitable 时 `_sync`（L251-262）先 `close()` 掉误生协程再抛 `TypeError("An asynchronous stage requires arun()")`（L261）；`_arun` 经 `_await`（L265-267）兼容自定义 awaitable。

## 五、设计决策与权衡

1. **纯度即架构约束**：`Select` 构造期校验 selector 非纯即 `ValueError`（L451-452），`Repeat` 对 Gate 同校验（L536-537）。分支选择与循环判定强制纯函数，副作用只许发生在 body——诊断事件流因此能如实反映"哪里发生了什么类别的工作"。更彻底的是 `Select._arun`（L462-466）里 selector 仍调用同步 `self.selector.run`：契约既保证纯，异步路径无需 selector 异步。
2. **有界性强制**：`Repeat` 要么 `max_iterations` 要么 `bounded_by` 域预算名，皆无直接 `ValueError`（L542-543）；且 `max_iterations` 用 `type(...) is not int` 精确类型检查（L540-541）——连 `True`（bool 是 int 子类）都拒绝，杜绝隐性无限循环进入 agent 主链。
3. **declare/bind 分离**：`PassDefinition` 让"步骤是什么"（名字+契约+工厂签名）与"依赖什么"（`__call__` 实参）解耦，`signature` 支持无副作用依赖自省——160 处调用点的依赖注入地基。
4. **Control 是值不是上下文**：预算/取消/诊断全走显式值传递（L136-138）而非 ambient context——代价是每层穿参，收益是调用链类型透明、诊断可序列化。
5. **标签净化**：`with_branch`（L143-146）把复杂 key 降级为 `type(branch).__name__`——诊断通道不泄业务数据。代价面：深嵌套下三连 emit 有常量开销，frozen `replace` 全量复制。

## 六、新人提示与坑

- **搜不到包**：`computer_use.pipeline` 磁盘上不存在，去 `computer_use_engine/pipeline/`（setup.py:22 别名）。
- **同步误跑异步必炸**：handler 返回协程却走 `run()` 得 `TypeError: An asynchronous stage requires arun()`（core.py:261），协程已被 close 不会再报 "never awaited"——排障先查调用侧是否该用 `arun`。
- **三组"二选一"构造参数**：`Sequence` positional vs `steps=`（L427-428）、`Repeat` `advance` vs `on_decision=`（L532-533）、`Scope` `factory` vs `using=`（L607-608）同时给即 TypeError。
- **`Scope` 缺 body/factory 直接 TypeError**（L611-612），且无条件加 RESOURCE effect（L614）。
- **`Repeat` 的 advance 回调是同步的**：`_decision` 用 `_sync(self.advance(...))`（L554）。
- **空 `Sequence` 合法**：原样返回输入（L411）；**Contract 是 frozen**（L75-76）。

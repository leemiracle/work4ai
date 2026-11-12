# 10 · 可组合求导流水线：`src/torchjd/autojac/_transform/_base.py`

## 1. 角色定位

122 行（wc 实测），autojac 子系统内部的"微内核"：定义 `TensorDict` 类型别名与 `Transform` 抽象基类，以及两个组合子 `Composition`（串接）与 `Conjunction`（合取）。backward/mtl_backward 的全部计算都被表达为 Transform 的组合链——`AccumulateJac << Jac`（09 篇 :135）、`Stack(task_transforms)` + 公共 `Jac`（`_mtl_backward.py:175-178`）——这是把"求导编排"做成**可组合代数**的尝试：九个基础变换（Grad/Jac/Stack/Select/Diagonalize/Init/AccumulateGrad/AccumulateJac…，barrel `__all__` 13 项，`_transform/__init__.py:11-25`）像乐高块，两个运算符 `<<`（:58）与 `|`（:59）像卡扣。本文件是全库抽象密度最高的设计层。图谱视角：fan-in 10（全部 9 个派生变换文件 + barrel import 它，图谱），fan-out 12（4 个类被 contains + 8 条 tested_by，图谱）——`tests/unit/autojac/_transform/` 有专门的 test_base/test_stack 等分文件守护。

## 2. 内部结构：类/函数地图

| 行号 | 定义 | 要点 |
|---|---|---|
| :9 | `TensorDict: TypeAlias = dict[Tensor, Tensor]` | 流经全流水线的统一数据形态：张量→张量的字典 |
| :10-19 | 四类流的非正式注释 | **纯注释、无类型**——Gradients（值形同键形 :11-12）/ Jacobians（值多一个首维 :13-14）/ GradientVectors（摊平向量 :15-16）/ JacobianMatrices（矩阵化 :17-19）；注释头承认"for performance reasons"（:10）：真做四类型会拖慢运行时，遂以文档约定代替 |
| :22-23 | `class RequirementError(ValueError)` | 键集不合法的专用异常 |
| :26-59 | `class Transform(ABC)` | 微内核根：抽象 `__call__(input: TensorDict) -> TensorDict`（:41-43）+ 抽象 `check_keys(input_keys) -> output_keys`（:45-56）；具体方法 `compose`（:32-33）/`conjunct`（:35-36）与操作符绑定 `__lshift__ = compose`（:58）、`__or__ = conjunct`（:59）；`__str__` 返回裸类名（:38-39） |
| :62-84 | `class Composition(Transform)` | `__init__(outer, inner)`（:70-72）+ `__call__`：`intermediate = self.inner(input); return self.outer(intermediate)`（:77-79）+ `check_keys` 链式传递（:81-84）；`__str__` 渲染 `" ∘ "`（:75） |
| :87-121 | `class Conjunction(Transform)` | 构造收 `Sequence[Transform]`（:95）；`__call__` 把各变换对同一输入的结果按 `|=` 并集（:108-112）；`check_keys` 要求各输出键集**两两不相交**否则 RequirementError（:118-119）；`__str__` 渲染 `"(a | b)"` 且嵌套去括号（:98-106） |

设计上最值得停留的是**双方法协议**：`__call__` 执行计算，`check_keys` 纯静态推演"输入键集→输出键集"——一个 Transform 因此可以不跑就回答"我能接在谁的后面"，组合链的正确性可以前置验证。

## 3. 外部连接

**9 个派生变换**（图谱 10 条 imports 入边，含 barrel）：`_differentiate.py`（`Differentiate(Transform, ABC)` :12——Jac/Grad 的公共父）、`_jac.py`（`Jac(Differentiate)` :12）、`_grad.py`、`_init.py`、`_diagonalize.py`、`_select.py`、`_stack.py`、`_accumulate.py`（双类 AccumulateGrad/AccumulateJac），加 `_ordered_set.py` 的 OrderedSet 与 barrel 自身。**上游消费**：`_backward.py:5`、`_jac.py`（autojac 顶层）、`_mtl_backward.py`、`_utils.py`（create_jac_dict 用 Init/Diagonalize 造种子）。**tested_by 8 条**（图谱）：`tests/unit/autojac/_transform/test_base.py`、`test_stack.py` 及各变换专属测试，其中 `test_interactions.py` 直接测 `Init << Diagonalize << Jac` 这类真实管道的端到端数值。

**与 06 篇 `<<` 的对偶**：两处 `__lshift__` 语义同构（右先左后），但对象域不同——Weighting 域组合"权重器×函数"（有 nn.Module 语义），Transform 域组合"变换×变换"（纯函数语义）；Transform 域还多出 `__or__` 合取（:59），Weighting 域没有对应物（权重器没有"并行分头再并集"的形态）。

## 4. 数据流：mtl_backward 的变换树走读

Conjunction 最烧脑的应用在多任务链（对照 09 篇单链）。`mtl_backward([loss1, loss2], features, shared_params, ...)` 的组装（`_mtl_backward.py`）：每任务一条 `Grad` 分支（对各自损失求对共享表示 features 的梯度），`Stack(task_transforms)`（:175）把各任务的梯度字典**沿新首维堆叠**成 Jacobian 形态，再接公共 `Jac(features, shared_params, ...)`（:178）继续向参数层求导。走读一段典型执行：

1. 输入 TensorDict 携带各损失种子，流入 `Conjunction` 或 Composition 的 inner；
2. `Composition.__call__`（:77-79）：`inner` 先行——例如 `Jac`（`_jac.py:12`）按 `n_chunks = math.ceil(m / max_chunk_size)`（`_jac.py:73`）切块、每块走 vmap 或直调（`_get_jacs_chunk` :103-119），产出 `{param: (m,)+param.shape}` 的 Jacobians 形流；
3. `outer` 收接——`AccumulateJac.__call__`（`_accumulate.py:34-36`）调 `accumulate_jacs` 写 `.jac` 返回 `{}`；
4. 若链上有 `Conjunction`（:108-112）：各分支拿到**同一个输入字典**，各自产出键不相交的子字典后 `union |=` 合并——`check_keys`（:114-121）先静态验证过不相交性，运行时并集不会互相覆盖；
5. 键协议贯穿全程：`Differentiate.check_keys`（`_differentiate.py:58-66`）要求输入键集精确等于 outputs 集、返回 inputs 集——`RequirementError`（:22）在任何键错配时给出可定位的报错。

一句话：`<<` 管"流水线串行"，`|` 管"多路归并"，`check_keys` 是不花运行时代价的类型检查器。

## 5. 设计决策（含批判视角）

- **dict[Tensor, Tensor] 以张量为键**：用张量对象身份（id）做键，参数与梯度的绑定天然免疫命名冲突；代价是 Tensor 不可哈希异议（PyTorch Tensor 实现了按 id 的 hash）与不可序列化——调试时只能靠形状与 id 辨认，`tests/conftest.py:53-60` 的参数化 id 渲染（`"T" + str(list(val.shape))`，:60）正是为此打的补丁；
- **四类流只写在注释里**（:10-19）：性能是官方理由（注释原文"for performance reasons"）。这实际是把类型系统的活儿降级为文档——mypy 无法阻止把 Gradients 流接进期望 Jacobians 流的变换，靠 `check_keys` 的键集检查兜住"键"的错配但兜不住"形状语义"的错配（形状检查散在各变换内部）；
- **`check_keys` 的静态推演**：让 mtl_backward 这类复杂链可以在组装期（而非运行期）验证拓扑合法性——正确的抽象换来了提前报错；
- 批判视角一：**双协议（`__call__` + `check_keys`）没有强制同步**——新增 Transform 若 `check_keys` 与 `__call__` 的实际键行为不一致，静态检查通过、运行时错乱，且没有任何测试基建强制对拍两者（test_base.py 只测基类行为本身）；
- 批判视角二：`Composition`/`Conjunction` 都是可变对象（无 `__slots__`、无不可变性保障），组装后的链仍可被外部改写 `self.inner`——乐高的乐趣与误用的风险并存；
- 批判视角三：`__str__` 手写渲染（:75、:98-106，含嵌套去括号特判 :102-103）与 `__repr__` 缺失，长链的调试输出全靠这几个手搓字符串，一旦某子类覆写 `__str__` 不守约定（返回含 "|" 或 "∘" 的串）就会破坏去括号逻辑——约定链脆弱。

## 6. 新人提示

1. 记住三件套的分工：`TensorDict`（:9）是血流、`__call__` 是心脏、`check_keys` 是心电图——读任何新变换先看它的 `check_keys` 返回什么键集，输入输出形状语义就清楚了；
2. 手绘 mtl_backward 的变换树（Grad×N → Stack → Jac → Accumulate 双类）再对照 `_mtl_backward.py:170-180` 的组装代码，是理解 `|` 与 `<<` 协作的最快路径；
3. 写新变换的模板：继承 Transform、实现两方法、`__str__` 保持裸类名、在 `_transform/__init__.py` 登记——然后去 `tests/unit/autojac/_transform/` 抄一个现有测试的骨架；
4. 撞到 `RequirementError` 时读消息里的键集差（哪个张量多了/少了），十有八九是 backward 调用点的 tensors/inputs 参数与变换期望不符，而不是变换本身有 bug。

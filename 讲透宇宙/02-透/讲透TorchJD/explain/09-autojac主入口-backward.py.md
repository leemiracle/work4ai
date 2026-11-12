# 09 · autojac 主入口：`src/torchjd/autojac/_backward.py`

## 1. 角色定位

135 行（wc 实测），库的第一公民 `backward` 的实现文件——对标 `torch.autograd.backward`，但把结果累积进自定义的 **`.jac` 字段**而非 `.grad`（docstring :24-26）。用户视角它是 Jacobian descent 的入口：`backward([loss1, loss2])` 之后每个参数的 `.jac` 多了 m 行。实现视角它是 10 篇 `_transform` 流水线的第一个真实客户：函数体只有 4 步校验 + 2 步组装（:107-121），真正的工作全委托给一条 `AccumulateJac << Jac` 变换链（:135）。同包三兄弟：`jac`（返回元组而非写字段）、`mtl_backward`（双写 `.grad`+`.jac`，`_mtl_backward.py:25`）、`jac_to_grad`（聚合桥，`_jac_to_grad.py:22`），barrel `autojac/__init__.py:13` 的 `__all__` 恰好四项。图谱视角：fan-in 7（3 条 imports 入边：顶层门面、本包 barrel、`tests/unit/autojac/test_backward.py`，图谱）。

## 2. 内部结构：类/函数地图

imports（:1-11）两组：`_transform` 包五符号（:5：`AccumulateJac`、`Jac`、`OrderedSet`、`Transform`——组合子的原料）与 `_utils` 五函数（:6-11：`as_checked_ordered_set`、`check_optional_positive_chunk_size`、`create_jac_dict`、`get_leaf_tensors`）。

**`backward(tensors, /, *, jac_tensors=None, inputs=None, retain_graph=False, parallel_chunk_size=None)`**（:14-121）：
- 签名全关键字限定，五参与 `torch.autograd.backward` 对照；`jac_tensors` 是 `grad_tensors` 的 Jacobian 版（docstring :29-36：形状 `(m,) + tensor.shape`，首维一致，缺省 identity）；
- `:107` chunk 校验前置；`:109` `as_checked_ordered_set(tensors, "tensors")`（`autojac/_utils.py:20`，下文简称 `_utils.py`）去重保序（Jacobian 行序=损失序的保证）；`:111-112` 空集 ValueError；
- `:114-117` inputs 缺省时 `get_leaf_tensors(...)`（`_utils.py:155`）——**自动遍历 autograd 图找叶张量**（BFS 找 AccumulateGrad 节点，`_utils.py:184`）；显式给则 `OrderedSet(inputs)`（:117）；
- `:119` `create_jac_dict`（`_utils.py:106`）——None 时用 `(Diagonalize << Init)({})` 现造 identity Jacobian 字典；`:120-121` 组装并执行变换链。

**`_create_transform(...)`**（:124-135）：:132 `jac = Jac(...)`、:134 `accumulate = AccumulateJac()`、**:135 `return accumulate << jac`**——文件头注释 :5 声明式预告了这一行。docstring 警告块（:98-105）交代 vmap 三大坑（编译函数输出、`retains_grad=True`、CUDA RNN，各附 issue 链接），处方都是 `parallel_chunk_size=1` 退化串行。

## 3. 外部连接

**上游**（图谱 3 条 imports 入边）：`src/torchjd/__init__.py:5`（弃用再导出预取，01 篇）、`autojac/__init__.py:8`（正牌导出）、`tests/unit/autojac/test_backward.py`（19 例，实测）。**下游**：`_transform/__init__.py` 与 `_utils.py`——前者是 10 篇的全部内容。文档侧 4 条 documents 边（图谱）对应 `docs/source/docs/autojac/backward.rst` 与三篇教程。`jac_to_grad` 与本函数构成"计算-聚合"两步协议：`.jac` 让中间检查（monitoring.rst 挂 hook）与聚合（`_jac_to_grad.py:120-127` 校验 `is_tensor_with_jac`、`retain_jac=False` 时 :136 `_free_jacs` 清场）成为可能。

## 4. 数据流：`backward([y1, y2])` 逐步走读

docstring 自带最小例（:53-66）：`param = torch.tensor([1., 2.], requires_grad=True)`，`y1 = [-1.,1.] @ param`，`y2 = (param**2).sum()`，期望 `param.jac` 为 `[[-1.,1.],[2.,4.]]`。

1. **入参整形**：:109 得 `OrderedSet([y1, y2])`（保序去重）；:111 过空检查；:114-115 `inputs=None` → `get_leaf_tensors` 从 `grad_fn` BFS 下行找到唯一的 `AccumulateGrad(param)` → `OrderedSet([param])`；
2. **种子构造**：:119 `create_jac_dict` 走 identity 分支（`_utils.py:124-127`）：`Init`（各造单位种子）`<<` `Diagonalize`（升维成 `(m,)+shape` 的堆叠单位阵），返回 `{y1: [[1,0]], y2: [[0,1]]}` 形态的 TensorDict——**m=2 行 Jacobian 的 vmap 弹匣装填完毕**；
3. **链组装**（:132-135）：`AccumulateJac << Jac`——`Jac`（`_transform/_jac.py:12`）按 `chunk_size=None` 一次 vmap 全并行（`_get_jacs_chunk` :103-119，单行时直调免 vmap :112-115）；`AccumulateJac` 把结果写进 `param.jac` 返回空 TensorDict（`_accumulate.py:34-36`）；
4. **执行**（:121）：`transform(jac_tensors_dict)`——`Composition.__call__`（`_transform/_base.py:77-79`）先 inner 后 outer：`Jac` 对每个 input 产出 `(m,) + input.shape` 的 Jacobian（`_transform/_jac.py:50-51` docstring 明言该形状契约），`AccumulateJac` 经 `accumulate_jacs`（`autojac/_accumulation.py`）写字段；
5. **内存语义**：`retain_graph=False`（:20）缺省释放计算图——要接 `.backward()` 或二次 `backward` 必须显式 True。

对照 `mtl_backward`（`_mtl_backward.py`）：组装"每任务一条 Grad 分支 + `Stack(task_transforms)` 合流（:175）+ 公共 `Jac`（:178）"的树形链（10 篇），把"任务私有参数走 `.grad`、共享参数走 `.jac`"的双写协议编码进变换拓扑——两个入口的全部差异都在 `_create_transform` 一层。

## 5. 设计决策（含批判视角）

- **结果写 `.jac` 而非 `.grad`**：核心抉择。`.grad` 语义被 PyTorch 占用，混写会与 optimizer 冲突；独立字段让"Jacobian 计算"与"聚合"两阶段显式分离（`jac_to_grad`），中间可插入检查/修改。代价：自定义字段不受 autograd 管理，生命周期全靠库约定（`_jac_to_grad.py:136` 的 `_free_jacs`）；
- **OrderedSet 保序**（:109/:117）：Jacobian 行序=损失序是数学正确性的前提（聚合器按行配权重），普通 set 随机序会静默错配——为此在 `_transform` 自造 `OrderedSet`（10 篇）；
- **inputs 自动发现**（:114-115）：省去用户枚举参数；实现靠遍历非公开的 autograd 节点（`_utils.py:178` 注释承认 AccumulateGrad 非公开，:179 还挂了 `ty: ignore`）——吃 PyTorch 内部实现的风险，换来零配置体验；
- 批判视角一：`parallel_chunk_size` 的 None 缺省（:21）是"全并行 vmap"激进档，与 :98-105 警告块的 vmap 三坑直接冲突——库选性能优先、把退避留给用户排障，CUDA+RNN 场景会先撞异常再读文档；
- 批判视角二：函数体把校验、发现、种子、组装执行压成 15 行直译体（:107-121），可读性靠 docstring 补偿；`_create_transform` 只服务本函数却升为模块级私有函数，是为变换链可独立 import 测试付出的结构税；
- 批判视角三：`jac_tensors`（:18）是给 partial JD / 图分段场景预留的"预乘 Jacobian"高级通道，文档位置却在参数表第二位，新手易误用——它的存在说明 backward 本质是"线性变换回传器"而非仅"Jacobian 计算器"，这层抽象在 docstring 只以 "analog to grad_tensors"（:29-30）轻带过。

## 6. 新人提示

1. 第一课永远是字段区别：`backward` 写 `.jac`（每损失一行），`jac_to_grad` 才写 `.grad`；`param.jac` 在 optimizer.step() 前不会消失，但 `jac_to_grad` 默认聚合后清空（`retain_jac=False`）；
2. 报错 "All `tensors` should have a `grad_fn`"（`_utils.py:167`）意味着你传了叶张量或已 detach 的张量——backward 的输入必须是"算出来的"量；
3. vmap 相关异常（CUDA RNN / compiled fn / retains_grad）一律先试 `parallel_chunk_size=1`（:104 处方）再深查；
4. 想读懂全库，本文件与 10 篇连读：这里只看 `_create_transform` 的两行（:132-135），全部魔法在 `Jac` 的 chunk/vmap 策略与 `AccumulateJac` 的字段写入——建议接着读 `tests/unit/autojac/_transform/test_interactions.py`，它端到端测真实管道的数值。

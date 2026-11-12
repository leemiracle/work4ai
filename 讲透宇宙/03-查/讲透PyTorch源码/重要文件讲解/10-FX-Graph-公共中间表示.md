# 10. torch/fx/graph.py — FX Graph：整个编译栈的公共中间表示

> 源文件：`torch/fx/graph.py`（2959 行）。知识图谱定位：layer `fx-ir`（"FX 中间表示"），节点 `file:torch/fx/graph.py`，复杂度 complex。
> 前置阅读：04-Dynamo（前端）、06-Inductor（后端）。本文讲两者之间的"货币"——FX Graph IR。

## 1. 架构角色：谁都在用这张图

知识图谱的 import 边（27 条入边）直接暴露了它的地位：

- **Dynamo 前端**：`torch/_dynamo/eval_frame.py`、`torch/_dynamo/functional_export.py` imports 本文件——Dynamo 从字节码重建出的计算图就是 `fx.Graph`；
- **Inductor 后端**：`torch/_inductor/compile_fx.py` imports 本文件——`compile_fx(graph_module, example_inputs)` 的输入就是这里的 Graph；
- **torch.export**：`torch/export/_trace.py`、`exported_program.py`、`_unlift.py` depends_on 本文件——ExportedProgram 的 graph 属性即 FX Graph（ONNX 导出在现行架构里走 dynamo→torch.export 这条链，所以同样落在这张 IR 上）；
- **FX 自家生态**：`proxy.py`（tracing）、`interpreter.py`（解释执行/Transformer 模式）、`passes/graph_manipulation.py`、`split_utils.py`（子图切分）、整个 `torch/ao/quantization/fx/` 量化栈（12 个文件 imports）。

一句话：**Dynamo 捕获语义 → FX Graph 表达语义 → AOTAutograd/Inductor/export/量化 消费语义**。graph.py 是这个三角贸易的清算所。

文件内部结构（contains 边 + 源码）：`Graph`（1398 行起，约 1300 行）、`CodeGen` 代码生成家族（368-1359）、`_Namespace` 命名管理（164）、`_InsertPoint` 插入点（274）、`_node_list` 链表视图（291）、`_FindNodesLookupTable` 查找加速表（1362）。`__all__ = ["PythonCode", "CodeGen", "Graph"]`（48 行）。

## 2. 数据模型：哨兵 + 双向链表 + 双向记账

### 2.1 Graph 本体几乎不存"东西"

`Graph.__init__`（1447-1467）只有：

- `self._root: Node = Node(self, "", "root", "", (), {})`（1457）——**哨兵节点**，`_next` 指向第一个真节点，`_prev` 指向最后一个。链表为空时 `root._next is root._prev is root`；
- `self._insert = self._root.prepend`（1459）——默认插入函数：往哨兵前面插 = **追加到图尾**（这就是"不设插入点时新节点总在末尾"的实现，一行闭包引用，没有 if-else）；
- `self._len`、`self._graph_namespace`、`self._codegen = CodeGen()`、`self._find_nodes_lookup_table`。

节点顺序就存在每个 `Node` 的 `_prev/_next` 指针里（node.py 序列化字典 390-391 可见），Graph 只持有链表头。`Graph.nodes` 属性（1477-1490）返回 `_node_list` 视图：`__iter__` 直接调 **C++ 实现的 `_NodeIter`**（27 行从 `torch._C` 导入，311 行使用）——热路径不走 Python 迭代器。docstring 明确承诺：**迭代中增删节点是安全的**（1482-1483），这是后面所有 pass 能边遍历边改写的基础。

### 2.2 生产者/消费者双向映射

数据流记账分散在 Node 上，但**规则由 Graph 层定义**：

- 每个 Node 维护 `_input_nodes: dict[Node, None]`（我消费谁）和 `users: dict[Node, None]`（谁消费我），两个 dict 互为转置。`all_input_nodes` 就是 `_input_nodes.keys()`（node.py:498-510）；
- `node.args = new_args` 赋值（node.py:464-473）或 `insert_arg`（node.py:546-552）会自动更新两侧记账——**改 args 不是改数据，是改图结构**；
- `_input_nodes` 顺序 = args/kwargs 中 Node 出现顺序，`lint()`（2611-2689）据此做拓扑序检查：任何 arg 必须已定义（2631-2635）。

`_FindNodesLookupTable`（1362-1395）是 Graph 侧的加速侧表：`(op, target)` 二级 dict，`find_nodes(op=..., target=...)`（1499-1524）从 O(n) 线扫变 O(1)，这是 Inductor/DCE 反复查同名算子的关键优化。create_node/erase_node 时同步 insert/remove（1661、1704）。

## 3. 六种 opcode 与节点创建 API

`_legal_ops`（68-70）封死了 IR 的全部语义种类，每个 op 的 target 类型不同：

| op | target 类型 | 语义 | 创建 API（行号） |
|---|---|---|---|
| `placeholder` | str（参数名） | 函数输入 | `Graph.placeholder(name, type_expr, default_value)` 1768 |
| `call_function` | Callable | 自由函数/算子调用 | `Graph.call_function(fn, args, kwargs)` 1961 |
| `call_method` | str（方法名） | `args[0].method(...)` | `Graph.call_method` 1922 |
| `get_attr` | str（限定名） | 从 Module 树取参数/子模块 | `Graph.get_attr` 1801 |
| `call_module` | str（限定名） | 调子模块 forward | `Graph.call_module` 1869 |
| `output` | "output" | return 语句 | `Graph.output(result)` 2426 |

**所有路径最终汇聚到 `create_node`**（1586-1663），它做六件事：

1. 类型校验：args 必须 tuple、kwargs 必须 dict（1622-1631）；
2. 反裸 SymInt 卫兵：call_* 类 op 的参数里出现原始 `SymInt/SymFloat/SymBool` 直接 warn，指路 `create_*_node()` 或 `materialize_symints()`（1635-1644）——符号值必须以"图内节点"存在，不能藏在 Python 对象里逃过 IR；
3. 命名：`_Namespace.create_name`（164-227）——candidate 经非法字符清洗（`_name_regex` 141）、避开关键字/builtin（`_illegal_names` 94-95）、`base_N` 计数去重（`_base_count` 防二次方循环，207-217）；
4. 构造 `Node(self, name, op, target, args, kwargs, type_expr)`（1649）；
5. 触发 owning_module 的 `_create_node_hooks`（1651-1656）；
6. `self._insert(n)`（1660）挂进链表 + 查找表 insert + `_len += 1`。

细节语义：`placeholder` 的 default_value 非空时被塞进 `args[0]`（1797）——IR 里"默认值"编码为节点的第一个参数；`output` 把返回值整个包进 `args=(result,)`（2446-2447）；`get_attr`/`call_module` 在 owning_module 存在时会校验引用真实性并 warn（1851-1865、1906-1916）。

派生便捷 API：`create_size_node/create_stride_node/create_storage_offset_node`（2019-2046）——把 `x.size(i)` 降为 `aten.sym_size.int` 图节点并回填 meta，是动态形状进 IR 的正门。

## 4. "执行"一个 Graph：没有 `Graph.__call__`，从来都是生成 Python 代码

任务清单里问的 "Graph.__call__ vs create_node"，在本 checkout 里要先把事实摆正：**当前版本 `Graph` 类没有 `__call__` 方法**（全 fx 树 grep 无命中；`proxy.py:680` 的 `__call__` 是 Proxy 的）。执行身份由三层拼成：

1. **生成代码**：`GraphModule.recompile()`（graph_module.py:926）调 `graph.python_code()` 拿到 `PythonCode(src, globals, ...)`（dataclass，245-260），再 `exec(compile(src, key, "exec", dont_inherit=True), globals)`（graph_module.py:145）——FX 的"编译"就是把 IR 印成 Python 源码再 exec；
2. **GraphModule 是 nn.Module**：调用走标准 `nn.Module.__call__` → 生成的 forward；
3. **非默认 CodeGen 的输入输出适配**：`Graph.process_inputs/process_outputs`（1665-1674）委托给 codegen，契约写在 `CodeGen.process_inputs` docstring（476-485）：
   `f.graph.process_outputs(f.graph(*f.graph.process_inputs(*inputs))) == f(*inputs)`
   ——boxed/pytree/export 三种 codegen 改变了 forward 的签名，靠这两个钩子在"图语义"与"函数签名"之间换算。

所以对立面其实是：**`create_node` 是"写 IR"的唯一闸口（tracing 和程序化构造都汇到这），而"执行"是 IR→Python 源码→exec 的物化**。这个"IR 能还原成可跑 Python"的性质叫 graph is executable，它让 FX 图永远可以退回 eager 跑（Interpreter 之外的第二条执行路径）。

## 5. 改写不变量：replace_all_uses_with / erase_node

图改写的全部安全性建立在两条不变量上：

**不变量 A（erase_node，1676-1715）**：节点 `users` 非空不许删（1686-1690 抛 RuntimeError，把剩余 users 打印给你看）；跨图删节点直接抛错（1691-1692）；`_erased` 标志保证幂等（1693-1695，迭代器可能还握着已删节点的句柄）。删除动作本身：摘链表（`_remove_from_list`，1706）→ 置 `_erased` → **把自己的 args/kwargs 全部换成 None**（1712-1715 的 `_update_args_kwargs(map_arg(..., lambda n: None))`）——这一步是精髓：nulling 让上游生产者的 `users` 表自动收缩，引用计数式的级联。

**不变量 B（replace_all_uses_with，node.py:713-757）**：遍历 `self.users` 的快照（745，防迭代中修改），对每个 user 调 `_replace_input_with`。两个现代参数：`delete_user_cb` 选择性跳过某些 user（749-750）；`propagate_meta=True` 把 meta 整体搬给替换节点——前提是替换节点 meta 为空（737-744），AOTAutograd 用它保住 fake tensor 元数据。替换时还会触发 `_replace_hooks`（746-754）。

配套设施：

- `inserting_before(n) / inserting_after(n)`（1717-1765）：返回 `_InsertPoint`（274-288）。实现极其轻：进入时把 `graph._insert` 换成 `n.prepend`/`n.append`，退出时还原——**插入点不是位置数据，是一个可替换的函数槽**。`inserting_before(None)` = 插到图首（1736-1737 转成 `inserting_after(self._root)`）；`with g.inserting_before(g.output_node()):` 是最常见姿势（`output_node()` 1492-1497 从链表尾取 output 节点）；
- `node_copy`（2387-2422）/`graph_copy`（1526-1553）：跨图复制，`arg_transform` 回调负责旧图 Node→新图 Node 的重定向（val_map 模式是所有 Transformer 的标准写法）；`__deepcopy__`（1555-1584）显式重写为迭代式正是为了防默认深拷贝在长链表上**递归爆栈**；
- `eliminate_dead_code`（2691-2778）：先 `lint()` 保拓扑序，倒序遍历，无 user 且无副作用（`node.is_impure`）才删；docstring 警告副作用覆盖不完整（2727-2734）；还会递归 DCE 子 GraphModule（2765-2776）；
- `lint()`（2611-2689）：四查——opcode 合法、节点归属本图且在侧表中、拓扑序（用前必先定义）、call_module/get_attr 的 target 真实存在于 owning_module。

## 6. hooks 体系（对应旧资料里的 "on_import"）

旧版资料提到的 `on_import` 钩子在本 checkout 已不存在；现行机制是三组挂在 **owning GraphModule** 上的钩子（graph_module.py:653-654 定义，1205-1240 提供 register/remove API）：

- `_create_node_hooks`：create_node 里触发（1651-1656）；
- `_erase_node_hooks`：erase_node 里触发（1697-1702）；
- `_replace_hooks`：replace_all_uses_with 里触发（node.py:746），收到 `(old, new_name, user)`。

典型用途是子图切分（splitter）这类需要在图变动时维护外部映射的 pass。另有 **代码级钩子** `on_generate_code(make_transformer)`（2784-2867）：对生成代码的 `body: list[str]` 做后处理（例：插 `pdb.set_trace()`），支持链式组合和 context manager 自动还原——Inductor 的 minifier 大量用它改写生成代码做定位。

## 7. graph_hash 与"值省略（elide）"的现代对应物

任务清单里的 `graph_hash`/`elide` 在本版本同样无同名 API，功能由两处承担：

- **图内容哈希**：`graph_module.py:_metadata_hash`（423-447）——把生成代码 + 全部节点 metadata JSON 化后 sha256/base32，内容寻址生成 `FX_CACHE` 里的 forward 文件名（962-965）。Graph 内部的 hash-consing 则出现在 `materialize_symints`（2148-2153：per-call `expr_to_proxy` 缓存让共享子表达式的 SymInt 复用同一子图）；
- **值省略**：`CodeGen._gen_python_code` 里的 last-use 分析（671-685：倒序扫一遍，记录每个 Node 在执行序中的**最后一次**使用）+ `delete_unused_values`（687-712）：在每个调用点后发射 `;  dead_1 = dead_2 = None`（710 行，dim 灰色注释）——生成的 Python 主动释放不再用的中间张量，长序列上省显存；无 user 但因副作用保留的节点也自我释放（700-704）。boxed 参数版本（941-1002）把装箱参数的生死窗口进一步压到"装箱后、调用前"。

## 8. tracing vs 程序化构造：同一个 create_node 的两条进路

**路一（symbolic_trace）**：`torch.fx.symbolic_trace` → `_symbolic_trace.Tracer`（282 行起）。`Tracer.trace()` 在 857 行 `self.graph = Graph(tracer_cls=tracer_cls)` 建空图，把用户输入包成 `Proxy`（proxy.py:600）跑一遍 forward；Proxy 重载的所有运算符（`__add__`/`__getitem__`/`__call__`…）最终调 `TracerBase.create_proxy`（proxy.py:340），而 `TracerBase.create_node`（proxy.py:215-236）在做完可变性检查、记录 module scope 与 stack_trace（239-259，进 node.meta）之后，**一行委托 `self.graph.create_node(...)`（236）**。Dynamo 路线不同：它不跑 Proxy，而是从字节码帧分析直接批量调 `graph.call_function`（proxy_tensor/proxy_tensor.py 里 python_dispatcher 路径），但落点相同。

**路二（程序化/pass）**：`GraphAppendingTracer`（proxy.py:579-585）——最小 TracerBase，只带一个 graph 引用，专供"不在 tracing 中但想用 Proxy 运算符建图"的场景。graph.py 自己就是最大用户：`materialize_symints`（2111-2380）在 2188 行 `tracer = torch.fx.proxy.GraphAppendingTracer(self)`，然后 Pass 1 扫图建 symbol→Proxy 映射（2228-2243：SymInt placeholder 直接建 Proxy；张量 placeholder 的形状符号记 `(node, dim, divisor)`；unbacked 符号走 `node.meta["unbacked_bindings"]` 的 keypath），Pass 2 惰性发射 `sym_size.int`/`floordiv` 等恢复子图（2305-2346），再用 sympy 解释器 + hash-cons 把整个 sympy 表达式降成 FX 子图（2257-2289）。`_resolve_unbacked_binding`（2048-2109）按 keypath 逐步 emit `size/stride/getitem/floordiv`。

**结论**：`Graph.create_node` 是唯一的写入口——tracing 只是"让 Python 帮你调 create_node"，passes 是"你自己调 create_node"。这让两条产出的图完全同构，Dynamo 图可以直接喂给手写 FX pass。

另一个易踩点写在 docstring 里（2139-2146）：默认插入点是图尾，**已有 output 节点的图上直接调 call_function 会把节点插到 return 后面变孤儿**，必须 `with graph.inserting_before(graph.output_node()):`。

## 9. str(graph) 与 Python 源码发射：为什么打印出来就能跑

两个打印入口，两种形态：

**`__str__`（2571-2587）**：人类可读 SSA 风格（类 docstring 1435-1442 的示例）——每行 `%name : [num_users=N] = op[target=...](args=..., kwargs=...)`，靠 `Node.format_node` 顺带收集 placeholder 名拼出 `graph(x, y):` 签名。这是调试视角。

**`python_code(root_module)`（2462-2543）→ `CodeGen._gen_python_code`（502-1122）**：机器可执行形态，FX 的灵魂。流程：

1. **独立命名空间**（NOTE: Graph Namespaces，2489-2508）：生成源码里的局部名（节点值）和全局名（函数/类型引用）必须在**一个新 _Namespace** 里统一去重——node.name 只在图命名空间里唯一，源码层还要和 `add_global` 注册的 `torch/operator/inf/nan` 等共存（532-562）；实现手法是 `override_node_repr`（2519-2530）：临时把每个节点的 `_repr_fn` 换成"向源码命名空间要名字"，结束后还原——Node 的 repr 协作式设计（2511-2515 注释）在这里兑现；
2. **逐节点 emit**（`emit_node` 780-1037，按 op 分派）：placeholder → 函数签名参数（869-883，含类型注解与默认值）；call_method → `x.relu(...)`（884-893）；call_function → `global_name(args)`（894-1005），其中 `_operator` 的魔法方法被美化回 `a + b`（`magic_methods` 表 2913-2942，899-912），inplace 变体美化成 `a += b; node = a`（916-924），双参 getattr 特判成属性访问 `a.b`（928-940），boxed 参数拆成独立局部变量行（941-1002）；call_module/get_attr → `self.submod.path(...)`（1006-1024）；output → `generate_output`（1025-1036，返回注解写回签名）；
3. **last-use 清理与行号映射**：每个节点前埋 `# COUNTER: i` 注释（1051），body 经 `_body_transformer` 后再扫一遍剔除 counter 并生成 `_lineno_map`（1094-1105）——**生成代码行号 ↔ 节点索引**的映射，profiler/tlparse 归因全靠它；
4. **收尾**：空图发 `pass`（1069-1073）保语法合法；被 wrap 的函数补 `torch.fx.wrap("name")` 语句（1075-1079）；最后拼 `wrap_stmts + def forward(...): + 缩进 body`，返回 `PythonCode(src, globals_, _lineno_map, _prologue_start)`（1110-1122）。

verbose 模式（786-849）把 node.meta 的 example value（fake tensor/DTensor/SymInt）变成类型注解字符串 `: "f32[s0, 64]"`——这就是 `TORCH_LOGS=graph` 输出里那些形状标注的出处，env 开关 `FX_GRAPH_SHOW_STRIDE/DEVICE/META`（524-530）。

### CodeGen 家族（可替换的印码器）

- `CodeGen`（368）：默认，`def forward(self, x): ...`；
- `_BoxedCodeGen`（1131-1170）：签名变 `def forward(self, args_list):`，体内 `args_iter = iter(args_list)` 逐个解包后 `args_list.clear()`——让调用方持有的输入 list 清空、输入张量提前释放（编译器内部路径用）；
- `_PyTreeCodeGen`（1173-1307）：forward 保留用户原始 `(args, kwargs)` 签名，体内 `tree_flatten_spec` 展平到 placeholder，输出 `tree_unflatten(..., self._out_spec)` 还原嵌套结构；
- `_ExportCodeGen`（1310-1359）：`_PyTreeCodeGen` 子类，但输入输出经 `self._in_shuffle_graph/_out_shuffle_graph` 两个 GraphModule 做"洗牌"，placeholder 位置参数直连，贴近 ATen 语义——torch.export 的 flat graph 由此而来。

切换方式：`graph.set_codegen(codegen)`（2780-2782），深拷贝 Graph 时 codegen 一并 deepcopy（1570）。

## 10. 数据流总览

```
用户 nn.Module
   │  symbolic_trace（Tracer+Proxy 记账）           ┐
   │  Dynamo 字节码分析（eval_frame）                ├─全部汇入→ Graph.create_node
   │  FX pass 手写（graph_manipulation/quant…）     ┘
   ▼
fx.Graph ── nodes: 哨兵root+双向链表 ── Node(_prev/_next/_input_nodes/users)
   │  改写: replace_all_uses_with / erase_node / inserting_* / node_copy / DCE / lint
   │  符号: create_size_node / materialize_symints（sympy→子图）
   ▼
Graph.python_code → CodeGen._gen_python_code → PythonCode(src, globals)
   │  GraphModule.recompile: exec(compile(src))        ← str(gm.graph) 可跑的根本原因
   ▼
GraphModule（nn.Module，可执行）
   │  AOTAutograd joint graph / Inductor compile_fx / torch.export / 量化 / ONNX
   ▼
编译产物
```

## 11. 值得记的实现细节

- `_Namespace.create_name` 的 `_base_count`（207-217）：候选名带数字后缀时按 base 查计数再线性探查，注释明说否则 while 循环二次方；
- `_node_list.__reversed__` 与方向参数（291-314）：同一个类实例化出正/反两种视图，DCE 倒序遍历零成本；
- `create_node` 里 hooks 检查用 `getattr(self.owning_module, "_create_node_hooks", None)`（1653）——Graph 允许脱离 GraphModule 独立存在（`Graph()` 直接建），所以一切 module 相关能力都要 None-guard；
- `__deepcopy__` 手写（1555-1584）：链表结构对默认递归 deepcopy 极不友好（长图爆栈），迭代式 graph_copy + memo 复用是教科书解法；
- `materialize_symints` 的 meta 双键约定（2166-2184）：export 风格 `meta["val"]` 与 dynamo 风格 `meta["example_value"]` 并存，读写都做 fallback，新节点还要"镜像"周围图的键约定（`_set_node_val`）——两个编译前端的历史包袱被 Graph 层抹平；
- `emit_node` 不自带换行（1044-1045 NOTE），依赖 `delete_unused_values` 收尾追加——两个函数的输出交错拼装成最终 body。

## 12. 小结

graph.py 用最朴素的两个字典型数据结构（双向链表存顺序、互转置 dict 存依赖）撑起了 PyTorch 2.x 的公共 IR。设计上三个决定性选择：**(1) create_node 单一写入口**——tracing/程序化/Dynamo 三条路同构汇入；**(2) IR 即可执行 Python**——python_code/CodeGen 让任何图随时退回 eager，调试性和 `lint()` 一样是一等公民；**(3) 结构性操作只暴露少数正交原语**（插入点/替换/删除+不变量），复杂 pass 全部在这层之上组合。理解了这三点，Dynamo→AOTAutograd→Inductor 之间传递的"那张图"就不再是黑盒。

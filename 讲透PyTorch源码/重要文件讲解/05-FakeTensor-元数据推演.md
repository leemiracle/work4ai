# 05 · FakeTensor fake_tensor.py — 元数据推演机器

> 源码: `torch/_subclasses/fake_tensor.py` (3881 行) | 图层: `layer:export-subclasses` | 复杂度: complex
> 一句话:它定义了一种**没有数据的张量**——只推演 shape/dtype/device/alias 等元数据,
> 让 Dynamo/export/Inductor 能在零内存开销下"空跑"整个模型,是 PT2 抽象解释(abstraction)的基石。

---

## 1. 架构位置:谁在用它,为什么存在

knowledge graph 把它归入 `layer:export-subclasses`(导出与张量子类机制层,tour order 9)。
核心洞察来自 tour 描述:"捕获的图交给后端前,需要推演每个算子输出的形状与元数据——
FakeTensor 没有 Real Data,只做 shape/dtype/device 推演,让追踪零内存开销"。

反向依赖(29 条 incoming 边)刻画了它的消费者版图:

- **Dynamo 前端**: `eval_frame.py`、`output_graph.py`、`variables/builder.py`(把用户真实参数 fakify 后喂进符号执行);
- **torch.export**: `export/_trace.py`、`exported_program.py`(严格模式导出全程在 fake 世界里跑);
- **Inductor**: `codecache.py`、`graph.py`(编译期对 FX 图做 shape/stride 预推演);
- **FX passes**: `fake_tensor_prop.py`(对已捕获图做纯 fake 的 ShapePropagation)。

正向依赖里最关键的三家:
- `meta_utils.py` 的 `MetaConverter`——真正干"从真实张量抄元数据"的活;
- `fake_impls.py`——各个具体算子的 fake 规则(nonzero/item/index 等数据依赖算子在这里处理);
- `torch/fx/experimental/symbolic_shapes.py` 的 `ShapeEnv`——符号形状引擎,与本文件双向咬合。

## 2. 为什么"没有数据的张量"值得 3900 行代码

编译器要回答的核心问题是:给定输入,每个中间张量的 **shape/stride/dtype/layout/设备/别名关系** 是什么?
最朴素的答案是真跑一遍——但那意味着为一个大模型分配全部中间内存,还得有 GPU。
FakeTensor 的答案:**只保留元数据,扔掉数据**。底层实现上,每个 FakeTensor 包着一个
`device=meta` 的真实张量(meta device 的分配是 no-op,不占内存),再外挂一个 `fake_device`
字段(L834-846 的类注释说得直白:meta 张量不建模设备传播,FakeTensor 额外携带
`fake_device` 来追踪"本应使用的设备")。于是 `torch.zeros([4096,4096], device="cuda")`
在 fake 模式下成本约等于一次 dict 更新。

由此获得三个杠杆:
1. **零内存 tracing**:export/compile 时不需要真权重,Dynamo 甚至可以只看参数元数据;
2. **跨设备推演**:没有 GPU 的机器上也能模拟 CUDA 执行路径(配合 `__enter__` 里把
   CUDA device guard 换成 NoOp 的技巧,L1722-1725);
3. **作为算子契约测试场**:meta kernel 写错(输出 shape 不对)会在 fake 层被交叉验证抓到。

## 3. FakeTensor 类解剖 (L834-1330, 约 500 行)

`class FakeTensor(Tensor)` 继承自真 Tensor,所以 Python 层一切属性访问走 Tensor 的
C 实现,但数据在 meta device 上。关键字段(L843-867):

- `_fake_device: torch.device` — 逻辑设备("本应在哪");
- `fake_mode: FakeTensorMode` — 反向指针,指向创建它的模式;
- `constant: Tensor | None` — 常量折叠通道(见 §7);
- `real_tensor` — `propagate_real_tensors` 实验路径中携带的真值影子;
- `pytype / dispatch_keys` — 原张量的 Python 类型与 dispatch key 集合(fake 不完整模拟它们,需单独记账);
- `nonzero_memo / item_memo / unique_memo / ...` — 数据依赖算子的 SymInt 记忆(见 §8)。

### 3.1 device 的双重语义 —— `[in_kernel_invocation]` (L1610-1620)

```python
@property
def device(self):                       # L897-903
    if self.fake_mode.in_kernel_invocation:
        return torch.device("meta")
    else:
        return self.fake_device
```

这是全文件最精妙的一点:**用户代码里 `x.device` 返回逻辑设备**(让 `if x.is_cuda`、
`torch.zeros(..., device=x.device)` 表现得像真张量);**而 meta kernel 执行期间返回 meta**
(kernel 内新分配应落在 meta、`is_meta` 检查应为真)。`in_kernel_invocation` 这个 bool
由 `in_kernel_invocation_manager`(L717)上下文管理器翻转,`FakeTensor.__torch_dispatch__`
处理 `prim.device.default` 时也遵守同一协议(L1116-1124)。

### 3.2 dispatch key 伪装 —— Note [Fake Tensor Dispatch Keys] (L917-930)

fake_device 是 CUDA 的张量,dispatch key 却要落到 Meta kernel,怎么统一?
做法:把 FakeTensor 的 key 集从 `Meta` 换成 `CUDA`(连带 Autocast/Autograd 相关 key,
以建模设备特定行为),`__torch_dispatch__` 位于这些 key 之下、BackendComponent 之上;
进入 kernel 时再把 `Meta` 加进 thread-local 的 **include set**,让分发实际命中 meta kernel。
代价是注释里承认的:dispatch key 优先级高于 Meta 的后端可能走错路。
`is_mkldnn`(L875)就是 `dispatch_keys` 记账的一个下游补丁——layout 查询要看记录的 keys 而非 meta 事实。

### 3.3 `__new__` 与数据指针防御 (L948-1073)

`FakeTensor.__new__(fake_mode, elem, device, ...)` 要求 `elem` 必须已经是 meta 张量
(L1038-1041 有 assertion),默认还**禁止 fake meta 设备**(`allow_meta=False`,
L1049-1053)——因为"你在 fake 一个 meta 张量"通常意味着你把本该传真张量的地方传错了。
L1033-1036 是另一道防御:`_set_throw_on_mutable_data_ptr` 让任何对 fake 张量
`data_ptr()` 后尝试改写底层(未分配的)内存的代码立刻爆炸,而不是静默 segfault。

## 4. `__torch_dispatch__`:张量子类的扩展点协议

PyTorch 张量子类机制的总纲:任何 `Tensor` 子类实现 `__torch_dispatch__` 类方法后,
所有涉及该子类张量的 **ATen 算子调用**都不会走常规 kernel,而是改道到这个方法,
拿到 `(func: OpOverload, types, args, kwargs)`——func 是完整的算子 schema 对象。
这是"用户可插拔的分发层",torch.compile 的三大子类(FakeTensor、FunctionalTensor、
各类 wrapper subclass)全部挂在这一个钩子上。

本文件有**两层** `__torch_dispatch__`,分工不同:

1. **`FakeTensor.__torch_dispatch__`** (L1107):子类层兜底。只处理三类事:
   `prim.device.default` 的双语义设备查询(L1116)、`_DISPATCH_META_HANDLERS` 里的
   属性快路径(size/stride/numel,L1135)、以及对**不认识的其他子类返回 NotImplemented**
   (L1143-1149,把控制权让给下一个 dispatch 处理者——这是子类互操作的关键礼节)。
2. **`FakeTensorMode.__torch_dispatch__`** (L1694):模式层主战场。注意它开头就断言
   "进入这里时 FAKE key 的 mode 必须已被摘下"(L1702)——模式协议是先 pop 再调用,
   防止无限递归;真正的逻辑在 `dispatch()` (L2481)。

## 5. FakeTensorMode:总控状态机 (L1528-3510, 约 2000 行)

`FakeTensorMode(TorchDispatchMode)` 是**进程内可同时存在多个**的推演引擎实例。
类属性里就有全局状态:`cache`(dict)、`cache_hits/misses`、`epoch`(L1529-1535)。
`__init__` (L1552) 的关键参数:

- `shape_env: ShapeEnv | None` — 传入则启用符号形状;`static_shapes` 默认 = `shape_env is None`(L1585-1588);
- `allow_fallback_kernels=True` — 允许无 meta 实现时回退真 kernel(见 §9);
- `export=False` — 导出模式的开关会影响 item memo 策略(L1559-1568 的长注释:防止
  deferred runtime assert 意外变 guard);
- `_mode_key = TorchDispatchModeKey.FAKE` (L1636) — 标记自己是 **infra mode**,
   分发优先级低于用户模式:用户模式能看到"进入 fake 前的世界"。

### 5.1 嵌套协议 (L1713-1756)

`__enter__` 用"摘下-比较-恢复"三步处理嵌套:先 `_unset_dispatch_mode(FAKE)`,
若摘下来的不是自己(说明外层有别的 fake mode),记入 `enter_stack` 元组并在退出时
**恢复外层模式**。同一个 mode 重复 enter 则是 no-op。注释 (L1648-1657) 给出 canonical
场景:**导出 fake 模型时内外两个 fake mode 并存**——外层是用户建的(无 ShapeEnv),
内层是 Dynamo 建的(带 ShapeEnv 负责动态形状符号化),两阶段各司其职。这就是
"fake mode nesting" 的官方语义,也是 sharp edge 高发区(见 §10)。

### 5.2 dispatch 优先级链 (L2481-2512 → L2703-3234)

`dispatch()` 的主干 `_dispatch_impl` 是一条精心排序的 fallback 链,顺序即语义:

1. `_DISPATCH_META_HANDLERS` — size/stride/numel 等属性查询直接服务 (L2492);
2. **常量折叠**:全部输入带 `constant` 且无符号尺寸 → 真跑 kernel,输出标记为常量
   (L2827-2864;`nondeterministic_seeded`/`inplace_view` 除外——随机与视图内联会破坏 memo);
3. 高阶算子:查 `registered_hop_fake_fns` (L2875-2887);
4. **Python meta 表** `torch._decomp.meta_table` 有实现则跳过分解直接走下面;
5. 否则 **Python decomposition 表**(有符号尺寸时优先,L3091-3103),再否则
   `func.decompose()`(CompositeImplicitAutograd 分解,L3105-3109);
6. prims 的 `prim_meta_impl` (L3117-3125);
7. **用户注册的 fake 规则**:`torch._library.simple_registry` 里 `register_fake` 的
   kernel (L3150-3160),自定义算子的正门;
8. `op_implementations_checks`(构造函数参数改写等,L3186-3192);
9. **不安全回退** `run_fallback_kernel` (L3194-3210):仅当无符号尺寸且命名空间在
   白名单(aten/prims 等,L3241-3250)才允许;
10. 最后:在 `in_kernel_invocation_manager` 下**真跑 meta kernel**(L3221-3223),
    输出经 `wrap_meta_outputs_with_default_device_logic` (L3317) 包装修正设备。

`wrap_meta_outputs_with_default_device_logic` 做设备一致性收尾:用
`_find_common_device` 算出公共设备,meta 输出经 converter 包成带 `fake_device` 的
FakeTensor;若 meta kernel 输出设备与公共设备不符则报错——这是对 kernel 的
**隐式契约检查**。`alias/detach` 特判保留输入的 `dispatch_keys`(L3331-3337)。

### 5.3 dispatch 缓存 (L1529, L1784-1873)

`_cached_dispatch_impl`:用 `_CacheKeyState(shape_env)` 构造 cache key(张量只以
`TensorMetadata` 参与 key,所以 key 便宜),查 `FakeTensorMode.cache`(类级全局)
或 `shape_env.fake_tensor_cache`(符号场景挂到 ShapeEnv 生命周期)。
**hit 路径不重跑 kernel,而是凭缓存里的 TensorMetadata 现场 `torch.empty_strided`
(meta) 重建输出**(L2375-2397);view 算子直接 `set_` 到输入参数的 `untyped_storage()`
重建别名(L2390-2397)。negative entry(`_DispatchCacheBypassEntry`)记录"该输出
不可缓存"的原因避免重复检查;`cache_crosscheck_enabled` 时会禁用缓存空跑一遍
交叉验证(L1846-1853)——测试专用的一致性武器。`_validate_symbolic_output_for_caching`
(L3511) 负责符号输出的可缓存性裁定。

## 6. FakeTensorConverter:真↔假的边界海关 (L393-745)

真实张量进入 fake 世界必须经 `from_real_tensor` (L487)。要点:

- **memo 幂等**:`_get_memo` 按 `MetaTensorId` 查表(L471-479),同一个真张量多次
  fakify 得到同一个 FakeTensor——这是别名关系不破碎的第一道保险;
- **符号化入口**:带 `shape_env` 时把 source/`symbolic_context` 传给 `MetaConverter`
  (L552-559),由 symbolic_shapes 在这里决定每个维度是静态 int 还是 SymInt
  (`_dynamo/variables/builder.py` 正是从这里把用户参数变成符号形状输入);
- **0 维 CPU 标量的 item memo**(L586-607):int 全系 + float64 才允许装具体值,
  float32/16 不行——f32→f64 的语义漂移是可观察行为;
- **常量别名失效**:`constant_storage_mapping` 用 `StorageWeakRef` 索引所有共享
  同一 storage 的常量 fake 张量(L413-448);`const_t.add_(...)` 这类写入发生时,
  `invalidate_constant_aliases` 把同 storage 的所有常量一键打回非常量。
  这是常量折叠正确性的核心:别名 + mutation = 常量必须作废。

## 7. 常量折叠与 real-vs-fake storage 语义

fake 张量的"storage"是 meta 的、不占内存的;真实数据只存在于 `constant` 通道。
两条规则维持这个世界观:

1. **常量算常量 = 常量**(L2827-2864):全常量输入时,在 `no_dispatch()` 下用真常量
   真算,输出重新 fakify 成新常量(`make_constant=True`)。`no_dispatch` 在这里
   "VERY DANGERous(segfault 级)"(L2789-2791)——若误对 wrapper 子类真张量关分发,
   会绕过子类协议直接写底层;
2. **fallback 时数据是借来的** (L3573-3635):`run_fallback_kernel` 给每个 fake 输入
   `torch.zeros_like(e, device=e.fake_device)` 造真零张量,真跑 kernel,再从输出
   **反推** fake 元数据。注意它拒绝 `inplace_view`(L3583)、拒绝输出 alias 到输入
   storage 的情况(L3620-3625)——因为零张量间的 alias 关系不可信,照抄会把
   "独立的张量"误标成"共享视图"。

`propagate_real_tensors` 实验路径(L2918-3057)是第三种语义:fake 与 real 并行推演,
逐 op 用 `_maybe_infer_fake` 交叉比对(L2514-2555,SymInt 用 ShapeEnv 代入判定相等),
mismatch 可配置为自动改写 fake kernel(`generate_fake_kernels_from_real_mismatches`)。
这是把 fake 层当"meta kernel 的单元测试"的新方向。

## 8. 符号形状集成:与 symbolic_shapes.py 的咬合

`ShapeEnv` 不在本文件,但没有它,动态形状编译就无从谈起。咬合点:

- **入口**:converter fakify 时按 `symbolic_context` 为每个尺寸建 SymInt;
- **推演**:meta kernel 里,`empty([s0+1, 4])` 的输出 shape 是 sympy 表达式;
  `has_symbolic_sizes` (L2733-2735) 会改变 dispatch 链走向(优先 Python 分解,
  禁止 fallback——真 kernel 不认识 SymInt);
- **guard**:推演中产生的布尔约束(如 `Eq(s0, s1)`)经 ShapeEnv 沉淀为编译产物的
  runtime guard;`maybe_suppress = shape_env.suppress_guards`(L2364-2368)允许
  cache 重建等**内部操作**不污染 guard 集;
- **unbacked SymInt 与数据依赖算子**:`nonzero()/item()/unique()` 的输出尺寸依赖
  数据,推演不可知。方案是 `SymNumberMemoDescriptor` (L761-831) 描述符:第一次
  调用时经 ShapeEnv `create_unbacked_symint()` 分配一个"无符号上界"的新符号
  (fake_impls.py L852、L1361-1369),memo 记住 `(值, version_counter, epoch)`
  三元组——张量被改(`_version` 变)或重推演(`epoch` 变,L1533-1535)即失效,
  保证同一张量同一状态下 item() 结果一致。`allow_scalar_outputs=False`(L1592)
  则是 Dynamo 语境下默认禁止裸标量泄漏出图。

## 9. 异常分类学:把"推演失败"变成可路由的信号 (L150-192)

这个文件定义了一整套异常,**每种对应一类被精确认知的失败**:

| 异常 | 含义 | 典型来源 |
|---|---|---|
| `DataDependentOutputException` | 输出依赖数据,静态不可知 | `nonzero`/`item` 无 ShapeEnv 时(fake_impls L848/1363/1660) |
| `DynamicOutputShapeException` | 禁止动态形状时输出尺寸是符号 | static_shapes 模式(L1907 注释) |
| `UnsupportedOperatorException` | 无 meta/fake 实现且不许 fallback | L3207 |
| `FakeTensorDeviceMismatchError` | 输入设备不一致 | `_find_common_device` |
| `UnsupportedFakeTensorException` | 该类张量尚不支持 fakify(如 quantized,L519-520) |
| `MetadataMismatchError` | fake/real 交叉验证失败 | L2545/2577 |

Dynamo 在 `_dynamo/exc.py`/`utils.py` 消费这些异常,翻译成 graph break 或
recompile 决策——错误处理本身就是编译器的控制流。

## 10. Sharp edges:官方注释里承认的坑

1. **fake mode 嵌套**:内外双 mode(导出 fake 模型)是支持的场景,但任何
   `maybe_get_fake_mode`(L294,从张量/调用栈/TLS 三处猜当前 mode)的误判都会让
   推演混用两个 mode 的 converter/ShapeEnv,症状是莫名的 symbol 冲突;
2. **数据依赖算子**:没有 ShapeEnv 时 `nonzero` 直接炸 `DataDependentOutputException`;
   有 ShapeEnv 时也要靠 unbacked SymInt + 上界推理续命,精度损失是常态;
3. **常量 + mutation + 别名**:常量折叠依赖 storage 反查失效机制,任何遗漏路径
   (新写的 inplace 算子忘了 `invalidate_written_to_constants`,L2889)都会让
   stale 常量污染后续推演;
4. **fallback kernel 的别名盲区**(L3614-3617 的 TODO 自认):输入元数据变化
   不会检测、输出与输入的 alias 只能保守拒绝,无法正确重建;
5. **`in_kernel_invocation` 非线程安全**(L1622-1624 自注),多线程共享一个
   fake mode 会互相污染 device 语义;
6. **mkldnn 等非 strided 布局**只能靠 `dispatch_keys` 记账 + 特判
   (`is_mkldnn`/`to_dense` L875-895、L3065-3076),是补丁摞补丁的重灾区。

## 11. 一图流:一次 `fake_x = fake_y + 1` 的旅程

```
torch.add(fake_y, 1)
  → dispatcher: keys=Meta(伪装自 fake_device), __torch_dispatch__ 层命中
  → FakeTensorMode.__torch_dispatch__ (L1694) → dispatch (L2481)
  → cache key = (add, TensorMetadata(y), 常量) → miss
  → _dispatch_impl: 无子类、非常量、无符号尺寸 → meta_table 无 → 
    最终 in_kernel_invocation_manager 下 func(*args) 命中 C++ meta kernel (L3222)
    [此刻 y.device == "meta",分配落在 meta]
  → wrap_meta_outputs_with_default_device_logic (L3317):
    _find_common_device → from_meta_and_device 包成 FakeTensor(fake_device=cuda)
  → 结果写入 FakeTensorMode.cache
```

理解了这个循环,就理解了 torch.compile 的"编译期张量世界"如何以零数据成本运转——
后面 FunctionalTensor(functionalization,同层姊妹文件)再把这个世界的视图/mutation
关系规范化,后端拿到的才是干净可编译的图。

> 延伸阅读:`meta_utils.py`(MetaConverter 的符号化细节)、`fake_impls.py`
> (数据依赖算子规则)、`symbolic_shapes.py`(ShapeEnv/guard/undo 引擎本体)、
> `fx/passes/fake_tensor_prop.py`(图上批量推演的消费者用法)。

# 09 · nn.Module module.py — 神经网络基类

> 源码: `torch/nn/modules/module.py` (3066 行) | 图层: `layer:nn-modules` | 复杂度: complex
> 一句话:`Module` 是 torch.nn 的根类——它把"参数、缓冲区、子模块"三种状态塞进三个 dict,
> 用 `__setattr__` 拦截赋值实现自动注册,让任意嵌套的模型树获得统一的
> 设备迁移 / 序列化 / hook / train-eval 语义;全仓库 85 个类直接继承它。

---

## 1. 架构位置:nn 模块层的根

knowledge graph 中 `file:torch/nn/modules/module.py` 属于 `layer:nn-modules`
("torch.nn 的 Module 体系、容器与线性/卷积/归一化/RNN 等标准层"),出现在 **Tour #4**
("nn 模块体系与优化器")的核心节点。图里 `class:...module.py:Module` 是**最大的 class 节点**
(lineRange 407-3066,77 个方法),收到 **85 条直接 `inherits` 边**:`_ConvNd`(所有卷积)、
`_NormBase`(BatchNorm/LayerNorm/RMSNorm 之祖)、`Sequential`/`ModuleList`/`ModuleDict`/
`ParameterList`/`ParameterDict`(容器)、`_DropoutNd`、RNN 家族、padding 家族……
换句话说:torch.nn 里**除 Function 式接口外的每一个类,追根溯源都是 Module**。

它的存在回答的问题是:Tensor + autograd 已经能算梯度了,为什么还要一层抽象?
因为训练一个模型需要的不是单个张量,而是**一棵参数树**——需要统一遍历(喂给 optimizer)、
统一搬设备、统一存取 checkpoint、统一切换 train/eval、统一插调试探针。
Module 就是这棵树的节点协议,所有横切能力都长在这一个类上。

文件结构(L21-404 的"类外"部分常被忽略,但很重要):
- `_IncompatibleKeys`(L40-51):load_state_dict 的返回值 namedtuple,全匹配时 repr 为
  `<All keys matched successfully>`;
- `_WrappedHook`(L74-110):给 hook 挂 weakref 指向所属 module 的包装器(见 §5);
- **8 个模块级全局 hook 注册函数**(L139-385):`register_module_forward_hook` 等,
  写入 L113-122 的 6 个模块级 `_global_*_hooks` OrderedDict——这是**进程级全局状态**,
  torch.compile 的密探(nn module hooks)、profiler 都靠它;
- `_forward_unimplemented`(L391-404):forward 的默认实现,raise NotImplementedError。

## 2. 状态模型:三个 dict + 一堆 hook dict

`__init__`(L482-524)刻意绕开自己重载的 `__setattr__`,用
`super().__setattr__(...)` 直写属性(L499-504 的注释明说是为了避免开销)。
初始化的核心是三棵"注册表":

- `_parameters: dict[str, Parameter|None]`——要被优化的张量;
- `_buffers: dict[str, Tensor|None]`——随模型走但不被优化的状态
  (BatchNorm 的 `running_mean`),`_non_persistent_buffers_set` 记录哪些不进 state_dict;
- `_modules: dict[str, Module|None]`——子模块,构成树的边。

外加 `training: bool`(L505,默认 True)和 12 个 hook OrderedDict。
**注意一个"留白"设计:实例上根本没有 `weight` 这样的普通属性**——参数/缓冲区/子模块
只存在于三个 dict 里,普通属性才走 `self.__dict__`。这决定了下面两个 dunder 的分工。

## 3. 注册魔法:`__setattr__` / `__getattr__`

**写入侧**(`__setattr__`,L1980-2083)按 value 类型四路分发:

1. `isinstance(value, Parameter)` → 先 `remove_from` 从其他容器除名(L1981-1987,
   保证一个名字只在一个 dict 里),再 `register_parameter(name, value)`;
2. `isinstance(value, Module)` → 直接入 `_modules`(L2011-2026),沿途跑
   `_global_module_registration_hooks`(L2022-2025,可替换 value——量化/metasz 借此注入);
3. `isinstance(value, Buffer)` 或名字已在 `_buffers` → 走 buffer 分支。
   这里藏着一段自嘲的 `=== HACK ===`(L2053-2081):为了兼容子类"错误地"重写了
   不带 `persistent` 参数的 `register_buffer`,运行时 `inspect.signature` 探测签名再决定怎么调;
4. 其余 → `super().__setattr__`(普通属性)。

于是 `self.conv1 = nn.Conv2d(...)` 这行最普通的 Python,实际执行的是
"把子模块登记进 `_modules`,使其被 named_modules/state_dict/.to() 看见"。
这就是文档(L412-430)说"以普通属性方式赋值即注册"的机制真相。
配套约束:`register_parameter` 拒绝 `grad_fn` 非空的张量(L628-634,
参数必须是 leaf);名字不允许含 `.`(L568/614/660,因为 `.` 是 state_dict 的路径分隔符)。

**读取侧**(`__getattr__`,L1963-1978)只在**普通属性查找失败后**才被 Python 调用,
依次查 `_parameters` → `_buffers` → `_modules`,找不到才 raise AttributeError。
`__delattr__`(L2085-2094)与 `__dir__`(L3031-3042)同样三表联动。
读写合起来,三个 dict 在用户眼里"透明"——`self.weight` 直接可用,
但 `parameters()`/`state_dict()` 能靠 dict 枚举一切。

## 4. 模块树遍历与迭代器族

所有 `named_*`/`xxx` 方法共享一个骨架 `_named_members`(L2654-2672):
以 `named_modules()`(L2849-2896,自递归 + memo 去重)为骨架,对每个模块取
`get_members_fn(module)`(如 `module._parameters.items()`),用 `memo` set 对
**张量对象**去重(`remove_duplicate=True` 时权重共享的层只报一次)。
`children()` 是一层,`modules()` 是全树,`get_submodule("net_b.linear")`(L674-737)
则按 `.` 逐段 `getattr` 下钻——docstring 明说它是 O(深度),比扫全树的 named_modules 便宜。
这套遍历是 `optimizer = SGD(model.parameters(), ...)` 背后的实际机制。

## 5. 调用链:`__call__` → `_wrapped_call_impl` → `_call_impl`

`__call__: Callable = _wrapped_call_impl`(L1926)是**类属性赋值**而非 def——
配合 L1789 "torchrec tests the code consistency" 的注释,这个写法被外部项目逐字符校验,
不许动。三层结构:

```
model(x) → __call__ = _wrapped_call_impl (L1783)
    ├─ _compiled_call_impl 非 None → 走 torch.compile 包装(§8)
    └─ 否则 → _call_impl (L1791)
```

`_call_impl` 第一件事(L1792):`forward_call = self._slow_forward if tracing else self.forward`
——jit trace 在跑时换用带 scope 的慢路径(§7)。然后是著名的**hook 快速路径**
(L1795-1798):本模块 4 个 hook dict 和 6 个全局 dict 全空时,直接
`return forward_call(*args, **kwargs)`,零开销——这就是"不用 hook 时 hook 体系免费"的原因。

有 hook 时进入 `inner()`(L1803-1880),执行顺序是理解本文件的钥匙:

1. **forward pre-hooks**:先全局后本模块(L1814-1834),`with_kwargs` 变体可改写
   (args, kwargs),否则只改 args;返回非 None 即替换输入;
2. **backward 钩子的正向铺设**:若有 full backward hooks / backward pre-hooks,
   构造 `BackwardHook(self, ...)`(来自 `torch.utils.hooks`,L1838-1839)并在
   **输入张量上挂 autograd hook**(`setup_input_hook`)——模块级 backward hook
   是用 autograd 节点拼出来的一条"梯度走廊";
3. `result = forward_call(*args, **kwargs)`(L1841);
4. **forward hooks**:先全局后本模块(L1842-1857),返回非 None 替换输出;
5. 输出侧再挂 `bw_hook.setup_output_hook(result)`(L1859-1864);
6. **非 full(旧式)backward hooks**(L1866-1878):从输出里挖出第一个 grad_fn,
   `grad_fn.register_hook(_WrappedHook(hook, self))` 直接挂在 autograd 节点上;
   `_maybe_warn_non_full_backward_hook`(L1562-1631)会检查输入/输出是否
   Tensor 或 Tensor 元组、grad_fn 是否唯一,不满足就 FutureWarning 劝你换
   register_full_backward_hook——旧语义在多 Node/嵌套结构下会丢梯度。

全局与模块 hook 的**合流**发生在 `_get_backward_hooks`(L1535-1553):
full/非 full 两组各自"全局在前、本地在后"。full 与非 full 互斥
(实例级 `_is_full_backward_hook` L1521-1527,全局级 L311-318/374-381,双向检查)。

`_WrappedHook`(L74-110)解决的问题是:挂在 grad_fn 上的 hook 签名是
`(grad) -> grad`,拿不到 module;包装后用 `weakref.ref(module)` 补上 self,
调用时解引用(L85-91,死模块直接 raise "hook of a dead Module"),
还实现了 `__getstate__/__setstate__` 让带 hook 的模块可 pickle。

**异常路径**(L1889-1923):`torch.compiler.is_compiling()` 时直接 `inner()`
(try/except 会污染编译帧);否则 try 包住,异常时补跑所有 `always_call=True` 的
forward hook(L1898-1921,单个 hook 抛错只 warn 不遮蔽原异常),再 `raise`。

## 6. state_dict / load_state_dict:树的序列化协议

**保存**是两段式。`state_dict()`(L2203-2291)负责遍历与钩子编排:
跑 `_state_dict_pre_hooks`(L2273)→ 调本层 `_save_to_state_dict`(L2275)→
对 `_modules` 递归,prefix 拼成 `prefix + name + "."`(L2276-2282,这就是
`layer1.0.weight` 这种 key 的来源)→ 跑 `_state_dict_hooks`(L2283-2290)。
`_save_to_state_dict`(L2152-2178)只写本层:params detach 后写入、
跳过 None 与 non-persistent buffer;并用 `getattr(self.__class__, "get_extra_state", ...)
is not Module.get_extra_state`(L2174-2177)做**类级覆写探测**——只有子类真覆写了
`get_extra_state` 才写 `prefix + "_extra_state"` 键(基类方法直接 raise,
L892-911,是"永不 injured 的哨兵")。版本号 `_version`(L443)随
`destination._metadata` 携带(L2269-2271),供加载侧做 BC 分支。
post-hook 有个精细的兼容补丁(L2115-2137):私有 API 尊重返回值,公共
`register_state_dict_post_hook` 打 `_from_public_api` 标记强制原地改
(修 #117437:旧语义只对根模块生效)。

**加载**镜像对称。`load_state_dict()`(L2539-2652)先拷贝 state_dict(L2588,
允许下游钩子改),然后内嵌递归闭包 `load()`(L2593-2628):对每个子模块用
prefix 过滤出它的子 dict 再下钻;每层跑 `_load_from_state_dict` 后执行
`_load_state_dict_post_hooks`(可原地改 `_IncompatibleKeys`,从而影响 strict 判定)。

`_load_from_state_dict`(L2354-2537)是兼容性博物馆:
- 0.3→0.4 的 0-dim/1-dim 张量 BC(L2440-2447);
- shape 不匹配进 `error_msgs` 而非立刻抛(L2449-2455,最后统一 raise);
- meta 参数 + 非 meta 检查点 → 提示用 `assign=True`(L2457-2468);
- 三种写回路径(L2470-2504):`use_swap_tensors`(future flag,换内存保 identity)、
  `assign_to_params_buffers`(`setattr` 整个换对象,适配 FSDP/meta 初始化)、
  默认 `param.copy_(input_param)`(原地拷,**保住 optimizer 里的参数身份**——
  这就是"先 to/cuda 后建 optimizer"注释的根源)。

## 7. 设备/精度迁移与 jit/trace 兼容层

**`_apply`(L930-1038)是所有迁移的唯一引擎**。递归子模块后,对每个 param
在 `no_grad` 下算 `param_applied = fn(param)`,然后三选一写回:
1. `torch.utils.swap_tensors`(L977-995):future flag 开启、或 tensor 是
   wrapper subclass/FakeTensor 时用——**原对象存储被换**,所有引用(含 optimizer
   持有的)自动跟进;grad 会先置 None 降低 use_count 再换;
2. `param.data = param_applied`(L996-998):shallow-copy 类型兼容时的历史行为
   (`compute_should_use_set_data`,L939-953,受 `torch.__future__` 两个开关控制);
3. 新建 `Parameter` 替换 dict 条目(L999-1006):普通 `.to()` 跨 dtype 的现实路径
   ——**参数对象换新**,这正是"cuda() 会让参数变成不同对象,要在建 optimizer 前调"
   (L1084-1086 docstring)的机制解释。
buffers 最简单:直接 `self._buffers[key] = fn(buf)`(L1034-1036)。
`cuda/xpu/mtia/cpu/type/float/double/half/bfloat16/to_empty/share_memory`
(L1081-1240)全是 `_apply(lambda t: ...)` 的一行包装。
`to()`(L1259-1392)多了 `torch._C._nn._parse_to` 参数归一(L1345)、
整型 dtype 不动只搬设备的规则、以及 meta tensor 报错时指路 `to_empty()`(L1379-1390)。

**jit/trace 垫片**就是 `_slow_forward`(L1763-1781):`torch._C._get_tracing_state()`
存在且 forward 不是 ScriptMethod 时,从 `torch.jit._trace._trace_module_map`
查当前模块在 trace 中的名字,`tracing_state.push_scope(name)` / finally `pop_scope`
——让 torch.jit.trace 记录的图带正确层级命名。`dump_patches`(L441)是更古老的
pickle 补丁开关遗物。

## 8. train/eval、requires_grad_ 与 compile() 交互

`train(mode)`(L2898-2918)自上而下递归设 `self.training` 并对 `children()` 递归;
`eval()` 就是 `train(False)`(L2936)。**模式只是一个 bool 标志**——行为差异完全靠
forward 里 `if self.training:` 自觉实现(Dropout/BatchNorm),基类不做任何调度。
`requires_grad_`(L2938-2959)与 `zero_grad`(L2961-2988,set_to_none 默认 True)
则直接建立在 §4 的 parameters() 迭代器之上。

**`compile()`**(L3057-3066)只有一行:
`self._compiled_call_impl = torch.compile(self._call_impl, *args, **kwargs)`。
与直觉不同,它**不编译 forward,而是编译 `_call_impl`**——hook 编排逻辑一起进图,
`torch.compiler.is_compiling()` 分支(L1889)保证编译帧里异常语义不被 try/except 破坏。
下次 `model(x)` 时 `_wrapped_call_impl`(L1783-1787)优先分发给编译产物。
`__getstate__`(L1928-1931)pickle 时丢弃 `_compiled_call_impl`(编译产物不可序列化);
`__setstate__`(L1933-1958)为旧 checkpoint 回填缺失的 hook dict——新老字段演进全靠
这两个 dunder 兜底。另注意 `_replicate_for_data_parallel`(L3044-3055):
DataParallel 副本浅拷贝 dict 但清空 `_parameters`、置 `_is_replica`,副本参数引用原模块
(zero_grad 的警告 L2970-2977 由此而来)。

## 9. 小结:一个类扛起的横切面

| 能力 | 机制锚点 |
|---|---|
| 自动注册 | `__setattr__` 四路分发 + `remove_from` 互斥(L1980-2083) |
| 属性透出 | `__getattr__` 三级 fallback(L1963-1978) |
| 树遍历 | `_named_members` + memo 去重(L2654-2672) |
| 调用/hook | `__call__`→`_wrapped_call_impl`→`_call_impl` 快慢路径(L1783-1926) |
| 序列化 | state_dict 前后钩子 + `_save/_load_from_state_dict` 分层(L2152-2652) |
| 迁移 | `_apply` 三种写回策略(L930-1038) |
| 模式 | train/eval 递归布尔传播(L2898-2936) |
| 编译 | `_compiled_call_impl` 热切换(L1783, 3057-3066) |
| trace | `_slow_forward` scope 推送(L1763-1781) |

理解了 Module,就理解了 PyTorch "nn 侧"的全部 API 表面:它没有用任何黑魔法,
靠的是**把注册收进 dict、把调用收进单一 choke point、把遍历收进递归骨架**三个朴素决定,
再以大量 BC 垫片(版本号、0.3 布局、HACK 分支、__setstate__ 回填)维持十年兼容。

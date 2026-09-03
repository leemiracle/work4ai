# 06 · Inductor compile_fx.py — 编译后端总入口

> 源码: `torch/_inductor/compile_fx.py` (3769 行) | 图层: `layer:inductor-backend` | 复杂度: complex
> 一句话:它是 torch.compile 默认后端 Inductor 的"总调度台"——从 Dynamo/AOTAutograd 手里接过 FX 图,
> 串起 pre-grad → joint → post-grad 三段图优化、FX graph cache 查询、IR lowering、scheduler、Triton/C++ codegen,
> 最终交回一个可直接运行的 `CompiledFxGraph`。

---

## 1. 架构位置:PT2 编译栈的最后一棒

PT2 全栈:`torch.compile` → **Dynamo**(字节码捕获,见 04 篇 eval_frame)→ **AOTAutograd**(joint 图切分)
→ **Inductor**(本篇)。knowledge graph 把 `torch/_inductor` 整体标为 `layer:inductor-backend`
("FX 图到 Triton/C++ 代码生成、autotune、fusion 决策与 FX graph cache"),tour #10 明确指出:
**compile_fx.py 是总入口(fusion 决策、图 pass 调度、缓存管理)**。

它的挂载点在 `torch/_inductor/__init__.py:59-61`:`compile()` 直接调 `compile_fx(gm, example_inputs, config_patches=options)`。
所以当你写 `torch.compile(model, backend="inductor")`(默认)时,Dynamo 捕获的 FX 图最终流入的就是本文件的 `compile_fx`。

关键认知(文件 docstring L3095-3105 原意):**compile_fx 虽然住在 `_inductor` 包里,它自己并不直接编译单个图**;
它负责调用 AOTAutograd,并在切分出前向/后向图后被**回调**到 `inner_compile`(默认 `compile_fx_inner`)做真正的编译。
即"外层编排 AOTAutograd + 内层逐图编译"的双层结构。另注意 NB(L3103):**该函数接管输入 GraphModule 的所有权,可能原地修改它**。

依赖图(knowledge graph `depends_on`/`imports` 边,共 60 条出边)核心邻居:
- `fx_passes/pre_grad.py` / `joint_graph.py` / `post_grad.py` — 三段 FX 图优化
- `graph.py`(GraphLowering)— FX 图 → IR 的降级器
- `ir.py` — IRNode 体系(Loops/Pointwise/Reduction/ExternKernel...)
- `codecache.py`(FxGraphCache/AotCodeCompiler)— 编译产物缓存
- `decomposition.py` — ATen 算子分解表
- `virtualized.py`(`V`)— 编译期全局上下文单例
- 上游: `torch/_dynamo/*`(compiled_autograd、device_interface)、`torch/_functorch/aot_autograd`

## 2. 双层入口:compile_fx 与 compile_fx_inner 的回调反转

```
Dynamo backend 回调
 └─ compile_fx (L3086)                      ← 外层:一次编译请求(整个子图)
     ├─ config_patches 递归重入 (L3122-3132)
     ├─ cpp_wrapper/fx_wrapper 特殊通道 (L3147-3203)
     └─ _maybe_wrap_and_compile_fx_main (L3249)  ← 规范化包装(返回值 tuple 化/输入扁平化)
         └─ _compile_fx_main (L3299)         ← 真正的主体
             ├─ (1) 组装 fw/bw/inference compiler + partition_fn
             └─ (3) dynamo_common.aot_autograd(...)(L3500)
                 ├─ (3a) 用 decompositions 建 joint graph
                 ├─ (3b) partition_fn 切 fw/bw(内跑 joint-graph passes)
                 ├─ (3c) 回调 fw_compiler / bw_compiler
                 │     ├─ compile_fx_forward (L2792)
                 │     └─ compile_fx_backward (L2945)
                 │         └─ inner_compile = compile_fx_inner (L1018)
                 │             └─ _compile_fx_inner (L1098)      ← 内层:编译"一张"图
                 │                 └─ fx_codegen_and_compile (L2103)
                 │                     └─ _InProcessFxCompile.codegen_and_compile (L1535)
                 └─ (3d) 组装 fw+bw 返回 runnable
```

`_compile_fx_main` 的 docstring(L3308-3318)就是这条流水线的权威自述。pre-grad passes 的调用时机有个细节
(L3328-3329 注释):它们**不在** `_compile_fx_main` 里直接跑,而是作为 `pre_grad_passes=run_pre_grad_passes`
回调(L3509)挂给 AOTAutograd 的 `aot_module_simplified`,在 **autograd cache 查询之后**才执行——缓存命中时省掉整段 pass 开销。

## 3. 外层 compile_fx:接收 FX 图并对接 AOTAutograd

### 3.1 入口规范化(L3086-3212)
- `decompositions` 参数可由调用方传入,包装成 picklable 的 `_ConstantDecompTable`(L3072,模块级 dataclass,
  以 `(module, qualname)` 地址支持 pickle-by-reduce),否则用 `select_decomp_table`(decomposition.py);
- `config_patches` 非空时递归重入自身(L3122),并把 `inner_compile` 也包一层 `config.patch`——因为
  **backward 编译可能发生在 compile_fx 返回之后**(惰性编译),配置必须跟着回调走;
- 有 CUDA/XPU 输入时立刻 `AsyncCompile.wakeup()`(L3141-3145)预热子进程编译池;
- `cpp_wrapper`/`fx_wrapper`(AOTInductor 路径)走独立通道(L3147-3203):patch `get_cpp_wrapper_config()`,
  fakify script objects,并拒绝 compile-on-one-rank(L3148-3169,设备索引烘焙进 C++ guard 不可跨 rank 移植)。

### 3.2 包装层 _maybe_wrap_and_compile_fx_main(L3249-3296)
递归自嵌套的规范化管道:返回值不是 tuple 就 `make_graph_return_tuple`;Dynamo export 图(`_PyTreeCodeGen`)
走 `handle_dynamo_export_graph`;嵌套容器输入走 `flatten_graph_inputs`。Dynamo 正常路径三者皆不触发,
直达 `_compile_fx_main`。

### 3.3 partition_fn(L2637-2701):joint 图怎么切
```python
gm = _recursive_joint_graph_passes(gm, skip_invoke_subgraph=True, ...)  # 先跑 joint passes
return min_cut_rematerialization_partition(gm, joint_inputs, compiler="inductor", ...)  # L2677
```
默认切分器是 functorch 的 **min-cut 重计算切分**——在"保存激活 vs 重计算"之间做最小割权衡。
也支持 `config.custom_partitioner_fn`(须为 `CustomPartitionerFn` 实例,L2686)与 `partitioner_fn_override`
(HOP 子图复用同一 joint-pass + 原生分区器管道)。joint passes 本体在 `_recursive_joint_graph_passes`(L724-769):
常数折叠、去冗余 view、softmax 乘除改写等(fx_passes/joint_graph.py),且**递归处理 invoke_subgraph HOP 嵌套区域**
——pass 之后再补一轮新产生的子图(L760-768)。

### 3.4 fw/bw 编译器回调(L3347-3402)
`fw_compiler` → `compile_fx_forward`;`bw_compiler` → `compile_fx_backward`;`inference_compiler` 在
`config.freezing` 且无 grad 时换成 `fw_compiler_freezing`(L2476:joint passes → 布局优化决策 →
`freeze()` 把常量权重烘焙进图,产出"参数冻结"的推理图)。三者都套 `SerializableAOTDispatchCompiler`,
使其可被 AOTAutograd cache 序列化重放。

### 3.5 AOTInductor 分叉(L3412-3488)
`V.aot_compilation=True` 时(`compile_fx_aot`,L2401,强制 `cpp_wrapper=True` L2416-2418,`V.set_aot_compilation(True)` L2445),
不跑 aot_autograd 而走 `aot_export_module(trace_joint=False)` 导出前向图,`_unlift_graph` 还原签名后交给
inference_compiler——最终产物是 `.so` 文件路径(`CompiledAOTI`,L2034)。

## 4. 内层 compile_fx_inner → _compile_fx_inner:单图编译 + 缓存状态机

`compile_fx_inner`(L1018)只是 kwargs 缺省填充 + cpp_wrapper 配置补丁的薄壳;主体 `_compile_fx_inner`(L1098):

1. **autotune 预热**(L1112-1119):`use_pipelined_autotuning()` 为真时立刻 `AutotuneProcessPool.get_instance().warm_up()`
   (autotune_process.py L1421/L1505)——把 max-autotune 子进程池尽早拉起,与编译流水线并行;
2. **空图短路**(L1125-1144):图中无调用节点且非 aot_mode 时直接 `make_boxed_func(gm.forward)` 返回;
3. **对齐检查表**(L1148,`get_input_idxs_to_check` L2168):对"codegen 假设对齐但运行时未必对齐"的 GPU 输入,
   生成运行时对齐检查(不对齐则 clone)的下标集合;
4. **FxGraphCache 查询**(L1187-1246):`use_cache` 条件 = 未禁缓存 且 (本地 `config.fx_graph_cache` 或远程
   `fx_graph_remote_cache`)且非 aot_mode 且后端支持缓存(codegen 后端经 `init_backend_registration` + 
   `get_wrapper_codegen_for_device` 查询,L1172-1182)。命中路径:`FxGraphCache.prepare_key`(L1227)算键 →
   `load_with_key`(L1238)加载;
5. **四态状态机**:
   - `bypass`(L1293,键生成失败/输入不可缓存):编译但不落盘;
   - `miss`(L1320):`TritonBundler.begin_compile()` → 编译 → 收集 Triton kernel bundle(L1345-1349)→
     `FxGraphCache._save_graph`(L1362)本地+远程落盘;
   - `hit`(L1370):几乎无事可做,只把 cache key 贴回图上;
   - `bundled_autograd_cache`(L1250):编译但不存 FxGraphCache,产物直接进 AOTAutogradCache;
6. 每个缓存动作都有 CompileEventLogger/tlparse 埋点(L1396-1440,`fx_graph_cache_hit/miss/bypass/disabled`);
7. `compiled_graph.post_compile(example_inputs, constants, graph_kwargs)`(L1441)——**cudagraph 录制、
   wrapper 编译等后处理在这里发生**( cudagraph policy 见 L1443-1445)。

所有异常统一包成 `InductorError(e, currentframe())`(L1284/L1315/L1353),配 `ShortenTraceback/SkipFrame` 直通。

## 5. fx_codegen_and_compile 与 FxCompile 执行模式(L2103-2165)

工厂函数:按 `FxCompileMode`(L183:NORMAL/SERIALIZE/SUBPROCESS)选择执行方案——
`_InProcessFxCompile`(默认,当前进程)/`_DebugSerdeFxCompile`(测序列化)/`_SubprocessFxCompile`(子进程编译);
`fx_compile_async` 再包 `_AsyncFxCompile`,`fx_compile_progressive` 包 `_ProgressiveFxCompile`
(先出快速版再用渐进配置 `_get_progression_configs` L233 优化重编)。这套由环境变量
`TORCHINDUCTOR_FX_COMPILE_MODE` 控制(L199-230)。抽象基类 `FxCompile`(L1506)只定义 `codegen_and_compile` 接口。

## 6. _InProcessFxCompile.codegen_and_compile(L1535-2100):单图编译的完整流水线

这是 Inductor 编译一张(前向或后向)图的真实顺序:

1. **shape_env 获取**(L1629-1631):`gm.shape_env` 或从输入重建——动态形状的符号系统入口;
2. **view→reshape**(L1649,`view_to_reshape`):布局优化会把 contiguous 变 channels-last,
   原 view 可能不再合法,必须提前替换(否则 timm resnest/botnet 等模型直接报错);
3. **fake_tensor_prop**(L943-970,补跑 FakeTensorProp,05 篇主角):`torch.no_grad()` 下用 FakeTensor
   解释执行补全每个节点的 meta(shape/dtype/stride)。进 Inductor 后图里已无 autograd API,安全;
4. **post-grad passes**(L1680,`_recursive_post_grad_passes` L772):reinplace、算子删除、偏置解融合、
   构造器搬迁等(fx_passes/post_grad.py)。注意 L780-806 的正确性回退:关闭 post-grad passes 的 lite 模式下,
   若图里有用户自定义 Triton kernel,仍强制跑 reinplace + functional→mutation 分解,否则 lowering 直接报错;
5. **AOTI 常量分离**(L1751-1787,aot_mode only):`split_const_gm`(L814)把可常量折叠子图剥出来单独
   用一个 `GraphLowering(is_const_graph=True)` 编译;
6. **GraphLowering 构造与执行**(L1789-1824):
   ```python
   graph = GraphLowering(gm, example_inputs=..., shape_env=..., ...)
   graph.freeze_runtime_asserts()          # L1818:runtime assert 集合从此封板
   with V.set_graph_handler(graph), V.set_extern_kernel_nodes([]):
       graph.run(*example_inputs)          # L1824:fx.Interpreter 遍历,逐节点 lowering 成 IR
   ```
   `V`(virtualized.py)是编译期全局上下文:graph handler、fake_mode、aot_compilation 都挂在上面,
   使深层代码不靠参数传递就能拿到当前图;
7. **输出 stride 符号化记录**(L1825-1841):每个输出用 `SymExprPrinter` 把 stride 打成 sympy 字符串存进
   CompiledFxGraph——缓存加载时再 eval,保住动态形状下的 stride 语义;
8. **产物分派**(L1851-1917):
   - fx_wrapper AOT:`graph.codegen()[0].gm` 直接拿 GraphModule(L1859);
   - **cpp_wrapper/AOTI**:`graph.codegen_with_cpp_wrapper()` 出 C++ wrapper + kernel 代码 →
     `AotCodeCompiler.compile(...)`(L1895,codecache.py)编译成 `.so`;
   - **默认(Python wrapper)**:`graph.compile_to_module()`(L1913)→ `compiled_fn = compiled_module.call`;
9. **cudagraph 可用性裁决**(L1977-2059):符号形状输入 + `cudagraph_skip_dynamic_graphs` → 禁;
   图里有 cudagraph 不兼容算子(`get_first_incompatible_cudagraph_node`)→ 禁;lowering 检查
   (`check_lowering_disable_cudagraph`);全图零 kernel 时标记 `kernel_free_cudagraph`(L2053-2059);
10. **返回 CompiledFxGraph**(L2080-2100):打包 compiled_fn、GraphLowering、原始 gm、output_strides、
    cudagraph 禁用原因、metrics 增量、static_input_idxs 等——它是 output_code.py 中运行时态的载体。

### lowering 与 scheduler 去哪了?
在 `GraphLowering.run`(graph.py L1140,继承 fx.Interpreter)里:每个 `call_function` 节点经
`run_node`(L1947)查 lowering 表转成 IRNode buffer 表示(fusion 决策也在此层)。codegen 时
`_update_scheduler()`(L3002)构造 `Scheduler(self.operations)`(L3011)做节点排序与 fusion 分组,
`codegen()`(L3013)驱动各后端写代码。**Triton vs C++ 的选择不在 compile_fx 里写死**:
GPU kernel 走 Triton codegen,CPU/extern 走 C++(以及 FallbackKernel 直接调 ATen);
compile_fx 只决定 **wrapper 层**语言:Python(默认)/C++(`cpp_wrapper`,配置见 `get_cpp_wrapper_config`
L2590-2616:`autotune_at_compile_time`、`store_cubin` 等 AOTI 必需项)/FX IR(`fx_wrapper`)。

## 7. 动态形状的五个接触点

1. **shape_env 注入**(L1629):Dynamo 传来的 gm 自带 shape_env,否则 `shape_env_from_inputs` 重建;
2. **fake_tensor_prop 用支持符号形状的 decomposition**(L953 注释 + `enable_python_dispatcher`);
3. **runtime asserts 封板**(L1818):lowering 期间新增的 sizevar 断言在 codegen 时统一生成 shape guard;
4. **符号输入自动禁 cudagraph**(L1978-2003):带 SymInt 的输入图默认不进 CUDA Graph(地址稳定性无法保证),
   并把来源 stack_trace 写进禁用原因;
5. **输出 stride 符号串**(L1825-1841)与 post_compile 时的对齐检查(`inputs_to_check`)。

## 8. 与 AOTAutograd 的接收协议(数据流总结)

```
Dynamo 捕获 aten FX 图 + FakeTensor 例输入
  → backend = torch._inductor.compile (__init__.py L59)
    → compile_fx:接管 gm 所有权
      → aot_autograd(fw_compiler, bw_compiler, partition_fn, decompositions, pre_grad_passes)(L3500)
        [AOTAutograd 侧] joint graph = 前向 + autograd 反向追踪(用 decompositions 分解)
        [AOTAutograd 侧] partition_fn → min-cut 切成 fw graph / bw graph(此处内跑 joint passes)
        [AOTAutograd 侧] 回调 fw_compiler(gm_fw, fake_inputs) / bw_compiler(gm_bw, ...)
      → compile_fx_forward/backward 补 user_visible_output_idxs、static_input_idxs 等元数据
        → compile_fx_inner → FxGraphCache 查询 → (miss) _InProcessFxCompile
          → view_to_reshape → fake_tensor_prop → post_grad_passes
          → GraphLowering.run(FX→IR)→ Scheduler(fusion/排序)→ codegen(Triton/C++)
          → CompiledFxGraph → post_compile(cudagraph 录制)→ 存缓存
  → 返回 boxed callable:输入 list → kernel 启动 → 输出 list
```

`compile_fx_forward`(L2792)的元数据工作值得注意:`user_visible_output_idxs`(L2885-2911,训练图输出 =
原始输出 + 保存激活,需按 `fw_metadata.num_mutated_inp_runtime_indices` 偏移定位用户可见段,供 cudagraph
克隆判定)与 inference 路径的 joint passes(L2845)。`compile_fx_backward`(L2945)则推导 **static backward
inputs**(saved tensors 地址稳定集合,L2981-3001 的两条过近似修正注释是理解 static_input_idxs 语义的钥匙)。

## 9. 设计模式与要点提炼

- **回调反转编排**:compile_fx 把"编译器"作为闭包(fw/bw/inference compiler)交给 AOTAutograd,
  自身只管切分前的准备工作——Inductor 因此能同时服务训练/推理/导出三种模式而主体不变;
- **BoxedBool 可变共享**:`cudagraphs=BoxedBool(...)`(L1552)是引用语义布尔,前向编译中发现的禁用原因
  能被后向编译看见,无需重新传递;
- **V 单例(virtualized)**:graph handler/fake_mode/aot 标志走全局上下文,避免十几层参数穿透;
- **缓存分层**:AOTAutogradCache(最外,跨进程复用整个 aot 编排,`autograd_cache_key` L3702 显式复制
  `_compile_fx_main` 的上下文管理器组合保证键与真实编译一致)> FxGraphCache(单图产物,本地+远程,
  codecache.py)> TritonBundler(kernel 级 cubin 捆绑)> CppCodeCache(C++ 编译单元);
- **正确性优先的降级**:每个可选优化(passes、cudagraph、layout_opt)都有明确的禁用原因字符串
  (`disable_cudagraphs_reason`),可观测、可解释——排障时 `TORCH_LOGS=+inductor` 能看到全部裁决;
- **编译即异常包装**:所有用户可见错误统一 `InductorError` + 帧缩短,防止编译器内部栈污染用户报错。

## 10. 阅读路线建议

先读 `_compile_fx_main` docstring(L3308)建立全局,再沿"一次 cache miss 的前向编译"单线程读:
`compile_fx`(L3086)→ `compile_fx_forward`(L2792)→ `_compile_fx_inner`(L1098)→
`_InProcessFxCompile.codegen_and_compile`(L1535)→ `GraphLowering.run`(graph.py L1140)→
`Scheduler`(scheduler.py)。后三个文件是本系列后续篇章的主题。

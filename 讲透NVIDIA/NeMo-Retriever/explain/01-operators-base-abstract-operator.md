# 01 · operators 基座：AbstractOperator + CPU/GPU mixin + ArchetypeOperator

> 路径相对 `nemo_retriever/src/nemo_retriever/`。

## 角色定位

这是全仓 1702 节点里复用面最广的一组文件：`operators/abstract_operator.py`（70 行）定义所有算子的行为契约，`operators/cpu_operator.py` 与 `operators/gpu_operator.py` 是两个纯标记 mixin，`operators/operator_archetype.py`（120 行）提供"图里放原型、执行时定 CPU/GPU"的延迟绑定机制。抽取、嵌入、重排、入库、查询、agentic——每条管线的每一站都是这三个文件的直接子类。读懂它等于拿到全仓的语法糖密码：graph/README.md 称之为自定义算子的权威出处。

## 内部结构

`AbstractOperator(ABC)` 在 `operators/abstract_operator.py:15`。三个 `@abstractmethod`：`preprocess`/`process`/`postprocess`（`:23-30`），子类必须全实现。`run()`（`:32-36`）按固定顺序串联三者并返回最终 data。`__call__`（`:38-40`）直接委托 `run()`——这个看似多余的别名是接 Ray Data 的关键：`map_batches` 接受 callable class，算子实例本身就能当 transform 函数传进去。

构造侧有两个精心设计：`__init__`（`:18-21`）把全部 kwargs 存进 `_graph_init_kwargs` 并 setattr 为实例属性——图构建期的参数原样留档；`get_constructor_kwargs()`（`:42-57`）用 `inspect.signature(type(self).__init__` 反推构造签名，缺的参数从实例属性（含 `_name` 私有变体，`:54-56`）补齐。这一对组合实现了"执行器侧重建"：driver 构建图 → 序列化类名+kwargs → Ray worker 上 `operator_class(**operator_kwargs)` 重新实例化，重模型（OCR/嵌入模型）从不跨进程序列化。

链式语法 `__rshift__`（`:59-70`）只做一件事：把自己包成 Node 然后委托给 `Node.__rshift__`，于是 `op_a >> op_b >> op_c` 返回立即可执行的 Graph。

两个 mixin 是空类：`CPUOperator`（`operators/cpu_operator.py:8`）与 `GPUOperator`（`operators/gpu_operator.py:8`），docstring 明说执行器用 `isinstance` 检查——GPU 份额调度就落在 `graph/executor.py:571` 的 `issubclass(node.operator_class, GPUOperator)`。典型组合如 `TextEmbedGPUActor(AbstractOperator, GPUOperator)`（`operators/embed/text_embed.py:187`）。

`ArchetypeOperator`（`operators/operator_archetype.py:26`）是第三层：类属性 `_cpu_variant_class`/`_gpu_variant_class`（`:29-30`）挂两个具体变体；类方法 `resolve_operator_class()`（`:50-67`）按资源探测结果挑变体——`prefers_cpu_variant` 优先（`:58-59`）、有 GPU 且有 GPU 变体选 GPU（`:60-62`）、否则回退 CPU。实例方法 `preprocess/process/postprocess/run/__call__` 五件全委托 `_resolve_delegate()`（`:78-91`），委托带缓存：`_delegate_cache_key`（`:114-120`）取 (cpu 数, gpu 数) 二元组，资源没变就复用已构造的 delegate（`:99-100`）——避免每次调用都重新加载模型。样例见 `common/modality/convert/to_pdf.py:193` 的 `DocToPdfConversionActor(ArchetypeOperator)`（CPU 变体在同文件 `:170`）与 `operators/embed/text_embed.py:238` 的 `TextEmbedActor`（`:239` 只挂 `_gpu_variant_class`）。

## 外部连接

上游消费者是 `graph/pipeline_graph.py:30` 的 Node——构造时（`:56`）就调用 `get_constructor_kwargs()` 把 kwargs 冻结进节点。`graph/executor.py:472` 在 InprocessExecutor 里用 `node.operator_class(**node.operator_kwargs)` 重建算子；RayDataExecutor 则把同一对类名+kwargs 作为 `fn_constructor_kwargs` 传给 `map_batches`（`graph/executor.py:883-891`）。资源探测依赖 `common/ray_resource_hueristics.py` 的 `gather_local_resources`（archetype `:55,97` 两处调用）。反向：`operators/base.py` 与 `operators/content.py` 等根模块再导出这组基类供外部 UDF 使用（examples/udfs 的 html_to_markdown 示例即继承此基座）。

## 数据流

单算子视角：`data → preprocess → process → postprocess → data`，data 在库模式内是 pandas DataFrame（列如 bytes/path/text/metadata），跨 Ray stage 时被 `_ArrowPandasOperatorAdapter`（`graph/executor.py:176`）处理 Arrow↔pandas 转换。原型算子视角：`data → ArchetypeOperator.run → delegate.run → data`，delegate 首次调用时构造、之后缓存。整链视角：`op_a >> op_b` 语法糖产出 Graph，`Graph.execute`（`graph/pipeline_graph.py:165-172`）先 `resolve_for_local_execution` 再逐节点 `_execute_node`（`:198-204`，父输出喂子输入，叶输出收集成列表）。

## 设计决策

1. **三段式而非单 process**：preprocess/postprocess 给"输入适配/输出适配"留了标准插槽，让同一 process 内核可以套不同 I/O 形态——执行器与算子作者各自只改自己的三分之一。
2. **标记 mixin 而非构造参数**：`num_gpus` 之类的资源语义用类型系统表达，调度器只看类型不看配置，算子作者无法忘标（忘了标 GPU mixin 就拿不到 GPU）。
3. **kwargs 反射重建而非 pickle**：跨进程传"类名+参数字典"而不是序列化实例，模型权重、CUDA context 都留在 worker 侧，是分布式摄取不炸的根本前提。
4. **原型算子的缓存键用资源计数而非布尔**：`(cpu, gpu)` 二元组（`:114-120`）允许 GPU 热插拔后自动重解析，又不至于每次调用都探测。
5. 基类只有 70 行、mixin 各 20 行——刻意做薄，把"算子是什么"压到最小共识，其余语义全部下放。

## 新人提示

- 写自定义算子的最小清单：继承 `AbstractOperator`(+`CPUOperator`)，实现三方法，然后 `my_op >> downstream_op` 即可入图；examples/udfs/ 有两个现成模板。
- 忘实现任一抽象方法会在实例化时立刻 TypeError——不要绕过 ABC 去继承非 ABC 基类。
- `get_constructor_kwargs` 只认"构造参数名 == 实例属性名（或 _前缀）"，自定义算子若在 `__init__` 里改名存属性，重建时会丢参数。
- 排查"GPU 算子没拿到 GPU"问题时，先确认算子类确实混入了 `GPUOperator`，再看 `graph/executor.py:571` 的 `issubclass` 分支与 `:580-587` 的零 GPU 警告日志。
- 原型算子解析失败会抛 "could not resolve a concrete hardware-specific operator"（`operators/operator_archetype.py:105`）——意味着两个变体类都没配上。

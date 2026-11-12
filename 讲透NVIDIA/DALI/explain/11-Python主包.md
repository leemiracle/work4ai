# 11. Python 主包：nvidia.dali 门面、框架插件与实验后端

## 一、角色定位

这层是 `import nvidia.dali` 后用户接触到的全部世界：`Pipeline` 门面、`fn`/`ops` 算子入口、各框架迭代器插件与 experimental/dynamic 动态模式。Python 层是"薄"的——动态生成算子类、记录符号图、翻译各框架张量，重活在 C++。核心 pipeline.py 单文件 2527 行，`class Pipeline` 在 dali/python/nvidia/dali/pipeline.py:97（约 2000 行百余方法）。

## 二、内部结构

`pipeline_def`（dali/python/nvidia/dali/pipeline.py:2210）在 `enable_conditionals=True` 时经 `_preprocess_pipe_func`（:2121）调用 `_conditionals._autograph.convert(recursive=True, user_requested=True)`（:2124）做 AutoGraph 条件转换；`_generate_graph`（:2150）在 `with pipe:` 里执行函数体，`fn.*` 调用记为 DataNode 并 `set_outputs`。条件运行时栈机为 `_ConditionStack`（dali/python/nvidia/dali/_conditionals.py:177）。

算子层是导入期代码生成：`_load_ops`（dali/python/nvidia/dali/ops/__init__.py:722）枚举 C++ 注册算子、`python_op_factory` 造类并 `setattr` 进子模块；模块尾部即执行 `_load_ops()`（:898），`Reload()`（:754）供插件后装。`fn` 是 ops 的函数式再包装（per-call 设备默认，dali/python/nvidia/dali/fn/__init__.py:68）；纯 Python 算子由 `_get_base_impl`（dali/python/nvidia/dali/ops/_operators/python_function.py:32）按 impl_name 动态解析 C++ 符号。

external_source 甄别点：模式判定不在 `__call__`（dali/python/nvidia/dali/external_source.py:700）而在 `get_callback_from_source`（dali/python/nvidia/dali/_utils/external_source_impl.py:284）——非 isinstance，而是 `iter(source)` 试探 + `TypeError "not iterable"` 落 callable（:329），None 沿用构造期 callback（:352）。math.py 是薄封装：30+ 函数共享 `_arithm_op`（dali/python/nvidia/dali/math.py:21）。外围：auto_aug/（dali/python/nvidia/dali/auto_aug/auto_augment.py:37）是纯策略层只组合既有 fn 算子；`_PipelineDebug`（dali/python/nvidia/dali/_debug_mode.py:745）继承 Pipeline 做 eager 无图执行；`ProcPool`（dali/python/nvidia/dali/_multiproc/pool.py:329）以共享内存支撑并行 external_source（py_num_workers>1）。

## 三、外部连接

向下经 pybind：`PYBIND11_MODULE(backend_impl, ...)`（dali/python/backend_impl.cc:3085），Expose* 按模块分区注册（ExposePipeline :2479）。勘误钉版：GPU 版函数名 `ExposeTesorListGPU` 是单 s 的 "Tesor" 拼写遗留（dali/python/backend_impl.cc:1879，调用点 :2148），属编译单元内部符号不进 ABI 故从未修。

插件围绕 base_iterator：`LastBatchPolicy`（dali/python/nvidia/dali/plugin/base_iterator.py:37，语义表 :121-136）与基类 `_DaliBaseIterator`（:55）；pytorch/paddle/jax 的 `DALIGenericIterator` 均派生自它（dali/python/nvidia/dali/plugin/pytorch/__init__.py:43 等）；tf 例外——`DALIIterator()` 返回 TF dataset op 包装 `DALIIteratorWrapper`（dali/python/nvidia/dali/plugin/tf.py:307），不继承基类。甄别两点：①pytorch 的 `DataLoader` 不在顶层包而在 proxy 服务器模式（dali/python/nvidia/dali/plugin/pytorch/experimental/proxy/__init__.py:781，继承 torchdata DataLoader）；②numba 插件并非仅 .pyi 存根——顶层 `__init__.py` 是 601 行真实现，仅 `fn/` 子模块配 .pyi。triton.py 的 `autoserialize`（dali/python/nvidia/dali/plugin/triton.py:16）服务 Triton ENSEMBLE。

动态模式的实验后端其实在 operators/ 树：`ResizeOpImplCvCuda`（dali/operators/image/resize/experimental/resize_op_impl_cvcuda.h:32）把 resize 委托 CV-CUDA，MiniBatch 循环经 `PushFramesToBatch`（:184）喂数；亮点是按 batch_size 分桶的批缓存 `std::unordered_map<int, BatchCache> batch_cache_`（:298），复用 `nvcv::TensorBatch` 免反复分配。桥接层 `NVCVOperator`（dali/operators/nvcvop/nvcvop.h:193）。

## 四、数据流

定义期：`@pipeline_def` →（可选）AutoGraph 转换 → `_generate_graph` 执行函数体 → DataNode 链 → `set_outputs`。运行期：迭代器驱动 `pipe.run()`，epoch 终点由 reader_name/size 决定（base_iterator.py:74）；输出经 `feed_ndarray`（torch_utils.py:34）按 cuda_stream 异步拷入各框架。

## 五、设计决策与取舍

导入期 `_load_ops` 一次付清算子类生成代价，换 `ops.decoders.image` 直接可点的体验，代价是 import 时间与需显式 Reload。external_source 的 try/except 试探换兼容任意 iterable/generator function，代价是错误判定依赖 "not iterable" 字符串匹配（external_source_impl.py:333）。pipeline.py 单文件 2500 行是循环依赖压力下的聚合——拆文件需 import 手术。

## 六、新人提示

找算子优先看 `fn`（官方 API，含 per-call 设备推断）。LastBatchPolicy 语义看 base_iterator.py:121-136 表格——FILL 且未 padded 时会重复补齐样本，训练/评估须区分。external_source 三态（callable/iterable/generator func）与 cycle 合法组合在 external_source_impl.py:284-358 说清；调试图执行用 `_PipelineDebug`。

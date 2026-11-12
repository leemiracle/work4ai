# 09 · lib/CAPI/ + python/ —— 从 C 边界到 nanobind：三层 Python 绑定链

## ① 角色定位

这套代码让 Python 前端能驱动 C++ 编译器内核，路径是经典 MLIR 三层链：**C++ 实现 → C API（稳定 ABI 边界）→ nanobind 扩展（`_cuda_tile`）→ Python 门面（cuda_tile_ops.py）**。`lib/CAPI/` 三文件：Registration.cpp（注册）、Dialect/CudaTileDialect.cpp（746 行，类型+属性工厂）、Dialect/CudaTileOptimizer.cpp（88 行，优化入口）。`python/` 三角色：SiteInitializer.cpp（site 初始化钩子）、Dialect/DialectCudaTile.cpp（741 行手写 nanobind 绑定）、cuda_tile/dialects/cuda_tile_ops.py（5375 行，生成+手写混合体）。绑定面规模实测：三个 `cuda_tile-c` 头合计 **101 个 `MLIR_CAPI_EXPORTED` 导出**（CudaTileDialect.h 97 + Optimizer.h 2 + Registration.h 2）；nanobind 侧 **18 个类注册**（6 type subclass + 11 attribute subclass + 1 nb::class_）+ 5 个模块级函数。

## ② 内部结构

**CudaTileDialect.cpp** 按"每个类型/属性一个 section"平铺：六个 view 类型各占一段（PointerType :46 / TileType :67 / TokenType :105 / TensorViewType :121 / PartitionViewType :172 / StridedViewType :242），节奏统一——IsA 谓词、GetTypeID、Get 工厂、逐字段 getter、GetChecked 带验证版本（模板 `getCheckedType`，:36-40）。属性区十一个枚举属性（RoundingMode :324、MemoryScope :439、AtomicRMWMode :485、Signedness :531 等）全走 `symbolize*/stringify*` 字符串往返。两个复合工厂：`OptimizationHintsAttrGetEntryOpHint`（:587-623）手工拼双层 DictionaryAttr（外层 arch 键、内层 hint 键），`numCta==0` 视为未指定跳过（:597）；`GetLoadStoreOpHint`（:625-654）用 `allowTma==-1` 作哨兵（:635）。`mlirCudaTileWriteBytecodeToBuffer`（:668-692）malloc 缓冲交调用方，配 `mlirCudaTileFreeBuffer`（:694-697）——显式所有权协议。**CudaTileOptimizer.cpp** 极薄：Init 置默认值（:24-36）、`toCpp` 翻译配置（:40-47）、`ApplyOptimizations`（:50-88）调内核并临时挂诊断回调（:68-76）。

**DialectCudaTile.cpp** 是 `NB_MODULE(_cuda_tile, m)`（:23）单模块。5 个模块级函数：`register_dialect`/`register_passes`（:27-38）、`applyTileIROptimizations`（:53-66，配规避 EMBED_CAPI 符号问题的 `TileIROptimizationsOptsWrapper` :42-50）、`addLoopSplitThresholdAttr`（:68-82，打 discardable 属性设循环分裂阈值）、`writeBytecode`（:84-111，CAPI bytes→file.write→free）。类型绑定六个 subclass：TileType.get 走 GetChecked 并把 null 译成 `None`（:149-153）；TensorViewType 的形状/步长用 `Optional[int]`，`None` 编码成 kDynamic、负值当场抛 invalid_argument（:200-214）；Partition/StridedView 的 `dim_map` 缺省自动生成恒等映射（:281-286）。属性绑定十一个：RoundingModeAttr 与 MemoryOrderingSemanticsAttr 对非法值**回退默认**（nearest_even :474-479 / weak :539-543），MemoryScope/PaddingValue/AtomicRMWMode 等则**直接抛异常**（:565-568）——两种失败哲学并存。

**cuda_tile_ops.py** 是混合体：前半手写——16 个标量元素类型包装类（Boolean :47 到 Float4E2M1FN :107）、11 个 Enum（:198 起）、`get_*_attr` 工厂族（:320-462）、MMAConfig 预设表（:464-702）；后半是 ODS 生成基类上的薄特化：`_ConstantOp`（:1361）把 Python 值列表转 DenseElementsAttr，`_GlobalOp`（:1375）加 alignment/visibility kwargs，`ModuleOp`（:5245）附 body 属性。尾部是手写 `TileIrGenerator` Builder 门面（:5298 起，配 `EntryContext` 上下文管理器 :5265）与 PDL 原子操作包装。

## ③ 外部连接

构建侧（python/CMakeLists.txt）钉死链条：SiteInitializer 扩展 `MODULE_NAME _site_initialize_1` 且 `EMBED_CAPI_LINK_LIBS CudaTileCAPIRegistration`（:38-45）——下划线模块名触发 MLIR Python 自动 site 初始化协议（register_dialects 钩子，SiteInitializer.cpp:26-28）。方言绑定 `declare_mlir_dialect_python_bindings` 的 `TD_FILE dialects/CudaTileOps.td` 只是 `include Ops.td` 的薄壳（CudaTileOps.td:14），`DEPENDS` 钉住 IR/Ops.td 保证再生、`GEN_ENUM_BINDINGS_TD_FILE` 指向 Types.td（:48-67）。nanobind 扩展 `_cuda_tile` 以 `EMBED_CAPI_LINK_LIBS` 内嵌 CAPI（MLIRCAPIIR + CudaTileCAPIDialects + CudaTileCAPIOptimizer，:69-79），`add_mlir_python_common_capi_library`（:82 起）聚合成可重定位 CAPI 库。运行时 `_cuda_tile` 被三层 Python 消费：`cuda_tile_ops.py:14-18` 的 `from .._mlir_libs import _cuda_tile`；`_cuda_tile_ops_gen`（TD 生成的 op 基类）；`mlir._mlir` 核心（`MLIR_PYTHON_PACKAGE_PREFIX=cuda_tile._mlir.` 重定位，:23）。

## ④ 数据流

Python 用户构造 `tile<4xf32>` 的旅程：`TileType.get([4], f32)` → nanobind classmethod（DialectCudaTile.cpp:145-156）→ `mlirCudaTileTileTypeGetChecked`（CudaTileDialect.cpp:93-99）→ C++ uniquing 池 → wrap 成 MlirType → nanobind 重包成 Python 实例。优化链：`applyTileIROptimizations(module, opts)` → `mlirCudaTileApplyOptimizations`（DialectCudaTile.cpp:61-63）→ `optimizeTileIRModule`（CudaTileOptimizer.cpp:79-80）原地写回。bytecode 落盘链：`writeBytecode(f, module)` → CAPI malloc → `nb::bytes` 拷进 Python → f.write → `mlirCudaTileFreeBuffer`（DialectCudaTile.cpp:92-107）——每个 malloc 配对 free。

## ⑤ 设计决策

为什么不直接 nanobind 绑 C++ 而绕 C API？`EMBED_CAPI_LINK_LIBS` 机制要求符号从 C 边界导出以便多扩展共享单份 CAPI 库（"controlled exports"，python/CMakeLists.txt:76-78），且 DialectCudaTile.cpp:113-114 明言 "TODO: Implement CudaTile python bindings using tablegen. For now we implemented C-API wrappers manually"——手写是显式技术债。TileType.get 有意选 GetChecked 而非裸 get（非法 shape 返回 None 而非崩溃），PointerType.get 因"无 verifier"只能走裸 get（:124-127 注释）。失败哲学分裂（回退 vs 抛异常）的看点：RoundingMode/MOS 属"宽松默认合理"的高频路径，MemoryScope 等属"拼错即 bug"的低频路径。TensorViewType 负维度提前拒绝（:207-213）防的是 kDynamic 被当合法值穿透进 IR。

## ⑥ 新人提示

找绑定入口别在 .py 里 grep 类定义——先看 DialectCudaTile.cpp 的 NB_MODULE，再看 ops.py 的 `_ods_cext.register_operation(_Dialect, replace=True)` 装饰器（:1359/:1373/:5243），`replace=True` 意味手写类整体顶替生成类。调"属性没生效"优先怀疑字符串拼写：枚举属性全走 symbolize 往返，非法字符串在 RoundingMode 会静默变 nearest_even 而非报错。给 CAPI 加函数的三步契约：头文件 `MLIR_CAPI_EXPORTED` 声明、Dialect.cpp 实现、DialectCudaTile.cpp 绑定——漏第二步会在链接期报 undefined symbol。SiteInitializer 的 register_passes 不是自动钩子（SiteInitializer.cpp:25-27 注释明示需手动调），忘调会出现 textual pipeline 解析失败。源码勘误：任务书"python/dialects/"路径实际为 `python/Dialect/`（C++ 绑定）+`python/cuda_tile/dialects/`（Python 门面）；"104 函数/13 类"与源码实测（101 导出/18 类注册）有出入。

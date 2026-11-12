# 09 · operators 库：fusion DAG IR、EVT 与 rubin kernel

## 角色定位

`operators/`（图谱域 692 节点/183 文件）是 CUTLASS 4.x 的 Python-first 算子库：用户以 Python lambda/AST 描述 epilogue 融合，经 EVT（Epilogue Visitor Tree）DAG IR 编译为 CuTeDSL kernel。三条主线：`cutlass/operators/`（API 面+fusion 编译器+heuristics）、`cutlass/kernels/rubin/`（Rubin/SM107 代际 GEMM kernel 与 CLI）、`providers/cutedsl/`（代际 EVT 参考实现）。它是第 07/08 篇 CuTeDSL 运行时与 PyIR 线的最大消费者。

## 内部结构

**API 面**（operators/__init__.py）聚合：`Operator` 基类（base.py，__init__.py:53）、`Manifest`（manifest.py:48）、`CompiledArtifact`（artifact.py，__init__.py:52）、代际目标 `ArchPortability/TargetSm`（arch.py，__init__.py:35）与 heuristics 家族。kernel 侧 `kernels/rubin/gemm/dense_gemm_universal.py`（1323 行）是旗舰：`Sm107DenseGemmUniversal`（dense_gemm_universal.py:85，继承 SM107PersistentDenseGemmKernel）+ 三入口 `bmm`（L713）/`compile_bmm`（L763）/`run`（L864），命令行解析 `_parse_comma_separated_ints`（L1116）。

**fusion DAG IR**（fusion/ir/）是核心资产：
- node.py（330 行）：`TupleEmitter`（node.py:45）、实现基类 `ImplBase`（L70）、空实现 `NoOpImpl`（L159）、节点元数据 `NodeBase`（L174）、拓扑遍历 `TopoVisitorImpl`（L313）；
- compute_nodes.py：`ComputeImplBase`（compute_nodes.py:41）/`ComputeImpl`（L50）/`ComputeNode`（L68）；
- load_nodes.py（312 行）：`AccumulatorImpl`（load_nodes.py:57）、`LoadSrcImpl`（L67）、`AuxLoadImpl`（L95）、广播三兄弟 Row/Column/Scalar（L132/L175/L218）、`LoadNode`（L282）；
- store_nodes.py（276 行）：`StoreDImpl`（store_nodes.py:59）、`AuxStoreImpl`（L85）、规约基类 `ReductionImplBase`（L119）+三实现（L183/L198/L213）、`StoreNode`（L228）；
- dag_ir.py：`DAGIR`（dag_ir.py:46）骑 networkx 图，`add_node`（L70）/`add_edge`（L78）/可达集（L166）。

**passes 流水线**（fusion/passes/）：`EVTPassBase`（pass_manager.py:45）与 `EVTPassManager(nx.DiGraph)`（pass_manager.py:118）驱动十个 pass（dag_2_tree、layout_elimination、shape_type_propagation、smem_size_calculator 等，一文件一 pass）。

**pycute 内嵌副本**（fusion/pycute/）：`LayoutBase`（layout.py:41）、`Layout`（L49）、`coalesce`（L135）、`composition`（L196）、`complement`（L246）、逆布局 `right_inverse`（L274）、`logical_divide`（L311）、`Swizzle`（swizzle.py:60）、`ComposedLayout`（swizzle.py:93）。**甄别**：与 `python/pycute/` 独立包同源分叉——layout.py 409 vs 367 行、2 vs 4 空格缩进，同构但副本略多函数；并存是 vendored 去 PyPI 依赖而非疏忽。

**providers/cutedsl/evt/** 摆着 12 个代际参考实现（sm80_tensorop_gemm、sm90_static_persistent、sm100_persistent、sm107_dense_gemm、sm100_mixed_input、EFC 子目录与 converter.py）；gemm/ 下即第 08 篇的 scheduler.py。前端 `fusion/frontend/python_ast.py` 吃 Python AST，后端 sm80/sm90/sm100 三代 emitter+`*_nodes.py` 对齐硬件代差。

## 外部连接

向下依赖 CuTeDSL 执行栈（`cute.jit`+JitExecutor，第 07 篇）与 PyIR 的 _mlir 注入（scheduler.py:31，第 08 篇）；向上以 `EpilogueFunctorVisitor`（fusion/epilogue.py:41）与 C++ 侧 EVT（include/cutlass/epilogue/fusion/ 的 visitor 体系，组 1 第 04 篇）共享树形 epilogue 概念——Python 侧是同概念新实现；heuristics/nvmatmul/（ranker.py/_mapping.py）运行时调 nvidia-matmul 服务选优配置；metadata/design/（sm100.py/sm107.py/tile_scheduler.py）把代际约束做成可编程元数据。

## 数据流

用户 epilogue lambda → python_ast.py 前端解 AST → 构 `DAGIR`（load/compute/store 节点挂 ImplBase 实现）→ `EVTPassManager` 跑十个 pass（DAG 转树、布局消除、形状/类型传播、smem 尺寸计算）→ 按代际选 emitter 生成 CuTeDSL 调用序列 → 与 rubin kernel（Sm107DenseGemmUniversal）合成 → CuTeDSL JIT 出 cubin → `run/bmm` 入口执行；CompiledArtifact 缓存产物供 `compile_bmm` 复用。

## 设计决策

1. **Impl/Node 双轨**：NodeBase 只存 DAG 元数据，算法全放 ImplBase 子类——visitor（TopoVisitorImpl node.py:313）与 pass 可只看元数据层。
2. **DAGIR 骑在 networkx 上**（pass_manager.py:118 继承 nx.DiGraph）：免费获得图算法，代价是 networkx 依赖。
3. **三代 emitter 平铺**（sm80/sm90/sm100 平级目录）：代际差异大（TMA/UMMA 语义），不做超类抽象反而直白。
4. **vendored pycute**：发布件不拖 PyPI 依赖，双副本漂移（409 vs 367 行）是可接受代价。

## 新人提示

- 入门：rubin `run`（dense_gemm_universal.py:864）跑通一次 → 读 dag_ir.py 258 行 → 对照 sm100_nodes.py 看一个 epilogue 算子完整降级。
- 改 epilogue 语义先查 store_nodes.py 规约三件套（L183/L198/L213）——列/行/标量规约最常被重复发明。
- 两个 pycute 别混用：operators fusion 只 import 内嵌副本；独立包 python/pycute 服务教学示例。
- rubin 是代际代号（SM107），其 dense/blockscaled kernel 与第 11 篇 generator 的 SM107 生成面互补。

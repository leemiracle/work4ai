# 08 Matrix 与算子层（matrix.h / operators/）

## 角色定位

`include/matrix.h`（1361 行）是 AMGX 一切数值计算的矩阵载体，也是全库最大类所在地；`include/operators/` 则把它抽象成可与任意包装算子平起平坐的 Operator 根。两文件合谋构成"数据体+算术契约"的分层：求解器面向 Operator 编程（`solvers/solver.h:216` m_A 即 Operator 指针），Matrix 是其最重的实现。图谱里 MatrixBase 节点（`matrix.h:65-987`）标注为"全库最大类"，matrix.cu 另有 1238 行离线模板实现。

## 内部结构

三段式单文件：第一段 MatrixBase（`matrix.h:65` `class MatrixBase : public AuxData, public Operator<T_Config>`——双继承同时拿到属性挂载与算子契约）；第二段 host 显式特化（`matrix.h:989-991` `Matrix<TemplateConfig<AMGX_host,...>> : public MatrixBase<...>`）；第三段 device 特化（apply 实现在 `matrix.h:1192`，host 版在 `matrix.h:1030`）。数据布局是 CSR/BSR 五元组：block_dimy/dimx/block_size（`matrix.h:74-77`）、props 标志、num_rows/num_cols/num_nz（`matrix.h:79`）；块尺寸静态参数化贯穿全库模板。device 侧持有 cuSPARSE 资源：cuMatDescr 创建/销毁（`matrix.h:194/221`）、描述符拷贝工具（`matrix.h:242-247`），头部直接 include amgx_cusparse（`matrix.h:36`）。matrix.cu 四大件：resize（`matrix.cu:698`，45 行）、setupMatrix（`matrix.cu:744`，68 行）、reorderColumnsByColor（`matrix.cu:840`，101 行——着色列重排的核心落地）、sortByRowAndColumn（`matrix.cu:942`，42 行）。

## 外部连接

Operator 根在 `operators/operator.h:14`：apply 纯虚（`operator.h:34`，注释 L30-33 明言"latency hiding 必须由具体算子内部处理，不能外传"）、getManager 纯虚（`operator.h:44`）、维度/视图接口族（`operator.h:46-57`）——视图协议（ViewType/OWNED/INTERIOR/EXTERIOR）是分布式与单卡统一的关键。派生算子四件：SolveOperator 把任意 Solver 包装成算子（`solve_operator.h:15`，apply 即求解，使 AMG 预条件子可嵌套——`solver_operator.h` 是其 compose 变体）；ShiftedOperator 算 (A-σI)v（`shifted_operator.h:13`）；DeflatedMultiplyOperator 投影掉已知特征子空间（`deflated_multiply_operator.h:14`）；PageRankOperator 转移矩阵+阻尼（`pagerank_operator.h:13`）。向 cusp 的桥是 MatrixCusp 适配器（`matrix_cusp.h:20`，持 `Matrix<TConfig>* pM` 指针做零拷贝视图，全文件仅 121 行）。数值内核主力 `generic_spmv_csr.h`（326 行）：`csr_generic_spmv_vector_kernel` 以 VECTORS_PER_BLOCK/THREADS_PER_VECTOR 模板参数+`__launch_bounds__`（`generic_spmv_csr.h:19-24`）实例化出大量变体。

## 数据流

上传路径：setValuesFromHost 系列（MatrixBase 成员）→ resize 定容（matrix.cu:698）→ setupMatrix 装配（matrix.cu:744，含 diag 提取与 allow_recompute_diag 决策）。多色求解器触发时：求解器 isColoringNeeded → Matrix 调 coloring → reorderColumnsByColor（matrix.cu:840）把同色列打包，使多色 GS 的按色批量 kernel 免分支访存。solve 期每次 apply（matrix.h:1030/1192）按 currentView（operator.h:54-56 视图族）决定算 OWNED 还是含 halo 的完整区间；分布式场景 getManager（`matrix.h:967`）把 halo 交换委托给 DistributedManager。

## 设计决策

其一，Matrix 同时继承 AuxData+Operator 而非持有算子，避免 setup 期类型切换；其二，host/device 用显式特化而非运行时分派——编译期双实例换运行时零开销，代价是模板爆炸（matrix.cu 全是离线模板定义）；其三，reorderColumnsByColor 放 Matrix 层而非求解器层，一次重排供全部按色列读的 kernel 复用；其四，cuSPARSE 描述符内嵌（matrix.h:194-247）让 device 矩阵可直接喂 cuSPARSE 对照路径（测试 `src/tests/smoother_cusparse.cu` 即验证此等价）。

## 新人提示

改矩阵结构先看 `matrix.h:120-135` 的防御：is_initialized 后 set blockDim/num_nz 直接 FatalError——结构不可变期由 setup 前后划界。读 device kernel 从 generic_spmv_csr.h 入手最短；追踪"为什么我的求解器没着色"沿 isColoringNeeded→getColoringScope（solver.h:146）→matrix_coloring_scheme 配置链查。MatrixCusp 是访问内嵌 cusp gallery/precond 的唯一正门，别手搬五元组。

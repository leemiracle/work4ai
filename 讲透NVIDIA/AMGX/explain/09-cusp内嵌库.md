# 09 cusp 内嵌库（include/cusp/，vendored v0.3.0）

## 角色定位

AMGX 把 NVIDIA 的稀疏线性代数库 cusp 整棵内嵌在 `include/cusp/`（血统见 `cusp/version.h:20` CUSP_VERSION=300，按 `version.h:16-23` 的编码公式即 v0.3.0；README/CHANGELOG 记录 CUDA 4.x 时代的 vendored 来源）。它在 AMGX 中扮演三重角色：单卡参考算法库（krylov/precond/relaxation）、格式工具与 IO 层（容器/转换/MatrixMarket）、以及 GPU kernel 写法范本（thrust functor 组合）。图谱 cusp 域 267 节点：148 个 file 节点分两面粉——用户面 45 个（容器/算法公共 API）、detail 实现面 103 个；另有 30 class、87 function（函数节点全落在 detail 参考实现里）。

## 内部结构

容器层五种稀疏格式共同派生 `detail/matrix_base.h:15` 的基类：COO 三数组（`coo_matrix.h:71`）、CSR（`csr_matrix.h:77`，AMGX 主格式的 cusp 侧对应物）、DIA 对角线存储（`dia_matrix.h:91`）、ELL 定宽打包（`ell_matrix.h:88`，行长均匀时 GPU 高吞吐）、HYB=ELL+COO 混合（`hyb_matrix.h:114`）；每种配只读视图（如 `ell_matrix.h:224`）。稠密侧 array1d（`array1d.h:44`，直接继承 amgx::thrust 的 vector_base）与 array2d（`array2d.h:182`）。格式体系用空 struct tag 树（format.h）做编译期分派，`linear_operator.h:22` 的线性算子基类持有维度让迭代法泛型接受矩阵/预条件子（`linear_operator.h:37` identity_operator 占位）。算法层：krylov 家族 cg/bicg/bicgstab/bicgstab_m（732 行实现是 krylov 线最大）/gmres（Arnoldi+Givens）/arnoldi；收敛监控 default_monitor（`monitor.h:85`）与收敛率增强版 convergence_monitor（`monitor.h:249`）。预条件家族：smoothed_aggregation 单卡 SA-AMG 参考实现（`precond/smoothed_aggregation.h:62`，428 行装配）、ainv 近似逆（`precond/ainv.h:21`）、diagonal（`precond/diagonal.h:66`）；松弛器 jacobi（`relaxation/jacobi.h:21`）与 polynomial（`relaxation/polynomial.h:21`）；稠密直接法 LU 包装成 linear_operator（`detail/lu.h:105`）。

## 外部连接

与 AMGX 本体的桥有三座：`cusp/memory.h:34-37` 的 CuspMemMap 把 cusp host/device 内存 tag 映射到 AMGX_host/AMGX_device；`matrix_cusp.h:20` 的 MatrixCusp 零拷贝视图让 AMGX Matrix 直接进 cusp 算法；FGMRES 反向借用——Hessenberg 就存在 `cusp::array2d`（`solvers/fgmres_solver.h:103`）。`detail/spectral_radius.h:39` estimate_spectral_radius 幂迭代与 `:69` ritz_spectral_radius 是 AMGX 平滑器自动估谱的数学来源。gallery 提供 Poisson（2D/3D Laplacian）/diffusion/stencil/random 测试矩阵，`io/matrix_market.h` 是 AMGX 测试矩阵标准 IO。`graph/detail/maximal_independent_set.inl` 的 Luby 风格 MIS 是 AMGX PMIS 系选择器的算法原型。

## 数据流

用户面 API（multiply/convert/transpose/print）全部是薄声明，落地走 `detail/dispatch/multiply.h` 等分发层——按两算子内存空间组合编译期路由到 host 或 device 实现，无运行时开销；host 乘法在 MKL 可用时转发稀疏 BLAS（`detail/host/spmv_mkl.h`）。host 参考实现族（`detail/host/reference/csr.h` 1189 行最大，含 csr_tobsr/matmat_pass1/2 等 27 函数）源自 scipy sparsetools（`detail/host/update.sh` 从 scipy SVN 拉取保持同源），专供 GPU 结果验证——AMGX 的 csr_multiply 测试即以它为真值参照。device 侧 kernel 以 thrust functor 组合表达（`detail/device/conversion.h` 十余 functor 拼装格式互转）。

## 设计决策

内嵌而非外链：cusp 已停维（CUDA 4.x 时代），AMGX 需要无依赖交付且要改 amgx::thrust 命名空间适配新 CUDA（commit 91a8413 "Fix CUDA 13 tuple compatibility" 正是此类修补）；dispatch 编译期路由把 host/device 选择压进模板，代价是 2×2 组合实例化膨胀；参考实现留 scipy 血统换来 GPU kernel 的可信对照——这是 GPU 数值库的"参考实现=规格"范式。

## 新人提示

读 cusp 按"用户面→dispatch→实现"三层走最快，别一头扎进 detail。找 AMGX 某行为的单机真值参照优先查 `detail/host/reference/`（csr.h/coo.h/csc.h/bsr.h 四族齐全，CSC 与 CSR 互为镜像）。注意 `cusp::thrust` 与 std thrust 的命名空间差异——AMGX 补丁层专门隔离了它。version.h 的版本编码公式（L16-23）是判断内嵌版本快照的唯一可靠依据，README 的"CUDA 4.x"仅是历史语境。

# AMGX Onboarding：GPU 加速代数多重网格求解器库全景导览

> 知识基座：understand 图谱 1233 节点 / 3136 边 / 15 层 / 16 步 tour / 0 issues / fingerprints 661 文件 @ commit 91a8413e（v2.5.0）。
> 本文全部行号锚均从源码核实（2026-11-06）。

---

## 1. 项目定位：AmgX 是什么

AmgX（Algebraic Multigrid Solver）是 NVIDIA 开源的 **GPU 加速核心线性求解器库**，用于加速仿真计算中最耗时的线性方程组求解部分（README.md:3-6）。它解决的问题是：工业级仿真（油藏、结构力学、CFD 的隐式非结构方法）中 Ax=b 的规模动辄千万到十亿未知量，直接法不可用，单靠 Krylov 迭代又收敛慢——**代数多重网格（AMG）是这类稀疏系统的最优预条件器族，而 AmgX 把整套 AMG 层级构建与循环求解搬到了 GPU 上**，通过纯 C API 对外暴露，把单卡到多卡（用户自带 MPI）的并行细节全部抽象掉。

**三种 AMG 变体**是理解本库的第一把钥匙（对应图谱 L02/L03/L04 三层）：

| 变体 | 层级类（源码锚） | 思路 | 典型场景 |
|---|---|---|---|
| classical（经典/Ruge-Stüben） | `include/classical/classical_amg_level.h:32` `Classical_AMG_Level_Base` | 逐点分裂 C/F（粗点/细点），插值延长的传统两阶段 | 标量椭圆算子，油藏模拟主力 |
| aggregation（聚合） | `include/aggregation/aggregation_amg_level.h:35` `Aggregation_AMG_Level_Base` | 把强连接的点聚合成粗点，Galerkin 乘积 A_c=R·A·P | GPU 上最常用路线，块系统 |
| energymin（能量最小化） | `include/energymin/energymin_amg_level.h:31` `Energymin_AMG_Level_Base` | 插值系数由能量泛函最小化确定 | 需要 smoothed 聚合质量的场合 |

值得注意的是 README.md:21 的特性清单只写了 "Classical (Ruge-Steuben) and Unsmoothed Aggregation"——**energymin 变体在代码里完整存在（含专属 selector/interpolator）但未进 README 特性行**，这是文档滞后于代码的一处小差量，读代码时不要被 README 误导以为只有两种。

第二把钥匙是**求解器组合系统**：AMG 本身在框架里只是 `Solver` 体系中的一个预条件器（`include/solvers/algebraic_multigrid_solver.h` 把整套 AMG 包装成 Solver），外层再套 PCG/FGMRES/GMRES/BiCGSTAB 等 Krylov 迭代，逐层又用 Jacobi/多色 Gauss-Seidel/ILU/DILU/多项式做平滑——用户用一份 JSON 就能声明任意嵌套的求解器树（"flexible solver composition system"，README.md:4）。

对外形态上，AmgX 的唯一契约面是 **C API**：`include/amgx_c.h` 以 `AMGX_API` 导出 81 个函数（`grep -c AMGX_API` 实证），覆盖 initialize → matrix_upload → solver_setup → solve → finalize 全流程；`include/amgxP_c.h`（16 个导出）面向插件、`include/amgx_eig_c.h`（5 个导出）面向特征值求解。Fortran/Python 等绑定全部经这层 C 接口。版本锚：`ReleaseVersion.txt` = 2.5.0，API 版本三元组在 `include/version.h:12`（`__AMGX_API_VERSION_MAJOR`）与 `src/api_version.cu`。

一句话定位：**AmgX = 三种 AMG 变体 × 20+ 种求解器/平滑器 × 多卡 MPI 分布式 × 一份 JSON 配置，全部塞进 81 个导出函数的 C 门面后面**。图工程视角的"密度"感：661 个被分析文件中 include/ 占绝对大头——这是一个**头文件模板库为主、.cu 只做离线模板实例化（ETI）**的 CUDA C++ 工程（后文第 3 节展开此模式）。

---

## 2. 架构总览：15 层全景地图

图谱把 661 个文件组织成 15 层。从上往下读就是"从门面到地基"：

| 层 | 名称 | 文件数 | 职责与关键锚 |
|---|---|---|---|
| L01 | 核心 AMG 架构 | 8 | 顶层骨架：`src/amg.cu`（1564 行总装线，AMG_Setup functor @ amg.cu:147）、`src/amg_solver.cu`（AMG_Solver 主入口 setup/solve @ :188/:274）、`src/amg_config.cu`（1545 行配置解析中枢）、`include/amg_level.h:51`（层级抽象基类） |
| L02 | classical 经典 AMG | 36 | `Classical_AMG_Level_Base` 组织 strength→selector→interpolator 三段式；strength 三度量（affinity/ahat/all @ include/classical/strength/）、PMIS/HMIS 粗点选择（pmis.h:23）、distance1/distance2/multipass 插值（interpolators/） |
| L03 | aggregation 聚合 AMG | 33 | `Aggregation_AMG_Level_Base` + 聚合 selector（size2/size4/size8/parallel_greedy/multi_pairwise/adaptive/geo 等 12 文件 @ include/aggregation/selectors/）+ 粗算子生成器四实现（serial/thrust/hybrid/low_deg @ include/aggregation/coarseAgenerators/） |
| L04 | energymin 与缩放收敛 | 27 | 第三种 AMG 变体（em_interpolator.h:20 与 classical 的 Interpolator 同名不同命名空间）+ scalers 矩阵预归一化（include/scalers/ 四文件）+ convergence 收敛判据工厂（convergence.h:104 ConvergenceFactory，五种判据实现） |
| L05 | 求解器家族 | 55 | `include/solvers/solver.h:22` Solver 基类（310 行）+ 27 个求解器头：krylov（cg/pcg/pcgf/gmres/fgmres/bicgstab/pbicgstab/idr/idrmsync）、松弛（jacobi/block_jacobi/cf_jacobi/gauss_seidel/kaczmarz 及 multicolor 族）、多项式（cheb/chebyshev_poly/polynomial/kpz_polynomial）、直接法 dense_lu |
| L06 | 循环与调度 | 16 | `include/cycles/fixed_cycle.h:20` FixedCycle 基座（Dispatcher 策略化）+ V/W/F/CG/CG_Flex 五循环（各自 Factory）+ convergence_analysis |
| L07 | Matrix 与算子 | 39 | `include/matrix.h:65` MatrixBase（1361 行三段式）+ `include/operators/operator.h:34` 纯虚 apply + 五复合算子 + multiply/csr_multiply/generic_spmv_csr SpMV 族 + IO/permute/transpose/truncate |
| L08 | 分布式通信 | 25 | `include/distributed/distributed_manager.h:194` DistributedManagerBase（2111 行，全库最大单类）+ CommsMPI 族 + comms_visitors.h:144/180/212 三 Visitor + ETI 清单四件 |
| L09 | 着色与特征值 | 49 | `include/matrix_coloring/matrix_coloring.h:130` 着色工厂（11 策略，src/matrix_coloring/ 12 个 .cu 实证）+ `include/eigensolvers/eigensolver.h:25` EigenSolver 基座（184 行）+ arnoldi/lanczos/lobpcg/jacobi_davidson/subspace_iteration |
| L10 | cusp 内嵌库·容器与方法 | 63 | `include/cusp/` 用户面：array1d/array2d 容器、coo/csr/dia/ell/hyb 五种稀疏格式（format.h:16-26 空 struct 继承树 tag）、krylov/precond/relaxation/gallery 参考实现 |
| L11 | cusp 内嵌库·detail | 87 | cusp 实现面：detail/host 21 + device 31 + dispatch 4（`include/cusp/detail/dispatch/multiply.h:14` 编译期空间路由）+ spmv_mkl（extern "C" 声明 MKL 稀疏 BLAS） |
| L12 | 基础设施 | 67 | `include/basic_types.h:113` TemplateConfig（全库类型之根）+ `include/vector.h:143/:405` Vector 双特化 + error.h/determinism_checker/amgx_timer 诊断线 + Resources（resources.h:21）+ sm_utils.inl（598 行 SM 加载策略） |
| L13 | C API 门面 | 10 | `include/amgx_c.h`（611 行，81 导出）+ `src/amgx_c.cu`（5358 行，库对外最大实现文件）+ amgxP_c/amgx_eig_c + amgx_c_wrappers.inl（C++ 模板包装） |
| L14 | 预设配置与构建文档 | 79 | `src/configs/` 62 份 JSON 预设 + 8 份 eigen_configs + CMakeLists 双层 + 版本三件套（version.h/ReleaseVersion.txt/CHANGELOG） |
| L15 | 测试框架 | 67 | `src/tests/` 60 个 .cu 专题测试 + `include/unit_test.h:45` UnitTest 基类（:118 纯虚 run）+ test_utils.h（821 行）+ testframework |

**三条贯穿性的纵向线索**（比层更能解释代码为什么这样组织）：

1. **工厂注册表线**：几乎每个可配置的算法维度都有自己的 `Factory + registerFactory` 静态注册表——Solver（solver.h:271）、Cycle（cycle.h:77）、Convergence（convergence.h:104）、MatrixColoring（matrix_coloring.h:130）、EigenSolver（eigensolver.h:151）、Interpolator（classical/interpolators/interpolator.h:35）、聚合 Selector（agg_selector.h:42）、CoarseAGenerator（coarse_A_generator.h:39）、Strength（classical/strength/strength.h）。AMG_LevelFactory 甚至以枚举 `AlgorithmType` 而非字符串作键（src/amg_level.cu:156-163）。这是全库最大的模式一致性。
2. **host/device 双特化线**：`TemplateConfig<AMGX_host,...>` 与 `<AMGX_device,...>` 两个特化几乎出现在每个核心类上（Matrix matrix.h:989/:1151、Vector vector.h:143/:405、三种 AMG_Level、Solver），配合 `basic_types.h:134-137` 的 setMemSpace/setVecPrec 元函数做空间/精度变换。
3. **cusp 内嵌线**：AMGX 从 2013 年起把 cusp 稀疏线性代数库整个内嵌进 include/cusp/（L10+L11 共 150 文件，占全库 23%），容器与格式 tag 是 Matrix/Vector 的直接地基，`amgx::thrust` 命名空间兼容层（basic_types.h:15 + thrust_wrapper.h:39）统一屏蔽 thrust/CCCL 版本差异。

---

## 3. AMG_Setup 主流程：一次 setup 的总装线

### 3.1 入口链条：C API → AMG_Solver → AMG → AMG_Setup

一次典型求解的调用栈自外向内：

```
AMGX_solver_setup()                 include/amgx_c.h:382（C 门面）
  └─ AMGX_Solver C++ 包装           src/amgx_c.cu（5358 行）+ amgx_c_wrappers.inl 模板分发
      └─ AMG_Solver::setup          src/amg_solver.cu:188（接收 Matrix，驱动层级构建）
          └─ AMG<t_vec,t_mat,t_ind>::setup   src/amg.cu:1123（host 矩阵）/ :1152（device 矩阵）
              └─ AMG_Setup<...>::setup       src/amg.cu:147（functor 类，146-1563 行区间）
                  └─ 逐层生成 AMG_Level      include/amg_level.h:51
```

`src/amg.cu` 共 1564 行，是 Setup/Solve 的总装线。它的结构非常"反直觉"但极具代表性——**头文件里几乎不写实现、.cu 文件是"离线模板定义区"**：`AMG_Setup` 是一个纯静态 functor 类（amg.cu:147 `class AMG_Setup`），模板参数是三个精度枚举（`AMGX_VecPrecision/AMGX_MatPrecision/AMGX_IndPrecision`，amg.cu:145），内部再按 `TConfig_hd`（host 或 device 配置）分派。与之平行的 `AMG_Solve` functor 在 amg.cu:1086。文件尾部的显式实例化（ETI）清单给出真正编进库里的精度组合——**6 种**（amg.cu:1549-1558）：

- 实数三组合：`<vecDouble,matDouble,indInt>`、`<vecFloat,matFloat,indInt>`、`<vecDouble,matFloat,indInt>`（混合精度）
- 复数三组合：`<vecComplex,matComplex>`、`<vecDoubleComplex,matComplex>`、`<vecDoubleComplex,matDoubleComplex>`

这 6 个组合与 C API 侧 `AMGX_mode` 枚举一一对应，也是全库"精度正交性"的落点：`include/amg.h:48` 的 `class AMG` 以三精度枚举作模板参数（而非 T_Config），顶层按精度组合显式特化——新人找"某精度下 setup 到底跑什么代码"，从这份 ETI 清单反查最快。

### 3.2 配置系统：AMG_Config 的类型擦除（amg_config.cu 1545 行）

setup 的一切行为由 `AMG_Config` 驱动（`include/amg_config.h`，346 行）。核心设计是**类型擦除的 Parameter**：单个参数值用模板构造/get/set 特化存取，参数元信息由 ParameterDescription/ParameterMargins 描述，参数本体存进 map 树并支持作用域前缀（default/level 1/smoother 等嵌套作用域，这是"求解器树"配置的实现基础）。

`src/amg_config.cu` 的三个入口（统一消化一切配置来源）：

- `parseParameterString`（amg_config.cu:60）：`key=value;key=value` 字符串，C API 的 `AMGX_config_create` 走这里；
- `parseParameterStringAndFile`（:104）：字符串 + JSON 预设文件合并——**62 份官方预设 JSON（src/configs/）就是被这个函数吃进去的**；
- config_version 迁移（:76 与 :159-171）：显式校验 `config_version` 只能为 1 或 2，v1 语法在加载时迁移到 v2，报错信息直接打印违规 config 串。

全部默认参数在 `src/core.cu` 的 `registerParameter` 调用群注册——例如分布式通信器选择参数 `"communicator"` 注册于 core.cu:338，取值 `<MPI|MPI_DIRECT>`，默认 `"MPI"`（这个参数第 7 节还会回来，它是一处常见误解的源头）。

### 3.3 层级生成：AMG_Level 与三变体的统一骨架

`include/amg_level.h:51` 定义 `AMG_Level` 抽象基类：`compute_residual`/`dispose`/`swap` 等层级行为与 `solveAmmmx` 入口，并挂 `AsyncSolverSetupTask`（amg_level.h:25，派生 AsyncTask）支持粗层求解器的异步 setup。`AMG_LevelFactory`（amg_level.h:319，实现 src/amg_level.cu:156）按 AlgorithmType 枚举分发到三变体：

- **classical**（classical_amg_level.h:32）：`Classical_AMG_Level_Base` 派生自 AMG_Level，host/device 双特化（:117 起）。流程三段式——strength（连接强度，`include/classical/strength/strength.h:21` 基类 + affinity/ahat/all 三度量 + strength_base.h:23 Strength_BaseBase 公共底座）→ selector（C/F 分裂，PMIS 系列在 `include/classical/selectors/pmis.h:23` PMIS_SelectorBase）→ interpolator（插值=延长，`include/classical/interpolators/interpolator.h:18` Interpolator 基类/:35 Factory，distance1/distance2/multipass 三实现）。
- **aggregation**（aggregation_amg_level.h:35）：selector 决定哪些点聚成一个粗点——`include/aggregation/selectors/agg_selector.h:20` Selector 基类（:30 纯虚 `setAggregates`）/ :42 SelectorFactory；具体策略 12 个头文件，从朴素 size2/size4/size8（固定尺寸）到 parallel_greedy（GPU 并行贪心）、multi_pairwise、adaptive（自适应）、geo（几何）。聚合结果交给粗算子生成器消费：`include/aggregation/coarseAgenerators/coarse_A_generator.h:21` CoarseAGenerator 基类，四条实现路线 serial/thrust/hybrid/low_deg（同目录四个头文件）按规模与设备选择。
- **energymin**（energymin_amg_level.h:31）：`Energymin_AMG_Level_Base`，插值器在 `include/energymin/interpolators/em_interpolator.h:20`——**与 classical 的 Interpolator 类同名**（都叫 `Interpolator`，都有 ：35 附近的 InterpolatorFactory），靠命名空间与路径区分，读代码时必须看 include 路径别只看类名（图谱以 filePath 区分两节点，同源）。

殊途同归：三个变体都产出下一层粗网格算子（classical 用 P^T·A·P、aggregation 用 Galerkin 乘积 A_c=R·A·P、energymin 在最小化约束下组装），循环直到矩阵规模低于 `matrix_size coarse` 阈值后交给粗层直接求解器（dense_lu 或迭代法）。每层还各自持有 DistributedManager 的粗层副本，分布式状态随层级同步收缩。

---

## 4. 求解器体系：310 行基类 + 静态注册表工厂

### 4.1 Solver 基类与工厂（include/solvers/solver.h）

`include/solvers/solver.h` 全文 310 行，是 27 个求解器头的公共契约，三个要点：

1. **`class Solver : public AuxData`**（solver.h:22）——Solver 派生自 AuxData（可挂任意附件的键值容器），这使得任意 Solver 可被当作数据袋传递；Solver 本身又持有 setup/solve_pure_butt/solve 接口、性能计数、tau/monitor 钩子。
2. **SolverFactory 静态注册表**（solver.h:271）：`registerFactory(name, f)`/`unregisterFactory`/`allocate`（:295/:296），私有 `std::map<std::string, SolverFactory<TConfig>*>& getFactories()`（:307）持有全局 map。**新增求解器 = 写一个类 + 注册一个 Factory，无需改任何分发代码**——这是全库可扩展性的核心机制。
3. 每个 .cu 求解器文件的离线模板定义末尾有 ETI 块（同 amg.cu 模式），把 `Solver<TemplateMode<CASE>::Type>` 按全部支持的模式实例化。

`include/solvers/` 目录 28 个头文件（27 求解器 + solver.h 本身）按用途分四族：

### 4.2 Krylov 家族（外层迭代主力）

- **CG 族**：`cg_solver.h`（CG，对称正定）、`pcg_solver.h`（预条件 CG，最常用）、`pcgf_solver.h`（灵活预条件——预条件子在迭代间可变，比如预条件器本身是另一套迭代 AMG 时必须用它）；
- **GMRES 族**：`gmres_solver.h`（重启 GMRES，非对称系统）、`fgmres_solver.h:49`（`FGMRES_Solver`，灵活变体，预条件可变时更稳；:118 是它的 Factory）。AmgX 的 GMRES 重启参数与 Krylov 维度都走配置；
- **短递归族**：`bicgstab_solver.h`、`pbicgstab_solver.h`（预条件 BiCGSTAB）、`idr_solver.h`、`idrmsync_solver.h`（IDR 族，通信量更小的替代品，src/tests 里有专门的 IDR_Convergence_Poisson.cu 验证）。

### 4.3 松弛平滑族（AMG 每层的误差平滑器）

AMG 的收敛速度来自层级结构，逐层误差平滑靠这些"局部求解器"：

- **Jacobi 系**：jacobi、block_jacobi（`block_jacobi_solver.h:18` BlockJacobiSolver_Base，块矩阵走 block_common_solver.h 公共路径）、cf_jacobi（区分 C/F 点）、jacobi_l1（L1 缩放对角，改善对强不对称矩阵的稳健性）；
- **Gauss-Seidel 系**：gauss_seidel、fixcolor_gauss_seidel、以及**多色族 multicolor_gauss_seidel/multicolor_ilu/multicolor_dilu**——多色 GS/ILU 是 GPU 上真正能并行的 GS 变体（同色行互不依赖可同时算），它依赖 L09 的行着色子系统（第 8 节）；
- **kaczmarz**：行投影松弛，对某些奇异系统（如纯 Neumann 问题）有奇效；
- **多项式族**：cheb（Chebyshev 迭代）、chebyshev_poly、polynomial、kpz_polynomial——多项式平滑的特点是**零通信成本**（只做 SpMV 序列），多卡场景比 GS 族有优势。

### 4.4 桥接与直接法

`algebraic_multigrid_solver.h` 是关键的桥接件：**把整套 AMG 层级包装成 Solver 体系里的一个预条件器/求解器**——这就是"嵌套求解器树"的粘合点（FGMRES 的预条件器是一个 AMG，AMG 每层的 smoother 又是 multicolor_dilu，dilu 又依赖着色……全部经工厂字符串递归组装）。`dense_lu_solver.h` 在最粗层做稠密 LU 直接解；`user_solver.h`/`dummy_solver.h` 留出用户自定义与空实现占位。

**读代码提示**：solvers 目录下大量同名 .cu（src/solvers/）只是头文件声明类的离线模板定义；找算法本体逻辑一律从 include/solvers/*.h 的类定义入手，src/solvers/*.cu 只在需要看 kernel 展开时才进。smoother 的 device kernel 微观原语（共享内存加载/规约）集中在 `include/sm_utils.inl`（598 行）：`enum Ld_mode { LD_AUTO, LD_CA, LD_CG, LD_TEX, LD_NC }`（sm_utils.inl:116）+ `struct Ld<LD_*>` 特化族（:122/:129/:163/:196）——SM 在这里是 shared memory 与 smoother 的双关。

---

## 5. 循环与调度：FixedCycle 的 Dispatcher 策略化设计

### 5.1 为什么循环长这样：template-template 参数

多重网格循环的经典画像是"预平滑→限制（细到粗）→递归→延长（粗到细）→后平滑"，V/W/F/CG 四种循环只是递归次数与外层加速方式不同。AmgX 把这个共性抽成 **FixedCycle 基座 + Dispatcher 策略注入**：

```cpp
// include/cycles/fixed_cycle.h:19-20
template< class T_Config,
          template<AMGX_VecPrecision, AMGX_MatPrecision, AMGX_IndPrecision> class CycleDispatcher >
class FixedCycle: public Cycle<T_Config>
```

`CycleDispatcher` 是 **template-template 参数**：V/W/F/CG 各自提供一个 `*_CycleDispatcher` 类（如 `include/cycles/v_cycle.h:17` 的 `V_CycleDispatcher`、f_cycle.h:18、cg_cycle.h:17、cg_flex_cycle.h:17），FixedCycle::cycle（`src/cycles/fixed_cycle.cu:25`，278 行的实现主体）在递归点按策略分发——例如 fixed_cycle.cu:174 递归时显式构造 `V_CycleDispatcher<...>`（V 循环往粗层走永远还是 V），而 ：179 用外层传入的 `CycleDispatcher`（W 循环粗层保持 W）。**循环"形状"的差异被压缩成一行策略选择，主体代码零重复**，这是批甄别实证的策略化设计亮点。

循环家族与工厂（`include/cycles/cycle.h`）：

- `Cycle_Base`（cycle.h:22）与 Cycle 接口的 host/device 特化；
- `CycleFactory`（cycle.h:77）静态注册表（实现 src/cycles/cycle.cu:95 registerFactory），按配置字符串 `cycle=v|w|f|cg|cgflex` 实例化；
- 各循环 = `FixedCycle + 各自 Dispatcher + 各自 Factory`（cg_cycle.h:28 `CG_Cycle : public FixedCycle<T_Config, CG_CycleDispatcher>`，cg_flex_cycle.h:29、f_cycle.h:29 同构；w_cycle.h 同）；
- **CG 循环**（cg_cycle 与 cg_flex_cycle）把多重网格 V 循环当预条件器嵌进外层 CG 递归，是对聚合 AMG 收敛的再加速，也是配置 `convergence` 判据的消费现场。

`src/cycles/convergence_analysis.cu` + `include/cycles/convergence_analysis.h` 提供按层收敛因子分析（调参时判断"哪一层的 smoother 拖了后腿"）。

### 5.2 收敛判据工厂（L04 的 convergence 子组）

循环什么时候停由 `include/convergence/convergence.h` 的另一座工厂决定：`Convergence` 基类（convergence.h:64）+ `ConvergenceFactory`（:104，registerFactory @ :113）。四种判据实现各一文件：`absolute.h`（绝对残差阈值）、`relative_ini.h`（相对初始残差，最常用）、`relative_max.h`（相对历史最大残差）、`combined_rel_ini_abs.h`（混合判据）。**配置里 `convergence=RELATIVE_INI` 之类的字符串最终落到这座工厂**——注意它与 L05 求解器工厂、L06 循环工厂是三座独立的注册表，JSON 预设里分别出现在不同作用域（求解器作用域配 convergence，循环作用域配 cycle）。

### 5.3 缩放器（scalers）：setup 前的条件数预处理

同在 L04 的 `include/scalers/`：`binormalization.h`（双对角归一化）、`nbinormalization.h`、`diagonal_symmetric.h`、基类 `scaler.h`（src/scalers/ 四个 .cu 对应）。它们在 AMG setup 之前对矩阵做缩放变换，改善条件数与聚合质量——配置 `scaling=binormalization` 时启用，对不均匀对角的系统（油藏多相流典型）收益明显。

---

## 6. Matrix 与 cusp 内嵌库：数据面双核心

### 6.1 matrix.h 1361 行三段式

`include/matrix.h` 是全库数据面的枢纽，结构是清晰的三段：

1. **MatrixBase 通用体**（matrix.h:65）：`class MatrixBase : public AuxData, public Operator<T_Config>`——同时是附件容器与算子。它定义 CSR/BSR 数据布局（row_offsets/col_indices/values 三元组 + 块大小 blockdim 静态参数化，标量块=1、耦合块=n×n）、颜色/对角/属性（diag 剥离与否、matrix_format）生命周期、setValuesFromHost 一整套初始化接口。
2. **host 特化**（matrix.h:989）：`Matrix<TemplateConfig<AMGX_host,...>>`，补 host 侧操作；
3. **device 特化**（matrix.h:1151）：`Matrix<TemplateConfig<AMGX_device,...>>`，补 device kernel 钩子与分布式接口（halo 行、boundary 映射，与 L08 的 DistributedManager 握手）。

**Operator 根类**在 `include/operators/operator.h:14`，核心是纯虚 `virtual void apply(const Vector&, Vector&, ViewType) = 0`（operator.h:34）——全库"算子"概念的根，继承链 Operator→Matrix（matrix.h:65 实证）。operators/ 目录再派生五种复合算子：`solve_operator.h:15` SolveOperator、`solver_operator.h:14` SolverOperator（把 Solver 包装成算子——与 algebraic_multigrid_solver 的反向桥）、`shifted_operator.h:13` ShiftedOperator（A+σI，特征值求解用）、`deflated_multiply_operator.h:14` DeflatedMultiplyOperator（缩编/deflation）、`pagerank_operator.h:13` PagerankOperator（PageRank 场景）。**Matrix 能当算子、Solver 能当算子、平移/缩编的变体也是算子**——这是 Krylov 外层能随意组合预条件器的类型学基础。

### 6.2 SpMV 族与 Galerkin 乘积

- `include/multiply.h`（31 行）：gemm/multiply(A·B、A^T·B) 泛型声明入口；
- `include/csr_multiply.h:55` `CSR_Multiply_Impl`：device 特化（:114）直接继承 `Hash_Workspace`（:114，哈希法稀疏乘积工作区），:131 `m_use_cusparse_spgemm` 开关与 ：183 `cusparse_multiply` 后端——**CSR 乘 CSR 的核心算子，聚合 AMG 的 Galerkin 粗算子 A_c=R·A·P 就在这里落地**，后端在 cusparse/thrust/hash 之间选择；
- `include/generic_spmv_csr.h:19-23` `csr_generic_spmv_vector_kernel`：以模板参数（块大小/向量宽度）实例化出大量 kernel 变体，是 AMGX kernel 模板化的典型样本——同一个算法源码覆盖 blockdim=1 到 1×1/2×2/.../8×8 块矩阵与多种访存向量化宽度。

矩阵加工与 IO 工具围绕 Matrix 展开：permute、transpose、truncate（粗化后裁剪小值）、gaussian_elimination（matrix_analysis）、`include/matrix_io.h:28` MatrixIO 统一读写门面（按扩展名分派到 readers：MatrixMarket/bin/FlashBinary 等，实现 src/readers.cu）。

### 6.3 Vector：一个接口，两种 thrust 血统

`include/vector.h`（735 行）是 AMGX 最核心的数据容器：host 特化直接 `: public amgx::thrust::host_vector<...>`（vector.h:143），device 特化 `: public device_vector_alloc<...>`（vector.h:405）——**同一 Vector 接口、两种 thrust 基类**，统一了 copy/convert/mods 跨空间操作与分布式 halo 元数据。`PODVector`（vector.h:95）提供原始字节视图（二进制 IO 与 MPI 直传用）。配套的向量运算泛型在 `include/blas.h`（axpy/axpby/dot/nrm 模板族，65 入边枢纽）与 `include/norm.h`（norm_type 分派），复数类型层在 `include/amgx_types/util.h`（338 行，float/double/cuComplex/cuDoubleComplex 四特化的 get/abs/conj 统一操作）。

### 6.4 cusp 内嵌库（L10+L11，150 文件）

AmgX 把 cusp（NVIDIA 早年的 thrust 系稀疏线性代数库）**整库内嵌**在 include/cusp/，分两面：

- **用户面（L10）**：容器 array1d/array2d（`include/cusp/array1d.h:44` `class array1d : public amgx::thrust::detail::vector_base<T, default_memory_allocator<T,MemorySpace>>`，视图 :116）；五种稀疏格式 coo/csr/dia/ell/hyb 各一文件；**`include/cusp/format.h:16-26` 的格式 tag 体系**——known_format/unknown_format 根下 dense(array1d/array2d) 与 sparse(coo/csr/dia/ell/hyb) 全部是空 struct 继承树，供转换与打印函数按 tag 模板重载编译期选择；数值方法组 krylov（cg/bicg/bicgstab(_m)/gmres/arnoldi 的 .h+.inl 对）、precond（diagonal/ainv/smooth/smoothed_aggregation/strength）、relaxation（jacobi/polynomial）、gallery（poisson/diffusion/stencil/random 测试矩阵生成，src/tests 大量用）、graph（最大独立集）。
- **实现面（L11）**：detail/ 下 host 21 + device 31 + dispatch 4 + 顶层 31。三个值得记住的模式：`include/cusp/detail/blas.inl:331/:543` 按 `iterator_traits<...>::memory_space` 特化在 host/CUDA 路径间切换；`include/cusp/detail/dispatch/multiply.h:14` 的 `namespace dispatch` + 模板特化（:26 host 特化/:42 device 特化）做**编译期空间路由，零运行时开销**；`include/cusp/detail/host/convert.h` 以矩阵格式 tag 模板重载做 n×n 格式组合分发；`spmv_mkl.h` 经 extern "C" 声明 MKL 稀疏 BLAS 入口（host 后端可选）。device 侧转换算法全部以 functor + thrust::transform/scan/sort 组合表达（conversion.h），random.inl 用 functor+计数迭代器实现 device 端零存储随机序列。

**为什么值得内嵌**：Matrix/Vector 直接站在 cusp 容器与格式 tag 上，blended precision（vec/mat 精度解耦）依赖 cusp 的 allocator/tag 机制；且 cusp 上游已停止演进，内嵌让 AmgX 摆脱外部版本漂移（代价是 include/cusp/detail/config.h 的构建配置宏与 thrust_wrapper.h:39 的兼容层要随 CCCL 升级手工维护——`include/thrust_wrapper.h:80/:86` 包装 sort/sort_by_key 即为此）。

---

## 7. 分布式与 C API：多卡账本 + 81 导出的对外契约

### 7.1 DistributedManagerBase：全库最大单类（2111 行）

`include/distributed/distributed_manager.h` 的 `DistributedManagerBase`（:194 起，核心区约 194-1340，文件共 2111 行）是 AMGX 多卡运行时的**数据账本**：管理本 rank 窗口的行列全局索引映射、跨界邻接的 A/B/Halo 三类集合（halo 行、boundary 列、跨界管理协商表），以及 coarse 层的分布式收缩（1341-1343 friend 声明带出 host/device 两特化互访，distributed_manager.h 后段还有 host/device 两个派生特化 :2084/:2085 附近的 friend 群）。三种 AMG 变体的 Level 类都是它的 friend（:1338-1340：energymin/classical/aggregation 三 Base）——**层级构建时直接操作账本搬运跨界行**，而非走公共接口，这是性能代码常见的耦合选择。

### 7.2 CommsMPI 族与通信器选择（含一处重要勘误）

通信类层次：`include/distributed/comms_mpi.h:36` `CommsMPI : public DistributedComms`（基类在 `distributed_comms.h:26`，工厂 :340 DistributedCommsFactory）→ `CommsMPIHostBufferStream`（hostbuffer 中转）→ `include/distributed/comms_mpi_gpudirect.h:14` `CommsMPIDirect : public CommsMPIHostBufferStream`（CUDA-aware 直传）。

**勘误（读配置与排障时必防）**：通信器的选择是**配置参数显式指定，不是运行时自动探测**。链条实证：`src/core.cu:338` 注册参数 `"communicator"`，取值 `<MPI|MPI_DIRECT>`、默认 `"MPI"`；`src/distributed/distributed_manager.cu:2388` 读取该参数，:2392 `MPI_DIRECT` → `new CommsMPIDirect`（打印 "Using CUDA-Aware MPI (GPU Direct) communicator"），:2400 `MPI` → `new CommsMPIHostBufferStream`（"Using Normal MPI (Hostbuffer) communicator"），非法值走 else 分支。想让多卡跑 GPUDirect 必须两件事齐备：① MPI 库本身 CUDA-aware（编译期由用户保证，库内没有 MPI_Query_cuda_support 之类的探测调用）；② 配置里显式 `communicator=MPI_DIRECT`。图谱批甄别笔记里"运行时探测 CUDA-aware 能力决定启用"的表述不准确，以源码为准。

收发逻辑的解耦用**访问者模式**：`include/distributed/comms_visitors.h:144` ReceiverVisitor、:180 SenderVisitor、:212 SynchronizerVisitor（及 SynchSendVec/AsynchSendVec 等向量族 Visitor）把"对哪种数据做哪种收发"从 CommsMPI 剥离——**新增向量类型只需扩展 visitor，不改通信类**；comms_visitors1-4 四个 ETI 清单头（include/distributed/comms_visitors1_eti.h 到 4）是纯显式实例化清单。AmgX 自身的 MPI 初始化/查询包装在 `include/distributed/amgx_mpi.h`；矩阵分布策略（1D/2D 分块）在 `matrix_distribution.h` + `src/distributed/distributed_arranger.cu`（arranger 负责跨界行的重排与协商）。

### 7.3 C API：81 个导出与 5358 行实现

对外契约面 `include/amgx_c.h`（611 行）：

- **81 个 `AMGX_API` 函数**（grep 实证），SWIG/Windows dllexport 兼容的纯 C 接口；句柄一律 `void**` 风格不透明指针传出（AMGX_solver_handle 等在 amgx_c.h:119-120 定义为哑结构体指针）。
- 全流程锚点：`AMGX_initialize`（amgx_c.h:165）、`AMGX_solver_create`（:373）、`AMGX_solver_setup`（:382）、`AMGX_solver_solve`（:386）、`AMGX_matrix_upload_all`（:270）/`AMGX_matrix_upload_all_global`（:545，多卡全局矩阵带 partition 向量，:244-256 注释详细约定 partition_data 语义）/`_global_32`（:560）。
- **ABI 警告**（amgx_config.h:8-9 原文注释）："WARNING: Always use enums, do NOT use knowledge about the formulas for AMGX_Mode"——枚举数值布局是 ABI 的一部分但**语义上禁止按数值解释**，只能按标识符使用；跨语言绑定尤其要注意别把 AMGX_Mode 的位组合公式硬编码。
- `src/amgx_c.cu` 5358 行是库对外最大实现文件：C 入口经 `include/amgx_c_wrappers.inl` 的 C++ 模板包装按 mode 分派落地（大量 `*_impl` 模板，如 amgx_c.cu:3346 `AMGX_vector_upload_impl`），amgx_c_common.cu/amgx_c_common.h 承载共享工具。**.inl 文件是 tree-sitter 类工具的解析盲区**（图谱阶段手工补扫实证）——用 IDE/ctags 浏览 C API 实现时注意 wrappers.inl 里的内容不一定会被索引。

配套两个小门面：`amgxP_c.h`（16 导出，插件协议：第三方求解器以动态库形式注册进工厂体系）与 `amgx_eig_c.h`（5 导出，特征值求解器绑定——bindEigensolver 把 Eigensolver 绑到 solver 上，eigenvector 用于 deflation 或 PageRank 类应用）。

---

## 8. 新人上手：从 62 份预设到源码阅读路线

### 8.1 构建、示例与配置

**构建**（README.md Quickstart）：CMake 工程（根 CMakeLists.txt + src/CMakeLists.txt 双层），依赖 CUDA + MPI（可选，`AMGX_WITH_MPI` 开关）+ CCCL/thrust；产出 libamgx 与 examples。examples/ 目录有现成最小程序：`amgx_capi.c`（单卡 C API 全流程）、`amgx_mpi_capi.c`/`amgx_mpi_capi_agg.c`/`amgx_mpi_capi_cla.c`（多卡 + 聚合/经典配置样本）、`amgx_capi_multi.c`（多矩阵多解算器复用 Resources）、amgx_spmv_example（裸 SpMV）；测试矩阵 matrix.mtx 与生成器 generate_poisson.cu 就在手边，**clone 完先跑 amgx_capi.c 是最短正反馈回路**。

**配置系统三层入口对应三种用法**：

1. **62 份官方预设 JSON**（src/configs/*.json，ls 实证）：命名即语义——`AGGREGATION_JACOBI.json`、`AGGREGATION_DILU.json`、`AGGREGATION_GS.json`、`AGGREGATION_LOW_DEG_BJ.json`、`AMG_CLASSICAL_*.json`、`PCG_*`、`FGMRES_*`、`GMRES_*`、`PBICGSTAB_*`、`V/W_CYCLE.json` 等，覆盖「两大 AMG 变体 × PCG/FGMRES/GMRES/PBICGSTAB 外层 × Jacobi/GS/DILU 平滑」的组合矩阵。用户只需 `AMGX_config_create_from_file(&cfg, "FGMRES_AGGREGATION_DILU.json")` 一行即得完整参数树（经 amg_config.cu:104 parseParameterStringAndFile 消化）。
2. **8 份 eigen_configs**（src/configs/eigen_configs/，无扩展名）：ARNOLDI/LANCZOS/LOBPCG/JACOBI_DAVIDSON/POWER_ITERATION/SUBSPACE_ITERATION/PAGERANK/INVERSE_FGMRES，配合 amgx_eig_c API。
3. **内联字符串**：`AMGX_config_create(&cfg, "solver=FGMRES, cycle=F(1)")` 风格，key=value 分号串联（amg_config.cu:60）。

改预设时记住 config_version 1→2 的迁移逻辑（amg_config.cu:159-171）：新写配置一律 `config_version=2`（v2 才支持嵌套作用域语法）。

### 8.2 着色 11 策略与特征值子系统（L09）

多色 Gauss-Seidel/ILU 的并行化前提是**行着色**（同色行无依赖可并发）。`include/matrix_coloring/matrix_coloring.h:27` MatrixColoring 基类管理 color 索引与偏移，`MatrixColoringFactory`（:130，registerFactory :139）按配置 `matrix_coloring=<name>` 实例化 **11 种策略**（src/matrix_coloring/ 目录 12 个 .cu：11 策略 + coloring_utils）：

- 基线：uniform（全一色，等于 Jacobi 化）、round_robin；
- 贪心族：parallel_greedy（GPU 并行贪心，默认首选）、serial_greedy_bfs；
- 极小化最大色数：min_max、min_max_2ring、greedy_min_max_2ring（两轮通信窗口的分布式贪心）；
- 其他：multi_hash（哈希着色）、locally_downwind（下风着色，对流问题）、greedy_recolor（重着色优化）。

选型直觉：不确定就用 parallel_greedy；分布式大图色数爆炸时试 min_max_2ring。着色结果缓存在 Matrix 的属性里（matrix.h 的 MatrixBase 段管理生命周期），多色 smoother 直接按色偏移遍历。

特征值子系统同层：`include/eigensolvers/eigensolver.h:25` EigenSolver 基座（184 行）+ EigenSolverFactory（:151，registerFactory :161），注册 arnoldi/lanczos/lobpcg/jacobi_davidson/subspace_iteration/single_iteration；`src/amg_eigensolver.cu` 的 amg_eigensolver 顶层桥接；`multivector_operations.h`/`qr.h` 支撑多向量谱计算。用途有二：AMG 层级分析（谱半径估计平滑权重）与 PageRank/deflation 类应用（见 eigenvector_solver.h 与 pagerank_operator.h:13）。

### 8.3 源码阅读路线（图谱 16 步 tour 的浓缩版）

按依赖顺序、每步给"为什么值得读"：

1. **`include/basic_types.h:113`**（TemplateConfig 四参数 + :175 TemplateMode 模式萃取）与 `include/types.h:13`（ASSIGNMENTS: COARSE=-1/FINE=-2/STRONG_FINE=-3/UNASSIGNED=-4——classical 分裂的编码约定）——全库类型之根。注意 TemplateConfig 实际定义在 basic_types.h 而非 types.h（types.h 是枚举层），图谱 tour 的表述以此为准修正。
2. **`src/amg_config.cu:60-171`** ——读懂配置解析，后面所有组件的字符串参数都从这进。
3. **`src/amg.cu:147`（AMG_Setup functor）+ src/amg_solver.cu:188/:274** ——setup/solve 总装线；顺手看文件尾 ETI 清单（6 个精度组合）。
4. **`include/amg_level.h:51`** ——层级抽象，再各花十分钟看三个变体 Base 类（classical_amg_level.h:32 / aggregation_amg_level.h:35 / energymin_amg_level.h:31）的 setupAggregation/setupClassical 差异。
5. **`include/solvers/solver.h:22-310`** ——基类与工厂，然后按需跳进你想用的求解器头（fgmres_solver.h:49 是好样本）。
6. **`include/cycles/fixed_cycle.h:19` + src/cycles/fixed_cycle.cu:25-180** ——Dispatcher 策略化的教科书实现，读懂 template-template 参数这步最值。
7. **`include/matrix.h:65/989/1151` + include/operators/operator.h:34** ——数据与算子双根。
8. **`include/vector.h:95/143/405` + include/cusp/format.h:16-26 + include/cusp/array1d.h:44`** ——容器地基。
9. **分布式**：`include/distributed/distributed_manager.h:194`（先读注释与成员布局，2111 行不必通读）+ `src/distributed/distributed_manager.cu:2388-2403`（通信器选择）+ comms_visitors.h:144/180/212。
10. **`include/amgx_c.h`** 通读 81 导出注释（写得相当好），配 `src/amgx_c.cu` 的对应 impl。

### 8.4 测试框架与调试工具（L15）

- 测试骨架四件套：`include/unit_test.h:45` UnitTest 基类（:118 纯虚 run，断言宏与 UnitTestFailedException :39）、`src/utest.cu` 用例注册驱动、`include/test_utils.h`（821 行，向量比较/随机矩阵构造工具族）、`src/testframework.cu` 框架装配。60 个 `src/tests/*.cu` 专题测试是**理解各子系统的行为级文档**：aggregates_determinism_test.cu（聚合确定性）、block_conversion.cu、amg_levels_reuse.cu、fgmres_convergence_poisson.cu / IDR_Convergence_Poisson.cu（端到端收敛链）、ILU/DILU 等价、分布式 IO、C API 容错。改内核算法后跑对应专题测试是最快回归路径。
- 诊断工具：`include/error.h:101` FatalError 宏在抛出点捕获 `__FILE__/__LINE__` 配 stacktrace 回溯（amgx_exception 携带 reason/where/trace，error.h:61）；`include/amgx_timer.h` 条件编译切换 NVTX_RANGES/CUDA_PROF 后端（nsight 集成）；`include/determinism_checker.h:16` hash_path_determinism_checker——**以逐 kernel 输出哈希链替代位比较**，绕开浮点归约顺序不确定性来查"同一配置两次运行结果是否逐 kernel 一致"（多卡排障利器，src/determinism_checker.cu:19 私有实现）。
- `include/cutil.h`（62 入边）：设备查询/containsNan/printVector 等来自早期 CUDA SDK samples 的调试辅助。

### 8.5 新人常见坑清单（实证汇总）

1. **README 特性清单不含 energymin**，但代码完整支持（第 1 节勘误）——选型评估时以 include/energymin/ 为准。
2. **GPUDirect 不会自动启用**：默认 `communicator=MPI`（core.cu:338），要 `MPI_DIRECT` 显式配置且 MPI 库必须 CUDA-aware（第 7.2 节勘误）。
3. **AMGX_Mode 枚举值禁止按数值解释**（amgx_config.h:8 注释原文警告），绑定代码一律用标识符。
4. **`.inl` 文件是工具盲区**（amgx_c_wrappers.inl/hash_containers_detail.inl/hash_index.inl/sm_utils.inl）：IDE 索引/grep 类工具可能漏报其中的类与方法，读 C API 实现与 smoother kernel 时直接打开文件看。
5. **同名类靠命名空间区分**：classical/interpolators/interpolator.h:18 与 energymin/interpolators/em_interpolator.h:20 都叫 `Interpolator`，全局搜索时务必带路径限定。
6. **`.cu` 大多是离线模板定义不是算法本体**：先读 include/ 的类定义，再进 .cu 看 kernel。
7. **三座工厂别混**：solver（solver.h:271）、cycle（cycle.h:77）、convergence（convergence.h:104）各自独立注册，JSON 里配置作用域不同。
8. **混合精度的合法组合只有 6 种**（amg.cu 尾部 ETI），vec/mat 精度不是任意笛卡尔积——`AMGX_vecFloat × AMGX_matDouble` 这类组合不存在。

---

## 附：勘误与图谱口径说明

- 本文与图谱（1233n/3136e/15 层/16 步/0 issues）同 commit 基线 91a8413e；行号锚全部从源码逐条核实。
- 相对图谱摘要的三处修正：①TemplateConfig 定义在 basic_types.h:113（tour t01 表述为 types.h，types.h 实为枚举层）；②gpudirect 通信器为配置显式选择（core.cu:338 + distributed_manager.cu:2392-2400），非"运行时探测"；③README 特性行未列 energymin 变体。
- 图谱批甄别笔记（NOTES-DIGEST 36 条）已吸收进对应章节：Parameter 类型擦除（第 3 节）、Dispatcher 策略化（第 5 节）、cusp dispatch 编译期路由（第 6 节）、visitor 解耦（第 7 节）、determinism 哈希链（第 8.4 节）、.inl 盲区（第 7.3/8.5 节）。


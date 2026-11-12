# 02 cuBLASLt：精度阶梯、TestBench 模板枢纽与 CustomFind 搜索引擎

## 角色定位

cuBLASLt 是经典 cuBLAS 的低层对偶：不再一个函数一个算法，而是"描述符+算法对象+启发式"三件套。图谱 L04 层把它与 cuBLASMp 合并为"进阶 GEMM 域"。顶层 `cuBLASLt/CMakeLists.txt` 只有 38 行，用 20 个 `add_subdirectory`（:20-:39）聚合全部示例，且顺序本身就是一条精度阶梯：LtDgemmEmulated（fp64 仿真）→ LtSgemm（fp32）→ LtFp8Matmul → LtBlk128x128Fp8Matmul → LtMxfp8Matmul → LtNvfp4Matmul（:20-:25），再接 grouped 变体与 CustomFind/PlanarComplex/GreenContext 等专题。

## 内部结构

真正的骨架在 `cuBLASLt/Common/`（helpers.h 800 行 + helpers.cpp 667 行 + LtMatmulCustomFind.h 345 行）。核心是 `TestBench` 模板（helpers.h:119-:124）：六个类型参数 `InTypeAB, OutType=InTypeAB, ComputeType=OutType, ScaleType=ComputeType, DScaleType=ScaleType, InTypeC=OutType`，一套默认值链让最简写法 `TestBench<float>` 一词成型（LtSgemm/main.cpp:21）。四个构造器伸缩式委托（helpers.h:128-:259）逐步补齐 alpha/beta、缩放张量、scale mode 等高级参数；成员区一次性容纳 bias、指针数组批处理（APtrArrayHost 等，:726-:734）与 grouped GEMM 的 m/n/k 数组（:747-:767）。`run()` 只有四行（:695-:702）：copyToDevice → runSample 闭包 → copyFromDevice → sync——示例 main 只需构造 bench 并塞进一个 lambda。helpers.cpp 的 667 行里 635 行是一张 `matmulTileName[]` 硬编码 tile 名表（:22-:658），`tileToString`（:661-:667）做越界检查的查表——tree-sitter 只捕到 1 个函数正是因为主体是显式数据。

## 外部连接

每个示例 CMakeLists 引 `../Common` 头文件路径并链接 cublasLt+cudart（LtSgemm/CMakeLists.txt）。TestBench 通过 `StorageType<__nv_fp4_e2m1>`（helpers.h:45）处理 fp4 打包存储，`isNarrowPrecision()`（:114-:117）判定 fp8/fp4 走缩放路径；fillData 对 half/fp4 组合显式特化（:770-:798）。CustomFind 头被 LtSgemmCustomFind 与 LtFp8CustomFind 两示例共用。

## 数据流

LtFp8CustomFind 的 main 仅 36 行（`cuBLASLt/LtFp8CustomFind/main.cu`）：`TestBench<__nv_fp8_e4m3, __nv_fp8_e4m3, float, float, float, __nv_bfloat16>`（:25）声明 A/B=e4m3、计算 fp32、C 入 bf16；几何 1024×512×4096、workspace 16MB（:26）；lambda 里一行调 `LtMatmulCustomFind`（:29-:32），A=e4m3、C=bf16、D=e4m3、alpha/beta fp32。引擎本体在 LtMatmulCustomFind.h：先建 operation 描述符与四个 layout（:175-:187），`cublasLtMatmulAlgoGetIds` 拿算法 ID 池（:189），再探测设备是否支持 cluster launch（:198-:200，Hopper 以上才展开 `CUBLASLT_CLUSTER_SHAPE` 维度）；随后是六层嵌套枚举 tile→stages→cluster→customOption→swizzle→splitK（:247-:327），splitK 试探序列硬编码 `{2,3,4,5,6,8,12,16,32}`（:162），每个组合经 `customMatmulRun` 计时（:68，event 计圈、`kernelRepeats=10` :167，workspace 不足判 NOT_SUPPORTED :123），上限 100 个组合（`ALGO_COMBINATIONS` :164），最后 `std::sort` 按耗时排序打印（:330，`printPerfStructure` :41-:62 逐项解包 algoId/tile/splitK/swizzle/stages）。

## 设计决策

两个决策值得注意：其一，示例与引擎彻底分离——20 个示例的 main 全部<40 行，差异只体现在 TestBench 类型参数与几何，符合"教 API 不教实现"的定位；其二，CustomFind 暴露完整搜索空间是 cuBLASLt 与 cuBLAS 的本质分野（heuristic 默认 vs 手动调优）。勘误一处：`LtMatmulCustomFind.h:338-:344` 清理段销毁 preference/Cdesc/Bdesc/Adesc/operationDesc/两个 event，唯独漏掉 :187 创建的 Ddesc（泄漏）；且 `preference` 声明后从未创建（:158 置 NULL），其销毁是死代码——官方示例也有 cleanup 瑕疵。

## 新人提示

入门顺序建议 LtSgemm（看 TestBench 最简形态）→ LtFp8Matmul（看缩放类型参数如何流动）→ LtFp8CustomFind（看搜索空间全貌）。读 helpers.h 先看 :119-:124 的默认值链与 :260-:273 的构造体初始化列表，成员即数据流清单。调优自己的 GEMM 时直接抄 CustomFind 的六层循环骨架，把 `ALGO_COMBINATIONS` 与 splitK 序列当作预算旋钮。

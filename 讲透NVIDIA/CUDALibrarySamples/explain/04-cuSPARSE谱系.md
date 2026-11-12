# 04 cuSPARSE 谱系：35 个示例铺满稀疏算子全谱

## 角色定位

cuSPARSE 是全仓覆盖最完整的"算子谱系库"：35 个示例目录从向量级原语（axpby/rot/gather/scatter/spvv）一路铺到 SpMV/SpMM/SpSV/SpSM、SDDMM、SpGEMM 与迭代求解器（cg/bicgstab），外加格式转换（dense2sparse_csr/blockedell、sparse2dense、coosort、compression）与图捕获专题（图谱 L05 层 150 节点、t05 导览）。语言分布实证：33 个纯 C（.c）+ 仅 2 个 C++（compression_example.cpp 267 行、spmm_blockedell_example.cpp 171 行）——compression 需要 RAII 模板类管理 VMM 资源，故弃 C。勘误：README 只列 31 例，sddmm_bsr、spmvop_csr、spmv_sell、spsv_sell 四个目录未被收录。

## 内部结构

最简原型 axpby（109 行）给出 generic API 标准型：`cusparseCreateSpVec`/`CreateDnVec` 建描述符（`cuSPARSE/axpby/axpby_example.cu:76-80`）、一行 `cusparseAxpby`（:83）、宿主机逐元素验证（:93-99，注释自嘲"直接浮点比较在标准代码里不可靠"但此处值皆为精确可表示）。矩阵算子同构：描述符（CSR/COO/BSELL 由 create 函数族区分）→ bufferSize → (analysis) → execute。SpGEMM 展示两段式预算：`cusparseSpGEMM_workEstimation` 先空 buffer 探 nnz 上界再带 buffer 二次调用（`spgemm/spgemm_example.cu:134/:142`），`compute`（:149/:156）后 `copy` 落格式，beta≠0 时 C 值会被复用更新（:175 注释）；spgemm_mem/spgemm_reuse 两个变体分别演示用户自管内存与描述符复用。

两个迭代求解器是"cuSPARSE+cuBLAS 协同"的完整教材（均为 C，gcc 语义即纯 C 编译）：`cg_example.c`（497 行）先 `make_laplace_matrix` 造 5 点 Laplacian（:71-:128，grid=700 → n=490000、nnz=5n-4g=2447200，对角加 mass=0.04 :100 专为 ICHOL 稳定）；`gpu_CG`（:132-:307）里 SpMV/SpsV 归 cuSPARSE（:156/:220，三解 L⁻¹L⁻ᵀ 预条件 :167-:198），dot/nrm2/axpy/scal 归 cuBLAS（:206/:211/:227/:237/:243/:247/:273/:283）。bicgstab（591 行）同构无预条件版（`gpu_BiCGStab` :131 起）。

## 外部连接

cg/bicgstab 与 cuBLAS 域（篇 01）直接互操作——这是仓内少有的跨库示例。compression_example.cpp 独树一帜地深入 CUDA 驱动 API VMM：`cuMemCreate` 时置 `CU_MEM_ALLOCATION_COMP_GENERIC`（`cuSPARSE/compression/compression_example.cpp:73`）、查 granularity（:81）、`cuMemAddressReserve`→`cuMemMap`→`cuMemSetAccess` 三步挂载（:87-:103），析构对称回收（:115-:117），退路是普通 cudaMalloc 的模板分叉（:132）；随后用同一 `cusparseAxpby`（:168）+ event 计时（:173-:174）演示压缩显存的可用性。它与 graph_capture（`cudaStreamBeginCapture` 流捕获范式）一起构成"库 API 之外的系统课"。

## 数据流

通用数据流：宿主 CSR/COO 数组 → cudaMemcpy → 描述符包装 → bufferSize/malloc external buffer → execute → 拷回验证。cg 的数据流最丰富：A 与 L 共享 row/col 数组仅 values 分离（:382-:383，IC 就地因子化）；文件里新旧两代 API 并存是重要考点——矩阵侧用 generic `cusparseSpMatDescr`（:387-:395），IC(0) 预条件却用 legacy `cusparseMatDescr_t`+`cusparseDcsric02` 全家（:423-:457 含 zeroPivot 检查），正是迁移期代码的真实写照。

## 设计决策

三分层选型清晰：教学型小例（8 元素向量）保证手验可行；求解器例（49 万阶）演示真实规模但收敛阈值 1e-8、上限 10000 迭代（:313-:314）给出可复现终止条件；性能型专题（compression/graph_capture）不追求正确性叙事而演示机制。SpGEMM 的 workEstimation/compute/copy 三段拆分让 nnz 未知的问题可两遍完成，代价是 API 面扩大——两个变体示例正是在教如何消化这个代价。

## 新人提示

按 axpby → dense2sparse_csr → spmv_csr → spmm_csr → spgemm 的顺序走完即掌握 generic API 全貌；做格式选型时对比 spmv_csr/coo/sell 三例的描述符差异。读 cg 先看 :71 生成器与 :382 的共享数组技巧；写自己的求解器时直接抄 CHECK_CUDA/CHECK_CUSPARSE/CHECK_CUBLAS 三宏（:26-:54）。compression 例只应在支持压缩的驱动/设备上跑，且注意其析构路径对称性——这是它作为唯一深度驱动层示例的教学点。

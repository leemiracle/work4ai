# 03 · transforms 立即执行层与 exec 驱动

> 对象：`include/matx/transforms/` 直接子文件约 30 个（子目录后端另篇）。
> 勘误（甄别条款）：①"matxTransformOp"不存在——真实标记是嵌套类型 `matx_transform_op`（`operators/sum.h:64`）+ trait `is_matx_transform_op`（`core/type_utils_both.h:203`）；②"convert 直接子文件"不存在，`convert/` 是子目录；③transforms.h 只 include 一个头（`transforms/transforms.h:35`），其余经 operators 进 matx.h。

## 一、角色定位

`A = B + C` 与 `(out = expr).run(cudaExecutor(stream))` 在 `.run()` 前只建类型不碰数据；执行一刻控制流进 `BaseOp::run`（`operators/base_operator.h:181`），所有"重"操作的实现住在 transforms/。三层分工：**operators/** 是表达式语法门面，`Exec()` 只一行转调（`operators/conv.h:190`）；**transforms/** 是立即执行层，每个重操作一份 `*_impl(out, in..., executor)` 自由函数，持有 kernel 启动、库句柄、plan 缓存与临时内存生命周期；**kernels/** 仅 11 个 `.cuh`，只放无库可用的自研信号 kernel——reduce 无自研 kernel，CUDA 路径全交 CUB（`transforms/reduce.h:653`）。include 枢纽是 reduce.h，拉入 cub.h 等（`transforms/reduce.h:47-49`）。

## 二、内部结构

`BaseOp::run` 依次判 CUDAJITExecutor（免 PreRun/PostRun，`operators/base_operator.h:189`）→ 动态秩拒绝 → mtie → set 细分五路：分布式物化 / **transform 短路** / 直填 / 张量到张量 `cudaMemcpyAsync`（:258）/ 通用路径。transform 判定 `is_matx_transform_op<T::op_type>() && is_tensor_view_v<T::tensor_type>()`（:215），再 `TransformExec`（:222）。

**TransformExec 是钥匙**（`operators/set.h:504`）：`op_.InnerPreRun`（递归触发嵌套输入的临时分配）→ `op_.Exec(make_tuple(out_))`（transform 输出直接写用户 LHS）→ `PostRun`，注释明言是避免额外 async allocation 的 shortcut。对照通用路径（RHS 普通表达式）PreRun（:276）→ `ex.Exec(*tp)`（:279）→ PostRun（:282）：RHS transform 先在临时张量算完（sum 例 `operators/sum.h:330/333`），元素级 kernel 物化到 LHS，`matxFree`（:343）——差别即一次分配加一趟拷贝。

**plan 缓存代表——CUB 封装**：`matxCubPlan_t`（`transforms/cub.h:303`）构造时先以 `d_temp=nullptr` 调 Exec 探测 `temp_storage_bytes`（CUB 两阶段 API），再 `matxAlloc(..., MATX_ASYNC_DEVICE_MEMORY, stream)`（:376）；析构 `matxFree`（:427）。外壳 `cub_sum`（:2157）先试转置归约快路径（:2163），再 `GetCache().LookupAndExec`（:2119）——MISS 建 plan 入缓存，HIT 只 SetParams+Exec。缓存 key=线程/设备/类型哈希/形状/dtype/stream（`core/cache.h:222`）。

**数据移动三代表**：reduce——CUDA 路径 `sum_impl` 一行转调 `cub_sum`（`transforms/reduce.h:653`），按输出秩分流 SegmentedReduce（`transforms/cub.h:947`）或全量 Reduce（:979）；transpose——非连续输入直接 throw（`transforms/transpose.h:75`），shared memory 按 `TILE_DIM*(TILE_DIM+1)` 申请消 bank conflict（:81），grid 按 tile 取整（:85），kernel 是 `kernels/transpose.cuh:28` 的 32×32 tile（:20）直写交换读，Host 版是 permute 委托（:118）；copy——本体就是 `(out = in).run(exec)`（`transforms/copy.h:73`），set 的语法糖。

## 三、外部连接

**向上**：门面→实现一一对应（`operators/sum.h:305`、`operators/transpose.h:123`）；门面带 `matx_transform_op` 标记让 run 认出重操作走短路。**向下**：有库一律桥接——归约/排序/扫描→CUB（`transforms/cub.h:947`），长卷积→cuFFT，求解→cuSolver（`transforms/solver_common.h:187` 基类）。适配器 `RandomOperatorIterator`（`core/iterator.h:49`）把任意惰性算子包成 random_access_iterator 现场求值；`ReduceInput`（`core/reduce_utils.h:98`）对秩<2 连续 view 走裸指针，否则折叠维度再包迭代器。`transforms/cccl_iterators.h:40` 是 CCCL≥3.2 迭代器垫片。自研 kernel 仅限无库信号族（conv 直卷/filter/pwelch/find_peaks/resample_poly/channelize_poly/sar_bp/matvec/transpose，见 `transforms/resample_poly.h:173/189` 两变体），与 kernels/ 11 个 `.cuh` 对应。**向侧**：每个 `*_impl` 按执行器重载成对（`transforms/reduce.h:647/675`），域选择编译期完成；cudaExecutor::Exec（`executors/cuda.h:85`）负责元素级 kernel，`find_best_launch_params` 搜 (EPT,block,group)（:113）；自研 kernel 用 `get_grid_dims`（`core/get_grid_dims.h:46`）。Host 侧：OMP 且过阈值（`transforms/host_algorithms.h:56`）才 `thrust::omp::par`（:120）。

## 四、数据流

`(Vo = sum(Vi,{1})).run(stream)` 时序：set 对象 → run 的 transform 分支（`operators/base_operator.h:215`）→ `TransformExec`（:222）→ `sum_impl`（`operators/sum.h:305`）→ `cub_sum`（`transforms/reduce.h:653`）→ 转置快路径（:2163）失败则查缓存（:2119）→ MISS 构造 `matxCubPlan_t`（:303）探测并 `matxAlloc`（:376）→ `ReduceInput` 选裸指针或迭代器 → SegmentedReduce::Sum（:947）。全程零 host 同步、零额外物化。

**临时内存三范式**：(a) operator PreRun/PostRun——嵌在更大表达式时 AllocateTempTensor（`operators/sum.h:330`）分配、`matxFree`（:343）同 stream 释放；(b) plan 持有——CUB/cuFFT workspace 存进缓存对象，析构才释放（`transforms/cub.h:427`）；(c) 即用即弃——pwelch 先 `(X = fft(x*w,nfft)).run(stream)`（`transforms/pwelch.h:62`）再自研 kernel 归一（:69）；percentile 借道 sort（`transforms/percentile.h:100`）；sar_bp 用 `GetStreamAlloc` 按精度档实例化五种模板 kernel（`transforms/sar_bp.h:188/195`）。

## 五、设计决策

1. **plan 缓存优先**：CUB 探测/cuFFT 句柄创建昂贵，全入 `GetCache()`（`core/cache.h:222`）；代价是全局一把锁与 plan 进程级存活，`MATX_DISABLE_CUB_CACHE`（`transforms/cub.h:2170`）可关。
2. **短路省一次物化**：`(A = sum(B))` 通用路径需临时张量+元素级拷贝，短路让 CUB 直接写 A；`can_alias`（`core/type_utils_both.h:228`）可豁免别名检查。
3. **stream 序异步内存**：分配、kernel、释放全排进同一 stream（`core/allocator.h:223`），host 零同步。
4. **买库 vs 自研界线**：conv 双路——DIRECT 自研 kernel（CUDA-only，host 端 `transforms/conv.h:432` throw），AUTO/FFT 走 cuFFT 路（:448）。
5. **域编译期选择 + 表达式喂库**：impl 按执行器成对重载零运行时开销；RandomOperatorIterator+ReduceInput 让 CUB 直接消费惰性表达式。`run(cudaStream_t)` 重载（`operators/base_operator.h:307`）自动包 executor，两种触发同路径。

## 六、新人提示

- 断点：`BaseOp::run`（`operators/base_operator.h:181`）是总入口；短路判定 :215/:222；重操作跳转链 operators/X.h→transforms/X.h。
- 别名检查由 `MATX_EN_UNSAFE_ALIAS_DETECTION` 门控（:218），关编译时不查；表达式按值进 kernel 有 `CUDA_MAX_VAL_PARAM` 上限（`executors/cuda.h:98`），只约束元素级路径。
- host transpose 是 permute 表达式（`transforms/transpose.h:118`）；非连续输入 CUDA 版直接抛（:75）；conv DIRECT 方法 CUDA-only（:432）。缓存 key 含 stream：多流场景 plan 与显存放大。
- 阅读顺序：run 分派树 → `operators/set.h:504` → 任一 `*_impl`（transpose.h 最短）→ cub.h → cache.h。

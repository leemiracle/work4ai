# 06 · 数据线：RAPIDS 与 GPU 数据科学

> 系列第 06 篇：**GPU 数据科学为什么快、生态位在哪**。原料 cudf/cuml/cuCollections/cuvs/cuopt/cudf-spark/nvImageCodec/nv-embedding-cache（九仓 deepwiki + 四仓本地源码）；横切底座 NVIDIA-CUDA-STACK.md。行号锚 2026-11-04 于 `/usr-data/data2/repos/agent-repos/NVIDIA/` 核实（cudf@94d6af3、cuml@62dd6647b、cuCollections@0293849、cuvs@697e449）。

## 一、第一性原理设问：数据科学负载到底吃什么资源

把 ETL/特征工程拆到算子级：group-by = 顺序扫描 + 哈希归并；join = 建表 + 逐行探测；sort = 多遍 radix；过滤/变换 = 逐元素流。共同点：**每字节数据只伴随个位数 flops**——与 GEMM 每 byte 数百 flops 正相反。放回 roofline：这些操作全部趴在"带宽腰"上，算术强度 < 1 flop/B。结论一：**数据科学的加速比上限 ≈ 内存带宽比**。H100 HBM3 是 3.35 TB/s，双路服务器 DDR5 约 0.5 TB/s（≈7×）；B200 HBM3e 8 TB/s（≈16×）。这就是 cudf 实测"5-20×、常在 10× 量级"的物理出处——不是魔法，是带宽代差。

但 GPU 的数据不在这块快内存里。PCIe Gen5 x16 理论 64 GB/s、实测约 50 GB/s，比 DDR 还低一个量级。设 CPU 每字节处理耗时 t_cpu、GPU 端加速比 R（≈带宽比）、PCIe 带宽 B_pcie，则端到端加速比：

$$S \;=\; \frac{t_{cpu}\,D}{D/B_{pcie} + t_{cpu}D/R} \;=\; \frac{a\,R}{a+R},\qquad a \equiv t_{cpu}\cdot B_{pcie}$$

这是 a 与 R 的**调和平均**——被较小者卡死。a 的物理含义："PCIe 搬一个字节的工夫，CPU 能处理几个字节"。例：10 GB 全表扫描+变换，pandas 跑 100 s（t_cpu=10 ns/B），则 a=500，S≈6.9（搬运可忽略）；换成轻量过滤 t_cpu=0.1 ns/B（同一表 1 s），a=5，S≈2.9，再叠加每算子 ~10 µs 的 kernel launch 与 host 端对象开销，**小数据/轻变换 GPU 必输**。立得住的场景由此推出，只有两个：**数据已在 GPU 上**（前接推理/训练/GPU 解码，零搬运），或**数据量大到搬一次摊得平**（GB 级起步）。整条 RAPIDS 产品线——列式内存、算子底盘、零代码代理、Spark 插件——都是在把"搬运次数"压向零的工程。

## 二、直觉层：货架、料仓与整车厂

**列存 vs 行存 = 图书馆按主题分架 vs 每人一个档案袋**。统计"全表年龄均值"：行存要把每个档案袋翻开取一页；列存是把年龄架从头扫到尾——顺序流式，正是带宽设备的最爱。落到 SIMT：warp 里 32 线程读同列相邻 32 个 int32，合成一次 128 B 事务（coalesced）；行存下每线程跨行跳步，128 B 事务里只用到 8 B，带宽直接打 16 折。**GPU 列式不是数据帧的偶然形态，是 coalesced 访存的必要条件**。

**cudf 三件套 = 货架体系**：`column` 是标准集装箱（数据 + 有效位图 + 长度），`table` 是等长集装箱的货架，`column_view`/`table_view` 是贴在货架上的清单——指得到货物、不拥有货物。所有算子收发 view，所有权只在边界处移动一次。

**cuco static_map = 工地料仓**：开仓前按预期存量（键数 ÷ 0.5 装载率）一次性定容量，线程凭探测序列（probing scheme）找空位；装满超过水位就得停工开更大的仓（rehash）。为什么 GPU 哈希表偏爱"static"：CPU 的 std::unordered_map 可以随时 rehash，GPU 上 rehash 意味着全体线程停顿重排、代价巨大——所以 libcudf 的 groupby/join 都走"build 一次（插键）、probe 多次（查键）"的静态料仓模式。

**RAPIDS 复用网络 = 水煤电-标准件厂-整车厂**：rmm 是水煤电（统一显存分配器），cuco/raft 是标准件厂（并发容器、通信与数值原语），libcudf 与 cuvs 是两家发动机厂（关系算子+IO / 向量检索+聚类），cuml、cudf.pandas、cudf-spark 是整车厂——装同一套底盘、卖不同的车（sklearn 面、pandas 面、Spark 面）。

## 三、机制层：从列式内存到算子底盘

### 3.1 列式三件套与 Arrow 零拷贝边界

libcudf 的所有权分层从类定义处一眼可见：`column` 是"拥有 nullable 设备数据的列容器"（`cudf/cpp/include/cudf/column/column.hpp:37`），`table` 是"一组同尺寸 column"（`cudf/cpp/include/cudf/table/table.hpp:31`），两者都只提供移动构造、深拷贝显式付费（构造函数收 `cuda::stream_ref` 与 `rmm::device_async_resource_ref`）；只读路径全走 `column_view_base` 层（`cudf/cpp/include/cudf/column/column_view.hpp:44`）。null 语义用位图（bitmask）不是 0/1 字节——这是向 Arrow 对齐的刻意选择，也是与 numpy bool 数组的本质差异。

Arrow 互操作是 RAPIDS 与外部世界的合同。`to_arrow_device` 的头文件注释写得很精确："without performing copies if possible"（`cudf/cpp/include/cudf/interop.hpp:508`），并且白纸黑字列出**三类必须拷贝的例外**（`interop.hpp:551-560`）：BOOL8（Arrow 用位图、cudf 用每值 1 字节）、DECIMAL32/64（cudf 不存精度，统一升格 decimal128）、STRING（Arrow 要求空串列有 int32 offset 子数组）。反方向的 `from_arrow` 用 `custom_view_deleter` 保住例外情形下分配的内存（`interop.hpp:149-154`）。所以"Arrow 零拷贝互操作"的准确表述是：**设备内存上的列数据默认零拷贝，例外恰好是三处表示分歧**——数据帧界的 USB-C 也有转接头。

变长类型的列式表示是同一逻辑的延伸：字符串列不是"每行一个 string 对象"，而是**两条子列**——offsets（每行的字节起点）+ 连续 chars 缓冲（`cudf/cpp/include/cudf/strings/strings_column_view.hpp:53` 的 `offsets_column_index` 把它建模为第 0 号子列）。好处是遍历字符数据仍然是顺序流（正则/子串/哈希全部可并行切分），代价是任何"按行取串"都要 offsets→chars 一次间接寻址——这正是字符串-heavy 负载在 GPU 上收益打折的结构原因，也是 nvtext 要自带并行 regex 引擎（字符类有限状态机编译成 kernel）而非复用 CPU 正则的根本动机。

### 3.2 groupby/join 的 build 侧：cuco static_set 实证

哈希聚合的心脏在 `cudf/cpp/src/groupby/hash/`。类型定义处（`helpers.cuh:87-95`）：`global_set_t = cuco::static_set<cudf::size_type, cuco::extent<int64_t>, cuda::thread_scope_device, row_comparator_t, probing_scheme_t, rmm::mr::polymorphic_allocator<char>, cuco::storage<GROUPBY_BUCKET_SIZE>>`——七个模板参数各自回答一个问题：键是行号（size_type）、容量按 int64 extent 预定、设备级线程作用域、**多列组合键不拼接而是逐列比较**（row_comparator 处理 nullable 行等值）、探测方案、内存走 rmm 分配器、桶存储形态。

构造现场（`compute_groupby.cu:92-102`）：`cuco::static_set{cuco::extent<int64_t>{num_keys}, cudf::detail::CUCO_DESIRED_LOAD_FACTOR, cuco::empty_key{CUDF_SIZE_TYPE_SENTINEL}, d_row_equal, probing_scheme_t{row_hasher_with_cache_t{...}}, ...}`。三个工程细节：①`CUCO_DESIRED_LOAD_FACTOR = 0.5`（`cudf/cpp/include/cudf/detail/cuco_helpers.hpp:16`）——装载率压到一半，是用内存换探测长度（open addressing 的期望探测次数随装载率陡增，50% 时平均 ~1.5 次探测定序）；②空键哨兵用 `CUDF_SIZE_TYPE_SENTINEL = -1`（`cuco_helpers.hpp:13`）；③**哈希带缓存**——先把全部行哈希算好（`compute_groupby.cu:85` 附近的 `hashes` lambda），探测时比较哈希先短路、逐列比较只在哈希撞车时发生。

join 侧同构：`cudf/cpp/src/join/key_remapping.cu:31` 引 `cuco/static_set.cuh`，`:257` 定 `probing_scheme_type = cuco::linear_probing<1, key_hasher>`——单槽步进的线性探测，GPU 上比双重哈希缓存行为更友好；build 侧同样以哈希+行号入表，probe 侧拿左表行号批量探测。**cuCollections 自身的分层**是这套玩法能成立的原因：`static_map`（`cuCollections/include/cuco/static_map.cuh:88`）是 host 端拥有内存与生命周期的"料仓"，`static_map_ref`（`static_map_ref.cuh:58`）是可按值传进 kernel 的设备视图，`dynamic_map`（`dynamic_map.cuh:47`）用分块+迁移支持运行时增删——libcudf 选前两者，因为 SQL 算子天然是"build 一次 probe 多次"。

### 3.3 复用网络的真实拓扑（本篇最大勘误点）

"libcudf 的 join/groupby 原语被 cuml/cuvs 复用"是流传最广的印象，但源码不给面子：**cuml 与 cuvs 的 C++ 层零 libcudf 引用**（grep 全仓实证），cuml 的 CMake 依赖清单是 cccl/rmm/raft/cuvs/treelite（`cuml/cpp/CMakeLists.txt:277-289`）。复用是**纵向的、分层的**，不是横向的：

| 层 | 仓 | 提供什么 | 谁在用 |
| --- | --- | --- | --- |
| 显存分配 | rmm | 统一分配器/内存池（水煤电） | 全家 |
| 并发容器/原语 | cuco、raft、CCCL | static_map/set、通信、scan/sort | libcudf、cuvs、cuml |
| **域特化 A：关系算子** | libcudf | join/groupby/sort/IO | cudf Python、cudf.pandas、cudf-polars、Java JNI→**cudf-spark**（`cudf-spark/sql-plugin/.../Plugin.scala:398` 以 SparkPlugin 注入） |
| **域特化 B：ANN/聚类** | cuvs | IVF-PQ/HNSW/CAGRA、kmeans、距离 | **cuml**（`cuml/cpp/src/kmeans/kmeans_fit.cu:58` 直调 `cuvs::cluster::kmeans::fit`；`tsne.cu:12` 用 `cuvs/distance`） |
| 上层 API | cuml / cudf.pandas / cudf-spark | sklearn 面 / pandas 面 / Spark 面 | 终端用户 |

所以准确的说法是：**RAPIDS 的公共底盘是 rmm+cuco+raft（内存+容器+原语），libcudf 与 cuvs 是底盘上两个平行的域特化，cuml 是站在 cuvs 肩上的 ML 门面**。cudf 与 cuml 在 C++ 层互不相识，只在 Python 层握手（cuml 估计器直接吃 cudf.DataFrame 输入，`cuml/python/cuml/cuml/cluster/kmeans.pyx` 的 output_type 支持 'cudf'）。

### 3.4 cuvs：ANN 索引与 RAG 时代接驳

向量检索是"数据已在 GPU"生态位的完美案例：embedding 由 GPU 推理产出，检索本就与推理同驻。cuvs 的三族索引对应三个物理权衡：**IVF-PQ**（倒排+乘积量化，内存省 8-32×，有损）以 `ivf_pq::index` 类为主体（`cuvs/cpp/include/cuvs/neighbors/ivf_pq.hpp:476`）；**HNSW** 是 CPU 生态王者，多层图结构串行贪心；**CAGRA** 是 GPU 原生的单层图索引——查询 = 一批 query 并行地在图上做束搜索（`cagra.hpp:1365` 起 `search()` 的六组模板实例化对应多 dtype/IdxT 组合），batch 间天然并行，正好填满 SIMT；建图走 NN-Descent 迭代细化，也是大吞吐并行负载。

最能说明生态位设计的是**混合部署出口**：`cagra.hpp:3037` 的 `serialize_to_hnswlib`——GPU 上建好 CAGRA 图，序列化成 hnswlib 兼容格式给 CPU 服务进程用；映射策略由 `hnsw_heuristic_type`（`cagra.hpp:266`，SIMILAR_SEARCH_PERFORMANCE vs SAME_GRAPH_FOOTPRINT）选择。GPU 当建图工厂、CPU 当查询引擎，一份数据两种部署。RAG 检索链的另一半是 embedding 查询缓存：nv-embedding-cache 提供 GPU set-associative 缓存层（deepwiki 7.1 组相联设计），后端可挂 RocksDB/Redis（6.x 插件体系），Triton 集成（8.6）——它管的是"高频 embedding 别反复过 PCIe"，与 cuvs 的"批量 ANN"互补。

### 3.5 cuopt：运筹优化为什么姓"GPU 数据"

线性规划的现代求解器三个引擎并存：内点法（barrier）、对偶单纯形、PDLP（一阶法）。barrier 每轮迭代要解一个大而稀疏的 KKT 方程组——cuopt 的实现是 **cuDSS 稀疏 Cholesky**（`cuopt/cpp/src/barrier/barrier.cu:919` 实例化 `sparse_cholesky_cudss_t`，配套 `csr_kkt_build.cuh`/`device_sparse_matrix.cu` 全是稀疏 CSR 设施），稀疏三角分解是典型访存 bound，与 groupby 同吃一条带宽逻辑——这是 cuopt 在"数据线"而非"算子线"的根本原因。MIP 则在其上叠 branch-and-bound（`branch_and_bound/`），GPU 加速的是节点 LP 松弛的批量求解；routing（VRP）走元启发式+约束传播（`routing/`），邻域评估高度并行。摄入端再往前一步是 nvImageCodec：JPEG/JPEG2K/TIFF 解码本身放上 GPU（nvJPEG 系扩展，CPU 解码器作 fallback），让"图像→张量"管线全程不落地——与训练线 DALI 同一动机。

## 四、程序员实操：零代码迁移三件套与内存护栏

**迁移路径按改动成本升序排**：

1. **cudf.pandas（零行代码改动）**：notebook 里 `%load_ext cudf.pandas`，脚本里 `python -m cudf.pandas script.py`。机制：install() 调 `ModuleAccelerator.install("pandas", "cudf", "pandas")`（`cudf/python/cudf/cudf/pandas/__init__.py:34-37`）挂 import hook（`module_accelerator.py:192` 的 `exec_module`），此后 `import pandas` 拿到的是代理模块；每个对象都是 fast/slow 双态代理（`fast_slow_proxy.py:816` 的 `_FastSlowProxy`）——GPU 路径能执行的走 cudf，不能的（`to_excel`、闭包 lambda、冷门 API）自动带着数据落回 CPU pandas，数据经 Arrow 搬运。**用 `cudf.pandas.profiler.Profiler` 或 line profiler 看哪些行走了 slow path**——那是优化清单。
2. **cuml.accel**：`import cuml.accel; cuml.accel.install()` 后 sklearn 代码不改一行（代理 estimator 体系，与 cudf.pandas 同构）；子进程跑原版 sklearn 测试套做兼容性回归（deepwiki 4.3）。
3. **cudf-polars**：`polars.LazyFrame(...).collect(engine="gpu")`——polars IR 直接编译到 libcudf，流式执行器支持超显存数据集。
4. **Spark 作业**：`rapids-4-spark` jar + `spark.rapids.sql.enabled=true`，插件经 SparkPlugin 扩展点注入（`Plugin.scala:398`），把 Catalyst 物理计划逐节点换成 GPU 算子（GpuColumnVector 列式），不支持的算子按代价模型回退 CPU；shuffle 换 RapidsShuffleManager（UCX 直传显存）。

**内存护栏**：`cudf.set_option("spill", True)` 或环境变量 `CUDF_SPILL`（`cudf/python/cudf/cudf/options.py:224`）启用 buffer 级 spill——SpillableBuffer 把设备内存换出到 host，取用时再换回；`spill_on_demand` 默认 True（`options.py:237`），挂 RMM 的 OOM handler 在分配失败时自动腾挪。配套纪律：拿到裸设备指针（`.ptr`）的 buffer 会被标记 exposed、永久失去 spill 资格——混用 cupy/自定义 kernel 时注意。dask-cudf 把这张护栏扩展到多卡（partition 级 spill+显存感知调度）。

**四个高频坑**：①**小数据 GPU 反而慢**——第一节调和平均公式已给定量解释，经验阈值：数据 < 数百 MB 且操作轻，先测再迁；②**host-device 往返吃掉一切**——`.to_pandas()`/`.to_numpy()`/打印 DataFrame 每次都是全量 PCIe 搬运，循环里放一次就清零收益，结果落盘用 `to_parquet`（GPU 直写）；③**逐行 apply/lambda 是伪并行**——要么回 CPU 要么编译（cudf 的 numba UDF / cubin JIT），str 列的正则走 nvtext 的并行 regex 引擎而非 Python re；④**shuffle 类算子瓶颈在传输**——分布式 groupby/join 的宽依赖走网络，GPU 只加速本地部分，收益要看 AQE/分区数配置。

## 五、批判边界

1. **调和平均封顶**：S=aR/(a+R)。a=t_cpu·B_pcie 由工作负载决定——"GPU 版 pandas"对轻变换小表永远无解，这不是实现问题，是 PCIe 物理决定的。
2. **零代码迁移的暗税**：fast/slow 每次切换都经 Arrow 走一次 host 搬运；代理层对 pandas 的兼容是"高频路径全覆盖+长尾自动回退"，**回退本身可能比纯 pandas 更慢**（多一层代理+多一次搬运）。迁移前先 profiler 摸清回退面。
3. **单卡显存墙**：spill 是"读一次 PCIe 写一次 PCIe"的以时间换空间，TB 级数据要么 dask-cudf 分布式要么 cudf-polars 流式；显存预算要给 build 侧哈希表留 2× 余量（50% 装载率的直接代价）。
4. **ANN 的三角约束**：IVF-PQ 有损（recall 换内存），CAGRA 图常驻显存（百万级向量 × 度 64 × 4B ≈ 数 GB），serialize_to_hnswlib 出口意味着 NVIDIA 自己也承认"GPU 建图+CPU 服务"是常见终态——不是所有环节都该留在 GPU。
5. **cuopt 不是免费的 Gurobi 杀手**：MIP 的 branch-and-bound 是本质串行搜索树，GPU 加速的是节点松弛批量求解；PDLP 对坏条件问题收敛慢。规模与结构（稀疏度）决定胜负。
6. **变长与嵌套类型惩罚**：字符串列每次按行取值都要 offsets→chars 间接寻址，struct/list 列更是要递归下钻子列——列式的收益随嵌套深度衰减；sort 也一样，定宽数值键走多遍 radix（CUB DeviceRadixSort 直排），多列混合键要先做 row-encoding（把整行压成可比对的字节串）再排序，编码本身一遍全表扫描。字符串/嵌套占比过高的负载，先在 CPU 上做类型瘦身再上 GPU。
7. **生态位再强调**：RAPIDS 的正确定位不是"替代 pandas/sklearn"，是两个生态位——**数据已在 GPU**（推理/训练后接特征工程与聚合、RAG 检索）与**数据大到搬一次摊得平**（GB-TB 级 ETL、Spark 换算子）。之外的场景用 CPU 工具不是保守，是正确。

## 六、费曼检验

1. **groupby/join 的 build 侧为什么用 cuco static_set 而不是 dynamic_map？50% 装载率在换什么？** SQL 算子是"build 一次、probe 多次"的静态负载，不需要运行时增删，也就不必付 dynamic_map 分块迁移的复杂度；static 容器 build 时按 extent 一次性分配。装载率 50% 是"内存翻倍"换"期望探测长度 ~1.5 次"——open addressing 的探测成本随装载率非线性上升，GPU 上一次长探测就是一次非合并访存，用空间买带宽是正确交易（`compute_groupby.cu:94` 与 `cuco_helpers.hpp:16` 实证）。
2. **cuml 的 KMeans 在 GPU 上训练，它调用了 libcudf 的什么算子？** 一个都没调。`kmeans_fit.cu:58` 直调 `cuvs::cluster::kmeans::fit`；cuml 的 C++ 依赖清单（`cuml/cpp/CMakeLists.txt:277-289`）里根本没有 cudf。cudf 与 cuml 的公共底盘是 rmm+cuco+raft，libcudf 与 cuvs 是底盘上平行的两个域特化——"RAPIDS 共享 cudf 算子"是把底盘误记成了发动机。
3. **50 MB CSV 做 groupby，pandas 0.8 s，cudf.pandas 能加速吗？** 用 S=aR/(a+R) 推：t_cpu=0.8s/50MB=16 ns/B，a=16e-9×50e9=800，理论上 S≈R（搬运只要 1 ms）；但 0.8 s 的 CPU 活里含大量 Python 对象开销，算子 launch 与代理层开销在毫秒级同台竞争，实测收益常常 <2×。正确判断：这单不值得迁，除非它在循环里跑一万次（此时该考虑常驻 GPU）。

**一句话总结**：数据线的全部戏码，是把"每字节个位数 flop"的带宽型负载放进 7-16 倍带宽差的 HBM——列式内存让 SIMT 合并访存成立，cuco+raft+rmm 是全家共用的底盘（libcudf 与 cuvs 是其上平行域特化，cuml 站在 cuvs 肩上），而调和平均公式 S=aR/(a+R) 把生态位钉死在"数据已在 GPU 或大到搬一次摊得平"，其余一切（零代码代理、spill、Spark 插件）都是把这个边界往外推的工程。

---

## 勘误（任务书前提/deepwiki/常见认知 vs 本仓源码）

1. **"cudf 的 join/groupby/sort 原语被 cuml、cuvs 复用"不成立**：grep 实证 cuml 与 cuvs 的 C++ 层零 libcudf 引用，cuml CMake 依赖是 cccl/rmm/raft/cuvs/treelite（`cuml/cpp/CMakeLists.txt:277-289`）；真实复用方向是 **cuml→cuvs**（`kmeans_fit.cu:58`、`tsne.cu:12`）。"一个算子底盘+多个上层域"应修正为"一个内存/容器/原语底盘（rmm+cuco+raft）+两个平行域特化（libcudf 关系算子、cuvs ANN）+多个 API 门面"。
2. **"线性规划内点法=稠密线性代数"不准确**（任务书原话）：cuopt 的 barrier 用 **cuDSS 稀疏 Cholesky**（`barrier.cu:919` `sparse_cholesky_cudss_t`，KKT 以 CSR 构建），稀疏三角分解才是其访存 bound 的实质；稠密内点法是教科书小规模形态。
3. **"Arrow 零拷贝互操作"不能无条件表述**：`interop.hpp:508` 明示 "without performing copies if possible"，:551-560 列三类强制拷贝例外——BOOL8（位图 vs 字节）、DECIMAL32/64→decimal128、STRING 空 offset 子数组。
4. **deepwiki cuvs 页引 `hnsw_heuristic_type` 位于 cagra.hpp:145-156**：本仓（697e449）实际 enum 定义在 `:266`、默认值在 `:439`、`serialize_to_hnswlib` 在 `:3037`——deepwiki 行号对不上本仓版本，本篇锚全按本仓重核。
5. **"cuML 与 cuDF 同属 RAPIDS 所以共享代码"**：共享的是依赖（rmm/cuco/raft/cuvs）不是 libcudf 算子；两者唯一交点在 Python 层（cuml 吃 cudf.DataFrame 输入）。

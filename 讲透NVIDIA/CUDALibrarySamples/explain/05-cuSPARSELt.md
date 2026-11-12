# 05 cuSPARSELt：2:4 结构化稀疏的静态/动态双目标示例

## 角色定位

cuSPARSELt 是 cuSPARSE 家族里瞄准"2:4 结构化稀疏张量核"（Ampere 起硬件级稀疏加速）的专用库，示例只有两个但密度极高：`matmul/matmul_example.cpp`（378 行）讲基础流程，`matmul_advanced/matmul_advanced_example.cpp`（499 行）讲批处理/ReLU/bias/SplitK 高级特性（图谱 t06）。入口 SM 白名单横跨 8.0/8.6/8.7/8.9/9.0/10.0/10.1/11.0/12.0/12.1 十代架构（matmul_example.cpp:117-:136），不匹配返回专用退出码 `EXIT_UNSUPPORTED=2`（:113）——让上层脚本可区分"失败"与"硬件不支持"。

## 内部结构

两示例共享同一五件套流程：`cusparseLtInit` → 描述符三连（`cusparseLtStructuredDescriptorInit` 给 A 且挂 `CUSPARSELT_SPARSITY_50_PERCENT`（matmul_example.cpp:214-:218，即 2:4 稀疏度枚举）、B/C 用 `cusparseLtDenseDescriptorInit` :220-:227）→ `MatmulDescriptorInit`（:230，C 与 D 同描述符，原地输出）→ `MatmulAlgSelectionInit`+`MatmulPlanInit`（:235-:239）→ 剪枝与压缩。剪枝是理解本库的钥匙：`cusparseLtSpMMAPrune` 就地把稠密 A 剪成 2:4 合法形态（:249），`SpMMAPruneCheck` 校验合法性（:251-:261，非法则库不保证结果正确——示例直接退出）；随后 `SpMMACompressedSize`（:266）+ `SpMMACompress`（:273）把剪枝后的 A 压成 kernel 专吃的数据布局，此后所有 matmul 调用喂的都是 dA_compressed 而非 dA。

advanced 版在此骨架上叠四组特性，全部经 `cusparseLtMatmulDescSetAttribute`/`MatDescSetAttribute` 注入：批处理三 stride（`batch_strideA = m*k+128` 的 +128 是对齐 padding，matmul_advanced_example.cpp:171-:177；描述符逐矩阵设 num_batches :277-:283；stride 设 0 即广播，:286 注释）；ReLU 激活三属性（ACTIVATION_RELU/UPPERBOUND=15.0/THRESHOLD=1.0，:314-:329）；bias 指针（:331-:341，bias 类型按数值路线编译期决定——INT8 路线 bias 用 float，:48-:53）；SplitK 经 `AlgGetAttribute` 只读查询三件（SPLIT_K/SPLIT_K_MODE/SPLIT_K_BUFFERS，:351-:370，模式枚举 ONE_KERNEL/TWO_KERNELS 打印对比）。

## 外部连接

构建层是本域最有辨识度的设计：`matmul/CMakeLists.txt` 从同一份 .cpp 生成两个目标——`matmul_example` 链动态 `libcusparseLt.so`，`matmul_example_static` 链 `libcusparseLt_static.a` 且额外带 `CMAKE_DL_LIBS`（静态库内部 dlopen 依赖），双目标验证同一 API 面在两种链接形态下等价。类型层：文件头 `AB_TYPE` 宏三路特化（FP8 e4m3/BF16/FP16/INT8 各定义 AB_t/C_t/COMPUTE_t/Bias_t 四元组，:40-:54），配 `cuda_type<>`/`cusparse_compute_type<>` trait 模板（:61-:95）把 C++ 类型映射到 CUDA 枚举。上游链接还有 CUDA::cusparse（头文件依赖）。

## 数据流

执行流核心在 matmul_example.cpp:276-:300：可选 `cusparseLtMatmulSearch` 暴力搜最优 plan（:282-:285，注意它真实执行多次使 dC 累积，:287 必须重灌 dC 再进正式计算——注释专门提醒）；`MatmulGetWorkspace`（:293）→ malloc → `cusparseLtMatmul`（:298-:300，携带 plan/alpha/beta/workspace/多流数组）。验证流完全宿主侧：拷回剪枝后的 hA（:313），三重循环按 row/col-major 与转置组合解析线性下标（`A_std_layout` :315-:316，posA/posC 三元选择 :325-:330）重算参考解，逐元素直接比对（:339-:353）。

## 设计决策

三段式（prune→compress→matmul）把"稀疏化损失"显式交给用户：库不替你决定剪哪些元素，PruneCheck 只做合法性裁判——权值剪枝策略留给训练侧。C=D 同描述符的原地语义省一次分配；搜索与执行分离让 autotune 成本一次性摊销进 plan。advanced 的属性注入全部走同一个 SetAttribute 入口，库面保持窄。

## 新人提示

先跑 matmul 确认硬件在白名单内（退出码 2 不是 bug）；改 advanced 时从 :171 的三个 batch_stride 与 num_batches 入手最快见效。自己带权重时跳过 SpMMAPrune 改为手工构造 2:4 合法矩阵亦可，但务必仍调 PruneCheck。链接静态目标时记得它对 dl 的额外依赖，交叉编译环境先验证 libdl 存在。

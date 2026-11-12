# 04 · FMHA cubin 资产坐标系：181 个二进制源码化文件与两代符号体系

## 角色定位

`plugin/bertQKVToContextPlugin/fused_multihead_attention{,_v2}/` 两目录是仓库最奇特的层：**181 个 .cpp 文件（55 v1 + 126 v2）每个都是一段预编译 GPU 二进制的 C++ 源码化封装**——xxd 风格十六进制数组，单文件从 19KB 到 669KB SASS（v2 int8 384_64 sm90 最大，36080 行），tree-sitter 零提取属预期，图谱 L06 以 181 节点整体收录。它们与 03 篇的 MHARunner 相对：逻辑半边决定「何时发射」，本层提供「发射什么」。坐标解码：文件名 `fused_multihead_attention_v2_fp16_128_64_kernel.sm80.cpp` 四维=**dtype × seqlen(S) × headDim(D) × sm_arch**——128 是序列长度、64 是头宽（meta 表首字段实证：`{DATA_TYPE_FP16, 64, 64, kSM_75,...}`，S 与 D 对应）。

## 内部结构

每个 blob 文件一个唯一符号，180 个以 ELF 魔数 `{0x7f,0x45,0x4c,0x46}` 开头（如 `fused_multihead_attention_v2_fp16_64_64_kernel.sm75.cpp:23`）——纯 cubin；唯一例外 `fused_multihead_attention_fp16_128_64_kernel.sm75.cpp:25` 以 `{0x50,0xed,...}`（BA55ED50）开头，是 v1 遗留的 fatbin 封装。**两代符号体系并存**：旧代 `fused_multihead_attention[_v2]_<dtype>_<S>_<D>_kernel[_sm<arch>]_cubin` 与新代 `cubin_fmha_v1|v2_<dtype>_<S>_<D>_sm<arch>_cu_cubin`；v2 头两代混用（`fused_multihead_attention_v2.h:104-127` 新旧 extern 毗邻，新代如 :118-119/:122 的 `cubin_fmha_v2_{int8,fp16}_512_*_sm75_cu_cubin`），全量 extern 声明 v1 头 45 个（`fused_multihead_attention.h:346-351` 等）、v2 头 126 个，合计 171。**分派表**是本层的灵魂：`FusedMultiHeadAttentionKernelMetaInfoV2`（v2.h:410-422）字段为 mDataType/mS/mD/mSM/mCubin/mCubinSize/mFuncName/mSharedMemBytes/mThreadsPerCTA/mUnrollStep/mInterleaved——同一个 cubin 可注册多行（如 :432-438 的 `..._128_64_kernel_sm75_noloop` 与 `..._sm75` 共用 blob，靠 UnrollStep 32/0 区分），v2 表 248 行（:424 起）、v1 表 50 行。架构门禁用 `#error` 硬断言（v2.h:402-408：九个 ENABLE_SM 宏一个未定义即拒绝编译），SM100/SM120 声明块以条件编译分仓（:209-251/:359-401）。

## 外部连接

向上：v2.h 被 `mhaRunner.cu` 的 `FusedMHARunnerFP16v2::mhaImpl`（:920 起）消费——运行时按 `(DataType,S,SM)` 查表、`cuModuleLoadData` 装载、`cuLaunchKernel` 发射；v1 侧同构。向下：CMake 按架构选择性链接，`fused_multihead_attention/CMakeLists.txt:19` 明言「files are huge, we only want to compile them if used」——`add_plugin_source_if_exists`（:21-28）对 `BERT_QKV_SUPPORTED_SMS`（:29-33，`should_compile_kernel` 在 :30 逐 SM 判定，含 100/120 Blackwell）探测存在才收编，构建期筛架构、运行期驱动按 GPU 选 SASS。横向：generate.py 等生成脚本**上游缺位**——两目录除 blob 外仅有 CMakeLists 与两个头文件，hex 数组如何从 .cu 编译产物生成无迹可查（符号命名两代并存亦无迁移说明），复现管线在 NVIDIA 内部仓。同模式复刻：TensorRT-LLM 的 cutlass fmha 资产、FlashMLA 的预编译 blob 均继承此「二进制即源码」哲学。

## 数据流

发射路径全链：`MHARunner::run`（03 篇）→ 查 `sMhaKernelMetaInfosV2[]`（v2.h:424 起）命中行 → 取 mCubin 指针与 mCubinSize → driver API 装载模块 → `cuLaunchKernel(mFuncName, ..., mSharedMemBytes)`——mInterleaved 标记 INT8 交错布局（对应 03 篇 int8 交错插件线），mThreadsPerCTA 128/256 决定网格形态。**本层独有发现：10 个死 blob**——v1 目录的 `cubin_fmha_v1_{fp16,int8}_*_{sm100,sm120}_cu_cubin`（如 `fused_multihead_attention_fp16_256_64_kernel.sm120.cpp`）以新代命名定义，但 `fused_multihead_attention.h` **从未声明这些 extern、分派表亦无行引用**（全仓 grep 零消费者）：Blackwell 扩容时生成器产出了新命名 blob，v1 头的声明与表未同步更新——资产先行的半成品迁移，白编译约 1.5MB 二进制。

## 设计决策

①**源码化二进制而非资源文件**：hex 数组参与正常编译链接，免运行时文件 IO 与路径部署，git 可 diff（虽然 diff 不可读）；代价是仓库膨胀数 MB 与 review 噪音。②**meta 表驱动而非函数指针直连**：SASS 无 C++ 符号约定，表把二进制世界的 (dtype,S,D,sm) 与 driver API 的 launch 参数缝合，同 blob 多行注册支持 noloop/interleaved 变体零成本复用。③**编译期架构裁剪**：CMake `should_compile_kernel` 按 CMAKE_CUDA_ARCHITECTURES 过滤，只给目标 GPU 付编译时间。④**两代命名不收敛**：新代 `cubin_fmha_*` 出现后旧代未迁移，v2 头甚至两代同表——命名规范让位于增量安全，是大型二进制资产库的现实主义。⑤**头文件 #error 门禁**（v2.h:402-408）把「架构宏未定义」从运行期神秘崩溃提前到编译期。

## 新人提示

估算支持矩阵直接读 meta 表而非 README：v2 覆盖 = sMhaKernelMetaInfosV2 的 (dtype,S,sm) 集合，v1 = 50 行老表；`isValid()` 的探测逻辑（03 篇）就是对着这两张表查键。别用编辑器打开 sm90/sm100 大 blob（36K 行起步），用 `grep -c "0x"` 看规模、`head -30` 看魔数即可判断 cubin/fatbin。排查「为什么我的 (S,headDim) 组合走了 unfused 慢路径」：先查表里有没有该坐标行，再看 `mUnrollStep/mSharedMemBytes` 变体选择；headDim≠64 的变长序列必经 QkvPaddingRunner 补零（03 篇）。最后，若要给新架构加 blob，记得同步头文件 extern 声明与 meta 表——v1 的 10 个死 blob 就是漏了后两步的前车之鉴。

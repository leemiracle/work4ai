# cuDNN BSA forward（blk64）：移植范式的标准解剖——入口、spec、双实现

> 文件：`tirx_kernels/cudnn/bsa/block_sparse_attention_forward_sm100_blk64.py`（入口 124 行）
> 深读对象还包括子包 `_block_sparse_attention_forward_sm100_blk64/`：`spec.py`（613）、`kernel.py`（450）、`source_kernel.py`（1139）、`data.py`（337）、`reference.py`（366）。
> 知识图谱定位：「cuDNN 移植 kernel 层」，上游 = cuDNN Frontend @ 7b5327b3。

## 角色定位

cuDNN Frontend 移植家族的 sparse attention 代表：**block-sparse attention forward**。解决的问题是长上下文里的 topK 稀疏注意力——每个 query tile 只 attends 被选中的若干 64-token KV block（blk64 即 KV block 尺寸），而不是整条序列。它在家族里的兄弟是 blk128 变体、backward、combine，以及 MoE grouped GEMM、GDN/KDA linear attention 等，全部移植自 cuDNN Frontend 的 CuTeDSL 源码。`KERNEL_META` 里的 `reference_requirements` 锁死了上游 git commit（aded9909...）和 CUTLASS DSL 版本（==4.8.0.dev0），正确性测试要跑真 cuDNN 实现逐位对照——这是移植家族与原生家族最醒目的区别。

## kernel 算法

稀疏语义由四个元数据张量定义：`block_index`（CSR 式的稀疏 block id 列表）、`block_sizes`（变长 block 的有效 token 数）、`block_nums`（变 block 计数模式）、`split_offsets`（KV split 切分）。forward 主循环是经典 online softmax：对每个被选 KV block 内每个 token，算 QK 点积（warp 归约）、更新 row_max/row_sum、按新旧 max 重缩放累加 V；末尾归一化写出。当 `kv_splits>1` 时做 flash-decoding 式 split-KV：各 split 写 f32 partial + LSE，由 `combine` kernel 以 `weight = exp2((lse_split − safe_max)·log2e)` 为权重合并（LSE 加权数学上严格等价于完整 softmax 的合并；全 -inf 的空 split 有 `safe_max` 与 `local_last` 双保险）。`use_clc` 打开时 grid 维度塌缩、CTA 变 persistent 由 CLC 动态领活。combine 本身也是个小精品：4 warps、grid=(row_tiles, 2, batch)，一个动态 smem arena 切出 `s_lse`/`s_max_split`/`s_o` 三个视图，`cp.async.cg` 16 字节搬运 partial O，`load_stage`/`compute_stage` 双指针 4 槽环形流水让载入与 `f32x2` 打码乘加重叠，LSE 槽位还做了 XOR swizzle 防 Bank 冲突。

## 代码结构

这个子包是仓库**移植范式的标准形状**，五模块各司其职：入口文件 124 行纯委托（`get_kernel`/`prepare_data`/`run_test`/`run_bench` 全部转发）；`spec.py` 是纯 config 矩阵——35 条 correctness + 23 条 benchmark 配置，维度覆盖 bhsd/bshd 布局、MHA/GQA/MQA 头映射（注释特意说明三种头比覆盖 identity 折叠、2 的幂移位、ratio 3 倒数乘三种下降低路径）、fixed/variable/variable_empty 计数模式、kv_splits 1~8、int64 stride、奇数 seqlen（129/4097/8191 这类"非整齐"形状是刻意压力位）；`data.py` 管数据制备与 `tirx_launch`（把多个 executable 按序绑定到已备数据）；`reference.py` 编译上游参考。最有教学价值的是 **`kernel.py` 与 `source_kernel.py` 的双实现并存**：前者是"数值直译"的标量 bring-up 版（16 warps、逐 token 循环、`_load_bf16`/`_exp2`/`_warp_sum` 手写 PTX 小函数），文件头明说是"同一契约的可读陈述"，且只支持 MHA（GQA 直接 raise NotImplementedError 并指路"warp-specialized producer is the live path"）；后者才是 `get_kernel` 实际返回的生产版——16 warps 划成 softmax（0-7，192 寄存器）、correction（8-11）、mma（12）、epilogue（13）、load（14）、idle/CLC（15）六角色，`K.specialize(chain_dispatch=True)` 链式分派。`get_kernel` 的返回是列表：`[forward]` 或 `[forward, combine]`——split 模式下一个"kernel"其实是两段流水。读 kernel.py 建立语义心智模型，再读 source_kernel.py 看工程化，是本家族的标准学法。

## 性能设计

source_kernel.py 的 SM100 火力全开：`tcgen05.mma.ws`（**warp-specialized MMA**，cta_group::1，tile 形状 M=64×N=256×D=128）+ TMEM 512 列；输入走 TMA 5D——K/V 的 TensorMap 把 (batch, kv_head) 融进最外维，稀疏 block id 直接作坐标（`sparse_id()` 读 CSR 解出 sid，越界 clamp 到 `raw_count-1`），KV 三级 stage 流水，每组 4 个 block 的 K 装载顺序刻意重排（sub 0,2,1,3 的 slot 交换）以适配 MMA 操作数布局；同步协议精确到每个生产者-消费者对：`TMABar`（q_full/kv_full）、`TCGen05Bar`（被 MMA 消费的 q_empty/spo/oacc）、`MBarrier`（softmax 侧 stats/oepi），各带自己的到达计数（如 oacc_empty=128、spo_empty=256），每个 `init` 调用与上游 SharedStorage 前缀逐字对齐。CLC 持久化用 `clusterlaunchcontrol.try_cancel.async...multicast::cluster::all` 原语试探取消未启动的 CTA 把工作偷回来，响应走 16 字节邮箱 `clc_response`。共享内存是一个 217088 字节的一维 arena，`K.smem_pool(base=arena)` 逐字节规划（barrier 区、stats_smem、pair_smem、q_smem 8192×bf16、kv_smem 98304×bf16，exchange/o_smem 两个 16384 元素视图直接别名进 kv_smem 的空闲段），结尾 `assert pool.offset == 217088` 锁死布局——移植时"共享内存布局必须与上游逐字节等价"的极端纪律。

## 与其他家族对比

和 flashinfer 移植相比：同为移植，cuDNN 源是 CuTeDSL 重型 warp-specialized 流水线，移植产物天然继承"多角色+多 barrier 协议"的复杂度；flashinfer 的 decode kernel 则多是标量 CUDA core 风格，移植出来就是单文件直球 PTX。和 msa 相比：两者都是稀疏注意力，但 cuDNN BSA 的稀疏是"每 q_block 一个 KV block 列表"，MSA 是"每 KV block 一段 query rows"（k2q 方向），且 MSA 无 CLC、用静态 work list。家族内部还有 blk64/blk128 兄弟与 backward/combine 成对出现的规律——前向子包读通了，backward 子包就是同一套 arena/协议骨架换算梯度语义。对比 msa 家族还能看到一个有趣镜像：BSA 的 split partial 由自家 `combine` kernel（本子包内）收尾，MSA 的 split slot 由独立注册的 `sparse_atten_fwd_combine` 收尾——"forward+combine"这对组合在两个家族里各自演化出同构不同工的实现，对读能看出 flash-decoding 合并范式的两种工程表达。另外本家族的 combine kernel 展示了 `cp.async` 手写多 stage 流水 + `f32x2` 打包乘加的 epilogue 范式，在别处不常见。

## 新人提示

学移植先学这个子包的**目录纪律**：入口薄、spec 纯数据、双实现并存、reference 锁 commit——照这个形状给新上游建目录不会错。bench 协议也有可学之处：`run_gpu` 默认只计时 tirx，`--with-references` 打开后才编译运行 cuDNN 参考并在计时前做一次中途校验（`validate_outputs(..., with_oracle=False)`），参考计时与自家计时互不污染。读代码顺序：`kernel.py` 的 `forward` 从 grid 解码读到输出写回（约 120 行主线）→ `spec.py` 挑三个 config 对着读（fixed vs variable、s1 vs s2）→ `source_kernel.py` 从 380 行的 smem arena 规划往下读角色体。注意入口 `run_test` 的验证链是 `tirx_launch` 与 `source_launch` 双跑后 `validate_outputs(sources=("tirx","source"))`——所有移植 kernel 的正确性信仰都建立在这条链上。

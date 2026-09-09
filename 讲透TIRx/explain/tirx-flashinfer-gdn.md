# gdn_decode_bf16_wide_vec_mtp：FlashInfer 移植家族的 decode 主力与 MTP 语义

> 文件：`tirx_kernels/flashinfer/gdn_decode/gdn_decode_bf16_wide_vec_mtp.py`（1473 行，注册名同名）
> 知识图谱定位：「FlashInfer 移植 kernel 层」，上游 = FlashInfer @ f2e04400（`gdn_kernels/gdn_decode_bf16_state.py`）。

## 角色定位

FlashInfer 移植家族中 `flashinfer.gdn_decode` 入口的四兄弟之一（ilp4 / wide_vec_t1 / **wide_vec_mtp** / fp32_mtp_warp），也是最能代表该家族气质的一个：**GDN（Gated DeltaNet）线性注意力的 decode kernel，MTP（Multi-Token Prediction）变体**。它服务的模型是 Qwen3-Next 一类的混合线性注意力架构——config 校验里 `_HEAD_CONFIGS = ((16,32),(8,16),(4,8),(2,4))` 明写"Qwen3-Next TP head pair"。解决的计算问题：decode 阶段每个请求要推进 2~8 个 token（投机解码一次验收多步），对每步做门控状态递推并产出输出。同层兄弟还有 RMSNorm/topk/量化等 decode 服务小算子，构成 MLC 生态的推理主力层。

## kernel 算法

GDN 的核心是一个 V×K 的外积状态矩阵 `h` 的递推（代码里全程驻留寄存器 `r_h`）：

- 衰减门 `g = exp(−A · softplus(dt_bias + a))`（softplus 用 `ex2/lg2` PTX 近似，x>20 时线性分支防溢出）；
- 写入门 `β = sigmoid(b_gate)`；
- 读取：`sums = kᵀ(g ⊙ h)`（本文件先衰减再读，注意与某些实现的顺序差异）；
- 校正写入：`h ← g ⊙ h + k ⊗ [β·(v − sums)]`；
- 输出：`o = qᵀ h`（更新后的状态）。

可选 q/k L2 归一化（`rsqrt(Σk²+ε)`，warp 蝶形归约）。**MTP 语义是本文件的灵魂**：token 循环被拆成 phase_a（recovery 段，只推进状态不出输出——为验收失败的草稿 token 重算状态）与 phase_b（输出段），`accepted_steps` 每请求指定验收数；配套 `cache_intermediate_states`（把每步中间态写进 intermediate 池供后续验证）、`per_token_pool_scatter`（按 `ssm_state_indices` 逐 token 散写状态，另有 padded/flat 两种池布局）、`read_indices/write_indices` 双状态池间接寻址（负索引 clamp 到 0 的容错，`same_pool=False` 时读写分池）。状态池的 slot 由 int64 `state_slot_stride` 寻址，`_pool_factor` 把这些开关折算成池容量倍率（scatter +seq_len、分池 +1、负索引再 +1），harness 的 `_allocate_pool` 在 padded 模式下还多分配一个 head 的物理空间但只暴露前 num_v_heads 个——用真实越界友好的底层数组测边界。这些开关在 correctness 矩阵里被系统性穷举（38 条 config 覆盖每种组合的边界），是"配置空间即测试空间"的典范。

## 代码结构

单文件自包含，和 basic 家族一样单兵作战，但 harness 部分显著更厚：`_require_supported_config` 校验参数域（seq_len∈[2,8]、tile_v∈{32,64,128}、recovery 与 cache/scatter 互斥、scatter 要求 update 且禁 cache 等，把 MTP 各开关的合法组合写成显式契约）；`get_kernel` 是**派生工厂**——从 config 算出 ROWS_PER_GROUP、ITERS_PER_GROUP、`SHARED_BYTES=1096*seq_len+256`、smem 内 `S_K_BYTE_OFFSET` 等三十多个常量全部烘焙进 `_make_gdn_decode_bf16_wide_vec_mtp` 的闭包。device 主体约 590 行：CTA 坐标解出 (n, hv, v_tile, h)，注意 grid 是 `lambda p: p["batch"]*NUM_V_HEADS*NUM_V_TILES` 的**动态 grid**（从 launch 参数算，而非 trace 时定死）；128 线程按 **8 groups × 16 lanes** 切 K=128（每 lane 拥 8 列，`ELEMS_PER_LANE=8`），V 维按 `v_tile*TILE_V + group*ROWS_PER_GROUP + iter*ILP_ROWS` 切 ILP_ROWS=4 行一组。q/k 先经一个"每 warp 一个 token"的预处理 pass 存进 smem（s_q/s_k 布局带 K+8 padding），门控标量 g/β 算好后成对写进 `s_gb`，主循环两段 `TK.serial` 分别走 phase_a/phase_b。MTP 相位边界是条件组合最多的地方：phase_a_bound/phase_b_begin/phase_b_bound 三个 int32 局部量按 accepted_steps 与各开关分三档赋值——建议读到这里画真值表。

## 性能设计

与 cuDNN 家族的重型流水线**完全相反的哲学**：纯 CUDA core、零 tensor core、零 TMA、零 mbarrier，靠**宽向量访存 + 指令级打包**吃满 decode 的内存带宽。三个看家本领：① `_load_state_bf16x32`/`_store_state_f32x32` 用 `ld.global.L1::evict_first.v4.b32` 一次搬 16 字节（8 个 bf16），bf16→f32 用移位拼位（`shift_left 16` / `and 0xFFFF0000` 把同一 word 拆成两个 f32），状态流载标记 evict-first 因为 decode 状态只读一次；② `_packed_fma` 发 `fma.rn.f32x2`——两个 f32 装进 64-bit 寄存器对一条指令算两路，主循环所有乘加尽量成对（连 `mov.b64` 的打包/拆包都被注释点名为"一条指令两个有序结果，不是两次标量运算"）；③ `_shfl_bfly_f32` 蝶形 `shfl.sync.bfly.b32` 做 warp 内 16-lane 部分和归约，DPS 风格（目标操作数钉住调用点）让 shuffle 只发射一次而不是在每个使用处重发。自适应 `tile_v`：work units（batch×num_v_heads）≥1024 用 128、≥512 用 64、≥128 用 32，小负载缩 CTA 数保 occupancy；TILE_V==32 时额外把状态预取提到元数据加载之前。smem q/k staging 与 `st.shared.b32` 逐元素写、`ld.shared.b32` 读回，换取跨 token 复用。

## 与其他家族对比

同家族四兄弟是这个 kernel 的天然消融实验：`ilp4` 是窄向量基线，`wide_vec_t1` 单 token、`fp32_mtp_warp` 换状态精度（fp32 状态+warp 划分），本文件是"宽向量+MTP"的合体形态——横向对比四个文件能精确看出每项技术的贡献。与 cuDNN BSA 对比则像两个世界：那边 16 warps 六角色 + 十余条 barrier 协议贴 CuTeDSL 源；这边 4 warps 单角色、唯一同步是 `cta_sync`，因为 FlashInfer 上游本身就是朴素的 CUTLASS 标量 kernel，移植忠实保留了"小核快迭代"的 decode 风格。与 basic 家族比：同是单文件，但 basic 有 `K.specialize` 角色划分与逐形状调优表，这里所有形状适应都折进 config 派生常量，warm body 里几乎看不到分支。

## 新人提示

这是学**"上游 Python API → TIRx 特化"映射**的最佳教材：上游 flashinfer 的函数签名参数（head 配置、tile_v、MTP 开关）如何一一变成 trace 常量、派生公式写在哪、校验边界在哪。读法：先读 config 区（`_production_case`/`_correctness_case`，78 条 bench 配置按 `_select_tile_v` 的 work-unit 阈值自动筛）建立参数空间地图 → `get_kernel` 看派生逻辑 → 主体从 CTA 坐标解码读到 phase_a 主循环（`_packed_fma` 密集区）→ 最后啃 phase_b 与 scatter/cache 的条件组合。harness 侧还有两个可偷师的细节：`_compile_tirx_for_config` 以 config 元组为键做编译缓存，避免同 config 重复走 `tvm.compile`；`_run_reference` 直接 import flashinfer 上游生成期望输出，`_assert_case_close` 分 dtype 定容差。想懂 MTP 推理服务的状态管理（draft/verify/recovery），这个文件就是活文档。

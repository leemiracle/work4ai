# csrc/smxx/decode/combine/combine.cu 精讲

> 原文件：`csrc/smxx/decode/combine/combine.cu`（230 行）

## ① 角色定位

**splitKV 归并器**——解码三段流水（scheduler → 主解码内核 → combine）的收官。主内核把每序列 KV 切成至多 `num_sm_parts` 份，各 split 独立算出**未归一化的 fp32 部分和** `o_accum` 与局部 `lse_accum`；本内核按全局 softmax 权重加权合成最终 bf16 输出与全局 lse，并可选融合 attention sink。

## ② 内部结构

模板内核 `flash_fwd_mla_combine_kernel<ElementT, HEAD_DIM_V=512, BLOCK_SIZE_M=8, MAX_SPLITS, NUM_THREADS=256>`：grid `(b*s_q, 1, ceil(h_q/8))`，**一个 warp 负责一个 (序列位置, 头)**（静态断言 `NUM_THREADS/32 == BLOCK_SIZE_M`，warp_idx 即头偏移）。宿主侧用 `MLA_NUM_SPLITS_SWITCH` 宏阶梯（32/64/…/256）按 `num_sm_parts` 选编译期 MAX_SPLITS，再以 **`cudaLaunchKernelEx` + `cudaLaunchAttributeProgrammaticStreamSerialization`** 启用 PDL（207-219 行）。显式实例化 bf16；fp16 受 `FLASH_MLA_DISABLE_FP16` 门控。

## ③ 外部连接

输入来自 api 层分配的 `lse_accum/o_accum` 与 `params.h` 的 `CombineParams`（两层张量指针+步长、`num_splits_ptr`、可选 `attn_sink`）。消费 scheduler 产出的 num_splits 前缀和（36-37 行）。cute/cutlass 仅用于构造全局内存视图与展开宏。

## ④ 数据流

① 越界 warp 早退；② `my_num_splits == 1` 直接 return——**单 split 序列由主内核直写终值，combine 空转**；③ `cudaGridDependencySynchronize()`（59 行）等主内核完成（PDL 语义）；④ 预取 `ELEMS_PER_THREAD = 512/(32*4) = 4` 个 float4 入寄存器（不用 `__ldg`，与 PDL 不兼容）；⑤ LSE 归并（72-119 行）：每 lane 取若干 split 的局部 lse，warp 求 `max_lse`（全 -inf 钳 0），`sum = Σ exp2(local-max)`，`global_lse = log2(sum)+max`；lane 0 写 `gLse = global_lse / M_LOG2E` 换回自然底；⑥ attn_sink 融合：`global_lse += log2(1+exp2(attn_sink*L2E - global_lse))`；每 split 缩放系数 `exp2(local-global)` 存 smem；⑦ 加权累加：`result += scale * datas`，同循环**预取下一 split 的 float4**（软件流水）；⑧ 转 ElementT 后两个 bf16 打包 8 字节单条 store。

## ⑤ 设计决策

- **exp2/log2 域运算**：rescale 在 2 的幂底上做，`exp2f/log2f` 快于 `expf/logf`；仅最终写出时换回自然底；先减全局 max 再 exp 防溢出。
- **PDL**：combine 依赖主内核全量完成，传统流序会强制排空；PDL 让启动/预取与主内核尾巴重叠，代价是禁用 `__ldg`。
- **MAX_SPLITS 编译期阶梯**：smem `8*(MAX_SPLITS+1)*4` 字节随 split 数增长，8 档实例化避免为 256 split 常态付大 smem，宿主按实需选档。
- **边界语义**：`sum==0 || -inf` 时 `global_lse=INFINITY`（98 行）——无 token 可注意的序列输出全零，配合 attn_sink 分支保证边界正确。

## ⑥ 新人提示

1. 主内核写的 `o_accum` 是**未除以 Σexp 的加权和**——combine 做的是 flash attention 在线 softmax 的跨 split 版。
2. 调 NaN 优先查 `lse_accum` 是否含 ±inf，再看 attn_sink 分支注释（106-112 行），那里浓缩了所有边界情形。
3. `MLA_NUM_SPLITS_SWITCH` 的 `FLASH_ASSERT(false)` 意味着 num_sm_parts>256 直接崩；改 `BLOCK_SIZE_M` 须同步 23 行断言与 204 行 smem 公式。

# B · 通信与算子内核：DeepEP / DeepGEMM / FlashMLA / TileKernels / DualPipe / EPLB / LPLB / profile-data

> 研究型代码考古笔记。对象：`C:\workspace\work4ai\.tools\deepseek-repos\` 下 8 个仓库的本地浅克隆。
> 所有数字均来自实际读到的 README / 源码 / 文档；文件路径均相对各仓库根目录。
> 注意时效性：本次克隆时间约为 2026 年中，DeepEP/DeepGEMM/TileKernels 已演进出 **V2/Mega/新版**形态，
> 与 2025-02 开源周首发版不同。笔记对两代形态分别记录，并明确标注来源文件。

---

## 1. DeepEP —— MoE 专家并行通信库（Day 2）

**定位一句话**：DeepSeek 自研的 MoE all-to-all（dispatch/combine）GPU 通信库，V1 用 NVSHMEM 实现「NVLink 域内转发 + RDMA 域间直发」双通道与纯 RDMA 低延迟路径，V2 重写为 NCCL Gin 后端 + `ElasticBuffer` 统一接口 + 解析式 SM/QP 计算。

### 1.1 V1（NVSHMEM 时代，`docs/legacy.md` + `csrc/kernels/legacy/` + `csrc/legacy/`）

**双通道分层设计**（`csrc/kernels/legacy/compiled.cuh`：`LEGACY_NUM_MAX_NVL_PEERS = 8`）
- 每个 GPU 按 `rank / 8`、`rank % 8` 分解为 rdma_rank 与 nvl_rank（`csrc/legacy/buffer.hpp:120`），即「8 卡 NVLink 域 × N 个 RDMA 节点」。
- 跨节点 token 先经 RDMA 发到目标节点上的某个 NVLink 对端 buffer，再由目标节点内 8 卡经 NVLink 分发——即 normal kernel 的「NVLink+RDMA 转发」模型（`internode.cu` 中 `WarpRole::kRDMAAndNVLForwarder / kForwarderCoordinator / kNVLReceivers` 三类 warp，`__launch_bounds__((kNumDispatchRDMASenderWarps + 1 + 8) * 32)`）。

**性能数字**（`docs/legacy.md`，H800：NVLink ~160 GB/s 上限，CX7 400 Gb/s RDMA ~50 GB/s 上限）
- normal 内核（V3/R1 预训练设定：4096 token/batch，hidden 7168，top-4 group × top-8 expert，FP8 dispatch + BF16 combine）：
  - EP8 单机：dispatch 153 GB/s / combine 158 GB/s（NVLink 打满 ~97%）
  - EP16：43/43 GB/s；EP32：58/57；EP64：51/50 GB/s（RDMA）
- low-latency 纯 RDMA 内核（生产解码设定：128 token/batch）：dispatch 延迟 77 µs(EP8)→192 µs(EP256)，带宽 98→39 GB/s；combine 延迟 114 µs(EP8)→369 µs(EP256)。

**buffer 尺寸公式**（`csrc/legacy/config.hpp`）
- normal NVLink buffer ≈ `num_channels(=num_sms/2) × num_nvl_ranks × [chunked_recv_tokens × (hidden_bytes + source_meta + topk idx/weights + scales)]`，其中 kNumMaxTopK=128、kNumMaxScales=128 均为硬编码假设。
- RDMA buffer 同构但 ×2（奇偶双 buffer 流水）。
- 官方推荐配置表（`deep_ep/buffers/legacy.py:245-288`）：如 dispatch EP64 = Config(num_sms, nvl_send 32, nvl_recv 288, rdma_send 8, rdma_recv 128)；combine EP64 = (num_sms, 1, 288, 8, 128)。约束 `rdma_send ≤ rdma_recv/2`（lazy head 更新防死锁，`config.hpp:50`）。

**low-latency 纯 RDMA 路径**（`csrc/legacy/config.hpp: LowLatencyLayout` + `csrc/kernels/legacy/internode_ll.cu`）
- 布局：奇偶对称的 send/recv/信号量三组 buffer；`num_bytes_per_dispatch_msg = sizeof(int4) + max(hidden×2, hidden + num_scales×4)`（FP8 时 hidden 字节数 + per-128 通道 scale），`num_bytes_per_combine_msg = num_scales×sizeof(bf162) + hidden×2`（combine 消息内嵌 per-128 min/max 元数据）。
- 接收 buffer 大小 = `num_experts × num_max_dispatch_tokens_per_rank × msg_bytes`；要求 `num_qps_per_rank == num_local_experts`（QP 数必须等于本卡专家数，`legacy.py:255-256`，默认 24，`NVSHMEM_IBGDA_NUM_RC_PER_PE` 控制）。
- 官方建议 `num_max_dispatch_tokens_per_rank ≤ 256`（低延迟模式吃显存远大于 normal 模式）。
- dispatch 内核（`internode_ll.cu:129`，1024 线程单 block 多 SM）：warp 内做 **per-128 通道 FP8 cast**（`warp_reduce_max<16>` 求 amax → `calculate_fp8_scales` → `__nv_cvt_float2_to_fp8x2`），然后 `nvshmemi_ibgda_put_nbi_warp` 直接 IBGDA 发送（同 NVLink 域则 `nvshmemi_get_p2p_ptr` 走 `st_na_global` 直写对端显存）；目标地址 = `expert_local_idx × num_ranks × max_tokens × msg + rank × max_tokens × msg + slot_idx`（预分配槽位、零协商）。slot 由 `atomicAdd(atomic_counter_per_expert)` 分配。
- **hook 机制（send/recv 重叠）**：`phases` 参数拆分 `LEGACY_LOW_LATENCY_SEND_PHASE=1 / RECV_PHASE=2`（`compiled.cuh:11-12`）；`return_recv_hook=True` 时内核只发 RDMA 请求就返回，把「等接收 + 从 recv buffer 解包到输出 tensor」封装成 `recv_hook = [=](){ launcher(RECV_PHASE); }`（`csrc/legacy/buffer.hpp:1577-1592`）。这就是 V3/R1 解码「RDMA 发出后 0 SM 占用」的实现。
- 容错：barrier 带 `clock64()` 超时 + `mask_buffer` 屏蔽慢 rank（`internode_ll.cu:41-68`，`LEGACY_NUM_TIMEOUT_CYCLES`）。
- 10-bit LogFMT 压缩：`kNumBits = 10`（`internode_ll.cu:561`），低精度传输压缩编码。
- **UB PTX 技巧**（`docs/legacy.md` Notices）：用 `ld.global.nc.L1::no_allocate.L2::256B` 读 volatile 数据——`.nc` 本不许读易变数据，但 Hopper 上 L1 与 non-coherent cache 合一、`no_allocate` 是强语义，实测正确且更快；可 `DISABLE_AGGRESSIVE_PTX_INSTRS=1` 关闭。

### 1.2 V2（NCCL Gin 后端，主 README + `csrc/elastic/` + `deep_ep/buffers/elastic.py`）

- 统一 `ElasticBuffer` 接口覆盖高吞吐/低延迟/Engram/PP/AGRS；buffer 尺寸按 MoE 参数解析计算并 **2 MB 对齐**（`get_buffer_size_hint` → `_C.calculate_elastic_buffer_size`）；支持最大 **EP2048**。
- **解析式 SM 计算**（`elastic.py:729-834 get_theoretical_num_sms`）：带宽模型 `sm_read_gbs=200, sm_write_gbs=50`（每 SM HBM 读写带宽假设），按期望 top-k 跨域命中数（`get_expected_topk` 组合数学）推 sm_read/sm_write/rdma/nvlink 流量，取受限链路 → `num_sms = max(4, ceil(理论值×1.25))` 且偶数对齐；与计算重叠时取小值，不重叠时 `max(num_sms, 64)`。**V3 类训练 SM 从 24 降到 4-6，性能持平或更好**（README）。
- **解析式 QP 计算**（`elastic.py:836-853`）：direct 模式 `min(num_sms, 8)+1`（少 QP 省 doorbell）；hybrid 模式每 channel 独立 QP `num_sms×16+1`。
- dispatch 内核 warp 组织（`csrc/kernels/elastic/dispatch.hpp:130-196`）：4 个 notify warp（cached_mode 时为 0）+ 单机时 dispatch warp（按 smem 塞满 ≤32）或混合模式 scaleout warp + forward warp（每 SM 每 channel 各一）。
- 性能（V3 设定 8K token、hidden 7168、top-8、FP8 dispatch/BF16 combine）：SM90 EP8×2 CX7：90/81 GB/s @12 SM；SM100 NVLink EP8：726/740 GB/s @64 SM（max perf）、643/675 GB/s @24 SM（min SM）。**较 V1 峰值性能至多 1.3×，SM 数省至多 4×**。
- 新增 0-SM 原语：Engram（RDMA 远程 KV/记忆取回）、PP send/recv（NVLink/RDMA）、CP（Copy Engine）、AG/RS（开发中）；`Elastic GPU+CPU 弹性 buffer` 在路线图。
- 环境/网络工程：IB 虚拟车道隔离（`sl_idx` 或 `EP_OVERRIDE_RDMA_SL`）、自适应路由全场景建议开启、拥塞控制禁用（伤带宽）、`PCI_ATOMIC_MODE=4` 提升 RDMA 原子性能（README Network configurations）。
- JIT：全内核运行时编译，缓存 `$HOME/.deep_ep`（`EP_JIT_CACHE_DIR`），nvcc C++20，可 dump PTX/SASS、ptxas 检查无 local memory（`EP_JIT_PTXAS_CHECK`）。
- 社区分支生态：Tencent 零拷贝 PR#453、AntGroup Normal-SMFree/LL-SBO/LL-Layered、hybrid-ep（TMA/NVFP4）、MORI（AMD ROCm）、nvDev（CFT）、uccl（异构 GPU/NIC）。

### 1.3 工程亮点
- 编译：`setup.py`（torch cpp_extension）+ CMake 仅编宿主端；CUDA 全 JIT（V1 部分内核 AOT）。
- 测试：`tests/elastic/test_ep.py / test_agrs.py / test_engram.py / test_pp.py`，`tests/legacy/test_intranode.py / test_internode.py / test_low_latency.py`（含 `return_recv_hook` 双态对比与 kineto 计时）。
- CI：`.github/workflows/{format,build,publish}.yml`。
- 对称 buffer 通过 NVSHMEM/NCCL window + IPC handle 分发（`buffer.hpp` 中 `buffer_ptrs[8]`、`cudaMemcpy` 灌 `buffer_ptrs_gpu`）。

### 1.4 与其他仓库的关系
- dispatch 的 per-128 通道 FP8 输出格式与 DeepGEMM `m_grouped_fp8_gemm_*_contiguous/masked` 的 SF 布局配套（README 互引）；LPLB 用 DeepEP buffer 内部通信子收集负载统计（`init_from_deep_ep`）；profile-data 的 decode 说明了其 0-SM hook 用法。

### 1.5 对 work4ai 的输入
- 讲透GPU与系统级：UB PTX 案例、IBGDA/GIN 用户态 RDMA、QP/doorbell、barrier+超时掩蔽、L1/L2 cache 语义。
- 讲透分布式AI系统：EP all-toall 的分层域模型（NVLink 域/RS 域）、SM 预算的解析式建模、0-SM 通信原语、双微批重叠解码。
- 讲透KV Cache：Engram 远程取回（0 SM RDMA）。
- 工程化手册库：JIT 编译器架构（include_parser/cache/compiler）、环境变量清单、网络调优清单（VL/AR/CC/PCI atomic）。

---

## 2. DeepGEMM —— FP8/FP4/BF16 GEMM 与融合 MoE 内核库（Day 3）

**定位一句话**：为 V3/R1 训练推理提供「clean as a tutorial」的张量核内核库：SM90 FP8 1D2D/1D1D GEMM + 分组 MoE 布局 + V3.2 索引器 MQA + Mega MoE 融合内核，全部 JIT。

### 2.1 核心机制

**per-128 缩放两级量化（1D2D 内核，SM90）**（`deep_gemm/include/deep_gemm/impls/sm90_fp8_gemm_1d2d.cuh`）
- `DG_STATIC_ASSERT(BLOCK_K == 128, "Only support per-128-channel FP8 scaling")`（:58）：K 块固定 128。
- SFA（激活）TMA 加载、按行；SFB（权重）按 128 列粒度，`kMustUseUniformedScaleB = (BLOCK_K % BLOCK_N == 0)` 决定每块 1 或 2 个 SFB。
- **WGMMA 累加 + CUDA core 逐 128 块提升**：tensor core 先算裸 FP8 累加 `accum`，每完成一个 K 块，CUDA core 做 `final_accum += (scale_a × scale_b) × accum`（:331-347，predicate 化避免双循环）——这就是 DeepSeek「细粒度量化、粗粒度累加」精度策略的内核形态。
- 输出仅 BF16 无累加（:64）；TMA store 用 STSM 写 swizzle shared memory。

**SM90 启发式（解析式 cost model，非自动调优）**（`csrc/jit_kernels/heuristics/sm90.hpp`）
- block_m 候选 {64,128}（≤16/32 加 16/32；BF16 输出加 256）；M 分组连续布局的 block_m 直接 = M 对齐值；block_n 枚举到 192(1D2D)/160(1D1D)；block_k = 128/元素大小。
- 约束：cluster ≤2、swizzle ≥64B、stages ≥3（小块 ≥4，隐藏 TMA 延迟）、smem_capacity=232448。
- **性能模型**（`get_layout_info`：L1 128 B/cycle/SM、L2 `min(64×num_sms, ~6154)` B/cycle，只建模 L1/L2 cycle + wave 效率，HBM/TC 视为常量）选最优布局。
- launch：128 TMA 线程 + 128/256 计算线程（block_m≤64 用 128）。

**SM100 路径**（`sm100_fp8_fp4_gemm_1d1d.cuh` / `heuristics/sm100.hpp`）
- SF 为 **UE8M0 packed**（4 个打包进 1 个 `torch.int`，README；块 M/N 对齐 `num_utccp_aligned_elems=128`）；tcgen05 UMMA `make_instr_desc_block_scaled` + UTCCP 搬 SF 进 tensor memory + `make_runtime_instr_desc_with_sf_id` 动态选 SF id（:285-389）。
- 支持全部 NT/TN/NN/TT 布局（SM90 仅 NT）；tmem 多级 epilogue 流水。

**分组 MoE 三布局**（README + `deep_gemm/__init__.py`）
- `m_grouped_*_contiguous`：仅分组 M 轴（N/K 固定），专家段拼接 + `get_mk_alignment_for_contiguous_layout()` 对齐——训练/预填充。
- `m_grouped_*_masked`：给 mask tensor，配 DeepEP 低延迟内核输出 + CUDA graph 解码（CPU 不知道每专家 token 数）。
- `k_grouped_*_contiguous`：分组 K 轴，M/N 固定——MoE **权重反向**（2025.05.14 PR#95 新增 dense/MoE 权重梯度内核）。

**V3.2 闪电索引器 MQA 内核**（README §V3.2 MQA kernels）
- `fp8_mqa_logits`：`out[i,j] = Σ_heads relu(q_i·kv_j×sf)×weights_i`，E4M3 输入 + 每 token 浮点 SF，输出 `[seq_len, seq_len_kv]` token-token logits；分页版 `fp8_paged_mqa_logits`。
- 另有 `tf32_hc_prenorm_gemm`（HyperConnection 预归一化 GEMM）、einsum、FP8×FP4、`smxx_cublaslt` 回退。

**Mega MoE（2026.04 PR#304/#316）**
- 把 EP dispatch + Linear1(FP8×FP4) + SwiGLU + Linear2(FP8×FP4) + EP combine 融成**单个 mega-kernel**，NVLink 通信与张量核计算重叠（`sm100_fp8_fp4_mega_moe.cuh`：TMA 传 `smem_sfa/smem_sfb`，`BlockPhase::Linear1/Linear2` 任务态调度，`scheduler/mega_moe.cuh`）。
- 对称内存：`get_symm_buffer_for_mega_moe(...)`（需 PyTorch ≥2.9 对称内存 API），权重 `transform_weights_for_mega_moe` 预变换布局。

### 2.2 性能与工程
- README News：2025.04.18 达 **1550 TFLOPS（H800）**；开源周时宣传 1350+ TFLOPS、核心逻辑 ~300 行（open-infra-index Day 3）。
- JIT：`csrc/jit/cache.hpp` 进程内 `unordered_map<path, KernelRuntime>` + 磁盘缓存 `~/.deep_gemm`；NVRTC 可选（`DG_JIT_USE_NVRTC=1`，编译加速至 10×，部分 case 性能略降，2025.07 后默认关闭 NVRTC/SASS 后处理，NVCC 12.9 自动做 FFMA interleave）。
- 测试：`tests/test_core.py` 类缺失（当前为 test_fp8_fp4/test_bf16/test_attention/test_mega_moe/test_layout/test_einsum/test_hyperconnection/test_legacy/test_sanitizer）；`deep_gemm/testing/bench.py` + `scripts/quick_plot_pm.py`（性能模型对比绘图）。
- 全局工具：`set_num_sms/set_tc_util/set_pdl/set_mk_alignment/transform_sf_into_required_layout/get_mn_major_tma_aligned_packed_ue8m0_tensor` 等（README Utilities）。

### 2.3 关系与 work4ai 输入
- 与 DeepEP：masked 布局直接吃 DeepEP 低延迟输出（README 明说）；Mega MoE 内置 EP 通信。
- 与 FlashMLA：共同覆盖 V3.2「注意力前」的索引器计算。
- work4ai：讲透GPU与系统级（WGMMA/tcgen05、TMA swizzle、SF 布局、寄存器/tmem 预算、JIT 工程）；讲透优化理论（L1/L2 解析 cost model、wave 效率）；讲透模型（V3 FP8 训练量化的实际粒度：激活 per-128、权重 per-128 列、SM100 UE8M0）。

---

## 3. FlashMLA —— MLA 解码与稀疏注意力内核（Day 1）

**定位一句话**：V3/V3.2 的注意力内核库：分页 KV cache 的 MQA 解码（吸收式 MLA，h_q 全 128 头在一卡）+ DSA token 级稀疏 prefill/decode（FP8 KV cache）+ SM100 密集 MHA 前反向。

### 3.1 核心机制与数字
- **维度**：MLA 解码 `head_dim_k=576, head_dim_v=512`（MQA 模式，c_kv 单头）；MHA prefill `d_qk=192/128, d_v=128`（README 支持矩阵注 [2]）。V3/V3.1/V3.2 均 576/512（`flash_mla/flash_mla_interface.py:92-93`）。
- **分页 KV**：`page_block_size=64`（sm90 dense `config.h: BLOCK_SIZE_M=64, PAGE_BLOCK_SIZE=64`；sparse_fp8 `components/config.h: PAGE_BLOCK_SIZE=64, BLOCK_M=64, TOPK_BLOCK_SIZE=64, HEAD_DIM_ROPE=64`）。
- **FP8 KV cache 布局（656 B/token）**（README + interface:94-98）：512 B 量化 NoPE（512×fp8_e4m3）+ 16 B scale（4×fp32，每 128 通道一个）+ 128 B RoPE（64×bf16，不量化保精度）。kernel 读 FP8、反量化成 BF16 计算再输出 BF16。
- **稀疏索引**：`indices[b, s_q, topk]`，值 = `page_block_idx × page_block_size + offset`（页号已编入索引，kernel 不需要 block_table）；无效项 -1；支持 `topk_length` 变长与 `extra_k_cache` 二段 KV（V3.2 DSA 的 2048 额外锚点类机制）。
- **split-KV + combine 两段式**：`smxx/decode/get_decoding_sched_meta` 先跑 tile scheduler 元数据 kernel（`DecodingSchedMeta{begin/end_req_idx, begin/end_block_idx, begin_split_idx, is_first/last_req_splitted}`，`csrc/params.h:10-16`），主 kernel 按 split 写 `o_accum/lse_accum`，`smxx/decode/combine` 合并（`MAX_SPLITS` 检查）。
- **「跷跷板」调度（seesaw）**（`docs/20250422-new-kernel-deep-dive.md`）：
  - 算力/带宽比 ≈ `2·h_q·s_q` → H800（降频后 ~865 TFLOPS / 3.35 TB/s）当 `h_q·s_q ≥ 128` 为计算受限；V3 解码不用 TP、h_q=128 → 计算受限。
  - 64×512 输出矩阵占 32,768 个 32-bit 寄存器/SM（65,536 上限的一半），放不下两份 → FA3 ping-pong 不可行。
  - 解法：每步取两个 KV 块（K0/K1/V0/V1），输出纵向劈成 O_L、O_R（各 64×256），两 warp group 交错执行 11 步数学等价流水（doc 内 0-11 步伪代码），实现单输出矩阵的「乒乓」。
  - 细粒度 TMA 流水：64×576 的 K 块拆 9 个 64×64 TMA copy，到一块算一块；`CacheHintSm90::EVICT_FIRST` 提升 L2 命中。
  - 结果：**80% 张量核利用率（对降频峰值）、3 TB/s 访存、最高 660 TFLOPS**（旧版 580 TFLOPS/3000 GB/s → 新版 +5~15%）。
  - PDL（Programmatic Dependent Launch）重叠 splitkv 主内核与 combine；tile scheduler 均衡 SM 负载。
- **性能表**（README）：dense 解码 H800 3000 GB/s & 660 TFLOPS；稀疏解码（FP8 KV、BF16 计算）H800 410 TFLOPS / B200 350 TFLOPS（未充分优化）；稀疏 prefill H800 640 TFLOPS / B200 1450 TFLOPS；SM100 MHA 前向 1460 TFLOPS / 反向 1000 TFLOPS（B200，NVIDIA PR#76）。
- 接口演进：`get_mla_metadata` 现为惰性占位，首次 `flash_mla_with_kvcache` 才生成调度元数据（`flash_mla_interface.py:37-50`）；同一 sched_meta 跨步复用（CUDA graph 友好）。
- `ModelType::{V32, MODEL1}` 双模板（V3.2 与其它模型头部配置）。

### 3.2 工程亮点
- `setup.py`：CUTLASS submodule 自动 `git submodule update`；arch `90a`/`100f` gencode；sm100 需 NVCC ≥12.9；sm90 sparse 实例化 `*_persistent_h64/h128.cu`（persistent kernel）。
- 测试：`tests/test_flash_mla_{dense_decoding,sparse_decoding,sparse_prefill}.py`、`test_fmha_sm100.py`；`tests/kernelkit/`（bench/compare/generate/precision——内核对拍工具）；`tests/quant.py`（FP8 KV 量化参考实现）、`tests/ref.py`（PyTorch 参考含 exp2/log2 base-2 softmax 语义）。
- 生态：MetaX/沐摩线程/Hygon/寒武纪类（Intellifusion/Deep-Spark/Iluvatar）/AMD AITER 全有移植（README Community Support）。

### 3.3 关系与 work4ai 输入
- V3.2 DSA 稀疏注意力 → 与 DeepGEMM 的 indexer logits 内核上下游相连；解码 h_q=128 前提来自 open-infra-index Day 6（解码实例不用 TP）。
- work4ai：讲透KV Cache（656B 布局、page 64、压缩 latent 的实际显存账）；讲透GPU与系统级（寄存器预算→调度约束的推理链、seesaw、TMA 流水、PDL、persistent kernel）；讲透分布式AI系统（split-KV 调度器与 EP 解码的关系）。

---

## 4. TileKernels —— TileLang 编写的 LLM 算子库（Day 1 系列之外的新仓库）

**定位一句话**：用 TileLang DSL 写的「门控/量化/路由/转置/Engram/MHC」训练级算子库；注意：当前版本（2026）已与开源周首发的 GEMM/attention/block-sparse 版不同，重心移到 Engram 与 Manifold HyperConnection。

### 4.1 当前内核清单（`tile_kernels/` 实测目录）
- `moe/`：`topk_gate_kernel`（top-k 专家选择+打分）、`group_count_kernel`、`get_fused_mapping_kernel`、`inplace_unique_group_indices_kernel`、`expand_to_fused_kernel`/`reduce_fused_kernel`（融合 expand/reduce）、`normalize_weight_kernel`、`top2_sum_gate_kernel`、`topk_sum_and_topk_group_idx_kernel`、`mask_indices_by_tp_kernel`、`aux_fi_kernel`（辅助损失）、`scoring.py`。
- `quant/`：`per_token_cast`（e4m3/e2m1/e5m6）、`per_channel_cast(_fused)(_and_transpose)`、`per_block_cast(_lossless)`、`cast_back(_e5m6)`、`swiglu_forward_and_per_channel_cast_and_transpose`、`swiglu_forward_and_per_token_cast`、`swiglu_backward_and_per_token_cast`（融合 SwiGLU+量化）。
- `transpose/`：`batched_transpose_kernel`。
- `engram/`：`engram_gate_kernel`（融合 RMSNorm）、`engram_hash_kernel`、`engram_fused_weight_kernel`（前/反向）、`engram_grad_w_reduce_kernel`。
- `mhc/`（Manifold HyperConnection）：`sinkhorn_kernel`（Sinkhorn 归一化）、`pre_split_mixes`、`pre_apply_mix`、`head_compute_mix`、`norm_fn`、`multilayer_recompute`、`post`、`expand`、`pre_big_fuse`。
- `modeling/`：`torch.autograd.Function` 组合层（`engram_gate`、mHC pipeline 各 op）。
- `torch/`：纯 PyTorch 参考实现（对拍基准）。

### 4.2 tilelang 写法要点（以 `quant/per_token_cast_kernel.py` 为例）
- `@tilelang.jit(pass_configs={TL_DISABLE_WARP_SPECIALIZED: True, TL_ENABLE_LOWER_LDGSTG_PREDICATED: True})` 包住 `@T.prim_func`；`T.Kernel(grid..., threads=128)`；`T.alloc_fragment/alloc_shared` 显式寄存器/共享内存；`T.annotate_layout + T.Fragment(forward_fn=...)` 自定义寄存器布局（向量化排布 `id // vec % threads`）；`T.copy(..., disable_tma=True)` 强制 LDGSTG 路径；`T.reduce_absmax/reduce_max` 内建归约原语。
- SF 粒度 `num_per_channels ∈ (16, 32, 64, 128)` 或整行（hidden%64==0 时）；支持 `use_tma_aligned_col_major_sf`（对接 DeepGEMM/DeepEP 的列主 SF 布局）、`round_sf`（2 的幂）、`use_packed_ue8m0`（SM100 打包 SF）——**量化约定与 DeepEP V2/DeepGEMM 完全同族**。
- 两段 amax 归约技巧：FP16 先做 stage1 局部 absmax（省带宽）→ 乘输入 SF → FP32 stage2 精确 absmax。
- E5M6：新中间格式（`e5m6`），lossless per-block cast 变体。

### 4.3 工程与生态
- 要求：Python ≥3.10、PyTorch ≥2.10、TileLang ≥0.1.9、SM90/SM100、CUDA ≥13.1（README）。
- 测试：`pytest tests/... -n 4`，`--run-benchmark` 开基准，`TK_FULL_TEST=1 pytest -n 4 --count 2` 压力测试；自带 `pytest_benchmark_plugin.py / pytest_random_plugin.py / conftest.py`。
- 说明：作者 Wang/Xu/Yu/Zhao 等（Citation 2026），部分内核已用于内部训练推理，README 自述「不代表最佳实践，持续改进」。

### 4.4 关系与 work4ai 输入
- 与 DeepEP V2（Engram）、DeepGEMM（HC 内核 `tf32_hc_prenorm_gemm` 同属 HyperConnection 栈）直接配套——TileKernels 是 Engram/mHC 时代的「配套小算子层」。
- work4ai：讲透GPU与系统级（DSL 生成 CUDA 的工程路线：fragment 布局/归约原语/pass 配置）；讲透模型（HyperConnection、Engram 前向的反向传播细节）；工程化手册库（pytest-benchmark 插件化、对拍式测试结构）。

---

## 5. DualPipe —— 双向流水线并行算法（Day 4）

**定位一句话**：V3 报告中的双向 PP 调度：微批次从流水线两端对向注入，使「前向/反向的计算与通信」完全重叠，气泡公式减半。

### 5.1 核心机制（`dualpipe/dualpipe.py`）
- 构造：两个模块 `modules=(m0, m1)` + `rank_mapping`；前半 rank（`is_in_second_half=False`）phase0=正向 phase1=反向，后半对调（`phase ^= self.is_in_second_half`）。首 rank 与末 rank 各持一半 micro-batch 的输入/标签（`step()` 中 scatter 成 `half_num_chunks`）。
- **8 步调度**（`step()` :358-425，逐 rank 计步数）：
  1. `nF0`：预热前向；2. `nF0F1`：双向注入；3. `nB1W1F1`（**ZB 零气泡**：`_backward_chunk(1, enable_zb=True)` + `_weight_chunk()`）；4. 主稳态 `nF0B1F1B0`（`_forward_backward_chunk(0,1)` + `(1,0)` 交错）；5. `nB1F1B0`；6. `nB1B0`（后半启用 ZB）；7. `nWB0`；8. `nW`。
- **重叠的本质**：`_forward_backward_compute_chunk` 在支持时调用模块自定义静态方法 `overlapped_forward_backward(module0, inputs0, criterion0, labels0, module1, loss1, outputs1, output_grads1)`——即**模块自己实现「本 chunk 前向与对向 chunk 反向共用一份 kernel 时间」的融合算子**（V3 里即 MoE 层把 dispatch/combine 通信缝进共享专家前向与反向，见 profile-data）；库不假设能重叠时退化为顺序 F→B。
- 零气泡（ZB1P 风格）：`WeightGradStore` 暂存权重梯度，`_weight_chunk()` 按 FIFO 延迟 flush。
- 约束：`num_ranks % 2 == 0`、`num_chunks` 偶数且 `≥ 2 × num_ranks`（:332-333）。
- 通信：`dist.batch_isend_irecv` 批量 P2P；首末 rank 收 loss/输出。

### 5.2 DualPipeV（`dualpipe/dualpipev.py`）
- Sea AI Lab「cut-in-half」V 型派生：4 PP rank（8 stage）+10 micro-batch 示例；同等气泡下设备数减半（PP/2）、每设备参数仍 2×、激活 PP+1（README 对比表）。
- 气泡公式表（README）：1F1B `(PP-1)(F+B)`；ZB1P `(PP-1)(F+B-2W)`；DualPipe/DualPipeV `(PP/2-1)(F&B+B-3W)`。

### 5.3 工程与关系
- 依赖仅 PyTorch ≥2.0；`examples/example_dualpipe.py / example_dualpipev.py` 可单机多进程跑通；真实使用需自实现 `overlapped_forward_backward`（README 注）。
- 与 profile-data 互引（训练 profile 展示一对 F/B chunk 的重叠）；作者 Jiashi Li / Chengqi Deng / Wenfeng Liang。
- work4ai：讲透分布式AI系统（PP 调度代际：1F1B→ZB→双向；气泡/显存的解析权衡）；讲透优化理论（把调度写成可枚举步数的确定性程序）；工程化手册库（如何设计可复现的调度 demo）。

---

## 6. EPLB —— 专家并行负载均衡器（Day 4）

**定位一句话**：V3 论文的冗余专家策略的开源实现：按负载统计把重载专家复制 r 份，再启发式装箱到 GPU，尽量让同组专家同节点（配合 group-limited routing）。

### 6.1 算法（`eplb.py`，单文件 ~160 行）
- **入口** `rebalance_experts(weight, num_replicas, num_groups, num_nodes, num_gpus)`：`weight [层数, 逻辑专家数]`。
- **两种策略**：`num_groups % num_nodes == 0` → 分层（hierarchical），否则全局（退化为 `rebalance_experts_hierarchical(weight, num_replicas, 1, 1, num_gpus)`）。README：分层用于 prefill（小 EP），全局用于 decode（大 EP）。
- **分层三步**：
  1. `balanced_packing(tokens_per_group, num_nodes)`：组→节点装箱（每个 bin 恰好 n/m 个对象，贪心选当前总重最小的未满 bin——LPT 变体，保证负载均衡且组不拆散）；
  2. `replicate_experts(tokens_per_mlog, num_physical_experts // num_nodes)`：节点内复制——迭代地复制 `argmax(weight/logcnt)` 的专家（「负载/副本数」最大的专家优先，最小化最大副本负载）；
  3. `balanced_packing(tokens_per_phy, num_gpus // num_nodes)`：物理专家→GPU 装箱。
- 输出 `phy2log / log2phy / logcnt`；README 示例：2 层 × 12 专家，16 副本（每层 4 冗余），2 节点 × 4 GPU。
- 负载预测不在库内（README：常用历史统计滑动平均）——留给 EPLB 之上的系统。

### 6.2 关系与 work4ai
- V3 技术报告「冗余专家」的直接代码化；LPLB 内嵌本算法做静态重排（`lplb/eplb.py` 是其复制品）；DeepSeek-V3 推理仓库用它做预填充/解码分置。
- work4ai：讲透优化理论（装箱/复制比的贪心近似与最优性讨论：`max weight/logcnt` 等价于最小化最大负载的多副本分数背包）；讲透分布式AI系统（EP 负载均衡的静态层）。

---

## 7. LPLB —— 线性规划负载均衡（早期研究）

**定位一句话**：EPLB 的动态化研究原型：在冗余专家构成的固定拓扑（Cube/Hypercube/Torus）上，对每个 batch 解一个 LP，把 token 沿「冗余边」重定向到轻载 GPU；LP 求解器跑在**单个 SM** 上。

### 7.1 形式化与实现（`lplb/planner.py` + README）
- `r2o [group_size, num_redundants]`：冗余专家→原专家映射。结构约束（planner.py docstring）：每 rank 冗余数相同；任意 rank 的第 i 个冗余专家是另一 rank 第 i 个专家的拷贝 ⇒ 每个冗余专家恰好被两 rank 共享（构成图的边）。
- **LP**：边容量 = 当前 batch 中该冗余专家分得的 token 数；沿边重分配 token 流，最小化 EP 组内负载不均衡（README How it works）。
- 求解器：`CompiledSolver`（`lplb/_cpp`）实现单 SM **内点法（IPM）**，线性代数用 cuSolverDx/cuBLASDx（`download-mathdx.sh` 下载 mathdx 头文件库）。
- 与 DeepEP：`init_from_deep_ep(buffer)` 直接复用 DeepEP 内部通信子做实时负载统计（NVLink/NVSHMEM 广播，替代 `torch.distributed.allreduce`）。
- `run(indices, avail_counter, N_SMS)`：输入逻辑专家选择，输出物理专家重定向；`N_SMS=100` 级别可调（README 示例）。
- 常量 `256`（planner.py:31 与 tests）为每 rank token 上界参数。
- **典型拓扑**（README + `tests/test_solve.py`）：`CUBE_8P2E`（8 GPU 立方体含对角边，每 GPU ≥2 专家）、`HYPERCUBE_16P2E`（16 GPU 无对角）、`RING_8P`、`torus_2d(8,4)`；测试断言解的负载比 ≤ ~1.01–1.1。
- **自述局限**（README）：只均衡 token 数、不建模分组 GEMM 时间的非线性；求解 ~100 µs（节点内）对小 batch 不可忽略；极端全局不均衡时可能劣于 EPLB（不给同一原始专家多副本）。

### 7.2 工程与关系
- 构建：`pip install --no-build-isolation`（依赖 CUDA ≥12.6.3 + mathdx）；pytest（`tests/test_idx_processing.py / test_solve.py`）。
- EPLB（静态重排）+ LPLB（逐 batch 动态重定向）= 两级负载均衡；DeepEP 提供统计通道。
- work4ai：讲透优化理论（LP 建模范式进生产内核的完整案例：容量约束、对偶解释、100µs 级 GPU 求解器）；工程化手册库（mathdx 设备端求解器集成）。

---

## 8. profile-data —— V3/R1 计算-通信重叠的剖析数据（Day 4）

**定位一句话**：三个 PyTorch Profiler trace（chrome tracing 格式），公开 V3/R1 训练（DualPipe）、prefill、decode 的真实重叠时间线，是「论文声称 ↔ 内核实况」的对照证据。

### 8.1 内容与配置（README + JSON 实测）
- `train.json`（3.0 MB）：DualPipe 的一对前向/反向 chunk（每 chunk 含 **4 层 MoE**）；配置 = V3 预训练：**EP64、TP1、4K 序列**；profiling 时不含 PP 通信；MoE 路由按「绝对均衡」模拟。
  - 实测高频内核（对 `"name"` 计数）：`ac2g`（all-compute-to-graphics 之外为 DeepEP 内部辅助 kernel，4876 次）、`cuda::per_token_cast_to_fp8_with_channels<bf16, 128, ...>`（**per-128 通道逐 token FP8 cast**，76 次）、`dpsk::grouped_gemm::cuda::utils::transpose<512,128,4,4>`、CUTLASS 实例 `dpsk::grouped_gemm::cuda::fp8_ptp128c::GemmKernel`（per-tensor-per-128-channel）与 `fp8_dptp128c_acc`（带累加反向）——**训练生产栈的量化粒度命名直接可见**。
- `prefill.json`（16.7 MB）：**EP32、TP1**（V3/R1 线上部署同款），prompt 4K、每 GPU batch 16K token；两个 micro-batch 重叠计算与 all-to-all，且两微批的注意力负载人为均衡（同一条 prompt 可被拆进两个微批）。
- `decode.json`（4.4 MB）：**EP128、TP1**、prompt 4K、每 GPU 128 请求；同样双微批重叠，但 all-to-all 不占 SM：RDMA 消息发出后所有 SM 释放给计算，算完再等通信完成（→ DeepEP 低延迟 hook 模式的实况）。

### 8.2 用法与关系
- 用 chrome://tracing 或 edge://tracing 直接可视化；仓库仅 README + 3 JSON + 3 截图。
- 是 DualPipe README、DeepEP 解码设计的「证据层」；训练栈内核名（dpsk:: 前缀 = DeepSeek 内部 CUTLASS 分支）可与 DeepGEMM 当前 API 对应（per-token per-128-channel）。
- work4ai：讲透分布式AI系统（读 trace 判断重叠质量的方法论）；工程化手册库（profiler 数据作为可发布产物的实践）。

---

## 9. 八仓纵向综合：DeepSeek 的「算子-通信-负载均衡」内核栈

**分层拼图（自底向上）**：

1. **量化/SF 层**：per-token-128-channel（激活）× per-128 或 per-tensor（权重）的 FP8 约定贯穿全栈——DeepEP dispatch 内核边发边 cast（`warp_reduce_max<16>`）、DeepGEMM 1D2D 内核消费同款 SF、TileKernels 生成同款 SF（`use_tma_aligned_col_major_sf / packed_ue8m0`）、FlashMLA 的 KV cache 656B 也是 4×128 通道 SF、profile-data 里 `per_token_cast_to_fp8_with_channels<_,128>` 与 `fp8_ptp128c` 留名。**一个量化约定统一了通信、GEMM、attention、profiling 四层**。
2. **GEMM/Attention 算子层**：DeepGEMM（密集/分组/Masked/反向 + V3.2 索引器 + Mega MoE）与 FlashMLA（MQA 解码/稀疏 prefill-decode/MHA）共同支撑 V3→V3.2 的「Dense MLA → DSA 稀疏 + 闪电索引器」演进。两者共享同一套工程方法论：**JIT 编译、解析式 cost model 选布局（不做运行时 autotune）、warp specialization + TMA 多级流水、把约束写进 static_assert**。
3. **通信层（DeepEP）**：V1 证明了「NVLink 域内转发 + IBGDA 纯 RDMA 直写 + hook 0-SM 接收」三层武器；V2 把经验升级为**解析式设计**（SM/QP 公式、统一 ElasticBuffer、NCCL Gin 复用现有通信子），并把 EP 外的 PP/CP/Engram/AGRS 一并「通信原语化」。方向明确：通信内核与计算内核共享同一份 SM 预算表，按带宽模型直接推导。
4. **调度层**：DualPipe 把 PP 气泡公式从 `(PP-1)(F+B)` 压到 `(PP/2-1)(F&B+B-3W)`，代价是 2× 参数——其成立前提恰恰是模块级 `overlapped_forward_backward`（MoE 层内缝入 dispatch/combine 通信，profile-data 训练 trace 可证）。
5. **负载均衡层**：EPLB（分钟级静态：复制 r 份重专家 + 组-节点-GPU 三级装箱）→ LPLB（batch 级动态：冗余专家拓扑上的 LP，单 SM IPM 100µs）→（DeepEP V2 路线图里的 EP replay 消中间 buffer）。负载信息经 DeepEP 通信子回流，闭环。
6. **证据层**：profile-data 用真实 trace 把「论文公式」钉在内核时间线上（EP64 训练 / EP32 prefill / EP128 decode 与 open-infra-index Day 6 的推理总览一致）。

**「为 MoE 重塑整个底座」的思路**（跨仓提炼）：
- **先定模型语义，再定通信语义**：V3 的 group-limited routing（top-4 组×top-8 专家）直接映射为 DeepEP 的「NVLink 8 卡域 + RDMA 域」硬件拓扑和 EPLB 的组感知装箱——路由算法、网络拓扑、负载均衡三者同构设计。
- **算子即通信，通信即算子**：从 Mega MoE（单 kernel 内做完 dispatch+GEMM+SwiGLU+GEMM+combine）到 DualPipe 的模块级 F&B 融合，DeepSeek 持续把通信搬进计算 kernel 的「空闲槽位」（CUDA core 做量化的同时 tensor core 做乘、RDMA 飞行时 SM 全给计算）。
- **用解析模型替代搜索**：DeepEP V2 的 SM/QP 公式、DeepGEMM 的 L1/L2 cycle 模型、FlashMLA 的 FLOPs/byte 判据（h_q·s_q ≥ 128）——三家都不搞运行时 autotuning，而是把硬件常数（NVLink 160GB/s、CX7 50GB/s、SM 读 200/写 50 GB/s、L1 128B/cycle）写进公式。这是「H800 这种已知封闭集群上的全局最优」方法论。
- **精度-带宽联合设计**：FP8 dispatch（传输省一半）、FP8 KV（656B/token）、10-bit LogFMT、UE8M0（SF 从 FP32 4B 压到 1B 且免乘法）——每条通信/访存路径都配一个低精度变体。
- **开源节奏即架构叙事**：2025-02 开源周按「Day1 算子 → Day2 通信 → Day3 GEMM → Day4 调度/均衡/证据 → Day5 存储 → Day6 系统」逐层揭底座（open-infra-index 总索引）；2025-2026 的演进（DeepEP V2、Mega MoE、TileKernels 的 Engram/mHC、FlashMLA 稀疏化）显示同一底座正被改造成 **V3.2/V4 时代「稀疏注意力 + 超节点 scale-up + 记忆分层（Engram）」**的新形态。

**诚实性说明**：本笔记未读到的内容（如 DeepEP V2 内核 .cu 的完整数据面、Mega MoE 测试的绝对性能数、FlashMLA sm100 kernel 内部实现、TileKernels 原开源周版本的 GEMM/attention 内核——当前克隆中已不存在）一律未写或明确标注「README/文档所述」。3FS/smallpond/harness 等非本任务仓库未深入。

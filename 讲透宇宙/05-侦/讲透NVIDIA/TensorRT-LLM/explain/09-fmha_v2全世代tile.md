# 09 · fmha_v2：SM70-120 全世代注意力 tile 体系与 6990 行代码生成中枢

## 一、角色定位

`cpp/kernels/fmha_v2/` 是 TensorRT-LLM 自研的融合多头注意力 kernel 仓，覆盖**六个 SM 世代**（sm2name 映射，setup.py:21-33：70/72=volta、75=turing、80/86/87=ampere、89=ada、90=hopper、120=blackwell），服务 context/prefill 阶段的主注意力计算。它的特殊性在于组织方式：一份 `setup.py`（6990 行）当**代码生成中枢**，笛卡尔积枚举 kernel 规格，生成 kernel 源码、host API 与 cubin 头，再交给 `train_ops/` 复用同一套设施生成训练侧变体。这是"用构建系统管理 kernel 组合爆炸"的代表作，对应图谱 L13 层。

## 二、内部结构

**setup.py 三段生成管线**：`get_kernel_code`（setup.py:2235）按 KernelSpec 拼 kernel 源；`get_api_code`（:2473）生成 host 侧分发 API；`get_cubin_header`（:3346）产出 cubin+源码双头（:4024-4025 注释保留了新旧行为切换开关）。规格由 namedtuple+IntEnum+`itertools.product` 枚举（模块头 import 块）：架构 × dtype × tile 形状 × warpspec 与否等维度的组合。dtype 面 `dtype2traits`（setup.py:35-44）七档：int8→imma、fp16→hmma（fp16/fp32 累加两档）、bf16→hmma、e4m3→qmma（fp32/fp16 累加 + e4m3_fp16 混合）——每个 dtype 映射到对应 tensor core 指令族 traits。`get_effective_sm_and_name`（:2163）处理"指令版本 ≤ 目标架构"的降级：ksm_mma 可以落后于目标 sm，kernel 按指令代而非目标代编译。

**tile 基建按世代分层**。`src/fmha/` 共享层：smem_tile*.h（QKV/O/V 各自的共享内存 tile）、gmem_tile*.h（gmem_tile_o_packed 等 packed 变体）、fragment/softmax/mask/alibi_params/numeric_types、`paged_kv_cache.h`（分页 KV 接入）、`kernel_traits.h`。`src/fmha/hopper/` 是 SM90 专属：`gmma_descriptor.h`/`tma_descriptor.h`（GMMA/TMA 描述符）、utils_gmma/utils_hgmma/utils_hgmma_bf16/utils_igmma/utils_qgmma 五族矩阵指令封装、`utils_warpgroup.h`、`compute_tile.h`、`arrive_wait.h`（warpgroup 级同步）。`src/fmha/warpspec/` 是 warp specialization 通用件：`dma.h`/`compute.h`（DMA 与计算 warp 分工）、`circular_buffer.h`（多级流水）、`epilogue.h`；`warpspec_sm120/` 为 Blackwell 单列。寄存器再分配实锤：`setmaxnreg_compute_str` 反复出现在模板里（setup.py:1706/1755/1805/1855/1905），`get_reg_count`（:2142-2146）给 dma/compute warp 各配 224/232 寄存器——warpspec 的本质就是用 setmaxnreg 把寄存器预算向计算 warp 倾斜。

**train_ops/ 训练侧变体**（`train_setup.py`（510 行）直接 import 上游 setup.py 复用模板设施，train_setup.py:21）：fprop 家族 `fused_multihead_attention_fprop_kernel.h`/`_1xN.h`/`_1xN_reload.h`/flash_attn 变体；dgrad 家族五档（1xN、1xN_flash、1xN_noloop、1xN_reload、1xN_reload_noloop），配套 `smem_tile_d.h`/`smem_tile_dq.h`/`gmem_tile_d.h`/`fmha_noloop_reduce.cu`——dQ 反传是这仓独有的重头。兼容三入口：`bert_mha_train_api.cpp`（BERT 训练）、`apex_mha_api.cpp`（NVIDIA Apex 接口）、`te_mha.py`（TransformerEngine 集成）、`fp8_mha_api.cpp`+`hopper/fmha_fprop_fp8_512_sm90.cu`/`fmha_dgrad_fp8_512_sm90.cu`（SM90 FP8 训练）。**dropout 用 Philox**：`philox.h` 实现 `class Philox`（philox.h:22）device 内联构造（seed/subsequence/offset 三元组，key/counter 布局对齐 curand 语义），训练 kernel 在 device 侧确定性再生 dropout 掩码。

warpspec 的 DMA 侧实现在 `src/fmha/warpspec/dma.h`（957 行）：`run_packed_qkv`（dma.h:182）编排 Q/KV 的 TMA 预取，load_q/load_kv 双缓冲（dma.h:292-293/:305）与 circular_buffer 配合；计算侧 `compute.h`（717 行）与之成对；GMMA 描述符编排在 `src/fmha/hopper/gmma_descriptor.h`（603 行）。

## 三、外部连接

Makefile 双架构锁 `TORCH_CUDA_ARCH_LIST="8.0;9.0"`（Makefile:28，SHELL 强制 bash，见图谱 pipeline:cpp/kernels/fmha_v2/Makefile 节点）；test 侧 `test_sm70/75/80/90_configs.sh` 按世代跑配置矩阵，`test/fmha/filter_rules.py` 用统一签名 `(fmha_arg, **kwargs)` 在 pytest collection 期组合过滤规则（返回 None/覆盖列表/无操作三态）；`train_ops/fmha_unit_test.py` 以 try/except ImportError 容忍未构建场景。产品侧：编译产物经 `tensorrt_llm` 的 attentionOp 分派面（cpp/tensorrt_llm/common/attentionOp.cpp 的 enqueueContext 按 Ampere/Hopper/Blackwell×MLA/滑窗/Sage/投机解码分派，图谱 L11）进入 PyTorch 后端。

## 四、数据流

一次生成：spec 表 → `get_kernel_code` 展开模板（含 setmaxnreg 段与寄存器数）→ nvcc 编译出 cubin → `get_cubin_header` 序列化为头文件数组 → `get_api_code` 生成的 API 按 (架构, dtype, tile) 查表 launch。运行时一轮 fprop：TMA/GMEM 装 QKV tile → warpspec 下 DMA warp 预取下一 tile 进 circular buffer、compute warp 做 QK GMMA → softmax（softmax.h 的在线重标度）→ PV GMMA → epilogue 写 O；训练侧再叠 dgrad：D 与 dV/dK 走 1xN 系列，noloop 变体把 reduce 拆出（fmha_noloop_reduce.cu），Philox 以相同 seed/offset 在反向时再生前向掩码。

## 五、设计决策

① **代码生成压组合爆炸**：六个架构 × 七 dtype × tile 参数 × 是否 warpspec，手写不可维护；setup.py 让"加一个 spec"变成加一行枚举。② **指令代与目标代解耦**（get_effective_sm_and_name）：同一 kernel 源在 89 上按 ampere 指令编译，避免为每目标代重写。③ **warpspec 从 Hopper 开始值得**：TMA 异步装载后，DMA/compute warp 分工 + setmaxnreg 寄存器再分配才能兑现收益——这解释了为什么 warpspec 目录与 hopper 目录并列而非嵌套。④ **训练与推理同源**：train_ops 复用 setup.py 而非 fork，dgrad 的 noloop 变体牺牲一次额外 reduce 换主循环寄存器余量，是对 SM80 寄存器预算的精准妥协。⑤ Philox 而非 host RNG：掩码必须前反向逐位一致，counter 型 RNG 是唯一可 device 确定性再生的选择。

## 六、新人提示

入口三件：README.md → setup.py 的 sm2name/dtype2traits 两张表 → 任一 `get_*_code` 函数读模板展开方式。改 kernel 优先改模板再重新生成，不要手改产物。跑单测记住 Makefile 的 arch 锁与 XQA 环境变量不同族（这是另一个目录）；train_ops 未构建时 pytest 静默跳过属预期（fmha_unit_test.py 的 ImportError 容忍），别误判为测试通过。调 warpspec kernel 时先看 get_reg_count 的配额——寄存器改崩的表现是 setmaxnreg 断言而非慢。图谱提示：Makefile 节点只收 pipeline: 两个，target 未入图（详见 README 勘误）。

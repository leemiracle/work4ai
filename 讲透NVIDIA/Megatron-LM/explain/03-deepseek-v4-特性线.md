# 03 · DeepSeek-V4 特性线——CSA/HCA 压缩、DSA indexer 蒸馏、mHC 与 YaRN Triton

> 主战场：`megatron/core/transformer/experimental_attention_variant/`（15 文件 9607 行）+ `megatron/core/models/hybrid/layers/utils.py` + `megatron/training/models/deepseek_v4.py` + `fusions/` 两个融合文件。这是 mcore 对 DeepSeek-V4 "先压缩再稀疏" 注意力家族的完整实现。

## ① 角色定位：这个子系统解决什么问题

DeepSeek-V3.2 的 DSA 用 Lightning Indexer 为每个 query 选 Top-2048 KV；V4 在其前插入**在线压缩**——先把 KV 序列按比率池化成短序列再选 top-k，三种注意力模式按压缩比区分：CSA（compress_ratio=4，重叠压缩）、HCA（128，非重叠重压缩）、WINDOW（0，纯滑窗不压缩）。mcore 把这条特性线落成四件事：①用**单字符层模式串**（hybrid pattern）描述任意 SWA/CSA/HCA/DSA/Mamba 混合堆叠；②把 V3.2 的 indexer KL 蒸馏损失扩展到压缩场景（教师分布要计入被压缩掉的质量）；③DSA indexer/稀疏 MLA 的 TileLang fused kernel 后端；④mHC 超连接（n 流残差）与 MLA+YaRN RoPE 的 Triton 融合。一句话：**这批代码让 mcore 能训练 V4 代的混合注意力模型，而不只是推理**。

## ② 内部结构：关键类/函数与行号锚

**压缩比符号系统（`models/hybrid/layers/utils.py`）**：`Symbols` 类是 hybrid pattern 的词表——`CSA="C"`（:23，注释即 "DSv4 Compressed Sparse Attention (compress_ratio=4)"）、`HCA='H'`（:24）、`WINDOW="W"`（:26）。`LAYER_CONFIG_MAP`（:31-42）里 C/H/W 三个符号**映射到同一个 `CSALayerConfig`**（`experimental_attention_variant/dsv4_layer_config.py:7`，仅多一个 `compress_ratio: int = 0` 字段），区分发生在 `create_layer_config`（utils.py:68）的收尾处（:85）：按符号从 `DSV4_COMPRESS_RATIO_MAP = {CSA: 4, HCA: 128, WINDOW: 0}`（:43）回填压缩比。反查函数 `get_layer_symbol_from_config`（:89）用压缩比逆映射回符号，配错比值直接 ValueError（:102-110）。训练侧配套 `megatron/training/models/deepseek_v4.py:9` 的 `normalize_dsv4_hybrid_csa_compress_ratios`：把紧凑比例列表（只含 W/C/H 注意力层）展开成全层列表，且 **assert 用户给的比值必须等于符号默认值**（:37-40、:60-64）——压缩比是模型定义的一部分，不是可调超参。

**压缩器（`csa.py:422` `Compressor`）**：门控池化——`linear_wkv`+`linear_wgate` 两个 duplicated 投影（:465-484）、每压缩组一个 FP32 绝对位置嵌入 `_ape`（:487-491，注释注明"reference DeepSeek V4 checkpoint 中保持高精度"）。关键分岔在 :449-450：`self.overlap = compress_ratio == 4; self.coff = 1 + int(self.overlap)`——**ratio=4 用重叠窗口（coff=2），ratio=128 用非重叠（coff=1）**；`_overlap_transform`（:515）做重叠窗口重排。`backward_dw`（:511）把投影的权重梯度推迟到主反向（wgrad 延迟线）。

**混合注意力模块（`deepseek_v4_hybrid_attention.py`）**：`DSv4HybridAttention`（:67）在 SWA/CSA/HCA 三模式间切换（图谱原话），`DSv4HybridSelfAttention`（:419）组装 QKV/输出投影并管理 per-layer CUDA Graph 捕获区；`_q_rms_norm`（:48）整个函数被 `@torch.compile` 包裹。

**DSA indexer 与 KL 蒸馏（`dsa.py`）**：`DSAIndexer`（:1237）docstring 直接引用 DeepSeek-V3.2 参考实现；RoPE 类型二选一 rope/yarn（:1284-1306）；`is_dsa_skip_topk_layer`（:36）/`source_dsa_compute_layer`（:49）实现**top-k 复用**——每 topk_freq 层重算一次 indexer，中间层复用结果。损失线四层：`compute_dsa_indexer_loss`（:432，教师=FP32 全量 attention scores bmm，:509-513）；`_compute_indexer_teacher_probabilities`（:570）实现 `non_compressed_lse` 机制——被压缩/滑窗挡住的教师 key 不进 bmm，但其质量以 detached LSE 参与 softmax 分母（`torch.logaddexp` 合成 full_lse，:622），并处理 FP32 下溢（:633-639 注释：跨 head 公共平移保相对权重，"CSA currently requires TP1"）；底层算子在 `dsa_indexer_loss.py`（`INDEXER_LOSS_EPS=1e-10` :9、L1 归一化 :12、`KL(target||predict)` 元素项 :27）；训练挂载靠 `DSAIndexerLossAutoScaler`（:1145，forward 恒等、backward 注入 KL 梯度）与 fused 版 `FusedDSAIndexerLoss`（:1030）。

**TileLang kernel 后端**：入口 `dsa_tilelang_kernels.py:16` `run_fused_qk_topk`（docstring："TileLang backend hooks for optional fused DeepSeek sparse attention kernels"，返回 indices-only 适配共享 hook 契约）；实体在 `ops/`（9 文件 2886 行）——`tilelang_dsa.py`（908 行，`fused_qk_topk_lighting` :215）、`tilelang_indexer_loss.py`（`_get_kl_kernel` :56、`sparse_indexer_kl` :200）、sparse_mla 前向/反向（310/529 行）。另有 cuDNN 后端 `dsa_cudnn_kernels.py`（2698 行，目录最大）。

**mHC 超连接（`transformer/hyper_connection.py`）**：`HyperConnectionModule`（:191）实现 `x_{l+1} = H_res^T @ x_l + H_post^T @ F(H_pre @ x_l)`；`mapping_proj` 从 n*C 维投影出 n²+2n 个动态映射值（:231-233）；Sinkhorn-Knopp 投影有自定义 autograd（:69）。**条件导入**在 :257-270：`if config.use_fused_mhc: from megatron.core.fusions.fused_mhc_kernels import ...`，否则回落 native 实现。融合库 `fusions/fused_mhc_kernels.py:49` 定义 `MHCBackend = Literal["auto", "native", "triton", "cutile"]`，带可用性探测（`is_cutile_available` :87）与一次性日志。hybrid 侧还有层边界包装器 `models/hybrid/layers/hybrid_hyper_connection.py:HyperConnectionHybridLayer`。

**MLA/YaRN Triton（`fusions/fused_mla_yarn_rope_apply.py`，996 行）**：`_mla_rope_fwd_inplace_kernel`（:79）等 `@triton.jit` 内核 + `@triton.autotune` 扫 BLOCK_H 1→128（:64-73）；文件头 try/except 里用 **MagicMock 替身保证无 Triton 时 doctest 可跑**（:23-26）。配套数学在 `models/common/embeddings/yarn_rotary_pos_embedding.py:21` `YarnRotaryEmbedding`（correction range 插值 + mscale 浓度因子，6 个 `_yarn_*` 辅助函数）。

## ③ 外部连接：与哪些子系统互依

这条特性线两头都咬合别的子系统。**向上**挂 hybrid 模型线（第 04 篇）：Symbols 词表被 `models/hybrid/hybrid_layer_allocation.py` 的 pattern 解析消费，C/H/W 层经 `create_layer_config` 进 `HybridModel` 的逐层构建；DSv4 spec 装配独立成 `deepseek_v4_hybrid_attention_module_specs.py`（`get_dsv4_hybrid_module_spec_for_backend`，按后端能力绑 linear_qkv/core_attention）。**向下**依赖并行基座：`DSAIndexer.__init__` 用 `ProcessGroupCollection.use_mpu_process_groups(required_pgs=["tp","cp"])`（dsa.py:1282），Compressor 更是**强制要求显式 pg_collection**（csa.py:450，None 直接 ValueError——新代码不再容忍全局并行态）。**横向**接第 02 篇 MoE：CSA/HCA 教师损失的注释提到"CSA currently requires TP1"；`fine_grained_activation_offload`（deepseek_v4_hybrid_attention.py:1-3 import）把注意力和 paged stash 的激活 offload 线连起来。mHC 的条件导入则是 fusions 层的典型消费方式——`fused_mla_yarn_rope_apply` 在 DSv4 注意力里同样以 try/except 引入（:19-26，失败置 None 走非融合路径）。

## ④ 数据流：一次典型调用的路径

以 HCA 层（ratio=128）训练前向为例：

1. `HybridModel` 按 pattern 字符（'H'）调 `create_layer_config`（utils.py:68）→ CSALayerConfig + compress_ratio=128。
2. `DSv4HybridSelfAttention` 先过 QKV 投影与 `_q_rms_norm`，KV 一路进 `Compressor`（csa.py:422）：每 128 个 token 一组，`linear_wkv`/`linear_wgate` 门控池化 + `_ape` 位置嵌入，输出 1/128 长度的压缩 KV。
3. `DSAIndexer`（若非 skip 层）在压缩 KV 上算 index scores 选 top-k（TileLang 后端走 `run_fused_qk_topk` → `fused_qk_topk_lighting`）；skip 层用 `source_dsa_compute_layer` 找到上游结果直接复用。
4. 稀疏 MLA 只对 top-k+压缩条目做注意力；`DSAttention`（dsa.py:1677）有吸收/非吸收双路径。
5. 反向时 indexer 蒸馏损失生效：教师=FP32 全量 scores（含 `non_compressed_lse` 外部质量），`indexer_loss_from_target` 算 KL，`DSAIndexerLossAutoScaler` 把梯度乘 scale 注入主干梯度流——**indexer 是被"蒸馏"出来的，训练结束后教师支路可弃**。
6. 层间残差全程由 `HyperConnectionModule` 管理：`compute_mappings`（:346）产出动态 H_pre/H_post/H_res，融合后端按 auto 策略选 triton/cutile/native。

## ⑤ 设计决策：为什么这么设计

**为什么 C/H/W 共用一个 CSALayerConfig 而不是三个类？** 压缩比是唯一的差异维度且取值被锁死（assert 钉住 4/128/0），三个类只会复制代码。符号→比值的映射表 `DSV4_COMPRESS_RATIO_MAP` 放在 Symbols 里，等于把"V4 有哪几种注意力"声明为**词表级常量**，pattern 解析、config 生成、合法性校验共享同一份真值（推断：反向查找函数的存在说明符号与比值的双向一致性是被刻意维护的）。

**为什么教师分布要引入 non_compressed_lse？** 压缩把绝大多数 key 挡在 bmm 之外，若教师分布只在压缩后的 key 上归一化，indexer 学到的目标分布就是错的（漏掉了滑窗/未压缩 key 的概率质量）。用 detached LSE 做分母修正是最小代价方案：不重算全量 scores，只传一个 [b,np,sq] 的小张量。FP32 下溢的处理（跨 head 公共平移，:633-639）说明这条路径在 128× 压缩下真实触发过（推断：注释里"external window/sink mass can put every head's compressed mass below FP32 normal range"是实战教训）。

**为什么 TileLang 而不是全 Triton？** TileLang 是 tile 级 DSL，对 indexer 这种"top-k 选择+损失 fused"的复杂 tile 程序比手写 Triton 表达力强；同时保留 cuDNN 后端（dsa_cudnn_kernels.py 2698 行）和 Triton（ops/indexer.py）形成三后端竞争。mHC 那边同样三后端（triton/cutile/native），且 :255-261 的注释展示了精细取舍：`fused_add_3` 永远用 torch.compile，因为"cuTile 一个平凡 a+b+c 要 56 regs/thread，对纯访存约束的 elementwise 不值"——**后端选择下沉到单个算子粒度**。

**为什么 skip-topk（topk_freq）存在？** 相邻 DSA 层的 top-k 选择高度相关，重算是浪费；V4 用 hash 路由前几层的思路同源——把"选哪些 token"的计算跨层复用。这把 indexer 成本从 O(层数) 摊到 O(层数/topk_freq)。

## ⑥ 新人提示：坑/入口/阅读顺序

- **阅读顺序**：utils.py 的 Symbols（60 行）→ dsv4_layer_config.py（13 行）→ csa.py 的 Compressor（:422-600）→ deepseek_v4_hybrid_attention.py → dsa.py 只读 :36-56（skip-topk）、:1237-1350（indexer）、:432-520 + :570-644（损失）→ fusions 两个文件扫头部即可。
- **别被文件名骗**：`dsa.py` 的 DSA 是 V3.2 稀疏注意力，V4 的 C/H/W 全部走 `csa.py`+`deepseek_v4_hybrid_attention.py`；但 indexer 与 KL 损失是两者共用的（V4 的 HCA 在压缩 KV 上复用同一 indexer）。
- **compress_ratio 不可自造**：想要 ratio=8？normalize 函数的 assert 会拦你——改代码改词表，不是改命令行。
- **experimental_attention_variant 目录是"特性旗舱"**：条件导入（TE/hadamard/TileLang/融合 RoPE）遍布头部，读代码先看每个 try/except 决定了哪些路径在你环境里实际存在，否则会追进死分支。
- TileLang kernel 全部懒加载且返回 Optional（run_fused_qk_topk 失败返回 None 回落 PyTorch naive 实现 `fused_qk_topk_naive` dsa.py:690），性能调优时先确认真的走了 TileLang 路径（`log_fused_mhc_backend_once` 式的一次性日志是判断依据）。
- 测试入口在 `tests/unit_tests/transformer/`；hybrid pattern 的合法性测试在 `tests/unit_tests/models/hybrid/test_layer_utils.py`。

# 讲透 Star-Attention（NVIDIA）

> 本地仓：/usr-data/data2/repos/agent-repos/NVIDIA/Star-Attention @ dadb4be9
> 主题：星注意力——分块局部编码（Phase 1）+ anchor 同步的全局 query 注意力（Phase 2），ICML 2025 / arXiv 2411.17116 配套实现。
> 论文口径：RULER 16K-128K 保持 Ring Attention 97-100% 精度，推理加速 1.2x-4.7x。

## 全链产物状态

| 产物 | 状态 | 规模/说明 |
|---|---|---|
| deepwiki/ | ✅（2026-10-26 轮） | INDEX + 全页 |
| understand 图谱 | ✅ | 141 节点 / 230 边 / 6 层 / 8 步 tour，validator 0 issues，fingerprints 51 文件@dadb4be9（仓内 .understand-anything/knowledge-graph.json） |
| onboarding/ | ✅ | ONBOARDING.md，7 节，不计空格 ~5.6k 字符，45 锚全核实 |
| explain/ | ✅ | 3 篇（核心核 / 三基线 / Llama 注入层），六节结构，锚 16/24/18 |
| 勘误清单 | ✅ | 6 条（下文），全部 file:line 实证 |

## 已核实勘误（README/文档 vs 源码实证）

1. **attn_type 文档串过时，'starkv' 不存在、'ring' 未列**：`run_star_attn_inference.py:124` 与 `scripts/time_inference.py:109` 的 docstring 都写 `One of ['dense', 'star', 'starkv']`，但实际分发只实现 dense/ring/star（run_star_attn_inference.py:72/:81/:90），传入 starkv 会 `Unsupported attention type`（:103）。
2. **num_ring_steps 默认值文档与签名打架**：modeling_flash_attention_utils.py:82-83 docstring 称 "defaults to -1"（=启用完整环形），实际签名默认 `num_ring_steps: int = 0`（:53，零通信局部注意力）。
3. **README 自定义数据示例对 star/ring 不可直接运行**：README.md:215 示例是裸 `python run_star_attn_inference.py ... --attn_type star`，但 `init_distributed` 仅在 RANK 环境变量存在时才 `dist.init_process_group`（run_star_attn_inference.py:39-40），随后 model.py:80 直接 raise "Distributed environment is not initialized!"，且 modeling_llama.py:67-71 在 import 期就要求 dist 已初始化——star/ring 必须在 torchrun 下运行，只有 dense 可单进程裸跑。
4. **DenseAttentionModel 不继承分布式基类**：图谱与常见解读把三基线说成"基类 + 三实现"，实际 `DenseAttentionModel`（model.py:337）是独立类，自带 AutoModelForCausalLM 装载（:343），仅 Star（:174）/Ring（:269）继承 DistributedInferenceBaseModel（:24）。
5. **launch.sh 128K 配置与 README"统一 1/4"表述矛盾**：README.md:91（Figure 1 caption）称 "All runs use a block and anchor block size set to one-quarter of the total sequence length"，但 launch.sh:52 的 131072 档用 `-bs 16384`（=1/8 上下文）；16K/32K/64K 三档（launch.sh:49-51）才是严格 1/4。
6. **Phase 2 通信量口径：文档"query host 收集"vs 实现"全 rank all_gather"**：README.md:289 称每 token 只需向 query host 传"一个标量 s_h + 一个向量 A_h"，实现是 `dist.all_gather` 让每个 rank 都收到全量的 out 与 LSE（star_flash_attn/star_flash_attn.py:41-42），且 LSE 按 (head, query 行) 一份而非每 token 单标量；数学等价（utils.py:33-34 log 空间合并），通信模式与常量口径不同。

## 目录

- deepwiki/ — DeepWiki 快照
- onboarding/ONBOARDING.md — 7 节上手指南（定位/分层/子系统/数据流/运行/决策与勘误/路线）
- explain/01-star-flash-attn-kernel.md — 星注意力核心核（164 行算法闭环）
- explain/02-model-three-baselines.md — Star/Ring/Dense 三基线编排
- explain/03-modeling-llama-injection.md — HF Llama 注入层（718 行缝合术）

2026-11-11 讲透NVIDIA 批量轮（四仓一体）产出。

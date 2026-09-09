# 讲透 FlashMLA — explain 精讲索引

FlashMLA 是 DeepSeek 官方开源的 MLA（Multi-head Latent Attention）高性能内核仓，服务 V2/V3/V3.2 系列的注意力计算。本目录收录 4 篇重要文件精讲，选自知识图谱 tour 前 4 步引用的核心文件，覆盖"Python 门面 → C++ 分派 → 瓦片调度 → splitKV 归并"完整解码链路。

## 精讲目录

| # | 文件 | 行数 | 主题 | 链接 |
|---|------|------|------|------|
| 1 | `flash_mla/flash_mla_interface.py` | 435 | Python 唯一门面：sched_meta 惰性初始化与复用校验、dense/sparse 双路径、FP8 潜在 KV 656B 布局、FlashAttn varlen autograd 兼容层 | [01-flash_mla_interface-Python门面层.md](01-flash_mla_interface-Python门面层.md) |
| 2 | `csrc/api/sparse_decode.h` | 495 | C++ 分派中枢：DecodeFeatures 特征集、四实现类（Sm90/Sm100-Head64/Head64x2/Head128）、Head64x2 指针平移拼 128 头、三段流水编排 | [02-sparse_decode.h-Cpp分派中枢.md](02-sparse_decode.h-Cpp分派中枢.md) |
| 3 | `csrc/smxx/decode/get_decoding_sched_meta/get_decoding_sched_meta.cu` | 116 | 瓦片调度器：单 warp 贪心等额装箱，把不等长序列切成 num_sm_parts 份 SE 线索引，产出 DecodingSchedMeta + num_splits 前缀和 | [03-get_decoding_sched_meta.cu-瓦片调度器.md](03-get_decoding_sched_meta.cu-瓦片调度器.md) |
| 4 | `csrc/smxx/decode/combine/combine.cu` | 230 | splitKV 归并：warp-per-head 在线 softmax 跨 split 合并、exp2/log2 域运算、PDL 程序化依赖启动、MAX_SPLITS 编译期阶梯、attn_sink 融合 | [04-combine.cu-splitKV归并.md](04-combine.cu-splitKV归并.md) |

## 核心模式速览

- **MLA 潜在 KV**：MQA 化（h_k=1）+ head_dim 576（NoPE 512 + RoPE 64）与 head_dim_v 512 分离；FP8 模式只压 NoPE 段（512B）+ 4 组 fp32 scale（16B），RoPE 段保 bf16（128B），共 656B/token。
- **分块 KV（paged KV）**：`block_table + cache_seqlens` 管理页式 KV；稀疏模式改用 `indices` 直接给 token 级地址（`block_idx*block_size + offset`）。
- **splitKV 两阶段**：调度器均衡切分 → 各 SM 独立算部分和（fp32 o_accum/lse_accum）→ combine 按全局 LSE 加权归并，单 split 序列短路。

## 建议阅读顺序

按编号 1→2→3→4 读，正好沿一次解码调用的调用栈下行：Python 断言层 → 架构分派 → 负载装箱 → 数值归并。每篇开头标注原文件相对路径与行数，六节结构（角色定位/内部结构/外部连接/数据流/设计决策/新人提示），全部基于真实源码，无臆造 API。

*生成：2026-09-05，基于仓库知识图谱（273 节点/11 步 tour）挑选。*

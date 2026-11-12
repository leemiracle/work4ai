# FlashMLA 新人指南（简版）

> 依据仓库 knowledge-graph（273 节点/442 边/9 层/11 步导览）与 README 整理。图谱位于仓内 `.understand-anything/knowledge-graph.json`。

## 一、项目是什么与定位

FlashMLA 是 DeepSeek 官方开源的 **MLA（Multi-head Latent Attention）高性能注意力内核库**，驱动 DeepSeek-V3 与 V3.2-Exp 模型的推理与训练，是 FlashAttention 2/3 思路在 MLA 上的专精实现。内核矩阵覆盖稀疏/稠密 × prefill/解码四象限：稀疏内核支撑 DeepSeek Sparse Attention（DSA，V3.2 的 token 级稀疏注意力，prefill 含 TopK 选取两遍式实现、解码配 FP8 KV cache）；稠密内核覆盖 prefill（SM100 MHA，NVIDIA 贡献的 CUTLASS 3.x FMHA，前向+反向）与解码（SM90 MQA splitKV）。性能标杆：H800 上稠密解码 3000 GB/s 带宽（memory-bound）/660 TFLOPS（compute-bound），稀疏 prefill 640 TFLOPS（H800）、1450 TFLOPS（B200）。术语上注意 MLA 两种模式：MQA 模式即 `head_dim_k`=576、`head_dim_v`=512（V3 系列解码形态），MHA 模式为 `head_dim_k`=192/128、`head_dim_v`=128（SM100 prefill 形态），详见 V3.2 论文附录。配套两篇官方 deep-dive 博客（docs/ 下）是第一手学习材料。仓库另含 MetaX/摩尔线程/海光/AMD 等社区移植入口。

## 二、架构分层（按图谱 9 层）

图谱 9 层，可归为四个带：

- **工程与接口带（L1-L3）**：项目文档与构建配置（README、两篇 deep-dive、setup.py、cutlass 子模块）；Python 接口与基准层（公开 API + autograd 封装 + 官方基准脚本）；C++ 公共接口与分派层（`csrc/api` 的 pybind 绑定与五个 `*_fwd/decode.h` 分派头，按架构 SM90/SM100 × 头维 64/128 × 稀疏/稠密 × 精度 BF16/FP8 路由到具体内核）。
- **共享设施带（L4-L5）**：kerutils CUDA 设备原语库（git 子模块，头文件-only，SM80/90/100 三代专化原语）；跨架构共享组件 smxx（解码 tile scheduler 元数据生成 + splitKV 结果归并 combine 内核）。
- **内核带（L6-L8）**：SM90 Hopper 内核（decode 的 splitKV MLA head64 稠密主线 + FP8 稀疏变体、prefill 的 FP8 稀疏注意力）；SM100 Blackwell 解码内核（head64/head64x2/head128 家族）；SM100 prefill 内核（CUTLASS dense FMHA + 稀疏 fwd + 小 TopK 特化）。
- **L9 测试框架与 kernelkit 工具**：pytest 正确性套件、纯 PyTorch naive 参考实现与 bench/compare 工具箱。

一句话调用链：Python API（get_mla_metadata → flash_mla_with_kvcache）→ pybind → 分派头按架构/头维/精度路由 → SM90/SM100 内核（kerutils 原语内联支撑）→ smxx combine 归并输出。

## 三、核心模块（每层 1-2 个）

| 层 | 代表模块 | 职责 |
|---|---|---|
| L1 | `setup.py`、`docs/*deep-dive.md` | arch flags（90a/100f）编译；官方内核逐行解读 |
| L2 | `flash_mla/flash_mla_interface.py`、`benchmark/bench_flash_mla.py` | 三大公开 API + FlashAttnVarlenFunc autograd；四路径（SDPA/CUDA/FlashInfer/Triton）基准 |
| L3 | `csrc/api/api.cpp`、`sparse_decode.h` | pybind 绑定 5 函数；Decode_Sm90/Sm100_Head64/Head64x2/Head128 路由表 |
| L4 | `kerutils/device/sm100/{intrinsics,gemm}.cuh` | 头文件-only 设备原语：tcgen05/tmem/TMA 封装 |
| L5 | `get_decoding_sched_meta.cu`、`combine.cu` | 生成 tile scheduler 元数据（SE 曲线索引）；splitKV 部分结果 LSE 加权归并 |
| L6 | `sm90/decode/dense/splitkv_mla.cuh`、`sparse_fp8/components/dequant.h` | Hopper 稠密解码主内核（1355 行，双 warpgroup O_L/O_R 拆分）；FP8→BF16 反量化 |
| L7 | `sm100/decode/head64/kernel.cuh`、`config.h` | Blackwell 持久化解码主内核（968 行，tcgen05 UTCMMA）；V32/MODEL1 编译期配置 |
| L8 | `sm100/prefill/dense/`（collective/mainline）、`sparse fwd` | CUTLASS 3.x FMHA（fwd+bwd，NVIDIA 贡献）；稀疏 prefill k512/k576 实例化 |
| L9 | `tests/lib.py`、`tests/kernelkit/` | naive attention 参考实现 + KVScope 分页 KV 模拟；bench/compare/precision 工具箱 |

## 四、快速上手

**环境**：SM90/SM100 GPU；CUDA ≥12.8（SM100 内核需 12.9+）；PyTorch ≥2.0。

```bash
git clone https://github.com/deepseek-ai/FlashMLA.git flash-mla
cd flash-mla
git submodule update --init --recursive   # 必须拉 kerutils/cutlass 子模块
pip install -v .
```

**解码用法**（先一次元数据，循环内调内核）：

```python
from flash_mla import get_mla_metadata, flash_mla_with_kvcache
tile_scheduler_metadata, num_splits = get_mla_metadata(
    cache_seqlens, s_q * h_q // h_kv, h_kv, h_q, is_fp8, topk)
o_i, lse_i = flash_mla_with_kvcache(
    q_i, kvcache_i, block_table, cache_seqlens, dv,
    tile_scheduler_metadata, num_splits,
    is_causal, is_fp8_kvcache, indices)   # indices 传入即 token 级稀疏
```

稀疏 prefill 用 `flash_mla_sparse_fwd(q, kv, indices, sm_scale)`（无 batch 维，多 batch 需 reshape）；稠密 MHA prefill 用 `flash_attn_varlen_func` 家族（用法同 flash_attn 包）。解码与 prefill 均返回 `(out, lse)`（prefill 另含 max_logits），lse 为每个 query 头的 log-sum-exp；稀疏 `indices` 张量形状 `(batch, s_q, topk)`，页号已编码进索引故无需 block_table，无效项置 `-1`。FP8 KV cache 每token 656B：512B NoPE（FP8）+16B scale（4×FP32）+128B RoPE（BF16 不量化），量化细节见 `tests/quant.py`。

**测试与基准**：`python tests/test_flash_mla_dense_decoding.py`、`test_flash_mla_sparse_decoding.py`、`test_fmha_sm100.py`、`test_flash_mla_sparse_prefill.py`；基准对比跑 `benchmark/bench_flash_mla.py`。

## 五、学习路径（按图谱 11 步 Tour）

1. **全局观**：README + 两篇 deep-dive，记住两个数字：Hopper 解码 3000 GB/s / 580 GB/s 带宽墙语境与 660 TFLOPS。
2. **Python API**：三个入口各司其职——get_mla_metadata 出调度元数据、flash_mla_with_kvcache 解码、flash_mla_sparse_fwd 稀疏 prefill；FlashAttnVarlenFunc 补训练反传。
3. **C++ 分派**：api.cpp 绑定 5 函数，五个 `*_fwd/decode.h` 头构成"架构-头维-精度"路由表，是浏览内核的地图。
4. **共享组件**：params.h 的 FlashMLAParams、smxx 的元数据生成与 combine——所有解码内核的公共依赖，先读再看内核。
5. **kerutils**：三代架构原语库，性能细节第一现场，遇到看不懂的设备代码回来查这里。
6. **SM90 解码主线**：splitkv_mla.cuh 把 KV 切 64 份并行部分 softmax 再归并；对照 traits.h 的 MMA 布局与 2025-04 博客的乒乓调度。
7. **SM90 FP8 稀疏**：dequant 组件反量化参与 softmax；prefill 侧两遍式 TopK 8192；配套 2025-09 博客有逐行解读。
8. **SM100 解码**：head64 两代模型实例化 + Head64x2 双份变体 + head128，看 kernel.cuh 的持久化 tcgen05 实现。
9. **SM100 prefill**：CUTLASS dense FMHA 自底向上组装（collective→mainline→kernel→device），与稀疏 fwd/小 TopK 特化对照。
10. **正确性防线**：tests/lib.py 的 naive 参考实现是行为的最终定义，四套 pytest 覆盖全内核矩阵。
11. **性能验证**：bench 脚本内置 Triton 参考实现，跑通四路径对比即完成入门闭环。

建议节奏：第 1-5 步一天建立地图（配合两篇博客），第 6-7 步精读 Hopper 主线（核心投入），第 8-9 步按目标架构选读，第 10-11 步动手跑通验证。

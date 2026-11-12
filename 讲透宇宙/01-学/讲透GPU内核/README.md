# 讲透GPU内核（D4 学区首单元 · 2026-11-12 孵化）

> 知识地图治理清单"学区断层"第三单元（继 [讲透集合通信](../讲透集合通信/README.md)/[讲透推理服务](../讲透推理服务/README.md) 之后）：D4 编译与内核层此前零教学单元，本单元从 02-透 区代表作 [讲透Triton](../../02-透/讲透Triton/README.md)/[讲透FlashMLA](../../02-透/讲透FlashMLA/README.md)/[讲透DeepGEMM](../../02-透/讲透DeepGEMM/README.md) 反向蒸馏成五幕教学体。

## 篇目表

| 幕 | 文件 | 一句话 |
|---|---|---|
| 一 · 直觉 | [01-直觉-为什么要手写内核.md](01-直觉-为什么要手写内核.md) | 框架算子的隐形税：launch 开销+中间张量物化 |
| 二 · 数学 | [02-数学-roofline与重用.md](02-数学-roofline与重用.md) | 屋脊公式 + tiling 把访存降为 1/tile 的重用数学 |
| 三 · 代码 | [03-代码-roofline与tiling真跑.md](03-代码-roofline与tiling真跑.md) | 双实验真跑：decode vs prefill 物理断层 + 访存 1/256 |
| 四 · 不足 | [04-不足-手写内核的代价.md](04-不足-手写内核的代价.md) | 数值一致性、平台特异性、可移植性地狱 |
| 五 · 应用 | [05-应用-从FlashAttention到国产栈.md](05-应用-从FlashAttention到国产栈.md) | 融合的胜利、FP8 GEMM、TileKernels/mHC、TIRx |

## 核心数字速览（来自 03 幕真跑）

| 实验 | 结果 |
|---|---|
| 7B decode roofline | 强度 1.0 FLOP/B vs A100 屋脊 153 → memory-bound（带宽口 6.87ms = 算力口的 172 倍） |
| 7B 4K prefill | 强度 3134 FLOP/B → compute-bound（同一模型，两种物理问题） |
| tiling L=1024 | tile=256 时访存降为 naive 的 **1/256**（与理论精确一致，数值抽验 allclose ✓） |

## 素材源（证据锚点）

- [讲透Triton](../../02-透/讲透Triton/README.md)（GPU kernel DSL+52 页）、[讲透DeepGEMM](../../02-透/讲透DeepGEMM/README.md)（FP8 分组 GEMM）、[讲透FlashMLA](../../02-透/讲透FlashMLA/README.md)（MLA 注意力 kernel，KV 协议 656B→528B/FP4 演进）
- [讲透TileKernels](../../02-透/讲透TileKernels/README.md)（Tile 级 kernel+mHC 论文落地，torch.equal 位级断言）、[讲透TIRx](../../02-透/讲透TIRx/README.md)（沐曦 kernel 库，图谱金标准首例）、[讲透FlagGems](../../03-查/讲透FlagGems/deepwiki/INDEX.md)

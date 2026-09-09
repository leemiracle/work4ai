# 视角1

> Roofline Model（compute/memory bound）
> 自动生成: 2026-06-30 13:34  机器: greatwall-pc / Phytium D3000

# Lens 1: Roofline Model

## 1.1 实测各级内存带宽

| 层级 | 工作集 | 实测带宽 |
|---|---|---|
| L1D | 4 KB | 77.6 GB/s |
| L1D+ | 32 KB | 79.4 GB/s |
| L2 | 256 KB | 72.5 GB/s |
| L2+ | 4032 KB | 26.5 GB/s |
| L3+ | 16384 KB | 26.8 GB/s |
| DRAM | 65536 KB | 23.1 GB/s |

## 1.2 各算子 Arithmetic Intensity + Roofline 预测

D3000 峰值：FP32=40 GFLOPS, DRAM BW=23.1 GB/s
Memory-bound 上限 = DRAM_BW × AI；Compute-bound 上限 = peak

| 算子 | AI (FLOPs/B) | Roofline 上限 | 实测 GFLOPS | 性质 |
|---|---|---|---|---|
| GEMM 1024³ (FP32) | 170.7 | 40.0 GFLOPS | 39.45 | compute-bound ✓ |
| GEMM 64³ (FP32) | 10.7 | 40.0 GFLOPS | 39.45 | transitional |
| GEMM 2048³ (FP32) | 341.3 | 40.0 GFLOPS | 30.00 | compute-bound ✓ |
| Conv im2col (CIN=64, 3×3) | 286.4 | 40.0 GFLOPS | 7.63 | compute-bound ✓ |
| Winograd F(2,3) | 12544.0 | 40.0 GFLOPS | 18.13 | compute-bound ✓ |
| Winograd F(4,4) | 3136.0 | 40.0 GFLOPS | 26.19 | compute-bound ✓ |
| Elem-wise add | 0.1 | 1.9 GFLOPS | 1.00 | memory-bound |
| Attention N=1024 | 32.0 | 40.0 GFLOPS | 3.23 | transitional |

## 1.3 关键洞察

- GEMM 1024³ AI=1024，远超 DRAM/peak 交叉点 → **compute-bound**
- Winograd F(4,4) AI=1（高复用）→ compute-bound，故能达 26 GFLOPS
- Element-wise AI=0.08 → 纯 memory-bound，性能受带宽限制
- GEMM 64³ AI=64 但工作集 16KB 装得下 L1（BW 高）→ 仍可接近 peak
- GEMM 2048³ 工作集 48MB 超 L3 → 走 DRAM，AI 仍高但实际掉到 30 GFLOPS

**工程结论**：算子优化方向取决于 bound 性质
- compute-bound → 增强 ILP（MR=8、4 FVU 全开）
- memory-bound → 数据布局、prefetch、分块复用

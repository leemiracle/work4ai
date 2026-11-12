# 三 · 代码：roofline 与 tiling 真跑

> [roofline_tiling.py](roofline_tiling.py)（120 行，纯 NumPy/stdlib）两个实验把 02 幕公式变成可执行输出。以下全部为 2026-11-12 真跑结果。

## 3.1 实验 1：屋脊判定（GPU 参数表内置 A100/H100/B200）

```python
GPUS = {'A100': (312, 2039), 'H100': (990, 3350), 'B200': (2250, 8000)}  # TFLOPS, GB/s
def roofline(name, flops, moved_bytes):
    ai = flops / moved_bytes
    ridge = peak_t * 1e12 / (peak_bw * 1e9)
    bound = 'compute' if ai >= ridge else 'memory'
```

真跑输出（7B 模型 FP16）：

```
[A100] 强度 1.0 FLOP/B vs 屋脊 153 → memory-bound, T≥6.87 ms (算力口 0.04 / 带宽口 6.87)
[A100] 强度 3134.4 FLOP/B vs 屋脊 153 → compute-bound, T≥183.79 ms (算力口 183.79 / 带宽口 8.97)
[H100] 强度 1.0 FLOP/B vs 屋脊 296 → memory-bound, T≥4.18 ms
```

第一行是 decode（移动 $2P$ 权重字节、做 $2P$ FLOPs，强度恒 1.0——与模型大小无关！）；第二行是 prefill $s{=}4096$（权重一遍+激活流 $4sdL$）。**同一模型、同一批权重，屋脊把前向切成两种物理问题**——这个输出就是 [讲透推理服务](../讲透推理服务/README.md) 05 幕 P/D 分离产业架构的全部理论依据。

顺带一个真踩的坑：本模拟器初版把 prefill 激活字节写成 `0.1*P*s`（无意义量纲），跑出来 prefill 被判 memory-bound——**公式错了输出不会报错，只会安静地说谎**；修正为 $4sdL$ 后才符合"长 prompt 吃满算力"的物理直觉。这正是 02.5 节"roofline 是下界推导不是实测"的另一面：输入账目错，结论全错。

## 3.2 实验 2：tiling 访存对账（理想缓存模型）

```python
naive = 2 * L ** 3                                  # 每次乘加读 2 标量
blocks = (L // tile) ** 2
tiled = blocks * 2 * tile * L                       # 行块/列块驻留后被重用 tile 次
```

真跑输出（$L=1024$，缓存可驻留 400 万元素）：

| tile | naive 读 | tiled 读 | 实测降幅 | 理论 |
|---|---|---|---|---|
| 32 | 2.15G | 0.07G | 1/32 | 1/32 ✓ |
| 64 | 2.15G | 0.03G | 1/64 | 1/64 ✓ |
| 128 | 2.15G | 0.02G | 1/128 | 1/128 ✓ |
| 256 | 2.15G | 0.01G | 1/256 | 1/256 ✓ |

**四档精确吻合**——重用数学不是近似，是整数层面可对账的恒等式。每档同时用 NumPy 分块 matmul 做数值抽验（`np.allclose(C, C_ref)` 全过）：**重排计算顺序不改变结果**，但真实硬件上浮点结合序不同会有 ULP 级差异（04 幕的坑）。

## 3.3 从模拟器到真实 kernel 的三级台阶

1. **本模拟器**：理想缓存+标量计数，证明重用恒等式；
2. **Triton**：把 tiling 写成 GPU 程序——`tl.load` 一个块进 SRAM、`tl.dot` 在块上算、循环累积（[讲透Triton](../../02-透/讲透Triton/README.md) 是这条学习线的正门：block pointer/autotune/pipelining）；
3. **手写 CUDA/PTX 级**：tile 大小对着 warp/tcgen05 张量核心形状精算、异步拷贝双缓冲、TMA 批量搬运（[讲透DeepGEMM](../../02-透/讲透DeepGEMM/README.md)/[讲透FlashMLA](../../02-透/讲透FlashMLA/README.md) 的实战现场）。

模拟器证明了"为什么"，Triton 演示了"怎么写"，手写层展示"极限在哪"——三级台阶缺一不可跳。

📌 下一步 → [04-不足：手写内核的代价](04-不足-手写内核的代价.md)

✍️ 练习：把模拟器 GPU 表加进你手头的卡（查规格书填 TFLOPS/GB/s），算它的屋脊点；再用 `torch.cuda.get_device_properties` 实测你的卡跑 GEMV 与 GEMM 的实际强度，看落在屋脊图哪一侧。

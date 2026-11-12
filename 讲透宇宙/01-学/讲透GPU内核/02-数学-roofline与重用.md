# 二 · 数学：roofline 与重用

## 2.1 屋脊模型：一张图判生死

任何 kernel 的时间下界由两条"屋顶"压住：

$$T \ge \max\left(\frac{F}{\Pi_{compute}},\; \frac{M}{\Pi_{bw}}\right)$$

$F$=浮点运算量，$M$=移动字节数，$\Pi$=硬件峰值。定义**算术强度** $AI = F/M$（FLOP/B）与**屋脊点** $R = \Pi_{compute}/\Pi_{bw}$：

- $AI < R$：**memory-bound**——时间由带宽决定，算力在闲着；
- $AI > R$：**compute-bound**——时间由算力决定，带宽在闲着。

代入 A100（FP16 算力 312 TFLOPS / HBM 2 TB/s）：$R = 153$ FLOP/B。FP16 GEMM 每 2 字节能做 $2s$ 次乘加（$s$=矩阵边长）——$s=4096$ 时 $AI = s = 4096 \gg 153$，纯 GEMM 天生 compute-bound；而逐元素算子（GELU/加法）每 2 字节只做 1 FLOP，$AI=0.5$——天生 memory-bound。**融合的数学本质：把 $AI=0.5$ 的算子挂到 $AI=4096$ 的 GEMM 尾巴上，让它蹭带宽的顺风车。**

## 2.2 实例：同一模型，两种物理

7B 模型 FP16（[03 幕](03-代码-roofline与tiling真跑.md)真跑数字）：

| 场景 | 移动字节 | 强度 | A100 判定 | 时间下界 |
|---|---|---|---|---|
| decode 单 token | $2P = 14$GB | **1.0** | memory | 6.87 ms（带宽口=算力口 172 倍） |
| prefill $s=4096$ | $2P + 4sdL \approx 18$GB | **3134** | compute | 183.79 ms（算力口=带宽口 20 倍） |

这就是 [讲透推理服务](../讲透推理服务/02-数学-吞吐定律与KV账本.md) 02.3 节 P/D 分离的全部物理基础——**同一份权重，decode 是带宽生意，prefill 是算力生意**，一份 roofline 账本推出一个产业架构。

## 2.3 tiling 的重用数学：访存降为 1/tile

矩阵乘 $C = AB$（边长 $L$）：naive 三重循环里 $A[i,k]$ 每次用到都从内存读——总读次数 $2L^3$。**分块（tiling）**把 $C$ 切成 $tile \times tile$ 子块，每块计算时把 $A$ 的行块（$tile \times L$）与 $B$ 的列块（$L \times tile$）驻留缓存，被重用 $tile$ 次：

$$M_{tiled} = \left(\frac{L}{tile}\right)^2 \cdot 2 \cdot tile \cdot L = \frac{2L^3}{tile}$$

访存降为 naive 的 $\frac{1}{tile}$。约束：**驻留集 $2 \cdot tile \cdot L$ 必须塞进缓存**——tile 越大重用越好、但缓存放不下就前功尽弃。这就是真实 GEMM kernel 里 tile 大小要对着 shared memory 容量（A100 194KB/SM）精打细算的原因。

注意边界：重用收益以 tile 为单位兑现，所以 kernel 的 tile 选择= 2.1 节 roofline 的实践形态——**把 $AI$ 从 0.5 推过屋脊点的每一步都来自重用**。

## 2.4 从 tiling 到 FlashAttention：online softmax 的两步走

FA 的难点比 GEMM 多一层：softmax 分母依赖全行最大值与总和，理论上要扫两遍——但分母可以**增量修正**：

$$m_{new} = \max(m_{old}, m_{tile}), \quad l_{new} = e^{m_{old}-m_{new}} l_{old} + \sum_{tile} e^{x - m_{new}}$$

每处理一个 KV 块就更新一次 $(m, l)$，已输出的部分和用 $\exp(m_{old}-m_{new})$ 重标定。**数学上的可交换性（最终结果不变）换来访存上的 $O(s)$**——这是"算法改造配合 kernel 设计"的范式：光会 tiling 不够，要找到允许单遍扫的数学形式。

## 2.5 适用边界

- roofline 用**峰值**做下界，真实 kernel 只能逼近（80-90% 已是优秀）；DRAM 实测带宽（A100 ~1.6-1.9TB/s 有效）比标称低；
- 多算子的端到端网络层，瓶颈可能在launch 间隙/同步，roofline 只覆盖"在算的时段"；
- 对 decode GEMV 类，shared memory tiling 帮助有限（没有行重用可挖），优化转向权重布局（w4a8 量化、kernel 融合把 norm/激活挂上）——强度公式告诉你"别在 tiling 上白费力气"。

📌 下一步 → [03-代码：roofline 与 tiling 真跑](03-代码-roofline与tiling真跑.md)

✍️ 练习：用 2.3 公式算 A100 上 $L=8192$、shared memory 194KB（FP16 可驻留 ~9.7 万元素）下 $tile$ 的可行上限；对照 H100（228KB）看代际变化对 tile 策略的影响。

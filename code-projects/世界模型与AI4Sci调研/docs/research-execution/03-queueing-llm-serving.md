# 课题 PR-5 第一个结果：排队论分析 LLM Serving

> 对应课题：`docs/research-topics-50.md` PR-5 / `docs/learning-paths.md` 路径 3
> 关联章节：模块 12 §05 §14.3 排队论分析

---

## 1. 问题

LLM serving 本质是排队系统。把 vLLM 副本建模为 M/G/1（泊松到达 + 一般服务时间 + 单服务台），问：**服务时间方差 σ_S 如何影响等待时间？continuous batching 的排队论机制是什么？**

## 2. 理论

**Pollaczek-Khinchine 公式**：$W_q = \frac{\lambda \cdot \mathbb{E}[S^2]}{2(1-\rho)}$，其中 $\rho = \lambda \cdot \mathbb{E}[S]$，$\mathbb{E}[S^2] = \mathbb{E}[S]^2 + \sigma_S^2$

关键：$W_q$ 直接依赖 $\sigma_S^2$——**方差越大，等待越长**。

## 3. 实验

λ=20 req/s, E[S]=0.04s, ρ=0.80, 扫描 σ_S ∈ [0.01, 0.10]

## 4. 结果

| σ_S | 理论 W_q | 模拟 W_q | P99 | 重尾倍数 |
|---|---|---|---|---|
| 0.01 | 85ms | 82ms | 373ms | 基准 |
| 0.02 | 100ms | 104ms | 517ms | 1.2× |
| 0.05 | 205ms | 451ms | 2374ms | 2.4× |
| 0.06 | 260ms | 1214ms | 4138ms | 3.1× |
| 0.08 | 400ms | 58582ms | 115463ms | 4.7× |
| 0.10 | 580ms | 134943ms | 271751ms | 6.8× |

## 5. 发现

1. **σ ≤ 0.05 时理论吻合**（比值 0.96-2.2×），**σ > 0.05 时模拟严重偏离**（比值 146-233×）——因为 ρ=0.80 接近饱和，高方差导致系统"偶尔卡住"后无法恢复。**这是 M/G/1 稳态假设的失效边界。**

2. **方差增 10×（0.01→0.10），等待时间增 ~7×（理论）但模拟增 1600×（实际）**——接近饱和时，方差的影响非线性放大。

3. **P99 是平均的 5×**（σ=0.05 时：平均 451ms，P99 2374ms）——**只看平均延迟严重低估用户体验**。

4. **M/M/1（指数服务）的 W_q 是 M/D/1（确定性服务）的 2×**——服务时间方差减半，等待也减半。

## 6. continuous batching 的排队论解释

```
传统 serving（FIFO）= M/G/1 with 重尾
  - 少数超长请求（长 prefill + 长 decode）让后面所有请求排队等
  - σ_S 大 → W_q 大

continuous batching = 把"服务"从"整个请求"改为"一个 decode step"
  - 每个 decode step 的服务时间几乎相同（σ_S → 0）
  - M/G/1 → M/D/1
  - W_q 减半

prefill-decode 分离 = 进一步把 prefill（compute-bound）和 decode（memory-bound）分到不同队列
  - 长 prefill 不阻塞短 decode
  - 两个独立的 M/D/1，各自的 σ 更小
```

## 7. Gap

- σ > 0.05 时理论与模拟偏离的理论解释：是否是 M/G/1 稳态假设失效？还是模拟样本量不够（20000 可能不够覆盖重尾）？
- 真实 vLLM trace 的 σ_S 是多少？（需要生产数据）
- continuous batching 后的等效 σ_S 能否从架构参数预测？

## 8. 工程直觉

| 排队论概念 | 工程直觉 |
|---|---|
| 重尾方差 $\sigma_S^2$ | 少数超长请求让所有人等 |
| ρ → 1 | 系统接近饱和，方差影响非线性放大 |
| continuous batching | 把"按请求排队"改为"按 token 轮流" |
| prefill-decode 分离 | 长 prefill 不阻塞短 decode |
| P99 vs 平均 | 用户感知的是 P99，不是平均 |

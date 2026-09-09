# VAE 数学精读：变分推断 + ELBO + 重参数化

> 参照：Kingma & Welling 2013 / Auto-Encoding Variational Bayes
>
> csdiy 对应：tinygen/vae.py + loss-functions精读 + backprop-graph精读

---

## 一、问题：生成模型的核心难题

```
真实数据分布 p(x) 未知 → 无法直接采样

自编码器（AE）:
  编码器 x → z → 解码器 z → x̂
  问题: z 空间不连续 → 无法从 z 采样生成新数据

VAE 的解法:
  编码器输出分布 q(z|x) → 从分布采样 z → 解码器生成 x
  z 空间连续 → 可以从 N(0,I) 采样生成新数据
```

---

## 二、变分推断：为什么不能直接优化 p(x)

### 对数似然

```
log p(x) = log ∫ p(x|z) p(z) dz

→ 对 z 的积分无法解析求解（高维）
```

### 证据下界（ELBO）

```
log p(x) ≥ ELBO = E_{q(z|x)}[log p(x|z)] - KL(q(z|x) || p(z))

① 重建项: E[log p(x|z)] → 解码器从 z 重建 x 的质量
② 正则项: KL(q(z|x) || N(0,I)) → 编码器输出接近标准正态

→ 最大化 ELBO = 最大化重建 + 最小化 KL
```

### ELBO 推导

```
log p(x) = log ∫ p(x,z) dz
         = log ∫ p(x,z) × q(z|x) / q(z|x) dz
         = log E_{q(z|x)}[p(x,z) / q(z|x)]

Jensen 不等式:
  ≥ E_{q(z|x)}[log p(x,z) / q(z|x)]
  = E_{q(z|x)}[log p(x|z)] + E_{q(z|x)}[log p(z) / q(z|x)]
  = E_{q(z|x)}[log p(x|z)] - KL(q(z|x) || p(z))
  = ELBO
```

---

## 三、重参数化技巧（Reparameterization Trick）

### 问题：采样不可微

```
z ~ q(z|x) = N(μ(x), σ(x))
z = μ + σ × ε,  ε ~ N(0,I)

如果直接 z = sample(N(μ, σ)):
  → 采样操作没有梯度 → 无法反向传播
```

### 解法：把随机性移到外面

```
z = μ + σ × ε   （ε 是独立于参数的随机变量）

∂z/∂μ = 1       ← 可微！
∂z/∂σ = ε       ← 可微！

→ 梯度可以通过 z 回传到 μ 和 σ
→ 这就是 "重参数化技巧"
```

### 代码（参照 tinygen/vae.py）

```python
def reparameterize(self, mu, logvar):
    sigma = [math.exp(0.5 * lv) for lv in logvar]
    eps = [random.gauss(0, 1) for _ in range(len(mu))]
    return [m + s * e for m, s, e in zip(mu, sigma, eps)], sigma
```

---

## 四、KL 散度的闭式解

### 当 q(z|x) 和 p(z) 都是高斯时

```
q(z|x) = N(μ, σ²)
p(z)   = N(0, 1)

KL(q || p) = 0.5 × Σ (μ² + σ² - log(σ²) - 1)
```

### 推导

```
KL(N(μ,σ²) || N(0,1))
= ∫ N(μ,σ²) × log(N(μ,σ²) / N(0,1)) dz
= 0.5 × (μ² + σ² - log(σ²) - 1)
```

→ 这就是 VAE 损失函数中的 KL 项（闭式解 → 不需要蒙特卡洛估计）。

---

## 五、β-VAE（可控的 KL 权重）

```
ELBO_β = E[log p(x|z)] - β × KL(q(z|x) || p(z))

β=1: 标准 VAE
β>1: 更强的 KL 惩罚 → z 更接近 N(0,I) → 生成质量降但解耦更好
β<1: 更弱的 KL → 重建更好但生成多样性降
```

---

## 六、VAE vs AE vs GAN vs Diffusion

| 维度 | AE | VAE | GAN | DDPM |
|------|----|-----|-----|------|
| 潜空间 | 不连续 | **连续** | 连续 | 连续 |
| 生成 | ❌ | ✅ | ✅ | ✅ |
| 训练 | 稳定 | 稳定 | **不稳定** | 稳定 |
| 质量 | 差 | 中 | 好 | **最好** |
| 速度 | 快 | 快 | 快 | 慢 |
| 数学 | 简单 | **变分推断** | 博弈论 | 随机微分 |

---

## 七、一句话总结

> VAE = 编码器输出分布（不是点）+ 重参数化让采样可微。
>
> ELBO = 重建质量 + KL 正则（让 z 空间连续 → 可生成）。
>
> 重参数化技巧：z = μ + σ·ε → 梯度通过 μ, σ 回传。
>
> **VAE 是变分推断 + 深度学习的完美结合——用神经网络参数化概率分布。**

---

*配套：tinygen/vae.py（`../projects/tinygen/vae.py`） | loss-functions精读（`loss-functions-精读.md`） | backprop-graph精读（`backprop-graph-精读.md`）*

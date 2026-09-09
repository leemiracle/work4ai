# Sessa 深度分析：attention 嵌入 recurrent feedback 的拓扑创新

> arXiv:2604.18580（2026-04，LibratioAI / Liubomyr Horbatko）
> 核心：把 attention 嵌入 recurrent feedback path，而非 interleave

## TL;DR

Sessa 提出了 attention-SSM 混合的**第三种拓扑**：不是 interleave（Jamba）、不是 replace（Mamba），而是**嵌套**——把 attention 放在 recurrent feedback 环里。理论上证明了 $O(\ell^{-\beta})$（$\beta < 1$）的 power-law memory tail，比 Transformer 的 $O(1/\ell)$ 和 Mamba 的 exponential decay 都慢。是 2026 年长上下文架构的理论突破。

---

## 1. 三种 hybrid 拓扑对比

| 拓扑 | 代表 | 结构 | 信息流 |
|---|---|---|---|
| **Interleave** | Jamba / Zamba | [Transformer 层] → [Mamba 层] → ... | 串行：层间传递 |
| **Replace** | Mamba | 全用 SSM，无 attention | 单一递推 |
| **Nest（Sessa）** | Sessa | attention 在 recurrent feedback 环里 | 嵌套：attention 操作已经变换过的 state，结果再反馈 |

关键差异：**interleave 的 attention 和 SSM 各管一段（不共享 state）；Sessa 的 attention 操作的是 SSM 已变换的 state，且结果反馈回 SSM**。

---

## 2. 理论核心：power-law memory tail

### 2.1 三种衰减律

| 架构 | 记忆影响衰减 | 含义 |
|---|---|---|
| Transformer（diffuse attention）| $O(1/\ell)$ | token 距离 $\ell$ 越远，影响线性衰减 |
| Mamba（failed freeze-time）| exponential | 指数衰减（很快忘记）|
| **Sessa** | **$O(\ell^{-\beta})$，$0 < \beta < 1$** | **幂律衰减（比 1/ℓ 慢）** |

### 2.2 为什么 power-law 比 1/ℓ 慢

$\ell^{-\beta}$ 当 $\beta < 1$ 时，比 $\ell^{-1}$ 衰减慢。例如 $\beta = 0.5$：
- $\ell = 100$：$100^{-0.5} = 0.1$ vs $100^{-1} = 0.01$（Sessa 的影响大 10×）
- $\ell = 10000$：$10000^{-0.5} = 0.01$ vs $10000^{-1} = 0.0001$（大 100×）

**直觉解释**：在 Sessa 里，一个旧 token 到当前 token 有**多条 attention-based 路径**（因为 attention 在 feedback 环里被多次激活），而标准 Transformer 只有一条（单次 attention read）。多路径让旧信息有更多"存活机会"。

### 2.3 唯一实现 distance-invariant retrieval

在显式假设下，Sessa 是唯一能实现"影响不随距离衰减"的架构类——即 $\beta \to 0$ 的极限。Transformer 和 Mamba 都做不到。

---

## 3. Sessa 的 mixer 结构

```
输入 x → [gated-MLP block wrapping recurrent mixer]
                  │
                  ├─ forward causal attention → forward signal f
                  │
                  └─ feedback attention → weights over strict past
                       ↓
                  feedback solve（causal，混合 past mixer outputs）
                  ↓
                  输出 s
```

核心：一个 gated-MLP block 里**同时包含 forward attention 和 feedback attention**，feedback solve 是一个因果（causal）的线性系统求解。

---

## 4. 实验结果（合成任务 + WikiText）

| 模型 | 参数 | WikiText-103 PPL | 长上下文 benchmark |
|---|---|---|---|
| Transformer baseline | 125M | 标准 | 衰减明显 |
| Mamba baseline | 125M | 略差于 Transformer | 衰减更明显 |
| **Sessa** | 125M | **与 Transformer 竞争** | **最强** |

**局限**：
- 只在 125M / 350M 参数验证
- 合成长上下文 benchmark 是自设计的，未在标准 long-context benchmark（如 RULER）上验证
- 理论假设（"subcritical diffuse-routing"）较强，实际是否满足未完全论证
- GitHub 代码已开源（LibratioAI/sessa），但社区复现结果尚少

---

## 5. 对长上下文架构设计的影响

### 5.1 挑战"interleave 是唯一 hybrid 路径"

Jamba 证明了 interleave 可行，但它没有理论保证"interleave 是最优的"。Sessa 证明了**嵌套拓扑在理论上更优**（power-law vs 1/ℓ）。这开启了新的设计空间。

### 5.2 与 KDA 的关系

Kimi K3 的 KDA（Delta-rule 线性 attention）是 interleave 路线的最新工业化。Sessa 是 nest 路线的理论先驱。如果 Sessa 的理论在更大规模上成立，未来的模型可能从 interleave（Jamba/K3）转向 nest（Sessa 风格）。

### 5.3 对模块 11 §07 §2.7 的更新

现有 §2.7 说"2026 的共识是混合（interleave）"。Sessa 挑战了这个共识——混合的方式（interleave vs nest）也很重要，甚至比"是否混合"更重要。

---

## 6. 来源

- [arXiv:2604.18580](https://arxiv.org/abs/2604.18580)（原始论文）
- [GitHub: LibratioAI/sessa](https://github.com/LibratioAI/sessa)（官方实现）
- [Groundy 解析](https://groundy.com/articles/sessa-breaks-the-mamba-or-transformer-binary-distance-invariant-retrieval/)（第三方深度分析）

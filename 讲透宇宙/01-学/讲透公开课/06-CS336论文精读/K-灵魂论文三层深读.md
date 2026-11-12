# K · 灵魂论文三层深读（8 篇 · 实验验证版）

> **本文档定位**：对 8 篇 ⭐⭐⭐ 灵魂论文做「直觉 → 数学 → **可运行实测**」三层讲透。
> 全部实验来自 [`experiments/verify_soul_papers.py`](./experiments/verify_soul_papers.py)（仅依赖 numpy，`python3` 直接跑），**以下输出均为真实运行结果**（存档于 [`experiments/OUTPUT.txt`](./experiments/OUTPUT.txt)，2026-08-14, numpy 2.2.6）。
>
> 这正是 CS336 的精神：**论文结论不是背出来的，是跑出来的**。

---

## K1 · Scaled Dot-Product Attention：为什么除以 √d_k

> 对应 [B1 Transformer (2017)](./B-Transformer架构.md#b1)

**直觉**：softmax 对输入尺度极敏感——logit 差 5 以上就近似 winner-take-all。点积是 $d_k$ 个乘加的和，维度越大方差越大，不缩放的话 attention 在训练初期就"过早自信"，梯度消失。

**数学**：设 $q, k$ 各分量独立、均值 0 方差 1，则 $\text{Var}(q\cdot k) = d_k$。除以 $\sqrt{d_k}$ 后方差回到 1。softmax 的回传梯度为 $\partial L/\partial \text{logit}_i \propto p_i(1-p_i)$，$p$ 接近 one-hot 时梯度→0。

**实测**（$d_k=128$，2000 个 key）：

```
未缩放: std= 11.37  softmax熵= 0.732  梯度量级∝p(1-p)=1.75e-04
÷√d_k: std=  1.00  softmax熵= 7.101  梯度量级∝p(1-p)=4.99e-04
理论: 未缩放 std = √d_k = 11.31；最大熵 = ln(2000) = 7.60
```

**读数**：未缩放 logits 的 std=11.37 与理论 $\sqrt{128}=11.31$ 吻合；softmax 熵从 0.73（近乎 one-hot）恢复到 7.10（接近最大熵 7.60）。**这一个除法就是把 attention 从"过早饱和"救回来的全部秘密**。

---

## K2 · RoPE：内积只依赖相对位置（数值证明）

> 对应 [B7 RoPE (2021)](./B-Transformer架构.md#b7)

**直觉**：把每个 2 维平面对旋转一个与位置成正比的角度。两个向量都旋转后做点积，"绝对角度"在点积中相消，只剩角度差——即相对位置。

**数学**：$\tilde q_m = R_m W_q x$，其中 $R_m$ 是 $d/2$ 个频率为 $\theta_i = 10000^{-2i/d}$ 的 2D 旋转块的块对角矩阵。由正交性 $R_m^\top R_n = R_{n-m}$：

$$\tilde q_m^\top \tilde k_n = (W_q x)^\top R_{n-m} (W_k x')$$

只依赖 $n - m$。

**实测**（$d=16$，固定一对 q/k）：

```
位置对 (m,n)  相对距离 m-n   旋转后内积 q·k
(   3,   1)        2        1.30553898
(  10,   8)        2        1.30553898
(1000, 998)        2        1.30553898      ← 位置推到 1000 依然成立（外推性）
(   5,   2)        3        3.68147669
(  17,  14)        3        3.68147669
相对距离=2 的三组内积完全一致? True
相对距离=3 的两组内积完全一致? True
```

**读数**：相对距离相同 → 内积在浮点意义上完全相等（误差 < 1e-10）。这就是 RoPE 能外推 + 表达相对位置 的机器证明。CS336 A1 的 `test_rope.npz` 测的正是这个性质。

---

## K3 · AdamW：解耦权重衰减（λ 被 √v̂ "吃掉"的实证）

> 对应 [B9 AdamW (2017)](./B-Transformer架构.md#b9)

**直觉**：Adam 里每个参数的步长被 $\sqrt{\hat v_t}$ 归一化。若把 L2 正则 $\lambda w$ 加进梯度，它也会被除以 $\sqrt{\hat v_t}$——**λ 想要的"温和衰减"被自适应机制扭曲了**。AdamW 把衰减从梯度里拿出来，直接乘在参数上。

**数学**：
- Adam+L2：$g_t = \nabla L + \lambda w$，更新 $w \leftarrow w - \eta\, \hat m_t/\sqrt{\hat v_t}$（L2 进入 $m, v$）
- AdamW：$w \leftarrow (1-\eta\lambda)\, w - \eta\, \hat m_t/(\sqrt{\hat v_t}+\epsilon)$（衰减独立于自适应）

纯衰减（无任务梯度）时 AdamW 有闭式解 $w_t = w_0 (1-\eta\lambda)^t$。

**实测**（$w_0=5, \eta=0.05, t=100$，纯衰减对照）：

```
     λ |    AdamW(解耦) |  Adam+L2(耦合)  |  理论(1-ηλ)^t
  0.02 |       4.5240   |     1.122231    |    4.5240
  0.10 |       3.0289   |     1.122230    |    3.0289
  0.50 |       0.3976   |     1.122230    |    0.3976
```

**读数**：AdamW 三行与理论值**逐位一致**——λ 精确控制衰减。Adam+L2 三种 λ 全部落到 1.1222——衰减速率 $\approx \eta \cdot \text{sign}(w)$（每步 ~0.05 的线性下降），**与 λ 无关**。想要 λ=0.02 的温和正则，Adam+L2 却给了激进衰减。这就是"大模型必须用 AdamW"的数值根源。

---

## K4 · FLOPs Calculus：C ≈ 6ND 与 MFU（对账 LLaMA-1-7B）

> 对应 [D3 Bahdanau FLOPs Calculus (2022)](./D-Scaling-Laws.md#d3)

**直觉**：每个参数对每个 token 贡献 2 次乘加（1 次 forward + 2 次 backward，按乘加=2 FLOPs 折算共 6），所以训练 $D$ 个 token 的总 FLOPs $\approx 6ND$。这是所有算力规划的第一公式。

**数学**：SwiGLU 配方的参数量（每层）= attention $4d^2$ + FFN $3 \cdot d \cdot \frac{8}{3}d = 8d^2$，共 $12d^2$；每 token 训练 FLOPs 主项 $6N$，加上注意力得分项 $2 \cdot L \cdot n_{ctx} \cdot d$。训练时间 $T = C / (\text{GPU数} \times \text{峰值FLOPS} \times \text{MFU})$。

**实测**（LLaMA-1-7B 近似配置 $d=4096, L=32, V=32000$，训 1T tokens）：

```
参数量 N ≈ 6.57B (LLaMA-1-7B 官方 6.7B)          ← 解析公式误差 ~2%
每 token 训练 FLOPs: 参数项 6N = 3.94e+10；注意力项 = 5.37e+08 (1.4%)
训 1T tokens: C = 6ND = 3.94e+22 FLOPs
2048×A100(312 TFLOPS, MFU 45%) 预计训练时长 = 38.1 小时 ≈ 1.6 天
（LLaMA-1-7B 官方报告: 82,432 A100·h ÷ 2048 = 40.3h ≈ 1.7 天 → 误差 <10% ✓）
```

**读数**：三条独立验证——①解析参数公式 vs 官方 6.7B 误差 2%；②注意力 ctx 项只占 1.4%（所以 6N 主导，短上下文时忽略 ctx 项合法）；③训练时长预测 38.1h vs 官方 40.3h，**误差 <10%**。一张纸 + 一个公式，就能把千万美元的训练预算算到 ±10%。这就是 CS336 L2 "算力会计学" 的威力。

---

## K5 · Chinchilla：拟合 L(N,D)——以及一个著名的"矛盾"

> 对应 [D4 Chinchilla (2022)](./D-Scaling-Laws.md#d4)

**直觉**：loss 由"不可约熵 $E$ + 模型容量项 + 数据容量项"三部分组成，各自幂律衰减。用网格搜索 $(\alpha, \beta)$ + 线性最小二乘 $(E, A, B)$ 即可拟合——这正是 CS336 A3 要做的事。

**数学**：$L(N, D) = E + \dfrac{A}{N^\alpha} + \dfrac{B}{D^\beta}$。固定 $C = 6ND$ 求最优 $N^*$，由拉格朗日条件推出 $N^* \propto C^{\beta/(\alpha+\beta)}$，$D^* \propto C^{\alpha/(\alpha+\beta)}$——**模型和数据应近似等比例增长**。

**实测**（150 个带 0.3% 噪声的合成数据点，复现论文 Approach 3 拟合流程）：

```
真值:   α=0.34, β=0.28, E=1.70
拟合出: α=0.33, β=0.28, E=1.69, A=340, B=412       ← 拟合方法有效 ✓

用论文发表常数 (α=0.34, β=0.28, A=406.4, B=410.7) 推最优:
  C=5.9e+21: N*=  4.1B, D*= 0.24T, D*/N*= 57.7
  C=5.9e+22: N*= 11.9B, D*= 0.83T, D*/N*= 69.6
  C=5.9e+23: N*= 34.2B, D*= 2.87T, D*/N*= 84.0
⚠️ 在 Chinchilla 实际算力 (C=5.9e23) 处，参数化拟合给出 D*/N*≈84，而非 '≈20'！
```

**读数（重要的一课）**：
1. **拟合方法论有效**：$\alpha, \beta, E$ 全部恢复（A 略偏，噪声下正常）。
2. **发现"矛盾"**：论文标题结论 "≈20 tokens/参数"（70B×1.4T）来自 Approach 1/2（包络/IsoFLOP 直接读数）；而 **Approach 3 发表的参数化常数隐含 D*/N*≈84**（最优模型更小、数据更多）。
3. **这不是我们代码的 bug**——这是社区熟知的 Chinchilla 拟合矛盾：Epoch AI 的复现（**Besiroglu et al. 2024，恰好是本库 [D6](./D-Scaling-Laws.md#d6) 的作者**）系统分析并修正了该拟合。且 $D^*/N^* \propto C^{1-2\beta/(\alpha+\beta)} \approx C^{0.08}$，**本来就不是常数 20**。
4. **工程教训**：headline 法则 ≠ 参数化拟合的隐含值；引用"20 倍法则"前先看它来自哪条估计路线、在什么算力尺度。

---

## K6 · GRPO 组内优势 & DPO 损失形状

> 对应 [H6 GRPO (2024)](./H-对齐与后训练.md#h6) 与 [H5 DPO (2023)](./H-对齐与后训练.md#h5)

**直觉**：GRPO 不要 value 网络——同一 prompt 采样一组回答，**组内排名就是优势**。DPO 把 RLHF 压成一个 sigmoid 分类损失——奖励差越大损失越小，学反了则线性受罚。

**数学**：
- GRPO：$\hat A_i = \dfrac{r_i - \text{mean}(r_{1..G})}{\text{std}(r_{1..G})}$（组内 z-score）
- DPO：$\mathcal L = -\log\sigma\big(\beta \cdot \text{gap}\big)$，gap = 隐式奖励差（chosen 减 rejected 的对数概率比变化）

**实测**：

```
原始奖励:  [0.8  0.2  0.5  0.5  0.0  1.0]
GRPO优势:  [ 0.891 -0.891  0.   0.  -1.485  1.485]     ← 均值0、方差1，无需 critic ✓

DPO: 隐式奖励差 gap → 损失
  gap=-2: L=0.9130 ██████████     ← 偏好学反，损失大
  gap=+0: L=0.6931 ████████       ← = ln2（随机水平）
  gap=+2: L=0.5130 ██████
  gap=+4: L=0.3711 ████           ← 学对了，但边际收益递减（sigmoid 饱和）
```

**读数**：GRPO 优势恰好均值 0、关于排名对称——这就是"组内相对"的全部含义，PPO 的 critic 被一组同伴替代。DPO 在 gap=0 时损失恰为 $\ln 2$（二分类随机猜测），sigmoid 形状天然抑制"过度自信"（gap=4 只比 gap=2 多降 0.14）。

---

## K7 · BPE：6 轮贪心合并的完整轨迹

> 对应 [A10 Sennrich BPE (2016)](./A-历史根基.md#a10)

**直觉**：反复合并"当前出现频率最高的相邻符号对"。频率最高的对（如 l+o）最先合并——统计意义上最值得分配一个新 token。

**数学**：每轮选 $\arg\max_{(a,b)} \sum_{w \in V} \text{freq}(w) \cdot \#\!(a,b)\text{ in } w$，合并后更新词表，重复 $k$ 轮得到 $k$ 条合并规则。

**实测**（语料 `low low low lower lowest newest newest widest`，6 轮）：

```
第1轮: 合并 ('l','o')      → 'lo'       (频次 5)
第2轮: 合并 ('lo','w')     → 'low'      (频次 5)
第3轮: 合并 ('e','s')      → 'es'       (频次 4)
第4轮: 合并 ('es','t')     → 'est'      (频次 4)
第5轮: 合并 ('est','</w>') → 'est</w>'  (频次 4)
第6轮: 合并 ('low','</w>') → 'low</w>'  (频次 3)
学到的合并序列: ['lo', 'low', 'es', 'est', 'est</w>', 'low</w>']
```

**读数**：注意合并的**复合性**——第 2 轮合并的是第 1 轮的产物 (`lo`+`w`)，第 5 轮是 `est`+`</w>`。词片是层级生长的，不是平面切分。'lowest' 会被切成 `low` + `est</w>`（两个都学到了）——这正是 BPE 泛化到未登录词的方式。CS336 A1 手写 BPE 的核心逻辑就这 30 行。

---

## K8 · KV Cache：MHA vs GQA vs MQA vs MLA 的显存账单

> 对应 [B11 GQA (2023)](./B-Transformer架构.md#b11) 与 [B15 MLA (2024)](./B-Transformer架构.md#b15)

**直觉**：自回归推理要缓存历史 token 的 K/V。显存 $\propto 2 \times \text{层数} \times \text{ctx} \times \text{KV头数} \times \text{head\_dim}$。降低"KV 头数"是唯一不伤 token 并行的旋钮——GQA 降到 8，MQA 降到 1，MLA 干脆缓存低秩压缩向量。

**数学**：$\text{KV}_{bytes} = 2_{(K,V)} \times \text{bytes} \times L \times n_{ctx} \times n_{kv} \times d_h$。LLaMA-2-70B：$L{=}80$，64 query 头，$d_h{=}128$，bf16（2 bytes）。

**实测**：

```
ctx=  4096: MHA=   10.7GB | GQA(8)=    1.3GB | MQA=   0.2GB | MLA(512d)=   0.7GB
ctx= 32768: MHA=   85.9GB | GQA(8)=   10.7GB | MQA=   1.3GB | MLA(512d)=   5.4GB
ctx=131072: MHA=  343.6GB | GQA(8)=   42.9GB | MQA=   5.4GB | MLA(512d)=  21.5GB
```

**读数**：ctx=128K 时 **MHA 单序列要 343.6GB**——任何单卡都放不下，这就是长上下文在 2023 年之前做不大的硬约束。GQA（LLaMA-2-70B 的选择）降到 42.9GB（8×），MLA（DeepSeek-V2 的选择）再用低秩压缩进一步压缩（本估算取 512 维压缩向量，实际配置略有出入但量级正确）。**架构论文里的每个"注意力变体"，背后都是这张账单**。

---

## K 总结：8 个实验各自验证了什么

| 实验 | 论文 | 验证的核心结论 | 结果 |
|------|------|--------------|------|
| K1 | Transformer | ÷√d_k 防 softmax 饱和 | std 11.37→1.00，熵 0.73→7.10 ✓ |
| K2 | RoPE | 内积只依赖相对位置 | 相对距离相同 → 内积相等（<1e-10）✓ |
| K3 | AdamW | 解耦衰减 vs λ 被归一化 | AdamW=理论值；Adam+L2 与 λ 无关 ✓ |
| K4 | FLOPs Calculus | C≈6ND + MFU 预算 | 训练时长预测 vs LLaMA-1 官方误差 <10% ✓ |
| K5 | Chinchilla | 拟合方法 + 最优 D/N | α,β 恢复 ✓；并复现著名"84 vs 20"矛盾 ⚠️ |
| K6 | GRPO/DPO | 组内 z-score 优势 / sigmoid 损失 | 优势均值 0 ✓；gap=0 → L=ln2 ✓ |
| K7 | BPE | 贪心高频对合并 + 层级词片 | 完整 6 轮合并轨迹 ✓ |
| K8 | GQA/MLA | KV cache 显存账 | 128K ctx: MHA 343.6GB → GQA 42.9 → MLA 21.5 ✓ |

> **最重要的一课来自 K5**：8 个实验里 7 个"验证成功"，1 个"验证出矛盾"——而那个矛盾（Chinchilla 参数化拟合 vs headline 法则）**恰恰是真实存在的科学争议**，还牵出了 D6 的作者去修正它。**实验的价值不在于确认你想听的，而在于暴露你没料到的**。

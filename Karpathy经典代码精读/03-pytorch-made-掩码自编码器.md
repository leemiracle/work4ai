# 03 · pytorch-made — 144 行讲透掩码自编码器 MADE

> **Andrej Karpathy · pytorch-made**（594★）。Masked Autoencoder for Density Estimation（Germain et al. 2015, [arXiv:1502.03509](https://arxiv.org/abs/1502.03509)）的 PyTorch 复现。**144 行**讲透怎么用一个 MLP + 一组 mask 实现"一次前向算完所有 $P(x_k | x_{<k})$"——比 RNN 快，是自回归生成模型的关键 trick。
>
> 源码：[`repos/pytorch-made/made.py`](./repos/pytorch-made/made.py) ｜ 原仓库：https://github.com/karpathy/pytorch-made

---

## 0. 为什么 MADE 值得学

**自回归模型的痛点**：要建模 $P(x) = \prod_k P(x_k | x_{<k})$。RNN 一次算一个 $x_k$，要算完整序列得跑 T 次前向。**能不能一次前向就把所有条件概率都算出来？**

MADE 的回答：**能**——给 MLP 的每个权重矩阵戴上"mask"，强行让 output unit $k$ 只连到 input unit $<k$。这样一次前向 $\text{MLP}(x)$ 的第 $k$ 个输出就只是 $x_{<k}$ 的函数，等于 $P(x_k | x_{<k})$。

| 方法 | 算完整序列 | 优势 |
|---|---|---|
| RNN | T 次前向（串行）| 可变长 |
| **MADE** | **1 次前向**（全并行）| 快，可训 |
| Transformer attention | 1 次前向（带 mask）| 现代 LLM 用的就是这思路 |

> 🎯 **关键认知**：MADE 是 attention mask（因果掩码）的"前传"。GPT 的下三角 attention mask 和 MADE 的连接 mask 是**同一个思想的不同实现**——都用掩码强制"只看过去"。读懂 MADE，GPT 的 causal mask 就豁然开朗。

---

## Step 1 · MaskedLinear（`made.py` L14-25）——戴面具的全连接层

```python
class MaskedLinear(nn.Linear):
    def __init__(self, in_features, out_features, bias=True):
        super().__init__(in_features, out_features, bias)
        self.register_buffer('mask', torch.ones(out_features, in_features))   # 1 矩阵

    def set_mask(self, mask):
        self.mask.data.copy_(torch.from_numpy(mask.astype(np.uint8).T))       # 外部注入

    def forward(self, input):
        return F.linear(input, self.mask * self.weight, self.bias)            # 关键：mask × weight
```

唯一改动：`forward` 里 `self.mask * self.weight`——mask 为 0 的位置权重被置零，**那条连接被砍掉**。其他和 `nn.Linear` 一模一样。

**为什么不用 dropout 或结构上删除连接？** 用 0-1 mask 最灵活——可以动态换 mask（MADE 的 ensemble 就是换不同 mask 重训），且不破坏 `nn.Linear` 的接口。

---

## Step 2 · update_masks（L68-94）—— MADE 的灵魂

整个 MADE 的精妙就在这个函数：**怎么设计 mask，让 output k 只依赖 input <k？**

### 2.1 给每个神经元分配一个"序号" m[l]

```python
self.m[-1] = np.arange(self.nin) if self.natural_ordering else rng.permutation(self.nin)
for l in range(L):
    self.m[l] = rng.randint(self.m[l-1].min(), self.nin-1, size=self.hidden_sizes[l])
```

- 输入层 `m[-1]`：每个 input unit 一个序号（0 到 nin-1，自然序或随机置换）
- 隐藏层 `m[l]`：每个隐藏 unit 从 `[m[l-1].min(), nin-1]` 随机抽一个序号

**序号的含义**："这个神经元最多能'看到'哪些输入"——序号为 d 的隐藏 unit 只能连到序号 ≤ d 的输入。

### 2.2 mask 矩阵：`m[l-1][:,None] <= m[l][None,:]`

```python
masks = [self.m[l-1][:,None] <= self.m[l][None,:] for l in range(L)]
masks.append(self.m[L-1][:,None] < self.m[-1][None,:])    # 输出层用严格 <（不是 <=）
```

这是关键公式。对层间连接矩阵 `mask[out, in]`：

- **隐藏层之间**用 `<=`：隐藏 unit d 接收来自所有序号 ≤ d 的下层 unit
- **输出层**用 **严格 `<`**：output unit k 只接收序号 **< k** 的隐藏 unit

**为什么输出用 `<` 不是 `<=`？** 这就保证了 **output k 不依赖 input k**——严格小于切断了"自己看自己"的路径，自回归性成立。

### 2.3 nout > nin（输出 mean+std）

```python
if self.nout > self.nin:
    k = int(self.nout / self.nin)
    masks[-1] = np.concatenate([masks[-1]]*k, axis=1)   # 把输出 mask 复制 k 份
```

若 `nout = 2*nin`，前 nin 个输出是均值、后 nin 个是标准差——两组都遵循同一个因果 mask。这让 MADE 能输出**分布参数**（不只点估计）。

---

## Step 3 · forward（L96-97）—— 平凡到惊人

```python
def forward(self, x):
    return self.net(x)
```

**就这一行**。所有巧思都在 mask 的构造里，前向就是一个普通 MLP。这是 MADE 最优雅的地方：**把"自回归"完全编码进网络结构（mask），前向无需任何特殊逻辑**。

对比：
- RNN 前向：显式循环 `h = f(h, x_t)` 串行 T 次
- MADE 前向：一次矩阵乘 + ReLU + ... + 矩阵乘，**完全并行**

---

## Step 4 · bash 跑通验证（自回归性铁证）

`made.py` 末尾自带测试：对每个 output k 反向传播，看梯度非零的 input——验证 output k **不依赖** input k。

```bash
cd Karpathy经典代码精读/repos/pytorch-made
python3 made.py
```

```
checking nin 10, hiddens [200], nout 10, natural False
output  8 depends on inputs:                          [] : OK
output  4 depends on inputs:                         [8] : OK
output  0 depends on inputs:                      [4, 8] : OK
output  7 depends on inputs:                   [0, 4, 8] : OK
output  2 depends on inputs:                [0, 4, 7, 8] : OK
output  9 depends on inputs:             [0, 2, 4, 7, 8] : OK
...
output  3 depends on inputs:    [0, 1, 2, 4, 5, 6, 7, 8, 9] : OK   ← 依赖除自己 3 外的全部
```

**铁证**：
1. **output k 永不依赖 input k**（所有 isok = OK）。这就是自回归性。
2. **依赖集单调递增**：`[] → [8] → [4,8] → [0,4,8] → ...`——序号越大的 output 依赖越多输入，完全符合 $P(x_k | x_{<k})$ 的因果结构。
3. **顺序被打乱**（8,4,0,7,2,9,...）：因为 `natural_ordering=False`，input 顺序被随机置换——MADE 支持任意 ordering，甚至 ensemble 多个 ordering（`num_masks>1`）。

> 🎯 **测试方法本身值得学**：用 `loss = output[0,k]; loss.backward(); grad != 0` 反推"output k 依赖哪些 input"——这是验证任何自回归模型因果性的通用技巧。GPT 的 causal attention mask 也能用同样方法验证。

---

## 三个关键洞察

### 洞察 1 · mask 即结构：把因果性编码进权重

MADE 不改 forward、不加循环、不引入新算子——**只给权重戴面具**。这是"用参数结构表达归纳偏置"的典范。Transformer 的 causal mask、ImageGPT 的 raster-scan mask、MAE 的 patch mask 都是同一家族的变体。

### 洞察 2 · 一次前向 vs T 次循环：并行的代价

RNN 串行（T 次前向）但能处理变长；MADE 并行（1 次前向）但固定长度。**这个 trade-off 贯穿整个序列建模史**——Transformer 用 attention mask 解决了"并行 + 变长"，但代价是 $O(T^2)$ 计算。MADE 是这条思路的起点之一。

### 洞察 3 · ordering ensemble：同一个模型多种分解

$P(x) = \prod_k P(x_k | x_{<k})$ 的"分解顺序"不唯一（可以从左到右，也可以任意置换）。MADE 用 `num_masks>1` 训多个 ordering 的 ensemble，降低对单一顺序的过拟合。这是"自回归模型的 data augmentation"。

---

## 与 work4ai 对接

| 本精读讲透的 | work4ai 深度版 |
|---|---|
| mask 实现自回归 | [`讲透Transformer`](../讲透Transformer/)（causal attention mask）|
| 自回归分解 $P(x)=\prod P(x_k\|x_{<k})$ | [`讲透基础模型`](../讲透基础模型/)（NTP 就是自回归）|
| MADE → Transformer attention | [`讲透生成模型`](../讲透生成模型/)（AR 模型谱系：MADE→PixelCNN→GPT）|
| mask × weight 的工程实现 | [`讲透PyTorch`](../讲透PyTorch/)（自定义 Layer）|

**阅读路径**：读 [讲透生成模型] 搞懂自回归分解 → 读本精读看 mask 怎么实现一次前向 → 读 [讲透Transformer] 看 attention mask 的现代版。

---

## 📌 下一步

- **继续 Karpathy 系列**：下一篇 `04-lecun1989-repro-复现1989论文.md`（377 行，复现 LeCun 1989 反向传播论文，历史+实践），对接讲透反向传播。
- **动手**：用 MADE 建一个像素级图像生成模型（在 MNIST 上），采样看生成质量。Karpathy 的 [pytorch-normalizing-flows](./repos/pytorch-normalizing-flows/) 用 MADE 做 flow 的条件器（下一篇会精读）。
- **对照 GPT**：把 MADE 的 mask 换成 Transformer 的 causal attention mask，理解两者"用不同方式实现同一个因果约束"。

## ✍️ 练习

1. **（验证）** 跑 `python3 made.py`，把 `natural_ordering` 改成 `True`，看依赖集顺序是否变成自然序 0,1,2,...,9。为什么？
2. **（手算 mask）** 对 nin=3, hidden=[2], nout=3, natural_ordering，手算每层的 m[l] 和 mask 矩阵。验证 output 1 不连 input 1。
3. **（思考）** MADE 的 mask 是稠密矩阵（0-1），占内存。Transformer 的 causal mask 是"下三角"，可以用加法 broadcast 而不存矩阵。两种 mask 的内存/计算 trade-off？
4. **（开放）** MADE 支持任意 ordering（随机置换），GPT 用固定自然序（左到右）。为什么 GPT 不用随机 ordering ensemble？提示：语言有天然时序；计算成本；注意力已部分解决。

---

> **源码**：[`repos/pytorch-made/made.py`](./repos/pytorch-made/made.py)（144 行）｜ 论文：[MADE, Germain et al. 2015](https://arxiv.org/abs/1502.03509)

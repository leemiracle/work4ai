# 08 · build-nanogpt — 完整复现 GPT-2：从数据加载到评测

> **Andrej Karpathy · build-nanogpt**（5.4k★）。*Let's reproduce GPT-2 (124M)* 视频的配套代码——`train_gpt2.py` 521 行。**模型与 [nanoGPT](./07-nanoGPT-从零训练GPT.md) 几乎相同**，但补全了 nanoGPT 缺的**完整训练管线**：fineweb 数据加载 / HellaSwag 评测 / DDP 分布式 / 梯度累积 / cosine LR schedule。8×A100 训 ~1 epoch 复现 GPT-2 124M（val loss 2.85 ≈ 原版 2.84）。
>
> 源码：``repos/build-nanogpt/train_gpt2.py`` ｜ 视频：*Let's reproduce GPT-2: training in PyTorch*

---

## 0. build-nanogpt vs nanoGPT：从"模型"到"完整训练闭环"

| 维度 | nanoGPT | **build-nanogpt** |
|---|---|---|
| 模型 | ✅ GPT | ✅ GPT（几乎一样）|
| 数据加载 | 简单 | ✅ **fineweb 分 shard + DDP 切分** |
| 评测 | 无 | ✅ **HellaSwag**（标准 LLM benchmark）|
| 分布式 | 单卡 | ✅ **DDP（torchrun）** |
| 梯度累积 | 无 | ✅ **支持任意 total_batch_size** |
| LR schedule | 固定 | ✅ **warmup + cosine decay** |
| 复现 GPT-2 | 理论可 | ✅ **实测复现**（val loss 2.85）|

> 🎯 **本篇不重复讲模型**（nanoGPT 精读已讲透）。本篇专讲 **build-nanogpt 的训练管线工程**——怎么把一个能前向的模型，变成能真训出 GPT-2 水平的完整系统。

---

## Step 1 · 训练管线全景（`train_gpt2.py` 四件套）

```
┌─────────────────────────────────────────────────────────┐
│  ① 数据: DataLoaderLite                                  │
│     edu_fineweb10B 分 shard → token 序列 → x/y 切片      │
├─────────────────────────────────────────────────────────┤
│  ② 模型: GPT (model.py 同 nanoGPT)                       │
│     + from_pretrained (可选 HF 权重热启)                  │
├─────────────────────────────────────────────────────────┤
│  ③ 训练: DDP + 梯度累积 + cosine LR                       │
│     19073 steps × total_batch 0.5M tokens                │
├─────────────────────────────────────────────────────────┤
│  ④ 评测: 每 250 步 val loss + HellaSwag acc              │
│     + checkpoint 保存                                     │
└─────────────────────────────────────────────────────────┘
```

---

## Step 2 · DataLoaderLite（L214-252）—— fineweb 分 shard 流式加载

```python
class DataLoaderLite:
    def __init__(self, B, T, process_rank, num_processes, split):
        shards = [s for s in os.listdir("edu_fineweb10B") if split in s]  # 分 shard
        ...
    def next_batch(self):
        buf = self.tokens[pos : pos+B*T+1]
        x = buf[:-1].view(B, T)   # 输入（错位切片）
        y = buf[1:].view(B, T)    # 目标（错位 1 位）
        pos += B*T*num_processes  # 多进程时各跳过别人的份额
        if out_of_bounds: load_next_shard()
```

**两个关键设计**：

1. **错位切片 = 自回归目标**：`x = buf[:-1]`, `y = buf[1:]`——y 永远是 x 的下一 token。一句话 `[a,b,c,d]` → x=`[a,b,c]`, y=`[b,c,d]`。这是所有自回归 LM 数据准备的铁律。

2. **分 shard + 多进程切分**：10B token 数据分多个 `.npy` shard，逐个加载；DDP 时每个进程从 `process_rank * B*T` 偏移开始，互不重叠。

bash 验证（x/y 切片）：
```
tokens: [0,1,2,...,19]
x: [[0,1,2,3],[4,5,6,7]]      ← 输入
y: [[1,2,3,4],[5,6,7,8]]      ← 目标(错位1位)
→ 每位置预测下一 token
```

---

## Step 3 · HellaSwag 评测（L258-275）—— 标准常识推理 benchmark

```python
def get_most_likely_row(tokens, mask, logits):
    # 对 4 个候选项，各算 completion 区域的平均 CE loss
    shift_losses = F.cross_entropy(...)            # 每位置的 loss
    masked_shift_losses = shift_losses * mask      # 只看 completion 区域
    avg_loss = sum_loss / mask.sum()               # 每候选项的平均 loss
    pred_norm = avg_loss.argmin()                  # loss 最低 = 最可能
    return pred_norm
```

**HellaSwag 任务**：给一个场景描述，4 个候选续写，选最合理的。例：*"The man fell off the table. He ___"* → [landed safely / did a flip / got hurt / kept walking]。

**评测逻辑**：每个候选拼到 prompt 后，过模型算**候选区域的平均 CE loss**——loss 最低的就是模型认为最可能的。**acc 衡量模型的常识推理**。

> 📌 **mask 的作用**：只算"候选续写"部分的 loss，不算 prompt 部分（prompt loss 都一样，无区分力）。这是 masked evaluation 的标准做法。

**GPT-2 124M 的 HellaSwag acc ≈ 29%**（随机是 25%，所以 29% 表示有微弱常识）。

---

## Step 4 · DDP 分布式 + 梯度累积（L288-331）

### 4.1 DDP 启动

```bash
torchrun --standalone --nproc_per_node=8 train_gpt2.py   # 8 GPU
```

DDP 自动设 `RANK`/`LOCAL_RANK`/`WORLD_SIZE` 环境变量。代码里：

```python
ddp = int(os.environ.get('RANK', -1)) != -1
if ddp:
    init_process_group(backend='nccl')
    ddp_rank = int(os.environ['RANK'])
    device = f'cuda:{ddp_local_rank}'
```

每个 GPU 跑同样模型，处理不同数据，反向后梯度 all-reduce 同步。

### 4.2 梯度累积（任意 total_batch_size）

```python
total_batch_size = 524288   # 0.5M tokens
grad_accum_steps = total_batch_size // (B*T*ddp_world_size)
```

bash 验证：
```
1 GPU: grad_accum=8  (每步累积 8 个 micro-batch 才更新)
4 GPU: grad_accum=2
8 GPU: grad_accum=1  (单卡 batch 已够大)
```

**为什么梯度累积？** 显存限制单次 forward 的 batch（B=64），但有效 batch 想要 0.5M tokens。解法：**前向 N 次、梯度累加、第 N 次才 optimizer.step()**。数学上等价于大 batch，显存只用小 batch。

---

## Step 5 · cosine LR schedule（L349-364）

```python
max_lr, min_lr = 6e-4, 6e-5
warmup_steps, max_steps = 715, 19073

def get_lr(it):
    if it < warmup_steps:                          # ① 线性 warmup
        return max_lr * (it+1) / warmup_steps
    if it > max_steps:                             # ② 超时降到 min
        return min_lr
    decay_ratio = (it - warmup_steps) / (max_steps - warmup_steps)
    coeff = 0.5 * (1 + math.cos(math.pi * decay_ratio))   # ③ cosine 衰减
    return min_lr + coeff * (max_lr - min_lr)
```

**三段式 LR schedule**（GPT-2/LLaMA 等都在用）：

| 阶段 | 步数 | lr | 作用 |
|---|---|---|---|
| ① Warmup | 0 → 715 | 0 → 6e-4（线性升）| 防初期梯度爆炸（Adam 自适应状态未稳定）|
| ② Cosine decay | 715 → 19073 | 6e-4 → 6e-5（余弦降）| 后期细调，收敛到极小值附近 |
| ③ Min | >19073 | 6e-5（固定）| 训练结束的 floor |

bash 验证：
```
step      0: lr=8.4e-07  (warmup 起点)
step    715: lr=6.0e-04  (warmup 终点 = max)
step  10000: lr=3.3e-04  (cosine 中段)
step  19073: lr=6.0e-05  (cosine 终点 = min)
```

> 🎯 **warmup 为什么必须？** 训练初期模型随机，梯度方向噪声大；Adam 的一阶/二阶矩估计还在累积，大 lr 会让参数跑飞。warmup 让 lr 从 0 慢慢升，给 Adam 状态"热身"时间。这是大模型训练的铁律。

---

## Step 6 · 复现 GPT-2 的实测结果

Karpathy 用 build-nanogpt 在 8×A100 上训 GPT-2 124M（fineweb-edu 10B tokens，~1 epoch = 19073 steps）：

| 指标 | build-nanogpt 复现 | GPT-2 原版 | 差距 |
|---|---|---|---|
| **val loss** | **2.85** | ~2.84 | ~0（几乎完全复现）|
| **HellaSwag acc** | ~29% | ~29.4% | ~0 |
| 训练成本 | 8×A100 × ~1 epoch | OpenAI 原版 | 可比 |

**这个结果的震撼**：一个 521 行的脚本，从零训出的 GPT-2 和 OpenAI 原版几乎一样。**证明了 GPT-2 没有黑魔法**——架构 + 数据 + 训练配方公开后，谁都能复现。这也是 build-nanogpt 成为"业界复现 LLM 起点"的原因。

---

## 三个关键洞察

### 洞察 1 · 训练管线比模型更难（工程占大头）

nanoGPT 的 330 行模型 + build-nanogpt 的 521 行管线（数据/评测/分布式/LR）。**管线代码比模型还多**。复现一个 LLM，60% 工作在"数据加载 + 评测 + 分布式 + 调度"，不是模型架构。

### 洞察 2 · 梯度累积 = 用显存换 batch size

显存不够装大 batch？前向多次、梯度累加、最后一次更新。**数学等价于大 batch，显存只用小 batch**。这是平民 GPU 训大模型的钥匙——8GB 显存也能模拟 0.5M token 的有效 batch。

### 洞察 3 · warmup + cosine decay 是 LLM 训练的"通用配方"

GPT-2/3、LLaMA、PaLM、几乎所有大模型都用 warmup + cosine decay。**这个 schedule 本身就是"深度学习训练的标准协议"**。读懂 build-nanogpt 的 get_lr，你就懂了 LLaMA 训练脚本里的 LR 那段。

---

## 与 work4ai 对接

| 本精读讲透的 | work4ai 深度版 |
|---|---|
| 训练管线全景 | [`讲透基础模型`](../讲透基础模型/)（LLM 训练全流程）|
| cosine LR / warmup | [`讲透优化器`](../讲透PyTorch/11-损失函数与优化器.md)（LR schedule）|
| DDP 分布式 | [`讲透分布式AI系统`](../讲透分布式AI系统/)（DDP/FSDP）|
| HellaSwag / 评测 | [`讲透数据`](../讲透数据/)（LM benchmark）|
| 梯度累积 | [`讲透GPU与系统级`](../讲透GPU与系统级/)（显存优化）|

**阅读路径**：[minGPT](./06-minGPT-minimal-GPT.md)（架构）→ [nanoGPT](./07-nanoGPT-从零训练GPT.md)（工程优化）→ **本篇（完整管线）**。读完这三篇，你能从零写出可训的 GPT。

---

## 📌 下一步

- **GPT 三连完成**！下一篇 `09-makemore-字符级语言模型.md`（719 行，字符级 AR-LM 的渐进式实现：bigram→MLP→RNN→Transformer 四种范式对比）。
- **动手训**：`python train_gpt2.py`（需 GPU + fineweb 数据）；或先跑 `sample.py`（用 HF 预训练 GPT2 权重生成文本）。
- **看视频**：Karpathy *Let's reproduce GPT-2*（4h，逐行训出 124M）。

## ✍️ 练习

1. **（手算 batch）** total_batch=524288，B=64，T=1024，单卡。grad_accum 应是多少？验证脚本里 `1 GPU: grad_accum=8` 对吗？
2. **（LR 曲线）** 画 get_lr 的完整曲线（0 到 20000 步）。warmup 段是直线吗？cosine 段在哪个步数降到 max_lr 和 min_lr 的中点？
3. **（思考）** HellaSwag 评测为什么用"候选区域的平均 loss"而不是"全句 loss"？如果用全句 loss，4 个候选项的差异会变大还是变小？
4. **（开放）** Karpathy 复现的 GPT-2 val loss 2.85 ≈ 原版 2.84。这个"几乎完美复现"说明了什么？如果换更大数据（100B 而非 10B），val loss 会更低还是饱和？

---

> **源码**：``repos/build-nanogpt/train_gpt2.py``（521 行）｜ ``hellaswag.py``（177 行评测）｜ ``fineweb.py``（82 行数据下载）

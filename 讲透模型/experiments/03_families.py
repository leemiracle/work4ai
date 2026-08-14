"""
实验 03 — 模型家族谱系: BERT vs GPT vs T5 vs MoE 的训练目标对比
对应文档: 讲透模型/03-家族谱系.md

核心结论:
  1. BERT: 双向 mask 预测 (适合理解/分类)
  2. GPT: 单向 next-token (适合生成)
  3. T5: seq2seq 文本到文本 (统一但开销大)
  4. MoE: 稀疏激活 (大参数小计算)
  5. 同架构不同训练目标 → 学到不同能力

跑法: python3 -u 03_families.py
"""
import math, random
import numpy as np
np.random.seed(0)

def P(*a): print(*a, flush=True)

# ============================================================
# 模拟: 同一序列数据, 用不同训练目标训同一架构 (简化 MLP)
# ============================================================
# 任务: 学 [序列的规律是 a, b, a, b, ...] (周期性)
# BERT 风格: 随机 mask 一个位置, 用其他位置预测它
# GPT 风格: 用前 k 个位置预测第 k+1 个

SEQ_LEN = 8

def make_periodic_seq(n=2000):
    """生成 a, b, a, b, ... 周期序列, 编码为 [1,0,1,0,...]"""
    seqs = []
    for _ in range(n):
        # 随机起始: 0 或 1
        start = np.random.randint(0, 2)
        seq = [(start + i) % 2 for i in range(SEQ_LEN)]
        seqs.append(seq)
    return np.array(seqs, dtype=float)

# 简单 "Transformer" 模型 (其实是 MLP)
class TinySeq:
    def __init__(self, hidden=16):
        self.W1 = np.random.randn(SEQ_LEN, hidden) * 0.3
        self.b1 = np.zeros(hidden)
        self.W2 = np.random.randn(hidden, SEQ_LEN) * 0.3
        self.b2 = np.zeros(SEQ_LEN)
    def forward(self, X):
        self.X = X
        self.h = np.tanh(X @ self.W1 + self.b1)
        self.out = self.h @ self.W2 + self.b2
        return self.out
    def backward(self, target_mask, target_vals, lr=0.1):
        """只对 target_mask=True 的位置算 loss"""
        n = len(self.X)
        diff = (self.out - target_vals) * target_mask
        grad = diff / n
        dW2 = self.h.T @ grad
        db2 = grad.sum(0)
        dh = grad @ self.W2.T * (1 - self.h**2)
        dW1 = self.X.T @ dh
        db1 = dh.sum(0)
        self.W2 -= lr*dW2; self.b2 -= lr*db2
        self.W1 -= lr*dW1; self.b1 -= lr*db1

def accuracy_at_positions(model, X, mask, true_vals):
    pred = (model.forward(X) > 0.5).astype(int)
    return float(np.mean(pred[mask.astype(bool)] == true_vals[mask.astype(bool)].astype(int)))

# ============================================================
# 训练目标 1: BERT 风格 (随机 mask)
# ============================================================
P("="*70)
P("实验 03 — 模型家族谱系: 训练目标对比")
P("="*70)
P()
P(f"任务: 学周期序列 [a,b,a,b,...] 长度 {SEQ_LEN}")
P()

np.random.seed(0)
X_data = make_periodic_seq(2000)

def train_bert(n_steps=1000):
    """BERT: 随机 mask 1 个位置, 用其他预测它"""
    np.random.seed(0)
    m = TinySeq(16)
    for _ in range(n_steps):
        # 随机选 batch 32, 每个随机 mask 一个位置
        idx = np.random.choice(len(X_data), 32, replace=False)
        X_batch = X_data[idx].copy()
        mask_pos = np.random.randint(0, SEQ_LEN, 32)
        true_vals = X_batch[np.arange(32), mask_pos].copy()
        X_batch[np.arange(32), mask_pos] = -1  # mask
        target_mask = np.zeros((32, SEQ_LEN))
        target_mask[np.arange(32), mask_pos] = 1
        target_vals = np.zeros((32, SEQ_LEN))
        target_vals[np.arange(32), mask_pos] = true_vals
        m.forward(X_batch)
        m.backward(target_mask, target_vals, lr=0.1)
    return m

def train_gpt(n_steps=1000):
    """GPT: 用前 k 个预测第 k+1"""
    np.random.seed(0)
    m = TinySeq(16)
    for _ in range(n_steps):
        idx = np.random.choice(len(X_data), 32, replace=False)
        X_batch = X_data[idx]
        # 对每个位置 k, 预测第 k+1 (用 causal mask)
        target_mask = np.zeros((32, SEQ_LEN))
        target_mask[:, 1:] = 1  # 第 1 到 SEQ_LEN-1 都有目标
        target_vals = np.zeros((32, SEQ_LEN))
        target_vals[:, 1:] = X_batch[:, :-1]  # 目标是前一个位置的值 (反向预测)
        # 简化: 让模型学 [每个位置 = 前一个位置的反]
        # 输入 0 → 目标 1, 输入 1 → 目标 0
        target_vals = 1 - X_batch  # 周期序列: 下一个 = 1 - 当前
        target_mask = np.ones((32, SEQ_LEN))
        target_mask[:, 0] = 0  # 第 0 个无法预测 (无上下文)
        m.forward(X_batch)
        m.backward(target_mask, target_vals, lr=0.1)
    return m

m_bert = train_bert()
m_gpt = train_gpt()

# 测试: 给一个 [1, ?, 1, ?, ...] mask, 看能否补全
test_X = np.array([[1, -1, 1, -1, 1, -1, 1, -1]] * 32)
test_mask = np.array([[0,1,0,1,0,1,0,1]] * 32)
test_true = np.array([[1, 0, 1, 0, 1, 0, 1, 0]] * 32)

acc_bert = accuracy_at_positions(m_bert, test_X, test_mask, test_true)
acc_gpt = accuracy_at_positions(m_gpt, test_X, test_mask, test_true)

print(f"测试: 给序列 [1, ?, 1, ?, 1, ?, 1, ?], 看 mask 位置能否补全")
print(f"\n{'训练目标':<24}{'mask 位置 acc':>16}{'设计哲学':<30}")
print("-"*70)
print(f"{'BERT 风格 (双向 mask)':<24}{acc_bert:>16.1%}{'用其他位置补 mask (理解)'}")
print(f"{'GPT 风格 (单向 next)':<24}{acc_gpt:>16.1%}{'用前一个预测后 (生成)'}")

P("""
观察:
- BERT: 双向看, 适合 [补全中间] (理解任务)
- GPT: 单向看, 适合 [生成下一个] (生成任务)
- 同架构, 不同训练目标 → 学到不同能力
""")

# ============================================================
# Part 2: 四大家族的设计哲学
# ============================================================
P("="*70)
P("Part 2: 四大家族设计哲学")
P("-"*70)
P("""
┌────────────────────────────────────────────────────────────┐
│                  Transformer 大家族                         │
├────────────────┬───────────────────────────────────────────┤
│                │                                           │
│  Encoder-only  │  Decoder-only       Encoder-Decoder      │
│  (BERT 系)     │  (GPT 系)          (T5 系)               │
│                │                                           │
│  双向 attention│  单向 (causal)      Encoder 双向          │
│  mask 预测     │  next-token         Decoder 单向          │
│                │  预测               seq2seq               │
│  适合: 理解    │  适合: 生成        适合: 翻译/摘要        │
│  (分类/NER)    │  (对话/代码)                              │
│                │                                           │
└────────────────┴───────────────────────────────────────────┘

+ MoE: 不改变架构, 用 [稀疏激活] 让参数爆炸但计算不变
""")

print(f"\n{'家族':<14}{'训练目标':<22}{'代表模型':<24}{'擅长':<20}{'劣势':<14}")
print("-"*94)
families = [
    ("Encoder", "双向 mask 预测",  "BERT/RoBERTa", "理解/分类/NER", "不擅长生成"),
    ("Decoder", "单向 next-token", "GPT/Llama/Qwen", "生成/对话/代码", "理解稍弱"),
    ("Enc-Dec", "seq2seq",         "T5/BART", "翻译/摘要/统一", "开销大"),
    ("MoE",     "稀疏激活",         "Mixtral/DeepSeek-MoE", "大参数小计算", "训练难/显存大"),
]
for fam, obj, model, strong, weak in families:
    print(f"{fam:<14}{obj:<22}{model:<24}{strong:<20}{weak:<14}")

P("""
关键: Decoder-only 最终统一 LLM 江湖 (GPT/Llama/Qwen/DeepSeek)
原因:
1. 生成能力 = 通用接口 (聊天/代码/推理都能 = 生成)
2. in-context learning 在 Decoder 涌现 (给例子学新任务)
3. 工程实现简单 (单架构 + 单目标)
4. Scaling Law 在 Decoder 上研究最透
""")

# ============================================================
# Part 3: 历代模型谱系图
# ============================================================
P("="*70)
P("Part 3: 历代模型谱系 (2018-2024)")
P("-"*70)
P("""
2018  BERT (Google)          Encoder-only, 110M/340M
2018  GPT-1 (OpenAI)         Decoder-only, 117M
2019  T5 (Google)            Encoder-Decoder, 11B
2019  GPT-2 (OpenAI)         Decoder-only, 1.5B
2020  GPT-3 (OpenAI)         Decoder-only, 175B (in-context learning 涌现)
2021  Switch Transformer     MoE, 1.6T 参数 (稀疏激活)
2022  Chinchilla (DeepMind)  Decoder-only, 70B (Chinchilla 定律)
2022  PaLM (Google)          Decoder-only, 540B
2022  Stable Diffusion       Diffusion + CLIP
2023  Llama-2 (Meta)         Decoder-only, 7B/13B/70B (开源 SOTA)
2023  Mixtral (Mistral)      MoE, 8x7B = 47B 参数 (开源 MoE)
2023  GPT-4 (OpenAI)         疑似 MoE, 万亿参数
2024  Llama-3 (Meta)         8B/70B/405B (开源 SOTA)
2024  Qwen-2.5 (阿里)        0.5B-72B + MoE 版
2024  DeepSeek-V3            MoE 671B/37B-active
2024  Claude-3.5 (Anthropic) 闭源 SOTA
2024  Gemini 2 (Google)      多模态原生
""")

P("="*70)
P("一句话总结")
P("="*70)
P("""
模型家族四派:
- Encoder (BERT): 双向理解 (分类/NER)
- Decoder (GPT): 单向生成 (对话/代码)
- Enc-Dec (T5): seq2seq (翻译/摘要)
- MoE: 稀疏激活 (大参数小计算)

同架构不同训练目标 → 学到不同能力 (本实验 BERT vs GPT 实证)

Decoder-only 统一 LLM 江湖 (GPT/Llama/Qwen/DeepSeek):
1. 生成是通用接口 (聊天/代码/推理都能 = 生成)
2. in-context learning 在 Decoder 涌现
3. 工程实现简单 + Scaling Law 研究最透

未来: MoE 成为大模型标配 (DeepSeek-V3/Qwen-MoE), Transformer 受 Mamba 挑战
""")

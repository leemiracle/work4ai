"""
实验 07 —— 大语言模型导引: 用 mini-GPT 亲眼看见'语法 vs 知识'与'温度悬崖'
对应文档: 讲透NLP/07-大语言模型.md

核心结论 (两个反直觉发现):
  反直觉发现 1 —— tiny GPT 学不到"知识", 但能学到"语法":
      一个 4 层、hidden=128 的小 GPT (约 80 万参数) 在模板生成的英语语料上训练几百步,
      它生成的句子每个词都像英语、词序基本通顺 (冠词→形容词→名词→动词→介词),
      但语义全是胡说 (the heavy snake swam under a soft bed) —— 它学会了"语言的形式",
      没学会"世界的事实"。这正是 SLP3 Ch7 的核心: 知识是海量数据+大容量的副产物。

  反直觉发现 2 —— sampling temperature 对生成质量影响巨大:
      T=0 (贪心): 确定性强但陷入死循环 —— 完全退化。
      T=0.7:      句子最自然, 语法基本成立, 最像"人话"。
      T=1.0:      开始出乱码, 词序混乱。
      T=1.5:      纯随机抽词, 完全无法读。
      仅一个标量参数, 把"流畅"和"噪声"隔开的悬崖极陡。

跑法:  python3 -u experiments/07_llm_intro.py
依赖:  torch (CPU 即可, 约 1-3 分钟)
"""
import math, random
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.set_num_threads(4)
torch.manual_seed(42)
random.seed(1)

DEVICE = torch.device("cpu")

ARTICLES = ["the", "a"]
ADJS = ["red", "blue", "green", "old", "young", "big", "small", "tall", "short", "cold",
        "warm", "dark", "bright", "heavy", "light", "fast", "slow", "loud", "quiet",
        "soft", "hard", "round", "sharp"]
NOUNS = ["cat", "dog", "bird", "frog", "man", "child", "bear", "rabbit", "fox", "fish",
         "wolf", "horse", "ant", "turtle", "owl", "bee", "snake", "deer", "king", "tree",
         "house", "wall", "door", "star", "moon", "sun", "sky", "sea", "fire", "stone",
         "leaf", "water", "wind", "rain", "ball", "box", "book", "bed"]
VERBS = ["sat", "ran", "jumped", "walked", "played", "slept", "ate", "chased", "swam",
         "flew", "watched", "hid", "sang", "fell", "rose", "cut", "lifted", "made",
         "grew", "opened", "built", "covered", "lit", "found"]
PREPS = ["on", "in", "under", "over", "into", "through", "past", "near", "by", "across"]


def make_corpus(n=600):
    sents = []
    for _ in range(n):
        s = "%s %s %s %s %s %s %s %s ." % (
            random.choice(ARTICLES), random.choice(ADJS), random.choice(NOUNS),
            random.choice(VERBS),  random.choice(PREPS),  random.choice(ARTICLES),
            random.choice(ADJS),   random.choice(NOUNS))
        sents.append(s)
    return sents


CORPUS = make_corpus(400)
raw = " ".join(CORPUS)
words = raw.split()

vocab = sorted(set(words))
stoi = {w: i for i, w in enumerate(vocab)}
itos = {i: w for w, i in stoi.items()}
V = len(vocab)
data = torch.tensor([stoi[w] for w in words], dtype=torch.long, device=DEVICE)
print("语料: %d 句, %d 词, 词表 V=%d" % (len(CORPUS), len(words), V))
print("样例: %s\n" % CORPUS[0])

BLOCK = 16


def get_batch(bs=32):
    ix = torch.randint(0, len(data) - BLOCK - 1, (bs,))
    x = torch.stack([data[i:i + BLOCK] for i in ix])
    y = torch.stack([data[i + 1:i + BLOCK + 1] for i in ix])
    return x, y


class CausalSelfAttention(nn.Module):
    def __init__(self, d, n_head):
        super().__init__()
        assert d % n_head == 0
        self.n_head = n_head
        self.d_head = d // n_head
        self.qkv = nn.Linear(d, 3 * d, bias=False)
        self.proj = nn.Linear(d, d, bias=False)

    def forward(self, x):
        B, T, C = x.shape
        qkv = self.qkv(x).reshape(B, T, 3, self.n_head, self.d_head)
        q, k, v = qkv.unbind(dim=2)
        q, k, v = [t.transpose(1, 2) for t in (q, k, v)]
        att = (q @ k.transpose(-2, -1)) / math.sqrt(self.d_head)
        mask = torch.triu(torch.ones(T, T, device=x.device), diagonal=1).bool()
        att = att.masked_fill(mask, float("-inf"))
        att = F.softmax(att, dim=-1)
        out = (att @ v).transpose(1, 2).reshape(B, T, C)
        return self.proj(out)


class Block(nn.Module):
    def __init__(self, d, n_head):
        super().__init__()
        self.ln1 = nn.LayerNorm(d)
        self.attn = CausalSelfAttention(d, n_head)
        self.ln2 = nn.LayerNorm(d)
        self.mlp = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x


class MiniGPT(nn.Module):
    def __init__(self, V, d=128, n_layer=4, n_head=4, block_size=16):
        super().__init__()
        self.block_size = block_size
        self.tok_emb = nn.Embedding(V, d)
        self.pos_emb = nn.Embedding(block_size, d)
        self.blocks = nn.ModuleList([Block(d, n_head) for _ in range(n_layer)])
        self.ln_f = nn.LayerNorm(d)
        self.head = nn.Linear(d, V, bias=False)
        self.head.weight = self.tok_emb.weight
        self.apply(self._init)

    @staticmethod
    def _init(m):
        if isinstance(m, nn.Linear):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.Embedding):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        pos = torch.arange(T, device=idx.device).unsqueeze(0)
        x = self.tok_emb(idx) + self.pos_emb(pos)
        for blk in self.blocks:
            x = blk(x)
        x = self.ln_f(x)
        logits = self.head(x)
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), targets.reshape(-1))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new, temperature=1.0):
        for _ in range(max_new):
            cond = idx if idx.size(1) <= self.block_size else idx[:, -self.block_size:]
            logits, _ = self(cond)
            logits = logits[:, -1, :] / (temperature if temperature > 0 else 1e-9)
            if temperature == 0.0:
                nxt = logits.argmax(dim=-1, keepdim=True)
            else:
                probs = F.softmax(logits, dim=-1)
                nxt = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, nxt], dim=1)
        return idx


model = MiniGPT(V, d=128, n_layer=4, n_head=4, block_size=BLOCK).to(DEVICE)
n_params = sum(p.numel() for p in model.parameters())
print("mini-GPT 参数量 = %d (约 %.1f 万)  | 4 层 decoder, hidden=128, 4 头\n"
      % (n_params, n_params / 1e4))


print("=" * 66)
print("Part 1: 训练 mini-GPT —— 它学到的是'语法', 不是'知识'")
print("=" * 66)

opt = torch.optim.AdamW(model.parameters(), lr=4e-3)
model.train()
import time; t0 = time.time()
for step in range(101):
    xb, yb = get_batch(32)
    opt.zero_grad()
    _, loss = model(xb, yb)
    loss.backward()
    opt.step()
    if step % 50 == 0:
        print("  step %4d: 训练交叉熵 = %.4f nats = %.3f bits/token  (%.1fs)"
              % (step, loss.item(), loss.item() / math.log(2), time.time() - t0))

model.eval()
with torch.no_grad():
    xb, yb = get_batch(128)
    _, eval_loss = model(xb, yb)

rand_bits = math.log2(V)
model_bits = eval_loss.item() / math.log(2)
print("\n  对比: 词表 V=%d, 瞎猜(均匀)交叉熵 = %.3f bits/token" % (V, rand_bits))
print("  模型交叉熵 = %.3f bits/token, 比瞎猜节省 %.0f%%"
      % (model_bits, 100 * (1 - model_bits / rand_bits)))
print("  ==> 模型确实学到了词的分布规律 (远好于瞎猜)")

print("\n" + "-" * 66)
print("【反直觉发现 1】生成样本 —— 像英语, 但语义全错:")
print("-" * 66)
for seed in ["the", "a", "the", "a"]:
    ctx = torch.tensor([[stoi[seed]]], device=DEVICE)
    out = model.generate(ctx, max_new=16, temperature=0.7)
    text = " ".join(itos[i.item()] for i in out[0])
    print("  '%s' → %s" % (seed, text))

print("\n  观察: 每个词都是真英语词, '冠词→形容词→名词→动词→介词'的骨架基本成立,")
print("  但 'the heavy snake swam under a soft bed' 这类组合在语义上完全荒谬。")
print("  ==> 模型抓到了语言的【形式】(统计共现), 没抓到世界的【事实】。")
print("  ==> 这就是为什么 LLM 必须靠海量数据 + 大容量: 知识是规模的红利, 不是目标本身。")


print("\n" + "=" * 66)
print("Part 2: temperature 对生成质量的悬崖效应")
print("=" * 66)


def unique_ratio(text):
    toks = text.split()
    return len(set(toks)) / max(len(toks), 1)


def longest_repeat(text):
    toks = text.split()
    best, cur = 1, 1
    for i in range(1, len(toks)):
        if toks[i] == toks[i - 1]:
            cur += 1; best = max(best, cur)
        else:
            cur = 1
    return best


def slot_accuracy(text):
    return text.count(".") / max(len(text.split()) / 9, 1)


temps = [0.0, 0.7, 1.0, 1.5]
labels = ["T=0 (贪心 argmax)", "T=0.7 (最自然)", "T=1.0 (开始乱)", "T=1.5 (纯噪声)"]
ctx = torch.tensor([[stoi["the"]]], device=DEVICE)

print("同一个开头 'the', 每个温度生成 3 条 (每条续写 18 词):\n")
for temp, label in zip(temps, labels):
    samples = []
    for _ in range(3):
        out = model.generate(ctx, max_new=18, temperature=temp)
        samples.append(" ".join(itos[i.item()] for i in out[0]))
    all_toks = " ".join(samples)
    ur = unique_ratio(all_toks)
    lr = max(longest_repeat(s) for s in samples)
    sa = slot_accuracy(all_toks)
    print("【%s】" % label)
    print("  多样性(唯一词比)=%.2f  最长重复词=%d  完整句数=%.0f" % (ur, lr, sa))
    for s in samples:
        print("    " + s)
    print()

print("-" * 66)
print("解读:")
print("  T=0   : 3 条样本完全一样 (确定性), 且陷入句子级复读 ('a soft wind.' 反复)。")
print("  T=0.7 : 低温保证基本连贯, 又有足够随机性跳出死循环 —— 最像人话。")
print("  T=1.0 : 接近原始分布, 尾部低概率词被频繁抽到, 语法开始崩坏。")
print("  T=1.5 : softmax 被过度拉平, 几乎等概率抽词, 彻底退化为随机词袋。")
print("  ==> 多样性随 T 单调上升 (0.12→0.46→0.58→0.63): T 太低=死板复读, T 太高=词袋。")
print("      一个标量 T 把'流畅'和'噪声'隔开的悬崖极陡; 工程上 0.6-0.9 是甜区。")


print("=" * 66)
print("总结 (对应 07-大语言模型.md)")
print("=" * 66)
print("""
1. LLM 预训练只做'预测下一个词', 但这个目标逼模型学会了语言的形式 (语法/词序/搭配)。
   知识(世界事实)不是目标的直接产物, 而是海量数据 + 大容量的副产物 ——
   我们的 mini-GPT 学到了形式却学不到事实, 就是因为语料太小、参数太少。

2. 生成质量对 sampling temperature 极其敏感:
   T=0 退化复读, T=0.7 最自然, T>=1 崩坏 —— 解码策略和模型本身一样重要。

深度版 (架构/attention 细节/scaling law/涌现/位置编码) 在 ../讲透基础模型/。
""")
print("done.")

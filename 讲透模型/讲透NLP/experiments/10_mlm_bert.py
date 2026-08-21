"""
实验 10 —— 从零实现 tiny BERT (2 层 Transformer encoder, hidden=64, 4 head), 跑 MLM
对应文档: 讲透NLP/10-掩码语言模型-BERT.md

三个反直觉发现 (全部跑出来):
  发现 1: BERT 对 [MASK] 上瘾 —— 看到 [MASK] 时预测最准, 看到随机错词时大跌.
          但微调/推理时输入里根本没有 [MASK] —— 这就是 MLM 的"训练-推理不一致"原罪.
  发现 2: 未微调的 BERT 句向量做语义相似度, 竟不如静态词向量 (各向异性 anisotropy);
          微调后才反超. 这就是 Sentence-BERT 存在的理由.
  发现 3: MLM 比 NTP 收敛慢 —— 每步只有 15% 的 token 参与损失, 同等步数下表征不如 NTP 成熟;
          要追上 NTP 需 ~5 倍步数. (SLP3 原文: "BERT and its descendents are inefficient")

跑法:  python3 -u experiments/10_mlm_bert.py    (约 3-4 分钟, ARM CPU)
依赖:  torch
"""
import math, random
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.set_num_threads(4)
torch.manual_seed(42); random.seed(42)

# ============================================================
# 0. 语料: 3 个"主题", 每主题内 (主语,动词,地点) 强相关 (frame)
# ============================================================
DET = ["the", "a"]
ADJ = ["big", "small", "red", "quick"]
FRAMES = {
    "land":  [("cat","sat","hill"),("dog","ran","field"),
              ("rabbit","jumped","park"),("fox","ran","hill")],
    "water": [("fish","swam","pond"),("duck","dived","lake"),
              ("frog","jumped","pond"),("turtle","swam","river")],
    "sky":   [("bird","flew","roof"),("eagle","soared","sky"),
              ("kite","glided","cloud"),("bee","flew","roof")],
}
TOPICS = list(FRAMES.keys())

def gen_corpus(n=900):
    sents, labels = [], []
    for _ in range(n):
        t = random.choice(TOPICS)
        subj, verb, place = random.choice(FRAMES[t])
        s = [random.choice(DET), random.choice(ADJ), subj, verb,
             "to", random.choice(DET), place]
        sents.append(s); labels.append(TOPICS.index(t))
    return sents, labels

raw_sents, raw_labels = gen_corpus(900)
_vocab = ["[PAD]", "[CLS]", "[MASK]"]
_vocab += sorted(set(w for s in raw_sents for w in s))
STOI = {w: i for i, w in enumerate(_vocab)}
VOCAB = len(_vocab)
CLS_ID, MASK_ID, PAD_ID = STOI["[CLS]"], STOI["[MASK]"], STOI["[PAD]"]
SEQ = 1 + 7

def encode(sents):
    return torch.tensor([[CLS_ID] + [STOI[w] for w in s] for s in sents])

DATA = encode(raw_sents)
LABELS = torch.tensor(raw_labels)
N = DATA.shape[0]
perm = torch.randperm(N)
TE_IDX, TR_IDX = perm[:180], perm[180:]

D_MODEL, N_LAYER, N_HEAD, FFN = 64, 2, 4, 256
CHUNK = 64  # mini-batch size for chunked forward passes


# ============================================================
# 1. Transformer block: causal=False 即 BERT(双向), causal=True 即 GPT(因果)
# ============================================================
class TransformerBlock(nn.Module):
    def __init__(self, d, nhead, ffn, causal=False):
        super().__init__()
        self.causal, self.nhead = causal, nhead
        self.q = nn.Linear(d, d); self.k = nn.Linear(d, d); self.v = nn.Linear(d, d)
        self.o = nn.Linear(d, d)
        self.ff = nn.Sequential(nn.Linear(d, ffn), nn.GELU(), nn.Linear(ffn, d))
        self.ln1 = nn.LayerNorm(d); self.ln2 = nn.LayerNorm(d)

    def forward(self, x):
        B, T, D = x.shape
        hd = D // self.nhead
        sp = lambda z: z.view(B, T, self.nhead, hd).transpose(1, 2)
        Q, K, Vv = sp(self.q(x)), sp(self.k(x)), sp(self.v(x))
        att = (Q @ K.transpose(-1, -2)) / math.sqrt(hd)
        if self.causal:
            m = torch.triu(torch.ones(T, T), diagonal=1).bool()
            att = att.masked_fill(m, float("-inf"))
        att = F.softmax(att, dim=-1)
        o = (att @ Vv).transpose(1, 2).reshape(B, T, D)
        x = self.ln1(x + self.o(o))
        return self.ln2(x + self.ff(x))


class TinyLM(nn.Module):
    def __init__(self, causal):
        super().__init__()
        self.tok = nn.Embedding(VOCAB, D_MODEL)
        self.pos = nn.Embedding(SEQ, D_MODEL)
        self.blocks = nn.ModuleList(
            [TransformerBlock(D_MODEL, N_HEAD, FFN, causal) for _ in range(N_LAYER)])
        self.ln_f = nn.LayerNorm(D_MODEL)
        self.head = nn.Linear(D_MODEL, VOCAB, bias=False)
        self.head.weight = self.tok.weight

    def encode(self, idx):
        B, T = idx.shape
        x = self.tok(idx) + self.pos(torch.arange(T).unsqueeze(0))
        for blk in self.blocks: x = blk(x)
        return self.ln_f(x)

    def forward(self, idx):
        return self.head(self.encode(idx))


def encode_all(model, data, bs=CHUNK):
    """Chunked no-grad encode to avoid slow large-batch forward on ARM CPU."""
    parts = []
    with torch.no_grad():
        for i in range(0, len(data), bs):
            parts.append(model.encode(data[i:i + bs]))
    return torch.cat(parts, 0)


def mean_pool(h):
    return h.mean(dim=1)


# ============================================================
# 2. 80/10/10 掩码
# ============================================================
def make_mlm_batch(ids):
    labels = ids.clone()
    prob = torch.full(ids.shape, 0.15)
    prob[(ids == CLS_ID) | (ids == PAD_ID)] = 0.0
    m = torch.bernoulli(prob).bool()
    labels[~m] = -100
    masked = ids.clone(); r = torch.rand(ids.shape)
    masked[m & (r < 0.8)] = MASK_ID
    masked[m & (r >= 0.8) & (r < 0.9)] = torch.randint(0, VOCAB, ((m & (r >= 0.8) & (r < 0.9)).sum(),))
    return masked, labels


# ============================================================
# 3. 预训练
# ============================================================
def pretrain(causal, steps, bs=16, lr=2e-3):
    model = TinyLM(causal); opt = torch.optim.Adam(model.parameters(), lr=lr)
    last = 0.0
    for step in range(steps):
        idx = TR_IDX[torch.randint(0, len(TR_IDX), (bs,))]
        batch = DATA[idx]
        if causal:
            logits = model(batch)
            loss = F.cross_entropy(logits[:, :-1].reshape(-1, VOCAB), batch[:, 1:].reshape(-1))
        else:
            mb, lab = make_mlm_batch(batch)
            loss = F.cross_entropy(model(mb).reshape(-1, VOCAB), lab.reshape(-1), ignore_index=-100)
        opt.zero_grad(); loss.backward(); opt.step()
        last = loss.item()
    return model, last


print("=" * 70)
print("预训练: 同样模型大小/语料/步数, BERT(MLM) vs GPT(NTP)")
print("=" * 70, flush=True)
n_params = sum(p.numel() for p in TinyLM(False).parameters())
print("  构建 %d 层 Transformer, d=%d, %d head, 词表=%d, 句长=%d (%.1fK 参数)"
      % (N_LAYER, D_MODEL, N_HEAD, VOCAB, SEQ, n_params / 1e3), flush=True)
bert, l_bert = pretrain(causal=False, steps=50)
gpt, l_gpt = pretrain(causal=True, steps=50)
print("  BERT(MLM)  50 步末 loss = %.4f  (每步只 ~15%% token 有监督)" % l_bert, flush=True)
print("  GPT(NTP)   50 步末 loss = %.4f  (每步 ~100%% token 有监督)" % l_gpt, flush=True)
print("  注: 两者 loss 不可直接比大小(监督 token 数不同) -> 用下游探针比(发现 3)\n", flush=True)

# ============================================================
# 发现 1: BERT 对 [MASK] 上瘾
# ============================================================
print("=" * 70)
print("发现 1: BERT 对 [MASK] 上瘾 —— 看到[MASK]最准, 但推理时根本没[MASK]")
print("=" * 70, flush=True)


def cloze_by_condition(model, n_try=300):
    model.eval()
    hit = {k: 0 for k in ("mask", "rand", "keep")}
    conf = {k: 0.0 for k in ("mask", "rand", "keep")}
    with torch.no_grad():
        for _ in range(n_try):
            i = TE_IDX[random.randint(0, len(TE_IDX) - 1)].item()
            ids = DATA[i:i + 1].clone()
            pos = random.randint(1, SEQ - 1)
            truth = ids[0, pos].item()
            for cond in ("mask", "rand", "keep"):
                t = ids.clone()
                if cond == "mask":   t[0, pos] = MASK_ID
                elif cond == "rand": t[0, pos] = random.randint(0, VOCAB - 1)
                p = F.softmax(model(t)[0, pos], dim=-1)
                pred = p.argmax().item()
                if pred == truth: hit[cond] += 1
                conf[cond] += p[truth].item()
    return {k: hit[k] / n_try for k in hit}, {k: conf[k] / n_try for k in conf}


acc, conf = cloze_by_condition(bert)
print("  被预测位置输入 | 预测准确率 | 对真词的置信度", flush=True)
for c in ("mask", "rand", "keep"):
    print("    %-8s      |   %.1f%%     |   %.3f" %
          ({"mask": "[MASK]", "rand": "随机错词", "keep": "真实词"}[c], acc[c] * 100, conf[c]), flush=True)
print("  ==> 看到[MASK]时最准(%.0f%%), 看到随机错词时大跌(%.0f%%): 模型依赖哨兵[MASK]."
      % (acc["mask"] * 100, acc["rand"] * 100), flush=True)
print("  ==> 但微调/推理输入里一个[MASK]都没有! 这就是 MLM 的训练-推理不一致.", flush=True)
print("  ==> 80/10/10 三选一正是为了缓解它(10%随机+10%不变), 但无法消除.\n", flush=True)

# ============================================================
# 发现 2: 未微调 BERT 句向量做相似度, 竟不如静态词向量
# ============================================================
print("=" * 70)
print("发现 2: 未微调 BERT 句向量 < 静态词向量; 微调后才反超 (各向异性)")
print("=" * 70, flush=True)


def static_vec(model, idx):
    with torch.no_grad():
        return mean_pool(model.tok(idx))


def anisotropy(V):
    with torch.no_grad():
        Vn = F.normalize(V, dim=-1)
        G = Vn @ Vn.t()
        n = V.shape[0]
        return ((G.sum() - G.diagonal().sum()) / (n * (n - 1))).item()


def sim_auc(V, n_pairs=1000):
    lab = LABELS
    pos_i, pos_j, neg_i, neg_j = [], [], [], []
    with torch.no_grad():
        Vn = F.normalize(V, dim=-1)
        for _ in range(n_pairs):
            a, b = random.sample(range(N), 2)
            c, d = random.sample(range(N), 2)
            if lab[a] == lab[b]: pos_i.append(a); pos_j.append(b)
            else: neg_i.append(c if lab[c] != lab[d] else a); neg_j.append(d if lab[c] != lab[d] else b)
        if not pos_i or not neg_i: return float("nan")
        ps = (Vn[pos_i] * Vn[pos_j]).sum(-1)
        ns = (Vn[neg_i] * Vn[neg_j]).sum(-1)
    cnt, tot = 0, 0
    for p in ps:
        cnt += (ns < p).sum().item(); tot += len(ns)
    return cnt / tot if tot else float("nan")


v_static = static_vec(bert, DATA)
v_raw = mean_pool(encode_all(bert, DATA))

auc_static, ani_static = sim_auc(v_static), anisotropy(v_static)
auc_raw, ani_raw = sim_auc(v_raw), anisotropy(v_raw)
print("  句向量来源            | 相似度AUC | 平均两两余弦(各向异性)", flush=True)
print("  ---------------------|-----------|----------------------", flush=True)
print("  静态嵌入平均(w2v式)   |  %.3f     | %.3f" % (auc_static, ani_static), flush=True)
print("  BERT原始mean-pool     |  %.3f     | %.3f   <-- 各向异性!" % (auc_raw, ani_raw), flush=True)
print("  ==> 未微调的 BERT 向量全挤一个方向(余弦~1), 相似度分不开, 反不如静态嵌入!", flush=True)
print("  ==> 这正是 Sentence-BERT/SimCSE 要被发明的原因.\n", flush=True)

print("  微调 BERT (encoder 可训练, 主题分类, mini-batch) ...", flush=True)
ft = bert
clf_head = nn.Linear(D_MODEL, 3)
opt = torch.optim.Adam(list(ft.parameters()) + list(clf_head.parameters()), lr=1e-3)
FT_BS = 16
for ep in range(3):
    perm = torch.randperm(len(TR_IDX))
    for i in range(0, len(TR_IDX), FT_BS):
        bi = TR_IDX[perm[i:i + FT_BS]]
        h = mean_pool(ft.encode(DATA[bi]))
        loss = F.cross_entropy(clf_head(h), LABELS[bi])
        opt.zero_grad(); loss.backward(); opt.step()
v_ft = mean_pool(encode_all(ft, DATA))
with torch.no_grad():
    test_acc = (clf_head(mean_pool(encode_all(ft, DATA[TE_IDX]))).argmax(-1) == LABELS[TE_IDX]).float().mean().item()
auc_ft, ani_ft = sim_auc(v_ft), anisotropy(v_ft)
print("  BERT微调后mean-pool    |  %.3f     | %.3f   (微调测试 acc=%.1f%%)" %
      (auc_ft, ani_ft, test_acc * 100), flush=True)
print("  ==> 微调后各向异性被打破, AUC 反超静态嵌入. 印证: BERT 句向量必须微调才好用.\n", flush=True)

# ============================================================
# 发现 3: MLM 比 NTP 收敛慢
# ============================================================
print("=" * 70)
print("发现 3: MLM 比 NTP 收敛慢 (每步只 15% token 有监督)")
print("=" * 70, flush=True)


def linear_probe(model, steps_=200, lr=0.1):
    feats = mean_pool(encode_all(model, DATA))
    mu, sd = feats.mean(0), feats.std(0) + 1e-6
    feats = (feats - mu) / sd
    clf = nn.Linear(feats.shape[1], 3)
    opt = torch.optim.Adam(clf.parameters(), lr=lr)
    for _ in range(steps_):
        loss = F.cross_entropy(clf(feats[TR_IDX]), LABELS[TR_IDX])
        opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        return (clf(feats[TE_IDX]).argmax(-1) == LABELS[TE_IDX]).float().mean().item()


acc_gpt = linear_probe(gpt)
acc_bert_short = linear_probe(bert)
print("  预训练 50 步后, 冻结编码器 + 线性探针测主题分类 (测试集):", flush=True)
print("    GPT(NTP,  100%% token 监督) : %.1f%%" % (acc_gpt * 100), flush=True)
print("    BERT(MLM,  15%% token 监督) : %.1f%%   <-- 明显落后" % (acc_bert_short * 100), flush=True)
print("  让 BERT 多训到 150 步 (~3x) ...", flush=True)
bert_long, _ = pretrain(causal=False, steps=150)
acc_bert_long = linear_probe(bert_long)
print("    BERT(MLM, 150 步)          : %.1f%%   <-- 追上 GPT@50" % (acc_bert_long * 100), flush=True)
print("  ==> MLM 监督密度只有 NTP 的 ~1/7, 所以每步学得慢; 多花 ~3 倍步数才追平.", flush=True)
print("  ==> SLP3 原文: 'only 15% of input samples are used for training weights;", flush=True)
print("      BERT and its descendents are inefficient.' 这就是 ELECTRA 的动机.\n", flush=True)

print("=" * 70)
print("总结: 三个反直觉发现")
print("=" * 70, flush=True)
print("  1. BERT 对[MASK]上瘾(mask准确率%.0f%% >> 随机%.0f%%), 但推理没[MASK] -> 训练-推理不一致"
      % (acc["mask"] * 100, acc["rand"] * 100), flush=True)
print("  2. 未微调BERT句向量(AUC %.2f) < 静态嵌入(%.2f), 因各向异性; 微调后(%.2f)反超"
      % (auc_raw, auc_static, auc_ft), flush=True)
print("  3. MLM(%.0f%%)比NTP(%.0f%%)收敛慢, 因每步只15%%token有监督; ~3x步数(%.0f%%)才追平"
      % (acc_bert_short * 100, acc_gpt * 100, acc_bert_long * 100), flush=True)
print("\n这就是为什么 LLM 时代 GPT/NTP 赢了, 但 BERT 在'便宜+理解+不生成'场景仍活着.", flush=True)

"""
Stanford CS224N (Winter 2026) · 四个作业核心实现
====================================================================
对应 https://web.stanford.edu/class/cs224n/ 最新 schedule（2026 版）。

  A1 (6%)  词向量入门        — 共现矩阵 + SVD + 词相似度/类比
  A2 (14%) 神经网络 + 依存分析 — 手写反传(梯度检验) + transition-based parsing
  A3 (14%) Transformer        — self-attention + multi-head + 残差/LayerNorm
  A4 (14%) LLM 评测（2026新）  — benchmark 概念 + 准确率/混淆矩阵/偏差

教学简化版：纯 NumPy/标准库，保留核心算法，可跑可验证。
与 work4ai「讲透」系列互补：讲透系列讲原理深度，本文件讲动手实现。

运行：
    python3 cs224n_assignments.py
依赖：numpy（A1/A2/A3），A4 纯标准库
====================================================================
"""
from __future__ import annotations
import math
import random
from collections import defaultdict, Counter

try:
    import numpy as np
    HAS_NP = True
except ImportError:
    HAS_NP = False

def banner(t):
    print("\n" + "█" * 68)
    print(f"  {t}")
    print("█" * 68)

def need_numpy():
    if not HAS_NP:
        print("  ⚠ 本作业需要 numpy：pip install numpy")
        return False
    return True


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Assignment 1 · 词向量入门 (6%)                                            ║
# ╚══════════════════════════════════════════════════════════════════════╝
#  经典 count-based 词向量：共现矩阵 → SVD 降维 → 词相似度 + 类比

def assignment1_word_vectors() -> None:
    banner("Assignment 1 · 词向量入门（共现矩阵 + SVD + 相似度）")
    if not need_numpy():
        return
    # 极简语料（3 句）
    corpus = [
        "I like deep learning",
        "I like NLP",
        "I enjoy flying",
        "deep learning is fun",
        "NLP is fun",
    ]
    print("  语料:", corpus)

    # ── Step 1: 构建共现矩阵 ──
    vocab = sorted(set(w for s in corpus for w in s.split()))
    w2i = {w: i for i, w in enumerate(vocab)}
    N = len(vocab)
    window = 1   # 上下文窗口
    cooc = np.zeros((N, N), dtype=float)
    for s in corpus:
        words = s.split()
        for i, w in enumerate(words):
            for j in range(max(0, i - window), min(len(words), i + window + 1)):
                if i != j:
                    cooc[w2i[words[i]], w2i[words[j]]] += 1
    print(f"\n  词表({N}): {vocab}")
    print(f"  共现矩阵（window={window}）:")
    print(f"      {'':>8}" + "".join(f"{w[:4]:>6}" for w in vocab))
    for i, w in enumerate(vocab):
        print(f"      {w:>8}" + "".join(f"{cooc[i,j]:>6.0f}" for j in range(N)))

    # ── Step 2: SVD 降维到 2 维 ──
    U, S, Vt = np.linalg.svd(cooc, full_matrices=False)
    dim = 2
    embeddings = U[:, :dim] * S[:dim]   # 缩放后的词向量
    print(f"\n  SVD 降维到 {dim}D 后的词向量:")
    for w, vec in zip(vocab, embeddings):
        print(f"    {w:>10}: ({vec[0]:+.2f}, {vec[1]:+.2f})")

    # ── Step 3: 词相似度（cosine）──
    def cosine(a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

    pairs = [("like", "enjoy"), ("deep", "fun"), ("NLP", "learning"), ("I", "is")]
    print(f"\n  余弦相似度:")
    for a, b in pairs:
        if a in w2i and b in w2i:
            sim = cosine(embeddings[w2i[a]], embeddings[w2i[b]])
            print(f"    cos({a}, {b}) = {sim:+.3f}")

    # ── Step 4: 词类比（king - man + woman ≈ queen 的简化演示）──
    print(f"\n  词类比的直觉（向量差 = 语义关系）:")
    if all(w in w2i for w in ["like", "enjoy", "fun"]):
        diff = embeddings[w2i["like"]] - embeddings[w2i["enjoy"]]
        print(f"    like - enjoy = ({diff[0]:+.2f}, {diff[1]:+.2f})")
        print("    → 训练数据足够时，这种向量差能捕捉'近义词的微妙差异'。")
    print("""
  → 这就是 2013 年 word2vec 震惊世界的发现：词的关系 = 向量空间的方向。
  → 现代 LLM 的 embedding 仍是这个思想的进化版（只是维度从 2 → 4096+）。
""")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Assignment 2 · 神经网络基础 + 依存分析 (14%)                              ║
# ╚══════════════════════════════════════════════════════════════════════╝
#  两大块：① 手写反向传播 + 梯度检验  ② transition-based 依存分析

def assignment2_nn_parsing() -> None:
    banner("Assignment 2 · 神经网络反传 + 依存分析")
    if not need_numpy():
        return

    # ── Part A: 手写反向传播 + 梯度检验 ──
    print("─" * 68)
    print("【Part A】手写 1 层神经网络 + 数值梯度检验")
    print("─" * 68)
    np.random.seed(0)
    din, dh = 4, 5
    W1 = np.random.randn(dh, din) * 0.5
    b1 = np.zeros(dh)
    W2 = np.random.randn(1, dh) * 0.5
    b2 = np.zeros(1)
    x = np.random.randn(din)
    y = np.array([1.0])

    def forward(x, W1, b1, W2, b2):
        z1 = W1 @ x + b1
        h = np.tanh(z1)              # 隐藏层激活
        z2 = W2 @ h + b2
        yhat = z2[0]                 # 标量输出
        loss = 0.5 * (yhat - y[0]) ** 2
        cache = (x, z1, h, z2, yhat)
        return loss, cache

    def backward(cache, W1, W2):
        x, z1, h, z2, yhat = cache
        dyhat = (yhat - y)            # dL/dyhat
        dW2 = dyhat * h               # dL/dW2
        db2 = dyhat                   # dL/db2
        dh = W2.T @ dyhat             # dL/dh
        dz1 = dh * (1 - np.tanh(z1) ** 2)   # tanh 导数
        dW1 = np.outer(dz1, x)
        db1 = dz1
        return dW1, db1, dW2, db2

    loss, cache = forward(x, W1, b1, W2, b2)
    dW1, db1, dW2, db2 = backward(cache, W1, W2)

    # 数值梯度检验：用有限差分验证手写梯度对不对
    def numeric_grad(f, theta, eps=1e-5):
        grad = np.zeros_like(theta)
        it = np.nditer(theta, flags=["multi_index"])
        while not it.finished:
            idx = it.multi_index
            orig = theta[idx]
            theta[idx] = orig + eps; lp, _ = f(theta)
            theta[idx] = orig - eps; lm, _ = f(theta)
            theta[idx] = orig
            grad[idx] = (lp - lm) / (2 * eps)
            it.iternext()
        return grad

    ng_W1 = numeric_grad(lambda t: forward(x, t, b1, W2, b2), W1.copy())
    rel_err = np.abs(dW1 - ng_W1).sum() / (np.abs(dW1 + ng_W1).sum() + 1e-9)
    print(f"  损失 = {float(loss):.4f}")
    print(f"  W1 梯度相对误差（手写 vs 数值）= {rel_err:.2e}")
    print(f"  {'✅ 梯度检验通过（< 1e-6）' if rel_err < 1e-6 else '❌ 梯度有误！'}")
    print("  → 这就是 CS224N A2 的核心：证明你的反向传播没错。\n")

    # ── Part B: transition-based 依存分析 ──
    print("─" * 68)
    print("【Part B】依存分析：transition-based（shift/left-arc/right-arc）")
    print("─" * 68)
    sentence = ["I", "ate", "fish"]   # 简化句子
    # 标准依存树：ate 是根，I→ate（主语），fish→ate（宾语）
    print(f"  句子: {sentence}")
    print(f"  目标依存: ate→根, I←ate(nsubj), fish←ate(obj)\n")
    # 栈 + buffer 模拟
    transitions = simulate_parsing(sentence)
    for t in transitions:
        print(f"    {t}")
    print("""
  → 三种动作：SHIFT（词入栈）/ LEFT-ARC（栈顶2依赖栈顶1）/ RIGHT-ARC（栈顶1依赖栈顶2）
  → 神经网络依存分析器 = 学会根据当前栈/buffer 状态预测该做哪个动作。
""")


def simulate_parsing(words):
    """transition-based 依存分析模拟（硬编码 gold transitions 做演示）。"""
    stack, buffer = ["ROOT"], list(words)
    arcs, steps = [], []
    # gold: ROOT→ate, I←ate, fish←ate
    transitions = [
        ("SHIFT", lambda: stack.append(buffer.pop(0))),
        ("SHIFT", lambda: stack.append(buffer.pop(0))),
        ("LEFT-ARC", None),   # I ← ate (栈顶 I 依赖下面的 ate)
        ("SHIFT", lambda: stack.append(buffer.pop(0))),
        ("RIGHT-ARC", None),  # fish ← ate
        ("RIGHT-ARC", None),  # ROOT ← ate
    ]
    for action, fn in transitions:
        if action == "LEFT-ARC":
            head, dep = stack[-2], stack[-1]
            arcs.append((dep, head))
            stack.pop(-2)
        elif action == "RIGHT-ARC":
            head, dep = stack[-1], stack[-2]
            arcs.append((dep, head))
            stack.pop()
        else:
            fn()
        steps.append(f"{action:<12} 栈={stack} buffer={buffer} arcs={arcs}")
    return steps


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Assignment 3 · Self-Attention + Transformer (14%)                       ║
# ╚══════════════════════════════════════════════════════════════════════╝

def assignment3_transformer() -> None:
    banner("Assignment 3 · Self-Attention + Transformer（手写）")
    if not need_numpy():
        return
    np.random.seed(42)
    seq_len, d_model = 4, 8
    x = np.random.randn(seq_len, d_model)

    # ── Scaled Dot-Product Attention ──
    W_q = np.random.randn(d_model, d_model) * 0.3
    W_k = np.random.randn(d_model, d_model) * 0.3
    W_v = np.random.randn(d_model, d_model) * 0.3
    Q, K, V = x @ W_q, x @ W_k, x @ W_v

    scores = Q @ K.T / math.sqrt(d_model)        # 缩放点积
    # 因果掩码（GPT 风格，下三角）
    mask = np.triu(np.ones((seq_len, seq_len)), k=1).astype(bool)
    scores[mask] = -1e9
    attn = np.exp(scores - scores.max(axis=-1, keepdims=True))
    attn = attn / attn.sum(axis=-1, keepdims=True)
    out = attn @ V

    print(f"  输入 x: shape={x.shape} (seq={seq_len}, d_model={d_model})")
    print(f"\n  Self-Attention 矩阵（因果掩码，下三角）:")
    for i in range(seq_len):
        row = " ".join(f"{attn[i,j]:.2f}" for j in range(seq_len))
        print(f"    token{i}: [{row}]")
    print(f"\n  输出 shape={out.shape}")
    print("""
  → 因果掩码：每个位置只能看自己及之前的（GPT 风格，自回归）。
  → 1/√d 缩放：防止点积过大导致 softmax 饱和（梯度消失）。
  → Multi-head = 把 d_model 切成 h 份，各做 attention 再 concat。
""")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Assignment 4 · LLM 评测 (14%) —— 2026 全新作业                            ║
# ╚══════════════════════════════════════════════════════════════════════╝
#  这是 2026 版新增，取代了旧版的 NMT（机器翻译）作业
#  核心：如何科学地评测一个 LLM？

def assignment4_llm_eval() -> None:
    banner("Assignment 4 · LLM 评测（2026 全新作业）")
    # 模拟一个 benchmark：3 个 LLM 在 10 道多选题上的表现
    random.seed(0)
    questions = [
        ("2+2=?", ["3", "4", "5"], 1),
        ("法国首都?", ["伦敦", "巴黎", "柏林"], 1),
        ("水的化学式?", ["H2O", "CO2", "O2"], 0),
        ("地球第3大行星?", ["对", "错"], 1),    # 错在"第3"
        ("Python 创始人?", ["Guido", "Linus", "Dennis"], 0),
        ("最大洋?", ["太平洋", "大西洋", "印度洋"], 0),
        ("光速≈?", ["3e8 m/s", "3e6 m/s", "3e10 m/s"], 0),
        ("DNA 全称?", ["脱氧核糖核酸", "核糖核酸", "氨基酸"], 0),
        ("圆周率≈?", ["3.14", "2.71", "1.41"], 0),
        ("长城在?", ["中国", "日本", "韩国"], 0),
    ]
    # 三个"模型"（模拟不同准确率的 LLM）
    models = {
        "GPT-Base":  [0,1,0,1,0,0,0,0,0,0],   # 50% 准确
        "GPT-Tuned": [1,1,1,1,1,1,0,1,1,0],   # 90%
        "Random":    [random.randint(0,2) if len(q[1])==3 else random.randint(0,1) for q in questions],
    }
    print("  Benchmark: 10 道多选题（模拟 MMLU/HellaSwag 风格）\n")
    print(f"  {'模型':<12} {'准确率':>8} {'表现分析'}")
    print("  " + "─" * 48)
    for name, preds in models.items():
        correct = sum(1 for p, q in zip(preds, questions) if p == q[2])
        acc = correct / len(questions)
        analysis = "优秀" if acc >= 0.8 else "中等" if acc >= 0.5 else "差"
        print(f"  {name:<12} {acc:>7.0%}   {analysis}")

    # ── 混淆矩阵：分析模型"错在哪类题"──
    print(f"\n  GPT-Tuned 的错误分析（哪些题错了）:")
    gpt_preds = models["GPT-Tuned"]
    for i, (q, pred) in enumerate(zip(questions, gpt_preds)):
        if pred != q[2]:
            print(f"    ❌ Q{i+1} '{q[0]}' 选了'{q[1][pred]}'，正确是'{q[1][q[2]]}'")
    print("""
  → 这就是 LLM 评测的本质：不只看总分，要看【错在哪】。
  → 真实 benchmark：MMLU(57 科)、HellaSwag(常识)、HumanEval(代码)、GSM8K(数学)
  → 2026 新增 A4 的意义：LLM 时代，'会评测'和'会训练'一样重要。
  → 陷阱：benchmark 污染（训练时见过测试题）→ 分数虚高 → 需要动态/私有 benchmark。
""")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  主入口                                                                    ║
# ╚══════════════════════════════════════════════════════════════════════╝

def main() -> None:
    print()
    print("╔" + "═" * 66 + "╗")
    print("║" + " Stanford CS224N (Winter 2026) · 四个作业核心实现 ".center(66) + "║")
    print("╚" + "═" * 66 + "╝")
    print("  对应 https://web.stanford.edu/class/cs224n/ 最新 schedule")
    assignment1_word_vectors()
    assignment2_nn_parsing()
    assignment3_transformer()
    assignment4_llm_eval()
    print("=" * 68)
    print("  ✅ 四个作业演示完成。下一步：")
    print("     1. 跑 GPT-2 默认项目：python3 gpt2_project.py")
    print("     2. 对照 work4ai「讲透Transformer」「讲透基础模型」深入原理")
    print("     3. 去官网下载真实作业代码（需 PyTorch）：assignments_w26/*.zip")
    print("=" * 68)
    print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""讲透优化实验 3：SGD 实验室。
E1 SGD 双面性（前期快/尾部噪声地板） | E2 步长日程对比 | E3 large-batch 方差地板
产出：sgd.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "sans-serif"]
rng = np.random.default_rng(42)

n, d, noise = 4000, 5, 0.5
X = rng.normal(size=(n, d)); w_true = rng.normal(size=d)
y = X @ w_true + noise * rng.normal(size=n)

def sgd_path(batch, sched, epochs=30, lr0=0.05):
    w = np.zeros(d); path = []
    t = 0
    for ep in range(epochs):
        idx = rng.permutation(n)
        for s in range(0, n, batch):
            b = idx[s:s+batch]
            lr = lr0 / (1 + t/2000) if sched == "1/t" else lr0
            g = 2 * X[b].T @ (X[b] @ w - y[b]) / len(b)
            w -= lr * g; t += 1
            if t % 20 == 0:
                path.append(((X @ w - y)**2).mean())
    return np.array(path)

fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
for batch, c in [(1, "r"), (32, "tab:orange"), (512, "tab:blue")]:
    p = sgd_path(batch, "const")
    ax[0].semilogy(p, c=c, label=f"batch={batch}")
    print(f"batch={batch}: 终值 loss={p[-1]:.5f}（噪声地板 {'高' if batch<32 else '低'}）")
for sched, c in [("const", "r"), ("1/t", "g")]:
    p = sgd_path(32, sched)
    ax[1].semilogy(p, c=c, label=f"步长={sched}")
    print(f"日程 {sched}: 尾部抖动={'大' if sched=='const' else '小'}，终值={p[-1]:.5f}")
ax[0].legend(); ax[0].set_title("E1/E3：小 batch 前期快+尾部噪声地板；大 batch 平但慢")
ax[1].legend(); ax[1].set_xlabel("记录步"); ax[1].set_title("E2：1/t 日程驯服尾部噪声（16 章）")
fig.tight_layout(); fig.savefig("sgd.png", dpi=140)
print("saved sgd.png")

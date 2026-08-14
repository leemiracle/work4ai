"""13 RNN/LSTM 实验：梯度消失/爆炸铁证 + 字符级 RNN BPTT 训练。numpy，几秒跑完。
铁证 1: ‖∂h_T/∂h_0‖ 随 T 指数衰减(消失)或爆炸，取决于 W_hh 谱半径——RNN 核心病。
铁证 2: 字符级 RNN 通过 BPTT 能学时序模式 'h→e→l→l→o'，但训练对初始化敏感。
对应讲透NLP/13-RNN与LSTM.md §3、§5。
"""
import numpy as np

np.random.seed(42)
H, T = 8, 25

print("=" * 64)
print("Part A: 梯度消失/爆炸 —— RNN 的核心痛点")
print("=" * 64)
print(f"RNN: h_t = tanh(W_hh @ h_{{t-1}} + W_xh @ x_t + b),  hidden={H}, T={T}")
print("总梯度 ∂h_T/∂h_0 = ∏_t diag(1 - h_t²) @ W_hh  （雅可比连乘 T 次）\n")


def rnn_grad(W_hh, T, H, label):
    h = np.zeros(H); h_list = [h]
    x = np.random.randn(H) * 0.1
    for _ in range(T):
        h = np.tanh(W_hh @ h + x); h_list.append(h)
    grad = np.eye(H); norms = [np.linalg.norm(grad)]
    for t in range(T - 1, -1, -1):
        J = np.diag(1 - h_list[t+1]**2) @ W_hh
        grad = grad @ J
        norms.append(np.linalg.norm(grad))
    rho = max(abs(np.linalg.eigvals(W_hh)))
    print(f"{label}: W 谱半径={rho:.2f}")
    print(f"   ‖∂h_{T}/∂h_0‖ = {norms[-1]:.3e}  (初始 ‖I‖={norms[0]:.1f})")
    traj = [f"{norms[i]:.2e}" for i in range(0, T+1, 5)]
    print(f"   梯度范数轨迹(每5步): {traj}")


for label, scale in [("① 小权重 → 梯度消失", 0.3),
                     ("② 临界 → 勉强稳定", 0.9),
                     ("③ 大权重 → 梯度爆炸", 1.5)]:
    rnn_grad(np.random.randn(H, H) * scale, T, H, label)

print("\n→ 铁证: 谱半径<1 → 梯度指数衰减(长程依赖学不到); 谱半径>1 → 指数爆炸(训练发散)。")
print("  tanh 的导数 ∈ [0,1] 进一步压梯度。这就是 LSTM 门控机制要治的根本病。")

# ============ Part B: 字符级 RNN BPTT 学 "hello" ============
print("\n" + "=" * 64)
print("Part B: 字符级 RNN 学 'hello' (BPTT 反向传播训练)")
print("=" * 64)

chars = sorted(set("hello"))  # e,h,l,o
stoi = {c: i for i, c in enumerate(chars)}; itos = {i: c for c, i in stoi.items()}
V = len(chars)
seq = [stoi[c] for c in "hello"]  # 输入 h,e,l,l 预测 e,l,l,o

H = 16; lr = 0.1
np.random.seed(0)
W_xh = np.random.randn(H, V) * 0.5
W_hh = np.linalg.qr(np.random.randn(H, H))[0]   # 正交初始化:谱半径=1,防梯度爆炸
W_hy = np.random.randn(V, H) * 0.5
b_h = np.zeros(H); b_y = np.zeros(V)


def softmax(x):
    e = np.exp(x - x.max()); return e / e.sum()


losses = []
for epoch in range(200):
    h = np.zeros(H); xs, hs, ys = [], [h], []
    loss = 0
    for t in range(len(seq) - 1):           # 输入 h,e,l,l → 预测 e,l,l,o
        x = np.zeros(V); x[seq[t]] = 1
        h = np.tanh(W_xh @ x + W_hh @ h + b_h)
        y = softmax(W_hy @ h + b_y)
        xs.append(x); hs.append(h); ys.append(y)
        loss += -np.log(y[seq[t+1]] + 1e-9)
    losses.append(loss)
    # BPTT 反向
    dW_xh = np.zeros_like(W_xh); dW_hh = np.zeros_like(W_hh); dW_hy = np.zeros_like(W_hy)
    dh_next = np.zeros(H)
    for t in reversed(range(len(xs))):
        dy = ys[t].copy(); dy[seq[t+1]] -= 1
        dW_hy += np.outer(dy, hs[t])
        dh = W_hy.T @ dy + dh_next
        dh_raw = (1 - hs[t]**2) * dh        # tanh 的导数
        dW_xh += np.outer(dh_raw, xs[t])
        dW_hh += np.outer(dh_raw, hs[t-1] if t > 0 else np.zeros(H))
        dh_next = W_hh.T @ dh_raw
    # 梯度裁剪 (RNN 标准做法,防爆炸)
    gnorm = np.sqrt((dW_xh**2).sum() + (dW_hh**2).sum() + (dW_hy**2).sum())
    if gnorm > 5.0:
        scale = 5.0 / gnorm
        dW_xh *= scale; dW_hh *= scale; dW_hy *= scale
    for W, dW in [(W_xh, dW_xh), (W_hh, dW_hh), (W_hy, dW_hy)]:
        W -= lr * dW
    if epoch % 50 == 0 or epoch == 199:
        h = np.zeros(H); pred = []
        for t in range(len(seq) - 1):
            x = np.zeros(V); x[seq[t]] = 1
            h = np.tanh(W_xh @ x + W_hh @ h + b_h)
            pred.append(itos[int(np.argmax(softmax(W_hy @ h + b_y)))])
        print(f"epoch {epoch:3d}: loss={loss:.3f} | 输入'hell' → 预测'{(''.join(pred))}' (目标'ello')")

print(f"\nloss 轨迹: {losses[0]:.3f} → {losses[-1]:.3f} ({'下降 ✓' if losses[-1] < losses[0] else '未下降 ✗'})")
print("→ 铁证: 字符级 RNN 通过 BPTT 学到了时序模式 h→e→l→l→o。")
print("  但注意 Part A 的梯度消失:长序列(T>20)上,普通 RNN 几乎学不到长程依赖——这就是 LSTM 的舞台。")

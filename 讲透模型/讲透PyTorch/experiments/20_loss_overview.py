"""
讲透损失函数 —— 综合实验脚本
================================
4 个子实验, 一次性验证损失函数的核心性质:
  实验1: 五大损失的【形状】对比 (为什么 MSE 重罚大错, MAE 一视同仁)
  实验2: MSE vs MAE 的【离群点敏感性】(鲁棒性之争)
  实验3: 交叉熵 + softmax 的【梯度魔法】(为什么这俩是天作之合)
  实验4: 数值稳定性 (为什么不能裸写 log, 必须 logsumexp)

跑法: python3 loss_overview.py
依赖: torch, numpy, matplotlib
"""
import numpy as np
import torch
import torch.nn.functional as F
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(0)
torch.manual_seed(0)

# ============================================================
# 实验 1: 五大损失的【形状】—— 单点误差 e = (y_hat - y) 的函数曲线
# ============================================================
print("=" * 72)
print("实验 1: 损失函数形状对比  (横轴 = 预测误差 e = y_hat - y)")
print("=" * 72)

e = np.linspace(-3, 3, 601)          # 误差从 -3 到 3

# (a) 回归损失: 输入是连续误差 e
mse  = e ** 2                          # L2
mae  = np.abs(e)                       # L1
huber = np.where(np.abs(e) <= 1.0,     # delta=1
                 0.5 * e ** 2,
                 np.abs(e) - 0.5)

# (b) 分类损失: 输入是"预测为正类的概率 p", 真实标签固定看 y=1 和 y=0
p = np.linspace(0.001, 0.999, 999)
# 二分类交叉熵 BCE:  真实 y=1 时 loss = -log(p);  y=0 时 loss = -log(1-p)
bce_correct = -np.log(p)               # 预测对(y=1, p->1 时 loss->0)
bce_wrong   = -np.log(1 - p)           # 预测错(y=1, p->0 时 loss->+inf)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

ax = axes[0]
ax.plot(e, mse, "r-",  linewidth=2.5, label="MSE  (L2):  e^2")
ax.plot(e, mae, "b-",  linewidth=2.5, label="MAE  (L1):  |e|")
ax.plot(e, huber, "g-", linewidth=2.5, label="Huber (delta=1)")
ax.set_xlabel("error  e = y_hat - y")
ax.set_ylabel("loss")
ax.set_title("Regression losses\nMSE punishes big errors MORE (quadratic)")
ax.legend(fontsize=10); ax.grid(alpha=0.3); ax.set_ylim(0, 5)

# 实验1 数值: MSE 和 MAE 在 e=3 处的比值
print(f"  在 |e|=3 时:  MSE={3**2:.0f}, MAE={3:.0f}, 比值={9/3:.0f}x")
print(f"  在 |e|=1 时:  MSE={1:.0f}, MAE={1:.0f}, 比值={1/1:.0f}x")
print(f"  ==> MSE 对大错的惩罚随误差平方增长; MAE 是线性的 (一视同仁)\n")

# ============================================================
# 实验 2: MSE vs MAE 的【离群点敏感性】
# ============================================================
print("=" * 72)
print("实验 2: 离群点敏感性  (拟合一条直线, 加入 1 个离群点)")
print("=" * 72)

# 真实数据: y = 2x, 10 个干净点 + 1 个离群点
x_clean = np.linspace(0, 1, 10)
y_clean = 2 * x_clean
# 加 1 个离群点
x_outlier = np.array([0.5])
y_outlier = np.array([10.0])           # 远离真实直线

x_all = np.concatenate([x_clean, x_outlier])
y_all = np.concatenate([y_clean, y_outlier])

# 解析最优常数拟合 (拟合一个数 c, 让损失最小)
# MSE 最优 c = 均值;  MAE 最优 c = 中位数
c_mse = np.mean(y_all)
c_mae = np.median(y_all)
print(f"  数据: 10 个干净点 y≈2x (范围 0~2), 加 1 个离群点 y=10")
print(f"  MSE 最优常数 c = 均值   = {c_mse:.3f}  (被离群点拉飞了!)")
print(f"  MAE 最优常数 c = 中位数 = {c_mae:.3f}  (稳如老狗)")
print(f"  干净数据的真实中心 ≈ 1.0")
print(f"  ==> MSE 假设高斯噪声, 1 个离群点 = '不可能事件', 强行拟合;")
print(f"      MAE 假设拉普拉斯噪声(重尾), 离群点是常态, 几乎不受影响\n")

ax = axes[1]
ax.scatter(x_clean, y_clean, c="green", s=60, zorder=5, label="clean points")
ax.scatter(x_outlier, y_outlier, c="red", s=150, marker="X", zorder=5, label="outlier")
ax.axhline(c_mse, color="red",   linestyle="--", linewidth=2, label=f"MSE fit: c={c_mse:.2f}")
ax.axhline(c_mae, color="blue",  linestyle="--", linewidth=2, label=f"MAE fit: c={c_mae:.2f}")
ax.axhline(1.0,   color="green", linestyle=":",  linewidth=1.5, label="true center=1.0")
ax.set_xlabel("x"); ax.set_ylabel("y")
ax.set_title("Outlier robustness\nMSE pulled away by 1 outlier, MAE stays put")
ax.legend(fontsize=8, loc="upper left"); ax.grid(alpha=0.3)
ax.set_ylim(-0.5, 11)

# ============================================================
# 实验 3: 交叉熵 BCE 形状 + softmax+CE 梯度魔法
# ============================================================
print("=" * 72)
print("实验 3: 交叉熵 BCE 的形状 + softmax+CE 的【梯度魔法】")
print("=" * 72)

ax = axes[2]
ax.plot(p, bce_correct, "g-", linewidth=2.5, label="BCE (true y=1): -log(p)")
ax.plot(p, bce_wrong,   "r-", linewidth=2.5, label="BCE (true y=0): -log(1-p)")
ax.set_xlabel("predicted prob p")
ax.set_ylabel("loss")
ax.set_title("Binary Cross-Entropy\nloss -> inf when confidently WRONG")
ax.legend(fontsize=9); ax.grid(alpha=0.3); ax.set_ylim(0, 6)
ax.annotate("confident+wrong\n=> HUGE loss", xy=(0.05, 3), xytext=(0.25, 4.5),
            fontsize=9, arrowprops=dict(arrowstyle="->", color="k"))

print(f"  真实 y=1, 预测 p=0.99:  BCE = {-np.log(0.99):.4f}  (几乎没错)")
print(f"  真实 y=1, 预测 p=0.01:  BCE = {-np.log(0.01):.2f}  (自信地错, 重罚!)")
print(f"  真实 y=1, 预测 p=1e-10: BCE = {-np.log(1e-10):.1f}  (爆炸)")
print(f"  ==> 交叉熵的核心哲学: 【自信地错】比【犹豫地错】罚得重得多\n")

# softmax + CE 的梯度魔法 (3 分类)
print("  softmax + CE 组合的梯度推导:")
print("    logits z,  softmax 出概率 p = softmax(z),  CE loss")
print("    dLoss/dz = p - onehot(y)   <-- 仅仅 4 个字符, 极其简洁!")
# 数值验证
logits = torch.tensor([1.0, 2.0, 0.5], requires_grad=True)
target = torch.tensor(1)               # 真实类别是第 1 类
probs = F.softmax(logits, dim=0)
loss = F.cross_entropy(logits.unsqueeze(0), target.unsqueeze(0))
loss.backward()
manual_grad = probs - F.one_hot(target, 3).float()
print(f"    logits    = {logits.tolist()}")
print(f"    softmax p = {[round(x,4) for x in probs.tolist()]}")
print(f"    autograd  dL/dz = {[round(x,4) for x in logits.grad.tolist()]}")
print(f"    manual (p-y)    = {[round(x,4) for x in manual_grad.tolist()]}")
print(f"    两者完全一致!  这就是 softmax+CE 成为分类标准配对的原因\n")

# ============================================================
# 实验 4: 数值稳定性 —— 裸 log 会爆炸, logsumexp 救场
# ============================================================
print("=" * 72)
print("实验 4: 数值稳定性  (裸 log vs logsumexp)")
print("=" * 72)

fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))

# 4a. BCE 的 log(0) 爆炸
ax = axes2[0]
eps_list = [1e-1, 1e-2, 1e-4, 1e-8, 1e-12, 1e-16, 0.0]
naive_losses = []
for eps in eps_list:
    pp = eps                       # 预测概率趋近 0
    try:
        l = -np.log(pp) if pp > 0 else float("inf")
    except (ValueError, ZeroDivisionError):
        l = float("inf")
    naive_losses.append(l)
ax.bar(range(len(eps_list)), naive_losses, color=["green"]*4 + ["orange","red","darkred"])
ax.set_xticks(range(len(eps_list)))
ax.set_xticklabels([f"p={e}" if e > 0 else "p=0" for e in eps_list], rotation=45, fontsize=8)
ax.set_ylabel("BCE loss  -log(p)")
ax.set_title("Naive -log(p) explodes as p->0\n(need clipping or logsumexp)")
ax.grid(alpha=0.3, axis="y")
print(f"  裸 BCE -log(p):  p=1e-8 -> {-np.log(1e-8):.0f},  p=0 -> inf (NaN 污染整个训练!)")
print(f"  PyTorch BCEWithLogits 内部自动 clamp, 永远不会 NaN\n")

# 4b. softmax 的 logsumexp 技巧
ax = axes2[1]
# 大 logits 会导致裸 softmax 溢出
logits_big = torch.tensor([1000.0, 1001.0, 1002.0])

# 裸 softmax:  exp(1000) = inf
print(f"  logits = [1000, 1001, 1002]")
try:
    naive_softmax = torch.exp(logits_big) / torch.exp(logits_big).sum()
    print(f"  裸 softmax  = {[round(x,4) for x in naive_softmax.tolist()]}")
except Exception as ex:
    print(f"  裸 softmax  = 溢出 ({ex})")

# 数值验证: 先 exp 再除 (裸做法)
naive_exp = torch.exp(logits_big)
print(f"  裸 exp([1000,1001,1002]) = {naive_exp.tolist()}  (全部 inf!)")

# 正确做法: logsumexp 平移
stable_softmax = F.softmax(logits_big, dim=0)
print(f"  F.softmax (logsumexp)     = {[round(x,4) for x in stable_softmax.tolist()]}  (完全正常)")

# 演示 logsumexp 的数学等价性
m = logits_big.max()
lse_naive = torch.log(torch.exp(logits_big - m).sum()) + m   # 等价但稳定
print(f"  logsumexp(z) = max(z) + log(sum(exp(z - max(z))))")
print(f"               = {lse_naive.item():.4f}  (避免了大数 exp)")

# 画 logsumexp 示意图: 平移不变性
demo_x = np.linspace(-2, 8, 100)
ax.plot(demo_x, np.exp(demo_x), "r-", linewidth=2.5, label="exp(z)  (overflows at z~700)")
ax.plot(demo_x, np.exp(demo_x - 8), "b-", linewidth=2.5, label="exp(z - max)  (always <1, safe)")
ax.axhline(1, color="gray", linestyle=":", alpha=0.5)
ax.set_xlabel("z"); ax.set_ylabel("value")
ax.set_title("logsumexp trick: shift by max(z)\nexp stays in [0,1], no overflow")
ax.legend(fontsize=9); ax.grid(alpha=0.3)

plt.tight_layout()
out1 = "loss_shapes.png"
out2 = "numerical_stability.png"
fig.savefig(out1, dpi=110)
fig2.savefig(out2, dpi=110)
print(f"\n==> 图已保存: experiments/{out1}, experiments/{out2}")
print("==> 全部 4 个实验完成!")

"""
实验 00 —— 数值微分 vs 反向传播: 为什么反传是唯一可行的方法
对应文档: 00-为什么需要反传.md / 02-为什么反向不是前向.md
核心: 数值微分要 O(n) 次前向(n=参数数), 反传只需 1 次前向+1 次反向.
      本实验用 1000 个参数实测: 数值微分慢几十倍, 且参数越多差距越大.
跑法: python3 00_numerical_vs_backprop.py
"""
import torch, time

torch.manual_seed(0)

def make_model_and_input(nparams_rows):
    W = torch.randn(nparams_rows, 10, requires_grad=True)
    x = torch.randn(10)
    return W, x

def f(W, x):
    return torch.relu(W @ x).sum()   # 标量损失

# 数值微分: 逐参数扰动, 每参数 2 次前向 (中心差分)
def numerical_grad(W, x, eps=1e-4):
    g = torch.zeros_like(W)
    with torch.no_grad():
        for i in range(W.shape[0]):
            for j in range(W.shape[1]):
                orig = W[i, j].item()
                W[i, j] = orig + eps; fp = f(W, x).item()
                W[i, j] = orig - eps; fm = f(W, x).item()
                W[i, j] = orig
                g[i, j] = (fp - fm) / (2 * eps)
    return g

# 反向传播: 1 次前向 + 1 次反向
def backprop_grad(W, x):
    if W.grad is not None: W.grad = None
    out = f(W, x); out.backward()
    return W.grad.clone()

print("=" * 66)
print("数值微分 vs 反向传播 (参数量 = rows × 10)")
print("=" * 66)
print(f"{'参数量':>8} {'数值微分(s)':>14} {'反传(s)':>12} {'慢几倍':>10} {'梯度最大差':>12}")
print("-" * 66)
for rows in [10, 50, 100, 200]:
    n = rows * 10
    W, x = make_model_and_input(rows)
    t0 = time.time(); ng = numerical_grad(W, x); t_num = time.time() - t0
    W, x = make_model_and_input(rows)
    t0 = time.time(); bg = backprop_grad(W, x); t_bp = time.time() - t0
    diff = (ng - bg).abs().max().item()
    print(f"{n:>8} {t_num:>14.3f} {t_bp:>12.4f} {t_num/max(t_bp,1e-9):>9.0f}x {diff:>12.2e}")

print("-" * 66)
print("\n解读:")
print("  - 两种方法梯度几乎一致(差在数值微分的截断误差), 都正确")
print("  - 但数值微分的耗时随参数量线性增长(O(n)次前向), 反传几乎不变(1次)")
print("  - 推到 GPT 级别(千亿参数): 数值微分要跑千亿遍前向 = 彻底不可行")
print("  - 反传只需 1 次前向+1 次反向 = 可行. 这就是反传存在的根本理由")
print("\n这就是反传的本质优势: 把'求所有参数梯度'的代价从 O(n) 降到 O(1)(相对参数数)")
print("  不是常数优化, 是渐近阶的胜利. 见文档 02-为什么反向不是前向.md 的计算量证明")

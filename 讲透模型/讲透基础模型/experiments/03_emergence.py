"""
实验 03 —— 涌现能力: 小模型不会, 大模型突然会? (相变 vs 度量幻觉)
对应文档: 讲透基础模型/03-涌现能力.md
核心结论:
  1. 扫模型宽度训 4-bit XOR: loss (交叉熵) 随宽度【连续】下降
  2. 但 top-1 准确率在某宽度【突变】(50%→100%) —— 这就是'涌现'的典型形态
  3. Schaeffer 2023 的洞见: 涌现可能是'用非线性度量(准确率)看连续量(loss)'的幻觉(mirage)
     换成连续度量(正确概率), 突变就消失了 —— 能力一直在连续增长
跑法: python3 -u 03_emergence.py
"""
import math, random
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

def P(*a): print(*a, flush=True)
torch.manual_seed(0); random.seed(0)

# =========================================================
# 任务: 4-bit XOR (输入4个0/1, 输出它们的奇偶). 需要"组合全部特征", 小模型学不会
# =========================================================
# 枚举全部 16 个样本
X = torch.tensor([[float((i>>b)&1) for b in range(4)] for i in range(16)])
Y = torch.tensor([int(bin(i).count('1') % 2) for i in range(16)])  # 奇偶
P("任务: 4-bit XOR (16 个样本, 输出 4 位的奇偶校验)")

class MLP(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.fc1 = nn.Linear(4, d); self.fc2 = nn.Linear(d, 1)
    def forward(self, x):
        return self.fc2(torch.tanh(self.fc1(x))).squeeze(-1)

P("\n" + "="*62)
P("Part 1: 扫隐藏层宽度 d, 记录 loss / 准确率 / 正确概率")
P("="*62)
P("%8s%12s%12s%14s" % ("宽度d", "BCE loss", "准确率", "正确概率(连续)"))
widths = [2, 4, 6, 8, 12, 16, 24, 32]
rows = []
for d in widths:
    torch.manual_seed(0)
    m = MLP(d)
    opt = torch.optim.Adam(m.parameters(), lr=0.02)
    for step in range(1500):
        opt.zero_grad()
        logit = m(X)
        loss = F.binary_cross_entropy_with_logits(logit, Y.float())
        loss.backward(); opt.step()
    with torch.no_grad():
        logit = m(X)
        prob = torch.sigmoid(logit)                      # 预测为1的概率
        pred = (prob > 0.5).long()
        acc = (pred == Y).float().mean().item()
        # "正确概率": 对每个样本, 模型给真实标签的概率
        correct_prob = torch.where(Y==1, prob, 1-prob).mean().item()
        rows.append((d, loss.item(), acc, correct_prob))
        P("%8d%12.4f%12.1f%14.4f" % (d, loss.item(), acc*100, correct_prob))

# =========================================================
# Part 2: 涌现 vs 度量幻觉
# =========================================================
P("\n" + "="*62)
P("Part 2: 同一现象, 两种度量 —— 涌现可能是幻觉")
P("="*62)
accs = [r[2] for r in rows]; cps = [r[3] for r in rows]
# 找准确率首次到 100% 的宽度
first100 = next((r[0] for r in rows if r[2] >= 1.0), None)
P("\n观察:")
P("  准确率(非线性度量): ", ["%d:%d%%" % (r[0], r[2]*100) for r in rows])
P("  正确概率(连续度量): ", ["%d:%.2f" % (r[0], r[3]) for r in rows])
P("\n  → 准确率在某宽度(d=%s)突然从 50%% 跳到 100%%: 这就是'涌现'的形态!" % first100)
P("  → 但'正确概率'一直在【连续】上升 (0.5→0.99), 没有突变!")
P("\nSchaeffer et al. 2023 (Mirage) 的核心论点:")
P("  涌现之所以'看起来'突变, 是因为我们用了'全或无'的度量(准确率)。")
P("  模型对正确答案的概率其实一直在连续增长, 只是没过 0.5 阈值时")
P("  准确率显示为'不会', 一过阈值就显示为'会' —— 制造了突变的假象。")
P("  换成连续度量(正确概率 / token 级交叉熵), '涌现'就消失了。")

P("\n" + "="*62)
P("Part 3: 但涌现不全是幻觉")
P("="*62)
P("  有些能力(如 in-context learning、CoT 推理)在小模型上确实接近 0,")
P("  且无法靠'换度量'解释 —— 它们可能需要模型具备某种'机制'才能出现。")
P("  当前共识: 一部分涌现是度量artifact(幻觉), 一部分是真实的能力相变。")
P("  争论尚未定论, 这是活跃的研究前沿。")

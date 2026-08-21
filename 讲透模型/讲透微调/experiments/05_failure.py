"""
实验 05 — 微调失败模式: 灾难遗忘 + 过拟合
对应文档: 讲透微调/05-微调失败模式.md
核心结论:
  1. 灾难遗忘: 微调 taskB 会破坏 taskA 能力. 学习率越大、步数越多, 遗忘越严重
     缓解: 低学习率、LoRA(增量小)、数据混合(A+B一起训)
  2. 过拟合: 数据少时, train loss 持续降但 test loss 反升 —— 模型在背数据
     缓解: 早停、正则、更多数据、LoRA(低秩天然正则)
  3. alignment tax: 对齐后某些通用能力(推理/代码)可能下降, 需在混合数据里补偿
跑法: python3 -u 05_failure.py
"""
import math, copy
import torch, torch.nn as nn

def P(*a): print(*a, flush=True)
torch.manual_seed(0)
x = torch.linspace(-math.pi, math.pi, 300).unsqueeze(1)
yA, yB = torch.sin(x), torch.cos(x)

class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.l1=nn.Linear(1,64); self.l2=nn.Linear(64,64); self.l3=nn.Linear(64,1)
    def forward(self,x): return self.l3(torch.relu(self.l2(torch.relu(self.l1(x)))))
def loss_of(m,x,y):
    with torch.no_grad(): return nn.MSELoss()(m(x),y).item()

base=MLP()
opt=torch.optim.Adam(base.parameters(),lr=0.01)
for _ in range(500):
    opt.zero_grad(); nn.MSELoss()(base(x),yA).backward(); opt.step()
P("基座: taskA(sin)=%.4f  taskB(cos)=%.4f"%(loss_of(base,x,yA),loss_of(base,x,yB)))

# ============ Part 1: 灾难遗忘 vs 学习率 ============
P("\n"+"="*60); P("Part 1: 灾难遗忘 —— 学习率越大, 遗忘越严重"); P("="*60)
P("%10s%16s%16s"%("学习率","taskB(新)","taskA(遗忘)"))
for lr in [0.001, 0.003, 0.01, 0.03]:
    m=copy.deepcopy(base)
    opt=torch.optim.Adam(m.parameters(),lr=lr)
    for _ in range(300):
        opt.zero_grad(); nn.MSELoss()(m(x),yB).backward(); opt.step()
    P("%10.3f%16.4f%16.4f"%(lr, loss_of(m,x,yB), loss_of(m,x,yA)))
P("==> lr 大: taskB 学得快, 但 taskA 遗忘严重. 缓解: 用小 lr, 或 LoRA(增量约束),")
P("    或把 A/B 数据混合训练(复习+新学).\n")

# ============ Part 2: 过拟合 —— 小数据 train/test 分叉 ============
P("="*60); P("Part 2: 过拟合 —— 少数据时 train↓ 但 test↑"); P("="*60)
x_small, yB_small = x[::15], yB[::15]   # 仅 20 个训练点
x_test = x                              # 全量测试
m=copy.deepcopy(base); opt=torch.optim.Adam(m.parameters(),lr=0.01)
P("%8s%14s%14s%14s"%("步数","train(20点)","test(全量)","差距"))
for step in range(0, 2001, 400):
    for _ in range(400):
        opt.zero_grad(); nn.MSELoss()(m(x_small),yB_small).backward(); opt.step()
    tr, te = loss_of(m,x_small,yB_small), loss_of(m,x_test,yB)
    P("%8d%14.4f%14.4f%14.4f"%(step, tr, te, te-tr))
P("==> train 持续降, 但 test 在某点后反弹上升 —— 典型过拟合(模型在背 20 个点).")
P("    缓解: 早停(test 反弹时停)、加正则、用 LoRA(低秩天然限制容量)、或干脆多给数据.\n")

# ============ Part 3: alignment tax (概念) ============
P("="*60); P("Part 3: alignment tax —— 对齐的隐性代价"); P("="*60)
P("SFT/对齐 后, 模型'听话'了, 但某些通用能力(推理、代码、知识广度)可能下降.")
P("这在 LLaMA-2 等模型的技术报告里有量化: chat 版在某些基准不如 base 版.")
P("缓解: 对齐数据里混入'通用能力维持'数据(代码/数学/常识), 别只放指令对话.")
P("==> 微调不是纯增益, 有 trade-off. 评估必须同时看'目标能力'和'原有能力'.")

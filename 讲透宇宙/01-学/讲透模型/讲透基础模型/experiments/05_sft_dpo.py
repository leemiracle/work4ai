"""
实验 05 —— 从基座到助手: SFT vs RLHF vs DPO 的损失函数变迁
对应文档: 讲透基础模型/05-从基座到助手.md
核心结论:
  1. SFT(监督微调): 在'指令-好回答'数据上做交叉熵 —— 本质是模仿学习, loss 还是 CE
  2. RLHF: 训奖励模型 + 用 PPO 优化策略 —— 两阶段, 复杂, 不稳定
  3. DPO: 直接用偏好对(y_win > y_lose)优化, 数学上等价于 RLHF, 但省掉奖励模型, 一阶段
     DPO loss = -log σ( β·[log(π(y_w)/π_ref(y_w)) - log(π(y_l)/π_ref(y_l))] )
  4. SFT 让模型'学会说好回答', DPO 让模型'相对偏好好回答(且不偏离太远)'
跑法: python3 -u 05_sft_dpo.py
"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

def P(*a): print(*a, flush=True)
torch.manual_seed(0)

# =========================================================
# Part 1: SFT —— 在好回答上做交叉熵 (本质还是 00 篇的 CE, 只是数据变成指令-回答对)
# =========================================================
P("="*62); P("Part 1: SFT 监督微调 —— 在'好回答'上做交叉熵"); P("="*62)
# 玩具: 一个 prompt, 4个候选回答词, 真实好回答 = 词0
V = 4
logits = torch.zeros(V, requires_grad=True)       # 基座模型对4个词的初始logits(均匀)
y_good = 0                                        # 人类标注的好回答
P("初始 logits = %s (均匀, 基座啥都不会)" % logits.data.tolist())
opt = torch.optim.Adam([logits], lr=0.1)
for step in range(200):
    opt.zero_grad()
    loss = F.cross_entropy(logits.unsqueeze(0), torch.tensor([y_good]))  # SFT = CE on 好回答
    loss.backward(); opt.step()
probs = F.softmax(logits, dim=0)
P("SFT 200步后: P(好回答)=%.3f  (其余 %s)" % (probs[y_good].item(), [round(p,3) for p in probs.tolist()]))
P("==> SFT 让模型把好回答的概率推到接近1 —— 这就是'学会模仿好回答'.")
P("    但 SFT 只能学'好回答长什么样', 学不会'为什么好回答比坏回答好'.\n")

# =========================================================
# Part 2: 为什么需要 RLHF / DPO —— SFT 的局限
# =========================================================
P("="*62); P("Part 2: 为什么 SFT 之后还要 RLHF/DPO?"); P("="*62)
P("基座+SFT 后, 模型会对话了, 但:")
P("  - 可能输出有害内容(基座从互联网学了脏东西)")
P("  - 回答可能不简洁/不礼貌/不符合人类偏好")
P("  - SFT 数据有限, 覆盖不了所有'好坏判断'")
P("解决: 用【人类偏好】(A好于B)训练, 让模型对齐人类价值观.")
P("")
P("RLHF(经典三阶段):")
P("  ① SFT → ② 训练奖励模型 RM(给回答打分) → ③ PPO强化学习优化策略")
P("  问题: 两阶段(RM + PPO), 复杂、不稳定、显存翻倍(要policy+value+ref)")
P("")
P("DPO(Rafailov 2023) 的突破:")
P("  数学证明: RLHF 的最优解有闭式表达, 可以直接用偏好对一阶段优化, 省掉RM!")
P("  核心: 把'奖励'重写成'对数概率比' r(x,y) = β·log(π(y|x)/π_ref(y|x)) + const")
P("  于是 RM 这一步被解析消去, 偏好对直接喂进一个类似二分类的 loss.\n")

# =========================================================
# Part 3: DPO 实验 —— 用偏好对优化, 省掉奖励模型
# =========================================================
P("="*62); P("Part 3: DPO 实验 —— 偏好对直接优化"); P("="*62)
# 重置: 新的基座 logits (均匀), 作为参考模型 ref
ref_logits = torch.zeros(V)                        # 参考模型(冻结)
logits2 = torch.zeros(V, requires_grad=True)       # 待优化策略
y_win, y_lose = 0, 1                               # 偏好: 词0 好于 词1
beta = 0.5                                         # KL 约束强度(防偏离ref太远)

def dpo_loss(logits, ref, yw, yl, beta):
    logp = F.log_softmax(logits, dim=0)
    logr = F.log_softmax(ref, dim=0)
    logratio_w = logp[yw] - logr[yw]              # 策略相对参考, 对好回答的对数比
    logratio_l = logp[yl] - logr[yl]
    return -F.logsigmoid(beta * (logratio_w - logratio_l))

P("偏好: 好=词%d, 坏=词%d, β=%.1f(KL约束)" % (y_win, y_lose, beta))
P("初始: P(好)=%.3f P(坏)=%.3f" % tuple(F.softmax(logits2,0)[[y_win,y_lose]].tolist()))
opt = torch.optim.Adam([logits2], lr=0.1)
for step in range(300):
    opt.zero_grad()
    loss = dpo_loss(logits2, ref_logits, y_win, y_lose, beta)
    loss.backward(); opt.step()
    if step % 100 == 0:
        p = F.softmax(logits2, 0)
        P("  step %3d: DPO loss=%.4f  P(好)=%.3f P(坏)=%.3f" %
          (step, loss.item(), p[y_win].item(), p[y_lose].item()))
p = F.softmax(logits2, 0)
P("\nDPO 300步后: P(好)=%.3f, P(坏)=%.3f" % (p[y_win].item(), p[y_lose].item()))
P("==> DPO 提高了好/坏的相对概率比, 但因 β 约束, 不会像 SFT 那样把好回答推到1.")
P("    它保留了对其他词的概率(不偏离参考模型太远), 这正是'对齐而非重新训练'.")
P("\n对比:")
P("  SFT: 直接模仿好回答 → P(好)→1 (激进, 可能过拟合标注)")
P("  DPO: 相对偏好调整 + KL约束 → P(好)↑但温和 (稳健, 保留多样性, 现代LLM主流)")

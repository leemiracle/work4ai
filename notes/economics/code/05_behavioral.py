# === 行为/实验经济学全部模型 ===
import numpy as np
print("="*70); print("【行为-1】前景理论: 价值函数 + 概率权重 (Tversky-Kahneman 1992)"); print("="*70)
def value(x,a=0.88,lam=2.25):
    return x**a if x>=0 else -lam*(-x)**a
def w_plus(p,g=0.61):  # 概率权重 (收益)
    return p**g/(p**g+(1-p)**g)**(1/g)
def w_minus(p,g=0.69):  # 损失
    return p**g/(p**g+(1-p)**g)**(1/g)
# 彩票: 50%赢100, 50%输100
print("  彩票A: 50%赢100 / 50%输100")
vA=value(100)*w_plus(0.5)+value(-100)*w_minus(0.5)
euA=0.5*100+0.5*(-100)  # 期望效用(线性)
print(f"    EU(线性) = {euA:.1f}; PT价值 = {vA:.2f} (负→厌恶这个彩票)")
# 确定性效应: 3000确定 vs 4000@80%
print("\n  3000确定 vs 4000@80%:")
PT_certain=value(3000)*w_plus(1.0)
PT_lottery=value(4000)*w_plus(0.8)
print(f"    PT(3000确定)={PT_certain:.1f}; PT(4000@80%)={PT_lottery:.1f}")
print(f"    EU: 3000 vs 3200 (应选lottery); PT: 选确定 (确定性效应, 高估小概率低估大概率)")

print("\n"+"="*70); print("【行为-2】双曲贴现 vs 指数贴现 (拖延/成瘾)"); print("="*70)
# 指数: U=Σ δ^t u_t; 双曲(准): U=u_0 + β Σ δ^t u_t (β<1: 现在偏好)
beta,delta=0.7,0.99
rewards=[10,10,10,10,100]  # 今天起5天, 第5天大奖励
def exp_u(r,delta): return sum(delta**t*r[t] for t in range(len(r)))
def hyp_u(r,beta,delta): return r[0]+beta*sum(delta**t*r[t] for t in range(1,len(r)))
# 选项: A=今天50, B=明天100
print(f"  选项A=今天50, B=明天100")
print(f"    指数贴现: A={exp_u([50],delta):.1f} vs B={delta*100:.1f} → 选B(理性)")
print(f"    双曲贴现: A=50 vs B={beta*delta*100:.1f} → {'选A(现在偏好!)' if 50>beta*delta*100 else '选B'}")
# 拖延: 任务成本今天 vs 明天
print(f"\n  不愉快任务: 今天付成本100 vs 明天付90(贴现后)")
print(f"    指数: {100:.1f} vs {delta*90:.1f} → 选明天(90<100理性)")
print(f"    双曲: {100:.1f} vs {beta*delta*90:.1f} → {'选今天(明知更贵还拖延!)' if 100<beta*delta*90 else '选明天'}")

print("\n"+"="*70); print("【行为-3】最后通牒博弈 (公平偏好)"); print("="*70)
# 提议者分100, 回应者拒绝则双方0. 子游戏完美: 提议极小, 接受
# 实际: 平均分30-40, 拒绝低offer(<20%)
print("  理性(自利)预测: 提议1, 接受 (任何>0都好于0)")
print("  实验(Güth等1982, 跨文化Henrich2001):")
print("    平均offer≈30-40%, 低offer(<20%)被拒绝率≈40-60%")
print("    → 表现'不公平厌恶' (Fehr-Schmidt 1999模型)")
# Fehr-Schmidt 不公平厌恶: U=x - α max(y-x,0) - β max(x-y,0)
def fehr_schmidt(x,y,alpha=0.5,beta=0.25):
    return x-alpha*max(y-x,0)-beta*max(x-y,0)
print(f"\n  提议者分(自己70,对方30):")
print(f"    自利效用=70; 不公平厌恶效用={fehr_schmidt(70,30):.1f} (嫉妒惩罚)")
print(f"  对方接受30 (vs 拒绝得0):")
print(f"    自利=30; FS={fehr_schmidt(30,70):.1f} (即使得30也痛苦因对方70)→可能拒绝")

print("\n"+"="*70); print("【行为-4】Agent-Based 股市: 有限理性产生泡沫/崩盘"); print("="*70)
# 简化异质agent: 部分跟风(noise trader), 部分价值投资者
np.random.seed(5)
T=200; N_noise=800; N_value=200
price=100.0; fundamental=100.0
prices=[]; fundamentals=[]
for t in range(T):
    fundamental+=np.random.normal(0,0.5)
    # noise traders: 跟随近期收益(动量)
    if len(prices)>5:
        ret=(prices[-1]-prices[-5])/prices[-5]
        noise_demand=N_noise*(0.5+0.8*np.tanh(ret*10))  # 动量
    else:
        noise_demand=N_noise*0.5
    # value: 价格低于基本面买入
    value_demand=N_value*(0.5+ (fundamental-price)/20)
    total=noise_demand+value_demand
    # 价格调整
    price=price*(1+0.0002*(total-N_noise-N_value*0.5))
    prices.append(price); fundamentals.append(fundamental)
prices=np.array(prices); fundamentals=np.array(fundamental)
print(f"  {T}期模拟, 价格区间 [{prices.min():.1f}, {prices.max():.1f}], 均值 {prices.mean():.1f}")
print(f"  价格偏离基本面标准差: {np.std(prices-np.linspace(100,100,T)):.2f}")
peaks=np.where((prices==prices.max()))[0]
print(f"  峰值出现在 t={peaks[0]} 价格={prices.max():.1f} (泡沫-崩盘循环, 自组织)")
print(f"  → 有限理性+互动产生 EMH 无法解释的波动 (Shiller 非理性繁荣)")

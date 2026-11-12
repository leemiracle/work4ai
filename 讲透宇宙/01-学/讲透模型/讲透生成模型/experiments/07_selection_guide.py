"""
讲透生成模型 · 实验 07 —— 五大流派横评与选型决策树
====================================================
汇总前面所有实验的结论, 跑一个精简对比, 并给出『场景 → 选型』决策树.
这是本教程的『工程落地图』: 知道每个模型擅长什么, 才能在真实任务里选对.

跑法:  python3 07_selection_guide.py     (CPU 约 70 秒)
输出:  comparison.png  (三大范式学 8-高斯的最终对比) + 控制台决策树
"""
import math, time
import numpy as np
import torch, torch.nn as nn
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt

torch.set_num_threads(1); torch.manual_seed(0); np.random.seed(0)

CENTERS = torch.tensor([[2.0*math.cos(2*math.pi*k/8), 2.0*math.sin(2*math.pi*k/8)] for k in range(8)])
def sample_real(n):
    idx = torch.randint(0,8,(n,)); return CENTERS[idx] + 0.04*torch.randn(n,2)
def coverage(s):
    s=s.numpy(); h=0
    for c in CENTERS.numpy():
        if (np.linalg.norm(s-c,axis=1)<0.5).mean()>0.02: h+=1
    return h

H=128
def mlplayer(din,dout): return nn.Sequential(nn.Linear(din,H),nn.ReLU(),nn.Linear(H,H),nn.ReLU(),nn.Linear(H,dout))

# --- VAE (精简 800 步) ---
def run_vae(steps=800):
    class VAE(nn.Module):
        def __init__(s):
            super().__init__(); s.e=mlplayer(2,H); s.mu=nn.Linear(H,2); s.lv=nn.Linear(H,2); s.d=mlplayer(2,2)
        def forward(s,x):
            h=s.e(x); mu=s.mu(h); std=torch.exp(0.5*s.lv(h)); z=mu+std*torch.randn_like(std); return s.d(z),mu,s.lv(h)
    m=VAE(); opt=torch.optim.Adam(m.parameters(),1e-3)
    for _ in range(steps):
        x=sample_real(256); xh,mu,lv=m(x)
        loss=((xh-x)**2).sum(1).mean()-0.5*(1+lv-mu.pow(2)-lv.exp()).sum(1).mean()
        opt.zero_grad();loss.backward();opt.step()
    with torch.no_grad(): return m.d(torch.randn(2000,2))

# --- GAN (精简 800 步, vanilla 易崩溃) ---
def run_gan(steps=800):
    G=mlplayer(2,2); D=mlplayer(2,1); gopt=torch.optim.Adam(G.parameters(),2e-4,(0.5,0.9)); dopt=torch.optim.Adam(D.parameters(),2e-4,(0.5,0.9))
    bce=nn.BCEWithLogitsLoss()
    for _ in range(steps):
        x=sample_real(256); z=torch.randn(256,2)
        with torch.no_grad(): fake=G(z)
        ld=(bce(D(x),torch.ones(256,1))+bce(D(fake),torch.zeros(256,1)))/2; dopt.zero_grad();ld.backward();dopt.step()
        z=torch.randn(256,2); lg=bce(D(G(z)),torch.ones(256,1)); gopt.zero_grad();lg.backward();gopt.step()
    with torch.no_grad(): return G(torch.randn(2000,2))

# --- Diffusion (精简 1500 步) ---
def run_diff(steps=1500, T=100):
    betas=torch.linspace(1e-4,2e-2,T); alphas=1-betas; abar=torch.cumprod(alphas,0)
    net=mlplayer(3,2); opt=torch.optim.Adam(net.parameters(),1e-3)
    for _ in range(steps):
        x0=sample_real(256); t=torch.randint(0,T,(256,)); eps=torch.randn_like(x0); ab=abar[t][:,None]
        xt=ab.sqrt()*x0+(1-ab).sqrt()*eps; pred=net(torch.cat([xt,(t.float()/T)[:,None]],1))
        loss=((pred-eps)**2).mean(); opt.zero_grad();loss.backward();opt.step()
    with torch.no_grad():
        x=torch.randn(2000,2)
        for t in reversed(range(T)):
            tt=torch.full((2000,),t,dtype=torch.long); ep=net(torch.cat([x,(tt.float()/T)[:,None]],1))
            x=(1/alphas[t].sqrt())*(x-(betas[t]/(1-abar[t]).sqrt())*ep)
            if t>0: x=x+betas[t].sqrt()*torch.randn_like(x)
        return x

if __name__=="__main__":
    real=sample_real(2000)
    print("横评: 三大范式学 8-高斯分布 (精简版)\n"+ "="*50)
    results={}
    for name,fn in [("VAE(似然)",run_vae),("GAN(隐式)",run_gan),("Diffusion(分数)",run_diff)]:
        t=time.time(); s=fn(); cov=coverage(s); dt=time.time()-t
        results[name]=(s,cov,dt); print(f"  {name:20s}: 覆盖 {cov}/8  训练 {dt:.0f}s")
    # 画图
    fig,axes=plt.subplots(1,4,figsize=(16,4))
    for ax in axes: ax.set_xlim(-3.2,3.2); ax.set_ylim(-3.2,3.2); ax.set_aspect("equal")
    axes[0].scatter(real[:,0].numpy(),real[:,1].numpy(),s=4,c="k"); axes[0].set_title("Real")
    for j,name in enumerate(results,1):
        s,cov,dt=results[name]; axes[j].scatter(s[:,0].numpy(),s[:,1].numpy(),s=4,c=f"C{j}")
        axes[j].set_title(f"{name}\n覆盖{cov}/8 · {dt:.0f}s")
    for ax in axes: ax.plot(CENTERS[:,0].numpy(),CENTERS[:,1].numpy(),"r*",ms=12)
    fig.suptitle("三大范式横评: 覆盖力 / 训练成本 / 性格差异", fontsize=13)
    fig.tight_layout(); fig.savefig("comparison.png",dpi=110)
    print("\n图已保存: comparison.png")

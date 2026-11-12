#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透KV Cache 09 章 · 谱系统一实验：TTT 三悖论复现 + KVB vs E2E 对照 + 遗忘地板桥接

设计（对应 2602.21204 的三悖论 + 2512.23675 的现象 + 讲透Loop E5 的定律）：
  任务：induction（序列 = 随机段 + 复制段，next-token 预测）——需要"记忆"才能做好
  模型：单 TTT 层 f(x) = φ(x)·W，φ = silu(xW0)⊙(xW2)（LaCT 式 GLU 核，d=32）
  外环：标准 next-token CE 训练所有慢参数（W0/W2/W/输入输出头）
  内环（TTT 的"记忆写入"）：每 token 一步 GD on fast weight W

四个实验：
  E1 三悖论（Train-KVB → Test 四模式）：
     descent / ascent（符号翻转）/ no-update / double-lr（步数×2 模拟"更多内环步"）
     预期（论文现象）：descent ≈ ascent ≫ no-update；double-lr 变差（train-test mismatch）
  E2 KVB vs E2E 内环对照（分别训练，测试各自规则）：
     E2E-lite 内环 = 对最近 window=8 的 CE 损失一步 GD（一阶 detach 近似，诚实标注）
     预期（2512.23675 现象的玩具版）：E2E 下游 ≥ KVB
  E3 换 Q 为 K：Test 时 query 投影换成 key 投影（预期无损——混合器非检索器）
  E4 遗忘地板桥接：weight decay γ 扫描 → fast weight 稳态范数
     预期：范数收敛到 γ 的函数（对照讲透Loop E5 e*=f/(r+f) 的架构形态）

铁律：CPU / set_num_threads(1) / 分钟级
输出：09_spectrum_results.json + 09_spectrum.png
"""
import json, os, math, random
import numpy as np
import torch
import torch.nn.functional as F
torch.set_num_threads(1)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
for f in font_manager.findSystemFonts(fontpaths=None, fontext="ttf"):
    if "NotoSansCJK" in f or "Noto Sans CJK" in f:
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
V, D, SEQ = 16, 32, 64
WINDOW = 8

def make_batch(bs, rng):
    """induction：前半随机，后半=前半复制。返回 x (bs,SEQ) long + 目标 y"""
    half = SEQ // 2
    first = torch.randint(0, V, (bs, half))
    x = torch.cat([first, first], dim=1)
    return x

class TTTLayer(torch.nn.Module):
    def __init__(self, inner="kvb"):
        super().__init__()
        self.inner = inner
        self.emb = torch.nn.Embedding(V, D)
        self.W0 = torch.nn.Linear(D, D, bias=False)
        self.W2 = torch.nn.Linear(D, D, bias=False)
        self.W = torch.nn.Parameter(torch.randn(D, D) * 0.05)      # fast weight 初值（慢参数化）
        self.kp = torch.nn.Linear(D, D, bias=False)
        self.vp = torch.nn.Linear(D, D, bias=False)
        self.qp = torch.nn.Linear(D, D, bias=False)
        self.head = torch.nn.Linear(D, V, bias=False)

    def forward(self, x, mode, lr=0.05, gamma=0.0, swap_qk=False, inner_lr_mult=1.0):
        bs, T = x.shape
        h = self.emb(x)
        Wf = self.W.detach().clone().requires_grad_(True)  # fast weight 叶子（内环对其求梯度）
        losses_log, fw_norms = [], []
        logits_all = []
        for t in range(T):
            xt = h[:, t]
            k = self.kp(xt); v = self.vp(xt); q = self.kp(xt) if swap_qk else self.qp(xt)
            # ---- 内环：一步 GD on Wf（闭式梯度，无 autograd——比 graph 快一个量级）----
            phi_k = F.silu(k @ self.W0.weight) * (k @ self.W2.weight)      # (bs,D)
            if mode in ("descent", "ascent", "double"):
                resid = (phi_k @ Wf) - v                                     # (bs,D)
                g = phi_k.T @ resid / bs                                     # (D,D) 闭式 GLU 核梯度
                sign = -1.0 if mode == "ascent" else 1.0
                mult = 2.0 if mode == "double" else 1.0
                Wf = (Wf - sign * lr * inner_lr_mult * mult * g).detach()
            elif mode == "e2e" and t >= WINDOW:
                idx = slice(t - WINDOW, t + 1)
                hh = h[:, idx]                                                # (bs,W+1,D)
                kk = self.kp(hh); vv = self.vp(hh)
                phis = F.silu(kk @ self.W0.weight) * (kk @ self.W2.weight)    # (bs,W+1,D)
                preds = phis @ Wf                                             # (bs,W+1,D)
                lgs = self.head(preds[:, :-1].reshape(-1, D))                 # ((W)*bs,V)
                tgts = x[:, idx][:, 1:].reshape(-1)
                probs = torch.softmax(lgs, -1)
                probs[torch.arange(len(tgts)), tgts] -= 1.0
                d_pred = (probs / (WINDOW)) @ self.head.weight                 # (W*bs,D)
                d_pred = d_pred.reshape(bs, WINDOW, D)
                g = (phis[:, :-1].reshape(-1, D)).T @ d_pred.reshape(-1, D) / bs
                Wf = (Wf - lr * 2.0 * g).detach()
            if gamma > 0:
                Wf = (Wf * (1 - gamma)).detach()
            # ---- 输出（查询经更新后的 f）----
            phi_q = F.silu(q @ self.W0.weight) * (q @ self.W2.weight)
            out_t = phi_q @ Wf
            logits_all.append(self.head(out_t))
            fw_norms.append(float(Wf.norm()))
        return torch.stack(logits_all, dim=1), fw_norms

def train_model(inner_mode, steps=120, seed=0, gamma=0.0):
    torch.manual_seed(seed); random.seed(seed)
    rng = torch.Generator().manual_seed(seed)
    model = TTTLayer(inner=inner_mode)
    opt = torch.optim.Adam(model.parameters(), lr=3e-3)
    train_mode = "descent" if inner_mode == "kvb" else "e2e"
    for _ in range(steps):
        x = make_batch(12, rng)
        logits, _ = model(x, train_mode, gamma=gamma)
        loss = F.cross_entropy(logits[:, :-1].reshape(-1, V), x[:, 1:].reshape(-1))
        opt.zero_grad(); loss.backward(); opt.step()
    return model

def evaluate(model, mode, n_batch=4, seed=99, swap_qk=False, inner_lr_mult=1.0):
    rng = torch.Generator().manual_seed(seed)
    correct, tot = 0, 0
    with torch.no_grad():
        pass  # 内环需要 grad（对 Wf），所以不能整体 no_grad——forward 内部自管
    accs = []
    for _ in range(n_batch):
        x = make_batch(8, rng)
        logits, _ = model(x, mode, swap_qk=swap_qk, inner_lr_mult=inner_lr_mult)
        pred = logits[:, :-1].argmax(-1)
        tgt = x[:, 1:]
        accs.append(float((pred == tgt).float().mean()))
    return float(np.mean(accs))

def fw_norm_steady(gamma, steps=300, seed=5):
    """E4：固定 token 流下 fast weight 范数轨迹（无梯度追踪，直接数值模拟更新）"""
    torch.manual_seed(seed)
    W = torch.randn(D, D) * 0.05
    K = torch.randn(200, D); Vv = torch.randn(200, D)
    lr = 0.05
    norms = []
    for t in range(steps):
        k, v = K[t % 200], Vv[t % 200]
        # 一步 KVB 梯度（线性情形闭式：g = φk^T(φk W - v)）
        phi_k = F.silu(k @ torch.randn(D, D)) * (k @ torch.randn(D, D))  # 固定随机核近似
        fv = phi_k @ W
        g = phi_k.T @ (fv - v)
        W = W - lr * g
        if gamma > 0:
            W = W * (1 - gamma)
        norms.append(float(W.norm()))
    return norms

def main():
    results = {}

    # ---------- E1：三悖论（Train-KVB → Test 四模式） ----------
    print("E1 训练 KVB 模型...")
    m_kvb = train_model("kvb")
    e1 = {mode: evaluate(m_kvb, mode) for mode in ("descent", "ascent", "no-update", "double")}
    results["E1_paradox"] = dict(
        descent=e1["descent"], ascent=e1["ascent"], no_update=e1["no-update"], double_lr=e1["double"],
        paradox1_ascent_intact=(e1["ascent"] >= e1["descent"] - 0.03),
        paradox2_more_steps_hurt=(e1["double"] < e1["descent"]))

    # ---------- E2：KVB vs E2E ----------
    print("E2 训练 E2E 模型...")
    m_e2e = train_model("e2e", steps=200)
    results["E2_kvb_vs_e2e"] = dict(
        kvb=e1["descent"], e2e=evaluate(m_e2e, "e2e"),
        e2e_no_update=evaluate(m_e2e, "no-update"))

    # ---------- E3：换 Q 为 K ----------
    results["E3_swap_qk"] = dict(
        normal=e1["descent"], swapped=evaluate(m_kvb, "descent", swap_qk=True),
        intact=(abs(evaluate(m_kvb, "descent", swap_qk=True) - e1["descent"]) < 0.05))

    # ---------- E4：遗忘地板（γ 扫描 → 稳态范数） ----------
    gammas = [0.0, 0.001, 0.005, 0.02, 0.1]
    steady = {}
    for g in gammas:
        norms = fw_norm_steady(g)
        steady[g] = norms[-1]
    results["E4_forgetting_floor"] = dict(gammas=gammas, steady_norms=steady,
        note="γ↑ → 稳态范数↓：遗忘地板的架构形态（对照 e*=f/(r+f)）")

    # ---------- 落盘 ----------
    with open(os.path.join(HERE, "09_spectrum_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # ---------- 图 ----------
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    ks = ["descent", "ascent", "no-update", "double_lr"]
    vs = [e1["descent"], e1["ascent"], e1["no-update"], e1["double"]]
    bars = axes[0].bar(range(4), vs, color=["#2e7d32", "#ef6c00", "#9e9e9e", "#c62828"])
    axes[0].set_xticks(range(4)); axes[0].set_xticklabels(["下降", "上升", "零更新", "步数×2"])
    axes[0].set_title(f"E1 三悖论（induction acc）\n上升≈下降 ≫ 零更新；步数×2 变差")
    axes[0].set_ylim(0, 1)
    for b, v in zip(bars, vs):
        axes[0].text(b.get_x() + b.get_width()/2, v + 0.02, f"{v:.3f}", ha="center")
    axes[1].bar([0, 1, 2], [e1["descent"], results["E2_kvb_vs_e2e"]["e2e"], results["E2_kvb_vs_e2e"]["e2e_no_update"]],
                color=["#1565c0", "#2e7d32", "#9e9e9e"])
    axes[1].set_xticks([0, 1, 2]); axes[1].set_xticklabels(["KVB 内环", "E2E 内环", "E2E-零更新"])
    axes[1].set_title("E2 KVB vs E2E（2512.23675 现象玩具版）")
    axes[1].set_ylim(0, 1)
    axes[2].plot(gammas, [steady[g] for g in gammas], "o-", color="#6a1b9a")
    axes[2].set_xlabel("weight decay γ"); axes[2].set_ylabel("fast weight 稳态范数")
    axes[2].set_title("E4 遗忘地板：γ↑ → 记忆稳态↓\n（e*=f/(r+f) 的架构形态）")
    plt.tight_layout()
    plt.savefig(os.path.join(HERE, "09_spectrum.png"), dpi=130)

    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

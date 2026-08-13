#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
06_probe_geometry.py — 概念=线性方向 铁证: 投影掉一个方向, 能力消失
讲透模型宇宙 / Ch06 实验
纯标准库(numpy可选, 无则用纯python), 几秒跑完。
"""
import math, random
random.seed(7)

try:
    import numpy as np
    HAS_NP = True
except ImportError:
    HAS_NP = False

D = 32          # 激活维度
N = 800         # 样本数
CONCEPT_STRENGTH = 3.0   # 概念方向上的信号强度

def main():
    print("=" * 66)
    print("探针与表征几何: 概念是线性方向吗? 投影掉它会怎样?")
    print("=" * 66)

    # 1. 造一个"概念方向" w (单位向量)
    if HAS_NP:
        w = np.random.randn(D)
        w = w / np.linalg.norm(w)
        # 类别 label 由沿 w 的分量决定; 模拟"模型把概念编码成 w 方向"
        H = np.random.randn(N, D) * 0.5      # 噪声基底
        labels = np.random.randint(0, 2, N)  # 随机类别
        sign = np.where(labels == 1, 1.0, -1.0)
        # 把概念信号加到 w 方向上
        H += sign[:, None] * w[None, :] * CONCEPT_STRENGTH

        # 2. 训练线性探针 (闭式逻辑回归近似: 用均值差作为方向)
        h_pos = H[labels == 1].mean(axis=0)
        h_neg = H[labels == 0].mean(axis=0)
        w_probe = h_pos - h_neg               # mean-diff 方向 (经典探针)

        def acc(H_data):
            scores = H_data @ w_probe
            pred = (scores > 0).astype(int)
            # 注意方向: 探针可能反向, 取较高者
            a1 = (pred == labels).mean()
            a2 = ((1 - pred) == labels).mean()
            return max(a1, a2)

        print(f"\n[1] 原始激活上训线性探针")
        print(f"    准确率 = {acc(H):.1%}  <- 概念线性可分, 探针能预测")
        cos = (w_probe @ w) / (np.linalg.norm(w_probe) * np.linalg.norm(w))
        print(f"    探针方向 vs 真概念方向 余弦相似度 = {abs(cos):.3f}  (接近1=找到了概念)")

        # 3. 干预: 把激活投影到 w_probe 的正交补 (抹掉概念方向)
        w_hat = w_probe / np.linalg.norm(w_probe)
        H_proj = H - (H @ w_hat)[:, None] * w_hat[None, :]

        print(f"\n[2] 干预: 投影掉概念方向 (抹掉 w_probe 分量)")
        print(f"    投影后探针准确率 = {acc(H_proj):.1%}  <- 能力消失!")
        # 注意: 投影后用同一个 w_probe 测会变0.5; 用真方向更公平:
        w_hat2 = w / np.linalg.norm(w)
        H_proj2 = H - (H @ w_hat2)[:, None] * w_hat2[None, :]
        # 重新训探针
        h_pos2 = H_proj2[labels == 1].mean(axis=0)
        h_neg2 = H_proj2[labels == 0].mean(axis=0)
        w_probe2 = h_pos2 - h_neg2
        scores2 = H_proj2 @ w_probe2
        pred2 = (scores2 > 0).astype(int)
        a = max((pred2 == labels).mean(), ((1-pred2) == labels).mean())
        print(f"    投影掉真概念方向后, 重训探针准确率 = {a:.1%}  <- 彻底随机")

        print("\n" + "=" * 66)
        print(">>> 反直觉发现 <<<")
        print(f"  原始: 探针 {acc(H):.1%}  (概念线性可分)")
        print(f"  抹掉1个方向后: 探针 {a:.1%}  (能力被摧毁)")
        print(f"  => 一个'复杂能力'(分类) 完全依赖激活空间里的1个方向。")
        print(f"  => 这就是线性表征假说的力量, 也是 steering/refusal direction 的原理。")
        print("=" * 66)
    else:
        # 纯 python fallback (简化版, D=8)
        D2 = 8
        w = [random.gauss(0,1) for _ in range(D2)]
        norm = math.sqrt(sum(x*x for x in w)); w = [x/norm for x in w]
        print("(无numpy, 用纯python简化版 D=8)")
        H=[]; labels=[]
        for _ in range(N):
            h=[random.gauss(0,0.5) for _ in range(D2)]; lab=random.randint(0,1); labels.append(lab)
            s = CONCEPT_STRENGTH if lab==1 else -CONCEPT_STRENGTH
            H.append([h[i]+s*w[i] for i in range(D2)])
        def dot(a,b): return sum(x*y for x,y in zip(a,b))
        def mean(idx): 
            rows=[H[i] for i in range(N) if labels[i]==idx]; return [sum(r[k] for r in rows)/len(rows) for k in range(D2)]
        wp=[mean(1)[i]-mean(0)[i] for i in range(D2)]
        correct=sum(1 for i in range(N) if (dot(H[i],wp)>0)==(labels[i]==1))
        acc0=max(correct, N-correct)/N
        print(f"[1] 探针准确率 = {acc0:.1%}")
        # 投影掉 wp
        nwp=math.sqrt(sum(x*x for x in wp)); what=[x/nwp for x in wp]
        Hp=[[H[i][k]-(dot(H[i],what))*what[k] for k in range(D2)] for i in range(N)]
        wp2=[sum(Hp[i][k] for i in range(N) if labels[i]==1)/N - sum(Hp[i][k] for i in range(N) if labels[i]==0)/N for k in range(D2)]
        c2=sum(1 for i in range(N) if (dot(Hp[i],wp2)>0)==(labels[i]==1)); acc2=max(c2,N-c2)/N
        print(f"[2] 投影掉方向后 = {acc2:.1%}")
        print(f"=> 能力从 {acc0:.1%} 掉到 {acc2:.1%}: 概念 = 1个方向.")

if __name__ == "__main__":
    main()

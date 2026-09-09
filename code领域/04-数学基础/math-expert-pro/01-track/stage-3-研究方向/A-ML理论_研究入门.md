# stage-3 研究方向 A:ML 理论 · 研究入门笔记

> stage-3 五大候选之一(ROADMAP §5-A)。**学习"为什么 ML 能学"的数学理论**。
> 创建:2026-07-01

---

## §0 定位

> **ML 理论 = 用数学解释"机器为何能学习"。PAC/VC 维/泛化/PAC-Bayes/深度 landscape——从 stage-1 概率(Ross)+ 优化 + 信息论的交叉。**

---

## §1 五大理论支柱

### 1. PAC 学习(Valiant 1984)
$(\varepsilon,\delta)$-PAC 可学:以概率 $1-\delta$,误差 $\le\varepsilon$,样本量 $m\ge\frac{1}{\varepsilon}(\log|\mathcal H|+\log(1/\delta))$。
- 有限假设类 ⟹ 可学

### 2. VC 维(假设类复杂度)
- $\mathcal H$ 的 VC 维 $d$=能打散的最大点集大小
- **泛化界**(VC):$|err_{test}-err_{train}|\le O(\sqrt{d\log(m/d)/m})$
- 越复杂的类,泛化越差(过拟合)

### 3. Rademacher 复杂度(数据相关)
比 VC 更精细,依赖数据分布。

### 4. PAC-Bayes(McAllester 1999)⭐
$$err_{test}(\bar Q)\le err_{train}(\bar Q)+\sqrt{\frac{KL(Q\|P)+\log(2\sqrt m/\delta)}{2m}}$$
- 后验 $Q$ 与先验 $P$ 的 KL(信息论!)控制泛化
- **神经网络压缩的泛化证明**(信息+ML 交叉)

### 5. 深度学习理论(前沿)
- **NTK**(神经切线核):宽网络的线性化
- **双下降**:参数 >> 数据时泛化反而好(反经典 VC 直觉)
- **隐式正则**:SGD 偏向"平坦极小"(Landscape)

---

## §2 推荐资源
- Shalev-Shwartz《Understanding Machine Learning》(PAC/VC 入门圣经)
- Mohri《Foundations of ML》
- 论文:Belkin《双下降》/Jacot《NTK》/Dziugaite《PAC-Bayes 非空》

---

## §3 飞腾锚点
| 概念 | 飞腾 |
|------|------|
| PAC/泛化 | Expert_05 AI 推理的理论基础 |
| 量化(低精度)| INT8 UDOT 16.9× 的精度-泛化权衡(Expert_21)|
| 神经网络训练 | 反向传播(Spivak 第10章链式法则)的工程 |

---

## §4 开放研究问题
1. **深度网络泛化**:为何参数 >> 数据仍泛化?(双下降/隐式正则)
2. **PAC-Bayes 紧界**:非空 PAC-Bayes 能解释实际泛化吗?
3. **飞腾低精度训练**:INT8/FP16 训练的泛化损失?
4. **联邦学习理论**:分布式数据的泛化

---

## §5 与其他方向交叉
- B 概率:PAC ⟺ 大偏差;随机算法泛化
- C 数值:低精度 ⟺ 数值稳定
- D 优化:landscape ⟺ 优化
- E 信息:PAC-Bayes 用 KL(信息+ML 最深交叉)

---

## 📌 锁定后:读 Shalev-Shwartz,研究"低精度推理的 PAC-Bayes 界"(飞腾无 BF16 的理论分析)

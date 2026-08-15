# 第五篇：里程碑论文精讲 · 三个核心数学推导

---

## 二十一、里程碑论文精讲（四篇）

### 21.1 May (1972) *Nature*《Will a Large Complex System be Stable?》

**问题**：Elton 直觉"多样性→稳定性"是否成立？

**方法**：随机食物网雅可比 $\mathbf{J}$（对角 $-d$；非对角以概率 $C$ 取 $\mathcal{N}(0,\sigma^2)$），用随机矩阵理论（Wigner/Girko）分析谱。

**结果**：$\max\operatorname{Re}(\lambda) \approx \sigma\sqrt{SC} - d$；稳定要求 $\sigma\sqrt{SC} < d$。

**冲击**：与直觉相反——随机复杂度降低稳定性。数值验证（`may_stability.py`）：σ√(SC)=0.9→1% 失稳；1.0→34%；1.1→74%；1.5→100%。

**修正**：真实食物网非随机——弱连接多（McCann 1998）、嵌套、模块化 → 可稳定。最终结论：**结构化复杂稳定，随机复杂失稳**。

### 21.2 Scheffer et al. (2001/2009) *Nature* 稳态转换 / 早期预警

**洞察**：多稳态 + 超阈值突变 + 滞后。fold 分岔；临界慢化 → Var↑、AR(1)↑、互相关↑、闪烁（`ews_tipping.py` 已验证）。

**意义**：生态学从事后描述变为**事前预警**；方法外溢到气候/金融/医学。

### 21.3 Hamilton (1964)《The Genetical Evolution of Social Behaviour》

**问题**：达尔文难题——利他如何进化？

**洞察**：基因视角。利他通过亲属间接传基因：$rB > C$ → 亲缘选择理论，解释真社会性（单倍二倍性：姐妹 r=3/4 > 母女 1/2）。

### 21.4 Hubbell (2001)《The Unified Neutral Theory》

**挑衅**：宏观多样性模式可由"生态等价 + 随机漂变 + 迁移"完全解释，无需生态位（Kimura 中性理论的生态版）。

**贡献**：把**零假设**引入群落生态学——任何生态位理论都要先击败中性零假设。现代共识：小尺度/高多样性中性主导，大尺度/强梯度生态位主导。

---

## 二十二、三个核心数学推导

### 22.1 May-Wigner 稳定性判据 σ√(SC) < d

**设定**：$\mathbf{J} = -d\mathbf{I} + \mathbf{A}$；$\mathbf{A}$ 非对角以概率 $C$ 取 $\mathcal{N}(0,\sigma^2)$。

**Step 1**：$\mathbf{A}$ 元素方差 $= C\sigma^2$（伯努利 × 高斯）。

**Step 2**：**Girko 圆律**——零均值 iid 随机矩阵（方差 $\varsigma^2$）的特征值均匀分布于复平面半径 $\varsigma\sqrt{S}$ 圆内。此处谱半径 $\rho(\mathbf{A}) \approx \sigma\sqrt{SC}$。

**Step 3**：$\mathbf{J}$ 特征值 $= -d + (\mathbf{A}\text{ 的特征值})$——谱圆左移 $d$。

**Step 4**：稳定 ⟺ 谱圆右缘 < 0：
$$-d + \sigma\sqrt{SC} < 0 \iff \sigma\sqrt{SC} < d$$

**直观**：$\sigma\sqrt{SC}$ 是互作"噪音"量级，$d$ 是自调节"刹车"。复杂度增大 → 噪音超刹车 → 失稳。

> 修正：食物网互作成对相关（±符号）把圆律变椭圆（Allesina-Tang 2012），但 √(SC) 标度不变。

### 22.2 Hamilton 规则 rB > C

**设定**：利他等位基因 $A$；携带者代价 $C$，受体收益 $B$；受体携带 $A$ 概率 = 亲缘系数 $r$。

**核算**（广义适合度）：
- 直接损失：$-C$
- 间接收益（亲属通道）：$+rB$
- 净效应：$\Delta W_A = rB - C > 0 \iff rB > C$

**亲缘系数**：自身 1；子女/全同胞 1/2；孙辈/半同胞 1/4；堂表 1/8。

**膜翅目**：单倍二倍 → 姐妹 r = 1/2(父) + 1/4(母) = **3/4** > 母女 1/2 → 帮母亲繁殖姐妹比自己生育更传基因。

### 22.3 边际值定理（MVT, Charnov 1976）

**问题**：斑块耗竭环境中何时离开？

**设定**：瞬时收益 $g(t)$ 递减；累计 $G(t)=\int_0^t g$；旅行时间 $\tau$。最大化长期平均：
$$R(t^*) = \frac{G(t^*)}{t^* + \tau}$$

**求导置零**：
$$\frac{dR}{dt^*} = \frac{g(t^*)(t^*+\tau) - G(t^*)}{(t^*+\tau)^2} = 0 \Rightarrow g(t^*) = \frac{G(t^*)}{t^*+\tau} = R$$

**结论**：当斑块**瞬时收益率下降到环境平均收益率时离开**。

**几何**：从 $(-\tau, 0)$ 向 $G(t)$ 曲线作切线，切点即 $t^*$。

**预测**（实验支持）：高质量斑块停留更久；旅行时间长 → 停留更久。

**普适**：最优停止理论经典；与经济学边际分析、bandit 的 explore-exploit 同构。

---

## 实验-理论对照表

| 实验 | 验证的理论 | 关键数值 |
|------|-----------|---------|
| chaos_logistic.py | May 1976 混沌 | 倍周期序列 + 周期3窗口 |
| leslie_matrix.py | Leslie 1945 | λ1=1.527；弹性：幼体存活 0.304 最大 |
| lotka_volterra.py | LV + RM | N\*=4, P\*=10；高K→极限环（富营养悖论）|
| ews_tipping.py | Scheffer EWS | Var τ=0.24↑, AR(1) τ=0.93↑（p<1e-5）|
| may_stability.py | May 1972 | 失稳概率在 σ√(SC)=d 处 sigmoid 跳变 |

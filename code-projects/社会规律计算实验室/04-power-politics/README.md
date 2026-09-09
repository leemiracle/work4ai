# 子领域 4 · Power-Politics · 权力、政治与冲突

> **研究命题**：革命为什么突然爆发？投票为什么不可能完美？极化为什么涌现？政治现象背后的数学骨架。

---

## 为什么这个子领域重要

政治学是社会科学里数学化最晚的——因为"权力"听起来不可量化。但 1950 年代后，Arrow / Downs / Buchanan / Olson 用博弈论和公理化方法证明：

- 民主有数学极限（Arrow）
- 革命是相变（Kuran / Granovetter）
- 极化从微观规则涌现（Hegselmann-Krause）

这些工具让你能**预测**政治现象的规律，而不只是描述。

---

## 章节地图

| # | 文件 | 核心问题 | 关键工具 |
|---|---|---|---|
| 1 | `01-arrow-impossibility.md` | 民主为什么不可能完美？ | Arrow 5 公理 |
| 2 | `02-revolution-phase.py` | 革命为什么突然爆发？ | Granovetter 阈值、Kuran 双重偏好 |
| 3 | `03-polarization-emergence.py` | 极化如何涌现？ | HK 有界信任模型 |

---

## 跑代码

```bash
cd /data/usershare/ai/social-laws/04-power-politics/
python3 02-revolution-phase.py
python3 03-polarization-emergence.py
```

---

## 核心命题回顾

跑完本子领域，你应该能用 5 句话总结：

1. **民主有数学极限**（Arrow 不可能定理）
2. **革命是相变**（Kuran 双重偏好 + 阈值模型）
3. **极化从微观规则涌现**（HK 有界信任）
4. **信息茧房降低 ε，加剧极化**
5. **预测革命几乎不可能——相变本质不可预测**

---

## 进阶批判

1. **Arrow 公理太强**：IIA 在政治中本就不合理
2. **Kuran 模型忽略网络结构**：阈值取决于邻居而非全体
3. **HK 假设观点是 1 维**：现实是多维
4. **政权也在学习**：会主动制造阈值断层
5. **西方中心主义**：政治理论主要来自西方民主国家

---

## 子领域间的连接

- **power-politics × cooperation**：投票是大规模合作博弈
- **power-politics × inequality**：不平等是革命诱因
- **power-politics × culture**：意识形态塑造阈值分布
- **power-politics × crosscuts**：算法×极化（子领域 7）

---

## 📊 已抓取的真实 CSSCI 论文（NCPSSD 核实）

### 📄 ⭐ 陈小鼎、张涛（2026）《世界政治极端化与国际关键矿产供应链安全》
- 《当代亚太》2026 年第 2 期，第 91-119 页
- **中国社科院亚太与全球战略研究院**（CSSCI 政治学顶刊）
- **直接对应**：本项目 `03-polarization-emergence.py` 的 HK 极化涌现模型
- **可对接**：把 HK 模型从"个体观点"扩展到"国家立场"，跑国际极化仿真

### 📄 廖凡、陈兆源（2026）《大国博弈与国际法的秩序价值》
- 《当代亚太》2026 年第 2 期，第 154-180 页
- 大国博弈 = 多人囚徒困境（模块 2）+ 国际合作（Ostrom 模块 2 第 4 节）

详见 [`docs/cssci-real-papers.md`](../docs/cssci-real-papers.md)

---

## 推荐文献

### 必读 ⭐
- Arrow, K. (1951). *Social Choice and Individual Values.*
- Kuran, T. (1989). *Sparks and Prairie Fires.* Public Choice.
- Hegselmann & Krause (2002). *Opinion dynamics and bounded confidence.* JASSS.

### 进阶
- Sen, A. (1970). *Collective Choice and Social Welfare.*
- Acemoglu & Robinson (2006). *Economic Origins of Dictatorship and Democracy.*

### 科普
- Sunstein, C. (2017). *#Republic.* （信息茧房）

---

## 完成标志

✅ 能列举 Arrow 5 公理
✅ 能解释 Kuran 双重偏好
✅ HK 模型能跑出极化涌现
✅ 写完 `notes/week-07-power-politics-finale.md`

---

*完成本章后进入 [`../05-culture-cognition/`](../05-culture-cognition/)*

# 子领域 3 · Inequality · 不平等与社会分层

> **研究命题**：财富差异如何涌现、固化、传递？这是社会科学的核心议题，也是数学化最有成果的领域之一。

---

## 为什么这个子领域重要

不平等是 21 世纪最大的政治议题。但讨论经常陷入情绪化——左派说"剥削"，右派说"自然"。

本子领域用数学回答：
- **涌现**：从微观随机规则必然产生不平等（Sugarscape）
- **形态**：财富分布为什么是幂律？（帕累托）
- **结构**：r > g 是不平等扩大的数学根源（Piketty）
- **流动**：代际传递如何？哪些政策有效？（Chetty）

数学让我们看清：**不平等不是阴谋，但也不是命运**。

---

## 章节地图

| # | 文件 | 核心问题 | 关键工具 |
|---|---|---|---|
| 1 | `01-pareto-distribution.py` | 财富为什么是幂律？ | 乘性过程、80/20、α 指数 |
| 2 | `02-sugarscape.py` | 不平等如何从随机涌现？ | ABM、Epstein-Axtell |
| 3 | `03-piketty-r-g.md` | r > g 的政策含义？ | 长期数据分析 |

---

## 跑代码

```bash
cd /data/usershare/ai/social-laws/03-inequality/
python3 01-pareto-distribution.py
python3 02-sugarscape.py
```

---

## 核心命题回顾

跑完本子领域，你应该能用 5 句话总结：

1. **财富是乘性过程 → 必然幂律**（帕累托）
2. **不平等从随机规则涌现**（Sugarscape）
3. **r > g 是结构性根源**（Piketty）
4. **机会平等不够，需要主动补偿**
5. **不平等 ≠ 剥削，但剥削加剧它**

---

## 进阶批判

1. **帕累托 α 不是命运**：政策可以改变 α（北欧 vs 美国）
2. **ABM 过度简化**：真实社会有制度、产权、文化
3. **Piketty 的 r 定义**：自住房和金融资产性质不同
4. **不平等的多维性**：财富 ≠ 收入 ≠ 机会 ≠ 幸福感
5. **代际流动 ≠ 静态平等**：北欧流动高，但静态差距也在扩大

---

## 子领域间的连接

- **inequality × networks**：富人的网络更密（Neckerman）
- **inequality × cooperation**：不平等破坏合作（模块 2）
- **inequality × revolution**：极端不平等引发相变（模块 4）
- **inequality × culture**：地位消费（Veblen）固化阶级
- **inequality × cities**：城市规模法则加剧（模块 6）

---

## 📊 已抓取的真实 CSSCI 论文（NCPSSD 核实）

### 📄 屈小博、林泽锋（2026）《人工智能暴露对中国城市零工工资的影响》
- 《财贸经济》2026 年第 6 期，第 105-124 页
- **中国社科院财经战略研究院**（CSSCI 经济学顶刊）
- **直接对应**：Piketty `r > g` 的 21 世纪版本——AI 资本对零工劳动的暴露度
- **可对接代码**：在 `02-sugarscape.py` 里加"AI 冲击"参数

### 📄 尹涛等（2026）《数据资产能否降低企业债务违约风险》
- 《财贸经济》2026 年第 6 期，第 87-104 页
- 数据作为新资本——K/Y 公式里 K 现在包括数据资产

详见 [`docs/cssci-real-papers.md`](../docs/cssci-real-papers.md)

---

## 推荐文献

### 必读 ⭐
- Piketty, T. (2014). *Capital in the 21st Century.*
- Epstein & Axtell (1996). *Growing Artificial Societies.*
- Chetty et al. (2017). *Mobility Rates in the 100 Largest Commuting Zones.*

### 数据
- World Inequality Database: [wid.world](https://wid.world)
- Oxfam 年度不平等报告
- 中国家庭金融调查 (CHFS)

---

## 完成标志

✅ 能解释帕累托 α 的含义
✅ Sugarscape 跑出不平等涌现
✅ 能默写 r > g 的含义
✅ 写完 `notes/week-06-inequality-finale.md`

---

*完成本章后进入 [`../04-power-politics/`](../04-power-politics/)*

# 子领域 1 · Relations · 社会关系与网络

> **研究命题**：你的机会、你的权力、你的命运，更多由你的**关系结构**决定，而非你的能力。

---

## 为什么从这里开始

社会网络科学是**社会科学里最数学化、最可验证、最容易可视化**的分支。它是从文科跨入数理社科的最佳桥梁——格兰诺维特凭一篇弱连带论文就能名垂青史，因为网络视角直接改写了"关系是什么"的定义。

更重要的：**网络视角贯穿本项目所有其他子领域**。
- 合作问题（子领域 2）= 节点在网络上反复博弈
- 不平等（子领域 3）= 财富在网络上累积
- 革命（子领域 4）= 信息在网络上扩散
- 文化（子领域 5）= 模因在网络上传播
- 城市（子领域 6）= 空间网络上的Schelling 模型

学完这一章，你就有了一套**反复使用**的工具。

---

## 章节地图

| # | 文件 | 核心问题 | 关键工具 |
|---|---|---|---|
| 1 | `01-graph-basics.py` | 怎么用数学描述"关系"？ | 图论基础、邻接矩阵、Karate Club |
| 2 | `02-weak-ties.py` | 为什么找工作靠"不熟的人"？ | Granovetter 弱连带、信息冗余 |
| 3 | `03-small-world.py` | 为什么是"六度分隔"？ | Watts-Strogatz 模型、相变 |
| 4 | `04-scale-free.py` | 为什么会有 hubs？ | BA 模型、幂律、优先链接 |
| 5 | `05-centrality-power.py` | "权力"怎么测？ | 4 种中心性、PageRank |

---

## 跑代码

```bash
cd /data/usershare/ai/social-laws/01-relations/
python3 01-graph-basics.py    # 图论基础
python3 02-weak-ties.py       # Granovetter 弱连带
python3 03-small-world.py     # Watts-Strogatz
python3 04-scale-free.py      # BA 无标度
python3 05-centrality-power.py # 4 种中心性
```

每个文件会生成同名 `.png` 可视化。

---

## 核心命题回顾

跑完这 5 节，你应该能用 5 句话总结 relations 子领域：

1. **关系结构决定机会**——同样能力的人，位置不同结果不同。
2. **弱连带是桥**——格兰诺维特反直觉地发现"不熟的人更有用"。
3. **小世界涌现**——少量"远程边"让网络平均距离暴跌。
4. **富者愈富**——优先链接让 hubs 自发产生，幂律是结果。
5. **权力有 4 种数学**——度/介数/特征向量/PageRank 各识别一种权力。

---

## 进阶批判（写在最后）

学完本章，**警惕**：
- 网络结构是必要的，但**不充分**解释社会现象
- 中心性 ≠ 真实权力（见 05 节末尾的批判）
- 网络是静态的，社会是动态的
- "关系决定命运"会被某些政治立场利用（精英主义 / 关系主义）
- 网络分析源自西方个人主义传统，**家族/集体社会**可能需要修正

→ 这些批判会贯穿后续所有子领域，并在子领域 7（crosscuts）的伦理讨论中回到中心。

---

## 推荐文献

### 必读 ⭐
- Granovetter 1973 - *The Strength of Weak Ties*
- Watts & Strogatz 1998 - *Collective dynamics of 'small-world' networks* (Nature)
- Barabási & Albert 1999 - *Emergence of Scaling in Random Networks* (Science)

### 教材 📖
- Barabási - *Network Science*（免费在线：networksciencebook.com）
- Newman - *Networks* (2nd ed.)

### 科普 💡
- Barabási - *Linked* (2002)
- Christakis & Fowler - *Connected* (2009)

---

## 完成标志

✅ 5 个 `.py` 都跑出图
✅ 能解释"为什么弱连带比强连带更有用"
✅ 能写出 WS 模型的相变公式
✅ 能默写 BA 模型的两条核心机制
✅ 能比较 4 种中心性指标的语义差异
✅ 写完 `notes/week-03-relations-finale.md`

---

*完成本章后进入 [`../02-cooperation/`](../02-cooperation/)*

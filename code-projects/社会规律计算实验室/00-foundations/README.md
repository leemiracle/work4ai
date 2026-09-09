# 模块 0 · Foundations · 方法论基础

> 这里没有代码，只有"为什么"和"怎么做"。如果你跳过本模块直接写代码，会发现**你有工具却不知道要修什么**。

---

## 本模块要解决的问题

1. **为什么要用数学研究社会？**——这不是显然的事。社会学主流传统是定性研究。我们要回答：数学化带来了什么、丢失了什么。
2. **本项目的研究套路是什么？**——从现象到模型到批判的完整流程。
3. **我数学不够怎么办？**——`math-primer.md` 自检 + 边学边补，不要等。
4. **工具链如何准备？**——Python + NumPy + NetworkX + Matplotlib。

---

## 任务清单（Week 0-1，5-10h）

### Day 1：阅读 + 思考（2h）
- [ ] 通读 [`../docs/methodology.md`](../docs/methodology.md)
- [ ] 划出 3 个最有共鸣的论点，写到 `../../notes/week-00-methodology.md`
- [ ] 划出 3 个最让你怀疑的论点，记下疑问

### Day 2：数学自检（2h）
- [ ] 做 [`../docs/math-primer.md`](../docs/math-primer.md) 全部 5 大项 15 道题
- [ ] 填表自评（🟢/🟡/🔴）
- [ ] 把结果存到 `../../notes/week-00-math-selfcheck.md`
- [ ] 制定补课计划（按优先级，参照 math-primer 末尾）

### Day 3：工具链（1h）
- [ ] `pip install numpy scipy networkx matplotlib`
- [ ] 跑测试代码：
  ```python
  import numpy as np, networkx as nx, matplotlib.pyplot as plt
  g = nx.karate_club_graph()
  nx.draw(g, with_labels=True)
  plt.savefig("../../notes/test-network.png")
  ```
- [ ] 如果上面跑不通，找原因（Python 版本、依赖冲突）

### Day 4：浏览文献（2h）
- [ ] 通读 [`../docs/reading-list.md`](../docs/reading-list.md)
- [ ] 挑出阶段 1-2 要读的 3 篇 ⭐ 项
- [ ] 找到这些文献的 PDF 或链接，存到 `../../notes/papers/`

### Day 5：复盘 + 启动（1-3h）
- [ ] 写 `../../notes/week-00-reflection.md`（300-500 字）：
  - 本项目和你想象的一样吗？
  - 数学自检结果如何？最弱在哪？
  - 你最期待的子领域是哪个？为什么？
- [ ] 开始子领域 1：`../01-relations/`

---

## 本模块的"非任务"

不要做这些：
- ❌ **不要先补完所有数学再开始**——边学边补，先跑代码。
- ❌ **不要把所有文献读完再开始**——每周读 1-2 篇就够。
- ❌ **不要追求完美理解 methodology**——理解 70% 就够，剩下 30% 在做项目中慢慢消化。
- ❌ **不要纠结于项目哲学**——干起来，比想清楚更重要。

---

## 一个关键提醒

本项目的所有"研究"都是**模仿真实研究**——但**不是真正的研究**。

真实研究需要：
- 处理真实数据
- 与已有文献对话
- 提出新问题或新方法
- 接受同行评审

本项目的目标是**让你具备做真实研究的能力**——把 Schelling 模型跑通、理解 Piketty 的 r > g、能复现 Generative Agents——这些是基础。**有了这些基础，你才能做真正的新研究**。

所以前 10 周不要焦虑"我什么时候能做新东西"。先**把经典吃透**。牛顿说"站在巨人肩上"，他没说的是"上肩的过程很费劲"。

---

## 完成标志

✅ methodology 能复述给一个外行听
✅ 数学自检 5 项里至少 2 项绿
✅ 工具链跑通
✅ 写完 `notes/week-00-reflection.md`
✅ 准备好进入 `01-relations/`

---

*进入下一关：[`../01-relations/`](../01-relations/)*

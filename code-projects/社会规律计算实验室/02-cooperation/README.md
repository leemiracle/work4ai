# 子领域 2 · Cooperation · 合作与集体行动

> **研究命题**：自然选择鼓励自私，为什么生物界（包括人类）有那么多合作？这是横跨演化生物学、博弈论、政治哲学的核心问题。

---

## 为什么这个子领域如此根本

"合作如何可能？" 是 20 世纪社会科学的最深问题之一：
- **经济学**：市场合作 vs 公地悲剧
- **政治学**：民主如何运转 vs 革命如何爆发
- **生物学**：真社会性昆虫、利他行为
- **哲学**：道德从哪里来？
- **AI**：怎么让多智能体合作？

每门学科都从不同角度回答这个问题，但**数学骨架是同一套**：博弈论 + 演化动力学。

---

## 章节地图

| # | 文件 | 核心问题 | 关键工具 |
|---|---|---|---|
| 1 | `01-classic-games.py` | 理性人为什么会背叛？ | 囚徒困境、Axelrod 锦标赛 |
| 2 | `02-nash-math.md` | 怎么证明均衡存在？ | Kakutani 不动点（硬数学） |
| 3 | `03-evolutionary-game.py` | 演化如何选策略？ | 复制子动力学、ESS |
| 4 | `04-collective-action.md` | 公地悲剧能避免吗？ | Olson vs Ostrom |
| 5 | `05-five-rules-nowak.md` | 合作的统一理论？ | Nowak 五规则 |

---

## 跑代码

```bash
cd /data/usershare/ai/social-laws/02-cooperation/
python3 01-classic-games.py        # 经典博弈 + Axelrod 锦标赛
python3 03-evolutionary-game.py    # 演化博弈
```

`02-nash-math.md`、`04-collective-action.md`、`05-five-rules-nowak.md` 是纯数学/理论文档，不需要跑代码（但可以挑战自己实现）。

---

## 核心命题回顾

跑完这 5 节，你应该能用 6 句话总结：

1. **个体理性 ≠ 集体理性**——囚徒困境
2. **混合策略让任何博弈都有均衡**——Nash 定理
3. **重复博弈里 TIT-for-TAT 称王**——Axelrod 锦标赛
4. **合作可以演化为稳定策略**——ESS
5. **公地悲剧不是必然**——Ostrom 八原则
6. **合作演化遵循 5 条数学规则**——Nowak

---

## 进阶批判

学完本章，**警惕**：

1. **博弈论不是道德指南**
   - "纳什均衡"告诉你人们会停在哪，不告诉你应该停在哪
   - "理性" 在博弈论里 = 最大化支付，与日常理性不同

2. **支付矩阵是研究者设定的**
   - 同一个故事用不同支付矩阵 → 不同结论
   - 谁定义"代价"和"收益"，谁就定义了"理性"

3. **演化博弈的"适应度"假设**
   - 把生物繁殖等同于策略扩散，是简化
   - 文化演化更复杂（不是达尔文式的）

4. **Ostrom 八原则的边界**
   - 对 N > 1000 的大群体不适用
   - 全球公地（气候、海洋）可能根本无法自治

5. **Nowak 五规则的文化特殊性**
   - 主要来自西方研究传统
   - 东亚社会的合作机制可能不同（集体主义、面子、关系）

---

## 子领域间的连接

- **合作 × 网络**（与子领域 1）：网络结构影响合作演化（Nowak 规则 4）
- **合作 × 不平等**（与子领域 3）：合作失败 → 不平等加剧
- **合作 × 政治**（与子领域 4）：民主制度 = 大规模合作机制
- **合作 × 文化**（与子领域 5）：文化规范降低合作成本
- **合作 × LLM**（与子领域 7）：AI 多智能体合作是前沿问题

---

## 📊 已抓取的真实 CSSCI 论文（NCPSSD 核实）

### 📄 ⭐ 张帅（2026）《权力分配、资源筹措与多利益攸关方参与全球粮食安全治理的有效性》
- 《当代亚太》2026 年第 2 期，第 120-153 页
- **中国社科院亚太与全球战略研究院**（CSSCI 政治学顶刊）
- **直接对应**：本项目 `04-collective-action.md` 的 Ostrom 公地治理
- 多利益攸关方 = N 人公共物品博弈；粮食安全 = 全球公地
- **可对接**：Ostrom 八原则在 N=全球尺度的实证检验

### 📄 封凯栋、纪怡（2026）《创新竞争的市场机制：纳尔逊理论视角下的分析》
- 《经济思想史学刊》2026 年第 2 期，第 66-95 页
- **中国社科院经济所**（CSSCI 经济学顶刊）
- 纳尔逊（Richard Nelson）演化经济学——直接对接本项目 `03-evolutionary-game.py` 复制子动力学

详见 [`docs/cssci-real-papers.md`](../docs/cssci-real-papers.md)

---

## 推荐文献

### 必读 ⭐
- Axelrod, R. (1984). *The Evolution of Cooperation.*
- Nowak, M. (2006). *Five Rules for the Evolution of Cooperation.* Science.
- Ostrom, E. (1990). *Governing the Commons.*

### 数学硬核 📖
- Osborne, M. (2003). *An Introduction to Game Theory.*
- Nowak, M. (2006). *Evolutionary Dynamics.*

### 科普 💡
- Dawkins, R. (1976). *The Selfish Gene.*
- Ridley, M. (2010). *The Rational Optimist.*
- Nowak & Highfield (2011). *SuperCooperators.*

---

## 完成标志

✅ 能默写囚徒困境支付矩阵
✅ 能解释 TIT-for-TAT 的 4 大美德
✅ 能写出复制子动力学方程
✅ 能列举 Ostrom 八原则的至少 5 条
✅ 能列举 Nowak 五规则
✅ 写完 `notes/week-05-cooperation-finale.md`

---

*完成本章后进入 [`../03-inequality/`](../03-inequality/)*

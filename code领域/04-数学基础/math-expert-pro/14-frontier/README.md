# 14-frontier：数学前沿追踪模块

> 解决痛点：**「发展太快，没办法直接找到最前沿最有效的」**
> 定位：你身边的一位"数学雷达"——告诉你**当下最热的方向、最大的突破、最值得追的人**，并标注**可信度与时效**。

---

## 🎯 这个模块解决什么

数学不再是 19 世纪的"缓慢学科"。2024-2026 的现实：
- **AI 正在重写数学研究方式**：AlphaProof 在 IMO 2024 拿银牌（28/42），AlphaEvolve 发现新算法，Lean 4 成为形式化标准
- **千禧问题逐个被蚕食**：Poincaré 已解（Perelman），其余 6 个每年都有"逼近"
- **方向爆炸**：解析数论、加性组合、随机矩阵、深度学习理论、Tropical 几何…新方向层出不穷
- **信息淹没**：arXiv math 每天新增 200+ 篇，没人能读完

**本模块 = 你的前沿过滤器**：把噪音过滤掉，只留"重要 + 可信 + 与你的路径相关"。

---

## 📁 目录结构

| 文件 | 内容 | 何时查 |
|------|------|--------|
| [arXiv地图/](arXiv地图/) | arXiv math 分类树 + 各领域活跃度 + 怎么订阅 | 想追某方向的最新论文 |
| [顶刊与奖项/](顶刊与奖项/) | Annals/Inventiones/JAMS/Acta 发表规律 + Fields/Abel/突破奖得主工作 | 想知道"谁是当下权威" |
| [conjecture进展/](conjecture进展/) | 7 大千禧问题 + 50 个重要猜想 的最新进展追踪表 | 想看"人类知识的边界在哪" |
| [AI-for-Math/](AI-for-Math/) | AlphaProof/Lean/FunSearch/Auto-TPS 全图谱 + 形式化数学革命 | 想了解 AI 如何改变数学 |
| [热点方向追踪/](热点方向追踪/) | 2024-2026 最热 10 方向（深度学习理论/加性组合/...）+ 入口文献 | 想选研究方向 / 找论文选题 |

---

## 🔥 必读三份（按顺序）

### 1. [AI-for-Math/01-AI正在重写数学研究.md](AI-for-Math/01-AI正在重写数学研究.md) ⭐
**2024-2026 最重要的事**。AlphaProof IMO 银牌 → Lean 形式化革命 → AlphaEvolve 进化算法设计。如果你只读一份，读这份。

### 2. [conjecture进展/千禧问题与大猜想进展表.md](conjecture进展/千禧问题与大猜想进展表.md) ⭐
七大千禧难题的最新进展（截至 2026.07）+ 50 个重要猜想的"已解决/部分进展/开放"状态表。

### 3. [热点方向追踪/2024-2026十大热点方向.md](热点方向追踪/2024-2026十大热点方向.md) ⭐
当下最活跃的 10 个数学方向，每个附"为什么热 + 入门文献 + 与 AI 的交叉"。

---

## 📡 信息源金字塔（可信度排序）

```
Tier S（最高可信，事实基准）
├── Annals of Math / Inventiones / JAMS / Acta Math（四大顶刊，同行评审 ≥1 年）
├── Fields/Abel/突破奖得主官方页面
├── arXiv 经四大刊接收的预印本
└── ICM 邀请报告（4 年一次）

Tier A（高可信，专家解读）
├── Terence Tao 博客 "What's New"（terrytao.wordpress.com）
├── Tim Gowers 博客（gowers.wordpress.com）
├── Quanta Magazine 数学板块（quantamagazine.org/mathematics）
├── AK @_akhaliq（每日 arXiv 速递）
└── ICM/ICM卫星会议讲座视频

Tier B（中等可信，需交叉验证）
├── MathOverflow 高赞回答
├── Not Even Wrong / Secret Blogging Seminar
├── 机器之心/PaperWeekly 数学专栏
└── Numberphile / Mathologer / 3Blue1Brown（科普但权威）

Tier C（低可信，仅作线索）
├── 社交媒体转发（需回溯 Tier S/A 源）
└── 预印本未经评审的"声称证明"
```

> **铁律**：任何"X 问题被解决"的消息，必须回溯到 Tier S 源（顶刊或获奖）才算数。预印本"声称证明"的，标记为 🟡 待验证。

---

## ⏱️ 追踪节奏建议

| 频率 | 动作 | 时长 |
|------|------|------|
| 每天 | 扫 AK 推特 + arXiv 你订阅的 2-3 个分类 | 10 min |
| 每周 | 读 1 篇 Quanta 数学文 + 翻 Tao 博客标题 | 30 min |
| 每月 | 精读 1 篇 hot direction 的综述/survey | 2 h |
| 每季度 | 更新 [conjecture进展表](conjecture进展/) | 1 h |
| 每年（ICM 年）| 看 Fields 得主工作 + ICM 邀请报告列表 | 1 周 |

---

## 🎯 与项目其他模块的连接

| 你想... | 跳到 |
|---------|------|
| 把前沿与主轨学习结合 | [01-track/stage-3-研究方向/](../01-track/stage-3-研究方向/) |
| 看某个前沿方向需要哪些基础 | [17-decision/方向决策/](../17-decision/方向决策/) |
| 找某个前沿方向的教材 | [09-crosstext/](../09-crosstext/) + [18-resources/](../18-resources/) |
| 形式化验证你的证明 | [AI-for-Math/02-Lean形式化数学入门.md](AI-for-Math/02-Lean形式化数学入门.md) |
| 看 Tao 如何实践 AI 数学（PFR/Equational Theories）| [AI-for-Math/03-Tao的AI数学实践.md](AI-for-Math/03-Tao的AI数学实践.md) ⭐ |
| 看数学家怎么追前沿 | [02-lens-mathematicians/反思层/开放记录轴.md](../02-lens-mathematicians/反思层/) |

---

## 📊 时效声明

- 本模块所有事实标注**信息日期**（如「2024.07.25 DeepMind 官方」）
- 每年 ICM 后（8 月）+ 年底（12 月）做两次内容刷新
- 任何"突破"消息默认标 🟡 待验证，直至 Tier S 源确认

---

> 💡 **使用心法**：前沿是"视野"不是"任务"。不要焦虑追不上——选 2-3 个与你路径相关的方向深跟，其余只扫标题。**深度 > 广度，可信 > 速度**。

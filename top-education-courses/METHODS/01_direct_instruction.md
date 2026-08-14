# 01 · 直接教学 (Direct Instruction)

> 旗手：**Engelmann (Distar) / Rosenshine / Kirschner-Sweler-Clark**。被进步主义长期低估、却**证据最硬**的教学法。新手教学的默认选择。

---

## 核心机制

**Rosenshine "Principles of Instruction" (2012)** 十原则（共识提炼）：
1. 每日复习（激活先前知识）
2. 新材料小步呈现
3. 提大量问题
4. 建模（think aloud）
5. 检查全员理解
6. 引导练习（ scaffolded ）
7. 独立练习
8. 当场反馈
9. 高成功率达（~80%）
10. 周月复习 + 间隔 + 检索

= **小步 + 高频互动 + 即时反馈 + 重复**。

## 证据

- **Project Follow Through**（1968–1977，美国最大教育实验）：直接教学组在所有科目**显著胜出**其他 8 种教学法。
- **Hattie d≈0.6**（高质量直接教学）。
- **Kirschner/Sweler/Clark (2006)** "Why Minimal Guidance During Instruction Does Not Work"：对**新手**，直接教学远优于纯发现。

## 何时用
- 新手（图式少）
- 结构化知识（数学/语法/程序/技能奠基）
- 时间紧
- 高成功率奠基阶段

## 何时翻车
- 熟手（无聊、不挑战）
- 高阶能力（批判/创造）——直接讲不出高阶
- 动机已高的学生（压抑自主）

## RL 接口
直接教学 = **dense reward shaping + curriculum**：
- 小步 = 细粒度 curriculum
- 即时反馈 = dense reward
- 高成功率 = 可达 reward（避免无效负 reward）

新手缺 world model，dense reward 让 model-free 学习成为可能。这正是直接教学对新手有效的 RL 解释。

## 项目锚点
- **ZPD**：直接教学把任务切到 ZPD 下沿，新手够得着。
- **费曼 F2**：直接教学的"检查理解"= 轻量 F2 门。
- **欺骗动力学**：直接教学的危险=学生"跟得上节奏"≠"懂"。要 F2 迁移题戳穿。

> 📌 下一步：[`02_discovery_pbl.md`] 看直接教学的对立面。

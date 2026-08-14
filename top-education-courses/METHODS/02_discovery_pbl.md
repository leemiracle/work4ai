# 02 · 发现学习 / 项目式学习 PBL

> 旗手：**Bruner (发现学习) / Papert (constructionism) / Buck Institute (PBL)**。直接教学的对极——学生在真实问题中自主探究。

---

## 核心机制

- **发现学习**（Bruner 1960）：学生自己发现规律（如归纳几何性质），而非被告知。
- **PBL**（项目式）：长程真实项目驱动，多学科整合。
- **建构主义 constructionism**（Papert）：**通过制作外物**建构知识（孩子用 LOGO 编程学几何）。

关键变体：
- **纯发现**（无指导）：❌ 对新手有害
- **引导式发现**（guided discovery）：✅ 教师提供支架/线索/边界

## 证据

- **Kirschner 2006**：纯发现学习对新手效应 < 直接教学。
- **Hattie**："problem-based learning" 对**医学等高阶熟手** d≈0.6；对**新手** d<0.4。
- **PBL（Buck Institute 标准）**：有效条件是**有支架 + 真实驱动问题 + 公开成果 + 反思**。

> 🪶 关键变量不是"发现 vs 讲"，是**学习者已有图式**。熟手图式够，能自主建构；新手图式缺，纯发现 = 在 ZPD 外空转。

## 何时用
- 熟手（已有基础）
- 高阶能力（批判/创造/整合）
- 时间允许（PBL 慢）
- 真实世界问题（动机高）

## 何时翻车
- 新手无支架（迷路、挫败）
- 时间紧（PBL 講不完大纲）
- 目标模糊（学生不知道"做完算什么"）
- 教师不会支架（关键技能）

## PBL 成功的必要条件（Buck Institute Gold Standard PBL）
1. 有挑战的驱动问题
2. 持续探究
3. 真实情境
4. 学生声音与选择
5. 反思
6. 批评与修订
7. 公开成果

> 缺任一项，PBL 退化为"主题活动"——热闹但没深度学习。

## RL 接口
发现学习 = **sparse reward + exploration**：
- 纯发现 = 纯 sparse reward → 新手样本效率极低
- 引导式发现 = sparse reward + reward shaping（教师提示）→ 可行
- PBL = 多目标 long-horizon RL

熟手有 world model，sparse reward 也能学（model-based 规划）。新手无 model，sparse reward 学不动。**这是 PBL 对熟手有效对新手无效的 RL 解释**。

## 项目锚点
- **ZPD**：PBL 把学生推到 ZPD 上沿挑战。新手没有下沿基础，会跌出 ZPD。
- **故事原语**：PBL = 把学习编成"真实故事"（有驱动问题 = 有 Purpose）。故事化学习法（[`../../故事化学习法/`]）是 PBL 的元理论版。
- **熵治理**：PBL 高效熵减（真实问题信息量大），但协调/摸索成本也高（边缘熵增）。
- **欺骗动力学**：PBL 易被"假探究"欺骗——学生表演做项目但没深想。F2 + 公开成果（critique & revision）防骗。

> 📌 下一步：[`03_mastery_flipped.md`] 看直接教学的"掌握学习"变体 + 翻转课堂。

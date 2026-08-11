# CS224V: Conversational Virtual Assistants with Deep Learning

> Stanford University, Autumn 2025
> Instructor: **Monica Lam** (Stanford 编译器女王)
> Time: Mon/Wed 3:00-4:20 PM, Gates B1
> Prerequisites: LINGUIST 180/280 / CS124 / CS224N/U/S 之一
> Units: 3-4
> Difficulty: ⭐⭐⭐⭐

---

## 📚 课程独特定位

**Monica Lam 不是普通 NLP 教授**——她是**编译器 + 系统专家**。她把 LLM 当编译目标：

> "用 SMT (Satisfiability Modulo Theories) 求解器约束 LLM，实现**数学上无幻觉**的 agent"

这是与 CS329Z（prompt 工程）和 CS329H（RLHF）**完全不同的路线**！

---

## 🎯 7 个核心问题

| # | 问题 | Monica Lam 的解法 |
|---|------|-----------------|
| 1 | RAG without hallucination | 用 SMT 约束检索 |
| 2 | 自然语言 → SQL / SPARQL | SMT 验证 |
| 3 | 文献综述自动写作 | 非幻觉引用 |
| 4 | 无幻觉 task agent | 工具调用形式化 |
| 5 | 长文档 QA | 增量检索 |
| 6 | 从文档提取 KG | SMT 一致性检查 |
| 7 | SMT 提升推理 | 把推理变可满足性问题 |
| 8 | Computational thinking | 程序合成 |

---

## 📅 教学模式

- **2 个 Homeworks**（开始 5 周）：用工具构建无幻觉 LLM agent
- **Project**（剩余 7 周）：65% 评分
- **强制出勤**（15% 评分）
- **每周 mentor meeting**（10-15% 评分）

---

## 💻 项目代码

📁 `supplementary/grad_projects.py::cs224v_demo`

**实现**:
1. ✅ SMT Solver 简化版（事实集 + 规则）
2. ✅ 一致性检查（claim vs known facts）
3. ✅ NonHallucinatingAgent（拒绝回答无法验证的问题）
4. ✅ 知识库 + 规则推理

### 运行
```bash
cd supplementary
python3 grad_projects.py
```

**输出**:
```
Q: Transformer 是哪一年提出的？
A: [拒绝回答 - 无法验证]   ← 因为"2017" 在 KB 里是 "transformer 提出于 2017"

Q: BERT 基于什么架构？
A: BERT 基于 encoder 架构
Verified: True - ✓ 直接支持

Q: 什么是量子纠缠？
A: [拒绝回答 - 无法验证]   ← 不在知识库 → 拒绝
```

---

## 🎓 Project Gallery

2025 学生作品可访问: https://cs224v-2025-projects.genie.stanford.edu/

---

## 📊 与 CS329Z 的关键区别

| 维度 | CS329Z | CS224V |
|------|--------|--------|
| 解决幻觉 | prompt + 数据 | **SMT 约束** |
| 工具调用 | 函数 API | 形式化规约 |
| 验证 | 经验评估 | **数学证明** |
| 哲学 | 经验主义 | **形式主义** |

**Monica Lam 的方法**在数学上更可靠，但工程上更复杂。**强烈推荐**给想做"严肃 AI"（医疗 / 法律 / 金融）的学生。

---

## 🎯 学习路径

| 角色 | 推荐 |
|------|------|
| **想做严肃 AI（医疗/法律）** | CS224V 必修 |
| **想做形式化方法** | CS224V + CS157 (Logic) |
| **想做 RAG** | CS329Z → CS224V（深化）|
| **想做对话系统** | CS224V + CS224N |

---

## 🚀 扩展

完成后推荐：
1. **Stanford Genie Lab** — Monica Lam 研究组
2. Dafny / Lean / Coq — 形式化验证工具
3. Z3 Solver — 微软的 SMT 求解器
4. OpenAI *Process Reward Models* — 类似思路（process verification）

---

**对应代码**: `supplementary/grad_projects.py::cs224v_demo`

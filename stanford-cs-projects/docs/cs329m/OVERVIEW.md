# CS329M: Introduction to Machine Programming

> Stanford University, Autumn 2025
> Instructors: **Ranjit Jhala** + **Justin Gottschlich** (前 Meta AI, MP 概念创始人)
> Time: Tue 6:00-8:50 PM（**晚上 3 小时研讨**）
> Difficulty: ⭐⭐⭐⭐

---

## 📚 课程定位

**"Machine Programming" (MP)** 是 Gottschlich 在 Meta 提出的概念：

> "自动化软件开发的全部流程——从 spec 到代码到测试到部署"

与 CS329Z（通用 agent）区别：CS329M 专攻**代码生成 + 形式化方法**。

---

## 📅 推测模块（基于讲师研究方向）

### Part 1: MP 历史
1. compiler → 类型系统 → IDE → LLM agent 的演化
2. **Gottschlich "The Three Pillars of MP"** (ACM 2018):
   - Intention (spec)
   - Invention (algorithm)
   - Adaptation (correctness + efficiency)

### Part 2: 形式化规约
- Dafny / TLA+ / Coq
- Hoare Logic
- 契约式设计 (Design by Contract)

### Part 3: 类型系统 + 程序合成
- Type-directed synthesis
- Houdini (auto-witness)
- Example-driven synthesis (FlashFill)

### Part 4: LLM-based Code Generation
- **CodeBERT / CodeT5** (Salesforce)
- **StarCoder / Code Llama** (Meta/HF)
- GitHub Copilot / Codex 架构
- 上下文学习 vs fine-tuning

### Part 5: 自动测试生成
- Fuzzing (AFL / LibFuzzer)
- Property-based testing (Hypothesis)
- LLM-based test generation

### Part 6: 程序修复 (APR)
- Pattern-based (GenProg)
- ML-based (Prophet)
- LLM-based repair

### Part 7: Code Agent（最重要）
- **AlphaCode / AlphaCode 2** (DeepMind)
- **SWE-bench / SWE-agent** (Stanford)
- **OpenHands** (前 OpenDevin)
- **Claude Code / Codex** (Anthropic / OpenAI)

### Part 8: Bug Detection
- Static analysis (Infer / Coverity)
- ML-based (SySeVR / Devign)
- LLM-based (GPT-4 vulnerability detection)

### Part 9: Program Verification
- Dafny / F* (Microsoft Research)
- Coq + AI assist (CoqHammer)
- Lean + LLM (Lean Copilot)

### Part 10: Future
- 完全自主编程？
- AI 与人类 pair programming 的演化
- 程序员技能的重新定义

---

## 💻 项目代码

📁 `topic2-agent-v2/hw3_self_improve_coding.py::MiniCodingAgent`

**实现** mini SWE-agent：
1. ✅ 接受自然语言任务描述
2. ✅ 生成初版代码
3. ✅ 在沙箱中运行测试
4. ✅ 失败时分析错误 + 重试
5. ✅ 多次尝试 + 错误恢复

### 测试 Tasks（含真实测试代码）
```python
tasks = [
    CodingTask(
        description="Write a function that adds two numbers",
        test_code="assert solve(2, 3) == 5",
    ),
    CodingTask(
        description="Write factorial function",
        test_code="assert solve(5) == 120",
    ),
    # ...
]
```

**结果**: 4/4 (100% success rate)

---

## 📊 关键论文

### 🔴 P0
1. **Gottschlich et al. 2018** "The Three Pillars of Machine Programming" OOPSLA
2. **Li et al. 2022** "Competition-Level Code Generation with AlphaCode" Science
3. **Yang et al. 2024** "SWE-agent: Agent-Computer Interfaces" NeurIPS
4. **Wang et al. 2025** "OpenHands" ICLR
5. **Jimenez et al. 2024** "SWE-bench" ICLR
6. **Chen et al. 2021** "Evaluating LLMs Trained on Code" (Codex/HumanEval) arXiv

### 🟡 P1
7. **Nijkamp et al. 2022** "CodeGen"
8. Rozière et al. 2023 "Code Llama"
9. Li et al. 2023 "StarCoder"
10. **Le et al. 2024** "AlphaCodium"

---

## 🎯 学习路径

| 角色 | 推荐 |
|------|------|
| **想做 coding agent** | CS329M + CS329Z |
| **想形式化方法** | CS329M + CS157 (Computational Logic) |
| **想做 IDE/工具** | CS329M + CS242 (PL) |
| **想去 Cursor/Copilot** | CS329M + CS329Z W9 SWE-agent |

---

## 💡 与 CS329Z 区别

| 维度 | CS329Z | CS329M |
|------|--------|--------|
| 视角 | 通用 agent | 专攻代码 |
| 重点 | 系统设计 | 程序语义 |
| 工具 | DSPy / LangChain | Dafny / Fuzzer / Compiler |
| 评估 | 4-tuple eval | Test execution + coverage |

---

**对应代码**: `topic2-agent-v2/hw3_self_improve_coding.py`

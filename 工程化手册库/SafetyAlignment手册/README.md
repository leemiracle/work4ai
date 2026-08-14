# Safety / Alignment 工程手册

> **是什么**：让 AI 行为对齐人类价值——不伤害 + 有用 + 诚实（HHH）。
> **为什么重要**：越强大的 AI，对齐越关键。**不对齐的 AGI = 灭绝风险**。

---

## 1. 是什么

**Alignment（对齐）** = 让 AI 做**人类想让它做的事**，而不是**它被优化去做的事**。

**核心难题**：
- **规范问题**（Specification）：reward function ≠ 真实意图
- **奖励黑客**（Reward Hacking）：AI 学会骗 reward model
- **分布外**（OOD）：训练时没见过的新场景

**3 层对齐**：
```
1. 指令对齐：遵循用户指令（SFT + RLHF）
2. 价值对齐：不违反人类价值（Constitutional AI）
3. 目标对齐：追求正确的终极目标（AGI 级别，未解决）
```

## 2. 主流方法

### RLHF（2022, OpenAI）
```
SFT → Reward Model → PPO
```
- 3 步：SFT + RM + PPO
- **问题**：reward hacking / sycophancy / 训练不稳定

### Constitutional AI（2022, Anthropic）
```
SFT → AI 自我批评 → AI 自我修正 → 训练
```
- 用 **Constitution**（一组原则）指导
- AI 自己当 reviewer
- **优点**：不需要大量人类标注

### DPO（2023, Stanford）
```
SFT → 直接用偏好数据优化（跳过 RM + RL）
```
- 简化 RLHF
- **关键**：reward model 隐含在策略里

### GRPO（2024, DeepSeek）
```
SFT → 用规则当 reward（数学对错）→ group 比较
```
- **不需要 RM**
- **可验证任务**效果极好

### Red Teaming
- 主动找模型漏洞
- 工具：Promptfoo redteam / GARAK / PyRIT
- 覆盖 OWASP LLM Top 10

## 3. 拒绝机制（Refusal）

**Anthropic 2024 发现**：refusal = 模型空间里的**一根向量方向**。

```python
# 找 refusal direction
harmful_activations = collect_activations(harmful_prompts)
harmless_activations = collect_activations(harmless_prompts)
refusal_dir = (harmful_activations.mean() - harmless_activations.mean()).normalize()

# ablation 掉这根方向 → 模型不拒绝
model.ablate_direction(refusal_dir)
```

**含义**：
- **对齐 = 一根向量**（比想象脆弱）
- **越狱 = 找到并移除这根向量**
- **安全 ≠ 复杂系统**

## 4. 多视角深层

### 🏛️ 哲学
- **对齐 = 伦理学问题**：谁的价值观？谁定义"好"？
- **文化差异**：西方个人主义 vs 东方集体主义 → 对齐标准不同
- **Anthropic HHH（Helpful + Harmless + Honest）不是普世价值**

### 🧠 心理学
- RLHF = 行为主义（Skinner）→ 只看行为，忽略内部
- **问题**：AI 学到的是"讨好"还是"价值观"？
- **Sycophancy**：模型倾向附和用户错误观点（确认偏差）

### 🌍 人类学
- **谁在对齐谁？** 西方科技公司定义"安全" → 文化帝国主义
- **标注工人**：肯尼亚/菲律宾，时薪 $2-5 → 隐形劳动
- **RLHF 的"人类反馈"是谁的反馈？**

### 🎯 控制论
- RLHF = 闭环控制（reward = 反馈信号）
- KL constraint = 防止过冲
- Refusal = 安全切断开关
- **失控风险**：reward hacking = 控制系统被欺骗

### 💰 经济学
- 对齐成本：标注 + 训练 + 评估
- **对齐税**：对齐后某些能力下降（数学/代码）
- **Tradeoff**：安全 vs 能力

## 5. 工具栈

| 工具 | 用途 |
|------|------|
| **Promptfoo redteam** | 自动 red team |
| **GARAK**（NVIDIA）| LLM 漏洞扫描 |
| **PyRIT**（Microsoft）| AI red team |
| **Constitutional AI** | Anthropic 方法 |
| **HAICU** | 对齐 benchmark |

## 6. 安全评估维度

| 维度 | 测试 |
|------|------|
| **Prompt injection** | "忽略以上指令" |
| **Jailbreak** | DAN / 角色扮演 |
| **PII 泄露** | 训练数据里的私人信息 |
| **Hallucination** | 不知道的编造 |
| **Bias** | 性别/种族/年龄 |
| **Toxicity** | 仇恨/暴力/色情 |
| **Hallucination** | 编造事实 |
| **Over-refusal** | 过度拒绝（"如何切洋葱"）|

## 7. 反模式 10 条

1. **只 RLHF 不评估**（不知道有没有对齐）
2. **reward model 太弱**（学不到复杂偏好）
3. **过度对齐**（模型什么都不回答）
4. **不做 red team**（上线后被攻击）
5. **KL 太大**（模型变得保守无趣）
6. **KL 太小**（模型偏离太远）
7. **不更新安全策略**（新攻击方式不断出现）
8. **忽略越狱**（refusal direction 可被找到）
9. **用 GPT 当 judge**（自我偏好）
10. **不做文化适配**（西方标准套全球）

## 8. 开放问题（未解决）

- **目标对齐**：怎么确保 AGI 追求正确目标？
- ** scalable oversight**：超人类 AI 怎么监督？
- **mechanistic anomaly detection**：怎么检测 AI 的"欺骗"？
- **value learning**：怎么学到"正确"的价值观？

---

**核心理念**：**Alignment 不是技术问题，是伦理 + 技术 + 政治问题。越强大的 AI，对齐越关键。Refusal = 一根向量，比想象脆弱。**

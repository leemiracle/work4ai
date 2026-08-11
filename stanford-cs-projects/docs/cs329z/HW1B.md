# CS329Z HW1 Part B: DSPy-style Framework — 声明式 Agent 重写

> **课程**: CS329Z Engineering AI Agents (Autumn 2025)
> **作业**: HW1 Part B — 用 DSPy 重构 HW1A 关键组件
> **对应模块**: W3 Frameworks · W5 Optimization (GEPA)
> **代码位置**: `topic2-agent-v2/dspy_framework.py`
> **完成度**: ★★★★☆ (核心抽象完整，mock 模式可跑)
> **最后更新**: 2026-08-11

---

## 📚 作业定位

HW1 Part B 要求学生用 **DSPy 框架** 重写 Part A 中手写的 prompt 逻辑。核心命题：**把 prompt 写作变成可编程、可优化、模型无关的声明式范式**。

DSPy（Khattab et al. ICLR 2024）的核心洞察：与其手写 prompt 然后反复微调文字，不如写 **Signature**（输入输出契约），让 Optimizer 自动生成和改进 prompt。

本实现还覆盖 **CS329Z W5 的 GEPA prompt 优化**（Agrawal 2026），实现 reflective prompt evolution。

---

## 📅 核心模块

### 1. Signature — 声明式 LLM 调用契约
```python
Signature(
    instruction="Answer the math question precisely.",
    input_fields=["question"],
    output_fields=["answer"],
)
```
- `format_prompt(**inputs)`：自动生成结构化 system prompt
- `parse_output(response)`：用正则从响应解析字段（支持 `field: value` 和 `field=value`）
- **对比 HW1A**：Part A 手写每一行 prompt，Part B 只声明输入输出 schema

### 2. Module — 可组合的 LLM 调用单元
- 封装 `Signature + LLMClient + few-shot demos`
- `forward(**inputs)`：执行一次推理（类比 PyTorch `nn.Module`）
- `add_demos()`：注入 few-shot 示例
- 支持多个 Module 串联（ChainOfThought / RAG retrieval pipeline）

### 3. BootstrapFewShot Optimizer — 自动 few-shot 生成
- 从训练集 `(input, expected)` 中跑 LLM 生成预测
- **预测正确的自动成为 demos**（InstructGPT 风格数据筛选）
- `validate(pred, expected)`：自定义验证函数决定哪些进 demo 集
- `max_demos=3`：控制 prompt 长度爆炸

### 4. GEPAOptimizer — 反思式 Prompt 进化
GEPA (Agrawal 2026)：让 LLM 反思失败并改进 instruction。
```
for round in range(3):
    跑训练集 → 记录失败样本
    让 LLM 反思失败原因
    改进 instruction（加具体性约束）
    记录 score 曲线
```
- 跟踪 `history`：每轮的 avg_score + instruction 版本
- 收敛条件：`avg_score >= 0.95` 或无失败样本

---

## 💻 项目代码

**文件**: `topic2-agent-v2/dspy_framework.py`

**运行**：
```bash
cd topic2-agent-v2
python3 dspy_framework.py
```

**输出示例**：
```
📋 1. 单次 forward
   Input: question='What is 5 + 3?'
   Output: {'answer': '8'}

📋 2. Bootstrap FewShot
   编译出 2 个 demos

📋 3. GEPA-style Prompt Evolution
   Round 0: avg_score = 0.750, failures = 1
   Round 1: avg_score = 0.750, failures = 1
```

---

## 📊 关键论文

1. 🔴 **Khattab et al. 2024** "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines" ICLR — 本作业核心框架
2. 🔴 **Agrawal et al. 2026** "GEPA: Reflective Prompt Evolution" — prompt 优化可超 RL
3. 🟡 **Opsahl-Ong et al. 2024** "MIPROv2: Optimizing Multi-Step Instructional Prompts"
4. 🟡 **Soylu et al. 2024** "Fine-Tuning + Prompt Optimization Together"
5. 🟡 **Snell et al. 2024** "Scaling LLM Test-Time Compute" ICLR 2025

---

## 🎯 学习路径建议

1. **先跑 HW1A**（理解手写 prompt 的痛苦）→ 再跑 Part B（体会抽象的价值）
2. **对比反思**：demo 第 4 部分输出 HW1A vs HW1B 的对比分析——简单 QA/分类用 DSPy，复杂 agent loop 仍需手写
3. **进阶**：接入真实 LLM → 用 MIPROv2 替换 BootstrapFewShot → 在真实 benchmark 上对比优化效果

---

## 💡 HW1A vs HW1B 对比反思

| 维度 | HW1A（手写） | HW1B（DSPy） |
|------|-------------|-------------|
| Prompt 控制 | 直接控制每一行 | 声明 signature，自动生成 |
| 复杂逻辑 | 可做 ReAct loop | 复杂控制流不如手写灵活 |
| 换模型 | 需重写 prompt | 模型无关 |
| 自动优化 | 无 | Bootstrap + GEPA 自动改进 |
| 学习曲线 | 低（直接写） | 高（学 Signature/Module/Optimizer） |

**结论**：简单 QA / 分类 → DSPy。复杂 agent → 手写。**CS329Z 的设计意图是让学生同时体验两者，理解抽象的边界**。

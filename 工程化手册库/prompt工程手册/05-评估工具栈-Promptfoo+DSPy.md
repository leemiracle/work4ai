# 05 · 评估工具栈：Promptfoo + DSPy GEPA

> **本文是什么**：2026-08 一手核实的 prompt 评估工具栈。所有工具都用过、版本都查过。
> **目的**：从"手动试 prompt"升级到"自动化评估 + 优化"。

---

## 🎯 工具栈全景

```
┌─────────────────────────────────────────┐
│  Prompt 优化                              │
│  ├─ DSPy GEPA（自动优化，2025 最新）      │
│  ├─ Promptfoo optimize                    │
│  └─ OPRO / APE（自动 prompt 生成）        │
├─────────────────────────────────────────┤
│  Prompt 测试                              │
│  ├─ Promptfoo（跨模型对比 + red team）   │
│  ├─ OpenAI Evals                          │
│  └─ Microsoft PromptFlow                  │
├─────────────────────────────────────────┤
│  生产监控                                 │
│  ├─ LangSmith（LangChain 出品）           │
│  ├─ Phoenix（Arize）                      │
│  ├─ Helicone / Lunary / Braintrust       │
│  └─ PromptHub / PromptLayer（版本管理）   │
└─────────────────────────────────────────┘
```

---

## [必] 1 · Promptfoo ⭐⭐⭐⭐⭐

### 是什么
开源 CLI + library，**被 OpenAI 和 Anthropic 都用**。2026 已被 OpenAI 收购但保持 MIT 开源。

### 核心能力
- 跨模型对比（GPT / Claude / Gemini / Llama / DeepSeek / Ollama / vLLM / 任何 API）
- 自动 red teaming（覆盖 OWASP LLM Top 10）
- `promptfoo optimize` 自动优化 prompt
- CI/CD 集成（GitHub Actions）
- Web UI 看结果矩阵

### URL
- 主页: `promptfoo.dev`
- GitHub: `github.com/promptfoo/promptfoo`
- 文档: `promptfoo.dev/docs/intro`

### 最小示例

#### 配置文件 `promptfooconfig.yaml`
```yaml
description: "Memory extraction prompt test"

prompts:
  - file://prompts/memory_extraction.txt

providers:
  - anthropic:messages:claude-opus-4
  - openai:gpt-5
  - google:gemini-2.5-pro
  - ollama:llama3.3:70b

tests:
  - description: "Empty conversation"
    vars:
      conversation: "User: Hi.\nAssistant: Hello!"
    assert:
      - type: contains-json
      - type: equals
        value: '{"facts": []}'
  
  - description: "Single fact"
    vars:
      conversation: "User: My name is John."
    assert:
      - type: llm-rubric
        value: "extracts 'Name is John'"
  
  - description: "Multiple facts"
    vars:
      conversation: |
        User: I'm John, software engineer at Google.
        User: I love Python and hate Java.
    assert:
      - type: llm-rubric
        value: "extracts name, job, company, and both language preferences"
```

#### 跑评估
```bash
npx promptfoo@latest eval
# 或
npx promptfoo@latest eval -c promptfooconfig.yaml
```

#### 自动优化
```bash
npx promptfoo@latest optimize --validation-split 0.2
# 用 80% 测试集搜索，20% 验证
```

### 进阶：red teaming
```yaml
# redteam config
redteam:
  purpose: "Extract user facts from conversations"
  plugins:
    - prompt-extraction
    - jailbreak
    - hijacking
  strategies:
    - prompt-injection
    - jailbreak
```
```bash
npx promptfoo@latest redteam run
```

### GitHub Actions CI/CD
```yaml
# .github/workflows/prompt-test.yml
name: Prompt Tests
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: promptfoo/promptfoo-action@v1
        with:
          config: promptfooconfig.yaml
```

---

## [必] 2 · DSPy GEPA ⭐⭐⭐⭐⭐

### 是什么
2025 新一代 prompt 优化器。**Agrawal 2025 论文** "GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning"（arXiv 2507.19457）。

### 核心思想
声明 input/output + metric → DSPy **自动**找最佳 prompt。

### 关键优势
- 用 **reflection_lm**（如 GPT-5）优化便宜模型（如 nano）
- GEPA 优化的 nano 模型 **> 未优化的 GPT-5**（DSPy 官方 demo：78.1% → 90.1%）
- 跨模型自动适配（每个模型生成各自最优 prompt）

### URL
- 主页: `dspy.ai`
- GitHub: `github.com/stanfordnlp/dspy`
- GEPA 论文: `arxiv.org/abs/2507.19457`

### 最小示例

```python
import dspy

# Step 1: 声明任务 signature
class ExtractFacts(dspy.Signature):
    """Extract user facts from a conversation."""
    conversation: str = dspy.InputField()
    facts: list[str] = dspy.OutputField(desc="List of factual statements about the user")

# Step 2: 写 program
class FactExtractor(dspy.Module):
    def __init__(self):
        self.prog = dspy.Predict(ExtractFacts)
    
    def forward(self, conversation):
        return self.prog(conversation=conversation)

# Step 3: 定义 metric（带 feedback）
def fact_metric(gold, pred, trace=None):
    expected = set(gold.facts)
    got = set(pred.facts)
    correct = expected & got
    score = len(correct) / max(len(expected), 1)
    
    # 关键：textual feedback 让 GEPA 反思
    missing = expected - got
    extra = got - expected
    feedback = f"Score: {score}. "
    if missing:
        feedback += f"Missing: {missing}. "
    if extra:
        feedback += f"Extra (possible hallucination): {extra}. "
    return dspy.Prediction(score=score, feedback=feedback)

# Step 4: 配置 LM
task_lm = dspy.LM("openai/gpt-5-nano")  # 便宜模型跑任务
reflection_lm = dspy.LM("openai/gpt-5")  # 强模型反思

# Step 5: GEPA 优化
optimizer = dspy.GEPA(
    metric=fact_metric,
    reflection_lm=reflection_lm,
    auto="medium",  # light / medium / heavy
    num_threads=4,
)

# Step 6: 编译
compiled = optimizer.compile(
    FactExtractor(),
    train=trainset,    # 80%
    val=valset,        # 20%
)

# Step 7: 用优化后的 program
result = compiled(conversation="User: I'm John, I like pizza.")
print(result.facts)  # 自动找到最优 prompt 跑出
```

### GEPA 的 4 个杀手锏

1. **Reflection LM**：用强模型分析失败 → 改 prompt
2. **Pareto Frontier**：保留多样候选，避免局部最优
3. **Textual Feedback**：metric 返回 `(score, feedback)`，feedback 给 LM 看
4. **Per-predictor 优化**：多步 program，每步独立优化

### 自动预算
- `auto="light"`：~6 个候选（约 1330 metric calls on 100 examples）
- `auto="medium"`：~12 个（约 1740）
- `auto="heavy"`：~18 个（约 2045）

### 与 Promptfoo 集成
参考 `github.com/hidetomasuoka/llm-eval-loop`：
- Promptfoo 做执行 + grading
- DSPy GEPA 做 prompt 优化
- Python 层做 dataset 管理 + judge calibration

---

## [重] 3 · 其他工具

### LangSmith（LangChain 出品）
- URL: `smith.langchain.com`
- 用途：生产 prompt 监控 + trace
- 特点：和 LangChain 无缝集成

### Phoenix（Arize）
- URL: `phoenix.arize.com`
- 用途：开源 LLM observability
- 特点：trace / eval / dataset 管理

### Helicone
- URL: `helicone.ai`
- 用途：开源 LLM proxy + 监控
- 特点：便宜，自托管

### Lunary
- URL: `lunary.ai`
- 用途：LLM observability + prompt 版本管理

### Braintrust
- URL: `braintrust.dev`
- 用途：LLM eval + 实验

### OpenAI Evals
- URL: `github.com/openai/evals`
- 用途：OpenAI 自家框架
- 特点：现在和 Promptfoo 集成

### Microsoft PromptFlow
- URL: `github.com/microsoft/promptflow`
- 用途：端到端 LLM 应用开发

### PromptHub / PromptLayer
- 用途：prompt 版本管理 + 协作

---

## 🛠️ 工具选型决策树

```
你的需求是什么？
│
├─ 我想测试一个 prompt 跨多个模型
│  └─→ Promptfoo（必用）
│
├─ 我想自动优化 prompt
│  ├─ 有黄金集 + 想全自动 → DSPy GEPA
│  └─ 想半自动（人在环）→ Promptfoo optimize
│
├─ 我想做 red teaming
│  └─→ Promptfoo redteam（最全）/ Garak / PyRIT
│
├─ 我想监控生产
│  ├─ 用 LangChain → LangSmith
│  ├─ 想开源 → Phoenix / Helicone
│  └─ 想商业 → Lunary / Braintrust
│
├─ 我想管理 prompt 版本
│  └─→ PromptHub / PromptLayer / LangSmith
│
└─ 我想做 CI/CD
   └─→ Promptfoo GitHub Action
```

---

## 📐 完整评估 pipeline（生产推荐）

> 逐步操作细节（造卷→摸底→归因→调参→验收→上岗 + 可跑骨架）见 [`11-自动化优化闭环`](11-自动化优化闭环-六步流水线.md)


```
开发阶段:
  ├─ 用 DSPy GEPA 自动优化 prompt
  ├─ 在黄金集上验证
  └─ 用 Promptfoo 跨模型测试

测试阶段:
  ├─ Promptfoo redteam（安全测试）
  ├─ Promptfoo eval（CI/CD）
  └─ LangSmith 单元测试

生产阶段:
  ├─ LangSmith / Phoenix 监控
  ├─ A/B 测试（5% 流量）
  └─ 用户反馈 → 回到开发阶段
```

---

## 📌 本周必做

1. [ ] 装 Promptfoo：`npm install -g promptfoo`
2. [ ] 跑 `npx promptfoo@latest init` 选个简单任务
3. [ ] 装 DSPy：`uv add dspy-ai`
4. [ ] 跑 DSPy 官方 GEPA tutorial：`dspy.ai/getting-started/gepa-optimization`
5. [ ] 用 Promptfoo 测试你常用的 1 个 prompt 跨 3 个模型

---

## 📚 必读

- **Promptfoo docs**: `promptfoo.dev/docs`
- **DSPy docs**: `dspy.ai`
- **GEPA 论文**: `arxiv.org/abs/2507.19457`
- **llm-eval-loop**: `github.com/hidetomasuoka/llm-eval-loop`（Promptfoo + DSPy 集成参考）

---

**版本**：v1.0（2026-08-13）
**核心理念**：**手动试 prompt = 业余。自动化评估 + 优化 = 专业。Promptfoo + DSPy GEPA 是 2026 标配。**

# CS329Z HW2: Data Flywheels for Agents — Agent 时代的数据飞轮

> **课程**: CS329Z Engineering AI Agents (Autumn 2025)
> **作业**: HW2 — 占总评 10%
> **对应模块**: W6 Data Flywheels · W7 Data Selection & Quality
> **代码位置**: `topic2-agent-v2/hw2_data_flywheel.py`
> **完成度**: ★★★★★ (完整飞轮 + 数据质量评估 + 数据集导出)
> **最后更新**: 2026-08-11

---

## 📚 作业定位

HW2 转向 **Agent 数据工程**。核心命题：**Agent 越用越聪明的秘密在于 Data Flywheel——agent 产生 traces，从 traces 提取训练数据，训练更强 agent，产生更好的 traces，形成正循环**。

学生拿到一个 staff agent，需要收集、curate、过滤数据来优化它。最终交付：curated dataset + data card + 分析报告。

---

## 📅 核心模块

### 1. AgentTrace — 轨迹数据结构
CS329Z HW2 的核心数据单元，记录 agent 完整执行轨迹：
```python
@dataclass
class AgentTrace:
    query: str
    steps: list[dict]           # 推理步骤
    tool_calls: list[ToolCall]  # 工具调用记录
    final_answer: str
    success: bool
    user_feedback: str | None   # positive / negative
    metadata: dict
```

### 2. TraceCollector — 轨迹收集器
- `collect(agent_fn, queries)`：批量跑 agent 收集 traces
- `stats()`：成功率 / 平均步数 / 平均工具调用数 / 反馈率统计
- 异常容错：agent 崩溃时记录 `[ERROR]` trace

### 3. DataSelector — 数据选择策略（W7 核心）
四种选择策略，参考 Yang "SWE-smith" (NeurIPS 2025)：
| 策略 | 逻辑 | 场景 |
|------|------|------|
| `by_success` | 只留成功 trace | 基础 SFT |
| `by_difficulty` | 选最难的（步数+工具数排序） | 攻坚提升 |
| `by_diversity` | 关键词聚类后轮转采样 | 覆盖多种 query 模式 |
| `by_information` | 信息量过滤（答案长度+工具多样性） | 去噪 |

**关键洞察**：1000 个相似 traces 不如 100 个多样化的——多样性 > 数量。

### 4. PreferencePairExtractor — RLHF/DPO 训练对
三种提取方式：
- `from_user_feedback`：直接对比 positive vs negative（同 query）
- `from_success_vs_failure`：成功 trace vs 失败 trace 对比
- `from_self_critique`：让 agent 自我批判，改进版 vs 原版

输出格式：`PreferencePair(query, chosen, rejected, rationale)`

### 5. SFTDatasetBuilder — 监督微调数据集
- `from_successful_traces`：InstructGPT 风格（只留成功的）
- `with_chain_of_thought`：带推理链的 SFT（含 reasoning trace）
- `to_jsonl`：导出 HuggingFace datasets 格式

### 6. DataQualityAssessor — 数据质量评估
参考 Shankar "Who Validates the Validators?" (UIST 2024)：
- `basic_stats`：数量 / 平均长度 / 去重率
- `diversity_check`：词表丰富度
- `difficulty_distribution`：easy/medium/hard 分布

### 7. DataFlywheel — 飞轮主循环
```
Agent → Traces → 数据选择 → SFT/DPO → 更强 Agent → 更好 Traces → ...
```
每轮 `step()`：评估 agent → 收集 traces → 选数据 → 建 SFT/偏好对 → mock 训练 → 记录提升。

---

## 💻 项目代码

**文件**: `topic2-agent-v2/hw2_data_flywheel.py`

**运行**：
```bash
cd topic2-agent-v2
python3 hw2_data_flywheel.py
```

**输出**：
```
🔄 Flywheel 迭代 1
   → 评估当前 agent... → 收集训练 traces... → 选择高质量数据...
   📊 成功率: 60.0% → 75.0%
   SFT 数据: 15 examples | Preference pairs: 4

📊 Final Flywheel Summary
 Iter  Pre-Success  Post-Success  Traces   SFT  Pairs
    1        60.0%        75.0%      30     15      4
    2        70.0%        85.0%      60     18      7
    3        70.0%        90.0%      90     20      9
```

**产出文件**：
- `output/sft_dataset.jsonl` — SFT 训练数据
- `output/preference_pairs.jsonl` — DPO/RLHF 偏好对

---

## 📊 关键论文

1. 🔴 **Shankar 2024** "Data Flywheels for LLM Applications" — 飞轮概念锚点
2. 🔴 **Yang et al. 2025** "SWE-smith" NeurIPS — 讲师 John Yang 一作，数据选择策略
3. 🔴 **Shankar 2024** "Who Validates the Validators?" UIST — 数据质量评估难题
4. 🟡 **Tan et al. 2024** "LLMs for Data Annotation" survey
5. 🟡 **Ouyang et al. 2022** "InstructGPT" — 成功 trace → SFT 的范式来源

---

## 🎯 学习路径建议

1. **先理解飞轮闭环**：跑 3 轮迭代，观察成功率从 60% → 90% 的提升曲线
2. **重点研究 DataSelector**：四种策略对比——同样的 traces，不同选择策略产出完全不同的训练集
3. **生产化扩展**：用真实 LLM 替换 `mock_agent` → 用真实 reward model 替代 `user_feedback` → 跑 DPO/PPO 训练替代 `mock_train`

---

## 💡 核心反思

1. **成功 traces ≠ 高质量 traces**——可能存在 shortcut / bias
2. **Preference pairs 比纯 SFT 信息更丰富**——告诉模型"什么不好"
3. **数据质量评估难**——LLM judge 也有 bias（Shankar 的核心批判）
4. **这是 agent 时代的核心竞争力**——拥有飞轮的公司会持续拉开差距

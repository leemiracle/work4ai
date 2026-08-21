# 07 — ReAct：推理 + 行动

> 「讲透 Prompt」第八篇。02-06 都在"纯思维"（CoT/SC/ToT）。本篇讲 **ReAct**——让 LLM **边推理边行动**：思考一步 → 调工具 → 看结果 → 再思考。这是所有现代 Agent 的基础范式。

---

## 1. 灵魂：推理与行动交织

$$
\boxed{\text{ReAct} = \underbrace{\text{Thought}}_{\text{推理}} \to \underbrace{\text{Action}}_{\text{调工具}} \to \underbrace{\text{Observation}}_{\text{看结果}} \to \text{Thought} \to \cdots}
$$

---

## 2. 为什么需要 ReAct

### 2.1 纯推理的局限

CoT 只用模型内部知识。但模型不知道"今天天气""最新股价""用户的数据库里有什么"——需要**外部工具**。

### 2.2 纯行动的局限

如果只调工具不推理（"查 A → 查 B → 查 C"），工具调用是僵化的，不能根据结果动态调整。

### 2.3 ReAct 的闭环

```
Thought: 用户问"北京明天会下雨吗？" 我需要查天气。
Action: search_weather("北京", "明天")
Observation: 北京明天晴，最高 35°C
Thought: 用户可能还关心防晒，我可以补充建议。
Action: respond("北京明天晴，35°C，建议防晒")
```

**关键**：每步的 Action 依赖前面的 Observation——**动态决策**。

---

## 3. ReAct 的 Prompt 模板

```
你可以使用以下工具：
- search(query): 搜索网页
- calculator(expr): 计算
- database(sql): 查数据库

按以下格式回答：

Question: {用户问题}
Thought: 我应该先...
Action: tool_name(参数)
Observation: {工具返回}
Thought: 根据结果，我接下来...
Action: ...
Observation: ...
Thought: 我现在知道答案了
Final Answer: {最终回答}
```

LLM 按这个格式生成，解析器提取 Action 调用工具，把结果塞回 Observation——循环直到 Final Answer。

---

## 4. ReAct → 现代 Agent

| 框架 | 对 ReAct 的扩展 |
|---|---|
| **LangChain Agent** | ReAct + 更多工具 + 记忆 |
| **OpenAI Function Calling** | ReAct 的标准化（JSON 格式）|
| **AutoGPT** | ReAct + 自主目标生成 |
| **Claude Computer Use** | ReAct + 屏幕操作 |

**演化**：ReAct（2022）→ Function Calling（2023）→ Agent 框架（2024）→ Computer Use（2025）。核心思想没变：**推理和行动交织**。

---

## 5. ReAct 的工程坑

### 5.1 工具描述要清晰

LLM 选哪个工具、传什么参数，完全靠**工具描述**。描述模糊 → 选错工具。

```python
# 差的描述
def search(q): ...

# 好的描述
def search(query: str) -> list:
    """搜索网页，返回相关结果。query 应为关键词，不要整句。"""
```

### 5.2 控制循环次数

ReAct 可能陷入无限循环（一直 Thought 不 Final Answer）。要设 max_iterations。

### 5.3 错误恢复

工具调用失败（网络错/参数错）时，好的 ReAct Agent 能：
- 看 Observation 里的错误信息
- Thought: "参数错了，我应该..."
- 重试或换工具

差的 Agent 会卡住或重复同样的错误。

---

## 6. 局限

- **延迟高**：每步都要调 LLM + 可能调工具，多轮很慢
- **错误累积**：早期步骤错了，后面全错（无回溯，不像 ToT）
- **token 消耗**：对话历史越来越长，成本上升

---

## 📌 下一步

[08-Prompt 安全](08-Prompt安全.md)——Prompt 越强大，越需要防御：注入攻击、越狱、信息泄漏。

## ✍️ 练习

1. 写一个 ReAct prompt，让 LLM 能"查股票价格 + 算涨跌幅 + 给建议"。模拟 3 轮 Thought-Action-Observation。
2. ReAct 和 ToT（06 章）什么关系？（提示：ReAct 是"线性推进+工具"，ToT 是"树搜索+纯思维"。能结合吗？→ Tree-of-Thought with tool use。）
3. 如果工具描述写"search(query): 搜索"，LLM 会怎么传参？写成"search(keywords): 用关键词搜索网页"呢？描述精度如何影响 Agent 质量？

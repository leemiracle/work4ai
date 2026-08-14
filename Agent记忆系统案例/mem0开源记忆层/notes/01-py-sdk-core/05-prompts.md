# 05 — Prompt 系统（`mem0/configs/prompts.py`，1062 行）

> 整个 SDK 最长的配置文件,定义了**所有 LLM 调用的 prompt 模板**。
> 这里的设计直接决定 Mem0 的"算法质量"——April 2026 benchmark +21/+27 点主要靠这里改 prompt。

---

## 1. 文件全景（按行号分段）

| 行号 | 内容 | 用途 |
|------|------|------|
| L4-L13 | `MEMORY_ANSWER_PROMPT` | 基于 memory 回答问题（chat 接口） |
| L15-L60 | `FACT_RETRIEVAL_PROMPT` | 旧版（v1.0）fact 抽取 |
| L62-L121 | `USER_MEMORY_EXTRACTION_PROMPT` | 增强 user fact 抽取 |
| L123-L174 | `AGENT_MEMORY_EXTRACTION_PROMPT` | agent fact 抽取 |
| L176-L324 | `DEFAULT_UPDATE_MEMORY_PROMPT` | 旧版 ADD/UPDATE/DELETE/NONE 决策 |
| L326-L403 | `PROCEDURAL_MEMORY_SYSTEM_PROMPT` | procedural memory 总结 |
| L406-L460 | `get_update_memory_messages()` | 构造旧版 update prompt |
| L468-L944 | ⭐ **`ADDITIVE_EXTRACTION_PROMPT`** | v1.1+ 核心,ADD-only |
| L947-L957 | `AGENT_CONTEXT_SUFFIX` | agent 视角附加（拼到上面） |
| L965-L1062 | `generate_additive_extraction_prompt()` | v3 prompt builder |

---

## 2. ⭐ `ADDITIVE_EXTRACTION_PROMPT`（v3 核心算法）

L468-L944,**476 行**,是 Mem0 当前的核心算法 prompt。结构如下：

```
# ROLE
（Memory Extractor,只做 ADD 操作）

# INPUTS
## New Messages          — 当前 turn 的对话
## Summary               — 用户 profile 摘要（可空）
## Recently Extracted Memories  — 本 session 最近抽的（最多 20）→ 去重
## Existing Memories     — 系统已有相关 memory（top 10）→ 不重复抽 + linking
## Last k Messages       — 最近 20 条 → 解析代词
## Observation Date      — 对话发生日期（关键！时间锚点）
## Current Date          — 系统今天日期（不用于解析时间）
## Optional Inputs       — includes/excludes/custom_instructions/feedback_str

# GUIDELINES
## What to Extract       — 从 user + assistant 都抽
### Casual Topics Are Still Extractable
### Extract Incidental Facts, Not Just Requests
### Shared Photos and Images
## Memory Quality Standards
### Contextually Rich, Not Atomic    — "User has a dog named Poppy..." > "User has a dog"
### Clean Factual Statements
### Self-Contained                   — 替换代词
### Concise but Complete (15-80 words)
### Temporally Grounded              — 相对→绝对（用 Observation Date）
### Numerically Precise              — "416 pages" 不写 "about 400"
### Preserve Specific Details        — proper noun 不泛化
### Meaning-Preserving               — 防 misinterpretation

## Integrity Rules
- No Fabrication
- No Implicit Attribute Inference（不从名字推性别）
- Correct Attribution
- No Echo Extraction（不重抽 assistant 对 user 的复述）
- No Within-Response Duplication
- No Meta-Extraction（抽内容,不抽动作）
- No Detail Contamination from Context

## Memory Linking
（什么情况下加 linked_memory_ids）

# EXAMPLES
（12 个精心设计的示例：multi-topic / assistant rec / nothing / dedup / linking /...）

# CRITICAL: Exhaustive Extraction Checklist
（输出前的自检清单）

# OUTPUT FORMAT
{
  "memory": [
    {"id": "0", "text": "...", "attributed_to": "user", "linked_memory_ids": ["uuid"]}
  ]
}
```

### 关键设计点

| 设计 | 为什么 |
|------|-------|
| `Observation Date` vs `Current Date` 分开 | "User went to Paris last week" 在 6 个月后是无用的；必须 ground 到对话发生的日期 |
| `Recently Extracted Memories` (top 20) | 同 session 内的 dedup（不是跨 session） |
| `Existing Memories` (top 10) | 跨 session 的 dedup + linking |
| `linked_memory_ids` | 抽出来的新 memory 引用已有 memory 的 UUID → 形成 graph |
| `attributed_to: "user"/"assistant"` | 区分谁说的（user 说的比 assistant 的复述更可信） |
| 12 个 examples | 多 topic / 多 speaker / 文档分享 / 结构化数据 / 时间模糊 / 情绪... |
| "When in doubt, extract" | 防 LLM 偷懒,宁多勿少（hash dedup 兜底） |
| "First topic dominance" 警告 | 防 LLM 只抽第一个 topic,漏后面 |

---

## 3. ⭐ `generate_additive_extraction_prompt()` 函数

L1016-L1062,prompt builder：

```python
def generate_additive_extraction_prompt(
    summary=None,
    recently_extracted_memories=None,
    existing_memories=None,
    new_messages=None,
    *,
    last_k_messages=None,
    current_date=None,
    timestamp=None,
    custom_instructions=None,
    use_input_language=False,
):
    current_date, observation_date = _resolve_dates(current_date, timestamp)

    sections = []
    sections.append(f"## Summary\n{_format_summary(summary)}")
    sections.append(f"## Last k Messages\n{_format_conversation_history(last_k_messages)}")
    sections.append(f"## Recently Extracted Memories\n{_serialize_memories(recently_extracted_memories)}")
    sections.append(f"## Existing Memories\n{_serialize_memories(existing_memories)}")
    sections.append(f"## New Messages\n{_format_new_messages(new_messages)}")
    sections.append(f"## Observation Date\n{observation_date}")
    sections.append(f"## Current Date\n{current_date}")

    if custom_instructions:
        sections.append(f"## Custom Instructions\n{custom_instructions}")

    if use_input_language:
        sections.append("## Language Requirement\nCRITICAL: Respond in the SAME LANGUAGE...")

    sections.append("# Output:")
    return "\n\n".join(sections)
```

### 辅助函数（L968-L1013）

```python
PAST_MESSAGE_TRUNCATION_LIMIT = 300   # 历史消息每条最多 300 字符 + "..."

def _truncate_content(text, limit=300): ...
def _format_summary(summary): ...           # 支持 dict 或 str
def _format_conversation_history(messages): # 格式化为 "role: content\n"
def _serialize_memories(memories):          # JSON 序列化,默认 []
def _format_new_messages(new_messages):     # str 透传,其他 JSON 化
def _resolve_dates(current_date, observation_date):
    """两个日期都默认 today,observation 缺失时跟 current 一致"""
```

> **关键**：`last_k_messages` 每条 truncate 到 300 字符——防止单条超长消息吃掉 token budget。

---

## 4. add() 怎么调用 prompt

`mem0/memory/main.py` L911-L957（精简版）：

```python
# Phase 0: 拿最近 10 条 session 消息（SQLite）
last_messages = self.db.get_last_messages(session_scope, limit=10)

# Phase 1: 搜已有 memory（top 10）→ UUID→int mapping
existing_results = self.vector_store.search(query=parsed_messages, vectors=..., top_k=10, filters=...)
existing_memories = [{"id": str(idx), "text": mem.payload.get("data", "")} for idx, mem in enumerate(...)]

# Phase 2: 构造 prompt + 调 LLM
system_prompt = ADDITIVE_EXTRACTION_PROMPT
if is_agent_scoped:
    system_prompt += AGENT_CONTEXT_SUFFIX

user_prompt = generate_additive_extraction_prompt(
    existing_memories=existing_memories,
    new_messages=parsed_messages,
    last_k_messages=last_messages,
    custom_instructions=custom_instr,
)

response = self.llm.generate_response(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    response_format={"type": "json_object"},   # ⭐ 强制 JSON 输出
)
```

### 注意

- `summary` 和 `recently_extracted_memories` 在 OSS 调用时**没传**（看上面 Phase 2 的参数,只传了 existing/new/last_k/custom_instructions）
- 这两个参数 Platform 才有完整支持
- OSS 的 dedup 主要靠 `existing_memories`（vector search top 10）+ hash 去重

---

## 5. 旧 prompt（`FACT_RETRIEVAL_PROMPT` 等）

L15-L174 三个 prompt 是 v1.0 算法的产物,**当前 v1.1+ 不再使用**（但保留在文件里）：

| Prompt | 何时用 |
|--------|-------|
| `FACT_RETRIEVAL_PROMPT` | v1.0 单一 fact 抽取（user/assistant 不分） |
| `USER_MEMORY_EXTRACTION_PROMPT` | v1.0 user-only 抽取（强化"Don't include assistant"） |
| `AGENT_MEMORY_EXTRACTION_PROMPT` | v1.0 agent-only 抽取 |
| `DEFAULT_UPDATE_MEMORY_PROMPT` | v1.0 ADD/UPDATE/DELETE/NONE 决策（多次 LLM 调用） |
| `get_update_memory_messages()` | v1.0 update prompt 构造器 |

> 在 `mem0/memory/main.py` 顶部 import 还能看到它们（`from mem0.configs.prompts import ...`）,但 add() 主路径已经走 `ADDITIVE_EXTRACTION_PROMPT`。可能是 procedural memory 或向后兼容路径还在用。

---

## 6. `PROCEDURAL_MEMORY_SYSTEM_PROMPT`

L326-L403,procedural memory 专用。**procedural memory** = "agent 应该怎么做"的元知识,不是用户的事实。

调用路径：`Memory.add(memory_type=MemoryType.PROCEDURAL.value, agent_id="...")` → `_create_procedural_memory()` → 用这个 prompt。

prompt 让 LLM 把 agent 的执行历史总结成"任务目标 + 编号步骤 + 每步的动作 + 结果 + 上下文"。典型用例：browser agent 跑了 N 步,把过程总结成 procedural memory 供下次复用。

---

## 7. `AGENT_CONTEXT_SUFFIX`

L947-L957,**追加**到 `ADDITIVE_EXTRACTION_PROMPT` 后面（仅 agent scoped 调用时）：

```python
## Entity Context

The primary entity is an AI agent. Frame memories from the agent's perspective:
- For user-stated facts, frame as agent knowledge: "Agent was informed that [fact]"
- For agent actions, use direct statements: "Agent recommended [X]"
- For agent configuration, capture directly: "Agent is configured to [behavior]"

The attributed_to field should still reflect the original source.
```

> 把视角从"User"切到"Agent"。比如 `add(messages, agent_id="a1")` 时,user 说"我喜欢猫"会被抽成 "Agent was informed that the user likes cats",而不是 "User likes cats"。

---

## 8. 关键 prompt 工程 lesson

### Lesson 1：观察日期 vs 当前日期分离

```python
# 错（v1.0）
"Today's date is {datetime.now()}"   # 直接用今天

# 对（v1.1+）
"## Observation Date\n{observation_date}\n## Current Date\n{current_date}"
```

LLM 容易用 current date 解析"yesterday",但历史对话里"yesterday"应该指对话发生时。

### Lesson 2：12 个 diverse examples > 100 行规则

`ADDITIVE_EXTRACTION_PROMPT` 用 examples 覆盖：
- multi-topic（example 1）
- assistant recommendations（example 2）
- nothing to extract（example 3）
- dedup（example 5）
- multi-dimension（example 6）
- 时间模糊（example 7）
- 文档/参考资料抽取（example 8）
- 结构化数据（example 9）
- memory linking（example 10）
- 长 multi-topic（example 11）
- multi-speaker（example 12）

**每个 example 都讲一个具体 lesson**,比抽象规则有效得多。

### Lesson 3：输出格式严格约束

```
Return ONLY valid JSON parsable by json.loads(). No text, reasoning, explanations, or wrappers.

{
  "memory": [
    {"id": "0", "text": "...", "attributed_to": "user", "linked_memory_ids": [...]}
  ]
}
```

加 `response_format={"type": "json_object"}` 在 OpenAI 调用侧强制 JSON 模式（Provider 支持的话）。

### Lesson 4：自检清单（Crimson Checklist）

prompt 结尾加一段"输出前自检":

> Before producing output, mentally scan the ENTIRE conversation — every single message — and verify:
> 1. Have you extracted at least one memory from every distinct topic?
> 2. Have you extracted facts from messages in the MIDDLE and END, not just the beginning?
> 3. For conversations with 10+ messages, you should typically extract 5-15 memories.

强制 LLM 反思,**显著降低"first topic dominance"失败模式**。

### Lesson 5：明确"do"和"don't"

prompt 反复用"Do NOT" + "RIGHT/WRONG"对照：

```
- WRONG: "Assistant created a D&D adventure with enemies"
- RIGHT: "The Lost Temple of the Djinn adventure includes 4 Mummies (AC 11, 45 HP)..."
```

比抽象说"be specific"有效得多。

---

## 9. 一个常见误解

很多人以为 Mem0 的算法是"用 LLM 把对话变 facts"。**对了一半**。

实际是：
1. **LLM 抽 facts**（用 `ADDITIVE_EXTRACTION_PROMPT`）→ 输出 JSON list
2. **hash 去重**（md5(text),Python 算,不用 LLM）
3. **embed**（每条 fact 算向量）
4. **insert vector store**（持久化）
5. **entity 抽取 + linking**（用 spaCy / 外部 NER,不用 LLM）

prompt 只是 step 1。其他 4 步是确定性算法。

---

## 10. prompt 改进流程

April 2026 算法升级 = 重写 prompt + 加 entity linking + 加 BM25 + remove graph memory。

`prompts.py` 文件注释（L464-L466）：

```python
# ---------------------------------------------------------------------------
# V3 Additive Extraction Prompt (ADD-only with memory linking)
# Ported from platform/backend/shared/core/config/prompts.py
# ---------------------------------------------------------------------------
```

**"Ported from platform"**——OSS 是从 Platform 反向移植的。Platform 才是算法主战场,OSS 是公开版。

---

## 11. 接下来

| 想看 | 去哪 |
|------|------|
| add() 完整 pipeline（怎么调 prompt） | [`06-add-pipeline.md`](./06-add-pipeline.md) |
| entity linking 怎么工作 | [`06-add-pipeline.md`](./06-add-pipeline.md)（Phase 7 段） |
| Memory 类整体 | [`02-memory-main.md`](./02-memory-main.md) |

---

📌 **下一步** → [`02-memory-main.md`](./02-memory-main.md) `Memory` 类顶层结构（3851 行核心引擎的导航）。

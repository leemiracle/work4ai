# 03 · AI4Code — AI 写代码

> 代码是 AI 最先成熟的领域——因为代码本身就是 LLM 的"母语"（结构化、有明确对错、海量训练数据）。Copilot 让开发者效率提 30-50%，Cursor/Devin 在 2024-2025 把 IDE 变成 Agent。本章讲清楚：**从"补全"到"Agent 化 IDE"的范式转移、上下文工程的核心、代码评估为什么难**。
>
> 配套：[`讲透公开课/03-AI Infra`](<../讲透公开课/03-AI Infra 源码导读清单.md>)（你正在用的就是 AI4Code 的产物）

---

## 一、三级演进：补全 → 编辑 → Agent

### 1.1 第一级：补全（Copilot 1.0，2021）

- GitHub Copilot（基于 OpenAI Codex）：**当前光标位置 → 预测后续代码**
- 输入：当前文件 + 少量上下文
- 输出：单行/几行补全
- 价值：减少打字，但**不理解你的意图**

### 1.2 第二级：编辑（Cursor / Copilot Chat，2023-2024）

- **自然语言指令 → 修改多行/多文件**
- "把这个函数改成异步的"、"加个错误处理"
- 上下文：当前选区 + 对话历史 + 可手动 @ 文件
- 价值：理解局部意图，但仍局限在你显式给的上下文

### 1.3 第三级：Agent（Devin / Cursor Agent / Cline，2024-2025）

- **自然语言目标 → 自主规划 + 执行 + 验证**
- "帮我实现 issue #123" → Agent 读 issue、查代码、改文件、跑测试、提 PR
- 上下文：**自主检索整个 codebase** + 工具调用（git/终端/浏览器）
- 价值：自主完成任务，但有失败模式（幻觉改动、死循环）

> 🎯 **范式转移**：补全 = 被动打字员；编辑 = 副驾驶；**Agent = 实习生**。每一级，AI 的"自主性"和"上下文范围"都上一个台阶。

---

## 二、上下文工程：AI4Code 的真正护城河

模型层（GPT-4 / Claude / Sonnet）越来越同质化。**AI4Code 的差异在上下文工程**——怎么把"对的代码"喂给模型。

### 2.1 上下文从哪来

| 源 | 用途 | 难点 |
|----|------|------|
| 当前文件 | 主上下文 | 长文件截断 |
| LSP（语言服务器）| 跳转/补全/类型 | 跨文件依赖图 |
| 检索（embeddings）| 找相关代码 | 检索精度 + 排序 |
| Git 历史 | 理解演进 | 噪声多 |
| 错误信息 / 测试输出 | 反馈循环 | 长度爆炸 |

### 2.2 Cursor / Windsurf 的关键创新

- **Codebase indexing**：整个仓库建 embedding 索引，按相关性检索
- **@-mention**：手动指定文件/docs，精确控制上下文
- **Tool use**：让模型主动调 grep / find / read_file，自主找信息
- **Multi-file edit**：一次指令改多个文件，保持一致性

### 2.3 长上下文 ≠ 上下文工程

GPT-4 / Gemini 的 128k-2M 上下文窗口让人以为"塞进去就行"，但：
- **Lost in the middle**：长上下文中间的信息模型容易忽略
- **精度下降**：上下文越长，关键细节越容易被稀释
- **成本**：长上下文推理贵且慢

> 🔑 真正的工程是**用检索 + 工具调用动态构造最小且精确的上下文**，不是堆窗口大小。

---

## 三、评估演进：从 HumanEval 到真实 PR

代码生成评估，从玩具到真实，经历了三跳：

| Benchmark | 任务 | 局限 |
|-----------|------|------|
| **HumanEval**（2021）| 164 个函数级问题，单次生成 + 单元测试 | 太简单，玩具级 |
| **MBPP**（2022）| 974 个基础 Python 题 | 同样函数级 |
| **SWE-bench**（2023-10）| **真实 GitHub issue + 真实 PR + 真实测试** | 困难，最好模型 ~20-40% |
| **SWE-bench Verified**（2024）| 人工筛选的 500 题，更可靠 | 当前 Agent 主战场 |
| **LiveCodeBench**（2024）| 持续更新，防止数据污染 | 竞赛题为主 |

**SWE-bench 的意义**：第一次让"AI 能不能解真实软件工程问题"变得可量化。2024-2025 所有 AI4Code 系统（Devin/Cursor/Claude Sonnet）都在刷这个榜。

---

## 四、Agent IDE 三巨头（2025 现状）

| 产品 | 定位 | 特点 |
|------|------|------|
| **Cursor** | AI-first IDE（VS Code fork） | 上下文工程最强，主流开发者用 |
| **Devin**（Cognition）| 自主软件工程师 | SWE-bench SOTA，可执行长任务 |
| **Cline / Windsurf / Claude Code** | 开源 / IDE 内 Agent | 工具调用 + 多步规划 |

**共同架构**（2025 共识）：
```
用户目标
   ↓
规划器（Plan，LLM）
   ↓
工具调用循环（Act）：
   ├─ read_file / grep / glob
   ├─ edit_file / run_command
   ├─ browse_web（查文档）
   └─ submit_pr
   ↓
验证器（Observe，LLM 或测试）
   ↓ 失败则重规划
```

这就是 **ReAct / Plan-and-Execute** 范式在 IDE 的落地。详见 [`讲透Agent`](../讲透Agent/)。

---

## 五、深入：上下文工程实战 + Agent 的 plan-execute-verify

### 5.1 Copilot 的 FIM 训练（Fill-in-the-Middle）

代码模型的核心训练技巧是 **FIM**（Fill-in-the-Middle）：让模型学会"给定前后文，填中间"。

```
原始代码：    def add(a, b):  return a + b
标准训练：    输入 "def add(a, b):"  → 预测 "return a + b"  （只前缀）
FIM 训练：    输入 "<prefix>def add(a, b):\n<suffix>  # 这里返回和\n<middle>"
             → 预测 "  return a + b"  （中间填空）
```

**为什么关键**：IDE 里光标在代码**中间**，不是末尾——纯前缀训练的模型不会"向左看"。FIM 训练让模型同时利用前后文，**这是 Copilot 能用的根本**。

Codex（2021）/ Code Llama / DeepSeek-Coder / Qwen-Coder 全用 FIM 训练，比例通常 50%-90%。

### 5.2 Codebase indexing 实战

Cursor / Windsurf 的"读整个仓库"靠 **embedding 检索**：

```
建索引（一次性）：
  遍历所有 .py/.ts/.md 文件
  → 按语义分块（函数/类边界，~100-500 tokens/块）
  → 用 code embedding 模型编码
  → 存进本地向量库（Chroma/LanceDB）

查询时：
  用户问 "X 功能在哪实现"
  → embed(query) → 向量库 top-k 检索
  → rerank（cross-encoder）→ 取最相关 3-10 块
  → 塞进 LLM 上下文
```

**关键选型**：
- **embedding 模型**：`voyage-code-2` / `bge-large` / `text-embedding-3-large`——专门 code 的比通用的好
- **分块策略**：**按 AST 分**（函数/类边界）比固定长度好——保持语义完整
- **rerank**：必做——初次检索召回多，rerank 提精度

### 5.3 Agent 的 plan-execute-verify（IDE 落地）

Cursor Agent / Devin 内部的核心循环：

```
用户目标（"修复 issue #123"）
    ↓
【Plan】LLM 拆解任务：
    1. 读 issue 理解问题
    2. grep 找相关代码
    3. 定位 bug
    4. 改代码
    5. 跑测试验证
    6. 提 PR
    ↓
【Execute】逐步执行，每步：
    - 选工具（read_file / grep / edit / run）
    - 调工具，拿结果
    - 把结果加进上下文
    ↓
【Verify】每步后：
    - LLM 自检："这步做对了吗？"
    - 或客观验证（测试通过？编译成功？）
    ↓ 失败则回退 / 重新 plan
```

**关键工程**：
- **工具 schema 严格**：每个工具有明确参数 + 校验，防止 LLM 瞎调
- **上下文压缩**：长任务时，把旧步骤总结，腾出 context window
- **checkpoint**：每步存状态，崩溃可恢复
- **human approval**：高风险操作（push、删文件）必须人确认

> 🎯 **现实**：当前 Agent 在 SWE-bench Verified 上 ~30-50%——**能用但不稳**。复杂任务经常崩溃，需要人介入。所以产品形态是"**副驾驶 + 频繁确认**"，不是"甩手掌柜"。

---

## 六、挑战与开放问题

1. **长任务的可靠性**：Agent 跑 30 步后经常崩溃（错误累积）
2. **大型 codebase 的导航**：百万行代码的依赖理解，RAG 不够
3. **跨语言 / 跨范式**：从 Python 到 Rust 到 SQL 的迁移
4. **调试**：AI 能写代码，但**调试自己写的代码**仍然难（要"反事实推理"）
5. **代码 + 业务理解**：AI 不懂"为什么要这么改"——业务上下文缺失

---

## 六、一句话总结

> 🎯 **三句话**：
> 1. AI4Code 三级跳：补全（被动）→ 编辑（副驾驶）→ **Agent（实习生）**——每一级自主性 + 上下文范围都上一个台阶。
> 2. 真正的护城河不是模型，是**上下文工程**（检索 + 工具 + 多文件）。
> 3. 评估从 HumanEval（玩具）到 SWE-bench（真实 PR）——Agent IDE 主战场。

📌 **下一步**：进入 [04 AI4Medicine](./04-AI4Medicine.md)，看 AI 怎么在错误代价最高的领域落地。

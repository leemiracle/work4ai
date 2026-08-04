# 00 · AI for Software Engineering 是什么

> **第一性问题**：编程是 AI 应用最成熟的领域之一——但**软件工程**远不止写代码（需求 / 设计 / 测试 / 维护）。AI 改变了**整个软件生命周期**。
>
> 与 [`讲透AI应用全景/03-AI4Code`](../../讲透AI应用全景/03-AI4Code.md) 不同：前者讲"代码生成"，本篇问"**软件工程的 AI 化**"。
>
> 配套：[`讲透AI应用全景/03-AI4Code`](../../讲透AI应用全景/03-AI4Code.md) + [`讲透Prompt`](../../讲透Prompt/) + [`讲透Agent`](../../讲透Agent/)

---

## 一、软件工程为什么需要 AI

### 1.1 软件成本爆炸

- 全球软件开发：**$500B+/年**
- 程序员生产力瓶颈
- **AI 可能让效率 +50%**（GitHub 2022 Copilot 研究）

### 1.2 复杂度爆炸

- 单个系统 1000 万+ 行
- 微服务 / 分布式 / 云原生
- 人脑跟不上

### 1.3 维护成本

- 80% 软件成本在维护
- 历史代码难懂
- **AI 理解整个 codebase**

---

## 二、AI 在软件工程的六大应用

### 2.1 代码生成（Code Generation）

- **GitHub Copilot**（2021，OpenAI Codex）：50% 代码 AI 写
- **Cursor**（2023，VS Code fork）：原生 AI IDE
- **Claude Code / Devin**（2024）：完整软件工程师 Agent
- **代表 SWE-bench**（2024 benchmark）

详见 [`讲透AI应用全景/03-AI4Code`](../../讲透AI应用全景/03-AI4Code.md)。

### 2.2 代码理解 + 导航

- **LLM 理解整个 codebase**
- "这个函数干嘛的？" "找所有调用方"
- **Cursor / Continue / Sourcegraph Cody**

### 2.3 测试自动化

- **自动生成单元测试**（Diffblue / Codium）
- **fuzz testing** + AI
- **端到端测试生成**（Testim / Mabl）

### 2.4 代码审查（Code Review）

- **LLM 自动 PR 审查**
- 找 bug / 安全漏洞 / 性能问题
- **CodeRabbit / Graphite / Greptile**

### 2.5 DevOps + AIOps

- **日志异常检测**
- **故障预测**
- **自动 incident response**（Rootly / Resolve AI）

### 2.6 需求 + 设计

- LLM 从需求文档生成 spec
- UML / 架构图生成
- **早期但前景**

---

## 三、软件工程专属的方法学

### 3.1 上下文工程

- LLM 单次调用不够
- **RAG over codebase**（向量数据库 + 代码）
- 详见 [`讲透RAG`](../../讲透RAG/)。

### 3.2 Agent 化

- **多步任务**：写 + 测 + 修
- **工具调用**：浏览器 / shell / git
- 详见 [`讲透Agent`](../../讲透Agent/)。

### 3.3 评估 benchmark

- **SWE-bench**（2023）：真实 GitHub issue 修复
- **HumanEval / MBPP**：函数级
- **LiveCodeBench**：动态避免污染

### 3.4 安全 + 隐私

- 代码是 IP
- **本地 LLM**（Ollama / LM Studio）
- **企业版**（GitHub Copilot Enterprise）

---

## 四、当前前沿（2024-2026）

### 4.1 Devin（Cognition 2024）

- "第一个 AI 软件工程师"
- 完整 software 生命周期
- SWE-bench ~13%（2024 起）

### 4.2 SWE-bench 突破

- 2024：~20-40%（开源）
- 2026 目标：~80%（接近人类）

### 4.3 AI 原生 IDE

- **Cursor / Windsurf / Zed**
- 嵌入式 LLM
- **替代 VS Code** 部分场景

### 4.4 多 Agent 协作

- **CrewAI / AutoGen / LangGraph**
- 多个 AI agent 写大型软件
- 详见 [`讲透Agent`](../../讲透Agent/)。

### 4.5 编程教育变革

- 大学允许 Copilot（部分）
- 新课程：**prompt engineering / AI 协作**
- 详见 [`讲透AIfor各学科/教育`](../教育/)。

---

## 五、AI 改变了软件工程的什么

### 5.1 程序员角色

- **写代码 → 审代码**
- 工程师生产力 +50%（GitHub 研究）
- 初级 vs 高级：差距缩小还是扩大？

### 5.2 软件成本

- 开发成本可能降 30-50%
- **新商业模式**（更多软件可行）

### 5.3 软件质量

- AI 减少 bug？
- 或制造更多？
- **开放问题**

### 5.4 软件工程教育

- 算法 / 数据结构仍有用
- 但**新技能**：AI 协作 / 提问 / 评审
- 详见 [`讲透AIfor各学科/教育`](../教育/)。

---

## 六、开放问题

1. **AI 能替代程序员吗**？哪些工作安全？
2. **AI 生成的代码可靠吗**？
3. **AI 让软件质量提升还是下降**？
4. **编程教育怎么改**？
5. **软件工程伦理**：AI 写的代码出 bug 谁负责？

---

## 七、一句话总结

> 🎯 **四句话**：
> 1. **AI 改变整个软件生命周期**——从需求到维护。
> 2. **六大应用**：代码生成 / 理解 / 测试 / 审查 / DevOps / 需求设计。
> 3. **代表系统**：Copilot / Cursor / Devin / SWE-bench。
> 4. **程序员角色重塑**：写→审，**生产力 +50%**，但**质量 / 教育 / 伦理**待解决。

---

📌 **下一步**

1. **读**：GitHub Copilot 2022 / SWE-bench / Devin。
2. **和 [`讲透Agent`](../../讲透Agent/) + [`讲透Prompt`](../../讲透Prompt/) 对照**。
3. **进入 [01 Devin 深挖](./)**（待补）。

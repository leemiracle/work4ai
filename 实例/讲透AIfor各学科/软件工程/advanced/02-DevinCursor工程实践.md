# 软件工程 · Devin / Cursor 工程实践

> **博士级**：AI 软件工程师的工程实践 + 商业模式。

## 一、产品图谱

### 1.1 AI IDE

| 产品 | 公司 | 特点 |
|---|---|---|
| **Cursor** | Anysphere | VS Code fork，原生 AI |
| **Windsurf** | Codeium | Cursor 竞品 |
| **Zed** | Zed Industries | 高性能 Rust |
| **Continue** | 开源 | VS Code / JetBrains 插件 |

### 1.2 AI Agent

| 产品 | 公司 | 特点 |
|---|---|---|
| **Devin** | Cognition | 第一个"AI 软件工程师" |
| **OpenHands** | 开源 | Devin 替代 |
| **GitHub Copilot Workspace** | GitHub | 端到端 |
| **Amazon Q Developer** | AWS | 云集成 |

### 1.3 代码审查

- **CodeRabbit**：自动 PR review
- **Graphite / Greptile**
- **Gemini Code Assist**

## 二、Cursor 的成功（2024）

### 2.1 核心创新

- **Tab 补全**：Claude/GPT 驱动
- **Cmd-K**：选代码 + 改
- **代码库理解**：embedding + RAG
- **多模型**：Claude 3.5 / GPT-4 / 自研

### 2.2 商业模式

- $20/月 Pro
- $40/月 Business
- **估值 $2.6B**（2024）
- 增长极快

### 2.3 用户

- 大量开发者
- 公司采用（Anthropic / OpenAI 内部用）

## 三、Devin 的争议

### 3.1 2024.3 发布

- Cognition 宣称"第一个 AI 软件工程师"
- Demo 视频惊艳
- **估值 $2B**

### 3.2 争议

- **演示 vs 实际**：SWE-bench ~13%
- **夸大宣传**质疑
- **复现困难**

### 3.3 当前状态

- 持续改进
- 但仍远不能替代人类
- **辅助工具**

## 四、OpenHands（开源）

### 4.1 OpenDevin → OpenHands

- 开源 Devin 替代
- 社区驱动
- **MIT 协议**

### 4.2 架构

- LangGraph 风格
- 多 Agent
- 工具调用

## 五、企业采用

### 5.1 大公司

- **Google / Meta / Microsoft**：内部 AI 工具
- **Anthropic / OpenAI**：用 Cursor
- **Apple**：自研

### 5.2 创业公司

- 全员用 Cursor / GitHub Copilot
- 初级工程师 + AI
- **新工作流**

### 5.3 非科技公司

- 银行 / 医院 / 政府
- 谨慎采用
- **安全 + 合规**

## 六、生产力证据

### 6.1 GitHub Copilot 研究（2022）

- **55%** 开发者**更快**完成任务
- 46% 代码 AI 写
- 74% 更专注

### 6.2 反对证据

- **2023 METR 研究**：实际项目提升 < 20%
- 复杂任务 AI 帮不上
- **学习曲线**

### 6.3 代码质量

- AI 代码**更多 bug**？
- 或**更少**（自动 review）？
- **争议**

## 七、未来方向

### 7.1 多 Agent 协作

- CrewAI / AutoGen / LangGraph
- 多个角色协作写大软件

### 7.2 自然语言编程

- 完全用自然语言描述
- AI 实现细节
- **降低门槛**

### 7.3 持续学习

- AI 记住项目历史
- **个性化**

### 7.4 跨语言 / 跨平台

- 一个 AI 解所有语言
- Web / Mobile / Cloud

## 八、博士级练习

1. 试用 Cursor + Devin（免费层）
2. 分析 SWE-bench leaderboard
3. 评估代码质量（自动 + 人工）

## 关键引用

- GitHub Copilot 2022 研究
- Cognition Devin blog
- Anysphere Cursor blog
- METR 2023 评估

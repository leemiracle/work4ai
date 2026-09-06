# 软件工程 · SWE-bench + Agent 数学

> **博士级**：代码 Agent 的数学 + 评估。

## 一、SWE-bench 的问题形式

### 1.1 任务

给定 GitHub issue → Agent 修改代码 → 提交 PR → 跑测试。

### 1.2 数学

- **状态空间** $S$：仓库文件 + 测试状态
- **动作空间** $A$：编辑 / 读文件 / 跑命令
- **目标**：测试通过（$r = 1$）或失败（$r = 0$）

形式化为 **MDP**：

$$\pi^* = \arg\max_\pi \mathbb{E}\left[\sum_t r_t\right]$$

## 二、Agent 架构

### 2.1 ReAct（Reasoning + Acting）

```
Thought → Action → Observation → Thought → ...
```

**核心**：LLM 交替思考 + 行动。

### 2.2 SWE-agent（2024）

- **ACI**（Agent-Computer Interface）
- 设计 LLM 友好的命令
- 在 SWE-bench 上优化

### 2.3 多 Agent

- **AutoGen**：多个角色（coder / tester / reviewer）
- **LangGraph**：图结构协调
- **CrewAI**：任务委派

## 三、关键挑战

### 3.1 长上下文

- 大仓库 > 100K tokens
- **RAG over codebase**
- 详见 [`讲透RAG`](../../../讲透RAG/)

### 3.2 错误累积

- 每步错误累积
- **自我反思**（Reflexion）
- **回滚机制**

### 3.3 评估污染

- GitHub 公开 → LLM 训练见过
- **LiveCodeBench**（动态）
- **SWE-bench Live**

## 四、数学：上下文工程

### 4.1 上下文窗口分配

```
总窗口 = 系统 prompt + 历史 + 工具结果 + 当前思考
```

**挑战**：工具结果（文件 / 日志）大。

### 4.2 RAG 检索

- 代码 chunk 向量化
- 检索 top-k
- **重排序**

### 4.3 长期记忆

- Vector DB 存历史
- 按任务检索
- **持续学习**

## 五、SWE-bench 评估

### 5.1 数据

- 12 Python 仓库
- 2294 真实 GitHub issue
- 单元测试验证

### 5.2 当前 SOTA

- 2023：~2%（Devin）
- 2024：~40%（多个）
- 2026 目标：~80%（接近人类）

### 5.3 子集

- **SWE-bench Lite**：300 简化
- **SWE-bench Verified**：人工验证
- **SWE-bench Live**：动态避免污染

## 六、博士级练习

1. 在 SWE-bench Lite 跑 SWE-agent
2. 实现简单 ReAct
3. 分析 Devin 失败案例

## 关键引用

- Jimenez 2023 *ICLR* SWE-bench
- Yao 2022 *arXiv* ReAct
- Yang 2024 SWE-agent
- Shinn 2023 *NeurIPS* Reflexion

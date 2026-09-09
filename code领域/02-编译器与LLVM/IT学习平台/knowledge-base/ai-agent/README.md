# AI智能体系统

> 由多个AI智能体组成的自主协作系统，系统化提升个人能力

---

## 系统架构

```
┌─────────────────────────────────────────────────────┐
│         AI智能体协调器               │
│  (Orchestrator)                    │
└───────────────┬────────────────────────┘
                │
        ┌───────────┼───────────┐
        │           │           │
   ┌──┴─┐  ┌──┴─┐  ┌──┴─┐  ┌──┴─┐  ┌──┴─┐
   │    │  │    │  │    │  │
   │训练器│  │分析器│  │研究者│  │规划器│  │执行器│
   │    │  │    │  │    │  │
   └────┴┘  └────┴┘  └────┴┘  └────┴┘  └────┘
        │           │           │
        └───────────┴───────────┘
                │
        ┌───────────────────┐
        │   模型与工具层      │
        └───────────────────┘
```

---

## 智能体角色

### 1. 训练器 (Trainer)
**职责**：
- 负责每日认知训练
- 制定个性化训练计划
- 追踪训练进度
- 生成训练报告

**使用模型**：
- glm-4-flash: 快速训练
- glm-4-plus: 深度分析

**工具**：
- 每日认知训练工具
- 能力评估工具

---

### 2. 分析器 (Analyzer)
**职责**：
- 深度分析输入内容
- 识别模式和趋势
- 生成洞察和建议
- 发现隐含假设

**使用模型**：
- glm-4-plus: 深度分析
- glm-4-air: 常规分析
- search-pro: 文献检索

**工具**：
- 问题定义辅助
- 思考模型分析

---

### 3. 研究者 (Researcher)
**职责**：
- 信息收集和搜索
- 文献和案例检索
- 知识图谱构建
- 资源推荐

**使用模型**：
- search-pro: 文献搜索
- embedding-3: 向量检索
- glm-4-plus: 信息整合

**工具**：
- 知识检索工具
- 文献管理工具

---

### 4. 规划器 (Planner)
**职责**：
- 任务分解和规划
- 执行计划生成
- 资源分配
- 里程碑设置

**使用模型**：
- glm-4-plus: 规划和分解
- glm-4-air: 快速规划

**工具**：
- 任务管理工具
- 进度跟踪工具

---

### 5. 执行器 (Executor)
**职责**：
- 执行具体任务
- 工具调用
- 结果验证
- 错误处理和重试

**使用模型**：
- glm-4-flash: 快速执行
- codegeex-4: 代码相关
- glm-image: 可视化生成

**工具**：
- 所有AI工具和工作流
- 代码执行环境

---

## 工作流

### 工作流1：能力提升

```
用户输入: "提升问题定义能力"

1. 训练器分析 → 分析当前水平 (analyzer)
2. 规划器规划 → 创建30天计划 (planner)
3. 训练器执行 → 每日训练 (trainer)
4. 执行器验证 → 验证进展 (executor)
5. 分析器总结 → 分析进步 (analyzer)
```

### 工作流2：问题解决

```
用户输入: "系统性能下降"

1. 分析器深度分析 → 问题根因 (analyzer)
2. 研究者搜索 → 相关资料 (researcher)
3. 规划器规划 → 解决方案 (planner)
4. 执行器执行 → 实施方案 (executor)
5. 训练器训练 → 能力提升 (trainer)
```

### 工作流3：自主学习

```
用户输入: "学习新框架"

1. 研究者搜索 → 文档资料 (researcher)
2. 分析器分析 → 技术要点 (analyzer)
3. 规划器规划 → 学习路径 (planner)
4. 训练器执行 → 每日学习 (trainer)
5. 执行器实践 → 项目实践 (executor)
```

---

## 使用方法

### 启动系统

```bash
# 配置API密钥
export GLM_API_KEY="your-api-key-here"

# 启动系统
cd knowledge-base
./ai_agent/start_agent.sh

# 或直接运行
cd ai-agent
python3 main.py --interactive
```

### 交互模式

```bash
python3 ai-agent/main.py --interactive
```

**可用选项**：
1. 能力提升
2. 问题解决
3. 单智能体交互
4. 查看系统状态
5. 退出

### 批处理模式

```bash
python3 ai-agent/main.py --batch tasks.json
```

tasks.json 格式：
```json
[
  {
    "name": "任务1",
    "description": "每日认知训练",
    "type": "training",
    "input": "今天的观点"
  },
  {
    "name": "任务2",
    "description": "问题定义",
    "type": "analysis",
    "query": "分析这个问题"
  }
]
```

---

## 智能体通信

### 消息类型

```python
class MessageType:
    TASK = "task"           # 任务分配
    RESULT = "result"        # 结果返回
    REQUEST = "request"      # 请求处理
    NOTIFICATION = "notification"  # 通知消息
    ERROR = "error"          # 错误消息
```

### 消息示例

```python
# 训练器 → 规划器
message = {
    "id": "msg_001",
    "from_agent": "trainer_001",
    "to_agent": "planner_001",
    "type": "REQUEST",
    "content": {
        "task": "创建30天训练计划",
        "capability": "problem-definition",
        "current_level": 5,
        "target_level": 8
    }
}

# 规划器 → 训练器
message = {
    "id": "msg_002",
    "from_agent": "planner_001",
    "to_agent": "trainer_001",
    "type": "RESULT",
    "content": {
        "plan": "30天训练计划详情"
    }
}
```

---

## 记忆系统

### 短期记忆
- 临时存储
- 会话上下文
- 工作数据

### 长期记忆
- 能力评估历史
- 训练记录
- 问题解决案例

### 工作记忆
- 当前任务状态
- 中间结果
- 临时数据

---

## 模型使用

### 场景映射

| 场景 | 智能体 | 推荐模型 |
|------|--------|----------|
| 快速训练 | Trainer | glm-4-flash |
| 深度分析 | Analyzer | glm-4-plus |
| 文献搜索 | Researcher | search-pro |
| 快速规划 | Planner | glm-4-air |
| 代码分析 | Executor | codegeex-4 |
| 向量检索 | Researcher | embedding-3 |

### 并发管理

- 模型并发：动态管理
- 优先级队列：重要任务优先
- 成本控制：合理分配并发额度

---

## 开始使用

### 快速开始（3步）

**第1步：配置API**
```bash
export GLM_API_KEY="your-api-key-here"
```

**第2步：启动系统**
```bash
cd knowledge-base
./ai_agent/start_agent.sh
```

**第3步：交互使用**
```bash
python3 ai-agent/main.py --interactive
# 选择 "1. 能力提升"
```

---

## 核心特性

### 1. 多智能体协作
- 自动任务分解
- 智能路由
- 结果聚合
- 异步执行

### 2. 自主决策
- 模型选择
- 任务优先级
- 错误重试
- 动态调整

### 3. 记忆持久化
- 短期/长期/工作记忆
- 上下文管理
- 学习历史记录
- 经验积累

### 4. 工作流引擎
- 预定义工作流
- 自定义工作流
- 依赖管理
- 里程碑跟踪

---

## 技术架构

### 核心组件

1. **agent_framework.py** - 智能体框架
2. **main.py** - 主程序和协调器
3. **start_agent.sh** - 启动脚本
4. **tools/**** - 工具集成
5. **coordination/** - 协调机制
6. **planning/** - 任务规划
7. **memory/** - 记忆系统

---

## 文档和工具

### 文档
- README.md - 系统总览
- ARCHITECTURE.md - 架构设计
- AGENTS.md - 智能体详解

### 工具
- 模型管理器：ai-tools/utils/glm_models.py
- 认知训练：ai-tools/workflows/daily_cognitive_trainer.py
- 问题定义：ai-tools/workflows/problem_definition_assistant.py
- 能力评估：ai-tools/workflows/capability_assessment.py

---

## 下一步

1. 配置 GLM API 密钥
2. 运行启动脚本
3. 启动交互模式
4. 选择工作流或智能体
5. 开始系统能力提升

---

## 技术支持

### GLM API文档
- https://open.bigmodel.cn/
- https://open.bigmodel.cn/dev/api

### Python SDK
- pip install zhipuai
- pip install openai

### 问题反馈
- 在知识库项目中提出 Issue
- 参考文档和示例代码

---

**记住**：AI智能体系统是工具，核心价值仍然在人类的判断力和决策力。用智能体放大能力，而非替代它。
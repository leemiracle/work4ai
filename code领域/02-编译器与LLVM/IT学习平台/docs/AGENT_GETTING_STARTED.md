# AI Agent System - 快速开始指南

## 项目概述

这是一个完整的AI Agent系统，实现多Agent协同、自主决策、工具链调用等高级Agent能力。

---

## 核心概念

### 1. Agent（智能体）
Agent是具有以下能力的自主实体：
- **规划**: 分解目标，制定计划
- **推理**: 使用逻辑和知识进行决策
- **行动**: 调用工具执行操作
- **学习**: 从经验中改进
- **通信**: 与其他Agent协作

### 2. 工具（Tool）
Agent可以调用的功能模块：
- 数据库工具
- API工具
- 文件操作工具
- 代码执行工具
- 向量搜索工具
- LLM工具
- 记忆工具

### 3. 记忆（Memory）
Agent的记忆系统：
- **短期记忆**: 当前会话的上下文
- **长期记忆**: 持久化的知识和经验
- **情景记忆**: 完整的执行记录

### 4. 编排器（Orchestrator）
协调多个Agent完成复杂任务：
- 任务分解
- Agent调度
- 依赖管理
- 协调通信

---

## 快速开始

### 1. 安装依赖

```bash
cd backend

# 基础依赖
pip install -r requirements.txt

# AI依赖
pip install -r ai_requirements.txt

# Agent依赖
pip install -r agent_requirements.txt
```

**agent_requirements.txt**:
```
langchain==0.1.0
langchain-community==0.0.10
```

### 2. 启动服务

```bash
cd backend
python main.py
```

服务将在 `http://localhost:8000` 启动

### 3. 访问Agent API

```bash
# 查看所有Agent
curl http://localhost:8000/api/v1/agents/list

# 创建Agent任务
curl -X POST http://localhost:8000/api/v1/agents/task \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "学习LLVM编译器",
    "context": {"current_level": "beginner"},
    "priority": "high"
  }'

# 查看任务状态
curl http://localhost:8000/api/v1/agents/task/{task_id}
```

---

## Agent类型

### 学习相关Agent

#### LearningAgent
- 生成学习路径
- 分析学习进度
- 推荐学习资源
- 生成练习题

#### ConceptAgent
- 解释技术概念
- 生成学习材料
- 回答技术问题

#### QuizAgent
- 生成测试题
- 评估答案
- 提供反馈

### 项目管理Agent

#### ProjectAgent
- 分析项目风险
- 规划里程碑
- 跟踪进度
- 分配资源

#### TaskAgent
- 分解任务
- 优化任务顺序
- 估算工时
- 管理依赖

#### TeamAgent
- 分析团队效率
- 提供协作建议
- 优化沟通

### 编码相关Agent

#### CodeAgent
- 生成代码
- 优化代码
- 审查代码
- 重构建议

#### ReviewAgent
- 检测Bug
- 安全检查
- 性能分析
- 最佳实践

#### DebugAgent
- 诊断问题
- 分析错误
- 提供修复建议

### 知识管理Agent

#### KnowledgeAgent
- 提取知识
- 语义搜索
- 构建知识图谱
- 生成总结

#### SearchAgent
- 多源搜索
- 信息聚合
- 相关性排序

#### SummarizationAgent
- 文档总结
- 会议总结
- 报告生成

---

## Agent使用示例

### 1. 创建学习路径

```python
import requests

# 创建任务
response = requests.post(
    'http://localhost:8000/api/v1/agents/task',
    json={
        'goal': '学习LLVM编译器技术',
        'context': {
            'current_level': 'beginner',
            'available_time_week': 10
        },
        'priority': 'high',
        'execution_mode': 'sequential'
    }
)

task_id = response.json()['task_id']
print(f"任务创建成功: {task_id}")

# 查看执行进度
while True:
    status = requests.get(f'http://localhost:8000/api/v1/agents/task/{task_id}').json()
    print(f"状态: {status['status']}, 进度: {status['progress']*100:.1f}%")

    if status['status'] in ['completed', 'failed']:
        break

    import time
    time.sleep(5)
```

### 2. 代码审查Agent

```python
response = requests.post(
    'http://localhost:8000/api/v1/agents/execute',
    json={
        'agent': 'ReviewAgent',
        'task': {
            'goal': '审查这段Python代码',
            'context': {
                'code': '''def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)'''
            }
        }
    }
)

result = response.json()
print(result['output'])
```

### 3. 多Agent协作

```python
# 编排器会自动协调多个Agent
response = requests.post(
    'http://localhost:8000/api/v1/agents/task',
    json={
        'goal': '完成一个完整的Web应用项目',
        'context': {
            'type': 'fullstack',
            'tech_stack': ['react', 'python'],
            'timeline': '4周'
        },
        'execution_mode': 'hybrid'
    }
)

task_id = response.json()['task_id']

# 查看执行的步骤
execution = requests.get(f'http://localhost:8000/api/v1/agents/execution/{task_id}').json()
for step in execution['steps']:
    print(f"{step['agent']}: {step['subtask']['description']}")
    print(f"结果: {step['result']}")
```

---

## Agent工具使用

### 1. 调用数据库工具

```python
response = requests.post(
    'http://localhost:8000/api/v1/agents/tool/database_query',
    json={
        'query': 'SELECT * FROM notes WHERE category = "LLVM" LIMIT 10'
    }
)

print(response.json()['result'])
```

### 2. 执行代码

```python
response = requests.post(
    'http://localhost:8000/api/v1/agents/tool/execute_code',
    json={
        'language': 'python',
        'code': 'print("Hello, Agent!")'
    }
)

print(response.json()['result'])
```

### 3. 向量搜索

```python
response = requests.post(
    'http://localhost:8000/api/v1/agents/tool/vector_search',
    json={
        'query': 'LLVM SSA form',
        'collection_name': 'notes',
        'n_results': 5
    }
)

print(response.json()['result'])
```

---

## Agent记忆系统

### 1. 存储记忆

```python
response = requests.post(
    'http://localhost:8000/api/v1/agents/memory/store',
    json={
        'agent': 'LearningAgent',
        'key': 'user_learning_level',
        'value': 'intermediate',
        'memory_type': 'long_term',
        'importance': 0.8
    }
)
```

### 2. 检索记忆

```python
response = requests.get(
    'http://localhost:8000/api/v1/agents/memory/retrieve/user_learning_level'
)

print(response.json()['value'])
```

### 3. 语义搜索记忆

```python
response = requests.post(
    'http://localhost:8000/api/v1/agents/memory/search',
    json={
        'query': 'LLVM学习进度',
        'memory_type': 'long_term',
        'limit': 10
    }
)

print(response.json()['results'])
```

---

## Agent通信

### 1. Agent间消息传递

```python
response = requests.post(
    'http://localhost:8000/api/v1/agents/message/send',
    json={
        'sender': 'PlanningAgent',
        'receiver': 'TaskAgent',
        'type': 'request',
        'content': {
            'action': 'get_task_estimate',
            'parameters': {
                'task': '实现SSA Pass'
            }
        }
    }
)
```

### 2. 广播消息

```python
response = requests.post(
    'http://localhost:8000/api/v1/agents/message/broadcast',
    json={
        'sender': 'Orchestrator',
        'type': 'notification',
        'content': {
            'message': '系统维护将在1小时后开始'
        }
    }
)
```

---

## 最佳实践

### 1. Agent设计
- 明确Agent职责
- 避免Agent职责重叠
- 保持Agent简洁专注

### 2. 工具设计
- 工具应该做一件事并做好
- 提供清晰的错误信息
- 记录工具调用

### 3. 记忆管理
- 重要信息存长期记忆
- 临时信息存短期记忆
- 完整事件存情景记忆

### 4. 编排策略
- 独立任务并行执行
- 依赖任务顺序执行
- 复杂任务混合执行

---

## 故障排查

### 1. Agent未响应
```bash
# 检查Agent状态
curl http://localhost:8000/api/v1/agents/status/{agent_name}

# 重启Agent
curl -X POST http://localhost:8000/api/v1/agents/restart/{agent_name}
```

### 2. 工具调用失败
```bash
# 查看工具调用历史
curl http://localhost:8000/api/v1/agents/{agent_name}/tools/history
```

### 3. 记忆系统问题
```bash
# 清理短期记忆
curl -X POST http://localhost:8000/api/v1/agents/memory/cleanup/short_term

# 清理长期记忆
curl -X POST http://localhost:8000/api/v1/agents/memory/cleanup/long_term
```

---

## 下一步

- 查看 [Agent架构文档](../AGENT_ARCHITECTURE.md)
- 探索Agent API文档: `http://localhost:8000/docs`
- 学习Agent最佳实践
- 创建自定义Agent

---

**最后更新**: 2026-02-13

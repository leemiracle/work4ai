# AI驱动的IT学习与项目管理平台 - 快速开始指南

## 项目概述

这是一个融合了人工智能技术的综合性IT学习与项目管理平台，通过AI助手提升学习效率和项目管理水平。

---

## 核心AI功能

### 🎓 AI学习助手
- **智能对话**: 24/7 AI答疑，理解你的学习需求
- **个性化路径**: 根据你的目标和水平生成学习计划
- **进度分析**: AI分析学习进度，识别薄弱环节
- **智能练习**: 生成针对性的练习题和测验

### 📊 AI项目助手
- **风险预测**: 分析项目风险，提供缓解策略
- **任务优化**: 基于团队技能智能分配任务
- **自动报告**: 生成专业的项目进度报告
- **团队分析**: 优化团队协作效率

### 🧠 AI知识管理
- **智能总结**: 自动总结长文档和笔记
- **语义搜索**: 基于内容含义而非关键词搜索
- **内容生成**: 扩展内容、生成示例
- **知识图谱**: 自动构建知识关联

### 💻 AI编码助手
- **代码生成**: 根据描述生成代码
- **代码优化**: 改进代码质量和性能
- **代码解释**: 详细解释代码逻辑
- **Bug检测**: 自动发现潜在问题

---

## 快速开始

### 1. 安装依赖

#### 后端依赖

```bash
cd backend

# 基础依赖
pip install -r requirements.txt

# AI依赖
pip install -r ai_requirements.txt
```

**AI依赖说明**:
- `chromadb`: 向量数据库，用于存储文档嵌入
- `sentence-transformers`: 文本嵌入模型
- `openai`/`anthropic`: LLM API客户端（可选）
- `httpx`: 异步HTTP客户端

#### 前端依赖

```bash
cd frontend
npm install
```

### 2. 配置LLM

#### 选项1: 使用Ollama（推荐，免费本地部署）

```bash
# 安装Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull llama2
ollama pull nomic-embed-text  # 嵌入模型

# 启动Ollama服务
ollama serve
```

配置环境变量:
```bash
export LLM_PROVIDER="ollama"
export OLLAMA_BASE_URL="http://localhost:11434"
export EMBEDDING_PROVIDER="ollama"
```

#### 选项2: 使用OpenAI API

```bash
export LLM_PROVIDER="openai"
export OPENAI_API_KEY="your-openai-api-key"
export EMBEDDING_PROVIDER="openai"
```

#### 选项3: 使用Anthropic Claude

```bash
export LLM_PROVIDER="anthropic"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 3. 启动服务

#### 启动后端

```bash
cd backend
python main.py
```

后端将在 `http://localhost:8000` 启动

检查AI状态:
```bash
curl http://localhost:8000/api/v1/ai/status
```

#### 启动前端

```bash
cd frontend
npm start
```

前端将在 `http://localhost:3000` 启动

---

## AI功能使用指南

### AI学习助手

#### 1. AI对话

访问 `http://localhost:3000/ai`，点击"AI对话"标签页

**使用示例**:
- "请解释LLVM IR中的SSA形式"
- "如何优化循环代码？"
- "推荐一些学习编译原理的资源"

#### 2. 生成学习路径

1. 点击"学习助手"标签页
2. 点击"个性化学习路径"卡片中的"生成"按钮
3. 填写表单:
   - 学习目标: 例如"学习LLVM编译器技术"
   - 当前水平: 选择你的技能水平
   - 每周时间: 可投入学习的时间
4. 点击"生成"

AI将返回包含多个阶段的学习路径，每个阶段有明确的目标、主题和里程碑。

#### 3. 概念解释

在"学习助手"标签页中，输入任何技术概念，点击"解释"即可获得详细的解释。

**示例概念**:
- SSA (Static Single Assignment)
- 虚拟内存
- 编译器优化Pass
- RISC vs CISC

### AI项目助手

#### 1. 项目风险分析

```python
# 通过API调用
import requests

response = requests.post(
    'http://localhost:8000/api/v1/ai/project/risk-analysis',
    json={
        "project_data": {
            "name": "LLVM编译器项目",
            "team_size": 5,
            "phase": "开发阶段",
            "remaining_days": 30,
            "completed_tasks": 8,
            "total_tasks": 20
        }
    }
)

print(response.json())
```

#### 2. 任务优化

```python
response = requests.post(
    'http://localhost:8000/api/v1/ai/project/optimize-tasks',
    json={
        "team_members": [
            {
                "name": "Alice",
                "skills": ["Python", "C++", "LLVM IR"]
            },
            {
                "name": "Bob",
                "skills": ["Python", "Web开发"]
            }
        ],
        "tasks": [
            {
                "title": "实现SSA Pass",
                "required_skills": ["C++", "LLVM IR"]
            },
            {
                "title": "开发Web界面",
                "required_skills": ["Web开发", "Python"]
            }
        ]
    }
)
```

### AI知识管理

#### 1. 自动总结

```python
response = requests.post(
    'http://localhost:8000/api/v1/ai/knowledge/summarize',
    json={
        "content": "你的长文档内容...",
        "max_length": 500
    }
)

summary = response.json()['summary']
print(summary)
```

#### 2. 语义搜索

```python
response = requests.post(
    'http://localhost:8000/api/v1/ai/knowledge/search',
    json={
        "query": "如何优化编译器性能",
        "collection_name": "notes",
        "n_results": 5
    }
)

results = response.json()
print(results['answer'])
print(results['sources'])
```

### AI编码助手

#### 1. 代码生成

```python
response = requests.post(
    'http://localhost:8000/api/v1/ai/code/generate',
    json={
        "language": "python",
        "description": "实现快速排序算法"
    }
)

code = response.json()['code']
print(code)
```

#### 2. 代码优化

```python
response = requests.post(
    'http://localhost:8000/api/v1/ai/code/improve',
    json={
        "code": "你的代码...",
        "language": "python",
        "focus": ["performance", "readability"]
    }
)

improvement = response.json()['improvement']
print(improvement)
```

---

## 向量数据库

### 添加笔记到向量库

笔记创建时，系统会自动将内容添加到向量数据库，支持语义搜索。

### 管理向量集合

```bash
# 查看所有集合
curl http://localhost:8000/api/v1/ai/vector-store/collections

# 查看集合统计
curl http://localhost:8000/api/v1/ai/vector-store/stats/notes
```

---

## CLI AI命令

```bash
cd cli

# AI聊天（即将推出）
python main.py ai chat

# AI分析项目
python main.py ai project analyze

# AI生成学习路径
python main.py ai learning path --goal "学习LLVM"
```

---

## 最佳实践

### 1. 提示词工程

**好的提示词**:
```
"作为编译器专家，请解释LLVM IR中的SSA形式，并给出代码示例。
假设我是初学者，请用简单的语言。"
```

**不好的提示词**:
```
"SSA是什么？"
```

### 2. 上下文管理

- 在对话中提供足够的上下文信息
- 使用对话历史保持连贯性
- 及时纠正AI的误解

### 3. 验证AI输出

- 验证代码是否可以运行
- 检查技术建议的准确性
- 引用多个来源交叉验证

### 4. 隐私保护

- 不要输入敏感信息
- 注意数据保护政策
- 使用本地LLM提高隐私性

---

## 故障排查

### 1. Ollama连接失败

```bash
# 检查Ollama服务
curl http://localhost:11434/api/tags

# 如果失败，重启Ollama
ollama serve
```

### 2. 嵌入模型未下载

```bash
# 下载嵌入模型
ollama pull nomic-embed-text

# 或使用其他模型
ollama pull all-MiniLM-L6-v2
```

### 3. AI响应慢

- 检查网络连接
- 使用更小的模型
- 启用缓存
- 使用本地LLM

### 4. 向量数据库错误

```bash
# 清除向量数据库
rm -rf data/chroma

# 重新初始化
python main.py init
```

---

## 性能优化

### 1. 启用缓存

```python
# 在配置中
ENABLE_CACHE = true
CACHE_TTL = 3600
```

### 2. 批量处理

- 批量嵌入文档
- 批量查询向量库
- 批量生成回答

### 3. 异步处理

- 使用异步API
- 长任务后台执行
- 流式响应

---

## 扩展和自定义

### 添加自定义提示词模板

在 `backend/ai/rag.py` 中修改提示词模板:

```python
custom_prompt = """你的自定义提示词..."""
```

### 集成新的LLM

在 `backend/ai/llm.py` 中添加新的LLM提供商:

```python
async def _chat_custom(self, ...):
    # 实现自定义LLM调用
    pass
```

### 自定义向量库

在 `backend/ai/vector_store.py` 中添加新的向量库支持:

```python
def _configure_custom_vector_store(self):
    # 实现自定义向量库
    pass
```

---

## 高级功能

### 1. 流式响应

```python
async for chunk in llm_service.chat(messages, stream=True):
    print(chunk, end='', flush=True)
```

### 2. 自定义Agent

创建自定义AI Agent，添加特定领域知识。

### 3. 多模态AI

扩展到图像、视频和音频分析。

---

## 下一步

- 查看 [AI架构文档](../AI_ARCHITECTURE.md)
- 探索 [项目文档](./DEPLOYMENT.md)
- 学习 [LLM最佳实践](https://platform.openai.com/docs/guides/prompt-engineering)
- 了解 [向量数据库](https://www.pinecone.io/learn/vector-database/)

---

**祝你学习愉快！如有问题，请查看文档或提交Issue。**

---

**最后更新**: 2026-02-13

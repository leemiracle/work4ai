# AI工具包使用指南

> 知识库AI增强工具集，实现GLM模型的全面集成

---

## 目录结构

```
ai-tools/
├── README.md                       # 本文件
├── utils/                          # 工具类
│   └── glm_models.py              # GLM模型管理器
├── workflows/                       # 工作流
│   ├── daily_cognitive_trainer.py  # 每日认知训练
│   ├── problem_definition_assistant.py  # 问题定义辅助
│   └── capability_assessment.py   # 能力评估
├── agents/                          # AI智能体
│   └── ...
├── prompts/                         # 提示词库
│   └── ...
└── tests/                           # 测试
    └── ...
```

---

## 快速开始

### 1. 配置API密钥

```bash
# 设置环境变量
export GLM_API_KEY="your-api-key-here"

# 或在配置文件中创建
echo "GLM_API_KEY=your-api-key-here" > .env
```

### 2. 安装依赖

```bash
pip install openai  # 用于调用GLM API
# 或
pip install zhipuai  # 智谱AI官方SDK
```

### 3. 运行示例

```bash
# 每日认知训练
cd ai-tools/workflows
python daily_cognitive_trainer.py --interactive

# 问题定义辅助
python problem_definition_assistant.py --problem "项目延期了，需要加快进度"

# 能力评估
python capability_assessment.py --list
python capability_assessment.py --assess problem-definition
```

---

## 工具说明

### GLM模型管理器 (glm_models.py)

**功能**：
- 60+个GLM模型配置
- 模型推荐引擎
- 按类型筛选模型

**使用示例**：

```python
from ai-tools.utils.glm_models import GLMModelManager

manager = GLMModelManager()

# 打印所有模型
manager.print_all_models()

# 推荐模型
model = manager.recommend_model("深度分析", "deep")
print(f"推荐模型: {model}")

# 获取模型配置
config = manager.get_model("glm-4-plus")
print(f"模型: {config.name}, 并发: {config.concurrency}")
```

---

### 每日认知训练 (daily_cognitive_trainer.py)

**功能**：
- 实现五层认知训练
- AI辅助每一步分析
- 训练日志自动保存

**五层训练**：
1. 拆解（信息理解）
2. 推演（逻辑推理）
3. 量化（决策优化）
4. 画反馈（系统思维）
5. 复盘（元认知）

**使用示例**：

```bash
# 交互式模式
python daily_cognitive_trainer.py --interactive

# 单次训练
python daily_cognitive_trainer.py --input "微服务比单体架构好"

# 指定模型
python daily_cognitive_trainer.py --input "..." --model glm-4-plus

# 保存日志
python daily_cognitive_trainer.py --input "..." --save my-training.json
```

---

### 问题定义辅助 (problem_definition_assistant.py)

**功能**：
- 5问题框架分析
- 假设质疑清单
- 价值评估矩阵
- 多视角重新定义

**分析方法**：
1. `5q` - 5问题框架
2. `assumption` - 假设质疑
3. `value` - 价值评估
4. `perspectives` - 多视角
5. `full` - 完整分析

**使用示例**：

```bash
# 交互式模式
python problem_definition_assistant.py --interactive

# 完整分析
python problem_definition_assistant.py --problem "系统性能下降" --method full

# 单一方法
python problem_definition_assistant.py --problem "..." --method 5q
python problem_definition_assistant.py --problem "..." --method assumption

# 指定模型
python problem_definition_assistant.py --problem "..." --method full --model glm-4-plus

# 保存结果
python problem_definition_assistant.py --problem "..." --save definition.json
```

---

### 能力评估 (capability_assessment.py)

**功能**：
- 24个核心能力评估
- AI辅助评分
- 改进建议生成
- 评估报告生成

**使用示例**：

```bash
# 列出所有能力
python capability_assessment.py --list

# 交互式评估
python capability_assessment.py --interactive

# 评估指定能力
python capability_assessment.py --assess problem-definition,judgment

# 批量评估核心能力
python capability_assessment.py --assess problem-definition,judgment,resource-integration,influence

# 保存评估结果
python capability_assessment.py --assess problem-definition --save assessment.json
```

---

## 模型选择指南

| 场景 | 推荐模型 | 工具 |
|------|---------|------|
| 快速练习 | glm-4-flash | daily_cognitive_trainer.py |
| 深度分析 | glm-4-plus | problem_definition_assistant.py |
| 日常咨询 | glm-4-air | 所有工具 |
| 能力评估 | glm-4-plus | capability_assessment.py |
| 代码相关 | codegeex-4 | - |
| 知识检索 | embedding-3 + glm-4-plus | - |
| 文献搜索 | search-pro | - |

---

## 工作流集成

### 工作流1：每日训练

```bash
# 第一步：每日认知训练
python ai-tools/workflows/daily_cognitive_trainer.py --interactive

# 第二步：保存日志
# 自动保存到 learning-log/daily/

# 第三步：月度复盘
# 使用每月的数据进行分析
```

### 工作流2：问题解决

```bash
# 第一步：问题定义
python ai-tools/workflows/problem_definition_assistant.py --problem "..." --method full

# 第二步：分析AI建议
# 重新定义问题

# 第三步：每日训练
python ai-tools/workflows/daily_cognitive_trainer.py --input "重新定义后的问题"

# 第四步：记录到案例库
# 将结果保存到 cases/
```

### 工作流3：能力提升

```bash
# 第一步：初始评估
python ai-tools/workflows/capability_assessment.py --interactive

# 第二步：专项练习
# 选择1-2个能力进行专项练习

# 第三步：每日训练
# 持续进行每日认知训练

# 第四步：月度再评估
# 对比进步情况

# 第五步：调整计划
# 根据评估结果调整下月计划
```

---

## 提示词库

### 认知训练提示词

```python
# 拆解
prompt = """分析以下观点：
1. 核心定义是什么？
2. 前提假设是什么？
3. 边界在哪里？
4. 有反例吗？

观点：{input}
"""

# 推演
prompt = """对观点进行反向推理：
1. 如果为真会推出什么？
2. 如果为假会发生什么？
3. 有没有第三种解释？

观点：{input}
"""
```

### 问题定义提示词

```python
# 5问题框架
prompt = """对以下问题进行5问题框架分析：
1. 问题是什么？
2. 为什么是问题？
3. 为谁而存在？
4. 为什么现在解决？
5. 不解决会怎样？

问题：{input}
"""
```

### 能力评估提示词

```python
# 能力评估
prompt = """基于{capability}的评估维度，分析用户回答：
评估维度：{dimensions}
用户回答：{responses}

请提供：
1. 每个维度的得分（1-10分）
2. 得分理由
3. 改进建议
4. 下一步练习方向
"""
```

---

## API集成

### OpenAI兼容接口

```python
import openai

openai.api_key = os.getenv("GLM_API_KEY")
openai.api_base = "https://open.bigmodel.cn/api/paas/v4"

response = openai.ChatCompletion.create(
    model="glm-4-plus",
    messages=[{"role": "user", "content": "你好"}]
)

print(response.choices[0].message.content)
```

### 智谱AI官方SDK

```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key=os.getenv("GLM_API_KEY"))

response = client.chat.completions.create(
    model="glm-4-plus",
    messages=[{"role": "user", "content": "你好"}]
)

print(response.choices[0].message.content)
```

---

## 测试

```bash
# 测试模型管理器
python ai-tools/utils/glm_models.py

# 测试每日训练
python ai-tools/workflows/daily_cognitive_trainer.py --input "测试输入"

# 测试问题定义
python ai-tools/workflows/problem_definition_assistant.py --problem "测试问题" --method 5q

# 测试能力评估
python ai-tools/workflows/capability_assessment.py --list
```

---

## 下一步

1. 配置GLM API密钥
2. 运行第一个工具：每日认知训练
3. 尝试不同工具的功能
4. 根据需要自定义提示词
5. 集成到日常工作流

---

**记住**：AI是强大的工具，但判断力、决策力和影响力仍然是人类的核心价值。用 AI 放大这些能力，而非替代它们。
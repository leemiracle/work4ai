# Data Analysis Planning Agent

基于`react_agent.py`开发的具有自主规划能力的数据分析智能体，能够理解数据分析需求、制定分析计划并系统性地执行。

## 核心特性

### 🎯 自主规划能力
- **需求理解**: 深度理解业务问题和分析目标
- **计划制定**: 创建系统性的数据分析步骤计划
- **动态调整**: 根据分析结果动态调整后续步骤

### 📊 全流程分析
- **数据源检查**: 自动识别和检查可用数据源
- **数据加载**: 智能加载和预处理数据
- **探索性分析**: 进行全面的数据探索
- **统计分析**: 执行统计检验和深度分析
- **可视化**: 生成图表和可视化结果
- **洞察提取**: 提供业务洞察和建议

### 🤖 智能决策
- **步骤优化**: 根据数据特点优化分析步骤
- **工具选择**: 智能选择最适合的分析工具
- **结果验证**: 验证分析结果的可靠性

## 架构设计

### 继承结构
```
DataAnalysisPlanningAgent
├── 继承自 ConversableAgent
├── 扩展 ReActAgent 的规划能力
└── 集成数据分析专用工具
```

### 核心组件

#### 1. 规划状态管理
```python
class DataAnalysisPlanningAgent(ConversableAgent):
    analysis_plan: Optional[List[Dict[str, Any]]]  # 分析计划
    current_step: int = Field(default=0)           # 当前步骤
    planning_complete: bool = Field(default=False) # 规划完成状态
```

#### 2. 专用工具集
- `create_analysis_plan`: 创建分析计划
- `examine_data_sources`: 检查数据源
- `load_data`: 加载数据
- `explore_data`: 探索性分析
- `statistical_analysis`: 统计分析
- `create_visualization`: 创建可视化
- `generate_insights`: 生成洞察

#### 3. 智能提示模板
```python
_DATA_AGENT_SYSTEM_TEMPLATE = """
You are an expert data analyst with strong planning and execution capabilities.

1. Planning Phase: 理解目标、识别数据、创建计划
2. Execution Phase: 加载数据、执行分析、生成结果  
3. Communication Phase: 展示发现、提供洞察、建议后续
"""
```

## 使用方法

### 基础使用

```python
from dbgpt.agent.expand.data_agent import DataAnalysisPlanningAgent
from dbgpt.agent.resource import ToolPack, ResourcePack

# 1. 创建工具
tools = [DataSourceTool(), LoadDataTool(), ExploreDataTool()]
tool_pack = ToolPack(tools=tools)

# 2. 创建资源包
resource_pack = ResourcePack()
resource_pack._resources["tools"] = tool_pack

# 3. 创建Agent
agent = DataAnalysisPlanningAgent(resource=resource_pack)

# 4. 发送分析请求
message = AgentMessage(content="分析销售数据趋势，提供业务洞察")
response = await agent.act(message, sender=None)
```

### 高级配置

```python
# 自定义规划参数
agent = DataAnalysisPlanningAgent(
    max_retry_count=25,  # 增加重试次数
    resource=resource_pack,
    llm_client=your_llm_client
)

# 设置分析目标
agent.profile.goal = "专注于电商数据分析，提供精准的业务洞察"
```

## 工作流程

### 1. 需求理解阶段
```
用户输入 → 理解业务问题 → 识别分析目标 → 确定数据需求
```

### 2. 规划制定阶段
```
数据需求 → 检查数据源 → 制定分析计划 → 估算时间和资源
```

### 3. 执行分析阶段
```
执行计划 → 数据加载 → 探索分析 → 深度分析 → 结果验证
```

### 4. 结果呈现阶段
```
分析结果 → 生成洞察 → 创建可视化 → 提供建议 → 完成任务
```

## 示例场景

### 场景1: 销售趋势分析
```python
question = "分析我们的销售数据，识别趋势并提供业务规划洞察"

# Agent会自动执行：
# 1. 创建销售趋势分析计划
# 2. 检查可用的销售数据源
# 3. 加载销售数据
# 4. 进行趋势分析
# 5. 生成可视化图表
# 6. 提供业务洞察和建议
```

### 场景2: 客户细分分析
```python
question = "进行客户细分分析，识别不同客户群体特征"

# Agent会自动执行：
# 1. 制定客户细分分析计划
# 2. 检查客户数据
# 3. 执行细分算法
# 4. 分析各群体特征
# 5. 提供营销建议
```

## 扩展开发

### 添加自定义工具

```python
class CustomAnalysisTool(BaseTool):
    @property
    def name(self) -> str:
        return "custom_analysis"
    
    @property
    def description(self) -> str:
        return "执行自定义分析逻辑"
    
    async def async_execute(self, **kwargs):
        # 实现自定义分析逻辑
        return {"result": "自定义分析结果"}

# 添加到Agent
agent.resource._resources["custom_analysis"] = CustomAnalysisTool()
```

### 自定义规划逻辑

```python
class CustomDataAnalysisAgent(DataAnalysisPlanningAgent):
    async def create_custom_plan(self, objective: str):
        # 实现自定义规划逻辑
        custom_plan = [
            {"step": 1, "action": "custom_preprocessing"},
            {"step": 2, "action": "custom_analysis"},
        ]
        self.analysis_plan = custom_plan
        return custom_plan
```

## 最佳实践

### 1. 数据准备
- 确保数据源可访问
- 提供数据文档和元数据
- 预处理常见数据质量问题

### 2. 目标设定
- 明确分析目标和业务问题
- 提供背景信息和约束条件
- 设定期望的输出格式

### 3. 工具配置
- 根据分析需求配置合适工具
- 确保工具参数正确设置
- 提供工具使用文档

### 4. 结果验证
- 验证分析结果的合理性
- 检查数据质量影响
- 确认业务洞察的准确性

## 故障排除

### 常见问题

#### 1. 规划失败
```
问题: Agent无法创建有效的分析计划
解决: 检查数据源可用性，明确分析目标
```

#### 2. 工具执行错误
```
问题: 数据分析工具执行失败
解决: 检查工具参数，验证数据格式
```

#### 3. 结果质量差
```
问题: 分析结果不够深入或准确
解决: 提供更多背景信息，调整分析策略
```

### 调试方法

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查Agent状态
print(f"Planning complete: {agent.planning_complete}")
print(f"Current step: {agent.current_step}")
print(f"Analysis plan: {agent.analysis_plan}")
```

## 性能优化

### 1. 缓存策略
- 缓存数据加载结果
- 缓存分析计算结果
- 缓存常用查询结果

### 2. 并行处理
- 并行执行独立分析任务
- 异步处理数据加载
- 批量处理相似请求

### 3. 资源管理
- 合理管理内存使用
- 优化计算资源分配
- 控制并发任务数量

## 未来规划

### 短期目标
- [ ] 添加更多预定义分析模板
- [ ] 优化规划算法
- [ ] 增强错误处理能力

### 中期目标
- [ ] 支持多数据源联合分析
- [ ] 集成机器学习模型
- [ ] 添加实时分析能力

### 长期目标
- [ ] 支持自然语言交互
- [ ] 自动化报告生成
- [ ] 智能推荐系统

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 开发环境设置
```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/

# 代码格式化
black src/
```

### 提交规范
- 使用清晰的提交信息
- 添加适当的测试用例
- 更新相关文档

## 许可证

MIT License - 详见LICENSE文件
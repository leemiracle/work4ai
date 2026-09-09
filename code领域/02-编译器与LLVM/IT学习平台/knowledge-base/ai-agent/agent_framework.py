"""
AI AGENT系统框架
支持多智能体协作、任务规划和工具调用
"""

from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime
import asyncio
from abc import ABC, abstractmethod
import threading
import time


class MessageType(Enum):
    """消息类型"""
    TASK = "task"
    RESULT = "result"
    REQUEST = "request"
    NOTIFICATION = "notification"
    ERROR = "error"


class AgentRole(Enum):
    """智能体角色"""
    PLANNER = "planner"              # 规划智能体
    EXECUTOR = "executor"            # 执行智能体
    ANALYZER = "analyzer"            # 分析智能体
    COORDINATOR = "coordinator"      # 协调智能体
    RESEARCHER = "researcher"        # 研究智能体
    TRAINER = "trainer"              # 训练智能体


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Message:
    """智能体间消息"""
    id: str
    from_agent: str
    to_agent: str
    type: MessageType
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    reply_to: Optional[str] = None


@dataclass
class Task:
    """任务定义"""
    id: str
    type: str
    description: str
    priority: int  # 1-10, 10最高
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: float = 0.0  # 0.0-1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Tool:
    """工具定义"""
    name: str
    description: str
    parameters: Dict[str, Any]
    execute_func: Callable[..., Any]
    requires_model: Optional[str] = None


class MemoryStore:
    """记忆存储系统"""
    
    def __init__(self):
        self.short_term = {}  # 短期记忆
        self.long_term = {}    # 长期记忆
        self.working_memory = {}  # 工作记忆
        self.embeddings = {}    # 向量存储
    
    def store(self, key: str, value: Any, memory_type: str = "short_term"):
        """存储记忆"""
        if memory_type == "short_term":
            self.short_term[key] = {
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
        elif memory_type == "long_term":
            self.long_term[key] = {
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
        elif memory_type == "working":
            self.working_memory[key] = value
    
    def retrieve(self, key: str, memory_type: str = "short_term") -> Optional[Any]:
        """检索记忆"""
        if memory_type == "short_term":
            entry = self.short_term.get(key)
            return entry["value"] if entry else None
        elif memory_type == "long_term":
            entry = self.long_term.get(key)
            return entry["value"] if entry else None
        elif memory_type == "working":
            return self.working_memory.get(key)
        return None
    
    def search(self, query: str, memory_type: str = "long_term") -> List[Dict[str, Any]]:
        """搜索记忆"""
        if memory_type == "long_term":
            results = []
            for key, entry in self.long_term.items():
                if query.lower() in str(entry["value"]).lower():
                    results.append({"key": key, **entry})
            return results
        return []
    
    def clear_working_memory(self):
        """清理工作记忆"""
        self.working_memory.clear()
    
    def get_context(self, limit: int = 10) -> Dict[str, Any]:
        """获取上下文"""
        return {
            "short_term": dict(list(self.short_term.items())[-limit:]),
            "working": self.working_memory
        }


class BaseAgent(ABC):
    """基础智能体"""
    
    def __init__(self, agent_id: str, role: AgentRole, model_manager):
        self.agent_id = agent_id
        self.role = role
        self.model_manager = model_manager
        self.memory = MemoryStore()
        self.message_queue = asyncio.Queue()
        self.tools: Dict[str, Tool] = {}
        self.is_running = False
    
    @abstractmethod
    async def process_message(self, message: Message) -> Optional[Message]:
        """处理消息"""
        pass
    
    @abstractmethod
    async def execute_task(self, task: Task) -> Any:
        """执行任务"""
        pass
    
    async def start(self):
        """启动智能体"""
        self.is_running = True
        while self.is_running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                response = await self.process_message(message)
                if response:
                    # 发送响应
                    await self.send_message(response)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Agent {self.agent_id} error: {e}")
    
    async def stop(self):
        """停止智能体"""
        self.is_running = False
    
    async def send_message(self, message: Message):
        """发送消息（需要在子类中实现）"""
        # 默认实现，子类可以覆盖
        pass
    
    def register_tool(self, tool: Tool):
        """注册工具"""
        self.tools[tool.name] = tool
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """使用工具"""
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        
        # 记录工具使用
        self.memory.store(f"tool_{tool_name}_last_used", datetime.now().isoformat())
        
        # 执行工具
        result = tool.execute_func(**kwargs)
        
        # 存储结果到工作记忆
        self.memory.store(f"tool_{tool_name}_result", result, "working")
        
        return result
    
    def choose_model(self, task_type: str, priority: str = "balanced") -> str:
        """选择模型"""
        # 根据任务类型和优先级选择模型
        model_mapping = {
            "cognitive_training": "glm-4-flash",
            "problem_analysis": "glm-4-plus",
            "capability_assessment": "glm-4-plus",
            "code_analysis": "codegeex-4",
            "search": "search-pro"
            "visualization": "glm-image"
            "embedding": "embedding-3"
        }
        
        if task_type in model_mapping:
            base_model = model_mapping[task_type]
        else:
            base_model = self.model_manager.recommend_model(task_type, priority)
        
        return base_model
    
    def create_model_call(self, model_name: str, prompt: str) -> str:
        """创建模型调用（需要实际的API集成）"""
        # TODO: 集成实际的GLM API调用
        # 这里返回模拟输出
        model_config = self.model_manager.get_model(model_name)
        return f"[AI调用 - {model_name}]\n{prompt}"


class PlannerAgent(BaseAgent):
    """规划智能体 - 负责任务分解和规划"""
    
    def __init__(self, agent_id: str, model_manager):
        super().__init__(agent_id, AgentRole.PLANNER, model_manager)
        self.task_queue = []
    
    async def process_message(self, message: Message) -> Optional[Message]:
        """处理规划请求"""
        if message.type == MessageType.TASK:
            task = message.content
            subtasks = await self.decompose_task(task)
            
            # 返回规划结果
            return Message(
                id=f"plan_{datetime.now().timestamp()}",
                from_agent=self.agent_id,
                to_agent=message.from_agent,
                type=MessageType.RESULT,
                content=subtasks,
                metadata={"task_id": task.id}
            )
        
        return None
    
    async def execute_task(self, task: Task) -> Any:
        """执行规划任务"""
        # 生成执行计划
        plan = await self.create_execution_plan(task)
        
        # 存储计划
        self.memory.store(f"plan_{task.id}", plan, "long_term")
        
        return plan
    
    async def decompose_task(self, task: Task) -> List[Task]:
        """分解任务"""
        # 使用AI辅助任务分解
        prompt = f"""
        分解以下任务为子任务：

任务：{task.description}
任务类型：{task.type}

请提供：
1. 子任务列表（每个包含描述、预期时间）
2. 子任务之间的依赖关系
3. 执行顺序

请以JSON格式输出。
"""
        
        model_name = self.choose_model("task_planning", "deep")
        result = self.create_model_call(model_name, prompt)
        
        # TODO: 解析AI返回的JSON
        # 这里返回模拟的子任务
        subtasks = [
            Task(
                id=f"{task.id}_1",
                type=task.type,
                description=f"子任务1: {task.description}",
                priority=task.priority,
                dependencies=[],
                metadata={"parent_task": task.id}
            ),
            Task(
                id=f"{task.id}_2",
                type=task.type,
                description=f"子任务2: 验证{task.description}",
                priority=task.priority,
                dependencies=[f"{task.id}_1"],
                metadata={"parent_task": task.id}
            )
        ]
        
        return subtasks
    
    async def create_execution_plan(self, task: Task) -> Dict[str, Any]:
        """创建执行计划"""
        plan = {
            "task_id": task.id,
            "description": task.description,
            "steps": [],
            "estimated_time": 0,
            "resources": []
        }
        
        # 添加步骤
        plan["steps"] = [
            {"step": 1, "action": "分析任务", "agent": "analyzer"},
            {"step": 2, "action": "执行任务", "agent": "executor"},
            {"step": 3, "action": "验证结果", "agent": "analyzer"}
        ]
        
        return plan


class ExecutorAgent(BaseAgent):
    """执行智能体 - 负责具体任务执行"""
    
    def __init__(self, agent_id: str, model_manager):
        super().__init__(agent_id, AgentRole.EXECUTOR, model_manager)
        self.active_tasks = {}
    
    async def process_message(self, message: Message) -> Optional[Message]:
        """处理执行请求"""
        if message.type == MessageType.REQUEST:
            task = message.content
            result = await self.execute_task(task)
            
            return Message(
                id=f"exec_{datetime.now().timestamp()}",
                from_agent=self.agent_id,
                to_agent=message.from_agent,
                type=MessageType.RESULT,
                content=result,
                metadata={"task_id": task.id}
            )
        
        return None
    
    async def execute_task(self, task: Task) -> Any:
        """执行任务"""
        # 标记为进行中
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        self.active_tasks[task.id] = task
        
        try:
            # 根据任务类型执行
            if task.type == "cognitive_training":
                result = await self.execute_cognitive_training(task)
            elif task.type == "problem_definition":
                result = await self.execute_problem_definition(task)
            elif task.type == "capability_assessment":
                result = await self.execute_capability_assessment(task)
            else:
                result = {"error": f"Unknown task type: {task.type}"}
            
            # 标记为完成
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.progress = 1.0
            task.result = result
            
            return result
            
        except Exception as e:
            # 标记为失败
            task.status = TaskStatus.FAILED
            task.error = str(e)
            return {"error": str(e)}
    
    async def execute_cognitive_training(self, task: Task) -> Dict[str, Any]:
        """执行认知训练任务"""
        # 导入认知训练工具
        import sys
        sys.path.append("ai-tools/workflows")
        from daily_cognitive_trainer import DailyCognitiveTrainer
        
        trainer = DailyCognitiveTrainer()
        
        # 执行训练
        input_text = task.description
        results = trainer.full_training(input_text)
        
        return {
            "type": "cognitive_training",
            "input": input_text,
            "results": results
        }
    
    async def execute_problem_definition(self, task: Task) -> Dict[str, Any]:
        """执行问题定义任务"""
        import sys
        sys.path.append("ai-tools/workflows")
        from problem_definition_assistant import ProblemDefinitionAssistant
        
        assistant = ProblemDefinitionAssistant()
        
        # 执行分析
        results = assistant.full_definition(task.description)
        
        return {
            "type": "problem_definition",
            "problem": task.description,
            "results": results
        }
    
    async def execute_capability_assessment(self, task: Task) -> Dict[str, Any]:
        """执行能力评估任务"""
        import sys
        sys.path.append("ai-tools/workflows")
        from capability_assessment import CapabilityAssessmentAssistant
        
        assistant = CapabilityAssessmentAssistant()
        
        # 执行评估
        if "responses" in task.metadata:
            results = assistant.assess_capability(
                task.type,
                task.metadata["responses"]
            )
        else:
            results = {"error": "No responses provided"}
        
        return {
            "type": "capability_assessment",
            "capability": task.type,
            "results": results
        }


class AnalyzerAgent(BaseAgent):
    """分析智能体 - 负责深度分析和洞察"""
    
    def __init__(self, agent_id: str, model_manager):
        super().__init__(agent_id, AgentRole.ANALYZER, model_manager)
    
    async def process_message(self, message: Message) -> Optional[Message]:
        """处理分析请求"""
        if message.type == MessageType.REQUEST:
            task = message.content
            result = await self.analyze(task)
            
            return Message(
                id=f"analysis_{datetime.now().timestamp()}",
                from_agent=self.agent_id,
                to_agent=message.from_agent,
                type=MessageType.RESULT,
                content=result,
                metadata={"task_id": task.id}
            )
        
        return None
    
    async def execute_task(self, task: Task) -> Any:
        """执行分析任务"""
        # 根据任务类型分析
        if task.type == "deep_analysis":
            result = await self.deep_analyze(task)
        elif task.type == "capability_analysis":
            result = await self.analyze_capabilities(task)
        elif task.type == "trend_analysis":
            result = await self.analyze_trends(task)
        else:
            result = {"error": f"Unknown analysis type: {task.type}"}
        
        return result
    
    async def deep_analyze(self, task: Task) -> Dict[str, Any]:
        """深度分析"""
        # 使用AI辅助深度分析
        prompt = f"""
        对以下内容进行深度分析：

内容：{task.description}

请从以下维度分析：
1. 核心要点是什么？
2. 有什么隐含假设？
3. 有什么风险？
4. 有什么机会？
5. 有什么建议？

请提供详细的分析报告。
"""
        
        model_name = self.choose_model("deep_analysis", "deep")
        result = self.create_model_call(model_name, prompt)
        
        return {
            "type": "deep_analysis",
            "content": task.description,
            "analysis": result
        }
    
    async def analyze_capabilities(self, task: Task) -> Dict[str, Any]:
        """分析能力"""
        prompt = f"""
        分析以下能力相关内容：

内容：{task.description}

请分析：
1. 涉及哪些能力？
2. 能力水平如何？
3. 有哪些提升空间？
4. 有哪些改进建议？

请提供详细的能力分析。
"""
        
        model_name = self.choose_model("capability_analysis", "deep")
        result = self.create_model_call(model_name, prompt)
        
        return {
            "type": "capability_analysis",
            "content": task.description,
            "analysis": result
        }
    
    async def analyze_trends(self, task: Task) -> Dict[str, Any]:
        """分析趋势"""
        prompt = f"""
        分析以下内容中的趋势：

内容：{task.description}

请分析：
1. 有什么发展趋势？
2. 有什么关键转折点？
3. 有什么模式？
4. 有什么预测？

请提供详细的趋势分析。
"""
        
        model_name = self.choose_model("trend_analysis", "deep")
        result = self.create_model_call(model_name, prompt)
        
        return {
            "type": "trend_analysis",
            "content": task.description,
            "trend_analysis": result
        }


class CoordinatorAgent(BaseAgent):
    """协调智能体 - 协调其他智能体的工作"""
    
    def __init__(self, agent_id: str, model_manager):
        super().__init__(agent_id, AgentRole.COORDINATOR, model_manager)
        self.agents = {}  # agent_id -> agent
    
    def register_agent(self, agent: BaseAgent):
        """注册智能体"""
        self.agents[agent.agent_id] = agent
    
    async def process_message(self, message: Message) -> Optional[Message]:
        """处理协调请求"""
        if message.type == MessageType.TASK:
            task = message.content
            
            # 创建任务规划
            planner = self.agents.get("planner")
            if planner:
                plan = await planner.execute_task(task)
                
                # 分配子任务
                for subtask in plan.get("steps", []):
                    # 发送子任务给相应的智能体
                    agent_id = subtask.get("agent")
                    agent = self.agents.get(agent_id)
                    if agent:
                        await self.send_to_agent(agent_id, subtask)
                
                return Message(
                    id=f"coord_{datetime.now().timestamp()}",
                    from_agent=self.agent_id,
                    to_agent=message.from_agent,
                    type=MessageType.NOTIFICATION,
                    content="任务已分配",
                    metadata={"task_id": task.id, "plan": plan}
                )
        
        return None
    
    async def send_to_agent(self, agent_id: str, task: Any):
        """发送任务给智能体"""
        agent = self.agents.get(agent_id)
        if agent:
            await agent.message_queue.put(Message(
                id=f"task_{datetime.now().timestamp()}",
                from_agent=self.agent_id,
                to_agent=agent_id,
                type=MessageType.TASK,
                content=task
            ))
    
    async def execute_task(self, task: Task) -> Any:
        """执行协调任务"""
        # 协调任务就是协调其他智能体
        # 具体实现在 process_message 中
        return {"status": "coordinated"}
    
    async def broadcast(self, message: Message):
        """广播消息给所有智能体"""
        for agent_id, agent in self.agents.items():
            if agent_id != self.agent_id:
                await agent.message_queue.put(message)
    
    async def collect_results(self, task_id: str) -> List[Message]:
        """收集任务结果"""
        results = []
        for agent_id, agent in self.agents.items():
            if agent_id != self.agent_id:
                # 检查智能体的工作记忆
                result = agent.memory.retrieve(f"task_{task_id}_result", "working")
                if result:
                    results.append(result)
        return results


class ResearcherAgent(BaseAgent):
    """研究智能体 - 负责信息收集和检索"""
    
    def __init__(self, agent_id: str, model_manager):
        super().__init__(agent_id, AgentRole.RESEARCHER, model_manager)
    
    async def process_message(self, message: Message) -> Optional[Message]:
        """处理研究请求"""
        if message.type == MessageType.REQUEST:
            query = message.content.get("query", "")
            
            # 执行搜索
            results = await self.search(query, message.metadata)
            
            return Message(
                id=f"search_{datetime.now().timestamp()}",
                from_agent=self.agent_id,
                to_agent=message.from_agent,
                type=MessageType.RESULT,
                content=results,
                metadata={"query": query}
            )
        
        return None
    
    async def execute_task(self, task: Task) -> Any:
        """执行研究任务"""
        query = task.description
        
        # 搜索
        results = await self.search(query, task.metadata)
        
        return {
            "type": "research",
            "query": query,
            "results": results
        }
    
    async def search(self, query: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行搜索"""
        metadata = metadata or {}
        search_type = metadata.get("search_type", "general")
        
        # 使用AI模型进行搜索
        if search_type == "literature":
            prompt = f"""
            搜索关于以下主题的文献：

主题：{query}

请提供：
1. 相关论文（标题、作者、年份）
2. 核心贡献
3. 推荐阅读顺序

请提供5-10篇相关文献。
"""
            model_name = "search-pro"
        elif search_type == "case":
            prompt = f"""
            搜索关于以下主题的案例：

主题：{query}

请提供：
1. 相关案例
2. 案例背景
3. 解决方案
4. 关键要点

请提供3-5个相关案例。
"""
            model_name = "search-pro"
        else:
            prompt = f"""
            搜索关于以下主题的信息：

主题：{query}

请提供：
1. 核心概念
2. 关键要点
3. 相关资源
4. 建议的后续探索方向

请提供详细的搜索结果。
"""
            model_name = self.choose_model("search", "balanced")
        
        result = self.create_model_call(model_name, prompt)
        
        # 存储搜索结果
        self.memory.store(f"search_{hash(query)}", result, "long_term")
        
        return {
            "type": "search",
            "query": query,
            "search_type": search_type,
            "results": result
        }


class TrainerAgent(BaseAgent):
    """训练智能体 - 负责训练和能力提升"""
    
    def __init__(self, agent_id: str, model_manager):
        super().__init__(agent_id, AgentRole.TRAINER, model_manager)
        self.training_history = []
    
    async def process_message(self, message: Message) -> Optional[Message]:
        """处理训练请求"""
        if message.type == MessageType.REQUEST:
            training_request = message.content
            
            # 执行训练
            result = await self.create_training_plan(training_request)
            
            return Message(
                id=f"training_{datetime.now().timestamp()}",
                from_agent=self.agent_id,
                to_agent=message.from_agent,
                type= MessageType.RESULT,
                content=result,
                metadata={"training_request": training_request}
            )
        
        return None
    
    async def execute_task(self, task: Task) -> Any:
        """执行训练任务"""
        training_plan = task.metadata.get("training_plan")
        
        if training_plan:
            # 执行训练计划
            results = await self.execute_training_plan(training_plan)
            
            return {
                "type": "training",
                "plan": training_plan,
                "results": results
            }
        else:
            return {"error": "No training plan provided"}
    
    async def create_training_plan(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """创建训练计划"""
        capability = request.get("capability", "")
        current_level = request.get("current_level", 5)
        target_level = request.get("target_level", 8)
        timeframe = request.get("timeframe", "1 month")
        
        prompt = f"""
        为以下能力创建训练计划：

能力：{capability}
当前水平：{current_level}/10
目标水平：{target_level}/10
时间范围：{timeframe}

请提供：
1. 阶段分解（第1周、第2周等）
2. 每阶段的目标
3. 每天的练习内容（10-15分钟）
4. 关键里程碑
5. 评估方法

请提供详细的训练计划。
"""
        
        model_name = self.choose_model("training_planning", "deep")
        result = self.create_model_call(model_name, prompt)
        
        return {
            "capability": capability,
            "current_level": current_level,
            "target_level": target_level,
            "timeframe": timeframe,
            "plan": result
        }
    
    async def execute_training_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行训练计划"""
        # 导入训练工具
        import sys
        sys.path.append("ai-tools/workflows")
        from daily_cognitive_trainer import DailyCognitiveTrainer
        
        trainer = DailyCognitiveTrainer()
        
        # 记录训练历史
        self.training_history.append({
            "plan": plan,
            "timestamp": datetime.now().isoformat()
        })
        
        # 执行每日训练
        # 这里简化处理，实际应该每天执行
        results = []
        
        return {
            "type": "training_execution",
            "plan": plan,
            "history": self.training_history
        }
    
    async def get_training_summary(self) -> Dict[str, Any]:
        """获取训练总结"""
        summary = {
            "total_trainings": len(self.training_history),
            "history": self.training_history
        }
        return summary


class AIAgentSystem:
    """AI智能体系统"""
    
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.agents = {}
        self.message_bus = asyncio.Queue()
        self.task_queue = asyncio.Queue()
        self.is_running = False
        
        # 初始化智能体
        self._init_agents()
    
    def _init_agents(self):
        """初始化所有智能体"""
        # 创建智能体
        self.agents["planner"] = PlannerAgent("planner_001", self.model_manager)
        self.agents["executor"] = ExecutorAgent("executor_001", self.model_manager)
        self.agents["analyzer"] = AnalyzerAgent("analyzer_001", self.model_manager)
        self.agents["coordinator"] = CoordinatorAgent("coordinator_001", self.model_manager)
        self.agents["researcher"] = ResearcherAgent("researcher_001", self.model_manager)
        self.agents["trainer"] = TrainerAgent("trainer_001", self.model_manager)
        
        # 注册智能体到协调器
        coordinator = self.agents["coordinator"]
        for agent_id, agent in self.agents.items():
            if agent_id != "coordinator":
                coordinator.register_agent(agent)
    
    async def start(self):
        """启动系统"""
        self.is_running = True
        
        # 启动所有智能体
        tasks = [agent.start() for agent in self.agents.values()]
        await asyncio.gather(*tasks)
    
    async def stop(self):
        """停止系统"""
        self.is_running = False
        
        # 停止所有智能体
        tasks = [agent.stop() for agent in self.agents.values()]
        await asyncio.gather(*tasks)
    
    async def submit_task(self, task: Dict[str, Any]) -> str:
        """提交任务"""
        task_obj = Task(
            id=f"task_{datetime.now().timestamp()}",
            type=task.get("type", "general"),
            description=task.get("description", ""),
            priority=task.get("priority", 5),
            metadata=task.get("metadata", {})
        )
        
        # 添加到任务队列
        await self.task_queue.put(task_obj)
        
        # 通知协调器有新任务
        coordinator = self.agents["coordinator"]
        await coordinator.message_queue.put(Message(
            id=f"new_task_{datetime.now().timestamp()}",
            from_agent="system",
            to_agent="coordinator",
            type=MessageType.TASK,
            content=task_obj
        ))
        
        return task_obj.id
    
    async def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        status = {
            "is_running": self.is_running,
            "agents": {},
            "tasks_in_queue": self.task_queue.qsize()
        }
        
        # 收集所有智能体的状态
        for agent_id, agent in self.agents.items():
            status["agents"][agent_id] = {
                "role": agent.role.value,
                "is_running": agent.is_running,
                "memory": {
                    "short_term": len(agent.memory.short_term),
                    "long_term": len(agent.memory.long_term),
                    "working": len(agent.memory.working_memory)
                }
            }
        
        return status
    
    async def query(self, query: str, agent_type: str = "analyzer") -> Dict[str, Any]:
        """查询系统"""
        agent = self.agents.get(agent_type)
        if agent:
            await agent.message_queue.put(Message(
                id=f"query_{datetime.now().timestamp()}",
                from_agent="user",
                to_agent=agent.agent_id,
                type=MessageType.REQUEST,
                content={"query": query}
            ))
            
            # 等待结果
            # 在实际实现中，应该有更复杂的等待机制
            return {"status": "query_submitted", "agent": agent_type, "query": query}
        else:
            return {"error": f"Agent {agent_type} not found"}
    
    async def chat(self, message: str) -> str:
        """与系统对话"""
        # 分析用户消息
        analysis_result = await self.query(message, "analyzer")
        
        # 生成响应
        response = f"""
{message}

分析结果：
{analysis_result.get('results', 'No analysis available')}

需要我帮你做什么？
1. 进行每日认知训练
2. 定义一个问题
3. 评估一个能力
4. 搜索文献或案例
5. 制定训练计划

请告诉我你的选择。
"""
        
        return response


async def main():
    """测试AI智能体系统"""
    from glm_models import GLMModelManager
    
    # 创建系统
    model_manager = GLMModelManager()
    system = AIAgentSystem(model_manager)
    
    print("="*80)
    print("AI智能体系统")
    print("="*80)
    print()
    
    # 启动系统
    print("启动系统...")
    await system.start()
    
    # 等待用户输入
    print("系统已启动，输入 'exit' 退出")
    print()
    
    while True:
        user_input = input("> ")
        
        if user_input.lower() == 'exit':
            break
        
        # 发送到系统
        response = await system.chat(user_input)
        print(response)


if __name__ == "__main__":
    print("AI智能体系统模块")
    print("请使用 main.py 启动完整的智能体系统")
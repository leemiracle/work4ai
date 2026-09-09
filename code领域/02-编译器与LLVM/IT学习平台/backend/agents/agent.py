"""Agent Framework - Base Agent and Core Functionality."""

from typing import Dict, Any, List, Optional, Callable, AsyncIterator
from abc import ABC, abstractmethod
from datetime import datetime
import json
from pydantic import BaseModel
from .memory import MemorySystem
from .tools import ToolRegistry
from .llm import LLMService
from .config import AISettings


class Message(BaseModel):
    """Agent communication message."""

    id: str
    sender: str
    receiver: str
    type: str  # 'request', 'response', 'notification', 'error'
    content: Dict[str, Any]
    timestamp: datetime
    priority: str = "medium"  # 'high', 'medium', 'low'


class AgentState(BaseModel):
    """Agent state representation."""

    agent_name: str
    status: str  # 'idle', 'busy', 'error', 'stopped'
    current_task: Optional[str]
    memory_keys: List[str]
    tool_usage: Dict[str, int]
    total_tasks_completed: int
    last_activity: datetime
    metrics: Dict[str, Any]


class ToolCall(BaseModel):
    """Tool execution record."""

    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[Any]
    error: Optional[str]
    duration_ms: float
    timestamp: datetime


class Agent(ABC):
    """Base Agent class - all agents inherit from this."""

    def __init__(
        self,
        name: str,
        description: str,
        llm_service: Optional[LLMService] = None,
        memory_system: Optional[MemorySystem] = None,
        tool_registry: Optional[ToolRegistry] = None,
        settings: Optional[AISettings] = None
    ):
        self.name = name
        self.description = description
        self.settings = settings or AISettings()

        # Services
        self.llm_service = llm_service or LLMService(settings)
        self.memory = memory_system or MemorySystem(settings)
        self.tools = tool_registry or ToolRegistry()

        # State
        self.state = AgentState(
            agent_name=name,
            status="idle",
            current_task=None,
            memory_keys=[],
            tool_usage={},
            total_tasks_completed=0,
            last_activity=datetime.utcnow(),
            metrics={}
        )

        # Message handling
        self.message_handlers: Dict[str, Callable] = {}
        self._setup_message_handlers()

        # Tool calls history
        self.tool_history: List[ToolCall] = []

        # Initialize agent
        self.initialize()

    @abstractmethod
    def initialize(self):
        """Initialize the agent with default setup."""
        pass

    @abstractmethod
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return result."""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        pass

    def _setup_message_handlers(self):
        """Setup default message handlers."""
        self.register_handler("status", self._handle_status)
        self.register_handler("stop", self._handle_stop)
        self.register_handler("metrics", self._handle_metrics)

    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler."""
        self.message_handlers[message_type] = handler

    async def send_message(
        self,
        receiver: str,
        message_type: str,
        content: Dict[str, Any],
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """Send a message to another agent."""
        message = Message(
            id=self._generate_message_id(),
            sender=self.name,
            receiver=receiver,
            type=message_type,
            content=content,
            timestamp=datetime.utcnow(),
            priority=priority
        )
        # Message would be sent through message bus
        return {"message": message.dict(), "status": "sent"}

    async def receive_message(self, message: Message) -> Optional[Dict[str, Any]]:
        """Receive and handle a message."""
        handler = self.message_handlers.get(message.type)
        if handler:
            try:
                return await handler(message)
            except Exception as e:
                return {"error": str(e), "message_id": message.id}
        return {"error": f"No handler for message type: {message.type}"}

    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """Call a tool and record the call."""
        start_time = datetime.utcnow()

        try:
            tool = self.tools.get_tool(tool_name)
            result = await tool.execute(parameters)

            # Record successful call
            self.tool_history.append(ToolCall(
                tool_name=tool_name,
                parameters=parameters,
                result=result,
                error=None,
                duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                timestamp=start_time
            ))

            # Update tool usage
            self.state.tool_usage[tool_name] = self.state.tool_usage.get(tool_name, 0) + 1
            self.state.last_activity = datetime.utcnow()

            return result
        except Exception as e:
            # Record failed call
            self.tool_history.append(ToolCall(
                tool_name=tool_name,
                parameters=parameters,
                result=None,
                error=str(e),
                duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                timestamp=start_time
            ))

            raise

    async def think(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[str]] = None
    ) -> str:
        """Use LLM to think/reason."""
        system_prompt = self._get_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]

        if context:
            messages.append({"role": "system", "content": f"Context: {json.dumps(context, ensure_ascii=False)}"})

        if tools:
            tools_info = [self.tools.get_tool(t).describe() for t in tools if self.tools.has_tool(t)]
            messages.append({"role": "system", "content": f"Available tools: {json.dumps(tools_info, ensure_ascii=False)}"})

        messages.append({"role": "user", "content": prompt})

        response = await self.llm_service.chat(messages)
        return response

    async def plan(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Plan steps to achieve a goal."""
        prompt = f"""Plan steps to achieve the goal: {goal}

Context: {json.dumps(context or {}, ensure_ascii=False)}

Break down the goal into specific, executable steps.
For each step, specify:
- step_number
- description
- required_tools (list of tool names)
- estimated_time (in minutes)

Return as JSON array of steps."""

        response = await self.think(prompt, context)

        try:
            steps = json.loads(response)
            return steps if isinstance(steps, list) else []
        except json.JSONDecodeError:
            return []

    async def execute_plan(
        self,
        plan: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute a plan step by step."""
        results = []

        for step in plan:
            try:
                result = await self._execute_step(step)
                results.append({
                    "step": step,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "step": step,
                    "status": "error",
                    "error": str(e)
                })
                # Decide whether to continue or stop
                if step.get("critical", False):
                    break

        return results

    async def _execute_step(self, step: Dict[str, Any]) -> Any:
        """Execute a single step."""
        description = step.get("description", "")
        required_tools = step.get("required_tools", [])

        # Use LLM to decide how to execute
        prompt = f"""Execute this step: {description}

Available tools: {required_tools}

Decide which tools to call and with what parameters.
Return your plan as JSON with 'tool' and 'parameters' keys."""

        decision = await self.think(prompt)

        try:
            decision_json = json.loads(decision)
            tool_name = decision_json.get("tool")
            parameters = decision_json.get("parameters", {})

            if tool_name and self.tools.has_tool(tool_name):
                result = await self.call_tool(tool_name, parameters)
                return result
            else:
                return {"error": "Tool not found or not specified"}
        except json.JSONDecodeError:
            return {"error": "Could not parse decision"}

    def _get_system_prompt(self) -> str:
        """Get system prompt for this agent."""
        return f"""You are {self.name}, a specialized AI agent.

Description: {self.description}

Capabilities:
{chr(10).join(f'- {cap}' for cap in self.get_capabilities())}

Use your tools to complete tasks efficiently.
Think step by step before taking action."""

    def _generate_message_id(self) -> str:
        """Generate unique message ID."""
        return f"{self.name}_{int(datetime.utcnow().timestamp() * 1000000)}"

    async def _handle_status(self, message: Message) -> Dict[str, Any]:
        """Handle status request."""
        return self.state.dict()

    async def _handle_stop(self, message: Message) -> Dict[str, Any]:
        """Handle stop request."""
        self.state.status = "stopped"
        return {"status": "stopped", "message": f"Agent {self.name} stopped"}

    async def _handle_metrics(self, message: Message) -> Dict[str, Any]:
        """Handle metrics request."""
        return {
            "agent_name": self.name,
            "metrics": self.state.metrics,
            "tool_usage": self.state.tool_usage,
            "tool_history_count": len(self.tool_history),
            "total_tasks_completed": self.state.total_tasks_completed
        }

    def get_state(self) -> AgentState:
        """Get current agent state."""
        return self.state

    def get_tool_history(self) -> List[ToolCall]:
        """Get tool call history."""
        return self.tool_history

    def reset(self):
        """Reset agent state."""
        self.state.status = "idle"
        self.state.current_task = None
        self.tool_history = []


class ReActAgent(Agent):
    """ReAct (Reasoning + Acting) Agent - thinks before acting."""

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process task using ReAct pattern."""
        self.state.status = "busy"
        self.state.current_task = task.get("task_id", "unknown")
        self.state.last_activity = datetime.utcnow()

        try:
            # Step 1: Understand the task
            understanding = await self.think(f"Understand this task: {json.dumps(task, ensure_ascii=False)}")

            # Step 2: Plan
            plan = await self.plan(task.get("goal", ""), task.get("context"))

            # Step 3: Execute
            execution_results = await self.execute_plan(plan)

            # Step 4: Evaluate and reflect
            reflection = await self.think(
                f"Reflect on execution results: {json.dumps(execution_results, ensure_ascii=False)}"
            )

            # Step 5: Generate final response
            response = await self.think(
                f"Generate final response based on: understanding={understanding}, execution={json.dumps(execution_results, ensure_ascii=False)}, reflection={reflection}"
            )

            self.state.status = "idle"
            self.state.total_tasks_completed += 1

            return {
                "status": "success",
                "response": response,
                "understanding": understanding,
                "plan": plan,
                "execution": execution_results,
                "reflection": reflection
            }

        except Exception as e:
            self.state.status = "error"
            return {
                "status": "error",
                "error": str(e)
            }


class ReflexionAgent(Agent):
    """Agent with self-reflection capability."""

    async def reflect_on_action(
        self,
        action: Dict[str, Any],
        result: Dict[str, Any],
        outcome: str
    ) -> Dict[str, Any]:
        """Reflect on a past action."""
        prompt = f"""Reflect on this action and its outcome:

Action: {json.dumps(action, ensure_ascii=False)}
Result: {json.dumps(result, ensure_ascii=False)}
Outcome: {outcome}

Provide:
1. What worked well
2. What didn't work
3. What could be improved
4. Lessons learned

Return as JSON."""

        reflection = await self.think(prompt)

        try:
            reflection_json = json.loads(reflection)
            # Store in memory for future reference
            await self.memory.store(
                f"reflection_{self._generate_message_id()}",
                reflection_json
            )
            return reflection_json
        except json.JSONDecodeError:
            return {"reflection": reflection}

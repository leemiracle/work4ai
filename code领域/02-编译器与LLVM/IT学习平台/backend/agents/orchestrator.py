"""Agent Orchestrator - Coordinates multiple agents."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio
from .agent import Agent, Message
from .config import AISettings


class Task:
    """Task representation for orchestration."""

    def __init__(
        self,
        task_id: str,
        goal: str,
        context: Dict[str, Any],
        priority: str = "medium",
        deadline: Optional[datetime] = None
    ):
        self.task_id = task_id
        self.goal = goal
        self.context = context
        self.priority = priority
        self.deadline = deadline
        self.status = "pending"  # 'pending', 'in_progress', 'completed', 'failed'
        self.subtasks: List[Dict[str, Any]] = []
        self.dependencies: List[str] = []
        self.assigned_to: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class Orchestrator:
    """Coordinates multiple agents to complete complex tasks."""

    def __init__(
        self,
        settings: Optional[AISettings] = None
    ):
        self.settings = settings or AISettings()
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.message_bus: List[Message] = []
        self.execution_history: List[Dict[str, Any]] = []

    def register_agent(self, agent: Agent):
        """Register an agent."""
        self.agents[agent.name] = agent

    def unregister_agent(self, agent_name: str):
        """Unregister an agent."""
        if agent_name in self.agents:
            del self.agents[agent_name]

    def get_available_agents(self) -> List[str]:
        """Get list of available agents."""
        return [name for name, agent in self.agents.items() if agent.state.status != "stopped"]

    async def create_task(
        self,
        goal: str,
        context: Dict[str, Any],
        priority: str = "medium",
        deadline: Optional[datetime] = None
    ) -> Task:
        """Create and decompose a task."""
        task_id = self._generate_task_id()

        task = Task(
            task_id=task_id,
            goal=goal,
            context=context,
            priority=priority,
            deadline=deadline
        )

        self.tasks[task_id] = task

        # Decompose task
        await self._decompose_task(task)

        return task

    async def execute_task(
        self,
        task_id: str,
        execution_mode: str = "sequential"  # 'sequential', 'parallel', 'hybrid'
    ) -> Dict[str, Any]:
        """Execute a task by coordinating agents."""
        task = self.tasks.get(task_id)

        if not task:
            return {"error": f"Task {task_id} not found"}

        task.status = "in_progress"
        task.updated_at = datetime.utcnow()

        execution_record = {
            "task_id": task_id,
            "goal": task.goal,
            "mode": execution_mode,
            "started_at": datetime.utcnow().isoformat(),
            "steps": [],
            "final_result": None
        }

        try:
            if execution_mode == "sequential":
                result = await self._execute_sequential(task, execution_record)
            elif execution_mode == "parallel":
                result = await self._execute_parallel(task, execution_record)
            elif execution_mode == "hybrid":
                result = await self._execute_hybrid(task, execution_record)
            else:
                raise ValueError(f"Unknown execution mode: {execution_mode}")

            task.status = "completed"
            execution_record["final_result"] = result
            execution_record["status"] = "success"

        except Exception as e:
            task.status = "failed"
            execution_record["error"] = str(e)
            execution_record["status"] = "failed"

        finally:
            execution_record["completed_at"] = datetime.utcnow().isoformat()
            self.execution_history.append(execution_record)
            task.updated_at = datetime.utcnow()

        return execution_record

    async def _execute_sequential(self, task: Task, record: Dict) -> Any:
        """Execute task sequentially."""
        results = []

        for subtask in task.subtasks:
            if not self._can_execute_subtask(subtask):
                continue

            result = await self._execute_subtask(subtask)
            results.append(result)
            record["steps"].append({
                "subtask": subtask,
                "result": result
            })

        return {"results": results}

    async def _execute_parallel(self, task: Task, record: Dict) -> Any:
        """Execute independent subtasks in parallel."""
        # Filter tasks that can be executed now
        executable_subtasks = [st for st in task.subtasks if self._can_execute_subtask(st)]

        # Execute in parallel
        tasks = [self._execute_subtask(st) for st in executable_subtasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            record["steps"].append({
                "subtask": executable_subtasks[i],
                "result": result if not isinstance(result, Exception) else str(result)
            })

        return {"results": results}

    async def _execute_hybrid(self, task: Task, record: Dict) -> Any:
        """Execute task with hybrid sequential/parallel approach."""
        # Group independent tasks for parallel execution
        task_groups = self._group_dependent_tasks(task.subtasks)

        results = []

        for group in task_groups:
            if len(group) > 1:
                # Parallel execution
                parallel_results = await self._execute_parallel(
                    Task(task.subtasks[0]["task_id"], task.goal, task.context),
                    {"steps": []}
                )
                results.extend(parallel_results["results"])
            else:
                # Sequential execution
                result = await self._execute_subtask(group[0])
                results.append(result)

        return {"results": results}

    async def _execute_subtask(self, subtask: Dict[str, Any]) -> Any:
        """Execute a single subtask."""
        agent_name = subtask.get("agent")
        agent = self.agents.get(agent_name)

        if not agent:
            raise Exception(f"Agent {agent_name} not found")

        # Execute subtask
        result = await agent.process({
            "task_id": subtask["task_id"],
            "goal": subtask["goal"],
            "context": subtask.get("context", {})
        })

        return result

    async def _decompose_task(self, task: Task):
        """Decompose a task into subtasks using AI."""
        # Get available agents and their capabilities
        available_agents = self.get_available_agents()
        agent_capabilities = {
            name: agent.get_capabilities()
            for name, agent in self.agents.items()
        }

        # Use LLM to decompose task
        prompt = f"""Decompose this task into executable subtasks:

Task Goal: {task.goal}

Context: {json.dumps(task.context, ensure_ascii=False)}

Available Agents and Capabilities:
{json.dumps(agent_capabilities, ensure_ascii=False)}

For each subtask, specify:
- subtask_id
- description
- goal
- required_agent (must be from available agents)
- context (any additional context)
- dependencies (other subtask_ids that must complete first)

Return as JSON array of subtasks."""

        from .agent import Agent  # Import here to avoid circular dependency
        from .llm import LLMService

        llm = LLMService(self.settings)
        response = await llm.chat([{"role": "system", "content": "You are a task decomposition expert."},
                                    {"role": "user", "content": prompt}])

        try:
            subtasks = json.loads(response)
            task.subtasks = subtasks
        except json.JSONDecodeError:
            # Fallback: create a single subtask
            task.subtasks = [{
                "task_id": f"{task.task_id}_subtask_1",
                "description": "Complete the main task",
                "goal": task.goal,
                "required_agent": available_agents[0] if available_agents else "unknown",
                "context": task.context,
                "dependencies": []
            }]

    def _can_execute_subtask(self, subtask: Dict[str, Any]) -> bool:
        """Check if subtask can be executed (dependencies met)."""
        dependencies = subtask.get("dependencies", [])
        return all(self._is_dependency_completed(dep) for dep in dependencies)

    def _is_dependency_completed(self, dependency_id: str) -> bool:
        """Check if a dependency task is completed."""
        for task in self.tasks.values():
            if task.task_id == dependency_id and task.status == "completed":
                return True
        return False

    def _group_dependent_tasks(self, subtasks: List[Dict[str, Any]]) -> List[List[Dict]]:
        """Group subtasks by dependencies."""
        # Simple implementation: find independent tasks
        groups = []
        remaining = subtasks.copy()

        while remaining:
            # Find tasks with no unmet dependencies
            independent = [st for st in remaining if self._can_execute_subtask(st)]

            if not independent:
                # Circular dependency or all tasks have dependencies
                # Break the cycle by taking the first task
                groups.append([remaining[0]])
                remaining = remaining[1:]
            else:
                groups.append(independent)
                for st in independent:
                    remaining.remove(st)

        return groups

    def _generate_task_id(self) -> str:
        """Generate unique task ID."""
        return f"task_{datetime.utcnow().timestamp() * 1000000}"

    async def broadcast_message(self, message: Message):
        """Broadcast message to all agents."""
        self.message_bus.append(message)

        tasks = []
        for agent_name, agent in self.agents.items():
            if agent_name != message.sender:  # Don't send to self
                task = asyncio.create_task(agent.receive_message(message))
                tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            "message_id": message.id,
            "recipients": list(self.agents.keys()),
            "results": results
        }

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a task."""
        task = self.tasks.get(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "goal": task.goal,
            "status": task.status,
            "progress": len([st for st in task.subtasks if self._is_dependency_completed(st.get("task_id", ""))]) / len(task.subtasks) if task.subtasks else 0,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks and their status."""
        return [self.get_task_status(task_id) for task_id in self.tasks.keys()]

    def get_execution_history(self, task_id: str = None) -> List[Dict[str, Any]]:
        """Get execution history."""
        if task_id:
            return [record for record in self.execution_history if record["task_id"] == task_id]
        return self.execution_history

    async def cleanup(self, max_age_hours: int = 24):
        """Clean up old tasks and execution history."""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)

        # Clean old tasks
        old_tasks = [tid for tid, task in self.tasks.items() if task.updated_at < cutoff]
        for tid in old_tasks:
            del self.tasks[tid]

        # Clean old execution history
        self.execution_history = [
            record for record in self.execution_history
            if datetime.fromisoformat(record["completed_at"]) > cutoff
        ]

        return {"cleaned_tasks": len(old_tasks), "remaining_tasks": len(self.tasks)}

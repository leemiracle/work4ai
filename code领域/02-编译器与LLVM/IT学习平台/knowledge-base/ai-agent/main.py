#!/usr/bin/env python3
"""
AI Agent主程序 - 完整的智能体系统
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import argparse

# 添加路径
sys.path.append("ai-tools/utils")
sys.path.append("ai-tools/workflows")

from glm_models import GLMModelManager


class SimpleAgent:
    """简化版智能体"""
    
    def __init__(self, agent_id, agent_type, model_manager):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.model_manager = model_manager
        self.memory = {}
        self.tasks = []
    
    async def process(self, input_data):
        """处理输入"""
        if self.agent_type == "trainer":
            return await self.handle_training(input_data)
        elif self.agent_type == "analyzer":
            return await self.handle_analysis(input_data)
        elif self.agent_type == "researcher":
            return await self.handle_research(input_data)
        elif self.agent_type == "planner":
            return await self.handle_planning(input_data)
        elif self.agent_type == "executor":
            return await self.handle_execution(input_data)
        else:
            return {"error": f"Unknown agent type: {self.agent_type}"}
    
    async def handle_training(self, input_data):
        """处理训练请求"""
        try:
            # 导入训练工具
            from daily_cognitive_trainer import DailyCognitiveTrainer
            
            trainer = DailyCognitiveTrainer()
            user_input = input_data.get("input", "")
            
            print(f"[{self.agent_id}] 开始每日认知训练...")
            
            # 执行训练
            results = trainer.full_training(user_input)
            
            return {
                "agent": self.agent_id,
                "type": "training",
                "input": user_input,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_analysis(self, input_data):
        """处理分析请求"""
        query = input_data.get("query", "")
        depth = input_data.get("depth", "medium")
        
        # 选择模型
        model_name = self.model_manager.recommend_model("深度分析", depth)
        
        prompt = f"""
        深度分析以下内容：

{query}

请从以下维度分析：
1. 核心要点
2. 关键洞察
3. 潜在风险
4. 改进建议

请提供详细的分析。
"""
        
        print(f"[{self.agent_id}] 使用模型: {model_name} 进行深度分析...")
        
        # 调用模型（模拟）
        result = f"[AI输出 - {model_name}]\n{prompt}"
        
        # 存储到记忆
        self.memory[f"analysis_{datetime.now().timestamp()}"] = result
        
        return {
            "agent": self.agent_id,
            "type": "analysis",
            "query": query,
            "result": result,
            "model": model_name,
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_research(self, input_data):
        """处理研究请求"""
        query = input_data.get("query", "")
        search_type = input_data.get("search_type", "general")
        
        # 选择模型
        if search_type == "literature":
            model_name = "search-pro"
        elif search_type == "case":
            model_name = "search-pro"
        else:
            model_name = self.model_manager.recommend_model("搜索", "balanced")
        
        prompt = f"""
        搜索关于以下主题的信息：

{query}

请提供：
1. 相关资源
2. 关键信息
3. 建议的探索方向
"""
        
        print(f"[{self.agent_id}] 使用模型: {model_name} 进行搜索...")
        
        # 调用模型（模拟）
        result = f"[AI输出 - {model_name}]\n{prompt}"
        
        return {
            "agent": self.agent_id,
            "type": "research",
            "query": query,
            "result": result,
            "model": model_name,
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_planning(self, input_data):
        """处理规划请求"""
        task = input_data.get("task", "")
        
        # 选择模型
        model_name = self.model_manager.recommend_model("任务规划", "deep")
        
        prompt = f"""
        为以下任务创建执行计划：

{task}

请提供：
1. 任务分解（子任务列表）
2. 每个子任务的步骤
3. 预计时间
4. 依赖关系
5. 里程碑

请提供详细的执行计划。
"""
        
        print(f"[{self.agent_id}] 使用模型: {model_name} 创建执行计划...")
        
        # 调用模型（模拟）
        result = f"[AI输出 - {model_name}]\n{prompt}"
        
        return {
            "agent": self.agent_id,
            "type": "planning",
            "task": task,
            "result": result,
            "model": model_name,
            "timestamp": datetime.now().isoformat()
        }
    
    async def handle_execution(self, input_data):
        """处理执行请求"""
        task = input_data.get("task", "")
        task_type = input_data.get("task_type", "general")
        
        print(f"[{self.agent_id}] 开始执行任务...")
        
        # 根据任务类型执行
        if task_type == "cognitive_training":
            try:
                from daily_cognitive_trainer import DailyCognitiveTrainer
                trainer = DailyCognitiveTrainer()
                results = trainer.full_training(task)
                return {
                    "agent": self.agent_id,
                    "type": "execution",
                    "task": task,
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return {"error": str(e)}
        elif task_type == "problem_definition":
            try:
                from problem_definition_assistant import ProblemDefinitionAssistant
                assistant = ProblemDefinitionAssistant()
                results = assistant.full_definition(task)
                return {
                    "agent": self.agent_id,
                    "type": "execution",
                    "task": task,
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return {"error": str(e)}
        else:
            return {
                "agent": self.agent_id,
                "type": "execution",
                "task": task,
                "result": f"已执行任务: {task}",
                "timestamp": datetime.now().isoformat()
            }


class AIAgentOrchestrator:
    """AI智能体协调器"""
    
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.agents = {}
        
        # 创建智能体
        self._init_agents()
    
    def _init_agents(self):
        """初始化所有智能体"""
        self.agents["trainer"] = SimpleAgent("trainer_001", "trainer", self.model_manager)
        self.agents["analyzer"] = SimpleAgent("analyzer_001", "analyzer", self.model_manager)
        self.agents["researcher"] = SimpleAgent("researcher_001", "researcher", self.model_manager)
        self.agents["planner"] = SimpleAgent("planner_001", "planner", self.model_manager)
        self.agents["executor"] = SimpleAgent("executor_001", "executor", self.model_manager)
    
    async def process_request(self, request_type, input_data):
        """处理请求"""
        # 根据请求类型选择智能体
        agent_mapping = {
            "training": "trainer",
            "analysis": "analyzer",
            "research": "researcher",
            "planning": "planner",
            "execution": "executor"
        }
        
        agent_id = agent_mapping.get(request_type)
        agent = self.agents.get(agent_id)
        
        if agent:
            print(f"[协调器] 将请求转发给 {agent_id}")
            result = await agent.process(input_data)
            return result
        else:
            return {"error": f"Unknown request type: {request_type}"}
    
    async def multi_agent_workflow(self, workflow_type, input_data):
        """多智能体协作工作流"""
        print(f"[协调器] 开始多智能体工作流: {workflow_type}")
        
        results = {}
        
        if workflow_type == "capability_improvement":
            # 能力提升工作流
            print("步骤1: 分析当前能力")
            analysis_result = await self.agents["analyzer"].process({
                "query": f"分析用户的能力现状: {input_data.get('user_description', '')}",
                "depth": "deep"
            })
            results["analysis"] = analysis_result
            
            print("步骤2: 创建训练计划")
            plan_result = await self.agents["planner"].process({
                "task": f"提升能力: {input_data.get('capability', '')}"
            })
            results["planning"] = plan_result
            
            print("步骤3: 执行训练")
            exec_result = await self.agents["executor"].process({
                "task": input_data.get('training_content', ''),
                "task_type": "cognitive_training"
            })
            results["execution"] = exec_result
            
        elif workflow_type == "problem_solving":
            # 问题解决工作流
            print("步骤1: 深度分析问题")
            analysis_result = await self.agents["analyzer"].process({
                "query": input_data.get('problem', ''),
                "depth": "deep"
            })
            results["analysis"] = analysis_result
            
            print("步骤2: 制定解决方案")
            plan_result = await self.agents["planner"].process({
                "task": f"解决问题: {input_data.get('problem', '')}"
            })
            results["planning"] = plan_result
            
            print("步骤3: 执行解决方案")
            exec_result = await self.agents["executor"].process({
                "task": input_data.get('problem', ''),
                "task_type": "problem_definition"
            })
            results["execution"] = exec_result
            
            print("步骤4: 研究相关资料")
            search_result = await self.agents["researcher"].process({
                "query": input_data.get('research_query', ''),
                "search_type": "general"
            })
            results["research"] = search_result
        
        else:
            return {"error": f"Unknown workflow type: {workflow_type}"}
        
        results["workflow_type"] = workflow_type
        results["timestamp"] = datetime.now().isoformat()
        
        return results
    
    def get_status(self):
        """获取所有智能体状态"""
        status = {}
        for agent_id, agent in self.agents.items():
            status[agent_id] = {
                "type": agent.agent_type,
                "memory_items": len(agent.memory),
                "tasks_count": len(agent.tasks)
            }
        return status
    
    def get_available_agents(self):
        """获取可用智能体列表"""
        agents = []
        for agent_id, agent in self.agents.items():
            agents.append({
                "id": agent_id,
                "type": agent.agent_type
            })
        return agents


async def interactive_mode():
    """交互式模式"""
    print("="*80)
    print("AI智能体系统 - 交互式模式")
    print("="*80)
    print()
    
    # 创建协调器
    try:
        model_manager = GLMModelManager()
        orchestrator = AIAgentOrchestrator(model_manager)
    except Exception as e:
        print(f"初始化错误: {e}")
        print("请确保配置GLM_API_KEY环境变量")
        return
    
    print("可用智能体:")
    agents = orchestrator.get_available_agents()
    for agent in agents:
        print(f"  - {agent['id']:15s} ({agent['type']})")
    print()
    
    print("可用工作流:")
    print("  1. capability_improvement - 能力提升")
    print("  2. problem_solving - 问题解决")
    print("  3. single_agent - 单智能体处理")
    print("  4. status - 查看状态")
    print()
    
    while True:
        print("="*80)
        print("请选择:")
        print("1. 能力提升")
        print("2. 问题解决")
        print("3. 单智能体")
        print("4. 查看状态")
        print("5. 退出")
        print("="*80)
        
        choice = input("> ")
        
        if choice == "5":
            print("再见！")
            break
        elif choice == "1":
            print("\n能力提升工作流")
            print("-"*80)
            capability = input("要提升的能力: ")
            user_desc = input("用户描述（可选）: ")
            training_content = input("训练内容（可选）: ")
            
            result = await orchestrator.multi_agent_workflow("capability_improvement", {
                "capability": capability,
                "user_description": user_desc,
                "training_content": training_content
            })
            
            print("\n工作流结果:")
            for step, step_result in result.items():
                print(f"\n{step}:")
                print(step_result)
        
        elif choice == "2":
            print("\n问题解决工作流")
            print("-"*80)
            problem = input("问题描述: ")
            research_query = input("研究查询（可选）: ")
            
            result = await orchestrator.multi_agent_workflow("problem_solving", {
                "problem": problem,
                "research_query": research_query
            })
            
            print("\n工作流结果:")
            for step, step_result in result.items():
                print(f"\n{step}:")
                print(step_result)
        
        elif choice == "3":
            print("\n单智能体处理")
            print("-"*80)
            print("选择智能体类型:")
            print("1. trainer - 训练智能体")
            print("2. analyzer - 分析智能体")
            print("3. researcher - 研究智能体")
            print("4. planner - 规划智能体")
            print("5. executor - 执行智能体")
            
            agent_choice = input("\n选择智能体 (1-5): ")
            agent_map = {
                "1": "trainer",
                "2": "analyzer",
                "3": "researcher",
                "4": "planner",
                "5": "executor"
            }
            
            agent_type = agent_map.get(agent_choice)
            
            if agent_type == "trainer":
                input_data = {"input": input("训练输入: ")}
            elif agent_type == "analyzer":
                input_data = {"query": input("分析查询: "), "depth": "deep"}
            elif agent_type == "researcher":
                input_data = {"query": input("搜索查询: "), "search_type": "general"}
            elif agent_type == "planner":
                input_data = {"task": input("任务: ")}
            elif agent_type == "executor":
                task_type = input("任务类型 (cognitive_training/problem_definition/other): ")
                task = input("任务描述: ")
                input_data = {"task": task, "task_type": task_type}
            else:
                print("无效选择")
                continue
            
            result = await orchestrator.process_request(agent_type, input_data)
            
            print("\n智能体结果:")
            print(result)
        
        elif choice == "4":
            print("\n系统状态")
            print("-"*80)
            status = orchestrator.get_status()
            
            print("智能体状态:")
            for agent_id, agent_status in status.items():
                print(f"  {agent_id:20s}: {agent_status['type']} - 记忆: {agent_status['memory_items']} - 任务: {agent_status['tasks_count']}")
        
        else:
            print("无效选择，请重新输入")


async def batch_mode():
    """批处理模式"""
    print("="*80)
    print("AI智能体系统 - 批处理模式")
    print("="*80)
    print()
    
    try:
        model_manager = GLMModelManager()
        orchestrator = AIAgentOrchestrator(model_manager)
    except Exception as e:
        print(f"初始化错误: {e}")
        return
    
    # 从文件读取任务
    tasks_file = input("任务文件路径 (JSON): ")
    
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
    except Exception as e:
        print(f"读取文件错误: {e}")
        return
    
    print(f"加载了 {len(tasks)} 个任务")
    
    for i, task in enumerate(tasks, 1):
        print(f"\n处理任务 {i}/{len(tasks)}: {task.get('name', task.get('description', ''))}")
        
        request_type = task.get("type", "analysis")
        result = await orchestrator.process_request(request_type, task)
        
        print(f"结果: {result}")
        
        # 可选：保存结果
        if i < len(tasks):
            input("按回车继续下一个任务...")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI智能体系统")
    parser.add_argument("--interactive", action="store_true", help="交互式模式")
    parser.add_argument("--batch", type=str, help="批处理模式（JSON文件）")
    parser.add_argument("--status", action="store_true", help="查看状态")
    parser.add_argument("--models", action="store_true", help="查看所有模型")
    
    args = parser.parse_args()
    
    if args.models:
        print("所有GLM模型:")
        try:
            model_manager = GLMModelManager()
            model_manager.print_all_models()
        except Exception as e:
            print(f"模型管理器错误: {e}")
            return
    
    elif args.status:
        print("智能体状态:")
        try:
            model_manager = GLMModelManager()
            orchestrator = AIAgentOrchestrator(model_manager)
            status = orchestrator.get_status()
            
            for agent_id, agent_status in status.items():
                print(f"{agent_id:20s} {agent_status['type']:20s} - 记忆: {agent_status['memory_items']}")
        except Exception as e:
            print(f"获取状态错误: {e}")
            return
    
    elif args.interactive:
        import asyncio
        asyncio.run(interactive_mode())
    
    elif args.batch:
        import asyncio
        asyncio.run(batch_mode())
    
    else:
        print("AI智能体系统")
        print("="*80)
        print("请选择模式:")
        print("  python ai_agent.py --interactive  # 交互式模式")
        print("  python ai_agent.py --batch tasks.json  # 批处理模式")
        print("  python ai_agent.py --status  # 查看状态")
        print("  python ai_agent.py --models  # 查看所有模型")


if __name__ == "__main__":
    main()
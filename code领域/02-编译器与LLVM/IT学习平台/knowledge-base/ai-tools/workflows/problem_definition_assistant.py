#!/usr/bin/env python3
"""
问题定义AI辅助工具
帮助用户系统性地重新定义问题
"""

import os
import sys
from typing import Dict, List, Optional
import json
from datetime import datetime

from glm_models import GLMModelManager, ModelType


class ProblemDefinitionAssistant:
    """问题定义AI辅助器"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.model_manager = GLMModelManager(api_key)
        self.definition_history = []
    
    def analyze_5_questions(self, problem_statement: str, model_name: Optional[str] = None) -> Dict[str, str]:
        """5问题框架分析
        
        Args:
            problem_statement: 问题陈述
            model_name: 使用的模型（可选）
        """
        if model_name is None:
            model_name = self.model_manager.recommend_model("问题分析", "deep")
        
        prompt = f"""对以下问题进行5问题框架分析：

## 5问题框架
1. 问题是什么？    （清晰陈述问题，避免症状描述）
2. 为什么是问题？  （识别核心矛盾，明确负面影响）
3. 为谁而存在？    （明确问题对象，识别利益相关者）
4. 为什么现在解决？（时间紧迫性，机会窗口）
5. 不解决会怎样？  （机会成本，风险评估）

问题：{problem_statement}

请按照5问题框架结构化回答，每个问题用1-2句话回答。
"""
        
        result = self._call_model(model_name, prompt)
        
        self.definition_history.append({
            "method": "5_questions",
            "model": model_name,
            "input": problem_statement,
            "output": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "method": "5_questions",
            "model": model_name,
            "result": result
        }
    
    def question_assumptions(self, problem_statement: str, model_name: Optional[str] = None) -> Dict[str, str]:
        """假设质疑清单
        
        Args:
            problem_statement: 问题陈述
            model_name: 使用的模型（可选）
        """
        if model_name is None:
            model_name = self.model_manager.recommend_model("假设质疑", "deep")
        
        prompt = f"""质疑以下问题的前提假设：

## 假设质疑清单
□ 问题的前提是什么？
□ 这个前提是真的吗？
□ 如果前提是错的，问题还成立吗？
□ 有没有隐含的假设？
□ 问题本身的框架对吗？
□ 可以重新定义问题吗？
□ 问题是从谁的角度定义的？

问题：{problem_statement}

请逐一回答上述问题，指出隐含假设和可能的框架问题。
"""
        
        result = self._call_model(model_name, prompt)
        
        self.definition_history.append({
            "method": "question_assumptions",
            "model": model_name,
            "input": problem_statement,
            "output": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "method": "question_assumptions",
            "model": model_name,
            "result": result
        }
    
    def value_assessment(self, problem_statement: str, model_name: Optional[str] = None) -> Dict[str, str]:
        """价值评估矩阵
        
        Args:
            problem_statement: 问题陈述
            model_name: 使用的模型（可选）
        """
        if model_name is None:
            model_name = self.model_manager.recommend_model("价值评估", "balanced")
        
        prompt = f"""评估以下问题的价值：

## 价值评估矩阵

**影响度**（1-10分）：
- 影响多少人？
- 影响多大？
- 正面影响程度？

**紧迫性**（1-10分）：
- 时间窗口？
- 不解决会怎样？

**可行性**（1-10分）：
- 技术可行性？
- 资源可得性？

综合价值 = (影响度 × 紧迫性 × 可行性) / 3

问题：{problem_statement}

请为影响度、紧迫性、可行性各给出1-10分的评分，并说明理由。
最后计算综合价值。
"""
        
        result = self._call_model(model_name, prompt)
        
        self.definition_history.append({
            "method": "value_assessment",
            "model": model_name,
            "input": problem_statement,
            "output": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "method": "value_assessment",
            "model": model_name,
            "result": result
        }
    
    def multiple_perspectives(self, problem_statement: str, model_name: Optional[str] = None) -> Dict[str, str]:
        """多视角定义
        
        Args:
            problem_statement: 问题陈述
            model_name: 使用的模型（可选）
        """
        if model_name is None:
            model_name = self.model_manager.recommend_model("多视角分析", "deep")
        
        prompt = f"""从不同角度重新定义以下问题：

## 多视角定义

**用户视角**：他们遇到了什么困难？
- 核心痛点是什么？
- 真正需求是什么？

**技术视角**：技术上的本质问题？
- 技术约束是什么？
- 技术难点在哪里？

**业务视角**：对业务的价值是什么？
- 商业价值是什么？
- 成本收益如何？

**竞争对手视角**：他们会如何解决？
- 我们的差异化是什么？
- 竞争优势在哪里？

**未来视角**：5年后还会是问题吗？
- 趋势如何？
- 如何前瞻性解决？

问题：{problem_statement}

请从以上5个视角分析问题，并尝试提出重新定义的问题。
"""
        
        result = self._call_model(model_name, prompt)
        
        self.definition_history.append({
            "method": "multiple_perspectives",
            "model": model_name,
            "input": problem_statement,
            "output": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "method": "multiple_perspectives",
            "model": model_name,
            "result": result
        }
    
    def full_definition(self, problem_statement: str) -> Dict[str, Any]:
        """完整的问题定义分析
        
        Args:
            problem_statement: 问题陈述
        """
        print("="*80)
        print("问题定义AI辅助 - 完整分析")
        print("="*80)
        print(f"问题陈述: {problem_statement}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {}
        
        # 第一步：5问题框架
        print("第一步：5问题框架分析")
        print("-"*80)
        result_5q = self.analyze_5_questions(problem_statement)
        print(result_5q["result"])
        print()
        results["5_questions"] = result_5q
        
        # 第二步：假设质疑
        print("第二步：假设质疑")
        print("-"*80)
        result_assumption = self.question_assumptions(problem_statement)
        print(result_assumption["result"])
        print()
        results["question_assumptions"] = result_assumption
        
        # 第三步：价值评估
        print("第三步：价值评估")
        print("-"*80)
        result_value = self.value_assessment(problem_statement)
        print(result_value["result"])
        print()
        results["value_assessment"] = result_value
        
        # 第四步：多视角定义
        print("第四步：多视角重新定义")
        print("-"*80)
        result_perspectives = self.multiple_perspectives(problem_statement)
        print(result_perspectives["result"])
        print()
        results["multiple_perspectives"] = result_perspectives
        
        print("="*80)
        print("分析完成！")
        print("="*80)
        
        return results
    
    def save_definition(self, filepath: Optional[str] = None):
        """保存问题定义
        
        Args:
            filepath: 文件路径（可选）
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
            filepath = f"practices/problem-definition/definition-{timestamp}.json"
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.definition_history, f, ensure_ascii=False, indent=2)
        
        print(f"\n问题定义已保存到: {filepath}")
    
    def _call_model(self, model_name: str, prompt: str) -> str:
        """调用模型（需要实际的API调用）
        
        Args:
            model_name: 模型名称
            prompt: 提示词
        
        Returns:
            模型输出
        """
        # TODO: 实现实际的API调用
        # 这里返回模拟输出
        model_config = self.model_manager.get_model(model_name)
        
        return f"[模拟输出 - {model_name}]\n{prompt}"


def interactive_mode():
    """交互式问题定义模式"""
    assistant = ProblemDefinitionAssistant()
    
    print("="*80)
    print("问题定义AI辅助 - 交互式模式")
    print("="*80)
    
    while True:
        print("\n请输入问题陈述（输入 'quit' 退出）:")
        problem_statement = input("> ")
        
        if problem_statement.lower() == 'quit':
            break
        
        if not problem_statement.strip():
            continue
        
        # 执行完整分析
        results = assistant.full_definition(problem_statement)
        
        # 询问是否保存
        print("\n是否保存问题定义？(y/n):")
        choice = input("> ")
        if choice.lower() == 'y':
            assistant.save_definition()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="问题定义AI辅助工具")
    parser.add_argument("--problem", type=str, help="问题陈述")
    parser.add_argument("--method", type=str, choices=["5q", "assumption", "value", "perspectives", "full"],
                       default="full", help="分析方法")
    parser.add_argument("--interactive", action="store_true", help="交互式模式")
    parser.add_argument("--model", type=str, help="指定使用的模型")
    parser.add_argument("--save", type=str, help="保存到指定文件")
    
    args = parser.parse_args()
    
    assistant = ProblemDefinitionAssistant()
    
    if args.interactive:
        interactive_mode()
    elif args.problem:
        if args.method == "5q":
            result = assistant.analyze_5_questions(args.problem, args.model)
        elif args.method == "assumption":
            result = assistant.question_assumptions(args.problem, args.model)
        elif args.method == "value":
            result = assistant.value_assessment(args.problem, args.model)
        elif args.method == "perspectives":
            result = assistant.multiple_perspectives(args.problem, args.model)
        else:  # full
            results = assistant.full_definition(args.problem)
        
        if args.save:
            assistant.save_definition(args.save)
    else:
        print("请使用 --problem 提供问题陈述，或使用 --interactive 进入交互模式")
        print("\n示例:")
        print("  python problem_definition_assistant.py --problem '项目延期了，需要加快进度'")
        print("  python problem_definition_assistant.py --problem '系统性能下降' --method 5q")
        print("  python problem_definition_assistant.py --interactive")


if __name__ == "__main__":
    main()
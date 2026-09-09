#!/usr/bin/env python3
"""
每日认知训练AI辅助工具
实现30天认知训练的AI辅助流程
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import json

from glm_models import GLMModelManager, ModelType


class DailyCognitiveTrainer:
    """每日认知训练AI辅助器"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.model_manager = GLMModelManager(api_key)
        self.training_log = []
    
    def step1_decomposition(self, user_input: str, model_name: Optional[str] = None) -> str:
        """第一步：拆解（信息理解）
        
        Args:
            user_input: 用户的观点或问题
            model_name: 使用的模型（可选）
        """
        if model_name is None:
            model_name = self.model_manager.recommend_model("快速拆解", "fast")
        
        prompt = f"""分析以下观点，回答：

1. 核心定义是什么？
2. 前提假设是什么？
3. 边界在哪里？
4. 有反例吗？

观点：{user_input}

请用简洁的语言回答，每点不超过50字。
"""
        
        # 调用模型（这里需要实际的API调用）
        result = self._call_model(model_name, prompt)
        
        self.training_log.append({
            "step": "decomposition",
            "model": model_name,
            "input": user_input,
            "output": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def step2_reasoning(self, user_input: str, model_name: Optional[str] = None) -> str:
        """第二步：推演（逻辑推理）
        
        Args:
            user_input: 用户的观点或问题
            model_name: 使用的模型（可选）
        """
        if model_name is None:
            model_name = self.model_manager.recommend_model("逻辑推理", "balanced")
        
        prompt = f"""对观点进行反向推理：

1. 如果为真会推出什么？
2. 如果为假会发生什么？
3. 有没有第三种解释？

观点：{user_input}

请用简洁的语言回答，每点不超过50字。
"""
        
        result = self._call_model(model_name, prompt)
        
        self.training_log.append({
            "step": "reasoning",
            "model": model_name,
            "input": user_input,
            "output": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def step3_quantification(self, user_input: str, model_name: Optional[str] = None) -> str:
        """第三步：量化（决策优化）
        
        Args:
            user_input: 用户的观点或问题
            model_name: 使用的模型（可选）
        """
        if model_name is None:
            model_name = self.model_manager.recommend_model("量化评估", "balanced")
        
        prompt = f"""评估可信度（0-100%）并给出理由：

观点：{user_input}

请先给出可信度百分比，然后用1-2句话说明理由。
"""
        
        result = self._call_model(model_name, prompt)
        
        self.training_log.append({
            "step": "quantification",
            "model": model_name,
            "input": user_input,
            "output": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def step4_system_thinking(self, user_input: str, model_name: Optional[str] = None) -> str:
        """第四步：画反馈（系统思维）
        
        Args:
            user_input: 用户的观点或问题
            model_name: 使用的模型（可选）
        """
        if model_name is None:
            model_name = self.model_manager.recommend_model("系统思维", "deep")
        
        prompt = f"""识别三变量反馈链：

请从以下观点中识别3个变量，并画出它们之间的反馈关系：
A → B → C → A?

观点：{user_input}

请用简洁的方式描述反馈链。
"""
        
        result = self._call_model(model_name, prompt)
        
        self.training_log.append({
            "step": "system_thinking",
            "model": model_name,
            "input": user_input,
            "output": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def step5_reflection(self, today_findings: str, model_name: Optional[str] = None) -> str:
        """第五步：复盘（元认知）
        
        Args:
            today_findings: 今天的发现或反思
            model_name: 使用的模型（可选）
        """
        if model_name is None:
            model_name = self.model_manager.recommend_model("快速反思", "fast")
        
        prompt = f"""认知检查：

基于今天的发现，请帮助我：
1. 今天的判断偏差是什么？
2. 是信息问题还是推理问题？
3. 是情绪干扰还是过度自信？
4. 如何改进？

今天的发现：{today_findings}

请用简洁的语言回答，每点不超过30字。
"""
        
        result = self._call_model(model_name, prompt)
        
        self.training_log.append({
            "step": "reflection",
            "model": model_name,
            "input": today_findings,
            "output": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def full_training(self, user_input: str, today_findings: Optional[str] = None) -> Dict[str, str]:
        """完整的每日认知训练
        
        Args:
            user_input: 当天的观点或问题
            today_findings: 今天的发现（可选）
        """
        print("="*80)
        print("每日认知训练 - AI辅助版")
        print("="*80)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"输入: {user_input}")
        print()
        
        results = {}
        
        # 第一步：拆解
        print("第一步：拆解（信息理解）- 2分钟")
        print("-"*80)
        decomposition = self.step1_decomposition(user_input)
        print(decomposition)
        print()
        results["decomposition"] = decomposition
        
        # 第二步：推演
        print("第二步：推演（逻辑推理）- 2分钟")
        print("-"*80)
        reasoning = self.step2_reasoning(user_input)
        print(reasoning)
        print()
        results["reasoning"] = reasoning
        
        # 第三步：量化
        print("第三步：量化（决策优化）- 2分钟")
        print("-"*80)
        quantification = self.step3_quantification(user_input)
        print(quantification)
        print()
        results["quantification"] = quantification
        
        # 第四步：系统
        print("第四步：画反馈（系统思维）- 2分钟")
        print("-"*80)
        system = self.step4_system_thinking(user_input)
        print(system)
        print()
        results["system_thinking"] = system
        
        # 第五步：复盘
        print("第五步：复盘（元认知）- 2分钟")
        print("-"*80)
        findings = today_findings or "今天的学习和思考"
        reflection = self.step5_reflection(findings)
        print(reflection)
        print()
        results["reflection"] = reflection
        
        print("="*80)
        print("训练完成！总用时约10-15分钟")
        print("="*80)
        
        return results
    
    def save_log(self, filepath: Optional[str] = None):
        """保存训练日志
        
        Args:
            filepath: 日志文件路径（可选）
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y-%m-%d')
            filepath = f"learning-log/daily/cognitive-training-{timestamp}.json"
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.training_log, f, ensure_ascii=False, indent=2)
        
        print(f"\n训练日志已保存到: {filepath}")
    
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
    """交互式训练模式"""
    trainer = DailyCognitiveTrainer()
    
    print("="*80)
    print("每日认知训练 - 交互式模式")
    print("="*80)
    
    while True:
        print("\n请输入今天的观点或问题（输入 'quit' 退出）:")
        user_input = input("> ")
        
        if user_input.lower() == 'quit':
            break
        
        if not user_input.strip():
            continue
        
        print("\n今天的发现或反思（可选，直接回车跳过）:")
        today_findings = input("> ")
        
        # 执行完整训练
        results = trainer.full_training(user_input, today_findings)
        
        # 询问是否保存
        print("\n是否保存训练日志？(y/n):")
        choice = input("> ")
        if choice.lower() == 'y':
            trainer.save_log()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="每日认知训练AI辅助工具")
    parser.add_argument("--input", type=str, help="训练输入（观点或问题）")
    parser.add_argument("--findings", type=str, help="今天的发现或反思")
    parser.add_argument("--interactive", action="store_true", help="交互式模式")
    parser.add_argument("--model", type=str, help="指定使用的模型")
    parser.add_argument("--save", type=str, help="保存日志到指定文件")
    
    args = parser.parse_args()
    
    trainer = DailyCognitiveTrainer()
    
    if args.interactive:
        interactive_mode()
    elif args.input:
        results = trainer.full_training(args.input, args.findings)
        
        if args.save:
            trainer.save_log(args.save)
    else:
        print("请使用 --input 提供训练输入，或使用 --interactive 进入交互模式")
        print("\n示例:")
        print("  python daily_cognitive_trainer.py --input '微服务比单体架构好' --interactive")
        print("  python daily_cognitive_trainer.py --interactive")


if __name__ == "__main__":
    main()
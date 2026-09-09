#!/usr/bin/env python3
"""
AI辅助能力评估工具
帮助用户评估和追踪24个核心能力
"""

import os
import sys
from typing import Dict, List, Optional
import json
from datetime import datetime

from glm_models import GLMModelManager, ModelType


class CapabilityAssessmentAssistant:
    """能力评估AI辅助器"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.model_manager = GLMModelManager(api_key)
        self.assessment_history = []
        
        # 加载能力指标定义
        self.capabilities = self._load_capabilities()
    
    def _load_capabilities(self) -> Dict[str, Dict]:
        """加载能力指标定义"""
        capabilities = {}
        
        # 判断力层
        capabilities["problem-definition"] = {
            "name": "问题定义与选择",
            "priority": "⭐⭐⭐",
            "dimensions": [
                "框架质疑能力 (30%)",
                "价值判断能力 (25%)",
                "问题优先级判断 (25%)",
                "边界定义能力 (20%)"
            ]
        }
        
        capabilities["judgment"] = {
            "name": "判断与取舍",
            "priority": "⭐⭐⭐",
            "dimensions": [
                "信息筛选与概率估计 (30%)",
                "目标函数与取舍平衡 (35%)",
                "风险评估与应对 (20%)",
                "责任承担与复盘 (15%)"
            ]
        }
        
        capabilities["resource-integration"] = {
            "name": "资源整合",
            "priority": "⭐⭐",
            "dimensions": [
                "结构与模块设计 (30%)",
                "目标对齐与约束理解 (25%)",
                "接口设计与协作机制 (25%)",
                "反馈闭环与优化 (20%)"
            ]
        }
        
        capabilities["influence"] = {
            "name": "影响力与沟通",
            "priority": "⭐⭐",
            "dimensions": [
                "说服能力 (25%)",
                "信任建立能力 (25%)",
                "冲突处理能力 (25%)",
                "沟通结构化能力 (25%)"
            ]
        }
        
        # 思维力层
        capabilities["imagination"] = {
            "name": "想象力",
            "priority": "⭐⭐",
            "dimensions": [
                "组合能力 (25%)",
                "抽象能力 (25%)",
                "约束突破能力 (25%)",
                "未来推演能力 (25%)"
            ]
        }
        
        capabilities["abstract-modeling"] = {
            "name": "抽象建模",
            "priority": "⭐",
            "dimensions": [
                "问题抽象深度 (30%)",
                "模型结构化程度 (30%)",
                "模型验证能力 (20%)",
                "跨域迁移能力 (20%)"
            ]
        }
        
        capabilities["systems-thinking-advanced"] = {
            "name": "系统性思维扩展",
            "priority": "⭐⭐⭐",
            "dimensions": [
                "整体性认知 (25%)",
                "关系性理解 (25%)",
                "动态性洞察 (25%)",
                "杠杆点识别 (25%)"
            ]
        }
        
        # 认知层
        capabilities["critical-thinking"] = {
            "name": "批判性思维",
            "priority": "⭐⭐",
            "dimensions": [
                "质疑能力 (25%)",
                "分析能力 (25%)",
                "判断能力 (25%)",
                "元认知能力 (25%)"
            ]
        }
        
        capabilities["first-principles"] = {
            "name": "第一性原理",
            "priority": "⭐⭐",
            "dimensions": [
                "拆解能力 (25%)",
                "本质洞察 (25%)",
                "重组能力 (25%)",
                "质疑能力 (25%)"
            ]
        }
        
        capabilities["meta-cognition"] = {
            "name": "元认知",
            "priority": "⭐⭐",
            "dimensions": [
                "元认知监控 (30%)",
                "元认知控制 (30%)",
                "元认知评估 (20%)",
                "认知偏差识别 (20%)"
            ]
        }
        
        capabilities["reverse-thinking"] = {
            "name": "逆向思维",
            "priority": "⭐⭐",
            "dimensions": [
                "目标倒推 (30%)",
                "路径验证 (30%)",
                "约束识别 (20%)",
                "反向推理 (20%)"
            ]
        }
        
        capabilities["structured-thinking"] = {
            "name": "结构化思维",
            "priority": "⭐⭐",
            "dimensions": [
                "要素识别能力 (25%)",
                "关系建立能力 (25%)",
                "清晰表达能力 (25%)",
                "结构优化能力 (25%)"
            ]
        }
        
        # 基础层
        capabilities["systems-thinking"] = {
            "name": "系统级思维",
            "priority": "⭐",
            "dimensions": [
                "全局视野 (25%)",
                "权衡能力 (25%)",
                "时序思维 (25%)",
                "约束识别 (25%)"
            ]
        }
        
        capabilities["technical-depth"] = {
            "name": "技术底层理解",
            "priority": "⭐",
            "dimensions": [
                "原理深度 (25%)",
                "瓶颈识别 (25%)",
                "权衡判断 (25%)",
                "边界探索 (25%)"
            ]
        }
        
        capabilities["migration"] = {
            "name": "快速迁移",
            "priority": "⭐",
            "dimensions": [
                "抽象能力 (25%)",
                "结构识别能力 (25%)",
                "原理理解深度 (25%)",
                "多领域暴露 (25%)"
            ]
        }
        
        # 支持层
        capabilities["complex-system-design"] = {
            "name": "复杂系统设计",
            "priority": "⭐⭐",
            "dimensions": [
                "全局架构设计能力 (30%)",
                "多维度权衡能力 (25%)",
                "系统性风险识别 (25%)",
                "演化路径设计 (20%)"
            ]
        }
        
        capabilities["emotional-intelligence"] = {
            "name": "情商",
            "priority": "⭐",
            "dimensions": [
                "自我觉察 (25%)",
                "自我管理 (25%)",
                "社交觉察 (25%)",
                "关系管理 (25%)"
            ]
        }
        
        capabilities["execution"] = {
            "name": "执行力",
            "priority": "⭐",
            "dimensions": [
                "目标拆解能力 (25%)",
                "行动启动能力 (25%)",
                "持续推进能力 (25%)",
                "结果交付能力 (25%)"
            ]
        }
        
        capabilities["leadership"] = {
            "name": "领导力",
            "priority": "⭐",
            "dimensions": [
                "愿景能力 (25%)",
                "团队建设能力 (25%)",
                "沟通影响能力 (25%)",
                "决策担当能力 (25%)"
            ]
        }
        
        capabilities["learning"] = {
            "name": "学习能力",
            "priority": "⭐",
            "dimensions": [
                "信息输入能力 (25%)",
                "知识整合能力 (25%)",
                "技能内化能力 (25%)",
                "迁移应用能力 (25%)"
            ]
        }
        
        capabilities["resilience"] = {
            "name": "韧性",
            "priority": "⭐",
            "dimensions": [
                "压力认知能力 (25%)",
                "情绪调节能力 (25%)",
                "问题解决能力 (25%)",
                "恢复反弹能力 (25%)"
            ]
        }
        
        capabilities["adaptability"] = {
            "name": "适应性",
            "priority": "⭐",
            "dimensions": [
                "环境感知能力 (25%)",
                "学习调整能力 (25%)",
                "灵活应变能力 (25%)",
                "恢复反弹能力 (25%)"
            ]
        }
        
        capabilities["strategy"] = {
            "name": "战略与策略",
            "priority": "⭐⭐",
            "dimensions": [
                "长期预见能力 (25%)",
                "目标定位能力 (25%)",
                "资源配置能力 (25%)",
                "风险管理能力 (25%)"
            ]
        }
        
        return capabilities
    
    def assess_capability(self, capability_id: str, user_responses: Dict[str, str], model_name: Optional[str] = None) -> Dict[str, Any]:
        """评估单个能力
        
        Args:
            capability_id: 能力ID
            user_responses: 用户的回答
            model_name: 使用的模型（可选）
        """
        if model_name is None:
            model_name = self.model_manager.recommend_model("能力评估", "deep")
        
        capability = self.capabilities.get(capability_id)
        if not capability:
            return {"error": f"能力 '{capability_id}' 不存在"}
        
        prompt = f"""基于{capability['name']}的评估维度，分析用户回答：

## 能力：{capability['name']}
## 优先级：{capability['priority']}

## 评估维度：
{chr(10).join([f"{i+1}. {dim}" for i, dim in enumerate(capability['dimensions'])])}

## 用户回答：
{json.dumps(user_responses, ensure_ascii=False, indent=2)}

请提供：
1. 每个维度的得分（1-10分）
2. 得分理由
3. 改进建议（3-5条）
4. 下一步练习方向

请以JSON格式输出，格式如下：
{{
  "dimension_scores": {{"维度1": 得分, "维度2": 得分, ...}},
  "total_score": 总分,
  "reasoning": "得分理由",
  "suggestions": ["建议1", "建议2", ...],
  "next_steps": ["下一步1", "下一步2", ...]
}}
"""
        
        result = self._call_model(model_name, prompt)
        
        assessment = {
            "capability_id": capability_id,
            "capability_name": capability['name'],
            "model": model_name,
            "user_responses": user_responses,
            "ai_analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
        self.assessment_history.append(assessment)
        
        return assessment
    
    def batch_assess(self, capability_ids: List[str], responses: Dict[str, Dict[str, str]], model_name: Optional[str] = None) -> Dict[str, Any]:
        """批量评估多个能力
        
        Args:
            capability_ids: 能力ID列表
            responses: 所有能力的回答
            model_name: 使用的模型（可选）
        """
        results = {}
        
        for capability_id in capability_ids:
            if capability_id in responses:
                result = self.assess_capability(capability_id, responses[capability_id], model_name)
                results[capability_id] = result
        
        return results
    
    def generate_assessment_report(self, results: Dict[str, Any]) -> str:
        """生成评估报告
        
        Args:
            results: 评估结果
        """
        report = []
        report.append("="*80)
        report.append("AI辅助能力评估报告")
        report.append("="*80)
        report.append(f"评估时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"评估能力数: {len(results)}")
        report.append("")
        
        # 总体评分
        total_score = 0
        count = 0
        
        for capability_id, result in results.items():
            if "total_score" in result.get("ai_analysis", {}):
                total_score += result["ai_analysis"]["total_score"]
                count += 1
        
        avg_score = total_score / count if count > 0 else 0
        
        report.append(f"总体评分: {avg_score:.2f}/10")
        report.append("")
        
        # 每个能力的详细报告
        for capability_id, result in results.items():
            capability = self.capabilities.get(capability_id)
            if not capability:
                continue
            
            report.append(f"【{capability['name']}】{capability['priority']}")
            report.append("-"*80)
            
            ai_analysis = result.get("ai_analysis", {})
            
            if "dimension_scores" in ai_analysis:
                report.append("维度评分:")
                for dim, score in ai_analysis["dimension_scores"].items():
                    report.append(f"  {dim}: {score}/10")
                report.append("")
            
            if "total_score" in ai_analysis:
                report.append(f"总分: {ai_analysis['total_score']}/10")
                report.append("")
            
            if "reasoning" in ai_analysis:
                report.append(f"得分理由: {ai_analysis['reasoning']}")
                report.append("")
            
            if "suggestions" in ai_analysis:
                report.append("改进建议:")
                for suggestion in ai_analysis["suggestions"]:
                    report.append(f"  - {suggestion}")
                report.append("")
            
            if "next_steps" in ai_analysis:
                report.append("下一步:")
                for step in ai_analysis["next_steps"]:
                    report.append(f"  - {step}")
                report.append("")
            
            report.append("="*80)
        
        return "\n".join(report)
    
    def save_assessment(self, filepath: Optional[str] = None):
        """保存评估结果
        
        Args:
            filepath: 文件路径（可选）
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y-%m-%d')
            filepath = f"capability-metrics/assessment-{timestamp}.json"
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.assessment_history, f, ensure_ascii=False, indent=2)
        
        print(f"\n评估结果已保存到: {filepath}")
    
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
    
    def list_capabilities(self):
        """列出所有能力"""
        print("="*80)
        print("能力清单")
        print("="*80)
        print()
        
        for capability_id, capability in self.capabilities.items():
            print(f"【{capability_id}】{capability['name']} {capability['priority']}")
            print("  评估维度:")
            for dim in capability['dimensions']:
                print(f"    - {dim}")
            print()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI辅助能力评估工具")
    parser.add_argument("--list", action="store_true", help="列出所有能力")
    parser.add_argument("--assess", type=str, help="评估的能力ID（多个用逗号分隔）")
    parser.add_argument("--interactive", action="store_true", help="交互式评估")
    parser.add_argument("--model", type=str, help="指定使用的模型")
    parser.add_argument("--save", type=str, help="保存到指定文件")
    
    args = parser.parse_args()
    
    assistant = CapabilityAssessmentAssistant()
    
    if args.list:
        assistant.list_capabilities()
    elif args.assess:
        # 评估指定能力
        capability_ids = [c.strip() for c in args.assess.split(",")]
        print(f"请为以下能力提供您的回答:")
        for capability_id in capability_ids:
            capability = assistant.capabilities.get(capability_id)
            if capability:
                print(f"\n【{capability['name']}】")
                print("评估维度:")
                for i, dim in enumerate(capability['dimensions']):
                    print(f"  {i+1}. {dim}")
        
        # TODO: 收集用户回答并评估
        print("\n请提供您的回答（JSON格式）:")
        print('{"problem-definition": {"框架质疑": "...", "价值判断": "...", ...}, ...}')
    elif args.interactive:
        # 交互式评估
        print("交互式评估模式")
        print("请选择要评估的能力:")
        for capability_id in assistant.capabilities:
            capability = assistant.capabilities[capability_id]
            print(f"  {capability_id}: {capability['name']} {capability['priority']}")
        
        selected = input("\n输入能力ID（用逗号分隔）: ")
        capability_ids = [c.strip() for c in selected.split(",")]
        
        # TODO: 收集每个能力的回答
        for capability_id in capability_ids:
            if capability_id in assistant.capabilities:
                capability = assistant.capabilities[capability_id]
                print(f"\n【{capability['name']}】")
                print("评估维度:")
                for i, dim in enumerate(capability['dimensions']):
                    print(f"  {i+1}. {dim}")
                
                responses = {}
                for dim in capability['dimensions']:
                    response = input(f"{dim}: ")
                    responses[dim] = response
                
                result = assistant.assess_capability(capability_id, responses, args.model)
                print(result)
        
        if args.save:
            assistant.save_assessment(args.save)
    else:
        print("请使用 --list 查看所有能力，或使用 --assess 评估指定能力")
        print("\n示例:")
        print("  python capability_assessment.py --list")
        print("  python capability_assessment.py --assess problem-definition,judgment")
        print("  python capability_assessment.py --interactive")


if __name__ == "__main__":
    main()
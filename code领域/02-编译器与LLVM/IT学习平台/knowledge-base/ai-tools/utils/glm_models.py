#!/usr/bin/env python3
"""
GLM模型配置和工具类
支持所有GLM模型的调用
"""

import os
from typing import Dict, List, Optional, Any
import json
from dataclasses import dataclass
from enum import Enum

class ModelType(Enum):
    """模型类型枚举"""
    GENERAL = "通用模型"
    CODE = "代码模型"
    EMBEDDING = "向量模型"
    IMAGE = "图像大模型"
    VIDEO = "视频生成模型"
    REALTIME = "实时音视频模型"
    SEARCH = "搜索模型"
    RERANK = "重排序模型"

@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    type: ModelType
    concurrency: int
    description: str
    use_cases: List[str]

class GLMModelManager:
    """GLM模型管理器"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GLM_API_KEY")
        if not self.api_key:
            raise ValueError("GLM_API_KEY not found. Please set environment variable.")
        
        self.models = self._load_models()
    
    def _load_models(self) -> Dict[str, ModelConfig]:
        """加载所有GLM模型配置"""
        models = {}
        
        # 通用模型
        models["glm-4-plus"] = ModelConfig(
            name="glm-4-plus",
            type=ModelType.GENERAL,
            concurrency=20,
            description="复杂推理、深度分析、决策辅助",
            use_cases=["深度分析", "决策辅助", "复杂推理", "系统设计"]
        )
        
        models["glm-4-air"] = ModelConfig(
            name="glm-4-air",
            type=ModelType.GENERAL,
            concurrency=100,
            description="快速响应、日常咨询、知识检索",
            use_cases=["日常咨询", "知识检索", "快速分析"]
        )
        
        models["glm-4-flash"] = ModelConfig(
            name="glm-4-flash",
            type=ModelType.GENERAL,
            concurrency=200,
            description="高频交互、实时反馈、快速练习",
            use_cases=["高频交互", "快速练习", "实时反馈"]
        )
        
        models["glm-4-flashx"] = ModelConfig(
            name="glm-4-flashx",
            type=ModelType.GENERAL,
            concurrency=50,
            description="平衡快速和质量",
            use_cases=["日常练习", "问题分析"]
        )
        
        models["glm-4-long"] = ModelConfig(
            name="glm-4-long",
            type=ModelType.GENERAL,
            concurrency=10,
            description="长文本处理",
            use_cases=["长文本分析", "文献总结"]
        )
        
        models["glm-4v-plus"] = ModelConfig(
            name="glm-4v-plus",
            type=ModelType.GENERAL,
            concurrency=5,
            description="多模态理解",
            use_cases=["图像理解", "多模态分析"]
        )
        
        models["glm-zero-preview"] = ModelConfig(
            name="glm-zero-preview",
            type=ModelType.GENERAL,
            concurrency=50,
            description="预览版模型",
            use_cases=["实验性任务"]
        )
        
        models["glm-4"] = ModelConfig(
            name="glm-4",
            type=ModelType.GENERAL,
            concurrency=30,
            description="基础通用模型",
            use_cases=["一般任务"]
        )
        
        models["glm-3-turbo"] = ModelConfig(
            name="glm-3-turbo",
            type=ModelType.GENERAL,
            concurrency=50,
            description="快速响应",
            use_cases=["快速查询"]
        )
        
        models["glm-4-assistant"] = ModelConfig(
            name="glm-4-assistant",
            type=ModelType.GENERAL,
            concurrency=5,
            description="助手专用模型",
            use_cases=["助手任务"]
        )
        
        models["glm-4-alltools"] = ModelConfig(
            name="glm-4-alltools",
            type=ModelType.GENERAL,
            concurrency=5,
            description="工具调用专用",
            use_cases=["工具集成"]
        )
        
        # 代码模型
        models["codegeex-4"] = ModelConfig(
            name="codegeex-4",
            type=ModelType.CODE,
            concurrency=50,
            description="代码分析、架构审查、技术实现",
            use_cases=["代码审查", "代码生成", "调试辅助", "架构设计"]
        )
        
        # 向量模型
        models["embedding-3"] = ModelConfig(
            name="embedding-3",
            type=ModelType.EMBEDDING,
            concurrency=100,
            description="知识检索、相似度分析、模式匹配",
            use_cases=["知识检索", "向量搜索", "语义匹配"]
        )
        
        models["embedding-3-pro"] = ModelConfig(
            name="embedding-3-pro",
            type=ModelType.EMBEDDING,
            concurrency=100,
            description="增强版向量模型",
            use_cases=["高级知识检索"]
        )
        
        models["embedding-2"] = ModelConfig(
            name="embedding-2",
            type=ModelType.EMBEDDING,
            concurrency=50,
            description="基础向量模型",
            use_cases=["基础向量搜索"]
        )
        
        models["rerank"] = ModelConfig(
            name="rerank",
            type=ModelType.RERANK,
            concurrency=50,
            description="重排序模型",
            use_cases=["搜索结果重排序"]
        )
        
        # 图像模型
        models["glm-image"] = ModelConfig(
            name="glm-image",
            type=ModelType.IMAGE,
            concurrency=1,
            description="架构图生成、思维导图、可视化",
            use_cases=["图表生成", "架构图", "思维导图"]
        )
        
        models["cogview-4"] = ModelConfig(
            name="cogview-4",
            type=ModelType.IMAGE,
            concurrency=5,
            description="视觉理解",
            use_cases=["图像理解", "图表识别"]
        )
        
        # 搜索模型
        models["search-pro"] = ModelConfig(
            name="search-pro",
            type=ModelType.SEARCH,
            concurrency=5,
            description="文献检索、案例搜索",
            use_cases=["文献搜索", "案例检索", "知识搜索"]
        )
        
        models["web-search-pro"] = ModelConfig(
            name="web-search-pro",
            type=ModelType.SEARCH,
            concurrency=30,
            description="网络搜索",
            use_cases=["网络搜索", "信息收集"]
        )
        
        # 实时音视频
        models["glm-realtime"] = ModelConfig(
            name="glm-realtime",
            type=ModelType.REALTIME,
            concurrency=5,
            description="模拟对话、角色扮演",
            use_cases=["模拟对话", "角色扮演", "语音交互"]
        )
        
        models["glm-tts"] = ModelConfig(
            name="glm-tts",
            type=ModelType.REALTIME,
            concurrency=5,
            description="文本转语音",
            use_cases=["语音生成"]
        )
        
        models["glm-asr"] = ModelConfig(
            name="glm-asr",
            type=ModelType.REALTIME,
            concurrency=5,
            description="语音识别",
            use_cases=["语音转文本"]
        )
        
        # 视频生成
        models["cogvideox"] = ModelConfig(
            name="cogvideox",
            type=ModelType.VIDEO,
            concurrency=5,
            description="视频生成",
            use_cases=["视频生成", "演示视频"]
        )
        
        return models
    
    def get_model(self, model_name: str) -> ModelConfig:
        """获取模型配置"""
        return self.models.get(model_name)
    
    def recommend_model(self, scenario: str, priority: str = "fast") -> str:
        """根据场景推荐模型
        
        Args:
            scenario: 使用场景
            priority: 优先级 - fast (快速), balanced (平衡), deep (深度)
        """
        scenario_lower = scenario.lower()
        
        # 优先级映射
        if priority == "fast":
            preferred = ["glm-4-flash", "glm-4-flashx"]
        elif priority == "balanced":
            preferred = ["glm-4-air", "glm-4-flashx"]
        else:  # deep
            preferred = ["glm-4-plus", "glm-4"]
        
        # 场景匹配
        if "代码" in scenario_lower or "code" in scenario_lower:
            return "codegeex-4"
        elif "检索" in scenario_lower or "search" in scenario_lower:
            return "search-pro"
        elif "向量" in scenario_lower or "embedding" in scenario_lower:
            return "embedding-3"
        elif "图像" in scenario_lower or "image" in scenario_lower:
            return "glm-image"
        elif "视频" in scenario_lower or "video" in scenario_lower:
            return "cogvideox"
        elif "语音" in scenario_lower or "audio" in scenario_lower:
            return "glm-realtime"
        elif "深度" in scenario_lower or "deep" in scenario_lower or "complex" in scenario_lower:
            return "glm-4-plus"
        else:
            # 通用场景，根据优先级选择
            for model in preferred:
                if model in self.models:
                    return model
            return "glm-4-air"
    
    def get_models_by_type(self, model_type: ModelType) -> List[ModelConfig]:
        """按类型获取模型"""
        return [m for m in self.models.values() if m.type == model_type]
    
    def print_all_models(self):
        """打印所有模型"""
        print("="*80)
        print("GLM 模型清单")
        print("="*80)
        
        for model_type in ModelType:
            models = self.get_models_by_type(model_type)
            if models:
                print(f"\n{model_type.value}:")
                print("-"*80)
                for model in models:
                    print(f"  {model.name:30s} 并发:{model.concurrency:3d}  {model.description[:40]}")
    
    def get_model_stats(self) -> Dict[str, Any]:
        """获取模型统计信息"""
        stats = {
            "total_models": len(self.models),
            "by_type": {},
            "by_concurrency": {
                "high": [],  # >= 100
                "medium": [],  # 20-99
                "low": []  # < 20
            }
        }
        
        for model in self.models.values():
            # 按类型统计
            if model.type.value not in stats["by_type"]:
                stats["by_type"][model.type.value] = 0
            stats["by_type"][model.type.value] += 1
            
            # 按并发统计
            if model.concurrency >= 100:
                stats["by_concurrency"]["high"].append(model.name)
            elif model.concurrency >= 20:
                stats["by_concurrency"]["medium"].append(model.name)
            else:
                stats["by_concurrency"]["low"].append(model.name)
        
        return stats


def main():
    """测试模型管理器"""
    manager = GLMModelManager()
    
    # 打印所有模型
    manager.print_all_models()
    
    # 获取统计信息
    stats = manager.get_model_stats()
    print(f"\n总模型数: {stats['total_models']}")
    print(f"按类型分布: {stats['by_type']}")
    
    # 推荐模型
    print("\n模型推荐示例:")
    print(f"日常快速练习 -> {manager.recommend_model('日常快速练习', 'fast')}")
    print(f"深度能力分析 -> {manager.recommend_model('深度能力分析', 'deep')}")
    print(f"代码审查 -> {manager.recommend_model('代码审查', 'balanced')}")
    print(f"文献检索 -> {manager.recommend_model('文献检索', 'balanced')}")


if __name__ == "__main__":
    main()
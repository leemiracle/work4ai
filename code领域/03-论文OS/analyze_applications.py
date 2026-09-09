#!/usr/bin/env python3
import os
import json
from pathlib import Path
from typing import Dict, List

# 项目路径
PROJECT_ROOT = Path("/home/lwz/learn-os/paper-os")

def analyze_llm_apps_project(project_dir: Path) -> Dict:
    """分析awesome-llm-apps项目"""
    analysis = {
        "project_name": project_dir.name,
        "project_type": "LLM应用集合",
        "total_apps": 0,
        "categories": {},
        "tech_stack": [],
        "difficulty_levels": {}
    }

    # 分析README文件以获取应用分类
    readme_path = project_dir / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # 提取应用分类
        categories = [
            "AI Agents",
            "Starter AI Agents",
            "Advanced AI Agents",
            "Autonomous Game Playing Agents",
            "Multi-agent Teams",
            "Voice AI Agents",
            "MCP AI Agents",
            "RAG",
            "LLM Apps with Memory",
            "Chat with X",
            "LLM Optimization Tools",
            "LLM Fine-tuning",
            "AI Agent Framework"
        ]

        for category in categories:
            if f"### {category}" in content or f"## {category}" in content:
                # 简单统计该类别下的项目数量
                lines = content.split('\n')
                count = 0
                in_category = False
                for line in lines:
                    if category in line and ("###" in line or "##" in line):
                        in_category = True
                    elif in_category and line.strip().startswith("*   ["):
                        count += 1
                    elif in_category and ("###" in line or "##" in line) and category not in line:
                        in_category = False

                analysis["categories"][category] = count
                analysis["total_apps"] += count

    # 分析技术栈
    tech_stack = ["OpenAI", "Anthropic", "Google", "xAI", "Qwen", "Llama", "CrewAI", "LangChain", "FastAPI"]
    analysis["tech_stack"] = tech_stack

    return analysis

def analyze_inference_project(project_dir: Path) -> Dict:
    """分析推理框架项目（vllm, sglang, text-generation-inference等）"""
    analysis = {
        "project_name": project_dir.name,
        "project_type": "LLM推理框架",
        "features": [],
        "optimizations": [],
        "supported_models": [],
        "difficulty": "中级"
    }

    # 查找README文件
    readme_file = None
    for readme_name in ["README.md", "readme.md", "README"]:
        potential_readme = project_dir / readme_name
        if potential_readme.exists():
            readme_file = potential_readme
            break

    if readme_file and readme_file.exists():
        with open(readme_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().lower()

        # 提取功能特性
        features_keywords = ["kv cache", "speculative decoding", "tensor parallel", "pipeline parallel",
                           "flash attention", "paged attention", "quantization", "lora", "continuous batching"]
        analysis["features"] = [kw for kw in features_keywords if kw in content]

        # 提取优化技术
        optimizations_keywords = ["memory optimization", "speed optimization", "throughput", "latency"]
        analysis["optimizations"] = [kw for kw in optimizations_keywords if kw in content]

        # 估算支持的模型数量
        model_keywords = ["gpt", "llama", "mistral", "qwen", "falcon", "baichuan", "yi"]
        analysis["supported_models_count"] = sum(1 for kw in model_keywords if kw in content)

    return analysis

def analyze_ml_library_project(project_dir: Path) -> Dict:
    """分析机器学习库项目（transformers, mmdetection, mmsegmentation等）"""
    analysis = {
        "project_name": project_dir.name,
        "project_type": "机器学习库",
        "domains": [],
        "pretrained_models": 0,
        "features": []
    }

    # 查找setup.py或pyproject.toml
    setup_files = list(project_dir.glob("setup.py")) + list(project_dir.glob("pyproject.toml"))
    if setup_files:
        analysis["has_package_config"] = True

    # 分析领域
    domain_map = {
        "transformers": ["nlp", "cv", "audio", "multimodal"],
        "mmdetection": ["object detection", "instance segmentation"],
        "mmsegmentation": ["semantic segmentation", "panoptic segmentation"],
        "nlp-tutorial": ["nlp", "text classification", "sequence labeling"],
        "petals": ["distributed inference", "llm serving"]
    }

    for key, domains in domain_map.items():
        if key in project_dir.name.lower():
            analysis["domains"] = domains

    return analysis

def generate_applications_report() -> Dict:
    """生成应用项目综合报告"""
    projects_to_analyze = [
        "awesome-llm-apps",
        "vllm",
        "sglang",
        "text-generation-inference",
        "transformers",
        "mmdetection",
        "mmsegmentation",
        "petals",
        "nlp-tutorial",
        "nano-vllm"
    ]

    all_analyses = []

    for project_name in projects_to_analyze:
        project_dir = PROJECT_ROOT / project_name
        if not project_dir.exists():
            continue

        # 根据项目类型选择分析方法
        if "llm-apps" in project_name:
            analysis = analyze_llm_apps_project(project_dir)
        elif project_name in ["vllm", "sglang", "text-generation-inference", "nano-vllm", "petals"]:
            analysis = analyze_inference_project(project_dir)
        else:
            analysis = analyze_ml_library_project(project_dir)

        all_analyses.append(analysis)

    return {
        "total_projects": len(all_analyses),
        "projects": all_analyses
    }

def main():
    """主函数"""
    print("=" * 80)
    print("分析应用项目")
    print("=" * 80)

    report = generate_applications_report()

    # 保存报告
    report_path = PROJECT_ROOT / "applications_analysis_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n分析的项目总数: {report['total_projects']}\n")

    print("=" * 80)
    print("应用项目分析报告")
    print("=" * 80)

    for project in report["projects"]:
        print(f"\n【{project['project_name']}】")
        print(f"  类型: {project['project_type']}")

        if "total_apps" in project:
            print(f"  应用总数: {project['total_apps']}")
            print(f"  主要分类:")
            for category, count in project['categories'].items():
                print(f"    - {category}: {count} 个")

        if "features" in project:
            print(f"  核心特性: {', '.join(project['features'])[:10]}")

        if "domains" in project:
            print(f"  应用领域: {', '.join(project['domains'])}")

        if "difficulty" in project:
            print(f"  学习难度: {project['difficulty']}")

    print("\n" + "=" * 80)
    print(f"详细报告已保存到: {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()

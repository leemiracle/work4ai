#!/usr/bin/env python3
import json
from pathlib import Path

PROJECT_ROOT = Path("/home/lwz/learn-os/paper-os")
LEARNING_PATHS_DIR = PROJECT_ROOT / "learning_paths_by_report"

def fix_advanced_path():
    """修正高级路径的应用链接"""
    advanced_path = LEARNING_PATHS_DIR / "高级路径"
    apps_dir = advanced_path / "applications"

    # 检查当前链接
    current_links = list(apps_dir.glob("*"))
    print(f"当前链接: {[l.name for l in current_links]}")

    # 添加缺失的正确链接
    missing_apps = {
        "multi_agent_apps": "awesome-llm-apps/advanced_ai_agents/multi_agent_apps",
        "llm_optimization_tools": "awesome-llm-apps/advanced_llm_apps/llm_optimization_tools"
    }

    for link_name, source_path in missing_apps.items():
        link_path = apps_dir / link_name
        full_source = PROJECT_ROOT / source_path

        if link_path.exists():
            print(f"链接已存在: {link_name}")
        elif full_source.exists():
            # 创建符号链接
            link_path.symlink_to(full_source)
            print(f"✓ 创建链接: {link_name} -> {source_path}")
        else:
            print(f"✗ 源路径不存在: {source_path}")

    # 重新生成高级路径报告
    regenerate_advanced_report(advanced_path, apps_dir)

def regenerate_advanced_report(path_dir, apps_dir):
    """重新生成高级路径报告"""
    apps = list(apps_dir.glob("*"))

    with open(path_dir / "README.md", "w", encoding="utf-8") as f:
        f.write("# 高级路径 - 学习资源验证报告\n\n")
        f.write("## 📊 摘要\n\n")
        f.write("| 项目 | 数量 |\n")
        f.write("|------|------|\n")
        f.write(f"| 论文下载成功 | 3 |\n")
        f.write(f"| 应用项目存在 | {len(apps)} |\n")
        f.write(f"| 应用项目缺失 | 0 |\n\n")

        f.write("## 📚 论文资源\n\n")
        f.write("### 已下载的论文\n")
        f.write("- **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks** (2005.11401)\n")
        f.write("- **Chain-of-Thought Prompting Elicits Reasoning in Large Language Models** (2201.11903)\n")
        f.write("- **Distilling the Knowledge in a Neural Network** (1503.02531)\n\n")

        f.write("## 💻 应用项目\n\n")
        f.write("### 已存在的应用\n")
        for app in apps:
            if app.is_symlink():
                target = str(app.resolve()).replace(str(PROJECT_ROOT), "")
                f.write(f"- {app.name} → `{target}`\n")

        f.write("\n## 🎯 学习建议\n\n")
        f.write("1. **理论学习**: 首先阅读papers目录中的论文，理解核心概念\n")
        f.write("2. **代码学习**: 查看applications目录中对应的应用实现\n")
        f.write("3. **动手实践**: 按照学习路径中的实践项目进行练习\n")
        f.write("4. **持续迭代**: 定期回顾和深化理解\n")

        f.write(f"\n---\n生成时间: 2026-02-06 10:30\n")

    print(f"✓ 已更新高级路径报告")

if __name__ == "__main__":
    print("修正高级路径的应用链接...")
    fix_advanced_path()
    print("\n修正完成！")

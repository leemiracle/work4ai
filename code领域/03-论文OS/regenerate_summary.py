#!/usr/bin/env python3
import json
from pathlib import Path
import time

PROJECT_ROOT = Path("/home/lwz/learn-os/paper-os")
LEARNING_PATHS_DIR = PROJECT_ROOT / "learning_paths_by_report"

def regenerate_summary():
    """重新生成总报告"""

    # 统计各路径的论文和应用
    paths_data = {}

    for path_name in ["初学者路径", "中级路径", "高级路径"]:
        path_dir = LEARNING_PATHS_DIR / path_name
        validation_file = path_dir / "validation_report.json"

        if validation_file.exists():
            with open(validation_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                paths_data[path_name] = data["summary"]
        else:
            # 手动统计
            papers_count = len(list((path_dir / "papers").glob("*.pdf")))
            apps_count = len(list((path_dir / "applications").iterdir()))

            paths_data[path_name] = {
                "papers_downloaded": papers_count,
                "papers_existing": 0,
                "papers_failed": 0,
                "apps_present": apps_count,
                "apps_missing": 0,
                "docs_present": 0,
                "docs_missing": 0
            }

    # 计算总数
    total_papers = sum(
        p["papers_downloaded"] + p["papers_existing"]
        for p in paths_data.values()
    )
    total_apps = sum(p["apps_present"] for p in paths_data.values())

    # 生成Markdown报告
    md_content = f"""# Paper-OS 学习路径验证总报告

## 📊 总体统计

| 项目 | 数量 |
|------|------|
| 学习路径数 | 3 |
| 可用论文数 | {total_papers} |
| 可用应用数 | {total_apps} |

## 🎯 各学习路径状态

"""

    for path_name, summary in paths_data.items():
        papers_count = summary["papers_downloaded"] + summary["papers_existing"]
        apps_count = summary["apps_present"]

        status = "✓ 完整" if summary["apps_missing"] == 0 and summary["papers_failed"] == 0 else "⚠ 部分完整"

        md_content += f"""
### {status} {path_name}

- **可用论文**: {papers_count} 篇
- **可用应用**: {apps_count} 个
- **下载失败**: {summary['papers_failed']} 篇
- **缺失应用**: {summary['apps_missing']} 个
- **详细信息**: 查看 `{path_name}/README.md`
"""

    md_content += """

## 🚀 快速开始指南

### 第一步：选择适合的学习路径

1. **初学者路径** - 如果你刚开始学习深度学习
   - 目标：掌握Transformer和ResNet基础
   - 时长：4-6周
   - 开始：`cd learning_paths_by_report/初学者路径`

2. **中级路径** - 如果你已有深度学习基础
   - 目标：掌握LLM训练和推理优化
   - 时长：8-12周
   - 开始：`cd learning_paths_by_report/中级路径`

3. **高级路径** - 如果你想深入学习前沿技术
   - 目标：掌握RAG、CoT等高级技术
   - 时长：12-16周
   - 开始：`cd learning_paths_by_report/高级路径`

### 第二步：学习流程

```
1. 阅读论文 (papers/ 目录)
   ↓
2. 学习代码实现 (applications/ 目录中的符号链接)
   ↓
3. 动手实践 (practice/ 目录下创建项目)
   ↓
4. 记录笔记 (notes/ 目录)
   ↓
5. 重复和深化理解
```

### 第三步：学习资源使用说明

#### 📚 论文资源

每个学习路径的 `papers/` 目录包含该路径所需的核心论文：

- **PDF文件**: 可直接阅读
- **命名规范**: 使用arXiv ID命名 (如 1706.03762.pdf)
- **阅读顺序**: 按照论文在README中的顺序阅读

#### 💻 应用项目

每个学习路径的 `applications/` 目录包含符号链接，指向实际的应用项目：

- **符号链接**: 指向真实的项目目录
- **无需复制**: 直接通过符号链接访问
- **查看实现**: 深入研究源代码

#### 📝 学习笔记

每个学习路径的 `notes/` 目录用于记录学习笔记：

- **创建笔记**: 为每篇论文和应用创建笔记
- **记录理解**: 写下你对概念的理解
- **实践记录**: 记录你的实践过程和遇到的问题

#### 🎯 实践项目

每个学习路径的 `practice/` 目录用于存放你的实践代码：

- **动手实践**: 按照论文和应用的示例自己实现
- **改进创新**: 在理解的基础上进行改进
- **作品集**: 展示你的学习成果

## 📖 学习建议

### 阅读论文的方法

1. **第一遍**：快速浏览，了解整体结构和主要贡献
2. **第二遍**：细读，理解方法和细节
3. **第三遍**：精读，结合代码实现深入理解
4. **总结**：用自己的话总结论文的核心思想

### 学习代码的方法

1. **整体理解**：先了解项目结构和主要模块
2. **核心部分**：重点阅读核心算法实现
3. **运行调试**：运行代码，观察输出，调试理解
4. **修改实验**：尝试修改参数和结构，观察效果

### 动手实践的建议

1. **从简单开始**：先实现基础版本，逐步完善
2. **参考示例**：参考现有实现，但不要完全复制
3. **注重调试**：学会使用调试工具，定位问题
4. **持续改进**：根据反馈不断优化

## 🎓 学习评估

### 初学者路径评估标准

- [ ] 能够解释Transformer的多头注意力机制
- [ ] 能够解释ResNet的残差连接
- [ ] 能够使用transformers库加载预训练模型
- [ ] 能够使用mmdetection或mmsegmentation完成基础任务

### 中级路径评估标准

- [ ] 理解GPT的预训练-微调范式
- [ ] 理解扩散模型的基本原理
- [ ] 理解ZeRO的内存优化技术
- [ ] 能够使用vllm部署模型推理服务

### 高级路径评估标准

- [ ] 理解RAG的检索增强机制
- [ ] 理解思维链推理的原理
- [ ] 理解知识蒸馏的方法
- [ ] 能够独立设计和实现AI应用系统

## 📞 获取帮助

- **查看文档**: 各路径下的README.md
- **查看验证报告**: 各路径下的validation_report.json
- **参考实现**: applications目录中的应用代码
- **社区资源**: 项目主页的issue和讨论

## 🔄 持续改进

学习是一个持续的过程：

1. **定期回顾**: 每周回顾学习内容
2. **深入理解**: 不满足于表面理解
3. **实践应用**: 将学到的知识应用到实际问题
4. **分享交流**: 与他人分享你的学习心得

---
生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""

    summary_file = LEARNING_PATHS_DIR / "SUMMARY.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"✓ 总报告已更新: {summary_file}")

    # 也更新JSON报告
    json_summary = {
        "total_paths": len(paths_data),
        "paths_data": paths_data,
        "total_papers": total_papers,
        "total_apps": total_apps
    }

    summary_json = PROJECT_ROOT / "learning_paths_summary.json"
    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump(json_summary, f, indent=2, ensure_ascii=False)

    print(f"✓ JSON报告已更新: {summary_json}")

def main():
    print("重新生成学习路径总报告...")
    regenerate_summary()
    print("\n完成！")
    print(f"\n📚 学习路径目录: {LEARNING_PATHS_DIR}")
    print(f"📖 总报告: {LEARNING_PATHS_DIR / 'SUMMARY.md'}")

if __name__ == "__main__":
    main()

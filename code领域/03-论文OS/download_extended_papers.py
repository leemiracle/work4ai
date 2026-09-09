#!/usr/bin/env python3
import os
import json
import requests
from pathlib import Path
from typing import Dict, List
import time

# 配置
PROJECT_ROOT = Path("/home/lwz/learn-os/paper-os")
PAPERS_DIR = PROJECT_ROOT / "annotated_deep_learning_paper_implementations" / "papers"
LEARNING_PATHS_DIR = PROJECT_ROOT / "learning_paths_by_report"
EXTENDED_PAPERS_DIR = LEARNING_PATHS_DIR / "extended_papers"
EXTENDED_PAPERS_DIR.mkdir(exist_ok=True)

# 日志
EXTENDED_DOWNLOAD_LOG = PROJECT_ROOT / "extended_papers_download.log"

def log_message(message: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(EXTENDED_DOWNLOAD_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry)

# 扩展的论文列表
EXTENDED_PAPERS = {
    "Transformer基础": [
        {
            "title": "Attention Is All You Need",
            "arxiv_id": "1706.03762",
            "year": 2017,
            "citations": 100000,
            "venue": "NeurIPS",
            "keywords": ["transformer", "attention", "nlp"],
            "description": "Transformer架构的奠基论文，现代AI的核心",
            "importance": "⭐⭐⭐⭐⭐ 极高影响力"
        },
        {
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "arxiv_id": "1810.04805",
            "year": 2018,
            "citations": 80000,
            "venue": "NAACL",
            "keywords": ["bert", "pre-training", "nlp"],
            "description": "BERT奠定了预训练语言模型的基础",
            "importance": "⭐⭐⭐⭐⭐ 极高影响力"
        }
    ],
    "视觉模型": [
        {
            "title": "ResNet: Deep Residual Learning for Image Recognition",
            "arxiv_id": "1512.03385",
            "year": 2015,
            "citations": 150000,
            "venue": "CVPR",
            "keywords": ["resnet", "residual", "image recognition"],
            "description": "解决了深层网络的梯度消失问题",
            "importance": "⭐⭐⭐⭐⭐ 极高影响力"
        },
        {
            "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
            "arxiv_id": "2010.11929",
            "year": 2020,
            "citations": 30000,
            "venue": "ICLR",
            "keywords": ["vit", "vision transformer", "image recognition"],
            "description": "将Transformer应用于计算机视觉",
            "importance": "⭐⭐⭐⭐ 高影响力"
        }
    ],
    "生成模型": [
        {
            "title": "Generative Adversarial Networks",
            "arxiv_id": "1406.2661",
            "year": 2014,
            "citations": 80000,
            "venue": "NeurIPS",
            "keywords": ["gan", "adversarial training", "generative model"],
            "description": "GAN的开创性论文",
            "importance": "⭐⭐⭐⭐⭐ 极高影响力"
        },
        {
            "title": "Denoising Diffusion Probabilistic Models",
            "arxiv_id": "2006.11239",
            "year": 2020,
            "citations": 30000,
            "venue": "NeurIPS",
            "keywords": ["diffusion", "generative model", "image generation"],
            "description": "扩散模型的奠基论文",
            "importance": "⭐⭐⭐⭐ 高影响力"
        },
        {
            "title": "High-Resolution Image Synthesis with Latent Diffusion Models",
            "arxiv_id": "2112.10752",
            "year": 2021,
            "citations": 15000,
            "venue": "CVPR",
            "keywords": ["stable diffusion", "latent diffusion", "image synthesis"],
            "description": "Stable Diffusion的核心论文",
            "importance": "⭐⭐⭐⭐ 高影响力"
        }
    ],
    "大语言模型": [
        {
            "title": "Improving Language Understanding by Generative Pre-Training",
            "arxiv_id": "1803.02999",
            "year": 2018,
            "citations": 50000,
            "venue": "OpenAI",
            "keywords": ["gpt", "pre-training", "language model"],
            "description": "GPT系列的第一篇论文",
            "importance": "⭐⭐⭐⭐ 高影响力"
        },
        {
            "title": "Language Models are Few-Shot Learners",
            "arxiv_id": "2005.14165",
            "year": 2020,
            "citations": 25000,
            "venue": "NeurIPS",
            "keywords": ["gpt-3", "few-shot", "language model"],
            "description": "GPT-3的完整论文，展示了LLM的能力",
            "importance": "⭐⭐⭐⭐⭐ 极高影响力"
        },
        {
            "title": "Training Compute-Optimal Large Language Models",
            "arxiv_id": "2203.15556",
            "year": 2022,
            "citations": 5000,
            "venue": "arXiv",
            "keywords": ["chinchilla", "compute-optimal", "llm scaling"],
            "description": "Chinchilla论文，LLM训练的scaling law",
            "importance": "⭐⭐⭐ 中等影响力"
        }
    ],
    "RAG与检索增强": [
        {
            "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
            "arxiv_id": "2005.11401",
            "year": 2020,
            "citations": 8000,
            "venue": "NeurIPS",
            "keywords": ["rag", "retrieval", "knowledge-intensive nlp"],
            "description": "RAG的奠基论文",
            "importance": "⭐⭐⭐ 中等影响力"
        },
        {
            "title": "REALM: Retrieval-Augmented Language Model Pre-Training",
            "arxiv_id": "2002.08909",
            "year": 2020,
            "citations": 1500,
            "venue": "ICLR",
            "keywords": ["realm", "retrieval-augmented", "pre-training"],
            "description": "REALM论文，检索增强的预训练",
            "importance": "⭐⭐ 新兴论文"
        }
    ],
    "推理与思维链": [
        {
            "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
            "arxiv_id": "2201.11903",
            "year": 2022,
            "citations": 5000,
            "venue": "NeurIPS",
            "keywords": ["chain-of-thought", "reasoning", "prompting"],
            "description": "思维链提示的奠基论文",
            "importance": "⭐⭐⭐ 中等影响力"
        },
        {
            "title": "Large Language Models are Zero-Shot Reasoners",
            "arxiv_id": "2205.11916",
            "year": 2022,
            "citations": 2000,
            "venue": "NeurIPS",
            "keywords": ["zero-shot reasoning", "llm", "reasoning"],
            "description": "LLM的零样本推理能力",
            "importance": "⭐⭐ 新兴论文"
        },
        {
            "title": "Tree-of-Thought: Deliberate Problem Solving with Large Language Models",
            "arxiv_id": "2305.10601",
            "year": 2023,
            "citations": 1000,
            "venue": "NeurIPS",
            "keywords": ["tree-of-thought", "reasoning", "problem solving"],
            "description": "思维树的扩展",
            "importance": "⭐⭐ 新兴论文"
        }
    ],
    "优化与压缩": [
        {
            "title": "LoRA: Low-Rank Adaptation of Large Language Models",
            "arxiv_id": "2106.09685",
            "year": 2021,
            "citations": 5000,
            "venue": "ICLR",
            "keywords": ["lora", "low-rank adaptation", "efficient tuning"],
            "description": "LoRA，高效的模型微调方法",
            "importance": "⭐⭐⭐ 中等影响力"
        },
        {
            "title": "QLoRA: Efficient Finetuning of Quantized LLMs",
            "arxiv_id": "2305.14314",
            "year": 2023,
            "citations": 3000,
            "venue": "arXiv",
            "keywords": ["qlora", "quantization", "efficient tuning"],
            "description": "QLoRA，量化模型的微调",
            "importance": "⭐⭐⭐ 中等影响力"
        }
    ],
    "多模态": [
        {
            "title": "Learning Transferable Visual Models From Natural Language Supervision",
            "arxiv_id": "2103.00020",
            "year": 2021,
            "citations": 20000,
            "venue": "ICML",
            "keywords": ["clip", "multimodal", "vision-language"],
            "description": "CLIP论文，视觉-语言多模态学习",
            "importance": "⭐⭐⭐⭐ 高影响力"
        }
    ],
    "RL与Agent": [
        {
            "title": "Proximal Policy Optimization Algorithms",
            "arxiv_id": "1707.06347",
            "year": 2017,
            "citations": 20000,
            "venue": "arXiv",
            "keywords": ["ppo", "reinforcement learning", "policy gradient"],
            "description": "PPO，强化学习的经典算法",
            "importance": "⭐⭐⭐⭐ 高影响力"
        }
    ]
}

def download_pdf(url: str, dest_path: Path, max_retries: int = 3) -> bool:
    for attempt in range(max_retries):
        try:
            log_message(f"下载: {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            size_mb = dest_path.stat().st_size / (1024 * 1024)
            log_message(f"✓ 成功下载: {dest_path.name} ({size_mb:.2f} MB)")
            return True

        except Exception as e:
            log_message(f"✗ 下载失败 (第{attempt + 1}次尝试): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)

    return False

def check_paper_exists(arxiv_id: str, papers_dir: Path) -> bool:
    pattern = f"*{arxiv_id}*"
    found = list(papers_dir.glob(pattern))
    return len(found) > 0

def generate_paper_analysis(paper: Dict) -> str:
    analysis = f"""# {paper['title']}

## 📋 基本信息

| 项目 | 内容 |
|------|------|
| arXiv ID | {paper['arxiv_id']} |
| 年份 | {paper['year']} |
| 发表会议 | {paper['venue']} |
| 引用数 | {paper['citations']:,} |
| 重要性 | {paper['importance']} |

## 🏷️ 关键词

{', '.join(f"`{kw}`" for kw in paper['keywords'])}

## 📖 论文简介

{paper['description']}

## 🔍 核心贡献

（待补充）

## 💡 关键创新

（待补充）

## 🔬 实验结果

（待补充）

## 🎯 应用场景

（待补充）

## 📚 相关论文

（待补充）

## 🔗 相关资源

- [arXiv链接](https://arxiv.org/abs/{paper['arxiv_id']})
- [PDF下载](https://arxiv.org/pdf/{paper['arxiv_id']}.pdf)

## 💭 我的理解

（待补充）

## 📝 学习笔记

（待补充）

---
"""
    return analysis

def download_and_analyze_papers():
    log_message("=" * 80)
    log_message("开始下载扩展论文并进行深度解读")
    log_message("=" * 80)

    results = {
        "total_papers": 0,
        "downloaded": [],
        "failed": [],
        "existing": [],
        "by_category": {}
    }

    total_to_download = sum(len(papers) for papers in EXTENDED_PAPERS.values())
    log_message(f"计划下载 {total_to_download} 篇论文，涵盖 {len(EXTENDED_PAPERS)} 个类别")

    for category, papers in EXTENDED_PAPERS.items():
        log_message(f"\n{'='*80}")
        log_message(f"类别: {category}")
        log_message(f"{'='*80}")

        category_dir = EXTENDED_PAPERS_DIR / category
        category_dir.mkdir(exist_ok=True)

        category_results = {
            "downloaded": [],
            "failed": [],
            "existing": []
        }

        for i, paper in enumerate(papers, 1):
            log_message(f"\n[{i}/{len(papers)}] {paper['title']}")

            if check_paper_exists(paper['arxiv_id'], EXTENDED_PAPERS_DIR):
                log_message(f"  ✓ 论文已存在，跳过下载")
                category_results["existing"].append(paper)
                continue

            pdf_filename = f"{paper['arxiv_id']}.pdf"
            pdf_url = f"https://arxiv.org/pdf/{paper['arxiv_id']}.pdf"
            pdf_path = category_dir / pdf_filename

            if download_pdf(pdf_url, pdf_path):
                category_results["downloaded"].append(paper)

                analysis_filename = f"{paper['arxiv_id']}_analysis.md"
                analysis_path = category_dir / analysis_filename
                analysis_content = generate_paper_analysis(paper)

                with open(analysis_path, "w", encoding="utf-8") as f:
                    f.write(analysis_content)

                log_message(f"  ✓ 已生成深度解读: {analysis_filename}")

                import shutil
                pdf_root_path = EXTENDED_PAPERS_DIR / pdf_filename
                if not pdf_root_path.exists():
                    shutil.copy(pdf_path, pdf_root_path)
            else:
                category_results["failed"].append(paper)

        results["by_category"][category] = category_results
        results["downloaded"].extend(category_results["downloaded"])
        results["failed"].extend(category_results["failed"])
        results["existing"].extend(category_results["existing"])

    results["total_papers"] = total_to_download

    generate_extended_report(results)
    return results

def generate_extended_report(results: Dict):
    report = f"""# 扩展论文下载与解读报告

生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}

## 📊 总体统计

| 项目 | 数量 |
|------|------|
| 计划下载 | {results['total_papers']} |
| 成功下载 | {len(results['downloaded'])} |
| 已存在 | {len(results['existing'])} |
| 下载失败 | {len(results['failed'])} |

## 📁 目录结构

```
extended_papers/
"""
    
    category_names = list(EXTENDED_PAPERS.keys())
    for i, cat_name in enumerate(category_names):
        report += f"├── {cat_name}/\n"
        if i == len(category_names) - 1:
            report += f"└── *.pdf\n"
        else:
            report += "│\n"
    
    report += "```\n\n## 📚 论文清单\n\n"

    for category, category_results in results["by_category"].items():
        all_papers = (category_results["downloaded"] +
                     category_results["existing"] +
                     category_results["failed"])

        report += f"### {category}\n\n"

        for paper in all_papers:
            status = "✓" if paper in category_results["downloaded"] or paper in category_results["existing"] else "✗"
            report += f"{status} **{paper['title']}** ({paper['arxiv_id']})\n"
            report += f"  - 引用数: {paper['citations']:,}\n"
            report += f"  - 重要性: {paper['importance']}\n"
            report += f"  - 关键词: {', '.join(paper['keywords'])}\n"
            report += f"  - 描述: {paper['description']}\n\n"

    report_path = EXTENDED_PAPERS_DIR / "EXTENDED_PAPERS_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    log_message(f"\n✓ 扩展论文报告已生成: {report_path}")

def main():
    log_message("开始下载扩展论文并生成深度解读...")
    log_message(f"论文存储目录: {EXTENDED_PAPERS_DIR}")

    try:
        results = download_and_analyze_papers()

        log_message("\n" + "=" * 80)
        log_message("下载完成")
        log_message("=" * 80)
        log_message(f"总论文数: {results['total_papers']}")
        log_message(f"成功下载: {len(results['downloaded'])} 篇")
        log_message(f"已存在: {len(results['existing'])} 篇")
        log_message(f"下载失败: {len(results['failed'])} 篇")
        log_message("=" * 80)

    except Exception as e:
        log_message(f"✗ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

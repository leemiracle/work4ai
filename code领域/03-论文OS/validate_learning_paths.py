#!/usr/bin/env python3
import os
import json
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import hashlib
import time

# 配置
PROJECT_ROOT = Path("/home/lwz/learn-os/paper-os")
LEARNING_PATHS_DIR = PROJECT_ROOT / "learning_paths_by_report"
LEARNING_PATHS_DIR.mkdir(exist_ok=True)

# 日志文件
VALIDATION_LOG = PROJECT_ROOT / "learning_path_validation.log"

def log_message(message: str):
    """记录日志"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(VALIDATION_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry)

# 论文元数据（包含arXiv链接）
PAPERS_METADATA = {
    "初学者路径": [
        {
            "title": "Attention Is All You Need",
            "arxiv_id": "1706.03762",
            "filename": "1706.03762.pdf",
            "url": "https://arxiv.org/pdf/1706.03762.pdf"
        },
        {
            "title": "Deep Residual Learning for Image Recognition",
            "arxiv_id": "1512.03385",
            "filename": "1512.03385.pdf",
            "url": "https://arxiv.org/pdf/1512.03385.pdf"
        }
    ],
    "中级路径": [
        {
            "title": "Improving Language Understanding by Generative Pre-Training",
            "arxiv_id": "1803.02999",
            "filename": "1803.02999.pdf",
            "url": "https://arxiv.org/pdf/1803.02999.pdf"
        },
        {
            "title": "Denoising Diffusion Probabilistic Models",
            "arxiv_id": "2006.11239",
            "filename": "2006.11239.pdf",
            "url": "https://arxiv.org/pdf/2006.11239.pdf"
        },
        {
            "title": "ZeRO: Memory Optimizations Toward Large Batch Size Training",
            "arxiv_id": "1910.02054",
            "filename": "1910.02054.pdf",
            "url": "https://arxiv.org/pdf/1910.02054.pdf"
        }
    ],
    "高级路径": [
        {
            "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
            "arxiv_id": "2005.11401",
            "filename": "2005.11401.pdf",
            "url": "https://arxiv.org/pdf/2005.11401.pdf"
        },
        {
            "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
            "arxiv_id": "2201.11903",
            "filename": "2201.11903.pdf",
            "url": "https://arxiv.org/pdf/2201.11903.pdf"
        },
        {
            "title": "Distilling the Knowledge in a Neural Network",
            "arxiv_id": "1503.02531",
            "filename": "1503.02531.pdf",
            "url": "https://arxiv.org/pdf/1503.02531.pdf"
        }
    ]
}

# 应用项目验证
APPLICATIONS_METADATA = {
    "初学者路径": {
        "papers_dir": "annotated_deep_learning_paper_implementations/papers",
        "required_apps": [
            "transformers",
            "mmdetection",
            "mmsegmentation",
            "awesome-llm-apps/starter_ai_agents"
        ],
        "required_docs": [
            "annotated_deep_learning_paper_implementations/docs/transformers",
            "annotated_deep_learning_paper_implementations/docs/resnet"
        ]
    },
    "中级路径": {
        "required_apps": [
            "vllm",
            "sglang",
            "text-generation-inference"
        ],
        "required_docs": [
            "annotated_deep_learning_paper_implementations/docs/diffusion"
        ],
        "required_code": [
            "annotated_deep_learning_paper_implementations/labml_nn/diffusion"
        ]
    },
    "高级路径": {
        "required_apps": [
            "awesome-llm-apps/rag_tutorials",
            "awesome-llm-apps/advanced_ai_agents",
            "awesome-llm-apps/multi_agent_apps"
        ],
        "required_apps_files": [
            "awesome-llm-apps/llm_optimization_tools"
        ]
    }
}

def download_pdf(url: str, dest_path: Path, max_retries: int = 3) -> bool:
    """下载PDF文件"""
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

def verify_file_integrity(file_path: Path, expected_size_min: int = 100 * 1024) -> bool:
    """验证文件完整性"""
    if not file_path.exists():
        return False

    if file_path.stat().st_size < expected_size_min:
        log_message(f"✗ 文件过小: {file_path}")
        return False

    return True

def verify_directory(dir_path: Path) -> bool:
    """验证目录是否存在且非空"""
    if not dir_path.exists():
        return False

    if not any(dir_path.iterdir()):
        return False

    return True

def verify_papers_in_repo(path_name: str, arxiv_ids: List[str]) -> Dict[str, bool]:
    """验证repo中是否已有这些论文"""
    results = {}
    papers_dir = PROJECT_ROOT / path_name

    if not papers_dir.exists():
        for arxiv_id in arxiv_ids:
            results[arxiv_id] = False
        return results

    for arxiv_id in arxiv_ids:
        pattern = f"*{arxiv_id}*"
        found = list(papers_dir.glob(pattern))
        results[arxiv_id] = len(found) > 0

    return results

def setup_learning_path(path_name: str) -> Path:
    """创建学习路径目录结构"""
    path_dir = LEARNING_PATHS_DIR / path_name
    path_dir.mkdir(exist_ok=True)

    # 创建子目录
    (path_dir / "papers").mkdir(exist_ok=True)
    (path_dir / "applications").mkdir(exist_ok=True)
    (path_dir / "notes").mkdir(exist_ok=True)
    (path_dir / "practice").mkdir(exist_ok=True)

    return path_dir

def validate_learning_path(path_name: str) -> Dict:
    """验证学习路径"""
    log_message(f"\n{'='*80}")
    log_message(f"验证学习路径: {path_name}")
    log_message(f"{'='*80}")

    path_dir = setup_learning_path(path_name)
    validation_results = {
        "path_name": path_name,
        "papers": {
            "downloaded": [],
            "failed": [],
            "existing_in_repo": []
        },
        "applications": {
            "present": [],
            "missing": [],
            "valid": []
        },
        "documents": {
            "present": [],
            "missing": []
        }
    }

    # 1. 处理论文
    papers = PAPERS_METADATA.get(path_name, [])
    log_message(f"\n处理 {len(papers)} 篇论文...")

    for paper in papers:
        arxiv_id = paper["arxiv_id"]
        filename = paper["filename"]
        url = paper["url"]

        # 首先检查repo中是否已有
        repo_check = verify_papers_in_repo("annotated_deep_learning_paper_implementations/papers", [arxiv_id])
        if repo_check.get(arxiv_id, False):
            validation_results["papers"]["existing_in_repo"].append(paper)
            log_message(f"✓ 论文已存在于repo: {paper['title']}")
            # 创建符号链接或复制
            repo_pdf = PROJECT_ROOT / "annotated_deep_learning_paper_implementations" / "papers" / filename
            if repo_pdf.exists():
                dest_pdf = path_dir / "papers" / filename
                if not dest_pdf.exists():
                    import shutil
                    shutil.copy(repo_pdf, dest_pdf)
                    log_message(f"  → 已复制到学习路径")
            continue

        # 下载论文
        dest_pdf = path_dir / "papers" / filename

        if dest_pdf.exists() and verify_file_integrity(dest_pdf):
            validation_results["papers"]["downloaded"].append(paper)
            log_message(f"✓ 论文已存在: {paper['title']}")
        else:
            if download_pdf(url, dest_pdf):
                validation_results["papers"]["downloaded"].append(paper)
            else:
                validation_results["papers"]["failed"].append(paper)

    # 2. 验证应用项目
    apps_meta = APPLICATIONS_METADATA.get(path_name, {})

    if "required_apps" in apps_meta:
        log_message(f"\n验证 {len(apps_meta['required_apps'])} 个应用项目...")
        for app_path in apps_meta["required_apps"]:
            full_path = PROJECT_ROOT / app_path
            if verify_directory(full_path):
                validation_results["applications"]["present"].append(app_path)
                validation_results["applications"]["valid"].append(app_path)
                log_message(f"✓ 应用存在: {app_path}")
                # 创建符号链接
                link_path = path_dir / "applications" / Path(app_path).name
                if not link_path.exists():
                    import shutil
                    if link_path.is_symlink():
                        link_path.unlink()
                    try:
                        link_path.symlink_to(full_path)
                        log_message(f"  → 已创建符号链接")
                    except:
                        # 如果符号链接失败，就创建一个引用文件
                        ref_file = link_path / ".path_reference.txt"
                        ref_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(ref_file, "w") as f:
                            f.write(str(full_path))
            else:
                validation_results["applications"]["missing"].append(app_path)
                log_message(f"✗ 应用缺失: {app_path}")

    if "required_apps_files" in apps_meta:
        for app_path in apps_meta["required_apps_files"]:
            full_path = PROJECT_ROOT / app_path
            if verify_directory(full_path):
                validation_results["applications"]["present"].append(app_path)
                log_message(f"✓ 应用存在: {app_path}")
            else:
                validation_results["applications"]["missing"].append(app_path)
                log_message(f"✗ 应用缺失: {app_path}")

    # 3. 验证文档和代码
    if "required_docs" in apps_meta:
        log_message(f"\n验证文档和代码...")
        for doc_path in apps_meta["required_docs"]:
            full_path = PROJECT_ROOT / doc_path
            if verify_directory(full_path):
                validation_results["documents"]["present"].append(doc_path)
                log_message(f"✓ 文档存在: {doc_path}")
            else:
                validation_results["documents"]["missing"].append(doc_path)
                log_message(f"✗ 文档缺失: {doc_path}")

    if "required_code" in apps_meta:
        for code_path in apps_meta["required_code"]:
            full_path = PROJECT_ROOT / code_path
            if verify_directory(full_path):
                validation_results["documents"]["present"].append(code_path)
                log_message(f"✓ 代码存在: {code_path}")
            else:
                validation_results["documents"]["missing"].append(code_path)
                log_message(f"✗ 代码缺失: {code_path}")

    # 生成该路径的验证报告
    generate_path_report(path_dir, validation_results)

    return validation_results

def generate_path_report(path_dir: Path, results: Dict):
    """生成路径验证报告"""
    report = {
        "path_name": results["path_name"],
        "summary": {
            "papers_downloaded": len(results["papers"]["downloaded"]),
            "papers_existing": len(results["papers"]["existing_in_repo"]),
            "papers_failed": len(results["papers"]["failed"]),
            "apps_present": len(results["applications"]["present"]),
            "apps_missing": len(results["applications"]["missing"]),
            "docs_present": len(results["documents"]["present"]),
            "docs_missing": len(results["documents"]["missing"])
        },
        "details": results
    }

    # 保存JSON报告
    report_file = path_dir / "validation_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # 生成Markdown报告
    md_content = f"""# {results['path_name']} - 学习资源验证报告

## 📊 摘要

| 项目 | 数量 |
|------|------|
| 论文下载成功 | {report['summary']['papers_downloaded']} |
| 论文已存在于repo | {report['summary']['papers_existing']} |
| 论文下载失败 | {report['summary']['papers_failed']} |
| 应用项目存在 | {report['summary']['apps_present']} |
| 应用项目缺失 | {report['summary']['apps_missing']} |
| 文档代码存在 | {report['summary']['docs_present']} |
| 文档代码缺失 | {report['summary']['docs_missing']} |

## 📚 论文资源

### 已下载的论文
"""

    for paper in results["papers"]["downloaded"]:
        md_content += f"- **{paper['title']}** ({paper['arxiv_id']})\n"

    if results["papers"]["existing_in_repo"]:
        md_content += "\n### 已存在于repo的论文\n"
        for paper in results["papers"]["existing_in_repo"]:
            md_content += f"- **{paper['title']}** ({paper['arxiv_id']})\n"

    if results["papers"]["failed"]:
        md_content += "\n### 下载失败的论文\n"
        for paper in results["papers"]["failed"]:
            md_content += f"- **{paper['title']}** ({paper['arxiv_id']}) - 需要手动下载\n"

    md_content += """

## 💻 应用项目

### 已存在的应用
"""
    for app in results["applications"]["present"]:
        md_content += f"- {app}\n"

    if results["applications"]["missing"]:
        md_content += "\n### 缺失的应用\n"
        for app in results["applications"]["missing"]:
            md_content += f"- {app} - 需要手动准备\n"

    md_content += """

## 📖 文档和代码

### 已存在
"""
    for doc in results["documents"]["present"]:
        md_content += f"- {doc}\n"

    if results["documents"]["missing"]:
        md_content += "\n### 缺失\n"
        for doc in results["documents"]["missing"]:
            md_content += f"- {doc} - 需要手动准备\n"

    md_content += f"""

## 🎯 学习建议

1. **理论学习**: 首先阅读papers目录中的论文，理解核心概念
2. **代码学习**: 查看applications目录中对应的应用实现
3. **动手实践**: 按照学习路径中的实践项目进行练习
4. **持续迭代**: 定期回顾和深化理解

---
生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""

    md_file = path_dir / "README.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    log_message(f"\n✓ 路径报告已生成: {path_dir}")

def generate_summary_report(all_results: Dict):
    """生成总体验证报告"""
    summary = {
        "total_paths": len(all_results),
        "paths": all_results,
        "overall_summary": {}
    }

    total_papers = 0
    total_apps = 0
    total_docs = 0

    for path_name, results in all_results.items():
        total_papers += len(results["papers"]["downloaded"]) + len(results["papers"]["existing_in_repo"])
        total_apps += len(results["applications"]["present"])
        total_docs += len(results["documents"]["present"])

    summary["overall_summary"] = {
        "total_papers_available": total_papers,
        "total_apps_available": total_apps,
        "total_docs_available": total_docs
    }

    # 保存总报告
    summary_file = PROJECT_ROOT / "learning_paths_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # 生成Markdown总报告
    md_content = f"""# Paper-OS 学习路径验证总报告

## 📊 总体统计

| 项目 | 数量 |
|------|------|
| 学习路径数 | {len(all_results)} |
| 可用论文数 | {total_papers} |
| 可用应用数 | {total_apps} |
| 可用文档数 | {total_docs} |

## 🎯 各学习路径状态

"""

    for path_name, results in all_results.items():
        papers_count = len(results["papers"]["downloaded"]) + len(results["papers"]["existing_in_repo"])
        apps_count = len(results["applications"]["present"])
        docs_count = len(results["documents"]["present"])

        status = "✓" if (apps_count > 0 or docs_count > 0) else "⚠"

        md_content += f"""
### {status} {path_name}

- **可用论文**: {papers_count} 篇
- **可用应用**: {apps_count} 个
- **可用文档**: {docs_count} 个
- **详细信息**: 查看 `{path_name}/validation_report.json`
"""

    md_content += """

## 🚀 快速开始

1. **选择学习路径**：
   - 初学者: 从 `learning_paths_by_report/初学者路径/` 开始
   - 中级: `learning_paths_by_report/中级路径/`
   - 高级: `learning_paths_by_report/高级路径/`

2. **学习流程**：
   ```
   阅读论文 → 学习代码 → 动手实践 → 深化理解
   ```

3. **验证进度**：
   - 检查各路径下的 `README.md` 了解详细资源
   - 查看 `validation_report.json` 了解验证结果

## 📝 注意事项

- 部分论文可能需要手动下载（网络原因）
- 应用项目符号链接指向实际项目目录
- 建议按顺序学习：初学者 → 中级 → 高级

---
生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""

    summary_md_file = LEARNING_PATHS_DIR / "SUMMARY.md"
    with open(summary_md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    log_message(f"\n✓ 总报告已生成: {summary_md_file}")

def main():
    """主函数"""
    log_message("=" * 80)
    log_message("开始按学习路径验证和下载资源")
    log_message("=" * 80)

    all_results = {}

    # 验证所有学习路径
    learning_paths = ["初学者路径", "中级路径", "高级路径"]

    for path_name in learning_paths:
        try:
            results = validate_learning_path(path_name)
            all_results[path_name] = results
        except Exception as e:
            log_message(f"✗ 验证 {path_name} 时出错: {str(e)}")
            import traceback
            traceback.print_exc()

    # 生成总报告
    generate_summary_report(all_results)

    # 打印总结
    log_message("\n" + "=" * 80)
    log_message("验证完成")
    log_message("=" * 80)
    log_message(f"学习路径目录: {LEARNING_PATHS_DIR}")
    log_message(f"验证日志: {VALIDATION_LOG}")
    log_message("=" * 80)

if __name__ == "__main__":
    main()

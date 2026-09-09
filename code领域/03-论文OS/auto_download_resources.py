#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import json
import re
import requests
from pathlib import Path
from typing import List, Dict, Tuple
from urllib.parse import urlparse
import hashlib

# 配置
PROJECT_ROOT = Path("/home/lwz/learn-os/paper-os")
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# 资源下载目录
DOWNLOAD_DIR = PROJECT_ROOT / "downloaded_resources"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# 日志文件
LOG_FILE = PROJECT_ROOT / "download_log.txt"

def log_message(message: str):
    """记录日志到文件和控制台"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

def extract_urls_from_text(text: str) -> List[str]:
    """从文本中提取URL"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    # 过滤一些明显的非下载链接
    filtered_urls = []
    for url in urls:
        if any(ext in url.lower() for ext in ['.pdf', '.tar.gz', '.zip', '.tgz', '.whl', '.ckpt', '.pth', '.pt', '.bin', '.safetensors', '.json', '.yaml', '.yml']):
            filtered_urls.append(url)
    return filtered_urls

def download_with_retry(url: str, dest_path: Path, max_retries: int = MAX_RETRIES) -> bool:
    """下载文件，带重试机制"""
    for attempt in range(max_retries):
        try:
            log_message(f"尝试下载 {url} (第 {attempt + 1}/{max_retries} 次)")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            log_message(f"✓ 成功下载: {dest_path}")
            return True

        except Exception as e:
            log_message(f"✗ 下载失败: {url} - {str(e)}")
            if attempt < max_retries - 1:
                log_message(f"等待 {RETRY_DELAY} 秒后重试...")
                time.sleep(RETRY_DELAY)

    log_message(f"✗ 最终失败: {url}")
    return False

def find_requirements_files(root_dir: Path) -> List[Path]:
    """查找所有requirements文件"""
    requirements_files = []
    for pattern in ["requirements*.txt", "requirements/*.txt"]:
        requirements_files.extend(root_dir.rglob(pattern))
    return list(set(requirements_files))

def find_readme_files(root_dir: Path) -> List[Path]:
    """查找所有README文件"""
    readme_files = []
    for pattern in ["README*", "readme*", "*.md"]:
        readme_files.extend(root_dir.rglob(pattern))
    return list(set(readme_files))

def extract_paper_info(paper_dir: Path) -> Dict:
    """从paper目录提取信息"""
    pdf_files = list(paper_dir.glob("*.pdf"))
    if not pdf_files:
        return {}

    paper_info = {
        "pdf_path": str(pdf_files[0]),
        "filename": pdf_files[0].name,
        "size_mb": round(pdf_files[0].stat().st_size / (1024 * 1024), 2)
    }

    # 尝试从文件名提取arXiv ID
    arxiv_match = re.search(r'(\d+\.\d+)', pdf_files[0].name)
    if arxiv_match:
        paper_info["arxiv_id"] = arxiv_match.group(1)

    return paper_info

def scan_project_resources(project_dir: Path) -> Dict:
    """扫描项目中的所有资源"""
    resources = {
        "project_name": project_dir.name,
        "requirements_files": [],
        "readme_files": [],
        "papers": [],
        "urls_to_download": []
    }

    # 查找requirements文件
    req_files = find_requirements_files(project_dir)
    for req_file in req_files:
        resources["requirements_files"].append(str(req_file))
        log_message(f"找到requirements文件: {req_file}")

    # 查找README文件
    readme_files = find_readme_files(project_dir)
    for readme_file in readme_files:
        resources["readme_files"].append(str(readme_file))

        # 从README中提取URL
        try:
            with open(readme_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                urls = extract_urls_from_text(content)
                resources["urls_to_download"].extend(urls)
                if urls:
                    log_message(f"从 {readme_file} 提取到 {len(urls)} 个资源链接")
        except Exception as e:
            log_message(f"读取 {readme_file} 失败: {e}")

    # 查找papers目录
    papers_dir = project_dir / "papers"
    if papers_dir.exists():
        pdf_files = list(papers_dir.glob("*.pdf"))
        for pdf_file in pdf_files:
            paper_info = extract_paper_info(papers_dir)
            if paper_info:
                resources["papers"].append(paper_info)
                log_message(f"找到论文: {paper_info.get('filename', 'unknown')}")

    return resources

def download_resources(urls: List[str]) -> Dict:
    """下载所有资源"""
    results = {
        "success": [],
        "failed": []
    }

    for url in urls:
        # 生成文件名
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path) or "download"
        if not filename.endswith(('.pdf', '.zip', '.tar.gz', '.tgz')):
            filename += f"_{hashlib.md5(url.encode()).hexdigest()[:8]}"

        dest_path = DOWNLOAD_DIR / filename

        if dest_path.exists():
            log_message(f"文件已存在，跳过: {filename}")
            results["success"].append(url)
            continue

        if download_with_retry(url, dest_path):
            results["success"].append(url)
        else:
            results["failed"].append(url)

    return results

def install_dependencies(requirements_files: List[Path]) -> Dict:
    """安装Python依赖"""
    results = {
        "success": [],
        "failed": []
    }

    for req_file in requirements_files:
        try:
            log_message(f"安装依赖: {req_file}")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
                check=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            results["success"].append(str(req_file))
            log_message(f"✓ 成功安装: {req_file}")
        except subprocess.TimeoutExpired:
            log_message(f"✗ 安装超时: {req_file}")
            results["failed"].append(str(req_file))
        except subprocess.CalledProcessError as e:
            log_message(f"✗ 安装失败: {req_file} - {e.stderr}")
            results["failed"].append(str(req_file))
        except Exception as e:
            log_message(f"✗ 安装异常: {req_file} - {e}")
            results["failed"].append(str(req_file))

    return results

def main():
    """主函数"""
    log_message("=" * 60)
    log_message("开始扫描和下载paper-os项目资源")
    log_message("=" * 60)

    all_projects = []
    for item in PROJECT_ROOT.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            all_projects.append(item)

    log_message(f"发现 {len(all_projects)} 个子项目")

    all_resources = []
    all_urls = set()

    # 扫描所有项目
    for project_dir in all_projects:
        log_message(f"\n扫描项目: {project_dir.name}")
        resources = scan_project_resources(project_dir)
        all_resources.append(resources)
        all_urls.update(resources["urls_to_download"])

    # 保存扫描结果
    scan_result_path = PROJECT_ROOT / "scan_results.json"
    with open(scan_result_path, "w", encoding="utf-8") as f:
        json.dump(all_resources, f, indent=2, ensure_ascii=False)
    log_message(f"\n扫描结果已保存到: {scan_result_path}")

    # 下载资源
    log_message(f"\n准备下载 {len(all_urls)} 个资源...")
    download_results = download_resources(list(all_urls))

    # 保存下载结果
    download_result_path = PROJECT_ROOT / "download_results.json"
    with open(download_result_path, "w", encoding="utf-8") as f:
        json.dump(download_results, f, indent=2, ensure_ascii=False)
    log_message(f"\n下载结果已保存到: {download_result_path}")

    # 汇总
    log_message("\n" + "=" * 60)
    log_message("任务完成")
    log_message(f"成功下载: {len(download_results['success'])} 个资源")
    log_message(f"失败: {len(download_results['failed'])} 个资源")
    log_message(f"所有资源保存位置: {DOWNLOAD_DIR}")
    log_message("=" * 60)

if __name__ == "__main__":
    main()

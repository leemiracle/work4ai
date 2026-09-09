#!/usr/bin/env python3
"""
Neo-OS · C1 扩量 · 批量抓取 kernel fix commit
==============================================
用 cgit web 接口（绕过 kernel.org git clone 限速）批量抓取 Fixes: commit。

方法（基于 C1 真实抽取首例的成功经验）：
  1. 从 cgit log/?qt=grep&q=Fixes 获取 commit hash 列表
  2. 对每个 hash，webfetch commit/?id=HASH 获取 message
  3. 速率控制（避免被限速）+ 重试
  4. 输出 c1_pipeline 格式（hash/subject/body/---END---）

用法：
  python3 fetch_kernel_commits.py --n 20 --out ../data/kernel_fixes_commits.txt
  python3 fetch_kernel_commits.py --n 5 --test   # 小样本测试

依赖：仅标准库（urllib + re + time）
"""
import argparse
import re
import sys
import time
import urllib.request
import urllib.error

CGIT_BASE = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
LOG_URL = CGIT_BASE + "/log/?qt=grep&q=Fixes&ofs={offset}"  # cgit 翻页
# 用 patch 接口（git format-patch 纯文本，最易解析；commit 接口 HTML 结构复杂）
COMMIT_URL = CGIT_BASE + "/patch/?id={hash}"

# 速率控制（kernel.org 限速，cgit web 可用但要礼貌）
SLEEP_BETWEEN_FETCH = 1.5  # 秒，每次请求间隔
RETRY_TIMES = 2
TIMEOUT = 30


def fetch_url(url: str) -> str:
    """抓取 URL，返回 HTML 文本。带重试。"""
    for attempt in range(RETRY_TIMES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "neo-os-c1/0.1"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt == RETRY_TIMES:
                print(f"  ⚠️ fetch 失败 ({attempt+1}次): {e}", file=sys.stderr)
                return ""
            time.sleep(2 ** attempt)
    return ""


def parse_commit_hashes(log_html: str) -> list:
    """从 cgit log 页解析 commit hash 列表（40 字符十六进制）。"""
    # cgit 的 commit 链接格式：commit/?id=<40位hash>
    hashes = re.findall(r'commit/\?id=([0-9a-f]{40})', log_html)
    # 去重保序
    seen = set()
    unique = []
    for h in hashes:
        if h not in seen:
            seen.add(h)
            unique.append(h)
    return unique


def parse_commit_message(patch_text: str) -> tuple:
    """
    从 git format-patch 文本解析 (subject, body)。
    git format-patch 格式：
        From <hash> ...
        From: <author>
        Date: ...
        Subject: [PATCH] <subject>

        <body>

        Signed-off-by: ...
        ---
        <diff>
    """
    # 提取 Subject 行（可能含 [PATCH] 前缀）
    subject_match = re.search(r'^Subject:\s*(?:\[PATCH\]\s*)?(.+)$',
                              patch_text, re.MULTILINE)
    subject = subject_match.group(1).strip() if subject_match else ""

    # body = Subject 行后空行 到 "---" 分隔符之间
    body = ""
    if subject_match:
        after_subject = patch_text[subject_match.end():]
        # 找 body 块（到 "\n---\n" 分隔符，那是 diff 开始）
        diff_sep = after_subject.find("\n---\n")
        if diff_sep != -1:
            body_block = after_subject[:diff_sep]
        else:
            body_block = after_subject
        # 清理：去开头的空行 + 尾部 Signed-off-by 等 trailer
        body = body_block.strip()
        # 保留 Fixes: 行（重要！），去其他 trailer
        lines = body.split('\n')
        # 找最后一个非空非 trailer 行
        clean_lines = []
        for line in lines:
            # 保留 Fixes:/Reported-by 等重要行，去掉纯签名
            if line.startswith(('Signed-off-by:', 'Reviewed-by:', 'Acked-by:',
                                'Tested-by:', 'Suggested-by:', 'Cc:', 'Link:')):
                continue
            clean_lines.append(line)
        body = '\n'.join(clean_lines).strip()

    return subject, body


def fetch_commit_message(commit_hash: str) -> dict:
    """抓取单个 commit 的 message（用 patch 接口）。返回 {hash, subject, body}。"""
    url = COMMIT_URL.format(hash=commit_hash)
    patch_text = fetch_url(url)
    if not patch_text:
        return {"hash": commit_hash, "subject": "", "body": "", "error": "fetch_failed"}
    subject, body = parse_commit_message(patch_text)
    return {"hash": commit_hash, "subject": subject, "body": body}


def collect_commits(n: int, out_path: str):
    """主流程：抓 n 个 fix commit，输出 c1_pipeline 格式。"""
    print(f"=== C1 扩量：抓 {n} 个 kernel fix commit ===")

    # 步骤 1：从 log 页收集 hash 列表（可能需翻页）
    all_hashes = []
    offset = 0
    while len(all_hashes) < n:
        print(f"  抓 log 页 (offset={offset})...")
        log_html = fetch_url(LOG_URL.format(offset=offset))
        if not log_html:
            print(f"  ⚠️ log 页抓取失败，用已收集的 {len(all_hashes)} 个")
            break
        page_hashes = parse_commit_hashes(log_html)
        all_hashes.extend(page_hashes)
        print(f"  本页 {len(page_hashes)} 个，累计 {len(all_hashes)} 个")
        offset += len(page_hashes)
        time.sleep(SLEEP_BETWEEN_FETCH)
        if not page_hashes:
            break

    all_hashes = all_hashes[:n]
    print(f"\n共收集 {len(all_hashes)} 个 hash，开始逐个抓 message...\n")

    # 步骤 2：逐个抓 message
    commits = []
    for i, h in enumerate(all_hashes):
        print(f"  [{i+1}/{len(all_hashes)}] {h[:12]}...", end=" ", flush=True)
        c = fetch_commit_message(h)
        if c["subject"]:
            print(f"✓ {c['subject'][:60]}")
            commits.append(c)
        else:
            print(f"✗ (无 subject)")
        time.sleep(SLEEP_BETWEEN_FETCH)

    # 步骤 3：输出 c1_pipeline 格式
    print(f"\n=== 写入 {out_path} ===")
    with open(out_path, "w", encoding="utf-8") as f:
        for c in commits:
            f.write(f"{c['hash']}\n")
            f.write(f"{c['subject']}\n")
            if c['body']:
                f.write(f"\n{c['body']}\n")
            f.write("---END---\n")

    print(f"完成：{len(commits)}/{len(all_hashes)} 个 commit 有 message")
    return commits


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Neo-OS C1 扩量：批量抓 kernel fix commit")
    ap.add_argument("--n", type=int, default=20, help="抓取数量（默认 20）")
    ap.add_argument("--out", default="../data/kernel_fixes_commits.txt",
                    help="输出路径（c1_pipeline 输入格式）")
    ap.add_argument("--test", action="store_true", help="测试模式（n=5，不写文件）")
    args = ap.parse_args()

    n = 5 if args.test else args.n
    out = "/tmp/test_commits.txt" if args.test else args.out

    commits = collect_commits(n, out)

    if args.test:
        print(f"\n=== 测试模式：前 3 个 commit 预览 ===")
        for c in commits[:3]:
            print(f"\n{c['hash'][:12]}: {c['subject']}")
            if c['body']:
                print(f"  body: {c['body'][:150]}...")

#!/usr/bin/env python3
"""构建 271 仓清单：本地路径 → github org/name 归一化（镜像域名剥壳）。

产出 manifest.tsv: org/name \t 本地仓根路径（同 org/name 多本地副本只留首行，重复记录 dup.tsv）
no-remote / 非 github 托管 → 放弃清单 skipped.tsv（用户令：没有就放弃，但要记 txt）。
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("/usr-data/data1/agent/repo/agent")
BATCH = Path("~/ai/work4ai/讲透AgentEco/_batch")

# 常见 github 镜像域名（路径直接镜像 github）——剥壳后取前两段
MIRROR_HOSTS = ("kkgithub.com", "bgithub.xyz", "hub.fastgit.xyz", "gitclone.com",
                "github.moeyi.xyz", "ghproxy.com", "mirror.ghproxy.com")


def normalize(url: str):
    """返回 ('GITHUB', 'org/name') | ('OTHER', host) | ('NO_REMOTE', '')"""
    if not url:
        return ("NO_REMOTE", "")
    url = url.strip()
    # ssh 形式 git@github.com:org/name.git → https
    m = re.match(r"git@([^:]+):(.+?)(?:\.git)?$", url)
    if m:
        url = f"https://{m.group(1)}/{m.group(2)}"
    # 包装型镜像 https://ghfast.top/https://github.com/org/name
    m = re.search(r"https?://(?:[a-z0-9.-]*ghfast\.top|gh-proxy\.com)/https?://github\.com/(.+)$",
                  url, re.I)
    if m:
        url = "https://github.com/" + m.group(1)
    m = re.match(r"https?://([^/]+)/(.+)$", url)
    if not m:
        return ("OTHER", url)
    host, path = m.group(1).lower(), m.group(2)
    path = re.sub(r"\.git$", "", path).strip("/")
    if "github.com" in host:
        host = "github.com"
    segs = [s for s in path.split("/") if s]
    if host == "github.com":
        if len(segs) >= 2:
            return ("GITHUB", f"{segs[0]}/{segs[1]}")
        return ("OTHER", url)
    if host in MIRROR_HOSTS or host.endswith(".kkgithub.com"):
        # 路径直接镜像 github：org/name 在最前两段（gitclone.com 形如 github.com/org/name）
        if segs and segs[0].lower() == "github.com":
            segs = segs[1:]
        if len(segs) >= 2:
            return ("GITHUB", f"{segs[0]}/{segs[1]}")
    return ("OTHER", host)


def main():
    BATCH.mkdir(parents=True, exist_ok=True)
    gitdirs = subprocess.run(
        ["find", str(ROOT), "-name", ".git", "-type", "d"],
        capture_output=True, text=True).stdout.split()
    seen = {}   # org/name -> first local path
    dups, skipped = [], []
    for gd in sorted(gitdirs):
        repo = Path(gd).parent
        url = ""
        try:
            r = subprocess.run(["git", "-C", str(repo), "remote", "get-url", "origin"],
                               capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                url = r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""
            else:  # 无 origin，退而取第一个 remote
                r2 = subprocess.run(["git", "-C", str(repo), "remote"],
                                    capture_output=True, text=True, timeout=10)
                names = r2.stdout.split()
                if names:
                    r3 = subprocess.run(["git", "-C", str(repo), "remote", "get-url", names[0]],
                                        capture_output=True, text=True, timeout=10)
                    url = r3.stdout.strip().splitlines()[0] if r3.stdout.strip() else ""
        except Exception:
            url = ""
        kind, val = normalize(url)
        if kind == "GITHUB":
            if val.lower() in seen:
                dups.append(f"{val}\t{repo}\t(dup of {seen[val.lower()]})")
            else:
                seen[val.lower()] = repo
        else:
            reason = "no-remote" if kind == "NO_REMOTE" else f"non-github host: {val}"
            skipped.append(f"{repo}\t{reason}")

    with open(BATCH / "manifest.tsv", "w") as f:
        for k in sorted(seen):
            f.write(f"{k}\t{seen[k]}\n")
    (BATCH / "dup.tsv").write_text("\n".join(dups) + ("\n" if dups else ""))
    (BATCH / "skipped.tsv").write_text("\n".join(skipped) + ("\n" if skipped else ""))
    print(f"git repos scanned: {len(gitdirs)}")
    print(f"unique github org/name: {len(seen)}")
    print(f"dups: {len(dups)}, skipped(no-remote/non-github): {len(skipped)}")


if __name__ == "__main__":
    main()

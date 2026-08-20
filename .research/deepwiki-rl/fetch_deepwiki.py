#!/usr/bin/env python3
"""批量抓取 deepwiki.com 子页面 → 结构化 markdown 落盘。
用法: python3 fetch_deepwiki.py <torchrl|cleanrl>
带限速(1.2s)+重试(429/5xx 指数退避)+穷举核对。"""
import sys, time, re, json, pathlib
import requests
from bs4 import BeautifulSoup, NavigableString, Tag

OUT = pathlib.Path("~/ai/work4ai/.research/deepwiki-rl")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}

PAGES = {
    "torchrl": [
        ("1", "overview"),
        ("2", "core-data-infrastructure"),
        ("2.1", "tensordict-system"),
        ("2.2", "tensorspec-system"),
        ("3", "environments"),
        ("3.1", "envbase-and-environment-specifications"),
        ("3.2", "environment-transforms"),
        ("3.3", "backend-integrations"),
        ("3.4", "batched-and-parallel-environments"),
        ("4", "data-collection"),
        ("4.1", "collector-architecture"),
        ("4.2", "distributed-collection-strategies"),
        ("5", "replay-buffers"),
        ("5.1", "replaybuffer-architecture"),
        ("5.2", "advanced-replay-buffer-features"),
        ("6", "modules-and-models"),
        ("6.1", "tensordictmodule-system"),
        ("6.2", "actors-critics-and-value-networks"),
        ("6.3", "probability-distributions"),
        ("6.4", "neural-network-architectures"),
        ("6.5", "exploration-strategies"),
        ("7", "learning-algorithms"),
        ("7.1", "loss-module-architecture"),
        ("7.2", "on-policy-algorithms"),
        ("7.3", "off-policy-algorithms"),
        ("7.4", "value-based-algorithms"),
        ("7.5", "value-estimators"),
        ("8", "training-infrastructure"),
        ("8.1", "trainer-system"),
        ("8.2", "helper-utilities"),
        ("9", "llm-integration"),
        ("9.1", "llm-wrapper-system"),
        ("9.2", "llm-data-structures"),
        ("9.3", "llm-training-objectives"),
        ("9.4", "llm-environments-and-tools"),
        ("10", "multi-agent-reinforcement-learning"),
        ("11", "examples-and-tutorials"),
        ("12", "development-and-deployment"),
        ("12.1", "build-system"),
        ("12.2", "documentation-system"),
    ],
    "cleanrl": [
        ("1", "overview"),
        ("2", "getting-started"),
        ("2.1", "installation"),
        ("2.2", "basic-usage"),
        ("2.3", "model-zoo-and-huggingface-integration"),
        ("3", "core-algorithms"),
        ("3.1", "ppo-(proximal-policy-optimization)"),
        ("3.2", "dqn-(deep-q-network)"),
        ("3.3", "sac-(soft-actor-critic)"),
        ("3.4", "ddpg-and-td3"),
        ("3.5", "advanced-algorithms"),
        ("4", "jax-implementations"),
        ("4.1", "jax-algorithm-implementations"),
        ("4.2", "envpool-xla-integration"),
        ("5", "environment-integrations"),
        ("5.1", "classic-control"),
        ("5.2", "atari-games"),
        ("5.3", "mujoco-and-continuous-control"),
        ("5.4", "procgen-and-generalization"),
        ("5.5", "multi-agent-environments"),
        ("5.6", "isaac-gym-integration"),
        ("6", "envpool-integration"),
        ("7", "benchmarking-and-evaluation"),
        ("7.1", "running-benchmarks"),
        ("7.2", "experiment-tracking"),
        ("7.3", "hyperparameter-tuning-with-optuna"),
        ("8", "cloud-deployment"),
        ("8.1", "aws-batch-setup"),
        ("8.2", "docker-containers"),
        ("9", "testing-and-cicd"),
        ("10", "development-guide"),
        ("11", "contributing"),
        ("12", "glossary"),
    ],
}
REPO_SLUG = {"torchrl": "pytorch/rl", "cleanrl": "vwxyzjn/cleanrl"}

SKIP_IDS = {"DeepWiki", "Menu", "Dismiss"}  # 页面固定噪音


def el_to_md(el, depth=0):
    """递归把 bs4 元素转 markdown-ish 文本。"""
    if isinstance(el, NavigableString):
        return str(el)
    if not isinstance(el, Tag):
        return ""
    name = el.name.lower()
    if name in ("script", "style", "nav", "button", "svg"):
        return ""
    if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
        lvl = int(name[1])
        return "\n\n" + "#" * min(lvl + 1, 6) + " " + el.get_text(" ", strip=True) + "\n"
    if name == "pre":
        code = el.get_text()
        return "\n\n```\n" + code.rstrip() + "\n```\n"
    if name == "code":
        return "`" + el.get_text() + "`"
    if name == "li":
        return "\n" + "  " * depth + "- " + el.get_text(" ", strip=True)
    if name == "table":
        rows = []
        for tr in el.find_all("tr"):
            cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
            rows.append("| " + " | ".join(cells) + " |")
        return "\n\n" + "\n".join(rows) + "\n"
    if name == "br":
        return "\n"
    if name == "img":
        return "\n[图片: " + el.get("alt", "") + "]\n"
    parts = [el_to_md(c, depth + (1 if name in ("ul", "ol") else 0)) for c in el.children]
    text = "".join(parts)
    if name in ("p", "div", "section", "ul", "ol"):
        return "\n" + text
    return text


def clean(md):
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"[ \t]+\n", "\n", md)
    # 去掉页面尾部固定噪音
    for noise in ["Dismiss", "Refresh this wiki", "Enter email to refresh", "Index your code with", "Loading..."]:
        md = md.replace(noise, "")
    return md.strip()


def fetch(session, url, tries=4):
    for i in range(tries):
        try:
            r = session.get(url, headers=UA, timeout=30)
            if r.status_code == 200 and len(r.text) > 3000:
                return r.text
            wait = 8 * (i + 1)
            print(f"    [{r.status_code}] 等{wait}s 重试 {i+1}/{tries}")
            time.sleep(wait)
        except Exception as e:
            print(f"    EXC {type(e).__name__} 等{8*(i+1)}s")
            time.sleep(8 * (i + 1))
    return None


def main(repo):
    slug = REPO_SLUG[repo]
    outdir = OUT / repo
    outdir.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    ok, fail = [], []
    for num, slugname in PAGES[repo]:
        fname = f"{num}-{slugname}.md".replace("(", "").replace(")", "")
        url = f"https://deepwiki.com/{slug}/{num}-{slugname}"
        dest = outdir / fname
        if dest.exists() and dest.stat().st_size > 1500:
            print(f"  [跳过已存在] {num}")
            ok.append((num, fname, dest.stat().st_size))
            continue
        html = fetch(s, url)
        if not html:
            fail.append((num, url))
            print(f"  [失败] {num} {url}")
            continue
        soup = BeautifulSoup(html, "html.parser")
        main_el = soup.find("main") or soup.find("article") or soup.body
        md = el_to_md(main_el) if main_el else soup.get_text()
        md = clean(md)
        # 抓不到正文保护：太小视为失败
        if len(md) < 800:
            fail.append((num, url))
            print(f"  [太短{len(md)}b] {num}")
            continue
        dest.write_text(f"# deepwiki {repo} §{num} {slugname}\n> 来源: {url}\n\n{md}\n", encoding="utf-8")
        ok.append((num, fname, dest.stat().st_size))
        print(f"  [OK] {num} -> {fname} ({dest.stat().st_size//1024}KB)")
        time.sleep(1.2)
    print(f"\n== {repo}: 成功 {len(ok)}/{len(PAGES[repo])}, 失败 {len(fail)} ==")
    for n, u in fail:
        print(f"  FAIL {n}: {u}")
    (outdir / "_manifest.json").write_text(json.dumps(
        {"expected": len(PAGES[repo]), "ok": [(n, f, sz) for n, f, sz in ok],
         "failed": [u for _, u in fail], "fetched_at": time.strftime("%Y-%m-%d %H:%M")}, ensure_ascii=False, indent=1))
    return len(fail)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

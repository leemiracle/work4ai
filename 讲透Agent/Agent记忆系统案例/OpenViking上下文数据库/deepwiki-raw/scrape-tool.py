#!/usr/bin/env python3
"""Final DeepWiki extractor: RSC payload of any page embeds many/all wiki pages as T-blocks.
Fetch a few seed pages, merge+dedupe all '# '-starting text blocks until TOC coverage complete."""
import re, json, subprocess, os, time, urllib.parse, sys

OUT = "/tmp/opencode/openviking-deepwiki"
os.makedirs(OUT, exist_ok=True)
BASE = "https://deepwiki.com/volcengine/OpenViking/"

EXPECTED = {  # slug -> H1 title in page content
"1-overview":"Overview","1.1-what-is-openviking":"What is OpenViking","1.2-key-concepts":"Key Concepts",
"1.3-architecture-at-a-glance":"Architecture at a Glance",
"2-getting-started":"Getting Started","2.1-installation":"Installation","2.2-configuration":"Configuration",
"2.3-quick-start-examples":"Quick Start Examples","2.4-deployment-modes":"Deployment Modes",
"3-core-architecture":"Core Architecture","3.1-system-overview":"System Overview","3.2-client-layer":"Client Layer",
"3.3-service-layer":"Service Layer","3.4-viking-filesystem-(vikingfs)":"Viking Filesystem (VikingFS)",
"3.5-vector-database-layer":"Vector Database Layer",
"3.6-three-level-context-model-(l0l1l2)":"Three-Level Context Model (L0/L1/L2)",
"3.7-data-flow-and-processing-pipeline":"Data Flow and Processing Pipeline",
"4-subsystems":"Subsystems","4.1-resource-ingestion-and-parsing":"Resource Ingestion and Parsing",
"4.2-semantic-search-and-retrieval":"Semantic Search and Retrieval",
"4.3-session-and-memory-management":"Session and Memory Management",
"4.4-queue-and-async-processing":"Queue and Async Processing",
"4.5-vlm-and-embedding-integration":"VLM and Embedding Integration",
"4.6-storage-backend-configuration":"Storage Backend Configuration",
"4.7-transaction-and-locking":"Transaction and Locking",
"4.8-snapshots-and-multi-version-management":"Snapshots and Multi-Version Management",
"4.9-privacy-configs-and-encryption":"Privacy Configs and Encryption",
"4.10-observability-and-metrics":"Observability and Metrics",
"5-multi-language-build-system":"Multi-Language Build System","5.1-python-core-and-sdk":"Python Core and SDK",
"5.2-c++-vector-extensions":"C++ Vector Extensions","5.3-go-agfs-server":"Go AGFS Server",
"5.4-rust-cli-tool":"Rust CLI Tool","5.5-build-orchestration":"Build Orchestration",
"6-agent-integration-plugins":"Agent Integration Plugins",
"6.1-openclaw-plugin-installation-and-setup":"OpenClaw Plugin — Installation and Setup",
"6.2-openclaw-plugin-configuration-and-modes":"OpenClaw Plugin — Configuration and Modes",
"6.3-openclaw-plugin-memory-operations":"OpenClaw Plugin — Memory Operations",
"6.4-claude-code-memory-plugin":"Claude Code Memory Plugin",
"6.5-opencode-codex-and-other-integrations":"OpenCode, Codex, and Other Integrations",
"6.6-langchain-and-langgraph-integration":"LangChain and LangGraph Integration",
"7-vikingbot-agent-framework":"VikingBot Agent Framework","7.1-vikingbot-architecture":"VikingBot Architecture",
"7.2-vikingbot-channels-and-providers":"VikingBot Channels and Providers",
"8-web-studio":"Web Studio","8.1-web-studio-overview-and-features":"Web Studio Overview and Features",
"8.2-web-studio-api-client-and-authentication":"Web Studio API Client and Authentication",
"9-development-guide":"Development Guide","9.1-development-environment-setup":"Development Environment Setup",
"9.2-building-from-source":"Building from Source","9.3-testing-strategy":"Testing Strategy",
"9.4-code-quality-standards":"Code Quality Standards",
"10-cicd-pipeline":"CI/CD Pipeline","10.1-pull-request-workflow":"Pull Request Workflow",
"10.2-build-system":"Build System","10.3-testing-workflows":"Testing Workflows",
"10.4-dependency-management":"Dependency Management","10.5-release-process":"Release Process",
"10.6-docker-build-and-deployment":"Docker Build and Deployment",
"11-benchmarks-and-evaluation":"Benchmarks and Evaluation",
"11.1-locomo-long-term-memory-benchmark":"LoCoMo Long-Term Memory Benchmark",
"11.2-tau2-rag-and-other-benchmarks":"TAU2, RAG, and Other Benchmarks",
"12-api-reference":"API Reference","12.1-python-sdk-api":"Python SDK API","12.2-go-sdk-api":"Go SDK API",
"12.3-cli-commands-reference":"CLI Commands Reference","12.4-http-api-endpoints":"HTTP API Endpoints",
"12.5-authentication-oauth-and-multi-tenancy":"Authentication, OAuth, and Multi-Tenancy",
"12.6-mcp-integration":"MCP Integration",
"13-community-and-support":"Community and Support","13.1-getting-help":"Getting Help",
"13.2-reporting-issues":"Reporting Issues","13.3-contributing-guidelines":"Contributing Guidelines",
"14-glossary":"Glossary",
}
TITLE2SLUG = {v:k for k,v in EXPECTED.items()}

def fetch_blocks(url, tries=4):
    for t in range(tries):
        r = subprocess.run(["curl","-sL","--max-time","90","-A","Mozilla/5.0",url],
                           capture_output=True, text=True)
        if r.returncode==0 and len(r.stdout)>100000:
            chunks = re.findall(r'self\.__next_f\.push\(\[1,\s*("(?:[^"\\]|\\.)*")\]\)', r.stdout)
            payload = "".join(json.loads(c) for c in chunks)
            blocks = []
            for m in re.finditer(r'\d+:T([0-9a-f]+),', payload):
                n = int(m.group(1), 16)
                txt = payload[m.end():m.end()+n]
                if txt.startswith("# ") and len(txt) > 3000 and "<details>" in txt:
                    blocks.append(txt)
            return blocks
        time.sleep(5+5*t)
    return []

pages = {}  # title -> content
seeds = ["1-overview","4-subsystems","6-agent-integration-plugins","9-development-guide",
         "12-api-reference","14-glossary","2.4-deployment-modes","10.6-docker-build-and-deployment",
         "11.2-tau2-rag-and-other-benchmarks","13.3-contributing-guidelines","8.2-web-studio-api-client-and-authentication",
         "3.7-data-flow-and-processing-pipeline","7.2-vikingbot-channels-and-providers","12.6-mcp-integration"]
for s in seeds:
    if len(pages) == len(EXPECTED): break
    blocks = fetch_blocks(BASE + urllib.parse.quote(s, safe=".-+()"))
    new = 0
    for b in blocks:
        title = b[2:].split("\n",1)[0].strip()
        if title in TITLE2SLUG and title not in pages:
            pages[title] = b; new += 1
    print(f"seed {s}: +{new} new, total {len(pages)}/{len(EXPECTED)}", flush=True)
    time.sleep(2)

missing = [v for k,v in EXPECTED.items() if v not in pages]
print("MISSING:", missing)

# archive in TOC order
with open(f"{OUT}/full.md","w",encoding="utf-8") as f:
    f.write("# DeepWiki Archive: volcengine/OpenViking\n")
    f.write(f"# 抓取: {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}\n")
    f.write(f"# 页数: {len(pages)}/{len(EXPECTED)} | 来源: deepwiki.com RSC prefetch blocks\n")
    for slug, title in EXPECTED.items():
        if title in pages:
            f.write(f"\n\n<!-- ===== PAGE: {slug} ===== -->\n\n")
            f.write(pages[title].rstrip() + "\n")
print("full.md size:", os.path.getsize(f"{OUT}/full.md"))

# ClaudeClaw — Communication Plan

## Key Messages

**One-liner:** ClaudeClaw is a Claude Code plugin that turns Claude into a persistent, always-on agent for your Slack/WhatsApp/Telegram — with OS-level sandbox isolation and a composable extension system.

**Problem it solves:** You want Claude to be your team's support agent in Slack, answering questions, triaging issues, filing GitHub tickets — running 24/7, not just when you have a terminal open.

**Differentiators:**
- Plugin for Claude Code (not a standalone framework)
- OS-level sandbox isolation (not Docker, not app-level permissions)
- Composable extensions (install only what you use, no merge conflicts)
- Codebase small enough for Claude to self-improve (~8K lines)
- Directory-as-instance (no config files, no hidden state)

**Origin story:** Fork of NanoClaw (qwibitai), rebuilt as a Claude Code plugin with sandbox runtime, structured memory, webhook triggers, extension system. Two days, 40+ commits.

---

## Platform Content

### 1. X/Twitter — Thread (6 tweets)

**Tweet 1 (hook):**
I built a Claude Code plugin that turns Claude into a 24/7 agent on Slack.

It reads messages, triages issues, files GitHub tickets, and answers questions — all running in OS-level sandboxes with <10ms cold starts.

Open source: github.com/sbusso/claudeclaw

🧵

**Tweet 2 (problem):**
The problem: Claude Code is powerful but session-based. Close the terminal, Claude stops.

I needed Claude always listening on Slack — answering user questions, investigating bugs, creating GitHub issues with technical details while keeping the conversation clean.

**Tweet 3 (architecture):**
Architecture: Single Node.js process. Channels self-register at startup. Messages land in SQLite, a polling loop picks them up, and each agent spawns in an OS-level sandbox.

No Docker. No VMs. Sub-10ms cold starts. Kernel-enforced isolation.

**Tweet 4 (extensions):**
The extension system is the real win.

Slack, triage, SWE agents — all installable plugins. `/install-extension slack` clones from GitHub, compiles, copies skills, restarts.

No merge conflicts. Core updates are `git pull`. Extension updates are independent.

**Tweet 5 (self-improvement):**
The whole codebase (~8K lines) fits in Claude's context window.

Want to change behavior? Tell Claude. It reads the code, modifies it, commits. The codebase IS the configuration.

No config files. No YAML. Code changes committed to your fork.

**Tweet 6 (CTA):**
Try it:
```
git clone https://github.com/sbusso/claudeclaw
cd claudeclaw && claude
# /setup
```

Roadmap: multi-model routing (GPT-4, Gemini, Ollama), QMD semantic memory, Obsidian sync.

Star if useful ⭐

---

### 2. Reddit

**r/ClaudeAI** (title: "ClaudeClaw — Claude Code plugin that runs agents on Slack/WhatsApp/Telegram")

I built a Claude Code plugin that lets Claude run as a persistent agent on messaging channels. You bring your own API key, it runs locally on your machine.

**Quick start:**
```bash
git clone https://github.com/sbusso/claudeclaw
cd claudeclaw && claude
# type: /setup
```

**The problem it solves:** I wanted Claude answering support questions in our team Slack around the clock — not just when I have a terminal open. Existing solutions like OpenClaw are 500K+ lines with application-level security. I wanted something I could actually read and audit.

**How it works:** Channels (Slack, Telegram, WhatsApp) self-register at startup. Messages land in SQLite, a polling loop dispatches them to sandboxed Claude agents per group. Each agent gets its own isolated filesystem and memory. Responses route back through the originating channel.

**Architecture choices:**
- Runs as a Claude Code plugin (`--plugin-dir`), not a standalone app
- OS-level sandbox via Anthropic's `sandbox-runtime` — kernel-enforced, <10ms cold starts, no Docker needed
- Composable extensions — add channels with `/install-extension slack`
- Structured memory per group (daily logs, topic files, searchable)
- Per-group agent config: model, effort, allowed tools, cost limits
- ~8K lines of TypeScript, 386 tests

**What it's NOT:** A hosted service, a SaaS, or a wrapper API. It's a codebase you clone, own, and modify. The whole thing fits in Claude's context window.

Requirements: macOS/Linux, Node.js 20+, Claude Code, Anthropic API key.

Repo: https://github.com/sbusso/claudeclaw

Happy to discuss the sandbox isolation model, extension architecture, or anything else.

---

**r/SideProject** (title: "[Open Source] ClaudeClaw — Turn Claude into a 24/7 Slack agent with OS-level isolation")

Built this over a weekend: a Claude Code plugin that makes Claude a persistent agent on your messaging channels.

The use case: our team needed an AI assistant in Slack that could answer questions, triage issues, and file GitHub tickets — running continuously, not just during a terminal session.

Instead of building another AI framework, I made it a Claude Code plugin. You run `claude --plugin-dir claudeclaw`, set up your channels, and Claude is always on.

The security model uses kernel-level sandboxing (not Docker) — each agent spawns in <10ms with restricted network and filesystem access. The codebase is small enough (~8K lines) that Claude can read and modify itself.

Channels and agents are installable extensions — no monolith, install only what you need.

https://github.com/sbusso/claudeclaw

---

**r/programming** — Post a TECHNICAL ARTICLE, not the repo. Link to the published article on Dev.to or htdoc.dev.

r/programming rules: no project showcases, no feature lists, no repo links as posts. They want technical write-ups about HOW you built it, not WHAT you built.

**Option A — Use the sandbox deep dive article:**
Title: "OS-Level Sandboxing for AI Agents: Kernel-Enforced Isolation Without Docker"
Link: [published URL of article/nanoclaw-sandbox-deep-dive.md on htdoc.dev or Dev.to]

**Option B — Write a new focused technical article on one of:**
- "Building a manifest-based extension loader for a plugin system" (extension architecture)
- "Why I replaced Docker with Seatbelt/bubblewrap for AI agent isolation" (sandbox deep dive)
- "Inverting the credential model: trust secrets, restrict network" (security architecture)
- "Directory-as-instance: eliminating config files from an agent orchestrator" (philosophy)

Post the article to Dev.to/htdoc.dev first, then submit the link to r/programming. The article should focus on the engineering challenge and decisions, with ClaudeClaw as context — not the other way around.

---

**r/LocalLLaMA** (title: "[Open Source] ClaudeClaw: persistent agent orchestrator with multi-model routing on the roadmap (Ollama support planned)")

Built an agent orchestrator (Claude Code plugin) that currently runs Claude agents in OS-level sandboxes for Slack/WhatsApp/Telegram.

Sharing here because **multi-model routing is on the roadmap** — the architecture already has per-group model selection. The next step is provider-prefixed model strings (`ollama/llama3`, `openai/gpt-4o`) so you can:
- Run triage on a cheap local model
- Route complex tasks to Claude Opus or GPT-4
- Use Ollama for privacy-sensitive groups

The extension system means this would be a `claudeclaw-router` extension — plug it in when ready, don't touch core.

Current state: https://github.com/sbusso/claudeclaw
Roadmap: multi-model routing, QMD semantic memory, Obsidian integration

---

### 3. Hacker News (Show HN)

**Title:** Show HN: ClaudeClaw – Persistent Claude agents on Slack with OS-level sandboxing

**Text:**
ClaudeClaw is a Claude Code plugin that runs Claude as a persistent agent on messaging channels (Slack, WhatsApp, Telegram). Each agent spawns in an OS-level sandbox (Seatbelt/bubblewrap) with kernel-enforced filesystem and network restrictions. Sub-10ms cold starts, no Docker required.

I built it because I wanted Claude answering questions in our team's Slack 24/7. Existing frameworks were too large to audit (~500K lines) and used application-level security checks.

Architecture: Single Node.js process, SQLite polling loop, channels self-register at startup. The codebase is ~8K lines — small enough for Claude to hold in context and self-modify.

Key technical decisions:
- Sandbox security model: trust credentials, restrict network (vs Docker's protect credentials, allow network)
- Composable extensions: channels/agents are installable plugins with manifests, not merged branches
- Directory = instance: no config files, cwd is the state root

https://github.com/sbusso/claudeclaw

---

### 4. LinkedIn

**Post:**

I built ClaudeClaw — a Claude Code plugin that turns Claude into a persistent, always-on agent for team messaging channels.

**The problem:** Our team needed an AI assistant in Slack that could answer support questions, triage issues, and file GitHub tickets — running 24/7, not just when someone has a terminal open.

**The approach:** Instead of building another AI framework, I made it a Claude Code plugin. It runs as a background service, listening to Slack/WhatsApp/Telegram, routing messages to Claude agents that run in OS-level sandboxes with kernel-enforced isolation.

**What makes it different:**
→ OS-level sandboxing (not Docker) — <10ms cold starts, no VMs
→ Composable extensions — install only what you use
→ Small enough to understand (~8K lines) — Claude can read and modify its own code
→ Per-group agent config — model, tools, cost limits per channel
→ Structured memory — daily logs, topic files, searchable archive

**Open source:** https://github.com/sbusso/claudeclaw

Built on NanoClaw, rebuilt as a plugin in two days. 355 tests, composable extension system, multi-model routing on the roadmap.

If your team is looking at AI agents for internal support, this might be a good starting point. The whole point is that you own the code.

#AI #Agents #Claude #OpenSource #DevTools

---

### 5. Dev.to / Hashnode — Article

Use the release article at `article/claudeclaw-release.md` as the base. Add a "Getting Started" section at the top for dev audiences. Cross-post to both platforms.

**Title:** "ClaudeClaw: Building a Composable Agent Orchestrator as a Claude Code Plugin"

**Tags:** ai, agents, typescript, opensource, claude

---

### 6. Product Hunt

**Tagline:** Turn Claude into a 24/7 agent on your Slack, WhatsApp, or Telegram

**Description:**
ClaudeClaw is a Claude Code plugin that makes Claude a persistent, always-on agent for your messaging channels. It listens to Slack/WhatsApp/Telegram, routes messages to isolated Claude agents, manages memory, handles scheduled tasks and webhooks.

Key features:
🔒 OS-level sandbox isolation (<10ms cold starts)
🧩 Composable extension system (install only what you need)
🧠 Structured memory (daily logs, topics, searchable archive)
💰 Cost tracking per agent run
🔧 Self-improving — codebase fits in Claude's context window

**Maker comment:**
I built this because I needed Claude answering support questions in Slack 24/7. Existing frameworks were too large to audit. ClaudeClaw is ~8K lines — small enough to read end-to-end, and small enough for Claude to modify itself.

---

### 7. Discord Communities

**Anthropic Discord / Claude Code channels:**

Hey — built a Claude Code plugin called ClaudeClaw that runs Claude as a persistent agent on Slack/WhatsApp/Telegram.

It uses the Claude Agent SDK inside OS-level sandboxes (Anthropic's sandbox-runtime). Each agent spawns in <10ms, kernel-enforced network + filesystem isolation.

The extension system lets you install channels and agents as plugins — `/install-extension slack` clones, compiles, copies skills, restarts. No merge conflicts.

Repo: https://github.com/sbusso/claudeclaw

Would love feedback on the sandbox integration approach — especially the credential handling inversion (trust creds + restrict network vs Docker's protect creds + allow network).

---

### 8. GitHub Discussions / Issues

Create a "Welcome" discussion on the repo explaining the project, linking to the release article, and inviting feedback.

---

## Platform Priority

| Priority | Platform | Audience | Format | Timing |
|----------|----------|----------|--------|--------|
| 🔴 High | Hacker News | Technical builders | Show HN | Day 1 |
| 🔴 High | r/ClaudeAI | Claude users | Detailed post | Day 1 |
| 🔴 High | X/Twitter | Dev community | Thread | Day 1 |
| 🟡 Medium | LinkedIn | Professional network | Post | Day 1-2 |
| 🟡 Medium | r/programming | Engineers | Technical post | Day 1-2 |
| 🟡 Medium | r/SideProject | Builders | Project showcase | Day 2 |
| 🟡 Medium | Dev.to | Developer writers | Article (from release) | Day 2-3 |
| 🟡 Medium | r/LocalLLaMA | Local AI enthusiasts | Multi-model angle | Day 3 |
| 🟢 Low | Product Hunt | Product enthusiasts | Launch | Day 3-5 |
| 🟢 Low | Discord (Anthropic) | Claude community | Casual post | Day 1 |
| 🟢 Low | Hashnode | Developer writers | Cross-post from Dev.to | Day 3 |

## Hashtags / Keywords

X: #ClaudeCode #AIAgents #OpenSource #Sandbox #TypeScript #SlackBot
LinkedIn: #AI #Agents #Claude #OpenSource #DevTools #Automation
Reddit: claude, agents, sandbox, orchestrator, slack, open-source
Dev.to: ai, agents, typescript, opensource, claude

### 9. Awesome Agent Substack — Special Project Feature

**Title:** ClaudeClaw: Composable Agent Orchestrator as a Claude Code Plugin

**Body:**

This week's special feature: **ClaudeClaw** — an open-source (MIT) agent orchestrator that runs as a Claude Code plugin, turning Claude into a persistent, always-on agent across Slack, WhatsApp, Telegram, Discord, and Gmail.

**The pitch:** You want Claude running 24/7 in your team's Slack — triaging support questions, investigating bugs, filing GitHub issues — not just when someone has a terminal open. ClaudeClaw makes that a `git clone` + `/setup` away.

**What makes it interesting:**

🔒 **OS-level sandboxing, not Docker.** Each agent spawns in <10ms using Anthropic's `sandbox-runtime` (Seatbelt on macOS, bubblewrap on Linux). Kernel-enforced filesystem and network restrictions. The security model inverts Docker's: credentials are passed directly, but the agent can only connect to Anthropic's API — nowhere to exfiltrate.

🧩 **Composable extension system.** Channels and agents aren't bundled — they're installable extensions with their own repos. `/install-extension slack` clones from GitHub, compiles, copies skills, restarts. No merge conflicts, no monolith. Core stays lean (~8K lines).

🧠 **Structured memory.** Daily logs, topic files, long-term CLAUDE.md, searchable archive. PreCompact hooks auto-save conversations before context compaction. QMD semantic search (hybrid BM25 + vector + LLM re-ranking) on the roadmap.

📡 **Three trigger modes.** Channel messages (@mention), scheduled tasks (cron), and webhook triggers (HTTP POST with HMAC-SHA256). CI failures, GitHub events, and monitoring alerts can all invoke agents.

🔧 **Self-improving.** The entire codebase fits in Claude's context window. Want to change behavior? Tell Claude. It reads, modifies, and commits code changes. No config files — code is the configuration.

**Architecture at a glance:**
```
Channels → SQLite → Polling loop → Sandbox (Claude Agent SDK) → Response
Webhooks → HTTP → HMAC verify → Queue
```

Single Node.js process. Channels self-register at startup. Per-group isolation: each group gets its own sandbox, memory, filesystem, and agent config (model, tools, cost limits).

**Origin:** Fork of [NanoClaw](https://github.com/qwibitai/nanoclaw), rebuilt as a Claude Code plugin in two days. Added sandbox runtime, extension system, message router with hook pipeline, structured memory, webhook triggers, cost tracking, and per-group agent configuration.

**Roadmap:**
- Multi-model routing (OpenAI, Google, Ollama — provider-prefixed model strings)
- QMD semantic memory (fully local, no API calls for search)
- Obsidian vault integration
- TUI for instance management

**Links:**
- 🔗 Repo: [github.com/sbusso/claudeclaw](https://github.com/sbusso/claudeclaw)
- 🔗 Slack extension: [github.com/sbusso/claudeclaw-slack](https://github.com/sbusso/claudeclaw-slack)
- 🔗 Triage extension: [github.com/sbusso/claudeclaw-triage](https://github.com/sbusso/claudeclaw-triage)
- 📄 License: MIT
- 📋 Requirements: macOS/Linux, Node.js 20+, Claude Code, your own API key

---

## Follow-up Content (Week 2+)

1. **"How I sandbox AI agents without Docker"** — technical deep dive on sandbox-runtime
2. **"Building a composable extension system for AI agents"** — extension loader architecture
3. **"Directory-as-instance: why I stopped using config files"** — philosophy post
4. **Video demo** — 3-min screencast: setup → Slack message → agent response → memory
5. **"Multi-model routing for AI agents"** — when multi-model lands, announce with examples

# ClaudeClaw Landing Page — Design Spec

## Overview

A single-page GitHub Pages site for ClaudeClaw that positions it as a lightweight, auditable alternative to OpenClaw. Dark gradient design with isometric technical illustrations generated via Gemini API. Ships as `docs/index.html` (or a `site/` directory) deployed to GitHub Pages.

## Goals

1. **Capture OpenClaw search traffic** with a direct (but respectful) comparison
2. **Establish technical authority** through architecture illustrations and security details
3. **Convert developers** with a 30-second quick start

## Audience

Independent developers and small teams who find OpenClaw too large to audit or run. People searching "OpenClaw alternative", "lightweight agent orchestrator", "Claude agent framework".

## Visual Direction

**Dark Gradient Sections** — dark base (#0D1117 family) with subtle gradient shifts between sections. No cards. Full-width sections flowing into each other with natural color transitions.

- **Accent color**: Amber/gold (#D4870E → #E8A020) from the logo
- **Typography**: System font stack (Inter if loaded, else system sans). Monospace for code (JetBrains Mono or system mono)
- **Illustrations**: Isometric technical diagrams generated with Gemini API (Nano Banana Pro). Clean vector-style showing sandbox boundaries, message flow, channel connections
- **Effects**: Subtle parallax on illustrations, smooth scroll anchors, no heavy animations. Gradient section transitions create visual rhythm

## Color System

```
--bg-darkest:    #0A0A0B
--bg-dark:       #0D1117
--bg-mid:        #0F0F14
--bg-section:    #111318
--border:        #1a1a2e
--text-primary:  #f0f0f0
--text-secondary:#888888
--text-muted:    #555555
--accent:        #E8A020
--accent-dark:   #D4870E
--accent-glow:   rgba(212, 135, 14, 0.08)
--accent-border: rgba(212, 135, 14, 0.25)
```

## Page Sections

### 1. Hero

- Logo (64px, rounded square with amber gradient)
- Title: "ClaudeClaw"
- Subtitle: "Persistent agent orchestrator for Claude Code. Multi-channel. Sandboxed. 8K lines you can actually read."
- Stat pills: `<10ms cold start` · `~8K lines` · `No Docker`
- Terminal quick start block (3 lines: clone, cd, /setup)
- **Illustration**: Isometric overview — sandbox boundaries, channels flowing into message loop, agents in isolation boxes
- Background: linear-gradient #0D1117 → #0A0E14

### 2. Why Not OpenClaw?

- Heading: "Why not OpenClaw?"
- Subheading: "OpenClaw is a platform. ClaudeClaw is a tool. Same problem, different philosophy."
- Comparison table (not a diff, not aggressive — clean data):
  - Codebase: ~8K vs 500K+
  - Security: Kernel-enforced sandbox vs application-level
  - Cold start: <10ms vs seconds
  - Docker required: No vs Yes
  - Auditability: Fits in context window vs requires team
  - Configuration: Code changes (git revert) vs config sprawl
- Background: gradient shift to #0A0E14 → #0F0F14

### 3. How It Works

- Heading: "How it works"
- Subheading: "Single process. Channels in, sandboxed agents out."
- **Illustration**: Isometric flow diagram — Channels (Slack/WhatsApp/Telegram icons) → SQLite store → Message loop (highlighted as the heart) → Sandboxed agent with glowing isolation boundary → Response back to channel
- Also show: Webhooks as a second entry path into the queue
- Background: gradient shift to #0F0F14 → #0B0D12

### 4. Sandbox & Security

- Heading: "Sandbox-first security"
- Subheading: "The kernel enforces isolation, not your application code."
- Four pillars displayed as full-width stacked rows (NOT a 2x2 grid, NOT cards) with amber left-border accent:
  1. **Kernel isolation** — Seatbelt (macOS) / bubblewrap (Linux). OS-level enforcement.
  2. **Network restriction** — Agents can only reach api.anthropic.com. Nowhere to exfiltrate.
  3. **Zero overhead** — <10ms cold starts. No VMs, no containers, no daemon.
  4. **Per-group boundaries** — Each group sees only its own files. Kernel-enforced.
- **Illustration**: Isometric sandbox container showing visible walls, allowed/denied network paths, filesystem boundaries
- Background: gradient shift to #0B0D12 → #0D1018

### 5. Philosophy

- Heading: "A tool, not a platform"
- Three principles in a horizontal row (responsive → stacks on mobile):
  1. **Small enough to understand** — ~8K lines. One process. Fits in Claude's context window.
  2. **Built for one person** — Not a framework. Fork it, modify it, own it.
  3. **Code is configuration** — No YAML. Tell Claude to change the code. Every change is a revertible commit.
- Background: gradient shift to #0D1018 → #0A0C10

### 6. Features

- Heading: "Features"
- Alternating left/right layout (text on one side, illustration on the other):
  1. **Multi-channel routing** — Slack, WhatsApp, Telegram, Discord, Gmail. Channels self-register. [illustration: channel icons flowing into a funnel]
  2. **Structured memory** — Daily logs, topic files, searchable archive. QMD semantic search upgrade path. [illustration: layered memory files]
  3. **Three trigger modes** — @mention, cron schedules, webhook (HMAC-SHA256). [illustration: three input arrows]
  4. **Cost tracking & limits** — Per-run logging, per-group budgets, model selection. [illustration: dashboard-style meters]
- Background: gradient shift to #0A0C10 → #0D1117

### 7. Extensions

- Heading: "Composable extensions"
- Subheading: "Install only what you use. No merge conflicts."
- Terminal-style install demo showing `/install-extension slack` and `/install-extension triage`
- Grid of extensions: available (slack, triage) and planned (discord, gmail, memory, obsidian, tui) with dashed borders
- Background: gradient shift to #0D1117 → #0A0E14

### 8. Quick Start / CTA

- Heading: "Get started in 30 seconds"
- Requirements: macOS or Linux, Node.js 20+, Claude Code
- Terminal block with clone/cd/claude//setup commands
- Primary CTA button: "View on GitHub →" (amber gradient background)
- Background: gradient shift to #0A0E14 → #0D1117

### 9. Footer

- Left: MIT License · Built on NanoClaw
- Right: GitHub · Discussions · Claude Agent SDK links
- Minimal, single row

## Illustrations (Gemini Generation)

Generate 4-5 isometric illustrations using Nano Banana Pro (Gemini):

1. **Hero illustration**: Overview of the full system — channels on the left, message loop in the center, sandboxed agents on the right with glowing amber boundaries. Dark background, clean isometric style.
2. **Architecture flow**: Detailed message flow — channel icons → SQLite cylinder → polling loop gear → sandbox box with agent inside. Webhook arrow entering from below.
3. **Sandbox detail**: Cutaway view of a sandbox showing filesystem boundaries (green allowed, red denied), network restriction (only one outgoing arrow to api.anthropic.com), agent process inside.
4. **Channel routing**: Isometric view of multiple channel icons (Slack, WhatsApp, Telegram) converging into a single orchestrator node.
5. **Memory system** (optional): Layered file structure showing daily logs stacking, topic files branching, CLAUDE.md as the persistent base.

**Style prompt guidelines**: "Isometric technical diagram, dark background (#0D1117), amber/gold accent (#E8A020), clean vector style, minimal, no text, developer tool aesthetic, glowing boundaries"

## Technical Implementation

### Structure

```
docs/
  index.html          # Single-page landing (self-contained)
  assets/
    logo.webp         # Copy from repo assets/
    hero.webp         # Generated illustration
    architecture.webp # Generated illustration
    sandbox.webp      # Generated illustration
    channels.webp     # Generated illustration
```

GitHub Pages serves from `docs/` on main branch.

### Stack

- **Zero build step** — plain HTML + CSS + minimal vanilla JS
- **No framework** — single HTML file, inline or `<style>` block CSS
- **Responsive** — mobile-first, breakpoints at 768px and 1024px
- **Performance** — no JS frameworks, lazy-load illustrations, system fonts with optional Inter/JetBrains Mono from CDN
- **GitHub Pages** — deploy from `docs/` folder on main branch, or a `gh-pages` branch

### CSS Approach

- CSS custom properties for the color system
- Section backgrounds via linear-gradient
- Smooth scroll behavior (`scroll-behavior: smooth`)
- Minimal animations: fade-in on scroll (IntersectionObserver, ~15 lines of JS)
- Responsive grid with CSS Grid/Flexbox, no media query overload

### SEO / Meta

- Title: "ClaudeClaw — Lightweight Agent Orchestrator for Claude Code"
- Description: "Persistent agent orchestrator plugin for Claude Code. Multi-channel routing, OS-level sandbox isolation, structured memory. 8K lines. Open source."
- Open Graph + Twitter Card meta tags
- Canonical URL pointing to GitHub Pages domain
- Keywords targeting: claudeclaw, openclaw alternative, claude agent framework, agent orchestrator

## Deployment

1. Build the page in `docs/` directory
2. Generate illustrations with Gemini API
3. Enable GitHub Pages in repo settings (source: `docs/` on main branch)
4. Add `.superpowers/` to `.gitignore` if not already there

## Out of Scope

- Blog / changelog pages (README serves this)
- JavaScript SPA routing
- CMS or dynamic content
- Analytics (can add later)
- Custom domain (GitHub Pages default is fine for now)

# ClaudeClaw Landing Page — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-page dark-themed landing page for ClaudeClaw, deployed via GitHub Pages from the `docs/` directory, with AI-generated isometric illustrations.

**Architecture:** Single `docs/index.html` file with inline `<style>` CSS and ~15 lines of vanilla JS (scroll fade-in). Illustrations generated via Gemini Nano Banana Pro API and saved as static assets in `docs/assets/`. GitHub Pages serves from `docs/` on main. The existing `docs/*.md` files (SPEC, SECURITY, REQUIREMENTS) and `docs/superpowers/` coexist — GitHub Pages will serve `index.html` as the root and the markdown files remain accessible but won't be served as HTML.

**Tech Stack:** HTML5, CSS custom properties, vanilla JS (IntersectionObserver), Gemini API for illustration generation

**Spec:** `docs/superpowers/specs/2026-03-27-landing-page-design.md`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `docs/index.html` | Full landing page (HTML + inline CSS + inline JS) |
| Create | `docs/assets/logo.webp` | Copy of `assets/logo.webp` |
| Create | `docs/assets/hero.png` | Generated: system overview illustration |
| Create | `docs/assets/architecture.png` | Generated: message flow illustration |
| Create | `docs/assets/sandbox.png` | Generated: sandbox cutaway illustration |
| Create | `docs/assets/channels.png` | Generated: channel routing illustration |
| Modify | `.gitignore` | Add `.superpowers/` |

---

### Task 1: Scaffold and Gitignore

**Files:**
- Create: `docs/assets/` directory
- Copy: `assets/logo.webp` → `docs/assets/logo.webp`
- Modify: `.gitignore`

- [ ] **Step 1: Add `.superpowers/` to `.gitignore`**

Append to `.gitignore`:
```
# Brainstorm sessions
.superpowers/
```

- [ ] **Step 2: Create docs/assets and copy logo**

```bash
mkdir -p /Users/sbusso/Code/dev/claudeclaw/docs/assets
cp /Users/sbusso/Code/dev/claudeclaw/assets/logo.webp /Users/sbusso/Code/dev/claudeclaw/docs/assets/logo.webp
```

- [ ] **Step 3: Verify**

```bash
ls -la /Users/sbusso/Code/dev/claudeclaw/docs/assets/
```
Expected: `logo.webp` exists

- [ ] **Step 4: Commit**

```bash
git add .gitignore docs/assets/logo.webp
git commit -m "chore: scaffold landing page assets dir, add .superpowers to gitignore"
```

---

### Task 2: Generate Illustrations with Gemini

**Files:**
- Create: `docs/assets/hero.png`
- Create: `docs/assets/architecture.png`
- Create: `docs/assets/sandbox.png`
- Create: `docs/assets/channels.png`

Use the `nano-banana-pro` skill (Gemini image generation) for each illustration. The skill takes a text prompt and outputs an image file.

**Fallback:** If the `nano-banana-pro` skill is unavailable or the Gemini API fails, create simple SVG placeholder images with the same dark background and amber accent. Each SVG should contain basic geometric shapes (rectangles, arrows, circles) that convey the same concept. These can be replaced with generated illustrations later.

**Style base prompt:** "Isometric technical diagram on a dark background color #0D1117, amber gold accent color #E8A020, clean vector style, minimal, no text labels, developer tool aesthetic, glowing amber boundaries, subtle shadows"

- [ ] **Step 1: Generate hero illustration**

Use `/nano-banana-pro` skill with prompt:
```
Isometric technical diagram on dark background #0D1117 showing an agent orchestration system overview. On the left side, three messaging platform icons (chat bubbles) in muted colors flow rightward into a central hexagonal hub glowing amber #E8A020. From the hub, arrows flow right to three isolated sandbox boxes with glowing amber boundaries, each containing a small robot/agent icon. Clean vector style, minimal, no text, developer tool aesthetic, subtle depth shadows. The sandbox boxes should have visible walls suggesting isolation and security.
```
Output: `docs/assets/hero.png` at 2K resolution

- [ ] **Step 2: Generate architecture flow illustration**

Use `/nano-banana-pro` skill with prompt:
```
Isometric technical diagram on dark background #0D1117 showing a data flow pipeline. Left: three chat bubble icons in muted blue-grey. Arrow flows right to a cylindrical database (SQLite) in dark grey with amber #E8A020 rim glow. Arrow flows right to a gear/cog mechanism glowing amber representing a polling loop. Arrow flows right to a glowing amber-bordered box containing a small process icon representing a sandboxed agent. A second arrow enters the database from below, coming from a webhook icon (a small hook shape). Clean vector style, minimal, no text, developer tool aesthetic.
```
Output: `docs/assets/architecture.png` at 2K resolution

- [ ] **Step 3: Generate sandbox illustration**

Use `/nano-banana-pro` skill with prompt:
```
Isometric technical diagram on dark background #0D1117 showing a security sandbox cutaway view. A large transparent box with glowing amber #E8A020 edges contains a small process/agent icon in the center. Around the box walls: on one side, a green checkmark arrow pointing to a single server icon labeled-style (representing allowed API connection). On other sides, red X marks on multiple blocked arrows showing denied connections. Below the box, a filesystem layer showing green-highlighted allowed folder and red-highlighted denied folders. Clean vector style, minimal, no text, developer tool aesthetic, emphasis on boundaries and isolation.
```
Output: `docs/assets/sandbox.png` at 2K resolution

- [ ] **Step 4: Generate channels illustration**

Use `/nano-banana-pro` skill with prompt:
```
Isometric technical diagram on dark background #0D1117 showing multi-channel message routing. Five distinct messaging platform icons (chat bubbles of different shapes and muted colors: blue, green, purple, teal, red) arranged in a fan/arc pattern, each with a glowing connection line converging into a single central node glowing amber #E8A020. The central node is a rounded hexagon representing the orchestrator. Clean vector style, minimal, no text, developer tool aesthetic, the amber glow should create a warm focal point.
```
Output: `docs/assets/channels.png` at 2K resolution

- [ ] **Step 5: Verify all illustrations exist**

```bash
ls -la /Users/sbusso/Code/dev/claudeclaw/docs/assets/
```
Expected: `hero.png`, `architecture.png`, `sandbox.png`, `channels.png`, `logo.webp`

- [ ] **Step 6: Commit**

```bash
git add docs/assets/
git commit -m "feat: add AI-generated isometric illustrations for landing page"
```

---

### Task 3: Build the Landing Page HTML — Structure and CSS

**Files:**
- Create: `docs/index.html`

This task creates the full HTML file with all CSS custom properties, typography, layout, responsive breakpoints, and the scroll-fade JS. Content sections are added in the next task.

- [ ] **Step 1: Create `docs/index.html` with head, CSS, and empty body structure**

Write the complete HTML file with:
- `<!DOCTYPE html>`, charset, viewport meta
- SEO meta tags (title, description, OG, Twitter Card)
- Google Fonts link for Inter + JetBrains Mono (with `display=swap`)
- Full `<style>` block with:
  - CSS custom properties (color system from spec)
  - Reset/base styles (box-sizing, margin, smooth scroll)
  - Typography (headings, body, monospace, `.subtitle`, `.stat-pill`)
  - Section layout (`.section` full-width with padding, max-width inner container)
  - Comparison table styles
  - Terminal block styles (`.terminal`)
  - Sandbox pillars (`.pillar` — full-width row with left amber border)
  - Philosophy row (`.philosophy-grid` — 3-col, stacks on mobile)
  - Feature alternating layout (`.feature` with `.feature-text` + `.feature-img`, alternates via `:nth-child(even)`)
  - Extension grid
  - CTA button (`.btn-primary` amber gradient)
  - Footer
  - Responsive: stack to single column below 768px
  - `.fade-in` class (opacity 0, translateY 20px, transition 0.6s)
  - `.fade-in.visible` (opacity 1, translateY 0)
- Minimal `<script>` at bottom: IntersectionObserver watching `.fade-in` elements, adds `.visible` on intersect

The body should have empty `<section>` shells with correct IDs and classes:
```html
<section id="hero" class="section">...</section>
<section id="comparison" class="section">...</section>
<section id="how-it-works" class="section">...</section>
<section id="sandbox" class="section">...</section>
<section id="philosophy" class="section">...</section>
<section id="features" class="section">...</section>
<section id="extensions" class="section">...</section>
<section id="cta" class="section">...</section>
<footer>...</footer>
```

Reference the spec's color system (lines 28-41) and section background gradients (lines 53, 66, 74, 86, 95, 105, 113, 121) for exact values.

- [ ] **Step 2: Open in browser to verify base styles render**

```bash
open /Users/sbusso/Code/dev/claudeclaw/docs/index.html
```
Expected: Dark background, no errors in console, empty sections with correct gradient backgrounds visible.

- [ ] **Step 3: Commit**

```bash
git add docs/index.html
git commit -m "feat: landing page scaffold with CSS system and responsive layout"
```

---

### Task 4: Build the Landing Page HTML — Section Content

**Files:**
- Modify: `docs/index.html`

Fill in each section's HTML content. Reference the spec section-by-section (lines 45-127).

- [ ] **Step 1: Hero section**

Inside `<section id="hero">`:
- Logo `<img>` (64px, border-radius 16px)
- `<h1>ClaudeClaw</h1>`
- Subtitle `<p class="subtitle">`
- Stat pills container with 3 `<span class="stat-pill">` elements
- Terminal block with the 3-line quick start
- Hero illustration `<img src="assets/hero.png" loading="lazy" alt="ClaudeClaw architecture overview">` (all illustration `src` attributes use `.png` — the Gemini skill outputs PNG by default)
- All inner content wrapped in a `<div class="container fade-in">`

- [ ] **Step 2: Comparison section**

Inside `<section id="comparison">`:
- `<h2>Why not OpenClaw?</h2>`
- `<p class="subtitle">OpenClaw is a platform. ClaudeClaw is a tool. Same problem, different philosophy.</p>`
- `<table>` with 7 rows (header + 6 data rows per spec line 59-65)
- ClaudeClaw column highlighted with `--accent` color
- Wrap in `<div class="container fade-in">`

- [ ] **Step 3: How It Works section**

Inside `<section id="how-it-works">`:
- `<h2>How it works</h2>`
- `<p class="subtitle">Single process. Channels in, sandboxed agents out.</p>`
- Architecture illustration `<img src="assets/architecture.png" loading="lazy">`
- Wrap in `<div class="container fade-in">`

- [ ] **Step 4: Sandbox & Security section**

Inside `<section id="sandbox">`:
- `<h2>Sandbox-first security</h2>`
- `<p class="subtitle">The kernel enforces isolation, not your application code.</p>`
- 4 pillar divs (`.pillar` — full-width stacked rows, NOT grid):
  1. Kernel isolation
  2. Network restriction
  3. Zero overhead
  4. Per-group boundaries
- Sandbox illustration `<img src="assets/sandbox.png" loading="lazy">`
- Each pillar has: `<div class="pillar-title">` (amber, uppercase, small) + `<p>` (description)
- Wrap in `<div class="container fade-in">`

- [ ] **Step 5: Philosophy section**

Inside `<section id="philosophy">`:
- `<h2>A tool, not a platform</h2>`
- `<div class="philosophy-grid">` with 3 children:
  1. Small enough to understand
  2. Built for one person
  3. Code is configuration
- Each: amber `<h3>` title + `<p>` description
- Wrap in `<div class="container fade-in">`

- [ ] **Step 6: Features section**

Inside `<section id="features">`:
- `<h2>Features</h2>`
- 4 `.feature` divs, each containing `.feature-text` + `.feature-img`:
  1. Multi-channel routing + channels illustration
  2. Structured memory (text only — spec lists illustration but deferred to keep initial launch lean)
  3. Three trigger modes (text only — deferred)
  4. Cost tracking & limits (text only — deferred)
- Feature 1 uses `<img src="assets/channels.png" loading="lazy">`
- Features 2-4 are text-only for now. The CSS `.feature` layout should gracefully make text full-width when no image is present. Additional illustrations can be generated later.
- Wrap in `<div class="container fade-in">`

- [ ] **Step 7: Extensions section**

Inside `<section id="extensions">`:
- `<h2>Composable extensions</h2>`
- `<p class="subtitle">Install only what you use. No merge conflicts.</p>`
- Terminal block showing install commands
- Extension grid: 2 available (slack, triage) + 5 planned (discord, gmail, memory, obsidian, tui) with dashed borders and muted text
- Wrap in `<div class="container fade-in">`

- [ ] **Step 8: CTA section**

Inside `<section id="cta">`:
- `<h2>Get started in 30 seconds</h2>`
- `<p>` with requirements
- Terminal block with full clone/setup commands
- `<a class="btn-primary" href="https://github.com/sbusso/claudeclaw">View on GitHub →</a>`
- Wrap in `<div class="container fade-in">`

- [ ] **Step 9: Footer**

Inside `<footer>`:
- Left: `MIT License · Built on NanoClaw`
- Right: links to GitHub, Discussions, Claude Agent SDK
- Single row, flexbox space-between

- [ ] **Step 10: Open and verify full page**

```bash
open /Users/sbusso/Code/dev/claudeclaw/docs/index.html
```
Expected: All 9 sections render correctly with gradient backgrounds flowing, illustrations loading, scroll fade-in working, responsive on resize.

- [ ] **Step 11: Commit**

```bash
git add docs/index.html
git commit -m "feat: complete landing page with all sections and content"
```

---

### Task 5: Polish and Responsive Testing

**Files:**
- Modify: `docs/index.html`

- [ ] **Step 1: Test at 375px width (mobile)**

Open browser dev tools, resize to 375px. Check:
- Philosophy grid stacks to single column
- Feature alternating layout stacks (text above image)
- Comparison table is scrollable horizontally or reformats
- Stat pills wrap
- Terminal blocks don't overflow
- All text readable

Fix any issues found.

- [ ] **Step 2: Test at 768px width (tablet)**

Check intermediate breakpoint. Fix layout issues.

- [ ] **Step 3: Test at 1440px+ (desktop)**

Ensure max-width container keeps content readable. No horizontal scroll. Illustrations sized appropriately.

- [ ] **Step 4: Verify scroll fade-in animations**

Scroll through the page. Each section should fade in as it enters the viewport. Check that IntersectionObserver fires correctly.

- [ ] **Step 5: Commit any fixes**

```bash
git add docs/index.html
git commit -m "fix: responsive layout and animation polish"
```

---

### Task 6: Deploy to GitHub Pages

- [ ] **Step 1: Verify docs/ structure is complete**

```bash
ls -R /Users/sbusso/Code/dev/claudeclaw/docs/assets/
```
Expected: `logo.webp`, `hero.png`, `architecture.png`, `sandbox.png`, `channels.png` (illustrations are `.png` from Gemini output)

- [ ] **Step 2: Push to main**

```bash
git push origin main
```

- [ ] **Step 3: Enable GitHub Pages**

```bash
gh api repos/sbusso/claudeclaw/pages -X POST -f source.branch=main -f source.path=/docs 2>/dev/null || \
gh api repos/sbusso/claudeclaw/pages -X PUT -f source.branch=main -f source.path=/docs
```

- [ ] **Step 4: Verify deployment**

```bash
gh api repos/sbusso/claudeclaw/pages --jq '.html_url'
```

Wait ~60s then check the URL in browser. Expected: Landing page renders correctly at the GitHub Pages URL.

- [ ] **Step 5: Commit any final adjustments** (if canonical URL needs updating in meta tags)

```bash
git add docs/index.html
git commit -m "fix: update canonical URL to GitHub Pages domain"
git push origin main
```

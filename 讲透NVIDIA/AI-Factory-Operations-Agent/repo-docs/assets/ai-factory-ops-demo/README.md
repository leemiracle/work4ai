<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# AI Factory Operations Agent — motion graphics demo

A 31s, 1920×1080 @ 60fps cinematic explainer for the NVIDIA
[AI Factory Operations Agent](https://build.nvidia.com/nvidia/operate-ai-factories-with-agents)
blueprint ([source repo](https://github.com/NVIDIA/AI-Factory-Operations-Agent)).

This is an illustrative motion graphics explainer with synthetic telemetry and
synthesized audio. It contains no recorded cluster session or measured results.

`out/ai-factory-operations-agent.mp4` is the current render.
`out/ai-factory-operations-agent-15s.mp4` is the same sequence at a faster pace.

## What it's made of

No motion graphics library — no After Effects, Lottie, or Remotion. ~510 lines total.

| file | role |
| --- | --- |
| `demo.html` | The whole picture. One `<canvas>`, raw Canvas 2D. |
| `audio.py`  | The whole score, synthesized in numpy. No samples. |
| `render.py` | Playwright drives headless Chromium and screenshots each frame. |
| `build.sh`  | fonts → score → frames → mp4. |
| `fetch_fonts.py` | Pulls the two webfonts (not committed — see below). |

The animation is one pure function of time:

```js
window.renderFrame = f => draw(f / 60);
```

`draw(t)` paints the entire frame from scratch. No animation loop, no tweening,
no state carried between frames. Scenes are fade windows over `t`:

```js
const p   = (t,a,b)     => clamp((t-a)/(b-a));   // 0→1 between two times
const win = (t,a,b,c,d) => ...                   // in, hold, out
```

Per-frame randomness (which LED blinks when) comes from a seeded PRNG built once
at load. **Renders are therefore deterministic** — change one scene and re-render
only its frames: `uv run --with playwright python render.py frames $(seq 675 945)`.

## Build

Needs `uv`, `ffmpeg`, and a Chromium for Playwright
(`uv run --with playwright playwright install chromium`).

```bash
./build.sh          # ~4 min on an M-series laptop
JOBS=8 ./build.sh   # more parallel browsers
./cut-15s.sh        # derive the 15-second cut from the current render
```

## Fonts

Not committed, fetched on first build. NVIDIA Sans is NVIDIA's brand font and is
pulled from nvidia.com's CDN; Barlow and JetBrains Mono come from Google Fonts.
Keeping the binaries out leaves the repo text-only.

## The cut

| t | beat |
| --- | --- |
| 0.0 | Telemetry grid ignites from the centre; bold title |
| 5.2 | One node goes red, camera pushes in — "a training run has stopped" |
| 11.4 | The operator asks, typed live; browser ui / mosaic cli / mosaic-mcp |
| 15.4 | Datacenter row on top, six agents below, zones lighting in sequence |
| 22.1 | The agents converge; the root cause forms where they meet |
| 25.3 | The answer flies out and lands on the red node — it turns green |
| 27.5 | "back to work" |

The five datacenter zones map to the agents that read them: power → Hardware;
compute → Hardware + Observability; fabric → Observability + Job recovery;
storage → Job recovery + Research; control plane → Kubernetes + Cluster management.

## Making changes

Most edits are one or two lines. The timings live in one table at the top of `demo.html`:

```js
const T = {title:1.6, fault:5.2, ask:11.4, sys:15.4, heal:25.3};
```

| to change | edit |
| --- | --- |
| Scene timing | `T` in `demo.html`, and the matching cue times in `audio.py` |
| Zone pacing | `step` in `system()` |
| Agents / their tools | `AG` and `ZONES` |
| Copy | the `txt(...)` calls in `draw()` |
| Palette | `G` / `GD` / `R` / `WH` at the top |
| Length | `DUR` (and `DUR` in `audio.py` — they must match) |

Audio cue times are absolute seconds and must be moved in step with `T`, or
impacts land off their beats.

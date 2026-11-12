# space-demo-kit

Renders polished social demo videos (MP4) for Hugging Face Spaces. Each video looks like
the Space's own Gradio app doing its thing: the real HF Space header (emoji, `author/name`,
like count, "Running on ZERO"), inputs appearing in panels, a **Generate** press, a progress
sweep, and the real output filling the output panel — no marketing cards, no slogans.

- One HTML template, seven task modes: `i2v`, `t2v`, `edit`, `avatar`, `a2a`, `gallery`, `vqa`
- Branding (emoji, gradient, likes, hardware) is extracted from the Space page
- Media-first layout tuned for mobile feeds (big type, thick strokes, media > 50% of frame)
- Deterministic rendering: a seekable JS timeline stepped frame-by-frame through headless
  Chromium, assembled with ffmpeg (1440x1080, 30 fps, H.264, bt709)
- Audio modes mux the real audio in sync with on-screen playback (2x gain + limiter)

## Requirements

- Python 3.10+, `playwright` (`pip install playwright && python -m playwright install chromium`)
- ffmpeg / ffprobe
- Network on first run (downloads fonts, twemoji, HF logo)

## Usage

Write a manifest describing the demo (see `skills/space-demo-video/SKILL.md` for the full
schema and workflow), then:

```bash
python3 render.py manifests/my-demo.json
# -> out/my-demo/my-demo.mp4  +  out/my-demo/my-demo-contact.jpg
```

Example manifest (image edit):

```json
{
  "name": "krea-edit",
  "template": "edit",
  "space": { "id": "hugging-apps/krea2-identity-edit", "emoji": "🧬",
             "colorFrom": "blue", "colorTo": "gray", "likes": 27, "hardware": "zero-a10g" },
  "input_image": "/abs/path/woman.jpg",
  "prompt": "create a photo of this person at a busy night market at night",
  "before_image": "/abs/path/woman.jpg",
  "after_image": "/abs/path/woman_edited.webp",
  "input_label": "source image",
  "prompt_label": "edit instruction",
  "output_label": "edited image",
  "meta": "live output · zero-a10g"
}
```

The `manifests/` directory contains real examples for all seven modes.

## The end-to-end pipeline

How the fully automated videos (the ones on [hf.co/buckets/Mike0021/hugging-app-videos](https://huggingface.co/buckets/Mike0021/hugging-app-videos)) get made:

```
user message ("make a demo video for Space X")
   |
   v
orchestrator agent          any agent works: OpenClaw, Claude Code, Codex CLI...
   |                        it reads skills/space-demo-video/SKILL.md and dispatches
   v                        a worker session for the heavy lifting
worker session (codex)
   1. curl https://huggingface.co/api/spaces/<id>     -> emoji, colors, likes, hardware
   2. pick a real example input (the Space's own examples work best)
   3. run the LIVE Space via gradio_client            -> real output artifact
   4. write manifests/<name>.json                     (facts + asset paths only)
   5. python3 render.py manifests/<name>.json         -> MP4 + contact sheet
   6. verify (ffprobe + look at the contact sheet), deliver/post
```

The design is fully owned by the template (`templates/app-window.html`); agents never draw
frames. That is what keeps quality consistent across runs: an agent can only feed the
renderer facts and real assets.

Portability notes:
- The kit itself (steps 4–5) is plain Python + Playwright + ffmpeg; nothing OpenClaw-specific.
- `SKILL.md` uses the OpenClaw agent-skill format (frontmatter + markdown) and assumes the kit
  lives at `/root/code/space-demo-kit`; adjust paths for your host. It drops into Claude Code
  as a skill nearly unchanged.
- The "codex dispatch" section of the skill is about keeping a chat agent responsive during
  the ~10 min inference+render; if your orchestrator is fine blocking, ignore it.

## Agent skill

`skills/space-demo-video/SKILL.md` is an agent-facing skill (OpenClaw workspace skill format)
that teaches an agent when and how to use the kit: template selection, manifest schema,
live-inference asset capture, verification, and honest labeling of mocked assets.

## Structure

```
render.py                      # manifest -> MP4 (Playwright frame stepping + ffmpeg)
templates/app-window.html      # the single design template (all seven modes)
manifests/                     # example manifests
skills/space-demo-video/       # agent skill
```

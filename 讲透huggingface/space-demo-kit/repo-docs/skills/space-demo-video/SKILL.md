---
name: space-demo-video
description: "Create a polished social demo video (MP4, 4:3, ~10s) for any Hugging Face Space with the space-demo-kit renderer. Use whenever the user asks for a demo, promo, showcase, or social video of a HF Space or model. Covers template selection (i2v, t2v, edit, avatar, a2a, gallery, vqa), manifest schema, live asset capture, rendering, verification, and delivery."
---

# Space Demo Video (space-demo-kit)

The kit renders a Gradio-style "app window" video: a hero intro where the input opens
near full-frame with the prompt typing in large text (readable at mobile feed size),
a morph into the app layout with the Space's real header (emoji, author/name, likes,
hardware), a Generate press, a progress sweep, and the real output filling the output
panel edge-to-edge. Text auto-fits its panels (short answers render huge, long ones stay
readable). Branding is extracted from the Space page automatically. Output: 1440x1080
(4:3), 30 fps, ~12–17 s, H.264, silent unless the task itself involves audio.

Kit location on this machine: `/root/code/space-demo-kit`
Render command (the ONLY way to produce the video):

```bash
cd /root/code/space-demo-kit && python3 render.py manifests/<name>.json
# -> out/<name>/<name>.mp4  +  out/<name>/<name>-contact.jpg
```

## Golden rules

1. **Never design video frames by hand.** No PIL cards, no ffmpeg drawtext/overlay design,
   no custom HTML. The kit owns 100% of the design; you only supply facts and assets via a
   manifest JSON.
2. **Real outputs.** Generate the output by calling the live Space (`gradio_client`) with a
   real input. Only mock when live inference is impossible (quota, broken Space), and then
   label it honestly in the manifest `meta` field (e.g. `"mock demo assets"`) and tell the user.
3. **Real branding.** Pull `emoji`, `colorFrom`, `colorTo`, `likes`, and hardware from
   `https://huggingface.co/api/spaces/<id>` (`cardData` + `runtime.hardware.current`).
   If the user gives a MODEL id, resolve its demo Space first (model page / `spaces` field of
   `https://huggingface.co/api/models/<id>`).
4. **Prompts under 160 chars.** The renderer truncates displayed prompts around 150 chars;
   pick or write inputs that fit.
5. **Verify before delivering**: `ffprobe` the MP4 (duration, 1440x1080) and look at the
   contact sheet (no overflowing text, output visible). Then send the MP4 to the user as media.
6. **One look only.** Never put a `"style"` key in a manifest — the app-window template is the
   only production design and the renderer ignores styles. Anything under `experiments/` is a
   rejected prototype: never use it as an example or reference.

## Asset quality bar (hard requirements)

- **Inputs must be real content**: a real photograph, illustration, or clip at least 512 px on
  the short side. NEVER an emoji, icon, favicon, logo, or clipart — tiny images upscale into
  blurry blobs and ruin the video. Verify every asset with `file` + dimensions before using it.
- **Best input source**: the Space's own example assets (the `examples` in its Gradio config,
  or files in the Space repo via `https://huggingface.co/api/spaces/<id>/tree/main`). They are
  known to work with the model.
- **Before/after coherence (`edit`, `a2a`)**: the output MUST actually be derived from the
  input. Never pair two unrelated assets — an incoherent before/after is worse than no video.
  If live inference fails: retry via `gradio_client` (not hand-built HTTP calls), try another
  example input, and if it still fails, report the failure to the user and STOP. Do not
  fabricate the pair.

## Template selection

| template | Space task | required manifest fields |
|---|---|---|
| `i2v` | image → video | `input_image`, `prompt`, `video` (generated clip) |
| `t2v` | text → video | `prompt`, `video` |
| `edit` | image + instruction → image | `input_image`, `prompt`, `before_image`, `after_image` |
| `avatar` | portrait + audio → talking video | `input_image`, `audio`, `video` (audio can be the generated mp4 itself) |
| `a2a` | audio → audio | `audio_in`, `audio_out` |
| `gallery` | one input → several images | `input_image`, `prompt`, `outputs` (list of `{path, label}`, 4 items) |
| `vqa` | video/image + question → text | `video`, `prompt`, `answer` |

Text-to-image Spaces use `t2v`: turn the generated image into a short static clip first
(`ffmpeg -loop 1 -i out.webp -t 6 -r 30 -pix_fmt yuv420p static.mp4`) and pass it as `video`
(see `manifests/z-image-turbo-demo.json`). There is no `t2i` template.

## Manifest schema

Common fields (all templates):

```json
{
  "name": "my-demo",                    // output folder + file name
  "template": "edit",
  "space": {
    "id": "owner/space-name",
    "emoji": "🧬",                      // from cardData
    "colorFrom": "blue",                // from cardData
    "colorTo": "gray",                  // from cardData
    "likes": 27,                        // from the API
    "hardware": "zero-a10g"             // runtime.hardware.current
  },
  "meta": "live output · zero-a10g",    // small honest footer note; use "mock demo assets" for mocks
  "button": "Generate",                 // optional; e.g. "Enhance", "Animate"
  "input_label": "source image",        // optional label overrides
  "prompt_label": "edit instruction",
  "output_label": "edited image",
  "audio_gain": 2.0,                    // optional; default 2.0 (with limiter)
  "hero": false                         // optional; set false to skip the full-frame intro
}
```

Plus the template-specific fields from the table. All asset paths are absolute paths on
this machine. Store working assets under `/root/code/<project-dir>/` as usual.

## Workflow

1. `curl -s https://huggingface.co/api/spaces/<id>` → metadata for `space{}` fields.
2. Pick the template from the table. If the Space's task fits none of them, say so and pick
   the closest; do NOT invent a new design.
3. Capture assets: choose a good input (the Space's own example assets are ideal), run the
   live Space with `gradio_client`, download the real output. Verify the output file with
   `ffprobe`/`file` before rendering.
4. Write `manifests/<name>.json` in the kit.
5. Render (command above). First run downloads fonts/emoji (needs network) and, for video
   inputs, extracts frames. A render takes roughly 3–5 minutes — do not assume it hung.
6. Verify MP4 + contact sheet, then deliver the MP4 to the user as a media message.

## Codex dispatch (OpenClaw — mandatory)

Demo-video requests are heavy (live inference + a ~2 min render). Do NOT run inference or
rendering inline in the main session — it blocks you for many minutes. ALWAYS dispatch a
codex session per the codex-monitor skill (setsid, `</dev/null`, CODEX_HOME pinned) and let
the CODEX_FINISHED wake drive verification + delivery. Include in the codex prompt:
"Read /root/code/space-demo-kit/skills/space-demo-video/SKILL.md and follow it exactly.
Use the kit's render.py for ALL visuals; do not design any frame yourself."

## Gotchas

- Long Space ids auto-shrink in the footer; long repo names get ellipsized in the header — fine.
- The renderer needs Playwright + Chromium (already installed system-wide here).
- Audio templates (`avatar`, `a2a`) mux the real audio automatically, delayed to the moment
  playback starts on screen, at 2x gain with a limiter.
- `gallery` wants exactly 4 outputs for the 2x2 grid.
- `vqa` answers auto-fit the output panel: keep them 30–60 words so the type stays large.
- Do not edit `templates/app-window.html` or `render.py` for a one-off video. If a Space
  genuinely needs a new mode, report that instead of hacking around the kit.

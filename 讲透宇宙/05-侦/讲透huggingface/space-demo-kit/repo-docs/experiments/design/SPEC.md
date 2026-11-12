# VIRAL TEMPLATE FAMILY — CANONICAL DESIGN SPEC v1

Single source of truth for the builder. Merges 4 lens specs (story, art direction, motion,
quality bar) into one self-consistent system for `templates/viral.html`. Covers
**t2i, a2a, i2v, edit** (this implementation round) + short extension notes for
**t2v, vqa, avatar, gallery**.

## 0. Provenance / access gap

`/Users/vm/.claude/image-cache/44934587-0225-430f-91e0-5c1c687117a4/10.png` (the loved UniSE
reference) does not exist on disk — confirmed independently by all 4 lens agents and by this
merge pass (dir absent). This spec is built from CONTEXT.md's explicit prose analysis of that
image (huge type, rust/steel two-color editorial system on warm paper, ORIGINAL/ENHANCED cards,
NOW PLAYING state, zero chrome, "frame one already tells the whole story") plus direct pixel
inspection of all 6 baseline contact sheets (`x-resemble-poster/fullbleed/cards.jpg`,
`x-zimage-poster/fullbleed/cards.jpg`), read again during this merge. Flag to the orchestrator
if pixel-exact parity with `10.png` matters later.

Baseline defects directly observed (drives every decision below): payoff image at ~8-15% of
frame area inside oversized empty boxes (poster, cards); prompt/caption boxes teleport
position/size frame-to-frame (cards); "GENERATED IMAGE" panel empty with blinking cursor for
the first ~2.5s (poster, fullbleed); malformed/inconsistent timecodes (`0:005` vs
`00.4 / 10.0 SEC`); waveforms flat-mirrored/synthetic-looking; 4-5 competing hues per frame;
ungoverned gradient backgrounds (cards); chrome literally bisecting headline glyphs
(fullbleed); redundant restatement of the same fact 3-4x per frame; no single grid — spacing
is ad hoc; every transition is a generic fade/slide with no rhythm.

## 1. Key decisions (conflicts resolved, not debated)

The 4 lenses disagreed on several load-bearing points. Decisions below are final and override
any conflicting statement elsewhere in the source lens specs.

1. **Cold-Open Split is the pattern.** Output pixel/audio is present, at real final quality, at
   literal frame 0 (t=0.000s) for all four modalities, no exceptions. This overrides the motion
   lens's original t2i timing (which had the image hidden behind a typing+"GENERATING…"+
   clip-path-reveal sequence resolving at t≈3.6-4.2s), its a2a timing (1s of silent "pre-roll
   tension" before audio starts), and its i2v timing (video frozen/hidden until an iris-wipe at
   t≈1.6-2.1s). All three reproduced the named defect ("output appears late; first seconds are
   empty chrome or typing") and are deleted. The motion lens's easing curves, transition
   grammar, and continuous-motion invariant survive and are re-timed onto the cold-open beats
   below.
2. **Entrance choreography keeps its shape, loses its power to hide content.** Opacity is
   pinned at 1.0 for all payoff-critical elements (title, tagline, labels, media, URL) from
   t=0.000 onward — nothing fades in from invisible. The 0-320ms staggered "snap" window
   survives only as a small `translateY` position micro-settle (≤8px) on already-fully-visible
   content, giving a "just landed" cascade without ever showing an incomplete frame. This is
   necessary because feed thumbnails may sample any early frame, not just literal frame 0.
3. **a2a waveforms are never desaturated.** Rejects the art-direction lens's `--ink-45`
   grey-until-its-turn treatment for the inactive card. Both waveforms render in full role hue
   (rust or steel) at all times; only opacity differs (100% active / 55% inactive). This
   satisfies "always both visible, full color" and the quality bar's "one consistent
   opacity/color rule applied identically to both tracks."
4. **Color system is fixed editorial (rust/steel/paper), not Space-derived.** `colorFrom`/
   `colorTo` are not used anywhere in the visual system. A fixed palette guarantees contrast
   and gives the video family a recognizable, magazine-masthead consistency across arbitrary
   Spaces. Space identity carries only via manifest `title` and `emoji`.
5. **Edit uses a single wipe-card, not a side-by-side diptych.** Rejects the art-direction
   lens's "fixed diptych, no slider" layout and its stated rationale ("a slider reads as UI
   chrome"). A deterministic, `seek(t)`-driven clip-path wipe has no drag affordance, no cursor,
   no handle graphic — it is a cinematic before/after device, not UI chrome, and it is the
   strongest available causality gesture of the four modalities. A static diptych has no hero
   moment of its own and would violate the universal "one BIG moment per video" rule. BEFORE/
   AFTER labels sit above a single lane card at fixed positions; only the image content wipes.
6. **i2v layout is split-rail → full-bleed reframe, not a small centered "framed print insert."**
   Rejects the art-direction lens's compact 276×368 centered video composition — that layout
   reproduces the single worst-scoring baseline defect (payoff media confined to <15% of frame
   area) that the quality-bar lens itself flagged as the top offender. i2v is the one modality
   whose hero moment is allowed to break the layout-stable grid: after the reframe, video goes
   genuinely full-bleed (canvas edge-to-edge) with only a small persistent 200×200 corner photo
   chip and a footer scrim strip surviving. This is a deliberate, singular exception, stated
   here so no one "fixes" it back to grid-locked.
7. **WIPE transition class budget = one hero-moment SLOT per video, not one clip-path call.**
   Edit's hero moment is a single choreographed multi-beat gesture (sweep out → sweep back →
   settle → echo sweep) told across ~2.6s of screen time — this counts as ONE hero-moment slot,
   not five separate wipes. No modality gets a second, unrelated clip-path reveal anywhere else
   in its timeline (e.g. URL/footer emphasis pulses use a brightness/scale pulse, never
   clip-path — see §5 per-modality tables).
8. **Quality-bar checklist item 5 ("≥60% of frame area") is measured against the Body Zone**
   (the region not permanently reserved for hook-title/attribution chrome) for t2i, a2a, and
   edit — the fixed 96px-margin, layout-stable grid (decision below) makes a literal 60%-of-
   full-1440×1080-canvas target for those three architecturally incompatible with also carrying
   a legible hook title and a never-truncated URL, both separately mandated. For i2v, item 5 is
   measured against the full canvas, since decision #6 explicitly lets that modality's payoff
   go full-bleed. Payoff media must always claim the *maximum* height its modality's zone budget
   affords (the Lane component rule, §3.5) — never smaller, never stretched.
9. **Grid, type scale, color tokens, and texture/depth are adopted verbatim from the
   art-direction lens** (§3 below) — this is the most concretely specified, internally
   consistent part of the four lenses and directly resolves ~10 of the cheap-tell defects
   (dead space, teleporting elements, ad hoc spacing, mixed corner radii, floating shadowed
   cards).
10. **Easing curves, transition grammar, and the continuous-motion invariant are adopted from
    the motion lens** (§4 below), with hero-moment mechanics re-authored per decisions #1, #5,
    #6 to fit the Cold-Open Split beats.
11. **Durations, frame-accurate:** t2i = 8.0s / 240f. a2a = 10.2s / 306f (locked to real audio:
    5.2s original + 5.0s enhanced, `playStart = 0.0`, zero padding). i2v = 8.0s / 240f (real
    video 6.53s @ 32fps embedded, held on last frame for the remainder). edit = 8.0s / 240f.
    Three of four share 8.0s for series consistency; a2a is honestly locked to its real content
    length per the no-padding rule.
12. **No typing, no spinners, no "GENERATING…" state, ever.** Deleted globally, including the
    motion lens's type-hook/gen-sweep-marquee beats for t2i.

## 2. Story pattern — Cold-Open Split

**Definition:** input and output are both fully legible, at real final content, at t=0.000 in
every modality. Runtime after frame 0 proves, savors, and loops what was already shown — it
never reveals it for the first time.

**Why:** the loved reference works because "frame one already tells the whole story." The
named baseline defect is "the story buries the payoff: output appears late; first seconds are
empty chrome or typing." Cold-Open Split is the direct, structural fix — not a tweak.

**Rejected patterns:** *Linear* (type→generate→reveal near the end) is what the current
baseline already does; it is the defect, not a fix. *Tease-then-reveal* (blur/obscure output,
resolve later for suspense) optimizes for a curiosity gap the ≤2s/390px scroll-past test
punishes — a viewer who doesn't stop within 2s never sees the resolve.

### 2.1 Universal rules (all modalities, including future t2v/vqa/avatar/gallery)

| Rule | Statement |
|---|---|
| Thumbnail-safe window | Every frame in t∈[0.0, 2.0]s must, alone, communicate input + output + Space identity. Feed previews may sample any early frame, not exactly frame 0. |
| Always-both-visible | At every t, an input representation and an output representation are simultaneously on screen — full-size or a persistent labeled corner chip ≥12% frame width (i2v post-reframe). No beat shows output-only or input-only for longer than a single-frame crossing (<100ms). |
| No typing, no spinners, no empty chrome | Prompts/instructions render fully formed at t=0. No letter-by-letter typing, no blinking cursor, no "GENERATING…" empty-box state, ever. |
| No fade-to-black outro | End states hold on content; never cut to a blank/dead card. |
| One BIG moment per video | Exactly one deliberate, medium-specific hero moment (§5). Never a generic fade/slide shared across modalities. |
| Word budget ceiling | Persistent chrome ≤12 words when there's no real prompt/instruction caption; prompt/instruction captions are content, exempt from the ceiling, but shown in full at t=0 — never truncated then completed. |
| URL never truncated | `hf.co/spaces/<id>` on screen 100% of duration, full string, every modality. |
| Silent unless audio-native | t2i/i2v/edit: fully silent. a2a (and avatar, §6): real audio, 2x gain, starts at or before t=0.1s (this spec: exactly t=0.000) — never after a visual lead-in. |
| Loop philosophy | Pixel-seamless loop (end frame == frame-0 composition) where the medium allows it (t2i, edit). Where a hard cut is unavoidable (a2a's audio reset, i2v's split↔full-bleed cut), make the outro composition *rhyme* with the opening rather than differ maximally. Never pad real duration or loop source content to fake a seamless loop. |

### 2.2 First-frame thumbnail test

| Modality | Frame 0 composition | Passes "X in → Y out, this good" in ≤2s? |
|---|---|---|
| t2i | Full hero output image (real final pixels) + full prompt caption + title/tagline + URL | Yes — image is the whole frame |
| a2a | Two full-hue waveform cards (ORIGINAL rust 100%, ENHANCED steel 55%) + title + URL | Yes — shape reads as before/after pair; ear confirms by t≈1s |
| i2v | Split: photo rail (32%) + video's own first frame (68%, already playing), matched framing | Partial exactly at t=0.000 (a frozen grab can't prove motion); definitive by t=0.5s once motion diverges — inherent to any video-output modality |
| edit | 50/50 wipe split: full BEFORE left / full AFTER right, both real pixels, full instruction caption | Yes — both images + instruction on screen simultaneously |

## 3. Visual system

Canvas 1440×1080, 30fps. Fonts (already fetchable, no new FONTS entries needed): Space Grotesk
(500/700), Source Sans 3 (400/600/700), IBM Plex Mono (400/500).

### 3.1 Grid

Base unit `u = 8px`. Only these steps may appear anywhere in layout: `u2=16, u3=24, u4=32,
u6=48, u12=96, u20=160, u25=200`. No other spacing value is permitted.

Margin: fixed `96px` all four sides, every frame, every timestamp — **layout-stable** except
for i2v's post-reframe hero window (decision #6). Content box: x 96–1344 (w=1248), y 96–984.

Shared vertical rhythm, identical across t2i/a2a/edit (i2v uses it only up to the reframe):

```
y=96   margin-top
       Title (Display)              h=112
gap 24
       Subhead (tagline)             h=40
gap 24
       hairline rule + gap 32
y=328  ── BODY ZONE START (1248×600, modality-specific content) ──
y=928  ── BODY ZONE END ──
       hairline rule, gap 24
       Footer text                   h=32
       margin-bottom 96
y=1080
```

Title/Subhead/hairlines/Footer occupy identical y-ranges across all modalities and the full
duration of every clip — only Body Zone content changes over time. This is the mechanism that
reproduces "frame one already tells the whole story" for every frame, not just frame one.

### 3.2 Type scale

| Role | Family | Weight | Size | Tracking | Leading | Color | Case |
|---|---|---|---|---|---|---|---|
| Display (title) | Space Grotesk | 700 | 108px | -0.02em | 0.96 | `--ink` | as-given |
| Subhead (tagline) | Source Sans 3 | 600 | 32px | 0 | 1.3 | `--ink-70` | sentence |
| Eyebrow (ORIGINAL/PROMPT/BEFORE/etc.) | IBM Plex Mono | 500 | 26px | +0.10em | 1.0 | `--rust`/`--steel` (role) | UPPERCASE |
| Body/Quote (prompt, instruction) | Source Sans 3 | 600 | 40px | 0 | 1.35 | `--ink` | sentence, curly quotes |
| Data/Timecode | IBM Plex Mono | 400 | 28px | +0.02em | 1.0 | `--ink-45` | tabular-nums |
| Footer (url, mock note) | IBM Plex Mono | 500 | 30px | +0.01em | 1.0 | url=`--ink-70`, note=`--ink-45` | as-given |
| Micro (likes/hardware — OFF by default) | IBM Plex Mono | 400 | 20px | +0.04em | 1.0 | `--ink-45` | UPPERCASE |

Vanity metrics (likes/hardware) are omitted by default — they don't serve the 2-second
comprehension test; every element must be information, not decoration.

**390px downscale check** (scale 0.2708, matches `ffmpeg scale=390:-1` QA): Display→29px,
Subhead→9px, Eyebrow→7px, Body→11px, Data→8px, Footer→8px. Eyebrow words are short tracked
uppercase mono "shape words" (legible at 7px even if not readable letter-by-letter); Display
and Footer — the two hard-requirement roles (comprehension + never-truncated URL) — both clear
8-9px, safely legible. Verify these two first in the 390px test.

### 3.3 Color tokens

```css
--paper:   #F3EADA;                 /* canvas background, flat, no gradient, no exceptions */
--ink:     #241C14;                 /* Display/Body text */
--ink-70:  rgba(36,28,20,0.70);     /* Subhead, footer url */
--ink-45:  rgba(36,28,20,0.45);     /* Data role, footer note — NEVER used to desaturate a2a inactive card, see decision #3 */
--line:    rgba(36,28,20,0.12);     /* hairline rules, 1.5px */
--rust:    #9A3D1C;                 /* accent A: the thing that goes IN — prompt, original, before, source */
--rust-25: rgba(154,61,28,0.25);
--steel:   #2E5266;                 /* accent B: the thing that comes OUT — generated, enhanced, after, video */
--steel-25: rgba(46,82,102,0.25);
```

Semantic rule, zero exceptions, reused identically across all 4 modalities: **rust = input,
steel = output.** Max 2 accents on screen simultaneously in every modality. `colorFrom`/
`colorTo`/likes/hardware are not used (decision #4).

### 3.4 Texture & depth

- No drop shadows anywhere — hierarchy comes from line-weight and color, not shadow.
- Hairline rules: 1.5px solid `--line`, only at the 2 fixed points in the vertical rhythm.
- Frame border (every Lane component): 3px solid, `--rust`/`--steel` per role, radius 12px.
  One border weight, one radius, everywhere.
- Grain: deterministic seeded value-noise, seed=1440108, tiled 512×512, opacity 0.035,
  `mix-blend-mode: multiply`, rendered once as a static full-canvas overlay div — byte-identical
  across every `seek()` call, drifting only via `backgroundPosition` driven by `t` (§4.4).
- Vignette: radial-gradient multiply, transparent center → `--ink` 4% at the four corners.
  Static, not motion-linked.
- Zero UI chrome: no browser bars, no traffic lights, no pill/chip containers, no card fills
  distinct from `--paper`. Lane components are border-only; page paper shows through.

### 3.5 Frame-sizing rule — the Lane component

One atomic component, reused everywhere (build once, instantiate 1×/2×-stacked/2×-side-by-side):

```
lane.height = zone_height_budget_for_this_modality   (fixed per modality, §5)
lane.width  = min(1248, lane.height × source_aspect_ratio)
lane.x      = horizontally centered within the 1248 content width
border      = 3px solid (--rust | --steel per role), radius 12px
fit         = "contain" (box pre-computed to exact aspect → contain==cover; NEVER distort/crop
              real photo/video content)
```

Payoff media always claims the maximum height its zone budget affords — never smaller, never
stretched (decision #8). Exception: small reference/establishing chips (i2v's post-reframe
source-photo chip) are a fixed 200×200 square, `object-fit: cover` — the sole `cover` use in
the system, since it's an establishing reference, not the hero payoff. Waveforms have no
source aspect ratio and always span the full 1248px content width at their fixed lane height.

Eyebrow labels sit **outside and above** the frame, never overlaid on media pixels — kills the
baseline's header-bar-on-image and floating-pill-on-gradient patterns.

### 3.6 Attribution / footer

Fixed at y 952–984 on every modality, every frame:

```
[emoji 32px]  hf.co/spaces/<owner>/<name>                    [mock demo assets]
   manifest emoji, twemoji, no badge/circle bg
              Footer role, --ink-70, NEVER truncated.
              Fallback for long ids: step down 30px→26px, never ellipsize.
                                                        Footer role, --ink-45. Shown ONLY
                                                        when assets are mocked; omitted
                                                        entirely (not blank) when real.
```

No separate HF wordmark/logo in-frame — the `hf.co/` url carries attribution
(`hf_logo_url` intentionally unused, keeps "zero chrome").

### 3.7 Per-modality body-zone diagrams

Shared header/footer (y 96–328, y 928–1080) identical across all 4; only the 1248×600 body
zone differs. Accent budget = exactly 2 hues on screen in every diagram.

**t2i** — zone budget 600px total, split: PROMPT eyebrow+body (h=160 fixed) → gap32 → image
Lane (height = 600-160-32 = 408, width = 408×1536/1024 = 612, centered). Accents: rust
(PROMPT label) + steel (image frame).

**a2a** — two stacked waveform Lanes (h=160 each, gap48) + NOW PLAYING status line (progress
rule, no pill), block vertically centered in the 600px zone. Accents: rust (ORIGINAL) + steel
(ENHANCED), simultaneously present via the 100%/55%-opacity pair (decision #3).

**i2v (pre-reframe, t<1.0s)** — split rail: photo (32% content width, "PHOTO" label, rust
border) + video (68%, "VIDEO" label, steel border, already playing), both same height,
matched framing. **Post-reframe (t≥1.3s)** — video full-bleed (canvas edge-to-edge, the one
grid exception), 200×200 photo chip pinned top-left with `u3=24px` margin, footer gets a
minimal scrim strip for legibility. Accents: rust (photo chip) + steel (video), always 2.

**edit** — single wipe Lane, height = 600-56-24 = 520 (56 for instruction line, 24 gap), width
= 520×683/1024 = 347-ish (normalize `woman.jpg` 683×1024 and the 672×1024 edited output to a
common crop before wiping, or the wipe seam visibly jumps), centered. BEFORE label (rust, left
position) / AFTER label (steel, right position) sit above the single card, fixed, non-moving —
only the image content wipes underneath them. Accents: rust (BEFORE) + steel (AFTER).

## 4. Motion language

### 4.1 Named easing curves

Pure functions of progress `p ∈ [0,1]`, called from `seek(t)` via `lin(t,a,b)`
(clamp-normalize helper). No CSS transitions/animations — everything computed in JS per frame.

| name | role | cubic-bezier (devtool reference) | JS |
|---|---|---|---|
| `snap` | chrome micro-settle entrance (position only, opacity always 1); decisive width/position MORPHs (e.g. i2v reframe) | `cubic-bezier(0.16,1,0.3,1)` | `p===1?1:1-Math.pow(2,-10*p)` |
| `punch` | hero micro-emphasis: scale pop, glow blooms, ignition pulses | `cubic-bezier(0.34,1.56,0.64,1)` | back-out, `c1=1.70158,c3=c1+1; p=>1+c3*(p-1)**3+c1*(p-1)**2` |
| `wipe` | clip-path/mask reveals — the hero WIPE class only | `cubic-bezier(0.08,0.82,0.17,1)` | `p=>Math.sqrt(1-(p-1)**2)` |
| `settle` | secondary crossfades, label swaps, non-hero opacity/color changes ≤300ms | `cubic-bezier(0.65,0,0.35,1)` | `p=>p<.5?4*p**3:1-(-2*p+2)**3/2` |
| `glide` | anything tied to real elapsed time — audio playhead, video frame index, live progress fill, Ken-Burns drift. Must be linear or it reads as fake/rubber-banded | linear | `p=>p` |
| `driftLoop` | continuous idle motion with no start/end — playhead-dot pulse | periodic | `period=>(t)=>((Math.sin((t/period)*2*Math.PI-Math.PI/2)+1)/2)` |

```js
const clamp = (v,a,b)=>Math.min(b,Math.max(a,v));
const lin = (t,a,b)=>clamp((t-a)/(b-a),0,1);
const snap   = p=>p===1?1:1-Math.pow(2,-10*p);
const punch  = (()=>{const c1=1.70158,c3=c1+1;return p=>1+c3*Math.pow(p-1,3)+c1*Math.pow(p-1,2);})();
const wipe   = p=>Math.sqrt(1-Math.pow(p-1,2));
const settle = p=>p<.5?4*p*p*p:1-Math.pow(-2*p+2,3)/2;
const glide  = p=>p;
const driftLoop = (periodS)=>(tGlobal)=>((Math.sin((tGlobal/periodS)*Math.PI*2-Math.PI/2)+1)/2);
```

Retired: generic `easeIO`/`easeOut` as defaults for everything (the old poster.html pattern).
`translateY` is retired everywhere except the entrance micro-settle (§4.3) — never reused
mid-video; this is what gives the entrance its own identity instead of "everything fades/
slides the same way."

### 4.2 Transition grammar

- **WIPE** — clip-path/mask reveal of payload pixels. Curve=`wipe`. Budget: **one hero-moment
  slot per video** (may be a multi-beat choreographed sequence, e.g. edit's sweep-out/sweep-
  back/settle/echo-sweep is ONE slot told in several beats — decision #7). Never a second,
  unrelated clip-path reveal elsewhere in the same video, never used for chrome.
- **MORPH** — continuous numeric interpolation of a property already on screen (scale,
  clip-path %, color-mix, width, canvas redraw). Curve=`glide` if tied to real time/audio/
  video; `snap`/`punch` if tied to a discrete authored beat. Default class for everything that
  isn't the hero.
- **CROSSFADE** — opacity-only swap between two discrete states (label text, CTA text, dimming
  a finished card). ≤300ms, curve=`settle`. Reserved for secondary state changes so it never
  competes with the WIPE.
- **CUT** — instant, no interpolation. Used only at loop boundaries where the medium can't be
  seamless (a2a, i2v). Never mid-video.

Rule of thumb: if you're about to add a `translateY`/slide, it's only legal inside the 0-320ms
entrance window. If you're about to add a second clip-path reveal mid-video, stop — do a
CROSSFADE or MORPH instead.

### 4.3 Entrance choreography (0-320ms, all 4 modalities, per decision #2)

Opacity pinned at 1.0 for every element from t=0.000. Only a small `translateY` position
micro-settle is animated, staggered for a felt cascade:

| element | delay | duration | property | curve |
|---|---|---|---|---|
| title | 0ms | 160ms | translateY 8px→0 (opacity always 1) | `snap` |
| tagline | 40ms | 160ms | translateY 8px→0 | `snap` |
| card/lane frames + eyebrow labels | 80ms | 160ms | translateY 6px→0 | `snap` |
| now-line / progress readout (a2a only) | 120ms | 160ms | translateY 4px→0 | `snap` |
| footer | 160ms | 160ms | translateY 4px→0 | `snap` |

Window closes at t=320ms. Payoff media (image, waveforms, split layout, wipe card) is present
at full opacity and correct final position from t=0.000 with no translateY of its own except
t2i's dedicated scale micro-settle (§5.1) — media is the payoff, it does not get an entrance
effect layered on top of the causality-pulse hero moment that follows immediately after.

### 4.4 Continuous motion — no frame may be fully static

Invariant: at every t, at least one of {playhead position, video frame index, progress fill,
grain crawl, Ken-Burns scale, mm:ss counter text} has non-zero derivative.

Deterministic grain crawl (all 4 modalities, ambient texture, fixes "waveforms/canvas look
synthetic"): precomputed seeded-noise tile, baked once at setup, **not** regenerated per
frame. Position driven purely by `t` so out-of-order `seek(t)` calls reproduce identically:

```js
const offset = (t * 24) % 512; // 24px/sec, tileSize 512
el.style.backgroundPosition = `${-offset}px ${-offset*0.6}px`; // slight diagonal drift
```

| driver | active | amplitude/period | curve |
|---|---|---|---|
| grain crawl | entire duration, all 4 modalities | 24px/sec diagonal | linear (formula above) |
| Ken-Burns scale | t2i: push-in+pull-back (§5.1) · i2v: continuous 1.008→1.02 drift under real playback (§5.3) · edit: BEFORE-hold + AFTER-linger drift (§5.4) | see per-modality table | `glide` — must be linear, easing an open-ended drift reads as "settling to a stop," which is wrong |
| waveform playhead dot | a2a, both playback windows | scale 1.0→1.25→1.0, 500ms period | `driftLoop(0.5)` |
| progress fill (a2a pills) | a2a, entire playback | width tied 1:1 to real elapsed time | `glide` |
| video frame index (i2v) | entire playback | `frame = clamp(round(t*32), 0, 208)` | `glide` — the source motion IS the content, never eased |
| mm:ss / counters | a2a NOW PLAYING readout | recompute every call, `toFixed(1)` | — (changes every 30fps step by construction) |

Deleted from the motion lens's original table: typing-caret blink row, t2i gen-bar marquee row
— both were artifacts of the deleted typing/generating beats (decision #1, #12).

## 5. Per-modality timing tables + hero moments

30fps. Frame = round(t×30). `window.seek(0)` must render the full payoff state literally —
real image `src`, full waveform data, full wipe composition — never an empty container that
fills in later; this is a functional requirement of Cold-Open Split, not a preference.

### 5.1 t2i — Z-Image Turbo (prompt → image). 8.0s / 240 frames.

Source `z-image-turbo-live.png` is 1536×1024 vs 1440×1080 canvas — crop/fit must keep the
dragon+strawberry detail in frame at both 100% and 112% Ken-Burns crop.

| beat | t start–end | frame | what happens | curve |
|---|---|---|---|---|
| Frame zero | 0.000 | f0 | Full hero image (final pixels), full prompt caption (all words, no truncation), title/tagline/URL — this frame IS the thumbnail | — |
| Chrome micro-settle | 0.000–0.320 | f0–10 | title/tagline/labels/footer translateY settle per §4.3 | `snap` |
| Image micro-settle | 0.000–0.400 | f0–12 | image scale 101%→100% | `punch` |
| **HERO — causality pulse** | 0.400–0.700 | f12–21 | key prompt phrase ("tiny dragon") gets a left→right underline draw (this is the video's 1 WIPE-budget use, at decorative scale) synced with a soft glow-ring bloom on the matching image detail | underline=`wipe` (250ms), glow=`punch` (300ms) |
| Push-in | 1.200–4.600 | f36–138 | image scale 100%→112%, centered on the dragon/strawberry detail | `glide` |
| Hold | 4.600–5.600 | f138–168 | held at 112%; grain crawl only | — |
| Pull-back + URL pulse | 5.600–8.000 | f168–240 | scale 112%→100%, lands exactly on frame-0 crop at f240; URL brightness/scale pulse (NOT a wipe — budget already spent) | `glide` (scale), `settle` (URL pulse) |
| Loop | 8.000→0.000 | f240→f0 | pull-back ends exactly at frame-0 framing | **pixel-seamless** |

Causality-in-2s device: synced phrase-underline + image-detail glow, lands t≈0.7s. Payoff
appears t=0.000 (100% of runtime is proof, 0% is revelation).

### 5.2 a2a — Resemble Enhance (audio → audio). 10.2s / 306 frames. `T.playStart = 0.000`.

Real durations only: 5.2s original + 5.0s enhanced, zero padding (honesty requirement).

| beat | t start–end | frame | what happens | curve |
|---|---|---|---|---|
| Frame zero | 0.000 | f0 | Both waveforms fully drawn: ORIGINAL rust 100% opacity (active), ENHANCED steel 55% opacity (not desaturated — decision #3); title/tagline/labels/URL/footer present | — |
| Chrome micro-settle | 0.000–0.320 | f0–10 | per §4.3 | `snap` |
| Audio + playback 1 | 0.000–5.200 | f0–156 | audio starts at literal t=0; ORIGINAL playhead sweeps 0→100%, pill-1 fills, counter increments, playhead-dot pulses | `glide` (sweep/fill/counter), `driftLoop(0.5)` (dot) |
| Connecting cue | 1.200–1.800 | f36–54 | thin bracket/arrow morphs between the two card edges (causality proof within 2s) | `snap` (discrete authored beat) |
| **HERO — ignition** | 5.200–5.500 | f156–165 | card-out (ENHANCED) border punch 1.00→1.03→1.00; label color-mix desaturated→full + scale pulse (sin envelope, peaks mid-window); card-in (ORIGINAL) simultaneously crossfades opacity 1.0→0.55 | border/label=`punch`, crossfade=`settle` |
| Playback 2 | 5.200–10.200 | f156–306 | ENHANCED playhead sweeps 0→100%, pill-2 fills, counter, playhead-dot pulses | `glide`, `driftLoop(0.5)` |
| Outro CTA | 9.600–10.200 | f288–306 | label crossfades to "→ TRY IT LIVE" | `settle` |
| Loop | 10.200→0.000 | f306→f0 | hard cut to frame-0 opacity/label state; audio restarts | audio-native reset, not pixel-seamless — acceptable, reads as "replay the comparison" |

Ignition fires exactly at the real audio splice point (`t = T.playStart + 5.2`), zero drift
tolerance — the visual punch and the audible quality contrast land on the same frame. Lowest
word-budget modality (§6): audio carries the payoff, text stays out of the way.

### 5.3 i2v — Wan 2.2 (image + prompt → video). 8.0s / 240 frames.

Source video 6.53s @ 32fps = 209 frames (index 0–208), real speed, no loop-padding of content.

| beat | t start–end | frame | what happens | curve |
|---|---|---|---|---|
| Frame zero | 0.000 | f0 | Split: photo rail (32%, "PHOTO", rust border) + video rail (68%, "VIDEO", steel border, **already playing** — frame index 0), matched framing; title/tagline/prompt short-form/URL | — |
| Chrome micro-settle | 0.000–0.320 | f0–10 | per §4.3 | `snap` |
| Continuous playback | 0.000–6.530 | f0–196 | `frame = clamp(round(t×32), 0, 208)`, continuous from t=0 — the video's own clock never pauses for the reframe below | `glide` |
| Motion divergence | 0.000–0.500 | f0–15 | water sparkles, ears twitch — first unmistakable delta vs. the static photo (natural consequence of playing footage, not an authored transform) | — |
| **HERO — reframe** (decision #6, the one grid exception) | 1.000–1.300 | f30–39 | rail width/position interpolates split(32%/68%) → 200×200 fixed corner chip (top-left, `u3=24px` margin) + video expands to full-bleed (canvas edge-to-edge); layered micro-punch on the video card (scale continues from pre-hero 1.008→1.02→1.01, no reset pop); footer gets a minimal scrim strip for legibility over now-edge-to-edge video | width/position=`snap`, card punch=`punch` |
| Full-bleed playback | 1.300–6.530 | f39–196 | video continues full-bleed at real 1x speed; persistent 200×200 photo chip + labels + URL remain (always-both-visible) | `glide` |
| Hold + outro | 6.530–8.000 | f196–240 | hold last frame (index 208 pinned); corner chip persists; full prompt caption un-collapses via crossfade (spare-time detail reveal); URL brightness pulse | `settle` |
| Loop | 8.000→0.000 | f240→f0 | hard cut from full-bleed final frame back to split layout | **not pixel-seamless** (flagged — inherent to any video-output modality); softened by compositional rhyme (same photo+video pairing, just reframed) |

Causality-in-2s device: matched photo/video-first-frame framing at t=0 + visible motion
divergence by t=0.5s. Payoff appears as composition at t=0.000, as proof at t≈0.5s.

### 5.4 edit — Krea2 Identity Edit (image + instruction → image). 8.0s / 240 frames.

Normalize `woman.jpg` (683×1024) and `woman_night_market_edited.webp` (672×1024) to a common
crop before wiping, or the wipe seam visibly jumps.

| beat | t start–end | frame | what happens | curve |
|---|---|---|---|---|
| Frame zero | 0.000 | f0 | Wipe at 50%: full BEFORE (rust label, left) / full AFTER (steel label, right), both real pixels; full instruction caption; title/tagline/URL | — |
| Chrome micro-settle | 0.000–0.320 | f0–10 | per §4.3 | `snap` |
| **HERO — sweep out** | 0.000–1.000 | f0–30 | diagonal clip-path polygon wipe (leadX -20%→120%, ~8.5° slant) reveals 100% AFTER; light-sweep accent rides the edge (bell-curve opacity, peaks mid-wipe, zero at both ends); micro-punch on whole card at t≈0.5s | wipe=`wipe`, punch=`punch` |
| **HERO — sweep back** | 1.000–2.000 | f30–60 | wipe reverses, leadX 120%→-20%, full BEFORE revealed then settling — both full images now seen by t=2.0s | `wipe` |
| **HERO — settle** | 2.000–3.000 | f60–90 | wipe returns to exactly 50/50 resting composition | `wipe` |
| Identity-proof hold | 3.000–6.600 | f90–198 | held at 50/50; small loupe glides across matching facial landmarks in sync on both sides, 2–3 stops ~400ms each — proves *what stayed the same*, the modality's actual sell | `settle` per stop |
| **HERO — echo sweep** | 6.600–7.600 | f198–228 | quick out-and-back, 50%→0%→50%, 500ms each direction — rhythmic callback, no new state | `wipe` |
| Hold / outro | 7.600–8.000 | f228–240 | held exactly at 50% (== frame 0); URL brightness pulse | `settle` |
| Loop | 8.000→0.000 | f240→f0 | wipe already at 50% on both sides of the cut | **pixel-seamless** |

All five wipe beats (sweep out/back/settle/echo) are ONE hero-moment slot per decision #7, not
five independent WIPE uses. Causality-in-2s device: full sweep BEFORE→AFTER→BEFORE completes
by t=2.0s.

## 6. Word budget summary

| Modality | Persistent words (frame 0) | Peak words (any beat) | Dominant payoff channel |
|---|---|---|---|
| t2i | 25 | 25 | visual (image) |
| a2a | 11 | 13 (outro CTA) | audio (ear) |
| i2v | 16 | 32 (outro grace window) | visual (motion) |
| edit | 20 | 20 | visual (wipe gesture) |

a2a's low word count is structural — audio does the proving. Do not add explanatory captions
to "match" the other modalities; that competes with listening.

## 7. QUALITY BAR — verbatim checklist (pass/fail per rendered frame)

Kept verbatim from the quality-bar lens per the merge brief. Note on item 2/3: this spec's
fixed rust+steel palette (§3.3, decision #4) satisfies item 2's "e.g., rust+steel" clause;
this system does not use `colorFrom`/`colorTo`-derived gradients at all, so item 3's flat/grain
requirement is trivially met. Note on item 5: see decision #8 for how "frame area" is scoped
per modality.

1. [ ] Frame 1, viewed alone with no animation context, communicates: Space name, the real input, and a visible cue of the real output — a person shown only frame 1 can state what the demo does.
2. [ ] Exactly one accent-hue pair is used for the entire video (e.g., rust+steel or the Space's own colorFrom/colorTo); no third saturated hue appears anywhere except desaturated neutrals (paper/cream/ink/gray ≤10% saturation).
3. [ ] Background in every frame is a single flat tone or one deterministic seeded-grain texture — no multi-stop decorative mesh/radial gradient that isn't derived directly from the Space's declared colorFrom/colorTo.
4. [ ] No text renders below 28px actual glyph cap-height at the native 1440px-wide canvas, including timecodes, footers, and micro-labels.
5. [ ] The payoff media (generated/edited image, or output video frame) occupies ≥60% of total frame area in its reveal shot; never confined to a sub-25% thumbnail.
6. [ ] Every text block's baseline in a given frame sits on one shared grid (spacing unit declared per template, e.g. 8px); measured baseline y-values are integer multiples of that unit.
7. [ ] Each fact is stated exactly once per frame — no duplicated captions (banning e.g. a "NOW PLAYING: ORIGINAL" string when a panel is already labeled ORIGINAL and a playhead already marks position).
8. [ ] All timecodes within one video use exactly one format string throughout (e.g. always `0:05`, never mixed with `00.5 / 10.0s`, and never a malformed string like `0:005`).
9. [ ] A single corner-radius scale is declared per template (at most 2 values: one for panels/cards, one for pills) — no third ad hoc radius appears anywhere in the frame.
10. [ ] All drop shadows in a frame share one consistent recipe (offset, blur, opacity, implied light direction) — no sibling element at the same visual elevation uses a different shadow.
11. [ ] Waveforms are driven by the actual decoded peaks array and visibly change shape/amplitude per source file — never a static, generically mirrored placeholder bar pattern reused across different audio.
12. [ ] Played-vs-unplayed audio regions use one consistent opacity/color rule applied identically to both tracks (e.g. 100%→35% at the playhead) — no hard, ungoverned opacity seam.
13. [ ] Zero bounding-box collision between chrome (playhead line, progress rule, badge) and any text glyph — a line must never bisect a letterform.
14. [ ] `hf.co/spaces/<owner>/<name>` appears at least once, complete and untruncated, at ≥18px cap-height.
15. [ ] Any truncated caption/prompt ends at a word boundary with an intentional trailing ellipsis — never a mid-word cut.
16. [ ] Mocked-asset frames carry a footer disclosure ("mock demo assets" or equivalent) visible for ≥1s of screen time at ≥16px.
17. [ ] The hook element (Space name or one-line description) is the single largest type element in frame 1, at least 2× the cap-height of any secondary label present in that same frame.
18. [ ] Any header/wordmark lockup (icon + name, if used) is never the largest text element in any frame — always visually subordinate to that frame's hook or payoff.
19. [ ] A 390px-wide downscale of the hook frame and the payoff frame (`ffmpeg -vf scale=390:-1`) shows all key words legible with no anti-aliased mush — smallest legible glyph stroke ≥1.5px at that scale.
20. [ ] No more than 2 independently-drop-shadowed "floating" chip/card elements appear per frame — related chrome is grouped into one anchored composition rather than N independent free-floating cards.
21. [ ] A given semantic element (e.g. the prompt card) never teleports to a different XY anchor or a different size between adjacent frames of the same scene — position/size may animate continuously, never jump-cut.
22. [ ] The final frame reinforces the hook (title + Space id still visible/legible) so a loop cut reads as intentional, not an abrupt dead stop.
23. [ ] Each semantic text role (headline, micro-label, body/prompt copy, timecode) uses exactly one font weight+tracking value throughout the entire video — never 2+ weights for the same role across different frames.
24. [ ] Every discrete UI chip/label maintains ≥12px clear space from its own border before touching another element's bounding box.
25. [ ] Any progress/scrub bar reuses the frame's existing accent hue for its filled state (not a 3rd brand-plus-gray combination), with the track color a true neutral (≤5% saturation) if not an accent hue.

## 8. Extension notes — t2v, vqa, avatar, gallery

Same grid (§3.1), type scale (§3.2), color tokens (§3.3), texture rules (§3.4), Lane component
(§3.5), footer (§3.6), easing set and transition grammar (§4) apply unchanged. Only the
story-shape and Body Zone content differ.

| Modality | Story-shape note | Body Zone sketch |
|---|---|---|
| t2v (text→video) | No input image to anchor against — hardest case. Open with video **already moving** at frame 0 (never black/loading). Prove causality via the same prompt-phrase↔on-screen-action sync pulse as t2i's causality-pulse device (§5.1), landing under 1s, since there's no "before" image to wipe against. | PROMPT eyebrow+body above a full-height video Lane (no split needed — there's no input photo). |
| vqa (video+question→text) | Payoff is a text answer — apply "don't bury the payoff" to text too: show QUESTION and ANSWER both at frame 0, never withhold the answer for fake suspense. Spend runtime letting the video prove it by syncing an answer-phrase highlight to the exact video moment it refers to (a `settle`-class color-mix pulse on the phrase, timed to the frame it references). | Video Lane (steel border) + QUESTION/ANSWER eyebrow+body pair, ANSWER always visible from t=0. |
| avatar (portrait+audio→talking video) | Same matched-split device as i2v (static portrait rail next to talking-video's first frame), but audio starts at t=0.000 like a2a (exception to the silent rule) — mouth movement + audible speech together prove causality faster than any visual-only device. Reuse i2v's reframe hero moment mechanic verbatim, retimed to fire once speech clearly diverges from the static portrait (typically <0.5s). | Identical layout to i2v (§5.3) with audio muxed at `T.playStart=0.000`. |
| gallery (1 input→4 images) | Never reveal the 4 outputs one-by-one — that's the linear defect applied 4x. Open with all 4 already arranged in a 2×2 grid at hero scale next to a single small input chip, at frame 0. Causality proof is spatial (input placed centrally or as a corner chip, 4 variations fanned around it), not temporal — no per-image reveal sequence, ever. | 2×2 grid of image Lanes (steel border, each ≤ (1248-u3)/2 wide) + one 200×200 input chip (rust border, cover-fit, the same sole `cover` exception as i2v). |

## 9. Implementation / handoff notes

1. `window.seek(0)` must render the full payoff state literally (real `src`, full waveform
   data, full wipe composition) — not an empty container filling in at t=0.1. Functional
   requirement of Cold-Open Split, not a preference.
2. Build the shared header/footer as one partial reused by all modality bodies; implement the
   Lane component once and instantiate 1×/2×-stacked/2×-side-by-side/2×2-grid per modality — do
   not hand-roll per-template spacing.
3. Grain/vignette are single shared overlay divs, computed once at `setup()`, never per-frame.
4. The "always-both-visible" corner-chip pattern (i2v's 200×200 photo chip) is a reusable
   component, not a one-off — reuse verbatim for avatar and gallery (§8).
5. Smallest/tightest-legibility elements at 390px feed width are the URL and footer disclosure
   — verify those first in the 390px downscale test, before verifying prompt/instruction
   captions (§3.2).
6. t2i and edit achieve pixel-seamless loops by construction (end state == frame-0 state); a2a
   and i2v do not and should not be forced to — never add artificial padding or loop trickery
   to fake it, per the honesty requirement.
7. None of the four hero moments is a shared generic fade/slide — each is medium-specific
   (synced underline+glow / audio-locked ignition punch / rail-to-full-bleed reframe / wipe
   sweep sequence). Do not substitute a common transition-library default for any of them.
8. `render.py` mapping: add `"viral": "viral.html"` to `style_files`. Set `window.__T =
   {playStart: 0.0}` for a2a (and avatar) audio muxing — audio and visuals both begin at
   literal frame 0, the strongest possible statement of "the output is right there."

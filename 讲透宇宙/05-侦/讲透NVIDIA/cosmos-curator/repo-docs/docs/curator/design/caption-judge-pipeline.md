# Caption Judge Pipeline

## Goal

Build a narrow pipeline kind for judging caption changes between two metadata outputs.
The pipeline answers one question: did a candidate caption producer regress against a baseline
caption producer on the same clip window?

The pipeline does not compare non-caption metadata.

## Inputs

The pipeline takes two metadata datasets:

- `baseline`: baseline pipeline output root; metadata is read from `<baseline>/lance/v0`
- `candidate`: candidate pipeline output root; metadata is read from `<candidate>/lance/v0`
- optional `clip_limit` cap for local debugging

Each dataset is expected to use the native clip metadata schema:

- clip identity: `clip_uuid`, `video_uuid`
- media: `clip_location`
- clip timing: `start_ns`, `end_ns`, `duration_ns`
- windows: `windows[]`
- window identity: `windows[].start_ns`, `windows[].end_ns`
- captions: `windows[].captions`, keyed by caption model name
- token counts: `windows[].token_counts`, keyed by caption model name
- caption status: `windows[].caption_status`, `windows[].caption_failure_reason`

Window bounds are clip-relative nanoseconds.

## Pipeline Shape

1. Read baseline and candidate metadata as Arrow tables.
2. Project only columns required for caption judging.
3. Join clips by `clip_uuid`.
4. Explode `windows[]` on each side.
5. Join windows by `(clip_uuid, start_ns, end_ns)`.
6. Extract baseline and candidate caption text from the configured caption maps.
7. Classify rows:
   - `not_comparable`: missing window, missing caption, invalid bounds, unreadable clip media
   - `unchanged`: both captions are present and equal
   - `judge_candidate`: both captions are present and different
8. For `judge_candidate`, load the candidate-side clip media and extract the exact window MP4.
9. Send the window MP4 plus both captions to the configured judge.
10. Emit one row per judge failure, invalid response, or candidate regression, plus a compact run summary.

The judge receives the window media, not the full clip, except when the window spans the
entire clip.

## Window Media Extraction

The source video for judging is the candidate output's `clip_location`, because the judge asks
whether the candidate caption is acceptable for the media it produced.

Window extraction uses `windows[].start_ns` and `windows[].end_ns` as clip-relative time bounds:

- `start_s = start_ns / 1_000_000_000`
- `end_s = end_ns / 1_000_000_000`
- trim `clip_location` to `[start_s, end_s]`
- normalize timestamps in the extracted MP4 to start at zero

The first implementation can use ffmpeg for trim/transcode. It should cache the loaded clip
bytes per `clip_uuid` inside each actor batch so multiple windows on the same clip do not
re-read the same media.

## Judge Contract

The judge prompt is deterministic and uses neutral prompt labels: Caption A is the baseline
caption and Caption B is the candidate caption. The prompt does not include the semantic
baseline/candidate names or caption model names. It asks for one JSON object:

```json
{
  "winner": "a",
  "confidence": 0.9,
  "reason": "short explanation",
  "a_errors": ["error"],
  "b_errors": ["error"]
}
```

Valid `winner` values are `a`, `b`, and `tie`. The pipeline emits a regression issue only when
the judge returns `a`, then maps that result back to `winner: baseline` in the report. Invalid
judge responses are recorded as structured failures with the raw response truncated.

## Output

The default output is a JSON report for quick local use. A native tabular report can be added
once the row shape has settled.

The report records the inferred `caption_model_baseline` and `caption_model_candidate`
at top level and on relevant issue rows.

Issue row fields:

- `code`
- `message`
- `video_uuid`
- `clip_uuid`
- `start_ns`
- `end_ns`
- `output`
- `caption_model_baseline`
- `caption_model_candidate`
- `winner`
- `confidence`
- `reason`
- `baseline_errors`
- `candidate_errors`
- `baseline_caption`
- `candidate_caption`

Issue codes:

- `caption_window_not_comparable`
- `caption_judge_failed`
- `caption_judge_invalid_response`
- `caption_judge_prefers_baseline`

Summary fields:

- `clips_in_baseline`
- `clips_in_candidate`
- `clips_in_both`
- `windows_in_baseline`
- `windows_in_candidate`
- `windows_in_both`
- `windows_judged`
- `issues_by_code`
- `issues_by_output`
- `runtime_sec`

## Config Sketch

```yaml
schema_version: 1
kind: caption_judge
input:
  baseline: /config/output/baseline
  candidate: /config/output/candidate
output:
  report_path: /config/output/caption_judge_report.json
```

Optional fields include `judge`, `clip_limit`, and `max_workers_per_node`.
`progress` defaults to the Ray Data rich progress UI. The pipeline infers the
base caption model from each metadata side and requires exactly one
`windows[].captions` key per side.

## Execution Notes

Use Ray Data for the table path and an actor pool for the hosted judge:

- one actor owns one provider client
- one actor processes one request at a time
- multiple actors provide modest request concurrency
- media bytes are cached within a batch, not globally
- report rows are ordinary Python dicts converted to Arrow or JSON at the driver boundary

Default concurrency should be conservative: the actor pool is capped at
`min(num_windows, live_ray_nodes * max_workers_per_node)`. Users can raise
`max_workers_per_node` when endpoint rate limits are known.

## MVP

The first version should implement only the caption-judging path:

- metadata reads for both inputs
- clip/window join by `clip_uuid`, `start_ns`, and `end_ns`
- caption extraction from `windows[].captions`
- exact window MP4 extraction from candidate `clip_location`
- hosted judge over differing caption windows
- JSON report with issue rows and summary counters

After the MVP is useful, add:

- native tabular report output
- resume from partial report
- richer filters for videos, clips, windows, and caption status

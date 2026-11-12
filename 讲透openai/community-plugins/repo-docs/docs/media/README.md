# Grafana demo media

The README uses the **8×, 22.6-second** clip; the **180.767-second** walkthrough is the readable version. Both are silent H.264/yuv420p videos at 1680 × 956, 30 fps, with fast-start enabled and source metadata removed. The matching poster is the redacted full-video frame at 2:07.5.

This illustrates a local `checkout-evidence` workflow, **not the packaged plugin's end-to-end test results**. The metrics, investigation, and human approval flow are retained; only identity/UI display text is replaced. An on-screen caption makes that distinction explicit.

## Redactions and review

Opaque masks and generic labels cover the following regions. Times refer to the full-speed video; moving labels follow panel animations.

| Full-speed interval | Redacted display text |
| --- | --- |
| Throughout | Customer/project dashboard branding and browser profile/chrome labels |
| Before 0:54 | Workspace project selector |
| 0:04–0:12 and 0:21–0:46 | Terminal account, host, project, and container labels, including clipped edges |
| While visible | Internal model selector; the actual approval controls remain unobscured |

The review combines local OCR, quarter-second full-video samples, every frame of the 8× video, full-rate terminal/animation checks, and visual inspection. Both encoded outputs were fully decoded. OCR and sampling cannot prove the absence of every disclosure; this is a content review, not legal or brand clearance.

[The manifest](grafana-demo.json) records exact durations, byte counts, checksums, and review coverage. The unredacted original recording is preserved outside this repository and is not a distribution asset.

## Regenerate the fast clip

Use the **redacted full walkthrough**, never the unredacted source:

```sh
ffmpeg -nostdin -y -i docs/media/grafana-production-monitoring-demo.mp4 \
  -map 0:v:0 -vf 'setpts=(PTS-STARTPTS)/8,fps=30' -an \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -map_metadata -1 -movflags +faststart \
  docs/media/grafana-production-monitoring-demo-8x.mp4

ffmpeg -v error -xerror \
  -i docs/media/grafana-production-monitoring-demo-8x.mp4 -f null -
```

Regeneration may change bytes; recheck the output and update the manifest before committing it.

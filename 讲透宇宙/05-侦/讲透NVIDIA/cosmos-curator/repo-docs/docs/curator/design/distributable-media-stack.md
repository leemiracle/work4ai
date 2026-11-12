# Distributable Media Stack Design

## Summary

Cosmos Curator has two media policies for container images. The full and slim image build recipes are public and use the
root Pixi lock with the conda-forge LGPL media stack. The redistributable image is the NVIDIA-published binary image
path, so it uses a separate Pixi manifest and lockfile plus a custom, narrower FFmpeg build that excludes components we
cannot redistribute in the image.

This keeps the common path simple while making the compliance-driven path explicit.

## Motivation

The shared custom-media path tried to minimize drift by injecting the same FFmpeg/PyAV/OpenCV integration everywhere.
That reduced template differences, but it made the common full and slim builds pay for redistributable-image constraints:
source builds, Docker-time lockfile rewriting, and a media stack that no longer came directly from the Pixi solve. The
redistributable image still has a different codec policy, and it is not the main CI-exercised runtime. Making that policy
split explicit is easier to audit than hiding it behind a shared source-build path.

The earlier Pixi layout already used conda-forge LGPL FFmpeg for normal images. Restoring that model gives us a clearer
division of responsibility:

- Pixi owns normal runtime dependencies.
- Docker owns only image assembly for full and slim.
- Redistributable media policy is isolated in its own manifest, lockfile, and Docker path.

## Proposed Shape

### Full and Slim Images

The full and slim images share the main `pixi.toml` and `pixi.lock`.

Their media stack comes from conda-forge:

- `ffmpeg` pinned to the LGPL build variant.
- PyAV from conda-forge, so it uses the conda FFmpeg stack.
- OpenCV from conda-forge, using the headless build for image runtime environments.
- A `conda-pypi-map.json` entry maps conda OpenCV packages to the PyPI OpenCV package names, so PyPI packages such as
  PaddleOCR do not pull bundled OpenCV wheels back into the normal lock.
- Related media packages resolved normally by Pixi.

The full image still pre-installs selected Pixi environments at build time. The slim image still ships the manifest,
lockfile, Pixi, and source, then installs environments at runtime. Neither normal image needs the custom FFmpeg,
PyAV, or OpenCV source-build path.

### Redistributable Image

The redistributable image uses a separate Pixi workspace under:

```text
distributable/pixi.toml
distributable/pixi.lock
```

That manifest is generated from the main `pixi.toml` by a small script. The script preserves the shared runtime shape
but applies the redistributable media policy:

- remove conda-forge FFmpeg/OpenH264-dependent media packages;
- use PyPI PyAV/OpenCV package entries as placeholders for Docker-built wheels;
- include only image-runtime environments, excluding developer and cluster tooling;
- relock `distributable/pixi.lock`.

The generated manifest and lockfile are checked in. Regenerate both with
`pixi run -e tools python tools/update_distributable_pixi.py`. CI fails if they are stale after a main `pixi.toml`
change.

The redistributable Docker build installs from `distributable/pixi.toml` and `distributable/pixi.lock`, but copies them
into the image as the usual `pixi.toml` and `pixi.lock` so runtime commands do not need special paths.

The distributable lockfile does not capture the final custom PyAV/OpenCV wheel artifacts, because those wheels are built
inside the Docker media path against `/opt/ffmpeg`. The image build still rewrites the redistributable lockfile from the
locked PyPI wheel URLs to local `file://` wheelhouse URLs and patches the SHA256 values. This is a narrow substitution
for packages that keep the same names and versions, not a solve-time policy transform.

### Custom Media Artifacts

Redistributable builds still need a custom narrow FFmpeg in `/opt/ffmpeg`. PyAV and OpenCV wheels must be built against
that FFmpeg and installed through the redistributable image path.

The important invariant is that the redistributable image never contains `libopenh264*` or the normal conda-forge FFmpeg
stack.

## CI Checks

CI enforces the split with lint, build, and e2e-gated Slurm smoke checks:

- normal full/slim locks use the conda-forge LGPL FFmpeg build, not GPL;
- normal full/slim images use the root Pixi lock and do not run Docker-time PyAV/OpenCV wheel rewrites;
- redistributable locks do not include conda `ffmpeg` or `openh264`;
- redistributable images do not contain `libopenh264*`;
- redistributable image lockfile rewrites replace PyAV/OpenCV PyPI wheel URLs with local wheelhouse URLs;
- redistributable images run a bare Slurm smoke test that starts the container, imports PyAV/OpenCV, verifies the
  built-in `ffmpeg` and `ffprobe` are present, and checks the redistributable media policy;
- redistributable images run a second Slurm smoke test with a conda-forge FFmpeg prefix mounted over `/opt/ffmpeg:ro`
  from Lustre. That test verifies the user override path restores normal media capabilities, including H.264 decode and
  the supported transcode encoder surface;
- generated `distributable/pixi.toml` and `distributable/pixi.lock` are up to date.

A scoped pre-commit hook mirrors the generated manifest and lockfile staleness check for changes to `pixi.toml`,
`distributable/pixi.toml`, `distributable/pixi.lock`, or `tools/update_distributable_pixi.py`.

The full `slurm_end_to_end` job remains on the normal slim image because it exercises the standard media surface.
The redistributable Slurm smoke jobs are automatic with `run-e2e-tests`, manual on ordinary MRs, and scoped to cases
where the redistributable image is built. They are not merge-train gates yet because they depend on Slurm availability
and a Lustre-mounted FFmpeg override.

## Non-Goals

This design does not change pipeline behavior. It only changes how the container images source and validate their media
runtimes.

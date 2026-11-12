# Third-Party Dependencies

This directory contains external third-party repositories and libraries used by Cosmos Evaluator, along with the
`http_archive` module extension that fetches them.

## Fetched archives

These are pulled at build time by the `http_archive` extension declared in [`MODULE.bazel`](../MODULE.bazel). Each owns a
directory here holding a `BUILD` package marker, a `BUILD.<name>` overlay that exposes the relevant subset of the
upstream code as Bazel targets, and a `LICENSE` copied verbatim from the archive at the pinned commit. `Version` is the
upstream commit pinned in `MODULE.bazel`.

| Name | Source | Version | Description |
|------|--------|---------|-------------|
| **cosmos_drive_dreams_toolkits** | [nv-tlabs/Cosmos-Drive-Dreams](https://github.com/nv-tlabs/Cosmos-Drive-Dreams/tree/main/cosmos-drive-dreams-toolkits) | `908ba8f6` | Toolkits for Cosmos-Drive-Dreams, Cosmos-Transfer1, and Cosmos-Transfer2, working with RDS-HQ format data |
| **detectron2** | [facebookresearch/detectron2](https://github.com/facebookresearch/detectron2/tree/a1ce2f956a1d2212ad672e3c47d53405c2fe4312) | `a1ce2f95` | Subset of Detectron2 used by the object check — lazy/instantiate config helpers (`config/`) and the `file_io` + `registry` utilities (`utils/`) |
| **perception_models** | [facebookresearch/perception_models](https://github.com/facebookresearch/perception_models/tree/430a0121bd30e92df635bd59f724b2c52aa5bdd7) | `430a0121` | Perception Encoder (PE) vision encoder (`core/vision_encoder`: `config.py`, `pe.py`, `rope.py`) used by the CWIP model |

## Vendored archives

Unlike the entries above, these are checked into the repository directly rather than fetched by `http_archive`.

| Path | Source | Version | Description |
|------|--------|---------|-------------|
| [`ffmpeg/`](ffmpeg) | Prebuilt FFmpeg (LGPL build with NVENC + SVT-AV1 + dav1d + libvpx) | `9.0.1` (linux/amd64) | `ffmpeg-9.0.1-lgpl-nvenc-svtav1-linux-amd64.tar.gz`, exposed via the `ffmpeg_lgpl_tar` filegroup; `tar.sh` is a helper `sh_binary` for repackaging. The codec set is an allow-list (H.264 hardware-only, no HEVC at all) — `tar.sh` documents why each codec is on it |
| [`opencv/`](opencv) | Custom-built `opencv-python-headless` (`-DWITH_FFMPEG=OFF -DWITH_IPP=OFF`) | `4.13.0.92+noffmpeg.noipp` (cp313, linux/amd64) | `opencv_python_headless-4.13.0.92+noffmpeg.noipp-cp313-cp313-manylinux_2_28_x86_64.whl`, extracted into the `@opencv_python_headless` repo by the `local_wheel` extension and exposed as the `opencv_python_headless` `py_library` via `BUILD.opencv`; `build_wheel.sh` rebuilds it and replaces opencv-python's catch-all `LICENSE-3RD-PARTY.txt` with one that `curate_third_party_licenses.py` derives from the code the build contains. Strips the bundled FFmpeg from `cv2` (keeps all image ops; `VideoCapture`/`VideoWriter` lose the FFmpeg backend — callers use the vendored ffmpeg binary instead) and omits Intel IPP, whose license is not open source (image ops fall back to OpenCV's own SIMD code) |

## Python metadata (`.dist-info`)

A vendored Python library is only attributable if it reaches the runfiles tree — and therefore an image layer — with a
readable `.dist-info`. That directory is what `importlib.metadata` resolves and what an SBOM scanner reads out of a
shipped image, so a library without one runs in production while being invisible to attribution tooling.

A local wheel already ships its own. A source archive does not, so the `dist_info_*` attributes on its
`http_archive.archive(...)` tag synthesize one: `METADATA` naming the distribution, its version, and its license
expression, plus the upstream license text under `licenses/`. The version is the upstream release with the pinned commit
as a PEP 440 local segment (`0.6+a1ce2f95`), which says both what the code is and exactly which revision shipped.

Synthesizing the metadata is not enough on its own — a Bazel target has to carry it, or it never leaves the external
repo. Each overlay therefore declares a `dist_info` filegroup and every `py_library` in that overlay lists it in `data`.

[`tests/vendored_python_test.py`](tests/vendored_python_test.py) enforces all of this. It reads the declarations back
out of `MODULE.bazel` (via the `//:vendored_python_facts` genrule) and checks that each repo's metadata exists where the
declaration says, agrees with it on name and version, states a license, ships license text, and is carried by every
`py_library` in the overlay. A repo added without metadata fails the test with a message naming what to add.

## `http_archive.bzl`

Module extension wrapping Bazel's stock `http_archive` repository rule with three extra capabilities:

* `netrc` is resolved at fetch time, expanding `~` to the user's home directory. Needed for archives whose download URL
  requires netrc-based auth from a credentials file under `$HOME` (e.g. private GitLab archives).
* `patches` fixes up the extracted tree in place.
* `dist_info_*` synthesizes the `.dist-info` described above.

A module that depends on this one can `use_extension("@cosmos_eval//third_party:http_archive.bzl", "http_archive")`
and contribute its own `http_archive.archive(...)` tags; bzlmod merges all tags into a single extension run, so a
dependent module adds archives without forking this one.

## Conventions

1. Add an `http_archive.archive(...)` entry under the `http_archive` extension in [`MODULE.bazel`](../MODULE.bazel).
   * Set [`strip_prefix`](https://bazel.build/rules/lib/repo/http#http_archive-strip_prefix) to the deepest directory in
     the upstream archive that contains all the code we need (so we only pull the minimum subset).
   * Set [`add_prefix`](https://bazel.build/rules/lib/repo/http#http_archive-add_prefix) to
     `third_party/<repo_name>/path/to/deepest/directory`. If `<repo_name>` is redundant with the name of a root-level
     subdirectory in the upstream archive (e.g. `detectron2/detectron2`), drop it from `add_prefix`.
   * Set `dist_info_name`, `dist_info_version`, `dist_info_license`, and `dist_info_license_files`, plus `dist_info_root`
     matching the `add_prefix` directory the code lands in.
2. Create a `third_party/<repo_name>/` directory with a `BUILD` package marker that `exports_files` the overlay and the
   license text, a `BUILD.<repo_name>` overlay exposing the third-party code as Bazel targets, and a `LICENSE` copied
   verbatim from the archive at the pinned commit.
3. In the overlay, declare a `dist_info` filegroup globbing `*.dist-info/**` and list it in the `data` attribute of
   every `py_library`.
4. Set the [`imports`](https://bazel.build/reference/be/python#py_library.imports) attribute on `py_library` targets so
   internal `import` statements inside the third-party code resolve correctly.
5. Add the new repo's `:dist_info` and its overlay to the `data` attribute of
   [`tests/BUILD`](tests/BUILD)'s `vendored_python_test`, so it is audited.

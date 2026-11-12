# Third Party Notices

This is a NVIDIA fork of llama.cpp (https://github.com/ggml-org/llama.cpp) that adds CUDA stream query APIs needed for CiG (CUDA in Graphics) integration. The fork is distributed under the MIT license inherited from upstream.

This file enumerates third-party software whose source is included in or vendored by this repository, along with the location of each component's license file.

## Components vendored or bundled

| Component | Location | License | License location |
|---|---|---|---|
| llama.cpp + ggml (upstream) | `./`, `./ggml/` | MIT | `LICENSE` |
| nlohmann/json | `./vendor/nlohmann/json.hpp` | MIT | `licenses/LICENSE-jsonhpp` (also inline in `vendor/nlohmann/json.hpp`) |
| cpp-httplib | `./vendor/cpp-httplib/` | MIT | `vendor/cpp-httplib/LICENSE` |
| miniaudio | `./vendor/miniaudio/miniaudio.h` | Public Domain or MIT-0 (dual; user's choice) | inline at end of `vendor/miniaudio/miniaudio.h` |
| sheredom subprocess.h | `./vendor/sheredom/subprocess.h` | Unlicense (public-domain dedication; see https://unlicense.org/) | inline header in `vendor/sheredom/subprocess.h` |
| stb_image | `./vendor/stb/stb_image.h` | Public Domain or MIT (dual; user's choice) | inline at end of `vendor/stb/stb_image.h` |
| GGUF Python package | `./gguf-py/` | MIT | `gguf-py/LICENSE` |

## NVIDIA modifications

NVIDIA-modified files added CUDA stream query APIs (`ggml_backend_cuda_get_streams`, `llama_get_cuda_streams`) needed for CiG integration. Modified files carry SPDX headers identifying both the upstream copyright (The ggml authors) and NVIDIA's modification copyright (NVIDIA CORPORATION & AFFILIATES), under the MIT license.

The NVIDIA modification commit on this fork is `c9c0a19352fb063731a86b4740f3a58fc86394c9`.

## Upstream provenance

This fork was created from upstream llama.cpp at commit `c3c15053925746c74fc2aaf6b864bd66665393c4`. The fork main branch HEAD is `2917fd66c4edaee80a1af6bb84cb4bea81fb3c73`.

Upstream project: https://github.com/ggml-org/llama.cpp
Upstream license: https://github.com/ggml-org/llama.cpp/blob/master/LICENSE

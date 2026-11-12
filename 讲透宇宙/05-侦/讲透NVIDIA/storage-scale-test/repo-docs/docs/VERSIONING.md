<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Versions

Releases are annotated Git tags named `vMAJOR.MINOR.PATCH`, such as `v1.2.3`.
Changes between releases are in [CHANGELOG.md](../CHANGELOG.md).

## Reading a version

| Version | Meaning |
| --- | --- |
| `v1.2.3` | Exactly the `v1.2.3` release. |
| `v1.2.3-4-g0123456789ab` | Four commits after `v1.2.3`, at commit `0123456789ab`. |
| `untagged-42-g0123456789ab` | Commit `0123456789ab`; no release tag is in its history. |
| `shallow-g0123456789ab` | A shallow clone whose commit has no release tag. |
| `unknown` | Neither Git metadata nor a `VERSION` file was found. |

A `-modified` suffix means the source differs from that commit or release.
Ignored files such as `env.sh`, `results/`, and downloaded binaries don't
count. Requires Git 2.15 or newer.

Deployment tarballs and release source archives have no Git metadata; they
carry a `VERSION` file and a `SOURCE_SHA256` file list, which
`sha256sum -c SOURCE_SHA256` checks. `env.sh`, credentials, and benchmark
binaries are not listed, so adding or replacing them doesn't count.

User-facing commands accept `--version`; launcher and reporter `--version` and
`--help` work before `env.sh` or reporting dependencies are set up. A built
`s3test` binary also reports its version.

## Results and reports

Each result file gets a `<name>.out.project-version` file recording the version
that ran it, and each run log starts with the version. A resumed run keeps the
versions of results that already succeeded.

Reports list the versions that produced their results and the reporter's own:

```text
Produced by storage-scale-test: v1.2.3, v1.3.0
Reported by storage-scale-test: v1.4.0
```

`unknown` covers results recorded before versioning.

## Releasing

1. Move the `Unreleased` notes in `CHANGELOG.md` under a new
   `## [1.2.3] - YYYY-MM-DD` heading and merge that to `main`.
2. Tag the merged commit and push the tag:

   ```bash
   git tag -a v1.2.3 -m v1.2.3
   git push origin v1.2.3
   ```

The release workflow runs the source checks, builds and verifies
`storage-scale-test-v1.2.3-source.tar.gz` and its `.sha256`, and publishes a
GitHub release with the changelog section as its notes. It refuses tags that
are not on `main` or have no changelog section, and can be rerun safely.

To build and check an archive locally:

```bash
python3 utils/build_source_release.py --tag v1.2.3 --smoke
```

GitHub's automatic "Source code" downloads report `unknown`; use the attached
archive. Anyone who can push a `v*` tag can start a release, so restrict tag
creation with a repository ruleset.

# Releasing relore

Like transformers-mlinter, `vX.Y-release` branch pushes build and validate distributions;
`vX.Y.Z` (or `vX.Y.ZrcN`) tags also publish them to PyPI through trusted publishing.
The workflow runs the existing CI on Python 3.10 and 3.13, including Postgres parity,
then builds an sdist and wheel, checks metadata, and smoke-tests an installed wheel.
`python -m build` builds the wheel from the sdist, exercising both artifacts.

## One-time setup

Create a GitHub environment named `pypi-release` in `huggingface/relore`, preferably
with required reviewers and deployment rules allowing release tags. Configure this
[PyPI trusted publisher](https://docs.pypi.org/trusted-publishers/adding-a-publisher/):

| Field | Value |
| --- | --- |
| PyPI project | `relore` |
| GitHub owner | `huggingface` |
| Repository | `relore` |
| Workflow filename | `release.yml` |
| Environment | `pypi-release` |

For the first upload, if the project does not exist, create a pending publisher in
[account publishing settings](https://pypi.org/manage/account/publishing/).
If it already exists, its owner must configure the publisher. No PyPI token secret
is needed. These account settings are separate from the repository files.

## Prepare and validate

Start from a clean, up-to-date `main`. `relore/__init__.py` owns `__version__`;
setuptools reads it dynamically. Keep that single source.

For a new client-visible change, bump the patch and update the status examples in
`docs/cli.md` and `docs/how-search-works.md` in the same commit. Coordinate deployment
of that exact version: the client and daemon reject different versions. Packaging-only
changes need no compatibility bump if that version has never been uploaded to PyPI.
Never reuse an uploaded version.

Move the notes under `[Unreleased]` in `CHANGELOG.md` into `## [X.Y.Z] - YYYY-MM-DD`
and retain an empty `[Unreleased]` heading for future changes. For the first PyPI
release, summarize the existing client and daemon capabilities there too.

```bash
make install
make check
# Include Postgres locally when available; release CI requires both dialects.
# RELORE_TEST_POSTGRES_URL=postgresql://postgres:test@localhost:55432/relore_test make test
.venv/bin/python -m pip install --upgrade build twine
make build-release PYTHON=.venv/bin/python
.venv/bin/python -m twine check --strict dist/*
```

`build-release` removes old `build/`, `dist/`, and `*.egg-info` before building.
The workflow installs the wheel in a fresh environment outside the checkout,
checks that the base client has no server/parser dependencies, then installs extras
and exercises `relored`. Distributions are uploaded as the `python-dist` artifact.

## Release branch and tag

Land the preparation on `main`, then create the minor-line release branch:

```bash
git switch main
git pull --ff-only
git switch -c vX.Y-release
git push -u origin vX.Y-release
```

For a later patch, switch to the existing `vX.Y-release` branch and fast-forward it
with `git merge --ff-only main`, then push it. Wait for the Release workflow to pass.
Coordinate the daemon rollout using [operations.md](operations.md) and the existing
image workflow; the PyPI workflow does not deploy the daemon.

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

The tag must match `__version__` and have a dated changelog entry. Approve the
`pypi-release` environment when prompted. The publish job downloads the validated
artifacts from the same run and uploads them to PyPI without rebuilding.

Verify in a fresh environment against a daemon running the same version:

```bash
python -m pip install "relore==X.Y.Z"
relore --version
relore status --repo owner/name
```

After the first successful publication, update the Git install commands in
`docs/cli.md` and `docs/operations.md` to use PyPI (`pip install relore` for the client,
`pip install "relore[postgres]"` for the daemon). Keep `[Unreleased]` open; do not automatically bump the
development version after publishing. Unlike mlinter, relore's version is a wire
compatibility contract, so the next bump belongs with the next change and deployment.

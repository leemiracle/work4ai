`ci.yml` runs exactly what `make check` runs locally — ruff (format + lint) and pytest —
on the supported-Python floor and the newest release. There is deliberately no separate
type-check job: linting is ruff, full stop (see `AGENTS.md`).

`release.yml` reuses those checks, builds and validates the wheel and sdist on
`v*-release` branch pushes, and publishes `v*` tags through the `pypi-release`
environment. Only the publish job can request a PyPI OIDC token. See
[`docs/release.md`](../../docs/release.md) for setup and the release procedure.

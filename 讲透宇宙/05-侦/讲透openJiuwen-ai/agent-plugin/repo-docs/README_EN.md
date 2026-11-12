# JiuwenSwarm Agent Plugin (English)

Official plugin collection repository for **JiuwenSwarm** — the content source for
Hub marketplace assets of type `agent-plugin`. Each plugin package bundles
capability extensions for agents: **skills** (guidance), **tools** (execution) and
**rails** (lifecycle hooks).

## What's inside

| Directory | Purpose |
| --- | --- |
| `plugins/` | Plugin packages (flat, one package per directory; contents ship 1:1 to users) |
| `templates/plugin-template/` | Scaffold template consumed by `scripts/init.py` |
| `scripts/` | Toolchain: `init` / `validate` (L0/L1/L2) / `catalog` / `build` / `publish` / `sync_builtin` |
| `catalog/catalog.json` | Generated catalog (lockfile-style, do not edit by hand) |
| `docs/` | Plugin spec, publishing guide, repo design docs |
| `tests/` | Toolchain unit tests + per-plugin behavior tests (not shipped) |

## Quick start

```bash
python scripts/init.py my-plugin --skill usage-guide --tool counter
# fill manifest.json / README.md / components (remove every [TODO]), then:
python scripts/validate.py --only my-plugin
python scripts/catalog.py
```

See [README.md](./README.md) (Chinese) for the full guide,
[docs/plugin-spec.md](./docs/plugin-spec.md) for the package specification.

## License

[Apache-2.0](./LICENSE) © Huawei Technologies Co., Ltd.

# funes-integrations

The agent integrations Hugging Face maintains for [funes](https://github.com/huggingface/funes) —
`claude`, `codex`, `hermes` and `pi` — and the catalog `funes add <id>` installs them from.
Integrations maintained by their authors live wherever their authors put them;
[COMMUNITY.md](COMMUNITY.md) is where they are listed.

## Layout

One directory per integration, each a bundle as funes's
[integration contract](https://github.com/huggingface/funes/blob/main/docs/add.md#the-integration-contract)
describes it: a `manifest.json`, a `setup` executable, whatever the integration needs beside them,
and its own tests under `test/`. What each one installs into its agent, which of its events it
hooks, and what it needs on the box is in its README; what they share is below.

## How the bundles automate

Each bundle gives its agent the funes read tools — `funes mcp` registered as an MCP server, or
fronted by the extension where the agent has no MCP client — and drives one script of its own,
`funes-index.sh`, in two modes. Per turn, it converts the session that just changed into funes's
spool and runs `funes index --harness <id>`, then converts any other session changed since it last
ran, so a session whose own hook never fired — untrusted, timed out, a host that died mid-turn — is
caught at the next turn; the run is time-boxed, so a backlog fills in a bounded step per turn. At
the session boundaries, as `funes-index.sh --publish` and only with a memory bound, it converts,
indexes — waiting out a per-turn run's lock — and pushes; it runs at the session's end and again at
the next start, catching up whatever a missed end left behind. The conversion is the bundle's own
converter: a script for Claude Code and Codex, the extension or plugin itself for pi and Hermes. The
work runs detached, so a hook returns in well under a second and never blocks the turn or trips a
timeout. The memory rides in a file beside the scripts, so every hooks file is static.

| Bundle | Per turn | Publish, with a memory bound |
| --- | --- | --- |
| `claude` | `Stop`, `SubagentStop` | `SessionEnd`, `SessionStart` |
| `codex` | `Stop` | `SessionEnd`, `SessionStart` |
| `hermes` | `post_llm_call` | `on_session_finalize`, `on_session_start` |
| `pi` | `turn_end` | `session_shutdown`, and `session_start` when the process is fresh |

What funes guarantees around these — local-first indexing, one writer at a time, the secrets gate,
the wrong-memory guard — is in funes's
[automation docs](https://github.com/huggingface/funes/blob/main/docs/automation.md).

## Developing

A working copy installs into funes straight from the checkout:

```sh
funes add pi --from ./pi
```

funes confirms at the terminal before running files it did not publish — once, until they change.
Each bundle's tests run without a funes binary, against fakes:

```sh
sh pi/test/run.sh
```

## Releasing

A release is an integration's directory packed as `<id>.tar.gz`, published under `<id>/<version>/`
in the `huggingface/funes-integrations` bucket with a `SHA256SUMS` beside it, and listed in the
bucket's `catalog.json`. Versions are the integration's own — `version` in its manifest,
`MAJOR.MINOR.PATCH` — independent of funes's, and a published version is never replaced.

1. Bump `version` in `<id>/manifest.json` and merge.
2. Tag `<id>-v<version>` — `pi-v1.0.1` — and push the tag, or run the Release workflow by hand
   with the id and version.

The workflow checks the manifest against the tag, runs the bundle's tests, packs and publishes the
archive, and adds the release to the catalog. It needs `HF_FUNES_INTEGRATIONS_RELEASE_TOKEN`: a token
that can write that bucket, and nothing else. Releases run one at a time, since the catalog is
read, amended and written back.

### The catalog

`catalog.json`, `catalog_version` 1:

```json
{
  "catalog_version": 1,
  "integrations": {
    "pi": {
      "repo": "huggingface/funes-integrations",
      "releases": [
        {
          "version": "1.0.0",
          "contract_version": 1,
          "url": "hf://buckets/huggingface/funes-integrations/pi/1.0.0/pi.tar.gz",
          "sha256": "…"
        }
      ]
    }
  }
}
```

For the id it was asked for, funes takes the newest release whose `contract_version` is the one it
speaks, fetches the archive at `url` with the `SHA256SUMS` beside it, and refuses it unless its
digest is `sha256` and its manifest declares `version`. Fields funes does not know are ignored.

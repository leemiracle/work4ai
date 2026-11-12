# Community integrations

Integrations for [funes](https://github.com/huggingface/funes) that their authors maintain and
publish themselves. Listing here is how they are found, from funes's documentation, and nothing
more: it adds no `funes add` alias, funes does not vouch for what is listed, and Hugging Face has
not reviewed the code. Each row is its author's own declaration; installation and support are
theirs.

Anything that talks to funes belongs here — a managed integration bundle (`funes add <id> --from …`),
a native plugin for a client, a direct CLI or MCP consumer, a producer that writes
[funes's turns format](https://github.com/huggingface/funes/blob/main/docs/funes-jsonl.md). None
of it requires the managed installation contract. Several implementations for one harness may be
listed; the publisher and the integration's name tell them apart.

## Maintained by Hugging Face

Released from this repository and installed by name, `funes add <id>`.

| Integration | Harness | What it does |
| --- | --- | --- |
| [`claude`](claude/) | Claude Code | read tools, per-turn indexing, session-boundary publish |
| [`codex`](codex/) | Codex | read tools, per-turn indexing, session-boundary publish |
| [`hermes`](hermes/) | Hermes | read tools, per-turn indexing (beta), session-boundary publish |
| [`pi`](pi/) | pi | read tools, per-turn indexing, session-boundary publish |

## Community

| Integration | Publisher | Harness or client | What it does | funes interfaces | Source | Install and support |
| --- | --- | --- | --- | --- | --- | --- |
| _none yet_ | | | | | | |

## Listing yours

Open a pull request that adds one row to the table above, and nothing else. A row gives:

- the integration's name, and you or your organisation as its publisher;
- the harness or client it targets, and what it does in a few words;
- the funes interfaces it uses — recall, indexing, publishing, MCP, the turns format — as you
  declare them;
- links you own: the source, installation and compatibility notes, and where to get support.

Releases, digests and detailed compatibility claims belong in your own release notes and
documentation, so a new release needs no change here.

Review checks that the row is about funes, attributable to a publisher, and that its links
resolve. Nothing in a pull request is installed or executed, and a merged row is not an
endorsement.

## Keeping the list right

Update your row by pull request as your integration moves. A row whose links are dead, whose
integration is abandoned, or which misleads about what it does can be marked as such or removed:
open an issue naming the row, or a pull request. The publisher is asked first when they can be
reached.

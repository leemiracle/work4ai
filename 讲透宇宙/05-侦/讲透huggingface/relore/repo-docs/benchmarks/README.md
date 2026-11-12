# benchmarks

Four things are measured in this repository, and they answer different questions. Reaching
for the wrong one is how a session spends an evening proving something nobody asked.

| | what it answers | needs | in `make check`? |
|---|---|---|---|
| `huggingface-*.jsonl` + `relored mine\|judge\|bench` | **retrieval**: given a query, is the answering thread on the page? | an indexed database | no |
| `fieldrun/` | **flow**: what does an agent actually do with that page? | a database, a model, network | no |
| `probes/page_cost.py` | **page cost**: what does one rendered page cost, and how much of it is itself repeated? | an indexed database | no |
| `probes/api_latency.py` | **latency**: how long does the deployment take, verb by verb — and what do the web UI's own buttons cost? | a deployment | no |

None of them run in CI. Three need a database, two need the network, and one costs money.
They are measurements you take deliberately, before and after a change to what a verb puts
on a page.

## Section 10: retrieval

The frozen evaluation sets and the runner behind build plan §10 — `relore` scored against
GitHub search and against the agent's own `grep`, on `failure`, `rationale` and `precedent`
slices. `benchmarks/huggingface-transformers.jsonl` and `benchmarks/huggingface-bot-reviews.jsonl`
are **frozen**: `judge` refuses to add a label to either, and growing the ground truth means
a new file. See `relored bench --help`.

Two rules that live in the runner rather than in whoever reads the table: never compare
across backends, and restrict every baseline to the corpus window.

## `fieldrun/`: flow

Drives a tool-calling model on Hugging Face Inference Providers through real questions, with
the `relore` CLI in one arm and the `gh` CLI in the other, and records every call. Derives
`time_to_evidence`, `tool_share_of_prompt`, `tool_chars_median`, `repeat_share`, `rerolls`
and `cited_unseen`. See `fieldrun/README.md` — especially the part about not quoting totals.

## `probes/page_cost.py`: what a page costs

The static half of `fieldrun`'s `repeat_share`, and the cheaper one: no model, no network,
one second. It renders real threads out of an index and reports bytes, approximate tokens,
and **how much of each page the page has already said**.

```bash
python benchmarks/probes/page_cost.py --url "$RELORE_DATABASE_URL" \
    --repo huggingface/transformers --biggest 5
```

This is the measure that found relore#71: a thread page reprinted `owner/repo#N pr`, the
thread's title and a 76-character URL under every comment — three constants the head line
already carried — and on five production threads that was **24–33% of the whole page**. No
token total showed it; the repetition did. On `#46766`, before and after:

```
pre-fix :  6347 B  repeat=0.193  const=558 B  ['huggingface/transformers#46766', …]
post-fix:  4775 B  repeat=0.000  const=128 B  ['[authoritative]']
```

Both of its thresholds were wrong on the first draft and that same page corrected them —
the reasoning is in `echo()`, because a probe that silently under-reports is worse than none.

## `probes/api_latency.py`: what the deployment costs

```bash
python benchmarks/probes/api_latency.py --base https://relore.example.org \
    --repo huggingface/transformers --thread 46419
```

Times each verb against a live deployment, and separates the **connection baseline** from
what the verb costs — against a VPN-internal deployment, DNS + TCP + TLS is most of a fast
call and attributing it to the verb makes every verb look slow.

It also times the web UI's **own sample buttons**, read out of `relore/api/ui.py` rather
than retyped, because that strip is a latency surface and it is where a person reported the
product as slow. Measured against production before relore#71:

```
connection baseline (GET /healthz, best of 3): 0.11s
ui sample  why   src/transformers/masking_utils.py:1          4.03s
ui sample  why   …/modeling_rope_utils.py:180                 1.40s
ui sample  why   …/models/llama/modeling_llama.py:1           5.22s
ui sample  search  (all four)                            0.16-0.25s
verb       thread / --outline / --full                   0.14-0.17s
```

Two of the three `why` samples point at line 1 of a source file, where the origin pass was
pickaxing the licence header: five full `git log -S` walks for an answer that was empty.

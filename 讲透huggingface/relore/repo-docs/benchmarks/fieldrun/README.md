# fieldrun — drive a real model through a real question, and measure the flow

Section 10 scores **retrieval**: given a query, is the answering thread on the page. That
number cannot see the thing that actually costs a session, which is what an agent *does*
with the page — how many calls it makes, how much of its context the tool results occupy,
and how much of that was the same text twice.

Three builds' worth of exactly that was measured by hand (`relore/docs/gh-vs-relore-2026-09-14.md`
§§3d–3f in the playbooks repo). This is that method as a script, so a build can be measured
in a minute instead of an evening, and so two builds are measured the same way.

## Run it

```bash
export HF_TOKEN=hf_...                     # or just `huggingface-cli login`
export RELORE_REPO=huggingface/transformers

python benchmarks/fieldrun/run.py --dry-run                       # tools and tasks, no model
python benchmarks/fieldrun/run.py --model zai-org/GLM-4.7 --arm relore --arm github \
       --repeat 3 --out runs/
```

The model is served by **Hugging Face Inference Providers** through the OpenAI-compatible
router, so any tool-calling model there is a target: `--model` takes the repo id
(`zai-org/GLM-4.7`, `moonshotai/Kimi-K2.7-Code`, `deepseek-ai/DeepSeek-V3.2`, …) and
`--provider` pins one of that model's providers when it matters which one answered.

The `relore` client on `PATH` must be the same version as the deployed daemon — the two
refuse to talk across a difference (`relore/wire.py`), and a run whose every call came back
`client 0.3.16 is newer than this daemon` would be recorded as the model asking bad
questions.

## What it measures

Everything comes from one trace per run: every request's `usage` as the router reported it,
and every tool call's argv, exit code, wall time and output.

**Efficiency** — `calls`, `turns`, `prompt_tokens_billed`, and **`time_to_evidence`**: the
index of the first tool call whose output contains the thread that answers the question. A
run that reaches the answer at call 3 and spends nine more confirming it is a different
failure from one that never reaches it, and a total hides both.

**Brevity** — `tool_chars_median` / `_mean` / `_max`, and `tool_share_of_prompt`: how much
of the billed prompt is tool output. On the run that produced relore#70 that share was
**58%**, which is what made `thread` the thing to fix rather than `search`.

**Repetition** — `repeat_share`, the fraction of tool-output lines this run had already
been shown *verbatim* in an earlier result, and `rerolls`, the same argv asked twice. This
is the pair a token count cannot give you: six `--focus` rolls over one thread returning
overlapping samples (relore#70), or a thread page that reprints its own title and number on
every comment.

**Answered** — the final answer must cite the thread the frozen evaluation set judged as
the answer. Deliberately shallow, and the report prints every answer next to its verdict so
a reader can overrule it; scoring prose is §10's job and it has a judge for it. What must
not happen is a cheap wrong run scoring as a win.

## The arms

| arm | tool | why |
|---|---|---|
| `relore` | the `relore` CLI, **piped** | the piped form is the agent-facing contract (`docs/cli.md`); a caveat that only renders at a terminal is one this harness will show you the agent never got |
| `github` | the `gh` CLI, read-only | the control an agent otherwise reaches for, and §10.2's baseline |

`--checkout PATH` adds a `grep` tool to either arm — the harder control (§10.2), and the
one an agent with the repo open actually has.

Both arms get the same system prompt, the same task text and the same budget. Only the tool
list differs.

## Reading a report

**Read the per-call columns, not the totals.** Across three measured builds the per-call
numbers moved as predicted while run *totals* spanned **56% on agent trajectory alone** —
same build, same question, a different path through it (§3f). `prompt_tokens_billed` is
reported because it is what the run cost, not because it attributes anything to a build.
`tool_chars_median`, `repeat_share` and `time_to_evidence` are the measures that held up.
That is what `--repeat` is for: it runs each task N times and the table prints the spread,
so a single number is never the finding.

Write down what you expect before you look (§3f). A build that hit its per-call target and
missed its total prediction is a result about trajectory variance, not about the build —
and that only reads as a result if the prediction was written first.

## The tasks

`tasks.jsonl` — six questions over `huggingface/transformers`, each phrased the way somebody
would actually ask it and each carrying the thread number the **frozen** §10 evaluation set
judged as its answer (`benchmarks/huggingface-transformers.jsonl`). Two `failure`, three
`rationale`, one `precedent`, which are §6's query kinds.

They are questions, never thread numbers: a task that names the thread measures nothing.
`rationale:masking-layer-types` is the hard one on purpose — `transformers#37866` has 70
comments and a ten-comment page, and it is the thread the six-`--focus` loop in relore#70
was measured on.

Adding a task means adding its answer to the frozen set first, or saying in the row why the
golden is defensible without one. A golden invented to fit a run is how a benchmark stops
measuring anything.

## What it is not

It calls a hosted model over the network and costs money, so it is **not** part of
`make check` and never will be. It is a measurement you take deliberately, before and after
a change to what `thread`, `search` or `why` put on a page.

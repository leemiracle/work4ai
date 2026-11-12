# tokbench

> [!IMPORTANT]  
> The tokbench repository was heavily coded by agentic means to help us compare the performance of different
> tokenization engines. We're very welcoming of any patches to help improve it going further.
> 
> We're especially welcoming of any tips to improve performance of any engine evaluated within that framework
> for maximum fairness. Thank you!


A fair benchmark of tokenizer implementations. One folder per engine, one
timing loop per direction, and an id-verification gate so a number is never
published for an engine that computed something different.

```
core/          the measurement contract and the timing loops
driver/        the binary: runs the matrix, verifies, writes JSON
binsize/       a minimal program linking one engine, to weigh it
engines/<name> one adapter per engine
hf-jobs/       reproducible cloud runs on Hugging Face Jobs
dashboard.html single-file dashboard; drop the JSON onto it
```

## Why another benchmark

Most comparisons time different functions, on different vocabularies, with load
folded into encode, at different thread counts, without checking the two
produced the same ids.

- **Same work, verified.** Ids are hashed (FNV-1a) against the reference. A
  mismatch is marked `differ` and never ranked.
- **Same clock, in-process.** One `Engine::encode`, one `Instant`.
- **Load is not encode.** Vocabulary and automaton construction happen before
  the timer, reported as `load_ms`.
- **No timed pass re-encodes text.** See below.
- **One thread by default**, and every scaling curve says whose threads.
- **Extra work is disclosed.** An engine that also computes byte offsets keeps
  that cost, and the report says so.

## The corpus is the experiment

Throughput is a property of the tokenizer **and the text**. Fast BPE engines
cache pretokens, so a number largely reports how often the input repeats.
`tokbench measure recurrence` controls exactly that: it resamples a corpus's
own vocabulary into synthetic text at a chosen pretoken recurrence rate,
holding token density constant (`tok/kB` is printed as the audit) so nothing
but repetition varies. gpt2, one thread, ids verified in every cell:

| MB/s | 2.5× | 4.1× | 8.0× | 16.1× | 64.2× | 264× | gain |
|---|---:|---:|---:|---:|---:|---:|---:|
| gigatoken | 161 | 233 | 378 | 557 | 697 | 764 | **4.7×** |
| pipeline | 128 | 163 | 249 | 416 | 539 | 544 | 4.3× |
| tokie | 79 | 106 | 145 | 248 | 296 | 292 | 3.7× |
| pipeline-no-cache | 88 | 89 | 93 | 100 | 116 | 121 | 1.4× |
| kitoken | 28 | 27 | 28 | 27 | 31 | 32 | 1.1× |
| tiktoken | 18 | 18 | 17 | 19 | 20 | 19 | 1.1× |

Engines with a pretoken cache turn repetition into throughput; engines without
one are flat, which is the control. So a headline number is mostly a statement
about where its corpus sits on this curve — and **real English sits at 8.3×,
real Chinese at 1.31×**. That is the whole reason the corpora are mixed: at its
true operating point gigatoken leads `pipeline` by 1.26× on English and *loses*
to it on Chinese, 90 against 112. Not a weakness in its merge loop — Chinese
never supplies the repetition its cache exists to exploit.

Two more consequences. Timed slices are disjoint, because warming on the chunks
the reps re-encode once overstated gigatoken by 256×. And ablations are
heap-verified: a `-no-cache` row that does not hold less live heap than its twin
is not an ablation, whatever it measured.

Corpora are public at
[huggingface/tokbench-corpora](https://huggingface.co/datasets/huggingface/tokbench-corpora)
— parquet plus the byte-identical `.txt` the driver chunks, so a config name
there is a `--corpus` here. `make fixtures` pulls them, `CORPORA_REVISION=<sha>`
pins them. `code-mixed` and `agentic-traces` are not redistributable and stay
internal.

```python
load_dataset("huggingface/tokbench-corpora", "japanese")
```

## Measuring

`tokbench` runs the full matrix; `tokbench measure <family>` runs one.
`--engine`, `--model` and `--corpus` are repeatable, omit one to sweep it.

```console
$ tokbench measure encode --engine pipeline --compare-to hf-tokenizers \
    --model gpt2 --model llama-3 --corpus english --corpus chinese --corpus code

model         corpora  median MB/s  median ns/B           vs hf-tokenizers
-------  ------------  -----------  -----------  -------------------------
gpt2     3/3 measured        231.4         4.12   ×35.74 on 3/3 comparable
llama-3  3/3 measured        180.7         5.28   ×23.22 on 3/3 comparable

$ tokbench measure decode --engine pipeline --compare-to hf-tokenizers \
    --model gpt2 --model llama-3 --corpus english --corpus chinese

model         corpora  median MB/s  median ns/token          vs hf-tokenizers
-------  ------------  -----------  ---------------  ------------------------
gpt2     2/2 measured        314.2              8.2   ×7.79 on 2/2 comparable
llama-3  2/2 measured        367.8             10.1   ×6.89 on 2/2 comparable

$ tokbench measure latency --engine pipeline --compare-to hf-tokenizers \
    --model gpt2 --corpus english

model  p50 us  p99 us  samples  p50 vs hf-tokenizers  p99 vs hf-tokenizers
-----  ------  ------  -------  --------------------  --------------------
gpt2     2.25    5.21     1000                ×35.04                ×20.95
```

| family | what it answers |
|---|---|
| `encode` | MB/s and ns/byte, text → ids |
| `decode` | MB/s of text produced, ns per input token |
| `latency` | p50/p99 for one short document |
| `scaling` | throughput against thread count, with efficiency |
| `memory` | live heap after load and after encode, isolated child |
| `crate-size` | linked executable size across the tokenizers v1 crate and feature matrix |

Decode is timed over the *reference's* ids, or an engine that merges harder
feeds itself fewer tokens and posts a better rate for less work. The decoded
text is hashed against the reference's, not the corpus, because a lowercasing
normalizer makes `decode(encode(t)) != t` for a correct tokenizer. No decode
entry point means `decode_unsupported`, absent from the ranking rather than
zero in it.

Scaling curves are labelled `native-threads` or `independent-instances`.
`--padding off|longest|both` is an axis; the harness never pads on an engine's
behalf. `--cache-capacity N` sizes the tokenizers v1 BPE cache and `0` disables
it; every engine is also registered as `<name>-no-cache`, and
`cache_ablation_verified` records whether that half really held less heap.

## Example results

Apple M3 Max, single thread, median of 5 over disjoint slices, warm,
`add_special_tokens = false`, gpt2 and llama-3 × 8 corpora = 16 cells.

Encode, over the 3 cells every engine below verified:

| engine | median MB/s | × ref | min | max |
|---|---:|---:|---:|---:|
| pipeline | **90** | 10.7× | 49 | 172 |
| wordchipper | 50 | 6.0× | 44 | 89 |
| fastokens | 50 | 6.0× | 49 | 57 |
| tiktoken | 27 | 3.2× | 23 | 32 |
| kitoken | 25 | 3.0× | 22 | 33 |
| tokie | 21 | 2.5× | 9 | 79 |
| tokenizers 0.23.1 <sub>ref</sub> | 8 | 1.0× | 8 | 9 |

Decode, over the 5 cells every decode-capable engine verified:

| engine | median MB/s | × ref | ns/token |
|---|---:|---:|---:|
| tokie | **379** | 6.9× | 9.4 |
| pipeline | 337 | 6.1× | 11.2 |
| tiktoken | 257 | 4.6× | 16.9 |
| fastokens | 97 | 1.8× | 43.7 |
| tokenizers 0.23.1 <sub>ref</sub> | 55 | 1.0× | 78.1 |

Coverage, which must be read next to the ranking:

| engine | verified | ids differ | unsupported |
|---|---:|---:|---:|
| tokenizers 0.23.1 <sub>ref</sub> | 16 | — | 0 |
| pipeline | 16 | 0 | 0 |
| tiktoken | 16 | 0 | 0 |
| kitoken | 15 | 1 | 0 |
| tokie | 13 | 3 | 0 |
| wordchipper | 12 | 4 | 0 |
| fastokens | 8 | 0 | 8 |
| rust-gems-bpe | 0 | 0 | 16 |

## The engines

An engine that cannot run a cell returns `Unsupported` with the reason; ids that
disagree with the reference are marked `differ` and excluded from every ranking.

| engine | lang | class | notes |
|---|---|---|---|
| [hf-tokenizers](engines/hf-tokenizers) | Rust | native | reference and oracle, `tokenizers` 0.23.1 |
| [pipeline](engines/pipeline) | Rust | native | [tk-encode 1.0.0-rc.0](https://github.com/huggingface/tokenizers) |
| [kitoken](engines/kitoken) | Rust | native | BPE + Unigram + WordPiece |
| [tokie](engines/tokie) | Rust | native | |
| [tiktoken](engines/tiktoken) | Rust | native | needs a derived `ranks.tiktoken` |
| [fastokens](engines/fastokens) | Rust | native | rejects `tokenizer.json` without `model.type` |
| [rust-gems-bpe](engines/rust-gems-bpe) | Rust | native | `bpe-openai` only; plain `bpe` has no pre-tokenizer |
| [wordchipper](engines/wordchipper) | Rust | native | `BpeBacktrack` selector |
| [gigatoken](engines/gigatoken) | Rust | native | off by default; nightly, links libpython |
| [sentencepiece](engines/sentencepiece) | C++ | cffi | needs `spiece.model` |
| [llamacpp](engines/llamacpp) | C++ | cffi | needs a GGUF from `scripts/make_gguf.py` |
| [iree](engines/iree) | C | cffi | gpt2 only |
| [executorch](engines/executorch) | C++ | cffi | own process: its static PCRE2 preempts fastokens' and degrades it ~18× with correct ids |

`pipeline` and `hf-tokenizers` are the same project reading the same
`tokenizer.json`, so the gap is the encode path and nothing else. Decode is
wired for those two plus `tokie`, `tiktoken` and `fastokens`; the rest report
`decode_unsupported`. One method per adapter, and a welcome PR.

## Hugging Face Jobs

[`hf-jobs/`](hf-jobs/) runs the benchmark in an immutable container against a
pinned data revision, over several process-level repetitions, recording the
environment and writing reports plus checksums to a Storage Bucket:

```bash
make dash BUCKET=huggingface/tokbench-results JOB_ID=<job-id>
```

A hardware flavor does not pin a physical CPU, so absolute results stay
machine-specific; what Jobs buys is reproducible invocation and variance.

## Footprint

- **`crate_size_kb`** — published package size. `scripts/package_size.py`.
- **`binary_delta_kb`** — stripped bytes over a no-engine baseline.
  `scripts/binsize.sh`.
- **`heap_load_mb` / `heap_encode_mb`** — live heap after load and after
  encode, one child per engine, because in one process the allocator hands
  engine B the pages engine A freed. Live heap, not RSS: RSS is a high-water
  mark that bills a loader for what it already freed.

## Output

```json
{
  "dataset_metadata": { "corpus": "english", "model": "gpt2", "reps": 5, "warmup": true },
  "results": [
    { "tokenizer_name": "tokie", "total_tokens_produced": 245277,
      "mean_execution_time_seconds": 0.0028, "mbps": 96.7, "ns_per_byte": 9.86,
      "engine_class": "native", "verified": true, "ids_hash": "47cdd1399a60de5a",
      "decode_mbps": 412.7, "decode_ns_per_token": 9.8, "decode_verified": true,
      "heap_load_mb": 3.5, "heap_encode_mb": 7.2, "crate_size_kb": 181.0 }
  ],
  "runs": [ "...one entry per model × corpus cell..." ]
}
```

Every field is optional. A cell an engine could not run carries `unsupported`
with the reason, never a zero that would sort as slow.

## Adding an engine

Create `engines/<name>/`, implement two traits, add a line to
`driver/src/registry.rs`:

```rust
impl Build for Adapter {
    fn build(model: &Model) -> Result<Box<dyn Engine>, Unsupported> { ... }
}
impl Engine for Adapter {
    fn info(&self) -> Info { ... }
    fn encode(&mut self, text: &str, out: &mut Ids) { }
    fn decode(&mut self, ids: &[u32], out: &mut String)      // optional
        -> Result<(), Unsupported> { ... }
}
```

Use the library's ordinary public API. An allocation or conversion it forces
stays in the measurement, because the user pays it too; reaching into private
internals to skip work the public path does is out of bounds. `decode` may
decline — return `Err` rather than pushing a short string, or a truncated `out`
hashes as a fast, wrong decode.

## No benchmarking framework

`divan` has no machine-readable output; `criterion`'s `estimates.json` is a
private implementation detail and owns `fn main()`. Neither expresses an
engine × model × corpus matrix, and neither verifies that two engines produced
the same ids.

## Licence

Apache-2.0. Each engine remains under its own licence; this repository vendors
none of them.

Initial development by @ArthurZucker, @SBrandeis, @McPatate, @LysandreJik

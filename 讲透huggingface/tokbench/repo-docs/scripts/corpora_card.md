---
pretty_name: tokbench corpora
license: other
license_name: mixed-per-corpus
license_link: https://huggingface.co/datasets/huggingface/tokbench-corpora#provenance-and-licences
language:
  - am
  - ar
  - bn
  - zh
  - el
  - en
  - he
  - hi
  - ja
  - ka
  - ko
  - ru
  - ta
  - th
task_categories:
  - text-generation
size_categories:
  - 100K<n<1M
tags:
  - tokenizers
  - tokenization
  - benchmark
  - multilingual
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/*/train-*.parquet
  - config_name: amharic
    data_files:
      - split: train
        path: data/amharic/train-*.parquet
  - config_name: arabic
    data_files:
      - split: train
        path: data/arabic/train-*.parquet
  - config_name: bengali
    data_files:
      - split: train
        path: data/bengali/train-*.parquet
  - config_name: chinese
    data_files:
      - split: train
        path: data/chinese/train-*.parquet
  - config_name: english
    data_files:
      - split: train
        path: data/english/train-*.parquet
  - config_name: georgian
    data_files:
      - split: train
        path: data/georgian/train-*.parquet
  - config_name: greek
    data_files:
      - split: train
        path: data/greek/train-*.parquet
  - config_name: hebrew
    data_files:
      - split: train
        path: data/hebrew/train-*.parquet
  - config_name: hindi
    data_files:
      - split: train
        path: data/hindi/train-*.parquet
  - config_name: japanese
    data_files:
      - split: train
        path: data/japanese/train-*.parquet
  - config_name: korean
    data_files:
      - split: train
        path: data/korean/train-*.parquet
  - config_name: russian
    data_files:
      - split: train
        path: data/russian/train-*.parquet
  - config_name: tamil
    data_files:
      - split: train
        path: data/tamil/train-*.parquet
  - config_name: thai
    data_files:
      - split: train
        path: data/thai/train-*.parquet
  - config_name: agentic-swe
    data_files:
      - split: train
        path: data/agentic-swe/train-*.parquet
  - config_name: math-latex
    data_files:
      - split: train
        path: data/math-latex/train-*.parquet
  - config_name: added-special-dense
    data_files:
      - split: train
        path: data/added-special-dense/train-*.parquet
  - config_name: added-special-sparse
    data_files:
      - split: train
        path: data/added-special-sparse/train-*.parquet
  - config_name: added-normalized-dense
    data_files:
      - split: train
        path: data/added-normalized-dense/train-*.parquet
  - config_name: added-normalized-sparse
    data_files:
      - split: train
        path: data/added-normalized-sparse/train-*.parquet
  - config_name: chat-llama3
    data_files:
      - split: train
        path: data/chat-llama3/train-*.parquet
  - config_name: chat-chatml
    data_files:
      - split: train
        path: data/chat-chatml/train-*.parquet
  - config_name: chat-mistral
    data_files:
      - split: train
        path: data/chat-mistral/train-*.parquet
  - config_name: chat-deepseek
    data_files:
      - split: train
        path: data/chat-deepseek/train-*.parquet
---

# tokbench corpora

The input corpora for [tokbench](https://github.com/huggingface/tokbench), a
benchmark that measures tokenizer implementations against each other on the
same bytes. Each config is one corpus: ~5 MB of real text chosen to stress a
different part of a tokenizer.

Nothing here is new text. It is a fixed, pinned, redistributable excerpt of
public datasets, packaged so a tokenizer benchmark is reproducible by anyone
without re-deriving the inputs. Provenance and licence for every config are in
the table below.

## Layout

Two views of the same bytes:

| path | what it is |
|---|---|
| `data/<corpus>/train-*.parquet` | one row per document — `corpus`, `index`, `sep`, `text` |
| `fixtures/<corpus>.txt` | the corpus as a single file, byte-identical to what tokbench reads |

The raw `.txt` is not redundant. tokbench slices each corpus at fixed 10 KiB
byte offsets from byte 0, so the measurement is a function of the exact bytes;
a re-encoded or reordered file is a different benchmark. Rows are the corpus
split at its own boundary — a blank line for prose, a newline for the
`added-*` fixtures — and `sep` carries that boundary, so the two views can
never drift:

```python
rows = load_dataset(REPO, "english", split="train")
rows[0]["sep"].join(rows["text"])   # == fixtures/english.txt, byte for byte
```

That identity is checked against the source `sha256` at publish time, for
every config, and a mismatch aborts the upload.

## How to use

```python
from datasets import load_dataset

REPO = "huggingface/tokbench-corpora"

# one corpus
ds = load_dataset(REPO, "japanese", split="train")
ds[0]  # {'corpus': 'japanese', 'index': 0, 'sep': '\n\n', 'text': '...'}

# every corpus at once; filter on the `corpus` column
everything = load_dataset(REPO, split="train")
chat = everything.filter(lambda r: r["corpus"].startswith("chat-"))
```

Measuring a tokenizer over one corpus:

```python
from tokenizers import Tokenizer

tok = Tokenizer.from_pretrained("gpt2")
ds = load_dataset(REPO, "thai", split="train")
n_tokens = sum(len(e.ids) for e in tok.encode_batch(ds["text"]))
n_bytes = sum(len(t.encode()) for t in ds["text"])
print(f"{n_bytes / n_tokens:.2f} bytes/token")
```

### How tokbench consumes it

tokbench takes the `.txt` side, because its numbers depend on exact bytes:

```sh
make fixtures                             # pull fixtures/*.txt into data/fixtures/
make fixtures CORPORA_REVISION=<sha>      # pin to a commit for a reproducible run
```

which is `hf download huggingface/tokbench-corpora fixtures/<corpus>.txt
--repo-type dataset --revision <sha>`. The driver then reads every `.txt` under
`data/fixtures/` and uses the file stem as the corpus name, so a config name
here is exactly a `--corpus` argument there.

## What each corpus stresses

| config | stresses |
|---|---|
| `english` | Latin-script baseline; almost every tokenizer's best case |
| `chinese`, `japanese`, `korean` | dense CJK: few bytes per character, no or weak word separators |
| `thai` | no word separators at all — pre-tokenization has nothing to split on |
| `arabic`, `hebrew` | right-to-left, rich diacritics, normalizer-sensitive |
| `hindi`, `bengali`, `tamil` | Indic combining marks; grapheme clusters vs code points |
| `russian`, `greek`, `georgian`, `amharic` | non-Latin alphabets outside most BPE merge tables; Ethiopic is the sparsest |
| `math-latex` | backslash-and-brace runs, long symbol sequences, deep punctuation nesting |
| `agentic-swe` | agent trajectories: diffs, terminal output, tool calls, indentation runs |
| `chat-llama3`, `chat-chatml`, `chat-mistral`, `chat-deepseek` | conversations rendered through each family's real Jinja `chat_template`, so the added-token matcher sees a special token every few hundred bytes, in that family's actual markers |
| `added-special-*` | added/special tokens at high and low density — the added-token matcher in isolation |
| `added-normalized-*` | added tokens that the normalizer rewrites, the path a lowercasing or accent-stripping normalizer takes |

The four `chat-*` corpora are one per template *family*, not per model: a
benchmark feeds every engine identical bytes per cell, and a per-model corpus
would break the comparison. Llama-3 uses `<|start_header_id|>` blocks, Mistral
wraps in `[INST]`/`[/INST]` with no role headers, ChatML injects a default
system turn, and each serialises tool calls its own way.

## Provenance and licences

Every corpus is an excerpt of a public source, taken at a pinned revision. No
corpus is redistributed under a licence more permissive than its source.

| config(s) | source | licence |
|---|---|---|
| 13 non-English `lang` configs | [HuggingFaceFW/fineweb-2](https://huggingface.co/datasets/HuggingFaceFW/fineweb-2) `test` split, rev `af9c1333` | ODC-By 1.0 |
| `english` | [HuggingFaceFW/fineweb](https://huggingface.co/datasets/HuggingFaceFW/fineweb) `sample-10BT`, rev `9bb295dd` | ODC-By 1.0 |
| `math-latex` | [open-web-math](https://huggingface.co/datasets/open-web-math/open-web-math), rev `fde8ef8d` | ODC-By 1.0 |
| `agentic-swe` | [SWE-bench/SWE-smith-trajectories](https://huggingface.co/datasets/SWE-bench/SWE-smith-trajectories), rev `08e109b4` | MIT |
| `chat-*` | [HuggingFaceH4/ultrachat_200k](https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k), rendered through the public `chat_template` of Llama-3, Qwen2.5, Mistral-Nemo and DeepSeek-V3 | MIT |
| `added-*` | synthetic — generated filler over a 40-word vocabulary plus placeholder added tokens | CC0-1.0 |

The FineWeb and OpenWebMath corpora are filtered Common Crawl; users should
also observe the [Common Crawl terms of
use](https://commoncrawl.org/terms-of-use/). ODC-By requires attribution: cite
FineWeb / FineWeb-2 / OpenWebMath when you report numbers measured on those
configs.

This is raw web, code and agent text. Treat it as untrusted data: fine to feed
to a tokenizer, not fine to execute, and prefer `less` over `cat` — it can
contain terminal escape sequences. NUL bytes were stripped at build time;
everything else is kept as-is, because the mess is the point.

## Corpora tokbench uses that are not published here

Deliberately excluded. Each is a licence or provenance fact, not an oversight:

| corpus | why not |
|---|---|
| `code-mixed` | contains verbatim redis source (RSALv2 / SSPLv1 / AGPLv3) and junit5 (EPL-2.0) |
| `agentic-traces` | provenance unrecorded upstream — synthetic agent traces of unknown origin |
| `multilingual-mix` | built by interleaving `code-mixed` and `agentic-traces` paragraphs, so it inherits both |
| `agentic-tools` | derived from SWE-bench_Lite, which declares no licence; its patches include pylint (GPL-2.0) |
| `xnli` | `facebook/xnli` declares no licence |

A benchmark run that needs those must still build them locally.

## Citation

```bibtex
@software{tokbench,
  title  = {tokbench: a tokenizer implementation benchmark},
  author = {Hugging Face},
  url    = {https://github.com/huggingface/tokbench}
}
```

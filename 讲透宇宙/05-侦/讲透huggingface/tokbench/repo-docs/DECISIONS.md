# Decisions

## What we measure

- One timing loop per direction, shared by every engine — an engine measured on its own terms is not comparable.
- Encode and decode are both first-class; decode is timed over the reference's ids so an engine that merges harder cannot post a better rate for less work.
- The recurrence sweep is a first-class `tokbench measure recurrence` command, not a one-off script.
- Load is not encode: vocabulary and automaton construction happen before the clock.
- Single thread is the headline; every scaling curve states whose threads it used.

## What we removed

- Every interpreted engine — minbpe, mistral-common, ai-tokenizer — so there is no Python engine left at all.
- `python/harness.py` and the whole scripted-engine path, which only existed to drive those engines.
- blingfire — it never verified a single cell, so it was never rankable.
- The per-phase breakdown — it existed for one engine only, which makes it a property of that adapter rather than a comparable measurement.
- `figs/`, the committed sample outputs, and the scripts that only fed them.
- The dashboard stays.

## How the code reads

- No comments on the engine adapters — they are third-party libraries being plugged in, nothing more.
- Comments in `core/` and `driver/` only where they explain a decision the code cannot.
- Minimal over complete: the shortest thing that works.

## Fairness rules

- A cache ablation must be proved, not asserted — a `-no-cache` row must show lower live heap than its twin or it is not an ablation.
- A cache that is "worth ~1.0×" is not a result until it is explained — an unexplained null forces the experiment, not a footnote.
- A recurrence sweep may vary repetition and nothing else.
- Token density is held constant across a sweep and reported as an audit column, so a confound cannot hide.
- Sample the sweep vocabulary uniformly at random — frequency-ordered vocabularies make high-recurrence points out of short common words.
- Never pad a sweep corpus with generated filler; it tokenises nothing like real text.
- Report the achieved recurrence rate, never the requested one.
- An engine with no cache must not speed up with repetition — if it does, the harness is measuring something other than caching.
- gigatoken cannot be faster on non-repeating input because there is nothing to hit — tested and confirmed.
- Cross-engine medians use only cells every compared engine ran and verified.
- Timed slices are disjoint, so no timed pass ever re-encodes text it has already seen.

## Corpora

- The corpora are mixed on purpose — an English-only ranking reverses on CJK.
- The corpus-building scripts stay in the repo.
- The corpora themselves are published publicly on the Hub and must be easy to load.
- A corpus whose licence or provenance does not permit redistribution is withheld, with the reason stated.
- The published corpora ship byte-identical to what the driver chunks, or the numbers do not transfer.

## Reporting

- The README leads with why the data is mixed and what an unbounded cache actually measures.
- A table and a few sentences beat long prose — three successive drafts were rejected as bloat.
- Numbers in the README come from a real run, with the machine stated.
- An unbounded cache measures repetition, not tokenisation, and production traffic is not a corpus you encode twice.

## Repository

- `jobs/` is renamed `hf-jobs/`.
- `main` becomes the default branch.
- The user pushes to `main` manually; the agent never does.
- Commits carry no Claude attribution.

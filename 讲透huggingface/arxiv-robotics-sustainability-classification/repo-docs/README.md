# arxiv-sustainability-classification

Automated pipeline that downloads arXiv robotics papers, runs
**DeepSeek-V3.2-Exp** via the HuggingFace Inference API, and produces a
structured JSON dataset annotating each paper with its UN Sustainable
Development Goal (SDG) relevance.

The code takes the desired date range as input, fetches metadata for all papers in that range (on Arxiv's `cs.Ro`- robotics section), downloads the PDFs, and runs inference to classify each paper's sustainability motivation and SDG alignment. The final output is a JSON file with structured annotations for each paper, which can be used for analysis and visualization.


This repository's code is used for generating the dataset and analysis in the blog post:
[Robotics should think (and do) more about sustainability](https://huggingface.co/spaces/sustainable-robotics/sustainability-in-robotics#how-many-papers-are-motivated-by-sustainability-related-topics).

The generated dataset of 50,000 papers spaning from 2015 to Q1 of 2026 is available on HuggingFace:
https://huggingface.co/datasets/sustainable-robotics/robotics-arxiv-sustainability-classification


---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your HuggingFace token
export HF_TOKEN=hf_...

# 3. Run the full pipeline for a date range
# the example below processes papers published in April 2026, with outputs in ./run/2026-apr/
python run_pipeline.py \
    --start-date 2026-04-01 \ 
    --end-date   2026-04-30 \
    --work-dir   ./run/2026-apr
```

All outputs land in `--work-dir`:

| File | Contents |
|------|----------|
| `metadata.json` | Raw arXiv metadata fetched from the API |
| `pdfs/` | Downloaded PDF files |
| `metadata_for_pdfs.json` | Metadata filtered to locally available PDFs (with `pdf_path`) |
| `results.json` | DeepSeek responses + parsed SDG fields — **resumable** |

---

## Resuming an interrupted run

Just re-run the same command. Papers with an existing successful response
are skipped automatically. Use `--force-rerun` to reprocess everything.

```bash
# Resume
python run_pipeline.py --start-date 2025-01-01 --end-date 2025-06-30 \
    --work-dir ./run/2025-h1

# Force full rerun
python run_pipeline.py --start-date 2025-01-01 --end-date 2025-06-30 \
    --work-dir ./run/2025-h1 --force-rerun
```

---

## Running individual stages

Each pipeline module is also a standalone CLI script:

```bash
# Fetch metadata only
python -m pipeline.fetch_metadata \
    --start-date 2025-01-01 --end-date 2025-06-30 \
    --output ./run/metadata.json

# Download PDFs only
python -m pipeline.download_pdfs \
    ./run/metadata.json \
    --output-folder ./run/pdfs \
    --start-date 2025-01-01 --end-date 2025-06-30

# Build local metadata index (pdf_path fields)
python -m pipeline.prepare_metadata \
    ./run/metadata.json ./run/pdfs \
    --output ./run/metadata_for_pdfs.json

# Run inference only
python -m pipeline.infer_deepseek \
    ./run/metadata_for_pdfs.json \
    --output ./run/results.json

# Validate / check completion status
python -m pipeline.validate ./run/results.json
```

---

## Plotting and report generation

The `plotting/` folder contains standalone scripts that consume classified JSON
data directly (no regex re-parsing of raw model text).

Accepted input formats:
- Pipeline output (`run/.../results.json`) where parsed fields are under `deepseek.parsed`
- Compiled dataset where parsed fields are top-level keys

Generate a full PDF report in `run/.../report/`:

```bash
# Writes plots + README to ./run/2025-h1/report/
python plotting/generate_report.py ./run/2025-h1/results.json ./run/2025-h1
```

If you omit the second argument, the script creates a sibling `report/`
directory next to the input JSON.

Generated report artifacts:
- `total_in_time.pdf`
- `explicit_sustainability_vs_total.pdf`
- `impacts_mentions_motivation.pdf`
- `impacts_breakdown.pdf`
- `sdg_absolute.pdf`
- `sdg_relative.pdf`
- `README.md` (short explanation of each plot)

You can also run individual plotting scripts in `plotting/` directly with a JSON
path as input.

---

## Key options

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `deepseek-ai/DeepSeek-V3.2-Exp` | HF model ID |
| `--infer-workers` | `8` | Parallel inference threads |
| `--num-papers` | `0` (all) | Limit inference to first N papers |
| `--max-text-chars` | `100000` | Max PDF characters sent per paper |
| `--max-tokens` | `3000` | Max response tokens |
| `--temperature` | `0.2` | Sampling temperature |
| `--skip-fetch` | — | Skip metadata download stage |
| `--skip-download` | — | Skip PDF download stage |
| `--skip-infer` | — | Skip inference stage |
| `--force-rerun` | — | Re-process already-completed papers |

---

## Output JSON schema (`results.json`)

Each entry in the array is an arXiv metadata record enriched with a
`deepseek` field:

```json
{
  "id": "https://arxiv.org/abs/2501.12345",
  "title": "...",
  "authors": ["..."],
  "published": "2025-01-15T00:00:00Z",
  "summary": "...",
  "pdf_url": "...",
  "pdf_path": "/abs/path/to/file.pdf",
  "deepseek": {
    "success": true,
    "response": "... raw model output ...",
    "parsed": {
      "paper_type": "experimental",
      "motivated_by_sdgs": ["SDG 9"],
      "aligned_with_sdgs": ["SDG 9", "SDG 11"],
      "mentions_social_impact": false,
      "mentions_ecological_impact": false,
      "mentions_sustainability_impact": false,
      "mentions_un_sdgs": false
    },
    "model": "deepseek-ai/DeepSeek-V3.2-Exp",
    "time_seconds": 12.4,
    "error": null
  }
}
```

---

## Prompt resources

The SDG reference texts used in prompts live in `data/prompts/`:

| File | Contents |
|------|----------|
| `un_sdgs.txt` | Full list of 17 UN SDGs and their targets |
| `ifc_sdg_proposals.txt` | IFR proposals on how robots support SDGs |

Override paths with `--sdg-text` / `--ifr-text` on the inference stage.

<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/science-skills · page 10 Predicting the Past: Ancient Text Analysis · fetched 2026-10-26 -->

# Predicting the Past: Ancient Text Analysis

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/predictingthepast/SKILL.md](skills/predictingthepast/SKILL.md)
- [skills/predictingthepast/scripts/run_inference.py](skills/predictingthepast/scripts/run_inference.py)

</details>



The `predictingthepast` skill provides computational tools for analyzing, restoring, dating, and attributing ancient Latin and Ancient Greek inscriptions. As the sole non-biological skill in the repository, it bridges classical epigraphy and modern machine learning by running JAX-based neural network models—**Aeneas** for Latin and **Ithaca** for Greek [skills/predictingthepast/SKILL.md:1-20](), [skills/predictingthepast/scripts/run_inference.py:15-25](). 

The system performs four primary epigraphic tasks:
1. **Restoration**: Predicting missing or damaged characters represented by markup characters (`?` and `#`) [skills/predictingthepast/SKILL.md:16-19]().
2. **Attribution**: Determining the geographical provenance (region/location) and chronological date (year bins) of an inscription [skills/predictingthepast/SKILL.md:16-19]().
3. **Contextualization**: Retrieving parallel inscriptions from reference corpora to provide historical context [skills/predictingthepast/SKILL.md:16-19]().
4. **Embedding**: Generating dense text embedding vectors for downstream epigraphic comparisons [skills/predictingthepast/SKILL.md:16-19](), [skills/predictingthepast/scripts/run_inference.py:18-21]().

Sources: [skills/predictingthepast/SKILL.md:1-20](), [skills/predictingthepast/scripts/run_inference.py:15-25]()

---

```mermaid
graph TD
    A["UserQuery (\"Restore and date inscription\")"] --> B["preprocess.py (Text Normalization)"]
    B --> C["run_inference.py (JAX Model Runner)"]
    C --> D["aeneas_117149994_2.pkl / ithaca_153143996_2.pkl"]
    C --> E["visualize_results.py (HTML Dashboard)"]
    
    subgraph "Code Entity Space"
        B
        C
        D
        E
    end
```
*Figure 10.1: End-to-end execution flow bridging natural language queries to script entrypoints and checkpoint artifacts.*

Sources: [skills/predictingthepast/SKILL.md:36-40](), [skills/predictingthepast/scripts/run_inference.py:53-63]()

---

## 10.1 Inference Pipeline (`run_inference.py`)

The inference pipeline is driven by `run_inference.py`, which handles automatic model asset downloads from Google Cloud Storage (GCS), input text windowing, JAX model execution, and result enrichment. 

For texts exceeding `750` characters, the script implements an overlapping window strategy, aggregating scores across segments [skills/predictingthepast/scripts/run_inference.py:23-25](), [skills/predictingthepast/scripts/run_inference.py:97-100](). Tasks are modularly enabled via CLI flags (`--attribute`, `--restore`, `--contextualize`, and `--embedding`) [skills/predictingthepast/SKILL.md:128-138](). Geographical outputs are mapped to human-readable names using bundled region reference files, and chronological outputs are converted from 10-year bins into calendar years [skills/predictingthepast/scripts/run_inference.py:122-202]().

For detailed coverage of CLI flags, GCS range-request checkpoint downloads, sliding window splitting algorithms, and output handling, see [Inference Pipeline (run_inference.py)](#10.1).

Sources: [skills/predictingthepast/SKILL.md:128-138](), [skills/predictingthepast/scripts/run_inference.py:23-25](), [skills/predictingthepast/scripts/run_inference.py:97-100](), [skills/predictingthepast/scripts/run_inference.py:122-202]()

---

## 10.2 Preprocessing, Visualization, and Reference Data

Raw epigraphic transcriptions often contain editorial markings, accents, and non-standard characters that must be cleaned prior to model ingestion. The `preprocess.py` script normalizes Greek and Latin texts by removing punctuation, stripping editorial brackets, mapping numbers to neutral tokens, and filtering out-of-vocabulary characters [skills/predictingthepast/SKILL.md:66-93]().

To assist researchers in interpreting model outputs, `visualize_results.py` compiles JSON inference payloads into interactive HTML dashboards [skills/predictingthepast/SKILL.md:164-169](). These tools rely on bundled reference corpora—including the Inscriptions of Aphrodisias (`iphi`) and Later Epigraphic Database (`led`) datasets, region-to-name lookup tables, and proper name ledgers [skills/predictingthepast/scripts/run_inference.py:53-78]().

For detailed documentation on normalization rules, dashboard generation parameters, and dataset schemas, see [Preprocessing, Visualization, and Reference Data](#10.2).

Sources: [skills/predictingthepast/SKILL.md:66-93](), [skills/predictingthepast/SKILL.md:164-169](), [skills/predictingthepast/scripts/run_inference.py:53-78]()

---


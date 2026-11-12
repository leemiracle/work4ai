# Example: Biology Paper Discrepancy Detection

**Type:** Internal Consistency Check (Tier 1A)  
**Document:** Scientific paper on metabolic scaling  
**Result:** DISCREPANCY FOUND  
**Reproducible:** Yes — see instructions below

---

## Paper Reference

- **Title:** Metabolic scaling in small life forms
- **Authors:** Mark E. Ritchie, Christopher P. Kempes
- **arXiv:** [2403.00001](https://arxiv.org/abs/2403.00001)
- **PDF:** https://arxiv.org/pdf/2403.00001

**Copyright Note:** We do not redistribute the PDF. Download directly from arXiv.

---

## The Problem

This biology paper contains multiple internal tensions between figure labels and text claims for the scaling exponent β. These discrepancies could propagate into a RAG knowledge base and cause downstream confusion.

---

## Multi-Model Validation (December 2025)

Three different models independently found numerical tensions in this paper:

| Model | Figure Value | Text Value | Location | Notes |
|-------|--------------|------------|----------|-------|
| **ArxiParse** | β = 0.33 (1/3) | β = 0.73 (11/15) | Large prokaryote asymptotic vs Eq. 7 | 121% discrepancy |
| **Gemini 3 Pro** | β = 1.26 | β = 0.73 | Superlinear label vs asymptotic prediction | Paper explains via "essential volume" |
| **Claude Opus 4.5** | β = 1.26 | β = 1.68 | Superlinear label (Fig 2) vs text claim (page 5) | 25% discrepancy |

### Key Finding

All three findings are legitimate. The paper addresses some through the "essential volume" explanation, but the numerical inconsistencies exist and require careful reading to reconcile.

This demonstrates:
- Complex papers have multiple cross-referencing challenges
- Automated checking surfaces issues for human review
- Different models may catch different discrepancies
- Even explained discrepancies benefit from explicit flagging

---

## How to Reproduce

### Option 1: Manual Verification (Claude/Gemini)

1. Download the PDF from [arXiv 2403.00001](https://arxiv.org/pdf/2403.00001)
2. Upload to Claude Opus 4.5 or Gemini 3 Pro
3. Use this prompt:

```
Please analyze Figure 2 in this paper. Compare the scaling exponent (β)
shown in the figure for prokaryotes against the values predicted in the
text (Equation 7, the Metabolic scaling section on page 5, and Supplementary Figure 4 on page 19).

Report any numerical discrepancies between what the figure shows and
what the text claims.
```

4. The model should identify at least one of the discrepancies listed above

### Option 2: ArxiParse Pipeline

For automated cross-referencing of scientific papers:
- See [arxiparse.org](https://arxiparse.org)
- The pipeline extracts skeleton, figures, and runs claim validation automatically

---

## What Clarity Gate Found (ArxiParse Output)

```yaml
check: internal_consistency
type: figure_vs_text
status: DISCREPANCY_FOUND

findings:
  - claim_type: numerical_parameter
    parameter: β (scaling exponent)
    
    figure:
      location: Figure 2
      value: β = 1/3 ≈ 0.33
      context: "for large prokaryotes"
      
    text:
      location: Equation 7 prediction
      value: β = 11/15 = 0.73
      context: "prokaryote scaling"
      
    discrepancy:
      delta: 0.40
      relative_error: 121%
      severity: HIGH
      
    assessment: >
      The text predicts β = 0.73 from Equation 7, but Figure 2 
      shows β = 0.33 for large prokaryotes. The paper explains 
      this through scaling regime transitions, but the numerical 
      tension warrants flagging for reader attention.
```

---

## Why This Matters

### Without Clarity Gate

1. Paper ingested into RAG knowledge base
2. User asks: "What is the scaling exponent β for prokaryotes?"
3. RAG retrieves conflicting chunks:
   - Chunk A: "β = 0.33 for large prokaryotes"
   - Chunk B: "β = 0.73 for prokaryotes"
   - Chunk C: "β = 1.26 superlinear scaling"
   - Chunk D: "β = 1.68 for small prokaryotes"
4. LLM confidently reports one or synthesizes incorrectly
5. User makes decisions based on unreliable information

### With Clarity Gate

1. Discrepancies detected at ingestion
2. Document flagged for human review
3. Reviewer understands the scaling regime complexity
4. Annotated version ingested with context
5. Knowledge base maintains accurate nuance

---

## Performance

| Metric | Value | Notes |
|--------|-------|-------|
| Detection time | < 1 minute | Single run, informal timing |
| Manual equivalent | ~20+ minutes | Estimated time for careful cross-referencing |
| Models tested | 3 | ArxiParse, Gemini 3 Pro, Opus 4.5 |

**Caveat:** These are informal measurements, not rigorous benchmarks.

---

## The 7-Point Analysis

| Check | Result | Finding |
|-------|--------|---------|
| 1. Hypothesis vs. Fact | ⚠️ | Model predictions vs measurements |
| 2. Uncertainty Markers | ⚠️ | Predictions not always marked as such |
| 3. Assumption Visibility | ⚠️ | Different populations assumed |
| 4. Authoritative-Looking Data | ⚠️ | Figure presents as authoritative |
| **5. Data Consistency** | **❌ FAIL** | **Multiple figure vs. text mismatches** |
| 6. Implicit Causation | N/A | Not the primary issue |
| 7. Future State as Present | N/A | Not the primary issue |

---

## Resolution Options

### Option A: Add Explicit Reconciliation

The paper does explain the different scaling regimes, but could be clearer:

```markdown
Suggested annotation for RAG ingestion:

"NOTE: This paper discusses multiple β values for prokaryotes:
- β ≈ 1.68 (or 1.26): Superlinear regime for smallest prokaryotes
- β = 11/15 ≈ 0.73: Asymptotic prediction from Equation 7  
- β = 1/3 ≈ 0.33: Large prokaryote diffusion limit

These are not contradictions but different scaling regimes.
See the Metabolic scaling section (page 5) and Supplementary Figure 4 (page 19) for full explanation."
```

### Option B: Ingest with Warnings

```yaml
annotation:
  type: complexity_warning
  note: "Multiple β values exist for different size regimes; see paper for details"
  added_by: clarity_gate
  date: 2025-12-22
```

---

## Generalization

This example demonstrates Tier 1A pattern for all internal consistency checks:

1. **Extract claims** from different document locations
2. **Cross-reference** for consistency
3. **Flag discrepancies** with specific locations and values
4. **Route to human** with clear context
5. **Annotate or block** based on severity

The same approach applies to:
- Abstract vs. body claims
- Table vs. prose data
- Repeated values in different sections
- Figure labels vs. captions

---

## Limitations

| Limitation | Implication |
|------------|-------------|
| Single paper | May not generalize to all paper types |
| Physics/biology domain | Other domains not tested |
| Numerical claims focus | Text-based inconsistencies harder |
| Informal timing | Not benchmarked |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-21 | Initial example |
| 2.0 | 2025-12-22 | Added paper reference, multi-model validation, reproducibility instructions |

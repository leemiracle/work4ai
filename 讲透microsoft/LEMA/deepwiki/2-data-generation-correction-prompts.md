<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/LEMA · page 2 Data Generation: Correction Prompts · fetched 2026-10-26 -->

# Data Generation: Correction Prompts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [prompts/prompt_correction_csqa.txt](prompts/prompt_correction_csqa.txt)
- [prompts/prompt_correction_gsm8k.txt](prompts/prompt_correction_gsm8k.txt)
- [prompts/prompt_correction_math.txt](prompts/prompt_correction_math.txt)

</details>



The LEMA (Learning From Mistakes) framework relies on a data synthesis phase where a teacher LLM is prompted to generate mistake-correction pairs. Instead of simply training on correct solutions, LEMA generates "incorrect" reasoning traces and then uses specific prompts to identify the errors and provide corrected paths. This mimics human pedagogical methods where students learn by analyzing their own failures.

## Correction Methodology

The core of the data generation process is the **Correction Prompt**. This prompt instructs a teacher LLM (such as GPT-4) to act as an evaluator and tutor. The input to these prompts typically consists of a question and an "Original Solution" (which is often a sampled incorrect output from a smaller model or a perturbed reasoning chain). The teacher LLM is then tasked with producing:
1.  **Identification**: Locating the specific step where the reasoning first deviated from the correct path.
2.  **Explanation**: Describing *why* that specific step is logically or mathematically unsound.
3.  **Correction**: Providing a valid completion of the reasoning starting from the last correct point.

### Relationship Between System Components

The following diagram illustrates how the prompt templates interface with the teacher LLM to generate the training data used by the fine-tuning engine.

**Data Synthesis Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        [User_Prompt] --> [Teacher_LLM]
        [Original_Mistake] --> [Teacher_LLM]
    end

    subgraph "Code Entity Space"
        [Teacher_LLM] -- "Generates" --> [Correction_Data_JSONL]
        [Correction_Data_JSONL] -- "Consumed by" --> [make_data_module]
        [make_data_module] -- "Feeds" --> [qlora.py:train]
    end

    [prompts/prompt_correction_gsm8k.txt] -. "Template for" .-> [User_Prompt]
    [prompts/prompt_correction_csqa.txt] -. "Template for" .-> [User_Prompt]
```

**Sources:**
*   [README.md:21-26]()
*   [README.md:58-62]()

---

## GSM8K and MATH Correction Prompts

For mathematical reasoning, the prompts focus on sequential logic. The teacher LLM is provided with a few-shot context where it sees a math word problem followed by a step-by-step "Original Solution" that contains a calculation or conceptual error. 

The prompt structure forces the model to output a structured block containing an `Incorrect Step` identifier, an `Explanation` of the error, and a `Correct Solution`. This format is consistent across both the GSM8K (grade school math) and MATH (competition level) datasets, though the complexity of the few-shot examples differs to match the target difficulty.

For details on the specific step-by-step identification logic and LaTeX formatting requirements, see **[GSM8K and MATH Correction Prompts](#2.1)**.

**Sources:**
*   [prompts/prompt_correction_gsm8k.txt:1-82]()
*   [prompts/prompt_correction_math.txt:1-112]()

---

## CommonsenseQA Correction Prompt

Unlike the mathematical datasets, the CommonsenseQA (CSQA) prompt deals with multi-choice questions and qualitative reasoning. The correction prompt for CSQA is more elaborate, requiring the teacher LLM to evaluate five distinct candidate answers.

The generated correction data for CSQA follows a schema of `Explanations` (for all choices), `Reasons and Final Answer`, a `Mistakes` section identifying flaws in the initial reasoning, and a final `Corrected Answer` block. This targets four specific types of reasoning errors:
*   Contextual relevance
*   Taxonomic errors
*   Likely vs. serious conflation
*   Specificity issues

For details on the structured schema and the reasoning error categories, see **[CommonsenseQA Correction Prompt](#2.2)**.

**Sources:**
*   [prompts/prompt_correction_csqa.txt:1-69]()

---

## Prompt Template Mapping

The following table maps the dataset types to their respective prompt templates within the repository:

| Dataset | Prompt File Path | Primary Logic Type |
| :--- | :--- | :--- |
| **GSM8K** | `prompts/prompt_correction_gsm8k.txt` | Arithmetic/Step-based |
| **MATH** | `prompts/prompt_correction_math.txt` | Advanced Symbolic/LaTeX |
| **CSQA** | `prompts/prompt_correction_csqa.txt` | Commonsense/Elimination |

**Sources:**
*   [prompts/prompt_correction_gsm8k.txt:1-1]()
*   [prompts/prompt_correction_math.txt:1-1]()
*   [prompts/prompt_correction_csqa.txt:1-1]()

---


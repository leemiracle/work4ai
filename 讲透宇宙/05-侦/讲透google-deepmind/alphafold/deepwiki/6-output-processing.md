<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphafold · page 6 Output Processing · fetched 2026-10-26 -->

# Output Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [alphafold/common/confidence.py](alphafold/common/confidence.py)
- [alphafold/common/confidence_test.py](alphafold/common/confidence_test.py)
- [alphafold/data/parsers.py](alphafold/data/parsers.py)
- [alphafold/data/tools/jackhmmer.py](alphafold/data/tools/jackhmmer.py)
- [alphafold/notebooks/notebook_utils.py](alphafold/notebooks/notebook_utils.py)
- [alphafold/relax/amber_minimize.py](alphafold/relax/amber_minimize.py)
- [alphafold/relax/relax.py](alphafold/relax/relax.py)

</details>



This page describes how AlphaFold processes and refines its raw predicted protein structures to produce the final outputs. The output processing consists primarily of two main components: structure relaxation (using Amber) and generation of confidence metrics to evaluate prediction quality. 

For information about how confidence metrics are calculated in detail, see [Confidence Metrics](#6.1). For specifics on the structure relaxation process, see [Structure Relaxation](#6.2).

## Overview of Output Processing

Output processing takes the raw structure prediction from AlphaFold's Structure Module and transforms it into refined structures with associated confidence metrics. These steps are critical for producing biologically plausible structures and providing users with information about prediction reliability.

```mermaid
flowchart TD
    subgraph "Model Output"
        RawStructure["Raw Predicted Structure"]
        ConfidenceLogits["Confidence Logits"]
    end
    
    subgraph "Output Processing"
        RawStructure --> StructureViolations["Find Structural Violations"]
        StructureViolations --> AmberRelax["Amber Relaxation"]
        
        ConfidenceLogits --> pLDDT["compute_plddt()"]
        ConfidenceLogits --> PAE["compute_predicted_aligned_error()"]
        ConfidenceLogits --> pTM["predicted_tm_score()"]
        
        AmberRelax --> FinalStructure["Relaxed Structure"]
    end
    
    subgraph "Final Outputs"
        FinalStructure --> PDBFile["PDB File"]
        pLDDT --> ConfidenceJSON["confidence_json()"]
        PAE --> PAEMatrix["pae_json()"]
    end
```

Sources:
- [alphafold/relax/amber_minimize.py:426-505]()
- [alphafold/common/confidence.py:30-45]()
- [alphafold/common/confidence.py:127-155]()
- [alphafold/common/confidence.py:184-205]()

## Structure Refinement Process

After the AlphaFold model predicts a protein structure, it needs to be refined to resolve any structural violations (like steric clashes) and create a physically plausible model. This is achieved through the `AmberRelaxation` pipeline, which applies energy minimization via OpenMM with restraints to avoid large deviations from the predicted structure.

```mermaid
flowchart TB
    Start["Protein Instance"] --> Check["_check_residues_are_well_defined()"]
    Check --> Clean["clean_protein()"]
    Clean --> Pipeline["run_pipeline()"]
    
    subgraph "Relaxation Pipeline [amber_minimize.py]"
        Pipeline --> FindViolations["find_structural_violations()"]
        FindViolations --> Exclude["Exclude Violation Residues"]
        Exclude --> Minimize["_openmm_minimize()"]
        Minimize --> CheckMore["Check if Violations Remain"]
        CheckMore --> |"Yes"| Pipeline
        CheckMore --> |"No"| Done["Relaxation Complete"]
    end
    
    Done --> Output["Final PDB String"]
```

Sources:
- [alphafold/relax/amber_minimize.py:79-113]()
- [alphafold/relax/amber_minimize.py:145-153]()
- [alphafold/relax/amber_minimize.py:162-191]()
- [alphafold/relax/relax.py:23-90]()

## Structure Cleaning and Preparation

Before relaxation, the predicted structure must be cleaned to ensure compatibility with the OpenMM simulation package. This involves adding missing atoms and ensuring the atom mask is ideal. The `clean_protein` function handles the conversion of a `Protein` instance into a PDB string and fixes it using the `cleanup` module.

```mermaid
flowchart LR
    Prot["Protein Instance"] --> Ideal["_check_atom_mask_is_ideal()"]
    Ideal --> ToPDB["protein.to_pdb()"]
    ToPDB --> Fix["cleanup.fix_pdb()"]
    Fix --> CleanStr["cleanup.clean_structure()"]
    CleanStr --> FinalPDB["Cleaned PDB String"]
```

Sources:
- [alphafold/relax/amber_minimize.py:155-161]()
- [alphafold/relax/amber_minimize.py:162-191]()
- [alphafold/relax/cleanup.py:15-127]()

## Structural Violation Detection

A key part of the refinement process is finding and resolving structural violations. The system analyzes the protein structure to identify residues involved in violations, such as steric clashes or bond geometry issues. In `amber_minimize.py`, the system generates an `atom14` representation to perform these checks.

Sources:
- [alphafold/relax/amber_minimize.py:194-220]()
- [alphafold/relax/amber_minimize.py:320-366]()

## OpenMM Minimization Process

The actual structure relaxation uses `openmm` to perform energy minimization. It uses the `amber99sb.xml` force field and applies harmonic restraints to atoms (either `non_hydrogen` or `c_alpha`) to maintain the overall predicted fold while allowing local adjustments.

Sources:
- [alphafold/relax/amber_minimize.py:40-47]()
- [alphafold/relax/amber_minimize.py:49-77]()
- [alphafold/relax/amber_minimize.py:79-113]()

## Confidence Metrics Calculation

AlphaFold generates several confidence metrics to help users assess the reliability of predictions:

1.  **pLDDT**: Per-residue confidence score (0-100) calculated in `compute_plddt`.
2.  **PAE**: Predicted Aligned Error, calculated in `compute_predicted_aligned_error`.
3.  **pTM/ipTM**: Predicted TM-score and interface TM-score for complexes, calculated in `predicted_tm_score`.

```mermaid
flowchart TD
    Logits["Logits from Model Heads"] --> Softmax["_softmax()"]
    Softmax --> pLDDT["compute_plddt()"]
    Softmax --> PAE["compute_predicted_aligned_error()"]
    Softmax --> pTM["predicted_tm_score()"]
    
    pLDDT --> JSON_C["confidence_json()"]
    PAE --> JSON_P["pae_json()"]
```

Sources:
- [alphafold/common/confidence.py:23-27]()
- [alphafold/common/confidence.py:30-45]()
- [alphafold/common/confidence.py:61-81]()
- [alphafold/common/confidence.py:127-155]()
- [alphafold/common/confidence.py:158-181]()
- [alphafold/common/confidence.py:184-212]()

## Output File Generation

The final output includes multiple files representing the structural coordinates and the confidence metrics.

| Output File | Content | Format | Source Function |
| :--- | :--- | :--- | :--- |
| `relaxed_model.pdb` | Minimized coordinates | PDB | `AmberRelaxation.process` |
| `confidence.json` | pLDDT and categories | JSON | `confidence_json` |
| `pae.json` | PAE matrix | JSON | `pae_json` |

Sources:
- [alphafold/relax/relax.py:60-90]()
- [alphafold/common/confidence.py:61-81]()
- [alphafold/common/confidence.py:158-181]()

## Technical Implementation Details

### Amber Relaxation Parameters
The `AmberRelaxation` class (defined in `alphafold/relax/relax.py`) manages the refinement pipeline with the following key parameters:
*   `max_iterations`: Limit for L-BFGS iterations.
*   `tolerance`: Energy tolerance for convergence.
*   `stiffness`: Spring constant for heavy atom restraints.
*   `max_outer_iterations`: Number of violation-informed iterations (defaulting to iterative procedure if violations persist).

Sources:
- [alphafold/relax/relax.py:23-58]()
- [alphafold/relax/amber_minimize.py:426-450]()

### Confidence Metric Calculations
Confidence scores are derived from the predicted distribution over distance or error bins:
*   **pLDDT**: Uses `PredictedLDDTHead` logits to calculate an expected value of the LDDT per residue.
*   **PAE**: Uses `PredictedAlignedErrorHead` logits to calculate expected distance error between residue pairs.
*   **Categories**: pLDDT is categorized into 'D' (disordered < 50), 'L' (low < 70), 'M' (medium < 90), and 'H' (high > 90).

Sources:
- [alphafold/common/confidence.py:30-45]()
- [alphafold/common/confidence.py:47-59]()
- [alphafold/common/confidence.py:102-124]()

---


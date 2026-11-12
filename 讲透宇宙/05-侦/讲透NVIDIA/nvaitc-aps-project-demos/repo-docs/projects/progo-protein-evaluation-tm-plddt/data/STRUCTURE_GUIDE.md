# Directory Structure Guide

This guide shows where different files should be placed in the ProGo Protein Evaluation Pipeline.

## Input Files

### FASTA Files
- **Location**: `data/input/`
- **Example**: `data/input/your_sequences.fasta`
- **Purpose**: Input protein sequences for structure prediction

### Reference Sequences (Optional)
- **Location**: `data/reference_seqs.json`
- **Purpose**: Known sequences to check for duplicates (skips redundant predictions)

### Ground Truth Structures
- **Location**: `data/ground_truth/<set_name>/`
- **Structure**: 
  - `pdbs/` - Directory containing PDB/CIF files
  - `reference_seqs.json` - Reference sequences specific to this ground truth set
- **Example**: 
  - `data/ground_truth/set08/pdbs/*.pdb`
  - `data/ground_truth/set08/reference_seqs.json`
- **Purpose**: Known structures and sequences for comparison

## Output Files (Automatically Generated)

### Predicted Structures
- **Location**: `data/output/<run_name>/predicted_structures/`
- **Example**: `data/output/test_local/predicted_structures/*.pdb`

### Analysis Results
- **Location**: `data/output/<run_name>/analysis/`
- **Files**:
  - `analysis_results.json` - Detailed JSON format
  - `analysis_results.csv` - Spreadsheet format
  - `scientific_analysis.txt` - Human-readable analysis

### Logs
- **Central logs**: `logs/`
- **Run-specific logs**: `data/output/<run_name>/logs/`

## Example Directory Tree
```
progo-protein-evaluation-tm-plddt/
├── data/
│   ├── input/                    # Place your FASTA files here
│   │   ├── test_local.fasta
│   │   ├── set07_test.fasta
│   │   ├── set08_test.fasta
│   │   └── your_sequences.fasta
│   ├── ground_truth/             # Ground truth structures
│   │   ├── set07/
│   │   │   ├── pdbs/
│   │   │   │   └── *.pdb
│   │   │   └── reference_seqs.json
│   │   └── set08/
│   │       ├── pdbs/
│   │       │   └── *.pdb
│   │       └── reference_seqs.json
│   ├── output/                   # Auto-generated outputs
│   │   └── test_local/
│   │       ├── predicted_structures/
│   │       ├── analysis/
│   │       └── logs/
│   └── reference_seqs.json       # Optional global reference sequences (fallback)
└── logs/                         # Central logging
```

## Running Multiple Configurations

You can run the pipeline with different combinations of input FASTA files and ground truth sets:

### Example 1: Test set07 sequences against set07 ground truth
```bash
python -m src.main predict-and-evaluate --fasta set07_test.fasta --ground-truth-set set07
```
This will use `data/ground_truth/set07/reference_seqs.json` for duplicate checking.

### Example 2: Test set08 sequences against set08 ground truth
```bash
python -m src.main predict-and-evaluate --fasta set08_test.fasta --ground-truth-set set08
```
This will use `data/ground_truth/set08/reference_seqs.json` for duplicate checking.

### Example 3: Cross-evaluation (set07 sequences against set08 ground truth)
```bash
python -m src.main predict-and-evaluate --fasta set07_test.fasta --ground-truth-set set08
```
This allows you to see how sequences perform against different ground truth sets.

### Output Organization
Each run creates a unique output directory based on the input filename:
- `data/output/set07_test/` for set07_test.fasta
- `data/output/set08_test/` for set08_test.fasta
- `data/output/test_local_run1/`, `data/output/test_local_run2/`, etc. for repeated runs 
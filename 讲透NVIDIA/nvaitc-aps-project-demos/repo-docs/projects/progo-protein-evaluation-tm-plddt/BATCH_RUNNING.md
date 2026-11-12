# Batch Running Guide

This guide explains how to run multiple pipeline configurations easily.

## Quick Start

### Method 1: Interactive Selection (run_batch.py)
This script shows you available files and lets you choose:

```bash
python run_batch.py
```

Example interaction:
```
Available FASTA files:
  1. set07_test.fasta
  2. set08_test.fasta
  3. test_local.fasta

Available ground truth sets:
  1. set07
  2. set08

Enter the numbers of FASTA files to process (comma-separated, or 'all'):
> 1,2

Enter the numbers of ground truth sets to use (comma-separated, or 'all'):
> all
```

### Method 2: Command Line (run_simple.py)
Specify files directly on the command line:

```bash
# Single file, single ground truth
python run_simple.py test.fasta set08

# Multiple files/sets (comma-separated)
python run_simple.py "test1.fasta,test2.fasta" "set07,set08"

# All files against one ground truth
python run_simple.py ALL set08

# One file against all ground truths
python run_simple.py test.fasta ALL

# All combinations
python run_simple.py ALL ALL
```

### Comparing Results (compare_results.py)
After running multiple configurations:

```bash
python compare_results.py
```

This shows a table comparing all runs and identifies the best performing configurations.

## Adding New Files

1. **New FASTA files**: Place in `data/input/`
2. **New ground truth sets**: Create `data/ground_truth/<name>/` with:
   - `pdbs/` subdirectory containing PDB files
   - `reference_seqs.json` file for duplicate checking

The scripts automatically detect new files without any code changes needed! 
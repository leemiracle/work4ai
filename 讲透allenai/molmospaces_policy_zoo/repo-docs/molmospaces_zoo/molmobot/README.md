# MolmoBot-DROID

This implementation provides functionality for running MolmoBot-Droid on MolmoSpaces.

> [!NOTE]
> This is not the implementation used to collect the official results in the MolmoBot paper, and may not exactly reproduce those results.
> For better reproducibility, see the [MolmoBot repository](https://github.com/allenai/MolmoBot).

## Installation

```bash
pip install -e .[molmobot]
```

## Running with MolmoSpaces

```bash
python -m molmo_spaces.evaluation.eval_main molmospaces_zoo.molmobot.config:MolmoBotDroidEvalConfig --benchmark_dir <benchmark_path>
```

# DataDIVER

DataDIVER is a collection of Python utilities designed to support the discovery
of interpretable scientific models. The package is organized into two primary
modules:

1.  **Code Complexity Analysis (`code_metrics.py`)**: Metrics and scores to
    evaluate code complexity (e.g. for searching or evolving code models).
2.  **JAX-based Model Fitting (`jax_model_fitting.py`)**: Utilities for fitting
    and evaluating choice prediction models using JAX, optimized for speed with
    JIT compilation.

[![Unittests](https://github.com/google-deepmind/datadiver/actions/workflows/pytest_and_autopublish.yml/badge.svg)](https://github.com/google-deepmind/datadiver/actions/workflows/pytest_and_autopublish.yml)
[![PyPI version](https://badge.fury.io/py/datadiver.svg)](https://badge.fury.io/py/datadiver)

---

## Code Complexity Metrics (`code_metrics.py`)

This module provides tools for evaluating code complexity using standard AST
analysis and Halstead metrics.

### Public Functions

*   **`get_complexity_metrics(code: str)`**
    Computes raw complexity metrics for the given Python code string. Returned
    metrics include:
    *   `num_lines`: Total line count.
    *   `num_comments`: Number of comment lines (starting with `#`).
    *   `total_imports`: Number of imported symbols.
    *   `num_variables`: Number of variables.
    *   `halstead_vocab`, `halstead_size`, `halstead_volume`,
        `halstead_difficulty`, `halstead_effort`: Standard Halstead complexity
        metrics.

*   **`get_complexity_scores(code: str)`**
    Computes complexity scores normalized to the range `[0, 1]`. Scores are
    transformed such that higher values always represent *lower* complexity,
    making them suitable for optimization objectives.

*   **`normalize_metrics(raw_metrics: dict[str, Any])`**
    Normalizes raw metric values to `[0, 1]` based on empirical min/max ranges.

*   **`verify_num_params(agent_fun: str, n_params: int)`**
    Verifies that the number of parameters accessed by the agent function source
    code is at most `n_params`. Raises a `ValueError` if the function accesses
    more parameters than are available.

---

## Model Fitting (`jax_model_fitting.py`)

This module provides JIT-compiled optimization loops to fit agent parameters to
behavioral choice datasets.

### API Types

*   **`ChoicePredictionDataset` (dataclass)**
    Represents the dataset for model fitting.
    *   `inputs`: A dictionary mapping input names to JAX arrays (e.g. past
        choices, rewards).
    *   `next_choice`: An array of target choices to predict.
    *   `next_ignore`: A binary mask indicating trials to ignore during loss
        computation.

*   **`ChoicePredictionAgentFunction` (Protocol)**
    A protocol defining the interface for target agent models:
    ```python
    def __call__(
        self,
        *,
        params: chex.Array,
        agent_state: Any,
        **inputs: jax.typing.ArrayLike,
    ) -> tuple[chex.Array, Any]:
      ...
    ```
    Returns logits for the next choice and the updated internal agent state.

### Public Functions

*   **`make_choice_prediction_dataset(...)`**
    Helper function to format a raw data dictionary into a
    `ChoicePredictionDataset`. Shifts inputs by one trial so they represent
    past trial history.

*   **`split_choice_prediction_dataset(...)`**
    Splits a dataset into two halves (even-indexed and odd-indexed sessions) for
    cross-validation.

*   **`fit_choice_prediction_model(...)`**
    Fits agent parameters to a dataset. Uses a JIT-compiled optimization loop
    and executes multiple optimization restarts to avoid local minima.

*   **`evaluate_choice_prediction_model(...)`**
    Evaluates the choice prediction performance of an agent with given
    parameters on a dataset. Returns the normalized likelihood and predictions.

*   **`choice_prediction_twofold_crossvalidation(...)`**
    Performs even-odd two-fold cross-validation. Fits the model on one half of
    the dataset and evaluates it on the other half, returning the
    cross-validated normalized likelihood.

---

## License and disclaimer

Copyright 2026 DeepMind Technologies Limited

All software is licensed under the Apache License, Version 2.0 (Apache 2.0);
you may not use this file except in compliance with the Apache 2.0 license.
You may obtain a copy of the Apache 2.0 license at:
https://www.apache.org/licenses/LICENSE-2.0

All other materials are licensed under the Creative Commons Attribution 4.0
International License (CC-BY). You may obtain a copy of the CC-BY license at:
https://creativecommons.org/licenses/by/4.0/legalcode

Unless required by applicable law or agreed to in writing, all software and
materials distributed here under the Apache 2.0 or CC-BY licenses are
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the licenses for the specific language governing
permissions and limitations under those licenses.

*This is not an officially supported Google product.*

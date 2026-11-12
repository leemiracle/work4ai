<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/structured-data-models · page 3 Processing and Recipes · fetched 2026-10-26 -->

# Processing and Recipes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/images/ensemble_dark.svg](docs/source/images/ensemble_dark.svg)
- [docs/source/images/ensemble_light.svg](docs/source/images/ensemble_light.svg)
- [docs/source/images/pipeline_dark.svg](docs/source/images/pipeline_dark.svg)
- [docs/source/images/pipeline_light.svg](docs/source/images/pipeline_light.svg)
- [docs/source/processing.md](docs/source/processing.md)
- [sdm/processing/__init__.py](sdm/processing/__init__.py)
- [sdm/processing/numerical/__init__.py](sdm/processing/numerical/__init__.py)
- [sdm/processing/numerical/clip.py](sdm/processing/numerical/clip.py)
- [test/processing/test_contract.py](test/processing/test_contract.py)

</details>



The `sdm.processing` subsystem provides a composable, GPU-native pipeline framework for transforming structured data tables across model boundaries [docs/source/processing.md:3-3](). A {py:class}`~sdm.processing.recipe.Recipe` coordinates input feature preprocessing, target scaling and inverse transformation, and model output post-processing [docs/source/processing.md:22-24](). 

This page serves as a high-level parent overview of the processing and recipe architecture. For granular details, refer to the individual child sections linked below.

```mermaid
graph TD
    sub5 ["Natural Language Space"]
    sub6 ["Code Entity Space"]
    
    RawData["Raw Table Data"] --> RecipeFeatures["Feature Preprocessing"]
    RecipeFeatures --> ModelExec["Model Forward Pass"]
    ModelExec --> RecipeTarget["Target Inversion"]
    RecipeTarget --> RecipeOutput["Output Post-Processing"]
    
    sub5 -.-> sub6
    
    classDef default fill:#fff,stroke:#000,stroke-width:1px;
```
*Figure 1: High-level data flow through a processing recipe.*

**Sources:** `docs/source/processing.md:1-25`, `sdm/processing/__init__.py:1-55`

---

## 3.1. Processor Base Classes and Contracts

The foundational contract for all operations in `sdm.processing` is defined by the abstract base class `Processor` and its mixins [sdm/processing/__init__.py:6-10](). Processors manage state via `fit()`, transform tensors via `transform()`, and support device and dtype migration. State is serialized during checkpointing, and `InvertibleMixin` enables reversing transforms for tasks like target scaling.

For complete documentation on lifecycle methods, state save/load, and contract verification tests, see **[Processor Base Classes and Contracts](#3.1)**.

**Sources:** `sdm/processing/__init__.py:6-10`, `test/processing/test_contract.py:95-186`

---

## 3.2. Recipes and Execution Pipeline

A `Recipe` binds together `features`, `target`, and `output` processing pipelines [sdm/processing/__init__.py:54-54](). Execution is managed by dispatchers such as `StypeDispatch`, `TaskDispatch`, `TableDispatch`, and `Choice` [sdm/processing/__init__.py:17-21](). These route tensors to specific processors based on semantic types (`Stype`), machine learning tasks, or member tables within an ensemble.

```mermaid
graph TD
    "Recipe"["Recipe (sdm.processing.recipe.Recipe)"] --> "Features"["features: Processor"]
    "Recipe" --> "Target"["target: Processor"]
    "Recipe" --> "Output"["output: Processor"]
    
    "Features" --> "StypeDispatch"["StypeDispatch (sdm.processing.common.StypeDispatch)"]
    "Features" --> "TaskDispatch"["TaskDispatch (sdm.processing.common.TaskDispatch)"]
    
    classDef default fill:#fff,stroke:#000,stroke-width:1px;
```
*Figure 2: Structure of a Recipe and its dispatch mechanisms.*

For details on pipeline compilation, dispatcher logic, and series ensembles, see **[Recipes and Execution Pipeline](#3.2)**.

**Sources:** `sdm/processing/__init__.py:12-25`, `sdm/processing/recipe.py:1-50`, `docs/source/processing.md:53-74`

---

## 3.3. Numerical Processors

Numerical processors handle feature scaling, clipping, imputation, and dimensionality reduction on numerical tensor blocks (`Stype.numerical`). Available primitives include hard and saturated clamping (`Clip`, `ClipQuantiles`, `ClipSigma`), standardization (`Standardize`, `RobustScale`), mean and quantile imputation (`ImputeMean`), non-linear transformations (`PowerTransform`, `QuantileTransform`, `RankGaussian`), and linear projections (`PCA`, `RandomProjection`) [sdm/processing/numerical/__init__.py:6-22]().

For detailed mathematical formulations and implementation parameters, see **[Numerical Processors](#3.3)**.

**Sources:** `sdm/processing/numerical/__init__.py:6-22`, `sdm/processing/numerical/clip.py:14-35`

---

## 3.4. Categorical, Datetime, Text and Output Processors

Categorical and datetime processors handle discrete and temporal columns via alignment (`AlignCategories`), shuffling (`ShuffleCategories`), frequency encoding (`AddCategoryCounts`), mode imputation (`ImputeMode`), and calendar feature extraction (`AddCalendarFields`) [sdm/processing/__init__.py:46-52](). Text processors leverage `TFIDF` and `SentenceTransformer` [sdm/processing/__init__.py:26-26](). Output processors convert logits to probabilities (`Softmax`), sort quantile outputs (`SortQuantiles`), or aggregate ensemble estimates (`AverageEstimators`) [sdm/processing/__init__.py:53-53]().

For comprehensive usage guides on non-numerical processors, see **[Categorical, Datetime, Text and Output Processors](#3.4)**.

**Sources:** `sdm/processing/__init__.py:26-53`, `docs/source/processing.md:55-74`

---

## 3.5. Model Default Recipes

Foundation models such as `TabICLv2`, `TabFM`, `KumoTabular`, and `TimesFM3` define bespoke `default_recipe()` configurations [docs/source/processing.md:28-28](). These recipes compose specific chains of numerical, categorical, and output processors to match the expected input and output contracts of each model architecture.

```mermaid
graph TD
    "TabICLv2"["TabICLv2.default_recipe()"] --> "FeatProc"["Feature Pipeline"]
    "TabICLv2" --> "TargProc"["Target Pipeline"]
    "TabICLv2" --> "OutProc"["Output Pipeline"]
    
    "FeatProc" --> "ImputeMean"["ImputeMean"]
    "FeatProc" --> "Standardize"["Standardize"]
    
    classDef default fill:#fff,stroke:#000,stroke-width:1px;
```
*Figure 3: Default recipe composition for model boundaries.*

For per-model recipe implementations and customization patterns, see **[Model Default Recipes](#3.5)**.

**Sources:** `docs/source/processing.md:28-47`, `test/processing/test_contract.py:110-175`

---


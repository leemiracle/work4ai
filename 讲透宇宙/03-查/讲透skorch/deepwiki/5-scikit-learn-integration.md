<!-- source: DeepWiki mcp.deepwiki.com · repo skorch-dev/skorch · page 5 Scikit-learn Integration · fetched 2026-10-21 -->

# Scikit-learn Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/testing.yml](.github/workflows/testing.yml)
- [README.rst](README.rst)
- [docs/user/FAQ.rst](docs/user/FAQ.rst)
- [docs/user/callbacks.rst](docs/user/callbacks.rst)
- [docs/user/dataset.rst](docs/user/dataset.rst)
- [docs/user/installation.rst](docs/user/installation.rst)
- [docs/user/neuralnet.rst](docs/user/neuralnet.rst)
- [skorch/helper.py](skorch/helper.py)
- [skorch/tests/test_helper.py](skorch/tests/test_helper.py)

</details>



## Purpose and Scope

This document explains how skorch integrates with scikit-learn's ecosystem, enabling PyTorch neural networks to be used seamlessly with sklearn's tools for hyperparameter tuning, pipelines, and cross-validation. For details on individual integration components, see:
- API compatibility methods: [5.1](#5.1)
- Helper classes for data compatibility: [5.2](#5.2)
- Practical examples with sklearn tools: [5.3](#5.3)
- Parameter naming conventions: [5.4](#5.4)

## Integration Architecture

The following diagram shows how skorch bridges PyTorch and scikit-learn through three integration layers:

```mermaid
graph TB
    subgraph sklearn["sklearn Ecosystem"]
        GridSearchCV["GridSearchCV<br/>(param search)"]
        Pipeline["Pipeline<br/>(workflow)"]
        cross_val["cross_val_score<br/>(validation)"]
    end
    
    subgraph skorch_api["skorch API Layer"]
        fit["fit(X, y)<br/>partial_fit(X, y)"]
        predict["predict(X)<br/>predict_proba(X)"]
        score["score(X, y)"]
        params["get_params()<br/>set_params(**params)"]
    end
    
    subgraph skorch_helpers["skorch Helper Layer"]
        SliceDict["SliceDict<br/>(dict slicing)"]
        SliceDataset["SliceDataset<br/>(dataset wrapping)"]
        DataFrameTransformer["DataFrameTransformer<br/>(pandas support)"]
        predefined_split["predefined_split<br/>(validation control)"]
    end
    
    subgraph pytorch["PyTorch Backend"]
        Module["torch.nn.Module"]
        DataLoader["torch.utils.data.DataLoader"]
        Tensor["torch.Tensor"]
    end
    
    GridSearchCV --> fit
    Pipeline --> fit
    Pipeline --> predict
    cross_val --> fit
    cross_val --> predict
    cross_val --> score
    
    fit --> Module
    predict --> Module
    score --> Module
    params --> Module
    
    SliceDict --> GridSearchCV
    SliceDataset --> GridSearchCV
    DataFrameTransformer --> Pipeline
    predefined_split --> fit
    
    Module --> Tensor
    fit --> DataLoader
    predict --> DataLoader
```

Sources: [README.rst:83-114](), [docs/user/FAQ.rst:58-83](), [skorch/helper.py:1-535]()

## Core Integration Mechanisms

### sklearn Estimator API Implementation

The `NeuralNet` base class implements sklearn's estimator interface, providing compatibility with all sklearn tools:

```mermaid
graph LR
    subgraph sklearn_interface["sklearn Estimator Interface"]
        BaseEstimator["BaseEstimator"]
    end
    
    subgraph skorch_classes["skorch Classes"]
        NeuralNet["NeuralNet<br/>skorch/net.py"]
        NeuralNetClassifier["NeuralNetClassifier<br/>skorch/classifier.py"]
        NeuralNetRegressor["NeuralNetRegressor<br/>skorch/regressor.py"]
    end
    
    subgraph methods["Required Methods"]
        fit_method["fit(X, y)<br/>→ self"]
        predict_method["predict(X)<br/>→ y_pred"]
        get_params_method["get_params(deep=True)<br/>→ dict"]
        set_params_method["set_params(**params)<br/>→ self"]
        score_method["score(X, y)<br/>→ float"]
    end
    
    BaseEstimator -.->|"requires"| methods
    NeuralNet -.->|"implements"| methods
    NeuralNet --> NeuralNetClassifier
    NeuralNet --> NeuralNetRegressor
```

| Method | Purpose | Returns | Notes |
|--------|---------|---------|-------|
| `fit(X, y)` | Train model from scratch | `self` | Initializes if needed, trains for `max_epochs` |
| `partial_fit(X, y)` | Continue training | `self` | Does not re-initialize, useful for incremental learning |
| `predict(X)` | Generate predictions | `numpy.ndarray` | For classifiers, returns class labels |
| `predict_proba(X)` | Generate probabilities | `numpy.ndarray` | Available for classifiers |
| `score(X, y)` | Evaluate model | `float` | Accuracy for classifiers, R² for regressors |
| `get_params(deep=True)` | Get all parameters | `dict` | Includes nested parameters |
| `set_params(**params)` | Set parameters | `self` | Supports double-underscore notation |

Sources: [docs/user/neuralnet.rst:1-421](), [README.rst:72-114]()

### Behavioral Alignment with sklearn

skorch provides specific parameters and behaviors to ensure compatibility with sklearn workflows:

```mermaid
graph TB
    subgraph behaviors["Behavioral Alignment"]
        train_split["train_split=None<br/>(disable internal validation)"]
        warm_start["warm_start=True<br/>(continue training)"]
        verbose["verbose=0<br/>(suppress output)"]
        double_underscore["module__param=value<br/>(nested parameters)"]
    end
    
    subgraph use_cases["Use Cases"]
        cv["Cross-Validation<br/>(GridSearchCV, cross_val_score)"]
        pipeline["Pipeline Integration"]
        incremental["Incremental Learning"]
        hyperopt["Hyperparameter Tuning"]
    end
    
    train_split --> cv
    verbose --> cv
    double_underscore --> hyperopt
    warm_start --> incremental
    double_underscore --> pipeline
```

Key behavioral features:

| Feature | Parameter | Purpose | Example |
|---------|-----------|---------|---------|
| Disable internal validation | `train_split=None` | Let sklearn handle splitting | Used with `GridSearchCV` |
| Continue training | `warm_start=True` | Don't re-initialize on `fit()` | Multiple `fit()` calls |
| Suppress output | `verbose=0` | Quiet training | Grid search with many fits |
| Nested parameters | `module__<param>` | Access sub-component params | `module__num_units=10` |

Sources: [README.rst:104-114](), [docs/user/neuralnet.rst:282-293](), [docs/user/FAQ.rst:24-35]()

## Data Compatibility Helpers

skorch provides helper classes to bridge data format gaps between sklearn and PyTorch:

### SliceDict - Dictionary Slicing Support

The `SliceDict` class enables dictionaries to work with sklearn tools that expect array-like slicing:

```mermaid
graph LR
    subgraph input["Input Data"]
        dict_input["Python dict<br/>{key: array}"]
    end
    
    subgraph helper["SliceDict Helper<br/>skorch/helper.py:33-149"]
        SliceDict_class["SliceDict(**kwargs)"]
        getitem["__getitem__(slice)"]
        len["__len__()"]
        shape["shape property"]
    end
    
    subgraph sklearn_ops["sklearn Operations"]
        split["train_test_split"]
        cv_split["CV splitter"]
        indexing["Array indexing"]
    end
    
    dict_input --> SliceDict_class
    SliceDict_class --> len
    SliceDict_class --> getitem
    SliceDict_class --> shape
    
    len --> sklearn_ops
    getitem --> sklearn_ops
    shape --> sklearn_ops
```

Key characteristics:
- Wraps a dictionary of arrays with equal first dimension
- Supports slicing across all values simultaneously
- Cannot be indexed by single integers (use `[i:i+1]` instead)
- Preserves dictionary keys during slicing
- Compatible with numpy arrays and torch tensors as values

Sources: [skorch/helper.py:33-149](), [docs/user/FAQ.rst:58-68]()

### SliceDataset - PyTorch Dataset Wrapping

The `SliceDataset` class wraps PyTorch datasets for sklearn compatibility:

```mermaid
graph TB
    subgraph pytorch["PyTorch Data"]
        Dataset["torch.utils.data.Dataset"]
    end
    
    subgraph wrapper["SliceDataset Wrapper<br/>skorch/helper.py:153-269"]
        SliceDataset_class["SliceDataset(dataset, idx=0)"]
        lazy_slicing["Lazy slicing behavior"]
        subset_behavior["Returns SliceDataset on slice"]
        value_behavior["Returns actual value on int"]
    end
    
    subgraph sklearn_tools["sklearn Tools"]
        GridSearchCV_use["GridSearchCV<br/>(creates splits)"]
        cross_val_use["cross_val_score<br/>(creates folds)"]
    end
    
    Dataset --> SliceDataset_class
    SliceDataset_class --> lazy_slicing
    lazy_slicing --> subset_behavior
    lazy_slicing --> value_behavior
    
    subset_behavior --> GridSearchCV_use
    value_behavior --> GridSearchCV_use
    
    subset_behavior --> cross_val_use
    value_behavior --> cross_val_use
```

Important behavior:
- Returns `SliceDataset` when sliced (not actual data)
- Only loads data when indexed by integer
- Prevents loading entire dataset into memory during splitting
- Supports `idx` parameter to select X or y from dataset tuples
- Can apply transformations via `transform()` method

Sources: [skorch/helper.py:153-269](), [docs/user/FAQ.rst:70-83]()

### DataFrameTransformer - Pandas Integration

The `DataFrameTransformer` converts pandas DataFrames to dictionary format suitable for skorch:

```mermaid
graph TB
    subgraph pandas_data["Pandas Data"]
        DataFrame["pd.DataFrame<br/>(mixed types)"]
        float_cols["Float columns"]
        int_cols["Integer columns"]
        cat_cols["Categorical columns"]
    end
    
    subgraph transformer["DataFrameTransformer<br/>skorch/helper.py:288-534"]
        fit_transform["fit_transform(df)"]
        concat_floats["Concatenate floats → 'X'"]
        encode_cats["Encode categoricals → keys"]
    end
    
    subgraph output["Output Dictionary"]
        X_key["'X': float array"]
        cat_keys["'col_name': int arrays"]
    end
    
    subgraph module["Module Forward"]
        forward["forward(X, col_name, ...)"]
    end
    
    DataFrame --> float_cols
    DataFrame --> int_cols
    DataFrame --> cat_cols
    
    float_cols --> fit_transform
    int_cols --> fit_transform
    cat_cols --> fit_transform
    
    fit_transform --> concat_floats
    fit_transform --> encode_cats
    
    concat_floats --> X_key
    encode_cats --> cat_keys
    
    X_key --> forward
    cat_keys --> forward
```

Configuration options:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `treat_int_as_categorical` | `False` | Treat integers like categorical |
| `float_dtype` | `np.float32` | Cast float arrays to this dtype |
| `int_dtype` | `np.int64` | Cast categorical encodings to this dtype |

The transformer's `describe_signature()` method helps design module signatures by analyzing the required input dimensions.

Sources: [skorch/helper.py:288-534](), [skorch/tests/test_helper.py:557-782]()

### predefined_split - Custom Validation Sets

The `predefined_split()` function allows using pre-defined validation datasets:

```mermaid
graph LR
    subgraph data_prep["Data Preparation"]
        train_ds["Training Dataset"]
        valid_ds["Validation Dataset"]
    end
    
    subgraph predefined["predefined_split<br/>skorch/helper.py:271-285"]
        wrap["predefined_split(valid_ds)"]
        split_func["Returns split function"]
    end
    
    subgraph neuralnet["NeuralNet"]
        train_split_param["train_split=<func>"]
        fit_call["fit(train_ds)"]
    end
    
    valid_ds --> wrap
    wrap --> split_func
    split_func --> train_split_param
    train_ds --> fit_call
    train_split_param --> fit_call
```

This is particularly useful when:
- Data is already split (e.g., via `train_test_split`)
- Validation set has specific requirements
- Using predefined fold assignments

Sources: [skorch/helper.py:271-285](), [docs/user/FAQ.rst:135-173]()

## Integration with sklearn Tools

### GridSearchCV Integration

The following diagram shows the complete flow when using skorch with `GridSearchCV`:

```mermaid
sequenceDiagram
    participant User
    participant GridSearchCV
    participant NeuralNet
    participant Module
    
    User->>NeuralNet: set_params(train_split=None, verbose=0)
    User->>GridSearchCV: GridSearchCV(net, param_grid)
    User->>GridSearchCV: fit(X, y)
    
    loop For each param combination
        loop For each CV fold
            GridSearchCV->>NeuralNet: fit(X_train_fold, y_train_fold)
            NeuralNet->>NeuralNet: initialize() (if needed)
            NeuralNet->>Module: Train for max_epochs
            Module-->>NeuralNet: Training complete
            NeuralNet-->>GridSearchCV: self
            
            GridSearchCV->>NeuralNet: score(X_valid_fold, y_valid_fold)
            NeuralNet->>Module: predict(X_valid_fold)
            Module-->>NeuralNet: predictions
            NeuralNet-->>GridSearchCV: score
        end
    end
    
    GridSearchCV-->>User: best_params_, best_score_
```

Example configuration for grid search:

```python
# From README.rst:98-114
net.set_params(train_split=False, verbose=0)  # Critical settings
params = {
    'lr': [0.01, 0.02],
    'max_epochs': [10, 20],
    'module__num_units': [10, 20],  # Double-underscore for nested params
}
gs = GridSearchCV(net, params, refit=False, cv=3, scoring='accuracy')
```

Key considerations:
- Set `train_split=None` or `train_split=False` to disable internal validation
- Set `verbose=0` to suppress output during many fits
- Use `refit=False` if you only want to find best params without final training
- Use double-underscore notation for module parameters

Sources: [README.rst:98-114](), [docs/user/FAQ.rst:58-68](), [skorch/tests/test_helper.py:164-178]()

### Pipeline Integration

skorch networks work seamlessly in sklearn pipelines:

```mermaid
graph TB
    subgraph pipeline["sklearn Pipeline"]
        step1["Step 1:<br/>StandardScaler"]
        step2["Step 2:<br/>PCA"]
        step3["Step 3:<br/>NeuralNetClassifier"]
    end
    
    subgraph data_flow["Data Flow"]
        input["X, y"]
        scaled["Scaled X"]
        reduced["Reduced X"]
        output["Predictions"]
    end
    
    subgraph methods["Pipeline Methods"]
        fit_pipeline["pipeline.fit(X, y)"]
        predict_pipeline["pipeline.predict(X)"]
        score_pipeline["pipeline.score(X, y)"]
    end
    
    input --> step1
    step1 --> scaled
    scaled --> step2
    step2 --> reduced
    reduced --> step3
    step3 --> output
    
    fit_pipeline -.-> step1
    fit_pipeline -.-> step2
    fit_pipeline -.-> step3
    
    predict_pipeline -.-> step1
    predict_pipeline -.-> step2
    predict_pipeline -.-> step3
```

Example with `DataFrameTransformer`:

```python
# From README.rst:87-96 and skorch/tests/test_helper.py:733-748
pipe = Pipeline([
    ('scale', StandardScaler()),
    ('net', net),
])
pipe.fit(X, y)
y_proba = pipe.predict_proba(X)
```

With DataFrame transformation:

```python
# From skorch/tests/test_helper.py:733-748
pipe = Pipeline([
    ('transform', DataFrameTransformer()),
    ('net', net),
])
pipe.fit(df, y)  # df is a pandas DataFrame
```

Sources: [README.rst:87-96](), [skorch/tests/test_helper.py:733-748]()

### Cross-Validation Integration

Using skorch with sklearn's cross-validation functions:

```mermaid
graph TB
    subgraph cv_tools["Cross-Validation Tools"]
        cross_val_score["cross_val_score(net, X, y, cv=5)"]
        cross_val_predict["cross_val_predict(net, X, y, cv=5)"]
    end
    
    subgraph configuration["Required Configuration"]
        train_split_none["train_split=None<br/>(use CV split only)"]
        verbose_zero["verbose=0<br/>(suppress per-fold output)"]
    end
    
    subgraph execution["Execution"]
        fold1["Fold 1: fit + score"]
        fold2["Fold 2: fit + score"]
        fold3["Fold 3: fit + score"]
        fold4["Fold 4: fit + score"]
        fold5["Fold 5: fit + score"]
    end
    
    train_split_none --> cross_val_score
    verbose_zero --> cross_val_score
    
    cross_val_score --> fold1
    cross_val_score --> fold2
    cross_val_score --> fold3
    cross_val_score --> fold4
    cross_val_score --> fold5
```

Example usage:

```python
# From docs/user/dataset.rst:49-58
net = NeuralNetClassifier(
    module=MyModule,
    train_split=None,  # Critical: use CV split only
)

from sklearn.model_selection import cross_val_predict
y_pred = cross_val_predict(net, X, y, cv=5)
```

Sources: [docs/user/dataset.rst:49-58](), [docs/user/FAQ.rst:70-83]()

## Parameter Passing and Configuration

### Double-Underscore Notation

skorch uses sklearn's double-underscore (`__`) notation to access nested parameters:

```mermaid
graph TB
    subgraph notation["Parameter Notation"]
        module_param["module__num_units=100"]
        optimizer_param["optimizer__weight_decay=0.01"]
        criterion_param["criterion__weight=weights"]
        callback_param["callbacks__cp__monitor='valid_acc'"]
        iterator_param["iterator_train__shuffle=True"]
    end
    
    subgraph components["NeuralNet Components"]
        module["module_"]
        optimizer["optimizer_"]
        criterion["criterion_"]
        callbacks["callbacks_"]
        iterator["iterator_train_"]
    end
    
    module_param --> module
    optimizer_param --> optimizer
    criterion_param --> criterion
    callback_param --> callbacks
    iterator_param --> iterator
```

Common parameter patterns:

| Pattern | Component | Example | Purpose |
|---------|-----------|---------|---------|
| `module__*` | PyTorch module | `module__num_units=10` | Configure module architecture |
| `optimizer__*` | Optimizer | `optimizer__weight_decay=0.01` | Configure optimization |
| `criterion__*` | Loss function | `criterion__reduction='sum'` | Configure loss computation |
| `callbacks__<name>__*` | Specific callback | `callbacks__cp__monitor='valid_loss'` | Configure callback behavior |
| `iterator_train__*` | Training DataLoader | `iterator_train__shuffle=True` | Configure data loading |
| `iterator_valid__*` | Validation DataLoader | `iterator_valid__batch_size=256` | Configure validation batching |

Sources: [docs/user/neuralnet.rst:69-90](), [docs/user/neuralnet.rst:503-526](), [docs/user/FAQ.rst:8-21]()

### Virtual Parameters

Some parameters in skorch are "virtual" shortcuts that map to underlying component parameters:

```mermaid
graph LR
    subgraph virtual["Virtual Parameters"]
        lr["lr=0.01"]
        batch_size["batch_size=128"]
    end
    
    subgraph actual["Actual Parameters"]
        optimizer_lr["optimizer__lr=0.01"]
        train_batch["iterator_train__batch_size=128"]
        valid_batch["iterator_valid__batch_size=128"]
    end
    
    lr -.->|"maps to"| optimizer_lr
    batch_size -.->|"maps to"| train_batch
    batch_size -.->|"maps to"| valid_batch
```

Virtual parameter mapping:

| Virtual | Maps To | Notes |
|---------|---------|-------|
| `lr` | `optimizer__lr` | If both set, `optimizer__lr` takes precedence |
| `batch_size` | `iterator_train__batch_size`, `iterator_valid__batch_size` | Sets both iterators at once |

This provides convenience while maintaining full control through explicit parameters.

Sources: [docs/user/neuralnet.rst:158-194]()

### Parameter Access Methods

The following methods enable parameter introspection and modification:

```mermaid
graph TB
    subgraph methods["Parameter Methods"]
        get_params["get_params(deep=True)"]
        set_params["set_params(**params)"]
    end
    
    subgraph operations["Operations"]
        introspection["Parameter introspection"]
        modification["Parameter modification"]
        cloning["Object cloning"]
        grid_search["Grid search"]
    end
    
    subgraph behavior["Behavior"]
        deep_true["deep=True → recursive dict"]
        deep_false["deep=False → top-level only"]
        reinit["set_params → re-initialize if needed"]
    end
    
    get_params --> introspection
    get_params --> cloning
    get_params --> deep_true
    get_params --> deep_false
    
    set_params --> modification
    set_params --> grid_search
    set_params --> reinit
```

Key behaviors:
- `get_params(deep=True)` returns all parameters including nested ones
- `set_params()` returns `self` for method chaining
- Setting parameters may trigger re-initialization
- Used internally by sklearn's `clone()` function

Sources: [docs/user/neuralnet.rst:63-67](), [docs/user/callbacks.rst:92-106]()

## Complete Integration Example

The following example demonstrates multiple integration features working together:

```python
# From README.rst:44-114 and test files

import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from torch import nn
from skorch import NeuralNetClassifier
from skorch.helper import SliceDict

# Prepare data as dictionary
X, y = make_classification(1000, 20, n_informative=10, random_state=0)
X = SliceDict(X=X.astype(np.float32))  # Wrap for sklearn compatibility

# Define module
class MyModule(nn.Module):
    def __init__(self, num_units=10):
        super().__init__()
        self.dense0 = nn.Linear(20, num_units)
        self.output = nn.Linear(num_units, 2)
    
    def forward(self, X):  # Matches SliceDict key
        X = nn.functional.relu(self.dense0(X))
        return nn.functional.softmax(self.output(X), dim=-1)

# Create pipeline
net = NeuralNetClassifier(
    MyModule,
    max_epochs=10,
    lr=0.1,
    iterator_train__shuffle=True,  # Double-underscore for nested param
)

pipe = Pipeline([
    ('scale', StandardScaler()),
    ('net', net),
])

# Grid search with cross-validation
pipe.set_params(net__train_split=None, net__verbose=0)  # Configure for CV
params = {
    'net__lr': [0.01, 0.1],
    'net__module__num_units': [10, 20],
}
gs = GridSearchCV(pipe, params, cv=3, scoring='accuracy')
gs.fit(X, y)

print(f"Best score: {gs.best_score_:.3f}")
print(f"Best params: {gs.best_params_}")
```

This example shows:
1. Using `SliceDict` for dictionary data compatibility
2. Double-underscore notation for nested parameters
3. Integration with `Pipeline`
4. Integration with `GridSearchCV`
5. Proper configuration for cross-validation

Sources: [README.rst:44-114](), [skorch/tests/test_helper.py:164-178]()

## Common Integration Patterns

### Pattern: Disable Internal Validation for CV

When using sklearn cross-validation tools, disable skorch's internal train/validation split:

```python
net = NeuralNetClassifier(
    module=MyModule,
    train_split=None,  # or train_split=False
    verbose=0,
)
```

### Pattern: Dictionary Input with GridSearchCV

When using dictionary inputs, wrap with `SliceDict`:

```python
from skorch.helper import SliceDict

X_dict = {'input': X_array}
X_sliceable = SliceDict(**X_dict)
gs.fit(X_sliceable, y)
```

### Pattern: Dataset Input with GridSearchCV

When using PyTorch datasets, wrap with `SliceDataset`:

```python
from skorch.helper import SliceDataset

ds = MyPyTorchDataset(...)
ds_sliceable = SliceDataset(ds, idx=0)  # idx=0 for X, idx=1 for y
gs.fit(ds_sliceable, y)
```

### Pattern: Pre-defined Validation Split

When you have a specific validation set:

```python
from skorch.helper import predefined_split
from skorch.dataset import Dataset

valid_ds = Dataset(X_valid, y_valid)
net = NeuralNetClassifier(
    module=MyModule,
    train_split=predefined_split(valid_ds),
)
net.fit(X_train, y_train)
```

### Pattern: DataFrames in Pipeline

When working with pandas DataFrames:

```python
from skorch.helper import DataFrameTransformer

pipe = Pipeline([
    ('transform', DataFrameTransformer()),
    ('net', net),
])
pipe.fit(df, y)
```

Sources: [docs/user/FAQ.rst:58-173](), [skorch/helper.py:271-285]()

---


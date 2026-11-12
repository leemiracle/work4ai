<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/neural_lns · extra page Residual Dropout and Layer Norm Wrapper · fetched 2026-10-26 -->

# Residual Dropout and Layer Norm Wrapper

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [layer_norm.py](layer_norm.py)

</details>



This page documents the `ResidualDropoutWrapper` class implemented in `layer_norm.py`, which provides a Sonnet-based wrapper combining residual connections, conditional dropout, and layer normalization for graph neural network layers and other architectures.

## Purpose and Scope

The `ResidualDropoutWrapper` encapsulates standard neural network regularization and structural patterns. It wraps an arbitrary inner Sonnet module (`snt.Module`) and automatically applies:
1. The inner module computation on given inputs.
2. Conditional dropout during training.
3. Residual (skip) connection addition using either standard inputs or designated query inputs.
4. Optional layer normalization along the feature axis.

Sources: [layer_norm.py:15-68]()

---

## Class Architecture and Initialization

The `ResidualDropoutWrapper` inherits from `snt.Module` [layer_norm.py:21-21](). Its constructor `__init__` sets up the inner layer and configures the layer normalization operator if requested.

### Constructor Parameters

- `layer`: The inner module to wrap (e.g., a GNN layer or message passing block) [layer_norm.py:28-28]().
- `dropout_rate`: The float rate for dropout. A value of `0.0` disables dropout [layer_norm.py:29-29]().
- `apply_layer_norm`: A boolean (default `True`) determining whether to apply layer normalization after the residual addition [layer_norm.py:30-31]().
- `name`: Optional name string for the Sonnet module [layer_norm.py:32-32]().

If `apply_layer_norm` is enabled, the wrapper instantiates a Sonnet LayerNorm layer configured to normalize over the last axis (`axis=-1`) with scale and offset parameters enabled [layer_norm.py:40-43]().

```mermaid
graph TD
    A["ResidualDropoutWrapper.__init__"] --> B["snt.Module"]
    A --> C["self._layer"]
    A --> D["self._dropout_rate"]
    A --> E{self._apply_layer_norm}
    E -- True --> F["snt.LayerNorm(axis=-1, create_scale=True, create_offset=True)"]
    E -- False --> G["Skip LayerNorm"]

    sub: "Code Entity Space"
    class A,B,C,D,E,F,G codeNode;
```

Sources: [layer_norm.py:21-43]()

---

## Forward Computation and Data Flow

The forward pass is executed via the `__call__` method [layer_norm.py:44-68](). It processes inputs through a structured sequence of operations.

### Execution Steps

1. **Inner Layer Execution**: Computes initial `outputs` by passing `inputs`, along with any additional `*args` and `**kwargs`, to `self._layer` [layer_norm.py:54-54]().
2. **Conditional Dropout**: Checks `kwargs.get('is_training', False)`. If true, applies `tf.nn.dropout` using `self._dropout_rate` [layer_norm.py:57-58]().
3. **Residual Addition**: 
   - If `'query_inputs'` is present in `kwargs`, adds `kwargs['query_inputs']` to `outputs` [layer_norm.py:60-61]().
   - Otherwise, performs a standard residual connection by adding the primary `inputs` to `outputs` [layer_norm.py:62-63]().
4. **Layer Normalization**: If `self._apply_layer_norm` is enabled, passes the summed tensor through `self._layer_norm` [layer_norm.py:65-66]().
5. **Return**: Returns the finalized tensor [layer_norm.py:68-68]().

```mermaid
graph TD
    H["Inputs & Kwargs"] --> I["self._layer(inputs, *args, **kwargs)"]
    I --> J{is_training?}
    J -- True --> K["tf.nn.dropout(outputs, rate=self._dropout_rate)"]
    J -- False --> L["Bypass Dropout"]
    K --> M{query_inputs in kwargs?}
    L --> M
    M -- True --> N["outputs += kwargs['query_inputs']"]
    M -- False --> O["outputs += inputs"]
    N --> P{self._apply_layer_norm?}
    O --> P
    P -- True --> Q["self._layer_norm(outputs)"]
    P -- False --> R["Return outputs"]
    Q --> R

    sub: "Data Flow Space"
    class H,I,J,K,L,M,N,O,P,Q,R codeNode;
```

Sources: [layer_norm.py:44-68]()

---


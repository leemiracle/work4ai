<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/limit · page 3 Free Embedding Experiments · fetched 2026-10-26 -->

# Free Embedding Experiments

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [code/free_embedding_experiment.py](code/free_embedding_experiment.py)

</details>



This document covers the free embedding experiment system designed to find the theoretical limits of embedding-based retrieval. The system conducts optimization experiments to determine the critical N value - the maximum number of documents that can be successfully retrieved for a given embedding dimension and relevance structure. 

For information about the LIMIT dataset used in these experiments, see [LIMIT Dataset](#2). For details about the computational infrastructure and JAX optimization stack, see [Computational Infrastructure](#3.2).

## Purpose and Core Concept

The free embedding experiment system implements a search algorithm to find the "critical N" - the maximum number of documents N for which embeddings of dimension d can achieve perfect retrieval accuracy when each query has exactly k relevant documents. This validates theoretical limitations of embedding-based retrieval by finding the empirical breaking point through unconstrained optimization.

The system uses InfoNCE loss with full-batch training to learn optimal query and document embeddings, testing whether perfect retrieval is achievable for specific parameter combinations.

Sources: [code/free_embedding_experiment.py:16-37](), [README.md:46-47]()

## Critical N Search Algorithm

The search process uses a three-phase algorithm implemented in `_run_critical_n_search_for_config` to efficiently locate the critical N value:

### Multi-Phase Search Strategy

```mermaid
graph TD
    subgraph "Phase 1: Galloping Search"
        A[start_with_initial_n] --> B["evaluate_n(initial_n)"]
        B --> C{"accuracy >= 1.0?"}
        C -->|Yes| D["gallop_up: n_low = initial_n<br/>step = 1"]
        C -->|No| E["gallop_down: n_high = initial_n<br/>step = 1"]
        D --> F["n_test = n_low + step"]
        F --> G{"evaluate_n(n_test) >= 1.0?"}
        G -->|Yes| H["n_low = n_test<br/>step *= 2"]
        G -->|No| I["n_high = n_test<br/>break"]
        H --> F
        E --> J["n_test = max(n_high - step, 1)"]
        J --> K{"evaluate_n(n_test) < 1.0?"}
        K -->|Yes| L["n_high = n_test<br/>step *= 2"]
        K -->|No| M["n_low = n_test<br/>break"]
        L --> J
        I --> N["Phase 2: Binary Search"]
        M --> N
    end
    
    subgraph "Phase 2: Binary Search"
        N --> O["low = n_low, high = n_high"]
        O --> P["mid = (low + high) // 2"]
        P --> Q{"evaluate_n(mid) >= 1.0?"}
        Q -->|Yes| R["critical_n = mid<br/>low = mid + 1"]
        Q -->|No| S["high = mid - 1"]
        R --> T{"low <= high?"}
        S --> T
        T -->|Yes| P
        T -->|No| U["Phase 3: Sweep"]
    end
    
    subgraph "Phase 3: Fine-grained Sweep"
        U --> V["for offset in range(-4, 6)"]
        V --> W["evaluate_n(critical_n + offset)"]
        W --> X["Complete neighborhood exploration"]
    end
```

Sources: [code/free_embedding_experiment.py:576-676]()

### Evaluation Function

The `_evaluate_n` function handles experiment execution and result caching:

| Component | Function | Implementation |
|-----------|----------|----------------|
| **Signature-based Caching** | `get_params_signature` | Avoids redundant computation by checking processed signatures |
| **Experiment Execution** | `_process_experiment_and_save` | Runs single experiment and saves results incrementally |
| **Accuracy Selection** | `_pick_best_accuracy` | Chooses best accuracy signal from multiple metrics |

Sources: [code/free_embedding_experiment.py:602-625](), [code/free_embedding_experiment.py:591-600]()

## Experiment Execution Framework

### Single Experiment Workflow

```mermaid
graph TD
    subgraph "run_experiment_base"
        A["extract n, d, k, seed"] --> B["create_combinatorial_qrels(n, k)"]
        B --> C{"qrels generated?"}
        C -->|No| D["return_no_qrels_error_result"]
        C -->|Yes| E["get_device_context(device)"]
        E --> F["optimize_embeddings(experiment_data, params)"]
        F --> G["return experiment results"]
    end
    
    subgraph "create_combinatorial_qrels"
        H["itertools.combinations(range(n), k)"] --> I{"q_limit specified?"}
        I -->|Yes| J["rng.choice(combinations, q_limit)"]
        I -->|No| K["use all combinations"]
        J --> L["qrels_dict = {i: set(combo)}"]
        K --> L
    end
    
    subgraph "optimize_embeddings"
        M["initialize_embeddings(q, n, d)"] --> N["optax.adam(learning_rate)"]
        N --> O["convert_qrels_to_jax_matrix"]
        O --> P["make_jax_update(optimizer, temperature)"]
        P --> Q["training loop with early stopping"]
        Q --> R["evaluate_top_k_accuracy"]
    end
    
    B --> H
    F --> M
```

Sources: [code/free_embedding_experiment.py:496-535](), [code/free_embedding_experiment.py:123-151](), [code/free_embedding_experiment.py:363-493]()

### JAX Optimization Pipeline

The core optimization uses JAX for GPU-accelerated training with InfoNCE loss:

```mermaid
graph LR
    subgraph "initialize_embeddings"
        A["jax.random.normal(key_q, (q, d))"] --> B["jax.random.normal(key_d, (n, d))"]
        B --> C["L2 normalize embeddings"]
        C --> D["jax.device_put(embeddings, device)"]
    end
    
    subgraph "make_jax_update"
        E["@jax.jit decorator"] --> F["jax_loss_fn(q_embeds, d_embeds, relevance_matrix)"]
        F --> G["jax.value_and_grad(loss_wrapper)"]
        G --> H["optimizer.update(grads, opt_state, params)"]
        H --> I["optax.apply_updates(params, updates)"]
        I --> J["L2 normalize after update"]
    end
    
    subgraph "jax_loss_fn"
        K["logits = dot(q_embeds, d_embeds.T) / temperature"] --> L["jax.nn.log_softmax(logits, axis=1)"]
        L --> M["mask = relevance_matrix.astype(log_probs.dtype)"]
        M --> N["sum_pos_log_probs = sum(log_probs * mask)"]
        N --> O["return -sum_pos_log_probs / num_pos"]
    end
    
    D --> E
    J --> K
```

Sources: [code/free_embedding_experiment.py:348-360](), [code/free_embedding_experiment.py:279-311](), [code/free_embedding_experiment.py:250-276]()

## Configuration and Command-Line Interface

### Core Parameters

The experiment system uses `absl.flags` for configuration management:

| Flag | Type | Purpose | Default |
|------|------|---------|---------|
| `--d` | integer | Embedding dimension | Required |
| `--k` | integer | Relevant documents per query | Required |
| `--enable_critical_n_search` | integer | Starting N for search | Required |
| `--results_output_path` | string | JSON output path | None |
| `--device` | string | Compute device (gpu/tpu/cpu) | "gpu" |
| `--learning_rate` | float | Optimizer learning rate | 0.01 |
| `--num_iterations` | integer | Maximum training iterations | 100000 |
| `--temperature` | float | InfoNCE temperature parameter | 0.1 |

Sources: [code/free_embedding_experiment.py:682-723](), [code/free_embedding_experiment.py:58-71]()

### Usage Example

```bash
python free_embedding_experiment.py \
  --d=4 --k=2 \
  --enable_critical_n_search=11 \
  --results_output_path='d=4_k=2.json' \
  --device=gpu
```

Sources: [code/free_embedding_experiment.py:33-36]()

## Results Management and Output

### Result Structure and Serialization

```mermaid
graph TD
    subgraph "Experiment Result Schema"
        A["experiment_result"] --> B["parameters: Dict[str, Any]"]
        A --> C["metrics: Dict[str, Any]"]  
        A --> D["data: Dict[str, Any]"]
        
        B --> B1["n, d, k, seed"]
        B --> B2["learning_rate, num_iterations"]
        B --> B3["temperature, device"]
        
        C --> C1["final_accuracy: float"]
        C --> C2["best_accuracy_monitored: float"]
        C --> C3["max_accuracy_observed: float"]
        C --> C4["experiment_duration_seconds: float"]
        C --> C5["actual_q_generated: int"]
    end
    
    subgraph "NpEncoder Serialization"
        E["np.ndarray / jnp.ndarray"] --> F["asarray().tolist()"]
        G["set objects"] --> H["list(set)"]
        I["datetime objects"] --> J["isoformat()"]
        K["numpy scalars"] --> L["scalar.tolist()"]
    end
    
    subgraph "Incremental Saving"
        M["save_results_incrementally"] --> N["json.dumps(results_list, cls=NpEncoder)"]
        N --> O["os.makedirs(output_dir, exist_ok=True)"]
        O --> P["write to output_path"]
    end
    
    C --> E
    F --> M
    H --> M
    J --> M
    L --> M
```

Sources: [code/free_embedding_experiment.py:97-115](), [code/free_embedding_experiment.py:216-229](), [code/free_embedding_experiment.py:526-534]()

### Early Stopping and Monitoring

The optimization includes sophisticated early stopping with multiple monitoring options:

| Parameter | Purpose | Default |
|-----------|---------|---------|
| `early_stopping_patience` | Iterations to wait before stopping | 1000 |
| `early_stopping_min_delta` | Minimum improvement threshold | 0.00001 |
| `early_stopping_monitor_metric` | Metric to monitor ("loss" or "accuracy") | "loss" |
| `early_stopping_restore_best_weights` | Restore best weights after stopping | False |

The system tracks multiple accuracy signals: `final_accuracy`, `best_accuracy_monitored`, `max_accuracy_observed`, and `last_logged_accuracy` to provide robust signals for the critical N search logic.

Sources: [code/free_embedding_experiment.py:67-70](), [code/free_embedding_experiment.py:412-475](), [code/free_embedding_experiment.py:591-600]()

---


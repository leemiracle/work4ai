<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/dnc · page 2 Training the DNC · fetched 2026-10-26 -->

# Training the DNC

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [train.py](train.py)

</details>



This page covers the full training pipeline implemented in `train.py`: how the DNC model is constructed and run, how loss is computed and backpropagated, how gradients are clipped and applied, and how the training loop manages checkpointing and periodic reporting.

For details on the task used for training, see [The RepeatCopy Task](#2.1). For configuration flags, see [Training Configuration](#2.2). For the DNC model itself, see [Core Architecture](#3).

---

## Overview

`train.py` is the single entry point for training the DNC. It wires together the `RepeatCopy` dataset, the `DNC` model, and the TensorFlow training machinery into a complete supervised learning loop.

**Training Pipeline Diagram**

```mermaid
flowchart TD
    main["main()"]
    train_fn["train(num_training_iterations, report_interval)"]
    dataset["RepeatCopy(...)"]
    dataset_tensors["dataset_tensors\n(observations, target, mask)"]
    run_model["run_model(input_sequence, output_size)"]
    output_logits["output_logits\ntf.nn.dynamic_rnn output"]
    cost["dataset.cost(output_logits, target, mask)"]
    gradients["tf.gradients(train_loss, trainable_variables)"]
    clip["tf.clip_by_global_norm(..., max_grad_norm)"]
    optimizer["RMSPropOptimizer.apply_gradients(...)"]
    session["SingularMonitoredSession"]
    log["tf.logging.info(avg_loss, dataset_string)"]
    checkpoint["CheckpointSaverHook"]

    main --> train_fn
    train_fn --> dataset
    dataset --> dataset_tensors
    dataset_tensors --> run_model
    run_model --> output_logits
    output_logits --> cost
    cost --> gradients
    gradients --> clip
    clip --> optimizer
    optimizer --> session
    session --> log
    session --> checkpoint
```

Sources: [train.py:94-168]()

---

## Model Construction: `run_model`

The `run_model` function [train.py:69-91]() builds the TensorFlow graph for a single forward pass over an entire input sequence. It does not execute computation itself — it defines the graph nodes.

**Steps:**

1. **Assemble `access_config`** — a dict containing `memory_size`, `word_size`, `num_reads`, and `num_writes`, drawn from FLAGS.
2. **Assemble `controller_config`** — a dict containing `hidden_size` for the LSTM controller.
3. **Instantiate `dnc.DNC`** with the above configs plus `output_size` and `clip_value`.
4. **Compute `initial_state`** via `dnc_core.initial_state(FLAGS.batch_size)`.
5. **Run `tf.nn.dynamic_rnn`** with `time_major=True`, which unrolls the DNC across the entire sequence dimension and returns `output_sequence`.

```mermaid
flowchart LR
    flags["FLAGS\n(hidden_size, memory_size,\nword_size, num_write_heads,\nnum_read_heads, clip_value)"]
    access_config["access_config dict"]
    controller_config["controller_config dict"]
    dnc_core["dnc.DNC\n(access_config, controller_config,\noutput_size, clip_value)"]
    initial_state["dnc_core.initial_state(batch_size)"]
    dynamic_rnn["tf.nn.dynamic_rnn\n(cell=dnc_core, inputs=input_sequence,\ntime_major=True, initial_state=...)"]
    output_sequence["output_sequence\n[time, batch, output_size]"]

    flags --> access_config
    flags --> controller_config
    access_config --> dnc_core
    controller_config --> dnc_core
    dnc_core --> initial_state
    initial_state --> dynamic_rnn
    dnc_core --> dynamic_rnn
    dynamic_rnn --> output_sequence
```

Sources: [train.py:69-91]()

The `output_size` passed to `DNC` is `dataset.target_size`, which is determined by the `RepeatCopy` task configuration.

---

## Loss Computation

After `run_model` returns `output_logits`, the `train` function [train.py:94-158]() computes a masked sigmoid cross-entropy loss:

```
train_loss = dataset.cost(output_logits, dataset_tensors.target, dataset_tensors.mask)
```

The `mask` tensor is also used separately to produce a rounded binary `output` for visualization:

```
output = tf.round(tf.expand_dims(dataset_tensors.mask, -1) * tf.sigmoid(output_logits))
```

This `output` is only evaluated during reporting intervals and is passed to `dataset.to_human_readable(...)` for display. It is not used in the loss or gradient computation.

Sources: [train.py:102-108]()

---

## Gradient Clipping and Optimizer

Gradients are computed and clipped in two steps [train.py:111-126]():

| Step | Code construct | Purpose |
|---|---|---|
| Compute raw gradients | `tf.gradients(train_loss, trainable_variables)` | Differentiate loss w.r.t. all trainable parameters |
| Clip by global norm | `tf.clip_by_global_norm(grads, max_grad_norm)` | Cap the global L2 norm of the gradient vector at `max_grad_norm` (default: 50) |
| Apply gradients | `optimizer.apply_gradients(zip(grads, trainable_variables), global_step=global_step)` | Update parameters using RMSProp |

The optimizer is `tf.train.RMSPropOptimizer` configured with `learning_rate` (default: `1e-4`) and `epsilon` (default: `1e-10`).

A `global_step` variable [train.py:115-121]() is registered in both `GLOBAL_VARIABLES` and `GLOBAL_STEP` collections. It is incremented automatically by `apply_gradients` and is used to resume training from a checkpoint.

Sources: [train.py:111-126]()

---

## Checkpointing

Checkpoint behavior is conditional on the `checkpoint_interval` flag [train.py:130-138]():

- If `checkpoint_interval > 0`: a `tf.train.CheckpointSaverHook` is attached to the session. It saves to `checkpoint_dir` every `checkpoint_interval` steps.
- If `checkpoint_interval <= 0` (default: `-1`): no periodic saving hook is attached.

Regardless of the hook, `SingularMonitoredSession` is always given `checkpoint_dir`. On startup, it will restore from the latest checkpoint in that directory if one exists, allowing training to resume automatically.

| Flag | Default | Effect |
|---|---|---|
| `checkpoint_dir` | `/tmp/tf/dnc` | Directory to write/read checkpoints |
| `checkpoint_interval` | `-1` | Steps between saves; `-1` disables periodic saving |

Sources: [train.py:63-66](), [train.py:128-142]()

---

## Training Loop

The training loop [train.py:141-158]() runs inside a `tf.train.SingularMonitoredSession` context:

```mermaid
flowchart TD
    start["sess.run(global_step)\n→ start_iteration"]
    loop["for train_iteration in range(start_iteration, num_training_iterations)"]
    step["sess.run([train_step, train_loss])\n→ (_, loss)"]
    accum["total_loss += loss"]
    report_check["(train_iteration + 1) % report_interval == 0?"]
    report["sess.run([dataset_tensors, output])\ndataset.to_human_readable(...)\ntf.logging.info(avg_loss, dataset_string)\ntotal_loss = 0"]
    no_report["continue"]

    start --> loop
    loop --> step
    step --> accum
    accum --> report_check
    report_check -->|"Yes"| report
    report_check -->|"No"| no_report
    report --> loop
    no_report --> loop
```

**Key behaviors:**

- `start_iteration` is read from `global_step` at session start, so a restored checkpoint resumes from where it left off.
- Each iteration executes `train_step` (weight update) and reads back `train_loss` in a single `sess.run` call for efficiency.
- Every `report_interval` iterations (default: 100), `total_loss / report_interval` is logged as the average loss and the accumulated total is reset to zero.
- The `to_human_readable` output is also logged at each report, showing the raw input/output pattern for visual inspection.

Sources: [train.py:141-158]()

---

## Entry Point

`main` [train.py:161-163]() sets log verbosity to `INFO` level and calls `train(FLAGS.num_training_iterations, FLAGS.report_interval)`. `tf.app.run()` [train.py:167]() handles flag parsing before calling `main`.

To start training with defaults:

```
python train.py
```

To override flags:

```
python train.py --hidden_size=128 --memory_size=32 --num_training_iterations=200000
```

Sources: [train.py:161-167]()

---

## Summary: Key Symbols

| Symbol | Type | File | Role |
|---|---|---|---|
| `run_model` | function | `train.py` | Builds DNC graph; calls `tf.nn.dynamic_rnn` |
| `train` | function | `train.py` | Full training loop: loss, gradients, optimizer, session |
| `main` | function | `train.py` | Entry point; sets log verbosity |
| `dnc.DNC` | class | `dnc/dnc.py` | The RNNCore passed to `dynamic_rnn` |
| `repeat_copy.RepeatCopy` | class | `repeat_copy.py` | Generates `dataset_tensors`; computes `cost` |
| `tf.nn.dynamic_rnn` | TF op | — | Unrolls `DNC` over the time dimension |
| `tf.clip_by_global_norm` | TF op | — | Gradient clipping |
| `tf.train.RMSPropOptimizer` | TF class | — | Parameter update rule |
| `SingularMonitoredSession` | TF class | — | Managed session with checkpoint restore |
| `CheckpointSaverHook` | TF class | — | Periodic checkpoint saves |

---


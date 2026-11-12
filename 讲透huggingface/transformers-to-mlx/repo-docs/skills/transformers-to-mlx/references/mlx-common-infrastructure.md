# Changes to mlx-lm Common Infrastructure

Some model conversions require changes not just to a new model file, but to shared mlx-lm infrastructure (e.g., `ssm.py`, Metal kernels, `cache.py`). These changes carry risk because they affect all models that use the same code paths.

## When This Happens

A new model may need infrastructure changes when:
- It uses an existing module (SSM, cache, etc.) with different parameters or behavior than previous models
- The shared code has assumptions that don't hold for the new architecture
- A bug in shared code was latent because no previous model exercised that code path

## Principle: Localize Changes When Possible

Before modifying shared infrastructure, check whether the fix can be localized to the new model file instead. The goal is to minimize blast radius.

### Example: compute_dt clipping (Zamba2)

The shared `ssm.py` `compute_dt` function clips the time step delta to both a minimum and maximum:

```python
dt = mx.clip(dt, time_step_limit[0], time_step_limit[1])
```

Most SSM models (Mamba2, Falcon H1, Granite) pass both limits and this works correctly. But Zamba2's transformers implementation only clips the minimum — the max clipping is commented out.

**Bad approach:** Modify `compute_dt` to conditionally skip max clipping. This changes behavior for all SSM models.

**Good approach:** In `zamba2.py`, override the limit at the call site:

```python
time_step_limit = (self.args.time_step_min, float("inf"))
```

This keeps the change localized to `zamba2.py`, preserves the `ssm.py` API, and doesn't affect other models. The config's original `time_step_max` value is preserved; only the value passed to the SSM function is overridden. (Document why in the PR description, not in an inline comment.)

## When Shared Changes Are Unavoidable

Sometimes the fix genuinely belongs in shared code — for example, a kernel bug that happens to not affect current models but would produce wrong results for the new one.

### Example: SSM kernel group indexing (Zamba2)

The Metal SSM kernel computed `g_idx = n / G` for indexing into the B and C tensors, which didn't account for the batch dimension when `n_groups > 1`. Previous models all used `n_groups=1`, so the bug was latent.

The correct fix:
```metal
int batch_idx = n / H;
int h_idx = n % H;
int g_idx = h_idx / G;
// B/C offset: (batch_idx * NG + g_idx) * Ds
```

### Checklist for shared infrastructure changes

1. **Identify all models using the shared code** — search for imports/calls to the function or kernel being modified
2. **Verify the change is safe for existing models** — the new behavior must produce identical results for all current parameter combinations
3. **Test at least one existing model** after the change, not just the new one
4. **Prefer additive changes** — new parameters with defaults that preserve old behavior, rather than modifying existing parameter semantics
5. **Document the reason in the PR** — explain in the PR description (not in inline code comments) why the change was needed and which model triggered it
6. **Flag to the user** — when a conversion requires shared infrastructure changes, always inform the user before making the modification. These changes warrant extra review.

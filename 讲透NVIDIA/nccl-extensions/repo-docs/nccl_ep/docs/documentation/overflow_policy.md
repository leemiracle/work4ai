# Recv Overflow Policy

Routing is data-dependent, so a rank can be targeted by more tokens than the
`max_recv_tokens_per_rank` budget its group was created with.
`ncclEpGroupConfig_t::overflow_policy` selects what happens then.

This policy applies to **High Throughput (HT) only**; Low Latency ignores the
field.

## Where overflow is detected

Overflow is detected by the metadata scan inside `ncclEpCreateHandle` /
`ncclEpUpdateHandle` — not at dispatch time — by comparing the rank's true recv
total against the budget.

Incoming tokens are written into **two different buffers**, and each one is
checked against the same `max_recv_tokens_per_rank` budget:

1. **The library's staging buffer**, which holds **deduplicated tokens** — one row
   per arriving token, regardless of the number of local experts that consume it.
   A token whose staging row would reach the budget is dropped here.
2. **The caller's dispatch output buffer**, arranged according to the handle's
   layout:
   - **`NCCL_EP_LAYOUT_FLAT`** — also deduplicated. It counts exactly what staging
     counts, against the same budget, so anything that fit in staging fits here.
     This check never drops a token the first one kept.
   - **`NCCL_EP_LAYOUT_EXPERT_MAJOR`** — one slot per *(token, local expert)* pair,
     with each expert's zone padded up to `dispatch_output_per_expert_alignment`.
     A token whose output slot would reach the budget is dropped here.

Deduplication is the whole difference. Staging counts **tokens**; an expert-major
output counts **token-expert pairs**, then adds alignment padding. A token routed
to *k* of this rank's local experts occupies one staging row but *k* output slots,
so an expert-major output buffer is always the more crowded of the two. **A rank
can overflow its output buffer while everything fit in staging** — which is why the
second check exists, and why it only ever fires under expert-major.

## Policies

- **`NCCL_EP_OVERFLOW_TRAP`** — the zero-init default, since `NCCL_EP_OVERFLOW_AUTO`
  resolves to it. The device executes `__trap()` on overflow, which **aborts the
  process** and destroys the CUDA context; it is not a recoverable `ncclResult_t`.
  A diagnostic naming the actual and configured counts is printed from the device
  first. Appropriate when capacity is planned ahead and an overflow means a bug.

- **`NCCL_EP_OVERFLOW_DROP`** — the overflowing tokens are discarded and the
  pipeline continues normally. Dispatch and combine both return `ncclSuccess`.

## Behavior under `DROP`

- `ncclEpLayoutInfo_t.recv_total_counter` reports the **true, pre-drop** total,
  while the recv count driving the rest of the pipeline is clamped to
  `max_recv_tokens_per_rank`. Comparing the two is how a caller detects that a
  drop occurred and how many tokens were lost.
- Expert-major per-expert counts are clamped the same way: an expert whose zone
  begins at or past capacity reports a count of `0`, and its offset clamps to
  capacity.
- Retained slots hold their tokens as usual. On the expert-major permute path
  (the default when `NCCL_EP_HT_EM_LOCAL_DUP` and `NCCL_EP_HT_EM_NVLINK_DUP` are
  off), dispatch additionally zero-fills the output buffers up to
  `max_recv_tokens_per_rank`: `dispatch_outputs.tokens`, plus `topk_weights` on a
  forward dispatch and `scales` under `NCCL_EP_DISP_QUANT_FWD`. Tokens dropped at
  the staging buffer may still map to in-capacity slots in the expert-major layout
  (see [Example 2](#example-2-how-staging-drops-leave-phantom-rows)). To avoid
  data corruption, these slots are zeroed, turning them into no-ops during the
  expert GEMM phase. The fill is unconditional under `DROP`, so it costs one
  memset of the output region per dispatch even when nothing overflows.
- In combine, a dropped assignment contributes **zero** to its token's reduction.
  A token whose assignments were *all* dropped is returned as zeros. Dropped
  tokens are silently absent from the result; nothing downstream reports them.
- Because the counts are clamped by zone arithmetic while delivery is decided per
  slot, `expert_counters[e]` is an **upper bound** on the rows actually written,
  not an exact count. The zero-fill above is what makes consuming that bound safe.

## Example 1: padding overflows the budget that staging fit

Two local experts, `max_recv_tokens_per_rank = 8`,
`dispatch_output_per_expert_alignment = 2`. Eight distinct tokens arrive; five
route to `E0`, three to `E1`.

```
Staging buffer — deduplicated, one row per arriving token

  slot:   0     1     2     3     4     5     6     7
        [ T0 ][ T1 ][ T2 ][ T3 ][ T4 ][ T5 ][ T6 ][ T7 ]
        `-------------- 8 <= 8: nothing dropped --------------'

Output buffer — expert-major (token-expert pairs), each zone padded up to 2

  slot:   0     1     2     3     4    5   |  6     7     8    9
        [ ------ E0: 5 tokens ------ ][pad]  [ E1: 3 tokens ][pad]
                                              `-- kept --'`-- >= 8: DROPPED --'

  true padded total = 6 + 4 = 10  >  8
```

Every token fit in staging with the budget exactly met, yet `E1` still loses one
of its three tokens: padding `E0` from 5 slots to 6 pushed `E1`'s zone up, and its
third token landed at slot 8. The caller observes:

| Reported value | Value | Derivation |
|---|---|---|
| `expert_counters[0]` | `5` | `min(5, room = 8 - 0)` |
| `expert_counters[1]` | `2` | `min(3, room = 8 - 6)` — one of three tokens dropped |
| `expert_offsets[0]` | `0` | zone base |
| `expert_offsets[1]` | `6` | `min(cum = 6, capacity = 8)` |
| `recv_total_counter` | `10` | true pre-drop padded total |

`recv_total_counter (10) > max_recv_tokens_per_rank (8)` is the drop signal.

## Example 2: how staging drops leave phantom rows

Two local experts, `max_recv_tokens_per_rank = 4`, alignment `1` (no padding, to
isolate the effect). Six tokens arrive.

```
Staging buffer — deduplicated

  slot:   0     1     2     3   |   4     5
        [ T0 ][ T1 ][ T2 ][ T3 ]   [ T4 ][ T5 ]
        `-------- kept --------'   `-- >= 4: DROPPED --'

Routing:   E0 <- T0, T4          E1 <- T1, T2, T3, T5
                     ^^                              ^^
                     already dropped from staging

Output buffer — expert-major. Zone sizes come from the routing, so tokens
                dropped from staging still reserve their output slot.

  slot:   0     1     2     3   |   4     5
        [ T0 ][ T4 ][ T1 ][ T2 ]   [ T3 ][ T5 ]
           |     |                 `-- >= 4: dropped from output --'
           |     `-- no staging row exists -> never written -> PHANTOM
           `-- delivered
```

`expert_counters` reports `[2, 2]` — four valid rows, slots 0-3. But slot 1 was
never written by anyone: `T4` was dropped from staging, so the copy warp has no
source row for it, while the output buffer kept the slot because `1 < 4`. It is
neither a delivered
token nor alignment padding, so the pad warp skips it too. Without the zero-fill
it would hand the caller whatever the buffer held before — stale tokens from the
previous iteration, or uninitialized memory on the first.

This is why `expert_counters[e]` is an upper bound: `E0` advertises 2 rows and
delivers 1. Slot positions above are illustrative — the exact assignment depends
on scan order — but the mechanism is exactly this.

## Constraints

Two constraints are easy to trip over:

1. **`DROP` does not let you under-size the recv tensors.** They must still be
   allocated for `max_recv_tokens_per_rank` slots; dispatch returns
   `ncclInvalidArgument` otherwise. `DROP` bounds the damage from a routing spike,
   it does not shrink the buffers.
2. **`DROP` requires an explicit `max_recv_tokens_per_rank`.** It is incompatible
   with [HT eager mode](eager_mode.md) (`max_recv_tokens_per_rank = NCCL_EP_AUTO`), which relies on
   trap semantics, and `ncclEpCreateGroup` rejects the combination.

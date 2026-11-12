# Distributed Inference

For models that exceed a single machine's efficient memory range, MLX supports distributed inference across multiple machines using tensor parallelism (TP).

## Prerequisites

- Two or more Apple Silicon machines on the same network
- SSH access between machines (passwordless recommended)
- The same model, code, and Python environment at **identical paths** on all machines
- A hostfile describing the cluster topology

## Hostfile format

The hostfile is a JSON array. Each entry specifies an SSH hostname and its network IP addresses:

```json
[
    {
        "ssh": "bigmac1",
        "ips": ["172.18.3.128"]
    },
    {
        "ssh": "bigmac2",
        "ips": ["172.18.3.129"]
    }
]
```

The SSH hostnames must be resolvable (via `/etc/hosts`, `~/.ssh/config`, or DNS). The IPs are used for the ring communication backend.

If the user does not have a hostfile, ask them to provide:
- The SSH hostname or alias for each machine
- The IP address of each machine on the interconnect network (e.g., 10GbE)

## Running distributed inference

Use the `mlx.launch` script (installed in the venv's `bin/` directory):

```bash
.venv/bin/mlx.launch \
    --backend ring \
    --env MLX_METAL_FAST_SYNCH=1 \
    --hostfile /path/to/hosts.json \
    /path/to/sharded_generate.py \
    --model /path/to/model \
    --prompt "Who are you?"
```

Key flags:
- `--backend ring` — uses the ring communication backend over ethernet
- `--env KEY=VALUE` — propagates environment variables to all nodes (critical for `MLX_METAL_FAST_SYNCH=1`)
- `--hostfile` — path to the JSON hostfile

The `sharded_generate.py` example script lives in `mlx-lm/mlx_lm/examples/sharded_generate.py` and provides a ready-to-use generation harness. Key arguments:
- `--model` — HF repo ID or local path to the model
- `--prompt` / `-p` — text prompt
- `--max-tokens` / `-m` — maximum tokens to generate (default: 256)
- `--pipeline` — flag to use pipeline parallelism instead of tensor parallelism

## Syncing code and model across machines

All machines must have identical copies of the code, model weights, and Python environment at the same absolute paths.

### rsync setup

```bash
# Create directory structure on remote
ssh remote_host "mkdir -p /Users/pedro/code/project"

# Sync code and venv (fast, typically <1 min)
rsync -a /path/to/project/.venv remote_host:/path/to/project/
rsync -a /path/to/project/mlx-lm remote_host:/path/to/project/

# Sync model weights (slow for large models)
rsync -a /path/to/project/models remote_host:/path/to/project/

# If transformers is an editable install, sync that too
rsync -a /path/to/project/transformers remote_host:/path/to/project/
```

**Caveats:**
- macOS ships rsync 2.6.9 which lacks `--info=progress2`. Use `-a` without info flags, and check progress via `ssh remote_host "du -sh /path/to/model/"` in a separate terminal.
- The venv can be rsynced directly between machines **only if** the absolute paths match and both machines run the same architecture (arm64). The venv's symlinks and `pyvenv.cfg` reference absolute paths.
- If the venv points to a uv-managed Python (`~/.local/share/uv/python/...`), install the same Python version on the remote: `ssh remote_host "curl -LsSf https://astral.sh/uv/install.sh | sh && ~/.local/bin/uv python install 3.12"`.
- For 10GbE, large model transfers run at ~400-600 MB/s on big shards, so a 400 GB model takes ~12-15 minutes.

### Verify the remote environment

```bash
ssh remote_host "/path/to/project/.venv/bin/python -c 'import mlx.core as mx; import mlx_lm; print(\"OK\")'"
```

## Model requirements for distributed inference

### The `shard()` method

For tensor parallelism, the MLX model must implement a `shard(self, group)` method that distributes weights across ranks:

```python
def shard(self, group: Optional[mx.distributed.Group] = None):
    group = group or mx.distributed.init()
    N = group.size()

    for layer in self.model.layers:
        # Attention: shard heads across ranks
        layer.self_attn.q_proj = shard_linear(layer.self_attn.q_proj, "all-to-sharded", group=group)
        layer.self_attn.o_proj = shard_linear(layer.self_attn.o_proj, "sharded-to-all", group=group)
        layer.self_attn.n_heads //= N
        layer.self_attn.n_kv_heads //= N

        # MLP: shard intermediate dimensions across ranks
        layer.mlp.gate_proj = shard_linear(layer.mlp.gate_proj, "all-to-sharded", group=group)
        layer.mlp.down_proj = shard_linear(layer.mlp.down_proj, "sharded-to-all", group=group)
```

Sharding patterns:
- **`"all-to-sharded"`** — input replicated, output sharded (for Q/K/V, gate/up projections)
- **`"sharded-to-all"`** — input sharded, output replicated with all-reduce (for output, down projections)

### PipelineMixin

For pipeline parallelism (assigning different layers to different ranks), the model can inherit from `PipelineMixin` (in `mlx_lm.models.pipeline`). This provides a `pipeline()` method that handles layer assignment automatically.

### MoE sharding

For MoE layers, shard the gate, shared experts, and update `num_experts_per_tok`:

```python
if hasattr(layer.mlp, "switch_mlp"):
    # SwitchGLU handles its own sharding
    layer.mlp.switch_mlp = shard_inplace(layer.mlp.switch_mlp, group=group)
if hasattr(layer.mlp, "shared_experts"):
    layer.mlp.shared_experts.gate_proj = shard_linear(...)
    layer.mlp.shared_experts.down_proj = shard_linear(...)
```

## Performance expectations

The speedup from tensor parallelism comes primarily from **reduced per-node memory pressure**, not doubled compute:

| Scenario | Per-node memory | Typical speedup |
|----------|----------------|-----------------|
| 418 GB model on 1× 512 GB machine | 418 GB | 1× (baseline, ~15s/tok) |
| 418 GB model on 2× 512 GB machines | ~209 GB each | ~100-150× |

The dramatic speedup for memory-pressure-limited models confirms that the bottleneck is memory system efficiency (TLB, cache hierarchy), not raw bandwidth. See [Large Models](large-models.md) for details on why.

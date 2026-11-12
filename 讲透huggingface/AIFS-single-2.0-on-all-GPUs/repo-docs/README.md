# Running ECMWF AIFS using CUDA or Apple MPS or CPU ![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)

> ### ⚠️ Not officially affiliated with ECMWF
>
> ### 🚫 Not for operational or safety-critical use

---

ECMWF has released its AIFS weights on Hugging Face, including the current [aifs-single-2.0](https://huggingface.co/ecmwf/aifs-single-2.0) checkpoint.
AIFS is a data-driven medium-range forecasting model trained on ECMWF's ERA5 reanalysis and operational NWP analyses, and is described in [Lang et al. (2024)](https://arxiv.org/abs/2406.01465).

To generate a forecast from the published weights, ECMWF's documentation points to `anemoi-inference`.
However, the AIFS was trained with a dependency on [`flash-attn`](https://github.com/Dao-AILab/flash-attention),
which only compiles on **Ampere-class NVIDIA GPUs** (A100, H100, RTX 30xx+).
For anyone without that specific hardware, installing `flash-attn` and dealing with `anemoi` dependencies are the main barriers to running inference.

Therefore, we developed this tutorial and a lightweight wrapper to simplify running [aifs-single-2.0](https://huggingface.co/ecmwf/aifs-single-2.0) with `anemoi-inference` locally on any GPU or CPU, or using Hugging Face jobs.

---

## Why does `AIFS` rely on `flash-attn`

AIFS uses a **sliding-window graph-transformer** architecture. Each
attention layer calls `flash_attn_func` from the `flash-attn` package,
which computes the softmax and matrix multiplications into a single CUDA
kernel — fast, memory-efficient, and **Ampere-only**.

PyTorch 2.1+ ships its own fused attention via
`torch.nn.functional.scaled_dot_product_attention` (SDPA), which:

- Dispatches to a flash-attn-style kernel on capable hardware
- Falls back gracefully to memory-efficient attention or naive attention
- Works on CUDA, Apple MPS, and CPU

Our wrapper intercepts Anemoi's `flash_attn` import and routes it to SDPA.

> **Numerical caveat.** The SDPA path reproduces flash-attn's
> sliding-window semantics but is not bit-identical to the CUDA
> flash-attn kernels used during AIFS training. Small numerical
> differences are expected, especially on MPS and CPU where reduction
> order and precision differ. A `RuntimeWarning` is emitted on import
> to remind you of this.

---

## Running the forecasts locally

### Local setup

**Requirements:** Python ≥3.11, <3.13

```bash
git clone https://github.com/huggingface/AIFS-single-2.0-on-all-GPUs
cd AIFS-single-2.0-on-all-GPUs
pip install -r requirements.txt
```

> You do **not** need to `pip install flash-attn`.

**requirements.txt** (key packages, see the file for the pinned versions):

```
torch>=2.1
anemoi-models==0.9.3
anemoi-transform==0.4.2
anemoi-datasets==0.5.26
anemoi-graphs==0.6.4
anemoi-inference
```

---

### How it works

The wrapper lives in `aifs/compat.py`. It creates a fake `flash_attn`
module tree and registers it in `sys.modules` *before* any `Anemoi` import
can trigger the real package lookup:

```python
def _patch():
    """Install the flash_attn stub into ``sys.modules``."""
    if "flash_attn" in sys.modules:
        return

    flash_attn = types.ModuleType("flash_attn")
    flash_attn.__version__ = "2.6.0"
    flash_attn.flash_attn_func = _sdpa_compat

    # flash_attn.layers.rotary  (imported but only used on specific GPU paths)
    layers_mod = types.ModuleType("flash_attn.layers")
    rotary_mod = types.ModuleType("flash_attn.layers.rotary")

    def _rotary_not_implemented(*args, **kwargs):
        raise NotImplementedError(
            "flash_attn.layers.rotary.RotaryEmbedding is not available in the SDPA "
            "compatibility shim; this code path requires real flash-attn on CUDA."
        )

    rotary_mod.RotaryEmbedding = _rotary_not_implemented
    layers_mod.rotary = rotary_mod
    flash_attn.layers = layers_mod

    # flash_attn.flash_attn_interface  (the one Anemoi actually calls)
    interface_mod = types.ModuleType("flash_attn.flash_attn_interface")
    interface_mod.flash_attn_func = _sdpa_compat
    flash_attn.flash_attn_interface = interface_mod

    sys.modules["flash_attn"] = flash_attn
    sys.modules["flash_attn.layers"] = layers_mod
    sys.modules["flash_attn.layers.rotary"] = rotary_mod
    sys.modules["flash_attn.flash_attn_interface"] = interface_mod


_patch()
```

This code allows inference of AIFS on any GPU or CPU.

---

### Step-by-Step Tutorial

#### 1. Check Your Device

```python
from aifs import get_device, device_label
print(device_label())
# → "CUDA — NVIDIA A100-SXM4-40GB"
# → "Apple MPS (Metal)"
# → "CPU (no GPU detected — inference will be slow)"
```

#### 2. Download Initial Conditions

AIFS needs two consecutive 6-hour analyses as input: **t-6h** and **t**.
We pull them from [ECMWF Open Data](https://www.ecmwf.int/en/forecasts/datasets/open-data)
— freely available under CC BY 4.0 and the ECMWF Terms of Use (see
[Licences and attribution](#licences-and-attribution)).

Multiple datasets are downloaded at this step. Once downloaded for the first time, each dataset is stored in cache.
The first download takes a few minutes. Later, loading from cache only takes a few seconds.

During the initial download, rate limits and transient errors sometimes occur. If you get an error while downloading, wait a few seconds and try again.

```python
from aifs import load_ics

fields, date = load_ics(cache_dir="../ic_cache")
# First run: ~3–5 min download, saved to ic_cache/
# Later runs: <1 s from local .npz cache

print(date)
print(fields["2t"].shape)
```

**Fields downloaded**: surface, soil, ocean waves,
pressure levels, plus derived quantities (geopotential, wave direction components).

#### 3. Run a Forecast

```python
from aifs import run_forecast

states = run_forecast(
    fields,
    date,
    lead_time=24,
    num_chunks=16,
)
```

Each call to `run_forecast` returns a list of state dicts — one per
6-hour output step:

```python
for state in states:
    print(state["date"], state["fields"]["2t"].mean() - 273.15, "°C")
# 2025-01-15 06:00:00   14.32 °C
# 2025-01-15 12:00:00   14.38 °C
# 2025-01-15 18:00:00   14.41 °C
# 2025-01-16 00:00:00   14.29 °C
```

#### 4. Plot Forecast Fields

```python
from aifs import plot_field

# Single map
fig = plot_field(states[0], "2t")
fig.savefig("t2m_T+6h.png", dpi=150)
```

Available fields for plotting:

```python
from aifs import PLOTTABLE
print(PLOTTABLE)
# ['2t', 'msl', 'sp', 'tcw', '10u', '10v', 'swh', 'mwp',
#  't_850', 't_500', 'u_850', 'v_850', 'z_500', 'q_700']
```

#### 5. CLI Usage

```bash
# 24-hour forecast, save plots to ./outputs/
python run_forecast.py

# 48-hour forecast
python run_forecast.py --lead-time 48 --fields 2t msl z_500

# List IC cache
python run_forecast.py --list-cache

# Force re-download
python run_forecast.py --force-download

# Upload results to a HF dataset (private by default; use --public to make it public)
python run_forecast.py --dataset-repo your-hf-username/aifs-results --public
```

#### 6. Streaming for Long Runs

```python
from aifs import run_forecast_streaming

for state in run_forecast_streaming(fields, date, lead_time=120):
    t = state["fields"]["2t"].mean() - 273.15
    print(f"{state['date']}  global mean T2m = {t:.2f} °C")
```

## Running the forecast using Hugging Face jobs

If you don't have access to a GPU / CPU or to enough storage, you can run the forecast directly using Hugging Face jobs.
You can find more details about [Hugging Face jobs](https://huggingface.co/docs/hub/en/jobs-quickstart) and the [pricing](https://huggingface.co/docs/hub/en/jobs-pricing).

### Getting started with Hugging Face jobs

First install the Hugging Face CLI:

#### 1. Install the CLI

Recommended approach:

```
curl -LsSf https://hf.co/cli/install.sh | bash
```

Or using Homebrew:

```
brew install hf
```

Or using uv:

```
uv tool install hf
```

#### 2. Create a dataset to host your results

Create a dataset named `aifs-results` in your HF organization which will store the results of the forecast.

#### 3. Login to your Hugging Face account

Create an access token following the [documentation](https://huggingface.co/docs/hub/en/security-tokens). Grant the token read / write rights on your organization's `aifs-results` dataset and the permission to manage jobs.

#### 4. Run the forecast

The GitHub archive extracts as `AIFS-single-2.0-on-all-GPUs-main`, so make sure the `cd` target matches:

```bash
hf jobs run \
  --flavor t4-small \
  --secrets HF_TOKEN=$HF_TOKEN \
  pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel \
  bash -c "python -c \"import urllib.request; urllib.request.urlretrieve('https://github.com/huggingface/AIFS-single-2.0-on-all-GPUs/archive/refs/heads/main.tar.gz', 'repo.tar.gz')\" && \
           tar xzf repo.tar.gz && \
           cd AIFS-single-2.0-on-all-GPUs-main && \
           pip install -r requirements.txt huggingface_hub && \
           python run_forecast.py --lead-time 48 --no-plots --dataset-repo your-hf-username/aifs-results"
```

You can find more details about Hugging Face jobs [here](https://huggingface.co/docs/hub/en/jobs).

---

## Repository Structure

```
aifs-tutorial/
├── aifs/
│   ├── __init__.py          # Clean public API
│   ├── compat.py            # flash-attn → SDPA shim  ← the key piece
│   ├── device.py            # Device detection helpers
│   ├── initial_conditions.py # ECMWF Open Data download + cache
│   ├── forecast.py          # Thin anemoi-inference wrapper
│   └── plot.py              # Cartopy-based visualisation
├── notebook/
│   └── tutorial.ipynb       # This tutorial as a runnable notebook
├── forecasts/               # Where your forecasts will be saved
├── run_forecast.py           # CLI entrypoint
├── requirements.txt
└── README.md
```

---

## Operational and safety guidance

- **Do not use these forecasts for aviation, marine navigation, life-safety
  or any other operational decision-making.** The ECMWF Open Data Terms of
  Use explicitly disclaim all liability for accuracy, availability, or
  fitness for any particular purpose, and the SDPA shim in this repository
  introduces additional numerical divergence from the reference AIFS
  implementation. This wrapper replaces the CUDA-only `flash-attn` kernels
  with a `torch` SDPA fallback (see [How it works](#how-it-works)):
  numerical output may differ from a reference CUDA + flash-attn run,
  especially on Apple MPS and CPU.
- **Rate limits.** The ECMWF Open Data portal is limited to
  ~500 simultaneous connections globally. If your download stalls or
  errors, retry with backoff or switch to one of the cloud mirrors (AWS,
  Azure, GCP) — see the
  [ECMWF Open Data page](https://www.ecmwf.int/en/forecasts/datasets/open-data)
  for details.
- **Data retention.** ECMWF Open Data provides only the most recent
  ~12 forecast runs (~2–3 days). Cache your ICs locally if you need to
  reproduce a run later.
- **Full disclaimer.** *ECMWF does not accept any liability whatsoever for
  any error or omission in the data, their availability, or for any loss
  or damage arising from their use.*

---

## Licences and attribution

Three separate licences apply to material handled by this repository:

### AIFS model weights

The AIFS Single v2 checkpoint at
[`ecmwf/aifs-single-2.0`](https://huggingface.co/ecmwf/aifs-single-2.0) is
published by ECMWF under
[**Creative Commons Attribution 4.0 International (CC BY 4.0)**](https://creativecommons.org/licenses/by/4.0/).
The demonstration notebook and script files distributed alongside the
weights on the ECMWF model card are published under
[**Apache 2.0**](https://www.apache.org/licenses/LICENSE-2.0.txt).

### ECMWF Open Data (initial conditions)

The initial conditions downloaded by `aifs.load_ics()` come from
[ECMWF Open Data](https://www.ecmwf.int/en/forecasts/datasets/open-data),
licensed under [**CC BY 4.0**](https://creativecommons.org/licenses/by/4.0/)
and additionally subject to the
[**ECMWF Terms of Use**](https://apps.ecmwf.int/datasets/licences/general/).

### Required attribution for redistribution

If you publish or redistribute forecast data produced with this wrapper —
including by using `run_forecast.py --dataset-repo ...` to push results to
a Hugging Face dataset — you **must** attach the following wording, as
prescribed by ECMWF:

> 1. **Copyright statement:** Copyright "© \[year\] European Centre for Medium-Range Weather Forecasts (ECMWF)".
> 2. **Source:** [www.ecmwf.int](https://www.ecmwf.int)
> 3. **Licence statement:** This data is published under a Creative Commons Attribution 4.0 International (CC BY 4.0). <https://creativecommons.org/licenses/by/4.0/>
> 4. **Disclaimer:** ECMWF does not accept any liability whatsoever for any error or omission in the data, their availability, or for any loss or damage arising from their use.
> 5. **Modifications:** Indicate that the material has been modified (it has: initial conditions are regridded from 0.25° to N320, run through the AIFS model, and the SDPA shim in this repository is not bit-equivalent to the reference AIFS implementation). Indicate any previous modifications where applicable.

For **services** built on this data, ECMWF requires the alternative
wording specified in the
[ECMWF Terms of Use](https://apps.ecmwf.int/datasets/licences/general/)
(item beginning "Copyright statement: Copyright 'This service is based on
data and products of ECMWF'"). Please refer to the source page for the
authoritative text.


---

## FAQ

**Q: Where does the initial data come from?**
We use [ECMWF Open Data](https://www.ecmwf.int/en/forecasts/datasets/open-data),
which is freely available without registration under CC BY 4.0 and the
[ECMWF Terms of Use](https://apps.ecmwf.int/datasets/licences/general/).
See [Licences and attribution](#licences-and-attribution) for the required
wording.

**Q: Can I use AIFS Ensemble instead of AIFS Single?**
Not reliably with this shim. The `aifs-ens-2.0` checkpoint exercises
`flash_attn.layers.rotary.RotaryEmbedding`, which the SDPA compatibility
shim in `aifs/compat.py` deliberately does **not** implement — attempting
to run AIFS-ENS through this wrapper will raise `NotImplementedError` at
the first rotary-embedding call. AIFS-ENS also has different
requirements from AIFS-Single (an extra pressure-level variable `w`,
constant surface fields moved into `param_sfc_const`, ensemble member
selection via `number=...`), and was trained against different pinned
versions of the `anemoi-*` packages than those pinned in
`requirements.txt`. Running AIFS-ENS is best done on a real Ampere-class
GPU using the official `anemoi-inference` route documented on the
[ECMWF AIFS-ENS model card](https://huggingface.co/ecmwf/aifs-ens-2.0).

**Q: What is the size of the AIFS model and where is it stored?**
Hugging Face caches it under `~/.cache/huggingface/hub/`.
The AIFS Single v2 checkpoint is ~1 GB.

**Q: My MPS run crashes with an out-of-memory error.**
Set the `ANEMOI_INFERENCE_NUM_CHUNKS` environment variable higher (e.g. 64
or 128) — this is what the `num_chunks` argument to `run_forecast()`
controls. Also make sure no other GPU workloads are running. Note that
`num_chunks` operates at the anemoi-inference level, which is distinct
from the internal chunk size the SDPA shim uses to manage attention
memory in `aifs/compat.py`.

---

*This tutorial is **community-contributed** and is **not** produced,
endorsed or supported by ECMWF. ECMWF's own recommended path for running
AIFS is via [`anemoi-inference`](https://github.com/ecmwf/anemoi-inference)
as documented on the [official model card](https://huggingface.co/ecmwf/aifs-single-2.0).
The AIFS model weights are distributed by ECMWF under a **Creative Commons
Attribution 4.0 International (CC BY 4.0)** licence. Forecasts produced
with this wrapper are derived from ECMWF Open Data, which is likewise
licensed under **CC BY 4.0** and additionally subject to the
[ECMWF Terms of Use](https://apps.ecmwf.int/datasets/licences/general/).
See [Licences and attribution](#licences-and-attribution) above for the
wording that **must** accompany any redistribution or publication of these
forecasts.*

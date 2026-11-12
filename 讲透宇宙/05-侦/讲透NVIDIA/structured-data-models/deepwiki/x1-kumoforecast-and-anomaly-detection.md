<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/structured-data-models · extra page KumoForecast and Anomaly Detection · fetched 2026-10-26 -->

# KumoForecast and Anomaly Detection

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdm/models/kumo/timeseries/anomaly/block.py](sdm/models/kumo/timeseries/anomaly/block.py)
- [sdm/models/kumo/timeseries/anomaly/embedding.py](sdm/models/kumo/timeseries/anomaly/embedding.py)
- [sdm/models/kumo/timeseries/anomaly/noise_schedule.py](sdm/models/kumo/timeseries/anomaly/noise_schedule.py)
- [sdm/models/kumo/timeseries/forecast/block.py](sdm/models/kumo/timeseries/forecast/block.py)
- [sdm/models/kumo/timeseries/forecast/ckpt.py](sdm/models/kumo/timeseries/forecast/ckpt.py)
- [sdm/models/kumo/timeseries/forecast/cross.py](sdm/models/kumo/timeseries/forecast/cross.py)
- [sdm/models/kumo/timeseries/forecast/icl.py](sdm/models/kumo/timeseries/forecast/icl.py)
- [sdm/models/kumo/timeseries/forecast/model.py](sdm/models/kumo/timeseries/forecast/model.py)
- [sdm/models/kumo/timeseries/forecast/recipe.py](sdm/models/kumo/timeseries/forecast/recipe.py)
- [sdm/nn/sinusoidal.py](sdm/nn/sinusoidal.py)
- [test/models/kumo/timeseries/anomaly/test_block.py](test/models/kumo/timeseries/anomaly/test_block.py)
- [test/models/kumo/timeseries/anomaly/test_embedding.py](test/models/kumo/timeseries/anomaly/test_embedding.py)
- [test/models/kumo/timeseries/anomaly/test_noise_schedule.py](test/models/kumo/timeseries/anomaly/test_noise_schedule.py)
- [test/models/kumo/timeseries/anomaly/test_side_embedding.py](test/models/kumo/timeseries/anomaly/test_side_embedding.py)
- [test/models/kumo/timeseries/forecast/test_cross.py](test/models/kumo/timeseries/forecast/test_cross.py)
- [test/models/kumo/timeseries/forecast/test_icl.py](test/models/kumo/timeseries/forecast/test_icl.py)
- [test/models/kumo/timeseries/forecast/test_model.py](test/models/kumo/timeseries/forecast/test_model.py)
- [test/nn/test_sinusoidal.py](test/nn/test_sinusoidal.py)

</details>



## Purpose and Scope
This page details the implementation of time-series forecasting and anomaly detection models within the `sdm` library, focusing on `KumoForecast`, cross-channel attention mechanisms, recipes, sinusoidal embeddings, and the anomaly diffusion architecture (including residual blocks, noise schedules, and embedding modules).

---

## 1. KumoForecast Architecture and Data Flow

`KumoForecast` is a multivariate time-series forecasting foundation model that combines patch-based time-series embeddings with a transformer encoder and forecasting head [sdm/models/kumo/timeseries/forecast/model.py:36-43](). Operating under the `ICLModel` protocol, it treats rows as ordered time steps where past-only historical covariates (`x_context`) and target series (`y_context`) are provided, while future covariates (`x_query`) are ignored [sdm/models/kumo/timeseries/forecast/model.py:45-49]().

```mermaid
graph TD
    subcode["Code Entity Space"]
        KC[KumoForecast] --> MD[_KumoForecast]
        MD --> IC[ICLBlock]
        MD --> CC[CrossChannelAttention]
        MD --> SE[SinusoidalEmbedding]
        MD --> RI[RevIN]
    end
    subnlp["Natural Language Space"]
        TFS["Time-Series Forecasting Foundation"] --> KC
        CCA["Cross-Channel Mixing"] --> CC
        TST["Patch Tokenization & ICL"] --> IC
    end
    TFS -.-> KC
    CCA -.-> CC
    TST -.-> IC
```
*Sources: sdm/models/kumo/timeseries/forecast/model.py:26-79(), sdm/models/kumo/timeseries/forecast/cross.py:14-48(), sdm/nn/sinusoidal.py:10-36()*

During initialization, `KumoForecast` downloads or loads pretrained checkpoints from Hugging Face (`nvidia/Kumo-Forecast`), remapping weights via `remap_ckpt` [sdm/models/kumo/timeseries/forecast/model.py:90-106](). The `forward` method validates that context dimensions meet minimum size requirements (e.g., at least `context_size` rows) and strips future covariates with a warning [sdm/models/kumo/timeseries/forecast/model.py:109-189]().

Sources:
- `sdm/models/kumo/timeseries/forecast/model.py:26-189`
- `sdm/models/kumo/timeseries/forecast/ckpt.py:8-59`

---

## 2. Cross-Channel Attention and Recipes

To capture dependencies between variates after temporal encoding, `KumoForecast` provides optional cross-channel mixing via `CrossChannelAttention` [sdm/models/kumo/timeseries/forecast/model.py:41-42](). This module wraps a `TransformerBlock` operating across channel dimensions [sdm/models/kumo/timeseries/forecast/cross.py:14-48]().

```mermaid
graph TD
    Input[""x: Tensor [..., C, N, D]""] --> Transpose[""transpose(-3, -2)""]
    Transpose --> Block[""TransformerBlock""]
    Block --> TransposeBack[""transpose(-3, -2)""]
    TransposeBack --> Norm[""LayerNorm""]
    Norm --> Output[""Output Tensor""]
```
*Sources: sdm/models/kumo/timeseries/forecast/cross.py:36-48()*

The default processing recipe for `KumoForecast` is defined in `sdm/models/kumo/timeseries/forecast/recipe.py` [sdm/models/kumo/timeseries/forecast/recipe.py:7-16](). It utilizes frozen statistical state from standardizer checkpoints (`mean = -5.6712`, `scale = 8.6933`) applied via `sp.Standardize` for both features and targets, combined with an `sp.AverageEstimators` output reducer [sdm/models/kumo/timeseries/forecast/recipe.py:7-16]().

Sources:
- `sdm/models/kumo/timeseries/forecast/cross.py:14-48`
- `sdm/models/kumo/timeseries/forecast/recipe.py:7-16`

---

## 3. Sinusoidal and Positional Embeddings

Position and temporal encodings in the forecasting subsystem leverage standard sinusoidal embeddings [sdm/nn/sinusoidal.py:10-36](). The `SinusoidalEmbedding` module computes frequencies using a base `theta` (defaulting to $10,000$) over channel dimensions [sdm/nn/sinusoidal.py:18-36]().

For an input tensor of shape `[..., S, C]`, where `S` is sequence length and `C` is channels, position angles are computed as:

$$\text{angle} = \text{pos} \times \exp\left(-i \frac{\log(\theta)}{C}\right)$$

The module stacks sine and cosine components and flattens them to match the tensor dtype [sdm/nn/sinusoidal.py:30-36]().

Sources:
- `sdm/nn/sinusoidal.py:10-36`

---

## 4. Anomaly Detection: Diffusion Blocks and Residual Structures

Anomaly detection models within the Kumo suite use specialized temporal and feature attention blocks with gated residual connections (`ResidualBlock`) [sdm/models/kumo/timeseries/anomaly/block.py:12-161]().

```mermaid
graph TD
    subcode["Code Entity Space"]
        RB[ResidualBlock] --> TP[TransformerEncoderLayer: time_layer]
        RB --> FP[TransformerEncoderLayer: feature_layer]
        RB --> DP[Linear: diffusion_projection]
        RB --> SP[Linear: strategy_projection]
        RB --> CP[Conv1d: cond_projection]
    end
    subnlp["Natural Language Space"]
        TATT["Temporal Attention"] --> TP
        FATT["Feature Attention"] --> FP
        DIFF["Diffusion Step Embedding"] --> DP
        STRAT["Strategy Embedding"] --> SP
    end
    TATT -.-> TP
    FATT -.-> FP
    DIFF -.-> DP
    STRAT -.-> SP
```
*Sources: sdm/models/kumo/timeseries/anomaly/block.py:12-111()*

`ResidualBlock` accepts hidden feature tensors `[B, C, K, L]` (batch, channels, features, time length), side conditioning information, diffusion step embeddings, and masking-strategy embeddings [sdm/models/kumo/timeseries/anomaly/block.py:112-135](). If time or feature axes have length greater than 1, separate `TransformerEncoderLayer` instances process the sequence independently before normalization, gated chunking (`sigmoid` gating multiplied by `tanh` value), and output projections [sdm/models/kumo/timeseries/anomaly/block.py:136-161]().

Sources:
- `sdm/models/kumo/timeseries/anomaly/block.py:12-161`

---

## 5. Anomaly Detection: Embeddings and Noise Schedules

Conditioning and diffusion steps for anomaly detection are handled by dedicated embedding modules (`DiffusionEmbedding` and `SideEmbedding`) [sdm/models/kumo/timeseries/anomaly/embedding.py:11-168]().

`DiffusionEmbedding` maps discrete integer diffusion steps into continuous vector spaces via sinusoidal lookup tables and two linear projections activated by `SiLU` [sdm/models/kumo/timeseries/anomaly/embedding.py:11-79]().

`SideEmbedding` constructs multidimensional side information from continuous time coordinates and learned feature embeddings [sdm/models/kumo/timeseries/anomaly/embedding.py:81-168](). Time phases are computed using sinusoidal frequencies, normalized via layer norm, and concatenated with broadcasted feature embeddings and optional conditioning masks `[B, S, K, L]` [sdm/models/kumo/timeseries/anomaly/embedding.py:125-168]().

Sources:
- `sdm/models/kumo/timeseries/anomaly/embedding.py:11-168`

---


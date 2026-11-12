<!-- source: DeepWiki mcp.deepwiki.com · repo ruvnet/RuView · page 12 Research Extensions · fetched 2026-10-30 -->

# Research Extensions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/adr/ADR-179-occworld-candle-checkpoint-load-hardening.md](docs/adr/ADR-179-occworld-candle-checkpoint-load-hardening.md)
- [docs/research/sota-2026-05-22/PROGRESS.md](docs/research/sota-2026-05-22/PROGRESS.md)
- [docs/research/sota-2026-05-22/R5-subcarrier-saliency.md](docs/research/sota-2026-05-22/R5-subcarrier-saliency.md)
- [docs/research/sota-2026-05-22/R7-multilink-consistency.md](docs/research/sota-2026-05-22/R7-multilink-consistency.md)
- [docs/research/sota-2026-05-22/R8-rssi-only-count.md](docs/research/sota-2026-05-22/R8-rssi-only-count.md)
- [v2/crates/cog-person-count/cog/artifacts/saliency.json](v2/crates/cog-person-count/cog/artifacts/saliency.json)
- [v2/crates/nvsim-server/Cargo.toml](v2/crates/nvsim-server/Cargo.toml)
- [v2/crates/wifi-densepose-occworld-candle/src/cnn.rs](v2/crates/wifi-densepose-occworld-candle/src/cnn.rs)
- [v2/crates/wifi-densepose-occworld-candle/src/inference.rs](v2/crates/wifi-densepose-occworld-candle/src/inference.rs)
- [v2/crates/wifi-densepose-occworld-candle/src/lib.rs](v2/crates/wifi-densepose-occworld-candle/src/lib.rs)
- [v2/crates/wifi-densepose-occworld-candle/src/model.rs](v2/crates/wifi-densepose-occworld-candle/src/model.rs)
- [v2/crates/wifi-densepose-occworld-candle/src/transformer.rs](v2/crates/wifi-densepose-occworld-candle/src/transformer.rs)
- [v2/crates/wifi-densepose-occworld-candle/src/vqvae.rs](v2/crates/wifi-densepose-occworld-candle/src/vqvae.rs)
- [v2/crates/wifi-densepose-occworld-candle/tests/checkpoint_loading.rs](v2/crates/wifi-densepose-occworld-candle/tests/checkpoint_loading.rs)
- [v2/crates/wifi-densepose-occworld-candle/tests/input_validation.rs](v2/crates/wifi-densepose-occworld-candle/tests/input_validation.rs)
- [v2/crates/wifi-densepose-occworld-candle/tests/predict_honesty.rs](v2/crates/wifi-densepose-occworld-candle/tests/predict_honesty.rs)
- [v2/crates/wifi-densepose-pointcloud/Cargo.toml](v2/crates/wifi-densepose-pointcloud/Cargo.toml)
- [v2/crates/wifi-densepose-pointcloud/benches/splats_bench.rs](v2/crates/wifi-densepose-pointcloud/benches/splats_bench.rs)
- [v2/crates/wifi-densepose-pointcloud/src/pointcloud.rs](v2/crates/wifi-densepose-pointcloud/src/pointcloud.rs)

</details>



This page provides an overview of advanced research areas in the RuView ecosystem, including quantum/NV-diamond sensing, multivariate RF forecasting, multi-modal spatial research, and the State-of-the-Art (SOTA) research corpora (`docs/research/sota-2026-05-22/`). As a parent page, it introduces core concepts and links to detailed child pages.

Sources: [docs/research/sota-2026-05-22/PROGRESS.md:1-27]()

---

## 12.1 NVsim & Quantum Sensing

The `nvsim` crate and `nvsim-server` provide deterministic NV-diamond ensemble magnetometer simulation, Biot-Savart field computations, Lorentzian CW-ODMR responses, and MagFrame format serialization [v2/crates/nvsim-server/Cargo.toml:1-10](). They integrate with quantum-sensing and neural-decoding research documentation, including brain topology analysis.

### Code Entity Mapping: NVsim Pipeline
"Mapping quantum simulation crates to the server and observability dashboard."

```mermaid
flowchart TB
    subgraph ["nvsim Crate"]
        bfield["Biot-Savart Fields"]
        odmr["CW-ODMR Model"]
    end
    subgraph ["nvsim-server Crate"]
        server["nvsim-server binary\n(v2/crates/nvsim-server/src/main.rs)"]
        magframe["MagFrame Format\n(0xC51A_6E70)"]
    end
    subgraph ["Observability"]
        dashboard["NVsim Dashboard\n(Vite + Lit)"]
    end

    bfield --> server
    odmr --> server
    server -->|serializes| magframe
    magframe --> dashboard
```
Sources: [v2/crates/nvsim-server/Cargo.toml:1-28]()

For complete technical specifications, see the child page: [NVsim & Quantum Sensing](#12.1).

---

## 12.2 Forecasting & Predictive Memory

The `ruforecast` crate and associated pipelines handle independent Rust multivariate forecasting (ADR-348), zero-shot BIDMC evaluation scripts, governed local/fal training (ADR-349), and the `ruvector` predictive memory boundary (ADR-350), alongside clean-room and threat model documentation.

Sources: [docs/research/sota-2026-05-22/PROGRESS.md:28-56]()

For full details, see the child page: [Forecasting & Predictive Memory](#12.2).

---

## 12.3 Multi-Modal & Spatial Research

Multi-modal and spatial research spans multi-frequency mesh scanning (ADR-073), spiking neural CSI processing (ADR-074), RF tomography and SAR backprojection, iPhone LiDAR integration via `wifi-densepose-pointcloud`, off-axis head-coupled perspective demos (ADR-324), fal visual teacher LoRA, and the `examples/research-sota/` research corpus.

### Code Entity Mapping: SOTA Research & Pointcloud Pipeline
"Mapping SOTA research vectors and pointcloud voxelization benchmarks to code artifacts."

```mermaid
flowchart LR
    subgraph ["wifi-densepose-pointcloud"]
        bench["splats_bench.rs\n(to_gaussian_splats)"]
        pcl["pointcloud.rs"]
    end
    subgraph ["Research SOTA Corpus"]
        r5["r5_subcarrier_saliency.py"]
        r7["r7_multilink_consistency.py"]
        r8["r8_rssi_only_count.py"]
    end

    bench --> pcl
    r5 --> r8
    r7 --> r5
```
Sources: [v2/crates/wifi-densepose-pointcloud/benches/splats_bench.rs:1-35](), [docs/research/sota-2026-05-22/PROGRESS.md:30-67]()

For detailed documentation, see the child page: [Multi-Modal & Spatial Research](#12.3).

---

## Summary of Research Findings (SOTA 2026)

| Research Vector | Key Finding | Source |
| :--- | :--- | :--- |
| **RSSI-only Count (R8)** | Retains **94.82%** of full-CSI accuracy with 56× smaller input. | [docs/research/sota-2026-05-22/R8-rssi-only-count.md:21-30]() |
| **Subcarrier Saliency (R5)** | Count-task signal is **band-spread** (Max/Mean ratio 2.85×). | [docs/research/sota-2026-05-22/R5-subcarrier-saliency.md:44-57]() |
| **Adversarial Detection (R7)** | Stoer-Wagner mincut achieves **100%** detection rate across attacks. | [docs/research/sota-2026-05-22/R7-multilink-consistency.md:37-43]() |

Sources: [docs/research/sota-2026-05-22/PROGRESS.md:57-74]()

---

## Child Pages

| Child Page | Description |
| :--- | :--- |
| [NVsim & Quantum Sensing](#12.1) — The nvsim crate and nvsim-server: deterministic NV-diamond ensemble magnetometer simulation, Biot-Savart fields, ODMR response, MagFrame format, dashboard, and quantum-sensing/neural-decoding research docs including brain topology analysis. | Quantum simulation, MagFrame format, and Dashboard. |
| [Forecasting & Predictive Memory](#12.2) — ruforecast: independent Rust multivariate forecasting (ADR-348), zero-shot BIDMC evaluation scripts, governed local/fal training (ADR-349), ruvector predictive memory boundary (ADR-350), clean-room and threat model docs. | Multivariate forecasting, BIDMC evaluation, and ruvector memory. |
| [Multi-Modal & Spatial Research](#12.3) — Multi-frequency mesh scanning (ADR-073), spiking neural CSI processing (ADR-074), RF tomography/SAR backprojection, iPhone LiDAR integration, off-axis head-coupled perspective demos (ADR-324), fal visual teacher LoRA, and the research-sota example corpus. | Mesh scanning, SAR backprojection, point clouds, and research corpora. |

---

## Sources
- `docs/research/sota-2026-05-22/PROGRESS.md:1-74`
- `v2/crates/nvsim-server/Cargo.toml:1-29`
- `v2/crates/wifi-densepose-pointcloud/benches/splats_bench.rs:1-35`
- `docs/research/sota-2026-05-22/R8-rssi-only-count.md:21-30`
- `docs/research/sota-2026-05-22/R5-subcarrier-saliency.md:44-57`
- `docs/research/sota-2026-05-22/R7-multilink-consistency.md:37-43`

---


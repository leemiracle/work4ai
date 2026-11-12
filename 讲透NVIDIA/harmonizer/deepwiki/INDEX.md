# DeepWiki 索引 — NVIDIA/harmonizer

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 22 页 · 全文 138167 字符

- [1 Harmonizer: Project Overview](1-harmonizer-project-overview.md)
  - [1.1 Getting Started: Environment Setup & Checkpoint Download](1.1-getting-started-environment-setup-checkpoint-download.md)
  - [1.2 Repository Structure & Code Conventions](1.2-repository-structure-code-conventions.md)
- [2 Core Model Architecture](2-core-model-architecture.md)
  - [2.1 Pix2Pix_Turbo Wrapper](2.1-pix2pix-turbo-wrapper.md)
  - [2.2 Model Sub-modules: Pipeline, DiT, and Denoiser Scaling](2.2-model-sub-modules-pipeline-dit-and-denoiser-scaling.md)
  - [2.3 Cosmos-Predict2 Integration & Patches](2.3-cosmos-predict2-integration-patches.md)
- [3 Training Pipeline](3-training-pipeline.md)
  - [3.1 Data Curation & Dataset Preparation](3.1-data-curation-dataset-preparation.md)
  - [3.2 Loss Functions & Training Utilities](3.2-loss-functions-training-utilities.md)
  - [3.3 Multi-GPU Training Configuration](3.3-multi-gpu-training-configuration.md)
- [4 Inference](4-inference.md)
  - [4.1 Temporal Inference with the Pretrained Harmonizer](4.1-temporal-inference-with-the-pretrained-harmonizer.md)
  - [4.2 TensorRT-Accelerated Inference](4.2-tensorrt-accelerated-inference.md)
  - [4.3 Evaluation: Metrics & Test Dataset](4.3-evaluation-metrics-test-dataset.md)
- [5 ONNX Export & TensorRT Deployment](5-onnx-export-tensorrt-deployment.md)
  - [5.1 Exporting to ONNX](5.1-exporting-to-onnx.md)
  - [5.2 TensorRT Conversion & Inference](5.2-tensorrt-conversion-inference.md)
- [6 Project Governance & Legal](6-project-governance-legal.md)
  - [6.1 Licensing & Third-Party Attributions](6.1-licensing-third-party-attributions.md)
  - [6.2 Contributing & Security Reporting](6.2-contributing-security-reporting.md)
- [7 Glossary](7-glossary.md)

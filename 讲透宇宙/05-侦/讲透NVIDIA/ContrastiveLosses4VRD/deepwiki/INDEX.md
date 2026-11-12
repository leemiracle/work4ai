# DeepWiki 索引 — NVIDIA/ContrastiveLosses4VRD

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 21 页 · 全文 139057 字符

- [1 Overview](1-overview.md)
  - [1.1 Getting Started: Installation and Setup](1.1-getting-started-installation-and-setup.md)
  - [1.2 Datasets and Data Preparation](1.2-datasets-and-data-preparation.md)
- [2 Core Architecture](2-core-architecture.md)
  - [2.1 Model Builder and Generalized RCNN](2.1-model-builder-and-generalized-rcnn.md)
  - [2.2 Relationship Proposal Network (RelPN)](2.2-relationship-proposal-network-relpn.md)
  - [2.3 RelDN Head and Contrastive Losses](2.3-reldn-head-and-contrastive-losses.md)
- [3 Configuration System](3-configuration-system.md)
  - [3.1 Global Configuration Reference (lib/core/config.py)](3.1-global-configuration-reference-lib-core-config.py.md)
  - [3.2 Per-Dataset YAML Configuration Files](3.2-per-dataset-yaml-configuration-files.md)
- [4 Training Pipeline](4-training-pipeline.md)
  - [4.1 Training Script (train_net_step_rel.py)](4.1-training-script-train-net-step-rel.py.md)
  - [4.2 Data Loading and Minibatch Construction](4.2-data-loading-and-minibatch-construction.md)
  - [4.3 Dataset Layer (JsonDatasetRel and Catalog)](4.3-dataset-layer-jsondatasetrel-and-catalog.md)
- [5 Inference and Evaluation Pipeline](5-inference-and-evaluation-pipeline.md)
  - [5.1 Inference Engine (test_engine_rel.py and test_rel.py)](5.1-inference-engine-test-engine-rel.py-and-test-rel.py.md)
  - [5.2 Evaluation Metrics (task_evaluation_sg and task_evaluation_vg_and_vrd)](5.2-evaluation-metrics-task-evaluation-sg-and-task-evaluation-vg-and-vrd.md)
- [6 Utility Libraries](6-utility-libraries.md)
  - [6.1 Bounding Box and Spatial Feature Utilities](6.1-bounding-box-and-spatial-feature-utilities.md)
  - [6.2 Training Statistics, Logging, and Subprocess Utilities](6.2-training-statistics-logging-and-subprocess-utilities.md)
- [7 Glossary](7-glossary.md)

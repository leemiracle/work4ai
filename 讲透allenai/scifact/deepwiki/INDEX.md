# DeepWiki 索引 — allenai/scifact

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 21 页 · 全文 130765 字符

- [1 SciFact Overview](1-scifact-overview.md)
  - [1.1 Getting Started: Installation & Environment Setup](1.1-getting-started-installation-environment-setup.md)
  - [1.2 Dataset: Schema, Formats, and Claim Generation](1.2-dataset-schema-formats-and-claim-generation.md)
- [2 Verification Pipeline Architecture](2-verification-pipeline-architecture.md)
  - [2.1 Abstract Retrieval](2.1-abstract-retrieval.md)
  - [2.2 Rationale Selection](2.2-rationale-selection.md)
  - [2.3 Label Prediction](2.3-label-prediction.md)
  - [2.4 Prediction Merging and Pipeline Execution](2.4-prediction-merging-and-pipeline-execution.md)
- [3 Model Training](3-model-training.md)
  - [3.1 Training on SciFact, FEVER, and Snopes](3.1-training-on-scifact-fever-and-snopes.md)
  - [3.2 Transfer Learning: FEVER → SciFact](3.2-transfer-learning-fever-scifact.md)
- [4 Evaluation Framework](4-evaluation-framework.md)
  - [4.1 Metrics: Abstract-Level and Sentence-Level F1](4.1-metrics-abstract-level-and-sentence-level-f1.md)
  - [4.2 Component Evaluation Scripts and Leaderboard Submission](4.2-component-evaluation-scripts-and-leaderboard-submission.md)
- [5 COVID-19 Claim Verification](5-covid-19-claim-verification.md)
  - [5.1 COVID Pipeline Components: Retriever, Selector, Predictor](5.1-covid-pipeline-components-retriever-selector-predictor.md)
  - [5.2 verify_covid.py CLI and Report Generation](5.2-verify-covid.py-cli-and-report-generation.md)
- [6 Core Library: Data Models and Utilities](6-core-library-data-models-and-utilities.md)
  - [6.1 GoldDataset and Corpus Classes](6.1-golddataset-and-corpus-classes.md)
  - [6.2 PredictedDataset and Prediction Classes](6.2-predicteddataset-and-prediction-classes.md)
- [7 Glossary](7-glossary.md)

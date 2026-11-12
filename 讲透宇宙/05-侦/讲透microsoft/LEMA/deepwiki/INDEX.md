# DeepWiki 索引 — microsoft/LEMA

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 20 页 · 全文 114780 字符

- [1 LEMA: Overview and Architecture](1-lema-overview-and-architecture.md)
  - [1.1 Core Concepts and Methodology](1.1-core-concepts-and-methodology.md)
  - [1.2 Environment Setup and Dependencies](1.2-environment-setup-and-dependencies.md)
- [2 Data Generation: Correction Prompts](2-data-generation-correction-prompts.md)
  - [2.1 GSM8K and MATH Correction Prompts](2.1-gsm8k-and-math-correction-prompts.md)
  - [2.2 CommonsenseQA Correction Prompt](2.2-commonsenseqa-correction-prompt.md)
- [3 Training Pipeline](3-training-pipeline.md)
  - [3.1 Training Script Configuration (llama_2_70b_gsm8k.sh)](3.1-training-script-configuration-llama-2-70b-gsm8k.sh.md)
  - [3.2 QLoRA Fine-Tuning Engine (qlora.py)](3.2-qlora-fine-tuning-engine-qlora.py.md)
- [4 Inference and Evaluation Pipeline](4-inference-and-evaluation-pipeline.md)
  - [4.1 Adapter Merging (qlora_merge.py)](4.1-adapter-merging-qlora-merge.py.md)
  - [4.2 vLLM Batch Inference (vllm_inference.py)](4.2-vllm-batch-inference-vllm-inference.py.md)
  - [4.3 Answer Extraction and Accuracy Evaluation](4.3-answer-extraction-and-accuracy-evaluation.md)
- [5 Test Data Reference](5-test-data-reference.md)
  - [5.1 Math Benchmark Datasets (GSM8K and MATH)](5.1-math-benchmark-datasets-gsm8k-and-math.md)
  - [5.2 CommonsenseQA Dataset (csqa_dev.jsonl)](5.2-commonsenseqa-dataset-csqa-dev.jsonl.md)
- [6 Project Governance and Contributing](6-project-governance-and-contributing.md)
  - [6.1 License, Notice, and Code of Conduct](6.1-license-notice-and-code-of-conduct.md)
  - [6.2 Security Policy and Support Channels](6.2-security-policy-and-support-channels.md)
- [7 Glossary](7-glossary.md)

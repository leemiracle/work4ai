# Nemotron 3 RAG with Amazon Bedrock Knowledge Bases

An end-to-end retrieval-augmented generation (RAG) pipeline using NVIDIA Nemotron 3 with Amazon Bedrock Knowledge Bases and Bedrock Guardrails.

The notebook demonstrates:

- **Bedrock Knowledge Bases** backed by OpenSearch Serverless for document retrieval
- **Amazon Titan Text Embeddings V2** as the embedding model for data ingestion
- **Bedrock Guardrails** with content filters, denied topics, PII redaction, and word filters
- **`retrieve_and_generate` API** combining Knowledge Base retrieval + Nemotron generation + Guardrail enforcement in a single call

All resources (S3 bucket, IAM role, OpenSearch Serverless collection, Knowledge Base, Guardrail) are created programmatically, and the notebook includes cleanup steps. Sample documents for ingestion are in [`pdf_data/`](pdf_data/).

## Supported Models

| Model | Model ID | Parameters | Architecture |
|-------|----------|------------|-------------|
| Nemotron 3 Super | `nvidia.nemotron-super-3-120b` | 120B (12B active) | MoE + Hybrid Transformer-Mamba |
| Nemotron 3 Nano | `nvidia.nemotron-nano-3-30b` | 30B (3B active) | MoE + Hybrid Transformer-Mamba |

## Prerequisites

- AWS account with Bedrock model access enabled for NVIDIA Nemotron models and Amazon Titan Text Embeddings V2
- Permissions to create S3, IAM, OpenSearch Serverless, Bedrock Knowledge Base, and Bedrock Guardrail resources
- Python 3.10+
- `boto3` Python package
- AWS credentials configured via CLI, environment variables, or IAM role

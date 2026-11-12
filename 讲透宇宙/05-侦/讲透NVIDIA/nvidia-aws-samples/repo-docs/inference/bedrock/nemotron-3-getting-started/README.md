# Nemotron 3 Getting Started on Amazon Bedrock

A getting started guide for using NVIDIA Nemotron 3 models on Amazon Bedrock, covering inference, tool calling, streaming, and reasoning modes.

The notebook walks through three ways to interact with Nemotron models on Bedrock:

1. **OpenAI Chat Completions API** — use the familiar OpenAI SDK pointed at Bedrock's compatible endpoint
2. **InvokeModel API** — direct low-level Bedrock API access
3. **Converse API** — Bedrock's unified multi-model interface

Each API is demonstrated with basic inference (single and streaming), tool calling / function calling, reasoning mode via `reasoning_effort="high"`, and output parsing for reasoning traces.

## Supported Models

| Model | Model ID | Parameters | Architecture |
|-------|----------|------------|-------------|
| Nemotron 3 Super | `nvidia.nemotron-super-3-120b` | 120B (12B active) | MoE + Hybrid Transformer-Mamba |
| Nemotron 3 Nano | `nvidia.nemotron-nano-3-30b` | 30B (3B active) | MoE + Hybrid Transformer-Mamba |

## Prerequisites

- AWS account with Bedrock model access enabled for NVIDIA Nemotron models
- Python 3.10+
- `boto3` and `openai` Python packages
- For the OpenAI SDK: a Bedrock API key (created in the Bedrock console)
- For InvokeModel/Converse: AWS credentials configured via CLI, environment variables, or IAM role

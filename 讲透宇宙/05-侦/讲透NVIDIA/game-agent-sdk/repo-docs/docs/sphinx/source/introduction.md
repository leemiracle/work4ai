# Introduction
The Game Agent SDK provides on-device building blocks for AI companions, with a C99 ABI and a thin C++ wrapper for natural integration into game engines and other native applications. A companion uses artificial intelligence (AI) inferencing locally on the end user's GPU with a small language model (SLM). The SDK exposes three groups of APIs: **Agent** APIs for agentic loops, **Chat** APIs for direct inference, and **RAG** APIs for lexical, semantic, or hybrid knowledge retrieval over a developer-built corpus. Several examples are provided with the Game Agent SDK demonstrating how to use these APIs and how to compose them into a companion (see [Samples](samples.md)).

## Hardware Requirements
Any NVIDIA Ampere GPU architecture (or newer) is supported, as long as there is enough dedicated VRAM available on the NVIDIA GPU. See [Bundled Models](#bundled-models) below for VRAM estimates.

## Software Requirements
* Windows 10 or 11
* NVIDIA Driver version 570.65 or later
* Cuda 12.8 SDK or later

## Bundled Models
The release package bundles the following default models:

* Small Language Model (SLM): `Qwen3.5-4B-Q4_K_M`
* RAG embedding: `MiniLM-L6-v2.F32`, `multilingual-e5-base-Q8_0`
* GraphRAG re-ranking: `cross_encoder_ms-marco-MiniLM-L6-v2`

Approximate GPU VRAM usage:

| Component | GPU VRAM Usage |
| -------- | :-------: |
| SLM | 3.8 GB |
| RAG | 0.0 GB* |

*Performed on the host (CPU).
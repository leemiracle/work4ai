<!-- source: DeepWiki mcp.deepwiki.com · repo NirDiamant/agents-towards-production · page 4 Deployment & Infrastructure · fetched 2026-10-29 -->

# 4. Deployment & Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/repos_images/ai_architecture_diagram.svg](assets/repos_images/ai_architecture_diagram.svg)
- [tutorials/docker-intro/README.md](tutorials/docker-intro/README.md)
- [tutorials/runpod-gpu-deploy/README.md](tutorials/runpod-gpu-deploy/README.md)

</details>



This page covers production deployment strategies for AI agents, spanning from local containerization to scalable cloud GPU infrastructure and model customization. It provides a high-level overview of the transition from development prototypes to robust, enterprise-grade products.

For details on security, see [Security Framework](#3). For monitoring and observability details, see [Observability & Monitoring](#2.5).

## Overview

The deployment stack in the **Agents Towards Production** repository is designed to solve the "it works on my machine" problem by providing standardized environments and scalable execution runtimes.

| Component | Focus | Primary Tools |
| :--- | :--- | :--- |
| **Containerization** | Environment Consistency | Docker, Dockerfile |
| **Cloud Deployment** | Scalable Execution | RunPod, AWS Bedrock AgentCore |
| **Model Customization** | Domain Performance | Supervised Fine-Tuning (SFT), Ollama |

```mermaid
graph TD
    subgraph "Local Development"
        [code_logic] --> [requirements_txt]
    end

    subgraph "4.1 Containerization"
        [Dockerfile] --> [Docker_Image]
    end

    subgraph "4.2 Cloud Deployment"
        [Docker_Image] --> [RunPod_Serverless]
        [Docker_Image] --> [AWS_Bedrock_AgentCore]
    end

    subgraph "4.3 Model Customization"
        [Training_Data] --> [SFT_Fine_Tuning]
        [SFT_Fine_Tuning] --> [Custom_Model]
        [Custom_Model] --> [Ollama_Local_Host]
    end

    [RunPod_Serverless] --> [Production_API]
    [AWS_Bedrock_AgentCore] --> [Production_API]
    [Ollama_Local_Host] --> [On_Prem_API]
```
Sources: [tutorials/docker-intro/README.md:9-11](), [tutorials/runpod-gpu-deploy/README.md:31-38]()

---

## 4.1 Containerization

Containerization is the foundational layer for production agents. It ensures that the complex ecosystem of Python versions, ML libraries (like `torch` or `langchain`), and system dependencies remains consistent across environments.

*   **Reproducibility**: Docker solves the lack of reproducibility when shifting code between local and production environments [tutorials/docker-intro/README.md:95-99]().
*   **Dependency Management**: Agents often require specific GPU drivers or vector database clients that are packaged within the image [tutorials/docker-intro/README.md:11-12]().
*   **Volume Mounting**: Used for data persistence and local development without rebuilding images [tutorials/docker-intro/README.md:34-35]().

For details, see [Containerization](#4.1).

Sources: [tutorials/docker-intro/README.md:29-35](), [tutorials/docker-intro/README.md:85-93]()

---

## 4.2 Cloud Deployment

Scaling AI agents requires infrastructure that can handle unpredictable, resource-intensive GPU workloads without the overhead of managing raw virtual machines.

### RunPod Serverless
RunPod allows developers to package agents into containers and expose them via a `handler` function [tutorials/runpod-gpu-deploy/README.md:76-78]().
*   **The Handler Pattern**: Using the `runpod` SDK, a Python function is bound to execute when an endpoint is hit: `runpod.serverless.start({"handler": handler})` [tutorials/runpod-gpu-deploy/README.md:110-134]().
*   **Automatic Scaling**: Workers spin up and down based on request volume, ensuring cost efficiency [tutorials/runpod-gpu-deploy/README.md:52-54]().

### AWS Bedrock AgentCore
For managed enterprise environments, the `BedrockAgentCoreApp` SDK provides a decorator-based pattern (`@app.entrypoint`) to wrap agent logic as a production-ready HTTP service.

For details, see [Cloud Deployment](#4.2).

Sources: [tutorials/runpod-gpu-deploy/README.md:7-17](), [tutorials/runpod-gpu-deploy/README.md:134-135]()

---

## 4.3 Model Customization

Model customization bridges the gap between general-purpose LLMs and domain-specific agents through fine-tuning and specialized local hosting.

### Fine-Tuning (SFT)
Supervised Fine-Tuning (SFT) internalizes specialized knowledge and ensures consistent style, tone, and structured output formats like JSON [tutorials/fine-tuning-agents/fine_tuning_agents_guide.ipynb:20-45]().
*   **Training Data**: Requires specific message-based JSONL formats [tutorials/fine-tuning-agents/fine_tuning_agents_guide.ipynb:132-160]().

### On-Premises Hosting with Ollama
For privacy-conscious or low-latency applications, models can be hosted locally using Ollama. This is often integrated into the deployment stack to eliminate external API dependencies [tutorials/runpod-gpu-deploy/README.md:35-36]().

For details, see [Model Customization](#4.3).

Sources: [tutorials/runpod-gpu-deploy/README.md:35-36](), [tutorials/fine-tuning-agents/fine_tuning_agents_guide.ipynb:8-22]()

---

## Production Infrastructure Mapping

The following diagram maps high-level infrastructure concepts to specific code entities and files within the repository.

```mermaid
graph LR
    subgraph "Natural Language Space (Concepts)"
        [Deploy_Strategy] --> [Serverless_Compute]
        [Deploy_Strategy] --> [Container_Runtime]
        [Model_Strategy] --> [Fine_Tuning]
    end

    subgraph "Code Entity Space (Implementation)"
        [Serverless_Compute] --- handler_py["handler.py"]
        [Container_Runtime] --- docker_file["Dockerfile"]
        [Fine_Tuning] --- sft_notebook["fine_tuning_agents_guide.ipynb"]
        
        handler_py --> runpod_start["runpod.serverless.start()"]
        docker_file --> pip_install["uv pip install -r requirements.txt"]
    end
```
Sources: [tutorials/runpod-gpu-deploy/README.md:134-135](), [tutorials/runpod-gpu-deploy/README.md:149-153](), [tutorials/fine-tuning-agents/fine_tuning_agents_guide.ipynb:1-10]()

---


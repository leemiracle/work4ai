# NIM Build, Tune & Deploy Workshop

This repository contains hands-on notebooks for the NVIDIA NIM workshop, demonstrating how to build, fine-tune, and deploy Large Language Models using NVIDIA's AI stack.

## 🎯 Workshop Overview

Learn how to:
- Use NVIDIA NIM APIs for cloud-based inference
- Deploy NIM containers locally with GPU acceleration
- Fine-tune LLMs using LoRA (Low-Rank Adaptation) with NeMo
- Deploy custom LoRA adapters with NIM for production use

## 📚 Workshop Notebooks

1. **[00_Workshop_Setup.ipynb](00_Workshop_Setup.ipynb)** - Initial setup and environment configuration
2. **[01_NIM_API_Tutorial.ipynb](01_NIM_API_Tutorial.ipynb)** - Introduction to NVIDIA NIM cloud APIs
3. **[02_Local_NIM_Deployment.ipynb](02_Local_NIM_Deployment.ipynb)** - Deploy NIM containers locally
4. **[03_LoRA_Training_NeMo.ipynb](03_LoRA_Training_NeMo.ipynb)** - Fine-tune models with LoRA
5. **[04_Deploy_LoRA_with_NIM.ipynb](04_Deploy_LoRA_with_NIM.ipynb)** - Deploy LoRA adapters

## 🚀 Prerequisites

- NVIDIA GPU (A100, V100, or similar)
- Docker with NVIDIA Container Runtime
- Python 3.8+
- NGC Account (free at [ngc.nvidia.com](https://ngc.nvidia.com))
- NVIDIA API Key (get one at [build.nvidia.com](https://build.nvidia.com))

## 🔑 API Keys Setup

This workshop requires three API keys (stored in a `.env` file):
- **NVIDIA_API_KEY**: For accessing NVIDIA's cloud API services
- **NGC_API_KEY**: For downloading NIM containers from NVIDIA GPU Cloud
- **NGC_CLI_API_KEY**: For NGC CLI operations (optional, uses NGC_API_KEY as fallback)

The setup notebook (00_Workshop_Setup.ipynb) will guide you through obtaining and configuring these keys.

## 🛠️ Quick Start

1. Clone this repository:
```bash
git clone https://github.com/snaic-org/NIM-build-tune-deploy-participant.git
cd NIM-build-tune-deploy-participant
```

2. Run the setup notebook:
```bash
jupyter notebook 00_Workshop_Setup.ipynb
```

3. Follow the notebooks in order (00 → 01 → 02 → 03 → 04)

## 📁 Repository Structure

```
NIM-build-tune-deploy-participant/
├── 00_Workshop_Setup.ipynb         # Environment setup & API key configuration
├── 01_NIM_API_Tutorial.ipynb       # Cloud API tutorial
├── 02_Local_NIM_Deployment.ipynb   # Local deployment
├── 03_LoRA_Training_NeMo.ipynb     # LoRA training
├── 04_Deploy_LoRA_with_NIM.ipynb   # LoRA deployment
├── openai_example/                 # OpenAI API compatibility examples
│   └── openai_api_example.ipynb   # Example using OpenAI client with NIM
├── lora_tutorial/                  # Training data and configs
│   └── data/                       # Sample datasets
├── ngc-cli/                        # NGC CLI scripts
├── img/                            # Workshop images
└── .env                            # API keys (create this file)
```

## 🔧 Key Technologies

- **NVIDIA NIM**: Inference microservices for optimized model deployment
- **NeMo Framework**: For training and fine-tuning LLMs
- **LoRA**: Efficient fine-tuning technique
- **Docker**: Container-based deployment
- **NGC (NVIDIA GPU Cloud)**: Container registry and model repository

## 📝 Notes

- The workshop uses Llama 3.1 8B Instruct as the base model
- NIM containers require significant disk space (~50GB per model)
- First-time model downloads may take 5-10 minutes
- Subsequent runs use cached models for faster startup

## 🐛 Troubleshooting

If you encounter issues:
1. Ensure all API keys are properly set in the `.env` file
2. Verify Docker and NVIDIA Container Runtime are installed
3. Check that your GPU has sufficient memory (16GB+ recommended)
4. Confirm you have enough disk space for model caching

## 📄 License

This workshop material is provided for educational purposes. Model usage is subject to respective model licenses. 

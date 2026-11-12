> 来源: [https://deepwiki.com/kvcache-ai/ktransformers/13-troubleshooting-and-faq](https://deepwiki.com/kvcache-ai/ktransformers/13-troubleshooting-and-faq)
> DeepWiki kvcache-ai/ktransformers | Last indexed: 30 April 2026 (02be2b

# Troubleshooting and FAQ

  Relevant source files 
 - [README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1)
 - [doc/README.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/README.md?plain=1)
 - [doc/SUMMARY.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/SUMMARY.md?plain=1)
 - [doc/en/DeepseekR1_V3_tutorial.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1)
 - [doc/en/FAQ.md](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/FAQ.md?plain=1)
 - [kt-kernel/python/cli/commands/version.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/commands/version.py)
 - [kt-kernel/python/cli/i18n.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/i18n.py)
 - [kt-kernel/python/cli/utils/environment.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/utils/environment.py)
 - [kt-kernel/python/cli/utils/sglang_checker.py](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/utils/sglang_checker.py)
 
  This page provides solutions to common issues encountered when installing, building, and running KTransformers. It covers both `kt-kernel` (inference) and `kt-sft` (fine-tuning) modules, addressing installation failures, runtime errors, performance problems, and model-specific issues.

 
---

 
## Installation and Environment Issues

 
### Unified CLI Diagnostics (`kt doctor`)

 The `kt-cli` provides a built-in diagnostic tool to identify environment mismatches, missing dependencies, or hardware incompatibilities.

 **Command**:

 
```

```

 **Functionality**:

 
 - **Python Check**: Verifies the current Python environment and version [kt-kernel/python/cli/i18n.py122](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/i18n.py#L122-L122)
 - **Hardware Detection**: Identifies GPUs, VRAM, CPU cores, and NUMA topology [kt-kernel/python/cli/i18n.py124-127](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/i18n.py#L124-L127)
 - **ISA Verification**: Specifically checks for `AVX2`, `AVX512`, and `AMX` which are critical for `kt-kernel` performance [kt-kernel/python/cli/i18n.py138-139](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/i18n.py#L138-L139)
 - **Package Audit**: Checks versions of `kt-kernel`, `sglang-kt`, `torch`, and `transformers` [kt-kernel/python/cli/i18n.py38-41](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/i18n.py#L38-L41)
 
 **Sources**: [kt-kernel/python/cli/i18n.py120-142](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/i18n.py#L120-L142) [kt-kernel/python/cli/utils/environment.py63-72](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/utils/environment.py#L63-L72)

 
---

 
### SGLang Installation Issues

 KTransformers requires a specific fork of SGLang (`sglang-kt`) for optimal integration, particularly for features like the Triton MLA kernel [doc/en/DeepseekR1_V3_tutorial.md96-97](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L96-L97)

 **Problem**: `ImportError: No module named 'sglang'` or version mismatch.

 **Diagnosis**: The `kt-cli` checks for `sglang-kt` specifically to ensure the `kvcache-ai` fork is present [kt-kernel/python/cli/utils/sglang_checker.py18-42](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/utils/sglang_checker.py#L18-L42) It verifies if the package was installed from the fork's repository or as the `sglang-kt` package [kt-kernel/python/cli/utils/sglang_checker.py51-53](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/utils/sglang_checker.py#L51-L53)

 **Solutions**:

 
 - **One-click install**: Run `./install.sh` from the root directory [kt-kernel/python/cli/utils/sglang_checker.py195-197](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/utils/sglang_checker.py#L195-L197)
 - **Pip install**: `pip install sglang-kt` [kt-kernel/python/cli/utils/sglang_checker.py199-200](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/utils/sglang_checker.py#L199-L200)
 - **Source install**: 
```

```
 
 **Sources**: [kt-kernel/python/cli/utils/sglang_checker.py18-205](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/utils/sglang_checker.py#L18-L205) [kt-kernel/python/cli/commands/version.py18-50](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/commands/version.py#L18-L50)

 
---

 
### CPU Variant Detection and Overrides

 `kt-kernel` uses runtime detection to load the most optimized C++ extension for your CPU.

 **Logic Flow (Natural Language to Code Entities)**:

 
```

```

 **Common Variant Issues**:

 
| Symptom | Cause | Fix |
|---|---|---|
| Illegal Instruction | Binary uses AMX on non-AMX CPU | export KT_KERNEL_CPU_VARIANT=avx512 |
| Slow Inference | Loaded avx2 on amx CPU | Check BIOS for AMX/AVX512 enablement |
| ModuleNotFound | .so file missing for variant | Use kt doctor to check detected features kt-kernel/python/cli/i18n.py95-97 |

 **Sources**: [kt-kernel/python/cli/utils/environment.py40-49](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/utils/environment.py#L40-L49) [kt-kernel/python/cli/i18n.py94-107](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/i18n.py#L94-L107) [README.md65-68](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L65-L68)

 
---

 
## Runtime and Performance Troubleshooting

 
### CUDA Out of Memory (OOM)

 When running large models like DeepSeek-V3/R1 (671B) on limited VRAM (e.g., 24GB), memory pressure is high.

 **Memory Optimization Rules**:

 
 - **Expert Offloading**: KTransformers allows running the 671B model using as little as 14GB VRAM by offloading experts to DRAM [doc/en/DeepseekR1_V3_tutorial.md52](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L52-L52)
 - **KV Cache Fraction**: Adjust the proportion of VRAM allocated to the KV cache. V0.2.1 supports longer context (8K) in 24GB VRAM by integrating the Triton MLA kernel [doc/en/DeepseekR1_V3_tutorial.md63](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L63-L63)
 - **Multi-GPU**: If a single GPU OOMs, distribute the model across multiple GPUs using the multi-GPU configuration [doc/en/DeepseekR1_V3_tutorial.md69-71](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L69-L71)
 
 **Sources**: [doc/en/DeepseekR1_V3_tutorial.md52-72](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L52-L72) [README.md43-46](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L43-L46)

 
---

 
### Performance Bottlenecks

 **Problem**: Inference speed is significantly lower than benchmarks.

 **Diagnosis Tree**:

 
```

```

 **Key Performance Factors**:

 
 - **CPU Architecture**: AMX-based MoE kernels (V0.3+) provide significant speedups over standard implementations [doc/en/DeepseekR1_V3_tutorial.md54](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L54-L54)
 - **NUMA Topology**: On dual-socket systems, performance improves when utilizing both NUMA nodes correctly [doc/en/DeepseekR1_V3_tutorial.md54-58](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L54-L58)
 - **Memory Bandwidth**: Performance is often constrained by CPU memory bandwidth; ensure high-speed DRAM (e.g., DDR5-4800) is used [doc/en/DeepseekR1_V3_tutorial.md65-78](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L65-L78)
 
 **Sources**: [doc/en/DeepseekR1_V3_tutorial.md52-78](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L52-L78) [kt-kernel/python/cli/utils/environment.py40-61](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/utils/environment.py#L40-L61)

 
---

 
## Model and Quantization FAQ

 
### Supported Quantization Methods

 KTransformers supports multiple backends depending on hardware capabilities:

 
| Method | Target Hardware | Precision | Feature |
|---|---|---|---|
| AMX-INT8 | Intel Sapphire Rapids+ | 8-bit | High-speed CPU MoE README.md39 |
| AMX-BF16 | Intel Sapphire Rapids+ | BF16 | Native precision README.md39 |
| IQ1_S/FP8 | Modern GPUs / CPUs | Mixed | Hybrid weights README.md43 |
| GGUF (Q4_K_M) | General CPU | 4-bit | llama.cpp compatibility doc/en/DeepseekR1_V3_tutorial.md52 |

 **Sources**: [README.md39-51](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L39-L51) [doc/en/DeepseekR1_V3_tutorial.md52-60](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L52-L60)

 
---

 
### R1 "No Thinking" Issue

 **Problem**: DeepSeek-R1 does not produce the `<think>` block or reasoning steps.

 **Solution**: This is often related to the prompt format or the specific quantization used. Ensure you are using the correct chat template and that the model has not been over-quantized in a way that affects its reasoning capabilities [doc/en/DeepseekR1_V3_tutorial.md33-35](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L33-L35)

 **Sources**: [doc/en/DeepseekR1_V3_tutorial.md33-35](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/doc/en/DeepseekR1_V3_tutorial.md?plain=1#L33-L35)

 
---

 
## kt-sft (Fine-Tuning) Troubleshooting

 
### Training Speed and Memory

 **FAQ**: Why is KTransformers SFT faster than ZeRO-Offload? **Answer**: KTransformers uses a heterogeneous training architecture that is 6-12x faster than ZeRO-Offload for large MoE models while using about half the CPU memory [README.md100-101](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L100-L101)

 **Common Issues**:

 
 - **LLaMA-Factory Integration**: Ensure the environment is correctly set up using `kt-sft` mode in the CLI [kt-kernel/python/cli/i18n.py59](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/i18n.py#L59-L59)
 - **Quantization in Training**: KTransformers supports INT8/INT4 quantization for CPU/GPU hybrid fine-tuning to fit ultra-large models [README.md98-99](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L98-L99)
 
 **Sources**: [README.md91-103](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/README.md?plain=1#L91-L103) [kt-kernel/python/cli/i18n.py58-60](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/i18n.py#L58-L60)

 
---

 
## Common Error Messages and Solutions

 
| Error Message | Meaning | Solution |
|---|---|---|
| SGLang is not installed | Missing serving dependency | Run pip install sglang-kt or install.sh kt-kernel/python/cli/utils/sglang_checker.py191-200 |
| CUDA Version: Not found | NVIDIA drivers or toolkit missing | Check nvidia-smi and ensure drivers are installed kt-kernel/python/cli/utils/environment.py192-207 |
| version_not_installed | A required package is missing | Use kt doctor to identify the missing component kt-kernel/python/cli/i18n.py42 |
| Failed to install system deps | OS package manager error | Manually install required system libraries (e.g., libnuma-dev) kt-kernel/python/cli/i18n.py90-93 |

 **Sources**: [kt-kernel/python/cli/utils/sglang_checker.py155-205](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/utils/sglang_checker.py#L155-L205) [kt-kernel/python/cli/i18n.py32-107](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/i18n.py#L32-L107) [kt-kernel/python/cli/utils/environment.py192-218](https://github.com/kvcache-ai/ktransformers/blob/02be2bf5/kt-kernel/python/cli/utils/environment.py#L192-L218)

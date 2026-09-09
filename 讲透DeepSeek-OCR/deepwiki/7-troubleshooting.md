> 来源: [https://deepwiki.com/deepseek-ai/DeepSeek-OCR/7-troubleshooting](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/7-troubleshooting)
> DeepWiki deepseek-ai/DeepSeek-OCR

# Troubleshooting

  Relevant source files 
 - [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py)
 - [README.md](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1)
 - [requirements.txt](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/requirements.txt)
 
  This page provides solutions to common issues encountered when installing, configuring, and using DeepSeek-OCR. It covers problems specific to both the vLLM and Transformers inference frameworks, as well as general system issues.

 For configuration details, see [Configuration System](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.3-configuration-system). For framework-specific usage guidance, see [vLLM Inference](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.2-vllm-inference) or [Transformers Inference](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/3.1-transformers-inference). For model architecture details that may help diagnose issues, see [Model Architecture](https://deepwiki.com/deepseek-ai/DeepSeek-OCR/4.2-model-architecture).

 
---

 
## Diagnostic Overview

 
```

```

 **Sources:** [README.md68-106](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L68-L106) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py1-43](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L1-L43)

 
---

 
## Installation Issues

 
### CUDA and PyTorch Compatibility

 **Problem:** Version mismatches between CUDA, PyTorch, and vLLM cause import errors or runtime failures.

 **Required Versions:**

 
| Component | Version | Notes |
|---|---|---|
| CUDA | 11.8 | Specified in README README.md69 |
| PyTorch | 2.6.0 | Required for vLLM 0.8.5 README.md83 |
| vLLM | 0.8.5+cu118 | CUDA 11.8 wheel README.md81-84 |
| flash-attn | 2.7.3 | Must match CUDA version README.md86 |

 **Solution:**

 
```

```

 **Common Error:**

 
```
ImportError: cannot import name 'flash_attn_cuda' from 'flash_attn'
```

 This indicates CUDA version mismatch. Verify CUDA installation:

 
```

```

 **Sources:** [README.md68-86](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L68-L86)

 
---

 
### vLLM Installation Failures

 **Problem 1:** Wrong wheel file for your Python version

 The provided wheel `vllm-0.8.5+cu118-cp38-abi3-manylinux1_x86_64.whl` uses the stable ABI (`abi3`), which is compatible with Python 3.8+. However, download failures or architecture mismatches can occur.

 **Solution:**

 
 - Ensure Python 3.12.9 as specified in [README.md76](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L76-L76): `python --version`
 - Download the wheel from the official release: [https://github.com/vllm-project/vllm/releases/tag/v0.8.5](https://github.com/vllm-project/vllm/releases/tag/v0.8.5) [README.md81](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L81-L81)
 - Verify wheel compatibility: `pip debug --verbose | grep "Compatible tags"`
 
 **Problem 2:** Transformers version conflict warning

 The README notes:

 
> **Note:** if you want vLLM and transformers codes to run in the same environment, you don't need to worry about this installation error like: vllm 0.8.5+cu118 requires transformers>=4.51.1 [README.md88](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L88-L88)

 **Solution:** This warning is expected and can be ignored. The DeepSeek-OCR implementation uses custom model code that bypasses the version check. Both frameworks will work in the same environment despite the warning.

 **Sources:** [README.md80-88](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L80-L88)

 
---

 
### Flash Attention Build Errors

 **Problem:** Flash attention fails to compile with errors like:

 
```
error: 'cutlass' namespace not found
```

 **Solution:**

 
 - **Ensure no build isolation:** The `--no-build-isolation` flag is critical [README.md86](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L86-L86)

 
```

```
 - **Verify CUDA toolkit availability:**

 
```

```

 If not set:

 
```

```
 - **Check GCC version:** Flash attention requires GCC 7-11

 
```

```
 - **Pre-built wheels alternative:** If compilation fails, use pre-built wheels:

 
```

```
 
 **Sources:** [README.md85-86](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L85-L86)

 
---

 
## Model Loading Issues

 
### Download Failures

 **Problem:** Model fails to download from Hugging Face Hub

 **Common Errors:**

 
```
requests.exceptions.ConnectionError: HTTPSConnectionPool
OSError: We couldn't connect to 'https://huggingface.co'
```

 **Solution 1: Network Configuration**

 
```

```

 **Solution 2: Manual Download**

 
```

```

 **Solution 3: Use Snapshot Download**

 
```

```

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py17](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L17-L17)

 
---

 
### Weight Loading Errors

 **Problem:** Model weights fail to load with shape mismatches or missing keys

 **Error Example:**

 
```
RuntimeError: Error(s) in loading state_dict for DeepseekOCRForCausalLM:
    size mismatch for vision.clip_model.embeddings.position_embedding
```

 **Diagnostic Steps:**

 
 - **Verify model checkpoint integrity:**

 
```

```
 - **Check for incomplete downloads:**

 
```

```
 
 **Solution:**

 
```

```

 **Sources:** [README.md124-125](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L124-L125) [README.md174-175](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L174-L175)

 
---

 
### Trust Remote Code Issues

 **Problem:** Model fails to load without `trust_remote_code=True`

 **Error:**

 
```
ValueError: Loading this model requires you to execute code in the model repository.
Set `trust_remote_code=True` to proceed.
```

 **Explanation:** DeepSeek-OCR uses custom model architecture code. Both loading methods require this flag:

 **vLLM:**

 
```

```

 **Transformers:**

 
```

```

 **Security Note:** Only set `trust_remote_code=True` for trusted model sources. Review custom code at: [https://huggingface.co/deepseek-ai/DeepSeek-OCR/tree/main](https://huggingface.co/deepseek-ai/DeepSeek-OCR/tree/main)

 **Sources:** [README.md173-175](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L173-L175)

 
---

 
## Memory Issues

 
### GPU Out of Memory (OOM)

 
```

```

 **Problem:** CUDA out of memory during inference

 **Configuration Parameters:**

 
| Parameter | Location | Default | Memory Impact |
|---|---|---|---|
| MAX_CROPS | config.py:12 | 6 | High - Each crop adds ~256 tokens DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py12 |
| MAX_CONCURRENCY | config.py:13 | 100 | High - Controls batch size DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py13 |
| BASE_SIZE | config.py:8 | 1024 | Medium - Global view resolution DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py8 |
| IMAGE_SIZE | config.py:9 | 640 | Medium - Local crop resolution DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py9 |
| CROP_MODE | config.py:10 | True | High - Enables multi-crop processing DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py10 |

 **Solution Strategy:**

 **Step 1: Reduce Concurrent Sequences (vLLM)**

 
```

```

 **Step 2: Limit Maximum Crops**

 
```

```

 **Step 3: Use Smaller Resolution Mode**

 
```

```

 **Step 4: Adjust vLLM Memory Settings**

 
```

```

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py1-13](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L1-L13) [README.md122-129](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L122-L129)

 
---

 
### CPU Memory Issues

 **Problem:** Out of memory during image preprocessing with large datasets

 **Error:**

 
```
MemoryError: Unable to allocate array with shape (4096, 4096, 3)
```

 **Cause:** The `NUM_WORKERS` parameter controls parallel image preprocessing workers. Default is 64 [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py14](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L14-L14)

 **Solution:**

 
```

```

 **Memory Usage Estimate:**

 
 - Each worker loads and processes one image via Pillow [requirements.txt8](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/requirements.txt#L8-L8)
 - Typical image: ~50MB in memory (4000×3000 RGB)
 - 64 workers × 50MB = ~3.2GB minimum overhead.
 
 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py14](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L14-L14) [requirements.txt8-9](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/requirements.txt#L8-L9)

 
---

 
## vLLM Specific Issues

 
### Engine Initialization Failures

 **Problem:** AsyncLLMEngine fails to initialize

 **Error:**

 
```
RuntimeError: CUDA error: out of memory during model loading
```

 **Solution 1: Reduce Memory Footprint**

 
```

```

 **Error:**

 
```
ValueError: Cannot find model 'deepseek-ai/DeepSeek-OCR' in vLLM registry
```

 **Solution 2: Verify vLLM Version** The model is supported in:

 
 - vLLM 0.8.5+ (bundled version) [README.md81](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L81-L81)
 - vLLM nightly builds (upstream support as of 2025/10/23) [README.md109-115](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L109-L115)
 
 
```

```

 For upstream vLLM installation [README.md111-115](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L111-L115):

 
```

```

 **Sources:** [README.md108-115](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L108-L115) [README.md122-128](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L122-L128)

 
---

 
### Logits Processor Errors

 **Problem:** `NGramPerReqLogitsProcessor` causes warnings or unexpected behavior

 **Error:**

 
```
UserWarning: NGramPerReqLogitsProcessor whitelist_token_ids not set
```

 **Explanation:** The `NGramPerReqLogitsProcessor` prevents repetitive n-gram sequences in output [README.md120](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L120-L120) It requires configuration through `extra_args` in `SamplingParams`.

 **Correct Configuration:**

 
```

```

 **Common Mistakes:**

 
 - Not passing `whitelist_token_ids` for table tags [README.md154](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L154-L154)
 - Setting `ngram_size` too small (< 20) - causes over-suppression.
 - Not including processor in `LLM` initialization [README.md128](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L128-L128)
 
 **Sources:** [README.md119-128](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L119-L128) [README.md146-157](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L146-L157)

 
---

 
### SKIP_REPEAT Policy Issues

 **Problem:** Incomplete outputs are discarded entirely

 The `SKIP_REPEAT` configuration in `config.py` controls handling of incomplete generations:

 
```

```

 **Behavior:**

 
 - `True`: Sequences hitting `max_tokens` without proper termination are skipped.
 - `False`: All outputs returned, even if truncated.
 
 **Solution:** For batch processing where some truncation is acceptable:

 
```

```

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py16](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L16-L16)

 
---

 
## Transformers Specific Issues

 
### Attention Implementation Errors

 **Problem:** Flash attention not working or causing errors

 **Error:**

 
```
NotImplementedError: Flash Attention is not available for your configuration
```

 **Cause:** `_attn_implementation='flash_attention_2'` [README.md175](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L175-L175) requires:

 
 - Flash attention installed correctly [README.md86](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L86-L86)
 - CUDA-compatible GPU (compute capability ≥ 8.0 for optimal performance)
 - Proper PyTorch version [README.md83](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L83-L83)
 
 **Solution:**

 **Option 1: Verify Flash Attention**

 
```

```

 **Option 2: Fallback to Standard Attention**

 
```

```

 **Sources:** [README.md83-86](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L83-L86) [README.md174-175](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L174-L175)

 
---

 
### Device Placement Issues

 **Problem:** Model not moving to GPU or CUDA errors

 **Error:**

 
```
RuntimeError: Expected all tensors to be on the same device
```

 **Solution:**

 **Ensure proper device setup:**

 
```

```

 **Mixed precision issues:**

 
```

```

 **Sources:** [README.md170-176](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L170-L176)

 
---

 
## Image Processing Issues

 
### Unsupported Image Formats

 **Problem:** Image fails to load or process

 **Error:**

 
```
PIL.UnidentifiedImageError: cannot identify image file
```

 **Supported Formats:**

 
 - JPEG (.jpg, .jpeg) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py21](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L21-L21)
 - PNG (.png) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py21](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L21-L21)
 - PDF (.pdf) - via PyMuPDF [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py20](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L20-L20) [requirements.txt3](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/requirements.txt#L3-L3)
 
 **Solution:** Ensure images are converted to RGB using Pillow [requirements.txt8](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/requirements.txt#L8-L8) before processing [README.md132-133](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L132-L133)

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py19-22](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L19-L22) [README.md132-133](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L132-L133) [requirements.txt3-8](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/requirements.txt#L3-L8)

 
---

 
### Dynamic Cropping Failures

 **Problem:** Image cropping produces unexpected results or errors

 **Configuration Options:**

 
```

```

 **Diagnostic:**

 
```

```

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py8-15](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L8-L15)

 
---

 
## Output Quality Issues

 
### Repetitive Text Output

 
```

```

 **Problem:** Model outputs repeated text patterns.

 **vLLM Solution:** Ensure `NGramPerReqLogitsProcessor` is properly configured in `SamplingParams` [README.md147-157](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L147-L157)

 **Transformers Solution:** Use `model.infer` with specific parameters [README.md183](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L183-L183):

 
```

```

 **Sources:** [README.md146-157](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L146-L157) [README.md183](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L183-L183)

 
---

 
### Incomplete or Truncated Output

 **Problem:** Output ends mid-sentence.

 **Cause 1: Token Limit Reached** Check `max_tokens` setting (default in example is 8192 [README.md149](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L149-L149)).

 **Cause 2: SKIP_REPEAT Policy** If `SKIP_REPEAT = True`, vLLM may discard the output entirely if it hits `max_tokens` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py16](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L16-L16)

 **Sources:** [README.md149](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L149-L149) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py16](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L16-L16)

 
---

 
### Reference Tag Parsing Errors

 **Problem:** Special tokens appear in output or coordinates are incorrect.

 **Expected Behavior:**

 
 - `<|ref|>...<|/ref|>`: Text reference markers [README.md207](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L207-L207)
 - `<|grounding|>`: Spatial awareness token [README.md179-202](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L179-L202)
 
 **Prompt Examples for Reference:**

 
```

```

 **Sources:** [README.md179-183](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L179-L183) [README.md201-209](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L201-L209)

 
---

 
## Performance Issues

 
### Slow Inference Speed

 
```

```

 **Problem:** Inference is slower than expected throughput.

 **Expected Performance:**

 
 - vLLM on A100-40G: ~2500 tokens/s for PDF processing [README.md100](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L100-L100)
 
 **vLLM Optimization:**

 
```

```

 **Sources:** [README.md100](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L100-L100) [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py13-14](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L13-L14)

 
---

 
### Path Configuration Errors

 **Problem:** Input/output paths not set or incorrect.

 **Error:**

 
```
FileNotFoundError: INPUT_PATH is empty or does not exist
```

 **Solution:** Update `INPUT_PATH` and `OUTPUT_PATH` in `config.py` [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py24-25](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L24-L25)

 **Script-Path Mapping [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py20-22](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L20-L22):**

 
| Script | Supported INPUT_PATH |
|---|---|
| run_dpsk_ocr_image.py | .jpg, .png, .jpeg |
| run_dpsk_ocr_pdf.py | .pdf |
| run_dpsk_ocr_eval_batch.py | Omnidocbench images path |

 **Sources:** [DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py19-25](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py#L19-L25)

 
---

 
## Getting Help

 If you encounter issues not covered in this troubleshooting guide:

 
 - **Check the GitHub Issues:** [https://github.com/deepseek-ai/DeepSeek-OCR/issues](https://github.com/deepseek-ai/DeepSeek-OCR/issues)
 - **Join Discord:** [https://discord.gg/Tc7c45Zzu5](https://discord.gg/Tc7c45Zzu5) [README.md25](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L25-L25)
 - **Review the paper:** [DeepSeek_OCR_paper.pdf](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/DeepSeek_OCR_paper.pdf) [README.md37](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L37-L37)
 
 **Sources:** [README.md24-39](https://github.com/deepseek-ai/DeepSeek-OCR/blob/09eaf526/README.md?plain=1#L24-L39)

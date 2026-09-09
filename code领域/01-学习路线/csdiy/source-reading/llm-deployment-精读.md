# LLM 部署精读：从模型到生产服务

> 参照：vLLM / TGI / TensorRT-LLM / Ollama / llama.cpp
>
> csdiy 对应：kv-cache精读 + model-compression精读 + model-parallel精读 + tinyllm

---

## 一、LLM 部署全景

```
模型权重 (.safetensors)
  ↓ 加载
推理引擎 (vLLM / TGI / TRT-LLM)
  ↓ 优化
  ├── 量化 (INT4/INT8)
  ├── KV Cache (PagedAttention)
  ├── Flash Attention
  ├── Continuous Batching
  └── Tensor Parallelism
  ↓ 服务
API Server (OpenAI 兼容 / 自定义)
  ↓ 用户
客户端 (curl / Python SDK / Chat UI)
```

---

## 二、主流推理引擎对比

| 引擎 | 开发者 | 优势 | 劣势 | 适合 |
|------|--------|------|------|------|
| **vLLM** | UC Berkeley | PagedAttention + 高吞吐 | 显存占用大 | GPU 服务端 |
| **TGI** | HuggingFace | 兼容性好 + 模型支持广 | 比 vLLM 慢 10-20% | HuggingFace 生态 |
| **TensorRT-LLM** | NVIDIA | 最快（INT4 + kernel 融合） | 只支持 NVIDIA GPU | 生产极致性能 |
| **llama.cpp** | ggerganov | CPU/混合精度/最小依赖 | CPU 慢 | 边缘/个人 |
| **Ollama** | Ollama | 一键部署 + Docker | 封装层 → 灵活性低 | 快速试用 |
| **MLC-LLM** | TVM | 手机/GPU/浏览器 | 编译复杂 | 跨平台 |
| **LightLLM** | 三人行 | 纯 Python 可改 | 生态小 | 研究/定制 |

---

## 三、vLLM 部署详解

### 架构

```
vLLM Server:
  ├── AsyncLLMEngine（异步引擎）
  │   ├── Scheduler（调度器）
  │   │   ├── PagedAttention（KV Cache 管理）
  │   │   └── Continuous Batching（动态批处理）
  │   ├── Model Executor
  │   │   ├── Tensor Parallel（多 GPU）
  │   │   ├── Flash Attention
  │   │   └── CUDA Graph（kernel 融合）
  │   └── Tokenizer
  └── OpenAI API Server（FastAPI）
```

### 部署命令

```bash
# 基础部署
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-8B-Instruct \
    --tensor-parallel-size 1 \
    --max-model-len 8192

# 量化部署
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-70B-Instruct \
    --quantization awq \
    --tensor-parallel-size 4 \  # 4 GPU 张量并行
    --max-model-len 4096 \
    --gpu-memory-utilization 0.9

# 客户端（完全兼容 OpenAI SDK）
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")
response = client.chat.completions.create(
    model="meta-llama/Llama-3-8B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### 性能指标

```
vLLM 吞吐量（LLaMA-7B, A100 80GB）:
  单卡: ~3000 tokens/s（batch 并发时）
  4 卡: ~12000 tokens/s

延迟:
  单请求: ~30ms/token (decode)
  多并发: ~10ms/token (batch amortize)

vs HuggingFace Transformers:
  vLLM 快 24x（PagedAttention + continuous batching）
```

---

## 四、llama.cpp 部署详解

### 适用场景

```
✅ CPU 推理（无 GPU 的服务器/笔记本）
✅ 混合精度（CPU + GPU offload）
✅ 最小依赖（单二进制文件）
✅ 量化灵活（Q2_K ~ Q8_0）
✅ 适合个人/边缘部署
```

### 部署

```bash
# 1. 下载量化模型
wget https://huggingface.co/TheBloke/Llama-3-8B-GGUF/resolve/main/llama-3-8b.Q4_K_M.gguf

# 2. 启动 API 服务
./server -m llama-3-8b.Q4_K_M.gguf -c 4096 --port 8080

# 3. 客户端
curl http://localhost:8080/completion \
    -d '{"prompt": "Hello", "n_predict": 100}'
```

### 性能

```
LLaMA-7B Q4_K_M 在不同硬件:
  Apple M2 Pro:     ~25 tokens/s
  Intel i9-13900K:  ~15 tokens/s
  NVIDIA RTX 4090:  ~80 tokens/s (GPU offload)
  Raspberry Pi 5:   ~3 tokens/s
```

---

## 五、量化模型选择

```
模型格式选择:
  ┌── NVIDIA GPU → vLLM + AWQ/GPTQ INT4
  ├── AMD GPU → vLLM + GPTQ
  ├── Apple Silicon → llama.cpp + GGUF Q4_K_M
  ├── 纯 CPU → llama.cpp + GGUF Q4_K_S
  ├── 手机 → MLC-LLM / MNN
  └── 浏览器 → WebLLM / Transformers.js

量化精度选择:
  ┌── 显存够 → FP16（无量化）
  ├── 稍紧 → INT8（BitsAndBytes）
  ├── 很紧 → INT4（AWQ/GPTQ）
  └── 极限 → INT3（质量下降明显）
```

---

## 六、推理优化技术栈

```
                 ┌── PagedAttention (vLLM)
     KV Cache ───┤── Sliding Window (Mistral)
                 └── KV Quantization (INT8 Cache)

     Attention ─── Flash Attention 2/3
                  Sparse Attention
                  GQA/MQA

     Batching ──── Continuous Batching (vLLM)
                  In-flight Batching (TGI)

     Parallel ──── Tensor Parallel (Megatron)
                  Pipeline Parallel
                  Data Parallel (多副本)

     Compile ───── CUDA Graph (kernel 融合)
                  torch.compile (PyTorch 2.0)
                  TensorRT (NVIDIA 极致优化)

     Sampling ──── Speculative Decoding (EAGLE)
                  Medusa Heads
                  Chunked Prefill
```

---

## 七、生产部署架构

```
                    ┌─── Load Balancer (Nginx/HAProxy)
                    │         ↓
                    ├─── vLLM Server ×4 (GPU)
                    │         ↓
                    ├─── Redis (会话缓存)
                    │         ↓
                    ├─── PostgreSQL (日志/审计)
                    │         ↓
                    └─── Prometheus + Grafana (监控)

关键指标:
  • TTFT (Time to First Token): <500ms
  • TPOT (Time Per Output Token): <50ms
  • Throughput: >1000 tokens/s/GPU
  • Uptime: 99.9%

扩容:
  • 水平: 增加 vLLM 实例 + Load Balancer
  • 垂直: 增大 batch size + 更多 GPU
  • 模型: 量化 → 同 GPU 跑更大模型
```

---

## 八、成本估算

```
LLaMA-3-70B 部署成本:
  vLLM + 2×A100 80GB + AWQ INT4:
    GPU 月租: ~$3,800/月
    吞吐: ~5000 tokens/s
    每 1M tokens 成本: ~$0.03

  vs GPT-4 API:
    每 1M tokens: $10.00
    → 自部署便宜 300x（如果量够大）

盈亏平衡点:
  如果每月 >380M tokens → 自部署更划算
  如果每月 <380M tokens → API 更划算（省运维成本）
```

---

## 九、一句话总结

> GPU 部署用 vLLM（PagedAttention + Continuous Batching）。
> CPU/边缘部署用 llama.cpp（GGUF 量化）。
> 追求极致性能用 TensorRT-LLM。
>
> **vLLM 是当前开源推理引擎的事实标准——吞吐量比 HuggingFace 快 24x。**

---

*配套：[kv-cache-原理精读](kv-cache-原理-精读.md) | [model-compression精读](model-compression-精读.md) | [model-parallel精读](model-parallel-精读.md) | [tinyllm/serve.py](../projects/tinyllm/serve.py)*

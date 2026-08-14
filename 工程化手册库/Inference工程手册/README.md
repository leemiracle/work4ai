# Inference 工程手册

> **建立**：2026-08-13
> **是什么**：LLM 推理服务——从模型权重到生产 API。让训练好的模型能高效服务用户。
> **为什么重要**：训练一次 1 个月，推理每天亿次。**推理成本决定 AI 公司的生死**。

---

## 1. 是什么 + 为什么

**Inference = 把训练好的模型权重变成可调用的 API**。

核心挑战：
- **吞吐**（throughput）：每秒处理多少请求
- **延迟**（latency）：单请求多快（p50 / p99）
- **显存**（VRAM）：能装多大模型
- **成本**（cost）：$/1M token

**2026 关键数字**（vLLM v0.27 + A100 80GB + Llama 3.1 70B）：
- 吞吐：~3000 tokens/sec
- 延迟 p50：~100ms / token
- 显存：70B fp16 = 140GB（2 卡）/ int4 = 35GB（1 卡）
- 成本：~$0.5 / 1M token

---

## 2. 听说读写 4 能力

| 能力 | 含义 |
|------|------|
| **听** | 解析一个推理服务（serving engine / batch / cache / quant）|
| **说** | 用推理圈行话（PagedAttention / continuous batching / prefill-decode / KV cache）|
| **读** | 读推理论文（vLLM / Orca / FlashAttention / DistServe）|
| **写** | 部署一个生产推理服务 |

---

## 3. SEPAD 解析框架

```
S - Serving Engine（服务引擎）：vLLM / SGLang / TensorRT-LLM / llama.cpp
E - Execution Mode（执行模式）：batch / continuous batching / speculative decoding
P - Prefill-Decode（分离）：prefill（首 token 慢）vs decode（后续 token 快）
A - Attention（注意力）：FlashAttention 2/3/4 / PagedAttention / MLA
D - Deployment（部署）：单卡 / 多卡 / 多机 / 云原生
```

### S · Serving Engine
| 引擎 | 特点 | 适用 |
|------|------|------|
| **vLLM** v0.27 | 开源标准，PagedAttention，最快通用 | 通用首选 |
| **SGLang** | 结构化输出 + 缓存 | Agent / 函数调用 |
| **TensorRT-LLM** | NVIDIA 最优 | 纯 NVIDIA 追求极致 |
| **llama.cpp** | CPU/Mac | 端侧 / 本地 |
| **Ollama** | 易用 | 开发者本地 |
| **TGI**（HuggingFace）| 企业 | HuggingFace 生态 |
| **MLC-LLM** | 跨平台 | iOS/Android/Web |

### E · Execution Mode
- **Static batching**：等 batch 满 → 慢
- **Continuous batching**：请求随到随走 → vLLM 默认，**2-24x 提升**
- **Speculative decoding**：小模型猜 + 大模型验 → 2-3x 速度

### P · Prefill-Decode
- **Prefill**：处理整个 input prompt（计算密集，慢）
- **Decode**：逐 token 生成（显存密集，快）
- **分离部署**（DistServe 2024）：prefill 和 decode 在不同 GPU → 极致优化

### A · Attention
| 技术 | 速度提升 | 用途 |
|------|---------|------|
| **FlashAttention 2** | 2-3x | 2023 标准 |
| **FlashAttention 3** | 3-5x | H100 特化 |
| **FlashAttention 4** | 5-10x | Blackwell |
| **PagedAttention** | 内存省 5-10x | vLLM 核心 |
| **MLA**（DeepSeek）| KV 压缩 | DeepSeek V3/R 系列 |

### D · Deployment
- 单卡（24-80GB）：消费级 GPU，7B-70B（量化后）
- 多卡（2-8 卡）：TP（Tensor Parallel）
- 多机：PP（Pipeline Parallel）+ 网络
- 云原生：K8s + Triton / KServe

---

## 4. 6 维度评价

| 维度 | 指标 |
|------|------|
| **1. 吞吐** | tokens/sec / requests/sec |
| **2. 延迟** | TTFT（首 token 延迟）/ TPOT（每 token 延迟）|
| **3. 显存** | 峰值 VRAM / KV cache 占比 |
| **4. 精度** | vs 原模型输出一致（量化后）|
| **5. 成本** | $/1M token / GPU 小时费 |
| **6. 易用性** | 部署难度 / API 兼容性 |

### Benchmark 工具
- **vLLM benchmark**：`vllm serve --model X` + `benchmark_throughput.py`
- **LM Evaluation Harness**（EleutherAI）：下游任务
- **MLPerf**：行业标准

---

## 5. 工具栈（2026-08）

| 工具 | 版本 | 用途 |
|------|------|------|
| **vLLM** | v0.27.0（2026-08）| 开源推理标准 |
| **SGLang** | 持续更新 | 结构化输出 |
| **TensorRT-LLM** | NVIDIA | 极致 NVIDIA |
| **llama.cpp** | 持续更新 | CPU/Mac |
| **Ollama** | 持续更新 | 本地易用 |
| **TGI** | HuggingFace | 企业 |
| **OpenAI API** | 闭源 | 商业 API |
| **Anthropic API** | 闭源 | 商业 API |

---

## 6. 跨平台差异

| 平台 | 推荐引擎 | 特点 |
|------|---------|------|
| **NVIDIA H100/H200** | vLLM / TensorRT-LLM | 最快，FP8 支持 |
| **NVIDIA Blackwell** | TensorRT-LLM | FP4 支持 |
| **NVIDIA A100** | vLLM | 通用 |
| **AMD MI300** | vLLM ROCm | AMD 生态 |
| **Apple Silicon** | llama.cpp / MLX | Mac 优化 |
| **CPU** | llama.cpp | 慢但通用 |
| **云**（AWS/GCP/Azure）| vLLM | 弹性 |

---

## 7. 实战案例：用 vLLM 部署 7B 模型

### 基础部署

```bash
# 安装
pip install vllm

# 部署（一行命令）
vllm serve meta-llama/Llama-3.1-8B-Instruct \
    --port 8000 \
    --tensor-parallel-size 1 \  # 单卡
    --gpu-memory-utilization 0.9 \
    --max-model-len 8192

# 测试
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "prompt": "Hello, my name is",
        "max_tokens": 30
    }'
```

### 高级：量化 + continuous batching

```bash
# AWQ 量化模型
vllm serve TheBloke/Llama-3.1-70B-AWQ \
    --quantization awq \
    --tensor-parallel-size 2 \  # 2 卡
    --max-model-len 32768 \
    --enable-prefix-caching  # 缓存公共前缀
```

### Benchmark

```bash
# 吞吐测试
vllm bench serve \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --base-url http://localhost:8000

# 输出：
# Throughput: 2847.3 tokens/sec
# TTFT p50: 45ms
# TPOT p50: 12ms
```

---

## 8. 反模式 10 条

1. **不用 continuous batching**（静态 batch → 吞吐低 10x）
2. **FP16 部署 70B**（用 int4 / AWQ 省 70% 显存）
3. **不测延迟分布**（只看平均 → p99 可能爆）
4. **KV cache 无上限**（长 context OOM）
5. **不监控显存碎片**（PagedAttention 解决但需配置）
6. **单卡跑超大模型**（用 TP / PP 分卡）
7. **不缓存 prefix**（相同 system prompt 重复算 → 浪费）
8. **直接部署训练 checkpoint**（应该先 optimize + 量化）
9. **忽视 prefill 延迟**（首 token 慢 → 用户体验差）
10. **不跑下游任务**（量化可能掉点 → 必须验证准确率）

---

## 9. 下一步

- 读 vLLM 论文（arXiv 2309.06180，PagedAttention）
- 读 Orca 论文（continuous batching）
- 装 vLLM，部署 Llama 3.1 8B
- 用 `vllm bench` 跑 benchmark
- 试 AWQ 量化 + 对比 fp16

---

**版本**：v1.0（2026-08-13）
**核心理念**：**训练花 1 月，推理跑亿次。推理工程 = AI 公司的护城河。**

# tinyllm — LLM 系统（参照 nanoGPT + vLLM + tiktoken）

> 从零实现完整的 LLM 技术栈：模型架构 → 分词器 → 推理引擎 → API 服务。

## 模块清单

| 文件 | 参照 | 核心内容 |
|------|------|---------|
| `model.py` | nanoGPT / Attention Is All You Need | GPT 完整架构（MHA + FFN + Pre-LN + Weight Tying） |
| `tokenizer.py` | tiktoken / HuggingFace | BPE 训练 + 编码 + 解码 + 序列化 |
| `infer.py` | vLLM / TGI | KV Cache + Prefill/Decode + Greedy/Top-K/Top-P 采样 |
| `serve.py` | vLLM OpenAI Server | `/v1/chat/completions` 兼容 API |
| `demo.py` | — | 端到端：Tokenizer → Model → Inference → Stats |

## 端到端演示

```bash
python3 projects/tinyllm/demo.py
```

## API 服务

```bash
python3 projects/tinyllm/serve.py
# 然后：curl http://localhost:8000/v1/chat/completions \
#   -H 'Content-Type: application/json' \
#   -d '{"messages":[{"role":"user","content":"hello"}]}'
```

## csdiy 知识交叉

- [nanoGPT 读懂最小 GPT](../../source-reading/nanoGPT-读懂最小GPT.md) — model.py 的逐行参照
- [redis-eventloop](../../source-reading/redis-eventloop-逐行拆解.md) — serve.py 的事件循环基础
- [bloom-filter](../../source-reading/bloom-filter-精读.md) — 推理时的 SSTable 过滤
- [consistent-hashing](../../source-reading/consistent-hashing-精读.md) — 分布式推理的负载均衡

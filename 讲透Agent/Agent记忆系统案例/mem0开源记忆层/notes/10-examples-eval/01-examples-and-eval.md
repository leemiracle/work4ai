# 01 — Examples 与 Evaluation Benchmark

> `examples/` 是可跑的示例项目（10 个）,`evaluation/` 是 benchmark 子模块（git submodule 到 mem0ai/memory-benchmarks）。

---

## 1. examples/ 全清单

```
examples/
├── graph-db-demo/             # ⚠️ graph DB demo（v1.0 时代,可能过时）
├── mem0-demo/                 # 基础 demo
├── misc/                      # 杂项
├── multiagents/               # 多 agent 场景
├── multimodal-demo/           # 多模态（vision）
├── nemoclaw/                  # Nemoclaw 集成
├── notebooks/                 # Jupyter notebooks
│   ├── customer-support-chatbot.ipynb
│   ├── mem0-autogen.ipynb     # AutoGen 集成
│   └── helper/
├── openai-inbuilt-tools/      # OpenAI 内置工具集成
├── vercel-ai-sdk-chat-app/    # Vercel AI SDK 完整 chat app
└── yt-assistant-chrome/       # YouTube assistant Chrome 扩展
```

---

## 2. 选读示例

### `notebooks/customer-support-chatbot.ipynb`

客服 chatbot 完整 demo:
- 用 Mem0 存用户偏好
- search 注入 system prompt
- 多轮对话

### `notebooks/mem0-autogen.ipynb`

Microsoft AutoGen 多 agent + Mem0 集成。

### `vercel-ai-sdk-chat-app/`

完整 Next.js + Vercel AI SDK + Mem0 应用,生产参考。

### `yt-assistant-chrome/`

Chrome 扩展,看 YouTube 时实时存 video 内容到 Mem0。

### `multimodal-demo/`

vision LLM + Mem0（图片描述变 memory）。

### `multiagents/`

多 agent 共享 memory 场景（不同 agent_id 共用 user_id 等）。

---

## 3. ⚠️ graph-db-demo（过时）

> April 2026 重构移除了 graph memory（详见 [`../02-py-sdk-providers/05-graphs.md`](../02-py-sdk-providers/05-graphs.md)）。
>
> `examples/graph-db-demo/` 可能仍存在但**不再维护**。看代码注意:Neo4j 等已不在主 SDK。

---

## 4. evaluation/ 子模块

`evaluation/` 是 git submodule,指向 [`mem0ai/memory-benchmarks`](https://github.com/mem0ai/memory-benchmarks)。

### 初始化

```bash
git submodule update --init evaluation
# 或
git clone --recurse-submodules https://github.com/mem0ai/mem0.git

# 或独立 clone
git clone https://github.com/mem0ai/memory-benchmarks.git
cd memory-benchmarks
pip install -r requirements.txt
```

---

## 5. ⭐ 3 个 Benchmark

### LoCoMo（Long Conversation Memory）

长对话记忆评测。

```bash
python -m benchmarks.locomo.run \
  --project-name my-test \
  --backend cloud \
  --mem0-api-key $MEM0_API_KEY
```

Mem0 Platform 当前得分：**92.5**（+21 over old algorithm）

### LongMemEval

长记忆评测。

```bash
python -m benchmarks.longmemeval.run \
  --project-name my-test \
  --backend cloud \
  --mem0-api-key $MEM0_API_KEY \
  --all-questions
```

Mem0 Platform：**94.4**（+27,with 98.2 on assistant memory recall）

### BEAM（生产规模）

100K 和 10M token 规模评测。

```bash
python -m benchmarks.beam.run \
  --project-name my-test \
  --backend cloud \
  --mem0-api-key $MEM0_API_KEY \
  --chat-sizes 100K \
  --conversations 0-9
```

| Size | Score | Tokens | Latency p50 |
|------|-------|--------|------------|
| BEAM 1M | **64.1** | 6.7K | 1.00s |
| BEAM 10M | **48.6** | 6.9K | 1.05s |

---

## 6. Benchmark 后端

```bash
--backend cloud    # Mem0 Platform（推荐,最新算法）
--backend docker   # 自托管 docker compose
```

> OSS 用 docker backend,Platform 用 cloud backend。两者数字会差（Platform 永远高）。

---

## 7. 自定义 Benchmark

`memory-benchmarks` 仓库支持扩展：

- 加新评测数据集（`benchmarks/<name>/data/`）
- 实现 `run.py` 接口
- 加 scoring logic

详见 https://github.com/mem0ai/memory-benchmarks。

---

## 8. README benchmark 表（2026-04）

| Benchmark | Old | New | Tokens | Latency p50 |
|-----------|-----|-----|--------|-------------|
| LoCoMo | 71.4 | **92.5** | 7.0K | 0.88s |
| LongMemEval | 67.8 | **94.4** | 6.8K | 1.09s |
| BEAM 1M | — | **64.1** | 6.7K | 1.00s |
| BEAM 10M | — | **48.6** | 6.9K | 1.05s |

> 数字解读：
> - "+21" / "+27" 主要是 single-pass ADD-only + entity linking + BM25 融合带来的
> - "Tokens 6-7K" 是 search 时的 token budget（融合后只取 top_k）
> - "Latency 1s" 是 p50,包含 LLM + embed + vector search + entity boost

---

## 9. 跑 Benchmark 的注意

1. **API 配额**：1M token 的 BEAM 会消耗大量 API 调用,确认 quota
2. **时间**：完整 BEAM 10M 可能几小时
3. **成本**：cloud backend 走 Platform 计费,docker 走你自己的 OpenAI 等账单
4. **数据集**：部分数据集要单独下载（看 memory-benchmarks README）

---

## 10. 接下来

| 想看 | 去哪 |
|------|------|
| 完整 benchmark 仓库 | https://github.com/mem0ai/memory-benchmarks |
| 添加新示例 | `examples/` 直接加,PR welcome |
| Algorithm 详情 | [`../01-py-sdk-core/06-add-pipeline.md`](../01-py-sdk-core/06-add-pipeline.md) |

---

📌 **下一步** → [`../99-appendix/`](../99-appendix/) 术语表 + 数据流汇总。

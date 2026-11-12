# 讲透 cactus-compute/needle

> A 层清库 #13（小仓全链一体 6 批）· 2026-11-02

| 链路 | 状态 |
|---|---|
| 图谱 | 仓内 knowledge-graph.json：115n/184e/6层/8步，0 issues，fingerprints 38@7bd8a635 |
| 综合讲透 | `讲透.md`：4000 字 59 锚 |
| NOTES-DIGEST | 18 条 |

**一句话**：Needle 2=**45M 参数端侧工具调用模型**的 Python 包——三平面架构（零 JAX 契约层/惰性 JAX 训练层/.cact 部署枢纽）；SAN 架构（Engram 哈希记忆+MHC 超连接）。

**甄别亮点**：引擎版本 2.0.3 与包版本 2.0.8 独立演进；Python 端 KV sink 钩子 `_doc_prefix_len` 恒返回 0（真 sink 在 C++ 引擎内）；confidence 头不在微调范围（tuned 权重下恒 None）。

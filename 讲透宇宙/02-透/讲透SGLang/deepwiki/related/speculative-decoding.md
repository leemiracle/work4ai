# sgl-project/speculative-decoding（DeepWiki 无独立 wiki）

> 探测日期：2026-09-03。DeepWiki 对该仓仅有壳页面（~31KB，无正文容器），未生成 wiki 内容。

**该仓背景**：EAGLE 投机解码论文（*EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty*, ICML 2024 Oral）的官方实现仓，是 SGLang EAGLE 实现的上游参考。

**主仓替代资料**：

- [12-speculative-decoding](../12-speculative-decoding.md) —— SGLang 投机解码总览
- [12.1-eagle-algorithm-and-architecture](../12.1-eagle-algorithm-and-architecture.md) —— EAGLE 算法与架构
- [12.2-draft-and-verification-flow](../12.2-draft-and-verification-flow.md) —— draft/verify 流程
- [12.3-integration-with-scheduling](../12.3-integration-with-scheduling.md) —— 与调度器的集成

**源码深度解析**：`../../explain/sglang-srt-speculative-eagle_worker.md`（EAGLEWorker 逐方法解析：draft 建树 → target 树验证 → accept 结算 → KV 回滚的完整状态机）。

# sgl-project/sgl-router（DeepWiki 无独立 wiki）

> 探测日期：2026-09-03。DeepWiki 对该仓仅有壳页面（~31KB，无正文容器），未生成 wiki 内容。

**现状**：sgl-router 的功能已并入 sglang 主仓库，DeepWiki 主 wiki 以两章覆盖：

- [20-sglang-router-(sgl-router)](../20-sglang-router-(sgl-router).md) —— 总览
- [20.1-experimental-sgl-router:-slim-kv-aware-router](../20.1-experimental-sgl-router:-slim-kv-aware-router.md) —— 实验性 slim KV-aware router
- [20.2-router-grpc-pipeline-and-tool-parsing](../20.2-router-grpc-pipeline-and-tool-parsing.md) —— gRPC pipeline 与 tool 解析

**代码位置（commit ec075d8bc）**：rust workspace 已拆分，路由/网关逻辑位于仓根 `sgl-model-gateway/` crate（cache-aware 路由见 `sgl-model-gateway/src/policies/cache_aware.rs`，worker 管理见 `src/core/worker_manager.rs`）。

深度解析见 `../../explain/sglang-rust-cache_aware.md` 与 `../../explain/sglang-rust-worker_manager.md`。

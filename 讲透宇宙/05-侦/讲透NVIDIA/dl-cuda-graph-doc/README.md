# 讲透 dl-cuda-graph-doc（NVIDIA CUDA Graph Best Practice for PyTorch）

NVIDIA 官方 CUDA Graph 最佳实践文档站源仓——纯文档项目（26 md/12691 行 + Sphinx 构建链，无产品代码），在线版 https://docs.nvidia.com/dl-cuda-graph/ （README.md:7）。

## 全链状态表

| 阶段 | 产物 | 状态 |
|------|------|------|
| 图谱 | 仓内 `.understand-anything/knowledge-graph.json`（37 节点/77 边/2 层/6 步，fingerprints 37@fd32a8f6） | ✅ |
| 甄别笔记 | 仓内 `.understand-anything/NOTES-DIGEST.md`（3 条） | ✅ |
| 上手指南 | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（8 节 30+ 锚，README+ONBOARDING 合并口径） | ✅ |

> 仓：`/usr-data/data2/repos/agent-repos/NVIDIA/dl-cuda-graph-doc`（commit fd32a8f6，2026-10-19）。

## 十分钟速览（详细版见 onboarding/ONBOARDING.md）

- **入口** docs/index.md:22-54 三路径路由：系统学习五步 / 按症状速查七条 / 框架专属直达（Megatron·TE vs PyTorch）。
- **基础** docs/cuda-graph-basics/constraints.md 是全站"宪法"——**9 节编号约束**（异步/静态拓扑/静态参数/自包含捕获/CPU 不入图/多线程/内存/多设备/其他），后续一切问题回溯于此。
- **集成** torch-integration.md:43-48 三层 API（torch.cuda.graph / make_graphed_callables / torch.compile CUDAGraph Trees）；autocast 缓存清空陷阱与 `cache_enabled=False` 解法（:240-289）。
- **五案例**（docs/examples/introduction.md:63-80 八维对比表）：GPT-3 逐层+FP8 amax 持久缓冲化（gpt-3-175b.md:299-310）· Llama 3.1 整迭代 FullCudaGraphWrapper（llama-31-405b.md:72-128）· Llama 2 LoRA 逐层 CudaGraphManager 自动捕获（llama2-70b-lora.md:65-70）· RNN-T 自定义 graph() 图化贪心解码循环+分桶（rnnt.md:72-74）· SD2 monkey-patch optimizer_step 捕整迭代（stable-diffusion-v2.md:136-149）。
- **排查** 五类失效模式专题：numerical-errors.md（1773 行全站最长，静默失败=捕获期冻结动态行为）· capture-failures.md（1289 行，同步/内存/流三类）· memory/process-hang/performance 各专一题。
- **构建** `./scripts/sphinx-serve.sh` 一键热重载（sphinx-serve.sh:11-23，uv 自动安装+sync+autobuild）；MyST+Sphinx，mermaid 代码块构建时真渲染（conf.py:40）；双许可：文档 CC-BY-4.0 / 代码 MIT（README.md:42-43）。

## 勘误与钉版（相对知识图谱摘要）

1. **"七类约束"计数失准**：图谱节点摘要称 constraints.md 为"七类约束权威清单"，实际该页是 **9 节编号**（constraints.md:15/43/68/100/162/170/196/258/294）。第三方转述再传"七条"均以此为准纠偏。
2. **SD2"全站最长单篇"不实**：图谱摘要称 stable-diffusion-v2.md 为"全站最长单篇"（1100 行），实际 numerical-errors.md 1773 行 > capture-failures.md 1289 > memory-issues.md 1204 > SD2 1100——SD2 只是 examples 章最长。
3. **CudaGraphManager 归属站内矛盾**：examples/introduction.md 对比表 Capture Mechanism 行把 Llama 2 的机制标为 "**TE** `CudaGraphManager`"，而专页 llama2-70b-lora.md:10/:59 与 te-megatron-cuda-graphs.md:23 均明确它是 **Megatron-Core** 的组件（megatron/core/transformer/cuda_graphs.py，enabled by `MCORE_CUDA_GRAPH=1`，llama2-70b-lora.md:153）。专页为准。
4. **conf.py 版权年份 2025**（conf.py:14）与全部源文件 SPDX 头 2026 不一致——元数据未随发版更新。
5. **图谱 .gitkeep 节点摘要错位**：docs/assets/.gitkeep（119B 纯注释占位）被摘要成"保存 lora-arch.png 与 pp-execution.png 两张章节插图"——两图是同目录并列文件，非 gitkeep 内容。

## 阅读组合建议

- 只要一个入口：index.md 速查路由 + 对应 troubleshooting 专题。
- 做训练框架选型：te-megatron-cuda-graphs.md 三机制总览 → 按模型形态挑案例（逐层 PP 选 GPT-3/Llama2、整迭代选 Llama3.1/SD2、变长/循环选 RNN-T）。
- 改代码前必读：sync-free-code.md 隐式同步清单 + handling-dynamic-patterns.md 官方实现级改写。
- 本机相关技能：perf-torch-cuda-graphs / perf-torch-sync-free（与本站 torch-cuda-graph 章 methodology 同源互补）。

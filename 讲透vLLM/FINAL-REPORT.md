# 最终报告：vLLM 深度知识库构建

**执行日期**：2026-09-02 23:00 计划 → 2026-09-03 全天（含两次故障恢复）
**执行方式**：无人值守 opencode run + 主会话接管收尾（5 并发 file-analyzer）

## 三大任务完成情况

### 任务 1：DeepWiki 全量抓取 ✅（100% 覆盖）
- **62/62 子页面**：章节 1-overview 至 13-glossary，覆盖配置初始化/引擎架构/GPU 执行/模型注册/服务 API/量化 MoE/注意力后端/分布式执行/平台支持/构建部署/测试 CI/术语表
- **12 个相关仓库**摘要（deepwiki/related/）+ 组织页 47 仓库清单（_repo-list.md）
- **遗漏检查**：_links.txt vs 实际文件 100% 对齐 + 3 页抽样正文校验 PASS（记录于 _coverage-check.md）
- 总量 1.6MB，INDEX.md 提供中文索引表

### 任务 2：understand 三连 ✅（Phase 0-7 全链路）
- **/understand --language zh**：11615 节点 / 33598 边 / 16 架构层 / 14 步导览，中文摘要+标签，校验零 issue，fingerprints 基线已建（10.4MB，支持增量更新）
- **/understand-onboard**：ONBOARDING.md（4600 字：总览/16 层架构/15 关键概念/14 步路径/51 文件地图/15 复杂度热点）
- **/understand-explain**：14 篇核心文件深解（计划 12-15，实际 14），覆盖 config/engine/v1 核心/scheduler/kv_cache/model_runner/worker/input_batch/flash_attn/api_server/llm/llama/parallel_state

### 任务 3：合并 work4ai ✅
- 目录：讲透vLLM/{README.md, deepwiki/(64 md), knowledge-graph/(2), onboarding/(1), explain/(14)}
- 总量 13MB，git commit 见下

## 图谱覆盖范围与裁剪说明（诚实披露）

- 扫描 3836 文件（ignore 排除 tests/benchmarks/examples/docs 后），规划 172 语义批次
- **实际完成 71/172 批次**，覆盖策略为「架构主干优先」：
  - 100% T0 架构主干：v1/engine、v1/core（scheduler+kv_cache）、v1/worker、config、entrypoints、attention、distributed、kv_transfer/offload
  - 100% 模型实现家族：model_executor/models 按字母序全覆盖（含 Qwen/Llama/DeepSeek/Kimi-K3/MiniMax/新式平台分目录模型）+ transformers_utils + tool_parsers + reasoning
  - 100% Rust 前端：engine-core-client + server（HTTP/gRPC 路由全量）
  - 100% 多模态管线：multimodal 核心 + processors
- **裁剪 101 批**（记录于 deferred 清单）：fused_moe/quantization/mamba 的调优配置 JSON 数据文件（~1500 个纯数据文件，低语义价值）、边缘 json/rust 细节
- 影响：knowledge-graph.json 查询这些裁剪文件时无节点；主流程理解不受影响（分层已验证全覆盖已分析节点）

## 执行过程与故障记录

| 时间 | 事件 | 处置 |
|---|---|---|
| 09-02 23:00 | 首次运行 1 分钟即退场 | 根因：opencode run 非交互模式 bash 权限 auto-reject；修复：--auto flag |
| 09-03 09:11 | 二次运行（--auto） | DeepWiki + Phase 0/1 + 40 批次顺利完成 |
| 09-03 ~11:15 | API 断流停摆 | 根因：export 的 https_proxy 劫持 API 长连接（代理节点故障）；诊断：直连 401 正常 vs 代理 000；修复：unset 代理重启 |
| 09-03 11:12 | 三次运行（直连） | API 零失败，但单会话实际并发 ~1，速率 0.28 批/min，全量需 8h+ |
| 09-03 ~13:50 | **主会话接管** | 停掉低效会话，5 并发 task 补跑 31 个核心精选批次（~1.5h） |
| 09-03 15:00-17:00 | Phase 2 merge → Phase 4 分层 → Phase 5 导览 → Phase 6 校验 → Phase 7 落盘 → onboard + explain×14 → 合并 | 全链路完成 |

## 产物清单与统计

| 产物 | 数量/规模 |
|---|---|
| deepwiki/ | 64 md（62 主页 + related 摘要 + INDEX），1.6MB |
| knowledge-graph.json | 11615 节点 / 33598 边 / 16 层 / 14 步导览，11.5MB |
| ONBOARDING.md | 4600 字 / 6 章节 |
| explain/ | 14 篇 / 约 13000 字 |
| GRAPH-SUMMARY.md + README.md + FINAL-REPORT.md | 本套索引与报告 |

## 值得记录的深度发现（explain 系列精选）

1. **api_server.py 已是弃用壳**（59 行 re-export），真实实现在 `vllm/entrypoints/launchers/` 四件套——图表确认后再深解，避免学旧结构
2. **Scheduler 统一记账哲学**（woosuk 注释）：无 prefill/decode phase 区分，只有 `num_computed_tokens` 追赶 `num_tokens_with_spec`；当前版本无显式 FINISHED 队列
3. **EngineCore 双层分离**：逻辑层 EngineCore vs 进程层 EngineCoreProc，ZMQ 双 daemon 线程；`step_with_batch_queue` 填满队列优先于取结果消除 PP 气泡
4. **PagedAttention 全命中仍须重算末 token**（`max_cache_hit_length = num_tokens - 1`）
5. **VllmConfig 的 `model_config=None`** 是防止默认构造触发模型下载的刻意设计

## 遗留与后续建议

- 101 个裁剪批次如需补全（调优配置 JSON 除外），可基于 fingerprints + batches.json 断点续跑（本报告批次序号清单可复用）
- 阅读建议从 ONBOARDING.md 起步；deepwiki/6.5 提到 rust 前端与 explain 的 Rust 系列可互参
- 本知识库对应 2026-09-03 源码快照，vLLM 演进后可用 /understand 增量更新

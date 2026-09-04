# 讲透SGLang 构建终报（FINAL-REPORT）

> 构建日期：2026-09-03/04 | 流水线：DeepWiki 全量抓取 → /understand --language zh → /understand-onboard → /understand-explain → 汇编入库

## 交付物清单

| 交付物 | 规模 | 质量关卡 |
|--------|------|---------|
| deepwiki/ 110 页 | 2.0 MB，24 主章节 + 86 子页 | 目录树正则提取防漏 + 反向核对 missing=0/small=0 |
| deepwiki/related/ 8 仓 | flashinfer/nixl/xgrammar/vllm/TRT-LLM/TGI + 2 占位 | 2 个无 wiki 仓如实标注，不编造 |
| knowledge-graph/ | 5652 节点 / 12950 边 / 27 层 / 12 步 / 6.0 MB | 0 悬挂边 / 0 层重复 / 0 导览断链 / 中文 100% |
| onboarding/ONBOARDING.md | ~4600 字 | 27 层归并 6 大板块 + mermaid×2 + 14 天路径 |
| explain/ 18 篇 | 7590 行（平均 422 行/篇） | 行号实测核对 + 3 处过时认知修正 |
| 索引与校验 | INDEX.md（114 链接 0 断链）/_coverage-check/_repo-list | 自动链接校验通过 |

## 方法论（可复刻到下一个大仓）

1. **DeepWiki 全量抓取**：从主页 SSR HTML 正则提取全部 `/sgl-project/sglang/…` 链接去重（110 个，比手工抄目录可靠）→ `requests`+代理 4 并发抓取 → bs4 提取 `div.prose-custom` → 自写 HTML→MD 转换器（标题/表格/代码块/链接全保留，源码行号引用不丢）→ 断点续传（>2KB 跳过）+ 3 次退避重试 + 反向核对。
2. **知识图谱复用**：sglang 仓已有同 commit 中文图谱（meta.gitCommitHash == HEAD），走"校验而非重建"路径：自写校验脚本查悬挂边/层重复/tour 断链/中文率，全过则直接复用——节省了 vLLM 那次 8h+ 的图谱重建。
3. **explain 5 并行 task**：主会话拆 18 文件为 3 批（5+5+5+2+2 after retry），每 task 给模板（标题/行号引用/交互 grep 实证/设计决策/阅读建议）+ 输出路径，task 间互不阻塞。1 个 task 因账户限流失败，原 prompt 重试成功。
4. **零遗漏三道闸**：链接反向核对 → INDEX 链接自动校验（抓出并修正 2 处笔误）→ coverage-check 报告落盘。

## 版本考据修正（explain 阶段产出，全仓 grep 实证）

| 旧认知 | 实况（ec075d8bc） |
|--------|------------------|
| Rust 路由在 `rust/sgl-router/` | rust workspace 已拆分，实际在仓根 `sgl-model-gateway/` crate |
| 模型在 `srt/model_executor/models/` | 已迁至 `srt/models/`（193 个模型文件） |
| 模型有 forward_native/forward_cuda_graph 双入口 | 已演进为单一 `forward` + 两级分派（ModelRunner 层 graph-vs-eager；backend 层 extend-vs-decode） |
| TokenToKVPoolAllocator 在 memory_pool.py | 已拆至 `allocator.py` |
| Noisy Router（推理侧噪声注入） | 不存在（纯训练期技术）；本版本对应物是 shared 槽 randint / SGLANG_SIMULATE_UNIFORM_EXPERTS / EPLB random dispatch |

## 本轮新坑（钉版）

1. **deepwiki 代理间歇限流**：4 并发抓 ~60 页后 SSL EOF/reset 雪崩。对策=断点续传 + 降并发重跑（3 轮补齐），勿在一轮里硬刚。
2. **DeepWiki 无 wiki 壳页面**：HTTP 200 不代表有内容——`sgl-project/sgl-router` 等仓仅 31KB 壳、无 `div.prose-custom`。探测必须查容器而非状态码。
3. **snip 前缀渗入 heredoc**：python heredoc 连续两次把 `snip` 写进代码导致 SyntaxError。根治=复杂逻辑一律落 `.py` 脚本文件再执行（本流水线全部脚本化）。
4. **shell for 循环不能加 snip 前缀**（keyword construct 拒绝）→ 循环体写 `.sh` 文件执行。

## 与讲透vLLM 的复用关系

- 同一流水线第二代执行；图谱阶段从"全量重建 8h"优化为"同 commit 校验复用 5min"。
- `deepwiki/related/vllm.md` 为概要页，深度资料互链 `../讲透vLLM/`（62 页 + 12 related + 14 explain）。

## 维护建议

- SGLang 主仓大幅演进后：重跑 `/understand`（增量）、重跑 `/tmp/opencode/dw_fetch.py`（脚本与 URL 清单逻辑可从 `deepwiki/_links.txt` 恢复）、explain 篇按需更新行号。
- 知识图谱 json 可直接喂 `.understand-anything/` + `/understand-dashboard` 或做 RAG 语料。

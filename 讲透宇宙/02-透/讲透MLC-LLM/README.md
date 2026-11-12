# 讲透 MLC-LLM

MLC-LLM 深度知识库：基于 Apache TVM 的通用 LLM 部署引擎（编译器视角的 llama.cpp）。

> 源仓：`~/ai/mlc-llm` · 图谱 commit `9fa644f` · 1950 节点 / 4011 边 / 14 架构层 / 15 步导览 · 2026-09-05

## 目录

| 目录 | 内容 |
|---|---|
| `deepwiki/` | DeepWiki 全站抓取 28 页（含 INDEX.md + 覆盖率检查） |
| `onboarding/` | 新人上手指南（ONBOARDING.md，8 节，5996 字） |
| `explain/` | 5 篇核心文件精讲（六节结构，各 1500-2500 字） |

## explain 索引

| 文件 | 主题 | 锚点文件 |
|---|---|---|
| `explain/mlcllm-model-registry.md` | 模型注册中心：Model 四要素 + 47 条目矩阵 | `python/mlc_llm/model/model.py`（750 行） |
| `explain/mlcllm-compiler-pass.md` | 编译流水线：5 Phase 编排约 40 pass | `python/mlc_llm/compiler_pass/pipeline.py`（209 行） |
| `explain/mlcllm-llama-model.md` | 参考架构 + EAGLE draft 基座 | `python/mlc_llm/model/llama/llama_model.py`（542 行） |
| `explain/mlcllm-serve-engine.md` | Python 异步引擎 + 前缀缓存壳 | `serve/engine.py`+`engine_base.py`+`radix_tree.py` |
| `explain/mlcllm-cpp-engine.md` | C++ 引擎核心与线程化外壳 | `cpp/serve/engine.cc`+`threaded_engine.cc` |

## 阅读路径

1. `onboarding/ONBOARDING.md` 建立全局心智模型（15 步学习路径）
2. 按兴趣挑 `explain/` 精讲（每篇独立可读，含设计决策与新人提示）
3. 需要细节再查 `deepwiki/` 对应章节

## 已知勘误（相对早期任务描述）

- `serve/engine/async_engine.py` 不存在——实际为 `serve/engine.py`（1946 行）+ `serve/engine_base.py`（1278 行）
- radix tree Python 壳在 `serve/radix_tree.py`（154 行 FFI），算法本体在 `cpp/serve/radix_tree.cc`（845 行）

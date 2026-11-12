# 讲透 GenerativeAIExamples

> NVIDIA GenerativeAIExamples——RAG/Agent/OWD 示例全家（NIM 微服务化）：RAG 主线+部署矩阵+行业示例（能源/医疗/电信 5G/数字人）+社区群+NeMo SDG。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| understand 图谱 | ✅ 2026-11-07 | 仓内 `.understand-anything/knowledge-graph.json`：**2660n/3328e/15 层/15 步 tour**，fingerprints 1328@203b0de4 |
| onboarding | ✅ 2026-11-07 | `onboarding/ONBOARDING.md`（8 节 13135 字不计空格） |
| explain 12 篇 | ✅ 2026-11-07 | `explain/01-12` 合计 **70834 字符**，抽验 69 锚 0 坏 |

## 战况（151 批）

四 worker 大段滚动（1-38/39-76/77-114/115-151），75 分钟全清（158 件终验 2647 ID 唯一/1328 文件全覆盖零缺失）。merge 15 悬空=8 抽象基类+7 compose/依赖节点手术补建回补；补建节点经 3 轮补层后 finalize 过验。

## 甄别精选（源码级实证）

1. **根 .pre-commit 的 insert-license 钩子是 dead hook**（指向 0.8.0 重构前 RetrievalAugmentedGeneration/ 旧路径已失配；black/isort 有效）
2. **68/77 个 js/ts 是 `_next/static/chunks` 构建产物**（minified bundle 已标 build-artifact；真前端源码仅 ai-vws-sizing-advisor 9 个）
3. **medical-device-training-assistant=RAG 模板五件套同源副本**（base/configuration/server/utils/tracing）；nvidia_embedding.py 同源双副本（docstring 逐字相同实证）
4. **agent 示例实际分布于 community/+industries/**（顶层 agent/ 目录在当前版本不存在——磁盘实证）
5. 社区子项目互相独立、依赖全为外部包（ast 全量复扫仅 20 条真实项目内 imports）
6. healthcare rag_playground 仅 speech 单模式；default/speech 静态 html 字节级相同（Next.js 壳）；structured_data_rag prompt.yaml 顶层 prompts: 键包裹异于其他平铺
7. energy compose-full 的 Milvus 栈 etcd/minio/standalone 手术补建；Morpheus Dockerfile 的 entrypoint.sh 由上游构建上下文提供（不在本仓）

## 分层速览（15 层，1478 文件节点）

根文档构建 → RAG 主线(91) → 部署矩阵(74) → 评测观测(60) → 能源模拟(184) → 医疗资产(118) → VWS 容量顾问(163) → 数字人流式(183) → 电信 5G(100) → RAG 进阶社区群(178) → 社区百宝箱(165) → NeMo SDG(102) → 微调模型(25) → OSS 教程(10) → 文档站(21)

*2026-11-07 · cuda-stack-第七轮会话（舰队认领）*

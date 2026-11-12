# xinference understand 图谱 · 全链产物

> xorbits/inference(Xinference) @b3de260（2026-09-03 快照）· 产物 2026-11-09 · 真源本目录

## 状态

| 产物 | 规模 | 状态 |
|---|---|---|
| knowledge-graph.json | 2785 节点 / 5826 边 / 14 层 / 16 步 tour | ✅ validator 双验 0 issues 0 warnings |
| fingerprints 基线 | 609 文件 @b3de260 | ✅ 支持增量 |
| ONBOARDING.md | 5071 字 8 节 17 锚 | ✅ 抽验 100% 命中 |
| explain/ | 12 篇 41797 字符 | ✅ 锚三型判读终验真坏 0 |

## 裁剪口径（.understandignore 钉版）

thirdparty/（812 vendored 厂商 SDK）+ tests + benchmark/doc/frontend/assets 全裁 → 609 文件入图。

## 批分析实录（45 批 / 609 文件）

- 手扫补 imports/depends_on 合计 ~600 条（Python 仓三大盲区：函数体 lazy import、TYPE_CHECKING 块、`from types import` stdlib 误映射 xinference/types.py 的**假边**——多个批次独立甄别剔除 20+ 条）
- 重大甄别：SupervisorActor/WorkerActor 真身在 xinference/core/（deploy/ 仅入口壳，任务书路径被工人纠正）；stable_diffusion/core.py:415 存在**断裂导入**（FluxBatchScheduler 全仓无定义，开 batching 环境变量即 ImportError）；deepseek_v3.py:64 rank0 分支调 _set_result 全仓无定义（潜在 AttributeError）；get_launcher 无点号分支是死代码；Grafana 7 面板×4 语言变体=同 uid 互斥导入；旧轮（2026-09-21）嵌套图谱产物被本轮扫描自污染 5 节点（已标 pipeline-artifact，DeepChat 自指坑复现）
- 锚验收钉版（第二次实证 DataFlow 三型判读法）：初报 32.8% 坏 → 短路径自动展开 84/84 + 主题归位 55/60 + 内容抽验 4/4 → **真坏 0**；5 个"越界"系验证器误归位（文中全路径首引+简写复用是合规写作风格）

## 14 层速览

根配置 CI(24) → 包入口/SDK(16) → REST API/OAuth2(39) → core 控制面(31) → 模型抽象注册(60) → LLM 引擎矩阵(66) → Embedding/Rerank(15) → 图像/视频/世界(29) → 音频/Flexible(29) → 批调度/Xavier KV(17) → Token Router(44) → Docker 部署(35) → Monitor(57) → 测试/产物(163)

## 使用

- 新人：ONBOARDING.md → tour 16 步 → explain/ 12 篇（supervisor 7120 行 actor→worker→八模态分发→六引擎→scheduler→token router→metrics 全链）
- agent：knowledge-graph.json + 讲透Inference（work4ai）
- 增量：代码变更后重跑 prepare（fingerprints 跳过未变）

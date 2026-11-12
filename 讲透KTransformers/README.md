# 讲透 KTransformers · MoE 大模型 CPU+GPU 异构单机推理框架全量知识库

> **kvcache-ai/ktransformers** @ commit `31985f4`（2026-09-01）· 收官补齐 2026-09-20
> 三步流水线：DeepWiki 全量镜像（09-05 已抓）→ understand 中文知识图谱（本轮）→ onboard + explain 精讲（本轮）

KTransformers 是清华 KVCache.AI 开源的 MoE 大模型单机推理框架：**Attention 在 GPU、MoE experts 在 CPU/DISK 的异构分层部署**，让单机（甚至纯 CPU）跑起 DeepSeek 级百亿参数 MoE 模型。YAML 配置化组装 Transformer 层，每层算子可独立指定实现与硬件。

**2026 新版大重构**（本轮版本考古钉版）：
- 顶层 `ktransformers.py` 仅 35 行薄壳——pip install 后实装 **kt-kernel**（新 C++/CUDA 运行时内核）
- 经典 Python 框架整树挪入 **archive/ktransformers/**（YAML 组装遗产活在 `local_chat.py` 的 `optimize_and_load_gguf`）
- 服务层真主文件：`server/main.py`（FastAPI 装配）+ `api/openai/endpoints/chat.py`（/v1/chat/completions）

---

## 📦 资产导航

| 资产 | 内容 | 位置 |
|---|---|---|
| **DeepWiki 镜像** | 65+ 页（09-05 抓取）：语法/JSON Schema/structural tags/处理管线/运行时匹配/性能优化/C++ 实现细节 | [`deepwiki/`](./deepwiki/) |
| **知识图谱** | **2482 节点 / 4766 边 / 13 层架构 / 15 步导览**（file 567 + function 1162 + class 654；imports 880 + contains 1817 + exports 1316 + inherits 242 + calls 179；0 issues，fingerprints 557 code 文件基线） | 仓内 `.understand-anything/knowledge-graph.json`（2.1MB） |
| **新人上手指南** | 8 节 6000 字（项目概览/13 层架构/核心概念/学习路径/文件地图/复杂度热点/构建调试/常见坑） | [`onboarding/ONBOARDING.md`](./onboarding/ONBOARDING.md) |
| **重要文件精讲** | 6 篇×六节结构，论断落到方法名/行号 | [`explain/`](./explain/) 见下表 |

### explain 六篇（按学习顺序）

| # | 文件 | 主题 |
|---|---|---|
| 1 | [ktransformers-entry.md](./explain/ktransformers-entry.md) | 框架入口：薄壳化与新版装配链（含 local_chat 遗产路径） |
| 2 | [server-api.md](./explain/server-api.md) | API 服务：FastAPI 装配 + OpenAI 兼容 /v1/chat/completions |
| 3 | [moe-operator.md](./explain/moe-operator.md) | MoE 算子：experts.py 2096 行（KExpertsCPU mmap 分层/双执行器换边/decode 重叠五步） |
| 4 | [optimize-rules.md](./explain/optimize-rules.md) | 优化器：40+ YAML 规则引擎（首条命中/gen_optimize_config/两阶段编排） |
| 5 | [kt-kernel-cpu.md](./explain/kt-kernel-cpu.md) | CPU 内核：QUEST 块检索 + AMX tile_dpbusd/AVX tinyBLAS 双腿分工 |
| 6 | [kt-kernel-binding.md](./explain/kt-kernel-binding.md) | pybind11 总入口：POD 任务闭包→TaskQueue→WorkerPool→cudaLaunchHostFunc，六变体 .so 分派 |

---

## 🗺️ 十三层架构速览

```
API 服务层 86 · 文档网站前端 35
框架核心与工具 18 · 模型结构 28 · 算子层 23 · 优化层 39
kt-kernel Python 绑定 69
kt-kernel C++/CUDA 内核 138 · balance_serve 运行时 96 · 旧版 C++ 扩展 78
构建与部署 37 · CI/CD 12 · 文档 7
```

核心思想一句话：**YAML 规则决定"哪层用哪个算子放哪块硬件"，optimize_and_load_gguf 两阶段编排组装，kt-kernel 用 AMX/CUDA 微内核兑现算力**。

## 🚀 推荐路径

1. **30 分钟版**：ONBOARDING §1-2 → explain #1/#4（入口+规则引擎）
2. **半天版**：+ explain #3/#5/#6（MoE+内核深潜）+ DeepWiki 运行时匹配章
3. **深度版**：图谱 tour 15 步（全景→框架核心→YAML→模型→权重→算子注入→三大算子→优化→API→CPU 内核→模板算子→GPU→kt-cli→balance_serve→构建）

## 🔧 复现与增量

```bash
# 图谱在仓内（fingerprint 基线 commit 31985f4，557 code 文件）
# 增量：git pull 后重跑 /understand --auto-update
```

## 关联

- 上游：https://github.com/kvcache-ai/ktransformers
- 姊妹单元：[讲透vLLM](../讲透vLLM/README.md) · [讲透SGLang](../讲透SGLang/README.md) · [讲透Xinference](../讲透Xinference/README.md)（推理框架三部曲+）
- 13 仓流水线收官仓之一（2026-09-20 补齐 deepwiki 之外的图谱/指南/精讲）

# 讲透 Xinference · 分布式推理平台全量知识库

> **xorbitsai/inference（Xinference）** @ commit `b3de2604`（2026-09-03）· 收官补齐 2026-09-21
> 三步流水线：DeepWiki 全量镜像（09-05 已抓）→ understand 中文知识图谱（本轮）→ onboard + explain 精讲（本轮）

Xinference 是 Xorbits 开源的分布式推理**平台**（区别于 vLLM/SGLang 等**引擎**）：一条命令起服务，统一 RESTful API（OpenAI 兼容）部署 LLM/嵌入/重排/视觉/音频/视频全模态模型，多引擎后端（vLLM/SGLang/Transformers/llama.cpp/Mlx）可插拔，支持 xoscar actor 集群与 token-aware router。

---

## 📦 资产导航

| 资产 | 内容 | 位置 |
|---|---|---|
| **DeepWiki 镜像** | 51 页（09-05 抓取）：架构/模型支持/集群/引擎后端 | [`deepwiki/`](./deepwiki/) |
| **知识图谱** | **5301 节点 / 10685 边 / 11 层架构 / 15 步导览**（file 1231 + function 2179 + class 1803；imports 1760 + contains 3994 + exports 3743 + calls 643 + inherits 415；0 issues，fingerprints 1222 code 基线；本流水线第二大图谱） | 仓内 `.understand-anything/knowledge-graph.json`（4.3MB） |
| **新人上手指南** | 8 节 5998 字 | [`onboarding/ONBOARDING.md`](./onboarding/ONBOARDING.md) |
| **重要文件精讲** | 6 篇×六节结构 | [`explain/`](./explain/) 见下表 |

### explain 六篇（按学习顺序）

| # | 文件 | 主题 |
|---|---|---|
| 1 | [deploy-cmdline.md](./explain/deploy-cmdline.md) | 启动链：xinference-local→actor pool→RESTful 双进程 |
| 2 | [core-supervisor.md](./explain/core-supervisor.md) | SupervisorActor（7120 行）：注册表/launch/心跳自愈 |
| 3 | [llm-abstraction.md](./explain/llm-abstraction.md) | 统一抽象：LLM 基类+LLMFamilyV2+LLM_ENGINES 注册表（V1→V2 数据化） |
| 4 | [vllm-adapter.md](./explain/vllm-adapter.md) | 引擎适配：三模型类分型/load 四级路由/流式链/版本三层防御 |
| 5 | [restful-api.md](./explain/restful-api.md) | RESTful API：3832 行服务面、chat 双路径、SSE 流式 |
| 6 | [router.md](./explain/router.md) | Token-aware Router：六相管线、RoutingPolicy、CapacityGate |

---

## 🗺️ 十一层架构速览

```
自研核心 412                              第三方 vendored 907
├─ API 层 41                              （CosyVoice/whisper/fish_speech/
├─ 核心调度层 33                            qwen_vl 等模型源码内嵌）
├─ 集群路由层 35
├─ 模型注册与缓存 17
├─ LLM 模型层 103 · 多模态 91 · 嵌入重排 37
├─ 客户端 7 · 共享模块 11 · 部署 37
```

一句话主线：**cmdline 启动 → Supervisor actor 管模型生命周期 → RESTful 收请求（OpenAI 兼容）→ ModelActor 按引擎适配（vllm/sglang/...）出流式**；集群态再加 router 按能力+token 计量分发。

## 🚀 推荐路径

1. **30 分钟版**：ONBOARDING §1-3 → explain #1/#3（启动链+抽象）
2. **半天版**：+ explain #2/#4/#5（调度+引擎+API）+ DeepWiki 引擎章
3. **深度版**：图谱 tour 15 步（包入口→CLI→RESTful→Supervisor→模型守护→统一抽象→LLM 注册表→引擎适配→batching→多模态→嵌入重排→客户端→Router→容器化→vendored 疆界）

## 关联

- 上游：https://github.com/xorbitsai/inference
- 姊妹单元：[讲透vLLM](../讲透vLLM/README.md) · [讲透SGLang](../讲透SGLang/README.md)（引擎侧对照）· [讲透KTransformers](../讲透KTransformers/README.md)
- 13 仓流水线收官仓之三（2026-09-21）

# 前沿与媒体 · 37 - AI MLOps 与工程化专题

> 姊妹篇：[`讲透公开课 03 AI Infra`](../讲透公开课/03-AI%20Infra%20源码导读清单.md)｜ [`../讲透GPU与系统级/`](../讲透GPU与系统级/)。
>
> 03 是"开源 AI Infra"（vLLM/SGLang/Ray 等），本篇是"**MLOps 平台**"——端到端模型生命周期管理（实验/训练/部署/监控/治理）。给 ML 工程师 / MLOps 工程师。

---

## 0. MLOps 全流程

```
   数据准备 → 特征工程 → 训练 → 评估 → 部署 → 监控 → 再训练
       ↓         ↓         ↓       ↓       ↓       ↓       ↓
     DVC     Feast     W&B     Leaderboard → Seldon → Evidently → 触发
```

---

## 一、实验追踪 / 模型注册

| 工具 | 强项 |
|---|---|
| **Weights & Biases（W&B）** [wandb.ai](https://wandb.ai/) | **MLOps 事实标准**，实验追踪 + 模型注册 + Reports |
| **MLflow** | 开源 Databricks（轻量、广泛）|
| **Comet** | W&B 替代 |
| **Neptune.ai** | 深度学习友好 |
| **Aim** | 开源高性能实验追踪 |
| **TensorBoard** | 经典（TF 默认）|
| **HF TensorBoard / Trainer logging** | HF 默认 |

---

## 二、特征存储 / 数据版本

| 工具 | 强项 |
|---|---|
| **Feast** | 开源特征存储（Google 起源）|
| **Tecton** | 商业特征存储（Uber 团队）|
| **DVC** | 数据版本控制（基于 Git）|
| **LakeFS** | 数据湖版本 |
| **Pachyderm** | 数据管道 + 版本 |

---

## 三、编排 / 流水线

| 工具 | 强项 |
|---|---|
| **Kubeflow** | K8s 原生（复杂但强大）|
| **Airflow** | 通用 DAG（Apache）|
| **Prefect** | 现代 Airflow 替代 |
| **Dagster** | 数据资产导向 |
| **Metaflow** | Netflix 出品（Python 友好）|
| **Argo Workflows** | K8s 原生工作流 |
| **Flyte** | Lyft 出品（ML 友好）|

---

## 四、模型部署 / 服务

| 工具 | 强项 |
|---|---|
| **BentoML** | 模型打包 + 部署（开源）|
| **Seldon Core** | K8s 部署 |
| **KServe** | K8s Serverless 推理（标准）|
| **vLLM / TGI / SGLang** | 推理引擎（已在 [`讲透公开课 03`](../讲透公开课/03-AI%20Infra%20源码导读清单.md)）|
| **TorchServe** | PyTorch 官方 |
| **Triton Inference Server** | NVIDIA 官方 |

---

## 五、监控 / 治理

| 工具 | 强项 |
|---|---|
| **Evidently AI** | 数据漂移 + 模型质量监控 |
| **Arize AI** | 模型可观测性 |
| **Fiddler** | 模型监控 + 可解释 |
| **WhyLabs** | 数据质量监控 |
| **LangSmith**（LangChain）| LLM 应用监控 |
| **Helicone** | LLM API 监控 |
| **Phoenix**（Arize）| LLM 可观测性开源 |

---

## 六、商业 MLOps 平台

| 平台 | 强项 |
|---|---|
| **Databricks** | 数据 + ML 一体（Lakehouse）|
| **AWS SageMaker** | AWS 全栈 |
| **GCP Vertex AI** | Google 全栈 |
| **Azure ML** | Microsoft 全栈 |
| **Weights & Biases Platform** | 实验 + 模型管理 |
| **Vertex AI Studio / Bedrock** | LLM 平台 |
| **Hugging Face Endpoints** | 开源模型部署 |
| **Replicate / Modal / Together** | Serverless 推理 |

---

## 七、LLM Ops（新分支）

| 工具 | 强项 |
|---|---|
| **LangSmith** | LangChain 应用监控 |
| **Langfuse** | 开源 LLM 可观测 |
| **Helicone** | LLM 网关 + 监控 |
| **Portkey** | LLM 网关 |
| **PromptLayer** | Prompt 管理 |
| **Humanloop** | Prompt 评估 |
| **Braintrust** | LLM eval |
| **Promptfoo** | 开源 Prompt 评测 |

---

## 八、维护说明

- **2026-08-03 首版**。
- **重点跟踪**：W&B IPO / Databricks vs Snowflake / LLM Ops 工具整合。

📌 **下一步**：搭 MLOps？告诉我规模（个人/小团队/企业），我给推荐栈。

---

> 🔗 相关：[`讲透公开课 03`](../讲透公开课/03-AI%20Infra%20源码导读清单.md) ｜ [`34-开源生态`](./34-AI开源生态（HF与ModelScope）专题.md) ｜ [`08-Agent`](./08-AIAgent框架与工具调用专题.md)

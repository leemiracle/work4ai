# 前沿与媒体 · 34 - AI 开源生态专题（HF / ModelScope / Replicate / OpenRouter）

> 姊妹篇：[`02-后训练代码库`](./02-后训练信息源专题.md)｜ [`03-AI Infra 源码导读`](../讲透公开课/03-AI%20Infra%20源码导读清单.md)。
>
> 本篇聚焦"**模型与开源代码的入口**"——Hugging Face / ModelScope / Replicate / OpenRouter / 各类 hub。给所有 AI 开发者。

---

## 0. AI 开源生态的"四层"

```
   代码托管（GitHub）        ← 已在 01/02/03 多次提到
        ↓
   模型托管（HF Hub）        ← 本篇重点
        ↓
   数据集托管（HF Datasets） ← 本篇重点
        ↓
   推理服务（Replicate/Together） ← 已在 09
```

---

## 一、Hugging Face（事实标准）

| 子平台 | 强项 |
|---|---|
| **HF Hub** [huggingface.co](https://huggingface.co/) | 模型托管（百万+）|
| **HF Datasets** | 数据集（30 万+）|
| **HF Spaces** | ML 应用试玩（已在 [`20`](./20-AI艺术与创意社区专题.md)）|
| **Transformers** | 模型定义库（16.3w ⭐）|
| **PEFT / TRL / Diffusers / Accelerate** | 训练栈（已在 [`02`](./02-后训练信息源专题.md)）|
| **HF Courses** | 免费课（已在 [`讲透公开课 01`](../讲透公开课/01-前沿课实时清单.md)）|
| **HF Leaderboards** | Open LLM / Big Code 等 |
| **HF Inference API / Endpoints** | 商业推理 |
| **HF Hub Cloud (HF Pro / Enterprise)** | 私有部署 |

### 旗舰模型系列（开源）
- **Meta Llama 3 / 3.5 / 4**
- **Mistral / Mixtral / Codestral**
- **Qwen 2.5 / 3 / 3.5**（阿里，最热门中文）
- **DeepSeek V3 / R1**（2025 现象级）
- **Microsoft Phi / gpt-oss**
- **Google Gemma 2 / 3**
- **01.AI Yi / Yi-Vision**
- **Kimi K3**（月之暗面，2.8T MoE 开源）
- **Zhipu GLM-4 / 4.5**（智谱）

---

## 二、ModelScope（魔搭，阿里）

- **入口**：[modelscope.cn](https://modelscope.cn/)
- **地位**：中国最大开源模型平台（与 HF 对标）
- **优势**：国内带宽快，中文模型集中
- **配套**：与 PAI / 函数计算 / 通义集成

---

## 三、推理 / 托管服务

| 服务 | 强项 |
|---|---|
| **Replicate** [replicate.com](https://replicate.com/) | 一键跑模型，按秒计费 |
| **Together AI** | 开源模型 API（含 Red Pajama）|
| **Fireworks AI** | 高速推理 |
| **Modal** | Serverless GPU（含 AI 模板）|
| **Runway ML** | 视频 AI（已在 [`07`](./07-AI创意生成专题.md)）|
| **OpenRouter** [openrouter.ai](https://openrouter.ai/) | **多模型统一 API**（开发者首选）|
| **SiliconFlow 硅基流动** | 国内开源模型聚合 API |
| **DeepInfra** | 国外便宜推理 |

---

## 四、数据集 Hub

| 平台 | 强项 |
|---|---|
| **HF Datasets** | 全球最大 |
| **Papers with Code** | 论文配套数据 |
| **Kaggle Datasets** | Kaggle 生态 |
| **Common Crawl** | 网页 PB 级 |
| **LAION** | 图文对（已在 [`03`](./03-模态专题（NLP+Vision+Speech+多模态）.md)）|
| **Allen Institute Open Datasets** | Ai2 |
| **中国：百度千言 / 阿里 ModelScope** | 中文 |

---

## 五、AI 模型评估 Hub

- **LMSYS Chatbot Arena**（已在 [`01 E1`](./01-AI顶级信息源实时清单.md)/[`10`](./10-AI评测与基准大合集.md)）
- **Open LLM Leaderboard**（HF）
- **Big Code Models Leaderboard**（HF）
- **OpenCompass 司南**（已在 [`10`](./10-AI评测与基准大合集.md)）
- **Scale SEAL**（已在 [`01 E5`](./01-AI顶级信息源实时清单.md)）

---

## 六、AI Agent / 应用市场

| 平台 | 强项 |
|---|---|
| **Coze（扣子）** | 字节 Agent 平台 |
| **OpenAI GPT Store** | OpenAI GPTs 市场 |
| **Poe** | Quora 多 bot 市场 |
| **Hugging Chat Assistants** | HF Agent 市场 |
| **扣子海外版 Coze.com** | 字节海外 |

---

## 七、维护说明

- **2026-08-03 首版**：HF 已多处实抓确认活跃。
- **下次重核**：每季度（开源生态月级迭代）。
- **重点跟踪**：HF Hub 模型数突破 / 国产模型出海（DeepSeek/Qwen/Kimi 在 HF 排名）。

📌 **下一步**：找模型？告诉我用途（中文/英文/多模态/代码），我给推荐 + API 接入。

---

> 🔗 相关：[`02-后训练`](./02-后训练信息源专题.md) ｜ [`09-商业 API`](./09-AI商业产品与ToC应用专题.md) ｜ [`讲透公开课 03`](../讲透公开课/03-AI%20Infra%20源码导读清单.md)

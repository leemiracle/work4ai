# 前沿与媒体 · 09 - AI 商业产品与 ToC 应用专题

> 姊妹篇：[`06-AI 编程工具`](./06-AI编程工具专题.md)（编程向）｜ [`07-AI 创意生成`](./07-AI创意生成专题.md)（创意向）｜ [`08-AI Agent`](./08-AIAgent框架与工具调用专题.md)（框架向）。
>
> 本篇是"**消费者视角的 AI 产品地图**"——普通人日常在用什么 AI、付费给谁、各自差异化。给产品经理 / 投资人 / 普通用户的"消费决策指南"。
>
> **核对日期**：2026-08-03（首版；Anthropic 模型线 2026-08 已到 Sonnet 5 / Opus 5 / Fable 5 系列）
> **图例**：🟢 = 活跃　🟡 = 稳定　⚠️ = 反爬未核到

---

## 0. AI 消费品矩阵

```
                  通用助手 ←─────────→ 垂直专家
              ┌────────────┬────────────┐
   闭源旗舰    │ ChatGPT    │ Cursor     │
              │ Claude     │ Midjourney │
              │ Gemini     │ Suno       │
              ├────────────┼────────────┤
   开源/低门槛 │ DeepSeek   │ ComfyUI    │
              │ Qwen/通义   │ Aider      │
              │ Kimi/Llama │ OpenHands  │
              └────────────┴────────────┘
```

---

## 一、通用 AI 助手（闭源旗舰）

### 美系
| # | 产品 | 公司 | 模型 | 定位 |
|---|---|---|---|---|
| C1-1 | **ChatGPT** | OpenAI | GPT-5 / GPT-4o | 全球用户第一 |
| C1-2 | **Claude** | Anthropic | ✅ **Sonnet 5 / Opus 5 / Fable 5**（2026-08 系列升级）| 编程 / 长文 / Agent 最强 |
| C1-3 | **Gemini** | Google | Gemini 3 Pro | 原生多模态 + 集成 Workspace |
| C1-4 | **Copilot** | Microsoft | GPT 系 | 集成 Windows / Office |
| C1-5 | **Grok** | xAI | Grok 3 / 4 | X 集成，"少审查"|
| C1-6 | **Perplexity** | Perplexity | 多模型 | AI 搜索 |
| C1-7 | **Character.ai / Pi** | 独立 | 自研 | 角色对话 / 情感陪伴 |

### 中系
| # | 产品 | 公司 | 强项 |
|---|---|---|---|
| C1-8 | **豆包 / Doubao** | 字节 | 国内日活第一 |
| C1-9 | **Kimi** | 月之暗面 | **200 万字长上下文** + 国内研究者最爱 |
| C1-10 | **通义千问 / Qwen Chat** | 阿里 | 开源王者（Qwen3 / Qwen3.5 系列）|
| C1-11 | **文心一言 / 文小言** | 百度 | 国内最早 + 集成百度搜索 |
| C1-12 | **智谱清言 / ChatGLM** | 智谱 | GLM-4 / GLM-4.5 |
| C1-13 | **DeepSeek** | DeepSeek | **API 性价比之王**（V3 / R1）|
| C1-14 | **腾讯元宝 / Hunyuan** | 腾讯 | 集成微信 / 腾讯文档 |
| C1-15 | **MiniMax 海螺** | MiniMax | 多模态 / 视频生成 |

---

## 二、垂直专家产品

### 编程（详见 [`06`](./06-AI编程工具专题.md)）
- Cursor / Windsurf / GitHub Copilot / Claude Code / Devin / 通义灵码

### 创意（详见 [`07`](./07-AI创意生成专题.md)）
- Midjourney / Flux / Sora / Runway / Suno / ElevenLabs

### 办公 / 写作
| # | 产品 | 公司 | 强项 |
|---|---|---|---|
| W1 | **Notion AI** | Notion | 笔记 + AI 一体 |
| W2 | **Microsoft 365 Copilot** | Microsoft | Office 全家桶 |
| W3 | **Google Workspace AI** | Google | Docs/Gmail/Sheets |
| W4 | **Grammarly / DeepL Write** | 独立 | 英文写作润色 |
| W5 | **Writefull / PaperPal** | 独立 | 学术英文 |
| W6 | **有道 / WPS AI** | 网易 / 金山 | 中文办公 |

### 搜索 / 知识库
| # | 产品 | 公司 | 强项 |
|---|---|---|---|
| S1 | **Perplexity** | Perplexity | AI 搜索领导者 |
| S2 | **Genspark / You.com** | 独立 | AI 搜索竞争者 |
| S3 | **Glean** | Glean | 企业内部搜索 |
| S4 | **百度 AI 搜索 / 秘塔** | 百度 / 秘塔 | 中文 AI 搜索 |

### 客服 / 企业垂直
- Sierra / Decagon / Crescendo / Forethought（海外）
- 智齿 / 网易七鱼 / 容联七陌（中文）

### 数据分析
- **Julius AI / DeepNote / Hex / Mode** （数据科学）
- **Tableau Pulse / ThoughtSpot**（BI）

### 教育
- **Khan Academy Khanmigo**（K-12）
- **Duolingo Max**（语言）
- **Chegg / Course Hero**（高等教育）

---

## 三、API 平台（开发者向）

| # | 平台 | 强项 |
|---|---|---|
| A1 | **Anthropic API** | Claude Sonnet 5 / Opus 5 / Fable 5（2026-08）|
| A2 | **OpenAI API** | GPT-5 / Realtime / Embeddings |
| A3 | **Google Vertex AI** | Gemini 3 / 全栈 ML |
| A4 | **Together AI / Fireworks / Replicate** | 推理服务，开源模型多 |
| A5 | **OpenRouter** | **多模型统一 API**（开发者最常用）|
| A6 | **DeepSeek API** | 性价比之王 |
| A7 | **阿里百炼 / 火山引擎** | 中文 API |
| A8 | **SiliconFlow 硅基流动** | 国内开源模型 API 聚合 |

---

## 四、评测 / 选型参考

- **LMSYS Chatbot Arena**（[`01 清单 E1`](./01-AI顶级信息源实时清单.md)）：人类偏好金标准
- **Artificial Analysis**（[`01 清单 E4`](./01-AI顶级信息源实时清单.md)）：API 性价比
- **OpenCompass / SuperCLUE**：中文榜单
- **Hugging Face Spaces**：试玩

---

## 五、维护说明

- **2026-08-03 首版**：基于圈共识 + Anthropic 公告页确认 5 系列。
- **下次重核**：每月（消费产品月级迭代，模型日级迭代）。
- **重点跟踪**：Claude Sonnet 5 / GPT-5.5 / Gemini 4 / 国产模型下半年大版本。

📌 **下一步**：选模型纠结？告诉我用途（编程 / 写作 / 分析 / 多模态）+ 预算，我给推荐。

---

> 🔗 相关：[`../横向打通-能力获取决策框架.md`](../横向打通-能力获取决策框架.md)（怎么选方法）

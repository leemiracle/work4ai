# 前沿与媒体 · 36 - AI 数据标注与 RLHF 数据专题

> 姊妹篇：[`02-后训练数据集`](./02-后训练信息源专题.md)｜ [`35-创投`](./35-AI创业投资生态专题.md)（Scale 估值 $14B）。
>
> 数据是 LLM 的"生产资料"，**标注公司是 AI 链条最被忽视的"金矿"**——Scale AI $14B、Labelbox、Surge AI 是后训练真正的幕后推手。

---

## 0. AI 数据标注的"三波"

```
   ① 早期 CV 标注（2010s）         ← ImageNet / Scale AI 起家
        ↓
   ② 语音/NLP 标注（2015-2020）    ← Mozilla Common Voice / Appen
        ↓
   ③ RLHF 偏好标注（2022+）        ← Surge AI / Remotasks / Invisible Tech
        ↓
   ④ AI-辅助标注（2024+）          ← LLM 预标 + 人审 / Snorkel
```

---

## 一、顶级数据标注公司

| 公司 | 强项 | 状态 |
|---|---|---|
| **Scale AI** [scale.com](https://scale.com/) | **数据标注 No.1**（$14B 估值）/ Donovan 军用 / RLHF 一线供应商 | 🟢 |
| **Surge AI** [surgehq.ai](https://www.surge.ai/) | 高质量 RLHF 标注 | 🟢 |
| **Labelbox** | 数据引擎 + 标注平台 | 🟢 |
| **Snorkel AI** | **程序化标注**（弱监督） | 🟢 |
| **Appen**（澳洲上市）| 老牌标注，规模大但增长乏力 | 🟡 |
| **Invisible Technologies** | AI + 人审混合 | 🟢 |
| **Remotasks**（Scale 子）| 众包标注平台 | 🟢 |
| ** Toloka / Clickworker / Amazon MTurk** | 众包 | 🟡 |

### 中文标注
- **百度数据标注基地 / 阿里 / 字节**（自有）
- **龙猫数据 / 海天瑞声 / 标贝科技 / 数据堂**（专业公司）

---

## 二、关键数据集 / RLHF 数据

| 数据集 | 类型 | 强项 |
|---|---|---|
| **UltraFeedback**（已在 [`02 PT-D1`](./02-后训练信息源专题.md)）| 偏好对 | DPO 通用首选 |
| **HH-RLHF**（Anthropic）| 偏好对 | 经典 |
| **ShareGPT** | 真实用户对话 | 早期 SFT 重要源 |
| **OpenAssistant**（LAION）| 多语言对话 | 开源社区 |
| **Magpie**（已在 [`02 PT-D4`](./02-后训练信息源专题.md)）| 自合成 | ICLR 2025 |
| **RLHF-V / LLaVA-RLHF** | 多模态偏好 | 视觉对齐 |

---

## 三、数据标注工具（自托管）

| 工具 | 强项 |
|---|---|
| **Label Studio** | 开源全栈（CV/NLP/音频/视频）|
| **CVAT**（OpenCV）| 计算机视觉标注 |
| **Doccano** | NLP 标注（NER/分类/翻译）|
| **Prodigy**（spaCy 团队）| 主动学习 |
| **Label Studio + ML 后端** | AI 预标 + 人审 |
| **Argilla** | 现代 NLP 标注 |

---

## 四、合成数据（2024+ 趋势）

| 公司 / 技术 | 强项 |
|---|---|
| **Gretel / Mostly AI / Tonic** | 表格合成数据 |
| **Coxy / Datagen** | 视觉合成 |
| **Anthropic / OpenAI 内部** | 用 LLM 合成训练数据 |
| **Magpie / Self-Instruct / Evol-Instruct** | 自合成指令 |
| **Distillation from GPT-4/Claude** | 经典"模型蒸馏"（被 OpenAI TOS 限制）|

---

## 五、关键议题

- **AI 时代的标注工人生存**：非洲/菲律宾时薪 $1-2 的"AI 血汗工厂"（《Time》调查）
- **数据投毒**（已在 [`25`](./25-AI隐私与生物特征专题.md)）
- **版权**：Reddit/X/NYT 等内容平台要求数据付费
- **GPT-4 蒸馏合规**：OpenAI TOS 禁止用 GPT-4 训竞争模型

---

## 六、维护说明

- **2026-08-03 首版**。
- **重点跟踪**：Scale AI IPO 进展 / 合成数据替代人工 / 中文标注出海。

📌 **下一步**：标注某任务？告诉我（CV/NLP/RLHF/多模态），我给推荐工具 + 成本估算。

---

> 🔗 相关：[`02-后训练数据`](./02-后训练信息源专题.md) ｜ [`25-隐私`](./25-AI隐私与生物特征专题.md) ｜ [`35-创投`](./35-AI创业投资生态专题.md)

# 00 · AI for Linguistics 是什么

> **第一性问题**：NLP（自然语言处理）是 CS 角度的语言技术——但**语言学**是研究语言本身的科学。LLM 时代，**语言学没死，反而被重新激活**——因为 LLM 给了语言学家**前所未有的实验工具**。
>
> **核心问题**：LLM 真的"理解"语言吗？还是只是统计模式？这是语言学的复兴。
>
> 配套：[`讲透NLP`](../../讲透NLP-learning/)（CS 角度）+ [`讲透基础模型/advanced/02 涌现`](../../讲透基础模型/advanced/02-涌现的争论.md)

---

## 一、语言学为什么被 AI 重塑

### 1.1 经典语言学

- **生成语法**（Chomsky）：普遍语法 / 语言习得装置
- **结构主义**（Saussure）：能指 / 所指
- **认知语言学**：隐喻 / 框架

### 1.2 LLM 的挑战

- LLM **没普遍语法**——只学统计模式
- 但 LLM **能流利对话**——挑战 Chomsky 路线
- **Bender/Marcus**："随机鹦鹉"——LLM 不理解语言

### 1.3 经验主义复兴

- Chomsky 反对经验主义（行为主义）
- LLM = 极端经验主义（海量数据）
- **Chomsky vs Hinton 大战**（2023-）

---

## 二、AI 在语言学的六大应用

### 2.1 LLM 作为语言模型

- **LLM 内部表示**：揭示语言结构
- **Mechanistic Interpretability**：找语法 circuit
- 详见 [`讲透可解释性`](../../讲透可解释性/)。

### 2.2 形态学 + 词典学

- 自动词形分析
- LLM 辅助编纂词典
- **语料库语言学**复兴

### 2.3 句法学

- **句法树自动分析**（dependency parsing）
- LLM 的句法表示
- **争议**：LLM 学到真句法还是统计

### 2.4 语义学

- **词义消歧**
- **语义角色标注**
- **LLM 的语义表示**（BERTology）

### 2.5 语用学

- **言外之意**（暗示 / 讽刺 / 隐喻）
- LLM 的语用能力（仍有挑战）
- **对话分析**

### 2.6 社会语言学

- **方言 / 语言变体**
- LLM 的语言偏见（标准语 vs 方言）
- **AI 与语言平等**

---

## 三、语言学专属的方法学

### 3.1 语料库 + 统计

- **Brown Corpus / BNC / COCA**
- LLM 替代传统统计
- **大规模语言证据**

### 3.2 Psycholinguistics（心理语言学）

- 眼动 + EEG + LLM
- 比较人 vs LLM 处理
- 详见 [`讲透AIfor各学科/心理学`](../心理学/)。

### 3.3 田野调查 + AI

- 濒危语言记录
- AI 辅助语言学田野
- **Endangered Languages Project**（Google）

### 3.4 跨语言比较

- LLM 跨语言表示
- 普遍语法 vs 语言特异
- **XNLI / XTREME** benchmark

---

## 四、当前前沿（2024-2026）

### 4.1 LLM 句法 / 语义 circuit

- **Anthropic**：找 LLM 的语法 circuit
- **Tenney 2019 / Manning 2020s**：BERT 的句法表示
- **意义**：揭示 LLM 内部语法

### 4.2 Chomsky vs Hinton 大战

- **Chomsky 2023**：LLM 不理解语言
- **Hinton**：LLM 学到真表示
- **语言学界的核心争论**

### 4.3 濒危语言 AI

- **ELP**（Endangered Languages Project）
- AI 帮助记录 + 教学
- 3000+ 濒危语言

### 4.4 多语言 LLM

- **XGLM / BLOOM / Aya**
- 低资源语言支持
- **语言平等**

### 4.5 LLM 与语言习得

- 儿童学语言 vs LLM 学语言
- **数据效率**差异巨大
- **Chomsky 的论据**

---

## 五、AI 改变了语言学的什么

### 5.1 语言学的复兴

- LLM 给了**实验工具**
- 经典问题可测（LLM 有普遍语法吗？）

### 5.2 计算语言学主流化

- 从边缘到核心
- **所有语言学家必须懂 CS**

### 5.3 应用语言学爆发

- 机器翻译 / 教育语言 / 临床语言学
- LLM 让语言学应用扩展

### 5.4 语言多样性的挑战

- LLM 偏向高资源语言
- 低资源语言被边缘化
- **语言灭绝加速？**

---

## 六、开放问题

1. **LLM 理解语言吗**？Chomsky vs Hinton
2. **LLM 有普遍语法吗**？
3. **AI 加速语言灭绝还是保护**？
4. **LLM 的语言偏见**（英语中心）？
5. **AI 时代的语言学教育**？

---

## 七、一句话总结

> 🎯 **四句话**：
> 1. **LLM 让语言学复兴**——经典问题（普遍语法 / 理解）可测。
> 2. **六大应用**：LLM 作为模型 / 形态 / 句法 / 语义 / 语用 / 社会语言。
> 3. **核心争论**：Chomsky vs Hinton——LLM 理解语言吗？
> 4. **挑战**：语言偏见（英语中心）+ 濒危语言保护。

---

📌 **下一步**

1. **读**：Manning BERT syntax / Chomsky vs Hinton 2023。
2. **和 [`讲透NLP`](../../讲透NLP-learning/) + [`讲透可解释性`](../../讲透可解释性/) 对照**。
3. **进入 [01 LLM 句法 circuit 深挖](./)**（待补）。
---


---

## 🇨🇳 国内可访问资源映射

> 本领域核心资源多托管在大陆不易访问的平台（Google 系被墙、GitHub/HuggingFace 不稳定、Nature/Science 付费墙）。下表给出**国内可直接访问**的对应入口。

### 通用映射（所有 AI for 学科共享）

| 类型 | 境外 | 国内可访问 |
|---|---|---|
| 论文检索 | Google Scholar | [百度学术](https://xueshu.baidu.com) / [Semantic Scholar](https://semanticscholar.org)（可直连）/ [知网](https://cnki.net) |
| 论文全文 | Nature/Science/arXiv | [NSTL](https://nstl.gov.cn) 免费文献传递 / Semantic Scholar / 中科院文献情报中心 |
| 代码 | GitHub | [Gitee](https://gitee.com) / [ghproxy](https://ghproxy.com) 加速 |
| 模型/权重 | HuggingFace | [ModelScope 魔搭](https://modelscope.cn) / [百度千帆](https://cloud.baidu.com/product/wenxinworkshop) |
| 数据集 | 境外数据托管 | [阿里云天池](https://tianchi.aliyun.com) / [百度 AI Studio](https://aistudio.baidu.com) |
| 算力 | Colab / AWS GPU | [阿里 PAI](https://pai.alibaba.com) / [百度 BCC](https://cloud.baidu.com/product/bcc/gpu.html) / 各地**智算中心** |
| 大模型 API | GPT-4 / Claude | [智谱 GLM](https://zhipuai.cn) / [DeepSeek](https://deepseek.com) / [通义千问](https://tongyi.aliyun.com) / [文心](https://yiyan.baidu.com) |
| 视频/课程 | YouTube / Coursera | [B站](https://bilibili.com) / [学堂在线](https://xuetangx.com) / [中国大学 MOOC](https://icourse163.org) |

### 本学科特有

| 境外资源 | 国内可访问对应 |
|---|---|
| HuggingFace 语言学模型 | [ModelScope](https://modelscope.cn) / [OpenBMB](https://openbmb.org) |
| Universal Dependencies（GitHub）| Gitee 镜像 |
| WALS 世界语言结构图鉴 | 可直连（Max Planck 公开）/ 中国语言资源保护 |
| endangered languages 数据 | [中国语言资源保护工程](https://zhongguoyuyan.cn) |

📌 **一句话**：论文→Semantic Scholar/NSTL；代码→Gitee；模型→ModelScope；数据→天池/AI Studio；全程无需翻墙。

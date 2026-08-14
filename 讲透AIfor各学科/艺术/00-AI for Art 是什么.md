# 00 · AI for Art 是什么

> **第一性问题**：艺术是**人类创造力的最高表达**——AI 生成艺术（Midjourney / DALL-E / Stable Diffusion）2022 爆发，引发"**机器能创作艺术吗**"的根本争议。

## 一、AI 艺术的爆发

### 1.1 时间线

- **2014**：GAN（Goodfellow）—— AI 艺术开始
- **2021**：CLIP + VQGAN —— 早期文本生成
- **2022.4**：DALL-E 2（OpenAI）
- **2022.7**：Midjourney
- **2022.8**：Stable Diffusion（开源）
- **2024+**：Sora / Veo / Genie（视频）

### 1.2 公众反应

- **AIGA 比赛 2022**：Jason Allen 用 Midjourney 拿一等奖 → 争议
- **Getty Images 起诉 Stability AI**
- **艺术家集体诉讼**

## 二、AI 艺术技术

### 2.1 扩散模型

- 详见 [`讲透生成模型`](../../../讲透生成模型/)
- **DDPM / Stable Diffusion**
- 文本 → 图像

### 2.2 风格迁移

- **Gatys 2015**（神经风格迁移）
- A 照片 + B 风格 → 合成

### 2.3 超分辨率 + 修复

- 老照片修复
- 图像扩展（outpainting）
- **AI 修复**艺术品

### 2.4 视频生成

- Sora / Veo / Pika
- 短视频 / 动画
- **2024 商业化**

## 三、艺术研究 + AI

### 3.1 艺术史分析

- 大规模画作分析
- 风格演化
- **Artsy / WikiArt**

### 3.2 鉴定 + 真伪

- AI 判断画作年代 / 作者
- **Rucci / Casabona** 工作
- 但有错误案例

### 3.3 保护 + 修复

- AI 分析颜料 / 退化
- 虚拟修复
- **Mona Lisa 复原**

## 四、争议

### 4.1 "AI 算艺术吗"

- **工具主义**：是工具，人在用
- **作者主义**：AI 没意图 → 不是艺术
- **合作主义**：人机共创

### 4.2 版权

- 训练数据侵权（艺术家未授权）
- AI 生成作品不受版权（美国版权局）
- **NYT vs OpenAI** 延伸

### 4.3 艺术家生计

- 插画师 / 概念设计师失业？
- **2023 罢工**（Hollywood）
- **新工作流**：AI 辅助

### 4.4 多元 / 偏见

- Stable Diffusion 偏见（种族 / 性别）
- **西方美学**主导
- **去殖民化**艺术 AI

## 五、未来方向

### 5.1 个性化艺术

- 个人定制
- **AI + 用户共创**

### 5.2 沉浸式 + VR

- 生成 3D 场景
- 元宇宙艺术

### 5.3 实时生成

- 游戏 / 影视实时
- **AI 美术师**

### 5.4 艺术 + 教育

- AI 教绘画
- **降低门槛**

## 六、博士级练习

1. 用 Stable Diffusion 创作并分析偏见
2. 实现风格迁移（PyTorch）
3. 评估 AI 艺术 vs 人类艺术

## 关键引用

- Goodfellow 2014 GAN
- Rombach 2022 Stable Diffusion
- Saharia 2022 DALL-E 2
- Bender 2021（批评）
- EPFL Artlab 2024 *The Art of AI*
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
| Stable Diffusion（HuggingFace）| [ModelScope 搜 Stable Diffusion](https://modelscope.cn) / [百度文心一格](https://yige.baidu.com) |
| CLIP（OpenAI）| ModelScope / Gitee 镜像 |
| Midjourney / DALL-E | 国产：**通义万相** / **文心一格** / **智谱 CogView** |
| ArtStation / Behance | [站酷](https://zcool.com.cn) / 花瓣网 |

📌 **一句话**：论文→Semantic Scholar/NSTL；代码→Gitee；模型→ModelScope；数据→天池/AI Studio；全程无需翻墙。

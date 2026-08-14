# 00 · AI for Archaeology 是什么

> **第一性问题**：考古学是**通过物质遗存研究人类过去**——AI 帮考古学家"看见"看不见的：地下遗址 / 古代气候 / 古 DNA / 文化传播。

## 一、考古的挑战

### 1.1 数据稀缺 + 破碎

- 物质遗存少 / 不完整
- 解释依赖专家

### 1.2 大范围 + 不可见

- 遗址藏在地下
- 战乱区难进入

### 1.3 多源 + 跨学科

- 遥感 / 古 DNA / 化学 / 历史

## 二、AI 在考古

### 2.1 遥感 + AI 找遗址

- **LiDAR**（激光雷达）：穿透植被
- **卫星**：多光谱
- 案例：**玛雅 / 吴哥 / 丝绸之路**

### 2.2 古 DNA + 演化

- 详见 [`人类学/advanced/01`](../人类学/advanced/01-古DNA与演化分析.md)

### 2.3 文物分析

- 风格 / 年代 / 来源
- **化学成分**（XRF / 质谱）
- AI 分类 + 聚类

### 2.4 文化层 + 地层

- 自动识别考古层
- 时序分析

### 2.5 数字重建

- 3D 扫描
- 虚拟重建古城

## 三、关键案例

### 3.1 LiDAR 玛雅（2018+）

- 发现 6 万 + 古建筑
- 改写玛雅人口估计

### 3.2 Sarah Parcak / GlobalXplorer

- 卫星 + AI
- 公民科学
- **埃及 / 罗马新遗址**

### 3.3 Vesuvius（2024）

- 详见 [`历史学/advanced/02`](../历史学/advanced/02-Vesuvius与古籍AI.md)

### 3.4 中国新疆沙漠

- 雷达 + AI 找地下古城
- 丝绸之路遗址

## 四、方法学

### 3.1 多光谱遥感

- NDVI / 微波 / LiDAR
- AI 融合

### 3.2 古地磁 + AI

- 测年代
- AI 加速

### 3.3 化学指纹

- 同位素 + ML
- 推断来源

## 五、博士级练习

1. 在公开 LiDAR 数据找异常
2. 分析 Vesuvius 方法
3. 评估 GlobalXplorer 案例

## 关键引用

- Parcak 2017 *Archaeology from Space*
- Chase 2011 *PNAS*（玛雅 LiDAR）
- UNESCO 报告


---

## 领域知识深化：考古学核心技术

| 技术 | 原理 | AI 角色 |
|---|---|---|
| **LiDAR** | 激光雷达穿透植被测地形 | AI 自动识别遗址特征 |
| **遥感(卫星/无人机)** | 多光谱/雷达成像 | AI 图像分类/变化检测 |
| **地层学** | 文化层堆积顺序 | AI 辅助 3D 地层建模 |
| **类型学** | 文物分类/断代 | AI 图像分类/相似度匹配 |
| **C14 测年** | 放射性碳衰变 | 贝叶斯校正(BCal/OxCal) |
| **古DNA** | 古代基因组测序 | AI 基因组组装/人群分析 |
| **3D 重建** | 摄影/激光扫描 | NeRF/Gaussian Splatting |

**关键遗址项目**：Vesuvius Challenge(赫库兰尼姆古卷 AI 解读) / Giza Plateau(3D 重建)

**工具**：QGIS(地理信息) / Agisoft Metashape(3D) / Google Earth Engine / 古DNA分析
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
| LiDAR 遥感数据（美国 USGS）| [中科院空天院](http://air.cas.cn) / [国家文物局](http://ncha.gov.cn) |
| 古 DNA（Max Planck / Allen）| [国家基因库 CNGB](https://cncb.ac.cn) / 中科院古脊椎所 |
| Vesuvius / Ithaca（古籍）| 官网 / Gitee 镜像 |
| 3D 遗产数据 | [国家文物局](http://ncha.gov.cn) / 敦煌研究院 |

📌 **一句话**：论文→Semantic Scholar/NSTL；代码→Gitee；模型→ModelScope；数据→天池/AI Studio；全程无需翻墙。

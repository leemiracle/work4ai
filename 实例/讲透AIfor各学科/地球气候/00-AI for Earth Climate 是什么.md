# 00 · AI for Earth & Climate 是什么

> **第一性问题**：天气、海洋、地震、野火、气候变化——都是**混沌高维 PDE 系统**。人类靠超级计算机 + 数值方法做了 70 年，但 AI 在 2023-2024 一举超越——**GraphCast 在 10 天预报上击败 ECMWF IFS**（行业金标准 40 年）。
>
> 这是 AI 改变科学方法的最强实证之一。
>
> 配套：[`讲透AIfor各学科/物理`](../物理/)（流体力学）+ [`讲透AI应用全景/01-AI4Science`](../../讲透AI应用全景/01-AI4Science.md)

---

## 一、地球为什么需要 AI

### 1.1 系统 complexity

```
大气：10^25 个分子，三维 + 时间
海洋：10^25 个水分子，洋流 + 温度 + 盐度
陆地：地形 / 植被 / 土壤
冰雪：极地 / 冰川
生物圈：植被 / 动物
```

**耦合系统** + 非线性 + 多尺度——经典数值方法算到极限。

### 1.2 数据丰富但分散

- **卫星**：每秒 TB
- **气象站**：全球 1 万+
- **海洋浮标**：千+
- **地震仪**：万+
- **遥感**： Landsat / Sentinel

**问题**：数据多，但**异构 + 噪声 + 缺失**——AI 擅长处理。

### 1.3 紧迫应用

- **极端天气**（洪水 / 飓风 / 野火）越来越频繁
- **气候变化** 需要百年预测
- **自然灾害**需要实时预警

---

## 二、AI 在地球科学的五大应用

### 2.1 天气预报（**最强实证**）

**GraphCast**（DeepMind 2023 *Science*）：
- **GNN 全球天气预报**
- **10 天预报准确度超 ECMWF IFS**（行业金标准 40 年）
- **快 1000 倍**（单 TPU 分钟 vs 超算小时）
- **意义**：**第一次 AI 完胜数值方法**

**后续**：
- **Pangu-Weather**（华为 2023 *Nature*）：3D Earth-Specific Transformer
- **FourCastNet**（NVIDIA）：Fourier Neural Operator
- **FuXi**（复旦大学）：级联网络
- **GenCast**（DeepMind 2024）：扩散生成 + 集合预报
- **Aurora**（微软 2024）：多大气 + 海洋 + 气候基础模型

### 2.2 气候变化建模

**挑战**：百年预测 + 系统耦合。

**AI 方法**：
- **气候模型模拟器**（emulator）：替代慢数值模型
- **极端事件归因**：气候变化对单事件的影响
- **区域降尺度**（downscaling）：从粗到细
- 代表：**ClimSim**（2023 benchmark）

### 2.3 自然灾害

**应用**：
- **野火预测**（Google 2024 *Nature*）：全球野火蔓延预测
- **洪水预警**（Google 2024 *Nature*）：80+ 国家
- **地震预警**：实时检测 P 波
- **台风路径**：深度学习超经典
- **火山喷发**：InSAR + AI

### 2.4 海洋

- **洋流预测**：**Aurora** 等
- **海洋生物**：浮游植物分布
- **海平面上升**：卫星 + AI
- **海洋酸化**

### 2.5 陆地与生态

- **森林覆盖**：卫星 + AI 监测砍伐
- **农业**：作物产量预测 / 病虫害
- **地下水**：预测枯竭
- **生物多样性**：物种分布

---

## 三、地球科学专属的方法学

### 3.1 球面 / 几何约束

地球是球——AI 必须处理：
- **球面卷积**（Spherical CNN）
- **等变性**：旋转不变（地球自转）
- **图结构**：经纬网格 vs 六边形网格

**GraphCast** 用 **icosahedral grid**（20 面体细分）—— 球面均匀。

### 3.2 物理嵌入

- **守恒律**：能量 / 动量 / 质量
- **热力学**：熵增
- **AI 不能违反**——**Physics-Informed**

**GraphCast** 没显式约束，但学到了守恒（**emergent conservation**）。

### 3.3 多尺度

- **微观**（云形成）：米 / 秒
- **中观**（锋面）：百公里 / 时
- **宏观**（气候变化）：全球 / 年

**AI 多尺度建模** 是 2024+ 前沿。

### 3.4 数据同化（Data Assimilation）

把观测融入模型——**经典 KF / 4DVar vs AI**。

- **FourDimNet** 等
- **AI 加速数据同化** 100-1000 倍

---

## 四、当前前沿（2024-2026）

### 4.1 Aurora（微软 2024）

- 大气 + 海洋 + 气候 + 空气污染
- **通用地球基础模型**
- 5 个任务 SOTA

### 4.2 GenCast（DeepMind 2024）

- 扩散模型做**集合预报**（ensemble）
- 比 ECMWF ENS 更准（97.2% 情况）
- **概率预报** —— 决策关键

### 4.3 Prithvi（NASA-IBM 2023）

- 开源地球科学基础模型
- 多任务（洪水 / 野火 / 农业）

### 4.4 极端事件归因

- "气候变化使这次热浪概率增加 X 倍"
- AI 加速归因分析
- 政策影响大

### 4.5 早期预警

- **AI 地震预警**：秒级
- **AI 野火检测**：分钟级
- **Google Flood Hub**：80+ 国家免费预警

---

## 五、AI 改变了地球科学的什么

### 5.1 数值方法被颠覆

- **GraphCast 第一次完胜 ECMWF**——40 年的标杆被推翻
- 经典数值方法**没死**，但**必须重新定位**

### 5.2 全球公共产品

- Google 洪水预警免费给 80+ 国家
- AI 拯救生命（数十万人受益）
- **AI 的最大公益应用之一**

### 5.3 气候政策

- AI 加速气候归因
- 法律意义："气候变化造成这次灾害"——可追责
- **气候赔偿** + **政策制定**

---

## 六、开放问题

1. **气候百年预测的可靠性**？AI 能信吗？
2. **极端事件预测的极限**？
3. **AI 替代数值方法 vs 共存**？
4. **球面 + 多尺度 AI 的统一架构**？
5. **气候政策的伦理**？AI 归因算法律证据吗？

---

## 七、一句话总结

> 🎯 **四句话**：
> 1. **GraphCast 2023** 完胜 ECMWF——**AI 颠覆 40 年数值预报标杆**。
> 2. **五大应用**：天气（Pangu/GraphCast/Aurora）/ 气候 / 灾害（Google flood/wildfire）/ 海洋 / 陆地。
> 3. **方法学**：球面几何 + 物理约束 + 多尺度 + 数据同化。
> 4. **AI 改变地球科学**：数值方法颠覆 + 全球公益（预警）+ 气候政策——**AI4Science 最直接惠民的领域**。

---

📌 **下一步**

1. **读**：GraphCast *Science* 2023 / Aurora / GenCast。
2. **和 [`讲透AIfor各学科/物理`](../物理/) 流体力学 + PDE 对照**。
3. **思考开放问题**——AI 百年气候预测可信吗？博士论文级。
4. **进入 [01 GraphCast 深挖](./)**（待补）。
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
| GraphCast（DeepMind 天气）| ModelScope 搜 GraphCast / Gitee 镜像 |
| ECMWF 数据（欧洲）| [国家气象局](http://cma.gov.cn) / CMA 数据 |
| Google 洪水预警 | 论文（Semantic Scholar）|
| CMIP6 气候数据 | [国家气候中心](http://ncc.cma.gov.cn) / 清华大学 |

📌 **一句话**：论文→Semantic Scholar/NSTL；代码→Gitee；模型→ModelScope；数据→天池/AI Studio；全程无需翻墙。

# 历史学 · Vesuvius Challenge + 古籍 AI

> **博士级**：Vesuvius Challenge 等 2024 突破案例。

## 一、Vesuvius Challenge（2023-2024）

### 1.1 背景

- **赫库兰尼姆纸草卷**（Herculaneum papyri）
- AD 79 维苏威火山喷发碳化
- 18 世纪挖掘——但无法展开
- **800+ 卷**待读

### 1.2 突破

- **2023**：**Brent Seales**（Kentucky）X 射线 CT 扫描
- **挑战**：从 CT 重建找墨迹（碳 vs 碳）
- **2024.2**：**第一个团队**读出一段希腊文
- **奖金**：$700K+

### 1.3 方法

```
X 射线 CT 扫描
   ↓ 3D 体素
AI 模式识别
   ↓ ink vs papyrus
分割 + 解卷
   ↓
文字识别（古希腊文）
   ↓ 翻译
```

### 1.4 意义

- **可能改写古代哲学**（伊壁鸠鲁学派）
- **多卷可读**——大量新文献
- **方法可扩展**到其他古卷

## 二、Ithaca + Pythia（DeepMind）

### 2.1 Ithaca（Nature 2022）

- 古希腊铭文修复
- **断代准确率 ~70%**（vs 人 25%）
- **地点归因** ~70%

### 2.2 方法

- **Transformer** 处理铭文文本
- 训练数据：**PHI Greek Inscriptions**
- 多任务：修复 + 断代 + 地点

### 2.3 应用

- 历史学家**交互式使用**
- Ithaca CAN 界面

## 三、中国古籍 AI

### 3.1 CBDB（中国历代人物传记）

- **哈佛 + 北京大学 + 中研院**
- 40 万+ 历史人物
- 关系网络 + 传记

### 3.2 数字敦煌

- 7 世纪洞窟 3D 扫描
- AI 修复壁画
- 虚拟博物馆

### 3.3 古汉语 NLP

- 古汉语 → 现代汉语翻译
- 自动注释
- **MARKUS**（Donald Sturgeon）

## 四、其他突破

### 4.1 Seshat（全球历史数据库）

- **Peter Turchin** 等
- 跨文化历史数据
- **量化历史**

### 4.2 文艺复兴档案

- **意大利 / 梵蒂冈档案**
- LLM 处理手稿
- **新发现**

### 4.3 古埃及 / 美索不达米亚

- 楔形文字 OCR
- 象形文字识别
- **Google Arts & Culture**

## 五、考古 AI

### 5.1 LiDAR + AI

- **玛雅古城**（Caracol / Tikal）
- **亚马逊雨林** 失落城市
- AI 自动识别

### 5.2 卫星 + AI

- **Sarah Parcak**（GlobalXplorer）
- 中东 / 地中海遗址
- **公民科学**

### 5.3 水下考古

- 声呐 + AI
- 沉船识别
- 深海遗址

## 六、挑战

### 6.1 数据偏见

- 西方 / 英语中心
- 古文明数据不均

### 6.2 解释

- AI 修复可能**编造**
- 必须人类验证
- **透明度**

### 6.3 文化敏感

- 谁的遗产？
- 原住民数据主权

## 七、博士级练习

1. 用 Ithaca 界面分析一段铭文
2. 实现 LDA 分析古典文本
3. 评估 Vesuvius 方法

## 关键引用

- Assael 2022 *Nature* Ithaca
- Seales 2024 Vesuvius
- CBDB 文档
- Turchin 2018 *Historical Dynamics*

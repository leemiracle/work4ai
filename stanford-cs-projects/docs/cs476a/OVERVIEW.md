# CS476A: Music, Computing, and Design

> Stanford University, Autumn 2026
> 领域: 计算机音乐 / 创意编程
> Prerequisites: 编程基础 + 对音乐有兴趣（无需正式训练）
> Units: 3-4
> Difficulty: ⭐⭐⭐

---

## 📚 定位

用代码创造音乐——从算法作曲到交互式音乐系统，探索计算与艺术的交叉。

---

## 🎯 学习目标

- 理解声音的物理表示（频率、波形、频谱）
- 掌握算法作曲方法（马尔可夫链、L-system、规则系统）
- 能用 ChucK / Sonic Pi 进行实时音乐编程
- 设计交互式音乐系统

---

## 📅 核心模块

### Module 1: 声音基础
- 音高、频率与十二平均律
- 波形（正弦、方波、锯齿、三角）
- 谐波与音色
- 包络（ADSR）

### Module 2: 音乐理论速成
- 音阶（大调 / 小调 / 五声）
- 和弦与和弦进行
- 节奏与拍号
- 调式与转调

### Module 3: 算法作曲
- 马尔可夫链旋律生成
- L-system 与分形音乐
- 随机与噪声（白噪 / 粉噪）
- 约束满足作曲

### Module 4: 数字音频处理
- 采样与 Nyquist 定理
- 滤波器（低通 / 高通 / 带通）
- 混响、延迟与效果器
- 快速傅里叶变换（FFT）

### Module 5: 交互音乐系统
- 实时 Live Coding（ChucK / Sonic Pi）
- 传感器与物理输入
- 机器学习驱动的音乐生成（MusicVAE）
- 音乐可视化

---

## 💻 项目代码

📁 `supplementary/undergrad_projects.py::cs476a_demo`

**实现内容**:
1. ✅ 音符→频率映射（C4=261.63Hz）
2. ✅ C 大调音阶
3. ✅ 马尔可夫链旋律生成（7 音符转移矩阵）
4. ✅ 随机生成 8 音符旋律并输出频率

**运行**:
```bash
cd supplementary
python3 undergrad_projects.py
```

**输出示例**:
```
生成的旋律: C D E G C D G C
频率: ['262Hz', '294Hz', '330Hz', '392Hz', '262Hz', '294Hz', '392Hz', '262Hz']
关键: MIDI / 频率 / 和声 / 节奏 / Chuck 语言
```

---

## 📊 关键概念

| 概念 | 说明 |
|------|------|
| **ChucK** | Stanford 开发的强时间音乐编程语言 |
| **MIDI** | 数字音乐接口标准 |
| **马尔可夫链** | 基于状态转移的概率作曲 |
| **FFT** | 频域分析核心工具 |
| **ADSR** | Attack-Decay-Sustain-Release 包络 |

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **音乐 + 编程** | CS476A 是完美交叉点 |
| **创意编程入门** | 声音是最即时的反馈 |
| **AI 生成方向** | 音乐生成的基础 |
| **电子音乐制作** | 从代码到 Ableton |

---

## 🚀 扩展方向

1. 学习 ChucK 或 Sonic Pi 进行 Live Coding
2. 探索 Web Audio API（浏览器音乐编程）
3. 尝试 MusicVAE / Music Transformer（AI 作曲）
4. 听 Stanford Laptop Ensemble 演出

---

**对应代码**: `supplementary/undergrad_projects.py::cs476a_demo`

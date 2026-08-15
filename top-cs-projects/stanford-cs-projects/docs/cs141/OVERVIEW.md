# CS141: Sports and Data

> Stanford University, Autumn 2026
> 领域: 体育数据分析 / 统计建模
> Prerequisites: 无正式先修（推荐 CS109 或基础统计）
> Units: 3-4
> Difficulty: ⭐⭐

---

## 📚 定位

用数据科学方法分析体育数据——从球员评分到比赛策略，连接统计学与体育产业。

---

## 🎯 学习目标

- 掌握体育数据采集、清洗与可视化方法
- 理解高级统计指标（PER、WAR、Elo、xG）的设计原理
- 能用回归 / 分类模型预测比赛结果与球员表现
- 批判性评估分析结论（相关 vs 因果）

---

## 📅 核心模块

### Module 1: 数据采集与探索
- 公开数据源（Basketball Reference、StatsBomb）
- Play-by-play 数据结构解析
- 探索性分析（EDA）与可视化

### Module 2: 球员评分体系
- 传统统计 vs 高级指标
- PER（Player Efficiency Rating）计算
- Elo 评级系统与动态排名

### Module 3: 预测建模
- 回归：得分 / 胜率预测
- 分类：胜负 / 季后赛晋级概率
- 时间序列：球员状态追踪

### Module 4: 策略分析
- 期望值（Expected Goals, xG）
- 投篮选择优化（NBA 三分革命）
- 博弈论与比赛策略

### Module 5: 因果推断
- A/B 测试在体育中的局限
- 差分法（DiD）与工具变量
- "热手效应"真伪

---

## 💻 项目代码

📁 `supplementary/undergrad_projects.py::cs141_demo`

**实现内容**:
1. ✅ 模拟 NBA 球员数据（Curry / LeBron / Giannis）
2. ✅ 简化版 PER 计算（得分 + 篮板 + 助服加权）
3. ✅ 球员表现排名与可视化输出

**运行**:
```bash
cd supplementary
python3 undergrad_projects.py
```

**输出示例**:
```
球员表现 (按 PER 排序):
  Giannis   : 29分 11板 5助 PER=50.7
  LeBron    : 27分 8板 8助 PER=49.9
  Curry     : 30分 5板 6助 PER=47.0
```

---

## 📊 关键概念

| 概念 | 说明 |
|------|------|
| **PER** | Player Efficiency Rating，综合球员效率 |
| **xG** | Expected Goals，射门期望进球数 |
| **Elo** | 动态实力评级，象棋 / 足球常用 |
| **Plus-Minus** | 球员在场时球队净胜分 |
| **热手效应** | 连续命中的统计学争论 |

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **体育爱好者** | 用数据验证直觉 |
| **数据科学入门** | 真实数据集练手 |
| **量化分析方向** | 体育博彩 / 前台分析 |
| **通识选修** | 有趣的统计应用 |

---

## 🚀 扩展方向

1. 接入真实 NBA API 进行赛季级分析
2. 用机器学习预测 March Madness 晋级
3. 探索 Soccer Analytics（xG 模型）
4. 阅读 *The Undoing Project*（行为经济学与体育）

---

**对应代码**: `supplementary/undergrad_projects.py::cs141_demo`

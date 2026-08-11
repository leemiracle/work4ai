# CS377G: Designing Serious Games

> Stanford University, Autumn 2026
> 领域: 游戏设计 / 教育科技
> Prerequisites: 无硬性先修，推荐 HCI 或设计基础
> Units: 3-4
> Difficulty: ⭐⭐⭐

---

## 📚 定位

设计有目的的游戏——教育、健康、社会变革。用 MDA 框架连接游戏机制与学习目标。

---

## 🎯 学习目标

- 掌握游戏设计理论（MDA 框架、心流理论）
- 理解"严肃游戏"的设计原则
- 能将学习目标映射到游戏机制
- 通过迭代测试验证教育效果

---

## 📅 核心模块

### Module 1: 游戏设计基础
- MDA 框架：Mechanics / Dynamics / Aesthetics
- 游戏元素：规则、目标、反馈
- 心流理论（Csikszentmihalyi）

### Module 2: 严肃游戏理论
- 娱乐 vs 教育 vs 说服
- 内在动机 vs 外在动机
- 游戏化（Gamification）的陷阱

### Module 3: 学习游戏设计
- Bloom 分类法与游戏目标对齐
- 难度曲线与技能成长
- 失败的安全空间

### Module 4: 原型与迭代
- 纸面原型（Paper Prototyping）
- 快速数字原型
- Playtest 与用户研究

### Module 5: 评估与影响
- 学习效果评估方法
- 行为改变的测量
- 伦理：操纵 vs 赋能

---

## 💻 项目代码

📁 `supplementary/undergrad_projects.py::cs377g_demo`

**实现内容**:
1. ✅ MDA 框架完整展示（以代数学习游戏为例）
2. ✅ Mechanics → Dynamics → Aesthetics 映射
3. ✅ 学习目标与游戏机制对齐
4. ✅ 玩家学习曲线模拟（10 关，技能随成功递增）

**运行**:
```bash
cd supplementary
python3 undergrad_projects.py
```

**输出示例**:
```
Mechanics: ['quiz_question', 'score_point', 'lose_life', 'level_up']
Dynamics: ['player_learns', 'compete_with_time', 'review_wrong_answers']
Aesthetics: ['challenge', 'discovery', 'sensation']
Learning_Objective: 掌握基础代数

玩家学习曲线:
  Lv0: ██████████ 0.30 ✓
  Lv1: ███████████ 0.35 ✗
  ...
  Lv9: ████████████████████████ 0.75 ✓
```

---

## 📊 关键概念/论文

| 概念 | 说明 |
|------|------|
| **MDA 框架** | Mechanics-Dynamics-Aesthetics |
| **心流** | 技能与难度的平衡区 |
| **严肃游戏** | 有教育/训练/说服目的的游戏 |
| **游戏化** | 非游戏场景引入游戏元素 |

### 关键参考
1. Hunicke et al. 2004 — MDA 框架
2. Gee 2007 — *What Video Games Have to Teach Us*
3. McGonigal 2011 — *Reality is Broken*

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **教育科技方向** | 游戏化学习设计 |
| **游戏设计师** | 超越娱乐的设计思维 |
| **HCI / 交互设计** | 游戏是最好的交互案例 |
| **公益 / 社会创新** | 用游戏推动改变 |

---

## 🚀 扩展方向

1. 设计一个关于 AI 伦理的教育游戏
2. 学习 Twine（叙事游戏工具）
3. 探索 Duolingo / Khan Academy 的游戏化设计
4. 阅读 *The Art of Game Design* (Schell)

---

**对应代码**: `supplementary/undergrad_projects.py::cs377g_demo`

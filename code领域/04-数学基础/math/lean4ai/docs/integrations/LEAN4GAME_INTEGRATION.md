# Lean4Game 集成指南

## 项目概述

**Lean4Game** 是一个游戏化的 Lean4 学习平台，让定理证明变得有趣和互动。

| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/leanprover-community/lean4game |
| **在线版** | https://adam.math.hhu.de |
| **Stars** | 428 |
| **Forks** | 79 |
| **语言** | TypeScript/React |
| **许可证** | GPL-3.0 |

---

## 核心游戏

### 可玩游戏列表

| 游戏 | 描述 | 难度 | 状态 |
|------|------|------|------|
| **NNG4** | Natural Number Game | 初级 | ✅ 可玩 |
| **Invincible** | 线性逻辑游戏 | 中级 | ✅ 可玩 |
| **Harvey Mudd** | 哈维穆德教程 | 初级 | ✅ 可玩 |
| **Functional Linear Algebra** | 函数式线性代数 | 高级 | ✅ 可玩 |
| **Robo** | 机器人导航逻辑 | 初级 | ✅ 可玩 |

---

## 游戏架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Lean4Game 架构                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  前端 (React)                        │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │ 世界地图  │  │ 关卡编辑器│  │ 成就系统  │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │ 代码编辑器│  │ 证明显示  │  │ 提示系统  │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  后端 (Node.js)                      │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │ 游戏逻辑  │  │ 进度存储  │  │ 用户管理  │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  Lean4 服务器                        │   │
│   │  ┌──────────────────────────────────────────────┐   │   │
│   │  │  Lean4 进程 (lake env lean --server)          │   │   │
│   │  │  - 类型检查                                   │   │   │
│   │  │  - 策略执行                                   │   │   │
│   │  │  - 目标显示                                   │   │   │
│   │  └──────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Natural Number Game (NNG4)

### 游戏结构

```
NNG4/
├── World 1: Tutorial
│   ├── Level 1: 0 = 0
│   ├── Level 2: rfl
│   └── Level 3: 定义
│
├── World 2: Addition
│   ├── Level 1: 0 + n = n
│   ├── Level 2: n + 0 = n
│   ├── Level 3: succ(n) + m = succ(n + m)
│   └── ...
│
├── World 3: Multiplication
│   └── ...
│
└── World 4: Power
    └── ...
```

### 示例关卡

```lean
-- World 1, Level 1: 第一个证明
-- 目标: 证明 0 = 0

example : 0 = 0 := by
  rfl

-- World 2, Level 1: 加法零元
-- 目标: 证明 0 + n = n

example (n : Nat) : 0 + n = n := by
  rfl

-- World 2, Level 2: 加法零元右
-- 目标: 证明 n + 0 = n

example (n : Nat) : n + 0 = n := by
  induction n with
  | zero => rfl
  | succ n ih => 
    simp [Nat.add_succ]
    rw [ih]

-- World 2, Level 3: 加法结合律
-- 目标: 证明 (a + b) + c = a + (b + c)

example (a b c : Nat) : (a + b) + c = a + (b + c) := by
  induction c with
  | zero => 
    simp [Nat.add_zero]
  | succ c ih =>
    simp [Nat.add_succ]
    rw [ih]
```

---

## 创建自定义游戏

### 1. 游戏定义文件

```lean
-- Game.lean

import GameServer.Commands

Game "MyLean4AIGame"
Title "Lean4AI 游戏化学习"
Introduction "
欢迎来到 Lean4AI 游戏世界！
在这里，你将学习如何使用 Lean4 进行形式化验证。
"

-- 定义世界
World "Project"
Title "项目管理验证"

Level 1
Title "项目定义"

Introduction "
一个项目需要名称、预算和截止日期。
让我们定义一个有效的项目结构。
"

Statement (name : String) (budget : Nat) (deadline : Nat) :
  name ≠ "" → budget > 0 → True := by
  intro _ _
  trivial

Hint "使用 `intro` 引入假设"

Conclusion "太棒了！你已经学会了定义基本的项目约束。"
```

### 2. 关卡模板

```lean
-- Levels/ProjectManagement.lean

import GameServer.Commands

Game "Lean4AI"
Title "Lean4AI 游戏世界"

World "Project"
Title "项目管理"

-- Level 1: 有效项目
Level 1
Title "有效项目定义"

Statement project_valid (p : Project) :
  p.name ≠ "" ∧ p.budget ≥ 0 := by
  constructor
  · exact p.name_ne_empty
  · native_decide

-- Level 2: 任务管理
Level 2
Title "任务约束"

Statement task_constraint (t : Task) :
  t.points > 0 ∧ t.points ≤ 100 := by
  constructor
  · exact t.points_positive
  · exact t.points_bounded

-- Level 3: Sprint 容量
Level 3
Title "Sprint 容量验证"

Statement sprint_capacity (s : Sprint) (capacity : Nat) :
  s.totalPoints ≤ capacity → s.isValid := by
  intro h
  exact Sprint.mk_valid h

-- Level 4: 风险评估
Level 4
Title "风险分数验证"

Statement risk_bounded (r : Risk) :
  0 ≤ r.score ∧ r.score ≤ 1 := by
  constructor <;> native_decide

-- Level 5: 资源分配
Level 5
Title "资源分配正确性"

Statement resource_allocation (p : Project) (resources : List Resource) :
  resources.all (·.available) → p.canAllocate resources := by
  intro h
  exact Project.can_allocate h
```

### 3. 自定义命令

```lean
-- Commands.lean

import GameServer.Commands

/-- 显示项目状态 -/
def Project.status (p : Project) : String :=
  s!"Project: {p.name}\nBudget: {p.budget}\nSpent: {p.spent}"

/-- 检查项目健康度 -/
def Project.healthScore (p : Project) : Float :=
  if p.budget = 0 then 0
  else 1 - (p.spent.toFloat / p.budget.toFloat)

/-- 计算风险等级 -/
def Risk.level (r : Risk) : String :=
  if r.score < 0.3 then "Low"
  else if r.score < 0.7 then "Medium"
  else "High"

-- 游戏命令
CommandDoc project_status "显示项目当前状态"
CommandDoc health_check "检查项目健康度"
CommandDoc risk_level "计算风险等级"
```

---

## 与 Lean4AI 集成

### 1. 游戏桥接器

```python
# lean4game_bridge.py

import requests
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class GameState:
    game_id: str
    world: str
    level: int
    completed: bool
    code: str
    goals: List[str]
    messages: List[str]

@dataclass
class GameWorld:
    name: str
    title: str
    levels: int
    completed: int

class Lean4GameBridge:
    """
    Lean4Game 与 Lean4AI 的桥接器
    """
    
    def __init__(self, server_url: str = "https://adam.math.hhu.de"):
        self.server_url = server_url
        self.session: Optional[requests.Session] = None
    
    def load_game(self, game_id: str) -> dict:
        """
        加载游戏
        """
        response = requests.get(f"{self.server_url}/api/{game_id}/load")
        return response.json()
    
    def get_worlds(self, game_id: str) -> List[GameWorld]:
        """
        获取所有世界
        """
        response = requests.get(f"{self.server_url}/api/{game_id}/worlds")
        worlds_data = response.json()
        
        return [
            GameWorld(
                name=w["name"],
                title=w["title"],
                levels=w["levels"],
                completed=w.get("completed", 0)
            )
            for w in worlds_data
        ]
    
    def get_level(self, game_id: str, world: str, level: int) -> dict:
        """
        获取关卡信息
        """
        response = requests.get(
            f"{self.server_url}/api/{game_id}/{world}/{level}"
        )
        return response.json()
    
    def submit_solution(self, 
                        game_id: str, 
                        world: str, 
                        level: int, 
                        code: str) -> GameState:
        """
        提交解决方案
        """
        response = requests.post(
            f"{self.server_url}/api/{game_id}/submit",
            json={
                "world": world,
                "level": level,
                "code": code
            }
        )
        data = response.json()
        
        return GameState(
            game_id=game_id,
            world=world,
            level=level,
            completed=data.get("completed", False),
            code=code,
            goals=data.get("goals", []),
            messages=data.get("messages", [])
        )
    
    def get_hint(self, game_id: str, world: str, level: int) -> Optional[str]:
        """
        获取提示
        """
        response = requests.get(
            f"{self.server_url}/api/{game_id}/{world}/{level}/hint"
        )
        data = response.json()
        return data.get("hint")

class Lean4AIGameCreator:
    """
    创建 Lean4AI 主题游戏
    """
    
    def __init__(self, output_path: str = "./games"):
        self.output_path = output_path
    
    def create_project_management_game(self) -> str:
        """
        创建项目管理验证游戏
        """
        game_def = """
import GameServer.Commands

Game "Lean4AI-PM"
Title "项目管理大师"
Introduction "
欢迎来到项目管理验证世界！
学习如何用 Lean4 验证项目管理实践。
"

World "Basics"
Title "基础验证"

Level 1
Title "定义项目"
Introduction "
每个项目都有基本属性。让我们验证它们。
"

Structure Project where
  name : String
  budget : Nat
  deriving Repr

Statement valid_project (p : Project) :
  p.name ≠ "" := by
  intro h
  exact p.name_nonempty

Level 2
Title "预算约束"

Statement budget_constraint (p : Project) :
  p.budget ≥ 0 := by
  native_decide
"""
        return game_def
    
    def create_agile_game(self) -> str:
        """
        创建敏捷实践游戏
        """
        game_def = """
import GameServer.Commands

Game "Lean4AI-Agile"
Title "敏捷证明者"
Introduction "
探索敏捷开发的形式化验证！
"

World "Scrum"
Title "Scrum 验证"

Level 1
Title "Sprint 容量"

Statement sprint_capacity (points : Nat) (capacity : Nat) :
  points ≤ capacity → True := by
  intro _
  trivial

Level 2
Title "故事点约束"

Statement story_points (points : Nat) :
  points > 0 ∧ points ≤ 100 := by
  sorry
"""
        return game_def
    
    def create_ai_ethics_game(self) -> str:
        """
        创建 AI 伦理验证游戏
        """
        game_def = """
import GameServer.Commands

Game "Lean4AI-Ethics"
Title "AI 伦理验证"
Introduction "
学习如何形式化验证 AI 系统的伦理约束。
"

World "Fairness"
Title "公平性验证"

Level 1
Title "非歧视性"

Statement non_discrimination (scores : List Float) :
  scores.all (fun s => s ≥ 0 ∧ s ≤ 1) → True := by
  intro _
  trivial

Level 2
Title "透明度"

Statement transparency (model : AIModel) :
  model.interpretable = true → model.trustworthy = true := by
  intro h
  exact AIModel.trustworthy_if_interpretable h
"""
        return game_def

class GameProgressTracker:
    """
    游戏进度追踪器
    """
    
    def __init__(self):
        self.progress: Dict[str, Dict[str, List[int]]] = {}
    
    def complete_level(self, game_id: str, world: str, level: int):
        """
        标记关卡完成
        """
        if game_id not in self.progress:
            self.progress[game_id] = {}
        if world not in self.progress[game_id]:
            self.progress[game_id][world] = []
        if level not in self.progress[game_id][world]:
            self.progress[game_id][world].append(level)
    
    def get_completion_rate(self, game_id: str) -> float:
        """
        获取完成率
        """
        if game_id not in self.progress:
            return 0.0
        
        total_levels = self._count_total_levels(game_id)
        completed = sum(len(levels) for levels in self.progress[game_id].values())
        
        return completed / total_levels if total_levels > 0 else 0.0
    
    def _count_total_levels(self, game_id: str) -> int:
        # 这应该从游戏定义中获取
        game_totals = {
            "nng4": 100,
            "lean4ai-pm": 20,
            "lean4ai-agile": 15,
            "lean4ai-ethics": 10
        }
        return game_totals.get(game_id, 0)
    
    def export_progress(self) -> dict:
        """
        导出进度
        """
        return {
            "progress": self.progress,
            "summary": {
                game: {
                    "completed_levels": sum(len(l) for l in worlds.values()),
                    "worlds_completed": sum(1 for l in worlds.values() if len(l) > 0)
                }
                for game, worlds in self.progress.items()
            }
        }
```

### 2. 集成到 Leantime

```python
# leantime_game_integration.py

from lean4game_bridge import Lean4GameBridge, GameProgressTracker
from typing import Dict, List

class LeantimeGameIntegration:
    """
    将 Lean4Game 集成到 Leantime 项目管理
    """
    
    def __init__(self):
        self.game = Lean4GameBridge()
        self.tracker = GameProgressTracker()
    
    def project_to_game(self, project_id: str) -> str:
        """
        将项目转换为游戏关卡
        """
        # 根据项目特性生成关卡
        return f"lean4ai-project-{project_id}"
    
    def task_to_level(self, task_id: str, task_type: str) -> dict:
        """
        将任务转换为游戏关卡
        """
        level_mapping = {
            "verification": {
                "world": "Proofs",
                "level": 1,
                "title": "验证任务"
            },
            "design": {
                "world": "Structures",
                "level": 1,
                "title": "设计结构"
            },
            "implementation": {
                "world": "Code",
                "level": 1,
                "title": "实现代码"
            }
        }
        return level_mapping.get(task_type, level_mapping["verification"])
    
    def award_xp_for_completion(self, 
                                 user_id: str, 
                                 task_complexity: int) -> int:
        """
        完成任务时奖励经验值
        """
        base_xp = 100
        bonus = task_complexity * 10
        return base_xp + bonus
    
    def sync_progress_to_project(self, 
                                  project_id: str, 
                                  game_progress: dict) -> dict:
        """
        同步游戏进度到项目进度
        """
        return {
            "project_id": project_id,
            "completed_levels": game_progress["completed_levels"],
            "total_levels": game_progress["total_levels"],
            "percentage": (game_progress["completed_levels"] / 
                          game_progress["total_levels"]) * 100,
            "achievements": game_progress.get("achievements", [])
        }
    
    def generate_leaderboard(self, 
                              project_id: str) -> List[Dict]:
        """
        生成项目排行榜
        """
        # 示例排行榜
        return [
            {"rank": 1, "user": "Alice", "xp": 2500, "levels": 45},
            {"rank": 2, "user": "Bob", "xp": 2100, "levels": 38},
            {"rank": 3, "user": "Charlie", "xp": 1800, "levels": 32},
        ]
```

---

## 部署指南

### 1. 本地部署

```bash
# 克隆仓库
git clone https://github.com/leanprover-community/lean4game.git
cd lean4game

# 安装依赖
npm install

# 启动开发服务器
npm start

# 访问
# http://localhost:3000
```

### 2. 创建自定义游戏

```bash
# 创建游戏目录
mkdir -p games/lean4ai-game

# 创建游戏定义
cat > games/lean4ai-game/Game.lean << 'EOF'
import GameServer.Commands

Game "Lean4AI"
Title "Lean4AI 形式化验证游戏"
Introduction "
欢迎！学习形式化验证项目管理。
"
EOF

# 构建
lake build

# 在服务器上注册
# 编辑 server/src/games.json
```

### 3. Docker 部署

```dockerfile
# Dockerfile
FROM node:18

WORKDIR /app
COPY . .

RUN npm install
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

```bash
docker build -t lean4game .
docker run -p 3000:3000 lean4game
```

---

## 游戏化学习路径

```
┌─────────────────────────────────────────────────────────────┐
│                  Lean4AI 游戏化学习路径                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   初级 (0-500 XP)                                          │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  NNG4 World 1-2                                     │   │
│   │  ├── 加法世界                                        │   │
│   │  ├── 乘法世界                                        │   │
│   │  └── 基础证明策略                                    │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   中级 (500-2000 XP)                                       │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Lean4AI-PM (项目管理)                              │   │
│   │  ├── 项目验证                                        │   │
│   │  ├── 任务约束                                        │   │
│   │  └── Sprint 验证                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   高级 (2000-5000 XP)                                      │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Lean4AI-Agile (敏捷)                               │   │
│   │  ├── Scrum 验证                                      │   │
│   │  ├── Kanban 约束                                     │   │
│   │  └── 回顾分析                                        │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   专家 (5000+ XP)                                          │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Lean4AI-Ethics (AI伦理)                            │   │
│   │  ├── 公平性验证                                      │   │
│   │  ├── 透明度证明                                      │   │
│   │  └── 可解释性                                        │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 成就系统

```python
# achievements.py

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    xp_reward: int
    condition: callable

ACHIEVEMENTS = [
    Achievement(
        id="first_proof",
        name="证明学徒",
        description="完成你的第一个证明",
        icon="🎓",
        xp_reward=100,
        condition=lambda p: p.total_proofs >= 1
    ),
    Achievement(
        id="project_validator",
        name="项目验证者",
        description="验证10个项目约束",
        icon="✅",
        xp_reward=500,
        condition=lambda p: p.project_validations >= 10
    ),
    Achievement(
        id="agile_master",
        name="敏捷大师",
        description="完成所有敏捷世界关卡",
        icon="🏃",
        xp_reward=1000,
        condition=lambda p: p.agile_world_complete
    ),
    Achievement(
        id="theorem_creator",
        name="定理创造者",
        description="创建5个自定义定理",
        icon="💡",
        xp_reward=750,
        condition=lambda p: p.custom_theorems >= 5
    ),
    Achievement(
        id="lean_champion",
        name="Lean 冠军",
        description="达到 5000 XP",
        icon="🏆",
        xp_reward=2000,
        condition=lambda p: p.xp >= 5000
    ),
]

class AchievementSystem:
    def __init__(self):
        self.unlocked: List[str] = []
    
    def check_achievements(self, player_stats: dict) -> List[Achievement]:
        """
        检查新解锁的成就
        """
        new_unlocks = []
        for ach in ACHIEVEMENTS:
            if ach.id not in self.unlocked:
                if ach.condition(player_stats):
                    self.unlocked.append(ach.id)
                    new_unlocks.append(ach)
        return new_unlocks
    
    def get_progress(self, achievement_id: str, player_stats: dict) -> float:
        """
        获取成就进度
        """
        ach = next((a for a in ACHIEVEMENTS if a.id == achievement_id), None)
        if ach is None:
            return 0.0
        # 简化实现
        return 1.0 if ach.condition(player_stats) else 0.0
```

---

## 项目统计更新

| 指标 | 更新前 | 更新后 |
|------|--------|--------|
| 集成项目数 | 14 | 15 |
| 可玩游戏数 | - | 5+ |
| Stars 总和 | ~16,700 | ~17,100 |
| 游戏化关卡 | - | 200+ |

---

## 快速开始

```bash
# 在线游玩
open https://adam.math.hhu.de

# 本地部署
git clone https://github.com/leanprover-community/lean4game.git
cd lean4game && npm install && npm start

# 创建自定义游戏
cd lean4ai/games
lake init lean4ai-game
# 编辑 Game.lean
lake build
```

---

**版本**: 8.0.0 (Fifteen-in-One)
**更新日期**: 2025-03-25

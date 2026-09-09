# LeanProject 集成指南

## 项目概述

**LeanProject** 是一个用于蓝图驱动 (Blueprint-driven) 形式化项目的 Lean4 模板，帮助组织和管理大型形式化数学项目。

| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/leanprover-community/LeanProject |
| **Stars** | 103 |
| **Forks** | 15 |
| **语言** | Lean 4 |
| **许可证** | Apache 2.0 |
| **描述** | A template for blueprint-driven formalization projects in Lean |
| **类型** | 模板仓库 |

### 主题标签

- formal-mathematics, formalisation-mathematics, formalised-mathematics
- lean-blueprint, lean-theorem-prover, lean4, leanblueprint
- mathematical-programming, mathematics, proof-assistant, theorem-proving

---

## 蓝图驱动方法

### 什么是蓝图驱动？

```
┌─────────────────────────────────────────────────────────────┐
│                  蓝图驱动形式化方法                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   传统方法:                                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  数学证明 → 直接编写 Lean 代码 → 调试 → 完成        │   │
│   │                                                     │   │
│   │  问题:                                              │   │
│   │  • 缺乏全局规划                                     │   │
│   │  • 难以追踪进度                                     │   │
│   │  • 协作困难                                         │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   蓝图驱动方法:                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                     │   │
│   │  1. 创建蓝图 (Blueprint)                            │   │
│   │     ├── LaTeX 文档描述数学结构                      │   │
│   │     ├── 定义依赖关系                                │   │
│   │     └── 自动生成依赖图                              │   │
│   │                                                     │   │
│   │  2. 声明 Lean 命名                                  │   │
│   │     ├── 将蓝图条目映射到 Lean 名称                  │   │
│   │     └── 自动生成骨架代码                            │   │
│   │                                                     │   │
│   │  3. 实现证明                                        │   │
│   │     ├── 按依赖顺序工作                              │   │
│   │     ├── 自动追踪进度                                │   │
│   │     └── 可视化完成状态                              │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   优势:                                                     │
│   • 清晰的项目结构                                         │
│   • 自动依赖管理                                           │
│   • 进度可视化                                             │
│   • 支持大型协作                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 蓝图结构

```
LeanProject/
├── blueprint/
│   └── src/
│       ├── content/
│       │   ├── chapter1.tex    # 第一章
│       │   ├── chapter2.tex    # 第二章
│       │   └── ...
│       ├── print.tex           # 打印版本
│       └── web.tex             # Web 版本
│   │
├── project/
│   ├── lakefile.lean           # Lake 配置
│   ├── lean-toolchain          # Lean 版本
│   │
│   ├── LeanProject/
│   │   ├── Basic.lean          # 基础定义
│   │   ├── Chapter1.lean       # 第一章实现
│   │   └── ...
│   │
│   └── LeanProject.lean        # 主导入文件
│
├── home/                       # 项目主页
│   └── index.html
│
├── blueprint.pdf               # 生成的蓝图 PDF
└── docs/                       # 文档

```

---

## 使用指南

### 1. 从模板创建项目

```bash
# 方法1: 使用 GitHub 模板
# 访问 https://github.com/leanprover-community/LeanProject
# 点击 "Use this template"

# 方法2: 克隆并修改
cd /mnt/c/workspace/math/lean4ai
git clone https://github.com/leanprover-community/LeanProject.git my-project
cd my-project
rm -rf .git
git init
```

### 2. 蓝图编写

```latex
% blueprint/src/content/chapter1.tex

\documentclass{report}
\usepackage{leanblueprint}

\chapter{基础定义}

\section{项目结构}

\begin{definition}[Project]
\label{def:project}
一个项目由以下组件组成：
\begin{itemize}
  \item 名称
  \item 预算
  \item 任务列表
  \item 资源分配
\end{itemize}
\end{definition}

\begin{lemma}[项目预算约束]
\label{lem:budget-constraint}
\uses{def:project}
对于任意有效项目 $p$，有 $\text{spent}(p) \leq \text{budget}(p)$。
\end{lemma}

\begin{theorem}[项目有效性]
\label{thm:project-valid}
\uses{lem:budget-constraint}
如果所有任务都满足约束且资源分配合理，则项目是有效的。
\end{theorem}

\begin{proof}
设 $p$ 为满足条件的项目。
由引理~\ref{lem:budget-constraint}，预算约束成立。
因此，$p$ 是有效的。
\end{proof}
```

### 3. 声明 Lean 名称

```lean
-- project/LeanProject/Definitions.lean

/-
  蓝图条目映射
  
  LaTeX 标签              → Lean 名称
  ─────────────────────────────────────
  def:project             → Project
  lem:budget-constraint   → Project.budget_constraint
  thm:project-valid       → Project.is_valid
-/

/-- 蓝图 Definition 1.1: 项目 -/
structure Project where
  name : String
  budget : Nat
  spent : Nat
  tasks : List Task
  resources : List Resource

/-- 蓝图 Lemma 1.2: 预算约束 -/
theorem Project.budget_constraint (p : Project) (h : p.isValid) :
    p.spent ≤ p.budget := by
  exact h.spending_valid

/-- 蓝图 Theorem 1.3: 项目有效性 -/
theorem Project.is_valid (p : Project) 
    (h1 : ∀ t ∈ p.tasks, t.isValid)
    (h2 : p.resources.all (·.available)) :
    p.isValid := by
  exact Project.valid_iff.mpr ⟨h1, h2⟩
```

### 4. 依赖图生成

```bash
# 安装蓝图工具
pip install leanblueprint

# 生成依赖图
leanblueprint deps

# 输出示例:
# def:project → lem:budget-constraint → thm:project-valid
```

---

## LeanProject 模板结构

### lakefile.lean

```lean
import Lake
open Lake DSL

package «my-project» where
  version := v"0.1.0"

lean_lib «LeanProject» where
  globs := #[.one `LeanProject]

@[default_target]
lean_exe «leanproject» where
  root := `Main

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "master"

require batteries from git
  "https://github.com/leanprover-community/batteries" @ "main"
```

### 项目配置

```yaml
# project.yaml
name: my-project
version: "0.1.0"
description: "My blueprint-driven Lean4 project"

authors:
  - Your Name <your@email.com>

dependencies:
  mathlib: "master"
  batteries: "main"

blueprint:
  source: "blueprint/src"
  output: "docs/blueprint"
  
structure:
  - name: "Basic"
    path: "LeanProject/Basic.lean"
  - name: "Chapter1"
    path: "LeanProject/Chapter1.lean"
    depends_on: ["Basic"]
```

---

## 与 Lean4AI 集成

### 1. 项目管理蓝图

```latex
% lean4ai-blueprint/src/content/project-management.tex

\chapter{项目管理验证}

\section{项目结构}

\begin{definition}[Lean4AI Project]
\label{def:lean4ai-project}
一个 Lean4AI 项目包含：
\begin{itemize}
  \item \lean{Project}: 项目结构
  \item \lean{Task}: 任务定义
  \item \lean{Sprint}: Sprint 管理
  \item \lean{Risk}: 风险评估
  \item \lean{Resource}: 资源管理
\end{itemize}
\end{definition}

\section{验证规则}

\begin{lemma}[预算有效性]
\label{lem:budget-valid}
\uses{def:lean4ai-project}
对于任意项目 $p$：
$$ \text{spent}(p) \leq \text{budget}(p) $$
\end{lemma}

\begin{lemma}[Sprint 容量]
\label{lem:sprint-capacity}
\uses{def:lean4ai-project}
对于任意 Sprint $s$ 和容量 $c$：
$$ \text{totalPoints}(s) \leq c \implies \text{isValid}(s) $$
\end{lemma}

\begin{lemma}[风险分数]
\label{lem:risk-score}
\uses{def:lean4ai-project}
对于任意风险 $r$：
$$ 0 \leq \text{score}(r) \leq 1 $$
\end{lemma}

\begin{theorem}[项目健康度]
\label{thm:project-health}
\uses{lem:budget-valid, lem:sprint-capacity, lem:risk-score}
项目 $p$ 是健康的，当且仅当：
\begin{itemize}
  \item 预算有效
  \item 所有 Sprint 有效
  \item 所有风险分数有效
\end{itemize}
\end{theorem}
```

### 2. Lean 实现骨架

```lean
-- lean4ai-project/LeanProject/ProjectManagement.lean

/-
  蓝图映射:
  - def:lean4ai-project → ProjectManagement.Project
  - lem:budget-valid → Project.budget_valid
  - lem:sprint-capacity → Sprint.capacity_valid
  - lem:risk-score → Risk.score_valid
  - thm:project-health → Project.is_healthy
-/

namespace LeanProject

/-- 蓝图 Definition: 项目 -/
structure Project where
  name : String
  budget : Nat
  spent : Nat
  sprints : List Sprint
  risks : List Risk
  deriving Repr

/-- 蓝图 Lemma: 预算有效性 -/
theorem Project.budget_valid (p : Project) (h : p.isValid) :
    p.spent ≤ p.budget := by
  exact h.budget_ok

/-- 蓝图 Lemma: Sprint 容量 -/
theorem Sprint.capacity_valid (s : Sprint) (capacity : Nat) 
    (h : s.totalPoints ≤ capacity) :
    s.isValid := by
  exact Sprint.mk_valid h

/-- 蓝图 Lemma: 风险分数 -/
theorem Risk.score_valid (r : Risk) :
    0 ≤ r.score ∧ r.score ≤ 1 := by
  constructor <;> native_decide

/-- 蓝图 Theorem: 项目健康度 -/
theorem Project.is_healthy (p : Project) 
    (h1 : p.budget ≤ p.budget)  -- 预算有效
    (h2 : ∀ s ∈ p.sprints, s.isValid)  -- Sprint 有效
    (h3 : ∀ r ∈ p.risks, 0 ≤ r.score ∧ r.score ≤ 1) :  -- 风险有效
    p.isHealthy := by
  exact Project.healthy_iff.mpr ⟨h1, h2, h3⟩

end LeanProject
```

### 3. 进度追踪

```python
# blueprint_tracker.py

import os
import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class ProofStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    STUCK = "stuck"

@dataclass
class BlueprintEntry:
    """蓝图条目"""
    label: str
    kind: str  # "definition", "lemma", "theorem"
    lean_name: Optional[str]
    status: ProofStatus
    dependencies: List[str]
    file_path: Optional[str]

class BlueprintTracker:
    """
    蓝图进度追踪器
    """
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.entries: Dict[str, BlueprintEntry] = {}
    
    def parse_blueprint(self, blueprint_path: str) -> List[BlueprintEntry]:
        """
        解析蓝图 LaTeX 文件
        """
        entries = []
        
        with open(blueprint_path, 'r') as f:
            content = f.read()
        
        # 解析定义
        def_pattern = r'\\begin\{definition\}(?:\[.*?\])?\s*\\label\{(def:[^}]+)\}'
        for match in re.finditer(def_pattern, content):
            entries.append(BlueprintEntry(
                label=match.group(1),
                kind="definition",
                lean_name=None,
                status=ProofStatus.NOT_STARTED,
                dependencies=[],
                file_path=None
            ))
        
        # 解析引理
        lemma_pattern = r'\\begin\{lemma\}(?:\[.*?\])?\s*\\label\{(lem:[^}]+)\}'
        for match in re.finditer(lemma_pattern, content):
            label = match.group(1)
            deps = self._extract_uses(content, label)
            entries.append(BlueprintEntry(
                label=label,
                kind="lemma",
                lean_name=None,
                status=ProofStatus.NOT_STARTED,
                dependencies=deps,
                file_path=None
            ))
        
        # 解析定理
        theorem_pattern = r'\\begin\{theorem\}(?:\[.*?\])?\s*\\label\{(thm:[^}]+)\}'
        for match in re.finditer(theorem_pattern, content):
            label = match.group(1)
            deps = self._extract_uses(content, label)
            entries.append(BlueprintEntry(
                label=label,
                kind="theorem",
                lean_name=None,
                status=ProofStatus.NOT_STARTED,
                dependencies=deps,
                file_path=None
            ))
        
        return entries
    
    def _extract_uses(self, content: str, label: str) -> List[str]:
        """提取依赖"""
        # 查找 \uses{label} 后面的标签
        pattern = rf'\\label\{{{re.escape(label)}\}}.*?\\uses\{{([^}}]+)\}}'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return [t.strip() for t in match.group(1).split(',')]
        return []
    
    def scan_lean_files(self) -> Dict[str, ProofStatus]:
        """
        扫描 Lean 文件获取证明状态
        """
        status = {}
        
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.lean'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # 检查 sorry
                    if 'sorry' in content:
                        status[file_path] = ProofStatus.IN_PROGRESS
                    else:
                        status[file_path] = ProofStatus.COMPLETE
        
        return status
    
    def generate_progress_report(self) -> dict:
        """
        生成进度报告
        """
        entries = list(self.entries.values())
        
        return {
            "total": len(entries),
            "by_status": {
                "not_started": sum(1 for e in entries if e.status == ProofStatus.NOT_STARTED),
                "in_progress": sum(1 for e in entries if e.status == ProofStatus.IN_PROGRESS),
                "complete": sum(1 for e in entries if e.status == ProofStatus.COMPLETE),
                "stuck": sum(1 for e in entries if e.status == ProofStatus.STUCK),
            },
            "completion_rate": sum(1 for e in entries if e.status == ProofStatus.COMPLETE) / len(entries) if entries else 0,
            "entries": [
                {
                    "label": e.label,
                    "kind": e.kind,
                    "status": e.status.value,
                    "dependencies": e.dependencies
                }
                for e in entries
            ]
        }
    
    def visualize_dependency_graph(self) -> str:
        """
        生成依赖图 (Mermaid 格式)
        """
        lines = ["graph TD"]
        
        for label, entry in self.entries.items():
            # 添加节点
            color = {
                ProofStatus.NOT_STARTED: "#ff9999",
                ProofStatus.IN_PROGRESS: "#ffff99",
                ProofStatus.COMPLETE: "#99ff99",
                ProofStatus.STUCK: "#ff99ff"
            }[entry.status]
            
            node_name = label.replace(":", "_")
            lines.append(f'    {node_name}["{label}"]')
            lines.append(f'    style {node_name} fill {color}')
            
            # 添加边
            for dep in entry.dependencies:
                dep_name = dep.replace(":", "_")
                lines.append(f'    {dep_name} --> {node_name}')
        
        return "\n".join(lines)

class BlueprintGenerator:
    """
    从 Lean 代码生成蓝图骨架
    """
    
    def generate_from_lean(self, lean_path: str) -> str:
        """
        从 Lean 文件生成 LaTeX 蓝图
        """
        with open(lean_path, 'r') as f:
            content = f.read()
        
        latex_lines = [
            "\\documentclass{report}",
            "\\usepackage{leanblueprint}",
            "\\begin{document}",
            "",
            "\\chapter{Auto-generated Blueprint}",
            ""
        ]
        
        # 提取定义和定理
        # 简化实现
        lines = content.split('\n')
        counter = 1
        
        for line in lines:
            if line.strip().startswith('structure '):
                name = line.split('structure ')[1].split(' where')[0]
                latex_lines.append(f"\\begin{{definition}}[{name}]")
                latex_lines.append(f"\\label{{def:{name.lower()}}}")
                latex_lines.append(f"Structure: {name}")
                latex_lines.append("\\end{definition}")
                latex_lines.append("")
            
            elif line.strip().startswith('theorem '):
                name = line.split('theorem ')[1].split(' ')[0]
                latex_lines.append(f"\\begin{{theorem}}[{name}]")
                latex_lines.append(f"\\label{{thm:{name.lower()}}}")
                latex_lines.append(f"Theorem: {name}")
                latex_lines.append("\\end{theorem}")
                latex_lines.append("")
        
        latex_lines.extend([
            "\\end{document}"
        ])
        
        return "\n".join(latex_lines)
```

### 4. GitHub Actions 集成

```yaml
# .github/workflows/blueprint.yml
name: Build Blueprint

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Install Lean
      run: |
        curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y
        echo "$HOME/.elan/bin" >> $GITHUB_PATH
    
    - name: Build Lean project
      run: |
        cd project
        lake build
    
    - name: Install Python dependencies
      run: |
        pip install leanblueprint matplotlib
    
    - name: Generate blueprint
      run: |
        leanblueprint build
        leanblueprint deps > docs/dependency_graph.md
    
    - name: Check for sorry
      run: |
        python scripts/check_sorry.py project/LeanProject
    
    - name: Upload blueprint
      uses: actions/upload-artifact@v3
      with:
        name: blueprint
        path: docs/
    
    - name: Deploy to GitHub Pages
      if: github.ref == 'refs/heads/main'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs
```

---

## 最佳实践

### 1. 蓝图编写规范

```latex
% 命名规范:
% - 定义: def:category-name
% - 引理: lem:category-name
% - 定理: thm:category-name

% 好的例子:
\begin{definition}[Project Structure]
\label{def:project-structure}
...
\end{definition}

% 坏的例子:
\begin{definition}
\label{my-def}  % 不清晰
...
\end{definition}
```

### 2. Lean 命名映射

```lean
/-
  命名映射规范:
  
  蓝图标签                    Lean 名称
  ─────────────────────────────────────────
  def:project-structure    → Project.Structure
  lem:budget-valid         → Project.budget_valid
  thm:project-health       → Project.health_theorem
-/

-- 使用一致的命名约定
namespace Project

/-- 对应 def:project-structure -/
structure Structure where ...

/-- 对应 lem:budget-valid -/
theorem budget_valid ...

/-- 对应 thm:project-health -/
theorem health_theorem ...

end Project
```

### 3. 依赖管理

```lean
-- 按依赖顺序组织文件
-- LeanProject/
-- ├── Basic.lean         # 无依赖
-- ├── Definitions.lean   # 依赖 Basic
-- ├── Lemmas.lean        # 依赖 Definitions
-- └── Theorems.lean      # 依赖 Lemmas

-- Basic.lean - 基础定义
def BasicType := ...

-- Definitions.lean
import LeanProject.Basic
def DerivedType := ...

-- Lemmas.lean
import LeanProject.Definitions
theorem lemma1 : ...

-- Theorems.lean
import LeanProject.Lemmas
theorem main_theorem : ...
```

---

## 项目统计更新

| 指标 | 更新前 | 更新后 |
|------|--------|--------|
| 集成项目数 | 25 | 26 |
| 项目模板 | - | 1 |
| Stars 总和 | ~19,039 | ~19,142 |
| 蓝图工具 | - | 完整 |

---

## 快速开始

```bash
# 使用模板创建项目
# GitHub: Use this template

# 或克隆
git clone https://github.com/leanprover-community/LeanProject.git my-project
cd my-project

# 安装依赖
cd project && lake build

# 创建蓝图
mkdir -p blueprint/src/content
# 编写 LaTeX 蓝图

# 生成依赖图
leanblueprint deps
```

---

**版本**: 17.0.0 (Twenty-Six-in-One)
**更新日期**: 2025-03-25

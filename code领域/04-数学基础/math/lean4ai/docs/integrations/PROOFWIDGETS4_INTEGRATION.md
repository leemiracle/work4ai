# ProofWidgets4 集成指南

## 项目概述

**ProofWidgets4** 是 Lean4 的可视化组件工具包，用于创建交互式证明界面。

| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/leanprover-community/ProofWidgets4 |
| **Stars** | 194 |
| **Forks** | 44 |
| **语言** | Lean 4 / TypeScript |
| **许可证** | Apache 2.0 |
| **描述** | Helper toolkit for creating Lean 4 UserWidgets |
| **主题** | lean, lean4, visualization |

---

## 核心功能

### 架构

```
┌─────────────────────────────────────────────────────────────┐
│                  ProofWidgets4 架构                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              Lean4 代码                              │   │
│   │  @[widget_module]                                    │   │
│   │  def myWidget := ...                                 │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              ProofWidgets4 核心                      │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │Component │  │ RpcStore │  │Svg/Penpot│          │   │
│   │  │ 基础类    │  │ 远程调用  │  │ 图形渲染  │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              TypeScript/React 前端                   │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │  React   │  │  HTML    │  │  CSS     │          │   │
│   │  │  组件     │  │  渲染    │  │  样式    │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              VSCode / Neovim 显示                    │   │
│   │  交互式可视化界面                                      │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 内置组件

| 组件 | 描述 | 用途 |
|------|------|------|
| `Html.ofComponent` | 基础 HTML 组件 | 自定义 UI |
| `Svg` | SVG 图形 | 图表和可视化 |
| `Penpot` | 绘图工具 | 复杂图形 |
| `RpcStore` | 远程过程调用 | 数据传输 |

---

## 基本用法

### 1. 简单组件

```lean
import ProofWidgets

/-- 简单的文本显示组件 -/
@[widget_module]
def HelloWorld : ProofWidgets.Module where
  javascript := include_str "." / "hello.js"

-- 使用
#show HelloWorld
```

### 2. TypeScript 组件

```typescript
// hello.js
import * as React from 'react';

export default function(props) {
  return React.createElement('div', null, 'Hello, Lean4!');
}
```

### 3. 交互式组件

```lean
import ProofWidgets

/-- 带状态的计数器组件 -/
@[widget_module]
def Counter : ProofWidgets.Module where
  javascript := include_str "." / "counter.js"

-- 使用
#show Counter
```

```typescript
// counter.js
import * as React from 'react';
import { Rpc } from '@leanprover/infoview';

export default function(props) {
  const [count, setCount] = React.useState(0);
  
  return React.createElement('div', null, [
    React.createElement('p', null, `Count: ${count}`),
    React.createElement('button', {
      onClick: () => setCount(count + 1)
    }, 'Increment')
  ]);
}
```

---

## 与 Lean4AI 集成

### 1. 项目状态可视化

```lean
-- Lean4AI/Widgets/ProjectVisualization.lean

import ProofWidgets
import Lean4AI.Project.Basic

open Lean ProofWidgets

namespace Lean4AI.Widgets

/-- 项目健康度仪表盘 -/
@[widget_module]
def ProjectHealthDashboard : ProofWidgets.Module where
  javascript := include_str "." / "ProjectHealth.js"

/-- 显示项目健康度 -/
def showProjectHealth (p : Project) : ProofWidgets.Html :=
  let health := p.healthScore
  
  Html.div #[] #[
    Html.h2 #[] "项目健康度",
    Html.div #[Html.Style.expr "display: flex; gap: 10px;"] #[
      healthGauge health,
      projectStats p
    ]
  ]
where
  healthGauge (score : Float) : ProofWidgets.Html :=
    Html.div #[] #[
      Html.Svg.circle #[
        Svg.r "50",
        Svg.cx "60",
        Svg.cy "60",
        Svg.fill (colorFromScore score),
        Svg.stroke "black"
      ],
      Html.text s!"健康度: {(score * 100).toInt}%"
    ]
  
  projectStats (p : Project) : ProofWidgets.Html :=
    Html.div #[] #[
      Html.p #[] s!"预算: {p.budget}",
      Html.p #[] s!"已用: {p.spent}",
      Html.p #[] s!"剩余: {p.budget - p.spent}"
    ]
  
  colorFromScore (s : Float) : String :=
    if s >= 0.8 then "green"
    else if s >= 0.5 then "yellow"
    else "red"

/-- Sprint 进度可视化 -/
@[widget_module]
def SprintProgressWidget : ProofWidgets.Module where
  javascript := include_str "." / "SprintProgress.js"

def showSprintProgress (s : Sprint) : ProofWidgets.Html :=
  let completion := s.completionRate
  
  Html.div #[] #[
    Html.h3 #[] s!"Sprint: {s.name}",
    progressBar completion,
    taskList s.tasks
  ]
where
  progressBar (p : Float) : ProofWidgets.Html :=
    Html.div #[Html.Style.expr "
      width: 100%;
      background: #f0f0f0;
      border-radius: 5px;
    "] #[
      Html.div #[Html.Style.expr s!"
        width: {(p * 100).toInt}%;
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        height: 20px;
        border-radius: 5px;
        transition: width 0.3s;
      "] #[]
    ]
  
  taskList (tasks : List Task) : ProofWidgets.Html :=
    Html.ul #[] (tasks.map fun t =>
      Html.li #[] s!"{t.name}: {t.status}"
    )

/-- 风险矩阵可视化 -/
@[widget_module]
def RiskMatrixWidget : ProofWidgets.Module where
  javascript := include_str "." / "RiskMatrix.js"

def showRiskMatrix (risks : List Risk) : ProofWidgets.Html :=
  Html.div #[] #[
    Html.h3 #[] "风险矩阵",
    Html.Svg.svg #[
      Svg.width "400",
      Svg.height "400",
      Svg.viewBox "0 0 400 400"
    ] (risks.mapIdx fun i r =>
      riskPoint r (i.val * 50 + 25)
    )
  ]
where
  riskPoint (r : Risk) (x : Nat) : ProofWidgets.Svg :=
    Html.Svg.circle #[
      Svg.cx s!"{x}",
      Svg.cy s!"{(1 - r.score) * 400}",
      Svg.r "10",
      Svg.fill (if r.score > 0.7 then "red" else "green"),
      Svg.onclick s!"showRiskDetails('{r.name}')"
    ]

end Lean4AI.Widgets
```

### 2. TypeScript 前端组件

```typescript
// ProjectHealth.js
import * as React from 'react';

interface ProjectHealthProps {
  budget: number;
  spent: number;
  tasks: Task[];
}

export default function ProjectHealthDashboard(props: ProjectHealthProps) {
  const remaining = props.budget - props.spent;
  const healthScore = remaining / props.budget;
  
  const completedTasks = props.tasks.filter(t => t.status === 'done').length;
  const totalTasks = props.tasks.length;
  
  return React.createElement('div', {
    style: {
      padding: '20px',
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f5f5f5',
      borderRadius: '10px'
    }
  }, [
    // 标题
    React.createElement('h2', { 
      key: 'title',
      style: { color: '#333' }
    }, '项目健康度仪表盘'),
    
    // 健康度环形图
    React.createElement('div', {
      key: 'gauge',
      style: { display: 'flex', justifyContent: 'center', marginBottom: '20px' }
    }, [
      React.createElement(SVGCircle, {
        key: 'circle',
        percentage: healthScore * 100,
        size: 150,
        strokeWidth: 15
      })
    ]),
    
    // 统计卡片
    React.createElement('div', {
      key: 'stats',
      style: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px' }
    }, [
      statCard('预算', `$${props.budget}`, '#2196F3'),
      statCard('已用', `$${props.spent}`, '#FF9800'),
      statCard('剩余', `$${remaining}`, '#4CAF50')
    ]),
    
    // 任务进度
    React.createElement('div', {
      key: 'tasks',
      style: { marginTop: '20px' }
    }, [
      React.createElement('h3', { key: 'h3' }, '任务进度'),
      React.createElement(ProgressBar, {
        key: 'progress',
        value: completedTasks,
        max: totalTasks,
        label: `${completedTasks}/${totalTasks}`
      })
    ])
  ]);
}

function statCard(title: string, value: string, color: string) {
  return React.createElement('div', {
    style: {
      backgroundColor: 'white',
      padding: '15px',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      borderLeft: `4px solid ${color}`
    }
  }, [
    React.createElement('div', { 
      key: 'title',
      style: { fontSize: '12px', color: '#666' }
    }, title),
    React.createElement('div', { 
      key: 'value',
      style: { fontSize: '24px', fontWeight: 'bold', color }
    }, value)
  ]);
}

function SVGCircle({ percentage, size, strokeWidth }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;
  
  return React.createElement('svg', {
    width: size,
    height: size
  }, [
    React.createElement('circle', {
      key: 'bg',
      cx: size / 2,
      cy: size / 2,
      r: radius,
      fill: 'none',
      stroke: '#e0e0e0',
      strokeWidth
    }),
    React.createElement('circle', {
      key: 'fg',
      cx: size / 2,
      cy: size / 2,
      r: radius,
      fill: 'none',
      stroke: percentage > 70 ? '#4CAF50' : percentage > 40 ? '#FF9800' : '#f44336',
      strokeWidth,
      strokeDasharray: circumference,
      strokeDashoffset: offset,
      strokeLinecap: 'round',
      transform: `rotate(-90 ${size/2} ${size/2})`
    }),
    React.createElement('text', {
      key: 'text',
      x: '50%',
      y: '50%',
      textAnchor: 'middle',
      dy: '0.3em',
      fontSize: '20px',
      fontWeight: 'bold'
    }, `${Math.round(percentage)}%`)
  ]);
}

function ProgressBar({ value, max, label }) {
  const percentage = (value / max) * 100;
  
  return React.createElement('div', {
    style: { width: '100%' }
  }, [
    React.createElement('div', {
      key: 'bar',
      style: {
        width: '100%',
        height: '20px',
        backgroundColor: '#e0e0e0',
        borderRadius: '10px',
        overflow: 'hidden'
      }
    }, [
      React.createElement('div', {
        key: 'fill',
        style: {
          width: `${percentage}%`,
          height: '100%',
          backgroundColor: '#4CAF50',
          transition: 'width 0.3s'
        }
      })
    ]),
    React.createElement('div', {
      key: 'label',
      style: { textAlign: 'center', marginTop: '5px' }
    }, label)
  ]);
}
```

### 3. 证明状态可视化

```lean
-- Lean4AI/Widgets/ProofVisualization.lean

import ProofWidgets
import Lean.Meta

open Lean ProofWidgets Meta

namespace Lean4AI.Widgets

/-- 证明目标树可视化 -/
@[widget_module]
def ProofTreeWidget : ProofWidgets.Module where
  javascript := include_str "." / "ProofTree.js"

/-- 显示证明树 -/
def showProofTree (goals : List MVarId) : MetaM ProofWidgets.Html := do
  let nodes ← goals.mapM fun g => do
    let type ← g.getType
    pure (toString type)
  
  return Html.div #[] #[
    Html.h3 #[] "证明目标",
    Html.ul #[] (nodes.map fun n => Html.li #[] n)
  ]

/-- 策略应用历史 -/
@[widget_module]
def TacticHistoryWidget : ProofWidgets.Module where
  javascript := include_str "." / "TacticHistory.js"

structure TacticStep where
  tactic : String
  goal : String
  result : String
  deriving ToJson

def showTacticHistory (steps : List TacticStep) : ProofWidgets.Html :=
  Html.div #[] #[
    Html.h3 #[] "策略历史",
    Html.table #[
      Html.Style.expr "
        width: 100%;
        border-collapse: collapse;
      "
    ] #[
      Html.tr #[] #[
        Html.th #[] "策略",
        Html.th #[] "目标",
        Html.th #[] "结果"
      ],
      Html.tbody #[] (steps.map fun s =>
        Html.tr #[] #[
          Html.td #[] s.tactic,
          Html.td #[Html.Style.expr "font-family: monospace;"] s.goal,
          Html.td #[Html.Style.expr "color: green;"] s.result
        ]
      )
    ]
  ]

/-- 依赖图可视化 -/
@[widget_module]
def DependencyGraphWidget : ProofWidgets.Module where
  javascript := include_str "." / "DependencyGraph.js"

def showDependencyGraph (theorem : Name) : MetaM ProofWidgets.Html := do
  let deps ← getDependencies theorem
  
  return Html.div #[] #[
    Html.h3 #[] s!"依赖图: {theorem}",
    Html.Svg.svg #[
      Svg.width "800",
      Svg.height "600"
    ] (deps.mapIdx fun i d =>
      Html.Svg.g #[] #[
        Html.Svg.circle #[
          Svg.cx s!"{i.val * 100 + 50}",
          Svg.cy "100",
          Svg.r "20",
          Svg.fill "lightblue"
        ],
        Html.Svg.text #[
          Svg.x s!"{i.val * 100 + 50}",
          Svg.y "150",
          Svg.textAnchor "middle"
        ] (toString d)
      ]
    )
  ]
where
  getDependencies (n : Name) : MetaM (List Name) := do
    -- 简化实现
    pure [n]

end Lean4AI.Widgets
```

### 4. 交互式 Lean 信息面板

```typescript
// LeanInfoPanel.tsx
import * as React from 'react';
import { Rpc } from '@leanprover/infoview';

interface LeanInfoProps {
  fileName: string;
  line: number;
  column: number;
}

interface Goal {
  type: string;
  context: {name: string, type: string}[];
}

export default function LeanInfoPanel(props: LeanInfoProps) {
  const [goals, setGoals] = React.useState<Goal[]>([]);
  const [messages, setMessages] = React.useState<string[]>([]);
  
  React.useEffect(() => {
    // 获取 Lean 信息
    fetchGoals();
  }, [props.line, props.column]);
  
  const fetchGoals = async () => {
    try {
      const result = await Rpc.call('getGoals', {
        file: props.fileName,
        line: props.line,
        column: props.column
      });
      setGoals(result.goals);
      setMessages(result.messages);
    } catch (e) {
      console.error('Failed to fetch goals:', e);
    }
  };
  
  return React.createElement('div', {
    style: {
      padding: '15px',
      backgroundColor: '#1e1e1e',
      color: '#d4d4d4',
      fontFamily: 'Consolas, monospace',
      fontSize: '14px'
    }
  }, [
    // 目标显示
    React.createElement('div', { key: 'goals' }, [
      React.createElement('h4', { 
        key: 'h4',
        style: { color: '#569cd6' }
      }, 'Goals'),
      ...goals.map((g, i) => 
        React.createElement('div', {
          key: `goal-${i}`,
          style: {
            margin: '10px 0',
            padding: '10px',
            backgroundColor: '#252526',
            borderRadius: '4px'
          }
        }, [
          // 上下文
          ...g.context.map(c => 
            React.createElement('div', {
              key: c.name,
              style: { color: '#9cdcfe' }
            }, `${c.name} : ${c.type}`)
          ),
          // 分隔线
          React.createElement('hr', {
            key: 'sep',
            style: { borderColor: '#3c3c3c' }
          }),
          // 目标
          React.createElement('div', {
            key: 'goal-type',
            style: { color: '#4ec9b0' }
          }, `⊢ ${g.type}`)
        ])
      )
    ]),
    
    // 消息
    React.createElement('div', { 
      key: 'messages',
      style: { marginTop: '15px' }
    }, [
      React.createElement('h4', { 
        key: 'h4',
        style: { color: '#569cd6' }
      }, 'Messages'),
      ...messages.map((m, i) => 
        React.createElement('div', {
          key: `msg-${i}`,
          style: { color: '#ce9178' }
        }, m)
      )
    ]),
    
    // 建议策略
    React.createElement('div', {
      key: 'suggestions',
      style: { marginTop: '15px' }
    }, [
      React.createElement('h4', {
        key: 'h4',
        style: { color: '#569cd6' }
      }, 'Suggested Tactics'),
      ...suggestTactics(goals).map(t =>
        React.createElement('button', {
          key: t,
          style: {
            margin: '5px',
            padding: '5px 10px',
            backgroundColor: '#0e639c',
            color: 'white',
            border: 'none',
            borderRadius: '3px',
            cursor: 'pointer'
          },
          onClick: () => applyTactic(t)
        }, t)
      )
    ])
  ]);
}

function suggestTactics(goals: Goal[]): string[] {
  const suggestions: string[] = [];
  
  for (const g of goals) {
    if (g.type.includes('∧')) suggestions.push('constructor');
    if (g.type.includes('∨')) suggestions.push('left', 'right');
    if (g.type.includes('→')) suggestions.push('intro');
    if (g.type.includes('∃')) suggestions.push('use');
    if (g.type.includes('=')) suggestions.push('rfl', 'simp');
  }
  
  suggestions.push('native_decide', 'aesop');
  
  return [...new Set(suggestions)];
}

async function applyTactic(tactic: string) {
  await Rpc.call('applyTactic', { tactic });
}
```

---

## 自定义组件开发

### 1. 创建新组件

```bash
# 创建组件目录
mkdir -p Lean4AI/Widgets/src

# 创建 Lean 文件
cat > Lean4AI/Widgets/MyWidget.lean << 'EOF'
import ProofWidgets

@[widget_module]
def MyCustomWidget : ProofWidgets.Module where
  javascript := include_str "." / "my-widget.js"
EOF

# 创建 TypeScript 文件
cat > Lean4AI/Widgets/src/my-widget.tsx << 'EOF'
import * as React from 'react';

export default function(props: any) {
  return React.createElement('div', null, 'My Custom Widget');
}
EOF

# 编译 TypeScript
cd Lean4AI/Widgets/src
tsc my-widget.tsx --jsx react --esModuleInterop
```

### 2. lakefile 配置

```lean
-- lakefile.lean
import Lake
open Lake DSL

package lean4ai where
  -- 包配置

require ProofWidgets4 from git
  "https://github.com/leanprover-community/ProofWidgets4" @ "main"

@[default_target]
lean_lib Lean4AI.Widgets where
  roots := [
    `Lean4AI.Widgets.ProjectVisualization,
    `Lean4AI.Widgets.ProofVisualization
  ]
```

---

## 部署

### 1. 本地开发

```bash
# 克隆仓库
git clone https://github.com/leanprover-community/ProofWidgets4.git

# 构建
cd ProofWidgets4
lake build

# 在项目中使用
# lakefile.lean 中添加依赖
```

### 2. VSCode 集成

ProofWidgets4 自动与 VSCode 的 Lean4 扩展集成。只需在代码中使用：

```lean
import ProofWidgets

#show ProjectHealthDashboard
```

---

## 项目统计更新

| 指标 | 更新前 | 更新后 |
|------|--------|--------|
| 集成项目数 | 19 | 20 |
| 自定义组件 | - | 10+ |
| Stars 总和 | ~18,150 | ~18,344 |
| 可视化功能 | 基础 | 完整 |

---

## 快速开始

```bash
# 安装
cd /mnt/c/workspace/math/lean4ai
git clone https://github.com/leanprover-community/ProofWidgets4.git

# 添加到项目
# 在 lakefile.lean 中添加依赖

# 使用组件
# import ProofWidgets
# #show YourWidget
```

---

**版本**: 12.0.0 (Twenty-in-One)
**更新日期**: 2025-03-25

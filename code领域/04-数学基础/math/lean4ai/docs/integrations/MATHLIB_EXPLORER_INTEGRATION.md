# MathlibExplorer 集成：可视化数学理论网络

## 📖 项目概述

**MathlibExplorer** 是一个交互式可视化工具，用于展示 Lean 的 Mathlib 库中数学理论之间的导入关系。

### 核心价值

| 特性 | 描述 |
|------|------|
| **可视化导入图** | 展示理论之间的依赖关系 |
| **方向布局** | 从左到右：基础 → 高级 |
| **交互式探索** | 点击节点查看依赖 |
| **主题分组** | 相似理论归类 |

---

## 🎯 与我们项目的整合价值

### 1. 可视化我们的验证模块

```
我们的模块依赖关系：
┌─────────────────────────────────────────────────────┐
│                  项目管理验证层                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Leantime/ProjectManagement.lean                    │
│         │                                           │
│         ├── Agile/Verification.lean                 │
│         │         │                                 │
│         │         └── Mathlib.Data.Real.Basic       │
│         │                                           │
│         ├── Quant/Strategy.lean                     │
│         │         │                                 │
│         │         └── Mathlib.Analysis.Calculus     │
│         │                                           │
│         └── Medical/Decision.lean                   │
│                   │                                 │
│                   └── Mathlib.Data.Finset           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 2. 技术借鉴

| 技术 | 用途 | 我们的应用 |
|------|------|-----------|
| **图布局算法** | 从左到右的 DAG 布局 | 可视化项目依赖 |
| **交互式探索** | 点击节点高亮依赖 | 探索验证关系 |
| **主题分组** | 相似理论归类 | 模块分组 |
| **缩放拖拽** | 大规模图浏览 | 复杂项目导航 |

---

## 🔧 安装和使用

### 1. 克隆仓库

```bash
cd /mnt/c/workspace/math/lean4ai
git clone https://github.com/Crispher/MathlibExplorer.git
cd MathlibExplorer
```

### 2. 运行（MacOS/Linux/Windows）

```bash
# MacOS
cd release/bin_macos
./MathlibExplorer

# Linux
cd release/bin_linux
./MathlibExplorer

# Windows
cd release/bin_windows
MathlibExplorer.exe
```

### 3. 交互操作

| 操作 | 效果 |
|------|------|
| **滚轮** | 缩放 |
| **拖拽** | 移动视图 |
| **点击节点** | 高亮依赖/被依赖 |
| **点击主题标签** | 高亮整组理论 |

---

## 💡 核心技术提取

### 1. 导入图数据结构

```python
# import_graph.py

from dataclasses import dataclass
from typing import List, Dict, Set
import json

@dataclass
class ImportNode:
    """导入图节点"""
    id: str                    # 模块路径，如 "Mathlib.Data.Real.Basic"
    name: str                  # 简短名称，如 "Real.Basic"
    topic: str                 # 主题，如 "Analysis"
    dependencies: List[str]    # 直接依赖
    dependents: List[str]      # 直接被依赖
    transitive_deps: Set[str]  # 传递依赖
    transitive_dependents: Set[str]  # 传递被依赖

@dataclass
class ImportGraph:
    """导入图"""
    nodes: Dict[str, ImportNode]
    topics: Dict[str, List[str]]  # 主题 -> 节点列表
    
    def get_dependencies(self, node_id: str, transitive: bool = False) -> List[str]:
        """获取依赖"""
        node = self.nodes.get(node_id)
        if not node:
            return []
        return list(node.transitive_deps) if transitive else node.dependencies
    
    def get_dependents(self, node_id: str, transitive: bool = False) -> List[str]:
        """获取被依赖"""
        node = self.nodes.get(node_id)
        if not node:
            return []
        return list(node.transitive_dependents) if transitive else node.dependents
    
    def get_topic_nodes(self, topic: str) -> List[str]:
        """获取主题下的所有节点"""
        return self.topics.get(topic, [])
    
    def get_topic_dependencies(self, topic: str) -> Dict[str, List[str]]:
        """获取主题的依赖关系"""
        nodes = self.get_topic_nodes(topic)
        all_deps = set()
        for node_id in nodes:
            node = self.nodes[node_id]
            all_deps.update(node.dependencies)
        # 排除自身主题的节点
        return {dep: self.nodes[dep].topic for dep in all_deps if dep not in nodes}

class ImportGraphBuilder:
    """导入图构建器"""
    
    def __init__(self):
        self.nodes: Dict[str, ImportNode] = {}
        self.topics: Dict[str, List[str]] = {}
    
    def add_module(self, module_path: str, dependencies: List[str]):
        """添加模块"""
        # 解析主题
        parts = module_path.split('.')
        topic = parts[1] if len(parts) > 1 else "Other"
        name = '.'.join(parts[-2:]) if len(parts) >= 2 else module_path
        
        # 创建节点
        node = ImportNode(
            id=module_path,
            name=name,
            topic=topic,
            dependencies=dependencies,
            dependents=[],
            transitive_deps=set(),
            transitive_dependents=set()
        )
        
        self.nodes[module_path] = node
        
        # 添加到主题
        if topic not in self.topics:
            self.topics[topic] = []
        self.topics[topic].append(module_path)
        
        # 更新反向依赖
        for dep in dependencies:
            if dep in self.nodes:
                self.nodes[dep].dependents.append(module_path)
    
    def compute_transitive_relations(self):
        """计算传递关系"""
        # 使用拓扑排序计算传递闭包
        for node_id in self.nodes:
            self._compute_transitive_deps(node_id, set())
    
    def _compute_transitive_deps(self, node_id: str, visited: Set[str]):
        """计算传递依赖"""
        if node_id in visited:
            return
        
        visited.add(node_id)
        node = self.nodes[node_id]
        
        for dep_id in node.dependencies:
            if dep_id in self.nodes:
                dep = self.nodes[dep_id]
                node.transitive_deps.add(dep_id)
                dep.transitive_dependents.add(node_id)
                
                # 递归
                self._compute_transitive_deps(dep_id, visited)
                node.transitive_deps.update(dep.transitive_deps)
    
    def build(self) -> ImportGraph:
        """构建图"""
        self.compute_transitive_relations()
        return ImportGraph(nodes=self.nodes, topics=self.topics)
    
    def to_json(self) -> str:
        """导出为 JSON"""
        data = {
            'nodes': {
                id: {
                    'name': node.name,
                    'topic': node.topic,
                    'dependencies': node.dependencies,
                    'dependents': node.dependents
                }
                for id, node in self.nodes.items()
            },
            'topics': self.topics
        }
        return json.dumps(data, indent=2)


# 使用示例
if __name__ == "__main__":
    builder = ImportGraphBuilder()
    
    # 添加我们的模块
    builder.add_module("Leantime.ProjectManagement", [
        "Mathlib.Data.Real.Basic",
        "Mathlib.Data.List.Basic"
    ])
    
    builder.add_module("Agile.Verification", [
        "Mathlib.Data.Real.Basic",
        "Mathlib.Data.List.Basic",
        "Mathlib.Data.Nat.Basic"
    ])
    
    builder.add_module("Quant.Strategy", [
        "Mathlib.Data.Real.Basic",
        "Mathlib.Analysis.Calculus.Deriv"
    ])
    
    builder.add_module("Medical.Decision", [
        "Mathlib.Data.Real.Basic",
        "Mathlib.Data.Finset.Basic"
    ])
    
    # 构建图
    graph = builder.build()
    
    # 导出
    print(builder.to_json())
```

---

### 2. 图布局算法（从左到右的 DAG）

```python
# layout_algorithm.py

from typing import Dict, List, Tuple
import numpy as np

class DAGLayout:
    """有向无环图的从左到右布局"""
    
    def __init__(self, graph: ImportGraph):
        self.graph = graph
        self.positions: Dict[str, Tuple[float, float]] = {}
    
    def compute_layout(self) -> Dict[str, Tuple[float, float]]:
        """计算布局"""
        # 1. 拓扑排序确定层级
        levels = self._assign_levels()
        
        # 2. 每层内垂直排列
        self._assign_vertical_positions(levels)
        
        return self.positions
    
    def _assign_levels(self) -> Dict[int, List[str]]:
        """分配层级（基于最长路径）"""
        levels: Dict[int, List[str]] = {}
        
        for node_id in self.graph.nodes:
            # 计算到根节点的最长路径
            level = self._longest_path(node_id)
            if level not in levels:
                levels[level] = []
            levels[level].append(node_id)
        
        return levels
    
    def _longest_path(self, node_id: str) -> int:
        """计算到根节点的最长路径"""
        node = self.graph.nodes[node_id]
        if not node.dependencies:
            return 0
        
        max_level = 0
        for dep_id in node.dependencies:
            if dep_id in self.graph.nodes:
                max_level = max(max_level, self._longest_path(dep_id) + 1)
        
        return max_level
    
    def _assign_vertical_positions(self, levels: Dict[int, List[str]]):
        """分配垂直位置"""
        for level, nodes in levels.items():
            n = len(nodes)
            for i, node_id in enumerate(nodes):
                # X 坐标基于层级
                x = level * 200
                # Y 坐标均匀分布
                y = (i - n / 2) * 50
                self.positions[node_id] = (x, y)
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """获取边界"""
        if not self.positions:
            return (0, 0, 0, 0)
        
        xs = [p[0] for p in self.positions.values()]
        ys = [p[1] for p in self.positions.values()]
        
        return (min(xs), min(ys), max(xs), max(ys))
```

---

### 3. 交互式可视化（Web 版本）

```python
# web_visualizer.py

from flask import Flask, jsonify, send_file
from typing import Dict
import json

app = Flask(__name__)

class WebVisualizer:
    """Web 可视化服务器"""
    
    def __init__(self, graph: ImportGraph):
        self.graph = graph
        self.layout = DAGLayout(graph)
        self.positions = self.layout.compute_layout()
    
    def generate_html(self) -> str:
        """生成 HTML 页面"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Import Graph Explorer</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }
        svg {
            width: 100vw;
            height: 100vh;
        }
        .node {
            cursor: pointer;
        }
        .node circle {
            fill: lightblue;
            stroke: steelblue;
            stroke-width: 2px;
        }
        .node.highlighted circle {
            fill: orange;
        }
        .node.dependency circle {
            fill: lightgreen;
        }
        .node.dependent circle {
            fill: pink;
        }
        .link {
            fill: none;
            stroke: #999;
            stroke-width: 1px;
            opacity: 0.3;
        }
        .link.highlighted {
            stroke: red;
            stroke-width: 2px;
            opacity: 1;
        }
        .label {
            font-size: 10px;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <svg id="graph"></svg>
    <script>
        // 加载数据
        const nodes = Object.entries(DATA.nodes).map(([id, node]) => ({
            id,
            ...node,
            x: POSITIONS[id][0],
            y: POSITIONS[id][1]
        }));
        
        const links = [];
        nodes.forEach(node => {
            node.dependencies.forEach(dep => {
                links.push({ source: dep, target: node.id });
            });
        });
        
        // 创建 SVG
        const svg = d3.select('#graph');
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        // 绘制连线
        const link = svg.selectAll('.link')
            .data(links)
            .enter().append('path')
            .attr('class', 'link')
            .attr('d', d => {
                const source = nodes.find(n => n.id === d.source);
                const target = nodes.find(n => n.id === d.target);
                return `M${source.x},${source.y}L${target.x},${target.y}`;
            });
        
        // 绘制节点
        const node = svg.selectAll('.node')
            .data(nodes)
            .enter().append('g')
            .attr('class', 'node')
            .attr('transform', d => `translate(${d.x},${d.y})`)
            .on('click', handleClick);
        
        node.append('circle').attr('r', 10);
        
        node.append('text')
            .attr('class', 'label')
            .attr('dx', 12)
            .attr('dy', 4)
            .text(d => d.name);
        
        // 点击处理
        function handleClick(event, d) {
            // 重置所有样式
            node.classed('highlighted dependency dependent', false);
            link.classed('highlighted', false);
            
            // 高亮当前节点
            d3.select(this).classed('highlighted', true);
            
            // 高亮依赖
            d.dependencies.forEach(depId => {
                d3.select(`.node[id="${depId}"]`).classed('dependency', true);
                d3.select(`.link[source="${depId}"][target="${d.id}"]`).classed('highlighted', true);
            });
            
            // 高亮被依赖
            d.dependents.forEach(depId => {
                d3.select(`.node[id="${depId}"]`).classed('dependent', true);
                d3.select(`.link[source="${d.id}"][target="${depId}"]`).classed('highlighted', true);
            });
        }
        
        // 缩放
        const zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on('zoom', event => {
                svg.selectAll('g').attr('transform', event.transform);
            });
        
        svg.call(zoom);
    </script>
</body>
</html>
"""
    
    def start_server(self, port: int = 5000):
        """启动服务器"""
        @app.route('/')
        def index():
            return self.generate_html()
        
        @app.route('/data/nodes')
        def get_nodes():
            return jsonify({
                id: {
                    'name': node.name,
                    'topic': node.topic,
                    'dependencies': node.dependencies,
                    'dependents': node.dependents
                }
                for id, node in self.graph.nodes.items()
            })
        
        @app.route('/data/positions')
        def get_positions():
            return jsonify(self.positions)
        
        print(f"服务器启动: http://localhost:{port}")
        app.run(port=port)


# 使用示例
if __name__ == "__main__":
    # 构建图（见前面的代码）
    builder = ImportGraphBuilder()
    # ... 添加模块 ...
    graph = builder.build()
    
    # 创建可视化
    visualizer = WebVisualizer(graph)
    visualizer.start_server()
```

---

## 🎨 为我们的项目创建可视化

### 项目模块依赖图

```python
# visualize_project_structure.py

from import_graph import ImportGraphBuilder, ImportGraph
from layout_algorithm import DAGLayout
from web_visualizer import WebVisualizer

def create_project_graph() -> ImportGraph:
    """创建我们项目的导入图"""
    builder = ImportGraphBuilder()
    
    # 核心模块
    builder.add_module("Lean4.Core", [])
    
    # Mathlib 基础
    builder.add_module("Mathlib.Data.Real.Basic", ["Lean4.Core"])
    builder.add_module("Mathlib.Data.List.Basic", ["Lean4.Core"])
    builder.add_module("Mathlib.Data.Nat.Basic", ["Lean4.Core"])
    builder.add_module("Mathlib.Data.Finset.Basic", ["Lean4.Core"])
    
    # 项目管理模块
    builder.add_module("Leantime.ProjectManagement", [
        "Mathlib.Data.Real.Basic",
        "Mathlib.Data.List.Basic",
        "Mathlib.Data.Nat.Basic"
    ])
    
    # 敏捷验证模块
    builder.add_module("Agile.Verification", [
        "Mathlib.Data.Real.Basic",
        "Mathlib.Data.List.Basic",
        "Mathlib.Data.Nat.Basic",
        "Mathlib.Data.Finset.Basic"
    ])
    
    # 量化交易模块
    builder.add_module("Quant.Strategy", [
        "Mathlib.Data.Real.Basic",
        "Mathlib.Data.List.Basic"
    ])
    
    # 医疗决策模块
    builder.add_module("Medical.Decision", [
        "Mathlib.Data.Real.Basic",
        "Mathlib.Data.Finset.Basic"
    ])
    
    # Aeneas 集成
    builder.add_module("Aeneas.StateMonad", ["Lean4.Core"])
    builder.add_module("Aeneas.Builtins", ["Aeneas.StateMonad"])
    
    # LeanDojo 集成
    builder.add_module("LeanDojo.Extraction", ["Lean4.Core"])
    
    # Python 桥接
    builder.add_module("Bridge.Lean4", [
        "Leantime.ProjectManagement",
        "Agile.Verification",
        "Quant.Strategy",
        "Medical.Decision"
    ])
    
    builder.add_module("Bridge.Leantime", [
        "Bridge.Lean4"
    ])
    
    builder.add_module("Bridge.Agile", [
        "Bridge.Lean4",
        "Agile.Verification"
    ])
    
    builder.add_module("Bridge.LeanDojo", [
        "Bridge.Lean4",
        "LeanDojo.Extraction"
    ])
    
    builder.add_module("Bridge.Aeneas", [
        "Bridge.Lean4",
        "Aeneas.Builtins"
    ])
    
    return builder.build()

def visualize_project():
    """可视化项目"""
    # 创建图
    graph = create_project_graph()
    
    # 创建可视化
    visualizer = WebVisualizer(graph)
    
    # 启动服务器
    print("=" * 60)
    print("项目模块依赖可视化")
    print("=" * 60)
    print("\n操作说明：")
    print("  - 滚轮: 缩放")
    print("  - 拖拽: 移动视图")
    print("  - 点击节点: 查看依赖关系")
    print("  - 绿色: 依赖")
    print("  - 粉色: 被依赖")
    print("=" * 60)
    
    visualizer.start_server(port=8080)

if __name__ == "__main__":
    visualize_project()
```

---

## 📊 可视化效果

### 预期输出

```
项目模块依赖图（简化版）：

     Core
      │
  ────┼────────────────────
  │   │   │   │   │       │
  │ Real List Nat Finset  │
  │   │   │   │   │       │
  │   └───┼───┼───┘       │
  │       │   │           │
  │   ProjectManagement   │
  │       │               │
  │   Verification        │
  │       │               │
  │   ┌───┴───┬───────┐  │
  │   │       │       │  │
  │ Quant  Medical  Aeneas
  │   │       │       │  │
  │   └───┬───┴───────┘  │
  │       │              │
  │   Bridge.Lean4       │
  │       │              │
  │  ┌────┼────┬────┐    │
  │  │    │    │    │    │
  │ Leantime Agile LeanDojo
  │       │              │
  └───────┴──────────────┘
```

---

## 🔗 与我们项目的集成点

### 1. 集成到文档

```markdown
## 模块依赖图

![Module Dependencies](./images/module_graph.png)

使用 [MathlibExplorer](./MathlibExplorer/) 交互式探索模块依赖。
```

### 2. 集成到 YC-Killer Agent

```python
class VisualizationAgent:
    """YC-Killer 可视化代理"""
    
    def visualize_module_dependencies(self, module_path: str) -> str:
        """可视化模块依赖"""
        # 生成可视化
        return self.visualizer.generate_module_graph(module_path)
    
    def analyze_module_importance(self) -> Dict[str, int]:
        """分析模块重要性（基于被依赖次数）"""
        importance = {}
        for node_id, node in self.graph.nodes.items():
            importance[node_id] = len(node.transitive_dependents)
        return importance
```

### 3. 集成到 Leantime

```python
class LeantimeVisualization:
    """Leantime 项目可视化"""
    
    def generate_project_graph(self, project_id: int) -> str:
        """生成项目模块图"""
        # 获取项目模块
        modules = self.get_project_modules(project_id)
        
        # 构建图
        builder = ImportGraphBuilder()
        for module in modules:
            builder.add_module(module.path, module.dependencies)
        
        graph = builder.build()
        
        # 生成可视化
        visualizer = WebVisualizer(graph)
        return visualizer.generate_html()
```

---

## 📚 相关资源

### 官方资源
- **MathlibExplorer**: https://github.com/Crispher/MathlibExplorer
- **视频系列**: 《重构数学》on [bilibili](https://space.bilibili.com/613069855) and [YouTube](https://www.youtube.com/@yugu233/videos)

### 可视化工具
- **D3.js**: https://d3js.org
- **Graphviz**: https://graphviz.org
- **Gephi**: https://gephi.org

---

## 💡 总结

### MathlibExplorer 为我们带来

| 技术 | 价值 |
|------|------|
| **导入图可视化** | 理解模块依赖 |
| **布局算法** | 清晰展示层次 |
| **交互设计** | 直观探索 |
| **主题分组** | 快速定位 |

### 可直接使用

1. ✅ 克隆并运行 MathlibExplorer
2. ✅ 提取布局算法
3. ✅ 创建我们项目的可视化
4. ✅ 集成到 Web 界面

---

**下一步**: 运行 MathlibExplorer，探索 Mathlib 结构！

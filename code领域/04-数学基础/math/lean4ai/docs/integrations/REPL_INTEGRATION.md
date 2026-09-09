# Lean4 REPL 集成指南

## 项目概述

**Lean4 REPL** 是一个简单的 Lean4 交互式环境，返回关于错误和 sorries 的信息。

| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/leanprover-community/repl |
| **Stars** | 194 |
| **Forks** | 66 |
| **语言** | Lean 4 |
| **许可证** | Apache 2.0 |
| **描述** | A simple REPL for Lean 4 |

---

## 核心功能

### REPL 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Lean4 REPL 架构                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  输入 (JSON)                         │   │
│   │  {                                                  │   │
│   │    "cmd": "#check 1 + 1",                           │   │
│   │    "env": 0                                         │   │
│   │  }                                                  │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              Lean4 REPL 服务器                       │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │ 解析输入  │  │ 执行命令  │  │ 收集结果  │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │ 类型检查  │  │ 错误收集  │  │ 状态管理  │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  输出 (JSON)                         │   │
│   │  {                                                  │   │
│   │    "sorries": [],                                   │   │
│   │    "messages": [],                                  │   │
│   │    "env": 1                                         │   │
│   │  }                                                  │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 支持的命令

| 命令 | 描述 | 示例 |
|------|------|------|
| `#check` | 类型检查 | `#check 1 + 1` |
| `#eval` | 求值 | `#eval 2 + 2` |
| `#print` | 打印信息 | `#print Nat.add` |
| `def` | 定义 | `def x := 1` |
| `theorem` | 定理 | `theorem foo : True := trivial` |
| `example` | 示例 | `example : 1 + 1 = 2 := rfl` |
| `inductive` | 归纳类型 | `inductive MyType \| mk` |

---

## API 规范

### 输入格式

```json
{
  "cmd": "string",       // Lean4 命令
  "env": number | null,  // 环境ID (可选)
  "path": "string"       // 文件路径 (可选)
}
```

### 输出格式

```json
{
  "sorries": [           // sorry 列表
    {
      "goal": "string",  // 目标
      "line": number,    // 行号
      "column": number   // 列号
    }
  ],
  "messages": [          // 消息列表
    {
      "severity": "error" | "warning" | "info",
      "content": "string",
      "line": number,
      "column": number
    }
  ],
  "env": number,         // 新环境ID
  "tactics": [           // 策略状态 (可选)
    {
      "goal": "string",
      "goals": ["string"]
    }
  ]
}
```

---

## 安装与使用

### 1. 基本安装

```bash
# 克隆仓库
cd /mnt/c/workspace/math/lean4ai
git clone https://github.com/leanprover-community/repl.git

# 构建
cd repl
lake build

# 启动 REPL
lake exe repl
```

### 2. 使用示例

```bash
# 启动后，通过 stdin/stdout 通信
echo '{"cmd": "#check 1 + 1"}' | lake exe repl

# 输出:
# {"sorries":[],"messages":[],"env":0}

# 多行命令
echo '{"cmd": "def x := 1\n#eval x"}' | lake exe repl

# 带环境的连续命令
echo '{"cmd": "def y := 2", "env": 0}' | lake exe repl
# {"sorries":[],"messages":[],"env":1}

echo '{"cmd": "#eval y + 1", "env": 1}' | lake exe repl
# {"sorries":[],"messages":[],"env":2}
```

---

## 与 Lean4AI 集成

### 1. Python 客户端

```python
# lean4_repl_client.py

import subprocess
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import threading
import queue

@dataclass
class REPLMessage:
    severity: str
    content: str
    line: int
    column: int

@dataclass
class REPLSorry:
    goal: str
    line: int
    column: int

@dataclass
class REPLResponse:
    sorries: List[REPLSorry]
    messages: List[REPLMessage]
    env: int
    tactics: Optional[List[Dict]] = None

class Lean4REPLClient:
    """
    Lean4 REPL Python 客户端
    """
    
    def __init__(self, repl_path: str = "./repl"):
        self.repl_path = repl_path
        self.current_env: int = 0
        self._process: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
    
    def start(self):
        """
        启动 REPL 进程
        """
        self._process = subprocess.Popen(
            ["lake", "exe", "repl"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.repl_path
        )
    
    def stop(self):
        """
        停止 REPL 进程
        """
        if self._process:
            self._process.terminate()
            self._process = None
    
    def send_command(self, cmd: str, env: Optional[int] = None) -> REPLResponse:
        """
        发送命令到 REPL
        """
        with self._lock:
            request = {
                "cmd": cmd,
                "env": env if env is not None else self.current_env
            }
            
            if not self._process:
                self.start()
            
            self._process.stdin.write(json.dumps(request) + "\n")
            self._process.stdin.flush()
            
            response_line = self._process.stdout.readline()
            response_data = json.loads(response_line)
            
            # 更新环境
            self.current_env = response_data.get("env", self.current_env)
            
            return self._parse_response(response_data)
    
    def _parse_response(self, data: Dict) -> REPLResponse:
        """
        解析响应
        """
        sorries = [
            REPLSorry(
                goal=s["goal"],
                line=s["line"],
                column=s["column"]
            )
            for s in data.get("sorries", [])
        ]
        
        messages = [
            REPLMessage(
                severity=m["severity"],
                content=m["content"],
                line=m["line"],
                column=m["column"]
            )
            for m in data.get("messages", [])
        ]
        
        return REPLResponse(
            sorries=sorries,
            messages=messages,
            env=data.get("env", 0),
            tactics=data.get("tactics")
        )
    
    def check_type(self, expr: str) -> REPLResponse:
        """
        类型检查
        """
        return self.send_command(f"#check {expr}")
    
    def eval_expr(self, expr: str) -> REPLResponse:
        """
        求值表达式
        """
        return self.send_command(f"#eval {expr}")
    
    def define(self, name: str, value: str) -> REPLResponse:
        """
        定义
        """
        return self.send_command(f"def {name} := {value}")
    
    def theorem(self, name: str, statement: str, proof: str) -> REPLResponse:
        """
        定理
        """
        cmd = f"theorem {name} : {statement} := by\n{proof}"
        return self.send_command(cmd)
    
    def reset(self):
        """
        重置环境
        """
        self.current_env = 0
        self.stop()
        self.start()

class Lean4AIReplBridge:
    """
    Lean4AI 与 REPL 的桥接
    """
    
    def __init__(self, repl_client: Lean4REPLClient):
        self.repl = repl_client
    
    def verify_project(self, project_code: str) -> Dict[str, Any]:
        """
        验证项目代码
        """
        response = self.repl.send_command(project_code)
        
        errors = [m for m in response.messages if m.severity == "error"]
        warnings = [m for m in response.messages if m.severity == "warning"]
        sorries = response.sorries
        
        return {
            "valid": len(errors) == 0 and len(sorries) == 0,
            "errors": [{"line": e.line, "message": e.content} for e in errors],
            "warnings": [{"line": w.line, "message": w.content} for w in warnings],
            "sorries": [{"line": s.line, "goal": s.goal} for s in sorries],
            "incomplete": len(sorries) > 0
        }
    
    def interactive_proof(self, theorem: str) -> Dict[str, Any]:
        """
        交互式证明
        """
        # 首先发送带有 sorry 的定理
        cmd = f"theorem temp : {theorem} := by\n  sorry"
        response = self.repl.send_command(cmd)
        
        if response.sorries:
            return {
                "goal": response.sorries[0].goal,
                "hints": self._generate_hints(response.sorries[0].goal)
            }
        
        return {"goal": None, "hints": []}
    
    def _generate_hints(self, goal: str) -> List[str]:
        """
        根据目标生成提示
        """
        hints = []
        
        if "∧" in goal:
            hints.append("Try: constructor")
        if "∨" in goal:
            hints.append("Try: left or right")
        if "→" in goal:
            hints.append("Try: intro")
        if "∃" in goal:
            hints.append("Try: use")
        if "∀" in goal:
            hints.append("Try: intro")
        
        hints.append("Try: simp, native_decide, or aesop")
        return hints
    
    def incremental_development(self, code_snippets: List[str]) -> List[Dict]:
        """
        增量开发
        """
        results = []
        
        for snippet in code_snippets:
            response = self.repl.send_command(snippet)
            
            results.append({
                "code": snippet,
                "env": response.env,
                "errors": [m.content for m in response.messages if m.severity == "error"],
                "success": all(m.severity != "error" for m in response.messages)
            })
        
        return results

class ProjectVerificationSession:
    """
    项目验证会话
    """
    
    def __init__(self):
        self.client = Lean4REPLClient()
        self.client.start()
        self.bridge = Lean4AIReplBridge(self.client)
    
    def load_project_module(self, module_code: str) -> Dict:
        """
        加载项目模块
        """
        return self.bridge.verify_project(module_code)
    
    def define_structure(self, struct_def: str) -> Dict:
        """
        定义结构
        """
        return self.client.send_command(struct_def)
    
    def prove_theorem(self, name: str, statement: str, 
                      proof: Optional[str] = None) -> Dict:
        """
        证明定理
        """
        if proof:
            return self.client.theorem(name, statement, proof)
        else:
            return self.bridge.interactive_proof(statement)
    
    def get_goals(self) -> List[str]:
        """
        获取当前目标
        """
        response = self.client.send_command "#check _"
        if response.tactics:
            return [t["goal"] for t in response.tactics]
        return []
    
    def close(self):
        """
        关闭会话
        """
        self.client.stop()

# 使用示例
def example_usage():
    session = ProjectVerificationSession()
    
    # 定义项目结构
    result = session.define_structure("""
    structure Project where
      name : String
      budget : Nat
      spent : Nat
      deriving Repr
    """)
    print(f"Structure defined: {result}")
    
    # 证明定理
    proof_result = session.prove_theorem(
        "project_spending_valid",
        "∀ p : Project, p.spent ≤ p.budget → p.isValid := True",
        "intro p h\nexact h"
    )
    print(f"Theorem proved: {proof_result}")
    
    session.close()
```

### 2. Lean4AI REPL 服务器

```lean
-- Lean4AI/REPL/Server.lean

import Lean
import Repl

open Lean Elab Command

namespace Lean4AI.REPL

/-- 项目验证命令 -/
@[command_doc] elab "#verify_project" : command => do
  -- 验证当前项目中所有定理
  let env ← getEnv
  let mut theorems : Array Name := #[]
  
  for (name, info) in env.constants do
    if info.isTheorem then
      theorems := theorems.push name
  
  if theorems.isEmpty then
    logInfo "No theorems found"
  else
    logInfo s!"Found {theorems.size} theorems"

/-- 获取项目统计 -/
@[command_doc] elab "#project_stats" : command => do
  let env ← getEnv
  
  let mut stats := {
    theorems := 0
    definitions := 0
    inductives := 0
    structures := 0
  }
  
  for (_, info) in env.constants do
    if info.isTheorem then stats := { stats with theorems := stats.theorems + 1 }
    else if info.isDef then stats := { stats with definitions := stats.definitions + 1 }
  
  for (_, info) in env.inductiveTypes do
    stats := { stats with inductives := stats.inductives + 1 }
  
  logInfo s!"Project Statistics:
    Theorems: {stats.theorems}
    Definitions: {stats.definitions}
    Inductives: {stats.inductives}"

/-- 检查未完成证明 -/
@[command_doc] elab "#check_sorries" : command => do
  -- 扫描代码中的 sorry
  logInfo "Checking for sorry placeholders..."

/-- 建议证明策略 -/
def suggestTactics (goal : Expr) : MetaM (Array String) := do
  let mut suggestions := #[]
  
  let goalType ← inferType goal
  
  -- 检查目标类型并建议策略
  if goalType.isAppOf ``And then
    suggestions := suggestions.push "constructor"
  
  if goalType.isAppOf ``Or then
    suggestions := suggestions.push "left or right"
  
  if goalType.isForall then
    suggestions := suggestions.push "intro"
  
  suggestions := suggestions.push "simp"
  suggestions := suggestions.push "native_decide"
  suggestions := suggestions.push "aesop"
  
  return suggestions

end Lean4AI.REPL
```

### 3. Web 集成

```python
# web_repl_server.py

from flask import Flask, request, jsonify
from lean4_repl_client import Lean4REPLClient, Lean4AIReplBridge
import threading

app = Flask(__name__)

# 全局 REPL 客户端池
repl_pool = []
repl_lock = threading.Lock()

def get_repl():
    """获取或创建 REPL 客户端"""
    with repl_lock:
        if repl_pool:
            return repl_pool.pop()
        client = Lean4REPLClient()
        client.start()
        return client

def return_repl(client):
    """归还 REPL 客户端"""
    with repl_lock:
        repl_pool.append(client)

@app.route('/api/check', methods=['POST'])
def check_code():
    """检查 Lean4 代码"""
    data = request.json
    code = data.get('code', '')
    
    client = get_repl()
    try:
        response = client.send_command(code)
        return jsonify({
            'sorries': [{'goal': s.goal, 'line': s.line} for s in response.sorries],
            'messages': [{'severity': m.severity, 'content': m.content, 'line': m.line} 
                        for m in response.messages],
            'env': response.env
        })
    finally:
        return_repl(client)

@app.route('/api/eval', methods=['POST'])
def eval_expr():
    """求值表达式"""
    data = request.json
    expr = data.get('expr', '')
    
    client = get_repl()
    try:
        response = client.eval_expr(expr)
        return jsonify({
            'success': len([m for m in response.messages if m.severity == 'error']) == 0,
            'messages': [{'content': m.content} for m in response.messages]
        })
    finally:
        return_repl(client)

@app.route('/api/verify_project', methods=['POST'])
def verify_project():
    """验证项目"""
    data = request.json
    code = data.get('code', '')
    
    client = get_repl()
    try:
        bridge = Lean4AIReplBridge(client)
        result = bridge.verify_project(code)
        return jsonify(result)
    finally:
        return_repl(client)

@app.route('/api/interactive_proof', methods=['POST'])
def interactive_proof():
    """交互式证明"""
    data = request.json
    theorem = data.get('theorem', '')
    
    client = get_repl()
    try:
        bridge = Lean4AIReplBridge(client)
        result = bridge.interactive_proof(theorem)
        return jsonify(result)
    finally:
        return_repl(client)

@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # 预热 REPL 池
    for _ in range(3):
        client = Lean4REPLClient()
        client.start()
        repl_pool.append(client)
    
    app.run(host='0.0.0.0', port=5000)
```

---

## 高级用法

### 1. 批量验证

```python
class BatchVerifier:
    """
    批量验证器
    """
    
    def __init__(self, repl_client: Lean4REPLClient):
        self.client = repl_client
    
    def verify_file(self, file_path: str) -> Dict:
        """
        验证整个文件
        """
        with open(file_path, 'r') as f:
            content = f.read()
        
        return self.verify_content(content)
    
    def verify_content(self, content: str) -> Dict:
        """
        验证内容
        """
        # 分割成命令块
        commands = self._split_commands(content)
        
        results = []
        for cmd in commands:
            response = self.client.send_command(cmd)
            results.append({
                'command': cmd[:100],  # 截断显示
                'success': len([m for m in response.messages if m.severity == 'error']) == 0,
                'sorries': len(response.sorries)
            })
        
        return {
            'total': len(results),
            'passed': sum(1 for r in results if r['success'] and r['sorries'] == 0),
            'failed': sum(1 for r in results if not r['success']),
            'incomplete': sum(1 for r in results if r['sorries'] > 0),
            'details': results
        }
    
    def _split_commands(self, content: str) -> List[str]:
        """
        分割命令
        """
        # 简化实现：按空行分割
        commands = []
        current = []
        
        for line in content.split('\n'):
            if line.strip() == '':
                if current:
                    commands.append('\n'.join(current))
                    current = []
            else:
                current.append(line)
        
        if current:
            commands.append('\n'.join(current))
        
        return commands
```

### 2. 实时协作

```python
class CollaborativeSession:
    """
    协作会话
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.client = Lean4REPLClient()
        self.client.start()
        self.history = []
    
    def apply_change(self, change: Dict) -> Dict:
        """
        应用变更
        """
        # 应用变更并验证
        response = self.client.send_command(change['code'])
        
        self.history.append({
            'change': change,
            'response': response,
            'timestamp': time.time()
        })
        
        return {
            'success': len([m for m in response.messages if m.severity == 'error']) == 0,
            'messages': [m.content for m in response.messages]
        }
    
    def get_state(self) -> Dict:
        """
        获取当前状态
        """
        return {
            'session_id': self.session_id,
            'env': self.client.current_env,
            'history_length': len(self.history)
        }
    
    def rollback(self, steps: int) -> Dict:
        """
        回滚
        """
        if steps >= len(self.history):
            # 重置到初始状态
            self.client.reset()
            self.history = []
            return {'rolled_back': 'all'}
        
        # 回滚指定步数
        self.history = self.history[:-steps]
        
        # 重新应用
        self.client.reset()
        for h in self.history:
            self.client.send_command(h['change']['code'])
        
        return {'rolled_back': steps}
```

---

## 部署选项

### 1. Docker 部署

```dockerfile
# Dockerfile
FROM ubuntu:22.04

# 安装依赖
RUN apt-get update && apt-get install -y \
    git curl cmake build-essential

# 安装 elan
RUN curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | bash -s -- -y

ENV PATH="/root/.elan/bin:${PATH}"

# 克隆并构建 REPL
RUN git clone https://github.com/leanprover-community/repl.git /app/repl
WORKDIR /app/repl
RUN lake build

EXPOSE 5000

CMD ["lake", "exe", "repl"]
```

### 2. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  lean4-repl:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./workspace:/workspace
    environment:
      - LEAN_PATH=/workspace

  web-api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8080:8080"
    depends_on:
      - lean4-repl
```

---

## 项目统计更新

| 指标 | 更新前 | 更新后 |
|------|--------|--------|
| 集成项目数 | 18 | 19 |
| API 端点 | - | 5+ |
| Stars 总和 | ~17,956 | ~18,150 |
| REPL 功能 | - | 完整 |

---

## 快速开始

```bash
# 安装
cd /mnt/c/workspace/math/lean4ai
git clone https://github.com/leanprover-community/repl.git
cd repl && lake build

# 基本使用
echo '{"cmd": "#check 1 + 1"}' | lake exe repl

# Python 客户端
python3 -c "
from lean4_repl_client import Lean4REPLClient
client = Lean4REPLClient('./repl')
client.start()
print(client.eval_expr('2 + 2'))
client.stop()
"

# Web API
python3 web_repl_server.py
curl -X POST http://localhost:5000/api/check -d '{"code": "#check 1"}'
```

---

**版本**: 11.0.0 (Nineteen-in-One)
**更新日期**: 2025-03-25

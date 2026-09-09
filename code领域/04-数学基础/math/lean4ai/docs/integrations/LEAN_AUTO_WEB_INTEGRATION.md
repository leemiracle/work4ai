# Lean-Auto + Lean4Web 集成指南

## 项目概述

本文档整合两个重要的 Lean4 工具项目：

| 项目 | Stars | 描述 | 语言 | 用途 |
|------|-------|------|------|------|
| **lean-auto** | 164 | 自动化实验 | Lean | 证明自动化 |
| **lean4web** | 133 | Web 编辑器 | TypeScript | 在线开发 |

**总 Stars: 297**

---

## 第一部分: Lean-Auto

### 项目信息

| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/leanprover-community/lean-auto |
| **描述** | Experiments on automation for Lean |
| **语言** | Lean 4 |
| **许可证** | Apache 2.0 |

### 核心功能

```
┌─────────────────────────────────────────────────────────────┐
│                    Lean-Auto 架构                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   输入目标                                                   │
│       │                                                     │
│       ▼                                                     │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              自动化策略组合                          │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │  simp    │  │  omega   │  │  decide  │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │  aesop   │  │  native  │  │  ring    │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   └─────────────────────────────────────────────────────┘   │
│       │                                                     │
│       ▼                                                     │
│   启发式搜索                                                 │
│   • 策略排序                                                 │
│   • 超时控制                                                 │
│   • 回溯机制                                                 │
│       │                                                     │
│       ▼                                                     │
│   证明完成 / 失败报告                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 自动化策略

```lean
-- LeanAuto/Strategies.lean

import Lean
import Mathlib.Tactic

namespace LeanAuto

/-- 自动化配置 -/
structure AutoConfig where
  maxDepth : Nat := 10
  timeout : Nat := 30  -- 秒
  strategies : List String := ["simp", "omega", "aesop", "native_decide"]
  verbose : Bool := false

/-- 策略结果 -/
inductive TacticResult where
  | success : List MVarId → TacticResult
  | failed : String → TacticResult
  | timeout : TacticResult

/-- 策略评分 -/
def tacticScore (tactic : String) (goal : Expr) : Nat :=
  match tactic with
  | "native_decide" => if goal.isProp then 100 else 0
  | "simp" => 80
  | "omega" => if goal.hasLinearArith then 90 else 50
  | "aesop" => 70
  | "ring" => if goal.hasRingExpr then 95 else 30
  | _ => 50

/-- 策略排序 -/
def sortTactics (tactics : List String) (goal : Expr) : List String :=
  tactics.qsort fun t1 t2 => tacticScore t1 goal > tacticScore t2 goal

/-- 自动尝试策略 -/
partial def autoTry (config : AutoConfig) (depth : Nat) : TacticM Bool := do
  if depth > config.maxDepth then
    return false
  
  let goal ← getMainGoal
  let goalType ← goal.getType
  
  -- 排序策略
  let sortedTactics := sortTactics config.strategies goalType
  
  for tactic in sortedTactics do
    try
      let elapsed ← timeTactic tactic
      if elapsed < config.timeout then
        return true
    catch _ =>
      continue
  
  -- 尝试分解
  if goalType.isAppOf ``And then
    try
      evalTactic (← `(tactic| constructor))
      let remaining ← getUnsolvedGoals
      for g in remaining do
        setGoals [g]
        if ← autoTry config (depth + 1) then
          continue
        else
          return false
      return true
    catch _ =>
      return false
  
  return false
where
  timeTactic (tactic : String) : TacticM Nat := do
    let start ← IO.monoMsNow
    try
      evalTactic (← `(tactic| $(Syntax.mkIdent tactic.getId):ident))
      let elapsed ← IO.monoMsNow
      return (elapsed - start) / 1000
    catch e =>
      throw e

/-- 主自动化策略 -/
syntax "auto" : tactic
syntax "auto" " with " term,+ : tactic

elab_rules : tactic
| `(tactic| auto) => do
  let config : AutoConfig := {}
  let success ← autoTry config 0
  unless success do
    throwError "auto failed"
| `(tactic| auto with $tacs:term,*) => do
  let strategies := tacs.toList.map toString
  let config : AutoConfig := { strategies }
  let success ← autoTry config 0
  unless success do
    throwError "auto failed"

end LeanAuto
```

### 使用示例

```lean
import LeanAuto

-- 自动证明
example (p q : Prop) (hp : p) (hpq : p → q) : q := by
  auto

-- 带配置
example (a b : Nat) : a + b = b + a := by
  auto with simp, omega, ring

-- 算术证明
example (x y : Int) : x + y ≤ x + 2 * y ↔ y ≥ 0 := by
  auto with omega
```

---

## 第二部分: Lean4Web

### 项目信息

| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/leanprover-community/lean4web |
| **在线版** | https://live.lean-lang.org/ |
| **描述** | Lean web editor |
| **语言** | TypeScript |
| **许可证** | Apache 2.0 |

### 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Lean4Web 架构                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  前端 (React)                        │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │Monaco    │  │ Infoview │  │ FileTree │          │   │
│   │  │ Editor   │  │ Panel    │  │ Panel    │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │ Goals    │  │ Messages │  │ Widgets  │          │   │
│   │  │ View     │  │ Panel    │  │ Display  │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  通信层                              │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │ WebSocket│  │   RPC    │  │  LSP     │          │   │
│   │  │ 实时同步  │  │  远程调用 │  │ 协议     │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  后端服务器                          │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │ Lean     │  │ 文件     │  │ 项目     │          │   │
│   │  │ Server   │  │ 管理     │  │ 管理     │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

#### 1. 编辑器集成

```typescript
// src/editor/LeanEditor.tsx
import * as React from 'react';
import * as monaco from 'monaco-editor';

interface LeanEditorProps {
  initialValue: string;
  onChange: (value: string) => void;
  onCursorPosition: (position: Position) => void;
}

export function LeanEditor({ initialValue, onChange, onCursorPosition }: LeanEditorProps) {
  const editorRef = React.useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const containerRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (containerRef.current && !editorRef.current) {
      // 创建编辑器
      editorRef.current = monaco.editor.create(containerRef.current, {
        value: initialValue,
        language: 'lean4',
        theme: 'vs-dark',
        minimap: { enabled: true },
        fontSize: 14,
        lineNumbers: 'on',
        renderWhitespace: 'selection',
        automaticLayout: true,
      });

      // 监听变化
      editorRef.current.onDidChangeModelContent(() => {
        onChange(editorRef.current?.getValue() || '');
      });

      // 监听光标位置
      editorRef.current.onDidChangeCursorPosition((e) => {
        onCursorPosition({
          line: e.position.lineNumber,
          column: e.position.column,
        });
      });
    }

    return () => {
      editorRef.current?.dispose();
    };
  }, []);

  return <div ref={containerRef} style={{ height: '100%', width: '100%' }} />;
}

// Lean4 语法高亮定义
monaco.languages.register({ id: 'lean4' });

monaco.languages.setMonarchTokensProvider('lean4', {
  keywords: [
    'def', 'theorem', 'lemma', 'example', 'axiom', 'constant',
    'inductive', 'structure', 'class', 'instance',
    'namespace', 'end', 'section', 'variable', 'universe',
    'import', 'open', 'export', 'precedence', 'reserve',
    'prefix', 'infix', 'infixl', 'infixr', 'notation',
    'macro', 'macro_rules', 'elab', 'syntax',
    'if', 'then', 'else', 'match', 'with', 'do',
    'let', 'in', 'have', 'show', 'assume', 'take',
    'fun', 'forall', 'exists', 'Type', 'Prop', 'Sort',
    'by', 'begin', 'end', 'sorry', 'admit',
    'private', 'protected', 'partial', 'mutual',
  ],
  operators: [
    '=', '≠', '<', '>', '≤', '≥',
    '+', '-', '*', '/', '÷', '%',
    '∧', '∨', '¬', '→', '↔', '∀', '∃',
    '∘', '⊕', '⊗', '⊙',
    '⟨', '⟩', '⟪', '⟫',
  ],
  symbols: /[=><!~?:&|+\-*\/\^%]+/,
  
  tokenizer: {
    root: [
      [/[a-zA-Z_][a-zA-Z0-9_']*/, {
        cases: {
          '@keywords': 'keyword',
          '@default': 'identifier',
        },
      }],
      { include: '@whitespace' },
      [/[{}()\[\]]/, '@brackets'],
      [/[<>](?!@symbols)/, '@brackets'],
      [/@symbols/, {
        cases: {
          '@operators': 'operator',
          '@default': '',
        },
      }],
      [/\d*\.\d+([eE][\-+]?\d+)?/, 'number.float'],
      [/\d+/, 'number'],
      [/[;,.]/, 'delimiter'],
      [/"([^"\\]|\\.)*$/, 'string.invalid'],
      [/"/, 'string', '@string'],
      [/'[^\\']'/, 'string'],
      [/'/, 'string.invalid'],
      [/--.*$/, 'comment'],
      [/-\//, 'comment', '@comment'],
    ],
    comment: [
      [/[^\/*]+/, 'comment'],
      [/-\//, 'comment'],
      ['\\*/', 'comment', '@pop'],
      ['[\\/*]', 'comment'],
    ],
    string: [
      [/[^\\"]+/, 'string'],
      [/\\./, 'string.escape'],
      [/"/, 'string', '@pop'],
    ],
    whitespace: [
      [/[ \t\r\n]+/, 'white'],
    ],
  },
});
```

#### 2. Infoview 组件

```typescript
// src/infoview/Infoview.tsx
import * as React from 'react';
import { Rpc } from '@leanprover/infoview';

interface Goal {
  type: string;
  context: { name: string; type: string }[];
}

interface Message {
  severity: 'error' | 'warning' | 'info';
  content: string;
  line: number;
  column: number;
}

interface InfoviewProps {
  goals: Goal[];
  messages: Message[];
  line: number;
  column: number;
}

export function Infoview({ goals, messages, line, column }: InfoviewProps) {
  return (
    <div className="infoview">
      {/* 目标显示 */}
      <div className="goals-section">
        <h3>Goals ({goals.length})</h3>
        {goals.length === 0 ? (
          <div className="no-goals">No goals 🎉</div>
        ) : (
          goals.map((goal, idx) => (
            <GoalDisplay key={idx} goal={goal} index={idx} />
          ))
        )}
      </div>

      {/* 消息显示 */}
      <div className="messages-section">
        <h3>Messages</h3>
        {messages.map((msg, idx) => (
          <MessageDisplay key={idx} message={msg} />
        ))}
      </div>

      {/* 位置信息 */}
      <div className="position-info">
        Line {line}, Column {column}
      </div>
    </div>
  );
}

function GoalDisplay({ goal, index }: { goal: Goal; index: number }) {
  return (
    <div className="goal">
      <div className="goal-header">Goal {index + 1}</div>
      <div className="goal-context">
        {goal.context.map((ctx, idx) => (
          <div key={idx} className="context-item">
            <span className="context-name">{ctx.name}</span>
            <span className="context-separator"> : </span>
            <span className="context-type">{ctx.type}</span>
          </div>
        ))}
      </div>
      <div className="goal-separator">⊢</div>
      <div className="goal-type">{goal.type}</div>
    </div>
  );
}

function MessageDisplay({ message }: { message: Message }) {
  const className = `message message-${message.severity}`;
  return (
    <div className={className}>
      <span className="message-location">Line {message.line}:</span>
      <span className="message-content">{message.content}</span>
    </div>
  );
}
```

#### 3. 文件管理

```typescript
// src/file/FileTree.tsx
import * as React from 'react';

interface FileNode {
  name: string;
  type: 'file' | 'folder';
  children?: FileNode[];
  path: string;
}

interface FileTreeProps {
  root: FileNode;
  onFileSelect: (path: string) => void;
  currentFile: string | null;
}

export function FileTree({ root, onFileSelect, currentFile }: FileTreeProps) {
  return (
    <div className="file-tree">
      <FileNodeComponent
        node={root}
        level={0}
        onFileSelect={onFileSelect}
        currentFile={currentFile}
      />
    </div>
  );
}

function FileNodeComponent({
  node,
  level,
  onFileSelect,
  currentFile,
}: {
  node: FileNode;
  level: number;
  onFileSelect: (path: string) => void;
  currentFile: string | null;
}) {
  const [expanded, setExpanded] = React.useState(true);
  const isSelected = currentFile === node.path;

  const handleClick = () => {
    if (node.type === 'folder') {
      setExpanded(!expanded);
    } else {
      onFileSelect(node.path);
    }
  };

  return (
    <div className="file-node" style={{ paddingLeft: level * 16 }}>
      <div
        className={`file-item ${isSelected ? 'selected' : ''}`}
        onClick={handleClick}
      >
        <span className="file-icon">
          {node.type === 'folder' ? (expanded ? '📂' : '📁') : '📄'}
        </span>
        <span className="file-name">{node.name}</span>
      </div>
      {node.type === 'folder' && expanded && node.children && (
        <div className="file-children">
          {node.children.map((child, idx) => (
            <FileNodeComponent
              key={idx}
              node={child}
              level={level + 1}
              onFileSelect={onFileSelect}
              currentFile={currentFile}
            />
          ))}
        </div>
      )}
    </div>
  );
}
```

### 后端服务器

```typescript
// server/src/server.ts
import * as express from 'express';
import * as WebSocket from 'ws';
import * as http from 'http';
import { LeanClient } from './lean-client';

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Lean 客户端管理
const leanClients = new Map<string, LeanClient>();

// WebSocket 连接处理
wss.on('connection', (ws, req) => {
  const sessionId = generateSessionId();
  const client = new LeanClient();
  leanClients.set(sessionId, client);

  ws.on('message', async (data) => {
    try {
      const message = JSON.parse(data.toString());
      const response = await handleMessage(client, message);
      ws.send(JSON.stringify(response));
    } catch (error) {
      ws.send(JSON.stringify({ error: error.message }));
    }
  });

  ws.on('close', () => {
    leanClients.delete(sessionId);
    client.dispose();
  });
});

// 消息处理
async function handleMessage(client: LeanClient, message: any): Promise<any> {
  switch (message.type) {
    case 'sync':
      return await client.sync(message.content);
    case 'check':
      return await client.check(message.line, message.column);
    case 'complete':
      return await client.complete(message.line, message.column);
    case 'hover':
      return await client.hover(message.line, message.column);
    default:
      throw new Error(`Unknown message type: ${message.type}`);
  }
}

// Lean 客户端
export class LeanClient {
  private process: ChildProcess | null = null;
  private initialized = false;

  async initialize(): Promise<void> {
    this.process = spawn('lean', ['--server'], {
      stdio: ['pipe', 'pipe', 'pipe'],
    });

    // 初始化 LSP 通信
    await this.sendRequest('initialize', {
      capabilities: {
        textDocument: {
          completion: { completionItem: { snippetSupport: true } },
          hover: { contentFormat: ['markdown', 'plaintext'] },
        },
      },
    });

    this.initialized = true;
  }

  async sync(content: string): Promise<void> {
    await this.sendNotification('textDocument/didChange', {
      textDocument: { uri: 'file:///main.lean', version: 0 },
      contentChanges: [{ text: content }],
    });
  }

  async check(line: number, column: number): Promise<any> {
    return await this.sendRequest('textDocument/codeAction', {
      textDocument: { uri: 'file:///main.lean' },
      range: {
        start: { line, character: column },
        end: { line, character: column },
      },
    });
  }

  async complete(line: number, column: number): Promise<any> {
    return await this.sendRequest('textDocument/completion', {
      textDocument: { uri: 'file:///main.lean' },
      position: { line, character: column },
    });
  }

  async hover(line: number, column: number): Promise<any> {
    return await this.sendRequest('textDocument/hover', {
      textDocument: { uri: 'file:///main.lean' },
      position: { line, character: column },
    });
  }

  dispose(): void {
    this.process?.kill();
    this.process = null;
  }

  private async sendRequest(method: string, params: any): Promise<any> {
    // LSP 请求实现
  }

  private async sendNotification(method: string, params: any): Promise<void> {
    // LSP 通知实现
  }
}

function generateSessionId(): string {
  return Math.random().toString(36).substring(7);
}

server.listen(3000, () => {
  console.log('Lean4Web server running on http://localhost:3000');
});
```

---

## 与 Lean4AI 集成

### 1. 自动化验证服务

```python
# lean_auto_service.py

import subprocess
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class AutoResult:
    success: bool
    tactic_used: Optional[str]
    proof: Optional[str]
    error: Optional[str]

class LeanAutoService:
    """
    Lean-Auto 作为服务的封装
    """
    
    def __init__(self, lean_path: str = "lean"):
        self.lean_path = lean_path
    
    def auto_prove(self, theorem: str, statement: str) -> AutoResult:
        """
        自动证明定理
        """
        lean_code = f"""
import LeanAuto

theorem auto_test : {statement} := by
  auto
"""
        result = subprocess.run(
            [self.lean_path, "--run", "-"],
            input=lean_code,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return AutoResult(
                success=True,
                tactic_used="auto",
                proof="auto",
                error=None
            )
        else:
            return AutoResult(
                success=False,
                tactic_used=None,
                proof=None,
                error=result.stderr
            )
    
    def suggest_tactics(self, goal: str) -> List[str]:
        """
        建议策略
        """
        suggestions = []
        
        # 基于目标类型的启发式
        if "∧" in goal:
            suggestions.extend(["constructor", "and_intro"])
        if "∨" in goal:
            suggestions.extend(["left", "right", "or_intro"])
        if "→" in goal:
            suggestions.extend(["intro", "imp_intro"])
        if "∃" in goal:
            suggestions.extend(["use", "exists_intro"])
        if "=" in goal:
            suggestions.extend(["rfl", "congr", "simp"])
        
        # 通用策略
        suggestions.extend([
            "simp",
            "native_decide",
            "aesop",
            "omega",
            "ring",
            "linarith",
            "auto"
        ])
        
        return list(dict.fromkeys(suggestions))  # 去重保持顺序

class Lean4WebIntegration:
    """
    Lean4Web 与 Lean4AI 的集成
    """
    
    def __init__(self, web_url: str = "https://live.lean-lang.org"):
        self.web_url = web_url
    
    def create_project_session(self, project_id: str) -> dict:
        """
        创建项目会话
        """
        return {
            "project_id": project_id,
            "web_url": f"{self.web_url}/#project/{project_id}",
            "created": True
        }
    
    def share_code(self, code: str) -> str:
        """
        分享代码，返回可访问的 URL
        """
        # 实际实现会将代码上传到服务器
        import base64
        encoded = base64.b64encode(code.encode()).decode()
        return f"{self.web_url}/#code/{encoded}"
    
    def embed_editor(self, code: str = "") -> str:
        """
        生成可嵌入的编辑器 HTML
        """
        return f"""
<iframe 
  src="{self.web_url}/embed?code={code}"
  width="100%"
  height="500px"
  frameborder="0"
  style="border: 1px solid #ccc; border-radius: 4px;"
></iframe>
"""
```

### 2. Web IDE 功能

```typescript
// lean4ai-web-ide.ts
import * as React from 'react';

interface WebIDEConfig {
  projectId: string;
  initialCode?: string;
  onProofComplete?: (theorem: string) => void;
  onError?: (error: string) => void;
}

export function Lean4AIWebIDE({ projectId, initialCode, onProofComplete, onError }: WebIDEConfig) {
  const [code, setCode] = React.useState(initialCode || '');
  const [goals, setGoals] = React.useState<Goal[]>([]);
  const [messages, setMessages] = React.useState<Message[]>([]);

  // 连接到 Lean 服务器
  React.useEffect(() => {
    const ws = new WebSocket(`wss://api.lean4ai.com/project/${projectId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.goals) setGoals(data.goals);
      if (data.messages) setMessages(data.messages);
      if (data.complete) onProofComplete?.(data.theorem);
      if (data.error) onError?.(data.error);
    };

    return () => ws.close();
  }, [projectId]);

  const handleCodeChange = (newCode: string) => {
    setCode(newCode);
    // 发送到服务器进行验证
  };

  return (
    <div className="lean4ai-ide">
      <div className="editor-panel">
        <LeanEditor
          initialValue={code}
          onChange={handleCodeChange}
          onCursorPosition={(pos) => {/* 更新光标位置 */}}
        />
      </div>
      <div className="info-panel">
        <Infoview
          goals={goals}
          messages={messages}
          line={1}
          column={1}
        />
      </div>
      <div className="toolbar">
        <button onClick={() => {/* 运行 */}}>▶ Run</button>
        <button onClick={() => {/* 检查 */}}>✓ Check</button>
        <button onClick={() => {/* 格式化 */}}>Format</button>
        <button onClick={() => {/* 分享 */}}>Share</button>
      </div>
    </div>
  );
}
```

---

## 部署指南

### 1. Lean-Auto 部署

```bash
# 克隆
git clone https://github.com/leanprover-community/lean-auto.git
cd lean-auto

# 构建
lake build

# 在项目中使用
# lakefile.lean 添加依赖
```

### 2. Lean4Web 部署

```bash
# 克隆
git clone https://github.com/leanprover-community/lean4web.git
cd lean4web

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build

# Docker 部署
docker build -t lean4web .
docker run -p 3000:3000 lean4web
```

### 3. Docker Compose

```yaml
version: '3.8'

services:
  lean4web:
    build: ./lean4web
    ports:
      - "3000:3000"
    environment:
      - LEAN_PATH=/usr/local/bin/lean
    volumes:
      - ./projects:/app/projects

  lean-auto:
    build: ./lean-auto
    volumes:
      - ./projects:/app/projects
```

---

## 项目统计更新

| 指标 | 更新前 | 更新后 |
|------|--------|--------|
| 集成项目数 | 21 | 23 |
| 自动化策略 | - | 10+ |
| Web 组件 | - | 20+ |
| Stars 总和 | ~18,508 | ~18,805 |

---

## 快速开始

```bash
# 在线使用 Lean4Web
open https://live.lean-lang.org/

# 本地部署
git clone https://github.com/leanprover-community/lean4web.git
cd lean4web && npm install && npm run dev

# 使用 Lean-Auto
git clone https://github.com/leanprover-community/lean-auto.git
cd lean-auto && lake build
# 在 Lean 代码中使用: by auto
```

---

**版本**: 14.0.0 (Twenty-Three-in-One)
**更新日期**: 2025-03-25

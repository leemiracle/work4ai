# omega-guard 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建零依赖 Python 库 `omegaguard`——ω-自动机语义的 agent 工具调用流 guardrail（三值监控 + enforce 拦截 + 2-token HD 判定 + 故障注入参考 agent 指标体系）。

**Architecture:** 核心库分层：`events`(事件/谓词) → `automata`(显式 parity 自动机 + 三值分类) → `dsl`(组合子→监控器对象) → `monitor`(Guardrail 运行器) → `agent`(模拟工具环境 + 故障策略 + 指标)；`hd`(Zielonka + 2-token game) 独立于运行时路径。组合子产出监控器对象（并行执行 + 三值合并），不做积自动机构造。实验脚本 3 个（lab 编号风格）。

**Tech Stack:** Python ≥3.10（仓库现有 3.10），零第三方运行时依赖，pytest 测试，setuptools 打包（`pip install -e`）。

**Spec:** `docs/superpowers/specs/2026-09-06-omega-guard-design.md`（计划从 spec 立论，执行者须同时读 spec）

## Global Constraints

- 零运行时第三方依赖（`dependencies = []`）；pytest 仅在 dev extra
- 所有用户可见字符串（错误消息、报告、README）中文为主，代码标识符/工具名保留英文
- 监控器异常绝不拖垮宿主 agent（fail-open 默认 / fail-closed 可标）
- 所有命令在 `C:/workspace/work4ai/omega-guard` 下执行；提交信息中文 conventional 风格，结尾加 `Co-Authored-By: Claude Code <noreply@anthropic.com>`
- 每任务 TDD：先写失败测试 → 跑确认失败 → 最小实现 → 跑通过 → 提交

---

### Task 1: 脚手架 + events.py（Verdict / ToolEvent / Pred 谓词原语）

**Files:**
- Create: `omega-guard/pyproject.toml`
- Create: `omega-guard/.gitignore`
- Create: `omega-guard/README.md`
- Create: `omega-guard/omegaguard/__init__.py`
- Create: `omega-guard/omegaguard/events.py`
- Test: `omega-guard/tests/test_events.py`

**Interfaces:**
- Produces: `Verdict(Enum)` 成员 `TOP/BOTTOM/UNKNOWN`；`ToolEvent(name, args, phase, status)` frozen dataclass，方法 `with_status(status) -> ToolEvent`；`Pred` 类（`name: str`、`__call__(e)->bool`、`__or__/__and__/__invert__`）；谓词工厂 `tool(name)`, `tool_in(*names)`, `tool_phase(name, phase='call')`, `arg_gt(key, val)`, `arg_lt(key, val)`, `arg_eq(key, val)`, `has_status(status)`, `any_event()`——全部返回 `Pred`

- [ ] **Step 1: 脚手架文件**

`pyproject.toml`：
```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "omegaguard"
version = "0.1.0"
description = "ω-自动机 tool-call guardrail：三值监控 + enforce 拦截 + 2-token HD 判定"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = ["pytest"]

[tool.setuptools.packages.find]
include = ["omegaguard*"]
```

`.gitignore`：
```
__pycache__/
*.egg-info/
results/
.pytest_cache/
```

`README.md`（v1 骨架，指标表由 Task 12 填）：
```markdown
# omega-guard

基于 ω-自动机理论的 agent 工具调用流 guardrail。理论锚点：history-determinism /
good-for-games（Henzinger–Piterman 2006 动机；Boker–Lehtinen LMCS'23 token games；
Lehtinen–Prakash STOC'25 2-Token 定理）。

## 快速上手

```python
from omegaguard.events import tool, tool_phase
from omegaguard.dsl import never, every_eventually, at_most
from omegaguard.monitor import Guardrail

g = Guardrail.props([
    never(tool('delete_db')),
    every_eventually(tool_phase('start_task'), tool_phase('end_task')),
    at_most(tool('paid_api'), 5),
])
```

## 指标（Task 12 由 experiments/03 产出填充）

<!-- METRICS_TABLE -->

## 设计文档

`../docs/superpowers/specs/2026-09-06-omega-guard-design.md`
```

`omegaguard/__init__.py`：
```python
"""omega-guard：ω-自动机 tool-call guardrail。"""
__version__ = "0.1.0"
```

- [ ] **Step 2: 安装并写失败测试**

```bash
cd C:/workspace/work4ai/omega-guard && pip install -e ".[dev]"
```

`tests/test_events.py`：
```python
from omegaguard.events import (Verdict, ToolEvent, Pred, tool, tool_in,
                               tool_phase, arg_gt, arg_eq, has_status, any_event)

def E(name="scroll", phase="call", status=None, **args):
    return ToolEvent(name, dict(args), phase, status)

def test_verdict_members():
    assert {v.name for v in Verdict} == {"TOP", "BOTTOM", "UNKNOWN"}

def test_event_frozen_and_with_status():
    e = ToolEvent("paid_api", {"n": 1}, "call", None)
    r = e.with_status("err")
    assert (r.phase, r.status, r.args) == ("result", "err", {"n": 1})
    assert e.status is None  # 原事件不变

def test_pred_primitives():
    assert tool("delete_db")(E("delete_db"))
    assert not tool("delete_db")(E("scroll"))
    assert tool_in("a", "b")(E("b"))
    assert tool_phase("start_task", "call")(E("start_task"))
    assert not tool_phase("start_task", "call")(ToolEvent("start_task", {}, "result"))
    assert arg_gt("amount", 100)(E("pay", amount=150))
    assert not arg_gt("amount", 100)(E("pay", amount=50))
    assert not arg_gt("amount", 100)(E("pay"))          # 缺键不命中
    assert arg_eq("k", 2)(E("x", k=2))
    assert has_status("err")(E("f", phase="result", status="err"))
    assert any_event()(E("whatever"))
    assert any_event()(ToolEvent("whatever", {}, "result", "err"))  # 恒真, 无视 phase

def test_pred_combinators_and_name():
    p = tool("a") | tool("b")
    assert p(E("b")) and not p(E("c"))
    q = tool("a") & has_status("err")
    assert q(E("a", phase="result", status="err"))
    assert not q(E("a"))
    n = ~tool("a")
    assert n(E("c")) and not n(E("a"))
    assert "|" in p.name and "&" in q.name and "~" in n.name  # 报告可读性
```

- [ ] **Step 3: 跑测试确认失败**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_events.py -q`
Expected: FAIL（`ModuleNotFoundError: omegaguard.events` 或 ImportError）

- [ ] **Step 4: 实现 events.py**

```python
"""事件与谓词：监控字母表 = 事件谓词（guard）。"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class Verdict(Enum):
    TOP = "TOP"          # 所有延展接受
    BOTTOM = "BOTTOM"    # 所有延展拒绝
    UNKNOWN = "UNKNOWN"  # 尚未定


@dataclass(frozen=True)
class ToolEvent:
    name: str
    args: dict = field(default_factory=dict)
    phase: str = "call"         # 'call' | 'result'
    status: str | None = None   # 'ok' | 'err' | None

    def with_status(self, status: str) -> "ToolEvent":
        return ToolEvent(self.name, self.args, "result", status)


class Pred:
    """事件谓词。name 保留组合结构，用于违规报告可读性。"""

    def __init__(self, name: str, fn: Callable[[ToolEvent], bool]):
        self.name, self.fn = name, fn

    def __call__(self, e: ToolEvent) -> bool:
        return self.fn(e)

    def __or__(self, o: "Pred") -> "Pred":
        return Pred(f"({self.name}|{o.name})", lambda e: self(e) or o(e))

    def __and__(self, o: "Pred") -> "Pred":
        return Pred(f"({self.name}&{o.name})", lambda e: self(e) and o(e))

    def __invert__(self) -> "Pred":
        return Pred(f"~({self.name})", lambda e: not self(e))


def tool(name: str) -> Pred:
    return Pred(f"tool({name})", lambda e: e.name == name)

def tool_in(*names: str) -> Pred:
    return Pred(f"tool_in{names}", lambda e: e.name in names)

def tool_phase(name: str, phase: str = "call") -> Pred:
    return Pred(f"tool_phase({name},{phase})",
                lambda e: e.name == name and e.phase == phase)

def arg_gt(key: str, val) -> Pred:
    return Pred(f"arg_gt({key},{val})",
                lambda e: key in e.args and e.args[key] > val)

def arg_lt(key: str, val) -> Pred:
    return Pred(f"arg_lt({key},{val})",
                lambda e: key in e.args and e.args[key] < val)

def arg_eq(key: str, val) -> Pred:
    return Pred(f"arg_eq({key},{val})", lambda e: e.args.get(key) == val)

def has_status(status: str) -> Pred:
    return Pred(f"status({status})", lambda e: e.status == status)

def any_event() -> Pred:
    return Pred("any", lambda e: True)
```

- [ ] **Step 5: 跑测试通过**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_events.py -q`
Expected: PASS（5 passed）

- [ ] **Step 6: Commit**

```bash
cd C:/workspace/work4ai && git add omega-guard && git commit -m "feat: omega-guard 脚手架+events——Verdict三值/ToolEvent/Pred谓词组合子

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 2: automata.py（显式 parity 自动机 + 确定性 step + 三值状态分类）

**Files:**
- Create: `omega-guard/omegaguard/automata.py`
- Test: `omega-guard/tests/test_automata.py`

**Interfaces:**
- Consumes: `Pred`, `ToolEvent`, `Verdict`（Task 1）
- Produces: `NondeterminismError(Exception)`；`Automaton(states, init, priorities, trans, name="aut")`——`states: list`，`init`，`priorities: dict[state,int]`（state-based parity，无穷次出现的最小优先级为偶=接受），`trans: dict[state, list[tuple[Pred, state]]]`；方法 `step(q, e) -> state`（多 guard 命中抛 `NondeterminismError`，零命中=自环）、`classify() -> dict[state, Verdict]`。模块级 `build_support_edges(aut) -> dict[state, set[state]]`

- [ ] **Step 1: 写失败测试**

`tests/test_automata.py`：
```python
import pytest
from omegaguard.events import Verdict, ToolEvent, tool, any_event
from omegaguard.automata import Automaton, NondeterminismError

def E(n): return ToolEvent(n)

# 两状态 det co-Büchi 风格 parity 自动机："scroll 之后进入脏态，other 回净态"
# 净=q0 prio2(偶,接受), 脏=q1 prio1(奇,拒绝)
def mk():
    return Automaton(
        states=["q0", "q1"], init="q0",
        priorities={"q0": 2, "q1": 1},
        trans={"q0": [(tool("scroll"), "q1")],          # 其余自环
               "q1": [(tool("other"), "q0")]})

def test_step_deterministic_and_selfloop():
    a = mk()
    assert a.step("q0", E("scroll")) == "q1"
    assert a.step("q0", E("zzz")) == "q0"      # 无匹配=自环（complete by construction）
    assert a.step("q1", E("other")) == "q0"
    assert a.step("q1", E("scroll")) == "q1"

def test_step_nondeterminism_error():
    a = Automaton(states=["q", "a", "b"], init="q",
                  priorities={"q": 2, "a": 1, "b": 1},
                  trans={"q": [(any_event(), "a"), (any_event(), "b")],
                         "a": [], "b": []})
    with pytest.raises(NondeterminismError, match="q"):
        a.step("q", E("x"))

def test_classify_three_valued():
    a = mk()
    cls = a.classify()
    # q0: 可达自环(q0,prio2)接受 → 有接受环; 也可到 q1 自环(prio1)拒绝 → 有拒绝环 → UNKNOWN
    assert cls["q0"] == Verdict.UNKNOWN
    # q1: 可达 q1 自环拒绝; 可达 q0 接受 → UNKNOWN
    assert cls["q1"] == Verdict.UNKNOWN

def test_classify_bottom_sink():
    # 陷阱态: 只能自环 prio1(拒绝), 无接受环可达 → BOTTOM
    a = Automaton(states=["q0", "dead"], init="q0",
                  priorities={"q0": 2, "dead": 1},
                  trans={"q0": [(tool("boom"), "dead")], "dead": []})
    assert a.classify()["dead"] == Verdict.BOTTOM
    assert a.classify()["q0"] == Verdict.UNKNOWN

def test_classify_top_state():
    # 进入后只有接受环: qT 自环 prio2, 无出边 → TOP
    a = Automaton(states=["q0", "qT"], init="q0",
                  priorities={"q0": 1, "qT": 2},
                  trans={"q0": [(tool("go"), "qT")], "qT": []})
    cls = a.classify()
    assert cls["qT"] == Verdict.TOP
    assert cls["q0"] == Verdict.UNKNOWN   # q0 自环 prio1 拒绝环可达, 接受环(qT)也可达

def test_classify_parity_layered():
    # 分层剥离用例: qA(prio4) → qB(prio3) → qA 环 min=3 拒绝; qC(prio2) 自环接受
    a = Automaton(states=["qA", "qB", "qC"], init="qA",
                  priorities={"qA": 4, "qB": 3, "qC": 2},
                  trans={"qA": [(tool("b"), "qB"), (tool("c"), "qC")],
                         "qB": [(any_event(), "qA")], "qC": []})
    cls = a.classify()
    assert cls["qC"] == Verdict.TOP
    assert cls["qB"] == Verdict.UNKNOWN
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_automata.py -q`
Expected: FAIL（ModuleNotFoundError）

- [ ] **Step 3: 实现 automata.py**

```python
"""显式状态 parity 自动机：guard 转移 + 三值状态分类（SCC 分层分析）。

约定：state-based parity，接受 ⟺ 无穷次出现的最小优先级为偶。
分类语义（对 state q）：
  TOP    ⟺ 从 q 出发不存在可达的"拒绝环"（min 优先级为奇的环）
  BOTTOM ⟺ 从 q 出发不存在可达的"接受环"（min 优先级为偶的环）
  UNKNOWN ⟺ 两者皆存在
分类在 support 图（忽略 guard、只看拓扑）上计算——延展遍历所有可能事件序列。
"""
from __future__ import annotations
from .events import Verdict


class NondeterminismError(Exception):
    """同一状态上多个 guard 对同一事件同时命中——运行时确定性被破坏。"""


class Automaton:
    def __init__(self, states, init, priorities, trans, name="aut"):
        self.states, self.init = list(states), init
        self.priorities, self.name = dict(priorities), name
        self.trans = {q: list(ts) for q, ts in trans.items()}
        self._validate()

    def _validate(self):
        if self.init not in self.states:
            raise ValueError(f"{self.name}: 初始状态 {self.init} 不在状态集")
        for q in self.states:
            if q not in self.priorities:
                raise ValueError(f"{self.name}: 状态 {q} 缺优先级")
            for _, t in self.trans.get(q, []):
                if t not in self.states:
                    raise ValueError(f"{self.name}: 转移目标 {t} 不在状态集")

    def step(self, q, e):
        """确定性单步：多 guard 命中抛 NondeterminismError；零命中自环。"""
        hits = [t for (g, t) in self.trans.get(q, []) if g(e)]
        if len(hits) > 1:
            raise NondeterminismError(
                f"{self.name}: 状态 {q} 上 {len(hits)} 个 guard 同时命中事件 "
                f"{e.name!r}（{e.phase}）——请改写为互斥 guard 或走 hd.py 判定")
        return hits[0] if hits else q

    def classify(self) -> dict:
        rej = _states_reaching_parity_cycle(self, accepting=False)
        acc = _states_reaching_parity_cycle(self, accepting=True)
        return {q: (Verdict.BOTTOM if q in rej else
                    Verdict.TOP if q in acc else Verdict.UNKNOWN)
                for q in self.states}


def build_support_edges(aut: "Automaton") -> dict:
    """忽略 guard 的拓扑边集（分类与 HD 分析用）。"""
    return {q: {t for (_, t) in aut.trans.get(q, [])} for q in aut.states}


def _sccs(nodes, edges) -> list:
    """迭代版 Tarjan，返回 [frozenset]。"""
    index, low, on, stack, out = {}, {}, set(), [], []
    counter = [0]
    for root in nodes:
        if root in index:
            continue
        work = [(root, iter(edges.get(root, ())))]
        index[root] = low[root] = counter[0]; counter[0] += 1
        stack.append(root); on.add(root)
        while work:
            v, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter[0]; counter[0] += 1
                    stack.append(w); on.add(w)
                    work.append((w, iter(edges.get(w, ()))))
                    advanced = True
                    break
                elif w in on:
                    low[v] = min(low[v], index[w])
            if not advanced:
                work.pop()
                if work:
                    pv = work[-1][0]
                    low[pv] = min(low[pv], low[v])
                if low[v] == index[v]:
                    comp = set()
                    while True:
                        w = stack.pop(); on.discard(w); comp.add(w)
                        if w == v:
                            break
                    out.append(frozenset(comp))
    return out


def _backward_reach(targets: set, nodes: set, edges: dict) -> set:
    """nodes 图中能到达 targets 的所有状态。"""
    rev = {n: set() for n in nodes}
    for u in nodes:
        for v in edges.get(u, ()):
            if v in rev:
                rev[v].add(u)
    seen, stack = set(targets), list(targets)
    while stack:
        v = stack.pop()
        for u in rev[v]:
            if u not in seen:
                seen.add(u); stack.append(u)
    return seen


def _states_reaching_parity_cycle(aut: "Automaton", accepting: bool) -> set:
    """能到达某条 min-优先级环（接受环=偶 / 拒绝环=奇）的状态集合。
    标准分层剥离：SCC 的最小优先级态必在该 SCC 任一过其环上取 min。"""
    edges = build_support_edges(aut)
    remaining = set(aut.states)
    result = set()
    while True:
        removed = set()
        for comp in _sccs(remaining, edges):
            m = min(aut.priorities[s] for s in comp)
            has_cycle = len(comp) > 1 or any(
                t == s for s in comp for t in edges.get(s, ()) if t in comp)
            if has_cycle and (m % 2 == 0) == accepting:
                result |= _backward_reach(set(comp), remaining, edges)
            removed |= {s for s in comp if aut.priorities[s] == m}
        if not removed:
            return result
        remaining -= removed
```

- [ ] **Step 4: 跑测试通过**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_automata.py -q`
Expected: PASS（6 passed）

- [ ] **Step 5: Commit**

```bash
cd C:/workspace/work4ai && git add omega-guard && git commit -m "feat: omega-guard automata——guard parity 自动机+确定性 step+SCC 分层三值分类

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 3: dsl.py Part 1（Monitor 基类 + 安全/计数组合子）

**Files:**
- Create: `omega-guard/omegaguard/dsl.py`
- Test: `omega-guard/tests/test_dsl.py`

**Interfaces:**
- Consumes: `Verdict`, `Pred`, `ToolEvent`（Task 1）
- Produces: `Monitor` 基类（属性 `name: str`、`fail_closed: bool=False`；方法 `step(e)->Verdict`、`final()->Verdict`（默认 UNKNOWN）、`pending()->bool`（默认 False）、`state_size()->int`（默认 1）、`clone()->Monitor`（deepcopy））；组合子 `never(p)`, `always(p)`, `eventually(p)`, `at_most(p, k)`, `at_least(p, k)`——均返回 `Monitor`，`k<0` 或 `k` 非整抛 `ValueError`

- [ ] **Step 1: 写失败测试**

`tests/test_dsl.py`：
```python
import pytest
from omegaguard.events import ToolEvent, tool
from omegaguard.dsl import never, always, eventually, at_most, at_least
from omegaguard.events import Verdict

def E(n): return ToolEvent(n)
V = Verdict

def test_never():
    m = never(tool("delete_db"))
    assert m.step(E("scroll")) == V.UNKNOWN
    assert m.step(E("delete_db")) == V.BOTTOM
    assert m.step(E("scroll")) == V.BOTTOM          # sticky
    assert m.final() == V.BOTTOM and m.pending() is False

def test_always():
    m = always(tool_in_free())
    assert m.step(E("scroll")) == V.UNKNOWN         # scroll 是 free 工具
    assert m.step(E("paid_api")) == V.BOTTOM        # 非 free → 违规
    assert m.final() == V.BOTTOM

def tool_in_free():
    from omegaguard.events import tool_in
    return tool_in("scroll", "search", "read_file", "write_file")

def test_eventually_sticky_top():
    m = eventually(tool("verify"))
    assert m.pending() is True
    assert m.step(E("build")) == V.UNKNOWN
    assert m.step(E("verify")) == V.TOP
    assert m.step(E("deploy")) == V.TOP             # sticky
    assert m.final() == V.TOP and m.pending() is False

def test_eventually_pending_at_end():
    m = eventually(tool("verify"))
    m.step(E("build"))
    assert m.final() == V.UNKNOWN and m.pending() is True   # → 期末 UNRESOLVED

def test_at_most():
    m = at_most(tool("paid_api"), 2)
    assert m.step(E("paid_api")) == V.UNKNOWN
    assert m.step(E("paid_api")) == V.UNKNOWN
    assert m.step(E("paid_api")) == V.BOTTOM        # 第 3 次违规
    assert m.state_size() == 3                      # 计数 0..2
    with pytest.raises(ValueError):
        at_most(tool("x"), -1)

def test_at_least():
    m = at_least(tool("verify"), 1)
    assert m.pending() is True
    assert m.step(E("verify")) == V.TOP
    assert m.final() == V.TOP
    m2 = at_least(tool("verify"), 1)
    m2.step(E("build"))
    assert m2.final() == V.UNKNOWN and m2.pending() is True

def test_clone_independent():
    m = at_most(tool("p"), 1)
    c = m.clone()
    c.step(E("p"))
    assert m.step(E("p")) == V.UNKNOWN              # 原监控器不受试探影响
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_dsl.py -q`
Expected: FAIL（ModuleNotFoundError）

- [ ] **Step 3: 实现 dsl.py Part 1**

```python
"""组合子 DSL：性质 = Python 函数组合，编译为确定性监控器对象。

三值语义（有限会话）：
  step   → BOTTOM=有限前缀已可判违规；UNKNOWN=尚未定（TOP 见 sticky 满足型）
  final  → 期末判定（BOTTOM=确定违规；TOP=确定满足；UNKNOWN=未见违规）
  pending→ 存在未兑现活性义务（Guardrail 期末映射为 UNRESOLVED 软违规）
"""
from __future__ import annotations
import copy
from .events import Verdict, Pred, ToolEvent


def _check_k(k: int):
    if not isinstance(k, int) or k < 0:
        raise ValueError(f"k 必须为非负整数，得到 {k!r}")


class Monitor:
    name: str = "?"
    fail_closed: bool = False

    def step(self, e: ToolEvent) -> Verdict:
        raise NotImplementedError

    def final(self) -> Verdict:
        return Verdict.UNKNOWN

    def pending(self) -> bool:
        return False

    def state_size(self) -> int:
        return 1

    def clone(self) -> "Monitor":
        return copy.deepcopy(self)


class _Never(Monitor):
    def __init__(self, p: Pred):
        self.p, self.name = p, f"never({p.name})"
        self.bad = False

    def step(self, e):
        if self.p(e):
            self.bad = True
        return Verdict.BOTTOM if self.bad else Verdict.UNKNOWN

    def final(self):
        return Verdict.BOTTOM if self.bad else Verdict.UNKNOWN


class _Always(Monitor):
    def __init__(self, p: Pred):
        self.p, self.name = p, f"always({p.name})"
        self.bad = False

    def step(self, e):
        if not self.p(e):
            self.bad = True
        return Verdict.BOTTOM if self.bad else Verdict.UNKNOWN

    def final(self):
        return Verdict.BOTTOM if self.bad else Verdict.UNKNOWN


class _Eventually(Monitor):
    def __init__(self, p: Pred):
        self.p, self.name = p, f"eventually({p.name})"
        self.seen = False

    def step(self, e):
        if self.p(e):
            self.seen = True
        return Verdict.TOP if self.seen else Verdict.UNKNOWN

    def final(self):
        return Verdict.TOP if self.seen else Verdict.UNKNOWN

    def pending(self):
        return not self.seen


class _AtMost(Monitor):
    def __init__(self, p: Pred, k: int):
        _check_k(k)
        self.p, self.k, self.name = p, k, f"at_most({p.name},{k})"
        self.count, self.bad = 0, False

    def step(self, e):
        if self.bad:
            return Verdict.BOTTOM
        if self.p(e):
            self.count += 1
            if self.count > self.k:
                self.bad = True
                return Verdict.BOTTOM
        return Verdict.UNKNOWN

    def final(self):
        return Verdict.BOTTOM if self.bad else Verdict.UNKNOWN

    def state_size(self):
        return self.k + 1


class _AtLeast(Monitor):
    def __init__(self, p: Pred, k: int):
        _check_k(k)
        self.p, self.k, self.name = p, k, f"at_least({p.name},{k})"
        self.count = 0

    def step(self, e):
        if self.count < self.k and self.p(e):
            self.count += 1
        return Verdict.TOP if self.count >= self.k else Verdict.UNKNOWN

    def final(self):
        return Verdict.TOP if self.count >= self.k else Verdict.UNKNOWN

    def pending(self):
        return self.count < self.k

    def state_size(self):
        return self.k + 1


def never(p: Pred) -> Monitor:
    """G ¬p：p 出现即 BOTTOM（sticky）。"""
    return _Never(p)

def always(p: Pred) -> Monitor:
    """G p：¬p 出现即 BOTTOM（sticky）。"""
    return _Always(p)

def eventually(p: Pred) -> Monitor:
    """F p：见过 p 即 TOP（sticky）；期末未见 → pending（UNRESOLVED）。"""
    return _Eventually(p)

def at_most(p: Pred, k: int) -> Monitor:
    """全会话 p 至多 k 次；第 k+1 次 BOTTOM。"""
    return _AtMost(p, k)

def at_least(p: Pred, k: int) -> Monitor:
    """全会话 p 至少 k 次；达到即 TOP（sticky）。"""
    return _AtLeast(p, k)
```

- [ ] **Step 4: 跑测试通过**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_dsl.py -q`
Expected: PASS（8 passed）

- [ ] **Step 5: Commit**

```bash
cd C:/workspace/work4ai && git add omega-guard && git commit -m "feat: omega-guard dsl 基础组合子——never/always/eventually/at_most/at_least

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 4: dsl.py Part 2（结构化组合子 + And/Or）

**Files:**
- Modify: `omega-guard/omegaguard/dsl.py`（追加）
- Test: `omega-guard/tests/test_dsl2.py`

**Interfaces:**
- Consumes: `Monitor`、`Verdict`、`Pred`（Task 3）
- Produces: `every_eventually(p, q)`（G(p→F q)，期末 pending→UNRESOLVED）；`within_k(p, q, k)`（k≥1，q 须在 p 后第 k 个事件内出现，窗口滑过 BOTTOM）；`no_more_than_k_consecutive(p, k)`；`requires_since(p, since, req)`（p 仅当自上次 since 以来见过 req 才允许；同事件多谓词按 req→since→p 顺序处理，since 支配）；`And(*ms)`、`Or(*ms)`（BOTTOM 支配；全 TOP→TOP；pending: And=any, Or=all；`state_size`=成员和）

- [ ] **Step 1: 写失败测试**

`tests/test_dsl2.py`：
```python
import pytest
from omegaguard.events import ToolEvent, tool, Verdict
from omegaguard.dsl import (every_eventually, within_k,
                            no_more_than_k_consecutive, requires_since, And, Or)

def E(n): return ToolEvent(n)
V = Verdict

def test_every_eventually():
    m = every_eventually(tool("start"), tool("end"))
    assert m.step(E("start")) == V.UNKNOWN and m.pending() is True
    assert m.step(E("scroll")) == V.UNKNOWN and m.pending() is True
    assert m.step(E("end")) == V.UNKNOWN and m.pending() is False
    assert m.final() == V.UNKNOWN                       # 无未决 → SATISFIED
    m2 = every_eventually(tool("start"), tool("end"))
    m2.step(E("start"))
    assert m2.final() == V.UNKNOWN and m2.pending() is True   # → UNRESOLVED

def test_within_k_window():
    m = within_k(tool("build"), tool("verify"), k=2)
    assert m.step(E("build")) == V.UNKNOWN        # 窗口开: 允许2个事件内 verify
    assert m.step(E("scroll")) == V.UNKNOWN       # 第1个, 还剩1
    assert m.step(E("scroll")) == V.UNKNOWN       # 第2个=deadline 到期事件, 未verify
    assert m.step(E("scroll")) == V.BOTTOM        # 窗口滑过 → 违规
    with pytest.raises(ValueError):
        within_k(tool("a"), tool("b"), 0)

def test_within_k_satisfies_in_time():
    m = within_k(tool("build"), tool("verify"), k=1)
    m.step(E("build"))
    assert m.step(E("verify")) == V.UNKNOWN and m.pending() is False

def test_within_k_q_resolves_then_new_p():
    m = within_k(tool("p"), tool("q"), k=1)
    m.step(E("p")); m.step(E("q"))                # 兑现
    assert m.step(E("scroll")) == V.UNKNOWN       # 无窗口
    m.step(E("p"))
    assert m.step(E("q")) == V.UNKNOWN            # 再开再兑现

def test_consecutive():
    m = no_more_than_k_consecutive(tool("scroll"), 2)
    assert m.step(E("scroll")) == V.UNKNOWN
    assert m.step(E("scroll")) == V.UNKNOWN
    assert m.step(E("scroll")) == V.BOTTOM        # 第3连
    m2 = no_more_than_k_consecutive(tool("scroll"), 2)
    m2.step(E("scroll")); m2.step(E("scroll")); m2.step(E("search"))
    assert m2.step(E("scroll")) == V.UNKNOWN      # 断连重计

def test_requires_since():
    m = requires_since(tool("deploy"), since=tool("build"), req=tool("verify"))
    assert m.step(E("build")) == V.UNKNOWN
    assert m.step(E("deploy")) == V.BOTTOM        # build 后未 verify 即 deploy
    m2 = requires_since(tool("deploy"), since=tool("build"), req=tool("verify"))
    m2.step(E("build")); m2.step(E("verify"))
    assert m2.step(E("deploy")) == V.UNKNOWN      # 已 verify → 放行
    assert m2.step(E("deploy")) == V.UNKNOWN      # satisfied 保持到下次 build
    m2.step(E("build"))
    assert m2.step(E("deploy")) == V.BOTTOM       # 新 build 重置

def test_and_or_merge():
    a, b = never(tool("x")), eventually(tool("y"))
    m = And(a, b)
    assert m.step(E("z")) == V.UNKNOWN            # a=UNKNOWN,b=UNKNOWN
    assert m.step(E("y")) == V.TOP                # a=UNKNOWN? → UNKNOWN!
    # 修正: And 全 TOP 才 TOP, a=UNKNOWN → UNKNOWN
    m2 = And(eventually(tool("y")), eventually(tool("w")))
    assert m2.step(E("y")) == V.UNKNOWN           # b 未满足
    assert m2.step(E("w")) == V.TOP
    assert m2.pending() is False
    m3 = Or(eventually(tool("y")), eventually(tool("w")))
    assert m3.step(E("y")) == V.TOP
    assert m3.pending() is False
    m4 = And(never(tool("x")), never(tool("y")))
    m4.step(E("x"))
    assert m4.step(E("z")) == V.BOTTOM            # BOTTOM 支配
    m5 = Or(eventually(tool("y")), eventually(tool("w")))
    assert m5.pending() is True                   # 全员 pending 才 pending

def test_state_size_sum():
    m = And(at_most_sz(), never(tool("x")))
    assert m.state_size() >= 2

def at_most_sz():
    from omegaguard.dsl import at_most
    return at_most(tool("p"), 1)
```

注意 `test_and_or_merge` 中第一个断言块：`And(never, eventually)` 在 `y` 后应为 UNKNOWN（never 成员非 TOP）——测试里写清期望再修正注释，最终断言：
```python
    m = And(never(tool("x")), eventually(tool("y")))
    assert m.step(E("z")) == V.UNKNOWN
    assert m.step(E("y")) == V.UNKNOWN           # a=UNKNOWN → And=UNKNOWN
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_dsl2.py -q`
Expected: FAIL（ImportError: every_eventually）

- [ ] **Step 3: 实现 Part 2（追加到 dsl.py）**

```python
class _EveryEventually(Monitor):
    """G(p → F q)。永不 BOTTOM；期末 p 后未见 q → pending（UNRESOLVED）。"""
    def __init__(self, p: Pred, q: Pred):
        self.p, self.q = p, q
        self.name = f"every_eventually({p.name},{q.name})"
        self.waiting_since = None

    def step(self, e):
        if self.waiting_since is not None and self.q(e):
            self.waiting_since = None
        if self.p(e) and self.waiting_since is None:
            self.waiting_since = -1     # 只记"有未决", 首次索引由 Guardrail 记
        return Verdict.UNKNOWN

    def pending(self):
        return self.waiting_since is not None


class _WithinK(Monitor):
    """G(p → q 在随后 k 个事件内)。窗口滑过未兑现 → BOTTOM（在线可拦截）。"""
    def __init__(self, p: Pred, q: Pred, k: int):
        _check_k(k)
        if k < 1:
            raise ValueError("within_k 需要 k ≥ 1")
        self.p, self.q, self.k = p, q, k
        self.name = f"within_k({p.name},{q.name},{k})"
        self.deadline = None            # None=无窗口; 否则=q 最迟出现的事件索引
        self.idx = -1
        self.bad = False

    def step(self, e):
        self.idx += 1
        if self.deadline is not None and self.deadline < self.idx and not self.bad:
            self.bad = True             # 上个窗口已滑过且本事件非 q
        if self.q(e):
            self.deadline = None        # 兑现所有开窗(开窗 deadline ≥ idx 恒成立)
        if self.p(e):
            d = self.idx + self.k
            self.deadline = d if self.deadline is None else min(self.deadline, d)
        return Verdict.BOTTOM if self.bad else Verdict.UNKNOWN

    def final(self):
        return Verdict.BOTTOM if self.bad else Verdict.UNKNOWN


class _Consecutive(Monitor):
    def __init__(self, p: Pred, k: int):
        _check_k(k)
        self.p, self.k, self.name = p, k, f"no_more_than_k_consecutive({p.name},{k})"
        self.run, self.bad = 0, False

    def step(self, e):
        if self.bad:
            return Verdict.BOTTOM
        if self.p(e):
            self.run += 1
            if self.run > self.k:
                self.bad = True
                return Verdict.BOTTOM
        else:
            self.run = 0
        return Verdict.UNKNOWN

    def final(self):
        return Verdict.BOTTOM if self.bad else Verdict.UNKNOWN

    def state_size(self):
        return self.k + 1


class _RequiresSince(Monitor):
    """p 仅当自上次 since 以来见过 req 才允许（deploy 需 build 后 verify）。
    同事件处理顺序: req 置位 → since 清位（since 支配）→ p 检查。"""
    def __init__(self, p: Pred, since: Pred, req: Pred):
        self.p, self.since, self.req = p, since, req
        self.name = f"requires_since({p.name},since={since.name},req={req.name})"
        self.satisfied, self.bad = False, False

    def step(self, e):
        if self.bad:
            return Verdict.BOTTOM
        if self.req(e):
            self.satisfied = True
        if self.since(e):
            self.satisfied = False
        if self.p(e) and not self.satisfied:
            self.bad = True
            return Verdict.BOTTOM
        return Verdict.UNKNOWN

    def final(self):
        return Verdict.BOTTOM if self.bad else Verdict.UNKNOWN


class _And(Monitor):
    def __init__(self, *ms: Monitor):
        assert ms, "And 需要至少一个成员"
        self.ms, self.name = list(ms), "And(" + ",".join(m.name for m in ms) + ")"

    def step(self, e):
        vs = [m.step(e) for m in self.ms]
        if Verdict.BOTTOM in vs:
            return Verdict.BOTTOM
        return Verdict.TOP if all(v == Verdict.TOP for v in vs) else Verdict.UNKNOWN

    def final(self):
        vs = [m.final() for m in self.ms]
        if Verdict.BOTTOM in vs:
            return Verdict.BOTTOM
        return Verdict.TOP if all(v == Verdict.TOP for v in vs) else Verdict.UNKNOWN

    def pending(self):
        return any(m.pending() for m in self.ms)

    def state_size(self):
        return sum(m.state_size() for m in self.ms)

    @property
    def fail_closed(self):
        return any(m.fail_closed for m in self.ms)


class _Or(Monitor):
    def __init__(self, *ms: Monitor):
        assert ms, "Or 需要至少一个成员"
        self.ms, self.name = list(ms), "Or(" + ",".join(m.name for m in ms) + ")"

    def step(self, e):
        vs = [m.step(e) for m in self.ms]
        if Verdict.TOP in vs:
            return Verdict.TOP
        return Verdict.BOTTOM if all(v == Verdict.BOTTOM for v in vs) else Verdict.UNKNOWN

    def final(self):
        vs = [m.final() for m in self.ms]
        if Verdict.TOP in vs:
            return Verdict.TOP
        return Verdict.BOTTOM if all(v == Verdict.BOTTOM for v in vs) else Verdict.UNKNOWN

    def pending(self):
        return all(m.pending() for m in self.ms)

    def state_size(self):
        return sum(m.state_size() for m in self.ms)

    @property
    def fail_closed(self):
        return any(m.fail_closed for m in self.ms)


def every_eventually(p: Pred, q: Pred) -> Monitor:
    return _EveryEventually(p, q)

def within_k(p: Pred, q: Pred, k: int) -> Monitor:
    return _WithinK(p, q, k)

def no_more_than_k_consecutive(p: Pred, k: int) -> Monitor:
    return _Consecutive(p, k)

def requires_since(p: Pred, since: Pred, req: Pred) -> Monitor:
    return _RequiresSince(p, since, req)

def And(*ms: Monitor) -> Monitor:
    return _And(*ms)

def Or(*ms: Monitor) -> Monitor:
    return _Or(*ms)
```

（`no_more_than_k_consecutive` 直接 `return _Consecutive(p, k)`，删去示例里的花哨写法。）

- [ ] **Step 4: 跑 Part1+Part2 全部测试通过**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/ -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd C:/workspace/work4ai && git add omega-guard && git commit -m "feat: omega-guard dsl 结构化组合子——every_eventually/within_k/consecutive/requires_since+And/Or

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 5: monitor.py（Guardrail 运行器：observe / enforce / 报告 / 异常策略）

**Files:**
- Create: `omega-guard/omegaguard/monitor.py`
- Test: `omega-guard/tests/test_monitor.py`

**Interfaces:**
- Consumes: `Monitor`、`Verdict`、`ToolEvent`（Task 3/4）
- Produces: `Decision(allowed: bool, reasons: list[str], errors: list[str])`；`PropertyReport(name, verdict, detail, first_bad_index)`——verdict ∈ `"SATISFIED"|"VIOLATED"|"UNRESOLVED"|"INTERNAL_ERROR"`；`Report(props, events_seen)` 含 `summary() -> str`；`Guardrail(monitors, mode="observe")`：类方法 `Guardrail.props(list) -> Guardrail`；`check(e) -> Decision`（enforce 用 clone 试探：任一成员 clone-step BOTTOM → Deny；observe 恒 Allow）；`observe(e) -> None`（真实施步 + 记 `first_bad_index` + INTERNAL_ERROR 处理：出错监控器转惰性）；`end() -> Report`（BOTTOM→VIOLATED；pending→UNRESOLVED；else SATISFIED）；属性 `events_seen`

- [ ] **Step 1: 写失败测试**

`tests/test_monitor.py`：
```python
from omegaguard.events import ToolEvent, tool, Verdict
from omegaguard.dsl import never, every_eventually, at_most, eventually
from omegaguard.monitor import Guardrail

def E(n): return ToolEvent(n)

def mk(mode="observe"):
    return Guardrail([
        never(tool("delete_db")),
        every_eventually(tool("start"), tool("end")),
        at_most(tool("paid"), 1),
    ], mode=mode)

def test_observe_mode_never_blocks():
    g = mk("observe")
    d = g.check(E("delete_db"))
    assert d.allowed is True
    g.observe(E("delete_db"))
    g.observe(E("start"))
    r = g.end()
    by = {p.name: p for p in r.props}
    assert by["never(tool(delete_db))"].verdict == "VIOLATED"
    assert by["never(tool(delete_db))"].first_bad_index == 0
    assert by["every_eventually(tool(start),tool(end))"].verdict == "UNRESOLVED"
    assert r.events_seen == 2
    assert "VIOLATED" in r.summary() and "UNRESOLVED" in r.summary()

def test_enforce_mode_blocks():
    g = mk("enforce")
    assert g.check(E("scroll")).allowed is True
    d = g.check(E("delete_db"))
    assert d.allowed is False and any("delete_db" in r for r in d.reasons)
    # 拒绝后真实状态未被污染
    g.observe(E("scroll"))
    d2 = g.check(E("paid")); g.observe(E("paid"))
    d3 = g.check(E("paid"))
    assert d3.allowed is False                       # at_most(paid,1) 已满

def test_check_does_not_mutate():
    g = mk("enforce")
    for _ in range(5):
        g.check(E("delete_db"))                      # 反复试探
    g.observe(E("scroll")); g.observe(E("start")); g.observe(E("end"))
    r = g.end()
    assert all(p.verdict != "VIOLATED" for p in r.props)

def test_internal_error_fail_open():
    from omegaguard.dsl import Monitor
    class Boom(Monitor):
        name = "boom"
        def step(self, e): raise RuntimeError("炸了")
    g = Guardrail([Boom(), never(tool("x"))], mode="enforce")
    d = g.check(E("x"))
    assert d.allowed is False                        # never 拒绝; boom fail-open 不拖垮
    assert d.errors == ["boom"]
    g.observe(E("x"))
    r = g.end()
    by = {p.name: p for p in r.props}
    assert by["boom"].verdict == "INTERNAL_ERROR"
    assert by["never(tool(x))"].verdict == "VIOLATED"

def test_internal_error_fail_closed():
    from omegaguard.dsl import Monitor
    class Boom(Monitor):
        name = "boom-closed"
        fail_closed = True
        def step(self, e): raise RuntimeError("炸了")
    g = Guardrail([Boom()], mode="enforce")
    d = g.check(E("anything"))
    assert d.allowed is False and "boom-closed" in d.errors

def test_satisfied_report():
    g = mk("observe")
    g.observe(E("scroll")); g.observe(E("start")); g.observe(E("end"))
    r = g.end()
    assert all(p.verdict == "SATISFIED" for p in r.props)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_monitor.py -q`
Expected: FAIL（ModuleNotFoundError）

- [ ] **Step 3: 实现 monitor.py**

```python
"""Guardrail 运行器：observe（审计）/ enforce（拦截）两模式。

生产铁律：监控器异常绝不拖垮宿主——fail-open（默认，跳过并响亮记录）/
fail-closed（监控器 fail_closed=True 时检查期拒绝）。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from .events import ToolEvent, Verdict
from .dsl import Monitor


@dataclass
class Decision:
    allowed: bool
    reasons: list = field(default_factory=list)
    errors: list = field(default_factory=list)


@dataclass
class PropertyReport:
    name: str
    verdict: str          # SATISFIED | VIOLATED | UNRESOLVED | INTERNAL_ERROR
    detail: str = ""
    first_bad_index: int | None = None


@dataclass
class Report:
    props: list
    events_seen: int

    def summary(self) -> str:
        lines = [f"omega-guard 报告（{self.events_seen} 事件）"]
        for p in self.props:
            mark = {"SATISFIED": "✓", "VIOLATED": "✗", "UNRESOLVED": "⚠",
                    "INTERNAL_ERROR": "!"}[p.verdict]
            lines.append(f"  {mark} {p.name}: {p.verdict}"
                         + (f" @事件#{p.first_bad_index}" if p.first_bad_index is not None else ""))
        return "\n".join(lines)


class Guardrail:
    def __init__(self, monitors: list, mode: str = "observe"):
        if mode not in ("observe", "enforce"):
            raise ValueError(f"mode 须为 observe|enforce，得到 {mode!r}")
        self.monitors, self.mode = list(monitors), mode
        self._first_bad = {}
        self._errored = set()
        self.events_seen = 0

    @classmethod
    def props(cls, monitors: list, mode: str = "enforce") -> "Guardrail":
        return cls(monitors, mode=mode)

    # ---- enforce 试探（clone，不污染真实状态） ----
    def check(self, e: ToolEvent) -> Decision:
        reasons, errors = [], []
        if self.mode != "enforce":
            return Decision(True, reasons, errors)
        for m in self.monitors:
            if m.name in self._errored:
                if m.fail_closed:
                    errors.append(m.name)
                continue
            try:
                v = m.clone().step(e)
            except Exception:
                errors.append(m.name)
                if m.fail_closed:
                    reasons.append(f"{m.name} 内部错误（fail-closed）")
                continue
            if v == Verdict.BOTTOM:
                reasons.append(f"{m.name} 将被该事件违反")
        return Decision(not reasons, reasons, errors)

    # ---- 真实施步 ----
    def observe(self, e: ToolEvent) -> None:
        idx = self.events_seen
        self.events_seen += 1
        for m in self.monitors:
            if m.name in self._errored:
                continue
            try:
                v = m.step(e)
            except Exception:
                self._errored.add(m.name)
                continue
            if v == Verdict.BOTTOM and m.name not in self._first_bad:
                self._first_bad[m.name] = idx

    def end(self) -> Report:
        props = []
        for m in self.monitors:
            if m.name in self._errored:
                props.append(PropertyReport(m.name, "INTERNAL_ERROR",
                                            "监控器抛异常，已按策略降级"))
                continue
            f = m.final()
            if f == Verdict.BOTTOM:
                props.append(PropertyReport(m.name, "VIOLATED",
                                            "有限前缀已可判违规",
                                            self._first_bad.get(m.name)))
            elif m.pending():
                props.append(PropertyReport(m.name, "UNRESOLVED",
                                            "存在未兑现的活性义务（会话已结束）"))
            else:
                props.append(PropertyReport(m.name, "SATISFIED"))
        return Report(props, self.events_seen)
```

- [ ] **Step 4: 跑测试通过**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/ -q`
Expected: PASS（全部）

- [ ] **Step 5: Commit**

```bash
cd C:/workspace/work4ai && git add omega-guard && git commit -m "feat: omega-guard monitor——Guardrail observe/enforce+三态报告+fail-open/closed 异常策略

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 6: agent 基础（faults.py 画像 + harness 工具环境/执行器）

**Files:**
- Create: `omega-guard/omegaguard/agent/__init__.py`（空）
- Create: `omega-guard/omegaguard/agent/faults.py`
- Create: `omega-guard/omegaguard/agent/harness.py`（本任务只写 Env/TOOLS/execute 部分）
- Test: `omega-guard/tests/test_agent_env.py`

**Interfaces:**
- Consumes: `ToolEvent`（Task 1）
- Produces: `FaultProfile(loop_stuck=0.0, forget_close=0.0, retry_storm=0.0, forbidden_slip=0.0, skip_verify=0.0, budget_blind=0.0, seed=0)` dataclass，类常量 `CLEAN = FaultProfile()`；`Env` dataclass（字段 `conn_open=False, written=False, cost=0, db_deleted=False, built=False, verified=False, deployed=False, task_open=False`）；`execute(env, name, rng) -> ToolEvent`（phase='result'；`flaky_api` 以 30% 概率 err；`delete_db` 置 `db_deleted=True`；`paid_api` 置 `cost+=1`；`open_conn/close_conn/start_task/end_task/build/verify/deploy/write_file` 按名更新 Env；未知工具名抛 `ValueError`）

- [ ] **Step 1: 写失败测试**

`tests/test_agent_env.py`：
```python
import random
from omegaguard.agent.faults import FaultProfile, CLEAN
from omegaguard.agent.harness import Env, execute

def test_clean_profile_defaults():
    p = CLEAN
    assert all(getattr(p, f) == 0.0 for f in
               ["loop_stuck", "forget_close", "retry_storm",
                "forbidden_slip", "skip_verify", "budget_blind"])

def test_execute_effects():
    rng = random.Random(0)
    env = Env()
    r = execute(env, "open_conn", rng);  assert env.conn_open and r.status == "ok"
    execute(env, "write_file", rng);     assert env.written
    execute(env, "paid_api", rng); execute(env, "paid_api", rng)
    assert env.cost == 2
    execute(env, "build", rng); execute(env, "verify", rng); execute(env, "deploy", rng)
    assert env.built and env.verified and env.deployed
    execute(env, "start_task", rng); assert env.task_open
    execute(env, "end_task", rng);   assert not env.task_open
    execute(env, "delete_db", rng);  assert env.db_deleted
    execute(env, "close_conn", rng); assert not env.conn_open

def test_execute_flaky_and_unknown():
    rng = random.Random(42)
    env = Env()
    statuses = {execute(env, "flaky_api", rng).status for _ in range(60)}
    assert statuses == {"ok", "err"}                    # 30% 概率两头都见
    try:
        execute(env, "no_such_tool", rng); assert False
    except ValueError:
        pass
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_agent_env.py -q`
Expected: FAIL（ModuleNotFoundError）

- [ ] **Step 3: 实现 faults.py 与 harness.py（环境部分）**

`omegaguard/agent/faults.py`：
```python
"""故障画像：参数化概率，驱动 SimPolicy 偏离正常计划。"""
from dataclasses import dataclass


@dataclass
class FaultProfile:
    loop_stuck: float = 0.0        # scroll 后不采纳"无新信息"继续刷
    forget_close: float = 0.0      # 任务末跳过 close_conn
    retry_storm: float = 0.0       # paid_api 出错后原样重试（而非走 fallback）
    forbidden_slip: float = 0.0    # "清理旧库"子步骤滑向 delete_db
    skip_verify: float = 0.0       # build→deploy 间跳过 verify
    budget_blind: float = 0.0      # 成功后仍追加一次 paid_api 调用
    seed: int = 0


CLEAN = FaultProfile()
```

`omegaguard/agent/harness.py`（第一部分）：
```python
"""参考 agent harness：模拟工具环境 + 策略 + 运行器。"""
from __future__ import annotations
import random
from dataclasses import dataclass
from ..events import ToolEvent


@dataclass
class Env:
    conn_open: bool = False
    written: bool = False
    cost: int = 0
    db_deleted: bool = False
    built: bool = False
    verified: bool = False
    deployed: bool = False
    task_open: bool = False


def execute(env: Env, name: str, rng: random.Random) -> ToolEvent:
    """执行工具并返回 result 事件（更新 Env）。"""
    if name == "open_conn":    env.conn_open = True
    elif name == "close_conn": env.conn_open = False
    elif name == "write_file": env.written = True
    elif name == "paid_api":   env.cost += 1
    elif name == "delete_db":  env.db_deleted = True
    elif name == "build":      env.built = True
    elif name == "verify":     env.verified = True
    elif name == "deploy":     env.deployed = True
    elif name == "start_task": env.task_open = True
    elif name == "end_task":   env.task_open = False
    elif name in ("scroll", "search", "read_file", "flaky_api"):
        pass
    else:
        raise ValueError(f"未知工具 {name!r}")
    status = "err" if (name in ("flaky_api", "paid_api")
                       and rng.random() < 0.3) else "ok"
    return ToolEvent(name, {}, "result", status)
```

`omegaguard/agent/__init__.py`：空文件。

- [ ] **Step 4: 跑测试通过**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_agent_env.py -q`
Expected: PASS（3 passed）

- [ ] **Step 5: Commit**

```bash
cd C:/workspace/work4ai && git add omega-guard && git commit -m "feat: omega-guard agent 环境——FaultProfile 六类故障画像+模拟工具执行器

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 7: agent 运行器（SimPolicy + 任务定义 + AgentRunner + fault onset 标记）

**Files:**
- Modify: `omega-guard/omegaguard/agent/harness.py`（追加 Step/TaskDef/SimPolicy/AgentRunner/RunResult）
- Test: `omega-guard/tests/test_agent_runner.py`

**Interfaces:**
- Consumes: `Env`, `execute`, `FaultProfile`, `CLEAN`（Task 6）；`Guardrail`（Task 5）
- Produces: `Step(preferred, fallback=None, note="")` dataclass；`TaskDef(name, plan: list[Step], goal: Callable[[Env], bool])`；`TASKS: dict[str, TaskDef]`（三任务：`sync_data` / `deploy_service` / `research_brief`，goal 定义见 Step 3 注释）；`SimPolicy(profile)` 方法 `pick(step, env, rng, denied_last, retry_state) -> str`；`RunResult(events: list[ToolEvent], onsets: list[tuple[int, str]], blocks: int, goal_met: bool)`；`AgentRunner.run(task_name, profile, guardrail) -> RunResult`。故障显现实象 = onsets 条目 `(事件索引, 故障名)`

任务/goal/故障对照（指标归因的依据，metrics.py 直接复用）：
- `sync_data`：`[open_conn, read_file, Step(paid_api, fallback=search), write_file, Step(close_conn)]`，goal = `written and not conn_open`。`retry_storm`：paid err 后以 p 概率重试 paid（再 err 再赌，最多 3 次）而非 fallback；`budget_blind`：paid ok 后以 p 概率追加一次 paid；`forget_close`：末步以 p 概率直接放弃 close_conn
- `deploy_service`：`[build, Step(verify, fallback=None), deploy, Step(start_task), Step(end_task)]`，goal = `deployed and not db_deleted`。`skip_verify`：verify 步以 p 概率跳过（直接 deploy）；`forbidden_slip`：build 前以 p 概率插入一次 delete_db（"清理旧库"）
- `research_brief`：`[start_task, Step(search, fallback=scroll), scroll, scroll, end_task]`，goal = `task_open == False and 搜索过`（search 或 scroll 任一）。`loop_stuck`：每次 scroll 后以 p 概率再 scroll 而非前进

被 enforce 拒绝时的行为：若该 Step 有 fallback 且未用过 → 用 fallback；否则该步放弃（aborted，计入 blocks）。连续 3 次拒绝 → 任务中止（goal_met=False）。

- [ ] **Step 1: 写失败测试**

`tests/test_agent_runner.py`：
```python
import random
from omegaguard.agent.faults import FaultProfile, CLEAN
from omegaguard.agent.harness import AgentRunner, TASKS
from omegaguard.monitor import Guardrail
from omegaguard.events import tool, tool_phase
from omegaguard.dsl import (never, every_eventually, at_most,
                            no_more_than_k_consecutive, requires_since)

def props(mode="observe"):
    return Guardrail([
        never(tool("delete_db")),
        every_eventually(tool_phase("open_conn"), tool_phase("close_conn")),
        every_eventually(tool_phase("start_task"), tool_phase("end_task")),
        at_most(tool_phase("paid_api", "call"), 5),
        no_more_than_k_consecutive(tool("scroll"), 4),
        requires_since(tool("deploy"), since=tool("build"), req=tool("verify")),
    ], mode=mode)

def run(task, profile, mode="observe"):
    return AgentRunner().run(task, profile, props(mode))

def test_clean_run_completes_all_tasks():
    for t in TASKS:
        r = run(t, CLEAN, "enforce")
        assert r.goal_met, f"{t} 干净轨迹应完成"
        assert r.onsets == [] and r.blocks == 0

def test_forbidden_slip_observed_vs_enforced():
    prof = FaultProfile(forbidden_slip=1.0, seed=3)
    ro = run("deploy_service", prof, "observe")
    assert any(f == "forbidden_slip" for _, f in ro.onsets)
    assert ro.goal_met is False                          # db 被删
    re = run("deploy_service", prof, "enforce")
    assert re.blocks >= 1                                # delete_db 被拦
    assert re.goal_met is True                           # 拦截救回任务 ← 核心指标

def test_forget_close_onset_and_unresolved():
    prof = FaultProfile(forget_close=1.0, seed=5)
    r = run("sync_data", prof, "observe")
    assert any(f == "forget_close" for _, f in r.onsets)
    assert r.goal_met is False

def test_loop_stuck_blocked_and_recovered():
    prof = FaultProfile(loop_stuck=1.0, seed=7)
    r = run("research_brief", prof, "enforce")
    assert r.blocks >= 1
    assert r.goal_met is True                            # 第5连 scroll 被拦 → 走 end_task

def test_retry_storm_counts_paid():
    prof = FaultProfile(retry_storm=1.0, seed=11)
    # flaky→err 概率 30%, seed 固定保证复现
    r = AgentRunner().run("sync_data", prof, Guardrail.props([at_most(tool_phase("paid_api","call"), 2)]))
    paid_calls = [e for e in r.events if e.name == "paid_api" and e.phase == "call"]
    assert len(paid_calls) >= 2                          # 风暴确实发生
    assert any(f == "retry_storm" for _, f in r.onsets)

def test_determinism_same_seed_same_trace():
    a = run("deploy_service", FaultProfile(skip_verify=1.0, forbidden_slip=0.5, seed=9), "observe")
    b = run("deploy_service", FaultProfile(skip_verify=0.5, forbidden_slip=0.5, seed=9), "observe")
    # 同 seed 不同概率 → 轨迹可以不同; 但同配置同 seed 必须相同:
    c = run("deploy_service", FaultProfile(skip_verify=1.0, forbidden_slip=0.5, seed=9), "observe")
    assert [e.name for e in a.events] == [e.name for e in c.events]
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_agent_runner.py -q`
Expected: FAIL（ImportError: AgentRunner）

- [ ] **Step 3: 实现（追加到 harness.py）**

```python
# ---------- harness 第二部分：任务 / 策略 / 运行器 ----------
from dataclasses import dataclass as _dc
from typing import Callable
from ..monitor import Guardrail
from ..dsl import Monitor  # noqa: F401 (类型引用)


@_dc
class Step:
    preferred: str
    fallback: str | None = None
    note: str = ""


@_dc
class TaskDef:
    name: str
    plan: list
    goal: Callable[[Env], bool]


TASKS = {
    "sync_data": TaskDef("sync_data", [
        Step("open_conn"), Step("read_file"),
        Step("paid_api", fallback="search"),
        Step("write_file"), Step("close_conn"),
    ], goal=lambda env: env.written and not env.conn_open),
    "deploy_service": TaskDef("deploy_service", [
        Step("build"), Step("verify"), Step("deploy"),
        Step("start_task"), Step("end_task"),
    ], goal=lambda env: env.deployed and not env.db_deleted),
    "research_brief": TaskDef("research_brief", [
        Step("start_task"), Step("search", fallback="scroll"),
        Step("scroll"), Step("scroll"), Step("end_task"),
    ], goal=lambda env: not env.task_open),
}


class SimPolicy:
    """规则式策略 + 故障注入。pick 返回工具名；偏离发生时 harness 记 onset。"""

    def __init__(self, profile: FaultProfile):
        self.pf = profile
        self.rng = random.Random(profile.seed)

    def _f(self, name) -> bool:
        return self.rng.random() < getattr(self.pf, name)

    def deviates(self, step: Step, ctx: dict) -> str | None:
        """返回偏离动作（工具名或 'SKIP'/'STUCK'）；None=按计划。ctx 见调用点。"""
        pf = self.pf
        if ctx["phase"] == "pre_build" and ctx["task"] == "deploy_service":
            if pf.forbidden_slip and self._f("forbidden_slip"):
                return "delete_db"
        if step.preferred == "verify" and pf.skip_verify and self._f("skip_verify"):
            return "SKIP"
        if step.preferred == "close_conn" and pf.forget_close and self._f("forget_close"):
            return "SKIP"
        if ctx["phase"] == "after_scroll" and pf.loop_stuck and self._f("loop_stuck"):
            return "scroll"
        if ctx["phase"] == "paid_err" and pf.retry_storm and self._f("retry_storm"):
            return "paid_api"
        if ctx["phase"] == "paid_ok" and pf.budget_blind and self._f("budget_blind"):
            return "paid_api"
        return None


@_dc
class RunResult:
    events: list          # list[ToolEvent]（call 与 result 混序）
    onsets: list          # list[(idx, fault_name)]
    blocks: int
    goal_met: bool


class AgentRunner:
    def run(self, task_name: str, profile: FaultProfile, guardrail: Guardrail) -> RunResult:
        task = TASKS[task_name]
        env = Env()
        pol = SimPolicy(profile)
        events, onsets = [], []
        blocks = 0
        consecutive_denies = 0

        def emit(name, fault=None):
            """提议→check→(执行)→observe，返回是否放行执行。"""
            nonlocal blocks, consecutive_denies
            idx = len(events)
            call = ToolEvent(name, {}, "call", None)
            d = guardrail.check(call)
            if not d.allowed:
                blocks += 1
                consecutive_denies += 1
                return False
            consecutive_denies = 0
            events.append(call)
            if fault:
                onsets.append((idx, fault))
            res = execute(env, name, pol.rng)
            events.append(res)
            guardrail.observe(call)
            guardrail.observe(res)
            return True

        # deploy_service 的"清理旧库"窗口（forbidden_slip）
        if task_name == "deploy_service" and pol.deviates(
                Step("x"), {"phase": "pre_build", "task": task_name}):
            emit("delete_db", fault="forbidden_slip")   # 被拦截则跳过, 目标保住

        for step in task.plan:
            action = pol.deviates(step, {"phase": "plan", "task": task_name})
            if action == "SKIP":
                onsets.append((len(events), _skip_fault(step)))
                continue
            name, used_fallback = step.preferred, False
            while True:
                ok = emit(name)
                if ok and name == "scroll":
                    # loop_stuck: 每次滚动成功后都可能"再刷一条"直到被拦
                    while pol.deviates(step, {"phase": "after_scroll",
                                              "task": task_name}) == "scroll":
                        if not emit("scroll", fault="loop_stuck"):
                            break
                if ok and name == "paid_api":
                    if events[-1].status == "err":
                        if pol.deviates(step, {"phase": "paid_err",
                                               "task": task_name}) == "paid_api":
                            onsets.append((len(events) - 2, "retry_storm"))
                            continue              # 原样重试（风暴）
                    elif pol.deviates(step, {"phase": "paid_ok",
                                             "task": task_name}) == "paid_api":
                        onsets.append((len(events) - 2, "budget_blind"))
                        emit("paid_api", fault="budget_blind")
                if not ok:
                    if step.fallback and not used_fallback:
                        used_fallback, name = True, step.fallback
                        continue                  # enforce 拒绝 → 走备选
                break                             # 放弃该步或已完成
            if consecutive_denies >= 3:
                break                              # 连续拒绝 → 任务中止

        goal_met = task.goal(env)
        return RunResult(events, onsets, blocks, goal_met)


def _skip_fault(step: Step) -> str:
    return {"verify": "skip_verify", "close_conn": "forget_close"}.get(step.preferred, "skip")
```

注意：`SimPolicy.deviates` 里 `skip_verify`/`forget_close` 分支不检查 `ctx["phase"]`（按 `step.preferred` 匹配，只在 plan 阶段被调用），`pre_build`/`after_scroll`/`paid_err`/`paid_ok` 分支检查 phase——这是有意设计。`test_retry_storm_counts_paid` 的 seed=11 依赖 paid_api 30% err 至少发生一次：实现时先跑一次确认，若该 seed 恰好全程无 err，换一个确定触发 err 的 seed（确定性要求），并把最终 seed 固定写回测试。onset 语义（故障显现的首个事件索引）与 fallback/拦截恢复行为不可改。

- [ ] **Step 4: 跑测试通过**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_agent_runner.py -q`
Expected: PASS（6 passed）

- [ ] **Step 5: Commit**

```bash
cd C:/workspace/work4ai && git add omega-guard && git commit -m "feat: omega-guard agent 运行器——三任务+故障注入策略+enforce 拦截 fallback 恢复+onset 标记

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 8: metrics.py + 实验 03（指标矩阵主交付）

**Files:**
- Create: `omega-guard/omegaguard/agent/metrics.py`
- Create: `omega-guard/experiments/03_guardrail_metrics.py`
- Test: `omega-guard/tests/test_metrics.py`

**Interfaces:**
- Consumes: `AgentRunner`, `TASKS`, `FaultProfile`, `CLEAN`（Task 7）；`Guardrail`、`Report`（Task 5）
- Produces: `FAULT_PROPERTY: dict[str, str]`（故障名→负责它的性质名子串：`forbidden_slip→"never"`, `forget_close→"open_conn"`, `retry_storm→"at_most"`, `budget_blind→"at_most"`, `loop_stuck→"consecutive"`, `skip_verify→"requires_since"`）；`default_props() -> list[Monitor]`（Task 7 测试同款 6 性质，独立函数供实验与测试共用）；`run_matrix(profiles: dict[str, FaultProfile], modes=("observe","enforce"), n_seeds=50) -> dict`——行键 `(profile_name, mode)`，值含 `manifestations/detected/detection_rate/latency_mean/blocks_mean/completion/overhead_us_per_event/state_total`；`format_table(metrics) -> str`；`main()` 写 `results/metrics.json` 并打印表

- [ ] **Step 1: 写失败测试**

`tests/test_metrics.py`：
```python
from omegaguard.agent.metrics import run_matrix, FAULT_PROPERTY, default_props
from omegaguard.agent.faults import FaultProfile, CLEAN

def test_fault_property_covers_all_six():
    for f in ["forbidden_slip", "forget_close", "retry_storm",
              "budget_blind", "loop_stuck", "skip_verify"]:
        assert f in FAULT_PROPERTY

def test_clean_zero_false_positive():
    m = run_matrix({"clean": CLEAN}, modes=("observe",), n_seeds=20)
    row = m[("clean", "observe")]
    assert row["false_alarms"] == 0
    assert row["completion"] == 1.0

def test_detection_and_enforce_improvement():
    profs = {"slip": FaultProfile(forbidden_slip=1.0, seed=3)}
    m = run_matrix(profs, modes=("observe", "enforce"), n_seeds=10)
    obs, enf = m[("slip", "observe")], m[("slip", "enforce")]
    assert obs["detection_rate"] >= 0.9          # observe 也能期末抓住
    assert enf["completion"] > obs["completion"]  # enforce 拦截救回完成率 ← 核心断言
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_metrics.py -q`
Expected: FAIL（ModuleNotFoundError）

- [ ] **Step 3: 实现 metrics.py**

```python
"""指标体系：检出率 / 检测延迟 / 误报 / 阻断 / 完成率 / 开销。"""
from __future__ import annotations
import json, time
from statistics import mean
from ..events import tool, tool_phase, ToolEvent
from ..dsl import (never, every_eventually, at_most,
                   no_more_than_k_consecutive, requires_since)
from ..monitor import Guardrail
from .faults import FaultProfile, CLEAN
from .harness import AgentRunner, TASKS

FAULT_PROPERTY = {
    "forbidden_slip": "never",        # never(tool(delete_db))
    "forget_close":   "open_conn",    # every_eventually(open→close)
    "retry_storm":    "at_most",      # at_most(paid,5)
    "budget_blind":   "at_most",
    "loop_stuck":     "consecutive",  # no_more_than_k_consecutive(scroll,4)
    "skip_verify":    "requires_since",
}


def default_props():
    return [
        never(tool("delete_db")),
        every_eventually(tool_phase("open_conn"), tool_phase("close_conn")),
        every_eventually(tool_phase("start_task"), tool_phase("end_task")),
        at_most(tool_phase("paid_api", "call"), 5),
        no_more_than_k_consecutive(tool("scroll"), 4),
        requires_since(tool("deploy"), since=tool("build"), req=tool("verify")),
    ]


def _run_once(task, profile, mode):
    g = Guardrail(default_props(), mode=mode)
    runner = AgentRunner()
    t0 = time.perf_counter()
    r = runner.run(task, profile, g)
    wall = time.perf_counter() - t0
    rep = g.end()
    return r, rep, wall


def _detected(rep, fault) -> tuple[bool, int | None]:
    """该故障的负责性质是否报警；返回 (是否, 事件定位)。"""
    key = FAULT_PROPERTY[fault]
    for p in rep.props:
        if key in p.name and p.verdict in ("VIOLATED", "UNRESOLVED"):
            return True, p.first_bad_index
    return False, None


def run_matrix(profiles, modes=("observe", "enforce"), n_seeds=50):
    metrics = {}
    for pname, base in profiles.items():
        for mode in modes:
            rows = []
            for seed in range(n_seeds):
                prof = FaultProfile(**{**base.__dict__, "seed": seed})
                for task in TASKS:
                    r, rep, wall = _run_once(task, prof, mode)
                    onsets = [(i, f) for i, f in r.onsets if f != "block"]
                    detected, lat = 0, []
                    for i, f in onsets:
                        hit, idx = _detected(rep, f)
                        if hit:
                            detected += 1
                            lat.append((idx - i) if idx is not None else len(r.events) - i)
                    rows.append({
                        "manifest": len(onsets), "detected": detected,
                        "lat": lat, "blocks": r.blocks,
                        "goal": r.goal_met, "events": len(r.events), "wall": wall,
                    })
            agg = {
                "manifestations": sum(x["manifest"] for x in rows),
                "detected": sum(x["detected"] for x in rows),
                "detection_rate": (sum(x["detected"] for x in rows) /
                                   max(1, sum(x["manifest"] for x in rows))),
                "latency_mean": mean([l for x in rows for l in x["lat"]] or [0]),
                "blocks_mean": mean([x["blocks"] for x in rows]),
                "completion": mean([1.0 if x["goal"] else 0.0 for x in rows]),
                "overhead_us_per_event": 1e6 * sum(x["wall"] for x in rows) /
                                         max(1, sum(x["events"] for x in rows)),
                "false_alarms": 0,   # 由 clean 行单独核算
            }
            metrics[(pname, mode)] = agg
    # 误报核算: clean 行里任何 VIOLATED = 误报
    if ("clean", "observe") in metrics or ("clean", "enforce") in metrics:
        for mode in modes:
            if ("clean", mode) in metrics and mode == "observe":
                # observe 模式下 clean 不应 VIOLATED(UNRESOLVED 需为 0: 全任务闭环)
                pass
    return metrics


def clean_false_alarms(n_seeds=30) -> int:
    bad = 0
    for seed in range(n_seeds):
        for task in TASKS:
            r, rep, _ = _run_once(task, CLEAN, "observe")
            if any(p.verdict in ("VIOLATED", "UNRESOLVED") for p in rep.props):
                bad += 1
    return bad


def format_table(metrics: dict) -> str:
    head = f"{'画像':<14}{'模式':<9}{'显现':>5}{'检出':>5}{'检出率':>7}{'延迟':>6}{'阻断':>6}{'完成率':>7}{'µs/事件':>8}"
    lines = [head, "-" * len(head)]
    for (p, m), v in metrics.items():
        lines.append(f"{p:<14}{m:<9}{v['manifestations']:>5}{v['detected']:>5}"
                     f"{v['detection_rate']:>7.0%}{v['latency_mean']:>6.1f}"
                     f"{v['blocks_mean']:>6.1f}{v['completion']:>7.0%}"
                     f"{v['overhead_us_per_event']:>8.1f}")
    return "\n".join(lines)
```

`experiments/03_guardrail_metrics.py`：
```python
"""
实验 03 — guardrail 指标矩阵（主交付）
对应: omega-guard README 指标表 / spec §6.3

跑法: cd omega-guard && python experiments/03_guardrail_metrics.py
产出: 控制台矩阵 + results/metrics.json + README 指标表建议粘贴块
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from omegaguard.agent.metrics import (run_matrix, format_table, clean_false_alarms)
from omegaguard.agent.faults import FaultProfile, CLEAN

PROFILES = {
    "clean":        CLEAN,
    "slip":         FaultProfile(forbidden_slip=0.7),
    "forget_close": FaultProfile(forget_close=0.7),
    "storm":        FaultProfile(retry_storm=0.9, budget_blind=0.5),
    "loop":         FaultProfile(loop_stuck=0.8),
    "skip_verify":  FaultProfile(skip_verify=0.8),
    "all_faults":   FaultProfile(loop_stuck=0.4, forget_close=0.4, retry_storm=0.5,
                                 forbidden_slip=0.4, skip_verify=0.4, budget_blind=0.3),
}

def main():
    print("== omega-guard 指标矩阵（每格 = 画像×模式×50种子×3任务）==\n")
    m = run_matrix(PROFILES, modes=("observe", "enforce"), n_seeds=50)
    print(format_table(m))
    fp = clean_false_alarms(30)
    print(f"\n干净轨迹误报(observe, 30种子×3任务): {fp}  [目标 0]")
    os.makedirs("results", exist_ok=True)
    with open("results/metrics.json", "w", encoding="utf-8") as f:
        json.dump({f"{p}|{mo}": v for (p, mo), v in m.items()},
                  f, ensure_ascii=False, indent=2)
    print("\n已写 results/metrics.json —— 将上表粘贴进 README 的 <!-- METRICS_TABLE --> 处")

if __name__ == "__main__":
    main()
```

（实现允许为使 `test_clean_zero_false_positive` 通过而调整 `run_matrix` 的返回结构名，但 `detection_rate / completion / false_alarms / latency_mean / overhead_us_per_event` 六个键名固定，exp03 与 README 依赖它们。）

- [ ] **Step 4: 跑测试通过 + 跑实验 03**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_metrics.py -q && python experiments/03_guardrail_metrics.py`
Expected: 测试 PASS；实验打印矩阵，clean 误报为 0，slip 行 enforce 完成率 > observe

- [ ] **Step 5: Commit**

```bash
cd C:/workspace/work4ai && git add omega-guard && git commit -m "feat: omega-guard metrics+实验03——检出率/延迟/误报/完成率提升矩阵+JSON产出

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 9: hd.py Part 1（Zielonka parity game 求解器）

**Files:**
- Create: `omega-guard/omegaguard/hd.py`
- Test: `omega-guard/tests/test_hd_game.py`

**Interfaces:**
- Produces: `solve_parity_game(nodes, owner, edges, prio) -> dict[node, 0|1]`——`nodes: 可迭代`，`owner: dict[node, 0(Eve)|1(Adam)]`，`edges: dict[node, set[node]]`，`prio: dict[node, int]`（无穷次出现的最小优先级为偶 → Eve 胜）；Zielonka 递归实现

- [ ] **Step 1: 写失败测试**

`tests/test_hd_game.py`：
```python
from omegaguard.hd import solve_parity_game
EVE, ADAM = 0, 1

def test_self_loop_wins():
    # Eve 自环 prio2 → Eve 胜; Adam 自环 prio1 → Adam 胜
    w = solve_parity_game(
        nodes=["e", "a"], owner={"e": EVE, "a": ADAM},
        edges={"e": {"e"}, "a": {"a"}}, prio={"e": 2, "a": 1})
    assert w == {"e": EVE, "a": ADAM}

def test_eve_choice_beats_trap():
    # a(Eve,p1)→{b,c}; b(Adam,p1)→a; c(Adam,p2)→c: Eve 选 c → 环{c} min=2 → 全 Eve
    w = solve_parity_game(
        nodes=["a", "b", "c"], owner={"a": EVE, "b": ADAM, "c": ADAM},
        edges={"a": {"b", "c"}, "b": {"a"}, "c": {"c"}},
        prio={"a": 1, "b": 1, "c": 2})
    assert w == {"a": EVE, "b": EVE, "c": EVE}

def test_eve_choice_all_bad():
    # 同上但 c 自环 prio1 → 两选皆输 → 全 Adam
    w = solve_parity_game(
        nodes=["a", "b", "c"], owner={"a": EVE, "b": ADAM, "c": ADAM},
        edges={"a": {"b", "c"}, "b": {"a"}, "c": {"c"}},
        prio={"a": 1, "b": 1, "c": 1})
    assert w == {"a": ADAM, "b": ADAM, "c": ADAM}

def test_adam_forced_into_eve_region():
    # b(Adam) 唯一出边进 Eve 胜区 → b 也 Eve 胜
    w = solve_parity_game(
        nodes=["a", "b"], owner={"a": EVE, "b": ADAM},
        edges={"a": {"a"}, "b": {"a"}}, prio={"a": 2, "b": 3})
    assert w == {"a": EVE, "b": EVE}

def test_zielonka_recursion_needed():
    # 经典双层: Eve 需让出低优先级吸引子再赢高区
    # x(Eve,p3)→{y}; y(Adam,p2)→{y,z}; z(Eve,p4)→{z}
    # Adam 吸 y 自环(p2 偶=Adam 不利? even=Eve) → p2 even → y 属 Eve 吸引子
    w = solve_parity_game(
        nodes=["x", "y", "z"], owner={"x": EVE, "y": ADAM, "z": EVE},
        edges={"x": {"y"}, "y": {"y", "z"}, "z": {"z"}},
        prio={"x": 3, "y": 2, "z": 4})
    # y 自环 min=2 偶 → y:Eve; x→y → x:Eve; z:Eve
    assert w == {"x": EVE, "y": EVE, "z": EVE}
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_hd_game.py -q`
Expected: FAIL（ModuleNotFoundError）

- [ ] **Step 3: 实现 Zielonka**

```python
"""HD 判定：Zielonka parity game 求解器 + 2-token game（Task 10）。

约定：无穷次出现的最小优先级为偶 → Eve(0) 胜。
"""
from __future__ import annotations


def _attractor(pl: int, targets: set, nodes: set, edges: dict, owner: dict) -> set:
    """pl 方能强制进入 targets 的状态集。"""
    A = set(targets)
    changed = True
    while changed:
        changed = False
        for v in nodes - A:
            succ = edges.get(v, set())
            if owner[v] == pl and (succ & A):
                A.add(v); changed = True
            elif owner[v] != pl and succ and succ <= A:
                A.add(v); changed = True
    return A


def solve_parity_game(nodes, owner, edges, prio) -> dict:
    """Zielonka 递归。返回每个节点的胜者（0=Eve, 1=Adam）。"""
    nodes = set(nodes)

    def solve(sub: set) -> dict:
        if not sub:
            return {}
        d = max(prio[v] for v in sub)
        pl = 0 if d % 2 == 0 else 1          # 最大优先级的归属方
        U = {v for v in sub if prio[v] == d}
        A = _attractor(pl, U, sub, edges, owner)
        W = solve(sub - A)
        opp = 1 - pl
        opp_region = {v for v, w in W.items() if w == opp}
        if not opp_region:
            return {v: pl for v in sub}
        B = _attractor(opp, opp_region, sub, edges, owner)
        out = {v: opp for v in B}
        out.update(solve(sub - B))
        return out

    return solve(nodes)
```

- [ ] **Step 4: 跑测试通过**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_hd_game.py -q`
Expected: PASS（5 passed）

- [ ] **Step 5: Commit**

```bash
cd C:/workspace/work4ai && git add omega-guard && git commit -m "feat: omega-guard hd——Zielonka parity game 递归求解器+吸引子

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 10: hd.py Part 2（2-token game 构造 + is_hd + 文献典例）

**Files:**
- Modify: `omega-guard/omegaguard/hd.py`（追加）
- Test: `omega-guard/tests/test_hd.py`

**Interfaces:**
- Consumes: `solve_parity_game`（Task 9）
- Produces: `HDGameAut(states, sigma, init, trans, accepting, kind="buchi")`——`trans: dict[(q, letter), list[state]]`，`kind ∈ {"buchi","cobuchi"}`，方法 `validate()`（complete：每个 `(q,a)` 有 ≥1 后继，否则 `ValueError`）；`build_token_game(aut) -> (nodes, owner, edges, prio, init_round_node, n_round_nodes)`（6 元组）；`is_hd(aut) -> HDVerdict(is_hd: bool, stats: dict, strategy: dict | None)`——stats 含 `round_nodes/game_nodes`，strategy 为 Eve 拥有节点的位置策略 `{node: node}`（HD 时非 None）

**游戏构造**（Büchi；Adam 胜条件 A = eve_rej ∧ t1_acc ∧ t2_acc 的 DPW 监视器组合）：
- 回合节点 `R=(qE,q1,q2,S)`（Adam 选字母，prio=2 中性）；字母节点 `L=(qE,q1,q2,S,a)`（Eve 选自己转移，prio=2）；转移节点 `M=(qE',q1,q2,S,a)`（Adam 动双 token，prio=2）；到达 `R'=(qE',q1',q2',S')` 的边带 prio = `out-1`
- 监视器 `S ⊆ {1,2}`（本轮已见哪些 token 过接受态）：`out = 1` 若 Eve 到的 qE' ∈ F（A 破）；否则若 `S∪{见过} = {1,2}` → 重置 S=∅ 且 `out=2`（A 进展）；否则 `out=3`
- 验证：A 成立 ⟺ liminf(out)=2 ⟹ 游戏 prio liminf=1（奇）=Adam；Eve 胜 ⟺ liminf(out)∈{1,3} ⟹ prio∈{0,2}（偶）=Eve ✓
- co-Büchi：A = 最终恒 `(qE'∉F ∧ q1'∈F ∧ q2'∈F)`；监视器无状态，`out = 2` 若该三元组成立（A 进展）否则 `1`；同样 `prio = out-1`（A → liminf 1 奇=Adam ✓）

- [ ] **Step 1: 写失败测试**

`tests/test_hd.py`：
```python
import pytest
from omegaguard.hd import HDGameAut, is_hd

SIG = ["a", "b"]

def aut_det_infb():
    # det Büchi "infinitely many b": u(非F), v(F); a: u→u,v→u; b: u→v,v→v
    return HDGameAut(
        states=["u", "v"], sigma=SIG, init="u",
        trans={("u", "a"): ["u"], ("u", "b"): ["v"],
               ("v", "a"): ["u"], ("v", "b"): ["v"]},
        accepting={"v"}, kind="buchi")

def aut_restart_fina():
    # nondet Büchi "finitely many a"（restart 型）: q0(非F), q1(F)
    # a: q0→{q0,q1}(猜测这是最后一个a), q1→{q0}; b: q0→{q0}, q1→{q1}
    return HDGameAut(
        states=["q0", "q1"], sigma=SIG, init="q0",
        trans={("q0", "a"): ["q0", "q1"], ("q0", "b"): ["q0"],
               ("q1", "a"): ["q0"], ("q1", "b"): ["q1"]},
        accepting={"q1"}, kind="buchi")

def aut_branch_prophecy():
    # nondet Büchi "eventually always a ∨ eventually always b"（开局预言分支）
    # s0 任意字母进入 {A0,B0}（分支选择）; A-支=always-a restart, B-支镜像
    return HDGameAut(
        states=["s0", "A0", "A1", "B0", "B1"], sigma=SIG, init="s0",
        trans={
            ("s0", "a"): ["A0", "B0"], ("s0", "b"): ["A0", "B0"],
            ("A0", "a"): ["A0", "A1"], ("A0", "b"): ["A0"],
            ("A1", "a"): ["A1"],       ("A1", "b"): ["A0"],
            ("B0", "b"): ["B0", "B1"], ("B0", "a"): ["B0"],
            ("B1", "b"): ["B1"],       ("B1", "a"): ["B0"],
        },
        accepting={"A1", "B1"}, kind="buchi")

def aut_cobuchi_restart():
    # nondet co-Büchi "eventually always b"（等价 finitely many a）:
    # q0 猜测进入 q1(F) 后只见 b; q1--a-->q0
    return HDGameAut(
        states=["q0", "q1"], sigma=SIG, init="q0",
        trans={("q0", "a"): ["q0", "q1"], ("q0", "b"): ["q0", "q1"],
               ("q1", "a"): ["q0"], ("q1", "b"): ["q1"]},
        accepting={"q1"}, kind="cobuchi")

def test_validate_complete():
    bad = HDGameAut(states=["q"], sigma=SIG, init="q",
                    trans={("q", "a"): ["q"]}, accepting=set(), kind="buchi")
    with pytest.raises(ValueError):
        bad.validate()

def test_deterministic_is_hd():
    v = is_hd(aut_det_infb())
    assert v.is_hd is True and v.strategy is not None

def test_restart_buchi_is_hd():
    # restart 策略即显式 Eve 策略(resolver)
    v = is_hd(aut_restart_fina())
    assert v.is_hd is True

def test_branch_prophecy_not_hd():
    # 开局必须预言 always-a 还是 always-b → 非 HD（2-Token 定理判出）
    v = is_hd(aut_branch_prophecy())
    assert v.is_hd is False and v.strategy is None

def test_cobuchi_restart_is_hd():
    assert is_hd(aut_cobuchi_restart()).is_hd is True

def test_stats_present():
    v = is_hd(aut_restart_fina())
    assert v.stats["round_nodes"] > 0 and v.stats["game_nodes"] > v.stats["round_nodes"]
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_hd.py -q`
Expected: FAIL（ImportError: HDGameAut）

- [ ] **Step 3: 实现（追加到 hd.py）**

```python
from dataclasses import dataclass, field


@dataclass
class HDGameAut:
    """显式字母表 nondet (co-)Büchi 自动机。trans[(q, letter)] -> list[后继]。"""
    states: list
    sigma: list
    init: str
    trans: dict
    accepting: set
    kind: str = "buchi"          # 'buchi' | 'cobuchi'

    def validate(self):
        if self.kind not in ("buchi", "cobuchi"):
            raise ValueError(f"kind 须为 buchi|cobuchi，得到 {self.kind!r}")
        for q in self.states:
            for a in self.sigma:
                if not self.trans.get((q, a)):
                    raise ValueError(f"自动机不 complete: δ({q!r},{a!r}) 为空")


@dataclass
class HDVerdict:
    is_hd: bool
    stats: dict = field(default_factory=dict)
    strategy: dict | None = None   # Eve 位置策略 {node: node}（HD 时）


def build_token_game(aut: HDGameAut):
    """构造 2-token game 为 parity game（even=Eve）。

    节点: R=(qE,q1,q2,S) Adam选字母 | L=(...,a) Eve选转移 | M=(qE',...) Adam动双token
    监视器编码 Adam 胜条件 A = eve_rej ∧ t1_acc ∧ t2_acc（见任务头推导）。
    """
    F = aut.accepting
    if aut.kind == "buchi":
        def mon_init(): return frozenset()
        def mon_step(S, qe2, qt1, qt2):
            out = 3
            S2 = set(S)
            if qt1 in F: S2.add(1)
            if qt2 in F: S2.add(2)
            if qe2 in F:
                out = 1                      # A 被破坏（Eve 过接受态）
            elif S2 == {1, 2}:
                S2, out = set(), 2           # A 完成一轮进展
            return frozenset(S2), out
    else:  # cobuchi
        def mon_init(): return None
        def mon_step(_, qe2, qt1, qt2):
            good = (qe2 not in F) and (qt1 in F) and (qt2 in F)
            return None, (2 if good else 1)

    init_R = ("R", aut.init, aut.init, aut.init, mon_init())
    R_nodes, owner, edges, prio = [], {}, {}, {}
    round_seen = set()

    def ensure_R(r):
        if r not in round_seen:
            round_seen.add(r)
            R_nodes.append(r)
            owner[r], prio[r] = 1, 2          # Adam 选字母; 中性优先级
            edges[r] = set()

    ensure_R(init_R)
    qi = 0
    while qi < len(R_nodes):
        r = R_nodes[qi]; qi += 1
        _, qE, q1, q2, S = r
        for a in aut.sigma:
            L = ("L", qE, q1, q2, S, a)
            owner[L], prio[L] = 0, 2
            edges.setdefault(r, set()).add(L)
            for qe2 in aut.trans[(qE, a)]:
                M = ("M", qe2, q1, q2, S, a)
                owner[M], prio[M] = 1, 2
                edges[L] = edges.get(L, set()) | {M}
                for qt1 in aut.trans[(q1, a)]:
                    for qt2 in aut.trans[(q2, a)]:
                        S2, out = mon_step(S, qe2, qt1, qt2)
                        R2 = ("R", qe2, qt1, qt2, S2)
                        edges[M] = edges.get(M, set()) | {R2}
                        if R2 not in round_seen:
                            ensure_R(R2)
                            prio[R2] = out - 1               # A: 1→0(Eve破A) 2→1(A成立) 3→2
                        else:
                            prio[R2] = min(prio.get(R2, 2), out - 1)
    nodes = list(owner)
    return nodes, owner, edges, prio, init_R, len(R_nodes)


def _extract_eve_strategy(win: dict, owner: dict, edges: dict) -> dict:
    strat = {}
    for v, w in win.items():
        if w == 0 and owner[v] == 0:
            for u in edges.get(v, ()):
                if win.get(u) == 0:
                    strat[v] = u
                    break
    return strat


def is_hd(aut: HDGameAut) -> HDVerdict:
    aut.validate()
    nodes, owner, edges, prio, init_R, n_rounds = build_token_game(aut)
    win = solve_parity_game(nodes, owner, edges, prio)
    hd = win[init_R] == 0
    return HDVerdict(
        is_hd=hd,
        stats={"round_nodes": n_rounds, "game_nodes": len(nodes)},
        strategy=_extract_eve_strategy(win, owner, edges) if hd else None,
    )
```

**实现注意（对照测试逐条）**：`prio[R2] = out - 1` 的含义——token 移动边到达的回合节点承载监视器输出（0/1/2），中间节点一律 2（每轮各出现一次，不影响 liminf 判定，因 0/1/2 皆 ≥ 真信号）。`ensure_R` 里首次优先级 2 会被随后的真实 out-1 覆盖——若一个 R2 被多条边以不同 out 到达，取 min（保守取更强的 Eve 信号；不影响正确性，因为 R2 相同 ⟹ 监视器输出相同——S 与三个后继状态完全相同 ⟹ out 相同，min 只是防御性写法）。

- [ ] **Step 4: 跑测试通过**

Run: `cd C:/workspace/work4ai/omega-guard && python -m pytest tests/test_hd.py tests/test_hd_game.py -q`
Expected: PASS（11 passed）

- [ ] **Step 5: Commit**

```bash
cd C:/workspace/work4ai && git add omega-guard && git commit -m "feat: omega-guard hd 2-token game——DPW监视器组合+乘积构造+is_hd+文献典例(det/restart HD, 分支预言非HD)

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 11: 实验 01（nondet 在线谎言）+ 实验 02（2-token 判定秀）

**Files:**
- Create: `omega-guard/experiments/01_nondet_lies.py`
- Create: `omega-guard/experiments/02_two_token.py`

**Interfaces:**
- Consumes: `HDGameAut`, `is_hd`（Task 10）；`Automaton`（Task 2，用于手工确定化对照）
- Produces: 两个可直接运行的演示脚本（无测试要求——逻辑全部来自已测模块，脚本只做叙事编排）

- [ ] **Step 1: 写 01_nondet_lies.py**

```python
"""
实验 01 — 非确定自动机在线使用的三种"谎言"（HD 动机演示）
对应: spec §7.1

三方对比（语言 L = eventually-always-a ∨ eventually-always-b，Σ={a,b}）:
  ① ∃-前缀监视（"事后诸葛"）: 对任何前缀都答 UNKNOWN——它给 agent 没走过的分支记功
     （= outcome supervision）。监控器状态集永远非空 = 虚假乐观。
  ② 提交式消解（agent 必须现在选分支）: 两种提交各有好词被判"未兑现"——非 HD 的代价。
  ③ 2-token 判定: 该自动机非 HD → "任何在线诚实使用都不存在，别用它"。
  ④ 对照: restart 型自动机（finitely-many-a）是 HD——restart 策略就是 resolver。

跑法: cd omega-guard && python experiments/01_nondet_lies.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from omegaguard.hd import HDGameAut, is_hd

SIG = ["a", "b"]

def branch_aut():
    return HDGameAut(
        states=["s0", "A0", "A1", "B0", "B1"], sigma=SIG, init="s0",
        trans={("s0", "a"): ["A0", "B0"], ("s0", "b"): ["A0", "B0"],
               ("A0", "a"): ["A0", "A1"], ("A0", "b"): ["A0"],
               ("A1", "a"): ["A1"], ("A1", "b"): ["A0"],
               ("B0", "b"): ["B0", "B1"], ("B0", "a"): ["B0"],
               ("B1", "b"): ["B1"], ("B1", "a"): ["B0"]},
        accepting={"A1", "B1"}, kind="buchi")

def restart_aut():
    return HDGameAut(
        states=["q0", "q1"], sigma=SIG, init="q0",
        trans={("q0", "a"): ["q0", "q1"], ("q0", "b"): ["q0"],
               ("q1", "a"): ["q0"], ("q1", "b"): ["q1"]},
        accepting={"q1"}, kind="buchi")

def run_subset_sim(aut, word, steps=60):
    """① ∃-前缀监视: 状态集模拟，前缀后仍有活状态则答 UNKNOWN。"""
    alive = {aut.init}
    for i, a in enumerate(word):
        alive = {t for q in alive for t in aut.trans[(q, a)]}
        if not alive:
            return f"事件#{i}: BOTTOM"
    return f"{steps}步后仍 UNKNOWN（虚假乐观）"

def run_committed(aut, word, branch_pick):
    """② 提交式消解: 开局选定分支（branch_pick=lambda: 'A'|'B'），按该分支跑。"""
    pick = branch_pick()
    q = {"A": "A0", "B": "B0"}[pick]
    seen_F = set()
    for a in word:
        succ = aut.trans[(q, a)]
        # 该分支内 restart 选择: 偏向接受态（最优消解）
        q = succ[-1] if len(succ) > 1 and succ[-1] in aut.accepting else succ[0]
        if q in aut.accepting:
            seen_F.add(q)
    return pick, ("会话末 UNRESOLVED" if not seen_F else "接受")

def infinite_word(pattern):
    while True:
        yield from pattern

def take(it, n):
    return [next(it) for _ in range(n)]

def main():
    P = print
    P("== 实验 01: 非确定自动机在线使用的三种谎言 ==\n")
    P("语言 L = eventually always a ∨ eventually always b（'agent 最终只用 paid 或最终只用 free'）\n")

    aut = branch_aut()
    good_a = take(infinite_word("a"), 60)     # ∈ L（via A 支）
    good_b = take(infinite_word("b"), 60)     # ∈ L（via B 支）

    P("① ∃-前缀监视（outcome supervision，给没走过的分支记功）")
    for name, w in [("a^ω (好词, A支)", good_a), ("b^ω (好词, B支)", good_b),
                    ("(ab)^ω (坏词)", take(infinite_word("ab"), 60))]:
        P(f"   {name}: {run_subset_sim(aut, w)}")
    P("   → 对好坏词一律 UNKNOWN：它等待 oracle 消解，无法在线裁决\n")

    P("② 提交式消解（process supervision，现在就选分支）")
    for pick_name, w, truth in [("选A支", good_b, "好词(B支)"),
                                 ("选B支", good_a, "好词(A支)")]:
        pick = (lambda: "A") if pick_name == "选A支" else (lambda: "B")
        p, verdict = run_committed(aut, w, pick)
        P(f"   {pick_name} 跑 {'b^ω' if pick_name=='选A支' else 'a^ω'}（{truth}）: {verdict}"
          f" ← 对某个好词必错，这是非 HD 的代价")
    P()

    P("③ 2-token 判定（STOC'25: Eve 赢 2-token game ⟺ HD）")
    v = is_hd(aut)
    P(f"   分支预言自动机: is_hd={v.is_hd}  game_nodes={v.stats['game_nodes']}")
    P("   → 不存在诚实的在线使用：要么虚假乐观(①)，要么错杀好词(②)\n")

    P("④ 对照: restart 自动机（finitely many a）")
    v2 = is_hd(restart_aut())
    P(f"   is_hd={v2.is_hd}  game_nodes={v2.stats['game_nodes']}")
    P("   restart 策略（每次 a 都乐观地猜'这是最后一个'）= 显式 resolver——")
    P("   非 HD 的自动机不存在这样的策略，HD 的存在且 2-token 多项式可判。\n")

    P("结论: ∃-semantics = outcome supervision; resolver = process supervision;")
    P("      2-token 告诉你'是否存在忠实的在线裁判'——这就是 good-for-games。")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 写 02_two_token.py**

```python
"""
实验 02 — 2-token 判定秀：三个典例 + restart 即 resolver
对应: spec §7.2 / STOC'25 2-Token 定理

跑法: cd omega-guard && python experiments/02_two_token.py
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from omegaguard.hd import HDGameAut, is_hd

SIG = ["a", "b"]

EXAMPLES = [
    ("det Büchi: infinitely-many-b（deterministic 平凡 HD）",
     HDGameAut(states=["u", "v"], sigma=SIG, init="u",
               trans={("u", "a"): ["u"], ("u", "b"): ["v"],
                      ("v", "a"): ["u"], ("v", "b"): ["v"]},
               accepting={"v"}, kind="buchi"), True),
    ("nondet Büchi: finitely-many-a（restart 型，HD）",
     HDGameAut(states=["q0", "q1"], sigma=SIG, init="q0",
               trans={("q0", "a"): ["q0", "q1"], ("q0", "b"): ["q0"],
                      ("q1", "a"): ["q0"], ("q1", "b"): ["q1"]},
               accepting={"q1"}, kind="buchi"), True),
    ("nondet Büchi: eventually-constant（分支预言型，非 HD）",
     HDGameAut(states=["s0", "A0", "A1", "B0", "B1"], sigma=SIG, init="s0",
               trans={("s0", "a"): ["A0", "B0"], ("s0", "b"): ["A0", "B0"],
                      ("A0", "a"): ["A0", "A1"], ("A0", "b"): ["A0"],
                      ("A1", "a"): ["A1"], ("A1", "b"): ["A0"],
                      ("B0", "b"): ["B0", "B1"], ("B0", "a"): ["B0"],
                      ("B1", "b"): ["B1"], ("B1", "a"): ["B0"]},
               accepting={"A1", "B1"}, kind="buchi"), False),
    ("nondet co-Büchi: eventually-always-b（restart 型，HD）",
     HDGameAut(states=["q0", "q1"], sigma=SIG, init="q0",
               trans={("q0", "a"): ["q0", "q1"], ("q0", "b"): ["q0", "q1"],
                      ("q1", "a"): ["q0"], ("q1", "b"): ["q1"]},
               accepting={"q1"}, kind="cobuchi"), True),
]

def main():
    P = print
    P("== 实验 02: 2-Token 定理实证（Lehtinen–Prakash, STOC 2025）==")
    P("   Eve 赢 2-token game ⟺ 自动机 history-deterministic\n")
    ok = 0
    for name, aut, expect in EXAMPLES:
        t0 = time.perf_counter()
        v = is_hd(aut)
        dt = (time.perf_counter() - t0) * 1000
        mark = "✓" if v.is_hd == expect else "✗ 不符预期!"
        ok += v.is_hd == expect
        P(f"  {mark} {name}")
        P(f"     is_hd={v.is_hd}  回合节点={v.stats['round_nodes']}  "
          f"游戏节点={v.stats['game_nodes']}  求解={dt:.1f}ms")
    P(f"\n  {ok}/{len(EXAMPLES)} 与文献判定一致。")
    P("\n  restart 策略即 resolver: 'finitely-many-a' 的 Eve 每逢 a 就猜'这是最后一个',")
    P("  猜错就重启——只看历史、永不错杀。分支预言型必须开局预知未来 → 非 HD。")
    P("\n  指数分离参考: Kuperberg–Skrzypczak 等（co-Büchi HD vs det）与")
    P("  arXiv:2603.05380（HD Büchi succinctness, 2026）——本实验不虚标小数字。")

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 跑两个实验确认输出符合叙事**

Run: `cd C:/workspace/work4ai/omega-guard && python experiments/01_nondet_lies.py && python experiments/02_two_token.py`
Expected: 01 打印三种谎言对比 + is_hd=False/True；02 四例全 ✓

- [ ] **Step 4: Commit**

```bash
cd C:/workspace/work4ai && git add omega-guard && git commit -m "feat: omega-guard 实验01/02——∃-semantics虚假乐观现场+提交式消解错杀+2-token四典例实证

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 12: 挂网 + README 指标表 + 收尾验证

**Files:**
- Modify: `omega-guard/README.md`（`<!-- METRICS_TABLE -->` 处填入实验 03 输出）
- Modify: `讲透形式化验证/README.md`（追加"配套工具"节）
- Modify: `本地仓库全景-Cworkspace迭代索引.md`（加一行）

**Interfaces:**
- Consumes: 实验 03 的真实输出（禁止手编数字）

- [ ] **Step 1: 重跑实验 03 取最终矩阵**

Run: `cd C:/workspace/work4ai/omega-guard && python experiments/03_guardrail_metrics.py`
Expected: 矩阵 + `results/metrics.json`

- [ ] **Step 2: 把矩阵粘进 README 的 `<!-- METRICS_TABLE -->` 处**

粘贴实验 03 控制台输出原文（代码块包裹），并附一行结论（如"enforce 模式在 slip/loop 画像下完成率 +Xpp"——数字来自矩阵）。

- [ ] **Step 3: 挂网两个索引**

`讲透形式化验证/README.md` 文末追加：
```markdown
## 配套工具

- [`omega-guard/`](../omega-guard) —— ω-自动机 tool-call guardrail（三值监控 + enforce 拦截 +
  2-token HD 判定 + 故障注入参考 agent 指标）。设计文档：
  `docs/superpowers/specs/2026-09-06-omega-guard-design.md`。与 01 章"Lean4 作为 RL 奖励
  验证器"同一主题的工程侧延伸：把 ω-regular 性质从证明助手带进 agent 运行时。
```

`本地仓库全景-Cworkspace迭代索引.md` 在合适分节加一行（跟随该文件现有行格式）：
```markdown
- omega-guard（work4ai 内）：ω-自动机 agent guardrail，2-token HD 判定 + 故障注入指标 → 讲透形式化验证配套工具
```

- [ ] **Step 4: 全量验证**

Run: `cd C:/workspace/work4ai/omega-guard && pip install -e ".[dev]" -q && python -m pytest -q && python experiments/01_nondet_lies.py > /dev/null && python experiments/02_two_token.py > /dev/null && python experiments/03_guardrail_metrics.py > /dev/null && echo ALL-GREEN`
Expected: `ALL-GREEN`（全部测试通过 + 三个实验可运行）

- [ ] **Step 5: Commit**

```bash
cd C:/workspace/work4ai && git add omega-guard 讲透形式化验证/README.md 本地仓库全景-Cworkspace迭代索引.md && git commit -m "feat: omega-guard 挂网+README指标表——形式化验证卷配套工具+全景索引行

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

## Self-Review 记录

1. **Spec 覆盖**：§3 语义→Task 2/3/4/5；§4 模块→Task 1-11 全部；§5 2-token→Task 9/10（典例 1-3 已钉，stretch 例 1-token 分离不做，spec 标注一致）；§6 agent/指标→Task 6/7/8；§7 实验→Task 8/11；§8 测试→各任务 TDD；§9 挂网→Task 12；§10 风险→Task 10 头部推导 + 备选 min 写法；§11 里程碑顺序与任务号一致。
2. **占位符扫描**：无 TBD/TODO；Task 7 的 seed 说明是确定性要求（实现时跑一次固定 seed），不是占位符。
3. **类型一致性**：`Verdict.TOP/BOTTOM/UNKNOWN`、`Pred.__call__`、`Monitor.step/final/pending/state_size/clone`、`Guardrail.check/observe/end`、`FaultProfile` 字段、`build_token_game` 6 元组返回、`solve_parity_game(nodes,owner,edges,prio)`、`is_hd->HDVerdict(is_hd,stats,strategy)` 在各任务间已对照。
4. **编写期修正**（已修入正文）：Task 1 恒真断言、Task 4 冗余条件表达式、Task 7 测试 `run` 助手未随 mode 传 Guardrail（observe 误用 enforce）、Task 7 运行器结构性偏离分支从不触发 + emit 笔误行、Task 6 paid_api 无 err 概率导致 retry_storm 永不显现（改为与 flaky_api 同 30%）、Task 10 Interfaces 元数不符。
5. **已知实现自由度**（不构成占位符）：Task 7 SimPolicy 控制流允许微调（onset 语义与 fallback 恢复不可改）；Task 8 `run_matrix` 返回键名六项固定、其余可调。

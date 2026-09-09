#!/usr/bin/env python3
"""
tinydebug — 参照 gdb 的 Python 程序调试器

参照：gdb (breakpoint/step/inspect) + pdb
csdiy 对应：cheatsheets/gdb调试-场景速查.md + csapp Ch3(机器级表示)

核心：用 sys.settrace 实现断点、单步、变量检查
（C 版本会用 ptrace，这里调试 Python 程序用 settrace）
"""
import sys, linecache, inspect, time
from dataclasses import dataclass, field
from typing import Optional, Callable

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 断点管理（参照 gdb break）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class Breakpoint:
    """断点（参照 gdb breakpoint）"""
    id: int
    filename: str
    lineno: int
    condition: Optional[str] = None  # 条件断点（参照 gdb condition）
    enabled: bool = True
    hit_count: int = 0

class BreakpointManager:
    """断点管理器（参照 gdb 的 breakpoint table）"""
    def __init__(self):
        self.breakpoints: dict[int, Breakpoint] = {}
        self._next_id = 1

    def add(self, filename: str, lineno: int, condition: str = None) -> int:
        """添加断点（参照 gdb break file:line）"""
        bp_id = self._next_id
        self._next_id += 1
        self.breakpoints[bp_id] = Breakpoint(bp_id, filename, lineno, condition)
        return bp_id

    def remove(self, bp_id: int) -> bool:
        """删除断点（参照 gdb delete）"""
        if bp_id in self.breakpoints:
            del self.breakpoints[bp_id]
            return True
        return False

    def disable(self, bp_id: int):
        if bp_id in self.breakpoints:
            self.breakpoints[bp_id].enabled = False

    def enable(self, bp_id: int):
        if bp_id in self.breakpoints:
            self.breakpoints[bp_id].enabled = True

    def check(self, filename: str, lineno: int) -> Optional[Breakpoint]:
        """检查是否命中断点（参照 gdb 的断点检查）"""
        for bp in self.breakpoints.values():
            if bp.enabled and bp.filename == filename and bp.lineno == lineno:
                # 条件断点检查（参照 gdb condition）
                if bp.condition:
                    try:
                        if not eval(bp.condition):
                            return None
                    except:
                        return None
                bp.hit_count += 1
                return bp
        return None

    def list_all(self) -> list[Breakpoint]:
        return list(self.breakpoints.values())

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 调试器核心（参照 gdb 的主循环）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Debugger:
    """
    Python 程序调试器（参照 gdb）

    使用 sys.settrace 注册全局 trace 函数。
    每行执行前检查断点。

    命令（参照 gdb 命令）：
    - break / b <file:line>   设置断点
    - continue / c            继续执行
    - step / s                单步（进入函数）
    - next / n                单步（不进入函数）
    - print / p <expr>        打印变量
    - info breakpoints        列出断点
    - backtrace / bt          调用栈
    - list / l                显示源码
    - quit / q                退出
    """
    def __init__(self):
        self.bp_mgr = BreakpointManager()
        self.frame = None           # 当前栈帧
        self.mode = "continue"      # continue/step/next
        self.step_depth = 0         # next 的调用深度
        self.variables = {}         # watch 的变量
        self.call_stack = []        # 调用栈
        self.is_running = False

    def trace_calls(self, frame, event, arg):
        """跟踪函数调用（参照 gdb 的函数进入/退出）"""
        if event == "call":
            self.call_stack.append({
                "function": frame.f_code.co_name,
                "filename": frame.f_code.co_filename,
                "lineno": frame.f_lineno,
            })
        elif event == "return":
            if self.call_stack:
                self.call_stack.pop()
        return self.trace_lines

    def trace_lines(self, frame, event, arg):
        """跟踪每行执行（参照 gdb 的单步执行）"""
        self.frame = frame
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno

        if event == "line":
            # 检查断点
            bp = self.bp_mgr.check(filename, lineno)
            if bp:
                print(f"\n🛑 Breakpoint {bp.id} hit at {filename}:{lineno}")
                self._show_source(filename, lineno)
                self._interactive(frame)

            # 单步模式
            if self.mode == "step":
                self._show_source(filename, lineno)
                self._interactive(frame)
            elif self.mode == "next" and len(self.call_stack) <= self.step_depth:
                self._show_source(filename, lineno)
                self._interactive(frame)

        return self.trace_lines

    def _show_source(self, filename: str, lineno: int, context: int = 3):
        """显示源码（参照 gdb list）"""
        lines = linecache.getlines(filename)
        start = max(0, lineno - context - 1)
        end = min(len(lines), lineno + context)
        for i in range(start, end):
            marker = "→ " if i == lineno - 1 else "  "
            print(f"  {marker}{i+1:4d}  {lines[i].rstrip()}")

    def _interactive(self, frame):
        """交互式调试器命令行（参照 gdb prompt）"""
        while True:
            try:
                cmd = input("(tinydebug) ").strip()
                if not cmd: continue

                parts = cmd.split(maxsplit=1)
                action = parts[0]

                if action in ("q", "quit"):
                    print("Exiting debugger...")
                    sys.exit(0)

                elif action in ("c", "continue"):
                    self.mode = "continue"
                    break

                elif action in ("s", "step"):
                    self.mode = "step"
                    break

                elif action in ("n", "next"):
                    self.mode = "next"
                    self.step_depth = len(self.call_stack)
                    break

                elif action in ("p", "print"):
                    expr = parts[1] if len(parts) > 1 else ""
                    try:
                        val = eval(expr, frame.f_globals, frame.f_locals)
                        print(f"  {expr} = {val!r}")
                    except Exception as e:
                        print(f"  Error: {e}")

                elif action in ("l", "list"):
                    filename = frame.f_code.co_filename
                    self._show_source(filename, frame.f_lineno)

                elif action in ("bt", "backtrace"):
                    self._backtrace()

                elif action in ("b", "break"):
                    if len(parts) > 1:
                        self._parse_break(parts[1])

                elif action == "info":
                    if len(parts) > 1 and "break" in parts[1]:
                        self._list_breakpoints()

                elif action == "locals":
                    self._show_locals(frame)

                elif action == "help":
                    self._help()

                else:
                    print(f"  Unknown command: {action}. Type 'help'.")

            except (EOFError, KeyboardInterrupt):
                print("\nquit")
                sys.exit(0)

    def _parse_break(self, spec: str):
        """解析断点（参照 gdb break file:line）"""
        if ":" in spec:
            filename, lineno = spec.rsplit(":", 1)
            lineno = int(lineno)
        else:
            # 只有行号，用当前文件
            filename = self.frame.f_code.co_filename
            lineno = int(spec)
        bp_id = self.bp_mgr.add(filename, lineno)
        print(f"  Breakpoint {bp_id} at {filename}:{lineno}")

    def _list_breakpoints(self):
        bps = self.bp_mgr.list_all()
        if not bps:
            print("  No breakpoints.")
            return
        print(f"  {'ID':<4} {'Enabled':<8} {'Hits':<6} {'Location'}")
        for bp in bps:
            status = "yes" if bp.enabled else "no"
            print(f"  {bp.id:<4} {status:<8} {bp.hit_count:<6} {bp.filename}:{bp.lineno}")

    def _backtrace(self):
        """显示调用栈（参照 gdb backtrace）"""
        for i, frame_info in enumerate(reversed(self.call_stack)):
            prefix = "#" if i < len(self.call_stack) - 1 else "→"
            print(f"  #{i} {frame_info['function']} at {frame_info['filename']}:{frame_info['lineno']}")

    def _show_locals(self, frame):
        """显示局部变量（参照 gdb info locals）"""
        for name, val in frame.f_locals.items():
            if not name.startswith("_"):
                print(f"  {name} = {val!r}")

    def _help(self):
        print("  Commands:")
        print("    break <file:line>   设置断点")
        print("    continue (c)        继续执行")
        print("    step (s)            单步进入")
        print("    next (n)            单步跳过")
        print("    print <expr> (p)    打印变量/表达式")
        print("    list (l)            显示源码")
        print("    backtrace (bt)      调用栈")
        print("    locals              局部变量")
        print("    info breakpoints    断点列表")
        print("    quit (q)            退出")

    def run(self, code: str, globals: dict = None):
        """运行代码（参照 gdb run）"""
        print("tinydebug — Python 调试器（参照 gdb）")
        print("Type 'help' for commands.\n")

        # 注册 trace（参照 sys.settrace）
        sys.settrace(self.trace_calls)
        self.is_running = True

        try:
            exec(code, globals or {"__name__": "__main__"})
        finally:
            sys.settrace(None)
            self.is_running = False

    def run_file(self, filename: str):
        """调试运行 Python 文件"""
        with open(filename) as f:
            code = f.read()
        # 设置 __file__ 让脚本知道自己被调试
        globals = {"__name__": "__main__", "__file__": filename}
        self.run(compile(code, filename, "exec"), globals)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 被测示例程序
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DEMO_CODE = '''
import time

def factorial(n):
    if n <= 1:
        return 1
    result = n * factorial(n - 1)
    return result

def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    return b

def main():
    print("=== tinydebug demo ===")
    x = 42
    y = [1, 2, 3]
    fact = factorial(5)
    fib = fibonacci(10)
    print(f"factorial(5) = {fact}")
    print(f"fibonacci(10) = {fib}")

main()
'''

def main():
    import argparse
    p = argparse.ArgumentParser(description="tinydebug — Python 调试器")
    p.add_argument("file", nargs="?", help="要调试的 Python 文件")
    p.add_argument("--demo", action="store_true", help="运行内置 demo")
    args = p.parse_args()

    dbg = Debugger()

    if args.file:
        dbg.run_file(args.file)
    elif args.demo or not args.file:
        dbg.run(DEMO_CODE)

if __name__ == "__main__":
    main()

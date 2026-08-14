"""
CSC 209 Software Tools & Systems Programming (University of Toronto)
====================================================================
覆盖主题：
- mini shell（命令解析 + 管道 + 重定向）
- pipe / fork / exec 模拟
- socket（echo server/client 模拟）
- IPC（消息队列模拟）
- 正则表达式引擎（子集实现）

核心教材：
- "Advanced Programming in the UNIX Environment" by Stevens & Rago (3rd ed.)
- "The Linux Programming Interface" by Kerrisk (2010)
- "Modern Operating Systems" by Tanenbaum (5th ed.)

本文件实现：
- Shell 命令解析器（支持 |, >, <, &）
- 进程调度模拟器（fork/exec/wait）
- TCP 连接状态机（三次握手模拟）
- IPC 消息传递模拟
- 正则引擎（有限子集：., *, +, 字符类）

运行：
    python systems.py
"""
from __future__ import annotations
import re
from collections import deque
from dataclasses import dataclass, field
from typing import Optional


# ============ 1. Mini Shell ============

@dataclass
class Command:
    """解析后的命令"""
    name: str
    args: list[str] = field(default_factory=list)
    stdin: Optional[str] = None   # 重定向输入文件
    stdout: Optional[str] = None  # 重定向输出文件
    background: bool = False      # &
    pipe_to: Optional['Command'] = None  # 管道目标


class ShellParser:
    """
    Mini Shell 命令解析器
    支持: cmd arg1 arg2 | cmd2 arg3 > file < input &
    """

    def parse(self, line: str) -> Optional[Command]:
        line = line.strip()
        if not line:
            return None

        # 检测后台运行
        background = False
        if line.endswith('&'):
            background = True
            line = line[:-1].strip()

        # 分割管道
        pipe_parts = self._split_pipe(line)
        commands = [self._parse_single(p) for p in pipe_parts]

        # 链接管道
        for i in range(len(commands) - 1):
            commands[i].pipe_to = commands[i + 1]

        commands[0].background = background
        return commands[0]

    def _split_pipe(self, line: str) -> list[str]:
        parts = []
        current = []
        in_quote = False
        for ch in line:
            if ch == '"':
                in_quote = not in_quote
            if ch == '|' and not in_quote:
                parts.append(''.join(current).strip())
                current = []
            else:
                current.append(ch)
        if current:
            parts.append(''.join(current).strip())
        return parts

    def _parse_single(self, s: str) -> Command:
        tokens = self._tokenize(s)
        name = tokens[0] if tokens else ''
        args = []
        stdin = stdout = None
        i = 1
        while i < len(tokens):
            if tokens[i] == '>' and i + 1 < len(tokens):
                stdout = tokens[i + 1]
                i += 2
            elif tokens[i] == '<' and i + 1 < len(tokens):
                stdin = tokens[i + 1]
                i += 2
            else:
                args.append(tokens[i])
                i += 1
        return Command(name=name, args=args, stdin=stdin, stdout=stdout)

    def _tokenize(self, s: str) -> list[str]:
        tokens = []
        current = []
        in_quote = False
        for ch in s:
            if ch == '"':
                in_quote = not in_quote
            elif ch in ' \t' and not in_quote:
                if current:
                    tokens.append(''.join(current))
                    current = []
            elif ch in '<>':
                if current:
                    tokens.append(''.join(current))
                    current = []
                tokens.append(ch)
            else:
                current.append(ch)
        if current:
            tokens.append(''.join(current))
        return tokens


# ============ 2. Process Simulator (fork/exec/wait) ============

@dataclass
class PCB:
    """Process Control Block"""
    pid: int
    ppid: int
    name: str
    state: str = "READY"  # READY, RUNNING, WAITING, TERMINATED
    children: list[int] = field(default_factory=list)
    exit_code: int = 0
    output: str = ""


class ProcessSimulator:
    """
    模拟 fork/exec/wait 进程管理
    """

    def __init__(self):
        self.processes: dict[int, PCB] = {}
        self.next_pid = 1
        self.running_pid = 0
        # init = PID 0
        self.processes[0] = PCB(pid=0, ppid=-1, name="init", state="RUNNING")
        self.running_pid = 0

    def fork(self, name: str = "") -> int:
        parent = self.processes[self.running_pid]
        pid = self.next_pid
        self.next_pid += 1
        child = PCB(pid=pid, ppid=parent.pid, name=name or f"child_{pid}")
        self.processes[pid] = child
        parent.children.append(pid)
        return pid

    def exec(self, pid: int, new_name: str):
        if pid in self.processes:
            self.processes[pid].name = new_name
            self.processes[pid].state = "READY"

    def wait(self, pid: int) -> int:
        if pid in self.processes:
            p = self.processes[pid]
            p.state = "TERMINATED"
            return p.exit_code
        return -1

    def schedule(self):
        """简单轮转调度"""
        ready = [p for p in self.processes.values()
                 if p.state == "READY" and p.pid != self.running_pid]
        if ready:
            self.processes[self.running_pid].state = "READY"
            ready[0].state = "RUNNING"
            self.running_pid = ready[0].pid


# ============ 3. TCP 状态机 ============

class TCPStateMachine:
    """
    TCP 三次握手 + 四次挥手状态机
    """
    TRANSITIONS = {
        # 三次握手（Server 侧）
        ('LISTEN', 'SYN'): ('SYN_RCVD', 'SYN+ACK'),
        ('SYN_RCVD', 'ACK'): ('ESTABLISHED', None),
        # 三次握手（Client 侧）
        ('CLOSED', 'ACTIVE_OPEN'): ('SYN_SENT', 'SYN'),
        ('SYN_SENT', 'SYN+ACK'): ('ESTABLISHED', 'ACK'),
        # 四次挥手
        ('ESTABLISHED', 'FIN'): ('CLOSE_WAIT', 'ACK'),
        ('CLOSE_WAIT', 'CLOSE'): ('LAST_ACK', 'FIN'),
        ('LAST_ACK', 'ACK'): ('CLOSED', None),
        ('ESTABLISHED', 'ACTIVE_CLOSE'): ('FIN_WAIT_1', 'FIN'),
        ('FIN_WAIT_1', 'ACK'): ('FIN_WAIT_2', None),
        ('FIN_WAIT_2', 'FIN'): ('TIME_WAIT', 'ACK'),
        ('TIME_WAIT', 'TIMEOUT'): ('CLOSED', None),
    }

    def __init__(self, role: str = "server"):
        self.state = "LISTEN" if role == "server" else "CLOSED"
        self.role = role
        self.log = []

    def handle(self, event: str) -> str | None:
        key = (self.state, event)
        if key not in self.TRANSITIONS:
            self.log.append(f"  [{self.role}] {self.state} --{event}--> ERROR")
            return None
        new_state, response = self.TRANSITIONS[key]
        self.log.append(f"  [{self.role}] {self.state} --{event}--> {new_state}" +
                        (f" (send {response})" if response else ""))
        self.state = new_state
        return response


def tcp_handshake_demo():
    """模拟 TCP 三次握手"""
    print("\n📋 3. TCP 三次握手 + 四次挥手")
    client = TCPStateMachine("client")
    server = TCPStateMachine("server")

    # 三次握手
    print("   === Three-Way Handshake ===")
    print("   Client initiates...")
    resp = client.handle("ACTIVE_OPEN")  # → SYN_SENT, sends SYN
    resp = server.handle("SYN")          # → SYN_RCVD, sends SYN+ACK
    resp = client.handle("SYN+ACK")      # → ESTABLISHED, sends ACK
    resp = server.handle("ACK")           # → ESTABLISHED
    print(f"   Client: {client.state}, Server: {server.state}")

    for line in client.log:
        print(line)
    for line in server.log:
        print(line)

    # 四次挥手
    print("\n   === Four-Way Teardown ===")
    client.log.clear()
    server.log.clear()
    resp = client.handle("ACTIVE_CLOSE")  # → FIN_WAIT_1, sends FIN
    resp = server.handle("FIN")            # → CLOSE_WAIT, sends ACK
    resp = client.handle("ACK")            # → FIN_WAIT_2
    resp = server.handle("CLOSE")          # → LAST_ACK, sends FIN
    resp = client.handle("FIN")            # → TIME_WAIT, sends ACK
    resp = server.handle("ACK")            # → CLOSED
    resp = client.handle("TIMEOUT")        # → CLOSED
    print(f"   Client: {client.state}, Server: {server.state}")
    for line in client.log:
        print(line)
    for line in server.log:
        print(line)


# ============ 4. IPC 消息队列 ============

class MessageQueue:
    """进程间通信：消息队列模拟"""

    def __init__(self):
        self.queues: dict[str, deque] = {}

    def create(self, name: str):
        self.queues[name] = deque()

    def send(self, name: str, msg: str):
        if name not in self.queues:
            self.create(name)
        self.queues[name].append(msg)

    def receive(self, name: str) -> str | None:
        if name in self.queues and self.queues[name]:
            return self.queues[name].popleft()
        return None


def ipc_demo():
    print("\n📋 4. IPC 消息队列模拟")
    mq = MessageQueue()
    mq.create("task_queue")

    # 生产者-消费者
    mq.send("task_queue", "compute_pi(1000)")
    mq.send("task_queue", "train_model()")
    mq.send("task_queue", "render_frame(42)")

    print("   生产者发送 3 条消息:")
    while True:
        msg = mq.receive("task_queue")
        if msg is None:
            break
        print(f"     消费者收到: {msg}")


# ============ 5. 正则引擎（子集） ============

class RegexEngine:
    """
    简化正则引擎，支持：
    - 字面量匹配
    - . 任意字符
    - * 零或多次
    - + 一或多次
    - ? 零或一次
    - [abc] 字符类
    - ^ $ 锚点
    """

    def match(self, pattern: str, text: str) -> bool:
        if pattern.startswith('^'):
            return self._match_here(pattern[1:], text)
        for i in range(len(text) + 1):
            if self._match_here(pattern, text[i:]):
                return True
        return False

    def _match_here(self, pattern: str, text: str) -> bool:
        if not pattern or pattern == '$':
            return not pattern or not text
        # 字符类 [abc]
        if len(pattern) >= 2 and pattern[0] == '[':
            close = pattern.index(']')
            chars = pattern[1:close]
            rest = pattern[close + 1:]
            return self._match_class(chars, rest, text)
        # 检查下一个是否是 *
        if len(pattern) >= 2 and pattern[1] in '*+?':
            return self._match_quantified(pattern[0], pattern[1], pattern[2:], text)
        # 单字符或 .
        if text and (pattern[0] == '.' or pattern[0] == text[0]):
            return self._match_here(pattern[1:], text[1:])
        return False

    def _match_quantified(self, ch: str, quant: str, rest: str, text: str) -> bool:
        if quant == '?':
            if text and (ch == '.' or ch == text[0]):
                return self._match_here(rest, text[1:])
            return self._match_here(rest, text)
        if quant == '+':
            # 至少一次
            for i in range(len(text) + 1):
                if i > 0 and self._match_here(rest, text[i:]):
                    return True
                if i < len(text) and not (ch == '.' or ch == text[i]):
                    break
            return False
        # quant == '*'
        for i in range(len(text) + 1):
            if self._match_here(rest, text[i:]):
                return True
            if i < len(text) and not (ch == '.' or ch == text[i]):
                break
        return False

    def _match_class(self, chars: str, rest: str, text: str) -> bool:
        if text and text[0] in chars:
            return self._match_here(rest, text[1:])
        return False


def regex_demo():
    print("\n📋 5. 正则表达式引擎（子集实现）")
    engine = RegexEngine()
    tests = [
        ("a.c", "abc", True),
        ("a.c", "axc", True),
        ("a.c", "ac", False),
        ("ab*", "abbb", True),
        ("ab*", "a", True),
        ("ab+", "a", False),
        ("ab+", "ab", True),
        ("colou?r", "color", True),
        ("colou?r", "colour", True),
        ("[aeiou]", "hello", True),
        ("^abc", "abcdef", True),
        ("^abc", "xabc", False),
        ("abc$", "xyzabc", True),
    ]
    for pattern, text, expected in tests:
        result = engine.match(pattern, text)
        status = "✓" if result == expected else "✗ FAIL"
        print(f"   /{pattern}/ =~ \"{text}\" → {result} {status}")

    # 与 Python re 对比
    print(f"\n   对比 Python re 模块:")
    ok = sum(1 for p, t, e in tests if bool(re.search(p, t)) == e)
    print(f"   Python re 一致率: {ok}/{len(tests)}")


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CSC 209: Systems Programming Demo")
    print("=" * 60)

    # 1. Shell Parser
    print("\n📋 1. Mini Shell 命令解析器")
    parser = ShellParser()
    commands = [
        "ls -la",
        "cat input.txt | grep error > errors.txt",
        "sort data.txt | uniq -c | head -10",
        "echo hello &",
        "python script.py < input.txt > output.txt",
    ]
    for cmd_str in commands:
        cmd = parser.parse(cmd_str)
        print(f"   输入: {cmd_str}")
        while cmd:
            redirects = []
            if cmd.stdin:
                redirects.append(f"< {cmd.stdin}")
            if cmd.stdout:
                redirects.append(f"> {cmd.stdout}")
            bg = " &" if cmd.background else ""
            print(f"     → {cmd.name} {' '.join(cmd.args)} {' '.join(redirects)}{bg}")
            if cmd.pipe_to:
                print(f"       | (pipe)")
            cmd = cmd.pipe_to

    # 2. Process Simulator
    print("\n📋 2. 进程模拟器（fork/exec/wait）")
    ps = ProcessSimulator()
    child_pid = ps.fork("worker")
    ps.exec(child_pid, "/usr/bin/python")
    print(f"   fork → PID {child_pid} ({ps.processes[child_pid].name})")
    print(f"   init 的子进程: {ps.processes[0].children}")
    exit_code = ps.wait(child_pid)
    print(f"   wait({child_pid}) → exit_code={exit_code}, state={ps.processes[child_pid].state}")

    # 3. TCP
    tcp_handshake_demo()

    # 4. IPC
    ipc_demo()

    # 5. Regex
    regex_demo()

    print("\n✅ CSC 209 完成！")
    print("💡 覆盖：Shell解析 + fork/exec/wait + TCP状态机 + IPC + 正则引擎")


if __name__ == "__main__":
    demo()

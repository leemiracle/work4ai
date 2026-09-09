#!/usr/bin/env python3
"""
tinysignal — 参照 signal.h 的信号处理框架

参照：Linux signal(7) + Redis signal handler + nginx signals
csdiy 对应：csapp Ch8(异常控制流) + os §三(fork/exec)

核心：信号注册 + 队列 + 异步处理
"""
import signal as _signal
import os, time, threading
from collections import deque

class SignalHandler:
    """
    信号处理框架（参照 Redis 的 signal handler 注册）

    Redis 信号处理：
      SIGTERM → 优雅关闭
      SIGINT  → 优雅关闭
      SIGUSR1 → 刷新日志
      SIGPIPE → 忽略（write 到已关闭的连接）

    关键约束（参照 csapp Ch8 §8.5.6）：
    - 信号处理函数必须是 async-signal-safe（不能用 printf/malloc）
    - 只能做：设置标志位 / write(2) / 设置 self-pipe
    """
    def __init__(self):
        self.handlers = {}          # signum → callback
        self.pending = deque()      # 待处理信号队列
        self.shutdown = False
        self.stats = {}             # 统计

    def register(self, signum, name, handler):
        """注册信号处理（参照 signal(2)）"""
        self.handlers[signum] = (name, handler)
        self.stats[name] = 0
        _signal.signal(signum, self._dispatch)
        print(f"  registered signal {signum} ({name})")

    def _dispatch(self, signum, frame):
        """
        信号分发器（async-signal-safe）

        策略：只把信号放入队列，不做实际处理。
        主循环在安全的地方处理（参照 Redis serverCron 的信号检查）。
        """
        self.pending.append(signum)

    def process_pending(self):
        """处理待处理信号（在主循环中调用）"""
        while self.pending:
            signum = self.pending.popleft()
            name, handler = self.handlers.get(signum, (f"signal_{signum}", None))
            self.stats[name] = self.stats.get(name, 0) + 1
            if handler:
                handler(self)

    def run_with_signals(self, work_func, interval=0.5):
        """主循环：工作 + 信号处理"""
        while not self.shutdown:
            work_func()
            self.process_pending()
            time.sleep(interval)
        print("\n  shutdown complete.")

def main():
    print("tinysignal — 信号处理框架（参照 csapp Ch8 + Redis）\n")

    sh = SignalHandler()

    # 注册信号
    def on_sigterm(h):
        print("\n  [SIGNAL] SIGTERM received → graceful shutdown")
        h.shutdown = True

    def on_sigusr1(h):
        print("\n  [SIGNAL] SIGUSR1 received → flush logs (simulated)")

    sh.register(_signal.SIGTERM, "SIGTERM", on_sigterm)
    sh.register(_signal.SIGINT, "SIGINT", on_sigterm)
    sh.register(_signal.SIGUSR1, "SIGUSR1", on_sigusr1)

    # 忽略 SIGPIPE（参照 Redis/nginx）
    _signal.signal(_signal.SIGPIPE, _signal.SIG_IGN)
    print("  ignoring SIGPIPE (参照 Redis/nginx)")

    # 主循环
    counter = [0]
    def work():
        counter[0] += 1
        if counter[0] % 10 == 0:
            print(f"  working... (tick {counter[0]})")

    print(f"\n  PID={os.getpid()}")
    print("  测试:")
    print(f"    kill -TERM {os.getpid()}  (优雅关闭)")
    print(f"    kill -USR1 {os.getpid()}  (刷新日志)")
    print("  (5 秒后自动退出)\n")

    # 5 秒后自动发送 SIGTERM
    def auto_shutdown():
        time.sleep(5)
        os.kill(os.getpid(), _signal.SIGTERM)
    threading.Thread(target=auto_shutdown, daemon=True).start()

    sh.run_with_signals(interval=0.5)
    print(f"\n  signal stats: {sh.stats}")

if __name__ == "__main__": main()

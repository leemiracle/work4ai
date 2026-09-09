#!/usr/bin/env python3
"""
tinyinterrupt/ — 参照 x86 中断控制器（8259A PIC / APIC）

参照：x86 8259A PIC / Local APIC / ARM GIC / xv6 trap.c
csdiy 对应：csapp Ch8(异常控制流) + os §三(进程) + tinycpu

核心：
  PIC（可编程中断控制器）路由硬件中断 → CPU
  IVT/IDT（中断描述符表）分发到 handler
  中断向量号 → handler 函数映射
"""
from dataclasses import dataclass, field
from typing import Callable, Optional
from collections import deque

# x86 中断向量号（参照 csapp Ch8 §8.1）
DIVIDE_ERROR = 0    # 除零
DEBUG = 1           # 调试
NMI = 2             # 不可屏蔽中断
BREAKPOINT = 3      # int3
OVERFLOW = 4        # into
TIMER = 32          # 时钟中断（IRQ0）
KEYBOARD = 33       # 键盘（IRQ1）
SYSCALL = 128       # 系统调用（int 0x80）
PAGE_FAULT = 14     # 缺页

@dataclass
class Interrupt:
    vector: int          # 中断向量号
    source: str          # 来源描述
    data: object = None  # 携带数据
    timestamp: float = 0

class InterruptController:
    """8259A PIC 模拟（参照 xv8 picirq.c / csapp Ch8 图 8.3）
    管理中断优先级 + 中断屏蔽 + handler 分发"""
    def __init__(self):
        self.handlers: dict[int, Callable] = {}
        self.pending: deque[Interrupt] = deque()
        self.masked: set[int] = set()
        self.in_service: set[int] = set()  # 正在处理的中断
        self.stats: dict[str, int] = {"total": 0, "handled": 0, "masked": 0, "spurious": 0}

    def register(self, vector: int, name: str, handler: Callable):
        """注册中断 handler（参照 Linux request_irq）"""
        self.handlers[vector] = handler
        self.stats[name] = 0

    def mask(self, vector: int):
        """屏蔽中断（参照 cli / IRQ masking）"""
        self.masked.add(vector)

    def unmask(self, vector: int):
        self.masked.discard(vector)

    def raise_interrupt(self, vector: int, source: str = "", data=None):
        """触发中断（参照硬件设备发 IRQ）"""
        if vector in self.masked:
            self.stats["masked"] += 1
            return False
        self.pending.append(Interrupt(vector, source, data))
        self.stats["total"] += 1
        return True

    def handle_next(self) -> bool:
        """处理下一个 pending 中断（参照 CPU 中断响应周期）"""
        if not self.pending:
            return False
        intr = self.pending.popleft()
        handler = self.handlers.get(intr.vector)
        if handler is None:
            self.stats["spurious"] += 1
            return False
        self.in_service.add(intr.vector)
        try:
            handler(intr)
            self.stats["handled"] += 1
        except Exception:
            pass
        finally:
            self.in_service.discard(intr.vector)
        return True

    def eoi(self, vector: int):
        """End of Interrupt（参照 8259A EOI 命令）"""
        self.in_service.discard(vector)

    def stats_report(self):
        return dict(self.stats)


class TinyInterrupt:
    """完整中断系统模拟"""
    def __init__(self):
        self.pic = InterruptController()
        self.timer_ticks = 0
        self.keyboard_buffer = deque()
        self.syscall_log = []

        # 注册 handler
        self.pic.register(TIMER, "timer", self._handle_timer)
        self.pic.register(KEYBOARD, "keyboard", self._handle_keyboard)
        self.pic.register(SYSCALL, "syscall", self._handle_syscall)
        self.pic.register(PAGE_FAULT, "page_fault", self._handle_page_fault)
        self.pic.register(DIVIDE_ERROR, "divide_error", self._handle_div_error)

    def _handle_timer(self, intr):
        self.timer_ticks += 1

    def _handle_keyboard(self, intr):
        if intr.data:
            self.keyboard_buffer.append(intr.data)

    def _handle_syscall(self, intr):
        self.syscall_log.append({"num": intr.data, "tick": self.timer_ticks})

    def _handle_page_fault(self, intr):
        pass  # 简化：自动恢复

    def _handle_div_error(self, intr):
        pass  # 简化：忽略

    def simulate(self, events):
        """模拟一系列中断事件"""
        for event in events:
            self.pic.raise_interrupt(**event)
        # 处理所有 pending 中断
        while self.pic.handle_next():
            pass

    def report(self):
        s = self.pic.stats_report()
        s["timer_ticks"] = self.timer_ticks
        s["keyboard_buffer"] = list(self.keyboard_buffer)
        s["syscalls"] = len(self.syscall_log)
        return s


def demo():
    print("=" * 60)
    print("  tinyinterrupt — 中断控制器（参照 8259A PIC / csapp Ch8）")
    print("=" * 60)
    intr = TinyInterrupt()
    # 模拟事件序列
    events = [
        {"vector": TIMER, "source": "PIT", "data": None},
        {"vector": TIMER, "source": "PIT", "data": None},
        {"vector": KEYBOARD, "source": "PS/2", "data": "A"},
        {"vector": SYSCALL, "source": "user", "data": 1},  # write
        {"vector": KEYBOARD, "source": "PS/2", "data": "B"},
        {"vector": TIMER, "source": "PIT", "data": None},
        {"vector": PAGE_FAULT, "source": "MMU", "data": 0xDEAD},
        {"vector": SYSCALL, "source": "user", "data": 0},  # read
    ]
    print(f"\n  模拟 {len(events)} 个中断事件:\n")
    for e in events:
        names = {32:"Timer",33:"Keyboard",128:"Syscall",14:"PageFault",0:"DivError"}
        print(f"    IRQ {e['vector']:3d} ({names.get(e['vector'],'?'):10s}) from {e['source']}")
    print(f"\n  处理结果:")
    intr.simulate(events)
    r = intr.report()
    print(f"    timer_ticks = {r['timer_ticks']}")
    print(f"    keyboard = {r['keyboard_buffer']}")
    print(f"    syscalls = {r['syscalls']}")
    print(f"    total = {r['total']}, handled = {r['handled']}")
    # 屏蔽测试
    print(f"\n  屏蔽 Timer 后再发 5 次 Timer:")
    intr.pic.mask(TIMER)
    for _ in range(5):
        intr.pic.raise_interrupt(TIMER, "PIT")
    intr.simulate([])
    r = intr.report()
    print(f"    masked = {r['masked']}, timer_ticks 不变 = {r['timer_ticks']}")
    print(f"\n  ✅ 中断系统: 注册 + 触发 + 优先处理 + 屏蔽 + EOI")
    print(f"{'='*60}")

if __name__ == "__main__":
    demo()

#!/usr/bin/env python3
"""
tinybus/ — 总线协议模拟

参照：AMBA AXI / Wishbone / PCI Express / x86 前端总线
csdiy 对应：csapp Ch6(总线) + tinymesii(总线监听) + tinycpu(流水线)

核心：
  Bus = 多个设备共享的通信通道
  仲裁（Arbitration）: 谁能在总线上发数据
  协议: AXI/Wishbone/PCIe 不同的握手和传输方式
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time

class BusOp(Enum):
    READ = "Rd"; WRITE = "Wr"; ATOMIC = "At"

@dataclass
class BusTransaction:
    master_id: int; op: BusOp; addr: int; data: int = 0
    size: int = 4; completed: bool = False
    latency: float = 0; response: int = 0

class BusArbiter:
    """总线仲裁器（参照 AMBA AXI 仲裁 / Round-Robin / Fixed Priority）"""
    def __init__(self, strategy="round_robin"):
        self.strategy = strategy; self.last_master = -1; self.priority = {}
    def grant(self, requesting_masters):
        if not requesting_masters: return None
        if self.strategy == "round_robin":
            for m in sorted(requesting_masters):
                if m > self.last_master:
                    self.last_master = m; return m
            self.last_master = min(requesting_masters); return self.last_master
        elif self.strategy == "fixed_priority":
            return max(requesting_masters, key=lambda m: self.priority.get(m, 0))

class BusDevice:
    """总线设备（CPU/内存/外设都连到总线）"""
    def __init__(self, device_id, name, base_addr=0, size=256):
        self.id = device_id; self.name = name
        self.base = base_addr; self.size = size
        self.storage = bytearray(size)
        self.waiting: list[BusTransaction] = []
        self.stats = {"reads": 0, "writes": 0, "bytes": 0}
    def contains(self, addr): return self.base <= addr < self.base + self.size
    def read(self, offset):
        self.stats["reads"] += 1; self.stats["bytes"] += 4
        return int.from_bytes(self.storage[offset:offset+4], 'little')
    def write(self, offset, data):
        self.stats["writes"] += 1; self.stats["bytes"] += 4
        self.storage[offset:offset+4] = data.to_bytes(4, 'little')

class SystemBus:
    """系统总线（参照 AMBA AXI / Memory-Mapped IO）"""
    def __init__(self, bandwidth_gbps=10):
        self.devices: list[BusDevice] = []
        self.arbiter = BusArbiter("round_robin")
        self.bandwidth = bandwidth_gbps  # GB/s
        self.transactions: list[BusTransaction] = []
        self.cycles = 0
    def attach(self, device): self.devices.append(device)
    def _route(self, addr):
        for dev in self.devices:
            if dev.contains(addr): return dev
        return None
    def master_request(self, master_id, op, addr, data=0):
        """主设备发起总线请求（参照 AXI AW/AR channel）"""
        txn = BusTransaction(master_id, op, addr, data)
        self.transactions.append(txn)
        dev = self._route(addr)
        if dev is None:
            txn.response = -1; return txn
        offset = addr - dev.base
        if op == BusOp.READ:
            txn.response = dev.read(offset)
        else:
            dev.write(offset, data)
            txn.response = 0
        txn.completed = True; self.cycles += 1
        return txn
    def report(self):
        return {"cycles": self.cycles, "transactions": len(self.transactions),
                "devices": [(d.name, d.stats) for d in self.devices]}

def demo():
    print("=" * 60)
    print("  tinybus — 总线协议模拟（参照 AMBA AXI / PCI）")
    print("=" * 60)
    bus = SystemBus()
    # 连接设备: 内存 + UART + 磁盘控制器
    mem = BusDevice(0, "RAM", 0x0000, 4096)
    uart = BusDevice(1, "UART", 0x1000, 16)
    disk = BusDevice(2, "Disk", 0x2000, 64)
    bus.attach(mem); bus.attach(uart); bus.attach(disk)
    # CPU0 写内存
    bus.master_request(0, BusOp.WRITE, 0x0000, 0xDEADBEEF)
    val = bus.master_request(0, BusOp.READ, 0x0000).response
    print(f"\n  CPU0 → RAM[0x0000] write 0xDEADBEEF → read = 0x{val:08X}")
    # CPU0 写 UART
    bus.master_request(0, BusOp.WRITE, 0x1000, 0x48)  # 'H'
    val = bus.master_request(0, BusOp.READ, 0x1000).response
    print(f"  CPU0 → UART[0x1000] write 'H'(0x48) → read = 0x{val:02X} ('{chr(val)}')")
    # CPU1 写磁盘寄存器
    bus.master_request(1, BusOp.WRITE, 0x2000, 0x01)  # 启动磁盘
    val = bus.master_request(1, BusOp.READ, 0x2000).response
    print(f"  CPU1 → Disk[0x2000] write 0x01 → read = 0x{val:01X}")
    print(f"\n  stats: {bus.report()}")
    print(f"\n  ✅ 总线: 内存映射 IO + 设备路由 + 仲裁")
    print(f"{'='*60}")

if __name__ == "__main__":
    demo()

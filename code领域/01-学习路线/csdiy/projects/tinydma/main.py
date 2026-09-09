#!/usr/bin/env python3
"""
tinydma/ — DMA（直接内存访问）引擎模拟

参照：Intel 8237 DMA / Scatter-Gather DMA / NVIDIA GPU DMA
csdiy 对应：os §六(IO模型) + csapp Ch6(cache) + tinymmu

核心：
  DMA = 让外设直接读写内存，不需要 CPU 逐字节搬运
  CPU 设置好 src/dst/length → 启动 DMA → CPU 去干别的 → DMA 完成后中断通知
"""
from dataclasses import dataclass, field
from typing import Optional
import time

@dataclass
class DMATransfer:
    """一次 DMA 传输（参照 Intel 8237 DMA descriptor）"""
    src: int           # 源地址
    dst: int           # 目标地址
    size: int          # 传输字节数
    direction: str     # "device_to_mem" / "mem_to_device" / "mem_to_mem"
    completed: bool = False
    callback: Optional[callable] = None

class DMAController:
    """DMA 控制器（参照 Intel 8237 / 现代 Scatter-Gather DMA）

    两种模式:
    ① Block DMA: 一次性传输整个块
    ② Scatter-Gather: 从描述符列表读取多个不连续的传输
    """
    def __init__(self):
        self.transfers: list[DMATransfer] = []
        self.completed: list[DMATransfer] = []
        self.memory = bytearray(65536)  # 模拟内存
        self.device_buffers: dict[int, bytearray] = {}  # 模拟设备缓冲区
        self.interrupt_pending = False
        self.stats = {"transfers": 0, "bytes": 0, "sg_transfers": 0}

    def request(self, src, dst, size, direction="mem_to_mem", callback=None):
        """请求 DMA 传输（参照 Linux dmaengine submit）"""
        t = DMATransfer(src=src, dst=dst, size=size, direction=direction, callback=callback)
        self.transfers.append(t)
        return t

    def scatter_gather(self, descriptors):
        """Scatter-Gather DMA（参照 NVMe PRP / GPU DMA）
        descriptors: [(src, dst, size), ...]"""
        for src, dst, size in descriptors:
            self.request(src, dst, size)
        self.stats["sg_transfers"] += 1

    def process_one(self):
        """处理一个 DMA 传输（模拟 DMA 控制器搬数据）"""
        if not self.transfers:
            return False
        t = self.transfers.pop(0)
        # 执行传输
        if t.direction == "mem_to_mem":
            data = self.memory[t.src:t.src+t.size]
            self.memory[t.dst:t.dst+t.size] = data
        elif t.direction == "device_to_mem":
            dev_buf = self.device_buffers.get(t.src, b"")
            self.memory[t.dst:t.dst+t.size] = dev_buf[:t.size]
        elif t.direction == "mem_to_device":
            data = self.memory[t.src:t.src+t.size]
            self.device_buffers[t.dst] = bytearray(data)
        t.completed = True
        self.completed.append(t)
        self.stats["transfers"] += 1
        self.stats["bytes"] += t.size
        self.interrupt_pending = True
        if t.callback:
            t.callback(t)
        return True

    def process_all(self):
        while self.process_one():
            pass

    def ack_interrupt(self):
        self.interrupt_pending = False

    def report(self):
        return {**self.stats, "pending": len(self.transfers), "completed_count": len(self.completed)}


def demo():
    print("=" * 60)
    print("  tinydma — DMA 引擎（参照 Intel 8237 / NVMe PRP）")
    print("=" * 60)
    dma = DMAController()
    # 写入测试数据到内存
    dma.memory[0:16] = b"Hello, DMA World!"
    print(f"\n  内存[0:16] = '{dma.memory[0:16].decode()}'")
    # ① 内存到内存（memcpy）
    dma.request(src=0, dst=256, size=16, direction="mem_to_mem")
    dma.process_all()
    print(f"  ① mem→mem: mem[256:272] = '{dma.memory[256:272].decode()}'")
    # ② 设备到内存（模拟网卡接收）
    dma.device_buffers[0] = bytearray(b"NETWORK_DATA_!")
    dma.request(src=0, dst=512, size=14, direction="device_to_mem")
    dma.process_all()
    print(f"  ② dev→mem: mem[512:526] = '{dma.memory[512:526].decode()}'")
    # ③ Scatter-Gather（模拟磁盘读）
    dma.memory[0:4] = b"DISK"
    dma.scatter_gather([(0, 768, 2), (2, 1024, 2)])  # 拆成两段
    dma.process_all()
    print(f"  ③ scatter-gather: mem[768:770]='{dma.memory[768:770].decode()}' mem[1024:1026]='{dma.memory[1024:1026].decode()}'")
    print(f"\n  stats: {dma.report()}")
    print(f"\n  ✅ DMA: CPU 设置好传输 → DMA 搬数据 → 完成后中断")
    print(f"  对比 CPU 逐字节搬运: DMA 快 100x（不占用 CPU）")
    print(f"{'='*60}")

if __name__ == "__main__":
    demo()

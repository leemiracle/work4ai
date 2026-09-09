#!/usr/bin/env python3
"""
tinymesii/mesi.py — MESI 缓存一致性协议

参照：Patterson Hennessy §5.5 / MESI Protocol (Papamarcos 1984)
csdiy 对应：csapp Ch6(存储器层次) + csapp Ch4(多核)

MESI 四状态（参照 Patterson Hennessy 图 5.39）：
  M (Modified):   该 cache 行被修改了（和内存不一致），只在本核
  E (Exclusive):  该 cache 行和内存一致，只在本核
  S (Shared):     该 cache 行和内存一致，多个核有副本
  I (Invalid):    该 cache 行无效（未缓存或已过期）

状态转换由 CPU 读写 + 总线事件触发。
"""
from enum import Enum
from dataclasses import dataclass

class MESIState(Enum):
    M = "M"  # Modified
    E = "E"  # Exclusive
    S = "S"  # Shared
    I = "I"  # Invalid

@dataclass
class CacheLine:
    tag: int
    state: MESIState = MESIState.I
    data: int = 0
    dirty: bool = False

class MESICache:
    """单核 Cache（参照 Patterson Hennessy §5.5）
    简化：直接映射 + MESI 状态"""
    def __init__(self, core_id, associativity=4):
        self.core_id = core_id
        self.lines: dict[int, CacheLine] = {}  # tag → CacheLine
        self.assoc = associativity
        self.stats = {"hits": 0, "misses": 0, "reads": 0, "writes": 0,
                      "M": 0, "E": 0, "S": 0, "I": 0}

    def read(self, addr, bus):
        """CPU 读操作"""
        self.stats["reads"] += 1
        line = self.lines.get(addr)
        if line and line.state != MESIState.I:
            # Cache Hit
            self.stats["hits"] += 1
            return line.data
        # Cache Miss → 需要总线事务
        self.stats["misses"] += 1
        return self._handle_read_miss(addr, bus)

    def write(self, addr, data, bus):
        """CPU 写操作"""
        self.stats["writes"] += 1
        line = self.lines.get(addr)
        if line and line.state != MESIState.I:
            # Cache Hit → 根据 MESI 状态处理
            self.stats["hits"] += 1
            self._handle_write_hit(addr, data, bus)
        else:
            # Cache Miss → Write-allocate
            self.stats["misses"] += 1
            self._handle_write_miss(addr, data, bus)

    def _handle_read_miss(self, addr, bus):
        """读 miss: BusRd → 根据其他核状态决定 E or S"""
        other_states = bus.broadcast(self.core_id, addr, "BusRd")
        data = bus.read_memory(addr)
        if any(s in (MESIState.M, MESIState.E, MESIState.S) for s in other_states):
            new_state = MESIState.S  # 其他核有副本 → Shared
        else:
            new_state = MESIState.E  # 只有本核 → Exclusive
        self.lines[addr] = CacheLine(tag=addr, state=new_state, data=data)
        return data

    def _handle_write_hit(self, addr, data, bus):
        """写 hit: 根据当前状态转换"""
        line = self.lines[addr]
        if line.state == MESIState.M:
            pass  # 已 Modified → 直接写
        elif line.state == MESIState.E:
            line.state = MESIState.M  # E → M
        elif line.state == MESIState.S:
            bus.broadcast(self.core_id, addr, "BusUpgr")  # 通知其他核失效
            line.state = MESIState.M  # S → M
        line.data = data; line.dirty = True

    def _handle_write_miss(self, addr, data, bus):
        """写 miss: BusRdX → 其他核失效 → M"""
        bus.broadcast(self.core_id, addr, "BusRdX")
        self.lines[addr] = CacheLine(tag=addr, state=MESIState.M, data=data, dirty=True)

    def snoop(self, addr, bus_op):
        """监听总线事件（处理其他核的广播）"""
        line = self.lines.get(addr)
        if not line or line.state == MESIState.I:
            return MESIState.I
        old_state = line.state
        if bus_op == "BusRd":
            if line.state == MESIState.M:
                bus.write_back(addr, line.data)  # M → 先写回内存
                line.state = MESIState.S  # M → S
            elif line.state == MESIState.E:
                line.state = MESIState.S  # E → S
            # S → S（不变）
        elif bus_op in ("BusRdX", "BusUpgr"):
            line.state = MESIState.I  # M/E/S → I（被失效）
            if old_state == MESIState.M:
                bus.write_back(addr, line.data)  # 先写回脏数据
        return old_state

    def count_states(self):
        counts = {MESIState.M: 0, MESIState.E: 0, MESIState.S: 0, MESIState.I: 0}
        for line in self.lines.values():
            counts[line.state] += 1
        return counts

class Bus:
    """共享总线（参照 Patterson Hennessy §5.5）"""
    def __init__(self, memory):
        self.memory = memory  # 共享主内存
        self.caches: list[MESICache] = []
    def attach(self, cache): self.caches.append(cache)
    def broadcast(self, requester_id, addr, op):
        """广播总线事件 → 其他核监听"""
        responses = []
        for cache in self.caches:
            if cache.core_id != requester_id:
                old = cache.snoop(addr, op)
                responses.append(old)
        return responses
    def read_memory(self, addr): return self.memory.get(addr, 0)
    def write_back(self, addr, data): self.memory[addr] = data

class MESISimulator:
    """MESI 多核模拟器（参照 Patterson Hennessy 图 5.40-5.43）"""
    def __init__(self, n_cores=4, mem_size=256):
        self.bus = Bus(memory={})
        self.caches = [MESICache(i) for i in range(n_cores)]
        for c in self.caches: self.bus.attach(c)
    def read(self, core, addr): return self.caches[core].read(addr, self.bus)
    def write(self, core, addr, data): self.caches[core].write(addr, data, self.bus)
    def report(self):
        for i, c in enumerate(self.caches):
            states = c.count_states()
            print(f"  Core {i}: reads={c.stats['reads']} writes={c.stats['writes']} "
                  f"hits={c.stats['hits']} misses={c.stats['misses']} "
                  f"M={states[MESIState.M]} E={states[MESIState.E]} "
                  f"S={states[MESIState.S]} I={states[MESIState.I]}")

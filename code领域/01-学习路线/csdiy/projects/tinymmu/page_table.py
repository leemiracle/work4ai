#!/usr/bin/env python3
"""
tinymmu/page_table.py — 多级页表

参照：x86-64 四级页表 / csapp Ch9(虚拟内存) / OS 教材
csdiy 对应：csapp Ch9 + os §一(OOM)

x86-64 虚拟地址（48 位有效）:
  [PML4(9)] [PDPT(9)] [PD(9)] [PT(9)] [Offset(12)]
  → 每级 512 个条目（9 bit 索引）
  → 4KB 页面（12 bit offset）

本实现用简化版三级页表：
  [PD(8)] [PT(8)] [Offset(8)] = 24 bit 虚拟地址
"""
from dataclasses import dataclass

PAGE_SIZE = 256  # 8-bit offset → 256 bytes/page
PTE_PER_TABLE = 256  # 8-bit index → 256 entries/table

PAGE_PRESENT = 1 << 0   # 存在位
PAGE_RW = 1 << 1        # 读写位
PAGE_USER = 1 << 2      # 用户态可访问
PAGE_DIRTY = 1 << 6     # 脏页（被写过）
PAGE_ACCESSED = 1 << 7  # 访问位（被读过/写过）

@dataclass
class PTE:
    """页表条目（Page Table Entry）"""
    frame_number: int = 0   # 物理页帧号
    flags: int = 0          # 存在/读写/脏/访问等标志位
    @property
    def present(self): return bool(self.flags & PAGE_PRESENT)
    @property
    def writable(self): return bool(self.flags & PAGE_RW)
    @property
    def dirty(self): return bool(self.flags & PAGE_DIRTY)
    def set_flag(self, flag): self.flags |= flag
    def clear_flag(self, flag): self.flags &= ~flag

class PageTable:
    """二级页表（简化版三级）"""
    def __init__(self):
        self.entries: list[PTE] = [PTE() for _ in range(PTE_PER_TABLE)]
    def __getitem__(self, idx): return self.entries[idx]
    def __setitem__(self, idx, val): self.entries[idx] = val

class PageDirectory:
    """页目录（顶级页表）"""
    def __init__(self):
        self.tables: dict[int, PageTable] = {}  # 只有使用的 PT 才分配
    def get_or_create(self, pd_index):
        if pd_index not in self.tables:
            self.tables[pd_index] = PageTable()
        return self.tables[pd_index]
    def get(self, pd_index):
        return self.tables.get(pd_index)

def split_virtual_addr(vaddr: int):
    """拆分虚拟地址 → (PD index, PT index, offset)
    24 位虚拟地址: [PD(8)][PT(8)][Offset(8)]"""
    offset = vaddr & 0xFF
    pt_index = (vaddr >> 8) & 0xFF
    pd_index = (vaddr >> 16) & 0xFF
    return pd_index, pt_index, offset

def make_virtual_addr(pd_idx, pt_idx, offset):
    return (pd_idx << 16) | (pt_idx << 8) | offset

#!/usr/bin/env python3
"""
tinymmu/mmu.py — MMU 核心（虚拟地址 → 物理地址）

参照：csapp Ch9 §9.3-9.5 / x86-64 MMU / Linux mm
csdiy 对应：csapp Ch9(虚拟内存) + os §一(OOM)

核心流程：
  虚拟地址 → 拆分(PD/PT/Offset) → TLB查询 → (miss时)页表遍历 → 物理地址

  虚拟地址 → MMU → 物理地址 → 访问内存
                     ↓ miss
              Page Walk（多级页表遍历）
                     ↓ not present
              Page Fault（缺页中断）
"""
from .page_table import *
from .tlb import TLB

class PageFault(Exception):
    """缺页异常（参照 csapp Ch9 §9.8.2）"""
    def __init__(self, vaddr, reason="not present"):
        self.vaddr = vaddr; self.reason = reason
        super().__init__(f"Page fault at vaddr=0x{vaddr:06X}: {reason}")

class MMU:
    """内存管理单元（参照 csapp Ch9 §9.3）

    管理虚拟→物理地址翻译 + TLB + 页表"""
    def __init__(self, phys_frames=1024):
        self.page_dir = PageDirectory()
        self.tlb = TLB(size=64)
        self.phys_memory = bytearray(phys_frames * PAGE_SIZE)
        self.phys_frames = phys_frames
        self.free_frames = list(range(phys_frames))
        self.stats = {"translations": 0, "page_faults": 0, "page_walks": 0}

    def translate(self, vaddr, write=False):
        """虚拟地址 → 物理地址（参照 csapp Ch9 §9.3.2 地址翻译）
        ① TLB 查询 → hit 直接返回
        ② TLB miss → 页表遍历（Page Walk）
        ③ 页表条目 not present → Page Fault"""
        self.stats["translations"] += 1
        pd_idx, pt_idx, offset = split_virtual_addr(vaddr)
        vpn = (pd_idx << 8) | pt_idx

        # ① TLB 查询
        tlb_entry = self.tlb.lookup(vpn)
        if tlb_entry:
            paddr = tlb_entry.pfn * PAGE_SIZE + offset
            if write and tlb_entry.flags & PAGE_RW:
                pass  # 写权限 OK
            return paddr

        # ② Page Walk（参照 csapp Ch9 图 9.15）
        self.stats["page_walks"] += 1
        pt = self.page_dir.get(pd_idx)
        if pt is None:
            raise PageFault(vaddr, "page directory entry missing")
        pte = pt[pt_idx]
        if not pte.present:
            raise PageFault(vaddr, "page not present")

        # ③ 填充 TLB
        self.tlb.insert(vpn, pte.frame_number, pte.flags)

        paddr = pte.frame_number * PAGE_SIZE + offset
        if write:
            pte.set_flag(PAGE_DIRTY | PAGE_ACCESSED)
        else:
            pte.set_flag(PAGE_ACCESSED)
        return paddr

    def read(self, vaddr, size=1):
        """读虚拟内存"""
        paddr = self.translate(vaddr)
        return self.phys_memory[paddr:paddr+size]

    def write(self, vaddr, data: bytes):
        """写虚拟内存"""
        paddr = self.translate(vaddr, write=True)
        self.phys_memory[paddr:paddr+len(data)] = data

    def map_page(self, vpn, pfn=None, flags=PAGE_PRESENT|PAGE_RW):
        """映射虚拟页 → 物理页帧（参照 mmap / mprotect）"""
        if pfn is None:
            if not self.free_frames: raise MemoryError("OOM: no free frames")
            pfn = self.free_frames.pop(0)
        pd_idx, pt_idx = (vpn >> 8) & 0xFF, vpn & 0xFF
        pt = self.page_dir.get_or_create(pd_idx)
        pt[pt_idx].frame_number = pfn
        pt[pt_idx].flags = flags
        return pfn

    def unmap_page(self, vpn):
        """取消映射（参照 munmap）"""
        pd_idx, pt_idx = (vpn >> 8) & 0xFF, vpn & 0xFF
        pt = self.page_dir.get(pd_idx)
        if pt:
            pfn = pt[pt_idx].frame_number
            pt[pt_idx].flags = 0
            self.free_frames.append(pfn)
            self.tlb.invalidate(vpn)

    def handle_page_fault(self, vaddr):
        """缺页处理（参照 Linux do_page_fault）
        ① 分配物理页帧 ② 映射 ③ 返回（让指令重试）"""
        self.stats["page_faults"] += 1
        pd_idx, pt_idx, _ = split_virtual_addr(vaddr)
        vpn = (pd_idx << 8) | pt_idx
        pfn = self.map_page(vpn)
        return pfn

    def stats_report(self):
        return {**self.stats, **{"tlb_" + k: v for k, v in self.tlb.stats().items()}}

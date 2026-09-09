#!/usr/bin/env python3
"""
tinymmu/demo.py — MMU 端到端演示

5 个 demo：
  1. 地址翻译（虚拟→物理）
  2. TLB 缓存效果（hit rate）
  3. 缺页中断 + 懒分配
  4. 共享内存（多进程映射同一物理页）
  5. OOM（物理帧耗尽）
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tinymmu.mmu import MMU, PageFault
from tinymmu.page_table import split_virtual_addr, make_virtual_addr, PAGE_PRESENT, PAGE_RW

def demo_translate():
    print("┌─────────────────────────────────┐")
    print("│  Demo 1: 地址翻译               │")
    print("└─────────────────────────────────┘\n")
    mmu = MMU(phys_frames=256)
    mmu.map_page(vpn=0x0100, pfn=0x0042, flags=PAGE_PRESENT|PAGE_RW)
    vaddr = make_virtual_addr(0x01, 0x00, 0x42)  # PD=1, PT=0, offset=0x42
    paddr = mmu.translate(vaddr)
    pd, pt, off = split_virtual_addr(vaddr)
    print(f"  虚拟地址: 0x{vaddr:06X} (PD={pd}, PT={pt}, off=0x{off:02X})")
    print(f"  物理地址: 0x{paddr:06X} (frame=0x{paddr//256:04X}, off=0x{off:02X})")
    # 写入数据
    mmu.write(vaddr, b"HI!")
    data = mmu.read(vaddr, 3)
    print(f"  write(vaddr, 'HI!') → read = {data.decode()}")
    print(f"  ✅ 地址翻译正确\n  stats: {mmu.stats}")

def demo_tlb():
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 2: TLB 缓存效果           │")
    print("└─────────────────────────────────┘\n")
    mmu = MMU(phys_frames=256)
    # 映射 10 个虚拟页
    for i in range(10):
        mmu.map_page(vpn=0x0100 + i)
    # 第一次访问（全 TLB miss）
    for i in range(10):
        vaddr = make_virtual_addr(0x01, i, 0)
        mmu.translate(vaddr)
    print(f"  第一次访问 10 页（TLB 冷启动）:")
    print(f"  {mmu.tlb.stats()}")
    # 第二次访问（全 TLB hit）
    for i in range(10):
        vaddr = make_virtual_addr(0x01, i, 0)
        mmu.translate(vaddr)
    print(f"\n  第二次访问（TLB 热启动）:")
    print(f"  {mmu.tlb.stats()}")
    print(f"\n  TLB 命中率: {mmu.tlb.hit_rate():.1%}")

def demo_page_fault():
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 3: 缺页中断 + 懒分配     │")
    print("└─────────────────────────────────┘\n")
    mmu = MMU(phys_frames=256)
    vaddr = make_virtual_addr(0x02, 0x05, 0x10)
    print(f"  访问未映射地址 0x{vaddr:06X}:")
    try:
        mmu.translate(vaddr)
    except PageFault as e:
        print(f"  ❌ PageFault: {e}")
        print(f"  → 处理缺页: 分配物理帧 + 映射...")
        mmu.handle_page_fault(vaddr)
        paddr = mmu.translate(vaddr)
        print(f"  ✅ 重试成功: 物理地址 = 0x{paddr:06X}")
        mmu.write(vaddr, b"DATA")
        print(f"  write + read: {mmu.read(vaddr, 4).decode()}")
        print(f"  stats: {mmu.stats}")

def demo_shared_memory():
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 4: 共享内存               │")
    print("└─────────────────────────────────┘\n")
    mmu = MMU(phys_frames=256)
    shared_pfn = 0x0099
    # 两个不同的虚拟页映射到同一物理帧
    mmu.map_page(vpn=0x0100, pfn=shared_pfn)
    mmu.map_page(vpn=0x0200, pfn=shared_pfn)
    vaddr1 = make_virtual_addr(0x01, 0x00, 0)
    vaddr2 = make_virtual_addr(0x02, 0x00, 0)
    mmu.write(vaddr1, b"SHARED!")
    data = mmu.read(vaddr2, 7)
    print(f"  页A(0x{vaddr1:06X}) → 帧0x{shared_pfn:04X}")
    print(f"  页B(0x{vaddr2:06X}) → 帧0x{shared_pfn:04X} (同一物理帧)")
    print(f"  write(A, 'SHARED!') → read(B) = '{data.decode()}'")
    print(f"  ✅ 共享内存: 两个虚拟页看到同一物理页")

def demo_oom():
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 5: OOM（物理帧耗尽）      │")
    print("└─────────────────────────────────┘\n")
    mmu = MMU(phys_frames=10)  # 只有 10 个物理帧
    for i in range(10):
        mmu.map_page(vpn=i)
    print(f"  分配了 10 个物理帧（全部用完）")
    try:
        mmu.map_page(vpn=999)
    except MemoryError as e:
        print(f"  ❌ OOM: {e}")
        print(f"  → 操作系统会: ① 回收 LRU 页(swap) ② 杀进程(OOM Killer)")
    print(f"\n  Linux OOM Killer: 选 RSS 最大的进程杀掉")

def main():
    print("=" * 60)
    print("  tinymmu — 虚拟内存管理单元（参照 csapp Ch9）")
    print("=" * 60)
    demo_translate()
    demo_tlb()
    demo_page_fault()
    demo_shared_memory()
    demo_oom()
    print(f"\n{'='*60}")
    print(f"  tinymmu = page_table.py + tlb.py + mmu.py")
    print(f"  覆盖: 多级页表 → TLB → 地址翻译 → 缺页中断 → 共享内存 → OOM")
    print(f"{'='*60}")

if __name__ == "__main__": main()

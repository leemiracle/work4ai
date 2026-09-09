"""tinymmu — 参照 csapp Ch9 的虚拟内存管理单元"""
from .page_table import PageTable, PageDirectory, PTE, split_virtual_addr, make_virtual_addr
from .page_table import PAGE_PRESENT, PAGE_RW, PAGE_DIRTY, PAGE_ACCESSED, PAGE_SIZE
from .tlb import TLB
from .mmu import MMU, PageFault

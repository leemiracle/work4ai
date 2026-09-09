#!/usr/bin/env python3

class PageTableEntry:
    def __init__(self, page_frame_number=None):
        self.present = page_frame_number is not None
        self.read_write = True
        self.user_sup = True
        self.accessed = False
        self.dirty = False
        self.page_frame_number = page_frame_number if page_frame_number else 0
    
    def __repr__(self):
        status = "P" if self.present else "-"
        status += "W" if self.read_write else "R"
        status += "U" if self.user_sup else "S"
        status += "A" if self.accessed else "-"
        status += "D" if self.dirty else "-"
        return f"PTE[{self.page_frame_number:4d}] {status}"


class VirtualMemorySystem:
    def __init__(self, num_pages=1024, num_frames=512, page_size=4096):
        self.num_pages = num_pages
        self.num_frames = num_frames
        self.page_size = page_size
        self.page_table = [PageTableEntry() for _ in range(num_pages)]
        self.physical_memory = [None] * num_frames
        self.free_frames = set(range(num_frames))
        self.page_faults = 0
        self.tlb_hits = 0
        self.tlb_misses = 0
    
    def translate_address(self, virtual_address):
        """翻译虚拟地址为物理地址"""
        # 提取页号和偏移
        page_number = virtual_address // self.page_size
        offset = virtual_address % self.page_size
        
        if page_number >= self.num_pages:
            raise Exception(f"Virtual address out of range: {virtual_address}")
        
        # 检查页表项
        pte = self.page_table[page_number]
        
        if not pte.present:
            self.handle_page_fault(page_number)
            pte = self.page_table[page_number]
        
        pte.accessed = True
        
        # 计算物理地址
        physical_frame = pte.page_frame_number
        physical_address = physical_frame * self.page_size + offset
        
        return physical_address, pte
    
    def handle_page_fault(self, page_number):
        """处理页错误"""
        self.page_faults += 1
        
        if len(self.free_frames) > 0:
            # 有空闲帧
            frame = self.free_frames.pop()
        else:
            # 需要页面置换
            frame = self.evict_page()
        
        # 分配物理帧
        self.page_table[page_number].present = True
        self.page_table[page_number].page_frame_number = frame
        self.physical_memory[frame] = f"Data for page {page_number}"
        
        print(f"Page fault: Page {page_number} -> Frame {frame}")
    
    def evict_page(self):
        """简单的 FIFO 页面置换"""
        # 找到第一个可置换的页
        for i, pte in enumerate(self.page_table):
            if pte.present and not pte.dirty:
                frame = pte.page_frame_number
                pte.present = False
                print(f"Evicted: Page {i} from Frame {frame}")
                return frame
        
        # 如果都 dirty，找第一个
        for i, pte in enumerate(self.page_table):
            if pte.present:
                frame = pte.page_frame_number
                pte.present = False
                pte.dirty = False
                print(f"Evicted (dirty): Page {i} from Frame {frame}")
                return frame
        
        raise Exception("No page to evict")
    
    def read(self, virtual_address):
        """从虚拟地址读取"""
        physical_address, pte = self.translate_address(virtual_address)
        frame = physical_address // self.page_size
        return self.physical_memory[frame]
    
    def write(self, virtual_address, data):
        """向虚拟地址写入"""
        physical_address, pte = self.translate_address(virtual_address)
        frame = physical_address // self.page_size
        self.physical_memory[frame] = data
        pte.dirty = True
    
    def stats(self):
        return {
            "page_faults": self.page_faults,
            "tlb_hits": self.tlb_hits,
            "tlb_misses": self.tlb_misses,
            "tlb_hit_rate": self.tlb_hits / (self.tlb_hits + self.tlb_misses) if (self.tlb_hits + self.tlb_misses) > 0 else 0
        }


class TLB:
    def __init__(self, size=64):
        self.size = size
        self.cache = {}  # virtual_page -> physical_frame
        self.hits = 0
        self.misses = 0
    
    def lookup(self, virtual_page):
        if virtual_page in self.cache:
            self.hits += 1
            return self.cache[virtual_page]
        self.misses += 1
        return None
    
    def update(self, virtual_page, physical_frame):
        if len(self.cache) >= self.size:
            # 简单 FIFO
            self.cache.pop(next(iter(self.cache)))
        self.cache[virtual_page] = physical_frame
    
    def stats(self):
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        }


class LRUPolicy:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.access_order = []  # 用于追踪访问顺序
    
    def access(self, page):
        if page in self.cache:
            self.access_order.remove(page)
            self.access_order.append(page)
        else:
            if len(self.cache) >= self.capacity:
                self.evict()
            self.cache[page] = True
            self.access_order.append(page)
    
    def evict(self):
        if self.access_order:
            evicted = self.access_order.pop(0)
            del self.cache[evicted]
            return evicted
        return None


class ClockPolicy:
    def __init__(self, capacity):
        self.capacity = capacity
        self.frames = [{'page': None, 'ref': False} for _ in range(capacity)]
        self.hand = 0
    
    def access(self, page):
        for i, frame in enumerate(self.frames):
            if frame['page'] == page:
                frame['ref'] = True
                return True
        return False
    
    def insert(self, page):
        # 首先检查是否已存在
        if self.access(page):
            return
        
        # 寻找空闲帧或使用时钟算法
        while True:
            frame = self.frames[self.hand]
            
            if frame['page'] is None:
                frame['page'] = page
                frame['ref'] = True
                self.hand = (self.hand + 1) % self.capacity
                return
            
            if not frame['ref']:
                evicted = frame['page']
                frame['page'] = page
                frame['ref'] = True
                self.hand = (self.hand + 1) % self.capacity
                return evicted
            
            frame['ref'] = False
            self.hand = (self.hand + 1) % self.capacity


def test_virtual_memory():
    print("=== 虚拟内存系统演示 ===\n")
    
    # 创建虚拟内存系统
    vms = VirtualMemorySystem(num_pages=16, num_frames=8, page_size=4096)
    
    # 测试地址翻译
    print("1. 地址翻译测试")
    virtual_addr = 5000
    physical_addr, pte = vms.translate_address(virtual_addr)
    print(f"虚拟地址: {virtual_addr} -> 物理地址: {physical_addr}")
    print(f"页表项: {pte}\n")
    
    # 测试多次访问（触发页错误）
    print("2. 多次访问测试")
    for addr in [0, 4096, 8192, 12288, 16384]:
        try:
            pa, pte = vms.translate_address(addr)
            print(f"虚拟 {addr:6d} -> 物理 {pa:6d}")
        except Exception as e:
            print(f"错误: {e}")
    
    print(f"\n页错误次数: {vms.page_faults}")
    
    # 测试写入
    print("\n3. 写入测试")
    vms.write(0, "Hello World")
    data = vms.read(0)
    print(f"写入和读取: {data}")
    
    # 显示统计信息
    print("\n4. 系统统计")
    stats = vms.stats()
    print(f"页错误: {stats['page_faults']}")
    print(f"TLB 命中率: {stats['tlb_hit_rate']:.2%}")


def test_page_replacement():
    print("\n\n=== 页面置换算法对比 ===\n")
    
    # 模拟访问模式
    access_pattern = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    
    print(f"访问模式: {access_pattern}\n")
    
    # LRU 策略
    print("LRU 策略:")
    lru = LRUPolicy(capacity=3)
    lru_faults = 0
    for page in access_pattern:
        if not lru.access(page):
            lru.insert(page)
            lru_faults += 1
    print(f"页错误: {lru_faults}\n")
    
    # Clock 策略
    print("Clock 策略:")
    clock = ClockPolicy(capacity=3)
    clock_faults = 0
    for page in access_pattern:
        if not clock.access(page):
            evicted = clock.insert(page)
            if evicted is not None:
                print(f"  置换: 页 {evicted} -> 页 {page}")
            clock_faults += 1
    print(f"页错误: {clock_faults}")


def test_tlb():
    print("\n\n=== TLB 性能测试 ===\n")
    
    tlb = TLB(size=4)
    
    # 模拟访问
    access_sequence = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3]
    
    for page in access_sequence:
        frame = tlb.lookup(page)
        if frame is None:
            print(f"TLB 未命中: 页 {page}")
            # 模拟页表查找
            frame = page * 10  # 假设的物理帧
            tlb.update(page, frame)
        else:
            print(f"TLB 命中: 页 {page} -> 帧 {frame}")
    
    stats = tlb.stats()
    print(f"\nTLB 统计:")
    print(f"  命中: {stats['hits']}")
    print(f"  未命中: {stats['misses']}")
    print(f"  命中率: {stats['hit_rate']:.2%}")


if __name__ == "__main__":
    test_virtual_memory()
    test_page_replacement()
    test_tlb()
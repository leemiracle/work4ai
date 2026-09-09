# 虚拟内存

## 基本信息
- **分类**: 操作系统 -> 内存管理
- **关键机制**: 分页、页面置换、TLB
- **单位**: 页（通常 4KB）

## 核心概念
虚拟内存为每个进程提供独立的地址空间，实现内存抽象和保护。

## 内存层次结构
```
CPU 寄存器
    ↓ (1-10 cycles)
CPU 缓存 (L1/L2/L3)
    ↓ (10-100 cycles)
物理内存 (RAM)
    ↓ (1,000,000+ cycles)
磁盘/SSD
```

## 关键组件

### 1. 页表
虚拟地址到物理地址的映射
```c
struct page_table_entry {
    unsigned int present    : 1;  // 页是否在内存中
    unsigned int read_write : 1;  // 读写权限
    unsigned int user_sup   : 1;  // 用户/内核权限
    unsigned int accessed   : 1;  // 是否被访问
    unsigned int dirty      : 1;  // 是否被修改
    unsigned int page_frame_number : 20;  // 物理页帧号
};
```

### 2. 地址翻译
```python
def translate_address(virtual_address, page_table):
    page_number = virtual_address >> 12  # 高20位
    offset = virtual_address & 0xFFF    # 低12位
    
    if not page_table[page_number].present:
        raise PageFaultException()
    
    physical_frame = page_table[page_number].page_frame_number
    physical_address = (physical_frame << 12) | offset
    
    return physical_address
```

### 3. TLB (Translation Lookaside Buffer)
加速地址翻译的缓存
```python
class TLB:
    def __init__(self, size=64):
        self.cache = {}
        self.size = size
    
    def lookup(self, virtual_page):
        return self.cache.get(virtual_page)
    
    def update(self, virtual_page, physical_frame):
        if len(self.cache) >= self.size:
            self.cache.pop(next(iter(self.cache)))
        self.cache[virtual_page] = physical_frame
```

## 页面置换算法

### LRU (Least Recently Used)
```python
class LRUPolicy:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def access(self, page):
        if page in self.cache:
            self.cache.move_to_end(page)
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
            self.cache[page] = None
    
    def evict(self):
        return self.cache.popitem(last=False)[0]
```

### Clock 算法
```python
class ClockPolicy:
    def __init__(self, capacity):
        self.frames = [{'page': None, 'ref': False} for _ in range(capacity)]
        self.hand = 0
    
    def access(self, page):
        for i, frame in enumerate(self.frames):
            if frame['page'] == page:
                frame['ref'] = True
                return True
        return False
    
    def evict(self):
        while True:
            frame = self.frames[self.hand]
            if not frame['ref']:
                evicted = frame['page']
                return evicted
            frame['ref'] = False
            self.hand = (self.hand + 1) % len(self.frames)
```

## 页错误处理流程
1. CPU 触发页错误异常
2. 操作系统检查虚拟地址合法性
3. 分配物理页帧
4. 从磁盘加载数据（如需要）
5. 更新页表
6. 重启指令

## 优化技术

### 大页支持
```python
# 标准页: 4KB, 大页: 2MB, 巨页: 1GB
HUGE_PAGE_SIZE = 2 * 1024 * 1024  # 2MB
```

### 预取
```python
def prefetch_pages(access_pattern):
    predicted_pages = predict_next_access(access_pattern)
    for page in predicted_pages:
        if not page_in_memory(page):
            load_page_async(page)
```

### Copy-on-Write
```python
def fork_process(parent_pt):
    child_pt = copy_page_table(parent_pt)
    for entry in child_pt:
        entry.read_only = True
    return child_pt

def write_protection_fault(page):
    copy_page(page)
    page_entry.writable = True
```

## 应用场景
- 进程隔离
- 内存保护
- 内存超额分配
- 文件映射（mmap）

## 相关概念
- [[TLB]]
- [[缓存一致性]]
- [[内存映射文件]]

## 参考资源
- CSAPP Chapter 9
- 《深入理解计算机系统》第9章
- 《现代操作系统》第3章

## 实践项目
- 模拟虚拟内存系统
- 实现简单的分页机制
- 对比不同页面置换算法
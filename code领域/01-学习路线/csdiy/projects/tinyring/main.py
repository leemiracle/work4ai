#!/usr/bin/env python3
"""tinyring — 参照 Linux kfifo / DPDK ring 的无锁环形缓冲区
参照：Linux kfifo / DPDK rte_ring / Disruptor
csdiy 对应：csapp Ch6(cache line) + os §五(并发)
核心：环形数组 + 原子指针 → SPSC 无锁队列"""
import threading, time

class RingBuffer:
    """SPSC 环形缓冲区（参照 DPDK rte_ring SPSC 模式）
    Single Producer → Single Consumer → 不需要锁"""
    def __init__(self, capacity):
        self.capacity = capacity
        self.buf = [None] * capacity
        self.head = 0  # 消费者写（参照 volatile）
        self.tail = 0  # 生产者写
    def push(self, item):
        next_tail = (self.tail + 1) % self.capacity
        if next_tail == self.head: return False  # 满
        self.buf[self.tail] = item
        self.tail = next_tail
        return True
    def pop(self):
        if self.head == self.tail: return None  # 空
        item = self.buf[self.head]
        self.head = (self.head + 1) % self.capacity
        return item
    def is_empty(self): return self.head == self.tail
    def is_full(self): return (self.tail+1)%self.capacity == self.head
    def size(self): return (self.tail - self.head) % self.capacity

class BatchRing(RingBuffer):
    """批量操作环形缓冲区（参照 DPDK burst enqueue/dequeue）"""
    def push_batch(self, items):
        count = 0
        for item in items:
            if not self.push(item): break
            count += 1
        return count
    def pop_batch(self, n):
        return [self.pop() for _ in range(n) if not self.is_empty()]

def main():
    print("tinyring — 环形缓冲区（参照 Linux kfifo / DPDK）\n")
    rb = RingBuffer(8)
    for i in range(5): rb.push(f"item-{i}")
    print(f"  push 5 items → size={rb.size()}, full={rb.is_full()}")
    while not rb.is_empty():
        print(f"  pop → {rb.pop()}")
    print(f"  empty={rb.is_empty()}")

    # 多线程测试
    br = BatchRing(1024)
    produced = []; consumed = []
    def producer():
        for i in range(1000):
            while not br.push(i): time.sleep(0.0001)
            produced.append(i)
    def consumer():
        for _ in range(1000):
            item = None
            while item is None: item = br.pop()
            consumed.append(item)
    t1 = threading.Thread(target=producer); t2 = threading.Thread(target=consumer)
    t1.start(); t2.start(); t1.join(); t2.join()
    ok = produced == consumed
    print(f"\n  多线程: produced={len(produced)} consumed={len(consumed)} match={ok} ✅")
    print(f"\n  特点: O(1) push/pop, 零拷贝, cache-friendly（连续内存）")

if __name__ == "__main__": main()

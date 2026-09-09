#!/usr/bin/env python3
"""tinyeventloop — 参照 libuv/Node.js 的事件循环
参照：libuv / Node.js event loop / asyncio
csidi 对应：redis-eventloop精读 + eventloop-evolution精读
核心：IO事件 + 定时器 + 微任务 → 单线程异步"""
import time,heapq,select,socket
from collections import deque

class TinyEventLoop:
    """事件循环（参照 libuv / Redis ae.c）
    for { poll_io → run_timers → run_microtasks → run_idle }"""
    def __init__(self):
        self.timers=[]; self.microtasks=deque(); self.idle_callbacks=[]
        self.running=False; self.io_callbacks={}
    def call_later(self,delay,callback,*args):
        """定时器（参照 Redis aeCreateTimeEvent）"""
        heapq.heappush(self.timers,(time.monotonic()+delay,callback,args))
    def call_soon(self,callback,*args):
        """微任务（参照 Node.js process.nextTick）"""
        self.microtasks.append((callback,args))
    def on_idle(self,callback): self.idle_callbacks.append(callback)
    def register_io(self,fd,callback): self.io_callbacks[fd]=callback
    def run_once(self,timeout=0.1):
        now=time.monotonic()
        # 1. 定时器
        while self.timers and self.timers[0][0]<=now:
            _,cb,args=heapq.heappop(self.timers); cb(*args)
        # 2. 微任务
        while self.microtasks:
            cb,args=self.microtasks.popleft(); cb(*args)
        # 3. IO 事件（简化版，用 select）
        if self.io_callbacks:
            readable,_,_=select.select(list(self.io_callbacks.keys()),[],[],0.01)
            for fd in readable:
                self.io_callbacks[fd](fd)
        # 4. 空闲回调
        for cb in self.idle_callbacks: cb()
    def run(self):
        self.running=True
        while self.running:
            if not self.timers and not self.microtasks and not self.io_callbacks: break
            self.run_once()
    def stop(self): self.running=False

def main():
    print("tinyeventloop — 事件循环（参照 libuv/Redis ae.c）\n")
    loop=TinyEventLoop()
    log=[]
    # 定时器
    loop.call_later(0.3,lambda: log.append("timer 300ms"))
    loop.call_later(0.1,lambda: log.append("timer 100ms"))
    loop.call_later(0.2,lambda: log.append("timer 200ms"))
    # 微任务（在定时器之前执行）
    loop.call_soon(lambda: log.append("microtask 1"))
    loop.call_soon(lambda: log.append("microtask 2"))
    # 嵌套微任务
    def nest():
        log.append("nested microtask"); loop.call_soon(lambda: log.append("after nest"))
    loop.call_soon(nest)
    loop.run()
    print("  执行顺序:")
    for entry in log: print(f"    {entry}")
    print(f"\n  规律: microtask 先于 timer；timer 按 deadline 排序")

if __name__=="__main__": main()

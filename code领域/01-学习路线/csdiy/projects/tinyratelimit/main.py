#!/usr/bin/env python3
"""tinyratelimit — 参照 stripe/redis-cell 的限流器
参照：Token Bucket / Sliding Window / Leaky Bucket
csdiy 对应：tinyproxy(rate_limit) + redis-expiry精读
核心：三种限流算法 + 对比"""
import time, threading
from collections import deque

class TokenBucket:
    """令牌桶（参照 nginx limit_req / golang.org/x/time/rate）"""
    def __init__(self,rate,burst):
        self.rate=rate; self.burst=burst
        self.tokens=float(burst); self.last=time.monotonic(); self.lock=threading.Lock()
    def allow(self,n=1):
        with self.lock:
            now=time.monotonic(); elapsed=now-self.last
            self.tokens=min(self.burst,self.tokens+elapsed*self.rate); self.last=now
            if self.tokens>=n: self.tokens-=n; return True
            return False

class SlidingWindow:
    """滑动窗口（参照 Redis ZSET 限流）"""
    def __init__(self,window,limit):
        self.window=window; self.limit=limit; self.events=deque(); self.lock=threading.Lock()
    def allow(self):
        with self.lock:
            now=time.time()
            while self.events and self.events[0]<now-self.window: self.events.popleft()
            if len(self.events)<self.limit: self.events.append(now); return True
            return False

class LeakyBucket:
    """漏桶（参照 nginx limit_req_delay）"""
    def __init__(self,rate,capacity):
        self.rate=rate; self.capacity=capacity; self.water=0; self.last=time.monotonic(); self.lock=threading.Lock()
    def allow(self,amount=1):
        with self.lock:
            now=time.monotonic(); elapsed=now-self.last
            self.water=max(0,self.water-elapsed*self.rate); self.last=now
            if self.water+amount<=self.capacity:
                self.water+=amount; return True
            return False

def test_limiter(name,limiter,requests=100):
    allowed=0; denied=0
    for i in range(requests):
        if limiter.allow(): allowed+=1
        else: denied+=1
        time.sleep(0.01)  # 每 10ms 一个请求
    print(f"  {name:20s} allowed={allowed:4d} denied={denied:4d}")
    return allowed

def main():
    print("tinyratelimit — 限流器（参照 nginx/redis-cell）\n")
    print("  100 请求, 10ms 间隔, 限流 50/s:\n")
    test_limiter("TokenBucket(50/s,5)",TokenBucket(rate=50,burst=5))
    test_limiter("SlidingWindow(1s,50)",SlidingWindow(window=1.0,limit=50))
    test_limiter("LeakyBucket(50/s,5)",LeakyBucket(rate=50,capacity=5))
    print(f"\n  TokenBucket: 允许突发(burst)，适合 API")
    print(f"  SlidingWindow: 精确窗口限流，适合严格配额")
    print(f"  LeakyBucket: 平滑输出，适合流量整形")

if __name__=="__main__": main()

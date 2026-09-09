#!/usr/bin/env python3
"""tinypool — 参照 ThreadPoolExecutor 的线程池+连接池
参照：Python ThreadPool / Java ThreadPoolExecutor / HikariCP
csdiy 对应：os §五(并发) + patterns §7(对象池) + tinyproxy(连接池)
核心：固定线程池 + 任务队列 + 连接池"""
import threading,queue,time,socket
from collections import deque

class ThreadPool:
    """线程池（参照 Python concurrent.futures.ThreadPoolExecutor）"""
    def __init__(self,num_workers=4):
        self.workers=num_workers; self.queue=queue.Queue()
        self.threads=[]; self.running=True; self.completed=0
        for _ in range(num_workers):
            t=threading.Thread(target=self._worker,daemon=True); t.start(); self.threads.append(t)
    def _worker(self):
        while self.running:
            try:
                func,args=self.queue.get(timeout=1)
                func(*args); self.completed+=1; self.queue.task_done()
            except queue.Empty: continue
            except Exception: pass
    def submit(self,func,*args): self.queue.put((func,args))
    def wait(self): self.queue.join()
    def shutdown(self): self.running=False

class ConnectionPool:
    """连接池（参照 HikariCP / SQLAlchemy pool）
    复用连接 → 减少 TCP 握手开销"""
    def __init__(self,factory,max_size=10):
        self.factory=factory; self.max_size=max_size
        self.pool=deque(); self.in_use=0; self.lock=threading.Lock()
    def acquire(self):
        with self.lock:
            if self.pool:
                self.in_use+=1; return self.pool.popleft()
            if self.in_use<self.max_size:
                self.in_use+=1; return self.factory()
            raise RuntimeError("Pool exhausted")
    def release(self,conn):
        with self.lock:
            self.in_use-=1; self.pool.append(conn)
    def stats(self): return {"pool_size":len(self.pool),"in_use":self.in_use,"max":self.max_size}

def main():
    print("tinypool — 线程池+连接池（参照 ThreadPoolExecutor/HikariCP）\n")
    pool=ThreadPool(num_workers=4)
    results=[]
    def task(n):
        time.sleep(0.01); results.append(n**2)
    for i in range(20): pool.submit(task,i)
    pool.wait()
    print(f"  线程池: 20 tasks × 4 workers → completed={pool.completed}")
    print(f"  results[:5]={results[:5]} sorted={results==sorted(results)}")
    pool.shutdown()
    # 连接池
    mock_conns=[]
    conn_pool=ConnectionPool(lambda:f"conn-{len(mock_conns)}",max_size=3)
    for _ in range(3): mock_conns.append(conn_pool.acquire())
    print(f"\n  连接池: {conn_pool.stats()}")
    conn_pool.release(mock_conns[0]); print(f"  release 1 → {conn_pool.stats()}")
    c=conn_pool.acquire(); print(f"  acquire 1 → {conn_pool.stats()} (复用旧连接)")

if __name__=="__main__": main()

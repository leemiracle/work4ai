#!/usr/bin/env python3
"""tinyclock — 参照 Lamport/Vector Clock 的逻辑时钟
参照：Lamport Clock / Vector Clock / Hybrid Logical Clock
csdiy 对应：tinyraft + tinygossip + 分布式
核心：在没有全局时钟的分布式系统里排序事件"""
class LamportClock:
    """Lamport 逻辑时钟（参照 Lamport 1978 "Time, Clocks, and the Ordering of Events"）
    规则：send 时 C = C+1；recv 时 C = max(C, msg_C) + 1"""
    def __init__(self, pid): self.pid=pid; self.c=0
    def tick(self): self.c+=1; return self.c
    def send(self): self.c+=1; return {"pid":self.pid,"c":self.c}
    def recv(self, msg): self.c=max(self.c, msg["c"])+1; return self.c

class VectorClock:
    """向量时钟（参照 Mattern 1989）
    每个节点维护所有节点的计数器 → 精确因果关系"""
    def __init__(self, pid, n):
        self.pid=pid; self.n=n; self.vc=[0]*n
    def tick(self): self.vc[self.pid]+=1; return self.vc.copy()
    def send(self): self.vc[self.pid]+=1; return self.vc.copy()
    def recv(self, other): self.vc=[max(a,b) for a,b in zip(self.vc, other)]
    def happens_before(self, other):
        return all(a<=b for a,b in zip(self.vc, other)) and self.vc!=other

def main():
    print("tinyclock — 逻辑时钟（参照 Lamport + Vector Clock）\n")
    # Lamport Clock
    print("── Lamport Clock ──")
    a = LamportClock("A"); b = LamportClock("B")
    c1 = a.tick(); print(f"  A tick → {c1}")
    msg = a.send(); print(f"  A send → msg.c={msg['c']}")
    c2 = b.recv(msg); print(f"  B recv → {c2}")
    c3 = b.tick(); print(f"  B tick → {c3}")

    # Vector Clock
    print("\n── Vector Clock ──")
    va = VectorClock(0, 3); vb = VectorClock(1, 3)
    va.tick(); print(f"  A: {va.vc}")
    msg = va.send(); print(f"  A send: {msg}")
    vb.recv(msg); vb.tick(); print(f"  B: {vb.vc}")
    msg2 = vb.send(); print(f"  B send: {msg2}")
    va.recv(msg2); print(f"  A: {va.vc}")
    print(f"\n  A happens-before B? {va.happens_before(vb.vc)}")
    print(f"  B happens-before A? {vb.happens_before(va.vc)}")
    print(f"  → 它们是并发的（没有因果关系）")

    print(f"\n  Lamport: 单值，不精确（丢失因果关系）")
    print(f"  Vector: N 维，精确但空间 O(N)")

if __name__ == "__main__": main()

#!/usr/bin/env python3
"""tinygc — 参照 JVM/CPython 的标记-清除垃圾回收器
参照：JVM G1 / CPython gc / Go GC
csdiy 对应：rust-ownership精读 + csapp Ch9(堆)
核心：对象图遍历 + 标记活对象 + 清除死对象"""
from dataclasses import dataclass,field
from typing import Set
import weakref

@dataclass
class GCObject:
    id:int; name:str; refs:Set[int]=field(default_factory=set)
    marked:bool=False; generation:int=0

class TinyGC:
    """标记-清除 GC（参照 McCarthy 1960 + JVM）
    root_set: 全局引用（栈/全局变量）
    heap: 所有分配的对象
    """
    def __init__(self):
        self.heap:dict[int,GCObject]={}; self.roots:Set[int]=set(); self.next_id=0
        self.collections=0; self.total_freed=0; self.total_alive=0

    def alloc(self,name,refs=None):
        oid=self.next_id; self.next_id+=1
        obj=GCObject(oid,name,refs or set())
        self.heap[oid]=obj; return oid

    def add_root(self,oid): self.roots.add(oid)
    def del_root(self,oid): self.roots.discard(oid)

    def collect(self):
        """标记-清除（参照 Mark-Sweep 算法）"""
        # Phase 1: Mark（从 roots DFS 遍历对象图）
        for obj in self.heap.values(): obj.marked=False
        stack=list(self.roots); marked=set()
        while stack:
            oid=stack.pop()
            if oid in marked: continue
            obj=self.heap.get(oid)
            if not obj or obj.marked: continue
            obj.marked=True; marked.add(oid)
            stack.extend(obj.refs)

        # Phase 2: Sweep（清除未标记的对象）
        freed=[]
        for oid in list(self.heap.keys()):
            if not self.heap[oid].marked:
                freed.append(self.heap[oid].name)
                del self.heap[oid]

        self.collections+=1; self.total_freed+=len(freed); self.total_alive=len(self.heap)
        return freed

    def stats(self):
        return {"alive":len(self.heap),"roots":len(self.roots),
                "collections":self.collections,"total_freed":self.total_freed}

    def visualize(self):
        for oid,obj in sorted(self.heap.items()):
            mark="🟢" if obj.marked else "🔴"
            refs=f" → {obj.refs}" if obj.refs else ""
            root=" (ROOT)" if oid in self.roots else ""
            print(f"    {mark} #{oid} {obj.name}{root}{refs}")

def main():
    print("tinygc — 垃圾回收器（参照 JVM Mark-Sweep）\n")
    gc=TinyGC()

    # 分配对象图
    root=gc.alloc("App"); gc.add_root(root)
    db=gc.alloc("Database",{root}); gc.add_root(db)
    cache=gc.alloc("Cache",{root,db})
    conn1=gc.alloc("Conn1",{db})
    conn2=gc.alloc("Conn2",{db})
    temp=gc.alloc("TempData")  # 没有引用 → 可回收
    orphan=gc.alloc("Orphan",{temp})  # 引用了 temp 但自己也没被引用

    print("  GC 前堆状态:")
    gc.visualize()

    freed=gc.collect()
    print(f"\n  GC 收集: freed={freed}")
    gc.visualize()
    print(f"\n  stats: {gc.stats()}")

    # 模拟循环引用（GC 能处理，引用计数不能）
    print("\n  循环引用测试:")
    a=gc.alloc("NodeA"); b=gc.alloc("NodeB")
    gc.heap[a].refs={b}; gc.heap[b].refs={a}  # A→B→A 循环
    # 没有根指向 → 应该被回收
    freed2=gc.collect()
    print(f"  freed={freed2} (循环引用也能被 GC 回收 ✅)")

if __name__=="__main__": main()

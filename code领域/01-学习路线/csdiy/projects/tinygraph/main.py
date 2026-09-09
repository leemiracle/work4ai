#!/usr/bin/env python3
"""tinygraph — 参照 NetworkX 的图算法库
参照：NetworkX / igraph / Dijkstra 原始论文
csdiy 对应：算法基础 + 分布式(拓扑) + tinysearch(页面排名)
核心：BFS/DFS/Dijkstra/Topo-sort/最小生成树"""
from collections import defaultdict, deque
import heapq

class Graph:
    """加权有向图（参照 NetworkX DiGraph）"""
    def __init__(self): self.adj=defaultdict(dict); self.nodes=set()
    def add_edge(self,u,v,w=1): self.adj[u][v]=w; self.nodes.update([u,v])
    def add_node(self,n): self.nodes.add(n)
    def neighbors(self,n): return self.adj.get(n,{})

    def bfs(self,start):
        visited={start}; q=deque([start]); order=[start]
        while q:
            n=q.popleft()
            for nb in self.adj.get(n,{}):
                if nb not in visited: visited.add(nb); q.append(nb); order.append(nb)
        return order

    def dfs(self,start):
        visited=set(); order=[]; stack=[start]
        while stack:
            n=stack.pop()
            if n in visited: continue
            visited.add(n); order.append(n)
            for nb in sorted(self.adj.get(n,{}),reverse=True):
                if nb not in visited: stack.append(nb)
        return order

    def dijkstra(self,start):
        """最短路径（参照 Dijkstra 1959）"""
        dist={n:float('inf') for n in self.nodes}; dist[start]=0
        prev={}; pq=[(0,start)]
        while pq:
            d,u=heapq.heappop(pq)
            if d>dist[u]: continue
            for v,w in self.adj.get(u,{}).items():
                nd=d+w
                if nd<dist[v]: dist[v]=nd; prev[v]=u; heapq.heappush(pq,(nd,v))
        return dist,prev

    def topo_sort(self):
        """拓扑排序（参照 Kahn 算法）"""
        indeg={n:0 for n in self.nodes}
        for u in self.adj:
            for v in self.adj[u]: indeg[v]=indeg.get(v,0)+1
        q=deque([n for n in indeg if indeg[n]==0]); order=[]
        while q:
            n=q.popleft(); order.append(n)
            for v in self.adj.get(n,{}):
                indeg[v]-=1
                if indeg[v]==0: q.append(v)
        return order

    def mst(self):
        """最小生成树（Prim 算法）"""
        if not self.nodes: return []
        start=min(self.nodes); visited={start}; edges=[]; pq=[]
        for v,w in self.adj.get(start,{}).items(): heapq.heappush(pq,(w,start,v))
        while pq and len(visited)<len(self.nodes):
            w,u,v=heapq.heappop(pq)
            if v in visited: continue
            visited.add(v); edges.append((u,v,w))
            for nb,nw in self.adj.get(v,{}).items():
                if nb not in visited: heapq.heappush(pq,(nw,v,nb))
        return edges

def main():
    print("tinygraph — 图算法库（参照 NetworkX）\n")
    g=Graph()
    g.add_edge("A","B",4); g.add_edge("A","C",2); g.add_edge("B","C",5)
    g.add_edge("B","D",10); g.add_edge("C","D",3); g.add_edge("D","E",7); g.add_edge("C","E",8)
    print(f"  BFS(A): {g.bfs('A')}")
    print(f"  DFS(A): {g.dfs('A')}")
    dist,prev=g.dijkstra("A")
    print(f"  Dijkstra(A): {dict(dist)}")
    print(f"  Topo: {g.topo_sort()}")
    print(f"  MST: {g.mst()}")

if __name__=="__main__": main()

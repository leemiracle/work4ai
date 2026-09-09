#!/usr/bin/env python3
"""tinyroute — 参照 Linux ip route / BGP 的路由表
参照：Linux ip route2 / FRR BGP / csapp Ch11(网络编程)
csdiy 对应：network + tinydns + tinyproxy
核心：最长前缀匹配 + 路由表 + 静态路由"""
import ipaddress,bisect
from dataclasses import dataclass

@dataclass
class Route:
    network:str; prefix_len:int; gateway:str=None; interface:str="eth0"; metric:int=100
    def __str__(self): return f"{self.network}/{self.prefix_len} via {self.gateway or 'direct'} dev {self.interface} metric {self.metric}"

class RoutingTable:
    """路由表（参照 Linux fib_trie）
    核心算法：最长前缀匹配（Longest Prefix Match）"""
    def __init__(self): self.routes=[]
    def add(self,network,prefix_len,gateway=None,interface="eth0",metric=100):
        self.routes.append(Route(network,prefix_len,gateway,interface,metric))
        self.routes.sort(key=lambda r:(-r.prefix_len,r.metric))
    def lookup(self,ip):
        """最长前缀匹配（参照 Linux 路由查找）"""
        addr=ipaddress.ip_address(ip)
        for route in self.routes:
            net=ipaddress.ip_network(f"{route.network}/{route.prefix_len}",strict=False)
            if addr in net: return route
        return None
    def show(self):
        for r in self.routes: print(f"  {r}")
    def stats(self): return {"routes":len(self.routes)}

def main():
    print("tinyroute — 路由表（参照 Linux ip route）\n")
    rt=RoutingTable()
    rt.add("0.0.0.0",0,gateway="192.168.1.1",interface="eth0",metric=200)  # 默认路由
    rt.add("192.168.1.0",24,interface="eth0")  # 局域网直连
    rt.add("10.0.0.0",8,gateway="192.168.1.2",interface="eth0")  # VPN
    rt.add("172.16.0.0",12,gateway="192.168.1.3",interface="eth0")
    print("  路由表:")
    rt.show()
    print(f"\n  路由查找（最长前缀匹配）:")
    for ip in ["192.168.1.100","10.1.2.3","172.16.5.10","8.8.8.8"]:
        route=rt.lookup(ip)
        print(f"    {ip:16s} → {route}")
    print(f"\n  对比: BGP 用同样的最长前缀匹配，但跨自治系统")

if __name__=="__main__": main()

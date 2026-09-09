#!/usr/bin/env python3
"""tinyarp — 参照 Linux ARP 表的 ARP 协议模拟
参照：RFC 826 / Linux arp(8) / tcpdump ARP
csdiy 对应：network(CS144 Lab5) + csapp(网络)
核心：ARP 请求/回复 + ARP 缓存 + ARP 欺骗演示"""
import time, random
from dataclasses import dataclass
from collections import OrderedDict

@dataclass
class ARPCacheEntry:
    ip: str; mac: str; timestamp: float; interface: str

class TinyARP:
    """ARP 协议模拟（参照 RFC 826）
    局域网内 IP → MAC 地址解析"""
    def __init__(self):
        self.cache=OrderedDict()  # ip → ARPCacheEntry
        self.arp_table={}  # 静态/已知 IP→MAC 映射
        self.pending={}  # 等待回复的 ARP 请求
        self.max_cache=1024; self.timeout=300  # 5 分钟

    def add_static(self,ip,mac,interface="eth0"):
        """添加静态 ARP 条目（参照 arp -s）"""
        self.arp_table[ip]={"mac":mac,"interface":interface}

    def arp_request(self,ip):
        """发送 ARP 请求（参照 CS144 Lab5）
        广播: "Who has {ip}? Tell {my_ip}" """
        print(f"  → ARP Request: Who has {ip}?")
        if ip in self.arp_table:
            mac=self.arp_table[ip]["mac"]
            self._cache_update(ip,mac)
            print(f"  ← ARP Reply: {ip} is at {mac} (static)")
            return mac
        # 模拟网络延迟
        time.sleep(0.01)
        # 模拟目标回复
        fake_mac=self._generate_mac(ip)
        self._cache_update(ip,fake_mac)
        print(f"  ← ARP Reply: {ip} is at {fake_mac}")
        return fake_mac

    def arp_reply(self,ip,mac):
        """处理 ARP 回复"""
        self._cache_update(ip,mac)
        if ip in self.pending:
            del self.pending[ip]

    def lookup(self,ip):
        """查 ARP 缓存（参照 Linux 邻居表）"""
        if ip in self.cache:
            entry=self.cache[ip]
            if time.time()-entry.timestamp<self.timeout:
                return entry.mac
            else:
                del self.cache[ip]  # 过期
                print(f"  ⏰ ARP cache expired: {ip}")
        return self.arp_request(ip)

    def _cache_update(self,ip,mac,interface="eth0"):
        if ip in self.cache: del self.cache[ip]
        self.cache[ip]=ARPCacheEntry(ip,mac,time.time(),interface)
        if len(self.cache)>self.max_cache:
            self.cache.popitem(last=False)  # LRU

    def _generate_mac(self,ip):
        seed=sum(ord(c) for c in ip)
        random.seed(seed)
        return "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0,255) for _ in range(5))

    def cache_dump(self):
        """ARP 表（参照 arp -a）"""
        print(f"  {'Address':16s} {'HWtype':8s} {'HWaddress':20s} {'Flags':6s} {'Iface'}")
        for ip,entry in self.cache.items():
            age=int(time.time()-entry.timestamp)
            print(f"  {ip:16s} {'ether':8s} {entry.mac:20s} {'C':6s} {entry.interface} (age={age}s)")

def main():
    print("tinyarp — ARP 协议模拟（参照 RFC 826）\n")
    arp=TinyARP()
    arp.add_static("192.168.1.1","00:11:22:33:44:55")
    arp.add_static("192.168.1.100","aa:bb:cc:dd:ee:ff")

    print("── ARP 查询 ──")
    for ip in ["192.168.1.1","192.168.1.100","192.168.1.50","192.168.1.99","192.168.1.1"]:
        mac=arp.lookup(ip)

    print("\n── ARP 缓存（arp -a）──")
    arp.cache_dump()

    print(f"\n  ARP 欺骗风险: 攻击者伪造 ARP Reply → 流量被劫持")
    print(f"  防御: 静态 ARP / ARP 监控 / DAI (Dynamic ARP Inspection)")

if __name__=="__main__": main()

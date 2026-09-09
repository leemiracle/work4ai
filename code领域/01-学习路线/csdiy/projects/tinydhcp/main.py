#!/usr/bin/env python3
"""tinydhcp — 参照 dnsmasq/isc-dhcp-server 的 DHCP 服务器
参照：RFC 2131 DHCP / dnsmasq / kea
csdiy 对应：network + tinydns + OS(网络配置)
核心：DHCP DORA（Discover→Offer→Request→Ack）+ IP 池"""
import socket, struct, random, time
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class Lease:
    ip: str; mac: str; expiry: float; hostname: str = ""

class TinyDHCP:
    """DHCP 服务器（参照 RFC 2131）
    DORA 流程: Discover → Offer → Request → Acknowledge"""
    def __init__(self, pool_start="192.168.100.100", pool_end="192.168.100.200",
                 netmask="255.255.255.0", gateway="192.168.100.1", dns="8.8.8.8",
                 lease_time=3600):
        self.pool=self._gen_pool(pool_start,pool_end)
        self.leases: dict[str,Lease]={}  # mac → lease
        self.options={"subnet_mask":netmask,"router":gateway,
                      "dns":dns,"lease_time":lease_time,"server_id":"192.168.100.1"}
    def _gen_pool(self,start,end):
        s=sum(int(o)<<shift for o,shift in zip(start.split("."),[24,16,8,0]))
        e=sum(int(o)<<shift for o,shift in zip(end.split("."),[24,16,8,0]))
        return [".".join(str((i>>shift)&0xFF) for shift in [24,16,8,0]) for i in range(s,e+1)]
    def discover(self,mac,hostname=""):
        """DHCPDISCOVER → 分配 IP → DHCPOFFER"""
        # 检查已有租约
        if mac in self.leases and time.time()<self.leases[mac].expiry:
            ip=self.leases[mac].ip
        else:
            # 分配新 IP
            allocated={l.ip for l in self.leases.values() if time.time()<l.expiry}
            available=[ip for ip in self.pool if ip not in allocated]
            if not available: return None
            ip=random.choice(available)
            self.leases[mac]=Lease(ip,mac,time.time()+self.options["lease_time"],hostname)
        return ip
    def ack(self,mac):
        """DHCPREQUEST → DHCPACK"""
        if mac in self.leases:
            return self.leases[mac]
        return None
    def release(self,mac):
        """DHCPRELEASE"""
        if mac in self.leases: del self.leases[mac]
    def lease_table(self):
        active={mac:l for mac,l in self.leases.items() if time.time()<l.expiry}
        return active
    def pool_stats(self):
        active=len([l for l in self.leases.values() if time.time()<l.expiry])
        return {"total":len(self.pool),"active":active,"available":len(self.pool)-active}

def main():
    print("tinydhcp — DHCP 服务器（参照 RFC 2131 / dnsmasq）\n")
    dhcp=TinyDHCP()
    clients=[("aa:bb:cc:01","laptop"),("aa:bb:cc:02","phone"),
             ("aa:bb:cc:03","tablet"),("aa:bb:cc:04","iot-sensor")]
    print("── DORA 流程模拟 ──")
    for mac,name in clients:
        ip=dhcp.discover(mac,name)
        lease=dhcp.ack(mac)
        print(f"  {name:12s} ({mac}) → DISCOVER → OFFER {ip} → REQUEST → ACK ✅")
    print(f"\n── IP 池状态 ──")
    print(f"  {dhcp.pool_stats()}")
    print(f"\n── 租约表（参照 cat /var/lib/dhcp/dhcpd.leases）──")
    for mac,lease in dhcp.lease_table().items():
        remaining=int(lease.expiry-time.time())
        print(f"  {lease.ip:16s} {mac:18s} {lease.hostname:12s} TTL={remaining}s")

if __name__=="__main__": main()

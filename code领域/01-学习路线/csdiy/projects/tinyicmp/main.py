#!/usr/bin/env python3
"""tinyicmp — 参照 ping/traceroute 的 ICMP 实现
参照：iputils ping / traceroute / RFC 792
csdiy 对应：network 全部 + os §六(IO)
核心：构造 ICMP Echo Request + 解析回复"""
import socket, struct, time, os, sys

def checksum(data):
    """ICMP 校验和（参照 RFC 792）"""
    if len(data)%2: data+=b'\0'
    s=sum(struct.unpack(f"!{len(data)//2}H",data))
    s=(s>>16)+(s&0xffff)+((s>>16)+(s&0xffff)>>16)
    return ~s&0xffff

def ping(host,count=4,timeout=2):
    """Ping 实现（参照 iputils ping）"""
    try: dst=socket.gethostbyname(host)
    except: return f"Cannot resolve {host}"
    print(f"PING {host} ({dst}) 56(84) bytes of data.")
    sock=socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_ICMP)
    sock.settimeout(timeout)
    seq=0; rtts=[]
    for i in range(count):
        # 构造 ICMP Echo Request（参照 RFC 792）
        hdr=struct.pack("!BBHIH",8,0,0,os.getpid()&0xFFFF,seq)
        csum=checksum(hdr); hdr=struct.pack("!BBHIH",8,0,csum,os.getpid()&0xFFFF,seq)
        start=time.perf_counter()
        try:
            sock.sendto(hdr,(dst,0)); data,addr=sock.recvfrom(1024)
            rtt=(time.perf_counter()-start)*1000
            rtts.append(rtt)
            print(f"64 bytes from {addr[0]}: icmp_seq={seq} ttl=64 time={rtt:.1f} ms")
        except socket.timeout:
            print(f"Request timeout for icmp_seq={seq}")
        seq+=1; time.sleep(1)
    sock.close()
    if rtts:
        print(f"\n--- {host} ping statistics ---")
        print(f"{count} packets transmitted, {len(rtts)} received, {(1-len(rtts)/count)*100:.0f}% packet loss")
        print(f"rtt min/avg/max = {min(rtts):.1f}/{sum(rtts)/len(rtts):.1f}/{max(rtts):.1f} ms")

def main():
    print("tinyicmp — ICMP/Ping（参照 iputils ping）\n")
    host=sys.argv[1] if len(sys.argv)>1 else "127.0.0.1"
    if os.geteuid()!=0:
        print("  ⚠️ ICMP 需要 root 权限（sudo）")
        print("  演示校验和计算:")
        test_pkt=struct.pack("!BBHIH",8,0,0,12345,0)
        print(f"  ICMP Echo Request header: {test_pkt.hex()}")
        print(f"  checksum = {checksum(test_pkt):#06x}")
        print(f"\n  用法: sudo python3 main.py 8.8.8.8")
    else:
        ping(host)

if __name__=="__main__": main()

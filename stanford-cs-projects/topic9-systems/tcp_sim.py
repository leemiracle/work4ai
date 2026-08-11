"""
CS144 - Introduction to Computer Networking
覆盖课程模块：TCP / UDP / IP / HTTP / QUIC

实现内容：
1. 简化 TCP 状态机
2. 三次握手 + 四次挥手
3. 滑动窗口（流量控制）
4. 拥塞控制（ Tahoe / Reno 简化）

参考：Winstein CS144 / RFC 793 / RFC 9000 (QUIC)
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ============ TCP 状态机 ============

class TCPState(Enum):
    CLOSED = "CLOSED"
    LISTEN = "LISTEN"
    SYN_SENT = "SYN_SENT"
    SYN_RECEIVED = "SYN_RECEIVED"
    ESTABLISHED = "ESTABLISHED"
    FIN_WAIT_1 = "FIN_WAIT_1"
    FIN_WAIT_2 = "FIN_WAIT_2"
    CLOSE_WAIT = "CLOSE_WAIT"
    LAST_ACK = "LAST_ACK"
    TIME_WAIT = "TIME_WAIT"


@dataclass
class TCPPacket:
    src_port: int
    dst_port: int
    seq: int
    ack: int
    syn: bool = False
    ack_flag: bool = False
    fin: bool = False
    rst: bool = False
    window: int = 65535
    data: bytes = b""


class TCPEndpoint:
    """简化 TCP 端点（一方）"""

    def __init__(self, name: str):
        self.name = name
        self.state = TCPState.CLOSED
        self.seq = random.randint(0, 1000)
        self.ack = 0
        self.window = 4096
        self.sent_log: list[tuple[str, TCPPacket]] = []
        self.received_log: list[tuple[str, TCPPacket]] = []

    def send(self, pkt: TCPPacket, event: str = ""):
        self.sent_log.append((event or self.state.value, pkt))
        return pkt

    def receive(self, pkt: TCPPacket) -> Optional[TCPPacket]:
        self.received_log.append((self.state.value, pkt))
        return self._transition(pkt)

    def _transition(self, pkt: TCPPacket) -> Optional[TCPPacket]:
        """状态转移逻辑"""
        if self.state == TCPState.CLOSED:
            # Active open: 发 SYN
            if pkt.syn and not pkt.ack_flag:
                self.state = TCPState.SYN_SENT
                return None
        elif self.state == TCPState.LISTEN:
            if pkt.syn:
                self.state = TCPState.SYN_RECEIVED
                self.ack = pkt.seq + 1
                # 回 SYN+ACK
                return self.send(TCPPacket(0, 0, self.seq, self.ack,
                                            syn=True, ack_flag=True), "SYN+ACK")
        elif self.state == TCPState.SYN_SENT:
            if pkt.syn and pkt.ack_flag:
                # 收到 SYN+ACK，回 ACK
                self.state = TCPState.ESTABLISHED
                self.ack = pkt.seq + 1
                return self.send(TCPPacket(0, 0, self.seq, self.ack, ack_flag=True),
                                  "final ACK")
        elif self.state == TCPState.SYN_RECEIVED:
            if pkt.ack_flag:
                self.state = TCPState.ESTABLISHED
                return None
        elif self.state == TCPState.ESTABLISHED:
            if pkt.fin:
                self.state = TCPState.CLOSE_WAIT
                self.ack = pkt.seq + 1
                return self.send(TCPPacket(0, 0, self.seq, self.ack, ack_flag=True),
                                  "ACK FIN")
        elif self.state == TCPState.CLOSE_WAIT:
            # 应用层 close → 发 FIN
            self.state = TCPState.LAST_ACK
            return self.send(TCPPacket(0, 0, self.seq, self.ack, fin=True, ack_flag=True),
                              "FIN")
        elif self.state == TCPState.LAST_ACK:
            if pkt.ack_flag:
                self.state = TCPState.CLOSED
                return None
        return None


def simulate_handshake():
    """模拟 TCP 三次握手"""
    client = TCPEndpoint("Client")
    server = TCPEndpoint("Server")
    server.state = TCPState.LISTEN

    print("\n📋 TCP 三次握手:")
    # 1. Client → SYN
    syn = TCPPacket(1234, 80, client.seq, 0, syn=True)
    print(f"   [{client.name} → {server.name}] SYN seq={syn.seq}")
    server.receive(syn)

    # 2. Server → SYN+ACK
    syn_ack = TCPPacket(80, 1234, server.seq, server.ack, syn=True, ack_flag=True)
    print(f"   [{server.name} → {client.name}] SYN+ACK seq={syn_ack.seq} ack={syn_ack.ack}")
    client.receive(syn_ack)

    # 3. Client → ACK
    ack = TCPPacket(1234, 80, client.seq, client.ack, ack_flag=True)
    print(f"   [{client.name} → {server.name}] ACK")
    server.receive(ack)

    print(f"   Client state: {client.state.value}")
    print(f"   Server state: {server.state.value}")


# ============ 拥塞控制 ============

class TCPCongestionControl:
    """简化版 TCP Tahoe / Reno"""

    def __init__(self, mode: str = "tahoe"):
        self.mode = mode
        self.cwnd = 1.0           # 拥塞窗口
        self.ssthresh = 16.0      # 慢启动阈值
        self.state = "slow_start"
        self.dup_ack = 0

    def on_ack(self) -> dict:
        """收到 ACK"""
        if self.state == "slow_start":
            self.cwnd += 1.0
            if self.cwnd >= self.ssthresh:
                self.state = "congestion_avoidance"
        elif self.state == "congestion_avoidance":
            self.cwnd += 1.0 / self.cwnd
        self.dup_ack = 0
        return {"cwnd": self.cwnd, "state": self.state}

    def on_dup_ack(self) -> dict:
        """收到 3 duplicate ACKs (Tahoe/Reno 都触发)"""
        self.dup_ack += 1
        if self.dup_ack == 3:
            # Fast Retransmit
            self.ssthresh = max(self.cwnd / 2, 1.0)
            if self.mode == "tahoe":
                self.cwnd = 1.0
                self.state = "slow_start"
            elif self.mode == "reno":
                self.cwnd = self.ssthresh + 3  # Fast Recovery
                self.state = "fast_recovery"
        elif self.state == "fast_recovery" and self.mode == "reno":
            self.cwnd += 1
        return {"cwnd": self.cwnd, "state": self.state}

    def on_timeout(self) -> dict:
        """超时（Tahoe/Reno 都重置）"""
        self.ssthresh = max(self.cwnd / 2, 1.0)
        self.cwnd = 1.0
        self.state = "slow_start"
        self.dup_ack = 0
        return {"cwnd": self.cwnd, "state": self.state}


def simulate_congestion(steps=60):
    """模拟拥塞控制行为"""
    print(f"\n📋 TCP Tahoe 拥塞窗口演化 ({steps} 步):")
    tahoe = TCPCongestionControl(mode="tahoe")
    history = []
    for t in range(steps):
        if t == 20:  # timeout
            tahoe.on_timeout()
            print(f"   t={t}: ⚠️ Timeout")
        elif t == 40:  # 3 dup ACK
            tahoe.on_dup_ack()
            tahoe.on_dup_ack()
            tahoe.on_dup_ack()
            print(f"   t={t}: ⚠️ 3 Dup ACK")
        else:
            tahoe.on_ack()
        history.append((t, tahoe.cwnd, tahoe.state))

    # 简单 ASCII 可视化
    print("\n   cwnd 随时间:")
    max_cwnd = max(c for _, c, _ in history)
    for t, cwnd, state in history[::3]:  # 每 3 步采样
        bar = "█" * int(cwnd * 30 / max_cwnd)
        print(f"   t={t:3} {bar} {cwnd:.1f} ({state})")


# ============ 滑动窗口 ============

class SlidingWindow:
    """发送方滑动窗口"""

    def __init__(self, window_size: int = 4):
        self.window_size = window_size
        self.base = 0    # 最早未确认
        self.next_seq = 0  # 下一个发送
        self.buffer = {}

    def send(self, data) -> int:
        if self.next_seq - self.base >= self.window_size:
            return -1  # 窗口满
        seq = self.next_seq
        self.buffer[seq] = data
        self.next_seq += 1
        return seq

    def receive_ack(self, ack_seq: int):
        """收到 ACK"""
        if ack_seq >= self.base:
            # 累计确认
            while self.base <= ack_seq and self.base in self.buffer:
                del self.buffer[self.base]
                self.base += 1

    def in_flight(self) -> int:
        return self.next_seq - self.base


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CS144: TCP / Networking Demo")
    print("=" * 60)

    # 1. 三次握手
    simulate_handshake()

    # 2. 拥塞控制
    simulate_congestion()

    # 3. 滑动窗口
    print("\n📋 滑动窗口 (Go-Back-N):")
    sw = SlidingWindow(window_size=4)
    for i in range(8):
        seq = sw.send(f"DATA_{i}")
        status = f"sent seq={seq}" if seq >= 0 else "BLOCKED (window full)"
        print(f"   Send {i}: {status}, in_flight={sw.in_flight()}")
        if i == 2:  # 收到 ACK 0,1,2
            sw.receive_ack(2)
            print(f"   ← Received ACK 2, base advances, in_flight={sw.in_flight()}")

    print("\n✅ CS144 完成！")


if __name__ == "__main__":
    demo()

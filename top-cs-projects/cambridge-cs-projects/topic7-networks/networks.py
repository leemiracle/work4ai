"""
Part IB Computer Networking (Cambridge CST)
===========================================
覆盖主题：
- TCP 状态机（三次握手 / 四次挥手）
- 拥塞控制（慢启动 / 拥塞避免 / 快恢复）
- 滑动窗口（Go-Back-N / 选择重传）
- CSMA/CD 时隙仿真

核心教材：
- Kurose & Ross 2021 "Computer Networking: A Top-Down Approach" 7th ed, Pearson
- Tanenbaum & Wetherall 2014 "Computer Networks" 5th ed, Pearson
- Stevens 1994 "TCP/IP Illustrated, Volume 1" Addison-Wesley
- Jacobson 1988 "Congestion Avoidance and Control" SIGCOMM

本文件实现：
- TCP 状态机模拟（握手 + 挥手 + TIME_WAIT）
- 拥塞窗口演化（Tahoe / Reno）
- 滑动窗口协议（Go-Back-N）
- CSMA/CD 载波监听 / 冲突检测仿真

运行：
    python networks.py
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque
import random


# ================================================================
# 1. TCP 状态机
# ================================================================

class TCPStateMachine:
    """RFC 793 TCP 状态机"""

    TRANSITIONS = {
        ("CLOSED", "active_open"): ("SYN_SENT", "send SYN"),
        ("CLOSED", "passive_open"): ("LISTEN", ""),
        ("LISTEN", "recv SYN"): ("SYN_RCVD", "send SYN+ACK"),
        ("SYN_RCVD", "recv ACK"): ("ESTABLISHED", ""),
        ("SYN_SENT", "recv SYN+ACK"): ("ESTABLISHED", "send ACK"),
        ("ESTABLISHED", "close"): ("FIN_WAIT_1", "send FIN"),
        ("ESTABLISHED", "recv FIN"): ("CLOSE_WAIT", "send ACK"),
        ("FIN_WAIT_1", "recv ACK"): ("FIN_WAIT_2", ""),
        ("FIN_WAIT_2", "recv FIN"): ("TIME_WAIT", "send ACK"),
        ("CLOSE_WAIT", "close"): ("LAST_ACK", "send FIN"),
        ("LAST_ACK", "recv ACK"): ("CLOSED", ""),
        ("TIME_WAIT", "timeout"): ("CLOSED", "2MSL timeout"),
    }

    def __init__(self):
        self.state = "CLOSED"
        self.log = []

    def event(self, ev: str) -> str:
        key = (self.state, ev)
        if key in self.TRANSITIONS:
            new_state, action = self.TRANSITIONS[key]
            self.log.append(f"{self.state} --[{ev}]--> {new_state}  {action}")
            self.state = new_state
            return new_state
        self.log.append(f"{self.state} --[{ev}]--> ❌ INVALID")
        return self.state


def simulate_three_way_handshake():
    """三次握手"""
    client = TCPStateMachine()
    server = TCPStateMachine()
    server.event("passive_open")  # LISTEN
    client.event("active_open")   # SYN_SENT, send SYN
    server.event("recv SYN")      # SYN_RCVD, send SYN+ACK
    client.event("recv SYN+ACK")  # ESTABLISHED, send ACK
    server.event("recv ACK")      # ESTABLISHED
    return client, server


def simulate_four_way_teardown():
    """四次挥手"""
    client, server = simulate_three_way_handshake()
    client.event("close")          # FIN_WAIT_1
    server.event("recv FIN")       # CLOSE_WAIT
    client.event("recv ACK")       # FIN_WAIT_2
    server.event("close")          # LAST_ACK
    client.event("recv FIN")       # TIME_WAIT
    server.event("recv ACK")       # CLOSED
    client.event("timeout")        # CLOSED
    return client, server


# ================================================================
# 2. 拥塞控制（TCP Tahoe / Reno）
# ================================================================

@dataclass
class TCPCongestionControl:
    """TCP Tahoe / Reno 拥塞控制"""
    cwnd: float = 1.0       # 拥塞窗口（MSS）
    ssthresh: float = 16.0  # 慢启动阈值
    mode: str = "slow_start"
    mode_log: list = field(default_factory=list)
    cwnd_log: list = field(default_factory=list)
    reno: bool = True

    def on_ack(self):
        """收到 ACK"""
        self.cwnd_log.append(self.cwnd)
        self.mode_log.append(self.mode)
        if self.mode == "slow_start":
            self.cwnd += 1  # 指数增长
            if self.cwnd >= self.ssthresh:
                self.mode = "congestion_avoidance"
        elif self.mode == "congestion_avoidance":
            self.cwnd += 1 / self.cwnd  # 线性增长
        elif self.mode == "fast_recovery":
            self.cwnd += 1  # Reno fast recovery

    def on_timeout(self):
        """超时"""
        self.ssthresh = max(self.cwnd / 2, 1)
        self.cwnd = 1
        self.mode = "slow_start"
        self.cwnd_log.append(self.cwnd)
        self.mode_log.append("timeout!")

    def on_dup_ack(self, count: int):
        """3 次重复 ACK"""
        if count >= 3 and self.reno:  # Reno fast retransmit
            self.ssthresh = max(self.cwnd / 2, 1)
            self.cwnd = self.ssthresh + 3  # fast recovery
            self.mode = "fast_recovery"
            self.cwnd_log.append(self.cwnd)
            self.mode_log.append("fast_recovery")


# ================================================================
# 3. 滑动窗口（Go-Back-N）
# ================================================================

class GoBackN:
    """Go-Back-N ARQ"""

    def __init__(self, window_size: int, loss_rate: float = 0.2):
        self.window = window_size
        self.loss = loss_rate

    def send(self, total_packets: int) -> dict:
        random.seed(42)
        base = 1  # 最早未确认
        next_seq = 1
        total_tx = 0
        while base <= total_packets:
            # 发送窗口内所有包
            window_end = min(base + self.window - 1, total_packets)
            for seq in range(next_seq, window_end + 1):
                total_tx += 1
            next_seq = window_end + 1
            # 模拟 ACK
            all_acked = True
            for seq in range(base, window_end + 1):
                if random.random() < self.loss:
                    all_acked = False
                    break
            if all_acked:
                base = window_end + 1
            else:
                next_seq = base  # Go Back N: 重传
        return {"total_packets": total_packets, "total_transmissions": total_tx,
                "efficiency": total_packets / total_tx}


# ================================================================
# 4. CSMA/CD 仿真
# ================================================================

@dataclass
class CSMACDSim:
    """CSMA/CD 时隙仿真（以太网）"""
    n_nodes: int
    p_persistent: float = 0.5  # p-坚持概率
    backoff_max: int = 10

    def run(self, n_slots: int = 1000) -> dict:
        random.seed(42)
        nodes = [{"backoff": 0, "attempts": 0, "sent": 0, "collisions": 0}
                 for _ in range(self.n_nodes)]
        successful = 0
        collision_slots = 0
        idle_slots = 0
        for slot in range(n_slots):
            # 哪些节点要发？
            ready = [i for i, n in enumerate(nodes) if n["backoff"] == 0]
            if len(ready) == 0:
                idle_slots += 1
                for n in nodes:
                    if n["backoff"] > 0:
                        n["backoff"] -= 1
                continue
            if len(ready) == 1:
                # 成功发送
                node = nodes[ready[0]]
                node["sent"] += 1
                node["attempts"] = 0
                successful += 1
            else:
                # 冲突！
                collision_slots += 1
                for i in ready:
                    nodes[i]["collisions"] += 1
                    nodes[i]["attempts"] += 1
                    k = min(nodes[i]["attempts"], self.backoff_max)
                    nodes[i]["backoff"] = random.randint(0, 2**k - 1)
        return {
            "nodes": self.n_nodes, "slots": n_slots,
            "successful": successful, "collisions": collision_slots,
            "idle": idle_slots,
            "efficiency": successful / n_slots,
            "per_node": [{"sent": n["sent"], "collisions": n["collisions"]} for n in nodes],
        }


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 64)
    print("Part IB Computer Networking — Demo")
    print("=" * 64)

    # 1. TCP 状态机
    print("\n📋 1. TCP 三次握手 + 四次挥手")
    client, server = simulate_four_way_teardown()
    print("   Client 转换:")
    for line in client.log:
        print(f"     {line}")
    print(f"   Client 最终状态: {client.state}")
    print(f"   Server 最终状态: {server.state}")

    # 2. 拥塞控制
    print("\n📋 2. TCP Reno 拥塞窗口演化")
    cc = TCPCongestionControl(reno=True)
    for i in range(20):
        cc.on_ack()  # 慢启动 → 拥塞避免
    cc.on_dup_ack(3)  # 快恢复
    for i in range(5):
        cc.on_ack()
    cc.on_timeout()  # 回到慢启动
    for i in range(10):
        cc.on_ack()
    # ASCII 图
    print("   cwnd 演化:")
    max_c = max(cc.cwnd_log)
    for idx in range(0, len(cc.cwnd_log), 5):
        c = cc.cwnd_log[idx]
        bar = "#" * int(c / max_c * 30)
        print(f"   [{idx:3d}] {c:6.1f} |{bar} ({cc.mode_log[idx]})")

    # 3. Go-Back-N
    print("\n📋 3. Go-Back-N 滑动窗口")
    for w in [1, 3, 5]:
        gbn = GoBackN(window_size=w, loss_rate=0.15)
        result = gbn.send(total_packets=20)
        print(f"   window={w}: 发送{result['total_packets']}包, "
              f"实际传输{result['total_transmissions']}, "
              f"效率{result['efficiency']:.0%}")

    # 4. CSMA/CD
    print("\n📋 4. CSMA/CD 时隙仿真")
    for n in [2, 5, 10, 20]:
        sim = CSMACDSim(n_nodes=n, p_persistent=0.3)
        result = sim.run(n_slots=2000)
        print(f"   {n:2d} 节点: 成功={result['successful']}, "
              f"冲突={result['collisions']}, "
              f"空闲={result['idle']}, "
              f"效率={result['efficiency']:.1%}")

    print("\n✅ Computer Networking 完成！")
    print("\n💡 反直觉发现：")
    print("   - TCP 慢启动是指数增长（每 RTT 翻倍），不是「慢」")
    print("   - Go-Back-N 窗口越大效率越高，但单个丢包导致大量重传")
    print("   - CSMA/CD 节点增多时，冲突指数增长 → 效率骤降")
    print("   - 以太网在高负载下退化为 ALOHA（冲突风暴）")


if __name__ == "__main__":
    demo()

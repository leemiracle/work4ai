"""
mini-TCP —— Stanford CS144 风格的 TCP 教学实现
====================================================================
不用真网络包，而是【模拟】出 TCP 的全部关键机制，单机可跑、可注入丢包。

Stanford CS144 的 TCP project 分 5 个 milestone（用 C++ + SST 框架）：
  M1 字节流重组器     → 本文件 Part 1
  M2 TCP Receiver     → 本文件 Part 2
  M3 TCP Sender       → 本文件 Part 3（含重传）
  M4 连接管理+握手     → 本文件 Part 4（三次握手/四次挥手）
  M5 拥塞控制         → 本文件 Part 5（慢启动/AIMD/快重传）

核心思想（CS144 反复强调）：
  TCP 的本质 = 在【不可靠】的 IP 之上，造出【可靠】【有序】【流式】的字节通道。
  靠三件法宝：① 序列号 + 累积 ACK（知道丢了啥）② 重传（补回来）③ 窗口（控流量）

Berkeley CS162 视角（系统层）：
  socket() → 内核维护 TCB（传输控制块）→ 数据从用户态拷到发送缓冲
  → 内核协议栈分段发出 → 网卡。mini-TCP 帮你理解这条链的每一步。

运行：
    python3 mini_tcp.py
依赖：仅标准库
====================================================================
"""
from __future__ import annotations
import random

def banner(t):
    print("\n" + "█" * 68)
    print(f"  {t}")
    print("█" * 68)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 0 · 为什么需要 TCP？                                                ║
# ╚══════════════════════════════════════════════════════════════════════╝

def part0_why_tcp() -> None:
    banner("Part 0 · 为什么需要 TCP？—— IP 不可靠，TCP 来兜底")
    print("""
  IP 层（网络层）只承诺"尽力而为"：
    ✗ 包可能丢失（路由器队列满了就丢）
    ✗ 包可能乱序（走不同路径，先发后到）
    ✗ 包可能重复（路由抖动重传）
    ✗ 包可能损坏（ bit 翻转）

  TCP 在 IP 之上加了【可靠性层】，把上面的"✗"全变成"✓"：
    ✓ 不丢 → 序列号 + 重传
    ✓ 有序 → 重组器（reassembler）
    ✓ 不重 → 去重（看 seq 是否已收）
    ✓ 流控 → 滑动窗口
    ✓ 不拥塞 → 拥塞控制（AIMD）

  一句话：TCP = 不可靠 IP 之上的【可靠字节流】抽象。
  这就是 Stanford CS144 整门课的灵魂——你自己造一遍这个抽象。
""")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 1 · 字节流重组器（CS144 Milestone 1）                                ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
#  收到乱序/重叠的字节片段，重组出连续字节流。
#  这是 TCP Receiver 的地基。

class StreamReassembler:
    """CS144 M1：字节流重组器。收到任意片段，输出连续的已重组字节。"""
    def __init__(self, capacity=1000):
        self.capacity = capacity
        self._buf = {}        # index -> byte (未连续的碎片)
        self._next = 0        # 下一个期待的字节 index
        self._output = []     # 已重组的连续字节（字符串列表）

    def push(self, data: str, index: int):
        """收到一段 data，它对应字节流 [index, index+len) 位置。"""
        for i, ch in enumerate(data):
            abs_idx = index + i
            if abs_idx < self._next:
                continue                       # 已重组过，去重
            if abs_idx not in self._buf:
                self._buf[abs_idx] = ch
        # 检查是否新的连续片段就绪
        while self._next in self._buf:
            self._output.append(self._buf.pop(self._next))
            self._next += 1

    def stream_out(self) -> str:
        return "".join(self._output)

    @property
    def unassembled_bytes(self):
        return len(self._buf)


def part1_reassembler() -> None:
    banner("Part 1 · 字节流重组器（CS144 M1）")
    print("  场景：碎片乱序到达，重组器拼回连续字节流：\n")
    ra = StreamReassembler()
    arrivals = [
        ("loT", 2),    # index 2 起：'loT'
        ("CP", 5),     # index 5 起：'CP'（先到但接不上）
        ("He", 0),     # index 0 起：'He'（到齐 0-4）
        ("xxxx", 99),  # 远处的碎片，暂时接不上
    ]
    for data, idx in arrivals:
        ra.push(data, idx)
        out = ra.stream_out()
        print(f"  收到 '{data}' @index {idx} → 重组区=[{out}]  "
              f"未拼接碎片={ra.unassembled_bytes} 字节")
    print(f"\n  最终字节流: '{ra.stream_out()}'")
    print("""
  → 关键：收到碎片先存着（buf），一旦前面的 gap 被填上，立刻"滑出"到 output。
  → TCP Receiver 就是这么把乱序到达的 segment 拼回有序字节流的。
""")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 2 · TCP Segment + 不可靠网络                                        ║
# ╚══════════════════════════════════════════════════════════════════════╝

class TCPPacket:
    """简化 TCP 报文段。注意：seq 是【字节序号】，不是包编号！"""
    __slots__ = ("seq", "ack", "syn", "fin", "ack_flag", "window", "payload")
    def __init__(self, seq=0, ack=0, syn=False, fin=False, ack_flag=False,
                 window=64, payload=""):
        self.seq = seq; self.ack = ack
        self.syn = syn; self.fin = fin; self.ack_flag = ack_flag
        self.window = window; self.payload = payload

    @property
    def length(self):
        """本 segment 携带的字节流长度（SYN/FIN 各占 1 个序列号空间）。"""
        return len(self.payload) + (1 if self.syn else 0) + (1 if self.fin else 0)

    def flags(self):
        f = []
        if self.syn: f.append("SYN")
        if self.ack_flag: f.append("ACK")
        if self.fin: f.append("FIN")
        return "+".join(f) if f else "—"

    def __repr__(self):
        pl = repr(self.payload) if self.payload else "∅"
        return (f"[{self.flags()}] seq={self.seq} ack={self.ack} "
                f"len={self.length} data={pl}")


class LossyChannel:
    """模拟不可靠网络：可按概率丢包（教学用，同步时序）。"""
    def __init__(self, loss_indices=None, loss_prob=0.0):
        self.loss_indices = set(loss_indices or [])   # 指定丢失的 seq
        self.loss_prob = loss_prob
        self.sent = 0

    def send(self, pkt: TCPPacket, label=""):
        """返回 True 表示送达，False 表示丢失。"""
        self.sent += 1
        indexed_loss = pkt.seq in self.loss_indices
        if indexed_loss:
            self.loss_indices.discard(pkt.seq)   # 一次性：丢完移除，重传有机会成功
        lose = indexed_loss or random.random() < self.loss_prob
        status = "✗ DROPPED" if lose else "✓ delivered"
        print(f"    网络 {label}: {pkt}  →  {status}")
        return not lose


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 3 · TCP Sender（序列号 + 累积 ACK + 重传）                           ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
#  TCP 序列号的精髓（CS144 重点）：
#    seq = 本 segment 第一个字节的【字节流编号】（不是第几个包！）
#    ACK = "我已正确收到 seq < ack 的所有字节"（累积确认）
#    收到 ACK 后，把已确认的从发送缓冲移除；超时未确认 → 重传。

class TCPSender:
    """CS144 M3：发送端。维护未确认字节 + 超时重传。"""
    def __init__(self, channel: LossyChannel, isn=1000):
        self.channel = channel
        self.isn = isn                  # initial sequence number
        self._next_seq = isn + 1        # SYN 占一个序号
        self._base = isn + 1            # 最早未确认的字节序号
        self._outstanding = {}          # seq -> (data, retrans_count)
        self.total_retrans = 0

    def send_syn(self):
        pkt = TCPPacket(seq=self.isn, syn=True)
        self.channel.send(pkt, "SYN  ")
        return pkt

    def send_data(self, data: str):
        """把 data 作为一个 segment 发出。"""
        pkt = TCPPacket(seq=self._next_seq, payload=data, ack_flag=True)
        self._outstanding[self._next_seq] = [data, 0]
        self._next_seq += len(data)
        return self.channel.send(pkt, f"DATA ")

    def retransmit(self, seq):
        """超时重传未确认的 segment。"""
        if seq in self._outstanding:
            data, cnt = self._outstanding[seq]
            pkt = TCPPacket(seq=seq, payload=data, ack_flag=True)
            self._outstanding[seq][1] += 1
            self.total_retrans += 1
            return self.channel.send(pkt, f"RTRN ")
        return False

    def recv_ack(self, ackno: int):
        """收到累积 ACK：移除 seq < ackno 的所有已确认字节。"""
        acked = [s for s in self._outstanding if s + len(self._outstanding[s][0]) <= ackno]
        for s in acked:
            del self._outstanding[s]
        if ackno > self._base:
            self._base = ackno
        return len(acked)

    @property
    def in_flight(self):
        return len(self._outstanding)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 4 · 三次握手 + 数据传输 + 四次挥手                                    ║
# ╚══════════════════════════════════════════════════════════════════════╝

def part4_handshake_transfer() -> None:
    banner("Part 4 · 三次握手 + 数据传输 + 丢包重传")
    print("  场景：客户端发送 'Hi' 给服务端，第 2 个数据包丢失，观察重传。\n")
    ch = LossyChannel(loss_indices={1003})   # 故意让 seq=1003 的 "CD" 丢失
    sender = TCPSender(ch, isn=1000)

    # ── 三次握手 ──
    print("  ── 三次握手 ──")
    sender.send_syn()                          # ① SYN, seq=1000
    print("    服务端回复: [SYN+ACK] seq=5000 ack=1001")
    sender.recv_ack(1001)                      # ② 服务端 SYN+ACK，确认了客户端 SYN
    print("    客户端回复: [ACK] ack=5001   ← 握手完成，连接建立\n")

    # ── 数据传输（含丢包）──
    print("  ── 数据传输（seq=1003 的 'CD' 会被网络丢弃）──")
    sender.send_data("AB")                     # seq=1001, len=2 ✓
    sender.send_data("CD")                     # seq=1003, len=2 ✗ DROPPED
    sender.send_data("EF")                     # seq=1005, len=2 ✓

    print()
    print("  ── 服务端累积 ACK 反馈 ──")
    # CD(seq=1003) 丢了，服务端只能确认到 1003（AB 收到了）
    n = sender.recv_ack(1003)                  # AB 确认
    print(f"    服务端 [ACK] ack=1003  → 客户端确认 {n} 个 segment，"
          f"in-flight={sender.in_flight}")
    print("    服务端：我收到了 'AB'，但 'CD' 还没到（可能丢了）")
    print("    服务端持续回 [ACK] ack=1003（重复 ACK，提示发送端可能丢包）\n")

    # ── 超时重传 ──
    print("  ── 超时重传 ──")
    ok = sender.retransmit(1003)               # 重传 CD
    n2 = sender.recv_ack(1005)                 # CD+EF 都确认了
    print(f"\n    服务端 [ACK] ack=1005  → 客户端确认 {n2} 个 segment，"
          f"in-flight={sender.in_flight}")
    print(f"    总重传次数 = {sender.total_retrans}")
    print("""
  → 累积 ACK 的威力：即使中间 ACK 丢了，后面的 ACK 也能"补确认"前面的。
  → TCP 不说"我收到了第 N 个包"，而是说"我收到了前 ack 个字节"——更鲁棒。
""")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 5 · 拥塞控制（慢启动 / 拥塞避免 / AIMD）                              ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
#  TCP 不只管"可靠"，还管"别把网络压垮"。拥塞窗口 cwnd 是核心：
#    慢启动：cwnd 从 1 开始，每收到一个 ACK 翻倍（指数增长）
#    拥塞避免：cwnd 到阈值 ssthresh 后，每 RTT +1（线性增长）
#    丢包（超时）：ssthresh = cwnd/2，cwnd = 1（回到慢启动）
#    丢包（3 dup ACK）：ssthresh = cwnd/2，cwnd = cwnd/2（快恢复，不回 1）
#  这就是 AIMD：Additive Increase, Multiplicative Decrease。

def part5_congestion() -> None:
    banner("Part 5 · 拥塞控制 —— AIMD 让 TCP 学会'谦让'")
    print("  模拟 20 个 RTT，中间注入一次丢包，观察 cwnd 变化：\n")
    cwnd = 1.0
    ssthresh = 16.0
    print(f"  {'RTT':>4} {'事件':<18} {'cwnd':>7} {'ssthresh':>9}  阶段")
    print("  " + "─" * 56)
    for rtt in range(1, 21):
        if cwnd < ssthresh:
            phase = "慢启动 (×2)"
            cwnd = min(cwnd * 2, ssthresh)
        else:
            phase = "拥塞避免 (+1)"
            cwnd += 1
        # 在 RTT=10 注入一次超时丢包
        if rtt == 10:
            ssthresh = max(cwnd / 2, 2)
            cwnd = 1.0
            print(f"  {rtt:>4} {'💥 超时丢包!':<18} {cwnd:>7.1f} {ssthresh:>9.1f}  "
                  f"→ ssthresh 减半, cwnd 回 1")
            continue
        print(f"  {rtt:>4} {'正常 ACK':<18} {cwnd:>7.1f} {ssthresh:>9.1f}  {phase}")
    print("""
  → AIMD 的哲学：增性增长（慢慢试探带宽）+ 乘性减少（一丢包就果断让步）。
  → 数学上能证明 AIMD 是公平的：多条 TCP 流竞争，最终各占一半带宽。
  → 这就是为什么 10 亿台设备同时上网还能工作——TCP 的分布式公平性。
""")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 6 · 端到端完整模拟                                                  ║
# ╚══════════════════════════════════════════════════════════════════════╝

def part6_full_simulation() -> None:
    banner("Part 6 · 端到端模拟：发送 'Hello, TCP!' 并观察全流程")
    print("  用上面的组件，跑一次完整的可靠传输：\n")

    ra = StreamReassembler()           # 接收端重组器
    ch = LossyChannel(loss_indices={5})  # seq=5 的包会丢
    sender = TCPSender(ch, isn=0)      # isn=0, SYN 占 seq=0, 数据从 seq=1 起

    message = "Hello, TCP!"
    print(f"  待发送消息: '{message}'（{len(message)} 字节）")
    print(f"  分成 3 个 segment 发送，故意丢第 2 个：\n")

    # 分段发送（完整切分：Hell / o,  / TCP!）
    segs = [message[0:4], message[4:7], message[7:]]   # "Hell" "o, " "TCP!"
    seq_cursor = 1                      # 第一个数据 segment 的 seq
    delivered = []
    for seg in segs:
        ok = sender.send_data(seg)
        if ok:
            delivered.append((seq_cursor, seg))
        seq_cursor += len(seg)
    print()

    # 接收端处理到达的包（seq 是 1-based，push 转 0-based）
    print("  接收端重组过程：")
    for seq, data in delivered:
        ra.push(data, seq - 1)
        print(f"    收到 '{data}' → 重组区=[{ra.stream_out()}]")

    # 第 2 段丢了，触发重传
    print(f"\n  ⚠ 第 2 段 'o, '(seq=5) 丢失！接收端只重组到 '{ra.stream_out()}'")
    print("  发送端超时，重传：")
    ok = sender.retransmit(5)
    if ok:
        ra.push("o, ", 4)
        print(f"    收到 'o, ' → 重组区=[{ra.stream_out()}]")

    print(f"\n  ✅ 最终接收端字节流: '{ra.stream_out()}'")
    print(f"  ✅ 发送端总重传次数: {sender.total_retrans}")
    if ra.stream_out() == message:
        print("  ✅ 传输正确！不可靠网络 + 可靠 TCP = 完整消息\n")
    else:
        print(f"  ❌ 传输错误！期望 '{message}'，实际 '{ra.stream_out()}'\n")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 7 · Berkeley CS162 系统视角                                         ║
# ╚══════════════════════════════════════════════════════════════════════╝

def part7_system_view() -> None:
    banner("Part 7 · Berkeley CS162 系统视角 —— socket 到网卡的整条链")
    print("""
  CS162 教你：TCP 不只是协议，它是【操作系统】的一部分。一次 send() 的旅程：

  用户态：
    int fd = socket(AF_INET, SOCK_STREAM, 0);   ← 创建 socket fd
    write(fd, buf, len);                         ← 用户数据进入内核

  内核态（TCP 协议栈）：
    ① 数据进入【发送缓冲区】(send buffer)
    ② TCP 模块按 cwnd/mss 切分成 segment（就是你 Part 3 写的 Sender）
    ③ 每个segment交给 IP 层，加 IP 头 → 经路由表选下一跳
    ④ 进入网卡发送队列 → DMA → 物理网卡 → 网线/光纤

  反方向（接收）：
    网卡中断 → 内核收包 → IP 层 → TCP 层（你 Part 1 的 Reassembler）
    → 放入接收缓冲区 → 唤醒阻塞在 read() 的进程

  关键系统概念：
    • 阻塞 I/O：read() 没数据时进程睡眠（内核 wait queue）
    • 非阻塞 I/O：没数据立刻返回 EAGAIN（要配合 epoll/select）
    • 零拷贝：sendfile() 避免 数据在内核/用户态间反复拷贝

  → mini-TCP 帮你理解协议；CS162 帮你理解协议怎么"长"在 OS 里。
  → 真正的 Linux TCP 栈在 net/ipv4/tcp_*.c，几万行——但核心思想就是本文件这些。
""")


def main() -> None:
    print()
    print("╔" + "═" * 66 + "╗")
    print("║" + " mini-TCP · Stanford CS144 风格 TCP 教学实现 ".center(66) + "║")
    print("╚" + "═" * 66 + "╝")
    part0_why_tcp()
    part1_reassembler()
    part4_handshake_transfer()
    part5_congestion()
    part6_full_simulation()
    part7_system_view()
    print("=" * 68)
    print("  ✅ 全部演示完成。下一步：")
    print("     1. 跑路由协议对照：python3 routing.py")
    print("     2. 修改 LossyChannel 的丢包率，观察重传/拥塞行为变化")
    print("     3. 想做真正的 TCP，去做 CS144 的 C++ project（5 个 milestone）")
    print("=" * 68)
    print()


if __name__ == "__main__":
    main()

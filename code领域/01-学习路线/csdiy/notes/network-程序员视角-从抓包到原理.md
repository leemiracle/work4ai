# 计算机网络 · 程序员视角：从抓包现象反推 TCP/HTTP/epoll 原理

> 学网络最好的方式不是背 RFC，而是把你线上抓包看到的诡异现象一个个钉死在状态机和系统调用上。
> 本文每节都从一个**真实抓包现象**出发，反推背后的协议机制与内核实现，再给**能直接复制的 `tcpdump`/`ss`/`curl`/`strace` 命令**和修复方向，最后落到 CS144 的 TCP 协议栈源码。
>
> 配套课程：Stanford CS144（用 C++ 手写整个 TCP/IP 栈）、UC Berkeley CS168（Internet 架构与协议）、Kurose《自顶向下方法》（配 Wireshark lab）。源码参照：`github-repos/PKUFlyingPig/CS144-Computer-Network/libsponge/`。

---

## 〇、心智模型：网络连接 = 分布式状态机 + 无边界字节流 + 内核 socket 缓冲

所有线上网络事故，归根结底只撞到三堵墙：

| 墙 | 协议/内核做的事 | 出事的表现 |
|----|----------------|-----------|
| **分布式状态机** | 两端各自维护 TCP 状态，靠报文同步（握手/挥手/RST），必须达成共识 | 连接被重置、CLOSE_WAIT 堆积、TIME_WAIT 爆端口 |
| **无边界字节流** | TCP 不保留 `send` 的边界，只保证字节有序到达 | 粘包/半包、拆包拆错、消息截断 |
| **内核 socket 缓冲 + IO 模型** | 数据先入内核收发缓冲区，应用通过 fd + `epoll` 取；Nagle/延迟 ACK 也在这层 | CPU 不高但吞吐上不去、小包延迟 200ms |

下面六节，就是这三堵墙上的六种典型裂缝。每堵墙各撞两次。

---

## 一、连接突然被重置：`Connection reset`

### 抓包现场
线上服务偶发 `curl: (56) Recv failure: Connection reset by peer`，Java 抛 `java.net.SocketException: Connection reset`，Go 报 `read: connection reset by peer`。`tcpdump` 抓到一条带 `Flags [R.]` 之外、`Flags [R]`（Reset）的包，连接瞬间死亡。重启服务、压测高峰、客户端切换网络时最容易出现。

### 反推原理：RST 的触发场景 + 端口耗尽

**RST 是 TCP 的"强制击毙"信号。** 正常关闭走的是四次挥手（FIN），温柔体面；RST 则是"我不要这个连接了，立刻销毁，别等我"。收到 RST 的一端不回任何东西，直接把连接置为错误状态。看 CS144 怎么处理收到的 RST：

```cpp
// libsponge/tcp_connection.cc:35  segment_received —— 收到 RST 立即销毁连接
void TCPConnection::segment_received(const TCPSegment &seg) {
    _time_since_last_segment_received_counter = 0;
    if (seg.header().rst) {            // ← RST 标志位
        _sender.stream_in().set_error();
        _receiver.stream_out().set_error();
        _active = false;               // 连接立刻死亡，不再重传不再挥手
        return;
    }
    ...
}
```

RST 在四种场景下被发送，每种你都可能在线上踩到：

**(1) 向一个没有监听的端口发包。** 客户端 `connect` 一个已重启、端口还没 `bind` 的服务，内核回 RST。这是最常见的"服务刚重启那一瞬"的 reset。

**(2) 向一个已经关闭的连接发包。** 对端进程崩了/被杀/`close(fd)` 了，内核里那个四元组（src_ip:src_port → dst_ip:dst_port）已经不存在，再来的包一律 RST。

**(3) 应用主动 `close` 时缓冲区还有未读数据，或调了 `setsockopt(SO_LINGER, timeout=0)`。** 此时内核不发 FIN，直接发 RST，强制清场。很多"优雅关闭"做不好的服务会这样。

**(4) TCP 重传次数超限，内核主动放弃。** 这是 RST 最隐蔽的来源：网络抖动导致丢包，发送方反复重传，超过上限后内核认为连接已死，发 RST 自我了断。CS144 把这个逻辑写得很直白：

```cpp
// libsponge/tcp_connection.cc:136  tick —— 超时重传，超过上限就 RST 自己
void TCPConnection::tick(const size_t ms_since_last_tick) {
    _sender.tick(ms_since_last_tick);           // 交给 sender 重传
    if (_sender.segments_out().size() > 0) {
        TCPSegment retxSeg = _sender.segments_out().front();
        ...
        if (_sender.consecutive_retransmissions() > _cfg.MAX_RETX_ATTEMPTS) {
            _sender.stream_in().set_error();
            _receiver.stream_out().set_error();
            retxSeg.header().rst = true;        // ← 重传 8 次还失败，RST 了结
            _active = false;
        }
        _segments_out.push(retxSeg);
    }
}
```

而 sender 的重传是**指数退避**（每次失败 RTO 翻倍），避免在拥塞的网络里火上浇油：

```cpp
// libsponge/tcp_sender.cc:129  tick —— 超时重传 + 指数退避
void TCPSender::tick(const size_t ms_since_last_tick) {
    if (!_timer_running) return;
    _time_elapsed += ms_since_last_tick;
    if (_time_elapsed >= _rto) {
        _segments_out.push(_segments_outstanding.front());  // 重传最老的一个
        if (_receiver_window_size || _segments_outstanding.front().header().syn) {
            ++_consecutive_retransmissions;
            _rto <<= 1;           // ← 指数退避：1s→2s→4s→8s…
        }
        _time_elapsed = 0;
    }
}
```

`MAX_RETX_ATTEMPTS = 8`（`tcp_config.hh:17`），意味着初始 RTO 1s 的话，最坏要等 `1+2+4+...+128 ≈ 8` 分钟连接才被放弃——这就是为什么有时候"卡很久才报 reset"。

**端口耗尽（另一种"连不上"）。** 这不是 RST，但常和 reset 混淆。客户端作为主动连接方，每条连接占一个**临时端口**（ephemeral port，默认范围 `32768-60999`，约 2.8 万个）。如果你是高并发客户端、又频繁短连接，加上 `TIME_WAIT` 占用端口约 60 秒（2MSL），端口很快耗尽，表现为 `connect: Cannot assign requested address`。注意这时没有 RST 包，是本地内核直接拒绝 `connect`。

### 排查命令（都能跑）

```bash
# 1. 抓 RST 包（最直接）—— 看是谁发的、什么时机
sudo tcpdump -i any -n 'tcp[tcpflags] & tcp-rst != 0' and port 8080
# [S.] 后立刻 [R] → 端口没监听；ESTABLISHED 后突然 [R] → 进程崩了或 close(SO_LINGER)

# 2. 看当前所有 TCP 连接状态分布（一眼看出哪种状态异常多）
ss -tan | awk 'NR>1{print $1}' | sort | uniq -c | sort -rn
# ESTAB 占绝大多数正常；TIME_WAIT 几千正常，CLOSE-WAIT 一堆就是 bug

# 3. 看本机端口是否快耗尽（客户端排查连不上）
ss -tan | awk 'NR>1{print $4}' | awk -F: '{print $NF}' | sort -u | wc -l
cat /proc/sys/net/ipv4/ip_local_port_range     # 可用端口范围

# 4. 看一条具体连接的内核统计（重传次数、RTO、cwnd）
ss -ti dst 10.0.0.1:8080    # retrans 高 → 网络丢包，离 reset 不远

# 5. 模拟一个 RST：服务端主动 close 一个有未读数据的连接
python3 -c "
import socket,time
s=socket.socket(); s.bind(('',9090)); s.listen(1)
c,_=s.accept()             # 接受连接后什么都不读
time.sleep(2)              # 等客户端发数据进来
s.close()                  # 缓冲区还有数据 → 内核发 RST 而非 FIN
"
# 客户端 nc localhost 9090 敲几个字，会看到 connection reset
```

### 修复方向
- **客户端重试 + 熔断**：reset 是瞬态故障的常见表现，做有限重试（指数退避），连续失败就熔断，别雪崩。先 `tcpdump` 抓是谁发的 RST，再查对应端。
- **优雅关闭**：服务端关闭前确保读写都 `shutdown` 干净，别用 `SO_LINGER=0` 制造 RST；长连接 + 心跳，避免连接半死被中间设备 RST。
- **治端口耗尽**：短连接改长连接（连接池）；调大 `ip_local_port_range`；启用 `tcp_tw_reuse`（复用 TIME_WAIT 端口）。

### 一行本质
> **RST = TCP 的强制击毙令：要么你打错了门（端口没监听），要么对方已经死了，要么重传到绝望内核自己了断。**

**CS144 对应**：`tcp_connection.cc:38-43`（收到 RST 销毁连接）、`tcp_connection.cc:114-121`（`send_RST`）、`tcp_connection.cc:146-151`（重传超限自尽）、`tcp_sender.cc:129-142`（指数退避重传）、`tcp_state.cc:61-66`（RESET 状态）。

---

## 二、高并发服务 CPU 不高，吞吐却上不去

### 抓包现场
服务上线，压测到 1 万 QPS，`top` 一看 CPU 才 30%，内存也富裕，但 P99 飙到几百毫秒，`ss -s` 显示连接数几万。再加并发，吞吐不升反降。这是典型的"**IO 模型没选对**"——CPU 没忙在干活上，全忙在等待和上下文切换上。

### 反推原理：阻塞模型 vs select/poll/epoll

网络 IO 的本质是：**数据到达内核的 socket 接收缓冲区（`sk_buff` 队列），应用什么时候、怎么把数据取出来**。取数据的姿势决定了能扛多少并发连接。

**(1) 阻塞 IO（blocking IO）。** 一个连接配一个线程，`read()` 没数据就把线程挂起（进 `S` 状态，等内核唤醒）。简单直观，但 1 万连接 = 1 万线程，光线程栈就吃 80GB 内存（默认 8MB/线程），上下文切换把 CPU 耗光。这就是早期 Apache prefork / Tomcat bio 的模型，扛不过 C10K。

**(2) 非阻塞 IO + 轮询。** `read()` 立刻返回，没数据返回 `EAGAIN`。但你得自己 `while` 死循环轮询，把一个核跑满 100%，纯属浪费。

**(3) IO 多路复用（select/poll/epoll）。** 核心思想：**一个线程同时盯一堆 fd，谁就绪了内核通知谁**，线程只处理"有事干"的连接。

`select` 和 `poll` 的致命伤是**每次调用都要把全部 fd 从用户态拷到内核态，内核再线性扫描所有 fd 看谁就绪**，连接数一上万，单次调用的开销就线性爆炸。而且 `select` 还有 `FD_SETSIZE`（默认 1024）的硬上限。

**`epoll` 为什么快？** 三个设计：
- **内核维护就绪列表**：`epoll_ctl` 注册 fd 时把回调挂到该 socket 的等待队列上；数据一到内核，网卡中断处理直接把这个 fd 链入"就绪链表"，`epoll_wait` 只需把就绪链表里的 fd 拷出来，**O(就绪 fd 数)** 而非 O(总 fd 数)。
- **注册一次复用**：`epoll_ctl(ADD)` 只在连接建立时调一次，不像 `select` 每次都要重新传全部 fd。
- **`epoll_wait` 是真的阻塞/超时**：没事件时线程睡着（CPU 0%），有事件被唤醒，拿到的全是"真有事"的 fd，不浪费一个循环。

这就是 Nginx、Redis、Netty、Go runtime（底层 `epoll` + `netpoller`）扛十万百万连接的秘密。下面这段是 epoll 的标准用法骨架，Redis/Nginx 都是它的变体：

```c
// epoll 经典用法 —— 一个线程管 N 个连接，Redis/Nginx 都是它的变体
int epfd = epoll_create1(0);
struct epoll_event ev = {.events = EPOLLIN, .data.fd = listen_fd};
epoll_ctl(epfd, EPOLL_CTL_ADD, listen_fd, &ev);        // 注册一次，复用

struct epoll_event events[1024];
for (;;) {
    int n = epoll_wait(epfd, events, 1024, -1);  // 没事件就睡，n=就绪 fd 数，O(就绪数)
    for (int i = 0; i < n; i++) {                // 只处理"有事的"，不空转
        if (events[i].data.fd == listen_fd)
            epoll_ctl(epfd, EPOLL_CTL_ADD, accept(listen_fd,...), &ev);  // 新连接也注册
        else
            read(events[i].data.fd, buf, ...);   // 就绪的直接读，不阻塞
    }
}
```

**为什么 CPU 不高但吞吐上不去？** 几个可能：连接多了 `epoll_wait` 返回的事件处理太慢（业务逻辑重/锁竞争）；每次 `read`/`write` 只搬一点点（缓冲太小、没批量）；或者根本还在用阻塞模型（每连接一线程），CPU 全耗在线程切换上，`top` 看着不高是因为都阻塞着，但上下文切换 `cs` 飙高。

### 排查命令（都能跑）

```bash
# 1. 看服务在用什么 IO 模型（最关键一招）—— strace 抓系统调用
strace -p <pid> -f -e trace=epoll_wait,accept4,read,write -c
# epoll_wait 多 → epoll 模型（对）；大量 read 阻塞 → 阻塞模型（错）；select/poll → 老模型

# 2. 实时看 epoll_wait 等几个 fd、等多久（验证是否空转）
strace -p <pid> -e trace=epoll_wait -T -tt
# epoll_wait(...,-1)=1 <0.000123> 等 123us 拿到 1 事件，正常；timeout=0 立刻返回 → 忙轮询 bug

# 3. 看连接数 vs 线程数，判断是不是"一连接一线程"
ss -s && ps -eL | grep -c <进程名>    # 线程数≈连接数 → 阻塞模型，该换了

# 4. 看上下文切换次数（阻塞模型/锁竞争的指纹）
pidstat -w -p <pid> 1                 # cswch/s 自愿切换(等IO)

# 5. 看每条连接的收发缓冲区有没有堆积（处理不过来）
ss -tin dst :8080 | head
# Recv-Q 大且不消化 → 应用读太慢；Send-Q 大 → 对端收得慢或网络堵

# 6. 看网络栈软中断分布（高并发下单核可能被打满）
watch -n1 'cat /proc/net/softnet_stat'   # 第三列非0表示软中断丢包，需调 RPS/RFS
```

### 修复方向
- **务必用 epoll/kqueue 模型**：C 直接 `epoll`；Java 用 NIO/Netty（别用 bio）；Go 天生 `netpoller`；Python 用 `asyncio`/`uvloop`。一连接一线程的模型扛不过 C10K。
- **配 `SO_REUSEPORT` + 多进程**：Nginx/Envoy 的玩法，多个 worker 各自 `epoll` 同一端口，内核负载均衡，避免单 `accept` 成瓶颈。
- **业务别在 IO 线程干重活**：耗时逻辑扔到 worker 池/协程，IO 线程只管收发，否则 `epoll_wait` 处理慢、连接堆积。
- **调缓冲区 + 绑核**：`SO_RCVBUF/SO_SNDBUF` 别让窗口缩水；网卡中断绑核 + 开 RPS/RFS 多核分发软中断。

### 一行本质
> **吞吐上不去的元凶常常不是 CPU 不够，而是 IO 模型不对——`epoll` 让一个线程只伺候"有事的"连接，阻塞模型却让线程在无谓的等待和切换里耗尽预算。**

**原理对应**：Linux `fs/eventpoll.c`（epoll 内核实现，红黑树管 fd + 就绪链表）。CS144 虽不涉及 epoll，但其 `TCPConnection::segment_received`（`tcp_connection.cc:35`）就是协议栈收到报文后"分发"的逻辑，和 epoll 把就绪 fd 分发给应用是同一层思想。

---

## 三、粘包 / 半包：消息怎么拆都拆错

### 抓包现场
自定义二进制协议，客户端一次 `send` 三个 100 字节的请求，服务端 `recv` 一次却读到 250 字节（少了 50），或者一次读到 300 字节（三个粘一起）。换 MTU、加 `sleep` 都没用，每次粘/半的边界还不一样。新人最爱问的"TCP 怎么解决粘包"——其实这问题本身就是误区。

### 反推原理：TCP 是字节流，根本没有"包"的概念

**TCP 给你的承诺只有两条：(1) 字节按顺序到达；(2) 字节不丢不重。它从没承诺过"你一次 `send` 的内容对端一次 `recv` 收到"。**

TCP 是**字节流（byte stream）**，不是消息流。你调三次 `send(fd, "AAA")`、`send(fd, "BBB")`、`send(fd, "CCC")`，对端可能 `recv` 出 `"AAAB"`、`"BBCC"`、`"C"`，也可能一次性 `recv` 出 `"AAABBBCCC"`，完全取决于内核发送缓冲区的积压情况、MSS、Nagle 算法、网络时序。**"包"是应用层概念，TCP 层压根不存在。**

CS144 用一个 `ByteStream` 把这件事讲透了——发送方往里 `write` 字节，接收方从里 `read` 字节，中间是个无结构的 `deque<char>`，**没有任何"消息边界"标记**：

```cpp
// libsponge/byte_stream.hh:19  ByteStream 的存储 —— 就是个 deque<char>，没有边界
class ByteStream {
  private:
    std::deque<char> buffer;   // ← 字节队列，write 进来/read 出去，谁也不记"这拨是哪次写的"
    size_t capacity;
    ...
};
```

TCP 的可靠传输保证的就是：你 `write` 进 `deque` 的字节，按顺序、完整地出现在对端的 `deque` 里。至于你分几次 `write`、对端分几次 `read`，那是你和内核缓冲区、网络的"缘分"，协议不管。

所以**"粘包"不是 TCP 的 bug，是应用层没做消息分帧（framing）的 bug**。所有自定义协议都必须自己定义"一条消息的边界在哪"，常见三种方案：

**(1) 固定长度。** 每条消息恰好 N 字节，不够补齐。简单但浪费带宽，适合定长控制报文。

**(2) 分隔符。** 用一个不可能出现在正文里的字节/字符串（如 `\r\n`、`\0`）标记结束。HTTP/1 的 header、Redis 协议、行式协议都这样。风险是正文里混入分隔符要先转义。

**(3) 长度前缀（TLV/LV）。** 最通用：消息 = `[长度 N（定长，比如 4 字节大端 int）][N 字节 payload]`。接收方先读够 4 字节拿到 N，再死等够 N 字节 payload，凑齐算一条。gRPC（基于 HTTP/2 的 LENGTH frame）、Thrift、Protobuf over TCP、MQTT 都是这个思路的变体。

接收侧的标准拆包循环（伪码）：

```python
buf = b''
while True:
    buf += sock.recv(4096)                   # 攒着（半包也攒）
    while len(buf) >= 4:                      # 至少能读出 4 字节长度字段
        n = int.from_bytes(buf[:4], 'big')
        if len(buf) < 4 + n: break            # payload 没收全，继续等
        msg = buf[4:4+n]; buf = buf[4+n:]     # 凑齐一条，剩下的留给下一条
        handle(msg)
```

**"半包"就是同一次 `send` 的内容被拆成多个 TCP 段到达，对端要分多次 `recv` 凑齐**——这恰恰是 TCP 的正常行为，不是异常。

### 复现命令（都能跑）

```bash
# 终端 A（服务端）：nc -l 9090 | xxd | head
# 终端 B（客户端），三条之间不 sleep：printf 'AAAA\x00BBBB\x00CCCC\x00' | nc localhost 9090
# 会看到它们一次性到达（粘在一起），证明 send 次数 ≠ 接收边界

# 2. Python 复现粘包 + 长度前缀拆包（一条命令跑完）
python3 -c "
import socket, struct, threading, time
def server():
    s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 9091)); s.listen(1)
    c, _ = s.accept()
    buf = b''
    msgs = []
    while len(msgs) < 3:
        buf += c.recv(100)
        while len(buf) >= 4:
            n = struct.unpack('>I', buf[:4])[0]      # 读 4 字节长度前缀
            if len(buf) < 4 + n: break                # 半包，继续等
            msgs.append(buf[4:4+n]); buf = buf[4+n:]  # 凑齐一条
    print('收到 3 条消息:', msgs)
    c.close(); s.close()

threading.Thread(target=server, daemon=True).start()
time.sleep(0.3)
c = socket.socket(); c.connect(('127.0.0.1', 9091))
for m in [b'hello', b'world', b'tcp-stream']:
    c.sendall(struct.pack('>I', len(m)) + m)   # 长度前缀 + payload，哪怕三次 send 粘成一次也没事
    time.sleep(0.05)
c.close()
"
# 输出：收到 3 条消息: [b'hello', b'world', b'tcp-stream'] —— 边界完全靠应用层保证

# 3. 抓包看 TCP 段如何切分应用数据（seglen 和 send 次数毫无关系）
sudo tcpdump -i lo -n 'tcp port 9091' -A | grep -A2 'Length'
# 一次 send 可能被切成多个段，多次 send 也可能合到一个段
```

### 修复方向
- **永远自己分帧**：自定义 TCP 协议必须定义消息边界，首选"4 字节长度前缀 + payload"。别假设"一次 send = 一次 recv"。
- **用现成协议**：能上 HTTP/gRPC/MQTT 就别自己造，它们已把分帧、压缩、多路复用做对了。
- **接收侧必须循环凑包**：维护接收缓冲区，`recv` 数据追加进去循环切出完整消息，半包是常态。别用 `sleep` 当分隔符。

### 一行本质
> **TCP 是无边界的字节流，"粘包"是应用层没分帧的锅；解法只有一种：自己定义消息边界（长度前缀最稳），在接收侧循环凑包。**

**CS144 对应**：`byte_stream.hh:19`（`deque<char>` 字节流，无消息边界）、`stream_reassembler.cc`（字节流的重组，证明 TCP 只保证字节序不保证"包"）、`tcp_receiver.cc`（把字节流交给上层应用）。

---

## 四、`CLOSE_WAIT` 一堆不释放

### 抓包现场
服务跑两天，`ss -tan | grep CLOSE-WAIT | wc -l` 几千个还在涨，fd 也跟着涨，最后 `Too many open files` 拒服务。`netstat` 一看，全是被动关闭那端的 CLOSE_WAIT，对端早就 FIN 走了，本端却卡在这个状态不动。

### 反推原理：四次挥手状态机 + 谁负责 `close`

TCP 关闭是**四次挥手**（全双工，两个方向各关一次）。被动关闭方卡在 CLOSE_WAIT：

```
主动关闭方                         被动关闭方
ESTABLISHED                        ESTABLISHED
   |  应用 close(fd)                   |
   |  ─────── FIN ──────────────────►  |  收到 FIN → CLOSE_WAIT（卡这！等应用 close）
FIN_WAIT_1                        CLOSE_WAIT
   |  ◄────── ACK ───────────────────  |  （应用还能 read 残留数据，write 报错）
FIN_WAIT_2                             |  应用终于调 close(fd)
   |  ◄────── FIN ───────────────────  |  发 FIN → LAST_ACK
TIME_WAIT                          LAST_ACK
   |  ─────── ACK ──────────────────►  |
TIME_WAIT(等 2MSL)                 CLOSED
CLOSED
```

看 CS144 的状态定义，CLOSE_WAIT 的本质是"**对端的 FIN 我收到了、我的接收流结束了，但我的发送流还没结束（应用还没 `close`）**"：

```cpp
// libsponge/tcp_helpers/tcp_state.cc:35  CLOSE_WAIT —— 对端 FIN 已到，本端 FIN 未发
case TCPState::State::CLOSE_WAIT:
    _receiver = TCPReceiverStateSummary::FIN_RECV;   // 接收流已结束
    _sender = TCPSenderStateSummary::SYN_ACKED;       // 发送流还没结束（没发FIN）
    _linger_after_streams_finish = false;
    break;
```

**所以 CLOSE_WAIT 堆积，根因永远是一个：你的应用代码收到对端 FIN（即 `read` 返回 0 / EOF）后，没有及时调 `close(fd)`。** 连接卡在"对端关了我没关"的半开状态，内核里这个四元组和 fd 一直占着，直到应用层主动 `close` 才会进入 LAST_ACK → CLOSED。

常见代码 bug：
- `read` 返回 0（对端 FIN）后，直接 `break` 跳出循环，却忘了 `close(fd)`，fd 泄漏。
- 异常路径里只 `return` 没 `close`，连接卡死。
- 用了连接池但没处理"连接已被对端关闭"的情况，从池里取出来用才发现已坏，但归还时没关。
- 第三方库/框架的 bug，或 HTTP `Connection: close` 的响应没正确关闭。

**对比 TIME_WAIT：** 主动关闭方才会进 TIME_WAIT，待 2MSL（Linux 默认 60 秒）是为了：① 防止自己最后那个 ACK 丢了、对端重传 FIN 时自己还能应答；② 让网络上残留的旧报文消亡，别污染下一次同四元组的连接。CS144 用 `10 * rt_timeout` 模拟 2MSL：

```cpp
// libsponge/tcp_connection.cc:161  tick —— 两端都结束后，主动关闭方滞留 2MSL
if (check_inbound_ended() && check_outbound_ended()) {
    if (!_linger_after_streams_finish) {
        _active = false;                                   // 被动方直接结束
    } else if (_time_since_last_segment_received_counter >= 10 * _cfg.rt_timeout) {
        _active = false;                                   // 主动方等够 2MSL 才结束
    }
}
```

TIME_WAIT 是**正常且必要**的状态，少量无妨；但它占端口和一小块内核内存，**服务端如果是大量短连接的主动关闭方**，会积累海量 TIME_WAIT。CLOSE_WAIT 则**永远是 bug**，一个都不该有。

### 排查命令（都能跑）

```bash
# 1. 统计各状态连接数（CLOSE_WAIT > 0 就要警觉）
ss -tan | awk 'NR>1{print $1}' | sort | uniq -c | sort -rn

# 2. 找出所有 CLOSE_WAIT 连接，定位是哪个进程、哪条连接
ss -tanp state close-wait    # users:(("java",pid=12345,fd=99)) → fd=99 卡着没关

# 3. 看进程打开的 fd（确认 fd 泄漏）
ls -l /proc/<pid>/fd | grep socket | wc -l     # socket fd 数
cat /proc/<pid>/limits | grep 'open files'     # fd 上限，超了就 Too many open files

# 4. 对比 TIME_WAIT（主动关闭方的正常状态）
ss -tan state time-wait | wc -l    # 自己关太多短连接才会爆

```python
# 5. 模拟一个 CLOSE_WAIT：服务端 read 到 EOF 后故意不 close
python3 -c "
import socket,time
s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('',9092)); s.listen(1)
c,_=s.accept()
c.recv(100)         # 客户端 close 后这里返回 b''(EOF)
print('收到 EOF，故意不 close，ss 会看到 CLOSE_WAIT')
time.sleep(60)
"
# 客户端：python3 -c \"import socket; s=socket.socket(); s.connect(('localhost',9092)); s.close()\"
# 然后 ss -tan state close-wait 观察
```

### 修复方向
- **`read` 返回 0 立刻 `close`**：所有网络代码的铁律。`recv`/`read` 返回 0 = 对端 FIN，处理完残留必须 `close(fd)`。
- **用 RAII 保证 `close`**：C++ 析构 `close`，Go `defer conn.Close()`，Java try-with-resources。别让异常路径漏关。
- **连接池要校验存活**：取连接时检查是否还活着（`SO_KEEPALIVE` 或心跳），坏了丢弃重建。
- **服务端尽量做被动关闭方**：让客户端先 FIN，服务端进 CLOSE_WAIT（你能控制立刻关），避免积压 TIME_WAIT。

### 一行本质
> **CLOSE_WAIT = 对端 FIN 已到但你的应用没 `close(fd)`，fd 泄漏；TIME_WAIT = 你是主动关闭方，正常滞留 2MSL 防止报文错乱。前者永远是 bug，后者是特性。**

**CS144 对应**：`tcp_state.cc:35-44`（CLOSE_WAIT / LAST_ACK 状态定义）、`tcp_state.cc:57-60`（TIME_WAIT 状态）、`tcp_connection.cc:161-167`（2MSL 滞留逻辑）、`tcp_connection.cc:105-112`（`end_input_stream` 发起本端 FIN）。

---

## 五、接口偶尔慢 200ms：Nagle + 延迟 ACK 的死亡组合

### 抓包现场
内部 RPC 调用，绝大多数 5ms 返回，但**偶发 200ms / 40ms / 100ms** 的毛刺，规律性极强。抓包发现：客户端的小请求包发出后，要等很久才看到 ACK，然后服务端的响应才回。CPU、网络都不忙，就是莫名其妙卡一下。

### 反推原理：Nagle 算法 + Delayed ACK 互相锁死

这是两个"为减少小包而设计"的优化，单独看都合理，组合起来却制造了 200ms 的死锁。

**Nagle 算法（RFC 896，1984）。** 问题：像 Telnet 这种交互式应用，每敲一个键就发一个 1 字节的包，外加 40 字节 TCP/IP 头，开销巨大。Nagle 的规则：**如果上一个包还没被 ACK，当前要发的小数据就先攒在发送缓冲区，等 ACK 来了或攒够一个 MSS 再一起发。** 这样能把一堆小包合并成大包。CS144 的 `fill_window` 里虽然没有显式实现 Nagle，但 TCP 标准要求发送方在窗口未确认时延迟发送小段，思想一致。

**Delayed ACK（延迟确认，RFC 1122）。** 问题：每个数据包都立刻回 ACK，反向会有大量纯 ACK 小包。规则：**收到的数据不立即 ACK，最多延迟 200ms（Linux 默认 40ms 的 HZ 粒度），期间如果有反向数据要发就把 ACK 捎带（piggyback）在数据包里，省一个纯 ACK。**

**死亡组合：** 客户端发了一个小请求（触发 Nagle，因为还没 ACK，数据被攒住不发？不——第一个包会发出去），服务端收到后要回 ACK（触发 Delayed ACK，等 40ms 看有没有数据捎带）+ 处理后回响应。问题出在第二次：客户端发了两个小包（比如先发 header 再发 body，或先发请求再发一小段补充），第二个小包被 Nagle 攒住，等服务端的 ACK；服务端的 ACK 被 Delayed ACK 拖着 40ms；客户端等不到 ACK 就一直不发第二个包；服务端等不到完整请求就不回响应。**双方互等，直到 40ms 延迟 ACK 超时，链路才解开。**

这就是那神秘的 40ms（Linux `TCP_ACK_DELAY`）/ 200ms 的来源。**请求-响应型小包协议最容易踩**：Redis pub/sub、MySQL 的某些小查询、自研 RPC 的"两次 write"模式。

**TCP_NODELAY 是解药。** `setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &on, ...)` 关掉 Nagle 算法，小数据立刻发。代价是可能多几个小包，但在低延迟的请求-响应场景（尤其内网），Nagle 带来的合并收益远小于它制造的延迟。Redis、MySQL、gRPC 默认都开 `TCP_NODELAY`。

### 复现与排查命令（都能跑）

```bash
# 1. 抓包看 ACK 延迟（关键证据）—— 找两个相邻包之间 >40ms 的 ACK 间隔
sudo tcpdump -i any -n -tttt 'tcp port 8080' | head -40
# 看到 [.] ACK 和它确认的数据包时间戳相差 ~40ms，就是 Delayed ACK

# 2. 看连接是否开了 TCP_NODELAY（间接验证）
ss -ti dst :8080     # 看到 nodelay 字样 = 已开；没有 = Nagle 在工作

# 3. 复现 40ms 延迟：两次 write 小包，触发 Nagle+DelayedACK
python3 -c "
import socket, time
s = socket.socket(); s.connect(('127.0.0.1', 9093))   # 服务端用 nc -l 9093
s.send(b'A'); s.send(b'B')   # 两次小 send，第二个被 Nagle 攒住等 ACK
time.sleep(1)
"
# 开 nodelay 后对比：s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

# 4. curl 量化各阶段耗时（网络排障神器）
curl -o /dev/null -s -w 'connect:%{time_connect}s tls:%{time_appconnect}s ttfb:%{time_starttransfer}s total:%{time_total}s\n' http://example.com
# ttfb 高但 connect 低 → 服务器处理慢或 Nagle/延迟ACK作怪
```

### 修复方向
- **请求-响应协议默认开 `TCP_NODELAY`**：Redis/MySQL/gRPC/自研 RPC 都该开，尤其内网小包交互。性价比最高的一行代码。
- **别把一个请求拆成两次 `write`**：`write(header)` 再 `write(body)` 是 Nagle 高发场景。要么合并成一次 `write`，要么开 `TCP_NODELAY`，要么用 `writev` 一次发多段。
- **HTTP/2/gRPC 天然免疫**：多路复用 + 帧化，Nagle 影响被摊薄。

### 一行本质
> **200ms 毛刺常常是 Nagle（攒小包等 ACK）和 Delayed ACK（拖 40ms 才回 ACK）的死亡互锁；请求-响应型协议请无脑 `TCP_NODELAY`。**

**原理对应**：Linux `net/ipv4/tcp_output.c`（Nagle 判断 `tcp_nagle_check`）、`net/ipv4/tcp_input.c`（Delayed ACK 定时器，默认 40ms）。CS144 `tcp_sender.cc:fill_window`（发送时机控制）。

---

## 六、HTTPS 第一次慢、后面快：TLS 握手与会话复用

### 抓包现场
首次访问某 HTTPS 接口要 300ms，第二次访问只要 20ms。`curl` 反复测，前几次总有一个"冷启动"开销。抓包发现第一次比第二次多了一长串 `Client Hello`/`Server Hello`/证书/密钥交换的包，后面就没有了。

### 反推原理：TLS 握手开销、会话复用、HTTP/2

HTTP over TLS（HTTPS）在 TCP 三次握手之上，还要套一层 **TLS 握手**，这是"第一次慢"的全部来源。TLS 1.2 的完整握手要 **2 个 RTT**（4 个飞行段），TLS 1.3 优化到 **1 个 RTT**，但都比裸 HTTP 的 0 个额外 RTT 多。

**TLS 1.2 握手流程（2-RTT，"第一次慢"的来源）：**
```
Client                              Server
  | ── ClientHello ────────────────► |   RTT1（密码套件、随机数）
  | ◄── ServerHello+Certificate ──── |   证书链（验签，可能几 KB）
  | ◄── ServerKeyExchange+Done ───── |
  | ── ClientKeyExchange+Finished ─► |   RTT2（客户端算出主密钥）
  | ◄── ChangeCipherSpec+Finished ── |   RTT2 结束，之后才能发 HTTP
  | ═══ 应用数据（HTTP）加密传输 ═══ |
```

**第一次慢的成本明细：**
- **2 个 RTT** 的握手往返（TLS 1.2），跨洋 150ms RTT 就是 300ms 光在握手。
- **证书验证**：客户端要验证证书链（服务端证书 → 中间 CA → 根 CA），可能触发 OCSP 在线查吊销，或下载缺失的中间证书，又是一轮网络。
- **非对称加密计算**：密钥交换（ECDHE/RSA）的公钥运算，服务端 + 客户端各几十毫秒 CPU。
- **TCP 握手**：在 TLS 之前还有 1 个 RTT 的 TCP 三次握手。

**会话复用（Session Resumption）让"后面快"。** TLS 设计了两种复用机制，避免重复完整握手：
- **Session ID / Session Ticket**：首次握手后服务端给一个会话票据，客户端下次带上，服务端认出就直接用之前协商好的主密钥，**1 个 RTT**（TLS 1.2）甚至 **0-RTT**（TLS 1.3 早期数据）。
- **TLS 1.3 PSK**：预共享密钥模式，已知密钥时 0-RTT 直接发数据。

所以"第一次慢后面快"= **首次完整握手（2 RTT + 验证 + 计算），后续会话复用（1 RTT 甚至 0 RTT）**。`curl` 默认每次新连接都重新握手，所以每次都"第一次"；浏览器/HTTP 客户端带连接池和会话缓存，所以复用快。

**HTTP/2 的加成。** HTTPS 通常跑在 HTTP/2 上（`h2`，基于 TLS 的 ALPN 协商）。HTTP/2 一个 TCP 连接多路复用（multiplexing），多个请求并发跑在同一个流上，**省了反复握手和队头阻塞**。所以现代 HTTPS 客户端会保持一个长连接，所有请求复用它——这也是"后面快"的另一半原因。

### 排查命令（都能跑）

```bash
# 1. 量化 HTTPS 各阶段耗时（最直观）—— 连接、TLS握手、首字节、总耗时
curl -o /dev/null -s -w 'dns:%{time_namelookup}s  tcp:%{time_connect}s  tls:%{time_appconnect}s  ttfb:%{time_starttransfer}s  total:%{time_total}s\n' https://www.cloudflare.com
# tls(time_appconnect) 就是纯 TLS 握手耗时；连测两次，第二次变小=会话复用

# 2. 看 TLS 握手细节（openssl s_client 是 TLS 排障神器）
echo | openssl s_client -connect www.cloudflare.com:443 -servername www.cloudflare.com 2>/dev/null | grep -E 'Protocol|Cipher|Session-ID'
# Protocol: TLSv1.3 / 有 Session-ID 或 ticket → 下次可复用

# 3. 抓包看完整 TLS 握手包序列
sudo tcpdump -i any -n 'tcp port 443' -w https.pcap   # 用 wireshark 打开看 ClientHello/Certificate

# 4. 对比 HTTP vs HTTPS 的握手开销，并强制不复用复现"第一次慢"
curl -o /dev/null -s -w '%{time_appconnect}\n' http://example.com          # 0（无TLS）
curl -o /dev/null -s -w '%{time_appconnect}\n' --no-keepalive https://example.com  # 每次完整握手=慢
```

### 修复方向
- **连接池 + 会话复用**：客户端复用 TLS 连接（连接池）并开启 session ticket 缓存，把"第一次慢"变成"只第一次慢"。Go `http.Transport`、Java `HttpClient`、Python `requests.Session` 都自带。
- **升级 TLS 1.3 + HTTP/2**：TLS 1.3 握手从 2-RTT 降到 1-RTT（支持 0-RTT 但有重放风险）；HTTP/2（`h2`）多路复用，一个连接跑所有请求，消灭队头阻塞和重复握手。服务端 Nginx `http2 on`。
- **OCSP Stapling**：服务端把证书吊销状态预先附在握手里，省掉客户端单独查 OCSP 的一轮往返（Nginx `ssl_stapling on`）。
- **预热连接**：服务启动或低峰期预先建立一批 TLS 连接放池里，高峰直接用。

### 一行本质
> **HTTPS 第一次慢 = TLS 完整握手（2 RTT + 验证 + 计算）；后面快 = 会话复用 + 连接池 + HTTP/2 多路复用，把握手成本摊薄到接近零。**

**原理对应**：TLS 握手见 RFC 8446（1.3）/ 5246（1.2）；HTTP/2 多路复用见 RFC 7540。Linux 侧 `net/ipv4/tcp_input.c`（TCP 握手为 TLS 提供可靠通道）、`tls.c`（内核 TLS 卸载 ktls）。三次握手状态机基础同 CS144 `tcp_connection.cc:91`（`connect` 发 SYN）。

---

## 附录：把它们串起来的学习路径

1. **先抓包建立直觉**（CS168 + Wireshark）：所有协议都是"线上跑的报文"，`tcpdump`/Wireshark 是网络的"显微镜"。CS168 的 Traceroute/TCP 三个 lab 让你亲手构造、发送、分析报文。
2. **手写 TCP 栈**（Stanford CS144）：本文引用的 `libsponge/tcp_connection.cc`/`tcp_sender.cc`/`byte_stream.hh` 加起来不到 500 行，却完整实现了三次握手、状态机、重传、滑动窗口。配 8 个 checkpoint，从字节流一路做到 IP 路由。
3. **对照生产内核**：CS144 是"裸"TCP，Linux 是它的工业化版——`tcp_state.cc` 的状态机对应 `net/ipv4/tcp.c` 的 `tcp_set_state`，`byte_stream.hh` 的字节流对应内核 `sk_buff` 队列。理解 CS144 后读 Linux 网络栈会有"原来如此"的通透感。
4. **用现象反向巩固**：每遇线上诡异网络问题，先 `tcpdump`/`ss`/`strace` 三件套上阵，再回头问"CS144 里这块状态机怎么走的"。这才是把网络学成肌肉记忆的方式。

> 注：本文 CS144 引用基于 `PKUFlyingPig/CS144-Computer-Network`。所有 `tcpdump`/`ss`/`curl`/`openssl`/`strace` 命令在常见 Linux 下可直接运行，抓包需 `sudo`。`ss`（socket statistics）是 `netstat` 的现代替代，更快信息更全。抓包分析推荐配合 Wireshark 打开 `.pcap`。

---

## 🎤 费曼挑战（真懂了吗？）

> 费曼法：能讲给小学生听才算真懂。用 `python3 tools/feynman.py --source network` 记录。

### 挑战 1：epoll vs select（对应 §二）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | 为什么 epoll 比 select 快？本质区别是什么？ | O(就绪数) vs O(总数) |
| L2 联系 | 你的服务用的什么 IO 模型？瓶颈在哪？ | ss -l 看连接数 |
| L3 创造 | 写一个最小的 echo server（epoll 版，C 或 Go） | 能并发 1000 连接 |
| L4 教学 | 用"前台接待 vs 每人一个服务员"比喻向小孩解释 |

### 挑战 2：CLOSE_WAIT 堆积（对应 §四）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | CLOSE_WAIT 堆积是谁的锅？ | 对端发了 FIN 但本端没调 close |
| L2 联系 | 你的服务有多少 CLOSE_WAIT？ | ss -ant | grep CLOSE_WAIT |
| L3 创造 | 写一个永远不会泄漏 CLOSE_WAIT 的 HTTP 客户端 | 正确的 defer close |
| L4 教学 | 向运维画四次挥手状态机图 | 标出 11 个状态 |

### 挑战 3：TCP 粘包（对应 §三）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | TCP 粘包是 bug 吗？为什么？ | 不是 bug，TCP 是字节流 |
| L2 联系 | 你的协议怎么定义消息边界的？ | 长度前缀/分隔符/固定长度 |
| L3 创造 | 写一个带长度前缀的消息拆包器 | 处理半包+粘包 |
| L4 教学 | 解释"TCP 不保证消息边界"对协议设计的影响 | 应用层必须自己分帧 |

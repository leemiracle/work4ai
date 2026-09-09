# Linux TCP 状态机精读：11 个状态在内核里的真实实现

> TCP 的 11 个状态不只是教科书图——它们在 Linux 内核里是真实的代码路径。
>
> 配套：[network-程序员视角 §四](../notes/network-程序员视角-从抓包到原理.md) | [tinyproxy](../projects/tinyproxy/)
> csdiy 对应：CS144 lab + network + os

---

## 一、TCP 11 状态（RFC 793）

```
                              ┌──────────┐
                    被动 OPEN │  LISTEN  │ 主动 OPEN
                    ┌────────→│          │─────────┐
                    │         └──────────┘         │
                    │              │ recv SYN      │ send SYN
                    │              ↓               ↓
                    │         ┌──────────┐    ┌──────────┐
                    │         │ SYN_RCV  │    │ SYN_SENT │
                    │         └──────────┘    └──────────┘
                    │              │               │ recv SYN+ACK
                    │   send ACK   │               │ send ACK
                    │              ↓               ↓
                    │         ┌──────────────────────────┐
                    └────────→│      ESTABLISHED         │←─────┐
                              └──────────────────────────┘      │
                                  send/recv FIN            │ recv FIN
                                      ↓                     │ send ACK
                               ┌──────────┐               │
                               │FIN_WAIT_1│               │
                               └──────────┘               │
                     recv ACK     │                        │
                      ↓           │ recv FIN+ACK           │
                               ┌──────────┐    ┌──────────┐
                               │FIN_WAIT_2│    │ CLOSING  │
                               └──────────┘    └──────────┘
                       recv FIN      │               │
                       send ACK      ↓               │
                               ┌──────────┐          │
                               │ TIME_WAIT│          │
                               └──────────┘          │
                                   2MSL               │
                                      ↓               ↓
                               ┌──────────┐    ┌──────────┐
                               │  CLOSED  │    │CLOSED_WAIT│
                               └──────────┘    └──────────┘
                                                      │ send FIN
                                                      ↓
                                               ┌──────────┐
                                               │ LAST_ACK │
                                               └──────────┘
                                                      │ recv ACK
                                                      ↓
                                               ┌──────────┐
                                               │  CLOSED  │
                                               └──────────┘
```

---

## 二、内核里的状态枚举

```c
// 参照 Linux include/net/tcp_states.h
enum {
    TCP_ESTABLISHED = 1,
    TCP_SYN_SENT,
    TCP_SYN_RECV,
    TCP_FIN_WAIT1,
    TCP_FIN_WAIT2,
    TCP_TIME_WAIT,
    TCP_CLOSE,
    TCP_CLOSE_WAIT,
    TCP_LAST_ACK,
    TCP_LISTEN,
    TCP_CLOSING,
};
```

每个 `struct sock`（内核的 socket 表示）有一个 `sk_state` 字段存当前状态。

---

## 三、状态转换的核心函数

### 3.1 连接建立（三次握手）

```
客户端                          服务端
  │                               │
  │ --- SYN, seq=x --------------→│ LISTEN
  │ SYN_SENT                      │
  │                          ←──  │ SYN+ACK, seq=y, ack=x+1
  │                               │ SYN_RECV
  │ --- ACK, ack=y+1 ------------→│
  │ ESTABLISHED                   │ ESTABLISHED
```

**服务端路径**（参照 `net/ipv4/tcp_input.c`）：

```c
// 收到 SYN（在 LISTEN 状态）
int tcp_rcv_state_process(struct sock *sk, struct sk_buff *skb) {
    switch (sk->sk_state) {
    case TCP_LISTEN:
        // 收到 SYN → 创建子 socket → 状态改 SYN_RECV
        // （三次握手第二步）
        // 详见 inet_csk_accept + tcp_v4_conn_request
        break;

    case TCP_SYN_RECV:
        // 收到 ACK → 状态改 ESTABLISHED
        // （三次握手完成）
        tcp_set_state(sk, TCP_ESTABLISHED);
        break;
    }
}
```

**客户端路径**：

```c
// 发起连接（connect 系统调用）
int tcp_v4_connect(struct sock *sk, struct sockaddr *uaddr) {
    // 发 SYN
    tcp_set_state(sk, TCP_SYN_SENT);
    tcp_send_syn(sk);
}

// 收到 SYN+ACK（在 SYN_SENT 状态）
// → tcp_rcv_state_process → 改 ESTABLISHED → 发 ACK
```

### 3.2 连接关闭（四次挥手）

```
主动关闭方                       被动关闭方
  │                               │
  │ --- FIN, seq=u --------------→│ ESTABLISHED
  │ FIN_WAIT_1                    │
  │                          ←──  │ ACK, ack=u+1
  │ FIN_WAIT_2                    │ CLOSE_WAIT
  │                               │
  │                          ←──  │ FIN, seq=v
  │ TIME_WAIT                     │ LAST_ACK
  │ --- ACK, ack=v+1 ------------→│
  │ (2MSL)                        │ CLOSED
  │ CLOSED                        │
```

**主动关闭方**（FIN_WAIT_1 → FIN_WAIT_2 → TIME_WAIT）：

```c
// 发 FIN（close 系统调用）
void tcp_close(struct sock *sk, long timeout) {
    if (sk->sk_state == TCP_ESTABLISHED) {
        tcp_set_state(sk, TCP_FIN_WAIT1);
        tcp_send_fin(sk);
    }
}

// 收到 ACK（在 FIN_WAIT_1）
// → 改 FIN_WAIT_2

// 收到 FIN（在 FIN_WAIT_2）
// → 改 TIME_WAIT → 启动 2MSL 定时器 → 发 ACK
```

**TIME_WAIT 为什么 2MSL？**
- MSL（Maximum Segment Lifetime）= 报文最大生存时间（Linux 默认 30s）
- 2MSL = 60s（Linux 默认）
- 等待时间确保最后一个 ACK 到达对方
- 如果对方没收到 ACK → 重发 FIN → 这边还能响应

csdiy 交叉：[network §四 CLOSE_WAIT](../notes/network-程序员视角-从抓包到原理.md) — CLOSE_WAIT 堆积就是被关闭方没调 close()（一直停在 CLOSE_WAIT 状态）。

### 3.3 RST（强制重置）

```c
// 收到 RST → 立即 CLOSED（不等挥手）
// 参照 tcp_reset()
static void tcp_reset(struct sock *sk) {
    tcp_set_state(sk, TCP_CLOSE);
    // 通知应用层：Connection reset by peer
    sk->sk_err = ECONNRESET;
}
```

csdiy 交叉：[network §一 RST](../notes/network-程序员视角-从抓包到原理.md) — 连接到不存在的端口 → 内核回 RST。

---

## 四、TIME_WAIT 的工程细节

### 问题

高并发短连接场景下，TIME_WAIT 堆积（每个 60s）→ 端口耗尽（~65535 个）。

### 内核参数

```bash
# TIME_WAIT 相关的内核参数
net.ipv4.tcp_tw_reuse=1          # 允许复用 TIME_WAIT 连接（客户端）
net.ipv4.tcp_tw_recycle=0        # NAT 环境下有 bug，4.12 内核已移除
net.ipv4.tcp_max_tw_buckets=262144  # 最大 TIME_WAIT 数量
net.ipv4.tcp_fin_timeout=60      # FIN_WAIT_2 超时
```

### 为什么 tcp_tw_recycle 被移除

`tcp_tw_recycle=1` 会根据对端 timestamp 快速回收 TIME_WAIT。但在 NAT 环境下（多个内网机器共享一个公网 IP），timestamp 不一致 → 误判 → 丢包。

**教训**：性能优化不能破坏正确性。（参照 csdiy perf §3 反模式）

---

## 五、csdiy 知识交叉

| 知识点 | 精读位置 | 这篇的连接 |
|--------|---------|-----------|
| CLOSE_WAIT 堆积 | network §四 | 被关闭方没 close → 停在 CLOSE_WAIT |
| RST | network §一 | 内核 tcp_reset() → 立即 CLOSED |
| 粘包 | network §三 | TCP 无消息边界 → 应用层分帧 |
| Nagle + Delayed ACK | network §五 | tcp_sendmsg 的延迟发送 |
| CS144 TCP 栈 | labs/cs144 | 你自己实现的 TCP 状态机 |
| fork-exec | os §三 | accept 后 fork → 子进程处理连接 |

### 你在 CS144 lab 里实现的状态机

```
你的 TCPSender:    SYN_SENT → ESTABLISHED → FIN_SENT
你的 TCPReceiver:  LISTEN → SYN_RECV → ESTABLISHED → CLOSE_WAIT
你的 TCPConnection: 拼装两者 + 处理 RST + linger
```

**内核实现是同一个状态机，只是用 C 写 + 更多边界处理（重传/拥塞控制/窗口）**。

---

## 六、用 ss 验证状态

```bash
# 看当前所有 TCP 连接的状态分布（参照 network 速查）
ss -ant | awk '{print $1}' | sort | uniq -c | sort -rn

# 输出示例：
#   50 ESTAB
#   10 TIME-WAIT
#    3 CLOSE-WAIT    ← 如果多 = 有连接没关
#    1 LISTEN
```

csdiy 交叉：[network §四](../notes/network-程序员视角-从抓包到原理.md) — 这个命令就是你排查 CLOSE_WAIT 的第一步。

---

## 七、一句话总结

> TCP 11 个状态不是教科书图——每个状态对应内核 `tcp_rcv_state_process()` 的一个 case 分支。
>
> 状态转换 = 收到报文 → 查表 → 改状态 → 发报文。和你在 CS144 里实现的是同一个状态机，只是内核多了重传/拥塞/窗口的工程细节。
>
> **理解了状态机，你就理解了 CLOSE_WAIT 堆积、TIME_WAIT 端口耗尽、RST 强制重置的所有根因。**

---

*配套：[network-程序员视角 §四](../notes/network-程序员视角-从抓包到原理.md) | [CS144 lab](../labs/cs144-网络-从零跑起来.md) | [tinyproxy](../projects/tinyproxy/)*

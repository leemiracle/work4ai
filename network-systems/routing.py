"""
路由协议演示 —— OSPF（域内）+ BGP（域间）
====================================================================
配合 mini_tcp.py 食用。TCP 解决"可靠传输"，路由解决"数据包怎么找到路"。

两层路由体系（互联网的骨架）：
  域内路由（IGP）—— OSPF / IS-IS / RIP
       一个自治系统(AS)内部，路由器数有限，用链路状态 + Dijkstra
  域间路由（EGP）—— BGP
       AS 之间，全球几十万路由器，用路径矢量 + 策略

核心对比：
  OSPF = "我知道全网拓扑，自己算最短路"（上帝视角，域内够用）
  BGP  = "我只知道邻居告诉我能到哪，凭策略选"（分布式，域间必需）

运行：
    python3 routing.py
依赖：仅标准库
====================================================================
"""
from __future__ import annotations
import heapq
from collections import defaultdict

def banner(t):
    print("\n" + "█" * 68)
    print(f"  {t}")
    print("█" * 68)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 0 · 路由的本质                                                      ║
# ╚══════════════════════════════════════════════════════════════════════╝

def part0_why_routing() -> None:
    banner("Part 0 · 路由的本质 —— 数据包怎么从你家到 Google？")
    print("""
  你在浏览器输入 google.com，数据包要跨越半个地球。它怎么知道走哪条路？

  答案：每一跳的路由器查【路由表】—— "目的 IP → 从哪个口转发"。

  路由表怎么来？这就是路由协议的事：
    ① 域内（你公司/学校内部）：OSPF，路由器互相交换链路状态，跑 Dijkstra
    ② 域间（跨运营商/国家）：BGP，自治系统(AS)之间交换"可达性 + 路径"

  打个比方：
    OSPF = 小区内导航（你熟悉每条小路，自己算最短）
    BGP  = 跨城导航（你只看路牌"前方北京 200km"，凭指示走）
""")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 1 · OSPF（链路状态 + Dijkstra）                                      ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
#  OSPF 三步走：
#    1. 发现邻居（Hello 协议）
#    2. 洪泛链路状态通告 LSA（"我和 R2 代价 1，和 R3 代价 2"）
#    3. 每个路由器用 LSDB（全网拓扑）跑 Dijkstra，生成最短路径树 + 路由表

# 示例拓扑：6 个路由器的网络
OSPF_TOPOLOGY = {
    "R1": {"R2": 1, "R3": 4},
    "R2": {"R1": 1, "R3": 2, "R4": 6},
    "R3": {"R1": 4, "R2": 2, "R4": 1, "R5": 5},
    "R4": {"R2": 6, "R3": 1, "R5": 1, "R6": 3},
    "R5": {"R3": 5, "R4": 1, "R6": 2},
    "R6": {"R4": 3, "R5": 2},
}


def ospf_dijkstra(topology, src):
    """OSPF 的核心：Dijkstra 算最短路径，返回 dist + next_hop（路由表）。"""
    dist = {n: float("inf") for n in topology}
    dist[src] = 0
    next_hop = {n: None for n in topology}
    next_hop[src] = src
    visited = set()
    pq = [(0, src, src)]   # (dist, node, first_hop)
    while pq:
        d, u, fh = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        next_hop[u] = fh
        for nb, w in topology[u].items():
            if nb not in visited and d + w < dist[nb]:
                dist[nb] = d + w
                # next_hop: 如果 u 是 src 本身，下一跳就是 nb；否则继承
                new_fh = nb if u == src else fh
                heapq.heappush(pq, (d + w, nb, new_fh))
    return dist, next_hop


def part1_ospf() -> None:
    banner("Part 1 · OSPF —— 链路状态 + Dijkstra（域内路由）")
    print("  拓扑（6 路由器，边上数字 = OSPF 代价）：\n")
    print("       R2 ──6── R4")
    print("      ╱ │ ╲     │ ╲")
    print("    1   2   ╲   1   3")
    print("  R1────R3────R4──R6")
    print("        4│     1│   2│")
    print("        R3─────R5───R6")
    print("  （R1-R2=1, R1-R3=4, R2-R3=2, R2-R4=6, R3-R4=1, R3-R5=5, R4-R5=1, R4-R6=3, R5-R6=2）\n")

    src = "R1"
    dist, nh = ospf_dijkstra(OSPF_TOPOLOGY, src)
    print(f"  从 {src} 跑 Dijkstra 生成的路由表：")
    print(f"    {'目的':<6} {'下一跳':<8} {'总代价':>6}")
    print("    " + "─" * 26)
    for dst in sorted(OSPF_TOPOLOGY):
        if dst == src:
            continue
        print(f"    {dst:<6} {nh[dst]:<8} {dist[dst]:>6}")
    print("""
  → 每个 OSPF 路由器都独立跑 Dijkstra，结果一致（因为 LSDB 相同）。
  → 这就是"链路状态"协议：上帝视角 + 全局最优。
  → 反直觉亮点：R1→R3 直连代价 4，但绕道 R1→R2(1)→R3(2)=3 反而更便宜！
     R1 到所有目的的下一跳都是 R2——因为 R2 是通往"优质中转枢纽"的入口。
     这就是 Dijkstra 的价值：人眼容易看错，算法不会。
""")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 2 · BGP（路径矢量 + AS_PATH）                                        ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
#  BGP 不洪泛完整拓扑（全球几十万路由器，存不下），而是传播"可达性 + 路径"：
#    "我能到 8.8.8.0/24，路径是 AS100 → AS200 → AS300"
#  收到广播的 AS：
#    ① 看 AS_PATH 里有没有自己 → 有就拒收（防环）
#    ② 没有就按策略选最优（通常 AS_PATH 最短）

# AS 拓扑：5 个自治系统
AS_TOPOLOGY = {
    "AS100": {"neighbors": ["AS200", "AS300"]},
    "AS200": {"neighbors": ["AS100", "AS400", "AS500"]},
    "AS300": {"neighbors": ["AS100", "AS400"]},
    "AS400": {"neighbors": ["AS200", "AS300", "AS500"]},
    "AS500": {"neighbors": ["AS200", "AS400"]},
}


def bgp_propagate(as_topology, origin, prefix):
    """模拟 BGP 路径矢量传播。每个 AS 收到 (prefix, path)，防环 + 选最短。"""
    # best[as] = (prefix, as_path, from_as)
    best = {}
    # 起源 AS 宣告自己的前缀
    queue = [(origin, [origin])]
    best[origin] = (prefix, [origin], None)
    while queue:
        current, path = queue.pop(0)
        for nb in as_topology[current]["neighbors"]:
            new_path = path + [nb]
            # ① 防环：AS_PATH 含自己就拒收
            if nb in path:
                continue
            # ② 选优：AS_PATH 更短才更新
            if nb not in best or len(new_path) < len(best[nb][1]):
                best[nb] = (prefix, new_path, current)
                queue.append((nb, new_path))
    return best


def part2_bgp() -> None:
    banner("Part 2 · BGP —— 路径矢量 + AS_PATH（域间路由）")
    print("  AS 拓扑（5 个自治系统）：\n")
    print("     AS100 ── AS200 ── AS500")
    print("       │    ╱    │    ╱")
    print("     AS300 ── AS400")
    print()
    origin = "AS500"
    prefix = "8.8.8.0/24"   # 假设 AS500 拥有这个网段（像 Google 的 8.8.8.8）
    print(f"  {origin} 宣告拥有 {prefix}，BGP 开始路径矢量传播...\n")

    routes = bgp_propagate(AS_TOPOLOGY, origin, prefix)
    print(f"  {'AS':<8} {'AS_PATH（经过路径）':<30} {'从谁学到':<10}")
    print("  " + "─" * 52)
    for asn in sorted(routes):
        pfx, path, learned_from = routes[asn]
        path_str = " → ".join(path)
        src = learned_from or "(本地)"
        print(f"  {asn:<8} {path_str:<30} {src:<10}")
    print(f"""
  → 每个 AS 只知道"完整路径"，不需要全网拓扑（可扩展到全球规模）。
  → AS_PATH 还能防环：AS300 收到含 AS300 的路径会直接丢弃。
  → AS100 到 8.8.8.0/24 的路径：AS100→AS200→AS500（2 跳，最短）。
""")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 3 · OSPF vs BGP 对比                                                 ║
# ╚══════════════════════════════════════════════════════════════════════╝

def part3_compare() -> None:
    banner("Part 3 · OSPF vs BGP —— 两种路由哲学")
    rows = [
        ("算法",     "链路状态 + Dijkstra", "路径矢量"),
        ("范围",     "域内（IGP）",          "域间（EGP）"),
        ("视角",     "上帝视角（知全网拓扑）", "局部视角（知邻居说的）"),
        ("度量",     "代价（带宽/延迟）",     "策略（AS_PATH/LOCAL_PREF）"),
        ("规模",     "中等（几百路由器）",     "全球（几十万路由器）"),
        ("收敛",     "快（秒级）",            "慢（分钟级，策略复杂）"),
        ("选路标准",  "纯最短路",             "策略优先（可能不走最短）"),
        ("防环",     "Dijkstra 天然无环",     "AS_PATH 检查"),
    ]
    print(f"  {'维度':<12} {'OSPF':<26} {'BGP'}")
    print("  " + "─" * 60)
    for dim, ospf, bgp in rows:
        print(f"  {dim:<12} {ospf:<26} {bgp}")
    print("""
  → 为什么 BGP 不用 Dijkstra？全球太大，洪泛链路状态会让路由器爆炸。
     路径矢量只传"能到哪 + 经过谁"，信息量小得多，才撑得起互联网规模。
  → 为什么 OSPF 不用 BGP？域内要快、要最优，Dijkstra 秒级收敛，BPG 太慢。
""")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Part 4 · 你的数据包怎么到 Google                                          ║
# ╚══════════════════════════════════════════════════════════════════════╝

def part4_real_world() -> None:
    banner("Part 4 · 实战全景 —— 你 ping 8.8.8.8 时发生了什么？")
    print("""  你在家用 WiFi ping 8.8.8.8（Google DNS），数据包的旅程：

  [你的电脑]
    ↓ 查本机路由表：默认路由 → 家里路由器(192.168.1.1)
  [家里路由器]
    ↓ NAT 转换 → 查路由表 → 默认路由 → 运营商接入路由器
  [运营商 AS（如 AS4134 中国电信）]      ← 域内：OSPF
    ↓ 内部用 OSPF 路由到出口边界路由器
  [边界路由器]                            ← 域间：BGP
    ↓ 查 BGP 路由表：8.8.8.0/24 → AS_PATH 最短是 AS15169（Google）
    ↓ 转发给上游 ISP 或直连 Google 的对等点
  [经过若干 AS 的 BGP 跳]
    ↓ 每个 AS 边界路由器查 BGP 表，转发给 AS_PATH 上的下一个 AS
  [AS15169 Google]                       ← 域内：OSPF/IS-IS
    ↓ 进入 Google 内部网络，OSPF/IS-IS 路由到 8.8.8.8 所在机器
  [8.8.8.8 收到 ICMP，回包原路返回]

  → 两层路由协作：BGP 决定"去哪个 AS"，OSPF 决定"AS 内部怎么走"。
  → traceroute 能看到每一跳：先经过你家→运营商内部(OSPF)→边界→跨网(BGP)→Google内部。
  → 互联网本质 = BGP 把几万个 AS 粘起来的"网络的网络"。
""")


def main() -> None:
    print()
    print("╔" + "═" * 66 + "╗")
    print("║" + " 路由协议 · OSPF × BGP · 帮你理解数据包的旅程 ".center(66) + "║")
    print("╚" + "═" * 66 + "╝")
    part0_why_routing()
    part1_ospf()
    part2_bgp()
    part3_compare()
    part4_real_world()
    print("=" * 68)
    print("  ✅ 全部演示完成。下一步：")
    print("     1. 对照 TCP 部分：python3 mini_tcp.py")
    print("     2. 自己画个拓扑，改 OSPF_TOPOLOGY 的代价，观察路由表变化")
    print("     3. traceroute 8.8.8.8，亲眼看看 OSPF + BGP 的每一跳")
    print("=" * 68)
    print()


if __name__ == "__main__":
    main()

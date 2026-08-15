"""管理学 - 运营优化与组织网络分析验证"""
import numpy as np
import pulp
import networkx as nx

print("=" * 60)
print("1. 线性规划 LP (产品组合)")
print("=" * 60)
prob = pulp.LpProblem("product_mix", pulp.LpMaximize)
x = pulp.LpVariable("产品A", lowBound=0)
y = pulp.LpVariable("产品B", lowBound=0)
prob += 30 * x + 50 * y            # 利润
prob += 2 * x + 4 * y <= 100        # 工时约束
prob += 3 * x + 1 * y <= 80         # 材料约束
prob.solve(pulp.PULP_CBC_CMD(msg=0))
print(f"  A = {pulp.value(x):.2f}, B = {pulp.value(y):.2f}")
print(f"  最大利润 = {pulp.value(prob.objective):.2f}")

print("\n" + "=" * 60)
print("2. 关键路径法 CPM (项目调度)")
print("=" * 60)
# 活动: (时长, 前置)
tasks = {
    "A": (3, []),
    "B": (2, ["A"]),
    "C": (4, ["A"]),
    "D": (1, ["B"]),
    "E": (5, ["C"]),
    "F": (2, ["D", "E"]),
}
order, seen = [], set()
def visit(n):
    if n in seen:
        return
    for p in tasks[n][1]:
        visit(p)
    seen.add(n); order.append(n)
for n in tasks:
    visit(n)
es, ef, ls, lf = {}, {}, {}, {}
for n in order:
    dur = tasks[n][0]
    es[n] = max([ef[p] for p in tasks[n][1]] + [0])
    ef[n] = es[n] + dur
proj = max(ef.values())
for n in reversed(order):
    dur = tasks[n][0]
    succs = [m for m in tasks if n in tasks[m][1]]
    lf[n] = min([ls[m] for m in succs] + [proj])
    ls[n] = lf[n] - dur
slack = {n: ls[n] - es[n] for n in tasks}
critical = [n for n in order if slack[n] == 0]
print(f"  总工期 = {proj}")
print(f"  关键路径 = {' -> '.join(critical)}")
print(f"  各活动松弛: {slack}")

print("\n" + "=" * 60)
print("3. 经济订货量 EOQ (库存)")
print("=" * 60)
D, S, H = 10000, 50, 2  # 年需求, 每次订货成本, 单位年持有成本
Q = np.sqrt(2 * D * S / H)
print(f"  D={D}, S={S}, H={H} -> EOQ = {Q:.1f} 件, 年订货 {D/Q:.1f} 次")

print("\n" + "=" * 60)
print("4. 排队论 M/M/1 (服务系统)")
print("=" * 60)
lam, mu = 8, 10  # 到达率, 服务率
rho = lam / mu
L = rho / (1 - rho)       # 系统平均人数
Lq = rho ** 2 / (1 - rho) # 队列平均等待数
W = 1 / (mu - lam)         # 系统平均逗留
Wq = rho / (mu * (1 - rho))
print(f"  λ={lam}, μ={mu}, ρ={rho}")
print(f"  L={L:.2f}, Lq={Lq:.2f}, W={W:.3f}, Wq={Wq:.3f}")

print("\n" + "=" * 60)
print("5. 组织网络分析 ONA (Zachary 空手道俱乐部)")
print("=" * 60)
G = nx.karate_club_graph()
deg = nx.degree_centrality(G)
btw = nx.betweenness_centrality(G)
eig = nx.eigenvector_centrality(G, max_iter=1000)
clo = nx.closeness_centrality(G)
print(f"  节点数={G.number_of_nodes()}, 边数={G.number_of_edges()}")
print(f"  度中心性最高: 节点 {max(deg, key=deg.get)} = {max(deg.values()):.3f}")
print(f"  介数中心性最高: 节点 {max(btw, key=btw.get)} = {max(btw.values()):.3f}")
print(f"  特征向量中心性最高: 节点 {max(eig, key=eig.get)} = {max(eig.values()):.3f}")
print(f"  (节点0=俱乐部管理员, 节点33=教练, 二者均为关键意见领袖)")
comms = nx.community.greedy_modularity_communities(G)
print(f"  贪婪模块度社区检测: {len(comms)} 个社区, 大小 {[len(c) for c in comms]}")

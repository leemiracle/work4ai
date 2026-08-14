# CS309A: Cloud Computing

> Stanford University, Autumn 2026
> 领域: 分布式系统 / 云计算
> Prerequisites: CS110（系统基础）或同等经验
> Units: 3-4
> Difficulty: ⭐⭐⭐⭐

---

## 📚 定位

深入云原生系统——从 CAP 定理到微服务，理解支撑现代互联网的分布式基础设施。

---

## 🎯 学习目标

- 理解分布式系统核心理论（CAP、一致性模型）
- 掌握负载均衡与容错策略
- 理解云服务模型与架构模式
- 能设计可扩展的分布式系统

---

## 📅 核心模块

### Module 1: 分布式系统基础
- CAP 定理（Consistency / Availability / Partition tolerance）
- BASE vs ACID
- 一致性模型（强 / 最终 / 因果）
- 分布式共识（Paxos / Raft）

### Module 2: 负载均衡
- 算法：Round Robin / Least Connections / Consistent Hashing
- L4 vs L7 负载均衡
- 全球负载均衡（Geo-DNS）

### Module 3: 存储与数据库
- NoSQL 类型（Key-Value / Document / Column / Graph）
- 分片（Sharding）与复制（Replication）
- NewSQL（Spanner / CockroachDB）
- 缓存层（Redis / Memcached）

### Module 4: 微服务
- 单体 vs 微服务
- 服务发现与注册
- API 网关
- 服务网格（Istio / Linkerd）

### Module 5: 云原生与 DevOps
- 容器编排（Kubernetes）
- Serverless / FaaS
- 基础设施即代码（Terraform）
- 可观测性与 SRE

---

## 💻 项目代码

📁 `supplementary/undergrad_projects.py::cs309a_demo`

**实现内容**:
1. ✅ CAP 定理完整阐述（CP vs AP 权衡）
2. ✅ Round Robin 负载均衡模拟（100 请求 / 3 服务器）
3. ✅ 请求分布可视化

**运行**:
```bash
cd supplementary
python3 undergrad_projects.py
```

**输出示例**:
```
CAP 定理:
  - C (Consistency): 所有节点看到同样数据
  - A (Availability): 总能收到响应
  - P (Partition tolerance): 网络分区时继续工作
  → 只能选 2 个（分布式系统必须 P，所以是 CP vs AP）

Round Robin 负载均衡 (100 请求):
  Server 0: 34 请求
  Server 1: 33 请求
  Server 2: 33 请求
```

---

## 📊 关键概念

| 概念 | 说明 |
|------|------|
| **CAP 定理** | 分布式系统三选二 |
| **Raft / Paxos** | 分布式共识算法 |
| **Consistent Hashing** | 最小迁移的负载分配 |
| **微服务** | 单一职责的服务拆分 |
| **Kubernetes** | 容器编排事实标准 |

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **后端工程师** | 分布式系统核心知识 |
| **DevOps / SRE** | 云原生基础设施 |
| **系统架构师** | 可扩展性设计 |
| **CS110 后进阶** | 从单机到分布式 |

---

## 🚀 扩展方向

1. 阅读 *Designing Data-Intensive Applications* (Kleppmann)
2. 阅读 *Database Internals* (Petrov)
3. 实战：在 AWS/GCP 部署微服务
4. 探索 CS240（操作系统）深化底层

---

**对应代码**: `supplementary/undergrad_projects.py::cs309a_demo`

# CS350S: Privacy-Preserving Systems

> Stanford University, Fall 2025
> Instructor: **Emma Dauterman**（前 UC Berkeley，Alibi/TAP/Sieve 系统作者）
> Course Assistant: Teddy Zhang
> Time: 周二/周四 3:00–4:20 PM, 200-303
> Office Hours: 周二 4:30–5:30 PM, CoDa W340
> Prerequisites: **CS155**（计算机与网络安全）或同等
> Difficulty: ⭐⭐⭐⭐⭐（密码学 + 系统设计双重门槛）
> 官网: http://cs350s.stanford.edu/

---

## 📚 课程定位

CS350S 探索**使用密码学提供强隐私保证的系统**。它不是一门纯密码学理论课，也不是一门纯系统课——而是两者的交汇：

> **核心问题**：如何让系统在**不泄露用户数据**的前提下，仍然提供有用的功能？

学生将学习现代密码学工具（ORAM、PIR、MPC、DP）和系统技术（调度、缓存、网络），并研究它们如何在真实的隐私保护系统中协同工作以最小化开销。

### 讲师背景
**Emma Dauterman** 从 UC Berkeley 加入 Stanford，她的博士工作代表了隐私保护系统的前沿：
- **TAP**——基于纯客户端 Tor 替代方案（Tor + 分层加密），获 NSDI '25
- **Alibi**——用于交互式应用的匿名计算
- **Sieve**——隐私保护的数据管理系统

> 她的研究理念：**密码学不是障碍，而是系统设计的构建块**。

### 灵感来源
课程受多所高校同类课程启发：Berkeley CS294-163、MIT 6.893/6.5660、UCLA CS239、CMU 15-793、Brown CSCI2390、UNC COMP790-188。

---

## 🎯 学习目标

完成 CS350S 后，学生应能够：

1. **理解** 现代隐私保护密码学原语（透明日志、ORAM、PIR、MPC、DP、FL）
2. **分析** 真实隐私系统的设计权衡（安全性 vs 性能 vs 功能性）
3. **实现** 一个完整的隐私保护系统（从提案到评估）
4. **评估** 系统的安全属性（形式化威胁模型 + 实证性能测试）
5. **阅读** 系统安全顶会论文（IEEE S&P、USENIX Security、OSDI、SOSP）
6. **展示** 研究论文（15 分钟学术报告 + 问答）

---

## 📅 完整模块（Fall 2025 完整日程）

### Part 1: 基础
| 日期 | 主题 | 必读论文 |
|------|------|---------|
| 9/23 | 课程导论 | — |
| 9/25 | **密码学基础** | "How to Read a Paper" |
| 9/30 | **透明日志 I** ⭐ | Certificate Transparency (Google Chrome) |
| 10/2 | 透明日志 II（嘉宾: Kevin Lewi）| CONIKS（可审计的端到端加密）|

### Part 2: 安全硬件与 ORAM
| 日期 | 主题 | 必读论文 |
|------|------|---------|
| 10/7 | **安全硬件**（SGX/TDX/SEV）| VC3（SGX 上的 MapReduce）|
| 10/9 | **ORAM I** ⭐ | Goldreich-Ostrovsky '96（ORAM 理论基础）|
| 10/14 | ORAM II | Obladi（并发 ORAM 数据库，OSDI '18）|

### Part 3: 私有信息检索
| 日期 | 主题 | 必读论文 |
|------|------|---------|
| 10/16 | **PIR I** + **项目提案截止** | CGKS '95（PIR 开山论文）|
| 10/21 | PIR II | Splinter（NSDI '17，私有检索）|
| 10/23 | PIR III | Tiptoe（eprint 2023，亚线性 PIR）|

### Part 4: 匿名通信
| 日期 | 主题 | 必读论文 |
|------|------|---------|
| 10/28 | **匿名消息 I** | Tor（洋葱路由原论文）|
| 10/30 | 匿名消息 II | Riposte（混合匿名广播）|

### Part 5: 多方安全计算与隐私统计
| 日期 | 主题 | 必读论文 |
|------|------|---------|
| 11/6 | **MPC I**（嘉宾: Riana Pfefferkorn）| Signal Usernames + Pragmatic MPC Book |
| 11/11 | MPC II + **进展报告截止** | MAGE（OSDI '21，MPC GPU 加速）|
| 11/13 | **私有聚合统计**（嘉宾: Tim Geoghegan & Chris Patton）| Prio（隐私遥测）|
| 11/18 | **差分隐私** ⭐ | Dwork-Roth Book Ch.1-2 |
| 11/20 | **联邦学习** ⭐ | Google FL Blog + Flamingo（S&P '23）|

### Part 6: 项目展示
| 日期 | 活动 |
|------|------|
| 12/2 | 学生展示 I + **最终报告截止** |
| 12/4 | 学生展示 II |

---

## 🧮 核心算法与原语

### 1. 透明日志（Transparency Logs）
**目标**：让所有用户可验证数据未被篡改/删除。

**机制**：Merkle Tree + Append-Only Log + Gossip 协议
- 每个 append 操作产生新根哈希
- 用户通过 ** inclusion proof** 验证条目存在
- 通过 **consistency proof** 验证日志只追加不删除

**应用**：Certificate Transparency（Chrome 验证 HTTPS 证书）、WhatsApp Key Transparency

### 2. Oblivious RAM（ORAM）
**问题**：即使数据加密，访问模式（访问了哪个地址）也会泄露信息。

**核心思想**：让访问模式**与实际请求无关**——每次读一个数据，实际访问多个位置。

**Path ORAM**（最实用方案）：
- 将存储组织为树
- 每次 access 沿一条路径读写
- 读取后重新随机分配位置（reshuffle）

**复杂度**：$O(\log N)$ 带宽开销（N 为存储条目数）

### 3. Private Information Retrieval（PIR）
**目标**：用户从服务器检索第 $i$ 条记录，服务器**不知道 $i$**。

**信息论 PIR**（CGKS '95）：需 $k$ 个不通信的服务器，$O(n/k)$ 通信量
**计算论 PIR**：单服务器，利用同态加密，$O(\sqrt{n})$ 通信量
**双高效 PIR**：预处理后在线查询亚线性

### 4. 多方安全计算（MPC）
**目标**：多方联合计算函数 $f(x_1, \dots, x_n)$，不泄露各自的 $x_i$。

**核心协议**：
- **Yao 的混淆电路**（Garbled Circuits）——两方，布尔电路
- **GMW 协议**——多方，秘密共享
- **秘密共享**（Secret Sharing）——Shamir's $(k,n)$ 方案

### 5. 差分隐私（Differential Privacy）
**定义**：$(\epsilon, \delta)$-DP
$$P[\mathcal{M}(D) \in S] \leq e^\epsilon P[\mathcal{M}(D') \in S] + \delta$$

即：数据集 $D$ 与 $D'$（差一条记录）的输出分布几乎不可区分。

**机制**：
- **Laplace 机制**：$\tilde{f} = f(D) + \text{Laplace}(0, \Delta f / \epsilon)$
- **Exponential 机制**：按效用函数的概率分布采样

### 6. 联邦学习（Federated Learning）⭐
**目标**：模型训练时**数据不离开设备**。

**FedAvg 算法**：
1. 服务器将全局模型 $w_t$ 下发到各客户端
2. 各客户端在本地数据上训练：$w_{t+1}^k = w_t - \eta \nabla L_k(w_t)$
3. 服务器**加权平均**：$w_{t+1} = \sum_k \frac{n_k}{N} w_{t+1}^k$

> **注意**：FL 本身不提供完整隐私保护——梯度仍可能泄露信息。需结合 DP 或安全聚合（Secure Aggregation）。

---

## 💻 项目代码（本仓库）

📁 `topic8-med/medical_rag.py::FederatedHospital`

该文件实现了**联邦学习的核心机制**，对应 CS350S 11/20 的联邦学习模块：

**实现内容**：
1. ✅ **FederatedHospital 类**——模拟医院作为联邦学习的参与方
2. ✅ **local_train()**——本地训练，数据不出医院
3. ✅ **federated_averaging()**——FedAvg 加权平均聚合
4. ✅ **隐私对比实验**——本地模型 vs 联邦全局模型准确率

```bash
cd topic8-med
python3 medical_rag.py
```

**输出示例**:
```
📋 3. 联邦学习（FedAvg）
   Hospital A (Stanford): 67 样本
   Hospital B (UCSF): 67 样本
   Hospital C (Mayo): 66 样本
   Hospital A (Stanford) 本地准确率: 88.9%
   Hospital B (UCSF) 本地准确率: 84.4%
   Hospital C (Mayo) 本地准确率: 86.7%
   FedAvg 全局模型准确率: 91.1%
   ✓ 数据从未离开医院，但模型可以学到所有医院的信息
```

> 💡 这个 demo 展示了 FL 的核心价值：**协作训练的模型优于任何单医院模型，同时数据不离开本地**。这正是 CS350S 在医疗隐私场景下的核心应用。

---

## 📊 关键论文清单（课程完整阅读列表）

### 🔴 透明日志
1. **Laurie et al.** "Certificate Transparency: Public, Verifiable, Append-Only Logs" (ACM Queue)
2. **Melara et al. 2015** "CONIKS: Bringing Key Transparency to End Users" (USENIX Security)

### 🔴 ORAM
3. **Goldreich & Ostrovsky 1996** "Software Protection and Simulation on Oblivious RAMs"
4. **Stefanov et al. 2018** "Path ORAM" (JACM)
5. **Crooks et al. 2018** "Obladi: Oblivious RAM with Data Independence" (OSDI)

### 🔴 PIR
6. **Chor et al. 1995** "Private Information Retrieval"（PIR 开山）
7. **Wang et al. 2017** "Splinter: Practical Private Queries" (NSDI)
8. **Dauterman et al. 2023** "Tiptoe" (eprint)——讲师相关工作

### 🔴 MPC & DP & FL
9. **Prio Team 2017** "Prio: Private, Robust, and Scalable Computation of Aggregate Statistics" 
10. **Dwork & Roth 2014** "The Algorithmic Foundations of Differential Privacy"
11. **Boneh et al. 2023** "Flamingo: Multi-Party Training" (S&P)

---

## 🎯 学习路径建议

| 角色 | 推荐路径 |
|------|---------|
| **想做隐私系统研究** | CS155（安全基础）→ CS350S → OSDI/S&P 论文 |
| **想做 Web3/隐私计算** | CS350S + CS255（密码学）→ 零知识证明 |
| **想做医疗 AI 隐私** | CS350S（FL/DP）+ CS286（医疗 CV）|
| **想做安全工程** | CS155 + CS350S → 工业界安全团队 |

### 成绩构成
| 项目 | 占比 |
|------|------|
| 课堂参与 | 10% |
| 阅读回应（Reading Responses）| 15% |
| 论文展示（15 分钟）| 20% |
| 项目提案 | 5% |
| 项目进展报告 | 5% |
| 项目展示 | 20% |
| **最终项目报告** | **25%** |

> 课程高度研讨化——每周读论文 + 回应问题，最终构建一个隐私保护系统（5-6 页报告 + 代码）。

---

## 💡 反思

### 课程优势
1. **讲师一线研究**——Dauterman 自己就是 TAP/Alibi/Sieve 的作者，内容前沿
2. **系统视角独特**——不只教密码学理论，更教**如何把密码学做成高效系统**
3. **完整阅读列表**——每周精读经典论文，训练学术阅读能力
4. **项目导向**——最终项目要求完整实现+评估，培养系统构建能力
5. **嘉宾阵容强**——Kevin Lewi、Riana Pfefferkorn、Prio 团队等业界专家

### 潜在挑战
1. **先修门槛高**——CS155（密码学+安全）是硬性要求
2. **数学密集**——DP/ORAM 的理论分析需要扎实的概率论基础
3. **系统实现难**——项目需要真实实现，调试密码学代码极具挑战
4. **性能开销现实**——许多技术在实践中开销巨大，工业部署有限

---

## 🚀 扩展阅读

完成 CS350S 后推荐：
1. **CS255** — 密码学基础（更深入的理论）
2. **CS155** — 计算机与网络安全（如果未修过）
3. Dauterman 的论文：**TAP**（NSDI '25）、**Alibi**（S&P '24）
4. **Concrete ML / TFHE-rs**——全同态加密的工程实现
5. **OpenMined / PySyft**——开源隐私保护 ML 框架
6. **Signal 的安全协议文档**——真实世界隐私工程的标杆

---

**最后更新**: 2026-08-11
**对应代码**: `topic8-med/medical_rag.py::FederatedHospital`（联邦学习模拟）
**数据来源**: cs350s.stanford.edu（overview + schedule + assignments 完整抓取）

# CS258: Quantum Cryptography

> Stanford University | 研究生 | 量子密码学专题
> Instructor: **Mark Zhandry**（量子密码学 / 格密码学权威）
> 先修: CS255（密码学）或同等基础 + 线性代数 + 基础量子力学概念
> 难度: ⭐⭐⭐⭐⭐（密码学 + 量子计算交叉，数学门槛极高）
> 定位: BB84 / QKD / 量子签名，探索"后量子"与"量子增强"安全

---

## 📚 课程定位

CS258 是 Stanford **量子密码学专题课**，由 **Mark Zhandry** 教授主讲。Zhandry 在量子密码学与格密码学领域享有盛誉，研究量子计算对经典密码的威胁以及量子力学如何**增强**密码学（信息论级安全）。课程探讨两大方向：**量子计算如何破坏经典密码**（后量子密码）与**量子力学如何赋能新密码原语**（QKD / 量子签名）。

### Mark Zhandry 教授
- 密码学家，研究方向：量子密码学、格密码、不可区分混淆
- 代表作：量子 Oracle 模型、格基加密、量子随机预言机模型
- 现兼任 NTU（新加坡），与 Stanford 密码学组（Boneh 团队）深度合作

> 与 CS251（Blockchain / Boneh）共享 `topic10-theory/rsa_crypto.py`，其中 RSA / Diffie-Hellman 是理解"量子威胁"的基础。

---

## 🎯 学习目标

1. 理解**量子计算基础**（qubit / 叠加 / 纠缠 / 测量）
2. 掌握 **Shor 算法**为何能破解 RSA / ECC
3. 学习 **BB84 协议**（量子密钥分发，信息论级安全）
4. 理解**后量子密码**（PQC）的设计与标准化
5. 探索量子签名、量子货币、量子零知识证明等前沿原语

---

## 📅 核心模块

### Part 1: 量子计算基础
- Qubit 与 Bloch 球
- 量子门（Hadamard / CNOT / Pauli）
- 叠加（superposition）与纠缠（entanglement）
- 量子测量与不可克隆定理（No-Cloning Theorem）

### Part 2: 量子计算对经典密码的威胁
- **Shor 算法**：多项式时间分解大整数 / 离散对数 → RSA / ECC 崩溃
- **Grover 算法**：平方根加速搜索 → 对称密钥强度减半
- 量子随机预言机模型（QROM）

### Part 3: 量子密钥分发（QKD）
- **BB84 协议**（Bennett & Brassard 1984）：信息论级安全的密钥协商
- 测量基选择 + 误码率检测 + 隐私放大
- E91 协议（基于纠缠）
- QKD 的工程现实（光纤损耗 / 设备缺陷 / 侧信道）

### Part 4: 后量子密码（PQC）
- 格密码（Lattice）：Kyber（KEM）/ Dilithium（签名）— NIST 标准
- 哈希签名 / 多变量密码 / 码基密码
- NIST PQC 标准化进程

### Part 5: 量子增强密码原语
- 量子签名 / 量子货币（Wiesner 量子货币 / 公钥量子货币）
- 量子零知识证明 / 量子安全多方计算

---

## 💻 项目代码

📁 `topic10-theory/rsa_crypto.py`（与 CS251 共享）

CS258 的核心是理解"经典密码在量子计算下的脆弱性"，共享代码实现：
1. ✅ **RSA 从零实现**（理解 Shor 算法的攻击目标）
2. ✅ **Diffie-Hellman 密钥交换**（理解经典 KEX vs QKD）
3. ✅ **数字签名 / 区块链**（理解后量子签名需求）

### 运行
```bash
cd topic10-theory
python3 rsa_crypto.py
```

> **关键对比**：DH 依赖离散对数难题（Shor 可破），而 **BB84 QKD** 依靠物理定律保证安全——这正是 CS258 的核心张力。

---

## 📊 关键概念/论文

### 🔴 必读 P0
1. **Bennett & Brassard 1984** "BB84"（QKD 开山）+ **Wiesner 1983** "Conjugate Coding"（量子货币）
2. **Shor 1994**（RSA 终结者）+ **Grover 1996**（搜索平方根加速）

### 🟡 P1
3. **NIST PQC Standards**（FIPS 203/204/205: ML-KEM / ML-DSA / SLH-DSA）
4. **Nielsen & Chuang** "Quantum Computation and Quantum Information"（量子计算圣经）
5. Boneh-Shoup *Applied Cryptography* 后量子章节 + **Zhandry** 量子 Oracle 模型系列

### 核心概念
- **不可克隆定理**：无法完美复制未知量子态 → QKD 安全根基
- **BB84 安全性**：窃听必然引入误码，可被检测
- **Shor vs Grover**：指数加速（破 RSA）vs 平方根加速（弱化 AES）

---

## 🎯 适用人群

- **密码学研究员**: CS258 → 博士论文方向（PQC / 量子协议）
- **后量子工程师**: 部署 NIST PQC 标准（Kyber / Dilithium）
- **量子计算研究**: CS258 + 量子算法（理解密码学应用）
- **区块链 / Web3**: 抗量子区块链（BIP-360 等）

---

## 🚀 扩展

完成后推荐：
1. **CS255** — Introduction to Cryptography（经典密码学理论基础）
2. **CS251** — Blockchain Technologies（区块链密码学应用）
3. **PHYS221** / 量子计算课程（量子算法深度）
4. NIST PQC 文档 + liboqs 库 + IACR ePrint 量子密码板块

---

**对应代码**: `topic10-theory/rsa_crypto.py`（与 CS251 共享）

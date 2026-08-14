# CS251: Blockchain Technologies (Cryptocurrencies and Blockchain)

> Stanford University, Fall 2025
> Instructor: **Dan Boneh**（密码学大师，ACM Fellow，RSA 发明者之一）
> 时间: Mon/Wed 3:00-4:20pm, Gates B03
> Section: Friday 1:30-2:20pm
> 难度: ⭐⭐⭐⭐⭐（密码学 + 分布式系统 + 经济学交叉）
> 官网: https://cs251.stanford.edu/

---

## 📚 课程定位

**全球区块链教育的标杆课程**，由密码学领域最负盛名的学者之一 **Dan Boneh** 教授主讲。课程以 **Bitcoin** 和 **Ethereum** 为案例，系统覆盖区块链技术的全栈知识：从密码学基础到分布式共识，从智能合约到 DeFi 经济学，从隐私保护到扩展方案。

### Dan Boneh 教授

Boneh 是 **现代密码学的奠基人之一**：
- **学术地位**: Stanford CS 教授，ACM Fellow，IACR Fellow
- **代表性贡献**:
  - 🔴 **Boneh-Franklin IBE**（2001）—— 基于身份的加密（Identity-Based Encryption）
  - 🔴 **BLS 签名**（Boneh-Lynn-Shacham, 2001）—— 短签名方案，Ethereum ETH2 使用
  - 🔴 **Weil Pairing 在密码学中的应用** —— 双线性映射密码学
  - 🔴 **同态加密基础理论**
- **教材**: *Graduate Course in Applied Cryptography*（与 Victor Shoup 合著，免费在线）
- **教学风格**: 数学严谨 + 工程务实，将复杂密码学原语讲得清晰透彻

> 课程曾用名 "Bitcoin and Cryptocurrencies"，2023 年起更名 "Blockchain Technologies"，反映内容从单一比特币扩展到完整区块链生态。

---

## 🎯 学习目标

完成本课程后，学生应能：

1. **理解** 密码学原语：哈希函数、数字签名、Merkle 树、零知识证明
2. **掌握** Bitcoin 工作原理：UTXO 模型、PoW 共识、P2P 网络、交易脚本
3. **掌握** Ethereum 工作原理：EVM、智能合约（Solidity）、Gas 机制
4. **分析** 分布式共识协议：经典 BFT、Nakamoto Consensus、PoS
5. **理解** DeFi 生态：稳定币、借贷协议、DEX（去中心化交易所）、MEV
6. **评估** 区块链扩展方案：Layer 2（Rollups / State Channels）、闪电网络
7. **分析** 隐私技术：混币、zk-SNARKs、机密交易
8. **批判** 区块链技术的法律、伦理和社会影响

---

## 📅 完整模块（20 讲 + 4 项目 + 4 作业）

### 第一部分：密码学与 Bitcoin 机制（L1-L3）

- **L1 (Sep 22)** — Intro to Cryptography & Cryptocurrencies
  - 密码学基础：哈希函数（SHA-256）、数字签名（ECDSA/Schnorr）
  - Merkle 树：高效数据完整性验证
  - 🔴 *What is a Merkle Tree?*（decentralizedthoughts.github.io）
  - *Project 1 发布: Merkle Trees in Python*

- **L2 (Sep 24)** — Bitcoin Nuts and Bolts
  - Bitcoin 白皮书逐节精读
  - 区块结构、交易结构、P2P 网络协议
  - UTXO（Unspent Transaction Output）模型
  - 🔴 **Satoshi Nakamoto** — *Bitcoin: A Peer-to-Peer Electronic Cash System*（2008）
  - 🔴 Bitcoin Developer Guide: Block Chain / Transactions / P2P Network

- **L3 (Sep 29)** — Wallets: Managing and Protecting Crypto Assets
  - HD 钱包（Hierarchical Deterministic Wallets, BIP-32/44）
  - 助记词（BIP-39）、密钥管理、冷钱包 vs 热钱包
  - 🔴 Bitcoin Developer Guide: Wallets

**核心概念**: Hash Function、Digital Signature、Merkle Tree、UTXO Model、HD Wallet

### 第二部分：共识协议（L4-L6）

- **L4 (Oct 1)** — Classical Consensus: Network Models and SMR
  - 分布式系统基础：同步 / 异步 / 部分同步模型
  - 状态机复制（State Machine Replication, SMR）
  - 安全性（Safety）vs 活性（Liveness）
  - Dolev-Strong 广播协议
  - 🔴 *Foundations of Distributed Consensus and Blockchains*（Elaine Shi, pp. 9-63）
  - 🔴 decentralizedthoughts 博客系列: *What is Consensus?* / *Synchrony Models* / *The Threshold Adversary*

- **L5 (Oct 6)** — Consensus in the Internet Setting: Nakamoto Consensus
  - 互联网环境挑战：动态可用性（Dynamic Availability）
  - Nakamoto Consensus = PoW + 最长链规则
  - 女巫攻击（Sybil Attack）与 PoW 抗女巫性
  - 🔴 *Security Proof for Nakamoto Consensus*（decentralizedthoughts）
  - 🔴 *Bitcoin's Latency-Security Analysis Made Simple*（arXiv 2022, Section 4）
  - 🔴 *Flash Boys 2.0*（arXiv, Section 7）— MEV 开山论文

- **L6 (Oct 8)** — Accountability and Incentives: Proof-of-Stake
  - PoS 共识：从 PoW 到 PoS 的转变
  - 问责制（Accountability）与最终性（Finality）
  - Nothing-at-Stake 问题、Long Range Attack
  - 自私挖矿（Selfish Mining）
  - 可用性-最终性困境（Availability-Finality Dilemma）
  - 🔴 *Foundations of Consensus* (pp. 107-110)
  - 🔴 *BFT Protocol Forensics*（arXiv 2020）
  - 🔴 *Ebb-and-Flow Protocols: Resolution of the Availability-Finality Dilemma*（arXiv 2020）

**核心概念**: Byzantine Fault Tolerance、Nakamoto Consensus、Sybil Resistance、PoW vs PoS、Safety vs Liveness

### 第三部分：Ethereum 与智能合约（L7-L8）

- **L7 (Oct 13)** — Ethereum: EVM and Decentralized Apps
  - Ethereum 架构：Account Model vs UTXO Model
  - EVM（Ethereum Virtual Machine）指令集
  - Gas 机制：计算资源定价
  - 🔴 Ethereum Documentation / EVM Opcodes (evm.codes)
  - 🔴 *Ethereum Yellow Paper*（Gavin Wood）

- **L8 (Oct 15)** — Programming in Solidity
  - Solidity 语法与智能合约编程
  - 常见漏洞：Reentrancy（DAO 黑客事件）、Integer Overflow
  - 🔴 Solidity Documentation

**核心概念**: EVM、Gas、Account Model、Smart Contract、Solidity、Reentrancy Attack

### 第四部分：DeFi 与经济学（L9-L11）

- **L9 (Oct 20)** — Stablecoins and Lending Protocols
  - 稳定币类型：法币抵押（USDT/USDC）、加密抵押（DAI）、算法稳定币（UST）
  - 借贷协议：Compound / Aave 的利率模型
  - 闪电贷（Flash Loans）攻击
  - 🔴 *The Compound Protocol Whitepaper*
  - 🔴 *Attacking the DeFi Ecosystem with Flash Loans*（arXiv 2020）
  - 🔴 *A Survey of Stablecoins*（arXiv 2021）

- **L10 (Oct 22)** — Decentralized Exchanges (DEX)
  - 自动做市商（AMM）：Uniswap 的恒定乘积公式 $x \cdot y = k$
  - Uniswap V2 vs V3（集中流动性）
  - 滑点（Slippage）、无常损失（Impermanent Loss）
  - 🔴 *Uniswap V2 Whitepaper*（x·y=k）
  - 🔴 *Introduction to Uniswap V3*（集中流动性）
  - 🔴 *YieldSpace*（固定收益代币 AMM, Sections 2-3）

- **L11 (Oct 27)** — Maximal Extractable Value (MEV)
  - MEV 定义：矿工/验证者可提取的最大价值
  - 套利（Arbitrage）、三明治攻击（Sandwich Attack）、清算（Liquidation）
  - MEV-Boost / Flashbots：PoS 时代的 MEV 提取
  - 🔴 *Quantifying Blockchain Extractable Value*（arXiv 2021）

**核心概念**: AMM、Constant Product Formula、Flash Loan、Impermanent Loss、MEV、Sandwich Attack

### 第五部分：法律与 Layer-1 生态（L12-L13）

- **L12 (Oct 29)** — Legal Aspects and Regulation
  - *客座讲师: Miles Jennings（a16z）*
  - Howey 测试：代币是否为证券
  - SEC 监管框架
  - 🔴 Hinman Speech — *Digital Asset Transactions: When Howey Met Gary*
  - 🔴 Peirce — *The SECret Garden*
  - 🔴 *A Visual Guide to the Howey Test*

- **L13 (Nov 3)** — Other Layer-1 Architectures: Solana, Sui, Aptos
  - Solana：PoH（Proof of History）+ Sealevel 并行执行
  - Sui / Aptos：Move 语言的资源导向编程
  - 🔴 *AlpenGlow: A New Consensus for Solana*（Anza）
  - 🔴 *The Solana Programming Model for Ethereum Developers*

**核心概念**: Howey Test、Security Token vs Utility Token、PoH、Move Language

### 第六部分：隐私技术（L14-L16）

- **L14 (Nov 5)** — Privacy: De-anonymizing and Mixing
  - 区块链隐私分析：交易图分析
  - 混币器（Tornado Cash, Wasabi Wallet）
  - 🔴 *A Fistful of Bitcoins*（IMC 2013）— 早期 Bitcoin 去匿名化
  - 🔴 *ZeroLink: The Bitcoin Fungibility Framework*

- **L15 (Nov 10)** — zk-SNARKs for Privacy
  - 零知识证明基础：交互式 → 非交互式（Fiat-Shamir）
  - zk-SNARK = Succinct + Non-interactive + ARgument of Knowledge
  - 应用：Zcash 的屏蔽交易、机密交易（Confidential Transactions）
  - 🔴 *Zcash Paper*（Section 1）
  - 🔴 *Confidential Transactions*（Elements Project）

- **L16 (Nov 12)** — Constructing a Preprocessing zk-SNARK
  - PLONK：通用可信设置（Universal Trusted Setup）
  - 多项式承诺（Polynomial Commitments）
  - 🔴 *The PLONK SNARK*（eprint 2019）
  - 🔴 *Polynomial Commitments*（Section 1）

**核心概念**: Zero-Knowledge Proof、zk-SNARK、Fiat-Shamir Transform、Polynomial Commitment、Trusted Setup

### 第七部分：扩展方案（L17-L18）

- **L17 (Nov 17)** — Payment Channels and State Channels
  - 闪电网络（Lightning Network）：支付通道 + HTLC
  - 状态通道（State Channels）：通用链下计算
  - 🔴 *The Bitcoin Lightning Network Paper*（Poon & Dryja 2016）

- **L18 (Nov 19)** — Rollups: Optimistic, ZK, Based, Native
  - Layer 2 扩展核心方案
  - **Optimistic Rollup**: 欺诈证明（Fraud Proof），7 天挑战期
  - **ZK Rollup**: 有效性证明（Validity Proof），即时最终性
  - **Based Rollup**: 排序由 L1 驱动
  - 数据可用性（Data Availability）：EIP-4844 Blob
  - 🔴 *Optimistic Rollup*（Plasma Group）
  - 🔴 *Arbitrum*（USENIX Security 2018）
  - 🔴 *Blobs on Ethereum*（EIP-4844）

**核心概念**: Payment Channel、HTLC、Lightning Network、Optimistic Rollup、ZK Rollup、Fraud Proof vs Validity Proof、Data Availability

### 第八部分：前沿话题（L19-L20）

- **L19 (Dec 1)** — Account Abstraction, Bridging, Post-Quantum, AI
  - 账户抽象（EIP-4337 / EIP-7702）：智能合约钱包
  - 跨链桥（Bridges）：Optics / Wormhole / LayerZero
  - 后量子区块链：BIP-360（抗量子签名）
  - AI + 区块链：去中心化 AI 推理
  - 🔴 *You Could Have Invented Account Abstraction*
  - 🔴 *EIP-7702*
  - 🔴 *Post-quantum Bitcoin*（BIP-360）
  - 🔴 *How to Build a Private DAO*

- **L20 (Dec 3)** — The Future of Blockchains
  - *客座讲师: Arianna Simpson（a16z General Partner）*
  - 区块链行业的投资与创业视角

---

## 🧮 核心方法

### SHA-256 哈希
```python
import hashlib
def simple_hash(data: str) -> int:
    return int(hashlib.sha256(data.encode()).hexdigest(), 16)
```

### RSA 加密 / 签名
$$\text{Encrypt}: c = m^e \bmod n \qquad \text{Decrypt}: m = c^d \bmod n$$
$$\text{Sign}: \sigma = H(m)^d \bmod n \qquad \text{Verify}: H(m) \stackrel{?}{=} \sigma^e \bmod n$$

### Nakamoto Consensus（PoW）
1. 挖矿：找 $nonce$ 使 $H(blockHeader + nonce) < target$
2. 最长链规则：始终采纳累计工作量最大的链
3. 概率最终性：6 个确认后不可逆（概率上）

### Uniswap AMM（恒定乘积）
$$x \cdot y = k$$
交易 $\Delta x$ 数量的 token $X$ 获得 $\Delta y$ 数量的 token $Y$：
$$(x + \Delta x)(y - \Delta y) = k \quad \Rightarrow \quad \Delta y = y - \frac{k}{x + \Delta x}$$

### zk-SNARK 流程
```
电路 (Circuit)
    ↓  编译
R1CS (Rank-1 Constraint System)
    ↓  多项式化
QAP (Quadratic Arithmetic Program)
    ↓  多项式承诺
zk-SNARK Proof (π)  →  Verifier 验证 (常数时间)
```

---

## 💻 项目代码

📁 `topic10-theory/rsa_crypto.py`（255 行）

**实现内容**:
1. ✅ **RSA 从零实现**（Miller-Rabin 素数测试 + 扩展欧几里得）
2. ✅ **SHA-256 哈希**（stdlib 封装）
3. ✅ **RSA 数字签名**（签名 + 验证 + 篡改检测）
4. ✅ **简化区块链**（PoW 挖矿 + 链验证 + 篡改检测）
5. ✅ **Diffie-Hellman 密钥交换**

### 运行
```bash
cd topic10-theory
python3 rsa_crypto.py
```

### 核心代码片段

```python
# 区块链 PoW 挖矿
def mine(self, block: Block) -> int:
    prefix = "0" * self.difficulty
    nonce = 0
    while True:
        block.nonce = nonce
        if block.compute_hash().startswith(prefix):
            return nonce
        nonce += 1

# 链完整性验证
def verify(self) -> bool:
    for i in range(1, len(self.chain)):
        if self.chain[i].prev_hash != self.chain[i-1].compute_hash():
            return False
    return True

# RSA 签名验证
def rsa_verify(m, sig, pub):
    h_expected = simple_hash(str(m)) % pub.n
    h_got = pow(sig, pub.e, pub.n)
    return h_expected == h_got
```

### 课程作业

| 作业 | 内容 | 截止 |
|------|------|------|
| **Project 1** | Merkle Trees in Python | Oct 1 |
| **Homework 1** | 密码学练习 | Oct 7 |
| **Project 2** | Bitcoin 交易（python-bitcoinlib） | Oct 14 |
| **Homework 2** | Bitcoin 机制 | Oct 21 |
| **Project 3** | Ethereum 支付应用 | Oct 28 |
| **Homework 3** | Ethereum / Solidity | Nov 4 |
| **Project 4** | 链上钱包构建 | Nov 18 |
| **Homework 4** | DeFi / 共识 / 隐私 | Dec 2 |
| **Final Exam** | 24 小时窗口内 3 小时 | Dec 9 |

---

## 📊 关键论文 / 教材

### 🔴 必读 P0

| # | 论文 | 年份 | 核心贡献 |
|---|------|------|---------|
| 1 | **Satoshi Nakamoto** — *Bitcoin Whitepaper* | 2008 | 区块链开山之作 |
| 2 | **Ethereum Yellow Paper** (Wood) | 2014 | Ethereum 形式化规范 |
| 3 | **Uniswap V2** — *x·y=k* | 2018 | AMM 奠基 |
| 4 | **Lightning Network** (Poon & Dryja) | 2016 | 支付通道 |
| 5 | **PLONK** (Gabizon, Williamson & Ciobotaru) | 2019 | 通用 zk-SNARK |
| 6 | **Flash Boys 2.0** (Daian et al.) | 2019 | MEV 概念提出 |
| 7 | **Arbitrum** (Kalodner et al.) | 2018 | Optimistic Rollup |
| 8 | **Zcash Paper** | 2014 | zk-SNARK 隐私币 |

### 🟡 P1
9. *Foundations of Distributed Consensus and Blockchains* — Elaine Shi（免费教材）
10. *Compound Whitepaper* — 借贷协议
11. *BLS Signatures* — Boneh, Lynn & Shacham (2001)
12. *Boneh-Shoup* — *Applied Cryptography*（免费教材）

### 📖 延伸
13. *Mastering Bitcoin* (Andreas Antonopoulos) — 工程实践
14. *The Infinite Machine* (Camila Russo) — Ethereum 历史

---

## 🎯 学习路径

| 角色 | 推荐路径 |
|------|---------|
| **密码学研究员** | CS251 + CS255（Crypto I）+ CS355（Crypto II）→ IACR 发表 |
| **区块链工程师** | CS251 → 实习（Ethereum Foundation / Paradigm / a16z crypto） |
| **DeFi 研究员** | CS251 + 经济学课程 → DeFi 协议设计 |
| **安全审计员** | CS251 + CS155（计算机安全）→ 智能合约审计 |
| **加密货币交易员** | CS251 + 金融工程 → 量化策略 |

---

## 💡 反思与批判

### 课程优势
1. **Boneh 教授的密码学深度无可匹敌**——BLS 签名的发明者讲签名，PLONK 的同事讲零知识证明
2. **全栈覆盖**——从数学（zk-SNARK）到法律（Howey 测试），从共识理论到 DeFi 经济学
3. **与时俱进的课程设计**——每年更新，2025 版已包含 EIP-7702、Account Abstraction、AI + 区块链
4. **4 个编程 Project** 极其务实——Merkle 树 / Bitcoin 交易 / Ethereum 应用 / 链上钱包
5. **客座讲座质量极高**——a16z 的 Miles Jennings（法律）、Arianna Simpson（投资）

### 潜在局限
1. **数学门槛极高**——zk-SNARK 涉及椭圆曲线、多项式承诺，没有密码学背景的学生可能吃力
2. **Solidity 只讲 1 节课**——智能合约编程实战需要大量自学
3. **课程内容过载**——20 讲覆盖了其他学校一整年的内容，节奏极快
4. **缺乏实操环境**——没有 testnet 实际部署的环节
5. **对区块链的批判性反思不足**——课程倾向于"how it works"而非"should it exist"

### 独特价值
- **Boneh 是密码学世界的活化石**——听他讲密码学，就像听 Linus 讲操作系统
- **从密码学原语到 DeFi 应用的完整链条**——没有其他课程能做到这个深度和广度
- **zk-SNARK 章节（L15-L16）本身就是一门浓缩的零知识证明课**

---

## 🚀 扩展

完成 CS251 后推荐：
1. **CS255** — Introduction to Cryptography（Boneh，密码学理论深度）
2. **CS355** — Advanced Cryptography（零知识 / 多方安全计算）
3. **CS155** — Computer and Network Security（安全工程）
4. **EE374** — Blockchain and Cryptoeconomics（经济学视角）

### 实践资源
- **Remix IDE** — 在线 Solidity 开发环境
- **Hardhat / Foundry** — 智能合约开发框架
- **Etherscan** — 区块链浏览器
- **DeFi Pulse / DefiLlama** — DeFi 数据
- **Mirror.xyz** — 加密原生写作平台
- **a16z Crypto Research** — 前沿研究博客

### 社区
- **Ethereum Foundation** — https://ethereum.org/
- **Bitcoin Developer Reference** — https://developer.bitcoin.org/
- **IACR ePrint** — 密码学论文预印本

---

**最后更新**: 2026-08-11
**对应代码**: `topic10-theory/rsa_crypto.py`

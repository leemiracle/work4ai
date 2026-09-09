# Lab07 — 密码学专题（飞腾的杀手级特性）

> 飞腾 D3000 实测支持的密码学指令集极其完整：
> AES, SHA1, SHA256, **SHA3, SHA512, SM3, SM4**, PMULL, CRC32
> 这让它特别适合做国密合规、TLS 终结、区块链节点。

---

## 0. 学习目标（一句话）

**实测飞腾 D3000 各种硬件加密的吞吐**，并理解为什么硬件加速比软件实现快 100 倍。

---

## 1. 对应教材与课程

| 来源 | 章节 |
|------|------|
| 📖 | NIST FIPS 197 (AES) |
| 📖 | RFC 6234 (SHA1/256/512) |
| 📖 | GB/T 32905-2016 (SM3) |
| 📖 | GB/T 32907-2016 (SM4) |
| 📖 | ARM ARM (DDI 0487) §C2 "Cryptography Extensions" |

---

## 2. 核心概念速览

### 2.1 硬件加速的数学

AES 单轮需要 4 个操作：SubBytes, ShiftRows, MixColumns, AddRoundKey
- 软件：~50 cycles/byte（基于查表）
- 硬件（`AESE`, `AESMC`）：1 cycle/byte（10 轮共 10 cycles for 16 bytes）

→ **50x 加速**

### 2.2 飞腾 D3000 实测吞吐目标

> ⚠️ **方法学诚实声明**：下表"硬件"列测的是**指令吞吐演示，非完整算法**——
> `aes_test.c` 用 11 轮 AESE 但所有轮同一 round key（无 KeyExpansion）、`sha_compare.c` 硬件版仅 16 轮无消息调度。
> 完整 AES/SHA 实现见 OpenSSL。诊断报告 §2.3 记录了此方法学缺陷。

| 算法 | 硬件 | 软件 | 加速比 |
|------|------|------|--------|
| AES-128 (简化实测) | 0.5 GB/s (实测) / 5-10 (完整流水线) | 100-200 MB/s | 简化版无流水线 |
| SHA-256 | 3-5 GB/s | 200-400 MB/s | 15× |
| SHA-512 | 3-5 GB/s | 300-500 MB/s | 10× |
| SM3 | 2-4 GB/s | 150-300 MB/s | 15× |
| SM4 | 3-5 GB/s | 100-200 MB/s | 25× |
| CRC32C (实测) | 6.6 GB/s (实测) | 0.12 GB/s (table) | 18.9× (实测) |

---

## 3. 实验列表

### 3.1 实验 7.1：AES-128 实测（`aes_test.c`）

跑 10 次 AES-128 ECB 加密，测吞吐。

### 3.2 实验 7.2：SHA-256 vs SHA-512 vs SHA3（`sha_compare.c`）

对比 4 种哈希算法的吞吐。

### 3.3 实验 7.3：SM3 / SM4 国密（`sm_test.c`）

国密算法实测——飞腾在中国市场的核心优势。

### 3.4 实验 7.4：CRC32 多种实现（`crc_test.c`）

软件 CRC32 vs ARMv8 硬件 CRC32。

---

## 4. 编译与运行

```bash
cd Lab07_密码学专题
make
./aes_test
./sha_compare
./sm_test
./crc_test
```

---

📌 Capstone 项目组合在 [`Capstone/`](../Capstone/)。

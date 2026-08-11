# CS356: Topics in Computer and Network Security

> Stanford University | 本科 / 研究生 | 网络安全主题课
> Instructor: **Zakir Durumeric**（Censys / ZMap 作者，全网扫描先驱）
> 先修: CS110 或同等系统基础 + 基础网络知识
> 难度: ⭐⭐⭐⭐
> 定位: 攻击类型剖析 + 多层防御，理论与实践并重

---

## 📚 课程定位

CS356 是 Stanford **计算机与网络安全主题课**，由 **Zakir Durumeric** 教授主讲。Durumeric 是 **ZMap**（极速全网扫描器）和 **Censys**（互联网资产搜索引擎）的核心作者，在网络测量与安全领域享有盛誉。课程系统剖析各类**攻击手法**，并讲授对应的**防御机制**，强调"知己知彼"的安全思维。

### Zakir Durumeric 教授
- Stanford CS 教授，研究方向：网络测量、互联网安全、漏洞大规模检测
- 代表作：**ZMap**（45 分钟扫描全网）、**Censys**、Heartbleed 大规模测量
- 教学风格：大量真实案例（log4j / SolarWinds / Heartbleed）

---

## 🎯 学习目标

1. 理解主流**攻击类型**的原理与利用方式
2. 掌握**纵深防御**（defense in depth）的设计哲学
3. 学会使用安全工具（扫描 / 漏洞分析 / 入侵检测）
4. 评估真实世界的安全事件，设计缓解方案
5. 理解密码学、认证、授权在安全中的角色

---

## 📅 核心模块

### Part 1: 攻击类型剖析
- **缓冲区溢出**：栈溢出注入 shellcode
- **注入攻击**：SQL Injection（`' OR 1=1 --`）/ Command Injection
- **跨站攻击**：XSS（`<script>`）/ CSRF（伪造请求）
- **社会工程**：Phishing（钓鱼邮件）
- **中间人**：MITM 窃听 / 修改流量
- **拒绝服务**：DDoS（Syn flood / UDP amplification）
- **供应链攻击**：SolarWinds / log4j

### Part 2: 网络安全
- TLS / HTTPS 机制与弱点
- 证书颁发机构（CA）信任模型
- DNS 安全（DNSSEC / DNS over HTTPS）

### Part 3: 认证与授权
- 密码安全（哈希 / 盐 / 慢哈希）
- 多因素认证（MFA / TOTP）
- 访问控制（RBAC / ABAC）

### Part 4: 系统安全
- 沙箱与隔离（容器 / 虚拟机 / seccomp）
- 内存保护（ASLR / DEP / Stack Canary）
- 补丁管理与漏洞披露

### Part 5: 安全运营
- 入侵检测（IDS / IPS）
- 日志审计与取证
- 安全监控（SIEM）

---

## 💻 项目代码

📁 `supplementary/final_projects.py::cs356_demo()`

实现了网络安全**攻击类型速查**与**防御层级**框架：
- 8 类常见攻击 + 典型 payload 示例
- 6 层纵深防御（加密 / 认证 / 授权 / 审计 / 沙箱 / 补丁）

**运行**：
```bash
cd supplementary && python3 -c "from final_projects import cs356_demo; cs356_demo()"
```

输出覆盖 8 类攻击（Buffer Overflow / SQL Injection / XSS / Supply Chain …）+ 6 层防御（加密 / 认证 / 授权 / 审计 / 沙箱 / 补丁）。

---

## 📊 关键概念/论文

### 🔴 必读 P0
1. **Durumeric et al. 2013** "ZMap: Fast Internet-Wide Scanning"（USENIX Security）
2. **Heartbleed 测量**（Durumeric 团队，2014）
3. **OWASP Top 10** — Web 安全风险权威清单

### 🟡 P1
4. *Security Engineering*（Ross Anderson，免费在线）— 安全圣经
5. **Censys** / **Shodan** — 互联网资产搜索
6. **log4j / SolarWinds** 事件分析报告

### 核心概念
- **纵深防御（Defense in Depth）**：多层防护，单点失守不致命
- **最小权限原则（Least Privilege）**：只授予必要权限
- **零信任（Zero Trust）**：永不信任，始终验证

---

## 🎯 适用人群

- **安全工程师**: CS356 是核心训练 → 实习（Google / Microsoft / 安全初创）
- **渗透测试 / 红队**: CS356 + CS155（Computer Security）
- **SRE / DevSecOps**: 理解攻击面，加固基础设施
- **安全研究**: 读 ZMap / Censys 论文，全网测量

---

## 🚀 扩展

完成后推荐：
1. **CS155** — Computer and Network Security（更系统的安全工程）
2. **CS255** — Introduction to Cryptography（密码学理论）
3. **CS251** — Blockchain Technologies（区块链安全）
4. CTF 实战（picoCTF / DEF CON）+ 工具（Wireshark / Burp / nmap / ZMap）

---

**对应代码**: `supplementary/final_projects.py::cs356_demo()`

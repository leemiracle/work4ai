# stage-3 研究方向 E:信息论与编码 · 研究入门笔记

> stage-3 五大候选之一(ROADMAP §5-E)。本地书:GTM134《Coding and Information Theory》。
> 创建:2026-07-01

---

## §0 定位

> **信息论 = "信息"的数学化(Shannon 1948)。熵度量不确定性,互信息度量相关,编码定理给出压缩/传输的极限。这是通信/压缩/密码/ML 的公共语言。**

---

## §1 五大核心概念

### 1. Shannon 熵
$$H(X)=-\sum_x p(x)\log_2 p(x)\text{ (比特)}$$
- 均匀分布熵最大($\log n$);确定分布熵最小(0)
- **物理**:熵 = 平均需要多少比特编码 $X$

### 2. 互信息
$$I(X;Y)=H(X)-H(X|Y)=H(Y)-H(Y|X)$$
- $X,Y$ 独立 ⟺ $I=0$
- **应用**:特征选择(ML)/信道容量

### 3. 信源编码(无损压缩)
- **Shannon 信源编码定理**:平均码长 $\ge H(X)$(下界)
- 霍夫曼/算术编码(逼近 $H$)
- **LZ77/LZW**(gzip/zstd 的核心)

### 4. 信道编码(传输)
- **信道容量** $C=\max I(X;Y)$(Shannon 极限)
- 低于 $C$ 可靠传输;高于 $C$ 不可能
- **汉明/LDPC/Turbo/Polar 码**(逼近 Shannon 极限)

### 5. 率失真(有损压缩)
$R(D)$=在失真 $\le D$ 下的最小码率(JPEG/MP3/视频编码)

---

## §2 推荐书
- **GTM134 Coding and Information Theory**(本地)✅
- Cover-Thomas《Elements of Information Theory》(信息论圣经)
- MacKay《Information Theory, Inference, and Learning Algorithms》(信息+ML)

---

## §3 飞腾锚点
| 概念 | 飞腾/工程 |
|------|----------|
| 熵 | 数据压缩(zstd 跑在飞腾,workload_characterization 实测)|
| 信道编码 | 5G/WiFi/卫星通信 |
| **密码**(信息论安全)| **Lab07**(AES/SM3/SM4,国密合规)|
| 互信息 | 特征选择/信息增益(决策树)|

---

## §4 开放研究问题
1. **极化码(Polar)**:Arikan 2009 首次达 Shannon 极限(5G 上行)
2. **分布式信源编码**(Slepian-Wolf):多源压缩
3. **信息论安全**:一次一密完美安全但需等长密钥(量子密钥分发 QKD)
4. **信息 Bottleneck**:深度学习的表征压缩

---

## §5 与其他方向交叉
- A ML:PAC-Bayes 用 KL 散度(信息+学习)
- B 概率:大偏差理论(信息+概率)
- C 数值:量化误差的信息界
- D 优化:最大熵原理(信息+优化)

---

## 📌 锁定此方向后:读 GTM134 + Cover-Thomas,研究"国密 SM 系列的信息论分析"

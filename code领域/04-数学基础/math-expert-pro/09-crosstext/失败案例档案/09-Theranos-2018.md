# V26 失败案例档案 #9：Theranos 2018（$9 亿统计学造假）

> **伪造临床试验数据 → 90 亿美元泡沫**

---

## 📅 时间线

| 时间 | 事件 |
|------|------|
| 2003 | Elizabeth Holmes 19 岁辍学创办 Theranos |
| 2010-2014 | Theranos 估值飙升至 $90 亿 |
| 2015.10 | **Wall Street Journal John Carreyrou 调查** |
| 2015-2018 | FDA / CMS 调查 |
| **2018.9** | **Holmes 被控欺诈** |
| 2022.1 | Holmes 被判 11 年监禁 |

**直接损失**：
- 投资者 $7+ 亿
- 患者诊断错误（不可计数）
- "女版乔布斯"神话破灭

---

## 🎯 数学误用：临床统计学造假

### 错误 1：小样本过度推广
Theranos 主张一滴血测 200+ 项，但**临床数据仅几十例**。

### 错误 2：比较组缺失
Theranos 设备 vs 标准设备对比数据**故意不公开**。

### 错误 3：标准差操纵
"误差范围内一致"——实际**误差范围远超临床意义**。

### 错误 4：偏差数据
Theranos 用健康员工数据 vs 患者实际数据混淆。

---

## 🧠 认知偏差：传奇叙事 + 权威光环

### 偏差 1：传奇叙事
"19 岁辍学女生改变医学" → 媒体狂欢。

### 偏差 2：权威背书
Henry Kissinger / George Shultz / James Mattis 任董事 → 投资者迷信。

### 偏差 3：FOMO（错失恐惧）
Walgreens / Safeway 抢先合作。

### 偏差 4：沉默信号
内部员工 Tyler Shultz 警告 → 被律师函威胁。

---

## 🔍 正确做法

### 1. 双盲对比试验
Theranos 设备 vs 雅培/西门子标准设备。

### 2. Bland-Altman 图
```python
import numpy as np
import matplotlib.pyplot as plt
# 模拟 Theranos vs 标准
np.random.seed(0)
standard = np.random.normal(100, 15, 100)
theranos = standard + np.random.normal(20, 30, 100)  # Theranos 偏差大
mean = (standard + theranos) / 2
diff = theranos - standard
plt.scatter(mean, diff); plt.axhline(np.mean(diff), color='red')
plt.axhline(np.mean(diff) + 1.96*np.std(diff), color='red', linestyle='--')
plt.axhline(np.mean(diff) - 1.96*np.std(diff), color='red', linestyle='--')
plt.title('Bland-Altman: Theranos 不可接受的临床偏差')
```

### 3. FDA 注册
设备上市前必须 FDA 510(k) 或 PMA。

### 4. 实验室认证
CLIA 认证（Theranos 实际被吊销）。

### 5. 同行评审
发表在 NEJM / JAMA（Theranos 一篇都没发）。

---

## 📚 启示
1. **统计学是临床医学的根基**
2. **同行评审不可省**
3. **传奇 ≠ 真理**
4. **权威光环危险**——Kissinger 不懂数学
5. **告密者保护**——Tyler Shultz 是英雄
6. **Bland-Altman 是医学基本工具**

---

## 📐 接入
- `07-critique/`：新建 `失败案例09-Theranos 2018.md`
- `../math/华章数学丛书/51-概率论基础教程原书第九版.md`：假设检验
- `11-日常生活/02-病人理解诊断概率.md`

---

## 🎯 独家切面：**统计学造假的"商业泡沫"**——一个 Bland-Altman 图就能戳破的谎言，让投资者损失 $9 亿。

> 📖 [V26](../视角深度/V26-失败案例.md)

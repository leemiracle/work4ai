# 子领域 6 · Markets-Cities · 市场、组织与城市

> **研究命题**：经济网络、隔离机制、城市规模法则——市场和城市的数学骨架。

---

## 为什么这个子领域重要

城市/市场是 21 世纪的主要生存场景：
- 全球 55% 人口住在城市，2050 将达 68%
- 城市贡献 80%+ GDP，也贡献 70%+ 碳排放
- 公司组织是"小城市"
- 经济网络 = 抽象城市

数学化让我们看清楚：
- 隔离是涌现的（Schelling）
- 城市规模有数学极限（West）
- 公司有"规模不经济"

---

## 章节地图

| # | 文件 | 核心问题 | 关键工具 |
|---|---|---|---|
| 1 | `01-schelling.py` | ⭐⭐⭐ 为什么温和偏好产生极端隔离？ | Schelling 元胞自动机 |
| 2 | `02-scaling-laws.py` | 城市为什么有"1.15 次方"法则？ | West 幂律 |

---

## 跑代码

```bash
cd /data/usershare/ai/social-laws/06-markets-cities/
python3 01-schelling.py       # ⭐ 重头戏
python3 02-scaling-laws.py
```

---

## 核心命题回顾

跑完本子领域，你应该能用 5 句话总结：

1. **温和偏好 → 极端隔离**（Schelling 涌现）
2. **城市产出 ~ N^1.15，基础设施 ~ N^0.85**（West 幂律）
3. **大城市人均更富但更病**（β > 1 的双面性）
4. **公司利润 ~ N^0.8**（规模不经济）
5. **同一套数学贯穿生物/城市/公司**（universality class）

---

## 进阶批判

1. **Schelling 是 1 维偏好**——现实是多维身份
2. **West 的 1.15 不普适**——中国 1.05-1.20 之间
3. **β 不是常数**——技术革命改变 β
4. **公司组织不仅是规模**——还有战略、文化、领导力
5. **算法时代的"虚拟隔离"**——信息茧房 = Schelling 的网络版

---

## 子领域间的连接

- **markets × inequality**：城市加剧不平等（模块 3）
- **markets × revolution**：城市革命（模块 4）
- **markets × networks**：城市 = 网络的密集化（模块 1）
- **markets × LLM**：远程工作改变城市规模法则（模块 7）

---

## 📊 已抓取的真实 CSSCI 论文（NCPSSD 核实）

### 📄 ⭐⭐ 郑怡林、高亚飞、陆铭（2026）《倾斜城市：大城市人口空间分布与产业发展的国际比较及启示》
- 《国际经济评论》2026 年第 3 期，第 9-35 页
- **中国社科院世界经济与政治研究所**（CSSCI 经济学顶刊）
- **直接对应**：本项目 `02-scaling-laws.py` 的 West 1.15 法则
- **陆铭的最新论文**——把 West 法则从"总量"细化到"空间方向"
- 这是 `docs/cssci-frontiers.md` 提到的陆铭《大国大城》理论的最新学术版本

### 📄 翟东升、李雪景（2026）《东亚区域生产网络重构的国际政治经济学解读——以韩国产业布局调整为例》
- 《当代亚太》2026 年第 2 期，第 65-90 页
- 经济网络 = 模块 1 网络科学的应用

详见 [`docs/cssci-real-papers.md`](../docs/cssci-real-papers.md)

---

## 推荐文献

### 必读 ⭐
- Schelling, T. (1978). *Micromotives and Macrobehavior.*
- West, G. (2017). *Scale.*
- Bettencourt, L. (2013). *The Origins of Scaling in Cities.* Science.

### 进阶
- Epstein & Axtell (1996). *Growing Artificial Societies.*
- 陆铭 (2016). 《大国大城》

### 中文
- 周其仁 - 《城乡中国》
- 陆铭 - 《大国大城》
- 赵燕菁 - 关于城市规划的著作

---

## 完成标志

✅ Schelling 跑出"温和偏好 → 极端隔离"
✅ 能解释 1.15 和 0.85 的来源
✅ 写完 `notes/week-09-10-markets-finale.md`
✅ **启动 `projects/p1-schelling-interactive/`**（推荐作品集项目）

---

*完成本章后进入 [`../07-crosscuts/`](../07-crosscuts/) — 交叉专题（"并结合子领域"）*

# management_toolkit —— 管理学量化算法武器库

把"管理"从口号变成可计算的工程。全部算法均**实跑验证**，数值即为真实输出。

## 文件总览

| 文件 | 类别 | 覆盖算法 |
|---|---|---|
| `mgmt_decision_finance.py` | 决策 / 财务 | EMV、EVPI、贝叶斯更新、AHP、NPV/IRR、CAPM、Black-Scholes |
| `mgmt_ops_network.py` | 运营 / 网络 | LP(产品组合)、CPM 关键路径、EOQ、M/M/1 排队、ONA 中心性+社区 |
| `mgmt_systems_behavior.py` | 系统 / 博弈 / 行为 | 系统动力学(一阶/二阶)、纳什均衡(纯/混合)、前景理论、马尔可夫、PERT 蒙特卡洛 |
| `mgmt_perf_quality.py` | 绩效 / 质量 | 杜邦分解、EVA、TOPSIS、报童模型、DPMO 六西格玛、田口损失、波特五力加权 |
| `beer_game.py` | 系统动力学深挖 | **啤酒游戏** 4 级供应链仿真 + 牛鞭效应量化 → `beer_game.png` |
| `auction_mechanism.py` | 机制设计深挖 | 一价/二价/VCG 拍卖，验证 **DSIC + 收益等价定理** |
| `viz_ona.py` | 可视化 | 组织网络分析（度/介数/特征向量中心性 + 社区）→ `ona_karate.png` |
| `viz_systems.py` | 可视化 | 一阶 vs 二阶系统对比（过冲振荡）→ `systems_dynamics.png` |
| `viz_risk.py` | 可视化 | PERT 蒙特卡洛工期分布（P10/P50/P90）→ `pert_risk.png` |

## 快速运行
```bash
cd management_toolkit
python3 mgmt_decision_finance.py   # 决策与财务
python3 mgmt_ops_network.py        # 运营与网络
python3 mgmt_systems_behavior.py   # 系统与博弈
python3 mgmt_perf_quality.py       # 绩效与质量
python3 beer_game.py               # 牛鞭效应仿真
python3 auction_mechanism.py       # 拍卖机制设计
python3 viz_ona.py viz_systems.py viz_risk.py   # 生成 PNG
```
依赖：`numpy scipy networkx pulp matplotlib`（均已在环境内）。

## 关键实测结论速查
- **牛鞭**：终端需求方差 0.074 → 工厂订单方差 529，累计放大 **7177×**。
- **收益等价**：一价 0.6664 ≈ 二价 0.6664 ≈ 理论 0.6667。
- **DSIC**：二价拍卖真实报价效用 +0.034 > 任何偏离（抬高/压低都更差）。
- **PERT**：单点 14 周，P90=20.5 周，按单点完工概率仅 **7.8%**。
- **ONA**：空手道俱乐部 3 个社区 [17,9,8] 还原历史真实派系分裂。
- **系统动力学**：稳态库存 = 目标 − 销售率×τ（持续补货抵消销售）。

## 管理学思想地图（README 速记）
历史脉络：科学管理(泰勒) → 科层制(韦伯) → 人际关系(梅奥) → 决策学派(西蒙, 有限理性)
→ 系统/权变 → 战略(波特) → 质量/精益(戴明/TPS) → 学习型组织(圣吉/野中) → 平台/AI/算法管理。

十个理论支柱：科学管理｜科层制｜行为学派｜决策学派｜系统权变｜交易成本(Coase)｜
委托代理+机制设计(Jensen-Meckling)｜RBV+动态能力(Barney/Teece)｜波特竞争战略｜学习/知识管理。

八个视角：经济｜心理｜社会｜系统｜政治｜工程运营｜演化生物｜数据AI。

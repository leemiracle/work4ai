# 推荐系统 · 算法实现与教学集

> 全部代码已实跑验证（Python 3.10 + PyTorch 2.x + scikit-learn）。每个文件自包含，可直接运行。
> 覆盖工业推荐系统全链路：**召回 → 精排 → 重排 → 评估 → 前沿**。

## 目录与文件

| 文件 | 内容 | 核心验证点 |
|------|------|-----------|
| `01_core_algorithms.py` | 6 大核心算法：MF 召回 / FM 二阶交叉 / 双塔 DSSM(in-batch softmax) / DIN 目标注意力 / MMoE 多任务 / DPP 重排 | in-batch loss≈5.58 (ln64=4.16 基线)；DIN 换候选后池化向量 L2=0.099>0 |
| `02_dpp_rerank.py` | DPP 贪心正确实现（Cholesky 增量更新） | 数学严谨版，$O(k^2)$ 增量 |
| `03_dpp_demo.py` | DPP 价值演示（高分冗余副本场景） | 贪心相似度 0.50 → DPP 0.00，用 11% 相关性换 100% 多样性 |
| `04_advanced_models.py` | 6 大进阶：DeepFM / PLE-CGC / ESMM / 向量检索(IVF) / IPS-DR 反事实评估 / TIGER 语义 ID | ESMM `pCTCVR=pCTR×pCVR∈[0,1]`；DR 最接近真值 |

## 运行方式

```bash
# 依赖：torch, numpy, scikit-learn (faiss 可选, 未装则用 numpy 实现检索)
pip install torch numpy scikit-learn

# 按学习顺序运行
python3 01_core_algorithms.py      # 召回 + 精排 + 重排 基础
python3 02_dpp_rerank.py           # DPP 正确实现
python3 03_dpp_demo.py             # DPP 价值演示
python3 04_advanced_models.py      # 进阶模型 + 评估 + 前沿
```

## 算法全景索引

### 召回层（Retrieval）
- **协同过滤**：UserCF / ItemCF / Swing / **矩阵分解 MF/SVD** (`01`) / ALS / BPR
- **向量化双塔**：**DSSM** (`01`) / YouTube DNN / 多兴趣(MIND/ComiRec)
- **序列**：GRU4Rec / SASRec / BERT4Rec
- **图**：PinSage / GraphSAGE / **LightGCN**
- **生成式** ⭐：**TIGER 语义 ID** (`04`)

### 精排层（Ranking）
- **特征交互**：LR / GBDT+LR / **FM** (`01`) / **DeepFM** (`04`) / DCN / DCN-V2 / xDeepFM / AutoInt
- **序列注意力**：**DIN** (`01`) / DIEN / DSIN / BST / SIM(长序列)
- **多任务**：Shared-Bottom / **MMoE** (`01`) / **PLE-CGC** (`04`) / **ESMM** (`04`) / PEPNet ⭐

### 重排层（Re-ranking）
- **启发式**：MMR / 规则打散
- **数学最优**：**DPP** (`02`,`03`) / Fast-DPP / Sliding-DPP
- **列表级**：Seq2Slate / PRM
- **强化学习**：RL rerank / slate Q-learning

### 评估与因果
- **离线**：AUC / GAUC / NDCG@K / Recall@K
- **反事实** ⭐：**IPS / Doubly Robust** (`04`) / SNIPS / Unbiased Learning
- **在线**：A/B / **Interleaving** / **CUPED**

### 前沿（2024-2026）⭐
- **LLM4Rec**（4 角色：特征器 / 推理器 / Encoder / 直接推荐）
- **生成式检索**：TIGER / LMIndexer
- **推荐 Agent / 模拟器**：Agent4Rec / RecAgent
- **多模态召回**：CLIP-style 双塔
- **xAI X-For-You 六阶段管线**：Source→Hydrator→Filter→Scorer→Selector→SideEffect

## 工业级架构（多阶段漏斗）

```
全量候选(10^7~10^9)
  │  ① 召回 Retrieval       多路并行 + ANN 检索, 强调 Recall@K
  ▼
~10^4  ② 粗排 Pre-ranking   轻量双塔/小DNN, 强调 QPS
  ▼
~10^3  ③ 精排 Ranking       DeepFM/DIN/MMoE, 用全特征, 强调 AUC/GAUC
  ▼
几百   ④ 重排 Re-ranking    DPP/MMR/Seq2Slate, 全局多样性+公平
  ▼
几十   ⑤ 业务策略           强插/广告/打散/限频
  ▼
最终曝光(~20)
```

**为什么是漏斗**：① 算力（精排太重，不能跑亿级）；② 特征（重特征只在精排有）；③ 目标不同（召回求不漏，精排求排准，重排求全局优）。

## 核心论文清单

### 召回
- DSSM (Huang et al., CIKM 2013)
- YouTube DNN (Covington et al., RecSys 2016)
- Sampling-Bias-Corrected (YouTube 2019) — logQ 修正
- MIND (Li et al., CIKM 2019) — 多兴趣
- SASRec (Kang & McAuley, ICLR 2018)
- PinSage (Ying et al., KDD 2018) / LightGCN (He et al., SIGIR 2020)
- TIGER (Rajput et al., NeurIPS 2023) — 生成式检索 ⭐

### 精排
- FM (Rendle, ICDM 2010)
- Wide&Deep (Cheng et al., DLRS 2016) / DeepFM (Guo et al., IJCAI 2017)
- DCN / DCN-V2 (Wang et al., 2017/2021) / xDeepFM (Lian et al., KDD 2018)
- DIN (Zhou et al., KDD 2018) / DIEN (AAAI 2019) / BST (DLP-KDD 2019) / SIM (CIKM 2020)
- MMoE (Ma et al., KDD 2018) / PLE (Tang et al., ACM MM 2020) / ESMM (SIGIR 2018) / PEPNet (KDD 2023) ⭐

### 重排
- DPP 在推荐 (Chen et al., 2018) / Fast-DPP (Wilhelm et al., 2018)
- Seq2Slate (Bello et al., 2019) / PRM (Pei et al., RecSys 2019)

### 评估与因果
- CUPED (Deng et al., KDD 2013) / Interleaving (Chapelle et al., CIKM 2012)
- Unbiased Recommendation 综述 (Li et al., 2022+) ⭐

### 前沿
- P5 (Geng et al., RecSys 2022) — LLM 统一推荐
- Recformer (Li et al., EMNLP 2023) / Agent4Rec (Zhang et al., 2023-2024) ⭐

## 学习路线（8 周）

| 周 | 主题 | 实验 |
|----|------|------|
| 1 | CF 基础 (MF/BPR/ALS) | MovieLens + ALS |
| 2 | 双塔召回 (DSSM) | `01` 双塔 + Faiss 检索 |
| 3 | 序列召回 (SASRec) | 复现 SASRec |
| 4 | 图召回 (LightGCN) | LightGCN on MovieLens |
| 5 | 精排特征交互 (DeepFM) | `04` DeepFM + Criteo |
| 6 | 序列精排 (DIN/SIM) | `01` DIN target attention |
| 7 | 多任务 (MMoE/PLE/ESMM) | `01`+`04` 复现 seesaw |
| 8 | 重排+前沿 (DPP/TIGER) | `02`+`03`+`04` 语义 ID |

## 练习题

- 🟢 **基础**：写出 FM 二阶交叉的 $O(kn)$ 恒等变形推导；解释为什么双塔中间不能 cross。
- 🟡 **进阶**：在 `04` 中把 IVF 的 `n_probe` 从 2 调到 16，画 n_probe-召回率-速度权衡曲线。
- 🔴 **挑战**：实现简化版 SIM（GSU 类别匹配检索长历史 + ESU DIN 精排）。
- 🟣 **研究**：复现 TIGER 的 RQ-VAE 语义 ID（不只是 KMeans）。
- 💡 **批判**：用 5 个工程约束（延迟/成本/规模/反馈/评估）反驳"LLM 3 年内取代推荐模型"。

## 备注

- 论文检索接口今日（2026-08-14）不可用，前沿部分基于领域知识整理，⭐ 标注的较新条目细节建议核对最新 arXiv。
- 代码为教学最小实现，生产化需补充：分布式训练、特征平台、在线离线一致性、流式更新、监控告警。

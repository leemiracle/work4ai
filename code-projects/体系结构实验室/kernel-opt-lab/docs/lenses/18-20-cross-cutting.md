# 视角 18-20：法律/伦理/ESG 三视角综合（Cross-Cutting Lenses）

> **审查时间**：2026-06-30
> **审查者**：3 个 councillor delegate（calm-indigo-badger / eager-azure-raven / lively-coral-fox）
> **说明**：token 限制下，本文件聚合三视角的**核心发现**，完整报告在 delegate 结果中。

---

## 视角 18：知识产权/法律专家（IP Lawyer）

**视角定位**：半导体专利 + 开源许可证 + 技术出口管制。专长的看点是"算子库作为开源/商用资产的法律可流通性"。

**关键盲区**：
1. **无 LICENSE 文件**（git 扫描确认）——若选 MIT/Apache，需附加**"出口管制例外条款"**（参照 Google AOSP / oneDNN 做法：明示受 EAR 约束、禁止向被制裁实体再分发）
2. **PhyGCC GPL v3 传染性**——任何静态链接 PhyGCC 编译产物的分发触发 GPL 义务，下游闭源商业产品（信创政务云、车载）= 合规雷区
3. **Winograd 经典专利（Lavin & Gray 2016）已过期**，FlashAttention (Tri Dao) 是 BSD License，使用相对安全
4. **飞腾在 entity list 后软件出口合规**——任何含美国技术超 de minimis 的物项禁止向飞腾输出，本项目对外发布需明确 ECCN 分类 + 最终用户声明
5. **"飞腾"/"D3000"/"FTC862" 商标使用授权**未声明
6. 缺 NOTICE、CONTRIBUTORS、CODE_OF_CONDUCT 三件套

**P0 建议**：
- 加 `LICENSE`（建议 Apache-2.0 + 出口管制例外条款）
- 加 `NOTICE` + `CONTRIBUTORS.md`
- 新增 `docs/IP-POLICY.md`：专利风险（NEON intrinsics 是否触及 NVIDIA/ARM 专利）+ PhyGCC GPL 边界

**核心洞察**：**算子库作为信创开源项目最大的法律资产是"防御性专利 + OIN 加入"**。本项目作为飞腾生态开源样本，建议加入 Open Invention Network（OIN，Linux 专利共享池）获得专利保护伞。

---

## 视角 19：AI 伦理/治理专家（AI Ethics & Governance）

**视角定位**：参与过 UNESCO AI 伦理建议书 + 中国《新一代人工智能伦理规范》起草。看算子库作为"AI 基础设施"的政治性和伦理性。

**关键盲区**：
1. **无伦理审查声明**——算子库既能跑医疗 LLM 也能跑监控/军事，是否需要双用途审查机制
2. **算力主权叙事**：飞腾 + 麒麟作为"国产算力主权"的伦理正当性（vs 全球化开源）
3. **AI 治理合规**：欧盟 AI Act、中国《生成式 AI 服务管理暂行办法》、美国 NIST AI RMF 对底层算子库的连锁要求
4. **Jevons Paradox（反弹效应）**——更快的 GEMM 让模型更大，能耗反增，违背可持续 AI
5. **数字鸿沟**：高性能算子库开源/闭源对中小开发者的影响
6. **不可解释性风险**：NEON 优化是否引入了"不可解释"的数值漂移（FP16 累加 bug 即典型）
7. **无偏见测试**：算子精度对 LLM 输出公平性影响（INT8 量化在不同群体语料上的差异）

**P0 建议**：
- 新增 `docs/ETHICS-STATEMENT.md`：双用途边界声明 + 算力主权伦理正当性论证
- 新增 `docs/DUAL-USE-ASSESSMENT.md`：双用途风险评估矩阵（医疗/教育 = 低风险，监控/军事 = 高风险）
- README 加伦理免责声明

**核心洞察**：**算子库作为"中立基础设施"的真实政治性**——本项目作为飞腾 + 麒麟生态项目，必然带有"国产替代"政治叙事，需要在伦理声明中**诚实承认这层政治性**而非假装中立。中国 AI 治理合规对底层算子的连锁要求（生成式 AI 办法第 4 条要求"算法机制可解释"）会反向要求算子精度可追溯。

---

## 视角 20：可持续性/ESG 专家（Sustainability & ESG Analyst）

**视角定位**：半导体行业 carbon footprint + 绿色计算。看算力优化的能耗效率、碳足迹、ESG 合规。

**关键盲区**：
1. **GFLOPS/W（性能 watt 比）未测**——D3000 无 RAPL/INA226 功耗采集，但可用 fan RPM + 温升斜率反推
2. **碳足迹模型缺失**——单次推理的 gCO2e、训练大模型的全生命周期碳排放
3. **DVFS 智能调度的节能潜力未量化**——`lens-thermal` 显示 governor 已锁 performance，但未测 powersave/governor 切换的节能空间
4. **Green500 对标缺失**——HPC 行业绿色基准
5. **电子废弃物**：FTC862 EOL 回收、稀土元素（FTC862 已停产，存量设备的循环经济）
6. **流片 fab 水耗**：TSMC 每片晶圆 ~2200 加仑超纯水（FTC862 已流片，但下一代用国产 fab 水耗更高）
7. **未跑 MLPerf Energy benchmark**
8. **未考虑 silver bullet**：算法碳排 > 硬件碳排，算子优化的真实减排贡献

**P0 建议**：
- 新增 `analysis/lens-energy.c`：用 fan RPM 上升斜率 × FVU 指令密度反推 FVU 单元 mW/FLOP
- 新增 `analysis/lens-carbon.c`：基于中国电网 0.58 gCO2/kWh 算单次 LLM 推理碳足迹
- 新增 `docs/ESG-REPORT.md`：FTC862 跑 LLM 推理的可持续性报告（GFLOPS/W + 碳足迹 + EOL）

**核心洞察**：**算子优化对"可持续 AI"的真实贡献常被高估**——把 GEMM 从 60% 效率提到 92%，但用户立刻把模型从 7B 升到 70B，**绝对能耗反而上升**（Jevons Paradox）。诚实的 ESG 叙事应承认这点，强调"性能密度提升让单设备做更多事"而非"节能"。**4 核 tiled 143 GFLOPS vs 8 核 flat 97 GFLOPS** 是真正的 ESG 优势——同样 GFLOPS 用更少核 = 更低 fan RPM = 更适合无主动散热的边缘部署。

---

## 三视角交叉共识

| 共识点 | 法律 | 伦理 | ESG |
|---|---|---|---|
| 缺 LICENSE/合规章节 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 双用途/出口管制 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| PhyGCC GPL 风险 | ⭐⭐⭐ | — | — |
| Jevons Paradox | — | ⭐⭐ | ⭐⭐⭐ |
| 算力主权政治性 | ⭐⭐ | ⭐⭐⭐ | ⭐ |

**三视角共同 P0**：补齐 `LICENSE` + `docs/ETHICS-STATEMENT.md` + `docs/ESG-REPORT.md` 三件套，让项目具备**法律可流通 + 伦理可声明 + ESG 可披露**的最低门槛。

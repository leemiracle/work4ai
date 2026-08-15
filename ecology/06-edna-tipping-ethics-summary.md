# 第六篇（终篇）：eDNA 流水线 · 9 大地球临界要素 · 生态伦理深辩 · 补充 · 全局总结

---

## 二十三、eDNA / 宏基因组完整分析流水线

```
环境样本(水/土/空气)
   │ 1. 采样 (replicate, 体积标准化)
   ▼
DNA 提取 (DNeasy PowerSoil 等) → Qubit/NanoDrop 质控
   ▼
PCR 扩增条形码区
   │ 引物: 动物 COI(Leray-XT)/16S; 细菌 16S V3-V4;
   │       真核 18S V4; 真菌 ITS1/ITS2; 植物 rbcL/matK/trnL
   ▼
高通量测序 (Illumina 双端 / Nanopore 长读)
   ▼
[生物信息学]
   5. 质量过滤: fastp / Trimmomatic (Q>30)
   6. 引物切除: cutadapt
   7. 双端合并: vsearch --fastq_mergepairs
   8. ★ ASV 去噪: DADA2 (误差模型, 单碱基分辨率) / UNOISE3
   9. 去嵌合体: vsearch --uchime_denovo
   10. ★ 分类: BLAST / SINTAX / RDP Classifier(朴素贝叶斯)
       库: GenBank, BOLD(COI), SILVA(16S/18S), UNITE(ITS), MIDORI
   ▼
[群落统计]
   11. rarefaction 稀疏化
   12. α 多样性: Shannon / Simpson / Chao1 / Faith PD (picante)
   13. β 多样性: Bray-Curtis / UniFrac(需系统发育树)
   14. 排序: NMDS / PCoA / RDA / CCA (vegan)
   15. 差异: DESeq2 / ANCOM-BC
   ▼
物种存在/丰度表 → 生态解读
```

**关键算法点**：
- **DADA2**：自举误差模型区分测序误差与真实变异，ASV 取代 97% OTU
- **RDP Classifier**：朴素贝叶斯 + 8-mer 频率层级分类
- **UniFrac**：基于系统发育树分支长度的 β 多样性
- **Shotgun 宏基因组**：MEGAHIT/SPAdes 组装 → MetaBAT2 binning → MAG；功能注释 KEGG/COG

---

## 二十四、9 大地球临界要素（Lenton et al. 2008/2019）

| # | 要素 | 阈值 | 后果 |
|---|------|------|------|
| 1 | 亚马逊雨林 | 砍伐 20-25% + 升温 3-4°C | 萨瓦纳化, 释放 ~100 GtC |
| 2 | AMOC | 淡水注入 | 崩塌→欧洲降温、季风扰乱 |
| 3 | 格陵兰冰盖 | 1.5-3°C | 不可逆融化→海平面+7m |
| 4 | 西南极冰盖 | 海洋变暖 | 崩溃→+3m |
| 5 | 永冻土 | 升温 | 甲烷释放正反馈 |
| 6 | 季风(西非/印度) | 气溶胶/温度 | 失稳→粮食危机 |
| 7 | 珊瑚礁 | 1.5°C | 白化、钙化崩溃 |
| 8 | 北极海冰 | 升温 | 反照率反馈 |
| 9 | 北方针叶林 | 升温/火 | 南退、碳释放 |

**级联**：格陵兰→淡水→AMOC 减弱→亚马逊干旱；永冻土→升温→加剧全部。"全球多米诺"使 1.5°C 目标紧迫。2022 *Science*：1°C 已使 5 个要素进入不确定区间。

---

## 二十五、生态伦理深辩：整体主义 vs 个体主义

**案例**：黄石 1995 重引入狼——救生态系统，但狼杀麋鹿（个体痛苦）。

- **整体主义（Leopold 土地伦理）**："当整体稳定、美丽、完整时即正当。"可牺牲个体保系统——保护生物学主流操作伦理。
- **个体主义（Singer 功利 / Regan 权利）**：每个有感受力的个体有不可侵犯的内在价值——反狩猎、动物解放的根基。
- **调和**：Turner 中间道路；Rolston 分层价值论；实践妥协（人道控制入侵种）。
- **深层生态学（Næss 1973）**：生物圈平等主义 + 自我实现。
- **生态女性主义（Warren/Merchant）**：统治逻辑同时压迫女性与自然；批判机械自然观。
- **环境实用主义（Norton）**：搁置形而上分歧，适应性管理。

---

## 二十六、补充主题（求全）

- **MET 争议**：3/4 律小尺度偏差、分形机制简化批评
- **中性理论现代版**：Vellend 高维生态位融合；Portal 长期数据的漂变实证
- **宏生态学（Brown 1995）**：纬度多样性梯度 LDG（时间假说/能量-水假说/Rapoport 法则）
- **生态位构建（Odling-Smee）**：生物改造环境反馈影响选择——延展进化合成 EES
- **微生物组生态学**：人体/肠道/根际——宏生态概念直接迁移
- **城市生态学**：热岛、人造光、Urban Wildlife
- **恢复生态学**：reference ecosystem、novel ecosystems 接纳之争
- **PVA 过度自信批判**（Ellner-Fieberg-Mlstrup：必须报告不确定度）

---

## 二十七、全局总结

**三句话**：
1. **层级 + 涌现 + 尺度**——错尺度 = 错结论。
2. **复杂性双刃剑**：随机复杂失稳（May）；结构化复杂稳定+保险（弱连/嵌套/模块）。
3. **人类世**：临界点逼近；EWS（Var↑/AR1↑）是生态学的方法论礼物；地球边界 9 越 6。

**知识图谱**：
```
                    生态学 = 尺度 + 联结 + 进化
        ┌──────────────┼──────────────┐
     数学模型        理论            方法/技术
 逻辑斯谛/混沌    May稳定性       eDNA/DADA2
 Leslie矩阵λ1     Scheffer临界点   宏基因组/MAG
 LV/功能反应      Hamilton rB>C    SDM(MaxEnt/RF)
 May-Wigner       ESS/适应性动态   捕获重捕CJS
 边际值定理       Hubbell中性      遥感/CNN/BioCLIP
 EWS(Var/AR1)     Leopold/TEK      UniFrac/Shannon
 排序(NMDS/RDA)   地球边界         PVA/弹性分析
```

---

## 二十八、学习路径

- 📐 **理论**：May《Stability and Complexity》→ Tilman R\* → Hubbell → Scheffer《Critical Transitions》
- 💻 **建模**：Python/R 实现逻辑斯谛、Leslie、LV、EWS、May 判据（本存档 experiments/ 全部可复现）；R 包 deSolve/vegan/ade4/picante
- 🧬 **方法**：DADA2 流水线 → MaxEnt SDM → 相机陷阱 CNN
- 🌍 **全球**：Rockström 地球边界、IPBES、IPCC 临界点章节
- 🧭 **伦理**：Leopold《沙乡年鉴》、Næss、Kolbert《第六次灭绝》、Raworth《甜甜圈经济学》

## ✍️ 自测题

1. 为什么海洋占地球 70% 但 NPP 总量低于陆地？
2. May"复杂→不稳"与 Elton"多样→稳"如何调和？
3. 湖泊稳态转换前时间序列会出现哪 3 个 EWS？为什么？
4. Hamilton 规则如何解释膜翅目真社会性？
5. eDNA 的假阴性主要来源？
6. 一句话向政策制定者解释 ecological resilience vs 工程 resilience。

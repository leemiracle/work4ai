# 08 · 多模型 harness：Router、Cascade 与端点路由

> **核心论点**：harness 的 provider 层从"一个模型"变成"一组模型"时，模型选择本身成为 harness 的组成部分。
> **本文是什么**：路由/级联的工程决策 + 端点实测 + 多模型下的 C 组件新约束。

---

## 🗺️ 三阶段全景（Ensemble 综述 v6 修正版，arXiv:2502.18036）

```
(a) 推理前路由（省钱的预判）
    (a1) 离散效用：分类"哪个模型能答好" → Hybrid-LLM（ICLR 2024，DeBERTa 路由，40% 少调大模型无质量损失）
    (a2) 连续效用：回归/策略学习效用值 → OmniRouter、LLM-Bandit
(b) 推理中融合（最细粒度，需 logits——API 模型基本不可用）
    token/span/process 级：DeePEn、CDS（critical token 路由）、LE-MCTS
(c) 推理后整合
    (c1) 非级联：投票/相似度选择/LLM-Blender 式选后重生成；Smoothie（免标签，嵌入质心距离）
    (c2) 级联：置信度不达标就升级 → FrugalGPT（TMLR 2024，98% 降本上限）
```

**工程速断**：
- API-only 场景 → (b) 出局（拿不到 token 概率）
- EM-G 任务（可精确判对错：数学/代码/抽取）→ cascade 好写，先上
- OE-G 任务（开放生成）→ 评分难，router 或 Smoothie
- **组合最优**：cascade routing = 预判 + 后验止损对冲（Dekoninck et al. 证明的最优框架）

---

## 🛠️ 端点路由实测（本机 2026-08-17，GLM Coding Plan）

多模型不只是算法问题，**同一个 key 在不同端点能调的模型不同**：

| 端点 | glm-4-flash | glm-5.3 |
|---|---|---|
| `api/paas/v4`（普通）| ✅ 免费 | ❌ err 1220 无权限 |
| `api/coding/paas/v4`（coding plan）| — | ✅（积分计费：input 6.9 / cached 1.7 / output 24）|

```bash
export ZHIPU_CODING_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"  # glm-5.3/5-Turbo/4.7
export ZHIPU_BASE_URL="https://open.bigmodel.cn/api/paas/v4"                # 免费档
```

生产含义：**provider 抽象层要把"模型→端点→key 权限→计费"四元组一起路由**，不是只有 model name。GLM-5.3 目前仅 Coding Plan 入口（独立 API "即将上线"），权重两周后开源。

**成本优化三层渐进**（从零成本到投资）：
1. 置信度 cascade（无监督，一天上线，40-80% 降本）
2. Smoothie 免标签路由（多任务混合流量）
3. 训练 router（Hybrid-LLM 式，300M 编码器 + 10K 标注）

**防 routing 事故三铁律**：风险不对称时难判样本默认升级；模型池变更必须重评估 router；评分函数对齐业务指标而非代理指标。

---

## 🧩 多模型下 C 组件的新约束（单模型手册不会告诉你的）

| 约束 | 来源实证 | 对策 |
|---|---|---|
| 各模型窗口不同 | Letta 按模型分五档（5K/15K/25K/40K chars）| 上下文预算参数化 per-model |
| 压缩摘要由谁做 | fork 场景：便宜模型压缩 + 贵模型执行 | 压缩器也是路由对象 |
| thinking 字段格式不同 | GLM reasoning_content / Kimi reasoning_content / GPT 无 | 适配层统一（09 章）|
| 缓存前缀因模型而异 | prompt cache 按模型独立 | fork 子代理选同模型才能共享缓存 |

---

## 📐 决策树（你的系统怎么配）

```
流量大、查询难度可预判 ──────────→ Router（a 类）：分类路由
流量大、难度不可预判、可后验 ─────→ Cascade（c2）：置信度级联
两者都要 ───────────────────────→ Cascade Routing 组合
要 accuracy 且预算足 ────────────→ 投票 + LLM judge（c1）
自托管开源、要事实性 ────────────→ token 级 CDS（critical token 路由）
关键生产、错误代价不对称 ─────────→ 只降级容易判的，其余全走大模型
```

---

## 📌 本周必做

1. [ ] 用免费 glm-4-flash + coding 端点 glm-5.3 搭一条最小 cascade（置信度阈值切换），实测降本比
2. [ ] 检查你的 provider 层是否把端点/权限/计费硬编码死了

## 📚 推荐深读

- FrugalGPT（arXiv:2305.05176）/ Hybrid-LLM（arXiv:2404.14618）/ Smoothie（arXiv:2412.04692）
- RouterBench（arXiv:2403.12031，405k 推理结果的基准）
- [harness三综述合并解析](../../harness三综述合并解析.md) §1.6-1.7 / §2.4

---

**版本**：v1.0（2026-08-17）
**核心隐喻**：多模型 harness 像医院分诊台——Router 是预检护士（先看哪个科），Cascade 是逐级转诊（社区医院看不了转大三院），级联的止损是"别让小医院自信地治死"。端点路由是"医保目录"——同一个病人，不同卡能挂不同科。

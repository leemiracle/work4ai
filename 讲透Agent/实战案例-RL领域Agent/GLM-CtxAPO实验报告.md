# GLM-CtxAPO 实验报告：context 技术在最优 prompt 之上还有多少增益

> **日期**：2026-08-17 · **模型**：glm-5（coding-plan 套餐，thinking 默认开）· **调用**：24 次（4 臂 × 6 题）
> **脚本**：[glm_ctx_apo.py](./glm_ctx_apo.py) · **前置**：[GLM-APO实验报告](./GLM-APO实验报告.md)（RCF 最优 system，16/16）
> **对应**：rl_agent v3 toy Ctx-APO 的**真模型版**——回答"手册 06/12 的 context 技术，在已最优的 prompt 上还能加多少分"

---

## ★ 一句话结论

**RCF 已近饱和，context 技术的收益不在总分，在"改变错哪些题"与"推理成本"**：few-shot 有害（4/6，思考 token ×2.4），bookend/分隔符平分但分歧题互补，分隔符省 18% 思考 token。

## 实验设计

| 要素 | 设计 |
|---|---|
| 底座（固定） | RCF 最优 system（GLM-APO v1 产出，决赛 16/16） |
| 臂（变异对象） | ctx0 base=RCF 原样 / ctx1 +1 条同类 few-shot / ctx2 bookend（任务后重申约束）/ ctx3 `###` 分隔符 |
| 题集 | 16 题选 6：math#2(9.8vs9.11) math#3 json#4 code#8 know#12 know#15（v1 脆弱题优先） |
| 测量 | 对错（RLVR 判分）+ reasoning_tokens（context 是否影响推理预算分配） |

## 结果（24 次调用全记录于 glm_ctx_apo.log）

| 臂 | 对错 | 平均思考 token | vs base |
|---|---|---|---|
| ctx0/base | 5/6 | 683 | — |
| ctx1/+shot | **4/6** | **1671** | **掉分 + 成本 ×2.4** |
| ctx2/+bookend | 5/6 | 966 | 平局，成本 +42% |
| ctx3/+split | 5/6 | **561** | 平局，**成本 -18%** |

配对分歧（仅 know 类，2 题）：know#12 base✅shot❌bookend❌split✅；know#15 base❌shot❌bookend✅split❌——**位置/结构技术改变的是错误分布，不是总分**。

## 三条发现（比"全都有益"值钱）

1. **few-shot 在思考模型上有害**——手册 02"S 要素 5-10 条最佳"被一手实测推翻于 GLM-5：例子把知识题带偏（know#12 base 对 shot 错）+ 推理预算翻 2.4 倍。与手册 12 章"旗舰思考模型 0-3 条"的论断互证：**思考模型的 CoT 已内化，外显例子反而干扰推理路径并稀释注意力**。
2. **bookend/split 与 base 平局但分歧互补**——6 题样本不足以判显著（诚实标注），但方向与手册 06 的 lost-in-middle 论断一致：位置技术影响的是"哪些位置的信息被读到"。
3. **`###` 分隔符是最便宜的 context 优化**：同分下省 18% 思考 token——结构化让模型更快定位任务边界，减少"解析 prompt 结构"的推理开销。

## 教训

- **"最优 prompt"之后下一层杠杆是 context 结构**——但收益形态从"分数"变为"错误分布 + 成本"，评估指标必须跟着变（只看对错会漏掉 18% 的成本差）。
- GLM-5 的 reasoning_tokens 是 context 敏感的（561~1671，3 倍波动）——**context 结构是推理预算的旋钮**（v1 发现③的加强版）。

## §审查（v3.1 五角色二审记录）

对 rl_agent v3 增量的审查（oracle/security/councillor/performance-analyst 四 subagent + 主审计），修复情况：

| 级别 | 问题 | 修复 |
|---|---|---|
| P0 | **eval 隔离是假的**：persist=False 只挡 Q 表，评估期内 kb_curate/reflect/append_progress 仍写盘 → 跨变体 KB 漂移 | solve 内三处写盘全部按 `brain.persist` 门控（oracle） |
| P0 | **塑形必然"全关"退化**：混合分允许省成本盖过掉分（0.92→0.94 实为 2×0.01 纯成本分） | 改字典序 (reward, -cost) 元组比较——reward 不降才允许省成本（oracle） |
| P1 | ev_txt[:400] 截断致 grpo 类长输出漏固化 | 判据用完整 obs |
| P1 | kb_curate 只清 _KB_CACHE 不清 _SEARCH_CACHE → "下次可检索"对已缓存查询失效 | `_SEARCH_CACHE.clear()` |
| P1 | **CTX_F 只写不读**（进化成果孤儿，v2 "--sc 虚构"同型债） | `load_ctx()` + ACTIVE_CTX + harness_init 读回（实测第二轮 ctx 生效） |
| P1 | 卡片正文可被 task 文本投毒（换行/markdown 注入，幂等首写=持久投毒） | 内容净化（去换行/markdown 符号）+ 卡内加"⚠️ 自产证据"自标记（security） |
| P1 | glm_ctx_apo.py 半孤儿；glm_apo_eval6.py 未挂 | 均挂进 README 快速开始（councillor） |
| P2 | 母宇宙 README/AGENTS.md "716 行/24 项"过期；demo 时间矛盾 | 统一 829+ 行/30 项/~2.4s |

**修复后复跑**：demo 2.4s 战报 5.0/6 不变；Ctx-APO 语义变化——基线 reward 0.92→**1.00**（eval 隔离修复后不再被 lessons 污染），采纳轨迹 `reward=1.00 cost 0.07→0.06`（诚实的 Pareto：reward 不降才省成本）。

## 复现

```bash
python3 glm_ctx_apo.py --dry   # 变换自检（零调用）
python3 glm_ctx_apo.py         # 24 次真跑（~7min，含思考）
cat glm_ctx_apo.log            # 全记录
```

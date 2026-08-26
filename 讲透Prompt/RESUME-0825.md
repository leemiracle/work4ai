# RESUME-0825 —— 讲透Prompt 单元断点（已归档，见 RESUME-0826.md 完成档案）

> ⚠️ 本文件的"明日执行清单"已于 2026-08-26 全部执行完毕，单元完成。现行状态以 `RESUME-0826.md` 为准，下文仅存档。

## 一、已完成（勿重做）

### 素材层（全部就绪）
- **源站存档**：`_source/` 共 44 页 MDX（zh 35 + en 9）。抓取通道：`gh-proxy.com/https://raw.githubusercontent.com/dair-ai/Prompt-Engineering-Guide/main/pages/...`（zh 缺的页用 .en.mdx，如 guides_reasoning-llms.en.mdx 是模型适配章金矿）
- **论文核实**：25 篇 arXiv ID 已逐一直接核实（2201.11903 CoT / 2210.03629 ReAct / 2309.03409 OPRO / 2211.01910 APE / 2305.10601 ToT / 2205.11916 ZeroCoT / 2211.10435 PAL / 2303.09014 ART / 2302.11520 DSP / 2302.00923 MM-CoT / 2210.03493 AutoCoT / 2311.11482 MetaPrompting / 2505.11423 推理伤指令跟随 / 2505.05410 / 2505.10185 CoT百科 / 2504.21233 Phi-4-mini 等）。**未核实 6 个**（2312.11562/2402.18272/2010.15980/2101.00190/2001.08361/1706.03741）→ 章节里标注"据指南引用"即可，勿凭记忆补标题
- **Google Cloud**：websearch 拿到全文（cloud.google.com 直连被墙）。关键素材：Gemini 平台 prompt 组件表（Objective/Instructions/Constraints/Tone/Few-shot/Reasoning steps/Recap）+ "Thinking vs Reasoning：用 thinking 模型时删掉手写 step-by-step"——这是 08 章模型适配的关键证据
- **前沿检索（已到手，写 10 章直接用）**：
  - ACL 2026 Findings: Prompt 词汇敏感性 132k 变体，稳定性 Scaling Law，领域术语+行动指令=两大稳定支柱（aclanthology.org/2026.findings-acl.2084）
  - arXiv 2608.18539: 交互分解视角的 prompt 敏感性——SFT/规模/dense/few-shot 四因素降敏
  - arXiv 2608.03401: reasoning 接口评估（concise/early-answer 指令 vs gpt-oss effort 设置）
  - arXiv 2604.18897: 单 prompt 天花板（SAIR 竞赛 45+ 变体，Pareto 前沿，合并=均值非最大）→ 数学章核心素材
  - ACL 2026: Lost in the Prompt Order（CQO vs QOC 14pp 差距，因果注意力机制解释）→ 08 章素材
  - Springer 2026: 数学教育 prompt 研究（4 模型×4 技术×2880 解，Persona 七倍提升过程性质量）→ 11 章素材
  - 完整前沿搜索结果存 `~/.local/share/opencode/tool-output/tool_037fc0214001nFuto2xMWshPAX`（截断长文，可用 Read/Grep 挖）

### 实验层
- `experiments/common.py`：三通道验证通过（本地 Qwen2.5-0.5B / glm-4-flash / glm-5 thinking off）。含贪心解码 num_return 兼容补丁
- **E1 参数实验 ✅**：temp 0.0/0.7/1.5 → 开放生成互异 1/12/12；翻译正确率 100% 全档；top_p=0.1 在 temp=1.2 下强行拉回互异 1/12（核采样压过温度）。json+png 已落
- **E2 few-shot ✅**：k 曲线 Qwen k0=0%→k1=80%→k2+=90%；glm-4-flash k0=55%→k1+=95%；**随机标签消融：Qwen 75%（掉 15pp，格式+标签都看），glm 100%（无视标签只用格式）**——Min et al. 2022 在大模型上更极端成立。json+png 已落
- **E3 CoT ⏸**：脚本就绪未跑成（两次进程意外：nohup 被 timeout 连坐+一次用户中断。教训：长实验直接前台跑 timeout 给足 1500s+）

## 二、明日执行清单（按序）

1. **跑 E3**：`cd 讲透Prompt/experiments && timeout 1500 python3 e3_cot.py`（四条件×2模型×10题，~8min）
2. E4 Self-Consistency（glm-4-flash n=1/3/5/9 投票，妹妹年龄题+算术题）
3. E5 PAL（生成 Python 并 exec，日期题改造）
4. E6 ToT 24点 BFS vs CoT 基线（API）
5. E7 ReAct 最小循环（计算器工具）
6. E8 对抗：injection/泄露+防御消融
7. **E9 模型适配★**：同 prompt × {Qwen-0.5B, glm-4-flash, glm-4.7, glm-5(默认), glm-5(thinking off)} 矩阵，重点验证：few-shot 对小模型救命/大模型可省；手写 CoT 对 thinking 模型是否负作用（对照 2505.11423）；chat template 实测
8. **E10 自动优化★**：OPRO 最小自实现（元提示循环优化情感分类指令，glm-4-flash 当优化器+执行器）；DSPy 探索（pip 装，失败则手写 BootstrapFewShot 等价）
9. **E11 数学★**：GSM8K 8题×prompt策略矩阵×2模型；Persona 教学模板；Lean/Prover prompt（复用 实战案例-Prover数学Agent/prompts.py）
10. 写章节 00-12（README 篇目表已定；08/09/10/11 是重点章，每章嵌实验数字）
11. 挂网：讲透Agent 主README + prompt工程手册互链 + 记忆更新 + exercises/

## 三、关键坑（记住）

- GLM API：`~/.local/share/opencode/auth.json` 取 key；glm-5.3 无权限（错误1220），最高档 glm-5（默认开 thinking）；paas 端点 glm-4-flash/glm-4.7/glm-5 可用
- 本地 Qwen：thread=1；贪心解码不能 num_return>1（common.py 已兼容）
- arXiv 直连会被限流（429），核实用 abs 页单发+sleep 3s；export.arxiv.org 也被墙
- cloud.google.com 直连失败，用 websearch 抓
- 服务器网络间歇中断（08-24/25 都发生过）：明日跑长实验若中断，按幂等重跑

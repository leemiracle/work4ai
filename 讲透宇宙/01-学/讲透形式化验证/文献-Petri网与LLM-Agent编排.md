# 形式化方法文献清单 · 侧线：Petri 网 × LLM Agent 编排

> 与《LTL/LTLf 反应式综合》清单并列归档。核验日期：2026-09-06；核验方式：DBLP 公开检索 API 逐条确认（✅DBLP = 已确认存在对应 dblp.org/rec 条目；❌DBLP = DBLP 暂未收录，附官方出版页）。

## Petri 网 × LLM Agent 编排 / BPM 生成（Formal-LLM 线、ProMoAI 线、BPM 系）

脉络：理论底座是 van der Aalst (1998) 把工作流装进 Petri 网（WF-net 与 soundness）；BPM 圈 2023 年起系统引入 LLM（Vidgof–Mendling 议程文 + Grohs 等的 GPT-4 基线）；工程管线由 Aalst–RWTH 系打通——POWL 作为 LLM 可生成的中间表示（编译为 Petri 网），ProMoAI (IJCAI 2024) 串起"LLM 生成 → 过程挖掘修复 → 形式验证"闭环；同期 Formal-LLM 把高级 Petri 网用作 LLM agent 的行为轨道（前向/后向变迁、工作流可达性可判定）；外围延伸：PNoT 用 Petri 网做结构化提示（Petri 版思维链）、SyncPetri 用资源流引导 LLM 生成并发测试、Busch–Leopold 基准补上评测环节。与 LTL 反应式综合线（Strix 系）的分工：要"系统自动生成策略"找 LTL 综合，要"钉死流程、LLM 只准在轨道内发挥"找 Petri 网。

The Application of Petri Nets to Workflow Management | Wil M. P. van der Aalst | J. Circuits Syst. Comput. 1998 | 理论基石：WF-net（工作流网）与 soundness——"用 Petri 网描述工作流"的开山之作，本线一切工作的共同祖先 | https://dblp.org/rec/journals/jcsc/Aalst98 | ✅DBLP

Large Language Models for Business Process Management: Opportunities and Challenges | Maxim Vidgof, Stefan Bachhofner, Jan Mendling | BPM 2023 | BPM×LLM 议程设定文：LLM 放进 BPM 生命周期各阶段的机遇/风险地图 | https://dblp.org/rec/conf/bpm/VidgofBM23 | ✅DBLP

Large Language Models Can Accomplish Business Process Management Tasks | Michael Grohs, Luka Abb, Nourhan Elsayed, Jana-Rebecca Rehse | BPM Workshops 2023 | 系统评测 GPT-4 在 BPM 七类任务（含过程模型生成）上的能力基线 | https://dblp.org/rec/conf/bpm/GrohsAER23 | ✅DBLP

POWL: Partially Ordered Workflow Language | Humam Kourani, Sebastiaan J. van Zelst | BPM 2023（扩展摘要版 IJCAI 2024） | ProMoAI 的形式底座：可编译为 Petri 网的工作流语言——LLM 生成的目标中间表示 | https://dblp.org/rec/conf/bpm/KouraniZ23 | ✅DBLP

ProMoAI: Process Modeling with Generative AI | Humam Kourani, Alessandro Berti, Daniel Schuster, Wil M. P. van der Aalst | IJCAI 2024 | LLM 生成 POWL → Petri 网过程模型，再用过程挖掘工具修复+验证的完整管线 | https://dblp.org/rec/conf/ijcai/KouraniB0A24 | ✅DBLP

Formal-LLM: Integrating Formal Language and Natural Language for Controllable LLM-based Agents | Zelong Li, Wenyue Hua, Hao Wang, He Zhu, Yongfeng Zhang | CoRR 2024 (abs/2402.00798) | 高级 Petri 网做 agent 工作流轨道：前向/后向变迁支持失败回退，工作流可达性可判定（开工前即知 agent 能否到达目标） | https://dblp.org/rec/journals/corr/abs-2402-00798 | ✅DBLP（注意：DBLP 仅见 CoRR 版，未见正式会议/期刊版）

Petri Net of Thoughts: A Structure-Enhanced Prompting Approach for Process-Aware Artificial Intelligence | Aleksandar Gavric, Dominik Bork, Henderik A. Proper | EMISA 2025 (GI LNI P-362, pp. 105-110) | Petri 网版"思维链"：用过程发现技术引导 LLM 的结构化推理（顺序/并发/决策显式建模） | https://dl.gi.de/handle/20.500.12116/46250 （DOI: 10.18420/EMISA2025_15） | ❌DBLP（LNI EMISA 2025 卷暂未被 DBLP 收录，附 GI 官方页）

From Resource Flow to Executable Tests: Petri-Net-Guided LLM Test Generation for Concurrent Stateful Rust APIs | Kaiwen Zhang, Guanjun Liu | CoRR 2026 (abs/2607.21530) | SyncPetri：Petri 网资源流语义引导 LLM 生成并发有状态 API 的可执行测试 | https://dblp.org/rec/journals/corr/abs-2607-21530 | ✅DBLP

Towards a Benchmark for Large Language Models for Business Process Management Tasks | Kiran Busch, Henrik Leopold | HICSS 2025 | BPM 任务 LLM 基准：为"LLM 建过程模型"这一能力提供标准化评测 | https://dblp.org/rec/conf/hicss/BuschL25 | ✅DBLP

Bridging Domain Knowledge and Process Discovery Using Large Language Models | Ali Norouzifar, Humam Kourani, Marcus Dees, Wil M. P. van der Aalst | BPM Workshops 2024 | LLM 领域知识与过程发现融合：通往 Petri 网模型的数据驱动发现管线 | https://dblp.org/rec/conf/bpm/NorouzifarKDA24 | ✅DBLP

Translating Workflow Nets into the Partially Ordered Workflow Language | Humam Kourani, Gyunam Park, Wil M. P. van der Aalst | Petri Nets 2025 (ICATPN) | WF-net ↔ POWL 双向桥：老经典（Petri 网工作流）与新管线（LLM 生成）之间的形式等价通道 | 作者 DBLP 主页：https://dblp.org/pid/335/9391 | ⚠️S2 已核实（2025, Applications and Theory of Petri Nets），DBLP 条目未能定位（Springer LNCS 卷收录滞后）

---
### 备注（供后续增补）
- 候补观察：SPECpp 框架（Monotonicity-Guided Bottom-Up Petri Net Discovery, Tacke genannt Unterberg / Mannel / van der Aalst, CoRR abs/2608.09398, ✅DBLP）——Petri 网发现新法，若后续与 LLM 结合可归入本线。
- 本线与 LTL 综合线的应用分界（写书时可复用）：LTL 管时序承诺与自动策略生成，Petri 网管资源流与流程钉死；Formal-LLM 与 shielding 是两线各自在"agent 安全"上的落地形态。

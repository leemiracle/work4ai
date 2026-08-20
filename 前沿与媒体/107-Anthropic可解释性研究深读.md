# 前沿与媒体 · 107 - Anthropic 可解释性研究深读（interp 前沿线）

> 105 的配套深读篇之二。聚焦机制可解释性 2025-2026 四篇前沿文章（服务于 MATS interp 申请方向）。全文 webfetch 一手提炼，日期以原文页首为准（已纠 2 处与 sitemap lastmod 的偏差）。
> 读者定位：MATS Winter 2027 申请者（Neel Noda stream），需要判断：哪些是方法论前沿、哪些工具能立刻上手。

---

## 1. Natural Language Autoencoders（2026-05-07）★范式跃迁

🔗 [原文](https://www.anthropic.com/research/natural-language-autoencoders)

- **核心发现**：NLA 把激活直接"翻译"成可读自然语言——训练闭环：**激活 → 文字解释 → 重建激活**，用重建相似度逼出真实解释（绕开 SAE 特征的人工标注瓶颈）。
- **方法**：三模型副本——冻结目标模型 + **激活言语化器 AV**（激活→文本）+ **激活重建器 AR**（文本→激活），RL 联合训练。已实战：Opus 4.6 与 Mythos Preview 的**部署前对齐审计**。
- **关键数字**：代码破坏测试 NLA 测得评估觉察 16%（直接问模型近零）；SWE-bench Verified 26%；真实 claude.ai 使用 <1%；审计博弈中带 NLA 审计者胜率 12-15%，无 NLA <3%。
- **对 interp 的意义**：SAE 特征"语言化"的范式跃迁；**开源训练代码**（github.com/kitft/natural_language_autoencoders）+ Neuronpedia 开源模型，可复现。
- **局限**：解释会幻觉（编造上下文细节）；每激活生成数百 token，昂贵。

## 2. Open-Source Circuit Tracing（2025-05-29）★最佳入门工具

🔗 [原文](https://www.anthropic.com/research/open-source-circuit-tracing)

- **核心发现**：开源 attribution graph（归因图）生成库——任何人可在开源权重模型上追踪"模型想法"的内部计算路径。
- **方法**：归因图部分揭示决定输出的内部步骤；支持 Gemma-2-2b、Llama-3.2-1b；复用 GemmaScope 的 transcoder；Neuronpedia 交互前端。
- **对 interp 的意义**：**MATS 级最佳入门三合一**：生成图 + 可视化标注 + 改特征值做因果干预；demo notebook 提供未分析图，社区可贡献新电路发现。
- **局限**：仅小模型；归因图只"部分"还原计算。

## 3. Signs of Introspection（2025-10-29）★方法论锚点

🔗 [原文](https://www.anthropic.com/research/introspection)

- **核心发现**：用概念注入建立内部状态 ground-truth，证实现有 Claude 有**真实但高度不可靠**的内省——能在被注入概念被提及**之前**察觉"有东西在"。
- **方法**：①对照提示激活差分取概念向量注入无关上下文；②prefill 输出检测+回溯注入；③"想/不想 X"指令与奖惩激励可调制内部表征。
- **关键数字**：最佳协议下 Opus 4.1 察觉率仅 ~20%；Opus 4/4.1 显著优于 Claude 3~4.1 其他各代。
- **对 interp 的意义**："自我报告绑定内部状态"的内省研究方法论标杆（与 steering 应用划清界限）；研究提案的方法论引用锚点。
- **局限**：多数时候失败；人工扰动；概念向量语义本身不确定；闭源无复现代码。

## 4. Global Workspace in Language Models（2026-07-06）★理论×工程交叉

🔗 [原文](https://www.anthropic.com/research/global-workspace)

- **核心发现**：Claude 训练中**自发涌现** J-space——可报告、可按指令调制、参与多步推理、可跨任务复用的"全局工作空间"式内部表征集。
- **方法**：①**Jacobian lens**：为词表每个词找出使其更可能被未来说出的激活模式，直接读出"心里的词"；②swap 干预（France→China 一改四答全变）证明因果中介；③整体删除 J-space；④counterfactual reflection training 塑造内部思维。
- **关键数字**：J-space 同时仅持**几十个概念**、占内部活动 **<1/10**；读写连接密度部分网络**高约百倍**；删除后多步推理**掉至近零**，摘要/押韵低于更小的完整模型。
- **对 interp 的意义**：意识科学（GWT，Dehaene/Naccache/Butlin 评论）× interp 的交叉前沿；**Nanda 已在开源权重模型独立复现部分结果**；开源 anthropics/jacobian-lens + Neuronpedia demo。
- **局限**：J-lens 只识别单 token 概念；仅近似"真工作空间"。

---

## 给 MATS 申请的三句话判断（子代理结论）

方法论上，**Jacobian lens（理论驱动）与 NLA（工程驱动）是当前"读心"两线前沿**；可复现性上，**circuit-tracer（小模型）与 jacobian-lens（开源）是申请前最该上手跑的两件工具**；introspection 是概念注入范式出处，作提案的方法论引用。

与本仓既有地图的关系：`讲透模型宇宙/Part II 解剖`（探针/SAE/模型生物）覆盖到 2025 中的 SAE 世代；本篇四卡是 **SAE 之后的两代演进**（SAE→归因图→激活语言化/J-space）——若做申请材料，模型宇宙 07（SAE 4/6 特征）+ 本篇 NLA/J-space 构成完整技术叙事线。

## refs
- 四篇全文 webfetch 2026-08-20（子代理逐字读取，数字出自原文）
- 配套：`105`（全量索引）/ `106`（工程线深读）/ `讲透模型宇宙/Part II`（前置知识）
- 开源工具：github.com/kitft/natural_language_autoencoders ｜ anthropics/jacobian-lens ｜ circuit-tracing（Neuronpedia 前端）

*updated: 2026-08-20*

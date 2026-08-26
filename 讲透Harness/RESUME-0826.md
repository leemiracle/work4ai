# RESUME-0826 —— 讲透Harness 单元（2026-08-26 深夜终档：✅ 单元全部完成）

> **终态：00-12 章 + exercises + E1-E7 + 本地部署 e2e + QUICKSTART + 六处挂网，全部完成。**本文件转为完成档案（同讲透Loop RESUME 体例）。

## E7 终局（深夜补档）

- Phase 1：baseline (1,raw) 75% ｜ r0 50%（更差）｜ r2 75% 平手但多烧 1 调用 ｜ guided 75% 平手 → **终配置=默认（搜索零收益）**
- Phase 2：chosen/baseline 同为 (1,raw) → held-out 双 4/4=100%，gap=0（恒等式）
- **真实读数三层**（已写进 09 章 + json readout 已修正）：①小任务池上配置搜索成本>收益（AHE 的 +7.3pp 需要全基准池×10轮）②train75% vs held-out100% = 任务难度方差淹没配置效应 ③chosen==baseline 时 gap 无信息量——度量自由度警告
- 与讲透Loop E4（结构轴优化 8%→53.3% 正结果）构成完整对照：**优化什么比优化本身更重要**

## 单元最终清单（全部 ✅）

- 实验：E1-E7 json+png 全落盘（experiments/results/）
- 章节：00-12 + exercises.md（12 题，3★）
- 部署：deepseek-agent-harness zhipu 通道 e2e + QUICKSTART.md（含通道判定三环+故障速查）
- 挂网：讲透Agent 主README / 讲透Prompt / 讲透Context / harness工程手册 / harness精华合入 / deepseek-agent-harness README = 6 处
- 记忆：project 块已整块重写（含 ZHIPU 通道判定 08-26 修订）
- papers.md：§四 补 E4-E7+部署行

## 后续可选（新会话从这挑）

1. exercises #9（E6b 难分布：救回侧）/ #11（私有回归集 v0）/ #3（V0 换强模型测 harness dependence 模型轴）
2. 章节深化：Ch11 可补 deepseek-agent-harness 真实任务的轨迹逐行解剖（trace JSONL 已在 state/）
3. git 提交（用户未点名，留给用户决定）

## 一、今日全部完成（勿重做）

### 实验层（E1-E6 ✅ json+png 全落盘）
- **E1** naive vs 最小harness：真实 4/6→5/6；naive FCR=true（自称6/6）；harness FCR 结构性 0；调用 2→8
- **E2** 验证器三级：V0 自评漏报 2/13（全在"看起来合理"的真实生成上=execution-alignment failure）；V1 拦 6/13 零误杀；成本 V1≈0ms<V2≈3ms<<V0≈3862ms
- **E3** 崩溃恢复：无账本=100%幻觉恢复；账本=信息充分但 0.5B 解析 1/3 对（harness dependence 本地实锤）；meta：v1 解析器 bug 高估幻觉（解析器也是 harness）
- **E4** 预算守卫：矛盾任务 3/3 条件**零诚实放弃**（IMPOSSIBLE 出口给了也不用）；cap=2 省 3× 调用
- **E5** SELECT 代码化：ask_model **0%**（3/3 选已完成的 count_vowels）→ hybrid 100%（兜底3/3）→ code_select 100% 零调用
- **E6** 验证即级联：glm-4-flash 全过 → cascade≡all_flash 成本（6 vs 120，1/20）零遗憾侧成立；**升级侧未触发（诚实标注，E6b 留 exercises #9）**；png 已重画修正标题

### 章节层（00-12 ✅ + exercises ✅）
- 00 开场白/01 模型不是瓶颈/02 解剖学/03 验证即证据/04 状态与失忆/05 预算守卫/06 生命周期/07 参数趋同解/08 多模型/09 进化外环/10 前沿(Harness-Bench)/11 活案例/12 批判收尾
- 09 已按 E7 真实数字写成（负结果三层剥洋葱：零收益/方差淹没/gap 恒等）
- exercises.md：12 题（3 题★）

### 部署层（zhipu glm-5.3 coding plan 通道，e2e 全绿）★
- self-test ALL PASS（14+ 项）+ engine_probe ALL PASS（T1对话/T2工具调用/T3 thinker）
- **坑1（实踩）**：KH_ENGINE=zhipu 只切方言不切 base_url → 401（打到了 api.deepseek.com）。解：KH_BASE_URL 必须同设
- **通道判定三环证据链**：①key=auth.json[zhipuai-coding-plan]尾3KXf ②端点含 /api/coding/ 段 ③差分实测 coding×glm-5.3×thinking:disabled ✓0.9s / paas 同请求 400
- **推翻 08-17 记忆**：paas 端点现在也通 glm-5.3（默认thinking）——两通道真实差异=coding 接受 thinking:disabled；**带 thinking:disabled 的循环只能走 coding**（记忆块已修订）
- **真实任务 e2e**：修 calc.py `a-b→a+b`，agent 6 步完成（read→write→agent_test→verify→复测→done），**人工复核测试真过**
- **QUICKSTART.md**（最好用说明书）：三步部署+通道判定脚本+命令卡+故障速查+六组件导览；已挂网 deepseek-agent-harness/README

### 挂网（6 处）
讲透Agent 主README / 讲透Prompt / 讲透Context / harness工程手册 / harness精华合入 / deepseek-agent-harness README(QUICKSTART)

## 二、（原"未完成"清单——已全部完成，留档）

1. ~~E7 等跑完~~ ✅ 深夜完成，09 章已写（见文首"E7 终局"）
2. ~~E7 若崩溃 fallback~~ 未触发
3. git 提交：用户没点名要提交，先不动

## 三、今日新坑（记住）

- **snip heredoc 陷阱**：多行 heredoc 里部分行被注入"snip "前缀导致 SyntaxError——**复杂内联代码一律走 write 文件再跑**（replot_e6.py 教训）
- **nohup 会被 shell 超时连坐**：后台长任务必须 `setsid nohup … < /dev/null & disown`
- **后台实验抢 CPU**：前台实验 wall time 会被拉长 2-3×，对照实验的报告指标首选调用数（确定性）而非 wall time
- **E3/E5 解析器**：分段提取（第1问/第2问分开），全文 grep 函数名必高估幻觉
- **通道判定是部署刚需**不是知识点：probe 过≠走对通道，三环证据链见 QUICKSTART §二

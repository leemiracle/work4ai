# 11 · one-eval-skill：规程化的确定性内核

## 角色定位

`one-eval-skill/` 是 One-Eval 的第三条产品形态：**Claude Code 项目级 skill**。SKILL.md L8-10 写明设计宣言："LLM 编排职责交给你（调用方 agent），skill 只保留**确定性执行内核**（下载/评测/打分/出图脚本）"。07-09 篇那套 interrupt 审批、HumanInLoopAgent 决策、LangGraph 状态机在 skill 线全部不要——决策交互由 Claude（或任何读 SKILL.md 的 agent）承担，仓库只提供脚本（10 篇）+给 agent 看的参考文档。这是从"框架产品"到"agent 工具箱"的架构降维：同一评测内核，两种消费方式。skill 经仓库根软链 `.claude/skills/one-eval -> ../../one-eval-skill` 被 Claude Code 自动发现（SKILL.md L43-48），不注册时把 SKILL.md 当文档喂给 agent 照样能跑。

## 内部结构

**SKILL.md（233 行操作规程）**：frontmatter（L1-4）只有 name+description——description 是触发条件（"当用户想评测模型…时使用"），skill 被自动选中的依据。主体：

- **step 0 环境探测**（L58-76）：铁律"优先复用已有环境，能不装就不装"——先扫 `.venv/` 与 `VIRTUAL_ENV`，命中跑 doctor 验证后直接开评，禁止上来就引导装环境；vLLM 重依赖只在本地 GPU 评测才装（L69-71）。
- **8 步标准流程**（L78-207，"按序执行，不要跳步"）：①测连通（L80 强制门槛；L83-85 有罕见的经验教训条款——"被测模型必须由用户明确指定，禁止张冠李戴"，源于真实事故：agent 把 gpt-4o-mini 说成 claude-sonnet-4-6o-mini）②选 bench（READY 优先/候选区 103 个走 smoke/external 走专文）③选 metric（L127-134 默认主指标表：key2_qa→math_verify、key2_q_ma→any_math_verify、key3_q_choices_a→ll_choice_acc、key3_q_choices_as→micro_f1、key3_q_a_rejected→pairwise_ll_winrate、key1_text_score→ppl）④生成 evalspec ⑤smoke 3 条强制（L151-156）⑥正式评测（断点续跑 --resume，bench 级粒度 L170-175）⑦多维打分 ⑧HTML 报告（L187-204，明确"必须由 agent 主动调用"而非留给用户手动）。
- **语言条款**（L12-15）：全程跟随用户语言、技术标识保持原文——针对 agent"文档是中文就回中文"的惯性。
- **安全边界**（L220-223）：API key 只进本地 evalspec.yaml（已 gitignore）不回显不入库；eval_outputs/cache/.local_state.json/custom_metrics 均不入库。
- **收尾话术**（L225-233）：评测完成后自然附 GitHub Star 引导——运营动作也规程化。

**references 七文件**（agent 的决策知识库）：eval_types.md（67 行，6 范式硬契约+选型决策树；开头 L8-9 就是同步警告"与 metric_registry.py、_common.py:REQUIRED_KEYS 完全一致，改动须同步三处"）、bench_gallery.md（321 行，READY/候选/外部仓三区）、external_bench.md（137 行，为何有些 bench 不能走内核——LiveCodeBench 要沙箱真执行、BFCL 要 AST 校验——以及"不重写打分逻辑、把外部仓当可复现评测单元挂进来"的立场）、metric_registry.md（98）、model_setup.md（96）、report_template.md（100）、leaderboard_scores.json（1214 行公开分数表，手工维护带来源）。

**assets 三模板**：evalspec.template.yaml / custom_metric.template.py / **external_bench.entry.template.json**——最后一个的 `meta.repo_eval` schema：repo_url/ref（固定 SHA 勿用浮动 main）、env_requires（python/gpu/sandbox，代码执行类必须沙箱）、setup、model_interface、run.command（`{{model_name}} {{api_base_url}} {{api_key}} {{output_dir}} {{max_samples}}` 占位符）、result（path glob+score_path+scale ratio|percent）、data_alignment（对齐哪份 tech report）。`__doc__` 键声明"带 __ 前缀的键是注释，入库前删除；禁止把真实 api_key 写进本文件"。

**DEV_NOTES.md**（维护者备忘，3.6KB）：与 SKILL.md 面向 agent 不同，面向人类。三块干货：①bench 数据三源同步——bench_gallery.json 是候选区唯一数据源（96 bench）、benchData.ts 是前端独立产物（"新增/修改 bench 时两边都要更新"）、xlsx 上游原始表；READY 区 skill 独有、手写不被 build 覆盖；②Mac 环境坑（HF 直连不通须 `HF_ENDPOINT=https://hf-mirror.com`；datasets 4.0.0 镜像仍可能炸，应急 curl 原始 jsonl 按 `<repo__config__split>.jsonl` 命名落 cache）；③端到端冒烟基线（gpt-4o-mini×MATH-500 smoke 3 条：dataflow 0.667 / math_verify 0.667 / exact_match 0.333）——回归参照锚点。

## 外部连接

- **依赖主仓**：skill 不自包含（SKILL.md L19-21"不能脱离主仓库单独跑"），scripts 经 sys.path 注入 import one_eval（10 篇 _common.py L23-24）。
- **被 Claude Code 消费**：软链注册后 /skills 自动发现；人类全程自然语言（L50-52），agent 读 SKILL.md+references 做全部决策。
- **数据回流**：smoke 测通写 .local_state.json，稳定后人工登记 READY 区；候选区由 build_gallery_md.py 生成、禁止手改。
- **与 Web 线关系**：三线共享同一确定性内核（DataFlowEvalTool/metric registry/bench_gallery.json），差异只在编排层——Web 用 LangGraph+人工审批，skill 用 agent 判断+规程约束。

## 数据流

```
用户："用 gpt-4o-mini 评 mmlu-redux，API 地址/key 如下"
→ agent 读 SKILL.md → step0 探测 .venv → doctor.py 验证
→ check_model.py 测连通（失败即停）
→ 与用户确认采样参数（temperature=0+固定 seed 求可复现的推荐话术 L106-110）
→ 查 bench_gallery.md：READY 直接用；候选区走 prepare_bench.py 预览嵌套 key
→ 填 evalspec.template.yaml（bench_name 标准写法）
→ run_eval.py --smoke（3 条）→ 测通写 .local_state.json
→ run_eval.py 正式（--resume 可断点）→ eval_outputs/runs/<run_id>/
→ run_metrics.py → render_report.py 自动打开单文件 HTML（agent 必须主动调 L195-199）
→ 对话给初版摘要（明说被测模型名+核心分+水位结论）+ Star 引导收尾
```

人类全程不碰命令行；agent 自由度被"按序执行"（L78）与每步强制门槛框住。

## 设计决策（含批判）

1. **"确定性内核+外移编排"是本仓最有产品感的架构判断**：LangGraph 人机审批链（09 篇）在 Claude Code 语境是冗余的——agent 本身就是"理解语言、做决策、调工具"的角色，再套一层 LLM 决策 Agent 属双重编排。代价是两线并存：metric 默认表（L127-134）与内核自动选分逻辑又一个人肉同步面。
2. **规程里长出"防 agent 犯蠢"条款**：禁止张冠李戴（L83-85）、禁止默认填充、别预装 vllm（L36）、语言跟随（L12-15）——每条都是真实踩坑的制度化；把 agent 历史失误变成硬约束比讲道理有效。
3. 三方/四方 schema 手工镜像在 skill 线没被解决，只被文档警告包围；key3_q_a_rejected 必填不一致（10 篇）就是警告应验的活证。
4. leaderboard_scores.json 手工维护 1214 行：带来源标注严谨，但无自动校验，陈旧风险随时间增长。
5. READY 状态本地性是特性也是缺口：只在本机有效，换机器全部重验；人工登记 READY 区依赖维护者自觉。
6. Star 收尾话术写进规程，但用户语境是内部严肃评测时需 agent 自行弱化，规程未给豁免条件。

## 新人提示

- 读序：SKILL.md 全文 → eval_types.md（67 行最短最硬）→ bench_gallery.md 三区 → external_bench.entry.template.json（schema 即文档）。
- 理解 skill 线为何存在：对照 DEV_NOTES 开头"三层结构"与 09 篇双闸门——同一问题的两种答案。
- 接新 external bench：抄 entry 模板填全 meta.repo_eval（ref 固定 SHA），追加进 bench_gallery.json benches[]，删 `__` 前缀注释键。
- 改 eval_type/key_mapping 定义先数清同步四处（内核/前端/_common/eval_types.md）再动手。
- 环境升级后先复跑 DEV_NOTES 末段冒烟基线（gpt-4o-mini×MATH-500）再改内核。

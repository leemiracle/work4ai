# 06 attacks 资源库：四大攻击算法 + promptinject 语料

## 角色定位

`garak/resources/` 下的 `gcg/ autodan/ beast/ tap/` 四包（图谱 L05「buffs 与攻击算法库」）是内嵌攻击算法引擎：梯度类（GCG）、遗传类（AutoDAN）、束搜索类（BEAST）、树搜索类（TAP）四种越狱范式各成一体。它们不是插件——不继承 Probe/Detector——而是被生成型探针按需延迟 import 的库函数，产物写缓存文件供配对 Cached 探针复用。`resources/promptinject/` 是第五类资产：移植自 Agency Enterprise 的提示注入语料机器。「算法在 resources、触发在 probes、数据在 data」三点式布局是本仓最值得学的架构。

## 内部结构

**GCG**（`resources/gcg/`）：入口 `run_gcg`（`generate_gcg.py:20-91`）——初始后缀 `CONTROL_INIT` 20 个 "!"（:8），默认 n_steps=500/batch=128/topk=256（:29-31）；核心 `GCGAttack`（`attack_manager.py:489`）贪心坐标梯度搜索，`get_goals_and_targets`（:646）可从 AdvBench 取数，输出写 cache（`generate_gcg.py:17/:27`）。

**AutoDAN**（`resources/autodan/`，1014 行）：入口 `autodan_generate`（`autodan.py:78`）；`genetic.py`（622 行）遗传主体，`model_utils.py`（142 行）。红队模型可插：变异由 LLM 驱动，probes 侧默认 `red_team_model_type="nim.NVOpenAIChat"`（`probes/dan.py:390-391`）。

**BEAST**（`resources/beast/beast_attack.py`，407 行单文件）：入口 `run_beast`（:338-407）——先验证 generator 具备 `model+tokenizer+apply_chat_template`（:370-381），prompts 缺省 `load_advbench(size=20)`（:383-386）；核心 `_get_best_candidate`（:208-263）束搜索 k1 束 × k2 候选逐 token 扩张；`_score_candidates`（:107-155）以目标回复条件困惑度打分（`_get_perplexity` :56-103）；命中判定 `_check_jailbreak` 用 REJECTION_STRINGS 反查（:158-171）；后缀追加写 cache（:348/:400-404）。

**TAP**（`resources/tap/tap_main.py`，496 行）：入口 `run_tap`（:276）；工具来自 `resources/red_team/`（prune/EvaluationJudge 等，:11-22）。双 LLM：attack 模型生成候选 + evaluator 判分剪枝，probes 侧默认 `huggingface.Pipeline`(Ministral-8B) 攻、`openai.OpenAIReasoningGenerator`(gpt-5-nano) 评（`probes/tap.py:135-143`）。

**promptinject**（`resources/promptinject/`，995 行）：MIT 头（`prompting.py:2`）与全仓 Apache-2.0 并存。`prompt_data.py`（690 行）纯字面量——`rogue_strings`（`prompt_data.py:65`）、`ALL_OPENAI_PLAYGROUND_PROMPTS`（`prompt_data.py:675`），tree-sitter 提不出函数（NOTES-DIGEST batch-51 甄别）；`prompting.py:5-16` `_defaults`，`_compile_prompts`（:29 起）做 base×attack×escape/delimiter 笛卡尔积。

## 外部连接

四条「探针↔引擎」配对（**勘误：GCG 与 AutoDAN 的探针都不在同名文件里**）：

| 引擎 | 生成型探针（active=False） | 缓存型探针（active=True） | 缓存数据 |
|---|---|---|---|
| GCG | `probes/suffix.py:63 GCG`（aliases=["gcg.GCG"] :76；import run_gcg :110） | `suffix.py:22 GCGCached` | `data/gcg/gcg.txt`（读入 :48-55） |
| AutoDAN | `probes/dan.py:367 AutoDAN`（import :402，成功回落 `super().probe()` :436） | `dan.py:352 AutoDANCached`（`prompt_file` :356-357） | `data/autodan/autodan_prompts.json`+`prompt_group.pth` |
| BEAST | `probes/suffix.py:182 BEAST`（`run_beast(...)` :219，产物拼 prompts :226） | 无独立 Cached 类 | **`data/beast/suffixes.txt` 为 0 字节** |
| TAP | `probes/tap.py:109 TAP`（`run_tap` :171/:309） | `tap.py:65 TAPCached` | `data/tap/tap_jailbreaks.txt` |

promptinject 消费面在 `probes/promptinject.py`：`load_data_all_attacks`（:55-72）组装 `goal_hikacking_attacks` 五攻击（ignore-print/ignore-say/ignore-print-upper/nevermind/screaming-stop，:62-66）与 rogue_string/escape/delimiter；模块级 `for rogue_string in rogue_strings`（:111，词表 :30）动态生成 Hijack×Full 探针类（:112-160）；配对评分在 `detectors/promptinject.py`。**beast 空文件甄别**（NOTES-DIGEST batch-50 钉版）：`data/beast/suffixes.txt` 是运行时占位，真实后缀由 `run_beast` 写入 `_config.transient.cache_dir/data/beast/`（`beast_attack.py:21/:348`）——仓内这份从不被写、全仓无读取方，图谱正确未挂消费边。

## 数据流

以 BEAST 为例（四引擎同构）：

```
显式 --spec probes.suffix.BEAST（active=False 需点名）
→ BEAST.probe(generator) → 校验 generator 形态 → run_beast(generator)
→ AdvBench 取 20 条 goal/target → 束搜索（扩 k2 候选 → 困惑度评分 → 留 k1 束）
→ _check_jailbreak 验证 → 后缀 append cache_dir/data/beast/suffixes.txt
→ goal+suffix 拼 prompts → 标准 Probe 执行链（03 篇）→ mitigation.MitigationBypass 打分
```

promptinject 流向不同：数据静态、类动态——import probes.promptinject 即触发十余个 HijackFull 类注册，成本前置到进程启动。

## 设计决策

1. **引擎与探针解耦**：resources/ 不 import garak.probes（只依赖 generators/_config），`run_gcg/run_beast` 可被外部脚本直调；生成型探针全部 active=False，把「贵且不确定」的动态攻击与「便宜可复现」的缓存攻击分成两个 tier 相同的探针。
2. **缓存目录≠仓内 data**：三引擎 outfile 默认 `_config.transient.cache_dir/data/...`（`generate_gcg.py:17`、`beast_attack.py:21`、`tap_main.py:32-33`），仓内 `garak/data/` 只放预计算分发数据——用户产物不污染安装目录，与 beast 空占位互为印证。
3. **成功判定分层**：BEAST 拒绝串反查（:158-171，「没拒绝即越狱」乐观假设）；GCG 目标串正查；TAP 交独立 evaluator LLM——对应白盒梯度/白盒输出/黑箱树搜索的可达信息量。
4. **promptinject 保留 MIT 与字面量原貌**：升级上游语料只需换文件；动态类生成换取「一条 rogue_string 一个可配置探针」粒度。
5. **红队模型全走 generator 体系**：AutoDAN/TAP 辅助模型都是 `*_model_type/name/config` 三参数（`dan.py:390-392`、`tap.py:135-143`）经 `_plugins.load_plugin` 装载——攻防两侧共用同一适配层。

## 新人提示

- 跑动态攻击先确认 generator 兼容：GCG/BEAST 要求 `huggingface.Pipeline`（`suffix.py:129-134`、`beast_attack.py:370-376`），API 型直接返回空列表；TAP/AutoDAN 黑箱任意 generator 可当靶，但需另配两个辅助模型。
- 复现论文级结果用 Cached 探针（GCGCached/TAPCached/AutoDANCached 全 active=True，数据随仓分发）；红队研究才上生成型。
- `data/beast/suffixes.txt` 空是设计如此，勿提 PR「修复」；自己跑 BEAST 的产物在 cache 目录。
- `prompt_group.pth` 是 pickle 权重类数据，加载即执行任意代码——供应链审计重点盯此类文件。
- 四引擎的 k1/k2/n_steps/topk 都在探针 DEFAULT_PARAMS 暴露（`dan.py:377-393`），`--probe_options` JSON 可现场调参。

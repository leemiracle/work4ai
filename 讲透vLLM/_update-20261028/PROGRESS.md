# vLLM 知识库更新进度（2026-10-28 会话）

## 状态快照（随进度更新）
- 仓库: /usr-data/data2/repos/pytorch-landscape/repos/vllm @ 06e172b5cf（2026-10-28）；/usr-data/data2/kylin/vllm 是其 symlink
- 旧基线: 图谱 11615 节点/33598 边 @ 7894394b（2026-09-03）；deepwiki 62 页（2026-09-02）
- 备份: .understand-anything-bak-20260903/（128M 全量，含旧 intermediate）
- 本轮 delta: changed=1630 deleted=79 added=865 → 重分析 2484 文件 / 104 批（batches/，核心优先排序）

## 完成项
- [x] Task1 DeepWiki：74/74 TRUE_100，页已换入 deepwiki/，INDEX.md+coverage 重写（56 页全更新+18 新增+6 改名）
- [x] Task2 delta 对账：delta.json / reanalyze-set.json 落盘；裁剪 recipes/(190 preset)、UA 自身、备份目录泄漏
- [x] 派发模板 dispatch-template.txt（钉版条款全量）

## 进行中
- [x] Task3 派发：**105/105 批完成**（10-31 22:40；104 计划批+1 补录批）
  - 收官组 101-104（10-31 会话 c80bfac9）：101=119n/248e · 102=153n/303e · 103=167n/473e · 104=65n/103e，全部主会话独立抽验锚 HIT+对账 0 差
  - 验收修复：batch-104 29 个 complexity 误填 lineRange 坏锚已按源码重扫修复（26+3 async fn，残余 0）；step/pipeline/service/schema 白名单撞车已修（surgery_merge.py:48 VALID 扩，险丢 17 节点）
  - **batch-105 补录批（10-31 派）**：dry run 悬空归因发现 87 个"基线洞"文件（旧图零节点+1401 条新边实例引用，56 个 vllm/ 核心包内：logger.py/lora/request.py/parser/ 子系统/multimodal/media//pooler/tokwise/mhc 内核等——2026-09 轮 scanner 系统性漏收的整片处女地）→ 派 worker 真分析（非占位节点）；另 2 边 file:→service: 前缀修复（batch-104 docker 双 Dockerfile）
  - 其余 ~197 悬空端点=changed 文件中未再产出的符号（重构后消失，诚实丢弃）
  - 节奏实测 ~15min/批·车道，104 批 4 车道 ETA ~17:30
  - **100/104 完成**（10-31 22:10 会话 c80bfac9 断点续跑）。产物 148 文件零损坏（12039n/37435e），仅缺 101-104
  - 事故史：10-28 12:41 与 10-29 14:02 两次 1308 五小时团灭；10-29 轮 97/104 后在飞 097-098/101-102/103-104 三对——其中 097-100 死前落盘，101-104 未落
  - 10-31 22:05：收官两组已派（w: 101-102 / w: 103-104，2 并发防线）；全局覆盖对账=真缺口 0（46 未覆盖文件全在 101-104 内）
  - 预检完成：旧基线图谱完好 11615n/33598e@16层14导览；pipeline-bin 工具链齐（finalize 修版在位）
  - **事故：10-28 12:41 四 worker 同时被 1308 五小时上限团灭**（限额 14:18 重置）→ 10-29 13:33 全员 SendMessage 复活断点续跑（上下文保留，073 已在死前落盘零损失）
  - worker 战绩（至团灭前）：w4 26批 3842n/11494e · w3 14批 1746n/6123e · w1 19批 · w2 12批
  - 架构情报持续入档 worker-highlights.md（已 12 节：v1 引擎/speculator 家族/kv_offload/水印/config/entrypoints/RL+scale_out/KV connector 军团/weight_transfer 五后端/mono×3（V4.1+K3+M3）/Engram+PLE 记忆机制/RecoverSSM/K3/Step5 CSA-DSA/GLM-5-Next 双胞胎/MuseSpark/Qwen4-Exp 三线…）
  - 注意: 047/048 有跨批并单（2 文件节点在 047 产物）→ 终验按全局覆盖对账非逐批
  - 事故记录: 11:02 worker1 被 1302 杀（零产出）→ SendMessage 复活成功；Bash/SendMessage 分类器多度瞬时限流（重试即过）；本机 6 个并行 Claude 会话共享账户=限流根源
  - 已知遗留: 仓根 gen*.py/build*.py 临时脚本若干 → 收尾清理
  - 派发方式: Agent(general-purpose) prompt=模板+批号；完成后 SendMessage 续派下一组（保留上下文省重读）
- [x] Task4 手术: **✅ 正式落盘 10-31 23:04**——assembled 14454n/41124e（含 105 批 13002 原始新节点+51 二环兜底节点）；守恒闭合+终检悬空 0；残余丢弃=符号级 264+重复 49n/25e
- [x] Task5 layers/tour+finalize：**✅ 10-31 完成**——16 层/16 步/3168 全覆盖零重复（主会话独立终验）；finalize validator 0 issues/0 warnings + 独立校验复跑 0/0；fingerprints 7117 文件 @06e172b5cf（7121−4=清掉的仓根垃圾文件数，对账吻合）；intermediate 已清（scan-result.json 保留）
- [x] Task6 收尾：**✅ 10-31 收官**——knowledge-graph.json+GRAPH-SUMMARY.md 已同步 work4ai；README 状态更新（74 页/14454n/41124e/双 commit 锚）；FINAL-REPORT 增记更新轮全章（守恒账+四条钉版+架构情报索引）；仓根 json/math/re/sys 已清；项目记忆已存
- 遗留（下轮候选）：ONBOARDING.md 与 explain/ 14 篇未重写（主线仍有效，层名/数字以新图谱为准）；_update-20261028/ 工作目录归档保留

## 断点续跑指令（新会话）
1. 读本文件；2. 对账 products/ 缺批 vs batches/（batch-{i:03d}.json 1..104）；3. 缺批按模板派发（4 并发）；4. 全齐后跑 surgery_merge.py --dry → 正式；5. phase4_prep→layers/tour tasks→finalize→ua-inline-validate 0 issues→fingerprints；6. Task6 收尾
关键路径文件：delta.json / batches/_meta.json / products/ / surgery_merge.py / dispatch-template.txt

## Task7（2026-11-01 00:1x 追加，用户令"继续"）
- [x] ONBOARDING.md 重写（**✅ 21:3x 收官**）：8 节/10846 字符（同口径旧版 12562 精简 14%）/79 全路径锚 0 坏+抽验 8/8；仓内 .understand-anything/ONBOARDING.md 已同步；大勘误=旧主入口 api_server.py 已成 59 行弃用垫片
- [x] explain 13 篇刷新（**✅ 21:3x 收官**，旧 14 篇已归档 archive/explain-20260903/）：
  - 刷新依据=delta 交叉对账：12/14 篇目标文件 changed 命中 + VllmConfig 篇目标移位（vllm/config/vllm_config.py→vllm/config/vllm.py:349，config 已目录化）
  - W1 引擎线 5 篇（async_llm/core/scheduler/kv_cache_manager/arg_utils）· W2 worker 线 4 篇（model_runner/input_batch/gpu_worker/flash_attn）· W3 外围线 4 篇（config-vllm/parallel_state/entrypoints-llm/llama）
  - 2 篇未变保留原样：entrypoints-openai-api_server + （config 篇已归入刷新）
  - 规范：六节结构/锚源码实证≥15 每篇/不计空格 2500-4800 字/做完一篇落一篇
- [x] 收尾（**✅ 21:4x**）：verify_explain.py 全量终验 14 件套 0 坏（~1000 锚；11 个"坏锚"人工消歧全判真升格全路径）；README 六处脱钩修复（统计块旧基线 11615n/14 步→14454n/16 层 16 步等）；FINAL-REPORT 增 Task7 章（7 条内容级大勘误+3 条钉版）；字数口径=不计空格 4635-5221/篇+ONBOARDING 10846，README 已记口径
- 遗留下轮：新子系统 explain 篇（parser/snapshot/kv_cache_interface/Rust 前端/launchers 新入口）+api_server 旧篇代差说明；W2 自报 2 个 miss 复核为合法块起点锚（2117/4426）已采信

## Task8（2026-11-01 21:5x 追加，用户令"继续"——遗留下轮项当轮清）
- [x] 6 篇新写/重写（**✅ 22:3x 收官**，3 worker 全零重派）：
  - W5：vllm-parser-abstract_parser.md（4912 字/79 锚）· vllm-v1-kv_cache_interface.md（4884/76，**KVQuantMode 值 12 别名碰撞疑似上游 bug**）
  - W6：vllm-snapshot.md（5469/97，彩排机制+sleep level2 语义勘误）· rust-server-lib.md（5576/94，平行可切换+对等缺口清单）
  - W7：vllm-entrypoints-launchers.md（6397/111，五路选择树）· api_server 代差重写（4705/45，**上游文案 bug：`vllm server` 子命令不存在**）
- [x] 收尾（**✅ 22:4x**）：全量终验 20 件套 0 坏锚；仓根零污染；README（explain 14→19 篇+目录+时效）+FINAL-REPORT Task8 章+记忆已补记
- 新工具：qualify_anchors.py（多前缀锚自动升格，本轮 33 自动+9 人工全判真）
- 遗留下轮：KVQuantMode 碰撞核实报 issue · render/run_batch 独立篇 · highlights×explain 交叉索引页
- 派发前置已 ls 实证：parser 45 py/snapshot 5 文件/launchers 含 api_server/ 子目录/api_server.py=59 行

### Task7 断点续跑（11-01 20:10 会话 ac8a6af1 接管）
- 前会话（00:1x~15:52）成果：归档旧 ONBOARDING+14 篇 explain（15:46）；落新篇 2/13（async_llm 15:51 / config-vllm 15:52）；onboard-input.json 已重生成（15:46，16层/16步/30枢纽）
- 20:10 对账：12 目标源码路径全 OK@06e172b5cf；心跳 15:47 无并行实例
- 20:11 派发 4 worker（并发=4）：W1 引擎线余 4 篇（core/scheduler/kv_cache_manager/arg_utils）· W2 worker 线 4 篇（model_runner 7192L/input_batch/gpu_worker/flash_attn）· W3 外围线余 3 篇（parallel_state/entrypoints-llm/llama）· W4 ONBOARDING（8 节 4000-6000 字/≥40 锚）
- 终验脚本 verify_explain.py 已预置于本目录（锚界内校验+basename 消歧+不计空格字数）
- 21:0x 进展：**W1 ✅**（4 篇 4650-4788 字/60-85 锚全 PASS；1 basename 锚升格全路径）；**W3 ✅**（1302 杀于收尾报告期但 3 篇死前全落盘，验收 PASS：parallel_state 4731/74、entrypoints-llm 4869/61、models-llama 4936/62；7 个短锚消歧升格——vllm/ 前缀省略型+basename 歧义型，全部实证判真）；**W4 ✅**（ONBOARDING 10832 字同口径比旧版 12562 精简 14%，79 全路径锚 0 坏+8 抽验全命中；旧版主入口 api_server.py 已成 59 行弃用垫片等 6 条大勘误；仓内副本已同步）；async_llm 5221/config 4876 略超 4800 属行号锚密度漂移（历史区间内，README 记口径）
- 待：W2（4 篇）在飞 → 全量终验 → 收尾补记

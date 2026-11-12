# 04 · bench_gallery.json：121 基准唯一真源与分数库

## 角色定位

`one_eval/utils/bench_table/bench_gallery.json`（547KB）是全部基准的**唯一真源**：bench 检索、下载配置、字段映射、external_repo 挂载描述全部出自这里。server 启动即加载——app.py:400-401 用 `BENCH_REGISTRY_PATH` 实例化 `BenchRegistry`；任务书说的「patch_files 机制」并不在文件顶层，而藏在 10 个 external bench 的 `meta.repo_eval.patch_files` 里（05 篇详拆）。

## 内部结构

**注册结构**（实测 121 条）：每条必带 `bench_name/bench_table_exist/bench_source_url/bench_dataflow_eval_type/bench_prompt_template/bench_keys/meta` 七顶层字段；meta 必带 `source/aliases/category/tags/description/hf_meta`，111 条有 `key_mapping/evaluation/prompt/readiness`，94 条有 `download_config`，86 条有 `structure/key_mapping_reason/radar_dimensions`，10 条带 `bench_kind="external_repo"`+`meta.repo_eval`。eval_type 分布：`key3_q_choices_a` 49、`key2_qa` 37、`key2_q_ma` 10、`key3_q_a_rejected` 10、`key1_text_score` 5、null 10（external 仓不带）。

**BenchRegistry**（utils/bench_registry.py:10）四职责：①双格式加载——`{"benches":[...]}` 新格式与旧 bench_config.json 字典型兼容（58-76），casefold 去重、后定义优先（80-106，注释自述 gallery 多源生成会重复）；②名称/别名匹配，小写全等后再做 alias 子串（111-135）；③`search`（140-220）先精确解析用户点名（source=specified），再按 `meta.tags ∩ domain` 交集推荐（source=local_recommend），两者皆空直接返回防全表倾倒（165-166）；④`add_bench/remove_bench`（237-284, 286-335）写回文件+失败回滚内存。

**patch_files 机制**：`meta.repo_eval.patch_files=[{src,dest}]` 描述「本仓补丁 → 外部仓目标路径」，由 ExternalRepoRunner 安装前复制（external_repo_runner.py:352-367）、复用已装仓库时按 mtime 热更新（222-232）。10 个 external bench 全带。

**leaderboard_scores.json**（one-eval-skill/references/）：16 个 bench 的公开模型分数库（gsm8k、MATH-500、AIME_2024、MMLU-Pro、GPQA-Diamond、supergpqa、HumanEval、mathvista、humanevalplus、mbppplus、bfcl、livecodebench、gaia、mmmu、mmmu_pro、tau2_bench），手工维护，render_leaderboard.py 把用户自评分穿插进公开分排名。_README 六条硬规矩：①每条分数必带 source+source_url+as_of+setting 四要素，没出处不收；②setting 写清 shot/CoT/子集，口径不可比就标「仅供参考」；③0-1 小数与主分一致；④bench key 与框架对齐、大小写敏感；⑤种子示例会过时须自查；⑥只收单次推理分（0-shot/few-shot、greedy 或 avg@1），严禁 maj@k 投票分。已知缺口照登不硬凑：IFEval 口径不统一宁空、HumanEval 仅 6 条、GPQA-Diamond 取 DeepSeek-V3 同脚本 7 条。

## 外部连接

上游：server 的 `/api/benches/gallery` GET/POST（app.py:1904/1947）与 `/api/benches/upload`（1982，仅收 UTF-8 JSONL，上限 512MB=app.py:403 `MAX_CUSTOM_BENCH_BYTES`），删除仅限 `cache/custom_benches` 本地上传（2088-2105）；BenchSearchNode/BenchResolveAgent 经 registry 解析名称。下游：skill 侧 `references/bench_gallery.md` 由 build_gallery_md.py 从主 gallery 生成候选区（勿手改）+手工 READY 区；bench_table/ 内还有 config.json/benchData.ts/xlsx 三份历史资产并存。

## 数据流

用户点名或 domain 检索 → search 返回带 `source` 标记的条目 → 转 `BenchInfo` 入 state.benches → download_config 驱动下载 → key_mapping 指导字段拍平 → external bench 走 repo_eval 全链。上传线：JSONL 校验 → 落 cache/custom_benches → `build_local_bench_entry` 注册进同一 gallery 文件。

## 设计决策（含批判）

1. **单文件真源**：121 条一处维护，去重/回滚内建；但 547KB JSON 手工编辑易错，且 bench_table/ 内新旧四份资产无同步机制，漂移风险实际存在。
2. **包含匹配最长优先**：`math-500_v2` 能命中 `math`，宽进；代价是名字嵌套的 bench 可能误配。
3. **分数库宁缺毋滥**：六条硬规矩全是可信度防线，与主框架解耦放 skill 侧，公开分不污染评测主数据。
4. **上传白名单删除**：只能删本地上传 bench，内置条目不可破坏——但 add_bench 无 schema 校验，坏条目会直接进真源。

## 新人提示

找 bench 记住匹配口径（小写+别名）；加 bench 优先走 `/api/benches/upload` 而非手改 JSON；查某 bench 怎么评测看三层：`bench_dataflow_eval_type`（题型）→ `meta.key_mapping`（字段）→ `meta.repo_eval`（外评挂载）。分数对比必读 leaderboard_scores.json 的 _README 再下结论。

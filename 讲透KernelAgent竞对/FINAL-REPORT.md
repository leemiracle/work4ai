# 最终报告：讲透 KernelAgent 竞对四仓知识库构建

**执行日期**：2026-09-03（单日全链路）· **执行方式**：主会话编排 + 5 并发 task（file-analyzer/explain/onboard 复刻）

## 任务完成情况

### 任务 1：DeepWiki 结合 + 文档更新 ✅
- **四仓本体均未被 DeepWiki 索引**（钉版核验：KernelBlaster/KernelMem/ReGraphT 页面为 Loading 壳，EvoKernel 系 HF 数据集无页面）→ 策略=「关联仓 wiki + 源码深读补位」
- **关联仓 KernelBench（ScalingIntelligence）36/36 子页全量快照**（快照基线 2026-01-16, commit 2f65279d），curl+代理抓 SSR HTML → python 抽正文，3 页抽样与 webfetch 提取比对一致
- 快照落位：`shared-deepwiki/kernelbench/`（唯一正本）+ 四仓各自 `DEEPWIKI-DOCS/kernelbench/`（仓内副本）；每仓 `DEEPWIKI-DOCS/README.md` 写明交叉引用表（哪章对应本仓哪个模块）
- **遗漏检查**：_coverage-check.md（36/36，0 缺失）——注意 TOC 实为 36 页（8 章+28 子节），初数 35 系误计

### 任务 2：understand 三连 ×4 ✅（Phase 0-7 全链路，--language zh）

| 仓 | 文件策略 | 图谱 | 校验 |
|---|---|---|---|
| KernelBlaster | 63/440（排除 184 对 init.cu+driver.cpp 数据集） | 269n/589e/10 层/15 步 | 0 issue |
| KernelMem | 28/297（排除 KernelBench/ 270 任务） | 129n/258e/6 层/12 步 | 0 issue |
| EvoKernel | 32/2444（**采样式**：5 manifest+README+每集合代表 kernel 解剖） | 86n/136e/5 层/9 步 | 0 issue/0 warning |
| ReGraphT | 19/20（全量） | 48n/84e/6 层/9 步 | 0 issue/0 warning |

- **/understand-onboard ×4**：各仓 docs/ONBOARDING.md（2000-3100 字，六节齐：总览/分层/概念/导览/文件地图/复杂度热点）
- **/understand-explain ×22 篇**：KernelBlaster 8（opt_ncu_rl/database/graph/run_RL/feedback/rl_agents/servers/dataset）+ KernelMem 6（main/ncu/compile_and_run/memorybank/prompts/query_server）+ EvoKernel 4（manifest/cann-layout/best_code/pytorch-references）+ ReGraphT 4（construct/ReGraph/run+engine/prompt+gaps）
- 附加交付：EvoKernel **DATASET-AUDIT.md**（567 kernel 五集合统计：MHC 正确率 66.7% 唯一带 speedup 标签；iteration median 21；performance.mean 跨集合口径警示）

### 任务 3：合并 work4ai ✅
- 目录：`讲透KernelAgent竞对/{README.md, FINAL-REPORT.md, shared-deepwiki/, kernelblaster|kernelmem|evokernel|regrapht/}`
- 每仓子目录：ONBOARDING + DEEPWIKI-CROSSREF + knowledge-graph(摘要+json) + explain +（EvoKernel 另有 AUDIT）

## 值得记录的发现（竞对情报增量）

1. **ReGraphT 完成度低**：reasoner/{standard,cot,code_rag}.py 为 0 字节空占位、README 2 行——ICLR2026 投稿的早期开源形态，推理图核心（construct.py 248 行+ReGraph.py 221 行）真实存在但执行层缺失
2. **KernelBlaster 出厂 KB 审计坐实**：optimization_database.json 仅 3 状态组策展、无实测对（explain/database 篇逐字段核对）——跨 GPU 代际的状态匹配失效风险=我方 oracle 真值表的差异化空间
3. **EvoKernel 价值标签集中在 MHC**：15 例中 6 例 faster_than_baseline，是五集合里唯一带 baseline speedup 字段的——「值驱动检索」主张的直接证据载体也是最小样本
4. **KernelMem 的 gate 表**：memorybank 双资产（yaml 瓶颈先验+gate 值表）=人工策展长期记忆，与 KernelBlaster 出厂 KB 同属「静态策展」路线，维护成本与跨硬件迁移性是共同软肋
5. **四仓共享 KernelBench 评测基座**：DeepWiki 快照（36 页）一份正本+交叉引用表，避免四份重复

## 执行方法与坑（钉版）

| 坑/决策 | 处置 |
|---|---|
| `snip` 包 `for` 循环/赋值必炸 | 铁律②重演：复杂操作一律 write 脚本文件再 bash 执行 |
| DeepWiki 未索引仓页面是 JS 壳 | webfetch 一次确认壳页特征（"Loading..."）后不再重试；改抓关联仓 |
| SSR HTML 1MB/页含侧栏 TOC | 抽取器从 `Menu` 标记后截正文；尾噪声按 marker 截断 |
| 数据集仓不适合全量图谱 | EvoKernel 用采样式 scan-result（人工策展 32 代表文件），全集统计走确定性审计脚本 |
| merge 后 docker/requirements.txt 边被 drop | 批次间节点命名不一致所致，1 条边损失可接受（记录在案） |
| ua-inline-validate.cjs 非现成文件 | 从 SKILL.md Phase 6 内嵌代码落盘 /tmp/opencode/ 囍四仓复用 |

## 遗留与后续建议

- 四仓图谱支持 understand 增量更新（fingerprints 基线已建，meta.json 钉了 commit）
- EvoKernel 若需逐 kernel 全量图谱，可在采样骨架上扩批（batches 生成脚本可复用）
- ReGraphT 空文件若上游补全，/understand 增量跑一次即可（19 文件，分钟级）
- DeepWiki 快照为 2026-01-16 基线，上游 KernelBench 演进后可重跑抓取脚本刷新

# deepseek-harness 知识库全链刷新（2026-11-04 会话）

## 状态快照（随进度更新）
- 仓库: /usr-data/data2/repos/deepseek-ai/deepseek-harness @ 8bd073392e（0.2.2-alpha.3，2026-11-03）
- 旧基线: 图谱 3368 节点/5160 边/12 层/16 步 @ 76fda729（2026-09-04，0.1.2-rc.1）；fingerprints 2188 文件
- 本轮 delta: deleted=455 changed=808 added=2991 → 重分析 3799 文件 / 176 批
- 扫描口径: 5048 文件（.understandignore 本轮重建：裁 snapshots/vendor/.github/benchmarks/website/patches、tests、locales(*.json+*.ts)、*.zh.md（en canonical）、.agents/notes/archived、css、desktop 安装机器）

## 完成项
- [x] Task1 rescan+对账：scan-result.json 已换新（旧版备份 scan-result-old-012rc1.json）；delta.json / reanalyze-set.json / batches/(176) / packages-map.json(379) 落盘
- [x] 派发模板 dispatch-template.txt（dsh 适配：@deepseek-ai 包名解析/.js→.ts/Cordis 语义/生成目录文档轻析四条款）
- [x] Task6a DeepWiki 刷新：46/46 TRUE_100（MCP 通道一次过，1.65MB）；新 7 页；旧 39 页归档 deepwiki-old-202609/；INDEX.md 重写；related/ 三仓保留（2026-11-04 18:5x）
- [x] surgery_merge.py 本轮版预写完毕（悬空三分类+符号级悬空归因增强）

## 批分组（10 批/组，18 组）
G01:1-10 core/api · G02:11-20 session/context · G03:21-30 · G04:31-40 · G05:41-50 · G06:51-60 · G07:61-70 · G08:71-80(client) · G09:81-90 · G10:91-100 · G11:101-110 · G12:111-120 · G13:121-130 · G14:131-140(experimental) · G15:141-150 · G16:151-160(docs/.agents) · G17:161-170(apps/scripts) · G18:171-176

## 进行中
- [ ] Task2 批分析 176 批（4 并发车道；每完成一组台账打勾）
  - 18:47 派发 G01-G04（批 1-40）4 worker；18:56 复核 products=0（首批 ~15-20min 正常）；worker 在仓根建辅助脚本 scan_imports.py/extract.py（历轮常态，收尾清理）
  - **19:05 G01 被 1302 杀**（死前正修 batch-003 的 calls 边）→ 查盘（001-003 全落）→ SendMessage 复活续跑 004-010。19:06 盘面 9/176：001-003(G01) 011-012(G02) 021(G03) 031-033(G04)
  - **19:13 G04 被 1302 杀**（死前已核实 readUpdate 行号 89-132，正写 batch-034）→ SendMessage 复活续写 034-040。账户速率压力大，复活与派发错峰
  - **20:5x 进度核查**：53/176（G05 至 047、G06 至 054、G07 至 062、G08 在飞 071+）；抽验 batch-062（client UI 域）锚 5/5、imports 55/55 零坏——质量稳定。累计入图约 2300n/4400e（G01-G04 已收官 1763n/3733e+在飞批次）

## Task5 预备（explain 选篇对账，2026-11-04 19:0x 完成）
- 14 篇旧目标交叉 delta：**12 篇 CHANGED 需重写**；core-scope 目标 UNCHANGED 保留原篇；landlock-main 目标 DELETED——`native/landlock-run/` 已整体改名 `native/system/`（新 sibling flock.c + docs/cli-contract/flock-contract），重写目标改 `native/system/packages/entry/src/main.c`
- 新篇候选（图谱落成后按 hub 度+delta 定）：typert gateway / boot / api session-controller / sdk team-mode / experimental 代表
- 旧 README 路径注 `~/ai/explore/...` 已失效 → 收尾统一改 `/usr-data/data2/repos/deepseek-ai/deepseek-harness`

- [x] **G05 ✅ 21:0x**（批 41-50 全落：316n/714e，imports 零差；甄别：fork 种子=父会话已完成 turn 均衡前缀+捕获入子持久转录、workflow-ptc guest-source.ts 是生成器产出的自包含 ESM 字符束（源-束双轨）、指向 typert/protocol 与 vendor 的 inherits 跳边防悬空语义入 summary）→ 补位派发 G09（批 81-90）
- [x] **G04 ✅ 20:4x**（批 31-40 全落：298n/550e，imports 210/210 零差；甄别：HarnessError 实在 llm/src/error.ts、TypertRemoteService 在 typert/protocol/src/index.ts:250；1302 死前 batch-034 已完整落盘复活后独立验收采纳）→ 补位派发 G08（批 71-80）
- [x] **G02 ✅ 20:2x**（批 11-20 全落：569n/1073e，imports 421/421 零差，锚 28/28；tree-sitter 漏 abstract class 四处手工补=SessionPersistence/FileReferenceService/SessionTelemetryBackend/CompactionEngine；scoped 两段包名切基坑）→ 补位派发 G07（批 61-70）
- [x] **G03 ✅ 20:0x**（批 21-30 全落：409n/854e，imports 全 1:1，锚 10/10；shell 执行器族/ssh 组/terminal PTY 全景入图；行号提取器三 bug 自修后重扫）→ 补位派发 G06（批 51-60）
- [x] **G01 ✅ 19:2x**（批 1-10 全落：487n/1256e，imports 745/745 零差，锚抽验 20/20；甄别：dsh-session→packages/core/session、api 包 Host/Client 双编译面、Typert 生成 Client 面在 lib/ 非源树=诚实缺口 surgery 不补；vendored 依赖 74 条按外部依赖不发）→ 19:2x 补位派发 G05（批 41-50）

## 1308 接力协议（2026-11-04 23:34 预计到墙 · watchdog 自动续航）
全局机制已在位并验证：`~/.claude/bin/claude-429-watchdog.sh`（v3，crontab */10 ensure + 进程常驻；18:03 那波 1308 已自动复活 3 个会话实证）。本会话（sid c5cc9afb）到墙后：
1. watchdog 扫到 "[1308]...重置...23:3x" 错误文本 → 睡到重置点 → `claude --resume c5cc9afb --permission-mode bypassPermissions -p "继续被中断的任务"`
2. **复活实例动作序列**（严格按序）：
   a. 读本文件台账 + `ls products/batch-*.json` 按序号去重盘点已完成批
   b. 台账"进行中"各组对照：**盘上已有的批一律验收采纳不重做**（死前落盘优先原则）；在飞组可能死前已写完若干批，全部按序号收割
   c. 在飞组的 worker 先试 SendMessage 复活（browser-use 轮实证 1308 团灭后 2/4 可复活保留上下文）；复活失败或无响应再按 dispatch-template.txt 重派缺批（4 并发 Agent general-purpose，prompt 模式同前组）
   d. 176/176 齐后进 Task3 surgery（`python3 surgery_merge.py --dry` 先跑，看悬空归因再正式）
3. 典型死法：四 worker 同刻团灭（18:47 起 4 车道，23:34 时 G0x 各自在飞一组的中段）——按序号收割即可，零损失的充要条件=worker 每批落盘纪律（模板已含）
4. 若复活发生在 23:34 后 token 低峰，可维持 4 并发；若再遇 1302 连杀，降到 2 并发硬扛

- [x] **G06 ✅（死于收尾核验期，零损失）**批 51-60 全落盘
- **20:04-20:06 1308 五小时墙提前到**（重置 23:33:42；用户预判 23:34=重置点非到墙点）→ G07/G08/G09 同刻团灭 → watchdog 自动复活会话（23:34）→ **跨 1308 墙 SendMessage 三复活全成功**（G07 续 069-070 / G08 补 080 / G09 验 084 残卷后续 085-090）+ 派 G10（91-100）。23:34 盘面 80/176
  - 实证钉版：watchdog 恢复后 SendMessage 复活依然可达（browser-use 轮 2/4 → 本轮 3/3），死前落盘纪律零损失

- [x] **G08 ✅ 23:4x（复活后 3 分钟收官）**批 71-80 全落：560n/1207e，imports 628/628 零差；甄别：ui-plugin-manager 的 PluginRegistryProbe=TypertRemoteService(@Remote fastest() npm/npmmirror 竞速)、ui-settings/config-form.ts 刻意避开 api-remotes 防 Host tsc 死锁、巨文件取显著子集口径（1902 行取 24 节点）→ 补位派发 G11（批 101-110）

- [x] **G07 ✅ 23:5x（复活收官）**批 61-70 全落：489n/1089e，imports 595/595 零差（仅 2 条 */remote Typert 生成物 UNRESOLVED 如实不发）；memo(function) 形式组件漏提手工补口径固化 → 补位派发 G12（批 111-120）

## 断点续跑指令（新会话）
1. 读本文件；2. 对账 products/ 缺批 vs batches/（batch-NNN.json 1..176，用序号去重防 part 后缀）；3. 缺组按 dispatch-template.txt 派发（4 并发，Agent general-purpose，prompt=模板路径+组内批号清单）；4. 全齐后跑 surgery（改自 讲透vLLM/_update-20261028/surgery_merge.py，改 REPO/W 常量）--dry → 正式；5. phase4_prep → layers/tour tasks → finalize（pipeline-bin/understand/finalize_graph.py 修复版）→ ua-inline-validate 0 issues；6. explain 增量+DeepWiki 刷新+README 收尾
关键路径文件：delta.json / batches/ / products/ / surgery_merge.py / dispatch-template.txt

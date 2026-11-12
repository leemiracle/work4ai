# 10 · 上下文与持久化：transcript、checkpoint、组装管线

> 证据：minified 源码偏移考古（transcript record 表 `Vys`、FileHistory 系统、
> 组装管线）[S]。深报告（40 种 record 类型总表+resume 两遍扫描+dir-sync 还原）：
> `rea-claude/reports/10-context.md`。

## 1. Transcript JSONL（会话即文件）[S]

- 路径 `~/.claude/projects/<slug>/<sessionId>.jsonl`；slug=路径转连字符
  （>200 截断+base36 哈希）；
- **record 类型 40 种**，fold 语义四类：transcript / boundary-cleared /
  accumulate / last-wins；写策略三类：dedup-transcript / always / route-by-agent；
- 每行带 **parentUuid 链** + gitBranch + slug——对话是一棵显式的消息树；
- 写入工程学：100ms 批量 flush、32KB 元数据周期重写、**20MB→160MB 自适应
  物理压实**（rename 原子替换+并发写三重检测）。

**resume**：>5MB 走两遍字节级扫描（pass1 只抓 uuid/parentUuid 建图走链，
pass2 只 parse 链上行——不全量 parse 大文件）；断链时间戳兜底（≤5s）+
并行写恢复（共享 message.id 合并）。

## 2. checkpoint/rewind：纯文件备份（与 git 无关）[S]

- `~/.claude/file-history/<sid>/<hash16>@v<N>`：**硬链接去重**的快照版本链，
  内存快照上限 100；
- 每条 user 消息 turn 前建 preCheckpoint 快照；Edit/Write 前单文件 track；
- /rewind → open_message_selector → dry-run 预览 → code/conversation/both/
  summarize 五选项。

> **勘误**：chunk-wfta3tst（"git 集成"签名）实为 **dir-sync 引擎**（远程会话
> 工作区双向同步，forged-path/filter-attributes 防护）；**全仓无自动 commit**。

## 3. content-replacement：tool result 三级落盘 [S]

1. 执行时单条：阈值 `min(工具声明 max, 50KB 上限)` → 落盘
   `tool-results/<toolUseId>.txt`（目录符号链接安全走查：拒 nlink>1/项目外），
   替换为 `<persisted-output>` + 2KB 预览；
2. turn 起点聚合预算：按 assistant message.id 分组，tool_result 聚合 >200K 字符
   时**从大到小**挑可落盘项；替换经 content-replacement 记录写 transcript
   （重放可重建）；
3. microcompact 清老（见 02 册 §4）——三级共用同一替换状态；compact 后
   reconstructContentReplacementState 重建。
- 图片/文档永不替换；空结果 → `(tool completed with no output)`。

## 4. 上下文组装管线 [S]

- **CLAUDE.md 五层**：Managed → User → Project（根向 cwd 逐级）→ Additional →
  AutoMem；单文件预算 `max(40KB, 5%×窗口)`；
- msg0 = Jtr 包裹的 **isMeta user 消息**（section 顺序：claudeMd → userEmail →
  attachedProject → currentDate）——上下文不进 system prompt 而进首条消息；
- gitStatus 快照走 system prompt 末段；易变四节变更走 session_context
  attachment 重播（不是重发全量）。

## 5. readFileState（读后免重读的地基）[S]

成功读取记 `{content, mtimeMs, offset, limit, isPartialView}`（03 册 Edit
errorCode 6/7 的判定源）；microcompact 清旧结果时同步删 readFileState——
状态与内容共存亡。

## 6. 手搓启示（→ rl-and-agents/）

1. **对话即消息树**（parentUuid 链）：序列之外保留结构，rewind/分支/fork
   全靠它——mini 版加一个 parent 字段就获得树语义；
2. checkpoint 用硬链接快照（COW 语义、零拷贝）而非 git——**不要把版本控制
   混进状态管理**，两者解耦；
3. tool result 三级落盘+替换记录可重放：上下文超限不是"截断"而是
   "降级表示+可恢复"；
4. 两遍扫描 resume（先建图后 parse）是大 JSONL 的标准读法；
5. 上下文进 msg0 而非 system prompt：与缓存断点配合，动态内容不破坏
   system 前缀缓存。

# work4ai 项目直觉（AGENTS.md）

> work4ai = AI 学习知识库（600+ 文件，"讲透"系列宇宙）。治理框架：《复杂系统迭代work4ai.md》（复杂系统四视角：还原论/动力学/热力学/复杂系统）。
> 全局直觉见 `~/.config/opencode/AGENTS.md`；本文件是项目专属增量。

## 项目是什么

- 核心资产：`讲透X/` 系列（五幕：直觉→数学→代码→不足→应用）+ `用例库/`（279 仓深读卡）+ `前沿与媒体/`（100+ 专题清单）+ `Agent框架案例/`（仓库深读笔记）+ 元理论（故事迭代/熵论/复杂系统三支柱）
- 姊妹库索引：`本地仓库全景-Cworkspace迭代索引.md`（C:\workspace 21 仓总表 + Top10 合并清单）
- 深潜方法论：`透视GitHub-AI高星仓库全景.md`（生态观测锚点）

## 写入规范（知识卡宪法）

1. **新卡必须挂网**：写入任何单元先读该单元 README，产出后必须更新其索引/映射表——**孤儿文件 = 死亡内容**（孤儿率 <10% 健康线）
2. **证据锚点**：仓库分析一律 `文件:行号` 级证据（用例库标准）；引用规模数字必须实测（gongwen-mastery 虚标教训）
3. **卡片 frontmatter**：card_id / title / universe / burke（场景/主体/能动/行动/目的/张力/弧线）/ status / refs / updated
4. **合并优先级**：补桥互链 > 搬内容；改动讲透系列须保持五幕结构（普适类，见复杂系统篇 §2.2）
5. 中文为主；仓库名/产品名/代码保留原文

## 会话启动附加动作

- 读 `.agent/MEMORY.md` + `.agent/USER.md`（自成长记忆，见全局协议）
- 长任务先查 `.research/`（research 流水线工作区，断点续传）

## 项目红线

- `用例库/` 分册结构（A/B/C/D/E01-E24）不可重排——它是 279 仓的稳定坐标系
- 讲透单元的 README 篇目表 = 该宇宙的目录宪法，增删须给理由
- `.workbuddy-ai/memory/` 是历史日志（08-13~15），只读不迁；新日志写 `.agent/journal/`

## 公开仓脱敏规范（2026-08-20 治理，主仓 public @leemiracle/work4ai）

- **绝不入库**（.gitignore 已列）：`.agent/`（个人档案/记忆）、`xkernel-llm-constraints/`、`.research/xk-issues/`、`dual-chat/`（内部工作与私人内容）
- **内容替换规则**（写入任何文件前自查）：`/data/usershare/ai`→写 `~/ai`；`/home/lwz`→写 `~`；内网 IP/硬件型号→写"内网GPU服务器"等占位；不写公司邮箱/真名（git 作者统一 leemiracle noreply，mailmap 已配）
- 历史已 filter-repo 清洗（121 commit 重写，敏感旧史随 backup 分支删除）；新提交前如需再清历史：先提交全部工作区再跑 filter-repo，且必须删除远端 backup 分支

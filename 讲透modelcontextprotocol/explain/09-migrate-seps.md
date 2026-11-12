# 09 · migrate_seps.js —— SEP 体系的一次性历史迁移器

## 角色定位

`migrate_seps.js` 是仓库根目录 243 行的 CommonJS 裸脚本，图谱中为 `file:migrate_seps.js` 节点，归 L14「构建生成链与文档站点装配」层——全仓「源→产物」流水线的机械层（scripts 五脚本 + 本文件 + docs 站点资产 + plugins），而它是其中唯一已停转的齿轮。唯一使命写在文件头注释（migrate_seps.js:3-10）：把 GitHub issues 形态的旧 SEP（Specification Enhancement Proposal）评审体系批量转成仓内 markdown 文件，按 `{number}-{slug}.md` 存入根 seps/ 目录。

考古第一课：为什么根 seps/ 是 43 个编号 .md 加 README.md 与 TEMPLATE.md（共 45 文件），docs/seps/ 却是 43 个 .mdx 加 index.mdx（共 44 文件）？因为这是两段历史的分层化石——本文件生成的是**源树**（L07「SEP 提案·根目录源树」，PR 评审用原稿），scripts/render-seps.ts 再把源树渲染成**站点树**（L08「SEP 提案·站点渲染树」，Mintlify 页面）。

CLAUDE.md 写着 `npm run generate:seps`，但 package.json:28 实证该命令执行的是 `tsx scripts/render-seps.ts`——migrate_seps.js 不在任何 npm scripts、不在任何 CI workflow（全仓 grep 仅图谱缓存命中）。钉版结论：纯历史脚本，一次跑完即退役。

## 内部结构

243 行、8 个 function 定义，图谱收录其中 6 个函数节点，构成六段管线：

- **fetchSEPIssues（:26-35）**：execSync 一条 `gh issue list --label SEP --state all --limit 500`（:30），指定 number/title/state/labels/body/createdAt/closedAt/author 八字段 JSON。
- **getStatusFromLabels（:38-50）**：标签小写化后按 :42-47 优先级链映射——final→Final、accepted-with-changes→Accepted、accepted→Accepted、in-review→In-Review、draft→Draft、proposal→Draft；无匹配返回 null（:49）。
- **parseIssueBody（:59-110）**：标题剥离 `[SEP-n]` 前缀（:63 正则）；正文逐行抽 Type（:79-82）/Authors（:85-88）/Sponsor（:91-94）/PR 号（:97-100）/Created（:103-106）；缺省回退 Standards Track（:65）与 issue 作者（:67）。
- **cleanBodyContent（:113-151）**：正文清洗状态机——:127 识别 `## Preamble` 或 `# SEP-` 开头进入元数据段，:133 遇 Abstract/Motivation/Specification/Overview 主节放行，:140 滤残留元数据行，:145 砍头部空行。
- **generateSEPMarkdown（:154-177）**：拼目标格式——标题（:158）+ Status/Type/Created/Author(s) 列表（:159-162）+ 可选 Sponsor（:164-166）/PR（:168-170）+ **Issue 回链（:172）**+ 正文。
- **migrateSEPs（:190-235）**：主循环——逐条筛迁移资格、:206 记跳过日志、:213 解析失败即跳过、:220-221 清洗并生成、:223 拼文件名、:226 writeFileSync 落盘、:231-234 打印 Migrated/Skipped/Total 汇总。

另有 shouldMigrate（:53-56，只放行 Accepted/Final，:55）与 titleToFilename（:180-187，slug 化并截 50 字符，:186）两个小函数未单独成节点。死代码化石：STATUS_MAPPING（:17-23）声明后全文仅 :17 一处命中、从未被引用——映射实际由 getStatusFromLabels 的 if 链完成，是半途改实现的遗迹。骨架：:12-14 仅 require 三个 Node 内置模块，零第三方依赖；:194 输出目录定为 `__dirname/seps`；:197-199 缺失则递归建目录；:238-243 try/catch 直接执行、出错 exit 1。

## 外部连接

**上游：GitHub，但走 gh CLI 子进程而非 REST API**（:29-31 execSync）。依赖方式=本机装好 gh 且已登录。这正是图谱中它没有任何 imports 边的原因——唯一外向边是 depends_on → `document:seps/README.md`（weight 0.6，指向输出目录的说明文档）；上游 GitHub 与下游 seps/*.md 都不在模块系统里。

**下游：以 Issue 回链为指纹判定的迁移产物共 20 篇**（1024/932/973/985/986/990/991/994/1034/1036/1046/1302/1303/1319/1330/1577/1613/1686/1699/1730），每篇头部的 `- **Issue**: #N` 行就是 :172 的独家指纹。其余 23 篇编号 SEP 为 PR 纪元新增，头部是 `- **PR**: <URL>` 格式（932/990/994 兼有两种，应是迁移后手工补链）。

**与 render-seps.ts 的时代接力**：第一代=migrate_seps.js，GitHub issues → seps/*.md，一次性；第二代=scripts/render-seps.ts（486 行 TS），seps/*.md → docs/seps/*.mdx + 索引 + docs.json 导航（readAllSEPs :251-264 读源 → parseSEPMetadata :44-87 → 单页 :141-177 / 索引 :182-246 → updateDocsJson :317-378，main :383-482），持续运行——package.json:28 generate:seps、:42 check:seps（--check 漂移检测）双入口，CI 由 .github/workflows/render-seps.yml 驱动。一句话分工：migrate 把历史搬进仓库（跑一次），render 把仓库搬上网站（每次 PR 都跑）。

## 数据流

以 issue #1024 为例走完整旅程：

1. **打捞**：`gh issue list --label SEP --state all` 拉全量（:30），issue 编号即将成为 SEP 编号（:155 `sepNumber = issue.number`）。
2. **状态映射与闸门**：标签按 :42-47 优先级定状态；shouldMigrate 只放行 Accepted/Final（:55）——Draft/In-Review/proposal 一律跳过并计数，seps/ 只收已成文提案。
3. **元数据抽取**：正则逐行扫 issue 正文（:73-107），抽不到就用默认值。
4. **正文清洗**：状态机砍 Preamble 元数据段（:127/:133/:140），只留 Abstract 起的正文。
5. **落盘**：拼头部列表 + 清洗后正文（:158-174），titleToFilename slug 化（:183-186），:223 拼文件名，:226 写盘。

迁移后人工修整的痕迹（产物形态反推）：其一，`1024-mcp-client-security-requirements-for-local-server-.md` 的 slug 恰好 50 字符且以连字符收尾——正是 :186 `substring(0, 50)` 截断的化石指纹。其二，seps/1024 该文件 :7 的 `- **Issue**: #1024` 是迁移器独家输出；新纪元 SEP 没有此行。其三，新纪元字段迁移器根本生成不了：seps/1850-pr-based-sep-workflow.md:6 的 `- **Accepted**: 2025-11-28, 8 Yes...`（投票记录）、:9 的完整 PR URL（迁移器只产 `#数字` 短格式，:169）；seps/2133-extensions.md:7 的 `Sponsor: None (seeking sponsor)`（迁移器遇 null 直接省略该行，:164-166）。另外 1850 与 2133 的 PR 字段指向两个不同仓库（specification vs modelcontextprotocol），编号空间不止一个——跨仓考古别拿编号大小当时间序。

## 设计决策

**为何从 issues 迁仓内文件**：答案写在迁移产物里——seps/1850-pr-based-sep-workflow.md（SEP-1850，:5 Created 2025-11-20，Final）本身就是「PR 化 SEP 工作流」提案，Motivation（:15 起）列旧流程四大痛点：内容分散在 issue/外链/PR 多处、长文在 issue 正文难以迭代协作、issues 缺 Git 级版本控制、状态管理无一致机制。CLAUDE.md 的 Issue Creation 节也钉了现行政策：SEPs are pull requests adding a file to `seps/`, not issues。

**为何迁移器留仓不删**：可重放（脚本是「issue ↔ 文件」映射规则的机器可读版）、可审计（每篇老 SEP 靠 :172 的 Issue 回链溯源到原始讨论）、物证完整（L14 生成链唯一的第一代遗物，删了就断 issues 时代的实证）。

**工程代差是刻意保留的另一半理由**：本文件是根目录 CommonJS 裸脚本、零依赖、execSync 同步一把梭、无类型无测试无 --check；scripts/render-seps.ts 则是 TS + SEPMetadata 接口 + tsx + --check 干跑 + CI 集成。两代同仓并存即工程规范演进的对照标本。

## 新人提示

- **现在还需要跑吗？不需要，更不该跑**。判定实证：package.json 四条相关链（:24 generate、:28 generate:seps、:42 check:seps、:45 prep）无一指向它，CI 亦无入口。且 :226 writeFileSync 无条件覆盖——今天再跑会用 issues 陈旧数据砸掉 43 篇已被手工维护多轮的源稿（Accepted 投票记录、PR URL 等新字段全被抹掉）。
- **考古 SEP 早期史从哪入手**：seps/README.md（现行工作流）→ seps/1850-pr-based-sep-workflow.md（换代文档）→ 20 篇老 SEP 头部的 `- **Issue**: #N` 回链跳回 GitHub 原始 issue 看讨论（:172 就是给后人留的时光机）→ 本文件对照 seps/1024 头部看「迁移器输出形态」。
- **别把它当活代码改**：无调用方、无测试、无类型。SEP 文档有问题的正确路径是改根目录 seps/*.md 源稿 → `npm run generate:seps` 重渲染 → `npm run check:seps` 校验。本文件是博物馆展品，只读。

> 非空白字符 4763 / 锚 86（82 行号锚全部源码核实：migrate_seps.js 58 + render-seps.ts 6 + package.json 4 + seps 产物 8 + 图谱层锚 4；另 6 处图谱函数行区间与源码一致）

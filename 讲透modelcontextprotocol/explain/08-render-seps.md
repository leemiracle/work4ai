# 08 · render-seps.ts —— SEP 双树的唯一桥梁

## 一、角色定位

`scripts/render-seps.ts` 在图谱中是 `file:` 节点（L14 层），是 MCP 规范仓 **SEP 双树结构的唯一连接器**：上游根 `seps/*.md`（GitHub PR 评审面，L07 层 46 节点），下游 `docs/seps/*.mdx`（Mintlify 站点阅读面，L08 层 44 节点）。磁盘实测 `seps/` 45 文件、`docs/seps/` 44 文件——差一的账第五节拆解。它由 `package.json:28` 的 `generate:seps` 驱动（`tsx scripts/render-seps.ts`），`package.json:42` 的 `check:seps` 是同脚本的 `--check` 闸门模式。批分析称其 depends_on `seps/.keep`——**勘误：磁盘实测无此文件**，幽灵边。第三类下游常被忽略：`docs/docs.json` 的 SEPs 导航 tab 与 43 条短链重定向（`render-seps.ts:25`）。

## 二、内部结构

487 行分四区：

**元数据层（L44-124）**：核心 `parseSEPMetadata`（`render-seps.ts:44`）。**勘误任务书前提：无 markdown-it、无 gray-matter，纯自研正则**——因为源文件根本没有 YAML frontmatter，元数据是 bullet 列表（`- **Status**: Final`），故 L60-72 用八个 regex 逐字段抽取：标题（:60）、Status/Type/Created/Accepted（:64-67）、多行 Author(s)（:68，跨行续行正则）、Sponsor（:71）、PR（:72，兼容 `#123` 与 `/pull/123` 两种写法）。L46 先过滤 TEMPLATE.md/README.md/`0000-` 草稿；L51 文件名正则 `/^(\d+)-(.+)\.md$/` 抽出 SEP 号与 slug；L83 若 PR 行缺失则 prNumber 回退为 SEP 号——这是 SEP-1850 制度"SEP 号=PR 号"的内化。辅助函数四个：`formatAuthors`（:92，`@name` 转 GitHub 链接）、`formatPrLink`（:99，**硬编码仓地址**）、`truncateTitle`（:106，侧栏标题 40 字截断）、`getStatusBadgeColor`（:114，八状态→八色：final=green/accepted=blue/in-review=yellow/rejected·withdrawn=red/dormant=orange/superseded=purple，兜底 gray）。

**渲染层（L130-246）**：`FINAL_SEP_NOTICE`（:130）是注入每个 Final 页的历史记录通告；`generateSEPPage`（:141）生成单篇 MDX——L144 用 `indexOf("## Abstract")` 切片，**头部区整体丢弃**；L151-155 注入 frontmatter 三字段（title/sidebarTitle/description）；L157-160 双 Badge（状态色+类型灰）；L162-171 Field/Value 元数据表，L169 Accepted 为条件行（2640 无此行、1850 有）。`generateIndexPage`（:182）生成索引页：L184 按号降序、L187-194 状态分组统计、L200 总表行模板、L219-221 提交指引 Card、L235-244 八状态定义表。

**聚合层（L251-378）**：`readAllSEPs`（:251）readdirSync 过滤 .md；`groupSepsByStatus`（:269）按 :273 的八态顺序排导航组，L277-279 把 `in-review` 这类连字符状态标题化为 `In-Review`；`updateDocsJson`（:317）外科手术式改 docs.json——L343-348 清 Community tab 的遗留 SEPs 组、L351-363 把 SEPs tab 插在 Community 前、L311 的 `SEP_SHORT_LINK_SOURCE` 正则圈定托管范围，L366-368 **只替换自己管的重定向、手写的 121-43=78 条不动**、L369-375 生成 43 条短链。

**main 双模式（L383-487）**：L384 解析 `--check`；L401 把全部产物（index+43 页+docs.json）收进 expectedFiles；check 模式（L419-462）写临时目录、L437 先过 Prettier 再与磁盘逐文件比较（与写模式对齐，避免假阳性），L461 任何漂移 exit 1；写模式（L466-478）落盘后同样跑 Prettier。

## 三、外部连接

**上游**：根 `seps/*.md` 43 篇（加 README/TEMPLATE 共 45 文件），每篇是一个 PR 的评审产物——SEP-1850（`seps/1850-pr-based-sep-workflow.md`）制度化了这个流程：提案存 markdown、SEP 号取 PR 号、Git 管版本史，替代旧的 GitHub Issues 流程。**下游**：`docs/seps/*.mdx` 43 页 + `index.mdx`，外加 `docs/docs.json`。**migrate_seps.js**（仓根，243 行，**不在 scripts/ 下**）是历史一次性迁移器：`gh issue list --label SEP`（`migrate_seps.js:22`）拉旧 issue 按 label 映射状态转 markdown 落 `seps/`——迁移是 2025-11 的一次性动作，render-seps 是持续幂等渲染，二者一个造源树、一个养渲染树。**CI**：`render-seps.yml` 由 `seps/**/*.md` 与脚本自身变更触发（:8-9）；PR 上跑 `check:seps` 当闸门（:39，源树改了没跑 generate 就合并会被拦）；push main 后跑 `generate:seps`（:44），L50 用 `git status --porcelain` 检测漂移，L62 以 github-actions bot 身份自动 commit "docs: auto-render SEPs documentation"。另有 `sep-lifecycle.yml` 管 SEP 状态机（label 事件+周一全量扫），它是源树元数据的上游扰动源。

## 四、数据流：SEP-2640 的渲染旅程

SEP-2640 经 PR #2640 合并落成 `seps/2640-skills-extension.md`，CI 触发渲染，七步旅程：

1. `readAllSEPs` 读全文，文件名正则拆出 number=2640、slug=skills-extension；
2. 八个 regex 抽元数据：Status=Final、Type=Extensions Track、Created=2026-04-23、四位 @作者、PR 链接；
3. `getStatusBadgeColor("Final")` → green；
4. L144 从 `## Abstract` 切片，**源文件 L15-19 的工作组 `<Note>` 被整体丢弃**——渲染版头部 grep 实证无此 Note（正文 References 的 charter 链接不受影响）；
5. 组装：frontmatter 三字段 + green/gray 双 Badge + FINAL_SEP_NOTICE + 九行元数据表（2640 无 Accepted 行）+ 透传正文；
6. 旧 SEP 有一处真实的链接改写：1850 源 `seps/1850-pr-based-sep-workflow.md:11` 的 PR 是旧仓 `specification/pull/1850`，`formatPrLink` 硬编码新仓地址后渲染版统一为 `modelcontextprotocol/pull/1850`（GitHub 重定向兜底）——**勘误：正文相对链接零处理，不存在通用链接重写函数**；
7. docs.json 收尾：Final 组追加 `seps/2640-skills-extension` 页 + `/seps/2640` 短链。

对照头部差异即"渲染器注入的字段"：源是 H1+bullet 元数据；渲染版（`docs/seps/2640-skills-extension.mdx:1-31`）是 frontmatter+Badge+Notice+表格，正文自 `## Abstract` 逐字相同。

## 五、设计决策

**为何双树**：受众不同。源树为 GitHub diff 评审优化——纯 markdown、bullet 元数据、元数据变更即普通 diff 行；渲染树为 Mintlify 优化——frontmatter 供站点元信息、Badge/Card/Note 是 MDX 组件、导航进 docs.json。单树要么牺牲评审体验（MDX 组件污染 diff）要么牺牲站点体验。**迁移/渲染分离**：migrate 一次性有外部副作用（gh 命令、不可逆落盘），渲染幂等可重复跑（同输入同输出，CI 才敢 bot 自动 commit）。**45:44 差一账（磁盘实证）**：45=43 SEP+README+TEMPLATE，L46 过滤后 43 篇入渲染，产出 43 mdx+1 个 index.mdx=44。图谱 L07 46 节点=45 文件+1 幽灵 .keep；无任何 SEP 被漏渲染或合并。**check 先 Prettier 再比较**（L437）：与写模式格式化对齐，否则格式差异被误报为内容漂移。**docs.json 只托管自己的重定向**（L366）：手写 78 条与脚本 43 条共存不互踩，这是"生成器侵入既有配置文件"的教科书做法。

## 六、新人提示

- **新增 SEP 只动源树**：拷 `seps/TEMPLATE.md`（其 :5-10 定义八状态/四类型），改号改名，跑 `npm run generate:seps`——或直接推 PR 让 CI 渲染，但 PR 上 `check:seps` 会拦"改了源没跑 generate"的提交，本地先跑 `npm run prep`（`package.json:45`）最稳。
- **改渲染样式去 render-seps.ts**，不要手改 `docs/seps/*.mdx`——它们是生成物，下次渲染即被覆盖（CI 的 porcelain 检测就是防这种漂移）。
- **坑一**：Status 拼写不匹配八态（如 `Final ` 带尾空格已 trim，但 `Accepted-With-Changes` 这种）落兜底 gray 徽章，不报错只变色。
- **坑二**：文件名不合 `数字-slug.md` 约定只 `console.warn` 后跳过（L52-54），渲染树里静默缺页。
- **坑三**：Abstract 之前的任何内容（自定义 Note、扩展字段如 2640 的 Extension Identifier）都会被丢弃，想上站点请写进 Abstract 之后。
- **现状**：43 篇全 Final（grep 实证），index.mdx 的 Summary 只有一行、docs.json 只有一个 Final 组——Draft/In-Review 分组逻辑（L273）当前无数据触发，不是死代码。

---
源文件：`/usr-data/data2/repos/aaif-projects/repos/modelcontextprotocol/scripts/render-seps.ts`（487 行）

> 非空白字符 4790 / 锚 72

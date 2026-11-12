# 04 · 文档站构建链：mkdocs、宏系统与 llms 三件套

> 区域：`mkdocs.yml`（205 行站点配置）+ `.mkdocs/`（macros.py 宏系统 + overrides 模板 + 根跳转模板）+ `scripts/`（8 个 shell 脚本 + clean_schema_names.py）+ `docs/llms*.txt` 三件套 + CI `.github/workflows/docs.yml`
> 仓根：`/usr-data/data2/repos/aaif-projects/repos/A2A`。本文所有行号锚均经 grep/Read 从源文件核实（2026-10-24）。

## 角色定位

在知识图谱的 8 层架构里，本篇覆盖 L05「文档站构建层」。对一般项目，构建链是配套基础设施；对 A2A 这种**规范仓**，它就是生产线本体——仓里唯一手写的"产品内容"是 `specification/a2a.proto`（812 行）和 `docs/` 下的叙述性 Markdown，其余一切发布物都是从这条生产线流出的派生物：

1. **人读的 HTML 站点**（a2a-protocol.org，mkdocs-material 渲染 + mike 版本化）；
2. **机器读的 JSON Schema**（`specification/json/a2a.json`，protoc 工具链生成，`build_docs.sh:9` 定位）；
3. **LLM 读的 llms 三件套**（`build_llms_full.sh:8` 聚合产物 + 两份手写索引）。

三条输出线共享同一个真相源，这是全链最重要的不变量：`docs/llms-reference.txt:4-6` 白纸黑字声明 "This file is non-normative. The Protobuf definition (`specification/a2a.proto`) is the source of truth"；`docs/llms.txt:10` 同样把 proto 文件标为 "Source of truth for the wire protocol"；规范页里的 58 张对象表格也不是手写 Markdown，而是构建时由宏直接解析 proto AST 现场渲染（见下节）。

**nav 口径勘误**：任务书说"nav 26 页"，实测 `mkdocs.yml:21-62` 的 nav 共 **32 个叶条目 = 29 个本地 .md + 2 个外链 + 1 个生成 html**（脚本计数实证）。外链是 `mkdocs.yml:55`（DeepLearning.AI 课程）与 `:62`（GitHub Release Notes）；生成 html 是 `:43` 的 `sdk/python/api/index.html`——Sphinx 产物，源仓 checkout 里不存在（`.gitignore:214` 排除）。任何按"26"做的对账都会差 3-6 项，以 29 个本地 md 为准。

## 内部结构

### mkdocs.yml 配置全景

单文件 205 行，六个配置段落分工清晰：

| 段 | 行号 | 要点 |
|---|---|---|
| 站点元信息 | `:2-8` | `site_url: https://a2a-protocol.org/`（`:3`）、`site_dir: site`（`:7`）、`edit_uri: edit/main/docs/`（`:8`） |
| 环境注入 | `:11-18` | `exclude_docs` 排除 docs/README.md（`:11-12`）；**`a2a_version: !ENV [MIKE_VERSION, "dev"]`**（`:15`）——版本号不是写在配置里而是从 CI 环境变量读入，本地构建默认显示 `dev` |
| nav 导航树 | `:21-62` | Home/Documentation(8)/Extensions(3)/Specification(3)/Resources/Community(3)/Blog 七组；Documentation 组 `:24-31` 覆盖 what-is-a2a 到 multi-tenancy 八个概念页 |
| 主题 | `:81-128` | material 主题 + `custom_dir: .mkdocs/overrides`（`:82-83`）；features 20 项（`:109-128`），末尾 `versioning: provider: mike`（`:127-128`）把多版本职责整个外包给 mike |
| Markdown 扩展 | `:131-161` | **`pymdownx.snippets` 的 `base_path: .` + `url_download: true`（`:146-148`）是规范页"按锚嵌入外部内容"能力的地基**（03 篇已详述其消费方） |
| 插件 | `:164-204` | blog（`:165-167`，`post_url_format: "{date}/{slug}"`）、search、**macros（`:169-170`，`module_name: .mkdocs/macros`）**、redirects（`:171-202`，30 条历史 URL 映射，如 `:175` 把旧 `specification/agent-card.md` 重定向到新锚点 `specification.md#5-agent-discovery-the-agent-card`）、mike（`:203-204`，`canonical_version: latest`） |

两处"注释即文档"的联动值得注意：`repo_name/repo_url` 被整体注释掉（`:65-68`），注释明说原因是"the A2A repo is now shown in the SDK links row in the header (see .mkdocs/overrides/partials/sdk_repos.html)"——配置禁用与模板补位是同一决策的两半；`copyright`（`:71`）里埋了一句 "Reading as an AI agent? Start at llms.txt"，是 llms 三件套在人类页脚的镜像入口。

### macros.py：三宏 + 六辅助的 proto 直读渲染器

`.mkdocs/macros.py` 共 325 行。所谓"六函数宏系统"的精确构成是：**1 个 `define_env` 入口（`:48`，mkdocs-macros 约定俗成）内含 1 个局部函数 `_parse_proto`（`:51-58`），注册 3 个 `@env.macro` 装饰的宏，外挂 6 个模块级辅助函数**。

三个宏承担规范页全部表格的渲染，签名完全同构——第一个参数是 proto 里的类型名，第二个参数默认 `proto_file: str = 'specification/a2a.proto'`（`:62`、`:126`、`:148` 三处默认值，即任务书所说"三宏默认解析 a2a.proto"）：

| 宏 | 定义行 | 输出 | 消费 |
|---|---|---|---|
| `proto_to_table` | `:60-122` | 消息字段四列表（Field/Type/Required/Description，表头 `:109`） | `specification.md` 55 处 + `topics/extensions.md:93` |
| `proto_enum_to_table` | `:124-144` | 枚举值两列表（Value/Description，`:140-142`） | `specification.md:788`（TaskState）、`:800`（Role） |
| `proto_service_to_table` | `:146-187` | 服务方法四列表（Method/Request/Response/Description，`:183`） | `specification.md:2580`（A2AService，10.3 节） |

渲染链路五步（全部纯 Python，零 protoc 依赖——依赖是 `proto_schema_parser` 与 `tabulate`，`:10-22` 导入，`requirements-docs.txt:9-10` 安装）：

1. **定位解析**：`_parse_proto`（`:51-58`）用 `Path(env.conf['docs_dir']).parent / file_path`（`:53`）把默认相对路径锚到仓根，文件缺失直接抛 `FileNotFoundError`（`:55`）——宏层则兜底成 `**Error:**` 粗体文本（`:67-68`），不让整站构建崩掉；
2. **注释挂载**：proto AST 不自带注释归属，`_attach_comments`（`:227-239`）用缓冲区把每个 Comment 元素附着给紧随其后的真实元素，并递归处理嵌套 Message/OneOf（`:238-239`）——这是"proto 注释即文档 Description 列"的全部机制；
3. **类型查找**：`_find_type`（`:268-277`）递归按名字+类过滤匹配，所以嵌套消息也能被引用；
4. **字段行组装**：`_process_field`（`:280-319`）做三件聪明事——优先取 `json_name` 选项作展示名（`:289-292`），没有则 `_snake_to_camel_case`（`:322-325`）把 proto snake_case 转 camelCase，与 JSON 绑定的实际字段名一致；类型列经 `_format_type_for_docs`（`:242-265`）把非原始类型渲染成页内锚链接 `[\`Task\`](#task)`（`:256`）、repeated 渲染为 `array of`（`:262-263`）、map 渲染为 `map of X to`（`:258-260`）；Required 列综合 cardinality 与 `field_behavior` 选项判定（`:304-315`），oneof 成员单列 `Optional (OneOf)`（`:310-311`）；
5. **表格输出**：`tabulate(rows, headers, tablefmt='github')`（`:110`、`:184`）产 GitHub 风格管道表；oneof 组再追加一行规范性注记 "`A Task MUST contain exactly one of the following: ...`"（`:113-120`）。

`_extract_comments`（`:195-224`）里藏着一份**注释黑名单**（`:212-221`）：`protolint:`、`--8<--`、`Next ID:`、`api-linter`、`aip.dev/not-precedent` 五类 proto 工程注释被过滤，不进文档——对应 `a2a.proto:361` 的 `// Next ID: 20` 与 `:85-87` 的 api-linter 开关注释，实测确实不出现在任何渲染表格里。

### 八脚本分工

`scripts/` 目录九个文件，其中 8 个 shell 脚本按职能三分为**构建四件 + 质量三件 + 部署一件**：

| 脚本 | 行数 | 职责 | 关键行 |
|---|---|---|---|
| `build_docs.sh` | 98 | 总编排：schema 新鲜度检查→发布 spec 文件→SDK 文档→mkdocs/mike→ADR 拷贝 | 见下 |
| `proto_to_json_schema.sh` | 126 | proto→JSON Schema 单体转换 | 见"外部连接" |
| `build_sdk_docs.sh` | 68 | Sphinx 从 PyPI 装包生成 Python API 参考 | 03 篇已详述；`:26` 装 `a2a-sdk`、`:39` `sphinx-apidoc -f -e`、`:44/:49` html+text 双格式 |
| `build_llms_full.sh` | 150 | 全文档聚合为单文件 | 见下 |
| `deploy_root_files.sh` | 88 | 部署根文件到 gh-pages | `:16` 五文件清单（404.html/robots.txt/llms.txt/llms-reference.txt/llms-full.txt）、`:18` 三目录（root-redirects 的 extensions/bindings/.well-known） |
| `format.sh` | 33 | markdownlint --fix 自动格式化 | `:31` 对 `docs/` 跑 `markdownlint --fix`；`:7` 先调 sort_spelling.sh |
| `lint.sh` | 25 | Super Linter（Docker 镜像 slim-v8） | `:16-25` docker run 挂载仓根，`:12` 自动探测默认分支 |
| `sort_spelling.sh` | 16 | 拼写白名单排序去重 | `:16` `LC_ALL=C sort -u` 处理 `.github/actions/spelling/allow.txt` |

`build_docs.sh` 的编排顺序即生产序：`regen_needed()`（`:16-29`）用 mtime 对比 proto 与 json，**双 stat 语法兼容 Darwin（`:22-23` stat -f）与 Linux（`:25-26` stat -c）**；陈旧则调 proto_to_json_schema.sh，**转换失败只警告不中断**（`:36`）；随后无条件把 schema 与 proto 拷进 `docs/spec/`（`:46-60`，这是 `definitions.md:15/:30` 两处 `--8<--` 嵌入的文件来源）；再调 `build_sdk_docs.sh`（`:63-69`）；把 `.doc-venv/bin` 前置进 PATH（`:72-74`）后按第一参数分叉——`deploy` 走 `mike deploy`（`:76-79`），否则 `mkdocs build`（`:81-82`）；最后把住在 docs/ 之外的 `adrs/` 目录拷进 `site/adrs`（`:85-96`），因为规范页链接了 ADR 但 MkDocs 只认 docs_dir。

### llms 三件套的生成关系

三件套是**两份手写源 + 一份构建产物**的金字塔，不是三份并列输出：

| 文件 | 性质 | 规模 | 定位 |
|---|---|---|---|
| `docs/llms.txt` | 手写源（入库） | 108 行 | 策展索引：H2 分区（Start here `:32`/Specification `:39`/Core topics `:46`/Extensions `:56`/Build an agent `:62`/Key Documents `:103`）+ 顶部十条 Links（`:7-16`） |
| `docs/llms-reference.txt` | 手写源（入库） | 102 行 | 浓缩参考：协议速览，`§2` Core Data Objects 起（`:18`）按对象逐节 |
| `docs/llms-full.txt` | **构建产物（`.gitignore:15` 排除）** | 构建时生成 | 全量单文件：所有 md + proto + Python SDK text 参考的拼接 |

`build_llms_full.sh` 的聚合逻辑：输出目标 `docs/llms-full.txt`（`:8`）；先跑 SDK 文档脚本拿到 text 版参考（`:17-22`）；文件头声明"optimized for LLM consumption"并预告排版标记已剥离（`:25-34`）；依次内嵌 llms.txt 作 "Documentation Index"（`:37-47`）与 llms-reference.txt 作速查（`:50-58`）；然后 `find docs/` 收集全部 md/rst 但**排除 SDK html 源、docs/README、sdk/python.md 与自身**（`:106-110`），加上 SDK text 目录（`:113-118`）与 `specification/a2a.proto`（`:121-123`）；先写文件索引（`:126-133`）再逐文件以 `<file path="...">...</file>` XML 标签包裹追加（`append_file` `:75-93`，标签 `:81/:87`）。`strip_layout_markup`（`:64-72`）是唯一的净化器——awk 状态机跳过代码围栏（`:66`）、整行 div/span/section 包装（`:68`）与 HTML 注释（`:69`），内容承载的 HTML（图片/表格）保留。

## 外部连接

**CI 触发链（docs.yml，148 行）**：三条触发路径——push/PR 到 main 的 paths 过滤（`:7-27`，**明确包含 `specification/a2a.proto`（`:15/:27`）**，即改 proto 一行也会触发文档重建，这是"proto 即真相源"在 CI 层的落点）、release published（`:28-30`）、workflow_dispatch 手动带 version 输入（`:31-36`）。job 守卫 `if: github.repository == 'a2aproject/A2A'`（`:45`）防止 fork 白跑。环境矩阵横跨四语言生态：Python 3.13（`:62`）+ uv（`:65`）+ Buf 1.71.0（`:73-76`）+ Go 1.25（`:79-81`）；`Install build tools`（`:84-100`）装 protoc 28.3（`:86-89`）、`go install` bufbuild 的 protoc-gen-jsonschema（`:93`）、浅克隆 googleapis 到 third_party（`:99`）。四条部署分支：PR 只 `mkdocs build` 验证（`:108-110`）；push main 部署 `dev latest` 双别名（`:115`）；release 把 tag 名灌进 `MIKE_VERSION`（`:127`，与 `mkdocs.yml:15` 的 `!ENV` 对接）再 `mike deploy $MIKE_VERSION latest`（`:129`）；dispatch 用输入版本（`:142`）。三条部署分支收尾完全同构：`mike set-default --push --template .mkdocs/root-redirect-template.html latest`（`:118/:132/:145`）+ `deploy_root_files.sh`（`:121/:135/:148`）。

**proto→schema 工具链（proto_to_json_schema.sh）**：三级依赖检查——protoc/protoc-gen-jsonschema/jq 在 PATH（`:25-27`）；插件实现防呆（`:29-40`）用版本号正则 `^v[0-9]+\.[0-9]+\.[0-9]+$`（`:33`）确认是 bufbuild/protoschema-plugins 而非 chrusty 同名插件，装错了直接给出 `go install` 修正命令（`:38`）；googleapis 注解路径三级回退——`GOOGLEAPIS_DIR` 环境变量 → 仓内 `third_party/googleapis` → `/usr/local/include`（`:47-54`），并强制校验 `google/api/annotations.proto` 存在（`:56-69`）。转换三步：先 `grep -v` 清洗 proto 里的 `--8<--` 与 `protolint:` 注释到临时副本（`:80`，当前 a2a.proto 实测零命中，属防御性清洗——防的是宏嵌入语法混进 schema）；protoc `--jsonschema_opt=target=json-bundle` 生成（`:88-94`）；jq `-s` 把多个 bundle 的 `$defs` 归并为单体（`:108-118`，标题 "A2A Protocol Schemas"、明示 "Non-normative"）。

**clean_schema_names.py 后处理**：剥三层前缀——`.jsonschema.json` 文件后缀（`:7-8`）、proto 包名 `lf.a2a.v1.`（`:10-11`，对应 `a2a.proto:3` 的 `package lf.a2a.v1;`）、`google.protobuf.`（`:13-14`）；`replace_refs`（`:17-36`）递归改写所有 `#/$defs/` 引用保持一致；子 schema 剥 `$schema` 键以符合 Draft 2020-12（`:59-61`）。产物即 `docs/llms.txt:11/:43` 链接的 `a2a.json`。

**宏的 proto 级联**：proto 任何字段/注释变更 → CI paths 命中 → `build_docs.sh` mtime 检测重生成 json → 规范页 58 张宏表格自动同步——规范表格、JSON Schema、llms-full 内嵌的 proto 文本三者永远同源，不存在手工同步环节。

**根文件集群**：`deploy_root_files.sh:16` 的五文件中三个来自手写（`docs/404.html`——内嵌 JS 把旧路径重写到 `latest/` 前缀（`:27/:31`）；`docs/robots.txt`——头部注释即三件套机器入口清单（`:2-4`），并显式 Allow GPTBot（`:11`）、ClaudeBot（`:17`）、PerplexityBot（`:23`）等生成式 AI 爬虫；`docs/sitemap.xml`——版本无关的 sitemapindex，注释自述"deployed to the domain root by scripts/deploy_root_files.sh"（`:5`）并指回每版本 sitemap）。`:72-82` 的 diff 判定（staged 无变化就不提交）避免 CI 空转 commit。

## 数据流

一次完整的 main 分支文档部署流水（CI docs.yml 实测顺序）：

```
push（改了 a2a.proto 或 docs/** 或 mkdocs.yml 或 .mkdocs/** 或 scripts/）
 └─ docs.yml:7-27 paths 命中 → checkout(fetch-depth 0) + python3.13/uv + buf + go
     ├─ 装工具：protoc 28.3 + bufbuild protoc-gen-jsonschema + googleapis 克隆   (docs.yml:84-100)
     ├─ ./scripts/build_docs.sh                                                 (docs.yml:103)
     │   ├─ mtime 对比 a2a.proto vs specification/json/a2a.json（陈旧才重生）   (build_docs.sh:16-29)
     │   │   └─ proto_to_json_schema.sh → protoc json-bundle → jq 归并 → clean_schema_names.py 剥前缀
     │   ├─ 拷 a2a.json + a2a.proto → docs/spec/（definitions.md --8<-- 嵌入源） (build_docs.sh:46-60)
     │   ├─ build_sdk_docs.sh：新 venv → pip 装 a2a-sdk → sphinx-apidoc → html+text (build_sdk_docs.sh:14-57)
     │   └─ mkdocs build：
     │       ├─ macros 插件加载 .mkdocs/macros → specification.md 58 处 {{ }} 现场解析 proto AST 成表
     │       ├─ snippets 扩展展开 definitions.md:15/:30 的 spec 嵌入（全量 proto/json 进页面）
     │       └─ material 主题 + overrides 模板 + redirects 30 条 → site/
     ├─ bash scripts/build_llms_full.sh                                          (docs.yml:106)
     │   └─ llms.txt + llms-reference.txt + 全部 md（剥排版标记）+ proto + SDK text → docs/llms-full.txt
     │       （注意时序：此产物生成于 mike deploy 之前，故会被 mkdocs 收进版本目录）
     ├─ mike deploy --push --update-aliases dev latest                           (docs.yml:115)
     │   └─ 版本化 gh-pages：latest/ 与 dev/ 双别名，canonical_version=latest（mkdocs.yml:204）
     ├─ mike set-default --template .mkdocs/root-redirect-template.html latest   (docs.yml:118)
     │   └─ 站点根 404/根路径由模板双跳转接管：noscript meta refresh + JS replace 且保留 query/hash (template:43-50)
     └─ deploy_root_files.sh → 克隆 gh-pages → 拷五文件三目录 → diff 才 commit push        (docs.yml:121)
         └─ a2a-protocol.org/llms.txt、/llms-reference.txt、/llms-full.txt、/robots.txt 生效
```

宏渲染是流水里唯一"每次构建都重算"的环节（json 有 mtime 缓存，宏没有也无需要——解析 812 行 proto 是毫秒级），换来的是表格与 proto 的零漂移。

## 设计决策

1. **宏直读 proto vs 预生成快照**——选了前者，且刻意绕开 protoc：`macros.py:10-22` 用纯 Python 的 `proto_schema_parser` 解析 AST、`tabulate` 排表，`requirements-docs.txt:9-10` 随 docs 依赖安装即可，不要求文档贡献者装 Go/protoc 工具链（对比 `proto_to_json_schema.sh:25-27` 的三重二进制依赖——两条链路刻意异构：宏链零二进制依赖保证低门槛，schema 链接受重依赖换取权威 protoc 语义）。代价是 `proto_schema_parser` 与 protoc 对 proto 语法的理解可能有细微差异（推断：这是接受的风险，812 行 proto 无 exotic 语法时无感）。
2. **llms 三件套分层**——llms.txt（约 5KB 索引）/ llms-reference.txt（约 6KB 速查）/ llms-full.txt（全量单文件）对应 LLM 消费的三档预算，且互链成网：`llms.txt:37` 指 reference、`:16/:104` 指 full；`llms-reference.txt:8-9` 反向指回两者；`build_llms_full.sh:37-58` 又把前两者嵌进 full 头部。`copyright`（`mkdocs.yml:71`）与 `robots.txt:2-4` 是这个 LLM 入口体系在"人类页脚"与"爬虫协议"两侧的镜像。`<file path>` XML 包裹（`build_llms_full.sh:81`）与围栏保护（`:66`）说明作者对"LLM 分块解析友好性"有明确意识（设计意图由脚本注释 `:60-63` 自述支撑）。
3. **header.html 拷贝覆盖的风险自管理**——`overrides/partials/header.html` 是对上游 mkdocs-material 同名 partial 的整份拷贝加修改，注释直白承认风险："Based on the upstream mkdocs-material header; **re-check against upstream when bumping mkdocs-material**"（`:4-5`）。这是 MkDocs 覆盖机制（`custom_dir`，`mkdocs.yml:83`）的固有代价：partial 级覆盖不像块级 `{% block %}` 继承（对比 `main.html:3-4` 的 `{{ super() }}` 用法）那样只差异处生效，主题升级时上游 partial 的任何改动都不会自动跟进。`:61-64` 是其插入点：SDK 六语言仓链接行 `sdk_repos.html`（`:7-36` 七个链接，注释 `:4-5` 要求与 docs/sdk/index.md 保持同步）。
4. **失败降级而非硬失败**——schema 转换失败只 `Warning` 继续（`build_docs.sh:36`）、SDK 文档失败继续（`:66`）、宏里类型找不到返回 `**Error:**` 文本（`macros.py:73`）而非异常：文档站宁可缺一块也不整体构建失败，规范仓的发布连续性优先于产物完备性（行为实证；是否全然有意为推断）。
5. **版本化的三重接缝**——`!ENV MIKE_VERSION`（`mkdocs.yml:15`）让版本号贯穿页面；`versioning.provider: mike`（`:127-128`）+ `canonical_version: latest`（`:204`）；根跳转模板双通道（`root-redirect-template.html:43-50`，noscript meta refresh + JS replace，`:48` 特意保留 `window.location.search + hash`——深链带锚点不丢）。dev/latest 双别名（`docs.yml:115`）意味着 main 每次推送都是"预发布即现行版"，release tag 才落永久版本号。

## 新人提示

1. **加一页文档的完整链路**：写 `docs/topics/foo.md` → 在 `mkdocs.yml:23-62` 的对应组插一行 → 跑 `scripts/format.sh` 过 markdownlint（`.github/linters/.markdownlint.json` 规则）→ 需要进 LLM 索引则手改 `llms.txt` 对应分区 + 必要时 `llms-reference.txt`（这两份是手写源，不会自动收录新页）→ push 后 paths 过滤自动触发 CI。涉及协议对象的页面直接写 `{{ proto_to_table("TypeName") }}`，表格零手工。
2. **本地起站**：`uv pip install -r requirements-docs.txt`（10 个依赖，`requirements-docs.txt:1-10`）后 `mkdocs serve`。注意两点：`docs/sdk/python/api/` 是 gitignore 的生成物（`.gitignore:214`），本地不先跑 `scripts/build_sdk_docs.sh` 则 nav `:43` 那项 404；`a2a_version` 会显示 `dev`（`mkdocs.yml:15` 默认值），不是 bug。完整模拟走 `scripts/build_docs.sh`，它会先保证 spec 文件就位。
3. **宏报错排查**：页面上出现 `**Error:** Message \`X\` not found.`（`macros.py:73`）= `_find_type` 没找到，九成是名字打错或该类型嵌套在别的 message 里；`**Error:** Proto not found`（`:68`）= 路径问题，`_parse_proto` 以仓根为基准解析相对路径（`:53`）。宏改名/删类型不影响 mkdocs build 退出码（错误被吞成文本），**务必肉眼查渲染结果**，CI 不会替你抓这类坏表。改宏本身用 `mkdocs build --strict` 可抓未定义宏。
4. **坑：构建产物不入库是体系性约定**——`.gitignore` 五处相关排除：`specification/json/a2a.json`（`:9`，"Ephemeral schema artifacts (never commit)"注释钉版）、`docs/spec/`（`:12`）、`docs/llms-full.txt`（`:15`）、`docs/sdk/python/api/`（`:214`）、`.doc-venv`（`:6`）。看到工作区冒出这些目录别去 commit；反过来，clone 后立刻找 `a2a.json` 会扑空——它只活在构建后与线上（`docs/llms.txt:11` 的链接是 `a2a-protocol.org/latest/spec/a2a.json` 而非 GitHub 路径，原因即此）。
5. **坑：nav 计数口径**——对外引用统一说"29 个本地源 md 页（nav 32 叶条目含 2 外链 1 生成 html）"；"26 页"口径（含任务书）查无实据。同理 `docs/blog/posts/` 是 3 篇而非 4 篇（03 篇勘误复用）。
6. **坑：Windows 无本土路径**——`scripts/` 九个文件全是 `.sh`（ls 实证），`specification/json/README.md:179` 提到的 `build_docs.ps1` 不存在（03 篇勘误）；Windows 贡献者走 WSL/Git Bash。`build_docs.sh:21-26` 的 Darwin/Linux 双 stat 已是平台兼容的极限。
7. **提速技巧**：想看"proto 改动会变成什么"，不必跑全链——宏表用 `python3 -c "from proto_schema_parser.parser import Parser; ..."` 直接试解析；schema 链单跑 `GOOGLEAPIS_DIR=<googleapis路径> scripts/proto_to_json_schema.sh /tmp/a2a.json`（jq 的定义计数 `:125-126` 会告诉你规模）。读规范 HTML 页时记住：凡是 GitHub 管道表格，源码里都不存在，别在 docs/ 里 grep 表格内容——去 `specification.md` 搜 `{{ proto_to_table` 调用点，再回 proto 找定义。

---

本篇锚点清点：mkdocs.yml 22 处、macros.py 21 处、build_docs.sh 9 处、build_llms_full.sh 9 处、proto_to_json_schema.sh 8 处、clean_schema_names.py 5 处、build_sdk_docs.sh 4 处、deploy_root_files.sh 3 处、docs.yml 14 处、llms.txt 5 处、llms-reference.txt 3 处、gitignore 6 处、robots/sitemap/404/template/header/main.html 13 处、a2a.proto 4 处，合计约 126 处行号锚。

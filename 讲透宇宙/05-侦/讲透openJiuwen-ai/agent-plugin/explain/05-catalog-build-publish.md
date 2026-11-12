# 05 · catalog / build / publish：从目录清单到 Hub 发布线

## 一、角色定位

这三个脚本构成插件的**分发流水线**：`catalog.py`（205 行）把 plugins/ 扫描成机器可读的目录清单，`build.py`（251 行）把单个插件打成可上传的 zip，`publish.py`（280 行）编排"校验→打包→上传"三步把包送上 swarmskills Hub。三者与 validate.py 一样是零 import 依赖的兄弟脚本——publish 只经 subprocess 调前两者（`scripts/publish.py:235,239`），协作靠进程边界而非模块边界。

catalog.py 的核心定位写在 docstring（`scripts/catalog.py:4-7`）：catalog/catalog.json 是**生成物（lockfile 式，发布时提交）**——README 插件目录表格、产品内置同步清单、Hub 发布对账三方共用，**禁止手改**。与 Cargo.lock 同一设计：文件进 git，但真值来源是 plugins/ 的 manifest 集合，手工编辑会被下次生成覆盖，`--check` 把"漂移"变成 CI 可拦的 exit 1（L178-190）。

## 二、内部结构

**catalog.py 三段式**。采集段 `collect_entries()`（L58-109）：遍历 plugins/ 跳点开头目录（L61），对每个包读 manifest 并做四重防错——缺文件/坏 JSON 抛 ValueError（L63-68）、`manifest.id` 必须等于目录名（L70-74）、id 全仓唯一（L75-77）、version 必须匹配 `X.Y.Z` 正则（L30, L79-83）、package_type 必须 plugin（L84-87）。产出条目（L91-108）是 manifest 的**投影**：只保留 id/version/双语展示字段/category/tags + `capabilities` 三计数（skills 取目录名 L40-47、tools/rails 取 class 名 L50-55）+ `path`。渲染段 `render_catalog()`（L112-114）固定 `ensure_ascii=False, indent=2`——**输出字节级确定性**是 lockfile 语义的前提。README 同步段 `sync_readme()`（L145-158）：在 `<!-- catalog:begin/end -->` 锚点（L32-33，实锚在 README.md L17/L22）之间正则替换表格，无锚点或无改动都静默跳过（L147-148, L155-156）。表格本身 `render_readme_table()`（L117-142）以"N skill + N tool + N rail"聚合能力组成（L125-131），简介取 display_description.zh（L139）。

**build.py 两段式**。收集段 `collect_publish_files()`（L128-169）执行安全排除：黑名单目录 EXCLUDED_DIRS（L35-45，含 `.git/__pycache__/node_modules`，**tests/ 也在内**——L43 注释钉死不变量"plugins/ = 分发物 1:1"）；密钥类文件 EXCLUDED_FILES（L46-53，id_rsa/credentials.json/token*.json）与后缀 `.key/.p12/.pfx/.pyc`（L54）；`.env*` 全排但白名单 `.env.example/.env.template`（L55, L150）；**拒绝一切 symlink**（L130-131, L145-146, L155-156）并用 `lstat` 掩码 `0o170000 == 0o100000` 确保普通文件（L157-159，挡 fifo/socket/设备文件）；上限 MAX_FILES=10000 / 512MB / 深度 32（L57-59, L162-168）。白名单 env 模板还要过 `_validate_environment_template()`（L88-125）：敏感键正则（token/key/password/secret/credential/authorization，L81-83）只允许空值或 `${VAR}` 占位（L120-125），URL 不得内嵌用户名口令、query 敏感参数同样只认占位（L102-119），超长行用 `readline(65537)` 边读边断（L92-96）。打包段 `build_zip()`（L172-211）：产物名 `{id}-{version}.zip`（L184）；**固定时间戳** `ZIP_TIMESTAMP = (2020,1,1,0,0,0)`（L62）配合手工 ZipInfo（L190-193）实现**可复现构建**——同输入必得同 zip 字节；L191 注释专门提醒"手工构造的 ZipInfo 不继承 ZipFile 的压缩方式，必须显式指定"；`external_attr` 统一 0644（L193）；边写边算 sha256（L186, L195）；zip 超 50MB 即删产物抛错（L198-203）。

**publish.py 两段式**。协议段 `upload()`（L121-203）：**手工构造 multipart/form-data**（L149-165，boundary 用 `secrets.token_hex(24)`），字段 asset_name/plugin_version/display_name/description/tags/version_desc/visibility/force + file=asset.zip（L138-147），请求头 Bearer token + X-Checksum-SHA256（L171-175）；urllib 直连 300s 超时（L178），响应体限 2MB（L38, L179-181）。校验段 `_validate_hub_result()`（L58-106）对 Hub 响应做七连查：code==200（L70-74）、data 存在（L75-77）、资产类型在 `{"agent-plugin","plugin"}`（L43, L79-81）、asset_id/plugin_id 存在且不冲突（L82-87）、**回传 name/version 必须与请求一致**（L88-92）、visibility 合法或处于"受理未确认"态（L45-47, L96-103）、publish_result 非 publish_failed（L104-105）。主流程 `main()`（L206-276）三步编排：token 校验（L222-225）→ `[1/3]` subprocess 跑 validate.py（L234-235）→ `[2/3]` build.py（L237-239）→ `[3/3]` upload（L253-265），受理态 `pending_moderation` 单独提示（L269-270）。

## 三、外部连接

- **catalog 消费方三头**：README 目录表格（锚点机制）、`sync_builtin.py`（同步到主仓 built_in 目录，`scripts/sync_builtin.py:4-7`——建议仅 example-plugin 与旗舰插件走内置，其余走 Hub 在线分发）、Hub 发布对账。docstring L6 把这三头明示为 catalog 存在的理由。
- **build/publish 与主仓的镜像契约**：build.py 的排除规则"对齐主仓 server/runtime/marketplace/asset_package_builder.py 的 collect_publish_files"（L6-9），publish.py 的上传协议"对齐主仓 hub_publish_client.py"（L6-9）——与 validate/init 的同源关系一样，**本仓 scripts/ 是主仓发布逻辑的镜像实现**，主仓改协议两头同步。
- **publish → validate/build**：subprocess 硬依赖（L235, L239），`--skip-validate` 可跳过第一步但 help 明言"不推荐"（L219）。
- **环境变量契约**：`JIUWENSWARM_HUB_TOKEN` 必填、`JIUWENSWARM_HUB_BASE_URL` 可选（L11-13, L214-218），凭据"不落任何文件"（L11）。
- **pr_check/CI**：catalog --check 与 build 的组合进 PR 门禁（见 06 篇）；产物 dist/ 不进 git（build.py L16）。

## 四、数据流

一个插件的完整发布旅程（`publish.py example-plugin`）：

1. **前置**：读 `JIUWENSWARM_HUB_TOKEN`，缺失或含非可打印字符即退出（L222-225）。
2. **校验**：`[1/3]` 子进程跑 `validate.py example-plugin`（L235）——注意是**默认模式**而非 `--require-hot-load`，本地无 SDK 时 L2 会 PARTIAL 通过，"热加载尽力执行"（L234 原话）。
3. **打包**：`[2/3]` build.py 收集文件（排除+安全检查）→ 固定时间戳写 zip → 输出 sha256（L239 回到此流程上游）。publish 侧随后读 manifest 拼出 `dist/{id}-{version}.zip` 并确认存在（L241-251）——**两个脚本靠"文件名约定"交接**，publish 不接收 build 的返回值。
4. **上传**：`[3/3]` 一次性读入 zip 字节算 sha256（L134-136，注释承认"流式风格改为一次性读入（仓库脚本包体 ≤50MB）"）→ 拼 multipart → POST `/api/v1/plugins`（L167-176）。
5. **响应裁决**：Hub 回 JSON → `_validate_hub_result` 七连查（见上）→ 全过则打印"Hub 已确认资产 {asset_id}"；`pending_moderation` 提示等待审核（L269-270），否则提示回滚方式见 docs/hub-publish.md（L272）。
6. **目录线并行**：贡献者日常只需 `catalog.py`（生成）→ commit catalog.json + README 表格；PR 门禁跑 `catalog.py --check` 对账——已提交文件与重新生成结果逐字节比较（L182-183），不一致即"漂移"exit 1，修复指引就是重跑生成（L186）。

## 五、设计决策与权衡

1. **lockfile 式 catalog 的取舍**：生成物提交进 git 换来三方对账能力（README 表格永远和 plugins/ 一致、Hub 对账有快照、diff 直接可见插件增删）。代价是每个 PR 多一个"记得重新生成"的动作——`--check` CI 门禁把它变成强制。与手写目录页相比，杜绝 README 表格过期这一 wiki 类顽疾。
2. **手工 multipart 而非 requests**：全仓零第三方依赖基调下的必然选择。代价是 L149-165 手工拼 boundary 的代码——换来对协议字节的完全控制（sha256 对 payload 而非文件流，与手工拼装自洽）。
3. **可复现构建（固定 ZIP_TIMESTAMP）**：同一份源码任何人任何时间打包得到相同字节——sha256 因此有"跨人可比对"意义，供应链审计友好。
4. **排除规则宁可误杀**：`tests/` 整目录不进包（L43）——"分发物 1:1"不变量优先于包内自测试。密钥文件名黑名单 + 敏感键值白名单占位的组合拳，把"泄露凭据"这一发布事故的最大来源在打包期拦截。
5. **Hub 响应七连查的偏执**：连"回传 name/version 与请求不一致"都拦（L88-92）。上传场景拿到错误资产 id 的后果（覆盖别的插件、版本错乱）远重于多几行校验——"网络边界上的数据一律不可信"的教科书执行。
6. **visibility 受理态的宽松窗口**（L45-47, L96-103）：`pending_moderation` 等状态下 Hub 可能暂不下发 visibility，校验器显式放行"未确认"态——协议精确对齐主仓 parse_publish_result（L44 注释）。
7. **sync_builtin 默认拒绝覆盖**（`sync_builtin.py:68-72`）：已存在必须 `--force`，收尾提醒"请在主仓走正常代码评审流程提交，不要直接 push"（L76-79）——脚本权力自觉收窄到"复制"，不越权碰 git。

## 六、新人提示与坑

1. **catalog.json 手改必被覆盖**：`--check` 会把手改态判为漂移。正确路径：改 manifest → 跑 `catalog.py` → 一起提交。
2. **README 表格的锚点不能删**：`<!-- catalog:begin/end -->`（README.md L17/L22）外随便手写，锚点内属于机器——删掉锚点后 `sync_readme` 静默跳过（L147-148），表格从此停更且无报错。
3. **version 必须严格 X.Y.Z**：`1.0`、`v1.0.0`、`1.0.0-beta` 都过不了 CATALOG_RE（L30）。
4. **build 的 excluded 是提示不是错误**：输出 `excluded: tests/ …`（L207-210）属正常；致命的是 BuildError（UNSAFE_PATH/LIMIT_EXCEEDED/CREDENTIAL_VALUE）。
5. **.env.example 占位符语法**：敏感值只认 `${VAR}` 单一形态（L84），`$VAR`、`{{VAR}}` 都判 CREDENTIAL_VALUE；URL query 里的 token 参数同理（L111-119）。
6. **publish 本地跑会 PARTIAL 过**：`[1/3]` 用默认 validate（L235），无 SDK 时 L2 跳过仍继续上传——别把"本地 publish 成功"当热加载验证。
7. **--force 是覆盖不是更新**：同版本强制覆盖 Hub 资产（L212），正常迭代应递增 version（validate L616-618"更新由发布流程递增"）。
8. **zip 超限产物会被删除**（L200）：dist 里找不到 zip 不一定是没打过，可能打了又被删。
9. **图谱视角**：catalog.json 的 capabilities 计数（L101-105）是 manifest 派生视图——这正是批沉淀"catalog 锚点由 catalog.py 生成"的含义：README/catalog.json 表格是生成物，别当独立信息源。

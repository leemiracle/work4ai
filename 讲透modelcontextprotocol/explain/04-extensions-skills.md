# 04 · Skills 扩展与 extensions/ 关系网（L06 扩展层入口）

> 锚约定（均相对 `docs/extensions/`）：`skills:`=`skills/overview.mdx`；`apps:`=`apps/overview.mdx`；`build:`=`apps/build.mdx`；`tasks:`=`tasks/overview.mdx`；`matrix:`=`client-matrix.mdx`；`ext:`=`extensions/overview.mdx`。

## 一、角色定位

`docs/extensions/skills/overview.mdx` 是 Skills over MCP 扩展入口页（document 节点，图谱 L06「扩展体系与官方 Registry」层）。它定义的不是新 wire 格式，而是约定：用核心协议已有的 Resources 原语承载 Agent Skills 的发现与读取（skills:25-31）。扩展与核心协议的边界——扩展是规范的可选附加（ext:8），不进 schema 契约，按 SEP 立法：SEP-2133 五步 Propose→Implement→Review→Publish→Adopt（ext:97-101），标识符 `{vendor-prefix}/{extension-name}`（ext:10）。SEP-2640 状态 Final（skills:9），但页面明说 SDK/host 支持仍在实现（skills:12-13）——规范先行、实现追赶。

## 二、内部结构

443 行章节地图：

- **Skill 是什么**（L25-37）：目录=`SKILL.md`+可选支撑文件，格式整体委托外部 Agent Skills 规范（skills:29-31），本扩展只定 MCP 传输绑定；适用=组合多工具、带参考文件的复用工作流（skills:33-37）。
- **交互模型**（L39-48）：`resources/read` 读 `SKILL.md` 不激活 skill——必须走宿主 skill-loading 路径：校验+用户批准后才进上下文（skills:45-48）。
- **Capabilities**（L50-75）：服务端 MUST 同时声明 `resources` 能力与 `io.modelcontextprotocol/skills` 扩展（skills:52-54）；MUST 实现 `skills/list`+`skills/get`，文件本体走 `resources/read`（skills:69-70）；`directoryRead` 默认 false（skills:72-73）。
- **三方法**（L85-292）：`skills/list` 条目含 `uri`/`frontmatter`/`resources`（`"dynamic"`=生成式内容，skills:139-143）；manifest 铁律=MUST 列全 `SKILL.md`+每支撑文件，各带 URI+SHA-256+字节大小（skills:145-147）；`skills/get` 按 URI 取条目可刷新（skills:178-180），未知 URI 返 `-32602`（skills:428）；`SKILL.md` MUST 以含 `name`/`description` 的 frontmatter 开头且父目录末段=name（skills:226-228），相对引用按 skill 根解析（skills:230-233）；可选 `resources/directory/read`（skills:247-249），宿主 MUST NOT 把实时目录结果当 manifest 扩展（skills:288-292）。
- **消息流** mermaid 时序（L300-347）；**完整性校验**（L358-387，见四）；**限制** 512 文件/16 MiB 每 skill（skills:404-406）；**错误表**（L424-433）。

## 三、外部连接

六页成网（图谱 L06 document 节点）：

- **ext=枢纽**：下链 Apps/Tasks/Skills 三扩展（ext:38-75），并给协商机制——客户端每请求 `_meta.clientCapabilities` 声明（ext:137）、服务端在 `server/discover`（ext:169）、单边支持须优雅降级（ext:200-202）。
- **skills 页图谱边**（实测）：入边 6 条 related（←ext、←matrix、←seps/2640、←3 个 working group 页）；出边 6 条——related→matrix+SEP-2640，depends_on→四个 draft 规范页 `server/discover`/`server/resources`/`utilities/pagination`/`utilities/caching`（skills:54,88-89,189）——「扩展踩在核心原语上」的图证。
- **matrix**=14 客户端×4 扩展（matrix:35-50）：Apps 列 10 家全绿；Skills 列仅 mcpc 全绿+ChatGPT/fast-agent/MCP Inspector 三家 Partial（matrix:44,48-50）；opt-in 双边声明（matrix:16）。
- apps+build=SEP-1865 亦 Final；tasks=SEP-2663 Final；auth/ 三页同层但走 ext-auth 线，弱耦合。

## 四、数据流：一个 Skill 的完整生命周期

1. **作者打包**：`SKILL.md`+支撑文件；服务端从实际字节算完整 manifest（skills:397-398）。
2. **发现**：`skills/list` 得条目+manifest，带 `ttlMs`/`cacheScope`（不提供内容完整性，skills:151-152）。
3. **选择与保留**：模型按 name/description 选或用户显式选（skills:314-318）；身份=来源服务器+URI，name 只是标签不保证唯一（skills:154-158）；宿主保留条目至少到 `SKILL.md` 离开模型上下文（skills:360-362）。
4. **批准绑 manifest**：绑全部文件 URI+摘要集，无需预取文件（skills:242-243）；任一文件增删改即撤销批准（skills:371-373）。
5. **校验注入**：读 `SKILL.md`→校验字节数+SHA-256+逐字段比对 frontmatter（skills:364-367）→通过才注入并标注来源服务器（skills:334-337）；失败即拒用、`skills/get` 刷新（skills:354-356）。
6. **激活期按需读**：宿主在保留 manifest 内解析 URI→同服务器读→复验摘要→给内容（skills:339-346）。缓存须不可变或每次复验、排除出文件系统 skill 发现路径、重启后保留 MCP origin（skills:375-379）。

沙箱模型本质=**skill 内容是不可信输入**（skills:416）：manifest 圈定可读集；摘要只保证与 manifest 一致而非内容可信（skills:382-383）；`allowed-tools` 等宿主侧执行需逐 skill 批准、嵌套 skill 激活需新同意（skills:417-419）；跨服务器读取须点名双方逐调用批准（skills:413-416）。

## 五、设计决策

- **复用 Resources 而非新原语**：SEP-2640 摘要明言 skill 格式与渐进披露模型整体委托 Agent Skills 规范，本 SEP 只定传输绑定——不发明第二套文件语义，不支持扩展的客户端至少能当普通 resource 读。
- **独立于 tools（声明式 vs 命令式）**：tool=模型可调用的命令；skill=给模型的工作流说明书，按需渐进加载省上下文。skill 指挥模型组合调用若干 tools，二者正交。
- **强制 SHA-256=供应链防线**：skill 内容会驱动宿主执行动作，摘要把「服务器事后换内容」变成可检测事件——校验+批准绑摘要集+缓存隔离三件套。
- **与 Apps 互补**：Apps 管人机交互——返回内联渲染的 HTML（apps:14-15），`_meta.ui.resourceUri` 指 `ui://` 资源可预载（apps:60-63），跑宿主沙箱 iframe+CSP（apps:70-75）经 postMessage 通信（apps:146-149），`ui/` 方言、传输是 postMessage 而非 stdio/HTTP（apps:155-159）；Skills 管模型知识注入，信任=摘要+批准而非 iframe。
- **Tasks=时间维扩展**：长操作返回持久句柄而非阻塞（tasks:17-22），五状态 `working`/`input_required`/`completed`/`failed`/`cancelled`（tasks:126-132），轮询默认、`notifications/tasks` 可替代（tasks:139-145），服务器逐请求决定是否成 task（tasks:40-42）。它改「结果形状」（`resultType:"task"` 多态，tasks:181），Apps/Skills 加「能力面」。

## 六、新人提示

1. **选型口诀**：给人看的 UI→Apps；给模型的流程知识→Skills；超几秒的操作→Tasks。可叠加（skill 教模型用 app，app 的 tool 调用成 task）。Apps 构建有 `create-mcp-app` skill 让 agent 直接脚手架（build:28-29）。
2. **读 matrix**：opt-in 双边声明是前提，社区维护可能滞后；Skills 列 3 Partial+1 全绿——规范 Final≠生态就绪。
3. **演进面**：四 SEP（2133/2640/1865/2663）文本均 Final，但 Skills 的 SDK/host 在追；experimental-ext- 前缀仓是孵化通道（ext:77-91）；破坏性变更须换 `-v2` 新标识符（ext:118-122）。
4. **三条硬红线**：不预取文件（skills:242）；不用校验失败的内容（skills:369）；同 name skill 不得静默互替（skills:412）。

> 非空白字符 4321 / 锚 61（展开 250 行锚，六文件全源码核实）

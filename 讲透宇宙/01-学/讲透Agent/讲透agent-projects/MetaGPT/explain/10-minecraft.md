# 10 Minecraft Agent：Voyager JS 运行时的 vendored 移植

## 1. 角色定位

Minecraft 子系统是 NVIDIA Voyager（LLM agent 玩 Minecraft）的运行时移植：`metagpt/environment/minecraft/` 下 Python 侧只做编排，真正的 agent 执行体是一个 vendored 进来的 Node.js Express 服务器（`mineflayer/index.js`），LLM 生成的 JS 代码在其中 eval 执行并驱动 mineflayer bot。注意两层"名不副实"：`mineflayer/package.json:2` 写 `"name": "voyager"`——这个目录不是 mineflayer 库本身而是 Voyager 运行时；`mineflayer/mineflayer-collectblock/` 是 TheDudeFromCI 版 collectblock 插件为 Voyager 定制的 fork（其 README 自述 "This is a modified version to better support Voyager"），经 `file:mineflayer-collectblock`（package.json:19）本地协议挂载，均非 MetaGPT 原生代码。Python 消费端：`minecraft_env.py:22` 的 `MinecraftEnv(MinecraftExtEnv, Environment)` 是唯一角色入口——但全仓 grep 无任何 Role 类消费它，Voyager 式角色（含 skill 库）不在此版本仓库内，环境层是自洽孤岛。

## 2. 内部结构

Python 侧两层：`minecraft_ext_env.py:26` 的 `MinecraftExtEnv(ExtEnv)` 负责进程管理与 HTTP 协议——`run` 方法循环拉起 mineflayer 进程（重启超 3 次 `raise {}`，L114-118）后 POST `{server}/start`（L121-124）；`step` 方法先 `check_process/unpause` 再 POST `/step`（L172），成功后 `pause` 冻结游戏。`minecraft_env.py` 的 MinecraftEnv 再叠 Environment 抽象：`register_roles`（L143）、`update_event/update_task/update_context/update_code`（L147-164）把事件、任务、已验证代码写回 `voyager_chroma` 技能库（Chroma 向量库做 skill 记忆）。JS 侧 `index.js` 是四端点服务器：`/start`（L25，在 `bot.once("spawn")` 回调里才 `res.json` 首帧观测，L52——bot 连上但从未 spawn 则请求永久悬挂无超时）、`/step`（L152，核心是 L256 `await eval("(async () => {" + programs + "\n" + code + "})()")`）、`/stop`（L401）、`/pause`（L408）。观测体系在 `lib/observation/`（base/onChat/voxels/inventory/chests 等八类）；`lib/skillLoader.js` 名不副实——不做技能加载，是控制原语的 monkey-patch 注入器：`bot._chat = bot.chat` 后重写 `bot.chat`（L61-65）先 `bot.emit("chatEvent", "bot", message)` 再真发，这是 onChat 观测能捕获 bot 自身发言的关键链路。

## 3. 外部连接

进程层：`process_monitor.py` 守护 mineflayer 进程。技能层：`utils/common.py:833` 的 `load_mc_skills_code` 从 `metagpt/utils/` 目录读 Voyager 技能 js 文件拼进 programs 前缀——但仓内该目录现无 js 技能文件，属外部注入接口。collectblock 插件：`src/index.ts` barrel 导出 plugin，内部 new CollectBlock 并延迟加载 pathfinder/tool；MetaGPT 侧经 `file:` 协议依赖消费其编译产物。上游血统：index.js:7 的 `getNextTime` 从 `./lib/utils` 解构导入却全文件零调用（死导入）。

## 4. 数据流

一步循环：Python `step(code, programs)` → HTTP `/step` → JS 侧 unpause → eval 拼装 `(async () => { programs + code })()`——programs 是已验证技能代码前缀、code 是 LLM 新代码，两者拼成一个匿名函数整体执行 → 执行期间各观测器采集（base.js inject 的事件过滤：名字以 on 开头且非当前事件的观测被跳过）→ 错误经 `handleError`（L338）用正则 `/<anonymous>:(\d+):\d+\)/` 从栈帧行提取行号、减去 `programs.split("\n").length` 偏移反解出 LLM 代码的相对行号，并拼回 "at <你的代码行> in your code" → res.json 返回观测 → Python pause 冻结。代码验证通过则 `update_code` 入 Chroma 成为技能，下轮作为 programs 前缀复用——这就是 Voyager 的技能自增长环。

## 5. 设计决策

其一，eval 执行 LLM 代码是最激进也最诚实的选择：Minecraft 没有结构化 action space，代码即动作，配合栈帧反解把运行时错误翻译回 LLM 视角的行号。其二，观察/冻结节奏（step 后立即 pause）让异步游戏世界变成同步回合制，方便 LLM 决策。其三，技能库用向量检索召回旧代码作 few-shot。vendored fork 里三处上游遗留 bug 值得钉版：`Inventory.ts:32` 与 L39 的 callbackify 调用漏传 `itemFilter`（cb 路径下 undefined，placeItems 的 `!itemFilter(item)` 恒真跳过所有物品）、L66 `callbackify(gotoChest)(bot, location)` 漏传 cb 回调被吞——主代码走 Promise 路径不受影响，但任何人用旧式回调 API 就踩雷；`getClosestChest`（L11-28）选中即 `splice` 移除有副作用，语义是"试过就不再试"而非纯查询。`CollectBlock.ts:31` 用 `closest.constructor.name` 字符串 switch（'Block'/'Entity'）而非 instanceof，default 抛 UnknownType（L159-160）；L34 `success_count >= options.count` 的 break 只跳出 switch，主 while 对剩余目标逐个 removeTarget 空转，且 count 门控只管 Block 分支、Entity 拾取不受限，L69 NoItem 分支是 return 直接退出跳过 L166 的收尾播报。`TaskQueue.ts:8` 全仓零消费者，是上游库死代码。

## 6. 新人提示

跑通需要三方件：Minecraft 服务器（带 mineflayer 兼容协议）、Node 侧 `mineflayer/index.js`、Python 侧 MinecraftEnv——且此版本仓内没有现成 Voyager 角色，得自写 Role 调 `env.step`。读代码先看 index.js 的 `/step` 与 handleError，这是 LLM-代码-游戏三方契约的全部；调"观测缺字段"看 lib/observation/base.js 的事件过滤逻辑，它比你直觉的少采很多东西。改 collectblock 行为优先考虑在 Python 侧规避而不是修 fork——上游 callbackify 三处参数丢弃是已知坑。评估这套设计的可迁移性：eval+栈帧行号反解模式可复制到任何"LLM 写代码操作真实环境"的场景（浏览器、终端），是本子系统最有复用价值的资产；而 /start 无超时悬挂是生产化前必修项。

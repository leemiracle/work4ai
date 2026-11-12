# 11. help 子包与三 shell 补全：数据字典、渲染器与"帮助优先于报错"

> 锚点基准：`proot_distro/commands/help/` + `proot_distro/completions/`，行号现场核实。姊妹篇：01、06。

## 一、角色定位

本篇覆盖 CLI 的两块"知识层"：**help 子包**（`proot_distro/commands/help/`，L07/L08 命令层出口）与**三份 shell 补全**（L13 包数据层）。二者都不执行容器操作，却各自维护一份"命令面知识"的完整副本——help 面向人眼，补全面向 Tab 键。

规模上有个反直觉事实：`pages.py` 1080 行是 `commands/` 目录最大单文件，却**零行逻辑**——纯数据字典。加上 `render.py`（336 行纯格式化）与 `__init__.py`（167 行胶水），"文档即代码"分成数据、渲染、组装三件。补全三脚本 bash/zsh/fish 各 343/341/562 行，同一知识表的方言翻译。

## 二、内部结构

### 2.1 pages.py：数据字典

`HELP_PAGES`（pages.py:43）共 **17 个命令页**（import 实测），每页 schema：`usage`/`aliases`/`summary`/`options`（`(名字,说明)` 列表）/`examples`/`footer`（任意多个 `{title,intro,bullets,examples}` 块，由 render.py:290-336 按键消费）。

三个数据层技巧：

1. **平台门控内嵌进数据**：Termux 独有选项用 `*([(...)] if IS_TERMUX else [])` 解包进 options（头注释 pages.py:21-24 点明目的："帮助与 argparse 实际接受的东西保持同步"）。如 `--isolated` 仅 Termux 主机可见（pages.py:623-626）；login 页的 HOST BINDINGS 整个 footer 块（14 条 Android 路径，pages.py:685-707）在别处整块消失。
2. **写一次用两处**：`_IDENTITY_NOTE`（pages.py:33-40）解释 guest 内 PD_CONTAINER/PD_IMAGE 语义，login 与 run 共同引用（pages.py:741,1004），避免双份漂移。
3. **动态插值防改名**：示例全用 f-string 引 `PROGRAM_NAME`（如 pages.py:454）。

`TOP_COMMANDS`（pages.py:1061-1080）是总览页 18 行清单（17 页+help 自身），**按用户旅程排序而非字母序**——help 打头，install→login→run 主线居中，build/push 殿后。remove/reset/restore 三行携带红色警告 `"Destroys data!"`（pages.py:1070,1072,1074）。

### 2.2 render.py：纯格式化渲染器

对数据内容零假设，只做排版（render.py:21-25）：

- **宽度探测链**：`term_width()` 依次试 fd 2→1→0 的 `os.get_terminal_size`，再退 `COLUMNS` 与 `shutil.get_terminal_size`，钳制 `[32,92]` 列（render.py:39-40,50-72）。**先探 stderr**（render.py:55）因为帮助全写 stderr——stdout 被重定向时宽度应跟用户实际看着的终端。
- **双布局**：低于 `NARROW_BREAKPOINT=60` 列（render.py:43，手机竖屏 PTY 典型值）选项名与说明堆叠竖排（render.py:133-139）；宽屏两栏对齐（render.py:142-172），描述列不足 24 字符仍回落堆叠（render.py:151-153）。
- **commands_block 警告着色**：红字警告挤得进描述首行就内联（render.py:212-214），否则续行独立输出（render.py:219-220）；**shell_block** 示例带 `$` 提示符，折行行尾补 `\` 续行符（render.py:223-237）。

### 2.3 __init__.py：推导与总览页

`HELP_COMMANDS` 是全篇最精妙一行——字典推导遍历 `HELP_PAGES`，为每页造零参闭包（`_make_help_fn`，help/`__init__.py`:41-44,49）：`HELP_COMMANDS = {name: _make_help_fn(name) for name in HELP_PAGES}`。**新增命令页即自动注册渲染器**，无需第二张调度表。`command_help`（help/`__init__.py`:52-164）手写总览页七节，COMMANDS 节直接消费 `TOP_COMMANDS`（help/`__init__.py`:75）；它接受但忽略 `args`，只为与其它 `command_X` 签名对齐（help/`__init__.py`:55-58），才能进 `_COMMAND_HANDLERS`（cli.py:82）。

### 2.4 三份补全的平行解剖

三脚本同构四件套：容器枚举、镜像枚举、Termux 判定、分命令 case。方言差异：

- **双入口**：bash 一函数注册两次（proot-distro.bash:342-343）；zsh `#compdef proot-distro pd`（_proot-distro:1）；fish **全文复制 pd 块**（proot-distro.fish:411-562）——562 行的主因。
- **容器/镜像枚举**：容器名靠目录扫描+`rootfs` 子目录校验（proot-distro.bash:9-22 等），半成品容器不进补全；镜像引用三处同注释"cache 按哈希键存储，须经程序自身读回"（proot-distro.bash:24-29、_proot-distro:35-41、proot-distro.fish:38-42）。
- **能力漂移**：bash 的 `container:path` 补全最全（proot-distro.bash:224-234），zsh 仅 `_files`（_proot-distro:250-251），fish 仅容器名（proot-distro.fish:287-288）；`--` 后内层命令补全 bash/zsh 有（proot-distro.bash:135-140），fish 无。

## 三、外部连接

help 子包上游仅 constants 与 message 两件；`msg()` 是唯一输出口，**写 stderr**（message.py:207）——帮助不污染 `search -q | xargs` 类 stdout 管道。

cli.py 是 HELP_COMMANDS 的**四个消费点**：①无参或 `-h`/`help` 及其缩写触发总览（cli.py:267-271）；②`_dispatch_help` 在 argparse 前截击 `<cmd> -h|--help|--usage`（cli.py:197-210）；③未知选项与缺必需参数两条错误路径追加渲染对应页（cli.py:310-318,320-326）；④`args.help` 置位按 canonical 名查表（cli.py:296-301）。别名统一走 `ALIAS_TO_CANONICAL`（parser.py:103-113），`pd bkp -h` 与 `pd backup -h` 渲染同一页。parser.py 自身也做 IS_TERMUX 门控（parser.py:127-130,143-152），与 pages.py 门控互为镜像——"帮助里写的=argparse 接受的"由此保证。

补全连接方向相反：不 import Python，而是**镜像** constants.py 两样东西——容器目录布局（Termux 走 `$TERMUX__PREFIX/var/lib/proot-distro/containers`，否则 XDG 数据目录，proot-distro.bash:11-15，对应 constants.py:75-86）与 Termux 判定（见 5.6）。打包由 pyproject.toml 收口：补全为包数据并映射三 shell 目录（pyproject.toml:29-35）。

## 四、数据流

**A：`pd login --help`**。过嵌套 proot 检查（cli.py:260）→`_dispatch_help` 命中（cli.py:204-208）→闭包调 `render_page`（render.py:290）：宽度→USAGE+aliases→DESCRIPTION→OPTIONS（非 Termux 主机六个 Termux 选项不进列表）→EXAMPLES→HOST BINDINGS（Termux 才有）→NOTES→footer，全经 `msg()` 落 stderr，exit 0（cli.py:275）。

**B：`pd login`（缺容器名）**。`required_args_for` 发现缺参→`crit_error`（cli.py:322-323）→**紧接渲染该命令完整帮助页**（cli.py:324-325）→exit 1。看错时永远同时看到"怎么做对"。

**C：Tab 补全 `pd remove <TAB>`**。查命令行含 `-i/--image` 与否（proot-distro.bash:106）：有则执行 `list --image --quiet` 拿镜像引用，无则扫容器目录只认含 `rootfs/` 的名字（proot-distro.bash:19）。

## 五、设计决策

**1. 数据与渲染分离**。数据零逻辑、渲染零内容，双向自由：改文案不碰排版，改版式不动 17 页文案；HELP_PAGES 是普通 dict，测试与文档生成器可直接遍历。

**2. HELP_COMMANDS 推导而非维护**（help/`__init__.py`:49）。让"注册渲染器"从"记得改表"变成"数据存在的自然结果"——以数据为唯一事实源消灭平行账本。

**3. 帮助优先于报错**。本 CLI 最鲜明的 UX 立场，四路径全覆盖：无参给总览 exit 0；`_dispatch_help` 刻意**抢在 argparse 前**截击 `-h`，docstring 点破原因——"argparse 先跑，缺必需位置参数会报错而非给帮助"（cli.py:200-202；不截击则 `pd login -h` 先撞缺参错误）；未知命令 crit_error 后**追加**总览再退（cli.py:224-225）；未知选项/缺参数追加**该命令专属页**（cli.py:315-316,324-325）。错误告诉用户错了，帮助紧跟着告诉什么是对的。

**4. 输出走 stderr**。帮助是人读的，不是管道数据；`search -q`/`list -q` 机器输出独占 stdout（cli.py:330-337 注释），通道分离互不干扰；宽度探测因此以 stderr 为先（render.py:52-54）。

**5. 三份平行实现与同步维护成本**。命令面知识全仓有**七个副本**：parser.py 的 argparse 定义（权威源）、pages.py 17 页、TOP_COMMANDS、cli.py `_COMMAND_HANDLERS`（cli.py:64），加三份补全各自的子命令清单与帮助主题表（proot-distro.bash:57-58,335、_proot-distro:71-90,329-332、proot-distro.fish:73-74,407）——fish 再×2。给 login 加一个选项要动 parser.py+pages.py×2（login/run 两页 options 近乎逐行重复，pages.py:610-683,906-979）+三份补全。而 **CI 零防护**：36 件 unit 测试无一引用 HELP_PAGES/TOP_COMMANDS/HELP_COMMANDS/completions（grep 实证），同步全靠 pages.py 头注释约定——"补全滞后于新选项"的结构性温床，2.4 的能力漂移已是现实。

**6. `_is_termux` 两票制探测**。Python 侧 `_detect_termux`（constants.py:55-65）取三票——①platform 串含 android 或存在 `/system/build.prop` 或 `/data/app`；②`TERMUX_VERSION` 系环境变量任一存在；③TERMUX_PREFIX 可读可执行——`sum(checks) >= 2` 才认定（constants.py:65）。单票皆不可靠：桌面误设 TERMUX_VERSION、或 Android 原生 shell 无 Termux 环境都只出一票，两票齐到偶然性极小。三份补全运行时镜像同一逻辑（proot-distro.bash:44-51、_proot-distro:47-54、proot-distro.fish:48-66，bash 注释明言 mirroring `_detect_termux()`）——**必须运行时判定**，补全跑在 shell 进程 import 不了 Python。镜像已有语义漂移：Python 第一票含 `platform.platform()` 检查（constants.py:58），shell 只能查文件系统——第 5 条成本的又一实证。两票通过后连锁：RUNTIME_DIR 布局（constants.py:75-86）、DEFAULT_PATH_ENV（constants.py:108-113）、argparse 选项集（parser.py:127,143）、帮助文案与补全选项集（pages.py:21-24、proot-distro.bash:154-155）。

## 六、新人提示

1. **改帮助先读 pages.py:21-24 头注释**；login/run 两页 options 近乎逐行重复（pages.py:610-683,906-979），改其一必须同步其二。
2. **加新命令 checklist**：parser.py 子解析器+别名 → pages.py 加页 → TOP_COMMANDS 加行 → cli.py 处理器表 → 三份补全（fish 含 pd 块两处）→ 帮助主题表三处。漏掉补全不会有测试报警。
3. **验证渲染别用眼**：`COLUMNS=40` 与 `COLUMNS=120` 各跑一遍 `login --help`，检验 60 列断点两侧的堆叠/双栏切换；`2>/dev/null` 下全页消失即佐证 stderr 通道。bash 下 source 补全后可直接单测 `_proot_distro_get_containers`。
4. **两票制是安全相关判定**：误判改变状态目录落点（constants.py:75-86）；补全镜像与 Python 判定分叉会出现"补全给的容器名、程序却找不到"的灵异现象——改探测逻辑必须四实现一起动。

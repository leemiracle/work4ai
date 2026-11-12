# 01 · CLI 入口与命令分派：cli.py / parser.py / __init__.py

> 层位：L08「CLI 入口与帮助层」（图谱 14 层中的倒数第七层）。覆盖三个文件：
> `proot_distro/cli.py`（345 行）、`proot_distro/parser.py`（417 行）、
> `proot_distro/__init__.py`（25 行，纯 docstring 包根）。
> 所有行号锚均于 2026-10-27 在仓内现场核实，标注【实测】的行为均在本机以桩 proot 复跑验证。

## 一、角色定位：三层文件的分工

proot-distro 的命令行入口被刻意拆成"薄入口 / 厚解析 / 空包根"三件套：

- **`__init__.py` 是全仓 fan-in 之冠**。它只有一段 docstring（`__init__.py:21-25`），声明"公开入口是 `proot_distro.cli.main`"。图谱里它以 72 条入边位居全仓第一——仓内 60+ 个模块每一句 `from proot_distro.X import ...` 都会向包根 `__init__.py` 汇入一条 imports 边。它不定义任何符号，却是所有模块的公共祖先；这份"空"正是包根该有的样子：不承载逻辑，避免循环导入。
- **`cli.py` 是唯一的进程入口**。模块头注释（`cli.py:21-30`）自述架构："重活都在别处——parser.py 负责 argparse 构造，commands/help/ 负责帮助页，commands/* 每个子命令一个模块；main() 只做信号路由、运行环境检查（拒绝嵌套 proot、探测 proot）、跑解析器、校验必填位置参数、然后分派"。它是典型的**编排者**而非执行者：345 行里没有一行碰容器文件系统。
- **`parser.py` 是纯数据+构造层**。三张表（`ALIAS_TO_CANONICAL` 别名表、`REQUIRED_ARGS` 必填参数表、`required_args_for` 联动函数）加 17 个子命令构造函数，全部是声明式的 argparse 组装，唯一的控制流是一个 argparse 子类的 `error()` 重载（`parser.py:39-60`）。

入口链本身有两副面孔：现代安装走 `pyproject.toml` 的 console scripts——`proot-distro = "proot_distro.cli:main"` 与 `pd = "proot_distro.cli:main"` 两条别名都指到同一个函数（`pyproject.toml:22-24`）；仓根还保留一个源码直跑包装 `proot-distro.py:21-23`（`from proot_distro.cli import main` + `if __name__ == "__main__"`），供不开安装的开发场景。

## 二、内部结构：main() 的九段流水线

`cli.py` 的核心是 `_COMMAND_HANDLERS` 表（`cli.py:64-83`）：18 个键（17 个实命令 + help）到 `command_*` 函数的映射。这张表就是命令目录本身——`main()` 末尾 `handler(args)` 一行（`cli.py:345`）完成了全部"路由"。表驱动使得新增命令的成本 = 写一个模块 + 加两行（表里一行、import 一行）。

`main()`（`cli.py:246-345`）按顺序做九件事，每件都短小且有独立函数承载：

1. **SIGQUIT 改道**（`cli.py:252-258`）：`signal.signal(SIGQUIT, _sigquit_to_keyboard_interrupt)` 把 Ctrl-\ 变成 `KeyboardInterrupt` 异常（处理器在 `cli.py:86-87`）。注释写明动机：SIGQUIT 默认行为是"终止+core dump"，会跳过全仓各处 `except KeyboardInterrupt` 里已有的进度条清理、半成品文件删除和 "Aborted by user" 报文。
2. **拒绝嵌套 proot**（`cli.py:260` → `_refuse_nested_proot`，`cli.py:90-119`）：读 `/proc/<pid>/status` 的 `TracerPid:`，非零则再读 tracer 进程的 `Name:`，含 "proot" 即 `crit_error` + exit 1。报错文案很硬气："With 100% confidence this is not a mistake. Do not send bug reports!"（`cli.py:97-98`）——嵌套 proot 是已知不支持项，不是 bug。
3. **启动期 proot 探测**（`cli.py:262-265`）：先用 `ALIAS_TO_CANONICAL` 规范化第一个 token（`cli.py:263-264`），再交给 `_ensure_proot_available`（`cli.py:178-194`）。**五个命令豁免**：`build/push/kill/ps/search`（`cli.py:192`）。豁免理由写在 docstring 里：`build` 可能跑一个没有 RUN 指令的 Dockerfile（纯 Python 模式不需要 proot，它自己在解析 Dockerfile 后按需检查，见 `commands/build.py:171` 的延迟导入）；`push` 只读本地缓存上传 registry；`kill/ps` 只查会话注册表发信号；`search` 只查 Docker Hub——"因为运行时还没装就拒绝查镜像名是本末倒置"（`cli.py:188-190`）。探测本体 `ensure_proot_installed`（`cli.py:122-175`）：`PD_PROOT_BIN` 环境变量优先（交给 `get_proot_bin` 校验，坏值 crit_error+exit）；否则 `shutil.which("proot")`；缺失时非 Termux 直接退出，Termux 且有 TTY 才交互式提议 `pkg install -y -q proot`（`cli.py:170`），非 TTY 给出安装提示后退出。
4. **无参/裸帮助短路**（`cli.py:267-271`）：`argv[1]` 缺失或属于 `("-h","--help","help","hel","he","h")` 就渲染总览页并 exit 0。
5. **帮助预拦截**（`cli.py:274-275` → `_dispatch_help`，`cli.py:197-210`）：识别 `<command> -h/--help/--usage` 组合，**在 argparse 运行之前**渲染该命令的帮助页。`--usage` 是个有趣的角色——argparse 里根本没定义它，但预拦截层认它。注释点破目的：让"缺必填位置参数 + -h"永远出帮助而非报错。
6. **未知命令预检**（`cli.py:281` → `_reject_unknown_command`，`cli.py:213-227`）：在 argparse 之前手工验证第一个 token。`cli.py:277-280` 的注释解释了绕行的原因：未知子命令会让 `_SubParsersAction` 抛 `ArgumentError`，argparse 会先打印自己的 usage 再走 error 处理——预检保证错误输出完全由自家文案掌控。
7. **解析与未知参数复核**（`cli.py:283-318`）：`build_parser()` + `parse_known_args()`（不用 `parse_args`——后者遇到未知 token 会直接走 argparse 的 error，而这里要把"未知参数"变成带该命令帮助页的自家报错）。随后两道关卡：`args.command is None`（`cli.py:286-292`）与未知 token 复核（`cli.py:310-318`），后者把首个坏 token 分类报错：`-` 开头叫 "unrecognized option"，否则叫 "unexpected argument"（`cli.py:312`）。对 `login/run` 还会把 `--` 之前的部分重新解析一遍来得到干净的未知列表（详见第四节）。
8. **必填位置参数校验**（`cli.py:320-326`）：遍历 `required_args_for(canonical, args)` 返回的 `(arg_name, error_msg)` 对，缺谁报谁的专属文案。这些参数在 argparse 里全部是 `nargs="?"` 可选项（如 `parser.py:199`），"必填"语义完全由这张表在 main 里补判——这是"缺参数时打印帮助而非 argparse usage"的代价与手法。
9. **分隔符切分、quiet 全局化、分派**（`cli.py:328-345`）：`_split_separator` 处理 `--` 尾部命令（第四节详述）；`set_quiet(True)` 在分派**之前**调用（`cli.py:337-338`），让 helpers（docker、download 等）的 info 行与进度条也一并静音——但 `list` 和 `ps` 豁免，因为它们的 `--quiet` 语义不同（只打印名字/PID，不走 log_info）；`search` 两种语义都要所以保留（`cli.py:330-336` 注释）。最后查表分派。

`parser.py` 一侧的组织：`build_parser()`（`parser.py:161-191`）顶层 `add_help=False`（`parser.py:166`），`-h` 改为 `store_true` 旗标（`parser.py:168`）——这正是第 5 步能统一拦截的前提。子解析器以 `dest="command"` 注册（`parser.py:169`），`help` 也注册为一个带别名的子命令（`parser.py:171`），再依次调用 17 个 `_xxx(sub)` 构造函数（`parser.py:173-189`）。每个构造函数都把规范命令名盖章到 `p._pd_command`（如 `parser.py:198`），供 `error()` 重载渲染正确帮助页。`_PdArgumentParser.error()`（`parser.py:49-60`）把 argparse 的报错改写为：`crit_error(message)` + 该命令帮助页 + exit 1；`HELP_COMMANDS` 在此处**延迟导入**（`parser.py:50-53`），理由是帮助页只在错误路径上才需要，平时构建解析器不必为它买单。

## 三、外部连接：与 help 子包及 17 个命令模块的协作

- **commands/***：`cli.py:44-61` 一次性导入 18 个 `command_*` 入口。每个命令模块按约定只暴露一个 `command_<name>(args)` 函数（`commands/__init__.py:23-25` 注释自述"由 proot_distro.cli 接线进分派器"）。这 24 条 imports 边是图谱 L07→L08 层间的主干。
- **help 子包**：`HELP_COMMANDS` 是"命令名→零参渲染函数"的字典，由推导式批量生成：`{name: _make_help_fn(name) for name in HELP_PAGES}`（`commands/help/__init__.py:49`）。实测它有 **17 个键**（backup/build/clear-cache/copy/install/kill/list/login/ps/push/remove/rename/reset/restore/run/search/sync）——**不含 help 自己**。帮助数据本体在 `pages.py` 的 `HELP_PAGES`（`pages.py:43` 起，纯数据）与总览页命令表 `TOP_COMMANDS`（`pages.py:1061` 起，18 项含 help）。`command_help(args=None)` 的 `args` 形参纯为与其他 handler 签名对齐、故意忽略（`commands/help/__init__.py:52-57` docstring 明说）——这是"help 也是命令"统一表的代价。
- **基础层**：`constants.py` 提供 `IS_TERMUX`（import 时一次性探测，`constants.py:68`）与 `PROGRAM_NAME="proot-distro"`（`constants.py:32`）；`message.py` 提供着色字典 `C`（`message.py:113`）、`msg`（写 stderr，`message.py:187`）、进程级 quiet 开关 `set_quiet/is_quiet`（`message.py:171,182`）、`crit_error`（`message.py:227`，**只打印不退出**——退出永远由调用方 `sys.exit(1)`）。
- **arch.py**：`get_proot_bin()`（`arch.py:221`）被启动探测复用做 `PD_PROOT_BIN` 校验。
- **测试**：`tests/unit/test_parser.py` 覆盖三张表与各子命令旗标解析；`tests/integration/test_cli_dispatch.py`（105 行，11 个用例）直接打 `cli.main()` 验证分派行为：无参出帮助、未知命令、别名解析+必填校验、单命令帮助、quiet 全局化、search 免探测分发、未知选项拒绝、login 分隔符内命令（`test_cli_dispatch.py:24-98` 的 `def test_*` 清单）。

## 四、数据流：argv → args 的变形记（含实测）

从 `sys.argv` 到 `handler(args)`，数据经历五次变形：

1. **裸 argv 预判**：`sys.argv[1]` 直接对照帮助 token 集合与 `ALIAS_TO_CANONICAL`（18 个别名，`parser.py:103-113`，实测计数），别名如 `add/i/in/ins→install`、`sh→login`、`rm→remove`、`s/se→search`。注意别名**双注册**：既在 ALIAS_TO_CANONICAL，又在 argparse `add_parser(aliases=...)`（如 `parser.py:195-197`）——argparse 需要认识它们才能选对子解析器，而 `args.command` 拿到的可能是别名串，所以 main 里还要再规范化一次（`cli.py:294`）。
2. **argparse 解析**：产出 `args` 命名空间；位置参数全部可选（`nargs="?"` + `default=None`），"哪个位置参数必填、缺了报什么文案"完全由 `REQUIRED_ARGS`（`parser.py:66-84`，10 个命令）承载。
3. **条件联动**：`required_args_for`（`parser.py:87-98`）处理"位置参数含义随旗标漂移"：`remove --image` 时 `target` 的缺失文案从"容器名未指定"换成"镜像引用未指定 (e.g. 'ubuntu:24.04')"（`parser.py:95-97`）。【实测】`pd remove --image`（缺 target）报 `Error: image reference is not specified (e.g. 'ubuntu:24.04').`，exit 1——与 `pd install` 缺参的文案同款而与 `pd remove` 缺参不同。
4. **`--` 分隔符切分**：这是数据流上最微妙的一步。`login` 在 argparse 里注册了 `login_cmd = nargs="*"` 尾槽（`parser.py:268`），argparse 原生就能收尾部 token；而 **`run` 压根没注册 run_args 位置参数**（`parser.py:395-401` 里只有 `container_name` 和两个旗标）。【实测】`parse_known_args(['run','c','--','nginx','-g','daemon off;'])` 返回 `unknown=['nginx','-g','daemon off;']` 且 `args.run_args` 属性不存在——内部命令全部漏进未知列表。为此 `main()` 在复核未知参数前，只把 `--` 之前的切片重新喂给解析器（`cli.py:307-309`），得到不含内部命令的干净未知表；随后 `_split_separator`（`cli.py:230-243`）直接从原始 argv 按 `raw_args.index("--")` 手工切出 `args.run_args`（login 同样处理以保证两命令行为一致）。下游 `commands/run.py:115` 用 `getattr(args, "run_args", []) or []` 防御性读取（正因为该属性可能不存在），`commands/login/__init__.py:361` 对 `login_cmd` 同款防御，并以 `shlex.join(login_cmd)` 拼进 `-c`（`login/__init__.py:377,403`）。
5. **quiet 全局化**：`args.quiet` 旗标转成进程级 `set_quiet(True)`（`cli.py:337-338`），此后 helpers 里所有 `log_info` 与进度条静音（`message.py:210-213` 的 log_info 判 `_quiet`）。

## 五、设计决策：五处值得学的取舍

1. **"帮助优先于报错"贯穿到底**。argparse 的默认哲学是"参数错误就退出"，本项目反过来：所有必填校验从 argparse 挪到自家表（`REQUIRED_ARGS`），argparse 层全部 `add_help=False` + `nargs="?"`，再配 `error()` 重载与三处预拦截（裸帮助、`<cmd> -h/--help/--usage`、`--help` 旗标路径 `cli.py:296-301`）。代价是同一份"必填"知识要显式维护成表；收益是每类错误都能附上对应命令的完整帮助页而非两行 usage。
2. **退出码约定：0/1 二值**。所有失败路径一律 `sys.exit(1)`（帮助路径 `sys.exit(0)`，`cli.py:271,275,301`），`crit_error` 只负责红字打印（`message.py:227-229`），"打印"与"退出"职责分离。【实测】未知命令、缺必填、互斥组冲突、未知选项四类错误全部 exit=1，文案都以 `Error:` 开头。
3. **`parse_known_args` 而非 `parse_args`**：把 argparse 的失败降级成数据（unknown 列表），main 才有机会按"选项 vs 参数"分类报错（`cli.py:310-314`）并附帮助页。互斥组冲突这类 argparse 自身要 error 的场景，则由 `_PdArgumentParser.error()` 接管——【实测】`pd backup x -v -q` 报 `Error: argument -q/--quiet: not allowed with argument -v/--verbose` 后跟 backup 帮助页。
4. **`run` 不注册 varargs 位置参数**是精确的取舍：若注册了 `run_args=nargs="*"`，argparse 会把 `-g daemon off;` 里以 `-` 开头的 token 误当未知选项、且与尾部旗标搅在一起；不注册+手工切分让 `--` 之后的 token 原封不动（连 `--not-a-flag` 都进内命令）。代价是必须做两段式复核（全量解析给 unknown、切片重解析给 check_unknown），`cli.py:303-309` 注释直呼"re-parse only the portion before '--' to get a clean unknown list"。另一个隐含契约【实测】：`pd login c bash`（无 `--`）时 argparse 会把 `bash` 收进 `login_cmd`，但 `_split_separator` 随即因无 `--` 把它**重置为 []**（`cli.py:236-237`）——内部命令必须跟在字面量 `--` 后，裸尾 token 会被静默丢弃并落回默认 shell。
5. **平台差异内联进解析器**：`_add_login_or_run_common`（`parser.py:116-158`）里 `--isolated/--minimal`、`--no-link2symlink/--no-sysvipc/--no-kill-on-exit` 只在 `IS_TERMUX` 时注册（`parser.py:127-130,143-152`）——非 Termux 平台上这些选项是"未知选项"而非"无效选项"，报错路径自然统一。`--fix-low-ports` 只挂 login 不挂 run（`parser.py:123-126`，【实测】login 有 run 无）；`-l/--limit` 故意留成字符串让命令层自己校验，好报"太小/太大/非数字"而非 argparse 干瘪的 "invalid int value"（`parser.py:221-223` 注释）；backup 的 zstd 压缩项同理留在 choices 里让 command_backup 解释解释器为何写不了它（`parser.py:286-290` 注释）。

## 六、新人提示

- **改命令先动两处表**：新子命令要同时出现在 `build_parser` 的构造函数与 `_COMMAND_HANDLERS`；改名/加别名要同时改 `ALIAS_TO_CANONICAL`（`parser.py:103`）和 `add_parser(aliases=...)`，漏一处就是"argparse 认识但分派器不认识"（或反之）的死路。
- **必填校验有第三张表**：给命令加必填位置参数时，别只写 `add_argument`——必须同时进 `REQUIRED_ARGS`（`parser.py:66`），否则缺参静默通过直到 handler 内炸出 IndexError 类的远端错误。
- **`_pd_command` 盖章是隐式契约**：每个子解析器构造函数里 `p._pd_command = "..."` 一行（如 `parser.py:198,219`）决定 error() 渲染哪页帮助；忘写则错误时回退到无帮助页的裸报错。
- **别在 cli.py 里加业务逻辑**：它的自我定位是环境检查+解析+分派（`cli.py:21-30`）；登录构造在 `commands/login/`，同步算法在 `commands/sync.py`（47K 全仓最大命令模块），此处只该有路由。
- **调试分派问题从三条线排查**：`pd badcmd` 走 `_reject_unknown_command`（argparse 之前）；`pd login x --bogus` 走 main 的 unknown 复核（argparse 之后）；`pd backup x -v -q` 走 `_PdArgumentParser.error()`。三条路径的入口分别钉在 `cli.py:213`、`cli.py:310`、`parser.py:49`——【实测】三类错误的报错样式（有无帮助页、文案前缀）各不相同，可据此反查代码路径。
- **无 proot 环境下 CLI 活不过第三步**：非 Termux 主机缺 proot 时，`pd list` 也会在启动探测处 exit 1（`cli.py:140-145`）——【实测】本机报 `Error: proot utility does not exist on your system.`。想让纯解析类测试跑通，要么 mock 探测，要么用豁免命令（search/ps/kill/build/push），`tests/integration/test_cli_dispatch.py:63` 的 `test_search_dispatches_without_proot` 就是这么设计的。

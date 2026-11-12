> 标题：命令行接口——jev-mem 入口的模式分派与配置哈希缓存 · 源文件：jev_mem/cli.py（80 行）· 图谱标签：entry-point / cli / argument-parsing（图谱度数 in=3 / out=4）

## 角色定位

`jev-mem` console script 的本体（注册于 pyproject.toml:28），Jev-Mem 对外的第一张脸。docstring 第二句就交代了权力格局（jev_mem/cli.py:2）："The existing MAGMA path remains the default."——默认模式 test 直接把用户转交给 LoCoMo benchmark；真正的 Jev-Mem 构建/查询走 build/query 两模式，自己装配 JevMemSystem。

它同时是根入口 main.py 的实现体：main.py 是个 sys.modules 垫片，整个模块被替换成 jev_mem.cli（main.py:8），所以 `python main.py --help` 与 `jev-mem --help` 是同一个 argparse——第 31 篇讲的入口卫生测试正是踩在这条等价性上。80 行里没有一行业务逻辑：解析参数、翻译 flag、定位缓存目录、委托 system，是典型的薄壳编排层。

## 内部结构

单 main 函数，五段：

- **argparse（jev_mem/cli.py:19-32）**：三模式 build/query/test，默认 test（jev_mem/cli.py:21）；`--input` 一个参数两副面孔——build 模式吃 observation JSON、test 模式吃 LoCoMo JSON（help 文本原话，jev_mem/cli.py:22）；`--question` 查询文本；`--model` 默认 gpt-4o-mini（jev_mem/cli.py:24）；`--embedding-model` 二选一 minilm/openai（jev_mem/cli.py:25）；`--cache-dir` 默认 ./cache（jev_mem/cli.py:26）；四个 jev 开关（jev_mem/cli.py:27-31）与 `--jev-config` 配置文件路径。
- **前置校验与环境（jev_mem/cli.py:33-38）**：build/test 缺 `--input`、query 缺 `--question` 即 parser.error；`load_dotenv()` 把 .env 灌进环境（jev_mem/cli.py:37）——API key 的标准来路；logging 统一 INFO 级。
- **test 模式子进程分派（jev_mem/cli.py:39-48）**：拼 `[sys.executable, -m, jev_mem.benchmarks.locomo, ...]` 命令，dataset/model/embedding/cache-dir 四参数透传（jev_mem/cli.py:40-42）；四个 jev 布尔开关按需追加，下划线转连字符（jev_mem/cli.py:43-45）；jev_config 单独 extend（jev_mem/cli.py:46-47）；`return subprocess.call(command)` 退出码原样上浮（jev_mem/cli.py:48）。
- **config 与缓存命名空间（jev_mem/cli.py:49-63）**：jev_mem 开关翻译成 overrides——开写+读、jev_mock、单关写、单关读（jev_mem/cli.py:50-57）；`JevMemConfig.load(args.jev_config, **overrides)` 合并文件与命令行（jev_mem/cli.py:58）。关键一步：只要 write/read 任一启用，cache_dir 就追加 `jev_mem_` + config 序列化 sha256 的前十二字符（jev_mem/cli.py:60-62）——**配置指纹目录**，不同配置的图互不污染；audit_path 未设则默认落在该目录的 decisions.jsonl（jev_mem/cli.py:63）。随后 JevMemSystem 装配（jev_mem/cli.py:64）。
- **build/query 双路径（jev_mem/cli.py:65-76）**：build 若缓存目录已有 graph.json 先 load_memory 再续写（jev_mem/cli.py:66-67，增量构建）；读 input JSON、打印 build_memory_from_conversation 结果、save_memory 收尾（jev_mem/cli.py:68-70）。query 反向要求 graph.json 必须已存在否则 parser.error（jev_mem/cli.py:72-73），load 后打印 query 结果（jev_mem/cli.py:74-75）；两路径统一 return 0（jev_mem/cli.py:76）。

## 外部连接

import（jev_mem/cli.py:13-16）：dotenv 的 load_dotenv（.env 加载）；`.system.JevMemSystem`（第 01 篇编排门面，其 build/query/save/load 四方法即本文件委托面：jev_mem/system.py:25、54、63、68）；`memory.jev_mem_config.JevMemConfig`（第 02 篇控制面配置）。被引三方：pyproject.toml:28 的 console script 注册；main.py:1-8 垫片整体转发（`python main.py` 与本 CLI 同体）；tests/test_project_layout.py:55-68 的分派测试——monkeypatch 掉 load_dotenv 与 subprocess.call 后跑 `cli.main()`，断言退出码透传、命令前缀是 `python -m jev_mem.benchmarks.locomo`、dataset/jev-config 参数与 --no-jev-read 都进了命令行（tests/test_project_layout.py:63-68）。README.md:318 提示 `pip install -e .` 后即可用 jev-mem 系列命令。图谱 in=3/out=4 与实测一致（垫片、注册、测试三向入边）。

## 数据流

test 模式是**进程边界流**：本进程 argparse→命令行字符串翻译→子进程 benchmarks.locomo 完整接管（构建、检索、评分、落盘都在那边，见第 12 篇）；本进程只剩等待与退出码转发。build/query 模式是**进程内流**：.env→JevMemConfig 合成→配置指纹定位缓存目录→JevMemSystem 初始化（write/read 开启时 audit 流向该目录 decisions.jsonl）→build 增量写图或 query 读图检索→stdout 打印 JSON/答案。两条流共享 argparse 但互不相交：overrides 与配置指纹只作用于 build/query（test 模式在第 48 行就 return 了，配置决策完全交给子进程）。

## 设计决策

**子进程转发而不是函数调用**是本文件最重要的一笔。test 模式若直接 `from jev_mem.benchmarks.locomo import main` 调用，需要把本层 argparse 翻译成对方 argparse 的命名空间，两套参数定义耦合死；子进程化让边界退化为命令行字符串，benchmark 侧参数演进零波及。代价：flag 名下划线/连字符的手工翻译（jev_mem/cli.py:45）、双份解释器启动、子进程 stdout 不经本层格式化。tests/test_project_layout.py:55-68 正是为这层翻译护栏。

**配置指纹目录**（jev_mem/cli.py:60-62）与第 30 篇适配器的 manifest 内容寻址是同一思想在两处落地：图缓存的身份必须绑定构建它的配置。差异在粒度——适配器按题按 haystack 指纹建目录，CLI 按全局 config 哈希建目录；共同底线是绝不让不同配置共享一张图。注意指纹只在 write/read 任一启用时计算——全关的纯 MAGMA 用法走裸 ./cache，向后兼容旧布局。

**毛边三条**：其一，`--input` 双语义（jev_mem/cli.py:22）靠 help 文本维持，argparse 层无校验——build 模式喂 LoCoMo JSON 会在 build_memory_from_conversation 深处才炸，错误信息离用户操作很远；其二，build/query 两路径**零测试覆盖**——分派测试只罩 test 模式（tests/test_project_layout.py:58-68），增量续写（jev_mem/cli.py:66-67）与 query 的 graph.json 卫语句（jev_mem/cli.py:72-73）全靠人肉回归；其三，`--model` 默认 gpt-4o-mini 是硬编码供应商默认值（jev_mem/cli.py:24），与仓里"模型名透传、key 自备"的中立姿态略有不谐——不传就默认走 OpenAI 计费路线，新手最容易无意识踩上。

## 新人提示

先读 jev_mem/cli.py:39-48 的分派段再看 build/query 段——默认路径（test）反而是最间接的路径。上手顺序：`jev-mem --mode build --input examples/observations.json --jev-mem` 建图，`jev-mem --mode query --question "..." --jev-mem` 查询；跑基准直接 `jev-mem --mode test --input data/locomo10.json`。

四个坑：一，改了 JevMemConfig 任何字段，配置指纹就变（jev_mem/cli.py:61），旧图在新目录里"消失"——不是丢数据，是换门牌；要复用旧图得手动指回旧 `jev_mem_<hash>` 目录；二，build 前若缓存已有图会**静默增量续写**（jev_mem/cli.py:66-67），想要干净重建先删目录；三，jev 四开关只在 build/query 模式经 overrides 生效，test 模式只是字符串转发（jev_mem/cli.py:43-47），两侧行为可能有版本差；四，audit 日志默认跟着配置指纹目录走（jev_mem/cli.py:63），跨多次实验找 decisions.jsonl 时记得先算（或打印）当次配置的哈希目录名。

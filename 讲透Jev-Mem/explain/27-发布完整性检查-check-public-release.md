> 标题：公开发布完整性守门员——credential 扫描四模式精讲 · 源文件：scripts/check_public_release.py（207 行）· 图谱标签：工程基建层 / 安全闸门

## 角色定位

Jev-Mem 开源发布链的安全闸门：在代码出门前扫描 credential 模式与私有产物，**只报位置不打印值**。文件头（check_public_release.py:1-9）三条自我声明定调：仅标准库（零依赖，任何裸环境可跑）；四种扫描模式覆盖工作树/Git 暂存区/全文件树/Git 对象库四层；"This is a pattern guardrail, not a semantic privacy audit"（check_public_release.py:8）——正则护栏不是语义审计，作者对能力边界有清醒认知。

它守护的资产清单是 `public-release-files.txt`（check_public_release.py:18 引用，96 行显式 allowlist），配合 `scripts/export_public_repo.py`（导出器）与 CI 门禁组成完整发布流水线：改动→`--tracked` 扫描→导出 allowlist 树→`--all-files` 验产物→`--git-objects` 扫历史。这在一个从私有研究仓长出来的项目里是刚需——历史 blob 里躺着 API key 是最常见的泄漏姿势。

## 内部结构

- 规则表（check_public_release.py:19-35）：九条 credential 正则——TypeSafe apikey_ 双段（21）、OpenAI sk- 前缀族（22）、GitHub gh[pousr]_/github_pat_（23）、Hugging Face hf_（24）、Slack xox 族（25）、AWS AKIA/ASIA 访问键（26）、PEM 私钥头（27）、通用赋值式 `API_KEY=...` 值长二十四以上（28-30）、个人绝对路径 `/Users/xxx/`（31）；另有 AZURE 端点正则（33）与十三个私有后缀集合 `.pkl/.npy/.jsonl/.pem/.safetensors` 等（34-35）
- `Finding`（check_public_release.py:38-46）：frozen dataclass，`__str__` 只拼 `path:line:reason`（44-46）——整条管线没有任何路径会把匹配到的 secret 值本身打印出来
- `private_path`（check_public_release.py:49-67）：路径级黑名单六层过滤——绝对路径/上跳/反斜杠（53）；.env 家族但放行 .env.example（55）；私有后缀（57）；具名产物 graph.json/keyword_index.json/jev_mem_config.json 及 credentials*/service-account 前缀（59-60）；目录黑名单 .git/.venv/__pycache__ 加子串 "cache" 与 results/locomo_trg/longmem_ 前缀（62-63）；data/ 目录只放行 README（65-66）；再点名两个示例数据文件（67）
- `scan_content`（check_public_release.py:70-84）：单文件四查——路径黑名单（72-73）、五 MB 尺寸上限（19 定义、74-75 检查）、九正则逐 match 报行号（76-78，行号用 `content[:match.start()].count(b"\n") + 1` 计算）、Azure 端点对占位符白名单 your-resource/your-resource-name/example 放行其余报 finding（79-83）
- `public_paths`（check_public_release.py:87-107）：manifest 解析器——跳注释空行（91）、黑名单命中或重复即抛 ValueError（93-94）、逐段查 symlink（96-101，防符号链接绕过）、缺文件即抛（102-103）、空清单即抛（105-106）
- 四个扫描器：`scan_worktree`（110-115）只扫 manifest 列出的文件；`scan_index`（118-139）走 `git ls-files --stage -z`（125）扫**全部暂存条目**，mode 非 100644/100755 或 stage 非零报 "symlink, submodule, or unresolved"（132-133），内容用 `git cat-file blob` 取（135）——不依赖工作树，staged 未 commit 的版本也被覆盖；`scan_all_files`（142-159）rglob 全树，allowlist=manifest+SHA256SUMS（144），清单外文件（156-157）与 symlink（150-151）都是 finding；`scan_git_objects`（162-177）用 `--batch-all-objects` 遍历**所有本地 blob 含不可达对象**（169），逐 blob 内容扫描（173-176）
- `main`（check_public_release.py:180-203）：互斥模式组（183-186）、三元选择器（189-190）、异常处理只打印异常类型名不打印内容（192-195，注释明言 "Never dump subprocess output or file contents"）、findings 逐条打印后返回码一（196-200）、通过时打印文件计数（201-202）

## 外部连接

纯标准库（argparse/dataclasses/pathlib/re/subprocess，check_public_release.py:10-14），零仓内 import。fanOut 实测七处：CI 门禁 `.github/workflows/ci.yml:30`（`--tracked`）；`SECURITY.md:30` 与 `CONTRIBUTING.md:17`、`CONTRIBUTING.md:37` 的流程文档；`docs/releasing.md:11-12` 与 `docs/releasing.md:23` 的发布手册（含对导出产物再跑 `--all-files` 的复验步骤）；`scripts/export_public_repo.py:10-12` 直接 import ROOT/scan_content/scan_worktree 复用扫描逻辑做导出前校验与导出后复验；`tests/test_public_release.py:11` import 六个函数做单测；`public-release-files.txt:79` 把脚本自身列入发布清单（守门员自己也出门，用户可本地复跑同款检查）。

## 数据流

日常开发流：改文件→`python scripts/check_public_release.py`（默认模式）→scan_worktree 读 manifest→逐文件 read_bytes→scan_content 四查→零 finding 退出码零，有 finding 打印 `路径:行号:原因` 退出码一。

发布流（docs/releasing.md 记载）：stage 后跑 `--tracked`（CI 同款，扫描范围从 manifest 扩到整个暂存区——**这是关键差**：CI 门禁保证凡是进了 Git 索引的东西都干净，比 manifest 模式强一个量级）→export_public_repo 按 manifest 拷贝出干净树+SHA256SUMS（拷贝时逐文件二次 scan_content 防 TOCTOU，源变动即抛 "Source changed during export"）→对产物目录跑 `--all-files` 复验→发布前再跑 `--git-objects` 确认对象库里连不可达历史 blob 也无泄漏。四模式形成从"我打算发布什么"到"仓库里实际存在什么"的漏斗，越往后范围越大。

## 设计决策

**永不打印被扫值**是贯穿性设计：Finding 只有位置（44-46）、异常只报类型（194）、git 子进程 stderr 吞进 PIPE（120）——扫描器自身绝不成为泄漏源，这个属性对安全工具是自我一致性的要求。**manifest 显式 allowlist**（87-107）而非 ignorelist 是发布完整性的根本翻转：新文件默认不可发布，漏列即拒，与 scan_all_files 的 "file outside public allowlist"（157）互为表里——闭集语义让"意外多打包一个文件"这类事故在结构上不可能。

批判性发现三处：①通用赋值正则（28-30）值门槛定在二十四字符以上，短于它的真 secret（如某些 token）漏报，而长的非 secret（base64 图片串、hash）会误报——护栏方向的取舍是宁误报不漏报，但意味着 finding 非零不等于真泄漏，人工复核不可省；②private_path 的目录黑名单用子串匹配 "cache"（63），任何路径段含 cache 的目录全灭——保守方向正确，但用户若建 `benchmark_cache_notes/` 这类目录也会被拒，报错信息只有 "private artifact path" 不解释命中哪条规则，排障要读源码；③scan_index/scan_git_objects 用 subprocess 逐 blob 起 git 进程（135、176）——大仓库对象多时是性能热点，每 blob 一次进程创建开销，好在有五 MB 上限（19）兜住单文件扫描成本，整体仍属可接受的一次性发布操作。

## 新人提示

先读规则表与 private_path（check_public_release.py:19-67）——这是整个闸门的政策核心，改发布内容前先确认你的文件不在黑名单语义里。再按 scan_worktree→scan_index→scan_all_files→scan_git_objects 顺序读四个扫描器（110、118、142、162），对照 docs/releasing.md 的流程理解各自守哪道门。

三个坑：CI 挂了先看是不是 staged 了 manifest 外的文件——`--tracked` 扫全索引，本地 `python scripts/check_public_release.py` 过了不代表 CI 过，两者范围不同；新增公开文件必须同步加进 public-release-files.txt 且路径不得命中 private_path 六层黑名单任何一层，否则 public_paths 直接抛 ValueError（93-94）；看到 "non-placeholder Azure resource endpoint"（82）别慌——那只是端点名不是 key，把示例配置里的资源名改成 your-resource 类占位符即可。

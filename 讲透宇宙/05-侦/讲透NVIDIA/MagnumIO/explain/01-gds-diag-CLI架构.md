# 01 · gds-diag CLI 架构：入口分派、子命令注册与检查框架

## 一、角色定位

`gds-diag` 是 MagnumIO 仓库根下与 `gds/` 并列的独立诊断工具，定位"文件系统感知的 GPUDirect Storage（GDS）诊断工具集"。GDS 故障面横跨内核（PCI_P2PDMA/IOMMU）、驱动（nvidia-fs）、网络栈（OFED/DOCA）、容器与挂载（ext4 data=journal 即禁 O_DIRECT），gds-diag 收敛为纯 Python CLI、七个子命令分诊（pre/post-install、mount-check、config-audit、container-check、support-matrix、all）。cuFile 样例跑不通时 README 首先引导跑 all；且自带 skills/gds-diag/SKILL.md 把诊断知识封装成 AI agent 技能（本仓已注册 `MagnumIO:gds-diag`）。硬约束（入口 docstring）：只用标准库，最小环境 --help 也能活（`gds-diag/gds-diag.py:8-10`）。

## 二、内部结构

入口分派——`_build_parser()` 先调 `subcommands.discover()` 拿全量命令，再手工对齐生成顶层命令表（`gds-diag/gds-diag.py:50-52`）。注册循环（:73-83）对每命令三件事：add_common_flags 注公共旗标、add_arguments 注私有参数、set_defaults(_cmd=cmd) 塞进解析结果，分派只剩 `return int(args._cmd.run(args))`（:97）。退出码契约钉死：0 全过/1 有 FAIL/2 环境未就绪/3 参数错；argparse 用法错误默认退 2，main() 重映射为 3（:92-96）。

注册表——`discover()`（`gds-diag/subcommands/__init__.py:31-50`）用 pkgutil 遍历包内模块（跳过 `_` 前缀），取每模块 COMMAND 属性并校验类型。两处容错：单模块 import 失败仅 stderr 警告不中断发现（:36-42）；类型不符跳过（:43-47）。按 (order,name) 排序（:49），order 默认 100（`gds-diag/subcommands/_base.py:27`），all 以 order=0 居首（`gds-diag/subcommands/all.py:175`）。基类只约定四属性两方法（`gds-diag/subcommands/_base.py:17-43`）；add_common_flags 统一注入 --json/-v（:46-57）。

检查框架——`gds-diag/checks/result.py` 是数据模型：Status 五态（PASS/INFO/WARN/FAIL/N-A，:12-17）+ GDSMode 四路（Native nvidia-fs/P2PDMA/RDMA/Compat，:20-24）。CheckResult（:27-39）六字段最特别是 exempted——FAIL 因另一条 GDS 直连路径已实证可用而降为非阻断。聚合在 ModeReport.status（:49-61）：不适用→N/A，未豁免 FAIL→WARN（含豁免）→INFO→PASS 逐级沉降；blockers()/failing()（:63-69）供摘要列与详细区。渲染层 `gds-diag/checks/output.py` 持有 STATUS_ICON（:29-35）、"豁免 FAIL 显示为 WARN"降级（:189-193）、决定退出码的 overall_exit_code()（:397-401，只认降级后仍是 FAIL 的项）。

## 三、外部连接

图谱上 `subcommands/_base.py` fanIn=9：七命令模块全依赖它，注册表协议权威；`checks/__init__.py` fanIn=21、`checks/result.py` fanIn=19，是全工具被引最密的数据类型。all.py fanOut=14，经 `_command_by_name()`（`gds-diag/subcommands/all.py:39-41`）importlib 动态加载兄弟命令（连字符转下划线），新命令自动入池。外围三边：gds-diag-tests.yml 拉起 tests/ 20+ 个 pytest；skills/gds-diag/ 文档+包装脚本构成 agent 技能面；doc/DESIGN.md 是退出码契约规范出处（注释回指见 `gds-diag/subcommands/_base.py:37-41`）。

## 四、数据流

以 `./gds-diag.py pre-install --json` 走一遍：① main→discover→args._cmd 指向 PreInstallCommand（`gds-diag/subcommands/pre_install.py:553`）。② run() 按 args.json 二选一（:562-563），两路共用 `_collect_sections()`（:436-489）从 checks/ 点菜式调检查：Kernel 节经 `_preinstall_p2pdma_results()` 把 P2PDMA 硬失败降级为路由 WARN（:395-433，装前他路仍在）；Mounted Filesystems 读 /proc/mounts（:477）逐挂载点查 fs_matrix 并探 O_DIRECT。③ 检查产出 CheckResult 汇成分节 dict。④ JSON 路经 results_to_json 序列化（`gds-diag/checks/output.py:384-394`），附 tool_metadata（`gds-diag/checks/version.py:47-52`）与四态计数。⑤ overall_exit_code 收口。all 再加编排：`_planned_steps()`（`gds-diag/subcommands/all.py:58-78`）判宿主/容器选序列；人类模式遇非零即停（:107-110），JSON 模式 redirect_stdout 捕获子命令 stdout 反解析（:131-135）。

## 五、设计决策

注册表优于 switch-case：新命令=新文件+COMMAND 实例、入口零改动（`gds-diag/subcommands/_base.py:8-11`），换来 all 动态编排与测试独立可测。退出码契约单点化：DESIGN.md 钉版、入口重映射、输出层计算三处共享，CI/agent 可精确分支。exempted 降级最精巧：GDS 四路线并行，"nvidia-fs 不可用"单路线视角是 FAIL，P2PDMA 已实证可用时只是性能机会——数据模型自带严重性重估，渲染与退出码消费同一降级，永不分裂。标准库约束：诊断对象常是最小镜像，依赖重则先死。all 不 fork：进程内调用+stdout 劫持省一次 Python 启动；子命令 sys.exit() 会穿透，现均以返回值交码。

## 六、新人提示

① subparsers.help=SUPPRESS（`gds-diag/gds-diag.py:71`）+手工表格：改 help 不必动入口，列宽自动重算。② argparse 的 2 被 remap 成 3（:94-95），断言别拿 2 当参数错误。③ `_` 前缀模块不进注册表——私有 helper 用 `_` 开头，新命令千万别。④ "2=环境未就绪"由各命令自返，框架不强制；自造退出码破坏 CI 假设。⑤ all 的 JSON 模式要求子命令 --json 下只打 JSON，人类日志会让 _parse_child_json 失败（`gds-diag/subcommands/all.py:143-145`）；调试信息走 stderr。⑥ `gds-diag/checks/output.py:15` 的 _USE_COLOR 导入期求值一次，monkeypatch 无效。⑦ 版本号硬编码 1.0.0（`gds-diag/checks/version.py:14`），git commit 才是可追溯标识（2 秒超时+缺 git 兜底，:39-44）。⑧ checks/__init__.py 图谱 fanIn=21，但本体只有两行 SPDX 头——高 fanIn 是包入口语义非代码量。

---
自报：本文 3480 字（不计空格），完整路径行号锚 17 个。

# verify-deepseek/ — DeepSeek 对话 NCCL 论断验证（2026-11-03/04）

用户把本仓五份 explain 精讲文档（API 面/参数系统/init/bootstrap/拓扑搜索）喂给
DeepSeek（chat.deepseek.com/share/dix4sd6p2cb1ck9mcp）得到深度解析，随后下令
"为 nccl 创建各种实验、测试等代码验证所说的是否正确"。

**活套件**（可持续跑/扩展）：`/usr-data/data2/kylin/nccl-verify-dsseek/`（45+ 文件，
`bash run_all.sh` 一键五层；另含 runtime_tests/cross_vendor/ 跨厂商对照——**就绪态，
远程执行经用户裁定暂缓 2026-11-04**，三节点手动命令见其 README）。本目录是归档快照：

- `REPORT.md` — 五层完整运行报告（L1 静态 173 条 / L2 编译期 / L3 参数系统 / L4 语法层 / L5 框架侧）
- `CLAIMS.md` — 断言全表 + 勘误清单 + 验证者自纠 + 增量发现

## 核心结论

**171/173 静态断言成立**；L2/L3/L5 行为实验全绿。**三条勘误 + 一条验证者自纠**：

1. 新轨 `DEFINE_NCCL_PARAM` **10 处非 11 处**（⚠️ 错误源头是本目录 explain 文档自身
   ——参数系统篇写"11 处"，DeepSeek 转述传播；explain/02 与上游 README 已回写修正）
2. SGLang"关闭路径倾向 Abort"**与本地快照不符**（实为 destroy_process_group；
   vLLM 侧对应说法反而在 pynccl.py:250-258 逐字命中）
3. magic 校验在 init.cc:**2572** 非 2558（行号漂移；源头 explain/01，已回写）

**验证者自纠（比勘误更有方法论价值）**：首轮曾判"`ncclparam -l` 是 DeepSeek 幻觉"——
**错误**。该 CLI 真实存在（`src/param/ncclparam.cc` 实现 `-l`/`-a`，`src/Makefile:71`
`PARAMBIN := ncclparam` 构建、`:322` 安装），对话说法正确，且源头同样是本仓 explain 文档。
教训：absent 型检查只搜源码**内容**会漏构建目标/文件名维度——"查无"≠"不存在"。

增量发现（对话漏说）：PROFAPI 门控、`setenv(...,0)`→真实 env > conf、
NCCL_CONF_FILE 分支非瀑布、NO_CACHE 名单首读快照、重复注册 WARN 非 abort。

## 对 explain 文档的回写

explain/02（"11 处"→10 处）与 explain/01（:2558→:2572）已带勘误标记完成回写（2026-11-04）。

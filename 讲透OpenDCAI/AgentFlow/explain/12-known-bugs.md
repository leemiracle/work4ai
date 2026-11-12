# 12 · 已知 bug 与坑专篇：按危害分级的问题地图

> 所属仓库：OpenDCAI/AgentFlow（图谱 909 节点/1857 边）。本篇汇总全仓已核实的问题清单，按危害分级：**S 级（安全，需立即处置）→ A 级（功能性 bug，一触即发）→ B 级（死代码/死资产）→ C 级（工程卫生）**。每条给出精确行号锚与修复建议。前 11 篇分散提到的坑此处收口，另有多条本篇独家。

## 一、角色定位

这份清单的读者画像：①准备部署 AgentFlow 的运维（先看 S 级）；②准备贡献代码的开发者（A/B 级是现成的 first issue 猎场）；③做代码考古的人（C 级揭示仓库的演化史——vm→GUI 改名、bash/browser/code_executor 后端裁撤、py2→py3 迁移残留都在坑里留了化石）。

## 二、S 级：真实明文凭据未脱敏（应立即轮换）

**osworld-settings 三处真实凭据被提交进仓**（vendored OSWorld 时上游快照带入）：

- `sandbox/server/backends/resources/utils/osworld-settings/proxy/dataimpulse.json`——**真实住宅代理凭据**：gw.dataimpulse.com:823 的 username/password 均为 16 位 hex 形态的真实账密（此处不全文复述）；旁边就有 `dataimpulse.json.template` 空模板——作者知道该脱敏，真实版却一起进了版本库。
- `osworld-settings/google/settings.json`——真实邮箱（wordalan 前缀，20 字符）+ **明文弱口令密码**。
- `osworld-settings/thunderbird/settings.json`——另一真实邮箱（anonym-x 前缀）+ 25 字符明文密码。

**对照证据**：同目录 `googledrive/credentials.json` 与 `client_secrets.json` 的 token/client_secret 字段**已全部清空**——证明脱敏动作发生过但只做了 googledrive 一处，proxy/google/thunderbird 三处漏网。

**处置**：这三个账号/代理的凭据视为已泄露，**立即轮换**（改密码、作废代理 key）；仓库历史里清除（git filter-repo）或至少在下游 fork 里删除文件；`.gitignore` 加 `osworld-settings/**/*.json` 与 `*.yml`（保留 `.template`）。

## 三、A 级：功能性 bug（一触即发）

**A1 · calc.py 缩进缺陷——with 提前关文件**：`sandbox/server/backends/resources/utils/desktop_env/evaluators/getters/calc.py:9-14`。`with open(csv_path) as f:` 在 L9，块内只有 L10 的 `reader = csv.reader(f)` 一行；L12 的 `next(reader)`（跳表头）和 L14 的 `[row[2] for row in reader]`（取第三列）**写在 with 块外**。csv.reader 是惰性迭代器，with 退出时文件已关，两行读取抛 `ValueError: I/O operation on closed file`。函数 `get_conference_city_in_order` 被 VM 评测链调用时必炸。修复：三行全部缩进进 with 块。

**A2 · get_response 的 Python 2 遗风**：`projects/DocDancer/PDF_preprocess/2_process_extracted_data.py:71`——`image_bytes.encode("base64")`。Python 3 的 bytes 没有 encode 方法（str 才有），这行在 py3 下直接 AttributeError；`bytes.encode("base64")` 是 **Python 2 时代**的惯用法。修复一行：`base64.b64encode(image_bytes).decode()`。DocDancer 的 PDF 预处理流水线一旦走到 VLM 图像描述分支（get_response，2_process_extracted_data.py:41 定义）即崩。

**A3 · eval_score 的 eval() 注入面**：`projects/DocDancer/eval/eval_score.py:138、142、178、179`——四处裸 `eval()`（`gt = eval(gt)`、`sample["evidence_pages"] = eval(...)`）。动机是把 jsonl 里的字符串化列表还原，但 eval 执行任意表达式：**评测输入里埋一个 `__import__('os').system(...)` 字符串即成代码执行**。基准数据来自外部（MMLongBench 类公开集或自造 jsonl），这是标准的二阶注入面。修复：`ast.literal_eval`，四处全换，语义完全够用。

**A4 · run_pipeline.sh 的 set -e 吞掉错误处理**：`projects/DocDancer/PDF_preprocess/run_pipeline.sh:7` 开了 `set -e`，但三个步骤的 python 命令（L101、L119、L130）都是裸调用、后跟 `if [ $? -ne 0 ]; then print_error...; exit 1; fi`（L105-108、121-124、133-136）。**set -e 在 python 非零退出的瞬间就终止了 shell，`$?` 检查根本执行不到**——三段友好错误消息全是死代码，用户只会看到裸 traceback。修复二选一：去掉 set -e，或把命令改成 `if ! python ...; then` 形态。

**A5 · start_sandbox_server.sh 显式忽略 --host/--port**：`start_sandbox_server.sh:25-27`——参数解析循环里 `--host|--port|-p` 分支的处理是"收下参数然后什么都不做"，注释自陈"Host/port are resolved from config to avoid conflicting input sources"。用户传 `--port 9000` 会被静默吞掉、服务仍起在 config 的 18890——**不报错也不生效是最坏的失败模式**。修复：要么报错退出，要么打警告。

**A6 · synthesis 输出目录参数形同虚设**：`synthesis/pipeline.py:45-47`——`__init__` 的 `output_dir` 参数被无条件覆写为 `<仓根>/results/ds_synthesized_qa`，`--output-dir`/`config.output_dir`/`OUTPUT_DIR` 三级解析链（pipeline.py:250）与八个配置里各异的 output_dir 全部无效（详见第 07 篇）。

## 四、B 级：死代码与死资产

**B1 · DEFAULT_SERVER_CONFIG 三条幽灵后端**：`sandbox/sandbox.py:64-78`——默认配置模板（`DEFAULT_SERVER_CONFIG`，L47 起）的 resources 段注册了 bash/browser/code 三个后端（L64-68/L69-73/L74-78），backend_class 分别指向 `resources.bash.BashBackend`、`resources.browser.BrowserBackend`、`resources.code_executor.CodeExecutorBackend`——**这三个模块在 resources/ 下不存在**（实际只有 vm/rag/mcp）。config_loader 按类路径 import 失败后告警跳过，所以不崩，但默认模板承诺了五后端、实际只有 vm+rag 能活。这与 ARCHITECTURE.md:469-471/613 的目录树幻影（第 11 篇勘误 B）**同源**：文档与默认配置停留在同一批后端被裁撤之前。修复：删三条目，或把后端补回来。

**B2 · VllmV0 logits processor 零引用**：`projects/DocDancer/PDF_preprocess/mineru_vl_utils/logits_processor/vllm_v0_no_repeat_ngram.py:4` 定义 `VllmV0NoRepeatNGramLogitsProcessor`——全仓唯一出现处就是它的定义本身；`__init__.py` 的 `__lazy_attrs__`/`__all__` 只导出 V1 版（`.logits_processor.vllm_v1_no_repeat_ngram`）。纯死资产，可删。

**B3 · slides.py 双同名 enable_debug_logging**：`sandbox/.../evaluators/metrics/slides.py:15` 与 L28 连续定义两个同名函数——Python 后定义胜出，L15 版（带 `[PPTX_DEBUG]` 前缀的 formatter）**永远不生效**，L28 版（标准 formatter）被 compare_pptx_files（L198）调用。两函数体几乎相同，是复制粘贴事故。修复：删其一。

**B4 · chromium_port 硬编码 fixme 双子星**：`desktop_env/controllers/setup.py:718、766` 两处 `port = self.chromium_port  # fixme: this port is hard-coded, need to be changed from config file`——注释自己承认该走配置；而 vm.py 侧默认配置又写死 `chromium_port: 9222`（vm.py:364、402、676 三处默认值）。多 VM 并发时 9222 撞端口。desktop_env 里同类 fixme 共 10+ 处（vlc.py:42、controllers/python.py:22、server/main.py:72/266/274、chrome.py:430 等）——OSWorld vendored 代码原样带着上游的未竟事项。

**B5 · rollout/api.py 文档示例双断链**：`rollout/api.py:8-9` docstring 示例 `config_path="configs/rollout/rag_benchmark.json"` 与 `data_path="benchmark/benchmark.jsonl"`——**configs/rollout/ 目录不存在**（rollout 配置实际散在 configs/infer 与 configs/trajectory）、benchmark/benchmark.jsonl 也不存在。新人照 docstring 抄即 FileNotFoundError。

**B6 · README 启动命令指向不存在的脚本**：`README.md:110`、`README_zh.md:92` 的 `./sandbox-server.sh`——实际文件名 `start_sandbox_server.sh`（全仓唯一沙箱启动脚本；第 11 篇勘误 A，此处从"新人第一命令必挂"角度收录）。

## 五、C 级：工程卫生（漂移与遗留）

**C1 · vm→GUI 改名半途遗留**：GUI_config.json 引用 `seeds/vm/seeds.jsonl`（实际 seeds/GUI/）与 `configs/sandbox-server/vm_config.json`（实际 GUI_config.json）；USAGE_GUIDE.md 同样引 vm_config.json。改名只改了文件本身，引用全没跟上。

**C2 · configs/server 目录引用**：doc_ds_config.json 与 API_TOOL_TUTORIAL.md 都引 `configs/server/...`——该目录从不存在（实际叫 configs/sandbox-server）。

**C3 · `/path/to/AgentFlow/` 占位符**：configs/synthesis/text2sql_config.json 两处（sandbox_config_path 与 seeds_file）——不是环境变量占位而是裸路径占位，照抄跑不起来。

**C4 · 默认弱凭据兜底**：`${VM_CLIENT_PASSWORD:-password}`（GUI_config.json:27，vm.py:362 的默认配置里也是明文 `client_password: "password"`）与 mcp_config.json:19-20 的 `PGUSER:-eigent`/`PGPASSWORD:-camel`——内网演示友好，部署即弱口令。

**C5 · 两套占位符体系**：config_loader 的 `${VAR:-default}`（环境变量）与 MCP client 的 `${local_servers_paths}` 等（路径三元组，mcp/client.py:18）语法同形语义不同，MCP YAML 里写环境变量占位符会被静默跳过替换（mcp/client.py:43-48）。

**C6 · docstring 承诺未实现**：result_formatter.py:56-65 声称支持 RAGBatchSearchResult/RAGStatsResult/SessionResult/InitResult/BatchExecuteResult 五类，代码零实现，`rag:batch_search` 落进来直接 ValueError（result_formatter.py:810-816）。

**C7 · ds 基准缺席**：ds_infer.json/ds_trajectory.json 引用的 `benchmark/ds_benchmark.jsonl` 不存在（第 09/10 篇）。

## 六、数据流视角：坑的成因谱系

把 17 个坑按成因归类，能看到三条演化断层线：

1. **vendored 代码自带病**（A1 calc.py、B3 slides.py、B4 chromium_port、S 级凭据、A2/A3/A4 DocDancer 三连）——OSWorld 与 DocDancer 进仓时没做入境检疫。vendored 代码的 bug 密度显著高于自研部分，**入境 lint（pyflakes+缩进检查+secrets 扫描）能拦下一半**。
2. **重构没走完**（B1 幽灵后端+第 11 篇文档幻影、C1/C2 改名遗留、A6 输出目录焊死）——bash/browser/code_executor 裁撤与 vm→GUI 改名两次大手术的缝合线外露。
3. **演示级交付痕迹**（C3 占位符、C7 缺席基准、B5/B6 文档示例失修）——仓库从内网工程开源化时的最后一公里没走完。

修复优先级建议：S 级立即（轮换凭据）→ A1/A2（两行修复，各救活一条链）→ A3/A4（安全与可用性）→ B1（删三行，消架构误导）→ 其余按接触顺路修。

## 七、新人提示

- **动 S 级前先断网轮换**：删除文件不等于 revoke——git 历史里还在，凭据轮换才是根除。
- **跑 DocDancer PDF 流水线前**：先修 A2（一行）再看 A4（shell 死错误分支），否则失败时你会误以为"脚本没报错就是没问题"。
- **评测外部数据必先修 A3**：`sed -i 's/eval(/ast.literal_eval(/g'` 四处替换，语义等价零风险。
- **排查"默认配置说有五个后端但 status 只有两个"**：直接看 sandbox.py:52-78 与 resources/ 目录的差集，别怀疑自己配置写错。
- **给沙箱换端口**：改 config 的 server.port（config_loader 吃这个），--port 参数是摆设（A5）。
- **提 PR 的最佳起点**：B3（删重复函数）、B2（删死文件）、B6（README 两行改名）——零风险、当天可合，还能顺路读懂对应模块。
- **找同类坑的方法**：`grep -rn "fixme" --include="*.py"` 一屏（本仓 10+ 处）；`grep -rn 'eval(' projects/` 抓注入面；对 vendored 目录跑一遍 pyflakes 能把 A1/A2 类问题一网打尽。

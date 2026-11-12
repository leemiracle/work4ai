# measure_flights.py — CDP 调用级计时器：双臂对比实验的测量端

## 一、角色定位

scripts/measure_flights.py（70 行）是性能对比实验的执行器：跑一次真实 Flights 搜索，把 agent 发出的**每一次 CDP 调用**按方法名计次计时，连同源码指纹、环境配置、独立验证结果写入不可复用的输出目录。docstring 后半句是它的实验设计核心（measure_flights.py:1）："freeze source externally to compare revisions"——`--source` 参数指向一份冻结的旧版检出，本脚本自身住在新版仓库里，于是**同一任务、同一判据、同一测量器，可以分别度量两代代码**。docs/performance.md 的 matched 对比表（中位 9.450s→7.092s、TypeSafe 请求 22→17、CDP 调用 1,092→101）全部数字的采集端就是这 70 行。

## 二、内部结构

**双路径导入（measure_flights.py:12-22）**——本文件最精妙处：argparse 收 `--source`（默认 "."）与必填 `--output`（measure_flights.py:13-14）；`sys.path.insert(0, source)` 后 `from jev_ultrafast import Agent`（measure_flights.py:17-18）——**被测代码来自 --source 指向的检出**；随后 `sys.path.append(本仓根)` 再 `from examples.flights import GOALS, URL, verify`（measure_flights.py:21-22）——任务与判据永远取当前工作仓。旧臂实验时 --source 指向冻结 commit 68c077b 的检出（performance.md「The original arm is the frozen source from...」）。目录同样 `exist_ok=False`（measure_flights.py:25）。

**计时包装器（measure_flights.py:30-41）**：`raw = browser_module.cdp` 保存原函数（measure_flights.py:30）；`timed` 用 `time.perf_counter` 包住每次调用，按方法名把毫秒追加进 `defaultdict(list)`（measure_flights.py:34-38）；`browser_module.cdp = timed` 完成猴子补丁（measure_flights.py:41）。**补丁为何生效**：browser.py 以 `from browser_harness.helpers import cdp` 把函数导入自己模块命名空间（browser.py:10），其后所有裸名 `cdp(...)` 调用（browser.py:23-24、36、111、125）都走模块全局查找——重绑 `browser_module.cdp` 即拦截全部出站 CDP 流量，无论 Browser 还是 browser_operation 内层。计时单位毫秒三位小数（measure_flights.py:37）。

**运行与计时边界（measure_flights.py:42-51）**：先建 Agent（浏览器 setup 的 CDP 调用已被计时，属"预热线"），随后 `calls.clear()`（measure_flights.py:44）——注释点明「Setup is excluded in both arms, as in the original demo」（measure_flights.py:43），与 performance.md「Initial navigation is excluded in both arms」同口径；run 循环逐步打印（measure_flights.py:46-49）；异常不中断落盘，`error = f"{type(exc).__name__}: {exc}"` 记录后进 finally（measure_flights.py:50-51）——失败的运行同样产出完整测量件。

**收尾与 state.json（measure_flights.py:52-69）**：`snapshot()` 取状态（measure_flights.py:53）；计时结果聚合为 `{method: {count, ms}}`（measure_flights.py:54）；然后是**测量与验证分离**的关键动作——全新 `observe(screenshot=True)` 作最终页（measure_flights.py:56），注释明言「a NEW final observation for the independent result check, outside timing」（measure_flights.py:55）；依次附加 verification、error、cdp 统计、source_hashes、`task_hash`（对 [URL, GOALS] 整体 sha256，measure_flights.py:61——把测量绑定到逐字任务）、configuration（四个 TYPESAFE_*/TEXT_* 环境变量快照，measure_flights.py:62-65）、`Browser.getVersion` 的浏览器版本（measure_flights.py:66）、final_page；写盘后 `agent.close()`（measure_flights.py:67-69）。末行打印 `VERIFIED <bool> ERROR <msg>`（measure_flights.py:70）供批处理抓取。

## 三、外部连接

被测对象：--source 检出里的 jev_ultrafast 包（Agent、browser 模块都从那里来，measure_flights.py:18-19）。任务侧：examples/flights.py 的 URL/GOALS/verify（measure_flights.py:22）——与 record_flights.py:14 同源，保证两脚本口径可比。底座：browser_harness 的 cdp IPC（helpers.py:72）——注意计时含**Unix socket 往返**，量的是"agent 视角的协议调用墙钟"，非 Chrome 内部耗时。消费端：docs/full-speed-measurement.json 存六次运行的原始数据，performance.md 据此算中位数与符号检验（p=0.25 如实标注样本量不足）。

## 四、数据流

时钟双轨制：**任务时钟**是 agent.state 的 elapsed_ms——首次 predict 才启动（agent.py:69），止于 DONE，setup 与 finally 的验证观察都不在内；**CDP 计时窗**是 calls.clear() 之后的全部 cdp 调用——含 run 本体，也含 finally 里的最终 observe 与 getVersion（measure_flights.py:56、66 发生在 clear 之后且未再 clear）。聚合只保 count 与总毫秒（measure_flights.py:54），丢弃分布细节——够回答"新版少在哪类调用"，不够做分位数分析。state.json 因此同时携带两层证据：history 里逐动作的 latency/elapsed（模型侧），cdp 里逐方法的总账（浏览器侧）。

## 五、设计决策与取舍

1. **模块级猴子补丁而非埋点改源**：被测代码零侵入——冻结的旧版无需回改就能测，这正是双臂对比可行的前提；代价是计时点绑在 IPC 边界，粒度到不了 Chrome 内部。2. **setup 剔除用 clear() 而非移动构造**：与其分辨哪些构造调用算 setup，不如全部跑完后清零——实现一行，语义明确，两臂一致。3. **失败也落盘**（measure_flights.py:50-51）：对比实验最怕静默丢样本；error 字段让六次运行可全部公开（performance.md「All six attempts are included」）。4. **task_hash + source_hashes + configuration 三重指纹**（measure_flights.py:60-65）：任务文本、代码版本、模型配置任何一项漂移都能被审计发现——可复现性是本仓叙事的硬通货。5. **验证在计时外重观察**（measure_flights.py:55-56）：与 record_flights.py:66 同款设计，验证结论不受"最后一帧恰好是决策帧"影响。6. **统计只做中位数**：performance.md 明写三对样本 p=0.25 不做强主张——测量器克制地只提供原始计数，解释权留给报告的诚实脚注。

## 六、新人提示

- **CDP 计数窗 ≠ 任务计时窗**：calls 里包含 finally 的最终观察与 Browser.getVersion（measure_flights.py:56、66），而 elapsed_ms 止于 DONE——报告里"1,092→101 次协议调用"含验证观察这几次，横向对比两臂时无碍（两臂同口径），但别拿它减算"纯执行开销"。
- 猴子补丁只拦 jev_ultrafast.browser 模块内的调用：harness daemon 自身内部或 ensure_daemon 的调用不经此命名空间——计时覆盖的是 agent 侧全部流量，但前提是 `browser_module` 确实来自 --source 检出（measure_flights.py:17-19 的顺序不能颠倒，先 insert 再 import）。
- `--source .` 默认值测的是当前仓：想测工作区未提交改动时直接跑即可；想复现冻结基线必须另备检出目录——脚本不会替你 checkout。
- `mkdir(exist_ok=False)`（measure_flights.py:25）意味着批跑脚本要自己生成不重名目录；跑挂一次目录就废了，须删除重跑。
- examples/flights.py 与本脚本的验证输入不同：前者验 state["page"]（examples/flights.py:55），本脚本与 record_flights.py 均新观察（measure_flights.py:56、record_flights.py:66）——读三份 state.json 对比验证字段时注意口径。
- 图谱 tour 第 10 步称本脚本「把 CDP 函数包成计时器统计逐方法调用次数与耗时，写入可跨修订对比的 state.json」——与源码一致（measure_flights.py:34-41、54），无出入。

# 12 · 已知 bug 与坑专篇：九处实锤与行号锚

## 角色定位

本篇是 One-Eval 的"地雷图"：跨前 5 篇的缺陷集中收录，每条给**行号锚+实锤方式**（多数经运行时或 AST 验证）。分三层：会当场崩的（A）、不崩但行为已坏的（B）、工程卫生（C）。用法：改相关文件前先对照，别把已知的坑当成自己新引入的错误。

## 内部结构

### A. 会当场崩的

**A1 · utils_execute 引用未定义的 unsafe_execute——必 NameError（patch 整文件覆盖放大）**
锚：`one_eval/patches/livecodebench/utils_execute.py` L81 `p = multiprocessing.Process(target=unsafe_execute, ...)`。实锤：AST 解析全文件，定义的函数只有 `check_correctness` 一个（`unsafe_execute defined: False`）；py_compile 通过（语法层不报，**运行时必 NameError**）。机理：该文件是对 LiveCodeBench 仓 `lcb_runner/evaluation/utils_execute.py` 的补丁（头注释自称修复 Manager+僵尸进程泄漏 L18-22），重写时删掉了原版嵌套定义的 `unsafe_execute` 却保留 L81 调用。放大器是 patches 机制：bench_gallery.json 的 `patch_files` 把本文件**整文件覆盖**到 `dest: lcb_runner/evaluation/utils_execute.py`，由 external_repo_runner.py L352-367 评测前复制——LiveCodeBench 一跑 check_correctness 就炸：补丁修了进程泄漏，引入必崩调用。

**A2 · test_example 死 import nl2bench**
锚：`tests/test_example.py` L3 `from one_eval.nodes.nl2bench import NL2BenchNode`。实锤：`one_eval/nodes/` 无 nl2bench 模块（grep 退出码 1）——模块早已被 query_understand+bench_search 拆替（09 篇），测试没跟上。同文件 L4 import 的 EvalNode 存在（eval.py 7 行；BaseNode 有 log：core/node.py L21-22，NodeState 有 update：core/state.py L124），死穴全在 nl2bench 一行。

**A3 · register_custom_tool 契约错位被 hasattr 掩盖**
锚：`one_eval/core/graph.py` L100-133（custom_tool 装饰器 L100-108、_register_tools_for_role L110-133）；对端 tool_manager.py 只有 register_pre_tool（L19）与 register_post_tool（L40），**不存在 register_custom_tool**。双层机理：①GraphBuilder.__init__ 从不初始化 custom_tool_registry，字段只在装饰器被用时懒创建（L102-103），而全仓无人用装饰器 → L116-117 `if not hasattr(...): return` 永远提前返回，死代码静默潜伏；②真注册时 L122 抛 AttributeError，L128 兜底是 `except TypeError`——**接不住**，直接崩到节点执行层。契约错位+异常类型错配双重坏。

### B. 不崩但行为已坏的

**B1 · 恒真 Y/N 判断**
锚：`tests/test_interrupt.py` L143-144：`if user_input == 'Y' or 'y' or 'Yes' or 'yes' or 'YES':`——or 链上是四个非空字符串字面量，真值恒 True，条件恒真：输 N、乱码、直接回车全走"用户批准"；L146-148 拒绝分支是不可达死代码。正确写法 `user_input in ('Y','y',...)`。这是 interrupt 审批链（09 篇）的人工验收脚本，"批准路径永远通过"给人机审批机制虚假信心。

**B2 · node_docs SET/dict 静默错位（三引号起始位写错）**
锚：`one_eval/utils/node_docs.py` L1-15。两个"键值对"以 `"""QueryUnderstandNode": ...` 起笔——三引号把键值对吞成**一个字符串**，外层无映射，运行时实测 `type is set, len 2`。消费链四处 Dict 注解运行时拿 set：workflow_all.py L84/L126 → interrupt_node.py L26/L35（`or {}` 兜底对非空 set 失效）/L138 → human_in_loop_agent.py L49/L62/L75。终点 `json.dumps(set)` 抛 TypeError（实测 "Object of type set is not JSON serializable"）被 L71-72 `except Exception: return str(obj)` 吞掉，prompt 模板 `{node_docs}`（utils/prompts.py L208-210）填进 set 的 repr。**全链静默无日志**，HumanInLoopAgent 决策上下文受损。修复：改成真正的 `"NodeName": "doc"` 映射。

**B3 · GraphBuilder 伪继承不调 super**
锚：`one_eval/core/graph.py` L57-73：`__init__` 重新声明全部七个字段（state_model/entry_point/nodes/edges/conditional_edges/pre_tool_registry/post_tool_registry），**不调 super().__init__()**；L76-98 六个方法倒是个个 super() 转发——构造不转发、方法转发，继承名存实亡。危害：父类将来加字段/构造逻辑，子类实例完全感知不到，是复制漂移温床。

**B4 · 硬编码 fallback API IP**
锚：`one_eval/core/agent.py` L128-135：`self.api_url = os.getenv("OE_API_BASE", "http://123.129.219.111:3000/v1")`。不设环境变量的部署里，**所有 Agent 推理请求默认打向这个公网 IP**（08 篇整条 CustomLLMCaller 链以此为 base_url）——既是安全隐患（谁运营该端点？数据出境吗？）也是可用性陷阱（端点失效则静默走向超时）。正确做法 None+显式报错引导配置。

**B5 · 六范式 REQUIRED_KEYS 两方不一致**
锚：`one-eval-skill/scripts/_common.py` L252 `key3_q_a_rejected: ["input_better_key","input_rejected_key"]`（两项）vs `one-eval-web/src/pages/EvalComponents.tsx` L258 同键三项（含 input_question_key）。脚本放行的 spec 到前端审校被判"缺字段"（或反之）。eval_types.md L8-9"改动须同步三处"警告的活体应验（实际四处）。

### C. 环境与工程卫生

**C1 · 测试与 workflow 硬编码绝对路径**
`tests/test_hf.py` L11：`open("/mnt/DataFlow/scy/One-Eval/cache/gsm8k_dataset_card.md","w")`——写死内网机路径且是写文件型测试；`tests/test_workflow_metric_recommend.py` L30：`r"d:\CODE\Agent-Eval\One-Eval\cache\..."`——Windows 盘符，Linux 必挂；同族 workflow_all.py L211 与 workflow_eval.py L82 默认模型 `/mnt/DataFlow/models/Qwen2.5-7B-Instruct`（裸跑 FileNotFoundError）。

**C2 · 构建产物入库**
`git ls-files` 实锤三文件被跟踪：`one-eval-web/tsconfig.app.tsbuildinfo`（tsc 增量缓存→假 diff）、`vite.config.js` 与 `vite.config.d.ts`（vite.config.ts 编译副产物，可能与 .ts 源不同步）。处置：`git rm --cached` 三件+gitignore 补 `*.tsbuildinfo`。

### D. 别篇已展开、此处登记的次级坑

`"argument" in str(e)` 误捕节点 TypeError 致静默重跑（graph.py L159-168，08 篇）；`__init_subclass__` 吞一切异常（agent.py L20-27）；前端 interrupt 路由靠节点名匹配（Eval.tsx L565/L611/L625，07 篇）；apiBaseUrl 空依赖不热更新（Eval.tsx L163，07 篇）。

## 外部连接

波及面：A1 决定 external_repo 线（05 篇）LiveCodeBench 可用性；A3/B2/B3 在 graph/agent 骨架（08/09 篇）；B4 影响全部 LLM 节点；B5 卡在 skill/web 两线间（10/11 篇）；C 组决定新环境 tests 能否跑。修复优先级：A1 > B4（安全）> B2 > B1 > A2/A3 > B3 > B5 > C。

## 数据流（复现方法）

A1：`ast` 查定义集，或跑 LiveCodeBench 看 NameError 栈。B1：任意输入跑 test_interrupt.py 永远"批准"。B2：`type(node_docs)` 一行实锤。A3：临时挂 `@builder.custom_tool` 装饰器即 AttributeError。C2：`git ls-files | grep -E "tsbuildinfo|vite.config"`。

## 设计决策（含批判）

1. **patches 整文件覆盖**（external_repo_runner.py L222-232/L352-367）是 A1 根因：补丁以整文件为单位，上游其他定义不自动保留；改用真 diff patch 或 import 冒烟自检可挡此类事故。
2. **静默兜底文化**是 B1/B2/A3 共同土壤：`except Exception: pass`（agent.py L26-27）、`or {}`（interrupt_node L35）、`str(obj)`（human_in_loop_agent L72）、`except TypeError`（graph.py L128）——单个看都"防御性"，合起来把本该响亮的错误全部消音；评测框架的可信度依赖确定性，兜底应窄而响。
3. tests/ 无 CI 硬门槛迹象（死 import 与恒真判断能长期存活即证明），是开发沙盒而非回归防线；DEV_NOTES 冒烟基线（11 篇）才是事实回归参照。
4. 默认值塞真实端点 IP（B4）是红色信号：内网 IP 泄漏或把用户流量引向私服。

## 新人提示

- 提交前自查：动 patches/ 就 ast 核对定义集；动 node_docs/prompts 就 type() 一下；动前端范式表就 diff 四处。
- 跑 LiveCodeBench 前先看 A1——上游未修前别浪费时间调试"为什么评测起不来"。
- tests/ 当历史文档读，不当可运行规范；test_interrupt.py 的审批语义被 B1 污染，不能作为 interrupt 行为的证据。
- 修 B2 时顺手在 workflow_all 装配处加 `assert isinstance(node_docs, dict)`——一行断言防四层静默。

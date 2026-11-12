# One-Eval ONBOARDING.md

> 图谱基线：636 节点/1307 边/16 层/16 步 tour@8aba20ad（2026-11-03），行号锚均从源码核实。

## 1. 一句话定位

One-Eval（OpenDCAI org）是 **LLM 评测框架**：用 **LangGraph 工作流**把一句自然语言评测需求自动变成可复跑的评测流水线与报告（NL2Eval 范式），核心资产是 **121 基准的 bench_gallery.json 唯一真源**，外围四件套——open-dataflow 评测引擎、**FastAPI 后端**（server/app.py 27 路由）、**React/Vite 前端**（one-eval-web）、**ExternalRepoRunner 外评 Docker 桥**（10 个 repo_eval 基准走外部仓+沙箱）。one-eval-skill 把 LLM 编排外移给 Claude Code，只留确定性内核。

## 2. 心智模型

**① LangGraph 三层：core→agents→nodes→graph。** core/state.py 定义 MainState（add_messages reducer）+BenchInfo/ModelConfig 数据模型，一切流转的载体；core/agent.py:20-27 `__init_subclass__` 自动登记 Agent 子类；core/node.py BaseNode 是 Agent 的图运行时包装；core/graph.py GraphBuilder 提供链式 add_node/add_edge DSL，全部 workflow 从这里生长。

**② 去中心化指标系 @register_metric。** core/metric_registry.py（fanIn=19）装饰器登记 MetricMeta、pkgutil.walk_packages 自动扫描 metrics/common/ 六模块（general.py 一模块 18 指标）。推荐采用"LLM First+规则兜底"四级优先级（HOW_TO_REGISTER_METRIC.md:18；metric_recommend_agent.py:235）：用户 meta 强制→Registry 查表（dispatcher.py:39 最长子串匹配、:44 优先级推断）→LLM 主路径→兜底，膨胀为 primary/diagnostic/secondary 三级。

**③ ExternalRepoRunner 挂载模式。** 外评基准不在本仓跑：meta.repo_eval 声明 patch_files 与 dockerfile（10 个，mathvista/bfcl/livecodebench/gaia 等），external_repo_runner.py（1059 行）隔离克隆+每仓独立 venv+shell=False 防注入，L224/L354 复制补丁、L493 Docker 沙箱；patches/ 评测桥脚本即补丁本体。

## 3. 代码地图（按 16 层）

| 层 | 内容 | 代表文件 |
|---|---|---|
| L01 | 门面：配置与文档（7） | README/pyproject/HOW_TO_REGISTER_METRIC.md |
| L02 | core 核心抽象（6） | state/agent/node/graph/metric_registry |
| L03 | agents：9 个单一职能认知单元 | query_understand/metric_recommend/human_in_loop 等 |
| L04 | nodes：运行时包装+两道 HITL 闸（15） | dataflow_eval/interrupt/pre_eval_review |
| L05 | graph 工作流编排（10） | workflow_all（主管线）/bench_gallery/eval |
| L06 | toolkits（7） | tool_manager/external_repo_runner/hf 三件套 |
| L07 | metrics 机制（8） | dispatcher/config（12 套件覆盖 40+ 数据集） |
| L08 | metrics 实现（7） | general(18 指标)/analysis/math_verify/code |
| L09 | utils 逻辑件（9） | checkpoint/bench_registry/extractor/validators |
| L10 | **基准资产（6）** | **bench_gallery.json（121 基准唯一真源）** |
| L11 | 运行时横切（4） | logger（fanIn=49）/custom_llm_caller/progress_store |
| L12 | FastAPI 服务（1） | server/app.py 2133 行 27 路由 |
| L13 | patches 外评桥+镜像（19） | run_*_oneval.py/utils_execute/Dockerfile |
| L14 | one-eval-web 前端（32） | Eval.tsx（~2500 行状态机）/Gallery |
| L15 | one-eval-skill（23） | SKILL.md/run_eval/_common.py（fanOut=35 枢纽） |
| L16 | tests（12） | test_metric_recommend（六场景）等 |

横切规律：logger fanIn=49、state fanIn=46，改它们全仓震。

## 4. 核心链路走读：一次评测的旅程

1. **入口**：Eval.tsx agent 模式收需求→POST /api/workflow/start（app.py:850）→asyncio.create_task 后台跑图，progress_store 报进度。
2. **workflow 7 阶段**（workflow_all.py:87-173，14 节点）：查询理解→bench 检索→**人工审查中断**（interrupt_node.py:21-64 validators 命中即 interrupt() 暂停，前端 resume）→结构解析/keys→配置推荐+下载→任务判定（六种 eval_type）→**评测前确认**（第二道闸）→**DataFlow 评测循环**（dataflow_eval_node.py:75-126 eval_cursor 逐 bench 校验，缺失即 Command 跳回 PreEvalReview）→指标推荐→审查→打分→报告（雷达图）。
3. **指标计算**：dispatcher 查表兜底+LLM 主路径（:235 用户覆盖优先）→runner.py 线程池并行跑分按 id 对齐 pred/ref→extractor 抽答案。
4. **外评分支**：带 meta.repo_eval 改走 ExternalRepoRunner：克隆→独立 venv→复制 patches（L354-367）→或 Docker（L493）→评测桥把模型热注册进外部框架。
5. **报告渲染**：EvalComponents.tsx BenchCard（759 行，含 eval_type/key_mapping 编辑弹窗）+三阶段节点轨道；skill 线由 render_report/make_plots 出静态产物。

## 5. 运行与调试

```bash
pip install -e .          # 或 uv venv + uv pip install -e .（py3.10-3.11）
uvicorn one_eval.server.app:app --host 0.0.0.0 --port 8000   # README_zh.md:89；app.py:2130-2133 内置同款
cd one-eval-web && npm install && npm run dev                # :5173
```

- **先配后跑**：Settings 页配 HF Token/Agent API/裁判模型。
- **CLI 星型**：one-eval-skill/scripts/ 九脚本（run_eval/run_metrics/doctor 等）全部 import _common.py（fanOut=35）；**_common.py:21-24 把仓库根 insert 进 sys.path**，skill 线直接 import one_eval 复用主仓，单独拷走 scripts/ 会断粮；L399-400 再注入 custom_metrics/。
- **断点恢复**：checkpoint.py 工厂 AsyncSqliteSaver 同 thread_id 复用，debug 复制临时库防污染；支持 stop/resume/rerun 等。
- **doctor.py** 是环境自检入口。
- **@/ 别名**：tsconfig.app.json paths `"@/*":["./src/*"]` 与 vite.config.ts resolve.alias 双处声明，IDE 跳转与构建各看一份须同步。

## 6. 已知坑（改代码前必读，均有行号实证）

1. **node_docs SET/dict 静默错位**：node_docs.py:1-15 两个"键值对"以 `"""QueryUnderstandNode":...` 三引号起笔被吞成整串，运行时实测 type=set；下游 interrupt_node.py:26/35、human_in_loop_agent.py:49/62/75 拿 set，`or {}` 兜底失效，终点 json.dumps TypeError 被 human_in_loop_agent.py:71-72 吞掉——**全链静默无日志**。
2. **utils_execute 未定义 unsafe_execute**：patches/livecodebench/utils_execute.py:81 调 unsafe_execute，AST 定义集只有 check_correctness，py_compile 不报，**运行时必 NameError**；整文件覆盖机制放大，LiveCodeBench 一跑就炸。
3. **register_custom_tool 契约错位被 hasattr 掩盖**：core/graph.py:100-108 装饰器写 custom_tool_registry，对端 tool_manager.py 却只有 register_pre_tool(L19)/register_post_tool(L40)；构造器不初始化该字段，L116-117 `if not hasattr: return` 永远提前返回（死代码潜伏），真注册时 L122 AttributeError、L128 只接 TypeError——接不住。
4. **恒真 Y/N**：tests/test_interrupt.py:143-144 `if user_input=='Y' or 'y' or ...`——or 链全是非空字符串恒 True，输 N 也"批准"、拒绝分支不可达，interrupt 人工验收失去证据力。
5. **REQUIRED_KEYS 前后端不一致**：one-eval-skill/scripts/_common.py:252 key3_q_a_rejected 两项 vs one-eval-web/src/pages/EvalComponents.tsx:258 同键三项（含 input_question_key）——脚本放行的 spec 前端判缺字段。
6. **硬编码 fallback IP**：core/agent.py:128-131 `os.getenv("OE_API_BASE","http://123.129.219.111:3000/v1")`——不设变量时全部 Agent 推理默认打向该公网 IP（api_key 同）。
7. **@/ 别名双声明**（见 §5）：IDE 跳转可能失效或与构建解析不同步。
8. **构建产物入库**：git 实锤 one-eval-web/tsconfig.app.tsbuildinfo、vite.config.js、vite.config.d.ts 被跟踪——增量缓存造假 diff、副产物与源漂移。
9. 次级：GraphBuilder 伪继承不调 super（graph.py:57-73）；test_example.py:3 死 import；test_hf.py:11/test_workflow_metric_recommend.py:30 硬编码路径；workflow_all.py:211 默认模型 /mnt 路径。批判：**静默兜底文化**（except pass/or{}/str(obj)）消音了评测框架最需要的确定性，兜底应窄而响。

## 7. 上游与生态

- **open-dataflow（requirements.txt:43）**：评测引擎本体；dataflow_eval_tool.py 封装其生成+评测管线，类级缓存 serving 防 vLLM 重复加载。姊妹仓 DataFlow 为数据清洗上游。
- **LangGraph/LangChain**：图执行底座（interrupt/Command/checkpoint）；custom_llm_caller.py 用 httpx 直调 OpenAI 兼容 API、借 bind_tools 组 schema。
- **smolagents**：GAIA 外评 Dockerfile 用 uv 全量安装，即 gaia 桥的运行时。
- **OpenDCAI org**：One-Eval 是评测线入口；外部依赖=HF 数据源+BFCL/LiveCodeBench/GAIA 等上游仓；arXiv 2603.09821 引用锚。下游=one-eval-skill 与前端 Gallery（镜像 BenchGalleryItem 类型）。

## 8. 学习路径（16 步 tour × explain 12 篇）

**第一天（骨架）**：tour T01-T03（README/三层抽象/两大扩展点）+ explain 01、03，记住 MainState、DSL、四级优先级。
**第二天（主链路）**：T04-T06+T10（bench_gallery 唯一真源）+ explain 02、04；对照 §4 数 workflow_all.py 的 14 节点。
**第三天（外围分线）**：服务线 T12-T13+explain 06/07；外评线 T14+explain 05；skill 线 T15+explain 10/11。
**随时回看**：explain 08/09（细节）+**12-known-bugs 地雷图（与本文 §6 同源互证）**；tests（T16）当历史文档读。
上手：doctor.py→手动模式跑一次 mini 评测→断点观察 interrupt/resume→bench_registry 加自定义 bench 走完全程。

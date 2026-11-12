# 12 · 已知 bug 与坑专篇：13 处实证清单

> 本篇是全系列的"排雷地图"。以下每一条都在源码逐行核实过（行号以当前工作区为准），按"踩到时的症状 → 根因 → 定位锚 → 处置建议"组织。它们多数不挡主干流程——这正是能活到今天的原因——但每一条都可能在某个边际路径上突然变成你下午的噩梦。

## 12.1 make build 必 ModuleNotFoundError（dataflow.dataflowagent 路径残留）

**症状**：在 `dataflow_agent/toolkits/dockertool/` 下执行任何 make 目标，立刻 `ModuleNotFoundError: No module named 'dataflow'`。
**根因**：包早已从 `dataflow.dataflowagent` 更名为 `dataflow_agent`（pyproject.toml L57-59 `include = ["dataflow_agent*"]`），但 dockertool/Makefile 的全部目标仍用老路径——L4 `python -m dataflow.dataflowagent.toolkits.dockertool.build_docker`，run-thirdparty/run-stdlib/clean 同样；README.md L8/12/14 的命令示例一并漂移。理论上 `dataflow_agent/__init__.py` L1-27 曾有一个 sys.modules 兼容 shim（把 `dataflow.dataflowagent.*` 映射到新包），但它**整段被注释掉了**——残留 import 从此失去救命索。
**处置**：把 Makefile 与 README 里的 `dataflow.dataflowagent`/`dataflow/dataflowagent` 全局替换为 `dataflow_agent`；或恢复 __init__.py 的 shim（不推荐，兼容 shim 本身就是技术债）。

## 12.2 LLMClient 双定义，basetool 版零消费者

仓内有**两个同名 LLMClient**：`toolkits/basetool/llm_client.py:4`（httpx 手写 OpenAI 兼容客户端，带 sync/async 双 client）与 `toolkits/multimodaltool/providers.py:1486`。全仓唯一的消费方 `fastapi_app/services/rebuttal_service.py:12` import 的是 providers 版——**basetool 版是零消费者孤儿**。风险在于改错对象：给 basetool 版修 bug/加功能永远不会生效。处置：确认无外部使用后删除 basetool 版，或在后者头部加注释指向真身。

## 12.3 text.py 把 api_key 明文写进日志

`dataflow_agent/llm_callers/text.py` L33-39 的 `log.info("[LLM Output]\n" f"api_key={self.state.request.api_key}\n" ...)`——每次调 LLM 都把用户请求里的完整 api_key 打进日志。日志文件一旦被收集/外发，等于密钥随行泄露。处置：删除该行或脱敏为 `api_key=***{last4}`。这类"调试打印上位"是快速迭代期的常见债，排雷时应全仓 grep `api_key` 的日志语句。

## 12.4 WebAgent L548 参数错位（默认配置构造后即弃）

`agentroles/paper2any_agents/websearch_researcher.py`，`class WebAgent`（L533）的 `__init__`：L543-547 先做 `self.llm_config = llm_config or {默认字典}`（默认里含 `DF_API_URL`/`DF_API_KEY`/`THIRD_PARTY_MODEL` 环境兜底），**但 L548-550 随后读的是裸参数** `api_key = llm_config.get("api_key")`。当调用方不传 llm_config（None）时：默认字典构造完就被丢弃，`None.get(...)` 直接 AttributeError——兜底逻辑形同虚设。修法一行：三处改读 `self.llm_config`。附带两个雷：默认 `api_key` 是占位串 `"sk-xxx"`，默认端点是硬编码公网 IP `http://123.129.219.111:3000/v1`（L544，同款默认还出现在 settings.py:55-56 与 websearch_initial_analyzer.py:58 等多处）——这个 IP 是团队私有网关，开源环境不可达且不安全。

## 12.5 op_tools 同函数双重定义（后者静默覆盖前者）

`toolkits/optool/op_tools.py` 里 `get_prompt_sources_of_operator` 定义了**两次**：L247 与 L367，docstring 一字不差。Python 按定义顺序执行，L367 版本胜出，L247-366 区间的整个实现成为死代码。危险点：如果你基于 L247 版本的阅读去修改它，改动永远不会生效。处置：diff 两版本取正确者，删另一份。

## 12.6 types.ts 成段重复 interface（详见第 07 篇）

`frontend-workflow/src/components/paper2ppt/types.ts` L301-440 与 L160-299 成段重复十一个 interface（FrontendCanvasNodeStyle/VisualStyle/VisualSpec/Node/ContentAsset/ValidationIssue/Validation/LayoutIRNode/LayoutIR/DeckPalette/DeckTypography 两连发），`FrontendDeckPalette` 更达三次（L282/L423/L566）。TypeScript 声明合并让编译器沉默，同名字段类型分叉时才爆出难懂错误。此处只列索引，细节见 07 篇第 5 节第 3 条。

## 12.7 wa/__init__ 导出面与实际产出不一致

`fastapi_app/workflow_adapters/__init__.py` 的 `__all__` 只列 10 个函数，但目录下 9 个 `wa_*.py`（wa_paper2ppt/wa_paper2video/wa_paper2figure/wa_paper2citation/wa_kb_deepresearch/wa_kb_report/wa_paper2poster/wa_pdf2ppt/heavy_workflow_subprocess）合计定义了约 20 个 `run_*_wf_api` 公共函数。漏网清单：**wa_paper2poster、wa_pdf2ppt、wa_kb_report 三个模块整体未导入**，paper2citation 的 `run_paper2citation_author_publications_wf_api`/`run_paper2citation_paper_context_wf_api` 两函数也未上 __init__。这些入口只能靠深路径 `from fastapi_app.workflow_adapters.wa_paper2poster import ...` 使用——如果某个新调用方写了 `from ...workflow_adapters import run_paper2poster_generate_wf_api`，AttributeError。处置：__init__ 按"全量转发"补齐，或明确声明只有 __all__ 内的是公共 API。

## 12.8 states 空壳包 vs 单数 state.py

`dataflow_agent/states/`（复数）目录里只有一个 **0 字节的 __init__.py**——空壳包。真正的状态定义全在单数 `dataflow_agent/state.py`（L41 `class MainState`、L324 `class Paper2FigureState(MainState)` 等全系状态类）。坑点：IDE 自动补全或人肉记忆很容易写出 `from dataflow_agent.states import MainState`——不报错（空壳包存在！）但拿到的是空模块，AttributeError 在使用处才炸。这个复数目录多半是重构（合并进单数文件）后没删的空壳。处置：删除 states/ 目录，或在其中 re-export 单数模块。

## 12.9 fingerprintService 死代码

`frontend-workflow/src/services/fingerprintService.ts`（139 行）在全前端**零 import 消费者**（全仓 grep 无一处引用）。从命名看是设备指纹/用户识别的预留服务，接入计划流产。139 行死代码不影响构建但污染认知。处置：删除或在文件头注明"未接线"。

## 12.10 echomimic 死路径注入（ligang 的机器快照）

两处：其一 `dataflow_agent/workflow/wf_paper2video.py` L1018-1045 的 `if __name__ == "__main__":` 测试块，全部输入路径硬编码 `/data/users/ligang/DataFlow-Agent/outputs/...`（**老项目名 DataFlow-Agent + 特定用户家目录**）外加 `chat_api_url="http://123.129.219.111:3000/v1"`——直接 `python wf_paper2video.py` 必因路径不存在失败，这是把某台内网机器的现场快照"注入"了源文件。其二 `script/start_echomimic_apis.sh` L12-13 `ECHOMIMIC_CWD=/data/users/ligang/EchoMimic`、`ECHOMIMIC_PYTHON=/root/miniconda3/envs/echomimic/bin/python`（详见第 09 篇）。处置：__main__ 块改用 argparse/env 取路径；启动脚本路径全参数化。

## 12.11 curator 空模式 re.sub（手抖残句）

`agentroles/paper2any_agents/websearch_curator.py` L88-91 是一串清洗 HTML 的 re.sub：script/style/head 标签成对出现，唯独 **L90 `html = re.sub(r"", "", html)` 模式与替换串都是空串**。这显然是一句没写完（或删除正则时留下的）残句：`re.sub(r"",...)` 用空模式匹配文本的每一个位置，结果是 no-op 但白付一遍全串扫描。不炸、不改行为、纯垃圾语句——恰恰因为无害才最难被测试发现。处置：删除该行，或补上本想写的正则。

## 12.12 chart 双 agent 的 MainState 断引用（被 __future__ 掩盖）

`agentroles/paper2any_agents/chart_code_generator.py:107` 与 `chart_type_recommender.py:121` 都写着 `async def execute_pre_tools(self, state: MainState)`，但两个文件的 import 区**只导入了 `from dataflow_agent.state import Paper2FigureState`**，MainState 这个名字从未 import——按正常规则这是 NameError。不炸的原因在两文件 L9 的 `from __future__ import annotations`（PEP 563）：注解全部延迟为字符串，定义时不求值。暴露条件：任何代码路径对这两个方法做 `typing.get_type_hints()`（如序列化框架、文档生成器）或有人去掉 __future__ 行。处置：import 行补 MainState（它确实存在于 state.py:41）或注解改用已导入的 Paper2FigureState。

## 12.13 exporter load_from_json 半成品（签名承诺 Trajectory，返回 dict）

`dataflow_agent/trajectory/exporter.py` L287 `def load_from_json(self, filepath: str) -> Trajectory:`，实现体 L302-303 注释原话："这里需要实现从字典重建 Trajectory 的逻辑 / 简化版本：直接返回字典"，然后 `return data`——返回裸 dict。类型注解是谎言：调用方按类型提示写 `traj.steps` 会在运行时拿到 AttributeError（dict 没有 .steps）。配套的 load_from_jsonl（L305）倒是从一开始就诚实地声明返回 `List[Dict[str, Any]]`。处置：要么实现 dict→Trajectory 重建（export 侧的序列化器已具备反向信息），要么把签名改诚实。

## 收尾观察：这些坑的共性

按成因聚类，13 条其实是四类病：**改名残留**（12.1 路径、12.8 空壳包、12.10 老项目路径）——DataFlow→Paper2Any 的剥离没扫尾；**复制分化**（12.2 双 LLMClient、12.5 双定义、12.6 types 成段重复、12.7 __init__ 缺口、12.9 死代码）；**调试残留**（12.3 明文 key 日志、12.11 空正则、12.10 __main__ 快照）；**声明与实现脱节**（12.4 读错变量、12.12 未导入注解、12.13 类型谎言）。给接手者的排雷优先级：先处理安全项（12.3），再处理"改了不生效"陷阱（12.2/12.5/12.4），其余按接触到相应模块时顺手清理。每一条都适合作为新人的第一批练手 PR——改动小、验证方式明确（grep/单测/类型检查即可闭环）。

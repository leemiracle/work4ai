# 08 · dataflow/webui/：Gradio 前端与幽灵模块断裂

## 一、角色定位

`dataflow/webui/` 只有四个文件：空的 `__init__.py`、`operator_pipeline.py`（679 行）、`kbclean_webui.py`（179 行）、`kb_sglang_server.py`（约 170 行）和一个被前者依赖的工具层 `kbcleaning_tools.py`（135 行）。它承担两个互不相干的职责：① 通用"算子试验场"——把全仓注册表里的算子反射成 Gradio 动态表单，零代码试跑单个算子或 API pipeline；② 知识清洗（KBCleaning）专用前端——上传 PDF/URL，四步流水线一键跑完。注意：`dataflow webui` 命令（cli.py:420-439）拉起的是另一个独立仓库 DataFlow-WebUI 的 Release 包，与本目录不是一回事——本目录更像开发者自留的轻量调试台。

## 二、内部结构

**operator_pipeline.py 的核心是 `DynamicOperatorSystem`（operator_pipeline.py:48）**，名字与文件名（operator_pipeline）严重不符——它不是 pipeline 执行器，而是**反射注册表驱动的动态表单构建器**。三层发现机制：

- `_discover_operators`（L56-65）遍历 `OPERATOR_REGISTRY.get_obj_map()`，`_analyze_operator`（L119-139）用 `inspect.signature` 抽取每个算子 `__init__` 与 `run` 的参数名/类型注解/默认值（run 参数排除 `self`、`storage`，L137）。
- `_discover_pipelines`（L67-84）只扫 `statics/pipelines/api_pipelines/` 目录；`_extract_class_names`（L86-94）用 ast 强制每个 pipeline 文件恰好一个类，多了少了都 raise ImportError（L91-93）。
- 模块级 `dynamic_system = DynamicOperatorSystem()`（L182）——**import 即触发全量扫描与 `exec_module`**，代价是导入这个文件就等于执行了所有 api_pipelines。

UI 层是 `gr.Blocks`（L491）+ 中英双语文案字典 `zh_t`/`en_t`（L187-257），语言切换回调 `switch_language` 返回 **37 个按位置对应的 `gr.update` 元组**（L268-333）。

**kbclean_webui.py** 是纯手写表单：PDF 上传/路径/URL 三种输入进 `gr.State`，serving 三选一（vllm/api/sglang）切换参数区可见性（L98-103），运行回调 `run_pipeline_ui`（L42-95）开后台线程跑 `KBCleaning_Tools.run_pipeline`，靠 `redirect_stdout` + 0.2s 轮询把最后 10 行日志 yield 给前端。

**kb_sglang_server.py** 的 `SGLangServer` 是 LLM serving 适配器：懒启动（首次 generate 才 `launch_server`，L75-84）、`find_free_port` 随机端口（L59-63）、`generate_from_input`（L87-116）用 tokenizer 的 chat template 组消息后经 ThreadPoolExecutor 打本地 `/generate` 端点。

## 三、外部连接（专节：operators.generate 幽灵断裂）

`kbcleaning_tools.py:1-6` 顶部一行：

```python
from dataflow.operators.generate import (
    CorpusTextSplitterBatch, FileOrURLToMarkdownConverterBatch,
    KnowledgeCleanerBatch, MultiHopQAGeneratorBatch,
)
```

而 `dataflow/operators/` 下**不存在顶层 `generate` 模块**——算子已按域重构为 13 个子包（general_text、text_pt、text_sft、conversations、reasoning、knowledge_cleaning、code 等），每个域内部才各有自己的 `generate/` 子目录。这行 import 因此必然 ImportError，**整条 webui 知识清洗链（kbcleaning_tools → kbclean_webui）在当前代码态下无法启动**。

这不是孤例而是系统性断裂，全仓共 3 处 `operators.generate` 引用：① kbcleaning_tools.py:1（唯一的活代码引用，致命）；② `.github/ISSUE_TEMPLATE/2-ask-for-help.yaml:44`（issue 模板给用户的示例代码 `from dataflow.operators.generate import PromptedVQA`——用户照抄即报错）；③ `statics/scaffold/{{cookiecutter.repo_name}}/.github/ISSUE_TEMPLATE/2-ask-for-help.yaml:44`（cookiecutter 脚手架里的同一模板副本，会把错误示例扩散到每个用户仓库）。正确写法已在 cli_text.py:210-214 演示：`from dataflow.operators.knowledge_cleaning import KBCChunkGeneratorBatch, KBCTextCleanerBatch, KBCMultiHopQAGeneratorBatch`——四个旧类名也需按新域内类名对号。

其余连接：operator_pipeline 依赖 `OPERATOR_REGISTRY`（L10）、`LLMServingABC`（L11）、`FileStorage`（L12）、serving 层 `APILLMServing_request`/`LocalModelLLMServing_vllm`（L159/L165）；kbcleaning_tools 依赖 `SGLangServer`、pandas、MinerU 后端（L92-96 `mineru_backend="vlm-sglang-engine"`）。

## 四、数据流

**算子模式**：用户选算子 → `build_param_templates`（L353-386）从 `OperatorInfo` 生成 init/run 两段 JSON 模板（默认值预填，`llm_serving` 参数剔除后按需显示 API/本地两组表单）→ 点执行进 `gradio_run`（L397-427）：`json.loads` 两段 JSON，若算子需要 llm_serving 则 `create_serving_instance` 现造一个注入，`info.class_obj(**other_init)` 实例化（L413），`op_inst.run(storage=storage.step())`（L419），完成后读 `storage._get_cache_file_path(operator_step + 1)`（L420，私有方法）取输出文件，pandas 读出前 5 条渲染成 HTML 预览。

**KBCleaning 模式**：PDF/URL 列表 → `multi_pdf_or_url_to_json` 落 `raw_content` 字段的 jsonl（kbcleaning_tools.py:23-30）→ FileStorage 四连步：Markdown 转换 → 512-token 分块 → LLM 清洗 → MultiHop QA 生成（kbcleaning_tools.py:92-127），每步 `storage.step()` 滚动缓存。

## 五、设计决策（含批判）

**反射表单是聪明的设计**：算子注册表本身就是 single source of truth，新算子零配置自动出现在下拉框，inspect 抽默认值直接当表单初值——这是"注册表驱动"架构在 UI 侧的自然延伸。私有方法 `_get_cache_file_path`（L420）和 `vars(pipeline_inst)` 遍历换 serving（L458-460）则是对封装的穿透，说明 FileStorage/Pipeline 缺一个公开的"取上一步输出"接口。

批判三点：① **37 元组按位置绑定**（L268-333 vs L605-618）是定时炸弹——增删一个控件要同步改两处顺序，Gradio 不会报错只会错位；② API key 走 `os.environ["DF_API_KEY"]`（L157-158、405、449、484）进程级全局变量，两个并发请求互相覆盖密钥，多用户场景直接串号；③ kbclean_webui 的日志轮询只保留尾部 10 行且线程异常被静默吞掉（L90-95 只看 `thread.is_alive()`），流水线中途炸了前端只会看到日志不再增长。

## 六、新人提示

先跑 `python -m dataflow.webui.operator_pipeline`（L677-678，0.0.0.0:7862）感受算子模式，再读 `DynamicOperatorSystem._analyze_operator`——它是理解"注册表→可执行表单"全链路的钥匙。修 KBCleaning 断裂时别只改 import：四个旧类名（kbcleaning_tools.py:1-6）要逐一映射到 `dataflow/operators/knowledge_cleaning/` 域内的新类，并对照 cli_text.py:210-214 的现成写法。改 UI 文案永远记得 zh_t/en_t 双份同步加 37 元组顺序，这是本文件最容易翻车的机械性操作。

# 07 · dataflow/cli.py：命令行总入口

## 一、角色定位

`dataflow/cli.py`（442 行）是 `dataflow` 命令的 Typer 应用入口，也是整个仓库对用户暴露的第一张脸。它自己几乎不干活——版本检查、模型探测、chat 路由三件小事自己做，其余全部委派给 `dataflow/cli_funcs/` 下的实现模块（`cli_init.py`、`cli_text.py`、`cli_pdf.py`、`cli_eval.py`、`cli_webui.py`）。顶层 import 只有 `cli_env`、`cli_init` 和一个 `_echo` 工具（cli.py:15-17），因此 `import dataflow.cli` 极轻，真正的重依赖（torch、llamafactory、gradio）全部延迟到子命令函数体内才 import（cli.py:103、173、347、396）。

## 二、内部结构

文件按功能分五段：

1. **版本与更新**：`check_updates()`（cli.py:30-52）打印本地版本并 best-effort 查询 PyPI `open-dataflow`（`PYPI_API`，cli.py:26），网络失败只红字提示不抛异常。
2. **模型探测**：`ADAPTER_FILES`/`BASE_MODEL_FILES` 两个文件名集合（cli.py:27-28）判定目录是 LoRA 微调产物还是基座模型（`detect_models_in_dir`，cli.py:59-66）；`find_latest_saved_model`（cli.py:69-95）在 `{cache}/.cache/saves` 下按 `text2model_cache_`/`pdf2model_cache_` 前缀+时间戳排序取最新一次训练产物。
3. **chat 路由**：`start_chat`（cli.py:129-167）三级 fallback——显式 `--model` 参数 → 当前目录探测 → cache 里找最新模型；微调模型走仓内 `cli_text2model_chat`/`cli_pdf2model_chat`（cli.py:99-113），基座模型直接 subprocess 调外部 `llamafactory-cli chat`（cli.py:116-126）。
4. **子命令组**：`init`（cli.py:222-280，repo 子命令真实现、operator/pipeline/prompt 三个 TODO 占位 cli.py:265-280）、`eval`（cli.py:301-321，init/api/local 三动作）、`pdf2model`（cli.py:325-385）、`text2model`（cli.py:388-417）、`env`（cli.py:282-289）、`webui`（cli.py:420-439，下载 GitHub Release zip 并拉起独立 WebUI 后端）。
5. **main 回调**：`@app.callback(invoke_without_command=True)`（cli.py:204-219），`--version` 时打印后顺带查更新再退出；无子命令则打印 help。

一个细节：`pdf2model init` 对 `--train-backend` 做白名单校验，合法值来自延迟 import 的 `DATAFLEX_BACKEND_SPECS`（cli.py:347-356），`--qa vqa` 硬性只允许 `base`（cli.py:342-345）。

## 三、外部连接

- **下游实现**：cli.py 是壳，cli_funcs/ 是肉。`init repo` 委派 `init_repo_scaffold`（cli.py:257），`env` 委派 `cli_env()`（cli.py:286）。
- **外部世界**：PyPI API（更新检查）、GitHub Releases（webui 子命令，cli.py:423）、`llamafactory-cli`（chat 兜底）、以及 `dataflow text2model init` 落地的 `.cache/train_config.yaml` 与 `text2model_pipeline/` 内置脚本体系。
- **cli_env.py 的两处硬伤**（委派对象）：`cli_env.py:23` 把 "Torchvision version" 的值写成 `torch.__version__`——torchvision 版本从未被真正读取，纯复制粘贴笔误；`cli_env.py:65-76` 取 git commit 时 `os.chdir(imdlbenco_dir)`（cli_env.py:71）后不恢复 cwd，且注释写着 "don't change the current working directory"（cli_env.py:70）与行为正好相反，变量名 `imdlbenco`（cli_env.py:67-68）是本项目前身（imdlbenco 包）的残留——迁移改名时只改了注释没改干净。

## 四、数据流

以 `dataflow text2model train` 为例：cli.py:405-417 解析参数后调 `cli_text2model_train`（cli_text.py:353），其四步流水线依次产出：Step 1 合并输入 JSON/JSONL → `.cache/gpu/text_input.jsonl`（cli_text.py:386-404）；Step 2 跑用户目录的 `text_to_qa_pipeline.py` → `text2qa_step_step3.json`（cli_text.py:406-422）；Step 3 `merge_filter_qa_pairs.py` 转 Alpaca 格式 → `.cache/data/qa.json` + `dataset_info.json`（cli_text.py:424-451）；Step 4 `llama_factory_trainer.py` 训练，产物落 `.cache/saves/text2model_cache_<时间戳>/`（cli_text.py:128-129、153）。此后 `dataflow chat` 又用 cli.py:69-95 的探测器把这条产物链接回来。

## 五、设计决策（含批判）

**延迟 import 是本文件最正确的决策**：`dataflow --help` 不应触发 torch/vllm 级依赖加载。但配套的容错哲学是"红色提示+返回 False"（cli.py:109-113），错误码统一（`raise typer.Exit(code=1/2)`），对脚本化使用友好。

批判三点：

1. **text2model train Step 1 是断链的**。`get_dataflow_script_path("merge_json_jsonl.py")`（cli_text.py:390）在全仓找不到该文件（`text2model_pipeline/` 目录只有 `llama_factory_trainer.py`、`merge_filter_qa_pairs.py`、`text_to_qa_pipeline.py` 三个文件），函数返回 None 后 `str(None)` 变成字符串 `"None"`（cli_text.py:24），subprocess 实际执行 `python None` 必然失败。更讽刺的是 `check_required_files_for_training`（cli_text.py:227-267）专门列了这个脚本做存在性检查（cli_text.py:231），但该函数**无任何调用点**——防线建了没接线，死代码。
2. **templates/* 死路径**：`get_dataflow_script_path` 的 fallback 列表 `templates/text2model_pipeline`、`pipeline_templates`（cli_text.py:53-56；cli_pdf.py:180-181 同款）在仓内均不存在，是旧目录结构搬迁后的遗迹。
3. `--version` 强制联网查 PyPI（cli.py:215）且网络差时最多阻塞 5 秒（timeout=5，cli.py:40），CI 里 `dataflow --version` 会莫名变慢。

## 六、新人提示

读这个文件最快的路径：先看 cli.py:204-280 理解命令树，再挑一条子命令线（建议 text2model）进 cli_funcs 追。三条经验：① 改子命令行为时记得 cli.py 的壳与 cli_funcs 的实现是两处，参数在 cli.py:360-365/412 这类调用点做转换，容易漏传；② 排查 "python None" 这类诡异报错先怀疑 `get_dataflow_script_path` 返回了 None；③ `cli_env.py` 的 chdir 残留意味着任何在 env 之后依赖相对路径的代码都可能踩坑——修复它只需 `os.chdir` 前 `os.getcwd()` 存档、finally 里恢复。

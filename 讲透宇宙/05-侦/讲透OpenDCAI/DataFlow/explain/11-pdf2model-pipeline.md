# 11 · cli_funcs/pdf2model_pipeline/：自包含训练脚本体

## 一、角色定位

`dataflow/cli_funcs/pdf2model_pipeline/` 是 `dataflow pdf2model` 子命令背后的"脚本体"层——由 cli_pdf.py 通过 `run_script_with_args` 以子进程方式拉起的独立脚本集合。**先纠一个数**：本目录实际只有 3 个文件（dataflex_pdf2model_launcher.py 131 行、llama_factory_trainer.py 374 行、path_to_jsonl_script.py 265 行），并非更大的脚本群；这三件套覆盖了"找 PDF → 建 config → 起训练"的完整链路。它们与 cli_funcs 里的 text2model_pipeline/（3 文件）是姊妹目录。定位上的关键差异：**pdf2model 三文件全部只 import 标准库（os/json/yaml/subprocess/argparse/pathlib 等，launcher 见 dataflex_pdf2model_launcher.py:5-12，trainer 见 llama_factory_trainer.py:7-12）**，对仓内 dataflow 代码零依赖——真正"拷出去单独跑也不坏"的自包含脚本；对照组 text2model_pipeline/text_to_qa_pipeline.py:6-18 则 import 了 operators/serving/storage 三层仓内模块，并不自包含。

## 二、内部结构

- **llama_factory_trainer.py**：`LlamaFactoryTrainer` 类实现"检查-创建-读取-训练"闭环。`get_default_config()`（L37-103）内置 LoRA SFT 全套默认值（lora_rank 16/alpha 32、cosine 调度、bf16、val_size 0.1）；`check_and_create_config`（L105-119）存在即读、缺失即建；`_load_existing_config`（L121-154）做配置**向前迁移**——旧文件缺的新参数自动补默认值、过时的 `formatting` 键自动删除（L139-142）。
- **dataflex_pdf2model_launcher.py**：DataFlex 后端启动器。`verify_dataflex_available`（L15-29）用子进程试 `import dataflex.launcher` 探测外部包；`_build_train_command`（L80-98）按 `FORCE_TORCHRUN`（默认 1，L44-53）决定单进程 `python -m dataflex.launcher` 还是 torchrun 多卡（master_port 取 20001-29999 随机，L87）。
- **path_to_jsonl_script.py**：`PDFDetector` 扫描目录收集 PDF 清单落 `./.cache/pdf_list.jsonl`（L13-21），是流水线的第一步数据清点。

## 三、外部连接

上游：cli.py:325-385 的 `pdf2model init/train` 子命令与 cli_pdf.py（DATAFLEX_BACKEND_SPECS 定义于 cli_pdf.py:28-34，目前唯一注册后端是 `dataflex-less`，L26）。launcher 被 cli_pdf.py:599（可用性探测）与 cli_pdf.py:678-690（实际执行 `run_dataflex_train`）延迟 import。下游：外部 `llamafactory-cli train`（trainer L305 以 shell 字符串拼接调用）、外部 DataFlex 训练栈。配置经 `pdf2model_state` 状态字典（cli_pdf.py:330-340）跨步骤传递，dataflex 双 yaml（components + train）在 init 阶段生成（cli_pdf.py:298-324）。

## 四、数据流

init 阶段：cli_pdf 收集模型名/qa 类型/train_backend → trainer 的 `get_default_config()` 出默认 config → 按需额外落 dataflex yaml。train 阶段：`path_to_jsonl` 清点 PDF → 上游算子产 QA 数据到 `.cache/data/`（qa.json + dataset_info.json，trainer L230-233 检查）→ trainer `check_environment`（L221-287）验数据格式 → `start_training`（L289-321）subprocess 起 llamafactory-cli；或 launcher 路线起 DataFlex。产物统一落 `.cache/saves/pdf2model_cache_<时间戳>/`，由 cli.py:69-95 的模型探测器接回 chat。

## 五、设计决策（含批判）

**两处值得单独讲的决策**：

1. **双 trainer 近复制变体**：pdf 版与 text 版 llama_factory_trainer.py 368/374 行，diff 后**唯一实质差异**是数据格式检查分支——pdf 版先查 `"messages" in sample` 认 ShareGPT 格式（llama_factory_trainer.py:258-263），否则退查 Alpaca 三键（L265-270）；text 版只认 Alpaca（text2model_pipeline 对应 L255-268）。PDF→VQA/KBC 链路产出多模态对话数据用 ShareGPT，纯文本链路产 Alpaca，两条产品线各带一份 trainer。批判：两文件 95%+ 相同（连默认配置、print 文案都一致），配置迁移逻辑修 bug 必须改两处——这是"复制优于抽象"的短期选择，演化上已现分叉风险（pdf 版多了 6 行）。
2. **launcher 的 pin_memory 补丁注入**：`_launcher_cli_overrides`（dataflex_pdf2model_launcher.py:63-77）默认在命令尾部追加 `dataloader_pin_memory=false`，注释直言原因（L76）：VL 批次（如 Qwen2.5-VL）会产生**重叠存储的张量**，pin_memory() 遇到即崩。逃生门是环境变量 `PDF2MODEL_DATAFLEX_ALLOW_PIN_MEMORY`/`DATAFLOW_LESS_ALLOW_PIN_MEMORY`（L65-73）——注释掉补丁换回性能。这是把"模型输出的张量内存布局"这一底层兼容性问题用 CLI 参数覆盖优雅挡在用户视线之外，做法可取；代价是 pin_memory=false 对训练吞吐有可测损失，且默认全局生效（非 VL 模型也被牺牲）。

批判第三点：trainer L313 `subprocess.run(train_cmd, shell=True)` 用 shell 字符串拼接执行（config 路径含空格即碎），而 launcher L123 用参数列表模式——同一目录两种工程标准。

## 六、新人提示

改训练默认超参去 `get_default_config()`（L37-103）一处即可，`_load_existing_config` 会把新键自动迁移进用户旧 config，不破坏现场。排查"DataFlex not importable"先手动跑 launcher L18-23 的探测命令。想让多卡训练换端口看 L86-94 的 MASTER_ADDR/MASTER_PORT 环境变量。**最要紧的提醒**：如果同时维护 text/pdf 两条链，改 trainer 时先 diff 两份（`diff text2model_pipeline/llama_factory_trainer.py pdf2model_pipeline/llama_factory_trainer.py`），确认改动是否需要双边同步——历史上它们就是同一份文件复制出去的。

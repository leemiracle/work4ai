# 04 · fabric CLI 与脚手架

> 仓库：NVIDIA/NeMo-Fabric @ 86f86882 · crates/fabric-cli（1790 行 · main.rs 16 + lib.rs 10 + app.rs 480 + presets.rs 434 + scaffold.rs 566 + examples.rs 207 + assets.rs 77）

## 一、角色定位

`nemo-fabric` 命令行是用户的**第一触点与实验场**。app.rs:4 模块文档一语道破定位："Experiment with NeMo Fabric presets and maintained examples"——它不是运维工具，是把内置 preset 和官方示例"五分钟跑起来"的体验层。CLI 二进制本身极薄：main.rs 只有 16 行，lib.rs:10 把执行逻辑委托给 app.rs 的 execute_from；真正的工作分布在四个模块——app.rs（命令树）、presets.rs（五个内置预设）、examples.rs（维护的示例）、scaffold.rs（可编辑工程脚手架），assets.rs 提供"嵌入式资产暂存"这一共享底座。

CLI 是 workspace 默认成员之一（Cargo.toml:9-12 default-members 含 fabric-core 与 fabric-cli），与 PyPI 上的 nemo-fabric-runtime 不同通道发布（crates.io 侧），服务于 Rust 生态与快速冒烟。

## 二、内部结构（带行号）

**命令树（app.rs:27-53）**：`Command` 枚举六分支——Preset（List/Show 子命令，app.rs:56-64）、Example（List/Show/Init，app.rs:66-88）、Plan、Doctor、Run（带 `--input` 默认空，app.rs:44-50）、Version。app.rs:20 `arg_required_else_help` 让裸 `nemo-fabric` 直接打印帮助。

**互斥选择器（app.rs:90-128）**：`Selector` 的 `--preset` 与 `--example` 被 ArgGroup("source") 钉死 required=true + multiple=false（app.rs:91-96）——两个来源必须恰好选一个；`--variant` 只许配 example（app.rs:108 requires/conflicts）；`--model/--temperature` 只许配 preset。temperature 解析器（app.rs:130-139）拒绝 NaN/Inf。这种"编译期参数关系"设计让 clap 在解析层就挡掉所有非法组合。

**执行入口（app.rs:160-171）**：execute_from 先 try_parse_from，DisplayHelp/DisplayVersion 错误直接打印返回 Ok——帮助不是错误；run()（app.rs:178 起）按命令分发。

**内置预设（presets.rs:139-165）**：`PRESETS: [Preset; 5]`——scripted（"Credential-free deterministic smoke preset"，零凭据冒烟）/hermes（需 NVIDIA_API_KEY）/claude（需 NVIDIA_API_KEY + NVIDIA_FRONTIER_BASE_URL_ENV，presets.rs:156-158）/codex（同 claude）/deepagents（需 NVIDIA_API_KEY）。每个 Preset 含 name/description/required_env/build 函数/assets。

**内嵌资产（presets.rs:16-25）**：五个适配器 descriptor 全部 `include_str!` 编进二进制——scripted.fabric-adapter.json + run.py（一个确定性的假 harness，scripted 预设免凭据的秘密）、hermes/claude/codex/deepagents 的 .fabric-adapter.json。NVIDIA_API_CATALOG_BASE_URL 是 `https://integrate.api.nvidia.com/v1`（presets.rs:26）——NVIDIA 托管模型的统一入口。预设配置内联了真实工程判断：claude() 设 `permission_mode: "dontAsk"`（presets.rs:182-186），codex() 关掉 apps/multi_agent/plugins/web_search 并设 sandbox=workspace-write（presets.rs:204-216）——评测场景的沙箱默认值。

**示例（examples.rs）**：`EXAMPLES: [Example; 1]`（examples.rs:121）目前只有 code-review 一个，内嵌 calculator.py 工作区（examples.rs:14-15）与 code-review 技能 md，CODE_REVIEW_VARIANTS 五个变体 `["scripted","hermes","claude","codex","deepagents"]`（examples.rs:29）——同一示例 × 五种 harness 的能力对照实验。

**暂存资产（assets.rs）**：EmbeddedFile 是 (path, contents) 静态对；StagedAssets::create（assets.rs:31-47）把内嵌文件写进 `temp_dir/nemo-fabric-{pid}-{nonce}` 临时根，nonce 取纳秒时钟；impl Drop（assets.rs:59-62）在作用域结束自动 remove_dir_all——CLI 跑完不留垃圾，Rust RAII 做进程内清理。内嵌测试 assets.rs:69-86 验证 stage-and-remove 生命周期。

**脚手架（scaffold.rs）**：五个模板 include_str!（scaffold.rs:16-20）——python/main.py.tmpl + pyproject.toml.tmpl、rust/main.rs.tmpl + Cargo.toml.tmpl、共享 README.md.tmpl。Language 枚举 Python/Rust（scaffold.rs:30）。init()（scaffold.rs:48-82）流程：目标目录存在直接报错（防覆盖，scaffold.rs:51-56）→ variant 默认取 example.default_variant → 复用 preset 资产 → 叠加语言文件（scaffold.rs:85-110）→ README 模板三占位符替换（scaffold.rs:77-79 `{{EXAMPLE}}/{{VARIANT}}/{{LANGUAGE}}`）。render_python/render_rust（scaffold.rs:155 起）把 FabricConfig 实例值反渲染成模板代码——**生成的 main.py/main.rs 是可编辑的普通工程，不是一次性脚本**。

**本地依赖切换（scaffold.rs:112-131）**：rust_core_dependency 探测 `../fabric-core/Cargo.toml` 是否存在——存在则生成 `path = <canonicalize>` 本地路径依赖，否则用版本号。这意味着从仓内生成的 Rust 工程自动联动本地 core（改 core 即生效），从 crates.io 安装的用户拿到版本依赖。scaffold.rs:496/516 两个测试专门验证这两种形态。

## 三、外部连接

- **fabric-core**：app.rs:8-11 直接 import resolve_run_plan_from_config/doctor_plan/run_plan——CLI 的 Plan/Doctor/Run 三个命令就是 core 三个公开函数的 JSON 打印壳（app.rs:216-230 Plan 输出 to_string_pretty）。
- **适配器生态**：presets 资产里的五个 .fabric-adapter.json 与 adapters/python 的同名正式包（claude/codex/deepagents/hermes）是**精简版对正式版**关系——CLI 内嵌版让用户不装任何 PyPI 包也能体验完整生命周期。
- **examples/ 仓库目录**：examples.rs 的"maintained examples"与仓根 examples/ 目录（code_review_agent、langgraph_custom_agent 等）呼应，CLI 的 example init 把精选示例物化为本地工程。
- **skills/**：skills/nemo-fabric-build-adapter 与 skills/nemo-fabric-integrate 两个对外技能引导用户走 CLI 入口。

## 四、数据流

以 `nemo-fabric run --preset scripted --input "hello"` 为例：clap 解析 → run() 匹配 Command::Run → select_source 找到 scripted Preset → Preset::stage()（presets.rs:79 起）用 StagedAssets 把内嵌 descriptor+run.py 写进临时目录，base_dir 指向那里 → core 的 resolve_run_plan_from_config 在临时目录发现 descriptor → run_plan(plan, RunRequest::text("hello")) 走 scripted 适配器（确定性 Python 脚本）→ RunResult 打印 → StagedAssets Drop 清理临时目录。

example init 流程：`nemo-fabric example init code-review --language python` → find_example → scaffold::init 把 calculator.py+技能 md+pyproject.toml+main.py+README 写进目标目录 → 用户得到可 `pip install -e` 的完整工程。

## 五、设计决策

1. **资产编译期嵌入**：include_str! 让 CLI 单二进制自足——安装即用、零网络拉取、离线可跑 scripted 预设。代价是二进制体积，换来"冒烟体验永不因资产服务器挂掉而失败"。
2. **RAII 暂存目录**：StagedAssets 的 Drop 清理（assets.rs:59-62）比手动清理可靠——即使命令中途出错返回，Rust 析构照样执行。
3. **防覆盖硬失败**：init() 对已存在目录直接 Err（scaffold.rs:53-55），不搞交互式询问——CLI 工具在脚本里的可组合性优先。
4. **参数关系编译期化**：ArgGroup + requires + conflicts_with（app.rs:91-127）把"哪些旗标组合合法"全部交给 clap，run() 里不再出现参数合法性判断。
5. **本地/发布双态依赖**：rust_core_dependency 的探测式切换（scaffold.rs:112-131）让同一脚手架在贡献者机器与用户机器上都"做对的事"——贡献者改 core 立刻见效，用户拿到稳定版本。

## 六、新人提示

- 跑通第一个东西用 `nemo-fabric run --preset scripted`——零凭据、确定性输出，是验证安装的最快路径；claude/codex 预设要先备好 NVIDIA_API_KEY（presets Show 会列出 required_env，app.rs:196-203）。
- Plan 命令不执行只打印解析后的 RunPlan JSON——调试"为什么我的配置路由到这个适配器"时先跑 Plan 再跑 Doctor。
- 脚手架生成的工程是"活的"：Rust 工程在仓内生成时自动 path 依赖本地 core，别惊讶 Cargo.toml 里的本地路径。
- 给 CLI 加命令的模式：Command 枚举加分支（app.rs:27-53）→ run() 加匹配臂 → 需要新资产就进 assets/ + include_str!。preset 新增要同时改 PRESETS 数组与资产常量。
- examples.rs 的 Example 结构与 examples/ 仓根目录是两个体系：CLI 的 example 是"内嵌可 init 的模板"，仓根 examples/ 是"参考实现源码"，别混淆。

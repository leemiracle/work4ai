# workflows/cli.py — CLI 入口：18 条命令串起录制、生成、执行与托管

> 源文件：`workflows/cli.py`（2662 行，注意在 `workflows/` 根而非 `workflow_use/` 包内）

## 一、角色定位

这是 workflow-use 的**统一操作面**：基于 Typer 的 `workflow-cli`（L27-32），把仓库六大能力暴露为 18 条子命令——录制建流（create-workflow / create-workflow-no-ai / build-*-from-recording）、任务生成（generate-workflow，调 HealingService）、执行（run-workflow / run-workflow-no-ai / run-as-tool / run-workflow-csv / run-stored-workflow）、语义调试（generate-semantic-mapping / create-semantic-workflow）、资产管理（list / delete / workflow-info / generate-csv-template）、托管（mcp-server / launch-gui）。它同时是"无 AI 录制→语义工作流"转换链（`_convert_recording_to_semantic_workflow`，L380）的宿主——录制数据重放建映射的核心逻辑住在这里而非库内。

## 二、内部结构

- **模块级初始化**（L34-53）：import 时即建 `ChatBrowserUse(model='bu-latest')` 双实例（agent + extraction），失败则**交互式 input 补 API key**（L40-45）；随后单例化四大服务：`builder_service`（L47）、`recording_service`（L49-51，无需 LLM）、`healing_service`（L52）、`storage_service`（L53）。
- **录制构建助手族**（L65-873）：`_build_and_save_workflow_from_recording`（L65，LLM 路线）与 `_build_and_save_semantic_workflow_from_recording`（L153，语义路线）；录制修补三件套 `_fix_missing_navigation_steps`（L245）/`_is_form_progression`（L290）/`_infer_navigation_step`（L316）；噪音清理 `_filter_redundant_click_events`（L525）+`_select_best_click_from_group`（L618）；语义转换 `_convert_step_to_semantic`（L687）、`_simulate_step_interaction`（L796）、`_find_best_semantic_match`（L829）、`_extract_target_from_selector`（L850）。
- **语义转换总控**（L380-523）：见数据流。
- **18 个 `@app.command`**（L870-2605）：定义即文档，命令名与帮助文本齐整；入口 `if __name__ == '__main__': app()`（L2660-2662）。

## 三、外部连接

`RecordingService`（L20，起 uvicorn :7331 收扩展事件）、`HealingService.generate_workflow_from_prompt`（L2347）、`Workflow.load_from_file`/`run`（L1209/1310）、`get_mcp_server`（L19/L2151，SSE 暴露工作流为工具）、`WorkflowStorageService`（L2369 存取）、`BuilderService`（L99）。重放侧直接用 browser-use `Browser`（L414）。GUI 命令 `subprocess.Popen` 拉 `uvicorn backend.api:app` 与 `npm run dev ../ui`（L2170-2172）。依赖 pandas（L10，CSV 批跑用）。

## 四、数据流

**语义录制转换链**（create-workflow-no-ai 主路径）：`recording_service.capture_workflow()` 交互录制（L960）→ 临时 JSON 落 `./tmp`（L972-919）→ `_convert_recording_to_semantic_workflow`（L380）：先滤冗余点击（L396）、可选补导航（auto_fix，L402-408，该命令默认 False，L988）→ 起真实 Browser **重放**录制：navigation 步 goto + sleep 2 建页级语义映射（L432-436），每个交互步前 sleep 1 刷新映射（L447-455，注释点名动态表单），scroll 步用 `window.scrollBy` 重放再刷新（L483-485）→ `_convert_step_to_semantic` 把 cssSelector 步骤换成 target_text 锚（L464）→ 组语义工作流 dict（L513）。

**执行链**（run-workflow，L1182）：加载 Workflow → 输入编排：必填项全有默认值则免提示直用（L1228-1246），否则按类型交互提示（bool→confirm、number→float、string→str，L1280-1297）→ `workflow_obj.run`（L1310）。

**生成链**（generate-workflow，L2304）：`healing_service.generate_workflow_from_prompt`（L2347）→ 展示摘要 → 默认入库 storage（L2369）→ 打印后续命令引导（L2384-2390）。

**托管**：mcp-server 默认 8008 端口、SSE 传输、绑定 0.0.0.0、workflow_dir=./tmp（L2151-2157）；launch-gui 双进程 + Ctrl+C 联动 terminate（L2175-2182）。

## 五、设计决策与取舍

- **三处 `SemanticExtractor` 延迟导入**（L382/L1545/L1640）已核实：语义相关命令才 import，保证 `run-workflow` 等纯执行命令不背浏览器抽取栈的加载成本——CLI 启动延迟的工程化处理。
- **转换逻辑宿在 CLI 而非库**：重放建映射是"工具性"流程（一次性、可交互输出进度），与库内 `SemanticWorkflowExecutor`（执行期）分工明确；代价是这段重要逻辑难以被其他前端（如扩展 UI）复用。
- **输入默认值快捷通道**（L1228-1246）：全默认即可静默执行，为 CSV 批跑与 MCP 工具化铺路——无人值守场景优先。
- **Typer 而非 argparse**：类型注解即参数定义，Path 的 exists/file_okay 校验（L1183-1191）免费获得。
- **命令名双风格并存**：早期动词式（create-workflow）与后期动宾式（generate-workflow / run-stored-workflow）混排，是生长型 CLI 的典型地层。

## 六、新人提示（坑/勘误）

1. **generate-workflow 的模型参数是摆设**：`agent_model/extraction_model/workflow_model` 选项（L2306-2308，默认 gpt-4.1-mini/gpt-4.1）只在 L2338-2340 被回显，实际 LLM 硬编码 `ChatBrowserUse(model='bu-latest')`（L2334-2335）——传 `--agent-model` 无效，勘误钉版。
2. **import 即副作用**：模块级 LLM 初始化失败会走 `input()` 交互（L41-43），在 CI/管道等非 TTY 环境直接 EOFError——脚本化使用需预置 `BROWSER_USE_API_KEY`。
3. `mcp-server` 绑 `0.0.0.0`（L2155）：默认对外监听，容器内合理，本机调试建议显式 `--port` + 防火墙意识。
4. 录制转换的 sleep 值（导航后 2s L435、交互前 1s L451）是硬编码经验值，慢站点会提取到半渲染页面——先怀疑这里再看 SemanticExtractor。
5. `run-workflow` 的帮助文本仍写 ".workflow.json"（L1189），但 `Workflow.load_from_file` 实际走 `yaml.safe_load`（service.py L124）——**只吃 YAML**，帮助文本过期。
6. `./tmp` 既是默认保存目录（L56-61）又是 MCP 的 workflow_dir（L2151）——CLI 产出的工作流默认就能被 mcp-server 托管，这是隐性契约，挪目录要两处一起改。

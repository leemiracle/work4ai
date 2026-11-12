# NeMo-Inspector Onboarding

> 仓 /usr-data/data2/repos/agent-repos/NVIDIA/NeMo-Inspector @ c2a14ff9 · 49 文件 · 图谱 160n/403e/10 层
> 行号锚经源码逐行核实（2026-11-11）。`common.py` 本仓有三处（utils/、utils/decoration/、settings/constants/），锚带目录前缀消歧。

## 1. 定位：Dash 写的"模型预测检查器"

把多模型在同一数据集上的生成结果（jsonl）并排对比，供人工检查、过滤、排序、打标签、行内编辑、自定义统计、导出回 jsonl。典型输入是 llama 风格代码评测输出——答案内嵌 `{code_begin}...{code_end}` 与 `{code_output_begin}...{code_output_end}` 块（默认分隔符 settings/constants/configurations.py:15-21），UI 拆成 explanation/code/output 三段渲染。技术上是单页 Dash（Flask）应用，localhost:8080，无后端存储无认证，全部状态住 Python 进程内存。代码五块：入口（inspector_app.py+parse_agruments_helpers.py）、配置（settings/）、状态中枢（utils/common.py，全仓 fanOut 最高）、UI（layouts/+callbacks/）、渲染线（utils/decoration/+assets/scripts/）。

## 2. 启动与配置链

`python -m nemo_inspector`（__main__.py:15-18）→ `main()`（inspector_app.py:35-62）：忽略 SIGALRM（:36）；dataclass 展开成 CLI 参数（:40-45）；重建 dataclass（:47-50）；code_tags 合并默认分隔符（:51-52）；延迟 import callbacks 包（:54，import 副作用即回调注册）；cfg 写 `app.server.config["nemo_inspector"]`（:56——此后全仓经 Flask config 读配置，utils/common.py:106/:289/:397）；`app.run(host="localhost", port="8080")`（:59-62）。

**dataclass↔argparse 桥**（parse_agruments_helpers.py）：正向 `add_arguments_from_dataclass`（:30-95）递归遍历字段——bool→`store_true`（:79-84），dict→`ParseDict` action 收 `k=v` 列表（:22-27、:85-91），嵌套 dataclass 加 `prefix.`（:46-55）；反向 `create_dataclass_from_args`（:98-126）缺席字段按 default→default_factory→类型默认回退（:119-124）。CLI 即 `--model_prediction modelA=path1 modelB=path2`。**路径展开**在 InspectorConfig（settings/inspector_config.py:23-50）：`__post_init__` 把空格分隔多路径经 `_expand_paths` 展开——glob/目录 rglob("*.jsonl")/`dict.fromkeys` 去重保序。

## 3. 全局状态中枢：模块级单例

utils/common.py:38-47 定义九个模块级可变对象：`dataset_data`（★主数据 question→model→[记录]）、`custom_stats`/`general_custom_stats`、`stats_raw`、`excluded_rows`/`editable_rows`/`compared_rows`（行状态三集合）、`deleted_stats`、`labels`，访问全走 getter（:50-88）。这是 Dash 逼出的务实选择：回调共享大表格若用 Store 组件要浏览器↔服务器序列化往返，服务端全局零拷贝——单用户本地工具进程即会话。要点：① **getter 返回引用**——`get_table_data().sort(...)`（base_layout.py:168、:178）原地排序全局表、`get_editable_rows().add()`（detailed_sample_info.py:270）直改集合，重建函数天然生效；② **真值/副本分层**——`get_data_from_files`（utils/common.py:287-348）`@lru_cache` 缓存磁盘真值，`custom_deepcopy`（:277-284）两层浅拷贝灌工作副本（base_layout.py:341），过滤非叠加模式清空重拷回干净数据（:222-224；注意名字带 deep 实为两层浅拷贝）；③ **并行加载**——joblib `n_jobs=-1` 全核逐模型读文件（:330-334），重名自动 `_1` 后缀（:305-311），逐问题算好指标（:341-347）。

## 4. 布局与回调架构

**app 诞生**：callbacks/__init__.py:20-30 创建全局唯一 `app`（`suppress_callback_exceptions=True`——动态表格 id 不在初始 layout 必须开；Bootstrap 主题；assets 挂 nemo_inspector/assets），末尾才 import 两个回调子包触发注册。**骨架**（layouts/base_layouts.py:19-35）：Navbar+`page_content`+三个暗容器 `js_trigger`/`js_container`/`dummy_output`（:31-33）——Dash 只能靠属性变化驱动回调，哑组件是二级触发链火种（§6）。**唯一路由** callbacks/common/navigation.py:30-43：任何 pathname 都返回分析页 `get_compare_test_layout()`（base_layout.py:60-97：六模态框工具条+add_model+基准选择器；:94 `compare_models_rows` 装三层表格），顺带装配分隔符二元组（:34-40）。

**九大回调群**（callbacks/analyze_page/，8 文件 22 回调）：short_info_table.py:38 切基准模型重建表格、:61 分页；detailed_sample_info.py 9 回调管明细区交互（explain 03）；filter_dataset.py:86 过滤；sort_dataset.py:73 排序；update_dataset.py:59 改写数据；label_dataset.py:89/:193/:241 标签三件套；count_stats_dataset.py:83 exec 注册统计；save_dataset.py:56 导出（:59-60 路径解析、剔除 EXTRA_FIELDS=configurations.py:23 后写 jsonl）。**表格重建四件套**（base_layout.py:100-358）是公共后端：update/sort/filter/initial 四函数同构——读写全局表→组装简表+统计+明细三层；过滤支持 `&&`（:246-249）、注入 `base_generation` 变量（:253）、文件级模式整题剔除（:295-298）。

**两个暗坑**：① 同名 `apply_new_stat` 双回调（count_stats_dataset.py:83/:138）——Dash 按 Output 签名注册两者都能跑，但模块命名空间里名字只指向后者（§8.4）；② exec 注入面——用户代码统一走 `get_eval_function`（utils/common.py:226-239，模板包成 `def eval_function(data):...; return <末行>` 后 exec，无沙箱），异常靠 catch_eval_exception（:258-274）兜默认值。安全边界仅靠 host="localhost"。

## 5. 文本渲染线

总入口 `design_text_output`（utils/decoration/common.py:26-67）：ANSI 模式（:32-48，检测 `\x1b\[[0-9;]*m` 或 Traceback）ansi2html 转 HTML 装 iframe；LaTeX（:51-55）预处理后 `dcc.Markdown(mathjax=True)`；否则 Markdown/带 diff 样式 span。**LaTeX 预处理**（utils/decoration/latex.py:103-168）手写扫描器：`\[ \] \(` `\)` 改写 `$$`（:104-106），主循环识别 `\begin{}`/`$$`/单 `$` 三类定界（:70-93；单 `$` 要求紧邻非空白防"5 美元"误判），公式区外逐字符转义 Markdown 特殊字符（:96-100）。**diff**（utils/decoration/plain_text.py:37-84）：token 化（:19-34 三类 token）+SequenceMatcher 上色，语义"当前列视角"：当前列独有=绿、基准独有=红底删除线（:52-82）——注释的 deleted/inserted 与颜色直觉相反但结合调用方 common_layouts.py:131-142 自洽。**答案解析** `parse_model_answer`（utils/common.py:91-160）未闭合代码块打 `wrong_code_block`（:143-155）触发红边框（common_layouts.py:108-113）；`get_single_prompt_output_layout`（common_layouts.py:80-152）按段分派渲染函数。

## 6. iframe 高度协议：跨语言握手

内容 iframe 不自动撑高，协议两端跨两种语言：发送端 `update_height_js`（utils/decoration/common.py:91-104）生成量高 JS——四种高度取 max 后 `parent.postMessage({frameHeight, frameId}, '*')`（:100）；接收端 change_element_height.js:15-22 按 frameId 设 iframe 高度；textarea 侧 register_textarea.js:15-31 绑自适应。关键在触发链——Dash 重渲染不执行新 script，三级接力：重渲染回调顺带返回 `js_trigger+" "`（detailed_sample_info.py:95）→ callbacks/common/decoration.py:20-30 重新注入隐藏 iframe（utils/decoration/common.py:70-88，DOMContentLoaded 调 `parent.registerTextarea()`）→ 全部 textarea 重绑。js_container/js_trigger 暗容器即为此链存在；dummy_output 同理当信号源（detailed_sample_info.py:202）。

## 7. 测试

唯一测试 `nemo_inspector/tests/test_ping.py`：module fixture 子进程拉服务（:38-44），headless Chrome 开 localhost:8080/analyze 断言 add_model 可见（:74-82）。零单元测试——get_eval_function/preprocess_latex 等纯函数好测但上游没写。依赖 requirements/inspector.txt 八项（dash/dash-ace/dash_bootstrap_components/ansi2html/pygments/joblib/pandas/sshtunnel_requests，无版本钉死）+inspector-tests.txt。test_ping.py:39 走目录形式（__main__.py），setup.py:43-47 另注册 console_scripts——两条启动路径同达 main()。

## 8. 陷阱与勘误（源码实证）

1. **tests/README 引用上游 monorepo 路径本仓不存在**：要求装 `requirements/main.txt`、`common-tests.txt` 并跑 `pytest inspector/tests`；实际只有 inspector.txt/inspector-tests.txt、测试在 `nemo_inspector/tests`——拆仓残留，照抄即 FileNotFoundError。
2. **`parse_agruments_helpers.py` 文件名拼写笔误**：应为 parse_arguments_helpers（agruments 少 u），inspector_app.py:21-25 全仓引用带病传播。
3. **exec 注入安全面**：utils/common.py:226-239 与 count_stats_dataset.py:92-101 两处直接 exec 用户代码，无沙箱无过滤（异常兜底仅 :258-274）；唯一缓解 host="localhost" 写死（inspector_app.py:60）——改 0.0.0.0 即挂出任意 Python 执行权。
4. **同名 apply_new_stat 双回调合并**：count_stats_dataset.py:83（注册统计）与 :138（编辑器回填）同名，功能正常但按名引用只见后者。
5. **compare_styles.css 双重不存在**：utils/decoration/common.py:44 同一 link 两个 href（HTML 取第一个），且 assets/styles/ 下无此文件——死引用两头堵。
6. **input_file 死路径**：args_postproccessing（parse_agruments_helpers.py:129-132）塞、utils/common.py:291/:163 消费，但 InspectorConfig（inspector_config.py:41-44）无此字段恒为 `""`——dataset 联表永远走 None 分支。
7. **get_compared_rows 注解错**：utils/common.py:66 写 `-> Dict` 实为 set（:43）。
8. **按钮 style 重复键**：table_layouts.py:223/:225-229 等两个 `display` 键后者覆盖前者。
9. **register_textarea.js:26-27 死代码**：textarea 无 onload/onresize，仅 input 监听（:28）生效。
10. **可变默认参数**：table_layouts.py:302，只读未爆雷。

**上手顺序**：§2→§3→explain 05 三层表格→explain 03 明细回调→explain 04/06。改 UI 行为先查 settings/constants/（common.py:15-38 模式名/字段名、templates.py:16-18 动态 id 模板）。
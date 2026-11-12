# 讲透 NeMo-Inspector

> NVIDIA NeMo-Inspector——**Dash/Plotly 写的模型预测检查器 UI**：加载各模型 jsonl 预测文件→分析页对比表（明细/行内编辑/标签/过滤/排序/自定义统计/保存），模型答案按 code/latex/markdown/ansi 四模式渲染进自适应高度 iframe。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| understand 图谱 | ✅ 2026-11-11 | 仓内 `.understand-anything/knowledge-graph.json`：**160n/403e/10 层/12 步 tour**，双 validate 0/0，fingerprints 49@c2a14ff9（layers/tour 主会话自做） |
| onboarding | ✅ 2026-11-11 | `onboarding/ONBOARDING.md`（8 节 6544 字不计空格，101 锚） |
| explain 6 篇 | ✅ 2026-11-11 | `explain/01-06` 合计 **23421 字符**，318 锚（小仓口径，主会话抽验 4/4 命中） |

## 战况（5 批，主会话+单 worker 一夜收）

batch-2 超限按规范拆 2 part；同名 `apply_new_stat` 双回调合并为单节点（summary 注明第二重载）。

## 甄别精选（源码级实证）

1. **tests/README.md 引用路径是上游 monorepo 写法**：`requirements/main.txt`/`common-tests.txt`/`pytest inspector/tests` 本仓均不存在
2. `parse_agruments_helpers.py` 文件名拼写笔误（arguments 漏 u），全仓 import 沿用
3. **exec 注入用户代码链**：get_eval_function→catch_eval_exception——统计/过滤/排序/更新四回调共用，UI 工具的安全面边界
4. **decoration/common.py:44 双 href bug**：`href="…ansi_styles.css" href="…compare_styles.css"`——第二个 href 被 HTML 忽略，compare_styles.css 实际从未加载且文件不存在
5. `input_file` 死路径：被引用但 InspectorConfig 无此字段恒空
6. **iframe postMessage 跨语言协议**：update_height_js ↔ change_element_height.js / get_height_adjustment ↔ register_textarea.js；`postMessage(…, '*')` 目标源通配
7. get_compared_rows 注解 Dict 实为 set；table_layouts 按钮 style 重复 display 键；register_textarea.js onload/onresize 死代码；del_model 的 i+2 双偏移算术
8. 全局状态中枢 = utils/common.py 模块级可变单例（table_data/统计/标签/行状态）+ getter——回调间零 props 全靠它

## 分层速览（10 层，49 文件节点）

入口与打包(8) → 配置与常量(7) → 全局状态中枢(2) → 文本渲染线(5) → 前端资产(4) → 布局骨架(3) → 分析页布局(5) → 回调公共层(4) → 分析页回调群(9) → 测试(2)

*2026-11-11 · cuda-stack-第七轮会话（舰队夜战 · NeMo-Toolkit 三连之一）*

# 讲透 SkillSpector（NVIDIA/SkillSpector 全链知识库）

agent skill 安全检测器（Python，src-layout）：对 Claude/AI 生态的 SKILL.md 及捆绑产物做静态+行为+MCP+语义四线扫描，产出 SARIF 与检查账本。

| 环节 | 状态 | 产物与指标 |
|---|---|---|
| deepwiki | ✅ 2026-10-26 | TRUE_100（INDEX+全页+_coverage-check） |
| understand 图谱 | ✅ 2026-11-04 | 1497n/3170e/16 层/16 步 tour；双 validator 0/0；fingerprints 400 文件@2226747e；图谱在仓内 `.understand-anything/knowledge-graph.json` |
| onboarding | ✅ 2026-11-04 | ONBOARDING.md 8 节+勘误表（4394 汉字/17210 字符），49 锚终验全好 |
| explain | ✅ 2026-11-04 | 12 篇 57278 字符（不计空格），139 锚终验真坏 0（初报 15 坏全为 basename 语境歧义+IP 噪音，人工归位；2 缩写锚已修） |

## explain 索引（核心检测 6 + 外围 6）

01 cli 入口与参数面 / 02 graph 流程编排与状态 / 03 static_runner 与静态家族总装 / 04 行为检测线 / 05 MCP 三分析器 / 06 语义线与 llm_analyzer_base / 07 providers 基座与模型注册表 / 08 API 云端 provider 子包群 / 09 CLI 代理 provider 子包群 / 10 用户入口三件套 / 11 batch_scan 批量扫描子系统 / 12 测试巨阵与攻击 fixture 库

## 源码级勘误清单（11 条，全部行号锚实证）

1. **scanner 对 src-layout 全盲**（流水线实证）：tests/contrib 对 `skillspector.*` 的 import 全靠 AST 手扫（累计补边 ~500 条）；providers/__init__.py 工厂函数体内延迟 import 14 个子包 scanner 只记 2 条
2. DEVELOPMENT.md 三处坏链指向 nodes/llm_analyzer_base.py——实际在包根 src/skillspector/llm_analyzer_base.py
3. DEVELOPMENT.md "22 nodes" 陈旧计数——实测 27 分析器注册（SADD：静态 16+行为 4+MCP 3+语义 3+完整性 1）
4. 手写 bash 词法器在 static_patterns_tool_misuse.py:390/417/2352 而非 static_runner（_ShellToken/_ShellDelimiterFrame/_bounded_shell_tokens）
5. EVAL_DATASETS.md 声称跳过 evals/evals.json 但源码零实现；2.5.1 引用的 release.py 仓内不存在
6. providers 实测 13 分支非 14（nv_inference 是 try/except 可选导入且目录不存在的隐藏分支，__init__.py:163）
7. antigravity_cli 是注册但禁用的 fail-closed provider（:877-923，TTY-only 输出无法管道捕获）
8. nv_build registry 意大利语注释记录 202749 组合上限坑（:18-25）
9. test_pool_wiring.py 是模块级断言冒烟脚本非 pytest（零 test_ 函数）；mutation_max.py 是变异测试工具非 unittest 套件（tests-pro 连字符目录靠 sys.path 注入 :44-48）
10. 攻击 fixture 精巧样本：mcp_poisoned_tool 的 'reаd_data' 含西里尔同形字符 а（UTS #39）；malicious_skill SKILL.md 为"食谱加氰化物"提示注入+helper.py 凭据外传复合样本
11. deduplicate 是 report.py:1713 内部函数调用而非图节点；unicode_confusables.py 为生成的 UTS #39 数据表（1527 行 dict 字面量零函数）

## 流水线备注

- 2026-11-04 单日全链：前会话+本会话接力，两次 1308 五小时墙（11:36/14:31）三次 1302 瞬时限流全部 SendMessage 复活零损失
- 字数口径=不计空格总字符；explain 双组（核心线/外围线）各 6 篇

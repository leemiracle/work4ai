# 03 · systematic-debugging：四阶段纪律与四件技术兵器

## 角色定位

systematic-debugging 是仓内"纪律技能"的代表：铁律一行字——`NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST`（skills/systematic-debugging/SKILL.md:19），没完成 Phase 1 就不许提任何修复。它对抗的是编码代理最危险的反射：看到报错就"顺手修一下"。技能开头直言"随机修复浪费时间还制造新 bug，快补丁掩盖底层问题"（SKILL.md:10），并特别强调**越紧急越要用**——时间压力让瞎猜变得诱人，而系统化比乱试更快（SKILL.md:34-44）。

抗压设计是这个技能最厚的部分：12 条红旗（"快速修一下待会再查"/"多改几处一起跑测试"/"应该是 X，先改了再说"，SKILL.md:215-230）、人类伙伴口头信号解读表（"Stop guessing"="你在没理解就提修复"、"Ultrathink this"="质疑根本而不是症状"，SKILL.md:234-243）、合理化借口对照表（"紧急没时间走流程"→系统化比瞎试快，SKILL.md:245-256）三重冗余。收尾一句狠话："95% 的'查无根因'其实是调查不彻底"（SKILL.md:276）。

## 内部结构

**四阶段强制顺序**（SKILL.md:46-213）：

- **Phase 1 根因调查**：细读报错（栈迹逐行、行号/文件/错误码都记）→稳定复现（复现不了就继续收集证据，不许猜）→查最近变更（git diff/新依赖/配置）→多组件系统先加诊断埋点（对每个组件边界记录进出数据，跑一轮定位失效层，SKILL.md:72-108 给了 CI→构建→签名的四层示例）→深栈错误走 root-cause-tracing 回溯。
- **Phase 2 模式分析**：找同仓正常样本逐差异比对——"列出所有差异，再小也别假设'这不重要'"（SKILL.md:122-143）。
- **Phase 3 单一假设最小验证**：科学方法——一次只写下一个具体假设、做最小改动测它、不奏效就换新假设而非叠加修复（SKILL.md:145-168）。
- **Phase 4 实施与"3 次规则"**：先写失败测试（引用 test-driven-development 技能）→单一修复（禁止"顺手改进"）→验证；修复不奏效就数次数，**≥3 次失败=架构问题不是假设失败**，必须停下与人伙伴讨论"是否在靠惯性硬撑错误架构"（SKILL.md:192-213）。

**四件技术兵器**（SKILL.md:278-284 列为配套）：

1. **root-cause-tracing.md（169 行）**：从症状沿调用链逐级问"谁调用的"回溯到原始触发点再修源头（git init 错目录、文件写错位置这类深埋错误）；核心原则"在源头修，不在症状处修"（skills/systematic-debugging/root-cause-tracing.md:5-7）。
2. **defense-in-depth.md（122 行）**：根因修复后沿数据流每层加验证——因为"调用方错误"永远会发生，修复要能挡住下一个坏调用者。
3. **condition-based-waiting.md（115 行）+ 参考实现 .ts（158 行）**：用条件轮询替换任意 sleep——"等待你在乎的实际条件，而不是对耗时的猜测"（skills/systematic-debugging/condition-based-waiting.md:7）；唯一例外是真测时序行为（debounce/节流），且必须文档化原因（L30-32）。
4. **find-polluter.sh（63 行）**：测试污染定位脚本——线性逐个跑测试文件、每跑完检查污染文件是否出现（skills/systematic-debugging/find-polluter.sh:29-59），找到即报告并 exit 1（L57）。注意它是线性扫描而非 git bisect 式二分——对测试文件数不大的套件够用且实现直白。

**压测场景四份**：test-academic.md（学术问答）、test-pressure-1.md（生产事故每分钟损 1.5 万美元、经理吼"FIX IT NOW"、上周同症状加个 retry 2 分钟就修好——B 选项算下来"省 45 万美元"，skills/systematic-debugging/test-pressure-1.md:9-56）、test-pressure-2.md（与 condition-based-waiting 主题精确对位：sleep 乱枪=被禁反模式）、test-pressure-3.md（沉没成本+权威群体压力）。场景开头一律声明"这是真实场景，必须选择并行动，别问假设性问题"——逼代理在压力下做真决定。CREATION-LOG.md（119 行）记录技能从个人经验到仓内资产的演化史。

## 外部连接

上游：母技能的 Skill Priority 把"修 bug"路由到调试技能优先于领域技能（skills/using-superpowers/SKILL.md:105）。下游硬连接：Phase 4 第一步引用 superpowers:test-driven-development 写失败测试（SKILL.md:179），收尾引用 verification-before-completion 验证修复（SKILL.md:288）。测试连接：tests/skill-triggering/prompts/systematic-debugging.txt 夹具就是一段真实测试失败栈（parser.ts:42 TypeError）+一句"能查查怎么回事并修掉吗"，全程不点名技能，验隐式触发。姊妹技能 dispatching-parallel-agents 处理"多个不相关失败"的场景——各自独立根因时可并行派代理调查（skills/dispatching-parallel-agents/SKILL.md:12-14）。

## 数据流

一次纪律化调试的信息流：报错/异常行为 → Phase 1 证据收集（报错文本、复现步骤、git diff、组件边界埋点输出）→ Phase 2 差异清单（工作样本 vs 故障样本）→ Phase 3 假设卡片（"我认为根因是 X 因为 Y"，写下、最小验证、单一变量）→ Phase 4 失败测试（RED）→ 单点修复（GREEN）→ 全量回归 → 汇报（附验证输出，衔接 verification-before-completion 的"证据先于断言"）。若走 find-polluter.sh：污染检查路径 + 测试 glob 两个入参 → 逐文件 npm test → 命中输出污染详情与"如何深入调查"的命令建议。快速参考表把四阶段压缩成"关键活动+成功标准"两列（SKILL.md:258-265）；Real-World Impact 段给出量化对照：系统化 15-30 分钟/首修成功率 95%，乱试 2-3 小时/40%（SKILL.md:290-296）。

## 设计决策

- **红旗+借口表+口头信号三重冗余**：单靠规则挡不住压力下的合理化，每条红旗都配"Reality"反制句——这是 writing-skills 压测方法论（REFACTOR 阶段"每个新借口加显式反制"）的直接产物。
- **3 次规则写进流程而非注释**：SKILL.md:196 直接嵌在 Phase 4 步骤里（"If ≥ 3: STOP and question the architecture"），不是可选建议——把升级触发器制度化。
- **"环境性无根因"是合法出口但要留痕**：调查确属环境/时序/外部问题时，文档化调查过程+实施兜底处理+加监控（SKILL.md:267-274），但先自我怀疑 95%。
- **兵器独立成文件而非内联**：四件技术各自 100+ 行，按 writing-skills 的文件组织规则"Heavy reference (100+ lines) 独立文件、技能正文内联原则"拆分——SKILL.md 保持流程纪律，技术细节按需加载。
- **压测场景留在技能目录**：test-pressure 文件与技能同目录而非进 tests/，因为它们是技能的"测试用例"（RED 阶段的失败记录与回归资产），不是 CI 基础设施。

## 勘误与新人提示

勘误四条：(1) test-academic.md:3、test-pressure-1.md:5、test-pressure-2.md:5、test-pressure-3.md:5 仍写 `skills/debugging/systematic-debugging` 历史路径，技能实际位于 skills/systematic-debugging/SKILL.md——目录重组后压测文件未同步；(2) CREATION-LOG.md:25/57/107 引用的 skill-creation/SKILL.md、skills/meta/testing-skills-with-subagents、skills/debugging/... 均已不存在（现行位置是 skills/writing-skills/）；(3) find-polluter.sh 顶部自称 "Bisection script"（L2）但实现是线性逐测，注释与实现有措辞漂移；(4) test-pressure-2 的主题（condition-based-waiting）在 SKILL.md:284 有列，但 SKILL.md 未提及同目录的 .ts 参考实现文件名。

新人提示：遇到"改了三处还没修好"立即停——这条规则救过无数两小时黑洞；压测场景是理解技能设计意图的最佳入口，先读 test-pressure-1 再读红旗表会恍然大悟；condition-based-waiting 的 .ts 示例可直接抄进测试代码。

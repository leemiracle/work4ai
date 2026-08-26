# RESUME-0826 —— 讲透Prompt 完成档案（2026-08-26）

> 本单元**已完成**：13 章 + 11 实验（E1-E11 + E-mini）+ 12 组结果 json/png + 挂网 5 处。
> `RESUME-0825.md` 已归档（其"明日执行清单"全部执行完毕）。

## 一、今日完成清单（对 0825 清单逐条销账）

| 0825 计划 | 实际执行 | 偏差 |
|-----------|---------|------|
| ① E3 前台 timeout 1500s | **双通道改造**：api 前台 3min + local lite(6题64tok) 后台 setsid 20min + merge | 本地 CoT 单次实测 123s，全量 40min 会超时——用户指示跳过长跑，改造后无等待 |
| ② E4 SC | ✅ n=1/3/5/9，出**反例**：greedy 100% vs SC9 83%（系统性偏差 5:4 投错） | 比原设计更有价值 |
| ③ E5 PAL | ✅ 40% vs 40% 平手 + 失败分类学（错误搬家算术层→建模层）+ 沙箱三课 | 期间踩坑 3 次（白名单 __import__/剥 import 行/alarm），全写入 04 章 |
| ④ E6 ToT | ✅ 三臂：CoT 40% / ToT 0% / ToT无剪枝 0%（提议器是病灶） | 加了无剪枝诊断臂 |
| ⑤ E7 ReAct | ✅ 33%→67%（日期盲区必赢/简单题协议开销必输） | — |
| ⑥ E8 对抗 | ✅ 5/8 攻破、防御全 1/4、glm-5 真防御（复用 讲透Agent/讲透Prompt 深潜版分类学） | — |
| ⑦ E9 模型适配 | ✅ 4配置×3风格×双任务族；thinking 开关切换最优策略；咒语同号不同命 | 首版 iforder 裁判写错拼音序，修正重跑（教训入 08 章） |
| ⑧ E10 OPRO | ✅ 天花板效应 + 解析器也是 harness（5/8 轮解析失败）+ dspy 装通 + 手写 Bootstrap 等价 100% | — |
| ⑨ E11 数学 | ✅ zero-cot +87.5pp / few-cot 全稳 / Persona 过程≠对错 / Prover 三模板入 11 章 | — |
| ⑩ 00-12 章 | ✅ 13 章全写完（每章嵌实测数字+复现命令+练习） | 06 章补了 E-mini 实验（60%→73%） |
| ⑪ 挂网 | ✅ 本 README + 讲透Agent 主README 配套行 + 工程化手册总览互链 + exercises/EXERCISES.md + 记忆更新 + git 提交 | — |

## 二、五幕结构自查（宪法合规）

- 直觉→数学→代码→不足→应用：每章四幕以上，12 章批判收尾 ✅
- 每个知识点配实验：11 实验全部 bash 跑通、json+png 落盘 ✅
- arXiv 零凭记忆：25 篇 0825 核实 + 前沿 6 项 0825 检索，今日写作只引用已核实清单 ✅
- 诚实声明：n 小标注、裁判 bug 修正记录、记忆污染提示（E6/E11）、API 非确定性注记（E5 t1）✅

## 三、新铁律（写入项目记忆）

1. **本地 CPU CoT 单次 ~0.5s/token**：长文本生成实验先测单调用耗时，双通道拆分（api 前台/local lite 后台 setsid）
2. **API 重试风暴**：common.glm 默认 retries=3×180s ≈ 9min 会吃掉整个脚本——单发实验传 retries=1
3. **沙箱 exec 三课**：白名单 __import__ > 剥 import 行（别剥）；signal.alarm 必设
4. **裁判先于结论**：E9 iforder 拼音序裁判 bug 提醒——写判定函数后先抽查原始输出再信汇总数字
5. thinking 模型 max_tokens 给足（reasoning 吃预算，E8 空输出）

## 四、期权清单（按性价比，均未排期）

1. E10 解析器加固重跑（剥前缀/取块/重采样）——纯轨迹驱动 OPRO
2. E6 提议器定向化（"优先分数走法"）——prompt 移动搜索分布
3. E9 跨厂商矩阵（GPT/Claude/Gemini thinking）
4. E8 多轮渐进攻击 A12 + 防御位置效应
5. E4 错误相关性扫描——SC 适用性判据
6. exercises 11 题的参考答案（等读者做题）

## 五、文件清单（新增 28 个）

- 章节：`00-开场白.md` ~ `12-不足与展望.md`（13）
- 实验：`experiments/{e3_cot,e4_sc,e5_pal,e6_tot,e7_react,e8_injection,e9_adapt,e10_opro,e11_math,emini_chain}.py`（10 脚本，e3 重构三模式）
- 结果：`experiments/results/*.json + *.png`（12 组）
- 索引：`README.md` 重写、`exercises/EXERCISES.md`、本文件

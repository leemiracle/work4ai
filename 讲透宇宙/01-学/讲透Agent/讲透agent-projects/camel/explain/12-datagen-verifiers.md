# 12 数据生成与验证闭环：camel/datagen/ 与 camel/verifiers/

## 1. 角色定位

这对包构成 camel 的合成数据流水线：datagen 负责"造题+造解"（CoTDataGenerator/SelfImprovingCoTPipeline/SelfInstructPipeline 三条主管线，外加 evol_instruct 指令进化与 source2synth 子包），verifiers 负责"判卷"——MathVerifier（math_verify 符号比对）、PythonVerifier（沙箱跑代码比对输出）、PhysicsVerifier（带单位/符号比对）。二者构成 generator-verifier 回环：datagen 的 score/verify 步内嵌判卷逻辑。extractors 包（策略管道）是判卷前的答案抽取层，被 verifiers 与 environments 共用。camel/datagen/__init__.py 只导出三条主管线（:15-17），source2synth 与 evol_instruct 需子包路径访问。

## 2. 内部结构

**CoTDataGenerator（cot_datagen.py:64）**的类 docstring 宣称算法是"1. Monte Carlo Tree Search (MCTS)"（:71），但 `solve()`（:290）的真实结构是：直接解→错则进入 `for i in range(search_limit)` 迭代循环，每轮生成新解、算相似度分、保留最优、score>0.9 早停（:336-337）——**保最优的爬山法**，无节点扩展/回传/模拟；`binary_search_error`（:250）按句二分定位首个错误句；`solution_tree`（:139）只是 {question: {solution, error_position}} 结果字典，不是树。MCTS 属文档夸大（图谱钉版勘误）。

**SelfImprovingCoTPipeline（self_improving_cot.py:71，899 行）**是批量版：三个 prompt 模板 REASONING/EVALUATION/IMPROVEMENT_TEMPLATE 定义在**类体末尾**（:853/:864/:887）而非头部，方法内 `self.XXX` 靠运行时属性查找成立——按头部找常量会扑空。并发模型是"线程内伪异步"：`_batch_process_problems` 是 async def（:184）但内部用 ThreadPoolExecutor（:206）做同步并发，worker 线程里新建事件循环跑单任务（图谱钉版）。两个 AgentResponse 同名异义：cot_datagen.py:29 的（score: float 相似度）与 camel/datagen/self_instruct/self_instruct.py:440 的（answer: bool 分类判定）。

**evol_instruct 子包**：templates.py 定义 BaseEvolInstructTemplates（:22）+ EvolInstructTemplates（:47）+ MathEvolInstructTemplates（:207）两层；EvolInstructPipeline（camel/datagen/evol_instruct/evol_instruct.py:31）驱动指令进化。**幽灵导出勘误**：`__init__.py` 的 `__all__` 声明了 'MathEvolInstructTemplates'（camel/datagen/evol_instruct/__init__.py:19）但文件内只 import 了 EvolInstructPipeline（:15）——直接 `from camel.datagen.evol_instruct import MathEvolInstructTemplates` 会 ImportError，必须走 `...evol_instruct.templates` 子模块。

**verifiers 三件套**：BaseVerifier（camel/verifiers/base.py:28）契约含 setup（:90）/cleanup（:132）/verify（:165，抽象）/verify_batch（:307），结果模型在 camel/verifiers/models.py（VerificationOutcome 枚举 :21、VerificationResult :34、VerifierConfig :57）。MathVerifier（math_verifier.py:25）延迟 import math_verify 库（:110）做符号级等价判定；PythonVerifier（python_verifier.py:34）用 subprocess.run（:113/:146/:177）真跑代码比对 stdout；PhysicsVerifier（physics_verifier.py:784）**继承 PythonVerifier 而非 BaseVerifier**（校验链 Physics→Python→Base），单元解析（UnitParser :30）与解比对（PhysicsSolutionComparator :300）全靠组合。包内两种避环风格并存：math/python 走 `from camel.verifiers import BaseVerifier` 回指 barrel（math:19/python:27），physics 用相对导入 `from .python_verifier import`（:25）。

**extractors 的容器/策略双层**（extractors/base.py）：BaseExtractorStrategy（:26）是策略接口（抽象 extract :29-30）；BaseExtractor（:42）是容器，构造参数 `pipeline: List[List[BaseExtractorStrategy]]`（:57）——固定多阶段管道，阶段内按序尝试、阶段间串接。**勘误**：environments 侧的 ActionExtractor/MoveExtractor 继承的是策略接口 BaseExtractorStrategy 而非容器 BaseExtractor（tree-sitter callGraph 曾误记为继承关系）；BaseExtractor 本身也不继承 Strategy，二者是组合关系。

## 3. 外部连接

- **ChatAgent**：datagen 各管线的 generator/evaluator 全是 ChatAgent 实例；self_improving_cot 消费 camel.utils 的 BatchProcessor/retry_on_error。
- **source2synth ↔ agents 包级循环**：multi_hop_generator_agent.py 反向依赖 datagen.source2synth，同包另两文件又依赖 agents——文件级 DAG、包级互依赖（batch-24 钉版）；其 use_ai_model=False 路径恒产出空 QA 对（规则兜底半成品）。
- **environments**：RLCardsEnv 等的动作抽取消费 extractors 策略（见上勘误）；SingleStepEnv 经 structural typing 满足 Environment Protocol。
- **外部判卷库**：math_verify、sympy（PhysicsVerifier 八处延迟 import）都是可选依赖，import camel.verifiers 不触发安装检查。
- **reward 阈值口径三角**（batch-17 勘误）：RewardModelFilter 默认 0.5、registry 'reward' 项 0.7、SelfImprovingCoTPipeline 0.7——三处不一致，且 Nemotron 返回 logprobs（通常≤0）与阈值直接比较语义存疑。

## 4. 数据流

以 CoTDataGenerator 为例：`generate(solution_path)` 遍历题库 → 每题 `solve()`：get_answer 生成候选 → evaluate_partial_solution 打相似度分（LLM-as-judge）→ 爬山迭代+早停 → 不完美解走 binary_search_error 定位首错句 → 依据正确前缀重生成 → 结果累积进 solution_tree → 终局 dump 成 JSON（:435）。SelfImprovingCoT 批量版按 problem 切线程池并行，每题走 reasoning→evaluation→improvement 三模板循环。verifier 侧单次 verify：extractors 抽答案（剥离 markdown/单位/格式）→ MathVerifier 符号等价或 PythonVerifier 执行比对 → VerificationResult 回传调用方决定去留。

## 5. 设计决策

1. **判卷器继承执行器（Physics→Python）**：物理答案验证需要"先跑代码拿到数值与单位，再符号比对"两段，继承 PythonVerifier 复用沙箱执行段最直接——代价是 PhysicsVerifier 无法脱离代码执行语境独立使用。
2. **策略模式的严格双层**：策略只管"文本→答案字符串"，容器管阶段编排/缓存/超时/资源监控（构造参数 :57-62）——新增抽取方式零侵入；但 pipeline 构造期固定，运行期不能增删策略。
3. **爬山而非真 MCTS**：docstring 的 MCTS 与实现的爬山落差是"论文级叙事、工程级简化"的取舍——有 score 早停兜底，但按 MCTS 预期读代码会迷路。
4. **幽灵导出保留不修**：`__all__` 多列一个名字是低危 bug，上游不修大概是避免破坏 from x import * 的行为面——消费方以"子模块全路径"为正确姿势。
5. **async 外壳+线程池内核**：SelfImprovingCoT 保持 async API 面向未来，实际并行度全在线程池——await 它不会获得事件循环并发收益，别被签名误导做容量估算。

## 6. 新人提示

- **import 路径三坑**：`MathEvolInstructTemplates` 走 `camel.datagen.evol_instruct.templates`（幽灵导出）；source2synth 走子包全路径；两个 AgentResponse 同名不同义，grep 时先看 import 来源文件。
- **找模板常量去类体末尾**：self_improving_cot.py:853/864/887——IDE 大纲跳转可能直接定位到，但手工 sed 类头会以为常量丢了。
- **verifiers 包导入顺序敏感**：barrel 环依赖 `from .base import` 先执行；给 barrel 加新成员放在 base 之后，或学 physics 用相对导入。
- **复现实验必须显式传 seed**：ProcessorConfig.seed 默认 random.randint（batch-24 勘误）；reward 阈值三处口径不一，对齐时三个文件一起改。
- **PythonVerifier 是真执行**：subprocess 直跑被验代码（:113），喂不受信生成代码前确认运行环境隔离需求——它是"验证器"不是"沙箱"（沙箱谱系见 interpreters 篇）。
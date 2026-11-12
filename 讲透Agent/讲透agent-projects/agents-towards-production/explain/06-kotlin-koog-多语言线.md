# 06 | kotlin-agent-with-koog——JVM 生态的 agent 三步进阶线

## ① 角色定位

`tutorials/kotlin-agent-with-koog/` 对应图谱 L1 导览与 L9"构建与引导脚本"（run.sh 三函数+gradlew.bat 两函数）。它是仓内唯一非 Python 生态教程（tour step-11），教学目标是映射论证：**同一套 agent 模式（LLM 调用→工具注册→结构化输出）在 Kotlin 原生栈如何落地**。JetBrains 赞助位（根 README.md:149），Koog 即其开源 agent 框架。

## ② 内部结构

八件资产三组：
- **导览**：README.md 给 25-30 分钟定位（README.md:48）与三种跑法（run.sh 交互 / gradlew stepN 直跑 / 读 tutorial.md）；tutorial.md 497 行是正文——前置环境（tutorial.md:41-50）、build 文件逐段讲（tutorial.md:76-142）、三步各一章（Step1 tutorial.md:160 起 / Step2 tutorial.md:230 起 / Step3 tutorial.md:364 起），Python 对照注释贯穿全文（suspend≈async def、use≈with、?:≈or，tutorial.md:170-172）。
- **构建件**：build.gradle.kts——Kotlin 插件 2.1.0（build.gradle.kts:2-3）、`ai.koog:koog-agents:0.6.2`（build.gradle.kts:12）、coroutines 1.10.1（build.gradle.kts:15）、serialization-json 1.8.0（build.gradle.kts:18）、slf4j-nop 静音日志（build.gradle.kts:21）；三个 JavaExec 任务 step1/2/3（build.gradle.kts:29-48）；`sourceSets setSrcDirs(".")` 让 .kt 平铺教程根（build.gradle.kts:51-57）；`jvmToolchain(17)`（build.gradle.kts:60）。
- **三步源码**（平铺根目录）：`Step1_HelloAgent.kt` 36 行——`suspend fun main()`（Step1_HelloAgent.kt:8）、Elvis 取 key（Step1_HelloAgent.kt:13-14）、`simpleOpenAIExecutor(apiKey).use`（Step1_HelloAgent.kt:19）、三参 AIAgent（Step1_HelloAgent.kt:25-29）与 `agent.run`（Step1_HelloAgent.kt:32）。`Step2_AgentWithTools.kt` 122 行——`AssistantTools : ToolSet` 注解式工具类（Step2_AgentWithTools.kt:21-22）：@Tool getWeather（Step2_AgentWithTools.kt:24-36）、calculate（Step2_AgentWithTools.kt:38-43）、lookupFact（Step2_AgentWithTools.kt:45-54）、私有递归四则求值器（Step2_AgentWithTools.kt:57-78）；`ToolRegistry { tools(AssistantTools().asTools()) }`（Step2_AgentWithTools.kt:91-93）传入 AIAgent（Step2_AgentWithTools.kt:105）；一道三工具合问（Step2_AgentWithTools.kt:109-110）逼出 ReAct 循环。`Step3_StructuredOutput.kt` 102 行——@Serializable @SerialName("CityAnalysis") 数据类六字段全 @property:LLMDescription（Step3_StructuredOutput.kt:27-48）；自定义策略图 `strategy<String, CityAnalysis>`：preparePrompt 节点 + `nodeLLMRequestStructured<CityAnalysis>()`（Step3_StructuredOutput.kt:64-67）+ `then/forwardTo` 连线（Step3_StructuredOutput.kt:70-71）；AIAgentConfig 换 GPT4o 且 maxAgentIterations=5（Step3_StructuredOutput.kt:74-80）；`agent.run` 直接返回类型化对象（Step3_StructuredOutput.kt:91）。
- **引导件**：run.sh 135 行——`check_java` 解析 `java -version` 主版本号并 `-ge 17` 硬校验（run.sh:30-31），失败给五平台安装指引后 exit 1（run.sh:44-50）；`check_api_key` 掩码显示首 8 尾 4（run.sh:59）、缺失时交互式 read+export 会话级注入（run.sh:64-67）；`run_step` 回车执行/s 跳过（run.sh:85-89）、`./gradlew "$step" --quiet`（run.sh:92）、失败给修复提示返回 1（run.sh:94-97）；主流程三步连跑（run.sh:114-124）收尾指路 tutorial.md（run.sh:132）。gradlew.bat 94 行是 Windows wrapper，`::findJavaFromJavaHome`（gradlew.bat:56）与 `::execute`（gradlew.bat:70）为图谱仅有的 bat 函数节点。

## ③ 外部连接

外部依赖三个坐标：ai.koog:koog-agents（Step*.kt 全部 import ai.koog.*，如 Step1_HelloAgent.kt:1-3）、kotlinx-coroutines（suspend 运行时）、kotlinx-serialization（Step3 的 @Serializable 链）。运行期外部服务仅 OpenAI API（OPENAI_API_KEY，三步同检 Step2_AgentWithTools.kt:86-87）。仓内连接：README documents tutorial.md 与 run.sh（图谱边）；tutorial.md 引 assets/ 八张截图（architecture-diagram 等）；run.sh:92 反向调 gradlew step 任务，Gradle 再编根目录 .kt——引导件与源码的闭环。

## ④ 数据流

输入：OPENAI_API_KEY 环境变量 + 各步内嵌的问题字符串。Step1 数据流最短：prompt→executor→GPT4oMini→文本响应→println（Step1_HelloAgent.kt:32-33）。Step2 加工具环：LLM 收到工具 schema（由 @Tool+@LLMDescription 反射生成，Step2_AgentWithTools.kt:91-93 注册）→模型决定调用→框架反射执行 Kotlin 函数→结果回喂→模型合成终答（Step2_AgentWithTools.kt:113-118 注释四拍即 ReAct）。Step3 换输出契约：数据类经 serialization 生成 JSON schema→LLM 按 schema 产出 JSON→Koog 反序列化为 CityAnalysis 对象→字段级直接访问（Step3_StructuredOutput.kt:94-99），全程应用代码零字符串解析（tutorial.md:496 点题"framework handles the entire serialization round-trip"）。构建数据流：run.sh→gradlew stepN→JavaExec mainClass StepNKt（build.gradle.kts:32）→编译根目录源码执行。

## ⑤ 设计决策与陷阱

- **决策：平铺结构反惯例**。sourceSets 指到 "."（build.gradle.kts:51-57）放弃 src/main/kotlin——教程免导航（tutorial.md:72-74），代价是 JavaExec 任务须手写 mainClass（build.gradle.kts:29-48）。
- **决策：三步各换一个模型层**。Step1/2 用 GPT4oMini、Step3 升 GPT4o（Step3_StructuredOutput.kt:78）——结构化输出对模型能力更敏感。
- **决策：硬编码假数据工具**（Step2_AgentWithTools.kt:29-35 天气词典）与 runpod 线 fake_research 同哲学：无额外 key 也可跑通。
- **陷阱 1：JDK 17 是硬门槛**。run.sh:31 与 build.gradle.kts:60 双处校验；check_java 解析失败会走 else 分支误报版本低，换正规 JDK 即可。
- **陷阱 2：API key 会话级注入不持久**。run.sh:66 export 只活在脚本进程，直接 `./gradlew step1` 前须自行 export，否则 Step1_HelloAgent.kt:14 error() 抛"Set the OPENAI_API_KEY..."。
- **陷阱 3：evaluateExpression 是教学玩具**。Step2_AgentWithTools.kt:57-78 的递归求值器不处理优先级（最后索引分裂 +/-、最先分裂 *÷ 但递归顺序混合），`(1+2)*3` 外的复杂式会算错，别当 calculator 用。
- **陷阱 4：@property: 前缀是 Kotlin 注解目标语法**。Step3_StructuredOutput.kt:31 数据类构造参数上的 LLMDescription 必须写 `@property:`（Step3_StructuredOutput.kt:23-24 注释自称"a Kotlin quirk"），漏写则 schema 描述丢失。
- **决策：slf4j-nop 静音**（build.gradle.kts:21）——保证终端输出只有教学关心的 agent 对话。

## ⑥ 新人提示

Python 背景读者先读 tutorial.md:168-172 的三行对照表再进代码，suspend/use/Elvis 扫清后源码几乎无障碍。跑法首推 `./run.sh`（README.md:22）：环境检查、key 掩码、三步执行一次串完。产出检验：给 Step2 加第四个 @Tool 工具（如汇率换算）、给 Step3 的 CityAnalysis 加两字段，分别验证 ToolRegistry 反射与 schema 序列化链。深挖 Koog（策略图 DSL、多 agent 图编排）从本教程的 strategy 语法（Step3_StructuredOutput.kt:64-72）起步即可。

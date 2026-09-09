# 架构 · 内容深度摘要

> 基于 136 篇高价值全文的实体抽取 / 关键短语 / 自动摘要 / 子主题发现

## 1. 技术实体图谱（按分类）

**架构模式**：微服务(908) · 云原生(238) · Sidecar(90) · 低代码(77) · Serverless(75) · Service Mesh(64) · 事件驱动(59) · CQRS(36) · Saga(22) · DDD(16)

**编程语言**：Java(842) · Go(266) · JavaScript(94) · Python(68) · Ruby(67) · Rust(60) · Dart(48) · C++(39) · Golang(23) · TypeScript(21)

**公司/组织**：腾讯(114) · 阿里(112) · 字节跳动(67) · 百度(52) · Netflix(52) · 微软(52) · 蚂蚁(46) · 华为(39) · Apple(35) · Google(32)

**云原生**：Kubernetes(138) · Serverless(75) · Istio(69) · Docker(68) · CNCF(39) · Service Mesh(32) · Prometheus(31) · OpenTelemetry(29) · Grafana(25) · K8s(9)

**大模型**：Agent(138) · GPT(97) · ChatGPT(88) · o1(78) · 文心一言(27) · Claude(9) · GPT-4(5) · RAG(3) · DeepSeek(3) · GLM(2)

**方法论**：DevOps(91) · 可观测性(71) · 敏捷(54) · FinOps(30) · CI/CD(27) · GitOps(21) · SRE(6) · BDD(4) · TDD(3) · Scrum(3)

**前端框架**：Flutter(80) · React(76) · React Native(28) · Angular(27) · Vue(25) · Lit(6) · Svelte(3) · Next.js(3) · Redux(2) · Electron(1)

**消息/流**：Kafka(170) · Spark(48) · RabbitMQ(9) · Pulsar(6) · Flink(5) · RocketMQ(3) · Iceberg(3) · Storm(2) · Hudi(1) · Samza(1)

**数据库**：Redis(76) · ClickHouse(51) · MySQL(44) · Elasticsearch(35) · MongoDB(10) · HBase(7) · PolarDB(6) · Snowflake(5) · TiDB(5) · Doris(3)

**后端框架**：Spring(111) · gRPC(51) · Spring Boot(30) · Rails(12) · Spring Cloud(10) · Django(9) ·  thrift(5) · Express(4) · Flask(3) · Gin(2)

**云平台**：阿里云(49) · AWS(46) · 腾讯云(36) · Azure(34) · 火山引擎(31) · 百度智能云(14) · GCP(10) · Cloudflare(7) · Vercel(4) · 华为云(3)

**大数据**：Spark(48) · DataX(14) · Hadoop(11) · Hive(6) · Presto(5) · Flink(5) · Airflow(4) · Doris(3) · Ray(2) · DolphinScheduler(1)

**AI/ML框架**：TensorFlow(5) · JAX(4) · LangChain(3) · PyTorch(2) · Keras(1)

## 2. 核心关键短语 Top 25

| 短语 | 权重 |
|------|------|
| core | 3570.0 |
| js | 2052.0 |
| Kitex | 450.0 |
| codec | 264.0 |
| Kaggle | 256.0 |
| Grady | 240.0 |
| Thrift | 220.0 |
| Code | 198.0 |
| dialog | 192.0 |
| Serverless | 155.0 |
| JEP | 153.0 |
| Core | 144.0 |
| TuGraph | 133.0 |
| API 网 | 132.5 |
| Landy 嗯 | 126.0 |
| MCP | 113.0 |
| Terhorst | 108.0 |
| Harmel | 108.0 |
| UCI | 81.0 |
| Kamaruzzaman | 81.0 |
| FaaS 服务 | 78.0 |
| JDK | 75.0 |
| Java | 75.0 |
| JuiceFS | 73.0 |
| dubbo | 72.0 |

## 3. 发现的子主题

- **core**（权重 3570.0，约 1 篇提及）
- **js**（权重 2052.0，约 1 篇提及）
- **Kitex**（权重 450.0，约 5 篇提及）
- **codec**（权重 264.0，约 1 篇提及）
- **Kaggle**（权重 256.0，约 1 篇提及）
- **Grady**（权重 240.0，约 1 篇提及）
- **Thrift**（权重 220.0，约 1 篇提及）
- **Code**（权重 198.0，约 1 篇提及）
- **dialog**（权重 192.0，约 1 篇提及）
- **Serverless**（权重 155.0，约 2 篇提及）
- **JEP**（权重 153.0，约 1 篇提及）
- **Core**（权重 144.0，约 1 篇提及）

## 4. 概念演化（年度热门实体）

- **1970**：微服务(688) · Java(670) · Go(237) · Kafka(169) · 云原生(138) · Agent(136)
- **2021**：Flutter(48) · Java(10) · C++(3) · 美团(3) · 华为(3) · Dart(2)
- **2023**：Java(154) · 微服务(103) · 云原生(65) · Ruby(58) · Kubernetes(56) · Spark(56)
- **2024**：微服务(117) · 云原生(35) · Serverless(10) · Go(10) · 字节跳动(10) · Java(8)

## 5. 代表性文章·自动摘要

### 让 Flutter 在鸿蒙系统上跑起来
*2021 · 阅读 658,147*

> 在 Flutter 的架构设计中，最上层为框架层，使用 Dart 语言开发，面向 Flutter 业务的开发者；中间层为引擎层，使用 C/C++ 开发，实现了 Flutter 的渲染管线和 Dart 运行时等基础能力；最下层为嵌入层，负责与平台相关的能力实现。
> Flutter 框架注册 VSync 回调之后，通过 C++ 侧的 VsyncWaiter 类等待 VSync 信号，后者通过 JNI 等一系列调用，最终 Java 侧的 VsyncWaiter 类调用 Android SDK 的 Choreographer.postFrameCallback 方法，再通过 JNI 一层层传回 Flutter 引擎消费掉此回调。

### 简单聊聊配合dialog使用popover的问题
*2023 · 阅读 378,994*

> 在视频中，popover关闭方法并不会影响它与<div role="dialog">的交互。
> 考虑到目前 <dialog>的支持效果仍然比popover更好，所以在新项目中继续用 <dialog>应该也没啥问题。

### 可观测性也“卷”起来了！过去十年，我们在阿里云如何建设可观测体系？ | 卓越技术团队访谈录
*2023 · 阅读 361,993*

> EagleEye 的第一个重要发展契机是淘宝的双十一大促，这是 EagleEye 的首次大规模应用。
> 过去，EagleEye 在阿里内部积累了大量运维场景经验，脱胎于 EagleEye，ARMS 也积累了丰富的行业应用与运维经验。

### 首届运维数智化转型论坛：深化XOps运作，加速运维数智化转型
*2023 · 阅读 298,902*

> 过去三年，在信通院组织下，华为与运营商、业界企业广泛探讨、深度协同，联合支撑了 XOps 标准的建立与完善，同时华为以 XOps 标准为指引，帮助客户持续提升运维数智化水平，支撑客户参与信通院标准评估，共同构筑了产业影响力。
> 在主题演讲环节，信通院云大所审计与治理部业务主管刘昭炜先生、尚梦宸先生详细介绍了XOps标准体系，从 DevOps、BizDevOps、AIOps 及 FinOps 四大维度揭示了 XOps 对推进组织数智化转型的意义和作用，呼吁产业界各方持续加快参与行业标准制定，共同促进 XOps 产业生态持续健康发展。

### 最新议题出炉！2023 可信数据库发展大会：近百位行业大咖将出席演讲
*2023 · 阅读 251,757*

> 为进一步深入贯彻党的二十大关于“实现高水平科技自立自强，进入创新型国家前列”总体部署，落实《国家标准化发展纲要》《“十四五”数字经济发展规划》《“十四五”国家信息化规划》《“十四五”软件和信息技术服务业发展规划》《“十四五”大数据产业发展规划》等政策要求。
> 本届大会以“自主 创新 引领”为主题，共设置9个论坛，除7月4日主论坛外，7月5日分设金融行业、电信行业、互联网行业、汽车行业、云原生与开源数据库、搜索与分析型数据库、数据库运维及生态工具、时序时空及图数据库8个分论坛。

### Nature总结六大ChatGPT编程技巧：是非常强大的编程辅助工具！
*2023 · 阅读 220,355*

> 如今的ChatGPT已经火爆全网、席卷全球，这款由OpenAI打造的AI聊天机器人具备与人类几乎无异的顺畅语言表达能力。
> 例如，ChatGPT当中的“温度”选项其实就是创造力控制旋钮——温度设定得越高，AI就越是脑洞大开。

### 让文物“活”起来：揭秘火山引擎视频云三维重建技术
*2023 · 阅读 191,054*

> 为此，采用符号距离场（Signed Distance Fields，简称SDF）的技术方案来表示三维物体，结合深度学习的方法克服了以上重建难点。
> SDF 表示了空间中每个点到物体的有向距离，是一种隐式表示，二维 SDF 的示意图如下。

### 趣丸科技媒体算法负责人马金龙确认出席 ArchSummit 深圳
*2023 · 阅读 178,483*

> 马金龙拥有 9 年媒体算法开发经验，涉及音视频图像文本，负责过音频前后端处理，弱网优化，音视频质量提升，智能内容安全审核“T 网”，内容理解“T 悟”等大型项目。
> 除上述专题外 ，ArchSummit 深圳还将围绕基础架构技术、智能化数据治理、DataOps、Data Fabric 等高效数据开发与服务模式、Mesh 技术实践案例、QUIC 传输和架构优化等进行分享。

---
*由 InfoQ Atlas 内容情报层生成*

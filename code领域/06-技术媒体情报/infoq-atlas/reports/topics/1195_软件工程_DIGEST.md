# 软件工程 · 内容深度摘要

> 基于 33 篇高价值全文的实体抽取 / 关键短语 / 自动摘要 / 子主题发现

## 1. 技术实体图谱（按分类）

**编程语言**：Java(132) · Go(25) · Python(8) · Kotlin(3) · Rust(2) · JavaScript(2) · Ruby(2) · Scala(2) · C#(2) · Golang(1)

**公司/组织**：腾讯(68) · Google(18) · 微软(15) · 阿里(12) · Anthropic(12) · Intel(7) · 京东(5) · 阿里巴巴(5) · OpenAI(5) · 百度(3)

**方法论**：DevOps(77) · 敏捷(42) · CI/CD(13) · 可观测性(10) · Scrum(3) · SRE(3) · GitOps(2) · FinOps(1) · Chaos Engineering(1) · Observability(1)

**大模型**：Agent(113) · Claude(16) · GPT(14) · RAG(4) · ChatGPT(3) · GPT-4(1)

**云原生**：Prometheus(26) · Kubernetes(13) · Grafana(12) · Flux(4) · OpenTelemetry(4) · Docker(3) · K8s(1) · Serverless(1) · CNCF(1)

**后端框架**：Spring(40) · Spring Cloud(13) · Spring Boot(4) · gRPC(3) · Django(1) · Rails(1)

**架构模式**：微服务(30) · 云原生(8) · Sidecar(8) · SOA(1) · Serverless(1) · 中台(1)

**数据库**：Redis(3) · SQLite(3) · PostgreSQL(3) · Elasticsearch(2) · MongoDB(2) · MySQL(1) · DuckDB(1)

**前端框架**：React(6) · Lit(3) · Vue(2) · Angular(1) · Next.js(1)

**云平台**：腾讯云(4) · AWS(3) · 华为云(2) · Oracle Cloud(1)

**消息/流**：Spark(3) · Kafka(2)

**大数据**：Spark(3) · Hadoop(1)

**AI/ML框架**：vLLM(1)

## 2. 核心关键短语 Top 25

| 短语 | 权重 |
|------|------|
| launch.json 件 | 192.0 |
| JEP | 184.0 |
| AI 代 | 115.5 |
| AI 领域 | 95.0 |
| AI 驱动攻击 | 83.0 |
| AI 驱动系统 | 83.0 |
| AI 驱动世界 | 83.0 |
| Code | 78.0 |
| 执 probe handler | 61.67 |
| JDK | 60.0 |
| 旦 AI 介入 | 57.0 |
| DevOps 出 | 55.0 |
| BPF ringbuffer | 51.0 |
| Prometheus | 50.0 |
| 下 PromSql 表达式 | 50.0 |
| 触 probe handler 执 | 49.0 |
| tracepoint | 47.0 |
| 就 eBPF | 46.5 |
| 依赖 perf event | 46.33 |
| perf event 系统调 | 46.33 |
| 就 kprobe probe handler 力 | 43.6 |
| 执 post handler | 40.0 |
| Agent | 39.0 |
| ftrace perf | 37.0 |
| 函数 probe handler 力 | 37.0 |

## 3. 发现的子主题

- **launch.json 件**（权重 192.0，约 1 篇提及）
- **JEP**（权重 184.0，约 1 篇提及）
- **AI 代**（权重 115.5，约 2 篇提及）
- **AI 领域**（权重 95.0，约 1 篇提及）
- **AI 驱动攻击**（权重 83.0，约 1 篇提及）
- **AI 驱动系统**（权重 83.0，约 1 篇提及）
- **AI 驱动世界**（权重 83.0，约 1 篇提及）
- **Code**（权重 78.0，约 1 篇提及）
- **执 probe handler**（权重 61.67，约 1 篇提及）
- **JDK**（权重 60.0，约 2 篇提及）
- **旦 AI 介入**（权重 57.0，约 0 篇提及）
- **DevOps 出**（权重 55.0，约 1 篇提及）

## 4. 概念演化（年度热门实体）

- **1970**：Java(132) · Agent(113) · DevOps(77) · 腾讯(68) · 敏捷(42) · Spring(40)

## 5. 代表性文章·自动摘要

### 什么是Token？为什么大模型要计算Token数
*1970 · 阅读 34,908*

> 输入给 GPT 模型的 token 数和 GPT 模型生成文本的 token 数。
> 例如，你提问耗费了 100 token，GPT 根据你的输入，生成文本（也就是回答）了 200 token，那么一共消费的 token 数就是 300 。

### VS Code 的 launch.json 进行高效代码调试：配置和原理解析
*1970 · 阅读 24,193*

> 在 Visual Studio Code (VS Code) 中，launch.json 是一个用于配置调试会话的重要文件。
> 配置 launch.json： 首先，需要在项目根目录下创建或编辑 launch.json 文件。

### Java迎来增强功能字符串模板，代码简化，安全性提升
*1970 · 阅读 22,393*

> 这一新特性的目的是简化Java程序的编写，提高文本和表达式混合代码的可读性，增强Java程序从用户提供的值组成字符串时的安全性。
> Java 近期新闻：Java 28 岁、Payara、Micronaut 4.0-M5、Spring 更新

### B 站轻量级容灾演练体系构建与业务实践
*1970 · 阅读 21,745*

> 为了解决这一问题，ChaoBlade 作为一个封装工具，简化了注入参数，主要包括影响 IP、豁免 IP、本地端口和远程端口等。
> 在跨可用区（AZ）的断网容灾演练中，服务级别的测试通常需要遵循以下步骤：首先，流量需要切换到其他路径；其次，模拟在某个可用区的专线断网故障；最后，验证各项服务功能是否仍然正常。

### 万字长文解读Linux 内核追踪机制
*1970 · 阅读 21,523*

> perf 采样拿到的event 最终会被放到一个叫做perf event的数据结构里面，因为event都是在内核态产生的，采样时需要一个数据结构存储采集到的event，并在采样结束后，将采集到的event从内核态发送到用户态来使用，perf event就是用来做这个事情的，我们通常说的perf 是指用户态的工具，perf event是内核态的数据结构。
> 在使用perf record 子命令采集数据时，会通过perf_event_open 创建perf event，perf event 在初始化阶段扫描所有的trace event,检查是否存在与perf event 关联的 uprobe_event，找到对应的uprobe  event 事件后，就可以启用urpobe event了。

### 研发效能度量核心方法与实践：难点和反模式
*1970 · 阅读 21,121*

> 张乐，DevOps与研发效能资深实践者，长期工作于拥有数万研发的互联网大厂（百度、京东等），主攻敏捷与DevOps实践、DevOps平台建设、研发效能度量体系设计等方向，历任资深敏捷教练、DevOps平台产品总监、研发效能度量标准化联盟负责人等岗位。
> EXIN DevOps全系列国际认证授权讲师、凤凰项目DevOps沙盘国际授权教练。

### 从维护性工作到软件开发革命，运维15年间的大逆转
*1970 · 阅读 21,049*

> 在国内，最早拥抱 DevOps 的是互联网企业，特别是头部的互联网企业将 DevOps 的思想和理念固化为对外的商业化 DevOps 产品和服务，能利用它有效屏蔽 DevOps 实施过程中底层的复杂度。
> 容器和微服务技术加速了 DevOps 的落地，像腾讯这样的企业在两三年前也在内部大规模实践，将研发流程和使用的工具都进行了统一和收敛，构建仓库、CI/CD 流水线等都用 DevOps 来实现。

### 谷歌工作十年，我总结了这些工程师必备软技能
*1970 · 阅读 21,048*

> 这包括：数据结构（数组、对象、模块、哈希）、算法（搜索、排序）、架构（设计模式、状态管理）甚至性能优化（例如缓存、延迟加载等）。
> 这可能包括：你使用的语言（JavaScript、Python、Ruby 等）、你使用的框架（如 React、Angular、Vue 等）、你使用的后端（如 Django、Rails 等）以及技术你使用的堆栈（例如 Google App Engine、Google Cloud Platform 等）。

---
*由 InfoQ Atlas 内容情报层生成*

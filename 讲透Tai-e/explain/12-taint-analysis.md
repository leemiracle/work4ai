<!-- source: knowledge-graph tour step 12 | files: src/main/java/pascal/taie/analysis/pta/plugin/taint/TaintAnalysis.java, src/main/java/pascal/taie/analysis/pta/plugin/taint/SourceHandler.java, src/main/java/pascal/taie/analysis/pta/plugin/taint/YamlTaintConfigProvider.java -->
# 12 · 污点分析与规则库：TaintAnalysis、三 handler 与 96 个 YAML 规则文件

### 角色定位

污点分析是 pta 之上最重要的 client（图谱 L10 层）：指针分析回答"谁指向谁"，它回答"不可信输入能否流到危险操作"，是注入/XSS/路径穿越类检测的出口。它不是独立 `ProgramAnalysis` 而是 pta 插件：PointerAnalysis.java:159-161，`taint-config` 或 `taint-config-providers` 非空即挂 `new TaintAnalysis()`。

### 内部结构

**装配**：TaintAnalysis.java:87 `extends CompositePlugin`。`initialize()`（115-192）：清场（117-128）→ YAML 加载（131-138）→ Android 模式 mergeWith `ANDROID_DEFAULT`（唯一内容 `callSiteMode=true`，TaintConfig.java:47-48）→ 程序化 provider（143-164）→ addPlugin 三 handler（166-170）→ **对已发现方法重放回调**（171-191）。

**三在线 handler + 一离线 handler**：

- **SourceHandler**（OnFlyHandler）：onNewCallEdge 驱动（SourceHandler.java:108-119），`makeTaint` 造污点对象并注入返回值/base/参数（124-142），ARRAY/FIELD/param/field 型各有专门触发点（135-159,202-239）。
- **TransferHandler**（OnFlyHandler）：`processTransfer`（TransferHandler.java:115-170）给 base/参数/返回值间转移加带自定义 transfer 函数的 `TaintTransferEdge` PFG 边（129-132），函数体做"换型重铸"：旧 taint → 取 sourcePoint → `makeTaint(source, 新type)`（213-226），解决 String→StringBuilder 换型；污点转入 base/参数时生成人造 `StoreField` 语句反向传播（234-270）。
- **SanitizerHandler**（OnFlyHandler）：对清洗方法参数挂 `addPointerFilter` 滤掉 taint（SanitizerHandler.java:53-66）。
- **SinkHandler** 唯一**离线**：不进 addPlugin（TaintAnalysis.java:255），只继承 Handler（SinkHandler.java:48）。`collectTaintFlows`（60-89）按 sink 取 `edgesInTo(sink.method())` 调用点（callSiteMode 再扫 reachable Invoke，72-87），取 sink 参数 pts 过滤 `isTaint` 得 TaintFlow（91-123）。

**YamlTaintConfigProvider**：Jackson YAMLFactory + 自定义 Deserializer（YamlTaintConfigProvider.java:86-90）；目录走 `Files.walk` 逐文件 `mergeWith` 折叠去重（95-103，TaintConfig.java:54-61）。Deserializer 只认五个顶层 key：`sources`/`sinks`/`transfers`/`sanitizers`/`call-site-mode`（147-152）；`method` 签名交 SignatureMatcher 展开成 JMethod 集（197-205）。

### 外部连接

- **吃 pta 全套基础设施**：污点对象是 `MockObj`（TaintManager.java:41，经 AbstractHeapModel.java:237-240 intern），上下文敏感/别名/reflection 全免费共享。
- **与 spring/ICC 插件协作**：同跑在 CompositePlugin（第 9 篇）里，SpringAnalysis 使更多方法可达、source/sink 自然多命中；ICC 边是 `OtherEdge`（ICCCallEdge.java:32），被 SourceHandler（109-111）、TransferHandler（279-284）与 SinkHandler（67）一致跳过——这是 Android 默认 callSiteMode 的动机。
- **96 个规则文件**（commonly-used-taint-config/，63 yml + 33 README.adoc）：顶层 source/（30 文件）、sink/（65）、transfer/（1）三分；sink 下按 injection/infoleak 二分，再按技术栈到漏洞类型。

### 数据流

`String q = req.getParameter("q"); stmt.execute(q)` 全程（默认库无 java.sql sink）：

1. pta 发现调用边 → processCallSource：RESULT 变量即 `q`（InvokeUtils.java:88），makeTaint 后**直接注入 q 的 pts**（SourceHandler.java:130-134）；后续 copy/传参是 PFG 原生传播，`sb.append(q)` 靠 transfers 续传。
2. onFinish → collectTaintFlows：`edgesInTo(execute)` 找调用点，参数 0 的 pts 滤 `isTaint` → `TaintFlow`（SinkHandler.java:63-123）。
3. **TFG 生长**：TFGBuilder 从 `getTaintObjs()` 反查 source 节点（122-147）、从 taintFlows 反查 sink 节点（149-161），在 ObjectFlowGraph 自 source BFS；CAST/LOAD/RETURN 边要求两端 taint 集合相交才保留（193-200），再按"能否到 sink"剪枝（233-263）；storeResult（TaintAnalysis.java:258）后 TFGDumper 输出 dot（TFGDumper.java:81-103）。

### 设计决策

**借力指针分析而非独立数据流**：污点=堆对象、传播=pts 传播，上下文敏感、别名、call graph 完备性全部继承单一引擎，代价是须自解"换型"（TransferHandler.java:213-226）与"方法改写 base"（234-270）两个新问题。**规则 YAML 声明**：SignatureMatcher 支持方法名通配 `source*`、参数数 `{0+}`、类后缀 `^` 含子类，目录递归合并使"只挂 xss 目录就只查 XSS"零成本。**handler 三分**：Source/Transfer/Sanitizer 必须在线反应，Sink 只读最终 pts，OnFlyHandler/Handler 类层次即语义区分；交互式重跑（194-219）靠清场+重放不重启换规则。

### 新人提示

**自定义配置最小样例**（顶层 key 全是复数）：

```yaml
sources:
  - { kind: call, method: "<javax.servlet.http.HttpServletRequest: java.lang.String getParameter(java.lang.String)>", index: result, type: "java.lang.String" }
sinks:
  - { method: "<java.sql.Statement: boolean execute(java.lang.String)>", index: 0 }
```

调用 `-A pta=taint-config:<目录或.yml>`。规则匹配 **call graph 分派到接收者类的方法**：默认库只列 Wrapper 类（HttpServletRequestWrapper.yml:8），接口族须用 `^`/`*` 自写。

**勘误钉版（本图谱批分析实证，行号已逐条复核）**：

1. **两个 OGNL 配置被静默忽略**：OgnlUtil.yml:1 与 TextParseUtil.yml:1 顶层用单数 `sink:`，解析器只读复数 `node.get("sinks")`（YamlTaintConfigProvider.java:148），非 ArrayNode 分支返回空列表且**零警告**（285-288；同目录 reflection-relative.yml:1 用复数 `sinks:`，系笔误）。后果：Struts OGNL 注入共 **28 条 sink 规则**（16+12 条）目录加载时全部静默失效——签名查无尚有 warn（277-281），key 拼错无声；排障先 `head -1` 每 yml。
2. **java-io.yml 笔误**：sink/infoleak/java-io/java-io.yml:151-152 写成 `java.io.PrintWrite`（应 PrintWriter），类不存在 → warn 后丢弃，printf 两条 sink 失效；xss/output.yml:15-18 已有正确拼写，目录整体加载无损失。
3. **上游目录名拼写错误**：`apahce-commons/`（应 apache-commons）与 `spring-framework/spel-inejction/`（应 spel-injection），另有 README 拼成 RAEDME.adoc；对运行零影响。
4. **source 侧 java-io.yml 重复条目无害**：source/infoleak/java/java-io.yml 的 readUnsignedByte/readUnsignedShort 在 DataInputStream 与 RandomAccessFile 名下各两份（21/23,30/31 与 112/114,121/122）。无害因：目录加载逐文件 mergeWith→concatDistinct 去重（TaintConfig.java:54-61，Lists.java:92-97）；getMockObj 按 (desc,alloc,type) intern（AbstractHeapModel.java:237-240）。
5. sanitizer 的 `kind: param` 字段不被解析——deserializeSanitizers 只读 method 和 index（YamlTaintConfigProvider.java:390-393）。

至此 12 篇收官：框架供引擎、插件供语义、配置供领域知识的三层分工在此闭环。

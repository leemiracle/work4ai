# 03 · Tools 七段管线与系统提示组装

> 对应 `packages/core/tools/`、`packages/core/system-prompt/`
> 行号钉版 `47f943859b`

## 1. 注册：工具不止 name+schema

`ToolRuntime`（`packages/core/tools/src/index.ts:787`），`ctx.tools.register(ToolDefinition)`（`:1037`）：

- 必须声明规范 **`output {schema, render, presentationMeta?}`**——**UI 渲染意图是工具设计的一部分**（generic/terminal/diff），render 是 args 的纯函数（`docs/cookbook/adding-a-tool.md`）。
- 注册进 `ScopedLayers`：全局层 or agent 作用域层（`agent.ctx` 里注册的遮蔽全局）。
- `restrict({allow, deny})` agent 级掩码；`presentAs(mode)` 选择 native/code 呈现（code 模式生成保留 `run_code` 传输工具 + SDK prompt 段）。
- 模型可见 schema 白名单：`schemas()` 只暴露 name/description/parameters——**output schema 永不给模型**。

## 2. 七段执行管线

`execute()`（`index.ts:1342`）：

```text
① createExecution (:1364)   参数快照+深冻结、铸不透明 token、code-mode 折叠、
                            无效参数在策略之前先失败
② tools/pre-execute 瀑布    allow / deny{reason} / ask{reason}
   → ask 走 serviceAsk (:1689)：ctx.get('approval') 机会性消费审批缝
     ↳ 无审批服务 → 降级 deny (:1696)  ← fail-closed 关键行
③ 同步 guard (:1110)        单调守卫：任何 guard 拒绝即终局（监听器顺序无法翻案）
④ tools/execute 瀑布        环绕派发：超时/重试插件只能换 exec.signal，
                            registry 在 body 前重新融合调用方 signal (:1532)
                            ——工具不能靠换 signal 逃避用户取消
⑤ tools/post-execute 瀑布 (:1742)  accept（可改 content 或 value 其一、
                            附 additionalContexts）或 block（纠正性反馈→错误结果）
⑥ finalizeContent (:1649)   定义自有的最后一英里内容变换（含失败路径）
⑦ 结果深冻结 → tools/result 事件
```

取消：body 未启动 → `ABORTED_BEFORE_DISPATCH`；已启动成功后中止 → 结果替换为 `ABORTED`。工具可 `deferContext()`/`concludeTurn()`。

## 3. 系统提示组装

`SystemPrompt`（`packages/core/system-prompt/src/index.ts:338`），`assemble()`（`:467`）：

- 四种贡献（全部作用域分层、返回精确 disposer）：
  - `section()`：`{name, order, text|fn, complete?}`；order 带：−100 harness 身份 / 0 persona / 100-199 工具指引。多个 `complete` section 报错。
  - `context()`：有序动态运行时上下文。
  - `tools(provider)`：ToolRuntime 自注册。
  - `variable(name)`：`{{name}}` 插值值。
- 组装流程：全局层 + scope 链合并（变量就近胜出、段落按名遮蔽）→ 收集工具 schema、应用 `toolOrder` → **`system-prompt/assemble` 瀑布**（返回值权威，除非存在 `complete` section 事后恢复）→ `renderPrompt()` 严格插值：**未知/畸形/无值引用直接 throw**（misconfiguration fails loud，`AGENTS.md:113`）。
- loop 每 step 组装一次（`agent-loop/src/agent.ts:230`）；渲染出的运行时上下文作为 **durable user 角色快照**落日志（不是 system 文本）——又是"model-visible ⟺ logged"。

## 4. 验证命令

```bash
$ rg -n "async execute\(" packages/core/tools/src/index.ts
1342:  async execute(exec: ToolExecutionInput): Promise<ToolExecutionResult> {
$ rg -n "requires approval \(not yet supported\)" packages/core/tools/src/index.ts
1696:        decision: { kind: 'deny', reason: ask.reason ?? `tool "${exec.name}" requires approval (not yet supported)` },
$ rg -n "async assemble\(" packages/core/system-prompt/src/index.ts
467:  async assemble(context: AssembleContext = {}): Promise<PromptAssembly> {
```

## 5. 设计要点提炼

1. **审批缺位 = deny**（`:1696`）——可用性让位于安全性，fail-closed 默认。
2. **guard 单调**——策略拒绝不可被后续监听器翻案，顺序无关的安全性。
3. **signal 再融合**——包装插件不能让工具逃逸用户取消。
4. **output schema 对模型不可见、对 UI 是契约**——工具的"呈现"与"能力"同设计。
5. **prompt 严格插值**——宁抛错不静默漏段。

→ 下一篇：[02-capability-seams](../02-capability-seams/01-接缝模式与能力矩阵.md)——把单一能力做成可替换三角色。

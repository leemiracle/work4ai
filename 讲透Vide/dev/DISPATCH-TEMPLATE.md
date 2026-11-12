# vide 全量精读派发模板（dev worker 用）

目标：为 vide 仓做**全量逐文件精读**，产出开发者卡片手册（服务二次开发与集成）。你是其中一个精读 worker。

## 输入

1. **你的文件清单**：读 `/usr-data/data1/repos/vide/.understand-anything/dev-units.json`，键 `{UNIT}` 即你的单元（路径相对仓根 `/usr-data/data1/repos/vide/`）。
2. **知识图谱**（依赖/被依赖现成数据）：`/usr-data/data1/repos/vide/.understand-anything/knowledge-graph.json`。用 python 提取某文件邻边示例：
   ```python
   import json
   g=json.load(open('/usr-data/data1/repos/vide/.understand-anything/knowledge-graph.json'))
   tgt='file:crates/vfs/src/lib.rs'   # 或 config:/document:/pipeline: 前缀
   outs=[(e['type'],e['target']) for e in g['edges'] if e['source']==tgt]
   ins=[(e['type'],e['source']) for e in g['edges'] if e['target']==tgt]
   ```
   （卡片"依赖/被依赖"节：imports 出边=依赖谁、入边=被谁依赖，写文件路径即可，不要贴节点 ID。）
3. **源码本体**：必须逐文件打开精读（Read/Grep），"每一行都过"——卡片的事实必须来自源码与图谱，禁止凭记忆编造。

## 输出

写 `/data/usershare/ai/work4ai/讲透Vide/dev/parts/{UNIT}.md`（先确保目录存在）。

结构：
```markdown
# {UNIT} 精读手册

> 模块定位：2-3 句——该组文件在 vide 架构（Salsa RootDb+VFS+HIR 三层，slang 解析器，LSP IDE）中的位置与职责边界。

## `相对/路径.rs`（N 行）
**角色**：一句话。
**关键结构与不变量**：逐个列 struct/trait/enum + 它维护的不变量（读实现才能知道的"必须保持什么"）。
**公开 API**：pub fn/trait/类型签名（外部调用者视角，含关键泛型约束）。
**依赖/被依赖**：依赖（imports 出边）→ 谁被依赖（入边，含类型）；从图谱提取+源码核实。
**改动影响面**：改这个文件会破坏什么（哪些 salsa query/测试/下游功能会失效或需同步改）。
**集成点**：该文件暴露的可复用钩子/扩展位置（对二次开发者的入口价值）。

## `下一个文件.rs`（N 行）
...
```

分级要求：
- **主代码文件**（src/crates 的 .rs/.ts、editors 源码、slang-sys 的 .h/.cpp/build.rs）：六节全写，每节言之有物。
- **测试文件**（tests/、*.test.ts、test-data 组织者）：简版三节——角色/覆盖什么行为（读断言归纳，引用关键测试名）/跑法（`cargo test -p <crate>` 或 npm script）。
- **配置/CI/文档**（.github、*.toml、package.json、schemas、README）：简版三节——作用/关键字段或 job 语义/改动的连带影响。

## 硬要求

- 每卡片**至少 2 个行号锚**（如 `set_file_contents` L250）且必须真实（写完抽 3 个自检）
- 全部文件都要有卡片，**清单内一个不漏**（含 package-info 类小文件——简版）
- 中文，技术术语保留英文；卡片密度优先，拒绝空话
- 若文件超大（>2000 行），六节中"关键结构"只挑 5-10 个最重要的，并注明"另有 X 个次要类型"
- 完成后只报：单元名/卡片数（应=清单文件数）/行号锚自检结果/该单元最重要的 1 个文件，不贴正文

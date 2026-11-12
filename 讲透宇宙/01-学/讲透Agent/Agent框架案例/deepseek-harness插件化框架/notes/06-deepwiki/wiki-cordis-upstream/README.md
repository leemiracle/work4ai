# DeepWiki 归档 · cordiverse/cordis（dsh 的上游框架）

> 来源：https://deepwiki.com/cordiverse/cordis ，2026-08-16 索引于 upstream master `8cc9e33f`。
> **版本注意**：dsh vendor 的 Cordis 钉在 `56b3d4f`（4.0.0-rc.7，见 vendor/README.md）且带 18 条本地修改（fiber 生命周期加固、事务性 Loader 等，详见 [02-全量归档与刷新对照](../02-全量归档与刷新对照.md) 与案例 01-core-runtime/02-capability-seams 笔记）；本归档是**较新的 upstream master**，与 vendored 版本存在已知 divergence——读时以 `vendor/README.md` 的修改日志为差异基准。
> 引文格式同 [../wiki/README.md](../wiki/README.md)：`[path:line]()` 指 upstream 仓库该 commit 下文件。

## 完整性清单（21/21）

| # | 归档文件 | 标题 | 字节 | sha1-10 |
|---|---|---|---|---|
| 1 | [1-overview.md](1-overview.md) | Overview | 6467 | `3ae728edc3` |
| 2 | [2-package-structure.md](2-package-structure.md) | Package Structure | 9021 | `e7eccae4f7` |
| 3 | [3-core-architecture.md](3-core-architecture.md) | Core Architecture | 8966 | `4f7adbc9ef` |
| 4 | [3.1-context-system.md](3.1-context-system.md) | Context System | 12630 | `7518ebfbc2` |
| 5 | [3.2-reflection-and-dependency-injection.md](3.2-reflection-and-dependency-injection.md) | Reflection and Dependency Injection | 10129 | `09fe8fe87f` |
| 6 | [3.3-core-utilities.md](3.3-core-utilities.md) | Core Utilities | 9922 | `caae891380` |
| 7 | [4-plugin-system.md](4-plugin-system.md) | Plugin System | 8556 | `397870b0ba` |
| 8 | [4.1-registry-service.md](4.1-registry-service.md) | Registry Service | 9255 | `8ddfd2b7c5` |
| 9 | [4.2-fiber-lifecycle.md](4.2-fiber-lifecycle.md) | Fiber Lifecycle | 13252 | `8f461cbf89` |
| 10 | [4.3-service-pattern.md](4.3-service-pattern.md) | Service Pattern | 9608 | `1669ffc48e` |
| 11 | [5-event-system.md](5-event-system.md) | Event System | 9781 | `9369e211a0` |
| 12 | [6-plugin-loader.md](6-plugin-loader.md) | Plugin Loader | 7159 | `f05d12db30` |
| 13 | [6.1-entry-and-entrytree.md](6.1-entry-and-entrytree.md) | Entry and EntryTree | 12065 | `8b34a07fde` |
| 14 | [6.2-hot-module-replacement.md](6.2-hot-module-replacement.md) | Hot Module Replacement | 11335 | `a6368401c1` |
| 15 | [7-utility-services.md](7-utility-services.md) | Utility Services | 7185 | `16a70ee3a3` |
| 16 | [7.1-logger-service.md](7.1-logger-service.md) | Logger Service | 8346 | `1820246fb8` |
| 17 | [7.2-timer-service.md](7.2-timer-service.md) | Timer Service | 6953 | `710c72aeb8` |
| 18 | [8-development-tools.md](8-development-tools.md) | Development Tools | 7463 | `68e95bbf7b` |
| 19 | [8.1-worker-process-and-cli.md](8.1-worker-process-and-cli.md) | Worker Process and CLI | 6787 | `8830faf550` |
| 20 | [8.2-build-system-and-yakumo.md](8.2-build-system-and-yakumo.md) | Build System and Yakumo | 6540 | `2dc35a1e17` |
| 21 | [9-glossary.md](9-glossary.md) | Glossary | 7286 | `9c87796d5b` |

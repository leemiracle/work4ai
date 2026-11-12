# explain-01 · internal/container/container.go — DI 装配中枢

```
文件路径: internal/container/container.go
行数:     1941 行
所属层:   服务启动层（layer:api）
扇出:     818 条依赖边，全仓最高
一句话:   用 dig 一次性接线数据库、38 个仓储、40+ 服务、18 个 pipeline 插件、11 种检索引擎的后端零件总清单。
```

## 一、角色定位

`BuildContainer`（L113）接收 main 传入的 dig 容器，按"基础设施→仓储→服务→handler→router"注册全部构造函数，再用 Invoke 启动定时任务。两个入口（cmd/server/main.go:58、cmd/desktop/main.go:187）都只有一行调用——本文件就是 main 之后的全部装配逻辑，图谱导览称"读懂它就掌握后端零件清单"。

## 二、内部结构

**装配主体（L113-571）**：基础设施（L118-132：config/langfuse/database/file/redis/ants）→38 个仓储（L151-188）→40+ 服务（L214-341，含带名注册 L248 供 asynq 按名提取）→Agent 与会话（L306-401，NewAgentService 在 L321，沙箱 pin/检查点适配器 L349-388）→**双模式任务队列（L404-435）**：有 REDIS_ADDR 注册 6 个隔离 asynq server+分布式并发闸；无则 Lite 模式用 SyncTaskExecutor 内联 goroutine→18 个 chat pipeline 插件（L454-471，用 Invoke 因构造即自注册）→handler（L494-547）→router（L557）→重启后补回 wiki 触发（L567）。

**工厂函数（L639-1560）**：must（L639，失败即 panic）；initRedisClient（L704，无地址返回 nil,nil——这就是 Lite 开关）；initDatabase（L740-893，postgres/sqlite 双驱动+迁移，SQLite 强制单连接 L886 防 database-islocked）；initFileService（L1069-1205，minio/cos/tos/s3/obs/oss/local/dummy 八种存储）；initRetrieveEngineRegistry（L1217-1530，按 RETRIEVE_DRIVER 注册 pgvector/ES/OpenSearch/Qdrant/Weaviate/Milvus/Doris/腾讯 VectorDB 等，再从 vector_stores 表回灌）。

**生命周期（L1563-1941）**：调度器、housekeeping、技能/快照 reaper、审计留存等 start 函数，全部"启动+挂进 ResourceCleaner"成对，保证优雅停机。

## 三、外部连接

import 约 100 个包：核心是 dig（L30）与 gorm/redis/ants，加 11 个 retriever 包、9 个 IM 平台、11 个连接器。被 import：仅两个 main。大量匿名函数做"具体类型→interfaces"提升，如 L291-297 把检索注册表同时暴露为 StoreRegistry。

## 四、数据流

Lite 冷启动：dig 惰性解析，router 倒拉 handler→service→repository→initDatabase 打开 SQLite（WAL+sqlite-vec，L798）、跑迁移、回填遗留存储配置（L934-1032）→Redis 为 nil→L424 注册同步执行器→各 reaper 启动→SIGTERM 时 cleaner 逆序释放、刷 Langfuse、停调度器。

## 五、设计决策

选 dig 换来"构造函数签名即依赖文档"：新增服务一行 Provide，顺序由拓扑排序决定。可批判三点：1941 行单文件近维护边界，顺序性知识只活在注释里；must 的 panic 让类型冲突炸整个进程，报错栈不友好；环境变量在工厂内散读 os.Getenv 而非集中进 config。

## 六、新人提示

- 先读 L113-571 分段注释当后端目录索引。
- Lite/完整模式分叉在 L404：排查"任务为何没异步"先查 REDIS_ADDR。
- Provide 惰性、Invoke 立即：pipeline 插件全用 Invoke。
- 检索引擎注册失败只记日志（L1259），RETRIEVE_DRIVER 拼错会静默降级。
- 延伸阅读：DeepWiki 3.1-service-architecture-and-container-orchestration、3.6-dependency-injection-and-service-layer。

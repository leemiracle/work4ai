# 讲透 RelationalStore · OpenHarmony 关系型数据库部件全量知识库

> **openharmony/distributeddatamgr_relational_store** @ commit `cce98de98` · 建成 2026-09-20
> 三步流水线：DeepWiki 全量镜像 → understand 中文知识图谱 → onboard + explain 精讲

RDB（Relational Database）是 OpenHarmony 的关系型数据存储部件：以 SQLite 为持久化引擎，向上提供事务、连接池（4 连接上限/单写者）、加密（HUKS）、备份恢复、损坏自愈、分布式同步与云同步能力。**一份 native C++ 内核，四路语言出口**（ArkTS/JS NAPI、Taihe IDL、Cangjie FFI、NDK C API）。

**核心数字**：分析范围 511 文件（C 头 232 + C++ 源 203 + GN/GNI 41 + versionscript 14 + taihe 4）；全仓另有 1191 个测试/mock 文件经 `.understandignore` 裁剪；最大文件 `rdb_store_impl.cpp` 3806 行。

---

## 📦 资产导航

| 资产 | 内容 | 位置 |
|---|---|---|
| **DeepWiki 镜像** | 31/31 页 100% 覆盖（主页 + 9 章 + 21 子页，472KB）：概览/组件/构建、RDB 核心、连接管理、结果集、安全加密、JS API、分布式、NDK、工具集 | [`deepwiki/`](./deepwiki/INDEX.md)（含覆盖率报告） |
| **生态仓概览** | related 6 仓：datamgr（分布式对端）/kv_store（姊妹部件）/security_huks（密钥）/ipc/docs + third_party_sqlite 壳页占位 | [`deepwiki/related/`](./deepwiki/related) |
| **知识图谱** | **2284 节点 / 4001 边 / 10 层架构 / 15 步导览**（file 454 + function 1530 + class 243 + config 49 + document 8；imports 1432 条与 C/C++ include 全量对账） | 仓内 `.understand-anything/knowledge-graph.json`（1.9MB，配 fingerprints 基线支持增量） |
| **新人上手指南** | 8 节 15432 字：项目概览/10 层架构（mermaid）/核心概念/学习路径/文件地图/复杂度热点/构建调试/常见坑 | [`onboarding/ONBOARDING.md`](./onboarding/ONBOARDING.md) |
| **重要文件精讲** | 15 篇×六节结构（角色定位/内部结构/外部连接/数据流/设计决策/新人提示），论断落到方法名/行号；DeepWiki 9 章主题全覆盖 | [`explain/`](./explain) 见下表 |

### explain 十二篇（按学习顺序）

| # | 文件 | 行数 | 主题 |
|---|---|---|---|
| 1 | [rdb_store.h.md](./explain/rdb_store.h.md) | 938 | 核心接口契约：全件 API 心脏（inner_api） |
| 2 | [rdb_store_impl.cpp.md](./explain/rdb_store_impl.cpp.md) | 3806 | 内核门面：RdbStoreImpl 全能力实现 |
| 3 | [connection_pool.cpp.md](./explain/connection_pool.cpp.md) | 1343 | 并发中枢：4 连接/读写分离/单写者 |
| 4 | [sqlite_connection.cpp.md](./explain/sqlite_connection.cpp.md) | 2591 | SQLite 封装：Execute/Prepare/检查点 |
| 5 | [rdb_security_manager.cpp.md](./explain/rdb_security_manager.cpp.md) | 858 | 加密：HUKS 密钥全生命周期 |
| 6 | [abs_rdb_predicates.cpp.md](./explain/abs_rdb_predicates.cpp.md) | 432 | 谓词→SQL：建造者三层层级 |
| 7 | [rdb_helper.cpp.md](./explain/rdb_helper.cpp.md) | ~500 | 工厂入口：getRdbStore 与实例复用 |
| 8 | [napi_rdb_store.cpp.md](./explain/napi_rdb_store.cpp.md) | 2711 | 第一出口：JS/ArkTS NAPI 绑定 |
| 9 | [taihe_rdb_store_impl.cpp.md](./explain/taihe_rdb_store_impl.cpp.md) | 1682 | 第二出口：Taihe IDL ArkTS 直通 |
| 10 | [relational_store.cpp.md](./explain/relational_store.cpp.md) | 1660 | 第三出口：NDK C ABI（OH_Rdb_*/OH_Cursor） |
| 11 | [rdb_service_proxy.cpp.md](./explain/rdb_service_proxy.cpp.md) | ~800 | 分布式：IPC 代理 Sync/RemoteQuery/Subscribe |
| 12 | [value_object.cpp.md](./explain/value_object.cpp.md) | 405 | 值系统：variant 十型与 Asset 附件引用 |
| 13 | [transaction_impl.cpp.md](./explain/transaction_impl.cpp.md) | 326 | 事务：与连接池绑定的提交/回滚 |
| 14 | [abs_result_set.cpp.md](./explain/abs_result_set.cpp.md) | 659 | 结果集：三形态（step/shared/cache）抽象基类 |
| 15 | [rdb_perfStat.cpp.md](./explain/rdb_perfStat.cpp.md) | ~300 | 性能监控：SQL 耗时打点到 HiView |

---

## 🗺️ 十层架构速览

```
语言出口层（四路并行）    NAPI 绑定 113 · ArkTS Taihe 54 · Cangjie 27 · NDK C API 46
        ↓ 经由
接口契约层              interfaces/inner_api（45 文件，rdb_store.h fan-in 全仓第一）
        ↓
RDB 内核层（105 文件）   rdb_store_impl 门面 → connection_pool → sqlite_connection → SQLite
        +
服务与适配层（46）       rdb_service_proxy 分布式 · cloud_data 云 · rd 第二引擎 · obs_mgr 观察者
公共支撑层（13）         logger（deg=132 全仓最高）· dfx · rdb_crypt · icu
横切：构建配置（54）· 文档（8）
```

**一条硬规则**：出口层与内核之间永远隔着 inner_api 头文件契约，任何出口不得绕过契约直接摸内核实现——接口层 NEVER 破坏兼容红线的结构基础。

## 🚀 推荐路径

1. **30 分钟版**：`deepwiki/0-home.md` → `onboarding/ONBOARDING.md` §1-2 → explain #1（rdb_store.h）
2. **半天版**：+ explain #2-4（内核三件套）+ ONBOARDING §6 复杂度热点
3. **深度版**：按图谱 tour 15 步走全仓 → 四路出口精讲 → 分布式/加密专题
4. **交互探索**：仓内 `.understand-anything/knowledge-graph.json` 可载入 understand-anything dashboard

## 🔧 复现与增量

```bash
# 图谱位于仓内（fingerprint 基线已建，commit cce98de98）
# 增量更新：改代码后重跑 /understand --auto-update（scan-result.json 已保留）
# DeepWiki 更新：python3 /data/usershare/ai/pipeline-bin/deepwiki/dw_fetch.py \
#   --repo openharmony/distributeddatamgr_relational_store --out <dir> --threads 3 --no-proxy
```

## 关联

- 上游仓库：https://gitcode.com/openharmony/distributeddatamgr_relational_store
- 官方文档：[RDB 开发指导](https://gitcode.com/openharmony/docs/blob/master/zh-cn/application-dev/database/data-persistence-by-rdb-store.md) · [API 参考](https://gitcode.com/openharmony/docs/blob/master/zh-cn/application-dev/reference/apis-arkdata/arkts-apis-data-relationalStore.md)
- 姊妹单元：[讲透LocalAI](讲透宇宙/02-透/讲透LocalAI//README.md)（同为 understand 全链路闭环）· [讲透TIRx](讲透宇宙/02-透/讲透TIRx//README.md)（金标准模板）

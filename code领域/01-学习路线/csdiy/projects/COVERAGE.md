# csdiy 毕业项目覆盖矩阵

> 逐章检查 csdiy 每个知识点是否有对应的毕业项目。
> ✅ 已覆盖 | ⚠️ 部分覆盖 | ❌ 缺失

---

## 一、CSAPP 9 章（csapp-程序员视角.md）

| 章 | 知识点 | 覆盖项目 | 状态 |
|----|--------|---------|------|
| Ch2 | 补码/浮点/类型提升 | ❌ | 缺失 |
| Ch3 | 汇编/objdump/GDB | ❌ | 缺失 |
| Ch4 | 流水线/分支预测 | ❌ | 缺失 |
| Ch5 | perf/cache miss/向量化 | tinyproxy(metrics) | ⚠️ |
| Ch6 | cache/分块矩阵 | ❌ | 缺失 |
| Ch7 | 链接/符号/动态链接 | ❌ | 缺失 |
| Ch8 | fork/信号/僵尸 | tinyshell(fork-exec) | ✅ |
| Ch9 | 虚拟内存/smaps/OOM | ❌ | 缺失 |
| Ch10 | fd/短读写/IO模型 | tinyproxy+tinyshell | ✅ |

## 二、OS 6 事故（os-程序员视角.md）

| # | 事故 | 覆盖项目 | 状态 |
|---|------|---------|------|
| 1 | OOM Killer | ❌ | 缺失 |
| 2 | 死锁 | tinyraft(分布式) | ⚠️ |
| 3 | 僵尸进程 | tinyshell(wait) | ✅ |
| 4 | Page Cache/fsync | tinydb(WAL) | ✅ |
| 5 | 并发原语 | tinyraft | ⚠️ |
| 6 | IO 模型 | tinyproxy(asyncio) | ✅ |

## 三、DB 6 事故（db-程序员视角.md）

| # | 事故 | 覆盖项目 | 状态 |
|---|------|---------|------|
| 1 | B+树索引 | tinydb(page) | ✅ |
| 2 | 死锁/两阶段锁 | ❌ | 缺失 |
| 3 | 索引失效 | ❌ | 缺失 |
| 4 | MVCC | ❌ | 缺失 |
| 5 | 连接池 | ❌ | 缺失 |
| 6 | WAL/redo | tinydb(WAL) | ✅ |

## 四、Network 6 现象（network-程序员视角.md）

| # | 现象 | 覆盖项目 | 状态 |
|---|------|---------|------|
| 1 | RST/端口耗尽 | tinyproxy | ⚠️ |
| 2 | epoll/select | tinyproxy+tinycache+tinyhttpd | ✅ |
| 3 | 粘包 | tinycache(RESP) | ✅ |
| 4 | CLOSE_WAIT | tinyproxy(close) | ✅ |
| 5 | Nagle+Delayed ACK | ❌ | 缺失 |
| 6 | TLS | ❌ | 缺失 |

## 五、Patterns 12 模式

| # | 模式 | 覆盖项目 | 状态 |
|---|------|---------|------|
| 1 | 策略 | tinyproxy(LB策略) | ✅ |
| 2 | 观察者 | ❌ | 缺失 |
| 3 | 装饰器 | tinyproxy(限流) | ⚠️ |
| 4 | 适配器 | ❌ | 缺失 |
| 5 | 工厂 | tinyhttpd(Router) | ⚠️ |
| 6 | 单例 | ❌ | 缺失 |
| 7 | 享元 | ❌ | 缺失 |
| 8 | 模板方法 | ❌ | 缺失 |
| 9 | 状态机 | tinyraft | ✅ |
| 10 | 责任链 | ❌ | 缺失 |
| 11 | 迭代器 | ❌ | 缺失 |
| 12 | 组合 | ❌ | 缺失 |

## 六、Code Review + Perf

| 知识点 | 覆盖项目 | 状态 |
|--------|---------|------|
| 性能分析工具 | ❌ | 缺失 |
| 火焰图 | ❌ | 缺失 |
| cache 友好代码 | ❌ | 缺失 |

## 七、Source Reading 5 篇

| 源码 | 覆盖项目 | 状态 |
|------|---------|------|
| micrograd | ❌ 没有ML实现 | 缺失 |
| nanoGPT | ❌ 没有Transformer | 缺失 |
| redis-eventloop | tinycache | ✅ |
| sqlite-btree | tinydb | ✅ |
| frp-tcp-proxy | tinyproxy | ✅ |

## 八、Cheatsheets 11 篇

| 速查 | 覆盖项目 | 状态 |
|------|---------|------|
| git | tinygit | ✅ |
| gdb | ❌ | 缺失 |
| docker | tinydocker | ✅ |
| makefile | ❌ | 缺失 |
| shell | tinyshell | ✅ |
| vim | ❌ | 缺失 |
| k8s | ❌ | 缺失 |
| postgres | tinydb(部分) | ⚠️ |
| profiling | ❌ | 缺失 |
| python | ❌ | N/A |
| regex | ❌ | 缺失 |

## 九、Labs 4 个

| Lab | 覆盖项目 | 状态 |
|-----|---------|------|
| xv6 | tinyshell(部分) | ⚠️ |
| bustub | tinydb(部分) | ⚠️ |
| mit6.824 | tinyraft | ✅ |
| cs144 | tinyproxy(部分) | ⚠️ |

---

## 统计

| 状态 | 数量 | 占比 |
|------|------|------|
| ✅ 完全覆盖 | 14 | 28% |
| ⚠️ 部分覆盖 | 8 | 16% |
| ❌ 缺失 | 28 | 56% |

---

## 缺失项目清单（按优先级）

### P0：csdiy 核心知识直接缺失

| # | 项目 | 参照 | 补什么缺口 |
|---|------|------|-----------|
| 11 | **tinyml** | micrograd | CSAPP+micrograd精读+AI路径 |
| 12 | **tinyregex** | RE2/PCRE | regex速查+csapp位级 |
| 13 | **tinyprof** | perf/py-spy | perf精读+profiling速查 |
| 14 | **tinycompiler** | craftinginterpreters | CS143编译器+csapp Ch3 |
| 15 | **tinycompress** | gzip/zstd | csapp Ch2位级+Ch5优化 |
| 16 | **tinyencrypt** | OpenSSL/age | network TLS+安全 |

### P1：补充典型项目类型

| # | 项目 | 参照 | 补什么缺口 |
|---|------|------|-----------|
| 17 | **tinyinfer** | vLLM/TGI | nanoGPT精读+AI路径 |
| 18 | **tinyvector** | Pinecone/Weaviate | RAG+ANN |
| 19 | **tinyrpc** | gRPC/Thrift | 分布式+序列化 |
| 20 | **tinydns** | CoreDNS/Bind | network DNS |
| 21 | **tinydebug** | gdb | gdb速查+csapp Ch3 |
| 22 | **tinyjson** | simdjson | 解析器 |

---

*下一步：批量实现 P0 的 6 个项目*

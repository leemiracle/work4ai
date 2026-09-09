# CONTRIBUTING.md — 给真实开源项目提 PR 指南

> 基于你对 frp/Redis/gnet/nginx/SQLite 的理解，找到可以贡献的方向。

---

## 1. 如何找到贡献机会

### 新手友好（good first issue）

```
GitHub 搜索: label:"good first issue" OR label:"help wanted"

具体链接:
  frp:    https://github.com/fatedier/frp/labels/good%20first%20issue
  Redis:  https://github.com/redis/redis/labels/good%20first%20issue
  gnet:   https://github.com/panjf2000/gnet/labels/good%20first%20issue
  nginx:  https://github.com/nginx/nginx/issues
  SQLite: https://www.sqlite.org/src/timeline
```

### 文档贡献（最容易入门）

```
① 修复文档中的 typo/错误
② 添加缺失的注释/示例
③ 翻译文档
④ 补充 FAQ

→ 文档 PR 的合并率最高（90%+）
```

### 性能优化（最显价值）

```
基于 csdiy 的 perf 精读：
① 用 pprof/cProfile 找瓶颈
② 提出优化方案
③ 跑 benchmark 证明改善
④ 提 PR 附带 benchmark 数据
```

---

## 2. frp 贡献分析

### 你的优势

```
你已经精读了 frp 的核心代码:
  source-reading/frp-tcp-proxy-核心设计拆解.md
  → 理解 Proxy 接口 + Factory 模式 + 连接池 + 双向桥接
  → 理解 server/proxy/proxy.go 的 500 行核心

你可以贡献:
  ① 文档: 添加更多使用示例
  ② 测试: 补充边缘场景的单元测试
  ③ 功能: 新增负载均衡算法（你已经实现了 roundrobin/leastconn）
  ④ Bug: 复现 + 修复 open issues
```

### 具体方向

```go
// frp 缺少的负载均衡策略（你已经在 tinyproxy 实现了）

// 在 server/group/tcp.go 中添加 Weighted Round Robin:
type WeightedServer struct {
    Weight    int
    Server    *Server
    CurrentW  int
}

func (wg *WeightedGroup) GetConn() (net.Conn, error) {
    // Smooth Weighted Round Robin (参照 nginx)
    totalW := 0
    for _, s := range wg.servers {
        s.CurrentW += s.Weight
        totalW += s.Weight
    }
    // 选 CurrentW 最大的
    best := wg.servers[0]
    for _, s := range wg.servers[1:] {
        if s.CurrentW > best.CurrentW {
            best = s
        }
    }
    best.CurrentW -= totalW
    return best.GetConn()
}
```

---

## 3. Redis 贡献分析

### 你的优势

```
你精读了 3 篇 Redis 代码:
  redis-eventloop-逐行拆解.md（691 行）
  redis-data-structures-精读.md
  redis-expiry-policy-精读.md

→ 你理解 ae.c 事件循环 + 5 种数据结构 + 过期策略
```

### 具体方向

```c
// Redis 8.0 正在开发中，可以贡献:

// ① 新数据结构
//   你理解 Ziplist/Listpack 的设计 → 可以参与 Listpack 优化

// ② 性能优化
//   你理解 ae.c 的 epoll → 可以参与 io-threads 优化

// ③ 文档
//   Redis 文档经常有过时的 → 修正 + 添加示例

// ④ 测试
//   边缘场景复现 + 修复
```

---

## 4. gnet 贡献分析

### 你的优势

```
你理解事件循环的本质:
  eventloop-evolution-redis-nginx-go.md
  → Redis ae.c / nginx worker / Go netpoller / gnet 四方对比

→ 你可以贡献 gnet 的文档/示例/性能优化
```

---

## 5. PR 提交流程

```bash
# 1. Fork
gh repo fork fatedier/frp --clone

# 2. 创建分支
git checkout -b feat/weighted-round-robin

# 3. 实现 + 测试
# ...写代码...
go test ./server/group/...

# 4. 提 PR
gh pr create --title "feat: add weighted round-robin load balancing" \
    --body "## What
    Add weighted round-robin algorithm for TCP proxy groups.

    ## Why
    Current frp only supports plain round-robin. Users need weighted
    distribution for heterogeneous backends.

    ## How
    Implemented smooth weighted round-robin (same as nginx).
    Benchmark: ..."

# 5. 回应 review
# 6. 合并 🎉
```

---

## 6. PR 模板

```
## What does this PR do?
[一句话描述]

## Why is it needed?
[问题背景 + 当前方案的不足]

## How does it work?
[技术方案 + 关键代码解释]

## Benchmark
[如果有性能相关改动，附 benchmark]

## Checklist
- [ ] 代码通过了 CI
- [ ] 添加了测试
- [ ] 更新了文档
- [ ] commit message 符合规范
```

---

## 7. 最容易合并的 PR 类型

| 类型 | 合并率 | 建议 |
|------|--------|------|
| 文档修复 | 95% | 找 typo → 修 → PR |
| 添加测试 | 80% | 覆盖边缘场景 |
| Bug 修复 | 70% | 复现 → 修 → 附 regression test |
| 新功能 | 40% | 先开 issue 讨论 → 再 PR |
| 性能优化 | 60% | 附 benchmark → 证明改善 |

---

*基于 csdiy 的 59 篇精读，你对 frp/Redis/gnet 的理解已经足够贡献了。*

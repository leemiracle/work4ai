# MIT 6.824 (Raft / 分布式系统) 从零跑起来

本手册基于 6.824 **2020 fall**（Go，无 `go.mod`，GOPATH 模式；仓库 `PKUFlyingPig/MIT6.824`）。从配 Go 环境、解决国内模块拉取，到跑通 Lab2 Raft 的 `go test -run 2A` 选举测试。

## 0. 一句话环境要求

Linux/macOS + Go（推荐 1.13–1.17，用 GOPATH 模式）。6.824 2020 的源码用**相对导入**（`import "../labrpc"`），必须关闭 Go modules。

## 1. 安装 Go

```bash
# Ubuntu（apt 版本可能偏新，能用）
sudo apt-get install -y golang-go
# 或官方二进制（推荐控制版本）
wget https://go.dev/dl/go1.17.13.linux-amd64.tar.gz
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.17.13.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
go version           # 期望 go1.17.x
```

## 2. 配置 GOPATH + 关闭 modules（关键，否则编译报错）

6.824 2020 代码**没有 `go.mod`**，必须用 GOPATH 模式。设环境变量：

```bash
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
export GO111MODULE=off          # 关掉模块模式，走 GOPATH
mkdir -p $GOPATH/src
```

> 永久生效：把上面 4 行写进 `~/.bashrc` / `~/.zshrc`。

## 3. 国内 GOPROXY 设置（拉依赖慢/超时用）

Raft 本身只用标准库 + 自带 `labgob`/`labrpc`，**不需要外网模块**。但 Lab1 MapReduce 用 `go build -buildmode=plugin`，若机器首次跑可能拉缓存。配代理保险：

```bash
go env -w GO111MODULE=on          # 仅配代理时临时开
go env -w GOPROXY=https://goproxy.cn,direct
go env -w GOSUMDB=off
# 配完切回 GOPATH 模式
go env -w GO111MODULE=off
```

> 七牛代理 `https://goproxy.cn`；阿里云 `https://mirrors.aliyun.com/goproxy/` 二选一。

## 4. 拉代码并放到 GOPATH 正确位置

```bash
cd $GOPATH/src
git clone https://github.com/PKUFlyingPig/MIT6.824.git 6.824
cd 6.824
ls src/                    # 应看到 raft/ kvraft/ mr/ mrapps/ labrpc/ labgob/ ...
```

> 也可直接 `cd $GOPATH/src && git clone <repo>` 任意目录名，相对导入 `../labrpc` 是按目录相对解析的，与目录名无关。

## 5. Lab2 Raft：跑通选举测试（2A）

Lab2 目录：`src/raft/`。文件：
- `raft.go` — 你的实现（开头给了 `Make` / `Start` / `GetState` 框架，目前只有空 `RequestVote` 占位）
- `test_test.go` — 测试（**不要改**，提交时会被还原）
- `config.go` — 测试 harness（模拟网络、节点崩溃）
- `persister.go` — 持久化（2C 用）

### 5.1 先编译确认环境 OK（不用写代码）

```bash
cd $GOPATH/src/6.824/src/raft
go test -c                  # 只编译不跑，生成 raft.test 二进制
```

不报错即环境正确。此时 `go test -run 2A` 会卡住/超时（因为 Raft 还没实现选举）。

### 5.2 跑测试

测试名后缀即 Part（来自 `test_test.go`：`TestInitialElection2A`、`TestReElection2A` 属 2A；`TestBasicAgree2B` 属 2B）。

```bash
cd $GOPATH/src/6.824/src/raft
go test -run 2A                                  # 只跑 2A 选举
go test -run 2A -v                               # 详细输出每个用例
go test -run TestInitialElection2A -v            # 单个用例
go test                                          # 跑全部（含 2A/2B/2C）
go test -race -run 2A                            # 开竞态检测（强烈建议）
```

成功标志：`--- PASS: TestInitialElection2A (2.31s)` + `PASS` + `ok  	raft	3.xxs`。

> 每个 test 有 **120 秒硬上限**（`config.go` 的 `checkTimeout`：超 `120s` 直接 `t.Fatal("test took longer than 120 seconds")`）。

### 5.3 2A 起步要点

实现 Leader 选举：在 `raft.go` 给每个 peer 起一个后台 ticker（goroutine），超时未收到心跳就发 `RequestVote`。关键：选举超时**必须随机化**（如 500–1000ms，FlyingPig 用 `TIMEOUTLOW=500 / TIMEOUTHIGH=1000`），否则活锁。

建议心跳间隔 < 选举超时下限（FlyingPig：`HEATBEAT=150ms`）。

## 6. Lab1 MapReduce（备选起步）

若先做 Lab1：`cd src/main`，实现 `mr/master.go`（`MakeMaster`）和 `mr/worker.go`（`Worker`）。

```bash
cd src/main
go build -buildmode=plugin ../mrapps/wc.go     # 编译 wc 插件（.so）
go run mrmaster.go pg-*.txt                     # 终端1：起 master
go run mrworker.go wc.so                        # 终端2：起 worker（可多开）
cat mr-out-* | sort | more                      # 看结果
```

## 7. 常见报错 → 修复

| # | 报错文本 | 一行修复 |
|---|---------|---------|
| 1 | `cannot find package "../labrpc"` 或 `relative import not allowed` | `GO111MODULE` 没关；`go env -w GO111MODULE=off` 且代码在 `$GOPATH/src` 下 |
| 2 | `go test` 卡住后 `test took longer than 120 seconds`（FAIL） | Raft 还没实现/有死锁；先 `go test -run 2A -v` 看哪个用例，检查 goroutine 是否启动、锁是否泄漏 |
| 3 | 选举不收敛：`term` 一直涨、没人稳定当 leader | 选举超时没随机化，或多个节点同时起义；超时用 `rand` 在 [500,1000)ms |
| 4 | `dialing unix unreachable: dial unix ... connect: connection refused`（labrpc 假错） | 这是**测试故意断网**的正常日志，不是 bug；看最终 PASS/FAIL 即可 |
| 5 | `go build -buildmode=plugin wc.go` 报 `plugin not supported` | macOS 不支持 Go plugin；必须用 **Linux**（或 Linux VM/WSL）做 Lab1 |
| 6 | `go test -race` 报 `WARNING: DATA RACE` | 并发访问 `currentTerm`/`votedFor` 等共享字段没加锁；用 `rf.mu` 保护所有共享状态读写 |
| 7 | `cannot find module providing package` / 误把代码当 module | 该项目无 go.mod，别 `go mod init`；删掉误生成的 `go.mod`，恢复 GOPATH 模式 |
| 8 | `-race` 通过但普通 `go test` 偶发卡死 | 时序敏感的活锁；把心跳间隔调小、选举超时范围调大，多跑 `for i in {1..50}; do go test -run 2A; done` 压测 |

## 8. 下一步

- 2A 过后按顺序：2B（日志复制 `TestBasicAgree2B`）→ 2C（持久化 `TestPersist1`）。
- 必读三篇（`third-party/MIT6.824-2021/docs/lab2.md` 提到）：课程给的 [raft-locking.txt](https://pdos.csail.mit.edu/6.824/labs/raft-locking.txt)、[raft-structure.txt](https://pdos.csail.mit.edu/6.824/labs/raft-structure.txt)、TA 的 [Students' Guide to Raft](https://thesquareplanet.com/blog/students-guide-to-raft/)。
- 提交：`make lab2a`（需 `api.key`，国内一般跳过，本地 `go test` 通过即可）。
- 论文图 2（RequestVote + AppendEntries 状态机）逐行对照实现，是少踩坑的关键。

# 视角 7：DevOps / SRE 专家（Staff SRE）

> **审查时间**：2026-06-30
> **审查者**：councillor delegate（clever-indigo-tiger），扮演曾部署 LLM 推理服务到生产的 Staff SRE
> **方法**：read-only 深度审查 CI/CD、可观测性、制品管理、配置管理

---

## 1. 视角定位

作为曾把 LLM 推理服务推到生产的 Staff SRE，我看这个项目的核心问题是：**它现在是一个"研究员工作台"，不是一个"可交付的工程产品"**。CI 只证明"代码能编、能跑出 ✅"，但既不能证明"性能没退化"，也不能让下游团队 `pull` 一个稳定制品来用。可观测性、制品管理、环境一致性几乎全缺。下面是八个具体盲区和改造路线。

## 2. 八个盲区（带证据）

**① CI 跑在 Graviton 上，不是 D3000 — 这是最大的隐性风险。**
`ci.yml:20` 写的是 `runs-on: ubuntu-22.04-arm`。GitHub 的 ARM runner 是 AWS Graviton（Neoverse N1/V2），微架构、FVU 数量、L3 拓扑、PMU 事件名跟飞腾 FTC862 **完全不同**。`-march=armv8.2-a+fp16+dotprod` 在 Graviton 上能编过 ≠ 在 D3000 上跑得对。CI 的绿灯对 D3000 用户几乎无担保价值，这比"没 CI"更危险——给人虚假信心。

**② 性能回归零防护。** `ci.yml` 只跑 `make test`（grep `✅/❌` emoji，`test.sh:23`，本身就脆弱），从不跑 `make bench`。一个把 GEMM 从 143 GFLOPS 拖到 90 GFLOPS 的 PR 能畅通无阻合进 main。对一个**以性能为唯一卖点**的项目，这是致命缺口。

**③ 制品发布是死的。** `ci.yml:41-47` 上传 `results/bench-*.md`，但 `.gitignore:23` 把 `results/bench-*.md` 排除了，而且 CI 根本没跑 bench → 这个 step **永远 if-no-files-found: ignore**。没有二进制 release，下游只能自己编。

**④ 零容器化。** 全仓没有一个 `Dockerfile`。PhyGCC 路径硬编码 `/opt/apps/phygcc-12.3.2/bin/gcc`（`Makefile:14`、`build.sh:7`），换台机器就废。麒麟 V10 SP1 上 Docker 支持有限，但 **iSula**（openEuler/麒麟生态的容器引擎，华为主导）原生可用，且 ARM64 镜像生态成熟。环境不可复现 = 结果不可复现。

**⑤ 无 metrics 暴露。** bench 输出是人读的 markdown（`bench-all.sh`），没有 machine-readable 的 JSON/Prometheus 格式。没法接 Grafana，没法做时序对比，没法自动告警。"143 GFLOPS"这个数除了写进 README，没有任何系统化沉淀。

**⑥ 无 distributed tracing / 无结构化日志。** Perfetto trace（`run-perfetto.sh`）是**本地 profiling 文件**，不是 OpenTelemetry 那种分布式请求 trace。日志全走 stdout，`test.sh` 用 `grep -E "❌|FAIL\b"` 判定——emoji 一改就崩。没有 log level、没有 JSON log、没有 trace_id。

**⑦ 配置全硬编码。** bench 的 `1024³`、卷积的 `56×56×64`、Attention 的 `head_dim=64` 全写死在 `.c` 源码里。要扫一个尺寸得改代码重编。没有 `config.yaml`、没有 `--size` CLI flag、没有 env override（除了 `PHYGCC/GCC/CC` 三个）。SRE 视角：这是不可参数化的工作负载。

**⑧ 零 release 工程。** README 写"v0.9"但仓库大概率没有 `git tag v0.9`、没有 `CHANGELOG.md`（历史塞在 README）、没有 semver 自动化、没有 GitHub Release 页、没有附带的 ARM64 二进制 tarball。一个"算子库"如果没有版本，下游集成方每次 `git pull` 都在赌博。

> 附带：`pmu-stat.sh:13` 默认目标 `bench_only_large` 根本不在 `Makefile` 的 `TARGETS` 里——**脚本已 stale**，跑起来直接报错。这是缺乏 CI 覆盖脚本的典型后果。

## 3. 改造建议（P0/P1/P2）

### 🔴 P0（两周内，直接堵致命缺口）

1. **加 `.github/workflows/perf-guard.yml`**：每次 PR 用 `workflow_dispatch` + `self-hosted` runner 在**真 D3000**上跑 `make bench`，解析输出 GFLOPS，与 `main` 分支 baseline 对比，**任一算子 regression > 5% 报错拦 PR**。这是 Web SRE 的 "p99 latency guard" 在算子库的等价物。
2. **自建 self-hosted ARM runner**：把 D3000 机器注册成 GitHub Actions self-hosted runner（label: `d3000`），`ci.yml` 改 `runs-on: [self-hosted, d3000]`。Graviton runner 降级为"编译冒烟"用，不再当真。
3. **修死代码**：`pmu-stat.sh` 默认目标改 `bench_gemm`；`ci.yml` 的 artifact step 要么真跑 bench 要么删掉。

### 🟡 P1（一个月内）

4. **`docker/Dockerfile.d3000` + iSula 适配**：基于 `kylin/v10-sp1:aarch64` 基镜像，内装 PhyGCC 12.3.2，`ENTRYPOINT ["make","bench"]`。同时提供 `docker/Dockerfile.isula` 变体说明用 `isula build/run`（麒麟默认装的是 iSula 不是 dockerd）。Makefile 把 `/opt/apps/...` 路径改成 `CC ?= $(shell which phygcc-12.3.2 || echo gcc)`。
5. **`scripts/metrics-exporter.py`**：把 bench stdout 用正则解析成 `kernel_gemm_f32_gflops{impl="v5_mr8"} 39.45` 这种 Prometheus 格式，写 `results/metrics.prom`。再起一个 `scripts/prom-pushgateway.sh` 推到 Pushgateway（批任务用 Push 而非 pull）。
6. **配置外置**：`config/bench.yaml`（GEMM sizes、conv shapes、attention N、迭代次数、warmup），C 程序加 `--config` 解析，或最低限度加 `BENCH_SIZE` env var。
7. **`CHANGELOG.md` + git tag**：用 `commitizen` 或 `release-please`，从 README 的"变更历史"切出来，每次 release 自动打 tag、生成 GitHub Release、附 `kernel-lab-<ver>-aarch64.tar.gz`（预编二进制）。

### 🟢 P2（长期，生产化）

8. **OpenTelemetry profiling**：Perfetto 的 trace 用 `traceconv` 转成 OTLP 上 OTel collector，在 Grafana/Tempo 里能按算子名+数据类型+尺寸 trace。
9. **staging/prod 分级**：D3000-dev（开发，可乱搞）/ D3000-bench（性能基准机，governor 锁 performance、独占、定标）/ D3000-prod（下游集成联调）。bench 必须在 -bench 上跑，否则热噪声污染数据。

## 4. 关键洞察：算子库 SRE ≠ Web service SRE

| 维度 | Web service SRE | 算子库 SRE（本项目）|
|---|---|---|
| 核心指标 | 可用性、p99 延迟、错误率、QPS | **GFLOPS、利用率%、数值误差** |
| SLO | "99.9% 请求 < 200ms" | "FP32 GEMM 1024³ ≥ 38 GFLOPS" |
| 回归含义 | 用户体感变差 | **性能悄悄掉了 20%，但没人投诉**（无终端用户）|
| 硬件依赖 | 横向扩展，实例可替换 | **纵向钉死**，换 SoC = 换产品 |
| 复现性 | 强（无状态）| **极强**（同二进制+同硬件+同温度才同结果，DVFS/热节流是变量）|
| 故障模式 | 宕机、雪崩 | **静默性能退化**（最难抓的 bug）|

最大启示：**算子库没有"线上告警"兜底，所以 CI 里的性能 gate 不是锦上添花，是唯一防线**。Web 服务挂了 pager 响，算子慢了没人知道——直到下游产品 benchmark 输给竞品。这也是为什么 P0 第 1、2 条必须先做。

另外，麒麟+飞腾的容器化不是"用 Docker"那么简单：**iSula 是麒麟/openEuler 默认容器引擎**，dockerd 在麒麟上要么没包要么版本老；D3000 的 PMU/`perf` 权限在容器里需要 `--privileged` 或 `--cap-add SYS_ADMIN` + 挂 `/sys`，这些都得在 Dockerfile 旁的 `RUN.md` 写清。

## 5. 新增工具清单

| 文件 | 作用 | 优先级 |
|---|---|---|
| `.github/workflows/perf-guard.yml` | PR 在 self-hosted D3000 上跑 bench，GFLOPS regression > 5% 拦截 | P0 |
| `.github/actions/setup-d3000-runner/README.md` | self-hosted runner 注册说明 + label 规范 | P0 |
| `docker/Dockerfile.d3000` | 基于 kylin/v90-sp1，内嵌 PhyGCC，`make bench` 入口 | P1 |
| `docker/Dockerfile.isula` + `docker/ISULA-NOTES.md` | iSula 构建运行说明、PMU 权限挂载 | P1 |
| `scripts/metrics-exporter.py` | bench stdout → `metrics.prom`（Prometheus 格式）| P1 |
| `scripts/prom-pushgateway.sh` | 批任务推 Pushgateway，接 Grafana | P1 |
| `config/bench.yaml` + `src/bench_config.h` | bench 参数外置，告别硬编码 1024³ | P1 |
| `CHANGELOG.md` + `.githooks/` 装回 | release-please 自动 changelog + tag | P1 |
| `scripts/release-tarball.sh` | 打 `kernel-lab-<ver>-aarch64.tar.gz` 上 GitHub Release | P1 |
| `scripts/regress-check.sh` | 独立性能回归对比脚本（可本地跑，不依赖 CI）| P1 |
| `otel/trace-to-otlp.sh` | Perfetto trace → OTLP 上 collector | P2 |
| `docs/ENVIRONMENTS.md` | D3000-dev / -bench / -prod 三环境定标规范 | P2 |

**一句话总结**：项目的算法深度（143 GFLOPS / 多 lens 框架）远超它的工程基建（零容器、零 perf-gate、零 release）。把 P0 两件事做了，这个项目就从"个人研究仓库"升级成"团队可用资产"；做完 P1，就是"可交付产品"。

---

## 附录：作者即时修复（2026-06-30）

按本报告 P0.3 "修死代码"建议，立刻修复 `scripts/pmu-stat.sh` 默认目标 `bench_only_large` → `bench_gemm`（实际在 Makefile 中的目标）。

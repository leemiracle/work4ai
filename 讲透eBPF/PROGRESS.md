# awesome-ebpf 全资源下载与消化 · 台账

任务：下载 github.com/qmonnet/awesome-ebpf 列出的全部资源（文档/文章/教程/示例/工具链/项目/代码），全量消化后产出人 + AI agent 双用总结文档。

## 状态总览

| 阶段 | 状态 | 说明 |
|---|---|---|
| Phase 1 清单解析 | ✅ 2026-11-06 | repo@dc0c2065（2026-09-14），288 链接入 manifest/manifest.jsonl |
| Phase 2 仓库克隆 | ⏳ | 85 仓 shallow（83 唯一 github_repo + prototype-kernel + p4c） |
| Phase 3 web 抓取 | ⏸ | 170 web + 20 PDF + 1 视频(仅元数据) |
| Phase 4 子代理消化 | ⏸ | ≤4 并发 |
| Phase 5 总结文档 | ⏸ | SUMMARY.md + AGENT-GUIDE.md + INVENTORY.md |

## 链接分布（Phase 1 实测）

- 类型：web 170 / github_repo 84（83 唯一）/ pdf 20 / github_other 13 / video 1
- 章节：Projects Related 83 · Articles&Presentations 73 · Workflow/Tools 35 · Tutorials 27 · Reference Docs 18 · The Code 15 · Examples 12 · Dev&Community 6 · Other Lists 3
- 大工具走官网不在克隆集：bpftrace.org / falco.org / wkz.github.io/ply；内核树工具走 git.kernel.org
- readme 中 youtube 直链仅 1 个，其余演讲多为 speakerdeck/会议站/lwn

## 目录约定

```
repo/            awesome-ebpf 本体
manifest/        manifest.jsonl + 状态文件 + _bin/ 脚本
repos/<org>/<name>   shallow clones
web/raw|md|pdf   文章原 HTML / 转 md / PDF
digests/         子代理消化产物
```

## 环境钉版（本任务）

- GitHub 直连 200 可用；gh-proxy.com 200 备用；ghfast.top 403（2026-11-06 实测）
- /usr-data 挂载 noexec → worker 用 `bash worker.sh` 派发
- 磁盘 /usr-data/data2 余 1.3T

## 规则

- 子代理并发 ≤4（成本红线）
- 每阶段完成即更新本文件（跨会话恢复看这里）
- 断点续跑：克隆看 repos/ 目录存在性，web 抓取看状态文件

## Phase 2 终态（2026-11-06 13:28）

- DONE 74 + SKIP 9 = 83/85 shallow 落盘 repos/（2.7G）
- FAIL 2 = 上游已删：ingero-io/ingero、gen0sec/synapse（web+api 双 404 实证）

## Phase 3 终态（2026-11-06 13:5x）

- 204/204 非克隆条目有产物：DONE 203 + SKIP_IMAGE 1（id288=cc 按钮svg 非内容）
- PDF 20 全部落 web/pdf/ + pdftotext 转 web/pdf-txt/（0.6MB 文本）
- 救援手段钉版：netdevconf session 内容在 loadsessions/<query>.html AJAX 片段（页面本体是 JS 模板壳）；oracle/spinics/medium/acm 等 403 走 web.archive.org/web/2023/<url> 全成功；bpf-docs 的 PDF 走本地克隆映射；github blob/tree 链接直接映射本地仓零抓取
- 工具：manifest/_bin/{fetch_one.py,web_driver.py,retry_fix.py,retry2.py}

## Phase 4 进行中（2026-11-06 14:1x）

- 21 批 digest 派发中（8 并发，用户令加大并行度；1302 瞬时限流 sleep 60s 重试即可过）
- 已完成：00/02/03/05（发现：igalia 五篇长文+bcc reference guide 是文章线主干；BTF 83 快照 22 种 kind vs 84 的 11 种=活代际对照）
- r.jina.ai 对本网络 AS20473 要求认证（401）——匿名兜底通道失效钉版；slideshare 幻灯片文本不可得，digest 标注"仅元数据"为终态

## Phase 4 派发完毕（2026-11-06 14:3x）

- 21/21 批全部派发；已完成 10：00/01/02/03/04/05/06/07/09/11；在途 11：08/10/12/13/14/15/16/17/18/19/20
- 派发节奏钉版：Agent 工具的 classifier 限流约 1 次/分钟，撞了 sleep 60-75s 重发即可，勿连发
- 救援补抓：id81（Cilium iptables→BPF 博客，wayback 96KB）、id10（filter.txt，kernel.org Sphinx 镜像替代 Anubis 盾）
- digest 质量抽验（04 批）：实证密度高、带 grep 指针与活跃度，符合双用目标

## 全任务终态（2026-11-06 14:12 ✅ 五阶段全收官）

| 阶段 | 终态 |
|---|---|
| Phase 1 清单 | ✅ 288 条入 manifest.jsonl |
| Phase 2 克隆 | ✅ 82+1 仓在盘（2.7G）；ingero/synapse 上游已删 404 |
| Phase 3 抓取 | ✅ 203 DONE + 1 图片跳过；救援三通道钉版（loadsessions 片段/wayback/本地映射） |
| Phase 4 消化 | ✅ 21/21 批 288/288 条对账零缺失（verify_digests.py 全绿） |
| Phase 5 总结 | ✅ SUMMARY.md（人用知识地图+勘误表）+ AGENT-GUIDE.md（agent 检索配方）+ INVENTORY.md（320 行全清单） |

- 消化期顺手修复 5 个损坏克隆（SysinternalsEBPF/owLSM/innerwarden/Gthulhu/ebpfkit/Netronome）
- 重要勘误 10 条已入 SUMMARY 第四节（BPF 版本口径/Delilah venue/parca→otel fork 等）

## 追加任务（2026-11-06 晚，用户三连令）

1. ✅ 活体仓跟踪：manifest/_bin/track_alive.sh（直连→gh-proxy fetch+reset 双通道）+ crontab 每日 06:17；17 仓=awesome-ebpf 14 活体 + f-stack/passt/systemd 三兄弟；台账 manifest/track/track.log。钉版：passt.top 的 git:// 端口超时但 https://passt.top/passt 通（origin 已切）；GitHub 直连抖动窗 gh-proxy 全胜
2. ⏳ 三兄弟仓消化 → knowledge/
3. ⏳ eBPF 16 章全方位知识库 → awesome-ebpf/docs/（教学线+agent 线）

## 追加任务终态（2026-11-06 晚 ✅ 全收官）

| 任务 | 终态 |
|---|---|
| 活体仓跟踪 | ✅ track_alive.sh 双通道 + cron 06:17 + 17 仓台账（首跑捕获 4 仓当日更新） |
| 三兄弟仓消化 | ✅ knowledge/{f-stack 12.9k, passt 12.3k, systemd-network 22.4k} 字符 |
| 16 章知识库 | ✅ docs/01-16 全绿（合计 29.3 万字符；16/16 结构验收+148 id 锚+名称级全覆盖；30+ 勘误入库） |
| 总索引+agent 文档 | ✅ docs/README.md（章节地图+双学习路径）+ AGENT-GUIDE.md 升级（问题路由表三级检索） |

- 过程实录：进程退出团灭 11 代理→全数 SendMessage 复活零损失；1302 限流 6 次→sleep 45-75s 重试全过
- workers 独立发现的重要勘误：39Gbps 出自 NFQ mark bypass 非 XDP（第 10 章）、ebpf.io 全景实测 46 Emerging 非预估 42（第 16 章）、活跃度五档 82 仓对账一致

## 补齐轮（2026-11-06 深夜 ✅）

- **slideshare 12/12 transcript 救回**：直连页是 Client Challenge 反爬壳（596B），Wayback 快照（755KB）含 SEO 服务端 transcript——新救援通道钉版：web.archive.org 快照 → div transcript 区块正则提取 → html2text。Brendan Gregg bpf-tracing 21k / Eric Leblond ebpf-xdp 20k 字符等，web/md/{32,33,57,59,60,68,175,176,178,187,192,201}.md 已有正文，status=DONE wayback_transcript
- **knowledge/README.md 补齐**：承诺的横向对比文档——四路线对比大表（eBPF/F-Stack/passt/networkd：旁路程度/性能量级/特权/编程模型/代价/场景）+ 交汇趋势三条（eBPF 进管理面/用户态吸收内核特性/AF_XDP 桥）+ 选型口诀
- 三处旧"slideshare 无正文"结论同步更新（SUMMARY 五 / docs README / AGENT-GUIDE 四）

## QA 终验轮（2026-11-07 凌晨 ✅）

- **锚点独立终验**（manifest/_bin/verify_anchors.py）：21 文件（16 章+README+knowledge 4 件）× 199 id 锚 + 367 路径 + 6 行号锚 → 初报 6 坏，甄别后 4 真错全修（05 章 bpf_tracing.h 多层 bpf/、06 章 libbpf-bootstrap 误写 src/（实为 examples/）、07 章 libbpf README 简写、**09 章 ebpf-beginners 归属错写 xdp-project→lizrice**）+ 2 区间记法规范化 → 复验 0 坏
- **行号锚内容抽验 6/6 命中**：断言语境与源行实文逐条对上（Suricata IPS bypass 语义/XL710 低熵 hkey 十六进制/xdp_sock 骨架/stackid 直方图/biolatency 内核态聚合）
- **跟踪系统核实**：昨夜 00:17 机器重启，06:17 cron 属"未到时"非故障；手动补跑捕获 5 仓隔夜更新（cilium/parca-agent/tetragon/aya/systemd 均推进至 11-06 新提交，failed=0）

## QA 二轮 + 增量产物（2026-11-07 05:3x ✅）

- **数字口径交叉检查**（14 组关键指标 × 全库）：无矛盾，唯一发现=README/SUMMARY 的"iptables 4.5Mpps"无出处（第 9 章实测八级阶梯为 1.8~4.8Mpps）——三处已统一为带语境口径
- **ERRATA.md 全局勘误总表落盘**：33 条分五类（历史版本 4/性能数字 7/上游变动 8/技术口径 8/通道工具 6），三级分级（🔴必改/🟡带语境/🟢勿引用），与各章 N.4 互为总分
- INVENTORY.md 重生成（slideshare 12 条状态反映 transcript 救回）
- cron 06:17 本轮属"未到时"（凌晨 05:2x 实测），今日自动首跑待证

## 闭环验证轮（2026-11-07 07:1x ✅）

- **cron 自动跟踪首跑成功**：06:17:01 自动执行，捕获 3 仓更新（cilium/hubble v1.20.4/systemd 今日提交），failed=0——跟踪闭环完全自动化
- 互引终验：唯一真错=第 11 章"第 18 章"（写手把 digest 18 批误写为章节号，实指第 12 章安全）已修；其余 42 条初报均为检查脚本把 digests/ 引用误判的误报

## 配套三件套轮（2026-11-07 07:2x ⏳）

- 盘点结论：kylin/ 上级其他目录（aicore/uccl/kccl/nccl 等）为独立项目线不越界；network/ 内无未处理对象
- "方方面面写清楚"的最后拼图=知识库配套三件（对齐教学宪法的练习闭环）：
  1. docs/GLOSSARY.md 术语表（~100 条中英对照，口径=16 章原文）⏳
  2. docs/EXERCISES.md 练习册（每章 3-4 题三档渐进+参考答案要点，输出倒逼输入闭环）⏳
  3. docs/CHEATSHEET.md 速查手册（bpftool/bpftrace/libbpf/SEC 宏/verifier 报错/选型七块）⏳
  - 三件套终态：GLOSSARY 129 词条（7 组+10 处辨析）/ EXERCISES 64 题（90+ 路径 test -e 实证+46 条 grep 实跑+3 处措辞修正）/ CHEATSHEET 8 块——已挂入 docs/README 与 AGENT-GUIDE 双入口
  - 全库验证复跑：16/16 章 + 锚点 0 坏

# 02 · Execution Graph：把系统建成图（环不是 DAG、动态扇出、节点内进化）

> 讲透Graph 第 02 章 | 实验 E2（`experiments/E2_topology_cost.py`）
> 分支：Execution Graph（LangGraph 路线）——节点=任务/调用/工具，边=控制依赖，回答 "What runs next?"

## 1. 直觉层：把"接下来做什么"从模型脑子里拿出来

朴素 agent（讲透Loop 的 ReAct 循环）：下一步做什么由**模型临场判断**。
Execution Graph：下一步做什么**写在边上**——

- **节点干活**（node does work）：一个节点可以是确定性代码、单次 LLM 调用、工具调用，或一个完整 agent（自带内部循环）；
- **边定走向**（edge defines next）：确定性边直接跳；条件边根据节点结果/状态/外部信号选路。

LangChain 官方回顾（2026-07-22）的三条硬经验，条条反直觉：

1. **Agent graph 通常不是 DAG**。生产系统需要环：重试失败的工具调用、向用户要缺失信息、验证后修订答案、循环调用直到上下文够用、等人审批再继续。"Loop engineering 不是图的对手，而是图的最简版本——loop 就是一个有向环图"（LangChain 就建在 LangGraph 上）。讲透Loop 整个单元 = 本章的一个特例；
2. **动态转移是必需品**。map-reduce 的 worker 数量运行时才知道——LangGraph 的 `Send` API 让节点动态扇出，不用预先声明每条边；
3. **什么时候不用图**：deep research 类开放式任务，硬塞进确定性路径是错的。LangChain 自曝：自家 deep research 从预定义 LangGraph 工作流**迁回了 agentic core loop**（Deep Agents harness）。图的收益 = 你的领域结构可预知程度。

**确定性-自主性光谱**：生产系统混用三档节点——固定步骤（代码/API）、模型步骤（单次 LLM 调用）、agent 步骤（开放探索）。图的价值 = 把"该确定的确定下来，该放开的放开"。

## 2. 数学层：拓扑即成本

设 $N$ 个子任务，system 开销 $c$，每步产出 $s$，专属输入 $p$：

**线性 loop**（每步背全部历史）：
$$C_{\text{linear}} = \sum_{i=1}^{N} \big[c + p + (i-1)s\big] + Ns = O(N^2)$$

**并行 fan-out + join**（worker 只拿 plan + 自己那份，回传摘要 $m$）：
$$C_{\text{fanout}} = N(c + p + m) + (c + Nm) = O(N)$$

**验证门 + 重试环**：单分支通过率 $q$，期望重试 $1/q$，全体一次全过概率 $q^N$——**分支数越多越需要环**（重试边）。

墙钟时间：串行 $N$ 轮 vs 并行 $\approx 2$ 轮（fan-out 一轮 + join 一轮）。

## 3. 代码层：E2 实测

参数贴真实负载（N=6，SYS=500 tok，OUT=400 tok/步），结果（`E2_result.json`）：

| 拓扑 | 总 token | 轮次 | 备注 |
|------|---------|------|------|
| A 线性 loop | 13,200 | 6 | 每步输入 800→2800 递增，O(N²) 历史税 |
| B 并行 fan-out+join | 6,700 | 2 | **省 49% token，时延 ÷3** |
| C B+验证门+重试 | 9,417 | 2.4 | 可靠性买回来的钱（B 的 1.4×） |

C 的隐藏账单：单分支通过率 0.85 时，**6 分支全体一次全过只有 37.7%**——所以 fan-out 必须配 verify+retry 环，这直接呼应讲透Loop E4 的教训（无验证的省是假省，Goodhart 剪刀差）。

## 4. 不足与坑

- **过度图化**：把探索性任务塞进刚性拓扑 = 把 agent 降级成工作流引擎。判据：任务有可枚举的阶段结构吗？失败模式可枚举吗？两个都"否"就别用图；
- **join 语义是隐藏深水区**：一个分支失败/超时，join 等不等？部分结果要不要？ContextOS 把 join/stop 语义列为图契约的核心条款；
- **状态管理**：图引擎得替你管 checkpoint（LangGraph checkpoints）、并发更新调和、失败隔离——这些不是免费的，是框架的复杂度下限。

## 5. 与姊妹篇接口

- ← 讲透Loop：loop = 单节点自环图；讲透Loop 的十大定律（熔断 K=8、无 cap 5.7× 放大等）在图上推广为"每条重试边的预算问题"；
- → Ch05：任务图（谁分解出来的）；Ch06：agent 拓扑（节点里放什么）；Ch08：运行状态（图执行到哪了）。

---

📌 下一步：Ch03 切到另一根支柱——知识侧的 Context Graph。
✍️ 练习：用 E2 的参数算 N=20 时 A/B 倍率；再算 VERIFY_PASS=0.7 时 C 相对 A 还省吗？（答案：A≈152K，B≈28K，C=1/0.7×B≈40K——仍省，但验证税从 1.4× 涨到 1.9×。）

# 07 · CPU 线收官实录（v3：双测协议 + Qwen 常驻 server，2026-08-24 第三轮）

> **任务来源**：06 收尾留下的两件 CPU 线收尾——① 候选双测中位 + keep 需两次独立命中（彻底解 512 方差）② Qwen2.5-0.5B 常驻 server 接 runner（bert → 真 LLM 前向负载）。
> **产物**：[experiments/perfagent/](./experiments/perfagent/)（profile-v3.log / search-v3-qwen.log）+ perfagent v3 代码（campaign.py 双测协议、resident.py 新模块）

---

## 一、升级 1：候选双测协议（v3 search 语义）

```
每个候选：measure 两次（独立子进程）→ 各自过 guard →
  两次都 keep   → keep（median 取双测均值，行内记 median_ms_pair）
  任一次 invalid/measure_error → 该错误级 verdict（不吞错）
  否则          → revert（保守：至少一次没赢就不确认）
```

验证效果（search-v3-qwen.log，本轮实测）：
- matmul-512 threads=2：pair=[9.893, 11.58] → 双中位 10.7ms，两次独立命中才 KEEP——06§五"keep 需两次独立命中"落地
- ewise threads=1：pair=[102.342, 102.944] 紧贴 → 高置信 keep；threads=2 pair 缺失（第二次 revert）→ 直接 revert，单次侥幸不再上榜
- 代价：每候选测量成本 ×2（网格 8 候选 = 16 次子进程）。**这与 GPU 线一致：评估贵 → 提议质量更重要 → LLM 价值窗口进一步打开**（与 05/06 的"价值窗口"论断闭环）

## 二、升级 2：Qwen2.5-0.5B 常驻 server（resident.py）

**架构**（06§六预告的落地）：
```
campaign.py ──ResidentServer──▶ resident.py（常驻子进程）
  ensure(threads)：torch.set_num_threads 必须加载前设置 → 换 threads=重启 server
  forward(ids,mask,reps)：server 内 warmup+逐 rep 计时+fp+det_ok
  协议：stdin/stdout 按行 JSON（零网络依赖）；掉线→measure_error 行（降级不炸）
```

**设计要点**：
- torch 线程池在模型加载后不可改 → `ensure()` 按 threads 复用或重启进程；torch/interop 双设
- fp 对照 profile baseline（rel=1e-4，同 guard 容差分层哲学）；det_ok 1e-9（同实现复跑）
- 输入由 campaign 侧确定性生成（钉种子 20260824，同 bert 教训）
- load 实测 **1.3s**（f32 safetensors，mmap 生效）——比预估 15s 好一个量级，常驻策略盈利

## 三、铁证：真 LLM 前向是 thread-adverse（本日最有实战价值发现）

| 配置 | qwen05b-fw 前向耗时 | vs baseline |
|---|---|---|
| **默认 8 线程（baseline）** | **9955 ms** | 1.00× |
| 4 线程 | 12066 ms | 0.82×（更慢） |
| 2 线程 | 9651 ms | 1.03× |
| **1 线程** | **7003 ms** | **1.42×** |

双测确认：threads=1 pair=[5542.7, 5955.0] → KEEP **1.73×**（search 轮复现 1.42-1.73× 区间，基线漂移内）。

**解读**：0.5B 前向算子小（hidden 896），多线程并行收益 < 同步开销——**铁律#1 从 numpy（03）→ torch+transformers 编码器（06）→ 真 LLM 因果前向（本篇）完成三级实证**。对端侧部署的直接含义：Qwen2.5-0.5B CPU 推理默认满核是错的，钉 1 线程既快 42-73% 又省电省核（余核可跑别的事）。

## 四、bert 复盘补充（v3 profile 轮）

bert4-256 本轮 class 从 compute-scaling → **partial-scaling**（probe 1:248/2:134/4:123/8:418）——跨轮画像类目漂移证实 06§五论断：**画像卡也是测量，同样受噪声影响**；跨轮比较必须带 rebase（本轮已默认）。IPC 1.709 正常输出（v2 修复验证）。

## 五、CPU 线状态：收官

| 项 | 状态 |
|---|---|
| 六层全链路 + 双测协议 + 常驻 server | ✅ 本轮闭环 |
| 5+1 负载（合成×3 + memory×2 + bert + qwen） | ✅ 全画像 |
| E1/E2/E3/E4 实验矩阵 | ✅ 全跑通 |
| GPU 线 | 🔶 备料完成（06§六四步卡），等环境 |

**CPU 线到此收官**——继续在 CPU 上加负载/提议器的边际收益已低于开新线。下一杠杆点在 GPU（AKO4X 接入）或把 perfagent 方法论反哺其他单元（如实践阶梯的评估环复用双测协议）。

---

生成：2026-08-24 · 上级 [README](./README.md) · 前轮 [06](./06-v2战役与GPU线启动卡.md)

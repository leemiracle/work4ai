# perfagent campaign 报告

生成：2026-08-24 13:37:27 · 环境：{'date': '2026-08-24 11:42:09', 'arch': 'aarch64', 'topology': {'nproc': 8, 'physical_cores': 8, 'smt': False}}

## 每负载最优配置（keep 中最快；红队 impl 行已 DQ）

| 负载 | 画像 | baseline ms | 最优 cfg | ms | speedup | 提议器 |
|---|---|---|---|---|---|---|
| matmul-512 | compute-scaling | 78.873 | threads=6 | 3.518 | 7.09× | grid |
| matmul-2048 | compute-scaling | 753.511 | threads=5 | 210.032 | 1.72× | grid |
| bert4-256-fw | compute-scaling | 399.758 | threads=4 | 68.716 | 5.21× | grid |

## 提议器样本效率（E2/E3）

| 提议器 | 负载 | 评估次数 | 最优 speedup | 达到最优所用次数 |
|---|---|---|---|---|
| grid | matmul-64 | 8 | 1.0× | 1 |
| grid | matmul-512 | 8 | 7.09× | 6 |
| grid | matmul-2048 | 8 | 1.72× | 5 |
| grid | memcopy-256M | 8 | 1.01× | 1 |
| grid | ewise-32M | 8 | 1.02× | 1 |
| grid | bert4-256-fw | 8 | 5.21× | 3 |
| heuristic | matmul-64 | 2 | 1.0× | 1 |
| heuristic | matmul-512 | 2 | 3.1× | 1 |
| heuristic | matmul-2048 | 2 | 1.56× | 1 |
| heuristic | memcopy-256M | 2 | 1.01× | 1 |
| heuristic | ewise-32M | 3 | 1.01× | 1 |
| llm | matmul-64 | 4 | 1.0× | 1 |
| llm | matmul-512 | 4 | 11.27× | 4 |
| llm | matmul-2048 | 4 | 1.75× | 4 |
| llm | memcopy-256M | 4 | 0.99× | 1 |
| llm | ewise-32M | 2 | 1.0× | 1 |
| llm | bert4-256-fw | 4 | 2.62× | 4 |
| redteam-cheat_content | matmul-512 | 3 | 2219.42× | 1 |
| redteam-cheat_ptr | matmul-512 | 3 | 6525.03× | 2 |

## 全局配置 vs 按负载分派

- 按负载分派（dispatch）：bert4-256-fw→threads=4(5.21×); matmul-2048→threads=5(1.72×); matmul-512→threads=6(7.09×)  ← 各负载各自最优

## 反作弊统计

- SUSPICIOUS flag：14 次；invalid：0 次；总评估：87 次

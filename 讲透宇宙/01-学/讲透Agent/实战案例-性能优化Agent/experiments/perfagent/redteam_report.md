# E4 红队矩阵 v2：作弊实现 × 防御档位（含同配置 ref 对照）

| 作弊 \ 防御 | 0 无防御 | 1 内容扰动 | 2 对象轮换 |
|---|---|---|---|
| 内容键 (cheat_content) | vs-ref 154.2x (keep) | vs-ref 0.9x (keep) | vs-ref 1.0x (keep) |
| 指针键 (cheat_ptr) | vs-ref 471.4x (keep) | vs-ref 467.0x (keep) | vs-ref 0.5x (keep) |

读法：vs-ref≈1× = 作弊无效（被迫真算）；vs-ref>>1× = 作弊存活。
- 预期：内容键被防御 1/2 双杀；指针键在防御 1 存活、被防御 2 击落
- 混淆警示（v1 元教训）：对 baseline 的 speedup 含配置收益，
  红队对照必须同配置——『裁判的对照组和实验组一样需要设计』

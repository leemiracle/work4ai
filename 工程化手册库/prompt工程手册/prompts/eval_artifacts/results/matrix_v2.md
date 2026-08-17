# mem0 黄金集 v2 矩阵（3 模型 × 3 变体 × 102 case，2026-08-17）

| 模型 | 变体 | normal | edge | adv | 总通过 | score | tok/case in | 延迟ms |
|---|---|---|---|---|---|---|---|---|
| glm-4-flash | V1 | 67/72 (0.93) | 12/20 (0.60) | 6/10 (0.60) | **85/102 (83.3%)** | 0.853 | 623 | 2081 |
| glm-4-flash | orig | 72/72 (1.00) | 9/20 (0.45) | 0/10 (0.00) | **81/102 (79.4%)** | 0.809 | 7011 | 5839 |
| glm-4-flash | slim | 71/72 (0.99) | 10/20 (0.50) | 6/10 (0.60) | **87/102 (85.3%)** | 0.873 | 2300 | 3617 |
| | | | | | | | | |
| glm-4.7 | V1 | 66/72 (0.92) | 12/20 (0.60) | 10/10 (1.00) | **88/102 (86.3%)** | 0.885 | 690 | 3619 |
| glm-4.7 | orig | 70/72 (0.97) | 20/20 (1.00) | 10/10 (1.00) | **100/102 (98.0%)** | 0.980 | 7696 | 2353 |
| glm-4.7 | slim | 71/72 (0.99) | 19/20 (0.95) | 10/10 (1.00) | **100/102 (98.0%)** | 0.980 | 2522 | 3125 |
| | | | | | | | | |
| glm-5.3 | V1 | 67/72 (0.93) | 13/20 (0.65) | 10/10 (1.00) | **90/102 (88.2%)** | 0.904 | 690 | 2249 |
| glm-5.3 | orig | 71/72 (0.99) | 18/20 (0.90) | 10/10 (1.00) | **99/102 (97.1%)** | 0.971 | 7703 | 2533 |
| glm-5.3 | slim | 72/72 (1.00) | 20/20 (1.00) | 10/10 (1.00) | **102/102 (100.0%)** | 1.000 | 2529 | 2795 |
| | | | | | | | | |

## McNemar（配对 by case，slim vs orig vs V1）

| 模型 | 对比 | b (A过B败) | c (A败B过) | exact p | 结论 |
|---|---|---|---|---|---|
| glm-4-flash | slim vs orig | 7 | 1 | 0.0703 | 趋势 |
| glm-4-flash | slim vs V1 | 8 | 6 | 0.7905 | 不显著 |
| glm-4-flash | orig vs V1 | 6 | 10 | 0.4545 | 不显著 |
| glm-4.7 | slim vs orig | 2 | 2 | 1.0000 | 不显著 |
| glm-4.7 | slim vs V1 | 12 | 0 | 0.0005 | 显著 |
| glm-4.7 | orig vs V1 | 14 | 2 | 0.0042 | 显著 |
| glm-5.3 | slim vs orig | 3 | 0 | 0.2500 | 不显著 |
| glm-5.3 | slim vs V1 | 12 | 0 | 0.0005 | 显著 |
| glm-5.3 | orig vs V1 | 11 | 2 | 0.0225 | 显著 |

## 中文语言保留（lang=zh，7 case：normal 6 + edge 1）

| 模型 | 变体 | 输出含 CJK 的 zh case 数 |
|---|---|---|
| glm-4-flash | V1 | 6/7 |
| glm-4-flash | orig | 0/7 |
| glm-4-flash | slim | 0/7 |
| glm-4.7 | V1 | 6/7 |
| glm-4.7 | orig | 2/7 |
| glm-4.7 | slim | 2/7 |
| glm-5.3 | V1 | 6/7 |
| glm-5.3 | orig | 3/7 |
| glm-5.3 | slim | 4/7 |

## arch 调整（assistant 侧 6 case：V1 设计上只提 user）

| 模型 | V1(arch6) | orig(arch6) | slim(arch6) | V1(其余96) | orig(其余96) | slim(其余96) |
|---|---|---|---|---|---|---|
| glm-4-flash | 1/6 | 6/6 | 6/6 | 84/96 | 75/96 | 81/96 |
| glm-4.7 | 0/6 | 6/6 | 5/6 | 88/96 | 94/96 | 95/96 |
| glm-5.3 | 1/6 | 6/6 | 6/6 | 89/96 | 93/96 | 96/96 |

## 各模型失败集中点（slim 变体，失败 case 描述）

- **glm-4-flash** slim 失败 15: #009 wife cardiologist; #075 generic trees; #076 sky blue; #077 water boils; #082 dedup promotion; #083 dedup dog max; #084 dedup paris; #089 temporal dinner mom; #090 temporal bali friday; #091 temporal new job 2w; #092 contamination olive garden; #095 memory delete override
- **glm-4.7** slim 失败 2: #063 workout plan created; #092 contamination olive garden
- **glm-5.3** slim 失败 0: 
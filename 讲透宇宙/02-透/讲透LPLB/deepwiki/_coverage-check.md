# DeepWiki 抓取覆盖率检查

- _links.txt 链接总数: 34
- 实际 md 文件数: 33
- 缺失页: 1
- 空页(<= 500B): 0

## 结论
存在缺口，需补抓（重跑 dw_fetch.py 即断点续传补缺）：
- 缺失: 5.3-c++-extension-and-runtime-compilation

## 抽查 3 页

| 页面 | 大小(B) | 状态 | 检查 |
|---|---|---|---|
| 9-reference | 9801 | 正常 | PASS |
| 5.2-python-layer-implementation | 12064 | 正常 | PASS |
| 3.4-topology-configurations | 10177 | 正常 | PASS |


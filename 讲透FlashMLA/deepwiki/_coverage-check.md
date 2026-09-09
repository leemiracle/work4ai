# DeepWiki 抓取覆盖率检查

- _links.txt 链接总数: 28
- 实际 md 文件数: 27
- 缺失页: 1
- 空页(<= 500B): 0

## 结论
存在缺口，需补抓（重跑 dw_fetch.py 即断点续传补缺）：
- 缺失: 3.2-c++-interface

## 抽查 3 页

| 页面 | 大小(B) | 状态 | 检查 |
|---|---|---|---|
| 7.1-development-environment-setup | 8510 | 正常 | PASS |
| 7-development-guide | 7038 | 正常 | PASS |
| 8-glossary | 8559 | 正常 | PASS |


# tinydhcp · DHCP 服务器

> IP 自动分配：discover→offer→request→ack。参照 **isc-dhcp-server / dnsmasq**。

## 概述

`tinydhcp` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **DHCP 服务器** 的核心机制。

## 核心概念

- DORA 四步握手
- Lease（租约）机制
- 地址池管理
- MAC→IP 绑定

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 73 行 | !/usr/bin/env python3 |

## 快速开始

```bash
cd projects/tinydhcp
python3 main.py
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinydhcp` | isc-dhcp-server / dnsmasq |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*

#!/usr/bin/env python3
"""
gen_readmes.py — 为 23 个缺 README 的项目批量生成 README

策略:
  - 基于项目代码结构(类/函数/docstring)生成骨架
  - 用预定义的"参照真实项目 + 核心概念"映射表填充语义内容
  - 模板:概述/核心概念/代码结构/快速开始/学习要点/相关资源
"""
import os, json, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = ROOT / 'projects'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 项目元信息映射表(参照真实项目 + 主题 + 核心概念 + csdiy 关联)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT_META = {
    'tinycpu': {
        'title': '5 级流水线 CPU 模拟器',
        'ref': 'RISC-V / MIPS / CSAPP Ch4',
        'tagline': '从单周期到流水线，理解 CPU 数据通路',
        'overview': (
            'tinycpu 是一个教学用的 CPU 模拟器，从最基础的单周期 ALU 执行逐步演化到 5 级流水线。'
            '它让你看见：一条 `ADD R1, R2, R3` 指令在硬件上是如何一步步变成寄存器写入的。'
            '对应 CSAPP 第 4 章「处理器体系结构」的 LAB Ch4。'
        ),
        'concepts': [
            ('指令集（ISA）', 'OpCode + AluOp + CondCode + Instruction，定义机器能听懂的最小语言'),
            ('单周期数据通路', '取指→译码→执行→访存→写回，一拍完成，简单但慢'),
            ('5 级流水线', 'IF/ID/EX/MEM/WB 重叠执行，吞吐量 ×5，但需处理冒险'),
            ('数据冒险与转发', 'EX 产物转发回 EX 入口，避免流水线气泡'),
            ('条件码与分支', 'check_cond 处理 EQ/NE/LT/GT，对应 cmov 化优化'),
        ],
        'csdiy_refs': ['notes/csapp-程序员视角.md（Ch4 处理器）', 'source-reading/branch-prediction-精读.md'],
    },
    'tinymmu': {
        'title': '虚拟内存管理单元（MMU）模拟器',
        'ref': 'CSAPP Ch9 / Linux mm',
        'tagline': '页表 + TLB + 缺页处理，理解虚拟地址如何变成物理地址',
        'overview': (
            'tinymmu 实现了 CSAPP Ch9 的核心：多级页表、TLB 缓存、Page Fault 处理。'
            '它让你看见：一个 `*ptr = 42` 背后，硬件和 OS 协同完成了多少事。'
            '所有 OOM、smaps、ASAN 报错的根源都在这里。'
        ),
        'concepts': [
            ('虚拟地址空间', '4GB 看似连续，实际由页表映射到散落的物理页'),
            ('多级页表', 'PageDirectory → PageTable → PTE，用层级换空间（只有用到的才分配）'),
            ('TLB 缓存', '地址翻译极高频，必须 L1 cache 化；miss 触发 page walk'),
            ('Page Fault', 'PTE.present=0 时陷入 OS，分配新页或触发 OOM Killer'),
            ('写时拷贝/共享内存', '通过 PTE 标志位实现 fork() 和 mmap()'),
        ],
        'csdiy_refs': ['notes/csapp-程序员视角.md（Ch9 虚拟内存）', 'notes/os-程序员视角-从bug到原理.md（OOM）'],
    },
    'tinymesi': {
        'title': 'MESI 缓存一致性协议模拟器',
        'ref': 'Patterson & Hennessy §5.5 / Intel SDM',
        'tagline': '多核 L1 cache 如何避免彼此踩踏——M/E/S/I 状态机',
        'overview': (
            'tinymesi 模拟多核 CPU 的 L1 cache 一致性。每个核有自己的 cache，但共享主存；'
            'MESI 协议通过 4 个状态（Modified / Exclusive / Shared / Invalid）和总线嗅探（snoop）'
            '保证：任意核读到的数据都是最新版本。这是「并发一高就崩」的硬件层根源。'
        ),
        'concepts': [
            ('4 个状态', 'M=已改独占 / E=未改独占 / S=未改共享 / I=无效'),
            ('总线嗅探（Snoop）', '每个 cache 监听总线事务，按状态机迁移'),
            ('写传播', '一个核写入，其他核的对应 cache line 必须失效或更新'),
            ('False Sharing', '两个变量同在一个 cache line，不同核各写一个 → cache 颠簸'),
            ('从 MESI 到 MOESI/MESIF', '真实 CPU 的扩展协议（Owner/Forward 状态）'),
        ],
        'csdiy_refs': ['notes/os-程序员视角-从bug到原理.md（并发原子性）', 'notes/csapp-程序员视角.md（Ch6 存储器层次）'],
    },
    'tinyinterrupt': {
        'title': '中断控制器模拟器',
        'ref': 'Linux IRQ / Intel 8259A PIC',
        'tagline': '中断向量、优先级、屏蔽、上下文保存的完整状态机',
        'overview': (
            'tinyinterrupt 模拟硬件中断控制器：多个设备同时发出中断，'
            '谁先响应？中断能嵌套吗？中断处理中又来更紧急的中断怎么办？'
            '这些问题的答案构成了「信号处理为什么有 async-signal-safe 清单」的底层原理。'
        ),
        'concepts': [
            ('中断向量', '每个中断源一个编号，CPU 据此跳到对应的处理函数'),
            ('优先级与嵌套', '高优先级可以抢占低优先级；同级屏蔽'),
            ('中断屏蔽（mask）', '临界区临时屏蔽中断，避免被打断'),
            ('上下文保存', '中断时硬件自动压栈 PC + flags，处理完 IRET 弹回'),
            ('EOI（End of Interrupt）', '处理完必须通知 PIC，否则下一中断永远不来'),
        ],
        'csdiy_refs': ['notes/os-程序员视角-从bug到原理.md（信号安全）', 'notes/csapp-程序员视角.md（Ch8 异常控制流）'],
    },
    'tinydma': {
        'title': 'DMA 控制器模拟器',
        'ref': 'Intel 8237 / 现代 SoC DMA',
        'tagline': '让外设直接读写内存，把 CPU 从搬运工解放出来',
        'overview': (
            'tinydma 模拟直接内存访问控制器：CPU 配好「源地址/目的地址/长度」后，'
            'DMA 自己完成搬运，CPU 该干嘛干嘛；搬运完了用中断通知。'
            '这是「零拷贝（zero-copy）为什么快」的硬件根基。'
        ),
        'concepts': [
            ('DMA 描述符', '一段内存描述一笔传输：src/dst/len/next'),
            ('Scatter-Gather', '链表式描述符，一次 DMA 完成多段不连续传输'),
            ('Cache Coherency 陷阱', 'DMA 改了内存，CPU cache 还是旧值 → 需要 cache flush/invalidate'),
            ('与中断协作', 'DMA 完成后触发中断，CPU 在 ISR 里收尾'),
        ],
        'csdiy_refs': ['source-reading/numa-architecture-精读.md', 'notes/perf-程序员视角-定位与优化.md（zero-copy）'],
    },
    'tinybus': {
        'title': '系统总线协议模拟器',
        'ref': 'PCI / AMBA AXI / Wishbone',
        'tagline': 'master 申请→arbiter 仲裁→读写 slave，多设备共享通道',
        'overview': (
            'tinybus 模拟 SoC 内部的系统总线：多个 master（CPU/DMA）都要访问多个 slave（RAM/ROM/MMIO），'
            '总线仲裁器（Arbiter）决定谁能占用这一拍。这是「为什么硬件是并发」的最小模型。'
        ),
        'concepts': [
            ('Master/Slave', '发起方 vs 响应方，PCI/AXI 的基本角色'),
            ('总线仲裁', '多个 master 同时申请，arbiter 按优先级/轮转裁决'),
            ('事务（Transaction）', '一次读/写 = 申请 + 地址 + 数据 + 应答'),
            ('MMIO', '内存映射 IO：CPU 用 mov 指令就能控制设备'),
        ],
        'csdiy_refs': ['notes/csapp-程序员视角.md（Ch6 IO 设备）'],
    },
}

# 其余 17 个项目用简洁模板
SIMPLE_META = {
    'tinyblob': ('大对象存储', 'S3 / Blob storage',
                 '分桶 + 对象元数据 + 范围读，理解云存储的最小内核',
                 ['Bucket/Object 命名', '元数据（meta）与数据分离', 'Range Get 支持部分下载',
                  '对象不可变性（immutable）']),
    'tinyarp': ('ARP 协议实现', 'arpwatch / Linux neigh',
                'IP→MAC 地址解析，含缓存表 + request/reply',
                ['ARP 缓存表（cache）', '广播 request / 单播 reply', '静态表项 vs 动态学习', '缓存超时']),
    'tinygc': ('垃圾回收器', 'Go G1 / Java G1 / Python gc',
               '标记-清除算法，根集 + 可达性分析',
               ['Root Set（根集）', '可达性分析（Tracing）', 'Mark-Sweep 三色标记', '内存泄漏 = 漏标']),
    'tiny2pc': ('两阶段提交', 'XA / Google Percolator',
                '分布式事务：prepare→commit/abort，含 Saga 补偿',
                ['Coordinator/Participant 角色', 'Prepare 阶段写日志', 'Commit/Abort 全员一致',
                 'Saga 用补偿事务替代回滚']),
    'tinybitcask': ('Bitcask 存储引擎', 'Riak Bitcask',
                    '追加写日志 + 内存 KeyDir，读快写快重启快',
                    ['只追加写（append-only）', 'KeyDir 在内存索引', 'merge 压缩合并', 'Hint File 加速重启']),
    'tinygraph': ('图算法库', 'NetworkX / Boost Graph',
                  'BFS/DFS/Dijkstra/拓扑排序/MST 全套',
                  ['邻接表表示', 'BFS 用队列', 'DFS 用栈/递归', 'Dijkstra 用优先队列',
                   '拓扑排序 = DFS 逆后序', 'MST = Kruskal/Patrimoni']),
    'tinyindex': ('索引结构对比', 'PostgreSQL BRIN / InnoDB',
                  'Hash / Sorted / LSM 三种索引的插入与查询',
                  ['Hash Index: O(1) 查找，不支持范围', 'Sorted Index: 二分查找，支持范围',
                   'LSM Index: 写入快，查询需合并', '索引选择性决定性能']),
    'tinywebsocket': ('WebSocket 协议', 'RFC 6455 / gorilla/websocket',
                      '握手 + 帧编解码，HTTP 升级到双向通信',
                      ['HTTP Upgrade 握手', 'Sec-WebSocket-Accept 计算（SHA1+Base64）',
                       '帧格式：FIN/opcode/mask/payload', '客户端→服务端必须 mask']),
    'tinyseq': ('序列号生成器', 'Twitter Snowflake / ULID',
                '分布式唯一 ID：Snowflake(机器+时间+序号) + ULID',
                ['Snowflake: timestamp(41)+worker(10)+seq(12)', '时钟回拨问题',
                 'ULID: 时间+随机，字典序可排序', 'ID 生成必须无中心']),
    'tinydhcp': ('DHCP 服务器', 'isc-dhcp-server / dnsmasq',
                 'IP 自动分配：discover→offer→request→ack',
                 ['DORA 四步握手', 'Lease（租约）机制', '地址池管理', 'MAC→IP 绑定']),
    'tinyeventloop': ('事件循环', 'libuv / Redis ae / Python asyncio',
                      'call_later/call_soon/register_io 的最小事件循环',
                      ['Ready Queue + Timer Heap', 'IO 多路复用（select/poll/epoll）',
                       '回调式 vs 协程式', 'run_once 单次心跳']),
    'tinypool': ('资源池', 'Java ThreadPool / HikariCP',
                 '线程池 + 连接池，复用昂贵的资源',
                 ['预创建 + 懒加载', 'borrow/return 协议', '空闲超时回收', '连接池 vs 线程池差异']),
    'tinyratelimit': ('限流算法', 'nginx limit_req / Sentinel',
                      '令牌桶 + 滑动窗口 + 漏桶三种限流',
                      ['Token Bucket: 允许突发', 'Sliding Window: 精确计数', 'Leaky Bucket: 强制匀速',
                       '分布式限流需 Redis Lua']),
    'tinysymtab': ('符号表', 'LLVM SymbolTable / ELF .symtab',
                   '作用域栈 + 符号解析，编译器核心数据结构',
                   ['Symbol(name/type/scope/kind)', 'Scope 嵌套（enter/exit）',
                    '符号解析 = 沿作用域栈向上找', '用于类型检查 + 代码生成']),
    'tinyhuffman': ('Huffman 编码', 'Deflate / gzip',
                    '频率驱动的最优前缀编码',
                    ['频率统计 → 优先队列', '构建 Huffman 树', '编码表生成', '压缩率 vs 算术编码']),
    'tinyicmp': ('ICMP 协议', 'ping / traceroute',
                 'echo request/reply + checksum',
                 ['Type/Code 字段', '校验和（一补码求和）', 'Ping 往返时延测量',
                  'Traceroute 用 TTL 递增']),
    'tinyroute': ('路由表', 'Linux FIB / quagga / BIRD',
                  '最长前缀匹配 + 路由聚合',
                  ['CIDR 前缀匹配', '最长前缀优先', '默认路由 0.0.0.0/0', '路由聚合减小表规模']),
}


def gen_p0_readme(name, meta):
    """P0/P1 详细模板"""
    return f"""# {name} · {meta['title']}

> {meta['tagline']}。参照 **{meta['ref']}**。

## 概述

{meta['overview']}

## 核心概念

| # | 概念 | 一句话 |
|---|------|--------|
""" + '\n'.join(f"| {i+1} | **{c[0]}** | {c[1]} |" for i, c in enumerate(meta['concepts'])) + f"""

## 代码结构

{gen_code_table(name)}

## 快速开始

```bash
cd projects/{name}
{'python3 demo.py' if (PROJECTS_DIR / name / 'demo.py').exists() else 'python3 main.py'}
```

## 学习要点

""" + '\n'.join(f"- {c[0]}：{c[1]}" for c in meta['concepts']) + f"""

## 参照真实项目

| tiny | 真实 |
|------|------|
| `{name}` | {meta['ref']} |

## 相关 csdiy 资源

""" + '\n'.join(f"- {r}" for r in meta['csdiy_refs']) + """

---

*本 README 由 gen_readmes.py 自动生成骨架 + 人工填充。*
"""


def gen_simple_readme(name, title, ref, tagline, concepts):
    """P2 简洁模板"""
    files = sorted(PROJECTS_DIR.glob(f'{name}/*.py'))
    file_table = '\n'.join(f"| `{f.name}` | {sum(1 for _ in open(f, errors='ignore'))} 行 | {(open(f, errors='ignore').readline().strip().strip('#').strip()[:60] or '主实现')} |" for f in files)
    return f"""# {name} · {title}

> {tagline}。参照 **{ref}**。

## 概述

`{name}` 是 csdiy 毕业项目之一，用最小可运行的代码演示 **{title}** 的核心机制。

## 核心概念

""" + '\n'.join(f"- {c}" for c in concepts) + f"""

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
{file_table}

## 快速开始

```bash
cd projects/{name}
{'python3 demo.py' if (PROJECTS_DIR / name / 'demo.py').exists() else 'python3 main.py'}
```

## 参照真实项目

| tiny | 真实 |
|------|------|
| `{name}` | {ref} |

---

*本 README 由 gen_readmes.py 生成。代码细节请直接读 main.py。*
"""


def gen_code_table(name):
    """生成代码结构表"""
    files = sorted((PROJECTS_DIR / name).glob('*.py'))
    rows = []
    for f in files:
        loc = sum(1 for _ in open(f, errors='ignore'))
        firstline = open(f, errors='ignore').readline().strip()
        if firstline.startswith('"""') or firstline.startswith("'''"):
            doc = firstline.strip('"\'').strip()[:50]
        else:
            doc = {'main.py': '主入口 + 演示', 'core.py': '核心实现',
                   'isa.py': '指令集定义', 'pipeline.py': '流水线实现',
                   'mmu.py': 'MMU 核心', 'page_table.py': '页表',
                   'tlb.py': 'TLB 缓存', 'mesi.py': 'MESI 协议核心',
                   'demo.py': '演示脚本'}.get(f.name, '实现文件')
        rows.append(f"| `{f.name}` | {loc} | {doc} |")
    return "| 文件 | 行数 | 内容 |\n|------|------|------|\n" + '\n'.join(rows)


def main():
    generated = []

    # P0 + P1 (6 个详细)
    for name, meta in PROJECT_META.items():
        readme = gen_p0_readme(name, meta)
        path = PROJECTS_DIR / name / 'README.md'
        path.write_text(readme, encoding='utf-8')
        generated.append(name)

    # P2 (17 个简洁)
    for name, (title, ref, tagline, concepts) in SIMPLE_META.items():
        readme = gen_simple_readme(name, title, ref, tagline, concepts)
        path = PROJECTS_DIR / name / 'README.md'
        path.write_text(readme, encoding='utf-8')
        generated.append(name)

    print(f"\n✓ 已生成 {len(generated)} 个 README:")
    for n in generated:
        print(f"  projects/{n}/README.md")

    # 统计覆盖率
    total = len(list(PROJECTS_DIR.glob('tiny*')))
    with_readme = sum(1 for d in PROJECTS_DIR.glob('tiny*')
                      if (PROJECTS_DIR / d.name / 'README.md').exists())
    print(f"\n📊 项目 README 覆盖率: {with_readme}/{total} = {with_readme*100//total}%")


if __name__ == '__main__':
    main()

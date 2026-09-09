# 政治类书目知识库 — 工具与使用说明

本目录存放从政治学相关 PDF 书籍中提取的结构化知识库，以及两个交互/命令行工具来检索它。

```
data/political-books-extracted/
├── knowledge_index.json      ← 结构化知识库（核心数据源）
├── knowledge_browser.py      ← 交互式浏览器（本说明的主角）
├── search_knowledge.py       ← 命令行搜索脚本（一次性查询）
└── *.json                    ← 各书原始提取结果（OCR + 全文 + 目录）
```

---

## 1. knowledge_browser.py —— 交互式知识浏览器

一个纯标准库的命令行程序，让你像浏览维基一样在知识库里漫游。

### 启动

```bash
cd /mnt/c/workspace/essence/data/political-books-extracted
python3 knowledge_browser.py
```

> 无任何外部依赖，只用 `json / os / re / random / sys`。  
> 支持 macOS / Linux / Windows（自动启用 Windows ANSI 颜色）。  
> 长列表自动分页，按 **回车** 翻页，按 **q** 返回。

### 主菜单功能

| 选项 | 功能 | 说明 |
|------|------|------|
| **1** | 搜索知识 | 输入关键词，可按类型过滤（全部/定义/命题/数据/案例），关键词红字高亮，显示书名+页码+原文 |
| **2** | 按主题浏览 | 六大主题分类：央地关系 · 财政与经济 · 合法性与政治 · 国家与社会 · 历史演变 · 国际关系 |
| **3** | 按书籍浏览 | 选书后看：目录 / 核心定义 / 核心命题 / 关键数据 / 关键案例 |
| **4** | 概念对照 | 输入概念名（如「权力」「合法性」），看它在不同书里如何被定义和使用 |
| **5** | 统计总览 | 总书数/字数/条目数、概念频率 TOP20、主题分布、数据类型分布、各书条目分布 |
| **6** | 随机发现 | 随机抽一条命题/数据/案例，用于偶然发现（serendipity） |
| **0** | 退出 | |

### 使用示例

**搜索「土地财政」的全部内容：**
```
请选择 > 1
关键词: 土地财政
类型: 1=全部  2=定义  3=命题  4=数据  5=案例
选择 [1]:          ← 回车默认「全部」
```
会依次列出：相关概念定义 → 命题论断 → 数据 → 案例 → 跨书对照。

**看「央地关系」主题：**
```
请选择 > 2
选择主题: 1        ← 央地关系
```

**对比「权力」在不同书中的定义：**
```
请选择 > 4
输入概念名: 权力
```
会按书分组，显示周雪光、周黎安、周飞舟各自如何使用「权力」一词。

---

## 2. search_knowledge.py —— 命令行一次性搜索

适合写脚本、做笔记时快速查一条。

```bash
# 全文搜索
python3 search_knowledge.py "行政发包制"

# 按类型过滤
python3 search_knowledge.py "土地财政"   --type definition     # 只看定义
python3 search_knowledge.py "运动式治理" --type proposition    # 只看命题
python3 search_knowledge.py "GDP"        --type data           # 只看数据
python3 search_knowledge.py "浙江村"     --type case           # 只看案例

# 跨书对照（看一个概念在多少本书里出现）
python3 search_knowledge.py "合法性" --cross-book
python3 search_knowledge.py "权力"   --cross-book --top 5

# 按书过滤
python3 search_knowledge.py "财政" --book "以利为利"

# 看统计
python3 search_knowledge.py --stats
```

类型别名：`definition/定义/概念` · `proposition/命题/论断` · `data/数据` · `case/案例`。

---

## 3. 知识库结构（knowledge_index.json）

```jsonc
{
  "metadata": {                       // 元数据
    "total_books": 15,                //   书数
    "total_chars": 882784,            //   总字数
    "total_entries": 4407,            //   总条目
    "sources": [ ... ],               //   来源书单
    "entry_counts": { ... }           //   各类条目数
  },
  "concepts": [                       // 概念定义
    { "concept": "改革",
      "definitions": [{ "book","author","page","text" }],
      "mentions":     [{ "book","count","context" }],
      "def_count": 22, "mention_count": 8 }
  ],
  "propositions": [                   // 理论命题/论断
    { "book","author","page","text","theme" }
  ],
  "data_points": [                    // 关键数据
    { "book","page","text","type","source_section" }
  ],
  "cases": [                          // 案例
    { "name","book","author","page","summary" }
  ],
  "cross_book_index": [               // 跨书概念对照
    { "concept","keyword","book","count","context","total_books" }
  ]
}
```

---

## 4. 重建知识库

如果原始 PDF 有更新，可重新提取并构建索引：

```bash
# 1) OCR 提取（已有 ocr_*.json 可跳过）
python3 ocr_batch.py          # 或 ocr_parallel.py / ocr_fast.py

# 2) 结构化提取（生成各书 *.json）
python3 parallel_extract.py   # 或 extract_full.py

# 3) 构建统一索引
python3 build_knowledge_index.py
```

构建完成后 `knowledge_browser.py` 与 `search_knowledge.py` 会自动读取最新索引。

---

## 5. 内容范围

知识库当前覆盖 **15 本书 / 约 88 万字**：

- 周雪光《中国国家治理的制度逻辑》
- 周黎安《转型中的地方政府》
- 《习近平谈治国理政》（第一/二/三卷）
- 周飞舟《以利为利》
- 黄奇帆《分析与思考》
- 孙萍《过渡劳动》
- 波普尔《历史决定论的贫困》
- 《陈云文选》（第一/二/三卷）
- 钱穆国学作品集（7 部合集）

主题横跨：央地关系、财政经济、政治合法性、国家治理、历史制度演变、国际关系。

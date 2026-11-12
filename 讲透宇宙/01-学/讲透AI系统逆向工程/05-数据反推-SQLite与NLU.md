# 05 · 数据反推：SQLite 与 NLU

> 端侧 AI 系统里有大量"非模型"数据——SQLite 数据库、NLU 规则表、配置 JSON。这些数据**通常不加密、不混淆**，是逆向的最容易突破口。
>
> 核心思路：**能从数据库反推的，不要去反编译代码**。这一章讲透 SQLite 全量 dump、跨 APK 一致性比对、NLU tag_pattern 反推——1 小时通常能拿 80% 的语义信息。

---

## 一、为什么数据反推 ROI 最高

| 维度 | 数据反推 | 模型反推 | native 反推 |
|------|---------|---------|------------|
| 工作量 | 1 小时 | 半天-1 天 | 数天-数周 |
| 防御 | 几乎无 | 加密 / 量化 | stripped / OLLVM |
| 工具复杂度 | sqlite3 命令行 | PyTorch + vtable walker | IDA + LLM |
| 信息密度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 误报率 | 低 | 中 | 高 |

**核心铁律**：**永远先 dump 所有数据库**。这一步不到 1 小时，但决定后面所有方向。

---

## 二、SQLite 全量 dump

### 2.1 找所有 .db 文件

```bash
# 在 APK 解包后
find apk_unpacked -type f -name "*.db" -exec ls -lah {} \;

# 或在 root 设备上 dump app 数据
adb shell "run-as com.xxx.target find /data/data/com.xxx.target -name '*.db'"
# 或带 root
adb shell "find /data/data/com.xxx.target -name '*.db' 2>/dev/null"
adb pull /data/data/com.xxx.target/databases/foo.db .
```

### 2.2 dump 单个 db 的完整 schema

```bash
sqlite3 foo.db ".schema"
# 输出所有 CREATE TABLE / CREATE INDEX 语句
```

```bash
sqlite3 foo.db ".tables"
# 输出所有表名
```

### 2.3 dump 表的样本数据

```bash
sqlite3 foo.db "SELECT * FROM tag_pattern LIMIT 5"
# 看 5 行样本,理解字段含义
```

### 2.4 自动化全量解析（Python）

```python
import sqlite3
import json
from pathlib import Path

def parse_db(db_path):
    """全量解析一个 SQLite,返回所有表的 schema + 样本"""
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    
    result = {'file': str(db_path), 'tables': {}}
    
    tables = [r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()]
    
    for t in tables:
        info = {'schema': None, 'count': 0, 'samples': []}
        
        # CREATE TABLE 语句
        schema_sql = db.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (t,)
        ).fetchone()
        info['schema'] = schema_sql[0] if schema_sql else None
        
        # 行数
        info['count'] = db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        
        # 前 3 行样本
        rows = db.execute(f"SELECT * FROM {t} LIMIT 3").fetchall()
        info['samples'] = [dict(r) for r in rows]
        
        result['tables'][t] = info
    
    db.close()
    return result

# 解析所有 db
all_dbs = list(Path('.').rglob('*.db'))
for db_path in all_dbs:
    result = parse_db(db_path)
    print(f"\n=== {db_path} ===")
    for t, info in result['tables'].items():
        print(f"  表 {t} ({info['count']} 行)")
        print(f"    schema: {info['schema']}")
        print(f"    sample: {info['samples'][0] if info['samples'] else '?'}")
```

---

## 三、跨 APK 一致性比对 ★

一个厂商通常有多个 APK（主 app + 服务 app + 助手 app），它们都包含同类的 db。**比对 db 内容**能挖出大量信息。

### 3.1 同 db 跨 APK 版本

```python
# 假设你有同一 db 在 4 个 APK 副本里
# (主 app, 主 app 的 _data, 助手 app, 助手 app 的 _data)

variants = {
    'AIService': Path('AIService__nlu.db'),
    'AIService_data': Path('AIService_data__nlu.db'),  # 通常 _data 版本更新
    'Assistant': Path('Assistant__nlu.db'),
    'Assistant_data': Path('Assistant_data__nlu.db'),
}

# 比对同一表的行数
table = 'tag_pattern'
counts = {}
for name, path in variants.items():
    db = sqlite3.connect(path)
    counts[name] = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    db.close()

print(counts)
# 典型输出（举例）: {'AIService': 50000, 'AIService_data': 50000,
#                    'Assistant': 50000, 'Assistant_data': 50000}
# → 完全一致:说明这个表是核心共享数据
```

### 3.2 发现"更新版本"

```python
# 某些表在不同 APK 里行数不同 → 业务定制
# 例如 sms_pattern:
#   AIService: 8797 行
#   AIService_data: 9663 行 ← 更新
#   Assistant: 7998 行 ← 业务定制(更少)
#   Assistant_data: 9663 行 ← 与 AIService_data 一致

# 结论:
# 1. _data 副本是"主版本"(行数最多)
# 2. 不同 APK 有不同业务定制
# 3. 选 _data 版本作为还原基准
```

### 3.3 比对内容差异（不只是行数）

```python
# 比较两份 db 的同一表,diff 出新增/删除/修改的行
import sqlite3

def diff_tables(db1_path, db2_path, table, key_column='id'):
    db1 = sqlite3.connect(db1_path)
    db2 = sqlite3.connect(db2_path)
    
    rows1 = {r[0]: r[1:] for r in db1.execute(f"SELECT {key_column}, * FROM {table}")}
    rows2 = {r[0]: r[1:] for r in db2.execute(f"SELECT {key_column}, * FROM {table}")}
    
    added = set(rows2) - set(rows1)
    removed = set(rows1) - set(rows2)
    modified = [k for k in set(rows1) & set(rows2) if rows1[k] != rows2[k]]
    
    print(f'+{len(added)}  -{len(removed)}  ~{len(modified)}')
    return added, removed, modified
```

---

## 四、NLU tag_pattern 反推 ★

这是数据反推最有价值的应用——**从 NLU 数据库反推意图体系**。

### 4.1 典型 NLU 数据库结构

```sql
CREATE TABLE tag_pattern (
    key TEXT,           -- 中文模式（如"打开设置"）
    val TEXT            -- 标签值
);

CREATE TABLE intervention_data (
    query TEXT,         -- 特殊 query
    intent TEXT         -- 强制 intent
);
```

### 4.2 反推 tag_pattern.val 格式

```python
import sqlite3
from collections import Counter

db = sqlite3.connect('nlu.db')
vals = [r[0] for r in db.execute("SELECT DISTINCT val FROM tag_pattern")]

# 看 val 的常见格式
format_patterns = Counter()
for v in vals:
    # 假设 v = "1_5$" 之类的格式
    parts = v.rstrip('$').split('_')
    if len(parts) >= 2 and all(p.isdigit() for p in parts):
        format_patterns['scene_subIntent$'] += 1

print(format_patterns)
# {'scene_subIntent$': 977}  ← 977 种 unique tag
```

### 4.3 反推 scene_id ↔ scene_name

```python
# 对每个 val "scene_sub$" 反推 scene
scenes = {}
for v in vals:
    parts = v.rstrip('$').split('_')
    scene_id = int(parts[0])
    sub_id = int(parts[1])
    scenes.setdefault(scene_id, []).append(sub_id)

# intervention_data 表通常有 6 个 (query, intent) 对
# 这 6 个 intent 名通常是 scene 名(如 "system", "setting", "phone")
intervention = list(db.execute("SELECT * FROM intervention_data"))
print(intervention)
# [('亮度', 'setting.brightness'), ('打开WiFi', 'setting.wifi'), ...]

# 每个 scene 有几个 subIntent? 看分布
for scene_id, subs in sorted(scenes.items()):
    print(f'scene {scene_id}: {len(subs)} subIntents (范围 {min(subs)}-{max(subs)})')
# scene 1: 12 subIntents (1-12)  ← 可能是 system(主功能)
# scene 2: 6 subIntents (13-18)  ← 可能是 setting
# ...
```

### 4.4 LLM 辅助语义对齐

把反推出的 scene 表喂给 LLM，让它根据 subIntent 涉及的中文 key 推 scene 名：

```python
# 把每个 scene_id 涉及的所有 key 收集起来
scene_keys = {}
for key, val in db.execute("SELECT key, val FROM tag_pattern"):
    scene_id = int(val.rstrip('$').split('_')[0])
    scene_keys.setdefault(scene_id, []).append(key)

# 喂给 LLM
prompt = "下面是 13 个 scene 的中文 pattern key,请推断每个 scene 的语义:\n"
for scene_id, keys in sorted(scene_keys.items()):
    prompt += f"\nscene {scene_id} ({len(keys)} keys): {keys[:5]}\n"

# 用 GLM-4 / Claude 跑
# LLM 会根据 key 的语义("亮度调到" → setting,"打电话给" → phone)推 scene 名
```

---

## 五、配置 JSON 反推

除了 SQLite，端侧 AI 还有大量配置 JSON：

```bash
find apk_unpacked -type f -name "*.json" -exec ls -lah {} \;
```

典型配置：
- `config.yaml` — 模型路径、SDK 配置
- `labels.json` — 分类标签表
- `mapping.json` — 业务映射

读这些 JSON 通常**不需要任何工具**——`cat` 出来即可。

```python
import json
from pathlib import Path

for json_path in Path('apk_unpacked/assets').rglob('*.json'):
    try:
        data = json.loads(json_path.read_text())
        print(f'\n=== {json_path} ===')
        if isinstance(data, dict):
            print(f'  keys: {list(data.keys())[:10]}')
        elif isinstance(data, list):
            print(f'  list of {len(data)} items, first: {data[0] if data else None}')
    except Exception as e:
        print(f'  解析失败: {e}')
```

---

## 六、SMS / 卡片正则反推

端侧 AI 系统常内置 SMS 解析（用于智能通知、生活场景识别）：

```sql
CREATE TABLE sms_pattern (
    pattern TEXT,        -- 正则或模板
    label TEXT,          -- 类别(航班/火车/快递)
    extractor TEXT       -- 信息提取规则
);
```

dump 出来看几行，就能反推：
- 厂商关注哪些类型的 SMS
- 用什么正则提取信息
- 业务场景的覆盖范围

---

## 七、自动化：写一个 db 全量解析工具

完整工具模板见 `experiments/05_sqlite_dump.py`。核心功能：
1. 递归找所有 .db
2. 每张表 schema + 样本 + 全量统计
3. 跨 APK 副本一致性比对
4. 落盘综合报告（JSON + Markdown）

---

## 八、陷阱总结

| 陷阱 | 症状 | 解法 |
|------|------|------|
| **加密的 SQLite** | `.tables` 报错"file is encrypted" | 用 SQLCipher 解（找 key），或跳过这层走别的 |
| **Room 生成 schema** | schema 里大量 `room_master_table` 等元表 | 过滤掉 `sqlite_sequence`、`room_master_table`、`android_metadata` |
| **WAL 模式** | 主 db 文件少行，但 -wal 文件大 | 同时 dump 主 db + -wal + -shm，合并 |
| **行数对不上** | 同表跨 APK 行数差异大 | 见 §三，可能是业务定制 |
| **字段名混淆** | 字段名是 `a` `b` `c` | 看周围的 CREATE TABLE 注释（ProGuard 不破坏注释）|

---

## 📌 下一步

- **想学 NLU 资源（marisa / AC）反推** → [03-二进制格式逆向](03-二进制格式逆向.md)
- **想学 SQLite 加进 PyTorch** → [06-模型恢复](06-模型恢复.md)
- **跑实验** → `experiments/05_sqlite_dump.py`

> 📝 **本章练习**：
> 1. 写一个自造的 SQLite db（5 张表，每张 10-100 行），用本章节的脚本 dump 出 schema + 样本。
> 2. 模拟"跨 APK 副本"——复制你的 db，改几行，用 diff_tables 比对。
> 3. **思考题**：为什么厂商不加密 NLU 数据库？（提示：性能 / 兼容性 / 加密 key 难管理 / 法律合规）

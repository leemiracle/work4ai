# 02 · 静态分析：DEX 反编译

> Dalvik 字节码（DEX）是 Android 应用的核心。这一章讲透**如何从混淆过的 DEX 里挖出最大信息**——不只看 Java 代码，还要挖 annotation / String table / 字段类型，这些都是反逆向绕不开的细节。
>
> 核心工具：**androguard**（Python 自动化）+ **JADX**（GUI 可视化）+ 手写 DEX header parser（最底层）。

---

## 一、DEX 文件结构

一个 DEX 文件长这样：

```
┌────────────────────────────────────────────┐
│ DEX header (112 bytes)                     │
│ - magic: "dex\n035\0"                      │
│ - checksum                                  │
│ - string_ids_size, string_ids_off          │ ← 字符串表
│ - type_ids_size, type_ids_off              │ ← 类型表
│ - proto_ids_size, proto_ids_off            │ ← 方法签名表
│ - field_ids_size, field_ids_off            │ ← 字段表
│ - method_ids_size, method_ids_off          │ ← 方法表
│ - class_defs_size, class_defs_off          │ ← 类定义表 ★
│ - data                                     │
└────────────────────────────────────────────┘
```

**关键洞察**：DEX 的所有"语义"都集中在 8 张表里——string / type / proto / field / method / class_def / data / map。**只要能解析这 8 张表就能拿到所有信息**，不需要真的反编译 bytecode。

---

## 二、用 androguard 解析 DEX

androguard 是 Python 库，最适合**自动化批量分析**。

### 2.1 安装

```bash
pip install androguard==3.4.0a1  # 或更新版本
```

### 2.2 列出所有类

```python
from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes.dvm import DalvikVMFormat

a = APK('target.apk')
for dex_bytes in a.get_all_dex():
    d = DalvikVMFormat(dex_bytes)
    for cls in d.get_classes():
        print(cls.get_name())  # Lcom/xxx/target/Foo;
```

### 2.3 列出类的字段和方法

```python
for cls in d.get_classes():
    if 'target/Foo' in cls.get_name():
        print(f'=== {cls.get_name()} ===')
        print('Fields:')
        for field in cls.get_fields():
            print(f'  {field.get_descriptor()} {field.get_name()}')
        print('Methods:')
        for method in cls.get_methods():
            print(f'  {method.get_descriptor()} {method.get_name()}')
```

### 2.4 找特定字符串的 xref（引用）

```python
# 找谁引用了 "subIntentInverse" 这个字符串
target_string = 'subIntentInverse'
for cls in d.get_classes():
    for method in cls.get_methods():
        code = method.get_code()
        if not code:
            continue
        for inst in code.get_bc().get_instructions():
            op_value = inst.get_output() if hasattr(inst, 'get_output') else str(inst)
            if target_string in str(inst):
                print(f'{cls.get_name()}.{method.get_name()} 引用了 {target_string}')
```

---

## 三、Annotation 解析 ★（最有价值）

### 3.1 为什么 annotation 重要

Android 字段的真实类型（特别是泛型 `List<Foo>`）**不写在字段定义里**，而是写在 `@dalvik/annotation/Signature` 注解里。如果只读字段定义，你看到的是 `List`；读 annotation 才知道是 `List<NoteSlot>`。

### 3.2 三种关键 annotation

| 注解 | 用途 | 反推价值 |
|------|------|---------|
| `@dalvik/annotation/Signature` | 泛型签名 | ⭐⭐⭐⭐⭐ 真实类型 |
| `@dalvik/annotation/Throws` | throws 声明 | ⭐⭐ 异常类型 |
| `@dalvik/annotation/EnclosingClass` | 内部类的外部类 | ⭐⭐ 类层级 |
| `@dalvik/annotation/MemberClasses` | 类的内部类列表 | ⭐⭐ 类层级 |
| `@androidx/annotation/Keep` | 防 ProGuard 混淆 | ⭐⭐⭐ 公开 API |
| `@SerializedName("xxx")` | Gson 字段映射 | ⭐⭐⭐ 序列化名 |
| `@Entity` / `@PrimaryKey` | Room ORM | ⭐⭐⭐ 数据库 schema |

### 3.3 用 androguard 解析 annotation

```python
for cls in d.get_classes():
    if 'entitystore' not in cls.get_name():
        continue
    print(f'\n=== {cls.get_name()} ===')
    
    # 类级 annotation
    for ann in cls.get_annotations():
        print(f'  Class @{ann.get_type()}')
    
    # 字段级 annotation
    for field in cls.get_fields():
        for ann in field.get_annotations():
            print(f'  Field {field.get_name()} @{ann.get_type()}')
            # 如果是 Signature, dump value
            if 'Signature' in ann.get_type():
                # 注意:annotation value 可能被混淆!见 §3.4
                for elem in ann.get_elements():
                    print(f'    sig = {elem.get_value()}')
```

### 3.4 Signature 混淆陷阱 ★

**问题**：厂商可能故意混淆 Signature 注解的 value——`string_idx` 指向无关字符串（如 `"\nStack Trace: "`）。

**症状**：
```python
# 解析 NoteBean.noteSlots 的 Signature
# 期望: Ljava/util/List<Lcom/xxx/NoteSlot;>;
# 实际: '\nStack Trace: '    ← 被混淆了!
```

**识别**：所有 Signature value 都指向无关字符串（约 100% 命中率说明是混淆，不是巧合）。

**对策**：走 Frida 运行时反射（详见 [04 章](04-动态插桩-Frida.md)）：

```javascript
Java.perform(function() {
    var NoteBean = Java.use('com.xxx.entitystore.NoteBean');
    var field = NoteBean.class.getDeclaredField('noteSlots');
    var type = field.getGenericType();  // 真实 ParameterizedType
    console.log('真实泛型:', type.toString());  // java.util.List<com.xxx.NoteSlot>
});
```

> 📌 **铁律**：**静态 annotation 拿到的信息要永远用动态反射验证一次**。Signature 混淆是常见陷阱。

---

## 四、String table xref 分析

DEX 的 `string_ids` 表是**所有字符串常量**。逐个看 xref（谁引用了它），能挖到很多信息。

### 4.1 找业务错误信息（暴露类间关系）

```python
# 业务校验失败时常 throw new IllegalArgumentException("foo is null")
# 这些字符串暴露了类间关系
for s in d.get_strings():
    if 'is null' in s or 'invalid' in s.lower():
        print(s)
```

典型输出：
```
momentType or outerId is null
noteId or slotId is null
personBeanList is empty
```

这些字符串**直接告诉你字段名 + 业务约束**。

### 4.2 找 SQL 语句（暴露 schema）

```python
for s in d.get_strings():
    if s.upper().startswith('CREATE TABLE') or s.upper().startswith('SELECT'):
        print(s)
```

Room ORM 编译时把 SQL 写进字符串表——这是最直接的 schema 来源。

### 4.3 找日志 tag（暴露类名）

```python
for s in d.get_strings():
    if len(s) < 30 and s.replace('.', '_').replace('/', '_').isidentifier():
        # 可能是 Log tag(常等于类名)
        print(s)
```

---

## 五、JADX 工作流

JADX 是 GUI 工具，适合**人工探索**。

### 5.1 全局搜索

`Ctrl+Shift+F` 全文搜索所有 dex。常用搜索词：
- `Intent` — 找 Activity / Service 启动点
- `native ` — 找 native 方法声明
- `@Override` — 找 override 关系
- `import` — 找第三方依赖

### 5.2 跟 Method xref

选中一个方法 → `Ctrl+左键` → 看哪里调用了它。这对**追踪调用链**极有用。

### 5.3 JADX-GPT 自动重命名

选中混淆类 → 右键 → "Rename with AI" → LLM 给建议名。

---

## 六、手写 DEX header parser（最底层）

如果想绕过 androguard（偶尔它解析某些 APK 会崩），可以手写最小 parser：

```python
import struct

def parse_dex_header(path):
    with open(path, 'rb') as f:
        data = f.read(112)
    
    magic = data[:8]
    assert magic[:4] == b'dex\n', f'不是 dex 文件: {magic}'
    
    # 解析关键字段
    fields = {}
    fields['version'] = magic[4:7].decode()
    fields['checksum'] = struct.unpack_from('<I', data, 8)[0]
    fields['string_ids_size'] = struct.unpack_from('<I', data, 0x38)[0]
    fields['string_ids_off'] = struct.unpack_from('<I', data, 0x3c)[0]
    fields['class_defs_size'] = struct.unpack_from('<I', data, 0x60)[0]
    fields['class_defs_off'] = struct.unpack_from('<I', data, 0x64)[0]
    
    return fields

print(parse_dex_header('classes.dex'))
# {'version': '039', 'string_ids_size': 5823, 'class_defs_size': 421, ...}
```

ULEB128 解码（DEX 大量用）：

```python
def read_uleb128(data, offset):
    """Unsigned LEB128 解码"""
    result = 0
    shift = 0
    while True:
        byte = data[offset]
        offset += 1
        result |= (byte & 0x7f) << shift
        if byte & 0x80 == 0:
            break
        shift += 7
    return result, offset
```

---

## 七、跨 dex 引用追踪

现代 APK 通常多 dex（classes.dex / classes2.dex / ...）。一个类的字段类型可能在另一个 dex：

```python
# 把所有 dex 的所有类建成索引
all_classes = {}  # {class_name: dex_id}
for i, dex_bytes in enumerate(apk.get_all_dex()):
    d = DalvikVMFormat(dex_bytes)
    for cls in d.get_classes():
        all_classes[cls.get_name()] = i

# 查找跨 dex 引用
for i, dex_bytes in enumerate(apk.get_all_dex()):
    d = DalvikVMFormat(dex_bytes)
    for cls in d.get_classes():
        for field in cls.get_fields():
            field_type = field.get_descriptor()
            if field_type.startswith('L') and field_type in all_classes:
                if all_classes[field_type] != i:
                    print(f'跨 dex: {cls.get_name()}.{field.get_name()} 引用 {field_type} (在 dex {all_classes[field_type]})')
```

---

## 八、实证：自造 Bean + 反编译

```bash
cd 讲透AI系统逆向工程/experiments
python 02_dex_parse.py
```

实验内容：
1. 用 `javac` 编译一个简单 Bean 类（`NoteBean.java`，含 `List<NoteSlot>` 字段 + `@Keep`）
2. 用 `d8` 编译成 dex
3. 用 androguard 反编译
4. 比较：字段名 / 字段类型 / Signature value / @Keep annotation

---

## 📌 下一步

- **想学二进制格式** → [03-二进制格式逆向](03-二进制格式逆向.md)
- **想学动态 hook** → [04-动态插桩-Frida.md)
- **跑实验** → `experiments/02_dex_parse.py`

> 📝 **本章练习**：
> 1. 写一个简单 Java 类（含 List/Map 泛型 + @Keep），编译成 dex，用 androguard 解析。验证泛型是否在 Signature annotation 里。
> 2. 在你合法持有的 APK 里搜索 SQL 字符串，看能挖到多少 schema 信息。
> 3. **思考题**：为什么 Java 反射 API 能拿到真实泛型（即使 Signature 被混淆）？泛型信息在 JVM 里以什么形式存在？（提示：ParameterizedType / Class file 的 Signature attribute）

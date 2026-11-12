# 04 · 动态插桩：Frida

> 静态分析够了 80% 的信息，剩下 20% 必须**动态**——让 app 跑起来，看真实数据流。这一章讲透 Frida：Java 层 hook、Native 层 hook、Stalker 全 trace，以及绕过反 Frida 检测的常用技巧。
>
> 核心思路：**与其反编译看代码，不如让代码自己告诉你答案**。

---

## 一、为什么需要动态分析

| 静态够的 | 动态必备的 |
|---------|----------|
| 字段名、类层级、方法签名 | 字段的**运行时真实值** |
| 字节码逻辑 | Native 函数的**输入输出 tensor** |
| Schema 字段顺序 | 加密 key、解密后的明文 |
| 公开 API 表 | 反射调用的真实类（绕混淆） |
| Annotation 元数据（可能被混淆）| 真实泛型 / 真实类型 |

**核心铁律**：静态可以骗你（混淆、加密、加固），动态骗不了你（JVM 必须知道真相才能运行）。

---

## 二、Frida 基础

### 2.1 安装

```bash
# 主机端
pip install frida-tools

# 设备端（root 真机）
# 方法1: frida-server（需要 root）
adb push frida-server-arm64 /data/local/tmp/
adb shell "chmod +x /data/local/tmp/frida-server-arm64 && /data/local/tmp/frida-server-arm64 &"

# 方法2: frida-gadget（不需要 root，但需要重打包 APK）
# 把 libfrida-gadget.so 注入到 APK，重新签名
```

### 2.2 第一个 hook

```bash
frida -U -n "com.xxx.target" -l hook.js
# -U: USB 设备
# -n: attach 已运行的进程
# -l: 加载 JS 脚本
```

```javascript
// hook.js
Java.perform(function() {
    var Foo = Java.use('com.xxx.target.Foo');
    Foo.bar.implementation = function(arg) {
        console.log('bar() called with:', arg);
        var result = this.bar(arg);  // 调用原方法
        console.log('bar() returned:', result);
        return result;
    };
});
```

---

## 三、Java 层 hook 模式

### 3.1 Hook 方法（最常用）

```javascript
Java.perform(function() {
    var Target = Java.use('com.xxx.Target');
    
    // 重写方法
    Target.foo.overload('java.lang.String').implementation = function(input) {
        console.log('[+] Target.foo("' + input + '")');
        var output = this.foo(input);
        console.log('[=] returned:', output);
        return output;
    };
    
    // 多 overload 时必须指定参数类型
    Target.foo.overload('int', 'boolean').implementation = function(a, b) {
        // ...
    };
});
```

### 3.2 Hook 构造函数

```javascript
var Target = Java.use('com.xxx.Target');
Target.$init.overload('java.util.List').implementation = function(list) {
    console.log('[+] new Target(list=' + list + ')');
    return this.$init(list);
};
```

### 3.3 反射 dump 字段类型（Signature 混淆对策 ★）

```javascript
Java.perform(function() {
    var NoteBean = Java.use('com.xxx.NoteBean');
    var fields = NoteBean.class.getDeclaredFields();
    
    fields.forEach(function(field) {
        var name = field.getName();
        var type = field.getType().getName();        // 申明类型
        var gtype = field.getGenericType().toString(); // 真实泛型
        
        console.log(name + ': ' + type + ' | generic: ' + gtype);
    });
});
// 输出:
// noteSlots: java.util.List | generic: java.util.List<com.xxx.NoteSlot>
// slotIdToImageVectorsMap: java.util.Map | generic: java.util.Map<java.lang.Long, com.xxx.ImageVectorMemory>
```

这是反 Signature 混淆的**最强工具**。

### 3.4 Hook JSONObject.put 抓业务对象

```javascript
var JSONObject = Java.use('org.json.JSONObject');
JSONObject.put.overload('java.lang.String', 'java.lang.Object').implementation = function(key, value) {
    if (key === 'subIntentInverse' || key === 'intent') {
        console.log('[JSONObject.put] ' + key + ' = ' + value);
    }
    return this.put(key, value);
};
```

> 📌 **铁律**：hook 通用 API（JSONObject / HashMap / Log）+ 加 if 过滤，比逐个 hook 业务方法更省事。

---

## 四、Native 层 hook

### 4.1 Hook 导出函数

```javascript
var nativeFunc = Module.findExportByName('libtarget.so', 'encrypt');
Interceptor.attach(nativeFunc, {
    onEnter: function(args) {
        // args[0], args[1], ... 是参数（pointer）
        console.log('[encrypt] input:', args[0].readByteArray(16));
        this.output_ptr = args[1];  // 保存 output 指针, onLeave 用
    },
    onLeave: function(retval) {
        console.log('[encrypt] output:', this.output_ptr.readByteArray(16));
    }
});
```

### 4.2 Hook 未导出函数（要找偏移）

```javascript
// 通过符号查找（如果未 strip）
var addr = Module.findExportByName('libtarget.so', 'target_func');

// 通过偏移（strip 后）
var libtarget = Process.findModuleByName('libtarget.so');
var func_addr = libtarget.base.add(0x12340);  // IDA/Ghidra 看到的偏移

Interceptor.attach(func_addr, { /* ... */ });
```

### 4.3 Dump 内存（拿 tensor / 模型权重）

```javascript
// 假设 nativeForward 第一个参数是 input tensor 指针
Interceptor.attach(Module.findExportByName(null, 'nativeForward'), {
    onEnter: function(args) {
        var tensor_ptr = args[1];
        // 假设是 float[128]
        var floats = [];
        for (var i = 0; i < 128; i++) {
            floats.push(tensor_ptr.add(i * 4).readFloat());
        }
        console.log('[input tensor]:', floats);
    }
});
```

这是**模型权重提取**的最强工具（参考 [06 章](06-模型恢复.md) 路线 3 KD 蒸馏）。

---

## 五、Stalker：全指令 trace

Stalker 跟踪一个线程执行的**每一条 ARM64 指令**——用于深度分析。

```javascript
var tid = Process.getCurrentThreadId();
Stalker.follow(tid, {
    events: { call: true },
    onCallSummary: function(summary) {
        // summary = {函数地址: 调用次数}
        for (var addr in summary) {
            console.log(addr + ': ' + summary[addr] + ' calls');
        }
    }
});
```

⚠️ Stalker 极重（性能降 100x+），只在必要时用。

---

## 六、Waydroid：不需要真机的动态分析

Waydroid 是 Linux 上的 Android 容器，能跑 arm64 APK（需要 Houdini translation）。

### 6.1 安装

```bash
# Linux 主机
sudo apt install waydroid
sudo waydroid init -s GAPPS  # 带 GApps
```

### 6.2 跑 arm64 APK

```bash
# 安装 arm64 APK（Waydroid 会自动翻译）
waydroid app install target.apk

# 启动
waydroid app launch com.xxx.target

# attach Frida
frida -U -n com.xxx.target -l hook.js
```

### 6.3 frida-gadget 重打包

如果 app 不让你 attach（反 Frida），用 gadget 重打包：

```bash
# 工具: objection
pip install objection
objection patchapk -s target.apk
# 产出: target.objection.apk（自动注入 frida-gadget）

# 安装到 Waydroid
waydroid app install target.objection.apk

# 启动后,Frida 自动注入
frida -U Gadget -l hook.js
```

---

## 七、反 Frida 检测及对策

### 7.1 检测手段

| 检测方式 | 原理 |
|---------|------|
| 扫 `/proc/self/maps` | 找 frida-agent / libfrida-gadget |
| 端口扫描 | frida-server 默认 port 27042 |
| 进程名扫描 | 找 frida-server / frida-helper |
| `pthread_create` 数量异常 | Frida 注入会多线程 |
| `isDebuggerAttached` | ptrace 检测 |
| `dlopen` 检测 | Frida 注入会用 dlopen |

### 7.2 对策

| 检测 | 对策 |
|------|------|
| maps 扫描 | gadget 改名（`libhelper.so`）|
| 端口扫描 | frida 改 port (`frida-server -l 0.0.0.0:8888`) |
| 进程名 | frida-server 改名 |
| ptrace | hook ptrace 返回 0 |

```javascript
// 反 anti-Frida 的 hook 示例
Interceptor.attach(Module.findExportByName(null, 'ptrace'), {
    onLeave: function(retval) {
        retval.replace(0);  // 让 ptrace 总是返回 0
    }
});
```

### 7.3 高级对抗：Magisk + Zygisk + Shamiko

root 设备 + Magisk + Zygisk 模块（如 Shamiko / LSPosed）可以隐藏 root + Frida 痕迹。这是绕过反检测的终极武器，但**需要合法持有的设备**。

---

## 八、KD 蒸馏数据采集（实战模式）

把 Frida hook 推理 API，收集 (in, out) 对，喂给 KD 蒸馏（[06 章](06-模型恢复.md)）。

```javascript
// frida_vendor_trace.js
var pairs = [];

Interceptor.attach(Module.findExportByName('libtarget.so', 'nativeForward'), {
    onEnter: function(args) {
        this.input = readTensor(args[1], 150);    // 输入 tensor 长度（150 = install 周数，举例）
    },
    onLeave: function(retval) {
        var output = readTensor(retval, 800);     // 输出 tensor 长度（800 = multi-label 维度，举例）
        pairs.push({input: this.input, output: output});
        if (pairs.length % 100 === 0) {
            send({type: 'pairs', data: pairs.slice(-100)});  // 发给 host
        }
    }
});

function readTensor(ptr, len) {
    var arr = [];
    for (var i = 0; i < len; i++) {
        arr.push(ptr.add(i * 4).readFloat());
    }
    return arr;
}
```

跑 ~1000 次真实推理，收集 1000+ 对 → 蒸馏训练。

---

## 九、Frida Python 绑定（自动化）

```python
import frida
import time

session = frida.get_usb_device().attach('com.xxx.target')
script = session.create_script(open('hook.js').read())

output = []
def on_message(message, data):
    if message['type'] == 'send':
        output.append(message['payload'])

script.on('message', on_message)
script.load()

time.sleep(60)  # 跑 60 秒收集
session.detach()

import json
with open('frida_output.json', 'w') as f:
    json.dump(output, f)
```

---

## 📌 下一步

- **想学 SQLite 反推** → [05-数据反推](05-数据反推-SQLite与NLU.md)
- **想看 KD 蒸馏完整流程** → [06-模型恢复](06-模型恢复.md)
- **跑实验** → `experiments/04_frida_template.js`

> 📝 **本章练习**：
> 1. 写一个简单 Android app（含 native 方法），在 Waydroid 或真机上跑通第一个 Frida hook。
> 2. Hook 你自己 app 的 `Log.d` 方法，dump 所有 log tag 和 message。这能帮你理解 hook 通用 API 的威力。
> 3. **思考题**：Frida 能 hook native 任意地址，为什么不能直接 hook 加密 key 解密的瞬间？需要满足什么条件？（提示：知道偏移 / 知道参数 layout / 知道调用时机）

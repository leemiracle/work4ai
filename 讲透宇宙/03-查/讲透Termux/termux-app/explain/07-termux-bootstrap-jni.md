# 07 · termux-bootstrap-jni：`.incbin` 内嵌 bootstrap 的原生半边

> `app/src/main/cpp/termux-bootstrap.c`（11 行）+ `termux-bootstrap-zip.S`（18 行）；Java 侧见《05-termux-installer》。

## 一、角色定位

这两个小文件是 Termux「开箱即用」的地基：**把完整 bootstrap（apt/bash/coreutils 的 zip）原样编译进 APK 共享库**，首启零网络长出 `$PREFIX`。知识图谱（1284 节点/2762 边）把两者归入 **L10「App 资源与原生引导层 App Resources & Native Bootstrap」**。分工：

- `termux-bootstrap-zip.S` 是**数据文件**：不含一条指令，只把磁盘 zip 变成 ELF `.rodata` 字节和全局符号 `blob`/`blob_size`（termux-bootstrap-zip.S:1-2）。
- `termux-bootstrap.c` 是**桥**：11 行 JNI 胶水，把这两个符号包装成 Java 可用的 `byte[]`（termux-bootstrap.c:6）。

存在理由：**每个 ABI 的 APK 只嵌一份匹配的 bootstrap**。源头是 2019-10-13 提交 `c76cec18`（"Include bootstrap zips as shared libraries"）：把此前首启从 `https://termux.org/bootstrap-<arch>.zip` 的现场下载，挪到构建期完成、数据挪进 `.so`（见第五节）。

## 二、内部结构

### termux-bootstrap-zip.S：18 行的"汇编版资源编译器"

1. **`.incbin` 四 ABI 宏切换**（termux-bootstrap-zip.S:5-12）：`.incbin` 把整个文件按原样插入当前段；选哪个 zip 由 **C 预处理器宏**决定——`__i686__`→x86、`__x86_64__`、`__aarch64__`→arm64-v8a、`__arm__`→armeabi-v7a，全是 NDK clang 编译各 ABI 时预定义。文件名大写 `.S` 是关键：大写才先过 cpp，`#if` 才生效。
2. **兜底熔断**（termux-bootstrap-zip.S:13-15）：宏全不匹配则 `# error Unsupported arch`，加新 ABI 忘加分支时构建期即炸。
3. **`.rodata` 嵌入**（termux-bootstrap-zip.S:3）：zip 进只读段，运行时按页文件映射——不占脏内存、不可执行（W^X 友好）。
4. **尺寸自算**（termux-bootstrap-zip.S:16-18）：`1b` 向后引用 GNU as **局部数字标号**（L16 的 `1:`）；`.int 1b - blob` 汇编期求出精确字节数，零运行时开销，不必发明 `blob_end` 符号；`.int` 固定 32 位，与 JNI `jsize` 匹配。

### termux-bootstrap.c：11 行 JNI 桥

- L3-4 `extern` 声明汇编层符号——C 与汇编的标准握手。
- L6 导出 `Java_com_termux_app_TermuxInstaller_getZip`：JNI 名字修饰 `Java_包_类_方法` 硬编码绑定 `TermuxInstaller.getZip()`（TermuxInstaller.java:384）。第二参写 `jobject This`，而 Java 侧是 `static native`（实际传 `jclass`）——jni.h 中 `jclass` 本就是 `jobject` 的 typedef，照写可编译。
- L8-9：`NewByteArray(env, blob_size)` 在 Java 堆分配等长数组，`SetByteArrayRegion` 把 blob 一次 `memcpy` 进去——全程**唯一一次拷贝**。

## 三、外部连接

图谱中触达两节点的边共 **6 条**（全图最稀疏的叶子区）：

- **termux-bootstrap-zip.S：fan-in = 2，fan-out = 0**。入边是 `termux-bootstrap.c` 与 `Android.mk` 的 `depends_on`（权重 0.6）；出边为零——纯符号提供者。
- **termux-bootstrap.c：出边 4 条**——`contains` + `exports`（权重 0.8）指向自己的 JNI 函数节点、`depends_on` 指向 `.S`（拿 blob 符号）、以及一条 `depends_on` 指向 `TermuxInstaller.java`。这条边运行时方向"反"（Java 调 native）但语义成立：C 符号名把 Java 类名硬编码进原生代码，改类名必先炸 C 侧。
- **构建系统**：`Android.mk:3-4` 定名 `libtermux-bootstrap` 并列两源文件，与 `System.loadLibrary("termux-bootstrap")`（TermuxInstaller.java:380）名字闭环；`app/build.gradle:110-112` 用 ndkBuild 挂进 AGP——全仓唯一原生模块，ndk-build 而非 CMake。
- **Java 消费链**：`TermuxActivity.java:399`（`onServiceConnected` 无会话时）→ `setupBootstrapIfNeeded` → 工作线程 `loadZipBytes()`（TermuxInstaller.java:159）。
- **上游数据源**：四 zip 不在 git（c76cec18 gitignore 了 `*.zip`），由 gradle 构建期下载进 `app/src/main/cpp/`（app/build.gradle:170、218，SHA-256 见第四节）。

## 四、数据流

两段四态：**zip 文件 → `.rodata` 字节 → `byte[]` → `$PREFIX` 文件树**。

**构建期（每 ABI 一遍）**：`downloadBootstraps`（app/build.gradle:218）按 `packageVariant`（默认 `apt-android-7`，app/build.gradle:12）取四份 SHA-256（aarch64 锁 `ea2aeba8...`，app/build.gradle:223）；先查本地缓存哈希、命中即复用（app/build.gradle:172-188），否则下载（app/build.gradle:190），哈希不符 `GradleException` 拒绝构建（app/build.gradle:204-206）。随后 ndk-build 编 `.S` 嵌入，`-Os -fno-stack-protector -Wl,--gc-sections`（app/build.gradle:65）压小包装层（blob 被 `getZip` 引用，不会被 gc 回收）。ABI splits（app/build.gradle:69-77）产出每 ABI 一份 APK——**各只嵌一份 bootstrap**（universal APK 四份全带）；`afterEvaluate` 把 `javaCompileProvider` 依赖到 `downloadBootstraps`（app/build.gradle:241）。

**运行期（仅首启走全链）**：`$PREFIX` 已存在则短路（TermuxInstaller.java:106），`.so` 根本不加载；否则 `loadZipBytes()`（TermuxInstaller.java:378）加载共享库并 JNI 拷出 `byte[]`，`ZipInputStream` 流式遍历（TermuxInstaller.java:160）：`SYMLINKS.txt` 按 `←` 拆 `(target, link)` 对（TermuxInstaller.java:163、167）；其余条目写进 `$STAGING_PREFIX`，`bin/`、`libexec`、apt helper/methods 打 `0700`（TermuxInstaller.java:197-201）；补建 symlink（TermuxInstaller.java:210）后 `renameTo` 原子改名成 `$PREFIX`（TermuxInstaller.java:215）。

## 五、设计决策

**为什么 `.incbin` 塞 `.so` 而非 assets/res/raw？** 三个硬理由：

1. **ABI 拆分白拿**：`splits.abi` 天然按 ABI 过滤 `lib/*/`，split APK 自动只带匹配的 bootstrap；放 assets 则四份 zip 要么全进每个 APK（体积 ×4），要么手工 per-ABI 配置。
2. **完整性锁定**：构建期 SHA-256（app/build.gradle:204-206）+ F-Droid 可复现构建；运行时下载无法 pin 校验和。
3. **合规与可用性**：Play 政策禁止运行时下载可执行代码；内嵌还让首启离线可用、摆脱对 termux.org 的依赖。

**免下载 ≠ 牺牲更新**：嵌入 zip 只播种首个 `$PREFIX`，之后升级走 `$PREFIX` 内 apt 自治；代价是 bootstrap 与 App 版本耦合，换 bootstrap 要发新版。

**历史对照**（git `c76cec18~1`）：旧 `determineZipUrl()` 首启现场拼 URL 边下边解，网络抖动、服务器搬家都砸首启；新方案把失败面压缩到"每次 CI 构建一次"——**运行时风险左移到构建期**。

**拷贝策略**：`getZip` 用一次性 `NewByteArray + SetByteArrayRegion` 而非 `NewDirectByteBuffer` 零拷贝——bootstrap 只在首启读一回，简单性值这一次 memcpy。**`useLegacyPackaging true`**（app/build.gradle:125-129）：`.so` 在 APK 内压缩、安装时解到 `nativeLibraryDir`，传输体积更小、磁盘双份。

## 六、新人提示

1. **加新 ABI 是三处联动**：`splits.include`（app/build.gradle:74）、`downloadBootstraps` 加校验和行（app/build.gradle:223 起）、`.S` 加 `#elif` 分支——第三处忘了有 `#error`（termux-bootstrap-zip.S:13-15）兜底。
2. **Java 类名/方法名与 C 符号是隐式契约**：重命名 `TermuxInstaller`/`getZip` 而不改 `Java_com_termux_app_TermuxInstaller_getZip`（termux-bootstrap.c:6），编译照过，首启才抛 `UnsatisfiedLinkError`——最难复现的生产崩溃型 bug。
3. **`clean` 会删 bootstrap zip**（app/build.gradle:210 删 `src/main/cpp/bootstrap-*.zip`），zip 又被 gitignore——离线 `clean assembleDebug` 死在下载步。预缓存：四 zip 放 `app/src/main/cpp/`，哈希匹配即跳过下载（app/build.gradle:172-188）。

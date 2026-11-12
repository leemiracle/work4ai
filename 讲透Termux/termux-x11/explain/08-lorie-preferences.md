# 08 · LoriePreferences：单一 XML 驱动的设置系统与代码生成链

> 文件：`lorie/src/main/java/com/termux/x11/LoriePreferences.java`（978 行，L4 Java 应用层）
> 配套：`lorie/build.gradle`（generatePrefs 任务）、`lorie/src/main/res/xml/preferences.xml`（82 行）、`LorieApp.java`
> 行号锚经源码现场核实（commit 29d4460b）。

## 1. 角色定位：settings UI + 类型化偏好 API + CLI 协议，一文四类

termux-x11 的设置系统不走"手写 Activity + findViewById"的路子，而是一条**以 preferences.xml 为单一事实源的生成链**：XML 定义偏好 → 构建期 gradle 任务生成强类型 `Prefs.java` → 运行时 `PrefsProto` 基类提供读写与存储分流 → `LoriePreferences` 承载 UI → `Receiver` 内部类暴露命令行协议。LoriePreferences.java 这一个文件装下四个角色：

- **`LoriePreferences` 本体**（`LoriePreferences.java:83`）：AppCompatActivity，设置页宿主，实现 `OnPreferenceStartFragmentCallback` 驱动子屏导航；
- **`LoriePreferenceFragment`**（`:200`）：PreferenceFragmentCompat 子类，负责整棵偏好树的动态化——i18n 标题、条件可见性、联动启用、值校验；
- **`Receiver`**（`:565`）：静态内部类，注册在 Manifest 上接收 `com.termux.x11.CHANGE_PREFERENCE` 广播（`AndroidManifest.xml:76-78`），其 `main()`（`:739`）可被 shell-loader 以 app_process 直启，等价于一个 `termux-x11-preference` 命令行工具；
- **`PrefsProto`**（`:799`）：继承 androidx `PreferenceDataStore` 的类型化读写基类，生成的 `Prefs` 字段全部实例化自它。

三个数字钉住体量：preferences.xml 实测 **63 个 `app:key`**（含 7 个 PreferenceScreen key：main/output/pointer/kbd/other/ekbar/userActions，`preferences.xml:5,12,27,41,57,63,71`），其中 56 个是偏好项——52 个可生成类型化字段（List 17 + Switch 30 + SeekBar 3 + EditText 2，extra_keys_config 特判），4 个纯 `Preference` 节点只做 UI 入口不进 Prefs（`version`/`enableAccessibilityService`/`requestNotificationPermission`/`configureResponseToUserActions`，`preferences.xml:10,49,59,60`）。消费侧 MainActivity 引用 `prefs.<key>` 三十余处，`onPreferencesChangedCallback`（`MainActivity.java:779`）一次回调全量重应用——设置系统的任何改动都会波及全应用。

## 2. 内部结构：从 XML 到强类型字段的三级流水线

### 2.1 generatePrefs：构建期代码生成

`build.gradle:56-114` 的 `generatePrefs` 任务是整条链的起点：用 `groovy.xml.DOMBuilder.parse` 解析 preferences.xml（`build.gradle:58`），遍历全部节点按标签名分派四种类型映射——`EditTextPreference`→StringPreference（显式排除 `extra_keys_config`，`:64-65`）、`SeekBarPreference`→IntPreference（`:66-67`）、`ListPreference`→ListPreference（`:68-72`，entries/values 属性裁掉 `@array/` 前缀取资源名）、`SwitchPreferenceCompat`→BooleanPreference（`:74-75`）——然后逐行拼出 `build/generated/java/com/termux/x11/Prefs.java`（`:78`）。生成的类（模板见 `:89-113`）每个偏好一个 public final 字段（如 `public final BooleanPreference fullscreen = ...`），外加 `HashMap<String, Preference> keys` 双大括号初始化块（`:99-102`）供运行期按字符串 key 反查。

两个关键接线：`android.sourceSets.main.java.srcDirs += 'build/generated/java'`（`:115`）把生成目录挂进编译源集；`preBuild.dependsOn generatePrefs`（`:116`）保证每次构建先重新生成。因此**改偏好只能改 preferences.xml，Prefs.java 是产物不是源码**——类型、默认值、key 名三者的单一事实源在 XML。

生成类还覆写 `attach()` 做**存量迁移**（`build.gradle:106-112`）：旧版布尔 `keepScreenOn` 若存在且新版 `screenIdleTimeout` 未写过，就翻译成 `"never"`/`"system"` 写入——升级用户不被重置。`extra_keys_config` 在循环外特判一行（`:98`），默认值取 `TermuxX11ExtraKeys.DEFAULT_IVALUE_EXTRA_KEYS`（`utils/TermuxX11ExtraKeys.java:42`，双行 EK 布局 JSON），因为它需要引用该常量而 XML 里写不了。

### 2.2 PrefsProto：类型化读写与双存储分流

`PrefsProto`（`LoriePreferences.java:799-977`）是运行期基类。`Preference` 内含 key/type/defValue 三元组（`:801-808`），四个子类各自实现 `get()/put()`：BooleanPreference（`:827-845`）、IntPreference（`:847-861`）、StringPreference（`:863-877`）、ListPreference（`:879-926`）。所有读写直落 `SharedPreferences` 且一律 `commit()` 同步落盘（如 `:843`）——设置项低频写、读方强依赖一致性的场景下，牺牲写入性能换简单。

**双显示器分流**是这里的隐藏主线。LorieApp 持有两份 Prefs：`builtInPrefs`（默认 SharedPreferences）与 `secondaryPrefs`（`"secondary"` 文件，`LorieApp.java:65-66`）；`getPrefs(ctx)`（`:97-102`）按"当前显示器非默认 Display 且 `storeSecondaryDisplayPreferencesSeparately` 开启"分流。PrefsProto 侧的配合是 `isSharedAcrossDisplays(key)`（`LoriePreferences.java:939-942`）：`storeSecondaryDisplayPreferencesSeparately` 与 `enableAccessibilityServiceAutomatically` 两个 key **无论当前挂哪个存储都强制读写 builtInPrefs**（`:834-836, :840-842`）——前者是分流开关本身（必须全局单值，否则主屏关了副屏还开着）、后者牵动无障碍服务全局状态。这解释了 `attach(ctx, preferences)`（`:944-947`）为何要保存 ctx：分流时需要回查 application 级 builtInPrefs。

它同时继承 `PreferenceDataStore` 并覆写全部十个桥接方法（`:949-971`）——这是 androidx preference 的扩展点，设置 UI 的读写由此被整体接管（见 2.3），而非走框架默认的 `PreferenceManager.setDefaultSharedPreferences`。`checkAttached()`（`:933-936`）在所有读写前拦一道"未 attach 就用"的空指针。ListPreference 的 `getArrayItems`（`:908-924`）值得一提：TypedArray 元素既可能是字符串也可能是**对另一个数组的引用**（TYPE_REFERENCE 时递归展开，`:915-917`），这让 entries 数组可以复用共享子数组。

### 2.3 LoriePreferenceFragment：动态化的偏好树

`onCreatePreferences`（`:262-326`）先 `setPreferenceDataStore(prefs())`（`:264`）把整棵树的读写接到 PrefsProto——双存储分流入设置 UI 就靠这一行。随后 `setPreferencesFromResource(R.xml.preferences, root == null ? "main" : root)`（`:269`）按 rootKey 加载对应 PreferenceScreen；顶部还做了一次旧 touchMode 值清洗（合法值序号减 1 不得大于 2，否则回落 `"1"`，`:266-267`）。XML 里只写 key 不写标题，标题由 `findId("lorie_pref_" + name)`（`:256-259`）动态查 string 资源回填，summary 同理带 `_summary` 后缀（`:275-284`）——**key 名即资源命名约定**。ListPreference 的 entries/entryValues 也从 `prefs().keys.get(key).asList()` 注入（`:286-291`），与生成字段同源。

条件可见性在 `:302-321`：`dexMetaKeyCapture` 仅 DeX 可用（`SamsungDexUtils.available()`）、`hideCutout` 需 Android P、`pointerCapture` 三项需 O、三个触控笔选项需真实存在 SOURCE_STYLUS 设备（`InputDevice.getDeviceIds()` 全量扫描）。`updatePreferencesLayout()`（`:351-387`）则管联动矩阵：displayResolutionMode 三选一控制 scale/exact/custom 三项可见（`:361-364`）；DeX 与无障碍互斥（`:366-367`）；`displayStretch`/`adjustResolution` 仅 exact/custom 模式启用（`:374-376`）；TIRAMISU+ 且未授权时才显示通知权限项（`:381-384`）。刷新手段是反射调用 `Preference.onSetInitialValue`（静态 Method 缓存，`:203-219`；循环对每个 key 重放，`:355-359`）——比逐字段 setter 更省的"让框架自己重读 DataStore"。

两处精细交互：`screenIdleTimeout` 的冲突警告（`:406-432`）——系统自身熄屏时长超过用户所选值时（应用层常亮结束后系统会接管熄屏），摘要里追加橙色加粗警告文本（`ForegroundColorSpan(0xFFFFA000)` + `StyleSpan(BOLD)`，`:429-430`），并把"System"选项文本替换为实际系统时长（`:394-403`）；`extra_keys_config` 完全绕开框架对话框，自建 MONOSPACE 字体编辑器并带 Reset 按钮（`:536-562`）。还有一组小的文案工程：`setNoActionOptionText`（`:435-444`）把音量上/下与媒体键三个 ListPreference 里的 "no action" 字面选项改写成 "no action (android volume control)" 之类可读文本（`:323-325`），语义是"交还系统处理"而非"什么都不做"。非偏好型节点也有各自行为：点击 `version` 项把版本号复制进剪贴板并弹 Toast（`:458-465`），点击 `requestNotificationPermission` 走 `ActivityCompat.requestPermissions` 申请通知权限（`:467-470`），统一收在 `onPreferenceTreeClick`（`:454-474`）且每次点击后顺手全量刷新布局（`:472`）。联动矩阵的首刷发生在 fragment 的 `onCreate`（`:447-451`）与宿主 `onWindowFocusChanged`（`:113-117`）——从系统设置页返回时靠后者补一次刷新。

## 3. 外部连接：广播协议两收两发，消费方一路到 MainActivity

**ACTION_PREFERENCES_CHANGED**（`"com.termux.x11.ACTION_PREFERENCES_CHANGED"`，`:84`）是设置系统对外的变化通知协议，extras 携带 `key`（变更项）与 `fromBroadcast`（来源标志）：

- **发送方 A**：UI 侧 `onPreferenceChange` 校验通过后（`:526-530`），`setPackage` 限定包内投递；
- **发送方 B**：CLI 侧 `Receiver.onReceive` 每改一个 key 发一次（`:695-699`）；
- **接收方 A**：LoriePreferences 自身的 receiver（`:87-95`），仅在 `fromBroadcast=true` 时刷新设置 UI（`:91-92`）——防止自身写入引发的重复刷新；注册在 onResume、注销在 onPause（`:147-160`），TIRAMISU+ 用 `RECEIVER_NOT_EXPORTED`（`:151`）；
- **接收方 B**：`LorieApp.onBroadcastReceive` 的 case（`LorieApp.java:181-186`）遍历全部 MainActivity 实例，逐个重取 prefs 并回调 `onPreferencesChanged(key)`。

注意 MainActivity 的刷新其实有**双通道冗余**：除广播外，LorieApp 还给两个 SharedPreferences 都挂了 `OnSharedPreferenceChangeListener`（`LorieApp.java:70-71`，定义 `:45-48`）直达 `onPreferencesChanged`。CLI 批量修改时两通道都会触发，靠回调侧 100ms 防抖（`MainActivity.java:774-775`）收敛。

其他连接：无障碍设置变化的系统级监听用 ContentObserver 而非广播——注册 `ENABLED_ACCESSIBILITY_SERVICES` 与 `ACCESSIBILITY_ENABLED` 两个 URI（`:138-142`），200ms 防抖刷新（`:101-104`），用户在系统设置里启停无障碍服务时 UI 联动正确。子屏导航由 XML 的 `app:fragment` 属性驱动（`preferences.xml:6-9` 的 `"output"/"pointer"/"kbd"/"other"`），`onPreferenceStartFragment` 回调（`:193-198`）以 fragment 名新建 LoriePreferenceFragment 入 back stack，带四向滑动动画（`:184-190`）；`ekbar` 子屏则是额外按键条 UI 上的按钮经 activity 的 `onClick`（`:793-795`）直达。CLI 入口的接线在 shell-loader：`termux-x11-preference.in:19` 用环境变量 `TERMUX_X11_LOADER_OVERRIDE_CMDENTRYPOINT_CLASS=com.termux.x11.LoriePreferences\$Receiver` 把 app_process 启动类覆盖为 Receiver，触发其 `main()`。

## 4. 数据流：三条生命周期叙事

**用户在 UI 改一项偏好**：开关拨动 → `onPreferenceChange`（`:478-533`）先做值校验（displayScale 吸附到 10 的倍数 `:484-491`；displayResolutionCustom 必须形如正数 `WxH` `:493-505`；enableAccessibilityServiceAutomatically 需 WRITE_SECURE_SETTINGS 权限，缺则弹 ADB 授权指引并拒绝 `:510-524`）→ 通过则框架经 PrefsProto 同步写入 SharedPreferences（连带 showAdditionalKbd 开启时强制 additionalKbdVisible=true 的联动，`:507-508`）→ 发广播 → 双通道汇聚到 `MainActivity.onPreferencesChangedCallback`（`MainActivity.java:779-811`）：重取 prefs（副屏分流生效，`:780`）、PIP 被关直接 finish（`:783-786`）、`applyWindowSettings` + 输入处理器与 LorieView 的 `reloadPreferences` + KeyInterceptor 按 `enableAccessibilityServiceAutomatically` 起/停（`:801-804`）。设置 UI 自身靠 50ms 防抖的 `updateLayout`（`:481-482`）刷新联动矩阵。

**CLI 改偏好**（`termux-x11-preference fullscreen:true` 或 stdin 逐行 `key=value`）：app_process 直启 `Receiver.main()`（`:739-788`）→ 判 stdin 是否管道（`:745`）、uid 为 0/2000（root/shell）时加 `FLAG_RECEIVER_FROM_SHELL`（`:751-752`）、把回执 Binder 塞进 extra（`:748`）→ 发 `CHANGE_PREFERENCE` 广播 → `onReceive`（`:578-708`）逐 key 处理：`list` 特参全量导出为 `"key"="value"` 逐行格式（按生成字段的类型分四种取值方式，List 值还会从存储的 value 反查 entries 翻译成可读文本，`:587-609`）；四个显式 case（displayResolutionCustom 格式校验、enableAccessibility 的权限闸与 KeyInterceptor 停机、extra_keys_config 直存、storeSecondaryDisplayPreferencesSeparately 强写 builtInPrefs 保持 canonical，`:619-658`）；default 按生成字段的 PrefsProto 类型分派——布尔 `"true"` 字面量、整数 parse、列表双匹配 entries/values 并在无匹配时报全部合法选项（`:660-691`）→ 每 key 发一次 PREFERENCES_CHANGED 广播 → `edit.commit()`（`:701`）。回执走 `sendResponse`（`:710-721`）双路：有 Binder 则 `remote.exit(status, text)`（对端 `:724-730` 打印 stdout 后 System.exit），否则 orderedBroadcast setResult；5 秒无响应 main 侧自杀（`:783-786`）防挂死。错误码亦有约定：1 表示校验失败、4 表示解析失败或无法识别的 key（`:628, :669, :689`），脚本可据此判别。

**构建期生成**：preBuild 触发 generatePrefs → 解析 XML 生成 Prefs.java（52 字段 + keys 表 + attach 迁移）→ 随源集编译。此后全仓 30+ 处 `prefs.xxx.get()` 强类型引用、`prefs.keys` 反查、keys 遍历（`:355`、`:589`）都建立在这次生成上。

## 5. 设计决策：五处值得抄的工程判断

1. **XML 单一事实源 + 构建期代码生成**：key 名、类型、默认值、entries 资源四要素只在 preferences.xml 出现一次，编译期强类型化杜绝字符串 key 拼写错误，新增偏好只改一处（XML）即可同时获得 UI 项与代码 API。代价是生成逻辑用 Groovy 拼字符串（`build.gradle:83-113`），重构 XML 属性名需同步改生成器——`:64` 对 extra_keys_config 的特判就是这类耦合的显形。
2. **PreferenceDataStore 扩展点接管而非绕开框架**：不另起一套设置读写层，而是让 PrefsProto 继承 DataStore（`:799`）、Fragment 侧一行 `setPreferenceDataStore`（`:264`）整体替换存储后端——双显示器分流、跨屏单值 key 因此对 UI 透明生效，且保留了 androidx preference 的全部交互（摘要、对话框、依赖联动）。
3. **广播 + SharedPreferences 监听双通道冗余**：变化通知同时走 ACTION_PREFERENCES_CHANGED 广播（显式、可带 key、CLI 也复用）与框架原生 listener（隐式、进程内必然到达），消费端防抖收敛（`MainActivity.java:774-775`）。设置 UI 刷新用 `fromBroadcast` 标志抑制自激（`:91-92`）。
4. **分流开关自身的全局单值化**：`isSharedAcrossDisplays`（`:939-942`）把"控制分流的开关"和"全局服务状态"钉死在 builtInPrefs，杜绝副屏存储里长出第二份分流状态——否则开关读写落在哪个存储取决于读它时的显示器，逻辑直接自噬。CLI 侧同样特判强写（`:653-658`，注释明言 "Always canonical"）。
5. **校验在写入前、迁移在 attach 时**：非法值（坏分辨率、越界缩放）在 `onPreferenceChange` 拒绝并保持 UI 一致（`:484-505`）；版本演进数据（keepScreenOn→screenIdleTimeout）在 attach 一次性翻译（`build.gradle:106-112`）。两道闸都不需要外部迁移脚本。

## 6. 新人提示：上手顺序与五个易错点

上手顺序：先读 `preferences.xml` 全文（82 行，偏好语义一目了然）→ 对照 `build.gradle:56-114` 想象生成的 Prefs.java 长什么样 → 读 PrefsProto 四个子类的 get/put → 最后读 Fragment 的两个 update/校验方法。改偏好时永远改 XML；调试时 `./gradlew :lorie:generatePrefs` 后看 `build/generated/java/com/termux/x11/Prefs.java` 是最快的因果验证。

易错点：①**直接编辑 build/generated 下的 Prefs.java**——下次构建即被覆盖，生成物不是源码；②**以为 4 个纯 Preference 节点也是偏好项**——version/enableAccessibilityService 等只承载 UI 动作，`prefs.keys` 里查不到；③**新增 key 后代码不认识**——生成链挂在 preBuild，IDE 索引未刷新时会误报符号缺失，重新 sync 即可；④**忽略双存储语义**——副屏场景下 `prefs` 引用取决于 attach 到的实例，`isSharedAcrossDisplays` 外的 key 在两块屏可以不同值，读偏好前先确认拿到的是 `getPrefs(ctx)` 的返回而非裸 builtInPrefs；⑤**IntPreference.defValue() 名不副实**（`:857-860`）——它返回的是**当前存储值**（与 `get()` 实现逐字相同），并非字面默认值，这是现存代码怪味，调用处（如生成字段仅赋初值）没踩坑，但别在新代码里当真默认值用。另注意 Receiver 是 exported 的（`AndroidManifest.xml:76`），CLI 协议的 key:value 语法以 `:` 分隔（`:776`），与 stdin 模式的 `=` 分隔不同（`:763`），混用会触发 help 退出。

# 02 · vendored office 校验库三倍体：md5 全等、C 源码 shim 与断链 schema

> 仓根 = `/usr-data/data2/repos/agent-repos/anthropics/skills`，锚为仓根相对路径。md5/行数全部现场实测（commit `8a1541c4a`）。

## 1. 角色定位

`skills/{docx,pptx,xlsx}/scripts/office/` 是仓内最重的共享资产——**同一套 50 文件校验库被原样复制三份**。实测：对三目录做全量 md5 对账，50 个相对路径文件两两零差异；`validators/base.py` 三份 md5 同为 `566ce69b…`，`soffice.py` 三份同为 `2508a6df…`，三目录整体拼接 md5 亦全等。它承担三大 document skills 的 XSD 校验、LibreOffice 沙箱适配、安全解包/原子打包三大底座职能，是"**skill 自包含分发哲学**"的最直接物证。

## 2. 内部结构

每份 office 库四个模块（50 文件 = 校验器 4 + helpers 4 + soffice 1 + schemas 39 + 入口若干）：

- **`validate.py`**：CLI 入口。按扩展族分派（`office/validate.py:99-106`），支持解包目录或打包文件直传；`--auto-repair` 修两类常见伤（`office/validate.py:11-13`：paraId 超 OOXML 上限、`w:t` 带空白缺 `xml:space="preserve"`）。
- **`validators/base.py`**（875 行）：全部具体校验器的基类。`base.py:16-22` 的 `@lru_cache` `_load_schema()` 用 lxml 编译 XSD 并缓存；`base.py:31-47` 的 `UNIQUE_ID_REQUIREMENTS` 定义 **15 类**唯一 ID 规则（comment/bookmark/sldid/sheet/sp/pic 等，file 或 global 作用域）；`base.py:55-71` 的 `SCHEMA_MAPPINGS` 是部件名→XSD 的路由表；`base.py:26-29` 的 `IGNORED_VALIDATION_ERRORS` 白名单放过 `hyphenationZone` 与 `purl.org/dc/terms`（微软文档的已知误报）。
- **`validators/`**：`docx.py`/`pptx.py`/`xlsx.py` 三具体类 + `redlining.py`（裸编辑检测，见 01 篇）。
- **`helpers/__init__.py`**（111 行）：公共依赖层——`safe_extract()`（`:74-82`，拒绝符号链接条目+`resolve()` 防路径逃逸）、`rezip()`（`:85-108`，临时文件+`os.replace` 原子替换）、`opc_target()` 关系目标解析。
- **`soffice.py`**（192 行）：LibreOffice 沙箱适配器，下文专述。
- **`schemas/`**（39 文件）：ISO-IEC29500-4_2016 全套（wml 3646 行/pml/sml/dml 系/shared 系）+ `ecma/fouth-edition/` 四件 + `microsoft/` 七件 + `mce/mc.xsd`。

## 3. 外部连接

- **对 lxml/defusedxml**：库内仅有的第三方依赖（零 numpy/pydantic 级依赖）。
- **对 LibreOffice**：`soffice.py` 是唯一进程边界；`thumbnail.py`/`accept_changes.py`/`recalc.py` 等技能级脚本全部经它转译调用。
- **对外部 schema 站点**：`ecma/fouth-edition/opc-coreProperties.xsd:8-10` 对 Dublin Core 的 import 指向 `http://dublincore.org/schemas/xmls/qdc/2003/04/02/dc.xsd` 远程地址——**未随仓 vendored**，离线时靠 lxml 缓存或忽略远程解析失败；`ISO-IEC29500-4_2016/xml.xsd` 同款处理（schemaLocation 指向 w3.org，本地副本已存）。
- **三倍体内部零连接**：三份副本互不引用——这是刻意的（见第 5 节）。

## 4. 数据流：一次校验在库内怎么走

以 `python skills/pptx/scripts/office/validate.py deck.pptx --original src.pptx` 为例：

1. CLI 解析：`--original` 锁定 OOXML 族（`office/validate.py:96-97`），family=pptx（`:99`）。
2. 打包文件 → `safe_extract()` 解到临时目录（`:110-118`，BadZipFile/ValueError/OSError 全捕获）。
3. 族分派构造 `PPTXSchemaValidator`（`:124-130` 的 match 语句；pptx/xlsx 族也可带 redlining？不——`--author` 仅 docx 族，`:105-106` 显式拒绝）。
4. 具体校验器继承 base：遍历包内 XML，按 `SCHEMA_MAPPINGS` 找 XSD（`base.py:711-724`，部件名/父目录名/`.rels` 后缀三级匹配），`_load_schema()` 编译缓存命中后 `assertValid` 逐文件校验。
5. 附加检查：唯一 ID 冲突扫描（`base.py:242-250`）、关系 ID 完整性、Content_Types 一致性、`mc:Ignorable` 预处理（把标记兼容命名空间洗掉再验）。
6. redlining（仅 docx + `--author`）：撤销新修订→与原件文本 diff→报告裸编辑。
7. 失败逐条输出，**每条点名修法**（`skills/pptx/SKILL.md:26` 的消费承诺）。

并行的 soffice 数据流：`run_soffice(args)`（`soffice.py:38-46`）检查 argv 无 `-env:UserInstallation` 就建临时 profile 并前置该参数 → `get_soffice_env()`（`:27-35`）复制环境、设 `SAL_USE_VCLPLUGIN=svp`（无头插件）、按需注入 LD_PRELOAD shim → subprocess 起 soffice。

## 5. 设计决策

- **为什么复制三份而不是共享**：skill 是安装/分发的最小单位。用户可以只装 `document-skills` 里的 xlsx 而不装 docx；任何 `from docx_scripts.office import …` 式共享在单技能安装时立即断链。代价是修 bug 必须同步三处——仓库用机械复制对冲（md5 全等说明有同步纪律）。**上游 ECMA 的目录名拼写笔误 `fouth-edition`（应 fourth）三技能同错**，反而成了复制纪律的化石证据。
- **运行时编译 C 的 socket shim**（`soffice.py:78-185`）：沙箱 VM 常禁 AF_UNIX socket，LibreOffice 的 UNO 桥一建 socket 就挂。方案：`_needs_shim()`（`:53-59`）先试建 AF_UNIX socket 探测；受限则把 `_SHIM_SOURCE` 约 108 行 C 写到临时目录、`gcc -shared -fPIC … -ldl` 现场编译（`:62-74`）成 `lo_socket_shim.so`，LD_PRELOAD 注入。C 层（`dlsym(RTLD_NEXT, …)` 取真实函数，`:102-115`）：`socket()` 对 AF_UNIX 失败时降级 `socketpair()`（`:118-140`）并登记 FD 簿记；`accept()` 阻塞读 wake pipe（`:152-163`）；`close()` 写 wake pipe 唤醒后 `_exit(0)`（`:166-184`，转换完成即退）；**FD≥1024 一律直通不 shim**（`:95-100`）——避开 fd 表溢出的高编号区间。为什么用 C 而不是 Python monkeypatch：LD_PRELOAD 作用于 soffice 子进程自身，Python 层无从插手。
- **"函数可见但禁止直用"的文档化契约**：`soffice.py:11-15` docstring 明说必须走 `run_soffice()` 而非拿 `get_soffice_env()` 自己起进程——env 不带 profile 名，非 root 沙箱引导不了默认 profile，soffice 会以 "User installation could not be completed" 中止。罕见的把负 API 也写进文档的诚实做法。
- **已知断链的死资产**：`microsoft/wml-2010.xsd:2-5` 对 `orel.xsd`/`oartbasetypes.xsd`/`oartsplineproperties.xsd` 三个 MS 专有 schema 的 import 被注释掉——这些文件从未随仓收录。只要被验文档不含那些命名空间的内容就无害；这是 vendored 集合"够用即可"的边界宣言。
- **白名单式容错**：`IGNORED_VALIDATION_ERRORS`（`base.py:26-29`）说明校验目标不是"ISO 纯度"而是"PowerPoint/Word 能打开"——工程准绳压倒标准准绳。

## 6. 新人提示

- **读懂一份等于读懂三份**：精读 `skills/xlsx/scripts/office/`（或任意一份）即可，其余两份逐字节相同（md5 可自验）。
- 改库必须三处同步：编辑后跑 `md5sum skills/*/scripts/office/validators/base.py` 确认一致，否则三个技能行为漂移。
- 排查 LibreOffice 挂死先看 `_SHIM_SO`（`soffice.py:50`，/tmp 下 `lo_socket_shim.so`）是否生成——没生成说明 `_needs_shim()` 判定不需 shim，问题在别处。
- XSD 报 `purl.org/dc/terms` 相关错误别慌，白名单本应吞掉；真出现说明文档用了非常规 core.xml 形态。
- 校验器对 schema 合法但 PowerPoint 拒开的隐患（图表轴 id 未声明等）另有一层 helpers 检查——XSD 全绿不等于文件能开，别停在第 4 节第 5 步。

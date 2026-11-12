# 02 · parser.py —— 3726 行解析中枢：三解析器 + 版本门控 + 注册表

> 源码：`raganything/parser.py`（3726 行，全仓最大文件，commit 2cd2b332）。一切文档进入系统的第一站：把 PDF/Office/图片/文本/HTML 变成统一的「MinerU 风格内容块列表」。

## 1. 角色定位

本文件是**抽象基类 + 三个具体解析器 + 进程内注册表 + 诊断工具箱 + 独立 CLI** 五合一：

- `Parser` 基类（`parser.py:359`）：格式常量 OFFICE/IMAGE/TEXT（:367-369）、URL 下载、LibreOffice 预转、文本直解析，与四个抽象方法 `parse_pdf`/`parse_image`/`parse_document`/`check_installation`（:1309,1333,1358,1382）。
- `MineruParser`（:1395，默认解析器）：subprocess 调 `mineru` CLI。`DoclingParser`（:2454）：唯一支持 HTML（`parse_html` :3022）。`PaddleOCRParser`（:3108）：进程内轻量 OCR。
- 注册表：`SUPPORTED_PARSERS = ("mineru", "docling", "paddleocr")`（:3548）+ `get_parser`（:3556）+ 自定义注册 `register_parser`（:3450）。文件尾附独立 CLI（`def main()` :3588）。

模块 docstring 两条硬约束（:19-21）：**MinerU 2.0 起不再内置 LibreOffice 转换**，Office 须先转 PDF；自定义注册表只在进程内生效，CLI 不做插件自动发现（:11-17）。

## 2. 内部结构

**（a）MinerU 3.x 锁定——本文件最重的工程投资**。`_MINERU_REQUIREMENT = "mineru[core]>=3.4.1,<4"`（`parser.py:77`）、`_MINERU_FIRST_UNSUPPORTED_MAJOR = 4`（:79）、`_MINERU_LAST_SUPPORTED_PYTHON = (3, 13)`（:83）。拒绝 4.x 的理由在注释：MinerU 4.0 把 `mineru -p <input> -o <output>` 换成子命令式 CLI 且只产 Markdown（:73-76）。Python 约束同理：3.x 全系声明 Requires-Python `<3.14`，py3.14+ 根本装不上，`_mineru_python_note()`（:91-99）指引用户改用 Docling。诊断链配套：`_parse_mineru_version`（:205）、`_describe_mineru_version_failure`（:266）、已知故障签名表 `_MINERU_KNOWN_FAILURES`（如 `'PageChars' object is not iterable` 对应 pdftext 版本不兼容，:117-120）、输出尾截取（40 行/4000 字符，:146-159）与 stderr 环形缓冲（deque maxlen=200，:1579）。

**（b）MineruParser 执行链**。`_run_mineru_command`（:1508）拼 `mineru -p <input> -o <output> -m <method>`（:1545-1553），可选 `-b backend`/`-l lang`/`-s/-e` 页范围/`-f`/`-t` 关公式表格/`-d device`/`-u vlm_url`（:1555-1572），支持 timeout 与自定义 env。Windows 路径安全专门处理（:1434-1455 哈希化）。产物读取 `_read_output_files`（:1893）是 **v2/legacy 双格式舞蹈**：优先 `*_content_list_v2.json` 经 `convert_mineru_content_list_v2` 拍平（:1981），失败或过滤后为空回退 legacy JSON（:1994-2011）；随后字段别名归一（`img_caption`↔`image_caption`，:2020-2030）、相对路径转绝对并做**路径穿越检查**（`is_relative_to` 不在基目录内置空，:2049-2056），最后 `attach_public_media_urls(item)` 挂公网 URL——全仓唯一调用点（:2060，Docling/PaddleOCR 不享受）。

**（c）基类公共设施**。`_download_file`（:387）：Chrome UA 防 403（:407）、30s 超时（:412）、按 Content-Type 推扩展名（:415-427）、失败清理临时文件（:443-454）。`convert_office_to_pdf`（:534）：输出 `<文档目录>/libreoffice_output/<stem>_<hash>/`（:544,570）；`_libreoffice_command_candidates`（:489）跨平台探测 libreoffice/soffice 乃至 Windows 安装路径（:496-519）；候选逐一尝试避免假 WARNING（:645-646）；注释留实测数据（7.4MB PPTX 在 soffice 下 4 分钟，:608）与各平台安装指引（:677-680）。`parse_text_file`（:1271）**禁止 PDF 往返**：历史用 ReportLab 渲 PDF 再 OCR，慢且引入渲染故障面（docstring 引 issue #24/#226/#316/#331，:1281-1284）；现在 `_text_to_content_blocks`（:1112）按空行分段，Markdown 的 ATX 标题成块带 `text_level`、本地图片引用经魔数校验（`_resolve_md_image` :1054 + `looks_like_image`，import :65）后产 MinerU 同构 image 块，URL/缺失/非图片保持字面文本。`convert_text_to_pdf`（:717）仍保留——内含中文 PDF 的 STSong-Light CID 字体注册（:806-820，简中标准 CID 字体、reportlab 内置，防静默失败 #24）——但主链路已不依赖。

**（d）分发逻辑**。`MineruParser.parse_document`（:2338）按扩展名路由：pdf→`parse_pdf`（:2067）、图片→`parse_image`（:2153）、Office→warning+`parse_office_doc`（:2301，转 PDF 再解析）、文本→`parse_text_file`、HTML→`html_requires_docling_error`（:347；扩展集 :344）、未知扩展→当 PDF 试（:2383-2388）。Docling 版（:2565）多 HTML 分支；PaddleOCR 版（:3396）最严格：`del method`（:3401）、未知格式直接 ValueError（:3421-3424）。

## 3. 外部连接（对齐图谱边）

- → `mineru_content.py`：`convert_mineru_content_list_v2`/`MineruContentListV2Error`（:66-69），按页结构拍平核心。
- → `asset_urls.py`：`attach_public_media_urls`（:64,2060）。→ `image_signature.py`：`looks_like_image` 魔数识别（:65），扩展名不可信。
- ← `raganything.py`（:36）/`processor.py`/`batch_parser.py`：解析入口消费方。
- → 外部世界：subprocess（mineru）、LibreOffice/soffice、urllib 下载、Pillow（TYPE_CHECKING 门控 :61-62）、PaddleOCR（延迟加载 :3129）。
- → 测试面：43 用例 `test_mineru_version_support.py` 钉死版本诊断行为。

## 4. 数据流

以一份 .docx 为例：`parse_document`（:2338）→ `parse_office_doc`（:2301）→ 基类 `convert_office_to_pdf`（:534）→ 回到 `parse_pdf`（:2067）→ `_prepare_mineru_paths`（:1455）建临时工作区 → `_run_mineru_command`（:1508）→ `_copy_mineru_output_tree`（:1487）搬回正式目录 → `_read_output_files`（:1893）v2 优先/legacy 回退 → 别名归一+路径安全+公网 URL（:2020-2060）→ 返回内容块列表。下游统一按「MinerU 风格块」消费，三解析器差异在此终结。URL 输入被 `_is_url`（:379）识别后先 `_download_file`（:387）落地再走同一路径。

## 5. 设计决策

- **subprocess 驱动 MinerU 而非进程内 import**：MinerU 依赖树重（torch 系），子进程隔离可控制超时/环境/崩溃面；代价是错误只剩 stderr，于是有签名表+版本诊断链补偿（117-306 行约 190 行纯诊断代码）。
- **v2/legacy 双格式宽容降级**：对 MinerU 跨版本输出漂移有韧性（:1959-2011）。
- **安全内建**：路径穿越检查（:2051）、图片魔数校验、Windows 危险路径哈希化，全部默认开启。
- **注册表拒绝覆盖内建名**（:3501-3506）：防自定义 parser 冒充 mineru；名称归一化 `_normalize_parser_name`（:3434）容忍大小写。
- **文本直解析废除 PDF 往返**：性能与故障面双赢，四个 issue 号钉在 docstring 防回归。

## 6. 新人提示

1. 换解析器只需 `RAGAnythingConfig(parser="docling")`；但 HTML 只有 Docling 支持，其他 parser 遇 HTML 抛引导性 ValueError（:347）。
2. MinerU 报错先看 `installation_error`：区分「没装/装了 4.x/Python 太新/mineru 起不来」四种情形，比日志里的 pip 建议精确。
3. Office 转换慢是 LibreOffice 的锅（实测 PPTX 分钟级，:608）；生产大批量建议预转 PDF。
4. 生产内容块里的图片路径是**绝对路径**且经安全校验；拿到相对路径说明走了 legacy 回退分支（:1965-1967）。
5. 写自定义 parser 参考 `register_parser` docstring 的 MarkerParser 样例（:3474-3494）：至少实现 `parse_document`+`check_installation`，HTML 能力可选。

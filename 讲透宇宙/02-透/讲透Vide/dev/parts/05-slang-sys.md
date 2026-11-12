# 05-slang-sys 精读手册

> 模块定位：slang-sys 是 vide 整个语法栈的最底层——把 `third_party/slang`（C++ SystemVerilog 前端，git submodule）用 CMake 编出静态库，再经 [CXX bridge](https://cxx.rs) 暴露给 Rust：解析入口（`SyntaxTree`/`Compilation`）、非类型化语法树视图（node/token/trivia/cursor/walk）、脚本生成的类型化 AST 与 Kind/Diagnostic 枚举、诊断转换、preprocessor trace、补全用 facts 表。它自身不含 Salsa query / VFS / HIR 逻辑——纯绑定层，workspace 内唯一消费者是 `crates/syntax`（"Syntax facade over slang-sys"，见其 Cargo.toml L14），后者再喂给 base-db/preproc/HIR/IDE。分层约定：**Rust 侧绝不持有 C++ 指针跨边界生存期**——所有返回值要么是拷贝出的 Rust-owned 数据（Raw* struct），要么是钉在 `SyntaxTree`（`cxx::SharedPtr`）上的裸指针视图（`NonNull`，借用 `'a`）。

---

## 构建与配置（5 卡）

## `crates/slang-sys/Cargo.toml`（16 行）
**作用**：crate 清单。`name = "slang-sys"`，`version = "11.0.0"`（L4 注释明确 "aligned with slang version"——升级 submodule 时必须同步改此版本号），`build = "build.rs"`。
**关键字段**：`cxx = { version = "1.0.124", features = ["c++20"] }`（L10）——桥需要 C++20；`tracing.workspace = true`（L11，诊断降级日志用）。build-dependencies：`cmake 0.1.50` + `cxx-build 1.0.124`（版本必须与 cxx 一致）+ `which 8.0.5`（找 sccache）。
**改动连带**：cxx/cxx-build 版本升降会同时改生成头路径（`DEP_CXXBRIDGE1_HEADER`）与桥语义；`edition = "2024"`（L6）依赖新式 `use<'a>` 语法（syntax_node.rs L383/L441），降 edition 会编译失败。

## `crates/slang-sys/src/.clangd`（16 行）
**作用**：clangd 配置，让三个 wrapper.cpp 在 IDE 里可解析（否则 slang include 与 cxx.h 全裂）。
**关键字段**：`-std=c++20`；include 路径 `-I../../../third_party/slang/include` 与 `external`（L7-8）；`-I../../../target/slang-sys/clangd/include`（L9）——该目录由 build.rs `build_cxx_bridge` L365-368/L394-395 拷贝 cxx.h + cxxbridge 生成头 + slang 安装头填充，**先跑一次 cargo build 才有补全**；`-DSLANG_BOOST_SINGLE_HEADER -DSLANG_STATIC_DEFINE`（L15-16）与 build.rs L382-383 的编译宏对齐。L10-12 的 `../../../../` 变体是给 build.rs 自身被 clangd 分析时用的相对深度兜底。
**改动连带**：新增 wrapper.cpp 或移动头文件不需改它；但改 build.rs 里的编译宏/安装布局时必须同步，否则 IDE 报错与真实编译不一致。

## `crates/slang-sys/build.rs`（455 行）
**角色**：构建总闸——跑 5 个 Python 代码生成器、CMake 编译上游 slang、编 CXX bridge、配置链接。
**关键结构与不变量**：
- `SLANG_SOURCE_DIR = "../../third_party/slang"`（L8）：slang 是 submodule，`find_slang_dir` L69-78 用 `CMakeLists.txt` 存在性校验，缺失时 panic 提示 `git submodule update --init`。
- `FFI_FILES`/`WRAPPER_HEADERS`/`WRAPPER_FILES`（L21-27）：三组文件清单是**桥的唯一事实源**——改文件名/增删桥文件必须同步这三处，否则 rerun 触发（L430-455）或编译列表漏项。
- `env_detection::cmake_cache_key`（L109-142）：把 CC/CXX/CMAKE_GENERATOR/toolchain 等 env 做 FNV-1a 哈希（注释明言"cache namespace, not security boundary"），拼进 CMake out_dir（L256-258）——**保证不同工具链的 CMake 缓存互不污染**；配合 `build_dir()` L92-95 按 `TARGET` 三元组再分目录（L14-19 注释解释为何必须按 target 分：CMake 缓存编译器探测）。
- `build_slang`（L254-347）：`SLANG_MASTER_PROJECT=OFF`、tests/tools/pylib 全关、install 开（L294-298）；mimalloc 关（L302，TODO 注释：slang 默认产 mimalloc 目标文件而非静态库，链接问题未解）；emscripten 分支 L305-313（`-fwasm-exceptions`、`CMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY`）；MSVC Release 优化旗恢复 L334-344（绕 cmake-rs 过滤 Cargo flags 的行为）。
- `generate_rust_defs`（L194-252）：**5 个生成器并行 spawn**（L233-243），输入是 slang 的 `scripts/{syntax,tokenkinds,triviakinds,diagnostics}.txt` + `include/slang/diagnostics/Diagnostics.h`，输出到 OUT_DIR 的 `{syntax_kind,token_kind,trivia_kind,diagnostic,ast}.rs`；python 解释器可用 `PYTHON` env 覆盖（L144-146）。
- `build_cxx_bridge`（L349-396）：`cxx_build::bridges(FFI_FILES)` + wrapper.cpp 一起编成 `slang_sys_bridge`（L393）；defines `SLANG_BOOST_SINGLE_HEADER`/`SLANG_STATIC_DEFINE`（L382-383）；debug 时加 `SLANG_DEBUG`（L390-392）；随后把 cxxbridge 生成头与 slang 安装头**递归拷进 clangd include 目录**（L394-395，服务 .clangd）。
- `setup_linking`（L416-428）：`static:-bundle=svlang` + fmt（debug 用 `fmtd`，L419/L423）——`-bundle` 把 C++ 静态库对象打进 rlib；非 emscripten Windows 补 `Advapi32`（L424-427，mimalloc 大页 token API）。
- sccache 通道（L153-170）：`VIDE_USE_SCCACHE_CMAKE=1` 强制；否则看 `RUSTC_WRAPPER` stem 是否在 {sccache,cachepot,buildcache,kache}（L167-169）；`SCCACHE_PATH` 可指定路径，找不到即 panic（L172-179）。
**公开 API**：build script，无 Rust API。
**依赖/被依赖**：depends_on 5 个 scripts/generate_*.py 与三个 ffi.rs/wrapper.cpp（图谱）；被 `config:crates/slang-sys/Cargo.toml`（build 字段）配置，`.gitmodules`（submodule）关联。
**改动影响面**：任何桥签名改动都会经 rerun 触发全量重编（L448-450 watch 含整个 slang submodule 目录 L433）；升 slang submodule = 全部生成代码重跑，若 slang 的 txt 格式变了，生成器会直接报错（好）或静默漂移（坏，靠 diagnostic.rs L13 的测试兜底）。
**集成点**：新增桥函数的最小路径——改 ffi.rs（签名）→ wrapper.h（声明）→ wrapper.cpp（实现）→ 若返回新 struct 需在 ffi.rs 加 Raw 定义；`VIDE_SLANG_BUILD_VERBOSE=1`（L13/L148-151）与 phase 计时日志（`log_phase` L58-60）是排查构建问题的入口。

## `crates/slang-sys/scripts/generate_syntax_kind.py`（156 行）
**角色**：从 slang `syntax.txt` 生成 Rust `SyntaxKind(u16)` newtype（OUT_DIR/syntax_kind.rs）。
**关键结构与不变量**：`load_syntax_kind_names` L13-66 解析 DSL：普通类型行（`Name final=true` 等标签 L60-62）、成员行、`kindmap<Base>` 块（L56-58）与 `empty` 分隔；**只有 `final=true` 且非 `multiKind` 的类型才产生 "TypeSyntax" 形态的 kind**（L25-30），kindmap 行映射到 `Base+"Syntax"`（L50）；重复 kind 抛错（L28-29/L48-49）；结果前置 `"Unknown"`（L66）。`render_syntax_kind` L69-132：常量序号=出现顺序（`Self(index)` L76），追加三个列表伪 kind：`SYNTAX_LIST=u16::MAX-2`、`TOKEN_LIST=u16::MAX-1`、`SEPARATED_LIST=u16::MAX`（L86-88）——**占据 u16 顶部，天然不与真实 kind 冲突**；生成 `ALL`、`from_raw/as_raw/is_unknown/is_list`、手写 `Debug`。
**公开 API**：CLI `--input`/`--out`（L139-140）。
**依赖/被依赖**：被 build.rs 调用（图谱 depends_on）；输出被 `src/syntax/syntax_kind.rs` include。
**改动影响面**：syntax.txt 的类型/标签变化直接改变生成的 kind 常量集与序号；序号=slang C++ `SyntaxKind` 枚举值，**两侧必须按同一顺序生成**（C++ 侧由 slang 自己的生成器保证），否则 `syntax_node_kind` 返回的 u16 对不上 Rust 常量。
**集成点**：新增语法类别（如新 SV 版本特性）时无需手写——升级 slang 后该脚本自动带上。

## `crates/slang-sys/scripts/generate_token_kind.py`（91 行）
**角色**：从 slang `tokenkinds.txt` 生成 `TokenKind(u16)`（OUT_DIR/token_kind.rs）。
**关键结构与不变量**：`load_token_kind_names` L13-20——每行一个 kind（跳过注释/空行），**顺序即枚举值**；`render_token_kind` L23-67 产出常量 + `ALL/from_raw/as_raw/is_unknown` + Debug。与 syntax 版差异：无列表伪 kind、无 kindmap DSL。
**公开 API**：CLI `--input`/`--out`（L73-74）。
**依赖/被依赖**：被 build.rs 调用；输出被 `src/token.rs` include。
**改动影响面**：序号必须与 slang C++ `slang::parsing::TokenKind` 逐位一致（wrapper.cpp L1326 直接 `static_cast<uint16_t>(token->kind)`）；`TokenKind::UNKNOWN`（index 0，因 "Unknown" 通常居首）被 syntax_node.rs L158 当哨兵过滤。
**集成点**：`token.rs` L11-12 的 `HIGH_Z0_KEYWORD` 别名就是为本生成器的 screaming_snake 输出（`HIGH_Z_0_KEYWORD`）补的兼容名——新 kind 若蛇形命名不合意，同样在 token.rs 加别名而非改生成器。

## `crates/slang-sys/scripts/generate_trivia_kind.py`（91 行）
**角色**：从 slang `triviakinds.txt` 生成 `TriviaKind(u8)`（OUT_DIR/trivia_kind.rs）。
**关键结构与不变量**：与 token 版同构，唯底宽 **u8**（L35 `pub struct TriviaKind(u8)`）——trivia 种类少（whitespace/注释/directive/skipped 等）；wrapper.cpp L1845 `static_cast<uint8_t>(...kind)` 对应。
**公开 API**：CLI `--input`/`--out`（L84-85）。
**依赖/被依赖**：被 build.rs 调用；输出被 `src/token.rs` L4-8 include 并 re-export。
**改动影响面**：`SyntaxTrivia::kind()`（trivia.rs L51-55）直接 `from_raw`；新 trivia 种类只需升级 slang。
**集成点**：IDE 侧区分注释/空白做折叠、着色时消费。

## `crates/slang-sys/scripts/generate_diagnostic.py`（384 行）
**角色**：双输入生成器——`diagnostics.txt`（诊断定义 DSL）+ `Diagnostics.h`（subsystem 枚举）→ OUT_DIR/diagnostic.rs（`DiagSubsystem`/`DiagnosticSeverity`/`DiagCode`/`DIAGNOSTIC_INFOS`/`DIAGNOSTIC_GROUPS`）。
**关键结构与不变量**：
- `parse_subsystems` L19-40：正则抓 `#define DS(x) ...` 宏体（L21-26），每个 `x(Name)` 一项——**subsystem 枚举值 = Diagnostics.h 里的顺序**，Rust `#[repr(u16)]`（L139）与之 ABI 对齐。
- `parse_diagnostics` L43-128：shlex 分词；`subsystem X` 切组（L73-77）；`group name = { ... }` 收集 warning-option 分组（L51-61/L79-84，未闭合报错 L125-126）；诊断行按首词分 warning（带 option 名 L87-91）/error/fatal/note（L92-96）；重名抛错（L100-101）；**L115-123：每 subsystem 内按 `(severity,name,message,option_name)` 排序后 `enumerate` 出 `code`**——`DiagCode` 的 code 不是 slang 文件顺序，而是本排序的稳定索引，依赖 slang 生成 Diagnostics.h 时同序（有 diagnostic.rs L13-28 的采样测试兜底）。
- `render_diag_code` L212-272：`DiagCode { subsystem: u16, code: u16 }`（L228-231）+ 每诊断一个 const（L221-223）+ `info()` 线性查 `DIAGNOSTIC_INFOS`（L258-260）。
- `render_groups` L312-344：option→诊断名展开成 `*_GROUP_DIAGNOSTICS: &[DiagCode]` 常量。
- `main` L347-380：**交叉校验** diagnostics.txt 用到的 subsystem 必须都在 Diagnostics.h 里（L360-364），防拼写漂移。
**公开 API**：CLI `--input`/`--diagnostics-header`/`--out`（L351-353）。
**依赖/被依赖**：被 build.rs 调用；输出被 `src/diagnostic/def.rs` include（图谱还有 def.rs depends_on 本脚本的 generated 边）。
**改动影响面**：slang 加诊断后必须重跑（自动）；若排序键改了（L119），全部 code 重排——而 C++ 侧 `diag.code.getCode()`（wrapper.cpp L155）传的是 slang 原生 code，**两侧 code 语义靠 slang 自身生成一致性保证，本脚本排序键不可轻动**。
**集成点**：`--pragma diagnostic ignore` 类功能（syntax_diagnostic.rs 测试 L252-263 验证）消费 `option_name`；`find_diagnostic_groups`（syntax_diagnostic.rs L186-192）消费 groups。

## `crates/slang-sys/scripts/generate_ast.py`（552 行）
**角色**：从 syntax.txt 生成类型化 AST（OUT_DIR/ast.rs）：每类型一个 struct 或 enum，实现 `AstNode` trait；外加 `HybridNode`/`TokenList`/`SyntaxList`/`SeparatedList` 容器。
**关键结构与不变量**：
- `load_types` L110-170：解析类型继承（`base=` 标签 L123）、成员（`parse_member` L94-107：token/tokenlist/list<T>/separated_list<T>/T?/T 六种）、kindmap（L160-162）；`TypeInfo.combined`（L126）= 祖先成员先序拼接——**成员访问器靠"从左到右数孩子"定位，继承链变了全部偏移**。
- `reverse_maps` L173-193：kind→类型 反查表 + 父类型聚合其所有后代 kind。
- `render_prefix` L206-223：访问第 i 个成员前，前面的 token/node 成员各占 1 个 child 槽（`index += 1` L215），**list 成员占 `syntax().list_child_size(n)` 个槽**（L217-220，list_ordinal 按 combined 顺序递增）——这是与 slang `SyntaxListInfo`（wrapper.cpp L1301-1311 `getChildListInfo`）的核心对齐机制。
- `render_member` L226-282：node 成员 `child_node(index).and_then(T::cast).unwrap()`（L271）——**缺员即 panic**，信任语法产生式；optional 成员返回 Option（L274-281）；`SeparatedList::children` 用 `step_by(2)` 跳过分隔符（L514）。
- `render_enum` L320-423：多 kind 类型（如 ModuleMember）生成为 enum，`select_variant` L336-348 把 kind 折叠到最近的声明基类 variant；`can_cast` 是全 kind 的 `||` 链（L389-391）。
- `render_ast` L426-535：固定头部——`AstNode` trait（L437-441：`can_cast/cast/syntax`）、`HybridNode`（万能 cast，L449-453）、三个列表容器。
- `snake` L83-86：成员名转蛇形，Rust 关键字加尾下划线（`type_`）。
**公开 API**：CLI `--input`/`--out`（L542-543）。
**依赖/被依赖**：被 build.rs 调用；输出被 `src/syntax/ast.rs` include。
**改动影响面**：改 syntax.txt 的成员顺序/新增成员 = 旧代码全部访问器偏移错位（不报编译错，运行时 unwrap panic 或静默错位）——**这是本 crate 最脆的一根线**；测试 syntax.rs L95-167（`generated_binding_ast_accessors_match_slang_parser`、`nested_list_accessors_stay_aligned`）是唯一防线。
**集成点**：crates/syntax 的 `slang_ext/node.rs`、`has_name.rs` 基于生成的类型写扩展 trait；新增 SV 语法的类型化访问自动可用。

---

## C++ 接口族（4 卡，覆盖 7 个 .h/.cpp）

## 接口族：公共头 `crates/slang-sys/src/wrapper.h`（20 行）
**角色**：全 crate 共用的 C++ helper 头——`slang_sys::helper::to_std_strings`（L13-19），把 `rust::Vec<rust::String>` 转 `std::vector<std::string>`（reserve + emplace，避免逐元素重分配）。
**关键结构与不变量**：唯一的 namespace 级 inline 函数；include cxx.h + 三个 slang 头（DiagnosticEngine/SyntaxTree/SourceManager，L6-10）——**这三个 include 决定了三个 wrapper 模块可用的 slang 面**。
**公开 API**：`to_std_strings(const rust::Vec<rust::String>&) -> std::vector<std::string>`（L13）。
**依赖/被依赖**：被 compilation/wrapper.h、diagnostic/wrapper.h、syntax/wrapper.h 三者 include（图谱）；自身依赖 cxx.h。
**改动影响面**：改签名需同步全部调用点（diagnostic/wrapper.cpp L123 经 `slang_sys::helper::` 限定使用）。
**集成点**：新 wrapper 模块要 Rust→C++ 字符串数组时直接复用，勿再写本地拷贝（compilation/wrapper.cpp L18-24 就有一处历史重复，可留意）。

## 接口族：syntax `crates/slang-sys/src/syntax/wrapper.h`（290 行）+ `crates/slang-sys/src/syntax/wrapper.cpp`（1876 行）
**角色**：桥的 C++ 半壁——最大接口族：SourceSession/包装 SyntaxTree、5 个解析入口、node/token/trivia 的指针级访问器、preprocessor trace 重建、facts 表。
**关键结构与不变量**（.h L26-290 声明 / .cpp 实现）：
- **类型别名**（.h L34-36）：`SyntaxNode = ::slang::syntax::SyntaxNode`、`SyntaxToken = ::slang::parsing::Token`、`SyntaxTrivia = ::slang::parsing::Trivia`——桥上流转的是**裸 slang 类型**，无包装。
- **`SourceSession`**（.h L38-50，.cpp L95-125）：持有一个 `slang::SourceManager` + 两张 path→buffer map。ctor `setDisableProximatePaths(true)`（.cpp L96）；`assign_source_buffer` 拒绝空 path（L101）、**同 path 不同文本抛 `logic_error`**（L106）——防 IDE 编辑竞态下的静默覆盖；`source_buffer(path)` 未注册即抛（L121-123）。不变量：一个 session = 一套 buffer id 空间，跨 session 的指针/range 无意义。
- **包装 `SyntaxTree`**（.h L52-68）：`shared_ptr<slang SyntaxTree> + shared_ptr<SourceSession> + root_buffer_id` 三件套（L52 有 TODO：希望未来直接暴露给 Rust 而非伪装成 SyntaxTree）。`wrap_syntax_tree`（.cpp L174-190）取 `getSourceBufferIds().front()` 当 root_buffer_id 且**拒绝空**（L182-183）。
- **解析入口**（.cpp L194-462）：`make_syntax_options`（L145-172）组装 `PreprocessorOptions`（predefines、additionalIncludePaths、`!expand_includes → maxIncludeDepth=0` L161-162）与 `ExpectedSyntaxOptions`（**有 offset → cursorOffset 局部采集；无 offset 但 collect → recordAll 全量** L164-170）；`guess` 分支选 `fromText` vs `fromFileInMemory`（L264-281）——后者保 compilation-unit 根契约（HIR 依赖，见 tree.rs L122-124 注释）；buffer 解析入口先 `addLineDirective(SourceLocation(buffer.id,0), 2, tree_name, 0)`（L307-309）把逻辑名映射到第 2 行，服务 `\<name>` 报告。
- **期望语法查询** `syntax_tree_expected_syntax_at`（.cpp L324-378）：读 `tree->getMetadata().expectedSyntax`，过滤 `location.buffer()==root_buffer` 且 `[start,end]` 窗口含 offset（L336-341），再对 code+subsystem+token_kind+context+location 全字段去重（L343-359）。
- **preprocessor trace**（.cpp L938-1170，约 230 行最复杂段）：`collect_nodes` 递归收集语法树+trivia 内嵌 directive 节点（L563-581）；define 先编号（L980-985），MacroUsage 事件分配 call_id 且 **call_id==expansion_id**（L1060-1063）；`calls` map 以 `(buffer_id,start,end)` 为 key 且**范围唯一性强制**（L1067-1076 抛错）；`trace_emitted_token`（L803-934）为每个发射 token 定 origin：kind 编码 1=Source/2=MacroBody/3=MacroArgument/4=Builtin/5=TokenPaste/6=Stringify/7=Predefine（L923、L862-905、L918-921），与 Rust `TraceTokenOrigin` 常量（preproc.rs L109-116）**手工镜像，改一侧必须改另一侧**；Source 宏的 body/argument token 缺元数据即抛 logic_error（L883-890、L910-916）——宁可崩不静默。source_buffers 收尾：剥离 SourceManager 内部 NUL 终止符（L1151-1155，注释说明不剥会破坏 predefine 校验与 range 长度）；predefine 的逻辑名 `<api>` 判定 origin=1（L1158-1162）。
- **emitted index 对账**（.cpp L1172-1223）：`trace_emitted_token_index_for_target` 注释钉版（L1196-1199）——**语法树 token 与发射流不要求位置同构**（恢复/宏拼接会造出未发射 token），只有目标 token 需要 emitted 身份；找不到即带 raw/kind/range 的详尽 logic_error（L1210-1221）。
- **node/token 访问器**（.cpp L1227-1510）：全是薄 cast——`syntax_node_kind` L1229、四段式 range（valid + start/end buffer/offset）、`range_with_context` 走 `map_range_with_context`（L39-64：用 `DiagnosticEngine::mapSourceRanges` 把宏内 range 映回 context 根、context 不属 owner 树即抛 L51-52）；`list_child_count/size` 委托 slang `getChildListInfo`（L1301-1311）；token 值访问器 `syntax_token_int_value` L1399-1421（四进制文本预格式化 + single_word 优化）。
- **keyword/directive 表**（.cpp L1461-1508）：`LexerFacts::getKeywordVersion/getKeywordTable` 按 version 查表，未知 version 一律返回空/Unknown。
- **facts 表**（.cpp L1512-1840）：对 `slang::syntax::SyntaxFacts` 的直通 + 四个**本仓自研补充**：`get_block_item_declaration_kind`（L1517-1541，default 分支用 getIntegerType/getKeywordType/isPossibleDataType 兜底判 DataDeclaration）、`get_library_map_member_kind`（L1543-1551）、`get_specify_item_kind`（L1553-1567）、`get_config_header_item_kind`/`get_config_rule_kind`（L1569-1584）；`is_possible_member_kind`（L1659-1725）≈60 case 的 token→member-kind 大表（vide 侧补全核心）；`is_keyword_candidate`（L1747-1793）按 `SyntaxKeywordContext` 枚举分发到上表，`keyword_candidates_for_context`（L1795-1814）遍历 keyword table 过滤+排序+去重。
**公开 API**：.h 是完整签名清单——tree 命名空间 7 个解析/查询函数（L71-142）、node 17 个（L146-182）、token 22 个（L186-238）、facts 31 个（L242-272）、trivia 6 个（L276-287）。
**依赖/被依赖**：wrapper.cpp include 自身 wrapper.h + `slang-sys/src/syntax/ffi.rs.h`（cxx 生成头，.cpp L3）；被 syntax/ffi.rs 桥引用（`include!("syntax/wrapper.h")`）；compilation 与 diagnostic 的 wrapper.h 都 include 本头。被 .clangd 配置覆盖。
**改动影响面**：改任何桥函数签名 = 同步 syntax/ffi.rs + 编译两份语言；`SyntaxTree`/`SourceSession` 内存布局变更波及 compilation/wrapper.cpp（session 领养逻辑）与 tree.rs 的 SharedPtr 持有。
**集成点**：给 Rust 暴露新 slang 能力的首选落点（如未来暴露 `getSourceBufferIds` 更多语义）；facts 的自研四表 + is_possible_member_kind 是 IDE 补全（keyword_candidates_for_context）的直接数据源。

## 接口族：diagnostic `crates/slang-sys/src/diagnostic/wrapper.h`（23 行）+ `crates/slang-sys/src/diagnostic/wrapper.cpp`（315 行）
**角色**：把 `slang::Diagnostics`（C++ 异构类型）转成平坦的 `RawSyntaxDiagnostic`（Rust 可拥有）。
**关键结构与不变量**：
- `diagnostics_to_rust`（.cpp L299-313）：每次调用**新建** `DiagnosticEngine` + `CollectingDiagnosticClient`，依次 `issue` 三批：warning-options 校验产物（L119-127，空选项跳过）、**pragma 映射**（`setMappingsFromPragmas` L308，源码里 `` `pragma diagnostic ignore `` 在此生效）、真实诊断（L311）——顺序保证 pragma/option 引发的错误也出现在结果里。
- `CollectingDiagnosticClient`（.cpp L219-280）：以 `const ::slang::Diagnostic*` 指针为 key 分配**稳定递增 id**（`next_diagnostic_id` 从 1 起，L279）；同一原始诊断第二次 report（即 note 复述）时查 `parent_ids` 建立 note→parent 关系（L229-234）；`reserve_note_ids`（L261-274）递归预登记嵌套 notes——不变量：**id 只在单次 collect 生命周期内稳定**，跨调用重编号。
- `to_rust_reported_diagnostic`（.cpp L145-213）：severity 取 `reported.severity`（pragma 可升降级）、args 用 `engine.formatArg` 全量格式化（L129-143 注释钉版：防新 arg 类型静默空串）；`map_source_ranges_to_context`（L86-117）算 primary_range：多 range 取并集但**任一跨 buffer 即放弃**（L104-111 注释明言 Rust 模型只有单 buffer 主区间，不猜）；expansionLocs 逐个转 (location, fullyOriginalLoc, macroName)（L199-208）；include stack 由 client 按需收集（L238-240）。
- `syntax_tree_diagnostics`（.cpp L286-293）：单树诊断入口，直接用 `tree.session->source_manager`。
**公开 API**：.h L9-13 `diagnostics_to_rust`、L18-21 `syntax_tree_diagnostics`。
**依赖/被依赖**：include 公共 wrapper.h 与 syntax/wrapper.h（SyntaxTree 类型）；被 diagnostic/ffi.rs 与 compilation/ffi.rs（经 `slang-sys/src/diagnostic/ffi.rs.h`，compilation/wrapper.cpp L2）引用；compilation/wrapper.h L10 反向 include 本头。
**改动影响面**：`RawSyntaxDiagnostic` 字段增删要同步 diagnostic/ffi.rs L33-54 与 syntax_diagnostic.rs 的 from_raw；primary_range 单 buffer 约束若放宽，IDE 消费端（L22-26 注释所述）需同步。
**集成点**：新增诊断元数据（如 macro 扩展链新语义）从这里进 Rust；`CollectingDiagnosticClient` 的 id/parent 机制是 IDE 里 note 分组的基石。

## 接口族：compilation `crates/slang-sys/src/compilation/wrapper.h`（70 行）+ `crates/slang-sys/src/compilation/wrapper.cpp`（187 行）
**角色**：`slang::ast::Compilation` 的薄壳：多树聚合 + parse/semantic 诊断提取。
**关键结构与不变量**：
- `Compilation` 类（.h L19-26）：`top_modules + shared_ptr<SourceSession> session + unique_ptr<::slang::ast::Compilation> inner`。ctor（.cpp L28-31）：`make_options`（L10-16）把 topModules 塞进 `CompilationOptions` 的 Bag。
- **session 单一性不变量**（.cpp L137-155 `add_syntax_tree`）：校验 tree 与 session 均有效（L138-139）；若 inner 已有 SourceManager 且**与树 session 不同 → logic_error**（L141-145，"all syntax trees added to a compilation must share one source session"）；首个外挂树把 session **领养**进 compilation（L151-152，注释解释：slang 在 addSyntaxTree 后仍引用树的 SourceManager，不领养则 Rust 侧 drop 会留下悬垂）。所有 parse_* 入口都**顺带 addSyntaxTree**（L59、L101、L113、L133）。
- 诊断提取（.cpp L157-185）：`getParseDiagnostics`/`getSemanticDiagnostics` 交给 diagnostic 模块转换；无 SourceManager（空 compilation）返回空 vec。
**公开 API**：.h L28-69——`new_compilation`、4 个 parse 入口、`register_source_buffers`、`add_syntax_tree`、`parse_diagnostics`、`semantic_diagnostics`。
**依赖/被依赖**：include ../diagnostic/wrapper.h、../syntax/wrapper.h、slang/ast/Compilation.h；被 compilation/ffi.rs 桥引用；其 `.cpp` 是唯一 include 两个生成头（compilation 与 diagnostic 的 ffi.rs.h）的翻译单元。
**改动影响面**：session 领养/校验逻辑是 Rust `Compilation::add_syntax_tree`（compilation.rs L31-33，clone SharedPtr 传入）正确性的前提——改这里会直接破坏 compilation.rs L184-192 的树存活测试。
**集成点**：vide 目前只用它做 parse/semantic 诊断与树聚合；未来做真正语义查询（symbol/type）应在此扩壳。

---

## Rust 侧（24 卡，.rs/.build.rs 逐文件）

## `crates/slang-sys/src/lib.rs`（19 行）
**角色**：crate 门面——声明 8 个模块并 re-export 公共类型。
**关键结构与不变量**：`pub mod` 8 个（L1-8：compilation/diagnostic/facts/preproc/source_buffer/syntax/token/value）；re-export 白名单（L10-19）：`SemanticFacts/SyntaxFacts`、preproc 的 Trace 全家、`SourceBuffer*`、`LiteralBase`、`SVInt/Bit/TimeUnit`——**`SyntaxTree` 等经 `syntax` 模块路径访问，不在根 re-export**。
**公开 API**：上述 re-export。
**依赖/被依赖**：仅向下聚合 8 模块（图谱）；图谱显示 `document:README.md` 引用、`.github/workflows/ci.yml` pipeline 触达本文件。
**改动影响面**：re-export 列表即 crate 公共面——增删会立刻影响 crates/syntax 的 `use slang_sys::...`。
**集成点**：二开者从这里看 crate 顶层 API 面。

## `crates/slang-sys/src/token.rs`（21 行）
**角色**：token/trivia kind 的生成代码挂载点 + `LiteralBase`。
**关键结构与不变量**：两个私有 mod 各 include OUT_DIR 生成文件再 `pub use *`（L1-8）；`HIGH_Z0_KEYWORD/HIGH_Z1_KEYWORD` 别名桥接生成器的 `HIGH_Z_0_KEYWORD` 蛇形输出（L10-13）；`LiteralBase`（L15-21）四进制枚举，与 wrapper.cpp `syntax_token_literal_base` 的 0/1/2/3 编码经 syntax_node.rs L347-352 手工映射。
**公开 API**：`TokenKind`、`TriviaKind`（生成）、`LiteralBase`。
**依赖/被依赖**：被 crate 内 facts/preproc/syntax 全家 + crates/syntax（lib.rs/ptr.rs/slang_ext/* 共 8 文件，图谱）import——**本 crate 被外部引用最多的文件之一**。
**改动影响面**：别名删除会破外部对 `HIGH_Z0_KEYWORD` 的引用；LiteralBase 顺序变更破坏 base() 映射。
**集成点**：所有按 token kind 分派的 IDE 逻辑（高亮/补全过滤）的枚举源。

## `crates/slang-sys/src/source_buffer.rs`（90 行）
**角色**：纯 Rust 的源缓冲标识/区间类型——跨 FFI 的 buffer 语义货币。
**关键结构与不变量**：`SourceBufferId { path, text: Option<String>, buffer_id, origin }`（L4-10，text 为 None 表示文本未随 trace 提供）；`SourceBufferOrigin { Source, Predefine }`（L12-16）；`SourceBufferRange { buffer_id, range }`（L18-22）；`SyntaxTreeBufferIds { root_buffer_id, source_buffers }`（L24-28）；`SourceLocation { buffer_id, offset }`（L31-35）与 `SourceRange { start, end }`（L38-42）——**半开区间、可跨两个 buffer**；`is_single_buffer`（L87-89）判 start/end 同 buffer；字段构造收窄为 `pub(crate) from_parts`（L45/L59），外部只能读 getter。
**公开 API**：上述类型 + 只读 getter（buffer_id/offset/start/end/start_buffer_id/end_buffer_id/is_single_buffer）。
**依赖/被依赖**：被 syntax.rs 全家（element/syntax_node/tree/trivia）、preproc.rs、compilation.rs 依赖；被 crates/syntax 的 lib.rs 与 has_text_range.rs import（图谱）。
**改动影响面**：`SourceRange` 是所有节点/token 区间的载体，改字段=全 crate + crates/syntax/slang_ext 连锁。
**集成点**：IDE 把 buffer_id+offset 换算 LSP 位置时的统一中间表示。

## `crates/slang-sys/src/value.rs`（167 行）
**角色**：四态 SystemVerilog 值的 Rust-owned 表示——**C++ 大整数不跨 FFI，只传标量元数据 + 四进制文本**（L7-11 doc 注释钉版）。
**关键结构与不变量**：`SVInt { bit_width, is_signed, has_unknown, single_word: Option<u64>, binary/octal/decimal/hexadecimal: String }`（L13-22）；`serialize(base)` 只认 2/8/10/16 否则 panic（L58-66）；Display 走 decimal（L69-73）。`TimeUnit::from_raw`（L86-100）0-5 映射 s..fs，未知值 warn+None（**降级不 panic**）。`Bit::from_raw`（L128-140）0/1/128/64 → L/H/X/Z，未知 warn+None——128/64 是 slang logic_t 的位编码。
**公开 API**：`SVInt`（getter + serialize）、`TimeUnit`、`Bit`。
**依赖/被依赖**：依赖 syntax/ffi.rs（RawSVInt，L5）；被 syntax_node.rs（token.int()）与 crates/syntax/lib.rs 消费（图谱）。
**改动影响面**：Bit 的 128/64 魔数与 slang `logic_t` 强耦合；serialize 支持新进制需同步 wrapper.cpp L1399-1421 的预格式化。
**集成点**：hover 显示字面量值、计算常量展开的直接数据源。

## `crates/slang-sys/src/facts.rs`（139 行）
**角色**：facts 门面——把 u16 进出的 FFI 谓词包装成类型安全的方法（零状态 unit struct）。
**关键结构与不变量**：`pub struct SyntaxFacts; pub struct SemanticFacts;`（L7-8，无字段）；`SyntaxFacts` 24 个关联函数（L10-133）：is_possible_* 十连（statement/expression/data_type/argument/param_assignment/port_connection/ansi_port/non_ansi_port/function_port/parameter）、is_gate_type/is_port_direction/is_net_type、get_* 六个 TokenKind→SyntaxKind 映射、`is_possible_member_kind(token, member)` 双参、`keyword_candidates_for_context(version, context)`（L103-108，context 以 `u8` 传递）、is_allowed_in_{compilation_unit,generate,module,interface,program,package} 六连。`SemanticFacts::is_edge_kind`（L135-139）是唯一的 semantic 侧条目。
**公开 API**：上述全部（经 lib.rs re-export）。
**依赖/被依赖**：依赖 syntax/ffi.rs + diagnostic（SyntaxKeywordContext）+ token；被 crates/syntax/lib.rs 消费（图谱）。
**改动影响面**：每个方法一对一绑 wrapper.cpp facts 实现——增删需三处同步（此处/ffi.rs/wrapper.cpp）。
**集成点**：IDE 补全与语法引导（"这个位置可能出现什么"）的权威数据面；新增上下文先扩 `SyntaxKeywordContext`（syntax_diagnostic.rs L81-98）再接此表。

## `crates/slang-sys/src/preproc.rs`（517 行）
**角色**：preprocessor trace 的 Rust 数据模型 + Raw→owned 转换（前端宏/头文件追踪的根基）。
**关键结构与不变量**：
- `Trace { root_buffer_id, source_buffers, events, include_edges, emitted_tokens }`（L7-14）——五段式全量快照。
- newtype id 族（L16-23）：`EventId/MacroCallId/MacroDefinitionId/MacroExpansionId` 皆 `pub u32` 元组——**trace 内稳定，跨 trace 无意义**。
- `Event`（L31-49）：directive/name/include_file_name token、params/arguments、body/expr_tokens、disabled_ranges——按事件种类部分填充。
- `MacroOrigin`（L51-58，0-4 panic 兜底 L258-269）；`EmittedToken`（L60-68）；`Token { raw_text, value_text, token_kind, range }`（L70-76）。
- `TokenOrigin` 枚举（L119-184）八 variant：Source/MacroBody/MacroArgument/Predefine/Builtin/TokenPaste/Stringify/Unavailable——携带完整溯源链（call/definition/expansion/parent id + body/argument index + 三个 range）；`TraceTokenOrigin` 的 kind 常量（L109-116）与 wrapper.cpp 手工镜像。
- `TokenOrigin::from_raw`（L284-390）：按 kind 分派；**必填字段缺失即 expect panic**（如 L302-311 macro body 无 call id 即崩），而可选 index 用 `has_*` 归 None——把"契约破坏"与"合法缺省"严格分开。
- `Trace::from_raw`（L186-221）：origin 未知值 panic（L198）；`range_required`（L424-426）对必填 range 缺失同样 expect。
**公开 API**：经 lib.rs re-export：`Trace/Event/EventId/MacroCallId/MacroDefinitionId/MacroExpansionId/MacroOrigin/MacroParam/ActualArgument/Token/TokenOrigin`；`EmittedToken` 供 syntax_node 用。
**依赖/被依赖**：依赖 syntax/ffi.rs + token + source_buffer；被 lib.rs 与 syntax/syntax_node.rs（`preprocessor_trace_emitted_token` 返回 `EmittedToken`，L456-469）消费。
**改动影响面**：字段变更同步 syntax/ffi.rs Raw* 与 wrapper.cpp 转换；kind 常量两份手工镜像（另一份在 wrapper.cpp）必须同步。
**集成点**：宏展开回溯 UI（token→宏调用链）与 crates/preproc 语义消费的公共数据模型；测试 L445-516（`operation_origins_preserve_missing_body_indices`）钉住 TokenPaste/Predefine 的可选 index 语义。

## `crates/slang-sys/src/diagnostic.rs`（29 行）
**角色**：diagnostic 模块聚合点 + 生成代码元数据采样测试。
**关键结构与不变量**：`mod def`（生成 include）、`pub(crate) mod ffi`（桥）、`mod syntax_diagnostic`，前两者与后者 re-export（L1-6）。
**公开 API**：`DiagSubsystem/DiagnosticSeverity/DiagCode/DiagnosticInfo/DIAGNOSTIC_INFOS/DiagnosticGroup/DIAGNOSTIC_GROUPS`（def）+ `SyntaxDiagnostic` 全家（syntax_diagnostic）。
**依赖/被依赖**：向下 def/ffi/syntax_diagnostic；被 compilation.rs、facts.rs、syntax/tree.rs 及 crates/syntax/lib.rs 引用（图谱）。
**改动影响面**：测试 L13-28（`generated_binding_diagnostic_metadata_matches_slang_definitions`）校验 EXPECTED_EXPRESSION 与 UNKNOWN_ESCAPE_CODE 的 name/subsystem/severity/message/option + default 组包含关系——**升级 slang 后必跑的第一道闸**。
**集成点**：run `cargo test -p slang-sys`（覆盖 L8-29 的内嵌测试）。

## `crates/slang-sys/src/diagnostic/def.rs`（9 行）
**角色**：OUT_DIR/diagnostic.rs 的 include 壳。
**关键结构与不变量**：私有 mod slang_diagnostic include 生成文件（L6-8）；L1-5 TODO 钉版：目前所有 subsystem 诊断混在一个 DiagCode 平面里，未来可能按 subsystem 拆枚举。
**公开 API**：`pub use slang_diagnostic::*`（L9）。
**依赖/被依赖**：被 diagnostic.rs 引用；图谱记录其与 generate_diagnostic.py 的生成关系。
**改动影响面**：无逻辑；TODO 落地时改此处与下游 `DiagCode::from_raw` 消费。
**集成点**：生成诊断 API 的唯一入口路径。

## `crates/slang-sys/src/diagnostic/ffi.rs`（72 行）
**角色**：diagnostic 桥 DSL——定义 Raw* 数据结构 + 唯一 extern 函数 `syntax_tree_diagnostics`。
**关键结构与不变量**：`#[cxx::bridge(namespace = "slang_sys::diagnostic")]`（L6）；`RawSyntaxDiagnostic`（L33-54）21 字段平坦结构——**cxx 不支持递归/Option，一律 has_* bool + 默认值**模式；`RawDiagnosticLocation/Range/Expansion`（L8-30）；L56-61 跨桥引用 syntax 的 `SyntaxTree` 不透明类型（`type SyntaxTree = crate::syntax::ffi::SyntaxTree`，经 include syntax/wrapper.h）；L63-71 声明 `syntax_tree_diagnostics(tree, warning_options) -> Vec<RawSyntaxDiagnostic>`。
**公开 API**：`pub(crate) use slang_ffi::*`——Raw* 供 syntax_diagnostic.rs 与 compilation/ffi.rs（后者把 `RawSyntaxDiagnostic` 声明为共享类型，compilation/ffi.rs L34-40）使用。
**依赖/被依赖**：被 diagnostic.rs/syntax_diagnostic.rs/syntax/tree.rs（diagnostics() 调用）与 build.rs（桥文件清单）引用。
**改动影响面**：字段增删三处同步（此处 + diagnostic/wrapper.cpp 转换 + syntax_diagnostic.rs from_raw）；struct 放 cxx bridge 里意味着 C++ 侧同名 struct 由 cxx 生成——**不能在 C++ 手工定义同名**。
**集成点**：新诊断元数据进 Rust 的通道。

## `crates/slang-sys/src/diagnostic/syntax_diagnostic.rs`（317 行）
**角色**：Rust 侧诊断模型（`SyntaxDiagnostic` 等）+ Raw→owned 转换 + 补全辅助类型。
**关键结构与不变量**：
- `SyntaxDiagnostic`（L9-35）：owned 数据；`option_name: Option<String>` 由空串转 None（L142）；`groups` 由 `find_diagnostic_groups`（L186-192，线性查 DIAGNOSTIC_GROUPS）反填——**生成代码与运行时数据的粘合点**；`primary_range`/`location`/`buffer_id`/`file_name` 全 Option 化；`ranges` 保留跨 buffer 全量（L22-26 doc：IDE 只吃 primary_range，ranges 留给需要完整报告的消费者）；`diagnostic_id/parent_diagnostic_id`（L33-34）承接 C++ client 的稳定 id（parent=0→None，L172-173）。
- `SyntaxDiagnostic::from_raw`（L124-175）：severity 未知 → warn 日志 + 按 Fatal 处理（L126-134，与 value.rs 的丢 None 策略不同——**诊断宁重勿丢**）。
- `ParserExpectedSyntax`（L60-69）+ `LexedTokenAtOffset`（L72-78）+ `SyntaxKeywordContext`（L81-121，`#[repr(u8)]` 14 variant，from_raw 数组线性查 L101-120）。
**公开 API**：`SyntaxDiagnostic`（pub 字段）、`SyntaxDiagnosticLocation/Range/Expansion`、`ParserExpectedSyntax`、`LexedTokenAtOffset`、`SyntaxKeywordContext`、`from_raw`（crate 内）。
**依赖/被依赖**：依赖 def（DIAGNOSTIC_GROUPS）+ ffi + syntax（SyntaxKind）+ token；被 diagnostic.rs re-export；被 crates/syntax 消费。
**改动影响面**：字段是 IDE 诊断管线（LSP publishDiagnostics）的输入契约。
**集成点**：`find_diagnostic_groups` 让 Rust 侧免传组信息；测试 L199-316 六个（组回填/位置元数据/pragma 映射/未知 warning option 报错/宏展开链/note 父子关系）几乎每个都对应一个 C++ 行为契约，改 diagnostic/wrapper.cpp 前先看这里。跑法 `cargo test -p slang-sys`。

## `crates/slang-sys/src/compilation.rs`（226 行）
**角色**：`Compilation` Rust 包装——多树聚合 + 诊断 + 带共享 session 的解析。
**关键结构与不变量**：`Compilation { raw: UniquePtr<ffi::Compilation> }`（L12-14）；`new`/`new_with_top_modules`（L22-29）走 ffi::new_compilation；`add_syntax_tree`（L31-33）传 `tree.raw.clone()`（SharedPtr 克隆，**Rust 侧 SyntaxTree 保持独立存活**——测试 L167-181 钉住 clone 后原树仍可用）；`parse_syntax_tree_from_buffer`（L60-76）：include_buffers 非空即 panic（L66-68）——buffer 解析要求缓冲已注册在 compilation session 上；`parse_library_map_syntax_tree_from_buffer`（L92-113）：带任何 include/predefine/expand 选项即 panic（L98-104）——库映射不支持这些；`raw_pin`（L135-137）把 UniquePtr 转 Pin<&mut>；`raw_parse_options`（L139-158）做 Rust options→FFI options 的 Vec 拆分展开。
**公开 API**：`Compilation::{new, new_with_top_modules, add_syntax_tree, register_source_buffers, parse_syntax_tree_from_text, parse_syntax_tree_from_buffer, parse_library_map_syntax_tree_from_text, parse_library_map_syntax_tree_from_buffer, parse_diagnostics_with_options, semantic_diagnostics_with_options}`。
**依赖/被依赖**：依赖 compilation/ffi.rs、diagnostic（SyntaxDiagnostic）、syntax（SyntaxTree 等）；被 lib.rs 与 crates/syntax/lib.rs 引用（图谱）。
**改动影响面**：session 语义（wrapper.cpp L137-155）变更直接打测试 L184-192（`compilation_keeps_an_attached_tree_source_session_alive`：drop 树后 compilation 诊断仍空即 session 领养生效）。
**集成点**：vide 需要跨文件语义（parse+semantic 诊断聚合）时的入口；`register_source_buffers`（L35-41）是"先注册后解析"IDE 模式的钩子（测试 L203-225 演示 include 链）。

## `crates/slang-sys/src/compilation/ffi.rs`（91 行）
**角色**：compilation 桥 DSL。
**关键结构与不变量**：`#[cxx::bridge(namespace = "slang_sys::compilation")]`（L13）；`ParseSyntaxTreeOptions`（L16-25）8 字段平坦结构；**跨桥类型缝合**是本文件精髓：L27-32 引 syntax 的 SyntaxTree（不透明，include syntax/wrapper.h），L34-40 引 diagnostic 的 `RawSyntaxDiagnostic`——`type RawSyntaxDiagnostic = crate::diagnostic::ffi::RawSyntaxDiagnostic` 并 include **两个头**（`slang-sys/src/diagnostic/ffi.rs.h` 生成头 + diagnostic/wrapper.h，L36-37），cxx 据此把两个桥的类型统一；extern 块 L42-90：`new_compilation -> UniquePtr<Compilation>`，可变方法全收 `Pin<&mut Compilation>`（cxx 对 C++ 类默认按值可变语义的规范写法），诊断两函数收 `&Compilation`。
**公开 API**：`pub(crate) use slang_ffi::*`（Compilation 不透明类型 + 9 个函数 + options struct）。
**依赖/被依赖**：被 compilation.rs 与 build.rs（桥清单 L21）引用；图谱：depends_on compilation/wrapper.cpp。
**改动影响面**：函数签名改动同步 wrapper.h/.cpp；新增 Pin<&mut> 方法注意 Rust 侧 raw_pin 约定。
**集成点**：未来给 compilation 加语义查询 API 的桥面落点。

## `crates/slang-sys/src/syntax.rs`（325 行）
**角色**：syntax 模块聚合点 + **整 crate 的行为验收测试场**（12 个集成级测试）。
**关键结构与不变量**：`pub mod ast; pub(crate) mod ffi;` + 8 个私有 mod 全量 re-export（L1-19）——外部经 `slang_sys::syntax::*` 拿到全部树视图类型。
**公开 API**：re-export cursor/element/iter/syntax_kind/syntax_node/tree/trivia/walk/ast 全部公共项。
**依赖/被依赖**：向下 10 个子模块；被 crate 内 compilation/facts/preproc/value 与 crates/syntax 的 12 个文件（lib/has_name/has_text_range/ptr/slang_ext/*）import——**crate 的绝对核心枢纽**。
**改动影响面**：测试 L26-324 覆盖：真实调用上游 parser（L26-45）、file 根保持 COMPILATION_UNIT（L48-52）、trace root_buffer 语义（L55-68）、predefine origin（L71-92）、生成 AST 访问器（L95-114）、嵌套列表对齐（L117-167）、诊断 owned 化（L170-185）、range 字节稳定（L188-207）、trivia/preorder（L210-236）、children/element（L239-269）、cursor（L272-298）、elem_preorder（L301-324）。任何树视图/生成器改动都会先在这里红。
**集成点**：跑法 `cargo test -p slang-sys`；新功能的第一个集成测试应加在此处（有完整解析环境）。

## `crates/slang-sys/src/syntax/syntax_kind.rs`（4 行）
**角色**：OUT_DIR/syntax_kind.rs include 壳。
**关键结构与不变量**：私有 mod + `pub use *`（L1-4）；生成的 `SyntaxKind(u16)` 含 `SYNTAX_LIST/TOKEN_LIST/SEPARATED_LIST` 三个 u16::MAX 区段伪 kind 与 `is_list()`。
**公开 API**：`SyntaxKind` 全部常量与方法。
**依赖/被依赖**：被 syntax.rs/element.rs/syntax_node.rs 引用（图谱）。
**改动影响面**：无逻辑；伪 kind 占 u16::MAX 顶部意味着真实 kind 数量不得超过 65532。
**集成点**：IDE 按 kind 分派的枚举源。

## `crates/slang-sys/src/syntax/ast.rs`（6 行）
**角色**：OUT_DIR/ast.rs include 壳（类型化 AST）。
**关键结构与不变量**：`mod slang_ast { include!(...) }` + re-export（L3-6）；doc 注释 L1-2 钉版"typed AST nodes generated from slang's syntax tree"。
**公开 API**：`AstNode` trait、`HybridNode`、`TokenList`/`SyntaxList`/`SeparatedList`、全部类型化 struct/enum。
**依赖/被依赖**：被 syntax.rs 与 crates/syntax 的 has_name.rs、slang_ext/node.rs 引用（图谱）。
**改动影响面**：全生成，手改即被覆盖。
**集成点**：二开者优先用 `AstNode::cast` 从非类型化视图升级到类型化访问。

## `crates/slang-sys/src/syntax/tree.rs`（616 行）
**角色**：`SyntaxTree`——Rust 侧解析门面 + 补全查询 + 词法级光标工具。
**关键结构与不变量**：
- `SyntaxTree { raw: SharedPtr<ffi::SyntaxTree>, preprocessor_trace_cache: Arc<OnceLock<Trace>> }`（L25-28）——**trace 惰性单次构建**（`preprocessor_trace` L265-273 get_or_init，clone 的树共享同一缓存因 Arc）。
- `SyntaxTreeOptions`（L37-48）：`expand_includes` 默认 true（L63）、`expected_syntax_offset` 的 doc（L44-47）钉版"completion metadata local to a single query"——**期望语法不落长期树，按光标单查**。
- 解析双模：`from_text*`（guess=true）vs `from_file_in_memory*`（guess=false，L119-132，doc L122-124"file-root contract required by HIR"）；`*_and_trace` 变体（L136-156）解析后立刻建 trace。
- 补全三件套：`expected_syntax_at_offset[_with_options]`（L182-209，**强制 collect_expected_syntax=false + offset=Some**，单点查询语义）、`library_map_expected_syntax_at_offset`（L211-221）、`expected_syntax_at(offset)`（L257-263）在已 parse 树上按 offset 过滤。
- 词法工具（纯 Rust 重实现，不走 slang）：`directive_at_offset`（L223-236，`` ` ``后缀词 → DIRECTIVE token + directive_kind）与 `token_word_at_offset`（L238-255，identifier/$system 词）；共享状态机 `LexState { Code, String, LineComment, BlockComment }`（L474-480）——`word_after_backtick_at_offset` L333-396 / `identifier_at_offset` L398-464 **跳过字符串与注释**（测试 L596-599）；`identifier_at_offset` 特判"光标在词尾且下一字节仍是标识符起始"（L429-431 `at_end`，避免词中误切）。
- `ParserExpectedSyntax::from_raw`（L297-330）：未知 code → warn + `UnknownDiagnostic(sub:code)` 名（L301-308）；未知 context 丢弃。
- **Send/Sync**（L482-488）：SAFETY 注释钉版——SharedPtr 拥有、构造后只读、可变 C++ 调用仅限构造与 trace 收集期；`PartialEq` 按 `root()==root()`（L496-502）。
**公开 API**：`SyntaxTree::{from_text, from_text_with_options, from_file_in_memory, from_file_in_memory_with_options, from_file_in_memory_with_options_and_trace, from_text_with_options_and_trace, from_library_map_text, root, diagnostics, diagnostics_with_options, expected_syntax_at_offset, expected_syntax_at_offset_with_options, library_map_expected_syntax_at_offset, directive_at_offset, token_word_at_offset, expected_syntax_at, preprocessor_trace, buffer_id, buffer_ids}` + `SyntaxTreeWithTrace`/`SyntaxTreeOptions`/`SyntaxTreeBuffer`。
**依赖/被依赖**：依赖 syntax/ffi.rs、syntax_node、diagnostic（转换）+ diagnostic/ffi、source_buffer、token；被 syntax.rs/syntax_node.rs/trivia.rs 引用。
**改动影响面**：`from_file_in_memory` 的 guess=false 是 HIR 根契约（下游 base-db 依赖）；两个词法工具被 crates/syntax 的 token_at_offset 扩展复用。
**集成点**：IDE 每次编辑的 parse 入口 + 补全三件套是 completion provider 的直连 API；测试 L504-616 十个（含 fixture 探针 `inspect_completion_fixture_expectations` L568-582 用 eprintln 观察全 offset 期望）。

## `crates/slang-sys/src/syntax/syntax_node.rs`（482 行）
**角色**：非类型化树视图双雄 `SyntaxNode`/`SyntaxToken` + 带 parent 的 token——**全 crate 借用安全的核心**。
**关键结构与不变量**：
- `SyntaxNode<'a> { raw: NonNull<ffi::SyntaxNode>, tree: &'a SyntaxTree }`（L26-29）——**裸 C++ 指针 + 树借用**，生存期由 `'a` 钉死；同构 `SyntaxToken<'a>`（L32-36）；`SyntaxTokenWithParent`（L41-45，doc L38-40：slang token 不带 parent 指针，需要上下文的操作必须随身带）。
- `SyntaxNode`（L47-216）：`root_buffer_id` doc（L59-66）钉版——include 展开树的结构 range 可能起于宏 buffer 终于源文件，**识别展示 buffer 必须问树而不是看 range**；`range()` 四段 FFI 拼装（L68-80）；`range_with_context`（L82-124，宏映射回 context）；`child_token` **过滤 UNKNOWN kind**（L158，生成 AST 的槽位语义靠它把空槽折叠掉）；`child(index)` 先试 node 后试 token（L161-169）；`first_token` 用 cursor 深搜（L183-196）；`identity()` 返回指针值当稳定 id（L213-215）；PartialEq/Hash 按 raw 指针（L218-230）——**同一树内指针即身份**。
- `SyntaxToken`（L232-410）：三个静态表函数（keyword_table_for_version/keyword_kind_for_version/directive_text 公开，directive_kind crate 内，L233-247）；类型化值访问器全部**先查 kind 门禁**：`int()` 仅 INTEGER_LITERAL（L326-329）、`bits()` 仅 UNBASED_UNSIZED（L331-335）、`real()` REAL|TIME（L337-340）、`base()` 仅 INTEGER_BASE + 0-3 映射（L342-357）、`time_unit()` 仅 TIME_LITERAL（L359-363）；`trivias_with_loc`（L381-409）**从 range.start 倒推**每个 trivia 的位置：显式 location 优先（include/endinclude 的行指令），否则 cursor-len 回退、`saturating_sub` 防负（L398）。
- `SyntaxTokenWithParent`（L426-482）：`range()` 委托 `range_with_context(self.parent)`（L431-433，宏 token 映回父上下文）；`preprocessor_trace_emitted_token_index/_emitted_token/_origin`（L445-473）——index 版可 Option，token 版断言存在（L464-467）。
**公开 API**：上述三类型全部 pub 方法。
**依赖/被依赖**：依赖 cursor/element/iter/syntax_kind/tree/trivia/walk/ffi + preproc（EmittedToken）+ source_buffer + token + value；被 syntax.rs、cursor.rs、element.rs、iter.rs、tree.rs、trivia.rs、walk.rs 互相引用（crate 内枢纽）；被 crates/syntax 的 slang_ext/node|token|trivia|support 消费。
**改动影响面**：UNKNOWN 过滤、identity 语义、Send/Sync（继承 tree.rs）都是下游 ptr.rs（弱引用语义）与 IDE 高亮的隐含契约。
**集成点**：二开者遍历树的标准姿势——`node.children()/elem_preorder()/walk()`；宏溯源从 `token.preprocessor_trace_origin()` 一键入链。

## `crates/slang-sys/src/syntax/element.rs`（75 行）
**角色**：`SyntaxElement`——node/token 的无 tag 统一视图。
**关键结构与不变量**：`SyntaxElementKind { Node(SyntaxKind), Token(TokenKind) }`（L8-12）；`SyntaxElement`（L18-22）两 variant，doc L14-17 钉版 token 变体必须带 parent；`kind()` 分派到双 Kind（L25-30）；`parent()` 对 Node 查 FFI、对 Token 直接取随身 parent（L50-55）；`From` impl 两个（L65-75）。
**公开 API**：两 enum + kind/as_node/as_token/as_tok_with_parent/parent/range。
**依赖/被依赖**：依赖 syntax_kind/syntax_node/source_buffer/token；被 cursor/iter/syntax_node/walk 引用（图谱）。
**改动影响面**：是 cursor 与两个 preorder 迭代器的元素类型，增 variant 需全部分派补齐。
**集成点**：写"同时处理节点和 token"的访问者时用。

## `crates/slang-sys/src/syntax/iter.rs`（96 行）
**角色**：children 迭代器族 + 祖先链迭代器。
**关键结构与不变量**：`SyntaxIdxChildren`（L5-10，产 `(index, element)`）；`SyntaxChildren`（L12-14，newtype 包装丢 index）；trait `ChildrenIter`（L17-22）= DoubleEnded + ExactSize + Clone 的别名 trait（ blanket impl）——**约束了全部 children 类迭代器的能发**（syntax_node.rs L383/L441 的 `impl ChildrenIter + use<'a>` 返回）；`next` 内 while 跳过被 UNKNOWN 过滤掉的空槽（L28-35）但 **ExactSizeIterator::len 用 end-start 原始计数**（L51-55）——len 可能高估实际产出（与 UNKNOWN 过滤的已知张力）；`SyntaxAncestors`（L77-96）自底向上含自身迭代。
**公开 API**：两迭代器 + ChildrenIter trait + SyntaxAncestors::start_from。
**依赖/被依赖**：依赖 element/syntax_node；被 syntax_node.rs（children/children_with_idx）与 syntax.rs 引用。
**改动影响面**：下游若依赖 len()==产出数的假设会被 UNKNOWN 槽打破。
**集成点**：需要 child 下标（如生成 AST 的 index 算术对账）时用 with_idx 版。

## `crates/slang-sys/src/syntax/cursor.rs`（136 行）
**角色**：`SyntaxCursor`——可复用的树上游标（walk/preorder 的引擎）。
**关键结构与不变量**：`SyntaxCursor { elem, path: Vec<(SyntaxNode, usize)> }`（L8-11）——path 栈存 (父节点, 子下标)，root 判定=path 空（L38-40）；`goto_first_child`（L49-59）push 并落位第一个**非空**孩子；sibling 移动在循环里跳空槽（L81-107）；`goto_first_child_after_pos`/`goto_last_child_before_pos`（L109-135）按字节位置选枝（IDE 光标定位）；`reset_to_root` 用 path.first 回根（L42-47）。
**公开 API**：new/to_elem/to_node/to_tok_with_parent/to_token/idx/is_root/reset_to_root/goto_first_child/goto_last_child/goto_parent/goto_next_sibling/goto_prev_sibling/goto_first_child_after_pos/goto_last_child_before_pos。
**依赖/被依赖**：依赖 element/syntax_node；被 syntax_node.rs（walk/first_token）与 walk.rs 引用。
**改动影响面**：`first_token`（syntax_node.rs L183-196）的正确性依赖 sibling 跳空语义。
**集成点**：写光标邻近查询（"光标左/右侧 token"）的标准工具。

## `crates/slang-sys/src/syntax/walk.rs`（104 行）
**角色**：两个 preorder 迭代器（node-only 与 node+token）。
**关键结构与不变量**：`WalkEvent<T> { Enter, Leave }`（L4-8）；`SyntaxNodePreorder`（L11-63）：`leaving` 标志驱动，Enter 时深潜（跳过 token 元素 L47-56），Leave 时找 next sibling 或上溯（L37-46）——**产出的是纯 node 序列**；`SyntaxElemPreorder`（L65-104）不跳 token，Leave 后直接 sibling（L92-97）。终止条件统一 `leaving && is_root`（L27/L82）。
**公开 API**：WalkEvent + 两迭代器 new/Iterator。
**依赖/被依赖**：依赖 cursor/element/syntax_node；被 syntax_node.rs（node_preorder/elem_preorder/tokens）引用。
**改动影响面**：`tokens()`（syntax_node.rs L206-211）= elem_preorder 过滤 Enter(Token)，语义改动波及全 token 扫描。
**集成点**：语法高亮（token 流）、结构化遍历（node 流）分别对应两个迭代器。

## `crates/slang-sys/src/syntax/trivia.rs`（132 行）
**角色**：`SyntaxTrivia`——token 附属注释/空白/directive 视图。
**关键结构与不变量**：`SyntaxTrivia { token, index, raw_text: String, tree }`（L12-18）——**raw_text 在构造时拷贝固化**（from_token L44-49，assert 界内 L46），此后 `get_raw_text` 返回 &str 不再进 FFI；PartialEq/Hash 含 raw_text（L20-34）——同 token 同 index 但文本不同视为不同（防树重建后误等）；`SyntaxTriviaLoc`（L37-42）；`explicit_location`（L61-78，include/endinclude 行指令产物）；`syntax()`（L80-85）返回 directive trivia 挂的内嵌语法节点（`` `ifdef `` 分支体等的入口）；`SyntaxTriviaIter`（L88-132）DoubleEnded + ExactSize。
**公开 API**：SyntaxTrivia（kind/get_raw_text/syntax）+ SyntaxTriviaLoc + 迭代器。
**依赖/被依赖**：依赖 ffi/syntax_node/tree/source_buffer/token；被 syntax_node.rs（trivia_at/trivias/trivias_with_loc）与 syntax.rs 引用；被 crates/syntax/slang_ext/trivia.rs 消费。
**改动影响面**：raw_text 固化策略与 tree.rs 测试 L522-535（"inline trivia read without borrowing a temporary view"）互为因果。
**集成点**：注释提取/折叠、`syntax()` 是条件编译区段分析的钥匙。

## `crates/slang-sys/src/syntax/ffi.rs`（375 行）
**角色**：syntax 桥 DSL——全 crate 最大的桥面（5 个 namespace 段、约 70 个 extern 声明）。
**关键结构与不变量**：
- Raw 结构 13 个（L11-157）：`RawTrace` 全家（SourceBuffer/SourceRange/Token/MacroParam/ActualArgument/Event/TokenOrigin/EmittedToken/IncludeEdge）、`RawSVInt`、`RawOptionalU32`、`RawExpectedSyntax`——全部平坦 + has_* 模式。
- 不透明类型 L158-164：`SyntaxTree/SyntaxNode/SyntaxToken`（指向 wrapper.h 的 slang 类型别名）。
- 分段：`slang_sys::syntax::tree`（L166-199，parse_syntax_tree 13 参——`#[allow(clippy::too_many_arguments)]` L3 压制）、`::node`（L201-248，**unsafe 裸指针进出的 17 个访问器**，range_with_context 系列带 owner: &SyntaxTree 防跨树指针）、`::token`（L250-303 值访问器 + L329-337 keyword/directive 表）、`::trivia`（L305-327）、`::facts`（L339-374，31 个 u16 谓词/映射）。
- unsafe 标记原则：**凡收/返裸指针的声明都标 unsafe**（Rust 侧调用点必须 unsafe 块，见 syntax_node.rs），表查询类（&str 进 Vec 出）不标。
**公开 API**：`pub(crate) use slang_ffi::*`——crate 内全部 FFI 入口。
**依赖/被依赖**：被 facts/preproc/syntax_node/tree/trivia/value 依赖（crate 内最大入度之一）；被 build.rs 桥清单引用；图谱 depends_on syntax/wrapper.cpp。
**改动影响面**：本文件是三语言缝合处——改一处动 wrapper.h/.cpp + Rust 调用点；node/token 的 range 四段式拆分（valid+start/end buffer/offset）是 SourceRange 拼装的源头。
**集成点**：给语法树暴露新能力的桥面模板——新函数按所属 namespace 段归位即可被 cxx 正确路由。

---

## 附：单元级要点速览

- **升级 slang submodule 的检查单**：跑 `cargo build -p slang-sys`（5 生成器全跑）→ `cargo test -p slang-sys`（diagnostic.rs 元数据采样 + syntax.rs 12 集成测试 + tree.rs/trivia 测试是四道闸）→ 同步 Cargo.toml L4 版本号。
- **三条手工镜像线（改一侧必改另一侧）**：①TraceTokenOrigin kind 常量（preproc.rs L109-116 ↔ wrapper.cpp L862-921/L923）；②Bit 的 128/64 编码（value.rs L128-138 ↔ slang logic_t）；③生成的 kind/diag code 序号 ↔ slang C++ 枚举值。
- **借用模型一句话**：`SyntaxTree`（SharedPtr，Send+Sync）拥有一切；`SyntaxNode/SyntaxToken`（NonNull+&tree）只是视图；跨 FFI 的数据要么 Raw* 拷贝、要么就是这些短命视图。

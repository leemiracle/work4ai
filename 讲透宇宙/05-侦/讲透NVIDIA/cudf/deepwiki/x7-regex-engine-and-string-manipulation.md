<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cudf · extra page Regex Engine and String Manipulation · fetched 2026-10-26 -->

# Regex Engine and String Manipulation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cpp/benchmarks/json/json.cu](cpp/benchmarks/json/json.cu)
- [cpp/benchmarks/string/replace.cpp](cpp/benchmarks/string/replace.cpp)
- [cpp/doxygen/regex.md](cpp/doxygen/regex.md)
- [cpp/include/cudf/detail/algorithms/copy_if.cuh](cpp/include/cudf/detail/algorithms/copy_if.cuh)
- [cpp/include/cudf/detail/algorithms/reduce.cuh](cpp/include/cudf/detail/algorithms/reduce.cuh)
- [cpp/include/cudf/detail/utilities/batched_memcpy.hpp](cpp/include/cudf/detail/utilities/batched_memcpy.hpp)
- [cpp/include/cudf/detail/utilities/batched_memset.hpp](cpp/include/cudf/detail/utilities/batched_memset.hpp)
- [cpp/include/cudf/json/json.hpp](cpp/include/cudf/json/json.hpp)
- [cpp/include/cudf/reduction/detail/reduction.cuh](cpp/include/cudf/reduction/detail/reduction.cuh)
- [cpp/include/cudf/reduction/detail/segmented_reduction.cuh](cpp/include/cudf/reduction/detail/segmented_reduction.cuh)
- [cpp/include/cudf/strings/capitalize.hpp](cpp/include/cudf/strings/capitalize.hpp)
- [cpp/include/cudf/strings/case.hpp](cpp/include/cudf/strings/case.hpp)
- [cpp/include/cudf/strings/char_types/char_types.hpp](cpp/include/cudf/strings/char_types/char_types.hpp)
- [cpp/include/cudf/strings/detail/copy_if_else.cuh](cpp/include/cudf/strings/detail/copy_if_else.cuh)
- [cpp/include/cudf/strings/detail/find.hpp](cpp/include/cudf/strings/detail/find.hpp)
- [cpp/include/cudf/strings/detail/gather.cuh](cpp/include/cudf/strings/detail/gather.cuh)
- [cpp/include/cudf/strings/detail/replace.hpp](cpp/include/cudf/strings/detail/replace.hpp)
- [cpp/include/cudf/strings/detail/scatter.cuh](cpp/include/cudf/strings/detail/scatter.cuh)
- [cpp/include/cudf/strings/detail/split.hpp](cpp/include/cudf/strings/detail/split.hpp)
- [cpp/include/cudf/strings/detail/split_utils.cuh](cpp/include/cudf/strings/detail/split_utils.cuh)
- [cpp/include/cudf/strings/detail/strings_children.cuh](cpp/include/cudf/strings/detail/strings_children.cuh)
- [cpp/include/cudf/strings/detail/strings_column_factories.cuh](cpp/include/cudf/strings/detail/strings_column_factories.cuh)
- [cpp/include/cudf/strings/detail/strip.cuh](cpp/include/cudf/strings/detail/strip.cuh)
- [cpp/include/cudf/strings/detail/utilities.cuh](cpp/include/cudf/strings/detail/utilities.cuh)
- [cpp/include/cudf/strings/detail/utilities.hpp](cpp/include/cudf/strings/detail/utilities.hpp)
- [cpp/include/cudf/strings/extract.hpp](cpp/include/cudf/strings/extract.hpp)
- [cpp/include/cudf/strings/findall.hpp](cpp/include/cudf/strings/findall.hpp)
- [cpp/include/cudf/strings/padding.hpp](cpp/include/cudf/strings/padding.hpp)
- [cpp/include/cudf/strings/regex/flags.hpp](cpp/include/cudf/strings/regex/flags.hpp)
- [cpp/include/cudf/strings/regex/regex_program.hpp](cpp/include/cudf/strings/regex/regex_program.hpp)
- [cpp/include/cudf/strings/replace.hpp](cpp/include/cudf/strings/replace.hpp)
- [cpp/include/cudf/strings/replace_re.hpp](cpp/include/cudf/strings/replace_re.hpp)
- [cpp/include/cudf/strings/side_type.hpp](cpp/include/cudf/strings/side_type.hpp)
- [cpp/include/cudf/strings/split/partition.hpp](cpp/include/cudf/strings/split/partition.hpp)
- [cpp/include/cudf/strings/split/split.hpp](cpp/include/cudf/strings/split/split.hpp)
- [cpp/include/cudf/strings/split/split_re.hpp](cpp/include/cudf/strings/split/split_re.hpp)
- [cpp/include/cudf/strings/strip.hpp](cpp/include/cudf/strings/strip.hpp)
- [cpp/src/io/csv/durations.cu](cpp/src/io/csv/durations.cu)
- [cpp/src/json/json_path.cu](cpp/src/json/json_path.cu)
- [cpp/src/strings/capitalize.cu](cpp/src/strings/capitalize.cu)
- [cpp/src/strings/case.cu](cpp/src/strings/case.cu)
- [cpp/src/strings/char_types/char_types.cu](cpp/src/strings/char_types/char_types.cu)
- [cpp/src/strings/contains.cu](cpp/src/strings/contains.cu)
- [cpp/src/strings/count_matches.cu](cpp/src/strings/count_matches.cu)
- [cpp/src/strings/count_matches.hpp](cpp/src/strings/count_matches.hpp)
- [cpp/src/strings/extract/extract.cu](cpp/src/strings/extract/extract.cu)
- [cpp/src/strings/extract/extract_all.cu](cpp/src/strings/extract/extract_all.cu)
- [cpp/src/strings/padding.cu](cpp/src/strings/padding.cu)
- [cpp/src/strings/regex/regcomp.cpp](cpp/src/strings/regex/regcomp.cpp)
- [cpp/src/strings/regex/regcomp.h](cpp/src/strings/regex/regcomp.h)
- [cpp/src/strings/regex/regex.cuh](cpp/src/strings/regex/regex.cuh)
- [cpp/src/strings/regex/regex.inl](cpp/src/strings/regex/regex.inl)
- [cpp/src/strings/regex/regex_program.cpp](cpp/src/strings/regex/regex_program.cpp)
- [cpp/src/strings/replace/backref_re.cu](cpp/src/strings/replace/backref_re.cu)
- [cpp/src/strings/replace/backref_re.cuh](cpp/src/strings/replace/backref_re.cuh)
- [cpp/src/strings/replace/multi.cu](cpp/src/strings/replace/multi.cu)
- [cpp/src/strings/replace/replace.cu](cpp/src/strings/replace/replace.cu)
- [cpp/src/strings/replace/replace_nulls.cu](cpp/src/strings/replace/replace_nulls.cu)
- [cpp/src/strings/replace/replace_re.cu](cpp/src/strings/replace/replace_re.cu)
- [cpp/src/strings/replace/replace_slice.cu](cpp/src/strings/replace/replace_slice.cu)
- [cpp/src/strings/search/count.cu](cpp/src/strings/search/count.cu)
- [cpp/src/strings/search/findall.cu](cpp/src/strings/search/findall.cu)
- [cpp/src/strings/split/partition.cu](cpp/src/strings/split/partition.cu)
- [cpp/src/strings/split/split.cu](cpp/src/strings/split/split.cu)
- [cpp/src/strings/split/split.cuh](cpp/src/strings/split/split.cuh)
- [cpp/src/strings/split/split_part.cu](cpp/src/strings/split/split_part.cu)
- [cpp/src/strings/split/split_re.cu](cpp/src/strings/split/split_re.cu)
- [cpp/src/strings/split/split_record.cu](cpp/src/strings/split/split_record.cu)
- [cpp/src/strings/strip.cu](cpp/src/strings/strip.cu)
- [cpp/src/strings/utilities.cu](cpp/src/strings/utilities.cu)
- [cpp/src/strings/wrap.cu](cpp/src/strings/wrap.cu)
- [cpp/tests/json/json_tests.cpp](cpp/tests/json/json_tests.cpp)
- [cpp/tests/streams/strings/replace_test.cpp](cpp/tests/streams/strings/replace_test.cpp)
- [cpp/tests/streams/strings/split_test.cpp](cpp/tests/streams/strings/split_test.cpp)
- [cpp/tests/strings/attrs_tests.cpp](cpp/tests/strings/attrs_tests.cpp)
- [cpp/tests/strings/booleans_tests.cpp](cpp/tests/strings/booleans_tests.cpp)
- [cpp/tests/strings/case_tests.cpp](cpp/tests/strings/case_tests.cpp)
- [cpp/tests/strings/chars_types_tests.cpp](cpp/tests/strings/chars_types_tests.cpp)
- [cpp/tests/strings/concatenate_tests.cpp](cpp/tests/strings/concatenate_tests.cpp)
- [cpp/tests/strings/contains_tests.cpp](cpp/tests/strings/contains_tests.cpp)
- [cpp/tests/strings/extract_tests.cpp](cpp/tests/strings/extract_tests.cpp)
- [cpp/tests/strings/fill_tests.cpp](cpp/tests/strings/fill_tests.cpp)
- [cpp/tests/strings/findall_tests.cpp](cpp/tests/strings/findall_tests.cpp)
- [cpp/tests/strings/pad_tests.cpp](cpp/tests/strings/pad_tests.cpp)
- [cpp/tests/strings/replace_regex_tests.cpp](cpp/tests/strings/replace_regex_tests.cpp)
- [cpp/tests/strings/replace_tests.cpp](cpp/tests/strings/replace_tests.cpp)
- [cpp/tests/strings/split_tests.cpp](cpp/tests/strings/split_tests.cpp)
- [cpp/tests/strings/strip_tests.cpp](cpp/tests/strings/strip_tests.cpp)

</details>



## Purpose and Scope
This page details the implementation of libcudf's regular expression engine and strings manipulation primitives (`nvtext`/`strings`). It covers regex compilation (`regcomp.cpp`), device-side execution states (`regex.inl`), search/extraction (`contains`, `extract`, `findall`), regular expression-based replacements with backreferences, splitting and partitioning utilities (`split.cu`, `split_record.cu`), as well as character casing, filtering, and padding helpers.

---

## 1. Regex Engine Architecture

The libcudf regular expression engine compiles standard regular expression patterns into a GPU-executable representation called `reprog` (host-side) and `reprog_device` (device-side).

### Compilation Pipeline (`regcomp`)
The compilation process starts on the host where UTF-8 patterns are converted to 32-bit character vectors (`cpp/src/strings/regex/regcomp.cpp:74-92`) via `string_to_char32_vector()`. The `regex_parser` class parses the pattern, creates instruction opcodes (such as `CAT`, `STAR`, `PLUS`, `QUEST`), and builds character classes (`reclass`) for ranges like `\d`, `\w`, and `\s` `[cpp/src/strings/regex/regcomp.cpp:48-61]`.

The compiled program manages instructions and class definitions through `reprog` mutation APIs:
- `reprog::add_inst()` adds regex instructions `[cpp/src/strings/regex/regcomp.cpp:96-109]`.
- `reprog::add_class()` appends character classification metadata `[cpp/src/strings/regex/regcomp.cpp:111-115]`.

### Device Evaluation State (`regex.inl`)
On the GPU, the regex engine evaluates strings using thread-local or warp-local state tracking structures. The `relist` struct manages instruction activation bitmaps and active character ranges per thread `[cpp/src/strings/regex/regex.inl:24-107]`.
- `relist::data_size_for()` computes buffer memory sizes based on the number of instructions `[cpp/src/strings/regex/regex.inl:28-31]`.
- `relist::activate()` enables a given instruction ID if not already marked in the current evaluation step `[cpp/src/strings/regex/regex.inl:66-75]`.
- `reprog_device::store()` and `reprog_device::load()` handle copying compiled program structures into shared memory or passing them to CUDA kernels `[cpp/src/strings/regex/regex.inl:144-185]`.

```mermaid
graph TD
    Pattern[""UTF-8 Regex Pattern""] --> Parser[""regex_parser (cpp/src/strings/regex/regcomp.cpp)""]
    Parser --> HostProg[""reprog Host Object""]
    HostProg --> DevStore[""reprog_device::store (cpp/src/strings/regex/regex.inl)""]
    DevStore --> RelistState[""relist State Machine (cpp/src/strings/regex/regex.inl)""]
    RelistState --> KernelExec[""CUDA Match Kernels""]

    subgraph "Code Entity Space"
        Parser
        HostProg
        DevStore
        RelistState
        KernelExec
    end

    Sources: cpp/src/strings/regex/regcomp.cpp:46-115, cpp/src/strings/regex/regex.inl:24-107
```

Sources: `cpp/src/strings/regex/regcomp.cpp:46-115`, `cpp/src/strings/regex/regex.inl:24-107`

---

## 2. Search and Extraction Operations

libcudf provides regex and substring search routines:
- **`contains`**: Checks whether a string matches a regex pattern or substring `[cpp/tests/strings/contains_tests.cpp:32-90]`.
- **`extract`**: Pulls out capturing groups from regular expression matches into separate output columns.
- **`findall`**: Returns all non-overlapping matches of a pattern within each string as a lists column.

Test suites such as `StringsContainsTests` validate various regex expressions (`\d`, `\w+`, `\s`, `\bworld\b`, character classes) across diverse ASCII and multi-byte UTF-8 inputs `[cpp/tests/strings/contains_tests.cpp:73-90]`.

Sources: `cpp/tests/strings/contains_tests.cpp:32-90`

---

## 3. Replacement and Backreferences

String replacement utilities support both literal patterns and regular expressions with backreferences (`\1`, `\2`, etc.):
- **`replace` / `replace_re`**: Scans strings for pattern matches and swaps them with replacement strings or backreferenced capture groups.
- **Backreference Resolution**: Handled via `backref_re.cu` and `replace_re.cu`, which parse capture group references in the replacement template and substitute matching substrings dynamically during device kernel execution.

Sources: `cpp/src/strings/replace/replace.cu`, `cpp/src/strings/replace/replace_re.cu`, `cpp/src/strings/replace/backref_re.cu`

---

## 4. Splitting and Partitioning

Splitting operations divide input strings into multiple tokens or separate columns based on explicit delimiters or whitespace.

### Split Implementation (`split.cu`, `split_record.cu`)
- **`split_helper()` & `split_fn()`**: Count delimiters across the entire column, record their positions, map them to individual strings, and construct a table of string columns (`[cpp/src/strings/split/split.cu:32-153]`).
- **Token Counting**: `token_count_fn` and `ws_token_count_fn` determine the number of tokens per row subject to an optional `max_tokens` limit (`[cpp/src/strings/split/split_record.cu:28-78]`).
- **Token Extraction**: `split_extract_fn`, `rsplit_extract_fn`, and `split_ws_extract_fn` slice strings into `string_index_pair` arrays (`[cpp/src/strings/split/split_record.cu:81-188]`).

```mermaid
graph TD
    InputCol[""strings_column_view (cpp/src/strings/split/split.cu)""] --> Helper[""split_helper / split_fn""]
    Helper --> CountFn[""token_count_fn / ws_token_count_fn (cpp/src/strings/split/split_record.cu)""]
    CountFn --> ExtractFn[""split_extract_fn / rsplit_extract_fn""]
    ExtractFn --> OutputTable[""unique_ptr<table> Output Columns""]

    subgraph "Code Entity Space"
        Helper
        CountFn
        ExtractFn
        OutputTable
    end

    Sources: cpp/src/strings/split/split.cu:32-153, cpp/src/strings/split/split_record.cu:28-188
```

Sources: `cpp/src/strings/split/split.cu:32-153`, `cpp/src/strings/split/split_record.cu:28-188`

---

## 5. Case and Padding Helpers

libcudf includes comprehensive character metadata tables and transformation functions for casing, filtering, and alignment.

### Casing and Title Case (`capitalize.cu`, `case.cu`)
- **`base_fn` & Title Case Tables**: `capitalize.cu` maintains `title_case_table` and `title_case_chars` constant memory arrays to handle Unicode characters with unique title-case rules `[cpp/src/strings/capitalize.cu:35-87]`.
- **Character Case Conversion**: `convert_char_fn` in `case.cu` accesses `multi_byte_cross_table` to map multi-byte UTF-8 characters across upper, lower, and title cases `[cpp/src/strings/case.cu:46-134]`.

### Character Type Filtering (`char_types.cu`)
- **`all_characters_of_type`**: Evaluates whether all characters in each string match specified character types (`string_character_types`) `[cpp/src/strings/char_types/char_types.cu:38-73]`.
- **`filter_characters_of_type`**: Removes or replaces characters matching particular flags using `filter_chars_fn` `[cpp/src/strings/char_types/char_types.cu:116-160]`.

Sources: `cpp/src/strings/capitalize.cu:31-135`, `cpp/src/strings/case.cu:40-135`, `cpp/src/strings/char_types/char_types.cu:38-160`, `cpp/include/cudf/strings/char_types/char_types.hpp:25-110`

---


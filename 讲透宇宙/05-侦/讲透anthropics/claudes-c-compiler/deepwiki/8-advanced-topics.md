<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claudes-c-compiler · page 8 Advanced Topics · fetched 2026-10-26 -->

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ideas/new_projects.txt](ideas/new_projects.txt)
- [src/common/const_arith.rs](src/common/const_arith.rs)
- [src/common/long_double.rs](src/common/long_double.rs)
- [src/frontend/preprocessor/README.md](src/frontend/preprocessor/README.md)
- [src/frontend/preprocessor/includes.rs](src/frontend/preprocessor/includes.rs)
- [src/frontend/preprocessor/utils.rs](src/frontend/preprocessor/utils.rs)
- [src/frontend/sema/const_eval.rs](src/frontend/sema/const_eval.rs)
- [src/frontend/sema/type_checker.rs](src/frontend/sema/type_checker.rs)
- [src/ir/lowering/complex.rs](src/ir/lowering/complex.rs)
- [src/ir/lowering/const_eval.rs](src/ir/lowering/const_eval.rs)
- [src/ir/lowering/expr_calls.rs](src/ir/lowering/expr_calls.rs)
- [src/ir/lowering/expr_types.rs](src/ir/lowering/expr_types.rs)
- [src/ir/lowering/global_init.rs](src/ir/lowering/global_init.rs)
- [src/ir/lowering/global_init_bytes.rs](src/ir/lowering/global_init_bytes.rs)
- [src/ir/lowering/global_init_compound.rs](src/ir/lowering/global_init_compound.rs)
- [src/ir/lowering/stmt_init.rs](src/ir/lowering/stmt_init.rs)
- [src/ir/lowering/stmt_return.rs](src/ir/lowering/stmt_return.rs)

</details>



This page covers specialized compiler features that require deep platform-specific knowledge and sophisticated handling across multiple compiler phases. These topics involve complex interactions between the frontend, IR lowering, and backend code generation.

The three main areas covered are:
- **Complex number support**: C99 `_Complex` types with platform-specific ABI handling
- **Long double precision**: 80-bit x87 vs 128-bit IEEE 754 binary128 representations
- **Constant evaluation**: Compile-time expression evaluation with architecture-aware semantics

For basic type system information, see [Type System](#3.2). For ABI handling in general, see [ABI Handling](#3.5). For backend code generation, see [Backend Code Generation](#5).

---

## 8.1 Complex Number Support

C99 `_Complex` types (`_Complex float`, `_Complex double`, `_Complex long double`) are represented in IR as stack-allocated pairs of floating-point values: `{real, imag}`. A complex value is always passed around as a pointer to this pair.

### Memory Layout

```mermaid
graph TB
    subgraph "Complex Type Layouts"
        CF["_Complex float<br/>8 bytes, align 4"]
        CD["_Complex double<br/>16 bytes, align 8"]
        CLD["_Complex long double<br/>x86-64: 32 bytes, align 16<br/>i686: 24 bytes, align 4"]
    end
    
    subgraph "Memory Structure"
        CF_MEM["[f32 real][f32 imag]"]
        CD_MEM["[f64 real][f64 imag]"]
        CLD_MEM["[f128 real][f128 imag]"]
    end
    
    CF --> CF_MEM
    CD --> CD_MEM
    CLD --> CLD_MEM
    
    subgraph "IR Representation"
        PTR["IrType::Ptr"]
        ALLOCA["Instruction::Alloca<br/>allocate stack space"]
        LOAD["Load real/imag via GEP"]
        STORE["Store real/imag via GEP"]
    end
    
    CF_MEM --> PTR
    CD_MEM --> PTR
    CLD_MEM --> PTR
    PTR --> ALLOCA
    ALLOCA --> LOAD
    ALLOCA --> STORE
```

**Sources**: [src/ir/lowering/complex.rs:1-48]()

### Core Complex Operations

The `Lowerer` struct in [src/ir/lowering/complex.rs]() provides methods for all complex operations:

| Method | Purpose | Formula |
|--------|---------|---------|
| `alloca_complex` | Allocate stack space for complex value | Returns `Value` pointer to `{real, imag}` |
| `store_complex_parts` | Store `(real, imag)` into alloca | Stores at offset 0 and `comp_size` |
| `load_complex_real` | Load real component | GEP offset 0 |
| `load_complex_imag` | Load imaginary component | GEP offset `comp_size` |
| `lower_complex_add` | Complex addition | `(a+bi) + (c+di) = (a+c) + (b+d)i` |
| `lower_complex_sub` | Complex subtraction | `(a+bi) - (c+di) = (a-c) + (b-d)i` |
| `lower_complex_mul` | Complex multiplication | `(a+bi)(c+di) = (ac-bd) + (ad+bc)i` |
| `lower_complex_div` | Complex division | `(a+bi)/(c+di) = ((ac+bd) + (bc-ad)i) / (c²+d²)` |
| `lower_complex_neg` | Complex negation | `-(a+bi) = (-a) + (-b)i` |
| `lower_complex_conj` | Complex conjugate | `conj(a+bi) = a + (-b)i` |

**Sources**: [src/ir/lowering/complex.rs:73-366]()

### Platform-Specific ABI Decomposition

```mermaid
graph LR
    subgraph "Complex ABI Classification"
        CFLOAT["_Complex float"]
        CDOUBLE["_Complex double"]
        CLDOUBLE["_Complex long double"]
    end
    
    subgraph "x86-64 SysV ABI"
        X86_CF["Packed in F64<br/>single XMM register"]
        X86_CD["Decomposed to (F64, F64)<br/>two XMM registers"]
        X86_CLD["Returned via ST(0)/ST(1)<br/>x87 FPU stack"]
    end
    
    subgraph "i686 i386 ABI"
        I686_CF["Packed in I64<br/>eax:edx registers"]
        I686_CD["Returned via sret<br/>hidden pointer"]
        I686_CLD["Returned via sret<br/>hidden pointer"]
    end
    
    subgraph "ARM/RISC-V ABI"
        ARM_CF["Decomposed to (F32, F32)<br/>two FP registers"]
        ARM_CD["Decomposed to (F64, F64)<br/>two FP registers"]
        ARM_CLD["Returned via sret<br/>hidden pointer"]
    end
    
    CFLOAT --> X86_CF
    CFLOAT --> I686_CF
    CFLOAT --> ARM_CF
    
    CDOUBLE --> X86_CD
    CDOUBLE --> I686_CD
    CDOUBLE --> ARM_CD
    
    CLDOUBLE --> X86_CLD
    CLDOUBLE --> I686_CLD
    CLDOUBLE --> ARM_CLD
```

**Sources**: [src/ir/lowering/expr_calls.rs:192-213](), [src/backend/common.rs]()

The function `decompose_complex_call_args` in [src/ir/lowering/expr_calls.rs:530-679]() handles ABI-compliant decomposition:

```mermaid
graph TB
    ARG["Complex Argument"]
    
    CHECK_TARGET{"Target Platform?"}
    CHECK_TYPE{"Complex Type?"}
    CHECK_VARIADIC{"Variadic Position?"}
    
    ARG --> CHECK_TARGET
    
    CHECK_TARGET -->|"x86-64"| X86_PATH["uses_packed_complex_float()<br/>decomposes_complex_double()"]
    CHECK_TARGET -->|"i686"| I686_PATH["No decomposition<br/>(struct ABI)"]
    CHECK_TARGET -->|"ARM/RISC-V"| ARM_PATH["decomposes_complex_float()<br/>decomposes_complex_double()"]
    
    X86_PATH --> CHECK_TYPE
    ARM_PATH --> CHECK_TYPE
    I686_PATH --> NO_DECOMPOSE["Pass as struct pointer"]
    
    CHECK_TYPE -->|"_Complex float"| CHECK_VARIADIC
    CHECK_TYPE -->|"_Complex double"| DECOMPOSE_D["load_complex_real()<br/>load_complex_imag()<br/>insert 2 FP args"]
    CHECK_TYPE -->|"Other"| NO_DECOMPOSE
    
    CHECK_VARIADIC -->|"Fixed param"| DECOMPOSE_F["Decompose to 2 F32/F64"]
    CHECK_VARIADIC -->|"Variadic param"| NO_DECOMPOSE
```

**Sources**: [src/ir/lowering/expr_calls.rs:530-679]()

### Complex Type Detection and Conversions

The `expr_ctype` method in [src/ir/lowering/complex.rs:424-519]() determines expression types with complex-aware overrides:

| Expression Pattern | Type Resolution |
|-------------------|-----------------|
| `__builtin_complex(real, imag)` | Depends on argument types |
| `conj(z)` / `conjf(z)` / `conjl(z)` | Same as argument |
| Arithmetic on complex operands | Uses `common_complex_type` for promotion |
| Conditionals with complex branches | Complex-aware type resolution |

The conversion helpers handle all type combinations:

- `real_to_complex`: Scalar to complex `(real, 0i)`
- `scalar_to_complex`: IR type to complex (preferred for calls)
- `complex_to_complex`: Between complex precisions
- `lower_complex_to_bool`: `(real != 0) || (imag != 0)` per C11 6.3.1.2

**Sources**: [src/ir/lowering/complex.rs:368-519]()

### Global Initialization with Complex Values

```mermaid
graph TB
    GLOBAL["Global Complex Variable"]
    
    INIT_TYPE{"Initializer Type?"}
    
    GLOBAL --> INIT_TYPE
    
    INIT_TYPE -->|"Scalar"| SCALAR["eval_const_expr<br/>Set real = scalar<br/>Set imag = 0"]
    INIT_TYPE -->|"Imaginary literal"| IMAG["ImaginaryLiteral<br/>Set real = 0<br/>Set imag = value"]
    INIT_TYPE -->|"Expression"| EVAL["eval_complex_global_init<br/>Try builtin_complex<br/>Extract real/imag"]
    INIT_TYPE -->|"Initializer list"| LIST["lower_complex_array_init<br/>Process pairs of values<br/>Pack into complex elements"]
    
    subgraph "Byte Serialization"
        SCALAR --> BYTES["write_const_to_bytes<br/>little-endian layout"]
        IMAG --> BYTES
        EVAL --> BYTES
        LIST --> ARRAY_BYTES["Fill array with<br/>interleaved real/imag"]
    end
```

The function `eval_complex_global_init` in [src/ir/lowering/global_init.rs:1462-1515]() handles complex constant evaluation, while `lower_complex_array_init` in [src/ir/lowering/global_init.rs:1517-1581]() handles arrays of complex values.

**Sources**: [src/ir/lowering/global_init.rs:1462-1581](), [src/ir/lowering/global_init_bytes.rs:456-488]()

---

## 8.2 Long Double Handling

The `long double` type has different representations depending on architecture:
- **x86-64**: 80-bit x87 extended precision (16 bytes with padding)
- **AArch64/RISC-V**: IEEE 754 binary128 quad precision (16 bytes)

### Format Structures

```mermaid
graph TB
    subgraph "x87 80-bit Format (x86-64, i686)"
        X87["16 bytes total"]
        X87_SIGN["Bit 79: Sign"]
        X87_EXP["Bits 78-64: 15-bit exponent<br/>bias 16383"]
        X87_INT["Bit 63: Explicit integer bit"]
        X87_MANT["Bits 62-0: 63-bit mantissa"]
        X87_PAD["Bytes 10-15: Padding<br/>(6 bytes)"]
        
        X87 --> X87_SIGN
        X87 --> X87_EXP
        X87 --> X87_INT
        X87 --> X87_MANT
        X87 --> X87_PAD
    end
    
    subgraph "IEEE 754 binary128 (ARM, RISC-V)"
        F128["16 bytes total"]
        F128_SIGN["Bit 127: Sign"]
        F128_EXP["Bits 126-112: 15-bit exponent<br/>bias 16383"]
        F128_MANT["Bits 111-0: 112-bit mantissa<br/>implicit leading 1"]
        
        F128 --> F128_SIGN
        F128 --> F128_EXP
        F128 --> F128_MANT
    end
    
    subgraph "IrConst Representation"
        IRCONST["IrConst::LongDouble(f64, [u8; 16])"]
        APPROX["f64: Approximate value<br/>for quick comparisons"]
        BYTES["[u8; 16]: Full precision bytes"]
        
        IRCONST --> APPROX
        IRCONST --> BYTES
    end
```

**Sources**: [src/common/long_double.rs:1-21]()

### Parsing Long Double Literals

The parsing pipeline in [src/common/long_double.rs]() uses `BigUint` for arbitrary-precision decimal arithmetic:

```mermaid
graph TB
    LITERAL["Long Double Literal<br/>e.g., 1.23456789012345678901L"]
    
    PREPARSE["preparse_long_double<br/>Strip suffix, detect sign"]
    
    FORMAT{"Format?"}
    
    LITERAL --> PREPARSE
    PREPARSE --> FORMAT
    
    FORMAT -->|"Hex"| HEX["parse_hex_float_x87/f128<br/>Direct binary conversion"]
    FORMAT -->|"Infinity"| INF["Return ±infinity pattern<br/>x87: 0x7FFF8000000000000000<br/>f128: 0x7FFF0000000000000000"]
    FORMAT -->|"NaN"| NAN["Return NaN pattern<br/>x87: 0x7FFFC000000000000000<br/>f128: 0x7FFF8000000000000000"]
    FORMAT -->|"Decimal"| DEC["parse_decimal_to_x87/f128"]
    
    subgraph "Decimal Parsing with BigUint"
        DEC --> SPLIT["Split into integer.fraction"]
        SPLIT --> INT_PART["Integer: BigUint::from_decimal_digits"]
        SPLIT --> FRAC_PART["Fraction: Build BigUint<br/>multiply by powers of 2"]
        INT_PART --> COMBINE["Combine and normalize"]
        FRAC_PART --> COMBINE
        COMBINE --> ROUND["Round to 64-bit (x87)<br/>or 113-bit (f128) mantissa"]
        ROUND --> PACK["Pack into byte array"]
    end
    
    HEX --> RESULT["[u8; 16] bytes"]
    INF --> RESULT
    NAN --> RESULT
    PACK --> RESULT
```

The key functions are:
- `parse_long_double_x87`: x86/i686 target, returns 80-bit x87 format
- `parse_long_double_f128`: ARM/RISC-V target, returns 128-bit IEEE format
- `BigUint::from_decimal_digits`: Converts decimal digit array to binary limbs
- `BigUint::shl` and `BigUint::mul_u32`: High-precision arithmetic operations

**Sources**: [src/common/long_double.rs:35-270](), [src/common/long_double.rs:68-171]()

### Software Arithmetic Operations

All long double arithmetic is implemented in pure software without inline assembly:

```mermaid
graph LR
    subgraph "x87 Operations"
        X87_ADD["x87_add(a, b)<br/>Decompose, align exponents<br/>Add mantissas, normalize"]
        X87_SUB["x87_sub(a, b)<br/>Decompose, align exponents<br/>Subtract mantissas, normalize"]
        X87_MUL["x87_mul(a, b)<br/>Decompose, multiply mantissas<br/>(128-bit × 128-bit)<br/>Normalize, round"]
        X87_DIV["x87_div(a, b)<br/>Decompose, divide mantissas<br/>Normalize, round"]
    end
    
    subgraph "f128 Operations"
        F128_ADD["f128_add(a, b)<br/>Same algorithm as x87<br/>but 113-bit mantissa"]
        F128_SUB["f128_sub(a, b)<br/>Same algorithm as x87<br/>but 113-bit mantissa"]
        F128_MUL["f128_mul(a, b)<br/>Same algorithm as x87<br/>but 113-bit mantissa"]
        F128_DIV["f128_div(a, b)<br/>Same algorithm as x87<br/>but 113-bit mantissa"]
    end
    
    subgraph "Shared Decompose Helpers"
        X87_DEC["x87_decompose(bytes)<br/>Extract (sign, exp, mantissa)"]
        F128_DEC["f128_decompose(bytes)<br/>Extract (sign, exp, mantissa)"]
    end
    
    X87_ADD --> X87_DEC
    X87_SUB --> X87_DEC
    X87_MUL --> X87_DEC
    X87_DIV --> X87_DEC
    
    F128_ADD --> F128_DEC
    F128_SUB --> F128_DEC
    F128_MUL --> F128_DEC
    F128_DIV --> F128_DEC
```

The decompose helpers return `(sign, exponent, mantissa)` tuples:
- `x87_decompose`: Returns `(bool, i32, u128)` with 64-bit mantissa (including explicit integer bit)
- `f128_decompose`: Returns `(bool, i32, u128)` with 113-bit mantissa (implicit leading 1 added)
- `f64_decompose`: Helper for conversions between precisions

**Sources**: [src/common/long_double.rs:272-1047]()

### Architecture-Specific Conversions

```mermaid
graph TB
    subgraph "Conversion Matrix"
        F64_TO_X87["f64_to_x87<br/>Widen 52-bit mantissa<br/>to 64-bit with explicit bit"]
        X87_TO_F64["x87_to_f64<br/>Round 64-bit mantissa<br/>to 52-bit, check overflow"]
        
        F64_TO_F128["f64_to_f128<br/>Widen 52-bit mantissa<br/>to 113-bit"]
        F128_TO_F64["f128_to_f64<br/>Round 113-bit mantissa<br/>to 52-bit"]
        
        X87_TO_F128["x87_to_f128<br/>Widen 64-bit to 113-bit<br/>Remove explicit int bit"]
        F128_TO_X87["f128_to_x87<br/>Round 113-bit to 64-bit<br/>Add explicit int bit"]
    end
    
    subgraph "Integer Conversions"
        I64_TO_X87["x87_from_i64<br/>Convert signed integer<br/>to normalized mantissa"]
        U64_TO_X87["x87_from_u64<br/>Convert unsigned integer<br/>to normalized mantissa"]
        I128_TO_X87["x87_from_i128<br/>Full 128-bit precision"]
        U128_TO_X87["x87_from_u128<br/>Full 128-bit precision"]
        
        X87_TO_I64["x87_to_i64<br/>Round to integer<br/>saturate on overflow"]
        X87_TO_U64["x87_to_u64<br/>Round to integer<br/>saturate on overflow"]
    end
    
    subgraph "Used By"
        CONST_EVAL["Constant Evaluation<br/>eval_const_expr"]
        GLOBAL_INIT["Global Initialization<br/>promote_to_long_double"]
        BACKEND["Backend Code Generation<br/>emit_cast"]
    end
    
    I64_TO_X87 --> CONST_EVAL
    X87_TO_F64 --> CONST_EVAL
    F64_TO_X87 --> GLOBAL_INIT
    X87_TO_I64 --> BACKEND
```

The conversion functions handle special cases:
- **Denormals**: x87 uses explicit integer bit, f128 uses implicit leading 1
- **Infinity**: Exponent all-ones, mantissa zero (with explicit bit set for x87)
- **NaN**: Exponent all-ones, mantissa non-zero (quiet NaN: high bit set)
- **Overflow**: When converting to narrower precision, clamp to ±infinity

**Sources**: [src/common/long_double.rs:1049-1380]()

### Long Double in Constant Evaluation

The constant evaluator handles long double literals with full precision:

```mermaid
graph TB
    LITERAL["FloatLiteralLongDouble(val, bytes, _)"]
    
    EVAL["eval_const_expr"]
    
    STORE["IrConst::LongDouble(val, bytes)"]
    
    LITERAL --> EVAL
    EVAL --> STORE
    
    subgraph "Operations"
        CAST["Cast to target type<br/>IrConst::cast_long_double_to_target"]
        BINOP["Binary operations<br/>eval_const_binop_long_double"]
        PROMOTE["Promote int/float<br/>promote_to_long_double_with_signedness"]
    end
    
    STORE --> CAST
    STORE --> BINOP
    STORE --> PROMOTE
    
    CAST --> ARCH_CHECK{"Target Architecture?"}
    ARCH_CHECK -->|"x86-64/i686"| X87_OPS["Use x87_* functions"]
    ARCH_CHECK -->|"ARM/RISC-V"| F128_OPS["Use f128_* functions"]
```

**Sources**: [src/ir/lowering/const_eval.rs:256-294](), [src/ir/lowering/global_init.rs:269-283]()

---

## 8.3 Constant Evaluation

Constant expression evaluation occurs at two levels: during semantic analysis (sema) and during IR lowering. Both share common arithmetic logic but have different type systems and state availability.

### Two-Phase Evaluation Architecture

```mermaid
graph TB
    subgraph "Frontend: Semantic Analysis"
        AST["AST Expression"]
        SEMA_EVAL["SemaConstEval::eval_const_expr"]
        SEMA_STATE["Sema State:<br/>TypeContext<br/>SymbolTable<br/>FunctionInfo"]
        SEMA_MAP["ConstMap<br/>(ExprId → IrConst)"]
        
        AST --> SEMA_EVAL
        SEMA_STATE --> SEMA_EVAL
        SEMA_EVAL --> SEMA_MAP
    end
    
    subgraph "Backend: IR Lowering"
        LOWER_EVAL["Lowerer::eval_const_expr"]
        LOWER_STATE["Lowering State:<br/>GlobalInfo<br/>func_state<br/>const_local_values<br/>struct_layouts"]
        LOOKUP["Check sema ConstMap<br/>O(1) fast path"]
        COMPUTE["Recompute with<br/>lowering-specific state"]
        
        LOWER_EVAL --> LOOKUP
        LOOKUP -->|"Cache hit"| RETURN["Return cached IrConst"]
        LOOKUP -->|"Cache miss"| COMPUTE
        LOWER_STATE --> COMPUTE
    end
    
    SEMA_MAP --> LOOKUP
    
    subgraph "Shared Arithmetic Core"
        SHARED["common::const_eval<br/>common::const_arith"]
        LITERAL["eval_literal"]
        BINOP["eval_binop_with_types"]
        PROMOTE["promote_sub_int"]
        
        SHARED --> LITERAL
        SHARED --> BINOP
        SHARED --> PROMOTE
    end
    
    SEMA_EVAL --> SHARED
    COMPUTE --> SHARED
    
    subgraph "Lowering-Only Features"
        GLOBAL_ADDR["eval_global_addr_expr<br/>&global, func, array"]
        LOCAL_CONST["const_local_values<br/>const-qualified locals"]
        PTR_DIFF["eval_const_ptr_diff<br/>pointer subtraction"]
        SIZEOF_RUNTIME["sizeof with runtime info<br/>unsized array dimensions"]
    end
    
    COMPUTE --> GLOBAL_ADDR
    COMPUTE --> LOCAL_CONST
    COMPUTE --> PTR_DIFF
    COMPUTE --> SIZEOF_RUNTIME
```

**Sources**: [src/frontend/sema/const_eval.rs:49-68](), [src/ir/lowering/const_eval.rs:26-255]()

### Constant Evaluation with Type-Aware Arithmetic

The shared arithmetic core in [src/common/const_arith.rs]() implements C semantics with width and signedness tracking:

```mermaid
graph LR
    subgraph "Type Information Flow"
        SEMA_TYPE["Sema: CType<br/>ctype_size()<br/>ctype.is_unsigned()"]
        LOWER_TYPE["Lowering: IrType<br/>ir_type.size()<br/>ir_type.is_unsigned()"]
        
        SHARED_PARAMS["Shared Function Parameters:<br/>(lhs_size: usize, lhs_unsigned: bool)<br/>(rhs_size: usize, rhs_unsigned: bool)"]
        
        SEMA_TYPE --> SHARED_PARAMS
        LOWER_TYPE --> SHARED_PARAMS
    end
    
    subgraph "Arithmetic Operations"
        BINOP["eval_binop_with_types"]
        INT_ARITH["eval_const_binop_int<br/>Handles 32-bit vs 64-bit<br/>Signed vs unsigned"]
        FLOAT_ARITH["eval_const_binop_float<br/>F32, F64, LongDouble"]
        LONG_DBL["eval_const_binop_long_double<br/>x87 vs f128 by architecture"]
        
        SHARED_PARAMS --> BINOP
        BINOP --> INT_ARITH
        BINOP --> FLOAT_ARITH
        BINOP --> LONG_DBL
    end
    
    subgraph "Result Width Preservation"
        RESULT["Return IrConst"]
        WIDTH_CHECK{"Operand Width?"}
        SIGN_CHECK{"Signedness?"}
        
        INT_ARITH --> WIDTH_CHECK
        WIDTH_CHECK -->|"32-bit"| SIGN_CHECK
        WIDTH_CHECK -->|"64-bit"| I64_RESULT["IrConst::I64"]
        SIGN_CHECK -->|"Unsigned"| I64_ZEXT["IrConst::I64<br/>(zero-extended u32)"]
        SIGN_CHECK -->|"Signed"| I32_RESULT["IrConst::I32"]
    end
```

**Sources**: [src/common/const_arith.rs:14-226]()

### Integer Promotion and Usual Arithmetic Conversions

C11 6.3.1.1 integer promotion and 6.3.1.8 usual arithmetic conversions are critical for correct constant folding:

| Operation | Rule | Implementation |
|-----------|------|----------------|
| Unary `+`, `-`, `~` | Promote operand to `int` (I32) | `promote_sub_int`: I8/U8/I16/U16 → I32 |
| Binary `+`, `-`, `*`, `/`, `%` | Convert both operands to common type | `eval_binop_with_types`: Compare sizes, promote |
| Bitwise `&`, `\|`, `^` | Integer promotion + usual arithmetic conversions | Same as binary arithmetic |
| Shift `<<`, `>>` | Promote left operand only | Left: `promote_sub_int`, Right: unchanged |
| Comparison `<`, `<=`, `>`, `>=` | Usual arithmetic conversions on operands | Result is always `int` (I32) |

The function `promote_sub_int` in [src/common/const_eval.rs:44-58]() handles sub-int types:

```rust
// Pseudocode based on actual implementation
fn promote_sub_int(val: IrConst, is_unsigned: bool) -> IrConst {
    match val {
        I8(v) => I32(v as i32),
        U8(v) => I32(v as u8 as i32),
        I16(v) => I32(v as i32),
        U16(v) => I32(v as u16 as i32),
        other => other,  // Already promoted
    }
}
```

**Sources**: [src/common/const_eval.rs:44-58](), [src/common/const_arith.rs:54-140]()

### Architecture-Aware sizeof Evaluation

The `sizeof` operator requires different handling in sema vs lowering:

```mermaid
graph TB
    SIZEOF["sizeof(expr or type)"]
    
    PHASE{"Evaluation Phase?"}
    
    SIZEOF --> PHASE
    
    PHASE -->|"Sema"| SEMA_SIZE["SemaConstEval::eval_sizeof<br/>Uses TypeContext"]
    PHASE -->|"Lowering"| LOWER_SIZE["Lowerer::sizeof_expr/sizeof_type<br/>Uses global metadata"]
    
    subgraph "Sema sizeof"
        SEMA_SIZE --> SEMA_RESOLVE["resolve_type_spec<br/>CType resolution"]
        SEMA_RESOLVE --> SEMA_LAYOUT["struct_layouts.get(key)<br/>layout.size"]
        SEMA_LAYOUT --> SEMA_UNSIZED["Unsized arrays:<br/>CType::size() = 0<br/>(dimension unknown yet)"]
    end
    
    subgraph "Lowering sizeof"
        LOWER_SIZE --> LOWER_GLOBAL["globals.get(name)<br/>actual allocated size"]
        LOWER_GLOBAL --> LOWER_INIT["Array sized from<br/>initializer element count"]
        LOWER_INIT --> LOWER_CORRECT["Correct dimension<br/>for sizeof(arr)/sizeof(arr[0])"]
    end
    
    subgraph "Why Two Phases?"
        REASON["Unsized array problem:<br/>PT cases[] = {{1,2},{3,4},...}<br/>Sema doesn't know count yet<br/>Lowering knows after analyze_declaration"]
    end
```

This is why `eval_const_expr` in the lowerer skips sema's cache for expressions containing `sizeof`:

```
if !matches!(expr, Expr::Identifier(_, _)) && !Self::expr_contains_sizeof(expr) {
    if let Some(val) = self.lookup_sema_const(expr) {
        return Some(val);  // Fast path: use pre-computed value
    }
}
```

**Sources**: [src/ir/lowering/const_eval.rs:34-87](), [src/frontend/sema/const_eval.rs:324-369]()

### Cast Chain Evaluation with Bit Tracking

Cast expressions require careful tracking of bit width and signedness through chains:

```mermaid
graph TB
    CAST["Cast Chain:<br/>(unsigned char)(int)(short)value"]
    
    EVAL["eval_const_cast<br/>Recursive evaluation"]
    
    FLOAT_CHECK{"Source is float?"}
    I128_CHECK{"Source is I128?"}
    BITS["eval_const_expr_as_bits<br/>Return (u64 bits, bool signed)"]
    
    CAST --> EVAL
    EVAL --> FLOAT_CHECK
    FLOAT_CHECK -->|"Yes"| FLOAT_CAST["IrConst::cast_float_to_target<br/>Value-based conversion"]
    FLOAT_CHECK -->|"No"| I128_CHECK
    I128_CHECK -->|"Yes"| I128_CAST["cast_i128_to_ir_type<br/>Full 128-bit value preserved"]
    I128_CHECK -->|"No"| BITS
    
    subgraph "Bit-based Cast Chain"
        BITS --> RECURSE["Recursive: eval_const_expr_as_bits(inner)"]
        RECURSE --> EXTRACT["(bits, src_signed) = result"]
        EXTRACT --> TRUNC["truncate_and_extend_bits<br/>Truncate to target width<br/>Sign/zero extend"]
        TRUNC --> FINAL_WIDTH["Return (bits, target_signed)"]
        FINAL_WIDTH --> TO_CONST["cast_bits_to_ir_const<br/>Convert to IrConst"]
    end
```

The function `truncate_and_extend_bits` in [src/common/const_arith.rs:228-243]() handles the width adjustment:

```rust
// Pseudocode based on actual implementation
fn truncate_and_extend_bits(bits: u64, target_width: u32, target_signed: bool) -> (u64, bool) {
    let mask = if target_width >= 64 { !0 } else { (1u64 << target_width) - 1 };
    let truncated = bits & mask;
    
    // Sign extend if target is signed and high bit is set
    let extended = if target_signed && (truncated & (1u64 << (target_width - 1))) != 0 {
        truncated | !mask  // Set all upper bits
    } else {
        truncated
    };
    
    (extended, target_signed)
}
```

**Sources**: [src/ir/lowering/const_eval.rs:257-294](), [src/common/const_arith.rs:228-243]()

### Global Address and Pointer Arithmetic

The lowering evaluator extends sema's capabilities with address expressions:

```mermaid
graph TB
    ADDR_EXPR["Address Expression:<br/>&global, func, array[3],<br/>struct.field, string+offset"]
    
    EVAL_GLOBAL["eval_global_addr_expr"]
    
    PATTERN{"Expression Pattern?"}
    
    ADDR_EXPR --> EVAL_GLOBAL
    EVAL_GLOBAL --> PATTERN
    
    PATTERN -->|"&identifier"| ADDR_OF["AddressOf(Identifier)<br/>Check globals, functions"]
    PATTERN -->|"&array[idx]"| ARRAY_ELEM["AddressOf(ArraySubscript)<br/>Base + idx * elem_size"]
    PATTERN -->|"&struct.field"| MEMBER["AddressOf(MemberAccess)<br/>Base + field_offset"]
    PATTERN -->|"identifier"| FUNC_OR_ARRAY["Function or array name<br/>Decays to pointer"]
    PATTERN -->|"string ± offset"| STRING_OFFSET["eval_string_literal_addr_expr<br/>Intern string, return label+offset"]
    
    ADDR_OF --> GLOBAL_ADDR["GlobalInit::GlobalAddr(label)"]
    ARRAY_ELEM --> OFFSET_ADDR["GlobalInit::GlobalAddrOffset(label, offset)"]
    MEMBER --> OFFSET_ADDR
    FUNC_OR_ARRAY --> GLOBAL_ADDR
    STRING_OFFSET --> OFFSET_ADDR
    
    subgraph "Pointer Difference"
        PTR_DIFF["eval_const_ptr_diff<br/>&arr[5] - &arr[0]"]
        DECOMPOSE["Extract base symbols and offsets"]
        SAME_BASE{"Same base symbol?"}
        COMPUTE_DIFF["(offset_lhs - offset_rhs) / elem_size"]
        
        PTR_DIFF --> DECOMPOSE
        DECOMPOSE --> SAME_BASE
        SAME_BASE -->|"Yes"| COMPUTE_DIFF
        SAME_BASE -->|"No"| FAIL["Return None"]
    end
```

**Sources**: [src/ir/lowering/const_eval_global_addr.rs:1-520](), [src/ir/lowering/const_eval.rs:158-165]()

### Constant Propagation in Optimization Passes

The IPCP (Interprocedural Constant Propagation) pass in [src/opt/ipcp.rs]() uses constant evaluation to propagate values across function boundaries:

```mermaid
graph LR
    IPCP["IPCP Pass"]
    
    SCAN["Scan all Call instructions"]
    
    CONST_ARGS{"All arguments<br/>are constants?"}
    
    CALLEE["Look up callee function"]
    
    MAP["Build param → const map"]
    
    PROPAGATE["Propagate into callee:<br/>Replace param uses<br/>with constants"]
    
    SIMPLIFY["Run simplify pass<br/>on callee"]
    
    DIRTY["Mark callee dirty<br/>for re-optimization"]
    
    IPCP --> SCAN
    SCAN --> CONST_ARGS
    CONST_ARGS -->|"Yes"| CALLEE
    CONST_ARGS -->|"No"| SKIP["Skip this call"]
    CALLEE --> MAP
    MAP --> PROPAGATE
    PROPAGATE --> SIMPLIFY
    SIMPLIFY --> DIRTY
```

**Sources**: [src/opt/ipcp.rs]()

---

## Summary

These advanced topics demonstrate the compiler's deep integration of platform-specific knowledge:

1. **Complex numbers**: Platform-specific ABI handling ensures correct parameter passing and return value conventions across all four target architectures, with decomposition for efficiency where applicable.

2. **Long double**: Full software arithmetic with arbitrary precision ensures correctness on both x87 (80-bit) and IEEE binary128 (128-bit) platforms, with careful handling of denormals, infinity, and NaN.

3. **Constant evaluation**: Two-phase evaluation (sema + lowering) with shared arithmetic core provides correct C semantics while allowing lowering-specific features like global address resolution and runtime sizeof computation.

**Sources**: [src/ir/lowering/complex.rs](), [src/common/long_double.rs](), [src/ir/lowering/const_eval.rs](), [src/frontend/sema/const_eval.rs](), [src/common/const_arith.rs]()

---


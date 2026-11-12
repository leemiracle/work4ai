<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claudes-c-compiler · page 6 Builtins and Intrinsics · fetched 2026-10-26 -->

# Builtins and Intrinsics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [projects/cleanup_code_quality.txt](projects/cleanup_code_quality.txt)
- [src/backend/arm/codegen/asm_emitter.rs](src/backend/arm/codegen/asm_emitter.rs)
- [src/backend/arm/codegen/inline_asm.rs](src/backend/arm/codegen/inline_asm.rs)
- [src/backend/arm/codegen/intrinsics.rs](src/backend/arm/codegen/intrinsics.rs)
- [src/backend/i686/codegen/asm_emitter.rs](src/backend/i686/codegen/asm_emitter.rs)
- [src/backend/i686/codegen/inline_asm.rs](src/backend/i686/codegen/inline_asm.rs)
- [src/backend/i686/codegen/intrinsics.rs](src/backend/i686/codegen/intrinsics.rs)
- [src/backend/inline_asm.rs](src/backend/inline_asm.rs)
- [src/backend/riscv/codegen/asm_emitter.rs](src/backend/riscv/codegen/asm_emitter.rs)
- [src/backend/riscv/codegen/inline_asm.rs](src/backend/riscv/codegen/inline_asm.rs)
- [src/backend/riscv/codegen/intrinsics.rs](src/backend/riscv/codegen/intrinsics.rs)
- [src/backend/x86/codegen/asm_emitter.rs](src/backend/x86/codegen/asm_emitter.rs)
- [src/backend/x86/codegen/inline_asm.rs](src/backend/x86/codegen/inline_asm.rs)
- [src/backend/x86/codegen/intrinsics.rs](src/backend/x86/codegen/intrinsics.rs)
- [src/backend/x86_common.rs](src/backend/x86_common.rs)
- [src/frontend/sema/builtins.rs](src/frontend/sema/builtins.rs)
- [src/ir/intrinsics.rs](src/ir/intrinsics.rs)
- [src/ir/lowering/expr_builtins.rs](src/ir/lowering/expr_builtins.rs)
- [src/ir/lowering/func_lowering.rs](src/ir/lowering/func_lowering.rs)
- [src/ir/module.rs](src/ir/module.rs)

</details>



This page documents the compiler's support for GCC-compatible builtin functions, hardware-specific intrinsics, and inline assembly. These features allow C programs to access compiler services (__builtin_* functions), hardware instructions (SSE/NEON/etc), and emit raw assembly code directly.

For detailed coverage of specific builtin functions, see [Builtin Functions](#6.1). For hardware intrinsics implementation details, see [Hardware Intrinsics](#6.2). For inline assembly constraint handling and template substitution, see [Inline Assembly](#6.3).

## Overview

The compiler implements three cross-cutting concerns that span the entire compilation pipeline:

1. **Builtin Functions**: Over 1000 `__builtin_*` functions for GCC compatibility (memory operations, math, overflow checking, type queries, etc.)
2. **Hardware Intrinsics**: Architecture-specific SIMD and crypto instructions (x86 SSE/AVX/AES, ARM NEON, RISC-V atomics)
3. **Inline Assembly**: GCC extended asm syntax with constraint resolution, register allocation, and template substitution

These features are handled at multiple compilation stages: semantic analysis (builtin resolution), IR lowering (dispatch and ABI handling), and backend code generation (native instruction emission).

## System Architecture

```mermaid
graph TB
    subgraph "Source Code"
        BUILTIN["__builtin_memcpy(dst, src, n)"]
        INTRIN["_mm_loadu_si128(ptr)"]
        ASM["asm volatile(template : outputs : inputs)"]
    end
    
    subgraph "Frontend - Semantic Analysis"
        RESOLVE["resolve_builtin(name)<br/>→ BuiltinInfo"]
        CLASSIFY["Classification:<br/>LibcAlias | Identity | Intrinsic"]
        TYPECHECK["Type checking<br/>const evaluation"]
    end
    
    subgraph "IR Lowering"
        DISPATCH["try_lower_builtin_call<br/>dispatch by BuiltinKind"]
        LIBCALL["LibcAlias → Call(memcpy)"]
        IDENTOP["Identity → first arg"]
        INTRINOP["Intrinsic → lower_builtin_intrinsic"]
        ASMPARSE["Inline ASM parsing<br/>constraint classification"]
    end
    
    subgraph "IR Representation"
        CALLIR["Instruction::Call"]
        INTRINSICIR["Instruction::Intrinsic<br/>IntrinsicOp enum"]
        ASMIR["Instruction::InlineAsm"]
    end
    
    subgraph "Backend Code Generation"
        X86EMIT["X86: SSE/AVX/AES<br/>x86-specific instructions"]
        ARMEMIT["ARM: NEON/Crypto<br/>AArch64 SIMD"]
        RVEMIT["RISC-V: Atomics/Vector<br/>scalar emulation"]
        ASMEMIT["InlineAsmEmitter trait<br/>constraint → register<br/>template substitution"]
    end
    
    subgraph "Assembly Output"
        ASMOUT["Native instructions:<br/>movdqu, aesenc (x86)<br/>ldr q0, aese (ARM)<br/>lr.w, fence (RISC-V)"]
    end
    
    BUILTIN --> RESOLVE
    INTRIN --> RESOLVE
    ASM --> ASMPARSE
    
    RESOLVE --> CLASSIFY
    CLASSIFY --> TYPECHECK
    TYPECHECK --> DISPATCH
    
    DISPATCH --> LIBCALL
    DISPATCH --> IDENTOP
    DISPATCH --> INTRINOP
    
    ASMPARSE --> ASMIR
    
    LIBCALL --> CALLIR
    IDENTOP --> CALLIR
    INTRINOP --> INTRINSICIR
    
    CALLIR --> X86EMIT
    INTRINSICIR --> X86EMIT
    INTRINSICIR --> ARMEMIT
    INTRINSICIR --> RVEMIT
    ASMIR --> ASMEMIT
    
    X86EMIT --> ASMOUT
    ARMEMIT --> ASMOUT
    RVEMIT --> ASMOUT
    ASMEMIT --> ASMOUT
```

**Diagram: Complete Builtins and Intrinsics Pipeline**

The system uses a three-tier classification at the frontend, followed by architecture-specific emission at the backend. Builtin functions are resolved by name in `BUILTIN_MAP`, classified by kind, and dispatched during IR lowering. Hardware intrinsics follow the same path but map to `IntrinsicOp` enums for backend emission. Inline assembly bypasses the builtin system entirely, using a shared framework for constraint resolution and operand substitution.

Sources: [src/frontend/sema/builtins.rs](), [src/ir/lowering/expr_builtins.rs](), [src/backend/inline_asm.rs]()

## Builtin Classification System

```mermaid
graph LR
    subgraph "BuiltinInfo Structure"
        KIND["BuiltinKind enum"]
        LIBC["LibcAlias(String)<br/>→ memcpy, strlen, etc."]
        IDENT["Identity<br/>→ return first arg"]
        INTRIN["Intrinsic(BuiltinIntrinsic)<br/>→ hardware ops"]
        CONST["ConstantF64(f64)<br/>→ compile-time constant"]
    end
    
    subgraph "BuiltinIntrinsic Categories"
        BIT["Bit Manipulation:<br/>Clz, Ctz, Bswap,<br/>Popcount, Parity"]
        OVER["Overflow Checking:<br/>AddOverflow, SubOverflow,<br/>MulOverflow, *OverflowP"]
        FP["FP Classification:<br/>FpClassify, IsNan,<br/>IsInf, IsFinite"]
        COMPLEX["Complex Numbers:<br/>ComplexReal, ComplexImag,<br/>ComplexConj, ComplexConstruct"]
        X86["x86 SIMD/Crypto:<br/>X86Lfence, X86Aesenc128,<br/>X86Pcmpeqb128, X86Crc32_*"]
        MISC["Miscellaneous:<br/>VaStart, VaEnd, VaCopy,<br/>ConstantP, ObjectSize,<br/>FrameAddress, ThreadPointer"]
    end
    
    KIND --> LIBC
    KIND --> IDENT
    KIND --> INTRIN
    KIND --> CONST
    
    INTRIN --> BIT
    INTRIN --> OVER
    INTRIN --> FP
    INTRIN --> COMPLEX
    INTRIN --> X86
    INTRIN --> MISC
```

**Diagram: Builtin Classification Taxonomy**

The `BuiltinInfo` struct in [src/frontend/sema/builtins.rs:10-47]() defines the classification. `LibcAlias` builtins emit direct function calls (e.g., `__builtin_memcpy` → `Call("memcpy")`). `Identity` builtins are no-ops that return their first argument unchanged (e.g., `__builtin_expect`). `Intrinsic` builtins map to `BuiltinIntrinsic` enums that receive special lowering and backend emission. `ConstantF64` represents compile-time constants like `__builtin_inf()`.

Sources: [src/frontend/sema/builtins.rs:10-47](), [src/ir/lowering/expr_builtins.rs:206-256]()

### Builtin Resolution Flow

| Stage | Component | File | Key Functions |
|-------|-----------|------|---------------|
| Registration | Static builtin map | [src/frontend/sema/builtins.rs:10-400]() | `BUILTIN_MAP: LazyLock<FxHashMap>` |
| Resolution | Name lookup | [src/frontend/sema/builtins.rs:402-408]() | `resolve_builtin(name) -> Option<BuiltinInfo>` |
| Lowering Dispatch | IR generation | [src/ir/lowering/expr_builtins.rs:37-256]() | `try_lower_builtin_call(name, args)` |
| Kind Handling | Type-specific lowering | [src/ir/lowering/expr_builtins.rs:258-467]() | `lower_builtin_intrinsic(intrinsic, name, args)` |
| Backend Emission | Instruction selection | [src/backend/x86/codegen/intrinsics.rs]() | `emit_intrinsic(op, dest, dest_ptr, args)` |

The builtin resolution flow starts with a static hashmap containing 1000+ entries. When the parser encounters a function call, semantic analysis checks `BUILTIN_MAP` before looking up user-defined functions. During IR lowering, `try_lower_builtin_call` dispatches on `BuiltinKind`, emitting `Call` instructions for `LibcAlias`, returning the first argument for `Identity`, or invoking `lower_builtin_intrinsic` for hardware operations.

Sources: [src/frontend/sema/builtins.rs](), [src/ir/lowering/expr_builtins.rs:37-256]()

## Hardware Intrinsics

```mermaid
graph TB
    subgraph "Frontend Registration"
        X86MAP["x86 SSE/AVX/AES mappings<br/>__builtin_ia32_*, _mm_*"]
        ARMMAP["ARM NEON mappings<br/>(handled as function calls)"]
        RVMAP["RISC-V atomic mappings<br/>(inline asm helpers)"]
    end
    
    subgraph "IR Intrinsic Operations"
        FENCE["Memory Barriers:<br/>Lfence, Mfence, Sfence, Pause"]
        STORE["Non-temporal Stores:<br/>Movnti, Movnti64, Movntdq, Movntpd"]
        PACKED["Packed Operations:<br/>Pcmpeqb128, Paddw128, Psubd128"]
        CRYPTO["Crypto Instructions:<br/>Aesenc128, Aesdec128, Crc32_*"]
        SHUFFLE["Shuffle/Pack:<br/>Pshufd128, Packssdw128, Punpcklbw128"]
        INSERT["Insert/Extract:<br/>Pinsrw128, Pextrw128, Pinsrd128"]
    end
    
    subgraph "Backend Platform Emission"
        X86IMPL["x86-64:<br/>movdqu, aesenc, crc32q<br/>REX/VEX/EVEX encoding"]
        ARMIMPL["AArch64:<br/>ldr q0, aese, crc32*<br/>NEON vector ops"]
        RVIMPL["RISC-V:<br/>Software emulation<br/>or scalar sequences"]
    end
    
    X86MAP --> FENCE
    X86MAP --> STORE
    X86MAP --> PACKED
    X86MAP --> CRYPTO
    X86MAP --> SHUFFLE
    X86MAP --> INSERT
    
    FENCE --> X86IMPL
    FENCE --> ARMIMPL
    FENCE --> RVIMPL
    
    STORE --> X86IMPL
    STORE --> ARMIMPL
    STORE --> RVIMPL
    
    PACKED --> X86IMPL
    PACKED --> ARMIMPL
    PACKED --> RVIMPL
    
    CRYPTO --> X86IMPL
    CRYPTO --> ARMIMPL
    CRYPTO --> RVIMPL
    
    SHUFFLE --> X86IMPL
    SHUFFLE --> ARMIMPL
    SHUFFLE --> RVIMPL
    
    INSERT --> X86IMPL
    INSERT --> ARMIMPL
    INSERT --> RVIMPL
```

**Diagram: Intrinsic Operation Flow by Architecture**

Hardware intrinsics use a platform-neutral `IntrinsicOp` enum defined in [src/ir/intrinsics.rs:19-119](). The frontend maps both `__builtin_ia32_*` names (GCC internal names) and `_mm_*` names (Intel header names) to the same intrinsic operations. During IR lowering, these become `Instruction::Intrinsic` nodes. Each backend implements `emit_intrinsic` to generate native instructions: x86-64 emits SSE/AVX instructions directly, AArch64 uses NEON equivalents, and RISC-V either emits atomics or software-emulates SIMD operations using scalar instructions.

Sources: [src/ir/intrinsics.rs:19-119](), [src/backend/x86/codegen/intrinsics.rs](), [src/backend/arm/codegen/intrinsics.rs](), [src/backend/riscv/codegen/intrinsics.rs]()

### x86-64 Intrinsic Coverage

| Category | Example Operations | Native Instructions | Source |
|----------|-------------------|---------------------|--------|
| Memory Fences | `_mm_lfence`, `_mm_mfence` | `lfence`, `mfence`, `sfence` | [src/backend/x86/codegen/intrinsics.rs:24-28]() |
| SSE Load/Store | `_mm_loadu_si128`, `_mm_storeu_si128` | `movdqu` | [src/backend/x86/codegen/intrinsics.rs:101-118]() |
| Packed Compare | `_mm_cmpeq_epi8`, `_mm_cmpeq_epi32` | `pcmpeqb`, `pcmpeqd` | [src/backend/x86/codegen/intrinsics.rs:119-142]() |
| AES-NI | `_mm_aesenc_si128`, `_mm_aesdec_si128` | `aesenc`, `aesdec`, `aesimc` | [src/backend/x86/codegen/intrinsics.rs:246-283]() |
| CLMUL | `_mm_clmulepi64_si128` | `pclmulqdq` | [src/backend/x86/codegen/intrinsics.rs:284-304]() |
| CRC32 | `_mm_crc32_u8`, `_mm_crc32_u64` | `crc32b`, `crc32q` | [src/backend/x86/codegen/intrinsics.rs:305-356]() |
| Shuffle | `_mm_shuffle_epi32`, `_mm_shufflelo_epi16` | `pshufd`, `pshuflw` | [src/backend/x86/codegen/intrinsics.rs:357-392]() |

The x86-64 backend supports 300+ intrinsics covering SSE, SSE2, SSE4.1, AES-NI, and CRC32 extensions. Each intrinsic maps to one or more native x86 instructions with appropriate REX/VEX prefix encoding. For example, `_mm_aesenc_si128` loads two 128-bit operands into `xmm0`/`xmm1`, executes `aesenc %xmm1, %xmm0`, and stores the result.

Sources: [src/backend/x86/codegen/intrinsics.rs:1-500](), [src/frontend/sema/builtins.rs:274-360]()

## Inline Assembly Framework

```mermaid
graph TB
    subgraph "AST Representation"
        TEMPLATE["Template string<br/>with % operands"]
        OUTPUTS["Output operands:<br/>[(constraint, value, name)]"]
        INPUTS["Input operands:<br/>[(constraint, value, name)]"]
        CLOBBERS["Clobber list:<br/>registers, cc, memory"]
    end
    
    subgraph "Shared Framework - Phase 1"
        CLASSIFY["classify_constraint<br/>→ AsmOperandKind"]
        KINDENUM["GpReg | FpReg | Memory |<br/>Specific(reg) | Tied(idx) |<br/>Immediate | Address"]
        METADATA["setup_operand_metadata<br/>mem_offset, imm_value"]
        RESOLVE["resolve_memory_operand<br/>indirect addressing"]
        ASSIGN["assign_scratch_reg<br/>register allocation"]
    end
    
    subgraph "Shared Framework - Phase 2-4"
        LOADINPUT["load_input_to_reg<br/>stack → register"]
        PRELOAD["preload_readwrite_output<br/>+ constraints"]
        SUBSTITUTE["substitute_template_line<br/>%0, %[name] → registers"]
        STORE["store_output_from_reg<br/>register → stack"]
    end
    
    subgraph "InlineAsmEmitter Trait"
        X86TRAIT["X86Codegen:<br/>x86-64 constraints,<br/>RIP-relative addressing"]
        I686TRAIT["I686Codegen:<br/>32-bit registers,<br/>register exhaustion"]
        ARMTRAIT["ArmCodegen:<br/>AArch64 constraints,<br/>w/x/s/d/q modifiers"]
        RVTRAIT["RiscvCodegen:<br/>RISC-V constraints,<br/>A (AMO address)"]
    end
    
    TEMPLATE --> CLASSIFY
    OUTPUTS --> CLASSIFY
    INPUTS --> CLASSIFY
    CLOBBERS --> ASSIGN
    
    CLASSIFY --> KINDENUM
    KINDENUM --> METADATA
    METADATA --> RESOLVE
    RESOLVE --> ASSIGN
    
    ASSIGN --> LOADINPUT
    LOADINPUT --> PRELOAD
    PRELOAD --> SUBSTITUTE
    SUBSTITUTE --> STORE
    
    LOADINPUT --> X86TRAIT
    LOADINPUT --> I686TRAIT
    LOADINPUT --> ARMTRAIT
    LOADINPUT --> RVTRAIT
    
    SUBSTITUTE --> X86TRAIT
    SUBSTITUTE --> I686TRAIT
    SUBSTITUTE --> ARMTRAIT
    SUBSTITUTE --> RVTRAIT
```

**Diagram: Inline Assembly Processing Pipeline**

The inline assembly framework in [src/backend/inline_asm.rs:1-1640]() uses a shared four-phase pipeline that all backends invoke via `emit_inline_asm_common`. Phase 1 classifies constraints and assigns registers (specific registers first, then scratch registers from an architecture-specific pool). Phase 2 loads input values into their assigned registers. Phase 3 performs template substitution, replacing `%0`, `%[name]`, and modifiers like `%w0` with actual register names. Phase 4 stores output registers back to their stack slots.

Sources: [src/backend/inline_asm.rs:1-1640](), [src/backend/inline_asm.rs:400-472]()

### Constraint Classification

```mermaid
graph LR
    subgraph "Constraint String"
        RAW["Input: '=r', '+rm', '&a'"]
        STRIP["Strip: =, +, &, %"]
        PARSE["Parse alternatives"]
    end
    
    subgraph "AsmOperandKind Enum"
        GP["GpReg<br/>r, q, R, l"]
        FP["FpReg<br/>x (x86), f (RISC-V)"]
        MEM["Memory<br/>m, o, V"]
        SPEC["Specific(String)<br/>a→rax, c→rcx"]
        TIED["Tied(usize)<br/>0, 1, 2"]
        IMM["Immediate<br/>i, I, n"]
        ADDR["Address<br/>A (RISC-V AMO)"]
        ZERO["ZeroOrReg<br/>rJ (RISC-V)"]
        CC["ConditionCode<br/>@cce, @ccne"]
        X87["X87St0, X87St1<br/>t, u (x87 stack)"]
        QREG["QReg<br/>Q (x86 %h access)"]
    end
    
    RAW --> STRIP
    STRIP --> PARSE
    
    PARSE --> GP
    PARSE --> FP
    PARSE --> MEM
    PARSE --> SPEC
    PARSE --> TIED
    PARSE --> IMM
    PARSE --> ADDR
    PARSE --> ZERO
    PARSE --> CC
    PARSE --> X87
    PARSE --> QREG
```

**Diagram: Constraint Classification Process**

The `classify_constraint` trait method maps GCC constraint strings to `AsmOperandKind` enums. Multi-alternative constraints like `"rm"` (register or memory) are parsed character-by-character with priority ordering: specific register > general register > floating-point register > memory > immediate. The classification determines how the operand is loaded, stored, and substituted in the template.

Sources: [src/backend/inline_asm.rs:19-52](), [src/backend/x86/codegen/asm_emitter.rs:26-116](), [src/backend/arm/codegen/asm_emitter.rs:43-99]()

### Register Allocation Strategy

| Architecture | GP Scratch Pool | FP Scratch Pool | Exhaustion Handling |
|--------------|-----------------|-----------------|---------------------|
| x86-64 | `rcx, rdx, rsi, rdi, r8-r11` (8 regs) | `xmm0-xmm15` (16 regs) | Overflow to `r12-r15`, then wrap |
| i686 | `ecx, edx, esi, edi, eax, ebx` (6 regs) | `xmm0-xmm7` (8 regs) | Return empty string → memory fallback |
| AArch64 | `x9-x15, x19-x21` (10 regs) | `v16-v25` (10 regs) | Mark callee-saved as used |
| RISC-V | `t0-t6, a2-a7, a0-a1` (15 regs) | `ft0-ft7` (8 regs) | Overflow to `s2-s11` with save/restore |

Each architecture implements `assign_scratch_reg` to allocate registers from a predefined pool, skipping those claimed by specific-register constraints or clobbers. x86-64 has the largest pool and can handle 8 GP operands without spillage. i686 has severe register pressure (only 6 GP registers) and returns an empty string when exhausted, triggering memory operand fallback for `"g"` constraints. RISC-V saves/restores borrowed callee-saved registers around the inline asm block.

Sources: [src/backend/x86/codegen/asm_emitter.rs:15-267](), [src/backend/i686/codegen/asm_emitter.rs:153-198](), [src/backend/arm/codegen/asm_emitter.rs:16-193](), [src/backend/riscv/codegen/asm_emitter.rs:16-251]()

### Template Substitution Rules

| Syntax | Meaning | Example | Output (x86-64) | Output (AArch64) |
|--------|---------|---------|-----------------|------------------|
| `%0` | Positional operand | `addl %0, %1` | `addl %rcx, %rdx` | `add x9, x10` |
| `%[name]` | Named operand | `mov %[src], %[dst]` | `movq %rax, %rbx` | `mov x0, x1` |
| `%w0` | 16-bit (x86) / 32-bit (ARM) | `movw %w0, (%rax)` | `movw %cx, (%rax)` | `mov w9, [x0]` |
| `%k0` | 32-bit (x86) | `movl %k0, %eax` | `movl %ecx, %eax` | N/A |
| `%b0` | 8-bit low (x86) | `movb %b0, (%rax)` | `movb %cl, (%rax)` | N/A |
| `%h0` | 8-bit high (x86) | `movb %h0, (%rax)` | `movb %ch, (%rax)` | N/A |
| `%c0` | Raw constant (no prefix) | `shl %c0` | `shl 5` | `lsl 5` |
| `%P0` | Raw symbol name | `call %P0` | `call memcpy` | `bl memcpy` |
| `%n0` | Negated immediate | `sub %n0` | `sub -5` | `sub -5` |
| `%a0` | Address reference | `lea %a0, %rax` | `lea symbol(%rip), %rax` | `adrp x0, symbol` |
| `%l[label]` | Goto label | `jz %l[done]` | `jz .L5` | `b.eq .L5` |

Template substitution is handled by architecture-specific implementations. x86-64 uses shared logic in [src/backend/x86_common.rs]() for parsing, with platform-specific operand emission (x86-64 uses RIP-relative addressing for `%a`, i686 uses direct symbol names). AArch64 has distinct modifier semantics: `%w` means 32-bit W register, `%x` means 64-bit X register, `%s/%d/%q` select FP/SIMD register views.

Sources: [src/backend/x86/codegen/inline_asm.rs:15-168](), [src/backend/arm/codegen/inline_asm.rs:1-279](), [src/backend/inline_asm.rs:322-398]()

## Complex Number Support

Complex types (`_Complex float`, `_Complex double`, `_Complex long double`) receive special builtin and ABI handling:

| Builtin | Purpose | IR Lowering | Platform Differences |
|---------|---------|-------------|---------------------|
| `creal`, `crealf`, `creall` | Extract real part | Load from offset 0 | x86-64 packed: unpack F64 |
| `cimag`, `cimagf`, `cimagl` | Extract imaginary part | Load from offset sizeof(component) | x86-64 packed: unpack F64 >> 32 |
| `conj`, `conjf`, `conjl` | Complex conjugate | Negate imaginary part | ABI decomposition first |
| `__builtin_complex` | Construct complex | Store real+imag consecutively | Recompose packed format |

On x86-64, `_Complex float` is packed into a single `F64` register for parameter passing (real in lower 32 bits, imaginary in upper 32 bits). ARM and RISC-V decompose into two separate FP registers. The builtins in [src/ir/lowering/expr_builtins.rs:601-647]() handle both representations transparently by checking `uses_packed_complex_float()` and applying the appropriate extraction logic.

Sources: [src/ir/lowering/expr_builtins.rs:27-34](), [src/ir/lowering/expr_builtins.rs:601-647](), [src/ir/lowering/func_lowering.rs:165-195]()

## Variadic Arguments

The `va_start`, `va_end`, and `va_copy` builtins provide variadic argument access:

```mermaid
graph LR
    subgraph "Builtin Calls"
        VASTART["__builtin_va_start(ap, last)"]
        VAEND["__builtin_va_end(ap)"]
        VACOPY["__builtin_va_copy(dest, src)"]
    end
    
    subgraph "IR Lowering"
        LOWERPTR["lower_va_list_pointer<br/>Handle array-to-pointer decay"]
        VAINSTR["Instruction::VaStart |<br/>Instruction::VaEnd |<br/>Instruction::VaCopy"]
    end
    
    subgraph "Backend Emission"
        X86VA["x86-64: gp_offset, fp_offset<br/>overflow_arg_area, reg_save_area"]
        I686VA["i686: simple pointer<br/>to stack arguments"]
        ARMVA["AArch64: __va_list struct<br/>stack, gr_top, vr_top"]
        RVVA["RISC-V: simple pointer<br/>to stack arguments"]
    end
    
    VASTART --> LOWERPTR
    VAEND --> LOWERPTR
    VACOPY --> LOWERPTR
    
    LOWERPTR --> VAINSTR
    
    VAINSTR --> X86VA
    VAINSTR --> I686VA
    VAINSTR --> ARMVA
    VAINSTR --> RVVA
```

**Diagram: Variadic Argument Handling**

The `va_list` type has architecture-specific ABI representations. x86-64 uses a complex struct with GP/FP register offsets and overflow area pointers. i686, RISC-V, and AArch64 use simpler pointer-based layouts. The IR lowering in [src/ir/lowering/expr_builtins.rs:126-153]() uses `lower_va_list_pointer` to correctly handle both local `va_list` variables (array type, needs address-of) and `va_list` parameters (pointer type after array-to-pointer decay, needs value load).

Sources: [src/ir/lowering/expr_builtins.rs:121-153](), [src/frontend/sema/builtins.rs:246-248]()

## Fortification Builtins

GCC's `_FORTIFY_SOURCE` feature defines wrapper functions that call `__builtin___*_chk` variants:

```c
// From glibc headers with _FORTIFY_SOURCE=2:
#define snprintf(...) __builtin___snprintf_chk(__VA_ARGS__, __builtin_object_size(...))
```

The compiler forwards all arguments to the glibc runtime `__*_chk` functions:

| Builtin | Runtime Function | Arguments Forwarded |
|---------|------------------|---------------------|
| `__builtin___memcpy_chk` | `__memcpy_chk` | `(dst, src, n, dst_size)` |
| `__builtin___snprintf_chk` | `__snprintf_chk` | `(buf, maxlen, flags, buflen, fmt, ...)` |
| `__builtin___sprintf_chk` | `__sprintf_chk` | `(buf, flags, buflen, fmt, ...)` |
| `__builtin___vsnprintf_chk` | `__vsnprintf_chk` | `(buf, maxlen, flags, buflen, fmt, va)` |

The lowering in [src/ir/lowering/expr_builtins.rs:470-541]() avoids infinite recursion by calling the runtime `__*_chk` function instead of the non-`_chk` variant. This is critical because glibc's fortification headers redefine standard functions like `snprintf` as always_inline wrappers that call the builtin, which would loop if the builtin tried to call `snprintf` again.

Sources: [src/ir/lowering/expr_builtins.rs:470-541](), [src/frontend/sema/builtins.rs:116-135]()

---


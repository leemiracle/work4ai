<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cccl · extra page Standard Library Components · fetched 2026-10-26 -->

# Standard Library Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/libcudacxx/extended_api/type_traits/is_floating_point.rst](docs/libcudacxx/extended_api/type_traits/is_floating_point.rst)
- [lib/cmake/thrust/FindTBB.cmake](lib/cmake/thrust/FindTBB.cmake)
- [libcudacxx/include/cuda/__type_traits/is_floating_point.h](libcudacxx/include/cuda/__type_traits/is_floating_point.h)
- [libcudacxx/include/cuda/std/__atomic/functions/cuda_ptx_generated_helper.h](libcudacxx/include/cuda/std/__atomic/functions/cuda_ptx_generated_helper.h)
- [libcudacxx/include/cuda/std/__cccl/builtin.h](libcudacxx/include/cuda/std/__cccl/builtin.h)
- [libcudacxx/include/cuda/std/__cccl/compiler.h](libcudacxx/include/cuda/std/__cccl/compiler.h)
- [libcudacxx/include/cuda/std/__cccl/cuda_toolkit.h](libcudacxx/include/cuda/std/__cccl/cuda_toolkit.h)
- [libcudacxx/include/cuda/std/__cccl/diagnostic.h](libcudacxx/include/cuda/std/__cccl/diagnostic.h)
- [libcudacxx/include/cuda/std/__cccl/dialect.h](libcudacxx/include/cuda/std/__cccl/dialect.h)
- [libcudacxx/include/cuda/std/__cccl/extended_data_types.h](libcudacxx/include/cuda/std/__cccl/extended_data_types.h)
- [libcudacxx/include/cuda/std/__cccl/system_header.h](libcudacxx/include/cuda/std/__cccl/system_header.h)
- [libcudacxx/include/cuda/std/__cmath/min_max.h](libcudacxx/include/cuda/std/__cmath/min_max.h)
- [libcudacxx/include/cuda/std/__cmath/nan.h](libcudacxx/include/cuda/std/__cmath/nan.h)
- [libcudacxx/include/cuda/std/__complex/complex.h](libcudacxx/include/cuda/std/__complex/complex.h)
- [libcudacxx/include/cuda/std/__complex/logarithms.h](libcudacxx/include/cuda/std/__complex/logarithms.h)
- [libcudacxx/include/cuda/std/__complex/nvbf16.h](libcudacxx/include/cuda/std/__complex/nvbf16.h)
- [libcudacxx/include/cuda/std/__complex/nvfp16.h](libcudacxx/include/cuda/std/__complex/nvfp16.h)
- [libcudacxx/include/cuda/std/__complex/vector_support.h](libcudacxx/include/cuda/std/__complex/vector_support.h)
- [libcudacxx/include/cuda/std/__cstdlib/abs.h](libcudacxx/include/cuda/std/__cstdlib/abs.h)
- [libcudacxx/include/cuda/std/__cstdlib/div.h](libcudacxx/include/cuda/std/__cstdlib/div.h)
- [libcudacxx/include/cuda/std/__functional/bind_front.h](libcudacxx/include/cuda/std/__functional/bind_front.h)
- [libcudacxx/include/cuda/std/__functional/not_fn.h](libcudacxx/include/cuda/std/__functional/not_fn.h)
- [libcudacxx/include/cuda/std/__internal/atomic.h](libcudacxx/include/cuda/std/__internal/atomic.h)
- [libcudacxx/include/cuda/std/__internal/features.h](libcudacxx/include/cuda/std/__internal/features.h)
- [libcudacxx/include/cuda/std/__type_traits/is_extended_floating_point.h](libcudacxx/include/cuda/std/__type_traits/is_extended_floating_point.h)
- [libcudacxx/include/cuda/std/__type_traits/is_trivially_copyable.h](libcudacxx/include/cuda/std/__type_traits/is_trivially_copyable.h)
- [libcudacxx/include/cuda/std/__type_traits/promote.h](libcudacxx/include/cuda/std/__type_traits/promote.h)
- [libcudacxx/include/cuda/std/__type_traits/type_list.h](libcudacxx/include/cuda/std/__type_traits/type_list.h)
- [libcudacxx/include/cuda/std/__utility/declval.h](libcudacxx/include/cuda/std/__utility/declval.h)
- [libcudacxx/include/cuda/std/cmath](libcudacxx/include/cuda/std/cmath)
- [libcudacxx/test/libcudacxx/cuda/iterators/transform_input_output_iterator/types.h](libcudacxx/test/libcudacxx/cuda/iterators/transform_input_output_iterator/types.h)
- [libcudacxx/test/libcudacxx/cuda/iterators/transform_output_iterator/types.h](libcudacxx/test/libcudacxx/cuda/iterators/transform_output_iterator/types.h)
- [libcudacxx/test/libcudacxx/cuda/test_platform.pass.cpp](libcudacxx/test/libcudacxx/cuda/test_platform.pass.cpp)
- [libcudacxx/test/libcudacxx/cuda/type_list.pass.cpp](libcudacxx/test/libcudacxx/cuda/type_list.pass.cpp)
- [libcudacxx/test/libcudacxx/libcxx/utilities/meta/meta.unary/meta.unary.cat/is_floating_point.pass.cpp](libcudacxx/test/libcudacxx/libcxx/utilities/meta/meta.unary/meta.unary.cat/is_floating_point.pass.cpp)
- [libcudacxx/test/libcudacxx/std/language.support/cstdlib/abs.pass.cpp](libcudacxx/test/libcudacxx/std/language.support/cstdlib/abs.pass.cpp)
- [libcudacxx/test/libcudacxx/std/language.support/cstdlib/div.pass.cpp](libcudacxx/test/libcudacxx/std/language.support/cstdlib/div.pass.cpp)
- [libcudacxx/test/libcudacxx/std/numerics/c.math/comparison.h](libcudacxx/test/libcudacxx/std/numerics/c.math/comparison.h)
- [libcudacxx/test/libcudacxx/std/numerics/c.math/error_functions.pass.cpp](libcudacxx/test/libcudacxx/std/numerics/c.math/error_functions.pass.cpp)
- [libcudacxx/test/libcudacxx/std/numerics/c.math/fp_abs.pass.cpp](libcudacxx/test/libcudacxx/std/numerics/c.math/fp_abs.pass.cpp)
- [libcudacxx/test/libcudacxx/std/numerics/c.math/fp_min_max.pass.cpp](libcudacxx/test/libcudacxx/std/numerics/c.math/fp_min_max.pass.cpp)
- [libcudacxx/test/libcudacxx/std/numerics/c.math/fp_traits.pass.cpp](libcudacxx/test/libcudacxx/std/numerics/c.math/fp_traits.pass.cpp)
- [libcudacxx/test/libcudacxx/std/utilities/memory/ptr.align/align.pass.cpp](libcudacxx/test/libcudacxx/std/utilities/memory/ptr.align/align.pass.cpp)
- [libcudacxx/test/libcudacxx/std/utilities/meta/meta.unary/meta.unary.cat/is_floating_point.pass.cpp](libcudacxx/test/libcudacxx/std/utilities/meta/meta.unary/meta.unary.cat/is_floating_point.pass.cpp)
- [libcudacxx/test/support/test_macros.h](libcudacxx/test/support/test_macros.h)

</details>



## Purpose and Scope

This page documents libcudacxx's implementation of C++ standard library components that work identically on both host and device. These components include type traits, complex numbers, mathematical functions, and atomic operations, all with first-class support for NVIDIA's extended floating-point types (`__half`, `__nv_bfloat16`, `__nv_fp8_*`, `__float128`). 

For compiler and platform abstraction mechanisms that enable these components, see [Compiler and Platform Abstraction](#2.3.3). For hardware-specific abstractions like CUDA Driver API wrappers, see [Hardware Abstractions](#2.3.2).

**Sources:** [libcudacxx/include/cuda/std/__cccl/builtin.h:1-494](), [libcudacxx/include/cuda/std/__cccl/extended_data_types.h:1-140]()

---

## Type Traits System

### Core Type Traits

libcudacxx provides standard C++ type traits like `is_floating_point`, `is_trivially_copyable`, `is_constructible`, etc., implemented using compiler builtins where available. The `_CCCL_BUILTIN_*` macro system in `builtin.h` abstracts compiler-specific builtin availability.

```mermaid
graph TB
    subgraph "Type Trait Query"
        User["User Code:<br/>is_floating_point_v&lt;T&gt;"]
        
        StdTrait["cuda::std::is_floating_point&lt;T&gt;<br/>[type_traits/is_floating_point.h:32-36]"]
        ExtTrait["cuda::is_floating_point&lt;T&gt;<br/>[__type_traits/is_floating_point.h:35-37]"]
        ExtendedCheck["__is_extended_floating_point_v&lt;T&gt;<br/>[is_extended_floating_point.h:28-73]"]
    end
    
    subgraph "Builtin Detection"
        BuiltinCheck["_CCCL_BUILTIN_IS_FLOATING_POINT<br/>[builtin.h:318-320]"]
        CompilerCheck["_CCCL_HAS_BUILTIN(__is_floating_point)"]
    end
    
    subgraph "Extended Type Support"
        HalfCheck["Specialization for __half"]
        BF16Check["Specialization for __nv_bfloat16"]
        FP8Check["Specializations for __nv_fp8_*"]
        F128Check["Specialization for __float128"]
    end
    
    User --> StdTrait
    User --> ExtTrait
    ExtTrait --> StdTrait
    ExtTrait --> ExtendedCheck
    StdTrait --> BuiltinCheck
    BuiltinCheck --> CompilerCheck
    ExtendedCheck --> HalfCheck
    ExtendedCheck --> BF16Check
    ExtendedCheck --> FP8Check
    ExtendedCheck --> F128Check
```

**Key traits include:**

| Trait | Builtin Macro | Files |
|-------|---------------|-------|
| `is_floating_point` | `_CCCL_BUILTIN_IS_FLOATING_POINT` | [builtin.h:318-320]() |
| `is_trivially_copyable` | `_CCCL_BUILTIN_IS_TRIVIALLY_COPYABLE` | [is_trivially_copyable.h:27-36]() |
| `is_constructible` | `_CCCL_BUILTIN_IS_CONSTRUCTIBLE` | [builtin.h:288-290]() |
| `is_assignable` | `_CCCL_BUILTIN_IS_ASSIGNABLE` | [builtin.h:280-282]() |

**Sources:** [libcudacxx/include/cuda/std/__cccl/builtin.h:44-494](), [libcudacxx/include/cuda/std/__type_traits/is_trivially_copyable.h:1-43](), [libcudacxx/include/cuda/__type_traits/is_floating_point.h:1-48](), [libcudacxx/include/cuda/std/__type_traits/is_extended_floating_point.h:1-80]()

### Extended Floating-Point Type Support

libcudacxx extends `is_floating_point` to recognize NVIDIA-specific floating-point types through the `__is_extended_floating_point_v` trait. This enables generic algorithms to work seamlessly with extended types.

```mermaid
graph LR
    subgraph "Type Categories"
        Standard["Standard FP Types<br/>float, double, long double"]
        Extended["Extended FP Types<br/>__half, __nv_bfloat16<br/>__nv_fp8_e4m3, __nv_fp8_e5m2<br/>__float128"]
    end
    
    subgraph "Detection Macros"
        NVFP16["_CCCL_HAS_NVFP16()<br/>[extended_data_types.h:48-52]"]
        NVBF16["_CCCL_HAS_NVBF16()<br/>[extended_data_types.h:54-59]"]
        NVFP8["_CCCL_HAS_NVFP8()<br/>[extended_data_types.h:61-77]"]
        F128["_CCCL_HAS_FLOAT128()<br/>[extended_data_types.h:111-125]"]
    end
    
    subgraph "Trait System"
        IsExtended["__is_extended_floating_point_v&lt;T&gt;<br/>[is_extended_floating_point.h:28]"]
        IsFloat["is_floating_point_v&lt;T&gt;"]
    end
    
    Standard --> IsFloat
    Extended --> NVFP16
    Extended --> NVBF16
    Extended --> NVFP8
    Extended --> F128
    
    NVFP16 --> IsExtended
    NVBF16 --> IsExtended
    NVFP8 --> IsExtended
    F128 --> IsExtended
    
    IsExtended --> IsFloat
```

**Extended type availability depends on:**

| Type | Required Header | Architecture | Macro |
|------|----------------|--------------|-------|
| `__half` | `cuda_fp16.h` | SM_53+ (device) | `_CCCL_HAS_NVFP16()` |
| `__nv_bfloat16` | `cuda_bf16.h` | SM_80+ (device) | `_CCCL_HAS_NVBF16()` |
| `__nv_fp8_e4m3`, `__nv_fp8_e5m2` | `cuda_fp8.h` | SM_89+ (device) | `_CCCL_HAS_NVFP8()` |
| `__float128` | Compiler support | SM_100+ (device) | `_CCCL_HAS_FLOAT128()` |

**Sources:** [libcudacxx/include/cuda/std/__cccl/extended_data_types.h:32-140](), [libcudacxx/include/cuda/std/__type_traits/is_extended_floating_point.h:25-80](), [libcudacxx/include/cuda/__type_traits/is_floating_point.h:32-46]()

### Type Promotion and Conversion

The `__promote` system implements C++ type promotion rules with extended type support. The `__numeric_type` trait determines the promoted type for mixed arithmetic operations.

```mermaid
graph TB
    subgraph "Type Promotion Rules"
        Input["Mixed-Type Expression:<br/>__half + float"]
        
        Promote["__promote&lt;__half, float&gt;<br/>[promote.h:153-157]"]
        NumericType1["__numeric_type&lt;__half&gt;<br/>[promote.h:31-56]"]
        NumericType2["__numeric_type&lt;float&gt;"]
        
        TestFunc["__test(__half) → float<br/>[promote.h:35-38]"]
        Result["Promoted Type: float"]
    end
    
    subgraph "Extended Type Handling"
        MixedCheck["__is_mixed_extended_floating_point<br/>[promote.h:65-106]"]
        Disallow["Disallow __half + __nv_bfloat16<br/>Different bit representations"]
    end
    
    Input --> Promote
    Promote --> NumericType1
    Promote --> NumericType2
    NumericType1 --> TestFunc
    NumericType2 --> TestFunc
    TestFunc --> Result
    
    Promote --> MixedCheck
    MixedCheck --> Disallow
```

**Promotion rules for extended types:**
- `__half` → `float`
- `__nv_bfloat16` → `float`
- `__half` + `__nv_bfloat16` → compilation error (mixed extended types disallowed)
- `__half` + `float` → `float`

**Sources:** [libcudacxx/include/cuda/std/__type_traits/promote.h:1-164]()

### Metaprogramming: Type Lists

The `__type_list` system provides compile-time type manipulation for metaprogramming, similar to `std::tuple` but operating purely at compile time.

```mermaid
graph TB
    subgraph "Type List Core"
        TL["__type_list&lt;Ts...&gt;<br/>[type_list.h:302-312]"]
        Size["__size member<br/>sizeof...(Ts)"]
        Call["__call template<br/>Apply meta-callable"]
    end
    
    subgraph "Meta-Callable Protocol"
        Callable["Meta-Callable Fn<br/>template&lt;class...&gt; __call alias"]
        Quote["__type_quote&lt;Template&gt;<br/>[type_list.h:94-99]"]
        Compose["__type_compose&lt;Fn1, Fn2&gt;<br/>[type_list.h:169-174]"]
        BindFront["__type_bind_front&lt;Fn, Ts...&gt;<br/>[type_list.h:184-186]"]
    end
    
    subgraph "Operations"
        At["__type_at&lt;I, List&gt;<br/>[type_list.h:581-586]"]
        Concat["__type_concat&lt;Lists...&gt;<br/>[type_list.h:784-785]"]
        Find["__type_find_if&lt;Fn, List&gt;<br/>[type_list.h:796-818]"]
        Index["__type_index&lt;Ip, Ts...&gt;<br/>[type_list.h:451-568]"]
    end
    
    TL --> Size
    TL --> Call
    Call --> Callable
    Callable --> Quote
    Callable --> Compose
    Callable --> BindFront
    
    TL --> At
    TL --> Concat
    TL --> Find
    At --> Index
```

**Key metaprogramming utilities:**

| Utility | Purpose | Implementation |
|---------|---------|----------------|
| `__type_list<Ts...>` | Type container | [type_list.h:302-312]() |
| `__type_at<I, List>` | Extract type at index | [type_list.h:581-586]() |
| `__type_index<I, Ts...>` | Index into parameter pack | Uses `__type_pack_element` or fallback [type_list.h:451-568]() |
| `__type_concat<Lists...>` | Concatenate type lists | [type_list.h:784-785]() |
| `__type_quote<Template>` | Turn template into meta-callable | [type_list.h:94-99]() |

**Sources:** [libcudacxx/include/cuda/std/__type_traits/type_list.h:1-1800](), [libcudacxx/test/libcudacxx/cuda/type_list.pass.cpp:1-1000]()

---

## Complex Numbers

### Standard Complex Implementation

libcudacxx provides `cuda::std::complex<T>` with dual-compatibility for host and device code. The implementation uses vectorized operations when available for extended floating-point types.

```mermaid
graph TB
    subgraph "Complex Class Hierarchy"
        BaseComplex["complex&lt;T&gt;<br/>[complex.h:65-208]"]
        ComplexFloat["complex&lt;float&gt;"]
        ComplexDouble["complex&lt;double&gt;"]
        ComplexHalf["complex&lt;__half&gt;<br/>[nvfp16.h:88-236]"]
        ComplexBF16["complex&lt;__nv_bfloat16&gt;<br/>[nvbf16.h:88-236]"]
    end
    
    subgraph "Storage Strategy"
        ScalarStorage["Scalar Storage<br/>_Tp __re_, __im_<br/>[complex.h:67-68]"]
        VectorStorage["Vector Storage<br/>__half2 __repr_<br/>[nvfp16.h:90]"]
        Alignment["Custom Alignment<br/>__complex_alignment_v&lt;T&gt;<br/>[vector_support.h:38]"]
    end
    
    subgraph "Operations"
        Addition["operator+=<br/>Vectorized for __half/__bfloat16<br/>[nvfp16.h:220-224]"]
        Multiplication["operator*<br/>C99 Annex G semantics<br/>[complex.h:272-382]"]
        Division["operator/<br/>Scaled division<br/>[complex.h:401-497]"]
    end
    
    BaseComplex --> ComplexFloat
    BaseComplex --> ComplexDouble
    BaseComplex --> ComplexHalf
    BaseComplex --> ComplexBF16
    
    ComplexFloat --> ScalarStorage
    ComplexHalf --> VectorStorage
    ComplexBF16 --> VectorStorage
    VectorStorage --> Alignment
    
    ComplexHalf --> Addition
    ComplexHalf --> Multiplication
    ComplexHalf --> Division
```

**Complex number features:**
- **Storage:** Scalar representation for standard types, vectorized (`__half2`, `__nv_bfloat162`) for extended types
- **Alignment:** Custom alignment via `__complex_alignment_v<T>` [vector_support.h:38]()
- **Conversions:** Non-narrowing conversions between compatible types
- **Operations:** Full arithmetic with C99 Annex G semantics for special values (NaN, infinity)

**Sources:** [libcudacxx/include/cuda/std/__complex/complex.h:1-800](), [libcudacxx/include/cuda/std/__complex/nvfp16.h:1-323](), [libcudacxx/include/cuda/std/__complex/nvbf16.h:1-324](), [libcudacxx/include/cuda/std/__complex/vector_support.h:1-131]()

### Extended Type Specializations

The `complex<__half>` and `complex<__nv_bfloat16>` specializations use vectorized storage and operations for optimal performance on NVIDIA GPUs.

```mermaid
graph LR
    subgraph "Vectorized Complex Operations"
        Add["operator+=(complex&<br/>[nvfp16.h:220-224]"]
        Sub["operator-=(complex&<br/>[nvfp16.h:226-230]"]
        Eq["operator==(complex&<br/>[nvfp16.h:232-235]"]
    end
    
    subgraph "Vector Intrinsics"
        HAdd2["__hadd2(__half2, __half2)<br/>Single instruction"]
        HSub2["__hsub2(__half2, __half2)<br/>Single instruction"]
        HBeq2["__hbeq2(__half2, __half2)<br/>Equality check"]
    end
    
    subgraph "Helper Functions"
        CalcPartials["__complex_calculate_partials<br/>[vector_support.h:86-105]"]
        VectorMul["Vector multiplication<br/>__first * __second"]
        PiecewiseMul["__complex_piecewise_mul<br/>[vector_support.h:109-124]"]
    end
    
    Add --> HAdd2
    Sub --> HSub2
    Eq --> HBeq2
    
    CalcPartials --> VectorMul
    PiecewiseMul --> VectorMul
```

**Vectorized operation examples:**

```cpp
// Addition uses __hadd2 for vectorized operations
complex<__half>& operator+=(complex& __lhs, const complex& __rhs) {
  __lhs.__repr_ = ::__hadd2(__lhs.__repr_, __rhs.__repr_);
  return __lhs;
}
```
[nvfp16.h:220-224]()

```cpp
// Multiplication helpers use vector types for efficiency
__abcd_results<_Tp> __complex_calculate_partials(_Tp __a, _Tp __b, _Tp __c, _Tp __d) {
  using _Vec = __type_to_vector_t<_Tp>;  // __half2 for __half
  _Vec __first{__a, __b};
  _Vec __second{__c, __d};
  _Vec __ac_bd = __first * __second;  // Vectorized multiply
  // ...
}
```
[vector_support.h:86-105]()

**Conversion rules:**
- `complex<__half>` → `complex<float>`: Uses `__half2float` [nvfp16.h:241-243]()
- `complex<__nv_bfloat16>` → `complex<float>`: Uses `__bfloat162float` [nvbf16.h:241-243]()
- Non-narrowing conversions are implicit, narrowing conversions require `explicit` [complex.h:84-96]()

**Sources:** [libcudacxx/include/cuda/std/__complex/nvfp16.h:88-236](), [libcudacxx/include/cuda/std/__complex/nvbf16.h:88-236](), [libcudacxx/include/cuda/std/__complex/vector_support.h:70-125]()

---

## Mathematical Functions

### Extended Type Support in cmath

libcudacxx extends standard `<cmath>` functions to work with NVIDIA extended floating-point types. The implementation strategy uses compiler builtins when available, with fallback implementations for constexpr and special cases.

```mermaid
graph TB
    subgraph "Function Resolution"
        UserCall["cuda::std::fmax(__half, __half)"]
        
        Template["Template overload<br/>fmax(_Tp, _Tp)<br/>[min_max.h:72-139]"]
        ExtCheck["__is_extended_arithmetic_v&lt;_Tp&gt;"]
    end
    
    subgraph "Implementation Strategy"
        RuntimeCheck["_CCCL_IF_NOT_CONSTEVAL_DEFAULT<br/>[dialect.h:156-178]"]
        
        HardwareImpl["Hardware Intrinsic<br/>__hmax(__half, __half)<br/>[min_max.h:78-83]"]
        BuiltinImpl["Compiler Builtin<br/>__builtin_fmax(float, float)<br/>[min_max.h:114-122]"]
        SoftwareImpl["Software Fallback<br/>isnan checks + comparison<br/>[min_max.h:126-138]"]
    end
    
    subgraph "Extended Type Paths"
        HalfPath["__half path<br/>CTK >= 12.2: __hmax<br/>else: __half2float + fmax"]
        BF16Path["__nv_bfloat16 path<br/>SM_80+: __hmax<br/>else: __bfloat162float + fmax"]
        F128Path["__float128 path<br/>SM_100+: __nv_fp128_fmax"]
    end
    
    UserCall --> Template
    Template --> ExtCheck
    ExtCheck --> RuntimeCheck
    
    RuntimeCheck --> HardwareImpl
    RuntimeCheck --> BuiltinImpl
    RuntimeCheck --> SoftwareImpl
    
    HardwareImpl --> HalfPath
    HardwareImpl --> BF16Path
    HardwareImpl --> F128Path
```

**Math function categories:**

| Category | Functions | Extended Type Support |
|----------|-----------|---------------------|
| Min/Max | `fmin`, `fmax`, `fminf`, `fmaxf`, `fminl`, `fmaxl` | [min_max.h:42-286]() |
| Absolute Value | `fabs`, `fabsf`, `fabsl`, `abs` | Hardware intrinsics for `__half`, `__nv_bfloat16` |
| Trigonometry | `sin`, `cos`, `tan`, `asin`, `acos`, `atan` | Promotion to `float`/`double` |
| Exponential | `exp`, `log`, `pow`, `sqrt` | Hardware intrinsics + software fallback |
| Complex | `abs`, `arg`, `norm`, `conj`, `polar` | [logarithms.h:1-300]() |

**Sources:** [libcudacxx/include/cuda/std/__cmath/min_max.h:1-287](), [libcudacxx/include/cuda/std/__complex/logarithms.h:1-300]()

### Implementation Details: fmin/fmax

The `fmin` and `fmax` functions demonstrate libcudacxx's multi-tier implementation strategy:

```mermaid
graph TB
    subgraph "fmax Implementation Tiers"
        T1["Tier 1: Hardware Intrinsic<br/>NV_IF_TARGET + __hmax"]
        T2["Tier 2: Compiler Builtin<br/>__builtin_fmaxf/fmax/fmaxl"]
        T3["Tier 3: Software<br/>isnan + comparison"]
        T4["Tier 4: Constexpr<br/>Pure comparison logic"]
    end
    
    subgraph "Decision Logic"
        IsConsteval["if consteval<br/>[dialect.h:153-178]"]
        HasBuiltin["_CCCL_USE_BUILTIN_FMAX()<br/>[min_max.h:65-68]"]
        IsExtended["is_same_v&lt;_Tp, __half&gt;"]
        HasCTK["_CCCL_CTK_AT_LEAST(12, 2)"]
        IsDevice["NV_IS_DEVICE"]
    end
    
    IsConsteval -->|false| IsExtended
    IsExtended -->|true| HasCTK
    HasCTK -->|true| T1
    HasCTK -->|false| IsDevice
    IsDevice -->|true| T1
    IsDevice -->|false| T3
    
    IsExtended -->|false| HasBuiltin
    HasBuiltin -->|true| T2
    HasBuiltin -->|false| T3
    
    IsConsteval -->|true| T4
```

**fmax for `__half` [min_max.h:74-139]():**

1. **Constexpr path:** Pure comparison without hardware operations
2. **CTK ≥ 12.2 path:** `::__hmax(__x, __y)` works on host and device
3. **Device + CTK < 12.2:** `::__hmax(__x, __y)` device intrinsic
4. **Host + CTK < 12.2:** `::cuda::std::fmax(::__half2float(__x), ::__half2float(__y))` with conversion

**Builtin detection [builtin.h:44-68]():**

```cpp
#if _CCCL_CHECK_BUILTIN(builtin_fmax) || _CCCL_COMPILER(GCC)
#  define _CCCL_USE_BUILTIN_FMAX() 1
#else
#  define _CCCL_USE_BUILTIN_FMAX() 0
#endif
```

**Sources:** [libcudacxx/include/cuda/std/__cmath/min_max.h:42-286](), [libcudacxx/include/cuda/std/__cccl/builtin.h:44-68](), [libcudacxx/include/cuda/std/__cccl/dialect.h:152-178]()

---

## Atomic Operations

libcudacxx provides `cuda::std::atomic<T>` and `cuda::atomic<T>` with support for extended floating-point types. Atomic operations use PTX instructions when available, with software fallbacks for unsupported types.

**Key atomic types:**
- `cuda::std::atomic<T>`: Standard C++ atomics, device and host
- `cuda::atomic<T>`: CUDA-specific atomics with memory scopes
- Memory scopes: `memory_scope_system`, `memory_scope_device`, `memory_scope_block`, `memory_scope_thread`

**Extended type support:**
- `atomic<__half>`: Available on SM_70+ [CTK 12.2+]
- `atomic<__nv_bfloat16>`: Available on SM_80+ [CTK 12.2+]
- Atomic operations: `load`, `store`, `exchange`, `compare_exchange`, arithmetic operations

For detailed atomic operation documentation, refer to the atomic operations section of the libcudacxx documentation.

**Sources:** [libcudacxx/include/cuda/std/__internal/atomic.h:1-100](), [libcudacxx/include/cuda/std/__atomic/functions/cuda_ptx_generated_helper.h:1-200]()

---

## Summary

libcudacxx's standard library components provide:

1. **Type Traits:** Compiler builtin-backed traits with extended FP type awareness
2. **Type Lists:** Compile-time metaprogramming infrastructure for generic algorithms
3. **Complex Numbers:** Vectorized implementations for extended types with C99 semantics
4. **Math Functions:** Multi-tier implementation strategy (hardware intrinsic → builtin → software → constexpr)
5. **Extended Types:** First-class support for `__half`, `__nv_bfloat16`, `__nv_fp8_*`, `__float128`
6. **Atomics:** PTX-backed atomic operations with memory scope control

The design philosophy prioritizes:
- **Zero-cost abstraction:** Use hardware intrinsics and compiler builtins when available
- **Constexpr support:** Fallback implementations that work at compile time
- **Cross-compiler compatibility:** Systematic detection and abstraction via `_CCCL_*` macros
- **Dual host/device compatibility:** Identical APIs that work on CPU and GPU

**Sources:** [libcudacxx/include/cuda/std/__cccl/builtin.h:1-494](), [libcudacxx/include/cuda/std/__cccl/extended_data_types.h:1-140](), [libcudacxx/include/cuda/std/__complex/complex.h:1-800](), [libcudacxx/include/cuda/std/__cmath/min_max.h:1-287](), [libcudacxx/include/cuda/std/__type_traits/type_list.h:1-1800]()

---


# A64_BASE — 指令首字母 H-P 部分

> **生成日期**：2026-06-29  
> **PDF 源版本**：ARM DDI 0487G.b (2021-07)

> a64_base_overview.md`](./a64_base_overview.md) 的拆分之一（按助记符首字母）。
> 含 126 条指令详解。

---

## 目录

- 4.3 `LDADDH, LDADDAH, LDADDALH, LDADDLH` (C6.2.100)
- 4.4 `LDADD, LDADDA, LDADDAL, LDADDL` (C6.2.101)
- 4.5 `LDAPR` (C6.2.102)
- 4.6 `LDAPRB` (C6.2.103)
- 4.7 `LDAPRH` (C6.2.104)
- 4.8 `LDAPUR` (C6.2.105)
- 4.9 `LDAPURB` (C6.2.106)
- 4.10 `LDAPURH` (C6.2.107)
- 4.11 `LDAPURSB` (C6.2.108)
- 4.12 `LDAPURSH` (C6.2.109)
- 4.14 `LDAPURSW` (C6.2.110)
- 4.15 `LDAR` (C6.2.111)
- 4.16 `LDARB` (C6.2.112)
- 4.17 `LDARH` (C6.2.113)
- 4.18 `LDAXP` (C6.2.114)
- 4.19 `LDAXR` (C6.2.115)
- 4.20 `LDAXRB` (C6.2.116)
- 4.21 `LDAXRH` (C6.2.117)
- 4.22 `LDCLRB, LDCLRAB, LDCLRALB, LDCLRLB` (C6.2.118)
- 4.23 `LDCLRH, LDCLRAH, LDCLRALH, LDCLRLH` (C6.2.119)
- 4.25 `LDCLR, LDCLRA, LDCLRAL, LDCLRL` (C6.2.120)
- 4.26 `LDEORB, LDEORAB, LDEORALB, LDEORLB` (C6.2.121)
- 4.27 `LDEORH, LDEORAH, LDEORALH, LDEORLH` (C6.2.122)
- 4.28 `LDEOR, LDEORA, LDEORAL, LDEORL` (C6.2.123)
- 4.29 `LDG` (C6.2.124)
- 4.30 `LDGM` (C6.2.125)
- 4.31 `LDLARB` (C6.2.126)
- 4.32 `LDLARH` (C6.2.127)
- 4.33 `LDLAR` (C6.2.128)
- 4.34 `LDNP` (C6.2.129)
- 4.36 `LDP` (C6.2.130)
- 4.37 `LDPSW` (C6.2.131)
- 4.38 `LDR (immediate)` (C6.2.132)
- 4.39 `LDR (literal)` (C6.2.133)
- 4.40 `LDR (register)` (C6.2.134)
- 4.41 `LDRAA, LDRAB` (C6.2.135)
- 4.42 `LDRB (immediate)` (C6.2.136)
- 4.43 `LDRB (register)` (C6.2.137)
- 4.44 `LDRH (immediate)` (C6.2.138)
- 4.45 `LDRH (register)` (C6.2.139)
- 4.47 `LDRSB (immediate)` (C6.2.140)
- 4.48 `LDRSB (register)` (C6.2.141)
- 4.49 `LDRSH (immediate)` (C6.2.142)
- 4.50 `LDRSH (register)` (C6.2.143)
- 4.51 `LDRSW (immediate)` (C6.2.144)
- 4.52 `LDRSW (literal)` (C6.2.145)
- 4.53 `LDRSW (register)` (C6.2.146)
- 4.54 `LDSETB, LDSETAB, LDSETALB, LDSETLB` (C6.2.147)
- 4.55 `LDSETH, LDSETAH, LDSETALH, LDSETLH` (C6.2.148)
- 4.56 `LDSET, LDSETA, LDSETAL, LDSETL` (C6.2.149)
- 4.58 `LDSMAXB, LDSMAXAB, LDSMAXALB, LDSMAXLB` (C6.2.150)
- 4.59 `LDSMAXH, LDSMAXAH, LDSMAXALH, LDSMAXLH` (C6.2.151)
- 4.60 `LDSMAX, LDSMAXA, LDSMAXAL, LDSMAXL` (C6.2.152)
- 4.61 `LDSMINB, LDSMINAB, LDSMINALB, LDSMINLB` (C6.2.153)
- 4.62 `LDSMINH, LDSMINAH, LDSMINALH, LDSMINLH` (C6.2.154)
- 4.63 `LDSMIN, LDSMINA, LDSMINAL, LDSMINL` (C6.2.155)
- 4.64 `LDTR` (C6.2.156)
- 4.65 `LDTRB` (C6.2.157)
- 4.66 `LDTRH` (C6.2.158)
- 4.67 `LDTRSB` (C6.2.159)
- 4.69 `LDTRSH` (C6.2.160)
- 4.70 `LDTRSW` (C6.2.161)
- 4.71 `LDUMAXB, LDUMAXAB, LDUMAXALB, LDUMAXLB` (C6.2.162)
- 4.72 `LDUMAXH, LDUMAXAH, LDUMAXALH, LDUMAXLH` (C6.2.163)
- 4.73 `LDUMAX, LDUMAXA, LDUMAXAL, LDUMAXL` (C6.2.164)
- 4.74 `LDUMINB, LDUMINAB, LDUMINALB, LDUMINLB` (C6.2.165)
- 4.75 `LDUMINH, LDUMINAH, LDUMINALH, LDUMINLH` (C6.2.166)
- 4.76 `LDUMIN, LDUMINA, LDUMINAL, LDUMINL` (C6.2.167)
- 4.77 `LDUR` (C6.2.168)
- 4.78 `LDURB` (C6.2.169)
- 4.80 `LDURH` (C6.2.170)
- 4.81 `LDURSB` (C6.2.171)
- 4.82 `LDURSH` (C6.2.172)
- 4.83 `LDURSW` (C6.2.173)
- 4.84 `LDXP` (C6.2.174)
- 4.85 `LDXR` (C6.2.175)
- 4.86 `LDXRB` (C6.2.176)
- 4.87 `LDXRH` (C6.2.177)
- 4.88 `LSL (register)` (C6.2.178)
- 4.89 `LSL (immediate)` (C6.2.179)
- 4.91 `LSLV` (C6.2.180)
- 4.92 `LSR (register)` (C6.2.181)
- 4.93 `LSR (immediate)` (C6.2.182)
- 4.94 `LSRV` (C6.2.183)
- 4.95 `MADD` (C6.2.184)
- 4.96 `MNEG` (C6.2.185)
- 4.97 `MOV (to/from SP)` (C6.2.186)
- 4.98 `MOV (inverted wide immediate)` (C6.2.187)
- 4.99 `MOV (wide immediate)` (C6.2.188)
- 4.100 `MOV (bitmask immediate)` (C6.2.189)
- 4.102 `MOV (register)` (C6.2.190)
- 4.103 `MOVK` (C6.2.191)
- 4.104 `MOVN` (C6.2.192)
- 4.105 `MOVZ` (C6.2.193)
- 4.106 `MRS` (C6.2.194)
- 4.107 `MSR (immediate)` (C6.2.195)
- 4.108 `MSR (register)` (C6.2.196)
- 4.109 `MSUB` (C6.2.197)
- 4.110 `MUL` (C6.2.198)
- 4.111 `MVN` (C6.2.199)
- 4.114 `NEG (shifted register)` (C6.2.200)
- 4.115 `NEGS` (C6.2.201)
- 4.116 `NGC` (C6.2.202)
- 4.117 `NGCS` (C6.2.203)
- 4.118 `NOP` (C6.2.204)
- 4.119 `ORN (shifted register)` (C6.2.205)
- 4.120 `ORR (immediate)` (C6.2.206)
- 4.121 `ORR (shifted register)` (C6.2.207)
- 4.122 `PACDA, PACDZA` (C6.2.208)
- 4.123 `PACDB, PACDZB` (C6.2.209)
- 4.125 `PACGA` (C6.2.210)
- 4.126 `PACIA, PACIA1716, PACIASP, PACIAZ, PACIZA` (C6.2.211)
- 4.127 `PACIB, PACIB1716, PACIBSP, PACIBZ, PACIZB` (C6.2.212)
- 4.128 `PRFM (immediate)` (C6.2.213)
- 4.129 `PRFM (literal)` (C6.2.214)
- 4.130 `PRFM (register)` (C6.2.215)
- 4.131 `PRFUM` (C6.2.216)
- 4.132 `PSSBB` (C6.2.218)
- 4.343 `HINT` (C6.2.92)
- 4.344 `HLT` (C6.2.93)
- 4.345 `HVC` (C6.2.94)
- 4.346 `IC` (C6.2.95)
- 4.347 `IRG` (C6.2.96)
- 4.348 `ISB` (C6.2.97)
- 4.349 `LD64B` (C6.2.98)
- 4.350 `LDADDB, LDADDAB, LDADDALB, LDADDLB` (C6.2.99)

---

## 指令详解

### 4.1 `LDADDH, LDADDAH, LDADDALH, LDADDLH` (C6.2.100)

> 💡 **被以下指令作为别名使用**：`STADDH`


**语义**：Atomic add on halfword in memory atomically loads a 16-bit halfword from memory, adds the value held in a register to it, and stores the result back to memory. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1043-p1045（共 3 页）



### 4.2 `LDADD, LDADDA, LDADDAL, LDADDL` (C6.2.101)

> 💡 **被以下指令作为别名使用**：`STADD`


**语义**：Atomic add on word or doubleword in memory atomically loads a 32-bit word or 64-bit doubleword from memory, adds the value held in a register to it, and stores the result back to memory. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1045-p1048（共 4 页）



### 4.3 `LDAPR` (C6.2.102)

**语义**：Load-Acquire RCpc Register derives an address from a base register value, loads a 32-bit word or 64-bit doubleword from the derived address in memory, and writes it to a register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1048-p1050（共 3 页）



### 4.4 `LDAPRB` (C6.2.103)

**语义**：Load-Acquire RCpc Register Byte derives an address from a base register value, loads a byte from the derived address in memory, zero-extends it and writes it to a register.


**汇编模板**：
```
LDAPRB <Wt>, [<Xn|SP> {,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn); 
 integer t = UInt(Rt); 
  
 boolean tag_checked = n != 31;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1050-p1052（共 3 页）



### 4.5 `LDAPRH` (C6.2.104)

**语义**：Load-Acquire RCpc Register Halfword derives an address from a base register value, loads a halfword from the derived address in memory, zero-extends it and writes it to a register.


**汇编模板**：
```
LDAPRH <Wt>, [<Xn|SP> {,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn); 
 integer t = UInt(Rt); 
  
 boolean tag_checked = n != 31;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1052-p1054（共 3 页）



### 4.6 `LDAPUR` (C6.2.105)

**语义**：Load-Acquire RCpc Register (unscaled) calculates an address from a base register and an immediate offset, loads a 32-bit word or 64-bit doubleword from memory, zero-extends it, and writes it to a register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1054-p1056（共 3 页）



### 4.7 `LDAPURB` (C6.2.106)

**语义**：Load-Acquire RCpc Register Byte (unscaled) calculates an address from a base register and an immediate offset, loads a byte from memory, zero-extends it, and writes it to a register.


**汇编模板**：
```
LDAPURB <Wt>, [<Xn|SP>{, #<simm>}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
bits(64) offset = SignExtend(imm9, 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1056-p1058（共 3 页）



### 4.8 `LDAPURH` (C6.2.107)

**语义**：Load-Acquire RCpc Register Halfword (unscaled) calculates an address from a base register and an immediate offset, loads a halfword from memory, zero-extends it, and writes it to a register.


**汇编模板**：
```
LDAPURH <Wt>, [<Xn|SP>{, #<simm>}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
bits(64) offset = SignExtend(imm9, 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1058-p1060（共 3 页）



### 4.9 `LDAPURSB` (C6.2.108)

**语义**：Load-Acquire RCpc Register Signed Byte (unscaled) calculates an address from a base register and an immediate offset, loads a signed byte from memory, sign-extends it, and writes it to a register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1060-p1062（共 3 页）



### 4.10 `LDAPURSH` (C6.2.109)

**语义**：Load-Acquire RCpc Register Signed Halfword (unscaled) calculates an address from a base register and an immediate offset, loads a signed halfword from memory, sign-extends it, and writes it to a register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1062-p1064（共 3 页）



### 4.11 `LDAPURSW` (C6.2.110)

**语义**：Load-Acquire RCpc Register Signed Word (unscaled) calculates an address from a base register and an immediate offset, loads a signed word from memory, sign-extends it, and writes it to a register.


**汇编模板**：
```
LDAPURSW <Xt>, [<Xn|SP>{, #<simm>}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
bits(64) offset = SignExtend(imm9, 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1064-p1066（共 3 页）



### 4.12 `LDAR` (C6.2.111)

**语义**：Load-Acquire Register derives an address from a base register value, loads a 32-bit word or 64-bit doubleword from memory, and writes it to a register. The instruction also has memory ordering semantics as described in Load-Acquire, Load-AcquirePC, and Store-Release on page B2-152. For information about memory accesses, see Load/store addressing modes on page C1-202.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1066-p1068（共 3 页）



### 4.13 `LDARB` (C6.2.112)

**语义**：Load-Acquire Register Byte derives an address from a base register value, loads a byte from memory, zero-extends it and writes it to a register. The instruction also has memory ordering semantics as described in Load-Acquire, Load-AcquirePC, and Store-Release on page B2-152. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDARB <Wt>, [<Xn|SP>{,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn); 
 integer t = UInt(Rt); 
  
 boolean tag_checked = n != 31;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1068-p1069（共 2 页）



### 4.14 `LDARH` (C6.2.113)

**语义**：Load-Acquire Register Halfword derives an address from a base register value, loads a halfword from memory, zero-extends it, and writes it to a register. The instruction also has memory ordering semantics as described in Load-Acquire, Load-AcquirePC, and Store-Release on page B2-152. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDARH <Wt>, [<Xn|SP>{,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn); 
 integer t = UInt(Rt); 
  
 boolean tag_checked = n != 31;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1069-p1070（共 2 页）



### 4.15 `LDAXP` (C6.2.114)

**语义**：Load-Acquire Exclusive Pair of Registers derives an address from a base register value, loads two 32-bit words or two 64-bit doublewords from memory, and writes them to two registers. For information on single-copy atomicity and alignment requirements, see Requirements for single-copy atomicity on page B2-128 and Alignment of data accesses on page B2-160. The PE marks the physical address being accessed as an exclusive access. This exclusive access mark is checked by Store Exclusive instructions


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt1>` | Is the 32-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Wt2>` | Is the 32-bit name of the second general-purpose register to be transferred, encoded in the "Rt2" field. |

| `<Xt1>` | Is the 64-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. 1 sz 0 0 1 0 0 0  |


</details>


*PDF 跨页*：p1070-p1072（共 3 页）



### 4.16 `LDAXR` (C6.2.115)

**语义**：Load-Acquire Exclusive Register derives an address from a base register value, loads a 32-bit word or 64-bit doubleword from memory, and writes it to a register. The memory access is atomic. The PE marks the physical address being accessed as an exclusive access. This exclusive access mark is checked by Store Exclusive instructions. See Synchronization and semaphores on page B2-179. The instruction also has memory ordering semantics as described in Load-Acquire, Load-AcquirePC, and Store-Release


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1072-p1074（共 3 页）



### 4.17 `LDAXRB` (C6.2.116)

**语义**：Load-Acquire Exclusive Register Byte derives an address from a base register value, loads a byte from memory, zero-extends it and writes it to a register. The memory access is atomic. The PE marks the physical address being accessed as an exclusive access. This exclusive access mark is checked by Store Exclusive instructions. See Synchronization and semaphores on page B2-179. The instruction also has memory ordering semantics as described in Load-Acquire, Load-AcquirePC, and Store-Release on pag


**汇编模板**：
```
LDAXRB <Wt>, [<Xn|SP>{,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn); 
 integer t = UInt(Rt); 
  
 boolean tag_checked = n != 31;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1074-p1075（共 2 页）



### 4.18 `LDAXRH` (C6.2.117)

**语义**：Load-Acquire Exclusive Register Halfword derives an address from a base register value, loads a halfword from memory, zero-extends it and writes it to a register. The memory access is atomic. The PE marks the physical address being accessed as an exclusive access. This exclusive access mark is checked by Store Exclusive instructions. See Synchronization and semaphores on page B2-179. The instruction also has memory ordering semantics as described in Load-Acquire, Load-AcquirePC, and Store-Releas


**汇编模板**：
```
LDAXRH <Wt>, [<Xn|SP>{,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn); 
 integer t = UInt(Rt); 
  
 boolean tag_checked = n != 31;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1075-p1076（共 2 页）



### 4.19 `LDCLRB, LDCLRAB, LDCLRALB, LDCLRLB` (C6.2.118)

> 💡 **被以下指令作为别名使用**：`STCLRB`


**语义**：Atomic bit clear on byte in memory atomically loads an 8-bit byte from memory, performs a bitwise AND with the complement of the value held in a register on it, and stores the result back to memory. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1076-p1078（共 3 页）



### 4.20 `LDCLRH, LDCLRAH, LDCLRALH, LDCLRLH` (C6.2.119)

> 💡 **被以下指令作为别名使用**：`STCLRH`


**语义**：Atomic bit clear on halfword in memory atomically loads a 16-bit halfword from memory, performs a bitwise AND with the complement of the value held in a register on it, and stores the result back to memory. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1078-p1080（共 3 页）



### 4.21 `LDCLR, LDCLRA, LDCLRAL, LDCLRL` (C6.2.120)

> 💡 **被以下指令作为别名使用**：`STCLR`


**语义**：Atomic bit clear on word or doubleword in memory atomically loads a 32-bit word or 64-bit doubleword from memory, performs a bitwise AND with the complement of the value held in a register on it, and stores the result back to memory. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1080-p1083（共 4 页）



### 4.22 `LDEORB, LDEORAB, LDEORALB, LDEORLB` (C6.2.121)

> 💡 **被以下指令作为别名使用**：`STEORB`


**语义**：Atomic exclusive OR on byte in memory atomically loads an 8-bit byte from memory, performs an exclusive OR with the value held in a register on it, and stores the result back to memory. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1083-p1085（共 3 页）



### 4.23 `LDEORH, LDEORAH, LDEORALH, LDEORLH` (C6.2.122)

> 💡 **被以下指令作为别名使用**：`STEORH`


**语义**：Atomic exclusive OR on halfword in memory atomically loads a 16-bit halfword from memory, performs an exclusive OR with the value held in a register on it, and stores the result back to memory. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1085-p1087（共 3 页）



### 4.24 `LDEOR, LDEORA, LDEORAL, LDEORL` (C6.2.123)

> 💡 **被以下指令作为别名使用**：`STEOR`


**语义**：Atomic exclusive OR on word or doubleword in memory atomically loads a 32-bit word or 64-bit doubleword from memory, performs an exclusive OR with the value held in a register on it, and stores the result back to memory. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1087-p1090（共 4 页）



### 4.25 `LDG` (C6.2.124)

**语义**：Load Allocation Tag loads an Allocation Tag from a memory address, generates a Logical Address Tag from the Allocation Tag and merges it into the destination register. The address used for the load is calculated from the base register and an immediate signed offset scaled by the Tag granule.


**汇编模板**：
```
LDG <Xt>, [<Xn|SP>{, #<simm>}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveMTEExt() then UNDEFINED; 
 integer t = UInt(Xt); 
 integer n = UInt(Xn); 
 bits(64) offset = LSL(SignExtend(imm9, 64), LOG2_TAG_GRANULE);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Xt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Xn" field. |

| `<simm>` | Is the optional signed immediate offset, a multiple of 16 in the range -4096 to 4080, defaulting to 0 and encoded in the |


</details>


*PDF 跨页*：p1090-p1091（共 2 页）



### 4.26 `LDGM` (C6.2.125)

**语义**：Load Tag Multiple reads a naturally aligned block of N Allocation Tags, where the size of N is identified in GMID_EL1.BS, and writes the Allocation Tag read from address A to the destination register at 4*A<7:4>+3:4*A<7:4>. Bits of the destination register not written with an Allocation Tag are set to 0.


**汇编模板**：
```
LDGM <Xt>, [<Xn|SP>]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveMTE2Ext() then UNDEFINED; 
 integer t = UInt(Xt); 
 integer n = UInt(Xn);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
if PSTATE.EL == EL0 then
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Xt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Xn" field. |


</details>


*PDF 跨页*：p1091-p1093（共 3 页）



### 4.27 `LDLARB` (C6.2.126)

**语义**：Load LOAcquire Register Byte loads a byte from memory, zero-extends it and writes it to a register. The instruction also has memory ordering semantics as described in LoadLOAcquire, StoreLORelease on page B2-153. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDLARB <Wt>, [<Xn|SP>{,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn); 
 integer t = UInt(Rt); 
  
 boolean tag_checked = n != 31;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1093-p1094（共 2 页）



### 4.28 `LDLARH` (C6.2.127)

**语义**：Load LOAcquire Register Halfword loads a halfword from memory, zero-extends it, and writes it to a register. The instruction also has memory ordering semantics as described in LoadLOAcquire, StoreLORelease on page B2-153.


**汇编模板**：
```
LDLARH <Wt>, [<Xn|SP>{,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn); 
 integer t = UInt(Rt); 
  
 boolean tag_checked = n != 31;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1094-p1095（共 2 页）



### 4.29 `LDLAR` (C6.2.128)

**语义**：Load LOAcquire Register loads a 32-bit word or 64-bit doubleword from memory, and writes it to a register. The instruction also has memory ordering semantics as described in LoadLOAcquire, StoreLORelease on page B2-153.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1095-p1097（共 3 页）



### 4.30 `LDNP` (C6.2.129)

**语义**：Load Pair of Registers, with non-temporal hint, calculates an address from a base register value and an immediate offset, loads two 32-bit words or two 64-bit doublewords from memory, and writes them to two registers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt1>` | Is the 32-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Wt2>` | Is the 32-bit name of the second general-purpose register to be transferred, encoded in the "Rt2" field. |

| `<Xt1>` | Is the 64-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt2>` | Is the 64-bit name of the second general-purpose register to be transferred, encoded in the "Rt2" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<imm>` | For the 32-bit variant: is the optional signed immediate byte offset, a multiple of 4 in the range -256 to 252, defaulti |


</details>


*PDF 跨页*：p1097-p1099（共 3 页）



### 4.31 `LDP` (C6.2.130)

**语义**：Load Pair of Registers calculates an address from a base register value and an immediate offset, loads two 32-bit words or two 64-bit doublewords from memory, and writes them to two registers. For information about memory accesses, see Load/store addressing modes on page C1-202.


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt1>` | Is the 32-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Wt2>` | Is the 32-bit name of the second general-purpose register to be transferred, encoded in the "Rt2" field. |

| `<Xt1>` | Is the 64-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt2>` | Is the 64-bit name of the second general-purpose register to be transferred, encoded in the "Rt2" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<imm>` | For the 32-bit post-index and 32-bit pre-index variant: is the signed immediate byte offset, a multiple of 4 in the rang |


</details>


*PDF 跨页*：p1099-p1103（共 5 页）



### 4.32 `LDPSW` (C6.2.131)

**语义**：Load Pair of Registers Signed Word calculates an address from a base register value and an immediate offset, loads two 32-bit words from memory, sign-extends them, and writes them to two registers. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDPSW <Xt1>, <Xt2>, [<Xn|SP>], #<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
boolean wback = TRUE; 
 boolean postindex = TRUE; 
Pre-index
Encoding
LDPSW <Xt1>, <Xt2>, [<Xn|SP>, #<imm>]!
Decode for this encoding
 boolean wback = TRUE; 
 boolean postindex = FALSE; 
Signed offset
Encoding
LDPSW <Xt1>, <Xt2>, [<Xn|SP>{, #<imm>}]
Decode for this encoding
 boolean wback = FALSE; 
 boolean postindex = FALSE; 
0
1
1
0
1
0
0
0
1
1
imm7
Rt2
Rn
Rt
31 30 29 28 27 26 25 24 23 22 21
15 14
10 9
5
4
0
opc
L
0
1
1
0
1
0
0
1
1
1
imm7
Rt2
Rn
Rt
31 30 29 28 27 26 25 24 23 22 21
15 14
10 9
5
4
0
opc
L
0
1
1
0
1
0
0
1
0
1
imm7
Rt2
Rn
Rt
31 30 29 28 27 26 25 24 23 22 21
15 14
10 9
5
4
0
opc
L

A64 Base Instruction Descriptions 
C6.2 Alphabetical list of A64 base instructions
C6-1104
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
ARM DDI 0487G.b
Non-Confidential
ID072021
Notes for all encodings
For information about the CONSTRAINED UNPREDICTABLE behavior of this instruction, see Appendix K1 
Architectural Constraints on UNPREDICTABLE Behaviors, and particularly LDPSW on page K1-8416.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt1>` | Is the 64-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt2>` | Is the 64-bit name of the second general-purpose register to be transferred, encoded in the "Rt2" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<imm>` | For the post-index and pre-index variant: is the signed immediate byte offset, a multiple of 4 in the range -256 to 252, |


</details>


*PDF 跨页*：p1103-p1106（共 4 页）



### 4.33 `LDR (immediate)` (C6.2.132)

**语义**：Load Register (immediate) loads a word or doubleword from memory and writes it to a register. The address that is used for the load is calculated from a base register and an immediate offset. For information about memory accesses, see Load/store addressing modes on page C1-202. The Unsigned offset variant scales the immediate offset value by the size of the value accessed before adding it to the base register value.


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the signed immediate byte offset, in the range -256 to 255, encoded in the "imm9" field. |

| `<pimm>` | For the 32-bit variant: is the optional positive immediate byte offset, a multiple of 4 in the range 0 to 16380, default |


</details>


*PDF 跨页*：p1106-p1109（共 4 页）



### 4.34 `LDR (literal)` (C6.2.133)

**语义**：Load Register (literal) calculates an address from the PC value and an immediate offset, loads a word from memory, and writes it to a register. For information about memory accesses, see Load/store addressing modes on page C1-202.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address = PC[] + offset;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<label>` | Is the program label from which the data is to be loaded. Its offset from the address of this instruction, in the range  |


</details>


*PDF 跨页*：p1109-p1111（共 3 页）



### 4.35 `LDR (register)` (C6.2.134)

**语义**：Load Register (register) calculates an address from a base register value and an offset register value, loads a word from memory, and writes it to a register. The offset register value can optionally be shifted and extended. For information about memory accesses, see Load/store addressing modes on page C1-202.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) offset = ExtendReg(m, extend_type, shift);
```

</details>


<details><summary>Assembler symbols / 操作数含义（7 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<Wm>` | When option<0> is set to 0, is the 32-bit name of the general-purpose index register, encoded in the "Rm" field. |

| `<Xm>` | When option<0> is set to 1, is the 64-bit name of the general-purpose index register, encoded in the "Rm" field. |

| `<extend>` | Is the index extend/shift specifier, defaulting to LSL, and which must be omitted for the LSL option when <amount> is om |

| `<amount>` | For the 32-bit variant: is the index shift amount, optional only when <extend> is not LSL. Where it is permitted to be o |


</details>


*PDF 跨页*：p1111-p1113（共 3 页）



### 4.36 `LDRAA, LDRAB` (C6.2.135)

**语义**：Load Register, with pointer authentication. This instruction authenticates an address from a base register using a modifier of zero and the specified key, adds an immediate offset to the authenticated address, and loads a 64-bit doubleword from memory at this resulting address into a register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. 1 1 1 1 1 0 0 0 M S 1 i |


</details>


*PDF 跨页*：p1113-p1115（共 3 页）



### 4.37 `LDRB (immediate)` (C6.2.136)

**语义**：Load Register Byte (immediate) loads a byte from memory, zero-extends it, and writes the result to a register. The address that is used for the load is calculated from a base register and an immediate offset. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDRB <Wt>, [<Xn|SP>], #<simm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
boolean wback = TRUE; 
 boolean postindex = TRUE; 
 bits(64) offset = SignExtend(imm9, 64); 
Pre-index
Encoding
LDRB <Wt>, [<Xn|SP>, #<simm>]!
Decode for this encoding
 boolean wback = TRUE; 
 boolean postindex = FALSE; 
 bits(64) offset = SignExtend(imm9, 64); 
Unsigned offset
Encoding
LDRB <Wt>, [<Xn|SP>{, #<pimm>}]
Decode for this encoding
 boolean wback = FALSE; 
 boolean postindex = FALSE; 
 bits(64) offset = LSL(ZeroExtend(imm12, 64), 0); 
0
0
1
1
1
0
0
0
0
1
0
imm9
0
1
Rn
Rt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0
size
opc
0
0
1
1
1
0
0
0
0
1
0
imm9
1
1
Rn
Rt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0
size
opc
0
0
1
1
1
0
0
1
0
1
imm12
Rn
Rt
31 30 29 28 27 26 25 24 23 22 21
10 9
5
4
0
size
opc

A64 Base Instruction Descriptions 
C6.2 Alphabetical list of A64 base instructions
C6-1116
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
ARM DDI 0487G.b
Non-Confidential
ID072021
Notes for all encodings
For information about the CONSTRAINED UNPREDICTABLE behavior of this instruction, see Appendix K1 
Architectural Constraints on UNPREDICTABLE Behaviors, and particularly LDRB (immediate) on page K1-8417.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the signed immediate byte offset, in the range -256 to 255, encoded in the "imm9" field. |

| `<pimm>` | Is the optional positive immediate byte offset, in the range 0 to 4095, defaulting to 0 and encoded in the "imm12" field |


</details>


*PDF 跨页*：p1115-p1118（共 4 页）



### 4.38 `LDRB (register)` (C6.2.137)

**语义**：Load Register Byte (register) calculates an address from a base register value and an offset register value, loads a byte from memory, zero-extends it, and writes it to a register. For information about memory accesses, see Load/store addressing modes on page C1-202.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) offset = ExtendReg(m, extend_type, 0);
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<Wm>` | When option<0> is set to 0, is the 32-bit name of the general-purpose index register, encoded in the "Rm" field. |

| `<Xm>` | When option<0> is set to 1, is the 64-bit name of the general-purpose index register, encoded in the "Rm" field. |

| `<extend>` | Is the index extend specifier, encoded in the "option" field. It can have the following values: UXTW when option = 010 S |

| `<amount>` | Is the index shift amount, it must be #0, encoded in "S" as 0 if omitted, or as 1 if present. Shared decode for all enco |


</details>


*PDF 跨页*：p1118-p1120（共 3 页）



### 4.39 `LDRH (immediate)` (C6.2.138)

**语义**：Load Register Halfword (immediate) loads a halfword from memory, zero-extends it, and writes the result to a register. The address that is used for the load is calculated from a base register and an immediate offset. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDRH <Wt>, [<Xn|SP>], #<simm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
boolean wback = TRUE; 
 boolean postindex = TRUE; 
 bits(64) offset = SignExtend(imm9, 64); 
Pre-index
Encoding
LDRH <Wt>, [<Xn|SP>, #<simm>]!
Decode for this encoding
 boolean wback = TRUE; 
 boolean postindex = FALSE; 
 bits(64) offset = SignExtend(imm9, 64); 
Unsigned offset
Encoding
LDRH <Wt>, [<Xn|SP>{, #<pimm>}]
Decode for this encoding
 boolean wback = FALSE; 
 boolean postindex = FALSE; 
 bits(64) offset = LSL(ZeroExtend(imm12, 64), 1); 
0
1
1
1
1
0
0
0
0
1
0
imm9
0
1
Rn
Rt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0
size
opc
0
1
1
1
1
0
0
0
0
1
0
imm9
1
1
Rn
Rt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0
size
opc
0
1
1
1
1
0
0
1
0
1
imm12
Rn
Rt
31 30 29 28 27 26 25 24 23 22 21
10 9
5
4
0
size
opc

A64 Base Instruction Descriptions 
C6.2 Alphabetical list of A64 base instructions
ARM DDI 0487G.b
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
C6-1121
ID072021
Non-Confidential
Notes for all encodings
For information about the CONSTRAINED UNPREDICTABLE behavior of this instruction, see Appendix K1 
Architectural Constraints on UNPREDICTABLE Behaviors, and particularly LDRH (immediate) on page K1-8417.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the signed immediate byte offset, in the range -256 to 255, encoded in the "imm9" field. |

| `<pimm>` | Is the optional positive immediate byte offset, a multiple of 2 in the range 0 to 8190, defaulting to 0 and encoded in t |


</details>


*PDF 跨页*：p1120-p1123（共 4 页）



### 4.40 `LDRH (register)` (C6.2.139)

**语义**：Load Register Halfword (register) calculates an address from a base register value and an offset register value, loads a halfword from memory, zero-extends it, and writes it to a register. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDRH <Wt>, [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if option<1> == '0' then UNDEFINED;    // sub-word index 
 ExtendType extend_type = DecodeRegExtend(option); 
 integer shift = if S == '1' then 1 else 0;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) offset = ExtendReg(m, extend_type, shift);
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<Wm>` | When option<0> is set to 0, is the 32-bit name of the general-purpose index register, encoded in the "Rm" field. |

| `<Xm>` | When option<0> is set to 1, is the 64-bit name of the general-purpose index register, encoded in the "Rm" field. |

| `<extend>` | Is the index extend/shift specifier, defaulting to LSL, and which must be omitted for the LSL option when <amount> is om |

| `<amount>` | Is the index shift amount, optional only when <extend> is not LSL. Where it is permitted to be optional, it defaults to  |


</details>


*PDF 跨页*：p1123-p1125（共 3 页）



### 4.41 `LDRSB (immediate)` (C6.2.140)

**语义**：Load Register Signed Byte (immediate) loads a byte from memory, sign-extends it to either 32 bits or 64 bits, and writes the result to a register. The address that is used for the load is calculated from a base register and an immediate offset. For information about memory accesses, see Load/store addressing modes on page C1-202.


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the signed immediate byte offset, in the range -256 to 255, encoded in the "imm9" field. |

| `<pimm>` | Is the optional positive immediate byte offset, in the range 0 to 4095, defaulting to 0 and encoded in the "imm12" field |


</details>


*PDF 跨页*：p1125-p1129（共 5 页）



### 4.42 `LDRSB (register)` (C6.2.141)

**语义**：Load Register Signed Byte (register) calculates an address from a base register value and an offset register value, loads a byte from memory, sign-extends it, and writes it to a register. For information about memory accesses, see Load/store addressing modes on page C1-202.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) offset = ExtendReg(m, extend_type, 0);
```

</details>


<details><summary>Assembler symbols / 操作数含义（7 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<Wm>` | When option<0> is set to 0, is the 32-bit name of the general-purpose index register, encoded in the "Rm" field. |

| `<Xm>` | When option<0> is set to 1, is the 64-bit name of the general-purpose index register, encoded in the "Rm" field. |

| `<extend>` | Is the index extend specifier, encoded in the "option" field. It can have the following values: UXTW when option = 010 S |

| `<amount>` | Is the index shift amount, it must be #0, encoded in "S" as 0 if omitted, or as 1 if present. 0 0 1 1 1 0 0 0 1 x 1 Rm o |


</details>


*PDF 跨页*：p1129-p1131（共 3 页）



### 4.43 `LDRSH (immediate)` (C6.2.142)

**语义**：Load Register Signed Halfword (immediate) loads a halfword from memory, sign-extends it to 32 bits or 64 bits, and writes the result to a register. The address that is used for the load is calculated from a base register and an immediate offset. For information about memory accesses, see Load/store addressing modes on page C1-202.


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the signed immediate byte offset, in the range -256 to 255, encoded in the "imm9" field. |

| `<pimm>` | Is the optional positive immediate byte offset, a multiple of 2 in the range 0 to 8190, defaulting to 0 and encoded in t |


</details>


*PDF 跨页*：p1131-p1135（共 5 页）



### 4.44 `LDRSH (register)` (C6.2.143)

**语义**：Load Register Signed Halfword (register) calculates an address from a base register value and an offset register value, loads a halfword from memory, sign-extends it, and writes it to a register. For information about memory accesses see Load/store addressing modes on page C1-202.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) offset = ExtendReg(m, extend_type, shift);
```

</details>


<details><summary>Assembler symbols / 操作数含义（7 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<Wm>` | When option<0> is set to 0, is the 32-bit name of the general-purpose index register, encoded in the "Rm" field. |

| `<Xm>` | When option<0> is set to 1, is the 64-bit name of the general-purpose index register, encoded in the "Rm" field. |

| `<extend>` | Is the index extend/shift specifier, defaulting to LSL, and which must be omitted for the LSL option when <amount> is om |

| `<amount>` | Is the index shift amount, optional only when <extend> is not LSL. Where it is permitted to be optional, it defaults to  |


</details>


*PDF 跨页*：p1135-p1137（共 3 页）



### 4.45 `LDRSW (immediate)` (C6.2.144)

**语义**：Load Register Signed Word (immediate) loads a word from memory, sign-extends it to 64 bits, and writes the result to a register. The address that is used for the load is calculated from a base register and an immediate offset. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDRSW <Xt>, [<Xn|SP>], #<simm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
boolean wback = TRUE; 
 boolean postindex = TRUE; 
 bits(64) offset = SignExtend(imm9, 64); 
Pre-index
Encoding
LDRSW <Xt>, [<Xn|SP>, #<simm>]!
Decode for this encoding
 boolean wback = TRUE; 
 boolean postindex = FALSE; 
 bits(64) offset = SignExtend(imm9, 64); 
Unsigned offset
Encoding
LDRSW <Xt>, [<Xn|SP>{, #<pimm>}]
Decode for this encoding
 boolean wback = FALSE; 
 boolean postindex = FALSE; 
 bits(64) offset = LSL(ZeroExtend(imm12, 64), 2); 
1
0
1
1
1
0
0
0
1
0
0
imm9
0
1
Rn
Rt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0
size
opc
1
0
1
1
1
0
0
0
1
0
0
imm9
1
1
Rn
Rt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0
size
opc
1
0
1
1
1
0
0
1
1
0
imm12
Rn
Rt
31 30 29 28 27 26 25 24 23 22 21
10 9
5
4
0
size
opc

A64 Base Instruction Descriptions 
C6.2 Alphabetical list of A64 base instructions
C6-1138
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
ARM DDI 0487G.b
Non-Confidential
ID072021
Notes for all encodings
For information about the CONSTRAINED UNPREDICTABLE behavior of this instruction, see Appendix K1 
Architectural Constraints on UNPREDICTABLE Behaviors, and particularly LDRSW (immediate) on 
page K1-8418.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the signed immediate byte offset, in the range -256 to 255, encoded in the "imm9" field. |

| `<pimm>` | Is the optional positive immediate byte offset, a multiple of 4 in the range 0 to 16380, defaulting to 0 and encoded in  |


</details>


*PDF 跨页*：p1137-p1140（共 4 页）



### 4.46 `LDRSW (literal)` (C6.2.145)

**语义**：Load Register Signed Word (literal) calculates an address from the PC value and an immediate offset, loads a word from memory, and writes it to a register. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDRSW <Xt>, <label>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer t = UInt(Rt); 
 bits(64) offset; 
  
 offset = SignExtend(imm19:'00', 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address = PC[] + offset;
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<label>` | Is the program label from which the data is to be loaded. Its offset from the address of this instruction, in the range  |


</details>


*PDF 跨页*：p1140-p1141（共 2 页）



### 4.47 `LDRSW (register)` (C6.2.146)

**语义**：Load Register Signed Word (register) calculates an address from a base register value and an offset register value, loads a word from memory, sign-extends it to form a 64-bit value, and writes it to a register. The offset register value can be shifted left by 0 or 2 bits. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDRSW <Xt>, [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if option<1> == '0' then UNDEFINED;    // sub-word index 
 ExtendType extend_type = DecodeRegExtend(option); 
 integer shift = if S == '1' then 2 else 0;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) offset = ExtendReg(m, extend_type, shift);
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<Wm>` | When option<0> is set to 0, is the 32-bit name of the general-purpose index register, encoded in the "Rm" field. |

| `<Xm>` | When option<0> is set to 1, is the 64-bit name of the general-purpose index register, encoded in the "Rm" field. |

| `<extend>` | Is the index extend/shift specifier, defaulting to LSL, and which must be omitted for the LSL option when <amount> is om |

| `<amount>` | Is the index shift amount, optional only when <extend> is not LSL. Where it is permitted to be optional, it defaults to  |


</details>


*PDF 跨页*：p1141-p1143（共 3 页）



### 4.48 `LDSETB, LDSETAB, LDSETALB, LDSETLB` (C6.2.147)

> 💡 **被以下指令作为别名使用**：`STSETB`


**语义**：Atomic bit set on byte in memory atomically loads an 8-bit byte from memory, performs a bitwise OR with the value held in a register on it, and stores the result back to memory. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1143-p1145（共 3 页）



### 4.49 `LDSETH, LDSETAH, LDSETALH, LDSETLH` (C6.2.148)

> 💡 **被以下指令作为别名使用**：`STSETH`


**语义**：Atomic bit set on halfword in memory atomically loads a 16-bit halfword from memory, performs a bitwise OR with the value held in a register on it, and stores the result back to memory. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1145-p1147（共 3 页）



### 4.50 `LDSET, LDSETA, LDSETAL, LDSETL` (C6.2.149)

> 💡 **被以下指令作为别名使用**：`STSET`


**语义**：Atomic bit set on word or doubleword in memory atomically loads a 32-bit word or 64-bit doubleword from memory, performs a bitwise OR with the value held in a register on it, and stores the result back to memory. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1147-p1150（共 4 页）



### 4.51 `LDSMAXB, LDSMAXAB, LDSMAXALB, LDSMAXLB` (C6.2.150)

> 💡 **被以下指令作为别名使用**：`STSMAXB`


**语义**：Atomic signed maximum on byte in memory atomically loads an 8-bit byte from memory, compares it against the value held in a register, and stores the larger value back to memory, treating the values as signed numbers. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1150-p1152（共 3 页）



### 4.52 `LDSMAXH, LDSMAXAH, LDSMAXALH, LDSMAXLH` (C6.2.151)

> 💡 **被以下指令作为别名使用**：`STSMAXH`


**语义**：Atomic signed maximum on halfword in memory atomically loads a 16-bit halfword from memory, compares it against the value held in a register, and stores the larger value back to memory, treating the values as signed numbers. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1152-p1154（共 3 页）



### 4.53 `LDSMAX, LDSMAXA, LDSMAXAL, LDSMAXL` (C6.2.152)

> 💡 **被以下指令作为别名使用**：`STSMAX`


**语义**：Atomic signed maximum on word or doubleword in memory atomically loads a 32-bit word or 64-bit doubleword from memory, compares it against the value held in a register, and stores the larger value back to memory, treating the values as signed numbers. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1154-p1157（共 4 页）



### 4.54 `LDSMINB, LDSMINAB, LDSMINALB, LDSMINLB` (C6.2.153)

> 💡 **被以下指令作为别名使用**：`STSMINB`


**语义**：Atomic signed minimum on byte in memory atomically loads an 8-bit byte from memory, compares it against the value held in a register, and stores the smaller value back to memory, treating the values as signed numbers. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1157-p1159（共 3 页）



### 4.55 `LDSMINH, LDSMINAH, LDSMINALH, LDSMINLH` (C6.2.154)

> 💡 **被以下指令作为别名使用**：`STSMINH`


**语义**：Atomic signed minimum on halfword in memory atomically loads a 16-bit halfword from memory, compares it against the value held in a register, and stores the smaller value back to memory, treating the values as signed numbers. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1159-p1161（共 3 页）



### 4.56 `LDSMIN, LDSMINA, LDSMINAL, LDSMINL` (C6.2.155)

> 💡 **被以下指令作为别名使用**：`STSMIN`


**语义**：Atomic signed minimum on word or doubleword in memory atomically loads a 32-bit word or 64-bit doubleword from memory, compares it against the value held in a register, and stores the smaller value back to memory, treating the values as signed numbers. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1161-p1164（共 4 页）



### 4.57 `LDTR` (C6.2.156)

**语义**：Load Register (unprivileged) loads a word or doubleword from memory, and writes it to a register. The address that is used for the load is calculated from a base register and an immediate offset.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1164-p1166（共 3 页）



### 4.58 `LDTRB` (C6.2.157)

**语义**：Load Register Byte (unprivileged) loads a byte from memory, zero-extends it, and writes the result to a register. The address that is used for the load is calculated from a base register and an immediate offset.


**汇编模板**：
```
LDTRB <Wt>, [<Xn|SP>{, #<simm>}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
bits(64) offset = SignExtend(imm9, 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1166-p1168（共 3 页）



### 4.59 `LDTRH` (C6.2.158)

**语义**：Load Register Halfword (unprivileged) loads a halfword from memory, zero-extends it, and writes the result to a register. The address that is used for the load is calculated from a base register and an immediate offset.


**汇编模板**：
```
LDTRH <Wt>, [<Xn|SP>{, #<simm>}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
bits(64) offset = SignExtend(imm9, 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1168-p1170（共 3 页）



### 4.60 `LDTRSB` (C6.2.159)

**语义**：Load Register Signed Byte (unprivileged) loads a byte from memory, sign-extends it to 32 bits or 64 bits, and writes the result to a register. The address that is used for the load is calculated from a base register and an immediate offset.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1170-p1172（共 3 页）



### 4.61 `LDTRSH` (C6.2.160)

**语义**：Load Register Signed Halfword (unprivileged) loads a halfword from memory, sign-extends it to 32 bits or 64 bits, and writes the result to a register. The address that is used for the load is calculated from a base register and an immediate offset.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1172-p1174（共 3 页）



### 4.62 `LDTRSW` (C6.2.161)

**语义**：Load Register Signed Word (unprivileged) loads a word from memory, sign-extends it to 64 bits, and writes the result to a register. The address that is used for the load is calculated from a base register and an immediate offset.


**汇编模板**：
```
LDTRSW <Xt>, [<Xn|SP>{, #<simm>}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
bits(64) offset = SignExtend(imm9, 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1174-p1176（共 3 页）



### 4.63 `LDUMAXB, LDUMAXAB, LDUMAXALB, LDUMAXLB` (C6.2.162)

> 💡 **被以下指令作为别名使用**：`STUMAXB`


**语义**：Atomic unsigned maximum on byte in memory atomically loads an 8-bit byte from memory, compares it against the value held in a register, and stores the larger value back to memory, treating the values as unsigned numbers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1176-p1178（共 3 页）



### 4.64 `LDUMAXH, LDUMAXAH, LDUMAXALH, LDUMAXLH` (C6.2.163)

> 💡 **被以下指令作为别名使用**：`STUMAXH`


**语义**：Atomic unsigned maximum on halfword in memory atomically loads a 16-bit halfword from memory, compares it against the value held in a register, and stores the larger value back to memory, treating the values as unsigned numbers. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1178-p1180（共 3 页）



### 4.65 `LDUMAX, LDUMAXA, LDUMAXAL, LDUMAXL` (C6.2.164)

> 💡 **被以下指令作为别名使用**：`STUMAX`


**语义**：Atomic unsigned maximum on word or doubleword in memory atomically loads a 32-bit word or 64-bit doubleword from memory, compares it against the value held in a register, and stores the larger value back to memory, treating the values as unsigned numbers. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1180-p1183（共 4 页）



### 4.66 `LDUMINB, LDUMINAB, LDUMINALB, LDUMINLB` (C6.2.165)

> 💡 **被以下指令作为别名使用**：`STUMINB`


**语义**：Atomic unsigned minimum on byte in memory atomically loads an 8-bit byte from memory, compares it against the value held in a register, and stores the smaller value back to memory, treating the values as unsigned numbers. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1183-p1185（共 3 页）



### 4.67 `LDUMINH, LDUMINAH, LDUMINALH, LDUMINLH` (C6.2.166)

> 💡 **被以下指令作为别名使用**：`STUMINH`


**语义**：Atomic unsigned minimum on halfword in memory atomically loads a 16-bit halfword from memory, compares it against the value held in a register, and stores the smaller value back to memory, treating the values as unsigned numbers. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1185-p1187（共 3 页）



### 4.68 `LDUMIN, LDUMINA, LDUMINAL, LDUMINL` (C6.2.167)

> 💡 **被以下指令作为别名使用**：`STUMIN`


**语义**：Atomic unsigned minimum on word or doubleword in memory atomically loads a 32-bit word or 64-bit doubleword from memory, compares it against the value held in a register, and stores the smaller value back to memory, treating the values as unsigned numbers. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1187-p1190（共 4 页）



### 4.69 `LDUR` (C6.2.168)

**语义**：Load Register (unscaled) calculates an address from a base register and an immediate offset, loads a 32-bit word or 64-bit doubleword from memory, zero-extends it, and writes it to a register. For information about memory accesses, see Load/store addressing modes on page C1-202.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1190-p1192（共 3 页）



### 4.70 `LDURB` (C6.2.169)

**语义**：Load Register Byte (unscaled) calculates an address from a base register and an immediate offset, loads a byte from memory, zero-extends it, and writes it to a register. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDURB <Wt>, [<Xn|SP>{, #<simm>}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
bits(64) offset = SignExtend(imm9, 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1192-p1193（共 2 页）



### 4.71 `LDURH` (C6.2.170)

**语义**：Load Register Halfword (unscaled) calculates an address from a base register and an immediate offset, loads a halfword from memory, zero-extends it, and writes it to a register. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDURH <Wt>, [<Xn|SP>{, #<simm>}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
bits(64) offset = SignExtend(imm9, 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1193-p1194（共 2 页）



### 4.72 `LDURSB` (C6.2.171)

**语义**：Load Register Signed Byte (unscaled) calculates an address from a base register and an immediate offset, loads a signed byte from memory, sign-extends it, and writes it to a register. For information about memory accesses, see Load/store addressing modes on page C1-202.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1194-p1196（共 3 页）



### 4.73 `LDURSH` (C6.2.172)

**语义**：Load Register Signed Halfword (unscaled) calculates an address from a base register and an immediate offset, loads a signed halfword from memory, sign-extends it, and writes it to a register. For information about memory accesses, see Load/store addressing modes on page C1-202.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1196-p1198（共 3 页）



### 4.74 `LDURSW` (C6.2.173)

**语义**：Load Register Signed Word (unscaled) calculates an address from a base register and an immediate offset, loads a signed word from memory, sign-extends it, and writes it to a register. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDURSW <Xt>, [<Xn|SP>{, #<simm>}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
bits(64) offset = SignExtend(imm9, 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1198-p1199（共 2 页）



### 4.75 `LDXP` (C6.2.174)

**语义**：Load Exclusive Pair of Registers derives an address from a base register value, loads two 32-bit words or two 64-bit doublewords from memory, and writes them to two registers. For information on single-copy atomicity and alignment requirements, see Requirements for single-copy atomicity on page B2-128 and Alignment of data accesses on page B2-160. The PE marks the physical address being accessed as an exclusive access. This exclusive access mark is checked by Store Exclusive instructions. See Sy


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt1>` | Is the 32-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Wt2>` | Is the 32-bit name of the second general-purpose register to be transferred, encoded in the "Rt2" field. |

| `<Xt1>` | Is the 64-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. 1 sz 0 0 1 0 0 0  |


</details>


*PDF 跨页*：p1199-p1201（共 3 页）



### 4.76 `LDXR` (C6.2.175)

**语义**：Load Exclusive Register derives an address from a base register value, loads a 32-bit word or a 64-bit doubleword from memory, and writes it to a register. The memory access is atomic. The PE marks the physical address being accessed as an exclusive access. This exclusive access mark is checked by Store Exclusive instructions. See Synchronization and semaphores on page B2-179. For information about memory accesses see Load/store addressing modes on page C1-202.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1201-p1203（共 3 页）



### 4.77 `LDXRB` (C6.2.176)

**语义**：Load Exclusive Register Byte derives an address from a base register value, loads a byte from memory, zero-extends it and writes it to a register. The memory access is atomic. The PE marks the physical address being accessed as an exclusive access. This exclusive access mark is checked by Store Exclusive instructions. See Synchronization and semaphores on page B2-179. For information about memory accesses see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDXRB <Wt>, [<Xn|SP>{,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn); 
 integer t = UInt(Rt); 
  
 boolean tag_checked = n != 31;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1203-p1204（共 2 页）



### 4.78 `LDXRH` (C6.2.177)

**语义**：Load Exclusive Register Halfword derives an address from a base register value, loads a halfword from memory, zero-extends it and writes it to a register. The memory access is atomic. The PE marks the physical address being accessed as an exclusive access. This exclusive access mark is checked by Store Exclusive instructions. See Synchronization and semaphores on page B2-179. For information about memory accesses see Load/store addressing modes on page C1-202.


**汇编模板**：
```
LDXRH <Wt>, [<Xn|SP>{,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn); 
 integer t = UInt(Rt); 
  
 boolean tag_checked = n != 31;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1204-p1205（共 2 页）



### 4.79 `LSL (register)` (C6.2.178)

> ⚠️ **这是 `LSLV` 的别名**。底层编码与 `LSLV` 相同，只是汇编器接受不同写法。


**语义**：Logical Shift Left (register) shifts a register value left by a variable number of bits, shifting in zeros, and writes the result to the destination register. The remainder obtained by dividing the second source register by the data size defines the number of bits by which the first source register is left-shifted.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LSLV gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding a shift amount from 0 to 31 in its bottom 5 bit |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register holding a shift amount from 0 to 63 in its bottom 6 bit |


</details>


*PDF 跨页*：p1205-p1207（共 3 页）



### 4.80 `LSL (immediate)` (C6.2.179)

> ⚠️ **这是 `UBFM` 的别名**。底层编码与 `UBFM` 相同，只是汇编器接受不同写法。


**语义**：Logical Shift Left (immediate) shifts a register value left by an immediate number of bits, shifting in zeros, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of UBFM gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<shift>` | For the 32-bit variant: is the shift amount, in the range 0 to 31. For the 64-bit variant: is the shift amount, in the r |


</details>


*PDF 跨页*：p1207-p1209（共 3 页）



### 4.81 `LSLV` (C6.2.180)

> 💡 **被以下指令作为别名使用**：`LSL (register)`


**语义**：Logical Shift Left Variable shifts a register value left by a variable number of bits, shifting in zeros, and writes the result to the destination register. The remainder obtained by dividing the second source register by the data size defines the number of bits by which the first source register is left-shifted.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding a shift amount from 0 to 31 in its bottom 5 bit |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register holding a shift amount from 0 to 63 in its bottom 6 bit |


</details>


*PDF 跨页*：p1209-p1211（共 3 页）



### 4.82 `LSR (register)` (C6.2.181)

> ⚠️ **这是 `LSRV` 的别名**。底层编码与 `LSRV` 相同，只是汇编器接受不同写法。


**语义**：Logical Shift Right (register) shifts a register value right by a variable number of bits, shifting in zeros, and writes the result to the destination register. The remainder obtained by dividing the second source register by the data size defines the number of bits by which the first source register is right-shifted.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LSRV gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding a shift amount from 0 to 31 in its bottom 5 bit |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register holding a shift amount from 0 to 63 in its bottom 6 bit |


</details>


*PDF 跨页*：p1211-p1213（共 3 页）



### 4.83 `LSR (immediate)` (C6.2.182)

> ⚠️ **这是 `UBFM` 的别名**。底层编码与 `UBFM` 相同，只是汇编器接受不同写法。


**语义**：Logical Shift Right (immediate) shifts a register value right by an immediate number of bits, shifting in zeros, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of UBFM gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<shift>` | For the 32-bit variant: is the shift amount, in the range 0 to 31, encoded in the "immr" field. For the 64-bit variant:  |


</details>


*PDF 跨页*：p1213-p1215（共 3 页）



### 4.84 `LSRV` (C6.2.183)

> 💡 **被以下指令作为别名使用**：`LSR (register)`


**语义**：Logical Shift Right Variable shifts a register value right by a variable number of bits, shifting in zeros, and writes the result to the destination register. The remainder obtained by dividing the second source register by the data size defines the number of bits by which the first source register is right-shifted.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding a shift amount from 0 to 31 in its bottom 5 bit |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register holding a shift amount from 0 to 63 in its bottom 6 bit |


</details>


*PDF 跨页*：p1215-p1217（共 3 页）



### 4.85 `MADD` (C6.2.184)

> 💡 **被以下指令作为别名使用**：`MUL`


**语义**：Multiply-Add multiplies two register values, adds a third register value, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(destsize) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（7 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |

| `<Wa>` | Is the 32-bit name of the third general-purpose source register holding the addend, encoded in the "Ra" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. Alia |


</details>


*PDF 跨页*：p1217-p1219（共 3 页）



### 4.86 `MNEG` (C6.2.185)

> ⚠️ **这是 `MSUB` 的别名**。底层编码与 `MSUB` 相同，只是汇编器接受不同写法。


**语义**：Multiply-Negate multiplies two register values, negates the product, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of MSUB gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p1219-p1221（共 3 页）



### 4.87 `MOV (to/from SP)` (C6.2.186)

> ⚠️ **这是 `ADD (immediate)` 的别名**。底层编码与 `ADD (immediate)` 相同，只是汇编器接受不同写法。


**语义**：Move between register and stack pointer : Rd = Rn This instruction is an alias of the ADD (immediate) instruction. This means that: The encodings in this description are named to match the encodings of ADD (immediate).


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of ADD (immediate) gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd|WSP>` | Is the 32-bit name of the destination general-purpose register or stack pointer, encoded in the "Rd" field. |

| `<Wn|WSP>` | Is the 32-bit name of the source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<Xd|SP>` | Is the 64-bit name of the destination general-purpose register or stack pointer, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the source general-purpose register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1221-p1222（共 2 页）



### 4.88 `MOV (inverted wide immediate)` (C6.2.187)

> ⚠️ **这是 `MOVN` 的别名**。底层编码与 `MOVN` 相同，只是汇编器接受不同写法。


**语义**：Move (inverted wide immediate) moves an inverted 16-bit immediate value to a register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of MOVN gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<imm>` | For the 32-bit variant: is a 32-bit immediate, the bitwise inverse of which can be encoded in "imm16:hw", but excluding  |

| `<shift>` | For the 32-bit variant: is the amount by which to shift the immediate left, either 0 (the default) or 16, encoded in the |


</details>


*PDF 跨页*：p1222-p1224（共 3 页）



### 4.89 `MOV (wide immediate)` (C6.2.188)

> ⚠️ **这是 `MOVZ` 的别名**。底层编码与 `MOVZ` 相同，只是汇编器接受不同写法。


**语义**：Move (wide immediate) moves a 16-bit immediate value to a register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of MOVZ gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<imm>` | For the 32-bit variant: is a 32-bit immediate which can be encoded in "imm16:hw". For the 64-bit variant: is a 64-bit im |

| `<shift>` | For the 32-bit variant: is the amount by which to shift the immediate left, either 0 (the default) or 16, encoded in the |


</details>


*PDF 跨页*：p1224-p1226（共 3 页）



### 4.90 `MOV (bitmask immediate)` (C6.2.189)

> ⚠️ **这是 `ORR (immediate)` 的别名**。底层编码与 `ORR (immediate)` 相同，只是汇编器接受不同写法。


**语义**：Move (bitmask immediate) writes a bitmask immediate value to a register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of ORR (immediate) gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd|WSP>` | Is the 32-bit name of the destination general-purpose register or stack pointer, encoded in the "Rd" field. |

| `<Xd|SP>` | Is the 64-bit name of the destination general-purpose register or stack pointer, encoded in the "Rd" field. |

| `<imm>` | For the 32-bit variant: is the bitmask immediate, encoded in "imms:immr", but excluding values which could be encoded by |


</details>


*PDF 跨页*：p1226-p1228（共 3 页）



### 4.91 `MOV (register)` (C6.2.190)

> ⚠️ **这是 `ORR (shifted register)` 的别名**。底层编码与 `ORR (shifted register)` 相同，只是汇编器接受不同写法。


**语义**：Move (register) copies the value in a source register to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of ORR (shifted register) gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wm>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xm>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p1228-p1230（共 3 页）



### 4.92 `MOVK` (C6.2.191)

**语义**：Move wide with keep moves an optionally-shifted 16-bit immediate value into a register, keeping other bits unchanged.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<imm>` | Is the 16-bit unsigned immediate, in the range 0 to 65535, encoded in the "imm16" field. |

| `<shift>` | For the 32-bit variant: is the amount by which to shift the immediate left, either 0 (the default) or 16, encoded in the |


</details>


*PDF 跨页*：p1230-p1232（共 3 页）



### 4.93 `MOVN` (C6.2.192)

> 💡 **被以下指令作为别名使用**：`MOV (inverted wide immediate)`


**语义**：Move wide with NOT moves the inverse of an optionally-shifted 16-bit immediate value to a register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<imm>` | Is the 16-bit unsigned immediate, in the range 0 to 65535, encoded in the "imm16" field. |

| `<shift>` | For the 32-bit variant: is the amount by which to shift the immediate left, either 0 (the default) or 16, encoded in the |


</details>


*PDF 跨页*：p1232-p1234（共 3 页）



### 4.94 `MOVZ` (C6.2.193)

> 💡 **被以下指令作为别名使用**：`MOV (wide immediate)`


**语义**：Move wide with zero moves an optionally-shifted 16-bit immediate value to a register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<imm>` | Is the 16-bit unsigned immediate, in the range 0 to 65535, encoded in the "imm16" field. |

| `<shift>` | For the 32-bit variant: is the amount by which to shift the immediate left, either 0 (the default) or 16, encoded in the |


</details>


*PDF 跨页*：p1234-p1236（共 3 页）



### 4.95 `MRS` (C6.2.194)

**语义**：Move System Register allows the PE to read an AArch64 System register into a general-purpose register.


**汇编模板**：
```
MRS <Xt>, (<systemreg>|S<op0>_<op1>_<Cn>_<Cm>_<op2>)
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
AArch64.CheckSystemAccess('1':o0, op1, CRn, CRm, op2, Rt, L); 
  
 integer t = UInt(Rt); 
  
 integer sys_op0 = 2 + UInt(o0); 
 integer sys_op1 = UInt(op1); 
 integer sys_op2 = UInt(op2); 
 integer sys_crn = UInt(CRn); 
 integer sys_crm = UInt(CRm);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
X[t] = AArch64.SysRegRead(sys_op0, sys_op1, sys_crn, sys_crm, sys_op2);
```

</details>


<details><summary>Assembler symbols / 操作数含义（7 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rt" field. |

| `<systemreg>` | Is a System register name, encoded in the "o0:op1:CRn:CRm:op2". The System register names are defined in Chapter D13 AAr |

| `<op0>` | Is an unsigned immediate, encoded in the "o0" field. It can have the following values: 2 when o0 = 0 3 when o0 = 1 |

| `<op1>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op1" field. |

| `<Cn>` | Is a name 'Cn', with 'n' in the range 0 to 15, encoded in the "CRn" field. |

| `<Cm>` | Is a name 'Cm', with 'm' in the range 0 to 15, encoded in the "CRm" field. |

| `<op2>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op2" field. |


</details>


*PDF 跨页*：p1236-p1237（共 2 页）



### 4.96 `MSR (immediate)` (C6.2.195)

**语义**：Move immediate value to Special Register moves an immediate value to selected bits of the PSTATE. For more information, see PSTATE.


**汇编模板**：
```
MSR <pstatefield>, #<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if op1 == '000' && op2 == '000' then SEE "CFINV"; 
 if op1 == '000' && op2 == '001' then SEE "XAFLAG"; 
 if op1 == '000' && op2 == '010' then SEE "AXFLAG"; 
  
 AArch64.CheckSystemAccess('00', op1, '0100', CRm, op2, '11111', '0'); 
 bits(2) min_EL; 
 boolean need_secure = FALSE; 
  
 case op1 of 
     when '00x' 
         min_EL = EL1; 
     when '010' 
         min_EL = EL1; 
     when '011' 
         min_EL = EL0; 
     when '100' 
         min_EL = EL2; 
     when '101' 
         if !HaveVirtHostExt() then 
             UNDEFINED; 
         min_EL = EL2; 
     when '110' 
         min_EL = EL3; 
     when '111' 
         min_EL = EL1; 
         need_secure = TRUE; 
  
 if UInt(PSTATE.EL) < UInt(min_EL) || (need_secure && !IsSecure()) then 
     UNDEFINED; 
  
 PSTATEField field; 
 case op1:op2 of 
     when '000 011' 
         if !HaveUAOExt() then 
1
1
0
1
0
1
0
1
0
0
0
0
0
op1
0
1
0
0
CRm
op2
1
1
1
1
1
31 30 29 28 27 26 25 24 23 22 21 20 19 18
16 15 14 13 12 11
8
7
5
4
3
2
1
0

A64 Base Instruction Descriptions 
C6.2 Alphabetical list of A64 base instructions
C6-1238
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
ARM DDI 0487G.b
Non-Confidential
ID072021
             UNDEFINED; 
         field = PSTATEField_UAO; 
     when '000 100' 
         if !HavePANExt() then 
             UNDEFINED; 
         field = PSTATEField_PAN; 
     when '000 101' field = PSTATEField_SP; 
     when '011 010' 
         if !HaveDITExt() then 
             UNDEFINED; 
         field = PSTATEField_DIT; 
     when '011 100' 
         if !HaveMTEExt() then 
             UNDEFINED; 
         field = PSTATEField_TCO; 
     when '011 110' field = PSTATEField_DAIFSet; 
     when '011 111' field = PSTATEField_DAIFClr; 
     when '011 001' 
         if !HaveSSBSExt() then 
             UNDEFINED; 
         field = PSTATEField_SSBS; 
     otherwise UNDEFINED; 
  
 // Check that an AArch64 MSR/MRS access to the DAIF flags is permitted 
 if PSTATE.EL == EL0 && field IN {PSTATEField_DAIFSet, PSTATEField_DAIFClr} then 
     if !ELUsingAArch32(EL1) && ((EL2Enabled() && HCR_EL2.<E2H,TGE> == '11') || SCTLR_EL1.UMA == '0') 
then 
         if EL2Enabled() && !ELUsingAArch32(EL2) && HCR_EL2.TGE == '1' then 
             AArch64.SystemAccessTrap(EL2, 0x18); 
         else 
             AArch64.SystemAccessTrap(EL1, 0x18);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
case field of
```

</details>


*PDF 跨页*：p1237-p1240（共 4 页）



### 4.97 `MSR (register)` (C6.2.196)

**语义**：Move general-purpose register to System Register allows the PE to write an AArch64 System register from a general-purpose register.


**汇编模板**：
```
MSR (<systemreg>|S<op0>_<op1>_<Cn>_<Cm>_<op2>), <Xt>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
AArch64.CheckSystemAccess('1':o0, op1, CRn, CRm, op2, Rt, L); 
  
 integer t = UInt(Rt); 
  
 integer sys_op0 = 2 + UInt(o0); 
 integer sys_op1 = UInt(op1); 
 integer sys_op2 = UInt(op2); 
 integer sys_crn = UInt(CRn); 
 integer sys_crm = UInt(CRm);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
AArch64.SysRegWrite(sys_op0, sys_op1, sys_crn, sys_crm, sys_op2, X[t]);
```

</details>


<details><summary>Assembler symbols / 操作数含义（7 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<systemreg>` | Is a System register name, encoded in the "o0:op1:CRn:CRm:op2". The System register names are defined in Chapter D13 AAr |

| `<op0>` | Is an unsigned immediate, encoded in the "o0" field. It can have the following values: 2 when o0 = 0 3 when o0 = 1 |

| `<op1>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op1" field. |

| `<Cn>` | Is a name 'Cn', with 'n' in the range 0 to 15, encoded in the "CRn" field. |

| `<Cm>` | Is a name 'Cm', with 'm' in the range 0 to 15, encoded in the "CRm" field. |

| `<op2>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op2" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rt" field. |


</details>


*PDF 跨页*：p1240-p1241（共 2 页）



### 4.98 `MSUB` (C6.2.197)

> 💡 **被以下指令作为别名使用**：`MNEG`


**语义**：Multiply-Subtract multiplies two register values, subtracts the product from a third register value, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(destsize) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（7 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |

| `<Wa>` | Is the 32-bit name of the third general-purpose source register holding the minuend, encoded in the "Ra" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. Alia |


</details>


*PDF 跨页*：p1241-p1243（共 3 页）



### 4.99 `MUL` (C6.2.198)

> ⚠️ **这是 `MADD` 的别名**。底层编码与 `MADD` 相同，只是汇编器接受不同写法。


**语义**：This instruction is an alias of the MADD instruction. This means that: The encodings in this description are named to match the encodings of MADD.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of MADD gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p1243-p1244（共 2 页）



### 4.100 `MVN` (C6.2.199)

> ⚠️ **这是 `ORN (shifted register)` 的别名**。底层编码与 `ORN (shifted register)` 相同，只是汇编器接受不同写法。


**语义**：Bitwise NOT writes the bitwise inverse of a register value to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of ORN (shifted register) gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wm>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xm>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rm" field. |

| `<shift>` | Is the optional shift to be applied to the final source, defaulting to LSL and encoded in the "shift" field. It can have |

| `<amount>` | For the 32-bit variant: is the shift amount, in the range 0 to 31, defaulting to 0 and encoded in the "imm6" field. For  |


</details>


*PDF 跨页*：p1244-p1246（共 3 页）



### 4.101 `NEG (shifted register)` (C6.2.200)

> ⚠️ **这是 `SUB (shifted register)` 的别名**。底层编码与 `SUB (shifted register)` 相同，只是汇编器接受不同写法。


**语义**：Negate (shifted register) negates an optionally-shifted register value, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SUB (shifted register) gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wm>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xm>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rm" field. |

| `<shift>` | Is the optional shift type to be applied to the second source operand, defaulting to LSL and encoded in the "shift" fiel |

| `<amount>` | For the 32-bit variant: is the shift amount, in the range 0 to 31, defaulting to 0 and encoded in the "imm6" field. For  |


</details>


*PDF 跨页*：p1246-p1248（共 3 页）



### 4.102 `NEGS` (C6.2.201)

> ⚠️ **这是 `SUBS (shifted register)` 的别名**。底层编码与 `SUBS (shifted register)` 相同，只是汇编器接受不同写法。


**语义**：Negate, setting flags, negates an optionally-shifted register value, and writes the result to the destination register. It updates the condition flags based on the result.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SUBS (shifted register) gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wm>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xm>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rm" field. |

| `<shift>` | Is the optional shift type to be applied to the second source operand, defaulting to LSL and encoded in the "shift" fiel |

| `<amount>` | For the 32-bit variant: is the shift amount, in the range 0 to 31, defaulting to 0 and encoded in the "imm6" field. For  |


</details>


*PDF 跨页*：p1248-p1250（共 3 页）



### 4.103 `NGC` (C6.2.202)

> ⚠️ **这是 `SBC` 的别名**。底层编码与 `SBC` 相同，只是汇编器接受不同写法。


**语义**：Negate with Carry negates the sum of a register value and the value of NOT (Carry flag), and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SBC gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wm>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xm>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p1250-p1252（共 3 页）



### 4.104 `NGCS` (C6.2.203)

> ⚠️ **这是 `SBCS` 的别名**。底层编码与 `SBCS` 相同，只是汇编器接受不同写法。


**语义**：Negate with Carry, setting flags, negates the sum of a register value and the value of NOT (Carry flag), and writes the result to the destination register. It updates the condition flags based on the result.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SBCS gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wm>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xm>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p1252-p1254（共 3 页）



### 4.105 `NOP` (C6.2.204)

**语义**：No Operation does nothing, other than advance the value of the program counter by 4. This instruction can be used for instruction alignment purposes.


**汇编模板**：
```
NOP
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
// do nothing
```

</details>


*PDF 跨页*：p1254-p1255（共 2 页）



### 4.106 `ORN (shifted register)` (C6.2.205)

> 💡 **被以下指令作为别名使用**：`MVN`


**语义**：Bitwise OR NOT (shifted register) performs a bitwise (inclusive) OR of a register value and the complement of an optionally-shifted register value, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（7 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<shift>` | Is the optional shift to be applied to the final source, defaulting to LSL and encoded in the "shift" field. It can have |


</details>


*PDF 跨页*：p1255-p1257（共 3 页）



### 4.107 `ORR (immediate)` (C6.2.206)

> 💡 **被以下指令作为别名使用**：`MOV (bitmask immediate)`


**语义**：Bitwise OR (immediate) performs a bitwise (inclusive) OR of a register value and an immediate register value, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd|WSP>` | Is the 32-bit name of the destination general-purpose register or stack pointer, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<Xd|SP>` | Is the 64-bit name of the destination general-purpose register or stack pointer, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<imm>` | For the 32-bit variant: is the bitmask immediate, encoded in "imms:immr". For the 64-bit variant: is the bitmask immedia |


</details>


*PDF 跨页*：p1257-p1259（共 3 页）



### 4.108 `ORR (shifted register)` (C6.2.207)

> 💡 **被以下指令作为别名使用**：`MOV (register)`


**语义**：Bitwise OR (shifted register) performs a bitwise (inclusive) OR of a register value and an optionally-shifted register value, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（7 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<shift>` | Is the optional shift to be applied to the final source, defaulting to LSL and encoded in the "shift" field. It can have |


</details>


*PDF 跨页*：p1259-p1261（共 3 页）



### 4.109 `PACDA, PACDZA` (C6.2.208)

**语义**：Pointer Authentication Code for Data address, using key A. This instruction computes and inserts a pointer authentication code for a data address, using a modifier and key A.


<details><summary>Operation 伪代码（点击展开）</summary>

```
if source_is_sp then
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose source register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1261-p1262（共 2 页）



### 4.110 `PACDB, PACDZB` (C6.2.209)

**语义**：Pointer Authentication Code for Data address, using key B. This instruction computes and inserts a pointer authentication code for a data address, using a modifier and key B.


<details><summary>Operation 伪代码（点击展开）</summary>

```
if source_is_sp then
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose source register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1262-p1263（共 2 页）



### 4.111 `PACGA` (C6.2.210)

**语义**：Pointer Authentication Code, using Generic key. This instruction computes the pointer authentication code for an address in the first source register, using a modifier in the second source register, and the Generic key. The computed pointer authentication code is returned in the upper 32 bits of the destination register.


**汇编模板**：
```
PACGA <Xd>, <Xn>, <Xm|SP>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
boolean source_is_sp = FALSE; 
 integer d = UInt(Rd); 
 integer n = UInt(Rn); 
 integer m = UInt(Rm); 
  
 if !HavePACExt() then 
     UNDEFINED; 
  
 if m == 31 then source_is_sp = TRUE;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
if source_is_sp then
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm|SP>` | Is the 64-bit name of the second general-purpose source register or stack pointer, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p1263-p1264（共 2 页）



### 4.112 `PACIA, PACIA1716, PACIASP, PACIAZ, PACIZA` (C6.2.211)

**语义**：Pointer Authentication Code for Instruction address, using key A. This instruction computes and inserts a pointer authentication code for an instruction address, using a modifier and key A.


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose source register or stack pointer, encoded in the "Rn" field. Operation for all |


</details>


*PDF 跨页*：p1264-p1267（共 4 页）



### 4.113 `PACIB, PACIB1716, PACIBSP, PACIBZ, PACIZB` (C6.2.212)

**语义**：Pointer Authentication Code for Instruction address, using key B. This instruction computes and inserts a pointer authentication code for an instruction address, using a modifier and key B.


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose source register or stack pointer, encoded in the "Rn" field. Operation for all |


</details>


*PDF 跨页*：p1267-p1270（共 4 页）



### 4.114 `PRFM (immediate)` (C6.2.213)

**语义**：Prefetch Memory (immediate) signals the memory system that data memory accesses from a specified address are likely to occur in the near future. The memory system can respond by taking actions that are expected to speed up the memory accesses when they do occur, such as preloading the cache line containing the specified address into one or more caches.


**汇编模板**：
```
PRFM (<prfop>|#<imm5>), [<Xn|SP>{, #<pimm>}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
bits(64) offset = LSL(ZeroExtend(imm12, 64), 3);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<prfop>` | Is the prefetch operation, defined as <type><target><policy>. <type> is one of: PLD Prefetch for load, encoded in the "R |

| `<imm5>` | Is the prefetch operation encoding as an immediate, in the range 0 to 31, encoded in the "Rt" field. This syntax is only |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<pimm>` | Is the optional positive immediate byte offset, a multiple of 8 in the range 0 to 32760, defaulting to 0 and encoded in  |


</details>


*PDF 跨页*：p1270-p1272（共 3 页）



### 4.115 `PRFM (literal)` (C6.2.214)

**语义**：Prefetch Memory (literal) signals the memory system that data memory accesses from a specified address are likely to occur in the near future. The memory system can respond by taking actions that are expected to speed up the memory accesses when they do occur, such as preloading the cache line containing the specified address into one or more caches.


**汇编模板**：
```
PRFM (<prfop>|#<imm5>), <label>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer t = UInt(Rt); 
 bits(64) offset; 
  
 offset = SignExtend(imm19:'00', 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address = PC[] + offset;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<prfop>` | Is the prefetch operation, defined as <type><target><policy>. <type> is one of: PLD Prefetch for load, encoded in the "R |

| `<imm5>` | Is the prefetch operation encoding as an immediate, in the range 0 to 31, encoded in the "Rt" field. This syntax is only |

| `<label>` | Is the program label from which the data is to be loaded. Its offset from the address of this instruction, in the range  |


</details>


*PDF 跨页*：p1272-p1274（共 3 页）



### 4.116 `PRFM (register)` (C6.2.215)

**语义**：Prefetch Memory (register) signals the memory system that data memory accesses from a specified address are likely to occur in the near future. The memory system can respond by taking actions that are expected to speed up the memory accesses when they do occur, such as preloading the cache line containing the specified address into one or more caches.


**汇编模板**：
```
PRFM (<prfop>|#<imm5>), [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if option<1> == '0' then UNDEFINED;    // sub-word index 
 ExtendType extend_type = DecodeRegExtend(option); 
 integer shift = if S == '1' then 3 else 0;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) offset = ExtendReg(m, extend_type, shift);
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<prfop>` | Is the prefetch operation, defined as <type><target><policy>. <type> is one of: PLD Prefetch for load, encoded in the "R |

| `<imm5>` | Is the prefetch operation encoding as an immediate, in the range 0 to 31, encoded in the "Rt" field. This syntax is only |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<Wm>` | When option<0> is set to 0, is the 32-bit name of the general-purpose index register, encoded in the "Rm" field. 1 1 1 1 |


</details>


*PDF 跨页*：p1274-p1276（共 3 页）



### 4.117 `PRFUM` (C6.2.216)

**语义**：Prefetch Memory (unscaled offset) signals the memory system that data memory accesses from a specified address are likely to occur in the near future. The memory system can respond by taking actions that are expected to speed up the memory accesses when they do occur, such as preloading the cache line containing the specified address into one or more caches.


**汇编模板**：
```
PRFUM (<prfop>|#<imm5>), [<Xn|SP>{, #<simm>}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
bits(64) offset = SignExtend(imm9, 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<prfop>` | Is the prefetch operation, defined as <type><target><policy>. <type> is one of: PLD Prefetch for load, encoded in the "R |

| `<imm5>` | Is the prefetch operation encoding as an immediate, in the range 0 to 31, encoded in the "Rt" field. This syntax is only |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the optional signed immediate byte offset, in the range -256 to 255, defaulting to 0 and encoded in the "imm9" field. |


</details>


*PDF 跨页*：p1276-p1278（共 3 页）



### 4.118 `PSSBB` (C6.2.218)

> ⚠️ **这是 `DSB` 的别名**。底层编码与 `DSB` 相同，只是汇编器接受不同写法。


**语义**：Physical Speculative Store Bypass Barrier is a memory barrier which prevents speculative loads from bypassing earlier stores to the same physical address.


**汇编模板**：
```
PSSBB
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of DSB gives the operational pseudocode for this instruction.
```

</details>


*PDF 跨页*：p1279-p1280（共 2 页）



### 4.119 `HINT` (C6.2.92)

**语义**：Hint instruction is for the instruction set space that is reserved for architectural hint instructions.


**汇编模板**：
```
HINT #<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
SystemHintOp op; 
  
 case CRm:op2 of 
     when '0000 000' op = SystemHintOp_NOP; 
     when '0000 001' op = SystemHintOp_YIELD; 
     when '0000 010' op = SystemHintOp_WFE; 
     when '0000 011' op = SystemHintOp_WFI; 
     when '0000 100' op = SystemHintOp_SEV; 
     when '0000 101' op = SystemHintOp_SEVL; 
     when '0000 110' 
         if !HaveDGHExt() then EndOfInstruction();    // Instruction executes as NOP 
         op = SystemHintOp_DGH; 
     when '0000 111' SEE "XPACLRI"; 
     when '0001 xxx' 
         case op2 of 
             when '000' SEE "PACIA1716"; 
             when '010' SEE "PACIB1716"; 
             when '100' SEE "AUTIA1716"; 
             when '110' SEE "AUTIB1716"; 
             otherwise EndOfInstruction(); 
     when '0010 000' 
         if !HaveRASExt() then EndOfInstruction();    // Instruction executes as NOP 
         op = SystemHintOp_ESB; 
     when '0010 001' 
         if !HaveStatisticalProfiling() then EndOfInstruction();    // Instruction executes as NOP 
         op = SystemHintOp_PSB; 
     when '0010 010' 
         if !HaveSelfHostedTrace() then EndOfInstruction();    // Instruction executes as NOP 
         op = SystemHintOp_TSB; 
     when '0010 100' 
         op = SystemHintOp_CSDB; 
     when '0011 xxx' 
         case op2 of 
             when '000' SEE "PACIAZ"; 
             when '001' SEE "PACIASP"; 
             when '010' SEE "PACIBZ"; 
             when '011' SEE "PACIBSP"; 
             when '100' SEE "AUTIAZ"; 
             when '101' SEE "AUTHASP"; 
             when '110' SEE "AUTIBZ"; 
             when '111' SEE "AUTIBSP"; 
     when '0100 xx0' 
         op = SystemHintOp_BTI; 
         // Check branch target compatibility between BTI instruction and PSTATE.BTYPE 
1
1
0
1
0
1
0
1
0
0
0
0
0
0
1
1
0
0
1
0
CRm
op2
1
1
1
1
1
31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11
8
7
5
4
3
2
1
0

A64 Base Instruction Descriptions 
C6.2 Alphabetical list of A64 base instructions
ARM DDI 0487G.b
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
C6-1033
ID072021
Non-Confidential
         SetBTypeCompatible(BTypeCompatible_BTI(op2<2:1>)); 
     otherwise EndOfInstruction();
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
case op of
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<imm>` | Is a 7-bit unsigned immediate, in the range 0 to 127 encoded in the "CRm:op2" field. The encodings that are allocated to |


</details>


*PDF 跨页*：p1032-p1034（共 3 页）



### 4.120 `HLT` (C6.2.93)

**语义**：Halt instruction. An HLT instruction can generate a Halt Instruction debug event, which causes entry into Debug state.


**汇编模板**：
```
HLT #<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if EDSCR.HDE == '0' || !HaltingAllowed() then UNDEFINED; 
 if HaveBTIExt() then 
     SetBTypeCompatible(TRUE);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
Halt(DebugHalt_HaltInstruction);
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<imm>` | Is a 16-bit unsigned immediate, in the range 0 to 65535, encoded in the "imm16" field. |


</details>


*PDF 跨页*：p1034-p1035（共 2 页）



### 4.121 `HVC` (C6.2.94)

**语义**：Hypervisor Call causes an exception to EL2. Software executing at EL1 can use this instruction to call the hypervisor to request a service.


**汇编模板**：
```
HVC #<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
if !HaveEL(EL2) || PSTATE.EL == EL0 || (PSTATE.EL == EL1 && (!IsSecureEL2Enabled() && IsSecure())) then
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<imm>` | Is a 16-bit unsigned immediate, in the range 0 to 65535, encoded in the "imm16" field. |


</details>


*PDF 跨页*：p1035-p1036（共 2 页）



### 4.122 `IC` (C6.2.95)

> ⚠️ **这是 `SYS` 的别名**。底层编码与 `SYS` 相同，只是汇编器接受不同写法。


**语义**：Instruction Cache operation. For more information, see op0==0b01, cache maintenance, TLB maintenance, and address translation instructions on page C5-399.


**汇编模板**：
```
IC <ic_op>{, <Xt>}
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SYS gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<ic_op>` | Is an IC instruction name, as listed for the IC system instruction pages, encoded in the "op1:CRm:op2" field. It can hav |

| `<op1>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op1" field. |

| `<Cm>` | Is a name 'Cm', with 'm' in the range 0 to 15, encoded in the "CRm" field. |

| `<op2>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op2" field. |

| `<Xt>` | Is the 64-bit name of the optional general-purpose source register, defaulting to '11111', encoded in the "Rt" field. |


</details>


*PDF 跨页*：p1036-p1037（共 2 页）



### 4.123 `IRG` (C6.2.96)

**语义**：Insert Random Tag inserts a random Logical Address Tag into the address in the first source register, and writes the result to the destination register. Any tags specified in the optional second source register or in GCR_EL1.Exclude are excluded from the selection of the random Logical Address Tag.


**汇编模板**：
```
IRG <Xd|SP>, <Xn|SP>{, <Xm>}
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveMTEExt() then UNDEFINED; 
 integer d = UInt(Xd); 
 integer n = UInt(Xn); 
 integer m = UInt(Xm);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) operand = if n == 31 then SP[] else X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd|SP>` | Is the 64-bit name of the destination general-purpose register or stack pointer, encoded in the "Xd" field. |

| `<Xn|SP>` | Is the 64-bit name of the first source general-purpose register or stack pointer, encoded in the "Xn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Xm" field. Defaults to XZR if absent. |


</details>


*PDF 跨页*：p1037-p1039（共 3 页）



### 4.124 `ISB` (C6.2.97)

**语义**：Instruction Synchronization Barrier flushes the pipeline in the PE and is a context synchronization event. For more information, see Instruction Synchronization Barrier (ISB) on page B2-147.


**汇编模板**：
```
ISB {<option>|#<imm>}
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// No additional decoding required
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
InstructionSynchronizationBarrier();
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<option>` | Specifies an optional limitation on the barrier operation. Values are: SY Full system barrier operation, encoded as CRm  |

| `<imm>` | Is an optional 4-bit unsigned immediate, in the range 0 to 15, defaulting to 15 and encoded in the "CRm" field. |


</details>


*PDF 跨页*：p1039-p1040（共 2 页）



### 4.125 `LD64B` (C6.2.98)

**语义**：Single-copy Atomic 64-byte Load derives an address from a base register value, loads eight 64-bit doublewords from a memory location, and writes them to consecutive registers, Xt to X(t+7). The data that is loaded is atomic and is required to be 64-byte aligned.


**汇编模板**：
```
LD64B <Xt>, [<Xn|SP> {,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveFeatLS64() then UNDEFINED; 
 if Rt<4:3> == '11' || Rt<0> == '1' then UNDEFINED; 
  
 integer n = UInt(Rn); 
 integer t = UInt(Rt); 
 boolean tag_checked = n != 31;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
CheckLDST64BEnabled();
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1040-p1041（共 2 页）



### 4.126 `LDADDB, LDADDAB, LDADDALB, LDADDLB` (C6.2.99)

> 💡 **被以下指令作为别名使用**：`STADDB`


**语义**：Atomic add on byte in memory atomically loads an 8-bit byte from memory, adds the value held in a register to it, and stores the result back to memory. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1041-p1043（共 3 页）


---


---

📌 **下一步**：回到 [`a64_base_overview.md`](./a64_base_overview.md) 看其他首字母，或 [`isa_reference/README.md`](./README.md) 看其他扩展。
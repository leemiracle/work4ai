# A64_BASE — 指令首字母 A-G 部分

> **生成日期**：2026-06-29  
> **PDF 源版本**：ARM DDI 0487G.b (2021-07)

> a64_base_overview.md`](./a64_base_overview.md) 的拆分之一（按助记符首字母）。
> 含 89 条指令详解。

---

## 目录

- 4.1 `ADC` (C6.2.1)
- 4.2 `ADR` (C6.2.10)
- 4.13 `ADRP` (C6.2.11)
- 4.24 `AND (immediate)` (C6.2.12)
- 4.35 `AND (shifted register)` (C6.2.13)
- 4.46 `ANDS (immediate)` (C6.2.14)
- 4.57 `ANDS (shifted register)` (C6.2.15)
- 4.68 `ASR (register)` (C6.2.16)
- 4.79 `ASR (immediate)` (C6.2.17)
- 4.90 `ASRV` (C6.2.18)
- 4.101 `AT` (C6.2.19)
- 4.112 `ADCS` (C6.2.2)
- 4.113 `AUTDA, AUTDZA` (C6.2.20)
- 4.124 `AUTDB, AUTDZB` (C6.2.21)
- 4.134 `AUTIA, AUTIA1716, AUTIASP, AUTIAZ, AUTIZA` (C6.2.22)
- 4.145 `AUTIB, AUTIB1716, AUTIBSP, AUTIBZ, AUTIZB` (C6.2.23)
- 4.156 `AXFLAG` (C6.2.24)
- 4.187 `BFC` (C6.2.27)
- 4.198 `BFI` (C6.2.28)
- 4.209 `BFM` (C6.2.29)
- 4.220 `ADD (extended register)` (C6.2.3)
- 4.221 `BFXIL` (C6.2.30)
- 4.232 `BIC (shifted register)` (C6.2.31)
- 4.243 `BICS (shifted register)` (C6.2.32)
- 4.254 `BL` (C6.2.33)
- 4.264 `BLR` (C6.2.34)
- 4.275 `BLRAA, BLRAAZ, BLRAB, BLRABZ` (C6.2.35)
- 4.281 `BR` (C6.2.36)
- 4.282 `BRAA, BRAAZ, BRAB, BRABZ` (C6.2.37)
- 4.283 `BRK` (C6.2.38)
- 4.284 `BTI` (C6.2.39)
- 4.285 `ADD (immediate)` (C6.2.4)
- 4.286 `CASB, CASAB, CASALB, CASLB` (C6.2.40)
- 4.287 `CASH, CASAH, CASALH, CASLH` (C6.2.41)
- 4.288 `CASP, CASPA, CASPAL, CASPL` (C6.2.42)
- 4.289 `CAS, CASA, CASAL, CASL` (C6.2.43)
- 4.290 `CBNZ` (C6.2.44)
- 4.291 `CBZ` (C6.2.45)
- 4.292 `CCMN (immediate)` (C6.2.46)
- 4.293 `CCMN (register)` (C6.2.47)
- 4.294 `CCMP (immediate)` (C6.2.48)
- 4.295 `CCMP (register)` (C6.2.49)
- 4.296 `ADD (shifted register)` (C6.2.5)
- 4.297 `CFINV` (C6.2.50)
- 4.298 `CFP` (C6.2.51)
- 4.299 `CINC` (C6.2.52)
- 4.300 `CINV` (C6.2.53)
- 4.301 `CLREX` (C6.2.54)
- 4.302 `CLS` (C6.2.55)
- 4.303 `CLZ` (C6.2.56)
- 4.304 `CMN (extended register)` (C6.2.57)
- 4.305 `CMN (immediate)` (C6.2.58)
- 4.306 `CMN (shifted register)` (C6.2.59)
- 4.307 `ADDG` (C6.2.6)
- 4.308 `CMP (extended register)` (C6.2.60)
- 4.309 `CMP (immediate)` (C6.2.61)
- 4.310 `CMP (shifted register)` (C6.2.62)
- 4.311 `CMPP` (C6.2.63)
- 4.312 `CNEG` (C6.2.64)
- 4.313 `CPP` (C6.2.65)
- 4.314 `CRC32B, CRC32H, CRC32W, CRC32X` (C6.2.66)
- 4.315 `CRC32CB, CRC32CH, CRC32CW, CRC32CX` (C6.2.67)
- 4.316 `CSDB` (C6.2.68)
- 4.317 `CSEL` (C6.2.69)
- 4.318 `ADDS (extended register)` (C6.2.7)
- 4.319 `CSET` (C6.2.70)
- 4.320 `CSETM` (C6.2.71)
- 4.321 `CSINC` (C6.2.72)
- 4.322 `CSINV` (C6.2.73)
- 4.323 `CSNEG` (C6.2.74)
- 4.324 `DC` (C6.2.75)
- 4.325 `DCPS1` (C6.2.76)
- 4.326 `DCPS2` (C6.2.77)
- 4.327 `DCPS3` (C6.2.78)
- 4.328 `DGH` (C6.2.79)
- 4.329 `ADDS (immediate)` (C6.2.8)
- 4.330 `DMB` (C6.2.80)
- 4.331 `DRPS` (C6.2.81)
- 4.332 `DSB` (C6.2.82)
- 4.333 `DVP` (C6.2.83)
- 4.334 `EON (shifted register)` (C6.2.84)
- 4.335 `EOR (immediate)` (C6.2.85)
- 4.336 `EOR (shifted register)` (C6.2.86)
- 4.337 `ERET` (C6.2.87)
- 4.338 `ERETAA, ERETAB` (C6.2.88)
- 4.339 `ESB` (C6.2.89)
- 4.340 `ADDS (shifted register)` (C6.2.9)
- 4.341 `EXTR` (C6.2.90)
- 4.342 `GMI` (C6.2.91)

---

## 指令详解

### 4.1 `ADC` (C6.2.1)

**语义**：Add with Carry adds two register values and the Carry flag value, and writes the result to the destination register.


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

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p876-p878（共 3 页）



### 4.2 `ADR` (C6.2.10)

**语义**：Form PC-relative address adds an immediate value to the PC value to form a PC-relative address, and writes the result to the destination register.


**汇编模板**：
```
ADR <Xd>, <label>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer d = UInt(Rd); 
 bits(64) imm; 
  
 imm = SignExtend(immhi:immlo, 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) base = PC[];
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<label>` | Is the program label whose address is to be calculated. Its offset from the address of this instruction, in the range +/ |


</details>


*PDF 跨页*：p895-p896（共 2 页）



### 4.3 `ADRP` (C6.2.11)

**语义**：Form PC-relative address to 4KB page adds an immediate value that is shifted left by 12 bits, to the PC value to form a PC-relative address, with the bottom 12 bits masked out, and writes the result to the destination register.


**汇编模板**：
```
ADRP <Xd>, <label>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer d = UInt(Rd); 
 bits(64) imm; 
  
 imm = SignExtend(immhi:immlo:Zeros(12), 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) base = PC[];
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<label>` | Is the program label whose 4KB page address is to be calculated. Its offset from the page address of this instruction, i |


</details>


*PDF 跨页*：p896-p897（共 2 页）



### 4.4 `AND (immediate)` (C6.2.12)

**语义**：Bitwise AND (immediate) performs a bitwise AND of a register value and an immediate value, and writes the result to the destination register.


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


*PDF 跨页*：p897-p899（共 3 页）



### 4.5 `AND (shifted register)` (C6.2.13)

**语义**：Bitwise AND (shifted register) performs a bitwise AND of a register value and an optionally-shifted register value, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（8 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<shift>` | Is the optional shift to be applied to the final source, defaulting to LSL and encoded in the "shift" field. It can have |

| `<amount>` | For the 32-bit variant: is the shift amount, in the range 0 to 31, defaulting to 0 and encoded in the "imm6" field. For  |


</details>


*PDF 跨页*：p899-p901（共 3 页）



### 4.6 `ANDS (immediate)` (C6.2.14)

> 💡 **被以下指令作为别名使用**：`TST (immediate)`


**语义**：Bitwise AND (immediate), setting flags, performs a bitwise AND of a register value and an immediate value, and writes the result to the destination register. It updates the condition flags based on the result.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<imm>` | For the 32-bit variant: is the bitmask immediate, encoded in "imms:immr". For the 64-bit variant: is the bitmask immedia |


</details>


*PDF 跨页*：p901-p903（共 3 页）



### 4.7 `ANDS (shifted register)` (C6.2.15)

> 💡 **被以下指令作为别名使用**：`TST (shifted register)`


**语义**：Bitwise AND (shifted register), setting flags, performs a bitwise AND of a register value and an optionally-shifted register value, and writes the result to the destination register. It updates the condition flags based on the result.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. Alias is preferred when TST |


</details>


*PDF 跨页*：p903-p905（共 3 页）



### 4.8 `ASR (register)` (C6.2.16)

> ⚠️ **这是 `ASRV` 的别名**。底层编码与 `ASRV` 相同，只是汇编器接受不同写法。


**语义**：Arithmetic Shift Right (register) shifts a register value right by a variable number of bits, shifting in copies of its sign bit, and writes the result to the destination register. The remainder obtained by dividing the second source register by the data size defines the number of bits by which the first source register is right-shifted.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of ASRV gives the operational pseudocode for this instruction.
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


*PDF 跨页*：p905-p907（共 3 页）



### 4.9 `ASR (immediate)` (C6.2.17)

> ⚠️ **这是 `SBFM` 的别名**。底层编码与 `SBFM` 相同，只是汇编器接受不同写法。


**语义**：Arithmetic Shift Right (immediate) shifts a register value right by an immediate number of bits, shifting in copies of the sign bit in the upper bits and zeros in the lower bits, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SBFM gives the operational pseudocode for this instruction.
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


*PDF 跨页*：p907-p909（共 3 页）



### 4.10 `ASRV` (C6.2.18)

> 💡 **被以下指令作为别名使用**：`ASR (register)`


**语义**：Arithmetic Shift Right Variable shifts a register value right by a variable number of bits, shifting in copies of its sign bit, and writes the result to the destination register. The remainder obtained by dividing the second source register by the data size defines the number of bits by which the first source register is right-shifted.


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


*PDF 跨页*：p909-p911（共 3 页）



### 4.11 `AT` (C6.2.19)

> ⚠️ **这是 `SYS` 的别名**。底层编码与 `SYS` 相同，只是汇编器接受不同写法。


**语义**：Address Translate. For more information, see op0==0b01, cache maintenance, TLB maintenance, and address translation instructions on page C5-399.


**汇编模板**：
```
AT <at_op>, <Xt>
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SYS gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<at_op>` | Is an AT instruction name, as listed for the AT system instruction group, encoded in the "op1:CRm<0>:op2" field. It can  |

| `<op1>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op1" field. |

| `<Cm>` | Is a name 'Cm', with 'm' in the range 0 to 15, encoded in the "CRm" field. |

| `<op2>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op2" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rt" field. 1 1 0 1 0 1 0 1 0 0 0 0 1 op1 0 1  |


</details>


*PDF 跨页*：p911-p913（共 3 页）



### 4.12 `ADCS` (C6.2.2)

**语义**：Add with Carry, setting flags, adds two register values and the Carry flag value, and writes the result to the destination register. It updates the condition flags based on the result.


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

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p878-p880（共 3 页）



### 4.13 `AUTDA, AUTDZA` (C6.2.20)

**语义**：Authenticate Data address, using key A. This instruction authenticates a data address, using a modifier and key A.


<details><summary>Operation 伪代码（点击展开）</summary>

```
if HavePACExt() then
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose source register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p913-p914（共 2 页）



### 4.14 `AUTDB, AUTDZB` (C6.2.21)

**语义**：Authenticate Data address, using key B. This instruction authenticates a data address, using a modifier and key B.


<details><summary>Operation 伪代码（点击展开）</summary>

```
if HavePACExt() then
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose source register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p914-p915（共 2 页）



### 4.15 `AUTIA, AUTIA1716, AUTIASP, AUTIAZ, AUTIZA` (C6.2.22)

**语义**：Authenticate Instruction address, using key A. This instruction authenticates an instruction address, using a modifier and key A.


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose source register or stack pointer, encoded in the "Rn" field. Operation for all |


</details>


*PDF 跨页*：p915-p917（共 3 页）



### 4.16 `AUTIB, AUTIB1716, AUTIBSP, AUTIBZ, AUTIZB` (C6.2.23)

**语义**：Authenticate Instruction address, using key B. This instruction authenticates an instruction address, using a modifier and key B.


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose source register or stack pointer, encoded in the "Rn" field. Operation for all |


</details>


*PDF 跨页*：p917-p919（共 3 页）



### 4.17 `AXFLAG` (C6.2.24)

**语义**：Convert floating-point condition flags from Arm to external format. This instruction converts the state of the PSTATE.{N,Z,C,V} flags from a form representing the result of an Arm floating-point scalar compare instruction to an alternative representation required by some software.


**汇编模板**：
```
AXFLAG
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveFlagFormatExt() then UNDEFINED;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bit Z = PSTATE.Z OR PSTATE.V;
```

</details>


*PDF 跨页*：p919-p920（共 2 页）



### 4.18 `BFC` (C6.2.27)

> ⚠️ **这是 `BFM` 的别名**。底层编码与 `BFM` 相同，只是汇编器接受不同写法。


**语义**：Bitfield Clear sets a bitfield of <width> bits at bit position <lsb> of the destination register to zero, leaving the other destination bits unchanged.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of BFM gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<lsb>` | For the 32-bit variant: is the bit number of the lsb of the destination bitfield, in the range 0 to 31. For the 64-bit v |

| `<width>` | For the 32-bit variant: is the width of the bitfield, in the range 1 to 32-<lsb>. For the 64-bit variant: is the width o |


</details>


*PDF 跨页*：p922-p924（共 3 页）



### 4.19 `BFI` (C6.2.28)

> ⚠️ **这是 `BFM` 的别名**。底层编码与 `BFM` 相同，只是汇编器接受不同写法。


**语义**：Bitfield Insert copies a bitfield of <width> bits from the least significant bits of the source register to bit position <lsb> of the destination register, leaving the other destination bits unchanged.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of BFM gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<lsb>` | For the 32-bit variant: is the bit number of the lsb of the destination bitfield, in the range 0 to 31. For the 64-bit v |

| `<width>` | For the 32-bit variant: is the width of the bitfield, in the range 1 to 32-<lsb>. For the 64-bit variant: is the width o |


</details>


*PDF 跨页*：p924-p926（共 3 页）



### 4.20 `BFM` (C6.2.29)

**语义**：Bitfield Move is usually accessed via one of its aliases, which are always preferred for disassembly.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) dst = X[d];
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<immr>` | For the 32-bit variant: is the right rotate amount, in the range 0 to 31, encoded in the "immr" field. For the 64-bit va |

| `<imms>` | For the 32-bit variant: is the leftmost bit number to be moved from the source, in the range 0 to 31, encoded in the "im |


</details>


*PDF 跨页*：p926-p928（共 3 页）



### 4.21 `ADD (extended register)` (C6.2.3)

**语义**：Add (extended register) adds a register value and a sign or zero-extended register value, followed by an optional left shift amount, and writes the result to the destination register. The argument that is extended from the <Rm> register can be a byte, halfword, word, or doubleword.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（7 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd|WSP>` | Is the 32-bit name of the destination general-purpose register or stack pointer, encoded in the "Rd" field. |

| `<Wn|WSP>` | Is the 32-bit name of the first source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd|SP>` | Is the 64-bit name of the destination general-purpose register or stack pointer, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the first source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<R>` | Is a width specifier, encoded in the "option" field. It can have the following values: W when option = 00x W when option |

| `<m>` | Is the number [0-30] of the second general-purpose source register or the name ZR (31), encoded in the "Rm" field. sf 0  |


</details>


*PDF 跨页*：p880-p883（共 4 页）



### 4.22 `BFXIL` (C6.2.30)

> ⚠️ **这是 `BFM` 的别名**。底层编码与 `BFM` 相同，只是汇编器接受不同写法。


**语义**：Bitfield Extract and Insert Low copies a bitfield of <width> bits starting from bit position <lsb> in the source register to the least significant bits of the destination register, leaving the other destination bits unchanged.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of BFM gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<lsb>` | For the 32-bit variant: is the bit number of the lsb of the source bitfield, in the range 0 to 31. For the 64-bit varian |

| `<width>` | For the 32-bit variant: is the width of the bitfield, in the range 1 to 32-<lsb>. For the 64-bit variant: is the width o |


</details>


*PDF 跨页*：p928-p930（共 3 页）



### 4.23 `BIC (shifted register)` (C6.2.31)

**语义**：Bitwise Bit Clear (shifted register) performs a bitwise AND of a register value and the complement of an optionally-shifted register value, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（8 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<shift>` | Is the optional shift to be applied to the final source, defaulting to LSL and encoded in the "shift" field. It can have |

| `<amount>` | For the 32-bit variant: is the shift amount, in the range 0 to 31, defaulting to 0 and encoded in the "imm6" field. For  |


</details>


*PDF 跨页*：p930-p932（共 3 页）



### 4.24 `BICS (shifted register)` (C6.2.32)

**语义**：Bitwise Bit Clear (shifted register), setting flags, performs a bitwise AND of a register value and the complement of an optionally-shifted register value, and writes the result to the destination register. It updates the condition flags based on the result.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（8 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<shift>` | Is the optional shift to be applied to the final source, defaulting to LSL and encoded in the "shift" field. It can have |

| `<amount>` | For the 32-bit variant: is the shift amount, in the range 0 to 31, defaulting to 0 and encoded in the "imm6" field. sf 1 |


</details>


*PDF 跨页*：p932-p934（共 3 页）



### 4.25 `BL` (C6.2.33)

**语义**：Branch with Link branches to a PC-relative offset, setting the register X30 to PC+4. It provides a hint that this is a subroutine call.


**汇编模板**：
```
BL <label>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
bits(64) offset = SignExtend(imm26:'00', 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
X[30] = PC[] + 4;
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<label>` | Is the program label to be unconditionally branched to. Its offset from the address of this instruction, in the range +/ |


</details>


*PDF 跨页*：p934-p935（共 2 页）



### 4.26 `BLR` (C6.2.34)

**语义**：Branch with Link to Register calls a subroutine at an address in a register, setting register X30 to PC+4.


**汇编模板**：
```
BLR <Xn>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) target = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xn>` | Is the 64-bit name of the general-purpose register holding the address to be branched to, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p935-p936（共 2 页）



### 4.27 `BLRAA, BLRAAZ, BLRAB, BLRABZ` (C6.2.35)

**语义**：Branch with Link to Register, with pointer authentication. This instruction authenticates the address in the general-purpose register that is specified by <Xn>, using a modifier and the specified key, and calls a subroutine at the authenticated address, setting register X30 to PC+4.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) target = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xn>` | Is the 64-bit name of the general-purpose register holding the address to be branched to, encoded in the "Rn" field. |

| `<Xm|SP>` | Is the 64-bit name of the general-purpose source register or stack pointer holding the modifier, encoded in the "Rm" fie |


</details>


*PDF 跨页*：p936-p938（共 3 页）



### 4.28 `BR` (C6.2.36)

**语义**：Branch to Register branches unconditionally to an address in a register, with a hint that this is not a subroutine return.


**汇编模板**：
```
BR <Xn>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) target = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xn>` | Is the 64-bit name of the general-purpose register holding the address to be branched to, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p938-p939（共 2 页）



### 4.29 `BRAA, BRAAZ, BRAB, BRABZ` (C6.2.37)

**语义**：Branch to Register, with pointer authentication. This instruction authenticates the address in the general-purpose register that is specified by <Xn>, using a modifier and the specified key, and branches to the authenticated address.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) target = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xn>` | Is the 64-bit name of the general-purpose register holding the address to be branched to, encoded in the "Rn" field. |

| `<Xm|SP>` | Is the 64-bit name of the general-purpose source register or stack pointer holding the modifier, encoded in the "Rm" fie |


</details>


*PDF 跨页*：p939-p941（共 3 页）



### 4.30 `BRK` (C6.2.38)

**语义**：Breakpoint instruction. A BRK instruction generates a Breakpoint Instruction exception. The PE records the exception in ESR_ELx, using the EC value 0x3c, and captures the value of the immediate argument in ESR_ELx.ISS.


**汇编模板**：
```
BRK #<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if HaveBTIExt() then 
     SetBTypeCompatible(TRUE);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
AArch64.SoftwareBreakpoint(imm16);
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<imm>` | Is a 16-bit unsigned immediate, in the range 0 to 65535, encoded in the "imm16" field. |


</details>


*PDF 跨页*：p941-p942（共 2 页）



### 4.31 `BTI` (C6.2.39)

**语义**：Branch Target Identification. A BTI instruction is used to guard against the execution of instructions which are not the intended target of a branch.


**汇编模板**：
```
BTI {<targets>}
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
SystemHintOp op; 
  
 if CRm:op2 == '0100 xx0' then 
     op = SystemHintOp_BTI; 
     // Check branch target compatibility between BTI instruction and PSTATE.BTYPE 
     SetBTypeCompatible(BTypeCompatible_BTI(op2<2:1>)); 
 else 
     EndOfInstruction();
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

| `<targets>` | Is the type of indirection, encoded in the "op2<2:1>" field. It can have the following values: (omitted) when op2<2:1> = |


</details>


*PDF 跨页*：p942-p944（共 3 页）



### 4.32 `ADD (immediate)` (C6.2.4)

> 💡 **被以下指令作为别名使用**：`MOV (to/from SP)`


**语义**：Add (immediate) adds a register value and an optionally-shifted immediate value, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd|WSP>` | Is the 32-bit name of the destination general-purpose register or stack pointer, encoded in the "Rd" field. |

| `<Wn|WSP>` | Is the 32-bit name of the source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<Xd|SP>` | Is the 64-bit name of the destination general-purpose register or stack pointer, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<imm>` | Is an unsigned immediate, in the range 0 to 4095, encoded in the "imm12" field. Alias is preferred when MOV (to/from SP) |


</details>


*PDF 跨页*：p883-p885（共 3 页）



### 4.33 `CASB, CASAB, CASALB, CASLB` (C6.2.40)

**语义**：Compare and Swap byte in memory reads an 8-bit byte from memory, and compares it against the value held in a first register. If the comparison is equal, the value in a second register is written to memory. If the write is performed, the read and write occur atomically such that no other modification of the memory location can take place between the read and write.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register to be compared and loaded, encoded in the "Rs" field. |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be conditionally stored, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p944-p946（共 3 页）



### 4.34 `CASH, CASAH, CASALH, CASLH` (C6.2.41)

**语义**：Compare and Swap halfword in memory reads a 16-bit halfword from memory, and compares it against the value held in a first register. If the comparison is equal, the value in a second register is written to memory. If the write is performed, the read and write occur atomically such that no other modification of the memory location can take place between the read and write.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register to be compared and loaded, encoded in the "Rs" field. |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be conditionally stored, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p946-p948（共 3 页）



### 4.35 `CASP, CASPA, CASPAL, CASPL` (C6.2.42)

**语义**：Compare and Swap Pair of words or doublewords in memory reads a pair of 32-bit words or 64-bit doublewords from memory, and compares them against the values held in the first pair of registers. If the comparison is equal, the values in the second pair of registers are written to memory. If the writes are performed, the reads and writes occur atomically such that no other modification of the memory location can take place between the reads and writes.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（9 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the first general-purpose register to be compared and loaded, encoded in the "Rs" field. <Ws> must |

| `<W(s+1)>` | Is the 32-bit name of the second general-purpose register to be compared and loaded. |

| `<Wt>` | Is the 32-bit name of the first general-purpose register to be conditionally stored, encoded in the "Rt" field. <Wt> mus |

| `<W(t+1)>` | Is the 32-bit name of the second general-purpose register to be conditionally stored. |

| `<Xs>` | Is the 64-bit name of the first general-purpose register to be compared and loaded, encoded in the "Rs" field. <Xs> must |

| `<X(s+1)>` | Is the 64-bit name of the second general-purpose register to be compared and loaded. |

| `<Xt>` | Is the 64-bit name of the first general-purpose register to be conditionally stored, encoded in the "Rt" field. <Xt> mus |

| `<X(t+1)>` | Is the 64-bit name of the second general-purpose register to be conditionally stored. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p948-p951（共 4 页）



### 4.36 `CAS, CASA, CASAL, CASL` (C6.2.43)

**语义**：Compare and Swap word or doubleword in memory reads a 32-bit word or 64-bit doubleword from memory, and compares it against the value held in a first register. If the comparison is equal, the value in a second register is written to memory. If the write is performed, the read and write occur atomically such that no other modification of the memory location can take place between the read and write.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register to be compared and loaded, encoded in the "Rs" field. |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be conditionally stored, encoded in the "Rt" field. |

| `<Xs>` | Is the 64-bit name of the general-purpose register to be compared and loaded, encoded in the "Rs" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be conditionally stored, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p951-p954（共 4 页）



### 4.37 `CBNZ` (C6.2.44)

**语义**：Compare and Branch on Nonzero compares the value in a register with zero, and conditionally branches to a label at a PC-relative offset if the comparison is not equal. It provides a hint that this is not a subroutine call or return.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand1 = X[t];
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be tested, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be tested, encoded in the "Rt" field. |

| `<label>` | Is the program label to be conditionally branched to. Its offset from the address of this instruction, in the range +/-1 |


</details>


*PDF 跨页*：p954-p955（共 2 页）



### 4.38 `CBZ` (C6.2.45)

**语义**：Compare and Branch on Zero compares the value in a register with zero, and conditionally branches to a label at a PC-relative offset if the comparison is equal. It provides a hint that this is not a subroutine call or return. This instruction does not affect condition flags.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand1 = X[t];
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be tested, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be tested, encoded in the "Rt" field. |

| `<label>` | Is the program label to be conditionally branched to. Its offset from the address of this instruction, in the range +/-1 |


</details>


*PDF 跨页*：p955-p956（共 2 页）



### 4.39 `CCMN (immediate)` (C6.2.46)

**语义**：Conditional Compare Negative (immediate) sets the value of the condition flags to the result of the comparison of a register value and a negated immediate value if the condition is TRUE, and an immediate value otherwise.


<details><summary>Operation 伪代码（点击展开）</summary>

```
if ConditionHolds(cond) then
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<imm>` | Is a five bit unsigned (positive) immediate encoded in the "imm5" field. |

| `<nzcv>` | Is the flag bit specifier, an immediate in the range 0 to 15, giving the alternative state for the 4-bit NZCV condition  |

| `<cond>` | Is one of the standard conditions, encoded in the "cond" field in the standard way. |


</details>


*PDF 跨页*：p956-p958（共 3 页）



### 4.40 `CCMN (register)` (C6.2.47)

**语义**：Conditional Compare Negative (register) sets the value of the condition flags to the result of the comparison of a register value and the inverse of another register value if the condition is TRUE, and an immediate value otherwise.


<details><summary>Operation 伪代码（点击展开）</summary>

```
if ConditionHolds(cond) then
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<nzcv>` | Is the flag bit specifier, an immediate in the range 0 to 15, giving the alternative state for the 4-bit NZCV condition  |

| `<cond>` | Is one of the standard conditions, encoded in the "cond" field in the standard way. |


</details>


*PDF 跨页*：p958-p960（共 3 页）



### 4.41 `CCMP (immediate)` (C6.2.48)

**语义**：Conditional Compare (immediate) sets the value of the condition flags to the result of the comparison of a register value and an immediate value if the condition is TRUE, and an immediate value otherwise.


<details><summary>Operation 伪代码（点击展开）</summary>

```
if ConditionHolds(cond) then
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<imm>` | Is a five bit unsigned (positive) immediate encoded in the "imm5" field. |

| `<nzcv>` | Is the flag bit specifier, an immediate in the range 0 to 15, giving the alternative state for the 4-bit NZCV condition  |

| `<cond>` | Is one of the standard conditions, encoded in the "cond" field in the standard way. |


</details>


*PDF 跨页*：p960-p962（共 3 页）



### 4.42 `CCMP (register)` (C6.2.49)

**语义**：Conditional Compare (register) sets the value of the condition flags to the result of the comparison of two registers Applies when sf == 0.


<details><summary>Operation 伪代码（点击展开）</summary>

```
if ConditionHolds(cond) then
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<nzcv>` | Is the flag bit specifier, an immediate in the range 0 to 15, giving the alternative state for the 4-bit NZCV condition  |

| `<cond>` | Is one of the standard conditions, encoded in the "cond" field in the standard way. |


</details>


*PDF 跨页*：p962-p964（共 3 页）



### 4.43 `ADD (shifted register)` (C6.2.5)

**语义**：Add (shifted register) adds a register value and an optionally-shifted register value, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（8 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<shift>` | Is the optional shift type to be applied to the second source operand, defaulting to LSL and encoded in the "shift" fiel |

| `<amount>` | For the 32-bit variant: is the shift amount, in the range 0 to 31, defaulting to 0 and encoded in the "imm6" field. sf 0 |


</details>


*PDF 跨页*：p885-p887（共 3 页）



### 4.44 `CFINV` (C6.2.50)

**语义**：Invert Carry Flag. This instruction inverts the value of the PSTATE.C flag.


**汇编模板**：
```
CFINV
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveFlagManipulateExt() then UNDEFINED;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
PSTATE.C = NOT(PSTATE.C);
```

</details>


*PDF 跨页*：p964-p965（共 2 页）



### 4.45 `CFP` (C6.2.51)

> ⚠️ **这是 `SYS` 的别名**。底层编码与 `SYS` 相同，只是汇编器接受不同写法。


**语义**：Control Flow Prediction Restriction by Context prevents control flow predictions that predict execution addresses based on information gathered from earlier execution within a particular execution context. Control flow predictions determined by the actions of code in the target execution context or contexts appearing in program order before the instruction cannot be used to exploitatively control speculative execution occurring after the instruction is complete and synchronized.


**汇编模板**：
```
CFP RCTX, <Xt>
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SYS gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rt" field. |


</details>


*PDF 跨页*：p965-p966（共 2 页）



### 4.46 `CINC` (C6.2.52)

> ⚠️ **这是 `CSINC` 的别名**。底层编码与 `CSINC` 相同，只是汇编器接受不同写法。


**语义**：Conditional Increment returns, in the destination register, the value of the source register incremented by 1 if the condition is TRUE, and otherwise returns the value of the source register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of CSINC gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" and "Rm" fields. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" and "Rm" fields. |

| `<cond>` | Is one of the standard conditions, excluding AL and NV, encoded in the "cond" field with its least significant bit inver |


</details>


*PDF 跨页*：p966-p968（共 3 页）



### 4.47 `CINV` (C6.2.53)

> ⚠️ **这是 `CSINV` 的别名**。底层编码与 `CSINV` 相同，只是汇编器接受不同写法。


**语义**：Conditional Invert returns, in the destination register, the bitwise inversion of the value of the source register if the condition is TRUE, and otherwise returns the value of the source register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of CSINV gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" and "Rm" fields. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" and "Rm" fields. |

| `<cond>` | Is one of the standard conditions, excluding AL and NV, encoded in the "cond" field with its least significant bit inver |


</details>


*PDF 跨页*：p968-p970（共 3 页）



### 4.48 `CLREX` (C6.2.54)

**语义**：Clear Exclusive clears the local monitor of the executing PE.


**汇编模板**：
```
CLREX {#<imm>}
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// CRm field is ignored
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
ClearExclusiveLocal(ProcessorID());
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<imm>` | Is an optional 4-bit unsigned immediate, in the range 0 to 15, defaulting to 15 and encoded in the "CRm" field. |


</details>


*PDF 跨页*：p970-p971（共 2 页）



### 4.49 `CLS` (C6.2.55)

**语义**：Count Leading Sign bits counts the number of leading bits of the source register that have the same value as the most significant bit of the register, and writes the result to the destination register. This count does not include the most significant bit of the source register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
integer result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p971-p973（共 3 页）



### 4.50 `CLZ` (C6.2.56)

**语义**：Count Leading Zeros counts the number of binary zero bits before the first binary one bit in the value of the source register, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
integer result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p973-p974（共 2 页）



### 4.51 `CMN (extended register)` (C6.2.57)

> ⚠️ **这是 `ADDS (extended register)` 的别名**。底层编码与 `ADDS (extended register)` 相同，只是汇编器接受不同写法。


**语义**：Compare Negative (extended register) adds a register value and a sign or zero-extended register value, followed by an optional left shift amount. The argument that is extended from the <Rm> register can be a byte, halfword, word, or doubleword. It updates the condition flags based on the result, and discards the result.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of ADDS (extended register) gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wn|WSP>` | Is the 32-bit name of the first source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xn|SP>` | Is the 64-bit name of the first source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<R>` | Is a width specifier, encoded in the "option" field. It can have the following values: W when option = 00x W when option |

| `<m>` | Is the number [0-30] of the second general-purpose source register or the name ZR (31), encoded in the "Rm" field. sf 0  |


</details>


*PDF 跨页*：p974-p976（共 3 页）



### 4.52 `CMN (immediate)` (C6.2.58)

> ⚠️ **这是 `ADDS (immediate)` 的别名**。底层编码与 `ADDS (immediate)` 相同，只是汇编器接受不同写法。


**语义**：Compare Negative (immediate) adds a register value and an optionally-shifted immediate value. It updates the condition flags based on the result, and discards the result.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of ADDS (immediate) gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wn|WSP>` | Is the 32-bit name of the source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<Xn|SP>` | Is the 64-bit name of the source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<imm>` | Is an unsigned immediate, in the range 0 to 4095, encoded in the "imm12" field. |

| `<shift>` | Is the optional left shift to apply to the immediate, defaulting to LSL #0 and encoded in the "sh" field. It can have th |


</details>


*PDF 跨页*：p976-p978（共 3 页）



### 4.53 `CMN (shifted register)` (C6.2.59)

> ⚠️ **这是 `ADDS (shifted register)` 的别名**。底层编码与 `ADDS (shifted register)` 相同，只是汇编器接受不同写法。


**语义**：Compare Negative (shifted register) adds a register value and an optionally-shifted register value. It updates the condition flags based on the result, and discards the result.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of ADDS (shifted register) gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<shift>` | Is the optional shift type to be applied to the second source operand, defaulting to LSL and encoded in the "shift" fiel |

| `<amount>` | For the 32-bit variant: is the shift amount, in the range 0 to 31, defaulting to 0 and encoded in the "imm6" field. For  |


</details>


*PDF 跨页*：p978-p980（共 3 页）



### 4.54 `ADDG` (C6.2.6)

**语义**：Add with Tag adds an immediate value scaled by the Tag granule to the address in the source register, modifies the Logical Address Tag of the address using an immediate value, and writes the result to the destination register. Tags specified in GCR_EL1.Exclude are excluded from the possible outputs when modifying the Logical Address Tag.


**汇编模板**：
```
ADDG <Xd|SP>, <Xn|SP>, #<uimm6>, #<uimm4>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveMTEExt() then UNDEFINED; 
 integer d = UInt(Xd); 
 integer n = UInt(Xn); 
 bits(64) offset = LSL(ZeroExtend(uimm6, 64), LOG2_TAG_GRANULE);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) operand1 = if n == 31 then SP[] else X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd|SP>` | Is the 64-bit name of the destination general-purpose register or stack pointer, encoded in the "Xd" field. |

| `<Xn|SP>` | Is the 64-bit name of the source general-purpose register or stack pointer, encoded in the "Xn" field. |

| `<uimm6>` | Is an unsigned immediate, a multiple of 16 in the range 0 to 1008, encoded in the "uimm6" field. |

| `<uimm4>` | Is an unsigned immediate, in the range 0 to 15, encoded in the "uimm4" field. |


</details>


*PDF 跨页*：p887-p888（共 2 页）



### 4.55 `CMP (extended register)` (C6.2.60)

> ⚠️ **这是 `SUBS (extended register)` 的别名**。底层编码与 `SUBS (extended register)` 相同，只是汇编器接受不同写法。


**语义**：Compare (extended register) subtracts a sign or zero-extended register value, followed by an optional left shift amount, from a register value. The argument that is extended from the <Rm> register can be a byte, halfword, word, or doubleword. It updates the condition flags based on the result, and discards the result.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SUBS (extended register) gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wn|WSP>` | Is the 32-bit name of the first source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xn|SP>` | Is the 64-bit name of the first source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<R>` | Is a width specifier, encoded in the "option" field. It can have the following values: W when option = 00x W when option |

| `<m>` | Is the number [0-30] of the second general-purpose source register or the name ZR (31), encoded in the "Rm" field. sf 1  |


</details>


*PDF 跨页*：p980-p982（共 3 页）



### 4.56 `CMP (immediate)` (C6.2.61)

> ⚠️ **这是 `SUBS (immediate)` 的别名**。底层编码与 `SUBS (immediate)` 相同，只是汇编器接受不同写法。


**语义**：Compare (immediate) subtracts an optionally-shifted immediate value from a register value. It updates the condition flags based on the result, and discards the result.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SUBS (immediate) gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wn|WSP>` | Is the 32-bit name of the source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<Xn|SP>` | Is the 64-bit name of the source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<imm>` | Is an unsigned immediate, in the range 0 to 4095, encoded in the "imm12" field. |

| `<shift>` | Is the optional left shift to apply to the immediate, defaulting to LSL #0 and encoded in the "sh" field. It can have th |


</details>


*PDF 跨页*：p982-p984（共 3 页）



### 4.57 `CMP (shifted register)` (C6.2.62)

> ⚠️ **这是 `SUBS (shifted register)` 的别名**。底层编码与 `SUBS (shifted register)` 相同，只是汇编器接受不同写法。


**语义**：Compare (shifted register) subtracts an optionally-shifted register value from a register value. It updates the condition flags based on the result, and discards the result.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SUBS (shifted register) gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<shift>` | Is the optional shift type to be applied to the second source operand, defaulting to LSL and encoded in the "shift" fiel |

| `<amount>` | For the 32-bit variant: is the shift amount, in the range 0 to 31, defaulting to 0 and encoded in the "imm6" field. For  |


</details>


*PDF 跨页*：p984-p986（共 3 页）



### 4.58 `CMPP` (C6.2.63)

> ⚠️ **这是 `SUBPS` 的别名**。底层编码与 `SUBPS` 相同，只是汇编器接受不同写法。


**语义**：Compare with Tag subtracts the 56-bit address held in the second source register from the 56-bit address held in the first source register, updates the condition flags based on the result of the subtraction, and discards the result.


**汇编模板**：
```
CMPP <Xn|SP>, <Xm|SP>
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SUBPS gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xn|SP>` | Is the 64-bit name of the first source general-purpose register or stack pointer, encoded in the "Xn" field. |

| `<Xm|SP>` | Is the 64-bit name of the second general-purpose source register or stack pointer, encoded in the "Xm" field. |


</details>


*PDF 跨页*：p986-p987（共 2 页）



### 4.59 `CNEG` (C6.2.64)

> ⚠️ **这是 `CSNEG` 的别名**。底层编码与 `CSNEG` 相同，只是汇编器接受不同写法。


**语义**：Conditional Negate returns, in the destination register, the negated value of the source register if the condition is TRUE, and otherwise returns the value of the source register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of CSNEG gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" and "Rm" fields. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" and "Rm" fields. |

| `<cond>` | Is one of the standard conditions, excluding AL and NV, encoded in the "cond" field with its least significant bit inver |


</details>


*PDF 跨页*：p987-p989（共 3 页）



### 4.60 `CPP` (C6.2.65)

> ⚠️ **这是 `SYS` 的别名**。底层编码与 `SYS` 相同，只是汇编器接受不同写法。


**语义**：Cache Prefetch Prediction Restriction by Context prevents cache allocation predictions that predict execution addresses based on information gathered from earlier execution within a particular execution context. Cache allocation predictions determined by the actions of code in the target execution context or contexts appearing in program order before the instruction cannot be used to exploitatively control speculative execution occurring after the instruction is complete and synchronized.


**汇编模板**：
```
CPP RCTX, <Xt>
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SYS gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rt" field. |


</details>


*PDF 跨页*：p989-p990（共 2 页）



### 4.61 `CRC32B, CRC32H, CRC32W, CRC32X` (C6.2.66)

**语义**：CRC32 checksum performs a cyclic redundancy check (CRC) calculation on a value held in a general-purpose register. It takes an input CRC value in the first source operand, performs a CRC on the input value in the second source operand, and returns the output CRC value. The second source operand can be 8, 16, 32, or 64 bits. To align with common usage, the bit order of the values is reversed as part of the operation, and the polynomial 0x04C11DB7 is used for the CRC calculation.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(32) acc = X[n];    // accumulator
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose accumulator output register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose accumulator input register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the general-purpose data source register, encoded in the "Rm" field. sf 0 0 1 1 0 1 0 1 1 0 Rm 0 1 |


</details>


*PDF 跨页*：p990-p992（共 3 页）



### 4.62 `CRC32CB, CRC32CH, CRC32CW, CRC32CX` (C6.2.67)

**语义**：CRC32 checksum performs a cyclic redundancy check (CRC) calculation on a value held in a general-purpose register. It takes an input CRC value in the first source operand, performs a CRC on the input value in the second source operand, and returns the output CRC value. The second source operand can be 8, 16, 32, or 64 bits. To align with common usage, the bit order of the values is reversed as part of the operation, and the polynomial 0x1EDC6F41 is used for the CRC calculation.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(32) acc = X[n];    // accumulator
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose accumulator output register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose accumulator input register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the general-purpose data source register, encoded in the "Rm" field. sf 0 0 1 1 0 1 0 1 1 0 Rm 0 1 |


</details>


*PDF 跨页*：p992-p994（共 3 页）



### 4.63 `CSDB` (C6.2.68)

**语义**：Consumption of Speculative Data Barrier is a memory barrier that controls speculative execution and data value prediction.


**汇编模板**：
```
CSDB
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
ConsumptionOfSpeculativeDataBarrier();
```

</details>


*PDF 跨页*：p994-p995（共 2 页）



### 4.64 `CSEL` (C6.2.69)

**语义**：If the condition is true, Conditional Select writes the value of the first source register to the destination register. If the condition is false, it writes the value of the second source register to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
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

| `<cond>` | Is one of the standard conditions, encoded in the "cond" field in the standard way. |


</details>


*PDF 跨页*：p995-p997（共 3 页）



### 4.65 `ADDS (extended register)` (C6.2.7)

> 💡 **被以下指令作为别名使用**：`CMN (extended register)`


**语义**：Add (extended register), setting flags, adds a register value and a sign or zero-extended register value, followed by an optional left shift amount, and writes the result to the destination register. The argument that is extended from the <Rm> register can be a byte, halfword, word, or doubleword. It updates the condition flags based on the result.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn|WSP>` | Is the 32-bit name of the first source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the first source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<R>` | Is a width specifier, encoded in the "option" field. It can have the following values: W when option = 00x Alias is pref |


</details>


*PDF 跨页*：p888-p891（共 4 页）



### 4.66 `CSET` (C6.2.70)

> ⚠️ **这是 `CSINC` 的别名**。底层编码与 `CSINC` 相同，只是汇编器接受不同写法。


**语义**：Conditional Set sets the destination register to 1 if the condition is TRUE, and otherwise sets it to 0.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of CSINC gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<cond>` | Is one of the standard conditions, excluding AL and NV, encoded in the "cond" field with its least significant bit inver |


</details>


*PDF 跨页*：p997-p999（共 3 页）



### 4.67 `CSETM` (C6.2.71)

> ⚠️ **这是 `CSINV` 的别名**。底层编码与 `CSINV` 相同，只是汇编器接受不同写法。


**语义**：Conditional Set Mask sets all bits of the destination register to 1 if the condition is TRUE, and otherwise sets all bits to 0.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of CSINV gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<cond>` | Is one of the standard conditions, excluding AL and NV, encoded in the "cond" field with its least significant bit inver |


</details>


*PDF 跨页*：p999-p1001（共 3 页）



### 4.68 `CSINC` (C6.2.72)

**语义**：Conditional Select Increment returns, in the destination register, the value of the first source register if the condition is TRUE, and otherwise returns the value of the second source register incremented by 1.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
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

| `<cond>` | Is one of the standard conditions, encoded in the "cond" field in the standard way. Alias is preferred when CINC Rm != ' |


</details>


*PDF 跨页*：p1001-p1003（共 3 页）



### 4.69 `CSINV` (C6.2.73)

**语义**：Conditional Select Invert returns, in the destination register, the value of the first source register if the condition is TRUE, and otherwise returns the bitwise inversion value of the second source register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
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

| `<cond>` | Is one of the standard conditions, encoded in the "cond" field in the standard way. Alias is preferred when CINV Rm != ' |


</details>


*PDF 跨页*：p1003-p1005（共 3 页）



### 4.70 `CSNEG` (C6.2.74)

> 💡 **被以下指令作为别名使用**：`CNEG`


**语义**：Conditional Select Negation returns, in the destination register, the value of the first source register if the condition is TRUE, and otherwise returns the negated value of the second source register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
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

| `<cond>` | Is one of the standard conditions, encoded in the "cond" field in the standard way. |


</details>


*PDF 跨页*：p1005-p1007（共 3 页）



### 4.71 `DC` (C6.2.75)

> ⚠️ **这是 `SYS` 的别名**。底层编码与 `SYS` 相同，只是汇编器接受不同写法。


**语义**：Data Cache operation. For more information, see op0==0b01, cache maintenance, TLB maintenance, and address translation instructions on page C5-399.


**汇编模板**：
```
DC <dc_op>, <Xt>
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SYS gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<dc_op>` | Is a DC instruction name, as listed for the DC system instruction group, encoded in the "op1:CRm:op2" field. It can have |


</details>


*PDF 跨页*：p1007-p1009（共 3 页）



### 4.72 `DCPS1` (C6.2.76)

**语义**：Debug Change PE State to EL1, when executed in Debug state: If executed at EL0 changes the current Exception level and SP to EL1 using SP_EL1.


**汇编模板**：
```
DCPS1 {#<imm>}
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !Halted() then UNDEFINED;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
DCPSInstruction(LL);
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<imm>` | Is an optional 16-bit unsigned immediate, in the range 0 to 65535, defaulting to 0 and encoded in the "imm16" field. |


</details>


*PDF 跨页*：p1009-p1010（共 2 页）



### 4.73 `DCPS2` (C6.2.77)

**语义**：Debug Change PE State to EL2, when executed in Debug state: If executed at EL0 or EL1 changes the current Exception level and SP to EL2 using SP_EL2.


**汇编模板**：
```
DCPS2 {#<imm>}
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !Halted() then UNDEFINED;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
DCPSInstruction(LL);
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<imm>` | Is an optional 16-bit unsigned immediate, in the range 0 to 65535, defaulting to 0 and encoded in the "imm16" field. |


</details>


*PDF 跨页*：p1010-p1011（共 2 页）



### 4.74 `DCPS3` (C6.2.78)

**语义**：Debug Change PE State to EL3, when executed in Debug state: If executed at EL3 selects SP_EL3.


**汇编模板**：
```
DCPS3 {#<imm>}
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !Halted() then UNDEFINED;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
DCPSInstruction(LL);
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<imm>` | Is an optional 16-bit unsigned immediate, in the range 0 to 65535, defaulting to 0 and encoded in the "imm16" field. |


</details>


*PDF 跨页*：p1011-p1012（共 2 页）



### 4.75 `DGH` (C6.2.79)

**语义**：DGH is a hint instruction. A DGH instruction is not expected to be performance optimal to merge memory accesses with Normal Non-cacheable or Device-GRE attributes appearing in program order before the hint instruction with any memory accesses appearing after the hint instruction into a single memory transaction on an interconnect.


**汇编模板**：
```
DGH
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveDGHExt() then EndOfInstruction();
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
Hint_DGH();
```

</details>


*PDF 跨页*：p1012-p1013（共 2 页）



### 4.76 `ADDS (immediate)` (C6.2.8)

> 💡 **被以下指令作为别名使用**：`CMN (immediate)`


**语义**：Add (immediate), setting flags, adds a register value and an optionally-shifted immediate value, and writes the result to the destination register. It updates the condition flags based on the result.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn|WSP>` | Is the 32-bit name of the source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<imm>` | Is an unsigned immediate, in the range 0 to 4095, encoded in the "imm12" field. |

| `<shift>` | Is the optional left shift to apply to the immediate, defaulting to LSL #0 and encoded in the "sh" field. It can have th |


</details>


*PDF 跨页*：p891-p893（共 3 页）



### 4.77 `DMB` (C6.2.80)

**语义**：Data Memory Barrier is a memory barrier that ensures the ordering of observations of memory accesses, see Data Memory Barrier (DMB) on page B2-147.


**汇编模板**：
```
DMB <option>|#<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
case CRm<3:2> of 
     when '00' domain = MBReqDomain_OuterShareable; 
     when '01' domain = MBReqDomain_Nonshareable; 
     when '10' domain = MBReqDomain_InnerShareable; 
     when '11' domain = MBReqDomain_FullSystem; 
 case CRm<1:0> of 
     when '00' types = MBReqTypes_All; domain = MBReqDomain_FullSystem; 
     when '01' types = MBReqTypes_Reads; 
     when '10' types = MBReqTypes_Writes; 
     when '11' types = MBReqTypes_All;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
DataMemoryBarrier(domain, types);
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<option>` | Specifies the limitation on the barrier operation. Values are: SY Full system is the required shareability domain, reads |


</details>


*PDF 跨页*：p1013-p1015（共 3 页）



### 4.78 `DRPS` (C6.2.81)


**汇编模板**：
```
DRPS
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !Halted() || PSTATE.EL == EL0 then UNDEFINED;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
DRPSInstruction();
```

</details>


*PDF 跨页*：p1015-p1016（共 2 页）



### 4.79 `DSB` (C6.2.82)

**语义**：Data Synchronization Barrier is a memory barrier that ensures the completion of memory accesses, see Data Synchronization Barrier (DSB) on page B2-150.


**汇编模板**：
```
DSB <option>|#<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
boolean nXS = FALSE; 
  
 case CRm of 
     when '0000' alias = DSBAlias_SSBB; 
     when '0100' alias = DSBAlias_PSSBB; 
     otherwise alias = DSBAlias_DSB; 
  
 case CRm<3:2> of 
     when '00' domain = MBReqDomain_OuterShareable; 
     when '01' domain = MBReqDomain_Nonshareable; 
     when '10' domain = MBReqDomain_InnerShareable; 
     when '11' domain = MBReqDomain_FullSystem; 
 case CRm<1:0> of 
     when '00' types = MBReqTypes_All; domain = MBReqDomain_FullSystem; 
     when '01' types = MBReqTypes_Reads; 
     when '10' types = MBReqTypes_Writes; 
     when '11' types = MBReqTypes_All; 
Memory nXS barrier
(FEAT_XS)
Encoding
DSB <option>nXS|#<imm>
Decode for this encoding
 if !HaveFeatXS() then UNDEFINED; 
 MBReqTypes types = MBReqTypes_All; 
 boolean nXS = TRUE; 
 DSBAlias alias = DSBAlias_DSB; 
  
 case imm2 of 
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
1
CRm
1
0
0
1
1
1
1
1
31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11
8
7
6
5
4
3
2
1
0
opc
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
1 imm2 1
0
0
0
1
1
1
1
1
1
31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9
8
7
6
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
C6-1017
ID072021
Non-Confidential
     when '00' domain = MBReqDomain_OuterShareable; 
     when '01' domain = MBReqDomain_Nonshareable; 
     when '10' domain = MBReqDomain_InnerShareable; 
     when '11' domain = MBReqDomain_FullSystem; 
Alias conditions
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<option>` | For the memory barrier variant: specifies the limitation on the barrier operation. Values are: SY Full system is the req |


</details>


*PDF 跨页*：p1016-p1019（共 4 页）



### 4.80 `DVP` (C6.2.83)

> ⚠️ **这是 `SYS` 的别名**。底层编码与 `SYS` 相同，只是汇编器接受不同写法。


**语义**：Data Value Prediction Restriction by Context prevents data value predictions that predict execution addresses based on information gathered from earlier execution within a particular execution context. Data value predictions determined by the actions of code in the target execution context or contexts appearing in program order before the instruction cannot be used to exploitatively control speculative execution occurring after the instruction is complete and synchronized.


**汇编模板**：
```
DVP RCTX, <Xt>
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SYS gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rt" field. |


</details>


*PDF 跨页*：p1019-p1020（共 2 页）



### 4.81 `EON (shifted register)` (C6.2.84)

**语义**：Bitwise Exclusive OR NOT (shifted register) performs a bitwise Exclusive OR NOT of a register value and an optionally-shifted register value, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（8 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<shift>` | Is the optional shift to be applied to the final source, defaulting to LSL and encoded in the "shift" field. It can have |

| `<amount>` | For the 32-bit variant: is the shift amount, in the range 0 to 31, defaulting to 0 and encoded in the "imm6" field. For  |


</details>


*PDF 跨页*：p1020-p1022（共 3 页）



### 4.82 `EOR (immediate)` (C6.2.85)

**语义**：Bitwise Exclusive OR (immediate) performs a bitwise Exclusive OR of a register value and an immediate value, and writes the result to the destination register.


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


*PDF 跨页*：p1022-p1024（共 3 页）



### 4.83 `EOR (shifted register)` (C6.2.86)

**语义**：Bitwise Exclusive OR (shifted register) performs a bitwise Exclusive OR of a register value and an optionally-shifted register value, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（8 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<shift>` | Is the optional shift to be applied to the final source, defaulting to LSL and encoded in the "shift" field. It can have |

| `<amount>` | For the 32-bit variant: is the shift amount, in the range 0 to 31, defaulting to 0 and encoded in the "imm6" field. For  |


</details>


*PDF 跨页*：p1024-p1026（共 3 页）



### 4.84 `ERET` (C6.2.87)

**语义**：Exception Return using the ELR and SPSR for the current Exception level. When executed, the PE restores PSTATE from the SPSR, and branches to the address held in the ELR.


**汇编模板**：
```
ERET
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if PSTATE.EL == EL0 then UNDEFINED;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
AArch64.CheckForERetTrap(FALSE, TRUE);
```

</details>


*PDF 跨页*：p1026-p1027（共 2 页）



### 4.85 `ERETAA, ERETAB` (C6.2.88)

**语义**：Exception Return, with pointer authentication. This instruction authenticates the address in ELR, using SP as the modifier and the specified key, the PE restores PSTATE from the SPSR for the current Exception level, and branches to the authenticated address.


<details><summary>Operation 伪代码（点击展开）</summary>

```
AArch64.CheckForERetTrap(TRUE, use_key_a);
```

</details>


*PDF 跨页*：p1027-p1028（共 2 页）



### 4.86 `ESB` (C6.2.89)

**语义**：Error Synchronization Barrier is an error synchronization event that might also update DISR_EL1 and VDISR_EL2.


**汇编模板**：
```
ESB
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveRASExt() then EndOfInstruction();
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
SynchronizeErrors();
```

</details>


*PDF 跨页*：p1028-p1029（共 2 页）



### 4.87 `ADDS (shifted register)` (C6.2.9)

> 💡 **被以下指令作为别名使用**：`CMN (shifted register)`


**语义**：Add (shifted register), setting flags, adds a register value and an optionally-shifted register value, and writes the result to the destination register. It updates the condition flags based on the result.


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

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. Alias is preferred when CMN |


</details>


*PDF 跨页*：p893-p895（共 3 页）



### 4.88 `EXTR` (C6.2.90)

> 💡 **被以下指令作为别名使用**：`ROR (immediate)`


**语义**：Extract register extracts a register from a pair of registers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
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

| `<lsb>` | For the 32-bit variant: is the least significant bit position from which to extract, in the range 0 to 31, encoded in th |


</details>


*PDF 跨页*：p1029-p1031（共 3 页）



### 4.89 `GMI` (C6.2.91)

**语义**：Tag Mask Insert inserts the tag in the first source register into the excluded set specified in the second source register, writing the new excluded set to the destination register.


**汇编模板**：
```
GMI <Xd>, <Xn|SP>, <Xm>
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
bits(64) address = if n == 31 then SP[] else X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Xd" field. |

| `<Xn|SP>` | Is the 64-bit name of the first source general-purpose register or stack pointer, encoded in the "Xn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Xm" field. |


</details>


*PDF 跨页*：p1031-p1032（共 2 页）




---

📌 **下一步**：回到 [`a64_base_overview.md`](./a64_base_overview.md) 看其他首字母，或 [`isa_reference/README.md`](./README.md) 看其他扩展。
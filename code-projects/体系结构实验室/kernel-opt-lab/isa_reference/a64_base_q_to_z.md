# A64_BASE — 指令首字母 Q-Z 部分

> **生成日期**：2026-06-29  
> **PDF 源版本**：ARM DDI 0487G.b (2021-07)

> a64_base_overview.md`](./a64_base_overview.md) 的拆分之一（按助记符首字母）。
> 含 135 条指令详解。

---

## 目录

- 4.133 `RBIT` (C6.2.219)
- 4.135 `RET` (C6.2.220)
- 4.136 `RETAA, RETAB` (C6.2.221)
- 4.137 `REV` (C6.2.222)
- 4.138 `REV16` (C6.2.223)
- 4.139 `REV32` (C6.2.224)
- 4.140 `REV64` (C6.2.225)
- 4.141 `RMIF` (C6.2.226)
- 4.142 `ROR (immediate)` (C6.2.227)
- 4.143 `ROR (register)` (C6.2.228)
- 4.144 `RORV` (C6.2.229)
- 4.146 `SB` (C6.2.230)
- 4.147 `SBC` (C6.2.231)
- 4.148 `SBCS` (C6.2.232)
- 4.149 `SBFIZ` (C6.2.233)
- 4.150 `SBFM` (C6.2.234)
- 4.151 `SBFX` (C6.2.235)
- 4.152 `SDIV` (C6.2.236)
- 4.153 `SETF8, SETF16` (C6.2.237)
- 4.154 `SEV` (C6.2.238)
- 4.155 `SEVL` (C6.2.239)
- 4.157 `SMADDL` (C6.2.240)
- 4.158 `SMC` (C6.2.241)
- 4.159 `SMNEGL` (C6.2.242)
- 4.160 `SMSUBL` (C6.2.243)
- 4.161 `SMULH` (C6.2.244)
- 4.162 `SMULL` (C6.2.245)
- 4.163 `SSBB` (C6.2.246)
- 4.164 `ST2G` (C6.2.247)
- 4.165 `ST64B` (C6.2.248)
- 4.166 `ST64BV` (C6.2.249)
- 4.167 `ST64BV0` (C6.2.250)
- 4.168 `STADDB, STADDLB` (C6.2.251)
- 4.169 `STADDH, STADDLH` (C6.2.252)
- 4.170 `STADD, STADDL` (C6.2.253)
- 4.171 `STCLRB, STCLRLB` (C6.2.254)
- 4.172 `STCLRH, STCLRLH` (C6.2.255)
- 4.173 `STCLR, STCLRL` (C6.2.256)
- 4.174 `STEORB, STEORLB` (C6.2.257)
- 4.175 `STEORH, STEORLH` (C6.2.258)
- 4.176 `STEOR, STEORL` (C6.2.259)
- 4.177 `STG` (C6.2.260)
- 4.178 `STGM` (C6.2.261)
- 4.179 `STGP` (C6.2.262)
- 4.180 `STLLRB` (C6.2.263)
- 4.181 `STLLRH` (C6.2.264)
- 4.182 `STLLR` (C6.2.265)
- 4.183 `STLR` (C6.2.266)
- 4.184 `STLRB` (C6.2.267)
- 4.185 `STLRH` (C6.2.268)
- 4.186 `STLUR` (C6.2.269)
- 4.188 `STLURB` (C6.2.270)
- 4.189 `STLURH` (C6.2.271)
- 4.190 `STLXP` (C6.2.272)
- 4.191 `STLXR` (C6.2.273)
- 4.192 `STLXRB` (C6.2.274)
- 4.193 `STLXRH` (C6.2.275)
- 4.194 `STNP` (C6.2.276)
- 4.195 `STP` (C6.2.277)
- 4.196 `STR (immediate)` (C6.2.278)
- 4.197 `STR (register)` (C6.2.279)
- 4.199 `STRB (immediate)` (C6.2.280)
- 4.200 `STRB (register)` (C6.2.281)
- 4.201 `STRH (immediate)` (C6.2.282)
- 4.202 `STRH (register)` (C6.2.283)
- 4.203 `STSETB, STSETLB` (C6.2.284)
- 4.204 `STSETH, STSETLH` (C6.2.285)
- 4.205 `STSET, STSETL` (C6.2.286)
- 4.206 `STSMAXB, STSMAXLB` (C6.2.287)
- 4.207 `STSMAXH, STSMAXLH` (C6.2.288)
- 4.208 `STSMAX, STSMAXL` (C6.2.289)
- 4.210 `STSMINB, STSMINLB` (C6.2.290)
- 4.211 `STSMINH, STSMINLH` (C6.2.291)
- 4.212 `STSMIN, STSMINL` (C6.2.292)
- 4.213 `STTR` (C6.2.293)
- 4.214 `STTRB` (C6.2.294)
- 4.215 `STTRH` (C6.2.295)
- 4.216 `STUMAXB, STUMAXLB` (C6.2.296)
- 4.217 `STUMAXH, STUMAXLH` (C6.2.297)
- 4.218 `STUMAX, STUMAXL` (C6.2.298)
- 4.219 `STUMINB, STUMINLB` (C6.2.299)
- 4.222 `STUMINH, STUMINLH` (C6.2.300)
- 4.223 `STUMIN, STUMINL` (C6.2.301)
- 4.224 `STUR` (C6.2.302)
- 4.225 `STURB` (C6.2.303)
- 4.226 `STURH` (C6.2.304)
- 4.227 `STXP` (C6.2.305)
- 4.228 `STXR` (C6.2.306)
- 4.229 `STXRB` (C6.2.307)
- 4.230 `STXRH` (C6.2.308)
- 4.231 `STZ2G` (C6.2.309)
- 4.233 `STZG` (C6.2.310)
- 4.234 `STZGM` (C6.2.311)
- 4.235 `SUB (extended register)` (C6.2.312)
- 4.236 `SUB (immediate)` (C6.2.313)
- 4.237 `SUB (shifted register)` (C6.2.314)
- 4.238 `SUBG` (C6.2.315)
- 4.239 `SUBP` (C6.2.316)
- 4.240 `SUBPS` (C6.2.317)
- 4.241 `SUBS (extended register)` (C6.2.318)
- 4.242 `SUBS (immediate)` (C6.2.319)
- 4.244 `SUBS (shifted register)` (C6.2.320)
- 4.245 `SVC` (C6.2.321)
- 4.246 `SWPB, SWPAB, SWPALB, SWPLB` (C6.2.322)
- 4.247 `SWPH, SWPAH, SWPALH, SWPLH` (C6.2.323)
- 4.248 `SWP, SWPA, SWPAL, SWPL` (C6.2.324)
- 4.249 `SXTB` (C6.2.325)
- 4.250 `SXTH` (C6.2.326)
- 4.251 `SXTW` (C6.2.327)
- 4.252 `SYS` (C6.2.328)
- 4.253 `SYSL` (C6.2.329)
- 4.255 `TBNZ` (C6.2.330)
- 4.256 `TBZ` (C6.2.331)
- 4.257 `TLBI` (C6.2.332)
- 4.258 `TST (immediate)` (C6.2.334)
- 4.259 `TST (shifted register)` (C6.2.335)
- 4.260 `UBFIZ` (C6.2.336)
- 4.261 `UBFM` (C6.2.337)
- 4.262 `UBFX` (C6.2.338)
- 4.263 `UDF` (C6.2.339)
- 4.265 `UDIV` (C6.2.340)
- 4.266 `UMADDL` (C6.2.341)
- 4.267 `UMNEGL` (C6.2.342)
- 4.268 `UMSUBL` (C6.2.343)
- 4.269 `UMULH` (C6.2.344)
- 4.270 `UMULL` (C6.2.345)
- 4.271 `UXTB` (C6.2.346)
- 4.272 `UXTH` (C6.2.347)
- 4.273 `WFE` (C6.2.348)
- 4.274 `WFET` (C6.2.349)
- 4.276 `WFI` (C6.2.350)
- 4.277 `WFIT` (C6.2.351)
- 4.278 `XAFLAG` (C6.2.352)
- 4.279 `XPACD, XPACI, XPACLRI` (C6.2.353)
- 4.280 `YIELD` (C6.2.354)

---

## 指令详解

### 4.1 `RBIT` (C6.2.219)

**语义**：Reverse Bits reverses the bit order in a register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand = X[n];
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


*PDF 跨页*：p1280-p1282（共 3 页）



### 4.2 `RET` (C6.2.220)

**语义**：Return from subroutine branches unconditionally to an address in a register, with a hint that this is a subroutine return.


**汇编模板**：
```
RET {<Xn>}
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

| `<Xn>` | Is the 64-bit name of the general-purpose register holding the address to be branched to, encoded in the "Rn" field. Def |


</details>


*PDF 跨页*：p1282-p1283（共 2 页）



### 4.3 `RETAA, RETAB` (C6.2.221)

**语义**：Return from subroutine, with pointer authentication. This instruction authenticates the address that is held in LR, using SP as the modifier and the specified key, branches to the authenticated address, with a hint that this instruction is a subroutine return.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) target = X[30];
```

</details>


*PDF 跨页*：p1283-p1284（共 2 页）



### 4.4 `REV` (C6.2.222)

**语义**：Reverse Bytes reverses the byte order in a register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand = X[n];
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


*PDF 跨页*：p1284-p1286（共 3 页）



### 4.5 `REV16` (C6.2.223)

**语义**：Reverse bytes in 16-bit halfwords reverses the byte order in each 16-bit halfword of a register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand = X[n];
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


*PDF 跨页*：p1286-p1288（共 3 页）



### 4.6 `REV32` (C6.2.224)

**语义**：Reverse bytes in 32-bit words reverses the byte order in each 32-bit word of a register.


**汇编模板**：
```
REV32 <Xd>, <Xn>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer d = UInt(Rd); 
 integer n = UInt(Rn); 
  
 integer datasize = if sf == '1' then 64 else 32; 
  
 integer container_size; 
 case opc of 
     when '00' 
         Unreachable(); 
     when '01' 
         container_size = 16; 
     when '10' 
         container_size = 32; 
     when '11' 
         if sf == '0' then UNDEFINED; 
         container_size = 64;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1288-p1290（共 3 页）



### 4.7 `REV64` (C6.2.225)

**语义**：Reverse Bytes reverses the byte order in a 64-bit general-purpose register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of REV gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1290-p1291（共 2 页）



### 4.8 `RMIF` (C6.2.226)

**语义**：Performs a rotation right of a value held in a general purpose register by an immediate value, and then inserts a selection of the bottom four bits of the result of the rotation into the PSTATE flags, under the control of a second immediate mask.


**汇编模板**：
```
RMIF <Xn>, #<shift>, #<mask>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveFlagManipulateExt() then UNDEFINED; 
 integer lsb = UInt(imm6); 
 integer n = UInt(Rn);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(4) tmp;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<shift>` | Is the shift amount, in the range 0 to 63, defaulting to 0 and encoded in the "imm6" field, |

| `<mask>` | Is the flag bit mask, an immediate in the range 0 to 15, which selects the bits that are inserted into the NZCV conditio |


</details>


*PDF 跨页*：p1291-p1292（共 2 页）



### 4.9 `ROR (immediate)` (C6.2.227)

> ⚠️ **这是 `EXTR` 的别名**。底层编码与 `EXTR` 相同，只是汇编器接受不同写法。


**语义**：Rotate right (immediate) provides the value of the contents of a register rotated by a variable number of bits. The This instruction is an alias of the EXTR instruction. This means that: The encodings in this description are named to match the encodings of EXTR.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of EXTR gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Ws>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" and "Rm" fields. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xs>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" and "Rm" fields. |

| `<shift>` | For the 32-bit variant: is the amount by which to rotate, in the range 0 to 31, encoded in the "imms" field. For the 64- |


</details>


*PDF 跨页*：p1292-p1294（共 3 页）



### 4.10 `ROR (register)` (C6.2.228)

> ⚠️ **这是 `RORV` 的别名**。底层编码与 `RORV` 相同，只是汇编器接受不同写法。


**语义**：Rotate Right (register) provides the value of the contents of a register rotated by a variable number of bits. The bits that are rotated off the right end are inserted into the vacated bit positions on the left. The remainder obtained by dividing the second source register by the data size defines the number of bits by which the first source register is right-shifted.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of RORV gives the operational pseudocode for this instruction.
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


*PDF 跨页*：p1294-p1296（共 3 页）



### 4.11 `RORV` (C6.2.229)

> 💡 **被以下指令作为别名使用**：`ROR (register)`


**语义**：Rotate Right Variable provides the value of the contents of a register rotated by a variable number of bits. The bits that are rotated off the right end are inserted into the vacated bit positions on the left. The remainder obtained by dividing the second source register by the data size defines the number of bits by which the first source register is right-shifted.


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


*PDF 跨页*：p1296-p1298（共 3 页）



### 4.12 `SB` (C6.2.230)

**语义**：Speculation Barrier is a barrier that controls speculation.


**汇编模板**：
```
SB
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveSBExt() then UNDEFINED;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
SpeculationBarrier();
```

</details>


*PDF 跨页*：p1298-p1299（共 2 页）



### 4.13 `SBC` (C6.2.231)

> 💡 **被以下指令作为别名使用**：`NGC`


**语义**：Subtract with Carry subtracts a register value and the value of NOT (Carry flag) from a register value, and writes the result to the destination register.


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


*PDF 跨页*：p1299-p1301（共 3 页）



### 4.14 `SBCS` (C6.2.232)

> 💡 **被以下指令作为别名使用**：`NGCS`


**语义**：Subtract with Carry, setting flags, subtracts a register value and the value of NOT (Carry flag) from a register value, and writes the result to the destination register. It updates the condition flags based on the result.


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


*PDF 跨页*：p1301-p1303（共 3 页）



### 4.15 `SBFIZ` (C6.2.233)

> ⚠️ **这是 `SBFM` 的别名**。底层编码与 `SBFM` 相同，只是汇编器接受不同写法。


**语义**：Signed Bitfield Insert in Zeros copies a bitfield of <width> bits from the least significant bits of the source register to bit position <lsb> of the destination register, setting the destination bits below the bitfield to zero, and the bits above the bitfield to a copy of the most significant bit of the bitfield.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SBFM gives the operational pseudocode for this instruction.
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


*PDF 跨页*：p1303-p1305（共 3 页）



### 4.16 `SBFM` (C6.2.234)

**语义**：Signed Bitfield Move is usually accessed via one of its aliases, which are always preferred for disassembly.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) src = X[n];
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


*PDF 跨页*：p1305-p1308（共 4 页）



### 4.17 `SBFX` (C6.2.235)

> ⚠️ **这是 `SBFM` 的别名**。底层编码与 `SBFM` 相同，只是汇编器接受不同写法。


**语义**：Signed Bitfield Extract copies a bitfield of <width> bits starting from bit position <lsb> in the source register to the least significant bits of the destination register, and sets destination bits above the bitfield to a copy of the most significant bit of the bitfield.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SBFM gives the operational pseudocode for this instruction.
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


*PDF 跨页*：p1308-p1310（共 3 页）



### 4.18 `SDIV` (C6.2.236)

**语义**：Signed Divide divides a signed integer register value by another signed integer register value, and writes the result to the destination register. The condition flags are not affected.


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

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p1310-p1311（共 2 页）



### 4.19 `SETF8, SETF16` (C6.2.237)

**语义**：Set the PSTATE.NZV flags based on the value in the specified general-purpose register. SETF8 treats the value as an 8 bit value, and SETF16 treats the value as an 16 bit value.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(32) tmpreg = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1311-p1312（共 2 页）



### 4.20 `SEV` (C6.2.238)

**语义**：Send Event is a hint instruction. It causes an event to be signaled to all PEs in the multiprocessor system. For more information, see Wait for Event mechanism and Send event on page D1-2536.


**汇编模板**：
```
SEV
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
SendEvent();
```

</details>


*PDF 跨页*：p1312-p1313（共 2 页）



### 4.21 `SEVL` (C6.2.239)

**语义**：Send Event Local is a hint instruction that causes an event to be signaled locally without requiring the event to be signaled to other PEs in the multiprocessor system. It can prime a wait-loop which starts with a WFE instruction.


**汇编模板**：
```
SEVL
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
SendEventLocal();
```

</details>


*PDF 跨页*：p1313-p1314（共 2 页）



### 4.22 `SMADDL` (C6.2.240)

> 💡 **被以下指令作为别名使用**：`SMULL`


**语义**：Signed Multiply-Add Long multiplies two 32-bit register values, adds a 64-bit register value, and writes the result to the 64-bit destination register.


**汇编模板**：
```
SMADDL <Xd>, <Wn>, <Wm>, <Xa>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer d = UInt(Rd); 
 integer n = UInt(Rn); 
 integer m = UInt(Rm); 
 integer a = UInt(Ra); 
Alias conditions
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(32) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |

| `<Xa>` | Is the 64-bit name of the third general-purpose source register holding the addend, encoded in the "Ra" field. |


</details>


*PDF 跨页*：p1314-p1316（共 3 页）



### 4.23 `SMC` (C6.2.241)

**语义**：Secure Monitor Call causes an exception to EL3.


**汇编模板**：
```
SMC #<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
AArch64.CheckForSMCUndefOrTrap(imm16);
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<imm>` | Is a 16-bit unsigned immediate, in the range 0 to 65535, encoded in the "imm16" field. |


</details>


*PDF 跨页*：p1316-p1317（共 2 页）



### 4.24 `SMNEGL` (C6.2.242)

> ⚠️ **这是 `SMSUBL` 的别名**。底层编码与 `SMSUBL` 相同，只是汇编器接受不同写法。


**语义**：Signed Multiply-Negate Long multiplies two 32-bit register values, negates the product, and writes the result to the 64-bit destination register.


**汇编模板**：
```
SMNEGL <Xd>, <Wn>, <Wm>
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SMSUBL gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p1317-p1318（共 2 页）



### 4.25 `SMSUBL` (C6.2.243)

> 💡 **被以下指令作为别名使用**：`SMNEGL`


**语义**：Signed Multiply-Subtract Long multiplies two 32-bit register values, subtracts the product from a 64-bit register value, and writes the result to the 64-bit destination register.


**汇编模板**：
```
SMSUBL <Xd>, <Wn>, <Wm>, <Xa>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer d = UInt(Rd); 
 integer n = UInt(Rn); 
 integer m = UInt(Rm); 
 integer a = UInt(Ra); 
Alias conditions
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(32) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |

| `<Xa>` | Is the 64-bit name of the third general-purpose source register holding the minuend, encoded in the "Ra" field. |


</details>


*PDF 跨页*：p1318-p1320（共 3 页）



### 4.26 `SMULH` (C6.2.244)

**语义**：Signed Multiply High multiplies two 64-bit register values, and writes bits[127:64] of the 128-bit result to the 64-bit destination register.


**汇编模板**：
```
SMULH <Xd>, <Xn>, <Xm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer d = UInt(Rd); 
 integer n = UInt(Rn); 
 integer m = UInt(Rm);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p1320-p1321（共 2 页）



### 4.27 `SMULL` (C6.2.245)

> ⚠️ **这是 `SMADDL` 的别名**。底层编码与 `SMADDL` 相同，只是汇编器接受不同写法。


**语义**：Signed Multiply Long multiplies two 32-bit register values, and writes the result to the 64-bit destination register.


**汇编模板**：
```
SMULL <Xd>, <Wn>, <Wm>
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SMADDL gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p1321-p1322（共 2 页）



### 4.28 `SSBB` (C6.2.246)

> ⚠️ **这是 `DSB` 的别名**。底层编码与 `DSB` 相同，只是汇编器接受不同写法。


**语义**：Speculative Store Bypass Barrier is a memory barrier which prevents speculative loads from bypassing earlier stores to the same virtual address under certain conditions.


**汇编模板**：
```
SSBB
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of DSB gives the operational pseudocode for this instruction.
```

</details>


*PDF 跨页*：p1322-p1323（共 2 页）



### 4.29 `ST2G` (C6.2.247)

**语义**：Store Allocation Tags stores an Allocation Tag to two Tag granules of memory. The address used for the store is calculated from the base register and an immediate signed offset scaled by the Tag granule. The Allocation Tag is calculated from the Logical Address Tag in the source register.


**汇编模板**：
```
ST2G <Xt|SP>, [<Xn|SP>], #<simm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 bits(64) offset = LSL(SignExtend(imm9, 64), LOG2_TAG_GRANULE); 
 boolean writeback = TRUE; 
 boolean postindex = TRUE; 
Pre-index
(FEAT_MTE)
Encoding
ST2G <Xt|SP>, [<Xn|SP>, #<simm>]!
Decode for this encoding
 if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 bits(64) offset = LSL(SignExtend(imm9, 64), LOG2_TAG_GRANULE); 
 boolean writeback = TRUE; 
 boolean postindex = FALSE; 
Signed offset
(FEAT_MTE)
1
1
0
1
1
0
0
1
1
0
1
imm9
0
1
Xn
Xt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0
1
1
0
1
1
0
0
1
1
0
1
imm9
1
1
Xn
Xt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0
1
1
0
1
1
0
0
1
1
0
1
imm9
1
0
Xn
Xt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0

A64 Base Instruction Descriptions 
C6.2 Alphabetical list of A64 base instructions
C6-1324
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
ARM DDI 0487G.b
Non-Confidential
ID072021
Encoding
ST2G <Xt|SP>, [<Xn|SP>{, #<simm>}]
Decode for this encoding
 if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 bits(64) offset = LSL(SignExtend(imm9, 64), LOG2_TAG_GRANULE); 
 boolean writeback = FALSE; 
 boolean postindex = FALSE;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt|SP>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Xt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Xn" field. |

| `<simm>` | Is the optional signed immediate offset, a multiple of 16 in the range -4096 to 4080, defaulting to 0 and encoded in the |


</details>


*PDF 跨页*：p1323-p1325（共 3 页）



### 4.30 `ST64B` (C6.2.248)

**语义**：Single-copy Atomic 64-byte Store without Return stores eight 64-bit doublewords from consecutive registers, Xt to X(t+7), to a memory location. The data that is stored is atomic and is required to be 64-byte-aligned.


**汇编模板**：
```
ST64B <Xt>, [<Xn|SP> {,#0}]
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


*PDF 跨页*：p1325-p1326（共 2 页）



### 4.31 `ST64BV` (C6.2.249)

**语义**：Single-copy Atomic 64-byte Store with Return stores eight 64-bit doublewords from consecutive registers, Xt to X(t+7), to a memory location, and writes the status result of the store to a register. The data that is stored is atomic and is required to be 64-byte aligned.


**汇编模板**：
```
ST64BV <Xs>, <Xt>, [<Xn|SP>]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveFeatLS64() then UNDEFINED; 
 if Rt<4:3> == '11' || Rt<0> == '1' then UNDEFINED; 
  
 integer n = UInt(Rn); 
 integer t = UInt(Rt); 
 integer s = UInt(Rs); 
 boolean tag_checked = n != 31;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
CheckST64BVEnabled();
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xs>` | Is the 64-bit name of the general-purpose register into which the status result of this instruction is written, encoded  |

| `<Xt>` | Is the 64-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1326-p1328（共 3 页）



### 4.32 `ST64BV0` (C6.2.250)

**语义**：Single-copy Atomic 64-byte EL0 Store with Return stores eight 64-bit doublewords from consecutive registers, Xt to X(t+7), to a memory location, with the bottom 32 bits taken from ACCDATA_EL1, and writes the status result of the store to a register. The data that is stored is atomic and is required to be 64-byte aligned.


**汇编模板**：
```
ST64BV0 <Xs>, <Xt>, [<Xn|SP>]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveFeatLS64() then UNDEFINED; 
 if Rt<4:3> == '11' || Rt<0> == '1' then UNDEFINED; 
  
 integer n = UInt(Rn); 
 integer t = UInt(Rt); 
 integer s = UInt(Rs); 
 boolean tag_checked = n != 31;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
CheckST64BV0Enabled();
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xs>` | Is the 64-bit name of the general-purpose register into which the status result of this instruction is written, encoded  |

| `<Xt>` | Is the 64-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1328-p1330（共 3 页）



### 4.33 `STADDB, STADDLB` (C6.2.251)

**语义**：Atomic add on byte in memory, without return, atomically loads an 8-bit byte from memory, adds the value held in a register to it, and stores the result back to memory.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDADDB, LDADDAB, LDADDALB, LDADDLB gives the operational pseudocode for this
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1330-p1332（共 3 页）



### 4.34 `STADDH, STADDLH` (C6.2.252)

**语义**：Atomic add on halfword in memory, without return, atomically loads a 16-bit halfword from memory, adds the value held in a register to it, and stores the result back to memory.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDADDH, LDADDAH, LDADDALH, LDADDLH gives the operational pseudocode for this
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1332-p1334（共 3 页）



### 4.35 `STADD, STADDL` (C6.2.253)

**语义**：Atomic add on word or doubleword in memory, without return, atomically loads a 32-bit word or 64-bit doubleword from memory, adds the value held in a register to it, and stores the result back to memory.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDADD, LDADDA, LDADDAL, LDADDL gives the operational pseudocode for this
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1334-p1336（共 3 页）



### 4.36 `STCLRB, STCLRLB` (C6.2.254)

**语义**：Atomic bit clear on byte in memory, without return, atomically loads an 8-bit byte from memory, performs a bitwise AND with the complement of the value held in a register on it, and stores the result back to memory.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDCLRB, LDCLRAB, LDCLRALB, LDCLRLB gives the operational pseudocode for this
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1336-p1338（共 3 页）



### 4.37 `STCLRH, STCLRLH` (C6.2.255)

**语义**：Atomic bit clear on halfword in memory, without return, atomically loads a 16-bit halfword from memory, performs a bitwise AND with the complement of the value held in a register on it, and stores the result back to memory.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDCLRH, LDCLRAH, LDCLRALH, LDCLRLH gives the operational pseudocode for this
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1338-p1340（共 3 页）



### 4.38 `STCLR, STCLRL` (C6.2.256)

**语义**：Atomic bit clear on word or doubleword in memory, without return, atomically loads a 32-bit word or 64-bit doubleword from memory, performs a bitwise AND with the complement of the value held in a register on it, and stores the result back to memory.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDCLR, LDCLRA, LDCLRAL, LDCLRL gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1340-p1342（共 3 页）



### 4.39 `STEORB, STEORLB` (C6.2.257)

**语义**：Atomic exclusive OR on byte in memory, without return, atomically loads an 8-bit byte from memory, performs an exclusive OR with the value held in a register on it, and stores the result back to memory.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDEORB, LDEORAB, LDEORALB, LDEORLB gives the operational pseudocode for this
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1342-p1344（共 3 页）



### 4.40 `STEORH, STEORLH` (C6.2.258)

**语义**：Atomic exclusive OR on halfword in memory, without return, atomically loads a 16-bit halfword from memory, performs an exclusive OR with the value held in a register on it, and stores the result back to memory.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDEORH, LDEORAH, LDEORALH, LDEORLH gives the operational pseudocode for this
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1344-p1346（共 3 页）



### 4.41 `STEOR, STEORL` (C6.2.259)

**语义**：Atomic exclusive OR on word or doubleword in memory, without return, atomically loads a 32-bit word or 64-bit doubleword from memory, performs an exclusive OR with the value held in a register on it, and stores the result back to memory.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDEOR, LDEORA, LDEORAL, LDEORL gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1346-p1348（共 3 页）



### 4.42 `STG` (C6.2.260)

**语义**：Store Allocation Tag stores an Allocation Tag to memory. The address used for the store is calculated from the base register and an immediate signed offset scaled by the Tag granule. The Allocation Tag is calculated from the Logical Address Tag in the source register.


**汇编模板**：
```
STG <Xt|SP>, [<Xn|SP>], #<simm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 bits(64) offset = LSL(SignExtend(imm9, 64), LOG2_TAG_GRANULE); 
 boolean writeback = TRUE; 
 boolean postindex = TRUE; 
Pre-index
(FEAT_MTE)
Encoding
STG <Xt|SP>, [<Xn|SP>, #<simm>]!
Decode for this encoding
 if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 bits(64) offset = LSL(SignExtend(imm9, 64), LOG2_TAG_GRANULE); 
 boolean writeback = TRUE; 
 boolean postindex = FALSE; 
Signed offset
(FEAT_MTE)
1
1
0
1
1
0
0
1
0
0
1
imm9
0
1
Xn
Xt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0
1
1
0
1
1
0
0
1
0
0
1
imm9
1
1
Xn
Xt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0
1
1
0
1
1
0
0
1
0
0
1
imm9
1
0
Xn
Xt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0

A64 Base Instruction Descriptions 
C6.2 Alphabetical list of A64 base instructions
ARM DDI 0487G.b
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
C6-1349
ID072021
Non-Confidential
Encoding
STG <Xt|SP>, [<Xn|SP>{, #<simm>}]
Decode for this encoding
 if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 bits(64) offset = LSL(SignExtend(imm9, 64), LOG2_TAG_GRANULE); 
 boolean writeback = FALSE; 
 boolean postindex = FALSE;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt|SP>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Xt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Xn" field. |

| `<simm>` | Is the optional signed immediate offset, a multiple of 16 in the range -4096 to 4080, defaulting to 0 and encoded in the |


</details>


*PDF 跨页*：p1348-p1350（共 3 页）



### 4.43 `STGM` (C6.2.261)

**语义**：Store Tag Multiple writes a naturally aligned block of N Allocation Tags, where the size of N is identified in GMID_EL1.BS, and the Allocation Tag written to address A is taken from the source register at 4*A<7:4>+3:4*A<7:4>.


**汇编模板**：
```
STGM <Xt>, [<Xn|SP>]
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


*PDF 跨页*：p1350-p1351（共 2 页）



### 4.44 `STGP` (C6.2.262)

**语义**：Store Allocation Tag and Pair of registers stores an Allocation Tag and two 64-bit doublewords to memory, from two registers. The address used for the store is calculated from the base register and an immediate signed offset scaled by the Tag granule. The Allocation Tag is calculated from the Logical Address Tag in the base register.


**汇编模板**：
```
STGP <Xt1>, <Xt2>, [<Xn|SP>], #<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 integer t2 = UInt(Xt2); 
 bits(64) offset = LSL(SignExtend(simm7, 64), LOG2_TAG_GRANULE); 
 boolean writeback = TRUE; 
 boolean postindex = TRUE; 
Pre-index
(FEAT_MTE)
Encoding
STGP <Xt1>, <Xt2>, [<Xn|SP>, #<imm>]!
Decode for this encoding
 if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 integer t2 = UInt(Xt2); 
 bits(64) offset = LSL(SignExtend(simm7, 64), LOG2_TAG_GRANULE); 
 boolean writeback = TRUE; 
 boolean postindex = FALSE; 
Signed offset
(FEAT_MTE)
0
1
1
0
1
0
0
0
1
0
simm7
Xt2
Xn
Xt
31 30 29 28 27 26 25 24 23 22 21
15 14
10 9
5
4
0
0
1
1
0
1
0
0
1
1
0
simm7
Xt2
Xn
Xt
31 30 29 28 27 26 25 24 23 22 21
15 14
10 9
5
4
0

A64 Base Instruction Descriptions 
C6.2 Alphabetical list of A64 base instructions
C6-1352
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
ARM DDI 0487G.b
Non-Confidential
ID072021
Encoding
STGP <Xt1>, <Xt2>, [<Xn|SP>{, #<imm>}]
Decode for this encoding
 if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 integer t2 = UInt(Xt2); 
 bits(64) offset = LSL(SignExtend(simm7, 64), LOG2_TAG_GRANULE); 
 boolean writeback = FALSE; 
 boolean postindex = FALSE;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt1>` | Is the 64-bit name of the first general-purpose register to be transferred, encoded in the "Xt" field. |

| `<Xt2>` | Is the 64-bit name of the second general-purpose register to be transferred, encoded in the "Xt2" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Xn" field. |

| `<imm>` | For the post-index and pre-index variant: is the signed immediate offset, a multiple of 16 in the range -1024 to 1008, e |


</details>


*PDF 跨页*：p1351-p1354（共 4 页）



### 4.45 `STLLRB` (C6.2.263)

**语义**：Store LORelease Register Byte stores a byte from a 32-bit register to a memory location. The instruction also has memory ordering semantics as described in LoadLOAcquire, StoreLORelease on page B2-153. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
STLLRB <Wt>, [<Xn|SP>{,#0}]
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


*PDF 跨页*：p1354-p1355（共 2 页）



### 4.46 `STLLRH` (C6.2.264)

**语义**：Store LORelease Register Halfword stores a halfword from a 32-bit register to a memory location. The instruction also has memory ordering semantics as described in LoadLOAcquire, StoreLORelease on page B2-153. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
STLLRH <Wt>, [<Xn|SP>{,#0}]
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


*PDF 跨页*：p1355-p1356（共 2 页）



### 4.47 `STLLR` (C6.2.265)

**语义**：Store LORelease Register stores a 32-bit word or a 64-bit doubleword to a memory location, from a register. The instruction also has memory ordering semantics as described in LoadLOAcquire, StoreLORelease on page B2-153.


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


*PDF 跨页*：p1356-p1358（共 3 页）



### 4.48 `STLR` (C6.2.266)

**语义**：Store-Release Register stores a 32-bit word or a 64-bit doubleword to a memory location, from a register. The instruction also has memory ordering semantics as described in Load-Acquire, Load-AcquirePC, and Store-Release on page B2-152. For information about memory accesses, see Load/store addressing modes on page C1-202.


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


*PDF 跨页*：p1358-p1360（共 3 页）



### 4.49 `STLRB` (C6.2.267)

**语义**：Store-Release Register Byte stores a byte from a 32-bit register to a memory location. The instruction also has memory ordering semantics as described in Load-Acquire, Load-AcquirePC, and Store-Release on page B2-152.


**汇编模板**：
```
STLRB <Wt>, [<Xn|SP>{,#0}]
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


*PDF 跨页*：p1360-p1361（共 2 页）



### 4.50 `STLRH` (C6.2.268)

**语义**：Store-Release Register Halfword stores a halfword from a 32-bit register to a memory location. The instruction also has memory ordering semantics as described in Load-Acquire, Load-AcquirePC, and Store-Release on page B2-152. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
STLRH <Wt>, [<Xn|SP>{,#0}]
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


*PDF 跨页*：p1361-p1362（共 2 页）



### 4.51 `STLUR` (C6.2.269)

**语义**：Store-Release Register (unscaled) calculates an address from a base register value and an immediate offset, and stores a 32-bit word or a 64-bit doubleword to the calculated address, from a register.


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


*PDF 跨页*：p1362-p1364（共 3 页）



### 4.52 `STLURB` (C6.2.270)

**语义**：Store-Release Register Byte (unscaled) calculates an address from a base register value and an immediate offset, and stores a byte to the calculated address, from a 32-bit register.


**汇编模板**：
```
STLURB <Wt>, [<Xn|SP>{, #<simm>}]
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


*PDF 跨页*：p1364-p1366（共 3 页）



### 4.53 `STLURH` (C6.2.271)

**语义**：Store-Release Register Halfword (unscaled) calculates an address from a base register value and an immediate offset, and stores a halfword to the calculated address, from a 32-bit register.


**汇编模板**：
```
STLURH <Wt>, [<Xn|SP>{, #<simm>}]
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


*PDF 跨页*：p1366-p1368（共 3 页）



### 4.54 `STLXP` (C6.2.272)

**语义**：Store-Release Exclusive Pair of registers stores two 32-bit words or two 64-bit doublewords to a memory location was successful, or of 1 if no store was performed. See Synchronization and semaphores on page B2-179. For information on single-copy atomicity and alignment requirements, see Requirements for single-copy atomicity on page B2-128 and Alignment of data accesses on page B2-160. If a 64-bit pair Store-Exclusive succeeds, it causes a single-copy atomic update of the 128-bit memory location


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register into which the status result of the store exclusive is written, encod |

| `<Xt1>` | Is the 64-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt2>` | Is the 64-bit name of the second general-purpose register to be transferred, encoded in the "Rt2" field. |

| `<Wt1>` | Is the 32-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Wt2>` | Is the 32-bit name of the second general-purpose register to be transferred, encoded in the "Rt2" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. Aborts and alignmen |


</details>


*PDF 跨页*：p1368-p1371（共 4 页）



### 4.55 `STLXR` (C6.2.273)

**语义**：Store-Release Exclusive Register stores a 32-bit word or a 64-bit doubleword to memory if the PE has exclusive access to the memory address, from two registers, and returns a status value of 0 if the store was successful, or of 1 The instruction also has memory ordering semantics as described in Load-Acquire, Load-AcquirePC, and Store-Release on page B2-152. For information about memory accesses see Load/store addressing modes on page C1-202.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register into which the status result of the store exclusive is written, encod |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. Aborts and alignmen |


</details>


*PDF 跨页*：p1371-p1374（共 4 页）



### 4.56 `STLXRB` (C6.2.274)

**语义**：Store-Release Exclusive Register Byte stores a byte from a 32-bit register to memory if the PE has exclusive access to the memory address, and returns a status value of 0 if the store was successful, or of 1 if no store was performed.


**汇编模板**：
```
STLXRB <Ws>, <Wt>, [<Xn|SP>{,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn); 
 integer t = UInt(Rt); 
 integer s = UInt(Rs);    // ignored by all loads and store-release 
  
 boolean tag_checked = n != 31; 
  
 boolean rt_unknown = FALSE; 
 boolean rn_unknown = FALSE; 
 if s == t then 
     Constraint c = ConstrainUnpredictable(); 
     assert c IN {Constraint_UNKNOWN, Constraint_UNDEF, Constraint_NOP}; 
     case c of 
         when Constraint_UNKNOWN rt_unknown = TRUE;    // store UNKNOWN value 
         when Constraint_UNDEF   UNDEFINED; 
         when Constraint_NOP     EndOfInstruction(); 
 if s == n && n != 31 then 
     Constraint c = ConstrainUnpredictable(); 
     assert c IN {Constraint_UNKNOWN, Constraint_UNDEF, Constraint_NOP}; 
     case c of 
         when Constraint_UNKNOWN rn_unknown = TRUE;    // address is UNKNOWN 
         when Constraint_UNDEF   UNDEFINED; 
         when Constraint_NOP     EndOfInstruction(); 
Notes for all encodings
For information about the CONSTRAINED UNPREDICTABLE behavior of this instruction, see Appendix K1 
Architectural Constraints on UNPREDICTABLE Behaviors, and particularly STLXRB on page K1-8420.
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

| `<Ws>` | Is the 32-bit name of the general-purpose register into which the status result of the store exclusive is written, encod |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. Aborts 0 0 0 0 1 0  |


</details>


*PDF 跨页*：p1374-p1376（共 3 页）



### 4.57 `STLXRH` (C6.2.275)

**语义**：Store-Release Exclusive Register Halfword stores a halfword from a 32-bit register to memory if the PE has exclusive access to the memory address, and returns a status value of 0 if the store was successful, or of 1 if no store was performed. See Synchronization and semaphores on page B2-179. The memory access is atomic. The instruction also has memory ordering semantics as described in Load-Acquire, Load-AcquirePC, and Store-Release on page B2-152. For information about memory accesses see Load


**汇编模板**：
```
STLXRH <Ws>, <Wt>, [<Xn|SP>{,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn); 
 integer t = UInt(Rt); 
 integer s = UInt(Rs);    // ignored by all loads and store-release 
  
 boolean tag_checked = n != 31; 
  
 boolean rt_unknown = FALSE; 
 boolean rn_unknown = FALSE; 
 if s == t then 
     Constraint c = ConstrainUnpredictable(); 
     assert c IN {Constraint_UNKNOWN, Constraint_UNDEF, Constraint_NOP}; 
     case c of 
         when Constraint_UNKNOWN rt_unknown = TRUE;    // store UNKNOWN value 
         when Constraint_UNDEF   UNDEFINED; 
         when Constraint_NOP     EndOfInstruction(); 
 if s == n && n != 31 then 
     Constraint c = ConstrainUnpredictable(); 
     assert c IN {Constraint_UNKNOWN, Constraint_UNDEF, Constraint_NOP}; 
     case c of 
         when Constraint_UNKNOWN rn_unknown = TRUE;    // address is UNKNOWN 
         when Constraint_UNDEF   UNDEFINED; 
         when Constraint_NOP     EndOfInstruction(); 
Notes for all encodings
For information about the CONSTRAINED UNPREDICTABLE behavior of this instruction, see Appendix K1 
Architectural Constraints on UNPREDICTABLE Behaviors, and particularly STLXRH on page K1-8420.
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

| `<Ws>` | Is the 32-bit name of the general-purpose register into which the status result of the store exclusive is written, encod |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. Aborts and alignmen |


</details>


*PDF 跨页*：p1376-p1378（共 3 页）



### 4.58 `STNP` (C6.2.276)

**语义**：Store Pair of Registers, with non-temporal hint, calculates an address from a base register value and an immediate offset, and stores two 32-bit words or two 64-bit doublewords to the calculated address, from two registers. For information about memory accesses, see Load/store addressing modes on page C1-202. For information about Non-temporal pair instructions, see Load/store non-temporal pair on page C3-227.


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


*PDF 跨页*：p1378-p1380（共 3 页）



### 4.59 `STP` (C6.2.277)

**语义**：Store Pair of Registers calculates an address from a base register value and an immediate offset, and stores two 32-bit words or two 64-bit doublewords to the calculated address, from two registers. For information about memory accesses, see Load/store addressing modes on page C1-202.


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


*PDF 跨页*：p1380-p1383（共 4 页）



### 4.60 `STR (immediate)` (C6.2.278)

**语义**：Store Register (immediate) stores a word or a doubleword from a register to memory. The address that is used for the store is calculated from a base register and an immediate offset. For information about memory accesses, see Load/store addressing modes on page C1-202.


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |

| `<simm>` | Is the signed immediate byte offset, in the range -256 to 255, encoded in the "imm9" field. |

| `<pimm>` | For the 32-bit variant: is the optional positive immediate byte offset, a multiple of 4 in the range 0 to 16380, default |


</details>


*PDF 跨页*：p1383-p1386（共 4 页）



### 4.61 `STR (register)` (C6.2.279)

**语义**：Store Register (register) calculates an address from a base register value and an offset register value, and stores a 32-bit word or a 64-bit doubleword to the calculated address, from a register. For information about memory accesses, see Load/store addressing modes on page C1-202.


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


*PDF 跨页*：p1386-p1388（共 3 页）



### 4.62 `STRB (immediate)` (C6.2.280)

**语义**：Store Register Byte (immediate) stores the least significant byte of a 32-bit register to memory. The address that is used for the store is calculated from a base register and an immediate offset. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
STRB <Wt>, [<Xn|SP>], #<simm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
boolean wback = TRUE; 
 boolean postindex = TRUE; 
 bits(64) offset = SignExtend(imm9, 64); 
Pre-index
Encoding
STRB <Wt>, [<Xn|SP>, #<simm>]!
Decode for this encoding
 boolean wback = TRUE; 
 boolean postindex = FALSE; 
 bits(64) offset = SignExtend(imm9, 64); 
Unsigned offset
Encoding
STRB <Wt>, [<Xn|SP>{, #<pimm>}]
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
0
0
1
1
1
0
0
0
0
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
0
0
1
1
1
0
0
1
0
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
ARM DDI 0487G.b
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
C6-1389
ID072021
Non-Confidential
Notes for all encodings
For information about the CONSTRAINED UNPREDICTABLE behavior of this instruction, see Appendix K1 
Architectural Constraints on UNPREDICTABLE Behaviors, and particularly STRB (immediate) on page K1-8421.
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


*PDF 跨页*：p1388-p1391（共 4 页）



### 4.63 `STRB (register)` (C6.2.281)

**语义**：Store Register Byte (register) calculates an address from a base register value and an offset register value, and stores a byte from a 32-bit register to the calculated address. For information about memory accesses, see Load/store addressing modes on page C1-202.


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


*PDF 跨页*：p1391-p1393（共 3 页）



### 4.64 `STRH (immediate)` (C6.2.282)

**语义**：Store Register Halfword (immediate) stores the least significant halfword of a 32-bit register to memory. The address that is used for the store is calculated from a base register and an immediate offset. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
STRH <Wt>, [<Xn|SP>], #<simm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
boolean wback = TRUE; 
 boolean postindex = TRUE; 
 bits(64) offset = SignExtend(imm9, 64); 
Pre-index
Encoding
STRH <Wt>, [<Xn|SP>, #<simm>]!
Decode for this encoding
 boolean wback = TRUE; 
 boolean postindex = FALSE; 
 bits(64) offset = SignExtend(imm9, 64); 
Unsigned offset
Encoding
STRH <Wt>, [<Xn|SP>{, #<pimm>}]
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
0
1
1
1
1
0
0
0
0
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
0
1
1
1
1
0
0
1
0
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
C6-1394
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
ARM DDI 0487G.b
Non-Confidential
ID072021
Notes for all encodings
For information about the CONSTRAINED UNPREDICTABLE behavior of this instruction, see Appendix K1 
Architectural Constraints on UNPREDICTABLE Behaviors, and particularly STRH (immediate) on page K1-8421.
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


*PDF 跨页*：p1393-p1396（共 4 页）



### 4.65 `STRH (register)` (C6.2.283)

**语义**：Store Register Halfword (register) calculates an address from a base register value and an offset register value, and stores a halfword from a 32-bit register to the calculated address. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
STRH <Wt>, [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]
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


*PDF 跨页*：p1396-p1398（共 3 页）



### 4.66 `STSETB, STSETLB` (C6.2.284)

**语义**：Atomic bit set on byte in memory, without return, atomically loads an 8-bit byte from memory, performs a bitwise OR with the value held in a register on it, and stores the result back to memory.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDSETB, LDSETAB, LDSETALB, LDSETLB gives the operational pseudocode for this
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1398-p1400（共 3 页）



### 4.67 `STSETH, STSETLH` (C6.2.285)

**语义**：Atomic bit set on halfword in memory, without return, atomically loads a 16-bit halfword from memory, performs a bitwise OR with the value held in a register on it, and stores the result back to memory.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDSETH, LDSETAH, LDSETALH, LDSETLH gives the operational pseudocode for this
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1400-p1402（共 3 页）



### 4.68 `STSET, STSETL` (C6.2.286)

**语义**：Atomic bit set on word or doubleword in memory, without return, atomically loads a 32-bit word or 64-bit doubleword from memory, performs a bitwise OR with the value held in a register on it, and stores the result back to memory.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDSET, LDSETA, LDSETAL, LDSETL gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1402-p1404（共 3 页）



### 4.69 `STSMAXB, STSMAXLB` (C6.2.287)

**语义**：Atomic signed maximum on byte in memory, without return, atomically loads an 8-bit byte from memory, compares it against the value held in a register, and stores the larger value back to memory, treating the values as signed numbers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDSMAXB, LDSMAXAB, LDSMAXALB, LDSMAXLB gives the operational pseudocode for
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. 0 0 1 1 1 0 0 0 0 R |


</details>


*PDF 跨页*：p1404-p1406（共 3 页）



### 4.70 `STSMAXH, STSMAXLH` (C6.2.288)

**语义**：Atomic signed maximum on halfword in memory, without return, atomically loads a 16-bit halfword from memory, compares it against the value held in a register, and stores the larger value back to memory, treating the values as signed numbers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDSMAXH, LDSMAXAH, LDSMAXALH, LDSMAXLH gives the operational pseudocode
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. 0 1 1 1 1 0 0 0 0 R |


</details>


*PDF 跨页*：p1406-p1408（共 3 页）



### 4.71 `STSMAX, STSMAXL` (C6.2.289)

**语义**：Atomic signed maximum on word or doubleword in memory, without return, atomically loads a 32-bit word or 64-bit doubleword from memory, compares it against the value held in a register, and stores the larger value back to memory, treating the values as signed numbers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDSMAX, LDSMAXA, LDSMAXAL, LDSMAXL gives the operational pseudocode for this
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1408-p1410（共 3 页）



### 4.72 `STSMINB, STSMINLB` (C6.2.290)

**语义**：Atomic signed minimum on byte in memory, without return, atomically loads an 8-bit byte from memory, compares it against the value held in a register, and stores the smaller value back to memory, treating the values as signed numbers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDSMINB, LDSMINAB, LDSMINALB, LDSMINLB gives the operational pseudocode for this
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. 0 0 1 1 1 0 0 0 0 R |


</details>


*PDF 跨页*：p1410-p1412（共 3 页）



### 4.73 `STSMINH, STSMINLH` (C6.2.291)

**语义**：Atomic signed minimum on halfword in memory, without return, atomically loads a 16-bit halfword from memory, compares it against the value held in a register, and stores the smaller value back to memory, treating the values as signed numbers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDSMINH, LDSMINAH, LDSMINALH, LDSMINLH gives the operational pseudocode for
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. 0 1 1 1 1 0 0 0 0 R |


</details>


*PDF 跨页*：p1412-p1414（共 3 页）



### 4.74 `STSMIN, STSMINL` (C6.2.292)

**语义**：Atomic signed minimum on word or doubleword in memory, without return, atomically loads a 32-bit word or 64-bit doubleword from memory, compares it against the value held in a register, and stores the smaller value back to memory, treating the values as signed numbers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDSMIN, LDSMINA, LDSMINAL, LDSMINL gives the operational pseudocode for this
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1414-p1416（共 3 页）



### 4.75 `STTR` (C6.2.293)

**语义**：Store Register (unprivileged) stores a word or doubleword from a register to memory. The address that is used for the store is calculated from a base register and an immediate offset.


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


*PDF 跨页*：p1416-p1418（共 3 页）



### 4.76 `STTRB` (C6.2.294)

**语义**：Store Register Byte (unprivileged) stores a byte from a 32-bit register to memory. The address that is used for the store is calculated from a base register and an immediate offset.


**汇编模板**：
```
STTRB <Wt>, [<Xn|SP>{, #<simm>}]
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


*PDF 跨页*：p1418-p1420（共 3 页）



### 4.77 `STTRH` (C6.2.295)

**语义**：Store Register Halfword (unprivileged) stores a halfword from a 32-bit register to memory. The address that is used for the store is calculated from a base register and an immediate offset.


**汇编模板**：
```
STTRH <Wt>, [<Xn|SP>{, #<simm>}]
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


*PDF 跨页*：p1420-p1422（共 3 页）



### 4.78 `STUMAXB, STUMAXLB` (C6.2.296)

**语义**：Atomic unsigned maximum on byte in memory, without return, atomically loads an 8-bit byte from memory, compares it against the value held in a register, and stores the larger value back to memory, treating the values as unsigned numbers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDUMAXB, LDUMAXAB, LDUMAXALB, LDUMAXLB gives the operational pseudocode
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. 0 0 1 1 1 0 0 0 0 R |


</details>


*PDF 跨页*：p1422-p1424（共 3 页）



### 4.79 `STUMAXH, STUMAXLH` (C6.2.297)

**语义**：Atomic unsigned maximum on halfword in memory, without return, atomically loads a 16-bit halfword from memory, compares it against the value held in a register, and stores the larger value back to memory, treating the values as unsigned numbers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDUMAXH, LDUMAXAH, LDUMAXALH, LDUMAXLH gives the operational pseudocode
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. 0 1 1 1 1 0 0 0 0 R |


</details>


*PDF 跨页*：p1424-p1426（共 3 页）



### 4.80 `STUMAX, STUMAXL` (C6.2.298)

**语义**：Atomic unsigned maximum on word or doubleword in memory, without return, atomically loads a 32-bit word or 64-bit doubleword from memory, compares it against the value held in a register, and stores the larger value back to memory, treating the values as unsigned numbers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDUMAX, LDUMAXA, LDUMAXAL, LDUMAXL gives the operational pseudocode for this
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1426-p1428（共 3 页）



### 4.81 `STUMINB, STUMINLB` (C6.2.299)

**语义**：Atomic unsigned minimum on byte in memory, without return, atomically loads an 8-bit byte from memory, compares it against the value held in a register, and stores the smaller value back to memory, treating the values as unsigned numbers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDUMINB, LDUMINAB, LDUMINALB, LDUMINLB gives the operational pseudocode for
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. 0 0 1 1 1 0 0 0 0 R |


</details>


*PDF 跨页*：p1428-p1430（共 3 页）



### 4.82 `STUMINH, STUMINLH` (C6.2.300)

**语义**：Atomic unsigned minimum on halfword in memory, without return, atomically loads a 16-bit halfword from memory, compares it against the value held in a register, and stores the smaller value back to memory, treating the values as unsigned numbers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDUMINH, LDUMINAH, LDUMINALH, LDUMINLH gives the operational pseudocode for
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. 0 1 1 1 1 0 0 0 0 R |


</details>


*PDF 跨页*：p1430-p1432（共 3 页）



### 4.83 `STUMIN, STUMINL` (C6.2.301)

**语义**：Atomic unsigned minimum on word or doubleword in memory, without return, atomically loads a 32-bit word or 64-bit doubleword from memory, compares it against the value held in a register, and stores the smaller value back to memory, treating the values as unsigned numbers.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of LDUMIN, LDUMINA, LDUMINAL, LDUMINL gives the operational pseudocode for this
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xs>` | Is the 64-bit name of the general-purpose register holding the data value to be operated on with the contents of the mem |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1432-p1434（共 3 页）



### 4.84 `STUR` (C6.2.302)

**语义**：Store Register (unscaled) calculates an address from a base register value and an immediate offset, and stores a 32-bit word or a 64-bit doubleword to the calculated address, from a register. For information about memory accesses, see Load/store addressing modes on page C1-202.


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


*PDF 跨页*：p1434-p1436（共 3 页）



### 4.85 `STURB` (C6.2.303)

**语义**：Store Register Byte (unscaled) calculates an address from a base register value and an immediate offset, and stores a byte to the calculated address, from a 32-bit register. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
STURB <Wt>, [<Xn|SP>{, #<simm>}]
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


*PDF 跨页*：p1436-p1437（共 2 页）



### 4.86 `STURH` (C6.2.304)

**语义**：Store Register Halfword (unscaled) calculates an address from a base register value and an immediate offset, and stores a halfword to the calculated address, from a 32-bit register. For information about memory accesses, see Load/store addressing modes on page C1-202.


**汇编模板**：
```
STURH <Wt>, [<Xn|SP>{, #<simm>}]
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


*PDF 跨页*：p1437-p1438（共 2 页）



### 4.87 `STXP` (C6.2.305)

**语义**：Store Exclusive Pair of registers stores two 32-bit words or two 64-bit doublewords from two registers to a memory location if the PE has exclusive access to the memory address, and returns a status value of 0 if the store was successful, or of 1 if no store was performed. See Synchronization and semaphores on page B2-179. For information on single-copy atomicity and alignment requirements, see Requirements for single-copy atomicity on page B2-128 and Alignment of data accesses on page B2-160. I


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register into which the status result of the store exclusive is written, encod |

| `<Xt1>` | Is the 64-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xt2>` | Is the 64-bit name of the second general-purpose register to be transferred, encoded in the "Rt2" field. |

| `<Wt1>` | Is the 32-bit name of the first general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Wt2>` | Is the 32-bit name of the second general-purpose register to be transferred, encoded in the "Rt2" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. Aborts and alignmen |


</details>


*PDF 跨页*：p1438-p1441（共 4 页）



### 4.88 `STXR` (C6.2.306)

**语义**：Store Exclusive Register stores a 32-bit word or a 64-bit doubleword from a register to memory if the PE has exclusive access to the memory address, and returns a status value of 0 if the store was successful, or of 1 if no store was performed. See Synchronization and semaphores on page B2-179. For information about memory accesses see Load/store addressing modes on page C1-202.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register into which the status result of the store exclusive is written, encod |


</details>


*PDF 跨页*：p1441-p1443（共 3 页）



### 4.89 `STXRB` (C6.2.307)

**语义**：Store Exclusive Register Byte stores a byte from a register to memory if the PE has exclusive access to the memory address, and returns a status value of 0 if the store was successful, or of 1 if no store was performed. See Synchronization and semaphores on page B2-179. The memory access is atomic.


**汇编模板**：
```
STXRB <Ws>, <Wt>, [<Xn|SP>{,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn); 
 integer t = UInt(Rt); 
 integer s = UInt(Rs);    // ignored by all loads and store-release 
  
 boolean tag_checked = n != 31; 
  
 boolean rt_unknown = FALSE; 
 boolean rn_unknown = FALSE; 
 if s == t then 
     Constraint c = ConstrainUnpredictable(); 
     assert c IN {Constraint_UNKNOWN, Constraint_UNDEF, Constraint_NOP}; 
     case c of 
         when Constraint_UNKNOWN rt_unknown = TRUE;    // store UNKNOWN value 
         when Constraint_UNDEF   UNDEFINED; 
         when Constraint_NOP     EndOfInstruction(); 
 if s == n && n != 31 then 
     Constraint c = ConstrainUnpredictable(); 
     assert c IN {Constraint_UNKNOWN, Constraint_UNDEF, Constraint_NOP}; 
     case c of 
         when Constraint_UNKNOWN rn_unknown = TRUE;    // address is UNKNOWN 
         when Constraint_UNDEF   UNDEFINED; 
         when Constraint_NOP     EndOfInstruction(); 
Notes for all encodings
For information about the CONSTRAINED UNPREDICTABLE behavior of this instruction, see Appendix K1 
Architectural Constraints on UNPREDICTABLE Behaviors, and particularly STXRB on page K1-8422.
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

| `<Ws>` | Is the 32-bit name of the general-purpose register into which the status result of the store exclusive is written, encod |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. Aborts 0 0 0 0 1 0  |


</details>


*PDF 跨页*：p1443-p1445（共 3 页）



### 4.90 `STXRH` (C6.2.308)

**语义**：Store Exclusive Register Halfword stores a halfword from a register to memory if the PE has exclusive access to the memory address, and returns a status value of 0 if the store was successful, or of 1 if no store was performed.


**汇编模板**：
```
STXRH <Ws>, <Wt>, [<Xn|SP>{,#0}]
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer n = UInt(Rn); 
 integer t = UInt(Rt); 
 integer s = UInt(Rs);    // ignored by all loads and store-release 
  
 boolean tag_checked = n != 31; 
  
 boolean rt_unknown = FALSE; 
 boolean rn_unknown = FALSE; 
 if s == t then 
     Constraint c = ConstrainUnpredictable(); 
     assert c IN {Constraint_UNKNOWN, Constraint_UNDEF, Constraint_NOP}; 
     case c of 
         when Constraint_UNKNOWN rt_unknown = TRUE;    // store UNKNOWN value 
         when Constraint_UNDEF   UNDEFINED; 
         when Constraint_NOP     EndOfInstruction(); 
 if s == n && n != 31 then 
     Constraint c = ConstrainUnpredictable(); 
     assert c IN {Constraint_UNKNOWN, Constraint_UNDEF, Constraint_NOP}; 
     case c of 
         when Constraint_UNKNOWN rn_unknown = TRUE;    // address is UNKNOWN 
         when Constraint_UNDEF   UNDEFINED; 
         when Constraint_NOP     EndOfInstruction();
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

| `<Ws>` | Is the 32-bit name of the general-purpose register into which the status result of the store exclusive is written, encod |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be transferred, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. Aborts and alignmen |


</details>


*PDF 跨页*：p1445-p1447（共 3 页）



### 4.91 `STZ2G` (C6.2.309)

**语义**：Store Allocation Tags, Zeroing stores an Allocation Tag to two Tag granules of memory, zeroing the associated data locations. The address used for the store is calculated from the base register and an immediate signed offset scaled by the Tag granule. The Allocation Tag is calculated from the Logical Address Tag in the source register.


**汇编模板**：
```
STZ2G <Xt|SP>, [<Xn|SP>], #<simm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 bits(64) offset = LSL(SignExtend(imm9, 64), LOG2_TAG_GRANULE); 
 boolean writeback = TRUE; 
 boolean postindex = TRUE; 
Pre-index
(FEAT_MTE)
Encoding
STZ2G <Xt|SP>, [<Xn|SP>, #<simm>]!
Decode for this encoding
 if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 bits(64) offset = LSL(SignExtend(imm9, 64), LOG2_TAG_GRANULE); 
 boolean writeback = TRUE; 
 boolean postindex = FALSE; 
Signed offset
(FEAT_MTE)
1
1
0
1
1
0
0
1
1
1
1
imm9
0
1
Xn
Xt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0
1
1
0
1
1
0
0
1
1
1
1
imm9
1
1
Xn
Xt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0
1
1
0
1
1
0
0
1
1
1
1
imm9
1
0
Xn
Xt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0

A64 Base Instruction Descriptions 
C6.2 Alphabetical list of A64 base instructions
C6-1448
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
ARM DDI 0487G.b
Non-Confidential
ID072021
Encoding
STZ2G <Xt|SP>, [<Xn|SP>{, #<simm>}]
Decode for this encoding
 if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 bits(64) offset = LSL(SignExtend(imm9, 64), LOG2_TAG_GRANULE); 
 boolean writeback = FALSE; 
 boolean postindex = FALSE;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt|SP>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Xt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Xn" field. |

| `<simm>` | Is the optional signed immediate offset, a multiple of 16 in the range -4096 to 4080, defaulting to 0 and encoded in the |


</details>


*PDF 跨页*：p1447-p1449（共 3 页）



### 4.92 `STZG` (C6.2.310)

**语义**：Store Allocation Tag, Zeroing stores an Allocation Tag to memory, zeroing the associated data location. The address used for the store is calculated from the base register and an immediate signed offset scaled by the Tag granule. The Allocation Tag is calculated from the Logical Address Tag in the source register.


**汇编模板**：
```
STZG <Xt|SP>, [<Xn|SP>], #<simm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 bits(64) offset = LSL(SignExtend(imm9, 64), LOG2_TAG_GRANULE); 
 boolean writeback = TRUE; 
 boolean postindex = TRUE; 
Pre-index
(FEAT_MTE)
Encoding
STZG <Xt|SP>, [<Xn|SP>, #<simm>]!
Decode for this encoding
 if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 bits(64) offset = LSL(SignExtend(imm9, 64), LOG2_TAG_GRANULE); 
 boolean writeback = TRUE; 
 boolean postindex = FALSE; 
Signed offset
(FEAT_MTE)
1
1
0
1
1
0
0
1
0
1
1
imm9
0
1
Xn
Xt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0
1
1
0
1
1
0
0
1
0
1
1
imm9
1
1
Xn
Xt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0
1
1
0
1
1
0
0
1
0
1
1
imm9
1
0
Xn
Xt
31 30 29 28 27 26 25 24 23 22 21 20
12 11 10 9
5
4
0

A64 Base Instruction Descriptions 
C6.2 Alphabetical list of A64 base instructions
C6-1450
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
ARM DDI 0487G.b
Non-Confidential
ID072021
Encoding
STZG <Xt|SP>, [<Xn|SP>{, #<simm>}]
Decode for this encoding
 if !HaveMTEExt() then UNDEFINED; 
 integer n = UInt(Xn); 
 integer t = UInt(Xt); 
 bits(64) offset = LSL(SignExtend(imm9, 64), LOG2_TAG_GRANULE); 
 boolean writeback = FALSE; 
 boolean postindex = FALSE;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt|SP>` | Is the 64-bit name of the general-purpose register to be transferred, encoded in the "Xt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Xn" field. |

| `<simm>` | Is the optional signed immediate offset, a multiple of 16 in the range -4096 to 4080, defaulting to 0 and encoded in the |


</details>


*PDF 跨页*：p1449-p1451（共 3 页）



### 4.93 `STZGM` (C6.2.311)

**语义**：Store Tag and Zero Multiple writes a naturally aligned block of N Allocation Tags and stores zero to the associated data locations, where the size of N is identified in DCZID_EL0.BS, and the Allocation Tag written to address A is taken from the source register bits<3:0>.


**汇编模板**：
```
STZGM <Xt>, [<Xn|SP>]
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


*PDF 跨页*：p1451-p1452（共 2 页）



### 4.94 `SUB (extended register)` (C6.2.312)

**语义**：Subtract (extended register) subtracts a sign or zero-extended register value, followed by an optional left shift amount, from a register value, and writes the result to the destination register. The argument that is extended from the <Rm> register can be a byte, halfword, word, or doubleword.


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

| `<m>` | Is the number [0-30] of the second general-purpose source register or the name ZR (31), encoded in the "Rm" field. sf 1  |


</details>


*PDF 跨页*：p1452-p1455（共 4 页）



### 4.95 `SUB (immediate)` (C6.2.313)

**语义**：Subtract (immediate) subtracts an optionally-shifted immediate value from a register value, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd|WSP>` | Is the 32-bit name of the destination general-purpose register or stack pointer, encoded in the "Rd" field. |

| `<Wn|WSP>` | Is the 32-bit name of the source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<Xd|SP>` | Is the 64-bit name of the destination general-purpose register or stack pointer, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<imm>` | Is an unsigned immediate, in the range 0 to 4095, encoded in the "imm12" field. |

| `<shift>` | Is the optional left shift to apply to the immediate, defaulting to LSL #0 and encoded in the "sh" field. It can have th |


</details>


*PDF 跨页*：p1455-p1457（共 3 页）



### 4.96 `SUB (shifted register)` (C6.2.314)

> 💡 **被以下指令作为别名使用**：`NEG (shifted register)`


**语义**：Subtract (shifted register) subtracts an optionally-shifted register value from a register value, and writes the result to the destination register.


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

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. Alias is preferred when NEG |


</details>


*PDF 跨页*：p1457-p1459（共 3 页）



### 4.97 `SUBG` (C6.2.315)

**语义**：Subtract with Tag subtracts an immediate value scaled by the Tag granule from the address in the source register, modifies the Logical Address Tag of the address using an immediate value, and writes the result to the destination register. Tags specified in GCR_EL1.Exclude are excluded from the possible outputs when modifying the Logical Address Tag.


**汇编模板**：
```
SUBG <Xd|SP>, <Xn|SP>, #<uimm6>, #<uimm4>
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


*PDF 跨页*：p1459-p1460（共 2 页）



### 4.98 `SUBP` (C6.2.316)

**语义**：Subtract Pointer subtracts the 56-bit address held in the second source register from the 56-bit address held in the first source register, sign-extends the result to 64-bits, and writes the result to the destination register.


**汇编模板**：
```
SUBP <Xd>, <Xn|SP>, <Xm|SP>
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
bits(64) operand1 = if n == 31 then SP[] else X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Xd" field. |

| `<Xn|SP>` | Is the 64-bit name of the first source general-purpose register or stack pointer, encoded in the "Xn" field. |

| `<Xm|SP>` | Is the 64-bit name of the second general-purpose source register or stack pointer, encoded in the "Xm" field. |


</details>


*PDF 跨页*：p1460-p1461（共 2 页）



### 4.99 `SUBPS` (C6.2.317)

> 💡 **被以下指令作为别名使用**：`CMPP`


**语义**：Subtract Pointer, setting Flags subtracts the 56-bit address held in the second source register from the 56-bit address held in the first source register, sign-extends the result to 64-bits, and writes the result to the destination register. It updates the condition flags based on the result of the subtraction.


**汇编模板**：
```
SUBPS <Xd>, <Xn|SP>, <Xm|SP>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveMTEExt() then UNDEFINED; 
 integer d = UInt(Xd); 
 integer n = UInt(Xn); 
 integer m = UInt(Xm); 
Alias conditions
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) operand1 = if n == 31 then SP[] else X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Xd" field. |

| `<Xn|SP>` | Is the 64-bit name of the first source general-purpose register or stack pointer, encoded in the "Xn" field. |

| `<Xm|SP>` | Is the 64-bit name of the second general-purpose source register or stack pointer, encoded in the "Xm" field. |


</details>


*PDF 跨页*：p1461-p1463（共 3 页）



### 4.100 `SUBS (extended register)` (C6.2.318)

> 💡 **被以下指令作为别名使用**：`CMP (extended register)`


**语义**：Subtract (extended register), setting flags, subtracts a sign or zero-extended register value, followed by an optional left shift amount, from a register value, and writes the result to the destination register. The argument that is extended from the <Rm> register can be a byte, halfword, word, or doubleword. It updates the condition flags based on the result.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) result;
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn|WSP>` | Is the 32-bit name of the first source general-purpose register or stack pointer, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn|SP>` | Is the 64-bit name of the first source general-purpose register or stack pointer, encoded in the "Rn" field. Alias is pr |


</details>


*PDF 跨页*：p1463-p1466（共 4 页）



### 4.101 `SUBS (immediate)` (C6.2.319)

> 💡 **被以下指令作为别名使用**：`CMP (immediate)`


**语义**：Subtract (immediate), setting flags, subtracts an optionally-shifted immediate value from a register value, and writes the result to the destination register. It updates the condition flags based on the result.


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


*PDF 跨页*：p1466-p1468（共 3 页）



### 4.102 `SUBS (shifted register)` (C6.2.320)

**语义**：Subtract (shifted register), setting flags, subtracts an optionally-shifted register value from a register value, and writes the result to the destination register. It updates the condition flags based on the result.


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

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. Alias is preferred when CMP |


</details>


*PDF 跨页*：p1468-p1470（共 3 页）



### 4.103 `SVC` (C6.2.321)

**语义**：Supervisor Call causes an exception to be taken to EL1.


**汇编模板**：
```
SVC #<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
AArch64.CheckForSVCTrap(imm16);
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<imm>` | Is a 16-bit unsigned immediate, in the range 0 to 65535, encoded in the "imm16" field. |


</details>


*PDF 跨页*：p1470-p1471（共 2 页）



### 4.104 `SWPB, SWPAB, SWPALB, SWPLB` (C6.2.322)

**语义**：Swap byte in memory atomically loads an 8-bit byte from a memory location, and stores the value held in a register back to the same memory location. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register to be stored, encoded in the "Rs" field. 0 0 1 1 1 0 0 0 A R 1 Rs 1 0 |


</details>


*PDF 跨页*：p1471-p1473（共 3 页）



### 4.105 `SWPH, SWPAH, SWPALH, SWPLH` (C6.2.323)

**语义**：Swap halfword in memory atomically loads a 16-bit halfword from a memory location, and stores the value held in a register back to the same memory location. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register to be stored, encoded in the "Rs" field. |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1473-p1475（共 3 页）



### 4.106 `SWP, SWPA, SWPAL, SWPL` (C6.2.324)

**语义**：Swap word or doubleword in memory atomically loads a 32-bit word or 64-bit doubleword from a memory location, and stores the value held in a register back to the same memory location. The value initially loaded from memory is returned in the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) address;
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Ws>` | Is the 32-bit name of the general-purpose register to be stored, encoded in the "Rs" field. |

| `<Wt>` | Is the 32-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xs>` | Is the 64-bit name of the general-purpose register to be stored, encoded in the "Rs" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose register to be loaded, encoded in the "Rt" field. |

| `<Xn|SP>` | Is the 64-bit name of the general-purpose base register or stack pointer, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1475-p1477（共 3 页）



### 4.107 `SXTB` (C6.2.325)

> ⚠️ **这是 `SBFM` 的别名**。底层编码与 `SBFM` 相同，只是汇编器接受不同写法。


**语义**：Signed Extend Byte extracts an 8-bit value from a register, sign-extends it to the size of the register, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SBFM gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1477-p1479（共 3 页）



### 4.108 `SXTH` (C6.2.326)

> ⚠️ **这是 `SBFM` 的别名**。底层编码与 `SBFM` 相同，只是汇编器接受不同写法。


**语义**：Sign Extend Halfword extracts a 16-bit value, sign-extends it to the size of the register, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SBFM gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1479-p1481（共 3 页）



### 4.109 `SXTW` (C6.2.327)

> ⚠️ **这是 `SBFM` 的别名**。底层编码与 `SBFM` 相同，只是汇编器接受不同写法。


**语义**：Sign Extend Word sign-extends a word to the size of the register, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SBFM gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1481-p1482（共 2 页）



### 4.110 `SYS` (C6.2.328)

**语义**：System instruction. For more information, see op0==0b01, cache maintenance, TLB maintenance, and address translation instructions on page C5-399 for the encodings of System instructions.


**汇编模板**：
```
SYS #<op1>, <Cn>, <Cm>, #<op2>{, <Xt>}
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
AArch64.CheckSystemAccess('01', op1, CRn, CRm, op2, Rt, L); 
  
 integer t = UInt(Rt); 
  
 integer sys_op1 = UInt(op1); 
 integer sys_op2 = UInt(op2); 
 integer sys_crn = UInt(CRn); 
 integer sys_crm = UInt(CRm); 
Alias conditions
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
AArch64.SysInstr(1, sys_op1, sys_crn, sys_crm, sys_op2, X[t]);
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<op1>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op1" field. |

| `<Cn>` | Is a name 'Cn', with 'n' in the range 0 to 15, encoded in the "CRn" field. |

| `<Cm>` | Is a name 'Cm', with 'm' in the range 0 to 15, encoded in the "CRm" field. |

| `<op2>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op2" field. Alias is preferred when AT CRn == '0111' |


</details>


*PDF 跨页*：p1482-p1484（共 3 页）



### 4.111 `SYSL` (C6.2.329)

**语义**：System instruction with result. For more information, see op0==0b01, cache maintenance, TLB maintenance, and address translation instructions on page C5-399 for the encodings of System instructions.


**汇编模板**：
```
SYSL <Xt>, #<op1>, <Cn>, <Cm>, #<op2>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
AArch64.CheckSystemAccess('01', op1, CRn, CRm, op2, Rt, L); 
  
 integer t = UInt(Rt); 
  
 integer sys_op1 = UInt(op1); 
 integer sys_op2 = UInt(op2); 
 integer sys_crn = UInt(CRn); 
 integer sys_crm = UInt(CRm);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
// No architecturally defined instructions here.
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rt" field. |

| `<op1>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op1" field. |

| `<Cn>` | Is a name 'Cn', with 'n' in the range 0 to 15, encoded in the "CRn" field. |

| `<Cm>` | Is a name 'Cm', with 'm' in the range 0 to 15, encoded in the "CRm" field. |

| `<op2>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op2" field. |


</details>


*PDF 跨页*：p1484-p1485（共 2 页）



### 4.112 `TBNZ` (C6.2.330)

**语义**：Test bit and Branch if Nonzero compares the value of a bit in a general-purpose register with zero, and conditionally branches to a label at a PC-relative offset if the comparison is not equal. It provides a hint that this is not a subroutine call or return. This instruction does not affect condition flags.


**汇编模板**：
```
TBNZ <R><t>, #<imm>, <label>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer t = UInt(Rt); 
  
 integer datasize = if b5 == '1' then 64 else 32; 
 integer bit_pos = UInt(b5:b40); 
 bits(64) offset = SignExtend(imm14:'00', 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand = X[t];
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<R>` | Is a width specifier, encoded in the "b5" field. It can have the following values: W when b5 = 0 X when b5 = 1 In assemb |

| `<t>` | Is the number [0-30] of the general-purpose register to be tested or the name ZR (31), encoded in the "Rt" field. |

| `<imm>` | Is the bit number to be tested, in the range 0 to 63, encoded in "b5:b40". |

| `<label>` | Is the program label to be conditionally branched to. Its offset from the address of this instruction, in the range +/-3 |


</details>


*PDF 跨页*：p1485-p1486（共 2 页）



### 4.113 `TBZ` (C6.2.331)

**语义**：Test bit and Branch if Zero compares the value of a test bit with zero, and conditionally branches to a label at a PC-relative offset if the comparison is equal. It provides a hint that this is not a subroutine call or return. This instruction does not affect condition flags.


**汇编模板**：
```
TBZ <R><t>, #<imm>, <label>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer t = UInt(Rt); 
  
 integer datasize = if b5 == '1' then 64 else 32; 
 integer bit_pos = UInt(b5:b40); 
 bits(64) offset = SignExtend(imm14:'00', 64);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) operand = X[t];
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<R>` | Is a width specifier, encoded in the "b5" field. It can have the following values: W when b5 = 0 X when b5 = 1 In assemb |

| `<t>` | Is the number [0-30] of the general-purpose register to be tested or the name ZR (31), encoded in the "Rt" field. |

| `<imm>` | Is the bit number to be tested, in the range 0 to 63, encoded in "b5:b40". |

| `<label>` | Is the program label to be conditionally branched to. Its offset from the address of this instruction, in the range +/-3 |


</details>


*PDF 跨页*：p1486-p1487（共 2 页）



### 4.114 `TLBI` (C6.2.332)

> ⚠️ **这是 `SYS` 的别名**。底层编码与 `SYS` 相同，只是汇编器接受不同写法。


**语义**：TLB Invalidate operation. For more information, see op0==0b01, cache maintenance, TLB maintenance, and address translation instructions on page C5-399.


**汇编模板**：
```
TLBI <tlbi_op>{, <Xt>}
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SYS gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<op1>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op1" field. |

| `<Cm>` | Is a name 'Cm', with 'm' in the range 0 to 15, encoded in the "CRm" field. |

| `<op2>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op2" field. |

| `<tlbi_op>` | Is a TLBI instruction name, as listed for the TLBI system instruction group, encoded in the "op1:CRm:op2" field. It can  |


</details>


*PDF 跨页*：p1487-p1490（共 4 页）



### 4.115 `TST (immediate)` (C6.2.334)

> ⚠️ **这是 `ANDS (immediate)` 的别名**。底层编码与 `ANDS (immediate)` 相同，只是汇编器接受不同写法。


**语义**：Test bits (immediate) , setting the condition flags and discarding the result : Rn AND imm This instruction is an alias of the ANDS (immediate) instruction. This means that: The encodings in this description are named to match the encodings of ANDS (immediate).


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of ANDS (immediate) gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<Xn>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rn" field. |

| `<imm>` | For the 32-bit variant: is the bitmask immediate, encoded in "imms:immr". For the 64-bit variant: is the bitmask immedia |


</details>


*PDF 跨页*：p1491-p1492（共 2 页）



### 4.116 `TST (shifted register)` (C6.2.335)

> ⚠️ **这是 `ANDS (shifted register)` 的别名**。底层编码与 `ANDS (shifted register)` 相同，只是汇编器接受不同写法。


**语义**：Test (shifted register) performs a bitwise AND operation on a register value and an optionally-shifted register value.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of ANDS (shifted register) gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（6 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wn>` | Is the 32-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |

| `<shift>` | Is the optional shift to be applied to the final source, defaulting to LSL and encoded in the "shift" field. It can have |

| `<amount>` | For the 32-bit variant: is the shift amount, in the range 0 to 31, defaulting to 0 and encoded in the "imm6" field. For  |


</details>


*PDF 跨页*：p1492-p1494（共 3 页）



### 4.117 `UBFIZ` (C6.2.336)

> ⚠️ **这是 `UBFM` 的别名**。底层编码与 `UBFM` 相同，只是汇编器接受不同写法。


**语义**：Unsigned Bitfield Insert in Zeros copies a bitfield of <width> bits from the least significant bits of the source register to bit position <lsb> of the destination register, setting the destination bits above and below the bitfield to zero.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of UBFM gives the operational pseudocode for this instruction.
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


*PDF 跨页*：p1494-p1496（共 3 页）



### 4.118 `UBFM` (C6.2.337)

**语义**：Unsigned Bitfield Move is usually accessed via one of its aliases, which are always preferred for disassembly.


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(datasize) src = X[n];
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


*PDF 跨页*：p1496-p1499（共 4 页）



### 4.119 `UBFX` (C6.2.338)

> ⚠️ **这是 `UBFM` 的别名**。底层编码与 `UBFM` 相同，只是汇编器接受不同写法。


**语义**：Unsigned Bitfield Extract copies a bitfield of <width> bits starting from bit position <lsb> in the source register to the least significant bits of the destination register, and sets destination bits above the bitfield to zero.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of UBFM gives the operational pseudocode for this instruction.
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


*PDF 跨页*：p1499-p1501（共 3 页）



### 4.120 `UDF` (C6.2.339)

**语义**：Permanently Undefined generates an Undefined Instruction exception (ESR_ELx.EC = 0b000000). The encodings for UDF used in this section are defined as permanently UNDEFINED in the Armv8-A architecture.


**汇编模板**：
```
UDF #<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// The imm16 field is ignored by hardware. 
 UNDEFINED;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
// No operation.
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<imm>` | is a 16-bit unsigned immediate, in the range 0 to 65535, encoded in the "imm16" field. The PE ignores the value of this  |


</details>


*PDF 跨页*：p1501-p1502（共 2 页）



### 4.121 `UDIV` (C6.2.340)

**语义**：Unsigned Divide divides an unsigned integer register value by another unsigned integer register value, and writes the result to the destination register. The condition flags are not affected.


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

| `<Xm>` | Is the 64-bit name of the second general-purpose source register, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p1502-p1503（共 2 页）



### 4.122 `UMADDL` (C6.2.341)

> 💡 **被以下指令作为别名使用**：`UMULL`


**语义**：Unsigned Multiply-Add Long multiplies two 32-bit register values, adds a 64-bit register value, and writes the result to the 64-bit destination register.


**汇编模板**：
```
UMADDL <Xd>, <Wn>, <Wm>, <Xa>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer d = UInt(Rd); 
 integer n = UInt(Rn); 
 integer m = UInt(Rm); 
 integer a = UInt(Ra); 
Alias conditions
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(32) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |

| `<Xa>` | Is the 64-bit name of the third general-purpose source register holding the addend, encoded in the "Ra" field. |


</details>


*PDF 跨页*：p1503-p1505（共 3 页）



### 4.123 `UMNEGL` (C6.2.342)

> ⚠️ **这是 `UMSUBL` 的别名**。底层编码与 `UMSUBL` 相同，只是汇编器接受不同写法。


**语义**：Unsigned Multiply-Negate Long multiplies two 32-bit register values, negates the product, and writes the result to the 64-bit destination register.


**汇编模板**：
```
UMNEGL <Xd>, <Wn>, <Wm>
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of UMSUBL gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p1505-p1506（共 2 页）



### 4.124 `UMSUBL` (C6.2.343)

> 💡 **被以下指令作为别名使用**：`UMNEGL`


**语义**：Unsigned Multiply-Subtract Long multiplies two 32-bit register values, subtracts the product from a 64-bit register value, and writes the result to the 64-bit destination register.


**汇编模板**：
```
UMSUBL <Xd>, <Wn>, <Wm>, <Xa>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer d = UInt(Rd); 
 integer n = UInt(Rn); 
 integer m = UInt(Rm); 
 integer a = UInt(Ra); 
Alias conditions
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(32) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |

| `<Xa>` | Is the 64-bit name of the third general-purpose source register holding the minuend, encoded in the "Ra" field. |


</details>


*PDF 跨页*：p1506-p1508（共 3 页）



### 4.125 `UMULH` (C6.2.344)

**语义**：Unsigned Multiply High multiplies two 64-bit register values, and writes bits[127:64] of the 128-bit result to the 64-bit destination register.


**汇编模板**：
```
UMULH <Xd>, <Xn>, <Xm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer d = UInt(Rd); 
 integer n = UInt(Rn); 
 integer m = UInt(Rm);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) operand1 = X[n];
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Xn>` | Is the 64-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Xm>` | Is the 64-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p1508-p1509（共 2 页）



### 4.126 `UMULL` (C6.2.345)

> ⚠️ **这是 `UMADDL` 的别名**。底层编码与 `UMADDL` 相同，只是汇编器接受不同写法。


**语义**：Unsigned Multiply Long multiplies two 32-bit register values, and writes the result to the 64-bit destination register.


**汇编模板**：
```
UMULL <Xd>, <Wn>, <Wm>
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of UMADDL gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（3 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the first general-purpose source register holding the multiplicand, encoded in the "Rn" field. |

| `<Wm>` | Is the 32-bit name of the second general-purpose source register holding the multiplier, encoded in the "Rm" field. |


</details>


*PDF 跨页*：p1509-p1510（共 2 页）



### 4.127 `UXTB` (C6.2.346)

> ⚠️ **这是 `UBFM` 的别名**。底层编码与 `UBFM` 相同，只是汇编器接受不同写法。


**语义**：Unsigned Extend Byte extracts an 8-bit value from a register, zero-extends it to the size of the register, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of UBFM gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1510-p1511（共 2 页）



### 4.128 `UXTH` (C6.2.347)

> ⚠️ **这是 `UBFM` 的别名**。底层编码与 `UBFM` 相同，只是汇编器接受不同写法。


**语义**：Unsigned Extend Halfword extracts a 16-bit value from a register, zero-extends it to the size of the register, and writes the result to the destination register.


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of UBFM gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Wd>` | Is the 32-bit name of the general-purpose destination register, encoded in the "Rd" field. |

| `<Wn>` | Is the 32-bit name of the general-purpose source register, encoded in the "Rn" field. |


</details>


*PDF 跨页*：p1511-p1512（共 2 页）



### 4.129 `WFE` (C6.2.348)

**语义**：Wait For Event is a hint instruction that indicates that the PE can enter a low-power state and remain there until a wakeup event occurs. Wakeup events include the event signaled as a result of executing the SEV instruction on any PE in the multiprocessor system. For more information, see Wait for Event mechanism and Send event on page D1-2536.


**汇编模板**：
```
WFE
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
Hint_WFE(-1, WFxType_WFE);
```

</details>


*PDF 跨页*：p1512-p1513（共 2 页）



### 4.130 `WFET` (C6.2.349)

**语义**：Wait For Event with Timeout is a hint instruction that indicates that the PE can enter a low-power state and remain there until either a local timeout event or a wakeup event occurs. Wakeup events include the event signaled as a result of executing the SEV instruction on any PE in the multiprocessor system. For more information, see Wait for Event mechanism and Send event on page D1-2536.


**汇编模板**：
```
WFET <Xt>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveFeatWFxT() then UNDEFINED; 
  
 integer d = UInt(Rd);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) operand = X[d];
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rd" field. |


</details>


*PDF 跨页*：p1513-p1514（共 2 页）



### 4.131 `WFI` (C6.2.350)

**语义**：Wait For Interrupt is a hint instruction that indicates that the PE can enter a low-power state and remain there until a wakeup event occurs. For more information, see Wait For Interrupt on page D1-2540.


**汇编模板**：
```
WFI
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
Hint_WFI(-1, WFxType_WFI);
```

</details>


*PDF 跨页*：p1514-p1515（共 2 页）



### 4.132 `WFIT` (C6.2.351)

**语义**：Wait For Interrupt with Timeout is a hint instruction that indicates that the PE can enter a low-power state and remain there until either a local timeout event or a wakeup event occurs. For more information, see Wait For Interrupt on page D1-2540.


**汇编模板**：
```
WFIT <Xt>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveFeatWFxT() then UNDEFINED; 
  
 integer d = UInt(Rd);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bits(64) operand = X[d];
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rd" field. |


</details>


*PDF 跨页*：p1515-p1516（共 2 页）



### 4.133 `XAFLAG` (C6.2.352)

**语义**：Convert floating-point condition flags from external format to Arm format. This instruction converts the state of the PSTATE.{N,Z,C,V} flags from an alternative representation required by some software to a form representing the result of an Arm floating-point scalar compare instruction.


**汇编模板**：
```
XAFLAG
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if !HaveFlagFormatExt() then UNDEFINED;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
bit N = NOT(PSTATE.C) AND NOT(PSTATE.Z);
```

</details>


*PDF 跨页*：p1516-p1517（共 2 页）



### 4.134 `XPACD, XPACI, XPACLRI` (C6.2.353)

**语义**：Strip Pointer Authentication Code. This instruction removes the pointer authentication code from an address. The address is in the specified general-purpose register for XPACI and XPACD, and is in LR for XPACLRI.


**汇编模板**：
```
XPACLRI
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
integer d = 30; 
 boolean data = FALSE;
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xd>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rd" field. 1 1 0 1 1 0 1 0 1 1 0 0 0 0 0 |


</details>


*PDF 跨页*：p1517-p1519（共 3 页）



### 4.135 `YIELD` (C6.2.354)

**语义**：YIELD is a hint instruction. Software with a multithreading capability can use a YIELD instruction to indicate to the PE that it is performing a task, for example a spin-lock, that could be swapped out to improve overall system performance. The PE can use this hint to suspend and resume multiple software threads if it supports the capability.


**汇编模板**：
```
YIELD
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
Hint_Yield();
```

</details>


*PDF 跨页*：p1519-p1522（共 4 页）




---

📌 **下一步**：回到 [`a64_base_overview.md`](./a64_base_overview.md) 看其他首字母，或 [`isa_reference/README.md`](./README.md) 看其他扩展。
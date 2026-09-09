# A64 Base Instruction Set Overview — 354 条基础指令分类地图


> **生成日期**：2026-06-29  
> **PDF 源版本**：ARM DDI 0487G.b (2021-07)  
> **数据来源**：[`isa_instructions_v7.json`](https://example.com) — 755 条指令 / 36 FEAT，PyMuPDF 全自动提取  
> **飞腾实测平台**：D3000M (FTC862) @ 2.5 GHz, ARMv8.4-A

> 本文件是 [`isa_reference/`](./README.md) 系列之一。所有指令基于 ARM ARM DDI 0487G.b (2021-07)。

---

## 目录

- [0. 一句话](#0-一句话)

- [1. 现象：为什么需要它？](#1-现象为什么需要它)

- [2. 引入版本 & 飞腾状态](#2-引入版本--飞腾状态)

- [3. 指令清单总表（350 条）](#3-指令清单总表)

- [4. 每条指令详解](#4-每条指令详解按章节顺序)

  - 4.1 `ADC`
  - 4.2 `ADR`
  - 4.3 `LDADDH`
  - 4.4 `LDADD`
  - 4.5 `LDAPR`
  - 4.6 `LDAPRB`
  - 4.7 `LDAPRH`
  - 4.8 `LDAPUR`
  - ...（共 350 条）
- [5. 实测代码](#5-实测代码)

- [6. 性能预期](#6-性能预期飞腾-d3000m--25-ghz)

- [7. 缺陷与陷阱](#7-缺陷与陷阱)

- [8. 进一步阅读](#8-进一步阅读)


---

## 0. 一句话

A64 指令集全景图：354 条基础指令按 8 大类组织 —— 任何 ARM64 代码的根基。


---
## 1. 现象：为什么需要它？

A64 是 ARMv8-A 的 64-bit 指令集，所有指令固定 **32-bit 编码**（无 RVC 类似变长）。

**指令分类（按 ARM ARM C3.1 overview）**：

1. **Branch/Exception/System** (~30 条)
   - 无条件分支：B/BL/BR/BLR/RET
   - 条件分支：B.cond/CBZ/CBNZ/TBZ/TBNZ
   - 异常：SVC/HVC/SMC/BRK/DCPS
   - 系统：MSR/MRS/ISB/DMB/DSB

2. **Loads and Stores** (~80 条)
   - 普通：LDR/STR (register/immediate)
   - 多寄存器：LDP/STP/LDNP/STNP
   - 同步：LDXR/STXR/LDAR/STLR (v8.0 baseline LL/SC)
   - SIMD load：LD1/LD2/LD3/LD4 (struct load)

3. **Data processing - immediate** (~20 条)
   - 算术：ADD/SUB (imm)
   - 位操作：AND/ORR/EOR (imm)
   - 移位：LSL/LSR/ASR (imm)
   - 地址：ADR/ADRP

4. **Data processing - register** (~50 条)
   - 算术：ADD/SUB/MUL/UDIV/SDIV
   - 逻辑：AND/ORR/EOR/BIC/ORN
   - 移位：LSL/LSR/ASR/ROR/LSLV
   - 比较：CMP/CMN/TST
   - 条件：CSEL/CSINC/CNEG
   - 位域：BFM/UBFM/SBFM/BFI/BFXIL/EXTR

5. **Data processing - SIMD/FP** (~150 条，详见 v8.0_asimd.md)

6. **System** (~50 条)
   - Cache：DC (CIVAC/IVAC/CVAC/ZVA/...)
   - TLB：TLBI (ALL/ASID/VA/...)
   - Address Translation：AT
   - Instruction Cache：IC (IVAU/IALlu/...)
   - Barriers：DMB/DSB/ISB/PRFB


---
## 2. 引入版本 & 飞腾状态

**版本**：ARMv8.0-A mandatory（基线）。


**飞腾 D3000M 状态**：

飞腾 D3000M 全部支持（v8.0 是 mandatory baseline）。


**杀手级应用**：所有 ARM64 代码


---
## 3. 指令清单总表（350 条）

| 助记符 | 变体 | 章节号 | ARM 页 | PDF 页 | 别名 / 被别名 |

|--------|------|--------|--------|--------|---------------|

| `ADC` | - | C6.2.1 | C6-876 | p876 |  |

| `ADR` | - | C6.2.10 | C6-895 | p895 |  |

| `LDADDH, LDADDAH, LDADDALH, LDADDLH` | - | C6.2.100 | C6-1043 | p1043 | 被别名→STADDH |

| `LDADD, LDADDA, LDADDAL, LDADDL` | - | C6.2.101 | C6-1045 | p1045 | 被别名→STADD |

| `LDAPR` | - | C6.2.102 | C6-1048 | p1048 |  |

| `LDAPRB` | - | C6.2.103 | C6-1050 | p1050 |  |

| `LDAPRH` | - | C6.2.104 | C6-1052 | p1052 |  |

| `LDAPUR` | - | C6.2.105 | C6-1054 | p1054 |  |

| `LDAPURB` | - | C6.2.106 | C6-1056 | p1056 |  |

| `LDAPURH` | - | C6.2.107 | C6-1058 | p1058 |  |

| `LDAPURSB` | - | C6.2.108 | C6-1060 | p1060 |  |

| `LDAPURSH` | - | C6.2.109 | C6-1062 | p1062 |  |

| `ADRP` | - | C6.2.11 | C6-896 | p896 |  |

| `LDAPURSW` | - | C6.2.110 | C6-1064 | p1064 |  |

| `LDAR` | - | C6.2.111 | C6-1066 | p1066 |  |

| `LDARB` | - | C6.2.112 | C6-1068 | p1068 |  |

| `LDARH` | - | C6.2.113 | C6-1069 | p1069 |  |

| `LDAXP` | - | C6.2.114 | C6-1070 | p1070 |  |

| `LDAXR` | - | C6.2.115 | C6-1072 | p1072 |  |

| `LDAXRB` | - | C6.2.116 | C6-1074 | p1074 |  |

| `LDAXRH` | - | C6.2.117 | C6-1075 | p1075 |  |

| `LDCLRB, LDCLRAB, LDCLRALB, LDCLRLB` | - | C6.2.118 | C6-1076 | p1076 | 被别名→STCLRB |

| `LDCLRH, LDCLRAH, LDCLRALH, LDCLRLH` | - | C6.2.119 | C6-1078 | p1078 | 被别名→STCLRH |

| `AND (immediate)` | immediate | C6.2.12 | C6-897 | p897 |  |

| `LDCLR, LDCLRA, LDCLRAL, LDCLRL` | - | C6.2.120 | C6-1080 | p1080 | 被别名→STCLR |

| `LDEORB, LDEORAB, LDEORALB, LDEORLB` | - | C6.2.121 | C6-1083 | p1083 | 被别名→STEORB |

| `LDEORH, LDEORAH, LDEORALH, LDEORLH` | - | C6.2.122 | C6-1085 | p1085 | 被别名→STEORH |

| `LDEOR, LDEORA, LDEORAL, LDEORL` | - | C6.2.123 | C6-1087 | p1087 | 被别名→STEOR |

| `LDG` | - | C6.2.124 | C6-1090 | p1090 |  |

| `LDGM` | - | C6.2.125 | C6-1091 | p1091 |  |

| `LDLARB` | - | C6.2.126 | C6-1093 | p1093 |  |

| `LDLARH` | - | C6.2.127 | C6-1094 | p1094 |  |

| `LDLAR` | - | C6.2.128 | C6-1095 | p1095 |  |

| `LDNP` | - | C6.2.129 | C6-1097 | p1097 |  |

| `AND (shifted register)` | shifted register | C6.2.13 | C6-899 | p899 |  |

| `LDP` | - | C6.2.130 | C6-1099 | p1099 |  |

| `LDPSW` | - | C6.2.131 | C6-1103 | p1103 |  |

| `LDR (immediate)` | immediate | C6.2.132 | C6-1106 | p1106 |  |

| `LDR (literal)` | literal | C6.2.133 | C6-1109 | p1109 |  |

| `LDR (register)` | register | C6.2.134 | C6-1111 | p1111 |  |

| `LDRAA, LDRAB` | - | C6.2.135 | C6-1113 | p1113 |  |

| `LDRB (immediate)` | immediate | C6.2.136 | C6-1115 | p1115 |  |

| `LDRB (register)` | register | C6.2.137 | C6-1118 | p1118 |  |

| `LDRH (immediate)` | immediate | C6.2.138 | C6-1120 | p1120 |  |

| `LDRH (register)` | register | C6.2.139 | C6-1123 | p1123 |  |

| `ANDS (immediate)` | immediate | C6.2.14 | C6-901 | p901 | 被别名→TST (immediate) |

| `LDRSB (immediate)` | immediate | C6.2.140 | C6-1125 | p1125 |  |

| `LDRSB (register)` | register | C6.2.141 | C6-1129 | p1129 |  |

| `LDRSH (immediate)` | immediate | C6.2.142 | C6-1131 | p1131 |  |

| `LDRSH (register)` | register | C6.2.143 | C6-1135 | p1135 |  |

| `LDRSW (immediate)` | immediate | C6.2.144 | C6-1137 | p1137 |  |

| `LDRSW (literal)` | literal | C6.2.145 | C6-1140 | p1140 |  |

| `LDRSW (register)` | register | C6.2.146 | C6-1141 | p1141 |  |

| `LDSETB, LDSETAB, LDSETALB, LDSETLB` | - | C6.2.147 | C6-1143 | p1143 | 被别名→STSETB |

| `LDSETH, LDSETAH, LDSETALH, LDSETLH` | - | C6.2.148 | C6-1145 | p1145 | 被别名→STSETH |

| `LDSET, LDSETA, LDSETAL, LDSETL` | - | C6.2.149 | C6-1147 | p1147 | 被别名→STSET |

| `ANDS (shifted register)` | shifted register | C6.2.15 | C6-903 | p903 | 被别名→TST (shifted register) |

| `LDSMAXB, LDSMAXAB, LDSMAXALB, LDSMAXLB` | - | C6.2.150 | C6-1150 | p1150 | 被别名→STSMAXB |

| `LDSMAXH, LDSMAXAH, LDSMAXALH, LDSMAXLH` | - | C6.2.151 | C6-1152 | p1152 | 被别名→STSMAXH |

| `LDSMAX, LDSMAXA, LDSMAXAL, LDSMAXL` | - | C6.2.152 | C6-1154 | p1154 | 被别名→STSMAX |

| `LDSMINB, LDSMINAB, LDSMINALB, LDSMINLB` | - | C6.2.153 | C6-1157 | p1157 | 被别名→STSMINB |

| `LDSMINH, LDSMINAH, LDSMINALH, LDSMINLH` | - | C6.2.154 | C6-1159 | p1159 | 被别名→STSMINH |

| `LDSMIN, LDSMINA, LDSMINAL, LDSMINL` | - | C6.2.155 | C6-1161 | p1161 | 被别名→STSMIN |

| `LDTR` | - | C6.2.156 | C6-1164 | p1164 |  |

| `LDTRB` | - | C6.2.157 | C6-1166 | p1166 |  |

| `LDTRH` | - | C6.2.158 | C6-1168 | p1168 |  |

| `LDTRSB` | - | C6.2.159 | C6-1170 | p1170 |  |

| `ASR (register)` | register | C6.2.16 | C6-905 | p905 | alias→ASRV |

| `LDTRSH` | - | C6.2.160 | C6-1172 | p1172 |  |

| `LDTRSW` | - | C6.2.161 | C6-1174 | p1174 |  |

| `LDUMAXB, LDUMAXAB, LDUMAXALB, LDUMAXLB` | - | C6.2.162 | C6-1176 | p1176 | 被别名→STUMAXB |

| `LDUMAXH, LDUMAXAH, LDUMAXALH, LDUMAXLH` | - | C6.2.163 | C6-1178 | p1178 | 被别名→STUMAXH |

| `LDUMAX, LDUMAXA, LDUMAXAL, LDUMAXL` | - | C6.2.164 | C6-1180 | p1180 | 被别名→STUMAX |

| `LDUMINB, LDUMINAB, LDUMINALB, LDUMINLB` | - | C6.2.165 | C6-1183 | p1183 | 被别名→STUMINB |

| `LDUMINH, LDUMINAH, LDUMINALH, LDUMINLH` | - | C6.2.166 | C6-1185 | p1185 | 被别名→STUMINH |

| `LDUMIN, LDUMINA, LDUMINAL, LDUMINL` | - | C6.2.167 | C6-1187 | p1187 | 被别名→STUMIN |

| `LDUR` | - | C6.2.168 | C6-1190 | p1190 |  |

| `LDURB` | - | C6.2.169 | C6-1192 | p1192 |  |

| `ASR (immediate)` | immediate | C6.2.17 | C6-907 | p907 | alias→SBFM |

| `LDURH` | - | C6.2.170 | C6-1193 | p1193 |  |

| `LDURSB` | - | C6.2.171 | C6-1194 | p1194 |  |

| `LDURSH` | - | C6.2.172 | C6-1196 | p1196 |  |

| `LDURSW` | - | C6.2.173 | C6-1198 | p1198 |  |

| `LDXP` | - | C6.2.174 | C6-1199 | p1199 |  |

| `LDXR` | - | C6.2.175 | C6-1201 | p1201 |  |

| `LDXRB` | - | C6.2.176 | C6-1203 | p1203 |  |

| `LDXRH` | - | C6.2.177 | C6-1204 | p1204 |  |

| `LSL (register)` | register | C6.2.178 | C6-1205 | p1205 | alias→LSLV |

| `LSL (immediate)` | immediate | C6.2.179 | C6-1207 | p1207 | alias→UBFM |

| `ASRV` | - | C6.2.18 | C6-909 | p909 | 被别名→ASR (register) |

| `LSLV` | - | C6.2.180 | C6-1209 | p1209 | 被别名→LSL (register) |

| `LSR (register)` | register | C6.2.181 | C6-1211 | p1211 | alias→LSRV |

| `LSR (immediate)` | immediate | C6.2.182 | C6-1213 | p1213 | alias→UBFM |

| `LSRV` | - | C6.2.183 | C6-1215 | p1215 | 被别名→LSR (register) |

| `MADD` | - | C6.2.184 | C6-1217 | p1217 | 被别名→MUL |

| `MNEG` | - | C6.2.185 | C6-1219 | p1219 | alias→MSUB |

| `MOV (to/from SP)` | to/from SP | C6.2.186 | C6-1221 | p1221 | alias→ADD (immediate) |

| `MOV (inverted wide immediate)` | inverted wide immediate | C6.2.187 | C6-1222 | p1222 | alias→MOVN |

| `MOV (wide immediate)` | wide immediate | C6.2.188 | C6-1224 | p1224 | alias→MOVZ |

| `MOV (bitmask immediate)` | bitmask immediate | C6.2.189 | C6-1226 | p1226 | alias→ORR (immediate) |

| `AT` | - | C6.2.19 | C6-911 | p911 | alias→SYS |

| `MOV (register)` | register | C6.2.190 | C6-1228 | p1228 | alias→ORR (shifted register) |

| `MOVK` | - | C6.2.191 | C6-1230 | p1230 |  |

| `MOVN` | - | C6.2.192 | C6-1232 | p1232 | 被别名→MOV (inverted wide immediate) |

| `MOVZ` | - | C6.2.193 | C6-1234 | p1234 | 被别名→MOV (wide immediate) |

| `MRS` | - | C6.2.194 | C6-1236 | p1236 |  |

| `MSR (immediate)` | immediate | C6.2.195 | C6-1237 | p1237 |  |

| `MSR (register)` | register | C6.2.196 | C6-1240 | p1240 |  |

| `MSUB` | - | C6.2.197 | C6-1241 | p1241 | 被别名→MNEG |

| `MUL` | - | C6.2.198 | C6-1243 | p1243 | alias→MADD |

| `MVN` | - | C6.2.199 | C6-1244 | p1244 | alias→ORN (shifted register) |

| `ADCS` | - | C6.2.2 | C6-878 | p878 |  |

| `AUTDA, AUTDZA` | - | C6.2.20 | C6-913 | p913 |  |

| `NEG (shifted register)` | shifted register | C6.2.200 | C6-1246 | p1246 | alias→SUB (shifted register) |

| `NEGS` | - | C6.2.201 | C6-1248 | p1248 | alias→SUBS (shifted register) |

| `NGC` | - | C6.2.202 | C6-1250 | p1250 | alias→SBC |

| `NGCS` | - | C6.2.203 | C6-1252 | p1252 | alias→SBCS |

| `NOP` | - | C6.2.204 | C6-1254 | p1254 |  |

| `ORN (shifted register)` | shifted register | C6.2.205 | C6-1255 | p1255 | 被别名→MVN |

| `ORR (immediate)` | immediate | C6.2.206 | C6-1257 | p1257 | 被别名→MOV (bitmask immediate) |

| `ORR (shifted register)` | shifted register | C6.2.207 | C6-1259 | p1259 | 被别名→MOV (register) |

| `PACDA, PACDZA` | - | C6.2.208 | C6-1261 | p1261 |  |

| `PACDB, PACDZB` | - | C6.2.209 | C6-1262 | p1262 |  |

| `AUTDB, AUTDZB` | - | C6.2.21 | C6-914 | p914 |  |

| `PACGA` | - | C6.2.210 | C6-1263 | p1263 |  |

| `PACIA, PACIA1716, PACIASP, PACIAZ, PACIZA` | - | C6.2.211 | C6-1264 | p1264 |  |

| `PACIB, PACIB1716, PACIBSP, PACIBZ, PACIZB` | - | C6.2.212 | C6-1267 | p1267 |  |

| `PRFM (immediate)` | immediate | C6.2.213 | C6-1270 | p1270 |  |

| `PRFM (literal)` | literal | C6.2.214 | C6-1272 | p1272 |  |

| `PRFM (register)` | register | C6.2.215 | C6-1274 | p1274 |  |

| `PRFUM` | - | C6.2.216 | C6-1276 | p1276 |  |

| `PSSBB` | - | C6.2.218 | C6-1279 | p1279 | alias→DSB |

| `RBIT` | - | C6.2.219 | C6-1280 | p1280 |  |

| `AUTIA, AUTIA1716, AUTIASP, AUTIAZ, AUTIZA` | - | C6.2.22 | C6-915 | p915 |  |

| `RET` | - | C6.2.220 | C6-1282 | p1282 |  |

| `RETAA, RETAB` | - | C6.2.221 | C6-1283 | p1283 |  |

| `REV` | - | C6.2.222 | C6-1284 | p1284 |  |

| `REV16` | - | C6.2.223 | C6-1286 | p1286 |  |

| `REV32` | - | C6.2.224 | C6-1288 | p1288 |  |

| `REV64` | - | C6.2.225 | C6-1290 | p1290 |  |

| `RMIF` | - | C6.2.226 | C6-1291 | p1291 |  |

| `ROR (immediate)` | immediate | C6.2.227 | C6-1292 | p1292 | alias→EXTR |

| `ROR (register)` | register | C6.2.228 | C6-1294 | p1294 | alias→RORV |

| `RORV` | - | C6.2.229 | C6-1296 | p1296 | 被别名→ROR (register) |

| `AUTIB, AUTIB1716, AUTIBSP, AUTIBZ, AUTIZB` | - | C6.2.23 | C6-917 | p917 |  |

| `SB` | - | C6.2.230 | C6-1298 | p1298 |  |

| `SBC` | - | C6.2.231 | C6-1299 | p1299 | 被别名→NGC |

| `SBCS` | - | C6.2.232 | C6-1301 | p1301 | 被别名→NGCS |

| `SBFIZ` | - | C6.2.233 | C6-1303 | p1303 | alias→SBFM |

| `SBFM` | - | C6.2.234 | C6-1305 | p1305 |  |

| `SBFX` | - | C6.2.235 | C6-1308 | p1308 | alias→SBFM |

| `SDIV` | - | C6.2.236 | C6-1310 | p1310 |  |

| `SETF8, SETF16` | - | C6.2.237 | C6-1311 | p1311 |  |

| `SEV` | - | C6.2.238 | C6-1312 | p1312 |  |

| `SEVL` | - | C6.2.239 | C6-1313 | p1313 |  |

| `AXFLAG` | - | C6.2.24 | C6-919 | p919 |  |

| `SMADDL` | - | C6.2.240 | C6-1314 | p1314 | 被别名→SMULL |

| `SMC` | - | C6.2.241 | C6-1316 | p1316 |  |

| `SMNEGL` | - | C6.2.242 | C6-1317 | p1317 | alias→SMSUBL |

| `SMSUBL` | - | C6.2.243 | C6-1318 | p1318 | 被别名→SMNEGL |

| `SMULH` | - | C6.2.244 | C6-1320 | p1320 |  |

| `SMULL` | - | C6.2.245 | C6-1321 | p1321 | alias→SMADDL |

| `SSBB` | - | C6.2.246 | C6-1322 | p1322 | alias→DSB |

| `ST2G` | - | C6.2.247 | C6-1323 | p1323 |  |

| `ST64B` | - | C6.2.248 | C6-1325 | p1325 |  |

| `ST64BV` | - | C6.2.249 | C6-1326 | p1326 |  |

| `ST64BV0` | - | C6.2.250 | C6-1328 | p1328 |  |

| `STADDB, STADDLB` | - | C6.2.251 | C6-1330 | p1330 |  |

| `STADDH, STADDLH` | - | C6.2.252 | C6-1332 | p1332 |  |

| `STADD, STADDL` | - | C6.2.253 | C6-1334 | p1334 |  |

| `STCLRB, STCLRLB` | - | C6.2.254 | C6-1336 | p1336 |  |

| `STCLRH, STCLRLH` | - | C6.2.255 | C6-1338 | p1338 |  |

| `STCLR, STCLRL` | - | C6.2.256 | C6-1340 | p1340 |  |

| `STEORB, STEORLB` | - | C6.2.257 | C6-1342 | p1342 |  |

| `STEORH, STEORLH` | - | C6.2.258 | C6-1344 | p1344 |  |

| `STEOR, STEORL` | - | C6.2.259 | C6-1346 | p1346 |  |

| `STG` | - | C6.2.260 | C6-1348 | p1348 |  |

| `STGM` | - | C6.2.261 | C6-1350 | p1350 |  |

| `STGP` | - | C6.2.262 | C6-1351 | p1351 |  |

| `STLLRB` | - | C6.2.263 | C6-1354 | p1354 |  |

| `STLLRH` | - | C6.2.264 | C6-1355 | p1355 |  |

| `STLLR` | - | C6.2.265 | C6-1356 | p1356 |  |

| `STLR` | - | C6.2.266 | C6-1358 | p1358 |  |

| `STLRB` | - | C6.2.267 | C6-1360 | p1360 |  |

| `STLRH` | - | C6.2.268 | C6-1361 | p1361 |  |

| `STLUR` | - | C6.2.269 | C6-1362 | p1362 |  |

| `BFC` | - | C6.2.27 | C6-922 | p922 | alias→BFM |

| `STLURB` | - | C6.2.270 | C6-1364 | p1364 |  |

| `STLURH` | - | C6.2.271 | C6-1366 | p1366 |  |

| `STLXP` | - | C6.2.272 | C6-1368 | p1368 |  |

| `STLXR` | - | C6.2.273 | C6-1371 | p1371 |  |

| `STLXRB` | - | C6.2.274 | C6-1374 | p1374 |  |

| `STLXRH` | - | C6.2.275 | C6-1376 | p1376 |  |

| `STNP` | - | C6.2.276 | C6-1378 | p1378 |  |

| `STP` | - | C6.2.277 | C6-1380 | p1380 |  |

| `STR (immediate)` | immediate | C6.2.278 | C6-1383 | p1383 |  |

| `STR (register)` | register | C6.2.279 | C6-1386 | p1386 |  |

| `BFI` | - | C6.2.28 | C6-924 | p924 | alias→BFM |

| `STRB (immediate)` | immediate | C6.2.280 | C6-1388 | p1388 |  |

| `STRB (register)` | register | C6.2.281 | C6-1391 | p1391 |  |

| `STRH (immediate)` | immediate | C6.2.282 | C6-1393 | p1393 |  |

| `STRH (register)` | register | C6.2.283 | C6-1396 | p1396 |  |

| `STSETB, STSETLB` | - | C6.2.284 | C6-1398 | p1398 |  |

| `STSETH, STSETLH` | - | C6.2.285 | C6-1400 | p1400 |  |

| `STSET, STSETL` | - | C6.2.286 | C6-1402 | p1402 |  |

| `STSMAXB, STSMAXLB` | - | C6.2.287 | C6-1404 | p1404 |  |

| `STSMAXH, STSMAXLH` | - | C6.2.288 | C6-1406 | p1406 |  |

| `STSMAX, STSMAXL` | - | C6.2.289 | C6-1408 | p1408 |  |

| `BFM` | - | C6.2.29 | C6-926 | p926 |  |

| `STSMINB, STSMINLB` | - | C6.2.290 | C6-1410 | p1410 |  |

| `STSMINH, STSMINLH` | - | C6.2.291 | C6-1412 | p1412 |  |

| `STSMIN, STSMINL` | - | C6.2.292 | C6-1414 | p1414 |  |

| `STTR` | - | C6.2.293 | C6-1416 | p1416 |  |

| `STTRB` | - | C6.2.294 | C6-1418 | p1418 |  |

| `STTRH` | - | C6.2.295 | C6-1420 | p1420 |  |

| `STUMAXB, STUMAXLB` | - | C6.2.296 | C6-1422 | p1422 |  |

| `STUMAXH, STUMAXLH` | - | C6.2.297 | C6-1424 | p1424 |  |

| `STUMAX, STUMAXL` | - | C6.2.298 | C6-1426 | p1426 |  |

| `STUMINB, STUMINLB` | - | C6.2.299 | C6-1428 | p1428 |  |

| `ADD (extended register)` | extended register | C6.2.3 | C6-880 | p880 |  |

| `BFXIL` | - | C6.2.30 | C6-928 | p928 | alias→BFM |

| `STUMINH, STUMINLH` | - | C6.2.300 | C6-1430 | p1430 |  |

| `STUMIN, STUMINL` | - | C6.2.301 | C6-1432 | p1432 |  |

| `STUR` | - | C6.2.302 | C6-1434 | p1434 |  |

| `STURB` | - | C6.2.303 | C6-1436 | p1436 |  |

| `STURH` | - | C6.2.304 | C6-1437 | p1437 |  |

| `STXP` | - | C6.2.305 | C6-1438 | p1438 |  |

| `STXR` | - | C6.2.306 | C6-1441 | p1441 |  |

| `STXRB` | - | C6.2.307 | C6-1443 | p1443 |  |

| `STXRH` | - | C6.2.308 | C6-1445 | p1445 |  |

| `STZ2G` | - | C6.2.309 | C6-1447 | p1447 |  |

| `BIC (shifted register)` | shifted register | C6.2.31 | C6-930 | p930 |  |

| `STZG` | - | C6.2.310 | C6-1449 | p1449 |  |

| `STZGM` | - | C6.2.311 | C6-1451 | p1451 |  |

| `SUB (extended register)` | extended register | C6.2.312 | C6-1452 | p1452 |  |

| `SUB (immediate)` | immediate | C6.2.313 | C6-1455 | p1455 |  |

| `SUB (shifted register)` | shifted register | C6.2.314 | C6-1457 | p1457 | 被别名→NEG (shifted register) |

| `SUBG` | - | C6.2.315 | C6-1459 | p1459 |  |

| `SUBP` | - | C6.2.316 | C6-1460 | p1460 |  |

| `SUBPS` | - | C6.2.317 | C6-1461 | p1461 | 被别名→CMPP |

| `SUBS (extended register)` | extended register | C6.2.318 | C6-1463 | p1463 | 被别名→CMP (extended register) |

| `SUBS (immediate)` | immediate | C6.2.319 | C6-1466 | p1466 | 被别名→CMP (immediate) |

| `BICS (shifted register)` | shifted register | C6.2.32 | C6-932 | p932 |  |

| `SUBS (shifted register)` | shifted register | C6.2.320 | C6-1468 | p1468 |  |

| `SVC` | - | C6.2.321 | C6-1470 | p1470 |  |

| `SWPB, SWPAB, SWPALB, SWPLB` | - | C6.2.322 | C6-1471 | p1471 |  |

| `SWPH, SWPAH, SWPALH, SWPLH` | - | C6.2.323 | C6-1473 | p1473 |  |

| `SWP, SWPA, SWPAL, SWPL` | - | C6.2.324 | C6-1475 | p1475 |  |

| `SXTB` | - | C6.2.325 | C6-1477 | p1477 | alias→SBFM |

| `SXTH` | - | C6.2.326 | C6-1479 | p1479 | alias→SBFM |

| `SXTW` | - | C6.2.327 | C6-1481 | p1481 | alias→SBFM |

| `SYS` | - | C6.2.328 | C6-1482 | p1482 |  |

| `SYSL` | - | C6.2.329 | C6-1484 | p1484 |  |

| `BL` | - | C6.2.33 | C6-934 | p934 |  |

| `TBNZ` | - | C6.2.330 | C6-1485 | p1485 |  |

| `TBZ` | - | C6.2.331 | C6-1486 | p1486 |  |

| `TLBI` | - | C6.2.332 | C6-1487 | p1487 | alias→SYS |

| `TST (immediate)` | immediate | C6.2.334 | C6-1491 | p1491 | alias→ANDS (immediate) |

| `TST (shifted register)` | shifted register | C6.2.335 | C6-1492 | p1492 | alias→ANDS (shifted register) |

| `UBFIZ` | - | C6.2.336 | C6-1494 | p1494 | alias→UBFM |

| `UBFM` | - | C6.2.337 | C6-1496 | p1496 |  |

| `UBFX` | - | C6.2.338 | C6-1499 | p1499 | alias→UBFM |

| `UDF` | - | C6.2.339 | C6-1501 | p1501 |  |

| `BLR` | - | C6.2.34 | C6-935 | p935 |  |

| `UDIV` | - | C6.2.340 | C6-1502 | p1502 |  |

| `UMADDL` | - | C6.2.341 | C6-1503 | p1503 | 被别名→UMULL |

| `UMNEGL` | - | C6.2.342 | C6-1505 | p1505 | alias→UMSUBL |

| `UMSUBL` | - | C6.2.343 | C6-1506 | p1506 | 被别名→UMNEGL |

| `UMULH` | - | C6.2.344 | C6-1508 | p1508 |  |

| `UMULL` | - | C6.2.345 | C6-1509 | p1509 | alias→UMADDL |

| `UXTB` | - | C6.2.346 | C6-1510 | p1510 | alias→UBFM |

| `UXTH` | - | C6.2.347 | C6-1511 | p1511 | alias→UBFM |

| `WFE` | - | C6.2.348 | C6-1512 | p1512 |  |

| `WFET` | - | C6.2.349 | C6-1513 | p1513 |  |

| `BLRAA, BLRAAZ, BLRAB, BLRABZ` | - | C6.2.35 | C6-936 | p936 |  |

| `WFI` | - | C6.2.350 | C6-1514 | p1514 |  |

| `WFIT` | - | C6.2.351 | C6-1515 | p1515 |  |

| `XAFLAG` | - | C6.2.352 | C6-1516 | p1516 |  |

| `XPACD, XPACI, XPACLRI` | - | C6.2.353 | C6-1517 | p1517 |  |

| `YIELD` | - | C6.2.354 | C6-1519 | p1519 |  |

| `BR` | - | C6.2.36 | C6-938 | p938 |  |

| `BRAA, BRAAZ, BRAB, BRABZ` | - | C6.2.37 | C6-939 | p939 |  |

| `BRK` | - | C6.2.38 | C6-941 | p941 |  |

| `BTI` | - | C6.2.39 | C6-942 | p942 |  |

| `ADD (immediate)` | immediate | C6.2.4 | C6-883 | p883 | 被别名→MOV (to/from SP) |

| `CASB, CASAB, CASALB, CASLB` | - | C6.2.40 | C6-944 | p944 |  |

| `CASH, CASAH, CASALH, CASLH` | - | C6.2.41 | C6-946 | p946 |  |

| `CASP, CASPA, CASPAL, CASPL` | - | C6.2.42 | C6-948 | p948 |  |

| `CAS, CASA, CASAL, CASL` | - | C6.2.43 | C6-951 | p951 |  |

| `CBNZ` | - | C6.2.44 | C6-954 | p954 |  |

| `CBZ` | - | C6.2.45 | C6-955 | p955 |  |

| `CCMN (immediate)` | immediate | C6.2.46 | C6-956 | p956 |  |

| `CCMN (register)` | register | C6.2.47 | C6-958 | p958 |  |

| `CCMP (immediate)` | immediate | C6.2.48 | C6-960 | p960 |  |

| `CCMP (register)` | register | C6.2.49 | C6-962 | p962 |  |

| `ADD (shifted register)` | shifted register | C6.2.5 | C6-885 | p885 |  |

| `CFINV` | - | C6.2.50 | C6-964 | p964 |  |

| `CFP` | - | C6.2.51 | C6-965 | p965 | alias→SYS |

| `CINC` | - | C6.2.52 | C6-966 | p966 | alias→CSINC |

| `CINV` | - | C6.2.53 | C6-968 | p968 | alias→CSINV |

| `CLREX` | - | C6.2.54 | C6-970 | p970 |  |

| `CLS` | - | C6.2.55 | C6-971 | p971 |  |

| `CLZ` | - | C6.2.56 | C6-973 | p973 |  |

| `CMN (extended register)` | extended register | C6.2.57 | C6-974 | p974 | alias→ADDS (extended register) |

| `CMN (immediate)` | immediate | C6.2.58 | C6-976 | p976 | alias→ADDS (immediate) |

| `CMN (shifted register)` | shifted register | C6.2.59 | C6-978 | p978 | alias→ADDS (shifted register) |

| `ADDG` | - | C6.2.6 | C6-887 | p887 |  |

| `CMP (extended register)` | extended register | C6.2.60 | C6-980 | p980 | alias→SUBS (extended register) |

| `CMP (immediate)` | immediate | C6.2.61 | C6-982 | p982 | alias→SUBS (immediate) |

| `CMP (shifted register)` | shifted register | C6.2.62 | C6-984 | p984 | alias→SUBS (shifted register) |

| `CMPP` | - | C6.2.63 | C6-986 | p986 | alias→SUBPS |

| `CNEG` | - | C6.2.64 | C6-987 | p987 | alias→CSNEG |

| `CPP` | - | C6.2.65 | C6-989 | p989 | alias→SYS |

| `CRC32B, CRC32H, CRC32W, CRC32X` | - | C6.2.66 | C6-990 | p990 |  |

| `CRC32CB, CRC32CH, CRC32CW, CRC32CX` | - | C6.2.67 | C6-992 | p992 |  |

| `CSDB` | - | C6.2.68 | C6-994 | p994 |  |

| `CSEL` | - | C6.2.69 | C6-995 | p995 |  |

| `ADDS (extended register)` | extended register | C6.2.7 | C6-888 | p888 | 被别名→CMN (extended register) |

| `CSET` | - | C6.2.70 | C6-997 | p997 | alias→CSINC |

| `CSETM` | - | C6.2.71 | C6-999 | p999 | alias→CSINV |

| `CSINC` | - | C6.2.72 | C6-1001 | p1001 |  |

| `CSINV` | - | C6.2.73 | C6-1003 | p1003 |  |

| `CSNEG` | - | C6.2.74 | C6-1005 | p1005 | 被别名→CNEG |

| `DC` | - | C6.2.75 | C6-1007 | p1007 | alias→SYS |

| `DCPS1` | - | C6.2.76 | C6-1009 | p1009 |  |

| `DCPS2` | - | C6.2.77 | C6-1010 | p1010 |  |

| `DCPS3` | - | C6.2.78 | C6-1011 | p1011 |  |

| `DGH` | - | C6.2.79 | C6-1012 | p1012 |  |

| `ADDS (immediate)` | immediate | C6.2.8 | C6-891 | p891 | 被别名→CMN (immediate) |

| `DMB` | - | C6.2.80 | C6-1013 | p1013 |  |

| `DRPS` | - | C6.2.81 | C6-1015 | p1015 |  |

| `DSB` | - | C6.2.82 | C6-1016 | p1016 |  |

| `DVP` | - | C6.2.83 | C6-1019 | p1019 | alias→SYS |

| `EON (shifted register)` | shifted register | C6.2.84 | C6-1020 | p1020 |  |

| `EOR (immediate)` | immediate | C6.2.85 | C6-1022 | p1022 |  |

| `EOR (shifted register)` | shifted register | C6.2.86 | C6-1024 | p1024 |  |

| `ERET` | - | C6.2.87 | C6-1026 | p1026 |  |

| `ERETAA, ERETAB` | - | C6.2.88 | C6-1027 | p1027 |  |

| `ESB` | - | C6.2.89 | C6-1028 | p1028 |  |

| `ADDS (shifted register)` | shifted register | C6.2.9 | C6-893 | p893 | 被别名→CMN (shifted register) |

| `EXTR` | - | C6.2.90 | C6-1029 | p1029 | 被别名→ROR (immediate) |

| `GMI` | - | C6.2.91 | C6-1031 | p1031 |  |

| `HINT` | - | C6.2.92 | C6-1032 | p1032 |  |

| `HLT` | - | C6.2.93 | C6-1034 | p1034 |  |

| `HVC` | - | C6.2.94 | C6-1035 | p1035 |  |

| `IC` | - | C6.2.95 | C6-1036 | p1036 | alias→SYS |

| `IRG` | - | C6.2.96 | C6-1037 | p1037 |  |

| `ISB` | - | C6.2.97 | C6-1039 | p1039 |  |

| `LD64B` | - | C6.2.98 | C6-1040 | p1040 |  |

| `LDADDB, LDADDAB, LDADDALB, LDADDLB` | - | C6.2.99 | C6-1041 | p1041 | 被别名→STADDB |


---
## 4. 每条指令详解（按首字母拆分）

> 由于本扩展指令较多（350 条），按助记符首字母拆分为 3 个文件：

- [a64_base_a_to_g.md](./a64_base_a_to_g.md) — 首字母 A-G (89 条)
- [a64_base_h_to_p.md](./a64_base_h_to_p.md) — 首字母 H-P (126 条)
- [a64_base_q_to_z.md](./a64_base_q_to_z.md) — 首字母 Q-Z (135 条)

---

## 5. 实测代码

详见：../Lab01_ISA与汇编/src/c_to_asm.c (反汇编对照)


---
## 6. 性能预期（飞腾 D3000M @ 2.5 GHz）

| 指令类 | latency | throughput | 备注 |
|--------|---------|-----------|------|
| ADD/SUB reg | 1 cyc | 4/cyc | 4-wide ALU |
| MUL | 3 cyc | 1/cyc | |
| SDIV/UDIV | ~20 cyc | 0.05/cyc | 非流水线 |
| LDR (L1 hit) | 4 cyc | 2/cyc | 2 load ports |
| LDP | 4 cyc | 1/cyc | |
| LDR (L2 hit) | ~10 cyc | 2/cyc | |
| STR | 0 cyc | 1/cyc | store buffer |
| B/BL | 1 cyc | 1/cyc | |
| BR/BLR | 2-3 cyc | 1/cyc | indirect |
| RET | 1-2 cyc | 1/cyc | RAS prediction


---
## 7. 缺陷与陷阱

1. **A64 没有 MOV 端即指令**：MOV 实际是 ORR/XOR 的 alias
2. **LDR/STR 立即数范围有限**：[-256, 255] 或 [0, 16380] step，远偏移要 ADD 计算地址
3. **没有 push/pop**：用 STP/LDP 替代
4. **条件码不是 ARMv7 那种**：只有 NZCV 4 个 flag
5. **CMP 是 SUBS 的 alias**：丢弃结果的减法


---
## 8. 进一步阅读

- ARM ARM §C3 (overview) / §C4 (encoding) / §C6 (descriptions)
- *ARM64 Assembly Language* (Whaley)
- ARM Learn the Architecture: A64


---
📌 **下一步**：回到 [`isa_reference/README.md`](./README.md) 看其他扩展。

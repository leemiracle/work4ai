# CPU 分支预测精读：从 Bimodal 到 TAGE

> 参照：Patterson Hennessy Appendix C / csapp Ch4(流水线) / 龙芯/LA464
>
> csdiy 对应：csapp Ch4 + tinycpu/pipeline.py + csapp Ch5(优化)

---

## 一、为什么需要分支预测

### 控制冒险（Control Hazard）

```
流水线执行到条件跳转（je/jne/jg...）:
  IF: [je loop]
  ID: 译码 → 是条件跳转
  EX: 需要计算跳转条件 → 还要 1 cycle

→ 后续指令该不该取？
  如果跳转: IF 需要从新地址取指 → 之前取的 2-3 条指令作废（pipeline flush）
  如果不跳: 继续顺序执行

延迟 = 2-3 cycles（branch penalty）
```

### 统计：20% 的指令是分支

```
平均每 5 条指令有 1 条分支
如果每次 flush 3 cycles → 30% 的性能损失

→ 分支预测器的准确率每提高 1% → IPC 提高 ~1%
```

---

## 二、静态预测（最简单）

### 预测不跳转

```
总是假设分支不跳（继续顺序执行）
准确率: ~60%（因为很多循环跳回开头 → 实际跳转概率 > 不跳）
```

### BTFN（Backward Taken, Forward Not-Taken）

```
向后跳（如 loop）→ 预测跳转（循环大概率继续）
向前跳（如 if-else）→ 预测不跳转
准确率: ~65-75%
```

---

## 三、动态预测（1-bit）

### 1-bit 预测器

```
每个分支地址记录 1 bit: 上次是否跳转

状态:
  0 → 预测不跳
  1 → 预测跳转

更新: 每次执行后用实际结果更新

问题:
  循环执行 99 次 → 第 100 次退出时预测错误
  下次进入循环 → 第 1 次又预测错误（上次退出了）
  → 1-bit 预测器对"基本总是跳"的循环有 2 次错误/迭代
```

---

## 四、2-bit 预测器（Bimodal）

### 四状态

```
      不跳转          不跳转
  00 (SN) ───→ 01 (WN) ───→ 00
    ↑                       ↓
    |        跳转            |
    |    ┌───←───┐          |
    ↓    ↓        |          ↓
  11 (ST) ←─── 10 (WT) ←──┘
      跳转          跳转

ST = Strongly Taken (11): 强预测跳转
WT = Weakly Taken   (10): 弱预测跳转
WN = Weakly Not     (01): 弱预测不跳
SN = Strongly Not   (00): 强预测不跳

→ 需要 2 次连续错误才翻转预测 → 对"99%跳"的循环只错 1 次
```

### 实现（GShare/Bimodal）

```
Pattern History Table (PHT):
  索引 = PC[lower_bits] XOR GlobalHistory[lower_bits]
  PHT[index] = 2-bit saturating counter

→ GShare: 用全局历史和 PC 做异或 → 对相关分支更好
```

---

## 五、TAGE（TAgged GEometric，当前最快）

### 核心：多历史长度表

```
T0: 2-bit bimodal（基线）
T1: 历史长度 = 2    的 tagged predictor
T2: 历史长度 = 4
T3: 历史长度 = 8
T4: 历史长度 = 16
T5: 历史长度 = 64   （几何级数增长的历史长度）

预测流程:
  ① 从最长历史表开始查找
  ② 如果有匹配的 tag → 用该表预测（长历史 → 更准确）
  ③ 如果都没匹配 → 用 T0 bimodal（基线）

→ 长历史捕获循环/周期模式
→ 短历史捕获局部相关
→ 几何分布平衡覆盖率和精度
```

### 效果

```
2-bit Bimodal:  ~93% 准确率
GShare:         ~95%
TAGE:           ~97-98%
感知器 (Perceptron): ~96-97%
```

---

## 六、分支目标预测（BTB）

### 问题

```
即使知道"会跳转" → 跳到哪里？（目标地址）

间接跳转 jmp *%rax → 目标地址动态变化
→ 需要 Branch Target Buffer (BTB) 缓存: PC → 目标地址
```

### Return Address Stack (RAS)

```
函数返回 ret → 目标是调用栈的下一个地址

RAS = 硬件栈:
  call → push(返回地址)
  ret  → pop() → 预测目标

准确率: ~99%（因为 call/ret 天然配对）
```

---

## 七、和 tinycpu 的交叉

你的 `tinycpu/pipeline.py` 实现了基础流水线但没有分支预测：

```python
# 当前：跳转直接更新 PC → 下一个 cycle 从新 PC 取指
# 没有预测 → flush 浪费 cycles

# 如果加分支预测:
def if_stage(self):
    instr = self.program[self.pc]
    if instr.opcode == OpCode.JXX:
        predicted_taken = self.branch_predictor.predict(self.pc)
        if predicted_taken:
            self.next_pc = instr.imm  # 预测跳转
            self.speculative = True    # 标记为投机执行
    # ...
```

---

## 八、分支预测安全问题：Spectre

```
Spectre V1 (Bounds Check Bypass):
  if (x < array_size):
      y = array[x]          ← 正常访问
      temp = cache[array2[y*4096]]  ← 投机执行（即使 x >= size）

  → 投机执行的内存读取 → 污染了 cache
  → 攻击者通过 cache timing 侧信道 → 推断 y 的值

→ 根因: 分支预测 + 投机执行 → 读取了不该读的数据
→ 解法: Speculative Store Bypass 禁用 / Retpoline / LFENCE
```

---

## 九、一句话总结

> 分支预测 = 用历史信息猜测跳转方向 → 避免流水线 flush。
>
> 2-bit Bimodal = 经典方案（93%）。TAGE = 当前最强（98%）。
>
> **Spectre = 分支预测的安全代价** → 投机执行泄露敏感数据。

---

*配套：[tinycpu/pipeline.py](../projects/tinycpu/pipeline.py) | [csapp Ch4](../notes/csapp-程序员视角.md) | [csapp Ch5(优化)](../notes/perf-程序员视角-定位与优化.md)*

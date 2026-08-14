# 激活 LLM 能力手段 · 真实对比实验

> 模型：`glm-4-flash` (智谱 BigModel) | 时间：2026-08-04 22:25:27 
> 测试题：3 个工人 3 天能刷 3 面墙。9 个工人 9 天能刷几面墙？
> 正确答案：**27**（推理：3人3天3面 → 1人1天 1/3 面 → 9人9天 = 9×9×(1/3) = 27）

## 结果汇总

| # | 手段 | 答案 | 正确? | 耗时 | tokens |
|---|---|---|---|---|---|
| 1 | Zero-shot baseline | 81 | ❌ | 11.3s | 178 |
| 2 | Zero-shot CoT | 81 | ❌ | 10.3s | 226 |
| 3 | Few-shot CoT（给推理示例） | 27 | ✅ | 8.6s | 233 |
| 4 | Expert Persona（数学教授） | 9 | ❌ | 17.5s | 543 |
| 5 | Emotional Prompting | 9 | ❌ | 10.5s | 172 |
| 6 | Plan-and-Solve | 27 | ✅ | 11.2s | 267 |
| 7 | Self-Critique（自我反驳） | 1 | ❌ | 16.0s | 328 |
| 8 | Take a Deep Breath | 27 | ✅ | 14.2s | 254 |
| 9 | Self-Consistency (N=5, T=0.7) | 27 | ✅ | 63.1s | — |

**正确率**：4/9 = **44%**

## 各手段详细回答

### Zero-shot baseline → 81 ❌

**Prompt**：
```
3 个工人 3 天能刷 3 面墙。9 个工人 9 天能刷几面墙？
```

**回答**：
```
首先，我们知道3个工人3天能刷3面墙。这意味着每个工人每天刷的墙面积是相同的。

我们可以设每个工人每天刷的墙面积为1个单位。那么，3个工人3天刷的墙面积就是3个单位乘以3天，等于9个单位。

现在，我们要计算9个工人9天能刷多少面墙。由于每个工人每天刷的墙面积是1个单位，那么9个工人每天刷的墙面积就是9个单位。

接下来，我们计算9个工人9天刷的墙面积。9个单位乘以9天等于81个单位。

所以，9个工人9天能刷81面墙。
```

### Zero-shot CoT → 81 ❌

**Prompt**：
```
3 个工人 3 天能刷 3 面墙。9 个工人 9 天能刷几面墙？

Let's think step by step.
```

**回答**：
```
要解决这个问题，我们可以先找出每个工人每天刷墙的效率，然后用这个效率来计算9个工人在9天内能刷多少面墙。

首先，我们知道3个工人在3天内能刷3面墙。这意味着每个工人每天刷墙的效率是：

3面墙 / (3个工人 * 3天) = 3面墙 / 9工人天 = 1/3面墙/工人天

这意味着每个工人每天可以刷1/3面墙。

现在，我们要计算9个工人在9天内能刷多少面墙。我们可以用每个工人每天刷墙的效率来计算：

(1/3面墙/工人天) * 9个工人 * 9天 = 1面墙/工人天 * 9工人 * 9天 = 81面墙

所以，9个工人在9天内能刷81面墙。
```

### Few-shot CoT（给推理示例） → 27 ✅

**Prompt**：
```
例子：2 个工人 2 天刷 2 面墙，4 个工人 4 天能刷几面墙？
推理：2人2天刷2面 → 1人2天刷1面 → 1人1天刷0.5面 → 4人4天刷 4×4×0.5 = 8 面。
答案：8

现在答：3 个工人 3 天能刷 3 面墙。9 个工人 9 天能刷几面墙？
推理：
```

**回答**：
```
3人3天刷3面墙，可以推出1人3天刷1面墙，进一步可以得出1人1天刷0.333...（即1/3）面墙。

现在，我们要计算9个工人9天能刷几面墙。

根据上面的推理，9个工人1天能刷9 × 0.333... = 3面墙。

因此，9个工人9天能刷的墙数为：
9天 × 3面/天 = 27面墙。

答案：27面墙。
```

### Expert Persona（数学教授） → 9 ❌

**Prompt**：
```
You are a math professor with 20 years of teaching experience. Solve carefully:

3 个工人 3 天能刷 3 面墙。9 个工人 9 天能刷几面墙？
```

**回答**：
```
Alright class, let's break this down carefully. This is a classic work-rate problem, and the key is to find the rate at which the workers can paint.

**1. Understand the given information:**
*   We have 3 workers.
*   They work for 3 days.
*   In that time, they complete 3 walls.

**2. Calculate the rate of work for one worker:**
*   Think about what the 3 workers are doing together over the 3 days. They are painting 3 walls.
*   How much work does one worker do in those 3 days? Since they are working together, we can think of the total work as being divided among them.
*   In 3 days, 1 worker paints 3 walls / 3 workers = 1 wall.
*   So, the rate of one worker is 1 wall per 3 days.

**3. Calculate the total work rate for 9 workers:**
*   If 1 worker paints 1 wall in 3 days, then 9 workers, working simultaneously, will paint 9 times as much in the same amount of time.
*   Total rate = 9 workers * (1 wall / 3 days/worker) = 9 walls / 3 days.
*   Simplifying this, the 9 workers have a combined rate of 3 walls per day.

**4. Calculate the total number of walls painted in 9 days:**
*   We know that 9 workers can paint 3 walls per day.
*   We want to know how many walls they can paint in 9 days.
*   Total walls = (Rate of 9 workers) * (Number of days)
*   Total walls = (3 walls/day) * (9 days)
*   Total walls = 27 walls

**Answer:**
9 个工人 9 天能刷 **27** 面墙。

*(Alternatively, using the formula: (Number of workers 1) / (Number of walls 1) = (Number of workers 2) / (Number of walls 2)*

```

### Emotional Prompting → 9 ❌

**Prompt**：
```
3 个工人 3 天能刷 3 面墙。9 个工人 9 天能刷几面墙？

This is very important to my career. Please be careful and precise.
```

**回答**：
```
这个问题可以通过比例来解决。

首先，我们知道3个工人3天能刷3面墙。这意味着每个工人每天能刷1面墙（因为3个工人×3天=9个工人天，9个工人天刷3面墙，所以1个工人天刷1面墙）。

现在，我们要计算9个工人9天能刷多少面墙。根据前面的比例，9个工人天能刷9面墙（因为每个工人天刷1面墙，所以9个工人天刷9面墙）。

所以，9个工人9天能刷9面墙。
```

### Plan-and-Solve → 27 ✅

**Prompt**：
```
Let's first understand the problem and devise a plan. Then carry out the plan to solve it.

问题：3 个工人 3 天能刷 3 面墙。9 个工人 9 天能刷几面墙？
```

**回答**：
```
首先，我们需要理解问题中的关系和规律。

问题中给出的信息是：
- 3个工人3天能刷3面墙。

从这个信息中，我们可以得出以下结论：
- 3个工人每天能刷1面墙（因为3面墙需要3天，所以每天刷1面墙）。
- 也就是说，每个工人每天能刷1/3面墙。

现在，我们要解决的问题是：
- 9个工人9天能刷几面墙？

根据我们刚才得出的结论，我们可以这样计算：
- 9个工人每天能刷的墙面积是3个工人每天能刷的墙面积的3倍（因为工人数量增加了3倍）。
- 所以，9个工人每天能刷3面墙。

接下来，我们计算9天能刷多少面墙：
- 9个工人每天刷3面墙，那么9天就能刷3面墙/天 × 9天 = 27面墙。

所以，9个工人9天能刷27面墙。
```

### Self-Critique（自我反驳） → 1 ❌

**Prompt**：
```
3 个工人 3 天能刷 3 面墙。9 个工人 9 天能刷几面墙？

先给出你的初步答案和推理。然后扮演 devil's advocate，给出 2 个最强反驳，最后给最终修正答案。
```

**回答**：
```
初步答案和推理：
如果3个工人3天能刷3面墙，那么每个工人每天刷墙的效率是1面墙/（3人×3天）= 1/9面墙/人/天。因此，9个工人每天能刷的墙是9人×（1/9面墙/人/天）= 1面墙/天。既然是9个工人，那么9天就能刷9面墙。

反驳1：
这个推理假设每个工人的工作效率是恒定的，但实际上，工人可能会因为疲劳、休息或其他因素导致效率下降。因此，9个工人在9天内可能不会每天都保持相同的效率。

反驳2：
这个推理还假设所有工人都在同一时间工作，但实际上，可能存在一些工人早退或迟到，或者在某些时间段内工作人数不足。这也会影响总的工作量。

最终修正答案：
考虑到上述反驳，我们可以得出结论，9个工人在9天内能刷的墙的数量可能不会是精确的9面墙。实际刷的墙的数量可能会因为工人的效率波动和工作时间的不确定性而有所减少。因此，一个更合理的估计可能是9个工人在9天内能刷的墙的数量在7到9面墙之间，具体取决于工人的实际工作效率和工作时间的稳定性。
```

### Take a Deep Breath → 27 ✅

**Prompt**：
```
Take a deep breath and work through this step by step.

3 个工人 3 天能刷 3 面墙。9 个工人 9 天能刷几面墙？
```

**回答**：
```
首先，我们需要确定每个工人每天能刷多少面墙。

根据题目，3个工人3天能刷3面墙。我们可以计算出每个工人每天刷墙的数量：

3个工人3天刷3面墙，那么1个工人3天能刷1面墙。

既然1个工人3天能刷1面墙，那么1个工人每天能刷的墙数为：
1面墙 / 3天 = 1/3面墙/天。

现在我们知道了每个工人每天能刷1/3面墙。

接下来，我们要计算9个工人9天能刷多少面墙。

9个工人每天能刷的墙数为：
9个工人 * 1/3面墙/天 = 3面墙/天。

既然9个工人每天能刷3面墙，那么9个工人9天能刷的墙数为：
3面墙/天 * 9天 = 27面墙。

所以，9个工人9天能刷27面墙。
```

### Self-Consistency (N=5, T=0.7) → 27 ✅

**Prompt**：
```
3 个工人 3 天能刷 3 面墙。9 个工人 9 天能刷几面墙？

Let's think step by step.
```

**回答**：
```
[27] | [27] | [27] | [9] | [27]
```

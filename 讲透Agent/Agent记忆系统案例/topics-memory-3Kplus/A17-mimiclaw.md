# A-17 `memovai/mimiclaw`（5.7K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\memovai__mimiclaw
> C（ESP-IDF/FreeRTOS，96 个文件）｜MIT ｜ 一句话定位：跑在 ESP32-S3（16MB Flash + 8MB PSRAM，约 $5-10 板子）上的无 OS 硬件 Agent，经 Telegram/飞书/WebSocket 对话，LLM 在云端（Anthropic），记忆全在本地闪存
> 代表**记忆系统的极端资源受限形态**：无检索、无嵌入、无数据库——"记忆=闪存上的 Markdown 文件 + 拼进系统提示的固定预算文本"。

## 1. 架构总览（目录地图，标出核心目录的职责）

- `main/mimi.c` — 总装：NVS/SPIFFS/消息总线初始化，各服务启动（含 PSRAM 打印，`mimi.c:117-118`）。
- `main/agent/` — `agent_loop.c`（FreeRTOS 任务 + ReAct 循环，362 行）、`context_builder.c`（每回合重建系统提示=记忆注入点，103 行）。
- `main/memory/` — `memory_store.c`（长期记忆+每日笔记读写，107 行）、`session_mgr.c`（JSONL 会话历史环形截断，165 行）。
- `main/bus/` — FreeRTOS 队列消息总线（队列长 16，`mimi_config.h:97`）：入站消息→agent，出站→通道。
- `main/channels/`（telegram/feishu 双 IM bot）、`main/gateway/ws_server.c`（WS 端口 18789，最多 4 客户端，`mimi_config.h:127-128`）。
- `main/llm/llm_proxy.c` — 云 LLM 代理（Anthropic/OpenAI 双协议，默认 claude-opus-4-5，`mimi_config.h:86-89`），流缓冲 32KB 放 PSRAM（`llm_proxy.c:94`）。
- `main/proxy/http_proxy.c` — HTTP 代理支持（国内直连 Anthropic 的现实工程需求，`mimi_config.h:28-33` 代理秘密项）。
- `main/cli/serial_cli.c` — 串口 CLI（heap_info 查看 PSRAM，`serial_cli.c:243-244`）。
- `main/onboard/` — WiFi 配网 captive portal（AP 前缀 MimiClaw-，`mimi_config.h:158-162`）。
- `main/heartbeat/`（HEARTBEAT.md 定时扫描自主唤醒，165 行）、`main/cron/`（cron.json 持久化定时任务，最多 16 个，`mimi_config.h:114-116`）。
- `main/tools/` — 文件/GPIO/cron/web_search/time 工具注册表（tool_registry.c 分发）；`main/skills/` — Markdown 技能加载（160 行）。
- `spiffs_data/` — 构建期烧入闪存的初始记忆资产（`CMakeLists.txt:9` spiffs_create_partition_image FLASH_IN_PROJECT）：config/SOUL.md、USER.md、memory/MEMORY.md、skills/*.md；`partitions.csv` 定义闪存分区。

**闪存布局**（`partitions.csv:1-8`）：
- 16MB Flash = nvs 24KB（键值秘密）+ 双 OTA app 分区（各 2MB）+ **SPIFFS 数据分区 0xBD0000（约 12MB，记忆唯一持久层）** + coredump 64KB。
- 上下文缓冲预算（`mimi_config.h:110-111`）：`MIMI_CONTEXT_BUF_SIZE = 16KB`（整个系统提示含全部注入记忆）、`MIMI_SESSION_MAX_MSGS = 20`。
- PSRAM 8MB Octal 80MHz（`sdkconfig.defaults.esp32s3:11-16`）；大缓冲全部 heap_caps_calloc(MALLOC_CAP_SPIRAM)（`agent_loop.c:176-178`），内部 RAM 预留 96KB（sdkconfig:16）。

## 2. 记忆机制深读（本笔记核心）

### 2.1 记忆的形态：三类闪存文件 + 一类 JSONL
1. **长期记忆 MEMORY.md**——`/spiffs/memory/MEMORY.md`（`mimi_config.h:107`）：
   - 整读整写：`memory_read_long_term` 一次性 fread 进调用方缓冲（`memory_store.c:30-42`）；
   - `memory_write_long_term` fopen("w") **全量覆写**（`memory_store.c:44-55`）；
   - 初始内容为空模板"(empty - MimiClaw will write memories here as it learns)"（`spiffs_data/memory/MEMORY.md:1-3`）。
2. **每日笔记 daily/<YYYY-MM-DD>.md**——事件日志形态：
   - `memory_append_today` 按当天日期生成路径（本地时区 PST8PDT，`mimi_config.h:83`；`memory_store.c:12-20`），追加一行 note，文件不存在则写 `# 日期` 头（`memory_store.c:57-79`）；
   - 读取 `memory_read_recent(buf, size, days)` 从今天往前逐日拼接，日与日之间插 `\n---\n`（`memory_store.c:81-107`）；
   - **"检索"就是按日期倒序全量拼接，没有任何索引**。
3. **人格/用户画像 SOUL.md、USER.md**——只读注入（`mimi_config.h:108-109`，烧录自 `spiffs_data/config/`；SOUL.md 定义性格与价值观"Accuracy over speed / User privacy and safety"，`spiffs_data/config/SOUL.md:1-11`）。
4. **会话历史 sessions/tg_<chat_id>.jsonl**——每 chat 一个文件，每行 `{"role","content","ts"}`（`session_mgr.c:14-51`）；按通道前缀 tg_ 命名（feishu 会话另建）。
5. **辅助记忆文件**：HEARTBEAT.md（待办任务）、cron.json（定时任务）、skills/*.md（程序性记忆，见 2.3）。

### 2.2 写入/抽取管线：谁触发、prompt 怎么说
- **写入者是云端 LLM 自己**，通过 write_file/edit_file 工具直接改闪存文件；固件不做任何抽取/蒸馏——抽取逻辑全部写在系统提示里（`context_builder.c:59-69`）：
  - "学到用户信息（名字/偏好/习惯/上下文）立即写 MEMORY.md"；
  - "值得记的事 append 到当日 daily note"；
  - "写前先 read_file MEMORY.md 再 edit_file 防丢内容"；
  - "写 daily 前用 get_current_time 拿日期"（无内部时钟）；
  - "保持精炼、不要倾倒原始对话"；"**主动保存，无需用户要求**"。
- 会话写入发生在回合成功后：只存 user 原文 + 最终 assistant 文本，**中间工具调用/工具结果不落盘**（`agent_loop.c:277-287`）。
- HEARTBEAT.md 是特殊"任务记忆"：每 30 分钟 FreeRTOS 定时器扫描（`mimi_config.h:118`），逐行启发式判断是否有未完成任务——跳过空行/`#` 标题/已完成 checkbox `- [x]`，发现可执行行才注入一条 system:heartbeat 消息唤醒 agent（`heartbeat.c:31-73`），提示词"Read /spiffs/HEARTBEAT.md and follow any instructions... 无事回复 HEARTBEAT_OK"（`heartbeat.c:16-18`）——无事不唤醒，省一次 LLM 调用。
- cron 任务由 LLM 通过 cron_add 工具创建（`context_builder.c:47-49`），持久化到 SPIFFS 的 cron.json，到期把预置消息推入总线触发 agent 回合（`cron_service.c:17-23`）；目标通道/ChatID 缺失时 sanitize 回 system:cron（`cron_service.c:25-51`）。

### 2.3 检索策略：无检索，只有"预算内固定窗口注入"
- **每回合重建系统提示**（`agent_loop.c:196`）= 六段拼装（`context_builder.c:32-99`）：
  1. 静态说明（身份/工具清单/GPIO/记忆规则/技能说明，硬编码 C 字符串，`context_builder.c:32-73`）；
  2. SOUL.md（## Personality）+ USER.md（## User Info）只读注入（`context_builder.c:76-77`）；
  3. **MEMORY.md 全文**（4KB 栈缓冲，`context_builder.c:80-83`）；
  4. **最近 3 天 daily 拼接**（4KB 栈缓冲，`context_builder.c:85-89`）；
  5. 技能摘要（2KB）：每个 skill.md 只注入首行标题+首段描述，全文让 LLM 按需 read_file（`skill_loader.c:101-159`，"read with: read_file <path>"，`skill_loader.c:150-152`）——**两级注入省 token**；
  6. 每回合动态追加 Current Turn Context（source_channel/source_chat_id + cron 投递规则，`agent_loop.c:65-89`）。
- 短期记忆：`session_get_history_json` 逐行 fgets 解析整个 JSONL（单行上限 2048 字节，`session_mgr.c:70`），**cJSON 对象环形缓冲只保留最近 20 条**（覆盖最旧，`session_mgr.c:80-87`），按序重建数组只取 role+content 丢弃 ts（`session_mgr.c:90-105`）；agent 侧再叠加 `MIMI_AGENT_MAX_HISTORY=20`（`mimi_config.h:77`）。
- 工具循环硬上限：`MIMI_AGENT_MAX_TOOL_ITER=10` 次迭代、`MIMI_MAX_TOOL_CALLS=4` 并行调用（`mimi_config.h:78-79`）；工具输出统一 8KB PSRAM 缓冲（`agent_loop.c:19,178`）——资源约束下的失控保护。

### 2.4 遗忘·整合·演化
- **遗忘=硬截断**：会话超过 20 条环形丢弃（旧消息仍留在 JSONL 文件里，只是不再注入）；session_clear 整文件删除（`session_mgr.c:128-138`）。
- daily note 无清理逻辑，闪存写满即 SPIFFS 写失败（`memory_store.c:69-72` 仅打日志返回 ESP_FAIL）；MEMORY.md 无长度控制机制。
- **无整合/decay/merge**：MEMORY.md 是否精炼完全依赖 LLM 遵守提示词（"Keep MEMORY.md concise and organized"，`context_builder.c:68`），固件不强制；read-before-write 防丢也仅是提示词约定。
- 技能是"可自增的程序性记忆"：LLM 可 write_file 新建 skill 到 /spiffs/skills/（`context_builder.c:73`），随烧录分区持久——经验可以沉淀为可复用操作说明。
- OTA 双分区（`partitions.csv:5-6`）使固件升级不丢 SPIFFS 记忆——**记忆比代码更持久**是嵌入式记忆设计的第一原则。

### 2.5 注入上下文的方式与资源工程
- 记忆注入即系统提示拼装，一次性、全量、有硬预算：16KB 上下文缓冲里 MEMORY.md≤4KB、daily≤4KB、skills≤2KB（`context_builder.c:80-99`）；超出即 snprintf 静默截断。
- 每回合 LLM 请求形态：system_prompt（重建）+ 最近 20 条 history + 当前 user 消息，工具定义单列（tools_json，`agent_loop.c:238`）；ReAct 中间态（assistant content 数组 + tool_result 块）只存活于本轮内存，不回写会话文件（`agent_loop.c:256-267` vs :277-287）。
- 内存分层工程：
  - TLS×2（Telegram+Claude）约 120KB、系统提示 16KB、流缓冲 32KB 全放 PSRAM（`docs/ARCHITECTURE.md:177-184`；`agent_loop.c:176-178`）；
  - agent 任务栈分配失败时按 24K→20K→16K→14K→12K 五级降级重试并打印最大空闲块（`agent_loop.c:334-359`）；
  - 双核钉核：agent 在 core 1，通道轮询在 core 0（`mimi_config.h:60,76`）。
- 文件工具安全：路径必须以 `/spiffs/` 开头且禁含 `..`（`tool_files.c:20-31`）；单文件读写上限 32KB（`tool_files.c:15`）；GPIO 白名单策略阻止 flash/PSRAM 专用脚 GPIO6-11（`gpio_policy.c:63`）。
- 每回合注入当前通道上下文（source_channel/source_chat_id）防 cron 消息发错目标（`agent_loop.c:65-89`），并在执行层对 cron_add 参数做确定性 patch（channel/chat_id 缺失或为 "cron" 时回填真实来源，`agent_loop.c:91-137`）——"提示约束+执行兜底"双层防错。
- 出站队列满时直接丢弃 working 状态/最终回复（队列长 16，`agent_loop.c:296-298`）——资源受限下的显式降级而非阻塞。

### 2.6 补充深读：cron 持久化与消息总线（记忆的触发基础设施）
- `cron_service.c`（440 行）：任务数组上限 16（`mimi_config.h:115`）、ID 用硬件随机数 `esp_random()` 生成 8 位十六进制（`cron_service.c:55-59`）；持久化到 /spiffs/cron.json（save_jobs 全量重写）；每 60 秒检查一次到期任务（`mimi_config.h:116`），到期后构造预置消息推入总线触发独立 agent 回合——定时任务本身是"未来事件的记忆"（何时、对谁、说什么）。
- 目的地消毒 `cron_sanitize_destination`：telegram 任务缺 chat_id 或误填 "cron" 时回落 system:cron（`cron_service.c:25-51`）——与 agent_loop 的 patch 层（`agent_loop.c:91-137`）构成同一防错的写入/执行两道闸。
- `bus/message_bus.c`：FreeRTOS 队列（入站+出站各 16 深，`mimi_config.h:97`）；mimi_msg_t 携带 channel/chat_id/content 三元组；heartbeat、cron、IM 通道统一汇入同一入站队列，由单 agent 任务串行消费（`agent_loop.c:188-191`）——**串行化同时是并发控制与记忆一致性机制**（同一时刻只有一个回合在读写闪存记忆）。

## 3. 关键代码摘录

**技能两级注入（目录进提示、正文按需读）**（`main/skills/skill_loader.c:150-152`）：
```c
off += snprintf(buf + off, size - off,
    "- **%s**: %s (read with: read_file %s)\n",
    title, desc, full_path);
```

**HEARTBEAT 定时器注册（30 分钟自动重载）**（`main/heartbeat/heartbeat.c:130-136`）：
```c
s_heartbeat_timer = xTimerCreate(
    "heartbeat",
    pdMS_TO_TICKS(MIMI_HEARTBEAT_INTERVAL_MS),  /* 30 * 60 * 1000 */
    pdTRUE,    /* auto-reload */
    NULL,
    heartbeat_timer_callback
);
```

**系统提示的记忆注入段**（`main/agent/context_builder.c:80-89`）：
```c
/* Long-term memory */
char mem_buf[4096];
if (memory_read_long_term(mem_buf, sizeof(mem_buf)) == ESP_OK && mem_buf[0]) {
    off += snprintf(buf + off, size - off, "\n## Long-term Memory\n\n%s\n", mem_buf);
}
/* Recent daily notes (last 3 days) */
char recent_buf[4096];
if (memory_read_recent(recent_buf, sizeof(recent_buf), 3) == ESP_OK && recent_buf[0]) {
    off += snprintf(buf + off, size - off, "\n## Recent Notes\n\n%s\n", recent_buf);
}
```

**会话历史环形截断（检索=保留最近 N 条）**（`main/memory/session_mgr.c:80-92`）：
```c
/* Ring buffer: overwrite oldest if full */
if (count >= max_msgs) {
    cJSON_Delete(messages[write_idx]);
}
messages[write_idx] = obj;
write_idx = (write_idx + 1) % max_msgs;
if (count < max_msgs) count++;
...
int start = (count < max_msgs) ? 0 : write_idx;
```

**每日笔记=事件日志追加**（`main/memory/memory_store.c:57-78`）：
```c
snprintf(path, sizeof(path), "%s/%s.md", MIMI_SPIFFS_MEMORY_DIR, date_str);
FILE *f = fopen(path, "a");
if (!f) {
    f = fopen(path, "w");        /* SPIFFS 无 O_APPEND|O_CREAT 语义，两次尝试 */
    if (f) fprintf(f, "# %s\n\n", date_str);
}
fprintf(f, "%s\n", note);
```

**心跳任务扫描（启发式判断有无待办）**（`main/heartbeat/heartbeat.c:52-68`）：
```c
/* Skip markdown headers */
if (*p == '#') { continue; }
/* Skip completed checkboxes: "- [x]" or "* [x]" */
if ((*p == '-' || *p == '*') && *(p + 1) == ' ' && *(p + 2) == '[') {
    char mark = *(p + 3);
    if ((mark == 'x' || mark == 'X') && *(p + 4) == ']') { continue; }
}
found_task = true; break;
```

**记忆写入职责外包给 LLM 的提示词**（`main/agent/context_builder.c:63-69`）：
```c
"IMPORTANT: Actively use memory to remember things across conversations.\n"
"- When you learn something new about the user ..., write it to MEMORY.md.\n"
"- When something noteworthy happens ..., append it to today's daily note.\n"
"- Always read_file MEMORY.md before writing, so you can edit_file ...\n"
"- You should proactively save memory without being asked.\n"
```

**任务栈五级降级**（`main/agent/agent_loop.c:334-347`）：
```c
const uint32_t stack_candidates[] = {
    MIMI_AGENT_STACK,   /* 24K */
    20 * 1024, 16 * 1024, 14 * 1024, 12 * 1024,
};
for (size_t i = 0; i < (sizeof(stack_candidates) / sizeof(stack_candidates[0])); i++) {
    BaseType_t ret = xTaskCreatePinnedToCore(
        agent_loop_task, "agent_loop", stack_size, NULL,
        MIMI_AGENT_PRIO, NULL, MIMI_AGENT_CORE);
    if (ret == pdPASS) { ...; return ESP_OK; }
}
```

**文件工具路径校验**（`main/tools/tool_files.c:20-31`）：
```c
static bool validate_path(const char *path)
{
    if (!path) return false;
    size_t base_len = strlen(MIMI_SPIFFS_BASE);
    if (strncmp(path, MIMI_SPIFFS_BASE, base_len) != 0) return false;
    if (base_len > 0 && MIMI_SPIFFS_BASE[base_len - 1] != '/') {
        if (path[base_len] != '/') return false;
    }
    if (strstr(path, "..") != NULL) return false;
    return true;
}
```

## 4. 基准/评测声明（反虚荣视角）
- 无任何记忆质量/基准评测；仓库仅 CI 构建验证（`.github/workflows/build.yml`、release.yml）[不可复现]。
- 5.7K★ 来自"最便宜硬件 Agent"的产品叙事与社区传播（README：一块 16MB Flash + 8MB PSRAM 的 ESP32-S3 板 ~$10 / 国内 ~¥30，`README.md:40`、`README_CN.md:40`；skills/deploy 更写 ~$5-10，`skills/deploy/SKILL.md:13`——"$5 芯片"的说法即源于此区间），非记忆能力证明。
- README 声称 "persistent memory" [自封]——机制上确实持久（SPIFFS + OTA 保数据），但无容量/寿命/一致性数据。
- docs/ARCHITECTURE.md 给出 PSRAM 预算表（TLS 120KB/JSON 32KB/会话缓存 32KB/系统提示 16KB/流 32KB，剩余 ~7.7MB，`docs/ARCHITECTURE.md:177-182`）——工程透明度好，但仍非记忆评测。
- 仓库自带技能资产（weather/gpio-control/daily-briefing/skill-creator，`spiffs_data/skills/`）与 skills/deploy 部署技能（含 validate.sh）表明其"可自部署"定位，但无量化验收口径 [自封]。

### 关键参数速查（`main/mimi_config.h`）
- 上下文预算：系统提示 16KB（:110）、会话 20 条（:77,111）、工具迭代 10 次（:78）、并行工具 4 个（:79）、工具输出 8KB（`agent_loop.c:19`）、LLM 流缓冲 32KB（:92）。
- 记忆缓冲：MEMORY.md 4KB、daily 3 天 4KB、skills 2KB（`context_builder.c:80-99`）。
- 时序：心跳 30 分钟（:118）、cron 检查 60 秒（:116）、TG 轮询 30 秒超时（:56）。
- 通道：TG/飞书消息上限 4096（:57,65）、WS 端口 18789（:127）、飞书 webhook 18790（:69）。

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量）
1. **记忆分级 = 注入预算分级**：稳定画像（SOUL/USER 只读）→ 长期记忆（全量 4KB）→ 时间窗记忆（3 天 daily 4KB）→ 按需记忆（skills 只给目录，正文 LLM 自取）。**每层有固定字节预算，总预算 16KB 封顶**——比"动态检索 top-k"更可预测，适合硬约束环境。
2. **daily note 是最朴素的事件日志记忆**：append-only、按日期命名、读取即拼接——与 opensquilla 的 dated-note（衰减）同构，但无索引；证明无检索场景下"日期窗口"本身就是可用的弱检索。
3. **抽取逻辑放提示词、可靠性放执行层**：read-before-write 靠提示（`context_builder.c:66`），但 cron 目标错误靠固件确定性 patch 修正（`agent_loop.c:91-137`）——不可靠的生成用代码兜底。
4. **任务记忆（HEARTBEAT.md）+ 定时扫描 = 无推送条件下的主动性**：心跳先本地启发式过滤"无事不唤醒"，省一次 LLM 调用（`heartbeat.c:77-80`）；被判定可执行的任务行交给 LLM 解释执行——廉价启发式当门卫、LLM 当执行者。
5. **技能=可自增的程序性记忆**：LLM 观察到可复用流程即可 write_file 沉淀 skill（`context_builder.c:73`），下回合自动进入技能目录——记忆不只是事实，还有"怎么做"。
6. **记忆 > 固件的持久性设计**：双 OTA 分区 + 独立 12MB SPIFFS，升级永不触碰记忆（`partitions.csv:5-7`）。
7. **会话"只存两端"**：user 原文 + 最终回答，工具中间态不落盘（`agent_loop.c:277-279`）——闪存写入次数（SPIFFS 磨损）与 token 双重节约。

## 6. 局限与风险
- `memory_write_long_term` 全量覆写（`memory_store.c:46`）：LLM 忘了先 read 就 write 会**整页丢失既有记忆**，仅靠提示词防护；且无版本/备份，掉电时 fopen("w") 截断后崩溃不可恢复。
- SPIFFS 非原子写：写入中断（掉电/看门狗复位）可能损坏文件；coredump 分区存在（`partitions.csv:8`）但记忆无日志结构保护。
- 检索为零：MEMORY.md 超 4KB 即静默截断，记忆增长上限≈4KB；daily 无限增长会逐渐吃满 12MB SPIFFS 且无 GC。
- SPIFFS 磨损均衡弱于 LittleFS/FATFS，日志型追加写是正确方向但无磨损监控。
- 单行会话记录上限 2048 字节（`session_mgr.c:70`），超长消息 fgets 被切成多行、cJSON 解析失败静默丢弃（`session_mgr.c:77-78`）。
- 所有记忆明文驻留闪存，设备物理失窃即记忆泄露；NVS 中的 API token 仅 obscure 而非加密。
- 提示词与身份硬编码在 C 字符串里（`context_builder.c:32-73`），改记忆策略需重新编译烧录固件。

## 7. 一句话对比 mem0
mem0 用"抽取→向量库→混合检索"把记忆做成中间件服务；mimiclaw 证明在 $5 芯片上记忆可以退化成"文件系统 + 系统提示固定预算拼装 + 让 LLM 自己当记忆管理器"。

具体差异点：
- 规模：mem0 服务端索引/嵌入流水线 / mimiclaw 全部记忆代码约 272 行 C（memory_store.c 107 + session_mgr.c 165）；
- 检索：mem0 向量+关键词 / mimiclaw 零检索，日期窗口+全量注入；
- 抽取：mem0 服务端 LLM 抽取结构化事实 / mimiclaw 云端模型靠系统提示自律读写 Markdown；
- 遗忘：mem0 无内建 decay / mimiclaw 环形截断 20 条；
- 定位价值：mimiclaw 是记忆系统的**下限参照系**——任何记忆架构都应说明自己比这套代码多买了什么（检索？遗忘？演化？审计？），以及是否值这个复杂度。

<!-- source: DeepWiki mcp.deepwiki.com · repo Orchestra-Research/AI-research-SKILLs · page 4 Using Skills with AI Agents · fetched 2026-10-26 -->

# Using Skills with AI Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [demos/README.md](demos/README.md)
- [docs/ROADMAP.md](docs/ROADMAP.md)
- [docs/SKILL_CREATION_GUIDE.md](docs/SKILL_CREATION_GUIDE.md)
- [docs/SKILL_TEMPLATE.md](docs/SKILL_TEMPLATE.md)
- [docs/assets/promo.gif](docs/assets/promo.gif)
- [docs/christmas-tree.svg](docs/christmas-tree.svg)
- [docs/tech-tree.svg](docs/tech-tree.svg)
- [packages/ai-research-skills/package.json](packages/ai-research-skills/package.json)
- [packages/ai-research-skills/src/index.js](packages/ai-research-skills/src/index.js)
- [packages/ai-research-skills/src/installer.js](packages/ai-research-skills/src/installer.js)
- [packages/ai-research-skills/src/prompts.js](packages/ai-research-skills/src/prompts.js)

</details>



This document explains how AI coding agents discover, load, and utilize skills during autonomous research workflows. It covers the technical mechanisms by which agents integrate with the skills library, the skill file format that enables semantic discovery, and concrete examples of agent-skill interaction patterns.

For information about installing skills to agents, see [Installation Guide](#2). For details on creating new skills, see [Contributing New Skills](#5). For the internal architecture of the installation system, see [CLI Architecture & Implementation](#6.3).

---

## Agent Integration Patterns

AI agents integrate with skills through a canonical directory structure with per-agent symlinks. The system supports five primary agents: Claude Code, Cursor, Windsurf, Gemini CLI, and Qwen Code.

### Supported Agent Configuration Directories

| Agent | Config Directory | Skills Path | Detection Method |
|-------|-----------------|-------------|------------------|
| Claude Code | `~/.claude/` | `~/.claude/skills/` | Check for `.claude` directory |
| Cursor | `~/.cursor/` | `~/.cursor/skills/` | Check for `.cursor` directory |
| Windsurf | `~/.windsurf/` | `~/.windsurf/skills/` | Check for `.windsurf` directory |
| Gemini CLI | `~/.gemini/` | `~/.gemini/skills/` | Check for `.gemini` directory |
| Qwen Code | `~/.qwen/` | `~/.qwen/skills/` | Check for `.qwen` directory |

### Canonical Storage Architecture

Skills are stored in a canonical directory at `~/.orchestra/skills/` with symlinks created in each agent's skills directory. This architecture ensures:

1. **Single source of truth** - Skills exist in one location
2. **Consistent updates** - Updating the canonical directory updates all agents
3. **Space efficiency** - No duplication across multiple agents
4. **Easy management** - Central location for skill tracking

```mermaid
graph TB
    subgraph "Canonical Storage"
        CANONICAL["~/.orchestra/skills/"]
        CAT01["01-model-architecture/"]
        CAT06["06-post-training/"]
        CAT12["12-inference-serving/"]
        CAT20["20-ml-paper-writing/"]
        
        CANONICAL --> CAT01
        CANONICAL --> CAT06
        CANONICAL --> CAT12
        CANONICAL --> CAT20
        
        CAT01 --> LITGPT["litgpt/SKILL.md"]
        CAT06 --> VERL["verl/SKILL.md"]
        CAT06 --> GRPO["grpo-rl-training/SKILL.md"]
        CAT12 --> VLLM["vllm/SKILL.md"]
        CAT20 --> PAPER["SKILL.md (standalone)"]
    end
    
    subgraph "Agent Symlinks"
        CLAUDE["~/.claude/skills/"]
        CURSOR["~/.cursor/skills/"]
        GEMINI["~/.gemini/skills/"]
        
        CLAUDE --> LITGPT
        CLAUDE --> VERL
        CLAUDE --> VLLM
        
        CURSOR --> LITGPT
        CURSOR --> GRPO
        CURSOR --> VLLM
        
        GEMINI --> VERL
        GEMINI --> PAPER
    end
    
    subgraph "Tracking"
        LOCKFILE["~/.orchestra/.lock.json"]
        LOCKFILE --> CANONICAL
    end
```

**Sources:** [README.md:80-91](), [packages/ai-research-skills/src/installer.js:9-10](), [packages/ai-research-skills/src/installer.js:119-151]()

### Agent Detection Implementation

The system uses filesystem checks to detect installed agents:

```mermaid
sequenceDiagram
    participant CLI as "CLI Installer"
    participant FS as "Filesystem"
    participant DETECT as "detectAgents()"
    
    CLI->>DETECT: Call detectAgents()
    DETECT->>FS: Check existsSync('~/.claude/')
    FS-->>DETECT: true
    DETECT->>FS: Check existsSync('~/.cursor/')
    FS-->>DETECT: false
    DETECT->>FS: Check existsSync('~/.windsurf/')
    FS-->>DETECT: true
    DETECT->>FS: Check existsSync('~/.gemini/')
    FS-->>DETECT: false
    DETECT->>FS: Check existsSync('~/.qwen/')
    FS-->>DETECT: false
    
    DETECT-->>CLI: Return [{name: "Claude Code", skillsPath: "~/.claude/skills/"}, {name: "Windsurf", skillsPath: "~/.windsurf/skills/"}]
```

The detection logic iterates through known agent configurations and returns only those with existing configuration directories on the system.

**Sources:** [README.md:86-87](), [packages/ai-research-skills/src/index.js:38-48]()

### Symlink Creation Process

When skills are installed, the system:

1. Downloads skills to `~/.orchestra/skills/` (canonical directory)
2. Creates symlinks in each detected agent's `skills/` directory
3. Handles both nested skills (`category/skill-name/`) and standalone skills (`category/`)

```mermaid
graph LR
    subgraph "Installation Flow"
        DOWNLOAD["downloadSkills()"]
        COPY["Copy to ~/.orchestra/skills/"]
        SYMLINK["createSymlinks()"]
        LOCK["Update .lock.json"]
        
        DOWNLOAD --> COPY
        COPY --> SYMLINK
        SYMLINK --> LOCK
    end
    
    subgraph "Symlink Logic"
        CHECK["existsSync(linkPath)?"]
        REMOVE["rmSync(linkPath)"]
        CREATE["symlinkSync(sourcePath, linkPath)"]
        
        CHECK -->|Yes| REMOVE
        CHECK -->|No| CREATE
        REMOVE --> CREATE
    end
    
    SYMLINK --> CHECK
```

**Sources:** [packages/ai-research-skills/src/installer.js:49-114](), [packages/ai-research-skills/src/installer.js:119-151]()

---

## Skill Structure & Format

Skills follow a standardized format that enables agents to discover, load, and utilize them effectively. The structure balances comprehensive documentation with progressive disclosure to optimize context window usage.

### Directory Structure

Skills are organized in numbered categories with either nested or standalone layouts:

**Nested skill layout** (most common):
```
06-post-training/
├── verl/
│   ├── SKILL.md                 # Main skill file (200-500 lines)
│   ├── references/              # Supporting documentation
│   │   ├── README.md
│   │   ├── architecture.md
│   │   └── examples.md
│   └── scripts/                 # Optional helper scripts
│       └── validate.py
```

**Standalone skill layout** (single skill per category):
```
20-ml-paper-writing/
├── SKILL.md                     # Main skill file
├── references/                  # Supporting documentation
│   ├── citation-verification.md
│   ├── latex-templates.md
│   └── writing-guidelines.md
└── scripts/
    └── check_citations.py
```

**Sources:** [CONTRIBUTING.md:260-282](), [docs/SKILL_CREATION_GUIDE.md:240-263]()

### YAML Frontmatter: The Discovery Index

Every `SKILL.md` begins with YAML frontmatter that serves as the semantic index for agent discovery. This metadata enables agents to search and filter skills based on task requirements.

**Required fields:**

| Field | Format | Purpose | Example |
|-------|--------|---------|---------|
| `name` | kebab-case | Unique identifier | `grpo-rl-training` |
| `description` | Plain text (max 1024 chars) | What it does AND when to use it | `Expert guidance for GRPO/RL fine-tuning with TRL...` |
| `version` | Semantic version | Skill version | `1.0.0` |
| `author` | Plain text | Author attribution | `Orchestra Research` |
| `license` | License ID | License type | `MIT` |
| `tags` | Array (Title Case) | Searchable terms | `[Reinforcement Learning, GRPO, TRL, Post-Training]` |
| `dependencies` | Array with versions | Required packages | `[transformers>=4.47.0, trl>=0.14.0]` |

**Example from actual skill:**

```yaml
---
name: grpo-rl-training
description: Expert guidance for GRPO/RL fine-tuning with TRL for reasoning and task-specific model training
version: 1.0.0
author: Orchestra Research
license: MIT
tags: [Reinforcement Learning, GRPO, TRL, Post-Training, RLHF, Reward Modeling, Reasoning, DPO, PPO, Structured Output]
dependencies: [transformers>=4.47.0, trl>=0.14.0, datasets>=3.2.0, peft>=0.14.0, torch]
---
```

**Naming conventions:**
- **name**: Use gerund form (e.g., `serving-llms`, `processing-data`, `training-models`)
- **description**: Third person, no "I can help you..." constructions
- **tags**: Capitalize acronyms (GRPO, TRL, RLHF, DPO, MLOps, RAG)

**Sources:** [CONTRIBUTING.md:126-208](), [docs/SKILL_CREATION_GUIDE.md:122-227](), [.claude-plugin/marketplace.json:69-83]()

### SKILL.md Content Structure

The main skill file follows a progressive disclosure pattern with three priority levels:

```mermaid
graph TB
    subgraph "SKILL.md (200-500 lines max)"
        FRONT["YAML Frontmatter"]
        QUICK["Quick Start (5-10 lines of code)"]
        WORKFLOWS["Common Workflows (with checklists)"]
        WHEN["When to Use vs Alternatives"]
        ISSUES["Common Issues & Solutions"]
        REFS["Links to references/"]
        
        FRONT --> QUICK
        QUICK --> WORKFLOWS
        WORKFLOWS --> WHEN
        WHEN --> ISSUES
        ISSUES --> REFS
    end
    
    subgraph "references/ (loaded on demand)"
        API["api-reference.md"]
        ARCH["architecture.md"]
        ADV["advanced-features.md"]
        EXAMPLES["examples.md"]
        TROUBLE["troubleshooting.md"]
        
        REFS -.->|"Agent loads"| API
        REFS -.->|"as needed"| ARCH
        REFS -.->|"during"| ADV
        REFS -.->|"task"| EXAMPLES
        REFS -.->|"execution"| TROUBLE
    end
```

**Priority Level 1: Always Loaded (in SKILL.md)**
- Quick start with minimal working example
- Common workflows with copy-paste checklists
- When to use this skill vs alternatives
- Common issues with immediate fixes

**Priority Level 2: Loaded on Demand (in references)**
- API reference documentation
- Architecture details
- Advanced features and optimizations
- Extended troubleshooting guides
- Detailed examples and tutorials

**Priority Level 3: Executed, Not Loaded**
- Helper scripts in `scripts/` directory
- Validation tools
- Setup automation

**Sources:** [docs/SKILL_CREATION_GUIDE.md:45-64](), [README.md:325-358]()

### Progressive Disclosure Pattern

Skills follow Anthropic's best practices by keeping SKILL.md concise and pointing to detailed materials:

**Implementation rules:**
1. SKILL.md body must be **under 500 lines** for optimal performance
2. Aim for **200-300 lines** in practice
3. Reference files must be **ONE LEVEL DEEP** (no nested references)
4. Assume agent knowledge - don't explain basics

**Example reference structure:**

```markdown
## Advanced topics

**Server deployment**: See [server-deployment.md](server-deployment.md)
**Offline inference**: See [offline-inference.md](offline-inference.md)  
**API reference**: See [api-reference.md](api-reference.md)
**Optimization**: See [optimization.md](optimization.md)
```

**Why this works:**
- Agent loads SKILL.md first (200-300 lines)
- Agent reads overview and workflows
- Agent loads specific reference file only when needed for current task
- Total context usage scales with task complexity, not skill comprehensiveness

**Sources:** [docs/SKILL_CREATION_GUIDE.md:45-103](), [CONTRIBUTING.md:83-93]()

### Workflow Checklists

Skills provide copy-paste checklists for multi-step tasks, enabling agents to track progress:

```markdown
## Deployment workflow

Copy this checklist and track progress:

\```
Task Progress:
- [ ] Step 1: Configure server settings
- [ ] Step 2: Validate configuration  
- [ ] Step 3: Deploy to production
- [ ] Step 4: Verify deployment
\```

**Step 1: Configure server settings**

Edit `config.yaml` with production values.

**Step 2: Validate configuration**

Run validator and fix errors:
\```bash
python validate.py config.yaml
# If errors: fix → validate again → continue
\```

**Step 3: Deploy to production**

[Specific deployment commands]

**Step 4: Verify deployment**

[Verification steps]
```

This pattern enables agents to maintain state across multi-turn interactions and resume complex workflows.

**Sources:** [docs/SKILL_CREATION_GUIDE.md:66-102](), [docs/SKILL_TEMPLATE.md:29-69]()

---

## Skill Discovery and Loading

Agents discover and load skills through a two-phase process: semantic search via YAML frontmatter, followed by progressive content loading.

### Phase 1: Semantic Search via YAML Frontmatter

When a user makes a request, agents scan the YAML frontmatter of all installed skills to find relevant matches.

```mermaid
sequenceDiagram
    participant USER as "User"
    participant AGENT as "AI Agent"
    participant FS as "Filesystem"
    participant YAML as "YAML Parser"
    
    USER->>AGENT: "Fine-tune Llama 3 with custom data"
    AGENT->>FS: List ~/.claude/skills/**/SKILL.md
    FS-->>AGENT: [axolotl/SKILL.md, unsloth/SKILL.md, peft/SKILL.md, ...]
    
    loop For each SKILL.md
        AGENT->>FS: Read first 20 lines (YAML frontmatter)
        FS-->>AGENT: YAML content
        AGENT->>YAML: Parse frontmatter
        YAML-->>AGENT: {name, description, tags}
        AGENT->>AGENT: Match against: "fine-tune", "Llama", "custom data"
    end
    
    AGENT->>AGENT: Rank by relevance
    AGENT-->>USER: Select: axolotl (score: 0.92), unsloth (score: 0.88)
```

**Matching criteria (in order of importance):**

1. **Exact keyword match in description** - e.g., "Fine-Tuning" in description
2. **Tag matches** - e.g., `[Fine-Tuning, LoRA, PEFT]`
3. **Skill name similarity** - e.g., `axolotl` for training tasks
4. **Dependency indicators** - e.g., `[torch, transformers]` suggests ML training

**Example search scenarios:**

| User Query | Matched Skills | Matching Elements |
|-----------|---------------|-------------------|
| "Deploy vLLM server" | `12-inference-serving/vllm/` | name:`vllm`, tags:`[Inference, Serving]`, description:"serving LLMs" |
| "GRPO training" | `06-post-training/grpo-rl-training/` | name:`grpo-rl-training`, tags:`[GRPO, RLHF]` |
| "Write NeurIPS paper" | `20-ml-paper-writing/` | description:"NeurIPS, ICML, ICLR", tags:`[ML Paper Writing]` |
| "Quantize model to 4-bit" | `10-optimization/gptq/`, `10-optimization/awq/` | tags:`[Quantization]`, description:"4-bit" |

**Sources:** [.claude-plugin/marketplace.json:1-255](), [CONTRIBUTING.md:126-208]()

### Phase 2: Progressive Content Loading

After identifying relevant skills, agents load content progressively based on task needs:

```mermaid
graph TB
    subgraph "Initial Load"
        SKILLMD["Load full SKILL.md (200-500 lines)"]
        PARSE["Parse into sections"]
        EXTRACT["Extract relevant workflows"]
    end
    
    subgraph "Task Execution"
        WORKFLOW["Execute workflow steps"]
        NEED["Need more detail?"]
        LOAD_REF["Load specific reference file"]
        NEED2["Need another reference?"]
        LOAD_REF2["Load another reference file"]
    end
    
    subgraph "Script Execution"
        EXEC["Execute helper scripts"]
        VALIDATE["Run validation"]
    end
    
    SKILLMD --> PARSE
    PARSE --> EXTRACT
    EXTRACT --> WORKFLOW
    WORKFLOW --> NEED
    NEED -->|Yes| LOAD_REF
    NEED -->|No| EXEC
    LOAD_REF --> NEED2
    NEED2 -->|Yes| LOAD_REF2
    NEED2 -->|No| EXEC
    LOAD_REF2 --> EXEC
    EXEC --> VALIDATE
```

**Loading sequence example (vLLM deployment):**

1. **Initial:** Load `12-inference-serving/vllm/SKILL.md` (356 lines)
   - Read quick start
   - Identify "Server deployment" workflow
   
2. **On-demand:** User needs deployment details
   - Load `references/server-deployment.md`
   - Read configuration options
   
3. **On-demand:** User encounters error
   - Load `references/troubleshooting.md`
   - Find error pattern and solution

4. **Execution:** User ready to deploy
   - Execute `scripts/validate_config.py`
   - Run deployment commands from workflow

**Context window optimization:**
- Baseline: 200-500 lines (SKILL.md only)
- +500-1000 lines per reference file loaded
- Scripts executed, not loaded (zero context cost)

**Sources:** [README.md:325-358](), [docs/SKILL_CREATION_GUIDE.md:45-64]()

### Lock File Tracking

The installation system maintains a lock file to track which skills are installed:

```json
{
  "version": "1.0.0",
  "installedAt": "2025-01-15T10:30:00.000Z",
  "skills": [
    {"category": "06-post-training", "skill": "verl", "standalone": false},
    {"category": "12-inference-serving", "skill": "vllm", "standalone": false},
    {"category": "20-ml-paper-writing", "skill": "20-ml-paper-writing", "standalone": true}
  ],
  "agents": ["claude", "cursor"]
}
```

This enables the system to:
- List installed skills without scanning directories
- Update only installed skills
- Track installation timestamps
- Know which agents have access

**Sources:** [packages/ai-research-skills/src/installer.js:27-44](), [packages/ai-research-skills/src/installer.js:280-293]()

---

## Example Workflows

This section demonstrates concrete examples of how agents use skills during autonomous research tasks.

### Workflow 1: Fine-Tuning with Unsloth

**User request:** "Fine-tune Llama 3.1 8B on my dataset with LoRA"

```mermaid
sequenceDiagram
    participant USER as "User"
    participant AGENT as "Agent"
    participant SKILLS as "Skills Directory"
    participant CODE as "Code Generation"
    participant GPU as "GPU Execution"
    
    USER->>AGENT: "Fine-tune Llama 3.1 8B on my dataset with LoRA"
    
    Note over AGENT: Phase 1: Discovery
    AGENT->>SKILLS: Scan YAML frontmatter
    SKILLS-->>AGENT: Match: 03-fine-tuning/unsloth (tags: [Fine-Tuning, LoRA])
    
    Note over AGENT: Phase 2: Load Skill
    AGENT->>SKILLS: Load 03-fine-tuning/unsloth/SKILL.md
    SKILLS-->>AGENT: Quick start + Workflow 1 checklist
    
    Note over AGENT: Phase 3: Generate Implementation
    AGENT->>CODE: Extract workflow steps
    CODE-->>AGENT: 1. Install unsloth, 2. Load model, 3. Configure LoRA, 4. Train
    
    AGENT->>USER: "I'll use Unsloth for 2x faster QLoRA fine-tuning. Here's the workflow..."
    
    Note over AGENT: Phase 4: Execution
    AGENT->>CODE: Generate training script
    CODE-->>AGENT: train.py (with LoRA config)
    
    AGENT->>GPU: Run training command
    GPU-->>AGENT: Training progress...
    
    Note over AGENT: Phase 5: Validation
    AGENT->>SKILLS: Load references/troubleshooting.md (on error)
    AGENT->>GPU: Apply fixes, resume
    
    GPU-->>AGENT: Training complete
    AGENT-->>USER: "Training complete! Model saved to ./output/"
```

**Actual skill sections used:**
1. YAML frontmatter → Discovery via tags `[Fine-Tuning, LoRA, Unsloth]`
2. Quick start → 5-line minimal example
3. Workflow 1: Basic fine-tuning → Checklist with 4 steps
4. Common issues → Error handling patterns

**Sources:** [README.md:161-165](), [.claude-plugin/marketplace.json:36-45]()

### Workflow 2: RLHF Training with GRPO

**User request:** "Set up GRPO reinforcement learning for reasoning tasks"

```mermaid
sequenceDiagram
    participant USER as "User"
    participant AGENT as "Agent"
    participant SKILLS as "Skills Directory"
    participant REF as "Reference Files"
    participant MODAL as "Modal GPU Cloud"
    
    USER->>AGENT: "Set up GRPO RL for reasoning tasks"
    
    Note over AGENT: Discovery
    AGENT->>SKILLS: Search for "GRPO", "RL", "reasoning"
    SKILLS-->>AGENT: Match: 06-post-training/grpo-rl-training
    
    AGENT->>SKILLS: Load SKILL.md
    SKILLS-->>AGENT: Workflow checklist with 8 steps
    
    Note over AGENT: Detailed Configuration Needed
    AGENT->>REF: Need reward model setup?
    AGENT->>SKILLS: Load references/reward-modeling.md
    SKILLS-->>AGENT: Reward model architecture + examples
    
    AGENT->>REF: Need hyperparameters?
    AGENT->>SKILLS: Load references/hyperparameters.md
    SKILLS-->>AGENT: GRPO beta, KL penalty configs
    
    Note over AGENT: Implementation
    AGENT->>USER: "I'll set up GRPO with TRL. Steps:\n1. Prepare preference data\n2. Train reward model\n3. Configure GRPO trainer\n4. Run RL training"
    
    AGENT->>MODAL: Provision H100 GPUs
    MODAL-->>AGENT: GPUs ready
    
    AGENT->>MODAL: Execute training script
    MODAL-->>AGENT: Training logs (epoch 1/3...)
    
    Note over AGENT: Monitoring
    AGENT->>REF: KL divergence too high?
    AGENT->>SKILLS: Load references/troubleshooting.md
    SKILLS-->>AGENT: Solution: Reduce beta parameter
    
    AGENT->>MODAL: Update config, resume
    MODAL-->>AGENT: Training complete, 95% win rate
    
    AGENT-->>USER: "Training complete! Model shows 95% win rate on reasoning tasks."
```

**Progressive loading in action:**
- **Initial:** Load `SKILL.md` (569 lines) → Overview + workflow checklist
- **Step 2:** Load `references/reward-modeling.md` → Reward model details
- **Step 3:** Load `references/hyperparameters.md` → Tuning guidance
- **On error:** Load `references/troubleshooting.md` → KL divergence fix

**Total context used:** ~1,500 lines (27% of total available documentation)

**Sources:** [README.md:177-179](), [.claude-plugin/marketplace.json:69-83]()

### Workflow 3: Production Inference with vLLM

**User request:** "Deploy Llama 3 70B with vLLM for production API"

```mermaid
sequenceDiagram
    participant USER as "User"
    participant AGENT as "Agent"
    participant SKILLS as "Skills Directory"
    participant REF as "Reference Files"
    participant SERVER as "Production Server"
    
    USER->>AGENT: "Deploy Llama 3 70B with vLLM for production"
    
    AGENT->>SKILLS: Search "vLLM", "inference", "serving", "production"
    SKILLS-->>AGENT: Match: 12-inference-serving/vllm
    
    AGENT->>SKILLS: Load SKILL.md
    SKILLS-->>AGENT: Quick start + Workflow 2: Server deployment
    
    Note over AGENT: Server Configuration
    AGENT->>REF: Need multi-GPU setup?
    AGENT->>SKILLS: Load references/multi-gpu.md
    SKILLS-->>AGENT: Tensor parallelism configuration
    
    AGENT->>USER: "I'll deploy with:\n- Tensor parallelism (4xA100)\n- PagedAttention for memory\n- OpenAI-compatible API"
    
    AGENT->>SERVER: Generate deployment script
    SERVER-->>AGENT: Configuration ready
    
    AGENT->>SERVER: Start vLLM server
    SERVER-->>AGENT: Server running on port 8000
    
    AGENT->>SERVER: Test API endpoint
    SERVER-->>AGENT: 200 OK, latency: 45ms
    
    Note over AGENT: Performance Tuning
    AGENT->>REF: Need optimization?
    AGENT->>SKILLS: Load references/optimization.md
    SKILLS-->>AGENT: Batching + cache tuning
    
    AGENT->>SERVER: Apply optimizations
    SERVER-->>AGENT: Throughput: 2400 tok/s
    
    AGENT-->>USER: "Production deployment complete! API at https://api.example.com\nThroughput: 2400 tokens/sec"
```

**Workflow checklist from SKILL.md:**

```
Task Progress:
- [x] Step 1: Install vLLM
- [x] Step 2: Configure multi-GPU setup
- [x] Step 3: Start server
- [x] Step 4: Verify API
- [x] Step 5: Load test and optimize
```

**Sources:** [README.md:218-222](), [.claude-plugin/marketplace.json:146-156]()

### Workflow 4: Writing Research Papers

**User request:** "Write a NeurIPS paper about my RLHF experiments"

```mermaid
graph TB
    subgraph "Phase 1: Skill Discovery"
        QUERY["User: Write NeurIPS paper about RLHF experiments"]
        SEARCH["Agent searches: 'NeurIPS', 'paper', 'writing'"]
        MATCH["Match: 20-ml-paper-writing"]
        LOAD["Load SKILL.md (532 lines)"]
        
        QUERY --> SEARCH
        SEARCH --> MATCH
        MATCH --> LOAD
    end
    
    subgraph "Phase 2: Workflow Execution"
        WF1["Workflow 1: Proactive draft delivery"]
        WF2["Workflow 2: Citation verification"]
        WF3["Workflow 3: LaTeX formatting"]
        
        LOAD --> WF1
        WF1 --> WF2
        WF2 --> WF3
    end
    
    subgraph "Phase 3: Reference Loading"
        REF1["references/writing-guidelines.md"]
        REF2["references/citation-verification.md"]
        REF3["references/latex-templates.md"]
        
        WF1 --> REF1
        WF2 --> REF2
        WF3 --> REF3
    end
    
    subgraph "Phase 4: Output Generation"
        DRAFT["Generate paper draft"]
        VERIFY["Verify all citations"]
        FORMAT["Apply NeurIPS template"]
        DELIVER["Deliver camera-ready PDF"]
        
        REF1 --> DRAFT
        REF2 --> VERIFY
        REF3 --> FORMAT
        FORMAT --> DELIVER
    end
```

**Key skill features used:**

1. **Proactive draft delivery** - Agent writes complete draft without user asking for each section
2. **Citation verification** - Never hallucinates references, validates all citations
3. **Conference-specific formatting** - Applies NeurIPS LaTeX template
4. **Writing guidelines** - Follows Neel Nanda, Farquhar, Gopen & Swan principles

**Progressive disclosure in action:**
- **SKILL.md:** Overview of 4 workflows (532 lines)
- **references/writing-guidelines.md:** Detailed writing advice
- **references/citation-verification.md:** Citation checking pipeline
- **references/latex-templates.md:** NeurIPS style files
- **references/reviewer-guidelines.md:** What reviewers look for

**Sources:** [README.md:269-270](), [.claude-plugin/marketplace.json:245-253]()

### Common Patterns Across Workflows

All agent-skill interactions follow this sequence:

1. **Discovery** - YAML frontmatter semantic search
2. **Initial Load** - Load SKILL.md (200-500 lines)
3. **Workflow Selection** - Identify relevant checklist
4. **Progressive Loading** - Load reference files as needed
5. **Execution** - Run scripts, generate code, execute commands
6. **Validation** - Check results, load troubleshooting if needed
7. **Iteration** - Repeat steps 4-6 until task complete

**Context window efficiency:**
- Minimum: 200-500 lines (SKILL.md only)
- Typical: 1,000-2,000 lines (SKILL.md + 2-3 references)
- Maximum: 3,000-5,000 lines (SKILL.md + all references)

This scales with task complexity while keeping most tasks in the lower range.

**Sources:** [docs/SKILL_CREATION_GUIDE.md:45-103](), [README.md:325-358]()

---


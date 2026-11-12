# vllm-skills

> 来源: https://deepwiki.com/vllm-project/vllm-skills 抓取日期: 2026-09-02（overview 级摘要）

---

Overview

# Overview

Relevant source files

  * [.claude-plugin/marketplace.json](https://github.com/vllm-project/vllm-skills/blob/c9962341/.claude-plugin/marketplace.json)
  * [README.md](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1)
  * [plugins/vllm-skills/.claude-plugin/plugin.json](https://github.com/vllm-project/vllm-skills/blob/c9962341/plugins/vllm-skills/.claude-plugin/plugin.json)

This page introduces the `vllm-skills` repository: what it is, what problems it solves, and how its components fit together. It provides modular, reusable agent skills required to operate and benchmark vLLM.

* * *

## Purpose

`vllm-skills` is a collection of modular agent skills for deploying and operating vLLM. The repository follows the [anthropics/skills](https://github.com/vllm-project/vllm-skills/blob/c9962341/anthropics/skills) template format [README.md3-7](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L3-L7) meaning each skill is a self-contained directory that can be registered with Claude Code.

The project addresses the complexity of LLM serving by providing automated workflows for:

  * **Deployment** : Support for local environments, Docker, and Kubernetes.
  * **Benchmarking** : Standardized tools for measuring throughput, latency (TTFT/TPOT), and prefix caching efficiency.
  * **Automation** : Integration with Claude Code allows users to trigger complex infrastructure tasks via natural language or slash commands [README.md52-66](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L52-L66)

Sources: [README.md1-18](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L1-L18) [plugins/vllm-skills/.claude-plugin/plugin.json1-7](https://github.com/vllm-project/vllm-skills/blob/c9962341/plugins/vllm-skills/.claude-plugin/plugin.json#L1-L7)

* * *

## Repository Structure

The repository organizes skills under a plugin-based architecture. The core logic resides within `plugins/vllm-skills/skills/`.

**Repository layout:**
    
    
    vllm-skills/
    ├── .claude-plugin/
    │   └── marketplace.json       # Marketplace metadata for Claude Code
    ├── plugins/
    │   └── vllm-skills/
    │       ├── .claude-plugin/
    │       │   └── plugin.json    # Plugin-specific metadata
    │       └── skills/            # Collection of individual skills
    │           ├── vllm-deploy-simple/
    │           ├── vllm-deploy-docker/
    │           ├── vllm-deploy-k8s/
    │           ├── vllm-bench-serve/
    │           ├── vllm-bench-random-synthetic/
    │           └── vllm-prefix-cache-bench/
    └── README.md
    

**Diagram: Repository file tree mapped to code entities**

Sources: [README.md11-18](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L11-L18) [.claude-plugin/marketplace.json1-15](https://github.com/vllm-project/vllm-skills/blob/c9962341/.claude-plugin/marketplace.json#L1-L15) [plugins/vllm-skills/.claude-plugin/plugin.json1-7](https://github.com/vllm-project/vllm-skills/blob/c9962341/plugins/vllm-skills/.claude-plugin/plugin.json#L1-L7)

* * *

## Skills Inventory

The repository provides six primary skills covering deployment and performance analysis.

Skill| Description  
---|---  
`vllm-deploy-simple`| Quick install and deploy vLLM locally with hardware detection.  
`vllm-deploy-docker`| Deploy using pre-built images or build-from-source with NVIDIA support.  
`vllm-deploy-k8s`| Kubernetes deployment with health probes and GPU resource limits.  
`vllm-bench-serve`| Benchmark existing OpenAI-compatible endpoints using `vllm bench serve`.  
`vllm-bench-random-synthetic`| Measure throughput/latency (TTFT, TPOT) without external datasets.  
`vllm-prefix-cache-bench`| Measure efficiency of automatic prefix caching (APC).  
  
Sources: [README.md11-18](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L11-L18)

* * *

## Integration with Claude Code

Skills integrate with Claude Code either via the Plugin Marketplace or through manual filesystem installation.

**Installation Methods:**

  1. **Marketplace** : Users can add the repository as a plugin source and install the `vllm-skills` plugin [README.md22-29](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L22-L29)
  2. **Manual** : Copying a specific skill directory from `plugins/vllm-skills/skills/` to either the global (`~/.claude/skills/`) or project-local (`.claude/skills/`) directory [README.md31-50](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L31-L50)

**Diagram: From user intent to running vLLM server**

Sources: [README.md20-66](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L20-L66) [.claude-plugin/marketplace.json1-15](https://github.com/vllm-project/vllm-skills/blob/c9962341/.claude-plugin/marketplace.json#L1-L15)

* * *

## The `SKILL.md` Contract

Every skill must contain a `SKILL.md` file at its root [README.md77-83](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L77-L83) This file serves as the manifest for Claude Code.

  * **YAML Frontmatter** : Contains the `name` (used for slash commands) and `description` (used by the agent's LLM to determine when to use the skill) [README.md78-83](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L78-L83)
  * **Markdown Body** : Contains detailed instructions, examples, and documentation that the agent uses to understand how to execute the skill's scripts or tools.

**Diagram: SKILL.md integration**

Sources: [README.md7-8](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L7-L8) [README.md74-83](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L74-L83)

* * *

## Contributing New Skills

The project follows a standardized contribution flow to ensure skills remain modular and compatible with the Anthropics template.

  1. **Directory Structure** : Create a new directory under `plugins/vllm-skills/skills/` [README.md76](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L76-L76)
  2. **Manifest** : Add a `SKILL.md` with required YAML frontmatter [README.md77-83](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L77-L83)
  3. **Components** : Add optional subdirectories: 
     * `scripts/`: For executable automation.
     * `references/`: For static configuration or documentation.
     * `assets/`: For images or non-code files [README.md84](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L84-L84)
  4. **Registration** : Update the main `README.md` index [README.md85](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L85-L85)

Sources: [README.md72-86](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L72-L86)

* * *

## License

The repository is released under the **Apache License 2.0**.

Sources: [README.md87-89](https://github.com/vllm-project/vllm-skills/blob/c9962341/README.md?plain=1#L87-L89)

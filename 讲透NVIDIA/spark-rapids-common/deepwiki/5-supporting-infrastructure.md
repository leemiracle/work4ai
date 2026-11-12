<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/spark-rapids-common · page 5 Supporting Infrastructure · fetched 2026-10-26 -->

# Supporting Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [checkout/action.yml](checkout/action.yml)

</details>



This document covers the supporting utilities and infrastructure components that enable the core functionality of the spark-rapids-common repository. These foundational components provide standardized, reusable building blocks that underpin the quality gates, project management, and automated merging systems.

The supporting infrastructure focuses on creating consistent, reliable interfaces to GitHub's native functionality while adding enterprise-grade configurability and error handling. For information about the quality validation pipeline that depends on this infrastructure, see [Quality Gates System](#2). For details about automated workflows that leverage these components, see [Automated Merging System](#4).

## System Architecture

The supporting infrastructure follows a wrapper pattern that enhances GitHub's native actions with standardized parameter handling, comprehensive configurability, and consistent error handling across the ecosystem.

### Infrastructure Component Architecture

```mermaid
graph TB
    subgraph "Supporting Infrastructure"
        subgraph "checkout/"
            checkout_action["checkout/action.yml"]
            checkout_composite["Composite Action"]
        end
        
        subgraph "GitHub Actions Core"
            actions_checkout["actions/checkout@v4"]
            github_api["GitHub API"]
        end
        
        subgraph "Consumer Workflows"
            quality_gates["Quality Gate Actions"]
            project_mgmt["Project Management Actions"]
            auto_merge["Auto-merge Actions"]
        end
    end
    
    checkout_action --> checkout_composite
    checkout_composite --> actions_checkout
    actions_checkout --> github_api
    
    quality_gates -.-> checkout_action
    project_mgmt -.-> checkout_action
    auto_merge -.-> checkout_action
    
    checkout_action --> repository_config["Repository Configuration"]
    checkout_action --> auth_config["Authentication Configuration"]
    checkout_action --> behavior_config["Checkout Behavior Configuration"]
    checkout_action --> advanced_config["Advanced Features Configuration"]
```

Sources: [checkout/action.yml:1-119]()

## Standardized Checkout Action

The checkout action serves as the primary infrastructure component, providing a comprehensive wrapper around GitHub's standard `actions/checkout@v4` action with enterprise-grade configurability and parameter standardization.

### Input Parameter Categories

The checkout action organizes its functionality into distinct parameter categories that address different aspects of repository checkout operations:

| Category | Parameters | Purpose |
|----------|------------|---------|
| Repository Configuration | `repository`, `ref`, `github-server-url` | Target repository identification |
| Authentication | `token`, `ssh-key`, `ssh-known-hosts`, `ssh-strict`, `ssh-user` | Secure repository access |
| Credential Management | `persist-credentials` | Git credential handling |
| Checkout Behavior | `path`, `clean`, `fetch-depth`, `fetch-tags`, `show-progress` | Basic checkout operations |
| Advanced Features | `filter`, `sparse-checkout`, `sparse-checkout-cone-mode`, `lfs`, `submodules` | Specialized checkout modes |
| Security | `set-safe-directory` | Git security configuration |

Sources: [checkout/action.yml:18-92]()

### Parameter Flow and Default Values

```mermaid
flowchart TD
    subgraph "Input Processing"
        github_context["GitHub Context Variables"]
        default_values["Action Default Values"]
        user_inputs["User-Provided Inputs"]
    end
    
    subgraph "Parameter Resolution"
        repository_param["repository: ${{ github.repository }}"]
        token_param["token: ${{ github.token }}"]
        ssh_strict_param["ssh-strict: 'true'"]
        ssh_user_param["ssh-user: 'git'"]
        persist_creds_param["persist-credentials: 'true'"]
        clean_param["clean: 'true'"]
        sparse_cone_param["sparse-checkout-cone-mode: 'true'"]
        fetch_depth_param["fetch-depth: '1'"]
        fetch_tags_param["fetch-tags: 'false'"]
        show_progress_param["show-progress: 'true'"]
        lfs_param["lfs: 'false'"]
        submodules_param["submodules: 'false'"]
        set_safe_param["set-safe-directory: 'true'"]
        github_server_param["github-server-url: 'https://github.com'"]
    end
    
    subgraph "actions/checkout@v4"
        checkout_execution["Repository Checkout Execution"]
    end
    
    github_context --> repository_param
    github_context --> token_param
    default_values --> ssh_strict_param
    default_values --> clean_param
    default_values --> fetch_depth_param
    
    user_inputs --> repository_param
    user_inputs --> token_param
    user_inputs --> ssh_strict_param
    
    repository_param --> checkout_execution
    token_param --> checkout_execution
    ssh_strict_param --> checkout_execution
    clean_param --> checkout_execution
    fetch_depth_param --> checkout_execution
```

Sources: [checkout/action.yml:19-29](), [checkout/action.yml:39-93]()

## Implementation Pattern

The checkout action implements a transparent wrapper pattern that preserves all upstream functionality while adding standardized defaults and comprehensive parameter support.

### Composite Action Structure

The action uses GitHub's composite action pattern to create a single-step wrapper that passes all parameters directly to the upstream `actions/checkout@v4` action:

```mermaid
graph LR
    subgraph "checkout/action.yml Structure"
        inputs_section["inputs: (22 parameters)"]
        runs_section["runs: composite"]
        steps_section["steps: single checkout step"]
    end
    
    subgraph "Parameter Mapping"
        input_repository["inputs.repository"]
        input_ref["inputs.ref"]
        input_token["inputs.token"]
        input_ssh_key["inputs.ssh-key"]
        input_path["inputs.path"]
        input_clean["inputs.clean"]
        input_fetch_depth["inputs.fetch-depth"]
    end
    
    subgraph "actions/checkout@v4 Integration"
        with_repository["with.repository"]
        with_ref["with.ref"]
        with_token["with.token"]
        with_ssh_key["with.ssh-key"]
        with_path["with.path"]
        with_clean["with.clean"]
        with_fetch_depth["with.fetch-depth"]
    end
    
    inputs_section --> input_repository
    input_repository --> with_repository
    input_ref --> with_ref
    input_token --> with_token
    input_ssh_key --> with_ssh_key
    input_path --> with_path
    input_clean --> with_clean
    input_fetch_depth --> with_fetch_depth
```

Sources: [checkout/action.yml:94-119]()

## Enterprise Configuration Support

The checkout action provides enterprise-grade configuration options that address common requirements in large-scale development environments.

### Authentication Methods

The action supports multiple authentication mechanisms for different enterprise scenarios:

- **Token Authentication**: Default GitHub token with option for custom tokens
- **SSH Authentication**: Full SSH key support with known hosts and strict checking
- **Credential Persistence**: Configurable credential storage for subsequent Git operations

### Advanced Checkout Features

Enterprise-specific features include:

- **Sparse Checkout**: Partial repository checkout with cone mode optimization
- **LFS Support**: Git Large File Storage integration
- **Submodule Handling**: Recursive submodule checkout options
- **Filter Support**: Partial clone capabilities for large repositories
- **Security Configuration**: Safe directory settings for containerized environments

Sources: [checkout/action.yml:30-43](), [checkout/action.yml:55-88]()

## Integration with Ecosystem

The standardized checkout action serves as a foundational component across the spark-rapids-common ecosystem, providing consistent repository access patterns for all dependent actions and workflows.

### Consumer Integration Pattern

```mermaid
graph TB
    subgraph "Consuming Actions"
        license_header["license-header-check"]
        markdown_links["markdown-link-check"]
        shell_check["shell-check"]
        signoff_check["signoff-check"]
        pr_desc_check["pr-description-check"]
    end
    
    subgraph "checkout Action Integration"
        checkout_step["- uses: NVIDIA/spark-rapids-common/checkout@main"]
        checkout_config["with: (standardized parameters)"]
    end
    
    subgraph "Standardized Behavior"
        consistent_fetch["Consistent fetch-depth: 1"]
        consistent_clean["Consistent clean: true"]
        consistent_auth["Standardized authentication"]
        consistent_security["Consistent security settings"]
    end
    
    license_header --> checkout_step
    markdown_links --> checkout_step
    shell_check --> checkout_step
    signoff_check --> checkout_step
    pr_desc_check --> checkout_step
    
    checkout_step --> checkout_config
    checkout_config --> consistent_fetch
    checkout_config --> consistent_clean
    checkout_config --> consistent_auth
    checkout_config --> consistent_security
```

Sources: [checkout/action.yml:15-16](), [checkout/action.yml:94-98]()

The supporting infrastructure provides the essential foundation that enables the spark-rapids-common ecosystem to deliver consistent, reliable automation across multiple repositories while maintaining enterprise-grade security and configurability standards.

---


<!-- source: DeepWiki mcp.deepwiki.com · repo prompt-security/clawsec · extra page Guarded Skill Installation · fetched 2026-10-27 -->

# Guarded Skill Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/clawsec-suite/SKILL.md](skills/clawsec-suite/SKILL.md)
- [skills/clawsec-suite/skill.json](skills/clawsec-suite/skill.json)

</details>



## Purpose and Scope

This page documents the **guarded skill installation mechanism** implemented by `guarded_skill_install.mjs`, which enforces a double-confirmation pattern for installing skills with known security advisories. The script acts as a gatekeeper that blocks risky installations until the user explicitly acknowledges advisory warnings, preventing agents from autonomously installing malicious or vulnerable skills.

This page covers the installation guard's command-line interface, exit code signaling, advisory matching logic, and integration with agent workflows. For the broader advisory monitoring system that powers this guard, see [Advisory Feed Architecture](#3.1). For the OpenClaw hook that monitors installed skills post-installation, see [Advisory Guardian Hook](#4.1.3).

---

## Two-Step Confirmation Model

The guarded installer implements a state machine with two explicit user confirmations:

```mermaid
stateDiagram-v2
    [*] --> UserRequest: "Install helper-plus v1.0.1"
    
    UserRequest --> FirstCheck: node guarded_skill_install.mjs<br/>--skill helper-plus --version 1.0.1
    
    FirstCheck --> AdvisoryLookup: Load feed.json
    AdvisoryLookup --> MatchAdvisories: Cross-reference skill+version
    
    MatchAdvisories --> NoMatch: No advisory found
    MatchAdvisories --> MatchFound: Advisory matches
    
    NoMatch --> ProceedInstall: Exit code 0<br/>"SAFE_TO_PROCEED"
    ProceedInstall --> [*]
    
    MatchFound --> DisplayWarning: Print advisory details<br/>severity, description, URL
    DisplayWarning --> ExitWithSignal: Exit code 42<br/>"ADVISORY_FOUND"
    
    ExitWithSignal --> SecondConfirmation: User reviews and<br/>explicitly approves
    
    SecondConfirmation --> SecondCheck: node guarded_skill_install.mjs<br/>--skill helper-plus --version 1.0.1<br/>--confirm-advisory
    
    SecondCheck --> BypassGuard: Skip advisory checks
    BypassGuard --> ProceedWithWarning: Exit code 0<br/>"USER_OVERRIDE"
    ProceedWithWarning --> [*]
    
    note right of ExitWithSignal
        Exit code 42 signals:
        "Advisory found, requires
        explicit second confirmation"
    end note
    
    note right of SecondConfirmation
        Agent must obtain explicit
        user approval before retry
        with --confirm-advisory flag
    end note
```

**Sources:** [skills/clawsec-suite/SKILL.md:139-159]()

---

## Command-Line Interface

The `guarded_skill_install.mjs` script accepts three command-line arguments:

| Argument | Required | Description |
|----------|----------|-------------|
| `--skill <name>` | Yes | Skill name (normalized: lowercase, hyphens for spaces) |
| `--version <version>` | Yes | Target version in semver format (e.g., `1.0.1`) |
| `--confirm-advisory` | No | Bypass advisory checks (requires prior exit code 42) |

### Usage Examples

**First attempt (advisory check):**
```bash
SUITE_DIR="$HOME/.openclaw/skills/clawsec-suite"
node "$SUITE_DIR/scripts/guarded_skill_install.mjs" \
  --skill helper-plus \
  --version 1.0.1
```

**Exit scenarios:**
- Exit code `0`: Safe to proceed (no advisory match)
- Exit code `42`: Advisory found, requires second confirmation
- Exit code `1`: Invalid arguments or system error

**Second attempt (user override after seeing advisory):**
```bash
node "$SUITE_DIR/scripts/guarded_skill_install.mjs" \
  --skill helper-plus \
  --version 1.0.1 \
  --confirm-advisory
```

**Exit:** Code `0` (proceeds with user override)

**Sources:** [skills/clawsec-suite/SKILL.md:142-155]()

---

## Exit Code 42: Advisory Found Signal

The script uses **exit code 42** as a structured signaling mechanism to communicate "advisory found, requires explicit user confirmation" to the calling agent or script.

### Exit Code Convention

```mermaid
graph LR
    subgraph "Exit Code Semantics"
        ExitZero["Exit 0<br/>SAFE_TO_PROCEED"]
        Exit42["Exit 42<br/>ADVISORY_FOUND"]
        ExitOne["Exit 1<br/>ERROR"]
    end
    
    subgraph "Agent Response"
        ProceedInstall["Proceed with<br/>skill installation"]
        DisplayWarning["Display advisory<br/>to user"]
        AbortOperation["Abort with<br/>error message"]
    end
    
    subgraph "User Action"
        ApprovalFlow["User reviews<br/>advisory details"]
        SecondAttempt["User explicitly<br/>confirms install"]
    end
    
    ExitZero --> ProceedInstall
    Exit42 --> DisplayWarning
    ExitOne --> AbortOperation
    
    DisplayWarning --> ApprovalFlow
    ApprovalFlow --> SecondAttempt
    SecondAttempt --> RetryWithFlag["Retry with<br/>--confirm-advisory"]
    
    style Exit42 stroke:#333,stroke-width:3px
    style ApprovalFlow stroke:#333,stroke-width:2px
```

### Why Exit Code 42?

Exit code 42 is chosen to be:
1. **Unambiguous:** Not a standard POSIX exit code (0=success, 1-2=errors, 126-130=reserved)
2. **Memorable:** References "The Answer" from The Hitchhiker's Guide to the Galaxy
3. **Grep-friendly:** Easily searchable in logs and agent code
4. **Non-destructive:** Signals "pause and confirm" rather than "error and abort"

**Agent workflow pattern:**
```bash
if node guarded_skill_install.mjs --skill foo --version 1.0.0; then
  # Exit 0: proceed with installation
  npx clawhub install foo
elif [ $? -eq 42 ]; then
  # Exit 42: show advisory and wait for user confirmation
  echo "WARNING: Advisory found. Review above details."
  echo "Confirm with: --confirm-advisory flag"
else
  # Exit 1: error condition
  echo "ERROR: Installation check failed"
fi
```

**Sources:** [skills/clawsec-suite/SKILL.md:148-151]()

---

## Advisory Matching Decision Flow

The guarded installer performs skill and version matching against the advisory feed:

```mermaid
graph TB
    Start["Parse --skill and --version<br/>arguments"]
    
    LoadFeed["Load feed.json<br/>(remote or local seed)"]
    
    NormalizeSkill["Normalize skill name<br/>(lowercase, hyphenate)"]
    
    ParseVersion["Parse semver version<br/>(major.minor.patch)"]
    
    IterateAdvisories["Iterate through<br/>advisories array"]
    
    CheckAffected["Check advisory.affected<br/>entries"]
    
    MatchSkillName["Match skill name<br/>(normalized comparison)"]
    
    CheckVersionRange["Check version constraints<br/>(.versions, .version_range)"]
    
    CollectMatches["Collect matching advisories<br/>with severity"]
    
    AnyMatches{"Found any<br/>matches?"}
    
    CheckConfirmFlag{"--confirm-advisory<br/>flag present?"}
    
    DisplayAdvisories["Print advisory details:<br/>- ID<br/>- Severity<br/>- Title<br/>- Description<br/>- URL"]
    
    Exit42["Exit with code 42<br/>ADVISORY_FOUND"]
    
    Exit0Safe["Exit with code 0<br/>SAFE_TO_PROCEED"]
    
    Exit0Override["Exit with code 0<br/>USER_OVERRIDE"]
    
    Start --> LoadFeed
    LoadFeed --> NormalizeSkill
    NormalizeSkill --> ParseVersion
    ParseVersion --> IterateAdvisories
    
    IterateAdvisories --> CheckAffected
    CheckAffected --> MatchSkillName
    MatchSkillName --> CheckVersionRange
    CheckVersionRange --> CollectMatches
    
    CollectMatches --> AnyMatches
    
    AnyMatches -->|No matches| Exit0Safe
    
    AnyMatches -->|Matches found| CheckConfirmFlag
    
    CheckConfirmFlag -->|Flag absent| DisplayAdvisories
    DisplayAdvisories --> Exit42
    
    CheckConfirmFlag -->|Flag present| Exit0Override
    
    style Exit42 stroke:#333,stroke-width:3px
    style CheckConfirmFlag stroke:#333,stroke-width:2px
    style DisplayAdvisories stroke:#333,stroke-width:2px
```

### Version Matching Logic

The script checks three version constraint patterns from advisory entries:

| Advisory Field | Matching Strategy | Example |
|----------------|-------------------|---------|
| `.versions[]` | Exact match array | `["1.0.0", "1.0.1"]` matches if `version` is in array |
| `.version_range.min` / `.max` | Semver range | `min: "1.0.0", max: "2.0.0"` matches `1.5.0` |
| `.version_range.pattern` | Wildcard patterns | `1.0.*` matches `1.0.0` through `1.0.999` |

**Normalization rules:**
- Skill names: lowercase, spaces → hyphens (e.g., `"Helper Plus"` → `"helper-plus"`)
- Versions: strict semver parsing, no prefixes (e.g., `v1.0.0` → `1.0.0`)

**Sources:** [skills/clawsec-suite/SKILL.md:148-155]()

---

## Integration with Agent Workflows

### Recommended Agent Pattern

Agents should implement the following workflow when handling skill installation requests:

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant GuardScript as guarded_skill_install.mjs
    participant Feed as Advisory Feed
    participant Installer as clawhub/curl
    
    User->>Agent: "Install helper-plus v1.0.1"
    Note over Agent: First confirmation: user request
    
    Agent->>GuardScript: node guarded_skill_install.mjs<br/>--skill helper-plus --version 1.0.1
    
    GuardScript->>Feed: Fetch/load feed.json
    Feed-->>GuardScript: Advisory data
    
    GuardScript->>GuardScript: Match skill+version against advisories
    
    alt No advisory match
        GuardScript-->>Agent: Exit 0 (SAFE_TO_PROCEED)
        Agent->>Installer: npx clawhub install helper-plus
        Installer-->>Agent: Installation complete
        Agent-->>User: "helper-plus v1.0.1 installed"
    else Advisory found
        GuardScript-->>Agent: Exit 42 (ADVISORY_FOUND)<br/>+ advisory details printed to stderr
        Agent-->>User: "WARNING: Advisory CLAW-2026-0042<br/>Severity: HIGH<br/>[details]<br/>Continue anyway?"
        
        User->>Agent: "Yes, install anyway"
        Note over Agent: Second confirmation: explicit override
        
        Agent->>GuardScript: node guarded_skill_install.mjs<br/>--skill helper-plus --version 1.0.1<br/>--confirm-advisory
        GuardScript-->>Agent: Exit 0 (USER_OVERRIDE)
        
        Agent->>Installer: npx clawhub install helper-plus
        Installer-->>Agent: Installation complete
        Agent-->>User: "helper-plus v1.0.1 installed<br/>(user override of advisory)"
    else Error condition
        GuardScript-->>Agent: Exit 1 (ERROR)
        Agent-->>User: "Installation check failed"
    end
```

### Shell Script Example

```bash
#!/bin/bash
set -euo pipefail

SKILL_NAME="$1"
SKILL_VERSION="$2"
SUITE_DIR="${HOME}/.openclaw/skills/clawsec-suite"
GUARD_SCRIPT="${SUITE_DIR}/scripts/guarded_skill_install.mjs"

# First attempt: check for advisories
if node "$GUARD_SCRIPT" --skill "$SKILL_NAME" --version "$SKILL_VERSION" 2>/tmp/advisory_warning; then
  # Exit 0: safe to proceed
  echo "No advisories found. Proceeding with installation."
  npx clawhub@latest install "$SKILL_NAME"
  exit 0
fi

EXIT_CODE=$?

if [ "$EXIT_CODE" -eq 42 ]; then
  # Advisory found: display warning and prompt for confirmation
  cat /tmp/advisory_warning
  echo ""
  echo "An advisory was found for this skill. Install anyway? (yes/no)"
  read -r CONFIRMATION
  
  if [ "$CONFIRMATION" = "yes" ]; then
    # Second attempt with explicit override
    node "$GUARD_SCRIPT" --skill "$SKILL_NAME" --version "$SKILL_VERSION" --confirm-advisory
    npx clawhub@latest install "$SKILL_NAME"
    echo "Installed $SKILL_NAME v$SKILL_VERSION (user override)"
  else
    echo "Installation cancelled by user."
    exit 1
  fi
else
  # Other error
  echo "ERROR: Installation guard failed with exit code $EXIT_CODE"
  cat /tmp/advisory_warning
  exit 1
fi
```

**Sources:** [skills/clawsec-suite/SKILL.md:139-159]()

---

## Implementation Details

### Script Location and Permissions

- **Path:** `skills/clawsec-suite/scripts/guarded_skill_install.mjs`
- **Type:** Node.js module script (`.mjs` extension)
- **Permissions:** Should be readable and executable (`644` or `755`)
- **Dependencies:** Shared libraries from `hooks/clawsec-advisory-guardian/lib/`

### Shared Library Dependencies

The guarded installer reuses code from the advisory guardian hook:

```mermaid
graph TB
    GuardScript["guarded_skill_install.mjs<br/>(Main script)"]
    
    UtilsLib["lib/utils.mjs<br/>- normalizeSkillName()<br/>- isObject()<br/>- uniqueStrings()"]
    
    VersionLib["lib/version.mjs<br/>- parseSemver()<br/>- matchesVersionConstraint()<br/>- matchesPattern()"]
    
    FeedLib["lib/feed.mjs<br/>- loadAdvisoryFeed()<br/>- validateFeedStructure()<br/>- fetchRemoteFeed()"]
    
    FeedJSON["advisories/feed.json<br/>(Local seed)"]
    
    RemoteFeed["https://raw.githubusercontent.com/<br/>prompt-security/clawsec/<br/>main/advisories/feed.json"]
    
    GuardScript --> UtilsLib
    GuardScript --> VersionLib
    GuardScript --> FeedLib
    
    FeedLib --> FeedJSON
    FeedLib --> RemoteFeed
    
    UtilsLib -.->|"normalizeSkillName()"| GuardScript
    VersionLib -.->|"matchesVersionConstraint()"| GuardScript
    FeedLib -.->|"loadAdvisoryFeed()"| GuardScript
    
    style GuardScript stroke:#333,stroke-width:3px
```

### Feed Loading Priority

The script attempts to load the advisory feed in this order:

1. **Remote feed:** `$CLAWSEC_FEED_URL` or default GitHub raw URL
2. **Local seed:** `~/.openclaw/skills/clawsec-suite/advisories/feed.json`
3. **Fail:** Exit with code 1 if both sources unavailable

### Advisory Matching Algorithm

The core matching logic follows this pseudocode:

```
function matchAdvisories(skillName, version, advisories):
    matches = []
    normalizedSkill = normalizeSkillName(skillName)
    parsedVersion = parseSemver(version)
    
    for advisory in advisories:
        if not advisory.affected:
            continue
            
        for affectedEntry in advisory.affected:
            if normalizeSkillName(affectedEntry.skill) != normalizedSkill:
                continue
                
            if matchesVersionConstraint(affectedEntry, parsedVersion):
                matches.append({
                    id: advisory.id,
                    severity: advisory.severity,
                    title: advisory.title,
                    description: advisory.description,
                    url: advisory.url
                })
                break  # One match per advisory is sufficient
    
    return matches
```

**Sources:** [skills/clawsec-suite/skill.json:77-80](), [skills/clawsec-suite/SKILL.md:139-159]()

---

## Output Format

The script outputs advisory details to **stderr** when exit code 42 is triggered:

### Sample Output (Exit Code 42)

```
ADVISORY FOUND: Installation blocked pending user confirmation

Advisory ID: CLAW-2026-0042
Severity: HIGH
Title: Data Exfiltration in helper-plus v1.0.0-1.0.2
Description: The helper-plus skill versions 1.0.0 through 1.0.2 contain a
             vulnerability that allows unauthorized transmission of workspace
             data to external servers.
URL: https://github.com/prompt-security/clawsec/issues/42

To proceed anyway, retry with: --confirm-advisory

Exit code: 42
```

### Sample Output (Exit Code 0, No Match)

```
SAFE_TO_PROCEED: No advisories found for helper-plus v1.0.1
Exit code: 0
```

### Sample Output (Exit Code 0, User Override)

```
USER_OVERRIDE: Proceeding with installation despite advisory (--confirm-advisory flag)
Exit code: 0
```

**Sources:** [skills/clawsec-suite/SKILL.md:148-155]()

---

## Security Considerations

### Non-Destructive Default

The guarded installer is **non-destructive by default**:
- Exit code 42 does not install anything
- Exit code 42 does not modify any files
- Only informs and requests explicit user approval

### Bypass Prevention

The `--confirm-advisory` flag does not bypass the guard; it **requires prior knowledge** of the advisory:

1. First invocation without flag → Exit 42 displays advisory details
2. User reviews advisory content
3. Second invocation with flag → User has explicitly acknowledged risk

This prevents automated bypass scenarios where an agent might add `--confirm-advisory` preemptively without showing advisory details to the user.

### Rate Limiting Considerations

The guarded installer makes one feed fetch per invocation. For frequent installation checks, consider:
- Using the local seed (`advisories/feed.json`) as fallback
- Implementing client-side caching with the suite's state file
- Rate-limiting installation attempts at the agent level

**Sources:** [skills/clawsec-suite/SKILL.md:223-234]()

---

## Relationship to Other Components

```mermaid
graph TB
    subgraph "Installation Request Flow"
        UserRequest["User requests skill install"]
        AgentDecision["Agent decides to install"]
    end
    
    subgraph "Guarded Installation Gate"
        GuardScript["guarded_skill_install.mjs<br/>(This component)"]
        AdvisoryLookup["Advisory feed lookup"]
        ExitCode["Exit code decision:<br/>0, 42, or 1"]
    end
    
    subgraph "Advisory System"
        FeedJSON["feed.json<br/>(See page 3.1)"]
        PollWorkflow["NVD polling<br/>(See page 3.2)"]
        CommunityReports["Community reports<br/>(See page 3.3)"]
    end
    
    subgraph "Post-Installation Monitoring"
        AdvisoryHook["clawsec-advisory-guardian<br/>(See page 4.1.3)"]
        Heartbeat["HEARTBEAT.md<br/>(See page 4.1.4)"]
    end
    
    subgraph "Actual Installation"
        ClawHub["npx clawhub install"]
        ManualInstall["curl + checksum verify"]
    end
    
    UserRequest --> AgentDecision
    AgentDecision --> GuardScript
    
    GuardScript --> AdvisoryLookup
    AdvisoryLookup --> FeedJSON
    
    PollWorkflow --> FeedJSON
    CommunityReports --> FeedJSON
    
    AdvisoryLookup --> ExitCode
    
    ExitCode -->|"Exit 0"| ClawHub
    ExitCode -->|"Exit 0"| ManualInstall
    ExitCode -->|"Exit 42"| UserApproval["User approval required"]
    UserApproval --> GuardScript
    
    ClawHub --> InstalledSkill["Skill installed in<br/>~/.openclaw/skills/"]
    ManualInstall --> InstalledSkill
    
    InstalledSkill --> AdvisoryHook
    AdvisoryHook --> Heartbeat
    
    style GuardScript stroke:#333,stroke-width:4px
    style ExitCode stroke:#333,stroke-width:3px
```

The guarded installer operates as a **pre-installation gate**, complementing:
- **Advisory guardian hook** ([#4.1.3](#4.1.3)): Monitors already-installed skills
- **Heartbeat workflow** ([#4.1.4](#4.1.4)): Periodic advisory checks
- **Advisory feed** ([#3.1](#3.1)): Source of threat intelligence

**Sources:** [skills/clawsec-suite/SKILL.md:1-252](), [skills/clawsec-suite/skill.json:1-175]()

---


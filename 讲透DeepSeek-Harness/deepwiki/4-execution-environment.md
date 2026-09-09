> 来源: [https://deepwiki.com/deepseek-ai/deepseek-harness/4-execution-environment](https://deepwiki.com/deepseek-ai/deepseek-harness/4-execution-environment)
> DeepWiki deepseek-ai/deepseek-harness

# Execution Environment

  Relevant source files 
 - [.agents/notes/implemented/architecture/2026-08-27-process-table-snapshots.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/architecture/2026-08-27-process-table-snapshots.i18n.yaml)
 - [.agents/notes/implemented/architecture/2026-08-27-process-table-snapshots.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/architecture/2026-08-27-process-table-snapshots.md?plain=1)
 - [.agents/notes/implemented/architecture/2026-08-27-process-table-snapshots.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/architecture/2026-08-27-process-table-snapshots.zh.md?plain=1)
 - [.agents/notes/implemented/feature/2026-08-08-windows-acl-restricted-token-sandbox.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/feature/2026-08-08-windows-acl-restricted-token-sandbox.i18n.yaml)
 - [.agents/notes/implemented/feature/2026-08-08-windows-acl-restricted-token-sandbox.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/feature/2026-08-08-windows-acl-restricted-token-sandbox.md?plain=1)
 - [.agents/notes/implemented/feature/2026-08-08-windows-acl-restricted-token-sandbox.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/feature/2026-08-08-windows-acl-restricted-token-sandbox.zh.md?plain=1)
 - [packages/fs/fs-local/README.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/README.i18n.yaml)
 - [packages/fs/fs-local/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/README.md?plain=1)
 - [packages/fs/fs-local/README.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/README.zh.md?plain=1)
 - [packages/fs/fs-local/package.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/package.json)
 - [packages/fs/fs-local/src/fsio.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/src/fsio.ts)
 - [packages/fs/fs-local/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/src/index.ts)
 - [packages/fs/fs-local/tests/filesystem.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/tests/filesystem.spec.ts)
 - [packages/fs/fs-local/tests/fsio.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/tests/fsio.spec.ts)
 - [packages/fs/fs/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs/README.md?plain=1)
 - [packages/fs/fs/package.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs/package.json)
 - [packages/fs/fs/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs/src/index.ts)
 - [packages/fs/fs/src/types.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs/src/types.ts)
 - [packages/fs/fs/tests/service.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs/tests/service.spec.ts)
 - [packages/fs/tool-fs/README.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/tool-fs/README.i18n.yaml)
 - [packages/fs/tool-fs/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/tool-fs/README.md?plain=1)
 - [packages/fs/tool-fs/README.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/tool-fs/README.zh.md?plain=1)
 - [packages/fs/tool-fs/package.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/tool-fs/package.json)
 - [packages/fs/tool-fs/src/edit.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/tool-fs/src/edit.ts)
 - [packages/fs/tool-fs/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/tool-fs/src/index.ts)
 - [packages/fs/tool-fs/src/read.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/tool-fs/src/read.ts)
 - [packages/fs/tool-fs/src/write.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/tool-fs/src/write.ts)
 - [packages/fs/tool-fs/tests/integration.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/tool-fs/tests/integration.spec.ts)
 - [packages/fs/tool-fs/tests/tools.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/tool-fs/tests/tools.spec.ts)
 - [packages/sandbox/sandbox-local/README.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-local/README.i18n.yaml)
 - [packages/sandbox/sandbox-local/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-local/README.md?plain=1)
 - [packages/sandbox/sandbox-local/README.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-local/README.zh.md?plain=1)
 - [packages/sandbox/sandbox-local/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-local/src/index.ts)
 - [packages/sandbox/sandbox-local/src/profiles.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-local/src/profiles.ts)
 - [packages/sandbox/sandbox-local/tests/local.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-local/tests/local.spec.ts)
 - [packages/sandbox/sandbox-local/tests/seatbelt.e2e.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-local/tests/seatbelt.e2e.ts)
 - [packages/sandbox/sandbox-policy/package.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-policy/package.json)
 - [packages/sandbox/sandbox-policy/tsconfig.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-policy/tsconfig.json)
 - [packages/sandbox/sandbox-windows-acl/README.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/README.i18n.yaml)
 - [packages/sandbox/sandbox-windows-acl/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/README.md?plain=1)
 - [packages/sandbox/sandbox-windows-acl/README.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/README.zh.md?plain=1)
 - [packages/sandbox/sandbox-windows-acl/package.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/package.json)
 - [packages/sandbox/sandbox-windows-acl/src/acl.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/src/acl.ts)
 - [packages/sandbox/sandbox-windows-acl/src/ffi.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/src/ffi.ts)
 - [packages/sandbox/sandbox-windows-acl/src/grant.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/src/grant.ts)
 - [packages/sandbox/sandbox-windows-acl/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/src/index.ts)
 - [packages/sandbox/sandbox-windows-acl/src/runner.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/src/runner.ts)
 - [packages/sandbox/sandbox-windows-acl/src/spawn.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/src/spawn.ts)
 - [packages/sandbox/sandbox-windows-acl/src/token.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/src/token.ts)
 - [packages/sandbox/sandbox-windows-acl/src/win32-abi.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/src/win32-abi.ts)
 - [packages/sandbox/sandbox-windows-acl/src/workspace-sid.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/src/workspace-sid.ts)
 - [packages/sandbox/sandbox-windows-acl/tests/acl.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/tests/acl.spec.ts)
 - [packages/sandbox/sandbox-windows-acl/tests/runner.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/tests/runner.spec.ts)
 - [packages/sandbox/sandbox-windows-acl/tests/workspace-sid.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/tests/workspace-sid.spec.ts)
 - [packages/sandbox/sandbox-windows-acl/verify/abi-probe.cpp](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/verify/abi-probe.cpp)
 - [packages/sandbox/sandbox/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox/README.md?plain=1)
 - [packages/sandbox/sandbox/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox/src/index.ts)
 - [packages/subprocess/subprocess-local/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/index.ts)
 - [packages/subprocess/subprocess-local/src/process-inspector.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/process-inspector.ts)
 - [packages/subprocess/subprocess-local/src/terminal.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/terminal.ts)
 - [packages/subprocess/subprocess-local/src/windows-inspector.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/windows-inspector.ts)
 - [packages/subprocess/subprocess-local/tests/local.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/tests/local.spec.ts)
 - [packages/subprocess/subprocess-local/tests/process-exit.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/tests/process-exit.spec.ts)
 - [packages/subprocess/subprocess-local/tests/process-inspector.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/tests/process-inspector.spec.ts)
 - [packages/subprocess/subprocess-local/tests/terminal.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/tests/terminal.spec.ts)
 - [packages/subprocess/subprocess-local/tests/windows-inspector.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/tests/windows-inspector.spec.ts)
 
  The **Execution Environment** in `dsh` manages how the system interacts with the host filesystem, spawns processes, and maintains security boundaries. It is built on the **Capability Seam** pattern, where high-level tools interact with abstract interfaces (`ctx.fs`, `ctx.subprocess`) that are fulfilled by specific provider plugins (e.g., `LocalFileSystem`, `LocalSubprocessRuntime`).

 
### Core Subsystems

 The environment is divided into three primary functional areas:

 
| Area | Responsibility | Primary Services |
|---|---|---|
| Filesystem | File I/O, atomic writes, and observation tracking. | FileSystem packages/fs/fs/src/index.ts25-27 LocalFileSystem packages/fs/fs-local/src/index.ts64 |
| Subprocess | Shell execution, PTY management, and process trees. | SubprocessRuntime packages/subprocess/subprocess/src/index.ts23 LocalSubprocessRuntime packages/subprocess/subprocess-local/src/index.ts37 |
| Sandboxing | Resource restriction and security policies. | SandboxProvider packages/sandbox/sandbox/src/index.ts37 Landlock (Linux), Windows ACL |

 
### System Architecture: From Tools to OS

 The following diagram illustrates how natural language tool calls from an agent are translated into concrete OS-level operations through the capability seams.

 **Tool-to-Entity Mapping**

 
```

```

 Sources: [packages/fs/tool-fs/src/read.ts136-163](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/tool-fs/src/read.ts#L136-L163) [packages/subprocess/subprocess-local/src/index.ts146-157](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/index.ts#L146-L157) [packages/fs/fs-local/src/index.ts64-77](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/src/index.ts#L64-L77)

 
---

 
### Filesystem & Observation

 The filesystem layer provides a unified interface for file operations with a focus on safety and consistency.

 
 - **Atomic Operations**: All writes are performed via a "write-then-rename" pattern to prevent partial file corruption [packages/fs/fs-local/src/fsio.ts4-5](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/src/fsio.ts#L4-L5) Writes stage an exclusive owner-only file in a private sibling directory and atomically publish it [packages/fs/fs-local/src/fsio.ts2-4](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/src/fsio.ts#L2-L4)
 - **Target Identity**: Files are identified by their `realpath` (`targetKey`), ensuring that symlinks and aliases share the same stale-check state [packages/fs/fs-local/src/index.ts2-4](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/src/index.ts#L2-L4)
 - **Observation Policy**: Tools like `read`, `write`, and `edit` emit `fs/observed` events [packages/fs/tool-fs/src/read.ts162](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/tool-fs/src/read.ts#L162-L162) This allows a policy plugin to enforce that a file must be read before it can be edited, using version tokens derived from high-resolution identity and freshness metadata [packages/fs/fs-local/src/fsio.ts73-76](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/src/fsio.ts#L73-L76)
 - **Concurrency**: Mutating operations (writes and edits) are serialized per `targetKey` using a mutation lock to prevent interleaving [packages/fs/fs-local/src/index.ts74-77](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/src/index.ts#L74-L77)
 
 For details on I/O primitives and search tools, see [Filesystem Tools & Observation](https://deepwiki.com/deepseek-ai/deepseek-harness/4.1-filesystem-tools-and-observation).

 
### Shell, Subprocess & Terminal

 `dsh` manages processes as **detached process trees**. This ensures that if a parent process is killed, all descendants (like a compiler spawned by a build script) are also reaped.

 
 - **Local Subprocess**: Uses POSIX process groups or Windows `taskkill` to manage trees [packages/subprocess/subprocess-local/src/spawn.ts2-6](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/spawn.ts#L2-L6) It includes a `SIGTERM` → grace period → `SIGKILL` escalation ladder [packages/subprocess/subprocess-local/src/index.ts33-35](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/index.ts#L33-L35)
 - **PTY Support**: Provides persistent terminal sessions via `node-pty`, allowing interactive shell tools to maintain state across steps [packages/subprocess/subprocess-local/src/index.ts161-180](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/index.ts#L161-L180)
 - **Output Collection**: Streams are captured by `OutputCollector` with bounded in-memory tails and optional "spill files" for large logs [packages/subprocess/subprocess-local/src/spawn.ts104-113](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/spawn.ts#L104-L113)
 - **Process Table Snapshots**: To optimize performance, the platform process table is read at most once per readiness poll or teardown pass via `ProcessSnapshot` [packages/subprocess/subprocess-local/src/process-inspector.ts20-33](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/process-inspector.ts#L20-L33)
 
 For details on shell tools and PTY management, see [Shell, Subprocess & Terminal](https://deepwiki.com/deepseek-ai/deepseek-harness/4.2-shell-subprocess-and-terminal).

 
### Sandboxing & Security

 The execution environment is designed to be restricted by default.

 
 - **Linux**: Uses `Landlock` via the `landlock-run` native addon to provide fine-grained filesystem access control [packages/sandbox/sandbox-local/src/index.ts28-33](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-local/src/index.ts#L28-L33)
 - **Windows**: Employs a `WRITE_RESTRICTED` token whose restricting SIDs include distinct workspace and temp write SIDs added to DACLs [packages/sandbox/sandbox-windows-acl/src/index.ts3-13](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/src/index.ts#L3-L13)
 - **Approval Seam**: High-risk operations (like modifying files outside a workspace) can be routed through an approval flow (`ctx.approval`) before execution [packages/fs/tool-fs/README.md66-69](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/tool-fs/README.md?plain=1#L66-L69)
 - **Environment Scrubbing**: Subprocesses are spawned with a credential-scrubbed environment to prevent leaking host secrets [packages/subprocess/subprocess-local/src/index.ts31-35](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/index.ts#L31-L35)
 
 For details on security configurations and platform-specific sandboxing, see [Sandboxing & Security](https://deepwiki.com/deepseek-ai/deepseek-harness/4.3-sandboxing-and-security).

 
---

 
### Execution Lifecycle

 The following diagram shows the lifecycle of a subprocess managed by `LocalSubprocessRuntime`, including how it handles clean teardown during host exit.

 **Subprocess Lifecycle & Cleanup**

 
```

```

 Sources: [packages/subprocess/subprocess-local/src/index.ts49-60](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/index.ts#L49-L60) [packages/subprocess/subprocess-local/src/index.ts79-102](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/index.ts#L79-L102) [packages/subprocess/subprocess-local/src/spawn.ts169-181](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/spawn.ts#L169-L181)

 **Sources:**

 
 - [packages/fs/fs-local/src/fsio.ts1-111](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/src/fsio.ts#L1-L111)
 - [packages/subprocess/subprocess-local/src/index.ts37-157](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/index.ts#L37-L157)
 - [packages/fs/fs-local/src/index.ts64-171](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/fs-local/src/index.ts#L64-L171)
 - [packages/fs/tool-fs/src/read.ts136-163](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/fs/tool-fs/src/read.ts#L136-L163)
 - [packages/subprocess/subprocess-local/src/spawn.ts1-181](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/spawn.ts#L1-L181)
 - [packages/sandbox/sandbox-windows-acl/src/index.ts1-130](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/sandbox/sandbox-windows-acl/src/index.ts#L1-L130)
 - [packages/subprocess/subprocess-local/src/process-inspector.ts20-96](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/subprocess/subprocess-local/src/process-inspector.ts#L20-L96)

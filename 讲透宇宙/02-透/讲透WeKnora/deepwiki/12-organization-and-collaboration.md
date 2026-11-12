> 来源: [https://deepwiki.com/Tencent/WeKnora/12-organization-and-collaboration](https://deepwiki.com/Tencent/WeKnora/12-organization-and-collaboration)
> DeepWiki Tencent/WeKnora

# Organization and Collaboration

  Relevant source files 
 - [frontend/src/api/organization/index.ts](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/organization/index.ts)
 - [frontend/src/views/organization/OrganizationSettingsModal.vue](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/organization/OrganizationSettingsModal.vue)
 - [internal/application/repository/agent_share.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/agent_share.go)
 - [internal/application/repository/kbshare.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/kbshare.go)
 - [internal/application/repository/organization.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/repository/organization.go)
 - [internal/application/service/agent_share.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_share.go)
 - [internal/application/service/kbshare.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/kbshare.go)
 - [internal/application/service/organization.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/organization.go)
 - [internal/handler/organization.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/organization.go)
 - [internal/types/interfaces/organization.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/interfaces/organization.go)
 - [internal/types/organization.go](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/organization.go)
 
  This document describes WeKnora's multi-tenant collaboration framework, including organizations (shared spaces), resource sharing mechanisms, and permission models. These features enable teams to collaborate on knowledge bases and agents while maintaining tenant isolation and granular access control.

 For general system architecture and multi-tenancy design, see [Security and Multi-Tenancy](https://deepwiki.com/Tencent/WeKnora/3.5-security-and-multi-tenancy). For tenant-specific configuration, see [Configuration Reference](https://deepwiki.com/Tencent/WeKnora/8-configuration-reference). For knowledge base and agent management outside of collaboration contexts, see [Knowledge Base Management](https://deepwiki.com/Tencent/WeKnora/4-knowledge-base-management) and [Agent Mode and Tool Integration](https://deepwiki.com/Tencent/WeKnora/5.3-agent-mode-and-tool-integration).

 For details on organization lifecycle, see [Organization Management](https://deepwiki.com/Tencent/WeKnora/12.1-organization-management). For details on resource sharing, see [Resource Sharing](https://deepwiki.com/Tencent/WeKnora/12.2-resource-sharing).

 
---

 
## Core Concepts

 
### Tenants

 Tenants are the top-level isolation boundary in WeKnora. Organization membership is keyed to the **tenant** rather than individual users [internal/application/service/organization.go42-45](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/organization.go#L42-L45) This design ensures permissions are stable and consistent at the organizational level, even if users change roles or leave the tenant. The entity `OrganizationTenantMember` tracks this relationship by tenant rather than by user, with the `RepresentativeUserID` used only for UI and audit purposes [internal/types/organization.go109-114](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/organization.go#L109-L114)

 
### Organizations (Shared Spaces)

 Organizations, also known as "共享空间" (Shared Spaces) in the UI, act as collaborative cross-tenant workspaces. They enable tenants to share resources such as knowledge bases and intelligent agents while preserving original ownership and tenant context [internal/types/organization.go60-61](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/organization.go#L60-L61) Organizations support joining via invitation codes with configurable expiry, allowing controlled multi-tenant collaboration [internal/types/organization.go79-84](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/organization.go#L79-L84)

 
### Permission Roles

 WeKnora uses a three-tier role-based access control (RBAC) system for organizations with roles defined as Admin, Editor, and Viewer [internal/types/organization.go9-19](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/organization.go#L9-L19) Permissions for shared resources are computed by combining the explicit share grant, the tenant's role within the organization, and tenant-level access caps to ensure that tenants with Viewer role remain read-only even if the share grants more rights [internal/application/service/kbshare.go27-36](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/kbshare.go#L27-L36)

 
| Role | Organization Management | Knowledge Base Permissions | Agent Permissions |
|---|---|---|---|
| Admin | Full control over settings, members, and join requests | Full control: edit content, manage settings, delete, share | Read-only access |
| Editor | Can share KBs and Agents to the organization | Can edit shared KB content, but not settings | Read-only access |
| Viewer | Can join the organization and access shared resources | View and search shared KBs only | Read-only access |

 Sources: [internal/application/service/organization.go42-45](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/organization.go#L42-L45) [internal/types/organization.go109-114](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/organization.go#L109-L114) [internal/types/organization.go9-19](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/organization.go#L9-L19) [internal/application/service/kbshare.go27-36](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/kbshare.go#L27-L36) [frontend/src/views/organization/OrganizationSettingsModal.vue48-52](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/organization/OrganizationSettingsModal.vue#L48-L52)

 
---

 
## Organization Architecture

 
### Data Model Linking Natural Language Space and Code Entity Space

 The organization collaboration feature acts as a bridge connecting the user's organizational context in natural language terms ("Shared Spaces") to the underlying code entities that manage membership, resource sharing, and roles.

 Diagram: Organization Data Model Mapping

 
```

```

 
 - `Organization` entities define the shared workspace with metadata, invite codes, and limits [internal/types/organization.go61-102](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/organization.go#L61-L102)
 - `OrganizationTenantMember` tracks which tenants belong to an organization and their assigned roles [internal/types/organization.go115-127](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/organization.go#L115-L127)
 - `KnowledgeBaseShare` and `AgentShare` represent knowledge bases and agents shared to the organization along with access permissions [internal/application/service/kbshare.go113-122](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/kbshare.go#L113-L122) [internal/application/service/agent_share.go169-178](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_share.go#L169-L178)
 
 Sources: [internal/types/organization.go61-102](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/organization.go#L61-L102) [internal/types/organization.go115-127](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/organization.go#L115-L127) [internal/application/service/kbshare.go113-122](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/kbshare.go#L113-L122) [internal/application/service/agent_share.go169-178](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_share.go#L169-L178)

 
---

 
## Permission Resolution Flow

 User access to shared resources is resolved primarily based on the caller’s tenant membership and role in the organization, as seen in the main HTTP handler and service layers.

 Diagram: Tenant Permission Resolution Pipeline

 
```

```

 This logic ensures organizations maintain strict tenant-bound access, supported by invite codes for joining. Non-members cannot enumerate private organizations; only members or those who join via valid invite can access organization details [internal/handler/organization.go136-141](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/organization.go#L136-L141)

 Sources: [internal/handler/organization.go75-76](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/organization.go#L75-L76) [internal/handler/organization.go113-146](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/organization.go#L113-L146) [internal/application/service/kbshare.go68-73](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/kbshare.go#L68-L73) [internal/application/service/organization.go275-285](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/organization.go#L275-L285)

 
---

 
## Resource Sharing Mechanisms

 
### Knowledge Base Sharing

 Knowledge bases can be shared cross-tenant via organizations by tenants with sufficient roles. The `KBShareService` manages sharing permissions, enforcing that only tenants with Editor or Admin roles in the target organization may share KBs to it [internal/application/service/kbshare.go98-107](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/kbshare.go#L98-L107)

 Effective permissions for accessing shared KBs account for:

 
 - The explicit share permission granted to the organization [internal/types/organization.go75-76](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/organization.go#L75-L76)
 - The role of the tenant in that organization [internal/types/organization.go77-78](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/organization.go#L77-L78)
 - A tenant role cap that prevents tenants with Viewer role in their own tenant from gaining editing rights via shares [internal/application/service/kbshare.go69-73](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/kbshare.go#L69-L73)
 
 For details, see [Resource Sharing](https://deepwiki.com/Tencent/WeKnora/12.2-resource-sharing).

 Sources: [internal/application/service/kbshare.go78-107](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/kbshare.go#L78-L107) [internal/types/interfaces/organization.go93-103](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/interfaces/organization.go#L93-L103)

 
---

 
### Agent Sharing

 Agents are also shareable within organizations with strict constraints:

 
 - Sharing can only be done by the agent's owning tenant [internal/application/service/agent_share.go154-159](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_share.go#L154-L159)
 - Agents must be fully configured (have chat and rerank models if `knowledge_search` tool is enabled) to be shared [internal/application/service/agent_share.go162-167](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_share.go#L162-L167)
 - Cross-tenant agent shares grant read-only `Viewer` access only [internal/application/service/agent_share.go150](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_share.go#L150-L150); editing agents across tenants is not supported.
 - Only tenants with Editor or Admin roles in the target org may share agents into it [internal/application/service/agent_share.go177-185](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_share.go#L177-L185)
 
 For details, see [Resource Sharing](https://deepwiki.com/Tencent/WeKnora/12.2-resource-sharing).

 Sources: [internal/application/service/agent_share.go148-187](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_share.go#L148-L187) [internal/application/service/agent_share.go40-57](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/agent_share.go#L40-L57)

 
---

 
## Organization Management UI

 The frontend includes a dedicated interface for managing organizations and shared resources, accessible through the "Shared Spaces" section. Management is supported by Vue.js stores and modal components [frontend/src/views/organization/OrganizationSettingsModal.vue1-37](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/organization/OrganizationSettingsModal.vue#L1-L37)

 
 - The `OrganizationSettingsModal.vue` component supports editing organization details [frontend/src/views/organization/OrganizationSettingsModal.vue48-104](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/organization/OrganizationSettingsModal.vue#L48-L104)
 - Tenant admins can configure invite codes, membership limits, and view pending join requests [frontend/src/views/organization/OrganizationSettingsModal.vue107-123](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/organization/OrganizationSettingsModal.vue#L107-L123)
 - Resource sharing is managed via navigation items for Knowledge Bases and Agents [frontend/src/views/organization/OrganizationSettingsModal.vue20-35](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/organization/OrganizationSettingsModal.vue#L20-L35)
 
 Diagram: Organization Resource Counts Integration Flow

 
```

```

 Sources: [internal/handler/organization.go157-196](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/handler/organization.go#L157-L196) [frontend/src/stores/organization.ts112-116](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/stores/organization.ts#L112-L116) [frontend/src/api/organization/index.ts187-196](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/organization/index.ts#L187-L196) [frontend/src/views/organization/OrganizationSettingsModal.vue20-35](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/views/organization/OrganizationSettingsModal.vue#L20-L35)

 
---

 
## Summary

 This page provides a high-level overview of WeKnora's organization and collaboration model, aimed at enabling multi-tenant teamwork through shared spaces and resource sharing. Key concepts include tenant-based membership, invite codes, strict role-based permission resolution, and distinct sharing mechanisms for knowledge bases and agents.

 For detailed technical documentation and implementation details, please refer to the following child pages:

 
 - **[Organization Management](https://deepwiki.com/Tencent/WeKnora/12.1-organization-management)**: Covers organization lifecycle including creation, membership management, invitations, roles, and permissions.
 - **[Resource Sharing](https://deepwiki.com/Tencent/WeKnora/12.2-resource-sharing)**: Explains sharing mechanisms for knowledge bases and agents, access control policies, and shared space UI features.
 
 Sources: [internal/application/service/organization.go40-51](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/application/service/organization.go#L40-L51) [internal/types/organization.go61-102](https://github.com/Tencent/WeKnora/blob/10973ed3/internal/types/organization.go#L61-L102) [frontend/src/api/organization/index.ts4-35](https://github.com/Tencent/WeKnora/blob/10973ed3/frontend/src/api/organization/index.ts#L4-L35)

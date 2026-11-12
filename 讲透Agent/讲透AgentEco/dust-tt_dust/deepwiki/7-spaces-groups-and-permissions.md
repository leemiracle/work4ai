<!-- source: DeepWiki mcp.deepwiki.com · repo dust-tt/dust · page 7 Spaces, Groups, and Permissions · fetched 2026-10-27 -->

# Spaces, Groups, and Permissions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [front-api/routes/w/[wId]/governance-permissions.test.ts](front-api/routes/w/[wId]/governance-permissions.test.ts)
- [front-api/routes/w/[wId]/governance-permissions.ts](front-api/routes/w/[wId]/governance-permissions.ts)
- [front-api/routes/w/[wId]/groups/[groupId]/spend_limit.test.ts](front-api/routes/w/[wId]/groups/[groupId]/spend_limit.test.ts)
- [front-api/routes/w/[wId]/keys/groups.test.ts](front-api/routes/w/[wId]/keys/groups.test.ts)
- [front-api/routes/w/[wId]/keys/groups.ts](front-api/routes/w/[wId]/keys/groups.ts)
- [front-api/routes/w/[wId]/permissions.ts](front-api/routes/w/[wId]/permissions.ts)
- [front/admin/audit_log_schemas/workspace.governance_permission_updated.json](front/admin/audit_log_schemas/workspace.governance_permission_updated.json)
- [front/components/pages/workspace/governance/GovernancePageSkeleton.tsx](front/components/pages/workspace/governance/GovernancePageSkeleton.tsx)
- [front/lib/api/groups/spend_limit.test.ts](front/lib/api/groups/spend_limit.test.ts)
- [front/lib/api/groups/spend_limit.ts](front/lib/api/groups/spend_limit.ts)
- [front/lib/api/keys/scopable_groups.ts](front/lib/api/keys/scopable_groups.ts)
- [front/lib/api/permissions/governance.ts](front/lib/api/permissions/governance.ts)
- [front/lib/api/permissions/governance_seeding.test.ts](front/lib/api/permissions/governance_seeding.test.ts)
- [front/lib/api/permissions/governance_seeding.ts](front/lib/api/permissions/governance_seeding.ts)
- [front/lib/api/poke/group_permissions.ts](front/lib/api/poke/group_permissions.ts)
- [front/lib/api/spaces.test.ts](front/lib/api/spaces.test.ts)
- [front/lib/api/spaces.ts](front/lib/api/spaces.ts)
- [front/lib/auth.ts](front/lib/auth.ts)
- [front/lib/auth.workspace_permission.test.ts](front/lib/auth.workspace_permission.test.ts)
- [front/lib/dev/byok_seed.sql](front/lib/dev/byok_seed.sql)
- [front/lib/dev/dust_hive_seed.sql](front/lib/dev/dust_hive_seed.sql)
- [front/lib/dev/dust_hive_seed_schema.test.ts](front/lib/dev/dust_hive_seed_schema.test.ts)
- [front/lib/model_tiers/allowed_tiers.ts](front/lib/model_tiers/allowed_tiers.ts)
- [front/lib/resources/group_permission_governance.test.ts](front/lib/resources/group_permission_governance.test.ts)
- [front/lib/resources/group_permission_registry.test.ts](front/lib/resources/group_permission_registry.test.ts)
- [front/lib/resources/group_permission_registry.ts](front/lib/resources/group_permission_registry.ts)
- [front/lib/resources/group_permission_resource.test.ts](front/lib/resources/group_permission_resource.test.ts)
- [front/lib/resources/group_permission_resource.ts](front/lib/resources/group_permission_resource.ts)
- [front/lib/resources/group_resource.test.ts](front/lib/resources/group_resource.test.ts)
- [front/lib/resources/group_resource.ts](front/lib/resources/group_resource.ts)
- [front/lib/resources/space_resource.test.ts](front/lib/resources/space_resource.test.ts)
- [front/lib/resources/space_resource.ts](front/lib/resources/space_resource.ts)
- [front/lib/swr/governance.ts](front/lib/swr/governance.ts)
- [front/migrations/20241205_update_space_group_names.ts](front/migrations/20241205_update_space_group_names.ts)
- [front/scripts/seed/factories/seedSpace.ts](front/scripts/seed/factories/seedSpace.ts)
- [front/scripts/seed_missing_governance_capabilities.ts](front/scripts/seed_missing_governance_capabilities.ts)
- [front/tests/utils/SpaceFactory.ts](front/tests/utils/SpaceFactory.ts)
- [front/tests/utils/WorkspaceFactory.ts](front/tests/utils/WorkspaceFactory.ts)
- [front/types/api/governance.ts](front/types/api/governance.ts)
- [front/types/group_permissions.ts](front/types/group_permissions.ts)
- [front/types/groups.ts](front/types/groups.ts)

</details>



This page provides a high-level overview of Dust's workspace access control model, which is built around the concepts of **Spaces**, **Groups**, and a **group-based permission system**. This system governs how users interact with resources within a workspace, ensuring appropriate access and capabilities.

Spaces serve as organizational units for various resources, while Groups define collections of users or system entities. Permissions are then granted to these Groups, determining their access rights within specific Spaces or across the workspace.

For detailed information on each component, please refer to the linked child pages.

## Spaces and Groups

Spaces (`SpaceResource` [front/lib/resources/space_resource.ts:59-59]()) are fundamental organizational units within a Dust workspace. They can represent different contexts, such as a "system" space for internal operations, a "global" space for workspace-wide resources, "conversations" for user interactions, or "project/pod" spaces for specific projects. Each space is associated with one or more `GroupResource`s [front/lib/resources/group_resource.ts:93-93](), which define its membership and access.

Groups (`GroupResource` [front/lib/resources/group_resource.ts:93-93]()) categorize users or system entities. Different `GroupKind`s [front/types/groups.ts:38-38]() exist, such as `regular_auto` (implicitly created for resources like spaces or agents), `regular_manual` (user-created), `global` (containing all workspace members), `system` (for internal Dust operations), `agent_editors` (for agent-specific editing permissions), and `provisioned` (synced from external identity providers) [front/types/groups.ts:30-36](). Group membership can be managed manually or automatically, and groups can have associated spend limits (`poolCapAwuCredits` [front/types/groups.ts:104-104]()).

The interaction between spaces and groups is crucial for defining access. For instance, when a new space is created, a corresponding group is often generated to manage its members [front/lib/api/spaces.test.ts:134-139](). Permissions are then assigned to these groups, dictating what actions members can perform within that space.

For details on `SpaceResource` and `GroupResource` management, space kinds, group membership, and the spaces API, see [Spaces and Groups](#7.1).

**Space and Group Relationship**
```mermaid
graph TD
    subgraph "Workspace"
        W[("Workspace")]
        W --> S1(Space "Global")
        W --> S2(Space "Project X")
        W --> S3(Space "Conversation Y")
        W --> S4(Space "System")

        G1(Group "Global Group")
        G2(Group "Project X Members")
        G3(Group "Project X Editors")
        G4(Group "Conversation Y Participants")
        G5(Group "System Group")

        S1 -- "Associated with" --> G1
        S2 -- "Associated with" --> G2
        S2 -- "Associated with" --> G3
        S3 -- "Associated with" --> G4
        S4 -- "Associated with" --> G5

        G1 -- "Contains all users" --> U1(User "Alice")
        G1 -- "Contains all users" --> U2(User "Bob")
        G2 -- "Contains" --> U1
        G3 -- "Contains" --> U2
        G4 -- "Contains" --> U1
        G4 -- "Contains" --> U2
    end
```
Sources:
- [front/lib/resources/space_resource.ts:59-59]()
- [front/lib/resources/group_resource.ts:93-93]()
- [front/types/groups.ts:38-38]()
- [front/types/groups.ts:30-36]()
- [front/lib/api/spaces.test.ts:134-139]()
- [front/types/groups.ts:104-104]()

## Authentication and Authorization

The `Authenticator` class [front/lib/auth.ts:142-142]() is the central component for managing authentication and authorization within Dust. It determines a user's or system entity's identity and their associated permissions. The `Authenticator` can be instantiated from various sources, such as a user session (`fromSession`) or an API key (`fromKey`) [front/lib/auth.ts:200-200]().

Permissions are managed through `GroupPermissionResource` [front/lib/resources/group_permission_resource.ts:174-176]() and `GroupPermissionRegistry` [front/lib/resources/group_permission_registry.ts:56-59](). The registry defines the valid `GrantVerb`s [front/types/group_permissions.ts:10-10]() (actions like `read`, `write`, `admin`, `create`, `publish`) and `GrantType`s [front/types/group_permissions.ts:10-10]() (roles like `reader`, `member`, `editor`, `admin`) that can be applied to different resource types (e.g., `space`, `agent`, `skill`) [front/lib/resources/group_permission_registry.ts:60-99]().

The `Authenticator` uses these definitions to resolve a caller's permissions, including checking if a user `hasWorkspacePermission` [front/lib/auth.ts:300-300]() for a specific action on a resource. This system supports both instance-level grants (for specific resources) and type-level grants (for all resources of a certain type) [front/lib/resources/group_permission_registry.ts:48-50](). Governance capabilities, such as who can create agents or publish skills, are also managed through this permission system, often involving type-level grants to specific groups or the global group [front/lib/auth.workspace_permission.test.ts:135-148]().

For a deep dive into the `Authenticator` class, `GroupPermissionResource`, `GroupPermissionRegistry`, and the governance system, see [Authentication and Authorization](#7.2).

**Authenticator and Permission Flow**
```mermaid
graph TD
    A[("Request (User/API Key)")] --> B{Authenticator.fromSession / fromKey}
    B --> C{Resolve User/Key Identity}
    C --> D[("User/Key Context (Workspace, Groups, Role)")]
    D --> E{Authenticator.hasWorkspacePermission(verb, resourceType, resourceId)}
    E --> F{GroupPermissionRegistry: Define Roles & Verbs}
    E --> G{GroupPermissionResource: Fetch Grants for Groups}
    F -- "Validates" --> G
    G -- "Grants" --> H{Permission Decision}
    H -- "Allowed" --> I[("Access Granted")]
    H -- "Denied" --> J[("Access Denied")]
```
Sources:
- [front/lib/auth.ts:142-142]()
- [front/lib/auth.ts:200-200]()
- [front/lib/resources/group_permission_resource.ts:174-176]()
- [front/lib/resources/group_permission_registry.ts:56-59]()
- [front/types/group_permissions.ts:10-10]()
- [front/lib/resources/group_permission_registry.ts:60-99]()
- [front/lib/auth.ts:300-300]()
- [front/lib/resources/group_permission_registry.ts:48-50]()
- [front/lib/auth.workspace_permission.test.ts:135-148]()

---


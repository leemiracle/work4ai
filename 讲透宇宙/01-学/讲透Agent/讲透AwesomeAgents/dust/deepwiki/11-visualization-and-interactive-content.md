<!-- source: DeepWiki mcp.deepwiki.com · repo dust-tt/dust · page 11 Visualization and Interactive Content · fetched 2026-10-26 -->

# Visualization and Interactive Content

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [front-api/routes/share/frame/[token].ts](front-api/routes/share/frame/[token].ts)
- [front-api/routes/v1/public/frames/[token]/index.test.ts](front-api/routes/v1/public/frames/[token]/index.test.ts)
- [front-api/routes/v1/public/frames/[token]/index.ts](front-api/routes/v1/public/frames/[token]/index.ts)
- [front/components/assistant/conversation/ConversationSidePanelContainer.tsx](front/components/assistant/conversation/ConversationSidePanelContainer.tsx)
- [front/components/assistant/conversation/actions/AuthenticatedVisualizationActionIframe.test.ts](front/components/assistant/conversation/actions/AuthenticatedVisualizationActionIframe.test.ts)
- [front/components/assistant/conversation/actions/AuthenticatedVisualizationActionIframe.tsx](front/components/assistant/conversation/actions/AuthenticatedVisualizationActionIframe.tsx)
- [front/components/assistant/conversation/actions/VisualizationActionIframe.test.ts](front/components/assistant/conversation/actions/VisualizationActionIframe.test.ts)
- [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx](front/components/assistant/conversation/actions/VisualizationActionIframe.tsx)
- [front/components/assistant/conversation/constant.test.ts](front/components/assistant/conversation/constant.test.ts)
- [front/components/assistant/conversation/constant.ts](front/components/assistant/conversation/constant.ts)
- [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx](front/components/assistant/conversation/interactive_content/FrameRenderer.tsx)
- [front/components/assistant/conversation/interactive_content/InteractiveContentContainer.tsx](front/components/assistant/conversation/interactive_content/InteractiveContentContainer.tsx)
- [front/components/assistant/conversation/interactive_content/PublicFrameRenderer.test.ts](front/components/assistant/conversation/interactive_content/PublicFrameRenderer.test.ts)
- [front/components/assistant/conversation/interactive_content/PublicFrameRenderer.tsx](front/components/assistant/conversation/interactive_content/PublicFrameRenderer.tsx)
- [front/components/assistant/conversation/interactive_content/PublicInteractiveContentContainer.tsx](front/components/assistant/conversation/interactive_content/PublicInteractiveContentContainer.tsx)
- [front/components/assistant/conversation/interactive_content/PublicInteractiveContentHeader.tsx](front/components/assistant/conversation/interactive_content/PublicInteractiveContentHeader.tsx)
- [front/components/markdown/VisualizationBlock.tsx](front/components/markdown/VisualizationBlock.tsx)
- [front/components/pages/share/EmailVerificationFlow.tsx](front/components/pages/share/EmailVerificationFlow.tsx)
- [front/components/pages/share/SharedFramePage.tsx](front/components/pages/share/SharedFramePage.tsx)
- [front/components/pod/PodFrameTabContent.tsx](front/components/pod/PodFrameTabContent.tsx)
- [front/components/pod/PodFrameVisualization.tsx](front/components/pod/PodFrameVisualization.tsx)
- [front/components/pod/conversation/PodPinnedBanner.tsx](front/components/pod/conversation/PodPinnedBanner.tsx)
- [front/components/pod/files/PodFrameSheet.tsx](front/components/pod/files/PodFrameSheet.tsx)
- [front/lib/api/actions/servers/common/viz/instructions.ts](front/lib/api/actions/servers/common/viz/instructions.ts)
- [front/lib/api/actions/servers/interactive_content/index.test.ts](front/lib/api/actions/servers/interactive_content/index.test.ts)
- [front/lib/api/actions/servers/interactive_content/index.ts](front/lib/api/actions/servers/interactive_content/index.ts)
- [front/lib/api/actions/servers/interactive_content/instructions_v2.ts](front/lib/api/actions/servers/interactive_content/instructions_v2.ts)
- [front/lib/api/actions/servers/interactive_content_v2/index.ts](front/lib/api/actions/servers/interactive_content_v2/index.ts)
- [front/lib/api/actions/servers/interactive_content_v2/tools/index.test.ts](front/lib/api/actions/servers/interactive_content_v2/tools/index.test.ts)
- [front/lib/api/actions/servers/interactive_content_v2/tools/index.ts](front/lib/api/actions/servers/interactive_content_v2/tools/index.ts)
- [front/lib/api/frames/build_and_publish.test.ts](front/lib/api/frames/build_and_publish.test.ts)
- [front/lib/api/frames/build_and_publish.ts](front/lib/api/frames/build_and_publish.ts)
- [front/lib/api/frames/publication_storage.test.ts](front/lib/api/frames/publication_storage.test.ts)
- [front/lib/api/frames/publication_storage.ts](front/lib/api/frames/publication_storage.ts)
- [front/lib/api/frames/publish_from_source.test.ts](front/lib/api/frames/publish_from_source.test.ts)
- [front/lib/api/frames/publish_from_source.ts](front/lib/api/frames/publish_from_source.ts)
- [front/lib/api/sandbox_functions/slug.ts](front/lib/api/sandbox_functions/slug.ts)
- [front/lib/api/share/frame_session.ts](front/lib/api/share/frame_session.ts)
- [front/lib/api/viz/extract_file_refs.test.ts](front/lib/api/viz/extract_file_refs.test.ts)
- [front/lib/api/viz/extract_file_refs.ts](front/lib/api/viz/extract_file_refs.ts)
- [front/lib/resources/skill/code_defined/global/pod_functions.ts](front/lib/resources/skill/code_defined/global/pod_functions.ts)
- [front/lib/swr/frames.ts](front/lib/swr/frames.ts)
- [front/lib/swr/share.ts](front/lib/swr/share.ts)
- [front/types/api/frame_manifest.test.ts](front/types/api/frame_manifest.test.ts)
- [front/types/api/frame_manifest.ts](front/types/api/frame_manifest.ts)
- [front/types/api/frame_storage.test.ts](front/types/api/frame_storage.test.ts)
- [front/types/api/frame_storage.ts](front/types/api/frame_storage.ts)
- [front/types/api/pod_function_reference.test.ts](front/types/api/pod_function_reference.test.ts)
- [front/types/api/pod_function_reference.ts](front/types/api/pod_function_reference.ts)
- [front/types/assistant/visualization.ts](front/types/assistant/visualization.ts)
- [viz/app/components/VisualizationWrapper.test.ts](viz/app/components/VisualizationWrapper.test.ts)
- [viz/app/components/VisualizationWrapper.tsx](viz/app/components/VisualizationWrapper.tsx)
- [viz/app/content/ClientVisualizationWrapper.tsx](viz/app/content/ClientVisualizationWrapper.tsx)
- [viz/app/content/ServerVisualizationWrapper.tsx](viz/app/content/ServerVisualizationWrapper.tsx)
- [viz/app/content/ServerVisualizationWrapperClient.tsx](viz/app/content/ServerVisualizationWrapperClient.tsx)
- [viz/app/content/page.tsx](viz/app/content/page.tsx)
- [viz/app/lib/data-apis/cache-data-api.ts](viz/app/lib/data-apis/cache-data-api.ts)
- [viz/app/lib/data-apis/rpc-data-api.test.ts](viz/app/lib/data-apis/rpc-data-api.test.ts)
- [viz/app/lib/data-apis/rpc-data-api.ts](viz/app/lib/data-apis/rpc-data-api.ts)
- [viz/app/lib/parseFileRefs.test.ts](viz/app/lib/parseFileRefs.test.ts)
- [viz/app/lib/parseFileRefs.ts](viz/app/lib/parseFileRefs.ts)
- [viz/app/lib/pod-function-hooks.test.tsx](viz/app/lib/pod-function-hooks.test.tsx)
- [viz/app/lib/pod-function-hooks.tsx](viz/app/lib/pod-function-hooks.tsx)
- [viz/app/lib/pod-function-slug.test.ts](viz/app/lib/pod-function-slug.test.ts)
- [viz/app/lib/pod-function-slug.ts](viz/app/lib/pod-function-slug.ts)
- [viz/app/lib/visualization-api.ts](viz/app/lib/visualization-api.ts)
- [viz/app/types.ts](viz/app/types.ts)

</details>



This page details the system for rendering interactive content, primarily "Frames," within the Dust platform. It covers the visualization iframe system, the storage mechanism for published Frames, the rendering process for interactive content, and the architecture of the dedicated Next.js application (`viz`). Key components discussed include `VisualizationActionIframe`, `FrameRenderer`, the `publication_storage` module, and the integration with Pod Functions.

## Visualization Iframe System

Interactive content, such as Frames, is rendered within an `<iframe>` element to provide isolation and a controlled execution environment. The `VisualizationActionIframe` component [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:40-44]() is responsible for embedding the `viz` Next.js application and facilitating communication between the parent Dust application and the embedded Frame.

### Communication Protocol

Communication between the parent application and the `viz` iframe occurs via `postMessage`. The `VisualizationActionIframe` component handles outgoing messages to the iframe and listens for incoming messages.

**Outgoing Messages (Parent to Iframe):**
The parent sends messages to the iframe to provide configuration, data, and to trigger actions.
- `setContentHeight`: Informs the parent about the iframe's content height for resizing [viz/app/components/VisualizationWrapper.tsx:175-182]().
- `downloadFileRequest`: Requests the parent to download a file [viz/app/components/VisualizationWrapper.tsx:187-192]().
- `displayCode`: Requests the parent to display the Frame's source code [viz/app/components/VisualizationWrapper.tsx:194-196]().
- `editText`: Requests the parent to edit a file's content [viz/app/components/VisualizationWrapper.tsx:198-200]().
- `callFunction`: Invokes a Pod Function [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:330-332]().

**Incoming Messages (Iframe to Parent):**
The iframe sends messages to the parent to request data, report errors, or signal readiness.
- `answer`: Responds to a command from the parent [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:125-131]().
- `callFunction`: Requests the parent to invoke a Pod Function [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:330-332]().
- `downloadFileRequest`: Requests the parent to download a file [viz/app/components/VisualizationWrapper.tsx:187-192]().
- `displayCode`: Requests the parent to display the Frame's source code [viz/app/components/VisualizationWrapper.tsx:194-196]().
- `editText`: Requests the parent to edit a file's content [viz/app/components/VisualizationWrapper.tsx:198-200]().

The `sendResponseToIframe` [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:118-131]() and `sendErrorToIframe` [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:134-164]() functions are used by the parent to send responses and errors back to the iframe.

### `VisualizationActionIframe` Component

The `VisualizationActionIframe` component [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:40-44]() is a React component that renders the `viz` application within an `<iframe>`. It manages the lifecycle of the iframe, including loading, error handling, and communication.

Key props include:
- `vizUrl`: The URL of the `viz` Next.js application.
- `visualization`: An object containing `accessToken` and `identifier` for the Frame [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:75-85]().
- `canInvokeFunctions`: A boolean indicating if the current user can invoke Pod Functions.
- `scopedUserIdentity`: User identity information for authorization within the iframe [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:30-34]().
- `viewer`: Information about the viewer, used for blocked action cards [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:196-206]().
- `framePath`: The path to the Frame within the Pod file system.

The component uses `useEventSource` [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:4]() to listen for server-sent events related to Sandbox Function invocations, such as `SandboxFunctionMCPApproveExecutionEvent` and `SandboxFunctionToolPersonalAuthRequiredEvent` [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:7-9](). These events can trigger UI elements like `SandboxFunctionPersonalAuthCard` and `SandboxFunctionToolApprovalCard` [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:1-2]() to handle authorization flows.

```mermaid
graph TD
    A[Dust Frontend] -->|Renders| B(VisualizationActionIframe)
    B -->|Embeds iframe| C(viz Next.js App)
    C -->|postMessage: "setContentHeight"| B
    B -->|postMessage: "answer"| C
    C -->|postMessage: "callFunction"| B
    B -->|API Call: /api/w/:wId/sandbox_functions/:fnId/invoke| D[Dust Backend]
    D -->|SSE: SandboxFunctionBlockingEvent| B
    B -->|Renders| E{Auth/Approval Cards}
    E -->|User Action| D
    D -->|SSE: SandboxFunctionInvocationEvent| B
    B -->|postMessage: "answer"| C
    C -->|API Call: /api/w/:wId/files/:fileId/edit-text| D
    D -->|Updates File| F[File Storage]
    C -->|API Call: /api/w/:wId/files/:fileId?action=view| D
    D -->|Fetches File Content| F
    C -->|postMessage: "downloadFileRequest"| B
    B -->|Triggers Browser Download| G[User Browser]

    subgraph "Dust Frontend"
        B
        E
    end

    subgraph "viz Next.js App (iframe)"
        C
    end

    subgraph "Dust Backend"
        D
        F
    end
```
**Diagram: Visualization Iframe Communication Flow**
Sources: [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:1-164](), [viz/app/components/VisualizationWrapper.tsx:175-200]()

## Frame Publication Storage

Frames are stored as "publications" in Google Cloud Storage (GCS). This system ensures versioning, immutability, and efficient retrieval of Frame assets. The `publication_storage.ts` module [front/lib/api/frames/publication_storage.ts:1-80]() handles the storage and retrieval logic.

### Storage Structure

Each Frame publication is identified by a `workspaceId`, `frameId`, and `publicationId`. The files associated with a publication are stored under a specific GCS path structure:
- `w/:workspaceId/frames/:frameId/publications/:publicationId/` [front/types/api/frame_storage.ts:31-39]()
- `manifest.json`: Contains the `FrameManifest` [front/types/api/frame_manifest.ts:1-10]() which describes the Frame, its entry points, and declared functions [front/types/api/frame_storage.ts:41-48]().
- `ui/bundle.js`: The bundled JavaScript code for the Frame's UI [front/types/api/frame_storage.ts:74-80]().
- `source/`: Directory for original source files [front/types/api/frame_storage.ts:50-56]().
- `functions/:functionName/bundle.js`: Bundled code for individual Pod Functions [front/types/api/frame_storage.ts:94-101]().
- `functions/:functionName/schema.json`: JSON schema for Pod Function inputs and outputs [front/types/api/frame_storage.ts:103-110]().

The `getFramePublicationManifestPath`, `getFramePublicationSourcePath`, `getFramePublicationUiBundlePath`, `getFramePublicationFunctionBundlePath`, and `getFramePublicationFunctionSchemaPath` functions [front/types/api/frame_storage.ts:41-110]() define these paths.

### `storeFramePublication`

The `storeFramePublication` function [front/lib/api/frames/publication_storage.ts:99-114]() is responsible for uploading all Frame assets to GCS. It takes the `FileResource` representing the Frame, `functionArtifacts` (bundled code and schemas for Pod Functions), the `manifest`, `sourceFiles`, and the `uiBundleCode`.

Before storing, it performs several validations:
- Ensures the `FileResource` is a Frames v2 type and belongs to the current workspace [front/lib/api/frames/publication_storage.ts:82-97]().
- Validates that all `sourceFiles` have safe relative paths and that the UI entry point and function entry points declared in the manifest exist within the `sourceFiles` [front/lib/api/frames/publication_storage.ts:120-157]().
- Checks for duplicate source paths and function artifact names [front/lib/api/frames/publication_storage.ts:130-136]().
- Verifies that all functions declared in the manifest have corresponding artifacts [front/lib/api/frames/publication_storage.ts:159-191]().

The actual storage process uses `concurrentExecutor` [front/lib/api/frames/publication_storage.ts:16]() to upload files in parallel to GCS. The manifest is stored last, acting as a commit marker [front/lib/api/frames/publication_storage.ts:199-200]().

### `activateFramePublication` and `publishFramePublication`

The `activateFramePublication` function [front/lib/api/frames/publication_storage.ts:300-319]() updates the `FileResource` to point to a newly stored publication, making it the active version. This involves updating the `contentHash` and `publicationId` fields of the `FileResource`.

The `publishFramePublication` function [front/lib/api/frames/publication_storage.ts:321-339]() combines `storeFramePublication` and `activateFramePublication` to perform a complete publication workflow.

```mermaid
graph TD
    A[Frame Source Files] --> B{Build Process}
    B --> C[UI Bundle Code]
    B --> D[Function Artifacts (Bundles & Schemas)]
    B --> E[Frame Manifest]
    F[FileResource (Frame)] --> G(storeFramePublication)
    G -->|Validates & Uploads| H[GCS Bucket]
    H -->|Stores UI Bundle| H1[.../ui/bundle.js]
    H -->|Stores Source Files| H2[.../source/*]
    H -->|Stores Function Bundles| H3[.../functions/:fn/bundle.js]
    H -->|Stores Function Schemas| H4[.../functions/:fn/schema.json]
    H -->|Stores Manifest (Last)| H5[.../manifest.json]
    G --> I(activateFramePublication)
    I --> J[Update FileResource: contentHash, publicationId]
    J --> K[Active Frame]
```
**Diagram: Frame Publication Workflow**
Sources: [front/lib/api/frames/publication_storage.ts:99-339](), [front/types/api/frame_storage.ts:31-110]()

## Interactive Content Rendering

The `FrameRenderer` component [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:60-68]() is responsible for displaying interactive content within the Dust application. It acts as a wrapper around `VisualizationActionIframe`, providing additional UI elements and logic for managing the Frame's state and interactions.

### `FrameRenderer` Features

- **Loading and Error States**: Displays spinners during loading and error messages if the Frame fails to load [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:75-76]().
- **Full-screen Mode**: Allows users to toggle a full-screen view of the Frame [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:130-133]().
- **Code Display**: Provides a button to show the Frame's source code [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:156]().
- **Revert Functionality**: Integrates with `useVisualizationRevert` [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:150-153]() to allow reverting Frame changes.
- **File Editing**: Handles `editText` requests from the iframe, allowing direct editing of Frame source files [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:157-201]().
- **Project Integration**: Determines if the Frame is part of a "Pod" (project) and provides options to save or pin it to the project [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:88-104]().
- **Sharing**: Offers functionality to share the Frame [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:7]().

### Public Frame Rendering

For publicly shared Frames, the `PublicFrameRenderer` component [front/components/assistant/conversation/interactive_content/PublicFrameRenderer.tsx:63-72]() is used. This component wraps `VisualizationActionIframe` and provides a public-facing header (`PublicInteractiveContentHeader` [front/components/assistant/conversation/interactive_content/PublicInteractiveContentHeader.tsx:3]()) and handles email verification flows if required [front/components/pages/share/EmailVerificationFlow.tsx:3]().

The `SharedFramePage` [front/components/pages/share/SharedFramePage.tsx:18-19]() is the entry point for viewing publicly shared Frames. It fetches metadata about the shared Frame (`useShareFrameMetadata` [front/lib/swr/share.ts:1-2]()) and the Frame content itself (`usePublicFrame` [front/lib/swr/frames.ts:1-2]()). It also handles tracking views with PostHog [front/components/pages/share/SharedFramePage.tsx:53-57]() and setting appropriate SEO meta tags [front/components/pages/share/SharedFramePage.tsx:75-138]().

## `viz` Next.js Application

The `viz` application is a standalone Next.js project (`viz/`) designed to render interactive content within an iframe. It acts as the runtime environment for Frames.

### `VisualizationWrapper`

The core of the `viz` application is the `VisualizationWrapper` component [viz/app/components/VisualizationWrapper.tsx:46-47](). This component:
- **Initializes the Runtime**: Sets up the `react-runner` environment for executing user-provided React code [viz/app/components/VisualizationWrapper.tsx:104-106]().
- **Handles File Resolution**: The `resolveFileRef` function [viz/app/components/VisualizationWrapper.tsx:61-114]() recursively resolves file references (e.g., `fil_...` IDs or relative paths) within the Frame's code. It distinguishes between Frame files (compiled as React modules) and data files (wrapped as `{ default: File }`).
- **Provides APIs**: Exposes `VisualizationAPI`, `VisualizationDataAPI`, and `VisualizationUIAPI` [viz/app/components/VisualizationWrapper.tsx:16-20]() to the Frame's runtime, allowing Frames to interact with the parent Dust application (e.g., `fetchFile`, `downloadFile`, `callFunction`).
- **Pod Function Integration**: Uses `PodFunctionHooksProvider`, `usePodFunction`, and `usePodFunctionMutation` [viz/app/lib/pod-function-hooks.tsx:9-11]() to enable Frames to call Pod Functions.
- **Error Handling**: Includes an `ErrorBoundary` [viz/app/components/VisualizationWrapper.tsx:4]() to catch and display errors within the Frame.
- **Tailwind Validation**: `validateTailwindCode` [viz/app/components/VisualizationWrapper.tsx:134-168]() checks for forbidden Tailwind arbitrary values in the generated code to prevent visualization failures.
- **PDF Mode**: Includes logic for delaying readiness in PDF mode to allow animations to complete [viz/app/components/VisualizationWrapper.tsx:46-47]().

### Pod Functions Integration

Frames can interact with server-side logic through Pod Functions. This integration is crucial for persistent data storage, calling other tools, or accessing workspace secrets.

- **`pod_functions` Skill**: The `podFunctionsSkill` [front/lib/resources/skill/code_defined/global/pod_functions.ts:39-40]() defines the capabilities and instructions for using Pod Functions. It emphasizes that Pod Functions are versioned, typed TypeScript functions running on the Pod's Computer, shared across conversations in a Pod.
- **Authoring**: Pod Functions are authored as TypeScript files within an app's `functions/` folder (e.g., `pod-<podId>/MyApp/functions/list-notes.ts`) [front/lib/resources/skill/code_defined/global/pod_functions.ts:75-77](). They must export a `schema` object (with `description`, `input`, `output` Zod schemas) and default-export an object with an `async fetch(request: Request): Promise<Response>` method [front/lib/resources/skill/code_defined/global/pod_functions.ts:126-137]().
- **Calling from Frame**: Frames can call Pod Functions using the `usePodFunction` hook [viz/app/lib/pod-function-hooks.tsx:10](). This hook handles the RPC communication with the parent Dust application, which then routes the invocation to the backend.
- **User Identity Policy**: Pod Functions can specify a `userIdentity` policy (e.g., `workspace_user_required`) [front/lib/api/frames/publication_storage.ts:53]() to control who can invoke them.

```mermaid
graph TD
    A[Frame Code (in viz iframe)] -->|usePodFunction()| B(PodFunctionHooksProvider)
    B -->|RPC: "callFunction"| C(VisualizationActionIframe)
    C -->|API Call: /api/w/:wId/sandbox_functions/:fnId/invoke| D[Dust Backend]
    D --> E[Sandbox Execution Environment]
    E --> F[Pod Function Runtime]
    F -->|Accesses| G[Pod File System / Databases]
    F -->|Calls| H[Other MCP Tools]
    F -->|Returns Result| E
    E --> D
    D -->|SSE: Invocation Events| C
    C -->|RPC: "answer"| B
    B --> A

    subgraph "viz Next.js App"
        A
        B
    end

    subgraph "Dust Frontend"
        C
    end

    subgraph "Dust Backend"
        D
        E
        F
        G
        H
    end
```
**Diagram: Pod Function Invocation Flow**
Sources: [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:330-332](), [viz/app/lib/pod-function-hooks.tsx:9-11](), [front/lib/resources/skill/code_defined/global/pod_functions.ts:39-40]()

Sources:
- [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:1-164]()
- [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:118-131]()
- [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:134-164]()
- [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:330-332]()
- [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:4]()
- [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:7-9]()
- [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:1-2]()
- [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:75-85]()
- [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:30-34]()
- [front/components/assistant/conversation/actions/VisualizationActionIframe.tsx:196-206]()
- [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:60-68]()
- [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:75-76]()
- [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:130-133]()
- [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:156]()
- [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:150-153]()
- [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:157-201]()
- [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:88-104]()
- [front/components/assistant/conversation/interactive_content/FrameRenderer.tsx:7]()
- [front/components/assistant/conversation/interactive_content/PublicFrameRenderer.tsx:63-72]()
- [front/components/assistant/conversation/interactive_content/PublicInteractiveContentHeader.tsx:3]()
- [front/components/pages/share/EmailVerificationFlow.tsx:3]()
- [front/components/pages/share/SharedFramePage.tsx:18-19]()
- [front/lib/swr/share.ts:1-2]()
- [front/lib/swr/frames.ts:1-2]()
- [front/components/pages/share/SharedFramePage.tsx:53-57]()
- [front/components/pages/share/SharedFramePage.tsx:75-138]()
- [front/lib/api/frames/publication_storage.ts:1-80]()
- [front/types/api/frame_storage.ts:31-39]()
- [front/types/api/frame_manifest.ts:1-10]()
- [front/types/api/frame_storage.ts:41-48]()
- [front/types/api/frame_storage.ts:74-80]()
- [front/types/api/frame_storage.ts:94-101]()
- [front/types/api/frame_storage.ts:103-110]()
- [front/types/api/frame_storage.ts:41-110]()
- [front/lib/api/frames/publication_storage.ts:99-114]()
- [front/lib/api/frames/publication_storage.ts:82-97]()
- [front/lib/api/frames/publication_storage.ts:120-157]()
- [front/lib/api/frames/publication_storage.ts:130-136]()
- [front/lib/api/frames/publication_storage.ts:159-191]()
- [front/lib/api/frames/publication_storage.ts:16]()
- [front/lib/api/frames/publication_storage.ts:199-200]()
- [front/lib/api/frames/publication_storage.ts:300-319]()
- [front/lib/api/frames/publication_storage.ts:321-339]()
- [viz/app/components/VisualizationWrapper.tsx:46-47]()
- [viz/app/components/VisualizationWrapper.tsx:4]()
- [viz/app/components/VisualizationWrapper.tsx:61-114]()
- [viz/app/components/VisualizationWrapper.tsx:16-20]()
- [viz/app/components/VisualizationWrapper.tsx:134-168]()
- [viz/app/components/VisualizationWrapper.tsx:175-182]()
- [viz/app/components/VisualizationWrapper.tsx:187-192]()
- [viz/app/components/VisualizationWrapper.tsx:194-196]()
- [viz/app/components/VisualizationWrapper.tsx:198-200]()
- [viz/app/lib/pod-function-hooks.tsx:9-11]()
- [front/lib/resources/skill/code_defined/global/pod_functions.ts:39-40]()
- [front/lib/resources/skill/code_defined/global/pod_functions.ts:75-77]()
- [front/lib/resources/skill/code_defined/global/pod_functions.ts:126-137]()
- [viz/app/lib/pod-function-hooks.tsx:10]()
- [front/lib/api/frames/publication_storage.ts:53]()

---


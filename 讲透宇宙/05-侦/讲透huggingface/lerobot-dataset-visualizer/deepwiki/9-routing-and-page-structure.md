<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/lerobot-dataset-visualizer · page 9 Routing and Page Structure · fetched 2026-10-26 -->

# Routing and Page Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/[org]/[dataset]/[episode]/page.tsx](src/app/[org]/[dataset]/[episode]/page.tsx)
- [src/app/layout.tsx](src/app/layout.tsx)
- [src/app/page.tsx](src/app/page.tsx)

</details>



## Purpose and Scope

This document describes the Next.js App Router architecture used in the LeRobot Dataset Visualizer. It covers the route structure, dynamic parameter handling, server-side rendering patterns, and page component responsibilities. For detailed information about the data fetching that occurs on these routes, see [Core Data Pipeline](#3). For UI components rendered by these pages, see [Episode Viewer Component](#4).

---

## Route Architecture Overview

The application uses Next.js 13+ App Router with file-system based routing. All routes are defined under `src/app/`, following the App Router convention where folder names in square brackets represent dynamic segments.

```mermaid
graph TB
    subgraph "Route Structure"
        Root["/ (root)"]
        Layout["layout.tsx<br/>(Root Layout)"]
        Home["page.tsx<br/>(Home Page)"]
        Explore["/explore<br/>(Not shown in files)"]
        Dynamic["[org]/[dataset]/[episode]/<br/>page.tsx"]
    end
    
    subgraph "Dynamic Parameters"
        Dynamic --> Org["org: string<br/>(e.g., 'lerobot')"]
        Dynamic --> Dataset["dataset: string<br/>(e.g., 'aloha_static_cups_open')"]
        Dynamic --> Episode["episode: string<br/>(e.g., 'episode_0')"]
    end
    
    subgraph "Page Functions"
        Dynamic --> PageFunc["EpisodePage()<br/>async function"]
        Dynamic --> MetaFunc["generateMetadata()<br/>async function"]
    end
    
    subgraph "Data Flow"
        PageFunc --> Parse["Parse episode number<br/>from string"]
        Parse --> Fetch["getEpisodeDataSafe()"]
        Fetch --> Render["<EpisodeViewer />"]
    end
    
    Root --> Layout
    Layout --> Home
    Layout --> Explore
    Layout --> Dynamic
    
    style Dynamic fill:#f9f9f9,stroke:#333,stroke-width:2px
    style PageFunc fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [src/app/layout.tsx:1-23](), [src/app/page.tsx:1-191](), [src/app/[org]/[dataset]/[episode]/page.tsx:1-34]()

---

## Dynamic Route Pattern

The primary visualization route follows the pattern `/:org/:dataset/:episode`, implemented as a nested folder structure with bracket notation. This pattern allows users to navigate directly to any episode of any dataset from any organization on HuggingFace.

### Route Segment Structure

| Segment | Type | Example | Constraint |
|---------|------|---------|------------|
| `org` | Dynamic | `lerobot` | Organization name on HuggingFace |
| `dataset` | Dynamic | `aloha_static_cups_open` | Dataset name within organization |
| `episode` | Dynamic | `episode_0` | Episode identifier with `episode_` prefix |

The episode segment uses a specific naming convention where the route parameter is a string like `episode_0`, which is parsed to extract the numeric episode index [src/app/[org]/[dataset]/[episode]/page.tsx:26]().

```mermaid
graph LR
    URL["URL Path<br/>/lerobot/aloha_static_cups_open/episode_0"]
    
    subgraph "Next.js Routing"
        Params["params object<br/>{org, dataset, episode}"]
    end
    
    subgraph "Parameter Processing"
        OrgProp["org: 'lerobot'"]
        DatasetProp["dataset: 'aloha_static_cups_open'"]
        EpisodeString["episode: 'episode_0'"]
        
        EpisodeString --> RegexReplace["replace(/^episode_/, '')"]
        RegexReplace --> EpisodeNum["episodeNumber: 0<br/>(number type)"]
    end
    
    URL --> Params
    Params --> OrgProp
    Params --> DatasetProp
    Params --> EpisodeString
    
    subgraph "Data Fetching"
        EpisodeNum --> FetchCall["getEpisodeDataSafe(<br/>org, dataset, episodeNumber)"]
    end
```

**Sources:** [src/app/[org]/[dataset]/[episode]/page.tsx:18-27]()

---

## Server-Side Rendering Pattern

The episode page uses Next.js server components for server-side rendering and data fetching. The configuration explicitly sets `dynamic = "force-dynamic"` to prevent static generation and ensure fresh data on each request [src/app/[org]/[dataset]/[episode]/page.tsx:5]().

### Server Component Functions

```mermaid
graph TB
    subgraph "generateMetadata()"
        GMInput["params Promise"]
        GMInput --> GMAwait["await params"]
        GMAwait --> GMReturn["return {title}"]
    end
    
    subgraph "EpisodePage()"
        EPInput["params Promise"]
        EPInput --> EPAwait["await params"]
        EPAwait --> EPParse["Parse episode number"]
        EPParse --> EPFetch["getEpisodeDataSafe()"]
        EPFetch --> EPData["{data, error}"]
        EPData --> EPRender["<Suspense><EpisodeViewer /></Suspense>"]
    end
    
    subgraph "Rendering Output"
        EPRender --> Browser["Browser receives<br/>pre-rendered HTML"]
    end
    
    style GMReturn fill:#f9f9f9,stroke:#333,stroke-width:2px
    style EPData fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Key Implementation Details:**

1. **Metadata Generation** [src/app/[org]/[dataset]/[episode]/page.tsx:7-16](): Generates page title dynamically based on route parameters. Used by Next.js for HTML `<title>` tag and OpenGraph metadata.

2. **Data Fetching** [src/app/[org]/[dataset]/[episode]/page.tsx:27](): Calls `getEpisodeDataSafe()` on the server before rendering. This returns both successful data and error states for graceful error handling.

3. **Suspense Boundary** [src/app/[org]/[dataset]/[episode]/page.tsx:29-31](): Wraps `EpisodeViewer` in React Suspense with `fallback={null}` to handle streaming server rendering.

**Sources:** [src/app/[org]/[dataset]/[episode]/page.tsx:1-34]()

---

## Home Page and Routing Logic

The home page (`src/app/page.tsx`) serves multiple purposes: displaying a landing interface, handling redirects based on environment variables, and processing URL parameters for HuggingFace Spaces integration.

### Client-Side Routing Patterns

The home page uses client-side routing with several redirect mechanisms:

```mermaid
graph TB
    Load["Home Page Loads"]
    
    Load --> EnvCheck{"process.env.REPO_ID<br/>defined?"}
    EnvCheck -->|Yes| EnvRedirect["Redirect to<br/>/{REPO_ID}/episode_{N}"]
    
    EnvCheck -->|No| PathCheck{"searchParams.get('path')<br/>exists?"}
    PathCheck -->|Yes| PathRedirect["router.push(path)"]
    
    PathCheck -->|No| LegacyCheck{"searchParams.get('dataset')<br/>exists?"}
    LegacyCheck -->|Yes| LegacyRedirect["Build URL from<br/>dataset & episode params"]
    
    LegacyCheck -->|No| ShowUI["Show Landing UI"]
    
    subgraph "Landing UI Components"
        ShowUI --> Input["Text Input<br/>for dataset ID"]
        ShowUI --> Examples["Example Dataset<br/>Buttons"]
        ShowUI --> ExploreLink["Explore Page Link"]
        ShowUI --> YTBg["YouTube Background<br/>Video"]
    end
    
    Input --> ManualNav["router.push(value)"]
    Examples --> ManualNav
    ExploreLink --> ManualNav
```

**Sources:** [src/app/page.tsx:15-54](), [src/app/page.tsx:102-189]()

### Environment Variable Configuration

| Variable | Purpose | Example | Usage |
|----------|---------|---------|-------|
| `REPO_ID` | Dataset identifier for single-dataset mode | `lerobot/aloha_static_cups_open` | Redirects home to specific dataset [src/app/page.tsx:22-29]() |
| `EPISODES` | Space-separated episode list | `0 1 2 3` | Determines first episode to display [src/app/page.tsx:23-26]() |

When `REPO_ID` is set, the application operates in single-dataset mode, automatically redirecting users to the first episode of the configured dataset.

### URL Parameter Handling

The home page supports multiple URL parameter formats for integration with HuggingFace Spaces:

```mermaid
graph LR
    subgraph "URL Parameter Formats"
        Format1["?path=/org/dataset/episode_0"]
        Format2["?dataset=org/dataset&episode=0"]
        Format3["?dataset=org/dataset"]
    end
    
    subgraph "Processing"
        Format1 --> Direct["Direct push:<br/>router.push(path)"]
        Format2 --> Build1["Build:<br/>/{dataset}/episode_{episode}"]
        Format3 --> Build2["Build:<br/>/{dataset}"]
    end
    
    subgraph "Time Parameter"
        TimeParam["?t=123"]
        TimeParam --> Append["Append to redirect URL"]
    end
    
    Direct --> Navigate["Navigation occurs"]
    Build1 --> Navigate
    Build2 --> Navigate
```

**Sources:** [src/app/page.tsx:32-53]()

### YouTube Background Video

The home page includes a YouTube video background player for visual appeal:

1. **API Loading** [src/app/page.tsx:58-64](): Dynamically loads YouTube IFrame API script
2. **Player Initialization** [src/app/page.tsx:66-93](): Creates player with autoplay, mute, and loop settings
3. **Loop Management** [src/app/page.tsx:85-90](): Implements manual loop by seeking to start when video reaches 60 seconds
4. **Cleanup** [src/app/page.tsx:95-99](): Destroys player on component unmount

**Sources:** [src/app/page.tsx:56-100]()

---

## Root Layout Configuration

The root layout provides global configuration for all pages:

```mermaid
graph TB
    subgraph "Root Layout (layout.tsx)"
        HTML["<html lang='en'>"]
        Meta["Metadata:<br/>title & description"]
        Body["<body> with Inter font"]
        Children["Page content (children)"]
    end
    
    HTML --> Body
    Body --> Children
    
    subgraph "Applied to All Routes"
        Children --> Home["/ (Home)"]
        Children --> Episode["/:org/:dataset/:episode"]
        Children --> Explore["/explore"]
    end
```

**Configuration Details:**

- **Font**: Inter font family from Google Fonts [src/app/layout.tsx:5]()
- **Default Metadata**: Application title and description [src/app/layout.tsx:7-10]()
- **Global Styles**: Imports `globals.css` for Tailwind CSS [src/app/layout.tsx:3]()

The layout is minimal, allowing individual pages to control their own structure. The episode page can override the default title through its `generateMetadata` function.

**Sources:** [src/app/layout.tsx:1-23]()

---

## Navigation Flow Summary

```mermaid
graph TB
    Browser["User Browser"]
    
    Browser --> Entry{"Entry Point"}
    
    Entry -->|Direct URL| Episode["/:org/:dataset/:episode"]
    Entry -->|Root path| Home["/"]
    Entry -->|Explore| Explore["/explore"]
    
    Home --> EnvMode{"REPO_ID set?"}
    EnvMode -->|Yes| AutoRedirect["Auto-redirect to<br/>configured dataset"]
    EnvMode -->|No| UserInput["User input or<br/>example selection"]
    
    UserInput --> Episode
    AutoRedirect --> Episode
    
    subgraph "Episode Page Server Actions"
        Episode --> ServerFetch["Server: getEpisodeDataSafe()"]
        ServerFetch --> SSR["Server: Render with data"]
        SSR --> Hydrate["Browser: Hydrate client components"]
    end
    
    Hydrate --> Interactive["Interactive EpisodeViewer"]
    
    Interactive --> NavAction{"User Navigation"}
    NavAction --> PrevNext["Prev/Next episode<br/>(URL change)"]
    NavAction --> NewDataset["Enter new dataset<br/>(Return to home)"]
    
    PrevNext --> Episode
    NewDataset --> Home
```

**Sources:** [src/app/page.tsx:1-191](), [src/app/[org]/[dataset]/[episode]/page.tsx:1-34]()

---

## Key Routing Patterns

### 1. Server Component Data Fetching

The episode page demonstrates the Next.js 13+ pattern of fetching data directly in server components:

```typescript
// Pattern: await async function in component
const { data, error } = await getEpisodeDataSafe(org, dataset, episodeNumber);
```

This eliminates the need for `getServerSideProps` and allows data fetching to be collocated with the component [src/app/[org]/[dataset]/[episode]/page.tsx:27]().

### 2. Promise-based Parameters

Next.js 15+ returns route parameters as Promises, requiring async/await:

```typescript
// Pattern: await params before use
const { org, dataset, episode } = await params;
```

Both `generateMetadata` and `EpisodePage` follow this pattern [src/app/[org]/[dataset]/[episode]/page.tsx:12](), [src/app/[org]/[dataset]/[episode]/page.tsx:24]().

### 3. Suspense Boundaries

Server components use Suspense to handle streaming rendering:

```typescript
<Suspense fallback={null}>
  <EpisodeViewer data={data} error={error} />
</Suspense>
```

The `fallback={null}` provides a clean loading experience while server-rendering completes [src/app/[org]/[dataset]/[episode]/page.tsx:29-31]().

### 4. Client-Side Navigation

The home page uses `useRouter` for programmatic navigation and `useSearchParams` for reading URL parameters [src/app/page.tsx:4-5](), [src/app/page.tsx:16-17](). This enables smooth client-side transitions without full page reloads.

**Sources:** [src/app/[org]/[dataset]/[episode]/page.tsx:1-34](), [src/app/page.tsx:1-191]()

---


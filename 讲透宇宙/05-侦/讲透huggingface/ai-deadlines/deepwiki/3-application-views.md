<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/ai-deadlines · page 3 Application Views · fetched 2026-10-26 -->

# Application Views

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/App.tsx](src/App.tsx)
- [src/pages/Calendar.tsx](src/pages/Calendar.tsx)
- [src/pages/Index.tsx](src/pages/Index.tsx)

</details>



This document provides a detailed explanation of the primary application views in the AI Deadlines system. It covers the structure, functionality, and implementation of the main pages that users interact with. For information about the underlying conference data model that powers these views, see [Conference Data System](#2).

## View Structure Overview

The AI Deadlines application provides two primary views for accessing conference information:

1. **Conference Listing View** - The main page that displays conferences as filterable cards
2. **Calendar View** - An alternative view showing conferences in a calendar format

These views represent different ways of interacting with the same underlying conference data.

```mermaid
graph TD
    subgraph "Core Data"
        confData["conferences.yml"]
    end

    subgraph "Main Views"
        indexPage["Index Page"]
        calendarPage["Calendar Page"]
    end

    subgraph "Routing"
        router["React Router"]
    end

    confData --> indexPage
    confData --> calendarPage
    router --> indexPage
    router --> calendarPage
```

Sources: [src/App.tsx:17-23](), [src/pages/Index.tsx:2-4](), [src/pages/Calendar.tsx:2-3]()

## Application Routing

The application uses React Router to manage navigation between the different views. The main routes are defined in the App component:

```mermaid
flowchart LR
    subgraph "App.tsx"
        router["BrowserRouter"]
        routes["Routes"]
    end

    subgraph "Route Paths"
        home["/"]
        cal["/calendar"]
        notFound["*"]
    end

    subgraph "View Components"
        index["Index Component"]
        calendar["Calendar Component"]
        notFoundPage["NotFound Component"]
    end

    router --> routes
    routes --> home
    routes --> cal
    routes --> notFound
    home --> index
    cal --> calendar
    notFound --> notFoundPage
```

Sources: [src/App.tsx:12-28]()

## Conference Listing View

The Conference Listing View is the main entry point to the application. It presents conferences as a grid of cards with comprehensive filtering capabilities.

### Structure and Components

```mermaid
flowchart TD
    subgraph "Index Page"
        header["Header Component"]
        filters["Filter Controls"]
        grid["Conference Grid"]
    end

    subgraph "Filter Controls"
        tagButtons["Category Buttons"]
        pastToggle["Past Conferences Toggle"]
        countryFilter["Country Filter Popover"]
    end

    subgraph "Conference Grid"
        card1["Conference Card"]
        card2["Conference Card"]
        cardN["..."]
    end

    header --> filters
    filters --> tagButtons
    filters --> pastToggle
    filters --> countryFilter
    grid --> card1
    grid --> card2
    grid --> cardN
```

Sources: [src/pages/Index.tsx:140-284]()

### Key Features

1. **Category Filtering**: Users can filter conferences by selecting one or more category tags
2. **Country Filtering**: A popover control allows filtering by conference location
3. **Past Conference Toggle**: Option to show or hide conferences with past deadlines
4. **Search Functionality**: Header component provides search across conference titles and names
5. **URL Parameter Support**: Selected filters are reflected in URL parameters for bookmarking and sharing

### Implementation Details

The `Index` component manages several pieces of state:
- `selectedTags`: Set of category identifiers that are currently selected
- `selectedCountries`: Set of country names that are currently selected
- `searchQuery`: Current search text from the header
- `showPastConferences`: Boolean toggle for showing past events

The component applies these filters to the conference data and produces a filtered list for display:

```mermaid
flowchart TD
    confData["conferences.yml"] --> filters["Filter Functions"]
    filters --> filtered["Filtered Conferences"]
    filtered --> sort["Sort by Deadline"]
    sort --> display["Display as Cards"]

    subgraph "Filter Criteria"
        tags["Selected Tags"]
        countries["Selected Countries"]
        search["Search Query"]
        past["Show Past Toggle"]
    end

    tags --> filters
    countries --> filters
    search --> filters
    past --> filters
```

Sources: [src/pages/Index.tsx:40-83](), [src/pages/Index.tsx:85-117]()

## Calendar View

The Calendar View provides a time-based visualization of conferences, showing both submission deadlines and conference dates in a calendar format.

### Structure and Components

```mermaid
flowchart TD
    subgraph "Calendar Page"
        calHeader["Header Component"]
        viewToggle["View Toggle\n(Month/Year)"]
        legend["Category Legend"]
        calComp["Calendar Component"]
        eventDialog["Event Dialog"]
    end

    subgraph "Calendar Features"
        monthView["Month View"]
        yearView["Year View"]
        dayContent["Day Cell Content"]
        dayEvents["Day Events"]
    end

    calHeader --> viewToggle
    viewToggle --> monthView
    viewToggle --> yearView
    legend --> calComp
    calComp --> dayContent
    dayContent --> dayEvents
    dayEvents --> eventDialog
```

Sources: [src/pages/Calendar.tsx:70-752]()

### Key Features

1. **Dual View Modes**: Toggle between month view and year view
2. **Category Filtering**: Select which conference categories to display
3. **Deadline Highlighting**: Shows submission deadlines with distinct styling
4. **Conference Duration**: Visualizes conference durations across calendar days
5. **Detailed Event Dialog**: Click on a day to view detailed information about events
6. **Search Functionality**: Header component provides search across all conferences

### Implementation Details

The Calendar component maintains several key state variables:
- `selectedDate`: Currently selected date in the calendar
- `isYearView`: Boolean toggle between year and month views
- `currentMonth`/`currentYear`: Current display period
- `selectedCategories`: Set of categories to display
- `showDeadlines`: Boolean to toggle deadline display

The component processes conference data to extract deadline and event dates for display in the calendar:

```mermaid
flowchart TD
    confData["conferences.yml"] --> parse["Parse ISO Dates"]
    parse --> filter["Filter by Category"]
    filter --> separate["Separate Deadlines\nand Conferences"]
    separate --> render["Render in Calendar"]
    
    subgraph "Calendar Processing"
        getDayEvents["getDayEvents Function"]
        getEvents["getEvents Function"]
        renderDayContent["renderDayContent Function"]
    end
    
    getDayEvents --> render
    getEvents --> render
    renderDayContent --> render
```

Sources: [src/pages/Calendar.tsx:116-154](), [src/pages/Calendar.tsx:156-197](), [src/pages/Calendar.tsx:263-313]()

## View Interaction Patterns

The two main views share common interaction patterns and components:

```mermaid
sequenceDiagram
    participant User
    participant Header
    participant IndexView
    participant CalendarView
    participant ConferenceData
    
    User->>Header: Perform search
    Header->>IndexView: Update searchQuery
    Header->>CalendarView: Update searchQuery
    
    IndexView->>ConferenceData: Filter by query
    CalendarView->>ConferenceData: Filter by query
    
    User->>IndexView: Select category tag
    IndexView->>ConferenceData: Filter by tag
    
    User->>CalendarView: Select category
    CalendarView->>ConferenceData: Filter by category
    
    User->>Header: Navigate between views
```

Sources: [src/pages/Index.tsx:142-145](), [src/pages/Calendar.tsx:578]()

## Shared Components

Both main views leverage several shared components:

1. **Header Component**: Provides navigation and search functionality
2. **Dialog Components**: Display detailed information about conferences
3. **UI Components**: Tooltips, popovers, buttons, and other UI elements

```mermaid
graph TD
    subgraph "Shared Components"
        header["Header\n(Navigation & Search)"]
        dialog["Dialog Components\n(Conference Details)"]
        ui["UI Components\n(Buttons, Tooltips, etc.)"]
    end
    
    subgraph "Views"
        index["Index View"]
        calendar["Calendar View"]
    end
    
    header --> index
    header --> calendar
    dialog --> index
    dialog --> calendar
    ui --> index
    ui --> calendar
```

Sources: [src/pages/Index.tsx:142](), [src/pages/Calendar.tsx:578](), [src/pages/Calendar.tsx:706-749]()

## Data Flow in Views

Both views follow a similar data flow pattern where conference data is filtered and transformed for display:

```mermaid
flowchart LR
    confYml["conferences.yml"] --> dataLoad["Load Data"]
    dataLoad --> filter["Apply Filters"]
    filter --> transform["Transform for Display"]
    transform --> render["Render UI Components"]
    
    subgraph "User Interactions"
        search["Search Input"]
        catSelect["Category Selection"]
        countrySelect["Country Selection"]
        dateSelect["Date Selection"]
    end
    
    search --> filter
    catSelect --> filter
    countrySelect --> filter
    dateSelect --> filter
```

Sources: [src/pages/Index.tsx:40-83](), [src/pages/Calendar.tsx:116-197]()

## Summary

The application views provide two complementary ways to interact with conference data:

1. **Conference Listing View** offers a list-based approach with powerful filtering options, ideal for quickly finding specific conferences.

2. **Calendar View** provides a temporal visualization, making it easier to understand submission deadlines and conference dates in relation to each other.

Both views access the same underlying conference data but present it in different ways to support different user tasks and preferences.

---


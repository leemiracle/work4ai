<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/jev-ultrafast · extra page DOM Snapshot Reader (snapshot.js) · fetched 2026-10-30 -->

# DOM Snapshot Reader (snapshot.js)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jev_ultrafast/browser.py](jev_ultrafast/browser.py)
- [jev_ultrafast/snapshot.js](jev_ultrafast/snapshot.js)

</details>



The DOM Snapshot Reader (`snapshot.js`) is responsible for atomically reading the Document Object Model, detecting visible HTML and ARIA controls, assigning stable code-owned identities via a JavaScript `WeakMap` cache, and exposing freshness guards used by the browser harness [jev_ultrafast/browser.py:12-14](). It executes directly inside the target browser session via `Runtime.evaluate` to inspect state without multi-process overhead [jev_ultrafast/browser.py:1-1]().

---

## 1. Cache Initialization & Code-Owned Identity

When `snapshot.js` executes, it checks for or initializes a global state cache on the window object: `window.__jevFast`. This cache contains a `WeakMap` for element-to-ID mappings (`cache.ids`), a `Map` for ID-to-element lookups (`cache.nodes`), and an integer counter (`cache.next`) [jev_ultrafast/snapshot.js:1-8](). 

The `identity(e)` helper function checks if an element already exists in `cache.ids`. If not, it assigns the next sequential integer, registers it in `cache.nodes`, and returns the integer ID [jev_ultrafast/snapshot.js:4-7](). Pruned or detached nodes are automatically cleaned up from `cache.nodes` during this initialization pass [jev_ultrafast/snapshot.js:8-8]().

```mermaid
graph TD
  sub5[""DOM Element (e)""] --> identity[""identity(e)""]
  identity --> check[""cache.ids.has(e)?""]
  check -- "No" --> assign[""cache.ids.set(e, cache.next++)""]
  assign --> store[""cache.nodes.set(id, e)""]
  check -- "Yes" --> get[""cache.ids.get(e)""]
  store --> returnId[""Return Integer ID""]
  get --> returnId
```
*Figure 1: Code Entity Identity Mapping Flow via `identity()` and `window.__jevFast`.*

Sources: `jev_ultrafast/snapshot.js:1-8`

---

## 2. Visibility, Accessibility Names, and Role Resolution

To ensure only interactive controls are exposed to the model, `snapshot.js` defines several filtering and semantic inspection helpers:

- **Safety and Visibility**: `safe(e)` rejects password, file, and hidden input types [jev_ultrafast/snapshot.js:9-9](). `visible(e)` ensures elements are not within `[aria-hidden="true"]` or `[inert]` containers and pass `checkVisibility({checkOpacity: true, checkVisibilityCSS: true})` [jev_ultrafast/snapshot.js:10-11]().
- **Accessible Name Computation**: `name(e)` recursively resolves accessible names via `aria-labelledby`, `aria-label`, associated `<label>` elements, button values, `alt` text, text child nodes, `title`, and `placeholder` attributes [jev_ultrafast/snapshot.js:12-23]().
- **ARIA and Tag Role Mapping**: `role(e)` normalizes explicit `role` attributes and implicit HTML tags (`<button>`, `<a>`, `<select>`, `<textarea>`, `<input>`) into a standardized set of actionable UI roles (`button`, `link`, `checkbox`, `radio`, `switch`, `tab`, `menuitem`, `option`, `combobox`, `textbox`, `searchbox`, `spinbutton`) [jev_ultrafast/snapshot.js:24-43]().

```mermaid
graph TD
  Query[""document.querySelectorAll(selector)""] --> Filter[""safe(e) && visible(e)""]
  Filter --> GetRole[""role(e)""]
  GetRole --> ValidRole{{"Valid Role Found?"}}
  ValidRole -- "Yes" --> GetName[""name(e)""]
  GetName --> BuildBase[""Build Base Action Object""]
  ValidRole -- "No" --> Skip[""Skip Element""]
```
*Figure 2: Element Evaluation and Role Resolution Pipeline in `snapshot.js`.*

Sources: `jev_ultrafast/snapshot.js:9-43`

---

## 3. Action Space Extraction & Bounding Box Filtering

`snapshot.js` queries all interactive selectors (`a[href], button, input, textarea, select, summary, [contenteditable="true"],` and explicit ARIA roles) [jev_ultrafast/snapshot.js:26-27](). For each matching element:

1. It validates visibility, bounding client rectangles (`getBoundingClientRect`), and ensures coordinates fall within the viewport bounds (`innerWidth`, `innerHeight`) [jev_ultrafast/snapshot.js:56-59]().
2. It assigns an action kind based on element properties: `select` for `<select>` option iteration, `fill` for editable text controls, or `click` for buttons, links, and checkboxes [jev_ultrafast/snapshot.js:68-80]().
3. It appends contextual actions like "Open [Label]" for editables or `scroll_down`, `scroll_up`, and `wait` sentinel actions [jev_ultrafast/snapshot.js:79-79](), [jev_ultrafast/snapshot.js:101-104](). Actions are capped at 250 items to fit model context limits [jev_ultrafast/snapshot.js:99-100]().

Sources: `jev_ultrafast/snapshot.js:56-106`

---

## 4. Freshness Guards and Page Keys

To prevent executing stale decisions against mutated DOM states, `snapshot.js` exposes two verification structures:

- **`cache.pageKey()`**: Captures global document metrics including `performance.timeOrigin`, `location.href`, scroll offsets, window dimensions, and an array of all form input values and states (`value`, `checked`, `selectedIndex`, `disabled`, `readOnly`) [jev_ultrafast/snapshot.js:44-46]().
- **`cache.guard(e)`**: Generates a tuple representing the local state of a specific node `e`, including its ID, role, name, value, checked state, index, read-only status, disabled state, ARIA attributes (`aria-disabled`, `aria-expanded`, `aria-checked`, `aria-selected`, `href`), and a slice of its scoping container's `innerText` [jev_ultrafast/snapshot.js:47-54]().

The Python `Browser` class invokes `fresh(page, action)` to compare these guards against current DOM conditions before executing any `click` or `select` action [jev_ultrafast/browser.py:88-99]().

Sources: `jev_ultrafast/snapshot.js:44-54`, `jev_ultrafast/browser.py:88-99`

---


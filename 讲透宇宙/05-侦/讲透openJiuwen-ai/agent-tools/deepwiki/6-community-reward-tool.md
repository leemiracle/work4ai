<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/agent-tools · page 6 Community Reward Tool · fetched 2026-11-02 -->

# Community Reward Tool

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [reward_tool/index.html](reward_tool/index.html)
- [reward_tool/run-tests.js](reward_tool/run-tests.js)
- [reward_tool/test-runner.bat](reward_tool/test-runner.bat)
- [reward_tool/test.html](reward_tool/test.html)

</details>



The **Community Reward Tool** (`reward_tool/`) is a standalone, browser-based lucky draw application designed for openJiuwen community events and university outreach programs (`[reward_tool/index.html:1-6]()`). It includes a rich, animated UI for managing participant pools, multi-tier prizes, color-coded groupings, and an automated headless testing pipeline using Node.js (`[reward_tool/run-tests.js:1-5]()`).

---

## 1. Browser Application Architecture (`index.html`)

The core application resides in `reward_tool/index.html` [reward_tool/index.html:1-10](). It relies on client-side vanilla JavaScript and CSS animations, utilizing `html2canvas` [reward_tool/index.html:7-7]() for exporting lucky draw results as snapshot images. 

Key functional blocks within the browser UI include:
- **Configuration Section**: Activity naming, minimum/maximum number ranges, and excluded number parsing (`[reward_tool/index.html:77-82]()`).
- **Prize & Color Management**: Dynamic addition and removal of prize tiers (`addPrize`, `removePrize`) and color-coded group ranges (`addColor`, `removeColor`) (`[reward_tool/run-tests.js:17-32]()`).
- **Drawing Loop & Progress Control**: Controls for drawing numbers (`startDraw`, `startDrawWithProgressControl`) with abort support (`resetAllWithAbort`) (`[reward_tool/run-tests.js:26-30]()`).
- **Result Snapshot & Sorting**: Winner rendering (`renderWinnerList`), color-based sorting (`sortWinnersByColor`), and canvas snapshot capture (`captureSnapshot`) (`[reward_tool/run-tests.js:20-25]()`).

```mermaid
graph TD
    UI[""Browser UI index.html""] --> Config[""Config Section minNumber/maxNumber""]
    UI --> Prize[""Prize Manager addPrize/removePrize""]
    UI --> Draw[""Draw Engine startDraw""]
    Draw --> Stats[""Statistics updateStats""]
    Draw --> Render[""Winner Renderer renderWinnerList""]
    Render --> Export[""Snapshot Exporter captureSnapshot""]

    sub: "Code Entity Space"
    Config -.->|parsed by| Parse[""parseExcludeNumbers""]
    Draw -.->|tracked by| Cov[""coverage.functions""]
    Render -.->|ordered by| Sort[""sortWinnersByColor""]
```
*Sources: `[reward_tool/index.html:1-233]()`, `[reward_tool/run-tests.js:16-34]()`*

---

## 2. Custom Test Framework & Headless Runner (`run-tests.js` & `test.html`)

To ensure reliability across community events, the reward tool features a comprehensive unit testing suite (`[reward_tool/test.html:1-10]()`) coupled with a custom Node.js headless test runner (`[reward_tool/run-tests.js:1-10]()`). 

### Test Framework Implementation
The test harness is implemented via the `TestFramework` class (`[reward_tool/run-tests.js:37-100]()`), which exposes assertion helpers and test registration methods:
- `test(suite, name, description, fn)`: Registers individual test cases.
- `assertEqual(actual, expected, msg)`: Verifies strict equality.
- `assertTrue(condition, msg)` / `assertFalse(condition, msg)`: Validates boolean expectations.
- `markCalled(funcName)`: Tracks function execution against the defined coverage list (`[reward_tool/run-tests.js:16-34]()`).

### Mock DOM Environment
Because the application is built for browsers, `run-tests.js` constructs a complete virtual DOM mock via `createMockDOM()` (`[reward_tool/run-tests.js:104-212]()`). This mock simulates input fields (`activityName`, `minNumber`, `maxNumber`), result containers, and DOM query methods (`getElementById`, `querySelector`, `createElement`) so that browser-targeted scripts can execute headlessly in Node.js.

```mermaid
graph TD
    Runner[""Node Runner run-tests.js""] --> Mock[""Virtual DOM createMockDOM""]
    Runner --> Framework[""TestFramework Class""]
    Framework --> Assert[""Assertions: assertEqual/assertTrue""]
    Framework --> Coverage[""Function Coverage Tracker coverage.functions""]
    Mock --> Elements[""Mock Elements: activityName/minNumber/maxNumber""]
    Framework --> TestCases[""Registered Test Suites""]

    sub: "Code Entity Space"
    Framework -.->|executes| Run[""runAll""]
    Mock -.->|supplies| DOM[""getElementById/querySelector""]
    Coverage -.->|records| Track[""markCalled""]
```
*Sources: `[reward_tool/run-tests.js:36-212]()`, `[reward_tool/test.html:1-10]()`*

---

## 3. Headless Execution & Automation (`test-runner.bat`)

For local development and continuous integration checks on Windows environments, a batch script wraps the Node.js runner (`[reward_tool/test-runner.bat:1-3]()`). 

Execution flow:
1. User or CI triggers `test-runner.bat`.
2. The batch script invokes Node.js on `run-tests.js` (`[reward_tool/test-runner.bat:2-2]`).
3. `run-tests.js` initializes the mock DOM, loads test suites, executes assertions, tracks function coverage across core routines (e.g., `addPrize`, `startDraw`, `parseExcludeNumbers`), and outputs pass/fail metrics to the console.

```mermaid
graph LR
    Bat[""test-runner.bat""] -->|calls| Node[""Node.js Runtime""]
    Node --> Script[""run-tests.js""]
    Script --> Init[""createMockDOM()""]
    Script --> Exec[""TestFramework.runAll()""]
    Exec --> Report[""Console Results & Coverage Report""]
```
*Sources: `[reward_tool/test-runner.bat:1-4]`, `[reward_tool/run-tests.js:68-98]()`*

---


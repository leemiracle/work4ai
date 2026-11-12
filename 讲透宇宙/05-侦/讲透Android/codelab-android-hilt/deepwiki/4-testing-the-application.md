<!-- source: DeepWiki mcp.deepwiki.com · repo android/codelab-android-hilt · page 4 Testing the Application · fetched 2026-10-23 -->

# Testing the Application

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/build.gradle](app/build.gradle)
- [app/src/androidTest/java/com/example/android/hilt/AppTest.kt](app/src/androidTest/java/com/example/android/hilt/AppTest.kt)

</details>



## Purpose and Scope

This document details the testing approach for the Android Hilt Codelab application. It focuses on instrumentation tests using Hilt for dependency injection, explaining how tests are structured, configured, and executed. This page covers testing configuration, test implementation patterns, and how Hilt facilitates testing through dependency injection.

For information about the application architecture and components being tested, see [Application Architecture](#3).

## Testing Configuration

The application uses standard Android testing libraries configured in the build.gradle file. The test instrumentation runner is set to the default `AndroidJUnitRunner`.

```mermaid
graph TD
    subgraph "Test Configuration"
        A["app/build.gradle"] --> B["testInstrumentationRunner: 
        AndroidJUnitRunner"]
        A --> C["Testing Dependencies"]
        C --> D["JUnit"]
        C --> E["AndroidX Test"]
        C --> F["Espresso"]
    end
```

Sources: [app/build.gradle:36-36](), [app/build.gradle:62-67]()

### Test Dependencies

The application uses the following testing dependencies:

| Dependency | Purpose |
|------------|---------|
| JUnit | Core testing framework |
| AndroidX Test Core-KTX | Android-specific testing utilities |
| AndroidX Test JUnit Extensions | JUnit extensions for Android testing |
| AndroidX Test Rules | Test rules for instrumentation tests |
| Espresso | UI testing framework |

Sources: [app/build.gradle:62-67]()

## Test Implementation

### Current Testing Approach

The application includes an instrumentation test that validates the basic user flow through the application. This test currently uses the ServiceLocator pattern for managing dependencies during testing.

```mermaid
flowchart TD
    subgraph "Test Execution Flow"
        A["AppTest"] --> B["Launch MainActivity"]
        B --> C["Verify Buttons Fragment displayed"]
        C --> D["Click Button 1"]
        D --> E["Navigate to Logs screen"]
        E --> F["Verify log entry displayed"]
    end

    subgraph "Dependency Management"
        G["ServiceLocator"] --> H["loggerLocalDataSource"]
        H --> I["removeLogs()"]
    end

    A --> G
```

Sources: [app/src/androidTest/java/com/example/android/hilt/AppTest.kt:34-60]()

### Key Test Components

The main test class `AppTest` includes:

1. **Test Setup/Teardown**: 
   - Teardown method that cleans up logs after each test using ServiceLocator
   - This ensures test isolation by preventing data from one test affecting others

2. **Happy Path Test**:
   - Launches the main activity
   - Performs UI interactions using Espresso
   - Verifies expected UI states using view matchers

Sources: [app/src/androidTest/java/com/example/android/hilt/AppTest.kt:37-59]()

## Transitioning to Hilt for Testing

While the current test uses the ServiceLocator pattern, the application is designed to use Hilt for dependency injection. Here's how testing can be transitioned to use Hilt:

```mermaid
flowchart TD
    subgraph "Before: ServiceLocator in Testing"
        A1["AppTest"] --> A2["ServiceLocator instance"]
        A2 --> A3["loggerLocalDataSource.removeLogs()"]
    end

    subgraph "After: Hilt in Testing"
        B1["@HiltAndroidTest\nAppTest"] --> B2["HiltTestApplication"]
        B2 --> B3["@Inject\nloggerLocalDataSource"]
        B1 --> B4["@UninstallModules"]
        B4 --> B5["Custom Test Modules"]
    end
```

### Implementing Hilt in Tests

To transition tests to use Hilt for dependency injection, the following changes would be needed:

1. **Test Annotations**:
   - Add `@HiltAndroidTest` annotation to test classes
   - Use `@UninstallModules` to replace production modules with test modules when needed

2. **Custom Test Rule**:
   - Use `HiltAndroidRule` to manage the Hilt component's lifecycle in tests

3. **Test Modules**:
   - Create test-specific modules that provide test doubles (mocks, fakes, etc.)

4. **Test Application**:
   - Use `HiltTestApplication` as the application class for tests

### Test Doubles with Hilt

```mermaid
graph TD
    subgraph "Hilt Test Architecture"
        A["@HiltAndroidTest\nAppTest"] --> B["HiltAndroidRule"]
        A --> C["Test Modules"]
        C --> D["FakeLoggerLocalDataSource"]
        C --> E["TestNavigator"]
        C --> F["TestDatabase"]
        A --> G["@Inject\nTest Dependencies"]
    end
```

## Espresso UI Testing Integration

The application uses Espresso for UI testing, which integrates well with Hilt for dependency injection in tests.

```mermaid
sequenceDiagram
    participant Test as "AppTest"
    participant Activity as "MainActivity"
    participant Button as "Button Fragment"
    participant Logs as "Logs Fragment"
    participant DataSource as "LoggerLocalDataSource"
    
    Test->>Activity: launch()
    Test->>Button: verify displayed
    Test->>Button: click "Button 1"
    Button->>DataSource: addLog()
    Test->>Button: click "All Logs"
    Button->>Logs: navigate
    Test->>Logs: verify log entry
    Test->>DataSource: removeLogs()
```

Sources: [app/src/androidTest/java/com/example/android/hilt/AppTest.kt:43-59]()

## Best Practices for Testing with Hilt

1. **Separate Test Modules**: Create dedicated modules for testing to provide test doubles.

2. **Targeted Module Replacement**: Use `@UninstallModules` to replace only the necessary modules, keeping the rest of the dependency graph intact.

3. **Consistent Teardown**: Ensure proper cleanup after tests using `@After` methods to maintain test isolation.

4. **Test Hierarchies**: Structure tests to match the application's component hierarchy (Application, Activity, Fragment).

5. **Custom Test Application**: When needed, create a custom test application class to control application-level dependencies.

Sources: [app/src/androidTest/java/com/example/android/hilt/AppTest.kt:37-40]()

## Test Execution

The application's tests can be executed through:

1. Android Studio's test runner
2. Gradle command line: `./gradlew connectedAndroidTest`
3. Continuous integration systems

Test results provide information about test success/failure and execution time, helping identify issues in the application's functionality.

---


# Rules for SwiftUI Testing

Actionable directives for authoring and debugging tests in Swift.

## 1. Swift Testing Rules (`test-`)

### `test-struct-suites`
- **Context:** Test organization.
- **Rule:** Define test suites as `struct`. Tests run in parallel with no shared state by default. Use `init()` for setup. Switch to `final class` only when you truly need reference semantics or `deinit` cleanup.
- **Avoid:** Using `class` by default. `setUp`/`tearDown` habits copied into Swift Testing suites.

### `test-expect-vs-require`
- **Context:** Assertions.
- **Rule:** Use `#expect` for independent non-critical checks. Use `try #require(x)` for unwrapping optionals or preconditions where failure must stop the test.
- **Avoid:** Using `#expect` to unwrap an optional (nil causes a crash, not a test failure).

### `test-parameterized`
- **Context:** Repeated logic.
- **Rule:** Use `@Test(arguments: [...])` to run a test with multiple inputs. Each argument combination becomes an independent, parallel test case.
- **Avoid:** Multiple separate `@Test` functions for the same logic with different data.

### `test-async-confirmation`
- **Context:** Async event verification.
- **Rule:** Use `confirmation(expectedCount:)` to verify that an async event or callback occurs a specific number of times.
- **Avoid:** `Thread.sleep`, `Task.sleep`, or `XCTestExpectation` in Swift Testing suites.

### `test-known-issue`
- **Context:** Expected failures.
- **Rule:** Use `withKnownIssue("reason — see #issue-number") { }` to mark tracked expected failures. Include the tracking ticket reference.
- **Avoid:** Leaving unexplained test failures or commenting out failing tests.

### `test-no-sleep`
- **Context:** Async synchronization.
- **Rule:** Never use `Thread.sleep` or `Task.sleep` to wait for async operations. Use `confirmation` or proper async/await.
- **Avoid:** `try await Task.sleep(for: .seconds(1))` as a timing workaround.

### `test-no-shared-state`
- **Context:** Test isolation.
- **Rule:** Each test must set up its own state in `init`. Do not use global variables or static state in test suites.
- **Avoid:** `static var` shared between tests. Global state mutation in parallel test suites.

### `test-mainactor-isolation`
- **Context:** UI-bound and main-thread-only code.
- **Rule:** Mark tests `@MainActor` when they interact with UI-facing observable state, main-thread-only frameworks, or code explicitly isolated to the main actor.
- **Avoid:** Assuming a test happens to run on the main thread. Cross-actor calls that hide isolation bugs.

### `test-behavior-names`
- **Context:** Test readability.
- **Rule:** Use `@Test("description of observable behavior")` with descriptive names that describe what the code does.
- **Avoid:** `func testUpdateName()` style names. Names that describe implementation, not behavior.

### `test-serialized-scope`
- **Context:** Test parallelism.
- **Rule:** Use `@Suite(.serialized)` only when tests share actual external state (database connection, file system, shared process state). Not for expressing sequential workflow.
- **Avoid:** `@Suite(.serialized)` as a default or to enforce a "run in order" approach.

## 2. Persistence Testing Rules (`test-data-`)

### `test-swiftdata-inmemory`
- **Context:** SwiftData tests.
- **Rule:** Always use an in-memory `ModelConfiguration`. Create a fresh `ModelContainer` in each test suite `init()`.

```swift
init() throws {
    let config = ModelConfiguration(isStoredInMemoryOnly: true)
    container = try ModelContainer(for: Order.self, configurations: config)
}
```

- **Avoid:** Testing against a persistent disk store. Sharing a `ModelContext` between tests.

### `test-predicate-validation`
- **Context:** SwiftData predicates.
- **Rule:** Test predicates with boundary data: empty strings, nil values, minimum and maximum values. Verify the predicate returns exactly the expected subset.
- **Avoid:** Only testing the happy path for predicates.

## 3. UI Testing Rules (`ui-test-`)

### `ui-test-accessibility-identifiers`
- **Context:** Element lookup.
- **Rule:** Add `.accessibilityIdentifier("stable-id")` in SwiftUI views. Use these IDs — not labels or text — in XCTest for all element lookups.
- **Avoid:** `.staticTexts["Exact String"]` lookups (break on localization changes).

### `ui-test-page-objects`
- **Context:** Test maintainability.
- **Rule:** Encapsulate each screen's elements and interactions in a Page Object class. Tests call page object methods, not raw `XCUIElement` APIs directly.
- **Avoid:** Raw element lookups repeated across multiple test functions.

### `ui-test-no-sleep`
- **Context:** Element synchronization.
- **Rule:** Use `waitForExistence(timeout: 5)` before interacting with elements that appear after animations or network calls. Never use `sleep()`.
- **Avoid:** `sleep(2)` or similar hardcoded waits.

### `ui-test-xctest-only`
- **Context:** Framework selection.
- **Rule:** All tests that use `XCUIApplication`, `XCUIElement`, or `addUIInterruptionMonitor` must use `XCTest`, not Swift Testing.
- **Avoid:** `import Testing` in UI test targets.

## Cross Reference Map

- `test-*`:
  see `../references/swift-testing.md`
- `test-swiftdata-inmemory`, `test-predicate-validation`:
  see `../references/persistence-testing.md`, `../../swiftui/references/swiftdata.md`
- `ui-test-*`:
  see `../references/ui-testing.md`, `../../swiftui/references/accessibility.md`, `../../swiftui/references/navigation.md`

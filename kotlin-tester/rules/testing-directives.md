# Rules for Kotlin Testing

Actionable directives for authoring and debugging tests in Kotlin.

## 1. Core Testing Rules (`test-`)

### `test-given-when-then`
- **Context:** Test structure.
- **Rule:** Every test must have explicit GIVEN (setup), WHEN (action), THEN (assertion) sections separated by blank lines and comments.
- **Avoid:** Flat test body without clear separation.

### `test-main-dispatcher-rule`
- **Context:** ViewModel testing.
- **Rule:** Apply `MainDispatcherRule` (sets `UnconfinedTestDispatcher` on Main) for all ViewModel tests. Required for `viewModelScope.launch` to work.
- **Avoid:** Tests failing because `Dispatchers.Main` is not initialized.

### `test-no-sleep`
- **Context:** Async synchronization.
- **Rule:** Never use `Thread.sleep` or `Task.sleep` in tests. Use `advanceUntilIdle()`, `advanceTimeBy()`, Turbine `awaitItem()`, or `confirmation`.
- **Avoid:** `Thread.sleep(1000)` or `delay(1000)` as timing workarounds.

### `test-no-shared-state`
- **Context:** Test isolation.
- **Rule:** Each test must set up its own state in `@Before`. No global or static mutable state shared between tests.
- **Avoid:** `companion object { var sharedState = ... }` or `@JvmStatic` mutable fields.

### `test-behavior-names`
- **Context:** Test naming.
- **Rule:** Use `SHOULD [expected behavior] WHEN [action/event] GIVEN [precondition]` naming. Backtick function names in Kotlin.
- **Avoid:** `testMethod1()`, `testUpdateName()` — names that describe implementation, not behavior.

### `test-fresh-sut`
- **Context:** System under test.
- **Rule:** Create a fresh SUT instance in `@Before` for every test. Inject fresh mocks.
- **Avoid:** Reusing SUT across tests without re-initialization.

### `test-no-mock-data-classes`
- **Context:** Mocking strategy.
- **Rule:** Use real data class instances for test data. Mock only interfaces and external dependencies.
- **Avoid:** `mockk<User>()` — use `User(id = "1", name = "Test")` instead.

### `test-no-private-testing`
- **Context:** Test scope.
- **Rule:** Test through public API only. Private functions are tested indirectly through public methods.
- **Avoid:** Using reflection to test private functions.

### `test-error-paths`
- **Context:** Coverage completeness.
- **Rule:** Cover error paths, edge cases (empty, null, boundary), and failure scenarios — not just happy path.
- **Avoid:** Only testing success cases.

### `test-tdd-red-first`
- **Context:** TDD workflow.
- **Rule:** Write the failing test first (RED), implement minimal code to pass (GREEN), then refactor. Never skip the RED phase.
- **Avoid:** Writing implementation before tests.

### `test-junit5-android`
- **Context:** Android Testing.
- **Rule:** Use JUnit 5 for Android unit tests when possible. Requires `android-junit5` plugin. Use `@Test` from `org.junit.jupiter.api`.
- **Avoid:** JUnit 4 for new JVM-based unit tests if JUnit 5 is configured.

### `test-mockk-constructor`
- **Context:** Mocking.
- **Rule:** Use `mockkConstructor(MyClass::class)` only when you cannot inject the dependency. Prefer constructor injection.
- **Avoid:** Overusing constructor mocking as it indicates poor design.

### `test-kotest-assertions`
- **Context:** Assertions.
- **Rule:** Use Kotest's `shouldBe`, `shouldThrow`, `shouldNotBeNull` for readable and idiomatic assertions.
- **Avoid:** `assertEquals`, `assertTrue` from JUnit when using Kotest.

### `test-kmp-common-test`
- **Context:** Kotlin Multiplatform.
- **Rule:** Put shared logic tests in `commonTest`. Use `kotlin.test` assertions for cross-platform compatibility.
- **Avoid:** Platform-specific tests for pure business logic.

## 2. Coroutine Testing Rules (`ctest-`)

### `ctest-runtest-for-suspend`
- **Context:** Suspend function testing.
- **Rule:** Wrap all tests calling suspend functions in `runTest { }`. Never use `runBlocking`.
- **Avoid:** `runBlocking { sut.suspendFunction() }` in tests.

### `ctest-advance-until-idle`
- **Context:** Async completion.
- **Rule:** Call `advanceUntilIdle()` after triggering async operations in ViewModel/Repository tests to ensure all coroutines complete.
- **Avoid:** Assuming coroutines complete immediately without `advanceUntilIdle()`.

### `ctest-turbine-for-flow`
- **Context:** Flow testing.
- **Rule:** Use Turbine's `.test { }` extension for testing Flow/StateFlow emissions. Use `awaitItem()`, `expectNoEvents()`, `cancelAndIgnoreRemainingEvents()`.
- **Avoid:** `flow.toList()` for complex emission timing tests.

### `ctest-fake-over-mock-flow`
- **Context:** Flow test dependencies.
- **Rule:** Prefer `FakeRepository` with `MutableStateFlow` over mocking Flow return values. Fakes give realistic emission behavior.
- **Avoid:** `every { repo.observeItems() } returns flowOf(items)` for complex scenarios.

### `ctest-test-dispatcher`
- **Context:** Dispatcher control.
- **Rule:** Use `UnconfinedTestDispatcher()` for eager execution (most tests) or `StandardTestDispatcher()` for controlled timing (testing delays).
- **Avoid:** Real dispatchers in tests.

## 3. UI Testing Rules (`ui-test-`)

### `ui-test-testtag-selectors`
- **Context:** Element lookup.
- **Rule:** Use `Modifier.testTag("stable-id")` in Compose, `withId(R.id.view)` in Espresso. Never rely on displayed text or position.
- **Avoid:** `onNodeWithText("Login")` or `onData().atPosition(0)` as primary selectors.

### `ui-test-robot-pattern`
- **Context:** Test maintainability.
- **Rule:** Use Robot/Page Object pattern for UI tests. Encapsulate screen interactions in Robot classes with fluent API.
- **Avoid:** Raw `onView()` or `composeTestRule.onNodeWithTag()` calls repeated across tests.

### `ui-test-idling-resource`
- **Context:** Async UI synchronization.
- **Rule:** Use `IdlingResource` (Espresso) or `waitUntil` (Compose) for async operations. Register before test, unregister after.
- **Avoid:** `Thread.sleep(2000)` waiting for network or animations.

### `ui-test-no-sleep`
- **Context:** UI test timing.
- **Rule:** Never use `Thread.sleep` in UI tests. Use `waitUntil`, `IdlingResource`, or `advanceTimeBy`.
- **Avoid:** `sleep(2)` in instrumented tests.

### `ui-test-orchestrator`
- **Context:** Instrumented test isolation.
- **Rule:** Enable `ANDROIDX_TEST_ORCHESTRATOR` for all instrumented tests. Each test gets a clean state.
- **Avoid:** Running instrumented tests without Orchestrator (shared state between tests).

### `ui-test-no-live-network`
- **Context:** Network in tests.
- **Rule:** Use `MockWebServer` or DI fakes for network. Never hit live backends in tests.
- **Avoid:** Tests that fail when the server is down.

### `ui-test-stable-selectors`
- **Context:** Selector durability.
- **Rule:** Use resource IDs, testTags, or content descriptions. Never use localized text, dynamic content, or position-only selectors.
- **Avoid:** `onNodeWithText(getString(R.string.login))` that breaks on locale change.

### `ui-test-per-test-isolation`
- **Context:** Test state.
- **Rule:** Clear app data, reset feature flags, and use fresh test accounts per test. Orchestrator helps but explicit cleanup is required.
- **Avoid:** Tests that pass in isolation but fail when run together.

## 4. Coverage Rules (`cov-`)

### `cov-kover-config`
- **Context:** Code coverage.
- **Rule:** Configure Kover with HTML + XML reports. Exclude generated and config code. Set up CI verification.
- **Avoid:** No coverage tooling or relying on manual reports.

### `cov-threshold-enforcement`
- **Context:** Coverage standards.
- **Rule:** Critical business logic: 100%. Public APIs: 90%+. General code: 80%+. Build fails below thresholds.
- **Avoid:** Coverage below 80% without documented justification.

## Cross Reference Map

- `test-*`:
  see `../references/unit-testing.md`, `../references/tdd-workflow.md`
- `ctest-*`:
  see `../references/flow-testing.md`, `../references/unit-testing.md`
- `ui-test-*`:
  see `../references/espresso-testing.md`, `../references/compose-testing.md`, `../references/instrumented-testing.md`
- `cov-*`:
  see `../references/coverage.md`, `../references/ci-testing.md`

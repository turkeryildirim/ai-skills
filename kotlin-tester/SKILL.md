---
name: kotlin-tester
description: Kotlin testing patterns for Android and KMP — JUnit 5, Kotest, MockK, Coroutines Test, Turbine, Espresso, Compose Testing, and UIAutomator. Use when authoring, refactoring, or debugging tests. Triggers on "test", "MockK", "Espresso", "Compose test", "runTest", "Turbine", "Kotest", "coverage".
model: inherit
---

# Kotlin Testing Best Practices

Modern testing patterns for Android, Kotlin, and KMP — JUnit 5, Kotest, MockK, Coroutines Test, Turbine, Espresso, Compose Testing, and UIAutomator. Focused on reliability, speed, and maintainability.

## Specialized Agents

| Agent | Role | Focus |
|-------|------|-------|
| **kotlin-tester-pro** | Test Expert | JUnit 5, Kotest, MockK, Coroutines, Espresso, Compose Testing, CI. |

## When to Use

Reference these guidelines when:
- Writing unit tests for ViewModels, UseCases, Repositories, mappers
- Writing Compose UI tests with `createComposeRule`
- Writing Espresso tests for View-based UIs
- Writing UIAutomator tests for system UI and cross-app flows
- Testing coroutines and Flow with `runTest` and Turbine
- Property-based testing with Kotest
- Testing shared code in KMP `commonTest`
- Setting up code coverage with Kover
- Configuring Gradle Managed Devices for CI
- Following TDD (RED/GREEN/REFACTOR) workflow
- Diagnosing flaky tests

## Step 1: Check Test Surface and Framework

- **Android projects:** JUnit 5 (or 4) + MockK + Turbine + `runTest` for unit tests. Espresso or Compose Testing for UI.
- **KMP projects:** `commonTest` with `kotlin.test` or Kotest. Platform-specific tests in `androidDeviceTest` / `iosTest`.
- **Kotlin server projects:** Kotest + MockK for unit tests. `testApplication` for Ktor.
- **Mixed projects:** Keep framework boundaries explicit. Do not mix JUnit and Kotest in the same file.

## Core Directives

### MUST DO

- **Naming:** Use `SHOULD [behavior] WHEN [action] GIVEN [precondition]` for test function names.
- **Structure:** GIVEN / WHEN / THEN in every test. Separate setup, action, and assertion.
- **Coroutines:** Use `runTest` for all suspend function tests. Call `advanceUntilIdle()` after async operations.
- **Dispatchers:** Use `MainDispatcherRule` (set `UnconfinedTestDispatcher` on Main) for ViewModel tests.
- **Flow:** Use Turbine's `.test {}` for Flow/StateFlow assertions.
- **Mocking:** Use `coEvery`/`coVerify` for suspend functions. Use `mockk(relaxed = true)` only for logs/non-critical deps.
- **Isolation:** Each test sets up its own SUT in `@Before` (or `beforeTest`). No shared mutable state.
- **Behavior:** Test observable behavior, not implementation details.
- **Coverage:** Target 80%+ general, 90%+ for public APIs, 100% for critical business logic.
- **UI Tests:** Use `Modifier.testTag` in Compose, `withId()` in Espresso. Never rely on displayed text.
- **Instrumented:** Use AndroidX Test Orchestrator. Disable animations. Use IdlingResources instead of sleep.

### MUST NOT DO

- **Sleep:** Never use `Thread.sleep` or `Task.sleep` in tests. Use `advanceUntilIdle()`, `advanceTimeBy()`, or Turbine.
- **Live Backend:** Never run tests against live network. Use MockWebServer, fakes, or MockK.
- **Mock Data Classes:** Do not mock data classes — use real instances.
- **Private Functions:** Do not test private functions directly — test through public API.
- **Mixed Frameworks:** Do not mix JUnit and Kotest imports in the same file.
- **Flaky Selectors:** Do not use localized text or position-based selectors for UI tests.
- **Execution Order:** Do not assume tests run in declaration order.
- **Shared State:** Do not use global or static state in test suites.

## Category Index — When to Load Which Reference

| # | Category | Impact | Load when… | Reference |
|--:|----------|:------:|------------|-----------|
| 1 | Unit Testing | CRITICAL | JUnit 5/4, ViewModel/UseCase/Repo tests, GIVEN/WHEN/THEN | [`references/unit-testing.md`](references/unit-testing.md) |
| 2 | Kotest | HIGH | Kotest specs, matchers, BehaviorSpec, property testing | [`references/kotest.md`](references/kotest.md) |
| 3 | Mocking | CRITICAL | MockK setup, stubbing, verification, capture, spy | [`references/mocking.md`](references/mocking.md) |
| 4 | Flow Testing | CRITICAL | Turbine, StateFlow testing, Flow assertions | [`references/flow-testing.md`](references/flow-testing.md) |
| 5 | TDD Workflow | HIGH | RED/GREEN/REFACTOR, TDD cycle, step-by-step guide | [`references/tdd-workflow.md`](references/tdd-workflow.md) |
| 6 | Property Testing | MEDIUM | Kotest property-based, Arb generators, checkAll | [`references/property-testing.md`](references/property-testing.md) |
| 7 | Coverage | MEDIUM | Kover config, coverage thresholds, CI integration | [`references/coverage.md`](references/coverage.md) |
| 8 | Espresso Testing | HIGH | View-based UI, RecyclerView, Intents, Robot Pattern | [`references/espresso-testing.md`](references/espresso-testing.md) |
| 9 | Compose Testing | HIGH | Compose UI tests, testTag, gestures, semantics | [`references/compose-testing.md`](references/compose-testing.md) |
| 10 | Instrumented Testing | HIGH | UIAutomator, Orchestrator, flake control, ADB | [`references/instrumented-testing.md`](references/instrumented-testing.md) |
| 11 | CI Testing | MEDIUM | GMD, GitHub Actions, Firebase Test Lab, artifacts | [`references/ci-testing.md`](references/ci-testing.md) |

## Rule Index

### 1. Core Testing (`test-`) — CRITICAL
`test-given-when-then` · `test-main-dispatcher-rule` · `test-no-sleep` · `test-no-shared-state` · `test-behavior-names` · `test-fresh-sut` · `test-no-mock-data-classes` · `test-no-private-testing` · `test-error-paths` · `test-tdd-red-first` · `test-junit5-android` · `test-mockk-constructor` · `test-kotest-assertions` · `test-kmp-common-test`

### 2. Coroutine Testing (`ctest-`) — CRITICAL
`ctest-runtest-for-suspend` · `ctest-advance-until-idle` · `ctest-turbine-for-flow` · `ctest-fake-over-mock-flow` · `ctest-test-dispatcher`

### 3. UI Testing (`ui-test-`) — HIGH
`ui-test-testtag-selectors` · `ui-test-robot-pattern` · `ui-test-idling-resource` · `ui-test-no-sleep` · `ui-test-orchestrator` · `ui-test-no-live-network` · `ui-test-stable-selectors` · `ui-test-per-test-isolation`

### 4. Coverage (`cov-`) — MEDIUM
`cov-kover-config` · `cov-threshold-enforcement`

## Validation Checklist

- [ ] Test naming follows `SHOULD...WHEN...GIVEN` pattern
- [ ] GIVEN / WHEN / THEN structure in every test
- [ ] `MainDispatcherRule` applied for ViewModel tests
- [ ] `runTest` used for suspend functions
- [ ] `advanceUntilIdle()` called after async operations
- [ ] Turbine used for Flow/StateFlow assertions
- [ ] JUnit 5 used for new Android unit tests
- [ ] Shared business logic tested in `commonTest` for KMP
- [ ] No `Thread.sleep` in any test
- [ ] Each test creates its own SUT in `@Before`
- [ ] Error paths and edge cases covered
- [ ] No shared mutable state between tests
- [ ] UI tests use testTag / withId for element lookup
- [ ] No live network calls in tests
- [ ] Kover configured with 80%+ threshold
- [ ] Compose tests use `createComposeRule` or `createAndroidComposeRule`
- [ ] Instrumented tests use AndroidX Test Orchestrator
- [ ] Animations disabled for instrumented tests

## External References

- [MockK Documentation](https://mockk.io/)
- [Kotlin Coroutines Test](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Turbine](https://github.com/cashapp/turbine)
- [Kotest](https://kotest.io/)
- [JUnit 5 Android Guide](https://github.com/mannodermaus/android-junit5)
- [Espresso](https://developer.android.com/training/testing/espresso)
- [Compose Testing](https://developer.android.com/develop/ui/compose/testing)
- [UIAutomator](https://developer.android.com/training/testing/other-components/ui-automator)
- [Android Testing Guide](https://developer.android.com/training/testing)
- [Kover](https://github.com/Kotlin/kotlinx-kover)

---
name: swiftui-tester
description: Swift Testing and XCTest patterns for SwiftUI apps. Use when authoring, refactoring, or debugging tests. Triggers on "test", "#expect", "#require", "XCTest", "unit test", "integration test", "@Test", "@Suite", "withKnownIssue".
model: inherit
---

# SwiftUI Testing Best Practices

Modern testing patterns using **Swift Testing** (Xcode 16+, Swift 6+) and **XCTest**. Focused on unit testing business logic, integration testing SwiftUI data flow, and UI testing.

## Specialized Agents

| Agent | Role | Focus |
|-------|------|-------|
| **swiftui-tester-pro** | Test Expert | Swift Testing, XCTest, Mocking, Async Testing, Migration. |

## When to Use

Reference these guidelines when:
- Writing new unit tests using Swift Testing (`@Test`, `#expect`, `#require`)
- Migrating legacy XCTest suites to Swift Testing
- Writing UI tests with XCTest
- Testing Swift Concurrency (async tests, actor isolation, confirmations)
- Mocking dependencies using Dependency Injection in tests
- Testing SwiftData models and predicates
- Using parameterized tests, test traits, `withKnownIssue`, and attachments
- Debugging failing tests or flaky UI tests

## Step 1: Check Test Surface and Tooling

- Use **Swift Testing** for new unit and integration tests when the project is on Xcode 16+ / Swift 6+.
- Keep **XCTest** for UI tests and any legacy areas where the target or tooling still requires it.
- If the project mixes both frameworks, keep file boundaries explicit and avoid casual cross-imports.

## Core Directives

### MUST DO

- **Swift Testing:** Use Swift Testing for all new unit and integration tests (Xcode 16+, Swift 6+).
- **Suites:** Use `struct` for test suites — enables parallel execution and no shared state by default.
- **Lifecycle:** Use `init()` for struct-suite setup. Switch to a `final class` suite only when reference semantics or `deinit` cleanup is genuinely needed.
- **Assertions:** Use `#expect` for general assertions; `#require` when a failure should stop the test immediately.
- **Async:** Mark tests `async` and `await` all async calls.
- **Actor Isolation:** Mark UI-facing or main-thread-bound tests `@MainActor` instead of relying on implicit thread affinity.
- **Data:** Use in-memory `ModelContainer` for testing SwiftData models.
- **UI Testing:** Use **XCTest** for UI tests — Swift Testing does not support `XCUIApplication`.
- **Known Issues:** Use `withKnownIssue()` to mark expected failures with tracking context.
- **Test Behavior:** Write tests that test behavior (what the code does), not implementation (how it does it).
- **Error Paths:** Cover error paths and edge cases, not just the happy path.
- **Determinism:** Prefer injected clocks, stubbed dependencies, and explicit launch arguments over timing assumptions.

### MUST NOT DO

- **Legacy Assertions:** Do NOT use `XCTAssert` in Swift Testing suites.
- **Shared State:** Do NOT use global variables or static state in test suites.
- **Blocking:** Never use `Thread.sleep`; use `confirmation` for async events or `await Task.yield()` for cooperative scheduling.
- **UI Tests in Swift Testing:** Do NOT attempt to use Swift Testing for `XCUIApplication` interactions.
- **Implementation Testing:** Do NOT test internal implementation details — test observable behavior.
- **Mixed Frameworks:** Do NOT mix `import XCTest` and `import Testing` in the same file (unless bridging intentionally).
- **Order Dependency:** Do NOT assume tests run in declaration order — Swift Testing runs in parallel by default.
- **Main-Thread Assumptions:** Do NOT rely on background tests implicitly mutating UI-bound state; isolate them with `@MainActor`.

## Category Index — When to Load Which Reference

| # | Category | Impact | Load when… | Reference |
|--:|----------|:------:|------------|-----------|
| 1 | Swift Testing | CRITICAL | `@Test`, traits, async assertions, migration | [`references/swift-testing.md`](references/swift-testing.md) |
| 2 | Persistence Testing | HIGH | SwiftData, CRUD, predicates, delete rules | [`references/persistence-testing.md`](references/persistence-testing.md) |
| 3 | UI Testing | HIGH | XCTest UI flows, identifiers, launch args, screenshots | [`references/ui-testing.md`](references/ui-testing.md) |

## Rule Index

### 1. Swift Testing (`test-`) — CRITICAL
`test-struct-suites` · `test-expect-vs-require` · `test-parameterized` · `test-async-confirmation` · `test-known-issue` · `test-no-sleep` · `test-no-shared-state` · `test-behavior-names` · `test-serialized-scope` · `test-mainactor-isolation`

### 2. Persistence Testing (`test-data-`) — HIGH
`test-swiftdata-inmemory` · `test-predicate-validation`

### 3. UI Testing (`ui-test-`) — HIGH
`ui-test-accessibility-identifiers` · `ui-test-page-objects` · `ui-test-no-sleep` · `ui-test-xctest-only`

## Validation Checklist

- [ ] New tests use `import Testing`.
- [ ] Test suites are defined as `struct`.
- [ ] `init()` is used for struct-suite setup; class suites are justified explicitly.
- [ ] `#require` used for unwrapping optionals or critical preconditions.
- [ ] `#expect(throws:)` used for error path verification.
- [ ] SwiftData tests use an in-memory container.
- [ ] Async tests `await` results — no `Thread.sleep`.
- [ ] `confirmation` used for async event verification.
- [ ] UI-bound tests are marked `@MainActor` when they touch main-thread-only state.
- [ ] UI tests use accessibility identifiers for stable element lookup.
- [ ] No `XCTest` imports in Swift Testing files (unless bridging).
- [ ] No shared state between test cases.
- [ ] `withKnownIssue` used for tracked/expected failures.
- [ ] Test names describe behavior, not implementation (`"user can update their display name"` not `"test updateName"`).
- [ ] Error paths and edge cases are covered.
- [ ] `@Suite(.serialized)` only used when tests share external state.

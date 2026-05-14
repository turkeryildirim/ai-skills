# Swift Testing (Xcode 16+, Swift 6+)

Expert guidance for using the Swift Testing framework for unit and integration tests.

## 1. Core Structure

```swift
import Testing

@Suite("User Authentication")
struct AuthenticationTests {
    let service: AuthService

    init() {
        // ✅ Use init() for struct-suite setup instead of setUp()/tearDown()
        service = AuthService(client: MockHTTPClient())
    }

    @Test("valid credentials return authenticated user")
    func validLogin() async throws {
        let user = try await service.login(email: "test@example.com", password: "secret")
        #expect(user.isAuthenticated)
        #expect(user.email == "test@example.com")
    }

    @Test("invalid password throws authenticationFailed error")
    func invalidPassword() async throws {
        #expect(throws: AuthError.authenticationFailed) {
            try await service.login(email: "test@example.com", password: "wrong")
        }
    }
}
```

- **`struct` suites:** Use `struct` for parallel execution with no shared state. Switch to `final class` only when you need reference semantics or `deinit` cleanup.
- **Descriptive names:** Use `@Test("behavior description")` — focus on what the code does, not what the function is named.
- **Error coverage:** Always test error paths with `#expect(throws:)`.

## 2. Assertions

```swift
// #expect — records failure, continues test
#expect(result == expected)
#expect(!items.isEmpty)
#expect(user.name == "Türker")

// #require — records failure AND stops test immediately
// Use when subsequent assertions depend on this value
let user = try #require(response.user)  // Stops if nil
#expect(user.role == .admin)            // Runs only if user is non-nil

// Error assertions
#expect(throws: NetworkError.noConnection) {
    try await client.fetch(invalidURL)
}
```

| Macro | Behavior | Use When |
|-------|----------|----------|
| `#expect` | Records failure, continues | Independent checks |
| `#require` | Stops test on failure | Unwrapping optionals, critical preconditions |

## 3. Parameterized Tests

```swift
// Single argument
@Test("formatting numbers with various locales",
      arguments: ["en_US", "de_DE", "tr_TR", "ar_SA"])
func numberFormatting(locale: String) {
    let formatted = formatter.format(1234.56, locale: Locale(identifier: locale))
    #expect(!formatted.isEmpty)
}

// Multiple arguments (Cartesian product)
@Test("order processing for all states and priorities",
      arguments: OrderStatus.allCases, Priority.allCases)
func orderProcessing(status: OrderStatus, priority: Priority) {
    let order = Order(status: status, priority: priority)
    #expect(order.isValid)
}
```

Each argument combination runs as an independent, parallel test case.

## 4. Async Testing and Confirmations

```swift
// ✅ Basic async test
@Test("profile loads asynchronously")
func loadProfile() async throws {
    let profile = try await profileService.fetch(userId: "123")
    #expect(profile.name == "Türker")
}

// ✅ Confirmation — verifies async event occurs N times
@Test("notification posted exactly once on save")
func saveNotification() async {
    await confirmation("save notification") { confirm in
        NotificationCenter.default.addObserver(forName: .didSave, object: nil, queue: nil) { _ in
            confirm()
        }
        await dataService.save(item)
    }
}

// ✅ Confirmation with expected count
@Test("progress updates three times during upload")
func uploadProgress() async {
    await confirmation("progress update", expectedCount: 3) { confirm in
        await uploader.upload(data) { _ in confirm() }
    }
}

// ❌ Never use sleep for async verification
try await Task.sleep(for: .seconds(1))  // Wrong — use confirmation
```

## 5. Test Traits and Configuration

```swift
// Tags for filtering and categorization
extension Tag {
    @Tag static var networking: Self
    @Tag static var auth: Self
}

@Test("fetch returns user data", .tags(.networking, .auth))
func fetchUser() { }

// Disabled with reason
@Test("flaky network test", .disabled("Investigating timeout — see #1234"))
func flakyNetworkTest() { }

// Conditional execution
@Test("requires iOS 18+", .enabled(if: ProcessInfo.processInfo.operatingSystemVersion.majorVersion >= 18))
func newAPITest() { }

// Time limit
@Test("completes within one minute", .timeLimit(.minutes(1)))
func longRunningTest() async { }

// Bug tracking
@Test("handles malformed JSON", .bug("https://github.com/repo/issues/42"))
func malformedJSONHandling() { }
```

## 6. Execution Model

```swift
// Default: parallel execution (do NOT assume order)
@Suite
struct ParallelTests {
    @Test func testA() { }  // May run before or after testB
    @Test func testB() { }
}

// Serialized: only for tests sharing external state
@Suite(.serialized)
struct DatabaseIntegrationTests {
    // Tests sharing a real database connection must not run in parallel
    @Test func insertRecord() { }
    @Test func deleteRecord() { }
}
```

**`.serialized` is NOT for expressing workflow or declaration order** between tests — it's for shared external state only.

## 7. Known Issues

```swift
// Mark expected failures
@Test("propane tank heating")
func grillHeating() {
    withKnownIssue("Propane tank is empty — see #567") {
        #expect(truck.grill.isHeating)  // Fails — but tracked
    }
}

// Conditional known issue
withKnownIssue("Only fails on simulator") {
    #expect(result == expected)
} when: {
    ProcessInfo.processInfo.environment["SIMULATOR_DEVICE_NAME"] != nil
}
```

## 8. Test Attachments

```swift
@Test("image processing produces correct output")
func imageProcessing() throws {
    let result = try processor.process(inputImage)

    // Attach image for diagnosis on failure
    let attachment = Attachment(result, named: "processed-image.png")
    Attachment.record(attachment)

    #expect(result.size == CGSize(width: 100, height: 100))
}
```

## 9. Exit Tests (fatalError, preconditionFailure)

```swift
@Test("accessing invalid index crashes")
func invalidIndexCrash() {
    #expect(processExitsWith: .failure) {
        let array: [Int] = []
        _ = array[0]  // fatalError / preconditionFailure
    }
}
```

## 10. Migration from XCTest

| XCTest | Swift Testing |
|--------|---------------|
| `XCTAssert(a == b)` | `#expect(a == b)` |
| `XCTAssertEqual(a, b)` | `#expect(a == b)` |
| `XCTAssertNil(x)` | `#expect(x == nil)` |
| `XCTAssertNotNil(x)` | `#expect(x != nil)` |
| `try XCTUnwrap(x)` | `try #require(x)` |
| `XCTAssertThrowsError(try f())` | `#expect(throws: SomeError.self) { try f() }` |
| `setUp()` | `init()` |
| `tearDown()` | `deinit` (for class) |
| `XCTestExpectation` | `confirmation` |
| `class FooTests: XCTestCase` | `struct FooTests` |

## 11. Common Mistakes

1. Testing implementation rather than behavior.
2. Neglecting error path coverage.
3. Using `sleep` instead of `confirmation` in async tests.
4. Sharing mutable state between test cases.
5. Assuming declaration-order execution.
6. Mixing `import XCTest` and `import Testing` in single files (unless bridging).
7. Non-`Sendable` test helpers in concurrent test scenarios.
8. Using `@Suite(.serialized)` to express workflow dependencies.

## Cross References

- Related rules: `test-struct-suites`, `test-expect-vs-require`, `test-parameterized`, `test-async-confirmation`, `test-known-issue`, `test-no-sleep`, `test-no-shared-state`, `test-mainactor-isolation`, `test-behavior-names`, `test-serialized-scope`
- Related references: [`ui-testing.md`](ui-testing.md), [`persistence-testing.md`](persistence-testing.md), [`../../swiftui/references/concurrency.md`](../../swiftui/references/concurrency.md)

# UI Testing with XCTest

Guidelines for writing stable and effective UI tests for SwiftUI applications.

## Core Rule

**UI testing requires XCTest.** Swift Testing does NOT support `XCUIApplication`, `XCUIElement`, or system alert handling.

## 1. Setup

```swift
import XCTest

final class CheckoutUITests: XCTestCase {
    var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false  // Stop on first failure
        app = XCUIApplication()
        app.launchArguments = ["--ui-testing"]  // Enable test mode in app
        app.launch()
    }
}
```

- Set `continueAfterFailure = false` — UI tests fail fast to avoid cascading failures.
- Use launch arguments/environment variables to enable test-specific app behavior (mock data, disabled animations).

## 2. Accessibility Identifiers

**CRITICAL:** Use `.accessibilityIdentifier("stable-id")` in SwiftUI views for all UI test element lookups.

```swift
// In SwiftUI view
Button("Place Order") { placeOrder() }
    .accessibilityIdentifier("checkout_place_order_button")

TextField("Email", text: $email)
    .accessibilityIdentifier("login_email_field")
```

```swift
// In XCTest
let placeOrderButton = app.buttons["checkout_place_order_button"]
let emailField = app.textFields["login_email_field"]
```

Identifiers must be:
- **Stable:** Not dependent on localized text.
- **Unique per screen:** Prefix with screen name (`checkout_`, `login_`).
- **Snake_case:** Consistent naming convention.

## 3. Page Object Model (POM)

Encapsulate each screen's elements and interactions in a Page Object:

```swift
struct LoginPage {
    let app: XCUIApplication

    var emailField: XCUIElement { app.textFields["login_email_field"] }
    var passwordField: XCUIElement { app.secureTextFields["login_password_field"] }
    var loginButton: XCUIElement { app.buttons["login_submit_button"] }
    var errorLabel: XCUIElement { app.staticTexts["login_error_label"] }

    func login(email: String, password: String) {
        emailField.tap()
        emailField.typeText(email)
        passwordField.tap()
        passwordField.typeText(password)
        loginButton.tap()
    }
}

// Test uses page object methods — not raw XCUIElement APIs
func testSuccessfulLogin() {
    let loginPage = LoginPage(app: app)
    loginPage.login(email: "test@example.com", password: "correct")

    XCTAssertTrue(app.buttons["home_profile_button"].waitForExistence(timeout: 5))
}
```

## 4. Element Interaction

```swift
// ✅ Wait before interacting with async content
let element = app.buttons["confirm_button"]
XCTAssertTrue(element.waitForExistence(timeout: 5))
element.tap()

// ✅ Text input
let field = app.textFields["search_field"]
field.tap()
field.typeText("SwiftUI")

// ✅ Scroll
app.swipeUp()
app.scrollViews.firstMatch.swipeDown()

// ✅ Verify element state
XCTAssertTrue(app.staticTexts["success_label"].exists)
XCTAssertFalse(app.staticTexts["error_label"].exists)
```

## 5. Handling System Alerts

```swift
// Register before performing action that triggers alert
addUIInterruptionMonitor(withDescription: "Location permission") { alert in
    alert.buttons["Allow While Using App"].tap()
    return true
}

// Trigger the action
app.buttons["enable_location_button"].tap()
app.tap()  // Required to process interruption monitor
```

## 6. Screenshots on Failure

```swift
override func tearDownWithError() throws {
    if testRun?.failureCount ?? 0 > 0 {
        let screenshot = app.screenshot()
        let attachment = XCTAttachment(screenshot: screenshot)
        attachment.name = "Failure Screenshot — \(name)"
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}
```

## 7. Disable Animations in Tests

In the app target, disable animations when launched in UI testing mode:

```swift
// AppDelegate or @main
if ProcessInfo.processInfo.arguments.contains("--ui-testing") {
    UIView.setAnimationsEnabled(false)
}
```

This prevents `waitForExistence` timeouts caused by animations.

## 8. MUST NOT DO

- **`sleep()`:** Never use hardcoded sleeps. Use `waitForExistence(timeout:)`.
- **Text-based lookups:** `app.staticTexts["Place Order"]` breaks on localization changes. Use identifiers.
- **Massive test functions:** Break large UI tests into focused scenarios by user journey.
- **Swift Testing for UI:** Never use `import Testing` in UI test targets.
- **No `continueAfterFailure = false`:** Without this, tests continue past failures and produce misleading results.

## Cross References

- Related rules: `ui-test-accessibility-identifiers`, `ui-test-page-objects`, `ui-test-no-sleep`, `ui-test-xctest-only`
- Related references: [`swift-testing.md`](swift-testing.md), [`../../swiftui/references/accessibility.md`](../../swiftui/references/accessibility.md), [`../../swiftui/references/navigation.md`](../../swiftui/references/navigation.md)

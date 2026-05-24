# Instrumented Testing (UIAutomator & Orchestrator)

Expert guidance for instrumented testing with UIAutomator, AndroidX Test Orchestrator, and cross-app UI automation.

## 1. Quick Reference Commands

| Task | Command |
|------|---------|
| List emulators | `emulator -list-avds` |
| Start emulator (headless) | `emulator -avd Pixel_8_API_34 -no-window -gpu swiftshader_indirect` |
| List connected devices | `adb devices` |
| Install APK | `adb install app-debug.apk` |
| Run all instrumented tests | `./gradlew connectedAndroidTest` |
| Run specific test class | `adb shell am instrument -w -e class com.example.MyTest com.example.test/androidx.test.runner.AndroidJUnitRunner` |
| Clear app data | `adb shell pm clear com.example` |
| Run with Orchestrator | `./gradlew connectedAndroidTest -PuseOrchestrator` |

## 2. AndroidX Test Orchestrator

Orchestrator runs each test in its own `Instrumentation` instance, ensuring per-test isolation (clean state, no shared storage pollution).

### Gradle setup

```kotlin
android {
    testOptions {
        execution = "ANDROIDX_TEST_ORCHESTRATOR"
    }
}

dependencies {
    androidTestUtil("androidx.test:orchestrator:1.5.1")
}
```

### Disable animations

```kotlin
android {
    testOptions {
        execution = "ANDROIDX_TEST_ORCHESTRATOR"
        animationsDisable = true
    }
}
```

Disabling animations prevents flaky `waitForIdle` and `waitForExistence` timeouts.

## 3. UIAutomator Setup

```kotlin
dependencies {
    androidTestImplementation("androidx.test.uiautomator:uiautomator:2.3.0")
    androidTestImplementation("androidx.test:runner:1.6.2")
    androidTestImplementation("androidx.test:rules:1.6.1")
}
```

### Core pattern

```kotlin
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.By
import androidx.test.uiautomator.Until

class CrossAppTest {
    private val device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())
    private val timeout = 5_000L

    @Test
    fun openBrowserAndVerifyUrl() {
        device.pressHome()
        device.wait(Until.hasObject(By.desc("Chrome")), timeout)

        val chrome = device.findObject(By.desc("Chrome"))
        chrome.click()

        device.wait(Until.hasObject(By.res("org.chromium.chrome", "url_bar")), timeout)
        val urlBar = device.findObject(By.res("org.chromium.chrome", "url_bar"))
        urlBar.text = "https://example.com"
        device.pressEnter()

        device.wait(Until.hasObject(By.text("Example Domain")), timeout)
        assert(device.findObject(By.text("Example Domain")) != null)
    }
}
```

### Waits with Until.hasObject (avoid sleeps)

```kotlin
val found = device.wait(Until.hasObject(By.desc("Submit")), 5_000)
assertTrue("Submit button never appeared", found)

val element = device.findObject(By.res("com.example", "status_text"))
device.wait(Until.hasObject(By.textContains("Success")), 10_000)
assertEquals("Success", element.text)
```

| Method | Purpose |
|--------|---------|
| `device.wait(Until.hasObject(selector), ms)` | Wait for element to appear |
| `device.wait(Until.gone(selector), ms)` | Wait for element to disappear |
| `device.waitForIdle(timeout)` | Wait for UI idle state |
| `device.hasObject(selector)` | Check if element exists (no wait) |

### Selector reference

| Selector | Purpose | Example |
|----------|---------|---------|
| `By.res(pkg, id)` | Resource ID | `By.res("com.example", "login_btn")` |
| `By.text(text)` | Exact text match | `By.text("Submit")` |
| `By.textContains(text)` | Partial text | `By.textContains("Loading")` |
| `By.desc(text)` | Content description | `By.desc("Settings")` |
| `By.clazz(className)` | Class name | `By.clazz("android.widget.EditText")` |
| `By.pkg(packageName)` | Package name | `By.pkg("com.example")` |
| `By.clickable(isClickable)` | Clickable state | `By.clickable(true)` |
| `By.checked(isChecked)` | Checked state | `By.checked(true)` |
| `By.enabled(isEnabled)` | Enabled state | `By.enabled(true)` |

## 4. Common Tasks

### Open notifications

```kotlin
device.openNotification()
device.wait(Until.hasObject(By.text("New message")), 3_000)
```

### Dismiss dialog

```kotlin
device.wait(Until.hasObject(By.text("OK")), 3_000)
device.findObject(By.text("OK")).click()
```

### Cross-app: launch browser

```kotlin
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://example.com"))
intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
InstrumentationRegistry.getInstrumentation().targetContext.startActivity(intent)

device.wait(Until.hasObject(By.text("Example Domain")), 5_000)
```

### Press hardware keys

```kotlin
device.pressHome()
device.pressBack()
device.pressEnter()
device.pressRecentApps()
```

## 5. Flake Control Principles

| Principle | Implementation |
|-----------|---------------|
| Use ATD system images | `aosp-atd` images are optimized for CI: smaller, faster, fewer pre-installed apps |
| Explicit waits only | Always use `Until.hasObject` or `waitUntil`; never `Thread.sleep` |
| Fail fast with diagnostics | Attach screenshots on failure; log view hierarchy |
| Avoid OEM-specific UI | Use AOSP or `aosp-atd` images; OEM skins (Samsung, Xiaomi) have different system UI |
| Isolate per test | Use Orchestrator; clear app data between tests |
| Retry with limit | Max 2 retries for flaky tests; if consistent, fix the root cause |

## 6. ADB Triage Commands

| Task | Command |
|------|---------|
| Screenshot | `adb shell screencap -p /sdcard/screen.png && adb pull /sdcard/screen.png` |
| Screen recording | `adb shell screenrecord /sdcard/test.mp4` (max 180s) |
| Pull recording | `adb pull /sdcard/test.mp4` |
| Logcat filtered | `adb logcat -s "TestRunner" "Espresso" "UIAutomator"` |
| Dump view hierarchy | `adb shell uiautomator dump /sdcard/ui.xml && adb pull /sdcard/ui.xml` |
| Clear app data | `adb shell pm clear com.example` |
| Grant permission | `adb shell pm grant com.example android.permission.CAMERA` |

## 7. Test Isolation Best Practices

### Clear data per test

```kotlin
@Before
fun clearAppData() {
    val context = InstrumentationRegistry.getInstrumentation().targetContext
    context.cacheDir.deleteRecursively()
    context.filesDir.deleteRecursively()
    context.getSharedPreferences("prefs", Context.MODE_PRIVATE).edit().clear().commit()
}
```

### Feature flags reset

```kotlin
@After
fun resetFeatureFlags() {
    FeatureFlagProvider.resetAll()
}
```

### Test accounts

```kotlin
companion object {
    @JvmStatic
    @BeforeClass
    fun ensureTestAccountExists() {
        TestAccountManager.createIfNotExists("test_automation@example.com")
    }

    @JvmStatic
    @AfterClass
    fun cleanupTestAccounts() {
        TestAccountManager.deleteAll("test_automation")
    }
}
```

## 8. When to Use What

| Tool | Best For |
|------|----------|
| **Espresso** | In-app View-based UI testing. Fast, deterministic, auto-synchronizes with async operations. |
| **Compose Testing** | In-app Jetpack Compose UI testing. Direct semantic tree access, no view hierarchy needed. |
| **UIAutomator** | Cross-app testing, system UI interactions, notifications, permissions dialogs, OEM-specific scenarios. |

### Decision flowchart

1. Testing Compose UI? -> Use Compose Testing (`createComposeRule`)
2. Testing View-based UI within your app? -> Use Espresso
3. Need to interact with system UI or other apps? -> Use UIAutomator
4. All three can coexist in the same test class if needed

## Cross References

- Related rules: `ui-test-orchestrator`, `ui-test-no-sleep`, `ui-test-per-test-isolation`, `ui-test-idling-resource`, `ui-test-disable-animations`
- Related references: [`espresso-testing.md`](espresso-testing.md), [`compose-testing.md`](compose-testing.md), [`ci-testing.md`](ci-testing.md), [`coverage.md`](coverage.md)

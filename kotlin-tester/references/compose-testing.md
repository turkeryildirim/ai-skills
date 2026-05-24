# Compose UI Testing

Expert guidance for testing Jetpack Compose UI with the official compose testing library.

## 1. Setup

```kotlin
dependencies {
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.7.8")
    debugImplementation("androidx.compose.ui:ui-test-manifest:1.7.8")
}
```

## 2. Test Rules

```kotlin
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.junit4.createAndroidComposeRule

class ButtonTest {
    @get:Rule
    val composeRule = createComposeRule()
}

class MainActivityTest {
    @get:Rule
    val composeRule = createAndroidComposeRule(MainActivity::class.java)
}
```

| Rule | Purpose |
|------|---------|
| `createComposeRule()` | Test composables in isolation — no Activity needed |
| `createAndroidComposeRule()` | Test within a real Activity (lifecycle, permissions) |

## 3. Finding Elements

```kotlin
import androidx.compose.ui.test.*

composeRule.onNodeWithTag("login_button")
composeRule.onNodeWithText("Sign In")
composeRule.onNodeWithContentDescription("Menu icon")
composeRule.onAllNodesWithTag("order_item")[0]
composeRule.onNode(hasText("Welcome") and hasClickAction())
composeRule.onNode(hasScrollAction())
```

| Finder | Purpose |
|--------|---------|
| `onNodeWithTag(tag)` | Find by `Modifier.testTag("tag")` — preferred |
| `onNodeWithText(text)` | Find by displayed text |
| `onNodeWithContentDescription(desc)` | Find by accessibility description |
| `onAllNodesWithTag(tag)` | Find multiple nodes; access by index |
| `onNode(matcher)` | Find with semantic matcher |

### Hierarchical finders

```kotlin
composeRule.onNode(
    hasAnyAncestor(that(hasTag("card_container"))) and hasText("Title")
)

composeRule.onNode(
    isSelectable() and hasText("Option A")
)
```

## 4. Actions

```kotlin
composeRule.onNodeWithTag("submit_button").performClick()
composeRule.onNodeWithTag("email_field").performTextInput("user@example.com")
composeRule.onNodeWithTag("email_field").performTextReplacement("new@example.com")
composeRule.onNodeWithTag("email_field").performTextClearance()
composeRule.onNodeWithTag("bottom_sheet").performScrollTo()
composeRule.onNodeWithTag("lazy_list").performScrollToIndex(15)
composeRule.onNodeWithTag("lazy_list").performScrollToKey("item_42")

composeRule.onNodeWithTag("card").performTouchInput { swipeLeft() }
composeRule.onNodeWithTag("card").performTouchInput { doubleClick() }
composeRule.onNodeWithTag("card").performTouchInput { longClick() }
composeRule.onNodeWithTag("image").performTouchInput { pinch(startDistance = 100f, endDistance = 200f) }
composeRule.onNodeWithTag("slider").performTouchInput { swipeRight(startX = 100f, endX = 300f) }
```

| Action | Purpose |
|--------|---------|
| `performClick()` | Click the element |
| `performTextInput(text)` | Append text to text field |
| `performTextReplacement(text)` | Replace all text |
| `performTextClearance()` | Clear text field |
| `performScrollTo()` | Scroll to make element visible |
| `performScrollToIndex(i)` | Scroll LazyColumn/LazyRow to index |
| `performScrollToKey(key)` | Scroll to item with key |
| `swipeLeft()` / `swipeRight()` | Swipe gesture |
| `doubleClick()` | Double-tap |
| `longClick()` | Long-press |
| `pinch()` | Pinch-to-zoom gesture |

## 5. Assertions

```kotlin
composeRule.onNodeWithTag("title").assertIsDisplayed()
composeRule.onNodeWithTag("deleted_view").assertDoesNotExist()
composeRule.onNodeWithTag("submit_button").assertIsEnabled()
composeRule.onNodeWithTag("submit_button").assertIsNotEnabled()
composeRule.onNodeWithTag("status_text").assertTextEquals("Success")
composeRule.onNodeWithTag("status_text").assertTextContains("ucc")
composeRule.onNodeWithTag("radio_option").assertIsSelected()
composeRule.onNodeWithTag("toggle").assertIsOn()
composeRule.onNodeWithTag("toggle").assertIsOff()
```

| Assertion | Purpose |
|-----------|---------|
| `assertIsDisplayed()` | Element is visible on screen |
| `assertDoesNotExist()` | Element is not in composition |
| `assertIsEnabled()` | Element is enabled |
| `assertIsNotEnabled()` | Element is disabled |
| `assertTextEquals(text)` | Exact text match (ignores whitespace by default) |
| `assertTextContains(text)` | Partial text match |
| `assertIsSelected()` | Selected state (radio, tab) |
| `assertIsOn()` / `assertIsOff()` | Toggle/Switch state |
| `assert(hasClickAction())` | Element is clickable |
| `assert(hasNoClickAction())` | Element is not clickable |

## 6. Synchronization

```kotlin
composeRule.waitForIdle()

composeRule.mainClock.advanceTimeBy(2000)

composeRule.waitUntil(timeoutMillis = 5_000) {
    composeRule.onNodeWithTag("loading").assertDoesNotExist()
    true
}

composeRule.waitUntilNodeCount(hasTag("result_item"), 5, timeoutMillis = 5_000)

composeRule.mainClock.autoAdvance = false
composeRule.mainClock.advanceTimeBy(300)
composeRule.mainClock.autoAdvance = true
```

| Method | Purpose |
|--------|---------|
| `waitForIdle()` | Wait for all pending compositions and animations |
| `advanceTimeBy(ms)` | Manually advance the test clock |
| `waitUntil { condition }` | Poll until condition is true |
| `autoAdvance = false` | Freeze time for precise animation testing |

## 7. Testing Patterns

### Test in isolation

```kotlin
@Test
fun buttonClickInvokesCallback() {
    var clicked = false

    composeRule.setContent {
        Button(onClick = { clicked = true }, modifier = Modifier.testTag("btn")) {
            Text("Click Me")
        }
    }

    composeRule.onNodeWithTag("btn").performClick()

    assert(clicked)
}
```

### Test with ViewModel

```kotlin
@Test
fun loginScreenShowsErrorOnFailure() {
    val fakeViewModel = LoginViewModel(FakeAuthRepository())

    composeRule.setContent {
        LoginScreen(viewModel = fakeViewModel)
    }

    composeRule.onNodeWithTag("email_field").performTextInput("bad@email")
    composeRule.onNodeWithTag("password_field").performTextInput("wrong")
    composeRule.onNodeWithTag("login_button").performClick()

    composeRule.onNodeWithTag("error_text").assertIsDisplayed()
    composeRule.onNodeWithTag("error_text").assertTextEquals("Invalid credentials")
}
```

### Test navigation

```kotlin
@Test
fun navigatingToDashboard() {
    val navController = TestNavHostController(ApplicationProvider.getApplicationContext())
    composeRule.setContent {
        AppNavHost(navController = navController)
    }

    composeRule.onNodeWithTag("login_button").performClick()

    composeRule.waitUntil(5_000) {
        navController.currentDestination?.route == "dashboard"
    }

    assertEquals("dashboard", navController.currentDestination?.route)
}
```

### Test state restoration

```kotlin
import androidx.compose.ui.test.junit4.StateRestorationTester

@Test
fun textRestoredAfterConfigChange() {
    val restorationTester = StateRestorationTester(composeRule)

    restorationTester.setContent {
        var text by rememberSaveable { mutableStateOf("") }
        TextField(
            value = text,
            onValueChange = { text = it },
            modifier = Modifier.testTag("input")
        )
    }

    composeRule.onNodeWithTag("input").performTextInput("Hello")

    restorationTester.emulateSavedInstanceStateRestore()

    composeRule.onNodeWithTag("input").assertTextEquals("Hello")
}
```

## 8. LazyColumn Testing

```kotlin
@Test
fun scrollAndClickItem() {
    composeRule.setContent {
        LazyColumn(Modifier.testTag("list")) {
            items(100) { index ->
                Text(
                    text = "Item $index",
                    modifier = Modifier.testTag("item_$index")
                )
            }
        }
    }

    composeRule.onNodeWithTag("list").performScrollToIndex(50)
    composeRule.onNodeWithTag("item_50").assertIsDisplayed()
}

@Test
fun dynamicContentAppearsAfterLoad() {
    composeRule.setContent {
        val items by remember { mutableStateOf(listOf<String>()) }
        LaunchedEffect(Unit) {
            delay(500)
            items = listOf("Alpha", "Beta", "Gamma")
        }
        LazyColumn(Modifier.testTag("list")) {
            items(items) { item ->
                Text(item, modifier = Modifier.testTag("item_$item"))
            }
        }
    }

    composeRule.waitUntilNodeCount(hasTag("item_Alpha"), 1, timeoutMillis = 3_000)
    composeRule.onNodeWithTag("item_Beta").assertIsDisplayed()
}
```

## 9. Screenshot Testing

### Capture to image (on-device)

```kotlin
@Test
fun matchesGoldenScreenshot() {
    composeRule.setContent {
        MyComposable()
    }

    composeRule.onRoot()
        .captureToImage()
        .asAndroidBitmap()
        .let { bitmap ->
            assertEquals(expectedWidth, bitmap.width)
            assertEquals(expectedHeight, bitmap.height)
        }
}
```

### Paparazzi (JVM-based, no emulator)

```kotlin
dependencies {
    testImplementation("app.cash.paparazzi:paparazzi:1.3.5")
}

class ScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun myComposable() {
        paparazzi.snapshot {
            MyComposable()
        }
    }
}
```

## 10. Debugging

```kotlin
composeRule.onNodeWithTag("container").printToLog("TEST_TREE")

composeRule.onAllNodesWithTag("item").apply {
    fetchSemanticsNodes().forEachIndexed { index, node ->
        Log.d("TEST_NODE", "Node $index: ${node.config}")
    }
}

composeRule.onNodeWithTag("list").onChildren().printToLog("CHILDREN")

composeRule.onNode(useUnmergedTree = true) {
    hasTestTag("inner_text")
}
```

| Method | Purpose |
|--------|---------|
| `printToLog(tag)` | Print semantic tree to logcat |
| `useUnmergedTree = true` | Access children of merged composables (e.g., `Button` containing `Text`) |

### useUnmergedTree

```kotlin
composeRule.onNode(
    matcher = hasTestTag("button_text"),
    useUnmergedTree = true
).assertTextEquals("Submit")
```

Use `useUnmergedTree = true` when a composable merges its children's semantics (e.g., `Button` merges `Text` inside it).

## 11. Best Practices

| Practice | Reason |
|----------|--------|
| Use `Modifier.testTag()` for all finders | Stable, localization-independent, refactoring-safe |
| Test in isolation with `setContent` | Fast, no Activity dependency |
| Use `waitUntil` for async content | Avoid flaky tests from race conditions |
| Test state restoration with `StateRestorationTester` | Verify `rememberSaveable` works correctly |
| Avoid `Thread.sleep` | Use `waitUntil` or `advanceTimeBy` instead |
| Use `onNodeWithText` sparingly | Breaks with localization; prefer `testTag` |
| Keep tests small and focused | One assertion scenario per test |

## Cross References

- Related rules: `ui-test-compose-testtag`, `ui-test-compose-isolation`, `ui-test-compose-waituntil`, `ui-test-compose-state-restoration`, `ui-test-no-sleep`
- Related references: [`espresso-testing.md`](espresso-testing.md), [`instrumented-testing.md`](instrumented-testing.md), [`coverage.md`](coverage.md)

# Espresso UI Testing

Expert guidance for writing stable, maintainable UI tests with Espresso for Android View-based screens.

## 1. Setup Dependencies

```kotlin
dependencies {
    androidTestImplementation("androidx.test.espresso:espresso-core:3.6.1")
    androidTestImplementation("androidx.test.espresso:espresso-intents:3.6.1")
    androidTestImplementation("androidx.test.espresso:espresso-contrib:3.6.1")
    androidTestImplementation("androidx.test:runner:1.6.2")
    androidTestImplementation("androidx.test:rules:1.6.1")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    debugImplementation("androidx.fragment:fragment-testing:1.8.6")
}
```

## 2. ViewMatchers

```kotlin
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.matcher.ViewMatchers.*

onView(withId(R.id.login_button))
onView(withText("Sign In"))
onView(withContentDescription("Navigate up"))
onView(allOf(withId(R.id.title), withText("Welcome")))
onView(not(isDisplayed()))
onView(hasSibling(withText("Order #123")))
onView(isDescendantOfA(withId(R.id.nav_host)))
```

| Matcher | Purpose | Example |
|---------|---------|---------|
| `withId` | Match by resource ID | `withId(R.id.email_field)` |
| `withText` | Match displayed text | `withText("Submit")` |
| `withContentDescription` | Match accessibility content description | `withContentDescription("Menu")` |
| `allOf` | Combine matchers (AND) | `allOf(withId(R.id.btn), isDisplayed())` |
| `not` | Negate a matcher | `not(isEnabled())` |
| `isDisplayed` | View is visible on screen | `isDisplayed()` |
| `hasSibling` | Match sibling view | `hasSibling(withText("Label"))` |
| `isDescendantOfA` | Match within container | `isDescendantOfA(withId(R.id.container))` |
| `withHint` | Match hint text | `withHint("Enter email")` |
| `withClassName` | Match class name | `withClassName(endsWith("EditText"))` |
| `withTagValue` | Match view tag | `withTagValue(`is`("header"))` |

## 3. ViewActions

```kotlin
import androidx.test.espresso.action.ViewActions.*

onView(withId(R.id.email_field)).perform(click())
onView(withId(R.id.email_field)).perform(typeText("user@example.com"))
onView(withId(R.id.email_field)).perform(replaceText("updated@example.com"))
onView(withId(R.id.email_field)).perform(clearText())
onView(withId(R.id.bottom_content)).perform(scrollTo())
onView(withId(R.id.pager)).perform(swipeLeft())
onView(withId(R.id.pager)).perform(swipeRight())
onView(withId(R.id.email_field)).perform(closeSoftKeyboard())
onView(withId(R.id.email_field)).perform(pressImeActionButton())
```

| Action | Purpose |
|--------|---------|
| `click()` | Tap the view |
| `typeText(text)` | Type text into editable field |
| `replaceText(text)` | Replace existing text |
| `clearText()` | Clear field contents |
| `scrollTo()` | Scroll to make view visible |
| `swipeLeft()` / `swipeRight()` | Swipe gesture on ViewPager |
| `closeSoftKeyboard()` | Dismiss on-screen keyboard |
| `pressImeActionButton()` | Press keyboard action (e.g., Done) |
| `doubleClick()` | Double-tap the view |
| `longClick()` | Long-press the view |

## 4. ViewAssertions

```kotlin
import androidx.test.espresso.assertion.ViewAssertions.*

onView(withId(R.id.result_text)).check(matches(isDisplayed()))
onView(withId(R.id.deleted_view)).check(doesNotExist())
onView(withId(R.id.submit_button)).check(matches(isEnabled()))
onView(withId(R.id.checkbox)).check(matches(isChecked()))
onView(withId(R.id.title)).check(matches(withText("Success")))
onView(withId(R.id.error_label)).check(matches(not(isDisplayed())))
```

| Assertion | Purpose |
|-----------|---------|
| `matches(matcher)` | Verify view matches condition |
| `doesNotExist()` | View is not in the view hierarchy |
| `matches(isEnabled())` | View is enabled |
| `matches(isChecked())` | CheckBox / Switch is checked |
| `matches(isNotChecked())` | CheckBox / Switch is unchecked |
| `matches(hasFocus())` | View has input focus |
| `matches(withText(text))` | View displays exact text |

## 5. RecyclerView Testing

```kotlin
import androidx.recyclerview.widget.RecyclerView
import androidx.test.espresso.contrib.RecyclerViewActions

onView(withId(R.id.recycler)).perform(
    RecyclerViewActions.scrollToPosition<RecyclerView.ViewHolder>(10)
)

onView(withId(R.id.recycler)).perform(
    RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(3, click())
)

onView(withId(R.id.recycler)).perform(
    RecyclerViewActions.actionOnItem<RecyclerView.ViewHolder>(
        hasDescendant(withText("Item 42")), click()
    )
)
```

### Click a child view inside a RecyclerView item

```kotlin
onView(withId(R.id.recycler)).perform(
    RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
        2,
        clickChildViewWithId(R.id.delete_button)
    )
)

fun clickChildViewWithId(childId: Int): ViewAction {
    return object : ViewAction {
        override fun getConstraints() = allOf(isDisplayed(), isClickable())
        override fun getDescription() = "Click child view with id $childId"
        override fun perform(uiController: UiController, view: View) {
            view.findViewById<View>(childId).performClick()
        }
    }
}
```

### Assert item count

```kotlin
fun withItemCount(count: Int): Matcher<View> {
    return object : BoundedMatcher<View, RecyclerView>(RecyclerView::class.java) {
        override fun matchesSafely(recycler: RecyclerView): Boolean {
            return recycler.adapter?.itemCount == count
        }
        override fun describeTo(description: Description) {
            description.appendText("RecyclerView with item count: $count")
        }
    }
}

onView(withId(R.id.recycler)).check(matches(withItemCount(5)))
```

## 6. Intent Testing

```kotlin
import androidx.test.espresso.intent.Intents
import androidx.test.espresso.intent.matcher.IntentMatchers.*

class CheckoutIntentTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(CheckoutActivity::class.java)

    @Before
    fun setup() {
        Intents.init()
    }

    @After
    fun teardown() {
        Intents.release()
    }

    @Test
    fun clickingBuyOpensPaymentScreen() {
        Intents.intending(hasComponent(PaymentActivity::class.java.name))
            .respondWith(Instrumentation.ActivityResult(Activity.RESULT_OK, null))

        onView(withId(R.id.buy_button)).perform(click())

        Intents.intended(hasComponent(PaymentActivity::class.java.name))
        Intents.intended(hasExtra("order_id", "123"))
    }

    @Test
    fun stubbedActivityResultReturnsData() {
        val resultData = Intent().putExtra("payment_status", "success")
        Intents.intending(hasComponent(PaymentActivity::class.java.name))
            .respondWith(Instrumentation.ActivityResult(Activity.RESULT_OK, resultData))

        onView(withId(R.id.buy_button)).perform(click())

        onView(withId(R.id.status_text)).check(matches(withText("success")))
    }
}
```

| Method | Purpose |
|--------|---------|
| `Intents.init()` | Start recording intents (call in `@Before`) |
| `Intents.release()` | Stop recording (call in `@After`) |
| `Intents.intending(matcher)` | Stub an intent response |
| `Intents.intended(matcher)` | Verify an intent was sent |

## 7. Custom Matchers

### Text color matcher

```kotlin
fun withTextColor(color: Int): Matcher<View> {
    return object : BoundedMatcher<View, TextView>(TextView::class.java) {
        override fun matchesSafely(textView: TextView): Boolean {
            return textView.currentTextColor == color
        }
        override fun describeTo(description: Description) {
            description.appendText("TextView with text color: $color")
        }
    }
}

onView(withId(R.id.error_label)).check(matches(withTextColor(Color.RED)))
```

### Drawable matcher

```kotlin
fun withDrawable(resourceId: Int): Matcher<View> {
    return object : BoundedMatcher<View, ImageView>(ImageView::class.java) {
        override fun matchesSafly(imageView: ImageView): Boolean {
            return imageView.drawable != null &&
                imageView.drawable.constantState ==
                imageView.context.getDrawable(resourceId)?.constantState
        }
        override fun describeTo(description: Description) {
            description.appendText("ImageView with drawable resource: $resourceId")
        }
    }
}
```

### Error text matcher

```kotlin
fun hasErrorText(expected: String): Matcher<View> {
    return object : BoundedMatcher<View, TextInputLayout>(TextInputLayout::class.java) {
        override fun matchesSafely(view: TextInputLayout): Boolean {
            return view.error?.toString() == expected
        }
        override fun describeTo(description: Description) {
            description.appendText("TextInputLayout with error: $expected")
        }
    }
}

onView(withId(R.id.email_input)).check(matches(hasErrorText("Invalid email")))
```

## 8. IdlingResource

```kotlin
import androidx.test.espresso.IdlingRegistry
import androidx.test.espresso.idling.CountingIdlingResource

object EspressoIdlingResource {
    private const val RESOURCE = "GLOBAL"
    val countingIdlingResource = CountingIdlingResource(RESOURCE)

    fun increment() = countingIdlingResource.increment()
    fun decrement() = countingIdlingResource.decrement()
}

// In production code
class OrderRepository {
    fun fetchOrders() {
        EspressoIdlingResource.increment()
        api.getOrders { result ->
            EspressoIdlingResource.decrement()
            handleResult(result)
        }
    }
}

// In test
@Before
fun registerIdlingResource() {
    IdlingRegistry.getInstance().register(EspressoIdlingResource.countingIdlingResource)
}

@After
fun unregisterIdlingResource() {
    IdlingRegistry.getInstance().unregister(EspressoIdlingResource.countingIdlingResource)
}
```

### OkHttp3 IdlingResource

```kotlin
dependencies {
    androidTestImplementation("com.jakewharton.espresso:okhttp3-idling-resource:1.0.0")
}

val okHttpIdlingResource = OkHttp3IdlingResource.create("okhttp", okHttpClient)
IdlingRegistry.getInstance().register(okHttpIdlingResource)
```

## 9. Robot Pattern

### LoginRobot

```kotlin
class LoginRobot {

    fun typeEmail(email: String) = apply {
        onView(withId(R.id.email_field)).perform(clearText(), typeText(email))
    }

    fun typePassword(password: String) = apply {
        onView(withId(R.id.password_field)).perform(clearText(), typeText(password))
        onView(isRoot()).perform(closeSoftKeyboard())
    }

    fun clickLogin() = apply {
        onView(withId(R.id.login_button)).perform(click())
    }

    infix fun verify(block: LoginVerification.() -> Unit) =
        LoginVerification().apply(block)
}

class LoginVerification {

    fun isSuccessDisplayed() {
        onView(withId(R.id.home_container)).check(matches(isDisplayed()))
    }

    fun isErrorDisplayed(message: String) {
        onView(withId(R.id.error_label)).check(matches(withText(message)))
    }

    fun isLoginButtonDisabled() {
        onView(withId(R.id.login_button)).check(matches(not(isEnabled())))
    }
}
```

### Test usage

```kotlin
@Test
fun successfulLogin() {
    loginRobot {
        typeEmail("user@example.com")
        typePassword("correct_password")
        clickLogin()
    } verify {
        isSuccessDisplayed()
    }
}

@Test
fun invalidEmailShowsError() {
    loginRobot {
        typeEmail("invalid")
        typePassword("password")
        clickLogin()
    } verify {
        isErrorDisplayed("Invalid email address")
        isLoginButtonDisabled()
    }
}

fun loginRobot(block: LoginRobot.() -> Unit) = LoginRobot().apply(block)
```

## 10. Test Rules

```kotlin
@get:Rule
val activityRule = ActivityScenarioRule(MainActivity::class.java)

@get:Rule
val grantPermissionRule = GrantPermissionRule.grant(
    android.Manifest.permission.CAMERA,
    android.Manifest.permission.ACCESS_FINE_LOCATION
)

class DisableAnimationsRule : TestRule {
    override fun apply(base: Statement, description: Description): Statement {
        return object : Statement() {
            override fun evaluate() {
                val animScale = Settings.Global.getFloat(
                    InstrumentationRegistry.getInstrumentation().targetContext.contentResolver,
                    Settings.Global.WINDOW_ANIMATION_SCALE, 1.0f
                )
                if (animScale != 0f) {
                    UiAutomatorHelper.setAnimationScale(0f)
                }
                try {
                    base.evaluate()
                } finally {
                    if (animScale != 0f) {
                        UiAutomatorHelper.setAnimationScale(animScale)
                    }
                }
            }
        }
    }
}

@get:Rule
val disableAnimations = DisableAnimationsRule()
```

## 11. Debugging

### Print view hierarchy

```kotlin
onView(isRoot()).perform(ViewActions.actionWithAssertions(
    object : ViewAction {
        override fun getConstraints() = any(View::class.java)
        override fun getDescription() = "Print view hierarchy"
        override fun perform(uiController: UiController, view: View) {
            Log.d("TEST_HIERARCHY", ViewHierarchyDumper.dump(view))
        }
    }
))
```

### Screenshot on failure

```kotlin
@get:Rule
val screenshotRule = ScreenshotRule()

class ScreenshotRule : TestWatcher() {
    override fun failed(e: Throwable?, description: Description) {
        val screenshot = InstrumentationRegistry.getInstrumentation()
            .uiAutomation.takeScreenshot()
        val file = File(
            InstrumentationRegistry.getInstrumentation()
                .targetContext.getExternalFilesDir(null),
            "${description.methodName}_failure.png"
        )
        screenshot.writeTo(file)
    }
}
```

## Cross References

- Related rules: `ui-test-robot-pattern`, `ui-test-idling-resource`, `ui-test-no-sleep`, `ui-test-intent-stubbing`, `ui-test-custom-matchers`, `ui-test-disable-animations`, `ui-test-recyclerview`, `ui-test-accessibility-identifiers`
- Related references: [`compose-testing.md`](compose-testing.md), [`instrumented-testing.md`](instrumented-testing.md), [`coverage.md`](coverage.md)

# JUnit Unit Testing for Android (4 & 5)

Expert guidance for writing unit tests with JUnit (4 and 5), MockK, coroutines-test, and Turbine in Android/Kotlin projects.

## 1. Setup Dependencies

### JUnit 4
```kotlin
dependencies {
    testImplementation("junit:junit:4.13.2")
    testImplementation("io.mockk:mockk:1.13.12")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.1")
    testImplementation("app.cash.turbine:turbine:1.1.0")
}
```

### JUnit 5 (Android)
Requires the `android-junit5` plugin.
```kotlin
dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter-api:5.11.0")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:5.11.0")
    testImplementation("org.junit.jupiter:junit-jupiter-params:5.11.0")
    testImplementation("io.mockk:mockk:1.13.12")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.1")
}
```

| Component | JUnit 4 | JUnit 5 |
|-----------|---------|---------|
| Test Annotation | `@Test (org.junit)` | `@Test (org.junit.jupiter.api)` |
| Before/After | `@Before`, `@After` | `@BeforeEach`, `@AfterEach` |
| BeforeAll/AfterAll | `@BeforeClass`, `@AfterClass` | `@BeforeAll`, `@AfterAll` |
| Ignore Test | `@Ignore` | `@Disabled` |
| Extensions/Rules | `@Rule`, `@ClassRule` | `@ExtendWith` |

## 2. Naming Convention

**Pattern:** `SHOULD [behavior] WHEN [action] GIVEN [precondition]`

```kotlin
@Test
fun `should return Success WHEN fetching valid user GIVEN repository has data`() {
}
```

## 3. Test Structure: GIVEN / WHEN / THEN

```kotlin
@Test
fun `should return Success WHEN login with valid credentials GIVEN user exists`() = runTest {
    // GIVEN
    val email = "test@example.com"
    val password = "secret123"
    val expectedUser = User(id = "1", email = email)
    coEvery { repository.login(email, password) } returns Result.success(expectedUser)

    // WHEN
    val result = loginUseCase(email, password)

    // THEN
    assertEquals(expectedUser, result.getOrNull())
    coVerify(exactly = 1) { repository.login(email, password) }
}
```

## 4. ViewModel Testing (JUnit 5)

In JUnit 5, you use `@ExtendWith` instead of `@Rule`.

```kotlin
@ExtendWith(MainDispatcherExtension::class)
class UserViewModelTest {

    private val getUserUseCase = mockk<GetUserInfoUseCase>()
    private lateinit var viewModel: UserViewModel

    @BeforeEach
    fun setUp() {
        viewModel = UserViewModel(getUserUseCase)
    }

    @Test
    fun `should update ui state to Success when use case returns user`() = runTest {
        val user = User(id = "1", name = "Türker")
        coEvery { getUserUseCase("1") } returns Result.success(user)

        viewModel.loadUser("1")
        advanceUntilIdle()

        assertEquals(UserUiState.Success(user), viewModel.uiState.value)
    }
}
```

### MainDispatcherExtension (JUnit 5)
```kotlin
@ExperimentalCoroutinesApi
class MainDispatcherExtension(
    private val testDispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : BeforeEachCallback, AfterEachCallback {
    override fun beforeEach(context: ExtensionContext?) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun afterEach(context: ExtensionContext?) {
        Dispatchers.resetMain()
    }
}
```

## 5. Parameterized Tests (JUnit 5)

JUnit 5 provides much cleaner parameterized tests.

```kotlin
@ParameterizedTest
@CsvSource(
    "user@example.com, true",
    "invalid, false",
    ", false",
    "a@b.c, true"
)
fun `should validate email correctly`(email: String, expected: Boolean) {
    assertEquals(expected, EmailValidator.isValid(email))
}

@ParameterizedTest
@ValueSource(strings = ["", " ", "   "])
fun `should return false for blank strings`(input: String) {
    assertFalse(EmailValidator.isValid(input))
}
```

## 6. MockK Best Practices

- **Clear Mocks:** Use `clearMocks(repo)` in `@BeforeEach` to prevent state leakage.
- **Strict Mocks:** Prefer strict mocks (default) to catch un-stubbed calls.
- **relaxed = true:** Use only for side-effect-only dependencies (e.g., Loggers).

## 7. Coroutine Testing Patterns

- **runTest:** Always use `runTest` for suspend functions.
- **advanceUntilIdle():** Use when you have `viewModelScope.launch` inside the function being tested.
- **Turbine:** Use for testing Flow/StateFlow emission sequences.

```kotlin
viewModel.uiState.test {
    viewModel.action()
    assertEquals(UiState.Loading, awaitItem())
    assertEquals(UiState.Success, awaitItem())
}
```

## 8. Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| `runBlocking` in tests | Doesn't support virtual time, slow | Use `runTest` |
| Hardcoded `Dispatchers.IO` | Untestable threading | Inject `DispatcherProvider` |
| Mocking data classes | Fragile, complex | Use real instances |
| Testing private logic | Couples to implementation | Test through public API |
| Shared mutable state | Flaky tests, execution order dependent | Reset state in `@BeforeEach` |

## Cross References

- Related rules: `test-given-when-then`, `test-junit5-android`, `ctest-runtest-for-suspend`, `ctest-turbine-for-flow`, `test-fresh-sut`, `test-no-sleep`
- Related references: [`kotest.md`](kotest.md), [`mocking.md`](mocking.md), [`flow-testing.md`](flow-testing.md)

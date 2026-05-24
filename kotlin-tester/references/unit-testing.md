# JUnit 4 Unit Testing for Android

Expert guidance for writing unit tests with JUnit 4, MockK, coroutines-test, and Turbine in Android/Kotlin projects.

## 1. Setup Dependencies

```kotlin
dependencies {
    testImplementation("junit:junit:4.13.2")
    testImplementation("io.mockk:mockk:1.13.12")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.1")
    testImplementation("app.cash.turbine:turbine:1.1.0")
    testImplementation("com.google.truth:truth:1.4.2")
}
```

| Library | Purpose |
|---------|---------|
| JUnit 4 | Test framework, assertions, runners |
| MockK | Kotlin-native mocking (mockk, every, verify) |
| coroutines-test | TestDispatcher, advanceUntilIdle, runTest |
| Turbine | Flow / StateFlow testing DSL |
| Truth | Readable assertions (assertThat) |

## 2. Naming Convention

**Pattern:** `SHOULD [behavior] WHEN [action] GIVEN [precondition]`

```kotlin
@Test
fun shouldReturnSuccess WHEN fetching valid user GIVEN repository has data() {
}

@Test
fun shouldThrowException WHEN saving duplicate email GIVEN email already exists() {
}

@Test
fun shouldEmitLoadingState WHEN refreshing data GIVEN initial state is idle() {
}
```

| Naming Style | Example | Use When |
|-------------|---------|----------|
| Full template | `shouldReturnUser WHEN login succeeds GIVEN valid credentials` | Standard tests |
| Short form | `shouldReturnSuccess WHEN valid input` | Simple scenarios |
| Edge case | `shouldThrowError WHEN email is blank GIVEN empty form` | Error paths |

## 3. Test Structure: GIVEN / WHEN / THEN

```kotlin
@Test
fun shouldReturnSuccess WHEN login with valid credentials GIVEN user exists() = runTest {
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

Use `// GIVEN`, `// WHEN`, `// THEN` comments to separate test phases clearly.

## 4. UseCase Tests

```kotlin
class GetUserInfoUseCaseTest {

    private val repository = mockk<UserRepository>()
    private val useCase = GetUserInfoUseCase(repository)

    @Test
    fun `should return user when repository succeeds`() = runTest {
        val user = User(id = "1", name = "Türker", email = "turker@example.com")
        coEvery { repository.getUser("1") } returns Result.success(user)

        val result = useCase("1")

        assertTrue(result.isSuccess)
        assertEquals(user, result.getOrNull())
    }

    @Test
    fun `should return failure when repository throws`() = runTest {
        coEvery { repository.getUser("99") } returns Result.failure(UserNotFoundException())

        val result = useCase("99")

        assertTrue(result.isFailure)
        assertThat(result.exceptionOrNull()).isInstanceOf(UserNotFoundException::class.java)
    }

    @Test
    fun `should not call repository when id is blank`() = runTest {
        val result = useCase("")

        assertTrue(result.isFailure)
        coVerify(exactly = 0) { repository.getUser(any()) }
    }
}
```

Key patterns:
- Mock the repository with `mockk<UserRepository>()`.
- Stub with `coEvery { ... } returns Result.success(...)` or `Result.failure(...)`.
- Assert with `assertEquals`, `assertTrue`, or Truth's `assertThat`.
- Verify calls with `coVerify`.

## 5. ViewModel Tests

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val getUserUseCase = mockk<GetUserInfoUseCase>()
    private val viewModel = UserViewModel(getUserUseCase)

    @Test
    fun `should update ui state to Success when use case returns user`() = runTest {
        val user = User(id = "1", name = "Türker")
        coEvery { getUserUseCase("1") } returns Result.success(user)

        viewModel.loadUser("1")
        advanceUntilIdle()

        assertEquals(UserUiState.Success(user), viewModel.uiState.value)
    }

    @Test
    fun `should update ui state to Error when use case fails`() = runTest {
        coEvery { getUserUseCase("1") } returns Result.failure(Exception("Not found"))

        viewModel.loadUser("1")
        advanceUntilIdle()

        assertThat(viewModel.uiState.value).isInstanceOf(UserUiState.Error::class.java)
    }

    @Test
    fun `should emit Loading then Success when loading user`() = runTest {
        val user = User(id = "1", name = "Türker")
        coEvery { getUserUseCase("1") } returns Result.success(user)

        viewModel.uiState.test {
            viewModel.loadUser("1")
            assertEquals(UserUiState.Loading, awaitItem())
            advanceUntilIdle()
            assertEquals(UserUiState.Success(user), awaitItem())
            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

Key patterns:
- Use `MainDispatcherRule` to replace `Dispatchers.Main` with a test dispatcher.
- Call `advanceUntilIdle()` after triggering actions to let coroutines complete.
- Assert on `viewModel.uiState.value` for final state, or use Turbine `.test {}` for emission sequences.

## 6. MainDispatcherRule

### Version A: UnconfinedTestDispatcher (eager execution)

```kotlin
@ExperimentalCoroutinesApi
class MainDispatcherRule(
    private val testDispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description?) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description?) {
        Dispatchers.resetMain()
    }
}
```

### Version B: StandardTestDispatcher (controlled execution)

```kotlin
@ExperimentalCoroutinesApi
class MainDispatcherRule(
    private val testDispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {

    val testDispatcherProvider = object : DispatcherProvider {
        override val main: Dispatcher = testDispatcher
        override val io: Dispatcher = testDispatcher
        override val default: Dispatcher = testDispatcher
    }

    override fun starting(description: Description?) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description?) {
        Dispatchers.resetMain()
    }
}
```

| Dispatcher | Behavior | Use When |
|-----------|----------|----------|
| `UnconfinedTestDispatcher` | Executes eagerly, no need for `advanceUntilIdle` | Simple ViewModel tests, no timing assertions |
| `StandardTestDispatcher` | Requires `advanceUntilIdle()` to execute | Testing Loading states, timing, order of emissions |

## 7. Repository Tests

```kotlin
class UserRepositoryImplTest {

    private val localDataSource = mockk<UserLocalDataSource>()
    private val remoteDataSource = mockk<UserRemoteDataSource>()
    private val repository = UserRepositoryImpl(localDataSource, remoteDataSource)

    @Test
    fun `should return cached user from local data source`() = runTest {
        val user = UserEntity(id = "1", name = "Türker")
        coEvery { localDataSource.getUser("1") } returns user

        val result = repository.getUser("1")

        assertEquals("Türker", result.getOrNull()?.name)
        coVerify(exactly = 0) { remoteDataSource.getUser(any()) }
    }

    @Test
    fun `should fetch from remote and save locally when local is empty`() = runTest {
        val remoteUser = UserDto(id = "1", name = "Türker")
        coEvery { localDataSource.getUser("1") } returns null
        coEvery { remoteDataSource.getUser("1") } returns remoteUser
        coEvery { localDataSource.saveUser(any()) } just Runs

        val result = repository.getUser("1")

        assertEquals("Türker", result.getOrNull()?.name)
        coVerify(exactly = 1) { remoteDataSource.getUser("1") }
        coVerify(exactly = 1) { localDataSource.saveUser(any()) }
    }

    @Test
    fun `should not save locally when remote fetch fails`() = runTest {
        coEvery { localDataSource.getUser("1") } returns null
        coEvery { remoteDataSource.getUser("1") } throws HttpException(Response.error<Any>(404, "".toResponseBody()))

        val result = repository.getUser("1")

        assertTrue(result.isFailure)
        coVerify(exactly = 0) { localDataSource.saveUser(any()) }
    }
}
```

Key patterns:
- Mock both local and remote data sources.
- Use `coVerify(exactly = 0) { ... }` to assert something was NOT called.
- Test the cache/fallback strategy by controlling which data source returns data.

## 8. Parameterized Tests

```kotlin
@RunWith(Parameterized::class)
class EmailValidatorParameterizedTest(
    private val email: String,
    private val expected: Boolean
) {

    companion object {
        @JvmStatic
        @Parameterized.Parameters(name = "validate({0}) = {1}")
        fun data(): Collection<Array<Any?>> = listOf(
            arrayOf("user@example.com", true),
            arrayOf("invalid", false),
            arrayOf("", false),
            arrayOf("a@b.c", true),
            arrayOf("no-at-sign.com", false),
            arrayOf("@missing-local.com", false),
            arrayOf("missing-domain@", false),
            arrayOf("spaces in@email.com", false),
            arrayOf("UPPER@EXAMPLE.COM", true),
        )
    }

    @Test
    fun `should validate email correctly`() {
        assertEquals(expected, EmailValidator.isValid(email))
    }
}
```

| Component | Purpose |
|-----------|---------|
| `@RunWith(Parameterized::class)` | Enables parameterized execution |
| `@Parameterized.Parameters` | Provides test data as collection of arrays |
| Constructor parameters | Each array element maps to a constructor param |
| `name = "validate({0}) = {1}"` | Human-readable test case names |

## 9. Checklist: New Test Class

| Step | Action |
|------|--------|
| 1 | Create test class in matching `test/` package |
| 2 | Add `@get:Rule val mainDispatcherRule = MainDispatcherRule()` if testing coroutines |
| 3 | Declare mocks with `mockk<Type>()` |
| 4 | Instantiate system-under-test with mocked dependencies |
| 5 | Write test following GIVEN/WHEN/THEN structure |
| 6 | Use `coEvery` to stub dependencies, `coVerify` to confirm calls |
| 7 | Call `advanceUntilIdle()` if using `StandardTestDispatcher` |
| 8 | Assert results with `assertEquals`, `assertTrue`, or `assertThat` |
| 9 | Add `beforeTest { clearMocks() }` if mocks persist across tests |

## Cross References

- Related rules: `test-naming-convention`, `test-given-when-then`, `test-usecase-pattern`, `test-viewmodel-pattern`, `test-main-dispatcher`, `test-parameterized`, `test-no-mock-data-classes`, `ctest-turbine`, `ctest-advance-until-idle`
- Related references: [`mocking.md`](mocking.md), [`flow-testing.md`](flow-testing.md), [`tdd-workflow.md`](tdd-workflow.md), [`property-testing.md`](property-testing.md)

# MockK Reference for Kotlin Testing

Comprehensive reference for mocking with MockK in Kotlin/Android tests.

## 1. Mock Creation

```kotlin
val repository = mockk<UserRepository>()
val useCase = spyk(LoginUseCase(repository))
val relaxedMock = mockk<AnalyticsService>(relaxed = true)
```

| Function | Behavior | Use When |
|----------|----------|----------|
| `mockk<T>()` | Strict mock — every call must be stubbed | Most unit tests, ensures all interactions are explicit |
| `mockk<T>(relaxed = true)` | Returns default values without stubbing | Secondary dependencies you don't care about in this test |
| `spyk(obj)` | Wraps real object, allows overriding specific methods | Partial mocking, testing real + stubbed behavior |
| `mockkClass(cls)` | Create mock from class reference | Dynamic mock creation |

### Relaxing Specific Return Types

```kotlin
val repo = mockk<UserRepository>(relaxUnitFun = true)
val service = mockk<NetworkService>() {
    every { timeout } returns 30_000
}
```

| Relaxation Option | Effect |
|-------------------|--------|
| `relaxed = true` | All functions return defaults (0, false, null, empty list) |
| `relaxUnitFun = true` | Unit-returning functions do nothing (no stub needed) |
| `every { ... } returns ...` inside mockk {} | Inline stubbing during creation |

## 2. Stubbing

### Basic Stubbing

```kotlin
every { repository.getUserCount() } returns 42
every { repository.getName() } returns "Türker"
every { repository.isActive() } returns true
every { repository.getNullable() } returns null
every { repository.getUser(any()) } throws UserNotFoundException()
every { repository.delete(any()) } just Runs
```

### Answer-Based Stubbing

```kotlin
every { repository.getUser(capture(slot)) } answers {
    User(id = slot.captured, name = "User $slot.captured")
}

every { calculator.add(any(), any()) } answers {
    firstArg<Int>() + secondArg<Int>()
}

coEvery { repository.fetchData(any()) } coAnswers {
    delay(100)
    Result.success(data)
}
```

| Stubbing | Purpose | Example |
|----------|---------|---------|
| `returns` | Return a fixed value | `returns User(...)` |
| `throws` | Throw an exception | `throws IOException()` |
| `just Runs` | Void function — do nothing | `just Runs` |
| `answers { }` | Compute return value dynamically | `answers { firstArg<Int>() + 1 }` |
| `coAnswers { }` | Suspend version of answers | `coAnswers { delay(100); data }` |
| `returnsMany` | Return different values on each call | `returnsMany(1, 2, 3)` |

### Sequential Returns

```kotlin
every { repository.getStatus() } returnsMany listOf("loading", "success")
every { repository.poll() } returns "first" andThen "second" andThen "third"
every { repository.retry() } returns "ok" andThenThrows IOException()
```

## 3. Capturing Arguments

```kotlin
val userSlot = slot<User>()

every { repository.save(capture(userSlot)) } just Runs

repository.save(User(id = "1", name = "Türker"))

assertEquals("Türker", userSlot.captured.name)
assertEquals("1", userSlot.captured.id)
```

### Multiple Captures

```kotlin
val users = mutableListOf<User>()

every { repository.save(capture(users)) } just Runs

repository.save(User(id = "1", name = "First"))
repository.save(User(id = "2", name = "Second"))

assertEquals(2, users.size)
assertEquals("Second", users[1].name)
```

| Capture Type | Description |
|-------------|-------------|
| `slot<T>()` | Captures single argument into `captured` property |
| `mutableListOf<T>()` | Captures all invocations into a list |

## 4. Verification

```kotlin
coVerify { repository.getUser("1") }
coVerify(exactly = 1) { repository.getUser("1") }
coVerify(exactly = 0) { repository.delete(any()) }
coVerify(atLeast = 1) { repository.getUser(any()) }
coVerify(atMost = 3) { repository.refresh() }
coVerifyOrder {
    repository.begin()
    repository.save(any())
    repository.commit()
}
coVerifyAll {
    repository.getUser("1")
    repository.getUser("2")
}
verify { analytics.trackEvent("login_success") }
```

| Verification | Meaning |
|-------------|---------|
| `verify { ... }` | Call happened at least once |
| `verify(exactly = n)` | Call happened exactly n times |
| `verify(exactly = 0)` | Call did NOT happen |
| `verify(atLeast = n)` | Call happened n or more times |
| `verify(atMost = n)` | Call happened n or fewer times |
| `verifyOrder { }` | Calls happened in this order (others allowed) |
| `verifyAll { }` | These and only these calls happened |
| `coVerify { }` | Suspend function version of verify |
| `wasNot(called)` | Alternative syntax — mock was never called |

## 5. Argument Matchers

```kotlin
every { repository.getUser(any()) } returns user
every { repository.search(match { it.length > 3 }) } returns results
every { repository.save(any<User>()) } just Runs
every { repository.findById(ofType(String::class)) } returns user

val slot = slot<String>()
every { repository.log(capture(slot)) } just Runs
```

| Matcher | Description | Example |
|---------|-------------|---------|
| `any()` | Matches any non-null value | `any()`, `any<User>()` |
| `anyNullable()` | Matches any value including null | `anyNullable<String>()` |
| `match { }` | Custom predicate | `match { it.length > 3 }` |
| `capture(slot)` | Captures the argument | `capture(stringSlot)` |
| `ofType(Class)` | Matches by type | `ofType(String::class)` |
| `eq(value)` | Exact equality (explicit) | `eq("exact")` |
| `none()` | Matches nothing | Useful for exhaustive verification |
| `isNull()` | Matches null | `isNull()` |
| `isNotNull()` | Matches any non-null | `isNotNull()` |

**Important:** If you use a matcher for one argument, you must use matchers for ALL arguments in that call.

```kotlin
// Wrong — mixing literal and matcher
every { repository.search("query", any()) } returns results

// Correct — all matchers
every { repository.search(eq("query"), any()) } returns results
```

## 6. Coroutine Mocking

```kotlin
// Stubbing suspend functions
coEvery { repository.fetchData() } returns Result.success(data)
coEvery { repository.fetchData() } throws IOException("network error")
coEvery { repository.upload(any()) } coAnswers {
    delay(500)
    Result.success(Unit)
}

// Verifying suspend functions
coVerify(exactly = 1) { repository.fetchData() }
coVerify { repository.upload(any()) }

// Sequence of suspend calls
coEvery { repository.poll() } returns Result.success("first") andThen Result.success("second")
```

| Function | Use For |
|----------|---------|
| `coEvery { }` | Stubbing suspend functions |
| `coVerify { }` | Verifying suspend functions |
| `coAnswers { }` | Dynamic return value in suspend context |
| `coInvoke` | Invoke suspend lambda captures |

## 7. Spy and Partial Mocking

```kotlin
class Calculator {
    fun add(a: Int, b: Int): Int = a + b
    fun multiply(a: Int, b: Int): Int = a * b
    fun complexOperation(a: Int): Int = add(a, 10) * multiply(a, 2)
}

@Test
fun `should use real add but mock multiply`() {
    val calculator = spyk(Calculator())

    every { calculator.multiply(any(), any()) } returns 100

    val result = calculator.complexOperation(5)

    assertEquals(1500, result)
    verify(exactly = 1) { calculator.add(5, 10) }
    verify(exactly = 1) { calculator.multiply(5, 2) }
}
```

| Operation | Code | Effect |
|-----------|------|--------|
| Create spy | `spyk(realObject)` | Wraps real object |
| Override method | `every { spy.method() } returns X` | Uses mock return |
| Call real method | `every { spy.method() } answers { callOriginal() }` | Explicitly delegates |
| Partial override | Override only some methods | Un-overridden methods use real implementation |

## 8. Faking Flows

When mocking Flow-returning functions, use a `FakeRepository` pattern with `MutableStateFlow`:

```kotlin
class FakeUserRepository : UserRepository {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    private val _error = MutableStateFlow<Throwable?>(null)

    override fun getUsers(): Flow<List<User>> = _users
    override fun getError(): Flow<Throwable?> = _error

    fun emitUsers(users: List<User>) {
        _users.value = users
    }

    fun emitError(error: Throwable) {
        _error.value = error
    }
}

@Test
fun `should display users when repository emits data`() = runTest {
    val fakeRepo = FakeUserRepository()
    val viewModel = UserViewModel(fakeRepo)

    fakeRepo.emitUsers(listOf(User(id = "1", name = "Türker")))

    assertEquals(listOf(User(id = "1", name = "Türker")), viewModel.users.value)
}
```

Alternatively, mock the Flow directly:

```kotlin
@Test
fun `should handle flow emission with mockk`() = runTest {
    val repository = mockk<UserRepository>()
    val flow = flowOf(User(id = "1", name = "Türker"))
    every { repository.getUsers() } returns flow

    val result = repository.getUsers().first()

    assertEquals("Türker", result.name)
}
```

| Approach | Pros | Cons |
|----------|------|------|
| FakeRepository | Realistic, reusable, type-safe | More boilerplate |
| MockK flow stub | Quick, minimal code | Less realistic, harder for complex flows |

## 9. Cleanup

```kotlin
class MyTest {

    private val repository = mockk<UserRepository>()

    @Before
    fun setUp() {
        clearMocks(repository)
    }

    @After
    fun tearDown() {
        clearMocks(repository, answers = true, recordedCalls = true)
    }
}
```

Or use `@BeforeEach` / `@AfterEach` with JUnit 5. For JUnit 4, use `@Before` / `@After`.

| Cleanup Function | Effect |
|-----------------|--------|
| `clearMocks(mock)` | Resets stubs and recorded calls |
| `clearMocks(mock, answers = true)` | Resets stubs only |
| `clearMocks(mock, recordedCalls = true)` | Resets call records only |
| `mockk()` | Creates fresh mock in field initializer |

**Best practice:** Initialize mocks as fresh instances in the class body or call `clearMocks()` in `@Before` to prevent state leakage between tests.

## Cross References

- Related rules: `test-no-mock-data-classes`, `ctest-fake-over-mock-flow`, `test-given-when-then`, `ctest-turbine-for-flow`
- Related references: [`unit-testing.md`](unit-testing.md), [`flow-testing.md`](flow-testing.md)

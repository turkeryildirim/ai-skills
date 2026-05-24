# Flow and StateFlow Testing with Turbine

Expert guidance for testing Kotlin Flow, StateFlow, and SharedFlow using the Turbine library.

## 1. Setup and Basic Usage

```kotlin
dependencies {
    testImplementation("app.cash.turbine:turbine:1.1.0")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.1")
}
```

```kotlin
import app.cash.turbine.test
import kotlinx.coroutines.test.runTest

@Test
fun `should emit expected values`() = runTest {
    val flow = flowOf(1, 2, 3)

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}
```

| Turbine Method | Purpose |
|---------------|---------|
| `.test { }` | Subscribe to flow and collect emissions |
| `awaitItem()` | Suspend until next emission, return it |
| `awaitError()` | Suspend until error, return it |
| `awaitComplete()` | Suspend until flow completes |
| `expectNoEvents()` | Assert no emissions, errors, or completion |
| `cancelAndIgnoreRemainingEvents()` | Cancel and consume remaining events |
| `cancel()` | Cancel the flow collection |

## 2. Testing StateFlow Emissions

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelFlowTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val getUserUseCase = mockk<GetUserInfoUseCase>()
    private lateinit var viewModel: UserViewModel

    @Test
    fun `should emit Idle then Loading then Success when loading user`() = runTest {
        val user = User(id = "1", name = "Türker")
        coEvery { getUserUseCase("1") } returns Result.success(user)
        viewModel = UserViewModel(getUserUseCase)

        viewModel.uiState.test {
            assertEquals(UserUiState.Idle, awaitItem())

            viewModel.loadUser("1")
            assertEquals(UserUiState.Loading, awaitItem())

            advanceUntilIdle()
            assertEquals(UserUiState.Success(user), awaitItem())

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `should remain in Error state when use case fails`() = runTest {
        coEvery { getUserUseCase("99") } returns Result.failure(Exception("Not found"))
        viewModel = UserViewModel(getUserUseCase)

        viewModel.uiState.test {
            viewModel.loadUser("99")
            advanceUntilIdle()

            skipItems(1) // Skip initial Idle
            val state = awaitItem()
            assertThat(state).isInstanceOf(UserUiState.Error::class.java)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

StateFlow always emits an initial value. Account for it with `awaitItem()` at the start or use `skipItems(1)`.

## 3. Testing Side Effects (SharedFlow)

```kotlin
class NavigationViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val repository = mockk<OrderRepository>()
    private lateinit var viewModel: NavigationViewModel

    @Test
    fun `should navigate to confirmation when order succeeds`() = runTest {
        coEvery { repository.placeOrder(any()) } returns Result.success(orderId)
        viewModel = NavigationViewModel(repository)

        viewModel.navigationEvents.test {
            viewModel.placeOrder(order)

            val event = awaitItem()
            assertEquals(NavigationEvent.Confirmation(orderId), event)

            expectNoEvents()
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `should show error toast when order fails`() = runTest {
        coEvery { repository.placeOrder(any()) } returns Result.failure(Exception("Payment failed"))
        viewModel = NavigationViewModel(repository)

        viewModel.sideEffects.test {
            viewModel.placeOrder(order)

            val effect = awaitItem()
            assertEquals(SideEffect.ShowToast("Payment failed"), effect)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

SharedFlow has no initial value. The first `awaitItem()` returns the first emission.

## 4. Testing Search Debounce

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class SearchViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule(
        testDispatcher = StandardTestDispatcher()
    )

    private val searchUseCase = mockk<SearchUseCase>()
    private lateinit var viewModel: SearchViewModel

    @Test
    fun `should debounce search queries and emit results`() = runTest {
        val results = listOf(SearchResult(title = "Kotlin"))
        coEvery { searchUseCase("Kot") } returns emptyList()
        coEvery { searchUseCase("Kotlin") } returns results
        viewModel = SearchViewModel(searchUseCase)

        viewModel.searchResults.test {
            viewModel.onSearchQueryChanged("Kot")
            advanceTimeBy(200)
            viewModel.onSearchQueryChanged("Kotlin")
            advanceTimeBy(500)

            val finalResult = awaitItem()
            assertEquals(results, finalResult)

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `should not emit results for queries shorter than 3 characters`() = runTest {
        viewModel = SearchViewModel(searchUseCase)

        viewModel.searchResults.test {
            viewModel.onSearchQueryChanged("ab")
            advanceTimeBy(500)

            expectNoEvents()
            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

Use `StandardTestDispatcher` for debounce tests. `UnconfinedTestDispatcher` executes immediately, making debounce timing untestable.

## 5. Testing Flow with combine

```kotlin
@Test
fun `should combine user and settings flows`() = runTest {
    val userFlow = MutableStateFlow(User(name = "Türker"))
    val settingsFlow = MutableStateFlow(Settings(theme = Theme.DARK))

    combine(userFlow, settingsFlow) { user, settings ->
        ProfileUiState(user = user, settings = settings)
    }.test {
        val initial = awaitItem()
        assertEquals(Theme.DARK, initial.settings.theme)
        assertEquals("Türker", initial.user.name)

        settingsFlow.value = Settings(theme = Theme.LIGHT)
        val updated = awaitItem()
        assertEquals(Theme.LIGHT, updated.settings.theme)

        cancelAndIgnoreRemainingEvents()
    }
}
```

When any upstream Flow in `combine` emits, a new combined emission is produced.

## 6. Turbine Utility Methods

```kotlin
flow.test {
    // Skip N emissions
    skipItems(2)

    // Wait for specific condition
    val item = awaitItem()
    assertTrue(item.isSuccessful)

    // Assert no pending events
    expectNoEvents()

    // Cancel and consume all remaining (prevents "unread events" error)
    cancelAndIgnoreRemainingEvents()
}
```

| Method | When to Use |
|--------|-------------|
| `awaitItem()` | You expect the next emission |
| `awaitError()` | You expect the flow to throw |
| `awaitComplete()` | You expect the flow to finish |
| `expectNoEvents()` | Assert nothing happened after this point |
| `skipItems(n)` | Ignore intermediate emissions you don't care about |
| `cancelAndIgnoreRemainingEvents()` | End of test — clean up unconsumed events |
| `cancel()` | Cancel without consuming (may throw on uncollected events) |

## 7. FakeRepository Pattern with MutableStateFlow

```kotlin
class FakeOrderRepository : OrderRepository {
    private val _orders = MutableStateFlow<List<Order>>(emptyList())
    private val _isLoading = MutableStateFlow(false)

    override fun getOrders(): Flow<List<Order>> = _orders
    override fun isLoading(): Flow<Boolean> = _isLoading

    suspend fun emitOrders(orders: List<Order>) {
        _orders.emit(orders)
    }

    fun setLoading(loading: Boolean) {
        _isLoading.value = loading
    }
}

@Test
fun `should display orders when repository emits data`() = runTest {
    val fakeRepo = FakeOrderRepository()
    val viewModel = OrderViewModel(fakeRepo)

    viewModel.orders.test {
        fakeRepo.emitOrders(listOf(Order(id = "1", total = 99.0)))

        val orders = awaitItem()
        assertEquals(1, orders.size)
        assertEquals(99.0, orders[0].total)

        cancelAndIgnoreRemainingEvents()
    }
}
```

Prefer `FakeRepository` over `mockk` for Flow-returning interfaces. It provides realistic behavior and avoids complex mock stubbing.

## 8. Testing with TestDispatcher

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class FlowTimingTest {

    @Test
    fun `should emit values with controlled timing`() = runTest {
        val flow = flow {
            emit(1)
            delay(100)
            emit(2)
            delay(200)
            emit(3)
        }

        flow.test {
            assertEquals(1, awaitItem())

            // Advance virtual time using the TestScope receiver
            advanceTimeBy(50)
            expectNoEvents()

            advanceTimeBy(50)
            assertEquals(2, awaitItem())

            advanceTimeBy(200)
            assertEquals(3, awaitItem())

            awaitComplete()
        }
    }
}
```

| Dispatcher | Timing Behavior |
|-----------|----------------|
| `StandardTestDispatcher` | Virtual time, requires `advanceTimeBy()` / `advanceUntilIdle()` |
| `UnconfinedTestDispatcher` | Real-time-like, executes immediately |
| `runTest` | Provides its own `TestCoroutineScheduler` |

## 9. Common Mistakes

### Not Calling advanceUntilIdle

```kotlin
@Test
fun `should emit loading state`() = runTest {
    viewModel.uiState.test {
        viewModel.loadData()
        // WRONG: nothing happens without advancing
        // assertEquals(UserUiState.Loading, awaitItem())

        advanceUntilIdle()
        assertEquals(UserUiState.Success(data), awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

### Not Cancelling Turbine

```kotlin
flow.test {
    assertEquals(1, awaitItem())
    // WRONG: test ends with unconsumed events → Turbine throws
    // Must call cancelAndIgnoreRemainingEvents()
    cancelAndIgnoreRemainingEvents()
}
```

### Ignoring Initial StateFlow Value

```kotlin
@Test
fun `should handle initial state`() = runTest {
    viewModel.state.test {
        // StateFlow always emits initial value
        val initial = awaitItem()
        assertEquals(UiState.Idle, initial)

        viewModel.action()
        cancelAndIgnoreRemainingEvents()
    }
}
```

### Using UnconfinedTestDispatcher for Timing Tests

```kotlin
// WRONG: UnconfinedTestDispatcher executes immediately — delay/debounce tests are meaningless
@get:Rule
val rule = MainDispatcherRule(UnconfinedTestDispatcher())

// CORRECT: Use StandardTestDispatcher when testing debounce or delay
@get:Rule
val rule = MainDispatcherRule(StandardTestDispatcher())
```

| Mistake | Fix |
|---------|-----|
| Missing `advanceUntilIdle()` | Call after triggering coroutine actions |
| Not cancelling Turbine | Always call `cancelAndIgnoreRemainingEvents()` at test end |
| Ignoring initial StateFlow value | `awaitItem()` first, then trigger action |
| Wrong dispatcher for timing | Use `StandardTestDispatcher` for debounce/delay tests |
| Not wrapping in `runTest` | Always use `runTest { }` for coroutine tests |

## Cross References

- Related rules: `ctest-runtest-for-suspend`, `ctest-advance-until-idle`, `ctest-turbine-for-flow`, `ctest-fake-over-mock-flow`, `ctest-test-dispatcher`
- Related references: [`unit-testing.md`](unit-testing.md), [`mocking.md`](mocking.md)

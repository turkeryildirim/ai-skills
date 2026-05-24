# Kotlin Coroutines and Flow

Expert guidance for structured concurrency, Flow, and reactive patterns in Kotlin (Coroutines 1.8+ / Kotlin 2.x).

## 1. Structured Concurrency

### Core Principle
Every coroutine has a parent. When the parent cancels, all children cancel. This prevents leaked coroutines.

### Scope Hierarchy

```
Application Scope
  └── viewModelScope
        ├── LaunchedEffect (Compose)
        ├── coroutineScope { }
        │     ├── async { }
        │     └── launch { }
        └── supervisorScope { }
              ├── launch { }
              └── launch { }
  └── lifecycleScope (Activity/Fragment)
        ├── lifecycleScope.launchWhenStarted
        └── repeatOnLifecycle(STARTED)
```

### Scope Sources

| Scope | Lifecycle Owner | Use Case |
|-------|----------------|----------|
| `viewModelScope` | ViewModel | ViewModel-driven work |
| `lifecycleScope` | Activity/Fragment | Lifecycle-bound work |
| `LaunchedEffect(key)` | Composable | UI-triggered side effects in Compose |
| `rememberCoroutineScope()` | Composable | User event handling in Compose |
| `CoroutineScope(SupervisorJob())` | Manual (DI) | Long-lived services |
| `GlobalScope` | Application | **Avoid** unless truly app-scoped |

### coroutineScope for Structured Parallelism
```kotlin
suspend fun fetchDashboard(): Dashboard = coroutineScope {
    val user = async { userRepo.getUser() }
    val feed = async { feedRepo.getFeed() }
    val notifications = async { notificationRepo.getNotifications() }
    Dashboard(
        user = user.await(),
        feed = feed.await(),
        notifications = notifications.await()
    )
}
```

If any child fails, all siblings are cancelled.

## 2. Dispatchers

| Dispatcher | Use For | Thread Pool |
|-----------|---------|-------------|
| `Dispatchers.Main` | UI updates, Compose recomposition | Main thread |
| `Dispatchers.IO` | Network, database, file I/O | Shared IO pool (64+ threads) |
| `Dispatchers.Default` | CPU-bound work (sorting, parsing, math) | Shared worker pool (core count) |
| `Dispatchers.Unconfined` | Testing only (immediate execution) | Inherit caller thread |

### Inject Dispatchers — Never Hardcode

```kotlin
interface DispatcherProvider {
    val io: CoroutineDispatcher
    val main: CoroutineDispatcher
    val default: CoroutineDispatcher
}

class DefaultDispatcherProvider : DispatcherProvider {
    override val io = Dispatchers.IO
    override val main = Dispatchers.Main
    override val default = Dispatchers.Default
}
```

```kotlin
class UserRepository(
    private val api: UserApi,
    private val dispatchers: DispatcherProvider
) {
    suspend fun fetchUsers(): List<User> = withContext(dispatchers.io) {
        api.getUsers()
    }
}
```

### KMP Dispatcher Notes

| Platform | `Dispatchers.IO` | `Dispatchers.Main` | `Dispatchers.Default` |
|----------|-------------------|--------------------|-----------------------|
| JVM/Android | Available | Available | Available |
| iOS (native) | **Not available** | Main thread | Available |
| JS/WASM | **Not available** | Available | Available |
| Native (desktop) | **Not available** | Available | Available |

For KMP, define your own dispatcher abstraction (as above) and map to platform-specific dispatchers in each module.

## 3. SupervisorJob

Use `SupervisorJob` when child failures should NOT cancel siblings.

```kotlin
val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

scope.launch {
    uploadImage(image1)
}

scope.launch {
    uploadImage(image2)
}
```

If `image1` upload fails, `image2` continues.

Inside `coroutineScope`, use `supervisorScope` for the same behavior:

```kotlin
suspend fun syncAll() = supervisorScope {
    launch { syncContacts() }
    launch { syncCalendar() }
    launch { syncMessages() }
}
```

## 4. async / await for Parallel Work

```kotlin
suspend fun loadProfile(id: String): Profile = coroutineScope {
    val userDeferred = async { userService.getUser(id) }
    val postsDeferred = async { postService.getPosts(id) }
    val statsDeferred = async { statsService.getStats(id) }

    Profile(
        user = userDeferred.await(),
        posts = postsDeferred.await(),
        stats = statsDeferred.await()
    )
}
```

Rules:
- Always use inside `coroutineScope` or `supervisorScope`
- Never use `async` when sequential execution is sufficient
- Call `await()` only once per deferred; it is idempotent but signals intent

## 5. Flow

### Cold vs Hot Flows

| Property | Cold Flow | Hot Flow (StateFlow/SharedFlow) |
|----------|-----------|----------------------------------|
| Activation | Starts on collection | Active regardless of collectors |
| Emission | Per collector | Shared across collectors |
| Replay | None (by default) | Configurable (StateFlow: 1, SharedFlow: 0+) |
| Resources | Released on cancel | Managed by scope lifecycle |
| Analogy | Like a video stream | Like a radio broadcast |

### Common Operators

| Operator | Purpose | Example |
|----------|---------|---------|
| `map` | Transform emitted values | `.map { it.toDomain() }` |
| `filter` | Keep matching emissions | `.filter { it.isActive }` |
| `flatMapLatest` | Switch to newest source, cancel previous | Search-as-you-type |
| `flatMapMerge` | Collect multiple in parallel | Fetch details for each item |
| `flatMapConcat` | Collect sequentially | Ordered sequential processing |
| `debounce` | Wait for silence before emitting | `.debounce(300.milliseconds)` |
| `retryWhen` | Conditional retry | Retry on network errors only |
| `combine` | Merge latest from multiple flows | Combine user + settings |
| `zip` | Pair emissions from two flows | Pair request + response |
| `distinctUntilChanged` | Ignore consecutive duplicates | Prevent redundant UI updates |
| `onEach` | Side effect per emission | Logging |
| `catch` | Handle upstream errors | `.catch { emit(emptyList()) }` |
| `flowOn` | Change dispatcher upstream | `.flowOn(Dispatchers.IO)` |

### flatMapLatest vs flatMapMerge vs flatMapConcat

| Operator | Cancels Previous? | Concurrency | Use Case |
|----------|-------------------|-------------|----------|
| `flatMapLatest` | Yes | 1 (latest only) | Search, real-time filters, switchMap equivalent |
| `flatMapMerge` | No | N (configurable concurrency) | Parallel API calls, fan-out |
| `flatMapConcat` | No | 1 (sequential) | Ordered processing, queue-like behavior |

```kotlin
val searchResults = searchQuery
    .debounce(300.milliseconds)
    .distinctUntilChanged()
    .flatMapLatest { query ->
        searchRepository.search(query)
    }
    .flowOn(Dispatchers.IO)
```

## 6. StateFlow

StateFlow is the preferred hot state holder for ViewModels.

```kotlin
class UsersViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UsersUiState>(UsersUiState.Loading)
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            repository.observeUsers()
                .catch { _uiState.value = UsersUiState.Error(it.message) }
                .collect { users ->
                    _uiState.value = UsersUiState.Success(users)
                }
        }
    }
}
```

### Updating StateFlow
```kotlin
_uiState.update { current ->
    current.copy(users = newUsers)
}
```

### stateIn Operator

Convert a cold Flow to a StateFlow with SharingStarted strategy:

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `SharingStarted.Eagerly` | Starts immediately, never stops | Critical data |
| `SharingStarted.Lazily` | Starts on first subscriber, never stops | One-time load |
| `SharingStarted.WhileSubscribed(5000)` | Starts on first subscriber, stops 5s after last leaves | UI-bound data (recommended) |

```kotlin
val uiState: StateFlow<UsersUiState> = repository.observeUsers()
    .map { UsersUiState.Success(it) }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = UsersUiState.Loading
    )
```

`WhileSubscribed(5000)` keeps the upstream alive for 5 seconds after the last collector disappears, preventing restarts during configuration changes.

## 7. SharedFlow

SharedFlow is for one-time events (navigation, snackbar, toasts).

### Sealed Effect Pattern
```kotlin
sealed interface UsersEffect {
    data class ShowSnackbar(val message: String) : UsersEffect
    data class NavigateToDetail(val userId: String) : UsersEffect
}

class UsersViewModel : ViewModel() {
    private val _effect = MutableSharedFlow<UsersEffect>()
    val effect: SharedFlow<UsersEffect> = _effect.asSharedFlow()

    fun onUserClicked(userId: String) {
        viewModelScope.launch {
            _effect.emit(UsersEffect.NavigateToDetail(userId))
        }
    }
}
```

### Collecting Effects in Compose
```kotlin
LaunchedEffect(Unit) {
    viewModel.effect.collect { effect ->
        when (effect) {
            is UsersEffect.ShowSnackbar -> snackbarHostState.showSnackbar(effect.message)
            is UsersEffect.NavigateToDetail -> navController.navigate("users/${effect.userId}")
        }
    }
}
```

### Channel as Alternative
Use `Channel` when you need guaranteed delivery (buffer = 1) and backpressure handling:

```kotlin
val events = Channel<UiEvent>()
viewModelScope.launch { events.send(UiEvent.RefreshComplete) }
```

## 8. Error Handling

### Result<T> Pattern (Preferred)
```kotlin
sealed interface Try<out T> {
    data class Success<out T>(val value: T) : Try<T>
    data class Failure(val error: AppError) : Try<Nothing>
}

suspend fun fetchUser(id: String): Try<User> = try {
    val user = api.getUser(id)
    Try.Success(user)
} catch (e: IOException) {
    Try.Failure(AppError.Network(e.message))
}
```

### CancellationException MUST Be Rethrown

```kotlin
suspend fun process(data: String) {
    try {
        performWork(data)
    } catch (e: CancellationException) {
        throw e
    } catch (e: IOException) {
        handleError(e)
    }
}
```

Never catch `CancellationException` without rethrowing. It breaks structured concurrency.

### flow.catch for Reactive Error Handling
```kotlin
repository.observeUsers()
    .catch { e ->
        when (e) {
            is IOException -> emit(emptyList())
            is HttpException -> throw UserException.ServerError(e.code())
            else -> throw e
        }
    }
    .collect { users -> render(users) }
```

### No Exception Flow Control
| Avoid | Instead |
|-------|---------|
| `try/catch` for expected conditions | `Result` / `Try` sealed type |
| Swallowing exceptions silently | Log + propagate or emit error state |
| Catching `CancellationException` | Always rethrow |
| `CoroutineExceptionHandler` for business errors | `try/catch` inside coroutine or `flow.catch` |

## 9. Lifecycle-Safe Collection

### In Fragments/Activities
```kotlin
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    viewLifecycleOwner.lifecycleScope.launch {
        viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
            viewModel.uiState.collect { state ->
                render(state)
            }
        }
    }
}
```

### In Compose
```kotlin
@Composable
fun UsersScreen(viewModel: UsersViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    UsersContent(uiState = uiState)
}
```

`collectAsStateWithLifecycle` automatically uses `repeatOnLifecycle(STARTED)` under the hood.

| Method | Safe? | Use In |
|--------|-------|--------|
| `collectAsStateWithLifecycle()` | Yes | Compose UI |
| `repeatOnLifecycle(STARTED) { collect }` | Yes | Fragment/Activity |
| `collectAsState()` | No (no lifecycle awareness) | Avoid for UI state |
| `launchWhenStarted` | Deprecated | Use `repeatOnLifecycle` |

## 10. Cooperative Cancellation

### ensureActive / yield
```kotlin
suspend fun processItems(items: List<Item>): List<Result> {
    return items.mapIndexed { index, item ->
        ensureActive()
        process(item)
    }
}
```

### try/finally with NonCancellable
```kotlin
suspend fun transfer(amount: Double) {
    try {
        deduct(amount)
        send(amount)
    } finally {
        withContext(NonCancellable) {
            logTransaction(amount)
        }
    }
}
```

Use `NonCancellable` only in `finally` blocks for cleanup. Never use it for regular work.

## 11. Callback Conversion

### callbackFlow
```kotlin
fun FirebaseUser.observeAuthState(): Flow<User?> = callbackFlow {
    val authStateListener = FirebaseAuth.AuthStateListener { auth ->
        trySend(auth.currentUser?.toDomainUser())
    }
    FirebaseAuth.getInstance().addAuthStateListener(authStateListener)

    awaitClose {
        FirebaseAuth.getInstance().removeAuthStateListener(authStateListener)
    }
}
```

Key rules:
- Always call `awaitClose` to clean up resources
- Use `trySend` (non-suspending) not `send` inside callbacks
- The flow is cold: starts on collection, stops on cancellation
- Wrap in `.flowOn(Dispatchers.IO)` if callbacks come from IO threads

### awaitClose Example with Sensors
```kotlin
fun Context.accelerometerFlow(): Flow<Triple<Float, Float, Float>> = callbackFlow {
    val sensorManager = getSystemService<SensorManager>()!!
    val accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)

    val listener = object : SensorEventListener {
        override fun onSensorChanged(event: SensorEvent) {
            trySend(Triple(event.values[0], event.values[1], event.values[2]))
        }
        override fun onAccuracyChanged(sensor: Sensor, accuracy: Int) {}
    }

    sensorManager.registerListener(listener, accelerometer, SensorManager.SENSOR_DELAY_UI)

    awaitClose { sensorManager.unregisterListener(listener) }
}.flowOn(Dispatchers.IO)
```

## 12. Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Launching in `GlobalScope` | Work continues after screen close | Use `viewModelScope` or `lifecycleScope` |
| Not rethrowing `CancellationException` | Coroutines never cancel | Always `throw e` in catch |
| Collecting in `onCreate` without lifecycle | Crashes after onDestroy | Use `repeatOnLifecycle` |
| Using `Dispatchers.IO` for CPU work | Thread starvation | Use `Dispatchers.Default` |
| Blocking inside suspend function | UI freezes, ANR | Use `withContext(Dispatchers.IO)` |
| SharedFlow with no replay lost events | Events dropped | Use `Channel` or ensure collector started |
| StateFlow initial value shown briefly | Flash of loading state | Use `stateIn` with proper initial or `SharingStarted.WhileSubscribed` |
| `flowOn` placed after `collect` | Wrong thread | Place `flowOn` before terminal operator |
| Nested `withContext` calls | Unnecessary context switch | Use single `withContext` at boundary |
| Using `async` without `await` | Fire-and-forget silently fails | Use `launch` for fire-and-forget, `async` only with `await` |
| MutableStateFlow.value in concurrent code | Race conditions | Use `MutableStateFlow.update {}` |
| Blocking queue operations in Flow | ANR, deadlock | Use `callbackFlow` or `channelFlow` |

## Cross References

- Related rules: `coro-structured-concurrency`, `coro-dispatcher-injection`, `coro-no-global-scope`, `coro-rethrow-cancellation`, `coro-lifecycle-collection`, `coro-stateflow-pattern`, `coro-sharedflow-events`, `coro-cooperative-cancellation`, `coro-callback-flow`, `coro-no-blocking`
- Related references: [`kotlin-conventions.md`](kotlin-conventions.md), [`architecture.md`](architecture.md), [`compose-ui.md`](compose-ui.md)

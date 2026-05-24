# Jetpack Compose UI Patterns

Expert guidance for building testable, performant, and well-structured Compose UI following modern best practices (Compose 1.7+ / Material 3).

## 1. Screen with ViewModel Pattern

```kotlin
@Composable
fun UsersScreen(
    viewModel: UsersViewModel = hiltViewModel(),
    onUserClick: (String) -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        viewModel.effect.collect { effect ->
            when (effect) {
                is UsersEffect.NavigateToDetail -> onUserClick(effect.userId)
                is UsersEffect.ShowSnackbar -> snackbarHostState.showSnackbar(effect.message)
            }
        }
    }

    UsersContent(
        uiState = uiState,
        onEvent = viewModel::onEvent,
        onUserClick = onUserClick
    )
}
```

### Pattern Rules
- `hiltViewModel()` provides the ViewModel via Hilt DI
- `collectAsStateWithLifecycle()` ensures lifecycle-safe collection
- Screen delegates to a stateless `*Content` composable
- Events flow up via lambdas, state flows down via parameters
- Effects are collected in `LaunchedEffect` at the screen level

## 2. State Management

### State Ownership Table

| State Owner | Mechanism | Scope | Use Case |
|-------------|-----------|-------|----------|
| ViewModel | `StateFlow` / `MutableStateFlow` | Screen lifecycle | Business state, fetched data |
| Composable | `remember` + `mutableStateOf` | Composition lifecycle | UI-only state (scroll, animation) |
| Composable | `rememberSaveable` | Configuration change survive | Form inputs, toggle state |
| Composable | `derivedStateOf` | Recomposition | Computed from other state |
| ViewModel | `SavedStateHandle` | Process death survive | Critical state to persist |

### ViewModel StateFlow (Primary Pattern)
```kotlin
class UsersViewModel(
    private val observeUsers: ObserveUsersUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<UsersUiState>(UsersUiState.Loading)
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            observeUsers()
                .catch { _uiState.value = UsersUiState.Error(it.message) }
                .collect { users ->
                    _uiState.update { UsersUiState.Success(users) }
                }
        }
    }
}
```

### remember for Local UI State
```kotlin
@Composable
fun CollapsibleSection(title: String, content: String) {
    var isExpanded by remember { mutableStateOf(false) }

    Column {
        Text(
            text = title,
            modifier = Modifier.clickable { isExpanded = !isExpanded }
        )
        if (isExpanded) {
            Text(text = content)
        }
    }
}
```

### derivedStateOf for Computed State
```kotlin
@Composable
fun UserList(users: List<User>) {
    val hasUnread by remember {
        derivedStateOf { users.any { it.hasUnreadMessages } }
    }

    BadgedBox(badge = { if (hasUnread) Badge() }) {
        Icon(Icons.Default.Mail, contentDescription = "Messages")
    }
}
```

`derivedStateOf` prevents unnecessary recompositions by only reading the derived value when dependencies change.

## 3. Compose Context Rules

### LaunchedEffect for Async Work
```kotlin
LaunchedEffect(userId) {
    viewModel.loadUser(userId)
}
```

- Key changes restart the effect
- Cancelled automatically when composable leaves composition
- NEVER call suspend functions directly in composable body

### Never Call Suspend in Body
```kotlin
// BAD - launches coroutine on every recomposition
@Composable
fun BadScreen(viewModel: MyViewModel) {
    viewModel.fetchData() // suspend function!
}

// GOOD - scoped to composition
@Composable
fun GoodScreen(viewModel: MyViewModel) {
    LaunchedEffect(Unit) {
        viewModel.fetchData()
    }
}
```

### rememberUpdatedState for Stale Closure Prevention
```kotlin
@Composable
fun TimerScreen(onTimeout: () -> Unit) {
    val currentOnTimeout by rememberUpdatedState(onTimeout)

    LaunchedEffect(Unit) {
        delay(5000)
        currentOnTimeout()
    }
}
```

Use `rememberUpdatedState` when a LaunchedEffect should not restart but needs the latest callback reference.

## 4. Composable Structure

### Extract Subcomponents
```kotlin
@Composable
fun UsersContent(
    uiState: UsersUiState,
    onEvent: (UsersEvent) -> Unit,
    onUserClick: (String) -> Unit
) {
    when (uiState) {
        UsersUiState.Loading -> LoadingIndicator()
        is UsersUiState.Success -> UserList(
            users = uiState.users,
            onUserClick = onUserClick
        )
        is UsersUiState.Error -> ErrorMessage(
            message = uiState.message,
            onRetry = { onEvent(UsersEvent.Retry) }
        )
    }
}

@Composable
private fun UserList(
    users: List<UserUiModel>,
    onUserClick: (String) -> Unit
) {
    LazyColumn {
        items(users, key = { it.id }) { user ->
            UserRow(user = user, onClick = { onUserClick(user.id) })
        }
    }
}
```

### Pass Only Needed Data
```kotlin
// BAD - passes entire ViewModel
@Composable
fun UserRow(viewModel: UsersViewModel) { ... }

// GOOD - passes only what's needed
@Composable
fun UserRow(user: UserUiModel, onClick: () -> Unit) { ... }
```

### Stateless Composables
Prefer stateless composables that receive data and callbacks. State lives in ViewModel or the nearest common ancestor.

## 5. Navigation in Compose

### NavHost Setup (in :app module)
```kotlin
@Composable
fun AppNavHost(navController: NavHostController) {
    NavHost(navController = navController, startDestination = "users") {
        composable("users") {
            UsersScreen(
                onUserClick = { userId ->
                    navController.navigate("users/$userId")
                }
            )
        }
        composable(
            "users/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.StringType })
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: return@composable
            UserDetailScreen(userId = userId)
        }
    }
}
```

### Route Constants
```kotlin
object Routes {
    const val USERS = "users"
    const val USER_DETAIL = "users/{userId}"

    fun userDetail(userId: String) = "users/$userId"
}
```

### Testing Navigation
```kotlin
@Test
fun navigatingToUser_showsDetailScreen() {
    val navController = TestNavHostController(context)
    navController.setGraph(R.navigation.nav_graph)

    composeTestRule.setContent {
        AppNavHost(navController = navController)
    }

    composeTestRule
        .onNodeWithTag("user_row_123")
        .performClick()

    assertEquals(Routes.userDetail("123"), navController.currentDestination?.route)
}
```

## 6. Scaffold + TopAppBar Pattern

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UsersScreen(
    viewModel: UsersViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Users") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { padding ->
        UsersContent(
            modifier = Modifier.padding(padding),
            uiState = uiState,
            onEvent = viewModel::onEvent
        )
    }
}
```

## 7. LazyColumn / LazyRow

### Basic Usage
```kotlin
LazyColumn(
    modifier = Modifier.fillMaxSize(),
    contentPadding = PaddingValues(vertical = 8.dp),
    verticalArrangement = Arrangement.spacedBy(4.dp)
) {
    items(
        count = users.size,
        key = { index -> users[index].id }
    ) { index ->
        UserRow(
            user = users[index],
            onClick = { onUserClick(users[index].id) }
        )
    }
}
```

### items() with Key
Always provide `key` for efficient recomposition:
```kotlin
items(users, key = { it.id }) { user ->
    UserRow(user = user, onClick = { onUserClick(user.id) })
}
```

### Sticky Headers
```kotlin
LazyColumn {
    users.groupBy { it.role }.forEach { (role, usersInRole) ->
        stickyHeader(key = role.name) {
            RoleHeader(role = role)
        }
        items(usersInRole, key = { it.id }) { user ->
            UserRow(user = user, onClick = onUserClick)
        }
    }
}
```

### Performance Rules

| Rule | Description |
|------|-------------|
| Always provide `key` | Enables efficient item diffing and recomposition |
| Avoid large items | Keep item composables simple; extract to smaller pieces |
| Use `contentType` | Helps Compose pool similar item types |
| Don't nest LazyColumn | Use a single LazyColumn with multiple item blocks |
| `fillMaxSize()` on LazyColumn | Ensures scrolling works correctly |

```kotlin
LazyColumn {
    items(
        count = items.size,
        key = { items[it].id },
        contentType = { "user_row" }
    ) { index ->
        UserRow(user = items[index])
    }
}
```

## 8. collectAsStateWithLifecycle Usage

```kotlin
@Composable
fun MyScreen(viewModel: MyViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    MyContent(uiState = uiState)
}
```

### Why Not collectAsState?

| Method | Lifecycle Aware | Stops on Background | Survives Config Change |
|--------|----------------|---------------------|----------------------|
| `collectAsStateWithLifecycle()` | Yes | Yes | Yes |
| `collectAsState()` | No | No (keeps collecting) | Yes |

`collectAsStateWithLifecycle` uses `repeatOnLifecycle(STARTED)` internally, saving resources when the app is backgrounded.

## 9. Side Effects

### LaunchedEffect (Key-Triggered)
```kotlin
LaunchedEffect(orderId) {
    viewModel.trackOrder(orderId)
}
```

Restarted when `orderId` changes. Cancelled when composable leaves composition.

### SideEffect (After Every Successful Recomposition)
```kotlin
SideEffect {
    analytics.trackScreenView("UsersScreen")
}
```

Use sparingly. Runs after every recomposition, not just the first.

### rememberUpdatedState (Avoid Stale References)
```kotlin
@Composable
fun AutoRefresh(refreshInterval: Duration, onRefresh: () -> Unit) {
    val currentOnRefresh by rememberUpdatedState(onRefresh)

    LaunchedEffect(refreshInterval) {
        while (true) {
            delay(refreshInterval.inWholeMilliseconds)
            currentOnRefresh()
        }
    }
}
```

### DisposableEffect (Cleanup)
```kotlin
@Composable
fun LocationTracker(onLocationUpdate: (Location) -> Unit) {
    DisposableEffect(Unit) {
        val listener = registerLocationListener { location ->
            onLocationUpdate(location)
        }

        onDispose {
            unregisterLocationListener(listener)
        }
    }
}
```

### Side Effect Decision Table

| Need | Use |
|------|-----|
| One-time async work on composition | `LaunchedEffect(Unit)` |
| Async work triggered by key change | `LaunchedEffect(key)` |
| Cleanup on leave composition | `DisposableEffect` |
| Notify external system after recomposition | `SideEffect` |
| Periodic work with latest callback | `LaunchedEffect` + `rememberUpdatedState` |
| Never | Direct suspend call in body |

## 10. Compose Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| `ViewModel()` in composable body | New instance on every recomposition | Use `hiltViewModel()` or `viewModel()` |
| Unstable parameters (Lambdas without `remember`) | Unnecessary recompositions | `remember { { ... } }` or method reference |
| Side effects in composable body | Runs on every recomposition | Wrap in `LaunchedEffect` |
| `Flow` without `remember` | New collector each recomposition | `collectAsStateWithLifecycle()` |
| Mutable state in singleton/object | Unpredictable recomposition | State in ViewModel via `StateFlow` |
| Passing ViewModel deep into tree | Tight coupling, untestable | Pass data and callbacks only |
| `mutableStateOf` in ViewModel | Not thread-safe | Use `MutableStateFlow` in ViewModel |
| Heavy computation in composable | Jank, frame drops | Move to ViewModel, use `derivedStateOf` |
| Creating objects in composable body | Allocations on every recomposition | `remember { ... }` for stable references |
| Not providing keys to `LazyColumn` | Inefficient diffing, flickering | Always use `key = { it.id }` |
| Nested `LazyColumn` | Conflicting scroll, performance | Single LazyColumn with sections |
| Ignoring `padding` from Scaffold | Content behind top bar / bottom nav | Apply `Modifier.padding(padding)` |

### Stable Types in Compose

Compose skips recomposition of children with stable, unchanged parameters. A type is stable if:
- It is a primitive type (`Int`, `String`, `Boolean`, etc.)
- It is an enum
- It is a data class with only stable fields (all `val`)
- It is a `State<T>` or `MutableState<T>`
- It is a function type (lambda)

Mutable data classes (`var` fields) are NOT stable. Always use immutable data classes for UI models.

```kotlin
data class UserUiModel(    // Stable - all val
    val id: String,
    val name: String,
    val avatarUrl: String
)
```

## Cross References

- Related rules: `compose-vm-pattern`, `compose-state-management`, `compose-no-suspend-in-body`, `compose-lazy-keys`, `compose-lifecycle-collection`, `compose-side-effects`, `compose-unstable-params`, `compose-stateless-composables`, `compose-navigation`, `compose-scaffold-pattern`
- Related references: [`kotlin-conventions.md`](kotlin-conventions.md), [`coroutines.md`](coroutines.md), [`architecture.md`](architecture.md), [`navigation-coordinator.md`](navigation-coordinator.md)

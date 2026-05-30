---
title: Kotlin Framework and Architecture Pattern Analysis
impact: HIGH
impactDescription: "Leaking business logic to the UI, incorrect Compose state modeling, and poor multiplatform separation degrade framework performance and modularity"
tags: kotlin, android, kmp, compose, framework
---

## Kotlin Framework and Architecture Pattern Analysis

**Impact: HIGH (Leaking business logic to the UI, incorrect Compose state modeling, and poor multiplatform separation degrade framework performance and modularity)**

Modern Kotlin frameworks—Jetpack Compose / Compose Multiplatform, Kotlin Multiplatform (KMP), Ktor, and Spring Boot—require adherence to domain segregation. Leaking business rules, improper UI state management, and abuse of cross-platform boundaries lead to high CPU overhead, spaghetti code, and poor scalability.

## Incorrect

```kotlin
// ❌ Dangerous Compose State manipulation and API queries inside UI components

@Composable
fun UserProfileScreen(userId: String) {
    // ❌ Performs raw database read on every recomposition!
    val user = AppDatabase.getInstance().userDao().getUserById(userId) 

    var isEditing by remember { mutableStateOf(false) }
    var inputName by remember { mutableStateOf(user?.name ?: "") }

    Column {
        Text("Profile: ${user?.name}")
        TextField(
            value = inputName,
            onValueChange = { inputName = it }
        )
        Button(onClick = {
            // ❌ Mutates database directly inside the UI click listener
            AppDatabase.getInstance().userDao().updateName(userId, inputName)
            isEditing = false
        }) {
            Text("Save")
        }
    }
}

// ❌ KMP Overuse of expect/actual for business logic
// commonMain
expect class TokenManager {
    fun saveToken(token: String) // ❌ Unnecessary platform-specific implementation class
}
```

## Correct

```kotlin
// ✅ Compose UI State Hoisting, VM-driven logic, and KMP Interface Separation

// commonMain - Repository Interface (Shared business contract)
interface TokenRepository {
    fun saveToken(token: String)
}

// UI State Definition
data class ProfileUiState(
    val userName: String = "",
    val isLoading: Boolean = false,
    val isSaveSuccess: Boolean = false
)

// ProfileViewModel.kt (Encapsulates logic, exposes pure states)
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val tokenRepository: TokenRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    fun updateName(userId: String, newName: String) {
        viewModelScope.launch {
            userRepository.updateName(userId, newName)
            tokenRepository.saveToken("TOKEN_$newName")
            _uiState.update { it.copy(userName = newName, isSaveSuccess = true) }
        }
    }
}

// Compose View - Renders states, hoists interaction logic
@Composable
fun UserProfileRoute(
    userId: String,
    viewModel: ProfileViewModel
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle() // ✅ Lifecycle-aware collection

    UserProfileScreen(
        uiState = uiState,
        onSaveName = { newName -> viewModel.updateName(userId, newName) } // ✅ Hoisted event
    )
}

@Composable
fun UserProfileScreen(
    uiState: ProfileUiState,
    onSaveName: (String) -> Unit
) {
    var inputName by rememberSaveable { mutableStateOf(uiState.userName) } // ✅ Survives configuration changes

    Column(modifier = Modifier.padding(16.dp)) {
        if (uiState.isLoading) {
            CircularProgressIndicator()
        } else {
            Text("Profile: ${uiState.userName}")
            OutlinedTextField(
                value = inputName,
                onValueChange = { inputName = it }
            )
            Button(onClick = { onSaveName(inputName) }) {
                Text("Save")
            }
        }
    }
}
```

## Framework Compliance Assessment

```
CRITICAL violations:
├── Network calls or database transactions triggered directly inside Composable functions
└── Platform framework classes (like Android `Context` or iOS `UIViewController`) inside KMP `commonMain`

HIGH violations:
├── Reading / writing disk or database directly in UI click listeners or Compose rendering blocks
├── Missing State Hoisting in UI, leading to components that mutate parent models directly
└── Overusing `expect`/`actual` in KMP for simple API features instead of interfaces and DI

MEDIUM violations:
├── ViewModels directly exposing `MutableStateFlow` instead of immutable `StateFlow`
├── Jetpack Compose screen elements omitting `remember` or `rememberSaveable` for UI-local states
└── Android Jetpack Compose collecting StateFlows using `.collectAsState()` instead of `.collectAsStateWithLifecycle()`

LOW violations:
├── Compose functions exceeding 150 lines without breakdown into smaller focused Composables
└── Hardcoded route string values inside Compose Navigation configs (use type-safe Nav or sealed classes)
```

## Directory Signals

```
✅ Healthy Multiplatform / UI separation:
commonMain/kotlin/.../repository/       → repository interfaces
commonMain/kotlin/.../ui/UserProfile.kt → shared Compose Multiplatform UI
androidMain/kotlin/.../TokenRepositoryImpl.kt → Android platform key-store write
iosMain/kotlin/.../TokenRepositoryImpl.kt     → iOS keychain implementation

❌ Warning signals:
UserProfileScreen.kt with SQL/API calls  → mixing DB with UI logic
expect class JSONParser                 → expect/actual abuse (use `kotlinx-serialization` in commonMain instead)
androidMain/ containing domain logic    → platform directories carrying common business logic
```

## Why

- **Recomposition Safety**: Jetpack Compose executes Composable code dozens of times per second (recomposition). Any database or network read inside a Composable blocks frames, leading to extremely choppy rendering, visual glitches, and massive battery drain.
- **State Hoisting**: Hoisting UI state ensures Composable functions are stateless, predictable, and fully testable in isolation. Stateless Composables are easier to preview, refactor, and reuse across multiple screens.
- **KMP Interface Abstraction**: Relying on standard interfaces instead of `expect`/`actual` declarations reduces tight binding to platforms, simplifies testing (as you can mock an interface in commonMain), and keeps compile times faster.

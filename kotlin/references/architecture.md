# Clean Architecture for Android and KMP

Expert guidance for structuring multi-module Kotlin projects with strict dependency rules, separation of concerns, and testability.

## 1. Four-Layer Module Architecture

### Module Types

| Layer | Modules | Purpose | Depends On |
|-------|---------|---------|------------|
| **App** | `:app` | DI wiring, navigation, Application class | feature, integration |
| **Feature** | `:feature:login`, `:feature:settings` | Screens, ViewModels, UI logic | component, common |
| **Component** | `:component:user`, `:component:network`, `:component:database` | Domain + Data for one capability | common |
| **Common** | `:common:core`, `:common:ui`, `:common:test` | Shared utilities, design system, test fixtures | Nothing (leaf) |
| **Integration** | `:integration:home-feed` | Cross-component coordination | component, common |

### Module Structure Diagram

```
┌─────────────────────────────────────────────────────────┐
│                        :app                              │
│  (DI modules, NavHost, Application, MainActivity)       │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
       ┌───────▼───────┐      ┌──────▼────────┐
       │  :feature:*   │      │ :integration:*│
       │ (Screen, VM)  │      │ (Orchestrate)  │
       └───────┬───────┘      └──────┬────────┘
               │                      │
       ┌───────▼──────────────────────▼────────┐
       │           :component:*                 │
       │  (domain/model, domain/usecase,        │
       │   domain/repository, data/repository,  │
       │   data/datasource, data/mapper)        │
       └───────────────────┬───────────────────┘
                           │
                   ┌───────▼───────┐
                   │  :common:*    │
                   │  (core, ui)   │
                   └───────────────┘
```

### Dependency Rules

| Rule | Description | Enforced By |
|------|-------------|-------------|
| Feature → Component | Features depend on component interfaces | Gradle `implementation` |
| Component → Common | Components depend on shared utilities | Gradle `implementation` |
| Feature → Common | Features may use common UI utilities | Gradle `implementation` |
| App → Feature + Integration | App wires everything together | Gradle `implementation` |
| Component ↛ Component | Components never depend on each other directly | Use integration modules |
| Feature ↛ Feature | Features never depend on other features | Zero tolerance |
| Nobody → App | No module depends on the app module | Zero tolerance |
| Common ↛ Anything | Common modules have zero external dependencies | Zero tolerance |

## 2. Zero-Tolerance Rules

| Rule | ID | Description |
|------|----|-------------|
| No feature cross-dependency | `arch-no-feature-cross-dep` | `:feature:login` must NOT depend on `:feature:settings` |
| No component cross-dependency | `arch-no-component-cross-dep` | `:component:user` must NOT depend on `:component:order` |
| No dependency on app | `arch-no-dependency-on-app` | No module may `implementation(project(":app"))` |
| No business logic in feature | `arch-no-business-in-feature` | UseCases live in component, not feature |
| No circular dependencies | `arch-no-circular-deps` | If A depends on B, B must not depend on A |
| No repo implementation in domain | `arch-repo-iface-in-domain` | Only interfaces in domain, implementations in data |

## 3. Feature Module Structure

```
:feature:login/
├── contract/
│   ├── LoginContract.kt         (UiState, Event, Effect sealed types)
│   └── LoginNavigation.kt       (Route definitions)
├── viewmodel/
│   └── LoginViewModel.kt        (State management, UseCase calls)
├── screen/
│   └── LoginScreen.kt           (Composable screen)
├── components/
│   ├── LoginForm.kt             (Extracted composables)
│   └── PasswordField.kt
└── di/
    └── LoginModule.kt           (Optional: feature-scoped DI)
```

### Contract Pattern
```kotlin
sealed interface LoginUiState {
    data object Idle : LoginUiState
    data object Loading : LoginUiState
    data class Success(val user: UserUiModel) : LoginUiState
    data class Error(val message: String) : LoginUiState
}

sealed interface LoginEvent {
    data class EmailChanged(val email: String) : LoginEvent
    data class PasswordChanged(val password: String) : LoginEvent
    data object SubmitClicked : LoginEvent
}

sealed interface LoginEffect {
    data class NavigateToHome(val userId: String) : LoginEffect
    data class ShowSnackbar(val message: String) : LoginEffect
}
```

### ViewModel
```kotlin
class LoginViewModel(
    private val loginUseCase: LoginUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<LoginUiState>(LoginUiState.Idle)
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

    private val _effect = MutableSharedFlow<LoginEffect>()
    val effect: SharedFlow<LoginEffect> = _effect.asSharedFlow()

    fun onEvent(event: LoginEvent) {
        when (event) {
            is LoginEvent.EmailChanged -> updateEmail(event.email)
            is LoginEvent.PasswordChanged -> updatePassword(event.password)
            LoginEvent.SubmitClicked -> submit()
        }
    }

    private fun submit() {
        viewModelScope.launch {
            _uiState.update { LoginUiState.Loading }
            when (val result = loginUseCase(email, password)) {
                is Try.Success -> {
                    _uiState.update { LoginUiState.Success(result.value.toUiModel()) }
                    _effect.emit(LoginEffect.NavigateToHome(result.value.id))
                }
                is Try.Failure -> {
                    _uiState.update { LoginUiState.Error(result.error.message) }
                }
            }
        }
    }
}
```

## 4. Component Module Structure

```
:component:user/
├── domain/
│   ├── model/
│   │   └── User.kt             (Plain Kotlin data class)
│   ├── repository/
│   │   └── UserRepository.kt   (Interface only)
│   └── usecase/
│       ├── GetUserUseCase.kt
│       ├── ObserveUsersUseCase.kt
│       └── UpdateUserUseCase.kt
├── data/
│   ├── repository/
│   │   └── UserRepositoryImpl.kt
│   ├── datasource/
│   │   ├── local/
│   │   │   └── UserLocalDataSource.kt
│   │   └── remote/
│   │       └── UserRemoteDataSource.kt
│   ├── mapper/
│   │   ├── UserMapper.kt       (Entity ↔ Domain mappers)
│   │   └── UserDtoMapper.kt
│   └── model/
│       ├── UserEntity.kt       (Room/database model)
│       └── UserDto.kt          (Network DTO)
└── di/
    └── UserModule.kt           (Binds repo interface to impl)
```

## 5. UseCase Pattern

### Suspend UseCase
```kotlin
class GetUserUseCase(
    private val repository: UserRepository
) {
    suspend operator fun invoke(id: String): Try<User> =
        repository.getUser(id)
}
```

### Flow-Based UseCase
```kotlin
class ObserveUsersUseCase(
    private val repository: UserRepository
) {
    operator fun invoke(): Flow<List<User>> =
        repository.observeUsers()
}
```

### UseCase with Parameters
```kotlin
class SearchUsersUseCase(
    private val repository: UserRepository
) {
    operator fun invoke(query: String, limit: Int = 20): Flow<List<User>> =
        repository.searchUsers(query, limit)
}
```

### Rules
- UseCases live in `component:*/domain/usecase/`
- They contain business logic only (validation, filtering, ordering)
- They delegate to repository interfaces
- They return domain models, never data-layer types
- One UseCase per operation (Single Responsibility)

## 6. Domain Models

Domain models are plain Kotlin classes with zero framework annotations.

```kotlin
data class User(
    val id: String,
    val name: String,
    val email: String,
    val role: Role,
    val createdAt: Instant
)

enum class Role {
    ADMIN, MEMBER, GUEST
}
```

| Rule | Description |
|------|-------------|
| No Room annotations | `@Entity`, `@ColumnInfo` belong in data layer |
| No Retrofit annotations | `@SerializedName`, `@GET` belong in data layer |
| No Compose types | `@Composable`, `MutableState` belong in feature layer |
| No Android framework types | `Context`, `SharedPreferences` belong in data layer |
| No serialization framework | Use mappers to convert to/from DTOs |

## 7. Repository Pattern

### Interface in Domain
```kotlin
interface UserRepository {
    suspend fun getUser(id: String): Try<User>
    fun observeUsers(): Flow<List<User>>
    suspend fun saveUser(user: User): Try<Unit>
    suspend fun deleteUser(id: String): Try<Unit>
}
```

### Implementation in Data
```kotlin
class UserRepositoryImpl(
    private val localDataSource: UserLocalDataSource,
    private val remoteDataSource: UserRemoteDataSource,
    private val dispatchers: DispatcherProvider
) : UserRepository {

    override suspend fun getUser(id: String): Try<User> =
        withContext(dispatchers.io) {
            try {
                val dto = remoteDataSource.getUser(id)
                localDataSource.save(dto.toEntity())
                Try.Success(dto.toDomain())
            } catch (e: IOException) {
                val cached = localDataSource.getUser(id)
                cached?.toDomain()?.let { Try.Success(it) }
                    ?: Try.Failure(AppError.Network(e.message))
            }
        }

    override fun observeUsers(): Flow<List<User>> =
        localDataSource.observeUsers()
            .map { entities -> entities.map { it.toDomain() } }
            .flowOn(dispatchers.io)
}
```

### DI Wiring
```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class UserModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository

    @Binds
    abstract fun bindUserLocalDataSource(
        impl: UserLocalDataSourceImpl
    ): UserLocalDataSource
}
```

## 8. Mapper Pattern

Mappers are extension functions defined near the data model they convert from.

### DTO → Domain
```kotlin
// In :component:user/data/model/UserDto.kt or data/mapper/UserDtoMapper.kt

data class UserDto(
    @SerializedName("id") val id: String,
    @SerializedName("full_name") val fullName: String,
    @SerializedName("email_address") val emailAddress: String
)

fun UserDto.toDomain(): User = User(
    id = id,
    name = fullName,
    email = emailAddress,
    role = Role.MEMBER,
    createdAt = Instant.now()
)
```

### Entity ↔ Domain
```kotlin
data class UserEntity(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    val role: String,
    val createdAt: Long
)

fun UserEntity.toDomain(): User = User(
    id = id,
    name = name,
    email = email,
    role = Role.valueOf(role),
    createdAt = Instant.ofEpochMilli(createdAt)
)

fun User.toEntity(): UserEntity = UserEntity(
    id = id,
    name = name,
    email = email,
    role = role.name,
    createdAt = createdAt.toEpochMilli()
)
```

### Naming Convention

| Direction | Function Name | Location |
|-----------|--------------|----------|
| DTO → Domain | `UserDto.toDomain()` | Near DTO class |
| Domain → Entity | `User.toEntity()` | Near Entity class |
| Entity → Domain | `UserEntity.toDomain()` | Near Entity class |
| Domain → UI | `User.toUiModel()` | In feature module |

## 9. Error Handling

### Sealed Try / AppError Pattern
```kotlin
sealed interface Try<out T> {
    data class Success<out T>(val value: T) : Try<T>
    data class Failure(val error: AppError) : Try<Nothing>
}

sealed class AppError(open val message: String) {
    data class Network(override val message: String, val code: Int? = null) : AppError(message)
    data class NotFound(override val message: String) : AppError(message)
    data class Validation(override val message: String, val field: String) : AppError(message)
    data class Unauthorized(override val message: String) : AppError(message)
    data class Timeout(override val message: String) : AppError(message)
    data class Unknown(override val message: String, val cause: Throwable?) : AppError(message)
}
```

### Usage in Repository
```kotlin
override suspend fun getUser(id: String): Try<User> = withContext(dispatchers.io) {
    try {
        val response = api.getUser(id)
        if (response.isSuccessful) {
            Try.Success(response.body()!!.toDomain())
        } else {
            when (response.code()) {
                401 -> Try.Failure(AppError.Unauthorized("Session expired"))
                404 -> Try.Failure(AppError.NotFound("User not found"))
                else -> Try.Failure(AppError.Network("Server error", response.code()))
            }
        }
    } catch (e: TimeoutCancellationException) {
        Try.Failure(AppError.Timeout("Request timed out"))
    } catch (e: IOException) {
        Try.Failure(AppError.Network("No internet connection"))
    } catch (e: Exception) {
        Try.Failure(AppError.Unknown(e.message ?: "Unknown error", e))
    }
}
```

### Usage in ViewModel
```kotlin
when (val result = getUserUseCase(userId)) {
    is Try.Success -> _uiState.update { UiState.Success(result.value) }
    is Try.Failure -> when (result.error) {
        is AppError.Network -> _effect.emit(Effect.ShowSnackbar("Network error"))
        is AppError.Unauthorized -> _effect.emit(Effect.NavigateToLogin)
        else -> _uiState.update { UiState.Error(result.error.message) }
    }
}
```

## 10. DI Wiring (App Module Only)

Dependency injection modules belong in `:app` or at the component level — never in feature modules for cross-feature bindings.

```
:app/
├── di/
│   ├── AppModule.kt            (App-wide bindings: DispatcherProvider, OkHttpClient)
│   ├── DatabaseModule.kt       (Room database instance)
│   ├── NetworkModule.kt        (Retrofit, interceptors)
│   └── NavigationModule.kt     (NavController, navigation graph)
├── navigation/
│   ├── AppNavHost.kt           (NavHost with all routes)
│   └── Routes.kt               (Route constants)
├── MainActivity.kt
└── Application.kt
```

### Rules
| Rule | Description |
|------|-------------|
| DI in `:app` or `:component:*/di/` | Feature modules never provide cross-feature dependencies |
| Navigation in `:app` only | Features define routes, app assembles the graph |
| No `@Singleton` in features | Use `@ViewModelScoped` or `@ActivityScoped` |
| Interface → Implementation binding | Use `@Binds`, not `@Provides` for implementations |

## 11. Integration Modules

When component A needs functionality from component B, create an integration module.

```
:integration:home-feed/
├── domain/
│   └── HomeFeedUseCase.kt      (Combines User + Feed + Notification components)
├── di/
│   └── HomeFeedModule.kt       (Wires cross-component UseCase)
└── HomeFeedCoordinator.kt      (Optional: orchestrates multi-component flow)
```

### When to Use Integration Modules

| Scenario | Solution |
|----------|----------|
| Home screen needs user + feed data | Integration module combines UseCases |
| Order completion needs inventory + payment | Integration UseCase with both repositories |
| Analytics tracking across features | Integration module observes shared events |
| A/B testing conditional behavior | Integration module provides strategy |

### Integration UseCase Example
```kotlin
class HomeFeedUseCase(
    private val observeUsers: ObserveUsersUseCase,
    private val observeFeed: ObserveFeedUseCase,
    private val observeNotifications: ObserveNotificationsUseCase
) {
    data class HomeData(
        val users: List<User>,
        val feed: List<FeedItem>,
        val unreadNotifications: Int
    )

    operator fun invoke(): Flow<HomeData> = combine(
        observeUsers(),
        observeFeed(),
        observeNotifications()
    ) { users, feed, notifications ->
        HomeData(
            users = users,
            feed = feed,
            unreadNotifications = notifications.count { !it.read }
        )
    }
}
```

## 12. Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Business logic in ViewModel | ViewModel becomes untestable, couples to UI | Move to UseCase in component |
| Business logic in feature | Feature grows into mini-monolith | Extract to component with domain layer |
| Shared mutable state between features | Race conditions, tight coupling | Integration module with single source of truth |
| Repository impl in domain layer | Violates dependency inversion | Impl stays in data layer |
| Domain model with framework annotations | Leaky abstraction, hard to reuse | Plain Kotlin, mappers in data layer |
| Feature importing another feature | Tight coupling, circular dependency risk | Integration module or event bus |
| UseCase returning DTO/Entity | Data layer leaks into domain | Return domain models only |
| ViewModel creating UseCase instances | No DI, untestable | Inject via constructor |
| Singleton repositories | Hard to test, hidden state | DI-managed lifecycle |
| God component (everything in one) | Unmaintainable, merge conflicts | Split by capability |

## Cross References

- Related rules: `arch-domain-pure-kotlin`, `arch-no-entity-in-ui`, `arch-logic-in-usecases`, `arch-no-fat-repository`, `arch-no-circular-deps`, `arch-no-feature-cross-dep`, `arch-no-component-cross-dep`, `arch-no-dependency-on-app`, `arch-no-business-in-feature`, `arch-no-ui-in-component`, `arch-di-only-in-app`, `arch-repo-iface-in-domain`
- Related references: [`kotlin-conventions.md`](kotlin-conventions.md), [`coroutines.md`](coroutines.md), [`compose-ui.md`](compose-ui.md), [`navigation-coordinator.md`](navigation-coordinator.md)

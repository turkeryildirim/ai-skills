# Idiomatic Kotlin Conventions

Comprehensive guide for writing idiomatic, safe, and maintainable Kotlin code following community best practices and modern language features (Kotlin 2.x).

## 1. Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Classes / Interfaces / Objects | PascalCase | `UserRepository`, `LoginResult` |
| Functions / Properties / Variables | camelCase | `fetchUsers()`, `itemCount` |
| Constants / Compile-time | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT_MS` |
| Backing properties | underscore prefix | `_state`, `_events` |
| Type parameters | Single uppercase letter or PascalCase | `T`, `R`, `Result` |
| Enum entries | SCREAMING_SNAKE_CASE | `LogLevel.DEBUG`, `HttpStatus.OK` |
| Packages | all lowercase, no underscores | `com.app.feature.login` |
| XML IDs / Compose | snake_case | `user_name_text`, `LoginScreen` |
| Boolean properties | is/has/can/should prefix | `isValid`, `hasPermission` |
| Extension files | `<extendedType>Kt` or named | `StringExt.kt`, `ViewUtils.kt` |

## 2. Null Safety Patterns

Kotlin's null safety is its strongest feature. Use these patterns in order of preference:

### Safe Call Chain
```kotlin
val city = user?.address?.city
```

### Elvis Operator for Defaults
```kotlin
val name = user?.name ?: "Unknown"
```

### `let` for Null-Gated Execution
```kotlin
user?.let { u ->
    repository.save(u)
}
```

### Early Return
```kotlin
fun process(user: User?) {
    val u = user ?: return
    u.sendEmail()
}
```

### `requireNotNull` for Arguments
```kotlin
fun process(id: String?) {
    val validId = requireNotNull(id) { "id must not be null" }
    repository.findById(validId)
}
```

### NEVER Use `!!`
The `!!` operator masks bugs and produces `KotlinNullPointerException` at runtime. Always prefer safe alternatives.

| Bad | Good |
|-----|------|
| `user!!.name` | `user?.name ?: "Unknown"` |
| `get() = field!!` | `lateinit var` or `by lazy` |
| `list.first()!!` | `list.firstOrNull() ?: error("empty")` |

## 3. Data Classes

Data classes are for holding immutable data. All fields must be `val`.

```kotlin
data class User(
    val id: String,
    val name: String,
    val email: String,
    val role: Role
)
```

### copy() for Immutable Updates
```kotlin
val updated = user.copy(name = "Alice", role = Role.ADMIN)
```

### Destructuring
```kotlin
val (id, name, _, role) = user
```

### Anti-Patterns

| Avoid | Instead |
|-------|---------|
| `var` in data class | Always use `val` + `copy()` |
| Data classes with logic | Keep as pure data holders |
| Deep inheritance of data classes | Use composition or sealed classes |

## 4. Sealed Classes and Interfaces

Sealed types enable exhaustive `when` expressions and type-safe state modeling.

### Result Type
```kotlin
sealed interface Result<out T> {
    data class Success<T>(val value: T) : Result<T>
    data class Failure(val error: AppError) : Result<Nothing>
}
```

### UI State Modeling
```kotlin
sealed interface UsersUiState {
    data object Loading : UsersUiState
    data class Success(val users: List<User>) : UsersUiState
    data class Error(val message: String) : UsersUiState
}
```

### UI Events (One-Shot)
```kotlin
sealed interface UsersEvent {
    data class ShowSnackbar(val message: String) : UsersEvent
    data class NavigateToDetail(val userId: String) : UsersEvent
}
```

### Exhaustive when
```kotlin
fun handle(result: Result<User>) = when (result) {
    is Result.Success -> showUser(result.value)
    is Result.Failure -> showError(result.error)
}
```

Prefer sealed interfaces over sealed classes when no shared state is needed between subtypes.

## 5. Functions

### Single-Expression Functions
```kotlin
fun fullName(firstName: String, lastName: String): String = "$firstName $lastName"

fun isValid(email: String): Boolean = email.contains("@") && email.contains(".")
```

### Extension Functions
```kotlin
fun String.isEmail(): Boolean =
    matches(Regex("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$"))

fun Int.toHex(): String = toString(16)
```

### Default Parameters Over Overloads
```kotlin
fun connect(
    host: String = "localhost",
    port: Int = 8080,
    timeoutMs: Long = 5000
): Connection

connect()
connect(host = "api.example.com")
connect(host = "api.example.com", port = 443, timeoutMs = 10_000)
```

### Parameter Ordering
Required parameters first, then optional (default) parameters:
```kotlin
fun search(query: String, limit: Int = 20, offset: Int = 0): List<Result>
```

## 6. Collections

### Immutable by Default
```kotlin
val users: List<User> = listOf(user1, user2)
val mapping: Map<String, User> = mapOf("a" to user1)
val unique: Set<String> = setOf("a", "b", "c")
```

Use `MutableList`, `MutableMap`, `MutableSet` only when building collections incrementally within a local scope, then expose as immutable.

### Sequences for Large or Chained Operations
```kotlin
val result = items
    .asSequence()
    .filter { it.isActive }
    .map { it.toDomain() }
    .take(50)
    .toList()
```

Use sequences when:
- Collection has 1000+ elements
- Chain has 3+ intermediate operations
- Using `take`, `first`, or `any` terminal operations early

### Functional Operators

| Operator | Purpose | Example |
|----------|---------|---------|
| `map` | Transform each element | `.map { it.name }` |
| `flatMap` | Transform + flatten | `.flatMap { it.tags }` |
| `filter` | Keep matching elements | `.filter { it.isActive }` |
| `groupBy` | Group by key | `.groupBy { it.role }` |
| `associateBy` | Map key to element | `.associateBy { it.id }` |
| `partition` | Split into matching/non-matching | `val (active, inactive) = users.partition { it.isActive }` |
| `sortedBy` | Sort by property | `.sortedBy { it.name }` |
| `distinctBy` | Remove duplicates by key | `.distinctBy { it.id }` |
| `fold` | Accumulate into result | `.fold(0) { acc, item -> acc + item.score }` |
| `zip` | Pair two collections | `names.zip(scores)` |

### associateBy Example
```kotlin
val userById: Map<String, User> = users.associateBy { it.id }
val user = userById[userId]
```

### partition Example
```kotlin
val (admins, others) = users.partition { it.role == Role.ADMIN }
```

## 7. Value Classes

Value classes avoid allocation overhead while providing type safety.

```kotlin
@JvmInline
value class EmailAddress(private val value: String) {
    init {
        require(value.contains("@")) { "Invalid email address: $value" }
    }

    override fun toString(): String = value
}
```

Use value classes for:
- Wrapper types (IDs, emails, percentages)
- Unit types to avoid mixing (Milliseconds vs Seconds)
- Domain primitives with validation

```kotlin
@JvmInline
value class UserId(val value: String)

@JvmInline
value class ProjectId(val value: String)

fun assignProject(user: UserId, project: ProjectId)
```

## 8. Error Handling

### Result<T> Pattern
```kotlin
sealed interface Try<out T> {
    data class Success<out T>(val value: T) : Try<T>
    data class Failure(val error: AppError) : Try<Nothing>
}

fun fetchUser(id: String): Try<User>
```

### require / check / error

| Function | When to Use | Throws |
|----------|-------------|--------|
| `require(condition)` | Validate function arguments | `IllegalArgumentException` |
| `check(condition)` | Validate object state | `IllegalStateException` |
| `error(message)` | Unreachable code path | `IllegalStateException` |

```kotlin
fun transfer(amount: Double, from: Account, to: Account) {
    require(amount > 0) { "Amount must be positive" }
    check(from.balance >= amount) { "Insufficient funds" }
}
```

### No Exception Flow Control
Never use exceptions for control flow. Return sealed types instead:

| Avoid | Instead |
|-------|---------|
| `throw InvalidInputException()` | Return `Result.Failure(ValidationError(...))` |
| `try/catch` for business logic | `fold`, `map`, `getOrDefault` on Result |
| Exceptions for validation | `require` + sealed result type |

## 9. Scope Functions

| Function | Receiver | Returns | Best For |
|----------|----------|---------|----------|
| `let` | `it` | Lambda result | Null checks, transformations, chaining |
| `run` | `this` | Lambda result | Executing a block with object context |
| `apply` | `this` | Receiver itself | Object configuration / initialization |
| `also` | `it` | Receiver itself | Side effects (logging, debugging) without altering chain |
| `with` | `this` | Lambda result | Operating on a non-receiver object |

### let for Null Gating
```kotlin
user?.let { u ->
    database.save(u)
    analytics.track("user_saved", u.id)
}
```

### apply for Configuration
```kotlin
val request = Request.Builder().apply {
    addHeader("Authorization", token)
    timeout(30, TimeUnit.SECONDS)
}.build()
```

### also for Side Effects
```kotlin
val users = repository.fetchUsers().also {
    logger.info("Fetched ${it.size} users")
}
```

### run for Scoped Computation
```kotlin
val result = run {
    val processed = data.map { transform(it) }
    val filtered = processed.filter { isValid(it) }
    filtered.sumOf { it.score }
}
```

### Avoid Over-Nesting
```kotlin
// Bad - nested scope functions
user?.let {
    it.address?.let { addr ->
        addr.city?.let { city ->
            println(city)
        }
    }
}

// Good - chain or early return
val city = user?.address?.city ?: return
println(city)
```

## 10. Delegation

### by lazy
```kotlin
val database: SQLiteDatabase by lazy {
    SQLiteDatabase.openDatabase(path, null, OPEN_READWRITE)
}
```

Use `by lazy` for expensive initialization that may not be needed, or to break circular initialization dependencies.

### Delegates.observable
```kotlin
var score: Int by Delegates.observable(0) { _, oldValue, newValue ->
    logger.info("Score changed: $oldValue -> $newValue")
}
```

### Interface Delegation
```kotlin
interface Logger {
    fun log(message: String)
}

class ConsoleLogger : Logger {
    override fun log(message: String) = println(message)
}

class TimedLogger(
    private val delegate: Logger = ConsoleLogger()
) : Logger by delegate {
    override fun log(message: String) {
        delegate.log("[${Instant.now()}] $message")
    }
}
```

Delegation is preferred over inheritance for composing behavior.

### Delegated Properties for Preferences
```kotlin
// Note: prefs.string() and prefs.boolean() are custom delegated property extensions, e.g.:
// fun SharedPreferences.string(key: String, def: String) = ReadWriteProperty<Any?, String>
class UserPreferences(private val prefs: SharedPreferences) {
    var theme: String by prefs.string("theme", "system")
    var notificationsEnabled: Boolean by prefs.boolean("notifications", true)
}
```

## 11. DSL Builders

### @DslMarker for Type Safety
```kotlin
@DslMarker
annotation class ServerDsl
```

### Type-Safe Builder Example
```kotlin
@DslMarker
annotation class ServerDsl

data class ServerConfig(
    val host: String,
    val port: Int,
    val database: DatabaseConfig,
    val features: List<Feature>
)

data class DatabaseConfig(
    val url: String,
    val poolSize: Int
)

data class Feature(
    val name: String,
    val enabled: Boolean
)

@ServerDsl
class ServerConfigBuilder {
    var host: String = "localhost"
    var port: Int = 8080
    private var database: DatabaseConfig = DatabaseConfig("", 10)
    private val features: MutableList<Feature> = mutableListOf()

    fun database(block: DatabaseBuilder.() -> Unit) {
        database = DatabaseBuilder().apply(block).build()
    }

    fun feature(name: String, enabled: Boolean = true) {
        features.add(Feature(name, enabled))
    }

    fun build(): ServerConfig = ServerConfig(host, port, database, features.toList())
}

@ServerDsl
class DatabaseBuilder {
    var url: String = ""
    var poolSize: Int = 10
    fun build(): DatabaseConfig = DatabaseConfig(url, poolSize)
}

fun serverConfig(block: ServerConfigBuilder.() -> Unit): ServerConfig =
    ServerConfigBuilder().apply(block).build()
```

### Usage
```kotlin
val config = serverConfig {
    host = "api.example.com"
    port = 443
    database {
        url = "jdbc:postgresql://db:5432/app"
        poolSize = 20
    }
    feature("caching")
    feature("rate-limiting", enabled = false)
}
```

## 12. when Expressions

### Exhaustive with Sealed Types
```kotlin
fun handleState(state: UiState) = when (state) {
    is UiState.Loading -> renderLoading()
    is UiState.Success -> renderContent(state.data)
    is UiState.Error -> renderError(state.message)
}
```

### as Expression (Prefer Over Statement)
```kotlin
val label = when (status) {
    Status.ACTIVE -> "Active"
    Status.PAUSED -> "Paused"
    Status.CANCELLED -> "Cancelled"
}

val discount = when {
    order.total > 1000 -> 0.15
    order.total > 500 -> 0.10
    order.total > 100 -> 0.05
    else -> 0.0
}
```

### Subject-less when for Complex Conditions
```kotlin
when {
    user.isAdmin && action == Action.DELETE -> allow()
    user.isBanned -> deny("User is banned")
    resource.isLocked -> deny("Resource is locked")
    else -> allow()
}
```

## 13. Object and Companion Object

### Object for Singletons
```kotlin
object Clock {
    fun now(): Instant = Instant.now()
}

object DateFormatters {
    val iso: DateTimeFormatter = DateTimeFormatter.ISO_OFFSET_DATE_TIME
    val dateOnly: DateTimeFormatter = DateTimeFormatter.ISO_LOCAL_DATE
}
```

### Companion Object for Factory Methods and Constants
```kotlin
data class Money private constructor(
    val amount: BigDecimal,
    val currency: Currency
) {
    companion object {
        fun of(amount: BigDecimal, currency: Currency): Money {
            require(amount >= BigDecimal.ZERO) { "Amount must be non-negative" }
            return Money(amount, currency)
        }

        fun usd(amount: BigDecimal): Money = of(amount, Currency.getInstance("USD"))
        fun eur(amount: BigDecimal): Money = of(amount, Currency.getInstance("EUR"))

        val ZERO_USD: Money = Money(BigDecimal.ZERO, Currency.getInstance("USD"))
    }
}
```

### Extension Functions on Companion
```kotlin
data class User(val id: String, val name: String) {
    companion object
}

fun User.Companion.fromJson(json: JsonObject): User =
    User(json.getString("id"), json.getString("name"))
```

## 14. Anti-Patterns

| Avoid | Instead | Rule |
|-------|---------|------|
| `!!` operator | Safe calls, Elvis, `let`, early return | `kt-no-force-unwrap` |
| `var` in data classes | `val` + `copy()` | `kt-immutable-data-class` |
| Unsafe lateinit access | Check `::property.isInitialized` or use nullable/lazy | `kt-no-lateinit-unsafe` |
| Overloaded functions | Default parameters | `kt-default-params` |
| Exception flow control | `Result` / `Try` sealed type | `kt-no-exception-control-flow` |
| Chained collection operations | Use `.asSequence()` for 3+ operations / large data | `kt-sequences-large-collections` |
| Mutable public collections | Expose read-only List, mutate internally | `kt-no-mutable-public` |
| Raw identifiers for IDs | Use `@JvmInline value class` | `kt-value-classes` |
| Generic package names | Use PascalCase/camelCase/SCREAMING_SNAKE appropriately | `kt-naming-conventions` |
| Non-null server fields | Default nullable fields (`= null`) | `kt-server-response-nullable` |
| Nested scope functions | Chain safe calls or use local variables | `kt-no-nested-scope-functions` |
| Ignoring platform type nullability | Treat all return values from Java as nullable | `kt-handle-java-platform-types` |
| Value class without validation | Add `init { require(...) }` for compile-time invariants | `kt-value-class-validation` |
| String-based routes | Type-safe Navigation (Navigation 2.8.0+) | `kt-type-safe-navigation` |
| GSON or manual JSON parsing | `kotlinx-serialization-json` | `kt-serialization-json` |
| Platform-specific expectations | Interface-based dependency injection | `kt-kmp-expect-actual` |
| Hardcoded preview data | `PreviewParameterProvider` | `kt-composable-preview-parameter` |

## Cross References

- Related rules: `kt-no-force-unwrap`, `kt-immutable-data-class`, `kt-sealed-interface`, `kt-default-params`, `kt-no-exception-control-flow`, `kt-sequences-large-collections`, `kt-no-mutable-public`, `kt-value-classes`, `kt-naming-conventions`, `kt-server-response-nullable`, `kt-no-lateinit-unsafe`, `kt-lambda-return-label`, `kt-lifecycle-paired-observer`, `kt-no-nested-scope-functions`, `kt-handle-java-platform-types`, `kt-value-class-validation`, `kt-logging-levels`, `kt-type-safe-navigation`, `kt-serialization-json`, `kt-kmp-expect-actual`, `kt-composable-preview-parameter`, `kt-opt-in-annotations`
- Related references: [`coroutines.md`](coroutines.md), [`architecture.md`](architecture.md), [`compose-ui.md`](compose-ui.md), [`navigation-coordinator.md`](navigation-coordinator.md)

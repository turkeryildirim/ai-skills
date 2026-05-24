# Rules for Kotlin and Android Development

Actionable directives for modern Kotlin, Coroutines, Architecture, and Android development.

## 1. Kotlin Patterns (`kt-`)

### `kt-no-force-unwrap`
- **Context:** Null safety.
- **Rule:** Use safe calls `?.` + Elvis `?:`, `let`, or early return. Document any `!!` usage with a comment explaining why null is impossible.
- **Avoid:** `user!!.name`

### `kt-immutable-data-class`
- **Context:** Data modeling.
- **Rule:** All `data class` properties must be `val`. Use `copy()` for updates.
- **Avoid:** `data class User(var name: String)`

### `kt-sealed-interface`
- **Context:** Restricted hierarchies.
- **Rule:** Use `sealed interface` over `sealed class` for flexibility (multiple inheritance). Use for Result types, states, events, errors.
- **Avoid:** `sealed class` when `sealed interface` suffices.

### `kt-default-params`
- **Context:** Function signatures.
- **Rule:** Use default parameter values instead of method overloads.
- **Avoid:** Multiple overloaded functions for the same operation.

### `kt-no-exception-control-flow`
- **Context:** Error handling.
- **Rule:** Use `Result<T>`, nullable returns, or sealed error types for expected failures. Use `require`/`check` for precondition violations.
- **Avoid:** Exceptions for expected business flow (e.g., `UserNotFoundException`).

### `kt-sequences-large-collections`
- **Context:** Collection processing.
- **Rule:** Use `.asSequence()` for collections with 3+ chained operations or large datasets. Use `sequence { yield() }` for generators.
- **Avoid:** Chained `List` operations on large datasets without `asSequence()`.

### `kt-no-mutable-public`
- **Context:** API design.
- **Rule:** Expose `List<T>` (immutable) in public API. Use `MutableList<T>` only internally.
- **Avoid:** Public properties of type `MutableList`.

### `kt-value-classes`
- **Context:** Type safety.
- **Rule:** Use `@JvmInline value class` to wrap primitives that could be confused (UserId, ProductId, Price). Add `init { require }` for validation.
- **Avoid:** Raw `String` or `Long` for domain identifiers.

### `kt-naming-conventions`
- **Context:** Code style.
- **Rule:** PascalCase for classes/interfaces, camelCase for functions/variables, SCREAMING_SNAKE for constants, lowercase for packages. Boolean properties: `is`, `has`, `can` prefix.
- **Avoid:** Abbreviations (`uid` → `userId`), `data`/`info`/`manager` suffixes.

### `kt-server-response-nullable`
- **Context:** API response models.
- **Rule:** All server response data class fields must be nullable with `= null` defaults. Server may omit fields.
- **Avoid:** Non-null fields in DTOs without guaranteed server behavior.

### `kt-no-lateinit-unsafe`
- **Context:** Property initialization.
- **Rule:** Use nullable `var x: T? = null` or `by lazy { }` instead of `lateinit var` when the value may be null at access time. `lateinit` is only valid for non-null, guaranteed-initialized properties.
- **Avoid:** `lateinit var` for nullable scenarios.

### `kt-lambda-return-label`
- **Context:** Lambda control flow.
- **Rule:** Use `return@label` (e.g., `return@forEach`) to return from lambdas. Never use bare `return` in a lambda (returns from outer function).
- **Avoid:** `return` inside `forEach`, `map`, `let` etc.

### `kt-lifecycle-paired-observer`
- **Context:** Lifecycle management.
- **Rule:** Always pair `addObserver` with `removeObserver` in corresponding lifecycle callbacks.
- **Avoid:** Adding observers without cleanup (memory leaks).

### `kt-no-nested-scope-functions`
- **Context:** Scope functions.
- **Rule:** Chain safe calls (`user?.address?.city?.let { }`) instead of nesting scope functions.
- **Avoid:** `user?.let { it.address?.let { it.city?.let { } } }`

### `kt-handle-java-platform-types`
- **Context:** Java interop.
- **Rule:** Treat all return values from Java code as nullable. Use safe calls or explicit null checks.
- **Avoid:** Assuming non-null from Java APIs.

### `kt-value-class-validation`
- **Context:** Value classes.
- **Rule:** Add `init { require(...) }` blocks to value classes for compile-time-enforced invariants.
- **Avoid:** Value classes without validation.

### `kt-logging-levels`
- **Context:** Logging.
- **Rule:** Use `Log.i` for normal flow checkpoints, `Log.w` for recoverable anomalies, `Log.e` for failures/errors. Never log sensitive data.
- **Avoid:** Using `Log.e` for normal flow or `Log.d` in production.

## 2. Concurrency Patterns (`coro-`)

### `coro-no-globalscope`
- **Context:** Coroutine scoping.
- **Rule:** Use `viewModelScope`, `lifecycleScope`, or custom `CoroutineScope`. Never `GlobalScope`.
- **Avoid:** `GlobalScope.launch { }`

### `coro-inject-dispatchers`
- **Context:** Thread management.
- **Rule:** Inject `CoroutineDispatcher` as constructor parameter. Default to `Dispatchers.IO` in production, `UnconfinedTestDispatcher()` in tests.
- **Avoid:** Hardcoded `Dispatchers.IO` in class bodies.

### `coro-supervisor-job`
- **Context:** Parallel failure handling.
- **Rule:** Use `supervisorScope` or `SupervisorJob()` when child failures should not cancel siblings.
- **Avoid:** `CoroutineScope(Job())` — one child failure cancels all.

### `coro-no-cancel-swallow`
- **Context:** Exception handling.
- **Rule:** Always rethrow `CancellationException`. Use `catch (e: CancellationException) { throw e }` before other catch blocks.
- **Avoid:** `catch (e: Exception) { }` without rethrowing `CancellationException`.

### `coro-no-runblocking`
- **Context:** Main thread safety.
- **Rule:** Never call `runBlocking` on the main thread. Use `launch`/`async` or `suspend` functions.
- **Avoid:** `runBlocking { fetchUser() }` in Activity or ViewModel.

### `coro-lifecycle-collection`
- **Context:** Flow collection in UI.
- **Rule:** Use `repeatOnLifecycle(STARTED)` in Activity/Fragment, `collectAsStateWithLifecycle()` in Compose.
- **Avoid:** `lifecycleScope.launch { flow.collect {} }` (collects in background).

### `coro-single-uistate`
- **Context:** ViewModel state.
- **Rule:** Use a single `UiState` data class per screen. Combine multiple flows with `combine()`.
- **Avoid:** Multiple `MutableStateFlow` properties exposed separately.

### `coro-cooperative-cancellation`
- **Context:** Long-running operations.
- **Rule:** Use `ensureActive()` or `yield()` in tight loops. Use `try/finally` with `NonCancellable` for cleanup.
- **Avoid:** CPU-bound loops without suspension points.

### `coro-callback-flow-cleanup`
- **Context:** Bridging callbacks to Flow.
- **Rule:** Always implement `awaitClose { }` in `callbackFlow` to unregister listeners.
- **Avoid:** `callbackFlow` without `awaitClose` (leaks callbacks).

### `coro-no-mutable-in-stateflow`
- **Context:** State updates.
- **Rule:** Always use immutable copies: `_state.update { it.copy(list = it.list + item) }`. Never mutate a collection inside StateFlow.
- **Avoid:** `_state.value.list.add(item)` — shared mutable state.

### `coro-no-flow-on-main`
- **Context:** Flow thread switching.
- **Rule:** Use `flowOn(Dispatchers.IO)` for upstream work. The collector's dispatcher is the caller's dispatcher.
- **Avoid:** `flowOn(Dispatchers.Main)` to force collection on main.

## 3. Architecture Patterns (`arch-`)

### `arch-domain-pure-kotlin`
- **Context:** Domain layer.
- **Rule:** `domain` module must contain only pure Kotlin — no Android imports, no framework annotations, no Room/Retrofit types.
- **Avoid:** `import android.*` in domain layer.

### `arch-no-entity-in-ui`
- **Context:** Data mapping.
- **Rule:** Always map DB entities and network DTOs to domain models. Use extension function mappers (`fun Entity.toDomain()`).
- **Avoid:** Exposing `ItemEntity` or `ItemDto` to presentation layer.

### `arch-logic-in-usecases`
- **Context:** Business logic placement.
- **Rule:** Extract business logic to UseCase classes with `operator fun invoke()`. ViewModel handles UI state only.
- **Avoid:** Complex calculations or business rules directly in ViewModel.

### `arch-no-fat-repository`
- **Context:** Repository implementation.
- **Rule:** Split repository logic into focused DataSource classes (local, remote). Repository coordinates between them.
- **Avoid:** Repository implementation with 500+ lines doing everything.

### `arch-no-circular-deps`
- **Context:** Module dependencies.
- **Rule:** If A depends on B, B must not depend on A. Use integration modules for cross-component coordination.
- **Avoid:** Circular module references.

### `arch-no-feature-cross-dep`
- **Context:** Feature modules.
- **Rule:** Feature modules must never depend on other feature modules. Share code via component/common modules.
- **Avoid:** `implementation(project(":feature:cart"))` from `feature:checkout`.

### `arch-no-component-cross-dep`
- **Context:** Component modules.
- **Rule:** Component modules must never depend on other components. Use integration modules.
- **Avoid:** `component:order` depending on `component:payment`.

### `arch-no-dependency-on-app`
- **Context:** Module boundaries.
- **Rule:** No module may depend on the `:app` module. `app` is a leaf consumer.
- **Avoid:** `implementation(project(":app"))` in any module.

### `arch-no-business-in-feature`
- **Context:** Feature layer.
- **Rule:** Feature modules contain only UI, ViewModel, and navigation contract. Business logic lives in component/domain.
- **Avoid:** UseCase implementations or business calculations in feature modules.

### `arch-no-ui-in-component`
- **Context:** Component layer.
- **Rule:** Component modules contain domain models, UseCases, Repository interfaces + implementations, DataSources. No Compose UI or View code.
- **Avoid:** `@Composable` functions in component modules.

### `arch-di-only-in-app`
- **Context:** Dependency injection.
- **Rule:** All DI module configuration lives in `:app`. Feature and component modules use constructor injection only.
- **Avoid:** Hilt modules or Koin modules in feature/component modules.

### `arch-repo-iface-in-domain`
- **Context:** Repository pattern.
- **Rule:** Repository interfaces defined in domain layer. Implementations in data layer.
- **Avoid:** `OrderRepositoryImpl` in `domain/repository/`.

## 4. Navigation Patterns (`nav-`)

### `nav-coordinator-owns-navigation`
- **Context:** Flow logic.
- **Rule:** Navigation flow logic lives in Coordinator classes, not ViewModel or View.
- **Avoid:** `navigator.showCheckout()` called directly from ViewModel.

### `nav-stateless-coordinator`
- **Context:** Coordinator design.
- **Rule:** Coordinators are stateless and know only where to go next. They can be application-scoped singletons.
- **Avoid:** Storing navigation state in Coordinator.

### `nav-lambda-callbacks`
- **Context:** ViewModel → Coordinator connection.
- **Rule:** Pass lambda callbacks to ViewModels (`var onItemClicked: ((Int) -> Unit)?`). Clear in `onCleared()` to avoid leaks.
- **Avoid:** Direct Coordinator references in ViewModel.

### `nav-no-god-coordinator`
- **Context:** Coordinator scope.
- **Rule:** One Coordinator per flow (Login, Onboarding, News). Use RootCoordinator to delegate between flows.
- **Avoid:** Single Coordinator handling all navigation.

### `nav-navigator-separation`
- **Context:** Navigator pattern.
- **Rule:** Navigator handles actual screen transitions (Fragment transactions, intents). Coordinator decides which transition. They are separate classes.
- **Avoid:** Coordinator directly performing Fragment transactions.

### `nav-coroutine-scoping`
- **Context:** Coroutine-based Coordinators.
- **Rule:** Flow Coordinators scoped to Activity ViewModel. Root Coordinator scoped to Application scope. Process intentions via actor for sequential processing.
- **Avoid:** Coordinators scoped to Fragment lifecycle.

## 5. Compose Patterns (`compose-`)

### `compose-stable-params`
- **Context:** Recomposition optimization.
- **Rule:** Composable parameters must be stable/immutable types or marked `@Stable`. Use `data class` for state parameters.
- **Avoid:** Unstable types (e.g., lambda with captured mutable state) as Composable parameters.

### `compose-no-vm-in-composable`
- **Context:** ViewModel instantiation.
- **Rule:** Use `hiltViewModel()` or `viewModel()` — never instantiate ViewModel directly in a Composable function body.
- **Avoid:** `val vm = MyViewModel()` inside `@Composable fun`.

### `compose-launched-effect-for-async`
- **Context:** Side effects.
- **Rule:** Use `LaunchedEffect(key)` for async operations triggered from Compose. Use `rememberUpdatedState` for callbacks.
- **Avoid:** Calling suspend functions directly in Composable body.

### `compose-no-side-effects`
- **Context:** Composable purity.
- **Rule:** Composable functions must not have side effects (network calls, DB writes). Use `LaunchedEffect` or `SideEffect`.
- **Avoid:** `api.fetchData()` inside `@Composable fun`.

### `compose-remember-flow`
- **Context:** Flow in Compose.
- **Rule:** Always wrap Flow creation with `remember { }` to avoid recreation on recomposition.
- **Avoid:** `val flow = someFlow()` without `remember` in Composable.

### `compose-testtag-for-testing`
- **Context:** Testability.
- **Rule:** Add `Modifier.testTag("stable-id")` to interactive Compose elements. Use testTag for UI test lookup.
- **Avoid:** Relying on displayed text for test element lookup.

## 6. Networking Patterns (`net-`)

### `net-status-validation`
- **Context:** HTTP responses.
- **Rule:** Always validate HTTP status codes (200–299) before decoding. Retrofit/OkHttp do not throw on 4xx/5xx.
- **Avoid:** Decoding response body without checking status code.

### `net-no-main-thread-calls`
- **Context:** Network thread safety.
- **Rule:** All network calls must run on `Dispatchers.IO` or via injected dispatcher. Never on main thread.
- **Avoid:** Synchronous network calls from Activity/ViewModel.

### `net-protocol-client`
- **Context:** Testability.
- **Rule:** Define API clients behind interfaces. Use `MockWebServer` or fakes for testing.
- **Avoid:** Concrete networking classes that cannot be substituted in tests.

### `net-no-completion-handlers`
- **Context:** Async patterns.
- **Rule:** Use `suspend` functions exclusively. No callback-based API patterns.
- **Avoid:** `fun fetch(callback: (Result<T>) -> Unit)`.

### `net-retry-with-backoff`
- **Context:** Network resilience.
- **Rule:** Use exponential backoff for retries. Check `Task.isCancelled` before retrying. Skip 4xx errors from retry.
- **Avoid:** Infinite retry loops or fixed-delay retries.

## 7. Build Patterns (`gradle-`, `conv-`)

### `gradle-version-catalog`
- **Context:** Dependency management.
- **Rule:** All dependency versions in `gradle/libs.versions.toml`. Reference via `libs.*` type-safe accessors.
- **Avoid:** Hardcoded version strings in `build.gradle.kts`.

### `gradle-ksp-over-kapt`
- **Context:** Annotation processing.
- **Rule:** Use KSP (`com.google.devtools.ksp`) instead of KAPT for all new annotation processing. KSP is faster and supports KMP.
- **Avoid:** `kotlin("kapt")` plugin for new modules.

### `gradle-implementation-over-api`
- **Context:** Dependency scope.
- **Rule:** Use `implementation` by default. Use `api` only when dependencies must be transitively exposed to consumers.
- **Avoid:** `api` for internal dependencies (leaks transitive deps, slows compilation).

### `conv-no-duplicate-config`
- **Context:** Convention plugins.
- **Rule:** Never duplicate SDK versions, Kotlin config, or compiler options in module `build.gradle.kts`. Use convention plugins.
- **Avoid:** `compileSdk = 35` in every module's build file.

### `conv-no-hardcoded-versions`
- **Context:** Plugin implementation.
- **Rule:** All versions in convention plugins come from version catalog via `libs.findVersion()` or `libs.findLibrary()`.
- **Avoid:** Hardcoded version strings in plugin code.

### `conv-one-concern-per-plugin`
- **Context:** Plugin design.
- **Rule:** Separate convention plugins per concern: `my.android.library`, `my.android.compose`, `my.android.unit.test`, `my.detekt`.
- **Avoid:** One giant plugin handling all configuration.

### `conv-shared-logic-extracted`
- **Context:** Plugin code reuse.
- **Rule:** Extract shared build logic (e.g., `configureKotlinAndroid()`) into top-level extension functions in the plugin source set.
- **Avoid:** Duplicated configuration across multiple plugins.

## 8. Security Patterns (`sec-`)

### `sec-no-tokens-in-sharedprefs`
- **Context:** Credential storage.
- **Rule:** Store all tokens, secrets, and credentials in `EncryptedSharedPreferences` or Android Keystore. Never in plain `SharedPreferences`, files, or source code.
- **Avoid:** `SharedPreferences.edit().putString("auth_token", token)`.

### `sec-encrypted-storage`
- **Context:** Sensitive data.
- **Rule:** Use `EncryptedSharedPreferences` or Jetpack Security for sensitive data at rest. Use certificate pinning for network.
- **Avoid:** Storing passwords, API keys, or PII in plain text.

## 9. Resource Patterns (`res-`)

### `res-no-reserved-names`
- **Context:** Resource naming.
- **Rule:** Never use Android reserved names (`background`, `foreground`, `icon`, `text`, `button`) for resource IDs, colors, or drawables. Add prefix (`app_background`, `ic_home`).
- **Avoid:** `<color name="background">#FFF</color>`.

### `res-naming-conventions`
- **Context:** Resource organization.
- **Rule:** Prefix: `ic_` for icons, `img_` for images, `bg_` for backgrounds, `layout_` for layouts. Use `app_name` pattern for strings.
- **Avoid:** Generic resource names without prefix.

## Cross Reference Map

- `kt-*`:
  see `../references/kotlin-conventions.md`, `../references/architecture.md`
- `coro-*`:
  see `../references/coroutines.md`, `../references/compose-ui.md`
- `arch-*`:
  see `../references/architecture.md`, `../references/navigation-coordinator.md`
- `nav-*`:
  see `../references/navigation-coordinator.md`, `../references/architecture.md`
- `compose-*`:
  see `../references/compose-ui.md`, `../references/coroutines.md`
- `net-*`:
  see `../references/networking.md`, `../references/architecture.md`
- `gradle-*`, `conv-*`:
  see `../references/build-configuration.md`, `../references/build-convention-plugins.md`
- `sec-*`:
  see `../references/architecture.md`, `../references/networking.md`
- `res-*`:
  see `../references/resources.md`, `../references/material-design.md`

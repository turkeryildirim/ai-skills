---
name: kotlin-architecture-guide
description: Kotlin architecture patterns (Android, Kotlin Multiplatform, and backend), concurrency models, DI systems, and common anti-patterns for architectural analysis.
type: reference
---

# Kotlin Architecture Guide

Reference for analyzing Kotlin projects — Android apps, Kotlin Multiplatform (KMP) codebases, Ktor, and Spring Boot backends.

## Maturity Levels

| Level | Signals |
|-------|---------|
| **Level 1** | Single flat package / `:app` monolith, direct DB/network queries in UI/Activities, global mutable state variables, no DI, blocking I/O on UI thread. |
| **Level 2** | Split into standard packages (`ui`, `data`), but business logic exists directly inside ViewModels or Activities. Unmanaged `GlobalScope` coroutines. |
| **Level 3** | Clear MVVM/MVI separation, constructor dependency injection (Hilt/Koin), ViewModel scope utilized, `StateFlow` used for exposing UI state. |
| **Level 4** | Multi-module Gradle structure (`:core`, `:feature`), Clean Architecture layer division (UI → UseCase → Repository), injected coroutine dispatchers, unit tests with MockK. |
| **Level 5** | Clean KMP layout separating `commonMain` logic from platform specifics, fully reactive flow pipelines, DI scopes managed correctly, robust test coverage (>70%) with Turbine. |

---

## Layout Pattern Comparison

### Android / KMP Single Module (Appropriate: small apps, prototypes)
```
app/
├── src/main/kotlin/com/myapp/
│   ├── data/                 → API clients, repositories, Room DB
│   ├── domain/               → Domain models
│   ├── ui/                   → ViewModels, Compose screens
│   └── App.kt                → Application class (DI entry point)
├── build.gradle.kts
└── settings.gradle.kts

✅ Acceptable for: prototypes, small apps (<10 screens)
❌ Problem when: the application grows, build times slow down, boundaries become blurred.
```

### Multi-module / Feature-based Layout (Recommended: complex apps, team environments)
```
myapp/
├── gradle/libs.versions.toml → Central dependency catalog
├── core/
│   ├── database/             → Room database definitions
│   ├── network/              → Ktor HTTP / Retrofit configurations
│   └── designsystem/         → Shared UI theme, buttons, typography
├── domain/                   → Interfaces, models, UseCases (no Android imports)
├── data/                     → Implements Domain Repositories
├── feature/
│   ├── auth/                 → Auth screens, ViewModels, DI Module
│   └── home/                 → Home screens, ViewModels, DI Module
├── app/                      → Thin launcher module, binds other modules together
├── build.gradle.kts
└── settings.gradle.kts
```

### Kotlin Multiplatform (KMP) Shared Module Layout
```
shared/
├── src/
│   ├── commonMain/           → Main business logic, domain, data APIs
│   │   └── kotlin/           → Shared Kotlin code, flows, models
│   ├── androidMain/          → Android-specific code (e.g. database setup, cryptography)
│   └── iosMain/              → iOS-specific code (Keychain, background task hooks)
├── build.gradle.kts
```

---

## Dependency Injection (DI) Assessment

### Hilt (Google Recommended for Android)
```
✅ Preferred for: Android-first projects, standard MVVM/MVI.
Detection: @HiltAndroidApp, @HiltViewModel in imports/annotations.
Healthy: Injection done via constructor, modules define binding interfaces.
Watch for: Injecting Android Activity Context into singletons or repositories.
```

### Koin (Lightweight Service Locator / DI)
```
✅ Preferred for: Kotlin Multiplatform (KMP), Ktor backend, swift setup.
Detection: org.koin.core, startKoin, get() inside builders.
Healthy: Module definitions grouped by feature, constructor injection matches.
Watch for: Large projects with unresolved runtime dependencies (no compile-time safety).
```

### Dagger 2
```
✅ Preferred for: Large, complex legacy Android projects with strict performance/compile-time requirements.
Detection: @Component, @Subcomponent, @Inject.
Watch for: Extreme boilerplate, complex subcomponent trees that slow down onboarding.
```

---

## Coroutines & Flow Patterns

### Reactive State Exposure
```kotlin
// ✅ Correct: Exposing UI state using read-only StateFlow
class ProductViewModel(private val repository: ProductRepository) : ViewModel() {
    private val _uiState = MutableStateFlow<ProductUiState>(ProductUiState.Loading)
    val uiState: StateFlow<ProductUiState> = _uiState.asStateFlow()

    init {
        loadProducts()
    }

    private fun loadProducts() {
        viewModelScope.launch {
            try {
                val data = repository.getProducts()
                _uiState.value = ProductUiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = ProductUiState.Error(e.localizedMessage ?: "Error")
            }
        }
    }
}
```

### StateFlow vs SharedFlow vs Channel

| Concept | Nature | Typical Use Case |
|---------|--------|------------------|
| **StateFlow** | State Container (has value, repeats last emission to new subscribers) | UI state binding, continuous reactive properties |
| **SharedFlow** | Event Stream (hot stream, emits to multiple listeners) | Navigation actions, toasts, analytics triggers |
| **Channel** | Pipe/Queue (point-to-point, consumed by one listener) | Single-time events (e.g., show confirmation dialog once) |

---

## Testing Architecture Benchmarks

```
✅ Healthy Kotlin testing layout:
domain/src/test/          → pure JUnit 5 / Kotest unit tests (no framework mocks needed)
data/src/test/            → Repository tests utilizing MockK or fake data sources
feature/*/src/test/       → ViewModel unit tests utilizing runTest and Turbine for flow assertions

Test patterns:
- Using Turbine to test Flow states:
  viewModel.uiState.test {
      assertEquals(UiState.Loading, awaitItem())
      assertEquals(UiState.Success(data), awaitItem())
  }

❌ Warning signals:
- Using real Android Context in local unit tests without Robolectric.
- Broadly launching coroutines in tests without overriding the Main dispatcher (fails with "Module with the Main dispatcher had failed to initialize").
- Launching heavy integration tests under `src/test/` instead of separating them.
```

---

## Common Anti-Patterns

| Anti-Pattern | Signs | Impact |
|-------------|-------|--------|
| **runBlocking Monolith** | calling `runBlocking` inside ViewModels, Android events, or Ktor routes | Freezes the active thread, leading to UI freezes (ANRs) or server throughput degradation |
| **GlobalScope Abuse** | `GlobalScope.launch { ... }` in normal business actions | Tasks run out of control, causing memory leaks and uncatchable exceptions |
| **Platform Leakage** | `import android.content.Context` inside Domain or UseCase classes | Breaks KMP compatibility, makes local unit tests slow and difficult |
| **Service Locator Dependency** | calling `startKoin` or `DaggerComponent` directly inside random classes to get instances | Obfuscates dependencies, prevents proper interface mocking during tests |
| **Direct DB read in Compose** | Calling DAO queries inside Composable blocks without Flow/LiveData | Triggers disk reads on every recomposition (60fps), causing severe UI lag |
| **Missing Flow cancellation** | Collecting Flows in UI without lifecycle scoping (`repeatOnLifecycle`) | Flow collection runs continuously even when the app is in the background, wasting CPU/Battery |
| **Hardcoded Dispatchers** | Directly using `Dispatchers.IO` or `Dispatchers.Default` inside class methods | Prevents overriding dispatchers in unit tests, causing flaky or asynchronous race conditions |

---

## Integration with Kotlin & Kotlin-Tester Skills

When analyzing or refactoring codebases, map architectural issues back to these specific rules within the **kotlin** and **kotlin-tester** skills for deep implementation guidance.

### Architecture & Modularity (`arch-`)
- **Domain Independence**: Ensure the domain layer is pure Kotlin. Violation flags `arch-domain-pure-kotlin`.
- **Interface Segregation**: Repositories must define their interfaces in the domain module. Violation flags `arch-repo-iface-in-domain`.
- **Entity Leakage**: Database entities or API DTOs should not leak into the UI. Violation flags `arch-no-entity-in-ui`.
- **Modularity Discipline**: Feature modules should never have cross-dependencies. Violation flags `arch-no-feature-cross-dep`.

### Coroutines & Flow (`coro-` & `ctest-`)
- **Scope Safety**: Prevent use of unmanaged scopes. Violation flags `coro-no-globalscope` and `coro-no-runblocking`.
- **Context Swapping**: Ensure dispatchers are injected rather than hardcoded. Violation flags `coro-inject-dispatchers` and `test-main-dispatcher-rule`.
- **Flow Assertions**: Validate reactive UI state using Turbine in unit tests. Violation flags `ctest-turbine-for-flow`.

### Compose UI & Framework (`compose-`)
- **Lifecycle Collection**: Expose read-only `StateFlow` and collect via lifecycle. Violation flags `coro-lifecycle-collection` and `compose-remember-flow`.
- **ViewModel Decoupling**: Composable UI components must not instantiate or directly hold view models. Violation flags `compose-no-vm-in-composable`.
- **State Hoisting**: Keep Compose UI components stateless and testable. Violation flags `compose-no-side-effects`.


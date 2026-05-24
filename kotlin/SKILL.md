---
name: kotlin
description: Kotlin modern patterns, coroutines, Clean Architecture, Compose, Hilt, and Material Design 3 for Android and KMP. Use when building, reviewing, or auditing Android/KMP apps. Triggers on "Kotlin", "Android", "Compose", "coroutine", "Hilt", "Room", "MVVM", "MVI", "Clean Architecture".
model: inherit
---

# Kotlin Best Practices

Modern Kotlin patterns for Android and Kotlin Multiplatform — coroutines, Clean Architecture, Jetpack Compose, Material Design 3, and build configuration. Focused on performance, testability, and maintainability.

## Specialized Agents

| Agent | Role | Focus |
|-------|------|-------|
| **kotlin-pro** | Kotlin Expert | Compose UI, state management, Material Design 3, HIG. |
| **kotlin-coroutines-pro** | Coroutines Expert | Structured concurrency, Flow, StateFlow, error handling. |
| **kotlin-build-pro** | Build Expert | Gradle, Version Catalogs, Convention Plugins, CI/CD. |
| **kotlin-conventions-pro** | Kotlin Conventions | Idiomatic code, null safety, DSL builders, collections. |

## When to Use

Reference these guidelines when:
- Building or refactoring Android/KMP applications
- Managing async operations with coroutines, Flow, StateFlow
- Designing clean architecture layers (domain, data, presentation)
- Building UI with Jetpack Compose and Material Design 3
- Configuring Gradle builds, version catalogs, or convention plugins
- Implementing navigation with Coordinator pattern
- Setting up dependency injection with Hilt or Koin
- Implementing persistence with Room or SQLDelight
- Writing networking layer with Retrofit or Ktor
- Ensuring accessibility and Material Design compliance

## Step 1: Detect Target Environment

**Always check the project's target SDK, Kotlin version, and Compose version.**

Check `build.gradle.kts` or `libs.versions.toml`:
```kotlin
// build.gradle.kts
android {
    compileSdk = 35
    defaultConfig { minSdk = 26 }
}
kotlinOptions { jvmTarget = "17" }
```

### Feature Availability by Version

| Feature | Version |
|---------|---------|
| Coroutines Flow, StateFlow | Kotlin 1.4+ |
| Compose Compiler (stable) | Kotlin 1.9+ / Compose BOM 2024+ |
| `@JvmInline value class` | Kotlin 1.5+ |
| Sealed interfaces | Kotlin 1.5+ |
| KSP (replace KAPT) | Kotlin 1.7+ |
| Compose Material 3 | Compose BOM 2023+ |
| NonCancellable cleanup | Coroutines 1.6+ |

## Step 2: Choose the Right Guidance Set

- Load `references/kotlin-conventions.md` before reviewing code style, null safety, or DSL patterns.
- Load `references/coroutines.md` before changing async operations, Flow, or StateFlow.
- Load `references/architecture.md` before structuring modules, UseCases, or Repositories.
- Load `references/compose-ui.md` before building Compose screens or state management.
- Load `references/navigation-coordinator.md` before implementing app navigation flows.
- Load `references/networking.md` before working with Retrofit or Ktor.
- Load `references/persistence.md` before touching Room or SQLDelight.
- Load `references/dependency-injection.md` before configuring Hilt or Koin.
- Load `references/build-configuration.md` before modifying Gradle or version catalogs.
- Load `references/build-convention-plugins.md` before creating convention plugins.
- Load `kotlin-tester` before authoring tests so implementation and test guidance stay aligned.

## Core Directives

### MUST DO

- **Coroutines:** Use structured concurrency. Prefer `viewModelScope` / `lifecycleScope`. Inject dispatchers.
- **State:** Use `StateFlow` + `collectAsStateWithLifecycle()` for UI state. Single `UiState` data class per screen.
- **Architecture:** Keep `domain` layer pure Kotlin. Map entities/DTOs to domain models. Extract business logic to UseCases.
- **Compose:** Use `Modifier.testTag` for testing. `LaunchedEffect` for side effects. `remember` for state. `@Stable` for custom types.
- **Navigation:** Use Coordinator pattern for flow logic. Navigate via lambdas, not from ViewModel.
- **Networking:** Always validate HTTP status codes. Use protocol-based API clients for testability.
- **Security:** Never store tokens in SharedPreferences. Use EncryptedSharedPreferences or Keychain.
- **Build:** Use Version Catalogs (`libs.versions.toml`). Prefer KSP over KAPT. Use Convention Plugins for multi-module.
- **Error Handling:** Use `Result<T>` or sealed error types. Rethrow `CancellationException`. Use `require`/`check` for preconditions.
- **Immutability:** Prefer `val`, immutable collections, `data class` with `copy()`. Use `@JvmInline value class` for type safety.

### MUST NOT DO

- **GlobalScope:** Never use `GlobalScope` in production code.
- **runBlocking:** Never use `runBlocking` on main thread.
- **!! Operator:** Never use `!!` except with explicit comment on truly impossible null.
- **CancellationException:** Never catch and swallow `CancellationException` — always rethrow.
- **Hardcoded Dispatchers:** Never hardcode `Dispatchers.IO` in classes — inject for testability.
- **Entity Leakage:** Never expose DB entities or DTOs to UI layer — always map to domain models.
- **Business in ViewModel:** Avoid putting business logic in ViewModel — extract to UseCases.
- **Feature Cross-Dependencies:** Feature modules must never depend on other feature modules.
- **Live Backend in Tests:** Never run tests against live backend — use MockWebServer or fakes.
- **Thread.sleep:** Never use `Thread.sleep` in tests — use proper async synchronization.

## Category Index — When to Load Which Reference

| # | Category | Impact | Load when… | Reference |
|--:|----------|:------:|------------|-----------|
| 1 | Kotlin Conventions | CRITICAL | Null safety, DSL, collections, scope functions | [`references/kotlin-conventions.md`](references/kotlin-conventions.md) |
| 2 | Coroutines | CRITICAL | Flow, StateFlow, SharedFlow, cancellation | [`references/coroutines.md`](references/coroutines.md) |
| 3 | Architecture | CRITICAL | Modules, UseCases, Repositories, Clean Arch | [`references/architecture.md`](references/architecture.md) |
| 4 | Compose UI | HIGH | Screens, state, theming, Material 3 | [`references/compose-ui.md`](references/compose-ui.md) |
| 5 | Networking | HIGH | Retrofit, Ktor, error handling, retry | [`references/networking.md`](references/networking.md) |
| 6 | Navigation | HIGH | Coordinator pattern, flow logic, deep links | [`references/navigation-coordinator.md`](references/navigation-coordinator.md) |
| 7 | Dependency Injection | HIGH | Hilt, Koin, scoping, testability | [`references/dependency-injection.md`](references/dependency-injection.md) |
| 8 | Build Configuration | HIGH | Gradle, Version Catalogs, flavors, optimization | [`references/build-configuration.md`](references/build-configuration.md) |
| 9 | Convention Plugins | HIGH | Multi-module build logic, plugin creation | [`references/build-convention-plugins.md`](references/build-convention-plugins.md) |
| 10 | Persistence | MEDIUM | Room, SQLDelight, mappers, migrations | [`references/persistence.md`](references/persistence.md) |
| 11 | Material Design 3 | MEDIUM | M3 components, spacing, typography, accessibility | [`references/material-design.md`](references/material-design.md) |
| 12 | Resources | MEDIUM | Naming, icons, reserved names, RTL | [`references/resources.md`](references/resources.md) |
| 13 | Project Setup | MEDIUM | New project, required files, SDK config | [`references/project-setup.md`](references/project-setup.md) |
| 14 | CI/CD | MEDIUM | GitHub Actions, GMD, coverage, pipelines | [`references/ci-cd.md`](references/ci-cd.md) |
| 15 | Code Quality | MEDIUM | Detekt, Ktlint, static analysis, CI enforcement | [`references/code-quality.md`](references/code-quality.md) |

## Rule Index

### 1. Kotlin Patterns (`kt-`) — CRITICAL
`kt-no-force-unwrap` · `kt-immutable-data-class` · `kt-sealed-interface` · `kt-default-params` · `kt-no-exception-control-flow` · `kt-sequences-large-collections` · `kt-no-mutable-public` · `kt-value-classes` · `kt-naming-conventions` · `kt-server-response-nullable` · `kt-no-lateinit-unsafe` · `kt-lambda-return-label` · `kt-lifecycle-paired-observer` · `kt-no-nested-scope-functions` · `kt-handle-java-platform-types` · `kt-value-class-validation` · `kt-logging-levels`

### 2. Coroutines (`coro-`) — CRITICAL
`coro-no-globalscope` · `coro-inject-dispatchers` · `coro-supervisor-job` · `coro-no-cancel-swallow` · `coro-no-runblocking` · `coro-lifecycle-collection` · `coro-single-uistate` · `coro-cooperative-cancellation` · `coro-callback-flow-cleanup` · `coro-no-mutable-in-stateflow` · `coro-no-flow-on-main`

### 3. Architecture (`arch-`) — CRITICAL
`arch-domain-pure-kotlin` · `arch-no-entity-in-ui` · `arch-logic-in-usecases` · `arch-no-fat-repository` · `arch-no-circular-deps` · `arch-no-feature-cross-dep` · `arch-no-component-cross-dep` · `arch-no-dependency-on-app` · `arch-no-business-in-feature` · `arch-no-ui-in-component` · `arch-di-only-in-app` · `arch-repo-iface-in-domain`

### 4. Navigation (`nav-`) — HIGH
`nav-coordinator-owns-navigation` · `nav-stateless-coordinator` · `nav-lambda-callbacks` · `nav-no-god-coordinator` · `nav-navigator-separation` · `nav-coroutine-scoping`

### 5. Compose (`compose-`) — HIGH
`compose-stable-params` · `compose-no-vm-in-composable` · `compose-launched-effect-for-async` · `compose-no-side-effects` · `compose-remember-flow` · `compose-testtag-for-testing`

### 6. Networking (`net-`) — HIGH
`net-status-validation` · `net-no-main-thread-calls` · `net-protocol-client` · `net-no-completion-handlers` · `net-retry-with-backoff`

### 7. Build (`gradle-`, `conv-`) — HIGH
`gradle-version-catalog` · `gradle-ksp-over-kapt` · `gradle-implementation-over-api` · `conv-no-duplicate-config` · `conv-no-hardcoded-versions` · `conv-one-concern-per-plugin` · `conv-shared-logic-extracted`

### 8. Security (`sec-`) — HIGH
`sec-no-tokens-in-sharedprefs` · `sec-encrypted-storage`

### 9. Resources (`res-`) — MEDIUM
`res-no-reserved-names` · `res-naming-conventions`

## Validation Checklist

- [ ] Kotlin naming conventions followed (PascalCase, camelCase, SCREAMING_SNAKE)
- [ ] No `!!` operator (except with documented justification)
- [ ] `data class` fields are `val`, not `var`
- [ ] Sealed interfaces used for restricted hierarchies
- [ ] Structured concurrency (no `GlobalScope`, no `runBlocking` on main)
- [ ] Dispatchers injected, not hardcoded
- [ ] `CancellationException` always rethrown
- [ ] Single `UiState` data class per screen
- [ ] `collectAsStateWithLifecycle()` used in Compose
- [ ] Domain layer contains no Android framework imports
- [ ] DB entities/DTOs mapped to domain models before reaching UI
- [ ] Business logic in UseCases, not ViewModels
- [ ] Feature modules have no cross-dependencies
- [ ] All dependencies declared in `libs.versions.toml`
- [ ] HTTP status codes validated before decoding
- [ ] Tokens stored in encrypted storage, not SharedPreferences
- [ ] `Modifier.testTag` on interactive Compose elements
- [ ] Material Design 3 spacing grid (8dp) and touch targets (48dp)
- [ ] Version catalog used (no hardcoded versions in build scripts)
- [ ] Coordinator pattern used for navigation flow logic

## External References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [Android Developer Guide](https://developer.android.com/)
- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Jetpack Compose Documentation](https://developer.android.com/develop/ui/compose)
- [Material Design 3](https://m3.material.io/)
- [Hilt Dependency Injection](https://dagger.dev/hilt/)
- [Room Persistence](https://developer.android.com/training/data-storage/room)
- [Gradle Version Catalogs](https://docs.gradle.org/current/userguide/version_catalogs.html)
- [Android Testing Guide](https://developer.android.com/training/testing)

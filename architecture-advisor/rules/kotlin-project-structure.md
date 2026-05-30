---
title: Kotlin Project Structure Analysis
impact: HIGH
impactDescription: "Monolithic layouts, poor dependency injection, and leaking platform dependencies into domain layers degrade Kotlin application modularity and testability"
tags: kotlin, project-structure, dependency-injection, gradle, layering
---

## Kotlin Project Structure Analysis

**Impact: HIGH (Monolithic layouts, poor dependency injection, and leaking platform dependencies into domain layers degrade Kotlin application modularity and testability)**

Kotlin applications across mobile (Android), cross-platform (Kotlin Multiplatform), and backend (Ktor, Spring Boot) require clear separation of concerns, strong encapsulation, and solid dependency injection. Tight coupling, global singletons, and poor packaging lead to unmaintainable, untestable codebases.

## Incorrect

```kotlin
// ❌ Manual singleton-based service locator and leaking platform dependencies

// MainApplication.kt - Leaks context and exposes global database
class MainApplication : Application() {
    companion object {
        lateinit var instance: MainApplication
        lateinit var database: AppDatabase // ❌ Global database reference
    }

    override fun onCreate() {
        super.onCreate()
        instance = this
        database = Room.databaseBuilder(this, AppDatabase::class.java, "db").build()
    }
}

// UserRepository.kt - Tightly coupled to Android Context and global state
class UserRepository {
    private val db = MainApplication.database // ❌ Hardcoded dependency on global singleton
    private val context = MainApplication.instance.applicationContext // ❌ Hardcoded platform dependency

    fun getUserName(userId: String): String {
        // Leaking UI/Platform logic (e.g., getting string resource in repository)
        val defaultName = context.getString(R.string.default_user_name) // ❌ UI resource in repository
        val user = db.userDao().getUserById(userId)
        return user?.name ?: defaultName
    }
}

// UserViewModel.kt - Instantiates repository manually
class UserViewModel : ViewModel() {
    private val userRepository = UserRepository() // ❌ Instantiated manually, untestable
}
```

## Correct

```
// ✅ Multi-module Clean Architecture Layout for Android/KMP

myproject/
├── build.gradle.kts
├── settings.gradle.kts
├── gradle/
│   └── libs.versions.toml    → Centralized Dependency Management (Version Catalog)
├── core/
│   ├── database/             → Room/SQLDelight setup
│   ├── network/              → Ktor Client/Retrofit setup
│   └── model/                → Pure domain models
├── data/                     → Implements Domain Repositories, depends on core/database, core/network
│   └── src/main/kotlin/.../UserRepositoryImpl.kt
├── domain/                   → Pure Kotlin, zero platform/framework dependencies
│   └── src/main/kotlin/
│       ├── model/            → Pure entities
│       ├── repository/       → Repository Interfaces
│       └── usecase/          → Interactors/Use Cases
└── feature/
    └── profile/              → Feature module: ViewModels, UI (Compose/Views)
        └── src/main/kotlin/.../ProfileViewModel.kt
```

```kotlin
// ✅ Constructor injection with interface separation

// domain/repository/UserRepository.kt (Pure Kotlin Interface)
interface UserRepository {
    suspend fun getUserName(userId: String): String
}

// data/repository/UserRepositoryImpl.kt (Data Implementation)
class UserRepositoryImpl @Inject constructor(
    private val userDao: UserDao,
    private val resourceProvider: ResourceProvider // ✅ Abstracted platform resource retrieval
) : UserRepository {
    override suspend fun getUserName(userId: String): String {
        val defaultName = resourceProvider.getString("default_user_name") // ✅ Abstracted
        val user = userDao.getUserById(userId)
        return user?.name ?: defaultName
    }
}

// feature/profile/ProfileViewModel.kt (Injected ViewModel)
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository // ✅ Injected interface dependency
) : ViewModel() {
    // UI Logic uses userRepository cleanly
}
```

## Structure Compliance Assessment

```
CRITICAL violations:
├── global mutable variables used to pass state between screens or layers
├── Android 'Context' passed as static reference or stored in ViewModels/Repositories
└── circular project module dependencies in settings.gradle.kts

HIGH violations:
├── No DI framework used in projects with >10 screens/classes (manual newing of classes)
├── Database (Room/SQLDelight) or HTTP queries executed directly inside ViewModels or UI Compose code
└── Business/Domain models importing UI-specific libraries (Compose, UIKit) or platform libraries

MEDIUM violations:
├── `settings.gradle.kts` declaring a single flat `:app` module for a large multi-feature app
├── Hardcoded dependency creation (e.g. `val repo = UserRepository()`) inside ViewModels
└── Direct import of platform-specific code in commonMain directories of a KMP project

LOW violations:
├── Hardcoded string resources or dimensions inside Repository or Domain layers
└── Missing gradle Version Catalog (`gradle/libs.versions.toml`) in multi-module projects
```

## Directory Signals

```
✅ Healthy Kotlin project structure:
domain/                 → Pure Kotlin library, no android/spring/ktor annotations
data/repository/        → Pure repository implementations, calling network & database interfaces
feature/*/ui/           → Compose layouts, UI-only models, ViewModel bindings
gradle/libs.versions.toml → Dependency definitions managed in one place

❌ Warning signals:
app/src/main/java/...   → Monolithic flat package structure with mixed files (ViewModel, Repo, Activity in one place)
domain/import android.* → Leaking Android APIs into pure business logic layer
val repo = Repo()       → Service Locator or manual instantiation preventing unit tests
```

## Why

- **Platform Decoupling**: Keeping domain layers platform-independent ensures they can be easily reused in KMP (Kotlin Multiplatform) for iOS, Android, and Web, and speeds up unit testing as they don't require instrumented Android environments.
- **Dependency Injection**: Constructor dependency injection enables clean unit testing. We can easily swap real database implementations with mocks (like MockK) during testing.
- **Gradle Modularity**: Feature-by-module separation allows gradle to compile modules in parallel, reducing incremental build times and enforcing API boundaries between different features.

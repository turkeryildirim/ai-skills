# Gradle Build Configuration

Gradle Kotlin DSL build configuration for Android multi-module projects. Covers version catalogs, dependency management, build performance, and compatibility matrices.

## 1. Version Catalog (libs.versions.toml)

```toml
[versions]
kotlin = "2.0.21"
agp = "8.7.3"
compose-bom = "2024.12.01"
retrofit = "2.11.0"
hilt = "2.53.1"
coroutines = "1.9.0"

[libraries]
kotlinx-coroutines-core = { group = "org.jetbrains.kotlinx", name = "kotlinx-coroutines-core", version.ref = "coroutines" }
kotlinx-coroutines-android = { group = "org.jetbrains.kotlinx", name = "kotlinx-coroutines-android", version.ref = "coroutines" }

retrofit-core = { group = "com.squareup.retrofit2", name = "retrofit", version.ref = "retrofit" }
retrofit-gson = { group = "com.squareup.retrofit2", name = "converter-gson", version.ref = "retrofit" }
okhttp-logging = { group = "com.squareup.okhttp3", name = "logging-interceptor", version = "4.12.0" }

hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler = { group = "com.google.dagger", name = "hilt-android-compiler", version.ref = "hilt" }

compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-ui = { group = "androidx.compose.ui", name = "ui" }
compose-material3 = { group = "androidx.compose.material3", name = "material3" }
compose-ui-tooling = { group = "androidx.compose.ui", name = "ui-tooling" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
android-library = { id = "com.android.library", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }

[bundles]
retrofit = ["retrofit-core", "retrofit-gson", "okhttp-logging"]
coroutines = ["kotlinx-coroutines-core", "kotlinx-coroutines-android"]
```

| Section | Purpose | Example |
|---|---|---|
| `[versions]` | Single source of truth for version strings | `kotlin = "2.0.21"` |
| `[libraries]` | Dependency coordinates with `group`, `name`, `version`/`version.ref` | `retrofit-core = { ... }` |
| `[plugins]` | Gradle plugin declarations | `hilt = { id = "...", version.ref = "hilt" }` |
| `[bundles]` | Groups of libraries applied together | `retrofit = ["retrofit-core", "retrofit-gson"]` |

## 2. Usage in build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.hilt)
}

dependencies {
    implementation(libs.bundles.retrofit)
    implementation(libs.bundles.coroutines)
    implementation(libs.hilt.android)
    ksp(libs.hilt.compiler)

    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.compose.material3)
    debugImplementation(libs.compose.ui.tooling)
}
```

- Type-safe accessors: `libs.retrofit.core` maps to the `retrofit-core` entry.
- Bundles: `libs.bundles.retrofit` applies all libraries in the bundle.
- BOM: `platform(libs.compose.bom)` sets versions for all Compose libraries — do NOT specify versions on individual Compose libraries.

## 3. BOM Management

```kotlin
dependencies {
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.compose.material3)
    implementation(libs.compose.foundation)
    androidTestImplementation(platform(libs.compose.bom))
}
```

When using a BOM (Bill of Materials), child libraries must NOT have their own version. The BOM controls versions for all members.

## 4. App Module build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.hilt)
    alias(libs.plugins.ksp)
}

android {
    namespace = "com.example.app"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "com.example.app.HiltTestRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
        }
        debug {
            isMinifyEnabled = false
            applicationIdSuffix = ".debug"
        }
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation(project(":core:data"))
    implementation(project(":core:domain"))
    implementation(project(":feature:home"))
    implementation(project(":feature:profile"))

    implementation(libs.bundles.retrofit)
    implementation(libs.hilt.android)
    ksp(libs.hilt.compiler)

    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.compose.material3)

    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.test.ext.junit)
}
```

## 5. Library Module build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
}

android {
    namespace = "com.example.core.domain"
    compileSdk = 35

    defaultConfig {
        minSdk = 26
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation(libs.kotlinx.coroutines.core)
    testImplementation(libs.junit)
}
```

Library modules should be minimal. Use convention plugins to avoid repeating common configuration across modules.

## 6. Dependency Scopes

| Scope | Available at | Transitive | Use Case |
|---|---|---|---|
| `implementation` | Compile + runtime of current module | No (to consumers) | Most dependencies |
| `api` | Compile + runtime of current + consumer modules | Yes | Dependencies exposed in public API |
| `compileOnly` | Compile only | No | Annotations, code generators (Hilt `@Inject`) |
| `runtimeOnly` | Runtime only | No | JNI libraries, logging backends |
| `ksp` | Annotation processing | No | Hilt compiler, Room compiler |
| `testImplementation` | Test compile + runtime | No | JUnit, Mockito, Turbine |
| `androidTestImplementation` | Android test compile + runtime | No | Espresso, Compose UI tests |
| `debugImplementation` | Debug build only | No | Compose UI tooling, LeakCanary |

## 7. Dependency Conflict Resolution

```kotlin
configurations.all {
    resolutionStrategy {
        force("com.squareup.okhttp3:okhttp:4.12.0")
    }
}

dependencies {
    implementation("some.library") {
        exclude(group = "com.squareup.okhttp3", module = "okhttp")
    }
}
```

| Command | Purpose |
|---|---|
| `./gradlew :app:dependencies` | View full dependency tree |
| `./gradlew :app:dependencies --configuration releaseRuntimeClasspath` | View specific configuration |
| `resolutionStrategy.force` | Override a transitive version |
| `exclude` | Remove a specific transitive dependency |

## 8. Build Performance (gradle.properties)

```properties
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
org.gradle.jvmargs=-Xmx4g -XX:+UseParallelGC
android.useAndroidX=true
android.nonTransitiveRClass=true
kotlin.code.style=official
```

| Property | Effect |
|---|---|
| `org.gradle.parallel=true` | Run independent projects in parallel |
| `org.gradle.caching=true` | Reuse outputs from previous builds |
| `org.gradle.configuration-cache=true` | Cache configuration phase results |
| `org.gradle.jvmargs=-Xmx4g` | Allocate 4 GB heap for Gradle daemon |
| `android.nonTransitiveRClass=true` | Only include R class resources from own module |

## 9. Compatibility Matrix

### Kotlin ↔ Compose Compiler

| Kotlin | Compose Compiler |
|---|---|
| 2.0.21 | 1.7.5 |
| 2.0.20 | 1.7.4 |
| 1.9.25 | 1.5.15 |
| 1.9.24 | 1.5.14 |

Starting with Kotlin 2.0, the Compose Compiler is bundled with the Kotlin plugin. Use `org.jetbrains.kotlin.plugin.compose` instead of `androidx.compose.compiler`.

### AGP ↔ Gradle

| AGP | Min Gradle | Max Gradle |
|---|---|---|
| 8.7.x | 8.9 | 8.x |
| 8.6.x | 8.7 | 8.x |
| 8.5.x | 8.7 | 8.x |

### AGP ↔ Kotlin

| AGP | Max Kotlin |
|---|---|
| 8.7.x | 2.0.21 |
| 8.6.x | 2.0.20 |
| 8.5.x | 1.9.25 |

Always check [the compatibility table](https://developer.android.com/build/kotlin-support) before upgrading.

## 10. Common Gradle Commands

| Command | Purpose |
|---|---|
| `./gradlew assembleDebug` | Build debug APK |
| `./gradlew assembleRelease` | Build release APK |
| `./gradlew installDebug` | Build and install debug APK on device |
| `./gradlew :app:dependencies` | View dependency tree |
| `./gradlew clean` | Clean build outputs |
| `./gradlew --stacktrace` | Run with full stack traces |
| `./gradlew --refresh-dependencies` | Force dependency re-download |
| `./gradlew build --scan` | Build with Gradle scan report |
| `./gradlew lint` | Run Android Lint |
| `./gradlew test` | Run all unit tests |
| `./gradlew connectedAndroidTest` | Run instrumented tests |

## 11. Kotlin DSL Tips

### Build Types

```kotlin
android {
    buildTypes {
        debug {
            isMinifyEnabled = false
            applicationIdSuffix = ".debug"
            buildConfigField("String", "BASE_URL", "\"https://api-staging.example.com\"")
        }
        release {
            isMinifyEnabled = true
            buildConfigField("String", "BASE_URL", "\"https://api.example.com\"")
        }
    }
}
```

### Product Flavors

```kotlin
android {
    flavorDimensions += "environment"

    productFlavors {
        create("staging") {
            dimension = "environment"
            applicationIdSuffix = ".staging"
        }
        create("production") {
            dimension = "environment"
        }
    }
}
```

### Source Sets

```kotlin
android {
    sourceSets {
        getByName("main") {
            java.srcDirs("src/main/kotlin")
        }
        getByName("test") {
            java.srcDirs("src/test/kotlin")
        }
    }
}
```

## 12. Build Error Diagnosis

| Error Keyword | Cause | Fix |
|---|---|---|
| `Duplicate class` | Same class from two dependencies | Exclude duplicate or use `resolutionStrategy.force` |
| `Manifest merger failed` | Conflicting manifest entries | Add `tools:replace` or fix conflicting attributes |
| `Compilation error` | Kotlin/Java source issue | Run with `--stacktrace` for details |
| `Cannot resolve` | Missing dependency or repository | Check `libs.versions.toml` and `settings.gradle.kts` repositories |
| `Namespace not specified` | Missing `namespace` in `android {}` | Add `namespace = "com.example.module"` |
| `Incompatible AGP/Kotlin` | Version mismatch | Check compatibility matrix above |
| `Configuration cache` | Plugin not compatible | Check plugin docs or disable temporarily |
| `OutOfMemoryError` | JVM heap too small | Increase `org.gradle.jvmargs` heap size |

## 13. Debugging Commands

```bash
./gradlew clean
./gradlew :app:dependencies --configuration releaseRuntimeClasspath
./gradlew assembleDebug --stacktrace
./gradlew assembleDebug --info
./gradlew --refresh-dependencies
./gradlew build --scan
```

## Cross References

- Related rules: `gradle-version-catalog`, `gradle-no-hardcoded-versions`, `gradle-bom-usage`, `gradle-dependency-scopes`, `gradle-performance`
- Related references: [`build-convention-plugins.md`](build-convention-plugins.md), [`dependency-injection.md`](dependency-injection.md)

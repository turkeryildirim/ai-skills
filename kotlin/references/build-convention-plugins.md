# Convention Plugins for Multi-Module Projects

Gradle convention plugins eliminate duplicated build configuration across modules. This reference covers the `build-logic` pattern for Android projects with Kotlin DSL.

## Problem Statement

Without convention plugins, every module's `build.gradle.kts` repeats the same `android {}` block, Kotlin options, and dependency declarations. A 20-module project can have 20 nearly identical build files. When you need to update `compileSdk` or add a compiler flag, you must edit all 20 files.

Convention plugins centralize shared configuration into reusable plugins that modules apply with a single line.

## 1. Project Structure

```
project/
├── build-logic/
│   └── convention/
│       ├── build.gradle.kts
│       └── src/main/java/
│           ├── AndroidLibraryConventionPlugin.kt
│           ├── AndroidComposeConventionPlugin.kt
│           ├── AndroidUnitTestConventionPlugin.kt
│           └── KotlinAndroid.kt          (shared extension functions)
├── app/
│   └── build.gradle.kts                  (applies plugins)
├── core/data/
│   └── build.gradle.kts                  (applies plugins)
├── feature/home/
│   └── build.gradle.kts                  (applies plugins)
├── libs.versions.toml
└── settings.gradle.kts
```

## 2. settings.gradle.kts with includeBuild

```kotlin
pluginManagement {
    includeBuild("build-logic")
}

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "MyApp"
include(":app")
include(":core:data")
include(":core:domain")
include(":feature:home")
```

`includeBuild("build-logic")` makes convention plugins available to all modules via `plugins {}` block.

## 3. build-logic/convention/build.gradle.kts

```kotlin
plugins {
    `kotlin-dsl`
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

kotlin {
    jvmToolchain(17)
}

dependencies {
    compileOnly(libs.android.gradlePlugin)
    compileOnly(libs.kotlin.gradlePlugin)
    compileOnly(libs.compose.gradlePlugin)
}

tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile>().configureEach {
    kotlinOptions {
        jvmTarget = "17"
    }
}

gradlePlugin {
    plugins {
        register("androidLibrary") {
            id = "myapp.android.library"
            implementationClass = "AndroidLibraryConventionPlugin"
        }
        register("androidCompose") {
            id = "myapp.android.compose"
            implementationClass = "AndroidComposeConventionPlugin"
        }
        register("androidUnitTest") {
            id = "myapp.android.test"
            implementationClass = "AndroidUnitTestConventionPlugin"
        }
    }
}
```

- `kotlin-dsl` plugin enables Kotlin DSL for writing convention plugins.
- AGP and Kotlin Gradle plugins are `compileOnly` — they are provided by the consuming module.
- The `gradlePlugin {}` block registers each plugin with an `id` and `implementationClass`.

## 4. Creating a Plugin

### AndroidLibraryConventionPlugin

```kotlin
class AndroidLibraryConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply("com.android.library")
            pluginManager.apply("org.jetbrains.kotlin.android")

            extensions.configure<com.android.build.gradle.LibraryExtension> {
                configureKotlinAndroid(this)
                defaultConfig.targetSdk = 35
            }
        }
    }
}
```

### Shared Extension Function: configureKotlinAndroid

```kotlin
internal fun Project.configureKotlinAndroid(
    commonExtension: CommonExtension<*, *, *, *, *, *>,
) {
    commonExtension.apply {
        compileSdk = 35

        defaultConfig {
            minSdk = 26
        }

        compileOptions {
            sourceCompatibility = JavaVersion.VERSION_17
            targetCompatibility = JavaVersion.VERSION_17
        }

        tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile>().configureEach {
            kotlinOptions {
                jvmTarget = "17"
                val warningsAsErrors: String? by project
                allWarningsAsErrors = warningsAsErrors.toBoolean()
            }
        }
    }
}
```

### ComposeConventionPlugin

```kotlin
class AndroidComposeConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply("org.jetbrains.kotlin.plugin.compose")

            extensions.configure<CommonExtension<*, *, *, *, *, *>> {
                buildFeatures {
                    compose = true
                }
            }

            dependencies {
                val bom = libs.findLibrary("compose-bom").get()
                add("implementation", platform(bom))
                add("implementation", libs.findLibrary("compose-ui").get())
                add("implementation", libs.findLibrary("compose-material3").get())
                add("debugImplementation", libs.findLibrary("compose-ui-tooling").get())
            }
        }
    }
}
```

### UnitTestConventionPlugin

```kotlin
class AndroidUnitTestConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            extensions.configure<CommonExtension<*, *, *, *, *, *>> {
                testOptions {
                    unitTests {
                        isIncludeAndroidResources = true
                        isReturnDefaultValues = true
                    }
                }
            }

            dependencies {
                add("testImplementation", libs.findLibrary("junit").get())
                add("testImplementation", libs.findLibrary("kotlinx-coroutines-test").get())
                add("testImplementation", libs.findLibrary("mockk").get())
                add("testImplementation", libs.findLibrary("turbine").get())
            }
        }
    }
}
```

## 5. Plugin Registration Block

Each plugin must be registered in the `gradlePlugin {}` block of `build-logic/convention/build.gradle.kts`:

```kotlin
gradlePlugin {
    plugins {
        register("androidLibrary") {
            id = "myapp.android.library"
            implementationClass = "AndroidLibraryConventionPlugin"
        }
        register("androidCompose") {
            id = "myapp.android.compose"
            implementationClass = "AndroidComposeConventionPlugin"
        }
        register("androidUnitTest") {
            id = "myapp.android.test"
            implementationClass = "AndroidUnitTestConventionPlugin"
        }
    }
}
```

| Field | Purpose |
|---|---|
| `register("name")` | Internal Gradle name |
| `id` | The plugin ID used in `plugins {}` blocks |
| `implementationClass` | Fully qualified class name of the plugin |

## 6. Applying in Modules

After registering convention plugins, modules apply them with a single line:

### Library module (core/data)

```kotlin
plugins {
    id("myapp.android.library")
    id("myapp.android.test")
}

dependencies {
    implementation(project(":core:domain"))
    implementation(libs.retrofit.core)
}
```

### Feature module (feature/home)

```kotlin
plugins {
    id("myapp.android.library")
    id("myapp.android.compose")
    id("myapp.android.test")
}

dependencies {
    implementation(project(":core:domain"))
    implementation(project(":core:data"))
}
```

## 7. Accessing Version Catalog in Plugins

To access the version catalog smoothly inside convention plugins, define a helper extension property in a shared file within `build-logic` (e.g., `src/main/java/KotlinAndroid.kt`):

```kotlin
import org.gradle.api.artifacts.VersionCatalog
import org.gradle.api.artifacts.VersionCatalogsExtension
import org.gradle.api.Project
import org.gradle.kotlin.dsl.getByType

val Project.libs: VersionCatalog
    get() = extensions.getByType<VersionCatalogsExtension>().named("libs")
```

Then you can use it in your plugins like this:

```kotlin
libs.findLibrary("compose-ui").get()
libs.findPlugin("kotlin-android").get().pluginId
libs.findBundle("retrofit").get()
```

The version catalog (`libs.versions.toml`) is accessible inside convention plugins via `VersionCatalogsExtension`. Never hardcode version strings in plugins.

## 8. Rules Table

| Rule | Description |
|---|---|
| Never duplicate config | If two modules share configuration, extract a convention plugin |
| Never hardcode versions | Always read from `libs.versions.toml` via `VersionCatalogsExtension` |
| One plugin per concern | Separate library, compose, Hilt, and test into individual plugins |
| Shared logic in extensions | Put reusable `configureKotlinAndroid()` in a shared file |
| Use `pluginManager.apply` | Prefer `pluginManager.apply("id")` over `apply(plugin = ...)` |
| `compileOnly` for build deps | AGP, Kotlin, and Compose Gradle plugins must be `compileOnly` |

## 9. When to Create a New Plugin

Use this checklist before creating a new convention plugin:

- [ ] Is this configuration shared across 2+ modules?
- [ ] Does it represent a single concern (e.g., Compose, Hilt, testing)?
- [ ] Will it reduce duplication in `build.gradle.kts` files?
- [ ] Can it be tested independently?
- [ ] Is the plugin ID following the `myapp.android.<concern>` naming pattern?

If the answer is "yes" to all, create a new plugin. If the config is only in one module, keep it in that module's `build.gradle.kts`.

## Cross References

- Related rules: `conv-no-duplicate-config`, `conv-no-hardcoded-versions`, `conv-one-concern-per-plugin`, `conv-shared-logic-extracted`, `gradle-version-catalog`
- Related references: [`build-configuration.md`](build-configuration.md), [`dependency-injection.md`](dependency-injection.md)

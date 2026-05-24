# Project Setup & Initialization — Reference

## Project Scenario Assessment

Before taking action, assess the current project state.

| Scenario                | Detection                                    | Action                                                        |
| ----------------------- | -------------------------------------------- | -------------------------------------------------------------- |
| Empty directory         | No files present                             | Create full project from Android Studio template or CLI        |
| Has Gradle wrapper      | `gradlew` / `gradlew.bat` exist, no `settings.gradle.kts` | Verify wrapper version, create missing config files           |
| Android Studio project  | `settings.gradle.kts` + `build.gradle.kts` + `app/` exist | Validate structure, update dependencies, verify build          |
| Incomplete project      | Some files missing or misconfigured          | Audit against checklist below, create/fix missing pieces       |

### Detection Commands

```bash
dir gradlew* 2>nul
dir settings.gradle* 2>nul
dir build.gradle* 2>nul
dir app\build.gradle* 2>nul
```

---

## Required Files Checklist

### Minimal project tree for a single-module Jetpack Compose app.

```
project-root/
├── .gitignore
├── build.gradle.kts                    # Root build file
├── settings.gradle.kts                 # Project settings, module includes
├── gradle.properties                   # Gradle and JVM configuration
├── gradle/
│   └── wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties   # Gradle distribution version
├── gradlew
├── gradlew.bat
├── app/
│   ├── build.gradle.kts                # App module build configuration
│   ├── proguard-rules.pro              # R8 / ProGuard rules (optional)
│   └── src/
│       ├── main/
│       │   ├── AndroidManifest.xml
│       │   ├── java/com/example/app/
│       │   │   ├── MainActivity.kt
│       │   │   ├── App.kt              # Compose entry point / theme
│       │   │   └── ui/
│       │   │       ├── theme/
│       │   │       │   ├── Theme.kt
│       │   │       │   ├── Color.kt
│       │   │       │   └── Type.kt
│       │   │       ├── screens/
│       │   │       └── components/
│       │   └── res/
│       │       ├── values/
│       │       │   ├── strings.xml
│       │       │   ├── colors.xml
│       │       │   └── themes.xml
│       │       ├── drawable/
│       │       ├── mipmap-anydpi-v26/
│       │       ├── mipmap-hdpi/
│       │       ├── mipmap-mdpi/
│       │       ├── mipmap-xhdpi/
│       │       ├── mipmap-xxhdpi/
│       │       └── mipmap-xxxhdpi/
│       ├── test/                        # Unit tests
│       │   └── java/com/example/app/
│       └── androidTest/                 # Instrumented tests
│           └── java/com/example/app/
└── gradle/
    └── libs.versions.toml               # Version catalog (recommended)
```

---

## gradle.properties — Required Configuration

```properties
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=1024m -XX:+HeapDumpOnOutOfMemoryError
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true

android.useAndroidX=true
android.nonTransitiveRClass=true
android.enableJetifier=false

kotlin.code.style=official
kotlin.incremental=true
```

| Property                          | Value / Purpose                                            |
| --------------------------------- | ---------------------------------------------------------- |
| `org.gradle.jvmargs`              | 4 GB heap, metaspace limit, heap dump on OOM               |
| `org.gradle.parallel`             | Parallel module builds                                     |
| `org.gradle.caching`              | Build cache for incremental builds                         |
| `org.gradle.configuration-cache`  | Cache configuration phase across invocations               |
| `android.useAndroidX`             | Mandatory for modern Android development                   |
| `android.nonTransitiveRClass`     | Faster builds, smaller R classes per module                |
| `android.enableJetifier`          | `false` — only needed for legacy Support Library deps      |
| `kotlin.code.style`               | `official` for consistent formatting                       |
| `kotlin.incremental`              | Incremental Kotlin compilation                             |

---

## Version Catalog (libs.versions.toml)

Recommended pattern for dependency management.

```toml
[versions]
agp = "8.7.3"
kotlin = "2.1.0"
compose-bom = "2024.12.01"
compose-compiler = "1.5.15"

[libraries]
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-ui = { group = "androidx.compose.ui", name = "ui" }
compose-material3 = { group = "androidx.compose.material3", name = "material3" }
compose-ui-tooling-preview = { group = "androidx.compose.ui", name = "ui-tooling-preview" }
compose-ui-tooling = { group = "androidx.compose.ui", name = "ui-tooling" }
activity-compose = { group = "androidx.activity", name = "activity-compose", version = "1.9.3" }
core-ktx = { group = "androidx.core", name = "core-ktx", version = "1.15.0" }
lifecycle-runtime-ktx = { group = "androidx.lifecycle", name = "lifecycle-runtime-ktx", version = "2.8.7" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
kotlin-compose = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
```

---

## Root build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.compose) apply false
}
```

---

## App Module build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
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

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }
}

dependencies {
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.compose.material3)
    implementation(libs.compose.ui.tooling.preview)
    implementation(libs.activity.compose)
    implementation(libs.core.ktx)
    implementation(libs.lifecycle.runtime.ktx)

    debugImplementation(libs.compose.ui.tooling)

    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.6.1")
    androidTestImplementation(platform(libs.compose.bom))
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}
```

---

## settings.gradle.kts

```kotlin
pluginManagement {
    repositories {
        google {
            content {
                includeGroupByRegex("com\\.android.*")
                includeGroupByRegex("com\\.google.*")
                includeGroupByRegex("androidx.*")
            }
        }
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolution {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "MyApp"
include(":app")
```

---

## AndroidManifest.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/Theme.MyApp">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.MyApp">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
```

---

## First Build Verification

The project must compile before any business logic is added.

```bash
./gradlew assembleDebug
```

| Check                              | Expected Result                                      |
| ---------------------------------- | ---------------------------------------------------- |
| `BUILD SUCCESSFUL` in output       | Project compiles without errors                      |
| APK generated                      | `app/build/outputs/apk/debug/app-debug.apk` exists  |
| No unresolved dependencies         | All version catalog entries resolve                  |
| No Kotlin compilation errors       | Compose compiler plugin applied correctly            |
| No Android manifest merge errors   | Namespace and package names are correct              |

> **Rule: Never add business logic until `./gradlew assembleDebug` succeeds.**

---

## KSP (Kotlin Symbol Processing) Enablement

For annotation processors that use KSP (Room, Hilt, Moshi, etc.):

```kotlin
plugins {
    id("com.google.devtools.ksp") version "2.1.0-1.0.29"
}

android {
    buildFeatures {
        buildConfig = true
    }
}

dependencies {
    ksp("androidx.room:room-compiler:2.6.1")
}
```

| Note                                                               |
| ------------------------------------------------------------------ |
| AGP 8.0+ requires `buildFeatures.buildConfig = true` if you reference `BuildConfig` |
| KSP is preferred over KAPT for faster builds (no stub generation)  |
| Always match KSP version to Kotlin version (`ksp-2.1.0-1.0.29` for Kotlin `2.1.0`) |

---

## Kapt to KSP Migration

| Step | Action                                                       |
| ---- | ------------------------------------------------------------ |
| 1    | Replace `kotlin-kapt` plugin with `com.google.devtools.ksp` |
| 2    | Replace `kapt(...)` with `ksp(...)` in dependencies          |
| 3    | Remove `kapt` plugin from classpath                         |
| 4    | Run `./gradlew assembleDebug` to verify                     |
| 5    | Remove `kapt { }` configuration blocks                      |

---

## Compose Compiler Plugin

Starting with Kotlin 2.0, Compose compiler is a Kotlin compiler plugin (not an AGP dependency).

```kotlin
plugins {
    id("org.jetbrains.kotlin.plugin.compose") version "2.1.0"
}
```

| Old (Kotlin < 2.0)                                 | New (Kotlin >= 2.0)                                  |
| --------------------------------------------------- | ---------------------------------------------------- |
| `composeOptions.kotlinCompilerExtensionVersion`     | Not needed — plugin manages version                  |
| `buildFeatures.compose = true`                      | Still required                                       |
| `implementation("androidx.compose.compiler:compiler:...")` | Not needed — plugin handles                  |

---

## Cross References

See related references for project setup:

- **resources.md** — Resource file conventions, naming, qualifiers
- **ci-cd.md** — CI/CD configuration, build verification in pipelines
- **material-design.md** — Theme and color configuration for Compose

---

## External References

| Resource                                         | URL                                                                  |
| ------------------------------------------------ | -------------------------------------------------------------------- |
| Create a Project                                 | <https://developer.android.com/studio/projects/create-project>       |
| Build Configuration                              | <https://developer.android.com/build>                                |
| Version Catalogs                                 | <https://developer.android.com/build/migrate-to-catalogs>            |
| Compose Setup                                    | <https://developer.android.com/develop/ui/compose/setup>             |
| KSP Documentation                                | <https://kotlinlang.org/docs/ksp-overview.html>                      |
| Gradle Wrapper                                   | <https://docs.gradle.org/current/userguide/gradle_wrapper.html>      |
| Android Gradle Plugin Release Notes              | <https://developer.android.com/build/releases/gradle-plugin>         |

# CI/CD for Android — Reference

## GitHub Actions Workflow

Minimal CI pipeline for an Android Jetpack Compose project.

**File: `.github/workflows/android.yml`**

```yaml
name: Android CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4
        with:
          gradle-home-cache-cleanup: true

      - name: Grant execute permission
        run: chmod +x gradlew

      - name: Run Detekt
        run: ./gradlew detekt

      - name: Run Ktlint
        run: ./gradlew ktlintCheck

      - name: Run unit tests
        run: ./gradlew testDebugUnitTest

      - name: Build debug APK
        run: ./gradlew assembleDebug

      - name: Upload debug APK
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: debug-apk
          path: app/build/outputs/apk/debug/*.apk

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: test-results
          path: |
            **/build/test-results/
            **/build/reports/
```

### Workflow Summary

| Step                | Purpose                                           | On Failure    |
| ------------------- | ------------------------------------------------- | ------------- |
| Checkout            | Clone repository                                  | Fail fast     |
| JDK 17 setup        | Android Gradle Plugin 8.x requires JDK 17         | Fail fast     |
| Gradle setup        | Caches, daemon management                         | Fail fast     |
| Detekt              | Static analysis (code smells, complexity)         | Fail build    |
| Ktlint              | Kotlin code style enforcement                     | Fail build    |
| Unit tests          | `testDebugUnitTest` — all local tests             | Fail build    |
| Debug build         | `assembleDebug` — compilation verification        | Fail build    |
| Upload APK          | Artifact available for download                   | Always        |
| Upload test results | Test reports for debugging                        | On failure    |

---

## Gradle Managed Devices for CI

Consistent emulator environments defined in Gradle for reproducible instrumented tests.

### Configuration

```kotlin
android {
    testOptions {
        managedDevices {
            localDevices {
                create("pixel6Api34") {
                    device = "Pixel 6"
                    apiLevel = 34
                    systemImageSource = "aosp-atd"
                }
                create("pixel6Api30") {
                    device = "Pixel 6"
                    apiLevel = 30
                    systemImageSource = "aosp-atd"
                }
            }
            groups {
                create("ciDevices") {
                    targetDevices.add(devices["pixel6Api34"])
                    targetDevices.add(devices["pixel6Api30"])
                }
            }
        }
    }
}
```

### ATD (Automated Test Device) Images

| Image Source   | Purpose                                    | Speed Gain            |
| -------------- | ------------------------------------------ | --------------------- |
| `aosp-atd`     | AOSP Automated Test Device (no Google APIs)| ~2-3x faster than standard |
| `google-atd`   | ATD with Google APIs (Play Services)       | ~2x faster            |
| `aosp`         | Standard AOSP image                        | Baseline              |
| `google`       | Standard with Google Play                  | Baseline              |

### CI Command

```bash
./gradlew pixel6Api34DebugAndroidTest
```

For device groups:

```bash
./gradlew ciDevicesGroupDebugAndroidTest
```

---

## Test Commands

| Command                                         | Purpose                                      |
| ----------------------------------------------- | -------------------------------------------- |
| `./gradlew testDebugUnitTest`                   | Run all unit tests (debug variant)           |
| `./gradlew testReleaseUnitTest`                 | Run all unit tests (release variant)         |
| `./gradlew connectedDebugAndroidTest`           | Run instrumented tests on connected device   |
| `./gradlew pixel6Api34DebugAndroidTest`         | Run instrumented tests on managed device     |
| `./gradlew ciDevicesGroupDebugAndroidTest`      | Run on all devices in group                  |
| `./gradlew testDebugUnitTest --tests "*.UserRepositoryTest"` | Run specific test class     |
| `./gradlew testDebugUnitTest --tests "*.UserRepositoryTest.login*"` | Run specific test |
| `./gradlew testDebugUnitTest --continue`        | Continue after test failures                 |
| `./gradlew koverXmlReportDebug`                 | Generate Kover XML coverage report           |
| `./gradlew koverHtmlReportDebug`                | Generate Kover HTML coverage report          |
| `./gradlew koverVerifyDebug`                    | Verify coverage meets threshold              |

---

## Kover — Coverage Configuration

Kotlin code coverage tool that works with Kotlin/JVM, Kotlin Multiplatform, and Android.

### Plugins Block

```kotlin
plugins {
    id("org.jetbrains.kotlinx.kover") version "0.9.1"
}
```

### Reports Configuration

```kotlin
kover {
    reports {
        total {
            xml {
                onCheck = true
                outputFile = layout.buildDirectory.file("reports/kover/report.xml")
            }
            html {
                onCheck = true
                outputDir = layout.buildDirectory.dir("reports/kover/html")
            }
            verify {
                onCheck = true
                rule {
                    minBound(80)
                    maxBound(100)
                }
            }
        }

        filters {
            excludes {
                classes(
                    "*.databinding.*",
                    "*.BuildConfig",
                    "*.*_MembersInjector",
                    "*.*_Factory",
                    "*.Hilt_*",
                    "*.*HiltModules*",
                    "*.ComposableSingletons*",
                    "*.ui.theme.*"
                )
                annotationClasses(
                    "dagger.hilt.codegen.OriginatingElement",
                    "javax.annotation.Generated"
                )
            }
        }
    }
}
```

### Verify Rule — 80% Threshold

```kotlin
kover {
    reports {
        total {
            verify {
                rule {
                    minBound(80)
                    maxBound(100)

                    filters {
                        excludes {
                            classes(
                                "*.databinding.*",
                                "*.BuildConfig",
                                "*.ui.theme.*"
                            )
                        }
                    }
                }
            }
        }
    }
}
```

| Configuration    | Value        | Notes                                         |
| ---------------- | ------------ | ---------------------------------------------- |
| `minBound`       | 80           | Minimum 80% line coverage required             |
| `maxBound`       | 100          | Upper bound (sanity check)                     |
| `onCheck`        | true         | Run verification during `check` task           |
| XML report       | enabled      | CI integration, SonarQube, Codecov             |
| HTML report      | enabled      | Local developer review                         |

---

## Coverage Targets

| Code Category          | Target Coverage | Notes                                              |
| ---------------------- | --------------- | -------------------------------------------------- |
| Critical logic         | 100%            | Payment, auth, data integrity, security            |
| Public API surface     | 90%+            | Library modules, exported functions                |
| General business logic | 80%+            | ViewModels, use cases, repositories                |
| UI (Compose)           | 60%+            | Smoke tests, screenshot tests; full coverage difficult |
| Generated code         | Exclude         | DataBinding, Hilt, BuildConfig, Compose adapters   |
| Utility / Extensions   | 80%+            | Should be easy to test fully                       |

### Exclusions for Coverage

Always exclude from coverage reports:

- `*.*_MembersInjector`
- `*.*_Factory`
- `*.Hilt_*`
- `*.databinding.*`
- `*.BuildConfig`
- `*.ComposableSingletons*`
- `*.ui.theme.*`
- `*.di.*` (dependency injection modules)

---

## CI Optimization Tips

### Emulator Performance (Linux CI)

| Technique                      | Configuration                                        | Impact              |
| ------------------------------ | ---------------------------------------------------- | ------------------- |
| KVM acceleration               | Enable nested virtualization on CI runner             | 5-10x emulator speed|
| Hardware graphics (`-gpu`)     | `emulator -gpu swiftshader_indirect`                 | Software GPU for CI |
| No window (`-no-window`)       | `emulator -no-window -no-audio`                      | Headless mode       |
| Cold boot (`-no-snapshot`)     | `emulator -no-snapshot-load`                         | Clean state         |
| ATD images                     | `systemImageSource = "aosp-atd"`                     | 2-3x faster tests   |

### Gradle Optimization

| Technique                      | Configuration                                        | Impact              |
| ------------------------------ | ---------------------------------------------------- | ------------------- |
| Build cache                    | `org.gradle.caching=true`                            | Avoid re-compilation|
| Configuration cache            | `org.gradle.configuration-cache=true`                | Faster config phase |
| Parallel execution             | `org.gradle.parallel=true`                           | Multi-module builds |
| Gradle action cache            | `gradle/actions/setup-gradle@v4`                     | Remote cache in CI  |
| Dependency caching             | Automatically handled by setup-gradle action         | No re-downloads     |

### Artifact Management

```yaml
- name: Upload test results on failure
  uses: actions/upload-artifact@v4
  if: failure()
  with:
    name: test-reports
    path: |
      **/build/reports/
      **/build/test-results/

- name: Upload APK
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: debug-apk
    path: app/build/outputs/apk/debug/*.apk
```

### Parallel Test Execution

```bash
./gradlew testDebugUnitTest --parallel --max-workers=4
```

| Flag              | Purpose                                   |
| ----------------- | ----------------------------------------- |
| `--parallel`      | Run subprojects in parallel               |
| `--max-workers`   | Limit concurrent workers (CI has limited CPU) |
| `--build-cache`   | Explicitly enable build cache             |
| `--continue`      | Don't stop on first failure               |

---

## Detekt Configuration

### Plugins Block

```kotlin
plugins {
    id("io.gitlab.arturbosch.detekt") version "1.23.7"
}
```

### Configuration File

**File: `detekt.yml`**

```yaml
buildUponDefaultConfig: true
config:
  validation: true
  warningsAsErrors: true

processors:
  active: true

console-reports:
  active: true

style:
  MaxLineLength:
    maxLineLength: 120
  UnusedPrivateMember:
    active: true

complexity:
  LongMethod:
    threshold: 60
  ComplexMethod:
    threshold: 15
  TooManyFunctions:
    thresholdInFiles: 15
    thresholdInClasses: 15

exceptions:
  TooGenericExceptionCaught:
    active: false
```

### CI Command

```bash
./gradlew detekt
```

---

## Ktlint Configuration

### Plugins Block

```kotlin
plugins {
    id("org.jlleitschuh.gradle.ktlint") version "12.1.2"
}
```

### Configuration

```kotlin
ktlint {
    android.set(true)
    outputColorName.set("RED")
    verbose.set(true)
    filter {
        exclude("**/generated/**")
        exclude("**/build/**")
    }
}
```

### CI Commands

```bash
./gradlew ktlintCheck
./gradlew ktlintFormat
```

---

## Firebase Test Lab (Optional)

For cloud-based instrumented testing when local emulators are insufficient.

### Prerequisites

| Requirement             | Setup                                            |
| ----------------------- | ------------------------------------------------ |
| Firebase project        | Create at <https://console.firebase.google.com>   |
| gcloud CLI              | `gcloud auth login` and `gcloud config set project` |
| Test bucket             | Cloud Storage bucket for test results            |

### Commands

```bash
gcloud firebase test android run \
  --type instrumentation \
  --app app/build/outputs/apk/debug/app-debug.apk \
  --test app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk \
  --device model=Pixel6,version=34,locale=en,orientation=portrait \
  --device model=Pixel6,version=30,locale=en,orientation=portrait \
  --timeout 600s
```

| Parameter    | Purpose                                   |
| ------------ | ----------------------------------------- |
| `--type`     | Test type: `instrumentation`, `robo`, `game-loop` |
| `--app`      | Path to APK under test                    |
| `--test`     | Path to test APK                          |
| `--device`   | Device specification (model, API, locale) |
| `--timeout`  | Max test execution time                   |

### GitHub Actions Integration

```yaml
- name: Run Firebase Test Lab
  uses: FirebaseExtended/action-device-farm-test@v1
  with:
    app-apk: app/build/outputs/apk/debug/app-debug.apk
    test-apk: app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
    run-timeout: '600s'
```

---

## Complete CI Pipeline — Full Example

```yaml
name: Android CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - uses: gradle/actions/setup-gradle@v4
      - run: chmod +x gradlew
      - run: ./gradlew detekt ktlintCheck

  unit-tests:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - uses: gradle/actions/setup-gradle@v4
      - run: chmod +x gradlew
      - run: ./gradlew testDebugUnitTest
      - run: ./gradlew koverXmlReportDebug
      - run: ./gradlew koverVerifyDebug
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-report
          path: app/build/reports/kover/

  build:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - uses: gradle/actions/setup-gradle@v4
      - run: chmod +x gradlew
      - run: ./gradlew assembleDebug
      - uses: actions/upload-artifact@v4
        with:
          name: debug-apk
          path: app/build/outputs/apk/debug/*.apk

  instrumented-tests:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - uses: gradle/actions/setup-gradle@v4
      - run: chmod +x gradlew
      - name: Enable KVM
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
          sudo udevadm control --reload-rules
          sudo udevadm trigger --name-match=kvm
      - run: ./gradlew ciDevicesGroupDebugAndroidTest
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: instrumented-test-results
          path: |
            **/build/reports/
            **/build/outputs/androidTest-results/
```

---

## Cross References

See related rules and references:

- **project-setup.md** — Build configuration, Gradle wrapper, version catalog
- **resources.md** — Resource conventions, naming, qualifiers
- **material-design.md** — Theme and accessibility requirements for testing

### CI/CD Related Rules

- **gradle-ci** — Gradle CI build optimization
- **gradle-cache** — Build cache and configuration cache setup
- **gradle-tests** — Test task configuration and execution
- **gradle-managed-devices** — Emulator definitions for CI
- **gradle-coverage** — Kover setup, thresholds, and exclusions
- **gradle-lint** — Detekt and Ktlint configuration

---

## External References

| Resource                                         | URL                                                                  |
| ------------------------------------------------ | -------------------------------------------------------------------- |
| GitHub Actions for Android                       | <https://developer.android.com/build/configure-build-tests/continuous-integration> |
| Gradle Managed Devices                           | <https://developer.android.com/build/manage-devices>                 |
| Kover Documentation                              | <https://kotlin.github.io/kotlinx-kover/>                            |
| Detekt                                           | <https://detekt.dev/>                                                |
| Ktlint                                           | <https://pinterest.github.io/ktlint/>                                |
| Firebase Test Lab                                | <https://firebase.google.com/docs/test-lab>                          |
| Android Emulator on CI                           | <https://github.com/ReactiveCircus/android-emulator-runner>          |
| Gradle Build Cache                               | <https://docs.gradle.org/current/userguide/build_cache.html>         |

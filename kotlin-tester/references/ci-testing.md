# CI Testing with Gradle Managed Devices

Expert guidance for running instrumented tests in CI with Gradle Managed Devices (GMD), GitHub Actions, and Firebase Test Lab.

## 1. GMD Device Definition

```kotlin
plugins {
    id("com.android.test")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.test"
    compileSdk = 35

    defaultConfig {
        minSdk = 24
        targetSdk = 35
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    testOptions {
        managedDevices {
            localDevices {
                create("pixel6api34") {
                    device = "Pixel 6"
                    apiLevel = 34
                    systemImageSource = "aosp-atd"
                }
            }
            devices {
                create("pixel8api35") {
                    device = "Pixel 8"
                    apiLevel = 35
                    systemImageSource = "aosp-atd"
                }
            }
        }
    }
}
```

## 2. System Image Sources

| Source | Description | Use Case |
|--------|-------------|----------|
| `aosp-atd` | AOSP with Automated Test Device optimizations | Fastest CI; minimal pre-installed apps; recommended default |
| `aosp` | Standard AOSP image | General testing without Google services |
| `google` | AOSP + Google APIs | Testing Google Play Services, Maps, Firebase |
| `google-atd` | Google APIs + ATD optimizations | CI with Google Play Services support |
| `android` | Stock Android (with Play Store) | Full device simulation; largest image size |

**Recommendation:** Use `aosp-atd` for most CI runs. Use `google-atd` only when tests depend on Google Play Services.

## 3. Device Groups for Parallel Matrix Testing

```kotlin
testOptions {
    managedDevices {
        localDevices {
            create("pixel8api35") {
                device = "Pixel 8"
                apiLevel = 35
                systemImageSource = "aosp-atd"
            }
            create("pixel6api31") {
                device = "Pixel 6"
                apiLevel = 31
                systemImageSource = "aosp-atd"
            }
            create("nexus7api28") {
                device = "Nexus 7"
                apiLevel = 28
                systemImageSource = "aosp"
            }
        }
        groups {
            create("phoneAndTablet") {
                targetDevices.add(devices["pixel8api35"])
                targetDevices.add(devices["pixel6api31"])
                targetDevices.add(devices["nexus7api28"])
            }
        }
    }
}
```

### Run device group

```bash
./gradlew phoneAndTabletGroupAndroidTest
```

## 4. Device Matrix Strategy

| Strategy | API Level | Device | Source | Purpose |
|----------|-----------|--------|--------|---------|
| Latest stable | 35 | Pixel 8 | `aosp-atd` | Catch regressions on newest platform |
| Popular mid-range | 33 | Pixel 6 | `aosp-atd` | Covers largest user segment |
| Minimum supported | 24 (or your minSdk) | Pixel 4 | `aosp` | Ensure backward compatibility |
| Tablet | 33 | Nexus 7 | `aosp-atd` | Verify responsive layouts |

### Recommended matrix for production apps

```kotlin
managedDevices {
    localDevices {
        create("pixel8Api35") {
            device = "Pixel 8"
            apiLevel = 35
            systemImageSource = "aosp-atd"
        }
        create("pixel6Api33") {
            device = "Pixel 6"
            apiLevel = 33
            systemImageSource = "aosp-atd"
        }
        create("pixel4Api26") {
            device = "Pixel 4"
            apiLevel = 26
            systemImageSource = "aosp"
        }
    }
    groups {
        create("ciMatrix") {
            targetDevices.add(devices["pixel8Api35"])
            targetDevices.add(devices["pixel6Api33"])
            targetDevices.add(devices["pixel4Api26"])
        }
    }
}
```

## 5. GitHub Actions Workflow

```yaml
name: Instrumented Tests (GMD)

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  android-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 17

      - name: Enable KVM acceleration
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
          sudo udevadm control --reload-rules
          sudo udevadm trigger --name-match=kvm

      - name: Cache Gradle
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: gradle-${{ hashFiles('**/*.gradle.kts', 'gradle/wrapper/gradle-wrapper.properties') }}
          restore-keys: gradle-

      - name: Cache GMD snapshots
        uses: actions/cache@v4
        with:
          path: |
            ~/.android/avd/*.avd/snapshots
            ~/.android/avd/*.avd/config.ini
          key: gmd-${{ hashFiles('**/build.gradle.kts') }}

      - name: Run instrumented tests
        run: ./gradlew ciMatrixGroupAndroidTest

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: |
            **/build/reports/androidTests/
            **/build/outputs/androidTest-results/
```

## 6. Key CI Requirements

| Requirement | Details |
|-------------|---------|
| KVM acceleration | Required for emulator performance on Linux CI runners. Without KVM, tests run 5-10x slower. |
| 8GB+ RAM | Emulator + Gradle daemon + test app require significant memory. |
| Disk space | Each GMD snapshot is ~2-4 GB. Plan for 10-15 GB total for multiple devices. |
| CPU cores | Minimum 2 vCPU; 4+ recommended for parallel device groups. |
| Ubuntu runner | `ubuntu-latest` or `ubuntu-22.04` — KVM is not available on macOS GitHub runners. |

## 7. Firebase Test Lab Integration

For runners without KVM or when testing on real devices:

```bash
gcloud firebase test android run \
    --type instrumentation \
    --app app/build/outputs/apk/debug/app-debug.apk \
    --test app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk \
    --device model=pixel8,version=34,locale=en_US,orientation=portrait \
    --device model=redfin,version=30,locale=en_US,orientation=portrait \
    --timeout 15m \
    --results-bucket gs://my-test-results \
    --results-dir test-run-${{ github.sha }}
```

### Gradle plugin for Firebase Test Lab

```kotlin
plugins {
    id("com.google.firebase.testlab") version "0.0.1-alpha07"
}

firebaseTestLab {
    devices {
        create("pixel8") {
            androidApiLevel = 34
            deviceModelId = "pixel8"
        }
    }
}
```

## 8. Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Emulator won't start | KVM not enabled | Add udev rule for KVM; verify with `ls -l /dev/kvm` |
| Slow boot (>60s) | No hardware acceleration | Ensure KVM is enabled; use `aosp-atd` images |
| Out of disk space | Multiple GMD snapshots | Cache snapshots; prune old ones with `./gradlew cleanManagedDevices` |
| Timeout during test | Test takes longer than default | Set `testOptions.execution = "ANDROIDX_TEST_ORCHESTRATOR"` and increase timeout |
| `com.android.builder.testing.api.DeviceException` | Emulator not responsive | Increase RAM allocation; retry step |
| Flaky tests on CI only | Timing, network, or disk speed | Use Orchestrator, `aosp-atd` images, explicit waits |
| GMD snapshot download slow | Large image on first run | Cache snapshot directory between CI runs |

## 9. Cache Management

```bash
./gradlew cleanManagedDevices --unusedOnly

./gradlew cleanManagedDevices

./gradlew ciMatrixGroupAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=com.example.SuiteName
```

| Command | Purpose |
|---------|---------|
| `cleanManagedDevices --unusedOnly` | Remove snapshots for device definitions no longer in build scripts |
| `cleanManagedDevices` | Remove all GMD snapshots (fresh download on next run) |
| `--info` flag | Debug GMD setup issues: `./gradlew pixel8Api35AndroidTest --info` |

## 10. Test Sharding

Run test suite in parallel across multiple emulator instances:

```bash
adb shell am instrument -w -e numShards 4 -e shardIndex 0 \
    com.example.test/androidx.test.runner.AndroidJUnitRunner
```

### Gradle sharding with GMD

GMD tests can be sharded directly from the command line without modifying the build script:

```bash
./gradlew pixel8api34AndroidTest \
    -Pandroid.testInstrumentationRunnerArguments.numShards=4 \
    -Pandroid.testInstrumentationRunnerArguments.shardIndex=0
```

### Firebase Test Lab smart sharding

```bash
gcloud firebase test android run \
    --type instrumentation \
    --app app-debug.apk \
    --test app-debug-androidTest.apk \
    --device model=pixel8,version=34 \
    --num-uniform-shards 4 \
    --timeout 15m
```

The `--num-uniform-shards` flag automatically splits tests across multiple virtual devices, running them in parallel.

## Cross References

- Related rules: `cov-kover-config`, `cov-threshold-enforcement`, `ui-test-orchestrator`, `ui-test-no-sleep`, `ui-test-per-test-isolation`
- Related references: [`coverage.md`](coverage.md), [`espresso-testing.md`](espresso-testing.md), [`compose-testing.md`](compose-testing.md), [`instrumented-testing.md`](instrumented-testing.md)

# Kover Code Coverage

Expert guidance for configuring and enforcing code coverage with Kover in Kotlin projects.

## 1. Gradle Plugin Setup

```kotlin
plugins {
    id("org.jetbrains.kotlinx.kover") version "0.9.1"
}
```

## 2. Kover Configuration Block

```kotlin
kover {
    currentProject {
        createVariant("custom") {
            sources {
                excludedSourceSets += "generated"
            }
        }
    }

    reports {
        filters {
            excludes {
                classes(
                    "*.dto.*",
                    "*._*" ,
                    "*.generated.*",
                    "*Bundle",
                    "*.*\$Companion",
                    "*.*\$Serializer",
                    "*.BuildConfig"
                )
                annotatedBy(
                    "javax.annotation.Generated",
                    "androidx.annotation.RestrictTo"
                )
            }
        }

        verify {
            rule("Minimum line coverage") {
                bound {
                    minValue = 80
                    metric = KotlinMetric.LINE
                    aggregation = AggregationType.COVERED_PERCENTAGE
                }
            }
        }
    }
}
```

### Verify Rule with minBound(80)

```kotlin
verify {
    rule("Branch coverage minimum") {
        minBound(80)
        maxBound(100)
    }

    rule("Critical path must be fully covered") {
        bound {
            minValue = 100
            metric = KotlinMetric.LINE
        }
        filters {
            includes {
                classes("com.example.domain.usecase.*")
            }
        }
    }
}
```

## 3. Coverage Targets

| Area | Target | Rationale |
|------|--------|-----------|
| Critical business logic | 100% | Use cases, payment processing, auth — zero tolerance for untested paths |
| Public API surface | 90%+ | Library or module public contracts must be verified |
| General application code | 80%+ | Balanced productivity and safety |
| Data classes / DTOs | Exclude | Auto-generated `equals`/`hashCode`/`toString`/`copy` — no logic to test |
| Generated code | Exclude | Protobuf, Moshi, Safe Args, BuildConfig — not hand-written |
| Composable functions (UI) | Exclude | Test via Compose UI tests instead; Kover measures line coverage poorly here |

## 4. Coverage Commands

| Command | Purpose |
|---------|---------|
| `./gradlew koverHtmlReport` | Generate HTML report for browsing |
| `./gradlew koverXmlReport` | Generate XML report (Cobertura format) for CI tools |
| `./gradlew koverVerify` | Verify coverage meets configured rules; fails build if below threshold |
| `./gradlew koverLog` | Print coverage summary to console |

### Per-variant commands

```bash
./gradlew koverHtmlReportDebug
./gradlew koverXmlReportRelease
./gradlew koverVerifyDebug
```

## 5. Viewing Reports

| OS | Report Path |
|----|------------|
| macOS / Linux | `build/reports/kover/html/index.html` |
| Windows | `build\reports\kover\html\index.html` |
| XML (all platforms) | `build/reports/kover/report.xml` |

Open the HTML report in a browser for per-class, per-method drill-down with line-level highlighting.

## 6. CI Integration with GitHub Actions

```yaml
name: Test & Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 17

      - name: Cache Gradle
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: gradle-${{ hashFiles('**/*.gradle.kts', 'gradle/wrapper/gradle-wrapper.properties') }}

      - name: Run tests
        run: ./gradlew test

      - name: Generate coverage XML
        run: ./gradlew koverXmlReport

      - name: Verify coverage threshold
        run: ./gradlew koverVerify

      - name: Upload to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: build/reports/kover/report.xml
          fail_ci_if_error: true
          token: ${{ secrets.CODECOV_TOKEN }}
```

## 7. Multi-Module Configuration

```kotlin
// In root build.gradle.kts
plugins {
    id("org.jetbrains.kotlinx.kover") version "0.9.1" apply false
}

// In each module's build.gradle.kts
plugins {
    id("org.jetbrains.kotlinx.kover")
}

// Merge reports in root
kover {
    merge {
        projects(":core", ":feature-auth", ":feature-checkout")
    }
}
```

## 8. Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Low coverage on data classes | `equals`/`hashCode`/`copy` generated | Exclude with `classes("*.dto.*")` or `annotatedBy("...")` |
| Generated code inflating totals | Protobuf, Moshi, Safe Args | Exclude via `classes("*.generated.*")` or `excludedSourceSets` |
| Composable functions show 0% | Kover instruments line-level, not compose semantics | Exclude composables from Kover; rely on Compose UI tests |
| Coverage drops after adding sealed interfaces | `when` exhaustiveness branches | Test all branches or exclude sealed class hierarchies from verify rules |
| Build fails on `koverVerify` | Coverage below threshold | Check HTML report, add targeted tests, or adjust `minBound` |
| Flaky coverage numbers | Non-deterministic test execution | Ensure tests are deterministic; avoid `Thread.sleep` and random data |

## 9. Excluding by Annotation

```kotlin
// Custom annotation for coverage exclusion
@Target(AnnotationTarget.CLASS, AnnotationTarget.FUNCTION)
annotation class NoCoverage

// In kover block
filters {
    excludes {
        annotatedBy("com.example.testing.NoCoverage")
    }
}
```

## Cross References

- Related rules: `cov-min-80`, `cov-critical-100`, `cov-exclude-data-classes`, `cov-exclude-generated`, `cov-verify-ci`, `cov-html-report`
- Related references: [`ci-testing.md`](ci-testing.md), [`espresso-testing.md`](espresso-testing.md), [`compose-testing.md`](compose-testing.md)

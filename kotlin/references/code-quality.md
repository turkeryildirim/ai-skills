# Code Quality Enforcement for Kotlin/Android

## Philosophy

- Zero warnings policy: all violations fail the build
- No `//noinspection` or `@Suppress` unless justified with a linked issue
- Formatting (ktlint) and static analysis (Detekt) run on every PR
- Pre-commit hooks prevent uncommitted violations

## Detekt

### detekt.yml

```yaml
complexity:
  LongMethod:
    threshold: 20
    excludes: &testExcludes
      - "**/test/**"
      - "**/androidTest/**"
  LongParameterList:
    functionThreshold: 4
    constructorThreshold: 6
    ignoreDefaultParameters: true
  TooManyFunctions:
    thresholdInFiles: 10
    thresholdInClasses: 10
    thresholdInInterfaces: 8
    thresholdInObjects: 8
    thresholdInEnums: 6
    ignorePrivate: true

style:
  MaxLineLength:
    maxLineLength: 120
    excludePackageStatements: true
    excludeImportStatements: true
    excludeCommentStatements: false
  WildcardImport:
    active: true
    excludeImports:
      - "java.util.*"

coroutines:
  GlobalCoroutineUsage:
    active: true

formatting:
  active: true
  android: true
  autoCorrect: true

naming:
  FunctionParameterNaming:
    active: true
    parameterPattern: "[a-z][A-Za-z0-9]*"
    privateParameterPattern: "[a-z][A-Za-z0-9]*"

exceptions:
  TooGenericExceptionCaught:
    active: true
    excludes:
      - "**/test/**"
      - "**/androidTest/**"
  TooGenericExceptionThrown:
    active: true
```

### Gradle Setup

```kotlin
plugins {
    id("io.gitlab.arturbosch.detekt") version "1.23.7"
}

detekt {
    buildUponDefaultConfig = true
    allRules = true
    config.setFrom(files("$projectDir/detekt.yml"))
    baseline = file("$projectDir/detekt-baseline.xml")
}

tasks.withType<io.gitlab.arturbosch.detekt.Detekt>().configureEach {
    reports {
        html.required.set(true)
        xml.required.set(true)
        sarif.required.set(true)
        md.required.set(true)
    }
}

dependencies {
    detektPlugins("io.gitlab.arturbosch.detekt:detekt-formatting:1.23.7")
}
```

## Ktlint

### Gradle Setup

```kotlin
plugins {
    id("org.jlleitschuh.ktlint") version "12.1.1"
}

ktlint {
    android.set(true)
    outputColorName.set("RED")
    additionalEditorconfigFile.set(file("$projectDir/.editorconfig"))
    filter {
        exclude("**/generated/**")
        include("**/kotlin/**")
    }
}
```

### .editorconfig

```editorconfig
root = true

[*]
charset = utf-8
end_of_line = lf
indent_size = 4
indent_style = space
insert_final_newline = true
trim_trailing_whitespace = true
max_line_length = 120

[*.{kt,kts}]
ij_kotlin_allow_trailing_comma = true
ij_kotlin_allow_trailing_comma_on_call_site = true
ij_kotlin_imports_layout = *,java.**,javax.**,kotlin.**,kotlinx.**,*
ij_kotlin_packages_to_use_import_on_demand = false
```

## Commands

| Command | Description |
|---|---|
| `./gradlew detekt` | Run Detekt on all source sets |
| `./gradlew detektMain` | Run Detekt on main source set only |
| `./gradlew detektTest` | Run Detekt on test source set only |
| `./gradlew ktlintCheck` | Check formatting with ktlint |
| `./gradlew ktlintFormat` | Auto-fix formatting with ktlint |

## CI Integration

```yaml
jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 17
      - name: Run Detekt
        run: ./gradlew detekt
      - name: Run Ktlint
        run: ./gradlew ktlintCheck
      - name: Upload Detekt Report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: detekt-report
          path: build/reports/detekt/
```

## Pre-commit Hooks

```bash
#!/bin/sh
./gradlew ktlintCheck detekt
if [ $? -ne 0 ]; then
  echo "Code quality check failed. Fix issues before committing."
  exit 1
fi
```

Install with:

```bash
cat << 'EOF' > .git/hooks/pre-commit
#!/bin/sh
./gradlew ktlintCheck detekt --quiet
EOF
chmod +x .git/hooks/pre-commit
```

Alternatively, use the Gradle task to install the hook:

```kotlin
tasks.register<Copy>("installGitHooks") {
    from("scripts/pre-commit")
    into(".git/hooks")
    filePermissions {
        user {
            read = true
            execute = true
        }
    }
}

tasks.named("prepareKotlinBuildScriptModel") {
    dependsOn("installGitHooks")
}
```

## Cross References

- [Detekt Documentation](https://detekt.dev/)
- [Ktlint Documentation](https://pinterest.github.io/ktlint/)
- [Android Kotlin Style Guide](https://developer.android.com/kotlin/style-guide)
- [Kotlin Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html)

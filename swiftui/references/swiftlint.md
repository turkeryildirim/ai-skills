# SwiftLint Configuration and Enforcement

Code quality enforcement for Swift projects using SwiftLint.

## 1. Recommended Setup

Use the SwiftLint build tool plugin via `SimplyDanny/SwiftLintPlugins` — no run script required:

```swift
// Package.swift
.package(url: "https://github.com/SimplyDanny/SwiftLintPlugins", from: "0.57.0")

// In target:
.target(
    name: "MyApp",
    plugins: [.plugin(name: "SwiftLintBuildToolPlugin", package: "SwiftLintPlugins")]
)
```

## 2. Configuration File (.swiftlint.yml)

Place at the project root. Three primary control mechanisms (choose one pattern):

```yaml
# Option A: Start with defaults, disable conflicting rules
disabled_rules:
  - trailing_whitespace
  - line_length

opt_in_rules:
  - empty_count
  - closure_spacing
  - explicit_init
  - first_where

# Option B: Whitelist-only approach (mutually exclusive with opt_in_rules)
# only_rules:
#   - identifier_name
#   - type_name
#   - force_unwrapping

excluded:
  - Pods
  - .build
  - DerivedData
  - "**/*.generated.swift"

analyzer_rules:
  - unused_import
  - unused_declaration

reporter: xcode  # or json, checkstyle, sarif
```

## 3. Rule Selection Strategy

1. Start with SwiftLint defaults (they cover the most common issues).
2. Disable rules that conflict with project conventions (e.g., `trailing_comma` if Xcode auto-formats differently).
3. Add opt-in rules incrementally — avoid enabling many at once in a large codebase.
4. For existing codebases: use baselines to suppress legacy violations while enforcing zero new violations.

## 4. Baselines (Incremental Adoption)

```bash
# Record current state — suppresses existing violations
swiftlint --write-baseline

# CI enforces: zero NEW violations allowed
swiftlint --baseline .swiftlint-baseline.json
```

This lets teams adopt SwiftLint on legacy codebases without fixing everything upfront.

## 5. Inline Suppression

```swift
// ✅ Suppress specific rule only
// swiftlint:disable:next force_unwrapping
let url = URL(string: "https://example.com")!

// ✅ Region suppression (must re-enable)
// swiftlint:disable force_cast
let view = someView as! UICollectionViewCell
// swiftlint:enable force_cast

// ❌ Suppress all rules — too broad
// swiftlint:disable:next all
```

Always re-enable after the region ends. Prefer excluded paths for generated code over inline suppressions.

## 6. CI Integration

```yaml
# GitHub Actions example
- name: SwiftLint
  run: |
    swiftlint lint \
      --strict \
      --reporter sarif \
      --output swiftlint.sarif

- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: swiftlint.sarif
```

- `--strict`: Treats warnings as errors.
- `--reporter sarif`: Compatible with GitHub Advanced Security for inline PR annotations.

## 7. Useful Opt-In Rules

| Rule | What It Enforces |
|------|-----------------|
| `empty_count` | `isEmpty` over `.count == 0` |
| `closure_spacing` | Spaces inside closure braces |
| `explicit_init` | No `.init()` — use type name |
| `first_where` | `.first(where:)` over `.filter().first` |
| `sorted_first_last` | `.min()` / `.max()` over `.sorted().first` |
| `contains_over_filter_count` | `.contains(where:)` over `.filter().count > 0` |
| `force_unwrapping` | Warns on `!` force-unwraps |
| `implicitly_unwrapped_optional` | Warns on `Type!` declarations |

## 8. Common Pitfalls

## Cross References

- Related rules: review alongside `swiftui-*`, `conc-*`, `data-*`, and `test-*` categories when enforcing conventions
- Related references: [`architecture.md`](architecture.md), [`view-structure.md`](view-structure.md), [`../../swiftui-tester/references/swift-testing.md`](../../swiftui-tester/references/swift-testing.md)

| Mistake | Fix |
|---------|-----|
| Running `--fix` in build phases | Only run `--fix` manually — it modifies files unpredictably during builds |
| Using `only_rules` with `opt_in_rules` | They're mutually exclusive — choose one |
| Forgetting to re-enable after `disable` | Always pair disable/enable |
| Adopting many opt-in rules at once | Add incrementally, verify each one |
| No `excluded` for Pods/generated files | Always exclude third-party and generated code |
| No baseline on large legacy codebase | Use `--write-baseline` for incremental adoption |

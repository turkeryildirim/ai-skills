# Rules for SwiftUI and Concurrency

Actionable directives for modern Swift and SwiftUI development.

## 1. SwiftUI Patterns (`swiftui-`)

### `swiftui-state-observable`
- **Context:** State management in iOS 17+.
- **Rule:** Use `@Observable` for classes. Inject with `@State` for ownership (mark `private`), `@Bindable` for shared bindings, `.environment()` for global access.
- **Avoid:** `ObservableObject`, `@Published`, `@StateObject`.

### `swiftui-view-extraction`
- **Context:** View composition.
- **Rule:** Extract subviews into separate `struct` types. Add `Equatable` conformance to views with expensive bodies. Pass only the data a view needs.
- **Avoid:** Massive computed properties in a single `View`. Returning `AnyView`.

### `swiftui-navigation-stack`
- **Context:** App navigation.
- **Rule:** Use `NavigationStack` with `NavigationPath` for programmatic control. Use `navigationDestination(for:destination:)` for decoupling. Each tab owns its own `NavigationPath`.
- **Avoid:** Legacy `NavigationView`. Shared `NavigationPath` across tabs.

### `swiftui-lazy-layouts`
- **Context:** Large collections.
- **Rule:** Use `LazyVStack`/`LazyHStack` inside `ScrollView` for large or dynamic collections. Use `LazyVGrid` for grid layouts. Always provide stable, unique `Identifiable` IDs in `ForEach`.
- **Avoid:** `VStack` for large collections. Array indices as `ForEach` IDs. `GeometryReader` inside lazy containers.

### `swiftui-foreground-style`
- **Context:** Styling.
- **Rule:** Use `foregroundStyle()` for text and shapes. It supports colors, gradients, and hierarchical styles.
- **Avoid:** `foregroundColor()`.

### `swiftui-gesture-state`
- **Context:** Gesture handling.
- **Rule:** Use `@GestureState` for intermediate values that auto-reset on gesture end. Use `@State` for persisted values. Keep `.onChanged()` closures lightweight (runs 60–120 fps). Use `Button` for single-tap actions.
- **Avoid:** Heavy computation in `.onChanged()`. `MagnificationGesture` and `RotationGesture` on iOS 17+ (use `MagnifyGesture`, `RotateGesture`). `onTapGesture` for primary actions.

### `swiftui-animation-scope`
- **Context:** Animations.
- **Rule:** Always use `.animation(_:value:)` with a specific `value` parameter. Check `accessibilityReduceMotion` before playing intense animations. Each `matchedGeometryEffect` ID must have exactly one source.
- **Avoid:** `.animation()` without `value:` (animates all changes). Multiple sources for same `matchedGeometryEffect` ID.

### `swiftui-task-lifecycle`
- **Context:** View-triggered async work.
- **Rule:** Use `.task` or `.task(id:)` for async loading that should start and cancel with the view lifecycle. Move heavy work into async functions or services and keep `body` declarative.
- **Avoid:** Starting network loads in `onAppear` without cancellation handling. Fire-and-forget `Task {}` blocks from button handlers when ownership matters.

## 2. Concurrency Patterns (`conc-`)

### `conc-strict-checking`
- **Context:** Swift 6+ compilation.
- **Rule:** "Strict Concurrency Checking" must be set to "Complete". Fix all data race warnings.
- **Avoid:** Ignoring concurrency warnings or suppressing them with casts.

### `conc-actor-isolation`
- **Context:** Shared state.
- **Rule:** Use `actor` for thread-safe shared state. Use `@MainActor` for UI-related classes (ViewModels, Views). Router classes must be `@MainActor`.
- **Avoid:** Direct mutation of shared state from multiple threads.

### `conc-task-groups`
- **Context:** Concurrent work.
- **Rule:** Prefer `withTaskGroup` or `withThrowingTaskGroup` for managing multiple child tasks.
- **Avoid:** Unstructured `Task {}` inside loops without collecting results.

### `conc-cooperative-cancellation`
- **Context:** Long-running tasks.
- **Rule:** Periodically check `Task.isCancelled` or call `try Task.checkCancellation()` in loops.
- **Avoid:** Ignoring cancellation signals. `Thread.sleep` in async code.

### `conc-no-unchecked-sendable`
- **Context:** Sendable conformance.
- **Rule:** Fix the underlying data race. Use value types, actors, or explicit Sendable conformance with real thread safety.
- **Avoid:** `@unchecked Sendable` as a quick fix for compiler errors.

## 3. SwiftData Patterns (`data-`)

### `data-delete-rules`
- **Context:** SwiftData relationships.
- **Rule:** Always specify `deleteRule` on `@Relationship`. Use `.cascade` for parent-child ownership, `.nullify` for loose associations.
- **Avoid:** Relationships without explicit delete rules (creates orphaned objects).

### `data-predicate-safety`
- **Context:** SwiftData queries.
- **Rule:** Use `#Predicate` macro. Use `!$0.property.isEmpty` instead of `isEmpty == false`. Keep predicates simple.
- **Avoid:** Complex chained predicates. Manual `NSPredicate`.

### `data-query-usage`
- **Context:** Data fetching.
- **Rule:** Use `@Query` in SwiftUI Views. Use `FetchDescriptor` in ViewModels and non-view code.
- **Avoid:** `@Query` in ViewModels or service classes.

### `data-indexing`
- **Context:** Query performance (iOS 18+).
- **Rule:** Add `@Index` to properties frequently used in predicates or sort descriptors.
- **Avoid:** Full-table scans on large datasets without indexes.

## 4. Security Patterns (`sec-`)

### `sec-keychain-accessible`
- **Context:** Keychain storage.
- **Rule:** Always set `kSecAttrAccessible` explicitly in every `SecItemAdd` call. Implement add-or-update pattern (handle `errSecDuplicateItem`).
- **Avoid:** Omitting `kSecAttrAccessible`. Delete-then-add race conditions.

### `sec-no-userdefaults-secrets`
- **Context:** Credential storage.
- **Rule:** Store all secrets, tokens, and credentials in Keychain, not `UserDefaults`, plists, or source code.
- **Avoid:** `UserDefaults.standard.set(token, forKey: "auth-token")`.

### `sec-biometric-binding`
- **Context:** Biometric authentication.
- **Rule:** Bind biometrics to Keychain items via `SecAccessControlCreateWithFlags`. Do not use `LAContext.evaluatePolicy()` as a standalone authentication gate.
- **Avoid:** Boolean gate pattern without keychain binding.

### `sec-no-mainactor-secitem`
- **Context:** Keychain performance.
- **Rule:** Perform all `SecItem*` calls on a dedicated background actor or queue, never on `@MainActor`.
- **Avoid:** Keychain operations on the main thread.

## 5. Networking Patterns (`net-`)

### `net-status-validation`
- **Context:** HTTP responses.
- **Rule:** Always validate HTTP status codes (200–299) before decoding. URLSession does not throw for 4xx/5xx responses.
- **Avoid:** Decoding response data without checking status code.

### `net-no-shared-session`
- **Context:** URLSession configuration.
- **Rule:** Use a configured `URLSession` instance with explicit timeouts, cache policies, and headers for production code.
- **Avoid:** `URLSession.shared` in production networking code.

### `net-protocol-client`
- **Context:** Testability.
- **Rule:** Define API clients behind protocols. Use `URLProtocol` subclasses for testing, not `URLSession` mocks.
- **Avoid:** Concrete networking classes that can't be substituted in tests.

### `net-no-completion-handlers`
- **Context:** Async patterns.
- **Rule:** Use only async/await variants of URLSession APIs for all new networking code.
- **Avoid:** Completion-handler variants of URLSession APIs.

## 6. Localization Patterns (`l10n-`)

### `l10n-no-concatenation`
- **Context:** Localized string construction.
- **Rule:** Use string interpolation with `LocalizedStringKey` for user-visible strings. Translators need reorderable placeholders.
- **Avoid:** Concatenating localized strings with `+`.

### `l10n-format-style`
- **Context:** Locale-sensitive values.
- **Rule:** Use `FormatStyle` for all dates, numbers, currency, measurements, and durations.
- **Avoid:** `DateFormatter`, `NumberFormatter`, hardcoded date format strings.

## 7. Layout Patterns (`layout-`)

### `layout-content-shape`
- **Context:** Tappable rows.
- **Rule:** Add `.contentShape(Rectangle())` to rows or containers that should be fully tappable.
- **Avoid:** Gesture only activating on visible pixels of sparse layouts.

### `layout-focus-state`
- **Context:** Keyboard management.
- **Rule:** Use `@FocusState` for keyboard focus management in forms. Dismiss keyboard by setting `@FocusState` to `nil`.
- **Avoid:** Manual `UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), ...)`.

## Cross Reference Map

- `swiftui-state-observable`:
  see `../references/state-management.md`, `../references/architecture.md`, `../references/concurrency.md`
- `swiftui-view-extraction`, `swiftui-lazy-layouts`:
  see `../references/view-structure.md`, `../references/performance.md`
- `swiftui-navigation-stack`, `swiftui-task-lifecycle`:
  see `../references/navigation.md`, `../references/concurrency.md`
- `swiftui-gesture-state`, `swiftui-animation-scope`:
  see `../references/gestures.md`, `../references/animations.md`, `../references/accessibility.md`
- `conc-*`:
  see `../references/concurrency.md`, `../references/navigation.md`, `../references/networking.md`
- `data-*`:
  see `../references/swiftdata.md`, `../../swiftui-tester/references/persistence-testing.md`
- `sec-*`:
  see `../references/security.md`, `../references/networking.md`
- `net-*`:
  see `../references/networking.md`, `../references/security.md`, `../references/concurrency.md`
- `l10n-*`:
  see `../references/localization.md`, `../references/formatstyle.md`
- `layout-*`:
  see `../references/view-structure.md`, `../references/accessibility.md`, `../references/gestures.md`

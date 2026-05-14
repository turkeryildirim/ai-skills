---
name: swiftui
description: SwiftUI modern patterns, Swift 6.3+ concurrency, SwiftData, security, and HIG-compliant design. Use when building, reviewing, or auditing iOS/macOS apps. Triggers on "SwiftUI", "SwiftData", "View", "async/await", "actor", "@Observable", "iOS app", "Figma to SwiftUI".
model: inherit
---

# SwiftUI Best Practices

Modern SwiftUI patterns (iOS 17–26+), Swift 6.3 concurrency, SwiftData persistence, security, and Apple's Human Interface Guidelines. Focused on performance, accessibility, and maintainability.

## Specialized Agents

| Agent | Role | Focus |
|-------|------|-------|
| **swiftui-pro** | SwiftUI Expert | View composition, state management, animations, gestures, and HIG. |
| **concurrency-pro** | Swift Concurrency Expert | Actors, Task Groups, Structured Concurrency, Swift 6 isolation. |
| **swiftdata-pro** | Persistence Expert | SwiftData models, relationships, predicates, CloudKit, and indexing. |
| **figma-swiftui** | Figma → SwiftUI | Pixel-perfect translation of Figma designs to native SwiftUI views. |

## When to Use

Reference these guidelines when:
- Building or refactoring SwiftUI views and layouts
- Managing data flow with `@State`, `@Binding`, and `@Observable`
- Implementing Swift Concurrency (`async/await`, Actors)
- Designing persistence layers with SwiftData
- Ensuring accessibility (VoiceOver, Dynamic Type)
- Optimizing view performance and rendering
- Working with animations, gestures, or navigation
- Implementing secure credential storage with Keychain/CryptoKit
- Translating Figma designs to SwiftUI views
- Setting up SwiftLint for code quality enforcement
- Following Apple's Human Interface Guidelines (HIG)

## Step 1: Detect Target Version

**Always check the project's target iOS version and Swift version.**

Check `Project Settings` or `Package.swift`:
```swift
// swift-tools-version: 6.3
platforms: [.iOS(.v18), .macOS(.v15)]
```

### Feature Availability by Version

| Feature | Version |
|---------|---------|
| Async/Await, Task, `foregroundColor()` | iOS 15+ |
| `NavigationStack`, `NavigationSplitView`, `Charts` | iOS 16+ |
| `@Observable`, SwiftData, String Catalogs, `FormatStyle` Duration | iOS 17+ |
| `foregroundStyle()`, `#expect` (Swift Testing), HPKE | iOS 18+ |
| SHA-3 in CryptoKit, ML-KEM/ML-DSA, Model subclassing, default actor isolation, `scrollEdgeEffectStyle()`, Tab(value:) | iOS 26+ |

## Step 2: Choose the Right Guidance Set

- Load `references/state-management.md` before changing data flow, property wrappers, or Observation migration.
- Load `references/concurrency.md` before changing tasks, actors, cancellation, or isolation boundaries.
- Load `references/swiftdata.md` before touching persistence or `@Model` types.
- Load `references/navigation.md` before refactoring multi-tab routing, deep links, or programmatic navigation.
- Load `references/accessibility.md` and `references/animations.md` together when changing motion-heavy UI.
- Load `swiftui-tester` before authoring tests so implementation and test guidance stay aligned.

## Core Directives

### MUST DO

- **Concurrency:** Target Swift 6.3+ with strict concurrency checking. Prefer `async/await` and Actors.
- **State:** Use `@Observable` (iOS 17+) instead of `ObservableObject`. Use `@State` for private view state; mark it `private`.
- **Views:** Extract subviews into small, focused structs to limit invalidation. Use `@ViewBuilder` for containers.
- **View Lifecycle:** Trigger async view work with `.task` / `.task(id:)` so cancellation follows the view lifecycle.
- **Navigation:** Use `NavigationStack` with `NavigationPath` for type-safe routing. Each tab owns its own `NavigationPath`.
- **Environment:** Use typed `@Environment` values for app-level dependencies and avoid global singletons in view code.
- **Persistence:** Add explicit delete rules to SwiftData relationships (e.g., `.cascade`). Use `#Predicate` macro.
- **Layout:** Use `LazyVStack`/`LazyHStack` for large collections. Use stable IDs in `ForEach`. Add `.contentShape(Rectangle())` to tappable rows.
- **Accessibility:** Add text labels to icon-only buttons. Use `FormatStyle` for locale-aware text. Prefer `Button` over `onTapGesture` for single-tap actions.
- **API Hygiene:** Use `foregroundStyle()` instead of `foregroundColor()`.
- **Networking:** Always validate HTTP status codes before decoding. Never use `URLSession.shared` in production.
- **Security:** Never store secrets in `UserDefaults`. Always set `kSecAttrAccessible` explicitly. Never call `SecItem*` on `@MainActor`.
- **Formatting:** Use `FormatStyle` (iOS 15+) for all dates, numbers, currency, and measurements. Never hardcode locales.

### MUST NOT DO

- **Body Bloat:** Never perform I/O, network calls, or heavy computation inside `body`.
- **Lifecycle Abuse:** Avoid loading async data from `onAppear` when `.task` or `.task(id:)` expresses the lifecycle more safely.
- **Type Erasure:** Avoid `AnyView`; use `@ViewBuilder` or `Group` instead.
- **Concurrency Hacks:** Do NOT use `@unchecked Sendable` to fix compiler errors; use actors or value types.
- **State Pitfalls:** Do NOT use `Binding(get:set:)` in view body; use `@State` with `onChange()` instead.
- **Legacy:** Avoid `ObservableObject`, `NavigationView`, `NSLocalizedString`, `MagnificationGesture` (iOS 17+), `RotationGesture` (iOS 17+).
- **UI Testing:** Do NOT use Swift Testing for UI tests (use XCTest).
- **Gestures:** Do NOT use heavy computation in `.onChanged()` closures (runs 60–120 fps). Use `.onEnded()` for expensive work.
- **Networking:** Do NOT mock `URLSession` directly; use `URLProtocol` subclasses. Never disable ATS.

## Category Index — When to Load Which Reference

| # | Category | Impact | Load when… | Reference |
|--:|----------|:------:|------------|-----------|
| 1 | State Management | CRITICAL | `@Observable`, Data Flow, Migration | [`references/state-management.md`](references/state-management.md) |
| 2 | Concurrency | CRITICAL | Actors, Task Groups, Strict Checking | [`references/concurrency.md`](references/concurrency.md) |
| 3 | SwiftData | CRITICAL | Models, Relationships, Predicates, Indexing | [`references/swiftdata.md`](references/swiftdata.md) |
| 4 | Architecture | HIGH | MV, MVVM, MVI, TCA, Clean Architecture | [`references/architecture.md`](references/architecture.md) |
| 5 | View Structure | HIGH | View Composition, `@ViewBuilder`, Layout | [`references/view-structure.md`](references/view-structure.md) |
| 6 | Performance | HIGH | Rendering Optimization, `_logChanges` | [`references/performance.md`](references/performance.md) |
| 7 | Navigation | HIGH | NavigationStack, Tabs, Deep Linking, iOS 26 | [`references/navigation.md`](references/navigation.md) |
| 8 | Accessibility | HIGH | VoiceOver, Dynamic Type, HIG | [`references/accessibility.md`](references/accessibility.md) |
| 9 | Networking | HIGH | URLSession, Async/Await, Retry, Auth | [`references/networking.md`](references/networking.md) |
| 10 | Localization | MEDIUM | String Catalogs, RTL, FormatStyle | [`references/localization.md`](references/localization.md) |
| 11 | Animation | MEDIUM | Implicit/Explicit, Keyframes, Phase, Symbols | [`references/animations.md`](references/animations.md) |
| 12 | Gestures | MEDIUM | Tap, Drag, Pinch, Rotate, Composition | [`references/gestures.md`](references/gestures.md) |
| 13 | Security | HIGH | Keychain, CryptoKit, Biometrics, TLS | [`references/security.md`](references/security.md) |
| 14 | FormatStyle | MEDIUM | Dates, Numbers, Currency, Measurements | [`references/formatstyle.md`](references/formatstyle.md) |
| 15 | SwiftLint | MEDIUM | Code quality, CI enforcement, rule config | [`references/swiftlint.md`](references/swiftlint.md) |

## Rule Index

### 1. SwiftUI Patterns (`swiftui-`) — CRITICAL
`swiftui-state-observable` · `swiftui-view-extraction` · `swiftui-navigation-stack` · `swiftui-lazy-layouts` · `swiftui-foreground-style` · `swiftui-gesture-state` · `swiftui-animation-scope` · `swiftui-task-lifecycle`

### 2. Concurrency (`conc-`) — CRITICAL
`conc-strict-checking` · `conc-actor-isolation` · `conc-task-groups` · `conc-cooperative-cancellation` · `conc-no-unchecked-sendable`

### 3. SwiftData (`data-`) — CRITICAL
`data-delete-rules` · `data-predicate-safety` · `data-query-usage` · `data-indexing`

### 4. Security (`sec-`) — HIGH
`sec-keychain-accessible` · `sec-no-userdefaults-secrets` · `sec-biometric-binding` · `sec-no-mainactor-secitem`

### 5. Networking (`net-`) — HIGH
`net-status-validation` · `net-no-shared-session` · `net-protocol-client` · `net-no-completion-handlers`

### 6. Localization (`l10n-`) — MEDIUM
`l10n-no-concatenation` · `l10n-format-style`

### 7. Layout (`layout-`) — MEDIUM
`layout-content-shape` · `layout-focus-state`

### 8. Testing (`test-`) — HIGH (See `swiftui-tester`)
Load `swiftui-tester` for unit and integration testing guidance using Swift Testing.

## Validation Checklist

- [ ] Swift 6.3 strict concurrency checking is enabled.
- [ ] `@Observable` is used for state management (iOS 17+ targets).
- [ ] `@State` properties are marked `private`.
- [ ] Views are small, focused, and extracted from large bodies.
- [ ] No heavy logic or I/O in `View.body`.
- [ ] Async view loading uses `.task` / `.task(id:)` with cancellation-aware flows.
- [ ] `NavigationStack` is used for programmatic navigation.
- [ ] Each tab maintains an independent `NavigationPath`.
- [ ] App-level dependencies are injected via typed environment values or explicit parameters.
- [ ] `foregroundStyle()` is used instead of legacy `foregroundColor()`.
- [ ] Accessibility labels are present for all interactive elements.
- [ ] SwiftData relationships have explicit delete rules.
- [ ] `String Catalogs` are used for localization (iOS 17+).
- [ ] No `AnyView` type erasure.
- [ ] HTTP status codes validated before JSON decoding.
- [ ] Secrets stored in Keychain, not `UserDefaults`.
- [ ] `FormatStyle` used for all locale-sensitive formatting.
- [ ] iOS 26+ APIs gated with `#available` checks.
- [ ] `.onChanged()` gesture closures are lightweight.
- [ ] Reduce Motion checked before playing intense animations.

## External References

- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui)
- [Swift Concurrency Guide](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)
- [SwiftData Documentation](https://developer.apple.com/documentation/swiftdata)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Swift Testing Guide](https://developer.apple.com/documentation/testing)
- [CryptoKit Documentation](https://developer.apple.com/documentation/cryptokit)
- [Keychain Services](https://developer.apple.com/documentation/security/keychain_services)

---
name: swift-architecture-guide
description: Swift/iOS architecture pattern benchmarks (MVC, MVVM, VIPER, TCA), SPM module structure, memory management, and common anti-patterns for architectural analysis.
type: reference
---

# Swift Architecture Guide

Reference for analyzing Swift/iOS and macOS projects.

## Maturity Levels

| Level | Signals |
|-------|---------|
| **Level 1** | All in ViewController, no separation |
| **Level 2** | Some model files, but ViewController still has network code |
| **Level 3** | MVVM with ViewModels, protocols for services |
| **Level 4** | Coordinators for navigation, SPM modules, protocol DI throughout |
| **Level 5** | Full MVVM or TCA, SPM feature modules, >60% test coverage |

---

## Architectural Pattern Comparison

### MVC (UIKit Default)
```swift
// Pattern: ViewController orchestrates Model and View
// ✅ Healthy: ViewController <150 lines, model holds data, views handle display
// ❌ Problem: "Massive ViewController" — everything in one class

Signals: UIViewController subclasses, UITableViewDelegate, no ViewModel files
Healthy VC size: <150 lines
Warning: 150-300 lines
Critical: >300 lines (likely Massive VC)
```

### MVVM
```swift
// Pattern: View ← binds to → ViewModel ← calls → Services/Repositories
// ✅ ViewController only handles UI lifecycle and binding
// ✅ ViewModel is testable without UIKit

Signals: *ViewModel.swift files, @Published, ObservableObject, Combine/async
Healthy ViewModel size: <200 lines
Healthy ViewController size: <100 lines (just binding code)
```

### VIPER
```swift
// Pattern: View ← Presenter ← Interactor → Entity/Repository, Router for navigation
// Heavy boilerplate — appropriate for very large teams and complex features

Signals: *Interactor.swift, *Presenter.swift, *Router.swift, *Builder.swift
⚠️ Watch for: VIPER folders but logic still in ViewController (cargo cult)
```

### TCA (The Composable Architecture)
```swift
// Pattern: State → Action → Reducer → Effect → State (unidirectional)
// Library: pointfreeco/swift-composable-architecture

Signals: ReducerProtocol conformances, Store, ViewStore, Effect types
✅ Generally well-structured when TCA is adopted consistently
⚠️ Watch for: mixing TCA with MVVM (architectural confusion)
```

### SwiftUI Native
```swift
// Pattern: View structs, @State/@StateObject, NavigationStack
// Best for: New projects, SwiftUI-first approach

Signals: struct ContentView: View, @StateObject, NavigationStack
Healthy View size: <100 lines
⚠️ Watch for: business logic in View body, @EnvironmentObject overuse
```

---

## SPM Module Structure Benchmarks

### Dependency Direction Rules
```
✅ Valid:
App Target → Feature Modules → Shared/Core → (nothing)
Feature Module → NetworkKit
Feature Module → Analytics (if properly abstracted)

❌ Invalid:
Core/Shared → Feature Module   (Core cannot know about features)
Feature A → Feature B          (Features must be independent)
Analytics → Feature            (Analytics should be a one-way sink)
```

### Size-Based Modularization Guidelines
```
< 5,000 LOC  → Single target acceptable
5,000-15,000 → Core + App split recommended
15,000-50,000 → Feature modules required
> 50,000 LOC  → Domain-based module packages (separate Package.swift per domain)
```

### Healthy Package.swift (Medium App)
```swift
let package = Package(
    name: "MyApp",
    platforms: [.iOS(.v16)],
    targets: [
        // Shared foundation — no feature dependencies
        .target(name: "SharedModels", dependencies: []),
        .target(name: "NetworkKit", dependencies: ["SharedModels"]),
        .target(name: "Analytics", dependencies: ["SharedModels"]),
        .target(name: "DesignSystem", dependencies: []),

        // Feature modules — depend only on shared layers
        .target(name: "AuthFeature",
                dependencies: ["SharedModels", "NetworkKit", "DesignSystem"]),
        .target(name: "OrdersFeature",
                dependencies: ["SharedModels", "NetworkKit", "Analytics"]),

        // App shell
        .target(name: "MyApp",
                dependencies: ["AuthFeature", "OrdersFeature"]),

        // Tests
        .testTarget(name: "AuthFeatureTests", dependencies: ["AuthFeature"]),
        .testTarget(name: "OrdersFeatureTests", dependencies: ["OrdersFeature"]),
    ]
)
```

---

## Concurrency Model Comparison

| Model | Modern Equivalent | When to Flag |
|-------|------------------|--------------|
| `DispatchQueue.main.async` | `await MainActor.run {}` | Mixed with async/await |
| `DispatchQueue.global().async` | `Task { }` | Mixed with async/await |
| Completion handlers | `async throws` | In new code (Swift 5.5+) |
| Combine Publishers | `AsyncSequence` or keep Combine | Mixing both unnecessarily |
| `@objc` selectors for async | `async/await` | Legacy pattern in new code |

### Concurrency Consistency Check
```
✅ Consistent: All async code uses Swift Concurrency (async/await, Task, Actor)
✅ Consistent: All async code uses Combine Publishers
⚠️ Mixed: Some use GCD, some use Combine, some use async/await
    → Flag as MEDIUM: agree on one model and migrate
```

---

## Memory Management Checklist

```swift
// Retain cycle patterns to look for:

// 1. Closures in long-lived objects
class MyViewController: UIViewController {
    var callback: (() -> Void)?

    func setup() {
        callback = { [weak self] in  // ✅ [weak self] prevents retain cycle
            self?.update()
        }
    }
}

// 2. Delegate patterns
class MyService {
    weak var delegate: MyServiceDelegate?  // ✅ weak delegate
    // strong delegate = retain cycle
}

// 3. NotificationCenter
// ✅ Remove observer in deinit
deinit {
    NotificationCenter.default.removeObserver(self)
    timer?.invalidate()
}
```

---

## Common Anti-Patterns

| Anti-Pattern | Signs | Impact |
|-------------|-------|--------|
| **Massive ViewController** | >300 lines, network + UI + logic | Untestable, brittle |
| **No architectural pattern** | Ad-hoc, inconsistent | Onboarding impossible |
| **Concrete service dependencies** | `let service = OrderAPIService()` | Cannot mock in tests |
| **Strong delegate** | `var delegate: Protocol?` without `weak` | Retain cycle, memory leak |
| **Missing [weak self]** | Closures capturing self strongly | Memory leak on every navigation |
| **try! / as! in production** | Force casts outside tests | Crash on unexpected server data |
| **Hardcoded secrets** | `let apiKey = "sk-..."` | Credential exposure in source |
| **No SPM for large codebase** | >15k LOC in single target | Slow builds, tight coupling |
| **Mixing GCD + async/await** | Both patterns without clear boundary | Race conditions, hard to reason about |

---
title: SwiftUI State Management Analysis
impact: HIGH
impactDescription: "Incorrect property wrapper usage causes view update loops, memory leaks, and unpredictable state ownership"
tags: swiftui, state, stateobject, observedobject, environmentobject, observable, binding
---

## SwiftUI State Management Analysis

**Impact: HIGH (Incorrect property wrapper usage causes view update loops, memory leaks, and unpredictable state ownership)**

Each SwiftUI property wrapper has a specific ownership and lifetime contract. Using the wrong wrapper causes unexpected view reconstruction, objects being recreated on every render, or state being shared when it should be local.

## Incorrect

```swift
// ❌ @StateObject for injected (not owned) view model — creates a new instance every time
struct OrderDetailView: View {
    @StateObject var viewModel: OrderDetailViewModel  // ❌ if passed from parent, use @ObservedObject

    init(order: Order) {
        _viewModel = StateObject(wrappedValue: OrderDetailViewModel(order: order))
        // ❌ StateObject wrapping a new init here will NOT be recreated correctly
        // Use @ObservedObject or pass the VM from the parent
    }
}

// ❌ @ObservedObject for a ViewModel the view should own — VM recreated every render
struct ProfileView: View {
    @ObservedObject var viewModel = ProfileViewModel()  // ❌ new instance on every render
    // Should be @StateObject
}

// ❌ @EnvironmentObject for state that is not global
struct CheckoutView: View {
    @EnvironmentObject var cartItem: CartItemViewModel  // ❌ if only used in checkout flow
    // Should be passed as @ObservedObject or via @Bindable
}
```

## Correct

```swift
// ✅ @State — local, ephemeral, value-type state
struct CounterView: View {
    @State private var count = 0  // ✅ owned by this view, primitive or simple struct

    var body: some View {
        Button("Count: \(count)") { count += 1 }
    }
}

// ✅ @StateObject — view OWNS the reference type, created once per view lifetime
struct OrderListView: View {
    @StateObject private var viewModel = OrderListViewModel()  // ✅ owned, persists across renders

    var body: some View { /* ... */ }
}

// ✅ @ObservedObject — view RECEIVES the reference type from parent
struct OrderDetailView: View {
    @ObservedObject var viewModel: OrderDetailViewModel  // ✅ injected, not owned

    init(viewModel: OrderDetailViewModel) {
        self.viewModel = viewModel
    }
}

// ✅ @Observable (Swift 5.9+ / iOS 17+) — preferred over ObservableObject
@Observable
final class UserViewModel {
    var name: String = ""
    var isLoading: Bool = false
    // No @Published needed — all stored properties are observed automatically
}

struct ProfileView: View {
    var viewModel: UserViewModel  // ✅ no wrapper needed with @Observable
}

// ✅ @EnvironmentObject — truly global/app-wide state only
struct RootApp: App {
    @StateObject private var authSession = AuthSession()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authSession)  // ✅ injected at root, used app-wide
        }
    }
}
```

## State Ownership Matrix

| Wrapper | Ownership | Use Case |
|---------|-----------|----------|
| `@State` | This view | Local UI state — toggle, text input, selected tab |
| `@StateObject` | This view | Owns the ViewModel — created once per view lifecycle |
| `@ObservedObject` | Parent | ViewModel injected from parent or environment |
| `@EnvironmentObject` | App/ancestor | Truly global: auth, theme, app-wide cart |
| `@Observable` (Swift 5.9+) | Flexible | Preferred modern replacement for ObservableObject |
| `@Bindable` (Swift 5.9+) | Flexible | Two-way binding into `@Observable` objects |

## State Compliance Assessment

```
HIGH violations:
├── @ObservedObject var vm = SomeViewModel() — recreated on every render (missing @StateObject)
├── @StateObject used with an object injected from the parent
└── Binding passed more than 2 levels deep (use @EnvironmentObject or restructure)

MEDIUM violations:
├── @EnvironmentObject for state scoped to a sub-flow (not truly global)
├── ObservableObject still used in new code targeting iOS 17+ (prefer @Observable)
└── @Published on all properties of a large class (not all need observation)

LOW violations:
├── @State for a complex struct that should be a ViewModel
└── Missing private on @State properties
```

## Why

- **`@StateObject` contract**: SwiftUI guarantees to create a `@StateObject` once per view identity and keep it alive across re-renders. Using it for injected objects breaks the parent's ownership semantics.
- **`@ObservedObject` is unowned**: If the parent that creates the `ObservedObject` is destroyed, the child's reference becomes invalid.
- **`@Observable` advantage**: Unlike `ObservableObject`, `@Observable` provides fine-grained dependency tracking — only views that read a specific property re-render when that property changes, not the whole object.
